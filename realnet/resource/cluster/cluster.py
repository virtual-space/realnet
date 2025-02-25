"""Kubernetes cluster integration implementation."""
from typing import Dict, Any, List, Optional
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException
from realnet.core.type import Type, Instance
from realnet.core.provider import ContextProvider

class Cluster(Type):
    """Kubernetes cluster integration resource."""

    def __init__(self, provider: ContextProvider):
        """Initialize Cluster resource.
        
        Args:
            provider: Provider instance
        """
        super().__init__(provider)
        self._initialize_k8s_client()
        self._api_client = None
        self._core_api = None
        self._apps_api = None
        self._batch_api = None
        self._rbac_api = None
        self._networking_api = None

    def _initialize_k8s_client(self):
        """Initialize Kubernetes client using in-cluster config."""
        try:
            # Try in-cluster config first (when running in pod)
            config.load_incluster_config()
        except config.ConfigException:
            try:
                # Fall back to kubeconfig for local development
                config.load_kube_config()
            except config.ConfigException as e:
                raise RuntimeError(f"Failed to initialize Kubernetes client: {e}")

        self._api_client = client.ApiClient()
        self._core_api = client.CoreV1Api(self._api_client)
        self._apps_api = client.AppsV1Api(self._api_client)
        self._batch_api = client.BatchV1Api(self._api_client)
        self._rbac_api = client.RbacAuthorizationV1Api(self._api_client)
        self._networking_api = client.NetworkingV1Api(self._api_client)

    def _get_api_for_kind(self, kind: str):
        """Get appropriate API client for resource kind."""
        kind_to_api = {
            'Pod': self._core_api,
            'Service': self._core_api,
            'ConfigMap': self._core_api,
            'Secret': self._core_api,
            'Namespace': self._core_api,
            'PersistentVolume': self._core_api,
            'PersistentVolumeClaim': self._core_api,
            'ServiceAccount': self._core_api,
            'Deployment': self._apps_api,
            'StatefulSet': self._apps_api,
            'DaemonSet': self._apps_api,
            'Job': self._batch_api,
            'CronJob': self._batch_api,
            'Role': self._rbac_api,
            'RoleBinding': self._rbac_api,
            'ClusterRole': self._rbac_api,
            'ClusterRoleBinding': self._rbac_api,
            'Ingress': self._networking_api
        }
        return kind_to_api.get(kind)

    def _get_list_method(self, api, kind: str, namespaced: bool = True):
        """Get appropriate list method for resource kind."""
        if namespaced:
            return getattr(api, f'list_namespaced_{kind.lower()}')
        return getattr(api, f'list_{kind.lower()}')

    def _get_read_method(self, api, kind: str, namespaced: bool = True):
        """Get appropriate read method for resource kind."""
        if namespaced:
            return getattr(api, f'read_namespaced_{kind.lower()}')
        return getattr(api, f'read_{kind.lower()}')

    def _get_create_method(self, api, kind: str, namespaced: bool = True):
        """Get appropriate create method for resource kind."""
        if namespaced:
            return getattr(api, f'create_namespaced_{kind.lower()}')
        return getattr(api, f'create_{kind.lower()}')

    def _get_update_method(self, api, kind: str, namespaced: bool = True):
        """Get appropriate update method for resource kind."""
        if namespaced:
            return getattr(api, f'replace_namespaced_{kind.lower()}')
        return getattr(api, f'replace_{kind.lower()}')

    def _get_delete_method(self, api, kind: str, namespaced: bool = True):
        """Get appropriate delete method for resource kind."""
        if namespaced:
            return getattr(api, f'delete_namespaced_{kind.lower()}')
        return getattr(api, f'delete_{kind.lower()}')

    def _to_realnet_attributes(self, k8s_obj) -> Dict[str, Any]:
        """Convert Kubernetes object to realnet attributes."""
        # Extract core metadata
        attributes = {
            'apiVersion': k8s_obj.api_version,
            'kind': k8s_obj.kind,
            'metadata': {
                'name': k8s_obj.metadata.name,
                'namespace': k8s_obj.metadata.namespace,
                'uid': k8s_obj.metadata.uid,
                'resourceVersion': k8s_obj.metadata.resource_version
            }
        }

        # Add labels if present
        if k8s_obj.metadata.labels:
            attributes['metadata']['labels'] = k8s_obj.metadata.labels

        # Add annotations if present
        if k8s_obj.metadata.annotations:
            attributes['metadata']['annotations'] = k8s_obj.metadata.annotations

        # Add spec if present
        if hasattr(k8s_obj, 'spec') and k8s_obj.spec:
            attributes['spec'] = k8s_obj.spec.to_dict()

        # Add status if present
        if hasattr(k8s_obj, 'status') and k8s_obj.status:
            attributes['status'] = k8s_obj.status.to_dict()

        return attributes

    def _from_realnet_attributes(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """Convert realnet attributes to Kubernetes object format."""
        return {
            'apiVersion': attributes.get('apiVersion'),
            'kind': attributes.get('kind'),
            'metadata': attributes.get('metadata', {}),
            'spec': attributes.get('spec', {})
        }

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Kubernetes resource.
        
        Args:
            data: Resource configuration data
        
        Returns:
            Created resource data
        """
        kind = data.get('kind')
        if not kind:
            raise ValueError("Resource kind is required")

        api = self._get_api_for_kind(kind)
        if not api:
            raise ValueError(f"Unsupported resource kind: {kind}")

        namespace = data.get('metadata', {}).get('namespace', 'default')
        namespaced = kind not in {'Namespace', 'PersistentVolume', 'ClusterRole', 'ClusterRoleBinding'}

        try:
            create_method = self._get_create_method(api, kind, namespaced)
            if namespaced:
                response = create_method(namespace=namespace, body=data)
            else:
                response = create_method(body=data)
            return self._to_realnet_attributes(response)
        except ApiException as e:
            raise RuntimeError(f"Failed to create {kind}: {e}")

    def read(self, name: str, namespace: str = 'default', kind: str = None) -> Dict[str, Any]:
        """Read Kubernetes resource.
        
        Args:
            name: Resource name
            namespace: Resource namespace
            kind: Resource kind
        
        Returns:
            Resource configuration data
        """
        if not kind:
            raise ValueError("Resource kind is required")

        api = self._get_api_for_kind(kind)
        if not api:
            raise ValueError(f"Unsupported resource kind: {kind}")

        namespaced = kind not in {'Namespace', 'PersistentVolume', 'ClusterRole', 'ClusterRoleBinding'}

        try:
            read_method = self._get_read_method(api, kind, namespaced)
            if namespaced:
                response = read_method(name=name, namespace=namespace)
            else:
                response = read_method(name=name)
            return self._to_realnet_attributes(response)
        except ApiException as e:
            if e.status == 404:
                raise ValueError(f"{kind} {name} not found")
            raise RuntimeError(f"Failed to read {kind}: {e}")

    def update(self, name: str, data: Dict[str, Any], namespace: str = 'default') -> Dict[str, Any]:
        """Update Kubernetes resource.
        
        Args:
            name: Resource name
            data: Updated configuration data
            namespace: Resource namespace
        
        Returns:
            Updated resource data
        """
        kind = data.get('kind')
        if not kind:
            raise ValueError("Resource kind is required")

        api = self._get_api_for_kind(kind)
        if not api:
            raise ValueError(f"Unsupported resource kind: {kind}")

        namespaced = kind not in {'Namespace', 'PersistentVolume', 'ClusterRole', 'ClusterRoleBinding'}

        try:
            update_method = self._get_update_method(api, kind, namespaced)
            if namespaced:
                response = update_method(name=name, namespace=namespace, body=data)
            else:
                response = update_method(name=name, body=data)
            return self._to_realnet_attributes(response)
        except ApiException as e:
            raise RuntimeError(f"Failed to update {kind}: {e}")

    def delete(self, name: str, namespace: str = 'default', kind: str = None) -> None:
        """Delete Kubernetes resource.
        
        Args:
            name: Resource name to delete
            namespace: Resource namespace
            kind: Resource kind
        """
        if not kind:
            raise ValueError("Resource kind is required")

        api = self._get_api_for_kind(kind)
        if not api:
            raise ValueError(f"Unsupported resource kind: {kind}")

        namespaced = kind not in {'Namespace', 'PersistentVolume', 'ClusterRole', 'ClusterRoleBinding'}

        try:
            delete_method = self._get_delete_method(api, kind, namespaced)
            if namespaced:
                delete_method(name=name, namespace=namespace)
            else:
                delete_method(name=name)
        except ApiException as e:
            if e.status != 404:  # Ignore if resource already deleted
                raise RuntimeError(f"Failed to delete {kind}: {e}")

    def list(self, namespace: Optional[str] = None, kind: Optional[str] = None) -> List[Dict[str, Any]]:
        """List Kubernetes resources.
        
        Args:
            namespace: Optional namespace to filter by
            kind: Optional kind to filter by
        
        Returns:
            List of resource configurations
        """
        if not kind:
            # If no kind specified, return all resources we can access
            resources = []
            for k in self._get_api_for_kind.keys():
                try:
                    resources.extend(self.list(namespace, k))
                except:
                    pass
            return resources

        api = self._get_api_for_kind(kind)
        if not api:
            raise ValueError(f"Unsupported resource kind: {kind}")

        namespaced = kind not in {'Namespace', 'PersistentVolume', 'ClusterRole', 'ClusterRoleBinding'}

        try:
            list_method = self._get_list_method(api, kind, namespaced)
            if namespaced and namespace:
                response = list_method(namespace=namespace)
            else:
                response = list_method()
            return [self._to_realnet_attributes(item) for item in response.items]
        except ApiException as e:
            raise RuntimeError(f"Failed to list {kind}: {e}")

    def get_items(self, module, endpoint, args, path, account, query, parent_item=None):
        """Get Kubernetes resources as realnet items."""
        # Extract namespace and kind from query if provided
        namespace = query.get('namespace') if query else None
        kind = query.get('kind') if query else None

        try:
            resources = self.list(namespace, kind)
            instances = []
            
            for resource in resources:
                # Create Instance for each resource
                resource_type = module.get_type(resource['kind'])
                if resource_type:
                    instance = Instance(
                        id=f"{resource['metadata']['namespace']}/{resource['metadata']['name']}" if resource['metadata'].get('namespace') else resource['metadata']['name'],
                        type=resource_type,
                        name=resource['metadata']['name'],
                        attributes=resource
                    )
                    instances.append(instance)
            
            return instances
        except Exception as e:
            raise RuntimeError(f"Failed to get Kubernetes resources: {e}")

    def get_item(self, module, endpoint, account, args, path):
        """Get specific Kubernetes resource as realnet item."""
        # Parse path to get namespace and name
        parts = path.split('/')
        if len(parts) == 2:
            namespace, name = parts
        else:
            namespace = 'default'
            name = parts[0]

        # Try to determine kind from the item's type
        kind = None
        if 'type' in args:
            kind = args['type']

        try:
            resource = self.read(name, namespace, kind)
            resource_type = module.get_type(resource['kind'])
            if resource_type:
                instance = Instance(
                    id=path,
                    type=resource_type,
                    name=resource['metadata']['name'],
                    attributes=resource
                )
                return instance
        except Exception as e:
            raise RuntimeError(f"Failed to get Kubernetes resource: {e}")

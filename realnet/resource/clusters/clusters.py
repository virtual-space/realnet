"""Kubernetes cluster management implementation."""
import os
import json
import yaml
import subprocess
from typing import Dict, Any, List
from realnet.core.provider import Provider
from realnet.core.type import Type

class Clusters(Type):
    """Kubernetes cluster management resource."""

    def __init__(self, provider: Provider):
        """Initialize Clusters resource.
        
        Args:
            provider: Provider instance
        """
        super().__init__(provider)
        self.clusters: Dict[str, Dict[str, Any]] = {}
        self.base_path = os.path.join(os.path.dirname(__file__), '..', '..', 'k8s')

    def _apply_manifests(self, cluster_name: str, manifests_dir: str) -> None:
        """Apply Kubernetes manifests for a cluster.
        
        Args:
            cluster_name: Name of the cluster
            manifests_dir: Directory containing K8s manifests
        """
        # Ensure kubectl context is set to the right cluster
        subprocess.run(['kubectl', 'config', 'use-context', cluster_name], check=True)
        
        # Apply manifests in order: namespace, storage, database, mqtt, realnet
        manifest_order = ['namespace.yaml', 'storage.yaml', 'postgresql.yaml', 'mosquitto.yaml', 'realnet.yaml']
        
        for manifest in manifest_order:
            manifest_path = os.path.join(manifests_dir, manifest)
            if os.path.exists(manifest_path):
                subprocess.run(['kubectl', 'apply', '-f', manifest_path], check=True)

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Kubernetes cluster configuration.
        
        Args:
            data: Cluster configuration data
        
        Returns:
            Created cluster data
        """
        name = data.get('name')
        if not name:
            raise ValueError("Cluster name is required")

        # Basic cluster configuration
        cluster_data = {
            'name': name,
            'status': 'configuring',
            'config': {
                'data_path': data.get('data_path', '/data'),
                'postgresql': {
                    'host': data.get('postgresql_host', 'postgresql'),
                    'port': data.get('postgresql_port', 5432),
                    'database': data.get('postgresql_database', 'realnet'),
                    'user': data.get('postgresql_user', 'realnet'),
                    'password': data.get('postgresql_password', 'realnet')
                },
                'mqtt': {
                    'host': data.get('mqtt_host', 'mosquitto'),
                    'port': data.get('mqtt_port', 1883)
                }
            }
        }

        try:
            # Generate Kubernetes manifests
            manifests_dir = os.path.join(self.base_path, name)
            os.makedirs(manifests_dir, exist_ok=True)

            # Create namespace manifest
            namespace = {
                'apiVersion': 'v1',
                'kind': 'Namespace',
                'metadata': {'name': name}
            }
            with open(os.path.join(manifests_dir, 'namespace.yaml'), 'w') as f:
                yaml.dump(namespace, f)

            # Create storage manifest (PV and PVC)
            storage = {
                'apiVersion': 'v1',
                'kind': 'PersistentVolume',
                'metadata': {'name': f'{name}-data'},
                'spec': {
                    'capacity': {'storage': '10Gi'},
                    'accessModes': ['ReadWriteMany'],
                    'hostPath': {'path': cluster_data['config']['data_path']}
                }
            }
            with open(os.path.join(manifests_dir, 'storage.yaml'), 'w') as f:
                yaml.dump(storage, f)

            # Create PostgreSQL manifest
            postgresql = {
                'apiVersion': 'apps/v1',
                'kind': 'StatefulSet',
                'metadata': {
                    'name': 'postgresql',
                    'namespace': name
                },
                'spec': {
                    'serviceName': 'postgresql',
                    'replicas': 1,
                    'selector': {'matchLabels': {'app': 'postgresql'}},
                    'template': {
                        'metadata': {'labels': {'app': 'postgresql'}},
                        'spec': {
                            'containers': [{
                                'name': 'postgresql',
                                'image': 'postgres:latest',
                                'env': [
                                    {'name': 'POSTGRES_DB', 'value': cluster_data['config']['postgresql']['database']},
                                    {'name': 'POSTGRES_USER', 'value': cluster_data['config']['postgresql']['user']},
                                    {'name': 'POSTGRES_PASSWORD', 'value': cluster_data['config']['postgresql']['password']}
                                ],
                                'ports': [{'containerPort': 5432}],
                                'volumeMounts': [{'name': 'data', 'mountPath': '/var/lib/postgresql/data'}]
                            }],
                            'volumes': [{'name': 'data', 'persistentVolumeClaim': {'claimName': f'{name}-postgresql'}}]
                        }
                    }
                }
            }
            with open(os.path.join(manifests_dir, 'postgresql.yaml'), 'w') as f:
                yaml.dump(postgresql, f)

            # Create Mosquitto manifest
            mosquitto = {
                'apiVersion': 'apps/v1',
                'kind': 'Deployment',
                'metadata': {
                    'name': 'mosquitto',
                    'namespace': name
                },
                'spec': {
                    'replicas': 1,
                    'selector': {'matchLabels': {'app': 'mosquitto'}},
                    'template': {
                        'metadata': {'labels': {'app': 'mosquitto'}},
                        'spec': {
                            'containers': [{
                                'name': 'mosquitto',
                                'image': 'eclipse-mosquitto:latest',
                                'ports': [{'containerPort': 1883}]
                            }]
                        }
                    }
                }
            }
            with open(os.path.join(manifests_dir, 'mosquitto.yaml'), 'w') as f:
                yaml.dump(mosquitto, f)

            # Apply the manifests
            self._apply_manifests(name, manifests_dir)
            
            cluster_data['status'] = 'running'
            self.clusters[name] = cluster_data
            
            return cluster_data

        except Exception as e:
            cluster_data['status'] = 'failed'
            cluster_data['error'] = str(e)
            self.clusters[name] = cluster_data
            raise

    def read(self, name: str) -> Dict[str, Any]:
        """Read cluster configuration.
        
        Args:
            name: Cluster name
        
        Returns:
            Cluster configuration data
        """
        if name not in self.clusters:
            raise ValueError(f"Cluster {name} not found")
        
        return self.clusters[name]

    def update(self, name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update cluster configuration.
        
        Args:
            name: Cluster name
            data: Updated configuration data
        
        Returns:
            Updated cluster data
        """
        if name not in self.clusters:
            raise ValueError(f"Cluster {name} not found")

        cluster_data = self.clusters[name]
        
        # Update configuration
        if 'data_path' in data:
            cluster_data['config']['data_path'] = data['data_path']
        if 'postgresql' in data:
            cluster_data['config']['postgresql'].update(data['postgresql'])
        if 'mqtt' in data:
            cluster_data['config']['mqtt'].update(data['mqtt'])

        # Regenerate and apply manifests
        try:
            manifests_dir = os.path.join(self.base_path, name)
            self._apply_manifests(name, manifests_dir)
            cluster_data['status'] = 'running'
        except Exception as e:
            cluster_data['status'] = 'failed'
            cluster_data['error'] = str(e)
            raise

        return cluster_data

    def delete(self, name: str) -> None:
        """Delete cluster.
        
        Args:
            name: Cluster name to delete
        """
        if name not in self.clusters:
            raise ValueError(f"Cluster {name} not found")

        try:
            # Delete Kubernetes resources
            subprocess.run(['kubectl', 'delete', 'namespace', name], check=True)
            
            # Remove manifests
            manifests_dir = os.path.join(self.base_path, name)
            if os.path.exists(manifests_dir):
                for file in os.listdir(manifests_dir):
                    os.remove(os.path.join(manifests_dir, file))
                os.rmdir(manifests_dir)

            del self.clusters[name]
        except Exception as e:
            raise RuntimeError(f"Failed to delete cluster {name}: {e}")

    def list(self) -> List[Dict[str, Any]]:
        """List all clusters.
        
        Returns:
            List of cluster configurations
        """
        return list(self.clusters.values())

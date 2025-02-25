import os
from typing import Dict, Any, List, Optional
import requests
from urllib.parse import urljoin
from realnet.provider.generic.resource import GenericResourceProvider
from realnet.core.config import Config
from realnet.core.type import Type

class WebsitesResourceProvider(GenericResourceProvider):
    def __init__(self):
        super().__init__()
        cfg = Config()
        self.wordpress_url = os.getenv('REALNET_WORDPRESS_URL')
        self.wordpress_token = os.getenv('REALNET_WORDPRESS_TOKEN')

        # Define types
        self.website_type = Type('Website', 'Item', {
            'module': 'websites.resource',
            'domain': '',
            'title': '',
            'theme': '',
            'status': 'draft',
            'wordpress_id': None
        })

        self.page_type = Type('Page', 'Item', {
            'module': 'websites.resource',
            'website': None,
            'path': '',
            'title': '',
            'content': '',
            'layout': '',
            'status': 'draft',
            'meta': {},
            'wordpress_id': None
        })

        self.post_type = Type('Post', 'Item', {
            'module': 'websites.resource',
            'website': None,
            'path': '',
            'title': '',
            'content': '',
            'excerpt': '',
            'author': '',
            'categories': [],
            'tags': [],
            'status': 'draft',
            'meta': {},
            'wordpress_id': None
        })

    def _sync_with_wordpress(self, type: str, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync content with WordPress"""
        url = urljoin(self.wordpress_url, '/wp-json/realnet/v1/sync')
        response = requests.post(url, json={
            'type': type,
            'action': action,
            'data': data
        }, headers={
            'X-Realnet-Token': self.wordpress_token
        })
        response.raise_for_status()
        return response.json()

    def _map_website(self, data: Dict[str, Any], wordpress_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Map website data to resource format"""
        return {
            'id': data.get('id', ''),
            'name': data.get('title', ''),
            'type': 'websites.website',
            'attributes': {
                'domain': data.get('domain', ''),
                'title': data.get('title', ''),
                'theme': data.get('theme', ''),
                'status': data.get('status', 'draft'),
                'wordpress_id': wordpress_data.get('site_id') if wordpress_data else None
            }
        }

    def _map_page(self, data: Dict[str, Any], wordpress_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Map page data to resource format"""
        return {
            'id': data.get('id', ''),
            'name': data.get('title', ''),
            'type': 'websites.page',
            'attributes': {
                'website': data.get('website', ''),
                'path': data.get('path', ''),
                'title': data.get('title', ''),
                'content': data.get('content', ''),
                'layout': data.get('layout', ''),
                'status': data.get('status', 'draft'),
                'meta': data.get('meta', {}),
                'wordpress_id': wordpress_data.get('page_id') if wordpress_data else None
            }
        }

    def _map_post(self, data: Dict[str, Any], wordpress_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Map post data to resource format"""
        return {
            'id': data.get('id', ''),
            'name': data.get('title', ''),
            'type': 'websites.post',
            'attributes': {
                'website': data.get('website', ''),
                'path': data.get('path', ''),
                'title': data.get('title', ''),
                'content': data.get('content', ''),
                'excerpt': data.get('excerpt', ''),
                'author': data.get('author', ''),
                'categories': data.get('categories', []),
                'tags': data.get('tags', []),
                'status': data.get('status', 'draft'),
                'meta': data.get('meta', {}),
                'wordpress_id': wordpress_data.get('post_id') if wordpress_data else None
            }
        }

    def get_resources(self, type: str, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get website resources"""
        # This would typically fetch from a database
        # For now, we'll return an empty list
        return []

    def get_resource(self, type: str, id: str) -> Optional[Dict[str, Any]]:
        """Get website resource by ID"""
        # This would typically fetch from a database
        # For now, we'll return None
        return None

    def create_resource(self, type: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create website resource"""
        try:
            if type == 'websites.website':
                wordpress_data = self._sync_with_wordpress('website', 'create', {
                    'domain': data['domain'],
                    'title': data['title'],
                    'theme': data.get('theme', '')
                })
                return self._map_website(data, wordpress_data)

            elif type == 'websites.page':
                wordpress_data = self._sync_with_wordpress('page', 'create', {
                    'title': data['title'],
                    'content': data['content'],
                    'status': data['status'],
                    'path': data['path'],
                    'meta': data.get('meta', {})
                })
                return self._map_page(data, wordpress_data)

            elif type == 'websites.post':
                wordpress_data = self._sync_with_wordpress('post', 'create', {
                    'title': data['title'],
                    'content': data['content'],
                    'status': data['status'],
                    'path': data['path'],
                    'excerpt': data.get('excerpt', ''),
                    'author': data.get('author', ''),
                    'categories': data.get('categories', []),
                    'tags': data.get('tags', []),
                    'meta': data.get('meta', {})
                })
                return self._map_post(data, wordpress_data)

        except Exception:
            return None

        return None

    def update_resource(self, type: str, id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update website resource"""
        try:
            if type == 'websites.website':
                wordpress_data = self._sync_with_wordpress('website', 'update', {
                    'id': data.get('wordpress_id'),
                    'domain': data['domain'],
                    'title': data['title'],
                    'theme': data.get('theme', '')
                })
                return self._map_website(data, wordpress_data)

            elif type == 'websites.page':
                wordpress_data = self._sync_with_wordpress('page', 'update', {
                    'id': data.get('wordpress_id'),
                    'title': data['title'],
                    'content': data['content'],
                    'status': data['status'],
                    'path': data['path'],
                    'meta': data.get('meta', {})
                })
                return self._map_page(data, wordpress_data)

            elif type == 'websites.post':
                wordpress_data = self._sync_with_wordpress('post', 'update', {
                    'id': data.get('wordpress_id'),
                    'title': data['title'],
                    'content': data['content'],
                    'status': data['status'],
                    'path': data['path'],
                    'excerpt': data.get('excerpt', ''),
                    'author': data.get('author', ''),
                    'categories': data.get('categories', []),
                    'tags': data.get('tags', []),
                    'meta': data.get('meta', {})
                })
                return self._map_post(data, wordpress_data)

        except Exception:
            return None

        return None

    def delete_resource(self, type: str, id: str) -> bool:
        """Delete website resource"""
        try:
            if type == 'websites.website':
                self._sync_with_wordpress('website', 'delete', {'id': id})
                return True

            elif type == 'websites.page':
                self._sync_with_wordpress('page', 'delete', {'id': id})
                return True

            elif type == 'websites.post':
                self._sync_with_wordpress('post', 'delete', {'id': id})
                return True

        except Exception:
            return False

        return False

    def serve_content(self, domain: str, path: str) -> Optional[Dict[str, Any]]:
        """Serve website content for given domain and path"""
        # This would typically fetch from a database and return content
        # For now, we'll return None
        return None

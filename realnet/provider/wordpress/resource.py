from typing import Dict, List, Any, Optional
from realnet.core.type import Type
from realnet.core.provider import ContextProvider
from .client import WordPressClient

class WordPressProvider(ContextProvider):
    def __init__(self, context: Dict[str, Any]):
        super().__init__(context)
        base_url = context.get('wordpress_url', 'http://wordpress.local')
        username = context.get('wordpress_admin_user', 'admin')
        password = context.get('wordpress_admin_pass', 'admin')
        
        self.client = WordPressClient(base_url)
        self.client.authenticate(username, password)

    def get_items(self, type_name: str, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get items based on type."""
        if type_name == 'wordpress.site':
            return self._map_sites(self.client.get_sites())
        elif type_name == 'wordpress.post':
            site_id = query.get('site_id', 1) if query else 1
            return self._map_posts(self.client.get_posts(site_id, 'posts'))
        elif type_name == 'wordpress.page':
            site_id = query.get('site_id', 1) if query else 1
            return self._map_posts(self.client.get_posts(site_id, 'pages'))
        elif type_name == 'wordpress.user':
            return self._map_users(self.client.get_users())
        return []

    def get_item(self, type_name: str, id: str) -> Optional[Dict[str, Any]]:
        """Get a specific item."""
        parts = id.split('/')
        if type_name == 'wordpress.site':
            sites = self.client.get_sites()
            for site in sites:
                if str(site['id']) == parts[0]:
                    return self._map_site(site)
        elif type_name == 'wordpress.post':
            if len(parts) == 2:  # site_id/post_id
                site_id, post_id = parts
                posts = self.client.get_posts(int(site_id), 'posts')
                for post in posts:
                    if str(post['id']) == post_id:
                        return self._map_post(post, site_id)
        elif type_name == 'wordpress.page':
            if len(parts) == 2:  # site_id/page_id
                site_id, page_id = parts
                pages = self.client.get_posts(int(site_id), 'pages')
                for page in pages:
                    if str(page['id']) == page_id:
                        return self._map_post(page, site_id)
        elif type_name == 'wordpress.user':
            users = self.client.get_users()
            for user in users:
                if str(user['id']) == parts[0]:
                    return self._map_user(user)
        return None

    def create_item(self, type_name: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new item."""
        if type_name == 'wordpress.site':
            site = self.client.create_site(self._unmap_site(data))
            return self._map_site(site)
        elif type_name == 'wordpress.post':
            site_id = data.get('site_id', 1)
            post = self.client.create_post(site_id, self._unmap_post(data), 'posts')
            return self._map_post(post, site_id)
        elif type_name == 'wordpress.page':
            site_id = data.get('site_id', 1)
            page = self.client.create_post(site_id, self._unmap_post(data), 'pages')
            return self._map_post(page, site_id)
        elif type_name == 'wordpress.user':
            user = self.client.create_user(self._unmap_user(data))
            return self._map_user(user)
        return None

    def update_item(self, type_name: str, id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing item."""
        parts = id.split('/')
        if type_name == 'wordpress.post' and len(parts) == 2:
            site_id, post_id = parts
            post = self.client.update_post(int(site_id), int(post_id), self._unmap_post(data), 'posts')
            return self._map_post(post, site_id)
        elif type_name == 'wordpress.page' and len(parts) == 2:
            site_id, page_id = parts
            page = self.client.update_post(int(site_id), int(page_id), self._unmap_post(data), 'pages')
            return self._map_post(page, site_id)
        elif type_name == 'wordpress.user':
            user = self.client.update_user(int(parts[0]), self._unmap_user(data))
            return self._map_user(user)
        return None

    def delete_item(self, type_name: str, id: str) -> bool:
        """Delete an item."""
        parts = id.split('/')
        if type_name == 'wordpress.site':
            return self.client.delete_site(int(parts[0]))
        elif type_name == 'wordpress.post' and len(parts) == 2:
            site_id, post_id = parts
            return self.client.delete_post(int(site_id), int(post_id), 'posts')
        elif type_name == 'wordpress.page' and len(parts) == 2:
            site_id, page_id = parts
            return self.client.delete_post(int(site_id), int(page_id), 'pages')
        elif type_name == 'wordpress.user':
            return self.client.delete_user(int(parts[0]))
        return False

    def _map_sites(self, sites: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map WordPress sites to realnet format."""
        return [self._map_site(site) for site in sites]

    def _map_site(self, site: Dict[str, Any]) -> Dict[str, Any]:
        """Map a WordPress site to realnet format."""
        return {
            'id': str(site['id']),
            'name': site['name'],
            'description': site.get('description', ''),
            'url': site['url'],
            'path': site.get('path', '/'),
            'status': site.get('status', 'active')
        }

    def _unmap_site(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert realnet site format to WordPress format."""
        return {
            'name': data['name'],
            'description': data.get('description', ''),
            'url': data.get('url', ''),
            'path': data.get('path', '/')
        }

    def _map_posts(self, posts: List[Dict[str, Any]], site_id: str = '1') -> List[Dict[str, Any]]:
        """Map WordPress posts to realnet format."""
        return [self._map_post(post, site_id) for post in posts]

    def _map_post(self, post: Dict[str, Any], site_id: str) -> Dict[str, Any]:
        """Map a WordPress post to realnet format."""
        return {
            'id': f"{site_id}/{post['id']}",
            'title': post['title']['rendered'],
            'content': post['content']['rendered'],
            'excerpt': post['excerpt']['rendered'],
            'status': post['status'],
            'author': str(post['author']),
            'date': post['date'],
            'modified': post['modified'],
            'site_id': site_id
        }

    def _unmap_post(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert realnet post format to WordPress format."""
        return {
            'title': data['title'],
            'content': data['content'],
            'excerpt': data.get('excerpt', ''),
            'status': data.get('status', 'publish'),
            'author': int(data.get('author', 1))
        }

    def _map_users(self, users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map WordPress users to realnet format."""
        return [self._map_user(user) for user in users]

    def _map_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Map a WordPress user to realnet format."""
        return {
            'id': str(user['id']),
            'username': user['username'],
            'name': user['name'],
            'email': user['email'],
            'roles': user.get('roles', []),
            'url': user.get('url', ''),
            'description': user.get('description', ''),
            'registered_date': user.get('registered_date', '')
        }

    def _unmap_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert realnet user format to WordPress format."""
        return {
            'username': data['username'],
            'name': data['name'],
            'email': data['email'],
            'roles': data.get('roles', ['subscriber']),
            'url': data.get('url', ''),
            'description': data.get('description', '')
        }

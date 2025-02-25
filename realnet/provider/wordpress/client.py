import requests
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin

class WordPressClient:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.token = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with WordPress using JWT"""
        auth_url = urljoin(self.base_url, '/wp-json/jwt-auth/v1/token')
        response = requests.post(auth_url, json={
            'username': self.username,
            'password': self.password
        })
        response.raise_for_status()
        self.token = response.json()['token']

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an authenticated request to the WordPress API"""
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        url = urljoin(self.base_url, f'/wp-json/wp/v2/{endpoint.lstrip("/")}')
        
        if 'headers' in kwargs:
            kwargs['headers'].update(headers)
        else:
            kwargs['headers'] = headers

        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

    def get_sites(self) -> List[Dict[str, Any]]:
        """Get list of sites in multisite installation"""
        return self._request('GET', '/sites')

    def get_site(self, site_id: int) -> Dict[str, Any]:
        """Get site details"""
        return self._request('GET', f'/sites/{site_id}')

    def get_pages(self, site_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get list of pages, optionally filtered by site"""
        endpoint = f'/sites/{site_id}/pages' if site_id else '/pages'
        return self._request('GET', endpoint)

    def get_page(self, page_id: int, site_id: Optional[int] = None) -> Dict[str, Any]:
        """Get page details"""
        endpoint = f'/sites/{site_id}/pages/{page_id}' if site_id else f'/pages/{page_id}'
        return self._request('GET', endpoint)

    def create_page(self, data: Dict[str, Any], site_id: Optional[int] = None) -> Dict[str, Any]:
        """Create a new page"""
        endpoint = f'/sites/{site_id}/pages' if site_id else '/pages'
        return self._request('POST', endpoint, json=data)

    def update_page(self, page_id: int, data: Dict[str, Any], site_id: Optional[int] = None) -> Dict[str, Any]:
        """Update an existing page"""
        endpoint = f'/sites/{site_id}/pages/{page_id}' if site_id else f'/pages/{page_id}'
        return self._request('PUT', endpoint, json=data)

    def delete_page(self, page_id: int, site_id: Optional[int] = None) -> Dict[str, Any]:
        """Delete a page"""
        endpoint = f'/sites/{site_id}/pages/{page_id}' if site_id else f'/pages/{page_id}'
        return self._request('DELETE', endpoint)

    def get_posts(self, site_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get list of posts, optionally filtered by site"""
        endpoint = f'/sites/{site_id}/posts' if site_id else '/posts'
        return self._request('GET', endpoint)

    def get_post(self, post_id: int, site_id: Optional[int] = None) -> Dict[str, Any]:
        """Get post details"""
        endpoint = f'/sites/{site_id}/posts/{post_id}' if site_id else f'/posts/{post_id}'
        return self._request('GET', endpoint)

    def create_post(self, data: Dict[str, Any], site_id: Optional[int] = None) -> Dict[str, Any]:
        """Create a new post"""
        endpoint = f'/sites/{site_id}/posts' if site_id else '/posts'
        return self._request('POST', endpoint, json=data)

    def update_post(self, post_id: int, data: Dict[str, Any], site_id: Optional[int] = None) -> Dict[str, Any]:
        """Update an existing post"""
        endpoint = f'/sites/{site_id}/posts/{post_id}' if site_id else f'/posts/{post_id}'
        return self._request('PUT', endpoint, json=data)

    def delete_post(self, post_id: int, site_id: Optional[int] = None) -> Dict[str, Any]:
        """Delete a post"""
        endpoint = f'/sites/{site_id}/posts/{post_id}' if site_id else f'/posts/{post_id}'
        return self._request('DELETE', endpoint)

    def get_users(self, site_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get list of users, optionally filtered by site"""
        endpoint = f'/sites/{site_id}/users' if site_id else '/users'
        return self._request('GET', endpoint)

    def get_user(self, user_id: int, site_id: Optional[int] = None) -> Dict[str, Any]:
        """Get user details"""
        endpoint = f'/sites/{site_id}/users/{user_id}' if site_id else f'/users/{user_id}'
        return self._request('GET', endpoint)

    def create_user(self, data: Dict[str, Any], site_id: Optional[int] = None) -> Dict[str, Any]:
        """Create a new user"""
        endpoint = f'/sites/{site_id}/users' if site_id else '/users'
        return self._request('POST', endpoint, json=data)

    def update_user(self, user_id: int, data: Dict[str, Any], site_id: Optional[int] = None) -> Dict[str, Any]:
        """Update an existing user"""
        endpoint = f'/sites/{site_id}/users/{user_id}' if site_id else f'/users/{user_id}'
        return self._request('PUT', endpoint, json=data)

    def delete_user(self, user_id: int, site_id: Optional[int] = None) -> Dict[str, Any]:
        """Delete a user"""
        endpoint = f'/sites/{site_id}/users/{user_id}' if site_id else f'/users/{user_id}'
        return self._request('DELETE', endpoint)

from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlparse
from http import HTTPStatus
from realnet.provider.websites.resource import WebsitesResourceProvider
from realnet.core.type import Type, Instance

class WebsitesRouter:
    def __init__(self):
        self.provider = WebsitesResourceProvider()
        
        # Define content type for responses
        self.content_type = Type('Content', 'Item', {
            'module': 'websites.content',
            'title': '',
            'content': '',
            'layout': '',
            'meta': {},
            'website': None,
            'author': '',
            'categories': [],
            'tags': [],
            'excerpt': '',
            'status': 'published'
        })

    def _parse_request(self, request: Dict[str, Any]) -> Tuple[str, str]:
        """Parse request to extract domain and path"""
        host = request.get('headers', {}).get('Host', '')
        path = request.get('path', '')

        # Handle port in host if present
        domain = host.split(':')[0] if ':' in host else host

        # Clean up path
        if not path:
            path = '/'
        elif path.endswith('/') and path != '/':
            path = path.rstrip('/')

        return domain, path

    def _create_response(self, content: Optional[Dict[str, Any]], status: int = HTTPStatus.OK) -> Dict[str, Any]:
        """Create HTTP response"""
        if not content:
            return {
                'statusCode': HTTPStatus.NOT_FOUND,
                'headers': {
                    'Content-Type': 'text/html'
                },
                'body': '<h1>404 Not Found</h1>'
            }

        try:
            # Create content instance
            content_instance = Instance(
                content.get('id', ''),
                self.content_type,
                content.get('title', ''),
                content.get('attributes', {})
            )
            
            # Create response with instance
            return {
                'statusCode': status,
                'headers': {
                    'Content-Type': 'text/html',
                    'X-Realnet-Type': content.get('type', ''),
                    'X-Realnet-ID': content.get('id', ''),
                    'X-Realnet-Website': content.get('attributes', {}).get('website', '')
                },
                'body': self._render_content(content_instance)
            }
        except Exception:
            return {
                'statusCode': HTTPStatus.NOT_FOUND,
                'headers': {
                    'Content-Type': 'text/html'
                },
                'body': '<h1>404 Not Found</h1>'
            }

    def _render_content(self, content: Instance) -> str:
        """Render content as HTML"""
        try:
            if content.type.name == 'websites.page':
                return self._render_page(content)
            elif content.type.name == 'websites.post':
                return self._render_post(content)
            return ''
        except Exception:
            return ''

    def _render_page(self, content: Instance) -> str:
        """Render page content"""
        layout = content.attributes.get('layout', 'default')
        meta = content.attributes.get('meta', {})
        
        # Basic HTML template
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{content.attributes.get('title', '')}</title>
            {''.join(f'<meta name="{k}" content="{v}">' for k, v in meta.items() if isinstance(v, str))}
        </head>
        <body class="layout-{layout}">
            <main>
                <article>
                    <h1>{content.attributes.get('title', '')}</h1>
                    <div class="content">
                        {content.attributes.get('content', '')}
                    </div>
                </article>
            </main>
        </body>
        </html>
        """
        return html

    def _render_post(self, content: Instance) -> str:
        """Render post content"""
        meta = content.attributes.get('meta', {})
        categories = content.attributes.get('categories', [])
        tags = content.attributes.get('tags', [])
        
        # Basic HTML template
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{content.attributes.get('title', '')}</title>
            {''.join(f'<meta name="{k}" content="{v}">' for k, v in meta.items() if isinstance(v, str))}
        </head>
        <body class="post">
            <main>
                <article>
                    <header>
                        <h1>{content.attributes.get('title', '')}</h1>
                        <div class="meta">
                            {f'<span class="author">{content.attributes["author"]}</span>' if content.attributes.get('author') else ''}
                            {f'<span class="categories">{", ".join(categories)}</span>' if categories else ''}
                            {f'<span class="tags">{", ".join(tags)}</span>' if tags else ''}
                        </div>
                    </header>
                    {f'<div class="excerpt">{content.attributes["excerpt"]}</div>' if content.attributes.get('excerpt') else ''}
                    <div class="content">
                        {content.attributes.get('content', '')}
                    </div>
                </article>
            </main>
        </body>
        </html>
        """
        return html

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming HTTP request"""
        try:
            # Parse request
            domain, path = self._parse_request(request)
            if not domain:
                return self._create_response(None)

            # Get content from provider
            content = self.provider.serve_content(domain, path)
            if not content:
                return self._create_response(None)

            # Create response
            return self._create_response(content)

        except Exception as e:
            return {
                'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR,
                'headers': {
                    'Content-Type': 'text/html'
                },
                'body': f'<h1>500 Internal Server Error</h1><p>{str(e)}</p>'
            }

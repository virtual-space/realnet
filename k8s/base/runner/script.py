import json

def handle_message(message):
    """Handle incoming message from MQTT topic"""
    try:
        # Parse message
        data = json.loads(message)
        action = data.get('action')
        content_type = data.get('type')
        content = data.get('content', {})

        # Validate required fields
        if not action or not content_type:
            raise ValueError("Missing required fields: action and type")

        # Handle WordPress content sync
        if content_type.startswith('websites.'):
            sync_wordpress_content(action, content_type, content)
        else:
            publish({
                'status': 'error',
                'message': f'Unsupported content type: {content_type}'
            })

    except Exception as e:
        publish({
            'status': 'error',
            'message': str(e)
        })

def sync_wordpress_content(action, content_type, content):
    """Sync content with WordPress"""
    try:
        # Map content type to WordPress type
        wp_type = content_type.split('.')[1]  # e.g. websites.page -> page
        
        # Prepare response data
        response = {
            'status': 'success',
            'type': content_type,
            'action': action
        }

        # Handle different content types
        if wp_type == 'website':
            response['data'] = sync_website(action, content)
        elif wp_type == 'page':
            response['data'] = sync_page(action, content)
        elif wp_type == 'post':
            response['data'] = sync_post(action, content)
        else:
            raise ValueError(f'Unsupported WordPress type: {wp_type}')

        # Publish response
        publish(response)

    except Exception as e:
        publish({
            'status': 'error',
            'type': content_type,
            'action': action,
            'message': str(e)
        })

def sync_website(action, content):
    """Sync website with WordPress"""
    if action == 'create':
        return {
            'id': content.get('id'),
            'domain': content.get('domain'),
            'title': content.get('title'),
            'theme': content.get('theme'),
            'status': content.get('status', 'draft')
        }
    elif action == 'update':
        return {
            'id': content.get('id'),
            'domain': content.get('domain'),
            'title': content.get('title'),
            'theme': content.get('theme'),
            'status': content.get('status', 'draft')
        }
    elif action == 'delete':
        return {
            'id': content.get('id')
        }
    else:
        raise ValueError(f'Unsupported action for website: {action}')

def sync_page(action, content):
    """Sync page with WordPress"""
    if action == 'create':
        return {
            'id': content.get('id'),
            'title': content.get('title'),
            'content': content.get('content'),
            'path': content.get('path'),
            'layout': content.get('layout'),
            'status': content.get('status', 'draft'),
            'meta': content.get('meta', {})
        }
    elif action == 'update':
        return {
            'id': content.get('id'),
            'title': content.get('title'),
            'content': content.get('content'),
            'path': content.get('path'),
            'layout': content.get('layout'),
            'status': content.get('status', 'draft'),
            'meta': content.get('meta', {})
        }
    elif action == 'delete':
        return {
            'id': content.get('id')
        }
    else:
        raise ValueError(f'Unsupported action for page: {action}')

def sync_post(action, content):
    """Sync post with WordPress"""
    if action == 'create':
        return {
            'id': content.get('id'),
            'title': content.get('title'),
            'content': content.get('content'),
            'path': content.get('path'),
            'excerpt': content.get('excerpt'),
            'author': content.get('author'),
            'categories': content.get('categories', []),
            'tags': content.get('tags', []),
            'status': content.get('status', 'draft'),
            'meta': content.get('meta', {})
        }
    elif action == 'update':
        return {
            'id': content.get('id'),
            'title': content.get('title'),
            'content': content.get('content'),
            'path': content.get('path'),
            'excerpt': content.get('excerpt'),
            'author': content.get('author'),
            'categories': content.get('categories', []),
            'tags': content.get('tags', []),
            'status': content.get('status', 'draft'),
            'meta': content.get('meta', {})
        }
    elif action == 'delete':
        return {
            'id': content.get('id')
        }
    else:
        raise ValueError(f'Unsupported action for post: {action}')

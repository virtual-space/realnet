import mimetypes

from flask import jsonify, request
from realnet.resource.items.items import Items

class Files(Items):
    
    def get(self, module, endpoint, args, path=None, content_type='text/html'):
        if path == 'upload-url':
            attributes = dict()
            attributes['filename'] = args.get('filename', 'file.tmp')
            attributes['filesize'] = args.get('size', 0)
            content_type = mimetypes.guess_type(attributes['filename'].lower())[0]
            if not content_type:
                if attributes['filename'].lower().endswith('heic'):
                    content_type = 'image/heic'
                else:
                    content_type = 'application/octet-stream'
            
            arguments = dict()
            # Get type from args or determine from content
            typename = args.get('type')
            if not typename:
                typename = 'File'
                if content_type.startswith('image/'):
                    typename = 'Image'
                elif content_type.startswith('application/pdf') or content_type.startswith('text/plain') or attributes['filename'].endswith('.md'):
                    typename = 'Document'
                    if attributes['filename'].endswith('.md'):
                        content_type = 'text/markdown'
                elif content_type.startswith('text/html'):
                    typename = 'Page'
                elif content_type.startswith('video/'):
                    typename = 'Video'
                elif content_type.startswith('application/zip') or content_type.startswith('application/x-zip-compressed'):
                    typename = 'File'
                elif content_type.startswith('text/csv'):
                    typename = 'File'
                elif attributes['filename'].endswith('.glb') or attributes['filename'].endswith('.gltf'):
                    typename = 'Scene'
            
            attributes['content_type'] = content_type
            arguments['type'] = typename
            # Handle parent_id and target
            parent_id = args.get('parent_id')
            if isinstance(parent_id, list):
                parent_id = parent_id[0] if parent_id else None
            
            target = args.get('target', 'item')
            if isinstance(target, list):
                target = target[0]
            
            print(f"Creating {target} with type: {typename}, parent_id: {parent_id}")  # Debug log
            
            if parent_id:
                if target == 'type':
                    parent_item = module.get_type_by_id(parent_id)
                    if parent_item:
                        arguments['parent_type_id'] = parent_id
                else:
                    parent_item = module.get_item(parent_id)    
                    if parent_item and module.can_account_write_item(module.get_account(), parent_item):
                        arguments['parent_id'] = parent_id
            
            arguments['ip_address'] = args.get('ip_address', None)
            for key, value in args.items():
                if not key in {'filename', 'file_size', 'parent_id', 'type', 'size', 'ip_address'}:
                    attributes[key] = value
            
            arguments['name'] = attributes['filename']
            arguments['attributes'] = attributes
            
            try:
                item = None
                print(f"Creating with arguments: {arguments}")  # Debug log
                if target == 'type':
                    item = module.create_instance(**arguments)
                else:
                    item = module.create_item(**arguments)
                
                if item:
                    print(f"Created {target} with id: {item.id}")  # Debug log
                    return module.get_data_upload_url(item.id)
                else:
                    return jsonify({"error": "Failed to create item"}), 500
            except Exception as e:
                print(f"Error creating item: {str(e)}")  # Debug log
                return jsonify({"error": f"Error creating item: {str(e)}"}), 500

        return self.render_item(module, endpoint, args, path, content_type)

    def post(self, module, endpoint, args, path=None, content_type='text/html'):
        if path == 'upload-confirm':
            # Get item_id from either 'key' (S3 style) or 'item_id' (legacy)
            item_id = args.get('key') or args.get('item_id')
            if not item_id:
                return jsonify({"error": "No item_id or key provided"}), 400
            if isinstance(item_id, list):
                item_id = item_id[0]
            item_id = str(item_id)
            
            # Get target type, defaulting to 'item'
            target = args.get('target', 'item')
            if isinstance(target, list):
                target = target[0]
            
            # Get the item based on target type
            try:
                if target == 'type':
                    print(f"Getting instance with id: {item_id}")  # Debug log
                    item = module.get_instance_by_id(item_id)
                    if not item:
                        return jsonify({"error": f"Instance not found with id: {item_id}"}), 404
                else:
                    print(f"Getting item with id: {item_id}")  # Debug log
                    item = module.get_item(item_id)
                    if not item:
                        return jsonify({"error": f"Item not found with id: {item_id}"}), 404
                
                # Initialize attributes from existing item
                attributes = dict(item.attributes) if item.attributes else {}
                
                # Handle filename
                filename = args.get('filename')
                if isinstance(filename, list):
                    filename = filename[0]
                if filename:
                    attributes['filename'] = filename
                elif 'filename' not in attributes:
                    attributes['filename'] = str(item_id)
                
                # Handle content type
                content_type = args.get('content_type')
                if not content_type and filename:
                    content_type = mimetypes.guess_type(filename.lower())[0]
                    if not content_type:
                        if filename.lower().endswith('heic'):
                            content_type = 'image/heic'
                        else:
                            content_type = 'application/octet-stream'
                if content_type:
                    attributes['content_type'] = content_type
                    attributes['mime_type'] = content_type
                
                # Handle filesize
                filesize = args.get('size')
                if isinstance(filesize, list):
                    filesize = filesize[0]
                if filesize is not None:
                    attributes['content_length'] = filesize
                
                # Add any additional attributes
                for key, value in args.items():
                    if not key in {'filename', 'file_size', 'parent_id', 'type', 'size', 'ip_address', 'content_type'}:
                        attributes[key] = value

                print(f"Updating {target} with attributes: {attributes}")  # Debug log
                
                if target == 'type':
                    module.update_instance(item.id, **{"attributes": attributes})
                else:
                    module.update_item(item.id, **{"attributes": attributes})

                return jsonify(item.to_dict()), 200
                
            except Exception as e:
                print(f"Error processing upload confirm: {str(e)}")  # Debug log
                return jsonify({"error": f"Error processing upload: {str(e)}"}), 500
            # module.create_item(**args)
        elif path and path.endswith('/data'):
            file_id = str(path.split('/')[-2])
            if not file_id:
                return jsonify({"error": "Invalid file path"}), 400
            
            print(f"Processing file upload for id: {file_id}")  # Debug log
            
            try:
                file = module.get_item(file_id)
                if not file:
                    return jsonify({"error": f"File not found with id: {file_id}"}), 404
                
                if not module.can_account_write_item(module.get_account(), file):
                    return jsonify({"error": "Permission denied"}), 403
                
                # Handle file upload from multipart form data
                if 'file' in request.files:
                    print(f"Processing multipart form upload for file: {file_id}")  # Debug log
                    file_data = request.files['file'].read()
                    module.update_data(file.id, file_data)
                    return jsonify(file.to_dict()), 200
                # Handle direct data upload
                elif 'data' in args:
                    print(f"Processing direct data upload for file: {file_id}")  # Debug log
                    module.update_data(file.id, args.get('data'))
                    return jsonify(file.to_dict()), 200
                else:
                    return jsonify({"error": "No file data provided"}), 400
            except Exception as e:
                print(f"Error processing file upload: {str(e)}")  # Debug log
                return jsonify({"error": f"Error processing file upload: {str(e)}"}), 500
                
        return self.render_item(module, endpoint, args, path, content_type)

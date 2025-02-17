from realnet.core.config import Config
from realnet.core.provider import DataProvider
from realnet.core.type import Data

from pathlib import Path
import mimetypes
import os

cfg = Config()

class LocalDataProvider(DataProvider):
    """A DataProvider implementation that stores data in the local filesystem."""
    
    def __init__(self, base_dir=None):
        """Initialize the LocalDataProvider with a base directory for storage.
        
        Args:
            base_dir (str, optional): Base directory for file storage. 
                                    Defaults to REALNET_STORAGE_PATH config or 'data'.
        """
        cfg = Config()
        self.base_dir = Path(base_dir if base_dir else cfg.get_storage_path() or 'data').resolve()
        # Create base directory if it doesn't exist
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, id):
        """Get the full file path for a given ID, ensuring it's within base_dir.
        
        Args:
            id (str): The file identifier
            
        Returns:
            Path: Resolved path object for the file
        """
        # Resolve path to ensure it's within base_dir
        file_path = (self.base_dir / id).resolve()
        if not str(file_path).startswith(str(self.base_dir)):
            raise ValueError("Invalid file path: Attempted directory traversal")
        return file_path

    def get_data(self, id):
        """Retrieve data from the filesystem by ID.
        
        Args:
            id (str): The file identifier
            
        Returns:
            Data: Data object containing file contents and metadata
            None: If file doesn't exist
        """
        try:
            file_path = self._get_file_path(id)
            if not file_path.exists():
                return None
                
            # Detect mimetype
            mimetype, _ = mimetypes.guess_type(str(file_path))
            if not mimetype:
                mimetype = 'application/octet-stream'
                
            # Get file size
            file_size = file_path.stat().st_size
            
            # Read file contents
            with open(file_path, 'rb') as f:
                content = f.read()
                
            return Data(id, mimetype, file_size, content)
        except Exception as e:
            print(f"Error reading file {id}: {str(e)}")
            return None

    def update_data(self, id, storage):
        """Store or update data in the filesystem.
        
        Args:
            id (str): The file identifier
            storage (bytes): The data to store
        """
        try:
            file_path = self._get_file_path(id)
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file contents
            with open(file_path, 'wb') as f:
                f.write(storage)
        except Exception as e:
            print(f"Error writing file {id}: {str(e)}")
            raise

    def delete_data(self, id):
        """Delete data from the filesystem.
        
        Args:
            id (str): The file identifier
        """
        try:
            file_path = self._get_file_path(id)
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            print(f"Error deleting file {id}: {str(e)}")
            raise

    def get_data_upload_url(self, id):
        """Get upload URL for local file storage.
        
        For local filesystem, this returns a direct upload endpoint URL
        instead of a presigned S3 URL.
        
        Args:
            id (str): The file identifier
            
        Returns:
            dict: Dictionary containing upload endpoint information
        """
        try:
            # Get the file path to check if it exists
            file_path = self._get_file_path(id)
            file_size = file_path.stat().st_size if file_path.exists() else 0
            filename = file_path.name if file_path.exists() else f"{id}"
            
            # Detect mimetype
            content_type, _ = mimetypes.guess_type(filename)
            if not content_type:
                content_type = 'application/octet-stream'
            
            return {
                'url': f'/files/{id}/data',
                'fields': {
                    'key': id,  # Use 'key' to match S3 provider format
                    'filename': filename,
                    'size': file_size,
                    'content_type': content_type
                },
                'local': True,
                'method': 'POST'
            }
        except Exception as e:
            print(f"Error getting upload path for {id}: {str(e)}")
            return None

    def confirm_data_upload(self, id):
        """Confirm data upload completion.
        
        This is a no-op for local filesystem since we don't need upload confirmation
        like we do with S3.
        
        Args:
            id (str): The file identifier
        """
        pass

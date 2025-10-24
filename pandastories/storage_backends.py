import os
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from django.core.files.base import ContentFile
from supabase import create_client, Client
from io import BytesIO
import logging

logger = logging.getLogger(__name__)


@deconstructible
class SupabaseStorage(Storage):
    """Custom storage backend for Supabase Storage"""
    
    def __init__(self):
        self.supabase_url = os.environ.get('SUPABASE_URL')
        self.supabase_key = os.environ.get('SUPABASE_KEY')
        self.bucket_name = os.environ.get('SUPABASE_BUCKET', 'media')
        
        if self.supabase_url and self.supabase_key:
            try:
                self.client: Client = create_client(self.supabase_url, self.supabase_key)
                logger.info(f"Supabase storage initialized for bucket: {self.bucket_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                self.client = None
        else:
            logger.warning("Supabase credentials not found, storage will not work")
            self.client = None
    
    def _save(self, name, content):
        """Save file to Supabase Storage"""
        if not self.client:
            raise ValueError("Supabase client not configured. Set SUPABASE_URL and SUPABASE_KEY.")
        
        try:
            # Read file content
            if hasattr(content, 'read'):
                file_content = content.read()
            else:
                file_content = content
            
            # Upload to Supabase (upsert=True allows overwriting)
            response = self.client.storage.from_(self.bucket_name).upload(
                name,
                file_content,
                file_options={
                    "content-type": self._get_content_type(name),
                    "upsert": "true"
                }
            )
            
            logger.info(f"Successfully uploaded {name} to Supabase bucket {self.bucket_name}")
            return name
            
        except Exception as e:
            logger.error(f"Failed to upload {name} to Supabase: {e}")
            raise
    
    def _open(self, name, mode='rb'):
        """Retrieve file from Supabase Storage"""
        if not self.client:
            raise ValueError("Supabase client not configured")
        
        response = self.client.storage.from_(self.bucket_name).download(name)
        return BytesIO(response)
    
    def delete(self, name):
        """Delete file from Supabase Storage"""
        if not self.client:
            return
        
        self.client.storage.from_(self.bucket_name).remove([name])
    
    def exists(self, name):
        """Check if file exists in Supabase Storage"""
        if not self.client:
            return False
        
        try:
            files = self.client.storage.from_(self.bucket_name).list()
            return any(f['name'] == name for f in files)
        except:
            return False
    
    def url(self, name):
        """Get public URL for file"""
        if not self.client:
            return f"/media/{name}"
        
        return self.client.storage.from_(self.bucket_name).get_public_url(name)
    
    def size(self, name):
        """Get file size"""
        if not self.client:
            return 0
        
        try:
            files = self.client.storage.from_(self.bucket_name).list()
            for f in files:
                if f['name'] == name:
                    return f.get('metadata', {}).get('size', 0)
        except:
            pass
        return 0
    
    def _get_content_type(self, name):
        """Determine content type from file extension"""
        ext = name.split('.')[-1].lower()
        content_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'svg': 'image/svg+xml',
            'pdf': 'application/pdf',
            'mp4': 'video/mp4',
            'mp3': 'audio/mpeg',
        }
        return content_types.get(ext, 'application/octet-stream')

#!/usr/bin/env python
"""
Upload static files to Supabase Storage
Run this locally: python upload_static_to_supabase.py
"""
import os
import sys
from pathlib import Path
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.environ.get('SUPABASE_URL')
# Use service_role key for uploads (has full access)
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY') or os.environ.get('SUPABASE_KEY')
BUCKET_NAME = 'static'

def get_content_type(extension):
    """Get content type from file extension"""
    content_types = {
        '.css': 'text/css',
        '.js': 'application/javascript',
        '.json': 'application/json',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.svg': 'image/svg+xml',
        '.woff': 'font/woff',
        '.woff2': 'font/woff2',
        '.ttf': 'font/ttf',
        '.eot': 'application/vnd.ms-fontobject',
        '.html': 'text/html',
        '.txt': 'text/plain',
        '.ico': 'image/x-icon',
        '.map': 'application/json',
    }
    return content_types.get(extension.lower(), 'application/octet-stream')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    sys.exit(1)

# Initialize Supabase client
client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Collect static files first
print("Collecting static files...")
os.system("python manage.py collectstatic --noinput --clear")

# Upload static files
staticfiles_dir = Path('staticfiles')
if not staticfiles_dir.exists():
    print(f"Error: {staticfiles_dir} does not exist")
    sys.exit(1)

print(f"\nUploading files from {staticfiles_dir} to Supabase bucket '{BUCKET_NAME}'...")

uploaded_count = 0
failed_count = 0

for file_path in staticfiles_dir.rglob('*'):
    if file_path.is_file():
        # Get relative path for Supabase
        relative_path = str(file_path.relative_to(staticfiles_dir)).replace('\\', '/')
        
        try:
            # Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Upload to Supabase
            client.storage.from_(BUCKET_NAME).upload(
                relative_path,
                file_content,
                file_options={
                    "content-type": get_content_type(file_path.suffix),
                    "upsert": "true"
                }
            )
            
            uploaded_count += 1
            if uploaded_count % 10 == 0:
                print(f"Uploaded {uploaded_count} files...")
                
        except Exception as e:
            print(f"Failed to upload {relative_path}: {e}")
            failed_count += 1

print(f"\n✓ Upload complete!")
print(f"  Uploaded: {uploaded_count} files")
print(f"  Failed: {failed_count} files")

# import os
# from django.core.files.storage import default_storage
# from django.core.files.base import ContentFile

# UPLOAD_DIR = "uploaded_files"

# def handle_uploaded_file(uploaded_file):
#     """
#     Saves uploaded file and returns its saved path.
#     """
#     if not os.path.exists(UPLOAD_DIR):
#         os.makedirs(UPLOAD_DIR)

#     file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
#     path = default_storage.save(file_path, ContentFile(uploaded_file.read()))
#     return path










import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import uuid

# Create uploaded_files directory if it doesn't exist
UPLOAD_DIR = "uploaded_files"

def ensure_upload_dir():
    """Ensure upload directory exists."""
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
        print(f"📁 Created upload directory: {UPLOAD_DIR}")

def handle_uploaded_file(uploaded_file):
    """
    Saves uploaded file and returns its saved path.
    Adds unique identifier to avoid filename conflicts.
    """
    ensure_upload_dir()
    
    # Generate unique filename to avoid conflicts
    original_name = uploaded_file.name
    file_extension = os.path.splitext(original_name)[1]
    unique_id = uuid.uuid4().hex[:8]
    safe_filename = f"{unique_id}_{original_name}"
    
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    # Save file
    path = default_storage.save(file_path, ContentFile(uploaded_file.read()))
    
    print(f"💾 Saved uploaded file: {original_name} -> {path}")
    return path

def get_uploaded_file_path(filename):
    """
    Get full path for an uploaded file.
    """
    return os.path.join(UPLOAD_DIR, filename)

def list_uploaded_files():
    """
    List all uploaded files.
    """
    ensure_upload_dir()
    return os.listdir(UPLOAD_DIR)

def delete_uploaded_file(filename):
    """
    Delete an uploaded file.
    """
    try:
        file_path = get_uploaded_file_path(filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        print(f"❌ Error deleting file {filename}: {e}")
    return False
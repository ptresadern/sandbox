import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-please-change')

    # Authentication
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
    USER_USERNAME = os.getenv('USER_USERNAME', 'user')
    USER_PASSWORD = os.getenv('USER_PASSWORD', 'user123')

    # Storage
    STORAGE_TYPE = os.getenv('STORAGE_TYPE', 'local')  # 'local' or 's3'
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'photo-gallery')
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size

    # AWS S3
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

    # Allowed file extensions
    ALLOWED_EXTENSIONS = {
        'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp',  # Images
        'mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm'  # Videos
    }

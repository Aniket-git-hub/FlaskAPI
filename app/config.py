# app/config.py

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/postgres')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis')
    
    # Use absolute paths for Docker volumes
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/app/uploads')
    LOGO_FOLDER = os.environ.get('LOGO_FOLDER', '/app/logos')
    PROCESSED_FOLDER = os.environ.get('PROCESSED_FOLDER', '/app/processed_videos')
    
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

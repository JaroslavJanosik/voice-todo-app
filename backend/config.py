import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / 'instance'
UPLOADS_DIR = BASE_DIR / 'uploads'


class Config:
    APP_NAME = os.environ.get('APP_NAME', 'voice-todo-app-backend')
    APP_VERSION = os.environ.get('APP_VERSION', '1.0.0')
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'please-change-this-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{INSTANCE_DIR / "database.db"}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 25 * 1024 * 1024))
    UPLOAD_FOLDER = str(UPLOADS_DIR)
    ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a', 'webm', 'mp4'}
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.environ.get(
            'CORS_ORIGINS',
            'http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173,http://127.0.0.1:4173,http://localhost:3000'
        ).split(',')
        if origin.strip()
    ]
    WHISPER_MODEL = os.environ.get('WHISPER_MODEL', 'base')

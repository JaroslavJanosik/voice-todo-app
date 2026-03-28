import pytest

from app import create_app
from models.model import db


class TestConfig:
    TESTING = True
    APP_NAME = 'voice-todo-app-backend-test'
    APP_VERSION = 'test'
    SECRET_KEY = 'test-secret'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024
    UPLOAD_FOLDER = '/tmp/voice-todo-test-uploads'
    ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a', 'webm', 'mp4'}
    CORS_ORIGINS = ['http://localhost:5173']
    WHISPER_MODEL = 'base'


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()

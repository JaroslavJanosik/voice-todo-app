from pathlib import Path
from typing import Optional

from flask import Flask
from flask_cors import CORS
from sqlalchemy import text
from werkzeug.exceptions import HTTPException

from api_response import failure_response
from exceptions import ApiError
from models.model import db
from routes.audio_routes import audio
from config import Config
from routes.system_routes import system
from routes.task_routes import tasks


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    CORS(app, resources={r"/*": {"origins": app.config['CORS_ORIGINS']}})

    app.register_blueprint(tasks, url_prefix='/tasks')
    app.register_blueprint(audio)
    app.register_blueprint(system)

    with app.app_context():
        _ensure_runtime_directories(app)
        db.create_all()
        _ensure_database_guards(app)

    register_error_handlers(app)

    return app


def _ensure_runtime_directories(app: Flask):
    Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)

    sqlite_path = _get_sqlite_database_path(app.config['SQLALCHEMY_DATABASE_URI'])
    if sqlite_path is not None:
        sqlite_path.parent.mkdir(parents=True, exist_ok=True)


def _get_sqlite_database_path(database_uri: str) -> Optional[Path]:
    sqlite_prefix = 'sqlite:///'
    if not database_uri.startswith(sqlite_prefix):
        return None

    return Path(database_uri[len(sqlite_prefix):]).expanduser()


def _ensure_database_guards(app: Flask):
    try:
        db.session.execute(
            text(
                'CREATE UNIQUE INDEX IF NOT EXISTS uq_task_normalized_description '
                'ON task (lower(trim(description)))'
            )
        )
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        app.logger.exception('Failed to create database guards.')
        raise RuntimeError('Database guards could not be created.') from exc


def register_error_handlers(app: Flask):
    @app.errorhandler(ApiError)
    def api_error(error):
        return failure_response(error.error_messages, status_code=error.status_code)

    @app.errorhandler(HTTPException)
    def http_error(error):
        if error.code == 413:
            return failure_response('Uploaded file is too large.', status_code=413)
        if error.code == 404:
            return failure_response('Resource not found.', status_code=404)

        message = error.description or 'Request failed.'
        return failure_response(message, status_code=error.code or 500)

    @app.errorhandler(Exception)
    def unexpected_error(error):
        app.logger.exception('Unexpected server error.')
        message = str(error) if app.config.get('TESTING') else 'Unexpected server error.'
        return failure_response(message, status_code=500)


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

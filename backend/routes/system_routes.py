from sqlalchemy import text

from api_response import success_response
from flask import Blueprint, current_app
from models.model import db
from services.audio_service import is_transcription_runtime_ready
from services.task_service import get_task_stats

system = Blueprint('system', __name__)


@system.route('/health', methods=['GET'])
def health():
    database_ok = _check_database()
    transcription_ready = is_transcription_runtime_ready()
    status = 'ok' if database_ok else 'degraded'

    return success_response(
        {
            "service": current_app.config['APP_NAME'],
            "status": status,
            "checks": {
                "database": "ok" if database_ok else "error",
                "transcriptionRuntime": "ready" if transcription_ready else "missing",
            },
        }
    )


@system.route('/meta', methods=['GET'])
def meta():
    return success_response(
        {
            "name": current_app.config['APP_NAME'],
            "version": current_app.config['APP_VERSION'],
            "taskStats": get_task_stats(),
            "limits": {
                "maxUploadBytes": current_app.config['MAX_CONTENT_LENGTH'],
                "allowedAudioExtensions": sorted(current_app.config['ALLOWED_AUDIO_EXTENSIONS']),
            },
        }
    )


def _check_database():
    try:
        db.session.execute(text('SELECT 1'))
        return True
    except Exception:
        current_app.logger.exception('Database health check failed.')
        return False

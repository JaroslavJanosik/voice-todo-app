from sqlalchemy import text

from api_response import failure_response, success_response
from flask import Blueprint, current_app
from models.model import db
from services.audio_service import get_transcription_runtime_status
from services.task_service import get_task_stats

system = Blueprint('system', __name__)


@system.route('/health', methods=['GET'])
def health():
    return success_response(_build_service_status())


@system.route('/ready', methods=['GET'])
def ready():
    service_status = _build_service_status()
    is_ready = service_status['status'] == 'ok'
    if is_ready:
        return success_response(service_status)

    return failure_response('Service is not ready.', status_code=503, result=service_status)


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


def _build_service_status():
    database_ok = _check_database()
    transcription_runtime = get_transcription_runtime_status(current_app.config['WHISPER_MODEL'])
    status = 'ok' if database_ok and transcription_runtime['status'] == 'ready' else 'degraded'

    return {
        "service": current_app.config['APP_NAME'],
        "status": status,
        "checks": {
            "database": "ok" if database_ok else "error",
            "transcriptionRuntime": transcription_runtime['status'],
        },
        "details": {
            "transcriptionRuntime": transcription_runtime['message'],
        },
    }

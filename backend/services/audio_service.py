import importlib.util
import os
import shutil
from pathlib import Path

from exceptions import BadRequestError, ServiceUnavailableError
from utils import save_audio_file

_transcription_models = {}
MIN_RECORDING_DURATION_MS = 700


def transcribe_uploaded_file(file_storage, *, model_name='base', language=None, duration_ms=None):
    if file_storage is None:
        raise BadRequestError('No file uploaded.')

    if not file_storage.filename:
        raise BadRequestError('No selected file.')

    filepath = save_audio_file(file_storage)
    if not filepath:
        raise BadRequestError('Invalid file format.')

    try:
        transcription_model = get_transcription_model(model_name)
        transcription_options = {
            'fp16': False,
            'temperature': 0,
        }
        normalized_language = normalize_transcription_language(language)
        if normalized_language:
            transcription_options['language'] = normalized_language

        result = transcription_model.transcribe(filepath, **transcription_options)
        transcription = (result.get('text') or '').strip()

        if not transcription:
            if duration_ms is not None and duration_ms < MIN_RECORDING_DURATION_MS:
                raise BadRequestError('Recording was too short. Please speak for a little longer.')

            raise BadRequestError('No speech detected in the uploaded audio.')

        return transcription
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


def get_transcription_model(model_name='base', *, require_local=False):
    cached_model = _transcription_models.get(model_name)
    if cached_model is not None:
        return cached_model

    try:
        import whisper
    except Exception as exc:
        raise ServiceUnavailableError(
            'Speech transcription is not available because Whisper is not installed.'
        ) from exc

    download_root = get_whisper_download_root()
    if require_local and not is_model_cached_locally(whisper, model_name, download_root):
        raise ServiceUnavailableError('Speech transcription model is not cached locally.')

    try:
        transcription_model = whisper.load_model(model_name, download_root=str(download_root))
        _transcription_models[model_name] = transcription_model
        return transcription_model
    except Exception as exc:
        raise ServiceUnavailableError('Speech transcription model could not be loaded.') from exc


def is_transcription_runtime_ready():
    return get_transcription_runtime_status()['status'] == 'ready'


def get_transcription_runtime_status(model_name='base'):
    if shutil.which('ffmpeg') is None:
        return {
            'status': 'missing',
            'message': 'ffmpeg is not installed.',
        }

    if importlib.util.find_spec('whisper') is None:
        return {
            'status': 'missing',
            'message': 'Whisper is not installed.',
        }

    try:
        get_transcription_model(model_name, require_local=True)
        return {
            'status': 'ready',
            'message': 'Speech transcription runtime is ready.',
        }
    except ServiceUnavailableError as exc:
        message = str(exc)
        status = 'missing' if 'not cached locally' in message.lower() else 'error'
        return {
            'status': status,
            'message': message,
        }


def get_whisper_download_root():
    configured_root = os.environ.get('WHISPER_CACHE_DIR')
    if configured_root:
        return Path(configured_root).expanduser()

    return Path.home() / '.cache' / 'whisper'


def is_model_cached_locally(whisper_module, model_name, download_root: Path):
    models = getattr(whisper_module, '_MODELS', {})
    model_url = models.get(model_name)
    if not model_url:
        return False

    model_filename = os.path.basename(model_url)
    return (download_root / model_filename).exists()


def normalize_transcription_language(language):
    if not language or not isinstance(language, str):
        return None

    normalized_language = language.strip().lower().replace('_', '-')
    language_code = normalized_language.split('-', 1)[0]

    if language_code.isalpha() and len(language_code) in {2, 3}:
        return language_code

    return None

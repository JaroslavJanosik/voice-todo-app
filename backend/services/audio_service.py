import importlib.util
import os

from exceptions import BadRequestError, ServiceUnavailableError
from utils import save_audio_file

_transcription_model = None


def transcribe_uploaded_file(file_storage, *, model_name='base'):
    if file_storage is None:
        raise BadRequestError('No file uploaded.')

    if not file_storage.filename:
        raise BadRequestError('No selected file.')

    filepath = save_audio_file(file_storage)
    if not filepath:
        raise BadRequestError('Invalid file format.')

    try:
        transcription_model = get_transcription_model(model_name)
        result = transcription_model.transcribe(filepath)
        transcription = (result.get('text') or '').strip()

        if not transcription:
            raise BadRequestError('No speech detected in the uploaded audio.')

        return transcription
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


def get_transcription_model(model_name='base'):
    global _transcription_model

    if _transcription_model is not None:
        return _transcription_model

    try:
        import whisper
    except Exception as exc:
        raise ServiceUnavailableError(
            'Speech transcription is not available because Whisper is not installed.'
        ) from exc

    try:
        _transcription_model = whisper.load_model(model_name)
        return _transcription_model
    except Exception as exc:
        raise ServiceUnavailableError('Speech transcription model could not be loaded.') from exc


def is_transcription_runtime_ready():
    return importlib.util.find_spec('whisper') is not None

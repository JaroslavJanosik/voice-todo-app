import sys
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from exceptions import BadRequestError, ServiceUnavailableError
from services import audio_service
from services.audio_service import get_transcription_model, get_transcription_runtime_status, transcribe_uploaded_file


def test_transcribe_uploaded_file_uses_language_hint_and_fp32():
    file_storage = SimpleNamespace(filename='recording.webm')
    transcription_model = Mock()
    transcription_model.transcribe.return_value = {'text': 'Nakupit mlieko'}

    with patch('services.audio_service.save_audio_file', return_value='/tmp/test-recording.webm'), patch(
        'services.audio_service.get_transcription_model',
        return_value=transcription_model,
    ), patch('services.audio_service.os.path.exists', return_value=True), patch('services.audio_service.os.remove'):
        result = transcribe_uploaded_file(file_storage, model_name='base', language='sk-SK', duration_ms=1200)

    assert result == 'Nakupit mlieko'
    transcription_model.transcribe.assert_called_once_with(
        '/tmp/test-recording.webm',
        fp16=False,
        temperature=0,
        language='sk',
    )


def test_transcribe_uploaded_file_rejects_short_empty_recording():
    file_storage = SimpleNamespace(filename='recording.webm')
    transcription_model = Mock()
    transcription_model.transcribe.return_value = {'text': '   '}

    with patch('services.audio_service.save_audio_file', return_value='/tmp/test-recording.webm'), patch(
        'services.audio_service.get_transcription_model',
        return_value=transcription_model,
    ), patch('services.audio_service.os.path.exists', return_value=True), patch('services.audio_service.os.remove'):
        with pytest.raises(BadRequestError, match='Recording was too short. Please speak for a little longer.'):
            transcribe_uploaded_file(file_storage, model_name='base', language='sk-SK', duration_ms=500)


def test_get_transcription_runtime_status_reports_missing_model_cache():
    with patch('services.audio_service.shutil.which', return_value='/usr/bin/ffmpeg'), patch(
        'services.audio_service.importlib.util.find_spec',
        return_value=True,
    ), patch(
        'services.audio_service.get_transcription_model',
        side_effect=ServiceUnavailableError('Speech transcription model is not cached locally.'),
    ):
        status = get_transcription_runtime_status()

    assert status['status'] == 'missing'
    assert status['message'] == 'Speech transcription model is not cached locally.'


def test_get_transcription_model_caches_models_per_model_name(monkeypatch, tmp_path):
    load_calls = []
    fake_whisper = SimpleNamespace(
        _MODELS={
            'base': 'https://example.com/base.pt',
            'small': 'https://example.com/small.pt',
        },
        load_model=lambda model_name, download_root: load_calls.append((model_name, download_root)) or f'model:{model_name}',
    )

    monkeypatch.setattr(audio_service, '_transcription_models', {})
    monkeypatch.setattr(audio_service, 'get_whisper_download_root', lambda: tmp_path)
    monkeypatch.setitem(sys.modules, 'whisper', fake_whisper)

    try:
        base_model = get_transcription_model('base')
        base_model_second_call = get_transcription_model('base')
        small_model = get_transcription_model('small')
    finally:
        monkeypatch.delitem(sys.modules, 'whisper', raising=False)

    assert base_model == 'model:base'
    assert base_model_second_call == 'model:base'
    assert small_model == 'model:small'
    assert load_calls == [
        ('base', str(tmp_path)),
        ('small', str(tmp_path)),
    ]

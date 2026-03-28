from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from exceptions import BadRequestError
from services.audio_service import transcribe_uploaded_file


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

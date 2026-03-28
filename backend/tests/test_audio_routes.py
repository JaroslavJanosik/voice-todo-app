from io import BytesIO
from unittest.mock import patch

from exceptions import BadRequestError, ServiceUnavailableError


def test_upload_audio_success(client):
    data = {'file': (BytesIO(b'audio-bytes'), 'recording.webm')}

    with patch('routes.audio_routes.transcribe_uploaded_file', return_value='Buy milk') as transcribe:
        response = client.post('/upload', data=data, content_type='multipart/form-data')

    assert response.status_code == 200
    assert response.get_json()['result']['transcription'] == 'Buy milk'
    transcribe.assert_called_once()


def test_upload_audio_missing_file(client):
    with patch('routes.audio_routes.transcribe_uploaded_file', side_effect=BadRequestError('No file uploaded.')):
        response = client.post('/upload', data={}, content_type='multipart/form-data')

    assert response.status_code == 400
    assert response.get_json()['errorMessages'] == ['No file uploaded.']


def test_upload_audio_service_unavailable(client):
    data = {'file': (BytesIO(b'audio-bytes'), 'recording.webm')}

    with patch(
        'routes.audio_routes.transcribe_uploaded_file',
        side_effect=ServiceUnavailableError('Speech transcription model could not be loaded.')
    ):
        response = client.post('/upload', data=data, content_type='multipart/form-data')

    assert response.status_code == 503
    assert response.get_json()['errorMessages'] == ['Speech transcription model could not be loaded.']

from unittest.mock import patch


def test_health_success(client):
    with patch(
        'routes.system_routes.get_transcription_runtime_status',
        return_value={'status': 'ready', 'message': 'Speech transcription runtime is ready.'}
    ):
        response = client.get('/health')

    assert response.status_code == 200
    body = response.get_json()
    assert body['isSuccess'] is True
    assert body['result']['status'] == 'ok'
    assert body['result']['checks']['database'] == 'ok'
    assert body['result']['checks']['transcriptionRuntime'] == 'ready'
    assert body['result']['details']['transcriptionRuntime'] == 'Speech transcription runtime is ready.'


def test_health_degraded_when_transcription_runtime_is_missing(client):
    with patch(
        'routes.system_routes.get_transcription_runtime_status',
        return_value={'status': 'missing', 'message': 'Speech transcription model is not cached locally.'}
    ):
        response = client.get('/health')

    assert response.status_code == 200
    body = response.get_json()
    assert body['result']['status'] == 'degraded'
    assert body['result']['checks']['transcriptionRuntime'] == 'missing'


def test_ready_success(client):
    with patch(
        'routes.system_routes.get_transcription_runtime_status',
        return_value={'status': 'ready', 'message': 'Speech transcription runtime is ready.'}
    ):
        response = client.get('/ready')

    assert response.status_code == 200
    body = response.get_json()
    assert body['isSuccess'] is True
    assert body['result']['status'] == 'ok'


def test_ready_returns_503_when_service_is_not_ready(client):
    with patch(
        'routes.system_routes.get_transcription_runtime_status',
        return_value={'status': 'missing', 'message': 'Speech transcription model is not cached locally.'}
    ):
        response = client.get('/ready')

    assert response.status_code == 503
    body = response.get_json()
    assert body['isSuccess'] is False
    assert body['errorMessages'] == ['Service is not ready.']
    assert body['result']['status'] == 'degraded'


def test_meta_success(client):
    with patch(
        'routes.system_routes.get_task_stats',
        return_value={"total": 3, "active": 2, "completed": 1, "completionRate": 33}
    ):
        response = client.get('/meta')

    assert response.status_code == 200
    body = response.get_json()
    assert body['result']['name'] == 'voice-todo-app-backend-test'
    assert body['result']['taskStats']['completionRate'] == 33

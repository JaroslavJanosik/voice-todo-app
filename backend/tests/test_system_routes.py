from unittest.mock import patch


def test_health_success(client):
    with patch('routes.system_routes.is_transcription_runtime_ready', return_value=True):
        response = client.get('/health')

    assert response.status_code == 200
    body = response.get_json()
    assert body['isSuccess'] is True
    assert body['result']['status'] == 'ok'
    assert body['result']['checks']['database'] == 'ok'
    assert body['result']['checks']['transcriptionRuntime'] == 'ready'


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

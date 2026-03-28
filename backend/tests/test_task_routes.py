from unittest.mock import patch

from exceptions import BadRequestError, ConflictError, NotFoundError


def test_get_tasks_success(client):
    tasks = [{"id": 1, "description": "Test task", "completed": False}]

    with patch('routes.task_routes.task_service.list_tasks', return_value=tasks):
        response = client.get('/tasks')

    assert response.status_code == 200
    body = response.get_json()
    assert body['isSuccess'] is True
    assert body['result'] == tasks


def test_get_task_not_found(client):
    with patch('routes.task_routes.task_service.get_task', side_effect=NotFoundError('Task with id 42 was not found.')):
        response = client.get('/tasks/42')

    assert response.status_code == 404
    assert response.get_json()['errorMessages'] == ['Task with id 42 was not found.']


def test_add_task_success(client):
    task = {"id": 1, "description": "Ship release", "completed": False}

    with patch('routes.task_routes.task_service.create_task', return_value=task) as create_task:
        response = client.post('/tasks', json={'task': 'Ship release'})

    assert response.status_code == 201
    assert response.get_json()['result'] == task
    create_task.assert_called_once_with('Ship release')


def test_add_task_duplicate(client):
    with patch('routes.task_routes.task_service.create_task', side_effect=ConflictError('Task already exists.')):
        response = client.post('/tasks', json={'task': 'Ship release'})

    assert response.status_code == 409
    assert response.get_json()['errorMessages'] == ['Task already exists.']


def test_update_task_bad_request(client):
    with patch(
        'routes.task_routes.task_service.replace_task',
        side_effect=BadRequestError('Task description is required.')
    ):
        response = client.put('/tasks/1', json={})

    assert response.status_code == 400
    assert response.get_json()['errorMessages'] == ['Task description is required.']


def test_patch_task_success(client):
    task = {"id": 3, "description": "Edited", "completed": True}

    with patch('routes.task_routes.task_service.patch_task', return_value=task) as patch_task:
        response = client.patch('/tasks/3', json={'task': 'Edited', 'completed': True})

    assert response.status_code == 200
    assert response.get_json()['result'] == task
    patch_task.assert_called_once_with(3, description='Edited', completed=True)


def test_toggle_task_success(client):
    task = {"id": 5, "description": "Toggle me", "completed": True}

    with patch('routes.task_routes.task_service.toggle_task', return_value=task):
        response = client.put('/tasks/5/toggle')

    assert response.status_code == 200
    assert response.get_json()['result']['completed'] is True


def test_delete_task_success(client):
    with patch('routes.task_routes.task_service.delete_task') as delete_task:
        response = client.delete('/tasks/9')

    assert response.status_code == 200
    assert response.get_json()['result']['message'] == 'Task deleted successfully'
    delete_task.assert_called_once_with(9)

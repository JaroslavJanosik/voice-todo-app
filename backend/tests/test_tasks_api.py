from unittest.mock import MagicMock, patch

import pytest

from app import create_app
from models.model import Task


# --------------------------------------------------------------------------- #
#  PyTest fixture                                                             #
# --------------------------------------------------------------------------- #
@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            yield client


# --------------------------------------------------------------------------- #
#  Helpers                                                                    #
# --------------------------------------------------------------------------- #
def _make_fake_query():
    """
    Return a MagicMock that behaves like Task.query:
        - order_by() is chain-able
        - get_or_404() can be configured per-test
        - all() can be configured per-test
    """
    fake_query = MagicMock(name="FakeQuery")
    fake_query.order_by.return_value = fake_query
    return fake_query


# --------------------------------------------------------------------------- #
#  GET /tasks                                                                 #
# --------------------------------------------------------------------------- #
def test_get_tasks_success(client):
    mock_task = MagicMock()
    mock_task.id = 1
    mock_task.description = "Test Task"
    mock_task.completed = False
    mock_task.to_dict.return_value = {
        "id": mock_task.id,
        "description": mock_task.description
    }

    fake_query = _make_fake_query()
    fake_query.all.return_value = [mock_task]

    with patch.object(Task, "query", fake_query):
        response = client.get("/tasks")

    assert response.status_code == 200
    tasks = response.get_json()
    assert any(t["id"] == 1 and t["description"] == "Test Task" for t in tasks)


def test_get_tasks_exception(client):
    fake_query = _make_fake_query()
    fake_query.order_by.side_effect = Exception("DB error")

    with patch.object(Task, "query", fake_query):
        response = client.get("/tasks")

    assert response.status_code == 500
    body = response.get_json()
    assert body and "error" in body


# --------------------------------------------------------------------------- #
#  POST /tasks                                                                #
# --------------------------------------------------------------------------- #
def test_add_task_success(client):
    mock_task = MagicMock()
    mock_task.id = 1
    mock_task.description = "New Task"
    mock_task.to_dict.return_value = {"id": mock_task.id, "description": mock_task.description}

    with patch("routes.task_routes.db.session.add"), \
            patch("routes.task_routes.db.session.commit"), \
            patch("routes.task_routes.Task", return_value=mock_task):
        response = client.post("/tasks", json={"task": "New Task"})

    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "Task added successfully"
    assert data["task"]["description"] == "New Task"


def test_add_task_missing_description(client):
    response = client.post("/tasks", json={})
    assert response.status_code == 400
    assert "Task description is required" in response.get_json()["error"]


def test_add_task_exception(client):
    with patch("routes.task_routes.db.session.add", side_effect=Exception("DB failure")), \
            patch("routes.task_routes.db.session.rollback"):
        response = client.post("/tasks", json={"task": "Test"})

    assert response.status_code == 500
    assert "DB failure" in response.get_json()["error"]


# --------------------------------------------------------------------------- #
#  PUT /tasks/<id>/toggle                                                     #
# --------------------------------------------------------------------------- #
def test_toggle_task_success(client):
    mock_task = MagicMock()
    mock_task.id = 1
    mock_task.description = "Test Task"
    mock_task.completed = False
    mock_task.to_dict.side_effect = lambda: {
        "id": mock_task.id,
        "description": mock_task.description,
        "completed": mock_task.completed,
    }

    fake_query = _make_fake_query()
    fake_query.get_or_404.return_value = mock_task
    fake_session = MagicMock()

    with patch.object(Task, "query", fake_query), \
            patch("routes.task_routes.db.session", fake_session):
        response = client.put("/tasks/1/toggle")

    assert response.status_code == 200
    body = response.get_json()
    assert body["message"] == "Task status updated"
    assert body["task"]["completed"] is True
    assert mock_task.completed is True


def test_toggle_task_exception(client):
    fake_query = _make_fake_query()
    fake_query.get_or_404.side_effect = Exception("DB error")
    fake_session = MagicMock()

    with patch.object(Task, "query", fake_query), \
            patch("routes.task_routes.db.session", fake_session):
        response = client.put("/tasks/1/toggle")

    assert response.status_code == 500
    body = response.get_json()
    assert "DB error" in body["error"]
    fake_session.rollback.assert_called_once()


# --------------------------------------------------------------------------- #
#  PUT /tasks/<id>                                                            #
# --------------------------------------------------------------------------- #
def test_update_task_success(client):
    mock_task = MagicMock()
    mock_task.id = 1
    mock_task.description = "Test Task"

    mock_task.to_dict.side_effect = lambda: {
        "id": mock_task.id,
        "description": mock_task.description,
    }

    fake_query = _make_fake_query()
    fake_query.get_or_404.return_value = mock_task

    with patch.object(Task, "query", fake_query), \
            patch("routes.task_routes.db.session.commit"):
        response = client.put("/tasks/1", json={"task": "Updated"})

    assert response.status_code == 200
    body = response.get_json()
    assert body["message"] == "Task updated successfully"
    assert body["task"]["description"] == "Updated"


def test_update_task_missing_description(client):
    response = client.put("/tasks/1", json={})
    assert response.status_code == 400
    assert "Task description is required" in response.get_json()["error"]


def test_update_task_exception(client):
    fake_query = _make_fake_query()
    fake_query.get_or_404.side_effect = Exception("DB error")
    fake_session = MagicMock()

    with patch.object(Task, "query", fake_query), \
            patch("routes.task_routes.db.session", fake_session):
        response = client.put("/tasks/1", json={"task": "Updated"})

    assert response.status_code == 500
    body = response.get_json()
    assert "DB error" in body["error"]
    fake_session.rollback.assert_called_once()


# --------------------------------------------------------------------------- #
#  DELETE /tasks/<id>                                                         #
# --------------------------------------------------------------------------- #
def test_delete_task_success(client):
    mock_task = MagicMock()

    fake_query = _make_fake_query()
    fake_query.get_or_404.return_value = mock_task

    with patch.object(Task, "query", fake_query), \
            patch("routes.task_routes.db.session.delete"), \
            patch("routes.task_routes.db.session.commit"):
        response = client.delete("/tasks/1")

    assert response.status_code == 200
    assert response.get_json()["message"] == "Task deleted successfully"


def test_delete_task_exception(client):
    fake_query = _make_fake_query()
    fake_query.get_or_404.side_effect = Exception("DB error")
    fake_session = MagicMock()

    with patch.object(Task, "query", fake_query), \
            patch("routes.task_routes.db.session", fake_session):
        response = client.delete("/tasks/1")

    assert response.status_code == 500
    body = response.get_json()
    assert "DB error" in body["error"]
    fake_session.rollback.assert_called_once()

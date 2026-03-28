from api_response import success_response
from flask import Blueprint, request
from services import task_service

tasks = Blueprint('tasks', __name__)


@tasks.route('', methods=['GET'])
def get_tasks():
    return success_response(task_service.list_tasks())


@tasks.route('/stats', methods=['GET'])
def get_task_stats():
    return success_response(task_service.get_task_stats())


@tasks.route('/<int:task_id>', methods=['GET'])
def get_task(task_id):
    return success_response(task_service.get_task(task_id))


@tasks.route('', methods=['POST'])
def add_task():
    payload = request.get_json(silent=True) or {}
    return success_response(task_service.create_task(payload.get('task')), status_code=201)


@tasks.route('/<int:task_id>/toggle', methods=['PUT'])
def toggle_task(task_id):
    return success_response(task_service.toggle_task(task_id))


@tasks.route('/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    payload = request.get_json(silent=True) or {}
    return success_response(task_service.replace_task(task_id, payload.get('task')))


@tasks.route('/<int:task_id>', methods=['PATCH'])
def patch_task(task_id):
    payload = request.get_json(silent=True) or {}
    return success_response(
        task_service.patch_task(
            task_id,
            description=payload.get('task'),
            completed=payload.get('completed'),
        )
    )


@tasks.route('/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task_service.delete_task(task_id)
    return success_response({"message": "Task deleted successfully"})

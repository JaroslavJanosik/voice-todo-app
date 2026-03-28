from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from exceptions import BadRequestError, ConflictError, NotFoundError
from models.model import Task, db


def list_tasks():
    return [task.to_dict() for task in Task.query.order_by(Task.created_at.desc(), Task.id.desc()).all()]


def get_task(task_id):
    return _get_task_or_raise(task_id).to_dict()


def create_task(description):
    normalized_description = _validate_description(description)
    _ensure_unique_description(normalized_description)

    task = Task(description=normalized_description)
    db.session.add(task)
    _commit_task_change()

    return task.to_dict()


def replace_task(task_id, description):
    task = _get_task_or_raise(task_id)
    normalized_description = _validate_description(description)
    _ensure_unique_description(normalized_description, current_task_id=task.id)

    task.description = normalized_description
    _commit_task_change()

    return task.to_dict()


def patch_task(task_id, *, description=None, completed=None):
    task = _get_task_or_raise(task_id)

    if description is None and completed is None:
        raise BadRequestError('At least one field must be provided for update.')

    if description is not None:
        normalized_description = _validate_description(description)
        _ensure_unique_description(normalized_description, current_task_id=task.id)
        task.description = normalized_description

    if completed is not None:
        if not isinstance(completed, bool):
            raise BadRequestError('Task completion flag must be a boolean value.')
        task.completed = completed

    _commit_task_change()
    return task.to_dict()


def toggle_task(task_id):
    task = _get_task_or_raise(task_id)
    task.completed = not task.completed
    db.session.commit()
    return task.to_dict()


def delete_task(task_id):
    task = _get_task_or_raise(task_id)
    db.session.delete(task)
    db.session.commit()


def get_task_stats():
    total = Task.query.count()
    completed = Task.query.filter_by(completed=True).count()
    active = total - completed
    completion_rate = round((completed / total) * 100) if total else 0

    return {
        "total": total,
        "active": active,
        "completed": completed,
        "completionRate": completion_rate,
    }


def _get_task_or_raise(task_id):
    _validate_task_id(task_id)
    task = db.session.get(Task, task_id)
    if task is None:
        raise NotFoundError(f'Task with id {task_id} was not found.')
    return task


def _validate_task_id(task_id):
    if not isinstance(task_id, int) or task_id <= 0:
        raise BadRequestError('Task id must be greater than 0.')


def _validate_description(description):
    if not isinstance(description, str):
        raise BadRequestError('Task description is required.')

    normalized_description = description.strip()
    if not normalized_description:
        raise BadRequestError('Task description is required.')

    return normalized_description[:500]


def _ensure_unique_description(description, current_task_id=None):
    normalized_description = description.strip().lower()
    existing_task = Task.query.filter(
        func.lower(func.trim(Task.description)) == normalized_description
    ).first()

    if existing_task is not None and existing_task.id != current_task_id:
        raise ConflictError('Task already exists.')


def _commit_task_change():
    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        if _is_duplicate_task_integrity_error(exc):
            raise ConflictError('Task already exists.') from exc
        raise


def _is_duplicate_task_integrity_error(error):
    message = str(error).lower()
    return 'uq_task_normalized_description' in message or 'unique constraint failed' in message

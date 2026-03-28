from unittest.mock import patch

import pytest
from sqlalchemy.exc import IntegrityError

from exceptions import BadRequestError, ConflictError, NotFoundError
from models.model import Task, db
from services import task_service


def test_create_task_trims_description(app):
    with app.app_context():
        created = task_service.create_task('  Finish release checklist  ')

    assert created['description'] == 'Finish release checklist'


def test_create_task_rejects_duplicate_description(app):
    with app.app_context():
        db.session.add(Task(description='Ship Release'))
        db.session.commit()

        with pytest.raises(ConflictError, match='Task already exists.'):
            task_service.create_task('  ship release ')


def test_create_task_translates_integrity_error_to_conflict(app):
    with app.app_context(), patch(
        'services.task_service.db.session.commit',
        side_effect=IntegrityError('insert into task', {}, Exception('UNIQUE constraint failed: index uq_task_normalized_description'))
    ):
        with pytest.raises(ConflictError, match='Task already exists.'):
            task_service.create_task('Ship Release')


def test_patch_task_updates_completion_and_text(app):
    with app.app_context():
        task = Task(description='Draft copy', completed=False)
        db.session.add(task)
        db.session.commit()

        updated = task_service.patch_task(task.id, description='Publish copy', completed=True)

    assert updated['description'] == 'Publish copy'
    assert updated['completed'] is True


def test_patch_task_requires_fields(app):
    with app.app_context():
        task = Task(description='Draft copy')
        db.session.add(task)
        db.session.commit()

        try:
            task_service.patch_task(task.id)
            assert False, 'Expected patch without changes to fail.'
        except BadRequestError as error:
            assert str(error) == 'At least one field must be provided for update.'


def test_get_task_rejects_missing_id(app):
    with app.app_context():
        try:
            task_service.get_task(999)
            assert False, 'Expected missing task lookup to fail.'
        except NotFoundError as error:
            assert str(error) == 'Task with id 999 was not found.'


def test_get_task_stats(app):
    with app.app_context():
        db.session.add_all(
            [
                Task(description='One', completed=False),
                Task(description='Two', completed=True),
                Task(description='Three', completed=True),
            ]
        )
        db.session.commit()

        stats = task_service.get_task_stats()

    assert stats == {"total": 3, "active": 1, "completed": 2, "completionRate": 67}

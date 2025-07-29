from flask import Blueprint, request, jsonify
from models.model import db, Task
from flask_cors import cross_origin

tasks = Blueprint('tasks', __name__)


@tasks.route('', methods=['GET'])
@cross_origin()
def get_tasks():
    try:
        tasks = Task.query.order_by(Task.created_at.desc()).all()
        return jsonify([task.to_dict() for task in tasks])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@tasks.route('', methods=['POST'])
@cross_origin()
def add_task():
    try:
        data = request.get_json()
        if not data or 'task' not in data:
            return jsonify({"error": "Task description is required"}), 400

        new_task = Task(description=data['task'])
        db.session.add(new_task)
        db.session.commit()

        return jsonify({
            "message": "Task added successfully",
            "task": new_task.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@tasks.route('/<int:task_id>/toggle', methods=['PUT'])
@cross_origin()
def toggle_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        task.completed = not task.completed
        db.session.commit()

        return jsonify({
            "message": "Task status updated",
            "task": task.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@tasks.route('/<int:task_id>', methods=['PUT'])
@cross_origin()
def update_task(task_id):
    try:
        data = request.get_json()
        if not data or 'task' not in data:
            return jsonify({"error": "Task description is required"}), 400

        task = Task.query.get_or_404(task_id)
        task.description = data['task']
        db.session.commit()

        return jsonify({
            "message": "Task updated successfully",
            "task": task.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@tasks.route('/<int:task_id>', methods=['DELETE'])
@cross_origin()
def delete_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": "Task deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

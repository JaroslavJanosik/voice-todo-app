from flask import Flask
from flask_cors import CORS

from models.model import db
from routes.task_routes import tasks
from routes.audio_routes import audio
from config import Config
import os


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    CORS(app, resources={r"/*": {"origins": app.config['CORS_ORIGINS']}})

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')), exist_ok=True)

    app.register_blueprint(tasks, url_prefix='/tasks')
    app.register_blueprint(audio)

    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)

import os
from pathlib import Path
from uuid import uuid4

from werkzeug.utils import secure_filename
from flask import current_app


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_audio_file(file):
    if file and allowed_file(file.filename, current_app.config['ALLOWED_AUDIO_EXTENSIONS']):
        extension = Path(secure_filename(file.filename)).suffix.lower()
        filename = f'{uuid4().hex}{extension}'
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filepath
    return None

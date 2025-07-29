import os

import whisper
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

from utils import save_audio_file

audio = Blueprint('audio', __name__, url_prefix='')

model = whisper.load_model("base")


@audio.route('/upload', methods=['POST'])
@cross_origin()
def upload_audio():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        filepath = save_audio_file(file)
        if not filepath:
            return jsonify({"error": "Invalid file format"}), 400

        try:
            result = model.transcribe(filepath)
            transcription = result['text']
        except Exception as e:
            return jsonify({"error": f"Transcription failed: {str(e)}"}), 500
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

        return jsonify({
            "success": True,
            "transcription": transcription
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

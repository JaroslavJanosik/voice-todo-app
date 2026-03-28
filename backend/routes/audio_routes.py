from api_response import success_response
from flask import Blueprint, current_app, request
from services.audio_service import transcribe_uploaded_file

audio = Blueprint('audio', __name__, url_prefix='')


@audio.route('/upload', methods=['POST'])
def upload_audio():
    file_storage = request.files.get('file')
    transcription = transcribe_uploaded_file(
        file_storage,
        model_name=current_app.config['WHISPER_MODEL'],
    )

    return success_response(
        {
            "transcription": transcription,
        }
    )

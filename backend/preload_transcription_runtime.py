import os

from services.audio_service import get_transcription_model, get_whisper_download_root


def main():
    model_name = os.environ.get('WHISPER_MODEL', 'base')
    download_root = get_whisper_download_root()
    print(f"Preloading Whisper model '{model_name}' into '{download_root}'.")
    get_transcription_model(model_name)
    print('Whisper transcription runtime is ready.')


if __name__ == '__main__':
    main()

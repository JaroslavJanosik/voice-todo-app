# Backend

Flask backend for the Voice Todo App. The backend now follows a more product-grade structure with service modules, consistent API response envelopes, health endpoints, duplicate protection, and automated tests.

## Requirements

- Python 3.9+
- FFmpeg 4.0+

Quick FFmpeg installs:

- macOS: `brew install ffmpeg`
- Ubuntu/Debian: `sudo apt update && sudo apt install ffmpeg`
- Windows: `winget install ffmpeg`

## Run Locally

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask run
```

## Main Endpoints

- `GET /health`
- `GET /meta`
- `GET /tasks`
- `GET /tasks/{id}`
- `GET /tasks/stats`
- `POST /tasks`
- `PUT /tasks/{id}`
- `PATCH /tasks/{id}`
- `PUT /tasks/{id}/toggle`
- `DELETE /tasks/{id}`
- `POST /upload`

## Response Envelope

Successful responses:

```json
{
  "statusCode": 200,
  "isSuccess": true,
  "errorMessages": [],
  "result": {}
}
```

Validation and server errors keep the same envelope with `isSuccess: false`.

## Tests

```bash
venv/bin/python -m pytest
```

Current backend coverage includes:

- Task route contract tests
- Task service behavior tests
- Audio upload route tests
- Health and metadata endpoint tests

## Environment Variables

See `.env.example`. The most important values are:

- `DATABASE_URL`
- `CORS_ORIGINS`
- `WHISPER_MODEL`
- `MAX_CONTENT_LENGTH`
- `APP_NAME`
- `APP_VERSION`

# Voice Todo App

Voice-first todo application with a Flask backend and a SvelteKit frontend. The project keeps its current glassmorphism visual style, but now has a more production-ready API, stronger resilience around failures, health endpoints, backend test coverage, and a Docker Compose entry point similar in spirit to `QaToDoApp-Pro`.

## Project Structure

```text
voice-todo-app/
├── backend/                    Flask API, transcription services, tests
├── frontend/
│   ├── svelte/                 Main SvelteKit frontend
│   └── html-css-javascript/    Legacy prototype kept in sync with the API
├── docker-compose.yml          Local multi-container setup
└── nginx.conf                  Reverse proxy for frontend + backend
```

## Local Development

Backend:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask run
```

Frontend:

```bash
cd frontend/svelte
npm ci
cp .env.example .env
npm run dev
```

Local URLs:

- Frontend: `http://localhost:5173`
- Backend API: `http://127.0.0.1:5000`
- Health: `http://127.0.0.1:5000/health`
- Metadata: `http://127.0.0.1:5000/meta`

## API Shape

Successful API responses use a consistent envelope:

```json
{
  "statusCode": 200,
  "isSuccess": true,
  "errorMessages": [],
  "result": {}
}
```

Failed responses use the same structure with `isSuccess: false`.

## Quality Checks

Backend:

```bash
cd backend
venv/bin/python -m pytest
```

Frontend:

```bash
cd frontend/svelte
npm run check
npm run build
npm run quality
```

## Docker Compose

```bash
docker compose up --build
```

Services:

- NGINX entry point: `http://localhost`
- Frontend container: `http://localhost:4173`
- Backend API: `http://localhost:5000`
- Persistent backend data volume: `voice-todo-data`

## Notes

- `ffmpeg` is required for Whisper transcription.
- The backend loads the Whisper model lazily, so the API can still boot even if transcription runtime is unavailable.
- The frontend can work with an explicit `PUBLIC_API_BASE_URL` or infer the backend URL automatically in local development.

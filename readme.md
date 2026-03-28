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
- Readiness: `http://127.0.0.1:5000/ready`
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
npx playwright install chromium
npm test
```

Playwright highlights:

- page object model for the voice dashboard
- end-to-end coverage for empty state, CRUD flows, duplicate-save resilience, and mocked voice capture
- API contract coverage for `/health`, `/meta`, and task CRUD endpoints
- can run either against Playwright-managed local servers or an already running Docker Compose stack

## CI

GitHub Actions workflow lives in `.github/workflows/ci.yml` and runs automatically on every push and pull request.

It covers:

- backend pytest suite
- backend syntax validation
- frontend `npm run check`
- frontend production build
- Playwright API and end-to-end suite, with report artifacts uploaded on failure

## Docker Compose

```bash
docker compose up --build
```

If default host ports are already in use on your machine, you can override them:

```bash
BACKEND_PORT=5050 FRONTEND_PORT=4175 NGINX_PORT=8080 docker compose up --build
```

The container stack now uses production-oriented runtimes:

- backend via Gunicorn
- frontend via SvelteKit Node adapter
- NGINX as the reverse proxy entry point
- container healthchecks for backend and frontend
- persistent Whisper cache under the shared backend data volume
- backend startup preloads the configured Whisper model in Docker Compose so readiness reflects real voice availability

Services:

- NGINX entry point: `http://localhost`
- Frontend container: `http://localhost:4173`
- Backend API: `http://localhost:5000`
- Persistent backend data volume: `voice-todo-data`

To run the Playwright suite against the running Docker stack instead of Playwright-managed dev servers:

```bash
docker compose up --build -d
cd frontend/svelte
PLAYWRIGHT_USE_EXTERNAL_SERVER=1 \
PLAYWRIGHT_FRONTEND_BASE_URL=http://127.0.0.1:80 \
PLAYWRIGHT_API_BASE_URL=http://127.0.0.1:5000 \
npx playwright test
```

If you started Docker Compose with overridden host ports, use the matching frontend and backend URLs in those Playwright environment variables.

## Notes

- `ffmpeg` is required for Whisper transcription.
- The backend loads the Whisper model lazily, so the API can still boot even if transcription runtime is unavailable.
- In Docker Compose, the backend now preloads the configured Whisper model before reporting itself healthy, so the stack does not come up “green” while voice transcription is still unusable.
- `/health` is now a liveness-style endpoint that still reports degraded runtime details without pretending everything is green.
- `/ready` is now a stricter readiness endpoint and returns `503` when the service is not fully ready to handle voice transcription.
- The frontend can work with an explicit `PUBLIC_API_BASE_URL` or infer the backend URL automatically in local development.
- `npm run preview` in the Svelte app now runs the real Node adapter server instead of `vite preview`, so local production preview matches deployment behavior more closely.

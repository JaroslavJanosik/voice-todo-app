# Frontend

SvelteKit frontend for the Voice Todo App. It keeps the current visual language, but now behaves more like a production UI: resilient API handling, editable task drafts that survive failed saves, task summary cards, testability hooks, and a cleaner API configuration model.

## Requirements

- Node.js 22+ recommended
- npm
- Docker runtime uses SvelteKit Node adapter rather than `vite preview`

## Run Locally

```bash
npm ci
cp .env.example .env
npm run dev
```

The app runs on `http://localhost:5173`.

## API Configuration

Default behavior:

- `PUBLIC_API_BASE_URL` wins when set
- local dev on `localhost:5173` automatically targets `localhost:5000`
- reverse proxy deployments can use relative API paths

Override explicitly with:

```bash
PUBLIC_API_BASE_URL=http://127.0.0.1:5000
```

## Main Scripts

- `npm run dev` – start development server
- `npm run build` – create production build
- `npm run start` – run the built Node adapter server
- `npm run preview` – alias for the production server preview
- `npm run check` – run Svelte + TypeScript checks
- `npm run typecheck` – alias for `npm run check`
- `npm test` – run the full Playwright suite
- `npm run test:e2e` – run browser end-to-end flows only
- `npm run test:api` – run public API contract tests only
- `npm run test:headed` – run Playwright in headed mode
- `npm run test:debug` – open the Playwright debugger
- `npm run test:report` – open the latest HTML report
- `npm run quality` – run `check` and `build`

## Playwright Test Stack

The frontend now includes a professional Playwright setup with:

- page object model under `tests/page-objects`
- reusable API client + helpers under `tests/support`
- shared fixtures under `tests/fixtures`
- end-to-end coverage for empty state, CRUD flows, duplicate-save resilience, and mocked voice capture
- API contract coverage for health, metadata, CRUD, and duplicate conflicts

Install the browser runtime once:

```bash
npx playwright install chromium
```

Then run the suite:

```bash
npm test
```

## Frontend Quality Highlights

- API envelope unwrapping with clear error messages
- retry action for failed initial load
- edit form stays open when save fails
- summary cards for total, active, completed, and progress
- `data-cy` hooks on key UI elements for Playwright coverage
- microphone selector and live input meter for safer voice capture diagnostics

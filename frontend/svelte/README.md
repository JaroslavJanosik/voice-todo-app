# Frontend

SvelteKit frontend for the Voice Todo App. It keeps the current visual language, but now behaves more like a production UI: resilient API handling, editable task drafts that survive failed saves, task summary cards, testability hooks, and a cleaner API configuration model.

## Requirements

- Node.js 22+ recommended
- npm

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
- `npm run preview` – preview the production build
- `npm run check` – run Svelte + TypeScript checks
- `npm run typecheck` – alias for `npm run check`
- `npm test` – alias for `npm run check`
- `npm run quality` – run `check` and `build`

## Frontend Quality Highlights

- API envelope unwrapping with clear error messages
- retry action for failed initial load
- edit form stays open when save fails
- summary cards for total, active, completed, and progress
- `data-cy` hooks on key UI elements for future e2e coverage

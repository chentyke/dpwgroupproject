# FIFA Player Data Analysis Frontend

This folder contains the Next.js dashboard for the FIFA Player Data Analysis System.

## Pages

- `/`: project overview dashboard
- `/explore`: dataset summary, schema preview, and cleaning status
- `/value-for-money`: player value-for-money rankings and market charts
- `/fairness`: league wage spread and nationality wage heatmap
- `/injury`: future Injury Prone and Solid Player projection
- `/advanced`: playing-style clustering and market-value prediction

## Run Locally

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open:

```text
http://127.0.0.1:3000
```

For full live data, run the backend from the repository root:

```bash
uvicorn app.main:app --reload
```

The frontend also includes fallback data in `web/lib/fallback-data.ts` so pages can render while backend work is in progress.

## Useful Commands

```bash
npm run lint
npm run generate:types
```

`npm run generate:types` exports the FastAPI OpenAPI schema and refreshes `web/lib/generated/api-types.ts`.

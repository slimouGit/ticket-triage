# Ticket Triage Frontend

React + TypeScript frontend for the Local LLM Ticket Triage app.

It allows users to:
- submit support tickets
- analyze them with a local LLM
- review structured analysis results
- browse and delete stored ticket analyses

## Development

From the `frontend` folder:

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
```

The build output is generated in `frontend/dist` and can be served by the FastAPI backend.
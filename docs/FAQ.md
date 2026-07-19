# FAQ

## Is this a medical device?

No. This repository is intended for research and clinical decision support workflows.

## Which ECG formats are supported?

Current backend upload route supports `.csv`, `.dat`, `.hea`, `.edf`.

## Does the backend use machine learning today?

The implemented diagnosis pipeline is rule-based. `ml_placeholder.py` is reserved for future model integration.

## Where can I inspect API contracts?

- `docs/API.md`
- Backend OpenAPI docs at `/docs`
- `backend/app/models/schemas.py`

## How do I run it quickly?

Use Docker Compose:

```bash
docker compose up --build
```

## Where are architectural diagrams?

See `docs/Architecture.md` and related docs pages with Mermaid diagrams.

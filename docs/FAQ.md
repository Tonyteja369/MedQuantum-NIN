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

## Can I use Raylight from an MCP client?

Any MCP client can connect. Not listed? Add Raylight as a remote MCP server with this URL. It speaks streamable HTTP and signs you in with your Raylight account.

## Where are architectural diagrams?

See `docs/Architecture.md` and related docs pages with Mermaid diagrams.

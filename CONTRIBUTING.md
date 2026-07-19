# Contributing to MedQuantum-NIN

Thanks for your interest in improving MedQuantum-NIN.

## Before You Start

- Read `README.md` and `docs/Development.md`.
- Search existing issues before opening a new one.
- For major changes, open an issue first to discuss scope.

## Development Setup

### Frontend

```bash
npm ci
npm run dev
npm run build
npm run lint
```

### Backend

```bash
cd backend
python -m pip install -r requirements.txt
pytest tests/ -v
ruff check app/ tests/
```

## Branching and Commits

- Branch naming: `type/short-description` (e.g., `docs/api-reference-update`, `fix/docker-healthcheck`)
- Use semantic-style commit prefixes where possible:
  - `feat:`
  - `fix:`
  - `docs:`
  - `chore:`
  - `refactor:`
  - `test:`

## Pull Requests

- Use the repository PR template.
- Keep PRs focused and reviewable.
- Update docs when behavior or interfaces change.
- Ensure builds/tests relevant to your changes pass.

## Documentation Rules

- Document only implemented behavior.
- Clearly label roadmap/future work.
- Keep API docs synchronized with backend routes and schemas.

## Code Style

- Frontend: TypeScript + React patterns already used in `src/`.
- Backend: FastAPI + Pydantic style used in `backend/app/`.
- Avoid introducing new frameworks unless justified.

## Reporting Security Issues

Please do not open public issues for vulnerabilities.
Use `SECURITY.md` for responsible disclosure instructions.

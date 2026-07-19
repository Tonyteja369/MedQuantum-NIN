# Development Guide

## Repository Layout

- Frontend source: `src/`
- Backend source: `backend/app/`
- Backend tests: `backend/tests/`

## Tooling

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

## Quality Notes

- Backend tests are implemented and passing in `backend/tests/`.
- Frontend build is implemented and should pass with `npm run build`.
- Linting must be run before PRs in both frontend and backend paths.

## Contribution Workflow

1. Create focused branch.
2. Make minimal, targeted changes.
3. Update docs with behavior changes.
4. Run relevant validation commands.
5. Open PR with checklist completion.

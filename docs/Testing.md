# Testing Strategy

## Backend Tests

Location: `backend/tests/`

Current suites:
- `test_preprocessing.py`
- `test_feature_extraction.py`
- `test_rule_engine.py`

Run:

```bash
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing
```

## Frontend Tests

Automated frontend unit/integration tests are not yet configured in this repository.
Current frontend validation focuses on type/build/lint checks.

Run:

```bash
npm run build
npm run lint
```

## Manual Testing

- Upload ECG file
- Load sample record
- Run analysis
- Generate report
- Verify dark/light theme and responsive layout

## Regression Focus

- API schema compatibility with frontend usage
- Rule engine outputs and confidence ranges
- Docker compose startup and health checks

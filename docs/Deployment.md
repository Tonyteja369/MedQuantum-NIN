# Deployment

## Local Docker Compose

```bash
docker compose up --build
```

Services:
- `backend` on `:8000`
- `frontend` on `:5173`

## Local Non-Docker

### Backend

```bash
cd backend
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
npm ci
npm run dev
```

## Environment

- Frontend uses `VITE_API_URL`
- Backend uses `backend/.env` values defined in `backend/.env.example`

## Production Recommendations

- Use immutable image tags
- Place API behind TLS reverse proxy
- Use external persistent storage for data and logs
- Keep CORS `ALLOWED_ORIGINS` strict
- Run with least privileges and non-root users

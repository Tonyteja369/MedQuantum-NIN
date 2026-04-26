#!/usr/bin/env bash
set -e
echo "Starting MedQuantum-NIN Backend..."
cd backend
../.venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
cd ..
sleep 2
echo "Starting React Frontend..."
npm run dev

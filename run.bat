@echo off
echo Starting MedQuantum-NIN Backend...
cd backend
start cmd /k "..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
cd ..
timeout /t 3
echo Starting React Frontend...
npm run dev

@echo off
echo Starting ZohoFlow Backend...
cd /d "%~dp0"

REM Install dependencies if needed
pip install -r web\backend\requirements.txt -q

REM Seed first user (idempotent)
python -m web.backend.seed

REM Start FastAPI with uvicorn
python -m uvicorn web.backend.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir web\backend

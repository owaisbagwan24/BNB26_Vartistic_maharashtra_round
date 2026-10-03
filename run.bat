@echo off
echo ========================================================
echo        Starting Re:Learn IDE Unified Server...
echo ========================================================
echo.
echo URL: http://localhost:8000
echo.
cd backend
python -m uvicorn main:app --port 8000 --reload
pause

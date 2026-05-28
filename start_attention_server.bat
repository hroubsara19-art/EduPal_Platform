@echo off
echo Starting Attention Tracker Server (FastAPI)...
cd /d "%~dp0"
start /B python attention_tracker/fastapi_server.py
echo Attention Tracker Server started in background.
echo To stop it, run: taskkill /F /IM python.exe

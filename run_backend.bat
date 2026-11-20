@echo off
title AI Doc Manager - Backend
cd /d "D:\ai-doc-manager\backend"
echo Starting Backend Server...
call ".\venv\Scripts\uvicorn.exe" main:app --reload --port 8000
pause

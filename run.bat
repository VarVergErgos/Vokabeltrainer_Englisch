@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo  Bitte zuerst setup.bat starten.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" app\main.py
if errorlevel 1 (
  echo.
  echo  Das Programm wurde mit einem Fehler beendet. Bitte Foto dieses Fensters an Claude schicken.
  pause
)

@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo  Vokabeltrainer - Einrichtung (einmalig, Internet noetig)
echo.
set "PY="
py -3 --version >nul 2>nul && set "PY=py -3"
if not defined PY python --version >nul 2>nul && set "PY=python"
if not defined PY if exist "D:\Python\python.exe" set "PY=D:\Python\python.exe"
if not defined PY (
  echo  FEHLER: Python wurde nicht gefunden.
  echo  Bitte Python 3.12 von python.org installieren und dann setup.bat nochmal starten.
  pause
  exit /b 1
)
echo  Verwende: %PY%
%PY% --version
if not exist ".venv\Scripts\python.exe" (
  %PY% -m venv .venv
)
if not exist ".venv\Scripts\python.exe" (
  echo  FEHLER: Die virtuelle Umgebung konnte nicht angelegt werden. Bitte Foto dieses Fensters an Claude schicken.
  pause
  exit /b 1
)
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo  FEHLER bei der Installation der Pakete. Bitte Foto dieses Fensters an Claude schicken.
  echo  Hinweis: Python 3.14 ist oft zu neu. Empfohlen ist Python 3.12.
  pause
  exit /b 1
)
mkdir voices 2>nul
mkdir dl 2>nul
for %%V in (en_US-ryan-medium de_DE-thorsten-medium) do (
  if not exist "voices\%%V\%%V.onnx" (
    (
      echo  Lade Stimme %%V ...
      curl.exe -L -o "dl\%%V.tar.bz2" "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-%%V.tar.bz2"
      tar.exe -xf "dl\%%V.tar.bz2" -C dl
      move "dl\vits-piper-%%V" "voices\%%V" >nul
    )
  )
)
rmdir /s /q dl 2>nul
echo.
if exist "voices\en_US-ryan-medium\tokens.txt" (
  echo  FERTIG. Starte das Programm mit run.bat
) else (
  echo  Die Stimmen fehlen noch. Bitte setup.bat nochmal starten oder Foto an Claude schicken.
)
pause

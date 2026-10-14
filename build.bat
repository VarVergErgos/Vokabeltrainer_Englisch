@echo off
chcp 65001 >nul
cd /d "%~dp0"
rem Baut das Programm als EXE-Ordner: dist\Vokabeltrainer\Vokabeltrainer.exe
rem Der fertige Ordner laeuft ohne Python und ohne Installation (z. B. von der USB-Platte an einem fremden Rechner).
if not exist ".venv\Scripts\python.exe" (
  echo  Bitte zuerst setup.bat starten.
  pause
  exit /b 1
)
echo  Das Bauen dauert einige Minuten. Bitte warten ...
if exist "dist\Vokabeltrainer" rmdir /s /q "dist\Vokabeltrainer"
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --windowed --name Vokabeltrainer --paths app --collect-all sherpa_onnx --collect-all lameenc --hidden-import lameenc --hidden-import openpyxl app\main.py
if errorlevel 1 (
  echo.
  echo  FEHLER beim Bauen. Bitte Foto dieses Fensters an Claude schicken.
  pause
  exit /b 1
)
xcopy /e /i /y voices "dist\Vokabeltrainer\voices" >nul
xcopy /e /i /y daten "dist\Vokabeltrainer\daten" >nul
xcopy /e /i /y docs "dist\Vokabeltrainer\docs" >nul
if exist vokabeln.db copy /y vokabeln.db "dist\Vokabeltrainer\" >nul
if exist bilder xcopy /e /i /y bilder "dist\Vokabeltrainer\bilder" >nul
echo.
echo  Pruefung der EXE ...
"dist\Vokabeltrainer\Vokabeltrainer.exe" --selftest
if exist "dist\Vokabeltrainer\selftest.txt" (
  type "dist\Vokabeltrainer\selftest.txt"
) else (
  echo  Es wurde keine Pruefdatei erzeugt. Bitte Foto dieses Fensters an Claude schicken.
)
del /q "dist\Vokabeltrainer\selftest.txt" >nul 2>&1
echo.
echo  FERTIG. Den ganzen Ordner dist\Vokabeltrainer auf die USB-Platte kopieren.
echo  Starten dort mit Vokabeltrainer.exe (Doppelklick). Stand Lernen und Datenbank sind enthalten.
pause

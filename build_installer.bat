@echo off
chcp 65001 >nul
cd /d "%~dp0"
rem Erzeugt installer\Vokabeltrainer_Setup.exe (normale Windows-Installation mit Startmenue, Desktop-Symbol und Deinstallation).
rem Enthalten: Programm, Stimmen, leere Kapitel-Vorlage, Hilfe. NICHT enthalten: Datenbank, Lernstand, Bilder, deine Kurs-Vokabeln (Excel), Sprachduschen.
rem Voraussetzung: build.bat wurde ausgefuehrt (Ordner dist\Vokabeltrainer) und Inno Setup 6 ist installiert (kostenlos).
if not exist "dist\Vokabeltrainer\Vokabeltrainer.exe" (
  echo  Der Ordner dist\Vokabeltrainer fehlt. Bitte zuerst build.bat ausfuehren.
  pause
  exit /b 1
)
set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" set "ISCC=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
if "%ISCC%"=="" for %%R in (HKCU HKLM) do for %%K in ("Software\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 6_is1" "Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 6_is1") do for /f "tokens=2,*" %%A in ('reg query "%%R\%%~K" /v InstallLocation 2^>nul ^| find "InstallLocation"') do if exist "%%B\ISCC.exe" set "ISCC=%%B\ISCC.exe"
if "%ISCC%"=="" (
  echo  Inno Setup wurde nicht gefunden. Bitte Foto an Claude schicken.
  echo  Bitte einmalig installieren: https://jrsoftware.org/isdl.php  kostenlos, Inno Setup 6 waehlen
  echo  Danach build_installer.bat noch einmal starten.
  pause
  exit /b 1
)
echo  Bereinigte Kopie ohne persoenliche Daten wird vorbereitet ...
if exist installer_staging rmdir /s /q installer_staging
robocopy "dist\Vokabeltrainer" "installer_staging" /E /XD bilder cache sicherung export export_MP3 Grammatik /XF vokabeln.db fehler.log selftest.txt sprachduschen.json Vokabeltrainer_Englisch_B1.xlsx Audiate_Saetze_Englisch_Deutsch.xlsx >nul
if errorlevel 8 (
  echo  FEHLER beim Kopieren. Bitte Foto dieses Fensters an Claude schicken.
  pause
  exit /b 1
)
if exist "installer_staging\voices\en_US-lessac-medium" rmdir /s /q "installer_staging\voices\en_US-lessac-medium"
rem Sicherheitspruefung: private Dateien duerfen NICHT in der Kopie sein
set "BAD="
for %%F in (vokabeln.db daten\sprachduschen.json daten\Vokabeltrainer_Englisch_B1.xlsx daten\Audiate_Saetze_Englisch_Deutsch.xlsx) do if exist "installer_staging\%%F" set "BAD=%%F"
if exist "installer_staging\voices\en_US-lessac-medium" set "BAD=voices\en_US-lessac-medium"
for %%D in (bilder sicherung export export_MP3 Grammatik cache) do if exist "installer_staging\%%D" set "BAD=%%D"
if defined BAD (
  echo  STOPP: Private Daten gefunden: %BAD%
  echo  Der Installer wird NICHT erzeugt. Bitte Foto an Claude schicken.
  rmdir /s /q installer_staging
  pause
  exit /b 1
)
echo  Pruefung bestanden: keine persoenlichen Daten in der Kopie.
echo  Installationsprogramm wird erzeugt ...
"%ISCC%" installer.iss
if errorlevel 1 (
  echo.
  echo  FEHLER beim Erzeugen. Bitte Foto dieses Fensters an Claude schicken.
  pause
  exit /b 1
)
rmdir /s /q installer_staging
echo.
echo  FERTIG: installer\Vokabeltrainer_Setup.exe
echo  Diese eine Datei kann an andere Personen weitergegeben werden.
start "" "installer"
pause

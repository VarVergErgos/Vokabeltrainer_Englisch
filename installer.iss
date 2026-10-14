; Inno Setup Skript fuer den Vokabeltrainer Englisch B1
; Wird von build_installer.bat benutzt. Quelle ist der bereinigte Ordner installer_staging (ohne persoenliche Daten).
[Setup]
AppId={{B7E3A1C2-5D4F-4E8A-9C61-2F0A7D1E9B34}
AppName=Vokabeltrainer Englisch B1
AppVersion=1.0
AppPublisher=Privates Lernprojekt
DefaultDirName=C:\Vokabeltrainer
DisableDirPage=no
LicenseFile=LIZENZEN.txt
InfoAfterFile=INSTALLATION.txt
DefaultGroupName=Vokabeltrainer
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=installer
OutputBaseFilename=Vokabeltrainer_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\Vokabeltrainer.exe
SetupLogging=yes

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "Symbol auf dem Desktop anlegen"; GroupDescription: "Zusätzliche Symbole:"

[Files]
Source: "LIZENZEN.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "installer_staging\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{autoprograms}\Vokabeltrainer Englisch B1"; Filename: "{app}\Vokabeltrainer.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\Vokabeltrainer Englisch B1"; Filename: "{app}\Vokabeltrainer.exe"; WorkingDir: "{app}"; Tasks: desktopicon
Name: "{autoprograms}\Vokabeltrainer Anleitung"; Filename: "{app}\docs\Bedienungsanleitung_Vokabeltrainer.docx"

[UninstallDelete]
; Datenbank, Bilder und Sicherungen des Benutzers bleiben bewusst erhalten.

[Run]
Filename: "{app}\Vokabeltrainer.exe"; Description: "Vokabeltrainer jetzt starten"; Flags: nowait postinstall skipifsilent

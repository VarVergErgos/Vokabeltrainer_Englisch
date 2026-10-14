# Vokabeltrainer Englisch B1

Ein privates Lernprogramm für Windows. Es läuft ohne Internet und ist für Menschen gedacht, die Englisch (B1) in kleinen Schritten üben wollen, auch mit Hörverlust bei hohen Tönen.

**Nur für private, nicht-kommerzielle Nutzung.** Keine Garantie, Nutzung auf eigene Verantwortung.

## Was kann es?
- Vorlesen von Wörtern und Sätzen (langsam, Hörhilfe hebt hohe Töne an)
- Abfrage mit Karteikarten in drei Richtungen und Wiederholung nach 1, 3, 7, 14 Tagen
- Eigene Kapitel anlegen, Excel-Import mit Vorlage, Bilder, Export (MP3, PDF, Excel, TXT)
- MP3 mit Übersetzung (Deutsch und Englisch) für unterwegs
- Suche, Fortschritt, mehrere Benutzer, Bedienungsanleitung im Programm

## Installation (für Anwender)
1. Unter *Releases* die Datei `Vokabeltrainer_Setup.exe` herunterladen und starten.
2. Vorgeschlagener Ordner: `C:\Vokabeltrainer`. Möglich ist auch `D:\Vokabeltrainer`.
3. Keine Administratorrechte nötig. Die Datenbank ist am Anfang leer. Die Excel-Vorlage liegt im Ordner `daten`.

Windows kann melden „Der Computer wurde durch Windows geschützt“, weil das Programm nicht signiert ist. Dann *Weitere Informationen* und *Trotzdem ausführen*.

## Selbst bauen
`setup.bat` (einmalig, holt Python-Pakete und die englische Stimme), `run.bat` zum Starten, `build.bat` baut die EXE, `build_installer.bat` das Setup (Inno Setup 6 nötig).

## Gebaut mit
Python, PySide6/Qt (LGPL), SQLite, sherpa-onnx (Apache-2.0) mit Piper-Stimmen, lameenc (LGPL), openpyxl, python-docx, numpy, reportlab, PyInstaller, Inno Setup. Entwickelt im Dialog mit der KI Claude (Anthropic). Alle Lizenzen: `LIZENZEN.txt` und im Programm unter *Info & Lizenzen*.

## Stimmen
- Englisch: `en_US-ryan-medium`, Daten RyanSpeech, **CC BY-NC-SA 4.0** (nur nicht-kommerziell)
- Deutsch: `de_DE-thorsten-medium` (Thorsten-Voice), CC0

## Eigene Inhalte
Das Repository enthält keine Kursinhalte, keine Bücher und keine Wortlisten. Bitte lege nur Inhalte ein, die du selbst nutzen darfst.

## Lizenz
Der Programmcode steht unter CC BY-NC-SA 4.0 (siehe `LICENSE`). Die genutzten Bibliotheken behalten ihre eigenen Lizenzen.

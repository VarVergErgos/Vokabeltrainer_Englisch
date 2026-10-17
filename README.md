# Vokabeltrainer Englisch B1

Ein kostenloses Lernprogramm für Windows, um Englisch (Niveau B1) in kleinen Schritten zu üben. Es läuft ohne Internet und ohne Anmeldung. Die Vokabeln werden langsam und deutlich vorgelesen. Eine Hörhilfe hebt hohe Töne an, das hilft bei Hörverlust.

> **Nur für private, nicht-kommerzielle Nutzung. Keine Garantie.**

## Herunterladen und installieren

1. Öffne die Seite **[Releases](../../releases/latest)** und lade die Datei **`Vokabeltrainer_Setup.exe`** herunter (ca. 220 MB).
2. Doppelklick auf die Datei. Du brauchst keine Administratorrechte.
3. Vorgeschlagener Ordner: `C:\Vokabeltrainer`. Du kannst auch `D:\Vokabeltrainer` oder einen anderen Ordner wählen.
4. Starte das Programm über das Startmenü oder das Desktop-Symbol.

Windows meldet beim ersten Start vielleicht „Der Computer wurde durch Windows geschützt“, weil das Programm nicht signiert ist. Klicke dann auf **Weitere Informationen** und **Trotzdem ausführen**.

## Simulation ansehen / See it in action

Eine interaktive, zweisprachige Simulation (Deutsch/English) zeigt die Oberfläche, den Excel-Import, den Export als PDF und Excel, die MP3-Erstellung, die Installation und alle Lizenzhinweise:
**https://varvergergos.github.io/Vokabeltrainer_Englisch/**
(Oder die Datei `docs/index.html` herunterladen und im Browser öffnen.)

## Der erste Start

Das Programm startet leer. Du legst eigene Kapitel an oder liest sie aus Excel ein. Dafür liegt im Ordner `daten` die Datei **`Kapitel_Vorlage.xlsx`**. Fülle sie aus und wähle im Programm **Kapitel → Kapitel aus Excel**. Eine Bedienungsanleitung findest du im Programm unter **Hilfe** und im Startmenü.

## Was kann es?

- **Vorlesen** von Wörtern und Sätzen mit einstellbarem Tempo und Hörhilfe
- **Abfrage** mit Karteikarten in drei Richtungen (Englisch → Deutsch, Deutsch → Englisch, Hören → Schreiben). Das Programm fragt nach 1, 3, 7 und 14 Tagen wieder
- **Eigene Kapitel** mit Bildern, Export als MP3, PDF, Excel und TXT
- **Grammatik und Zeiten**: zeigt alle PDFs aus dem Ordner `Grammatik` in einer Liste und öffnet sie per Doppelklick (der Ordner ist nach der Installation leer, du legst eigene PDFs hinein)
- **MP3 mit Übersetzung** (Deutsch und Englisch) zum Anhören unterwegs
- Suche, Fortschrittsanzeige, mehrere Benutzer

## Datenschutz

Alles bleibt auf deinem Rechner. Das Programm sendet keine Daten.

## Eigene Inhalte

Das Programm enthält keine Kursinhalte, keine Lehrbücher und keine Wortlisten. Trage nur Inhalte ein, die du selbst nutzen darfst. Gib Inhalte aus gekauften Büchern nicht weiter.

## Selbst bauen (für Fortgeschrittene)

Voraussetzung: Python 3.12. `setup.bat` (einmalig, holt Pakete und die Stimmen), `run.bat` zum Starten, `build.bat` baut die EXE, `build_installer.bat` baut das Setup (Inno Setup 6 nötig).

## Gebaut mit

Python, PySide6/Qt (LGPL), SQLite, sherpa-onnx (Apache-2.0) mit Piper-Stimmen, lameenc (LGPL), openpyxl, python-docx, numpy, reportlab, PyInstaller, Inno Setup. Entwickelt im Dialog mit der KI Claude (Anthropic).

Stimmen: Englisch `en_US-ryan-medium` (RyanSpeech, CC BY-NC-SA 4.0, nur nicht-kommerziell), Deutsch `de_DE-thorsten-medium` (Thorsten-Voice, CC0). Alle Lizenzen: [`LIZENZEN.txt`](LIZENZEN.txt) und im Programm unter **Info & Lizenzen**.

## Lizenz

Programmcode: CC BY-NC-SA 4.0 (siehe [`LICENSE`](LICENSE)). Die genutzten Bibliotheken und Stimmen behalten ihre eigenen Lizenzen.

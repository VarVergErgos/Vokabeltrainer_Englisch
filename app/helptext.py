# Bedienungsanleitung: eine Quelle fuer die Hilfe im Programm (HTML) und die Word-Datei.
# Eintraege: (Ueberschrift, [Absatz | ("liste", [Punkte]) | ("tipp", Text)])
TITEL = "Vokabeltrainer Englisch B1 – Bedienungsanleitung"

KAPITEL = [
 ("Was kann das Programm?", [
   "Der Vokabeltrainer hilft dir, Englisch für den B1-Kurs zu lernen. Alles liegt in einem Ordner und läuft ohne Internet.",
   ("liste", [
     "Vorlesen: Wörter und Sätze werden langsam und deutlich vorgelesen. Die Stimme hebt die hohen Töne an (Hörhilfe).",
     "Abfrage: Karteikarten in drei Richtungen. Das Programm merkt sich, was du kannst, und fragt zur richtigen Zeit wieder.",
     "Fortschritt: Du siehst, wie viele Karten du schon kannst, und wie viele Tage du hintereinander geübt hast.",
     "Kapitel: Du legst eigene Kapitel an, gibst Einträge ein, fügst Bilder und Screenshots hinzu und exportierst alles.",
     "Mehrere Benutzer teilen sich denselben Lernstand.",
   ])]),
 ("Installation", [
   "Doppelklick auf Vokabeltrainer_Setup.exe. Administratorrechte sind nicht nötig. Vorgeschlagen wird der Ordner C:\\Vokabeltrainer. Im Setup kannst du auch D:\\Vokabeltrainer oder einen anderen Ordner wählen.",
   "Windows meldet beim ersten Start eventuell „Der Computer wurde durch Windows geschützt“, weil das Programm nicht signiert ist. Dann „Weitere Informationen“ und „Trotzdem ausführen“ wählen.",
   "Beim ersten Start ist die Datenbank leer. Im Ordner daten liegt die Excel-Vorlage Kapitel_Vorlage.xlsx. Fülle sie aus und lies sie über Kapitel > Kapitel aus Excel ein.",
   "Das Programm ist nur für private, nicht-kommerzielle Nutzung. Mehr dazu im Menüpunkt Info & Lizenzen.",
   "Deinstallieren: Windows-Einstellungen > Apps, oder Startmenü > Vokabeltrainer deinstallieren. Deine Daten im Programmordner sichere vorher.",
 ]),
 ("Starten", [
   "Doppelklick auf run.bat im Ordner Vokabeltrainer. Beim allerersten Mal wird vorher setup.bat ausgeführt (einmalig, mit Internet).",
   "Links siehst du die Menüpunkte: Vorlesen, Abfrage, Kapitel, MP3 erstellen, Grammatik und Zeiten, Sprachduschen, Suchen, Fortschritt, Einstellungen, Hilfe und Info & Lizenzen. Unten links steht, wer angemeldet ist.",
 ]),
 ("Vorlesen", [
   "Wähle oben ein Kapitel. Jede Zeile ist ein Wort oder Satz mit deutscher Übersetzung.",
   ("liste", [
     "Pfeil neben einer Zeile: nur diese Zeile vorlesen.",
     "„Alle vorlesen“: das ganze Kapitel nacheinander.",
     "Tempo: der Regler stellt die Geschwindigkeit ein (0,6 bis 1,2). Langsamer ist meistens besser zum Verstehen.",
     "Stimme: Ryan (männlich, tief). Wenn die Stimme Lessac im Ordner voices liegt, kannst du sie auch wählen.",
     "Hörhilfe: hebt hohe Töne leicht an. Bei Hochtonverlust an lassen.",
   ]),
   ("tipp", "Beim ersten Vorlesen eines Satzes dauert es einen Moment. Danach ist er gespeichert und kommt sofort."),
 ]),
 ("Abfrage", [
   "Oben wählst du die Richtung und das Kapitel (oder alle Kapitel):",
   ("liste", [
     "Englisch → Deutsch: Du siehst das englische Wort und sagst die deutsche Bedeutung.",
     "Deutsch → Englisch: Du siehst das deutsche Wort und sagst das englische.",
     "Hören → Schreiben: Du hörst den englischen Satz, tippst ihn ins Feld und drückst Enter. Das Programm prüft deine Eingabe und bewertet selbst.",
   ]),
   "Ablauf einer Karte: Antwort überlegen, dann Enter, Leertaste oder den Knopf „Antwort zeigen“ drücken. Die Lösung erscheint. Dann bewertest du dich selbst:",
   ("liste", ["J oder Knopf „Wusste ich (J)“: richtig.", "N oder Knopf „Nochmal üben (N)“: falsch."]),
   "Wiederholung: Richtig beantwortete Karten kommen nach 1, 3, 7 und 14 Tagen wieder. Nach der vierten Stufe zählt die Karte als „kann ich“. Eine falsche Karte kommt in derselben Runde noch einmal und ist heute wieder fällig.",
   "Jede der drei Richtungen hat ihren eigenen Lernstand.",
 ]),
 ("Fortschritt", [
   "Hier siehst du für jede Richtung deinen Lernfortschritt in Prozent, insgesamt und für jedes Kapitel. Der Fortschritt zeigt, wie weit die Karten auf den vier Lernstufen sind: Stufe 1 = nach 1 Tag wieder abgefragt, Stufe 2 = nach 3 Tagen, Stufe 3 = nach 7 Tagen, Stufe 4 = nach 14 Tagen. 100 % heißt: jede Karte hat Stufe 4. Eine falsche Antwort setzt die Karte auf Stufe 0 zurück.",
   "Darunter steht, wie viele Karten auf welcher Stufe sind, außerdem „sicher“ (Stufe 3 und höher), heute fällig, heute beantwortet und die Lernserie (Tage in Folge, an denen du geübt hast). Der Balken ist orange unter 50 % und grün ab 50 %. Die Seite zeigt immer den aktuellen Stand.",
 ]),
 ("Kapitel anlegen und bearbeiten", [
   "Im Menüpunkt Kapitel steht links die Kapitelliste und rechts der Inhalt des gewählten Kapitels.",
   ("liste", [
     "Neues Kapitel: Titel eingeben, fertig. Die Nummer wird automatisch vergeben.",
     "Umbenennen, Kapitel löschen: Beim Löschen kommt vorher eine Rückfrage. Gelöscht werden auch die Bilder des Kapitels.",
     "Neuer Eintrag: Englisch und Deutsch sind Pflicht. Aussprache und Beispielsatz sind freiwillig.",
     "Ändern: Doppelklick auf einen Eintrag oder den Knopf „Ändern“.",
     "Eintrag löschen: Der Lernstand dieses Eintrags geht dabei verloren.",
   ]),
   ("tipp", "Doppelte Sätze: Gibt es einen Satz schon, sagt dir das Programm in welchem Kapitel. Er wird nicht noch einmal gespeichert. Groß- und Kleinschreibung und Satzzeichen spielen dabei keine Rolle."),
 ]),
 ("Ein ganzes Kapitel aus Excel einlesen", [
   "Das geht am schnellsten für viele Einträge auf einmal.",
   ("liste", [
     "Knopf „Excel-Vorlage öffnen“ (oder Datei daten\\Kapitel_Vorlage.xlsx).",
     "Im Blatt „Kapitel 1“ in Zelle B1 den Titel eintragen. In B2 kurz schreiben, worum es geht.",
     "Ab Zeile 5: links Englisch, daneben Deutsch. Aussprache und Beispielsätze sind freiwillig.",
     "Mehrere Kapitel: das Blatt kopieren. Jedes Blatt wird ein Kapitel.",
     "Datei speichern und schließen.",
     "In der App: Knopf „Kapitel aus Excel“ und die Datei wählen.",
   ]),
   "Danach zeigt dir das Programm, was neu ist und welche Sätze übersprungen wurden, weil es sie schon gibt.",
   ("tipp", "Die Blätter „Anleitung“ und „Beispiel“ in der Vorlage werden nicht eingelesen. Die Tabelle beginnt immer in Zeile 5."),
 ]),
 ("Bilder und Screenshots", [
   "Zu jedem Kapitel kannst du Bilder speichern, zum Beispiel einen Screenshot aus dem Kurs.",
   ("liste", [
     "Bild aus Datei: ein oder mehrere Bilder auswählen.",
     "Aus Zwischenablage (Strg+V): Mit Windows-Taste + Umschalt + S einen Ausschnitt des Bildschirms aufnehmen, dann hier Strg+V drücken.",
     "Doppelklick auf ein Bild vergrößert es. „Beschriftung“ fügt einen Text hinzu. „Bild löschen“ entfernt es.",
   ]),
   "Die Bilder liegen im Ordner bilder. Sie erscheinen auch im PDF-Export.",
 ]),
 ("Exportieren", [
   "Unten im Bereich Kapitel steht „Exportieren“. Die Dateien werden standardmäßig im Ordner export gespeichert.",
   ("liste", [
     "MP3: Alle englischen Wörter und Sätze (mit Beispielsatz) nacheinander, mit kurzen Pausen. Es gelten Stimme, Tempo und Hörhilfe aus dem Bereich Vorlesen. Das Erzeugen dauert je nach Länge etwas.",
     "PDF: Lernblatt zum Ausdrucken, mit großer Schrift und Bildern.",
     "Excel: Tabelle mit allen Einträgen, auch als Vorlage für weitere Bearbeitung.",
     "TXT: Textdatei (UTF-8), Englisch und darunter Deutsch.",
   ]),
 ]),
 ("MP3 erstellen (Deutsch und Englisch)", [
   "Menüpunkt „MP3 erstellen“: Du machst aus deinen Kapiteln MP3-Dateien zum Anhören unterwegs. In der MP3 sprechen die Stimmen den deutschen Satz und danach den englischen.",
   ("liste", [
     "Kreuze links die Kapitel an (oder „Alle auswählen“) und klicke auf „MP3 und Excel erstellen“.",
     "Reihenfolge: „Deutsch, dann Englisch“ oder umgekehrt.",
     "Pause dazwischen: Zeit zwischen deutschem und englischem Satz (Voreinstellung 1,5 Sekunden). „Pause nach jeder Zeile“: Zeit vor dem nächsten Paar (Voreinstellung 3 Sekunden).",
     "Tempo, englische Stimme und Hörhilfe stammen aus dem Bereich Vorlesen. Die deutsche Stimme heißt Thorsten.",
     "Alles landet im Ordner export_MP3 (Knopf „Ordner export_MP3 öffnen“). Dateiname: Kapitelnummer mit vier Stellen und der Kapitelname, höchstens 25 Zeichen, zum Beispiel „0012 Einheit 17 used to.mp3“.",
     "Zu jeder MP3 legt das Programm eine Excel-Datei mit demselben Namen an (Spalten Nr, Deutsch, Englisch). Aus dieser Excel-Datei wird die MP3 erzeugt.",
     "Excel verbessern: Datei öffnen, Text ändern, speichern. Danach „Vorhandene Excel-Datei verwenden“ ankreuzen und noch einmal erstellen. Die MP3 wird dann neu gemacht und die Excel-Datei bleibt, wie du sie gespeichert hast.",
   ]),
   ("tipp", "Eine MP3 mit vielen Zeilen dauert einige Minuten. Beim zweiten Mal geht es schneller, weil die Sprache gespeichert ist. Mit „Abbrechen“ stoppst du nach dem aktuellen Kapitel."),
 ]),
 ("Grammatik und Zeiten", [
   "Dieser Bereich zeigt alle PDF-Dateien aus dem Ordner „Grammatik“ im Programmordner. Das können Leitfäden zu den Zeiten (Simple Present, Present Continuous, Simple Past und weitere), Einstufungstests oder deine eigenen Unterlagen sein.",
   ("liste", [
     "Die Liste zeigt Titel, Art (Leitfaden, Test, Sammlung) und Größe. Die Nummer am Dateianfang bestimmt die Reihenfolge.",
     "Doppelklick auf eine Zeile oder „Öffnen“ zeigt die PDF in deinem PDF-Programm.",
     "Suchfeld: tippe ein Stück vom Namen, z. B. „Present“ oder „Test“.",
     "„Ordner öffnen“ zeigt den Ordner im Explorer. Kopiere dort neue PDFs hinein und klicke danach auf „Neu einlesen“.",
   ]),
   ("tipp", "Die PDFs gehören dir und bleiben auf deinem Rechner. Der Ordner Grammatik wird bei der Installation leer angelegt. Gib fremde Unterlagen nicht weiter."),
 ]),
 ("Sprachduschen (Zusatzbereich für eigene Lernbücher)", [
   "Dieser Zusatzbereich ist für den Inhalt von Lernbüchern, die du selbst besitzt und nutzen darfst. Er ist leer, bis du eine passende Datei einliest. Er ist getrennt von deinen eigenen Kapiteln. Er hat einen eigenen Lernstand und einen eigenen Fortschritt.",
   ("liste", [
     "Aufbau: Jede Lektion eines Buches ist ein Kapitel. Sie hat drei Rubriken: Vokabeln, Dialog und Nachsprechen, genau wie im Buch.",
     "Oben wählst du das Buch und die Rubrik. Danach wählst du mit den drei Knöpfen: Vorlesen, Abfrage oder Fortschritt.",
     "Vorlesen: wie im normalen Bereich, mit eigenem Tempo, eigener Stimme und Hörhilfe. Bei Dialogen steht der Sprecher über der Zeile.",
     "Abfrage: Englisch → Deutsch, Deutsch → Englisch und Hören → Schreiben. Alle Karten stammen aus dem gewählten Buch und der gewählten Rubrik.",
   ]),
   ("tipp", "Bei English Conversation 1 und 2 sowie bei den Nachsprechsätzen von Basis 1 und Sales Communication 1 und 2 steht im Buch nur Englisch. Diese Zeilen werden vorgelesen und in „Hören → Schreiben“ geübt. In den beiden anderen Richtungen kommen sie nicht vor, weil die deutsche Übersetzung fehlt."),
   "Die Daten kommen aus der Datei daten\\sprachduschen.json, falls du eine solche Datei selbst angelegt hast. Gib solche Inhalte nicht weiter, wenn sie aus gekauften Büchern stammen.",
 ]),
 ("Einstellungen, Benutzer und Sicherung", [
   ("liste", [
     "Schriftgröße und hell/dunkel: Einstellungen. Die Schrift wird sofort größer oder kleiner.",
     "Benutzer: Anlegen, Umbenennen, Löschen. Der Name steht nur im Verlauf. Der Lernstand ist für alle gleich.",
     "Sicherung: Der Knopf kopiert die Datenbank mit Datum in den Ordner sicherung. Mach vor größeren Änderungen eine Sicherung.",
     "Excel importieren: liest den Original-Vokabeltrainer ein (Doppelte werden übersprungen).",
   ]),
 ]),
 ("Suchen", [
   "Im Menüpunkt Suchen findest du jedes deutsche oder englische Wort in deinen eigenen Kapiteln und in den Sprachduschen.",
   ("liste", [
     "Tippe ein Wort oder einen Satzteil in das Feld. Die Treffer erscheinen sofort während du tippst.",
     "Die besten Treffer stehen oben: zuerst genau dieses Wort, dann Wörter, die so anfangen, dann alles, was den Text enthält. Treffer aus deinen eigenen Kapiteln stehen vor den Sprachduschen.",
     "Wo: überall, nur deine Kapitel oder nur Sprachduschen. Sprache: Englisch und Deutsch, nur Englisch oder nur Deutsch.",
     "Ganzes Wort: findet „art“ dann nicht mehr in „article“. Auch in Beispielsätzen: sucht zusätzlich in den Beispielsätzen.",
     "Umlaute sind egal: Wenn du „apfel“ tippst, findet das Programm auch „Äpfel“.",
     "Englisch anhören: spielt die markierte Zeile vor. Im Kapitel öffnen (oder Doppelklick): springt zum Eintrag im Bereich Vorlesen bzw. Sprachduschen.",
   ]),
   "In der Spalte „Wo steht es“ siehst du Kapitel, Buch, Lektion und Rubrik.",
 ]),
 ("Installationsprogramm für andere Personen", [
   "Damit andere Personen das Programm wie gewohnt installieren können (Doppelklick, weiter, fertig), gibt es ein Installationsprogramm.",
   ("liste", [
     "Einmalig Inno Setup 6 installieren (kostenlos, jrsoftware.org). Das ist nur für das Erzeugen nötig, nicht für die Empfänger.",
     "build.bat ausführen (erzeugt den Ordner dist\\Vokabeltrainer), danach build_installer.bat.",
     "Ergebnis: die eine Datei installer\\Vokabeltrainer_Setup.exe. Sie legt das Programm unter dem eigenen Benutzer an (ohne Administratorrechte), mit Eintrag im Startmenü, Desktop-Symbol und Deinstallation.",
     "Die Installation enthält keine persönlichen Daten: keine Datenbank, keinen Lernstand, keine Bilder, keine Kurs-Vokabeln und nicht die Sprachduschen. Das Programm startet bei den Empfängern komplett leer. Sie legen eigene Kapitel an oder lesen sie mit der Excel-Vorlage ein.",
   ]),
   ("tipp", "Die Sprachduschen stammen aus deinen gekauften Unterlagen. Sie werden bewusst nicht weitergegeben. Andere Personen müssen ihre eigenen Unterlagen haben."),
   "Windows kann beim ersten Start melden „Der Computer wurde durch Windows geschützt“, weil das Programm nicht signiert ist. Dann „Weitere Informationen“ und „Trotzdem ausführen“ wählen. Auf Firmenrechnern kann die Installation gesperrt sein.",
 ]),
 ("Programm auf der USB-Platte und an fremden Rechnern", [
   "Wenn du auf einem Rechner nichts installieren darfst, nutzt du die EXE-Version.",
   ("liste", [
     "Einmal auf deinem eigenen Rechner: Doppelklick auf build.bat. Das Bauen dauert einige Minuten. Am Ende prüft das Programm sich selbst und zeigt die Ergebnisse an.",
     "Danach liegt der Ordner dist\\Vokabeltrainer bereit. Kopiere diesen ganzen Ordner auf die USB-Platte.",
     "Auf dem fremden Rechner: Vokabeltrainer.exe per Doppelklick starten. Python und setup.bat sind nicht nötig.",
     "Datenbank, Lernstand, Bilder, Stimmen und Sprachduschen liegen im selben Ordner und wandern mit.",
   ]),
   ("tipp", "Der Lernstand der EXE-Version ist eine Kopie vom Zeitpunkt des Bauens. Danach lernen die beiden Ordner getrennt weiter. Nimm am besten einen der beiden als Hauptordner."),
   "Wenn die EXE nicht startet, steht der Grund in der Datei fehler.log neben dem Programm. Manche Firmenrechner blockieren unbekannte Programme. Dann hilft nur die IT-Abteilung.",
 ]),
 ("Tastatur", [
   ("liste", ["Enter oder Leertaste: Lösung zeigen.", "J: gewusst. N: nicht gewusst.", "Strg+V im Bereich Kapitel: Bild aus der Zwischenablage einfügen.", "Tab: zum nächsten Feld oder Knopf."]),
 ]),
 ("Wo liegen meine Daten?", [
   "Alles liegt im Programmordner: vokabeln.db (Wörter und Lernstand), bilder, export, sicherung, cache (gespeicherte Sprachdateien) und voices (Stimmen). Wenn du den Ordner auf einen USB-Stick kopierst, nimmst du alles mit.",
   ("tipp", "Der Ordner cache darf jederzeit gelöscht werden. Er füllt sich beim Vorlesen von selbst wieder."),
 ]),
 ("Wenn etwas nicht klappt", [
   ("liste", [
     "Keine Stimme: setup.bat noch einmal ausführen.",
     "MP3-Export klappt nicht: setup.bat noch einmal ausführen, er installiert das MP3-Paket.",
     "Neue Funktion fehlt: Programm ganz schließen und run.bat neu starten.",
     "Sonst: ein Foto der Fehlermeldung an Claude schicken.",
   ]),
 ]),
]

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def html(fs=None):
    h = ["<h1>%s</h1>" % esc(TITEL)]
    h.append("<p><b>Inhalt:</b> " + " · ".join('<a href="#k%d">%s</a>' % (i, esc(t)) for i, (t, _) in enumerate(KAPITEL)) + "</p>")
    for i, (t, items) in enumerate(KAPITEL):
        h.append('<h2><a name="k%d"></a>%s</h2>' % (i, esc(t)))
        for it in items:
            if isinstance(it, str):
                h.append("<p>%s</p>" % esc(it))
            elif it[0] == "liste":
                h.append("<ul>%s</ul>" % "".join("<li>%s</li>" % esc(x) for x in it[1]))
            else:
                h.append('<p style="background:#fff4cc;color:#222"><b>Tipp:</b> %s</p>' % esc(it[1]))
    return "".join(h)

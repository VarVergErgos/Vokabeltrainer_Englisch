# Menue "MP3 erstellen": je Kapitel eine MP3 (Deutsch, Pause, Englisch) und die Excel-Datei, aus der sie entsteht.
# Ablage: Ordner export_MP3 im Programmordner, Dateiname "0001 Kapitelname" (Name hoechstens 25 Zeichen).
import os, sys, subprocess
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem,
                               QComboBox, QDoubleSpinBox, QCheckBox, QProgressBar, QPlainTextEdit, QMessageBox)
import db, exporter, speech
from paths import ensure


class Mp3Job(QThread):
    prog = Signal(int, int, str)       # fertige Kapitel, alle Kapitel, aktueller Text
    line = Signal(str)
    done = Signal(int, int)            # erfolgreich, fehlgeschlagen

    def __init__(self, ids, speaker, opt):
        super().__init__(); self.ids, self.speaker, self.opt = ids, speaker, opt; self.stop = False

    def run(self):
        ok = bad = 0
        c = db.connect(db.db_path())
        o = self.opt
        for n, kid in enumerate(self.ids):
            if self.stop:
                self.line.emit("Abgebrochen."); break
            k = c.execute("SELECT * FROM kapitel WHERE id=?", (kid,)).fetchone()
            name = exporter.mp3_basename(k)
            self.prog.emit(n, len(self.ids), name)
            try:
                mp, xl, anz = exporter.export_mp3_paare(
                    c, k, o["ordner"], self.speaker, o["voice_en"], speech.DE_LABEL, o["speed"], o["hoer"],
                    o["de_zuerst"], o["p1"], o["p2"], o["alte_excel"], True,
                    lambda i, m: self.prog.emit(n, len(self.ids), "%s (%d von %d)" % (name, i, m)))
                self.line.emit("Fertig: %s  (%d Zeilen)" % (os.path.basename(mp), anz)); ok += 1
            except Exception as ex:
                import traceback
                tb = traceback.format_exc()
                try:
                    with open(ensure("") + os.sep + "fehler.log", "a", encoding="utf-8") as f:
                        f.write("MP3 %s\n%s\n" % (name, tb))
                except Exception:
                    pass
                last = [z.strip() for z in tb.strip().split("\n") if z.strip().startswith("File")][-1:]
                self.line.emit("FEHLER bei %s: %s  [%s]" % (name, ex, last[0] if last else ""))
                bad += 1
        c.close()
        self.prog.emit(len(self.ids), len(self.ids), "")
        self.done.emit(ok, bad)


class Mp3Page(QWidget):
    def __init__(self, conn, speaker, voice_fn, status):
        """voice_fn() liefert (Stimmenname Englisch, Tempo, Hoerhilfe) aus dem Bereich Vorlesen."""
        super().__init__()
        self.conn, self.speaker, self.voice_fn, self.status, self.job = conn, speaker, voice_fn, status, None
        v = QVBoxLayout(self); v.setContentsMargins(24, 20, 24, 16)
        t = QLabel("MP3 erstellen"); t.setObjectName("title"); v.addWidget(t)
        s = QLabel("Je Kapitel eine MP3 mit Deutsch und Englisch. Dazu wird die Excel-Datei angelegt, aus der die MP3 entsteht. "
                   "Beides landet im Ordner export_MP3."); s.setObjectName("muted"); s.setWordWrap(True); v.addWidget(s)
        h = QHBoxLayout(); a = QPushButton("Alle auswählen"); a.clicked.connect(lambda: self._all(True))
        b = QPushButton("Keine"); b.clicked.connect(lambda: self._all(False)); h.addWidget(a); h.addWidget(b); h.addStretch(1)
        self.cnt = QLabel(""); self.cnt.setObjectName("chip"); h.addWidget(self.cnt); v.addLayout(h)
        self.lst = QListWidget(); self.lst.itemChanged.connect(self._count); v.addWidget(self.lst, 1)
        o = QHBoxLayout()
        o.addWidget(QLabel("Reihenfolge")); self.order = QComboBox(); self.order.addItems(["Deutsch, dann Englisch", "Englisch, dann Deutsch"]); o.addWidget(self.order)
        o.addWidget(QLabel("Pause dazwischen")); self.p1 = QDoubleSpinBox(); self.p1.setRange(0.0, 10.0); self.p1.setSingleStep(0.1); self.p1.setValue(1.5); self.p1.setSuffix(" s"); o.addWidget(self.p1)
        o.addWidget(QLabel("Pause nach jeder Zeile")); self.p2 = QDoubleSpinBox(); self.p2.setRange(0.0, 15.0); self.p2.setSingleStep(0.5); self.p2.setValue(3.0); self.p2.setSuffix(" s"); o.addWidget(self.p2)
        o.addStretch(1); v.addLayout(o)
        self.alt = QCheckBox("Vorhandene Excel-Datei verwenden, wenn es sie schon gibt (z. B. nach eigenen Korrekturen)")
        v.addWidget(self.alt)
        self.hint = QLabel(""); self.hint.setObjectName("muted"); self.hint.setWordWrap(True); v.addWidget(self.hint)
        r = QHBoxLayout()
        self.go = QPushButton("MP3 und Excel erstellen"); self.go.setObjectName("pri"); self.go.clicked.connect(self.start); r.addWidget(self.go)
        self.stopb = QPushButton("Abbrechen"); self.stopb.setEnabled(False); self.stopb.clicked.connect(self._stop); r.addWidget(self.stopb)
        self.openb = QPushButton("Ordner export_MP3 öffnen"); self.openb.clicked.connect(self.open_folder); r.addWidget(self.openb)
        r.addStretch(1); v.addLayout(r)
        self.bar = QProgressBar(); self.bar.setTextVisible(True); v.addWidget(self.bar)
        self.log = QPlainTextEdit(); self.log.setReadOnly(True); self.log.setMaximumHeight(130); v.addWidget(self.log)
        self.refresh()

    def refresh(self):
        if self.job is not None and self.job.isRunning():
            return
        marked = {self.lst.item(i).data(Qt.UserRole) for i in range(self.lst.count()) if self.lst.item(i).checkState() == Qt.Checked}
        self.lst.blockSignals(True); self.lst.clear()
        for k in db.chapters(self.conn):
            it = QListWidgetItem("%04d  %s   (%d Einträge)" % (k["nr"], k["titel"], k["anzahl"]))
            it.setData(Qt.UserRole, k["id"]); it.setFlags(it.flags() | Qt.ItemIsUserCheckable)
            it.setCheckState(Qt.Checked if k["id"] in marked else Qt.Unchecked); self.lst.addItem(it)
        self.lst.blockSignals(False); self._count()
        ok = speech.voice_ok(speech.DE_VOICE)
        self.hint.setText("" if ok else "Die deutsche Stimme fehlt im Ordner voices (de_DE-thorsten-medium). Ohne sie kann keine MP3 mit Deutsch erstellt werden.")
        self.go.setEnabled(ok)

    def _all(self, on):
        self.lst.blockSignals(True)
        for i in range(self.lst.count()):
            self.lst.item(i).setCheckState(Qt.Checked if on else Qt.Unchecked)
        self.lst.blockSignals(False); self._count()

    def _ids(self):
        return [self.lst.item(i).data(Qt.UserRole) for i in range(self.lst.count()) if self.lst.item(i).checkState() == Qt.Checked]

    def _count(self, *_):
        self.cnt.setText("%d von %d Kapiteln gewählt" % (len(self._ids()), self.lst.count()))

    def start(self):
        ids = self._ids()
        if not ids:
            QMessageBox.information(self, "MP3 erstellen", "Bitte mindestens ein Kapitel ankreuzen."); return
        voice_en, speed, hoer = self.voice_fn()
        if not speech.voice_ok(speech.VOICES[voice_en]):
            QMessageBox.warning(self, "MP3 erstellen", "Die englische Stimme fehlt im Ordner voices."); return
        opt = dict(ordner=ensure("export_MP3"), voice_en=voice_en, speed=speed, hoer=hoer, de_zuerst=self.order.currentIndex() == 0,
                   p1=self.p1.value(), p2=self.p2.value(), alte_excel=self.alt.isChecked())
        self.log.clear(); self.bar.setRange(0, len(ids)); self.bar.setValue(0); self.bar.setFormat("%v von %m")
        self.go.setEnabled(False); self.stopb.setEnabled(True)
        self.job = Mp3Job(ids, self.speaker, opt)
        self.job.prog.connect(self._prog); self.job.line.connect(self.log.appendPlainText); self.job.done.connect(self._done)
        self.job.start()

    def _prog(self, n, m, text):
        self.bar.setValue(n); self.status("MP3: " + text if text else "")

    def _stop(self):
        if self.job:
            self.job.stop = True

    def _done(self, ok, bad):
        self.go.setEnabled(True); self.stopb.setEnabled(False)
        msg = "%d Kapitel fertig" % ok + ("  ·  %d mit Fehler" % bad if bad else "")
        self.log.appendPlainText(msg); self.status(msg)

    def open_folder(self):
        d = ensure("export_MP3")
        if sys.platform == "win32":
            os.startfile(d)
        else:
            subprocess.Popen(["xdg-open", d])

    def stop_job(self):
        if self.job is not None and self.job.isRunning():
            self.job.stop = True; self.job.wait(8000)

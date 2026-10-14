# Stufe 3: Kapitel anlegen, Eintraege eingeben, Bilder (Datei oder Strg+V), Export.
import os
from PySide6.QtCore import Qt, Signal, QThread, QSize
from PySide6.QtGui import QPixmap, QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem,
                               QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QFileDialog,
                               QMessageBox, QApplication, QInputDialog, QDialog, QFormLayout, QDialogButtonBox, QSplitter,
                               QMenu, QProgressDialog)
import db, exporter, importer
from paths import p, ensure


class AudioJob(QThread):
    done = Signal(str); failed = Signal(str); prog = Signal(int, int)
    def __init__(self, conn_path, kid, path, speaker, voice, speed, hoer):
        super().__init__(); self.a = (conn_path, kid, path, speaker, voice, speed, hoer)
    def run(self):
        try:
            conn_path, kid, path, speaker, voice, speed, hoer = self.a
            c = db.connect(conn_path)      # eigene Verbindung fuer den Thread
            k = c.execute("SELECT * FROM kapitel WHERE id=?", (kid,)).fetchone()
            exporter.export_audio(c, k, path, speaker, voice, speed, hoer, lambda i, n: self.prog.emit(i, n))
            c.close(); self.done.emit(path)
        except Exception as ex:
            self.failed.emit(str(ex))


class EntryDialog(QDialog):
    """Neuer oder bestehender Eintrag. Doppelte Saetze werden beim Speichern gemeldet."""
    def __init__(self, parent, e=None):
        super().__init__(parent); self.setWindowTitle("Eintrag bearbeiten" if e else "Neuer Eintrag"); self.setMinimumWidth(620)
        f = QFormLayout(self)
        self.en, self.de, self.au, self.ben, self.bde = (QLineEdit() for _ in range(5))
        self.en.setPlaceholderText("z. B. I would like a coffee, please.")
        self.de.setPlaceholderText("deutsche Übersetzung"); self.au.setPlaceholderText("Aussprache-Hilfe (freiwillig)")
        for lab, w in (("Englisch", self.en), ("Deutsch", self.de), ("Aussprache", self.au),
                       ("Beispielsatz Englisch", self.ben), ("Beispielsatz Deutsch", self.bde)):
            f.addRow(lab, w)
        if e:
            self.en.setText(e["englisch"]); self.de.setText(e["deutsch"]); self.au.setText(e["aussprache"])
            self.ben.setText(e["beispiel_en"]); self.bde.setText(e["beispiel_de"])
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel); bb.accepted.connect(self._ok); bb.rejected.connect(self.reject)
        f.addRow(bb)

    def _ok(self):
        if not self.en.text().strip() or not self.de.text().strip():
            QMessageBox.warning(self, "Eintrag", "Bitte Englisch und Deutsch ausfüllen."); return
        self.accept()

    def values(self):
        return [w.text().strip() for w in (self.en, self.de, self.au, self.ben, self.bde)]


class ImageView(QDialog):
    def __init__(self, parent, path, text):
        super().__init__(parent); self.setWindowTitle(text or "Bild"); v = QVBoxLayout(self)
        l = QLabel(); pm = QPixmap(path)
        l.setPixmap(pm.scaled(900, 650, Qt.KeepAspectRatio, Qt.SmoothTransformation)); v.addWidget(l)


class EditorPage(QWidget):
    changed = Signal()          # Daten wurden geaendert (Vorlesen/Abfrage neu laden)
    open_chapter = Signal(int)

    def __init__(self, conn, speaker, voice_fn, status):
        super().__init__()
        self.conn, self.speaker, self.voice_fn, self.status = conn, speaker, voice_fn, status
        self.kid = None; self.job = None
        root = QVBoxLayout(self); root.setContentsMargins(24, 20, 24, 16)
        t = QLabel("Kapitel"); t.setObjectName("title"); root.addWidget(t)
        s = QLabel("Links ein Kapitel wählen. Rechts Einträge und Bilder bearbeiten. Doppelklick auf einen Eintrag ändert ihn.")
        s.setObjectName("muted"); s.setWordWrap(True); root.addWidget(s)
        body = QHBoxLayout(); root.addLayout(body, 1)
        # links: Kapitelliste
        left = QVBoxLayout(); body.addLayout(left, 2)
        self.klist = QListWidget(); self.klist.currentRowChanged.connect(self._select); left.addWidget(self.klist, 1)
        for text, fn in (("➕ Neues Kapitel", self.new_chapter), ("📥 Kapitel aus Excel", self.import_xlsx), ("📄 Excel-Vorlage öffnen", self.open_template), ("✏️ Umbenennen", self.rename_chapter),
                         ("🔊 Im Vorlesen öffnen", self.to_listen), ("🗑 Kapitel löschen", self.del_chapter)):
            b = QPushButton(text); b.clicked.connect(fn); left.addWidget(b)
        # rechts
        right = QVBoxLayout(); body.addLayout(right, 5)
        self.head = QLabel(""); self.head.setObjectName("title2"); right.addWidget(self.head)
        self.tab = QTableWidget(0, 3); self.tab.setHorizontalHeaderLabels(["Englisch", "Deutsch", "Beispielsatz"])
        self.tab.setEditTriggers(QAbstractItemView.NoEditTriggers); self.tab.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tab.setSelectionMode(QAbstractItemView.SingleSelection); self.tab.verticalHeader().hide()
        for c in range(3):
            self.tab.horizontalHeader().setSectionResizeMode(c, QHeaderView.Stretch)
        self.tab.setWordWrap(True); self.tab.cellDoubleClicked.connect(lambda r, c: self.edit_entry())
        right.addWidget(self.tab, 3)
        r1 = QHBoxLayout(); right.addLayout(r1)
        for text, fn in (("➕ Neuer Eintrag", self.add_entry), ("✏️ Ändern", self.edit_entry), ("🗑 Eintrag löschen", self.del_entry)):
            b = QPushButton(text); b.clicked.connect(fn); r1.addWidget(b)
        r1.addStretch(1)
        il = QLabel("Bilder und Screenshots"); il.setObjectName("title2"); right.addWidget(il)
        self.imgs = QListWidget(); self.imgs.setViewMode(QListWidget.IconMode); self.imgs.setIconSize(QSize(120, 90))
        self.imgs.setResizeMode(QListWidget.Adjust); self.imgs.setMovement(QListWidget.Static); self.imgs.setFixedHeight(130)
        self.imgs.itemDoubleClicked.connect(self.show_image); right.addWidget(self.imgs)
        r2 = QHBoxLayout(); right.addLayout(r2)
        for text, fn in (("🖼 Bild aus Datei", self.add_image), ("📋 Aus Zwischenablage (Strg+V)", self.paste_image),
                         ("📝 Beschriftung", self.caption_image), ("🗑 Bild löschen", self.del_image)):
            b = QPushButton(text); b.clicked.connect(fn); r2.addWidget(b)
        r2.addStretch(1)
        r3 = QHBoxLayout(); right.addLayout(r3)
        el = QLabel("Exportieren:"); r3.addWidget(el)
        for text, fn in (("🎧 MP3", self.exp_mp3), ("📄 PDF", self.exp_pdf), ("📊 Excel", self.exp_xlsx), ("📝 TXT", self.exp_txt)):
            b = QPushButton(text); b.clicked.connect(fn); r3.addWidget(b)
        r3.addStretch(1)
        QShortcut(QKeySequence.Paste, self, activated=self._paste_shortcut)
        self.reload()

    # ---- Hilfen
    def k(self):
        return self.conn.execute("SELECT * FROM kapitel WHERE id=?", (self.kid,)).fetchone() if self.kid else None

    def _need(self):
        k = self.k()
        if not k:
            QMessageBox.information(self, "Kapitel", "Bitte zuerst links ein Kapitel wählen oder ein neues anlegen.")
        return k

    def reload(self, select_id=None):
        self.klist.blockSignals(True); self.klist.clear(); sel = 0
        for i, k in enumerate(db.chapters(self.conn)):
            it = QListWidgetItem("%d  %s  (%d)" % (k["nr"], k["titel"], k["anzahl"])); it.setData(Qt.UserRole, k["id"]); self.klist.addItem(it)
            if k["id"] == (select_id or self.kid):
                sel = i
        self.klist.blockSignals(False)
        if self.klist.count():
            self.klist.setCurrentRow(sel); self._select(sel)
        else:
            self.kid = None; self._fill()

    def _select(self, row):
        it = self.klist.item(row)
        self.kid = it.data(Qt.UserRole) if it else None
        self._fill()

    def _fill(self):
        k = self.k(); self.tab.setRowCount(0); self.imgs.clear()
        self.head.setText(("Kapitel %d: %s" % (k["nr"], k["titel"])) if k else "Kein Kapitel gewählt")
        if not k:
            return
        es = db.entries(self.conn, self.kid); self.tab.setRowCount(len(es))
        for r, e in enumerate(es):
            for c, v in enumerate((e["englisch"], e["deutsch"], e["beispiel_en"])):
                it = QTableWidgetItem(v); it.setData(Qt.UserRole, e["id"]); self.tab.setItem(r, c, it)
        self.tab.resizeRowsToContents()
        for b in db.images(self.conn, self.kid):
            f = os.path.join(ensure("bilder"), b["dateiname"])
            it = QListWidgetItem(QIcon(QPixmap(f)), b["beschreibung"] or "Bild"); it.setData(Qt.UserRole, b["id"]); it.setData(Qt.UserRole + 1, f)
            self.imgs.addItem(it)

    def _changed(self):
        sel = self.kid; self.reload(sel); self.changed.emit()

    def refresh(self):
        self.reload()

    # ---- Kapitel
    def new_chapter(self):
        titel, ok = QInputDialog.getText(self, "Neues Kapitel", "Titel des Kapitels:")
        if ok and titel.strip():
            kid, nr = db.new_chapter(self.conn, titel); self.reload(kid); self.changed.emit()
            self.status("Kapitel %d angelegt." % nr)

    def open_template(self):
        f = p("daten", "Kapitel_Vorlage.xlsx")
        if not os.path.exists(f):
            QMessageBox.warning(self, "Vorlage", "Die Datei fehlt:\n" + f); return
        try:
            os.startfile(f)
        except Exception:
            QMessageBox.information(self, "Vorlage", "Die Vorlage liegt hier:\n" + f)

    def import_xlsx(self):
        path, _ = QFileDialog.getOpenFileName(self, "Ausgefüllte Kapitel-Vorlage wählen", p("daten"), "Excel (*.xlsx)")
        if not path: return
        try:
            res = importer.import_chapter_xlsx(self.conn, path)
        except Exception as ex:
            QMessageBox.critical(self, "Import", "Die Datei konnte nicht gelesen werden:\n%s" % ex); return
        if not res:
            QMessageBox.information(self, "Import", "Es wurde nichts gefunden.\nIn der Vorlage muss in Zelle B1 ein Titel stehen und ab Zeile 5 mindestens ein Eintrag."); return
        z = []
        for titel, nr, neu, dups, fehl in res:
            z.append(("Kapitel %d „%s“: %d neu" % (nr, titel, neu)) if nr else ("„%s“: nichts übernommen" % titel))
            if dups: z.append("   Schon vorhanden, übersprungen (%d): %s%s" % (len(dups), "; ".join(dups[:5]), " …" if len(dups) > 5 else ""))
            if fehl: z.append("   Unvollständig, übersprungen: " + "; ".join(fehl[:5]))
        self.reload(); self.changed.emit(); QMessageBox.information(self, "Import", "\n".join(z))

    def rename_chapter(self):
        k = self._need()
        if not k: return
        titel, ok = QInputDialog.getText(self, "Kapitel umbenennen", "Neuer Titel:", text=k["titel"])
        if ok and titel.strip():
            db.update_chapter(self.conn, k["id"], titel, k["hinweis"] or ""); self._changed()

    def del_chapter(self):
        k = self._need()
        if not k: return
        n = self.conn.execute("SELECT COUNT(*) FROM eintrag WHERE kapitel_id=?", (k["id"],)).fetchone()[0]
        if QMessageBox.question(self, "Kapitel löschen", "Kapitel %d „%s“ mit %d Einträgen und allen Bildern wirklich löschen?\n(Tipp: vorher in den Einstellungen eine Sicherung machen.)"
                                % (k["nr"], k["titel"], n), QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            self.kid = None; db.delete_chapter(self.conn, k["id"]); self.reload(); self.changed.emit()

    def to_listen(self):
        k = self._need()
        if k: self.open_chapter.emit(k["nr"])

    # ---- Eintraege
    def _cur_entry(self):
        r = self.tab.currentRow()
        if r < 0: return None
        return self.conn.execute("SELECT * FROM eintrag WHERE id=?", (self.tab.item(r, 0).data(Qt.UserRole),)).fetchone()

    def _dup_msg(self, dup):
        QMessageBox.warning(self, "Satz gibt es schon", "Diesen Satz gibt es schon in Kapitel %d:\n„%s“\nEr wird nicht doppelt gespeichert." % dup)

    def add_entry(self):
        k = self._need()
        if not k: return
        d = EntryDialog(self)
        while d.exec() == QDialog.Accepted:
            en, de, au, ben, bde = d.values()
            eid, dup = db.add_new_entry(self.conn, k["id"], en, de, au, ben, bde)
            if dup:
                self._dup_msg(dup); continue
            self._changed(); self.status("Eintrag gespeichert."); break

    def edit_entry(self):
        e = self._cur_entry()
        if not e:
            QMessageBox.information(self, "Eintrag", "Bitte zuerst einen Eintrag in der Liste anklicken."); return
        d = EntryDialog(self, e)
        while d.exec() == QDialog.Accepted:
            dup = db.update_entry(self.conn, e["id"], *d.values())
            if dup:
                self._dup_msg(dup); continue
            self._changed(); break

    def del_entry(self):
        e = self._cur_entry()
        if e and QMessageBox.question(self, "Eintrag löschen", "„%s“ löschen?\n(Der Lernstand dazu geht verloren.)" % e["englisch"],
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            db.delete_entry(self.conn, e["id"]); self._changed()

    # ---- Bilder
    def add_image(self):
        k = self._need()
        if not k: return
        files, _ = QFileDialog.getOpenFileNames(self, "Bilder wählen", "", "Bilder (*.png *.jpg *.jpeg *.bmp *.gif)")
        for f in files:
            db.add_image_file(self.conn, k["id"], f)
        if files: self._fill(); self.status("%d Bild(er) hinzugefügt." % len(files))

    def paste_image(self):
        k = self._need()
        if not k: return
        pm = QApplication.clipboard().pixmap()
        if pm.isNull():
            QMessageBox.information(self, "Zwischenablage", "In der Zwischenablage ist kein Bild.\nTipp: Mit der Windows-Taste + Umschalt + S einen Bildschirmausschnitt aufnehmen, dann hier Strg+V."); return
        db.add_image_pixmap(self.conn, k["id"], pm); self._fill(); self.status("Bild aus der Zwischenablage eingefügt.")

    def _paste_shortcut(self):
        if self.isVisible() and not QApplication.clipboard().pixmap().isNull() and self.kid:
            self.paste_image()

    def _cur_img(self):
        it = self.imgs.currentItem()
        if not it:
            QMessageBox.information(self, "Bild", "Bitte zuerst ein Bild anklicken.")
        return it

    def show_image(self, it):
        ImageView(self, it.data(Qt.UserRole + 1), it.text()).exec()

    def caption_image(self):
        it = self._cur_img()
        if not it: return
        t, ok = QInputDialog.getText(self, "Beschriftung", "Text zum Bild:", text=it.text() if it.text() != "Bild" else "")
        if ok: db.set_image_text(self.conn, it.data(Qt.UserRole), t.strip()); self._fill()

    def del_image(self):
        it = self._cur_img()
        if it and QMessageBox.question(self, "Bild löschen", "Dieses Bild löschen?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            db.delete_image(self.conn, it.data(Qt.UserRole)); self._fill()

    # ---- Export
    def _ask(self, k, ext, title, filt):
        ziel = ensure("export")
        path, _ = QFileDialog.getSaveFileName(self, title, os.path.join(ziel, exporter.default_name(k, ext)), filt)
        return path

    def _run(self, fn, k, ext, title, filt):
        k = self._need() if k is None else k
        if not k: return
        path = self._ask(k, ext, title, filt)
        if not path: return
        try:
            fn(self.conn, k, path)
        except Exception as ex:
            QMessageBox.critical(self, "Export", "Das hat nicht geklappt:\n%s" % ex); return
        self.status("Gespeichert: " + path)
        QMessageBox.information(self, "Export", "Fertig. Gespeichert unter:\n%s" % path)

    def exp_txt(self):  self._run(exporter.export_txt, self.k(), "txt", "Als Text speichern", "Text (*.txt)")
    def exp_xlsx(self): self._run(exporter.export_xlsx, self.k(), "xlsx", "Als Excel speichern", "Excel (*.xlsx)")
    def exp_pdf(self):  self._run(exporter.export_pdf, self.k(), "pdf", "Als PDF speichern", "PDF (*.pdf)")

    def exp_mp3(self):
        k = self._need()
        if not k: return
        n = self.conn.execute("SELECT COUNT(*) FROM eintrag WHERE kapitel_id=?", (k["id"],)).fetchone()[0]
        if not n:
            QMessageBox.information(self, "MP3", "Das Kapitel hat noch keine Einträge."); return
        path = self._ask(k, "mp3", "Als MP3 speichern", "MP3 (*.mp3);;WAV (*.wav)")
        if not path: return
        voice, speed, hoer = self.voice_fn()
        self.pd = QProgressDialog("Die MP3 wird erzeugt …", None, 0, n, self); self.pd.setWindowModality(Qt.WindowModal); self.pd.setMinimumDuration(0); self.pd.setValue(0)
        self.job = AudioJob(db.db_path(), k["id"], path, self.speaker, voice, speed, hoer)
        self.job.prog.connect(lambda i, m: self.pd.setValue(i))
        self.job.done.connect(self._audio_done); self.job.failed.connect(self._audio_fail); self.job.start()

    def _audio_done(self, path):
        self.pd.close(); self.status("Gespeichert: " + path)
        QMessageBox.information(self, "MP3", "Fertig. Gespeichert unter:\n%s" % path)

    def _audio_fail(self, msg):
        self.pd.close(); QMessageBox.critical(self, "MP3", "Das hat nicht geklappt:\n%s" % msg)

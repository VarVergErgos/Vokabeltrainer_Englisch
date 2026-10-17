# Vokabeltrainer Englisch B1 - Hauptprogramm (Stufe 1: Vorlesen, Kapitelliste, Einstellungen, Import, Sicherung)
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QApplication, QWidget, QMainWindow, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
                               QStackedWidget, QButtonGroup, QComboBox, QScrollArea, QFrame, QSlider, QCheckBox,
                               QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox, QAbstractItemView, QInputDialog)
import db, importer, speech, quiz, editor, helptext, sprachdusche, sd_import, search, mp3export, lizenzen, grammatik
from paths import p

THEMES = {
    "hell": dict(bg="#eef1f4", surface="#ffffff", ink="#16212b", muted="#566574", line="#d9e0e7",
                 accent="#0b7a75", accentink="#ffffff", sel="#e0f1ef",
                 ok="#17803d", okbg="#e3f5e8", bad="#b3261e", badbg="#fde8e6", warn="#b45309"),
    "dunkel": dict(bg="#11171c", surface="#1a2229", ink="#e7edf2", muted="#98a7b4", line="#2a353e",
                   accent="#41c3ba", accentink="#04201e", sel="#18363a",
                   ok="#6fd48f", okbg="#15301f", bad="#ff8a80", badbg="#3b1b19", warn="#ffb36b"),
}

def qss(t, fs):
    return """
    QWidget{background:%(bg)s;color:%(ink)s}
    QLabel{background:transparent}
    #main,#page,#scrollbody{background:%(surface)s}
    #side{background:%(bg)s;border-right:1px solid %(line)s}
    QPushButton#nav{text-align:left;padding:10px 12px;border:0;border-radius:8px;background:transparent}
    QPushButton#nav:hover{background:%(sel)s}
    QPushButton#nav:checked{background:%(accent)s;color:%(accentink)s;font-weight:bold}
    QFrame#row{background:%(surface)s;border:1px solid %(line)s;border-radius:10px}
    QFrame#row[cur="true"]{background:%(sel)s;border:1px solid %(accent)s}
    QFrame#row QLabel{background:transparent}
    QPushButton#play{background:%(accent)s;color:%(accentink)s;border:0;border-radius:22px;min-width:44px;max-width:44px;min-height:44px;max-height:44px}
    QPushButton#btn{background:%(surface)s;border:1px solid %(line)s;border-radius:8px;padding:9px 16px;font-weight:bold}
    QPushButton#btn:hover{border-color:%(accent)s}
    QPushButton#pri{background:%(accent)s;color:%(accentink)s;border:1px solid %(accent)s;border-radius:8px;padding:9px 16px;font-weight:bold}
    QFrame#player{background:%(bg)s;border:1px solid %(line)s;border-radius:10px}
    QFrame#player QLabel,QFrame#player QCheckBox{background:transparent}
    QComboBox{background:%(surface)s;border:1px solid %(line)s;border-radius:8px;padding:6px 10px}
    QComboBox QAbstractItemView{background:%(surface)s;color:%(ink)s;selection-background-color:%(sel)s;selection-color:%(ink)s}
    QScrollArea{border:0;background:%(surface)s}
    QSlider::groove:horizontal{height:6px;background:%(line)s;border-radius:3px}
    QSlider::handle:horizontal{background:%(accent)s;width:18px;margin:-6px 0;border-radius:9px}
    QSlider::sub-page:horizontal{background:%(accent)s;border-radius:3px}
    QTableWidget{background:%(surface)s;gridline-color:%(line)s;border:1px solid %(line)s;border-radius:8px}
    QHeaderView::section{background:%(bg)s;color:%(muted)s;border:0;border-bottom:1px solid %(line)s;padding:6px}
    QTableWidget::item:selected{background:%(sel)s;color:%(ink)s}
    QCheckBox::indicator{width:20px;height:20px}
    QPushButton#pill{background:%(surface)s;border:1px solid %(line)s;border-radius:16px;padding:7px 18px;font-weight:bold}
    QPushButton#pill:checked{background:%(accent)s;color:%(accentink)s;border-color:%(accent)s;font-weight:bold}
    QPushButton#ok{background:%(okbg)s;color:%(ok)s;border:1px solid %(ok)s;border-radius:8px;padding:11px 18px;font-weight:bold}
    QPushButton#bad{background:%(badbg)s;color:%(bad)s;border:1px solid %(bad)s;border-radius:8px;padding:11px 18px;font-weight:bold}
    QFrame#card{background:%(surface)s;border:1px solid %(line)s;border-radius:14px}
    QFrame#card QLabel{background:transparent}
    QFrame#kpi{background:%(surface)s;border:1px solid %(line)s;border-radius:10px}
    QFrame#kpi QLabel{background:transparent}
    #kpival{font-size:%(h)dpt;font-weight:bold}
    #prompt{font-size:%(h)dpt;font-weight:bold}
    #answer{font-size:%(a)dpt;font-weight:bold;color:%(accent)s}
    QLineEdit{background:%(surface)s;border:1px solid %(line)s;border-radius:8px;padding:8px 10px}
    QProgressBar{background:%(line)s;border:0;border-radius:5px}
    QProgressBar::chunk{background:%(accent)s;border-radius:5px}
    #chip{background:%(sel)s;border:1px solid %(line)s;border-radius:11px;padding:2px 10px}
    #statusbar{background:%(bg)s;border-top:1px solid %(line)s;color:%(muted)s}
    #muted{color:%(muted)s}
    #title{font-size:%(h)dpt;font-weight:bold}
    #title2{font-size:%(h2)dpt;font-weight:bold;margin-top:6px}
    """ % dict(t, h=int(fs * 1.45), a=int(fs * 1.25), h2=int(fs * 1.15))


class SynthJob(QThread):
    done = Signal(list)
    failed = Signal(str)

    def __init__(self, speaker, texts, voice, speed, hoer):
        super().__init__()
        self.sp, self.texts, self.voice, self.speed, self.hoer = speaker, texts, voice, speed, hoer

    def run(self):
        try:
            self.done.emit([speech.wav_for_safe(self.sp, t, self.voice, self.speed, self.hoer) for t in self.texts])
        except Exception as e:           # Fehler als Text melden, Programm bleibt offen
            self.failed.emit(str(e))


class Row(QFrame):
    def __init__(self, e, on_play):
        e = dict(e)
        super().__init__()
        self.setObjectName("row"); self.setProperty("cur", False)
        lay = QHBoxLayout(self); lay.setContentsMargins(12, 10, 12, 10); lay.setSpacing(12)
        self.btn = QPushButton("▶"); self.btn.setObjectName("play"); self.btn.setAccessibleName("Vorlesen")
        self.btn.clicked.connect(on_play)
        lay.addWidget(self.btn, 0, Qt.AlignTop)
        col = QVBoxLayout(); col.setSpacing(2)
        if e.get("sprecher"):
            sp = QLabel(e["sprecher"]); sp.setObjectName("muted"); col.addWidget(sp)
        en = QLabel(e["englisch"]); en.setWordWrap(True); f = en.font(); f.setBold(True); en.setFont(f)
        col.addWidget(en)
        if e["aussprache"]:
            pr = QLabel(e["aussprache"]); pr.setObjectName("muted"); f = pr.font(); f.setItalic(True); pr.setFont(f)
            col.addWidget(pr)
        de = QLabel(e["deutsch"] or "(keine deutsche Übersetzung im Buch)"); de.setObjectName("muted"); de.setWordWrap(True); col.addWidget(de)
        if e["beispiel_en"]:
            ex = QLabel("%s<br><span style='color:gray'>%s</span>" % (e["beispiel_en"], e["beispiel_de"]))
            ex.setWordWrap(True); col.addWidget(ex)
        lay.addLayout(col, 1)

    def mark(self, on):
        self.setProperty("cur", on)
        self.btn.setText("■" if on else "▶")
        self.style().unpolish(self); self.style().polish(self)


class ListenPage(QWidget):
    def __init__(self, conn, speaker, status, scope=db.EIGEN):
        super().__init__()
        self.scope = scope
        self.conn, self.speaker, self.status = conn, speaker, status
        self.rows, self.ents, self.queue, self.session, self.job = [], [], [], 0, None
        v = QVBoxLayout(self); v.setContentsMargins(24, 20, 24, 16)
        self.title = QLabel("Vorlesen"); self.title.setObjectName("title"); v.addWidget(self.title)
        self.sub = QLabel(""); self.sub.setObjectName("muted"); self.sub.setWordWrap(True); v.addWidget(self.sub)
        top = QHBoxLayout(); top.addWidget(QLabel("Kapitel"))
        self.combo = QComboBox(); self.combo.setMinimumWidth(320); top.addWidget(self.combo)
        self.count = QLabel(""); self.count.setObjectName("chip"); top.addWidget(self.count); top.addStretch(1)
        v.addLayout(top)
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.body = QWidget(); self.body.setObjectName("scrollbody"); self.bl = QVBoxLayout(self.body)
        self.bl.setSpacing(8); self.bl.addStretch(1); self.scroll.setWidget(self.body); v.addWidget(self.scroll, 1)
        pl = QFrame(); pl.setObjectName("player"); h = QHBoxLayout(pl); h.setContentsMargins(14, 10, 14, 10); h.setSpacing(18)
        self.allbtn = QPushButton("▶ Alle vorlesen"); self.allbtn.setObjectName("pri"); self.allbtn.clicked.connect(self.play_all)
        h.addWidget(self.allbtn)
        c = QVBoxLayout(); self.tl = QLabel(); c.addWidget(self.tl)
        self.tempo = QSlider(Qt.Horizontal); self.tempo.setRange(60, 120); self.tempo.setValue(80); self.tempo.setMinimumWidth(150)
        self.tempo.valueChanged.connect(self._tempo); c.addWidget(self.tempo); h.addLayout(c)
        c = QVBoxLayout(); c.addWidget(QLabel("Stimme")); self.voice = QComboBox(); self.voice.addItems(list(speech.VOICES))
        c.addWidget(self.voice); h.addLayout(c)
        self.hoer = QCheckBox("Hörhilfe (Höhen anheben)"); self.hoer.setChecked(True); h.addWidget(self.hoer)
        h.addStretch(1); v.addWidget(pl)
        self._tempo()
        self.reload_chapters()
        self.combo.currentIndexChanged.connect(self.load)
        self.load()

    def _tempo(self):
        self.tl.setText("Tempo %s×" % ("%.2f" % (self.tempo.value() / 100.0)).replace(".", ","))

    def reload_chapters(self, select_nr=None):
        self.combo.blockSignals(True); self.combo.clear()
        for k in db.chapters(self.conn, self.scope):
            self.combo.addItem(db.chapter_label(k), k["id"])
        if select_nr is not None:
            i = self.combo.findText(str(select_nr) + "  ", Qt.MatchStartsWith)
            if i >= 0:
                self.combo.setCurrentIndex(i)
        self.combo.blockSignals(False)

    def load(self):
        self.stop()
        while self.bl.count() > 1:
            w = self.bl.takeAt(0).widget()
            if w: w.deleteLater()
        self.rows = []
        kid = self.combo.currentData()
        if kid is None:
            self.sub.setText("Noch keine Kapitel. Lege unter Kapitel ein neues Kapitel an oder lies eine ausgefüllte Excel-Vorlage ein (Kapitel > Kapitel aus Excel)."); self.count.setText("0 Einträge")
            return
        k = self.conn.execute("SELECT * FROM kapitel WHERE id=?", (kid,)).fetchone()
        self.sub.setText(("Kapitel %d · %s%s" % (k["nr"], k["titel"], (" · " + k["hinweis"]) if k["hinweis"] else "")) if self.scope.bereich == "eigen"
                         else "%s · %s%s" % (k["buch"], k["titel"], (" · " + k["hinweis"]) if k["hinweis"] else ""))
        self.ents = db.entries(self.conn, kid, self.scope.rubrik)
        self.count.setText("%d Einträge" % len(self.ents))
        for i, e in enumerate(self.ents):
            r = Row(e, lambda _=False, i=i: self.toggle(i)); self.rows.append(r); self.bl.insertWidget(self.bl.count() - 1, r)

    # ---- Abspielen
    def toggle(self, i):
        if self.queue_active and self.current == i:
            self.stop()
        else:
            self.start([i])

    queue_active = False
    current = -1

    def play_all(self):
        if self.queue_active:
            self.stop(); return
        self.start(list(range(len(self.ents))))

    def start(self, idx):
        if not speech.voice_ok(speech.VOICES[self.voice.currentText()]):
            QMessageBox.information(self, "Stimme fehlt", "Die Stimme ist noch nicht installiert.\nBitte setup.bat ausführen."); return
        self.stop(); self.queue = idx; self.queue_active = True; self.allbtn.setText("■ Stopp"); self._next()

    def stop(self):
        self.session += 1; self.queue = []; self.queue_active = False
        speech.stop_play()
        for r in self.rows: r.mark(False)
        self.current = -1; self.allbtn.setText("▶ Alle vorlesen")

    def _next(self):
        if not self.queue:
            self.stop(); return
        i = self.queue.pop(0); e = self.ents[i]
        for r in self.rows: r.mark(False)
        self.rows[i].mark(True); self.current = i
        self.scroll.ensureWidgetVisible(self.rows[i])
        texts = [e["englisch"]] + ([e["beispiel_en"]] if e["beispiel_en"] else [])
        s = self.session
        self.status("Wird vorbereitet ...")
        self.job = SynthJob(self.speaker, texts, self.voice.currentText(), self.tempo.value() / 100.0, self.hoer.isChecked())
        self.job.done.connect(lambda paths, s=s: self._play(paths, s)); self.job.failed.connect(self._fail)
        self.job.start()

    def _fail(self, msg):
        self.stop(); self.status("Fehler beim Sprechen: " + msg)
        QMessageBox.warning(self, "Sprachausgabe", "Das Vorlesen hat nicht geklappt:\n" + msg)

    def _play(self, paths, s, k=0):
        if s != self.session:
            return
        if k >= len(paths):
            QTimer.singleShot(500, lambda: self._next() if s == self.session else None); return
        self.status("Spielt ...")
        speech.play_async(paths[k])
        QTimer.singleShot(int((speech.wav_seconds(paths[k]) + 0.5) * 1000), lambda: self._play(paths, s, k + 1))


class ChaptersPage(QWidget):
    open_chapter = Signal(int)

    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        v = QVBoxLayout(self); v.setContentsMargins(24, 20, 24, 16)
        t = QLabel("Kapitel"); t.setObjectName("title"); v.addWidget(t)
        s = QLabel("Doppelklick auf ein Kapitel öffnet es im Bereich Vorlesen."); s.setObjectName("muted"); v.addWidget(s)
        self.tab = QTableWidget(0, 5); self.tab.setHorizontalHeaderLabels(["Nr.", "Titel", "Worum geht es", "Einträge", "Datum"])
        self.tab.setEditTriggers(QAbstractItemView.NoEditTriggers); self.tab.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tab.verticalHeader().hide(); self.tab.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tab.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tab.cellDoubleClicked.connect(lambda r, c: self.open_chapter.emit(int(self.tab.item(r, 0).text())))
        v.addWidget(self.tab, 1); self.refresh()

    def refresh(self):
        ks = db.chapters(self.conn); self.tab.setRowCount(len(ks))
        for r, k in enumerate(ks):
            for c, val in enumerate([k["nr"], k["titel"], k["hinweis"] or "", k["anzahl"], k["datum"] or ""]):
                it = QTableWidgetItem(str(val)); self.tab.setItem(r, c, it)
        self.tab.resizeRowsToContents()


class Placeholder(QWidget):
    def __init__(self, title, text):
        super().__init__()
        v = QVBoxLayout(self); v.setContentsMargins(24, 20, 24, 16)
        t = QLabel(title); t.setObjectName("title"); v.addWidget(t)
        s = QLabel(text); s.setObjectName("muted"); s.setWordWrap(True); v.addWidget(s); v.addStretch(1)


class HelpPage(QWidget):
    def __init__(self):
        super().__init__()
        from PySide6.QtWidgets import QTextBrowser
        v = QVBoxLayout(self); v.setContentsMargins(24, 20, 24, 16)
        h = QHBoxLayout(); t = QLabel("Hilfe"); t.setObjectName("title"); h.addWidget(t); h.addStretch(1)
        b = QPushButton("📄 Anleitung als Word öffnen"); b.clicked.connect(self.open_docx); h.addWidget(b); v.addLayout(h)
        self.view = QTextBrowser(); self.view.setOpenLinks(False); self.view.anchorClicked.connect(lambda u: self.view.scrollToAnchor(u.fragment()))
        self.view.setHtml(helptext.html()); v.addWidget(self.view, 1)

    def open_docx(self):
        f = p("docs", "Bedienungsanleitung_Vokabeltrainer.docx")
        try:
            os.startfile(f)
        except Exception:
            QMessageBox.information(self, "Hilfe", "Die Word-Datei liegt hier:\n" + f)


class InfoPage(QWidget):
    def __init__(self):
        super().__init__()
        from PySide6.QtWidgets import QTextBrowser
        v = QVBoxLayout(self); v.setContentsMargins(24, 20, 24, 16)
        t = QLabel("Info & Lizenzen"); t.setObjectName("title"); v.addWidget(t)
        self.view = QTextBrowser(); self.view.setHtml(lizenzen.html()); v.addWidget(self.view, 1)


class SettingsPage(QWidget):
    changed = Signal()
    users_changed = Signal()

    def __init__(self, conn, on_import):
        super().__init__()
        self.conn = conn
        v = QVBoxLayout(self); v.setContentsMargins(24, 20, 24, 16); v.setSpacing(14)
        t = QLabel("Einstellungen"); t.setObjectName("title"); v.addWidget(t)
        h = QHBoxLayout(); h.addWidget(QLabel("Schriftgröße"))
        self.fs = QSlider(Qt.Horizontal); self.fs.setRange(11, 24); self.fs.setValue(int(db.get_setting(conn, "schrift", 14)))
        self.fs.setMinimumWidth(240); h.addWidget(self.fs); self.fsl = QLabel(); h.addWidget(self.fsl); h.addStretch(1); v.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("Darstellung")); self.th = QComboBox(); self.th.addItems(["Automatisch", "Hell", "Dunkel"])
        self.th.setCurrentIndex(["auto", "hell", "dunkel"].index(db.get_setting(conn, "theme", "auto"))); h.addWidget(self.th); h.addStretch(1); v.addLayout(h)
        h = QHBoxLayout()
        b = QPushButton("Sicherung mit Datum"); b.setObjectName("btn"); b.clicked.connect(self.sichern); h.addWidget(b)
        b = QPushButton("Excel importieren …"); b.setObjectName("btn"); b.clicked.connect(on_import); h.addWidget(b); h.addStretch(1); v.addLayout(h)
        ul = QLabel("Benutzer (der Lernstand ist für alle gemeinsam)"); ul.setObjectName("muted"); v.addWidget(ul)
        h = QHBoxLayout()
        for text, fn in (("Benutzer anlegen …", self.user_add), ("Umbenennen …", self.user_rename), ("Löschen …", self.user_del)):
            b = QPushButton(text); b.setObjectName("btn"); b.clicked.connect(fn); h.addWidget(b)
        h.addStretch(1); v.addLayout(h)
        self.info = QLabel("Datenbank: " + db.db_path()); self.info.setObjectName("muted"); self.info.setWordWrap(True); v.addWidget(self.info)
        v.addStretch(1)
        self.fs.valueChanged.connect(self._save); self.th.currentIndexChanged.connect(self._save); self._lbl()

    def _lbl(self):
        self.fsl.setText("%d pt" % self.fs.value())

    def _save(self):
        self._lbl()
        db.set_setting(self.conn, "schrift", self.fs.value())
        db.set_setting(self.conn, "theme", ["auto", "hell", "dunkel"][self.th.currentIndex()])
        self.changed.emit()

    current_user = lambda self: self.window().user.currentText() if hasattr(self.window(), "user") else ""

    def user_add(self):
        n, ok = QInputDialog.getText(self, "Benutzer anlegen", "Name des neuen Benutzers:")
        if ok:
            if db.add_user(self.conn, n):
                self.info.setText("Benutzer angelegt: " + n.strip()); self.users_changed.emit()
            else:
                QMessageBox.information(self, "Benutzer", "Der Name ist leer oder gibt es schon.")

    def user_rename(self):
        old = self.current_user()
        n, ok = QInputDialog.getText(self, "Umbenennen", "Neuer Name für %s:" % old, text=old)
        if ok and old:
            if db.rename_user(self.conn, old, n):
                self.info.setText("Umbenannt: %s → %s" % (old, n.strip())); self.users_changed.emit(); self.window().select_user(n.strip())
            else:
                QMessageBox.information(self, "Benutzer", "Der Name ist leer oder gibt es schon.")

    def user_del(self):
        who = self.current_user()
        if QMessageBox.question(self, "Benutzer löschen", "Benutzer %s wirklich löschen?\n(Der gemeinsame Lernstand bleibt erhalten.)" % who) == QMessageBox.Yes:
            if db.delete_user(self.conn, who):
                self.info.setText("Gelöscht: " + who); self.users_changed.emit()
            else:
                QMessageBox.information(self, "Benutzer", "Der letzte Benutzer kann nicht gelöscht werden.")

    def sichern(self):
        ziel = db.backup(self.conn)
        self.info.setText("Sicherung gespeichert: " + ziel)


class MainWindow(QMainWindow):
    def __init__(self, conn):
        super().__init__()
        self.conn, self.speaker = conn, speech.Speaker()
        self.setWindowTitle("Vokabeltrainer Englisch B1"); self.resize(1100, 720)
        root = QWidget(); self.setCentralWidget(root); outer = QVBoxLayout(root); outer.setContentsMargins(0, 0, 0, 0); outer.setSpacing(0)
        body = QHBoxLayout(); body.setSpacing(0); outer.addLayout(body, 1)
        side = QFrame(); side.setObjectName("side"); side.setFixedWidth(210); sv = QVBoxLayout(side); sv.setContentsMargins(8, 12, 8, 10); sv.setSpacing(3)
        self.side = side; self.stack = QStackedWidget(); self.stack.setObjectName("main")
        self.status_lbl = QLabel(""); self.status_lbl.setObjectName("statusbar"); self.status_lbl.setContentsMargins(12, 5, 12, 5)
        self.listen = ListenPage(conn, self.speaker, self.set_status)
        self.chapters = editor.EditorPage(conn, self.speaker, lambda: (self.listen.voice.currentText(), self.listen.tempo.value() / 100.0, self.listen.hoer.isChecked()), self.set_status)
        self.chapters.changed.connect(self.data_changed)
        self.mp3 = mp3export.Mp3Page(conn, self.speaker, lambda: (self.listen.voice.currentText(), self.listen.tempo.value() / 100.0, self.listen.hoer.isChecked()), self.set_status)
        self.settings = SettingsPage(conn, self.do_import)
        self.quiz = quiz.QuizPage(conn, self.speak, lambda: self.user.currentText(), self.set_status)
        self.progress = quiz.ProgressPage(conn, self.bar_colors)
        self.gram = grammatik.GrammatikPage(self.set_status)
        self.help = HelpPage(); self.info = InfoPage()
        self.sd_scope = db.Scope("sd")
        self.sd_listen = ListenPage(conn, self.speaker, self.set_status, self.sd_scope)
        self.sd_quiz = quiz.QuizPage(conn, self.speak, lambda: self.user.currentText(), self.set_status, self.sd_scope)
        self.sd_progress = quiz.ProgressPage(conn, self.bar_colors, self.sd_scope)
        self.search = search.SearchPage(conn, self.speak); self.search.open_hit.connect(self.open_hit)
        self.sd = sprachdusche.SDPage(conn, self.sd_listen, self.sd_quiz, self.sd_progress, self.sd_scope)
        pages = [("🔊  Vorlesen", self.listen),
                 ("❓  Abfrage", self.quiz),
                 ("✏️  Kapitel", self.chapters),
                 ("🎧  MP3 erstellen", self.mp3),
                 ("📘  Grammatik und Zeiten", self.gram),
                 ("📚  Sprachduschen", self.sd),
                 ("🔎  Suchen", self.search),
                 ("📊  Fortschritt", self.progress),
                 ("⚙️  Einstellungen", self.settings),
                 ("📖  Hilfe", self.help),
                 ("ℹ️  Info && Lizenzen", self.info)]
        grp = QButtonGroup(self); grp.setExclusive(True); self.grp = grp
        for i, (name, page) in enumerate(pages):
            b = QPushButton(name); b.setObjectName("nav"); b.setCheckable(True); grp.addButton(b, i); sv.addWidget(b)
            self.stack.addWidget(page)
        grp.button(0).setChecked(True); grp.idClicked.connect(self.stack.setCurrentIndex)
        self.stack.currentChanged.connect(self.page_changed)
        sv.addStretch(1)
        ul = QLabel("Angemeldet als"); ul.setObjectName("muted"); sv.addWidget(ul)
        self.user = QComboBox(); sv.addWidget(self.user); self.reload_users()
        self.user.currentTextChanged.connect(lambda t: db.set_setting(self.conn, "letzter_benutzer", t) if t else None)
        ul = QLabel("Der Lernstand wird von allen gemeinsam genutzt."); ul.setObjectName("muted"); ul.setWordWrap(True); sv.addWidget(ul)
        body.addWidget(side); body.addWidget(self.stack, 1); outer.addWidget(self.status_lbl)
        self.chapters.open_chapter.connect(self.open_chapter)
        self.settings.changed.connect(self.apply_style); self.settings.users_changed.connect(self.reload_users)
        self.theme_name = 'hell'
        self.apply_style(); self.refresh_status()

    def closeEvent(self, ev):
        for j in (getattr(self, "speak_job", None), getattr(self.listen, "job", None), getattr(self.sd_listen, "job", None)):
            if j is not None and j.isRunning():
                j.wait(5000)
        self.mp3.stop_job()
        speech.stop_play(); super().closeEvent(ev)

    def page_changed(self, i):
        w = self.stack.widget(i)
        b = self.grp.button(i)
        if b is not None and not b.isChecked(): b.setChecked(True)
        if w is self.quiz:
            self.quiz.refresh()
        elif w is self.progress:
            self.progress.refresh()
        elif w is self.sd:
            self.sd.refresh()
        elif w is self.search:
            self.search.refresh()
        elif w is self.mp3:
            self.mp3.refresh()
        elif w is self.gram:
            self.gram.refresh()
        if w is not self.listen:
            self.listen.stop()
        if w is not self.sd:
            self.sd.stop()

    def bar_colors(self):
        mode = self.theme_name
        t = THEMES[mode]
        return (t["ok"], t["warn"], t["line"])

    def speak(self, text):
        """Einzelnen Text mit den Einstellungen aus dem Bereich Vorlesen sprechen (fuer die Abfrage)."""
        lp = self.listen if self.stack.currentWidget() is not self.sd else self.sd_listen
        if not speech.voice_ok(speech.VOICES[lp.voice.currentText()]):
            self.set_status("Die Stimme fehlt: bitte setup.bat ausführen."); return
        lp.stop(); self.speak_session = getattr(self, "speak_session", 0) + 1; s = self.speak_session
        job = SynthJob(self.speaker, [text], lp.voice.currentText(), lp.tempo.value() / 100.0, lp.hoer.isChecked())
        def play(paths):
            if s == self.speak_session:
                speech.stop_play(); speech.play_async(paths[0])
        job.done.connect(play); job.failed.connect(lambda m: self.set_status("Fehler beim Sprechen: " + m))
        self.speak_job = job; job.start()

    def reload_users(self):
        self.user.blockSignals(True); self.user.clear(); self.user.addItems(db.users(self.conn))
        last = db.get_setting(self.conn, "letzter_benutzer", "")
        i = self.user.findText(last)
        self.user.setCurrentIndex(i if i >= 0 else 0); self.user.blockSignals(False)
        db.set_setting(self.conn, "letzter_benutzer", self.user.currentText())

    def select_user(self, name):
        db.set_setting(self.conn, "letzter_benutzer", name); self.reload_users()

    def set_status(self, t):
        self.status_lbl.setText(t)

    def refresh_status(self):
        q = lambda sql: self.conn.execute(sql).fetchone()[0]
        n = q("SELECT COUNT(*) FROM eintrag e JOIN kapitel k ON k.id=e.kapitel_id WHERE COALESCE(k.bereich,'eigen')='eigen'")
        k = q("SELECT COUNT(*) FROM kapitel WHERE COALESCE(bereich,'eigen')='eigen'")
        sd = q("SELECT COUNT(*) FROM eintrag e JOIN kapitel k ON k.id=e.kapitel_id WHERE k.bereich='sd'")
        self.set_status("%s   ·   %d Einträge   ·   %d Kapitel%s" % (db.db_path(), n, k, ("   ·   Sprachduschen: %d Einträge" % sd) if sd else ""))

    def apply_style(self):
        fs = int(db.get_setting(self.conn, "schrift", 14)); mode = db.get_setting(self.conn, "theme", "auto")
        if mode == "auto":
            try:
                mode = "dunkel" if QApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark else "hell"
            except Exception:
                mode = "hell"
        self.theme_name = mode
        f = QFont("Segoe UI", fs); QApplication.instance().setFont(f)
        QApplication.instance().setStyleSheet(qss(THEMES[mode], fs))
        self.side.setFixedWidth(max(210, int(fs * 15)))

    def data_changed(self):
        self.listen.reload_chapters(); self.listen.load(); self.refresh_status()

    def open_hit(self, d):
        """Treffer der Suche im passenden Bereich oeffnen."""
        if d["bereich"] == "sd":
            self.sd.buch.setCurrentIndex(0); self.sd.rub.setCurrentIndex(0); self.sd._filter()
            lp = self.sd_listen; i = lp.combo.findData(d["kapitel_id"])
            if i >= 0: lp.combo.setCurrentIndex(i)
            lp.load(); self.stack.setCurrentWidget(self.sd); self.sd.grp.button(0).setChecked(True); self.sd._mode(0)
            self._mark(lp, d["id"])
        else:
            self.listen.reload_chapters(d["nr"]); self.listen.load(); self.stack.setCurrentWidget(self.listen); self._mark(self.listen, d["id"])

    def _mark(self, lp, eid):
        for i, e in enumerate(lp.ents):
            if e["id"] == eid and i < len(lp.rows):
                lp.scroll.ensureWidgetVisible(lp.rows[i]); lp.rows[i].setProperty("cur", True)
                lp.rows[i].style().unpolish(lp.rows[i]); lp.rows[i].style().polish(lp.rows[i]); break

    def open_chapter(self, nr):
        self.listen.reload_chapters(nr); self.listen.load(); self.stack.setCurrentIndex(0)

    def do_import(self):
        path, _ = QFileDialog.getOpenFileName(self, "Excel-Vokabeltrainer wählen", p("daten"), "Excel (*.xlsx)")
        if not path:
            return
        aud = p("daten", "Audiate_Saetze_Englisch_Deutsch.xlsx")
        neu, dop, kap = importer.import_xlsx(self.conn, path, aud if os.path.exists(aud) else None)
        self.listen.reload_chapters(); self.listen.load(); self.chapters.refresh(); self.refresh_status()
        QMessageBox.information(self, "Import", "%d neue Einträge, %d doppelte übersprungen (%d Kapitel)." % (neu, dop, kap))


def first_start_import(conn):
    if os.path.exists(sd_import.json_path()) and not sd_import.has_data(conn):
        sd_import.import_sd(conn)
    if conn.execute("SELECT COUNT(*) FROM kapitel WHERE COALESCE(bereich,'eigen')='eigen'").fetchone()[0] == 0:
        x = p("daten", "Vokabeltrainer_Englisch_B1.xlsx")
        if os.path.exists(x):
            a = p("daten", "Audiate_Saetze_Englisch_Deutsch.xlsx")
            importer.import_xlsx(conn, x, a if os.path.exists(a) else None)


def _log_error(text):
    try:
        with open(p("fehler.log"), "a", encoding="utf-8") as f:
            f.write(text + "\n")
    except Exception:
        pass


def selftest():
    """Pruefung fuer die fertige EXE: schreibt selftest.txt neben das Programm (Datenbank, Stimme, MP3-Baustein)."""
    z = []
    def step(name, fn):
        try:
            r = fn() or ""
            z.append(("FEHLER  " if "FEHLT" in str(r) else "OK      ") + "%s %s" % (name, r))
        except Exception as ex:
            import traceback
            z.append("FEHLER  %s: %s\n%s" % (name, ex, traceback.format_exc()))
    conn = db.connect()
    step("Programmordner", lambda: paths_dir())
    step("Datenbank", lambda: "%d Kapitel" % conn.execute("SELECT COUNT(*) FROM kapitel").fetchone()[0])
    step("Sprachduschen-Daten", lambda: "vorhanden" if os.path.exists(sd_import.json_path()) else "FEHLT: daten\\sprachduschen.json")
    for lab, name in speech.VOICES.items():
        step("Stimme " + name, lambda name=name: "installiert" if speech.voice_ok(name) else "FEHLT im Ordner voices")
    step("Stimme " + speech.DE_VOICE + " (nur MP3-Export)", lambda: "installiert" if speech.voice_ok(speech.DE_VOICE) else "FEHLT im Ordner voices")
    def synth():
        sp = speech.Speaker(); path = sp.wav_for("This is a test.", list(speech.VOICES)[0], 0.8, True)
        return "%.1f Sekunden Sprache" % speech.wav_seconds(path)
    step("Sprache erzeugen", synth)
    step("MP3-Baustein", lambda: __import__("lameenc") and "ok")
    step("Excel-Baustein", lambda: __import__("openpyxl") and "ok")
    with open(p("selftest.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(z) + "\n")
    return not any(x.startswith("FEHLER") for x in z)


def paths_dir():
    from paths import base_dir
    return base_dir()


def main():
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    app = QApplication(sys.argv)
    try:
        conn = db.connect()
        first_start_import(conn)
        w = MainWindow(conn); w.show()
    except Exception:
        import traceback
        t = traceback.format_exc(); _log_error(t)
        QMessageBox.critical(None, "Vokabeltrainer", "Das Programm konnte nicht starten.\nDie Fehlermeldung steht in der Datei fehler.log.\n\n" + t[-600:])
        sys.exit(1)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

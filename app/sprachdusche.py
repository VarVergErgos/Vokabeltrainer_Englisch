# Bereich "Sprachduschen": Zusatzbereich fuer eigene Lernbuecher, getrennt von den eigenen Kapiteln.
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QStackedWidget, QButtonGroup, QMessageBox)
import db, sd_import

RUBRIK_NAMEN = [(None, "Alle Rubriken"), ("vok", "Vokabeln"), ("dialog", "Dialog"), ("nach", "Nachsprechen")]


class SDPage(QWidget):
    def __init__(self, conn, listen, quiz, progress, scope):
        super().__init__()
        self.conn, self.listen, self.quiz, self.progress, self.scope = conn, listen, quiz, progress, scope
        v = QVBoxLayout(self); v.setContentsMargins(0, 0, 0, 0); v.setSpacing(0)
        head = QWidget(); hv = QVBoxLayout(head); hv.setContentsMargins(24, 20, 24, 6)
        t = QLabel("Sprachduschen"); t.setObjectName("title"); hv.addWidget(t)
        s = QLabel("Zusatzbereich für Lernbücher, die du selbst besitzt und nutzen darfst. Dieser Bereich ist getrennt von deinen eigenen Kapiteln: eigener Lernstand, eigener Fortschritt.")
        s.setObjectName("muted"); s.setWordWrap(True); hv.addWidget(s)
        self.nodata = QLabel(""); self.nodata.setWordWrap(True); hv.addWidget(self.nodata)
        self.load_btn = QPushButton("📥 Daten jetzt einlesen"); self.load_btn.setObjectName("pri"); self.load_btn.clicked.connect(self.load_data)
        hv.addWidget(self.load_btn, 0, Qt.AlignLeft)
        r = QHBoxLayout(); self.filters = QWidget(); fl = QHBoxLayout(self.filters); fl.setContentsMargins(0, 0, 0, 0)
        fl.addWidget(QLabel("Buch")); self.buch = QComboBox(); self.buch.setMinimumWidth(260); fl.addWidget(self.buch)
        fl.addWidget(QLabel("Rubrik")); self.rub = QComboBox(); [self.rub.addItem(n, k) for k, n in RUBRIK_NAMEN]; fl.addWidget(self.rub)
        fl.addStretch(1); hv.addWidget(self.filters)
        self.buch.currentIndexChanged.connect(self._filter); self.rub.currentIndexChanged.connect(self._filter)
        mh = QHBoxLayout(); self.grp = QButtonGroup(self); self.grp.setExclusive(True)
        self.modes = QWidget(); ml = QHBoxLayout(self.modes); ml.setContentsMargins(0, 0, 0, 0)
        for i, name in enumerate(("🔊  Vorlesen", "❓  Abfrage", "📊  Fortschritt")):
            b = QPushButton(name); b.setObjectName("pill"); b.setCheckable(True); b.setChecked(i == 0); self.grp.addButton(b, i); ml.addWidget(b)
        ml.addStretch(1); hv.addWidget(self.modes)
        v.addWidget(head)
        self.stack = QStackedWidget(); v.addWidget(self.stack, 1)
        for w in (listen, quiz, progress):
            self.stack.addWidget(w)
        self.grp.idClicked.connect(self._mode)
        self._fill_books(); self._state()

    # ---- Daten
    def _state(self):
        has = sd_import.has_data(self.conn)
        self.nodata.setVisible(not has); self.load_btn.setVisible(not has)
        self.filters.setVisible(has); self.modes.setVisible(has); self.stack.setVisible(has)
        if not has:
            self.nodata.setText("Noch keine Sprachduschen eingelesen. Die Datei daten\\sprachduschen.json wird dafür verwendet.")

    def _fill_books(self):
        cur = self.buch.currentData()
        self.buch.blockSignals(True); self.buch.clear(); self.buch.addItem("Alle Bücher", None)
        for (b,) in self.conn.execute("SELECT DISTINCT buch FROM kapitel WHERE bereich='sd' ORDER BY MIN(nr)", ()) if False else \
                self.conn.execute("SELECT buch FROM kapitel WHERE bereich='sd' GROUP BY buch ORDER BY MIN(nr)"):
            self.buch.addItem(b, b)
        i = self.buch.findData(cur); self.buch.setCurrentIndex(max(i, 0)); self.buch.blockSignals(False)

    def load_data(self):
        try:
            nb, nl, ne = sd_import.import_sd(self.conn)
        except Exception as ex:
            QMessageBox.critical(self, "Sprachduschen", "Das Einlesen hat nicht geklappt:\n%s" % ex); return
        self._fill_books(); self._state(); self._filter()
        QMessageBox.information(self, "Sprachduschen", "%d Bücher, %d Lektionen und %d Einträge wurden eingelesen." % (nb, nl, ne))

    # ---- Filter und Ansicht
    def _filter(self):
        self.scope.buch, self.scope.rubrik = self.buch.currentData(), self.rub.currentData()
        self.listen.reload_chapters(); self.listen.load(); self.quiz.reload_chapters()
        if self.stack.currentWidget() is self.quiz: self.quiz.start_round()
        elif self.stack.currentWidget() is self.progress: self.progress.refresh()

    def _mode(self, i):
        self.listen.stop(); self.stack.setCurrentIndex(i); self._show(self.stack.currentWidget())

    def _show(self, w):
        if w is self.quiz: self.quiz.refresh()
        elif w is self.progress: self.progress.refresh()

    def refresh(self):
        self._state()
        if sd_import.has_data(self.conn):
            self._show(self.stack.currentWidget())

    def stop(self):
        self.listen.stop()

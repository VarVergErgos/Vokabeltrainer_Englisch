# Suchmaske: findet deutsche und englische Woerter in allen Kapiteln und Sprachduschen.
import re, unicodedata
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QCheckBox, QPushButton,
                               QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView)
import db

MAXZEILEN = 400

def fold(s):
    """Vergleichsform: klein, ohne Umlaut-Striche (ä=a), ß=ss. So findet 'apfel' auch 'Äpfel'."""
    s = unicodedata.normalize("NFKD", (s or "").lower().replace("ß", "ss").replace("’", "'"))
    return "".join(c for c in s if not unicodedata.combining(c))

RUBRIK = {"vok": "Vokabeln", "dialog": "Dialog", "nach": "Nachsprechen", "": ""}


def load_index(conn):
    rows = conn.execute("""SELECT e.id, e.englisch, e.deutsch, e.beispiel_en, e.beispiel_de, e.rubrik, e.sprecher, e.kapitel_id,
                                  k.nr, k.titel, k.buch, COALESCE(k.bereich,'eigen') AS bereich
                           FROM eintrag e JOIN kapitel k ON k.id=e.kapitel_id ORDER BY k.bereich DESC, k.nr, e.pos, e.id""").fetchall()
    idx = []
    for r in rows:
        d = dict(r)
        d["f_en"], d["f_de"] = fold(d["englisch"]), fold(d["deutsch"])
        d["f_ben"], d["f_bde"] = fold(d["beispiel_en"]), fold(d["beispiel_de"])
        idx.append(d)
    return idx


def search(idx, text, bereich="alle", sprache="beide", ganz=False, beispiele=True):
    """Gibt (Treffer, Gesamtzahl) zurueck. Beste Treffer zuerst: gleich, Wortanfang, Wort im Text, sonst enthalten."""
    q = fold(text).strip()
    if not q:
        return [], 0
    pat = re.compile(r"(?<![a-z0-9])" + re.escape(q) + (r"(?![a-z0-9])" if ganz else "")) if q else None
    out = []
    for d in idx:
        if bereich != "alle" and d["bereich"] != bereich:
            continue
        fields = []
        if sprache in ("beide", "en"): fields.append(d["f_en"])
        if sprache in ("beide", "de"): fields.append(d["f_de"])
        score = None
        for f in fields:
            if f == q: s = 0
            elif pat.search(f) and f.startswith(q): s = 1
            elif pat.search(f): s = 2
            elif not ganz and q in f: s = 3
            else: continue
            score = s if score is None else min(score, s)
        if score is None and beispiele:
            ex = ([d["f_ben"]] if sprache in ("beide", "en") else []) + ([d["f_bde"]] if sprache in ("beide", "de") else [])
            if any((pat.search(f) if ganz else q in f) for f in ex):
                score = 4
        if score is not None:
            out.append((score, len(d["f_en"]), d))
    out.sort(key=lambda t: (t[0], t[2]["bereich"] != "eigen", t[1]))
    return [d for _, _, d in out], len(out)


def where(d):
    if d["bereich"] == "sd":
        return "%s · %s%s" % (d["buch"], d["titel"], (" · " + RUBRIK.get(d["rubrik"], "")) if d["rubrik"] else "")
    return "Kapitel %d: %s" % (d["nr"], d["titel"])


class SearchPage(QWidget):
    open_hit = Signal(dict)

    def __init__(self, conn, speak):
        super().__init__()
        self.conn, self.speak, self.idx, self.hits = conn, speak, [], []
        v = QVBoxLayout(self); v.setContentsMargins(24, 20, 24, 16); v.setSpacing(8)
        t = QLabel("Suchen"); t.setObjectName("title"); v.addWidget(t)
        s = QLabel("Tippe ein deutsches oder englisches Wort. Gesucht wird in deinen Kapiteln und in den Sprachduschen."); s.setObjectName("muted"); s.setWordWrap(True); v.addWidget(s)
        self.box = QLineEdit(); self.box.setPlaceholderText("Wort oder Satzteil, z. B. Versicherung oder insurance"); self.box.setClearButtonEnabled(True)
        v.addWidget(self.box)
        r = QHBoxLayout(); v.addLayout(r)
        r.addWidget(QLabel("Wo")); self.bereich = QComboBox(); [self.bereich.addItem(n, k) for k, n in (("alle", "Überall"), ("eigen", "Nur meine Kapitel"), ("sd", "Nur Sprachduschen"))]; r.addWidget(self.bereich)
        r.addWidget(QLabel("Sprache")); self.sprache = QComboBox(); [self.sprache.addItem(n, k) for k, n in (("beide", "Englisch und Deutsch"), ("en", "Nur Englisch"), ("de", "Nur Deutsch"))]; r.addWidget(self.sprache)
        self.ganz = QCheckBox("Ganzes Wort"); r.addWidget(self.ganz)
        self.bsp = QCheckBox("Auch in Beispielsätzen"); self.bsp.setChecked(True); r.addWidget(self.bsp); r.addStretch(1)
        self.info = QLabel(""); self.info.setObjectName("muted"); v.addWidget(self.info)
        self.tab = QTableWidget(0, 3); self.tab.setHorizontalHeaderLabels(["Englisch", "Deutsch", "Wo steht es"])
        self.tab.setEditTriggers(QAbstractItemView.NoEditTriggers); self.tab.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tab.setSelectionMode(QAbstractItemView.SingleSelection); self.tab.verticalHeader().hide(); self.tab.setWordWrap(True)
        for c in range(3): self.tab.horizontalHeader().setSectionResizeMode(c, QHeaderView.Stretch)
        self.tab.cellDoubleClicked.connect(lambda r, c: self.open_selected())
        v.addWidget(self.tab, 1)
        b = QHBoxLayout(); v.addLayout(b)
        self.b_play = QPushButton("🔊 Englisch anhören"); self.b_play.clicked.connect(self.play); b.addWidget(self.b_play)
        self.b_open = QPushButton("📖 Im Kapitel öffnen"); self.b_open.clicked.connect(self.open_selected); b.addWidget(self.b_open)
        b.addStretch(1)
        self.timer = QTimer(self); self.timer.setSingleShot(True); self.timer.setInterval(250); self.timer.timeout.connect(self.run)
        self.box.textChanged.connect(lambda _: self.timer.start())
        for w in (self.bereich, self.sprache): w.currentIndexChanged.connect(self.run)
        for w in (self.ganz, self.bsp): w.toggled.connect(self.run)
        self.box.returnPressed.connect(self.run)

    def refresh(self):
        self.idx = load_index(self.conn); self.run(); self.box.setFocus()

    def run(self):
        text = self.box.text()
        self.hits, n = search(self.idx, text, self.bereich.currentData(), self.sprache.currentData(), self.ganz.isChecked(), self.bsp.isChecked())
        shown = self.hits[:MAXZEILEN]; self.tab.setRowCount(len(shown))
        for r, d in enumerate(shown):
            for c, val in enumerate((("%s: " % d["sprecher"] if d["sprecher"] else "") + d["englisch"], d["deutsch"] or "–", where(d))):
                self.tab.setItem(r, c, QTableWidgetItem(val))
        self.tab.resizeRowsToContents()
        if not text.strip(): self.info.setText("%d Einträge durchsuchbar." % len(self.idx))
        elif n == 0: self.info.setText("Nichts gefunden.")
        else: self.info.setText("%d Treffer%s" % (n, (" (die ersten %d werden gezeigt, bitte genauer suchen)" % MAXZEILEN) if n > MAXZEILEN else ""))

    def _cur(self):
        r = self.tab.currentRow()
        if r < 0 and self.tab.rowCount(): r = 0
        return self.hits[r] if 0 <= r < len(self.hits) else None

    def play(self):
        d = self._cur()
        if d: self.speak(d["englisch"])

    def open_selected(self):
        d = self._cur()
        if d: self.open_hit.emit(d)

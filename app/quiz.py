# Abfrage (Karteikarten) und Fortschritt
import re
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor, QShortcut, QKeySequence
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QFrame, QLineEdit,
                               QProgressBar, QButtonGroup, QGridLayout)
import db

MODI = [("en_de", "Englisch → Deutsch"), ("de_en", "Deutsch → Englisch"), ("hoeren", "Hören → Schreiben")]
LIMITS = [("10 Karten", 10), ("20 Karten", 20), ("30 Karten", 30), ("Alle fälligen", 0)]


def variants(en):
    """Zulaessige Schreibweisen eines englischen Eintrags (ohne 'to', Klammern, Alternativen mit ' / ')."""
    t = re.sub(r"\(.*?\)", "", en)
    out = set()
    for part in t.split(" / "):
        k = db.norm(part)
        out.add(k)
        if k.startswith("to "):
            out.add(k[3:])
    return {v for v in out if v}


class QuizPage(QWidget):
    def __init__(self, conn, speak, user_fn, status, scope=db.EIGEN):
        super().__init__()
        self.scope = scope
        self.conn, self.speak, self.user_fn, self.status = conn, speak, user_fn, status
        self.modus, self.queue, self.cur, self.total, self.done, self.gewusst, self.nochmal = "en_de", [], None, 0, 0, 0, 0
        self.revealed, self.requeued, self.checked = False, set(), False
        v = QVBoxLayout(self); v.setContentsMargins(24, 20, 24, 16); v.setSpacing(10)
        t = QLabel("Abfrage"); t.setObjectName("title"); v.addWidget(t)
        self.sub = QLabel(""); self.sub.setObjectName("muted"); self.sub.setWordWrap(True); v.addWidget(self.sub)
        h = QHBoxLayout(); self.grp = QButtonGroup(self); self.grp.setExclusive(True)
        for i, (key, name) in enumerate(MODI):
            b = QPushButton(name); b.setObjectName("pill"); b.setCheckable(True); b.setChecked(i == 0); self.grp.addButton(b, i); h.addWidget(b)
        self.grp.idClicked.connect(self._mode); h.addStretch(1); v.addLayout(h)
        h = QHBoxLayout(); h.addWidget(QLabel("Kapitel")); self.kap = QComboBox(); self.kap.setMinimumWidth(260); h.addWidget(self.kap)
        self.lim = QComboBox(); [self.lim.addItem(n, x) for n, x in LIMITS]; h.addWidget(self.lim)
        self.chip = QLabel(""); self.chip.setObjectName("chip"); h.addWidget(self.chip)
        self.serie = QLabel(""); self.serie.setObjectName("chip"); h.addWidget(self.serie); h.addStretch(1); v.addLayout(h)
        self.bar = QProgressBar(); self.bar.setTextVisible(False); self.bar.setFixedHeight(10); v.addWidget(self.bar)
        self.card = QFrame(); self.card.setObjectName("card"); c = QVBoxLayout(self.card); c.setContentsMargins(24, 22, 24, 22); c.setSpacing(8)
        self.hint = QLabel(""); self.hint.setObjectName("muted"); self.hint.setAlignment(Qt.AlignCenter); self.hint.setWordWrap(True)
        self.prompt = QLabel(""); self.prompt.setObjectName("prompt"); self.prompt.setAlignment(Qt.AlignCenter); self.prompt.setWordWrap(True)
        self.pron = QLabel(""); self.pron.setObjectName("muted"); self.pron.setAlignment(Qt.AlignCenter)
        self.ctx = QLabel(""); self.ctx.setObjectName("muted"); self.ctx.setAlignment(Qt.AlignCenter); self.ctx.setWordWrap(True)
        self.input = QLineEdit(); self.input.setPlaceholderText("Hier auf Englisch schreiben"); self.input.hide()
        self.answer_lbl = QLabel(""); self.answer_lbl.setObjectName("answer"); self.answer_lbl.setAlignment(Qt.AlignCenter); self.answer_lbl.setWordWrap(True)
        for w in (self.hint, self.prompt, self.pron, self.ctx, self.input, self.answer_lbl):
            c.addWidget(w)
        c.addStretch(1); v.addWidget(self.card, 1)
        h = QHBoxLayout(); h.addStretch(1)
        self.b_listen = QPushButton("🔊 Anhören"); self.b_listen.setObjectName("btn")
        self.b_reveal = QPushButton("Antwort zeigen"); self.b_reveal.setObjectName("pri")
        self.b_no = QPushButton("Nochmal üben (N)"); self.b_no.setObjectName("bad")
        self.b_yes = QPushButton("Wusste ich (J)"); self.b_yes.setObjectName("ok")
        self.b_next = QPushButton("Weiter"); self.b_next.setObjectName("pri")
        self.b_new = QPushButton("Neue Runde"); self.b_new.setObjectName("pri")
        for b in (self.b_listen, self.b_reveal, self.b_no, self.b_yes, self.b_next, self.b_new):
            h.addWidget(b)
        h.addStretch(1); v.addLayout(h)
        self.b_listen.clicked.connect(self.listen_now); self.b_reveal.clicked.connect(self.reveal)
        self.b_yes.clicked.connect(lambda: self.rate(True)); self.b_no.clicked.connect(lambda: self.rate(False))
        self.b_next.clicked.connect(self.next_card); self.b_new.clicked.connect(self.start_round)
        self.input.returnPressed.connect(self.reveal)
        self.kap.currentIndexChanged.connect(lambda *_: self.start_round()); self.lim.currentIndexChanged.connect(lambda *_: self.start_round())
        for key, fn in (("J", lambda: self.rate(True)), ("N", lambda: self.rate(False))):
            sc = QShortcut(QKeySequence(key), self); sc.setContext(Qt.WidgetWithChildrenShortcut); sc.activated.connect(fn)
        for key in ("Return", "Enter", "Space"):
            sc = QShortcut(QKeySequence(key), self); sc.setContext(Qt.WidgetWithChildrenShortcut); sc.activated.connect(self.enter_key)
        self.reload_chapters()

    # ---------- Vorbereitung
    def reload_chapters(self):
        cur = self.kap.currentData()
        self.kap.blockSignals(True); self.kap.clear(); self.kap.addItem("Alle Kapitel", 0)
        for k in db.chapters(self.conn, self.scope):
            self.kap.addItem(db.chapter_label(k), k["id"])
        i = self.kap.findData(cur) if cur is not None else 0
        self.kap.setCurrentIndex(max(i, 0)); self.kap.blockSignals(False)

    def _mode(self, i):
        self.modus = MODI[i][0]; self.start_round()

    def start_round(self):
        rows = db.due_cards(self.conn, self.modus, self.kap.currentData() or None, self.lim.currentData(), scope=self.scope)
        self.queue = [dict(r) for r in rows]; self.total = len(self.queue)
        self.done = self.gewusst = self.nochmal = 0; self.requeued = set()
        self.serie.setText("Serie: %d Tage" % db.streak(self.conn))
        self.bar.setRange(0, max(self.total, 1)); self.bar.setValue(0)
        self.sub.setText({"en_de": "Du siehst den englischen Satz und denkst dir die deutsche Bedeutung.",
                          "de_en": "Du siehst das deutsche Wort und sagst es auf Englisch. Danach schaust du nach.",
                          "hoeren": "Du hörst das englische Wort oder den Satz und schreibst es auf."}[self.modus])
        self.next_card()

    def refresh(self):
        self.reload_chapters()
        if self.cur is None and self.done == 0:
            self.start_round()

    # ---------- Ablauf
    def _buttons(self, listen=False, reveal=False, rate=False, nxt=False, new=False):
        self.b_listen.setVisible(listen); self.b_reveal.setVisible(reveal); self.b_yes.setVisible(rate); self.b_no.setVisible(rate)
        self.b_next.setVisible(nxt); self.b_new.setVisible(new)

    def next_card(self):
        self.revealed = self.checked = False
        self.answer_lbl.setText(""); self.pron.setText(""); self.ctx.setText(""); self.input.hide(); self.input.clear()
        if not self.queue:
            self.cur = None
            self.hint.setText("Runde beendet" if self.total else "Heute ist nichts fällig")
            self.prompt.setText("Geschafft!" if self.total else "Alles erledigt")
            self.answer_lbl.setText(("%d gewusst, %d nochmal üben.\nSerie: %d Tage." % (self.gewusst, self.nochmal, db.streak(self.conn))) if self.total
                                    else "Wähle ein anderes Kapitel oder eine andere Richtung.")
            self._buttons(new=True); self.chip.setText("Karte %d von %d" % (self.done, self.total)); self.serie.setText("Serie: %d Tage" % db.streak(self.conn))
            return
        self.cur = self.queue.pop(0); c = self.cur
        self.chip.setText("Karte %d von %d" % (min(self.done + 1, self.total), self.total)); self.bar.setValue(self.done)
        if self.modus == "en_de":
            self.hint.setText("Was bedeutet das?"); self.prompt.setText(c["englisch"]); self.pron.setText(c["aussprache"])
            if c["art"] == "wort" and c["beispiel_en"]:
                self.ctx.setText(c["beispiel_en"])
            elif c.get("sprecher"):
                self.ctx.setText("Sprecher: " + c["sprecher"])
            self._buttons(listen=True, reveal=True)
        elif self.modus == "de_en":
            self.hint.setText("Wie sagt man das auf Englisch?"); self.prompt.setText(c["deutsch"]); self._buttons(reveal=True)
            if c.get("sprecher"): self.ctx.setText("Sprecher: " + c["sprecher"])
        else:
            self.hint.setText("Hör zu und schreibe das englische Wort oder den Satz auf"); self.prompt.setText("🔊")
            self.input.show(); self.input.setFocus(); self._buttons(listen=True, reveal=True); self.b_reveal.setText("Prüfen")
            self.listen_now()
        if self.modus != "hoeren":
            self.b_reveal.setText("Antwort zeigen")

    def listen_now(self):
        if self.cur:
            self.speak(self.cur["englisch"])

    def reveal(self):
        if not self.cur or self.revealed:
            return
        self.revealed = True; c = self.cur
        if self.modus == "hoeren":
            ok = db.norm(self.input.text()) in variants(c["englisch"])
            self.answer_lbl.setText(("✓ Richtig: " if ok else "✗ Richtig ist: ") + c["englisch"] + "\n" + c["deutsch"])
            self.checked = True; self.gewusst += ok; self.nochmal += (not ok); self._save(ok)
            self.done += 1; self.bar.setValue(self.done)
            if not ok: self._requeue()
            self._buttons(listen=True, nxt=True); return
        if self.modus == "en_de":
            self.answer_lbl.setText(c["deutsch"] + (("\n" + c["beispiel_de"]) if c["art"] == "wort" and c["beispiel_de"] else ""))
        else:
            self.answer_lbl.setText(c["englisch"]); self.pron.setText(c["aussprache"])
            self.ctx.setText(c["beispiel_en"] if c["art"] == "wort" else "")
        self._buttons(listen=True, rate=True)

    def rate(self, ok):
        if not self.cur or not self.revealed or self.modus == "hoeren" or self.checked:
            return
        self.checked = True; self._save(ok); self.done += 1; self.gewusst += ok; self.nochmal += (not ok)
        if not ok: self._requeue()
        self.next_card()

    def _requeue(self):
        if self.cur["id"] not in self.requeued:           # falsche Karte kommt einmal am Ende der Runde wieder
            self.requeued.add(self.cur["id"]); self.queue.append(self.cur); self.total += 1
            self.bar.setRange(0, self.total)

    def _save(self, ok):
        db.answer(self.conn, self.cur["id"], self.modus, ok, self.user_fn())

    def enter_key(self):
        if self.b_next.isVisible():
            self.next_card()
        elif self.b_reveal.isVisible():
            self.reveal()
        elif self.b_new.isVisible():
            self.start_round()


class StackBar(QWidget):
    """Balken: gefuellter Teil = Lernfortschritt in Prozent (erreichte Stufe von 4)."""
    def __init__(self, pct, colors):
        super().__init__(); self.pct = pct; self.c = colors; self.setFixedHeight(16)

    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing); w, h = self.width(), self.height()
        p.setPen(Qt.NoPen); p.setBrush(QColor(self.c[2])); p.drawRoundedRect(0, 0, w, h, h / 2, h / 2)
        ww = int(w * max(0, min(self.pct, 100)) / 100.0)
        if ww:
            p.setBrush(QColor(self.c[0] if self.pct >= 50 else self.c[1])); p.drawRoundedRect(0, 0, max(ww, h), h, h / 2, h / 2)


class ProgressPage(QWidget):
    def __init__(self, conn, colors_fn, scope=db.EIGEN):
        super().__init__()
        self.scope = scope
        self.conn, self.colors_fn = conn, colors_fn
        v = QVBoxLayout(self); v.setContentsMargins(24, 20, 24, 16); v.setSpacing(10)
        t = QLabel("Fortschritt"); t.setObjectName("title"); v.addWidget(t)
        s = QLabel("Alle Benutzer zusammen"); s.setObjectName("muted"); v.addWidget(s)
        h = QHBoxLayout(); h.addWidget(QLabel("Richtung")); self.mode = QComboBox(); [self.mode.addItem(n, k) for k, n in MODI]
        self.mode.currentIndexChanged.connect(self.refresh); h.addWidget(self.mode); h.addStretch(1); v.addLayout(h)
        self.kpis = QHBoxLayout(); v.addLayout(self.kpis)
        self.stufen = QLabel(""); self.stufen.setObjectName("muted"); self.stufen.setWordWrap(True); v.addWidget(self.stufen)
        self.body = QGridLayout(); self.body.setColumnStretch(1, 1); self.body.setHorizontalSpacing(12); v.addLayout(self.body)
        self.leg = QLabel(""); self.leg.setObjectName("muted"); v.addWidget(self.leg); v.addStretch(1)

    def refresh(self):
        s = db.stats(self.conn, self.mode.currentData(), scope=self.scope); col = self.colors_fn()
        while self.kpis.count():
            w = self.kpis.takeAt(0).widget()
            if w: w.setParent(None); w.deleteLater()
        for val, lab in (("%d %%" % s["prozent"], "Lernfortschritt"), (s["total"], "Einträge insgesamt"), (s["kann"], "sicher (Stufe 3+)"),
                         (s["faellig"], "heute fällig"), (s["heute"], "heute beantwortet"), ("%d Tage" % s["serie"], "Lernserie")):
            f = QFrame(); f.setObjectName("kpi"); l = QVBoxLayout(f)
            a = QLabel(str(val)); a.setObjectName("kpival"); b = QLabel(lab); b.setObjectName("muted"); l.addWidget(a); l.addWidget(b)
            self.kpis.addWidget(f)
        while self.body.count():
            w = self.body.takeAt(0).widget()
            if w: w.setParent(None); w.deleteLater()
        st = s["stufen"]
        self.stufen.setText("Stufen:  neu %d   ·   Stufe 0 (nochmal) %d   ·   Stufe 1 (1 Tag) %d   ·   Stufe 2 (3 Tage) %d   ·   Stufe 3 (7 Tage) %d   ·   Stufe 4 (14 Tage) %d"
                            % (s["total"] - sum(st), st[0], st[1], st[2], st[3], st[4]))
        for r, (nr, titel, n, kann, ueben, pct) in enumerate(s["kapitel"]):
            self.body.addWidget(QLabel(titel if self.scope.bereich != "eigen" else "%d  %s" % (nr, titel)), r, 0)
            self.body.addWidget(StackBar(pct, col), r, 1)
            pc = QLabel("%d %%" % pct); pc.setObjectName("muted"); self.body.addWidget(pc, r, 2)
        self.leg.setText("Lernfortschritt = erreichte Stufe von 4. 100 % heißt: jede Karte hat Stufe 4 (nach 14 Tagen richtig). Orange = unter 50 %, Grün = ab 50 %.")

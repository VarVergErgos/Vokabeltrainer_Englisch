# Menuepunkt "Grammatik und Zeiten": zeigt alle PDF-Dateien im Ordner Grammatik und oeffnet sie mit dem Standardprogramm.
import os, re
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                               QHeaderView, QAbstractItemView, QMessageBox)
from paths import p, ensure

ORDNER = "Grammatik"

def natkey(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]

def scan(root):
    """Alle PDF-Dateien im Ordner (auch in Unterordnern), natuerlich sortiert (01, 02, ... 10)."""
    out = []
    for d, _, fs in os.walk(root):
        for f in fs:
            if f.lower().endswith(".pdf"):
                out.append(os.path.join(d, f))
    return sorted(out, key=lambda x: natkey(os.path.relpath(x, root)))

def titel(datei):
    """Lesbarer Titel aus dem Dateinamen: ohne Nummer, ohne Unterstriche, ohne Zusatz 'A4 Quer'."""
    n = os.path.splitext(os.path.basename(datei))[0]
    n = re.sub(r"^\s*\d+[\s_.-]*", "", n)
    n = n.replace("_", " ")
    n = re.sub(r"\s*Leitfaden\s*A4\s*Quer", "", n, flags=re.I)
    n = re.sub(r"\s*Kombiniert\s*$", " (alle Leitfäden in einem)", n, flags=re.I)
    n = re.sub(r"Loesungen", "Lösungen", n); n = re.sub(r"Erklaerungen", "Erklärungen", n)
    n = re.sub(r"Leitfaeden", "Leitfäden", n)
    n = re.sub(r"(?<=[a-zäöü])(?=[A-ZÄÖÜ])", " ", n)       # EinstufungstestEnglisch -> Einstufungstest Englisch
    n = re.sub(r"\s+", " ", n).strip()
    return n or os.path.basename(datei)

def art(datei):
    n = os.path.basename(datei).lower()
    if "loesung" in n or "lösung" in n:
        return "Test mit Lösungen"
    if "einstufungstest" in n:
        return "Test"
    if "kombiniert" in n or re.search(r"grammatik_?\d*\.pdf$", n):
        return "Sammlung"
    if "leitfaden" in n or "grammatik" in n:
        return "Leitfaden"
    return "PDF"

def groesse(datei):
    try:
        b = os.path.getsize(datei)
    except OSError:
        return ""
    return "%d KB" % round(b / 1024) if b < 1024 * 1024 else ("%.1f MB" % (b / 1024 / 1024)).replace(".", ",")

class GrammatikPage(QWidget):
    def __init__(self, status=None):
        super().__init__()
        self.status = status or (lambda t: None)
        self.root = ensure(ORDNER); self.files = []
        v = QVBoxLayout(self); v.setContentsMargins(24, 20, 24, 16)
        t = QLabel("Grammatik und Zeiten"); t.setObjectName("title"); v.addWidget(t)
        s = QLabel("Hier stehen alle PDF-Dateien aus dem Ordner „Grammatik“. Doppelklick oder „Öffnen“ zeigt die Datei in deinem PDF-Programm.")
        s.setObjectName("muted"); s.setWordWrap(True); v.addWidget(s)
        h = QHBoxLayout()
        self.suche = QLineEdit(); self.suche.setPlaceholderText("Suchen, z. B. Present oder Test"); self.suche.setClearButtonEnabled(True)
        self.suche.textChanged.connect(self.filter); h.addWidget(self.suche, 1)
        self.count = QLabel(""); self.count.setObjectName("chip"); h.addWidget(self.count)
        v.addLayout(h)
        self.tab = QTableWidget(0, 4); self.tab.setHorizontalHeaderLabels(["Nr.", "Titel", "Art", "Größe"])
        self.tab.setEditTriggers(QAbstractItemView.NoEditTriggers); self.tab.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tab.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tab.verticalHeader().hide(); self.tab.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        hh = self.tab.horizontalHeader(); hh.setSectionResizeMode(0, QHeaderView.Fixed); hh.setSectionResizeMode(2, QHeaderView.Fixed); hh.setSectionResizeMode(3, QHeaderView.Fixed)
        self.tab.setColumnWidth(0, 60); self.tab.setColumnWidth(2, 170); self.tab.setColumnWidth(3, 90)
        self.tab.cellDoubleClicked.connect(lambda r, c: self.open_row(r))
        v.addWidget(self.tab, 1)
        self.leer = QLabel(""); self.leer.setObjectName("muted"); self.leer.setWordWrap(True); self.leer.setAlignment(Qt.AlignCenter); v.addWidget(self.leer)
        b = QHBoxLayout()
        self.openb = QPushButton("📄 Öffnen"); self.openb.setObjectName("pri"); self.openb.clicked.connect(lambda: self.open_row(self.tab.currentRow())); b.addWidget(self.openb)
        x = QPushButton("📂 Ordner öffnen"); x.setObjectName("btn"); x.clicked.connect(self.open_folder); b.addWidget(x)
        x = QPushButton("↻ Neu einlesen"); x.setObjectName("btn"); x.clicked.connect(self.refresh); b.addWidget(x)
        b.addStretch(1); v.addLayout(b)
        self.pfad = QLabel(""); self.pfad.setObjectName("muted"); self.pfad.setWordWrap(True); v.addWidget(self.pfad)
        self.refresh()

    def refresh(self):
        self.root = ensure(ORDNER); self.files = scan(self.root)
        self.pfad.setText("Ordner: " + self.root)
        self.filter()

    def filter(self):
        q = self.suche.text().strip().lower()
        rows = [(i, f) for i, f in enumerate(self.files, 1) if not q or q in (titel(f) + " " + art(f) + " " + os.path.basename(f)).lower()]
        self.tab.setRowCount(len(rows)); self.shown = [f for _, f in rows]
        for r, (i, f) in enumerate(rows):
            for c, val in enumerate([str(i), titel(f), art(f), groesse(f)]):
                it = QTableWidgetItem(val); it.setToolTip(os.path.relpath(f, self.root))
                if c in (0, 3): it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.tab.setItem(r, c, it)
        self.tab.resizeRowsToContents()
        if rows: self.tab.selectRow(0)
        n = len(self.files)
        self.count.setText("%d PDF" % n if not q else "%d von %d" % (len(rows), n))
        self.openb.setEnabled(bool(rows))
        if not self.files:
            self.leer.setText("Im Ordner Grammatik liegen noch keine PDF-Dateien.\nLege deine PDFs dort ab und klicke dann auf „Neu einlesen“.")
        elif not rows:
            self.leer.setText("Nichts gefunden.")
        else:
            self.leer.setText("")
        self.leer.setVisible(bool(self.leer.text()))

    def open_row(self, r):
        if r < 0 or r >= len(getattr(self, "shown", [])):
            return
        f = self.shown[r]
        if not os.path.exists(f):
            QMessageBox.information(self, "Grammatik", "Die Datei gibt es nicht mehr. Ich lese den Ordner neu ein.\n\n" + f); self.refresh(); return
        if QDesktopServices.openUrl(QUrl.fromLocalFile(f)):
            self.status("Geöffnet: " + os.path.basename(f))
        else:
            QMessageBox.information(self, "Grammatik", "Die Datei konnte nicht geöffnet werden. Sie liegt hier:\n" + f)

    def open_folder(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.root))

# Import aus dem Excel-Vokabeltrainer (Blatt "Alle Vokabeln") und optional aus der Audiate-Datei (Datum je Kapitel).
import re, warnings
import openpyxl
import db

FARBEN = ["#1F4E79", "#2E7D6B", "#8A4B9E", "#B5651D", "#B03A2E", "#3B7A2B", "#555555",
          "#0E7C86", "#6A4C93", "#A0522D", "#C2185B", "#00695C"]

def _kapitel_nr(text):
    m = re.match(r"\s*(\d+)\s+(.*)", str(text or ""))
    return (int(m.group(1)), m.group(2).strip()) if m else (None, str(text or ""))

def _datums(audiate_path):
    out = {}
    if not audiate_path:
        return out
    wb = openpyxl.load_workbook(audiate_path, read_only=True)
    ws = wb["Alle Sätze"] if "Alle Sätze" in wb.sheetnames else wb.worksheets[1]
    for row in ws.iter_rows(min_row=2, values_only=True):
        nr, _ = _kapitel_nr(row[1])
        if nr and nr not in out and row[2]:
            out[nr] = str(row[2])
    return out

def import_xlsx(conn, path, audiate_path=None):
    """Gibt (neue_eintraege, uebersprungen_doppelt, kapitel) zurueck."""
    warnings.filterwarnings("ignore")
    wb = openpyxl.load_workbook(path)
    datums = _datums(audiate_path)
    quellen = {}
    for ws in wb.worksheets:
        m = re.match(r"\s*(\d+)\s", ws.title)
        if m and ws["A2"].value:
            q = re.search(r"Quelle:\s*(.*?)\.\s+Lernstatus", str(ws["A2"].value))
            quellen[int(m.group(1))] = q.group(1) if q else ""
    ws = wb["Alle Vokabeln"]
    neu = doppelt = 0
    kap = {}
    pos = {}
    for row in ws.iter_rows(min_row=5, values_only=True):
        if not row or not row[1] or not row[2]:
            continue
        nr, titel = _kapitel_nr(row[1])
        if nr is None:
            continue
        if nr not in kap:
            kap[nr] = db.add_chapter(conn, nr, titel, thema=quellen.get(nr, ""), hinweis=quellen.get(nr, ""),
                                     datum=datums.get(nr), farbe=FARBEN[(nr - 1) % len(FARBEN)])
        en, pron, de, ex_en, ex_de = row[2], row[3] or "", row[4], row[5] or "", row[6] or ""
        art = "satz" if (not pron or not ex_en) else "wort"
        pos[nr] = pos.get(nr, 0) + 1
        if db.add_entry(conn, kap[nr], en, de, pron, ex_en, ex_de, art, pos[nr]):
            neu += 1
        else:
            doppelt += 1
    conn.commit()
    return neu, doppelt, len(kap)


# ---- Neue Kapitel aus der Mustervorlage (Kapitel_Vorlage.xlsx)
def _cell(ws, r, c):
    v = ws.cell(r, c).value
    return "" if v is None else str(v).strip()

def import_chapter_xlsx(conn, path):
    """Liest jedes Blatt, dessen Zelle A1 mit 'Kapitel-Titel' beginnt, als neues Kapitel.
    Rueckgabe: Liste (Titel, neu, [doppelte Saetze]) - leere Blaetter und Blaetter ohne Titel werden uebersprungen."""
    wb = openpyxl.load_workbook(path, data_only=True)
    out = []
    for ws in wb.worksheets:
        if not _cell(ws, 1, 1).lower().startswith("kapitel-titel"):
            continue
        titel, hinweis = _cell(ws, 1, 2), _cell(ws, 2, 2)
        rows = []
        for r in range(5, ws.max_row + 1):
            en, de = _cell(ws, r, 1), _cell(ws, r, 2)
            if en or de:
                rows.append((r, en, de, _cell(ws, r, 3), _cell(ws, r, 4), _cell(ws, r, 5)))
        if not titel or not rows:
            continue
        kid, nr = db.new_chapter(conn, titel, hinweis)
        neu, dups, fehl = 0, [], []
        for r, en, de, au, ben, bde in rows:
            if not en or not de:
                fehl.append("Zeile %d: Englisch oder Deutsch fehlt" % r); continue
            eid, dup = db.add_new_entry(conn, kid, en, de, au, ben, bde)
            if eid: neu += 1
            else: dups.append("%s (steht schon in Kapitel %d)" % (en, dup[0]))
        if neu == 0:                       # nichts uebernommen: leeres Kapitel wieder entfernen
            db.delete_chapter(conn, kid); nr = None
        out.append((titel, nr, neu, dups, fehl))
    conn.commit()
    return out

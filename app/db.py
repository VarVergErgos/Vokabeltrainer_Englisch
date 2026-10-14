# SQLite-Datenbank des Vokabeltrainers (eine Datei: vokabeln.db neben dem Programm).
import os, re, shutil, sqlite3, datetime
from datetime import date, timedelta
from paths import p, ensure

SCHEMA = """
CREATE TABLE IF NOT EXISTS kapitel(
  id INTEGER PRIMARY KEY, nr INTEGER UNIQUE, titel TEXT NOT NULL, thema TEXT DEFAULT '',
  hinweis TEXT DEFAULT '', datum TEXT, farbe TEXT);
CREATE TABLE IF NOT EXISTS eintrag(
  id INTEGER PRIMARY KEY, kapitel_id INTEGER NOT NULL REFERENCES kapitel(id) ON DELETE CASCADE,
  pos INTEGER DEFAULT 0, englisch TEXT NOT NULL, deutsch TEXT NOT NULL, aussprache TEXT DEFAULT '',
  beispiel_en TEXT DEFAULT '', beispiel_de TEXT DEFAULT '', art TEXT DEFAULT 'wort',
  norm_key TEXT NOT NULL UNIQUE, norm_beispiel TEXT DEFAULT '');
CREATE TABLE IF NOT EXISTS bild(
  id INTEGER PRIMARY KEY, kapitel_id INTEGER NOT NULL REFERENCES kapitel(id) ON DELETE CASCADE,
  dateiname TEXT NOT NULL, beschreibung TEXT DEFAULT '');
CREATE TABLE IF NOT EXISTS lernstand(
  eintrag_id INTEGER NOT NULL REFERENCES eintrag(id) ON DELETE CASCADE, richtung TEXT NOT NULL,
  status TEXT DEFAULT 'neu', richtig INTEGER DEFAULT 0, falsch INTEGER DEFAULT 0, naechster_termin TEXT,
  PRIMARY KEY(eintrag_id, richtung));
CREATE TABLE IF NOT EXISTS verlauf(
  id INTEGER PRIMARY KEY, zeit TEXT, eintrag_id INTEGER, richtung TEXT, richtig INTEGER, benutzer TEXT);
CREATE TABLE IF NOT EXISTS benutzer(id INTEGER PRIMARY KEY, name TEXT UNIQUE);
CREATE TABLE IF NOT EXISTS einstellung(key TEXT PRIMARY KEY, value TEXT);
"""

def norm(s):
    """Vergleichsschluessel: Kleinbuchstaben, ohne Satzzeichen, einfache Leerzeichen."""
    s = (s or "").lower().replace("’", "'")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", "", s)).strip()

def db_path():
    return p("vokabeln.db")

def connect(path=None):
    path = path or db_path()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA)
    if "stufe" not in [r[1] for r in conn.execute("PRAGMA table_info(lernstand)")]:
        conn.execute("ALTER TABLE lernstand ADD COLUMN stufe INTEGER DEFAULT 0")
    for tab, col, ddl in (("kapitel", "bereich", "TEXT DEFAULT 'eigen'"), ("kapitel", "buch", "TEXT DEFAULT ''"),
                          ("eintrag", "rubrik", "TEXT DEFAULT ''"), ("eintrag", "sprecher", "TEXT DEFAULT ''")):
        if col not in [r[1] for r in conn.execute("PRAGMA table_info(%s)" % tab)]:
            conn.execute("ALTER TABLE %s ADD COLUMN %s %s" % (tab, col, ddl))
    nb = conn.execute("SELECT COUNT(*) FROM benutzer").fetchone()[0]
    if nb == 0:
        conn.execute("INSERT INTO benutzer(name) VALUES('Benutzer')")            # neue, leere Installation
    elif conn.execute("SELECT COUNT(*) FROM benutzer WHERE name='Sigi'").fetchone()[0] == 0 and \
            conn.execute("SELECT COUNT(*) FROM benutzer WHERE name='Stefan'").fetchone()[0]:
        conn.execute("UPDATE benutzer SET name='Sigi' WHERE name='Stefan'")      # Umbenennung aus Version 1
    if nb == 0:
        conn.execute("INSERT OR IGNORE INTO benutzer(name) VALUES('Gast')")
    conn.commit()
    return conn

def add_chapter(conn, nr, titel, thema="", hinweis="", datum=None, farbe=None):
    row = conn.execute("SELECT id FROM kapitel WHERE nr=?", (nr,)).fetchone()
    if row:
        return row["id"]
    cur = conn.execute("INSERT INTO kapitel(nr,titel,thema,hinweis,datum,farbe) VALUES(?,?,?,?,?,?)",
                       (nr, titel, thema, hinweis, datum, farbe))
    return cur.lastrowid

def sentence_exists(conn, text):
    """Gibt (kapitel_nr, englisch) zurueck, wenn der Text schon als Eintrag oder Beispielsatz vorkommt."""
    k = norm(text)
    if not k:
        return None
    r = conn.execute("""SELECT k.nr AS nr, e.englisch AS en FROM eintrag e JOIN kapitel k ON k.id=e.kapitel_id
                        WHERE e.norm_key=? OR e.norm_beispiel=? LIMIT 1""", (k, k)).fetchone()
    return (r["nr"], r["en"]) if r else None

def add_entry(conn, kapitel_id, englisch, deutsch, aussprache="", beispiel_en="", beispiel_de="", art="wort", pos=0):
    """Legt einen Eintrag an. Gibt die ID zurueck oder None, wenn es den Satz schon gibt."""
    if sentence_exists(conn, englisch):
        return None
    if beispiel_en and sentence_exists(conn, beispiel_en):
        beispiel_en = beispiel_de = ""      # Beispielsatz waere doppelt: weglassen
    cur = conn.execute("""INSERT INTO eintrag(kapitel_id,pos,englisch,deutsch,aussprache,beispiel_en,beispiel_de,art,norm_key,norm_beispiel)
                          VALUES(?,?,?,?,?,?,?,?,?,?)""",
                       (kapitel_id, pos, englisch.strip(), deutsch.strip(), aussprache.strip(), beispiel_en.strip(),
                        beispiel_de.strip(), art, norm(englisch), norm(beispiel_en)))
    return cur.lastrowid

class Scope:
    """Welcher Bereich wird angezeigt? bereich 'eigen' (eigene Kapitel) oder 'sd' (Sprachduschen); optional Buch und Rubrik."""
    def __init__(self, bereich="eigen", buch=None, rubrik=None):
        self.bereich, self.buch, self.rubrik = bereich, buch, rubrik

EIGEN = Scope()

def chapters(conn, scope=EIGEN):
    sql = """SELECT k.*, (SELECT COUNT(*) FROM eintrag e WHERE e.kapitel_id=k.id%s) AS anzahl
             FROM kapitel k WHERE COALESCE(k.bereich,'eigen')=?""" % (" AND e.rubrik=?" if scope.rubrik else "")
    args = ([scope.rubrik] if scope.rubrik else []) + [scope.bereich]
    if scope.buch:
        sql += " AND k.buch=?"; args.append(scope.buch)
    return conn.execute(sql + " ORDER BY k.nr", args).fetchall()

def chapter_label(k):
    """Text fuer Auswahllisten: eigene Kapitel 'Nr  Titel', Sprachduschen 'Buch - Lektion ...'."""
    if k["bereich"] == "sd":
        return "%s · %s" % (k["buch"], k["titel"])
    return "%d  %s" % (k["nr"], k["titel"])

def entries(conn, kapitel_id, rubrik=None):
    if rubrik:
        return conn.execute("SELECT * FROM eintrag WHERE kapitel_id=? AND rubrik=? ORDER BY pos, id", (kapitel_id, rubrik)).fetchall()
    return conn.execute("SELECT * FROM eintrag WHERE kapitel_id=? ORDER BY pos, id", (kapitel_id,)).fetchall()

def get_setting(conn, key, default=None):
    r = conn.execute("SELECT value FROM einstellung WHERE key=?", (key,)).fetchone()
    return r["value"] if r else default

def set_setting(conn, key, value):
    conn.execute("INSERT INTO einstellung(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                 (key, str(value)))
    conn.commit()

def backup(conn):
    """Kopiert die Datenbank mit Datum nach sicherung\\. Gibt den Dateipfad zurueck."""
    conn.commit()
    ziel = os.path.join(ensure("sicherung"), "vokabeln_%s.db" % datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S"))
    dst = sqlite3.connect(ziel)
    conn.backup(dst)
    dst.close()
    return ziel


# ---- Benutzer (der Lernstand ist gemeinsam, der Name steht nur im Verlauf)
def users(conn):
    return [r["name"] for r in conn.execute("SELECT name FROM benutzer ORDER BY id")]

def add_user(conn, name):
    name = (name or "").strip()
    if not name or conn.execute("SELECT 1 FROM benutzer WHERE lower(name)=lower(?)", (name,)).fetchone():
        return False
    conn.execute("INSERT INTO benutzer(name) VALUES(?)", (name,)); conn.commit(); return True

def rename_user(conn, old, new):
    new = (new or "").strip()
    if not new or conn.execute("SELECT 1 FROM benutzer WHERE lower(name)=lower(?) AND name<>?", (new, old)).fetchone():
        return False
    conn.execute("UPDATE benutzer SET name=? WHERE name=?", (new, old))
    conn.execute("UPDATE verlauf SET benutzer=? WHERE benutzer=?", (new, old)); conn.commit(); return True

def delete_user(conn, name):
    if len(users(conn)) <= 1:
        return False
    conn.execute("DELETE FROM benutzer WHERE name=?", (name,)); conn.commit(); return True


# ---- Lernplan: Wiederholung nach 1, 3, 7 und 14 Tagen
INTERVALS = [1, 3, 7, 14]
RICHTUNGEN = ("en_de", "de_en", "hoeren")

def _today(today):
    return today or date.today()

def _scope_sql(scope, richtung=None):
    sql, args = " AND COALESCE(k.bereich,'eigen')=?", [scope.bereich]
    if scope.buch: sql += " AND k.buch=?"; args.append(scope.buch)
    if scope.rubrik: sql += " AND e.rubrik=?"; args.append(scope.rubrik)
    if scope.bereich != "eigen" and richtung != "hoeren": sql += " AND e.deutsch<>''"      # ohne Uebersetzung nur Hoeren
    return sql, args

def due_cards(conn, richtung, kapitel_id=None, limit=10, today=None, scope=EIGEN):
    """Faellige Karten zuerst (aelteste zuerst), danach neue Eintraege."""
    t = _today(today).isoformat()
    sql = """SELECT e.*, k.nr AS knr, l.naechster_termin AS termin, COALESCE(l.stufe,0) AS stufe
             FROM eintrag e JOIN kapitel k ON k.id=e.kapitel_id
             LEFT JOIN lernstand l ON l.eintrag_id=e.id AND l.richtung=?
             WHERE (l.eintrag_id IS NULL OR l.naechster_termin<=?)"""
    args = [richtung, t]
    if kapitel_id:
        sql += " AND e.kapitel_id=?"; args.append(kapitel_id)
    ss, sa = _scope_sql(scope, richtung); sql += ss; args += sa
    sql += " ORDER BY (l.eintrag_id IS NULL), l.naechster_termin, k.nr, e.pos, e.id"
    if limit:
        sql += " LIMIT ?"; args.append(limit)
    return conn.execute(sql, args).fetchall()

def answer(conn, eintrag_id, richtung, richtig, benutzer="", today=None):
    """Speichert das Ergebnis: richtig -> naechste Stufe, falsch -> zurueck auf Stufe 0 (heute wieder)."""
    d = _today(today)
    r = conn.execute("SELECT * FROM lernstand WHERE eintrag_id=? AND richtung=?", (eintrag_id, richtung)).fetchone()
    stufe = r["stufe"] if r else 0
    ok, bad = (r["richtig"], r["falsch"]) if r else (0, 0)
    if richtig:
        stufe = min(stufe + 1, len(INTERVALS)); ok += 1
        termin = (d + timedelta(days=INTERVALS[stufe - 1])).isoformat()
        status = "kann" if stufe >= 3 else "ueben"
    else:
        stufe = 0; bad += 1; termin = d.isoformat(); status = "ueben"
    conn.execute("""INSERT INTO lernstand(eintrag_id,richtung,status,richtig,falsch,naechster_termin,stufe) VALUES(?,?,?,?,?,?,?)
                    ON CONFLICT(eintrag_id,richtung) DO UPDATE SET status=excluded.status, richtig=excluded.richtig,
                    falsch=excluded.falsch, naechster_termin=excluded.naechster_termin, stufe=excluded.stufe""",
                 (eintrag_id, richtung, status, ok, bad, termin, stufe))
    conn.execute("INSERT INTO verlauf(zeit,eintrag_id,richtung,richtig,benutzer) VALUES(?,?,?,?,?)",
                 ("%sT%s" % (d.isoformat(), datetime.datetime.now().strftime("%H:%M:%S")), eintrag_id, richtung, int(bool(richtig)), benutzer))
    conn.commit()
    return status, termin

def streak(conn, today=None):
    """Anzahl Tage in Folge mit Lernen (heute oder gestern als Ende)."""
    d = _today(today)
    days = {r[0] for r in conn.execute("SELECT DISTINCT substr(zeit,1,10) FROM verlauf")}
    if d.isoformat() not in days:
        d = d - timedelta(days=1)
    n = 0
    while d.isoformat() in days:
        n += 1; d -= timedelta(days=1)
    return n

def stats(conn, richtung="en_de", today=None, scope=EIGEN):
    t = _today(today).isoformat()
    ss, sa = _scope_sql(scope, richtung)
    base = "FROM eintrag e JOIN kapitel k ON k.id=e.kapitel_id WHERE 1=1" + ss
    total = conn.execute("SELECT COUNT(*) " + base, sa).fetchone()[0]
    st = {r["status"]: r["n"] for r in conn.execute(
        "SELECT l.status AS status, COUNT(*) AS n FROM lernstand l JOIN eintrag e ON e.id=l.eintrag_id JOIN kapitel k ON k.id=e.kapitel_id "
        "WHERE l.richtung=?" + ss + " GROUP BY l.status", [richtung] + sa)}
    faellig = conn.execute("SELECT COUNT(*) FROM lernstand l JOIN eintrag e ON e.id=l.eintrag_id JOIN kapitel k ON k.id=e.kapitel_id "
                           "WHERE l.richtung=? AND l.naechster_termin<=?" + ss, [richtung, t] + sa).fetchone()[0]
    heute = conn.execute("SELECT COUNT(*) FROM verlauf v JOIN eintrag e ON e.id=v.eintrag_id JOIN kapitel k ON k.id=e.kapitel_id "
                         "WHERE substr(v.zeit,1,10)=?" + ss.replace("e.deutsch<>''", "1=1"), [t] + sa[:len(sa)]).fetchone()[0]
    per = []
    for k in chapters(conn, scope):
        n = conn.execute("SELECT COUNT(*) FROM eintrag e JOIN kapitel k ON k.id=e.kapitel_id WHERE e.kapitel_id=?" + ss, [k["id"]] + sa).fetchone()[0]
        c = {r["status"]: r["n"] for r in conn.execute(
            """SELECT l.status, COUNT(*) AS n FROM lernstand l JOIN eintrag e ON e.id=l.eintrag_id JOIN kapitel k ON k.id=e.kapitel_id
               WHERE l.richtung=? AND e.kapitel_id=?""" + ss + " GROUP BY l.status", [richtung, k["id"]] + sa)}
        sk = conn.execute("""SELECT COALESCE(SUM(l.stufe),0) FROM lernstand l JOIN eintrag e ON e.id=l.eintrag_id JOIN kapitel k ON k.id=e.kapitel_id
                             WHERE l.richtung=? AND e.kapitel_id=?""" + ss, [richtung, k["id"]] + sa).fetchone()[0]
        per.append((k["nr"], k["titel"], n, c.get("kann", 0), c.get("ueben", 0), round(100.0 * sk / (len(INTERVALS) * n)) if n else 0))
    stufen = [0] * (len(INTERVALS) + 1)
    for r in conn.execute("SELECT COALESCE(l.stufe,0) AS s, COUNT(*) AS n FROM lernstand l JOIN eintrag e ON e.id=l.eintrag_id JOIN kapitel k ON k.id=e.kapitel_id "
                          "WHERE l.richtung=?" + ss + " GROUP BY COALESCE(l.stufe,0)", [richtung] + sa):
        stufen[min(r["s"], len(INTERVALS))] = r["n"]
    summe = sum(i * c for i, c in enumerate(stufen))
    prozent = round(100.0 * summe / (len(INTERVALS) * total)) if total else 0
    return dict(total=total, kann=st.get("kann", 0), ueben=st.get("ueben", 0), neu=total - st.get("kann", 0) - st.get("ueben", 0),
                faellig=faellig, heute=heute, serie=streak(conn, today), kapitel=per, stufen=stufen, prozent=prozent)


# ---- Stufe 3: Kapitel und Eintraege bearbeiten, Bilder
def next_chapter_nr(conn):
    return (conn.execute("SELECT COALESCE(MAX(nr),0)+1 FROM kapitel WHERE COALESCE(bereich,'eigen')='eigen'").fetchone()[0])

def new_chapter(conn, titel, hinweis=""):
    nr = next_chapter_nr(conn)
    kid = add_chapter(conn, nr, titel.strip(), "", hinweis.strip(), date.today().isoformat())
    conn.commit(); return kid, nr

def update_chapter(conn, kid, titel, hinweis):
    conn.execute("UPDATE kapitel SET titel=?, hinweis=? WHERE id=?", (titel.strip(), hinweis.strip(), kid)); conn.commit()

def delete_chapter(conn, kid):
    for b in images(conn, kid):
        _remove_file(b["dateiname"])
    conn.execute("DELETE FROM kapitel WHERE id=?", (kid,)); conn.commit()

def add_new_entry(conn, kid, englisch, deutsch, aussprache="", beispiel_en="", beispiel_de=""):
    """Wie add_entry, aber meldet doppelte Saetze: (id, None) bei Erfolg, (None, (kapitel_nr, englisch)) bei Doppelung."""
    dup = sentence_exists(conn, englisch)
    if dup:
        return None, dup
    pos = conn.execute("SELECT COALESCE(MAX(pos),0)+1 FROM eintrag WHERE kapitel_id=?", (kid,)).fetchone()[0]
    art = "satz" if len(englisch.split()) > 3 else "wort"
    eid = add_entry(conn, kid, englisch, deutsch, aussprache, beispiel_en, beispiel_de, art, pos)
    conn.commit(); return eid, None

def update_entry(conn, eid, englisch, deutsch, aussprache, beispiel_en, beispiel_de):
    """Aendert einen Eintrag. Gibt (kapitel_nr, englisch) zurueck, wenn der neue Text bei einem ANDEREN Eintrag schon steht."""
    k = norm(englisch)
    r = conn.execute("SELECT k.nr AS nr, e.englisch AS en FROM eintrag e JOIN kapitel k ON k.id=e.kapitel_id "
                     "WHERE (e.norm_key=? OR e.norm_beispiel=?) AND e.id<>? LIMIT 1", (k, k, eid)).fetchone()
    if r:
        return (r["nr"], r["en"])
    conn.execute("UPDATE eintrag SET englisch=?, deutsch=?, aussprache=?, beispiel_en=?, beispiel_de=?, norm_key=?, norm_beispiel=? WHERE id=?",
                 (englisch.strip(), deutsch.strip(), aussprache.strip(), beispiel_en.strip(), beispiel_de.strip(), k, norm(beispiel_en), eid))
    conn.commit(); return None

def delete_entry(conn, eid):
    conn.execute("DELETE FROM eintrag WHERE id=?", (eid,)); conn.commit()

def images(conn, kid):
    return conn.execute("SELECT * FROM bild WHERE kapitel_id=? ORDER BY id", (kid,)).fetchall()

def add_image_file(conn, kid, src_path, beschreibung=""):
    """Kopiert eine Bilddatei in den Ordner bilder\\ und merkt sie sich."""
    ext = os.path.splitext(src_path)[1].lower() or ".png"
    name = "k%d_%s%s" % (kid, datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f"), ext)
    shutil.copy2(src_path, os.path.join(ensure("bilder"), name))
    conn.execute("INSERT INTO bild(kapitel_id,dateiname,beschreibung) VALUES(?,?,?)", (kid, name, beschreibung)); conn.commit()
    return name

def add_image_pixmap(conn, kid, pixmap):
    """Speichert ein Bild aus der Zwischenablage (QPixmap/QImage) als PNG."""
    name = "k%d_%s.png" % (kid, datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
    if not pixmap.save(os.path.join(ensure("bilder"), name), "PNG"):
        return None
    conn.execute("INSERT INTO bild(kapitel_id,dateiname,beschreibung) VALUES(?,?,?)", (kid, name, "")); conn.commit()
    return name

def _remove_file(name):
    try:
        os.remove(os.path.join(p("bilder"), name))
    except OSError:
        pass

def delete_image(conn, bid):
    r = conn.execute("SELECT dateiname FROM bild WHERE id=?", (bid,)).fetchone()
    if r:
        _remove_file(r["dateiname"])
    conn.execute("DELETE FROM bild WHERE id=?", (bid,)); conn.commit()

def set_image_text(conn, bid, text):
    conn.execute("UPDATE bild SET beschreibung=? WHERE id=?", (text, bid)); conn.commit()

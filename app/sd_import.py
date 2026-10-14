# Sprachduschen: liest daten\sprachduschen.json (aus den gekauften Begleitbuechern) in einen eigenen Bereich der Datenbank.
import json, os
import db
from paths import p

RUBRIKEN = [("vok", "Vokabeln"), ("dialog", "Dialog"), ("nach", "Nachsprechen")]

def json_path():
    return p("daten", "sprachduschen.json")

def has_data(conn):
    return conn.execute("SELECT COUNT(*) FROM kapitel WHERE bereich='sd'").fetchone()[0] > 0

def import_sd(conn, path=None):
    """Legt je Lektion ein Kapitel im Bereich 'sd' an. Gibt (Buecher, Lektionen, Eintraege) zurueck. Mehrfaches Einlesen ist ungefaehrlich."""
    path = path or json_path()
    data = json.load(open(path, encoding="utf8"))
    nb = nl = ne = 0
    for b in data:
        nb += 1
        for l in b["lektionen"]:
            nr = 1000 * b["nr"] + l["nr"]
            if conn.execute("SELECT 1 FROM kapitel WHERE nr=?", (nr,)).fetchone():
                continue
            titel = "Lektion %d: %s" % (l["nr"], l["titel"] or l.get("titel_de") or "")
            hinweis = (l.get("titel_de") or "")
            cur = conn.execute("INSERT INTO kapitel(nr,titel,thema,hinweis,datum,bereich,buch) VALUES(?,?,?,?,?,?,?)",
                               (nr, titel, "", hinweis, None, "sd", b["buch"]))
            kid = cur.lastrowid; nl += 1; pos = 0; seen = set()
            def add(rubrik, spr, en, de, art):
                nonlocal pos, ne
                key = "sd:%d:%s:%s:%s" % (kid, rubrik, db.norm(en), db.norm(de)[:40])
                if not en.strip() or key in seen: return
                seen.add(key); pos += 1; ne += 1
                conn.execute("""INSERT INTO eintrag(kapitel_id,pos,englisch,deutsch,aussprache,beispiel_en,beispiel_de,art,norm_key,norm_beispiel,rubrik,sprecher)
                                VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""", (kid, pos, en.strip(), de.strip(), "", "", "", art, key, "", rubrik, spr))
            for en, de in l["vok"]:
                add("vok", "", en, de, "wort" if len(en.split()) <= 3 else "satz")
            for spr, en, de in l["dialog"]:
                add("dialog", spr, en, de, "dialog")
            for en, de in l["nach"]:
                add("nach", "", en, de, "satz")
    conn.commit()
    return nb, nl, ne

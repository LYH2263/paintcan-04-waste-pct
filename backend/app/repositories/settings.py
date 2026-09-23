import sqlite3
def get_map(conn): return {r["key"]: r["value"] for r in conn.execute("SELECT * FROM settings").fetchall()}
def coverage_coats(conn):
    m = get_map(conn)
    return float(m.get("coverage", "8")), int(m.get("coats", "2"))
def waste_defaults(conn):
    """返回 (默认损耗百分点, 损耗上限百分点)。"""
    m = get_map(conn)
    return float(m.get("waste_pct", "0")), float(m.get("waste_max_pct", "20"))
def upsert(conn, key, value):
    conn.execute(
        "INSERT INTO settings(key,value) VALUES(?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, str(value)))
    conn.commit()

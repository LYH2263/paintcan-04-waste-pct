import sqlite3
def get_map(conn): return {r["key"]: r["value"] for r in conn.execute("SELECT * FROM settings").fetchall()}
def coverage_coats(conn):
    m = get_map(conn)
    return float(m.get("coverage", "8")), int(m.get("coats", "2"))
def waste_defaults(conn):
    m = get_map(conn)
    return float(m.get("waste_pct", "0")), float(m.get("waste_max_pct", "20"))
def set_values(conn, values):
    for k, v in values.items():
        conn.execute("INSERT INTO settings(key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (k, str(v)))
    conn.commit()

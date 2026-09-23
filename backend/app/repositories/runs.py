import json, sqlite3
from datetime import datetime, timezone
def insert(conn, kind, payload, result, room_id=None):
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute("INSERT INTO calc_runs(kind,room_id,input_json,result_json,created_at) VALUES (?,?,?,?,?)",
        (kind, room_id, json.dumps(payload, ensure_ascii=False), json.dumps(result, ensure_ascii=False), now))
    conn.commit(); return int(cur.lastrowid)
def list_recent(conn, limit=50):
    return [dict(r) for r in conn.execute("SELECT * FROM calc_runs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]
def get(conn, run_id):
    row = conn.execute("SELECT * FROM calc_runs WHERE id=?", (run_id,)).fetchone()
    if not row: return None
    item = dict(row)
    # 解析钉选的输入与结果：应付升数/损耗固化在 result_json 中，不随后续设置变化
    item["input"] = json.loads(item["input_json"] or "{}")
    item["result"] = json.loads(item["result_json"] or "{}")
    # 兼容改造前旧条：无损耗字段即视为 0 损耗，应付升数取当时钉选的基础升数，不据当前设置重算
    item["chargeable_liters"] = item["result"].get("chargeable_liters", item["result"].get("liters"))
    item["waste_pct"] = item["result"].get("waste_pct", item["input"].get("waste_pct", 0))
    item["liters"] = item["result"].get("liters")
    return item

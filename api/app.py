from flask import Flask, request, jsonify
import sqlite3, json, subprocess
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "db" / "resume_ai.db"
SCHEMA_PATH = BASE_DIR / "db" / "schema.sql"
PREVIEW_SCRIPT = BASE_DIR / "generate_template_preview.py"
PREVIEWS_DIR = BASE_DIR / "templates" / "previews"

# ── DB helpers ─────────────────────────────────────────────────────────────

def get_db():
    db_path = Path(DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    with open(Path(SCHEMA_PATH), encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

def generate_ticket():
    today = datetime.now().strftime("%Y%m%d")
    conn  = get_db()
    count = conn.execute(
        "SELECT COUNT(*) FROM orders WHERE ticket_no LIKE ?",
        (f"RES-{today}-%",)
    ).fetchone()[0]
    conn.close()
    return f"RES-{today}-{count + 1:04d}"

# ── Session endpoints ──────────────────────────────────────────────────────

@app.route("/session/<phone>", methods=["GET"])
def get_session(phone):
    """Return full session. collected_data is returned as a parsed object."""
    conn = get_db()
    row  = conn.execute("SELECT * FROM sessions WHERE phone_number=?", (phone,)).fetchone()
    conn.close()
    if not row:
        return jsonify({}), 200
    data = dict(row)
    try:
        data["collected_data"] = json.loads(data.get("collected_data") or "{}")
    except Exception:
        data["collected_data"] = {}
    return jsonify(data), 200


@app.route("/session", methods=["POST"])
def create_session():
    """Create a new session (called when a new user is detected)."""
    body = request.json or request.form.to_dict()
    phone = body.get("phone_number")
    if not phone:
        return jsonify({"ok": False, "error": "phone_number required"}), 400
    conn = get_db()
    conn.execute("""
        INSERT INTO sessions (phone_number, current_step, chosen_language, collected_data, last_active, status)
        VALUES (?, 'new', '', '{}', ?, 'active')
        ON CONFLICT(phone_number) DO NOTHING
    """, (phone, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@app.route("/session/<phone>/step", methods=["POST"])
def update_step(phone):
    """Update current_step and/or chosen_language."""
    body   = request.json or {}
    fields, vals = [], []
    if "current_step" in body:
        fields.append("current_step=?");    vals.append(body["current_step"])
    if "chosen_language" in body:
        fields.append("chosen_language=?"); vals.append(body["chosen_language"])
    fields.append("last_active=?"); vals.append(datetime.now().isoformat())
    vals.append(phone)
    conn = get_db()
    conn.execute(f"UPDATE sessions SET {', '.join(fields)} WHERE phone_number=?", vals)
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@app.route("/session/<phone>/data", methods=["POST"])
def update_collected_data(phone):
    """Merge incoming dict into collected_data. Null/empty values are skipped."""
    incoming = request.json or {}
    conn = get_db()
    row  = conn.execute("SELECT collected_data FROM sessions WHERE phone_number=?", (phone,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"ok": False, "error": "session not found"}), 404
    try:
        existing = json.loads(row["collected_data"] or "{}")
    except Exception:
        existing = {}
    for k, v in incoming.items():
        if v is not None and v != "":
            existing[k] = v
    conn.execute(
        "UPDATE sessions SET collected_data=?, last_active=? WHERE phone_number=?",
        (json.dumps(existing, ensure_ascii=False), datetime.now().isoformat(), phone)
    )
    conn.commit()
    conn.close()
    return jsonify({"ok": True, "collected_data": existing})


@app.route("/session/<phone>", methods=["DELETE"])
def delete_session(phone):
    conn = get_db()
    conn.execute("DELETE FROM sessions WHERE phone_number=?", (phone,))
    conn.execute("DELETE FROM conversations WHERE phone_number=?", (phone,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

# ── Conversation history ───────────────────────────────────────────────────

@app.route("/conversations/<phone>", methods=["GET"])
def get_conversations(phone):
    limit = request.args.get("limit", 10, type=int)
    conn  = get_db()
    rows  = conn.execute(
        "SELECT role, content, timestamp FROM conversations WHERE phone_number=? ORDER BY id DESC LIMIT ?",
        (phone, limit)
    ).fetchall()
    conn.close()
    return jsonify({"history": [dict(r) for r in reversed(rows)]})


@app.route("/conversations", methods=["POST"])
def save_conversation():
    body = request.json or {}
    conn = get_db()
    conn.execute(
        "INSERT INTO conversations (phone_number, role, content, timestamp) VALUES (?, ?, ?, ?)",
        (body["phone_number"], body["role"], body["content"], datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

# ── Orders ─────────────────────────────────────────────────────────────────

@app.route("/orders", methods=["POST"])
def create_order():
    body       = request.json or {}
    ticket_no  = generate_ticket()
    conn       = get_db()
    conn.execute(
        "INSERT INTO orders (ticket_no, phone_number, customer_name, service, amount, details, status, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (ticket_no, body.get("phone_number"), body.get("customer_name"),
         body.get("service"), body.get("amount", 0),
         json.dumps(body.get("details", {}), ensure_ascii=False),
         "pending_payment", datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    return jsonify({"ok": True, "ticket_no": ticket_no})


@app.route("/orders/<phone>", methods=["GET"])
def get_orders(phone):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM orders WHERE phone_number=? ORDER BY id DESC", (phone,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/orders/ticket/<ticket_no>", methods=["GET"])
def get_order_by_ticket(ticket_no):
    conn = get_db()
    row  = conn.execute("SELECT * FROM orders WHERE ticket_no=?", (ticket_no,)).fetchone()
    conn.close()
    return (jsonify(dict(row)), 200) if row else (jsonify({"error": "not found"}), 404)


@app.route("/orders/ticket/<ticket_no>/status", methods=["POST"])
def update_order_status(ticket_no):
    body   = request.json or {}
    status = body.get("status", "paid")
    conn   = get_db()
    conn.execute("UPDATE orders SET status=? WHERE ticket_no=?", (status, ticket_no))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

# ── Feedback ───────────────────────────────────────────────────────────────

@app.route("/feedback", methods=["POST"])
def add_feedback():
    body = request.json or {}
    conn = get_db()
    conn.execute(
        "INSERT INTO feedback (ticket_no, phone_number, rating, comment, created_at) VALUES (?,?,?,?,?)",
        (body.get("ticket_no",""), body["phone_number"],
         body.get("rating", 0), body.get("comment",""),
         datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

# ── Template preview ───────────────────────────────────────────────────────

@app.route("/generate-preview", methods=["POST"])
def generate_preview():
    body   = request.json or {}
    layout = body.get("layout", "A")
    colour = body.get("colour", "1")
    style  = body.get("style",  "I")
    phone  = body.get("phone",  "unknown")
    previews_dir = Path(PREVIEWS_DIR)
    previews_dir.mkdir(parents=True, exist_ok=True)
    output_path = previews_dir / f"{phone}_{layout}{colour}{style}.png"
    result = subprocess.run(
        ["python", PREVIEW_SCRIPT,
         "--layout", layout, "--colour", colour,
         "--style",  style,  "--output", output_path],
        capture_output=True, timeout=30
    )
    if result.returncode != 0:
        return jsonify({"ok": False, "error": result.stderr.decode()}), 500
    return jsonify({"ok": True, "imagePath": output_path})

# ── SOP file reader (for backwards compatibility) ──────────────────────────

@app.route("/sop", methods=["GET"])
def read_sop():
    path = request.args.get("path", "")
    if not path:
        return jsonify({"ok": False, "error": "No path"}), 400
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return jsonify({"ok": True, "sop": {"sop_content": content}})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

# ── Stale sessions ─────────────────────────────────────────────────────────

@app.route("/sessions/stale", methods=["GET"])
def stale_sessions():
    hours = request.args.get("hours", 1, type=int)
    conn  = get_db()
    rows  = conn.execute("""
        SELECT phone_number, current_step, last_active
        FROM sessions
        WHERE status='active'
          AND current_step NOT IN ('new','done')
          AND datetime(last_active) < datetime('now', ? || ' hours')
    """, (f"-{hours}",)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# ── Entrypoint ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5051, debug=False)

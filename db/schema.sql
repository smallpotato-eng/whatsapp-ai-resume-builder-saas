-- ============================================================
-- Resume-AI Schema (Micro-LLM + State Machine Architecture)
-- ============================================================

CREATE TABLE IF NOT EXISTS sessions (
  phone_number    TEXT PRIMARY KEY,
  current_step    TEXT    DEFAULT 'new',
  chosen_language TEXT    DEFAULT '',
  collected_data  TEXT    DEFAULT '{}',
  last_active     TEXT,
  status          TEXT    DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS conversations (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  phone_number TEXT,
  role         TEXT,
  content      TEXT,
  timestamp    TEXT
);

CREATE TABLE IF NOT EXISTS orders (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  ticket_no     TEXT UNIQUE,
  phone_number  TEXT,
  customer_name TEXT,
  service       TEXT,
  amount        REAL,
  details       TEXT,
  status        TEXT DEFAULT 'pending_payment',
  created_at    TEXT
);

CREATE TABLE IF NOT EXISTS feedback (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  ticket_no    TEXT,
  phone_number TEXT,
  rating       INTEGER,
  comment      TEXT,
  created_at   TEXT
);

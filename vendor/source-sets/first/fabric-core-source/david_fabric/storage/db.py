import sqlite3
import json
from pathlib import Path
from david_fabric.core.config import settings

def _connect():
    Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = _connect()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS goals (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        objective TEXT NOT NULL,
        project_id TEXT,
        context_json TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS plans (
        goal_id TEXT PRIMARY KEY,
        plan_json TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS runs (
        id TEXT PRIMARY KEY,
        goal_id TEXT NOT NULL,
        status TEXT NOT NULL,
        approved INTEGER NOT NULL,
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT,
        event_type TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)
    conn.commit()
    conn.close()

def execute(sql, params=()):
    conn = _connect()
    cur = conn.execute(sql, params)
    conn.commit()
    rows = cur.fetchall()
    conn.close()
    return rows

def save_goal(goal):
    execute(
        "INSERT INTO goals VALUES (?,?,?,?,?,?,?)",
        (goal.id, goal.title, goal.objective, goal.project_id,
         json.dumps(goal.context), goal.status, goal.created_at)
    )

def get_goal(goal_id):
    rows = execute("SELECT * FROM goals WHERE id=?", (goal_id,))
    if not rows:
        return None
    r = rows[0]
    return dict(r)

def save_plan(plan):
    execute(
        "INSERT OR REPLACE INTO plans VALUES (?,?,datetime('now'))",
        (plan.goal_id, plan.model_dump_json())
    )

def get_plan(goal_id):
    rows = execute("SELECT plan_json FROM plans WHERE goal_id=?", (goal_id,))
    return json.loads(rows[0]["plan_json"]) if rows else None

def save_run(run):
    execute(
        "INSERT INTO runs VALUES (?,?,?,?,?)",
        (run.id, run.goal_id, run.status, int(run.approved), run.created_at)
    )

def get_run(run_id):
    rows = execute("SELECT * FROM runs WHERE id=?", (run_id,))
    return dict(rows[0]) if rows else None

def add_event(run_id, event_type, payload):
    execute(
        "INSERT INTO events(run_id,event_type,payload_json,created_at) VALUES (?,?,?,datetime('now'))",
        (run_id, event_type, json.dumps(payload))
    )

def get_events(run_id):
    return [dict(x) for x in execute(
        "SELECT * FROM events WHERE run_id=? ORDER BY id", (run_id,)
    )]

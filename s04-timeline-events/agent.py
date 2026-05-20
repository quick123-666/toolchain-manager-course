"""
s04: Timeline Events — 时间线记录与查询
Motto: 做过的每件事都有迹可查

新增: timeline_events 表 + 6种事件类型自动记录。
"""

import sqlite3, datetime

DB = "projects.db"

conn = sqlite3.connect(DB)
conn.executescript("""
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY, name TEXT, description TEXT, phase TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS milestones (
    id TEXT PRIMARY KEY, project_id TEXT, title TEXT, status TEXT DEFAULT 'open',
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY, project_id TEXT, milestone_id TEXT,
    title TEXT, status TEXT DEFAULT 'todo', priority TEXT DEFAULT 'medium',
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (milestone_id) REFERENCES milestones(id)
);
CREATE TABLE IF NOT EXISTS timeline_events (
    id TEXT PRIMARY KEY,
    project_id TEXT, milestone_id TEXT, task_id TEXT,
    event_type TEXT, category TEXT, title TEXT, description TEXT,
    source TEXT DEFAULT 'pm_system',
    priority TEXT DEFAULT 'P2',
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (milestone_id) REFERENCES milestones(id),
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);
""")
conn.commit()

# ── 自动事件记录 ───────────────────────────────────────────
EVENT_MAP = {
    "project_created":   {"type": "BUSINESS",   "cat": "project_created",   "prio": "P1"},
    "milestone_created": {"type": "TECHNICAL",  "cat": "milestone_created", "prio": "P2"},
    "milestone_completed":{"type":"TECHNICAL",  "cat": "milestone_completed","prio": "P2"},
    "task_created":      {"type": "TECHNICAL",  "cat": "task_created",      "prio": "P3"},
    "task_done":         {"type": "TECHNICAL",   "cat": "task_done",         "prio": "P3"},
    "health_warning":    {"type": "TECHNICAL",   "cat": "health_warning",    "prio": "P1"},
}

def record_event(event_key, project_id, milestone_id=None, task_id=None, title="", description=""):
    meta = EVENT_MAP.get(event_key, {"type": "TECHNICAL", "cat": event_key, "prio": "P2"})
    eid = f"evt_{conn.execute('SELECT COUNT(*)+1 FROM timeline_events').fetchone()[0]:06d}"
    conn.execute("""
        INSERT INTO timeline_events
        (id,project_id,milestone_id,task_id,event_type,category,title,description,source,priority)
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (eid, project_id, milestone_id, task_id,
         meta["type"], meta["cat"], title, description, "pm_system", meta["prio"]))
    conn.commit()
    return f"[{eid}] {event_key}: {title}"

def get_timeline(project_id):
    rows = conn.execute("""
        SELECT id,category,title,priority,event_type,created_at
        FROM timeline_events WHERE project_id=? ORDER BY created_at DESC
    """, (project_id,)).fetchall()
    if not rows: return f"项目 {project_id} 暂无时间线记录"
    PRIO_EMOJI = {"P0": "🔴", "P1": "🟠", "P2": "🟡", "P3": "⚪"}
    lines = [f"=== 项目 {project_id} 时间线 ==="]
    for r in rows:
        emoji = PRIO_EMOJI.get(r[3], "⚪")
        date = r[5].split(".")[0].replace("T", " ")
        lines.append(f"{emoji} [{r[0]}] {date} | {r[1]} | {r[2]}")
    return "\n".join(lines)

# ── 模拟：自动触发事件 ─────────────────────────────────────
conn.execute("INSERT OR IGNORE INTO projects (id,name,phase) VALUES ('proj_0001','agent-harness-course','production')")
conn.execute("INSERT OR IGNORE INTO milestones (id,project_id,title) VALUES ('ms_0001','proj_0001','上线v1')")
conn.execute("INSERT OR IGNORE INTO tasks (id,project_id,milestone_id,title,status) VALUES ('task_0001','proj_0001','ms_0001','写代码','done')")
conn.commit()

events = [
    ("project_created",   "proj_0001", None, None, "agent-harness-course 上线", "新项目创建"),
    ("milestone_created", "proj_0001", "ms_0001", None, "上线v1", "里程碑创建"),
    ("task_created",      "proj_0001", "ms_0001", "task_0001", "写代码", "任务创建"),
    ("task_done",         "proj_0001", "ms_0001", "task_0001", "写代码完成", "任务完成"),
    ("health_warning",    "proj_0001", None, None, "健康度低于70%", "健康预警"),
]

print("=== s04: Timeline Events ===\n")
for ev in events:
    result = record_event(*ev)
    print(f"  记录: {result}\n")

print("\n--- 时间线查询 ---")
print(get_timeline("proj_0001"))

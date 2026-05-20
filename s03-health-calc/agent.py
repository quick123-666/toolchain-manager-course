"""
s03: Health Calculation — 健康度自动计算
Motto: 数字告诉你哪里要救火

新增: health_score() 函数，按任务完成率/里程碑进度/阻塞任务计算健康度。
"""

import sqlite3

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
""")
conn.commit()

# ── 健康度计算 ─────────────────────────────────────────────
def health_score(project_id):
    """
    三维健康度：
    - 任务完成率 (40%): done / total
    - 里程碑达成率 (40%): closed / total
    - 阻塞惩罚 (20%): -10 per blocked task
    """
    total_tasks = conn.execute("SELECT COUNT(*) FROM tasks WHERE project_id=?", (project_id,)).fetchone()[0]
    done_tasks  = conn.execute("SELECT COUNT(*) FROM tasks WHERE project_id=? AND status='done'", (project_id,)).fetchone()[0]
    total_ms    = conn.execute("SELECT COUNT(*) FROM milestones WHERE project_id=?", (project_id,)).fetchone()[0]
    closed_ms   = conn.execute("SELECT COUNT(*) WHERE project_id=? AND status='completed'", (project_id,)).fetchone()[0]
    blocked     = conn.execute("SELECT COUNT(*) FROM tasks WHERE project_id=? AND status='blocked'", (project_id,)).fetchone()[0]

    task_score = (done_tasks / total_tasks * 100) if total_tasks else 50
    ms_score   = (closed_ms  / total_ms   * 100) if total_ms   else 50
    block_pen  = blocked * 10

    raw = task_score * 0.4 + ms_score * 0.4 - block_pen
    return max(0, min(100, round(raw, 1)))

def get_health_report(project_id):
    p = conn.execute("SELECT id,name,phase FROM projects WHERE id=?", (project_id,)).fetchone()
    if not p: return f"项目 {project_id} 不存在"
    score = health_score(project_id)
    total = conn.execute("SELECT COUNT(*) FROM tasks WHERE project_id=?", (project_id,)).fetchone()[0]
    done  = conn.execute("SELECT COUNT(*) FROM tasks WHERE project_id=? AND status='done'", (project_id,)).fetchone()[0]
    blocked = conn.execute("SELECT COUNT(*) FROM tasks WHERE project_id=? AND status='blocked'", (project_id,)).fetchone()[0]
    blocked_list = conn.execute("SELECT id,title FROM tasks WHERE project_id=? AND status='blocked'", (project_id,)).fetchall()
    health_bar = "█" * int(score/10) + "░" * (10 - int(score/10))
    emoji = "🟢" if score >= 70 else "🟡" if score >= 40 else "🔴"
    lines = [
        f"{emoji} 项目 [{p[0]}] {p[1]} | phase={p[2]}",
        f"健康度: {health_bar} {score}/100",
        f"任务: {done}/{total} 完成 | 🔴 阻塞: {blocked}",
    ]
    if blocked_list:
        lines.append("阻塞任务:")
        for tid, title in blocked_list:
            lines.append(f"  [{tid}] {title}")
    return "\n".join(lines)

# ── 演示数据 ──────────────────────────────────────────────
conn.execute("INSERT OR IGNORE INTO projects (id,name,phase) VALUES ('proj_0001','agent-harness-course','production')")
conn.execute("INSERT OR IGNORE INTO milestones (id,project_id,title,status) VALUES ('ms_0001','proj_0001','上线v1','open')")
conn.execute("INSERT OR IGNORE INTO milestones (id,project_id,title,status) VALUES ('ms_0002','proj_0001','上线v2','completed')")
conn.execute("INSERT OR IGNORE INTO tasks (id,project_id,milestone_id,title,status) VALUES ('task_0001','proj_0001','ms_0001','写代码','done')")
conn.execute("INSERT OR IGNORE INTO tasks (id,project_id,milestone_id,title,status) VALUES ('task_0002','proj_0001','ms_0001','写文档','done')")
conn.execute("INSERT OR IGNORE INTO tasks (id,project_id,milestone_id,title,status) VALUES ('task_0003','proj_0001','ms_0001','测试','in_progress')")
conn.execute("INSERT OR IGNORE INTO tasks (id,project_id,milestone_id,title,status) VALUES ('task_0004','proj_0001','ms_0001','部署','blocked')")
conn.execute("INSERT OR IGNORE INTO tasks (id,project_id,milestone_id,title,status) VALUES ('task_0005','proj_0001','ms_0001','监控','todo')")
conn.commit()

# ── 工具注册 ──────────────────────────────────────────────
def _get_health(args):
    pid = args.get("project_id", "proj_0001")
    return get_health_report(pid)

TOOL_HANDLERS = {"get_health": _get_health}

# ── 运行 ──────────────────────────────────────────────────
def run():
    print("=== s03: Health Calculation ===\n")
    result = _get_health({"project_id": "proj_0001"})
    print(result)

if __name__ == "__main__":
    run()

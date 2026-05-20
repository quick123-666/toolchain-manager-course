"""
s02: Tasks & Status — SQLite 持久化
Motto: 没有任务的里程碑是空的

新增: tasks 表 + SQLite 持久化，_next_id 从数据库读。
其他工具（projects/milestones）复用 s01 接口，数据落地。
"""

import sqlite3, os

DB = "projects.db"

# ── 建表 ────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS projects (
        id TEXT PRIMARY KEY,
        name TEXT, description TEXT, phase TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS milestones (
        id TEXT PRIMARY KEY,
        project_id TEXT, title TEXT, status TEXT DEFAULT 'open',
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (project_id) REFERENCES projects(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        project_id TEXT, milestone_id TEXT,
        title TEXT, status TEXT DEFAULT 'todo',
        priority TEXT DEFAULT 'medium',
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (project_id) REFERENCES projects(id),
        FOREIGN KEY (milestone_id) REFERENCES milestones(id)
    )""")
    conn.commit()
    return conn

# ── 持久化状态 ─────────────────────────────────────────────
conn = init_db()

_next_proj_id = conn.execute("SELECT IFNULL(MAX(CAST(SUBSTR(id,6) AS INT)), 0) + 1 FROM projects").fetchone()[0]
_next_ms_id = conn.execute("SELECT IFNULL(MAX(CAST(SUBSTR(id,4) AS INT)), 0) + 1 FROM milestones").fetchone()[0]
_next_task_id = conn.execute("SELECT IFNULL(MAX(CAST(SUBSTR(id,5) AS INT)), 0) + 1 FROM tasks").fetchone()[0]

# ── 工具实现 ───────────────────────────────────────────────
def _register_project(args):
    global _next_proj_id
    name, desc, phase = args.get("name"), args.get("description",""), args.get("phase","planning")
    pid = f"proj_{_next_proj_id:04d}"
    conn.execute("INSERT INTO projects (id,name,description,phase) VALUES (?,?,?,?)", (pid,name,desc,phase))
    conn.commit()
    _next_proj_id += 1
    return f"项目 [{pid}] {name} 创建成功，phase={phase}"

def _list_projects(args):
    rows = conn.execute("SELECT id,name,phase FROM projects").fetchall()
    if not rows: return "暂无项目"
    return "\n".join([f"[{r[0]}] {r[1]} | phase={r[2]}" for r in rows])

def _get_project(args):
    pid = args.get("id")
    p = conn.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone()
    if not p: return f"项目 {pid} 不存在"
    ms = conn.execute("SELECT id,title,status FROM milestones WHERE project_id=?", (pid,)).fetchall()
    ts = conn.execute("SELECT id,title,status,priority FROM tasks WHERE project_id=?", (pid,)).fetchall()
    ms_lines = "\n".join([f"  [{r[0]}] {r[1]} | {r[2]}" for r in ms]) or "  (无)"
    ts_lines = "\n".join([f"  [{r[0]}] {r[1]} | {r[2]} | {r[3]}" for r in ts]) or "  (无)"
    return f"[{p[0]}] {p[1]}\n描述: {p[2]}\nphase: {p[3]}\n里程碑:\n{ms_lines}\n任务:\n{ts_lines}"

def _create_milestone(args):
    global _next_ms_id
    pid, title = args.get("project_id"), args.get("title")
    mid = f"ms_{_next_ms_id:04d}"
    conn.execute("INSERT INTO milestones (id,project_id,title) VALUES (?,?,?)", (mid,pid,title))
    conn.commit()
    _next_ms_id += 1
    return f"里程碑 [{mid}] {title} 创建成功"

def _create_task(args):
    global _next_task_id
    pid, mid, title = args.get("project_id"), args.get("milestone_id"), args.get("title")
    tid = f"task_{_next_task_id:04d}"
    conn.execute("INSERT INTO tasks (id,project_id,milestone_id,title) VALUES (?,?,?,?)",
                 (tid, pid, mid, title))
    conn.commit()
    _next_task_id += 1
    return f"任务 [{tid}] {title} 创建成功"

def _list_tasks(args):
    rows = conn.execute("SELECT id,title,status,priority,milestone_id FROM tasks").fetchall()
    if not rows: return "暂无任务"
    return "\n".join([f"[{r[0]}] {r[1]} | status={r[2]} | priority={r[3]} | ms={r[4]}" for r in rows])

def _update_task_status(args):
    tid, status = args.get("id"), args.get("status")
    valid = ("todo","in_progress","in_review","done","cancelled","blocked")
    if status not in valid: return f"status 必须是 {valid} 之一"
    conn.execute("UPDATE tasks SET status=? WHERE id=?", (status,tid))
    conn.commit()
    return f"任务 {tid} → {status}"

# ── LLM 模拟 ────────────────────────────────────────────────
MESSAGES = [{"role":"system","content":"任务管理工具: create_task, list_tasks, update_task_status"}]
TOOL_CALLS = [
    {"name":"register_project","args":{"name":"agent-harness-course","description":"Harness教学","phase":"production"}},
    {"name":"create_milestone","args":{"project_id":"proj_0001","title":"上线v1"}},
    {"name":"create_task","args":{"project_id":"proj_0001","milestone_id":"ms_0001","title":"写s01代码"}},
    {"name":"create_task","args":{"project_id":"proj_0001","milestone_id":"ms_0001","title":"写s01文档"}},
    {"name":"update_task_status","args":{"id":"task_0001","status":"in_progress"}},
    {"name":"list_tasks","args":{}},
    {"name":"get_project","args":{"id":"proj_0001"}},
]

def call_llm(messages):
    idx = len([m for m in messages if m.get("role")=="tool"])
    if idx < len(TOOL_CALLS):
        tc = TOOL_CALLS[idx]
        return {"role":"assistant","tool_use":tc["name"],"content":f'调用: {tc["name"]}'}
    return {"role":"assistant","tool_use":None,"content":"done"}

def run():
    print("=== s02: Tasks & SQLite ===")
    idx=0
    while True:
        inp = input("按回车继续(Q退出): ")
        if inp.strip().upper()=="Q": break
        resp = call_llm(MESSAGES)
        MESSAGES.append(resp)
        if not resp.get("tool_use"):
            print(f"\n完成: {resp['content']}\n"); break
        tc = TOOL_CALLS[idx]
        handlers = {"register_project":_register_project,"create_milestone":_create_milestone,
                     "create_task":_create_task,"list_tasks":_list_tasks,
                     "update_task_status":_update_task_status,"get_project":_get_project,
                     "list_projects":_list_projects}
        result = handlers[tc["name"]](tc["args"])
        MESSAGES.append({"role":"tool","content":result})
        print(f"\n[{idx+1}] {tc['name']}\n  → {result}\n")
        idx+=1
        if idx>=len(TOOL_CALLS): break

if __name__=="__main__":
    run()

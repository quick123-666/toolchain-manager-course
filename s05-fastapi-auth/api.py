"""
s05: FastAPI + Auth — REST API + 多 Key 认证
Motto: 服务可复用，前端解耦

新增:
- FastAPI 服务，端口 18901
- API Key 认证（apikey.py）
- CRUD 路由：/projects, /milestones, /tasks, /timeline
"""

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3, datetime

DB = "projects.db"

# ── 建表 ─────────────────────────────────────────────────
conn = sqlite3.connect(DB, check_same_thread=False)
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
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS timeline_events (
    id TEXT PRIMARY KEY, project_id TEXT, milestone_id TEXT, task_id TEXT,
    event_type TEXT, category TEXT, title TEXT, description TEXT,
    source TEXT DEFAULT 'pm_system', priority TEXT DEFAULT 'P2',
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS api_keys (
    id TEXT PRIMARY KEY, key_hash TEXT UNIQUE, name TEXT,
    role TEXT DEFAULT 'viewer', created_at TEXT DEFAULT (datetime('now'))
);
""")
conn.commit()

app = FastAPI(title="Project Manager API", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# ── Auth ─────────────────────────────────────────────────
KEYS = {
    "pfb_admin_a3f8b2c1d9e4f7a6b8c3d2e1f9a8b7c6": {"name": "admin", "role": "admin"},
    "pfb_viewer_1234567890abcdef": {"name": "viewer", "role": "viewer"},
}

def verify_key(x_api_key: str = Header(None)):
    if x_api_key not in KEYS:
        raise HTTPException(401, "Invalid API Key")
    return KEYS[x_api_key]

def require_admin(key=Depends(verify_key)):
    if key["role"] != "admin":
        raise HTTPException(403, "Admin only")
    return key

# ── Models ───────────────────────────────────────────────
class ProjectIn(BaseModel):
    name: str; description: str = ""; phase: str = "planning"

class MilestoneIn(BaseModel):
    project_id: str; title: str

class TaskIn(BaseModel):
    project_id: str; milestone_id: str; title: str; priority: str = "medium"

# ── Routes ────────────────────────────────────────────────
@app.get("/projects")
def list_projects(key=Depends(verify_key)):
    rows = conn.execute("SELECT id,name,phase,created_at FROM projects").fetchall()
    return [{"id":r[0],"name":r[1],"phase":r[2],"created_at":r[3]} for r in rows]

@app.post("/projects", status_code=201)
def create_project(p: ProjectIn, key=Depends(require_admin)):
    import uuid
    pid = f"proj_{uuid.uuid4().hex[:8]}"
    conn.execute("INSERT INTO projects (id,name,description,phase) VALUES (?,?,?,?)",
                 (pid, p.name, p.description, p.phase))
    conn.commit()
    return {"id": pid, "name": p.name}

@app.get("/projects/{pid}")
def get_project(pid: str, key=Depends(verify_key)):
    p = conn.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone()
    if not p: raise HTTPException(404, "Not found")
    ms = conn.execute("SELECT id,title,status FROM milestones WHERE project_id=?", (pid,)).fetchall()
    ts = conn.execute("SELECT id,title,status,priority FROM tasks WHERE project_id=?", (pid,)).fetchall()
    return {"id":p[0],"name":p[1],"description":p[2],"phase":p[3],"milestones":ms,"tasks":ts}

@app.post("/milestones", status_code=201)
def create_milestone(m: MilestoneIn, key=Depends(require_admin)):
    import uuid
    mid = f"ms_{uuid.uuid4().hex[:8]}"
    conn.execute("INSERT INTO milestones (id,project_id,title) VALUES (?,?,?)", (mid, m.project_id, m.title))
    conn.commit()
    return {"id": mid}

@app.get("/timeline/{pid}")
def get_timeline(pid: str, key=Depends(verify_key)):
    rows = conn.execute(
        "SELECT id,category,title,priority,created_at FROM timeline_events WHERE project_id=? ORDER BY created_at DESC",
        (pid,)).fetchall()
    return [{"id":r[0],"category":r[1],"title":r[2],"priority":r[3],"created_at":r[4]} for r in rows]

@app.get("/health/{pid}")
def health_summary(pid: str, key=Depends(verify_key)):
    total = conn.execute("SELECT COUNT(*) FROM tasks WHERE project_id=?", (pid,)).fetchone()[0]
    done  = conn.execute("SELECT COUNT(*) FROM tasks WHERE project_id=? AND status='done'", (pid,)).fetchone()[0]
    score = round(done/total*100, 1) if total else 50
    return {"project_id": pid, "task_done": done, "task_total": total, "health_score": score}

# ── Swagger 文档 ─────────────────────────────────────────
# 启动后访问 http://localhost:18901/docs

if __name__ == "__main__":
    import uvicorn
    print("s05 FastAPI 启动中...")
    print("API Docs: http://localhost:18901/docs")
    print("认证方式: Header X-Api-Key: pfb_admin_a3f8b2c1d9e4f7a6b8c3d2e1f9a8b7c6")
    uvicorn.run(app, host="0.0.0.0", port=18901)

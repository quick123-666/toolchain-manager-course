"""
s05: FastAPI 层
================
新增能力:
- REST API（GET/POST/PUT/DELETE）
- CORS 跨域支持
- Swagger 文档自动生成（/docs）

核心概念:
- Agent 循环 → HTTP API 层解耦
- 前端可以跨语言/跨框架调用
- 工具函数 → API Endpoint 一一对应
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uvicorn

# ── 复用 s04 的 database 层 ──────────────────────────────
from database import init_db, get_db, encode_key, decode_key

app = FastAPI(title="Toolchain Manager API", version="1.0.0",
              description="工具链管理系统的 FastAPI 层（s05）")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pydantic Models ────────────────────────────────────

class ToolIn(BaseModel):
    name: str
    url: str
    category_id: Optional[int] = None
    description: str = ""
    purpose: str = ""
    pricing: str = ""
    status: str = "活跃"

class ApiKeyIn(BaseModel):
    tool_id: int
    label: str
    key_value: str
    environment: str = "production"
    notes: str = ""
    expires_at: Optional[str] = None

class CostIn(BaseModel):
    tool_id: int
    month: str
    amount: float
    currency: str = "USD"
    notes: str = ""

class ProjectLifecycleIn(BaseModel):
    project_name: str
    description: str = ""
    repo_url: str = ""
    packaging_dir: str = ""
    askdb_backup_dir: str = ""
    spec_file: str = ""
    lifecycle_phase: str = "Phase_4_5"

class ProjectUpdateIn(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    repo_url: Optional[str] = None
    packaging_dir: Optional[str] = None
    askdb_backup_dir: Optional[str] = None
    spec_file: Optional[str] = None
    lifecycle_phase: Optional[str] = None

class ProjectRenameIn(BaseModel):
    new_name: str

# ── Dashboard ──────────────────────────────────────────

@app.get("/api/dashboard")
def dashboard():
    with get_db() as conn:
        c = conn.cursor()
        total = c.execute("SELECT COUNT(*) FROM tools").fetchone()[0]
        active = c.execute("SELECT COUNT(*) FROM tools WHERE status='活跃'").fetchone()[0]
        proj_count = c.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
        total_cost = c.execute("""
            SELECT COALESCE(SUM(amount), 0) FROM costs
            WHERE month = ?
        """, (datetime.now().strftime("%Y-%m"),)).fetchone()[0]
        return {"total_tools": total, "active_tools": active,
                "total_projects": proj_count, "monthly_cost": total_cost}

# ── Categories ─────────────────────────────────────────

@app.get("/api/categories")
def list_categories():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM categories ORDER BY sort_order").fetchall()
        return [dict(r) for r in rows]

# ── Tools ──────────────────────────────────────────────

@app.get("/api/tools")
def list_tools(category_id: Optional[int] = None, status: Optional[str] = None, q: Optional[str] = None):
    with get_db() as conn:
        sql = """
            SELECT t.*, c.name as category_name, c.icon as category_icon
            FROM tools t LEFT JOIN categories c ON t.category_id=c.id WHERE 1=1
        """
        args = []
        if category_id:
            sql += " AND t.category_id=?"
            args.append(category_id)
        if status:
            sql += " AND t.status=?"
            args.append(status)
        if q:
            p = f"%{q}%"
            sql += " AND (t.name LIKE ? OR t.purpose LIKE ? OR t.description LIKE ?)"
            args.extend([p, p, p])
        sql += " ORDER BY t.updated_at DESC"
        rows = conn.execute(sql, args).fetchall()
        return [dict(r) for r in rows]

@app.get("/api/tools/{tid}")
def get_tool(tid: int):
    with get_db() as conn:
        c = conn.cursor()
        tool = c.execute("""
            SELECT t.*, c.name as category_name, c.icon as category_icon
            FROM tools t LEFT JOIN categories c ON t.category_id=c.id WHERE t.id=?
        """, (tid,)).fetchone()
        if not tool:
            raise HTTPException(404, "Tool not found")
        keys = c.execute("SELECT * FROM api_keys WHERE tool_id=? ORDER BY created_at DESC", (tid,)).fetchall()
        costs = c.execute("SELECT * FROM costs WHERE tool_id=? ORDER BY month DESC", (tid,)).fetchall()
        projects = c.execute("""
            SELECT p.* FROM projects p
            JOIN tool_projects tp ON tp.project_id=p.id
            WHERE tp.tool_id=?
        """, (tid,)).fetchall()
        return {
            "tool": dict(tool),
            "api_keys": [dict(k) for k in keys],
            "costs": [dict(c) for c in costs],
            "projects": [dict(p) for p in projects]
        }

@app.post("/api/tools")
def create_tool(data: ToolIn):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO tools (name, url, category_id, description, purpose, pricing, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (data.name, data.url, data.category_id, data.description, data.purpose, data.pricing, data.status))
        return {"id": c.lastrowid}

@app.put("/api/tools/{tid}")
def update_tool(tid: int, data: ToolIn):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            UPDATE tools SET name=?, url=?, category_id=?, description=?,
            purpose=?, pricing=?, status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?
        """, (data.name, data.url, data.category_id, data.description,
              data.purpose, data.pricing, data.status, tid))
        if c.rowcount == 0:
            raise HTTPException(404, "Tool not found")
        return {"ok": True}

@app.delete("/api/tools/{tid}")
def delete_tool(tid: int):
    with get_db() as conn:
        conn.execute("DELETE FROM tools WHERE id=?", (tid,))
        return {"ok": True}

# ── API Keys ────────────────────────────────────────────

@app.get("/api/keys/{tool_id}")
def list_keys(tool_id: int):
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM api_keys WHERE tool_id=? ORDER BY created_at DESC", (tool_id,)).fetchall()
        return [dict(r) for r in rows]

@app.post("/api/keys")
def create_key(data: ApiKeyIn):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO api_keys (tool_id, label, key_value, environment, notes, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (data.tool_id, data.label, encode_key(data.key_value),
              data.environment, data.notes, data.expires_at))
        return {"id": c.lastrowid}

@app.get("/api/keys/decrypt/{kid}")
def decrypt_key(kid: int):
    with get_db() as conn:
        row = conn.execute("SELECT key_value FROM api_keys WHERE id=?", (kid,)).fetchone()
        if not row:
            raise HTTPException(404, "Key not found")
        return {"plaintext": decode_key(row["key_value"])}

@app.delete("/api/keys/{kid}")
def delete_key(kid: int):
    with get_db() as conn:
        conn.execute("DELETE FROM api_keys WHERE id=?", (kid,))
        return {"ok": True}

# ── Costs ───────────────────────────────────────────────

@app.get("/api/costs")
def list_costs(month: Optional[str] = None, tool_id: Optional[int] = None):
    with get_db() as conn:
        sql = "SELECT c.*, t.name as tool_name FROM costs c JOIN tools t ON c.tool_id=t.id WHERE 1=1"
        args = []
        if month:
            sql += " AND c.month=?"
            args.append(month)
        if tool_id:
            sql += " AND c.tool_id=?"
            args.append(tool_id)
        rows = conn.execute(sql + " ORDER BY c.month DESC", args).fetchall()
        return [dict(r) for r in rows]

@app.post("/api/costs")
def create_cost(data: CostIn):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO costs (tool_id, month, amount, currency, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (data.tool_id, data.month, data.amount, data.currency, data.notes))
        return {"id": c.lastrowid}

@app.delete("/api/costs/{cid}")
def delete_cost(cid: int):
    with get_db() as conn:
        conn.execute("DELETE FROM costs WHERE id=?", (cid,))
        return {"ok": True}

# ── Projects ────────────────────────────────────────────

@app.get("/api/projects")
def list_projects():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM projects ORDER BY name").fetchall()
        return [dict(r) for r in rows]

@app.post("/api/projects/lifecycle")
def register_project_lifecycle(data: ProjectLifecycleIn):
    """GraphSpec 专用：一键创建或更新项目全生命周期档案"""
    with get_db() as conn:
        c = conn.cursor()
        existing = c.execute(
            "SELECT id FROM projects WHERE name = ? AND created_by = 'graphspec'",
            (data.project_name,)
        ).fetchone()
        if existing:
            c.execute("""
                UPDATE projects SET description=?, repo_url=?, packaging_dir=?,
                askdb_backup_dir=?, spec_file=?, lifecycle_phase=?,
                updated_at=CURRENT_TIMESTAMP WHERE id=?
            """, (data.description, data.repo_url, data.packaging_dir,
                  data.askdb_backup_dir, data.spec_file, data.lifecycle_phase,
                  existing["id"]))
            return {"ok": True, "action": "updated", "id": existing["id"]}
        else:
            c.execute("""
                INSERT INTO projects (name, description, repo_url, packaging_dir,
                askdb_backup_dir, spec_file, lifecycle_phase, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'graphspec')
            """, (data.project_name, data.description, data.repo_url,
                  data.packaging_dir, data.askdb_backup_dir,
                  data.spec_file, data.lifecycle_phase))
            return {"ok": True, "action": "created", "id": c.lastrowid}

@app.get("/api/projects/lifecycle/{name}")
def get_project_lifecycle(name: str):
    with get_db() as conn:
        c = conn.cursor()
        row = c.execute(
            "SELECT * FROM projects WHERE name = ? AND created_by = 'graphspec'",
            (name,)
        ).fetchone()
        if not row:
            raise HTTPException(404, f"项目不存在: {name}")
        pid = row["id"]
        tools = c.execute("""
            SELECT t.* FROM tools t
            JOIN tool_projects tp ON tp.tool_id=t.id
            WHERE tp.project_id=?
        """, (pid,)).fetchall()
        history = c.execute(
            "SELECT * FROM project_change_history WHERE project_id=? ORDER BY changed_at DESC",
            (pid,)
        ).fetchall()
        return {
            "project": dict(row),
            "tools": [dict(t) for t in tools],
            "change_history": [dict(h) for h in history],
        }

@app.patch("/api/projects/lifecycle/{name}")
def update_project(name: str, data: ProjectUpdateIn):
    with get_db() as conn:
        c = conn.cursor()
        row = c.execute(
            "SELECT * FROM projects WHERE name = ? AND created_by = 'graphspec'",
            (name,)
        ).fetchone()
        if not row:
            raise HTTPException(404, f"项目不存在: {name}")
        changes = []
        for field in ["name","description","repo_url","packaging_dir",
                      "askdb_backup_dir","spec_file","lifecycle_phase"]:
            new_val = getattr(data, field, None)
            if new_val is not None and new_val != row[field]:
                changes.append((row[field], new_val, field))
        if not changes:
            return {"ok": True, "action": "unchanged"}
        set_clause = ", ".join(f"{f}=?" for _, _, f in changes)
        c.execute(f"UPDATE projects SET {set_clause}, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                  tuple(v for _, v, __ in changes) + (row["id"],))
        for old_val, new_val, field in changes:
            c.execute(
                "INSERT INTO project_change_history (project_id, field, old_value, new_value) VALUES (?, ?, ?, ?)",
                (row["id"], field, str(old_val), str(new_val))
            )
        return {"ok": True, "action": "updated",
                "changes": [{"field": f, "old": o, "new": n} for o, n, f in changes]}

@app.post("/api/projects/lifecycle/{name}/rename")
def rename_project(name: str, data: ProjectRenameIn):
    with get_db() as conn:
        c = conn.cursor()
        row = c.execute(
            "SELECT id, name FROM projects WHERE name = ? AND created_by = 'graphspec'",
            (name,)
        ).fetchone()
        if not row:
            raise HTTPException(404, f"项目不存在: {name}")
        if row["name"] == data.new_name:
            return {"ok": True, "action": "unchanged"}
        c.execute(
            "INSERT INTO project_change_history (project_id, field, old_value, new_value) VALUES (?, ?, ?, ?)",
            (row["id"], "name", row["name"], data.new_name)
        )
        c.execute("UPDATE projects SET name = ?, updated_at=CURRENT_TIMESTAMP WHERE id = ?",
                  (data.new_name, row["id"]))
        return {"ok": True, "action": "renamed", "old_name": name, "new_name": data.new_name}

@app.get("/api/projects/lifecycle/{name}/history")
def get_project_history(name: str):
    with get_db() as conn:
        row = conn.execute(
            "SELECT id FROM projects WHERE name = ? AND created_by = 'graphspec'",
            (name,)
        ).fetchone()
        if not row:
            raise HTTPException(404, f"项目不存在: {name}")
        history = conn.execute(
            "SELECT * FROM project_change_history WHERE project_id=? ORDER BY changed_at DESC",
            (row["id"],)
        ).fetchall()
        return [dict(h) for h in history]

@app.post("/api/tools/{tid}/link-project/{pid}")
def link_tool_project(tid: int, pid: int):
    with get_db() as conn:
        conn.execute("INSERT OR IGNORE INTO tool_projects (tool_id, project_id) VALUES (?, ?)", (tid, pid))
        return {"ok": True}

@app.delete("/api/tools/{tid}/unlink-project/{pid}")
def unlink_tool_project(tid: int, pid: int):
    with get_db() as conn:
        conn.execute("DELETE FROM tool_projects WHERE tool_id=? AND project_id=?", (tid, pid))
        return {"ok": True}

# ── Health ───────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "time": datetime.now().isoformat(), "version": "s05"}

# ── 静态文件（托管 s06 的 index.html） ───────────────────

from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

S06_HTML = os.path.join(os.path.dirname(__file__), "..", "s06-vue-frontend", "index.html")

@app.get("/", response_class=HTMLResponse)
def serve_index():
    if os.path.exists(S06_HTML):
        with open(S06_HTML, encoding="utf-8") as f:
            return f.read()
    return "<h1>请先运行 s06-vue-frontend/agent.py 生成 index.html</h1>"

@app.get("/index.html")
def serve_index_file():
    if os.path.exists(S06_HTML):
        return FileResponse(S06_HTML)
    return {"error": "index.html not found. Run s06-vue-frontend/agent.py first."}

if __name__ == "__main__":
    init_db()
    print("[s05] FastAPI 服务启动: http://localhost:18902")
    print("[s05] Swagger 文档: http://localhost:18902/docs")
    print("[s05] 前端页面: http://localhost:18902/")
    uvicorn.run(app, host="0.0.0.0", port=18902, reload=False)

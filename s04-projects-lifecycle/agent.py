"""
s04: 项目生命周期
================
新增能力:
- projects 表：项目档案（含 lifecycle_phase，GraphSpec 对齐）
- tool_projects 表：工具 ↔ 项目多对多
- project_change_history 表：变更历史（审计）

核心概念:
- 工具可以被多个项目共用（多对多）
- 项目有生命周期阶段（Phase_0 ~ Phase_5）
- 所有变更自动记录历史，支持审计回溯
"""

import sqlite3
import json
import os
import base64
from datetime import datetime
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), "toolchain.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def get_db():
    conn = get_conn()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                icon TEXT DEFAULT '📦',
                sort_order INTEGER DEFAULT 0
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS tools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                category_id INTEGER REFERENCES categories(id),
                description TEXT DEFAULT '',
                purpose TEXT DEFAULT '',
                pricing TEXT DEFAULT '',
                status TEXT DEFAULT '活跃',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_id INTEGER REFERENCES tools(id) ON DELETE CASCADE,
                label TEXT NOT NULL,
                key_value TEXT NOT NULL,
                environment TEXT DEFAULT 'production',
                notes TEXT DEFAULT '',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS costs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_id INTEGER REFERENCES tools(id) ON DELETE CASCADE,
                month TEXT NOT NULL,
                amount REAL NOT NULL DEFAULT 0,
                currency TEXT DEFAULT 'USD',
                notes TEXT DEFAULT ''
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                repo_url TEXT DEFAULT '',
                packaging_dir TEXT DEFAULT '',
                askdb_backup_dir TEXT DEFAULT '',
                spec_file TEXT DEFAULT '',
                lifecycle_phase TEXT DEFAULT 'Phase_0',
                created_by TEXT DEFAULT 'graphspec',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS project_change_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
                field TEXT NOT NULL,
                old_value TEXT DEFAULT '',
                new_value TEXT DEFAULT '',
                changed_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS tool_projects (
                tool_id INTEGER REFERENCES tools(id) ON DELETE CASCADE,
                project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
                PRIMARY KEY (tool_id, project_id)
            )
        """)
        # 种子分类
        cats = [
            ('AI Infra', '🤖', 1), ('Database', '🗄️', 2), ('Payments', '💳', 3),
            ('Email & Messaging', '📧', 4), ('Analytics', '📊', 5),
            ('Hosting & CDN', '🚀', 6), ('DevOps', '⚙️', 7),
        ]
        for name, icon, order in cats:
            c.execute("INSERT OR IGNORE INTO categories (name, icon, sort_order) VALUES (?, ?, ?)", (name, icon, order))
        # 种子工具
        seed = [
            ('Pinecone', 'app.pinecone.io', 1, '向量数据库 + RAG Assistant', 'AI 应用向量检索', 'Serverless 按查询计费', '活跃'),
            ('Upstash', 'console.upstash.com', 1, 'Serverless Redis + Kafka', 'Serverless 缓存、消息队列', 'Per-request 计费', '活跃'),
            ('Supabase', 'supabase.com', 2, '开源 Firebase 替代', 'PostgreSQL + Auth + Storage', '免费 500MB', '活跃'),
            ('Stripe', 'dashboard.stripe.com', 3, '在线支付处理', '收款、订阅管理', '2.9% + 30¢ per txn', '活跃'),
            ('Resend', 'resend.com', 4, '开发者邮件 API', 'Transactional email、React Email', 'Per-request 计费', '活跃'),
            ('PostHog', 'posthog.com', 5, '产品分析平台', '事件追踪、漏斗分析、A/B 测试', '免费 100万事件/月', '活跃'),
            ('Vercel', 'vercel.com', 6, '前端部署平台', 'Next.js 部署、Serverless Functions', '免费 100GB 带宽/月', '活跃'),
        ]
        for name, url, cat_id, desc, purpose, pricing, status in seed:
            c.execute("""
                INSERT OR IGNORE INTO tools (name, url, category_id, description, purpose, pricing, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, url, cat_id, desc, purpose, pricing, status))
        print("[s04] DB initialized:", DB_PATH)

# ── 辅助函数 ─────────────────────────────────────────────

def encode_key(raw):
    return base64.b64encode(raw.encode()).decode()

def decode_key(encoded):
    return base64.b64decode(encoded.encode()).decode()

# ── Projects ─────────────────────────────────────────────

def list_projects():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM projects ORDER BY name").fetchall()
        return [dict(r) for r in rows]

def get_project_detail(name):
    """查项目完整档案（含关联工具和变更历史）"""
    with get_db() as conn:
        c = conn.cursor()
        row = c.execute(
            "SELECT * FROM projects WHERE name = ? AND created_by = 'graphspec'",
            (name,)
        ).fetchone()
        if not row:
            return {"error": f"项目不存在: {name}"}
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

def register_project(data):
    """GraphSpec 专用：一键创建或更新项目全生命周期档案"""
    with get_db() as conn:
        c = conn.cursor()
        existing = c.execute(
            "SELECT id FROM projects WHERE name = ? AND created_by = 'graphspec'",
            (data["project_name"],)
        ).fetchone()
        if existing:
            c.execute("""
                UPDATE projects SET description=?, repo_url=?, packaging_dir=?,
                askdb_backup_dir=?, spec_file=?, lifecycle_phase=?,
                updated_at=CURRENT_TIMESTAMP WHERE id=?
            """, (data.get("description",""), data.get("repo_url",""),
                  data.get("packaging_dir",""), data.get("askdb_backup_dir",""),
                  data.get("spec_file",""), data.get("lifecycle_phase","Phase_4_5"),
                  existing["id"]))
            return {"ok": True, "action": "updated", "id": existing["id"]}
        else:
            c.execute("""
                INSERT INTO projects (name, description, repo_url, packaging_dir,
                askdb_backup_dir, spec_file, lifecycle_phase, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'graphspec')
            """, (data["project_name"], data.get("description",""), data.get("repo_url",""),
                  data.get("packaging_dir",""), data.get("askdb_backup_dir",""),
                  data.get("spec_file",""), data.get("lifecycle_phase","Phase_4_5")))
            return {"ok": True, "action": "created", "id": c.lastrowid}

def update_project_fields(name, **fields):
    """更新项目任意字段，自动记录变更历史"""
    with get_db() as conn:
        c = conn.cursor()
        row = c.execute(
            "SELECT * FROM projects WHERE name = ? AND created_by = 'graphspec'",
            (name,)
        ).fetchone()
        if not row:
            return {"ok": False, "error": f"项目不存在: {name}"}
        changes = []
        for field in ["name","description","repo_url","packaging_dir",
                      "askdb_backup_dir","spec_file","lifecycle_phase"]:
            new_val = fields.get(field)
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

def rename_project(name, new_name):
    """项目改名（记录变更历史）"""
    with get_db() as conn:
        c = conn.cursor()
        row = c.execute(
            "SELECT id, name FROM projects WHERE name = ? AND created_by = 'graphspec'",
            (name,)
        ).fetchone()
        if not row:
            return {"ok": False, "error": f"项目不存在: {name}"}
        if row["name"] == new_name:
            return {"ok": True, "action": "unchanged"}
        c.execute(
            "INSERT INTO project_change_history (project_id, field, old_value, new_value) VALUES (?, ?, ?, ?)",
            (row["id"], "name", row["name"], new_name)
        )
        c.execute("UPDATE projects SET name = ?, updated_at=CURRENT_TIMESTAMP WHERE id = ?",
                  (new_name, row["id"]))
        return {"ok": True, "action": "renamed", "old_name": name, "new_name": new_name}

# ── Tool ↔ Project 关联 ─────────────────────────────────

def link_tool_project(tool_id, project_name):
    with get_db() as conn:
        c = conn.cursor()
        proj = c.execute(
            "SELECT id FROM projects WHERE name=? AND created_by='graphspec'",
            (project_name,)
        ).fetchone()
        if not proj:
            return {"ok": False, "error": f"项目不存在: {project_name}"}
        c.execute("INSERT OR IGNORE INTO tool_projects (tool_id, project_id) VALUES (?, ?)",
                  (tool_id, proj["id"]))
        return {"ok": True}

def unlink_tool_project(tool_id, project_name):
    with get_db() as conn:
        c = conn.cursor()
        proj = c.execute(
            "SELECT id FROM projects WHERE name=? AND created_by='graphspec'",
            (project_name,)
        ).fetchone()
        if not proj:
            return {"ok": False, "error": f"项目不存在: {project_name}"}
        c.execute("DELETE FROM tool_projects WHERE tool_id=? AND project_id=?",
                  (tool_id, proj["id"]))
        return {"ok": True}

def get_tool_projects(tool_id):
    with get_db() as conn:
        rows = conn.execute("""
            SELECT p.* FROM projects p
            JOIN tool_projects tp ON tp.project_id=p.id
            WHERE tp.tool_id=?
        """, (tool_id,)).fetchall()
        return [dict(r) for r in rows]

# ── 其他 CRUD ────────────────────────────────────────────

def list_tools(category_id=None, status=None, q=None):
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
        rows = conn.execute(sql, args).fetchall()
        return [dict(r) for r in rows]

def add_tool(name, url, category_id=None, description="", purpose="", pricing="", status="活跃"):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO tools (name, url, category_id, description, purpose, pricing, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, url, category_id, description, purpose, pricing, status))
        return {"id": c.lastrowid}

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

# ── Agent 循环 ───────────────────────────────────────────

TOOL_HANDLERS = {}

def tool(name):
    def decorator(fn):
        TOOL_HANDLERS[name] = fn
        return fn
    return decorator

@tool("dashboard")
def dashboard_cmd(args):
    return json.dumps(dashboard(), ensure_ascii=False, indent=2)

@tool("list_tools")
def list_tools_cmd(args):
    result = list_tools(category_id=args.get("category_id"), status=args.get("status"), q=args.get("q"))
    return json.dumps(result, ensure_ascii=False, indent=2)

@tool("add_tool")
def add_tool_cmd(args):
    result = add_tool(**{k: v for k, v in args.items() if k in
        ["name", "url", "category_id", "description", "purpose", "pricing", "status"]})
    return json.dumps(result, ensure_ascii=False)

@tool("list_projects")
def list_projects_cmd(args):
    return json.dumps(list_projects(), ensure_ascii=False, indent=2)

@tool("get_project")
def get_project_cmd(args):
    result = get_project_detail(args["name"])
    return json.dumps(result, ensure_ascii=False, indent=2)

@tool("register_project")
def register_project_cmd(args):
    return json.dumps(register_project(args), ensure_ascii=False)

@tool("update_project")
def update_project_cmd(args):
    name = args.pop("name")
    return json.dumps(update_project_fields(name, **args), ensure_ascii=False, indent=2)

@tool("rename_project")
def rename_project_cmd(args):
    return json.dumps(rename_project(args["name"], args["new_name"]), ensure_ascii=False)

@tool("link_tool")
def link_tool_cmd(args):
    return json.dumps(link_tool_project(int(args["tool_id"]), args["project"]), ensure_ascii=False)

@tool("unlink_tool")
def unlink_tool_cmd(args):
    return json.dumps(unlink_tool_project(int(args["tool_id"]), args["project"]), ensure_ascii=False)

@tool("get_tool_projects")
def get_tool_projects_cmd(args):
    return json.dumps(get_tool_projects(int(args["tool_id"])), ensure_ascii=False, indent=2)

def parse(s):
    parts = s.split()
    args = {}
    for p in parts:
        if "=" in p:
            k, v = p.split("=", 1)
            args[k.strip()] = v.strip()
    return args

def call_llm(messages):
    last = messages[-1]["content"].lower().strip()
    if last.startswith("dashboard"):
        return {"tool_use": "dashboard", "args": {}}
    if last.startswith("register_project "):
        data = parse(last[16:])
        return {"tool_use": "register_project", "args": data}
    if last.startswith("update_project "):
        data = parse(last[15:])
        return {"tool_use": "update_project", "args": data}
    if last.startswith("rename_project "):
        data = parse(last[15:])
        return {"tool_use": "rename_project", "args": data}
    if last.startswith("get_project "):
        data = parse(last[12:])
        return {"tool_use": "get_project", "args": data}
    if last.startswith("list_projects"):
        return {"tool_use": "list_projects", "args": {}}
    if last.startswith("link_tool "):
        data = parse(last[10:])
        return {"tool_use": "link_tool", "args": data}
    if last.startswith("unlink_tool "):
        data = parse(last[12:])
        return {"tool_use": "unlink_tool", "args": data}
    if last.startswith("get_tool_projects "):
        data = parse(last[16:])
        return {"tool_use": "get_tool_projects", "args": data}
    if last.startswith("add_tool "):
        return {"tool_use": "add_tool", "args": parse(last[9:])}
    if last.startswith("list_tools") or last.startswith("search "):
        raw = last.replace("search ", "").replace("list_tools", "").strip()
        return {"tool_use": "list_tools", "args": parse(raw) if raw else {}}
    return {"tool_use": None, "content": "Try: dashboard, register_project, update_project, rename_project, get_project, list_projects, link_tool, unlink_tool, add_tool, list_tools"}

def run_agent():
    print("=" * 50)
    print("Toolchain Manager · s04 (项目生命周期)")
    print("可用工具:", list(TOOL_HANDLERS.keys()))
    print("=" * 50)
    messages = []
    while True:
        try:
            user_input = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        if not user_input:
            continue
        messages.append({"role": "user", "content": user_input})
        response = call_llm(messages)
        if not response.get("tool_use"):
            print(response.get("content", ""))
            messages.append({"role": "assistant", "content": response.get("content", "")})
            continue
        name = response["tool_use"]
        args = response.get("args", {})
        if name not in TOOL_HANDLERS:
            print(f"[ERROR] Unknown tool: {name}")
            continue
        result = TOOL_HANDLERS[name](args)
        print(result)
        messages.append({"role": "tool", "content": result})

if __name__ == "__main__":
    init_db()
    run_agent()

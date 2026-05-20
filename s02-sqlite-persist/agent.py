"""
s02: SQLite 持久化
==================
新增能力: 将工具数据写入 SQLite，进程重启后数据不丢失

核心概念:
- tools[] → SQLite tools 表
- 引入 database.py 封装连接和初始化
- 事务自动提交，连接自动关闭
"""

import sqlite3
import json
import os
from datetime import datetime
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), "toolchain.db")

# ── 数据库层 ─────────────────────────────────────────────

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
    """初始化数据库和种子数据"""
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
        # 种子分类
        cats = [
            ('AI Infra', '🤖', 1),
            ('Database', '🗄️', 2),
            ('Payments', '💳', 3),
            ('Email & Messaging', '📧', 4),
            ('Analytics', '📊', 5),
        ]
        for name, icon, order in cats:
            c.execute("INSERT OR IGNORE INTO categories (name, icon, sort_order) VALUES (?, ?, ?)", (name, icon, order))
        # 种子工具
        seed = [
            ('Pinecone', 'app.pinecone.io', 1, '向量数据库 + RAG Assistant', 'AI 应用向量检索', 'Serverless 按查询计费', '活跃'),
            ('Supabase', 'supabase.com', 2, '开源 Firebase 替代', 'PostgreSQL + Auth + Storage', '免费 500MB', '活跃'),
            ('Stripe', 'dashboard.stripe.com', 3, '在线支付处理', '收款、订阅管理', '2.9% + 30¢ per txn', '活跃'),
        ]
        for name, url, cat_id, desc, purpose, pricing, status in seed:
            c.execute("""
                INSERT OR IGNORE INTO tools (name, url, category_id, description, purpose, pricing, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, url, cat_id, desc, purpose, pricing, status))
        print("[s02] DB initialized:", DB_PATH)

# ── CRUD 操作 ─────────────────────────────────────────────

def list_tools(category_id=None, status=None):
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

def update_tool(tid, **fields):
    with get_db() as conn:
        allowed = ["name", "url", "category_id", "description", "purpose", "pricing", "status"]
        sets = {k: v for k, v in fields.items() if k in allowed}
        if not sets:
            return {"ok": False, "error": "No valid fields"}
        set_clause = ", ".join(f"{k}=?" for k in sets)
        sets["updated_at"] = datetime.now().isoformat()
        c = conn.cursor()
        c.execute(f"UPDATE tools SET {set_clause}, updated_at=? WHERE id=?",
                  tuple(sets.values()) + (tid,))
        return {"ok": c.rowcount > 0}

def delete_tool(tid):
    with get_db() as conn:
        conn.execute("DELETE FROM tools WHERE id=?", (tid,))
        return {"ok": True}

def get_tool(tid):
    with get_db() as conn:
        c = conn.cursor()
        tool = c.execute("""
            SELECT t.*, c.name as category_name, c.icon as category_icon
            FROM tools t LEFT JOIN categories c ON t.category_id=c.id WHERE t.id=?
        """, (tid,)).fetchone()
        if not tool:
            return {"error": "Tool not found"}
        return dict(tool)

def search_tools(q):
    with get_db() as conn:
        pattern = f"%{q}%"
        rows = conn.execute("""
            SELECT t.*, c.name as category_name FROM tools t
            LEFT JOIN categories c ON t.category_id=c.id
            WHERE t.name LIKE ? OR t.description LIKE ? OR t.purpose LIKE ?
        """, (pattern, pattern, pattern)).fetchall()
        return [dict(r) for r in rows]

# ── 模拟 LLM + Agent 循环 ────────────────────────────────

TOOL_HANDLERS = {}

def tool(name):
    def decorator(fn):
        TOOL_HANDLERS[name] = fn
        return fn
    return decorator

@tool("list_tools")
def list_tools_cmd(args):
    result = list_tools(category_id=args.get("category_id"), status=args.get("status"))
    return json.dumps(result, ensure_ascii=False, indent=2)

@tool("add_tool")
def add_tool_cmd(args):
    result = add_tool(**{k: v for k, v in args.items() if k in
        ["name", "url", "category_id", "description", "purpose", "pricing", "status"]})
    return json.dumps(result, ensure_ascii=False)

@tool("update_tool")
def update_tool_cmd(args):
    tid = int(args.pop("id"))
    result = update_tool(tid, **args)
    return json.dumps(result, ensure_ascii=False)

@tool("delete_tool")
def delete_tool_cmd(args):
    result = delete_tool(int(args["id"]))
    return json.dumps(result, ensure_ascii=False)

@tool("get_tool")
def get_tool_cmd(args):
    result = get_tool(int(args["id"]))
    return json.dumps(result, ensure_ascii=False, indent=2)

@tool("search_tools")
def search_tools_cmd(args):
    result = search_tools(args.get("q", ""))
    return json.dumps(result, ensure_ascii=False, indent=2)

def call_llm(messages):
    last = messages[-1]["content"].lower().strip()
    if last.startswith("add "):
        parts = last[4:].split()
        args = {}
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
                args[k.strip()] = v.strip()
        return {"tool_use": "add_tool", "args": args}
    if last.startswith("update "):
        parts = last[7:].split()
        args = {}
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
                args[k.strip()] = v.strip()
        return {"tool_use": "update_tool", "args": args}
    if last.startswith("delete "):
        parts = last[7:].split()
        args = {}
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
                args[k.strip()] = v.strip()
        return {"tool_use": "delete_tool", "args": args}
    if last.startswith("get "):
        parts = last[4:].split()
        args = {}
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
                args[k.strip()] = v.strip()
        return {"tool_use": "get_tool", "args": args}
    if last.startswith("search "):
        parts = last[7:].split()
        args = {}
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
                args[k.strip()] = v.strip()
        return {"tool_use": "search_tools", "args": args}
    if last in ("list", "ls", "list tools"):
        return {"tool_use": "list_tools", "args": {}}
    return {"tool_use": None, "content": "Unknown command."}

def run_agent():
    print("=" * 50)
    print("Toolchain Manager · s02 (SQLite 持久化)")
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

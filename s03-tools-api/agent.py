"""
s03: 工具分发表
================
新增能力: 引入 Categories / API Keys / Costs 表，
         工具从「单表」扩展为「多表关联」

核心概念:
- 分类体系（categories）独立于工具
- API Key 存储（base64 混淆）
- 月度费用追踪（costs）
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
        # 种子分类
        cats = [
            ('AI Infra', '🤖', 1),
            ('Database', '🗄️', 2),
            ('Payments', '💳', 3),
            ('Email & Messaging', '📧', 4),
            ('Analytics', '📊', 5),
            ('Hosting & CDN', '🚀', 6),
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
        print("[s03] DB initialized:", DB_PATH)

# ── 工具函数 ─────────────────────────────────────────────

def encode_key(raw):
    return base64.b64encode(raw.encode()).decode()

def decode_key(encoded):
    return base64.b64decode(encoded.encode()).decode()

# ── CRUD ───────────────────────────────────────────────────

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
            sql += " AND (t.name LIKE ? OR t.purpose LIKE ? OR t.description LIKE ?)"
            p = f"%{q}%"
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

def update_tool(tid, **fields):
    allowed = ["name", "url", "category_id", "description", "purpose", "pricing", "status"]
    sets = {k: v for k, v in fields.items() if k in allowed}
    if not sets:
        return {"ok": False}
    set_clause = ", ".join(f"{k}=?" for k in sets)
    sets["updated_at"] = datetime.now().isoformat()
    with get_db() as conn:
        c = conn.cursor()
        c.execute(f"UPDATE tools SET {set_clause}, updated_at=? WHERE id=?",
                  tuple(sets.values()) + (tid,))
        return {"ok": c.rowcount > 0}

def delete_tool(tid):
    with get_db() as conn:
        conn.execute("DELETE FROM tools WHERE id=?", (tid,))
        return {"ok": True}

def get_tool_detail(tid):
    with get_db() as conn:
        c = conn.cursor()
        tool = c.execute("""
            SELECT t.*, c.name as category_name, c.icon as category_icon
            FROM tools t LEFT JOIN categories c ON t.category_id=c.id WHERE t.id=?
        """, (tid,)).fetchone()
        if not tool:
            return {"error": "Tool not found"}
        keys = c.execute("SELECT * FROM api_keys WHERE tool_id=? ORDER BY created_at DESC", (tid,)).fetchall()
        costs = c.execute("SELECT * FROM costs WHERE tool_id=? ORDER BY month DESC", (tid,)).fetchall()
        return {
            "tool": dict(tool),
            "api_keys": [dict(k) for k in keys],
            "costs": [dict(c) for c in costs],
        }

# API Keys
def add_api_key(tool_id, label, key_value, environment="production", notes="", expires_at=None):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO api_keys (tool_id, label, key_value, environment, notes, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (tool_id, label, encode_key(key_value), environment, notes, expires_at))
        return {"id": c.lastrowid}

def list_api_keys(tool_id):
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM api_keys WHERE tool_id=? ORDER BY created_at DESC", (tool_id,)).fetchall()
        return [dict(r) for r in rows]

def decrypt_api_key(kid):
    with get_db() as conn:
        row = conn.execute("SELECT key_value FROM api_keys WHERE id=?", (kid,)).fetchone()
        if not row:
            return {"error": "Key not found"}
        return {"plaintext": decode_key(row["key_value"])}

def delete_api_key(kid):
    with get_db() as conn:
        conn.execute("DELETE FROM api_keys WHERE id=?", (kid,))
        return {"ok": True}

# Costs
def add_cost(tool_id, month, amount, currency="USD", notes=""):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO costs (tool_id, month, amount, currency, notes) VALUES (?, ?, ?, ?, ?)",
                  (tool_id, month, amount, currency, notes))
        return {"id": c.lastrowid}

def list_costs(month=None, tool_id=None):
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

def delete_cost(cid):
    with get_db() as conn:
        conn.execute("DELETE FROM costs WHERE id=?", (cid,))
        return {"ok": True}

# Dashboard
def dashboard():
    with get_db() as conn:
        c = conn.cursor()
        total = c.execute("SELECT COUNT(*) FROM tools").fetchone()[0]
        active = c.execute("SELECT COUNT(*) FROM tools WHERE status='活跃'").fetchone()[0]
        total_cost = c.execute("""
            SELECT COALESCE(SUM(amount), 0) FROM costs
            WHERE month = ?
        """, (datetime.now().strftime("%Y-%m"),)).fetchone()[0]
        return {"total_tools": total, "active_tools": active, "monthly_cost": total_cost}

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
    result = get_tool_detail(int(args["id"]))
    return json.dumps(result, ensure_ascii=False, indent=2)

@tool("add_api_key")
def add_api_key_cmd(args):
    result = add_api_key(
        tool_id=int(args["tool_id"]),
        label=args["label"],
        key_value=args["key_value"],
        environment=args.get("environment", "production"),
        notes=args.get("notes", ""),
        expires_at=args.get("expires_at"),
    )
    return json.dumps(result, ensure_ascii=False)

@tool("decrypt_key")
def decrypt_key_cmd(args):
    return json.dumps(decrypt_api_key(int(args["id"])), ensure_ascii=False)

@tool("add_cost")
def add_cost_cmd(args):
    result = add_cost(
        tool_id=int(args["tool_id"]),
        month=args["month"],
        amount=float(args["amount"]),
        currency=args.get("currency", "USD"),
        notes=args.get("notes", ""),
    )
    return json.dumps(result, ensure_ascii=False)

@tool("list_costs")
def list_costs_cmd(args):
    result = list_costs(month=args.get("month"), tool_id=int(args["tool_id"]) if args.get("tool_id") else None)
    return json.dumps(result, ensure_ascii=False, indent=2)

def call_llm(messages):
    last = messages[-1]["content"].lower().strip()
    # 解析 key=value 格式
    def parse(s):
        parts = s.split()
        args = {}
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
                args[k.strip()] = v.strip()
        return args

    if last.startswith("dashboard"):
        return {"tool_use": "dashboard", "args": {}}
    if last.startswith("add_tool "):
        return {"tool_use": "add_tool", "args": parse(last[9:])}
    if last.startswith("update_tool "):
        return {"tool_use": "update_tool", "args": parse(last[13:])}
    if last.startswith("delete_tool "):
        return {"tool_use": "delete_tool", "args": parse(last[13:])}
    if last.startswith("get_tool "):
        return {"tool_use": "get_tool", "args": parse(last[9:])}
    if last.startswith("add_api_key "):
        return {"tool_use": "add_api_key", "args": parse(last[12:])}
    if last.startswith("decrypt_key "):
        return {"tool_use": "decrypt_key", "args": parse(last[12:])}
    if last.startswith("add_cost "):
        return {"tool_use": "add_cost", "args": parse(last[9:])}
    if last.startswith("list_costs"):
        return {"tool_use": "list_costs", "args": parse(last[10:])}
    if last.startswith("search ") or last.startswith("list_tools"):
        cmd = "list_tools"
        raw = last.replace("search ", "").replace("list_tools", "").strip()
        args = parse(raw) if raw else {}
        return {"tool_use": cmd, "args": args}
    return {"tool_use": None, "content": "Try: dashboard, add_tool, update_tool, delete_tool, get_tool, add_api_key, decrypt_key, add_cost, list_costs, list_tools, search"}

def run_agent():
    print("=" * 50)
    print("Toolchain Manager · s03 (工具分发表)")
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

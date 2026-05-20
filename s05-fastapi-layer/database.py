"""
s05-fastapi-layer/database.py
==============================
被 api.py 复用的数据库层（直接从 s04 提取）
"""

import sqlite3
import os
import base64
from datetime import datetime
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "s04-projects-lifecycle", "toolchain.db")

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
        cats = [
            ('AI Infra', '🤖', 1), ('Database', '🗄️', 2), ('Payments', '💳', 3),
            ('Email & Messaging', '📧', 4), ('Analytics', '📊', 5),
            ('Hosting & CDN', '🚀', 6), ('DevOps', '⚙️', 7),
        ]
        for name, icon, order in cats:
            c.execute("INSERT OR IGNORE INTO categories (name, icon, sort_order) VALUES (?, ?, ?)", (name, icon, order))
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

def encode_key(raw):
    return base64.b64encode(raw.encode()).decode()

def decode_key(encoded):
    return base64.b64decode(encoded.encode()).decode()

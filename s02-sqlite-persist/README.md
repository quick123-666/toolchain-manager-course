# s02: SQLite 持久化

> 本章新增：将工具数据写入 SQLite，进程重启后数据不丢失

## 新增概念

- **SQLite 持久化** — `tools[]` 列表 → `tools` 表
- **`get_db()` 上下文管理器** — 自动 commit，自动 close
- **事务隔离** — 多步操作要么全成功，要么全回滚
- **`row_factory = sqlite3.Row`** — 结果可以像字典一样用 `row["name"]` 取值

## 核心代码

```python
DB_PATH = os.path.join(os.path.dirname(__file__), "toolchain.db")

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS categories ...
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS tools ...
        """)
        # 种子数据...

def list_tools(category_id=None, status=None):
    with get_db() as conn:
        sql = """SELECT t.*, c.name as category_name, c.icon as category_icon
                 FROM tools t LEFT JOIN categories c ON t.category_id=c.id WHERE 1=1"""
        args = []
        if category_id: sql += " AND t.category_id=?"; args.append(category_id)
        if status:      sql += " AND t.status=?";      args.append(status)
        rows = conn.execute(sql, args).fetchall()
        return [dict(r) for r in rows]
```

## 表结构

| 表名 | 用途 |
|------|------|
| `categories` | 工具分类（name, icon, sort_order） |
| `tools` | 工具节点（name, url, category_id, description, status...） |

## 与 s01 的 diff

```
  - tools: list[dict]          # 内存列表
  + tools: SQLite table        # 持久化存储
+ get_db() / init_db()        # 数据库上下文管理器
+ categories 表               # 分类支持
+ 种子数据（3个工具）           # Pinecone / Supabase / Stripe
```

## 运行

```bash
python agent.py
```

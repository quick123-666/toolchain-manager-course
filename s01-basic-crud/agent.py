"""
s01: 内存 CRUD
================
新增能力: Agent 循环 + 基本增删改查（纯内存，无持久化）

核心概念:
- tools[] 列表在内存中，进程结束即丢失
- 增删改查全在 Python list/dict 层面操作
- 模拟 LLM 决定调用哪个工具（write-back 模式）
"""

import json
from datetime import datetime

# ── 内存存储 ─────────────────────────────────────────────
tools: list[dict] = []
next_id = 1

# ── 工具分发表 ─────────────────────────────────────────
TOOL_HANDLERS: dict[str, callable] = {}

def tool(name: str):
    """装饰器：注册工具函数"""
    def decorator(fn):
        TOOL_HANDLERS[name] = fn
        return fn
    return decorator

# ── 内置工具 ─────────────────────────────────────────────

@tool("list_tools")
def list_tools(args: dict) -> str:
    """列出所有工具，可按 category 和 status 过滤"""
    category = args.get("category")
    status = args.get("status")
    result = [t for t in tools]
    if category:
        result = [t for t in result if t.get("category") == category]
    if status:
        result = [t for t in result if t.get("status") == status]
    return json.dumps(result, ensure_ascii=False, indent=2)

@tool("add_tool")
def add_tool(args: dict) -> str:
    """添加工具到内存列表"""
    global next_id
    tool_data = {
        "id": next_id,
        "name": args["name"],
        "url": args["url"],
        "category": args.get("category", "General"),
        "status": args.get("status", "活跃"),
        "description": args.get("description", ""),
        "purpose": args.get("purpose", ""),
        "pricing": args.get("pricing", ""),
        "created_at": datetime.now().isoformat(),
    }
    tools.append(tool_data)
    next_id += 1
    return json.dumps({"ok": True, "id": tool_data["id"]}, ensure_ascii=False)

@tool("update_tool")
def update_tool(args: dict) -> str:
    """更新工具信息（按 ID）"""
    tid = args["id"]
    for t in tools:
        if t["id"] == tid:
            for key in ["name", "url", "category", "status", "description", "purpose", "pricing"]:
                if key in args:
                    t[key] = args[key]
            t["updated_at"] = datetime.now().isoformat()
            return json.dumps({"ok": True}, ensure_ascii=False)
    return json.dumps({"ok": False, "error": "Tool not found"}, ensure_ascii=False)

@tool("delete_tool")
def delete_tool(args: dict) -> str:
    """从内存删除工具"""
    global tools
    tid = args["id"]
    before = len(tools)
    tools = [t for t in tools if t["id"] != tid]
    deleted = len(tools) < before
    return json.dumps({"ok": deleted}, ensure_ascii=False)

@tool("get_tool")
def get_tool(args: dict) -> str:
    """按 ID 获取单个工具"""
    tid = args["id"]
    for t in tools:
        if t["id"] == tid:
            return json.dumps(t, ensure_ascii=False, indent=2)
    return json.dumps({"error": "Tool not found"}, ensure_ascii=False)

@tool("search_tools")
def search_tools(args: dict) -> str:
    """按关键词搜索工具名称和描述"""
    q = args.get("q", "").lower()
    if not q:
        return json.dumps(tools, ensure_ascii=False, indent=2)
    result = [t for t in tools if q in t["name"].lower() or q in t.get("description", "").lower() or q in t.get("purpose", "").lower()]
    return json.dumps(result, ensure_ascii=False, indent=2)

# ── 模拟 LLM 决策 ───────────────────────────────────────

def call_llm(messages: list[dict]) -> dict:
    """
    确定性模拟 LLM：根据最后一条用户消息决定调用哪个工具。
    真实环境替换为 OpenAI / Claude API 调用。
    """
    last = messages[-1]["content"].lower().strip()

    # 解析指令
    if last.startswith("add "):
        # 格式: add name=xxx url=xxx category=xxx
        parts = last[4:].split()
        args = {}
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
                args[k.strip()] = v.strip()
        return {"tool_use": "add_tool", "args": args}

    if last.startswith("update "):
        # 格式: update id=1 name=xxx
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
        # 格式: get id=1
        parts = last[4:].split()
        args = {}
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
                args[k.strip()] = v.strip()
        return {"tool_use": "get_tool", "args": args}

    if last.startswith("search "):
        # 格式: search q=xxx
        parts = last[7:].split()
        args = {}
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
                args[k.strip()] = v.strip()
        return {"tool_use": "search_tools", "args": args}

    if last in ("list", "ls", "list tools"):
        return {"tool_use": "list_tools", "args": {}}

    return {"tool_use": None, "content": "Unknown command. Try: add, update, delete, get, search, list"}


# ── Agent 循环 ───────────────────────────────────────────

def run_agent():
    """主循环：接收命令，执行工具，输出结果"""
    print("=" * 50)
    print("Toolchain Manager · s01 (内存 CRUD)")
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
    # 预填充一些种子数据
    seed = [
        {"name": "Pinecone", "url": "app.pinecone.io", "category": "AI Infra", "status": "活跃",
         "description": "向量数据库 + RAG Assistant", "purpose": "AI 应用向量检索", "pricing": "Serverless 按查询计费"},
        {"name": "Supabase", "url": "supabase.com", "category": "Database", "status": "活跃",
         "description": "开源 Firebase 替代 (BaaS)", "purpose": "PostgreSQL + Auth + Storage", "pricing": "免费 500MB"},
        {"name": "Stripe", "url": "dashboard.stripe.com", "category": "Payments", "status": "活跃",
         "description": "在线支付处理", "purpose": "收款、订阅管理", "pricing": "2.9% + 30¢ per txn"},
    ]
    for s in seed:
        add_tool(s)

    print("[s01] 种子数据已加载:", len(tools), "个工具")
    run_agent()

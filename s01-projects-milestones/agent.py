"""
s01: Projects & Milestones — 内存 CRUD
Motto: 项目是所有管理的起点

核心循环不变，每章只加一个 TOOL_HANDLERS 条目。
"""

# ── 内存状态 ──────────────────────────────────────────────
_projects = []
_milestones = []
_next_proj_id = 1
_next_ms_id = 1

# ── Agent 核心循环 ─────────────────────────────────────────
MESSAGES = [
    {"role": "system", "content": (
        "你是一个项目管理系统。用户的指令会触发以下工具之一：\n"
        "  register_project  — 创建项目\n"
        "  list_projects    — 列出所有项目\n"
        "  get_project      — 查看单个项目详情\n"
        "  update_project   — 更新项目\n"
        "  delete_project   — 删除项目\n"
        "  create_milestone — 创建里程碑\n"
        "  list_milestones  — 列出里程碑\n"
        "  close_milestone  — 关闭里程碑\n"
        "无法回答时返回 'unknown'"
    )}
]

def TOOL_HANDLERS():
    return {
        "register_project": _register_project,
        "list_projects":    _list_projects,
        "get_project":      _get_project,
        "update_project":   _update_project,
        "delete_project":   _delete_project,
        "create_milestone": _create_milestone,
        "list_milestones":   _list_milestones,
        "close_milestone":   _close_milestone,
    }

# ── 工具实现 ──────────────────────────────────────────────
def _register_project(args):
    global _next_proj_id
    name = args.get("name")
    desc = args.get("description", "")
    phase = args.get("phase", "planning")
    p = {"id": f"proj_{_next_proj_id:04d}", "name": name, "description": desc, "phase": phase}
    _projects.append(p)
    _next_proj_id += 1
    return f"项目 [{p['id']}] {name} 创建成功，phase={phase}"

def _list_projects(args):
    if not _projects:
        return "暂无项目"
    lines = [f"[{p['id']}] {p['name']} | phase={p['phase']}" for p in _projects]
    return "\n".join(lines)

def _get_project(args):
    pid = args.get("id")
    for p in _projects:
        if p["id"] == pid:
            ms = [m for m in _milestones if m["project_id"] == pid]
            ms_lines = "\n".join([f"  [{m['id']}] {m['title']} | status={m['status']}" for m in ms]) or "  (无)"
            return f"[{p['id']}] {p['name']}\n  描述: {p['description']}\n  phase: {p['phase']}\n里程碑:\n{ms_lines}"
    return f"项目 {pid} 不存在"

def _update_project(args):
    pid = args.get("id")
    for p in _projects:
        if p["id"] == pid:
            p["name"] = args.get("name", p["name"])
            p["description"] = args.get("description", p["description"])
            p["phase"] = args.get("phase", p["phase"])
            return f"项目 {pid} 已更新"
    return f"项目 {pid} 不存在"

def _delete_project(args):
    global _projects, _milestones
    pid = args.get("id")
    before = len(_projects)
    _projects = [p for p in _projects if p["id"] != pid]
    _milestones = [m for m in _milestones if m["project_id"] != pid]
    return f"删除 {pid}，项目变化 {before}→{len(_projects)}"

def _create_milestone(args):
    global _next_ms_id
    project_id = args.get("project_id")
    title = args.get("title")
    ms = {"id": f"ms_{_next_ms_id:04d}", "project_id": project_id, "title": title, "status": "open"}
    _milestones.append(ms)
    _next_ms_id += 1
    return f"里程碑 [{ms['id']}] {title} 创建成功，关联项目 {project_id}"

def _list_milestones(args):
    if not _milestones:
        return "暂无里程碑"
    lines = [f"[{m['id']}] {m['title']} | project={m['project_id']} | status={m['status']}" for m in _milestones]
    return "\n".join(lines)

def _close_milestone(args):
    ms_id = args.get("id")
    for m in _milestones:
        if m["id"] == ms_id:
            m["status"] = "completed"
            return f"里程碑 {ms_id} 已关闭"
    return f"里程碑 {ms_id} 不存在"

# ── LLM 模拟（确定性）──────────────────────────────────────
TOOL_CALLS = [
    # 演示：注册两个项目
    {"name": "register_project", "args": {"name": "agent-harness-course", "description": "Harness 教学项目", "phase": "production"}},
    {"name": "register_project", "args": {"name": "bounded-memory", "description": "AI 记忆系统", "phase": "development"}},
    # 给项目加里程碑
    {"name": "create_milestone", "args": {"project_id": "proj_0001", "title": "s01 完成 CRUD"}},
    {"name": "create_milestone", "args": {"project_id": "proj_0001", "title": "上线 Dashboard"}},
    {"name": "create_milestone", "args": {"project_id": "proj_0002", "title": "v1 发布"}},
    # 列表验证
    {"name": "list_projects", "args": {}},
    {"name": "list_milestones", "args": {}},
    {"name": "get_project", "args": {"id": "proj_0001"}},
    # 关闭里程碑
    {"name": "close_milestone", "args": {"id": "ms_0001"}},
    {"name": "get_project", "args": {"id": "proj_0001"}},
]

def call_llm(messages):
    """确定性模拟：按顺序触发 TOOL_CALLS"""
    idx = len([m for m in messages if m.get("role") == "tool"])
    if idx < len(TOOL_CALLS):
        tc = TOOL_CALLS[idx]
        return {"role": "assistant", "tool_use": tc["name"], "content": f'调用工具: {tc["name"]}'}
    return {"role": "assistant", "tool_use": None, "content": "done"}

# ── 主循环 ─────────────────────────────────────────────────
def run():
    print("=== s01: Projects & Milestones ===")
    print("[按回车单步执行，按 Q 退出]")
    idx = 0
    while True:
        inp = input()
        if inp.strip().upper() == "Q":
            break
        response = call_llm(MESSAGES)
        MESSAGES.append(response)
        if not response.get("tool_use"):
            print(f"\n最终回复: {response['content']}\n")
            break
        tool_name = response["tool_use"]
        tc = TOOL_CALLS[idx]
        result = TOOL_HANDLERS()[tc["name"]](tc["args"])
        MESSAGES.append({"role": "tool", "content": result})
        print(f"\n[{idx+1}/{len(TOOL_CALLS)}] {tool_name}\n  → {result}\n")
        idx += 1
        if idx >= len(TOOL_CALLS):
            break

if __name__ == "__main__":
    run()

# Toolchain Manager · 工具链管理系统

> "模型是司机，Harness 是车，工具链是 Agent 的装备库。"

一个**从零搭建工具链管理 Agent 的教学仓库**，专注于展示如何逐步构建一个完整的 Toolchain Manager 系统。

---

## 课程理念

**三层知识对应三层架构：**

```
Session（对话）─────▶ 问题演化图谱（GraphSpec）
  vs.
Toolchain（工具链）──▶ 工具链管理系统（Toolchain Manager）
```

| 维度 | Session Evolution Graph | Toolchain Manager |
|------|-------------------------|-------------------|
| 源数据 | `Messages[]` 对话流 | `tools[]` 工具列表 |
| 核心概念 | problem / evolution / chain | tool / project / lifecycle |
| 数据层 | `problem_tracking` / `problem_evolution` | `tools` / `projects` / `costs` |
| 目标 | 从会话提炼问题演化图谱 | 从工具碎片构建项目装备库 |

---

## 学习路径（6 章节递增）

| 章节 | 职责 | 新增能力 | 代码行数 |
|------|------|----------|----------|
| **s01** | 内存 CRUD | Agent 循环 + 基本增删改查 | ~130 行 |
| **s02** | 持久化 | SQLite 写入 + 查询 | ~100 行 |
| **s03** | 工具分发表 | `register_tool` / `list_tools` 工具系统 | ~120 行 |
| **s04** | 项目生命周期 | 工具 ↔ 项目多对多 + 变更历史 | ~150 行 |
| **s05** | FastAPI 层 | REST API + CORS | ~120 行 |
| **s06** | Vue 前端 | 单文件 HTML + API 集成 | ~350 行 |

**核心 Agent 循环（全书不变）：**

```python
while True:
    response = call_llm(messages)              # 发给大模型
    messages.append(response)
    if not response.get("tool_use"):
        return response["content"]            # 无工具调用 → 结束
    result = TOOL_HANDLERS[name](args)        # 执行工具
    messages.append({"role": "tool", "content": result})  # write-back
```

---

## 快速开始

每章独立运行，无需安装依赖（Python 3.10+ 内置 `sqlite3`）：

```bash
# 第1章：内存 CRUD
cd s01-basic-crud && python agent.py

# 第2章：SQLite 持久化
cd s02-sqlite-persist && python agent.py

# 第3章：工具分发表
cd s03-tools-api && python agent.py

# 第4章：项目生命周期
cd s04-projects-lifecycle && python agent.py

# 第5章：FastAPI 服务
cd s05-fastapi-layer && python api.py

# 第6章：Vue 前端
cd s06-vue-frontend && python api.py   # 启动后访问 http://localhost:18902
```

---

## 项目路线图

- [x] s01–s03 — 基础架构（CRUD + 持久化 + 工具分发）
- [x] s04 — 项目生命周期（GraphSpec Phase 4.5 对齐）
- [x] s05 — FastAPI 层
- [x] s06 — Vue 前端
- [x] **打包分发** — `package.py` 一键 zip 打包

---

## 核心数据模型

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────────┐
│    tools     │────▶│   tool_projects  │◀────│    projects      │
│  (工具节点)   │     │   (多对多边)      │     │   (项目空间)      │
└──────────────┘     └──────────────────┘     └──────────────────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐
│   api_keys   │     │    costs     │
│  (密钥存储)   │     │  (月度账单)   │
└──────────────┘     └──────────────┘
```

**主要表结构：**

| 表名 | 用途 |
|------|------|
| `tools` | 工具节点（name, url, category, status...） |
| `categories` | 工具分类（AI Infra, Database, Payments...） |
| `api_keys` | 密钥存储（base64 混淆） |
| `costs` | 月度费用追踪 |
| `projects` | 项目档案（含 lifecycle_phase） |
| `tool_projects` | 工具 ↔ 项目多对多关联 |
| `project_change_history` | 项目变更历史（审计） |
| `monitor_logs` | 状态监控日志 |

---

## 设计原则

1. **增量章节设计** — 每章只增加一层机制，diff 即课件
2. **零依赖运行** — 只用 Python 标准库（sqlite3 + json）
3. **确定性模拟** — `call_llm()` 用固定逻辑模拟 LLM 决策
4. **GraphSpec 对齐** — 项目生命周期字段与 GraphForge 生态一致

<!-- toolchain-manager-course · https://github.com/quick123-666/toolchain-manager-course -->

<h1 align="center">🔥 toolchain-manager-course · 工具链管理 Agent 教学课</h1>

<p align="center">
  <strong>从零搭建工具链管理 Agent · 分章递增式教学</strong><br/>
  <sub>Build a Toolchain Manager step by step — no dependencies, pure stdlib</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" alt="python"/>
  <img src="https://img.shields.io/badge/章节-6%20章-FF6B6B?style=for-the-badge" alt="chapters"/>
  <img src="https://img.shields.io/badge/零依赖-stdlib%20only-2ea44f?style=for-the-badge" alt="stdlib"/>
  <img src="https://img.shields.io/badge/文档-中英双语-red?style=for-the-badge" alt="bilingual"/>
</p>

---

## 📖 课程理念

**三层知识对应三层架构：**

```
Session（对话）─────▶ 问题演化图谱（GraphSpec）
  vs.
Toolchain（工具链）──▶ 工具链管理系统（Toolchain Manager）
```

| 维度 | Session Evolution Graph | Toolchain Manager |
|------|------------------------|-------------------|
| 源数据 | `Messages[]` 对话流 | `tools[]` 工具列表 |
| 核心概念 | problem / evolution / chain | tool / project / lifecycle |
| 数据层 | `problem_tracking` / `evolution` | `tools` / `projects` / `costs` |
| 目标 | 从会话提炼问题演化图谱 | 从工具碎片构建项目装备库 |

---

## 🗺️ 章节路径（6 步递增）

| | 章节 | 核心能力 | 代码行数 |
|---:|------|----------|----------|
| 📦 | **s01** · 内存 CRUD | Agent 循环 + 基本增删改查 | ~130 行 |
| 💾 | **s02** · SQLite 持久化 | 数据库 write/read + 事务 | ~100 行 |
| 🛠️ | **s03** · 工具分发表 | `register_tool` / `list_tools` 系统 | ~120 行 |
| 🏗️ | **s04** · 项目生命周期 | 工具 ↔ 项目多对多 + 变更历史 | ~150 行 |
| ⚡ | **s05** · FastAPI 层 | REST API + CORS + Swagger | ~120 行 |
| 🎨 | **s06** · Vue 前端 | 单文件 HTML + API 集成 | ~350 行 |

**全书不变的核心 Agent 循环：**

```python
while True:
    response = call_llm(messages)              # 发给大模型
    messages.append(response)
    if not response.get("tool_use"):
        return response["content"]             # 无工具调用 → 结束
    result = TOOL_HANDLERS[name](args)        # 执行工具
    messages.append({"role": "tool", "content": result})  # write-back
```

---

## 🚀 快速开始

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

# 第5章：FastAPI 服务（需要 pip install fastapi uvicorn）
cd s05-fastapi-layer && pip install fastapi uvicorn && python api.py

# 第6章：Vue 前端（s05 需先启动）
cd s06-vue-frontend && python agent.py
# 然后访问 http://localhost:18902
```

---

## 📦 打包分发

```bash
python package.py   # 生成 toolchain-manager-{date}.zip
```

包含全部 6 章代码 + 中英双语文档 + MIT License。

---

## 🗂️ 核心数据模型

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

| 表名 | 用途 |
|------|------|
| `tools` | 工具节点（name, url, category, status...） |
| `categories` | 工具分类（AI Infra, Database, Payments...） |
| `api_keys` | 密钥存储（base64 混淆） |
| `costs` | 月度费用追踪 |
| `projects` | 项目档案（含 lifecycle_phase） |
| `tool_projects` | 工具 ↔ 项目多对多关联 |
| `project_change_history` | 项目变更历史（审计） |

---

## 🎯 设计原则

1. **增量章节设计** — 每章只增加一层机制，diff 即课件
2. **零依赖运行** — 只用 Python 标准库（sqlite3 + json）
3. **确定性模拟** — `call_llm()` 用固定逻辑模拟 LLM 决策
4. **GraphSpec 对齐** — 项目生命周期字段与 GraphForge 生态一致

---

## 👤 作者

📧 **[1539489228@qq.com](mailto:1539489228@qq.com)** · GitHub: **[@quick123-666](https://github.com/quick123-666)**

<p align="center">
  <img src="https://img.shields.io/github/stars/quick123-666/toolchain-manager-course?style=social" alt="stars"/>
  <br/><br/>
  <sub>⭐️ 欢迎 Star · 你的支持让项目被更多人发现</sub>
</p>

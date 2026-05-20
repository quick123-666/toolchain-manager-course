<div align="center">

# toolchain-manager-course

### 工具链管理 Agent 教学课 · Build a Toolchain Manager step by step

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![语言](https://img.shields.io/badge/文档-中英双语-red)](README.md)
[![Chapters](https://img.shields.io/badge/Chapters-6%20章-FF6B6B)](./s01-basic-crud/)
[![零依赖](https://img.shields.io/badge/零依赖-stdlib%20only-2ea44f)](.)
[![GraphSpec](https://img.shields.io/badge/Spec-GraphSpec-purple)](./assets/)

**[中文说明](#目录)** · **[English](#english)** · [架构文档](./docs/) · [GraphSpec](./assets/)

**模型是司机，Harness 是车，工具链是 Agent 的装备库。**

*The model drives. The harness is the vehicle. The toolchain is the Agent's arsenal.*

</div>

---

## 目录

- [这是什么](#这是什么)
- [解决什么问题](#解决什么问题)
- [核心特性](#核心特性)
- [系统架构](#系统架构)
- [六章课程](#六章课程)
- [快速开始](#快速开始)
- [数据模型](#数据模型)
- [工具一览](#工具一览)
- [示例输出](#示例输出)
- [设计原则](#设计原则)
- [与相关项目的关系](#与相关项目的关系)
- [路线图](#路线图)
- [贡献](#贡献)
- [许可证](#许可证)
- [GitHub 展示：Pin / Topics](#github-展示pin--topics)
- [English 英文说明](#english)

---

## 这是什么

**toolchain-manager-course（工具链管理 Agent 教学课）** 是一个**从零搭建工具链管理 Agent** 的教学仓库，专注一件事：

> 把零散的 AI 工具（Tool）组织成可管理、可查询的**项目装备库**（Toolchain Manager）。

不是又一个 ChatGPT 套壳，而是可运行的 **Python 实验课**（s01 → s06）：每章只增加一层机制，让你看清「CRUD → 持久化 → 工具分发 → 项目生命周期 → FastAPI → Vue 前端」如何拼装成完整系统。

| 三个词 | 含义 |
|--------|------|
| **Tool（工具）** | `tools[]` 是工具节点，Toolchain Manager 的管理对象 |
| **Chain（链）** | 工具 ↔ 项目多对多关联，形成装备链条 |
| **Manager（管理）** | `projects` / `categories` / `costs` / `api_keys` 完整管理体系 |

---

## 解决什么问题

| 痛点 | 本仓库的做法 |
|------|----------------|
| 工具散落在各处，没有统一管理 | 工具入库：`tools` 表 + 分类体系 |
| 不知道哪些项目用了哪些工具 | 工具 ↔ 项目多对多关联 |
| 工具 API Key 明文存储 | base64 混淆存储，线上换更安全的加密 |
| 想对齐 GraphForge / GraphSpec | 项目生命周期字段与 [GraphSpec](./assets/) 一致 |
| 教程太抽象，看不懂和业务的连接 | 每章 ~150 行可运行代码 + 明确数据语义 |

---

## 核心特性

- **分章增量**：s01 只有 CRUD，s02 加持久化，s03 加工具分发，s04 加项目生命周期，s05 加 FastAPI，s06 加 Vue 前端 —— diff 即课件
- **零依赖演示**：`python agent.py` 即可跑通（LLM 为确定性模拟，便于理解 write-back）
- **GraphSpec 对齐**：数据模型与 GraphForge 生态一致
- **工具链教学法**：与 [session-evolution-graph](https://github.com/quick123-666/session-evolution-graph) 同一体系
- **可扩展**：替换 `call_llm()` 即可接 OpenAI / Claude / Ollama；SQLite 可换 PostgreSQL

---

## 系统架构

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Session   │     │  s01 CRUD层  │     │  s02 持久化层  │     │  s03 工具分发层 │
│  （工具列表） │────▶│  + 基本操作   │────▶│   + SQLite   │────▶│  + categories │
└─────────────┘     └──────────────┘     └──────────────┘     └──────────────┘

                    ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
                    │  s04 项目层   │     │  s05 API层    │     │  s06 前端层    │
                    │  + projects  │────▶│  + FastAPI   │────▶│  + Vue HTML  │
                    └──────────────┘     └──────────────┘     └──────────────┘
```

---

## 六章课程

| 章节 | 目录 | 图谱角色 | 新增能力 | Motto |
|------|------|----------|----------|-------|
| **s01** | [`s01-basic-crud/`](./s01-basic-crud/) | 内存 CRUD | Agent 循环 + 基本增删改查 | 循环本身不「想」，想的是模型 |
| **s02** | [`s02-sqlite-persist/`](./s02-sqlite-persist/) | 持久化层 | SQLite write/read + 事务 | 数据不丢，工具才可靠 |
| **s03** | [`s03-tools-api/`](./s03-tools-api/) | 分发层 | `register_tool` / `list_tools` 系统 | 加工具 = 加 handler，循环不变 |
| **s04** | [`s04-projects-lifecycle/`](./s04-projects-lifecycle/) | 项目层 | 工具 ↔ 项目多对多 + 变更历史 | 没有项目的工具是散兵 |
| **s05** | [`s05-fastapi-layer/`](./s05-fastapi-layer/) | API 层 | REST API + CORS + Swagger | 前端解耦，服务可复用 |
| **s06** | [`s06-vue-frontend/`](./s06-vue-frontend/) | 前端层 | 单文件 HTML + API 集成 | 没有 UI 的工具不好用 |

### Agent 核心循环（全书不变）

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

## 快速开始

### 环境要求

- Python **3.10+**
- 无需安装第三方包（当前章节为教学模拟；s05/s06 需要 `pip install fastapi uvicorn`）

### 克隆与运行

```bash
git clone https://github.com/quick123-666/toolchain-manager-course.git
cd toolchain-manager-course

# 第 1 章：内存 CRUD
python s01-basic-crud/agent.py

# 第 2 章：SQLite 持久化
python s02-sqlite-persist/agent.py

# 第 3 章：工具分发表
python s03-tools-api/agent.py

# 第 4 章：项目生命周期
python s04-projects-lifecycle/agent.py

# 第 5 章：FastAPI 服务（需要 pip install）
pip install fastapi uvicorn
python s05-fastapi-layer/api.py

# 第 6 章：Vue 前端（s05 需先启动）
python s06-vue-frontend/agent.py
# 然后访问 http://localhost:18902
```

### 打包分发

```bash
python package.py   # 生成 toolchain-manager-{date}.zip
```

> [!TIP]
> Windows 终端若中文乱码，可先执行：`$env:PYTHONIOENCODING='utf-8'`

### 推荐学习顺序

1. 读 [`s01-basic-crud/README.md`](./s01-basic-crud/README.md)，跑 `agent.py`
2. 对比 s01 ~ s06 的 `agent.py` diff，只看**新增工具**
3. 读 [`docs/`](./docs/) 理解完整架构
4. （进阶）将 `call_llm` 换成真实 API，把 SQLite 换成 Supabase

---

## 数据模型

### 节点表 `tools`（工具节点）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 如 `tool_0001` |
| `name` | string | 工具名称 |
| `url` | string | 工具地址 |
| `category_id` | int | 分类 ID（外键） |
| `status` | enum | 状态：`活跃` / `停用` / `维护中` |
| `created_at` | datetime | 创建时间 |

### 关联表 `tool_projects`（工具 ↔ 项目多对多）

| 字段 | 类型 | 说明 |
|------|------|------|
| `tool_id` | string | 工具 ID |
| `project_id` | string | 项目 ID |

### 项目表 `projects`（项目档案）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 如 `proj_0001` |
| `name` | string | 项目名称 |
| `lifecycle_phase` | enum | 生命周期阶段 |
| `repo_url` | string | 仓库地址 |
| `created_at` | datetime | 创建时间 |

---

## 工具一览

| 工具 | 章节 | 读/写 | 作用 |
|------|------|-------|------|
| `register_tool` | s01 | 写 | 注册工具节点 |
| `list_tools` | s01/s02 | 读 | 列出所有工具 |
| `update_tool` | s01 | 写 | 更新工具信息 |
| `delete_tool` | s01 | 写 | 删除工具 |
| `register_category` | s03 | 写 | 注册分类 |
| `store_api_key` | s03 | 写 | 存储 API Key（base64 混淆）|
| `track_monthly_cost` | s03 | 写 | 记录月度费用 |
| `register_project` | s04 | 写 | 注册项目档案 |
| `assign_tool_to_project` | s04 | 写 | 工具 ↔ 项目关联 |
| `get_project_tools` | s04 | 读 | 查询项目所用工具 |

---

## 示例输出

**s02 运行后**（工具列表 + SQLite 持久化）：

```text
【tools 工具节点表】
  [tool_0001] OpenAI API   | category=AI Infra  | status=活跃
  [tool_0002] Supabase     | category=Database   | status=活跃
  [tool_0003] Stripe       | category=Payments   | status=活跃

【toolchain.db 已持久化，进程重启后数据不丢失】
```

**s04 运行后**（项目生命周期）：

```text
【projects 项目档案】
  [proj_0001] agent-harness-course  | phase=production
  [proj_0002] bounded-memory         | phase=development

【tool_projects 关联表】
  [tool_0001] OpenAI API   --belongs to--> [proj_0001] agent-harness-course
  [tool_0002] Supabase     --belongs to--> [proj_0001] agent-harness-course
  [tool_0003] Stripe       --belongs to--> [proj_0002] bounded-memory
```

---

## 设计原则

1. **增量章节设计** — 每章只增加一层机制，diff 即课件
2. **零依赖运行** — 只用 Python 标准库（sqlite3 + json）
3. **确定性模拟** — `call_llm()` 用固定逻辑模拟 LLM 决策
4. **GraphSpec 对齐** — 项目生命周期字段与 GraphForge 生态一致
5. **循环稳定，工具增长** — 与 [session-evolution-graph](https://github.com/quick123-666/session-evolution-graph) 同一 Agent Harness 体系

> [!NOTE]
> 当前 `call_llm()` 为**确定性模拟**（按轮次触发工具），用于教学。生产环境请替换为真实 LLM，并增加幂等、鉴权与审计。

---

## 与相关项目的关系

| 项目 | 关系 |
|------|------|
| [session-evolution-graph](https://github.com/quick123-666/session-evolution-graph) | 姊妹课：工具链管理 ↔ 会话演化图谱，同一 GraphSpec 生态 |
| [Learn Claude Code](https://learn.shareai.run/en/) | 通用 Harness 教学法；本仓库是其「工具链专题课」 |
| [GraphSpec / GraphForge](./assets/) | 数据规范参考 |
| [star-level](https://github.com/quick123-666/star-level) | 同作者的 Next.js 全栈示例 |
| [bounded-memory](https://github.com/quick123-666/bounded-memory) | 同作者的 AI 记忆系统 |

---

## 路线图

- [x] s01 — Agent 循环 + 内存 CRUD
- [x] s02 — SQLite 持久化
- [x] s03 — 工具分发表（categories / api_keys / costs）
- [x] s04 — 项目生命周期（工具 ↔ 项目多对多 + 变更历史）
- [x] s05 — FastAPI 层 + Swagger 文档
- [x] s06 — Vue 单文件前端 + API 集成
- [x] **打包分发** — `package.py` 一键 zip
- [ ] s07 — 真实 LLM 接入（OpenAI 兼容 API）
- [ ] 可视化：工具依赖图前端

欢迎通过 [Issue](https://github.com/quick123-666/toolchain-manager-course/issues) 讨论需求。

---

## 贡献

1. Fork 本仓库
2. 创建分支：`git checkout -b feature/your-idea`
3. 提交改动：`git commit -m "feat: 描述你的改动"`
4. 推送并发起 Pull Request

小步提交、清晰 commit message，与课程精神一致。

---

## 许可证

本项目采用 [MIT License](./LICENSE) 开源。

---

## GitHub 展示：Pin / Topics

| 操作 | 说明 |
|------|------|
| **Pin 到个人主页** | 在 [你的主页](https://github.com/quick123-666) 点 **Customize your pins**，把本仓库固定到最上方（最多 6 个） |
| **Topics 标签** | 仓库 **About → Edit**，建议添加：`agent` `llm` `toolchain` `python` `graphspec` `knowledge-graph` |
| **详细图文步骤** | 见 [docs/github-展示设置.md](./docs/github-展示设置.md) |

---

<a id="english"></a>

## English

### Overview

**toolchain-manager-course** is a hands-on course for building a **Toolchain Manager Agent** that organizes scattered AI tools into a manageable, queryable **project arsenal**.

Each chapter adds exactly one layer (CRUD → persistence → tool registry → project lifecycle → FastAPI → Vue frontend). The core Agent loop stays unchanged — diff is the courseware.

### Quick Start

```bash
git clone https://github.com/quick123-666/toolchain-manager-course.git
cd toolchain-manager-course

python s01-basic-crud/agent.py
python s02-sqlite-persist/agent.py
python s03-tools-api/agent.py
python s04-projects-lifecycle/agent.py

pip install fastapi uvicorn
python s05-fastapi-layer/api.py
python s06-vue-frontend/agent.py
# Visit http://localhost:18902
```

### Chapters

| Ch | Folder | Role | New Capability |
|----|--------|------|----------------|
| s01 | [s01-basic-crud](./s01-basic-crud/) | CRUD layer | Agent loop + basic CRUD |
| s02 | [s02-sqlite-persist](./s02-sqlite-persist/) | Persistence | SQLite write/read + transactions |
| s03 | [s03-tools-api](./s03-tools-api/) | Registry | `register_tool` / `list_tools` system |
| s04 | [s04-projects-lifecycle](./s04-projects-lifecycle/) | Project layer | Tool ↔ Project many-to-many + history |
| s05 | [s05-fastapi-layer](./s05-fastapi-layer/) | API layer | REST API + CORS + Swagger |
| s06 | [s06-vue-frontend](./s06-vue-frontend/) | Frontend | Single-file HTML + API integration |

### Core Agent Loop（unchanged across all chapters）

```python
while True:
    response = call_llm(messages)
    messages.append(response)
    if not response.get("tool_use"):
        return response["content"]
    result = TOOL_HANDLERS[name](args)
    messages.append({"role": "tool", "content": result})
```

### Features

- Incremental chapters (CRUD → persistence → registry → lifecycle → API → frontend)
- Zero deps for teaching demos — swap `call_llm()` for production
- GraphSpec-aligned schema
- Same harness pedagogy as [session-evolution-graph](https://github.com/quick123-666/session-evolution-graph)

### Roadmap

- [x] s01–s06 labs
- [ ] s07 real LLM API integration
- [ ] graph visualization UI

### License

[MIT](./LICENSE)

---

<div align="center">

**如果对你有帮助，欢迎 Star / Star if helpful**

[quick123-666](https://github.com/quick123-666) · [报告问题 / Issues](https://github.com/quick123-666/toolchain-manager-course/issues)

</div>

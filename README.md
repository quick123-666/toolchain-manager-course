<div align="center">

# toolchain-manager-course

### 项目管理系统教学课 · Build a Project Manager step by step

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![语言](https://img.shields.io/badge/文档-中英双语-red)](README.md)
[![Chapters](https://img.shields.io/badge/Chapters-6%20章-FF6B6B)](./s01-projects-milestones/)
[![零依赖](https://img.shields.io/badge/零依赖-stdlib%20only-2ea44f)](.)
[![GraphSpec](https://img.shields.io/badge/Spec-GraphSpec-purple)](./docs/)

**[中文说明](#目录)** · **[English](#english)** · [GraphSpec](./docs/)

**项目是一切管理的起点，没有项目的工具是散的。**

*Projects are the starting point of all management.*

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
- [示例输出](#示例输出)
- [设计原则](#设计原则)
- [与相关项目的关系](#与相关项目的关系)
- [路线图](#路线图)
- [许可证](#许可证)
- [English](#english)

---

## 这是什么

**toolchain-manager-course（项目管理系统教学课）** 是一个**从零搭建项目管理 Agent** 的教学仓库，专注一件事：

> 把项目（Projects）、里程碑（Milestones）、任务（Tasks）、时间线（Timeline）组织成可管理、可追踪的**项目装备库**。

不是又一个 ChatGPT 套壳，而是可运行的 **Python 实验课**（s01 → s06）：每章只增加一层机制，让你看清「CRUD → 持久化 → 任务状态 → 时间线 → FastAPI → Dashboard」如何拼装成完整系统。

| 三个词 | 含义 |
|--------|------|
| **Project（项目）** | `projects` 是顶层容器，管理目标 |
| **Milestone（里程碑）** | `milestones` 是目标分解，阶段标记 |
| **Task（任务）** | `tasks` 是行动单元，可追踪状态 |

---

## 解决什么问题

| 痛点 | 本仓库的做法 |
|------|----------------|
| 项目散落在文档/脑子里，没有统一管理 | 项目入库：`projects` 表 |
| 里程碑只是想法，没有关联任务 | 里程碑 → 任务 三层结构 |
| 不知道任务卡在哪，健康度靠感觉 | 健康度三维计算（任务完成率+里程碑达成+阻塞惩罚）|
| 做过的决定找不到记录 | `timeline_events` 全局审计日志 |
| 想对齐 GraphForge / GraphSpec | 项目生命周期字段与 [GraphSpec](./docs/) 一致 |

---

## 核心特性

- **分章增量**：s01 只有 CRUD，s02 加持久化，s03 加工具分发，s04 加项目生命周期，s05 加 FastAPI，s06 加 Vue 前端 —— diff 即课件
- **零依赖演示**：`python agent.py` 即可跑通（LLM 为确定性模拟，便于理解 write-back）
- **GraphSpec 对齐**：数据模型与 GraphForge 生态一致
- **可扩展**：替换 `call_llm()` 即可接 OpenAI / Claude / Ollama；SQLite 可换 PostgreSQL

---

## 系统架构

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Session   │     │  s01 CRUD层  │     │  s02 持久化层  │
│  （用户指令） │────▶│  + Projects │────▶│  + SQLite   │
└─────────────┘     └──────────────┘     └──────────────┘
                    ┌──────────────┐     ┌──────────────┐
                    │  s03 任务层   │     │  s04 时间线层  │
                    │  + Tasks    │────▶│  + Timeline │
                    └──────────────┘     └──────────────┘
                    ┌──────────────┐     ┌──────────────┐
                    │  s05 API层   │     │  s06 前端层   │
                    │  + FastAPI  │────▶│  + Dashboard │
                    └──────────────┘     └──────────────┘
```

---

## 六章课程

| 章节 | 目录 | 核心实体 | 新增能力 | Motto |
|------|------|----------|----------|-------|
| **s01** | [`s01-projects-milestones/`](./s01-projects-milestones/) | `projects` + `milestones` | 内存 CRUD | 项目是所有管理的起点 |
| **s02** | [`s02-tasks-status/`](./s02-tasks-status/) | `tasks` | SQLite 持久化 + 状态机 | 没有任务的里程碑是空的 |
| **s03** | [`s03-health-calc/`](./s03-health-calc/) | `health_score` | 健康度三维计算 | 数字告诉你哪里要救火 |
| **s04** | [`s04-timeline-events/`](./s04-timeline-events/) | `timeline_events` | 时间线记录 + 查询 | 做过的每件事都有迹可查 |
| **s05** | [`s05-fastapi-auth/`](./s05-fastapi-auth/) | FastAPI + Auth | REST API + Swagger + 多 Key | 服务可复用，前端解耦 |
| **s06** | [`s06-vue-dashboard/`](./s06-vue-dashboard/) | Vue Dashboard | 可视化 + API 集成 | 没有界面的系统不好用 |

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
- 无需安装第三方包（s05 需要 `pip install fastapi uvicorn`）

### 克隆与运行

```bash
git clone https://github.com/quick123-666/toolchain-manager-course.git
cd toolchain-manager-course

# 第 1 章：项目 + 里程碑 CRUD
python s01-projects-milestones/agent.py

# 第 2 章：任务 + SQLite 持久化
python s02-tasks-status/agent.py

# 第 3 章：健康度计算
python s03-health-calc/agent.py

# 第 4 章：时间线记录
python s04-timeline-events/agent.py

# 第 5 章：FastAPI 服务（需要 pip install）
pip install fastapi uvicorn
python s05-fastapi-auth/api.py

# 第 6 章：Dashboard（s05 需先启动）
# 双击 s06-vue-dashboard/index.html 在浏览器打开
```

### 打包分发

```bash
python package.py   # 生成 toolchain-manager-course-{date}.zip
```

> [!TIP]
> Windows 终端若中文乱码，可先执行：`$env:PYTHONIOENCODING='utf-8'`

---

## 数据模型

### `projects` 项目表

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 如 `proj_0001` |
| `name` | string | 项目名称 |
| `phase` | enum | `planning` / `development` / `production` / `archived` |
| `created_at` | datetime | 创建时间 |

### `milestones` 里程碑表

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 如 `ms_0001` |
| `project_id` | string | 外键 → projects |
| `title` | string | 里程碑名称 |
| `status` | enum | `open` / `completed` |

### `tasks` 任务表

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 如 `task_0001` |
| `project_id` | string | 外键 → projects |
| `milestone_id` | string | 外键 → milestones |
| `title` | string | 任务名称 |
| `status` | enum | `todo` / `in_progress` / `in_review` / `done` / `cancelled` / `blocked` |
| `priority` | enum | `low` / `medium` / `high` / `urgent` |

### `timeline_events` 时间线表

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 如 `evt_000001` |
| `project_id` | string | 外键 → projects |
| `event_type` | enum | `BUSINESS` / `TECHNICAL` / `DECISION` |
| `category` | string | 具体事件类型 |
| `title` | string | 事件标题 |
| `priority` | enum | `P0` / `P1` / `P2` / `P3` |
| `source` | string | `pm_system` |

---

## 示例输出

**s03 健康度计算**：

```
🟢 项目 [proj_0001] agent-harness-course | phase=production
健康度: ███████░░░ 71.4/100
任务: 3/5 完成 | 🔴 阻塞: 1
阻塞任务:
  [task_0004] 部署
```

**s04 时间线查询**：

```
=== 项目 proj_0001 时间线 ===
🟠 [evt_000005] 2026-05-20 10:00 | health_warning | 健康度低于70%
🟡 [evt_000004] 2026-05-20 09:55 | task_done | 写代码完成
🟡 [evt_000003] 2026-05-20 09:50 | task_created | 写代码
🟡 [evt_000002] 2026-05-20 09:45 | milestone_created | 上线v1
🔴 [evt_000001] 2026-05-20 09:40 | project_created | agent-harness-course 上线
```

---

## 设计原则

1. **增量章节设计** — 每章只增加一层机制，diff 即课件
2. **零依赖运行** — 只用 Python 标准库（sqlite3 + json）
3. **确定性模拟** — `call_llm()` 用固定逻辑模拟 LLM 决策
4. **GraphSpec 对齐** — 项目生命周期字段与 GraphForge 生态一致
5. **循环稳定，工具增长** — 与 [session-evolution-graph](https://github.com/quick123-666/session-evolution-graph) 同一 Agent Harness 体系

---

## 与相关项目的关系

| 项目 | 关系 |
|------|------|
| [plan-forge-build](https://github.com/quick123-666/plan-forge-build) | 生产版：本仓库的教学蓝图 |
| [session-evolution-graph](https://github.com/quick123-666/session-evolution-graph) | 姊妹课：会话演化图谱，同一 GraphSpec 生态 |
| [Learn Claude Code](https://learn.shareai.run/en/) | 通用 Harness 教学法；本仓库是其「项目管理系统专题课」 |
| [GraphSpec / GraphForge](./docs/) | 数据规范参考 |

---

## 路线图

- [x] s01 — Projects + Milestones CRUD
- [x] s02 — Tasks + SQLite 持久化
- [x] s03 — 健康度三维计算
- [x] s04 — Timeline Events 审计日志
- [x] s05 — FastAPI + 多 Key 认证
- [x] s06 — Vue Dashboard
- [ ] s07 — WebSocket 实时推送
- [ ] s08 — 真实 LLM 接入

---

## 许可证

本项目采用 [MIT License](./LICENSE) 开源。

---

<a id="english"></a>

## English

### Overview

**toolchain-manager-course** is a hands-on course for building a **Project Manager Agent** that organizes projects, milestones, tasks and timeline events into a manageable, trackable system.

Each chapter adds exactly one layer (Projects CRUD → persistence → task status → timeline → FastAPI → Dashboard). The core Agent loop stays unchanged — diff is the courseware.

### Quick Start

```bash
git clone https://github.com/quick123-666/toolchain-manager-course.git
cd toolchain-manager-course

python s01-projects-milestones/agent.py
python s02-tasks-status/agent.py
python s03-health-calc/agent.py
python s04-timeline-events/agent.py

pip install fastapi uvicorn
python s05-fastapi-auth/api.py
# then open s06-vue-dashboard/index.html
```

### Chapters

| Ch | Folder | Core Entity | New Capability |
|----|--------|--------------|----------------|
| s01 | [s01-projects-milestones](./s01-projects-milestones/) | projects + milestones | In-memory CRUD |
| s02 | [s02-tasks-status](./s02-tasks-status/) | tasks | SQLite persistence + status machine |
| s03 | [s03-health-calc](./s03-health-calc/) | health_score | 3-dimension health calculation |
| s04 | [s04-timeline-events](./s04-timeline-events/) | timeline_events | Audit log + query |
| s05 | [s05-fastapi-auth](./s05-fastapi-auth/) | FastAPI + Auth | REST API + Swagger + multi-key |
| s06 | [s06-vue-dashboard](./s06-vue-dashboard/) | Vue Dashboard | Visualization + API integration |

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

### Roadmap

- [x] s01–s06 labs
- [ ] s07 WebSocket real-time push
- [ ] s08 real LLM API integration

### License

[MIT](./LICENSE)

---

<div align="center">

**如果对你有帮助，欢迎 Star / Star if helpful**

[quick123-666](https://github.com/quick123-666) · [报告问题 / Issues](https://github.com/quick123-666/toolchain-manager-course/issues)

</div>

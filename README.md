<!-- toolchain-manager-course · https://github.com/quick123-666/toolchain-manager-course -->

<h1 align="center">🔥 toolchain-manager-course · 工具链管理 Agent 教学课</h1>

<p align="center">
  <strong>从零搭建工具链管理 Agent · 分章递增式教学</strong><br/>
  <sub>Build a Toolchain Manager step by step — Incremental chapter-based teaching</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" alt="python"/>
  <img src="https://img.shields.io/badge/章节-6%20章-FF6B6B?style=for-the-badge" alt="chapters"/>
  <img src="https://img.shields.io/badge/零依赖-stdlib%20only-2ea44f?style=for-the-badge" alt="stdlib"/>
  <img src="https://img.shields.io/badge/文档-中英双语-red?style=for-the-badge" alt="bilingual"/>
</p>

---

## 🔥 代表作 · 点卡片直达仓库

> 不依赖主页 Pin，下面就是我想让你先看到的项目（点标题或按钮进入）。

### ⭐ toolchain-manager-course · 工具链管理 Agent 教学课

<p align="left">
  <a href="https://github.com/quick123-666/toolchain-manager-course">
    <img src="https://img.shields.io/github/stars/quick123-666/toolchain-manager-course?style=social" alt="stars"/>
  </a>
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" alt="python"/>
  <img src="https://img.shields.io/badge/章节-6%20章-FF6B6B" alt="chapters"/>
  <img src="https://img.shields.io/badge/零依赖-stdlib%20only-2ea44f" alt="stdlib"/>
  <img src="https://img.shields.io/badge/文档-中英双语-red" alt="bilingual"/>
</p>

**从零搭建工具链管理 Agent · 分章递增式教学** — 6 章（s01→s06），零依赖，纯标准库，对齐 GraphSpec。

| | |
|---|---|
| **适合谁** | 想学 Agent 循环 / 工具链管理 / 图谱构建，不想啃十万行源码的人 |
| **你能得到** | 可运行的 Python 实验课 + 架构图 + 中英 README + 一键打包 |
| **立刻进入** | 👉 **[打开 toolchain-manager-course](https://github.com/quick123-666/toolchain-manager-course)** |

```text
s01 内存CRUD → s02 SQLite持久化 → s03 工具分发表
  → s04 项目生命周期 → s05 FastAPI层 → s06 Vue前端
```

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

```bash
# 第1章：内存 CRUD
cd s01-basic-crud && python agent.py

# 第2章：SQLite 持久化
cd s02-sqlite-persist && python agent.py

# 第3章：工具分发表
cd s03-tools-api && python agent.py

# 第4章：项目生命周期
cd s04-projects-lifecycle && python agent.py

# 第5章：FastAPI 服务（pip install required）
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

---

## 👤 作者

📧 **[1539489228@qq.com](mailto:1539489228@qq.com)** · GitHub: **[@quick123-666](https://github.com/quick123-666)**

<p align="center">
  <img src="https://img.shields.io/github/stars/quick123-666/toolchain-manager-course?style=social" alt="stars"/>
  <br/><br/>
  <sub>⭐️ 欢迎 Star · 你的支持让项目被更多人发现</sub>
</p>

<!-- toolchain-manager-course · https://github.com/quick123-666/toolchain-manager-course -->

<h1 align="center">🔥 toolchain-manager-course · Toolchain Manager Agent Kurs</h1>

<p align="center">
  <strong>Toolchain Manager Agent von Grund auf aufbauen · Kapitelweise inkrementelles Lehren</strong><br/>
  <sub>从零搭建工具链管理 Agent · 分章递增式教学</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" alt="python"/>
  <img src="https://img.shields.io/badge/Chapters-6-FF6B6B?style=for-the-badge" alt="chapters"/>
  <img src="https://img.shields.io/badge/Zero%20Dep-stdlib%20only-2ea44f?style=for-the-badge" alt="stdlib"/>
  <img src="https://img.shields.io/badge/中英双语-bilingual-red?style=for-the-badge" alt="bilingual"/>
</p>

---

## 📖 Course Philosophy

**Three-layer knowledge maps to three-layer architecture:**

```
Session（Dialogue）─────▶ Problem Evolution Graph（GraphSpec）
  vs.
Toolchain ──────────────▶ Toolchain Manager System
```

| Dimension | Session Evolution Graph | Toolchain Manager |
|-----------|----------------------|------------------|
| Source Data | `Messages[]` dialog flow | `tools[]` tool list |
| Core Concepts | problem / evolution / chain | tool / project / lifecycle |
| Data Layer | `problem_tracking` / `evolution` | `tools` / `projects` / `costs` |
| Goal | Build problem graph from conversations | Assemble project arsenal from tool fragments |

---

## 🗺️ Chapter Path（6 Incremental Steps）

| | Chapter | Core Capability | LOC |
|---:|--------|----------------|-----|
| 📦 | **s01** · In-Memory CRUD | Agent loop + basic CRUD | ~130 |
| 💾 | **s02** · SQLite Persistence | DB write/read + transactions | ~100 |
| 🛠️ | **s03** · Tool Registry | `register_tool` / `list_tools` system | ~120 |
| 🏗️ | **s04** · Project Lifecycle | Tool ↔ Project many-to-many + change history | ~150 |
| ⚡ | **s05** · FastAPI Layer | REST API + CORS + Swagger | ~120 |
| 🎨 | **s06** · Vue Frontend | Single-file HTML + API integration | ~350 |

**Core Agent Loop（unchanged across all chapters）：**

```python
while True:
    response = call_llm(messages)              # send to LLM
    messages.append(response)
    if not response.get("tool_use"):
        return response["content"]             # no tool → done
    result = TOOL_HANDLERS[name](args)         # execute tool
    messages.append({"role": "tool", "content": result})  # write-back
```

---

## 🚀 Quick Start

Each chapter runs independently. No dependencies required（Python 3.10+ built-in `sqlite3`）：

```bash
# Chapter 1: In-Memory CRUD
cd s01-basic-crud && python agent.py

# Chapter 2: SQLite Persistence
cd s02-sqlite-persist && python agent.py

# Chapter 3: Tool Registry
cd s03-tools-api && python agent.py

# Chapter 4: Project Lifecycle
cd s04-projects-lifecycle && python agent.py

# Chapter 5: FastAPI Service（pip install required）
cd s05-fastapi-layer && pip install fastapi uvicorn && python api.py

# Chapter 6: Vue Frontend（s05 must be running first）
cd s06-vue-frontend && python agent.py
# Then visit http://localhost:18902
```

---

## 📦 Packaging

```bash
python package.py   # generates toolchain-manager-{date}.zip
```

Includes all 6 chapters + bilingual docs + MIT License.

---

## 🗂️ Core Data Model

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────────┐
│    tools     │────▶│   tool_projects  │◀────│    projects      │
│  (tool node) │     │   (many-to-many) │     │  (project space) │
└──────────────┘     └──────────────────┘     └──────────────────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐
│   api_keys   │     │    costs     │
│  (key store) │     │ (monthly bill)│
└──────────────┘     └──────────────┘
```

| Table | Purpose |
|-------|---------|
| `tools` | Tool node（name, url, category, status...） |
| `categories` | Tool categories（AI Infra, Database, Payments...） |
| `api_keys` | Key storage（base64 obfuscated） |
| `costs` | Monthly cost tracking |
| `projects` | Project archive（incl. lifecycle_phase） |
| `tool_projects` | Tool ↔ Project many-to-many |
| `project_change_history` | Project change history（audit） |

---

## 🎯 Design Principles

1. **Incremental chapters** — Each chapter adds exactly one layer; diff is the courseware
2. **Zero dependencies** — Python standard library only（sqlite3 + json）
3. **Deterministic simulation** — `call_llm()` uses fixed logic to simulate LLM decisions
4. **GraphSpec alignment** — Project lifecycle fields aligned with GraphForge ecosystem

---

## 👤 Author

📧 **[1539489228@qq.com](mailto:1539489228@qq.com)** · GitHub: **[@quick123-666](https://github.com/quick123-666)**

<p align="center">
  <img src="https://img.shields.io/github/stars/quick123-666/toolchain-manager-course?style=social" alt="stars"/>
  <br/><br/>
  <sub>⭐️ Star the repo · Your support helps the project get discovered</sub>
</p>

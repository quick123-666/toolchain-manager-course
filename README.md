# Toolchain Manager · Course

> "Model is the driver, Harness is the car, and Toolchain is the Agent's arsenal."

A **chapter-by-chapter teaching repository** for building a complete Toolchain Manager system from scratch.

---

## Course Philosophy

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

## Learning Path（6 Incremental Chapters）

| Chapter | Responsibility | New Capability | LOC |
|---------|---------------|----------------|-----|
| **s01** | In-Memory CRUD | Agent loop + basic CRUD | ~130 |
| **s02** | Persistence | SQLite write + query | ~100 |
| **s03** | Tool Registry | `register_tool` / `list_tools` system | ~120 |
| **s04** | Project Lifecycle | Tool ↔ Project many-to-many + change history | ~150 |
| **s05** | FastAPI Layer | REST API + CORS + Swagger | ~120 |
| **s06** | Vue Frontend | Single-file HTML + API integration | ~350 |

**Core Agent Loop（unchanged across all chapters）:**

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

## Quick Start

Each chapter runs independently. No dependencies required（Python 3.10+ built-in `sqlite3`）:

```bash
# Chapter 1: In-Memory CRUD
cd s01-basic-crud && python agent.py

# Chapter 2: SQLite Persistence
cd s02-sqlite-persist && python agent.py

# Chapter 3: Tool Registry
cd s03-tools-api && python agent.py

# Chapter 4: Project Lifecycle
cd s04-projects-lifecycle && python agent.py

# Chapter 5: FastAPI Service
cd s05-fastapi-layer && python api.py

# Chapter 6: Vue Frontend（s05 must be running first）
cd s06-vue-frontend && python agent.py
# Then visit http://localhost:18902
```

---

## Project Roadmap

- [x] s01–s03 — Foundation（CRUD + persistence + tool registry）
- [x] s04 — Project lifecycle（aligned with GraphSpec Phase 4.5）
- [x] s05 — FastAPI layer
- [x] s06 — Vue frontend
- [x] **Packaging** — `package.py` one-command zip bundle

---

## Core Data Model

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

**Tables:**

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

## Design Principles

1. **Incremental chapters** — Each chapter adds exactly one layer; diff is the courseware
2. **Zero dependencies** — Python standard library only（sqlite3 + json）
3. **Deterministic simulation** — `call_llm()` uses fixed logic to simulate LLM decisions
4. **GraphSpec alignment** — Project lifecycle fields aligned with GraphForge ecosystem

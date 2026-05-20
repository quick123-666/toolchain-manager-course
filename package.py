"""
一键打包脚本
============
在 Windows (Git Bash / MSYS) 下运行:

    python scripts/package.py

输出:
    toolchain-manager-{date}.zip
    ├── s01-basic-crud/
    ├── s02-sqlite-persist/
    ├── s03-tools-api/
    ├── s04-projects-lifecycle/
    ├── s05-fastapi-layer/
    ├── s06-vue-frontend/
    ├── README-zh.md
    └── LICENSE
"""

import zipfile
import os
import datetime

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = PROJECT_ROOT  # 输出到项目目录
DATE = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
ZIP_NAME = f"toolchain-manager-{DATE}.zip"
ZIP_PATH = os.path.join(OUTPUT_DIR, ZIP_NAME)

# 只打包这些子目录和文件
CHAPS = [
    "s01-basic-crud",
    "s02-sqlite-persist",
    "s03-tools-api",
    "s04-projects-lifecycle",
    "s05-fastapi-layer",
    "s06-vue-frontend",
]
ROOT_FILES = [
    "README-zh.md",
    "README.md",
    "LICENSE",
    "package.py",        # 本脚本（供解压后再次打包）
]

def gen_readme():
    """生成 README.md（英文版，基于 README-zh.md 内容）"""
    return """# Toolchain Manager

> "Models are drivers, Harness is the car, Toolchain is the Agent's gear."

A **step-by-step teaching repository** for building a complete Toolchain Manager system, modeled after [session-evolution-graph](https://github.com/quick123-666/session-evolution-graph).

---

## Learning Path (6 Chapters)

| Chapter | Focus | New Capability | LOC |
|---------|-------|-----------------|-----|
| **s01** | In-Memory CRUD | Agent loop + basic CRUD | ~130 |
| **s02** | SQLite Persistence | DB write + query | ~100 |
| **s03** | Tool Dispatch | register_tool / list_tools | ~120 |
| **s04** | Project Lifecycle | Many-to-many + change history | ~150 |
| **s05** | FastAPI Layer | REST API + CORS + Swagger | ~120 |
| **s06** | Vue Frontend | Single-file HTML + API | ~350 |

**Core Agent Loop (unchanged across all chapters):**

```python
while True:
    response = call_llm(messages)
    messages.append(response)
    if not response.get("tool_use"):
        return response["content"]
    result = TOOL_HANDLERS[name](args)
    messages.append({"role": "tool", "content": result})
```

---

## Quick Start

```bash
# Chapter 1: In-Memory CRUD
cd s01-basic-crud && python agent.py

# Chapter 2: SQLite
cd s02-sqlite-persist && python agent.py

# Chapter 3: Tool Dispatch
cd s03-tools-api && python agent.py

# Chapter 4: Project Lifecycle
cd s04-projects-lifecycle && python agent.py

# Chapter 5: FastAPI (needs: pip install fastapi uvicorn)
cd s05-fastapi-layer && python api.py

# Chapter 6: Vue Frontend
# First run: python agent.py (generates index.html)
# Then start s05 api.py and visit http://localhost:18902
```

---

## Data Model

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────────┐
│    tools     │────▶│   tool_projects  │◀────│    projects      │
│  (Tool Node) │     │   (M:N edge)     │     │   (Project)      │
└──────────────┘     └──────────────────┘     └──────────────────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐
│   api_keys   │     │    costs     │
│  (Key Store) │     │ (Monthly $)  │
└──────────────┘     └──────────────┘
```

---

## Design Principles

1. **Incremental chapters** — each adds exactly one layer, diff is the curriculum
2. **Zero-dependency** — pure Python stdlib (sqlite3 + json)
3. **Deterministic simulation** — `call_llm()` uses fixed logic for teaching
4. **GraphSpec-aligned** — project lifecycle fields match GraphForge ecosystem

---

See [README-zh.md](README-zh.md) for Chinese documentation.
"""

def gen_package_py():
    """将自身复制到输出目录（方便二次打包）"""
    return open(__file__, encoding="utf-8").read()


def main():
    print(f"[package] Project root: {PROJECT_ROOT}")
    print(f"[package] Output: {ZIP_PATH}")

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        # 根目录文件
        for fname in ROOT_FILES:
            fpath = os.path.join(PROJECT_ROOT, fname)
            if fname == "package.py":
                fpath = __file__  # 打包自身（脚本在 PROJECT_ROOT 下）
            if os.path.exists(fpath):
                zf.write(fpath, arcname=os.path.join("toolchain-manager", fname))
                print(f"  + {fname}")

        # 章节
        for chap in CHAPS:
            chap_dir = os.path.join(PROJECT_ROOT, chap)
            for root, dirs, files in os.walk(chap_dir):
                for fname in files:
                    if fname.endswith(".pyc"):
                        continue
                    full = os.path.join(root, fname)
                    rel = os.path.relpath(full, PROJECT_ROOT)
                    zf.write(full, arcname=os.path.join("toolchain-manager", rel))
                    print(f"  + {rel}")

        # 生成 README.md
        zf.writestr(
            os.path.join("toolchain-manager", "README.md"),
            gen_readme(),
            compress_type=zipfile.ZIP_DEFLATED
        )
        print(f"  + README.md (generated)")

    print(f"\n[package] Done! {ZIP_PATH}")
    print(f"[package] Size: {os.path.getsize(ZIP_PATH) / 1024:.1f} KB")


if __name__ == "__main__":
    main()

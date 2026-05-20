# s04: 项目生命周期

> 本章新增：`projects` 表 + `tool_projects` 多对多 + `project_change_history` 变更历史

## 新增概念

- **项目档案** — 每个项目记录：repo_url、packaging_dir、askdb_backup_dir、spec_file
- **生命周期阶段** — `lifecycle_phase` 字段，对齐 GraphSpec（Phase_0 ~ Phase_5）
- **多对多关联** — 一个工具可属于多个项目（tool_projects 表）
- **变更历史审计** — 所有字段变更自动写入 `project_change_history`，不可篡改
- **GraphSpec Phase 4.5 对齐** — 项目注册 API `register_project` 支持一键创建完整档案

## 表结构（本章新增）

| 表名 | 用途 | 关联 |
|------|------|------|
| `projects` | 项目档案（name, repo_url, packaging_dir, lifecycle_phase...） | — |
| `project_change_history` | 变更历史（project_id, field, old_value, new_value） | → `projects.id` |
| `tool_projects` | 工具 ↔ 项目多对多关联 | `tool_id` + `project_id` |

## 新增工具命令

| 命令 | 作用 |
|------|------|
| `list_projects` | 列出所有项目 |
| `register_project project_name=xxx description=xxx repo_url=xxx lifecycle_phase=Phase_4_5` | 注册/更新项目 |
| `get_project name=xxx` | 获取项目详情（含关联工具和变更历史） |
| `update_project name=xxx lifecycle_phase=Phase_5` | 更新项目字段（自动记录历史） |
| `rename_project name=xxx new_name=xxx` | 项目改名（记录历史） |
| `link_tool tool_id=1 project=xxx` | 工具关联项目 |
| `unlink_tool tool_id=1 project=xxx` | 工具解除关联 |
| `get_tool_projects tool_id=1` | 查某工具关联的项目 |

## 变更历史机制

```python
def update_project_fields(name, **fields):
    for field in ["name","description","repo_url","packaging_dir",
                  "askdb_backup_dir","spec_file","lifecycle_phase"]:
        new_val = fields.get(field)
        if new_val is not None and new_val != row[field]:
            # 记录变更历史
            c.execute("""
                INSERT INTO project_change_history (project_id, field, old_value, new_value)
                VALUES (?, ?, ?, ?)
            """, (row["id"], field, str(row[field]), str(new_val)))
```

## 与 s03 的 diff

```
+ projects 表               # 项目档案
+ project_change_history   # 变更历史（审计）
+ tool_projects 表         # 多对多关联
+ register_project         # GraphSpec 一键注册
+ rename_project / update_project  # 记录历史的修改操作
+ 种子数据扩展分类至 7 个   # AI Infra / Database / Payments / Email / Analytics / Hosting / DevOps
```

## 运行

```bash
python agent.py
```

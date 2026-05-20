# s01: Projects & Milestones

## 本章内容

- `projects` / `milestones` 内存 CRUD
- 确定性 LLM 模拟触发工具调用

## 核心数据结构

```python
_projects = []      # {"id": "proj_0001", "name": "...", "phase": "..."}
_milestones = []    # {"id": "ms_0001", "project_id": "proj_0001", "title": "...", "status": "open"}
```

## 工具一览

| 工具 | 作用 |
|------|------|
| `register_project` | 创建项目 |
| `list_projects` | 列出所有项目 |
| `get_project` | 查看项目详情（含里程碑） |
| `update_project` | 更新项目 |
| `delete_project` | 删除项目（含关联里程碑） |
| `create_milestone` | 创建里程碑 |
| `list_milestones` | 列出所有里程碑 |
| `close_milestone` | 关闭里程碑 |

## Motto

> **项目是所有管理的起点**

没有项目，里程碑/任务/时间线都是散的。

## 运行

```bash
python agent.py
```

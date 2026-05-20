# s02: Tasks & Status

## 本章内容

- `tasks` 表：项目 → 里程碑 → 任务 三层结构
- SQLite 持久化：重启不丢数据
- `status` 状态机流转

## 数据模型

```sql
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    project_id TEXT, milestone_id TEXT,
    title TEXT, status TEXT DEFAULT 'todo', priority TEXT DEFAULT 'medium'
);
```

## 状态机

```
todo → in_progress → in_review → done
                          ↓
                    cancelled / blocked
```

## Motto

> **没有任务的里程碑是空的**

里程碑只是目标，任务才是行动。

## 运行

```bash
python agent.py
```

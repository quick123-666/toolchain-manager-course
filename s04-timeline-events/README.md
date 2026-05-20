# s04: Timeline Events

## 本章内容

- `timeline_events` 表：全局操作审计日志
- 6种事件类型自动记录：project_created / milestone_created / milestone_completed / task_created / task_done / health_warning
- 按项目查询时间线

## 数据模型

```sql
CREATE TABLE timeline_events (
    id, project_id, milestone_id, task_id,
    event_type,  -- BUSINESS / TECHNICAL / DECISION
    category,    -- 具体事件类型
    title, description,
    source,      -- pm_system
    priority,    -- P0~P3
    created_at
);
```

## Motto

> **做过的每件事都有迹可查**

没有时间线的项目管理系统是健忘的。

## 运行

```bash
python agent.py
```

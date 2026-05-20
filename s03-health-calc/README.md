# s03: Health Calculation

## 本章内容

- 健康度三维计算：任务完成率(40%) + 里程碑达成率(40%) - 阻塞惩罚(20%)
- `health_score()` 函数，返回 0-100 分

## 健康度公式

```
score = task_done/total * 40 + ms_closed/total * 40 - blocked * 10
```

## 评分等级

| 分值 | 状态 |
|------|------|
| 70-100 | 🟢 健康 |
| 40-69 | 🟡 预警 |
| 0-39 | 🔴 危急 |

## Motto

> **数字告诉你哪里要救火**

不要靠感觉，健康度是客观指标。

## 运行

```bash
python agent.py
```

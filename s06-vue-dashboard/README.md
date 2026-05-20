# s06: Vue Dashboard

## 本章内容

- 单文件 HTML Dashboard（Vue 风格，无需构建）
- 连接 s05 FastAPI，实时展示 Projects / Health / Timeline
- API Key 认证通过 Header 传递

## 截图预览

```
┌─────────────┬─────────────┬─────────────┐
│  Projects   │   Health    │  Timeline   │
│             │             │             │
│ agent-harn… │   71.4      │ 🟡 P1 …   │
│ bounded-mem…│ ████░░░░░  │ 🔴 P1 …   │
└─────────────┴─────────────┴─────────────┘
```

## Motto

> **没有界面的系统不好用**

CLI 能跑不代表用户会用，Dashboard 才是交付标准。

## 运行

```bash
# 1. 启动 s05 API
cd s05-fastapi-auth
pip install fastapi uvicorn
python api.py

# 2. 双击 index.html 在浏览器打开
```

## API 依赖

| 数据 | 路由 |
|------|------|
| 项目列表 | `GET /projects` |
| 健康度 | `GET /health/{pid}` |
| 时间线 | `GET /timeline/{pid}` |

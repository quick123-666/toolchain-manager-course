# s05: FastAPI + Auth

## 本章内容

- FastAPI 服务，端口 **18901**
- API Key 认证（admin / viewer 两种角色）
- CRUD 路由：/projects, /milestones, /tasks, /timeline, /health
- Swagger 文档：`http://localhost:18901/docs`

## 认证方式

```
Header: X-Api-Key: <key>
```

| Key | 角色 | 权限 |
|-----|------|------|
| `pfb_admin_...` | admin | 增删改 |
| `pfb_viewer_...` | viewer | 只读 |

## API 路由

| 方法 | 路由 | 说明 |
|------|------|------|
| GET | `/projects` | 列表 |
| POST | `/projects` | 创建 |
| GET | `/projects/{pid}` | 详情 |
| POST | `/milestones` | 创建里程碑 |
| GET | `/timeline/{pid}` | 时间线 |
| GET | `/health/{pid}` | 健康度 |

## Motto

> **服务可复用，前端解耦**

后端不关心谁在调用，前端不关心数据存在哪。

## 运行

```bash
pip install fastapi uvicorn
python api.py
```

访问 http://localhost:18901/docs 打开 Swagger UI。

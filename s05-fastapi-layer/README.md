# s05: FastAPI 层

> 本章新增：REST API + CORS + Swagger 自动文档，Agent 循环 → HTTP API 解耦

## 新增概念

- **FastAPI** — 现代化 Python Web 框架，自动生成 Swagger UI
- **解耦** — Agent 循环在前端，`api.py` 只负责 HTTP API 响应
- **Pydantic Models** — 请求/响应数据校验
- **CORS** — 允许跨域，前端可以单独部署
- **API 即工具** — 每个 `TOOL_HANDLERS` 函数 → 一个 HTTP Endpoint

## 新增依赖

```bash
pip install fastapi uvicorn
```

## API 端点一览

### Dashboard
| Method | Path | 作用 |
|--------|------|------|
| GET | `/api/dashboard` | 统计总览 |

### Categories
| Method | Path | 作用 |
|--------|------|------|
| GET | `/api/categories` | 列出所有分类 |

### Tools
| Method | Path | 作用 |
|--------|------|------|
| GET | `/api/tools` | 列出工具（?category_id=&status=&q=） |
| GET | `/api/tools/{tid}` | 获取详情（含 keys/costs/projects） |
| POST | `/api/tools` | 创建工具 |
| PUT | `/api/tools/{tid}` | 更新工具 |
| DELETE | `/api/tools/{tid}` | 删除工具 |

### API Keys
| Method | Path | 作用 |
|--------|------|------|
| GET | `/api/keys/{tool_id}` | 列出密钥 |
| POST | `/api/keys` | 添加密钥 |
| GET | `/api/keys/decrypt/{kid}` | 解密密钥 |
| DELETE | `/api/keys/{kid}` | 删除密钥 |

### Costs
| Method | Path | 作用 |
|--------|------|------|
| GET | `/api/costs` | 列出费用（?month=&tool_id=） |
| POST | `/api/costs` | 记录费用 |
| DELETE | `/api/costs/{cid}` | 删除记录 |

### Projects
| Method | Path | 作用 |
|--------|------|------|
| GET | `/api/projects` | 列出所有项目 |
| POST | `/api/projects/lifecycle` | GraphSpec 一键注册/更新项目 |
| GET | `/api/projects/lifecycle/{name}` | 获取项目档案（含关联工具和变更历史） |
| PATCH | `/api/projects/lifecycle/{name}` | 更新项目字段（自动记录历史） |
| POST | `/api/projects/lifecycle/{name}/rename` | 项目改名 |
| GET | `/api/projects/lifecycle/{name}/history` | 查变更历史 |
| POST | `/api/tools/{tid}/link-project/{pid}` | 工具关联项目 |
| DELETE | `/api/tools/{tid}/unlink-project/{pid}` | 解除关联 |

### Health
| Method | Path | 作用 |
|--------|------|------|
| GET | `/api/health` | 健康检查 |

## 架构

```
┌─────────────────┐     HTTP      ┌─────────────────┐
│  Vue Frontend   │◀─────────────▶│   FastAPI       │
│  (s06 index.html)│              │   (s05 api.py)  │
└─────────────────┘              └────────┬────────┘
                                          │
                                   ┌──────▼──────┐
                                   │  SQLite DB  │
                                   │  (s04 层)   │
                                   └─────────────┘
```

## 运行

```bash
# 安装依赖
pip install fastapi uvicorn

# 启动 API（会自动 init_db）
python api.py
```

访问：
- API: http://localhost:18902
- Swagger: http://localhost:18902/docs
- 前端: http://localhost:18902/（需先运行 s06 生成 index.html）

## 与 s04 的 diff

```
+ FastAPI web 框架
+ Pydantic 数据模型
+ RESTful 端点（GET/POST/PUT/DELETE/PATCH）
+ CORS 中间件
+ /docs Swagger 自动文档
+ / 前端入口（读取 s06 的 index.html）
```

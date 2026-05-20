# s03: 工具分发表

> 本章新增：引入 `api_keys` / `costs` 表，工具从「单表」扩展为「多表关联」

## 新增概念

- **多表关联** — tools ↔ categories（多对一）、tools ↔ api_keys / costs（一对多）
- **API Key 存储** — base64 混淆存储，真实环境应用更安全的加密（AES 等）
- **月度费用追踪** — `costs` 表按 `month` 字段聚合
- **Dashboard** — 聚合统计：`total_tools`, `active_tools`, `monthly_cost`
- **搜索** — `q` 参数支持 name / description / purpose 三字段模糊匹配

## 表结构（本章新增）

| 表名 | 用途 | 关联 |
|------|------|------|
| `api_keys` | 密钥存储（label, key_value, environment, expires_at） | `tool_id` → `tools.id` |
| `costs` | 月度账单（month, amount, currency, notes） | `tool_id` → `tools.id` |

## 新增工具命令

| 命令 | 作用 |
|------|------|
| `dashboard` | 统计总览 |
| `add_api_key tool_id=1 label=prod key_value=sk-xxx` | 添加密钥 |
| `decrypt_key id=1` | 解密密钥 |
| `add_cost tool_id=1 month=2025-05 amount=25.00` | 记录费用 |
| `list_costs tool_id=1` | 查工具费用记录 |

## API Key 安全说明

```python
# 演示用：简单 base64 混淆（不安全！）
def encode_key(raw):
    return base64.b64encode(raw.encode()).decode()

def decode_key(encoded):
    return base64.b64decode(encoded.encode()).decode()
```

> 真实生产环境应使用：环境变量、KMS 服务（如 AWS KMS、GCP Secret Manager）或专门的密钥管理服务（HashiCorp Vault）。

## 与 s02 的 diff

```
+ api_keys 表              # 密钥存储
+ costs 表                 # 费用追踪
+ dashboard 工具           # 聚合统计
+ q 搜索参数               # 三字段模糊匹配
+ 种子数据扩展至 7 个工具   # Pinecone / Upstash / Supabase / Stripe / Resend / PostHog / Vercel
```

## 运行

```bash
python agent.py
```

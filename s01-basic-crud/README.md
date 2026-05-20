# s01: 内存 CRUD

> 本章新增：Agent 循环 + 基本增删改查（纯内存，无持久化）

## 新增概念

- **内存存储** — `tools[]` 列表在进程内存中，进程结束数据丢失
- **工具分发表** — `TOOL_HANDLERS` 字典注册所有可用工具
- **write-back 模式** — 工具执行结果追加到 `messages[]`，供下一轮 LLM 使用
- **确定性模拟** — `call_llm()` 用固定规则解析用户指令，替代真实 LLM API

## 核心代码

```python
# 工具注册（装饰器模式）
TOOL_HANDLERS = {}
def tool(name):
    def decorator(fn):
        TOOL_HANDLERS[name] = fn
        return fn
    return decorator

@tool("list_tools")
def list_tools(args):
    return json.dumps([t for t in tools], ensure_ascii=False, indent=2)

# Agent 主循环
while True:
    user_input = input("> ").strip()
    messages.append({"role": "user", "content": user_input})
    response = call_llm(messages)         # 模拟 LLM 决定调用哪个工具
    if not response.get("tool_use"):      # 无工具调用 → 直接回复
        print(response["content"])
        continue
    result = TOOL_HANDLERS[response["tool_use"]](response["args"])
    print(result)
    messages.append({"role": "tool", "content": result})  # write-back
```

## 可用命令

| 命令格式 | 作用 |
|---------|------|
| `list` / `ls` | 列出所有工具 |
| `add name=xxx url=xxx` | 添加工具 |
| `update id=1 name=xxx` | 更新工具 |
| `delete id=1` | 删除工具 |
| `get id=1` | 获取单个工具 |
| `search q=xxx` | 关键词搜索 |

## 运行

```bash
python agent.py
```

## 与 s02 的 diff

```
+ SQLite 持久化（get_db / init_db）
+ tools 表 / categories 表
+ 数据库事务自动提交
```

> 本章是全书的**最小可运行版本**，后续章节不在此基础上叠加，而是在 `s02–s06` 各自独立演进。

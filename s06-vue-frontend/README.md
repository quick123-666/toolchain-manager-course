# s06: Vue 前端

> 本章新增：单文件 HTML（Vue 3 CDN）+ API 调用，完整的管理界面

## 新增概念

- **Vue 3 Composition API** — `setup()` + `ref` + `onMounted`
- **单文件 HTML** — 无需构建工具，直接浏览器打开
- **Fetch API** — 调用 s05 的 FastAPI 获取数据
- **响应式** — 数据驱动 UI，Tab 切换、搜索防抖、Toast 提示

## 功能页面

| Tab | 功能 |
|-----|------|
| 工具 | 列表 + 搜索 + 分类/状态过滤 + 详情（API Keys / Costs / Projects） |
| 项目 | 列表 + 详情（含关联工具和变更历史） |
| 添加工具 | 表单提交 |
| 注册项目 | GraphSpec Phase 4.5 项目档案注册 |

## 前端架构

```
index.html
├── Dashboard（4 个统计卡片）
├── Tabs（工具 / 项目 / 添加 / 注册）
├── Filter Bar（搜索 + 分类 + 状态过滤）
├── Tool Cards（点击查看详情）
├── Project Cards（点击查看详情 + 变更历史）
└── Toast（操作反馈）
```

## 数据流

```
用户操作
  │
  ▼
Vue setup()
  │
  ▼
fetch('http://localhost:18902/api/xxx')
  │
  ▼
FastAPI (s05 api.py)
  │
  ▼
SQLite (s04 toolchain.db)
```

## 首次运行

```bash
# 1. 生成 index.html（一次性）
python agent.py

# 2. 启动 s05 API
cd ../s05-fastapi-layer
pip install fastapi uvicorn
python api.py

# 3. 浏览器访问
# http://localhost:18902/
```

或者直接 `cd s05-fastapi-layer && python api.py`，FastAPI 会在 `/` 路由读取 s06 的 `index.html`。

## 与 s05 的 diff

```
+ Vue 3 前端（单文件 HTML）
+ 响应式 Tab 切换
+ 工具详情（API Keys / Costs / Projects）
+ 项目详情（含变更历史）
+ 添加工具表单
+ GraphSpec 项目注册表单
+ Toast 通知
+ 搜索防抖（debounce）
```

## 依赖（仅运行时）

- Vue 3 CDN：`https://unpkg.com/vue@3/dist/vue.global.prod.js`
- 无其他外部依赖

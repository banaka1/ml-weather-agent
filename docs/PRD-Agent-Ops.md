# 智能运维 Agent 平台 · 需求文档（PRD v1.1）

## 0. 文档信息
| 项 | 内容 |
|---|---|
| 文档名称 | 智能运维 Agent 平台 PRD |
| 版本 | v1.2 |
| 当前阶段 | 需求定义 |
| 关联代码 | `controller.py` / `agent.py` / `frontend/`（Vue SPA） |
| 依赖基线 | FastAPI + LangChain + 硅基流动 + 高德天气 + MySQL 5.7 + Vue 3 |
| v1.2 变更 | 前端由原生 HTML/CSS/JS 升级为 Vue 3 + Vite + Pinia + Vue Router + Element Plus + Axios + TypeScript |

---

## 1. 项目背景

在现有基线（豆包风格聊天前端 + FastAPI + LangChain 单工具调用天气）之上，扩展为可观测、可扩展、可审计的智能运维 Agent Demo，重点落地：
1. MySQL 持久化对话记录；
2. 用户登录系统（注册/登录/JWT）；
3. 历史会话保留与新建会话；
4. 意图识别 + 多工具编排 + 反幻觉；
5. NL2SQL 与故障诊断运维场景 Demo；
6. 前端升级为 **Vue 3 + Vite + Element Plus** 单页应用，提升可维护性与交互体验。

---

## 2. 目标与范围

### 2.1 目标
1. **登录与鉴权**：注册 / 登录 / JWT，接口级鉴权；
2. **会话管理**：新建 / 列表 / 切换 / 重命名 / 删除；
3. **消息持久化**：每轮对话落 MySQL，按会话 ID 检索；
4. **多轮上下文**：从 MySQL 拉取历史注入 Prompt；
5. **意图识别 + 多工具编排**；
6. **反幻觉**：Prompt 约束 + 输出校验；
7. **NL2SQL + 故障诊断 Demo**。

### 2.2 范围
| 类型 | 内容 |
|---|---|
| In Scope | 用户注册/登录、JWT、会话 CRUD、消息落库、意图识别、工具注册、NL2SQL、故障诊断、Vue 3 前端（登录页/聊天页/会话列表） |
| Out of Scope | OAuth/SSO、RBAC 多角色、模型微调、生产级高可用、监控告警平台对接、SSR/SSG |

---

## 3. 用户角色
| 角色 | 描述 | 权限 |
|---|---|---|
| 访客 | 未登录 | 仅可访问登录、注册页 |
| 注册用户 | 完成登录 | 拥有独立会话空间，仅能查看本人会话 |
| 运维工程师 | 注册用户子集（Demo 阶段不区分） | 可用 NL2SQL、故障诊断工具 |

---

## 4. 功能需求

### FR-1 用户登录系统（新增） P0
- FR-1.1 注册：`username` + `password`（bcrypt 加盐哈希），用户名唯一；
- FR-1.2 登录：校验密码 → 签发 JWT（HS256，默认 7 天），返回 `{token, user}`；
- FR-1.3 鉴权中间件：除登录注册及静态页外，所有 `/api/*` 必须带 `Authorization: Bearer <token>`；
- FR-1.4 登出：前端清 token；
- FR-1.5 前端新增登录页，未登录访问自动跳转。

### FR-2 会话管理（新增） P0
- FR-2.1 新建会话：`POST /api/sessions` → 返回 `session_id`，默认标题取首条消息前 12 字；
- FR-2.2 会话列表：`GET /api/sessions` → 当前用户全部会话（id、title、updated_at），按时间倒序；
- FR-2.3 切换会话：前端点击列表项 → `GET /api/sessions/{id}/messages` 拉历史 → 渲染；
- FR-2.4 重命名：`PATCH /api/sessions/{id}` `{title}`；
- FR-2.5 删除：`DELETE /api/sessions/{id}`（软删除 `is_deleted=1`）；
- FR-2.6 鉴权：会话归属校验，越权访问返回 403。

### FR-3 消息持久化（新增） P0
- FR-3.1 每轮对话写入 `messages` 表：`session_id / role / content / tool_calls / created_at`；
- FR-3.2 Agent 执行前从 MySQL 拉取该 session 最近 N 条（默认 20）注入 `chat_history`；
- FR-3.3 工具调用日志写入 `tool_call_logs`：`session_id / tool_name / args / result / latency_ms / created_at`；
- FR-3.4 支持分页拉取历史：`?page=1&size=20`。

### FR-4 意图识别 P0
- FR-4.1 `IntentClassifier` 输出 `{chat, weather, nl2sql, diagnose, unknown}`；
- FR-4.2 置信度 < 0.6 回退 `chat`；
- FR-4.3 意图结果随响应返回前端。

### FR-5 Function-Calling 工具编排 P0
- FR-5.1 `ToolRegistry` 单例，`register/all_tools`；
- FR-5.2 `bind_tools(registry.all_tools())` 一次性绑定；
- FR-5.3 支持多工具并行触发，循环上限 3 次；
- FR-5.4 每次调用写 `tool_call_logs`。

### FR-6 Prompt 约束 + 输出校验（反幻觉） P0
- FR-6.1 System Prompt：工具类必调工具、失败如实说明、数值带来源；
- FR-6.2 工具结果 Pydantic 结构校验；
- FR-6.3 最终回答规则校验（数值来源回溯），不通过则重试 1 次。

### FR-7 .env 密钥管理 P1
- 新增 `MYSQL_DSN`、`JWT_SECRET` 变量；
- 启动校验必需变量，缺失 fail-fast。

### FR-8 NL2SQL Demo P0
- `nl2sql_query(question)` → LLM 生成 SQL → sqlparse 语法校验 → 黑名单拦截 → 仅 SELECT + 强制 LIMIT ≤ 100 → 执行 → 自然语言回显。

### FR-9 故障诊断 Demo P1
- `diagnose_fault(symptom)` → 知识库检索 → 分步骤清单 → 多轮追问。

### FR-10 前端扩展（Vue 技术栈） P0
- **FR-10.1** 前端工程化：Vue 3 + Vite 构建，TypeScript 类型检查，ESLint + Prettier 代码规范；
- **FR-10.2** 路由：Vue Router 管理 `/login`、`/register`、`/chat` 等页面，未登录自动跳转登录页；
- **FR-10.3** 状态管理：Pinia 维护用户信息、当前会话、会话列表、消息列表；
- **FR-10.4** UI 组件库：Element Plus（表单、对话框、消息提示、下拉菜单等），自定义聊天组件（气泡、输入框、会话列表）；
- **FR-10.5** HTTP 层：Axios 实例统一封装，请求拦截器自动注入 `Authorization: Bearer <token>`，响应拦截器处理 401 跳登录、500 提示；
- **FR-10.6** 左侧栏："新对话"按钮 + 会话列表（标题 + 时间，点击切换，支持右键重命名/删除）；
- **FR-10.7** 顶部栏：标题 + 用户名 + 登出按钮；
- **FR-10.8** 消息区：欢迎页 + 对话气泡（用户右、AI 左）+ 打字动画 + 工具调用日志折叠面板；
- **FR-10.9** 输入区：多行文本框 + 发送按钮，Enter 发送、Shift+Enter 换行，发送中禁用；
- **FR-10.10** Token 持久化：存 `localStorage`，刷新页面不丢失登录态。

---

## 5. 数据库设计（MySQL 5.7）

详见 `sql/init.sql`，核心四张表：`users`、`sessions`、`messages`、`tool_call_logs`。

### 5.1 users 用户表
- id BIGINT AUTO_INCREMENT 主键
- username VARCHAR(64) 唯一
- password VARCHAR(128) bcrypt 哈希
- created_at DATETIME

### 5.2 sessions 会话表
- id CHAR(36) UUID 主键
- user_id BIGINT 外键 → users.id
- title VARCHAR(128) 默认"新对话"
- is_deleted TINYINT(1) 默认 0 软删除
- created_at / updated_at DATETIME
- 索引 idx_user_updated (user_id, updated_at)

### 5.3 messages 消息表
- id BIGINT AUTO_INCREMENT 主键
- session_id CHAR(36) 外键 → sessions.id
- role ENUM('human','ai','tool','system')
- content TEXT
- tool_calls JSON 模型工具调用决策
- created_at DATETIME
- 索引 idx_session_time (session_id, created_at)

### 5.4 tool_call_logs 工具调用日志
- id BIGINT AUTO_INCREMENT 主键
- session_id CHAR(36) 外键 → sessions.id
- tool_name VARCHAR(64)
- args JSON
- result TEXT
- latency_ms INT
- created_at DATETIME
- 索引 idx_session (session_id, created_at)

---

## 6. 技术栈

| 层级 | 技术 | 用途 |
|---|---|---|
| Web 框架 | FastAPI | 异步路由 + 依赖注入鉴权 |
| ORM | SQLAlchemy 2.x + PyMySQL | MySQL 操作 |
| 鉴权 | python-jose (JWT) + passlib[bcrypt] | token + 密码哈希 |
| 校验 | Pydantic v2 | 请求体、工具结果 schema |
| LLM 编排 | LangChain | ChatPromptTemplate、MessagesPlaceholder、@tool、ToolMessage |
| LLM 接入 | langchain_openai → 硅基流动 | OpenAI 兼容接口 |
| 外部工具 | 高德天气 API + 内置 SQLite（NL2SQL 示例库） | 实时天气 + 运维数据查询 |
| SQL 安全 | sqlparse | NL2SQL 语法解析 + 黑名单拦截 |
| 配置 | python-dotenv | 加载 .env |
| 前端框架 | Vue 3 + Vite | 单页应用构建 |
| 前端语言 | TypeScript | 类型安全 |
| 前端路由 | Vue Router 4 | 页面路由 + 登录守卫 |
| 状态管理 | Pinia | 用户/会话/消息状态 |
| UI 组件库 | Element Plus | 表单、对话框、消息提示等 |
| HTTP 客户端 | Axios | 请求封装 + 拦截器 |
| 代码规范 | ESLint + Prettier | 代码检查与格式化 |
| 数据库 | MySQL 5.7.26 | 用户/会话/消息/日志持久化 |

后端新增依赖：
```bash
pip install sqlalchemy pymysql python-jose[cryptography] "passlib[bcrypt]" sqlparse
```

前端依赖（`frontend/package.json`）：
```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.3.0",
    "pinia": "^2.1.7",
    "element-plus": "^2.7.0",
    "axios": "^1.7.0",
    "@element-plus/icons-vue": "^2.3.1"
  },
  "devDependencies": {
    "vite": "^5.2.0",
    "@vitejs/plugin-vue": "^5.0.0",
    "typescript": "^5.4.0",
    "vue-tsc": "^2.0.0",
    "eslint": "^8.57.0",
    "prettier": "^3.2.0",
    "sass": "^1.75.0"
  }
}
```

---

## 7. 系统架构

```
浏览器 (Vue 3 SPA: frontend/)
  ├─ Vue Router：/login /register /chat
  ├─ Pinia：userStore / sessionStore / chatStore
  ├─ Axios 拦截器：注入 JWT / 401 跳登录
  └─ Element Plus + 自定义聊天组件
  │  Authorization: Bearer <jwt>
  ▼
FastAPI (controller.py)
  ├─ AuthMiddleware（JWT 校验 → req.user）
  ├─ POST /api/auth/register|login
  ├─ POST /api/sessions  新建
  ├─ GET  /api/sessions  列表
  ├─ GET  /api/sessions/{id}/messages 历史
  ├─ PATCH/DELETE /api/sessions/{id}
  └─ POST /api/chat {session_id, message}
        ▼
Agent Orchestrator (agent.py 扩展)
  ├─ SessionStore (MySQL) 读历史→chat_history
  ├─ IntentClassifier
  ├─ PromptBuilder (system + history + input)
  ├─ LLM① bind_tools(registry.all_tools())
  │     ├─ get_weather    (高德 API)
  │     ├─ nl2sql_query   (SQLite+sqlparse)
  │     └─ diagnose_fault (知识库)
  ├─ ToolExecutor (并发 + 写 tool_call_logs)
  ├─ OutputValidator (反幻觉)
  └─ MessageStore (写 messages 表)
        ▼
   MySQL 5.7.26
   users / sessions / messages / tool_call_logs
```

---

## 7.1 前端工程结构（Vue 3）

前端项目位于 `frontend/` 目录，与后端解耦，通过 Axios 调用 FastAPI 接口。

```
frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── api/                    # 接口层（按业务模块分文件）
│   │   ├── request.ts          # Axios 实例 + 拦截器
│   │   ├── auth.ts             # 注册/登录/登出
│   │   ├── session.ts          # 会话 CRUD
│   │   └── chat.ts             # 对话、历史消息、工具日志
│   ├── assets/                 # 静态资源
│   │   └── styles/
│   │       └── variables.scss  # 主题色变量
│   ├── components/             # 通用组件
│   │   ├── ChatBubble.vue      # 消息气泡
│   │   ├── ChatInput.vue       # 输入框
│   │   ├── SessionList.vue     # 会话列表
│   │   └── ToolLogPanel.vue    # 工具调用日志折叠面板
│   ├── layouts/                # 布局
│   │   └── ChatLayout.vue      # 聊天页整体布局（侧边栏+主区）
│   ├── router/                 # 路由
│   │   └── index.ts            # 路由表 + 登录守卫
│   ├── stores/                 # Pinia 状态
│   │   ├── user.ts             # 用户信息 + token
│   │   ├── session.ts          # 会话列表 + 当前会话
│   │   └── chat.ts             # 消息列表 + 发送状态
│   ├── types/                  # TypeScript 类型
│   │   ├── api.ts              # 接口响应类型
│   │   └── models.ts           # 用户/会话/消息实体类型
│   ├── views/                  # 页面
│   │   ├── LoginView.vue       # 登录页
│   │   ├── RegisterView.vue    # 注册页
│   │   └── ChatView.vue        # 聊天主页
│   ├── App.vue
│   └── main.ts                 # 入口：挂载 Pinia/Router/ElementPlus
├── index.html
├── vite.config.ts              # Vite 配置（含后端代理）
├── tsconfig.json
├── eslint.config.js
├── .prettierrc
└── package.json
```

### 7.1.1 关键设计约束

| 约束点 | 说明 |
|---|---|
| **Axios 统一封装** | `api/request.ts` 导出实例，请求拦截器从 `localStorage` 取 token 注入 header；响应拦截器对 401 清 token 并跳 `/login`，对业务错误用 `ElMessage` 提示 |
| **Pinia 按模块拆分** | `user` / `session` / `chat` 三个 store，职责单一；刷新页面时从 localStorage 恢复 user/token |
| **路由守卫** | 全局前置守卫检查 token，未登录且目标非白名单（`/login`、`/register`）则重定向到 `/login` |
| **Element Plus 注册** | 全局注册 Element Plus + 图标库，按需引入样式 |
| **主题变量** | SCSS 变量定义品牌色（`--brand-primary` 等），与后端豆包风格保持一致 |
| **Vite 代理** | 开发环境将 `/api` 代理到 `http://127.0.0.1:8000`，解决跨域 |

### 7.1.2 Vite 代理配置示例

```ts
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
})
```

---

## 8. 接口设计

### 8.1 鉴权
```
POST /api/auth/register   {username, password}  → {user_id, username}
POST /api/auth/login      {username, password}  → {token, user}
GET  /api/auth/me         [Bearer]              → {user_id, username}
```

### 8.2 会话
```
POST   /api/sessions                  [Bearer]                → {session_id, title}
GET    /api/sessions                  [Bearer]                → [{id, title, updated_at}]
GET    /api/sessions/{id}/messages    [Bearer] ?page&size     → [{role, content, ts}]
PATCH  /api/sessions/{id}             [Bearer] {title}        → {ok}
DELETE /api/sessions/{id}             [Bearer]                → {ok}
```

### 8.3 对话
```
POST /api/chat  [Bearer] {session_id, message}
  → {reply, intent, tools:[{name, args, result, ms}]}
```

### 8.4 调试（可选）
```
GET /api/admin/tool_log?session_id=... [Bearer] → [{tool, args, result, ms}]
```

---

## 9. 安全约束

1. 密码：bcrypt 加盐，不存明文；
2. JWT：HS256，exp 默认 7 天，JWT_SECRET 走 .env；
3. 越权防护：所有会话/消息接口校验 session.user_id == req.user.id；
4. SQL 注入：ORM 参数化 + NL2SQL 黑名单（DROP/DELETE/TRUNCATE/ALTER/GRANT/UPDATE/REPLACE/RENAME）；
5. 密钥：.env 不入仓，.gitignore + .env.example；
6. 日志脱敏：tool_call_logs 不记录密钥。

---

## 10. 验收标准

| 编号 | 验收点 | 通过条件 |
|---|---|---|
| AC-1 | 注册/登录 | 注册→登录→拿到 token；错误密码拒绝 |
| AC-2 | 鉴权 | 无 token 访问 /api/chat → 401 |
| AC-3 | 新建会话 | 点新对话 → 侧边栏新增一条空会话 |
| AC-4 | 历史保留 | 重启服务+重登后，旧会话仍可看到并继续 |
| AC-5 | 切换会话 | 切换后消息区只显示该会话历史 |
| AC-6 | 越权 | 访问他人 session_id → 403 |
| AC-7 | 意图识别 | 问天气→weather；问 CPU→nl2sql；问你好→chat |
| AC-8 | 多工具编排 | 一次对话可触发 ≥2 工具且结果正确 |
| AC-9 | 反幻觉 | 工具失败不编造数值；数值可回溯 |
| AC-10 | NL2SQL 安全校验 | DROP/DELETE 被拦截；缺 LIMIT 自动补 |
| AC-11 | 故障诊断 | 输入 CPU 飙高 → 分步骤清单 + 多轮追问 |
| AC-12 | 密钥安全 | grep -r API_KEY *.py 无明文 |
| AC-13 | 前端工程化 | `npm run build` 无 TS 报错；`npm run lint` 无 ESLint 错误 |
| AC-14 | 登录守卫 | 未登录访问 `/chat` → 自动跳转 `/login` |
| AC-15 | Token 注入 | 已登录请求 `/api/chat` → Network 面板可见 `Authorization: Bearer` 头 |
| AC-16 | 会话切换 | 点击侧边栏不同会话 → 消息区渲染对应历史，URL 随 session 变化 |

---

## 11. 里程碑

| M | 内容 | 产出 |
|---|---|---|
| M1 | MySQL + 用户系统 | 建表 + 注册/登录/JWT + 鉴权中间件 |
| M2 | 会话 + 消息持久化 | 会话 CRUD + 历史拉取 + Agent 注入 |
| M3 | **Vue 前端工程搭建** | Vite + Vue3 + TS + Pinia + Router + Element Plus + Axios 封装 + 登录/注册页 |
| M4 | 前端聊天主界面 | 侧边栏会话列表 + 消息气泡 + 输入框 + 发送流程联调 |
| M5 | 意图识别 + 工具注册中心 | IntentClassifier / ToolRegistry |
| M6 | NL2SQL + 安全校验 | nl2sql_query + sqlparse + 黑名单 |
| M7 | 反幻觉校验 | OutputValidator + 重试 |
| M8 | 故障诊断 Demo | diagnose_fault + 知识库 |

---

## 12. 风险与对策

| 风险 | 等级 | 对策 |
|---|---|---|
| JWT 泄露 | 高 | HTTPS + 短 exp + 前端存 localStorage 谨慎 |
| 越权访问 | 高 | 每个会话接口校验 user_id 归属 |
| 会话历史膨胀 | 中 | 滑动窗口 20 条 + 摘要压缩 |
| LLM 生成非法 SQL | 高 | sqlparse + 白名单 + 黑名单三重拦截 |
| 工具调用死循环 | 中 | 循环上限 3 次 |
| 模型幻觉 | 高 | 输出校验 + 来源回溯 + 重试 |
| 密钥泄露 | 高 | .env + .gitignore + 启动校验 |
| 前端跨域 | 低 | Vite dev 代理 `/api` → 后端 8000 |
| 前端状态丢失 | 中 | Pinia 持久化 + localStorage 恢复 token |

---

## 13. .env.example

```ini
# LLM
SILICONFLOW_API_KEY=sk-xxx
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
SILICONFLOW_MODEL_NAME=deepseek-ai/DeepSeek-V4-Pro

# 高德天气
AMAP_API_KEY=xxx
AMAP_WEATHER_URL=https://restapi.amap.com/v3/weather/weatherInfo

# MySQL
MYSQL_DSN=mysql+pymysql://user:pass@127.0.0.1:3306/agent_ops?charset=utf8mb4

# JWT
JWT_SECRET=change-me-please
JWT_EXP_DAYS=7
```

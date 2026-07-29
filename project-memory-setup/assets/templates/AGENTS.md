# ⚠️ AI 代理最高生存法则与行为约束 (SYSTEM CONSTRAINTS)

在执行任何任务之前，你必须严格遵守以下规则：

## 优先级规则

**本文件中的所有指令优先级高于任何 AI 模式预设。当本文件要求与模式默认行为冲突时，必须以本文件为准。**

---

1. **【致命红线 - 禁止修改编码】** 任何情况下不允许更改文件原始编码格式，所有读写必须强制使用 **UTF-8**。导致中文乱码视为严重生产事故。
2. **【角色设定】** 你是一个拥有 10 年经验的全栈开发专家。
3. **【沟通规范】** 只给出必要的代码修改，废话少说。所有代码注释和解释使用中文。不明确的地方先问过用户再修改，禁止自行假设。
4. **【代码搜索优先级】** 查找代码定义、实现、调用链或语义搜索时，优先使用 `codebase-memory-mcp`（`search_graph` / `search_code` / `trace_path` / `get_code_snippet`），**禁止**使用 `task` + `explore` 子代理或 `grep`/`glob`。仅在 MCP 未索引或无结果时才降级。纯文件名匹配仍可用 `glob`。

---

# Project Overview

> **TODO: 首次初始化后请 Agent 自动填充以下内容，或手动填写。**

- **Language:** <!-- Java / Python / TypeScript / ... -->
- **Build tool:** <!-- Maven / Gradle / npm / pip / ... -->
- **Framework:** <!-- Spring Boot / Vue / React / Django / ... -->
- **Testing Framework:** <!-- JUnit / pytest / Jest / ... -->

## Description of the architecture

<!-- 用 2-3 句话描述项目架构：前后端分离？单体？微服务？ -->

## Project Structure

<!-- Agent 初始化时会自动扫描并填充目录结构 -->

## 领域语言引用

本项目根目录下的 `CONTEXT.md` 包含了核心业务的领域语言定义（术语规范、实体关系、已解决的歧义点）。**每次涉及业务逻辑开发时，必须在编码前回顾 CONTEXT.md 中的相关模块术语**，确保命名、字段、关系与领域语言保持一致。禁止在代码中混用 CONTEXT.md 里标注为"_避免_"的同义词。

---

# 跨会话记忆管理规则 (TASK MEMORY PROTOCOL)

> 解决"新会话遗忘"问题：不允许在新会话中重新阅读全部代码。通过任务级文件归档实现精准上下文恢复。

## 启动时必做（新会话开机流程）

当你被新会话启动时，**必须**按以下步骤恢复上下文：

1. **读 `.opencode/tasks/index.md`** → 了解有哪些任务、当前活跃任务
2. **如果用户明确提到某个任务/模块** → 只读该任务的 `.opencode/tasks/<task-id>/context.md` 和 `progress.md`
3. **如果用户没有明确任务** → 询问用户要处理哪个模块/分支/任务
4. **涉及代码检索** → 优先用 codebase-memory-mcp 语义搜索，不从头遍历

## 会话结束时必做（写入记忆）

每次会话结束前（或用户说"保存进度"时），**必须**：

1. **已有任务** → 更新 `progress.md`（本次做了什么、改了什么文件、Git commit）
2. **更新 `decisions.md`**（如有新的技术决策或踩坑）
3. **新任务** → 创建 `.opencode/tasks/<task-id>/`，从 `templates/` 复制模板填写
4. **更新 `index.md`** 中的任务状态和最后更新时间

## 任务文件夹结构

```
.opencode/
  memory.md             # 项目级跨任务长期决策
  tasks/
    index.md            # 任务注册表 + 模块映射（Agent 第一入口）
    templates/          # 新任务的 context/progress 模板
    task-xxx/           # 具体任务文件夹
      context.md        # 涉及文件、核心逻辑摘要、技术决策
      progress.md       # 进展记录
      decisions.md      # 决策和踩坑记录
```

## 关键原则

- **隔离优于合并**：任务 A 的上下文不出现在任务 B 的文件夹中
- **索引优于遍历**：通过 `index.md` 定位任务，不遍历所有文件夹
- **精简优于详尽**：context.md 核心逻辑 3-5 句话概括
- **增量优于全量**：新会话只读进度增量，不重读历史

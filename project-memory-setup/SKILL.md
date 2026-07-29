---
name: project-memory-setup
description: "Initialize AGENTS.md + CONTEXT.md + .opencode/ task memory system for a project. Use when user says '初始化项目记忆', 'setup project memory', '给项目建立记忆', '新项目配置', or when starting work on a project that lacks AGENTS.md/CONTEXT.md. Also use when user wants to enable cross-session AI memory for their project."
---

# Project Memory Setup

初始化项目的 AI 记忆体系：`AGENTS.md`（行为约束 + 记忆管理协议）、`CONTEXT.md`（领域语言）、`.opencode/` 目录（任务归档 + 长期记忆）。

## 工作流

按以下步骤顺序执行，每步完成后向用户确认关键信息再继续。

### 步骤 1：扫描项目结构

执行以下操作了解项目：

1. 读取根目录文件列表（`pom.xml` / `package.json` / `build.gradle` / `Cargo.toml` 等）
2. 识别项目类型、语言、框架、构建工具
3. 扫描一级子目录结构（Maven 模块、前端工程、docs 等）
4. 执行 `git branch -a` 和 `git log --oneline -10` 了解分支和提交历史
5. 检查是否已存在 `AGENTS.md`、`CONTEXT.md`、`.opencode/` 目录

**向用户确认**：总结识别到的项目信息（类型、框架、模块结构、分支情况），确认是否正确。

### 步骤 2：创建 .opencode/opencode.json

从 `assets/templates/opencode.json` 复制到项目 `.opencode/opencode.json`。

这个文件确保 AGENTS.md 和 CONTEXT.md 每次会话都会被 opencode 自动加载。

### 步骤 3：创建 AGENTS.md

从 `assets/templates/AGENTS.md` 复制到项目根目录，然后自动填充：

- **Project Overview 部分**：填入步骤 1 识别的语言、框架、构建工具
- **Description of the architecture**：用 2-3 句话总结架构
- **Project Structure**：列出目录树
- **Backing Services / Tasks 部分**：填入数据库、构建/运行命令

保留所有规则部分不变（编码红线、代码搜索优先级、记忆管理协议）。

### 步骤 4：创建 CONTEXT.md

从 `assets/templates/CONTEXT.md` 复制到项目根目录。

**如果项目有明确的业务领域**（如仓库管理、订单系统等）：
- 引导用户描述一个核心业务模块的领域术语
- 参考 shanxi-jbt 的 CONTEXT.md 作为格式范例（术语→定义→关系→模糊点）
- Agent 填写模板中的占位符

**如果是纯技术项目**（如框架/库/SDK）：
- 描述技术概念、模块关系、设计模式等

**向用户确认**：展示填好的 CONTEXT.md，确认术语和关系准确。

### 步骤 5：创建 .opencode/ 目录结构

从 `assets/templates/` 复制以下文件到项目 `.opencode/`：

```
.opencode/
  opencode.json         # 已在步骤 2 创建
  memory.md             # 从 assets/templates/memory.md 复制并填入架构要+常用命令
  tasks/
    index.md            # 从 assets/templates/tasks/index.md 复制并填入模块→目录映射
    templates/
      context.md        # 从 assets/templates/tasks/templates/context.md 复制
      progress.md       # 从 assets/templates/tasks/templates/progress.md 复制
```

**填充 `memory.md`**：填入步骤 1 识别的架构要点和常用命令。  
**填充 `tasks/index.md`**：根据步骤 1 识别的模块结构填充"模块→任务映射"表。

### 步骤 6：可选 - 索引代码库

询问用户是否对项目执行 codebase-memory-mcp 的 `index_repository` 索引（语义搜索代码图）。如果用户同意，执行 full 模式索引。

### 步骤 7：完成确认

向用户汇报创建的文件清单和关键内容摘要，并说明：
- 新会话启动时 opencode 会自动加载 AGENTS.md 和 CONTEXT.md
- 每次会话结束时对 Agent 说"保存进度"即可更新任务记忆
- 新任务使用前先确认 `.opencode/tasks/index.md` 中是否已有相关条目

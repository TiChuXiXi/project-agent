---
name: project-memory-setup
version: 2.3
description: "Initialize OR upgrade AGENTS.md + CONTEXT.md + LESSONS.md + .opencode/ task memory system for a project. Use when user says '初始化项目记忆', 'setup project memory', '给项目建立记忆', '升级项目记忆', 'update project memory', '新项目配置', or when starting work on a project that lacks AGENTS.md/CONTEXT.md. Also use when user wants to enable cross-session AI memory for their project."
---

# Project Memory Setup

初始化**或升级**项目的 AI 记忆体系，包含**四层能力 + 一个工具层**：

| 层 | 产出文件 | 作用 |
|----|---------|------|
| 文件层 | `LESSONS.md` | 高结构化的项目教训库（错误做法 → 正确做法） |
| 加载层 | `.opencode/opencode.json` | 让 AGENTS.md / CONTEXT.md / LESSONS.md 每次会话自动加载 |
| 行为协议层 | `AGENTS.md` | 写入"LESSONS 教训库强制使用协议"（优先检索 / 自动记录 / 去重 / 月度压缩） |
| 自动化闭环层 | `.opencode/commands/save.md` | `/save` 命令内置"0. 纠错检视"前置过滤器，用户纠正自动归档为教训 |
| 工具层 | codebase-memory-mcp | 代码语义索引（search_graph / trace_path 等），**是否安装由用户决定** |

## 工作模式（自动判定）

| 模式 | 适用场景 | 策略 |
|------|---------|------|
| **模式 A：全新初始化** | 项目没有任何记忆文件 | 按模板全套创建 |
| **模式 B：升级补足** | 项目已使用过本 skill（或部分具备） | 逐项对比**能力清单**，缺失才补足，已有内容绝不覆盖 |

## 能力清单（Capability Checklist）

以下 7 项是 skill 当前版本（v2.2）应具备的完整能力，**升级对比时以此为基准逐项检测**：

| # | 能力 | 存在性检测 | 关键特征检测（判定是否过时） |
|---|------|-----------|------------------------------|
| C1 | 根目录 `AGENTS.md` | 文件存在 | 包含"LESSONS 教训库强制使用协议"章节 |
| C2 | 根目录 `CONTEXT.md` | 文件存在 | 非空模板占位符（无 `<!-- TODO -->` 未填） |
| C3 | 根目录 `LESSONS.md` | 文件存在 | 包含"分类索引"和至少一个分类表格 |
| C4 | `.opencode/opencode.json` | 文件存在 | `instructions` 数组含 `"LESSONS.md"`（仅含 AGENTS.md/CONTEXT.md 视为过时） |
| C5 | `.opencode/commands/save.md` | 文件存在 | 含"0. 纠错检视"或"LESSONS 前置过滤"步骤 |
| C6 | `.opencode/memory.md` | 文件存在 | 非空（含架构要点/常用命令） |
| C7 | `.opencode/tasks/` 结构 | 存在 `index.md` + `templates/` | `index.md` 含"任务索引"表头 |

## 工作流

### 步骤 0：扫描项目 + 能力检测（判定模式，两种模式共用）

#### 0.1 扫描操作（按序执行）

1. 读取根目录文件列表（`pom.xml` / `package.json` / `build.gradle` / `Cargo.toml` 等）
2. 识别项目类型、语言、框架、构建工具
3. **模块/目录结构识别——必须遵循"模块识别三规则"**（防止把废弃模块当活跃模块）：
   - **规则 1（构建文件优先）**：Maven 项目必须以根 `pom.xml` 的 `<modules>` 标签为唯一权威；子目录存在于文件系统**不等于**该模块被启用。判定一个模块是否活跃 = 它出现在 `<modules>` 中且未被注释。
   - **规则 2（注释即废弃）**：在 `<modules>` 或 `<dependencyManagement>` 中被 `<!-- ... -->` 注释掉的模块（如 `zby-car`）、以及 XML 注释块中列出的模块（如 `zby-finance`），一律判定为**废弃/未启用模块**，必须显式排除，禁止写入 AGENTS.md 的 Project Structure。同样规则适用于 Gradle（`settings.gradle` 中被注释的 `include` 行）。
   - **规则 3（分栏输出）**：模块清单必须分两栏向用户展示——「✅ 已启用模块」（来自 `<modules>` 实际启用项）和「⛔ 已排除的废弃模块」（注释/未启用但目录仍在的项），并在确认环节请用户核对排除清单是否准确。
4. 执行 `git branch -a` 和 `git log --oneline -10` 了解分支和提交历史
5. 按上方**能力清单**逐项检测：文件存在性 + 关键特征（如 AGENTS.md 是否已含 LESSONS 协议、opencode.json 的 instructions 是否含 LESSONS.md、save.md 是否含步骤 0）

#### 0.2 能力检测输出模板（强制全量，禁止省略）

检测结果**必须逐行输出全部 7 项能力**（C1-C7），每项标注 ✅ 已具备 / ❌ 缺失 / ⚠️ 过时，**禁止只挑部分能力汇报、禁止跳过 C3（LESSONS.md）和 C5（save.md）**。输出格式：

```
| 能力 | 文件 | 检测结果 | 关键特征 |
|------|------|---------|---------|
| C1 | AGENTS.md | ✅/❌/⚠️ | 含 LESSONS 协议？ |
| C2 | CONTEXT.md | ✅/❌/⚠️ | 无 `<!-- TODO -->` 占位符未填？ |
| C3 | LESSONS.md | ✅/❌/⚠️ | 含分类索引？ |
| C4 | .opencode/opencode.json | ✅/❌/⚠️ | instructions 含 LESSONS.md？ |
| C5 | .opencode/commands/save.md | ✅/❌/⚠️ | 含步骤 0 纠错检视？ |
| C6 | .opencode/memory.md | ✅/❌/⚠️ | 非空？ |
| C7 | .opencode/tasks/ | ✅/❌/⚠️ | index.md 含任务索引表头？ |
```

> 任何一项显示 ❌ 或 ⚠️，都必须在汇报中单独说明其影响（如 C3 缺失 → 教训无法自动归档）并列入待办，禁止静默忽略。

#### 0.3 模式判定

- **全部缺失 → 模式 A（全新初始化）**
- **任一能力已存在 → 模式 B（升级补足）**

**向用户确认**：展示项目信息 + 模块分栏清单 + 检测结果表格（C1-C7 全量），确认走哪个模式。

> 🔴 CHECKPOINT：展示检测结果后**必须等待用户明确选择模式 A 或模式 B**，禁止自行判定后直接开工。

---

## 模式 A：全新初始化

> 执行步骤 0 后，按 A1 → A5 顺序创建五层文件（与顶部"四层能力 + 工具层"表格一一对应）。

### 步骤 A1：创建 .opencode/opencode.json（加载层）

从 `assets/templates/opencode.json` 复制到项目 `.opencode/opencode.json`。

这个文件确保 **AGENTS.md、CONTEXT.md、LESSONS.md** 每次会话都会被 opencode 自动加载。

### 步骤 A2：创建 AGENTS.md（行为协议层）

从 `assets/templates/AGENTS.md` 复制到项目根目录，然后自动填充：

- **Project Overview / Description / Structure / Backing Services**：填入步骤 0 识别的项目信息
- 保留所有规则部分不变（编码红线、代码搜索优先级、记忆管理协议、LESSONS 教训库强制使用协议）

### 步骤 A3：创建 LESSONS.md（文件层）

从 `assets/templates/LESSONS.md` 复制到项目根目录，然后按项目实际技术栈调整：

- **分类增删**：模板含 6 类，按项目语言增删（如纯 Java 项目删 TypeScript 类、可加 Vue 规范类）
- **元规则**：将 `_(初始化日期)_` 替换为当前日期
- **迁移口头教训**：主动询问用户"是否有过去反复提到过的纠错经验？"，格式化为表格填入

**向用户确认**：展示分类结构，确认与技术栈匹配。

> 🔴 CHECKPOINT：展示 LESSONS.md 分类结构，**必须等待用户确认分类与技术栈匹配**后再继续。

### 步骤 A4：创建 CONTEXT.md

从 `assets/templates/CONTEXT.md` 复制到项目根目录，引导用户描述领域语言（术语→定义→关系→模糊点；纯技术项目则描述技术概念/模块关系）。

**向用户确认**：展示填好的 CONTEXT.md。

> 🔴 CHECKPOINT：展示填好的 CONTEXT.md 让用户逐节核对，**禁止跳过此确认直接创建 .opencode/ 结构**。

### 步骤 A5：创建 .opencode/ 目录结构（自动化闭环层）

从 `assets/templates/` 复制以下文件：

```
.opencode/
  opencode.json         # 已在步骤 A1 创建
  commands/
    save.md             # 见下方"save 指令询问规则"
  memory.md             # 从 assets/templates/memory.md 复制并填入架构要点+常用命令
  tasks/
    index.md            # 从 assets/templates/tasks/index.md 复制并填入模块→目录映射
    templates/
      context.md        # 复制
      progress.md       # 复制
```

#### save 指令询问规则（必须询问，禁止擅自创建）

**在创建 `.opencode/commands/save.md` 之前，必须询问用户**：

> 🔴 CHECKPOINT："是否在当前项目创建 `/save` 自定义指令（`.opencode/commands/save.md`）？它会在保存进度时自动把用户纠正归档进 LESSONS.md。"

- 用户同意 → 从 `assets/templates/save.md` 复制
- 用户拒绝 → 跳过，并告知缺失影响（LESSONS 自动写入闭环不完整，可随时手动补）
- **用户已经存在该文件 → 按模式 B 的 C5 对比规则合并，不覆盖**

---

## 模式 B：升级补足（对比补缺，绝不覆盖）

**核心原则：已存在的文件绝不整文件覆盖。** 对能力清单 C1-C7 逐项处理：

### B1. 判定每项的处理动作

| 检测结果 | 动作 |
|---------|------|
| 缺失 | 从模板创建（全新内容） |
| 存在但关键特征缺失（过时） | **原地合并**：保留项目特定内容，仅追加缺失章节/条目 |
| 存在且特征齐全 | 跳过，不改动 |

### B2. 各项合并细则

| 能力 | 过时时的合并动作 |
|------|-----------------|
| C1 AGENTS.md 无 LESSONS 协议 | 在文件末尾追加"# LESSONS 教训库强制使用协议"章节（内容取自 `assets/templates/AGENTS.md` 末尾），**不动原有任何规则** |
| C2 CONTEXT.md 不完整 | 不自动改写领域语言（项目特定内容，AI 不可假设），仅提示用户是否补全 |
| C3 LESSONS.md 缺失 | 从模板创建；已有则跳过 |
| C4 opencode.json 的 instructions 缺 LESSONS.md | **合并数组**：在 `instructions` 数组中追加 `"LESSONS.md"`，**沿用现有条目的路径风格**（现有条目是相对路径则追加相对路径，是绝对路径则追加对应绝对路径），保留用户的其他配置项（commands / mcp / agents 等） |
| C5 save.md 缺步骤 0 | 在文件开头"# Save Progress Command"标题后插入"## 0. 纠错检视（LESSONS 前置过滤）"段落（内容取自 `assets/templates/save.md`），保留原有步骤 |
| C6 memory.md 缺失 | 从模板创建；已有则跳过（不合并历史决策） |
| C7 tasks/ 结构缺失 | 缺失的部分（index.md / templates/）从模板补齐，**已存在的 task-xxx 文件夹一律不动** |

### B3. 升级报告

向用户输出升级报告：

- ✅ 已具备（跳过）：列出
- 🔧 已升级（合并补足）：列出 + 说明追加了什么
- 🆕 已新建：列出
- ⚠️ 未处理（需用户决定）：如 CONTEXT.md 补全、MCP 安装等

---

## 公共步骤：codebase-memory-mcp 工具层（两种模式共用，必须询问）

### P1. 检测是否已安装

1. 检查全局配置 `~/.config/opencode/opencode.json` 和项目 `.opencode/opencode.json` 的 `mcp` 段是否有 `codebase-memory-mcp`
2. 若有，尝试调用 `list_projects` 验证连通；能返回结果即视为已安装可用

### P2. 未安装时询问用户

> 🔴 CHECKPOINT：**必须询问用户**，禁止静默安装或静默跳过。

**必须询问用户**：

> "检测到 codebase-memory-mcp 未安装。是否自动安装？它提供代码语义索引能力（search_graph / trace_path），能显著提升代码检索效率，但不是记忆体系的必需项。"

- **用户同意安装** → 提供两种安装层级，让用户选择：
  - **全局安装**（推荐，所有项目可用）：编辑 `~/.config/opencode/opencode.json` 的 `mcp` 段，追加：
    ```json
    "mcp": {
      "codebase-memory-mcp": {
        "type": "local",
        "command": ["<codebase-memory-mcp 可执行文件绝对路径>"],
        "enabled": true
      }
    }
    ```
  - **项目级安装**（仅当前项目可用）：在 `.opencode/opencode.json` 的 `mcp` 段追加同样配置
  - 若用户机器上没有该 MCP 的可执行文件，询问用户提供路径或从官方渠道获取；**不要自行假设安装位置**
- **用户拒绝安装** → 跳过，告知降级方案：代码检索将退回 grep/glob 等常规手段（见 AGENTS.md 第 4 条降级规则）

### P3. 安装后验证 + 索引询问

1. 安装后调用 `list_projects` 验证连通（失败则提示用户检查路径和 `enabled` 配置，**不阻塞其余记忆文件创建流程**）
2. 验证成功后，**询问用户**是否对当前项目执行 `index_repository` 索引（full 模式语义搜索代码图）；同意才执行

> 🔴 CHECKPOINT：索引属于重型环境操作，**必须等用户明确同意后才执行 `index_repository`**。

---

## 失败模式与兜底（Fallback）

以下任一场景触发时，**先告知用户再按表处理**，禁止静默跳过或静默失败：

| # | 触发条件 | 一线修复 | 仍失败兜底 |
|---|---------|---------|-----------|
| 1 | `assets/templates/` 下找不到某模板文件 | 核对模板文件名拼写（含路径） | 停止该步骤，向用户报告缺失，并依据本 SKILL.md 内的结构说明手写重建模板 |
| 2 | 项目 `.opencode/` 或 `commands/`、`tasks/templates/` 目录不存在 | 先创建目录再复制模板 | 报告创建失败原因（权限/只读），请用户处理 |
| 3 | 项目 `.opencode/opencode.json` 非标准 JSON（含注释/尾逗号） | 尝试去除注释后解析 | 不自动合并；展示两文件差异，让用户手动合并 `instructions` 数组 |
| 4 | `opencode.json` 解析成功但无 `instructions` 键 | 直接追加 `instructions: ["AGENTS.md","CONTEXT.md","LESSONS.md"]`，保留其余字段 | 同上，展示差异请用户手动合并 |
| 5 | `git branch -a` / `git log` 执行失败（非 git 项目） | 跳过 git 信息收集 | 在确认环节标注"非 git 仓库"，继续初始化 |
| 6 | 用户拒绝创建 `/save` 指令（C5） | 跳过并告知闭环不完整 | 在完成汇报中标记 ⚠️ 未创建，提示可随时手动补 |
| 7 | 用户拒绝安装 MCP（P2） | 跳过，告知降级为 grep/glob 检索 | 在完成汇报中标记 ⚠️，提示 AGENTS.md 已含降级规则 |
| 8 | MCP 安装后 `list_projects` 验证失败 | 提示用户检查可执行文件路径和 `enabled` 配置 | 不阻塞记忆体系其余部分，仅标记 MCP 待修 |
| 9 | 目标文件已存在但内容含用户手工改动 | 模式 B 规则原地合并，绝不整文件覆盖 | 若合并可能破坏用户内容，先备份为 `<file>.bak.YYYYMMDD-HHMM` 再合并 |
| 10 | 写入时出现编码问题（乱码风险） | 检查写入工具是否强制 UTF-8 | 停止写入，报告编码问题，修复后重试 |
| 11 | 项目无 `pom.xml` / `package.json` 等构建文件 | 跳过"模块识别三规则"，降级为纯目录扫描，并明确告知用户"未按构建文件校验模块" | 将目录清单完整列出，**询问用户**哪些目录是废弃/未启用模块后再写入 AGENTS.md |

---

## 反例黑名单（禁止事项）

优化/执行本 skill 时，以下行为**一律禁止**：

| # | 禁止行为 | 原因 | 替代做法 |
|---|---------|------|---------|
| 1 | 模式 B 下整文件覆盖已有 AGENTS.md / CONTEXT.md | 项目特定内容（规则、领域语言）会永久丢失 | 只追加缺失章节，原地合并 |
| 2 | 擅自创建 `/save` 指令 | 用户可能不想要自定义命令 | 先按"save 指令询问规则"询问 |
| 3 | 修改任何文件编码格式 | 中文乱码视为生产事故 | 读写强制 UTF-8 |
| 4 | 自行假设并填入 CONTEXT.md 领域语言 | AI 不可替代用户定义领域术语 | 引导用户描述，仅记录用户提供的内容 |
| 5 | 擅自安装 codebase-memory-mcp 或执行索引 | 环境级变更，影响全局 | 先询问用户（见 P2/P3） |
| 6 | 假设 MCP 可执行文件的位置 | 不同机器路径不同 | 询问用户提供路径或官方渠道获取 |
| 7 | 扫描阶段读入全部代码文件 | 浪费上下文，拖慢流程 | 只读根目录清单、构建文件和一级子目录 |
| 8 | 在步骤 0 检测后跳过用户确认直接开工 | 模式选择错误导致大量返工 | 🔴 等待用户明确选择模式 A 或 B |
| 9 | 把目录中存在但构建文件未启用的模块当作活跃模块（如 pom.xml 已注释的 zby-car 目录仍在） | 废弃代码进入 AGENTS.md 结构，误导后续开发与检索 | 以 `<modules>`/`settings.gradle` 实际启用项为准，废弃模块显式排除并分栏展示 |
| 10 | 能力检测结果只汇报部分项（跳过 C3 LESSONS.md / C5 save.md） | 缺失项被静默忽略，教训库/保存闭环建不起来 | 按 0.2 模板全量输出 C1-C7，任何 ❌/⚠️ 必须说明影响并列待办 |

---

## 完成确认

### 模式 A 汇报

创建的文件清单 + 四层闭环说明（新会话自动加载 / 犯错时 /save 自动归档 / 月度压缩）+ 冒烟测试建议（说句错误指令纠正后 `/save`，验证教训入表）。

### 模式 B 汇报

输出升级报告（见 B3），并说明：未覆盖任何既有内容，新增/升级内容下次会话自动生效。

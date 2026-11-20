# project-memory-setup v3

为项目建立一份能随 Git 仓库交接的长期记忆。换一个 Agent，或隔几周再回来，仍然可以查清三件事：当初为什么做、用户批准做到哪一步、哪些结果还有待验证。

## 安装 Skill

如果你的 Agent 支持安装 Skill，可以直接对它说：

> 请从 https://github.com/TiChuXiXi/project-agent 安装 `project-memory-setup` 到我的个人 Skills 目录。v3 的 `SKILL.md` 在仓库根目录。

习惯用终端的话，可以用下面的命令安装到个人范围，再按提示选择 Agent。`npx` 运行 `skills` 安装器；安装器直接从 GitHub 仓库读取 Skill，同名 npm 包或 GitHub Release 都不是前提。[安装器说明](https://github.com/vercel-labs/skills#install-a-skill)

```sh
npx skills add TiChuXiXi/project-agent --skill project-memory-setup -g
```

**本地版本还没推送时**，上面的命令会取到 GitHub 默认分支已有的版本。要安装手头这份 v3，进入含 `SKILL.md` 的本仓库根目录，直接指定当前目录：

```sh
npx skills add . --skill project-memory-setup -g
```

从本地源码安装时，将仓库根目录的 `SKILL.md`、`agents/`、`assets/`、`references/` 和 `scripts/` 一起放进宿主的 `skills/project-memory-setup/` 即可。项目记忆工具运行时需要 Python 3.9 或更高版本。

## 在项目里启用

打开**要维护的业务项目**，对 Agent 说：

> 初始化当前项目的长期记忆。保留已有规则，核对项目背景，把还不清楚的目标标为待确认。

Agent 会预览变更，在授权范围内创建项目记忆，并把后续 Agent 需要的规则写入项目根目录的 `AGENTS.md`。看到根目录的 `CONTEXT.md` 和 `.project-memory/tasks/index.md`，就可以开始记录和交接任务。把这些记忆文件随项目提交到 Git，其他人的工作副本也能读到。

**从 v2 升级**时，改说“把当前项目的记忆升级到 v3，保留历史任务和自定义规则”。迁移工具会将旧的 `.opencode/` 记忆移到 `.project-memory/`。若两个目录同时存在，或旧配置、`/save` 含有自定义内容，Agent 会指出需要核对的文件。处理后可以继续迁移。

## 日常怎么用

| 什么时候 | 可以直接说 | 项目记忆怎么用 |
| --- | --- | --- |
| 讨论方案 | “按旧工单号查询，这点定了。短信提醒再议。” | 分开记录已确认的查询方式和待讨论的提醒。 |
| 限定实施范围 | “这轮只加查询单测。” | 把实施授权记到任务里；测试通过只更新技术验证结果。 |
| 换会话或换 Agent | “继续工单查询，先告诉我上次定了什么、还能做什么。” | 从项目记录找回最新目标、已确认决定和批准范围，再读相关源码。 |
| 查历史依据 | “当时为什么只做本地查询？找到原记录给我看。” | 检索任务或归档，回到 Markdown 原文核对出处。 |

形成共识、明确授权、纠正信息或拿到验证结果时，Agent 按项目规则在当轮保存。无需输入 `/save`，想主动保存时，说“记一下刚才的决定”也可以。简单改错字之类的小修可以直接做。用户明确调整目标时，追加新版本，保留原先确认的表述和变更依据。

## 记忆存在哪里

| 目标项目中的位置 | 内容 |
| --- | --- |
| `AGENTS.md` | 新会话如何恢复任务，何时保存，如何处理冲突 |
| `CONTEXT.md`、`LESSONS.md` | 项目背景、目标、领域术语和可复用的经验 |
| `.project-memory/memory.md` | 跨任务沿用的架构决定、约束与来源 |
| `.project-memory/tasks/` | 任务索引、意图、讨论、授权、进度和验收证据 |

Markdown 原文是权威记录。目标、决策和计划用稳定 ID 关联，任务归档后仍可按 ID 查找。SQLite FTS5 索引用于加快检索，可以从原文重建。代码地图按需登记已核对的源码入口，使用时仍需回到当前源码确认。多个 Agent 同时保存时，项目工具只更新对应区块；同一区块发生冲突会保留双方内容并报告。

具体规则见[记忆语义与验收](references/memory-semantics.md)、[保存与检索](references/operations.md)和[按需代码地图](references/code-map.md)。

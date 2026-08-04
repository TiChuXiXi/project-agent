# project-memory-setup

> opencode 技能 — 为项目初始化 AI 记忆体系（AGENTS.md + CONTEXT.md + LESSONS.md + .opencode/ 任务记忆系统）

## 功能

跨会话保持 AI 对项目的理解一致性，每次新会话无需重复描述项目背景。

- **AGENTS.md** — 行为约束、编码规范、记忆管理协议
- **CONTEXT.md** — 业务领域语言、术语定义与关系
- **LESSONS.md** — 高结构化的项目教训库（错误做法 → 正确做法），配合 `/save` 命令自动归档用户纠正
- **.opencode/** — 自动加载配置、任务归档与长期记忆（tasks、templates、save 指令）

## 工作模式

| 模式 | 适用场景 | 策略 |
|------|---------|------|
| 模式 A：全新初始化 | 项目没有任何记忆文件 | 按模板全套创建 |
| 模式 B：升级补足 | 项目已使用过本 skill（或部分具备） | 逐项对比能力清单，缺失才补足，已有内容绝不覆盖 |

## 使用方式

1. 在 opencode 中加载此 skill
2. 输入触发词：「初始化项目记忆」「升级项目记忆」「setup project memory」等
3. 按工作流引导逐步完成项目记忆配置（每个关键决策点有 🔴 CHECKPOINT 用户确认）

## 目录结构

```
project-memory-setup/
├── SKILL.md                      # skill 工作流定义（v2.2）
├── agents/
│   └── openai.yaml               # agent 配置
└── assets/templates/
    ├── AGENTS.md                  # 行为约束 + LESSONS 强制使用协议模板
    ├── CONTEXT.md                 # 领域语言模板
    ├── LESSONS.md                 # 教训库模板（分类索引 + 元规则）
    ├── memory.md                  # 长期记忆模板
    ├── opencode.json              # opencode 自动加载配置模板
    ├── save.md                    # /save 命令模板（内置"0. 纠错检视"前置过滤）
    └── tasks/
        ├── index.md               # 任务索引模板
        └── templates/
            ├── context.md         # 任务上下文模板
            └── progress.md        # 任务进度模板
```

## 能力清单（C1-C7）

AGENTS.md · CONTEXT.md · LESSONS.md · opencode.json（含 LESSONS.md 自动加载）· save.md · memory.md · tasks/ 结构

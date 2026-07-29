# project-memory-setup

> opencode 技能 — 为项目初始化 AI 记忆体系（AGENTS.md + CONTEXT.md + .opencode/ 任务记忆系统）

## 功能

跨会话保持 AI 对项目的理解一致性，每次新会话无需重复描述项目背景。

- **AGENTS.md** — 行为约束、编码规范、记忆管理协议
- **CONTEXT.md** — 业务领域语言、术语定义与关系
- **.opencode/** — 任务归档与长期记忆（tasks、templates）

## 使用方式

1. 在 opencode 中加载此 skill
2. 输入触发词：「初始化项目记忆」「setup project memory」等
3. 按工作流引导逐步完成项目记忆配置

## 目录结构

```
project-memory-setup/
├── SKILL.md                      # skill 工作流定义
├── agents/
│   └── openai.yaml               # agent 配置
└── assets/templates/
    ├── AGENTS.md                  # 行为约束模板
    ├── CONTEXT.md                 # 领域语言模板
    ├── memory.md                  # 长期记忆模板
    ├── opencode.json              # opencode 配置模板
    └── tasks/
        ├── index.md               # 任务索引模板
        └── templates/
            ├── context.md         # 任务上下文模板
            └── progress.md        # 任务进度模板
```

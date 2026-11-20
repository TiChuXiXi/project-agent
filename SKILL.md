---
name: project-memory-setup
description: 初始化、升级或维护项目的长期 Agent 记忆。适用于跨会话恢复任务、保存设计共识、追溯项目目标或检索项目经验。
---

# 项目长期记忆

初始化或升级前先读 [记忆语义](references/memory-semantics.md)。在目标项目之外定位本 Skill，运行 `python <skill>/scripts/migrate.py PROJECT` 预览，再按授权加 `--apply`。这同时安装可随仓库携带的本地工具和行为规则。冲突按报告处理，重跑验证；不要覆盖自定义规则。以构建配置核对活跃模块，从 README 与用户原话提取项目背景。未知的动机保持待确认。

平时由目标项目 AGENTS.md 引导恢复和静默保存。仅对当前任务读相关条目。通过项目内 tools/memory.py 获取区块版本并保存，索引入口见 [操作说明](references/operations.md)。重要意图、决策和授权遵循记忆语义。简单任务直接做。索引或工具不可用时仍可读 Markdown，写入需具备同等并发保护。

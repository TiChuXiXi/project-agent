# 使用项目记忆
新任务从 tasks/templates/ 选择所需文档结构，在 tasks/<id>/ 下通过 save 写入区块即可创建文件，并在 tasks/index.md 用同一任务 ID 更新入口。续接既有任务/ADR 时先读原文。

在 CONTEXT.md 的 aliases 区块中，每行用“派单 = 分派工作 | 用户确认，需求会原话……”保存已核实的等价词。使用短词查询时会扩展同组别名。决定区块将状态单列一行（例如“状态：active”），注明边界、来源及目标 ID；被替代时标记 superseded 并链接新 ID。检索返回的是候选，状态或依据缺失时回到原文。

例：先执行 `python .project-memory/tools/memory.py read .project-memory/tasks/T7/context.md G-002@v1`；得到 missing 后将确认原话与依据写入 draft.txt，再执行 `python .project-memory/tools/memory.py save .project-memory/tasks/T7/context.md G-002@v1 missing draft.txt`。保存同一事实不会重复写入。编辑已有区块时使用 read 返回的 token。冲突保存在 .project-memory/conflicts/，按当前目标和原始依据合并后重新读取 token 再写。代码地图先用 code_map.py SOURCE 获取 sha、token，核对源码后用相同 SOURCE 和 --sha、--token、--note FILE 登记。

以下工具位于 .project-memory/tools/，从项目根目录运行，Python 3.9+。参数均可加 --help。文档和相对引用可直接阅读。

读取 memory.py read FILE ID，返回 body 和区块 token；区块不存在时 token 为 missing。把新正文放在 UTF-8 临时文件，执行 memory.py save FILE ID TOKEN INPUT。正文只包含该语义区块。读取后的 token 必须随保存传入；失败时查看报告的冲突副本并重新核对。不同区块可合并，重复内容零写入。命名普通区块如 scope、exploration、acceptance；作用域为文件。逻辑 ID 如 D-012、P-003 在项目内唯一。用 memory.py resolve ID 查找，Markdown 链接作为导航。G-001@v1 一类目标区块只可追加，下一版通过 --change-source 提供用户明确调整的依据，正文保留确认原话、新旧约定和影响范围。只允许把用户确认的原文写进 G 版本；候选写 exploration。不要把文件级快照覆盖回去。

工作中用 memory_index.py search 查询（可选 --history）；用 get REF 回查，rebuild 重建缓存。默认记忆文件、代码地图和 README 参与检索。可在 .project-memory/sources.txt 每行列项目相对 Markdown 路径或 path.md#章节标题，添加指定规范。缓存可删除，不入 Git。代码地图用 code_map.py 登记已核对的 entry，程序参数见 --help。普通小修不必登记地图或创建任务。

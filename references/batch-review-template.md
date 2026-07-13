# Batch Review Output Template

This template is for evaluating many reuse-scout test cases. It is separate from the user-facing report template.

## Human Review Table

Use this table when a human wants to judge whether batch outputs are useful:

| ID | 场景 | 结论 | 推荐复用路径 | 关键候选 | 不要重写 | 风险/待验证 | 审查建议 |
|---|---|---|---|---|---|---|---|
| 01 | AI PPT 生成器 | 不要从零做：优先 fork/组合 | fork_existing / compose_modules | candidate A; candidate B | PPTX 导出、模板系统 | 需深读 README/license | 可抽样深读 top 3 候选 |

Column meanings:

- `ID`: test case ID.
- `场景`: user idea title.
- `结论`: plain-language decision for a reviewer.
- `推荐复用路径`: normalized reuse decision label.
- `关键候选`: short list of top candidates; include signal only when useful.
- `不要重写`: modules the builder should avoid rebuilding.
- `风险/待验证`: confidence issues, source failures, license/install checks.
- `审查建议`: what the human reviewer should inspect next.

## Debug Table

Use this table only for script or search-quality debugging:

| ID | 输入想法 | 分类 | 初步建议 | Top reusable candidates | 不要重复实现 | 置信度 | 搜索覆盖 | 观察/待审查 |
|---|---|---|---|---|---|---|---|---|

The debug table may include counters such as kept/noise/failures/cache. Do not use it as the final user-facing output.

## Rules

- Keep the review table short and decision-oriented.
- Put raw counters and implementation details in the debug table.
- If candidate count is low, mark the case for keyword/source expansion.
- If noise count is high, mark the case for candidate relevance review.
- If confidence is low, avoid strong build-vs-reuse conclusions.

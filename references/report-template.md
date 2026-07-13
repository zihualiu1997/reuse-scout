# Reuse Scout Report Template

Default final output must be short, non-technical, and decision-first. Put the user-friendly answer first. Put detailed evidence later under an optional section.

Use Chinese when the user writes Chinese.

Do not expose the full research process unless it matters. Avoid long tables in the user-facing summary. Prefer 1-3 short paragraphs plus a copyable prompt.

```markdown
# 复用检查结果

## 先说结论

{用 1-3 段短话说明结果。不要堆术语。根据实际情况选择下面三种表达之一。}

### 情况 A：已经有人做得很像

我找到了几个和你想法很接近的现成项目/产品，其中最值得先看的是：

- {项目 A}：它已经做了 {相似功能}，和你的想法重合度很高。建议先让 AI 帮你读它的介绍、界面和代码结构，判断能不能直接改。
- {项目 B}：它更适合作为参考/备用，因为 {原因}。

我的建议：先不要从零做。先看 {项目 A} 能不能复用；如果能复用，你只需要改 {你的差异化部分}。

### 情况 B：没有完全一样的，但可以拼出来

我没有在当前搜索范围里看到“几乎一模一样”的成熟项目，但这个想法可以拆成几个常见模块来做：{模块 1}、{模块 2}、{模块 3}。

这些模块已经有现成项目/工具可以用：{项目/库 A} 负责 {用途}，{项目/库 B} 负责 {用途}，{项目/库 C} 负责 {用途}。

我的建议：不要从零写全部功能。用这些现成部分拼一个 MVP，自己只做 {真正有差异的部分}。

### 情况 C：比较新的想法

在当前搜索范围里，我没有找到高度相似的现成项目。这不代表全网一定没有，只能说明这次搜索没有发现强候选。

我的建议：可以做一个很小的 MVP。先实现 {最小核心功能}，暂时不要做 {容易膨胀的功能}。底层仍然可以复用 {通用模块/工具}，避免把时间花在基础设施上。

## 你下一步可以怎么做

1. 先让 AI 打开/阅读：{候选项目或工具列表，最多 3 个}。
2. 判断它们是否能直接改成你的想法。
3. 如果不能，再按“模块组合”的方式做 MVP。

## 可以直接复制给 LLM/Codex 的 Prompt

```text
我想做：{用户想法}

请先不要从零写代码。请先检查下面这些现成项目/工具是否可以复用：
1. {候选 A} - 可能用于 {用途}
2. {候选 B} - 可能用于 {用途}
3. {候选 C} - 可能用于 {用途}

请你先完成三件事：
1. 阅读这些项目的 README、界面截图/演示、license 和安装方式。
2. 判断哪个最适合作为底座，哪些只适合作为模块或参考。
3. 给出一个最小 MVP 实现方案，并明确哪些功能不要重复造轮子。

重要约束：
- 不要从零实现已经成熟的基础功能：{不要重写的模块列表}
- 本轮只做：{最小核心功能}
- 如果候选项目不可用，请先说明原因，再选择替代方案。
```

---

## 详细依据（可跳过）

### 搜索范围

- 搜过：{GitHub / npm / PyPI / Hugging Face / 产品替代站 / 其他}
- 没搜或没搜充分：{未覆盖来源}
- 置信度：高 / 中 / 低

### 候选对比

| 候选 | 它是什么 | 和想法的重合度 | 建议怎么用 | 风险 |
|---|---|---|---|---|
| {候选 A} | {一句话} | 高/中/低 | 直接用/改造/当模块/只参考 | {风险} |

### 不建议重复实现

- {模块 1}：建议用 {候选/工具}，因为 {原因}
- {模块 2}：建议用 {候选/工具}，因为 {原因}

### 未验证事项

- 是否能顺利安装/运行：未验证/已验证
- license 是否适合你的用途：未验证/已验证
- 是否仍在维护：未验证/已验证
```

## Style Rules

- The first visible answer must be understandable by a non-programmer.
- Keep the conclusion under 250 Chinese characters when possible; maximum 500 unless the user asks for detail.
- Do not start with search matrix, candidate tables, raw counts, package names, or debug details.
- Use words like “现成项目”, “可以直接改”, “可以当零件用”, “只适合参考” instead of unexplained technical labels like fork, SDK, boilerplate, registry.
- If using a technical word, add a short explanation: “fork（复制一份现有项目来改）”.
- Put all noisy details in “详细依据（可跳过）”.
- Always include a copyable LLM/Codex prompt before the optional details section.

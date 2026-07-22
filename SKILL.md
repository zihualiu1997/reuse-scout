---
name: reuse-scout
description: Pre-build reuse research for vibecoding project ideas. Use when a user wants to build a new app, tool, automation, agent, plugin, website, or software project and needs to check whether existing open-source projects, packages, templates, SaaS products, or skills can be reused before coding. Produces a build-vs-reuse decision report, search audit, candidate scoring, do-not-rebuild list, MVP route, and Codex handoff prompt.
---

# Reuse Scout

Use this skill before coding a new software idea. Your job is to prevent unnecessary wheel-building by researching reusable projects, packages, templates, products, and skills, then producing a practical build-vs-reuse decision.

Default stance: oppose building from scratch unless research shows it is necessary. Do not implement the project while using this skill unless the user explicitly asks to proceed after the report.

## Workflow

Follow this sequence:

```text
idea -> clarify -> decompose -> LLM seed discovery -> search matrix -> multi-source search -> candidate expansion -> scoring -> decision -> do-not-rebuild list -> MVP route -> Codex handoff prompt
```

Ask at most 3 clarifying questions when the idea is too vague. Prioritize target user, desired product form, and reuse constraints such as open-source, local-first, SaaS allowed, or deployment preference. If the user does not answer, continue with explicit assumptions.

For V1/V2 execution, use `references/v1-checklist.md` to keep the research complete and auditable. When network access is available and the task benefits from structured search, run `scripts/reuse_scout_search.py` with source-specific priority queries and required-source gates to collect initial candidates. Treat script output as evidence to inspect, not as the final answer.

## Required Behavior

### LLM Seed Discovery

Before formal external search, run an LLM-assisted seed discovery pass. Ask the model to propose possible existing projects, product names, community terms, SEO keywords, adjacent category names, competitor names, and exact search queries that might describe the same idea.

Treat this output only as search seed material, not evidence. Every LLM-suggested project, package, product, or repo must be verified through an inspectable source such as GitHub, a package registry, product page, README, docs, or official listing before it appears as a scored candidate or recommendation.

If the LLM seed pass says no similar project is known, do not use that as proof of novelty. Continue external search and report only the verified search scope.

### High-Overlap Candidate First

Before decomposing the idea into modules, actively look for a nearly identical existing project, skill, template, or product. If one is found, make it the center of the report and compare all module/composition routes against it. Do not bury an exact-match candidate inside a long module list.

Use a complexity brake: when a candidate covers the user's end-to-end job at roughly 70%+ overlap, the default recommendation should be `fork_existing`, `direct_use`, or `pause_and_narrow`, not a large custom architecture. Only recommend `compose_modules` or `build_mvp` after explaining why the high-overlap candidate is unsuitable.

When the idea is about creating a skill/agent from source materials such as chat logs, docs, transcripts, interviews, writing samples, or human work records, always search the skill/agent/persona-distilled-project space explicitly before generic chatbot/RAG modules. Include terms such as: `colleague skill`, `digital colleague`, `persona skill`, `work skill`, `chat logs to chatbot`, `conversation distillation`, `AI employee clone`, `customer service skill`, and `skill from source materials`.

If the user mentions or the conversation context contains a known potentially matching candidate, treat it as a seed candidate: inspect/verify it first, search its alternatives, and include it in the final report unless it is clearly irrelevant.

### Search Completion Gate

Define which source is required to discover each target candidate type before searching. GitHub or an equivalent inspectable skill ecosystem is normally required for Codex/Claude skills; npm, Hugging Face, and product documentation do not substitute for that coverage.

Keep a completed `empty` result separate from `rate_limited`, `auth_failed`, `network_failed`, and skipped queries. If a required source is incomplete, the result is inconclusive for that candidate type. Do not write "no existing skill/project was found"; say the specialized search did not complete, assign low confidence, and choose `pause_and_narrow` or supplementary search.

Run exact-match, known-seed, and target-type queries before broad module queries. When GitHub is anonymous, use a conservative query budget. If it becomes limited, stop further API requests, preserve unexecuted queries, and try authenticated search, web search, skill directories, or direct verification of known repository URLs.


- Do not search only the user's original wording. First run LLM seed discovery, then generate a search matrix with original terms, English terms, synonyms, parent categories, adjacent categories, module terms, implementation terms, product alternative terms, and LLM-seeded terms.
- Search both full-project candidates and reusable module/package candidates.
- Prefer high-recall search over quick single-source search. Use GitHub plus at least one package/model/product ecosystem when tools allow.
- If full-project candidates are fewer than 3 or module candidates are fewer than 5, expand keywords and search again before making a decision.
- After finding a strong candidate, expand through its README, topics, dependencies, related projects, forks, alternatives, and referenced competitors when available.
- Filter search noise before scoring. Exclude obvious false positives, copied-description spam, unrelated repositories with keyword-stuffed descriptions, and results whose actual repository purpose does not match the query.
- Cluster results by reuse role rather than presenting a flat link list.
- Highlight exact/high-overlap complete projects before lower-level modules. The first recommendation must answer: "Can I directly deploy/fork one existing thing instead of assembling many parts?"
- Produce a decision report, not a directory of links.
- Include search scope, uncovered sources, confidence, and unverified items.
- Report attempted, completed, incomplete, and skipped source coverage separately. Do not describe an attempted but failed source as covered.
- Never claim that nobody has built something. Say only what was or was not found in the current search scope.

## Reuse Decisions

The final report must choose one primary recommendation:

- `direct_use`: use an existing product or hosted tool.
- `fork_existing`: fork an existing project as the base.
- `compose_modules`: combine packages/templates/services.
- `reference_only`: use existing work for design or architecture, but build the core.
- `build_mvp`: build a narrow MVP from scratch only after reusable options are weak.
- `pause_and_narrow`: clarify scope or search more before building.

## Candidate Classification

Classify each useful candidate as one or more of:

- Complete project
- Library/SDK/package
- Template/boilerplate
- SaaS/product alternative
- Demo/prototype
- Awesome/list/curated directory
- Skill/agent workflow
- Reference project
- Avoid

For each candidate, capture: name, URL, source, type, what it does, overlap with the user's idea, best use, reuse mode, maintenance signal, adoption signal, documentation signal, setup complexity, license signal, risks, and verdict.

Do not let noisy search results become candidates. If a repository appears only because of unrelated copied text, config dumps, project-list content, or keyword stuffing, omit it or mention it only in the search audit as filtered noise.

## Confidence Rules

Use high confidence only when multiple sources were searched, strong candidates were found, candidates cross-validate each other, and key README/docs were inspected.

Use medium confidence when main sources were searched and some relevant candidates were found, but setup, demo, issue state, or license was not fully verified.

Use low confidence when search tools/network are unavailable, only one source was searched, candidates are sparse, keywords are uncertain, the user idea is vague, or candidate details cannot be inspected.

With low confidence, do not recommend a strong from-scratch build. Recommend narrowing, verifying, or supplementary search.

An incomplete required source always forces low confidence for that candidate type, even if unrelated sources completed successfully.


## Output Style

Default to a concise, beginner-friendly answer. The first section must be a short plain-language conclusion, not a technical report.

Structure final answers as:

1. `先说结论`: 1-3 short paragraphs. Explain whether the idea is already mostly done, can be assembled from existing parts, or looks relatively new.
2. `你下一步可以怎么做`: 2-4 concrete next steps.
3. `可以直接复制给 LLM/Codex 的 Prompt`: a copyable prompt for the next implementation/research agent.
4. `详细依据（可跳过）`: candidate table, search audit, confidence, risks, and technical details.

Keep technical details out of the first section. Use beginner-friendly terms: “现成项目”, “可以直接改”, “可以当零件用”, “只适合参考”. If a technical term is necessary, explain it briefly, e.g. “fork（复制一份现有项目来改）”.

Do not dump raw search matrices, debug counters, or long candidate lists into the user-facing summary. Put them in the optional details section.

## Report And References

Use `references/report-template.md` for the final report shape and Codex handoff prompt.

Use `references/search-strategy.md` for high-recall search tactics, query templates, candidate expansion, and anti-miss rules.

Use `references/scoring-rubric.md` for candidate fields, reuse modes, and scoring labels.

Use `references/examples.md` when you need realistic test cases or output calibration.

Use `references/batch-review-template.md` when summarizing many reuse-scout test cases for human review; keep debug counters separate from review conclusions.

## Anti-Hallucination Rules

Do not invent candidates, metrics, license details, maintenance state, or installation status. If a field is unknown, mark it `unknown_needs_verification`. LLM-suggested candidates are unverified seeds until confirmed through an inspectable source.

Forbidden phrases:

- "Nobody has built this"
- "No similar project exists"
- "This is a blank market"
- "The only option is to build from scratch"
- "No existing skill/project was found" when a required search source was incomplete
- "This is definitely suitable to fork" when it has not been verified

Preferred phrases:

- "Within the current search scope, I did not find a high-overlap complete project."
- "This appears suitable as a fork base, but setup and license still need verification."
- "The safer path is to reuse modules A/B/C and build only the differentiated workflow."



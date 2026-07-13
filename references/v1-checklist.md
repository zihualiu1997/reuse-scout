# V1 Research Checklist

Use this checklist for every reuse-scout report. It keeps the process decision-oriented while leaving room for domain judgment.

## 1. Intake

- State the user idea in one sentence.
- Record assumptions when the user did not specify audience, form factor, deployment preference, license constraints, or budget.
- Ask at most 3 clarifying questions only when the answer would materially change the search or decision.

## 1.25 LLM Seed Discovery

Before exact-match search and broad decomposition, ask an LLM for semantic expansion seeds.

- Capture possible existing projects, products, templates, skills, and agent workflows.
- Capture alternate names, SEO keywords, Chinese/English variants, adjacent categories, and competitor/alternative queries.
- Mark all LLM-suggested candidates as unverified until inspected through GitHub, package registry, product page, README, docs, or official listing.
- Never use an LLM claim that no similar project exists as evidence for `build_mvp`.

## 1.5 Exact-Match / Seed Pass

Before broad decomposition, check whether one existing project already covers the end-to-end job.

- Search the user's original job-to-be-done as a complete phrase and as English/synonym/LLM-seeded variants.
- Search the requested product form, especially `skill`, `agent`, `template`, `boilerplate`, `self-hosted`, or `SaaS` when relevant.
- Verify any known candidate from the user, conversation memory, local docs, or prior examples.
- If a candidate has about 70%+ end-to-end overlap, compare every custom/module route against it and prefer verify/fork/direct-use first.

## 2. Search Matrix

Create terms in these groups before searching:

- Original terms.
- English/general ecosystem terms.
- Synonyms and parent categories.
- Module terms.
- Implementation terms.
- Product alternative terms.
- Skill/agent ecosystem terms when relevant.
- Exact-match, known-seed, and LLM-seeded terms when there may be a whole product/project match.

## 3. Coverage Targets

Unless the user requests a quick pass, attempt:

- At least 3 full-project query groups.
- At least 3 module/package query groups.
- At least 2 parent-category query groups.
- At least 2 code/package/model sources when tools allow.
- At least 1 product/alternative/directory source when tools allow.

If sources are unavailable, record that in the search audit.

## 4. Candidate Hygiene

- Exclude copied-description noise, config dumps, broad project-list repos, dotfiles, and keyword-stuffed false positives.
- Do not count filtered noise toward candidate-count minimums.
- Deduplicate the same project across package, repo, docs, and demo URLs.
- Keep low-star candidates only when they solve a narrow module unusually well or are exact matches needing verification.

## 5. Candidate Review

For each meaningful candidate, capture:

- Name and URL.
- Source and type.
- What it does.
- Overlap with the user's idea.
- Best reuse mode.
- Maintenance/adoption/documentation/setup/license signals.
- Main risks and verification gaps.

## 6. Decision

Choose one primary recommendation:

- `direct_use`
- `fork_existing`
- `compose_modules`
- `reference_only`
- `build_mvp`
- `pause_and_narrow`

Prefer `pause_and_narrow` or more search when confidence is low.

## 7. Final Checks

Before finalizing, ensure the report includes:

- Do-not-rebuild list.
- MVP route.
- Codex handoff prompt.
- Search audit with sources, keywords, LLM seed terms used, candidate counts, confidence, and unverified items.
- No unsupported claim that nobody has built something.

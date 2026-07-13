# Reuse Scout Report Template

Use this structure for final output.

```markdown
# Reuse Scout Reuse Review

## Decision

Primary recommendation: direct_use / fork_existing / compose_modules / reference_only / build_mvp / pause_and_narrow

One-sentence reason: ...

Confidence: high / medium / low

## 1. Idea Decomposition

- Original idea: ...
- Target users: ...
- Core jobs to be done: ...
- Must-have features: ...
- Later features: ...
- Reusable modules: ...
- Assumptions: ...

## 2. Search Matrix

- Original terms: ...
- English terms: ...
- Synonyms / parent categories: ...
- Module terms: ...
- Product alternative terms: ...
- Ecosystem terms: ...

## 3. Candidate Overview

| Candidate | Type | Source | Relevance | Reuse mode | Risk | Verdict |
|---|---|---|---|---|---|---|
| ... | ... | ... | high/medium/low | ... | ... | ... |

## 4. Key Candidate Notes

### Candidate name

- URL: ...
- What it does: ...
- Overlap with the idea: ...
- Best use: direct use / fork / module / reference / avoid
- Strengths: ...
- Risks: ...
- Needs verification: ...

## 5. Do-Not-Rebuild List

- Module: reuse recommendation and reason
- Module: reuse recommendation and reason

## 6. Recommended MVP Route

Build first: ...

Do not build in this round: ...

Recommended combination:

1. Base: ...
2. Core modules: ...
3. Custom differentiated work: ...

## 7. Codex Handoff Prompt

```text
Continue this project using the reuse-scout findings.

User goal: {goal}

Recommended route: {decision}

Prefer reusing:
1. {candidate_1} - purpose: {usage_1}
2. {candidate_2} - purpose: {usage_2}
3. {candidate_3} - purpose: {usage_3}

Do not build from scratch:
- {module_1}
- {module_2}
- {module_3}

This round only implements:
- {mvp_scope_1}
- {mvp_scope_2}

This round does not implement:
- {out_of_scope_1}
- {out_of_scope_2}

Before coding:
1. Read candidate README, license, and installation instructions.
2. Check whether the candidate still runs or installs.
3. If a candidate is unusable, report why before choosing an alternative.
4. Keep existing base capabilities and implement only differentiated modules.
```

## 8. Search Audit

- Sources searched: GitHub / npm / PyPI / Hugging Face / AlternativeTo / ...
- Sources not covered: ...
- Keywords used: ...
- Expanded keywords: ...
- Candidate count: X complete projects, Y modules/packages, Z product alternatives
- Confidence: high / medium / low
- Unverified items: install not tested / issues not checked / license not confirmed / demo not verified
```


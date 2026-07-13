# Scoring Rubric

Use labels before numeric scores. Do not overfit to stars.

## Candidate Fields

```yaml
candidate:
  name:
  url:
  source:
  type:
  what_it_does:
  overlap_with_user_idea:
  best_use:
  reuse_mode:
  maintenance_signal:
  adoption_signal:
  documentation_signal:
  setup_complexity:
  license_signal:
  main_risks:
  verdict:
```

## Reuse Modes

- `direct_use`: use directly.
- `fork_base`: suitable as a fork base.
- `module_dependency`: use as a module dependency.
- `template_start`: use as a template starting point.
- `reference_only`: reference design or architecture only.
- `avoid`: do not use.
- `unknown_needs_verification`: information is insufficient.

## Labels

- Relevance: high / medium / low.
- Maturity: high / medium / low / unknown.
- Maintenance: active / mixed / stale / unknown.
- Setup difficulty: low / medium / high / unknown.
- Reuse value: high / medium / low.
- Risk: low / medium / high.

## Judgment Priorities

Prioritize:

- Whether the candidate solves the user's core job to be done.
- Whether it covers modules the user should not rebuild.
- Whether the current user/agent can realistically adapt it.
- README clarity, examples, install instructions, and demo availability.
- Recent maintenance and issue health.
- License compatibility signals.
- Technology stack fit with the requested product form.

Do not treat stars, popularity, or recency as sufficient. A lower-star library may be the best module dependency if it fits the core task and is easy to integrate.

## Exclusion Rules

Exclude or quarantine a result before scoring when:

- The repository purpose is unrelated after checking the name, description, topics, or README snippet.
- The search match comes from copied issue/commit text, generated config, terms text, or a broad project-ideas list.
- The repository is a personal dotfiles/config dump rather than a reusable project.
- The candidate has no discoverable license and would be recommended for direct reuse or fork; it may still be listed as `unknown_needs_verification` if it is uniquely relevant.
- The repository is low-signal and duplicates a stronger, clearer candidate.

Mention excluded result classes in the search audit if they materially affected search quality.

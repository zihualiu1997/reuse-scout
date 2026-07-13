# Search Strategy

Search success is the core capability. Do not treat this as a single GitHub search. Use high-recall, multi-round search.

## Search Matrix

Create this before searching:

```yaml
search_matrix:
  original_terms:
  english_terms:
  synonyms:
  parent_categories:
  adjacent_categories:
  module_terms:
  implementation_terms:
  product_alternative_terms:
  ecosystem_terms:
```

Example for a Rednote/Xiaohongshu asset and carousel tool:

```yaml
original_terms:
  - 小红书素材管理
  - 图文卡片生成
english_terms:
  - Xiaohongshu content tool
  - Rednote creator tool
  - social media asset manager
synonyms:
  - creator toolkit
  - content workflow
  - carousel generator
parent_categories:
  - social media management
  - digital asset management
  - content marketing platform
module_terms:
  - canvas editor
  - image template generator
  - media library
  - content calendar
implementation_terms:
  - React canvas editor
  - image export PNG
  - template editor web app
product_alternative_terms:
  - Canva alternative
  - Buffer alternative
  - Later alternative
```

## Source Priority

1. GitHub: complete projects, templates, awesome lists.
2. npm: frontend libraries, SDKs, editors, utilities.
3. PyPI: Python tools, AI workflows, automation packages.
4. Hugging Face: models, Spaces, datasets, AI demos.
5. Product Hunt / AlternativeTo / SaaSHub: products and substitutes.
6. Docker Hub / Vercel / Railway templates: deployable templates.
7. Skill/agent ecosystems: Codex skills, Claude skills, Cursor rules, agent workflows.


## V2 Scripted Search

When available, use `scripts/reuse_scout_search.py` to gather first-pass candidate evidence:

```bash
python scripts/reuse_scout_search.py --query "open source resume builder AI optimizer" --query "ATS resume checker open source" --format markdown
```

Supported sources in V2:

- GitHub repository search.
- npm registry search.
- Hugging Face model search where the public API responds.

The script does not replace judgment. After running it, still inspect high-value candidates, expand around strong candidates, and apply the scoring rubric.

Use `GITHUB_TOKEN` when available to reduce GitHub API rate-limit risk. Without a token, the script should still run but may hit stricter limits.

## Query Templates

GitHub:

```text
{domain} {product_type} open source
{domain} {job_to_be_done} github
{module} {framework} github
{keyword} awesome
{keyword} boilerplate
{keyword} template
{keyword} self hosted
{keyword} alternative
```

npm:

```text
{module}
{module} react
{module} editor
{module} generator
{module} export
{domain} sdk
```

PyPI:

```text
{domain}
{module}
{domain} parser
{domain} generator
{domain} automation
{ai_task}
```

Hugging Face:

```text
{domain}
{task}
{content_type}
{model_task}
{language/domain-specific term}
```

Product alternatives:

```text
{domain} software
{domain} tool
{product_type} alternative
best {domain} tools
open source alternative to {known_product}
```

## Candidate Expansion

After finding a candidate, inspect or search around:

- README mentions of alternatives, inspired by, related projects.
- GitHub topics.
- Package dependencies and dependent packages.
- Author or organization adjacent projects.
- Awesome/list entries in the same area.
- Similar repositories, forks, or same-name package repos.
- Issues/docs that mention competitors.

## Result Hygiene

Before scoring candidates, remove obvious search noise:

- Repositories where the description is copied commit text, config dumps, terms-of-service text, or a huge unrelated document.
- Project-list repositories that mention the keyword as one item among many unrelated practice ideas.
- Keyword-stuffed repositories whose actual purpose differs from the query.
- Personal dotfiles/config repositories unless the actual project is inside a relevant subfolder and worth inspecting.
- Abandoned examples with no README or unclear runnable path, unless they solve a narrow module unusually well.

If noisy results are common, add a short note to the search audit:

```text
Filtered noise: several GitHub results matched keywords through copied descriptions or unrelated project-list content and were excluded from candidate scoring.
```

Do not count filtered noise toward candidate-count minimums.

## Reverse Search

For strong candidates, search:

```text
"project-name" alternative
"project-name" vs
"project-name" GitHub topic
"project-name" inspired by
"project-name" fork
```

## Anti-Miss Rules

- Unless the user requests a quick pass, cover at least 3 full-project keyword groups, 3 module keyword groups, 2 parent-category keyword groups, 2 code/package sources, and 1 product/alternative source when available.
- If complete projects are fewer than 3, expand keywords and search again.
- If module/package candidates are fewer than 5, expand module and implementation terms and search again.
- Candidate-count minimums apply only after result hygiene filtering.
- For Chinese-market ideas, search Chinese terms, English terms, and brand/community terms such as pinyin or international names.
- If candidate counts remain low, state that scarcity in the current search scope does not prove an ecosystem gap.


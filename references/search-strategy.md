# Search Strategy

Search success is the core capability. Do not treat this as a single GitHub search. Use high-recall, multi-round search.

## LLM Seed Discovery

Run this before the search matrix. Its job is semantic expansion: find the names that different communities, SEO pages, GitHub authors, package authors, or product marketers might use for the same idea.

Ask the model for:

- Existing open-source projects, products, templates, skills, or agent workflows that might already solve the end-to-end job.
- Synonyms, adjacent categories, industry terms, pinyin/Chinese/English variants, and SEO phrases.
- Known competitor names, alternative-to queries, and community-specific labels.
- Exact GitHub/package/product queries to try.
- High-risk miss directions: terms that would cause a strong candidate to be missed if not searched.

Use the output only as seeds. Verification rules:

- Do not score or recommend an LLM-suggested candidate until a repository, package registry, product page, README, docs, or official listing has been inspected.
- If a suggested name cannot be verified, keep it in the search audit as `unverified_seed` or omit it from candidates.
- If the LLM suggests no known project, continue normal external search; absence from the seed pass is not evidence that the idea is new.

Prompt template:

```text
Given this software idea, list possible existing projects/products/templates/skills and the names different communities might use for it. Return only search seeds, not conclusions.

Idea: {user_idea}

Include:
1. likely exact-match project/product/skill names
2. alternate category names and SEO keywords
3. GitHub/package/product search queries
4. adjacent ecosystems to search
5. high-risk missed keywords
6. candidates that must be verified first
```

## Search Matrix

Create this after LLM seed discovery and before searching:

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
  llm_seed_terms:
  llm_seed_candidates_to_verify:
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

### Exact-Match Pass

Run an exact/high-overlap pass before broad module search. The goal is to avoid missing a project that already does the whole job.

Use these patterns:

```text
"{job_to_be_done}" github
"{input_material}" "{output_product}" github
"{domain}" "skill" github
"{domain}" "agent" "chat logs"
"{desired_product_form}" "source materials"
"{known_candidate_or_concept}" alternative
```

If this pass finds an end-to-end candidate, inspect it before continuing. It may make most module-search results secondary.


1. GitHub: complete projects, templates, awesome lists.
2. npm: frontend libraries, SDKs, editors, utilities.
3. PyPI: Python tools, AI workflows, automation packages.
4. Hugging Face: models, Spaces, datasets, AI demos.
5. Product Hunt / AlternativeTo / SaaSHub: products and substitutes.
6. Docker Hub / Vercel / Railway templates: deployable templates.
7. Skill/agent ecosystems: Codex skills, Claude skills, Cursor rules, agent workflows.
8. Known/contextual seed candidates from the user's prior conversation, local memory, or explicitly mentioned repos; verify rather than assuming.


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

### Skill / Agent From Materials Templates

Use these whenever the idea is "upload real materials and distill a reusable assistant/skill/persona/customer-service bot":

```text
colleague skill github
digital colleague skill github
persona skill work skill github
chat history to chatbot github
chat logs customer service bot github
conversation distillation chatbot github
customer service skill from chat logs
AI employee clone source materials github
wechat chat records customer service bot
微信聊天记录 客服机器人 github
聊天记录 蒸馏 客服机器人
```

Known regression seed: for prompts like "create an AI customer-service skill by uploading WeChat chat records and distilling a bot for common questions", `https://github.com/titanwings/colleague-skill.git` is a high-overlap candidate that must be inspected or clearly marked unavailable/unverified. Do not replace it with a generic RAG/module architecture unless verification shows it is unsuitable.


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

- Unless the user requests a quick pass, run LLM seed discovery, then cover at least 3 full-project keyword groups, 3 module keyword groups, 2 parent-category keyword groups, 2 code/package sources, and 1 product/alternative source when available.
- If complete projects are fewer than 3, expand keywords and search again.
- If module/package candidates are fewer than 5, expand module and implementation terms and search again.
- Candidate-count minimums apply only after result hygiene filtering.
- For Chinese-market ideas, search Chinese terms, English terms, and brand/community terms such as pinyin or international names.
- For skill/agent-building ideas, search skill/agent/persona terms before generic app/RAG terms. A skill-generation project can be a better match than a chatbot framework.
- If a known seed candidate is available from context or LLM seed discovery, include it in the exact-match pass even if ordinary keyword search did not surface it.
- If candidate counts remain low, state that scarcity in the current search scope does not prove an ecosystem gap.


# Examples And Evaluation Cases

Use these as forward-test prompts and output calibration cases.

## Evaluation Cases

1. AI resume optimization tool.
2. Rednote/Xiaohongshu asset manager and carousel card generator.
3. Personal knowledge base with RAG Q&A.
4. Local file auto-classification tool.
5. AI meeting-minutes organizer.
6. Chrome extension: summarize web pages into Notion.
7. Shopify/independent-store product image batch generator.
8. Sales follow-up automation mini CRM.
9. AI PPT generator.
10. Desktop pet / virtual assistant tool.

## Checks

For each case, verify:

- The output decomposes the idea before searching.
- Search covers full projects and modules/packages.
- The search matrix includes synonyms and parent categories.
- The report avoids unsupported claims that nothing exists.
- There is one clear primary recommendation.
- There is a do-not-rebuild list.
- There is a Codex handoff prompt.
- Obvious false positives and polluted GitHub results are filtered before candidate scoring.

## Mini Example

User idea: "I want to build an AI resume optimizer."

Expected shape:

- Decompose into resume builder, resume parser, ATS checker, JD matching, cover letter generation, template editing, PDF export.
- Search for complete resume builders and JSON Resume/markdown resume ecosystems.
- Search packages for resume parsing, PDF export, and document templating.
- Likely decision: do not build a complete editor from scratch; reuse JSON Resume or markdown resume tooling and build the differentiated JD matching and rewrite workflow.
- Handoff prompt should forbid rebuilding resume templates, PDF export, and basic editing unless existing candidates fail verification.
- Search audit should note if broad GitHub searches returned noisy false positives such as config dumps or project-list repositories.


## Regression Case: WeChat Chat Records -> Customer-Service Skill

User idea: "我想创建一个 ai 客服的 skill，我通过上传微信的聊天记录，蒸馏出一个客服机器人用来回答常见的问题"

Expected behavior:

- Do not jump straight to a custom RAG architecture or a long list of modules.
- Run LLM seed discovery first; it should surface or help search terms like `colleague skill`, `digital colleague`, `work skill`, `persona skill`, `chat history to chatbot`, `conversation distillation`, `微信聊天记录 客服机器人`.
- Treat LLM output as seeds only; verify every named project through GitHub/README/docs before recommending it.
- Search exact-match skill/agent/persona-generation terms before generic RAG terms.
- Inspect or explicitly mark unavailable the seed candidate `https://github.com/titanwings/colleague-skill.git`.
- If the seed candidate is available and roughly matches, likely decision: `fork_existing` or `pause_and_narrow` first. The user should try/deploy/fork that project before building a new multi-module system.
- Put generic RAG parts such as parsers, embeddings, vector DBs, FAQ extraction, and admin UI in the "only if the fork fails / later extension" bucket, not as the main route.
- Handoff prompt should say: verify license/setup/data ingestion of `titanwings/colleague-skill`, run it on a small WeChat export sample, and only then decide what minimal adapters are needed.

## Regression Case: Required Skill Search Is Rate-Limited

Observed search state:

- npm and Hugging Face queries complete.
- Product documentation is inspected.
- GitHub general queries partly complete.
- Codex/Claude skill-specific GitHub queries hit an anonymous API rate limit.

Expected behavior:

- Do not say "no existing skill was found", even with a current-search-scope caveat.
- State that the skill-specific search is incomplete and the result is inconclusive.
- Explain that npm, Hugging Face, and product documentation do not replace GitHub/skill-ecosystem coverage.
- Assign low confidence and choose `pause_and_narrow` until authenticated GitHub search or fallback discovery completes.
- Preserve the failed and skipped queries so a later run can resume them.

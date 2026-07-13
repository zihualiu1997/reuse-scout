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

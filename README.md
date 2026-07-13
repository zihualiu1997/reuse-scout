# reuse-scout

`reuse-scout` is a Codex skill for checking whether a new vibecoding idea already has useful existing projects, packages, templates, or products to reuse before building from scratch.

## Installed-skill update flow

Use this repository as the versioned source of truth. Keep the installed Codex skill as a copied runtime version.

Default paths on this machine:

```text
Repo:    C:\Users\AIRI\Documents\Q&A_Bot\work\reuse-scout-publish
Install: C:\Users\AIRI\.codex\skills\reuse-scout
```

To pull the latest GitHub version, sync the installed skill, and validate it:

```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\AIRI\Documents\Q&A_Bot\work\reuse-scout-publish\tools\update-installed.ps1"
```

The script copies only the skill runtime files:

```text
SKILL.md
agents/
references/
scripts/
```

It intentionally does not copy `.git`, `README.md`, or `tools/` into the installed skill folder.

## Manual validation

```powershell
$env:PYTHONUTF8='1'
python "C:\Users\AIRI\.codex\skills\.system\skill-creator\scripts\quick_validate.py" "C:\Users\AIRI\.codex\skills\reuse-scout"
```

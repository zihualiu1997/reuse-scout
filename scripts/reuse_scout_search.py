#!/usr/bin/env python3
"""Structured public-source search helper for the reuse-scout skill.

This dependency-free helper gathers first-pass candidate evidence from public
APIs, filters obvious search noise, deduplicates URLs, and emits JSON or
Markdown for the agent to inspect. It is not a ranking oracle.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable

USER_AGENT = "reuse-scout/0.2"
DEFAULT_TIMEOUT = 20
NOISE_PATTERNS = [
    r"skip to content",
    r"showing \d+ changed files",
    r"automatically generated file",
    r"do not edit",
    r"terms of service",
    r"last updated:",
    r"config_target_",
    r"config_package_",
    r"mega project list",
]

@dataclass
class Candidate:
    name: str
    url: str
    source: str
    description: str = ""
    stars: int | None = None
    updated_at: str | None = None
    license: str | None = None
    topics: list[str] = field(default_factory=list)
    package_version: str | None = None
    package_downloads_weekly: int | None = None
    candidate_type: str = "unknown"
    hygiene_status: str = "kept"
    hygiene_notes: list[str] = field(default_factory=list)
    query: str = ""


def http_json(url: str, token: str | None = None) -> tuple[Any | None, str | None]:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=DEFAULT_TIMEOUT) as response:
            raw = response.read().decode("utf-8", errors="replace")
            return json.loads(raw), None
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:500]
        return None, f"HTTP {exc.code}: {body}"
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def compact_text(value: str | None, limit: int = 500) -> str:
    text = re.sub(r"\s+", " ", value or "").strip()
    return text[:limit]


def query_tokens(query: str) -> set[str]:
    stop = {"open", "source", "github", "software", "project", "tool", "tools", "with", "using", "free"}
    return {token for token in re.findall(r"[a-zA-Z0-9]+", query.lower()) if len(token) > 2 and token not in stop}


def hygiene_notes(name: str, description: str, topics: Iterable[str] = (), query: str = "") -> list[str]:
    haystack = " ".join([name or "", description or "", " ".join(topics)]).lower()
    notes: list[str] = []
    for pattern in NOISE_PATTERNS:
        if re.search(pattern, haystack, flags=re.IGNORECASE):
            notes.append(f"matched noise pattern: {pattern}")
    if len(description or "") > 1200:
        notes.append("very long description")
    if name.startswith(".") or "/." in name:
        notes.append("dotfile/config-like repository name")
    tokens = query_tokens(query)
    if len(tokens) >= 2:
        overlap = {token for token in tokens if token in haystack}
        if len(overlap) < 2:
            notes.append("low query-term overlap")
    return notes


def classify_from_text(name: str, description: str, topics: Iterable[str] = ()) -> str:
    name_desc = " ".join([name, description]).lower()
    text = " ".join([name, description, " ".join(topics)]).lower()
    # Treat awesome/list signals in the project name or description as a directory.
    # Do not classify a normal project as a directory only because it has topics
    # such as awesome-ai-tools or awesome-resumes.
    if "awesome" in name_desc or "curated" in name_desc or re.search(r"\\blist\\b", name_desc):
        return "curated_directory"
    if "template" in name.lower() or "boilerplate" in name.lower():
        return "template"
    if "sdk" in text or "library" in text or "package" in text:
        return "library_package"
    if "mcp" in text or "agent" in text or "skill" in text:
        return "skill_agent_workflow"
    if "model" in text or "dataset" in text or "transformers" in text:
        return "model_or_ai_asset"
    return "complete_or_reference_project"


def search_github(query: str, limit: int, token: str | None) -> tuple[list[Candidate], str | None]:
    params = urllib.parse.urlencode({"q": query, "sort": "stars", "order": "desc", "per_page": limit})
    data, error = http_json(f"https://api.github.com/search/repositories?{params}", token=token)
    if error:
        return [], error
    candidates: list[Candidate] = []
    for item in data.get("items", []) if isinstance(data, dict) else []:
        topics = item.get("topics") or []
        desc = compact_text(item.get("description"))
        notes = hygiene_notes(item.get("full_name", ""), desc, topics, query)
        license_obj = item.get("license") or {}
        candidates.append(Candidate(
            name=item.get("full_name") or item.get("name") or "unknown",
            url=item.get("html_url") or "",
            source="github",
            description=desc,
            stars=item.get("stargazers_count"),
            updated_at=item.get("pushed_at") or item.get("updated_at"),
            license=license_obj.get("spdx_id") or license_obj.get("key"),
            topics=list(topics),
            candidate_type=classify_from_text(item.get("full_name", ""), desc, topics),
            hygiene_status="filtered_noise" if notes else "kept",
            hygiene_notes=notes,
            query=query,
        ))
    return candidates, None


def search_npm(query: str, limit: int) -> tuple[list[Candidate], str | None]:
    params = urllib.parse.urlencode({"text": query, "size": limit})
    data, error = http_json(f"https://registry.npmjs.org/-/v1/search?{params}")
    if error:
        return [], error
    candidates: list[Candidate] = []
    for obj in data.get("objects", []) if isinstance(data, dict) else []:
        package = obj.get("package") or {}
        links = package.get("links") or {}
        desc = compact_text(package.get("description"))
        name = package.get("name") or "unknown"
        notes = hygiene_notes(name, desc, package.get("keywords") or [], query)
        candidates.append(Candidate(
            name=name,
            url=links.get("repository") or links.get("npm") or "",
            source="npm",
            description=desc,
            updated_at=package.get("date") or obj.get("updated"),
            license=package.get("license"),
            topics=list(package.get("keywords") or []),
            package_version=package.get("version"),
            package_downloads_weekly=(obj.get("downloads") or {}).get("weekly"),
            candidate_type="library_package",
            hygiene_status="filtered_noise" if notes else "kept",
            hygiene_notes=notes,
            query=query,
        ))
    return candidates, None


def search_huggingface(query: str, limit: int) -> tuple[list[Candidate], str | None]:
    params = urllib.parse.urlencode({"search": query, "limit": limit})
    data, error = http_json(f"https://huggingface.co/api/models?{params}")
    if error:
        return [], error
    candidates: list[Candidate] = []
    if not isinstance(data, list):
        return candidates, None
    for item in data:
        model_id = item.get("modelId") or item.get("id") or "unknown"
        tags = item.get("tags") or []
        desc = compact_text(" ".join(tags[:12]))
        notes = hygiene_notes(model_id, desc, tags, query)
        candidates.append(Candidate(
            name=model_id,
            url=f"https://huggingface.co/{model_id}",
            source="huggingface_models",
            description=desc,
            stars=item.get("likes"),
            updated_at=item.get("lastModified"),
            topics=list(tags),
            candidate_type="model_or_ai_asset",
            hygiene_status="filtered_noise" if notes else "kept",
            hygiene_notes=notes,
            query=query,
        ))
    return candidates, None


def dedupe(candidates: Iterable[Candidate]) -> list[Candidate]:
    by_key: dict[str, Candidate] = {}
    for candidate in candidates:
        key = candidate.url.lower().removeprefix("git+").removesuffix(".git") or f"{candidate.source}:{candidate.name.lower()}"
        existing = by_key.get(key)
        if existing is None:
            by_key[key] = candidate
            continue
        # Prefer a kept candidate over a filtered duplicate. The same project can
        # be weak for one broad query and strong for another module query.
        if existing.hygiene_status != "kept" and candidate.hygiene_status == "kept":
            by_key[key] = candidate
            continue
        if existing.hygiene_status == candidate.hygiene_status == "kept":
            existing.query = existing.query + " | " + candidate.query
    return list(by_key.values())


def run_search(queries: list[str], sources: list[str], limit: int) -> dict[str, Any]:
    token = os.environ.get("GITHUB_TOKEN")
    all_candidates: list[Candidate] = []
    failures: list[dict[str, str]] = []
    for query in queries:
        if "github" in sources:
            candidates, error = search_github(query, limit, token)
            all_candidates.extend(candidates)
            if error:
                failures.append({"source": "github", "query": query, "error": error})
        if "npm" in sources:
            candidates, error = search_npm(query, limit)
            all_candidates.extend(candidates)
            if error:
                failures.append({"source": "npm", "query": query, "error": error})
        if "huggingface" in sources:
            candidates, error = search_huggingface(query, limit)
            all_candidates.extend(candidates)
            if error:
                failures.append({"source": "huggingface", "query": query, "error": error})
        time.sleep(0.1)
    unique = dedupe(all_candidates)
    kept = [c for c in unique if c.hygiene_status == "kept"]
    filtered = [c for c in unique if c.hygiene_status != "kept"]
    return {
        "queries": queries,
        "sources": sources,
        "candidate_count": len(unique),
        "kept_count": len(kept),
        "filtered_noise_count": len(filtered),
        "failures": failures,
        "candidates": [asdict(c) for c in kept],
        "filtered_noise": [asdict(c) for c in filtered[:25]],
    }


def to_markdown(result: dict[str, Any]) -> str:
    lines = ["# reuse-scout search results", ""]
    lines.append(f"Queries: {', '.join(result['queries'])}")
    lines.append(f"Sources: {', '.join(result['sources'])}")
    lines.append(f"Candidates: {result['kept_count']} kept, {result['filtered_noise_count']} filtered noise, {len(result['failures'])} source failures")
    if result["failures"]:
        lines.extend(["", "## Source failures"])
        for failure in result["failures"]:
            lines.append(f"- {failure['source']} / {failure['query']}: {failure['error']}")
    lines.extend(["", "## Kept candidates", ""])
    lines.append("| Name | Source | Type | Signal | Description | URL |")
    lines.append("|---|---|---|---:|---|---|")
    for c in result["candidates"]:
        signal = c.get("stars") if c.get("stars") is not None else c.get("package_downloads_weekly") or ""
        desc = (c.get("description") or "").replace("|", "\\|")[:180]
        lines.append(f"| {c['name']} | {c['source']} | {c['candidate_type']} | {signal} | {desc} | {c['url']} |")
    if result["filtered_noise"]:
        lines.extend(["", "## Filtered noise sample"])
        for c in result["filtered_noise"][:10]:
            note = "; ".join(c.get("hygiene_notes") or [])
            lines.append(f"- {c['name']} ({c['source']}): {note}")
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search public sources for reuse-scout candidate evidence.")
    parser.add_argument("--query", action="append", required=True, help="Search query. Repeat for multiple queries.")
    parser.add_argument("--source", action="append", choices=["github", "npm", "huggingface"], help="Source to search. Defaults to all supported sources.")
    parser.add_argument("--limit", type=int, default=5, help="Max results per query per source.")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    args = parse_args(argv)
    sources = args.source or ["github", "npm", "huggingface"]
    result = run_search(args.query, sources, max(1, min(args.limit, 25)))
    if args.format == "markdown":
        sys.stdout.write(to_markdown(result))
    else:
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))




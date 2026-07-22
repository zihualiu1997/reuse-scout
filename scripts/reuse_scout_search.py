#!/usr/bin/env python3
"""Collect first-pass reuse candidates from public APIs.

The helper keeps successful empty searches distinct from incomplete searches so
downstream agents do not turn rate limits or network failures into negative
findings.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable, Mapping

USER_AGENT = "reuse-scout/0.3"
DEFAULT_TIMEOUT = 20
SUCCESS_STATUSES = {"results", "empty"}
SKIPPED_STATUSES = {"skipped_rate_limited", "skipped_budget"}
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


@dataclass
class HttpResult:
    data: Any | None
    status: str
    error: str | None = None
    status_code: int | None = None
    rate_limit_remaining: str | None = None
    rate_limit_reset: str | None = None
    retry_after: str | None = None


@dataclass
class QueryOutcome:
    source: str
    query: str
    status: str
    candidate_count: int = 0
    error: str | None = None
    status_code: int | None = None
    rate_limit_remaining: str | None = None
    rate_limit_reset: str | None = None
    retry_after: str | None = None


def header_value(headers: Mapping[str, str] | Any, name: str) -> str | None:
    if not headers:
        return None
    value = headers.get(name) or headers.get(name.lower())
    return str(value) if value is not None else None


def classify_http_failure(status_code: int, body: str, headers: Mapping[str, str] | Any) -> str:
    remaining = header_value(headers, "X-RateLimit-Remaining")
    body_lower = body.lower()
    if status_code == 429 or (
        status_code == 403
        and (remaining == "0" or "rate limit" in body_lower or "secondary rate" in body_lower)
    ):
        return "rate_limited"
    if status_code in {401, 403}:
        return "auth_failed"
    return "http_error"


def http_json(url: str, token: str | None = None) -> HttpResult:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=DEFAULT_TIMEOUT) as response:
            raw = response.read().decode("utf-8", errors="replace")
            response_headers = response.headers
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as exc:
                return HttpResult(
                    data=None,
                    status="invalid_response",
                    error=f"JSONDecodeError: {exc}",
                    status_code=getattr(response, "status", None),
                )
            return HttpResult(
                data=data,
                status="ok",
                status_code=getattr(response, "status", 200),
                rate_limit_remaining=header_value(response_headers, "X-RateLimit-Remaining"),
                rate_limit_reset=header_value(response_headers, "X-RateLimit-Reset"),
                retry_after=header_value(response_headers, "Retry-After"),
            )
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:500]
        status = classify_http_failure(exc.code, body, exc.headers)
        return HttpResult(
            data=None,
            status=status,
            error=f"HTTP {exc.code}: {body}",
            status_code=exc.code,
            rate_limit_remaining=header_value(exc.headers, "X-RateLimit-Remaining"),
            rate_limit_reset=header_value(exc.headers, "X-RateLimit-Reset"),
            retry_after=header_value(exc.headers, "Retry-After"),
        )
    except urllib.error.URLError as exc:
        return HttpResult(data=None, status="network_failed", error=f"URLError: {exc.reason}")
    except Exception as exc:
        return HttpResult(data=None, status="network_failed", error=f"{type(exc).__name__}: {exc}")


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
    if "awesome" in name_desc or "curated" in name_desc or re.search(r"\blist\b", name_desc):
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


def outcome_from_http(source: str, query: str, result: HttpResult) -> QueryOutcome:
    return QueryOutcome(
        source=source,
        query=query,
        status=result.status,
        error=result.error,
        status_code=result.status_code,
        rate_limit_remaining=result.rate_limit_remaining,
        rate_limit_reset=result.rate_limit_reset,
        retry_after=result.retry_after,
    )


def search_github(query: str, limit: int, token: str | None) -> tuple[list[Candidate], QueryOutcome]:
    params = urllib.parse.urlencode({"q": query, "sort": "stars", "order": "desc", "per_page": limit})
    result = http_json(f"https://api.github.com/search/repositories?{params}", token=token)
    if result.status != "ok":
        return [], outcome_from_http("github", query, result)
    if not isinstance(result.data, dict):
        return [], QueryOutcome("github", query, "invalid_response", error="expected JSON object")

    candidates: list[Candidate] = []
    for item in result.data.get("items", []):
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
    status = "results" if candidates else "empty"
    return candidates, QueryOutcome(
        "github",
        query,
        status,
        candidate_count=len(candidates),
        status_code=result.status_code,
        rate_limit_remaining=result.rate_limit_remaining,
        rate_limit_reset=result.rate_limit_reset,
        retry_after=result.retry_after,
    )


def search_npm(query: str, limit: int) -> tuple[list[Candidate], QueryOutcome]:
    params = urllib.parse.urlencode({"text": query, "size": limit})
    result = http_json(f"https://registry.npmjs.org/-/v1/search?{params}")
    if result.status != "ok":
        return [], outcome_from_http("npm", query, result)
    if not isinstance(result.data, dict):
        return [], QueryOutcome("npm", query, "invalid_response", error="expected JSON object")

    candidates: list[Candidate] = []
    for obj in result.data.get("objects", []):
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
    status = "results" if candidates else "empty"
    return candidates, QueryOutcome("npm", query, status, candidate_count=len(candidates))


def search_huggingface(query: str, limit: int) -> tuple[list[Candidate], QueryOutcome]:
    params = urllib.parse.urlencode({"search": query, "limit": limit})
    result = http_json(f"https://huggingface.co/api/models?{params}")
    if result.status != "ok":
        return [], outcome_from_http("huggingface", query, result)
    if not isinstance(result.data, list):
        return [], QueryOutcome("huggingface", query, "invalid_response", error="expected JSON list")

    candidates: list[Candidate] = []
    for item in result.data:
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
    status = "results" if candidates else "empty"
    return candidates, QueryOutcome("huggingface", query, status, candidate_count=len(candidates))


def dedupe(candidates: Iterable[Candidate]) -> list[Candidate]:
    by_key: dict[str, Candidate] = {}
    for candidate in candidates:
        key = candidate.url.lower().removeprefix("git+").removesuffix(".git") or f"{candidate.source}:{candidate.name.lower()}"
        existing = by_key.get(key)
        if existing is None:
            by_key[key] = candidate
            continue
        if existing.hygiene_status != "kept" and candidate.hygiene_status == "kept":
            by_key[key] = candidate
            continue
        if existing.hygiene_status == candidate.hygiene_status == "kept":
            existing.query = existing.query + " | " + candidate.query
    return list(by_key.values())


def dedupe_strings(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = value.strip()
        key = normalized.casefold()
        if normalized and key not in seen:
            seen.add(key)
            result.append(normalized)
    return result


def github_token() -> str | None:
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")


def summarize_sources(sources: list[str], query_map: dict[str, list[str]], outcomes: list[QueryOutcome]) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    for source in sources:
        source_outcomes = [outcome for outcome in outcomes if outcome.source == source]
        counts = Counter(outcome.status for outcome in source_outcomes)
        assigned = len(query_map.get(source, []))
        completed = sum(counts[status] for status in SUCCESS_STATUSES)
        skipped = sum(counts[status] for status in SKIPPED_STATUSES)
        failed = assigned - completed - skipped
        summary[source] = {
            "assigned": assigned,
            "completed": completed,
            "with_results": counts["results"],
            "empty": counts["empty"],
            "failed": max(0, failed),
            "skipped": skipped,
            "coverage_complete": assigned > 0 and completed == assigned,
            "statuses": dict(counts),
        }
    return summary


def run_search(
    queries: list[str],
    sources: list[str],
    limit: int,
    source_queries: dict[str, list[str]] | None = None,
    required_sources: list[str] | None = None,
    github_query_budget: int | None = None,
) -> dict[str, Any]:
    source_queries = source_queries or {}
    required_sources = dedupe_strings(required_sources or [])
    shared_queries = dedupe_strings(queries)
    query_map = {
        source: dedupe_strings([*source_queries.get(source, []), *shared_queries])
        for source in sources
    }

    token = github_token()
    all_candidates: list[Candidate] = []
    outcomes: list[QueryOutcome] = []
    github_attempts = 0
    github_blocked = False

    for source in sources:
        for query in query_map[source]:
            if source == "github" and github_blocked:
                outcomes.append(QueryOutcome("github", query, "skipped_rate_limited"))
                continue
            if source == "github" and github_query_budget is not None and github_attempts >= github_query_budget:
                outcomes.append(QueryOutcome("github", query, "skipped_budget"))
                continue

            if source == "github":
                github_attempts += 1
                candidates, outcome = search_github(query, limit, token)
                if outcome.status == "rate_limited":
                    github_blocked = True
            elif source == "npm":
                candidates, outcome = search_npm(query, limit)
            elif source == "huggingface":
                candidates, outcome = search_huggingface(query, limit)
            else:
                candidates = []
                outcome = QueryOutcome(source, query, "unsupported_source", error="unsupported source")

            all_candidates.extend(candidates)
            outcomes.append(outcome)

    unique = dedupe(all_candidates)
    kept = [candidate for candidate in unique if candidate.hygiene_status == "kept"]
    filtered = [candidate for candidate in unique if candidate.hygiene_status != "kept"]
    source_summary = summarize_sources(sources, query_map, outcomes)
    coverage_complete = bool(sources) and all(source_summary[source]["coverage_complete"] for source in sources)
    required_coverage_complete = all(
        source in source_summary and source_summary[source]["coverage_complete"]
        for source in required_sources
    )
    claim_allowed = coverage_complete if not required_sources else required_coverage_complete
    incomplete_required_sources = [
        source for source in required_sources
        if source not in source_summary or not source_summary[source]["coverage_complete"]
    ]
    failures = [
        asdict(outcome) for outcome in outcomes
        if outcome.status not in SUCCESS_STATUSES
    ]

    return {
        "queries": shared_queries,
        "source_queries": source_queries,
        "sources": sources,
        "requested_sources": sources,
        "successful_sources": [source for source in sources if source_summary[source]["completed"] > 0],
        "incomplete_sources": [source for source in sources if not source_summary[source]["coverage_complete"]],
        "source_summary": source_summary,
        "coverage_complete": coverage_complete,
        "required_sources": required_sources,
        "claim_allowed": claim_allowed,
        "incomplete_required_sources": incomplete_required_sources,
        "github_auth": "token" if token else "anonymous",
        "candidate_count": len(unique),
        "kept_count": len(kept),
        "filtered_noise_count": len(filtered),
        "failures": failures,
        "query_outcomes": [asdict(outcome) for outcome in outcomes],
        "candidates": [asdict(candidate) for candidate in kept],
        "filtered_noise": [asdict(candidate) for candidate in filtered[:25]],
    }


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


def to_markdown(result: dict[str, Any]) -> str:
    lines = ["# reuse-scout search results", ""]
    lines.append(f"Requested sources: {', '.join(result['requested_sources']) or 'none'}")
    lines.append(f"Sources with completed queries: {', '.join(result['successful_sources']) or 'none'}")
    lines.append(f"Incomplete sources: {', '.join(result['incomplete_sources']) or 'none'}")
    lines.append(f"Coverage complete: {yes_no(result['coverage_complete'])}")
    lines.append(f"Negative claim allowed: {yes_no(result['claim_allowed'])}")
    if "github" in result["requested_sources"]:
        lines.append(f"GitHub auth: {result['github_auth']}")
    lines.append(
        f"Candidates: {result['kept_count']} kept, "
        f"{result['filtered_noise_count']} filtered noise, {len(result['failures'])} incomplete queries"
    )

    lines.extend(["", "## Source coverage", ""])
    lines.append("| Source | Assigned | Completed | Results | Empty | Failed | Skipped | Complete |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---|")
    for source, summary in result["source_summary"].items():
        lines.append(
            f"| {source} | {summary['assigned']} | {summary['completed']} | "
            f"{summary['with_results']} | {summary['empty']} | {summary['failed']} | "
            f"{summary['skipped']} | {yes_no(summary['coverage_complete'])} |"
        )

    if result["failures"]:
        lines.extend(["", "## Incomplete queries"])
        for failure in result["failures"]:
            detail = failure.get("error") or "not executed"
            lines.append(f"- {failure['source']} / {failure['query']} / {failure['status']}: {detail}")

    lines.extend(["", "## Kept candidates", ""])
    lines.append("| Name | Source | Type | Signal | Description | URL |")
    lines.append("|---|---|---|---:|---|---|")
    for candidate in result["candidates"]:
        signal = candidate.get("stars") if candidate.get("stars") is not None else candidate.get("package_downloads_weekly") or ""
        desc = (candidate.get("description") or "").replace("|", "\\|")[:180]
        lines.append(
            f"| {candidate['name']} | {candidate['source']} | {candidate['candidate_type']} | "
            f"{signal} | {desc} | {candidate['url']} |"
        )
    if result["filtered_noise"]:
        lines.extend(["", "## Filtered noise sample"])
        for candidate in result["filtered_noise"][:10]:
            note = "; ".join(candidate.get("hygiene_notes") or [])
            lines.append(f"- {candidate['name']} ({candidate['source']}): {note}")
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search public sources for reuse-scout candidate evidence.")
    parser.add_argument("--query", action="append", help="Shared search query. Repeat for multiple queries.")
    parser.add_argument("--github-query", action="append", help="Priority GitHub-only query. Runs before shared queries.")
    parser.add_argument("--npm-query", action="append", help="Priority npm-only query. Runs before shared queries.")
    parser.add_argument("--huggingface-query", action="append", help="Priority Hugging Face-only query. Runs before shared queries.")
    parser.add_argument("--source", action="append", choices=["github", "npm", "huggingface"], help="Source to search.")
    parser.add_argument("--required-source", action="append", choices=["github", "npm", "huggingface"], help="Source that must complete before a negative finding is allowed.")
    parser.add_argument("--github-query-budget", type=int, help="Maximum GitHub queries for this run. Remaining queries are marked skipped_budget.")
    parser.add_argument("--limit", type=int, default=5, help="Max results per query per source.")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    args = parser.parse_args(argv)
    if not any([args.query, args.github_query, args.npm_query, args.huggingface_query]):
        parser.error("provide at least one query")
    if args.github_query_budget is not None and args.github_query_budget < 1:
        parser.error("--github-query-budget must be at least 1")
    return args


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    args = parse_args(argv)
    source_queries = {
        "github": args.github_query or [],
        "npm": args.npm_query or [],
        "huggingface": args.huggingface_query or [],
    }
    if args.source:
        sources = dedupe_strings(args.source)
    elif args.query:
        sources = ["github", "npm", "huggingface"]
    else:
        sources = [source for source, queries in source_queries.items() if queries]

    result = run_search(
        queries=args.query or [],
        sources=sources,
        limit=max(1, min(args.limit, 25)),
        source_queries=source_queries,
        required_sources=args.required_source,
        github_query_budget=args.github_query_budget,
    )
    if args.format == "markdown":
        sys.stdout.write(to_markdown(result))
    else:
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

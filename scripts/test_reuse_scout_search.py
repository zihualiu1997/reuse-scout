#!/usr/bin/env python3
from __future__ import annotations

import os
import unittest
from unittest.mock import patch

import reuse_scout_search as scout


def outcome(source: str, query: str, status: str) -> scout.QueryOutcome:
    return scout.QueryOutcome(source=source, query=query, status=status)


class SearchStatusTests(unittest.TestCase):
    def test_rate_limit_is_not_treated_as_empty(self) -> None:
        self.assertEqual(
            scout.classify_http_failure(
                403,
                "API rate limit exceeded",
                {"X-RateLimit-Remaining": "0"},
            ),
            "rate_limited",
        )

    @patch.object(scout, "search_github")
    def test_rate_limit_stops_following_github_requests(self, search_github) -> None:
        search_github.side_effect = [
            ([], outcome("github", "first", "empty")),
            ([], outcome("github", "second", "rate_limited")),
        ]

        result = scout.run_search(
            ["first", "second", "third"],
            ["github"],
            5,
            required_sources=["github"],
        )

        self.assertEqual(search_github.call_count, 2)
        self.assertEqual(
            [item["status"] for item in result["query_outcomes"]],
            ["empty", "rate_limited", "skipped_rate_limited"],
        )
        self.assertFalse(result["claim_allowed"])
        self.assertFalse(result["coverage_complete"])

    @patch.object(scout, "search_github")
    def test_successful_empty_search_allows_scoped_negative_finding(self, search_github) -> None:
        search_github.side_effect = lambda query, limit, token: (
            [],
            outcome("github", query, "empty"),
        )

        result = scout.run_search(
            ["codex image editor skill", "claude image editor skill"],
            ["github"],
            5,
            required_sources=["github"],
        )

        self.assertTrue(result["claim_allowed"])
        self.assertTrue(result["coverage_complete"])
        self.assertEqual(result["source_summary"]["github"]["empty"], 2)

    @patch.object(scout, "search_npm")
    @patch.object(scout, "search_github")
    def test_other_sources_do_not_replace_incomplete_required_source(self, search_github, search_npm) -> None:
        search_github.return_value = ([], outcome("github", "skill", "rate_limited"))
        search_npm.return_value = ([], outcome("npm", "skill", "empty"))

        result = scout.run_search(
            ["skill"],
            ["github", "npm"],
            5,
            required_sources=["github"],
        )

        self.assertEqual(result["successful_sources"], ["npm"])
        self.assertFalse(result["claim_allowed"])
        self.assertEqual(result["incomplete_required_sources"], ["github"])

    @patch.object(scout, "search_github")
    def test_source_specific_queries_run_before_shared_queries(self, search_github) -> None:
        calls: list[str] = []

        def fake_search(query: str, limit: int, token: str | None):
            calls.append(query)
            return [], outcome("github", query, "empty")

        search_github.side_effect = fake_search
        scout.run_search(
            ["generic module"],
            ["github"],
            5,
            source_queries={"github": ["exact codex skill"]},
        )

        self.assertEqual(calls, ["exact codex skill", "generic module"])

    @patch.object(scout, "search_github")
    def test_query_budget_marks_unexecuted_queries(self, search_github) -> None:
        search_github.side_effect = lambda query, limit, token: (
            [],
            outcome("github", query, "empty"),
        )

        result = scout.run_search(
            ["one", "two", "three"],
            ["github"],
            5,
            required_sources=["github"],
            github_query_budget=2,
        )

        self.assertEqual(search_github.call_count, 2)
        self.assertEqual(result["query_outcomes"][-1]["status"], "skipped_budget")
        self.assertFalse(result["claim_allowed"])

        markdown = scout.to_markdown(result)
        self.assertIn("Coverage complete: no", markdown)
        self.assertIn("Negative claim allowed: no", markdown)
        self.assertIn("Incomplete sources: github", markdown)

    def test_gh_token_is_supported(self) -> None:
        with patch.dict(os.environ, {"GH_TOKEN": "test-token"}, clear=True):
            self.assertEqual(scout.github_token(), "test-token")


if __name__ == "__main__":
    unittest.main(verbosity=2)

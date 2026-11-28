from __future__ import annotations

import sys
import unittest
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from fetch_profile_metrics import build_profile_data, render_metrics_svg  # noqa: E402


def repository(
    name: str,
    language: str | None,
    pushed_at: str,
    *,
    fork: bool = False,
    private: bool = False,
    stars: int = 0,
) -> dict:
    return {
        "name": name,
        "owner": {"login": "AmDeep"},
        "private": private,
        "fork": fork,
        "language": language,
        "pushed_at": pushed_at,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": pushed_at,
        "html_url": f"https://github.com/AmDeep/{name}",
        "description": f"{name} sample",
        "stargazers_count": stars,
        "forks_count": 0,
        "archived": False,
        "topics": [],
    }


class FetchProfileMetricsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 11, 28, 12, tzinfo=timezone.utc)
        self.projects = [
            {
                "id": "alpha",
                "name": "Alpha",
                "repo": "alpha",
                "url": "https://github.com/AmDeep/alpha",
                "category": "Agent systems",
                "scope": "Test project",
                "summary": "A test repository.",
                "evidence": "A reproducible fixture.",
                "featured": True,
                "color": "#55D6BE",
            }
        ]
        self.repositories = [
            repository("alpha", "Python", "2026-11-27T12:00:00Z", stars=3),
            repository("beta", "TypeScript", "2026-10-15T12:00:00Z", stars=2),
            repository("no-language", None, "2026-03-02T12:00:00Z"),
            repository("forked", "Python", "2026-11-28T11:00:00Z", fork=True),
            repository("private", "Python", "2026-11-28T11:00:00Z", private=True),
        ]

    def test_filters_private_and_forked_repositories_and_counts_windows(self) -> None:
        data = build_profile_data(self.repositories, self.projects, self.now)
        snapshot = data["snapshot"]
        self.assertEqual(snapshot["originalPublicRepositories"], 3)
        self.assertEqual(snapshot["stars"], 5)
        self.assertEqual(snapshot["repositoriesPushed7d"], 1)
        self.assertEqual(snapshot["repositoriesPushed30d"], 1)
        self.assertEqual(snapshot["repositoriesPushed90d"], 2)
        self.assertEqual(snapshot["primaryLanguageCount"], 2)
        self.assertEqual([item["name"] for item in snapshot["languages"]], ["Python", "TypeScript"])

    def test_monthly_series_is_explicitly_latest_push_counts(self) -> None:
        data = build_profile_data(self.repositories, self.projects, self.now)
        monthly = data["snapshot"]["monthlyLatestPushes"]
        self.assertEqual(len(monthly), 12)
        self.assertEqual(monthly[-1]["key"], "2026-11")
        self.assertEqual(monthly[-1]["label"], "Nov")
        self.assertEqual(monthly[-1]["repositories"], 1)
        self.assertIn("not commit volume", data["definitions"]["monthlyActivity"])

    def test_metrics_svg_has_accessible_description_and_current_values(self) -> None:
        data = build_profile_data(self.repositories, self.projects, self.now)
        svg = render_metrics_svg(data)
        root = ET.fromstring(svg)
        self.assertEqual(root.attrib["role"], "img")
        self.assertIsNotNone(root.find("{http://www.w3.org/2000/svg}title"))
        self.assertIsNotNone(root.find("{http://www.w3.org/2000/svg}desc"))
        text = "".join(root.itertext())
        self.assertIn("PUBLIC REPOSITORY PULSE", text)
        self.assertIn("2026-11-28 12:00:00 UTC", text)
        self.assertIn("PUSHED · 30 DAYS", text)
        self.assertIn("prefers-reduced-motion: reduce", svg)

    def test_empty_repository_response_fails_instead_of_fabricating_zeroes(self) -> None:
        with self.assertRaisesRegex(ValueError, "No owned public"):
            build_profile_data([], self.projects, self.now)


if __name__ == "__main__":
    unittest.main()

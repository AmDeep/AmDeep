#!/usr/bin/env python3
"""Fetch public GitHub repository metadata and render the live profile snapshot."""

from __future__ import annotations

import calendar
import html
import json
import os
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

try:
    from .build_profile import ROOT, load_content, render_all
except ImportError:  # direct invocation from GitHub Actions or the command line
    from build_profile import ROOT, load_content, render_all


API_ROOT = "https://api.github.com"
USER_AGENT = "AmDeep-Profile-Metrics/1.0"
DATA_PATH = ROOT / "site" / "src" / "data" / "profile.json"
METRICS_PATH = ROOT / "profile" / "metrics.svg"


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def fetch_public_repositories(
    username: str = "AmDeep", token: str | None = None
) -> list[dict[str, Any]]:
    """Read only public, owned repositories; fail closed on API errors."""
    repositories: list[dict[str, Any]] = []
    page = 1
    while True:
        query = urlencode(
            {
                "type": "owner",
                "per_page": 100,
                "page": page,
                "sort": "pushed",
                "direction": "desc",
            }
        )
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": USER_AGENT,
            "X-GitHub-Api-Version": "2026-03-10",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        request = Request(
            f"{API_ROOT}/users/{username}/repos?{query}", headers=headers
        )
        try:
            with urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            # Never print request headers or environment values.
            raise RuntimeError(
                f"GitHub public-repository request failed on page {page}: "
                f"{type(exc).__name__}"
            ) from None
        if not isinstance(payload, list):
            raise RuntimeError(f"GitHub returned an unexpected response on page {page}.")
        repositories.extend(payload)
        if len(payload) < 100:
            break
        page += 1
    return [
        repo
        for repo in repositories
        if repo.get("private") is False
        and repo.get("fork") is False
        and str(repo.get("owner", {}).get("login", "")).lower() == username.lower()
    ]


def build_profile_data(
    repositories: list[dict[str, Any]],
    projects: list[dict[str, Any]],
    now: datetime | None = None,
) -> dict[str, Any]:
    """Build transparent, time-stamped metrics from repository metadata."""
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if not repositories:
        raise ValueError("No owned public non-fork repositories were returned.")

    public_repos = [
        repo
        for repo in repositories
        if repo.get("private") is False
        and repo.get("fork") is False
        and str(repo.get("owner", {}).get("login", "AmDeep")).lower() == "amdeep"
    ]
    if not public_repos:
        raise ValueError("No eligible public repositories remain after filtering.")

    by_name = {repo.get("name", "").lower(): repo for repo in public_repos}
    featured: list[dict[str, Any]] = []
    for project in projects:
        repo = by_name.get(project["repo"].lower())
        if not repo:
            raise ValueError(
                f"Featured repository {project['repo']} was not in the public result."
            )
        featured.append(
            {
                **project,
                "language": repo.get("language"),
                "stars": int(repo.get("stargazers_count") or 0),
                "forks": int(repo.get("forks_count") or 0),
                "pushedAt": repo.get("pushed_at"),
            }
        )

    repo_rows: list[dict[str, Any]] = []
    language_counts: Counter[str] = Counter()
    pushed_dates: list[tuple[dict[str, Any], datetime]] = []
    for repo in public_repos:
        language = repo.get("language")
        if language:
            language_counts[str(language)] += 1
        pushed_at = parse_timestamp(repo.get("pushed_at"))
        if pushed_at:
            pushed_dates.append((repo, pushed_at))
        repo_rows.append(
            {
                "name": str(repo.get("name") or ""),
                "description": str(repo.get("description") or ""),
                "url": str(repo.get("html_url") or ""),
                "language": language,
                "stars": int(repo.get("stargazers_count") or 0),
                "forks": int(repo.get("forks_count") or 0),
                "pushedAt": repo.get("pushed_at"),
                "createdAt": repo.get("created_at"),
                "updatedAt": repo.get("updated_at"),
                "archived": bool(repo.get("archived")),
                "topics": repo.get("topics") if isinstance(repo.get("topics"), list) else [],
            }
        )
    repo_rows.sort(key=lambda item: item["pushedAt"] or "", reverse=True)

    languages = [
        {"name": name, "repositories": count}
        for name, count in sorted(
            language_counts.items(), key=lambda pair: (-pair[1], pair[0].casefold())
        )[:8]
    ]
    monthly = []
    month_indexes = {}
    for offset in range(11, -1, -1):
        month_number = now.month - offset
        year = now.year + (month_number - 1) // 12
        month = (month_number - 1) % 12 + 1
        key = f"{year:04d}-{month:02d}"
        month_indexes[key] = len(monthly)
        monthly.append(
            {"key": key, "label": calendar.month_abbr[month], "repositories": 0}
        )
    for _repo, pushed_at in pushed_dates:
        index = month_indexes.get(pushed_at.strftime("%Y-%m"))
        if index is not None:
            monthly[index]["repositories"] += 1

    def pushed_within(days: int) -> int:
        threshold = now - timedelta(days=days)
        return sum(threshold <= pushed_at <= now for _, pushed_at in pushed_dates)

    data = {
        "schemaVersion": 1,
        "username": "AmDeep",
        "generatedAt": now.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "source": "GitHub public repository metadata",
        "scope": "Owned public repositories; forks and private repositories excluded.",
        "definitions": {
            "recentPushes": "Count of eligible repositories whose latest push_at is within the selected window.",
            "monthlyActivity": "Count of eligible repositories grouped by the month of their latest push_at; not commit volume.",
            "languages": "GitHub primary language, counted once per repository.",
        },
        "snapshot": {
            "originalPublicRepositories": len(public_repos),
            "stars": sum(int(repo.get("stargazers_count") or 0) for repo in public_repos),
            "forks": sum(int(repo.get("forks_count") or 0) for repo in public_repos),
            "primaryLanguageCount": len(language_counts),
            "repositoriesPushed7d": pushed_within(7),
            "repositoriesPushed30d": pushed_within(30),
            "repositoriesPushed90d": pushed_within(90),
            "lastPushAt": repo_rows[0]["pushedAt"] if repo_rows else None,
            "languages": languages,
            "monthlyLatestPushes": monthly,
        },
        "projects": featured,
        "repositories": repo_rows,
    }
    return data


def render_metrics_svg(data: dict[str, Any]) -> str:
    snapshot = data["snapshot"]
    metrics = [
        ("PUBLIC PROJECTS", str(snapshot["originalPublicRepositories"])),
        ("TOTAL STARS", str(snapshot["stars"])),
        ("PRIMARY LANGUAGES", str(snapshot["primaryLanguageCount"])),
        ("PUSHED · 30 DAYS", str(snapshot["repositoriesPushed30d"])),
    ]
    card_width = 250
    cards = []
    for index, (label, value) in enumerate(metrics):
        x = 40 + index * 280
        cards.append(
            f'<g><rect x="{x}" y="63" width="{card_width}" height="88" rx="14" fill="#172438" stroke="#2B3B53"/>'
            f'<text x="{x + 18}" y="91" fill="#A9B8CC" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="11" font-weight="700" letter-spacing="1">{html.escape(label)}</text>'
            f'<text x="{x + 18}" y="132" fill="#F3F6FB" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="32" font-weight="700">{html.escape(value)}</text></g>'
        )

    monthly = snapshot["monthlyLatestPushes"]
    chart_left, chart_top, chart_height = 64, 209, 86
    chart_width, gap = 1072, 21
    bar_width = (chart_width - gap * (len(monthly) - 1)) / len(monthly)
    max_value = max((int(item["repositories"]) for item in monthly), default=0) or 1
    bars = []
    for index, item in enumerate(monthly):
        value = int(item["repositories"])
        height = max(4, chart_height * value / max_value) if value else 4
        x = chart_left + index * (bar_width + gap)
        y = chart_top + chart_height - height
        color = "#55D6BE" if index == len(monthly) - 1 else "#476780"
        bars.append(
            f'<g><rect class="bar" x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{height:.1f}" rx="4" fill="{color}"/>'
            f'<text x="{x + bar_width / 2:.1f}" y="{chart_top + chart_height + 20}" fill="#A9B8CC" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="10">{html.escape(item["label"])}</text></g>'
        )

    generated = html.escape(data["generatedAt"].replace("T", " ").replace("Z", " UTC"))
    body = "".join(cards) + "".join(bars)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="330" viewBox="0 0 1200 330" role="img" aria-labelledby="title description">
  <title id="title">Live public repository metrics for AmDeep</title>
  <desc id="description">Generated {generated}. Counts include owned public non-fork repositories. The bar chart groups repositories by the month of their latest push, not by commit count.</desc>
  <style>
    @media (prefers-reduced-motion: no-preference) {{ .bar {{ transform-box:fill-box; transform-origin:bottom; animation:grow .65s cubic-bezier(.2,.8,.2,1) both; }} }}
    @media (prefers-reduced-motion: reduce) {{ .bar {{ animation:none!important; }} }}
    @keyframes grow {{ from {{ transform:scaleY(.08); opacity:.35; }} to {{ transform:scaleY(1); opacity:1; }} }}
  </style>
  <rect width="1200" height="330" rx="20" fill="#101826"/>
  <text x="40" y="36" fill="#F3F6FB" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="15" font-weight="700">PUBLIC REPOSITORY PULSE</text>
  <text x="1160" y="36" fill="#A9B8CC" text-anchor="end" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="11">Updated {generated}</text>
  {body}
  <text x="64" y="315" fill="#8295AD" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="10">Repositories grouped by month of their latest push_at · not a commit-volume chart</text>
</svg>
"""


def write_outputs(data: dict[str, Any]) -> list[str]:
    version = "".join(
        character
        for character in data["generatedAt"]
        if character.isdigit() or character in "TZ"
    )
    outputs = render_all(load_content(), metrics_version=version)
    outputs[str(DATA_PATH.relative_to(ROOT))] = json.dumps(
        data, ensure_ascii=False, indent=2
    ) + "\n"
    outputs[str(METRICS_PATH.relative_to(ROOT))] = render_metrics_svg(data)
    written = []
    for relative, text in outputs.items():
        target = ROOT / relative
        if target.exists() and target.read_text(encoding="utf-8") == text:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        written.append(relative)
    return written


def set_github_output(name: str, value: str) -> None:
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with Path(output_file).open("a", encoding="utf-8") as handle:
            handle.write(f"{name}={value}\n")


def main() -> int:
    username = os.environ.get("PROFILE_USERNAME", "AmDeep")
    token = os.environ.get("GITHUB_TOKEN")
    try:
        content = load_content()
        repositories = fetch_public_repositories(username, token)
        data = build_profile_data(repositories, content["projects"])
        if DATA_PATH.exists():
            existing = json.loads(DATA_PATH.read_text(encoding="utf-8"))
            existing_comparable = dict(existing)
            new_comparable = dict(data)
            existing_comparable.pop("generatedAt", None)
            new_comparable.pop("generatedAt", None)
            if existing_comparable == new_comparable:
                # Keep a stable snapshot timestamp and cache key when nothing changed.
                data["generatedAt"] = existing.get("generatedAt", data["generatedAt"])
        written = write_outputs(data)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"Profile refresh failed: {exc}", file=sys.stderr)
        return 1
    changed = bool(written)
    set_github_output("changed", str(changed).lower())
    if changed:
        print(
            f"Updated public metrics for {data['snapshot']['originalPublicRepositories']} "
            f"repositories; wrote {len(written)} files."
        )
    else:
        print("Public repository metadata and generated profile files are unchanged.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

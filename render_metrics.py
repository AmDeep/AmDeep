"""Render a compact SVG snapshot from public GitHub repository metrics."""

from __future__ import annotations

from datetime import date
from html import escape
import json
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def validate_metrics(metrics: Any) -> dict[str, Any]:
    if not isinstance(metrics, dict):
        raise ValueError("profile metrics must be a JSON object")

    for key in ("repos", "stars", "languageCount"):
        value = metrics.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{key} must be a non-negative integer")

    updated = metrics.get("updated")
    if not isinstance(updated, str):
        raise ValueError("updated must be an ISO date")
    try:
        date.fromisoformat(updated)
    except ValueError as exc:
        raise ValueError("updated must be an ISO date") from exc

    languages = metrics.get("languages")
    if not isinstance(languages, list) or len(languages) > 5:
        raise ValueError("languages must be a list of at most five entries")
    for language in languages:
        if not isinstance(language, dict):
            raise ValueError("each language entry must be an object")
        name = language.get("name")
        count = language.get("count")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("language names must be non-empty strings")
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ValueError("language counts must be non-negative integers")

    return metrics


def render_svg(metrics: Any) -> str:
    data = validate_metrics(metrics)
    cards = (
        ("OWNED PUBLIC REPOS", str(data["repos"])),
        ("PORTFOLIO STARS", str(data["stars"])),
        ("PRIMARY LANGUAGES", str(data["languageCount"])),
        ("UPDATED UTC", data["updated"]),
    )
    card_markup = []
    for index, (label, value) in enumerate(cards):
        x = 36 + index * 285
        value_size = 24 if label == "UPDATED UTC" else 38
        card_markup.append(
            f'<g><rect x="{x}" y="91" width="264" height="88" rx="14" '
            'fill="#142b42" stroke="#29465e"/>'
            f'<text x="{x + 18}" y="120" fill="#8eabc2" '
            'font-family="Inter,Segoe UI,Arial,sans-serif" font-size="11" '
            'font-weight="700" letter-spacing="1.1">'
            f"{escape(label)}</text>"
            f'<text x="{x + 18}" y="158" fill="#f1f7ff" '
            'font-family="Inter,Segoe UI,Arial,sans-serif" '
            f'font-size="{value_size}" font-weight="700">{escape(value)}</text></g>'
        )

    language_markup = []
    for index, language in enumerate(data["languages"]):
        x = 36 + index * 225
        name = escape(language["name"])
        count = language["count"]
        language_markup.append(
            f'<g><rect x="{x}" y="220" width="208" height="34" rx="17" '
            'fill="#12253a" stroke="#29465e"/>'
            f'<text x="{x + 14}" y="242" fill="#d2e3f2" '
            'font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12">'
            f"{name}</text>"
            f'<text x="{x + 192}" y="242" fill="#7ee7d6" text-anchor="end" '
            'font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12" '
            f'font-weight="700">{count}</text></g>'
        )

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="280" '
        'viewBox="0 0 1200 280" role="img" '
        'aria-labelledby="title description">'
        '<title id="title">AmDeep public GitHub snapshot</title>'
        '<desc id="description">Public repository, star, and primary language '
        f'metrics updated {escape(data["updated"])}.</desc>'
        '<defs><linearGradient id="background" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#0b1729"/>'
        '<stop offset="1" stop-color="#102c3c"/>'
        '</linearGradient></defs>'
        '<rect width="1200" height="280" rx="20" fill="url(#background)"/>'
        '<text x="36" y="42" fill="#f1f7ff" '
        'font-family="Inter,Segoe UI,Arial,sans-serif" font-size="19" '
        'font-weight="700">Public portfolio snapshot</text>'
        '<text x="36" y="64" fill="#91abc0" '
        'font-family="Inter,Segoe UI,Arial,sans-serif" font-size="12">'
        'Owned, non-fork public repositories · languages counted by repository'
        '</text>'
        + "".join(card_markup)
        + '<text x="36" y="203" fill="#91abc0" '
        'font-family="Inter,Segoe UI,Arial,sans-serif" font-size="11" '
        'font-weight="700" letter-spacing="1">TOP REPOSITORY LANGUAGES</text>'
        + "".join(language_markup)
        + "</svg>"
    )


def main() -> None:
    raw_metrics = os.environ.get("PROFILE_STATS")
    if raw_metrics is None:
        raise SystemExit("PROFILE_STATS environment variable is required")
    try:
        metrics = json.loads(raw_metrics)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"PROFILE_STATS is not valid JSON: {exc}") from exc

    svg = render_svg(metrics)
    target = ROOT / "assets" / "metrics.svg"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(svg + "\n", encoding="utf-8")
    print(f"Rendered {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

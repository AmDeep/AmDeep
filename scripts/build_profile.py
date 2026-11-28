#!/usr/bin/env python3
"""Generate the profile README and self-hosted SVGs from profile-content.json.

This intentionally uses only the Python standard library: the profile is static
Markdown and SVG, so a framework or third-party image service would add upkeep
without improving what GitHub can render.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTENT_PATH = ROOT / "profile-content.json"
RAW_BASE = "https://raw.githubusercontent.com/AmDeep/AmDeep/main/profile"
PAGES_URL = "https://amdeep.github.io/AmDeep/"
BACKGROUND = "#101826"
PANEL = "#172438"
PANEL_ALT = "#1D2C42"
TEXT = "#F3F6FB"
MUTED = "#A9B8CC"
GRID = "#2B3B53"
ACCENT = "#55D6BE"


def esc(value: Any) -> str:
    """Escape text and attributes for safe SVG/HTML output."""
    return html.escape(str(value), quote=True)


def load_content(path: Path = CONTENT_PATH) -> dict[str, Any]:
    content = json.loads(path.read_text(encoding="utf-8"))
    validate_content(content)
    return content


def validate_content(content: dict[str, Any]) -> None:
    required = ("name", "username", "headline", "subheadline", "intro", "projects")
    missing = [key for key in required if not content.get(key)]
    if missing:
        raise ValueError(f"Missing required profile fields: {', '.join(missing)}")
    projects = content["projects"]
    if not projects:
        raise ValueError("At least one featured project is required.")
    ids: set[str] = set()
    repos: set[str] = set()
    for project in projects:
        project_id = project.get("id", "")
        if not re.fullmatch(r"[a-z0-9-]+", project_id):
            raise ValueError(f"Invalid project id: {project_id!r}")
        if project_id in ids or project.get("repo") in repos:
            raise ValueError(f"Duplicate project id or repository: {project_id}")
        if not project.get("url", "").startswith(
            f"https://github.com/{content['username']}/"
        ):
            raise ValueError(f"Project URL is outside the profile owner: {project_id}")
        for key in ("name", "scope", "summary", "evidence"):
            if not project.get(key):
                raise ValueError(f"Project {project_id} is missing {key}.")
        ids.add(project_id)
        repos.add(project["repo"])
    if not any(project.get("featured") for project in projects):
        raise ValueError("At least one project must be featured.")


def svg_shell(title: str, description: str, body: str, width: int, height: int) -> str:
    title_id = "svg-title"
    desc_id = "svg-description"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="{title_id} {desc_id}">
  <title id="{title_id}">{esc(title)}</title>
  <desc id="{desc_id}">{esc(description)}</desc>
  <style>
    .sans{{font-family:Inter,'Segoe UI',Arial,sans-serif}}
    .mono{{font-family:'SFMono-Regular',Consolas,monospace}}
    .signal{{opacity:.85}}
    .pulse{{opacity:.82}}
    .card-accent{{opacity:.9}}
  </style>
  {body}
</svg>
"""


def render_hero(content: dict[str, Any]) -> str:
    body = f"""
  <defs>
    <linearGradient id="wash" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#17283E"/>
      <stop offset="1" stop-color="#102A35"/>
    </linearGradient>
    <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M32 0H0V32" fill="none" stroke="{GRID}" stroke-opacity=".45"/>
    </pattern>
  </defs>
  <rect width="1200" height="340" rx="24" fill="url(#wash)"/>
  <rect width="1200" height="340" rx="24" fill="url(#grid)"/>
  <circle cx="1050" cy="82" r="120" fill="#55D6BE" opacity=".06"/>
  <circle cx="1002" cy="258" r="150" fill="#82A8FF" opacity=".05"/>
  <text x="68" y="92" class="mono" font-size="15" fill="{ACCENT}" letter-spacing="2">AMDEEP · TORONTO</text>
  <text x="68" y="158" class="sans" font-size="52" font-weight="750" fill="{TEXT}">{esc(content['name'])}</text>
  <text x="70" y="202" class="sans" font-size="24" font-weight="650" fill="{TEXT}">{esc(content['headline'])}</text>
  <text x="70" y="238" class="sans" font-size="18" fill="{MUTED}">{esc(content['subheadline'])}</text>
  <text x="70" y="280" class="sans" font-size="16" fill="{MUTED}">Inspectable systems · explicit boundaries · reproducible evidence</text>
  <path d="M714 202H1098" stroke="#45617A" stroke-width="3" stroke-linecap="round"/>
  <path d="M744 202H1030" stroke="{ACCENT}" stroke-width="2" stroke-dasharray="5 12" opacity=".7"/>
  <circle cx="742" cy="202" r="11" fill="{ACCENT}" opacity=".18"/>
  <circle class="signal" cx="742" cy="202" r="6" fill="{ACCENT}"/>
  <g class="sans" text-anchor="middle">
    <rect x="708" y="132" width="124" height="42" rx="12" fill="{PANEL}" stroke="{GRID}"/>
    <text x="770" y="158" font-size="14" fill="{TEXT}">model output</text>
    <rect x="850" y="132" width="124" height="42" rx="12" fill="{PANEL}" stroke="{GRID}"/>
    <text x="912" y="158" font-size="14" fill="{TEXT}">validation</text>
    <rect x="992" y="132" width="124" height="42" rx="12" fill="{PANEL}" stroke="{GRID}"/>
    <text x="1054" y="158" font-size="14" fill="{TEXT}">bounded action</text>
  </g>
  <circle class="pulse" cx="770" cy="202" r="4" fill="{ACCENT}"/>
  <circle class="pulse" cx="912" cy="202" r="4" fill="#82A8FF"/>
  <circle class="pulse" cx="1054" cy="202" r="4" fill="#FFB86B"/>
  <text x="912" y="248" class="mono" font-size="12" text-anchor="middle" fill="{MUTED}">A recurring pattern in the selected projects</text>
"""
    return svg_shell(
        f"{content['name']} — {content['headline']}",
        "A visual summary of applied AI work across retrieval, agent systems, inference, and robotics, with validation before action.",
        body,
        1200,
        340,
    )


def render_evidence(content: dict[str, Any]) -> str:
    metrics = content["evidence_metrics"]
    width, height = 1200, 270
    card_width, gap, left = 344, 24, 56
    cards = []
    for index, metric in enumerate(metrics):
        x = left + index * (card_width + gap)
        cards.append(
            f"""
  <g>
    <rect x="{x}" y="64" width="{card_width}" height="152" rx="18" fill="{PANEL}" stroke="{GRID}"/>
    <rect class="card-accent" x="{x}" y="64" width="5" height="152" rx="3" fill="{ACCENT}"/>
    <text x="{x + 24}" y="104" class="mono" font-size="12" fill="{MUTED}" letter-spacing="1">{esc(metric['label'])}</text>
    <text x="{x + 24}" y="166" class="sans" font-size="48" font-weight="750" fill="{TEXT}">{esc(metric['value'])}</text>
    <text x="{x + 24}" y="194" class="sans" font-size="14" fill="{MUTED}">{esc(metric['note'])}</text>
  </g>"""
        )
    body = f"""
  <rect width="{width}" height="{height}" rx="22" fill="{BACKGROUND}"/>
  <text x="56" y="38" class="sans" font-size="16" font-weight="700" fill="{TEXT}">PROJECT SCOPE, NOT VANITY METRICS</text>
  {''.join(cards)}
  <text x="56" y="248" class="sans" font-size="12" fill="{MUTED}">Counts describe the documented contents of these repositories, not deployment volume or user impact.</text>
"""
    return svg_shell(
        "Project scope evidence",
        "Documented project counts: 12 agent labs, 15 retrieval projects, and a 12-stage inference portfolio. These are repository scope counts, not deployment metrics.",
        body,
        width,
        height,
    )


def render_approach(content: dict[str, Any]) -> str:
    nodes = [
        ("01", "Context", "retrieval · state · constraints", "#82A8FF"),
        ("02", "Proposal", "structured model output", "#D69BFF"),
        ("03", "Validation", "schema · policy · limits", "#55D6BE"),
        ("04", "Evidence", "tests · replay · measured results", "#FFB86B"),
    ]
    boxes = []
    for index, (number, title, subtitle, color) in enumerate(nodes):
        x = 50 + index * 286
        boxes.append(
            f"""
  <g>
    <rect x="{x}" y="80" width="246" height="124" rx="16" fill="{PANEL}" stroke="{GRID}"/>
    <text x="{x + 20}" y="110" class="mono" font-size="12" fill="{color}">{number}</text>
    <text x="{x + 20}" y="146" class="sans" font-size="22" font-weight="700" fill="{TEXT}">{esc(title)}</text>
    <text x="{x + 20}" y="176" class="sans" font-size="13" fill="{MUTED}">{esc(subtitle)}</text>
  </g>"""
        )
        if index < len(nodes) - 1:
            boxes.append(
                f'<path d="M{x + 250} 142H{x + 278}" stroke="{color}" stroke-width="2" marker-end="url(#arrow)"/>'
            )
    body = f"""
  <defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0 0L8 4L0 8" fill="none" stroke="{ACCENT}" stroke-width="1.5"/></marker></defs>
  <rect width="1200" height="270" rx="22" fill="{BACKGROUND}"/>
  <text x="50" y="42" class="sans" font-size="16" font-weight="700" fill="{TEXT}">HOW I DESIGN SYSTEMS</text>
  <text x="50" y="62" class="sans" font-size="12" fill="{MUTED}">A pattern visible across the selected agent, retrieval, inference, and robotics work.</text>
  {''.join(boxes)}
  <text x="50" y="242" class="mono" font-size="12" fill="{MUTED}">Model output is a proposal; deterministic checks decide what may proceed.</text>
"""
    return svg_shell(
        "Engineering approach",
        "A four-stage pattern across selected repositories: gather context, produce a structured proposal, validate it, and verify behavior with tests or replay.",
        body,
        1200,
        270,
    )


def render_project_card(project: dict[str, Any]) -> str:
    body = f"""
  <defs><linearGradient id="card" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{PANEL}"/><stop offset="1" stop-color="{BACKGROUND}"/></linearGradient></defs>
  <rect width="1100" height="220" rx="20" fill="url(#card)" stroke="{GRID}"/>
  <rect x="0" y="0" width="7" height="220" rx="4" fill="{esc(project['color'])}"/>
  <text x="36" y="47" class="mono" font-size="13" fill="{esc(project['color'])}" letter-spacing="1">{esc(project['scope'].upper())}</text>
  <text x="36" y="91" class="sans" font-size="29" font-weight="720" fill="{TEXT}">{esc(project['name'])}</text>
  <text x="36" y="130" class="sans" font-size="16" fill="{MUTED}">{esc(project['summary'])}</text>
  <text x="36" y="161" class="sans" font-size="14" fill="{TEXT}">{esc(project['evidence'])}</text>
  <text x="36" y="196" class="mono" font-size="12" fill="#8395AD">github.com/AmDeep/{esc(project['repo'])}</text>
  <circle class="pulse" cx="1044" cy="44" r="8" fill="{esc(project['color'])}" opacity=".8"/>
"""
    return svg_shell(
        project["name"],
        f"{project['scope']}. {project['summary']} Evidence: {project['evidence']}",
        body,
        1100,
        220,
    )


def html_link(url: str, label: str) -> str:
    return f'<a href="{esc(url)}">{esc(label)}</a>'


def readme_project_cell(project: dict[str, Any]) -> str:
    image = f"{RAW_BASE}/project-{project['id']}.svg"
    return (
        '<td width="50%" valign="top">'
        f'<a href="{esc(project["url"])}"><img src="{image}" alt="{esc(project["name"])}: {esc(project["scope"])}. {esc(project["summary"])}" width="100%"/></a>'
        f'<p><strong>{html_link(project["url"], project["name"])}</strong><br/>'
        f'{esc(project["summary"])}<br/><em>Evidence:</em> {esc(project["evidence"])}</p>'
        "</td>"
    )


def render_readme(content: dict[str, Any], metrics_version: str = "bootstrap") -> str:
    featured = [project for project in content["projects"] if project.get("featured")]
    supporting = [project for project in content["projects"] if not project.get("featured")]
    rows = []
    for start in range(0, len(featured), 2):
        pair = featured[start : start + 2]
        cells = [readme_project_cell(project) for project in pair]
        if len(cells) == 1:
            cells.append("<td width=\"50%\"></td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    featured_table = "<table>\n" + "\n".join(rows) + "\n</table>"
    supporting_block = ""
    if supporting:
        cards = "\n\n".join(
            f'<a href="{esc(project["url"])}"><img src="{RAW_BASE}/project-{project["id"]}.svg" alt="{esc(project["name"])}: {esc(project["scope"])}. {esc(project["summary"])}" width="100%"/></a>\n\n'
            f'**{html_link(project["url"], project["name"])}** — {esc(project["summary"])} '
            f'**Evidence:** {esc(project["evidence"])}'
            for project in supporting
        )
        supporting_block = (
            "\n<details>\n"
            "<summary>More robotics and edge projects</summary>\n\n"
            f"{cards}\n"
            "</details>\n"
        )
    links = " · ".join(html_link(link["url"], link["label"]) for link in content["links"])
    principles = "\n".join(f"- {esc(item)}" for item in content["principles"])
    metrics_url = f"{RAW_BASE}/metrics.svg?v={esc(metrics_version)}"
    return f"""# {esc(content['name'])}

<p align="center"><img src="{RAW_BASE}/hero.svg" alt="{esc(content['name'])}, {esc(content['headline'])} focused on retrieval, agents, inference, and robotics in {esc(content['location'])}." width="100%"/></p>

{esc(content['intro'])}

**{esc(content['location'])} · {esc(content['subheadline'])}**

{links}

## Selected work

{featured_table}
{supporting_block}
<p align="center"><img src="{RAW_BASE}/evidence.svg" alt="Documented portfolio scope: 12 agent labs, 15 retrieval projects, and a 12-stage inference portfolio; these are repository scope counts, not deployment metrics." width="100%"/></p>

## Live repository signals

<p align="center"><a href="{PAGES_URL}"><strong>Open the interactive portfolio dashboard →</strong></a></p>

<p align="center"><img src="{metrics_url}" alt="Dynamic snapshot of owned public repositories, stars, primary languages, and repositories whose latest push was within 30 days." width="100%"/></p>

<sub>Metrics cover owned public non-fork repositories. The monthly chart counts repositories by their latest push date, not commit volume.</sub>

## How I work

<p align="center"><img src="{RAW_BASE}/approach.svg" alt="Engineering approach: gather context, produce a structured proposal, validate it, then verify with tests or replay." width="100%"/></p>

{principles}

## Areas of focus

**Applied AI:** agent systems · retrieval-augmented generation · inference and serving<br/>
**Robotics and edge:** ROS 2 · model-to-control boundaries · edge vision · offline replay

The repositories are portfolio projects and reference implementations. Their READMEs describe setup, tests, assumptions, and limitations; no live deployment or business-impact claim is implied.

## Looking for

{esc(content['open_to'])}

---

<sub>Project visuals are generated from `profile-content.json`; live metrics come from public GitHub repository metadata. No third-party stats widgets or tracking badges.</sub>
"""


def render_all(
    content: dict[str, Any], metrics_version: str | None = None
) -> dict[str, str]:
    validate_content(content)
    if metrics_version is None:
        data_path = ROOT / "site" / "src" / "data" / "profile.json"
        if data_path.exists():
            try:
                data = json.loads(data_path.read_text(encoding="utf-8"))
                metrics_version = re.sub(r"[^0-9TZ]", "", data.get("generatedAt", ""))
            except (OSError, json.JSONDecodeError):
                metrics_version = ""
        metrics_version = metrics_version or "bootstrap"
    outputs = {
        "README.md": render_readme(content, metrics_version),
        "profile/hero.svg": render_hero(content),
        "profile/evidence.svg": render_evidence(content),
        "profile/approach.svg": render_approach(content),
    }
    for project in content["projects"]:
        outputs[f"profile/project-{project['id']}.svg"] = render_project_card(project)
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if generated README or SVGs differ from the checked-in versions",
    )
    args = parser.parse_args()
    try:
        outputs = render_all(load_content())
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Profile generation failed: {exc}", file=sys.stderr)
        return 1
    stale = []
    for relative_path, text in outputs.items():
        target = ROOT / relative_path
        if args.check:
            if not target.exists() or target.read_text(encoding="utf-8") != text:
                stale.append(relative_path)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
    if stale:
        print("Generated files are out of date: " + ", ".join(stale), file=sys.stderr)
        print("Run: python scripts/build_profile.py", file=sys.stderr)
        return 1
    if args.check:
        print(f"Profile output is current ({len(outputs)} generated files checked).")
    else:
        print(f"Generated {len(outputs)} profile files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

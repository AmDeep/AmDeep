"""Generate the profile's self-hosted SVGs from public GitHub data.

Outputs (in assets/): metrics.svg, card-<repo>.svg for each featured repo, marquee.svg.
Standard library only. Set GITHUB_TOKEN to avoid API rate limits.
Language bars count each repository's primary language, not lines of code.
"""
import html
import json
import os
import textwrap
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone

USER = os.environ.get("PROFILE_USER", "AmDeep")
OUT = os.environ.get("ASSETS_DIR", "assets")

# repo -> fallback description (used when the repo has no description of its own)
FEATURED = {
    "AIAgents": "Runnable reference patterns for reliable agent systems.",
    "RAGSystemLabs": "Hands-on labs for retrieval-augmented generation systems.",
    "inference-serving-portfolio": "Reproducible inference experiments, serving patterns, and benchmark evidence.",
    "ros2-vllm-navigation-bridge": "A bounded navigation bridge with explicit ROS 2 contracts and local obstacle checks.",
    "manipulation-vllm-safety-gateway": "Validation and approval boundaries for robot manipulation commands.",
    "edge-vision-vllm-inspector": "Computer-vision and inference integration patterns for edge deployment.",
}
TICKER = ["Python", "PyTorch", "vLLM", "LangGraph", "RAG", "ROS 2", "OpenCV", "ONNX Runtime",
          "TensorRT", "Triton", "MQTT", "Docker", "AWS", "Azure", "C++", "TypeScript", "SQL"]

BG, PANEL, LINE = "#0E1621", "#16263A", "#2C4058"
INK, SOFT, MUTE, TEAL, AMBER = "#E8EEF4", "#B8C7D6", "#8FA3B8", "#5CC8C0", "#FFB347"
SANS = "font-family:'Segoe UI','Helvetica Neue',Arial,system-ui,sans-serif"
MONO = "font-family:'JetBrains Mono',Consolas,ui-monospace,monospace"
esc = html.escape


def api(path):
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-assets"},
    )
    if os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {os.environ['GITHUB_TOKEN']}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def all_repos():
    repos, page = [], 1
    while True:
        batch = api(f"/users/{USER}/repos?per_page=100&type=owner&page={page}")
        repos += batch
        if len(batch) < 100:
            return repos
        page += 1


def write(name, body):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)


def metrics(repos):
    repos = [r for r in repos if not r["fork"] and not r["private"]]
    stars = sum(r["stargazers_count"] for r in repos)
    langs = Counter(r["language"] for r in repos if r["language"])
    top = langs.most_common(6)
    biggest = max((c for _, c in top), default=1)
    latest = max((r["pushed_at"] for r in repos), default="n/a")[:10]
    stats = [(str(len(repos)), "public repositories"), (str(stars), "stars received"),
             (str(len(langs)), "primary languages"), (latest, "latest push")]
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 320" role="img" aria-label="Public GitHub snapshot">',
         f'<style>.bar{{transform-box:fill-box;transform-origin:left;animation:grow 1.2s ease-out both}}'
         '@keyframes grow{from{transform:scaleX(0)}}@media (prefers-reduced-motion:reduce){.bar{animation:none}}</style>',
         f'<rect width="1200" height="320" fill="{BG}"/>',
         f'<text x="60" y="60" font-size="20" font-weight="600" fill="{SOFT}" style="{SANS}">Public, non-fork repositories by {esc(USER)}</text>']
    for i, (v, label) in enumerate(stats):
        x = 60 + i * 150
        p.append(f'<text x="{x}" y="120" font-size="{40 if i < 3 else 24}" font-weight="700" fill="{INK}" style="{SANS}">{esc(v)}</text>')
        p.append(f'<text x="{x}" y="148" font-size="14" fill="{MUTE}" style="{SANS}">{esc(label)}</text>')
    for i, (lang, n) in enumerate(top):
        y, w = 60 + i * 38, max(6, int(360 * n / biggest))
        p.append(f'<text x="700" y="{y+16}" font-size="14" fill="{SOFT}" style="{MONO}">{esc(lang)}</text>')
        p.append(f'<rect class="bar" x="860" y="{y}" width="{w}" height="22" rx="3" fill="{TEAL}"/>')
        p.append(f'<text x="{860+w+10}" y="{y+16}" font-size="14" fill="{MUTE}" style="{MONO}">{n}</text>')
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    p.append(f'<text x="60" y="296" font-size="13" fill="{MUTE}" style="{MONO}">Refreshed {stamp} by GitHub Actions</text></svg>')
    write("metrics.svg", "\n".join(p))


def card(repo, fallback):
    try:
        d = api(f"/repos/{USER}/{repo}")
    except urllib.error.HTTPError:
        d = {}
    desc = (d.get("description") or fallback)
    lines = textwrap.wrap(desc, 52)[:3]
    lang = d.get("language") or "n/a"
    stars = d.get("stargazers_count", 0)
    pushed = (d.get("pushed_at") or "")[:10] or "n/a"
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 560 190" role="img" aria-label="{esc(repo)}">',
         f'<defs><clipPath id="c"><rect width="560" height="190" rx="10"/></clipPath>'
         f'<linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{TEAL}" stop-opacity="0"/>'
         f'<stop offset=".5" stop-color="{TEAL}"/><stop offset="1" stop-color="{TEAL}" stop-opacity="0"/></linearGradient></defs>',
         '<style>.sweep{animation:sweep 5s ease-in-out infinite}@keyframes sweep{0%{transform:translateX(-240px)}100%{transform:translateX(560px)}}'
         '@media (prefers-reduced-motion:reduce){.sweep{animation:none;transform:translateX(160px)}}</style>',
         f'<g clip-path="url(#c)"><rect width="560" height="190" fill="{PANEL}"/>',
         f'<rect class="sweep" x="0" y="0" width="240" height="3" fill="url(#g)"/></g>',
         f'<rect x=".5" y=".5" width="559" height="189" rx="10" fill="none" stroke="{LINE}"/>',
         f'<text x="28" y="48" font-size="22" font-weight="700" fill="{INK}" style="{SANS}">{esc(repo)}</text>']
    for i, ln in enumerate(lines):
        p.append(f'<text x="28" y="{80 + i*24}" font-size="16" fill="{SOFT}" style="{SANS}">{esc(ln)}</text>')
    p.append(f'<circle cx="34" cy="158" r="5" fill="{AMBER}"/>')
    p.append(f'<text x="48" y="163" font-size="14" fill="{MUTE}" style="{MONO}">{esc(lang)}</text>')
    p.append(f'<text x="230" y="163" font-size="14" fill="{MUTE}" style="{MONO}">★ {stars}</text>')
    p.append(f'<text x="532" y="163" font-size="14" fill="{MUTE}" text-anchor="end" style="{MONO}">pushed {esc(pushed)}</text></svg>')
    write(f"card-{repo}.svg", "\n".join(p))


def marquee():
    gap, size = 56, 17
    widths = [int(len(t) * size * 0.62) + gap for t in TICKER]
    period = sum(widths)
    def row(offset):
        x, out = offset, []
        for t, w in zip(TICKER, widths):
            out.append(f'<text x="{x}" y="38" font-size="{size}" fill="{SOFT}" style="{MONO}">{esc(t)}</text>')
            out.append(f'<circle cx="{x + w - gap/2}" cy="32" r="2.5" fill="{AMBER}"/>')
            x += w
        return "".join(out)
    body = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 60" role="img" aria-label="Tools across my projects">'
            f'<defs><linearGradient id="f" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            f'<stop offset=".08" stop-color="#fff"/><stop offset=".92" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<mask id="m"><rect width="1200" height="60" fill="url(#f)"/></mask></defs>'
            f'<style>.t{{animation:run {period/55:.1f}s linear infinite}}@keyframes run{{to{{transform:translateX(-{period}px)}}}}'
            f'@media (prefers-reduced-motion:reduce){{.t{{animation:none}}}}</style>'
            f'<rect width="1200" height="60" fill="{BG}"/><g mask="url(#m)"><g class="t">{row(0)}{row(period)}{row(2*period)}</g></g></svg>')
    write("marquee.svg", body)


def main():
    metrics(all_repos())
    for repo, fb in FEATURED.items():
        card(repo, fb)
    marquee()


if __name__ == "__main__":
    main()

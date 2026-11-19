"""Generate every image on the profile from the public data of ALL repositories.

Writes SVGs to profile/. Standard library only. Set GITHUB_TOKEN (Actions provides it).
Env: PROFILE_USER (default AmDeep), SEED=1 to write placeholders when the API is unreachable.
"""
import hashlib
import html
import json
import math
import os
import textwrap
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone

USER = os.environ.get("PROFILE_USER", "AmDeep")
OUT = os.environ.get("PROFILE_DIR", "profile")
SEED = os.environ.get("SEED") == "1"

FEATURED = {
    "AIAgents": "Runnable reference patterns for reliable agent systems.",
    "RAGSystemLabs": "Hands-on labs for retrieval-augmented generation systems.",
    "inference-serving-portfolio": "Reproducible inference experiments, serving patterns, and benchmark evidence.",
    "ros2-vllm-navigation-bridge": "A bounded navigation bridge with explicit ROS 2 contracts and local obstacle checks.",
    "manipulation-vllm-safety-gateway": "Validation and approval boundaries for robot manipulation commands.",
    "edge-vision-vllm-inspector": "Computer-vision and inference integration patterns for edge deployment.",
}
TOOLBOX = {
    "Languages": ["Python", "C/C++", "TypeScript", "JavaScript", "SQL", "R", "MATLAB"],
    "AI / ML": ["PyTorch", "TensorFlow", "scikit-learn", "LangChain", "LangGraph", "vLLM"],
    "Robotics & systems": ["ROS 2", "OpenCV", "ONNX Runtime", "TensorRT", "Triton", "MQTT", "Docker", "AWS", "Azure"],
}
DOMAINS = {
    "Agents & LLM apps": ["agent", "llm", "langchain", "langgraph", "gpt", "openai", "chatbot", "genai", "vllm", "prompt"],
    "Retrieval (RAG)": ["rag", "retrieval", "embedding", "vector", "semantic search"],
    "Robotics & edge": ["ros", "robot", "navigation", "manipulation", "slam", "jetson", "edge", "embedded"],
    "Computer vision": ["vision", "opencv", "yolo", "detection", "segmentation", "image", "cnn"],
    "MLOps & cloud": ["mlops", "deploy", "aws", "azure", "docker", "inference", "serving", "sagemaker", "pipeline"],
    "Data science": ["kaggle", "prediction", "regression", "classification", "forecast", "analysis", "analytics", "nlp", "sentiment"],
}

BG, PANEL, LINE, GRID = "#0E1621", "#16263A", "#2C4058", "#1F3044"
INK, SOFT, MUTE, TEAL, AMBER = "#E8EEF4", "#B8C7D6", "#8FA3B8", "#5CC8C0", "#FFB347"
PALETTE = [TEAL, AMBER, "#6EA8FE", "#B197FC", "#F783AC", "#8CE99A"]
SLATE = "#8FA3B8"
esc = html.escape

BASE_CSS = (
    ".s{font-family:'Segoe UI','Helvetica Neue',Arial,system-ui,sans-serif}"
    ".m{font-family:'JetBrains Mono',Consolas,ui-monospace,monospace}"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
)


# ---------- helpers ----------
def hf(s, salt=""):
    return int(hashlib.md5((salt + s).encode()).hexdigest()[:8], 16) / 0xFFFFFFFF


def pdt(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def shade(hexc, f):
    r, g, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % (int(r * f), int(g * f), int(b * f))


def human_bytes(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1000 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1000


def svg(w, h, body, label, css=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">'
            f"<style>{BASE_CSS}{css}</style>"
            f'<rect width="{w}" height="{h}" fill="{BG}"/>{body}</svg>')


def txt(x, y, s, size=14, fill=SOFT, cls="s", weight=None, anchor=None, extra=""):
    a = f' text-anchor="{anchor}"' if anchor else ""
    w = f' font-weight="{weight}"' if weight else ""
    return f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{fill}"{w}{a}{extra}>{esc(str(s))}</text>'


def write(name, body):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)


def placeholder(name, w, h, label):
    write(name, svg(w, h, txt(w / 2, h / 2, "Waiting for the first data refresh: run the Actions workflow.", 16, MUTE, "m", anchor="middle"), label))


# ---------- GitHub data ----------
def _req(url, data=None):
    req = urllib.request.Request(url, data=data, headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-assets"})
    if os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {os.environ['GITHUB_TOKEN']}")
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)


def all_repos():
    repos, page = [], 1
    while True:
        batch = _req(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner&page={page}")
        repos += batch
        if len(batch) < 100:
            return [r for r in repos if not r.get("private")]
        page += 1


def repo_languages(repos):
    per, total = {}, Counter()
    for r in repos:
        if r["fork"]:
            continue
        try:
            d = _req(f"https://api.github.com/repos/{USER}/{r['name']}/languages")
        except Exception:
            continue
        per[r["name"]] = d
        total.update(d)
    return per, total


def contributions():
    q = ("query($l:String!){user(login:$l){contributionsCollection{contributionCalendar{totalContributions "
         "weeks{contributionDays{date contributionCount}}}}}}")
    d = _req("https://api.github.com/graphql", json.dumps({"query": q, "variables": {"l": USER}}).encode())
    cal = d["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return [(wk["contributionDays"]) for wk in cal["weeks"]], cal["totalContributions"]


def lang_colors(repos):
    ranked = [l for l, _ in Counter(r["language"] for r in repos if r.get("language")).most_common(6)]
    cmap = {l: PALETTE[i] for i, l in enumerate(ranked)}
    return ranked, cmap


# ---------- 1. repository universe ----------
def universe(repos, ranked, cmap):
    if not repos:
        return placeholder("universe.svg", 1200, 580, "Repository universe")
    lanes = ranked + ["Other"]
    W, H, left, right, top, bottom = 1200, 580, 270, 1120, 130, 500
    lane_h = (bottom - top) / len(lanes)
    created = [pdt(r["created_at"]) for r in repos]
    t0, t1 = min(created), max(created)
    span = max((t1 - t0).total_seconds(), 1)
    counts = Counter((r["language"] if r.get("language") in ranked else "Other") for r in repos)
    featured = set(FEATURED)
    body = [txt(48, 52, "Every repository, plotted by when it was created", 24, INK, weight=700),
            txt(48, 78, f"{len(repos)} public repositories ({sum(1 for r in repos if not r['fork'])} original, "
                f"{sum(1 for r in repos if r['fork'])} forks). Each dot is one repo.", 14, MUTE, "m")]
    for y in range(t0.year, t1.year + 1):
        x = left + (datetime(y, 1, 1, tzinfo=timezone.utc) - t0).total_seconds() / span * (right - left)
        if left - 5 <= x <= right + 5:
            body.append(f'<line x1="{x:.0f}" y1="{top - 6}" x2="{x:.0f}" y2="{bottom}" stroke="{GRID}"/>')
            body.append(txt(x + 6, bottom + 22, y, 13, MUTE, "m"))
    for i, lane in enumerate(lanes):
        y = top + lane_h * (i + 0.5)
        col = cmap.get(lane, SLATE)
        body.append(f'<line x1="{left - 20}" y1="{y:.0f}" x2="{right}" y2="{y:.0f}" stroke="{GRID}" stroke-dasharray="2 8"/>')
        body.append(f'<circle cx="52" cy="{y - 4:.0f}" r="5" fill="{col}"/>')
        body.append(txt(66, y, f"{lane}", 14, SOFT, "m"))
        body.append(txt(left - 28, y, counts[lane], 14, MUTE, "m", anchor="end"))
    labels, nodes = [], []
    for r in repos:
        lane = r["language"] if r.get("language") in ranked else "Other"
        i = lanes.index(lane)
        x = left + (pdt(r["created_at"]) - t0).total_seconds() / span * (right - left) + (hf(r["name"], "x") - .5) * 14
        y = top + lane_h * (i + .5) + (hf(r["name"], "y") - .5) * lane_h * .7
        rad = 3.5 + min(8, math.log10(1 + r.get("size", 0)) * 1.8) + min(4, r.get("stargazers_count", 0) * .8)
        col = cmap.get(lane, SLATE)
        cls = f"n f{int(hf(r['name'], 'c') * 3)}"
        delay = f"animation-delay:-{hf(r['name'], 'd') * 7:.1f}s"
        if r["fork"]:
            nodes.append(f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="{rad:.1f}" fill="none" stroke="{col}" stroke-width="1.5" style="{delay}"/>')
        else:
            nodes.append(f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="{rad:.1f}" fill="{col}" fill-opacity=".85" style="{delay}"/>')
        if r["name"] in featured:
            nodes.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad + 5:.1f}" fill="none" stroke="{AMBER}" stroke-width="1.5" class="ring"/>')
            labels.append(txt(x, y - rad - 10, r["name"], 12, INK, "m", anchor="end" if x > 950 else "middle"))
    body += nodes + labels
    body.append(f'<circle cx="52" cy="548" r="5" fill="{TEAL}"/>' + txt(66, 553, "original", 13, MUTE, "m")
                + f'<circle cx="160" cy="548" r="5" fill="none" stroke="{TEAL}" stroke-width="1.5"/>' + txt(174, 553, "fork", 13, MUTE, "m")
                + f'<circle cx="240" cy="548" r="7" fill="none" stroke="{AMBER}" stroke-width="1.5"/>' + txt(256, 553, "featured", 13, MUTE, "m")
                + txt(1150, 553, "dot size reflects code size and stars", 13, MUTE, "m", anchor="end"))
    css = (".n{animation:float 7s ease-in-out infinite alternate}.f1{animation-duration:9s}.f2{animation-duration:11s}"
           "@keyframes float{from{transform:translateY(-4px)}to{transform:translateY(4px)}}"
           ".ring{animation:ring 3s ease-in-out infinite}@keyframes ring{50%{stroke-opacity:.25}}")
    write("universe.svg", svg(W, H, "".join(body), "Every repository plotted by creation date and language", css))


# ---------- 2. insights ----------
def classify(repos):
    c = Counter()
    for r in repos:
        if r["fork"]:
            continue
        t = " ".join([r["name"], r.get("description") or "", " ".join(r.get("topics") or [])]).lower().replace("-", " ").replace("_", " ")
        for dom, words in DOMAINS.items():
            if any(w in t for w in words):
                c[dom] += 1
    return c.most_common()


def insights(repos, langbytes, cmap):
    if not repos:
        return placeholder("insights.svg", 1200, 420, "Profile insights")
    own = [r for r in repos if not r["fork"]]
    forks = [r for r in repos if r["fork"]]
    now = datetime.now(timezone.utc)
    active = sum(1 for r in own if now - pdt(r.get("pushed_at") or r["created_at"]) <= timedelta(days=90))
    years = (now - min(pdt(r["created_at"]) for r in repos)).days / 365.25
    stars = sum(r["stargazers_count"] for r in own)
    kpis = [(len(own), "original repositories"), (len(forks), "forked projects"), (stars, "stars earned"),
            (active, "active in last 90 days"), (f"{years:.1f}", "years on GitHub"),
            (human_bytes(sum(langbytes.values())) if langbytes else "n/a", "of code and notebooks")]
    body = [txt(48, 52, "Profile insights", 24, INK, weight=700),
            txt(48, 78, f"Computed from all {len(repos)} public repositories", 14, MUTE, "m")]
    for i, (v, lab) in enumerate(kpis):
        x, y = 48 + (i % 2) * 190, 104 + (i // 2) * 104
        body.append(f'<rect x="{x}" y="{y}" width="176" height="90" rx="8" fill="{PANEL}" stroke="{LINE}"/>')
        body.append(txt(x + 16, y + 44, v, 32, INK, weight=700))
        body.append(txt(x + 16, y + 70, lab, 13, MUTE))
    # languages by bytes
    body.append(txt(460, 112, "Languages by code volume", 16, SOFT, weight=600))
    tot = sum(langbytes.values()) or 1
    top = langbytes.most_common(7)
    mx = (top[0][1] / tot) if top else 1
    for i, (l, b) in enumerate(top):
        y = 140 + i * 38
        w = max(4, 150 * (b / tot) / mx)
        body.append(txt(460, y + 15, l, 13, SOFT, "m"))
        body.append(f'<rect class="bar" x="620" y="{y}" width="{w:.0f}" height="20" rx="3" fill="{cmap.get(l, SLATE)}" style="animation-delay:{i * .1:.1f}s"/>')
        body.append(txt(620 + w + 10, y + 15, f"{100 * b / tot:.0f}%", 13, MUTE, "m"))
    body.append(txt(460, 410, "Notebook outputs count toward Jupyter bytes,", 12, MUTE, "m"))
    body.append(txt(460, 426, "so notebook-heavy work looks larger here.", 12, MUTE, "m"))
    # domains
    body.append(txt(850, 112, "What the repositories are about", 16, SOFT, weight=600))
    doms = classify(repos)[:7]
    dm = doms[0][1] if doms else 1
    for i, (d, n) in enumerate(doms):
        y = 140 + i * 38
        w = max(4, 120 * n / dm)
        body.append(txt(850, y + 15, d, 13, SOFT, "m"))
        body.append(f'<rect class="bar" x="1010" y="{y}" width="{w:.0f}" height="20" rx="3" fill="{AMBER}" style="animation-delay:{i * .1:.1f}s"/>')
        body.append(txt(1010 + w + 10, y + 15, n, 13, MUTE, "m"))
    body.append(txt(850, 410, "Tagged from repo names, descriptions", 12, MUTE, "m"))
    body.append(txt(850, 426, "and topics; a repo can fit several.", 12, MUTE, "m"))
    css = ".bar{transform-box:fill-box;transform-origin:left;animation:grow 1s cubic-bezier(.2,.8,.2,1) both}@keyframes grow{from{transform:scaleX(0)}}"
    write("insights.svg", svg(1200, 445, "".join(body), "Profile insights across all repositories", css))


# ---------- 3. activity ----------
def activity(repos):
    if not repos:
        return placeholder("activity.svg", 1200, 380, "Repository activity")
    own = [r for r in repos if not r["fork"]]
    by_year = Counter(pdt(r["created_at"]).year for r in own)
    ys = list(range(min(by_year), max(by_year) + 1)) if by_year else []
    mx = max(by_year.values(), default=1)
    body = [txt(48, 52, "Repositories created per year", 20, INK, weight=700)]
    bw = min(48, 500 // max(len(ys), 1) - 10)
    step = bw + 10
    for i, y in enumerate(ys):
        n = by_year.get(y, 0)
        hgt = max(3, 200 * n / mx)
        x = 56 + i * step
        body.append(f'<rect class="rise" x="{x}" y="{300 - hgt:.0f}" width="{bw}" height="{hgt:.0f}" rx="3" fill="{TEAL}" style="animation-delay:{i * .08:.2f}s"/>')
        body.append(txt(x + bw / 2, 292 - hgt, n, 13, SOFT, "m", anchor="middle"))
        body.append(txt(x + bw / 2, 324, f"’{str(y)[2:]}", 13, MUTE, "m", anchor="middle"))
    body.append(f'<line x1="48" y1="304" x2="580" y2="304" stroke="{LINE}"/>')
    body.append(txt(660, 52, "Recently pushed", 20, INK, weight=700))
    recent = sorted(own, key=lambda r: r.get("pushed_at") or r["created_at"], reverse=True)[:6]
    cl = {}
    for i, r in enumerate(recent):
        y = 100 + i * 42
        lang = r.get("language") or "n/a"
        body.append(f'<circle cx="672" cy="{y - 5}" r="5" fill="{TEAL if i else AMBER}" class="{"pulse" if i == 0 else ""}"/>')
        body.append(txt(692, y, r["name"][:30], 17, INK, weight=600))
        body.append(txt(692, y + 18, lang, 12, MUTE, "m"))
        body.append(txt(1152, y, (r.get("pushed_at") or r["created_at"])[:10], 14, MUTE, "m", anchor="end"))
    css = (".rise{transform-box:fill-box;transform-origin:bottom;animation:r 1s cubic-bezier(.2,.8,.2,1) both}@keyframes r{from{transform:scaleY(0)}}"
           ".pulse{animation:p 1.8s ease-in-out infinite}@keyframes p{50%{opacity:.3}}")
    write("activity.svg", svg(1200, 380, "".join(body), "Repository activity", css))


# ---------- 4. isometric contribution skyline ----------
def skyline(weeks, total):
    A, B, k = (17.5, 4.0), (-8.0, 12.0), 1.0
    ox, oy, gap = 200, 190, .1
    days = [(d["date"], d["contributionCount"]) for w in weeks for d in w]
    mx = max((c for _, c in days), default=0) or 1
    # streaks
    best = cur = 0
    for _, c in days:
        cur = cur + 1 if c else 0
        best = max(best, cur)
    cur = 0
    for _, c in reversed(days):
        if c:
            cur += 1
        elif cur or _ != days[-1][0]:
            break
    busiest = max(days, key=lambda x: x[1], default=("", 0))
    active = sum(1 for _, c in days if c)
    cols = [GRID, "#2C6E73", "#3FA3A0", TEAL, "#9BE8E1"]
    items = []
    for wi, wk in enumerate(weeks):
        for di, d in enumerate(wk):
            items.append((wi * A[1] + di * B[1], wi, di, d["contributionCount"]))
    items.sort()
    bars = []
    for _, wi, di, c in items:
        lvl = 0 if c == 0 else max(1, min(4, math.ceil(4 * c / mx)))
        hgt = 2 if c == 0 else 6 + 96 * c / mx
        px = ox + wi * A[0] + di * B[0]
        py = oy + wi * A[1] + di * B[1]
        a = (A[0] * (1 - gap * 2), A[1] * (1 - gap * 2))
        b = (B[0] * (1 - gap * 2), B[1] * (1 - gap * 2))
        px += A[0] * gap + B[0] * gap
        py += A[1] * gap + B[1] * gap
        P0 = (px, py)
        P1 = (px + a[0], py + a[1])
        P2 = (px + a[0] + b[0], py + a[1] + b[1])
        P3 = (px + b[0], py + b[1])
        up = lambda p: (p[0], p[1] - hgt)
        pts = lambda *ps: " ".join(f"{x:.1f},{y:.1f}" for x, y in ps)
        col = cols[lvl]
        bars.append(f'<g class="b" style="animation-delay:{wi * .025:.2f}s">'
                    f'<polygon points="{pts(P3, P2, up(P2), up(P3))}" fill="{shade(col, .78)}"/>'
                    f'<polygon points="{pts(P1, P2, up(P2), up(P1))}" fill="{shade(col, .58)}"/>'
                    f'<polygon points="{pts(up(P0), up(P1), up(P2), up(P3))}" fill="{col}"/></g>')
    body = [txt(48, 52, f"{total:,} contributions in the last year", 26, INK, weight=700),
            txt(48, 78, f"longest streak {best} days · current streak {cur} · busiest day {busiest[1]} · active on {active} days", 14, MUTE, "m")]
    body += bars
    lx = 48
    body.append(txt(lx, 506, "less", 12, MUTE, "m"))
    for i, c in enumerate(cols):
        body.append(f'<rect x="{lx + 38 + i * 18}" y="496" width="12" height="12" rx="2" fill="{c}"/>')
    body.append(txt(lx + 38 + 5 * 18 + 6, 506, "more", 12, MUTE, "m"))
    css = ".b{transform-box:fill-box;transform-origin:50% 100%;animation:rise 1.2s cubic-bezier(.2,.8,.2,1) both}@keyframes rise{from{transform:scaleY(0)}}"
    write("skyline.svg", svg(1200, 520, "".join(body), f"{total} contributions in the last year as an isometric skyline", css))


# ---------- 5. project cards ----------
def cards(repos, langper):
    byname = {r["name"]: r for r in repos}
    for name, fallback in FEATURED.items():
        r = byname.get(name, {})
        desc = r.get("description") or fallback
        lines = textwrap.wrap(desc, 50)[:3]
        topics = (r.get("topics") or [])[:3]
        stars = r.get("stargazers_count", "–")
        pushed = (r.get("pushed_at") or "")[:10] or "–"
        main_lang = r.get("language") or "–"
        lb = langper.get(name, {})
        tot = sum(lb.values())
        W, Hh = 560, 210
        p = [f'<defs><clipPath id="c"><rect width="{W}" height="{Hh}" rx="10"/></clipPath>'
             f'<linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{TEAL}" stop-opacity="0"/><stop offset=".5" stop-color="{TEAL}"/>'
             f'<stop offset="1" stop-color="{TEAL}" stop-opacity="0"/></linearGradient></defs>',
             f'<g clip-path="url(#c)"><rect width="{W}" height="{Hh}" fill="{PANEL}"/><rect class="sweep" width="240" height="3" fill="url(#g)"/>']
        if tot:
            x = 0
            for i, (l, b) in enumerate(sorted(lb.items(), key=lambda kv: -kv[1])[:5]):
                w = W * b / tot
                p.append(f'<rect x="{x:.1f}" y="{Hh - 6}" width="{w:.1f}" height="6" fill="{PALETTE[i % 6]}"/>')
                x += w
        p.append("</g>")
        p.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{Hh - 1}" rx="10" fill="none" stroke="{LINE}"/>')
        p.append(txt(28, 48, name, 22, INK, weight=700))
        for i, ln in enumerate(lines):
            p.append(txt(28, 80 + i * 24, ln, 16, SOFT))
        cx = 28
        for t in topics:
            w = len(t) * 8 + 20
            p.append(f'<rect x="{cx}" y="140" width="{w}" height="22" rx="11" fill="none" stroke="{LINE}"/>' + txt(cx + w / 2, 155, t, 12, MUTE, "m", anchor="middle"))
            cx += w + 8
        p.append(f'<circle cx="34" cy="184" r="5" fill="{AMBER}"/>' + txt(48, 189, main_lang, 14, MUTE, "m")
                 + txt(230, 189, f"★ {stars}", 14, MUTE, "m") + txt(W - 28, 189, f"pushed {pushed}", 14, MUTE, "m", anchor="end"))
        css = ".sweep{animation:sw 5s ease-in-out infinite}@keyframes sw{from{transform:translateX(-240px)}to{transform:translateX(560px)}}"
        out = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {Hh}" role="img" aria-label="{esc(name)}">'
               f"<style>{BASE_CSS}{css}</style>{''.join(p)}</svg>")
        write(f"card-{name}.svg", out)


# ---------- 6. ticker, toolbox, wave footer, loop ----------
def marquee(repos):
    langs = [l for l, _ in Counter(r["language"] for r in repos if r.get("language")).most_common(6)]
    topics = [t for t, _ in Counter(t for r in repos for t in (r.get("topics") or [])).most_common(10)]
    items, seen = [], set()
    for t in ["Python", "PyTorch", "vLLM", "LangGraph", "RAG", "ROS 2", "OpenCV", "ONNX Runtime", "TensorRT", "Triton", "MQTT", "Docker", "AWS", "Azure"] + langs + topics:
        if t.lower() not in seen:
            seen.add(t.lower())
            items.append(t)
    size, gap = 17, 56
    widths = [int(len(t) * size * .62) + gap for t in items]
    period = sum(widths)

    def row(off):
        x, out = off, []
        for t, w in zip(items, widths):
            out.append(txt(x, 38, t, size, SOFT, "m") + f'<circle cx="{x + w - gap / 2}" cy="32" r="2.5" fill="{AMBER}"/>')
            x += w
        return "".join(out)
    body = ('<defs><linearGradient id="f" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".08" stop-color="#fff"/>'
            '<stop offset=".92" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            '<mask id="m"><rect width="1200" height="60" fill="url(#f)"/></mask></defs>'
            f'<g mask="url(#m)"><g class="t">{row(0)}{row(period)}{row(2 * period)}</g></g>')
    css = f".t{{animation:run {period / 55:.1f}s linear infinite}}@keyframes run{{to{{transform:translateX(-{period}px)}}}}"
    write("marquee.svg", svg(1200, 60, body, "Tools and topics across my repositories", css))


def toolbox():
    body, y, idx = [], 40, 0
    for grp, items in TOOLBOX.items():
        body.append(txt(48, y, grp, 16, SOFT, weight=600))
        x, row_y = 48, y + 18
        for t in items:
            w = len(t) * 9.4 + 34
            if x + w > 1150:
                x, row_y = 48, row_y + 44
            body.append(f'<g class="chip" style="animation-delay:{idx * .06:.2f}s"><rect x="{x:.0f}" y="{row_y}" width="{w:.0f}" height="34" rx="17" fill="{PANEL}" stroke="{LINE}"/>'
                        f'<circle class="dot" cx="{x + 17:.0f}" cy="{row_y + 17}" r="3.5" fill="{TEAL}" style="animation-delay:{(idx % 7) * .4:.1f}s"/>'
                        + txt(x + 29, row_y + 22, t, 14, INK, "m") + "</g>")
            x += w + 10
            idx += 1
        y = row_y + 34 + 38
    css = (".chip{animation:in .8s cubic-bezier(.2,.8,.2,1) both}@keyframes in{from{opacity:0;transform:translateY(10px)}}"
           ".dot{animation:d 3s ease-in-out infinite}@keyframes d{50%{opacity:.25}}")
    write("toolbox.svg", svg(1200, y - 10, "".join(body), "Toolbox: languages, AI/ML, robotics and systems", css))


def footer():
    def wave(amp, off):
        d = f"M0 {60 + off} " + " ".join(f"Q{150 + i * 300} {60 + off - amp * (1 if i % 2 == 0 else -1)} {300 + i * 300} {60 + off}" for i in range(8))
        return d + " V120 H0 Z"
    body = (f'<g class="w1"><path d="{wave(18, 0)}" fill="{TEAL}" fill-opacity=".10"/></g>'
            f'<g class="w2"><path d="{wave(14, 12)}" fill="{TEAL}" fill-opacity=".16"/></g>'
            f'<g class="w3"><path d="{wave(10, 24)}" fill="{TEAL}" fill-opacity=".25"/></g>')
    css = ("@keyframes a{to{transform:translateX(-1200px)}}.w1{animation:a 18s linear infinite}.w2{animation:a 12s linear infinite}.w3{animation:a 8s linear infinite}")
    write("footer.svg", svg(1200, 120, body, "", css))


def hero_and_loop():
    pass  # static files shipped alongside this script


# ---------- main ----------
def main():
    try:
        repos = all_repos()
    except Exception:
        if not SEED:
            raise
        repos = []
    ranked, cmap = lang_colors(repos)
    langper, langtotal = ({}, Counter())
    if repos:
        langper, langtotal = repo_languages(repos)
    universe(repos, ranked, cmap)
    insights(repos, langtotal, cmap)
    activity(repos)
    cards(repos, langper)
    marquee(repos)
    toolbox()
    footer()
    try:
        weeks, total = contributions()
        skyline(weeks, total)
    except Exception:
        if not os.path.exists(os.path.join(OUT, "skyline.svg")) or SEED:
            empty = [[{"date": f"2026-01-{(d % 28) + 1:02d}", "contributionCount": 0} for d in range(7)] for _ in range(53)]
            skyline(empty, 0)


if __name__ == "__main__":
    main()

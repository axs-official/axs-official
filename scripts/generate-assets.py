"""Generate the axs GitHub profile SVG cards (self-contained, CSS-animated)."""
import html
import json
import math
import os
import random
import textwrap

random.seed(11)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "profile", "assets")
os.makedirs(OUT, exist_ok=True)

with open(
    os.path.join(ROOT, "site", "src", "data", "contributions.json"), encoding="utf-8-sig"
) as fh:
    DATA = json.load(fh)

# Brand paths/colours, extracted from simple-icons once (see profile/scripts/icons.json).
with open(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons.json"), encoding="utf-8"
) as fh:
    ICONS = json.load(fh)

BG = "#0A0A0A"
PANEL = "#111111"
INK = "#F5F5F5"
MUTED = "#A3A3A3"
DIM = "#8F8F8F"
LINE = "#262626"
LINE_SOFT = "#1B1B1B"
ACCENT = "#FFFFFF"
BLUE = "#FFFFFF"
BLUE_SOFT = "#EDEDED"
LIVE = "#4ADE80"
ZERO = "#151515"
RAMP = [ZERO, "#343434", "#5E5E5E", "#949494", "#EDEDED"]

SANS = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
SERIF = "Georgia, 'Times New Roman', 'Iowan Old Style', serif"
MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"

W = 840
PAD = 32
CONTACT_EMAIL = "axs.contact.me@gmail.com"

BASE_CSS = """<style>
    .rise{animation:rise .8s cubic-bezier(.22,1,.36,1) both}
    .grow{transform-box:fill-box;transform-origin:left center;animation:grow 1s cubic-bezier(.22,1,.36,1) both}
    .blink{animation:blink 2.6s ease-in-out infinite}
    .sweep{animation:sweep 6s cubic-bezier(.5,0,.2,1) infinite}
    .spin{transform-box:fill-box;transform-origin:center;animation:spin 56s linear infinite}
    .spin-r{transform-box:fill-box;transform-origin:center;animation:spin 40s linear infinite reverse}
    .star{animation:twinkle 5s ease-in-out infinite}
    .cell{animation:pop .5s cubic-bezier(.22,1,.36,1) both}
    .fade{animation:fade 1.4s ease-out both}
    .float{animation:float 7s ease-in-out infinite}
    .dash{animation:dash 24s linear infinite}
    .scan{animation:scan 7.5s cubic-bezier(.45,0,.25,1) infinite}
    .draw{animation:draw 3.2s cubic-bezier(.4,0,.2,1) .3s both}
    @keyframes rise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
    @keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
    @keyframes blink{0%,100%{opacity:.3}50%{opacity:1}}
    @keyframes sweep{0%{transform:translateX(0);opacity:0}16%{opacity:.9}70%{opacity:.35}100%{transform:translateX(128px);opacity:0}}
    @keyframes spin{to{transform:rotate(360deg)}}
    @keyframes twinkle{0%,100%{opacity:.14}50%{opacity:.8}}
    @keyframes pop{from{opacity:0;transform:scale(.4)}to{opacity:1;transform:scale(1)}}
    @keyframes fade{from{opacity:0}to{opacity:1}}
    @keyframes float{0%,100%{transform:translateY(-3.5px)}50%{transform:translateY(3.5px)}}
    @keyframes dash{to{stroke-dashoffset:-240}}
    @keyframes scan{0%{transform:translateX(0);opacity:0}12%{opacity:1}82%{opacity:1}100%{transform:translateX(744px);opacity:0}}
    @keyframes draw{to{stroke-dashoffset:0}}
  </style>"""


def esc(value):
    return html.escape(str(value), quote=False)


def rgb(hex_color):
    value = hex_color.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def to_hex(channels):
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(round(c)))) for c in channels)


def mix(a, b, amount):
    first, second = rgb(a), rgb(b)
    return to_hex(first[i] + (second[i] - first[i]) * amount for i in range(3))


def brand(hex_color):
    """Brand colour, lifted only when it would disappear on a dark plate."""
    r, g, b = rgb(hex_color)
    luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
    if luminance < 0.06:
        return "#F2F2F2"
    if luminance < 0.26:
        return to_hex(channel + (255 - channel) * 0.5 for channel in (r, g, b))
    return "#" + hex_color.lstrip("#").upper()


def open_svg(height, label, title, extra_css=""):
    return f'''<svg width="{W}" height="{height}" viewBox="0 0 {W} {height}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{html.escape(label)}">
  <title>{esc(title)}</title>
  {BASE_CSS}{extra_css}
'''


def frame(height):
    return (
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{height - 1}" rx="16" '
        f'fill="{BG}" stroke="{LINE}"/>'
    )


def header(kicker, right=""):
    right_text = (
        f'<text x="{W - PAD}" y="38" text-anchor="end" font-family="{MONO}" font-size="12" '
        f'letter-spacing="1.4" fill="{DIM}">{esc(right)}</text>'
        if right
        else ""
    )
    return (
        f'<text x="{PAD}" y="38" font-family="{MONO}" font-size="13" letter-spacing="2.6" '
        f'fill="{BLUE_SOFT}">{esc(kicker)}</text>'
        + right_text
        + f'<path d="M{PAD} 52H{W - PAD}" stroke="{LINE}"/>'
    )


def grid(height, step=40, opacity=0.03):
    parts = [f'<g stroke="{ACCENT}" stroke-width="1" opacity="{opacity}">']
    x = 0
    while x <= W:
        parts.append(f'<path d="M{x} 0V{height}"/>')
        x += step
    y = 0
    while y <= height:
        parts.append(f'<path d="M0 {y}H{W}"/>')
        y += step
    parts.append("</g>")
    return "".join(parts)


def stars(count, max_x, height, avoid=()):
    out = []
    attempts = 0
    while len(out) < count and attempts < count * 80:
        attempts += 1
        x = round(random.uniform(30, max_x), 1)
        y = round(random.uniform(18, height - 16), 1)
        # Never drop a star on top of a word.
        if any(x0 <= x <= x1 and y0 <= y <= y1 for x0, y0, x1, y1 in avoid):
            continue
        r = random.choice([0.7, 0.8, 1.0, 1.2, 1.5])
        delay = round(random.uniform(0, 6), 2)
        duration = round(random.uniform(3.4, 7.5), 2)
        opacity = round(random.uniform(0.2, 0.75), 2)
        out.append(
            f'<circle class="star" cx="{x}" cy="{y}" r="{r}" fill="{ACCENT}" opacity="{opacity}" '
            f'style="animation-delay:{delay}s;animation-duration:{duration}s"/>'
        )
    return "".join(out)


def paragraph(x, y, text, size=15, chars=62, line_height=22, color=MUTED):
    lines = textwrap.wrap(text, width=chars)
    return "".join(
        f'<text x="{x}" y="{y + i * line_height}" font-family="{SANS}" font-size="{size}" '
        f'fill="{color}">{esc(line)}</text>'
        for i, line in enumerate(lines)
    )


def hero():
    height = 320
    cx, cy = 660, 152
    return (
        open_svg(
            height,
            "A-XS, full-stack developer. Privacy-first software, built end to end.",
            "A-XS — profile",
        )
        + f'''  <defs>
    <linearGradient id="name" x1="32" y1="112" x2="32" y2="176" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#FFFFFF"/>
      <stop offset="1" stop-color="#8C8C8C"/>
    </linearGradient>
    <linearGradient id="rule" x1="32" y1="0" x2="252" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity=".85"/>
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity=".13"/>
      <stop offset="0.6" stop-color="#FFFFFF" stop-opacity=".03"/>
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="planet" cx="0.32" cy="0.26" r="0.92">
      <stop offset="0" stop-color="#F2F2F2"/>
      <stop offset="0.42" stop-color="#8F8F8F"/>
      <stop offset="1" stop-color="#141414"/>
    </radialGradient>
    <clipPath id="pc"><circle cx="{cx}" cy="{cy}" r="45"/></clipPath>
  </defs>
  {frame(height)}
  {grid(height)}
  {stars(26, 812, height, avoid=[(24, 40, 470, 202), (24, 204, 534, 306), (632, 274, 820, 308)])}
  <circle cx="{cx}" cy="{cy}" r="196" fill="url(#glow)"/>
  <g>
    <circle class="spin-r" cx="{cx}" cy="{cy}" r="118" stroke="{ACCENT}" stroke-opacity=".16" stroke-width="1" stroke-dasharray="26 12"/>
    <circle class="spin" cx="{cx}" cy="{cy}" r="92" stroke="{LINE}" stroke-width="1" stroke-dasharray="2 6"/>
    <ellipse class="spin-r" cx="{cx}" cy="{cy}" rx="136" ry="36" stroke="{BLUE}" stroke-opacity=".6" stroke-width="1" transform="rotate(-24 {cx} {cy})"/>
    <circle cx="{cx}" cy="{cy - 92}" r="2.4" fill="{ACCENT}" opacity=".8"/>
  </g>
  <g>
    <circle cx="{cx}" cy="{cy}" r="45" fill="url(#planet)" stroke="{ACCENT}" stroke-opacity=".35"/>
    <g clip-path="url(#pc)" stroke="{ACCENT}" stroke-opacity=".18" stroke-width="1">
      <path d="M{cx - 45} {cy - 15}H{cx + 45}"/>
      <path d="M{cx - 45} {cy}H{cx + 45}"/>
      <path d="M{cx - 45} {cy + 15}H{cx + 45}"/>
      <ellipse cx="{cx}" cy="{cy}" rx="15" ry="45"/>
      <ellipse cx="{cx}" cy="{cy}" rx="30" ry="45"/>
    </g>
  </g>
  <g class="rise">
    <text x="{PAD}" y="66" font-family="{MONO}" font-size="13" letter-spacing="3" fill="{ACCENT}">A-XS / PROFILE</text>
  </g>
  <g class="rise" style="animation-delay:.08s">
    <text x="{PAD}" y="172" font-family="{SERIF}" font-size="62" letter-spacing="-1" fill="url(#name)">A-XS</text>
  </g>
  <rect x="{PAD}" y="189" width="220" height="1.5" fill="url(#rule)"/>
  <rect class="sweep" x="{PAD}" y="188.5" width="92" height="2" rx="1" fill="{BLUE}" opacity=".9"/>
  <g class="rise" style="animation-delay:.18s">
    <text x="{PAD}" y="234" font-family="{SANS}" font-size="18" fill="{INK}" fill-opacity=".94">Full-stack developer building privacy-first software.</text>
    <text x="{PAD}" y="260" font-family="{SANS}" font-size="15" fill="{MUTED}">Web apps, automation and tools that leave your data alone.</text>
  </g>
  <g font-family="{MONO}" font-size="12.5" letter-spacing="1.4" fill="{MUTED}">
    <circle class="blink" cx="36" cy="291" r="3.4" fill="{LIVE}"/>
    <text x="48" y="296">OPEN TO PAID WORK</text>
    <text x="234" y="296">FULL-STACK</text>
    <text x="356" y="296">REMOTE</text>
  </g>
</svg>'''
    )


def stats():
    height = 282
    week_avg = round(DATA["total"] / 52)
    tiles = [
        (f"{DATA['total']:,}", "CONTRIBUTIONS", 0.9),
        (f"{DATA['activeDays']}", "ACTIVE DAYS", 0.76),
        (f"{DATA['longestStreak']}", "BEST STREAK", 0.64),
        ("13", "REPOSITORIES", 0.54),
        ("2", "PUBLIC REPOS", 0.46),
        (f"{week_avg}", "COMMITS / WEEK", 0.4),
    ]
    cw, ch, gap = 250, 88, 13
    cards = []
    for i, (value, label, strength) in enumerate(tiles):
        col, row = i % 3, i // 3
        x = PAD + col * (cw + gap)
        y = 68 + row * (ch + 14)
        cards.append(
            f'''<g class="rise" style="animation-delay:{round(i * 0.07, 2)}s">
      <rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="12" fill="{PANEL}" stroke="{LINE}"/>
      <rect class="grow" x="{x + 14}" y="{y + 1}" width="{cw - 28}" height="2" rx="1" fill="{BLUE}" opacity="{strength}" style="animation-delay:{round(i * 0.07 + 0.1, 2)}s"/>
      <text x="{x + 20}" y="{y + 28}" font-family="{MONO}" font-size="12.5" letter-spacing="1.4" fill="{MUTED}">{esc(label)}</text>
      <text x="{x + 20}" y="{y + 71}" font-family="{SERIF}" font-size="40" letter-spacing="-0.5" fill="{INK}">{value}</text>
    </g>'''
        )
    return (
        open_svg(
            height,
            f"GitHub figures for axs-official: {DATA['total']} contributions, {DATA['activeDays']} active days, "
            f"{DATA['longestStreak']} day best streak, 13 repositories.",
            "GitHub activity",
        )
        + f'''  {frame(height)}
  {header("GITHUB", "LAST 12 MONTHS")}
  {''.join(cards)}
</svg>'''
    )


def activity():
    height = 322
    weeks = DATA["weeks"]

    def level(count):
        # Fixed buckets: one huge import day would otherwise flatten the whole map.
        if count == 0:
            return 0
        if count <= 2:
            return 1
        if count <= 6:
            return 2
        if count <= 14:
            return 3
        return 4

    x0 = 64
    step = 14.3
    cell = 12
    y0 = 84
    width = step * len(weeks)
    cells = []
    for wi, week in enumerate(weeks):
        for day in week:
            x = x0 + wi * step
            y = y0 + day["w"] * step
            fill = RAMP[level(day["c"])]
            delay = round(wi * 0.012 + day["w"] * 0.003, 3)
            cells.append(
                f'<rect class="cell" x="{x:.1f}" y="{y:.1f}" width="{cell}" height="{cell}" rx="2.5" '
                f'fill="{fill}" style="animation-delay:{delay}s">'
                f"<title>{day['d']}: {day['c']} contribution{'' if day['c'] == 1 else 's'}</title></rect>"
            )

    names = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    labels = []
    previous_month = None
    last_column = -99
    for index, week in enumerate(weeks):
        month = int(week[0]["d"][5:7])
        if month != previous_month and index - last_column >= 4:
            labels.append(
                f'<text x="{x0 + index * step:.1f}" y="74" font-family="{MONO}" font-size="12.5" '
                f'letter-spacing="1.2" fill="{DIM}">{names[month - 1]}</text>'
            )
            last_column = index
        previous_month = month

    legend = []
    lx = PAD + 38
    for shade in RAMP:
        legend.append(f'<rect x="{lx}" y="306" width="11" height="11" rx="2.5" fill="{shade}"/>')
        lx += 16

    # Weekly rhythm: active days per week (0-7), drawn left to right with a live dot.
    active = [sum(1 for day in week if day["c"] > 0) for week in weeks]
    base_y = 276
    top_y = 236
    points = [
        (x0 + i * step + cell / 2, base_y - (value / 7) * (base_y - top_y))
        for i, value in enumerate(active)
    ]
    line = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in points)
    area = line + f" L{points[-1][0]:.1f} {base_y} L{points[0][0]:.1f} {base_y} Z"
    length = sum(
        math.hypot(points[i + 1][0] - points[i][0], points[i + 1][1] - points[i][1])
        for i in range(len(points) - 1)
    )
    last_x, last_y = points[-1]

    return (
        open_svg(
            height,
            f"Contribution map for axs-official with {DATA['total']} contributions across {DATA['activeDays']} active days, "
            "plus the weekly rhythm over the last 52 weeks.",
            "Contributions",
        )
        + f'''  <defs>
    <clipPath id="heatClip"><rect x="{x0 - 2:.1f}" y="{y0 - 2}" width="{width + 4:.1f}" height="{step * 7 + 4:.1f}" rx="4"/></clipPath>
    <linearGradient id="scanGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{BLUE_SOFT}" stop-opacity="0"/>
      <stop offset="0.5" stop-color="{BLUE_SOFT}" stop-opacity=".22"/>
      <stop offset="1" stop-color="{BLUE_SOFT}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="rhythmFill" x1="0" y1="238" x2="0" y2="276" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{BLUE}" stop-opacity=".28"/>
      <stop offset="1" stop-color="{BLUE}" stop-opacity="0"/>
    </linearGradient>
  </defs>
  {frame(height)}
  {header("CONTRIBUTIONS", "LAST 12 MONTHS")}
  {''.join(labels)}
  <g font-family="{MONO}" font-size="12.5" letter-spacing="1" fill="{DIM}">
    <text x="{x0 - 10:.1f}" y="{y0 + step + 9:.1f}" text-anchor="end">MON</text>
    <text x="{x0 - 10:.1f}" y="{y0 + step * 3 + 9:.1f}" text-anchor="end">WED</text>
    <text x="{x0 - 10:.1f}" y="{y0 + step * 5 + 9:.1f}" text-anchor="end">FRI</text>
  </g>
  {''.join(cells)}
  <g clip-path="url(#heatClip)">
    <rect class="scan" x="{x0 - 34:.1f}" y="{y0 - 2}" width="68" height="{step * 7 + 4:.1f}" fill="url(#scanGrad)"/>
  </g>
  <path d="M{PAD} 202H{W - PAD}" stroke="{LINE}"/>
  <text x="{PAD}" y="226" font-family="{MONO}" font-size="12" letter-spacing="1.6" fill="{MUTED}">WEEKLY RHYTHM</text>
  <path d="{area}" fill="url(#rhythmFill)" class="fade" style="animation-delay:.5s"/>
  <path class="draw" d="{line}" stroke="{BLUE_SOFT}" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"
        style="stroke-dasharray:{length:.1f};stroke-dashoffset:{length:.1f}"/>
  <circle class="blink" cx="{last_x:.1f}" cy="{last_y:.1f}" r="3.4" fill="{BLUE}"/>
  <circle cx="{last_x:.1f}" cy="{last_y:.1f}" r="7" stroke="{BLUE}" stroke-opacity=".35"/>
  <text x="{PAD}" y="317" font-family="{MONO}" font-size="12.5" letter-spacing="1.4" fill="{DIM}">LESS</text>
  {''.join(legend)}
  <text x="{PAD + 130}" y="317" font-family="{MONO}" font-size="12.5" letter-spacing="1.4" fill="{DIM}">MORE</text>
</svg>'''
    )


def about():
    height = 268
    facts = [
        ("ROLE", "Full-stack developer"),
        ("FOCUS", "Privacy-first software"),
        ("OPEN TO", "Paid work"),
    ]
    rows = []
    for index, (label, value) in enumerate(facts):
        y = 92 + index * 56
        rows.append(
            f'<text x="560" y="{y}" font-family="{MONO}" font-size="12" letter-spacing="1.4" fill="{DIM}">{label}</text>'
            f'<text x="560" y="{y + 23}" font-family="{SANS}" font-size="15.5" fill="{INK}" fill-opacity=".92">{value}</text>'
        )
        if index < len(facts) - 1:
            rows.append(f'<path d="M560 {y + 34}H{W - PAD}" stroke="{LINE_SOFT}"/>')

    return (
        open_svg(
            height,
            "About A-XS: full-stack developer. Privacy-first software, built end to end. Open to paid work.",
            "About",
        )
        + f'''  {frame(height)}
  {header("ABOUT")}
  <g class="fade">
    {paragraph(PAD, 92, "I take a project end to end: database, API, interface and deploy. React and Next.js most days, Python when there is work worth automating.", size=15, chars=62)}
    {paragraph(PAD, 178, "Privacy decides the shape: no analytics, no cookies, no trackers, no accounts you didn't ask for. Ask and I'll walk you through the code.", size=15, chars=62)}
  </g>
  {''.join(rows)}
</svg>'''
    )


def work():
    height = 326
    items = [
        (
            "This site",
            "NEXT.JS · THREE.JS · TAILWIND",
            "The page you're on. 3D hero, my own contribution data, static build on GitHub Pages.",
        ),
        (
            "GitHub profile",
            "SVG · PYTHON",
            "These cards. A Python script, animated with CSS inside the SVG.",
        ),
        (
            "Everything else",
            "PRIVATE",
            "Scripts, private apps, half-finished ideas. Ask and I'll walk you through one.",
        ),
    ]
    rows = []
    for index, (title, tag, body) in enumerate(items):
        y = 86 + index * 80
        if index:
            rows.append(f'<path d="M{PAD} {y - 24}H{W - PAD}" stroke="{LINE_SOFT}"/>')
        rows.append(
            f'''<g class="rise" style="animation-delay:{round(index * 0.08, 2)}s">
      <text x="{PAD}" y="{y}" font-family="{SANS}" font-size="17" font-weight="600" fill="{INK}">{esc(title)}</text>
      <text x="{PAD}" y="{y + 23}" font-family="{MONO}" font-size="12.5" letter-spacing="1.1" fill="{MUTED}">{esc(tag)}</text>
      {paragraph(330, y - 1, body, size=14, chars=62, line_height=19, color=MUTED)}
    </g>'''
        )

    return (
        open_svg(
            height,
            "Things A-XS has built: this site, the GitHub profile cards, and private full-stack work.",
            "Work",
        )
        + f'''  {frame(height)}
  {header("WORK")}
  {''.join(rows)}
</svg>'''
    )


# What I use, most-used first.
KIT = [
    "python",
    "typescript",
    "javascript",
    "react",
    "nextjs",
    "node",
    "tailwind",
    "three",
    "rust",
    "cpp",
    "sqlite",
    "git",
    "actions",
    "linux",
    "docker",
    "figma",
    "rest",
]

STACK_LABELS = {
    "python": "Python",
    "javascript": "JavaScript",
    "react": "React",
    "nextjs": "Next.js",
    "tailwind": "Tailwind CSS",
    "typescript": "TypeScript",
    "node": "Node.js",
    "git": "Git",
    "three": "Three.js",
    "rust": "Rust",
    "actions": "GitHub Actions",
    "linux": "Linux",
    "sqlite": "SQLite",
    "docker": "Docker",
    "cpp": "C++",
            "figma": "Figma",
    "rest": "REST APIs",
}

BRAND_PILL = {
    "python":        "#3776AB",
    "typescript":    "#3178C6",
    "javascript":    "#F7DF1E",
    "react":         "#61DAFB",
    "nextjs":        "#000000",
    "node":          "#5FA04E",
    "tailwind":      "#06B6D4",
    "three":         "#000000",
    "rust":          "#000000",
    "cpp":           "#00599C",
    "sqlite":        "#003B57",
    "git":           "#F03C2E",
    "actions":       "#2088FF",
    "linux":         "#FCC624",
    "docker":        "#2496ED",
    "figma":         "#F24E1E",
    "rest":          "#8F8F8F",
}


def chip(slug, x, y, w):
    """Autofit monospace chip: name + small brand colour pill cap no wider than `w`."""
    label = STACK_LABELS[slug]
    color = BRAND_PILL[slug]
    # measure approximate width of label at size 11.2 (monospace, ~6.5px/glyph)
    est = len(label) * 6.6 + 14
    use_w = min(w, est) if est > 0 else w
    return (
        f'<g class="rise" style="animation-delay:{(x / (W - PAD * 2)) * 0.18}s">'
        f'<text x="{x + 6}" y="{y}" font-family="{MONO}" font-size="11.2" letter-spacing="0.2" fill="{INK}" fill-opacity="0.92">'
        f"{esc(label)}"
        f'</text>'
        f'<rect x="{x + est - 3}" y="{y - 8}" width="3.2" height="9" rx="1.6" fill="{color}" opacity="0.85"/>'
        f'</g>'
    )


def stack():
    """Compact toolchain panel: 2 columns of chips, one soft pulse accent."""
    COLS = 2
    GAP_X = 24
    GAP_Y = 18
    cell_w = (W - PAD * 2 - GAP_X) / COLS
    top = 74
    panels = []
    for index, slug in enumerate(KIT):
        col, row = index % COLS, index // COLS
        x = PAD + col * (cell_w + GAP_X)
        y = top + row * GAP_Y
        panels.append(chip(slug, x, y, cell_w))

    listing = ", ".join(STACK_LABELS[slug] for slug in KIT)
    rows = (len(KIT) + COLS - 1) // COLS

    return (
        open_svg(
            74 + rows * GAP_Y + 30,
            f"Toolchain: {listing}.",
            "Toolchain",
            extra_css='<style>'
            ' .pulse{animation:pulse 6s cubic-bezier(.5,0,.2,1) infinite}'
            ' @keyframes pulse{'
            ' 0%,100%{opacity:.12;stroke-width:1}'
            ' 50%{opacity:.55;stroke-width:1.6}'
            ' }'
            '</style>',
        )
        + f'''  {frame(74 + rows * GAP_Y + 30)}
  {grid(74 + rows * GAP_Y + 30, 60, 0.05)}
  <text x="{PAD}" y="54" font-family="{MONO}" font-size="13" letter-spacing="2.6" fill="{BLUE_SOFT}">TOOLCHAIN</text>
  <text x="{W - PAD}" y="54" text-anchor="end" font-family="{MONO}" font-size="12" letter-spacing="1.2" fill="{DIM}">{len(KIT)} TOOLS</text>
  <path d="M{PAD} 66H{W - PAD}" stroke="{LINE}"/>
  {''.join(panels)}
  <rect x="{PAD}" y="{74 + rows * GAP_Y + 8}" width="{W - PAD * 2}" height="1.4" class="pulse" fill="none" stroke="{BLUE}" stroke-opacity="0.4"/>
</svg>
    '''
    )


def contact():
    height = 194
    return (
        open_svg(
            height,
            f"Contact axs at {CONTACT_EMAIL} for paid work and business enquiries only. "
            "Every other link lives at axs-official.github.io/links.",
            "Contact",
        )
        + f'''  {frame(height)}
  <text x="{PAD}" y="34" font-family="{MONO}" font-size="13" letter-spacing="2.6" fill="{INK}">CONTACT</text>
  <text x="{W - PAD}" y="34" text-anchor="end" font-family="{MONO}" font-size="12" letter-spacing="1.4" fill="{BLUE_SOFT}">PAID WORK ONLY</text>
  <path d="M{PAD} 48H{W - PAD}" stroke="{LINE}"/>
  <text x="{PAD}" y="92" font-family="{SANS}" font-size="22" font-weight="500" fill="{INK}">{CONTACT_EMAIL}</text>
  <text x="{PAD}" y="118" font-family="{SANS}" font-size="14.5" fill="{MUTED}">Jobs you need built, fixed or automated.</text>
  <text x="{PAD}" y="140" font-family="{SANS}" font-size="13.5" fill="{DIM}">No free support — questions go in GitHub issues.</text>
  <text x="{W - PAD}" y="92" text-anchor="end" font-family="{MONO}" font-size="12.5" fill="{MUTED}">github.com/axs-official</text>
  <text x="{W - PAD}" y="116" text-anchor="end" font-family="{MONO}" font-size="12.5" fill="{DIM}">axs-official.github.io</text>
  <text x="{W - PAD}" y="140" text-anchor="end" font-family="{MONO}" font-size="12" letter-spacing="1.2" fill="{DIM}">FULL-STACK · REMOTE</text>
  <path d="M{PAD} 162H{W - PAD}" stroke="{LINE_SOFT}"/>
  <text x="{PAD}" y="184" font-family="{MONO}" font-size="12.5" letter-spacing="1.2" fill="{DIM}">ALL LINKS · axs-official.github.io/links</text>
</svg>'''
    )


def write(name, content):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    print(f"{path}: {len(content)} bytes")


write("hero-dark.svg", hero())
write("stats.svg", stats())
write("activity.svg", activity())
write("about.svg", about())
write("work.svg", work())
write("stack.svg", stack())
write("contact.svg", contact())


BTN_H = 44


def button(label, width=180):
    """A small pill button for the profile README (linked with markdown around it)."""
    return f'''<svg width="{width}" height="{BTN_H}" viewBox="0 0 {width} {BTN_H}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{html.escape(label)}">
  <title>{esc(label)}</title>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{BTN_H - 1}" rx="{(BTN_H - 1) / 2}" fill="{PANEL}" stroke="#333333"/>
  <text x="{width / 2}" y="27.5" text-anchor="middle" font-family="{MONO}" font-size="12" letter-spacing="1.7" fill="{INK}">{esc(label)}</text>
</svg>'''


write("btn-site.svg", button("VISIT SITE ↗"))
write("btn-links.svg", button("ALL LINKS ↗"))
write("btn-email.svg", button("EMAIL ME ↗"))

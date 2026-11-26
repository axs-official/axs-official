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
RAMP = [ZERO, "#166534", "#22C55E", "#F59E0B", "#EF4444"]

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
            extra_css='<style>'
            ' .breathe{animation:breathe 7s ease-in-out infinite}'
            ' @keyframes breathe{0%,100%{opacity:.10}50%{opacity:.28}}'
            '</style>',
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
    <radialGradient id="halo" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity=".26"/>
      <stop offset=".55" stop-color="#FFFFFF" stop-opacity=".06"/>
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
    </radialGradient>
    <clipPath id="pc"><circle cx="{cx}" cy="{cy}" r="45"/></clipPath>
  </defs>
  {frame(height)}
  {grid(height)}
  {stars(26, 812, height, avoid=[(24, 40, 470, 202), (24, 204, 534, 306), (632, 274, 820, 308)])}
  <circle cx="{cx}" cy="{cy}" r="196" fill="url(#glow)"/>
  <circle class="breathe" cx="{cx}" cy="{cy}" r="132" fill="url(#halo)"/>
  <g>
    <circle class="spin-r" cx="{cx}" cy="{cy}" r="118" stroke="{ACCENT}" stroke-opacity=".16" stroke-width="1" stroke-dasharray="26 12"/>
    <circle class="spin" cx="{cx}" cy="{cy}" r="92" stroke="{LINE}" stroke-width="1" stroke-dasharray="2 6"/>
    <ellipse class="spin-r" cx="{cx}" cy="{cy}" rx="136" ry="36" stroke="{BLUE}" stroke-opacity=".6" stroke-width="1" transform="rotate(-24 {cx} {cy})"/>
    <ellipse class="spin" cx="{cx}" cy="{cy}" rx="158" ry="54" stroke="{ACCENT}" stroke-opacity=".16" stroke-width="1" stroke-dasharray="1 8" transform="rotate(18 {cx} {cy})"/>
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


def terminal():
    """A shell that types a command, decodes it from ASCII, and answers:"""
    height = 268
    command = "echo 83 84 65 89 [80 82 73 86 65 84 69]"
    return (
        open_svg(
            height,
            "Terminal: the command echo 83 84 65 89 [80 82 73 86 65 84 69] is decoded from ASCII "
            "into the words STAY PRIVATE.",
            "Terminal",
            extra_css='<style>'
            ' .type{animation:type 1.8s steps(44,end) .4s both}'
            ' .caret{animation:caret 1.1s steps(1,end) infinite}'
            ' @keyframes type{from{transform:translateX(0)}to{transform:translateX(340px)}}'
            ' @keyframes caret{0%,49%{opacity:1}50%,100%{opacity:0}}'
            '</style>',
        )
        + f'''  {frame(height)}
  {header("TERMINAL", "ASCII DECODE")}
  <rect x="{PAD}" y="66" width="{W - PAD * 2}" height="178" rx="12" fill="#0C0C0C" stroke="{LINE}"/>
  <circle cx="52" cy="86" r="4" fill="#2A2A2A"/>
  <circle cx="68" cy="86" r="4" fill="#2A2A2A"/>
  <circle cx="84" cy="86" r="4" fill="{LIVE}" opacity=".8"/>
  <text x="106" y="90" font-family="{MONO}" font-size="11" letter-spacing="1.6" fill="{DIM}">axs — privacy shell</text>
  <text x="{PAD + 12}" y="124" font-family="{MONO}" font-size="13" fill="{LIVE}">$</text>
  <text x="{PAD + 26}" y="124" font-family="{MONO}" font-size="13" fill="{INK}">{esc(command)}</text>
  <rect class="type" x="{PAD + 26}" y="111" width="330" height="17" fill="#0C0C0C"/>
  <rect class="caret" x="{PAD + 378}" y="112" width="7" height="15" fill="{LIVE}" opacity=".85"/>
  <g class="fade" style="animation-delay:2.1s">
    <text x="{PAD + 12}" y="152" font-family="{MONO}" font-size="12" fill="{DIM}">&gt; ascii.dec(83 84 65 89) + ascii.dec(80 82 73 86 65 84 69)</text>
  </g>
  <g class="rise" style="animation-delay:2.4s">
    <text x="{PAD + 12}" y="198" font-family="{SERIF}" font-size="34" letter-spacing="4" fill="{INK}">STAY PRIVATE</text>
  </g>
  <g class="fade" style="animation-delay:2.9s">
    <text x="{PAD + 12}" y="226" font-family="{MONO}" font-size="11.5" fill="{MUTED}"># 7 bytes in, two words out. No analytics, no cookies, no trackers.</text>
  </g>
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
    height = 272
    facts = [
        ("ROLE", "Full-stack developer"),
        ("FOCUS", "Privacy-first software"),
        ("OPEN TO", "Paid work"),
    ]
    rows = []
    for index, (label, value) in enumerate(facts):
        y = 96 + index * 58
        rows.append(
            f'<text x="566" y="{y}" font-family="{MONO}" font-size="12" letter-spacing="1.4" fill="{DIM}">{label}</text>'
            f'<text x="566" y="{y + 25}" font-family="{SANS}" font-size="16.5" fill="{INK}" fill-opacity=".94">{value}</text>'
            f'<rect class="grow" x="566" y="{y + 39}" width="{W - PAD - 566}" height="1" fill="{LINE}" '
            f'style="animation-delay:{round(0.3 + index * 0.14, 2)}s"/>'
        )

    return (
        open_svg(
            height,
            "About A-XS: full-stack developer. Privacy-first software, built end to end. Open to paid work.",
            "About",
            extra_css='<style>'
            ' .bar{animation:bar 6s ease-in-out infinite}'
            ' @keyframes bar{0%,100%{opacity:.18}50%{opacity:.8}}'
            '</style>',
        )
        + f'''  {frame(height)}
  {header("ABOUT", "A-XS")}
  <rect class="bar" x="{PAD - 12}" y="78" width="2" height="152" rx="1" fill="{BLUE}"/>
  <g class="fade">
    {paragraph(PAD, 96, "I take a project end to end: database, API, interface and deploy. React and Next.js most days, Python when there is work worth automating.", size=15, chars=58)}
    {paragraph(PAD, 170, "Privacy decides the shape: no analytics, no cookies, no trackers, no logins you didn't ask for. Ask and I'll walk you through the code.", size=15, chars=58)}
  </g>
  <g class="fade" style="animation-delay:.45s">
    <text x="{PAD}" y="242" font-family="{MONO}" font-size="11.5" letter-spacing="1.4" fill="{MUTED}">NO ANALYTICS · NO COOKIES · NO TRACKERS</text>
  </g>
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

SHORT_LABEL = {
    "python": "Python",
    "typescript": "TypeScript",
    "javascript": "JavaScript",
    "react": "React",
    "nextjs": "Next.js",
    "node": "Node.js",
    "tailwind": "Tailwind",
    "three": "Three.js",
    "rust": "Rust",
    "cpp": "C++",
    "sqlite": "SQLite",
    "git": "Git",
    "actions": "Actions",
    "linux": "Linux",
    "docker": "Docker",
    "figma": "Figma",
    "rest": "REST",
}

REST_PATH = "M4 9h16M4 9l3.5-3.5M4 9l3.5 3.5M20 15H4M20 15l-3.5-3.5M20 15l-3.5 3.5"


def stack():
    """Toolchain constellation: brand icons drifting on an animated mesh."""
    height = 272
    size = 44
    rows = (KIT[:9], KIT[9:])
    centres = (122, 208)
    jitter = (-10, 7, -14, 3, -6, 12, -12, 5, -8)

    def spread(count, inset=0.0):
        left = PAD + size / 2 + inset
        right = W - PAD - size / 2 - inset
        if count == 1:
            return [(left + right) / 2]
        step = (right - left) / (count - 1)
        return [left + i * step for i in range(count)]

    top_x = spread(len(rows[0]))
    bottom_x = spread(len(rows[1]), inset=(top_x[1] - top_x[0]) / 2)
    first = [(x, centres[0] + jitter[i % len(jitter)]) for i, x in enumerate(top_x)]
    second = [(x, centres[1] + jitter[(i + 1) % len(jitter)]) for i, x in enumerate(bottom_x)]

    mesh = []
    for line in (first, second):
        for (ax, ay), (bx, by) in zip(line, line[1:]):
            mesh.append(
                f'<path class="flow" d="M{ax:.1f} {ay:.1f}L{bx:.1f} {by:.1f}" stroke="#3A3A3A" '
                f'stroke-width="1" style="animation-delay:{round(-random.uniform(0, 5), 2)}s"/>'
            )
    for i, (bx, by) in enumerate(second):
        for j in (i - 1, i, i + 1):
            if 0 <= j < len(first):
                ax, ay = first[j]
                mesh.append(
                    f'<path class="flow" d="M{ax:.1f} {ay:.1f}L{bx:.1f} {by:.1f}" stroke="#2F2F2F" '
                    f'stroke-width="1" stroke-opacity=".9" '
                    f'style="animation-delay:{round(-random.uniform(0, 5), 2)}s"/>'
                )

    nodes = []
    for line, slugs in zip((first, second), rows):
        for (cx, cy), slug in zip(line, slugs):
            if slug in ICONS:
                colour = brand(ICONS[slug]["hex"])
                icon = f'<path d="{ICONS[slug]["path"]}" fill="{colour}"/>'
            else:
                colour = "#C4C4C4"
                icon = (
                    f'<path d="{REST_PATH}" fill="none" stroke="{colour}" stroke-width="1.5" '
                    f'stroke-linecap="round" stroke-linejoin="round"/>'
                )
            label = SHORT_LABEL.get(slug, STACK_LABELS[slug])
            label_w = len(label) * 6.3 + 10
            nodes.append(
                f'<g class="node" style="animation-delay:{round(-random.uniform(0, 7.5), 2)}s">'
                f'<rect x="{cx - size / 2:.1f}" y="{cy - size / 2:.1f}" width="{size}" height="{size}" '
                f'rx="13" fill="{PANEL}" stroke="{LINE}"/>'
                f'<rect x="{cx - size / 2:.1f}" y="{cy - size / 2:.1f}" width="{size}" height="{size}" '
                f'rx="13" fill="{colour}" opacity=".09"/>'
                f'<g transform="translate({cx - 11:.1f} {cy - 11:.1f}) scale(.92)">{icon}</g>'
                f'</g>'
                f'<rect x="{cx - label_w / 2:.1f}" y="{cy + size / 2 + 7:.1f}" width="{label_w:.1f}" '
                f'height="15" rx="4" fill="{BG}" opacity=".9"/>'
                f'<text x="{cx:.1f}" y="{cy + size / 2 + 19:.1f}" text-anchor="middle" '
                f'font-family="{MONO}" font-size="10.5" letter-spacing=".4" fill="{MUTED}">{esc(label)}</text>'
            )

    listing = ", ".join(STACK_LABELS[slug] for slug in KIT)

    return (
        open_svg(
            height,
            f"Toolchain: {listing}.",
            "Toolchain",
            extra_css='<style>'
            ' .flow{stroke-dasharray:3 9;animation:flow 5s linear infinite}'
            ' .node{animation:drift 7.5s ease-in-out infinite}'
            ' @keyframes flow{to{stroke-dashoffset:-48}}'
            ' @keyframes drift{0%,100%{transform:translateY(-2.5px)}50%{transform:translateY(2.5px)}}'
            '</style>',
        )
        + f'''  {frame(height)}
  {header("TOOLCHAIN", f"{len(KIT)} TOOLS")}
  {''.join(mesh)}
  {''.join(nodes)}
</svg>'''
    )


def contact():
    height = 210
    return (
        open_svg(
            height,
            f"Contact axs at {CONTACT_EMAIL} for paid work and business enquiries only. "
            "Every other link lives at axs-official.github.io/links.",
            "Contact",
        )
        + f'''  {frame(height)}
  <text x="{PAD}" y="38" font-family="{MONO}" font-size="13" letter-spacing="2.6" fill="{BLUE_SOFT}">CONTACT</text>
  <text x="{W - PAD}" y="38" text-anchor="end" font-family="{MONO}" font-size="12" letter-spacing="1.4" fill="{INK}">PAID WORK ONLY</text>
  <path d="M{PAD} 52H{W - PAD}" stroke="{LINE}"/>
  <text x="{PAD}" y="98" font-family="{SANS}" font-size="25" font-weight="500" fill="{INK}">{CONTACT_EMAIL}</text>
  <rect class="grow" x="{PAD}" y="107" width="356" height="1.6" rx="1" fill="{BLUE}" opacity=".5" style="animation-delay:.4s"/>
  <text x="{PAD}" y="132" font-family="{SANS}" font-size="15" fill="{MUTED}">Jobs you need built, fixed or automated.</text>
  <text x="{PAD}" y="155" font-family="{SANS}" font-size="13.5" fill="{DIM}">No free support — questions go in GitHub issues.</text>
  <text x="{W - PAD}" y="96" text-anchor="end" font-family="{MONO}" font-size="12.5" fill="{MUTED}">github.com/axs-official</text>
  <text x="{W - PAD}" y="120" text-anchor="end" font-family="{MONO}" font-size="12.5" fill="{DIM}">axs-official.github.io</text>
  <text x="{W - PAD}" y="144" text-anchor="end" font-family="{MONO}" font-size="12" letter-spacing="1.2" fill="{DIM}">FULL-STACK · REMOTE</text>
  <path d="M{PAD} 176H{W - PAD}" stroke="{LINE_SOFT}"/>
  <text x="{PAD}" y="199" font-family="{MONO}" font-size="12.5" letter-spacing="1.2" fill="{DIM}">ALL LINKS · axs-official.github.io/links</text>
</svg>'''
    )


def write(name, content):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    print(f"{path}: {len(content)} bytes")


write("hero-dark.svg", hero())
write("terminal.svg", terminal())
write("activity.svg", activity())
write("about.svg", about())
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

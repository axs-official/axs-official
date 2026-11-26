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
ZERO = "#171717"
# Quiet days sit in red, the busiest days turn green: the warm end is the low end.
RAMP = [ZERO, "#8B2C2C", "#C2410C", "#E0A020", "#3FD863"]

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


def ring_point(cx, cy, rx, ry, deg, tilt):
    """A point on an ellipse rotated by `tilt`, in SVG (y-down) space."""
    a = math.radians(deg)
    phi = math.radians(tilt)
    x = cx + rx * math.cos(a) * math.cos(phi) - ry * math.sin(a) * math.sin(phi)
    y = cy + rx * math.cos(a) * math.sin(phi) + ry * math.sin(a) * math.cos(phi)
    return x, y


def orbit_css(name, cx, cy, rx, ry, tilt, steps=24, back=0.3):
    """Keyframe track that walks a satellite around a tilted ellipse, dimming it behind."""
    frames = []
    for i in range(steps):
        deg = i * 360.0 / steps
        x, y = ring_point(cx, cy, rx, ry, deg, tilt)
        opacity = 1 if math.sin(math.radians(deg)) > 0 else back
        frames.append(
            f"{i * 100 / steps:.2f}%{{transform:translate({x - cx:.1f}px,{y - cy:.1f}px);opacity:{opacity}}}"
        )
    return f"@keyframes {name}:" + ",".join(frames)


def hero():
    height = 320
    cx, cy = 660, 152

    ring_rx, ring_ry, ring_tilt = 150, 40, -22
    sx, sy = ring_point(cx, cy, ring_rx, ring_ry, 0, ring_tilt)
    ex, ey = ring_point(cx, cy, ring_rx, ring_ry, 180, ring_tilt)
    ring_back = f"M{sx:.1f} {sy:.1f}A{ring_rx} {ring_ry} {ring_tilt} 0 0 {ex:.1f} {ey:.1f}"
    ring_front = f"M{sx:.1f} {sy:.1f}A{ring_rx} {ring_ry} {ring_tilt} 0 1 {ex:.1f} {ey:.1f}"

    outer_rx, outer_ry, outer_tilt = 174, 60, 16
    osx, osy = ring_point(cx, cy, outer_rx, outer_ry, 0, outer_tilt)
    oex, oey = ring_point(cx, cy, outer_rx, outer_ry, 180, outer_tilt)
    outer_back = f"M{osx:.1f} {osy:.1f}A{outer_rx} {outer_ry} {outer_tilt} 0 0 {oex:.1f} {oey:.1f}"
    outer_front = f"M{osx:.1f} {osy:.1f}A{outer_rx} {outer_ry} {outer_tilt} 0 1 {oex:.1f} {oey:.1f}"

    meridians = "".join(
        f'<ellipse cx="{cx + dx}" cy="{cy}" rx="12" ry="45"/>' for dx in range(-66, 67, 22)
    )
    latitudes = "".join(
        f'<path d="M{cx - math.sqrt(45 ** 2 - dy ** 2):.1f} {cy + dy}'
        f'H{cx + math.sqrt(45 ** 2 - dy ** 2):.1f}"/>'
        for dy in (-30, -15, 0, 15, 30)
    )

    moon_css = (
        orbit_css("moonA", cx, cy, ring_rx, ring_ry, ring_tilt, 24, 0.28)
        + orbit_css("moonB", cx, cy, outer_rx, outer_ry, outer_tilt, 24, 0.2)
    )

    return (
        open_svg(
            height,
            "A-XS, full-stack developer. Privacy-first software, built end to end.",
            "A-XS — profile",
            extra_css="<style>"
            " .breathe{animation:breathe 7s ease-in-out infinite}"
            " .ringflow{animation:ringflow 11s linear infinite}"
            " .surface{animation:surface 26s linear infinite}"
            " .moonA{animation:moonA 26s linear infinite}"
            " .moonB{animation:moonB 58s linear infinite}"
            " @keyframes breathe{0%,100%{opacity:.10}50%{opacity:.26}}"
            " @keyframes ringflow{to{stroke-dashoffset:-120}}"
            " @keyframes surface{to{transform:translateX(-22px)}}"
            + moon_css
            + "</style>",
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
    <linearGradient id="rim" x1="{cx - 42}" y1="{cy - 44}" x2="{cx + 26}" y2="{cy + 40}" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity=".6"/>
      <stop offset=".62" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity=".13"/>
      <stop offset="0.6" stop-color="#FFFFFF" stop-opacity=".03"/>
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="planet" cx="0.33" cy="0.27" r="0.9">
      <stop offset="0" stop-color="#F4F4F4"/>
      <stop offset="0.35" stop-color="#A8A8A8"/>
      <stop offset="0.72" stop-color="#4A4A4A"/>
      <stop offset="1" stop-color="#101010"/>
    </radialGradient>
    <radialGradient id="term" cx="0.76" cy="0.8" r="0.62">
      <stop offset="0" stop-color="#000000" stop-opacity=".62"/>
      <stop offset="1" stop-color="#000000" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="spec" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity=".5"/>
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
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
  {stars(26, 812, height, avoid=[(24, 40, 470, 202), (24, 204, 534, 306), (470, 60, 830, 250)])}
  <circle cx="{cx}" cy="{cy}" r="196" fill="url(#glow)"/>
  <circle class="breathe" cx="{cx}" cy="{cy}" r="132" fill="url(#halo)"/>
  <circle class="spin-r" cx="{cx}" cy="{cy}" r="122" stroke="{ACCENT}" stroke-opacity=".14" stroke-width="1" stroke-dasharray="26 14"/>
  <circle class="spin" cx="{cx}" cy="{cy}" r="96" stroke="{LINE}" stroke-width="1" stroke-dasharray="2 6"/>
  <path class="ringflow" d="{outer_back}" stroke="{ACCENT}" stroke-opacity=".18" stroke-width="1" stroke-dasharray="2 9"/>
  <path class="ringflow" d="{ring_back}" stroke="{ACCENT}" stroke-opacity=".22" stroke-width="1.4"/>
  <path class="ringflow" d="{ring_back}" stroke="{ACCENT}" stroke-opacity=".5" stroke-width="1" stroke-dasharray="7 13"/>
  <g transform="translate({cx} {cy})">
    <g class="moonB">
      <circle r="6" fill="{ACCENT}" opacity=".14"/>
      <circle r="1.9" fill="{ACCENT}"/>
    </g>
  </g>
  <g>
    <circle cx="{cx}" cy="{cy}" r="47" fill="none" stroke="{ACCENT}" stroke-opacity=".05" stroke-width="9"/>
    <circle cx="{cx}" cy="{cy}" r="45" fill="url(#planet)"/>
    <g clip-path="url(#pc)">
      <g class="surface" stroke="{ACCENT}" stroke-opacity=".16" stroke-width="1" fill="none">
        {meridians}
      </g>
      <g stroke="{ACCENT}" stroke-opacity=".10" stroke-width="1" fill="none">
        {latitudes}
      </g>
      <circle cx="{cx}" cy="{cy}" r="45" fill="url(#term)"/>
    </g>
    <ellipse cx="{cx - 16}" cy="{cy - 19}" rx="14" ry="8.5" fill="url(#spec)" transform="rotate(-28 {cx - 16} {cy - 19})"/>
    <circle cx="{cx}" cy="{cy}" r="45" fill="none" stroke="url(#rim)" stroke-width="1.1"/>
  </g>
  <path class="ringflow" d="{outer_front}" stroke="{ACCENT}" stroke-opacity=".22" stroke-width="1" stroke-dasharray="2 9"/>
  <path d="{ring_front}" stroke="{BLUE}" stroke-opacity=".7" stroke-width="1.3"/>
  <g transform="translate({cx} {cy})">
    <g class="moonA">
      <circle r="9" fill="{ACCENT}" opacity=".16"/>
      <circle r="3" fill="{ACCENT}"/>
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


# %%terminal
LOOP = 9.6  # one full run of the terminal, seconds
OUT_START = 8.4  # output starts clearing
OUT_END = 9.0  # output gone


def _frames(name, stops):
    body = "".join(f"{round(at, 2):g}%{{{decl}}}" for at, decl in stops)
    return f" @keyframes {name}{{{body}}}"


def _at(seconds):
    return round(seconds / LOOP * 100, 2)


def _fade(name, start, dur=0.36, rise=0):
    """A block that appears at `start` and clears before the loop restarts."""
    if rise:
        hidden = f"opacity:0;transform:translateY({rise}px)"
        shown = "opacity:1;transform:translateY(0)"
        gone = "opacity:0;transform:translateY(0)"
    else:
        hidden, shown, gone = "opacity:0", "opacity:1", "opacity:0"
    return _frames(
        name,
        [
            (0, hidden),
            (_at(start), hidden),
            (_at(start + dur), shown),
            (_at(OUT_START), shown),
            (_at(OUT_END), gone),
            (100, gone),
        ],
    )


def _play(name, easing="linear"):
    return f'style="animation:{name} {LOOP}s {easing} infinite"'


def terminal():
    """A shell that types the command, presses Enter, decodes it — then runs again."""
    height = 306
    command = "echo 83 84 65 89 [80 82 73 86 65 84 69]"
    chars = len(command)
    size = 13
    advance = 7.8
    text_x = 64
    run = round(chars * advance, 1)  # forced with textLength, so the mask lines up exactly
    panel_y, panel_h = 64, 228
    type_start, type_end = 0.6, 2.3

    css = [
        # The cover slides right in character-sized steps, uncovering the line; the caret
        # rides its left edge. At the reset it slides back and wipes the command.
        _frames(
            "tmove",
            [
                (0, "transform:translateX(0)"),
                (_at(type_start), "transform:translateX(0)"),
                (_at(type_end), f"transform:translateX({run}px)"),
                (_at(9.0), f"transform:translateX({run}px)"),
                (_at(9.05), "transform:translateX(0)"),
                (100, "transform:translateX(0)"),
            ],
        ),
        # Solid while typing, gone once Enter lands.
        _frames(
            "tbar",
            [
                (0, "opacity:1"),
                (_at(type_end + 0.02), "opacity:1"),
                (_at(type_end + 0.08), "opacity:0"),
                (_at(9.02), "opacity:0"),
                (_at(9.04), "opacity:1"),
                (100, "opacity:1"),
            ],
        ),
        _frames(
            "lrule",
            [
                (0, "transform:scaleX(0)"),
                (_at(3.02), "transform:scaleX(0)"),
                (_at(3.32), "transform:scaleX(1)"),
                (_at(OUT_START), "transform:scaleX(1)"),
                (_at(OUT_END), "transform:scaleX(0)"),
            ],
        ),
    ]
    for name, start in (
        ("ld1", 2.5),
        ("ld2", 2.68),
        ("lhead", 2.86),
        ("lnote", 3.16),
        ("lprompt", 3.34),
        ("lsession", 2.94),
        ("lrow1", 3.02),
        ("lrow2", 3.1),
        ("lrow3", 3.18),
        ("lrow4", 3.26),
        ("lrow5", 3.34),
    ):
        css.append(_fade(name, start))
    css.append(_fade("lenter", 2.34, dur=0.18))

    return (
        open_svg(
            height,
            "Terminal: the command echo 83 84 65 89 [80 82 73 86 65 84 69] is decoded from ASCII "
            "into the words STAY PRIVATE.",
            "Terminal",
            extra_css="<style>"
            + "".join(css)
            + " .mg{transform-box:fill-box;transform-origin:left center}"
            + "</style>",
        )
        + f'''  <defs>
    <linearGradient id="bar" x1="0" y1="{panel_y}" x2="0" y2="{panel_y + 34}" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#161616"/>
      <stop offset="1" stop-color="#101010"/>
    </linearGradient>
  </defs>
  {frame(height)}
  {header("TERMINAL", "ASCII DECODE")}
  <rect x="{PAD}" y="{panel_y}" width="{W - PAD * 2}" height="{panel_h}" rx="12" fill="#0B0B0B" stroke="{LINE}"/>
  <rect x="{PAD}" y="{panel_y}" width="{W - PAD * 2}" height="32" rx="12" fill="url(#bar)"/>
  <rect x="{PAD}" y="{panel_y + 20}" width="{W - PAD * 2}" height="12" fill="url(#bar)"/>
  <path d="M{PAD} {panel_y + 32}H{W - PAD}" stroke="{LINE_SOFT}"/>

  <g>
    <circle cx="54" cy="{panel_y + 16}" r="7.4" fill="#FF5F57" opacity=".16"/>
    <circle cx="54" cy="{panel_y + 16}" r="4.4" fill="#FF5F57"/>
    <circle cx="72" cy="{panel_y + 16}" r="7.4" fill="#FEBC2E" opacity=".16"/>
    <circle cx="72" cy="{panel_y + 16}" r="4.4" fill="#FEBC2E"/>
    <circle cx="90" cy="{panel_y + 16}" r="7.4" fill="#28C840" opacity=".16"/>
    <circle cx="90" cy="{panel_y + 16}" r="4.4" fill="#28C840"/>
  </g>
  <text x="110" y="{panel_y + 20}" font-family="{MONO}" font-size="11.5" letter-spacing=".6" fill="{DIM}">axs — privacy shell</text>
  <text x="{W - PAD - 12}" y="{panel_y + 20}" text-anchor="end" font-family="{MONO}" font-size="10.5" letter-spacing="1.6" fill="#5E5E5E">TTY / 01</text>

  <text x="46" y="124" font-family="{MONO}" font-size="{size}" font-weight="700" fill="{LIVE}">$</text>
  <text x="{text_x}" y="124" font-family="{MONO}" font-size="{size}" fill="{INK}"
        textLength="{run}" lengthAdjust="spacing">{esc(command)}</text>
  <g style="animation:tmove {LOOP}s steps({chars},end) infinite">
    <rect x="{text_x}" y="111" width="{run}" height="18" fill="#0B0B0B"/>
    <g style="animation:tbar {LOOP}s linear infinite">
      <rect x="{text_x}" y="112" width="7.6" height="14.5" rx="1" fill="{LIVE}"/>
    </g>
  </g>
  <g {_play("lenter")}>
    <rect x="382" y="113" width="24" height="17" rx="4" fill="#151515" stroke="#2E2E2E"/>
    <text x="394" y="125.5" text-anchor="middle" font-family="{MONO}" font-size="11.5" fill="{DIM}">↵</text>
  </g>

  <g {_play("ld1")}>
    <text x="46" y="152" font-family="{MONO}" font-size="12.5" fill="#4A4A4A">├</text>
    <text x="{text_x}" y="152" font-family="{MONO}" font-size="12.5" fill="{DIM}">83 84 65 89</text>
    <text x="164" y="152" font-family="{MONO}" font-size="12.5" fill="#4A4A4A">→</text>
    <text x="184" y="152" font-family="{MONO}" font-size="12.5" letter-spacing="3" fill="{INK}" fill-opacity=".92">S T A Y</text>
  </g>
  <g {_play("ld2")}>
    <text x="46" y="172" font-family="{MONO}" font-size="12.5" fill="#4A4A4A">└</text>
    <text x="{text_x}" y="172" font-family="{MONO}" font-size="12.5" fill="{DIM}">80 82 73 86 65 84 69</text>
    <text x="228" y="172" font-family="{MONO}" font-size="12.5" fill="#4A4A4A">→</text>
    <text x="248" y="172" font-family="{MONO}" font-size="12.5" letter-spacing="3" fill="{INK}" fill-opacity=".92">P R I V A T E</text>
  </g>

  <g {_play("lhead")}>
    <text x="46" y="218" font-family="{SERIF}" font-size="34" letter-spacing="4.5" fill="{INK}">STAY PRIVATE</text>
  </g>
  <rect class="mg" x="46" y="229" width="292" height="1.4" fill="url(#rule)"
        style="animation:lrule {LOOP}s linear infinite"/>

  <g {_play("lnote")}>
    <text x="46" y="252" font-family="{MONO}" font-size="11.5" fill="{MUTED}"># 7 bytes in, two words out. No analytics, no cookies, no trackers.</text>
  </g>
  <g {_play("lprompt")}>
    <text x="46" y="274" font-family="{MONO}" font-size="{size}" font-weight="700" fill="{LIVE}">$</text>
    <rect class="caret-blink" x="{text_x}" y="261" width="7.6" height="15" rx="1" fill="{INK}" opacity=".9"/>
  </g>

  <path d="M588 110V276" stroke="#2C2C2C"/>
  <g {_play("lsession")}>
    <text x="612" y="128" font-family="{MONO}" font-size="10.5" letter-spacing="2.2" fill="{DIM}">SESSION</text>
  </g>
  <g font-family="{MONO}" font-size="12" letter-spacing=".4">
    <g {_play("lrow1")}>
      <text x="612" y="156" fill="#A8A8A8">shell</text>
      <text x="{W - PAD - 16}" y="156" text-anchor="end" fill="{INK}" fill-opacity=".95">zsh</text>
    </g>
    <g {_play("lrow2")}>
      <text x="612" y="182" fill="#A8A8A8">bytes</text>
      <text x="{W - PAD - 16}" y="182" text-anchor="end" fill="{INK}" fill-opacity=".95">7</text>
    </g>
    <g {_play("lrow3")}>
      <text x="612" y="208" fill="#A8A8A8">chars</text>
      <text x="{W - PAD - 16}" y="208" text-anchor="end" fill="{INK}" fill-opacity=".95">12</text>
    </g>
    <g {_play("lrow4")}>
      <text x="612" y="234" fill="#A8A8A8">trackers</text>
      <text x="{W - PAD - 16}" y="234" text-anchor="end" fill="{LIVE}">0</text>
    </g>
    <g {_play("lrow5")}>
      <text x="612" y="260" fill="#A8A8A8">cookies</text>
      <text x="{W - PAD - 16}" y="260" text-anchor="end" fill="{LIVE}">0</text>
    </g>
  </g>
</svg>'''
    )


# %% Undertale sprites
# Pixel maps lifted from the game's own sprite files (spr_maincharar_0, spr_sans_d_0,
# spr_heart_0, spr_gasterblaster_0) so Frisk and Sans look exactly as they do in the game.
FRISK_COLOURS = {"a": "#3D120E", "b": "#FFC90E", "c": "#67A4E0", "d": "#E607F8"}
FRISK_PX = (
    "....aaaaaaaaa....",
    "...aaaaaaaaaaaa..",
    "..aaaaaaaaaaaaaa.",
    ".aaaaaaaaaaaaaaaa",
    ".aaaaaaaaaaaaaaaa",
    "aaaaaaaaaaababaaa",
    "aaaaaaaaaabbabaa.",
    "aaaaaaaaaabbbbba.",
    "aaaaaabbaabbbbba.",
    "aaaaaabbbabbaaba.",
    "aaaaaaabbabbbbbba",
    "aaaaaaaabbbbbbbba",
    ".aaaaaaaabbbbbaaa",
    ".a.aaaaaabbbbbba.",
    "....a.aabbaaaaa..",
    ".......abba......",
    ".......aaaa......",
    "......aacaaa.....",
    ".....acacccca....",
    ".....adacadda....",
    ".....acacaacca...",
    ".....adaabbada...",
    ".....accabbaca...",
    ".....acccaacca...",
    ".....aaccccca....",
    "....aaaaa.aaa.aa.",
    "....aaaa..aaaaa..",
    ".....aaaa..aaa...",
)

SANS_COLOURS = {"a": "#000000", "b": "#FFFFFF", "c": "#4782C9", "d": "#BDC0C9"}
SANS_PX = (
    ".......aaaaaaaaa.......",
    ".....aabbbbbbbbbaa.....",
    "....abbbbbbbbbbbbba....",
    "....abbbbbbbbbbbbba....",
    "...abbbbbbbbbbbbbbba...",
    "...abbaaabbbbbaaabba...",
    "...abbaaabbbbbaaabba...",
    "...abbaaabbabbaaabba...",
    "....abbbbbaaabbbbba....",
    "...aababbbbbbbbbabaa...",
    "...abbaaaaaaaaaaabba...",
    "...abbbabababababbba...",
    "....aabbaaaaaaabbaa....",
    "...aaaaabbbbbbbaaaaa...",
    "..acaaaaaaaaaaaaaaaca..",
    ".aacaddabbbabbbaddacaa.",
    ".acccaddaaabaaaddaccca.",
    "accaacaaabbabbaaacaacca",
    "accccaccabbbbbaccacccca",
    "acccccacaabbbaacaccccca",
    ".acccaccabbbbbaccaccca.",
    "..aacaccaaaaaaaccacaa..",
    "...aaaccaaaaaaaccaaa...",
    "....aaaaaaaaaaaaaaa....",
    "....aaaaaaaaaaaaaaa....",
    ".....aaaaaaaaaaaaa.....",
    ".....addddaaaaaaaa.....",
    "....addddaa.abbbba.....",
    "....aaaaaa..abbbbba....",
    "............aaaaaaa....",
)

SOUL_COLOURS = {"a": "#FF3B3B"}
HEART_PX = (
    "..aa........aa..",
    ".aaaaa....aaaaa.",
    "aaaaaaa..aaaaaaa",
    "aaaaaaa..aaaaaaa",
    "aaaaaaaaaaaaaaaa",
    "aaaaaaaaaaaaaaaa",
    "aaaaaaaaaaaaaaaa",
    "aaaaaaaaaaaaaaaa",
    "aaaaaaaaaaaaaaaa",
    "aaaaaaaaaaaaaaaa",
    "..aaaaaaaaaaaa..",
    "..aaaaaaaaaaaa..",
    "....aaaaaaaa....",
    "....aaaaaaaa....",
    "......aaaa......",
    "......aaaa......",
)

BLASTER_COLOURS = {"a": "#000000", "b": "#FFFFFF"}
BLASTER_PX = (
    ".....................aa....................",
    "....................abba...................",
    "....................abba...................",
    "....................abba...................",
    "...................abbbba..................",
    ".........aa.......abbbbbba.......aa........",
    "........abba.....abbbbbbbba.....abba.......",
    ".......abba....aabbbbbbbbbbaa....abba......",
    "......abba...aabbbbbbbbbbbbbbaa...abba.....",
    ".....abba..aabbbbbbbbbbbbbbbbbbaa..abba....",
    "....abbba.abbbbbbbbbbbbbbbbbbbbbba.abbba...",
    "....abba.abbbbbbbbbbbbbbbbbbbbbbbba.abba...",
    "....abbaabbbbbbbbbbbbaabbbbbbbbbbbbaabba...",
    "...abbbbbbbbbbbbbbbbbaabbbbbbbbbbbbbbbbba..",
    "...abbbbbbbbbbbbbbbbbaabbbbbbbbbbbbbbbbba..",
    "..abbbbbbbbbbbbbbbbbbaabbbbbbbbbbbbbbbbbba.",
    "..abbbbbbbbbbbbbbbbbbaabbbbbbbbbbbbbbbbbba.",
    ".abbbbbbbbbbbbbbbbbbbaabbbbbbbbbbbbbbbbbbba",
    ".abbbbbbbabbbbbbbbbbbaabbbbbbbbbbbabbbbbbba",
    ".abbbbbbabbbbbbbbbbbbaabbbbbbbbbbbbabbbbbba",
    ".abbbbbaabbbbbbbbbbbbaabbbbbbbbbbbbaabbbbba",
    ".abbbbbaabbbbbbbbbbbbaabbbbbbbbbbbbaabbbbba",
    "..abbbbabbbaaabbbbbbbaabbbbbbbaaabbbabbbba.",
    "..abbbbabba...abbbbbbaabbbbbba...abbabbbba.",
    "...abbbabba..aaabbbbbaabbbbba....abbabbba..",
    "....abbaaba.abbaabbbbaabbbba.....abaabba...",
    "....abbaabaabbbbabbbbaabbbba.....abaabba...",
    "....abbaabaabbbbabbbbaabbbba.....abaabba...",
    "....abbaabbabbbbabbbbaabbbba....abbaabba...",
    ".....abaabbabbbbaabbbaabbba.....abbaaba....",
    ".....abbaabaabbbaabbbaabbba....aabaabba....",
    ".....abbaabbbaaaaabbbaabbbaaaaabbbaabba....",
    ".....abba.abbbbbbbbba..abbbbbbbbba.abba....",
    "..aa..aba.abbbbbbbbba..abbbbbbbbba.aba..aa.",
    ".abba.aba.abbbbbbbba....abbbbbbbba.aba.abba",
    "..aabaabbaabbbbbbbba....abbbbbbbbaabbaabaa.",
    "...abbabbaababbbbbba....abbbbbbabaabbabba..",
    "...abbbbbbababbbbbba....abbbbbbababbbbbba..",
    "...abbbbbbba.abbbbbbaaaabbbbbba.abbbbbbba..",
    "....abbbbbba.ababbbbbbbbbbbbaba.abbbbbba...",
    "....abbbbbba.ababbbbbbbbbbbbaba.abbbbbba...",
    ".....abbbbba.abababbbaabbbababa.abbbbba....",
    ".....abbbbba.abaa.aba..aba.aaba.abbbbba....",
    "......abbbba.aba..aba..aba..aba.abbbba.....",
    "......abbbba.aba..aba..aba..aba.abbbba.....",
    "......abbbba..a..aba....aba..a..abbbba.....",
    "......abbba......aba....aba......abbba.....",
    ".aa.a.abbba.......a......a.......abbba.a.aa",
    "abbabaabba........................abbaababb",
    ".ababaabba........................abbaababa",
    ".abababbba........................abbbababa",
    "..abbabbba........................abbbabba.",
    "..abbbbbba........................abbbbbba.",
    "...abbbbba........................abbbbba..",
    "...abbbbba........................abbbbba..",
    "...abbbba..........................abbbba..",
    "....aaaa............................aaaa...",
)


BONE_COLOURS = {"#": "#FFFFFF"}
BONE_PX = (
    ".##....##.",
    "####..####",
    "##########",
    "##########",
    ".########.",
    ".########.",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    ".########.",
    ".########.",
    "##########",
    "##########",
    "####..####",
    ".##....##.",
)


def sprite(rows, x, y, unit, palette):
    """Pixel map -> one rect per same-colour block, runs merged both ways, so sprites stay small."""
    assert len({len(row) for row in rows}) == 1, "sprite rows must be equal width"
    height, width = len(rows), len(rows[0])
    used = [[False] * width for _ in range(height)]
    parts = []
    for r in range(height):
        for c in range(width):
            ch = rows[r][c]
            if ch == "." or used[r][c]:
                continue
            c2 = c
            while c2 < width and rows[r][c2] == ch and not used[r][c2]:
                c2 += 1
            r2 = r + 1
            while r2 < height and all(rows[r2][k] == ch and not used[r2][k] for k in range(c, c2)):
                r2 += 1
            for rr in range(r, r2):
                for cc in range(c, c2):
                    used[rr][cc] = True
            parts.append(
                f'<rect x="{c * unit:.2f}" y="{r * unit:.2f}" width="{(c2 - c) * unit:.2f}" '
                f'height="{(r2 - r) * unit:.2f}" fill="{palette[ch]}"/>'
            )
    body = "".join(parts)
    return f'<g transform="translate({x:.1f} {y:.1f})" shape-rendering="crispEdges">{body}</g>'


SCENE_CSS = (
    "<style>"
    " .friskHop{animation:friskHop 12s linear infinite}"
    " .sansBob{animation:sansBob 3.8s ease-in-out infinite}"
    " .eye{animation:eye 12s linear infinite;opacity:0}"
    " .soulSlide{animation:soulSlide 12s linear infinite}"
    " .soulHop{animation:soulHop 12s linear infinite}"
    " .soulBob{animation:soulBob 1.5s ease-in-out infinite}"
    " .soulHurt{animation:soulHurt 12s linear infinite;opacity:0}"
    " .bone{animation:boneSlide 12s linear infinite;opacity:0}"
    " .boneL{animation:boneSlideL 12s linear infinite;opacity:0}"
    " .blasterWrap{animation:blasterIn 12s linear infinite;opacity:0}"
    " .beam{animation:beamShot 12s linear infinite;opacity:0;stroke-dasharray:100}"
    " .beamFlash{animation:beamFlash 12s linear infinite;opacity:0}"
    " .hpBar{animation:hpBar 12s linear infinite;transform-box:fill-box;transform-origin:0 50%}"
    " .hpN1{animation:hpN1 12s linear infinite}"
    " .hpN2{animation:hpN2 12s linear infinite;opacity:0}"
    " .hpN3{animation:hpN3 12s linear infinite;opacity:0}"
    " .hpN4{animation:hpN4 12s linear infinite;opacity:0}"
    " @keyframes friskHop{0%,50.5%{transform:translateY(0)}"
    "52%{transform:translateY(-6px)}53.5%{transform:translateY(-16px)}"
    "55.5%{transform:translateY(-16px)}57%{transform:translateY(-6px)}"
    "58.5%,100%{transform:translateY(0)}}"
    " @keyframes soulHop{0%,14%{transform:translateY(0)}"
    "15%{transform:translateY(-10px)}16.5%{transform:translateY(-20px)}"
    "19.5%{transform:translateY(-20px)}20.5%{transform:translateY(-10px)}"
    "21.5%,22.5%{transform:translateY(0)}"
    "23.5%{transform:translateY(-20px)}26%{transform:translateY(-20px)}"
    "27%{transform:translateY(-8px)}28%,100%{transform:translateY(0)}}"
    " @keyframes soulSlide{0%,29.6%{transform:translateX(0)}"
    "30.2%{transform:translateX(-6px)}32.4%{transform:translateX(-6px)}"
    "34%{transform:translateX(0)}51.6%{transform:translateX(0)}"
    "52.2%{transform:translateX(-8px)}54%{transform:translateX(-8px)}"
    "56.5%,83.4%{transform:translateX(0)}84%{transform:translateX(6px)}"
    "86%{transform:translateX(6px)}88%,100%{transform:translateX(0)}}"
    " @keyframes soulHurt{0%,29.6%{opacity:0}"
    "30%{opacity:.95}31%{opacity:0}31.6%{opacity:.9}32.6%{opacity:0}"
    "51.7%{opacity:0}52.1%{opacity:.95}53.1%{opacity:0}53.7%{opacity:.9}54.7%{opacity:0}"
    "83.4%{opacity:0}83.9%{opacity:.95}84.9%{opacity:0}85.5%{opacity:.9}86.5%{opacity:0}"
    "100%{opacity:0}}"
    " @keyframes soulBob{0%,100%{transform:translateY(0)}50%{transform:translateY(1.6px)}}"
    " @keyframes sansBob{0%,100%{transform:translateY(0)}50%{transform:translateY(-1.4px)}}"
    " @keyframes eye{0%,6%{opacity:0}7%{opacity:1}9%{opacity:.3}10%{opacity:1}"
    "65%{opacity:1}67%,100%{opacity:0}}"
    " @keyframes boneSlide{0%,6%{transform:translateX(0);opacity:0}7%{opacity:1}"
    "26%{transform:translateX(-662px);opacity:1}"
    "27%,100%{transform:translateX(-662px);opacity:0}}"
    " @keyframes boneSlideL{0%,6%{transform:translateX(0);opacity:0}7%{opacity:1}"
    "26%{transform:translateX(662px);opacity:1}"
    "27%,100%{transform:translateX(662px);opacity:0}}"
    " @keyframes blasterIn{0%,40%{opacity:0;transform:translateY(-12px)}"
    "43%{opacity:0;transform:translateY(-12px)}46%,62%{opacity:1;transform:translateY(0)}"
    "66%,100%{opacity:0;transform:translateY(-8px)}}"
    " @keyframes beamShot{0%,51.4%{stroke-dashoffset:100;opacity:0}"
    "51.8%{stroke-dashoffset:0;opacity:1}58.6%{stroke-dashoffset:0;opacity:1}"
    "59.4%,100%{stroke-dashoffset:0;opacity:0}}"
    " @keyframes beamFlash{0%,51.7%{opacity:0}52.2%{opacity:.16}54%{opacity:.07}"
    "58%,100%{opacity:0}}"
    " @keyframes hpBar{0%,29.9%{transform:scaleX(1)}30.2%{transform:scaleX(.76)}"
    "51.9%{transform:scaleX(.76)}52.2%{transform:scaleX(.52)}"
    "83.9%{transform:scaleX(.52)}84.2%{transform:scaleX(.28)}"
    "96.5%{transform:scaleX(.28)}97.5%,100%{transform:scaleX(1)}}"
    " @keyframes hpN1{0%,29.9%{opacity:1}30%,96.9%{opacity:0}97%,100%{opacity:1}}"
    " @keyframes hpN2{0%,29.9%{opacity:0}30%,51.9%{opacity:1}52%,100%{opacity:0}}"
    " @keyframes hpN3{0%,51.9%{opacity:0}52%,83.9%{opacity:1}84%,100%{opacity:0}}"
    " @keyframes hpN4{0%,83.9%{opacity:0}84%,96.9%{opacity:1}97%,100%{opacity:0}}"
    "</style>"
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
    lx = PAD + 44
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

    # Undertale: the map is the arena. Frisk and Sans stand on it, bones sweep across,
    # two Gaster Blasters fire an X through it, and the SOUL takes real hits.
    unit = 2.0
    grid_bottom = y0 + step * 6 + cell
    frisk_x = 68
    frisk_y = grid_bottom - 28 * unit
    sans_unit = 1.9
    sans_x, sans_y = 748, grid_bottom - 30 * sans_unit
    eye_x = sans_x + 15.5 * sans_unit
    eye_y = sans_y + 6.5 * sans_unit
    soul_unit = 1.75
    soul_x = 450
    soul_y = grid_bottom - 16 * soul_unit - 9
    blaster_unit = 0.72

    def aimed_blaster(x1, y1, x2, y2):
        """A blaster sitting on the start of a shot, rotated so its mouth points down the line."""
        dx, dy = x2 - x1, y2 - y1
        ang = math.degrees(math.atan2(-dx, dy))
        t = math.radians(ang)
        r = 28.5 * blaster_unit
        bx, by = x1 + r * math.sin(t), y1 - r * math.cos(t)
        w, h = 43 * blaster_unit, 57 * blaster_unit
        return (
            f'<g transform="translate({bx:.1f} {by:.1f}) rotate({ang:.1f})">'
            f"{sprite(BLASTER_PX, -w / 2, -h / 2, blaster_unit, BLASTER_COLOURS)}</g>"
        )

    x_shots = ((255, 104, 604, 181), (604, 129, 255, 181))
    x_beams = "".join(
        f'<line class="beam" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#DFF3FF" '
        f'stroke-width="9" stroke-linecap="round" stroke-opacity=".22" pathLength="100"/>'
        f'<line class="beam" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#FFFFFF" '
        f'stroke-width="2.6" stroke-linecap="round" pathLength="100"/>'
        for x1, y1, x2, y2 in x_shots
    )
    x_blasters = "".join(aimed_blaster(*shot) for shot in x_shots)
    bones = "".join(
        f'<g transform="translate(720 {grid_bottom - 20:.1f})">'
        f'<g class="bone" style="animation-delay:{delay}s">'
        f'<g transform="rotate(90)"><use href="#boneSprite"/></g></g></g>'
        for delay in (0.6, 1.4, 2.2)
    ) + "".join(
        f'<g transform="translate(64 {grid_bottom - 13:.1f})">'
        f'<g class="boneL" style="animation-delay:{delay}s">'
        f'<g transform="rotate(-90)"><use href="#boneSprite"/></g></g></g>'
        for delay in (8.2,)
    )

    return (
        open_svg(
            height,
            f"Contribution map for axs-official with {DATA['total']} contributions across {DATA['activeDays']} active days, "
            "the weekly rhythm over the last 52 weeks, and Frisk and Sans duelling across the grid.",
            "Contributions",
            SCENE_CSS,
        )
        + f'''  <defs>
    <filter id="spShadow" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="1.5" stdDeviation="1.1" flood-color="#000000" flood-opacity=".55"/>
    </filter>
    <filter id="soulSoft" x="-70%" y="-70%" width="240%" height="240%">
      <feGaussianBlur stdDeviation="3.4"/>
    </filter>
    <clipPath id="arenaClip">
      <rect x="{x0 - 2}" y="{y0 - 2}" width="{step * 52 + cell + 4:.1f}" height="{step * 6 + cell + 4:.1f}"/>
    </clipPath>
    <g id="boneSprite">
      {sprite(BONE_PX, -0.5, -0.5, 0.76, {"#": "#080808"})}
      {sprite(BONE_PX, 0, 0, 0.7, BONE_COLOURS)}
    </g>
    <linearGradient id="rhythmFill" x1="0" y1="238" x2="0" y2="276" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{BLUE}" stop-opacity=".28"/>
      <stop offset="1" stop-color="{BLUE}" stop-opacity="0"/>
    </linearGradient>
  </defs>
  {frame(height)}
  {header("CONTRIBUTIONS", "LAST 12 MONTHS")}

  <g>
    <text x="186" y="42" font-family="{MONO}" font-size="11" letter-spacing="1.4" fill="{MUTED}">HP</text>
    <rect x="208" y="33" width="92" height="10" rx="1" fill="#151515" stroke="#3A3A3A"/>
    <g transform="translate(210 35)">
      <rect class="hpBar" x="0" y="0" width="88" height="6" fill="#F2E14C"/>
    </g>
    <text class="hpN1" x="306" y="42" font-family="{MONO}" font-size="11" fill="#F2E14C">92</text>
    <text class="hpN2" x="306" y="42" font-family="{MONO}" font-size="11" fill="#F2E14C">70</text>
    <text class="hpN3" x="306" y="42" font-family="{MONO}" font-size="11" fill="#F2E14C">48</text>
    <text class="hpN4" x="306" y="42" font-family="{MONO}" font-size="11" fill="#F2E14C">26</text>
    <text x="336" y="42" font-family="{MONO}" font-size="10" letter-spacing="1.2" fill="#C9B458" fill-opacity=".75">KR</text>
  </g>
  {''.join(labels)}
  <g font-family="{MONO}" font-size="12.5" letter-spacing="1" fill="{DIM}">
    <text x="{x0 - 10:.1f}" y="{y0 + step + 9:.1f}" text-anchor="end">MON</text>
    <text x="{x0 - 10:.1f}" y="{y0 + step * 3 + 9:.1f}" text-anchor="end">WED</text>
    <text x="{x0 - 10:.1f}" y="{y0 + step * 5 + 9:.1f}" text-anchor="end">FRI</text>
  </g>
  {''.join(cells)}
  <rect class="beamFlash" x="{x0 - 6}" y="{y0 - 6}" width="{step * 52 + cell + 12:.0f}" height="{step * 6 + cell + 12:.0f}" fill="#FFFFFF"/>
  <path d="M{PAD} 202H{W - PAD}" stroke="{LINE}"/>
  <text x="{PAD}" y="226" font-family="{MONO}" font-size="12" letter-spacing="1.6" fill="{MUTED}">WEEKLY RHYTHM</text>
  <path d="{area}" fill="url(#rhythmFill)" class="fade" style="animation-delay:.5s"/>
  <path class="draw" d="{line}" stroke="{BLUE_SOFT}" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"
        style="stroke-dasharray:{length:.1f};stroke-dashoffset:{length:.1f}"/>
  <circle class="blink" cx="{last_x:.1f}" cy="{last_y:.1f}" r="3.4" fill="{BLUE}"/>
  <circle cx="{last_x:.1f}" cy="{last_y:.1f}" r="7" stroke="{BLUE}" stroke-opacity=".35"/>
  <text x="{PAD}" y="317" font-family="{MONO}" font-size="12.5" letter-spacing="1.4" fill="{DIM}">LESS</text>
  {''.join(legend)}
  <text x="{PAD + 136}" y="317" font-family="{MONO}" font-size="12.5" letter-spacing="1.4" fill="{DIM}">MORE</text>

  <!-- Undertale: attacks sweep the map, the SOUL takes hits and the HP bar drops. -->
  <g clip-path="url(#arenaClip)">{bones}{x_beams}</g>
  <ellipse cx="{frisk_x + 17:.1f}" cy="{grid_bottom - 1.6:.1f}" rx="17" ry="3" fill="#000000" opacity=".45"/>
  <ellipse cx="{sans_x + 21.8:.1f}" cy="{grid_bottom - 1.6:.1f}" rx="21" ry="3.4" fill="#000000" opacity=".45"/>
  <g class="friskHop" filter="url(#spShadow)">{sprite(FRISK_PX, frisk_x, frisk_y, unit, FRISK_COLOURS)}</g>
  <g class="sansBob" filter="url(#spShadow)">{sprite(SANS_PX, sans_x, sans_y, sans_unit, SANS_COLOURS)}</g>
  <g class="eye">
    <circle cx="{eye_x:.1f}" cy="{eye_y:.1f}" r="7.5" fill="#7FDBFF" opacity=".2"/>
    <circle cx="{eye_x:.1f}" cy="{eye_y:.1f}" r="2.8" fill="#A6ECFF"/>
  </g>
  <g class="blasterWrap">{x_blasters}</g>
  <g class="soulSlide">
    <g class="soulHop">
      <g class="soulBob">
        <ellipse cx="{soul_x + 14:.1f}" cy="{soul_y + 14:.1f}" rx="24" ry="21" fill="#000000"
                 opacity=".5" filter="url(#soulSoft)"/>
        <ellipse cx="{soul_x + 14:.1f}" cy="{soul_y + 14:.1f}" rx="18" ry="14" fill="#FF3B3B" opacity=".18"/>
        {sprite(HEART_PX, soul_x, soul_y, soul_unit, SOUL_COLOURS)}
        <g class="soulHurt">{sprite(HEART_PX, soul_x, soul_y, soul_unit, {"a": "#FFFFFF"})}</g>
      </g>
    </g>
  </g>
</svg>'''
    )


# %%about
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
            f'<g class="rise" style="animation-delay:{round(0.5 + index * 0.18, 2)}s">'
            f'<text x="566" y="{y}" font-family="{MONO}" font-size="12" letter-spacing="1.4" fill="{DIM}">{label}</text>'
            f'<text x="566" y="{y + 25}" font-family="{SANS}" font-size="16.5" fill="{INK}" fill-opacity=".94">{value}</text>'
            f"</g>"
            f'<rect class="grow" x="566" y="{y + 39}" width="{W - PAD - 566}" height="1" fill="{LINE}" '
            f'style="animation-delay:{round(0.62 + index * 0.18, 2)}s"/>'
        )

    copy = []
    for block, text in enumerate(
        (
            "I take a project end to end: database, API, interface and deploy. React and Next.js "
            "most days, Python when there is work worth automating.",
            "Privacy decides the shape: no analytics, no cookies, no trackers, no logins you didn't "
            "ask for. Ask and I'll walk you through the code.",
        )
    ):
        for line, text_line in enumerate(textwrap.wrap(text, 58)):
            copy.append(
                f'<text class="rise" x="{PAD}" y="{96 + block * 74 + line * 22}" font-family="{SANS}" '
                f'font-size="15" fill="{MUTED}" '
                f'style="animation-delay:{round(0.14 + (block * 3 + line) * 0.09, 2)}s">{esc(text_line)}</text>'
            )

    return (
        open_svg(
            height,
            "About A-XS: full-stack developer. Privacy-first software, built end to end. Open to paid work.",
            "About",
            extra_css="<style>"
            " .bar{animation:barflow 6.6s cubic-bezier(.45,0,.55,1) infinite}"
            " .sheen{animation:sheen 9.5s cubic-bezier(.4,0,.2,1) 1.2s infinite}"
            " @keyframes barflow{0%{transform:translateY(0);opacity:0}"
            "10%{opacity:1}88%{opacity:1}100%{transform:translateY(96px);opacity:0}}"
            " @keyframes sheen{0%{transform:translateX(0)}58%,100%{transform:translateX(1180px)}}"
            "</style>",
        )
        + f'''  <defs>
    <clipPath id="aboutClip">
      <rect x="0.5" y="0.5" width="{W - 1}" height="{height - 1}" rx="16"/>
    </clipPath>
    <linearGradient id="sheenGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset=".5" stop-color="#FFFFFF" stop-opacity=".05"/>
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
  </defs>
  {frame(height)}
  {header("ABOUT", "A-XS")}
  <rect x="{PAD - 12}" y="78" width="2" height="152" rx="1" fill="#1F1F1F"/>
  <rect class="bar" x="{PAD - 12}" y="78" width="2" height="56" rx="1" fill="{BLUE}"/>
  {''.join(copy)}
  <text class="rise" x="{PAD}" y="242" font-family="{MONO}" font-size="11.5" letter-spacing="1.4"
        fill="{MUTED}" style="animation-delay:.72s">NO ANALYTICS · NO COOKIES · NO TRACKERS</text>
  {''.join(rows)}
  <g clip-path="url(#aboutClip)">
    <rect class="sheen" x="-260" y="0" width="260" height="{height}" fill="url(#sheenGrad)"/>
  </g>
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
    """Toolchain constellation: icons float on a mesh with light running the wires."""
    height = 272
    size = 46
    rows = (KIT[:9], KIT[9:])
    centres = (120, 212)
    # Small enough that no plate can ever meet the label of the row above it.
    jitter = (-7, 5, -6, 3, -4, 7, -6, 4, -5)

    def spread(count, inset=0.0):
        left = PAD + size / 2 + inset
        right = W - PAD - size / 2 - inset
        if count == 1:
            return [(left + right) / 2]
        step = (right - left) / (count - 1)
        return [left + i * step for i in range(count)]

    top_x = spread(len(rows[0]))
    bottom_x = spread(len(rows[1]), inset=(top_x[1] - top_x[0]) / 2)
    first = [(x, centres[0] + jitter[i]) for i, x in enumerate(top_x)]
    second = [(x, centres[1] + jitter[(i + 1) % len(jitter)]) for i, x in enumerate(bottom_x)]

    edges = []
    for line in (first, second):
        for a, b in zip(line, line[1:]):
            edges.append((a, b))
    for i, b in enumerate(second):
        for j in (i - 1, i, i + 1):
            if 0 <= j < len(first):
                edges.append((first[j], b))

    wires = []
    packets = []
    for index, ((ax, ay), (bx, by)) in enumerate(edges):
        path = f"M{ax:.1f} {ay:.1f}L{bx:.1f} {by:.1f}"
        wires.append(f'<path class="wire" d="{path}" stroke="#3A3A3A" stroke-width="1"/>')
        colour = LIVE if index % 6 == 3 else "#E8E8E8"
        packets.append(
            f'<path class="packet" d="{path}" pathLength="100" stroke="{colour}" stroke-width="1.5" '
            f'stroke-linecap="round" style="animation-duration:{round(2.6 + (index % 5) * 0.42, 2)}s;'
            f'animation-delay:-{round(0.4 + index * 0.31, 2)}s"/>'
        )

    nodes = []
    for row_index, (line, slugs) in enumerate(zip((first, second), rows)):
        for column, ((cx, cy), slug) in enumerate(zip(line, slugs)):
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
            label_w = len(label) * 6.2 + 10
            float_duration = round(5.6 + ((index_of(slug) * 7) % 11) * 0.28, 2)
            float_delay = round(-((index_of(slug) * 13) % 19) * 0.37, 2)
            appear = round(0.34 + (row_index * 9 + column) * 0.045, 2)
            nodes.append(
                f'<g class="node" style="animation-duration:{float_duration}s;animation-delay:{float_delay}s">'
                f'<g class="plate" style="animation-delay:{appear}s">'
                f'<rect x="{cx - size / 2:.1f}" y="{cy - size / 2:.1f}" width="{size}" height="{size}" '
                f'rx="14" fill="{PANEL}" stroke="{LINE}"/>'
                f'<rect x="{cx - size / 2:.1f}" y="{cy - size / 2:.1f}" width="{size}" height="{size}" '
                f'rx="14" fill="{colour}" opacity=".07"/>'
                f'<rect x="{cx - size / 2:.1f}" y="{cy - size / 2:.1f}" width="{size}" height="{size}" '
                f'rx="14" fill="url(#sheen)"/>'
                f'<rect x="{cx - size / 2 + 0.5:.1f}" y="{cy - size / 2 + 0.5:.1f}" width="{size - 1}" '
                f'height="{size - 1}" rx="13.5" fill="none" stroke="{colour}" stroke-opacity=".22"/>'
                f'<g transform="translate({cx - 10:.1f} {cy - 10:.1f}) scale(.83)">{icon}</g>'
                f'<rect x="{cx - label_w / 2:.1f}" y="{cy + size / 2 + 6:.1f}" width="{label_w:.1f}" '
                f'height="15" rx="4" fill="{BG}" opacity=".9"/>'
                f'<text x="{cx:.1f}" y="{cy + size / 2 + 18:.1f}" text-anchor="middle" '
                f'font-family="{MONO}" font-size="10.5" letter-spacing=".4" fill="{MUTED}">{esc(label)}</text>'
                f'</g></g>'
            )

    listing = ", ".join(STACK_LABELS[slug] for slug in KIT)

    return (
        open_svg(
            height,
            f"Toolchain: {listing}.",
            "Toolchain",
            extra_css="<style>"
            " .wire{stroke-dasharray:3 6;animation:wire 13s linear infinite}"
            " .packet{stroke-dasharray:12 88;animation:packet 3.4s linear infinite;opacity:.9}"
            " .node{animation:drift 7s ease-in-out infinite}"
            " .plate{transform-box:fill-box;transform-origin:center;"
            "animation:nodein .9s cubic-bezier(.22,1,.36,1) both}"
            " @keyframes wire{to{stroke-dashoffset:-108}}"
            " @keyframes packet{from{stroke-dashoffset:0}to{stroke-dashoffset:-100}}"
            " @keyframes drift{0%,100%{transform:translate(0,-3.5px)}"
            "40%{transform:translate(1.5px,1px)}65%{transform:translate(-1.5px,2.5px)}}"
            " @keyframes nodein{from{opacity:0;transform:translateY(10px) scale(.86)}"
            "to{opacity:1;transform:translateY(0) scale(1)}}"
            "</style>",
        )
        + f'''  <defs>
    <linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity=".06"/>
      <stop offset=".55" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
  </defs>
  {frame(height)}
  {header("TOOLCHAIN", f"{len(KIT)} TOOLS")}
  {''.join(wires)}
  {''.join(packets)}
  {''.join(nodes)}
</svg>'''
    )


def index_of(slug):
    return KIT.index(slug)


# %%contact
def contact():
    height = 244
    # Right column: what each line is, then the value, flushed to the card edge.
    links = [
        ("GITHUB", "github.com/axs-official"),
        ("SITE", "axs-official.github.io"),
        ("MODE", "FULL-STACK · REMOTE"),
    ]
    rows = []
    for index, (label, value) in enumerate(links):
        y = 114 + index * 32
        rows.append(
            f'<g class="lift" style="animation-delay:{round(0.22 + index * 0.1, 2)}s">'
            f'<text x="576" y="{y}" font-family="{MONO}" font-size="10.5" letter-spacing="2" '
            f'fill="{DIM}">{label}</text>'
            f'<text x="{W - PAD}" y="{y}" text-anchor="end" font-family="{MONO}" font-size="12.5" '
            f'fill="{INK}" fill-opacity=".86">{esc(value)}</text>'
            f"</g>"
        )

    return (
        open_svg(
            height,
            f"Contact axs at {CONTACT_EMAIL} for paid work and business enquiries only. "
            "Questions and everything else: the links page at axs-official.github.io/links "
            "carries my socials, so message me there.",
            "Contact",
            extra_css="<style>"
            " .lift{animation:lift .9s cubic-bezier(.22,1,.36,1) both}"
            " .pulse{transform-box:fill-box;transform-origin:center;"
            "animation:pulse 2.6s cubic-bezier(.2,.6,.3,1) infinite}"
            " .trail{animation:trail 7s cubic-bezier(.4,0,.2,1) 1.1s infinite}"
            " .vtrail{animation:vtrail 8.4s cubic-bezier(.4,0,.2,1) .7s infinite}"
            " .glow{animation:glow 4.4s ease-in-out .8s infinite}"
            " @keyframes lift{from{opacity:0;transform:translateY(9px)}to{opacity:1;transform:translateY(0)}}"
            " @keyframes pulse{0%{transform:scale(.55);opacity:.6}70%,100%{transform:scale(2.2);opacity:0}}"
            " @keyframes trail{0%{transform:translateX(0);opacity:0}9%{opacity:.85}"
            "58%{transform:translateX(724px);opacity:.1}59%,100%{transform:translateX(724px);opacity:0}}"
            " @keyframes vtrail{0%{transform:translateY(0);opacity:0}12%{opacity:.8}"
            "72%{transform:translateY(68px);opacity:.15}73%,100%{transform:translateY(68px);opacity:0}}"
            " @keyframes glow{0%,100%{opacity:.3}50%{opacity:.75}}"
            "</style>",
        )
        + f'''  {frame(height)}
  <text x="{PAD}" y="38" font-family="{MONO}" font-size="13" letter-spacing="2.6" fill="{BLUE_SOFT}">CONTACT</text>
  <g class="lift" style="animation-delay:.16s">
    <text x="{W - PAD}" y="38" text-anchor="end" font-family="{MONO}" font-size="12" letter-spacing="1.4" fill="{INK}">PAID WORK ONLY</text>
  </g>
  <circle class="pulse" cx="674" cy="33.5" r="4" fill="{LIVE}"/>
  <circle class="lift" cx="674" cy="33.5" r="3.2" fill="{LIVE}" style="animation-delay:.16s"/>
  <path d="M{PAD} 52H{W - PAD}" stroke="{LINE}"/>
  <rect class="trail" x="{PAD}" y="51.4" width="84" height="1.6" rx=".8" fill="{BLUE}"/>

  <text class="lift" x="{PAD}" y="84" font-family="{MONO}" font-size="10.5" letter-spacing="2" fill="{DIM}" style="animation-delay:.04s">EMAIL</text>
  <g class="lift" style="animation-delay:.1s">
    <text x="{PAD}" y="114" font-family="{SANS}" font-size="26" font-weight="500" fill="{INK}">{CONTACT_EMAIL}</text>
  </g>
  <rect class="grow" x="{PAD}" y="123" width="322" height="1.8" rx="1" fill="{BLUE}" opacity=".55" style="animation-delay:.34s"/>
  <rect class="glow" x="{PAD}" y="123" width="322" height="1.8" rx="1" fill="{BLUE}" opacity=".4"/>
  <text class="lift" x="{PAD}" y="150" font-family="{SANS}" font-size="15" fill="{MUTED}" style="animation-delay:.44s">Jobs you need built, fixed or automated.</text>
  <text class="lift" x="{PAD}" y="174" font-family="{SANS}" font-size="13.5" fill="{DIM}" style="animation-delay:.52s">Questions? Go to the links page and message me on social media.</text>

  <path d="M548 96V184" stroke="#303030" stroke-width="1.2"/>
  <rect class="vtrail" x="547.2" y="96" width="1.6" height="20" rx=".8" fill="{BLUE}" opacity=".7"/>
  {''.join(rows)}

  <g class="lift" style="animation-delay:.62s">
    <rect x="{PAD}" y="196" width="{W - 2 * PAD}" height="32" rx="8" fill="{PANEL}" stroke="{LINE}"/>
    <circle class="blink" cx="{PAD + 18}" cy="212" r="3" fill="{LIVE}"/>
    <text x="{PAD + 30}" y="216" font-family="{MONO}" font-size="10.5" letter-spacing="2" fill="{DIM}">ALL LINKS</text>
    <text x="{W - PAD - 16}" y="216" text-anchor="end" font-family="{MONO}" font-size="12.5" fill="{INK}" fill-opacity=".9">axs-official.github.io/links  ↗</text>
  </g>
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

#!/usr/bin/env python3
"""Generates the flat-vector scene illustrations used on the site (assets/art/*.svg).

Style matches the five supplied reference images: pale blue-grey backdrop, a floor band,
dark navy and slate objects, brand blue, a yellow accent and small green status lights.
Run: python3 tools/make_illustrations.py
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "art"
OUT.mkdir(parents=True, exist_ok=True)

BG, FLOOR = "#ecf0f5", "#dde2e7"
NAVY, SLATE, GREY, LG, PALE = "#1f2c39", "#465462", "#a4afbb", "#d3dae0", "#f1f5f8"
BLUE, BBLUE, LB = "#2377da", "#3a91ee", "#abd0ff"
Y, G, W, RED = "#ffcd3b", "#70e3a0", "#ffffff", "#f0625d"
GY = 860  # ground line


# ---- primitives -----------------------------------------------------------
def rect(x, y, w, h, r=0, f=NAVY, extra=""):
    return f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{r}" fill="{f}" {extra}/>'


def circ(cx, cy, r, f=NAVY, extra=""):
    return f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r}" fill="{f}" {extra}/>'


def line(x1, y1, x2, y2, c=BLUE, w=14, extra=""):
    return f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{c}" stroke-width="{w}" stroke-linecap="round" {extra}/>'


def path(d, c=BLUE, w=14, f="none", extra=""):
    return f'<path d="{d}" stroke="{c}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" fill="{f}" {extra}/>'


def dots(d, c=BLUE, w=12, gap=30):
    """Dotted path using round caps on zero-length dashes."""
    return path(d, c, w, extra=f'stroke-dasharray="0 {gap}"')


def tick(cx, cy, s=1.0, c=W, w=16):
    return path(f"M{cx-28*s:.0f} {cy:.0f} L{cx-6*s:.0f} {cy+24*s:.0f} L{cx+32*s:.0f} {cy-22*s:.0f}", c, w)


def scene(*parts, floor=True):
    base = rect(0, 0, 1920, 1080, 0, BG)
    if floor:
        base += rect(0, GY, 1920, 220, 0, FLOOR)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" role="img" aria-hidden="true">{base}{"".join(parts)}</svg>'


# ---- objects --------------------------------------------------------------
def cloud(cx, cy, s=1.0, f=W):
    return (circ(cx - 70 * s, cy + 10 * s, 62 * s, f) + circ(cx, cy - 25 * s, 85 * s, f) + circ(cx + 85 * s, cy + 5 * s, 70 * s, f)
            + rect(cx - 130 * s, cy + 10 * s, 285 * s, 70 * s, 35 * s, f))


def building(x, y, w, h, cols=3, rows=3, win=LB, roof=None, door=False):
    out = [rect(x, y, w, h, 10, W, f'stroke="{LG}" stroke-width="5"')]
    if roof:
        out.append(rect(x - 10, y - 18, w + 20, 30, 8, roof))
    pad = w * 0.12
    cw = (w - pad * 2) / cols
    rh = min(70, (h * 0.62) / rows)
    for r in range(rows):
        for c in range(cols):
            out.append(rect(x + pad + c * cw + cw * 0.12, y + 40 + r * (rh + 34), cw * 0.76, rh, 6, win))
    if door:
        out.append(rect(x + w / 2 - 38, y + h - 100, 76, 100, 8, NAVY))
    return "".join(out)


def router(x, y, w=240, leds=(G, G, Y), antennas=0):
    out = [rect(x, y, w, 62, 16, NAVY)]
    for i, c in enumerate(leds):
        out.append(circ(x + 32 + i * 32, y + 31, 8, c))
    for i in range(antennas):
        ax = x + 50 + i * (w - 100) / max(1, antennas - 1) if antennas > 1 else x + w / 2
        out.append(rect(ax - 7, y - 90, 14, 92, 7, SLATE))
    return "".join(out)


def server(x, y, w=180, h=205):
    return (rect(x, y, w, h, 16, SLATE) + rect(x + 36, y + 36, w - 72, 14, 7, NAVY) + rect(x + 36, y + 62, w - 72, 14, 7, NAVY)
            + rect(x + 36, y + 88, w - 72, 14, 7, NAVY) + circ(x + w - 36, y + h - 44, 12, G))


def desk_phone(x, y):
    return (rect(x, y, 292, 248, 26, "#252d3a") + rect(x + 32, y + 32, 140, 80, 8, LB)
            + "".join(circ(x + 58 + i * 40, y + 148 + j * 30, 8, LG) for j in range(3) for i in range(3))
            + rect(x + 198, y - 18, 78, 274, 36, SLATE))


def mobile(x, y, w=158, h=338, accent=BLUE):
    return (rect(x, y, w, h, 28, NAVY) + rect(x + 14, y + 24, w - 28, h - 48, 14, W)
            + circ(x + w / 2, y + 92, 32, accent) + rect(x + 34, y + 160, w - 68, 12, 6, LG) + rect(x + 52, y + 186, w - 104, 12, 6, LG)
            + circ(x + w / 2, y + 262, 27, Y))


def laptop(cx, w=674, inner=None):
    sx, sy = cx - w / 2, GY - 522
    scr = (rect(sx, sy, w, 474, 26, NAVY) + rect(sx + 27, sy + 27, w - 54, 420, 8, W))
    scr += inner(sx + 27, sy + 27, w - 54, 420) if inner else ""
    return scr + rect(cx - 405, GY - 50, 810, 46, 22, GREY)


def monitor(cx, top, w=855, h=500, inner=None):
    x = cx - w / 2
    out = rect(x, top, w, h, 28, NAVY) + rect(x + 27, top + 27, w - 54, h - 54, 8, W)
    if inner:
        out += inner(x + 27, top + 27, w - 54, h - 54)
    out += rect(cx - 63, top + h, 126, GY - top - h - 20, 0, GREY) + rect(cx - 90, GY - 22, 180, 24, 12, GREY)
    return out


def headset(x, y, s=1.0):
    return (path(f"M{x:.0f} {y:.0f} A{125*s:.0f} {125*s:.0f} 0 0 1 {x+250*s:.0f} {y:.0f}", "#252d3a", 24 * s)
            + rect(x - 28 * s, y - 6 * s, 56 * s, 112 * s, 24 * s, "#252d3a") + rect(x + 222 * s, y - 6 * s, 56 * s, 112 * s, 24 * s, "#252d3a")
            + path(f"M{x-28*s:.0f} {y+80*s:.0f} Q{x-60*s:.0f} {y+110*s:.0f} {x-95*s:.0f} {y+95*s:.0f}", "#252d3a", 12 * s) + circ(x - 100 * s, y + 98 * s, 17 * s, Y))


def tower(x, base, h=640):
    top = base - h
    return (rect(x - 9, top, 18, h - 30, 9, SLATE) + line(x, base - 290, x - 80, base - 8, SLATE, 18) + line(x, base - 290, x + 80, base - 8, SLATE, 18)
            + circ(x, top - 6, 24, Y)
            + path(f"M{x-85:.0f} {top-90:.0f} Q{x-135:.0f} {top-6:.0f} {x-85:.0f} {top+78:.0f}", BLUE, 16)
            + path(f"M{x-52:.0f} {top-52:.0f} Q{x-82:.0f} {top-6:.0f} {x-52:.0f} {top+40:.0f}", BLUE, 16)
            + path(f"M{x+85:.0f} {top-90:.0f} Q{x+135:.0f} {top-6:.0f} {x+85:.0f} {top+78:.0f}", BLUE, 16)
            + path(f"M{x+52:.0f} {top-52:.0f} Q{x+82:.0f} {top-6:.0f} {x+52:.0f} {top+40:.0f}", BLUE, 16))


def padlock(cx, cy, s=1.0):
    return (path(f"M{cx-45*s:.0f} {cy-20*s:.0f} V{cy-62*s:.0f} A{45*s:.0f} {45*s:.0f} 0 0 1 {cx+45*s:.0f} {cy-62*s:.0f} V{cy-20*s:.0f}", NAVY, 22 * s)
            + rect(cx - 82 * s, cy - 30 * s, 164 * s, 128 * s, 22 * s, Y) + circ(cx, cy + 22 * s, 17 * s, NAVY) + rect(cx - 5 * s, cy + 24 * s, 10 * s, 40 * s, 5, NAVY))


def shield(cx, cy, s=1.0, f=BLUE):
    return (path(f"M{cx:.0f} {cy-130*s:.0f} L{cx+110*s:.0f} {cy-90*s:.0f} V{cy+10*s:.0f} C{cx+110*s:.0f} {cy+80*s:.0f} {cx+55*s:.0f} {cy+125*s:.0f} {cx:.0f} {cy+145*s:.0f} C{cx-55*s:.0f} {cy+125*s:.0f} {cx-110*s:.0f} {cy+80*s:.0f} {cx-110*s:.0f} {cy+10*s:.0f} V{cy-90*s:.0f} Z", f, 6, f)
            + tick(cx, cy + 5 * s, 1.5 * s, W, 20 * s))


def pin(cx, cy, s=1.0, f=Y):
    return path(f"M{cx:.0f} {cy+60*s:.0f} C{cx-70*s:.0f} {cy-10*s:.0f} {cx-52*s:.0f} {cy-70*s:.0f} {cx:.0f} {cy-70*s:.0f} C{cx+52*s:.0f} {cy-70*s:.0f} {cx+70*s:.0f} {cy-10*s:.0f} {cx:.0f} {cy+60*s:.0f} Z", f, 4, f) + circ(cx, cy - 20 * s, 18 * s, NAVY)


def xmark(cx, cy, s=1.0, c=RED):
    return line(cx - 26 * s, cy - 26 * s, cx + 26 * s, cy + 26 * s, c, 16 * s) + line(cx + 26 * s, cy - 26 * s, cx - 26 * s, cy + 26 * s, c, 16 * s)


def card(x, y, w, h, accent=BLUE, rows=2):
    out = rect(x, y, w, h, 16, W, f'stroke="{LG}" stroke-width="4"') + circ(x + 48, y + h / 2 - (10 if rows > 1 else 0), 28, accent)
    out += rect(x + 100, y + h / 2 - 22, w - 140, 14, 7, LG)
    if rows > 1:
        out += rect(x + 100, y + h / 2 + 4, w - 190, 14, 7, LG)
    return out


def gauge(cx, cy, r=170):
    return (path(f"M{cx-r:.0f} {cy:.0f} A{r} {r} 0 0 1 {cx+r:.0f} {cy:.0f}", LG, 36)
            + path(f"M{cx-r:.0f} {cy:.0f} A{r} {r} 0 0 1 {cx+r*0.7:.0f} {cy-r*0.71:.0f}", BLUE, 36)
            + line(cx, cy, cx + r * 0.55, cy - r * 0.5, NAVY, 16) + circ(cx, cy, 24, NAVY) + circ(cx, cy, 10, Y))


# ---- scenes ---------------------------------------------------------------
S = {}

S["sip"] = scene(
    cloud(960, 270, 1.15),
    dots("M440 700 C440 480 640 330 790 320", BLUE, 12, 30),
    dots("M1130 320 C1330 340 1430 480 1430 640", BLUE, 12, 30),
    desk_phone(330, 612),
    building(1280, 480, 300, 380, 2, 3, LB, None) + router(1310, 790, 240),
    rect(600, 826, 330, 22, 11, LG) + line(600, 837, 930, 837, GREY, 8) + circ(955, 837, 26, LG) + xmark(955, 837, 0.8, RED),
)

S["switch-off"] = scene(
    rect(190, 250, 520, 560, 30, W, f'stroke="{LG}" stroke-width="5"') + rect(190, 250, 520, 130, 30, BLUE) + rect(190, 330, 520, 50, 0, BLUE)
    + circ(300, 250, 20, NAVY) + circ(600, 250, 20, NAVY)
    + "".join(circ(270 + c * 66, 450 + r * 70, 17, LG) for r in range(4) for c in range(6))
    + circ(270 + 4 * 66, 450 + 2 * 70, 36, Y) + circ(270 + 4 * 66, 450 + 2 * 70, 13, NAVY),
    path("M780 830 C860 830 880 740 960 740 L1100 740", GREY, 24) + rect(1090, 704, 84, 74, 12, SLATE) + xmark(1060, 690, 1.0, RED),
    router(1250, 790, 400, (G, G, G)) + path("M1650 821 C1800 821 1800 540 1640 540 L1470 540", BBLUE, 26) + rect(1452, 508, 80, 66, 12, BBLUE),
    dots("M1190 740 C1220 740 1240 770 1260 795", BLUE, 12, 28),
)

S["lines"] = scene(
    rect(240, 560, 270, 270, 30, W, f'stroke="{LG}" stroke-width="6"') + rect(300, 630, 70, 56, 10, NAVY) + rect(400, 630, 70, 56, 10, NAVY) + circ(385, 760, 11, LG),
    path("M370 686 C370 780 520 790 640 790", BLUE, 16) + rect(636, 770, 44, 40, 8, BLUE),
    desk_phone(640, 612),
    rect(1100, 380, 520, 440, 26, W, f'stroke="{LG}" stroke-width="5"') + rect(1100, 380, 520, 96, 26, BLUE) + rect(1100, 440, 520, 36, 0, BLUE)
    + "".join(rect(1150, 520 + i * 70, 300, 18, 9, LG) + circ(1550, 530 + i * 70, 20, Y if i == 1 else LB) for i in range(4)),
)

S["failover"] = scene(
    tower(1560, GY, 600),
    building(780, 470, 310, 390, 2, 3, LB) + router(810, 790, 250, (G, G, Y)),
    path("M780 834 H430", Y, 20) + rect(150, 700, 170, 160, 16, SLATE) + rect(168, 722, 134, 14, 7, NAVY) + circ(285, 830, 12, RED),
    path("M330 834 H370", Y, 20) + xmark(390, 834, 0.9, RED) + path("M420 834 H430", Y, 20),
    dots("M1090 800 C1250 780 1380 560 1520 470", BLUE, 12, 30),
)

S["pop-up"] = scene(
    tower(330, GY, 640),
    laptop(1130, 620, lambda x, y, w, h: rect(x + 30, y + 30, w - 60, 90, 12, BLUE) + circ(x + 80, y + 75, 26, W) + rect(x + 30, y + 150, w - 60, 16, 8, LG) + rect(x + 30, y + 185, w - 160, 16, 8, LG) + circ(x + w - 90, y + h - 90, 34, Y)),
    router(730, 800, 190, (G, G, G), 2),
    dots("M420 470 C560 440 690 560 790 700", BLUE, 12, 30),
)

S["diverse"] = scene(
    building(250, 440, 300, 420, 2, 3, LB) + router(280, 790, 240, (G, G, G)),
    cloud(1500, 250, 1.1),
    path("M530 826 C800 826 1150 826 1500 826 L1500 400", Y, 20),
    dots("M530 560 C800 520 1100 400 1380 330", BLUE, 12, 30),
    circ(1500, 826, 44, NAVY) + circ(1500, 826, 16, G),
)

S["mpls"] = scene(
    cloud(960, 300, 1.25) + padlock(960, 330, 0.8),
    building(220, 540, 250, 320, 2, 2, LB), building(740, 580, 220, 280, 2, 2, LB), building(1290, 520, 300, 340, 2, 3, LB, BLUE), building(1710, 600, 170, 260, 1, 2, LB),
    dots("M340 530 C400 420 760 360 830 330", BLUE, 12, 30), dots("M850 570 C860 480 900 420 920 380", BLUE, 12, 30),
    dots("M1440 510 C1400 420 1210 360 1080 340", BLUE, 12, 30), dots("M1790 590 C1790 470 1500 330 1100 310", BLUE, 12, 30),
)

S["multi-site"] = scene(
    building(1000, 500, 340, 360, 2, 3, LB, BLUE, True), building(280, 620, 230, 240, 2, 2, LB), building(640, 660, 200, 200, 2, 1, LB), building(1560, 600, 230, 260, 2, 2, LB),
    pin(1170, 380, 1.3), pin(395, 540, 0.9, BBLUE), pin(740, 590, 0.9, BBLUE), pin(1675, 520, 0.9, BBLUE),
    dots("M395 570 C600 400 1000 340 1150 370", BLUE, 11, 28), dots("M740 620 C850 480 1000 400 1150 380", BLUE, 11, 28), dots("M1675 550 C1600 420 1400 370 1190 375", BLUE, 11, 28),
)

S["fibre"] = scene(
    rect(220, 600, 240, 260, 16, SLATE) + rect(250, 630, 82, 200, 8, NAVY) + rect(348, 630, 82, 200, 8, NAVY) + circ(300, 730, 8, G) + rect(205, 580, 270, 36, 12, GREY),
    path("M460 840 H1060", BBLUE, 22) + path("M460 810 H1060", BLUE, 12) + path("M460 868 H1060", Y, 10),
    building(1060, 460, 330, 400, 2, 3, LB) + router(1090, 790, 270, (G, G, G)),
    "".join(rect(1520 + i * 78, 760 - i * 105, 50, 100 + i * 105, 10, BLUE) for i in range(4)),
)

S["full-fibre"] = scene(
    gauge(700, 700, 260),
    circ(1380, 700, 150, LG) + circ(1380, 700, 118, BLUE) + circ(1380, 700, 78, "#1a5fb3") + circ(1380, 700, 40, W)
    + "".join(line(1380, 700, 1380 + 190 * math.cos(a * 0.7854), 700 + 190 * math.sin(a * 0.7854), BBLUE, 6) for a in range(8)),
    path("M1530 700 C1700 700 1760 560 1880 560", BBLUE, 22),
    router(1500, 800, 300, (G, G, G)),
    rect(80, 820, 260, 28, 14, LG),
)

S["lanes"] = scene(
    rect(0, 420, 1920, 130, 0, LG) + rect(0, 630, 1920, 130, 0, LG) + dots("M0 485 H1920", W, 10, 70) + dots("M0 695 H1920", W, 10, 70),
    "".join(rect(120 + i * 150, 452, 100, 66, 14, GREY if i % 2 else SLATE) for i in range(12)),
    rect(1100, 662, 260, 66, 22, Y) + path("M1400 695 H1800", BLUE, 12, extra='stroke-dasharray="0 34"') + path("M1780 660 L1830 695 L1780 730", BLUE, 14),
    circ(960, 250, 60, W) + tick(960, 250, 1.1, BLUE, 14),
    floor=False,
)

S["contact-centre"] = scene(
    monitor(800, 250, 1000, 520, lambda x, y, w, h: "".join(
        rect(x + 30 + (i % 2) * 330, y + 30 + (i // 2) * 180, 300, 150, 14, PALE)
        + rect(x + 55 + (i % 2) * 330, y + 55 + (i // 2) * 180, 110 + i * 25, 24, 12, [BLUE, Y, BBLUE, GREY][i])
        + rect(x + 55 + (i % 2) * 330, y + 105 + (i // 2) * 180, 190, 20, 10, LG) for i in range(4))
        + "".join(circ(x + w - 100, y + 75 + i * 100, 30, [BLUE, Y, NAVY][i]) + rect(x + w - 62, y + 66 + i * 100, 30, 16, 8, LG) for i in range(3))),
    headset(1360, 560, 1.15),
    rect(1480, 330, 280, 130, 30, W, f'stroke="{LG}" stroke-width="5"') + path("M1560 395 q40 -40 80 0", BLUE, 14) + circ(1560, 395, 10, BLUE) + circ(1640, 395, 10, BLUE),
)

S["certified"] = scene(
    shield(800, 470, 2.0),
    rect(1240, 600, 330, 260, 30, Y) + rect(1200, 790, 410, 70, 30, "#e6b52a") + rect(1360, 560, 100, 60, 14, Y),
    rect(250, 560, 260, 300, 20, W, f'stroke="{LG}" stroke-width="5"') + rect(330, 530, 100, 50, 14, SLATE)
    + "".join(circ(310, 650 + i * 70, 16, G) + rect(350, 641 + i * 70, 120, 16, 8, LG) for i in range(3)),
)

S["store"] = scene(
    laptop(900, 700, lambda x, y, w, h: "".join(rect(x + 30 + (i % 3) * 210, y + 40 + (i // 3) * 170, 180, 140, 12, PALE) + rect(x + 50 + (i % 3) * 210, y + 55 + (i // 3) * 170, 100, 70, 8, [BLUE, Y, BBLUE, LB, GREY, BLUE][i]) for i in range(6))),
    rect(1380, 690, 230, 170, 14, Y) + rect(1380, 690, 230, 44, 14, "#e6b52a") + rect(1470, 690, 50, 170, 0, W, 'opacity=".55"'),
    rect(1560, 770, 170, 90, 12, BLUE) + rect(1625, 770, 40, 90, 0, LB),
    path("M240 520 H300 L335 700 H600 L640 560 H320", NAVY, 20) + circ(380, 770, 28, NAVY) + circ(560, 770, 28, NAVY),
)

S["crm"] = scene(
    laptop(1050, 760, lambda x, y, w, h: "".join(rect(x + 30, y + 40 + i * 78, w - 60, 56, 10, PALE) + circ(x + 62, y + 68 + i * 78, 18, [BLUE, Y, BBLUE, LB, GREY][i]) + rect(x + 100, y + 58 + i * 78, 230, 16, 8, LG) for i in range(5))),
    mobile(300, 520, 190, 340),
    card(180, 280, 440, 150) + dots("M400 450 C420 500 440 520 470 540", BLUE, 12, 28),
    path("M215 600 q-40 -60 0 -120", BLUE, 14) + path("M180 620 q-80 -80 0 -160", BLUE, 14),
)

S["flow"] = scene(
    rect(220, 160, 1480, 640, 36, W, f'stroke="{LG}" stroke-width="6"'),
    circ(360, 480, 64, BLUE) + circ(360, 480, 24, W) + line(424, 480, 600, 480, GREY, 12),
    path("M700 380 L800 480 L700 580 L600 480 Z", Y, 6, Y),
    line(800, 480, 920, 480, GREY, 12) + rect(920, 420, 220, 120, 20, LB),
    path("M700 580 V670 H920", GREY, 12) + rect(920, 620, 220, 100, 20, LB),
    line(1140, 480, 1260, 480, GREY, 12) + rect(1260, 420, 220, 120, 20, BBLUE) + line(1480, 480, 1520, 480, GREY, 12)
    + circ(1580, 480, 60, G) + tick(1580, 482, 1.0, NAVY, 14),
    floor=False,
)

S["hotel"] = scene(
    building(260, 250, 420, 610, 3, 5, LB, BLUE, True),
    rect(960, 700, 360, 40, 14, SLATE) + rect(1010, 740, 20, 120, 0, SLATE) + rect(1250, 740, 20, 120, 0, SLATE) + circ(1140, 660, 38, Y) + rect(1100, 690, 80, 14, 7, Y),
    rect(1420, 640, 300, 190, 22, Y) + rect(1420, 680, 300, 40, 0, NAVY) + rect(1450, 760, 150, 16, 8, "#e6b52a"),
)

S["security"] = scene(
    server(560, 640, 200, 220) + server(560, 420, 200, 205),
    padlock(1100, 600, 1.9),
    shield(1560, 560, 1.4),
    dots("M780 560 C860 560 900 580 950 600", BLUE, 12, 28),
)

S["car"] = scene(
    rect(0, 846, 1920, 14, 0, LG),
    rect(150, 650, 760, 150, 48, BLUE) + path("M330 650 L410 540 Q430 515 470 515 H690 Q735 515 760 548 L830 650 Z", BLUE, 4, BLUE)
    + path("M388 640 L440 565 Q452 548 478 548 H560 V640 Z", LB, 4, LB) + path("M600 640 V548 H690 Q712 548 726 566 L775 640 Z", LB, 4, LB)
    + circ(880, 725, 22, Y) + rect(140, 712, 26, 40, 8, "#1a5fb3")
    + circ(300, 794, 70, NAVY) + circ(300, 794, 28, GREY) + circ(740, 794, 70, NAVY) + circ(740, 794, 28, GREY),
    rect(1130, 270, 640, 420, 40, NAVY) + rect(1162, 302, 576, 356, 20, W) + circ(1290, 420, 58, BLUE) + rect(1380, 392, 250, 20, 10, LG) + rect(1380, 432, 170, 20, 10, LG)
    + circ(1290, 570, 44, G) + circ(1450, 570, 44, RED) + circ(1610, 570, 44, LG),
    dots("M900 600 C980 520 1040 480 1120 470", BLUE, 12, 28),
)

S["story"] = scene(
    building(250, 240, 480, 620, 3, 5, LB, BLUE, True),
    rect(960, 540, 260, 310, 26, W, f'stroke="{LG}" stroke-width="5"') + rect(960, 540, 260, 70, 26, Y) + rect(960, 580, 260, 30, 0, Y)
    + circ(1010, 540, 14, NAVY) + circ(1170, 540, 14, NAVY) + rect(1005, 660, 170, 22, 11, LG) + rect(1005, 710, 120, 22, 11, LG) + tick(1090, 780, 1.0, BLUE, 14),
    rect(1340, 640, 330, 170, 22, BLUE) + rect(1630, 700, 150, 110, 18, BLUE) + rect(1650, 718, 100, 50, 10, LB) + circ(1440, 820, 44, NAVY) + circ(1440, 820, 16, GREY) + circ(1700, 820, 44, NAVY) + circ(1700, 820, 16, GREY),
    rect(1370, 580, 270, 22, 8, SLATE),
)


S["meeting"] = scene(
    laptop(1060, 760, lambda x, y, w, h: "".join(
        rect(x + 30 + (i % 2) * 215, y + 30 + (i // 2) * 175, 195, 155, 14, [BLUE, Y, LG, SLATE][i])
        + circ(x + 127 + (i % 2) * 215, y + 90 + (i // 2) * 175, 28, [W, NAVY, NAVY, W][i])
        + rect(x + 87 + (i % 2) * 215, y + 128 + (i // 2) * 175, 80, 34, 17, [W, NAVY, NAVY, W][i]) for i in range(4))),
    rect(230, 440, 360, 400, 26, W, f'stroke="{LG}" stroke-width="5"') + rect(230, 440, 360, 90, 26, BLUE) + rect(230, 500, 360, 30, 0, BLUE)
    + "".join(circ(290 + c * 62, 580 + r * 62, 14, LG) for r in range(3) for c in range(5)) + circ(290 + 2 * 62, 580 + 62, 28, Y),
    dots("M600 700 C640 700 660 700 690 700", BLUE, 12, 28),
)

S["integrations"] = scene(
    rect(800, 360, 320, 320, 50, W, f'stroke="{LG}" stroke-width="6"') + circ(960, 520, 70, BLUE) + path("M930 520 h60 M960 490 v60", W, 14),
    rect(300, 200, 200, 200, 36, BLUE) + circ(400, 300, 46, W), rect(1420, 200, 200, 200, 36, Y) + rect(1470, 270, 100, 24, 12, NAVY) + rect(1470, 315, 70, 24, 12, NAVY),
    rect(300, 640, 200, 200, 36, NAVY) + "".join(rect(345 + i * 38, 790 - (i + 1) * 36, 24, (i + 1) * 36, 6, LB) for i in range(4)),
    rect(1420, 640, 200, 200, 36, LB) + circ(1520, 740, 50, W) + circ(1520, 740, 20, BLUE),
    path("M500 300 C650 300 700 440 800 480", BLUE, 12, extra='stroke-dasharray="0 28"'), path("M1420 300 C1270 300 1220 440 1120 480", BLUE, 12, extra='stroke-dasharray="0 28"'),
    path("M500 740 C650 740 700 600 800 560", BLUE, 12, extra='stroke-dasharray="0 28"'), path("M1420 740 C1270 740 1220 600 1120 560", BLUE, 12, extra='stroke-dasharray="0 28"'),
    floor=False,
)

S["reliability"] = scene(
    cloud(960, 250, 1.2) + shield(960, 250, 0.5, BLUE),
    server(330, 640, 200, 220), server(860, 640, 200, 220), server(1390, 640, 200, 220),
    dots("M430 620 C440 480 700 330 810 300", BLUE, 12, 28), dots("M960 620 V420", BLUE, 12, 28), dots("M1490 620 C1480 480 1220 330 1110 300", BLUE, 12, 28),
    circ(1750, 760, 70, W) + path("M1750 710 V760 L1790 785", NAVY, 14),
)

S["voice-chat"] = scene(
    laptop(1000, 760, lambda x, y, w, h: rect(x + 30, y + 40, 330, 70, 20, LB) + rect(x + w - 380, y + 140, 330, 70, 20, BLUE)
        + rect(x + 30, y + 240, 250, 70, 20, LB) + rect(x + w - 330, y + 330, 280, 60, 20, BLUE)),
    desk_phone(250, 612),
    rect(260, 330, 330, 120, 30, W, f'stroke="{LG}" stroke-width="5"') + circ(330, 390, 22, BLUE) + circ(400, 390, 22, Y) + circ(470, 390, 22, LG),
)


def browser(x, y, w, h, inner=None):
    out = rect(x, y, w, h, 24, W, f'stroke="{LG}" stroke-width="5"') + rect(x, y, w, 62, 24, NAVY) + rect(x, y + 36, w, 26, 0, NAVY)
    out += circ(x + 38, y + 31, 9, RED) + circ(x + 68, y + 31, 9, Y) + circ(x + 98, y + 31, 9, G)
    if inner:
        out += inner(x, y + 62, w, h - 62)
    return out


def toggle(x, y, on=True):
    return rect(x, y, 84, 44, 22, BLUE if on else LG) + circ(x + (62 if on else 22), y + 22, 17, W)


S["portal"] = scene(
    browser(260, 250, 1000, 610, lambda x, y, w, h: rect(x, y, 230, h, 0, PALE)
        + "".join(circ(x + 50, y + 70 + i * 80, 18, BLUE if i == 0 else LG) + rect(x + 86, y + 62 + i * 80, 110, 16, 8, LG) for i in range(5))
        + "".join(rect(x + 270, y + 50 + i * 110, 380, 18, 9, LG) + rect(x + 270, y + 84 + i * 110, 260, 14, 7, LB) + toggle(x + w - 150, y + 50 + i * 110, i != 2) for i in range(4))),
    desk_phone(1400, 612),
    dots("M1260 560 C1310 560 1340 600 1390 650", BLUE, 12, 28),
)

S["collab-apps"] = scene(
    laptop(720, 720, lambda x, y, w, h: rect(x, y, 170, h, 0, PALE)
        + "".join(circ(x + 50, y + 60 + i * 80, 22, [BLUE, Y, NAVY, LB][i]) + circ(x + 68, y + 76 + i * 80, 8, G if i != 2 else GREY) for i in range(4))
        + rect(x + 210, y + 40, 260, 62, 18, LB) + rect(x + w - 330, y + 130, 300, 62, 18, BLUE) + rect(x + 210, y + 220, 200, 62, 18, LB)),
    rect(1180, 380, 340, 480, 34, NAVY) + rect(1200, 420, 300, 400, 12, W) + rect(1220, 440, 260, 180, 12, BLUE) + circ(1350, 530, 44, W) + rect(1225, 650, 250, 18, 9, LG) + rect(1225, 690, 170, 18, 9, LG),
    mobile(1590, 520, 170, 340),
    dots("M1090 620 C1120 620 1150 620 1170 620", BLUE, 12, 28),
)

S["teams-direct"] = scene(
    laptop(520, 640, lambda x, y, w, h: rect(x + 40, y + 40, 190, 190, 40, BBLUE) + rect(x + 95, y + 95, 80, 56, 14, W)
        + rect(x + 270, y + 60, w - 320, 22, 11, LG) + rect(x + 270, y + 110, w - 400, 22, 11, LG) + rect(x + 270, y + 160, w - 360, 22, 11, LG)),
    cloud(1000, 280, 1.1),
    dots("M730 520 C800 420 860 360 900 330", BLUE, 12, 28), dots("M1100 330 C1180 360 1260 440 1300 540", BLUE, 12, 28),
    desk_phone(1250, 612) + path("M1380 600 q0 -60 60 -60", BLUE, 14) + path("M1380 570 q0 -100 110 -100", BLUE, 14),
    rect(1620, 560, 150, 300, 20, W, f'stroke="{LG}" stroke-width="5"') + circ(1695, 640, 30, LB) + circ(1695, 720, 30, LB) + circ(1695, 800, 30, LB),
)

S["analytics"] = scene(
    rect(240, 190, 1440, 650, 36, W, f'stroke="{LG}" stroke-width="5"'),
    "".join(rect(320 + i * 90, 700 - h, 56, h, 10, BLUE if i % 2 == 0 else BBLUE) for i, h in enumerate([150, 260, 200, 340, 280, 400])),
    path("M330 420 C500 360 560 480 720 400 C860 330 940 460 1100 380", Y, 16),
    rect(1180, 260, 410, 150, 20, PALE) + rect(1210, 290, 150, 20, 10, LG) + rect(1210, 330, 260, 40, 10, BLUE),
    circ(1290, 590, 110, LG) + path("M1290 480 A110 110 0 1 1 1190 636", BLUE, 40) + circ(1290, 590, 56, W),
    circ(1520, 520, 44, Y) + rect(1500, 560, 40, 16, 8, Y),
    floor=False,
)

S["hardware"] = scene(
    desk_phone(250, 612),
    headset(760, 640, 1.1),
    circ(1250, 780, 150, SLATE) + circ(1250, 780, 118, NAVY) + circ(1250, 780, 40, SLATE) + "".join(circ(1250 + 78 * math.cos(a * 1.2566), 780 + 78 * math.sin(a * 1.2566), 9, [G, LB, LB, LB, Y][a]) for a in range(5)),
    rect(1500, 700, 300, 160, 26, GREY) + rect(1530, 660, 240, 60, 16, SLATE) + circ(1560, 780, 14, NAVY) + circ(1620, 780, 14, NAVY),
)

S["accessibility"] = scene(
    rect(210, 300, 500, 440, 40, W, f'stroke="{LG}" stroke-width="5"') + rect(260, 350, 400, 150, 20, BLUE) + rect(300, 395, 320, 18, 9, W) + rect(300, 435, 220, 18, 9, LB) + path("M300 600 q30 -50 60 0 q30 50 60 0", GREY, 14),
    rect(760, 300, 400, 440, 40, W, f'stroke="{LG}" stroke-width="5"') + path("M830 520 C900 430 1020 430 1090 520 C1020 610 900 610 830 520 Z", NAVY, 14, W) + circ(960, 520, 48, BLUE) + circ(960, 520, 18, W),
    rect(1210, 300, 500, 440, 40, W, f'stroke="{LG}" stroke-width="5"') + rect(1260, 360, 400, 100, 20, Y) + circ(1330, 410, 26, NAVY) + circ(1450, 410, 26, NAVY) + circ(1570, 410, 26, NAVY) + rect(1290, 520, 340, 140, 30, LB) + circ(1460, 590, 36, BLUE),
)

S["uk-support"] = scene(
    headset(740, 400, 1.7),
    circ(1330, 520, 190, W, f'stroke="{LG}" stroke-width="6"') + path("M1330 400 V520 L1420 570", NAVY, 20) + circ(1330, 520, 14, NAVY),
    pin(1330, 280, 1.0, Y),
    rect(330, 720, 150, 120, 20, W, f'stroke="{LG}" stroke-width="5"') + rect(360, 750, 90, 14, 7, LG) + rect(360, 780, 60, 14, 7, LG),
)


S["pbx-box"] = scene(
    rect(640, 560, 640, 300, 26, NAVY) + rect(670, 600, 580, 40, 12, SLATE) + "".join(circ(700 + i * 70, 700, 16, [G, G, G, Y, G, G, LB, LB][i]) for i in range(8))
    + "".join(rect(690 + i * 70, 760, 42, 40, 8, SLATE) for i in range(8)),
    desk_phone(170, 612), mobile(1500, 520, 170, 340),
    path("M460 760 C540 790 600 800 690 800", BLUE, 12, extra='stroke-dasharray="0 26"'), path("M1280 720 C1360 720 1420 700 1500 680", BLUE, 12, extra='stroke-dasharray="0 26"'),
    cloud(960, 330, 0.9) + dots("M960 430 V540", BLUE, 12, 26),
)

S["scale-up"] = scene(
    rect(250, 700, 220, 160, 20, NAVY) + circ(300, 780, 12, G) + rect(330, 770, 100, 14, 7, SLATE),
    rect(640, 560, 260, 300, 22, NAVY) + "".join(rect(670, 590 + i * 70, 200, 46, 10, SLATE) + circ(690, 613 + i * 70, 10, G) for i in range(4)),
    rect(1060, 380, 250, 480, 22, NAVY) + "".join(rect(1090, 410 + i * 70, 190, 46, 10, SLATE) + circ(1110, 433 + i * 70, 10, G if i != 3 else Y) for i in range(6))
    + rect(1370, 380, 250, 480, 22, NAVY) + "".join(rect(1400, 410 + i * 70, 190, 46, 10, SLATE) + circ(1420, 433 + i * 70, 10, G) for i in range(6)),
    pin(375, 640, 0.9, BBLUE), pin(770, 500, 1.0, BBLUE), pin(1340, 330, 1.2, Y),
)

S["dect"] = scene(
    rect(260, 380, 200, 480, 34, NAVY) + rect(285, 420, 150, 150, 14, LB) + "".join(circ(320 + (i % 3) * 40, 630 + (i // 3) * 40, 11, LG) for i in range(6)),
    rect(700, 520, 300, 340, 30, W, f'stroke="{LG}" stroke-width="5"') + circ(850, 600, 36, BLUE) + rect(740, 690, 220, 18, 9, LG) + rect(740, 730, 160, 18, 9, LG),
    rect(1240, 560, 200, 300, 24, SLATE) + rect(1270, 600, 140, 14, 7, NAVY) + circ(1340, 720, 20, G),
    path("M1460 600 q60 60 0 120", BLUE, 14) + path("M1500 570 q100 90 0 180", BLUE, 14) + path("M1540 540 q140 120 0 240", BLUE, 14),
    rect(1620, 640, 90, 220, 26, NAVY) + rect(1636, 668, 58, 56, 8, LB),
)

S["remote-worker"] = scene(
    path("M240 700 L400 560 L560 700 Z", BLUE, 6, BLUE) + rect(280, 690, 240, 170, 8, W, f'stroke="{LG}" stroke-width="5"') + rect(370, 760, 60, 100, 6, NAVY) + rect(300, 720, 50, 50, 6, LB) + rect(450, 720, 50, 50, 6, LB),
    shield(960, 480, 1.0),
    building(1340, 460, 340, 400, 2, 3, LB) + router(1380, 790, 260, (G, G, G)),
    dots("M560 780 C700 780 760 640 860 540", BLUE, 12, 28), dots("M1070 540 C1180 620 1270 760 1380 820", BLUE, 12, 28),
)

S["upgrade"] = scene(
    rect(260, 600, 260, 260, 22, GREY) + "".join(rect(290, 630 + i * 70, 200, 40, 10, LG) for i in range(3)),
    path("M600 730 H920", BLUE, 20) + path("M880 680 L940 730 L880 780", BLUE, 20),
    rect(1060, 440, 300, 420, 22, NAVY) + "".join(rect(1090, 470 + i * 80, 240, 52, 12, SLATE) + circ(1115, 496 + i * 80, 11, G) for i in range(4)),
    circ(1560, 560, 100, G) + tick(1560, 562, 1.5, W, 18),
    rect(1480, 720, 160, 130, 20, W, f'stroke="{LG}" stroke-width="5"') + rect(1480, 720, 160, 40, 20, BLUE) + circ(1530, 800, 14, Y),
)


def person(cx, cy, c=BLUE, s=1.0):
    return circ(cx, cy - 34 * s, 22 * s, c) + rect(cx - 32 * s, cy - 6 * s, 64 * s, 54 * s, 26 * s, c)


S["headset-types"] = scene(
    # wired: headset with cable to laptop
    headset(330, 560, 1.0) + path("M232 658 C190 720 260 780 360 800 L520 800", NAVY, 10) + rect(520, 780, 40, 40, 8, SLATE),
    # wireless DECT: headset on a base with waves
    headset(900, 560, 1.0) + rect(1120, 760, 200, 100, 22, SLATE) + rect(1150, 790, 140, 14, 7, NAVY) + circ(1290, 835, 9, G)
    + path("M1180 700 q50 -50 100 0", BLUE, 12) + path("M1160 670 q70 -80 140 0", BLUE, 12),
    # bluetooth: headset and phone
    mobile(1560, 520, 150, 340) + path("M1480 700 q-40 0 -60 -40", BLUE, 12, extra='stroke-dasharray="0 24"') + circ(1480, 640, 26, BBLUE) + path("M1472 628 l16 12 l-8 6 l-8 -6 l8 -6 l8 12", W, 5),
)

S["speakerphone"] = scene(
    rect(260, 640, 1400, 60, 26, GREY) + rect(360, 700, 24, 160, 0, SLATE) + rect(1540, 700, 24, 160, 0, SLATE),
    circ(960, 610, 130, NAVY) + rect(830, 600, 260, 40, 20, NAVY) + circ(960, 590, 86, SLATE) + "".join(circ(960 + 56 * math.cos(a * 0.7854), 590 + 56 * math.sin(a * 0.7854), 7, [G, LB, LB, LB, Y, LB, LB, LB][a]) for a in range(8)),
    person(560, 520, BLUE), person(780, 450, Y, 0.9), person(1140, 450, NAVY, 0.9), person(1380, 520, BBLUE),
    path("M820 450 q60 -100 140 -100 q80 0 120 100", BLUE, 10, extra='stroke-dasharray="0 22"'),
)

S["video-bar-room"] = scene(
    rect(380, 190, 1160, 520, 30, NAVY) + rect(410, 220, 1100, 460, 12, BG) + "".join(rect(440 + (i % 3) * 350, 250 + (i // 3) * 200, 320, 170, 14, [BLUE, Y, LG, SLATE, LB, BBLUE][i]) + circ(600 + (i % 3) * 350, 320 + (i // 3) * 200, 30, W) for i in range(6)),
    rect(560, 716, 800, 48, 20, SLATE) + circ(600, 740, 10, G) + circ(1320, 740, 10, BLUE) + rect(660, 728, 140, 22, 11, NAVY) + circ(960, 740, 14, NAVY),
    rect(500, 820, 920, 50, 24, GREY) + person(720, 800, BLUE, 0.8) + person(960, 800, Y, 0.8) + person(1200, 800, NAVY, 0.8),
)

S["room-sizes"] = scene(
    rect(120, 340, 480, 480, 28, W, f'stroke="{LG}" stroke-width="6"') + rect(210, 520, 300, 110, 22, GREY) + person(270, 520, BLUE, 0.7) + person(450, 520, Y, 0.7) + circ(360, 600, 30, NAVY),
    rect(680, 300, 560, 560, 28, W, f'stroke="{LG}" stroke-width="6"') + rect(760, 500, 400, 150, 26, GREY) + person(800, 480, BLUE, 0.7) + person(960, 470, Y, 0.7) + person(1120, 480, NAVY, 0.7) + person(860, 690, BBLUE, 0.7) + person(1060, 690, LB, 0.7) + circ(960, 575, 32, NAVY),
    rect(1320, 260, 480, 600, 28, W, f'stroke="{LG}" stroke-width="6"') + rect(1380, 440, 360, 280, 30, GREY) + "".join(person(1410 + i * 110, 420, [BLUE, Y, NAVY, BBLUE][i], 0.6) for i in range(4)) + "".join(person(1410 + i * 110, 760, [LB, BLUE, Y, NAVY][i], 0.6) for i in range(4)) + circ(1560, 580, 28, NAVY),
    floor=False,
)


def write_all():
    for name, svg in S.items():
        (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")
    print(f"wrote {len(S)} illustrations to {OUT}")


if __name__ == "__main__":
    write_all()

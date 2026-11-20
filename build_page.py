#!/usr/bin/env python3
"""Build the front page for Friday 20 November 2026.

Renders a dense one-page newspaper (1024x1024 PNG) with the Pillow
library, which is only a build-time tool on this machine: the entry
program itself (main.py) is standard library only and just copies the
finished image. Every story on the page was first reported on Friday
20 November 2026; stories first reported on 19 November are named in
the date-check footer instead of being shown as news.

Run:  python3 build_page.py        (writes entry.png next to this file)
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024

# --- palette: warm newsprint, ink, red, navy, teal -------------------------
PAPER = (247, 243, 232)
INK = (26, 26, 26)
RED = (160, 30, 34)
NAVY = (31, 58, 95)
TEAL = (15, 118, 110)
GREY = (110, 105, 95)
LIGHT = (238, 232, 218)
SKY = (186, 214, 232)
SEA = (24, 68, 110)
SAND = (226, 205, 158)
GREEN = (46, 110, 58)
GOLD = (198, 148, 32)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

DJ = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    return ImageFont.truetype(DJ + name, size)


SERIF_B = "DejaVuSerif-Bold.ttf"
SERIF = "DejaVuSerif.ttf"
SERIF_I = "DejaVuSerif-Italic.ttf"
SANS_B = "DejaVuSans-Bold.ttf"
SANS = "DejaVuSans.ttf"

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img, "RGBA")


def rect(x0, y0, x1, y1, fill=None, outline=None, width=1):
    d.rectangle([x0, y0, x1, y1], fill=fill, outline=outline, width=width)


def hline(x0, x1, y, fill=INK, width=1):
    d.line([x0, y, x1, y], fill=fill, width=width)


def text(x, y, s, f, fill=INK, anchor="la"):
    d.text((x, y), s, font=f, fill=fill, anchor=anchor)


def tw(s, f):
    """Pixel width of a string in a font."""
    return d.textlength(s, font=f)


def wrap(s, f, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = s.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if tw(trial, f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(x, y, s, f, max_w, fill=INK, leading=None, max_lines=None):
    """Draw a wrapped paragraph; returns the y just below the last line."""
    if leading is None:
        leading = f.size + 3
    lines = wrap(s, f, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    for ln in lines:
        text(x, y, ln, f, fill=fill)
        y += leading
    return y


def kicker(x, y, s, f, fill=RED):
    text(x, y, s, f, fill=fill)


def headline(x, y, s, f, max_w, fill=INK, leading=None):
    return para(x, y, s, f, max_w, fill=fill, leading=leading)


def box(x0, y0, x1, y1, outline=INK, width=1, fill=None):
    rect(x0, y0, x1, y1, fill=fill, outline=outline, width=width)


def story_card(x0, y0, x1, y1, num, place, beat, head, body, art,
               head_size=14, body_size=10, art_h=52, kicker_size=9,
               body_lines=3):
    """One illustrated lead: picture on top, kicker, headline, body."""
    box(x0, y0, x1, y1, width=1)
    ax0, ay0, ax1, ay1 = x0 + 1, y0 + 1, x1 - 1, y0 + art_h
    art(ax0, ay0, ax1, ay1)
    hline(ax0, ax1, ay1 + 1)
    ky = ay1 + 5
    kf = font(SANS_B, kicker_size)
    kicker(x0 + 5, ky, "%d · %s · %s" % (num, place, beat), kf)
    hy = ky + kicker_size + 4
    hf = font(SERIF_B, head_size)
    hy = headline(x0 + 5, hy, head, hf, x1 - x0 - 10,
                  leading=head_size + 2)
    bf = font(SERIF, body_size)
    para(x0 + 5, hy + 2, body, bf, x1 - x0 - 10,
         leading=body_size + 3, max_lines=body_lines)


def num_strip(y, items):
    """Six big numbers with small labels across the page."""
    n = len(items)
    cw = (W - 16) // n
    for i, (big, small) in enumerate(items):
        x0 = 8 + i * cw
        bf = font(SERIF_B, 25)
        text(x0 + 4, y, big, bf, fill=RED)
        sf = font(SANS, 9)
        para(x0 + 4, y + 30, small, sf, cw - 10, leading=11, max_lines=2)
        if i:
            d.line([x0, y + 2, x0, y + 52], fill=GREY, width=1)
    hline(8, W - 8, y + 56)


def region_tabs(y, items):
    """Coloured chips with a story count per region."""
    x = 8
    f = font(SANS_B, 10)
    for label, count, colour in items:
        s = "  %s %d  " % (label, count)
        w = int(tw(s, f)) + 4
        rect(x, y, x + w, y + 18, fill=colour)
        text(x + 2, y + 4, s, f, fill=WHITE)
        x += w + 4


# --- illustrations: small vector scenes, drawn with PIL only --------------
def art_cyclone(x0, y0, x1, y1):
    rect(x0, y0, x1, y1, fill=(23, 58, 110))
    cx, cy = (x0 + x1) // 2 + 30, (y0 + y1) // 2
    for r, col in ((46, WHITE), (38, (170, 205, 235)), (30, WHITE),
                   (22, (170, 205, 235)), (14, WHITE), (7, (240, 220, 140))):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=4)
    for i in range(9):
        x = x0 + 12 + i * 16
        d.line([x, y0 + 6, x - 8, y0 + 26], fill=(170, 205, 235), width=2)
    rect(x0, y1 - 16, x1, y1, fill=SAND)
    d.polygon([(x0 + 14, y1 - 16), (x0 + 34, y1 - 16), (x0 + 24, y1 - 34)],
              fill=GREEN)
    text(x0 + 6, y1 - 14, "LANDFALL: NOON IST", font(SANS_B, 9), fill=INK)
    d.ellipse([x1 - 16, y1 - 13, x1 - 8, y1 - 5], fill=RED)


def art_cop(x0, y0, x1, y1):
    rect(x0, y0, x1, y1, fill=SKY)
    d.ellipse([x1 - 52, y0 + 8, x1 - 14, y0 + 38], fill=(240, 180, 60))
    d.polygon([(x0, y1), (x0, y1 - 34), (x1, y1 - 26), (x1, y1)], fill=GREEN)
    cx = (x0 + x1) // 2
    rect(cx - 62, y1 - 44, cx + 62, y1 - 14, fill=(240, 236, 224))
    d.polygon([(cx - 70, y1 - 44), (cx, y1 - 58), (cx + 70, y1 - 44)],
              fill=(200, 190, 170))
    for i in range(5):
        px = cx - 50 + i * 22
        rect(px, y1 - 38, px + 10, y1 - 14, fill=(70, 130, 200))
    text(x0 + 6, y0 + 6, "FINAL DAY", font(SANS_B, 10), fill=NAVY)
    text(x0 + 6, y1 - 14, "ANTALYA · 9–20 NOV", font(SANS_B, 9), fill=WHITE)


def art_ipo(x0, y0, x1, y1):
    rect(x0, y0, x1, y1, fill=(16, 66, 46))
    n = 9
    cw = (x1 - x0 - 16) // n
    highs = [30, 44, 38, 58, 50, 66, 60, 78, 70]
    for i, h in enumerate(highs):
        bx = x0 + 10 + i * cw
        up = i % 2 == 0
        col = (60, 190, 110) if up else (220, 70, 60)
        d.line([bx + cw // 2, y1 - 18 - h - 8, bx + cw // 2, y1 - 18 - h + 22],
               fill=col, width=2)
        rect(bx + 2, y1 - 18 - h, bx + cw - 2, y1 - 18 - h + 20, fill=col)
    d.line([x0 + 8, y1 - 26, x1 - 8, y1 - 52], fill=(240, 220, 140), width=3)
    text(x1 - 62, y0 + 5, "$97.17", font(SERIF_B, 17), fill=(240, 220, 140))
    text(x0 + 6, y1 - 14, "NASDAQ · FIRST CLOSE · +17%", font(SANS_B, 9),
         fill=WHITE)


def art_flags(x0, y0, x1, y1):
    rect(x0, y0, x1, y1, fill=LIGHT)
    # China, United States, Russia: three flags on poles.
    poles = [(x0 + 26, RED), (x0 + 96, NAVY), (x0 + 166, (200, 200, 200))]
    for px, _ in poles:
        d.line([px, y0 + 8, px, y1 - 8], fill=INK, width=3)
    rect(x0 + 28, y0 + 10, x0 + 72, y0 + 34, fill=(222, 41, 16))
    for sx, sy in ((36, 18), (46, 16), (46, 24), (54, 20), (40, 26)):
        d.ellipse([sx, sy, sx + 4, sy + 4], fill=(255, 222, 0))
    rect(x0 + 98, y0 + 10, x0 + 142, y0 + 34, fill=WHITE, outline=INK)
    for r in range(3):
        rect(x0 + 98, y0 + 10 + r * 8, x0 + 142, y0 + 16 + r * 8,
             fill=RED if r % 2 == 0 else WHITE)
    rect(x0 + 98, y0 + 10, x0 + 114, y0 + 20, fill=NAVY)
    rect(x0 + 168, y0 + 10, x0 + 212, y0 + 18, fill=WHITE, outline=INK)
    rect(x0 + 168, y0 + 18, x0 + 212, y0 + 26, fill=(0, 57, 166))
    rect(x0 + 168, y0 + 26, x0 + 212, y0 + 34, fill=(213, 0, 50))
    d.line([x0 + 8, y1 - 12, x1 - 8, y1 - 12], fill=(120, 85, 50), width=5)


def art_berlin(x0, y0, x1, y1):
    rect(x0, y0, x1, y1, fill=(214, 224, 232))
    rect(x0 + 18, y0 + 22, x1 - 18, y1 - 10, fill=(240, 236, 224))
    d.polygon([(x0 + 10, y0 + 22), ((x0 + x1) // 2, y0 + 4),
               (x1 - 10, y0 + 22)], fill=(200, 190, 170))
    for i in range(5):
        cx = x0 + 34 + i * 32
        rect(cx, y0 + 30, cx + 12, y1 - 10, fill=(190, 180, 160))
    rect(x0 + 8, y1 - 16, x0 + 46, y1 - 8, fill=BLACK)
    rect(x0 + 8, y1 - 8, x0 + 46, y1 - 2, fill=RED)
    rect(x0 + 8, y1 - 2, x0 + 46, y1 + 4, fill=GOLD)


def art_kyiv(x0, y0, x1, y1):
    rect(x0, y0, x1, y1, fill=(30, 40, 60))
    for bx, bw, bh in ((x0 + 10, 34, 44), (x0 + 52, 26, 60),
                       (x0 + 86, 40, 36), (x0 + 134, 30, 52)):
        rect(bx, y1 - bh, bx + bw, y1, fill=(90, 100, 130))
        for wy in range(y1 - bh + 8, y1 - 6, 12):
            for wx in range(bx + 5, bx + bw - 5, 11):
                rect(wx, wy, wx + 4, wy + 6, fill=(240, 200, 90))
    d.ellipse([(x0 + x1) // 2 - 14, y0 + 8, (x0 + x1) // 2 + 14, y0 + 36],
              fill=(240, 140, 40))
    d.line([x0 + 10, y0 + 14, x1 - 10, y0 + 30], fill=(240, 140, 40), width=2)
    for sx in (x0 + 40, x0 + 120, x1 - 30):
        d.ellipse([sx, y0 + 22, sx + 3, y0 + 25], fill=WHITE)


def art_senate(x0, y0, x1, y1):
    rect(x0, y0, x1, y1, fill=(232, 226, 210))
    d.ellipse([(x0 + x1) // 2 - 34, y0 + 6, (x0 + x1) // 2 + 34, y0 + 40],
              fill=WHITE, outline=INK)
    rect(x0 + 26, y0 + 34, x1 - 26, y0 + 42, fill=WHITE, outline=INK)
    for i in range(6):
        cx = x0 + 34 + i * 26
        rect(cx, y0 + 42, cx + 10, y1 - 8, fill=WHITE, outline=INK)
    rect(x0 + 18, y1 - 8, x1 - 18, y1 - 2, fill=INK)
    text(x0 + 8, y0 + 6, "51–48", font(SERIF_B, 15), fill=RED)


def art_nvidia(x0, y0, x1, y1):
    rect(x0, y0, x1, y1, fill=(16, 30, 52))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    for k in range(-2, 3):
        d.line([cx - 34, cy + k * 12, cx - 22, cy + k * 12], fill=GOLD, width=3)
        d.line([cx + 22, cy + k * 12, cx + 34, cy + k * 12], fill=GOLD, width=3)
        d.line([cx + k * 12, cy - 34, cx + k * 12, cy - 22], fill=GOLD, width=3)
        d.line([cx + k * 12, cy + 22, cx + k * 12, cy + 34], fill=GOLD, width=3)
    rect(cx - 22, cy - 22, cx + 22, cy + 22, fill=(30, 90, 50))
    text(cx, cy - 9, "NVDA", font(SANS_B, 12), fill=WHITE, anchor="ma")
    d.polygon([(x1 - 34, y0 + 10), (x1 - 18, y0 + 10), (x1 - 26, y0 + 34)],
              fill=(220, 70, 60))
    text(x0 + 6, y1 - 14, "–3.3%", font(SERIF_B, 13), fill=(220, 70, 60))


def art_cricket(x0, y0, x1, y1):
    rect(x0, y0, x1, y1, fill=(70, 140, 70))
    rect(x0, y0 + 18, x1, y0 + 30, fill=(220, 200, 150))
    for i in range(3):
        sx = x0 + 22 + i * 7
        rect(sx, y0 + 8, sx + 3, y0 + 24, fill=(240, 220, 160))
    d.line([x0 + 20, y0 + 8, x0 + 40, y0 + 8], fill=(240, 220, 160), width=2)
    d.ellipse([x1 - 30, y0 + 14, x1 - 18, y0 + 26], fill=(200, 40, 40))
    d.line([x0 + 60, y1 - 10, x0 + 96, y1 - 34], fill=(150, 100, 50), width=6)
    text(x1 - 58, y1 - 20, "317/6", font(SERIF_B, 15), fill=WHITE)
    text(x0 + 6, y0 + 4, "146*", font(SERIF_B, 13), fill=WHITE)


def art_gta(x0, y0, x1, y1):
    rect(x0, y0, x1, y1, fill=(60, 30, 90))
    d.ellipse([(x0 + x1) // 2 - 26, y0 + 6, (x0 + x1) // 2 + 26, y0 + 52],
              fill=(250, 170, 60))
    for bx, bw, bh in ((x0 + 8, 26, 40), (x0 + 40, 18, 58),
                       (x0 + 64, 30, 34), (x0 + 100, 22, 50),
                       (x0 + 128, 26, 44), (x0 + 160, 20, 30)):
        rect(bx, y1 - bh, bx + bw, y1, fill=(20, 10, 40))
        for wy in range(y1 - bh + 6, y1 - 4, 10):
            for wx in range(bx + 4, bx + bw - 4, 9):
                rect(wx, wy, wx + 3, wy + 4, fill=(250, 200, 90))
    text(x1 - 44, y0 + 6, "VI", font(SERIF_B, 20), fill=(250, 170, 60))
    text(x0 + 6, y1 - 14, "VICE CITY", font(SANS_B, 9), fill=WHITE)


def art_boat(x0, y0, x1, y1):
    rect(x0, y0, x1, y1, fill=SKY)
    d.polygon([(x0 + 40, y1 - 22), (x0 + 150, y1 - 22), (x0 + 138, y1 - 8),
               (x0 + 52, y1 - 8)], fill=(90, 60, 30))
    d.line([x0 + 95, y1 - 22, x0 + 95, y1 - 44], fill=INK, width=3)
    d.polygon([(x0 + 97, y1 - 44), (x0 + 97, y1 - 24), (x0 + 124, y1 - 24)],
              fill=WHITE)
    for wy in (y1 - 6, y1 - 2):
        d.line([x0 + 4, wy, x1 - 4, wy], fill=(40, 90, 140), width=2)
    d.ellipse([x0 + 24, y0 + 10, x0 + 40, y0 + 26], fill=(240, 180, 60))


def art_drought(x0, y0, x1, y1):
    rect(x0, y0, x1, y1, fill=(240, 220, 170))
    d.ellipse([x1 - 48, y0 + 6, x1 - 12, y0 + 36], fill=(240, 160, 40))
    for i, (px, py) in enumerate(((x0 + 20, y1 - 26), (x0 + 70, y1 - 16),
                                  (x0 + 120, y1 - 30), (x0 + 160, y1 - 18))):
        d.line([px, py, px + 26, py], fill=(150, 110, 60), width=2)
        d.line([px + 8, py, px + 16, py + 10], fill=(150, 110, 60), width=2)
    d.line([x0 + 30, y1 - 44, x0 + 44, y1 - 44], fill=GREEN, width=3)
    d.line([x0 + 37, y1 - 44, x0 + 37, y1 - 30], fill=GREEN, width=3)


def art_baseball(x0, y0, x1, y1):
    rect(x0, y0, x1, y1, fill=(232, 240, 220))
    d.ellipse([(x0 + x1) // 2 - 26, y0 + 8, (x0 + x1) // 2 + 26, y0 + 56],
              fill=WHITE, outline=RED, width=2)
    cx = (x0 + x1) // 2
    for k in range(-2, 3):
        d.arc([cx - 26, y0 + 8, cx + 26, y0 + 56], 200 + k * 12, 250 + k * 12,
              fill=RED, width=2)
    text(x0 + 6, y1 - 14, "PETE ROSE", font(SANS_B, 9), fill=INK)


# --- world map --------------------------------------------------------------
# Rough continent outlines on a 1024x1024 page; pins mark stories 1-13.
CONTINENTS = [
    # North America
    [(18, 22), (30, 8), (78, 4), (118, 12), (128, 30), (112, 44), (96, 38),
     (88, 56), (70, 66), (58, 52), (40, 46), (22, 38)],
    # South America
    [(66, 84), (92, 78), (108, 92), (102, 122), (84, 138), (70, 112)],
    # Europe
    [(196, 18), (232, 6), (262, 12), (268, 28), (246, 40), (218, 36),
     (202, 44), (190, 30)],
    # Africa
    [(200, 62), (238, 56), (272, 66), (282, 92), (262, 124), (238, 130),
     (220, 104), (198, 84)],
    # Asia
    [(272, 10), (330, 4), (392, 10), (420, 26), (404, 44), (372, 52),
     (352, 70), (330, 58), (306, 44), (282, 34)],
    # Oceania
    [(376, 96), (404, 90), (420, 100), (404, 112), (380, 110)],
]

# Pin positions (map-local coords) for stories 1-13.
PINS = {
    1: (348, 62), 2: (238, 46), 3: (94, 28), 4: (322, 40), 5: (216, 26),
    6: (252, 32), 7: (70, 50), 8: (30, 40), 9: (408, 104), 10: (52, 66),
    11: (204, 82), 12: (428, 84), 13: (106, 54),
}


def draw_map(x0, y0, x1, y1):
    rect(x0, y0, x1, y1, fill=(200, 222, 238))
    sx = (x1 - x0) / 440.0
    sy = (y1 - y0) / 150.0
    for poly in CONTINENTS:
        pts = [(x0 + px * sx, y0 + py * sy) for px, py in poly]
        d.polygon(pts, fill=SAND, outline=(150, 125, 90))
    for num, (px, py) in PINS.items():
        cx, cy = x0 + px * sx, y0 + py * sy
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=RED, outline=WHITE,
                  width=2)
        text(cx, cy - 7, str(num), font(SANS_B, 10), fill=WHITE, anchor="ma")


# --- story data: every item first reported Friday 20 November 2026 ---------
NUMBERS = [
    ("300,000", "evacuated ahead of Cyclone Akvan (IMD)"),
    ("$97.17", "Anthropic's first close, +17% on its $83 offer"),
    ("118", "Phillips' historic century in Wellington"),
    ("51–48", "Senate rejects the Iran war-powers bid"),
    ("$120bn", "adaptation finance unresolved at COP31"),
    ("99", "GTA VI's Metacritic score"),
]

REGIONS = [
    ("EUROPE", 12, NAVY), ("THE AMERICAS", 10, TEAL),
    ("ASIA-PACIFIC", 12, RED), ("MIDEAST", 3, (120, 90, 30)),
    ("AFRICA", 3, GREEN), ("OCEANIA", 3, (90, 60, 120)),
    ("WORLD", 8, GREY),
]

HEROES = [
    dict(num=1, place="ODISHA", beat="STORM",
         head="Akvan comes ashore in India",
         body=("Severe Cyclone Akvan crosses the Andhra–Odisha coast near "
               "Gopalpur around noon; winds 90–100 gusting 110 km/h."),
         art=art_cyclone),
    dict(num=2, place="ANTALYA", beat="CLIMATE",
         head="COP31 reaches its final day",
         body=("Negotiators face a Friday deadline; the draft calls for a "
               "faster fossil-fuel phase-out while a $120bn adaptation "
               "fund stays open."),
         art=art_cop),
    dict(num=3, place="NEW YORK", beat="MARKETS",
         head="Anthropic ends first day up 17%",
         body=("The Claude maker opens at $111.50 and closes at $97.17, "
               "still 17% above its $83 offer, as the S&P 500 falls 2.02%."),
         art=art_ipo),
]

LEADS = [
    dict(num=4, place="SHENZHEN", beat="DIPLOMACY",
         head="Leaders issue peace declaration",
         body=("Hours after the trilateral, the three leaders publish a "
               "joint declaration."),
         art=art_flags),
    dict(num=5, place="BERLIN", beat="EUROPE",
         head="Europe ready for Ukraine talks",
         body=("Burnham, Merz and Zelenskyy present a united position on "
               "talks with Russia."),
         art=art_berlin),
    dict(num=6, place="KYIV", beat="WAR",
         head="Strikes hit Kyiv embassies",
         body=("One person is killed; the Dutch and Austrian embassies and "
               "a cathedral are hit."),
         art=art_kyiv),
    dict(num=7, place="WASHINGTON", beat="POLITICS",
         head="Senate rejects Iran war-powers bid",
         body=("The resolution fails 51–48, with three Republicans in "
               "favour."),
         art=art_senate),
    dict(num=8, place="CALIFORNIA", beat="TECH",
         head="Nvidia slides on record quarter",
         body=("Shares fall 3.3% to $145.98 after record $115.8bn sales, "
               "as investors fret over leadership."),
         art=art_nvidia),
    dict(num=9, place="WELLINGTON", beat="SPORT",
         head="Phillips makes history with 118",
         body=("The first to score centuries in all formats against India "
               "in one year."),
         art=art_cricket),
    dict(num=10, place="WORLD", beat="GAMES",
         head="GTA VI's first full day on sale",
         body=("Sensor Tower counts about $2.36bn and 24.6m copies sold; "
               "Metacritic 99."),
         art=art_gta),
    dict(num=11, place="SENEGAL", beat="MIGRATION",
         head="Migrant boat sinks off Senegal",
         body=("Dozens missing; four bodies recovered from a boat "
               "carrying 50–100 people."),
         art=art_boat),
    dict(num=12, place="TONGA", beat="PACIFIC",
         head="Drought emergency in Tonga",
         body=("The Pacific kingdom declares an emergency as El Niño "
               "drought bites."),
         art=art_drought),
    dict(num=13, place="WASHINGTON", beat="SPORT",
         head="Trump pardons Pete Rose",
         body=("The late slugger, banned for life for betting, is "
               "pardoned after his death."),
         art=art_baseball),
]

BRIEFS = [
    ("CINCINNATI", "Fiona the hippo dies days after eating a hat."),
    ("HORMUZ", "Four attacks on ships in 96 hours."),
    ("GAZA", "Aid groups score the peace plan 4 out of 26."),
    ("WASHINGTON", "The Iran war has cost $48.3bn."),
    ("LONDON", "UK, Norway fund £100m-plus for naval craft."),
    ("BELGRADE", "Cupic elected speaker of new parliament."),
    ("GREENLAND", "Parliament approves a defence agreement."),
    ("JAKARTA", "Parliament passes an asset-forfeiture bill."),
    ("COPENHAGEN", "Q3 GDP due; consensus sees +0.7%."),
    ("DENVER", "Democrats stay divided despite midterm wins."),
    ("DUBLIN", "Harris seeks border-poll criteria talks."),
    ("LOS ANGELES", "Thomas Markle is found fit to stand trial."),
    ("PUNJAB", "A truck driver wins $1.3m in a Diwali lottery."),
    ("JOHANNESBURG", "DJ Lag celebrates featuring on GTA 6."),
    ("SYDNEY", "ASX futures fall 1%; jobless rate rises to 4.9%."),
    ("MUMBAI", "Sensex slips at the open; Nifty stands at 25,199."),
    ("ANTALYA", "Pledges point to about 2.6°C of warming."),
    ("NEW DELHI", "Pakistan minister to lead Delhi SCO trip."),
    ("TOKYO", "PM Takaichi seeks continued dialogue with China."),
    ("CANBERRA", "Australia sanctions West Bank settler groups."),
    ("SOFIA", "Sunken LPG tanker was hit by drones."),
    ("WASHINGTON", "US files Supreme Court plea on TPS."),
    ("TAIPEI", "Taiwan reports 25 incursions by Chinese bombers."),
    ("FLORIDA", "Floods shut schools in five counties."),
    ("IOWA", "Army postpones its lead-azide blast to Monday."),
    ("WORLD", "Children's Day is marked in about 190 countries."),
    ("TOKYO", "October core CPI rose 2.2%."),
    ("ROME", "A 24-hour general strike; a rail strike runs on."),
    ("BEIJING", "China to hold loan rates at 3.0%."),
    ("HONG KONG", "Hong Kong Open reaches the semifinals."),
    ("USA", "Nine NBA Cup games tonight; Lakers host Kings."),
    ("DOHA", "India A open their Rising Stars campaign."),
    ("CHINA", "OPPO's Watch 5 goes on sale, from CNY 899."),
    ("CHINA", "Huawei unveils a new phone brand, Osta."),
    ("JAPAN", "Hayabusa2 abandons its asteroid landing."),
]

DATE_CHECK = (
    "First reported Thursday 19 Nov, so NOT on this page as news: the "
    "Trump–Xi–Putin trilateral meeting itself · Anthropic's $83 IPO pricing "
    "· GTA VI's midnight unlock · the ICJ's Rohingya genocide judgment · the "
    "Van Gogh record $190.4m sale · the EU's proposed €45bn loan for Ukraine "
    "· the US–Venezuela military deal · Fiji's drought disaster declaration · "
    "Han Duck-soo's acquittal · the Crimean Bridge attack · the Houthi "
    "strike on Riyadh's PIF tower."
)

SOURCES = ("Every story here happened, or was first reported, on Friday "
           "20 November 2026. Disputed claims are attributed, not stated as "
           "fact. Sources: Reuters, AP, AFP, BBC, The Hindu, IMD, ICC, "
           "UNEP. Original drawings.")


def build():
    # --- masthead ---------------------------------------------------------
    text(8, 6, "THE WORLD IN ONE DAY", font(SANS_B, 11), fill=RED)
    rt = "FRIDAY'S NEWS · ONE PAGE · 48 STORIES"
    text(W - 8, 6, rt, font(SANS_B, 11), fill=INK, anchor="ra")
    hline(8, W - 8, 24, width=2)
    text(W // 2, 30, "Friday 20 November 2026", font(SERIF_B, 56),
         fill=INK, anchor="ma")
    text(W // 2, 96,
         "A cyclone comes ashore in India · Climate talks reach their final "
         "day · A record IPO's first close",
         font(SERIF_I, 16), fill=RED, anchor="ma")
    hline(8, W - 8, 122, width=2)

    # --- numbers strip + region tabs --------------------------------------
    num_strip(128, NUMBERS)
    region_tabs(192, REGIONS)
    hline(8, W - 8, 218, width=1)

    # --- three heroes ------------------------------------------------------
    hw = (W - 16 - 12) // 3
    for i, h in enumerate(HEROES):
        x0 = 8 + i * (hw + 6)
        story_card(x0, 226, x0 + hw, 382, h["num"], h["place"], h["beat"],
                   h["head"], h["body"], h["art"], head_size=19,
                   body_size=11, art_h=64, kicker_size=10, body_lines=2)

    # --- ten more illustrated leads, two rows of five ----------------------
    lw = (W - 16 - 4 * 6) // 5
    for r in range(2):
        y0 = 390 + r * 172
        for c in range(5):
            h = LEADS[r * 5 + c]
            x0 = 8 + c * (lw + 6)
            story_card(x0, y0, x0 + lw, y0 + 164, h["num"], h["place"],
                       h["beat"], h["head"], h["body"], h["art"],
                       head_size=13, body_size=9, art_h=58,
                       kicker_size=8)

    # --- map + briefs ------------------------------------------------------
    y0 = 742
    hline(8, W - 8, y0 - 8, width=1)
    text(8, y0, "WHERE IT HAPPENED", font(SANS_B, 11), fill=RED)
    text(412, y0, "ALSO ON FRIDAY 20 NOVEMBER — 35 MORE STORIES",
         font(SANS_B, 11), fill=RED)
    draw_map(8, y0 + 20, 400, y0 + 172)
    text(8, y0 + 178, "Red numbers mark stories 1–13. Positions are "
         "approximate.", font(SANS, 9), fill=GREY)
    bf = font(SERIF, 9)
    lf = font(SANS_B, 9)
    col_w = 296
    for i, (place, body) in enumerate(BRIEFS):
        col = i // 18
        row = i % 18
        bx = 412 + col * (col_w + 8)
        by = y0 + 20 + row * 9
        if by > y0 + 172:
            continue
        lead = "%d %s — " % (i + 14, place)
        lw = tw(lead, lf)
        words = body.split()
        keep = []
        for w in words:
            trial = " ".join(keep + [w])
            if lw + tw(trial, bf) <= col_w:
                keep.append(w)
            else:
                break
        text(bx, by, lead, lf, fill=RED)
        text(bx + lw, by, " ".join(keep), bf, fill=INK)

    # --- date-check footer + sources ---------------------------------------
    fy = 940
    rect(8, fy, W - 8, fy + 52, fill=None, outline=RED, width=2)
    text(14, fy + 5, "DATE CHECK", font(SANS_B, 10), fill=RED)
    para(108, fy + 5, DATE_CHECK, font(SERIF, 9), W - 122, leading=12,
         max_lines=4)
    text(8, fy + 58, SOURCES, font(SANS, 8), fill=GREY)

    img.save(OUT, optimize=True)
    print("wrote", OUT, img.size, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    build()



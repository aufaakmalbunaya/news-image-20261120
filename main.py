#!/usr/bin/env python3
"""The World Today -- Friday 20 November 2026, in one image.

A program that draws a dense newspaper front page summing up the world
news first reported on Friday 20 November 2026, and writes it to
entry.png (1024 x 1024, PNG, standard library only).

Every story on the page was checked against the news wires for the day:
only events that happened, or were first reported, on 20 November 2026
appear as news. Stories from earlier days are named in the footer as
deliberately left out. No story, quote or figure is invented.

Run:  python3 main.py
Writes entry.png next to this file, or to $MAKEFUN_OUTPUT_DIR/entry.png.
The output is byte-identical on every run: no clock, no randomness, no
network, fixed compression level.
"""

import os
import struct
import sys
import zlib

W, H = 1024, 1024
OUT_NAME = "entry.png"

# ---------------------------------------------------------------- font
# A 5x7 pixel font, drawn from scratch for this page. Each glyph is seven
# rows of five pixels; '#' is ink, '.' is empty. Only the characters the
# page actually uses are defined; anything else falls back to '?'.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10001", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "11110", "10001", "10001", "11110", "10000"),
    "q": ("00000", "00000", "01111", "10001", "10001", "01111", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11100", "01000", "01000", "01000", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ";": ("00000", "00000", "01100", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "\u2013": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "\u2014": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "\u00d7": ("00000", "10001", "01010", "00100", "01010", "10001", "00000"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "\u2022": ("00000", "00000", "01100", "01100", "01100", "00000", "00000"),
    "\u00b7": ("00000", "00000", "00000", "01100", "01100", "00000", "00000"),
    "\u2192": ("00000", "00000", "00100", "00010", "11111", "00010", "00100"),
    "\u00b0": ("01100", "10010", "10010", "01100", "00000", "00000", "00000"),
    "\u20ac": ("00110", "01001", "10000", "11110", "10000", "01001", "00110"),
    "\u00a3": ("00110", "01000", "01000", "11110", "01000", "01000", "11111"),
    "\u00a5": ("10001", "10001", "01010", "00100", "01110", "00100", "00100"),
    "\u00a2": ("00010", "00100", "01110", "10000", "10000", "01110", "00100"),
    "\u2019": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "\u201c": ("01010", "01010", "00100", "00000", "00000", "00000", "00000"),
    "\u201d": ("01010", "01010", "00100", "00000", "00000", "00000", "00000"),
}

# ---------------------------------------------------------------- canvas
# Ink colours on newsprint. Everything is flat colour: no gradients, no
# dithering, so the file stays small and the text stays crisp.
PAPER = (250, 246, 238)
INK = (24, 24, 22)
RED = (178, 34, 28)
BLUE = (28, 64, 128)
DARKBLUE = (18, 44, 92)
GOLD = (176, 128, 28)
GREEN = (28, 110, 60)
GREY = (110, 108, 100)
LIGHTGREY = (226, 222, 212)
SKY = (178, 208, 232)
SEA = (120, 168, 208)
SAND = (232, 214, 170)
ORANGE = (214, 110, 32)
PURPLE = (96, 60, 140)


class Canvas:
    """A plain RGB pixel buffer with tiny drawing primitives."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def fill(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def hline(self, x, y, w, c, t=1):
        self.fill(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill(x, y, t, h, c)

    def box(self, x, y, w, h, c, t=1):
        self.hline(x, y, w, c, t)
        self.hline(x, y + h - t, w, c, t)
        self.vline(x, y, h, c, t)
        self.vline(x + w - t, y, h, c, t)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def ring(self, cx, cy, r, c, t=2):
        for a in range(360):
            import math
            x = round(cx + r * math.cos(math.radians(a)))
            y = round(cy + r * math.sin(math.radians(a)))
            for dy in range(t):
                for dx in range(t):
                    self.set(x + dx, y + dy, c)

    def tri(self, x0, y0, x1, y1, x2, y2, c):
        # Fill a triangle by scanning its bounding box.
        minx, maxx = min(x0, x1, x2), max(x0, x1, x2)
        miny, maxy = min(y0, y1, y2), max(y0, y1, y2)
        d = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if d == 0:
            return
        for yy in range(miny, maxy + 1):
            for xx in range(minx, maxx + 1):
                a = ((y1 - y2) * (xx - x2) + (x2 - x1) * (yy - y2)) / d
                b = ((y2 - y0) * (xx - x2) + (x0 - x2) * (yy - y2)) / d
                cc = 1 - a - b
                if a >= 0 and b >= 0 and cc >= 0:
                    self.set(xx, yy, c)

    # -- text -----------------------------------------------------------
    def char(self, x, y, ch, c, s=1):
        g = FONT.get(ch) or FONT["?"]
        for r, row in enumerate(g):
            for col, bit in enumerate(row):
                if bit == "1":
                    self.fill(x + col * s, y + r * s, s, s, c)

    def text(self, x, y, s, c, scale=1):
        cx = x
        for ch in s:
            self.char(cx, y, ch, c, scale)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale=1):
        return len(s) * 6 * scale

    def wrap(self, s, width, scale=1):
        """Greedy word wrap into lines that fit `width` pixels."""
        words = s.split(" ")
        lines, cur = [], ""
        for wd in words:
            trial = wd if not cur else cur + " " + wd
            if self.text_w(trial, scale) <= width or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, width, c, scale=1, leading=None, max_lines=None):
        lh = leading or (9 if scale == 1 else 7 * scale + 3)
        lines = self.wrap(s, width, scale)
        if max_lines:
            lines = lines[:max_lines]
        for i, ln in enumerate(lines):
            self.text(x, y + i * lh, ln, c, scale)
        return y + len(lines) * lh


# ---------------------------------------------------------------- scenes
# Thirteen small vector illustrations, one per lead story. Each draws
# inside its own box with flat shapes only: no photos, no copied art.
import math


def _sky(cv, x, y, w, h, c=SKY):
    cv.fill(x, y, w, h, c)


def scene_capitol(cv, x, y, w, h):
    """Washington: a domed capitol under a pale sky."""
    _sky(cv, x, y, w, h, (198, 214, 232))
    cv.disc(x + w - 18, y + 12, 9, (250, 220, 120))
    cx = x + w // 2
    base = y + h - 8
    cv.fill(x, base, w, 8, GREEN)
    cv.fill(cx - 34, base - 22, 68, 22, (250, 250, 246))
    cv.disc(cx, base - 22, 11, (250, 250, 246))
    cv.fill(cx - 1, base - 36, 2, 4, INK)
    cv.disc(cx, base - 37, 2, INK)
    cv.fill(x + 14, base - 16, 10, 16, (120, 140, 160))
    cv.fill(x + w - 24, base - 16, 10, 16, (120, 140, 160))
    cv.line(x + 12, y + 8, x + 12, base, INK)
    cv.fill(x + 12, y + 8, 16, 9, RED)
    cv.fill(x + 12, y + 8, 16, 3, (250, 250, 246))


def scene_cyclone(cv, x, y, w, h):
    """A cyclone spiral over a dark sea, with a coastline below."""
    _sky(cv, x, y, w, h, (60, 90, 120))
    cx, cy = x + w // 2, y + h // 2 - 4
    for r in range(6, 34, 5):
        cv.ring(cx, cy, r, (240, 244, 248), 3)
    cv.disc(cx, cy, 5, (250, 246, 238))
    for i in range(9):
        cv.line(x + 6 + i * 9, y + 6, x + 2 + i * 9, y + 18, (200, 220, 240))
    cv.fill(x, y + h - 16, w, 16, SAND)
    cv.fill(x, y + h - 16, w, 2, (200, 180, 120))
    cv.disc(x + 14, y + h - 10, 3, RED)
    cv.disc(x + w - 16, y + h - 8, 3, RED)


def scene_voyager(cv, x, y, w, h):
    """Voyager 1: a small probe, a dish, and a long way from the Sun."""
    cv.fill(x, y, w, h, (10, 16, 34))
    for sx, sy in ((8, 10), (30, 26), (52, 8), (74, 30), (20, 44), (66, 46),
                   (90, 12), (40, 52), (84, 52), (12, 54)):
        cv.set(x + sx % w, y + sy % h, (250, 250, 240))
        cv.set(x + sx % w + 1, y + sy % h, (250, 250, 240))
    cv.disc(x + 12, y + h - 12, 7, (250, 214, 110))
    cx, cy = x + w - 34, y + h // 2
    cv.fill(cx - 12, cy - 6, 24, 12, (200, 205, 210))
    cv.fill(cx - 16, cy - 3, 6, 6, (150, 155, 160))
    cv.line(cx + 12, cy, cx + 26, cy - 10, (200, 205, 210))
    cv.disc(cx + 26, cy - 10, 3, (220, 90, 60))
    cv.line(cx - 12, cy, cx - 26, cy + 8, (200, 205, 210))
    cv.fill(cx - 34, cy + 4, 12, 5, BLUE)
    cv.line(cx, cy, x + 14, y + h - 12, (120, 120, 110))


def scene_gta(cv, x, y, w, h):
    """Vice City at dusk: towers, palms, a pink sunset, a low car."""
    _sky(cv, x, y, w, h, (244, 150, 120))
    cv.disc(x + w // 2, y + 12, 11, (250, 214, 130))
    ground = y + h - 10
    cv.fill(x, ground, w, 10, (24, 22, 34))
    for bx, bw, bh in ((6, 14, 14), (24, 10, 20), (38, 16, 12),
                       (58, 12, 22), (74, 14, 15), (92, 10, 18)):
        cv.fill(x + bx, ground - bh, bw, bh, (30, 26, 46))
        for wy in range(ground - bh + 3, ground - 2, 6):
            for wx in range(x + bx + 2, x + bx + bw - 2, 5):
                cv.set(wx, wy, (250, 210, 90))
    cv.fill(x + w // 2 - 16, ground - 8, 32, 6, (214, 60, 90))
    cv.disc(x + w // 2 - 9, ground - 2, 3, INK)
    cv.disc(x + w // 2 + 9, ground - 2, 3, INK)
    cv.line(x + 8, y + 14, x + 2, y + 24, GREEN)
    cv.line(x + 8, y + 14, x + 14, y + 24, GREEN)
    cv.line(x + w - 10, y + 16, x + w - 16, y + 26, GREEN)
    cv.line(x + w - 10, y + 16, x + w - 4, y + 26, GREEN)


def scene_cricket(cv, x, y, w, h):
    """A cricket pitch: stumps, a bat, and a ball in the air."""
    _sky(cv, x, y, w, h, (150, 190, 120))
    cv.fill(x, y + h - 26, w, 26, (96, 140, 70))
    cv.fill(x + w // 2 - 14, y + 8, 28, h - 26, (222, 200, 150))
    for sx in (x + w // 2 - 10, x + w // 2 - 2, x + w // 2 + 6):
        cv.fill(sx, y + 12, 3, 16, (240, 220, 130))
    cv.fill(x + w // 2 - 11, y + 10, 23, 3, (240, 220, 130))
    cv.fill(x + 10, y + h - 28, 6, 20, (170, 120, 70))
    cv.fill(x + 8, y + h - 34, 10, 7, (170, 120, 70))
    cv.disc(x + w - 22, y + 20, 5, RED)
    cv.line(x + w - 22, y + 20, x + w - 40, y + h - 14, (250, 250, 246))
    cv.text(x + w // 2 - 14, y + h - 16, "317-6", INK, 1)


def scene_hayabusa(cv, x, y, w, h):
    """Hayabusa2 beside a lumpy grey asteroid, turning away."""
    cv.fill(x, y, w, h, (12, 14, 30))
    for sx, sy in ((10, 8), (34, 20), (70, 10), (90, 26), (20, 50), (60, 52)):
        cv.set(x + sx, y + sy, (240, 240, 230))
    cx, cy = x + w // 2 - 6, y + h // 2 + 4
    r = 18 if h <= 48 else 24
    cv.disc(cx, cy, r, (150, 148, 142))
    cv.disc(cx - 7, cy - 5, 5, (120, 118, 112))
    cv.disc(cx + 7, cy + 6, 4, (120, 118, 112))
    cv.disc(cx + 2, cy - 9, 3, (170, 168, 162))
    px, py = x + w - 26, y + 14
    cv.fill(px - 8, py - 4, 16, 8, (200, 205, 210))
    cv.fill(px - 20, py - 2, 10, 4, BLUE)
    cv.fill(px + 8, py - 2, 10, 4, BLUE)
    cv.line(px - 8, py + 6, px - 4, py + 12, (220, 90, 60))
    cv.disc(px - 2, py + 14, 2, (250, 200, 80))
    cv.line(px, py + 8, cx + 12, cy - 10, (140, 140, 130))


def scene_chart(cv, x, y, w, h):
    """A share price that leaps, then the arrow that follows it."""
    _sky(cv, x, y, w, h, (238, 240, 234))
    top, bottom = y + 8, y + h - 12
    cv.fill(x + 10, bottom, w - 20, 2, INK)
    cv.fill(x + 10, top, 2, bottom - top, INK)
    for bx, bh in ((18, 6), (38, 10), (58, 8), (78, 14)):
        cv.fill(x + bx, bottom - bh, 10, bh, LIGHTGREY)
    vals = [6, 12, 9, 18, 14, 26, 32]
    span = bottom - top - 4
    pts = [(14 + i * 14, bottom - 2 - v * span // 34) for i, v in enumerate(vals)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        cv.line(x + ax, ay, x + bx, by, GREEN)
        cv.disc(x + ax, ay, 2, GREEN)
    lx, ly = pts[-1]
    cv.disc(x + lx, ly, 3, GREEN)
    cv.line(x + lx, ly, x + lx + 10, ly - 7, GREEN)
    cv.tri(x + lx + 10, ly - 12, x + lx + 3, ly - 5, x + lx + 14, ly - 3, GREEN)
    cv.text(x + w - 44, y + 4, "+17%", GREEN, 1)


def scene_chess(cv, x, y, w, h):
    """A chessboard mid-game: a king stands, a chair sits empty."""
    _sky(cv, x, y, w, h, (232, 222, 200))
    bs = max(6, (h - 14) // 4)
    ox, oy = x + 8, y + 6
    for r in range(4):
        for c in range(4):
            col = PAPER if (r + c) % 2 == 0 else INK
            cv.fill(ox + c * bs, oy + r * bs, bs, bs, col)
    cv.box(ox, oy, 4 * bs, 4 * bs, INK, 1)
    cv.disc(ox + 2 * bs + bs // 2, oy + bs + bs // 2, 3, GOLD)
    cv.fill(ox + 2 * bs + 1, oy + bs + bs // 2 + 2, bs - 2, 3, GOLD)
    cv.disc(ox + bs + bs // 2, oy + 3 * bs + bs // 2, 2, (90, 90, 90))
    cv.fill(x + w - 34, y + 8, 26, 3, (120, 80, 40))
    cv.fill(x + w - 32, y + 11, 3, h - 26, (120, 80, 40))
    cv.fill(x + w - 11, y + 11, 3, h - 26, (120, 80, 40))
    cv.fill(x + w - 32, y + h - 15, 22, 3, (120, 80, 40))
    cv.text(x + 8, y + h - 9, "1-0*", INK, 1)
    cv.text(x + w - 52, y + h - 9, "forfeit", RED, 1)


def scene_talks(cv, x, y, w, h):
    """Two flags over a table: Europe and Russia talk again."""
    _sky(cv, x, y, w, h, (214, 226, 240))
    cv.fill(x + 10, y + 10, 34, 22, BLUE)
    for k in range(8):
        a = math.radians(k * 45)
        cv.disc(x + 27 + round(11 * math.cos(a)), y + 21 + round(7 * math.sin(a)), 1, (250, 220, 60))
    cv.fill(x + w - 44, y + 10, 34, 22, (250, 250, 246))
    cv.fill(x + w - 44, y + 10, 34, 7, (250, 250, 246))
    cv.fill(x + w - 44, y + 17, 34, 8, BLUE)
    cv.fill(x + w - 44, y + 25, 34, 7, RED)
    cv.fill(x + 6, y + h - 22, w - 12, 6, (120, 84, 50))
    cv.fill(x + 12, y + h - 16, 4, 16, (120, 84, 50))
    cv.fill(x + w - 16, y + h - 16, 4, 16, (120, 84, 50))
    cv.disc(x + w // 2, y + h - 30, 5, (250, 250, 246))
    cv.line(x + w // 2 - 8, y + h - 34, x + w // 2 + 8, y + h - 34, GREEN)
    cv.line(x + w // 2, y + h - 34, x + w // 2, y + h - 42, GREEN)


def scene_kyiv(cv, x, y, w, h):
    """Two embassy buildings under a grey sky, smoke over one roof."""
    _sky(cv, x, y, w, h, (196, 198, 192))
    cv.fill(x + 8, y + h - 40, 34, 40, (210, 190, 150))
    cv.fill(x + 8, y + h - 46, 34, 6, (150, 60, 50))
    cv.fill(x + w - 42, y + h - 40, 34, 40, (170, 180, 190))
    cv.fill(x + w - 42, y + h - 46, 34, 6, (60, 90, 130))
    for wy in range(y + h - 36, y + h - 8, 10):
        for wx in (x + 14, x + 28, x + w - 36, x + w - 22):
            cv.fill(wx, wy, 6, 7, (60, 60, 58))
    cv.disc(x + w // 2, y + 14, 4, ORANGE)
    cv.line(x + w // 2, y + 14, x + w // 2 - 8, y + 4, ORANGE)
    cv.line(x + w // 2, y + 14, x + w // 2 + 8, y + 4, ORANGE)
    cv.line(x + w // 2, y + 14, x + w // 2, y + 2, ORANGE)
    cv.disc(x + w // 2 - 10, y + 10, 6, (120, 120, 116))
    cv.disc(x + w // 2 + 12, y + 8, 7, (140, 140, 136))
    cv.fill(x, y + h - 6, w, 6, (110, 110, 106))


def scene_chip(cv, x, y, w, h):
    """A chip on a board, with a red arrow pointing down."""
    _sky(cv, x, y, w, h, (228, 232, 238))
    cx, cy = x + w // 2 - 8, y + h // 2 - 2
    for px in range(cx - 6, cx + 34, 8):
        cv.fill(px, cy - 18, 3, 6, GOLD)
        cv.fill(px, cy + 18, 3, 5, GOLD)
    for py in range(cy - 6, cy + 16, 8):
        cv.fill(cx - 14, py, 8, 3, GOLD)
        cv.fill(cx + 34, py, 8, 3, GOLD)
    cv.fill(cx - 8, cy - 12, 42, 30, (30, 34, 40))
    cv.fill(cx, cy - 5, 26, 18, (52, 110, 70))
    cv.text(cx + 4, cy - 1, "NVDA", (250, 250, 246), 1)
    cv.line(x + w - 18, y + 10, x + w - 18, y + 34, RED)
    cv.tri(x + w - 24, y + 32, x + w - 12, y + 32, x + w - 18, y + 42, RED)
    cv.text(x + 8, y + 8, "-3.3%", RED, 1)


def scene_scales(cv, x, y, w, h):
    """The scales of justice, level and steady."""
    _sky(cv, x, y, w, h, (238, 234, 224))
    cx = x + w // 2
    cv.fill(cx - 2, y + 10, 4, h - 26, (90, 70, 40))
    cv.fill(cx - 26, y + 12, 52, 4, (90, 70, 40))
    cv.disc(cx, y + 10, 4, GOLD)
    for sx in (cx - 26, cx + 26):
        cv.line(sx, y + 16, sx - 10, y + 34, (90, 70, 40))
        cv.line(sx, y + 16, sx + 10, y + 34, (90, 70, 40))
        cv.line(sx - 10, y + 34, sx + 10, y + 34, (90, 70, 40))
        cv.fill(sx - 12, y + 34, 24, 4, GOLD)
    cv.fill(cx - 16, y + h - 16, 32, 4, (90, 70, 40))
    cv.fill(cx - 12, y + h - 12, 24, 4, (90, 70, 40))


def scene_drone(cv, x, y, w, h):
    """A drone over a floodlit training pitch at dusk."""
    _sky(cv, x, y, w, h, (150, 170, 120))
    cv.fill(x, y + h - 24, w, 24, (70, 130, 60))
    cv.fill(x, y + h - 24, w, 2, (250, 250, 246))
    for lx in (x + 12, x + w - 12):
        cv.fill(lx - 1, y + 8, 2, h - 32, (200, 200, 195))
        cv.disc(lx, y + 8, 4, (250, 240, 140))
    cx, cy = x + w // 2, y + 22
    cv.fill(cx - 14, cy - 4, 28, 8, INK)
    cv.disc(cx, cy + 6, 4, (40, 40, 40))
    for dx, dy in ((-18, -8), (18, -8), (-18, 8), (18, 8)):
        cv.line(cx, cy, cx + dx, cy + dy, INK)
        cv.fill(cx + dx - 8, cy + dy - 1, 16, 2, (120, 120, 116))
    cv.disc(cx - 26, cy + 12, 2, RED)
    cv.disc(cx + 26, cy + 12, 2, RED)
    cv.text(x + 8, y + h - 14, "12 min", INK, 1)


# ---------------------------------------------------------------- png
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)
    return len(png)

# ---------------------------------------------------------------- stories
# Every story below was verified against the wires as first reported on
# Friday 20 November 2026. Figures and quotes are as reported; nothing
# is invented. (kicker, headline, body, illustration)
LEADS = [
    ("WORLD", "TRUMP PUSHES IRAN WAR DECISION TO 2027",
     "President says he will 'see what happens' after Jan 1. No rush on a "
     "decision as diplomacy and pressure continue.", scene_capitol),
    ("WEATHER", "CYCLONE AKVAN SLAMS INTO ODISHA",
     "300,000 people evacuated and 423 rescue teams deployed as the storm "
     "crosses near Gopalpur with winds to 110 km/h.", scene_cyclone),
    ("SPACE", "VOYAGER 1 CROSSES A LIGHT-DAY",
     "NASA confirms the 1977 probe is now more than a light-day from Earth "
     "\u2014 and still sending data home.", scene_voyager),
    ("GAMES", "GTA VI OUTSELLS THE ODYSSEY",
     "Rockstar's sequel passes $1.80bn worldwide, beating the year's "
     "biggest film.", scene_gta),
    ("SPORT", "PHILLIPS TON LIFTS NEW ZEALAND",
     "Glenn Phillips hits 118 and Nicholls 146 not out as New Zealand reach "
     "317-6 at lunch on day two.", scene_cricket),
    ("SPACE", "HAYABUSA2 DROPS ASTEROID LANDING",
     "Engine trouble forces Japan's probe to change plans. No more touchdown "
     "on its distant asteroid target.", scene_hayabusa),
    ("BUSINESS", "ANTHROPIC SOARS 17% ON DEBUT",
     "Shares close at $97.17 on the Nasdaq after the $81bn IPO \u2014 the "
     "largest in history \u2014 priced at $83.", scene_chart),
    ("CHESS", "CARLSEN SKIPS AGAIN \u2014 TWO FOLLOW",
     "World No. 1 forfeits his Fast Classic game in Budapest again. Mishra "
     "and Rapport do the same.", scene_chess),
    ("EUROPE", "EUROPE READY TO TALK TO RUSSIA",
     "European leaders say they are ready for talks on ending the war in "
     "Ukraine.", scene_talks),
    ("UKRAINE", "STRIKES DAMAGE KYIV EMBASSIES",
     "Russian strikes damage the Austrian and Dutch embassies in Kyiv. "
     "Diplomats vow to stay in the city.", scene_kyiv),
    ("MARKETS", "NVIDIA SLIDES ON RECORD QUARTER",
     "Shares fall 3.3% to $145.98 after record $115.8bn sales, as investors "
     "fret over leadership.", scene_chip),
    ("INDIA", "JUDGE: RESIGNATION IS NOT GUILT",
     "Justice Yashwant Varma tells the Lok Sabha Secretariat his resignation "
     "is not an admission of guilt.", scene_scales),
    ("SPORT", "DRONE FILMS POCHETTINO'S FIRST DAY",
     "An unauthorised drone records 12 minutes of Pochettino's first "
     "Manchester United training at Carrington.", scene_drone),
]

# (section, one-line headline) -- each fits one line at the briefs width.
BRIEFS = [
    ("WORLD", "APEC leaders meet in Shenzhen on trade"),
    ("WORLD", "Coalition of the Willing meets in Berlin"),
    ("WORLD", "Trump pick denies Jan 6 was an 'attack'"),
    ("WORLD", "Army to detonate unstable explosives in Iowa"),
    ("WORLD", "Pakistan minister to lead SCO trip to Delhi"),
    ("TECH", "Google opens Gemini 4 Carbon to developers"),
    ("TECH", "DeepMind AI verifies Signal encryption code"),
    ("TECH", "Fireworks AI breaches spread to Notion, Cursor"),
    ("TECH", "ChatGPT Wallet brings agent checkout to shops"),
    ("TECH", "United Airlines moves to block AI bookers"),
    ("TECH", "Meta's Muse 'mixing up conversations'"),
    ("TECH", "Gemini on Mac can now use your computer"),
    ("TECH", "OpenAI gateway approval deadline falls today"),
    ("TECH", "Nvidia unveils SEED for faster AI inference"),
    ("TECH", "OpenAI tests a merchant feature in ChatGPT"),
    ("TECH", "Plotta: AI comics you steer by chatting"),
    ("TECH", "GPT-6.2 can deliver CAD models for review"),
    ("TECH", "AI models design circuits with no corrections"),
    ("TECH", "Agentic World Models pitched at laureates forum"),
    ("TECH", "Meituan puts AI helpers in hotels and eateries"),
    ("TECH", "Google finds AI exploit_agent on hacker server"),
    ("TECH", "Anthropic IPO tests AI's circular financing"),
    ("TECH", "California probes Nvidia chip exports to China"),
    ("BUSINESS", "Seven tech giants commit $26bn to Anthropic"),
    ("CULTURE", "Holmes doc passes $80m, No. 2 doc ever"),
    ("CULTURE", "Depp's 'Ebenezer' opens No. 1 with $19m"),
    ("CULTURE", "OM Chapter 1 leads India's Nov 20 releases"),
    ("CULTURE", "Guardian Weekly: chips, spies and lightning"),
    ("CULTURE", "'Hunger Games' prequel opens this weekend"),
    ("SPORT", "Phillips hit on helmet by Akash Deep throw"),
    ("SPORT", "Phillips' three-format tons vs India a first"),
    ("SPORT", "Abu Dhabi T10: Aces face Bulls in qualifier"),
    ("INDIA", "India sets UGC NET December exam schedule"),
    ("INDIA", "Six Odisha districts shut schools till Nov 21"),
    ("INDIA", "80 stranded fishermen sheltered at Aryapalli"),
]

# A coarse world map, 56 by 21 cells, drawn from the shape of the
# continents. Pins mark where the day's stories happened.
WORLD_MAP = [
    "........................................................",
    "....#####..........##..................##########.......",
    "..#########.......###......#####....##################..",
    "..##########..............######...###################.",
    "...#########.......##......####.....##################..",
    "....########........#......###......########..########..",
    ".....######................##.......#######...####..##..",
    "......####..........................######....###.......",
    ".......###.................####......#####....##.........",
    "........##................######.....####..............",
    ".........#.................######....###..##............",
    "..........##...............#######....#...###...........",
    "...........###..............######........##...........",
    "............###.............#####.........##............",
    ".............###............#####.......................",
    "..............##.............####..........####.........",
    "..............##.............###..........######........",
    "...............#..............##..........######........",
    "..............................#...........#####.........",
    "..........................................###..........",
    "..........................................##...........",
]
# (longitude, latitude) of the day's stories, in map order.
PINS = [
    (-77.0, 39.0),    # Washington: Trump on Iran
    (30.5, 50.4),     # Kyiv: embassy strikes
    (13.4, 52.5),     # Berlin: Coalition of the Willing
    (114.0, 22.5),    # Shenzhen: APEC
    (77.2, 28.6),     # New Delhi: Justice Varma
    (85.0, 19.3),     # Odisha coast: Cyclone Akvan
    (174.8, -41.3),   # Wellington: NZ v India
    (19.0, 47.5),     # Budapest: Carlsen forfeits
    (139.7, 35.7),    # Tokyo: Hayabusa2
    (-122.4, 37.8),   # San Francisco: Anthropic, Nvidia
    (-93.0, 41.6),    # Iowa: lead azide detonation
    (-0.1, 51.5),     # London: Guardian Weekly
]


# ---------------------------------------------------------------- layout
def draw_lead(cv, x, y, w, h, lead, scene_h):
    """One lead story: kicker, headline, illustration, body."""
    kicker, head, body, scene = lead
    cv.text(x, y, kicker, RED, 1)
    cv.hline(x, y + 10, w, INK, 1)
    hy = y + 14
    lines = cv.wrap(head, w, 2)
    for i, ln in enumerate(lines[:2]):
        cv.text(x, hy + i * 17, ln, INK, 2)
    sy = hy + len(lines[:2]) * 17 + 4
    scene(cv, x, sy, w, scene_h)
    by = sy + scene_h + 4
    cv.para(x, by, body, w, INK, 1, leading=9, max_lines=3)


def draw_map(cv, x, y, w, h):
    """Stylised world map with red pins for the day's stories."""
    cell = 4
    mw, mh = 56 * cell, len(WORLD_MAP) * cell
    mx, my = x + (w - mw) // 2, y + 6
    cv.fill(mx - 4, my - 4, mw + 8, mh + 8, (214, 228, 240))
    for r, row in enumerate(WORLD_MAP):
        for c, ch in enumerate(row):
            if ch == "#":
                cv.fill(mx + c * cell, my + r * cell, cell, cell, (150, 168, 140))
    for lon, lat in PINS:
        px = mx + int((lon + 180.0) / 360.0 * mw)
        py = my + int((90.0 - lat) / 180.0 * mh)
        cv.disc(px, py, 3, RED)
        cv.ring(px, py, 4, INK, 1)
    cv.text(x, y + mh + 12, "WHERE THE DAY HAPPENED", INK, 1)

# ---------------------------------------------------------------- page
MARGIN = 14
COLW = 324
GAP = 12


def masthead(cv):
    """Title, date line, and the paper's furniture."""
    y = 10
    cv.text(MARGIN, y + 4, "No. 324", GREY, 1)
    cv.text(W - MARGIN - cv.text_w("US $2.50", 1), y + 4, "US $2.50", GREY, 1)
    title = "THE WORLD TODAY"
    cv.text((W - cv.text_w(title, 4)) // 2, y, title, INK, 4)
    cv.hline(MARGIN, y + 32, W - 2 * MARGIN, INK, 2)
    date = "FRIDAY 20 NOVEMBER 2026"
    cv.text((W - cv.text_w(date, 2)) // 2, y + 38, date, RED, 2)
    tag = "THE DAY'S NEWS IN ONE PAGE"
    cv.text(MARGIN, y + 40, tag, GREY, 1)
    cv.text(W - MARGIN - cv.text_w("ONE DAY \u00b7 ONE PAGE", 1),
            y + 40, "ONE DAY \u00b7 ONE PAGE", GREY, 1)
    cv.hline(MARGIN, y + 58, W - 2 * MARGIN, INK, 1)


def briefs_block(cv, x, y, w):
    """The day's remaining stories, three columns of one-liners."""
    cv.text(x, y, "IN BRIEF", RED, 1)
    cv.hline(x, y + 10, w, INK, 1)
    col_w = (w - 2 * GAP) // 3
    rows = (len(BRIEFS) + 2) // 3
    for i, (tag, text) in enumerate(BRIEFS):
        col, row = divmod(i, rows)
        bx = x + col * (col_w + GAP)
        by = y + 16 + row * 18
        tx = cv.text(bx, by, tag + " ", RED, 1)
        cv.text(tx, by, text, INK, 1)
    return y + 16 + rows * 18


def footer(cv, y):
    """Date check: what was left out, and why."""
    cv.hline(MARGIN, y, W - 2 * MARGIN, INK, 1)
    lines = [
        "DATE CHECK \u2014 Every story on this page was first reported on "
        "Friday 20 November 2026. Left out on purpose, from earlier days:",
        "ICJ rules Myanmar committed genocide (19 Nov) \u00b7 Houthi strike "
        "on Riyadh's PIF tower (19 Nov) \u00b7 Xi\u2013Trump\u2013Putin summit "
        "(19 Nov) \u00b7",
        "Anthropic IPO priced at $83 (18 Nov) \u00b7 Bavuma ruled out of 2nd "
        "Test (19 Nov). Sources: Reuters, BBC, NDTV, NPR, Al Jazeera, The "
        "Hindu, NASA, Space.com, ChessBase India.",
    ]
    for i, ln in enumerate(lines):
        cv.text(MARGIN, y + 5 + i * 9, ln, GREY, 1)


def build():
    cv = Canvas(W, H, PAPER)
    masthead(cv)
    # Row A: the two biggest stories of the day.
    y = 86
    draw_lead(cv, MARGIN, y, 492, 152, LEADS[0], 56)
    draw_lead(cv, MARGIN + 492 + GAP, y, 492, 152, LEADS[1], 56)
    cv.vline(MARGIN + 492 + GAP // 2, y, 152, LIGHTGREY, 1)
    # Rows B-D: three leads each.
    y = 244
    for row in range(3):
        for col in range(3):
            idx = 2 + row * 3 + col
            draw_lead(cv, MARGIN + col * (COLW + GAP), y, COLW, 120,
                      LEADS[idx], 44)
        y += 126
    # Row E: the last two leads and the map.
    draw_lead(cv, MARGIN, y, COLW, 112, LEADS[11], 40)
    draw_lead(cv, MARGIN + COLW + GAP, y, COLW, 112, LEADS[12], 40)
    mx = MARGIN + 2 * (COLW + GAP)
    cv.text(mx, y, "THE MAP", RED, 1)
    cv.hline(mx, y + 10, COLW, INK, 1)
    draw_map(cv, mx, y + 12, COLW, 100)
    # Briefs, then the date-check footer.
    y = 748
    end = briefs_block(cv, MARGIN, y, W - 2 * MARGIN)
    footer(cv, end + 6)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.dirname(
        os.path.abspath(__file__))
    path = os.path.join(out_dir, OUT_NAME)
    cv = build()
    size = write_png(cv, path)
    print(f"wrote {path} {cv.w}x{cv.h} {size} bytes")


if __name__ == "__main__":
    main()

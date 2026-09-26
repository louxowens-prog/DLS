"""Glossy toy icons used across the scenes. Each draws centred at (x, y) with size s (about 200*s px)."""
import math

import numpy as np
import skia

import sr
from sr import CYAN, INK, LEMON, LIME, PINK, RED, TANG, VIOLET, WHITE, darker, lighter, paint, path


def _g(c, pts, color, rim=None, lw=5):
    sr.glossy(c, path(pts), color, rim=rim or lighter(color, 0.7), lw=lw)


def _xf(pts, x, y, s):
    return np.asarray(pts, np.float32) * s + np.array([x, y], np.float32)


def chess_king(c, x, y, s, color=(245, 245, 255)):
    body = [(-60, 100), (60, 100), (48, 60), (30, 50), (40, -20), (22, -40), (30, -60), (-30, -60), (-22, -40), (-40, -20), (-30, 50), (-48, 60)]
    _g(c, _xf(body, x, y, s), color)
    _g(c, _xf([(-8, -60), (8, -60), (8, -80), (22, -80), (22, -94), (8, -94), (8, -108), (-8, -108), (-8, -94), (-22, -94), (-22, -80), (-8, -80)], x, y, s), LEMON)


def chess_knight(c, x, y, s, color=(40, 30, 70)):
    k = [(-55, 100), (55, 100), (45, 60), (38, 20), (44, -20), (30, -62), (10, -86), (0, -110), (-10, -84), (-34, -72), (-60, -40), (-66, -16),
         (-50, -8), (-30, -18), (-16, -12), (-34, 22), (-44, 60)]
    _g(c, _xf(k, x, y, s), color, rim=CYAN)
    c.drawCircle(x - 18 * s, y - 52 * s, 6 * s, paint(WHITE))


def tile(c, x, y, s, kind, T=0.0):
    """An 'image' tile for the recognition test: a glossy card with a simple picture."""
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 90 * s, y - 90 * s, 180 * s, 180 * s), 22 * s, 22 * s)
    p = skia.Path()
    p.addRRect(r)
    sr.glossy(c, p, {"cat": LEMON, "dog": TANG, "car": CYAN, "bird": LIME, "flower": PINK}[kind], lw=5)
    col = INK
    if kind == "cat":
        head = sr.ellipse(x, y + 10 * s, 50 * s, 42 * s)
        c.drawPath(path(head), paint(WHITE))
        for side in (-1, 1):
            c.drawPath(path([(x + side * 44 * s, y - 10 * s), (x + side * 36 * s, y - 58 * s), (x + side * 10 * s, y - 28 * s)]), paint(WHITE))
            c.drawCircle(x + side * 18 * s, y + 4 * s, 7 * s, paint(col))
    elif kind == "dog":
        c.drawPath(path(sr.ellipse(x, y + 10 * s, 48 * s, 44 * s)), paint(WHITE))
        for side in (-1, 1):
            c.drawPath(path(sr.ellipse(x + side * 46 * s, y + 8 * s, 16 * s, 34 * s)), paint((120, 70, 40)))
            c.drawCircle(x + side * 16 * s, y, 7 * s, paint(col))
        c.drawCircle(x, y + 24 * s, 10 * s, paint(col))
    elif kind == "car":
        c.drawPath(path([(x - 60 * s, y + 20 * s), (x - 40 * s, y - 14 * s), (x + 30 * s, y - 14 * s), (x + 62 * s, y + 20 * s)]), paint(WHITE))
        for side in (-1, 1):
            c.drawCircle(x + side * 34 * s, y + 26 * s, 14 * s, paint(col))
    elif kind == "bird":
        c.drawPath(path(sr.ellipse(x, y + 8 * s, 44 * s, 30 * s)), paint(WHITE))
        c.drawPath(path([(x + 40 * s, y), (x + 70 * s, y + 8 * s), (x + 40 * s, y + 16 * s)]), paint(TANG))
        c.drawCircle(x + 18 * s, y - 2 * s, 6 * s, paint(col))
    else:
        for k in range(6):
            a = k / 6 * 2 * math.pi + T
            c.drawCircle(x + 32 * s * math.cos(a), y + 32 * s * math.sin(a), 22 * s, paint(WHITE))
        c.drawCircle(x, y, 20 * s, paint(LEMON))


def gauge(c, x, y, r, value, label, lit, T=0.0, color=CYAN):
    """A chrome dashboard gauge; value 0..1 sweeps the needle; lit adds glow."""
    c.drawCircle(x, y, r * 1.12, paint(shader=sr.lin((x, y - r), (x, y + r), [(250, 250, 255), (120, 125, 150), (220, 225, 240)])))
    c.drawCircle(x, y, r, paint(shader=sr.rad((x, y - r * 0.3), r * 1.2, [(50, 40, 90), (15, 10, 35)])))
    for k in range(9):
        a = math.radians(135 + k * 270 / 8)
        c.drawLine(x + r * 0.78 * math.cos(a), y + r * 0.78 * math.sin(a), x + r * 0.92 * math.cos(a), y + r * 0.92 * math.sin(a),
                   paint(WHITE if k < 6 else RED, stroke=r * 0.05))
    if lit > 0:
        arc = skia.Path()
        arc.addArc(skia.Rect.MakeXYWH(x - r * 0.85, y - r * 0.85, r * 1.7, r * 1.7), 135, 270 * value)
        c.drawPath(arc, paint(color, 0.9 * lit, stroke=r * 0.12, blur=r * 0.05))
    a = math.radians(135 + 270 * value)
    c.drawLine(x, y, x + r * 0.8 * math.cos(a), y + r * 0.8 * math.sin(a), paint(RED if lit else (200, 60, 80), stroke=r * 0.07))
    c.drawCircle(x, y, r * 0.1, paint(WHITE))
    c.drawOval(skia.Rect.MakeXYWH(x - r * 0.6, y - r * 0.85, r * 1.2, r * 0.45), paint(WHITE, 0.18, blur=r * 0.05))
    f = sr.font("bungee-400", r * 0.3)
    lines = label.split("\n")
    for i, ln in enumerate(lines):
        w = f.measureText(ln)
        c.drawString(ln, x - w / 2, y + r * 1.42 + i * r * 0.34, f, paint(WHITE if lit else (190, 190, 220)))


def engine_block(c, x, y, s, T):
    blk = [(-150, 80), (150, 80), (170, -40), (-170, -40)]
    _g(c, _xf(blk, x, y, s), (200, 205, 225), rim=CYAN)
    for k in range(4):
        px = x + (-105 + k * 70) * s
        up = 30 * math.sin(T * 25 + k * 1.6) * s
        _g(c, _xf([(-24, 0), (24, 0), (24, -70), (-24, -70)], px, y - 40 * s + up, s), (245, 245, 255))
        c.drawCircle(px, y - 115 * s + up, 16 * s, paint(sr.TANG, blur=4 * s))
    pl = skia.Path()
    pl.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 130 * s, y + 5 * s, 260 * s, 56 * s), 10 * s, 10 * s))
    sr.glossy(c, pl, PINK, lw=4)
    f = sr.font("bungee-400", 30 * s)
    t = "GENERAL LEARNER"
    c.drawString(t, x - f.measureText(t) / 2, y + 45 * s, f, paint(WHITE))


def speedo(c, x, y, r, v, label="SKILL"):
    gauge(c, x, y, r, v, label, 1.0, color=LIME)


def bulb(c, x, y, s, lit=1.0):
    c.drawCircle(x, y, 60 * s, paint(LEMON, 0.9 * lit + 0.1))
    c.drawCircle(x, y, 110 * s, paint(LEMON, 0.35 * lit, blur=30 * s))
    c.drawRect(skia.Rect.MakeXYWH(x - 28 * s, y + 50 * s, 56 * s, 40 * s), paint((170, 175, 200)))
    c.drawCircle(x - 20 * s, y - 20 * s, 14 * s, paint(WHITE, 0.9))


def chip(c, x, y, s, label="", color=CYAN):
    body = skia.Path()
    body.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 80 * s, y - 60 * s, 160 * s, 120 * s), 14 * s, 14 * s))
    for k in range(5):
        for side in (-1, 1):
            c.drawRect(skia.Rect.MakeXYWH(x - 70 * s + k * 32 * s, y + side * 66 * s - 8 * s, 14 * s, 16 * s), paint((200, 200, 215)))
    sr.glossy(c, body, (40, 30, 80), rim=color, lw=4)
    if label:
        f = sr.font("bungee-400", 26 * s)
        c.drawString(label, x - f.measureText(label) / 2, y + 10 * s, f, paint(color))


def cup(c, x, y, s, T=0.0):
    body = [(-60, -50), (60, -50), (48, 60), (-48, 60)]
    _g(c, _xf(body, x, y, s), WHITE, rim=PINK)
    c.drawOval(skia.Rect.MakeXYWH(x - 56 * s, y - 62 * s, 112 * s, 26 * s), paint((110, 60, 30)))
    c.drawCircle(x + 70 * s, y, 26 * s, paint(WHITE, stroke=12 * s))
    for k in range(3):
        ph = T * 3 + k
        st = sr.bez((x - 30 * s + k * 30 * s, y - 70 * s), (x - 50 * s + k * 30 * s + 20 * math.sin(ph) * s, y - 120 * s),
                    (x - 25 * s + k * 30 * s, y - 170 * s))
        c.drawPath(path(st, closed=False), paint(WHITE, 0.7, stroke=10 * s, blur=3 * s))


def chair(c, x, y, s, color=TANG, broken=False):
    _g(c, _xf([(-40, 0), (40, 0), (40, 14), (-40, 14)], x, y, s), color)
    _g(c, _xf([(-40, -80), (-28, -80), (-28, 0), (-40, 0)], x, y, s), color)
    for lx in (-36, 32) if not broken else (-36,):
        c.drawRect(skia.Rect.MakeXYWH(x + lx * s, y + 14 * s, 8 * s, 60 * s), paint(darker(color, 0.6)))


def guest(c, x, y, s, color=PINK):
    c.drawCircle(x, y - 70 * s, 26 * s, paint(sr.cast_skin if hasattr(sr, "cast_skin") else (255, 196, 160)))
    _g(c, _xf([(-34, -40), (34, -40), (40, 30), (-40, 30)], x, y, s), color)


def broccoli(c, x, y, s):
    c.drawRect(skia.Rect.MakeXYWH(x - 16 * s, y - 20 * s, 32 * s, 80 * s), paint((150, 220, 120)))
    for dx, dy, r in ((-40, -40, 40), (0, -70, 46), (40, -40, 40), (-18, -20, 34), (22, -18, 34)):
        c.drawCircle(x + dx * s, y + dy * s, r * s, paint(shader=sr.rad((x + dx * s - 10 * s, y + dy * s - 10 * s), r * s * 1.2, [LIME, (40, 170, 60)])))


def peanut(c, x, y, s):
    for dy in (-34, 34):
        c.drawCircle(x, y + dy * s, 42 * s, paint(shader=sr.rad((x - 12 * s, y + dy * s - 12 * s), 52 * s, [(250, 220, 160), (200, 150, 90)])))
    c.drawPath(path([(x - 80 * s, y - 80 * s), (x + 80 * s, y + 80 * s)], closed=False), paint(RED, stroke=16 * s))
    c.drawCircle(x, y, 100 * s, paint(RED, stroke=16 * s))


def clock(c, x, y, s, hh=6, mm=0):
    c.drawCircle(x, y, 90 * s, paint(shader=sr.rad((x - 20 * s, y - 20 * s), 110 * s, [WHITE, (220, 225, 245)])))
    c.drawCircle(x, y, 90 * s, paint(INK, stroke=10 * s))
    a_h = math.radians((hh % 12) * 30 - 90 + mm * 0.5)
    a_m = math.radians(mm * 6 - 90)
    c.drawLine(x, y, x + 45 * s * math.cos(a_h), y + 45 * s * math.sin(a_h), paint(INK, stroke=12 * s))
    c.drawLine(x, y, x + 70 * s * math.cos(a_m), y + 70 * s * math.sin(a_m), paint(RED, stroke=8 * s))


def oven(c, x, y, s, T=0.0):
    _g(c, _xf([(-100, -90), (100, -90), (100, 90), (-100, 90)], x, y, s), (220, 220, 235), rim=CYAN)
    c.drawRect(skia.Rect.MakeXYWH(x - 76 * s, y - 40 * s, 152 * s, 100 * s), paint((40, 20, 30)))
    for k in range(6):
        fh = (40 + 30 * math.sin(T * 20 + k)) * s
        fx = x - 60 * s + k * 24 * s
        c.drawPath(path([(fx - 12 * s, y + 55 * s), (fx, y + 55 * s - fh), (fx + 12 * s, y + 55 * s)]), paint([RED, TANG, LEMON][k % 3]))


def wine(c, x, y, s, tilt=0.0, T=0.0, drops=0.0):
    c.save()
    c.translate(x, y)
    c.rotate(tilt)
    bowl = sr.bez((-50 * s, -110 * s), (-60 * s, 20 * s), (0, 20 * s), n=16)
    bowl2 = sr.bez((0, 20 * s), (60 * s, 20 * s), (50 * s, -110 * s), n=16)
    c.drawPath(path(np.vstack([bowl, bowl2])), paint((230, 240, 255), 0.55))
    c.drawPath(path([(-44 * s, -30 * s), (44 * s, -30 * s), (30 * s, 8 * s), (-30 * s, 8 * s)]), paint((190, 20, 70)))
    c.drawRect(skia.Rect.MakeXYWH(-5 * s, 20 * s, 10 * s, 80 * s), paint((230, 240, 255), 0.7))
    c.drawOval(skia.Rect.MakeXYWH(-40 * s, 96 * s, 80 * s, 16 * s), paint((230, 240, 255), 0.7))
    c.restore()
    rng = np.random.default_rng(3)
    for k in range(14):
        a = rng.uniform(-0.6, 0.6)
        d = drops * rng.uniform(80, 260) * s
        c.drawCircle(x + 60 * s + d * math.cos(a), y - 40 * s + d * math.sin(a) + 120 * drops ** 2 * s, rng.uniform(8, 18) * s, paint((200, 20, 80)))


def house(c, x, y, s):
    _g(c, _xf([(-200, 0), (200, 0), (200, -220), (-200, -220)], x, y, s), (255, 220, 240), rim=PINK)
    _g(c, _xf([(-240, -210), (0, -380), (240, -210)], x, y, s), RED)
    _g(c, _xf([(-40, 0), (40, 0), (40, -120), (-40, -120)], x, y, s), VIOLET)
    for wx in (-130, 130):
        c.drawRect(skia.Rect.MakeXYWH(x + (wx - 45) * s, y - 170 * s, 90 * s, 70 * s), paint(shader=sr.lin((0, y - 170 * s), (0, y - 100 * s), [LEMON, TANG])))
        c.drawRect(skia.Rect.MakeXYWH(x + (wx - 45) * s, y - 170 * s, 90 * s, 70 * s), paint(INK, stroke=5))


def mountain(c, x, y, s, color=(200, 220, 255)):
    _g(c, _xf([(-260, 0), (-60, -330), (40, -240), (120, -380), (300, 0)], x, y, s), color, rim=CYAN)
    _g(c, _xf([(-100, -270), (-60, -330), (-20, -275), (-50, -250)], x, y, s), WHITE)


def book(c, x, y, s, color=RED, title=""):
    b = skia.Path()
    b.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 90 * s, y - 120 * s, 180 * s, 240 * s), 10 * s, 10 * s))
    sr.glossy(c, b, color, lw=5)
    c.drawRect(skia.Rect.MakeXYWH(x - 78 * s, y - 110 * s, 14 * s, 220 * s), paint(darker(color, 0.6)))
    if title:
        f = sr.font("bungee-400", 22 * s)
        for i, ln in enumerate(title.split("\n")):
            c.drawString(ln, x - f.measureText(ln) / 2 + 8 * s, y - 40 * s + i * 30 * s, f, paint(WHITE))


def roller(c, x, y, s, color=WHITE):
    c.drawRect(skia.Rect.MakeXYWH(x - 90 * s, y - 30 * s, 180 * s, 60 * s), paint(color))
    c.drawRect(skia.Rect.MakeXYWH(x - 90 * s, y - 30 * s, 180 * s, 60 * s), paint(INK, stroke=5))
    c.drawLine(x, y - 30 * s, x, y - 160 * s, paint((200, 200, 215), stroke=10 * s))
    c.drawRect(skia.Rect.MakeXYWH(x - 14 * s, y - 260 * s, 28 * s, 100 * s), paint(PINK))


def firework(c, x, y, r, T, t0, color=LEMON):
    k = sr.ramp(T, t0, t0 + 0.6)
    if k <= 0 or k >= 1:
        return
    for i in range(18):
        a = i / 18 * 2 * math.pi
        rr = r * sr.ease(k)
        c.drawCircle(x + rr * math.cos(a), y + rr * math.sin(a) + 40 * k * k, 10 * (1 - k) + 3, paint(color, 1 - k * 0.8))

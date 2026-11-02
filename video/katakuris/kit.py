"""Shared scene props and effects."""
import math

import numpy as np
import skia

import bg
import kk
from kk import (BLOOD, CREAM, HOT, INK, KEY, LEMON, LILAC, MINT, ORANGE, PINK, SKIN, SKY, WHITE, W, H, bez, boil,
                clay_ellipse, clay_path, clay_poly, clay_shadow, lin, mix, paint, path, rad, smooth, twos)


def backdrop(st, img):
    st.c.drawImage(img, 0, 0)


def plaque(c, s, x=540, y=1240, size=30, tag="plaque"):
    """A small source label, like a TV news lower-third chip."""
    f = kk.font("rounded-800", size)
    w = f.measureText(s)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x - w / 2 - 22, y - size * 1.05, x + w / 2 + 22, y + size * 0.45), 14, 14),
                paint((20, 10, 50), 0.85))
    kk.text(c, s, x, y, size, "rounded-800", WHITE, tag=tag)


def tag_label(c, s, x, y, size=30, color=HOT, tag="tag", rot=-4):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    f = kk.font("rounded-900", size)
    w = f.measureText(s)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-w / 2 - 16, -size, w / 2 + 16, size * 0.4), 10, 10), paint(color))
    kk.text(c, s, 0, 0, size, "rounded-900", WHITE, tag=tag)
    c.restore()


def clay_house(c, x, y, s, T, seed=0, wall=(250, 230, 190), roof=(210, 60, 60), sink=0.0):
    t = twos(T)
    c.save()
    c.translate(x, y + sink * 200 * s)
    c.scale(s, s)
    clay_shadow(c, 0, 0, 150)
    clay_poly(c, [(-120, 0), (-120, -170), (120, -170), (120, 0)], wall, t, seed, amp=5)
    clay_poly(c, [(-150, -160), (0, -290), (150, -160)], roof, t, seed + 1, amp=5)
    clay_poly(c, [(-30, 0), (-30, -90), (30, -90), (30, 0)], (150, 90, 60), t, seed + 2, amp=3, prints=0)
    for sx in (-1, 1):
        clay_poly(c, [(sx * 80 - 25, -135), (sx * 80 + 25, -135), (sx * 80 + 25, -95), (sx * 80 - 25, -95)], (120, 190, 255), t, seed + 3 + sx, amp=2, prints=0, marks=0)
    c.restore()


def clay_hand(c, x, y, s, T, seed=0, rot=0.0, grab=0.0, color=(255, 190, 150)):
    """A big clay hand reaching down from above (grab 0 open .. 1 closed)."""
    t = twos(T)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    clay_poly(c, [(-60, -600), (60, -600), (70, -120), (-70, -120)], (90, 120, 200), t, seed + 9, amp=6)
    clay_ellipse(c, 0, -60, 95, 85, color, t, seed)
    for k in range(4):
        fx = -60 + k * 40
        L = 110 - abs(k - 1.5) * 12
        ang = (1 - grab) * (k - 1.5) * 8
        c.save()
        c.translate(fx, 0)
        c.rotate(ang)
        clay_ellipse(c, 0, L * (0.5 - 0.35 * grab), 20, L * (0.5 - 0.25 * grab), color, t, seed + 10 + k, amp=0.05, prints=0, marks=0)
        c.restore()
    clay_ellipse(c, 95, -40, 22, 55, color, t, seed + 20, rot=-40 + 40 * grab, prints=0, marks=0)
    c.restore()


def puff(c, x, y, t, r=160, seed=0):
    """A smoke puff and a burst of plastic CG stars (something appearing from nowhere)."""
    if t < 0 or t > 0.8:
        return
    k = t / 0.8
    for i in range(9):
        a = i * 2 * math.pi / 9 + seed
        d = r * (0.3 + k)
        c.drawCircle(x + d * math.cos(a), y + d * math.sin(a) * 0.6, r * 0.35 * (1 - k * 0.6), paint(WHITE, 0.85 * (1 - k)))
    for i in range(5):
        a = i * 2 * math.pi / 5 + 0.3
        kk.cg_star(c, x + r * 1.3 * k * math.cos(a), y + r * 1.3 * k * math.sin(a), 34 * (1 - k * 0.5), t * 3, seed=i,
                   color=[LEMON, HOT, MINT, LILAC, ORANGE][i])


def rain(c, T, n=110, color=(200, 210, 255), a=0.55, seed=3, x0=0, x1=W, y0=0, y1=H):
    rng = np.random.default_rng(seed)
    for i in range(n):
        x = rng.uniform(x0, x1)
        sp = rng.uniform(1400, 2000)
        y = y0 + ((rng.uniform(0, 1) * (y1 - y0) + T * sp) % (y1 - y0))
        c.drawLine(x, y, x - 8, y + 46, paint(color, a, stroke=2.5))


def paper_snow(c, T, n=60, seed=5, color=WHITE):
    rng = np.random.default_rng(seed)
    for i in range(n):
        x = rng.uniform(0, W) + 40 * math.sin(T * 1.5 + i)
        y = (rng.uniform(0, H) + T * rng.uniform(90, 180)) % H
        s = rng.uniform(8, 16)
        c.save()
        c.translate(x, y)
        c.rotate(T * 90 + i * 30)
        c.drawRect(skia.Rect.MakeLTRB(-s, -s * 0.6, s, s * 0.6), paint(color, 0.9))
        c.restore()


def confetti(c, T, n=90, seed=7, t0=0.0):
    rng = np.random.default_rng(seed)
    for i in range(n):
        x = rng.uniform(0, W) + 60 * math.sin(T * 2 + i)
        y = -40 + ((T - t0) * rng.uniform(250, 500) + rng.uniform(0, H)) % (H + 80)
        cc = [HOT, LEMON, MINT, SKY, ORANGE, LILAC][i % 6]
        c.save()
        c.translate(x, y)
        c.rotate(T * 200 + i * 40)
        c.drawRect(skia.Rect.MakeLTRB(-10, -5, 10, 5), paint(cc))
        c.restore()


def firework(c, x, y, t, color=LEMON, r=220, seed=0):
    """A CG firework: a burst of glowing dots with trails."""
    if t < 0 or t > 1.2:
        return
    k = ease_out(t / 1.2)
    rng = np.random.default_rng(seed)
    with kk.layer(c, 1.0, skia.BlendMode.kPlus):
        for i in range(26):
            a = i * 2 * math.pi / 26 + rng.uniform(-0.1, 0.1)
            d = r * k
            px, py = x + d * math.cos(a), y + d * math.sin(a) + 60 * k * k
            c.drawLine(x + d * 0.7 * math.cos(a), y + d * 0.7 * math.sin(a) + 40 * k * k, px, py, paint(color, 0.6 * (1 - k), stroke=4))
            c.drawCircle(px, py, 7 * (1 - k * 0.5), paint(color, 1 - k))


def ease_out(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def mirrorball(c, x, y, r, T):
    """A CG disco ball: chrome facets catching coloured light, spinning."""
    c.drawLine(x, 0, x, y - r, paint((200, 200, 210), stroke=4))
    c.save()
    c.clipPath(path(kk.ellipse(x, y, r, r, 48)), doAntiAlias=True)
    c.drawCircle(x, y, r, paint(shader=rad((x - r * 0.3, y - r * 0.3), r * 1.3, [(255, 255, 255), (170, 180, 200), (70, 70, 90)])))
    rows = 9
    for j in range(rows):
        lat = -math.pi / 2 + (j + 0.5) * math.pi / rows
        yy = y + r * math.sin(lat)
        rr = r * math.cos(lat)
        n = max(4, int(18 * math.cos(lat)))
        for i in range(n):
            lon = (i / n) * 2 * math.pi + T * 1.5
            if math.cos(lon) < 0:
                continue
            xx = x + rr * math.sin(lon)
            bright = (i + j + int(T * 10)) % 5 == 0
            cc = [WHITE, (255, 150, 220), (150, 220, 255), LEMON][(i * 3 + j) % 4] if bright else (120, 125, 145)
            c.drawRect(skia.Rect.MakeXYWH(xx - 6, yy - 6, 12, 12), paint(cc, 0.9))
    c.restore()


def spotlight(c, x0, y0, x1, y1, w, color, a=0.35):
    with kk.layer(c, 1.0, skia.BlendMode.kPlus):
        c.drawPath(path([(x0 - 10, y0), (x0 + 10, y0), (x1 + w, y1), (x1 - w, y1)]),
                   paint(shader=lin((x0, y0), (x1, y1), [(*color, a), (*color, a * 0.3)])))
        c.drawOval(skia.Rect.MakeLTRB(x1 - w, y1 - w * 0.25, x1 + w, y1 + w * 0.25), paint(color, a * 0.8))


def tv(c, x, y, s, T, draw_screen=None, tag="tv"):
    """A chunky CRT television (CG plastic) with an image on the screen."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-330, -260, 330, 260), 40, 40), paint(shader=lin((0, -260), (0, 260), [(210, 200, 190), (140, 130, 125)])))
    scr = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-280, -210, 170, 210), 50, 50)
    c.drawRRect(scr, paint((20, 30, 30)))
    c.save()
    c.clipRRect(scr, doAntiAlias=True)
    if draw_screen:
        draw_screen(c, -280, -210, 170, 210)
    for k in range(0, 420, 6):
        c.drawLine(-280, -210 + k, 170, -210 + k, paint(INK, 0.15, stroke=2))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-260, -195, -60, -120), 40, 40), paint(WHITE, 0.15))
    c.restore()
    for k in range(2):
        c.drawCircle(250, -120 + k * 110, 34, paint((80, 80, 80)))
    c.drawRect(skia.Rect.MakeLTRB(-220, 260, 220, 300), paint((90, 80, 80)))
    c.restore()


def phone(c, x, y, s, T, draw_screen=None):
    """A 2000s-meets-now phone (glossy CG) with a feed on it."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-230, -420, 230, 420), 50, 50), paint(shader=lin((-230, 0), (230, 0), [(60, 60, 70), (20, 20, 25)])))
    scr = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-205, -380, 205, 380), 30, 30)
    c.drawRRect(scr, paint(WHITE))
    c.save()
    c.clipRRect(scr, doAntiAlias=True)
    if draw_screen:
        draw_screen(c, -205, -380, 205, 380)
    c.restore()
    c.restore()


def big_button(c, x, y, s, press=0.0, label="STOP", tag="button"):
    """The big red emergency STOP button (glossy CG)."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawOval(skia.Rect.MakeLTRB(-230, -40, 230, 90), paint(INK, 0.4, blur=12))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-220, -60, 220, 60), 40, 40), paint(shader=lin((0, -60), (0, 60), [LEMON, (200, 160, 0)])))
    for k in range(-4, 5):
        c.drawLine(k * 50 - 20, -60, k * 50 + 20, 60, paint(INK, 0.8, stroke=14))
    dy = 30 * press
    c.drawOval(skia.Rect.MakeLTRB(-160, -120 + dy, 160, 20 + dy), paint((140, 0, 10)))
    c.drawOval(skia.Rect.MakeLTRB(-160, -160 + dy, 160, -10 + dy), paint(shader=rad((-40, -120 + dy), 200, [(255, 120, 120), (230, 20, 30), (150, 0, 10)])))
    c.drawOval(skia.Rect.MakeLTRB(-100, -150 + dy, 10, -110 + dy), paint(WHITE, 0.5))
    kk.text(c, label, 0, -65 + dy, 56, "dela-400", WHITE, tag=tag, outline=(120, 0, 10), ow=8)
    c.restore()


def creature_giant(c, x, y, s, T):
    import cast
    cast.creature(c, x, y, s, T, mood="open", look=(0.0, 0.3))


def clay_x(c, x, y, s, T, seed=0, color=BLOOD):
    """A red X rolled from two clay snakes."""
    t = twos(T)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    import cast
    for a in (45, -45):
        c.save()
        c.rotate(a)
        clay_path(c, cast._capsule(-120, 0, 120, 0, 30), color, t, seed + (a > 0), prints=1, marks=1)
        c.restore()
    c.restore()


def window_frame(c, x0, y0, x1, y1, color=WHITE):
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(color, stroke=18))

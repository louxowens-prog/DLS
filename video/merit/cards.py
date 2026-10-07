"""The title and the chapter cards, designed like the cover of a 1983 heavy-metal album or a fantasy paperback:
chrome lettering with a sky-to-sunset gradient and a hard horizon line, sparkling glints, an ornamental frame of
thorned vines and punched-card sigils, a roman numeral in a medallion, all on a painted nebula."""
import math

import numpy as np
import skia

import gel as G
import kit as K
import world as Wd
from kit import BLACK, WHITE, W, H, mix, paint

CHAPTERS = {1: "The Inheritance", 2: "The Pattern", 3: "The Multitude", 4: "The Verdict"}
NUMERALS = {1: "I", 2: "II", 3: "III", 4: "IV"}
TINT = {1: (40, 70, 230), 2: (220, 20, 30), 3: (220, 30, 160), 4: (150, 0, 10)}


def chrome(c, s, x, y, size, fname="newrocker-400", a=1.0, glow=(255, 60, 40), glow_k=1.0, T=0.0, glints=True,
           tag="title", sweep=None):
    """Chrome lettering centred at x, baseline y. sweep (0..1): a band of light travelling across the letters."""
    f = K.font(fname, size)
    w = f.measureText(s)
    x0 = x - w / 2
    top, bot = y - size * 0.74, y + size * 0.06
    mid = top + (bot - top) * 0.52
    if glow_k > 0:
        c.drawString(s, x0, y, f, G.glow_paint(glow, 0.55 * a * glow_k, blur=size * 0.18))
        c.drawString(s, x0, y, f, G.glow_paint(glow, 0.35 * a * glow_k, blur=size * 0.5))
    c.drawString(s, x0 + size * 0.03, y + size * 0.05, f, paint((0, 0, 0), 0.8 * a, stroke=size * 0.1))
    c.drawString(s, x0, y, f, paint((14, 8, 18), a, stroke=size * 0.09))
    sh = K.lin((0, top), (0, bot), [(30, 50, 150), (120, 160, 240), (236, 244, 255), (70, 36, 28), (180, 90, 40), (255, 190, 90), (255, 240, 200)],
               [0.0, 0.3, (mid - top) / (bot - top) - 0.01, (mid - top) / (bot - top) + 0.01, 0.72, 0.9, 1.0])
    c.drawString(s, x0, y, f, paint(shader=sh, a=a))
    c.drawString(s, x0, y, f, paint((255, 255, 255), 0.55 * a, stroke=max(1.5, size * 0.012)))
    if sweep is not None and 0 <= sweep <= 1:
        c.save()
        sx = x0 - size + (w + 2 * size) * sweep
        band = K.lin((sx - size * 0.4, top), (sx + size * 0.4, bot), [(255, 255, 255, 0.0), (255, 255, 255, 0.85), (255, 255, 255, 0.0)])
        p = paint(shader=band, a=a)
        p.setBlendMode(skia.BlendMode.kPlus)
        c.drawString(s, x0, y, f, p)
        c.restore()
    if glints:
        rng = K.rng_at(len(s), 7)
        for i in range(4):
            gx = x0 + w * rng.uniform(0.05, 0.95)
            gy = top + (bot - top) * rng.uniform(0.0, 0.4)
            k = max(0.0, math.sin(T * 2.2 + i * 1.9)) ** 6
            glint(c, gx, gy, size * 0.5 * k, a * k)
    K.reg(x0, top, x0 + w, bot + size * 0.2, tag)
    return w


def glint(c, x, y, r, a=1.0, color=(255, 255, 255)):
    """A four-pointed star of light, the sparkle on chrome."""
    if a <= 0.01 or r <= 1:
        return
    for ang, L in ((0, 1.0), (90, 1.0), (45, 0.45), (135, 0.45)):
        c.save()
        c.translate(x, y)
        c.rotate(ang)
        p = K.path([(-r * L, 0), (0, -r * 0.06), (r * L, 0), (0, r * 0.06)])
        c.drawPath(p, G.glow_paint(color, a))
        c.restore()
    c.drawCircle(x, y, r * 0.18, G.glow_paint(color, a, blur=r * 0.1))
    G.pool(c, x, y, r * 0.6, color, 0.5 * a)


def _vine(c, pts, a, col=(200, 170, 120), thorns=True, seed=0):
    p = K.smooth(pts, closed=False)
    c.drawPath(p, paint(col, a, stroke=5))
    c.drawPath(p, paint(mix(col, WHITE, 0.5), 0.4 * a, stroke=1.5))
    if thorns:
        rng = K.rng_at(seed, 3)
        for i in range(1, len(pts) - 1):
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            ang = math.atan2(y1 - y0, x1 - x0) + math.pi / 2 * (1 if i % 2 else -1)
            L = rng.uniform(16, 28)
            c.drawPath(K.path([(x0 - 4, y0), (x0 + math.cos(ang) * L, y0 + math.sin(ang) * L), (x0 + 4, y0)]), paint(col, a))


def frame(c, x0, y0, x1, y1, T, k=1.0, col=(214, 180, 120), seed=0):
    """An ornamental frame drawn in with k (0..1): double rules, thorned vines at the corners, sigils."""
    a = min(1.0, k * 1.5)
    L = k
    for inset, sw in ((0, 5), (18, 2)):
        r = skia.Rect.MakeLTRB(x0 + inset, y0 + inset, x1 - inset, y1 - inset)
        p = skia.Path()
        p.addRect(r)
        meas = skia.PathMeasure(p, False)
        ln = meas.getLength()
        dst = skia.Path()
        meas.getSegment(0, ln * L, dst, True)
        c.drawPath(dst, paint(col, a, stroke=sw))
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        pts = [(cx + sx * 30, cy + sy * 30), (cx + sx * 90, cy + sy * 50), (cx + sx * 150, cy + sy * 40), (cx + sx * 210, cy + sy * 70)]
        _vine(c, pts, a * k, col, seed=int(cx + cy))
        pts = [(cx + sx * 30, cy + sy * 30), (cx + sx * 50, cy + sy * 90), (cx + sx * 40, cy + sy * 150), (cx + sx * 70, cy + sy * 210)]
        _vine(c, pts, a * k, col, seed=int(cx * 2 + cy))
        c.drawCircle(cx + sx * 30, cy + sy * 30, 16, paint(col, a))
        c.drawCircle(cx + sx * 30, cy + sy * 30, 8, paint((20, 10, 16), a))


def sigil(c, x, y, r, T, a=1.0, col=(214, 180, 120)):
    """An eye inside a punched card inside a ring: the mark of the Clerks."""
    c.drawCircle(x, y, r, paint(col, a, stroke=4))
    c.drawCircle(x, y, r * 0.86, paint(col, 0.6 * a, stroke=1.5))
    for i in range(24):
        ang = i / 24 * 6.283 + T * 0.1
        c.drawLine(x + math.cos(ang) * r * 0.88, y + math.sin(ang) * r * 0.88, x + math.cos(ang) * r * 0.98, y + math.sin(ang) * r * 0.98,
                   paint(col, a, stroke=2))
    c.drawRoundRect(skia.Rect.MakeLTRB(x - r * 0.55, y - r * 0.32, x + r * 0.55, y + r * 0.32), 4, 4, paint(col, 0.9 * a, stroke=3))
    eye = K.smooth([(x - r * 0.42, y), (x, y - r * 0.24), (x + r * 0.42, y), (x, y + r * 0.24)])
    c.drawPath(eye, paint(col, a, stroke=3))
    c.drawCircle(x, y, r * 0.11, G.glow_paint((255, 60, 40), a))


def ring(c, x, y, r, T, a=1.0, col=(214, 180, 120)):
    """A medallion ring of ticks, like the edge of a reel."""
    c.drawCircle(x, y, r, paint(col, a, stroke=4))
    c.drawCircle(x, y, r * 0.86, paint(col, 0.6 * a, stroke=1.5))
    for i in range(36):
        ang = i / 36 * 6.283 + T * 0.1
        c.drawLine(x + math.cos(ang) * r * 0.88, y + math.sin(ang) * r * 0.88, x + math.cos(ang) * r * 0.98, y + math.sin(ang) * r * 0.98,
                   paint(col, a, stroke=2))


def nebula(c, T, tint, a=1.0, seed=0):
    """A painted nebula background in one colour, slowly turning."""
    c.drawPaint(paint((4, 2, 8)))
    rng = K.rng_at(seed, 11)
    for i in range(14):
        x = W / 2 + rng.normal(0, 300) + 40 * math.sin(T * 0.2 + i)
        y = H / 2 + rng.normal(0, 500) + 30 * math.cos(T * 0.17 + i)
        r = rng.uniform(200, 520)
        col = mix(tint, (255, 255, 255) if i % 5 == 0 else (0, 0, 0), rng.uniform(0.0, 0.4))
        c.drawCircle(x, y, r, G.glow_paint(col, a * rng.uniform(0.12, 0.3), blend=skia.BlendMode.kScreen, blur=r * 0.45))
    Wd.real_stars(c, T, n=140, y1=H, a=0.6 * a, seed=seed)


def chapter_card(c, n, T, t0, dur=1.5):
    """Chapter n at time T (the card appeared at t0)."""
    u = (T - t0) / dur
    tint = TINT[n]
    nebula(c, T, tint, seed=n)
    c.save()
    z = 1.0 + 0.05 * u
    c.translate(W / 2, 880)
    c.scale(z, z)
    c.translate(-W / 2, -880)
    frame(c, 80, 380, W - 80, 1240, T, k=K.ease(min(1.0, u * 2.2)), seed=n)
    ring(c, W / 2, 570, 118, T, a=K.ease(min(1.0, u * 3)))
    K.text(c, NUMERALS[n], W / 2, 612, 116, "metalmania-400", (255, 230, 200), tag="title", a=K.ease(min(1.0, u * 3)), outline=(20, 8, 12), ow=8)
    K.text(c, "CHAPTER " + NUMERALS[n], W / 2, 790, 54, "cinzel-800", mix(tint, WHITE, 0.6), tag="title", a=K.ease(min(1.0, u * 3)))
    title = CHAPTERS[n]
    size = 132 if len(title) < 13 else 116
    chrome(c, title, W / 2, 955, size, T=T, glow=tint, sweep=(u * 1.4 - 0.2), a=K.ease(min(1.0, u * 2.5 + 0.1)))
    c.drawLine(W / 2 - 220, 1060, W / 2 + 220, 1060, paint((214, 180, 120), K.ease(min(1.0, u * 2)), stroke=3))
    for sd in (-1, 1):
        c.drawCircle(W / 2 + sd * 240, 1060, 9, paint((214, 180, 120), K.ease(min(1.0, u * 2))))
    c.restore()


def title_card(c, T, t0, dur=1.4, wash_col=(255, 40, 30)):
    """INELIGIBLE: chrome over the moon, slammed into place with a flash."""
    u = (T - t0) / dur
    Wd.forest(c, T, moon_r=380, moon_xy=(540, 760), eye=0.0, stars=1.0)
    c.drawPaint(paint((0, 0, 0), 0.35))
    s = 1.0 + 0.25 * max(0.0, 1 - u * 6) ** 2
    c.save()
    c.translate(W / 2, 860)
    c.scale(s, s)
    c.translate(-W / 2, -860)
    chrome(c, "INELIGIBLE", W / 2, 920, 160, T=T, glow=wash_col, sweep=u * 1.3 - 0.15)
    c.restore()
    K.text(c, "A NIGHTMARE IN FOUR CHAPTERS", W / 2, 1040, 40, "cinzeldeco-700", (230, 210, 255), tag="title", a=K.ease(min(1.0, u * 2.5)))

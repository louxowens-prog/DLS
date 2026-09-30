"""The toolkit for the underworld: hand-painted cardboard, chalk scribbles, checkerboard floors in bad perspective,
tape on the seams, wobbly hand lettering, and the rubber-hose cartoon kit (noodle arms, white gloves, pie-cut eyes).

Cartoon things move "on twos" (12 drawings a second) and their lines boil: every drawing is traced again, slightly
differently. Live things (drawn in draw.py-style soft shading, in cast.py) move at 24.
"""
import math

import numpy as np
import skia

import draw as D
from draw import H, INK, W, WHITE, ease, mix, paint, path, ramp

BLACK, CHALK, BONE, GREY, DARK, MID, LIGHT = (8, 8, 8), (236, 234, 226), (226, 222, 206), (128, 126, 120), (40, 38, 36), (96, 94, 90), (190, 188, 180)
OUT = 7.0                                                               # the cartoon outline weight


def twos(T):
    """Cartoon time: held on twos (12 drawings a second)."""
    return math.floor(T * 12) / 12.0


def boil(T):
    return int(math.floor(T * 12)) % 3                                 # three tracings, cycled


def wob(pts, amp=3.0, seed=0, T=0.0):
    """Jitter points like a hand tracing them again (changes on twos)."""
    rng = np.random.default_rng(seed * 101 + boil(T) * 7 + 1)
    return [(x + rng.uniform(-amp, amp), y + rng.uniform(-amp, amp)) for x, y in pts]


def wline(c, x0, y0, x1, y1, col=BLACK, w=OUT, T=0.0, seed=0, amp=2.5, a=1.0):
    """A wobbly inked line."""
    n = max(2, int(math.hypot(x1 - x0, y1 - y0) / 60) + 2)
    pts = [(x0 + (x1 - x0) * i / (n - 1), y0 + (y1 - y0) * i / (n - 1)) for i in range(n)]
    pts = [pts[0]] + wob(pts[1:-1], amp, seed, T) + [pts[-1]]
    c.drawPath(D.smooth(pts, closed=False), paint(col, a, stroke=w))


def blob(c, pts, fill, T=0.0, seed=0, amp=2.5, outline=BLACK, ow=OUT, a=1.0, smooth=True):
    """A flat cartoon shape: boiling outline, flat fill."""
    p = (D.smooth if smooth else path)(wob(pts, amp, seed, T))
    c.drawPath(p, paint(fill, a))
    if outline is not None:
        c.drawPath(p, paint(outline, a, stroke=ow))
    return p


def circ(c, x, y, r, fill, T=0.0, seed=0, outline=BLACK, ow=OUT, a=1.0):
    n = 14
    pts = [(x + r * math.cos(2 * math.pi * i / n), y + r * math.sin(2 * math.pi * i / n)) for i in range(n)]
    return blob(c, pts, fill, T, seed, amp=max(0.8, r * 0.025), outline=outline, ow=ow, a=a)


# ------------------------------------------------------------------ cardboard and paint

def cardboard(c, pts, fill, T=0.0, seed=0, seams=(), tape=True, corrugate=True, a=1.0):
    """A painted cardboard flat: the shape, a darker edge, corrugation ghosts, seams with masking tape."""
    p = path(pts)
    c.drawPath(p, paint(fill, a))
    c.save()
    c.clipPath(p, doAntiAlias=True)
    b = p.computeTightBounds()
    if corrugate:
        for x in np.arange(b.left(), b.right(), 14):
            c.drawLine(x, b.top(), x + 6, b.bottom(), paint(mix(fill, INK, 0.12), 0.35 * a, stroke=2))
    for sx in seams:                                                   # seams between two sheets, taped
        c.drawLine(sx, b.top(), sx + 4, b.bottom(), paint(mix(fill, INK, 0.5), a, stroke=3))
        if tape:
            rng = np.random.default_rng(int(sx) + seed)
            for yy in np.linspace(b.top() + 40, b.bottom() - 40, 3):
                tape_strip(c, sx, yy + rng.uniform(-30, 30), 90, 34, rng.uniform(-12, 12), a=a)
    c.restore()
    c.drawPath(D.smooth(wob(pts, 2.0, seed, T)) if False else p, paint(mix(fill, INK, 0.55), a, stroke=5))


def tape_strip(c, x, y, w, h, rot, a=1.0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.drawRect(skia.Rect.MakeLTRB(-w / 2, -h / 2, w / 2, h / 2), paint((222, 214, 190), 0.8 * a))
    c.drawLine(-w / 2, -h / 2, -w / 2 + 6, h / 2, paint((200, 190, 160), 0.8 * a, stroke=2))
    c.drawLine(w / 2, -h / 2, w / 2 - 5, h / 2, paint((200, 190, 160), 0.8 * a, stroke=2))
    c.restore()


def checker(c, vp, y0, y1, x0l, x0r, x1l, x1r, n_cols=8, n_rows=7, cols=(CHALK, BLACK), skew=0.0, a=1.0):
    """A checkerboard floor in (bad) perspective: trapezoid from (x0l..x0r at y0) to (x1l..x1r at y1)."""
    def at(u, v):                                                       # u across 0..1, v depth 0 (far)..1 (near)
        vv = v ** 1.7
        y = y0 + (y1 - y0) * vv
        xl = x0l + (x1l - x0l) * vv
        xr = x0r + (x1r - x0r) * vv
        return (xl + (xr - xl) * u + skew * (1 - vv) * 60, y)
    for j in range(n_rows):
        for i in range(n_cols):
            q = [at(i / n_cols, j / n_rows), at((i + 1) / n_cols, j / n_rows), at((i + 1) / n_cols, (j + 1) / n_rows),
                 at(i / n_cols, (j + 1) / n_rows)]
            c.drawPath(path(q), paint(cols[(i + j) % 2], a))


def scribble(c, x0, y0, x1, y1, kind="spiral", col=CHALK, seed=0, a=0.8, w=4, density=1.0):
    """Chalky painted patterns on a flat: spirals, zigzags, dots, painted eyes, stars."""
    rng = np.random.default_rng(seed)
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x0, y0, x1, y1))
    if kind == "spiral":
        n = int(6 * density)
        for k in range(n):
            cx, cy = rng.uniform(x0, x1), rng.uniform(y0, y1)
            r0 = rng.uniform(30, 90)
            pts = [(cx + (r0 * t / 30) * math.cos(t * 0.55), cy + (r0 * t / 30) * math.sin(t * 0.55)) for t in range(1, 34)]
            c.drawPath(D.smooth(pts, closed=False), paint(col, a, stroke=w))
    elif kind == "zigzag":
        for yy in np.arange(y0 + 20, y1, 70 / density):
            pts = [(x, yy + (18 if k % 2 else -18)) for k, x in enumerate(np.arange(x0 - 20, x1 + 40, 40))]
            c.drawPath(path(pts, closed=False), paint(col, a, stroke=w))
    elif kind == "dots":
        for _ in range(int(160 * density)):
            c.drawCircle(rng.uniform(x0, x1), rng.uniform(y0, y1), rng.uniform(3, 9), paint(col, a))
    elif kind == "eyes":
        for _ in range(int(12 * density)):
            cx, cy, r = rng.uniform(x0, x1), rng.uniform(y0, y1), rng.uniform(18, 40)
            c.drawOval(skia.Rect.MakeLTRB(cx - r * 1.4, cy - r * 0.8, cx + r * 1.4, cy + r * 0.8), paint(col, a, stroke=w))
            c.drawCircle(cx + rng.uniform(-r * 0.4, r * 0.4), cy, r * 0.45, paint(col, a))
    elif kind == "stars":
        for _ in range(int(26 * density)):
            cx, cy, r = rng.uniform(x0, x1), rng.uniform(y0, y1), rng.uniform(10, 26)
            pts = [(cx + (r if k % 2 == 0 else r * 0.4) * math.cos(k * math.pi / 5 - math.pi / 2),
                    cy + (r if k % 2 == 0 else r * 0.4) * math.sin(k * math.pi / 5 - math.pi / 2)) for k in range(10)]
            c.drawPath(path(pts), paint(col, a))
    elif kind == "hatch":
        for x in np.arange(x0 - (y1 - y0), x1, 26 / density):
            c.drawLine(x, y1, x + (y1 - y0), y0, paint(col, a, stroke=w))
    c.restore()


def spiral_bg(c, cx, cy, T, turns=7, cols=(CHALK, BLACK), speed=2.0):
    """A hypnotic painted spiral filling the frame (the fall)."""
    c.drawRect(skia.Rect.MakeWH(W, H), paint(cols[1]))
    R = 1500
    n = 8
    rot = T * speed * 60
    for k in range(n):
        p = skia.Path()
        a0 = 360 / n * k + rot
        pts = []
        for i in range(120):
            t = i / 119
            r = R * t
            ang = math.radians(a0 + t * 360 * turns * 0.25)
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        for i in range(119, -1, -1):
            t = i / 119
            r = R * t
            ang = math.radians(a0 + 360 / n / 2 + t * 360 * turns * 0.25)
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        c.drawPath(path(pts), paint(cols[0]))


# ------------------------------------------------------------------ hand lettering

def letters(c, s, x, y, size, fname="londrina-900", col=WHITE, T=0.0, seed=0, jitter=1.0, align="center", tag="card",
            outline=None, ow=0.0, a=1.0, shadow=None, track=0.0):
    """Wobbly hand lettering: each letter traced with its own tilt and bounce, re-traced on twos."""
    f = D.font(fname, size)
    widths = [f.measureText(ch) + track for ch in s]
    w = sum(widths) - track
    x0 = x - w / 2 if align == "center" else (x - w if align == "right" else x)
    rng = np.random.default_rng(seed * 13 + boil(T) * 5 + 3)
    xx = x0
    for ch, cw in zip(s, widths):
        dy = rng.uniform(-1, 1) * size * 0.035 * jitter
        rot = rng.uniform(-1, 1) * 4.0 * jitter
        c.save()
        c.translate(xx + cw / 2, y + dy)
        c.rotate(rot)
        if shadow is not None:
            c.drawString(ch, -cw / 2 + size * 0.06, size * 0.07, f, paint(shadow, a))
        if outline is not None:
            c.drawString(ch, -cw / 2, 0, f, paint(outline, a, stroke=ow))
        c.drawString(ch, -cw / 2, 0, f, paint(col, a))
        c.restore()
        xx += cw
    D.reg_local(c, x0, y - size * 0.8, x0 + w, y + size * 0.2, tag)
    return w


def fit(s, fname, size, maxw):
    f = D.font(fname, size)
    w = f.measureText(s)
    return size if w <= maxw else size * maxw / w


# ------------------------------------------------------------------ rubber hose

def hose(c, x0, y0, x1, y1, bend=0.3, w=18, col=BLACK, T=0.0):
    """A noodle limb: one smooth bend, no elbow."""
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, y1 - y0
    cx, cy = mx - dy * bend, my + dx * bend
    p = skia.Path()
    p.moveTo(x0, y0)
    p.quadTo(cx, cy, x1, y1)
    c.drawPath(p, paint(col, stroke=w))


def glove(c, x, y, s=1.0, rot=0.0, point=False, fill=WHITE):
    """The white cartoon glove: puffy, three stitch lines, a cuff."""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    if point:
        fing = [(-12, -8), (40, -16), (44, -4), (8, 4)]                 # index finger out
        c.drawPath(D.smooth(fing), paint(fill))
        c.drawPath(D.smooth(fing), paint(BLACK, stroke=4.5))
    c.drawPath(D.smooth([(-26, -18), (0, -26), (22, -16), (26, 8), (6, 24), (-20, 20), (-30, 0)]), paint(fill))
    c.drawPath(D.smooth([(-26, -18), (0, -26), (22, -16), (26, 8), (6, 24), (-20, 20), (-30, 0)]), paint(BLACK, stroke=4.5))
    for k in (-8, 2, 12):
        c.drawLine(k - 14, -10, k - 4, -14, paint(BLACK, stroke=3))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-44, -14, -26, 14), 6, 6), paint(fill))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-44, -14, -26, 14), 6, 6), paint(BLACK, stroke=4))
    c.restore()


def pie_eye(c, x, y, rx, ry, look=(0.0, 0.0), blink=0.0, white=WHITE):
    """A 1930s pie-cut eye: a white oval, a black pupil with a wedge cut out of it."""
    ry2 = ry * (1 - 0.92 * blink)
    c.drawOval(skia.Rect.MakeLTRB(x - rx, y - ry2, x + rx, y + ry2), paint(white))
    c.drawOval(skia.Rect.MakeLTRB(x - rx, y - ry2, x + rx, y + ry2), paint(BLACK, stroke=4))
    if blink > 0.6:
        return
    px, py = x + look[0] * rx * 0.45, y + look[1] * ry * 0.4
    pr_x, pr_y = rx * 0.55, min(ry2, ry * 0.62)
    c.drawOval(skia.Rect.MakeLTRB(px - pr_x, py - pr_y, px + pr_x, py + pr_y), paint(BLACK))
    wedge = path([(px + pr_x * 0.1, py - pr_y * 0.2), (px + pr_x * 1.1, py - pr_y * 0.95), (px + pr_x * 1.1, py - pr_y * 0.15)])
    c.drawPath(wedge, paint(white))


def shoe(c, x, y, s=1.0, flip=1):
    c.save()
    c.translate(x, y)
    c.scale(s * flip, s)
    c.drawPath(D.smooth([(-14, -18), (30, -20), (48, -4), (40, 8), (-16, 8)]), paint(BLACK))
    c.drawOval(skia.Rect.MakeLTRB(14, -18, 34, -10), paint(WHITE, 0.5))
    c.restore()


def matte_edge(c, p, a=0.5):
    """The pale fringe round a live actor matted into a painted world (cheap blue-screen)."""
    c.drawPath(p, paint(WHITE, a * 0.55, stroke=5, blur=2))


def tinted(tint, c, fn):
    """Paint into the hand-tint layer under the drawing canvas's current transform."""
    if tint is None:
        return
    tint.save()
    tint.setMatrix(c.getTotalMatrix())
    fn(tint)
    tint.restore()

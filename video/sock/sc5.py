"""Chapter 5: MS Paint (chunky aliased pixels in the Windows 98 window, a cursor drawing it live), then PS1-era 3-D:
alignment in practice, Goodhart's law, four things that aren't what they measure, and the boat that won by losing."""
import math

import numpy as np
import skia

import common as C
import diy as K
import media2 as F
import tv
from diy import GOLD, HOT, INK, WHITE, W, H, paint, ramp
from common import E, S, Wx
from media2 import px, ptext

RED, YEL, GRN, BLU, MAG, BLK, GRY, BRN = (255, 0, 0), (255, 255, 0), (0, 160, 0), (0, 0, 255), (255, 0, 255), (0, 0, 0), (128, 128, 128), (128, 64, 0)


class Strokes:
    """A drawing made live: each item (t0, t1, kind, args) appears progressively between t0 and t1; the cursor sits
    at the tip of whatever is being drawn."""

    def __init__(self, items):
        self.items = items

    def draw(self, c, T):
        cur, tool = None, "pencil"
        for t0, t1, kind, a in self.items:
            if T < t0:
                continue
            k = 1.0 if t1 <= t0 else min(1.0, (T - t0) / (t1 - t0))
            tip = _draw(c, kind, a, k, T)
            if k < 1 and tip is not None:
                cur, tool = tip, {"spray": "spray", "fill": "fill", "text": "arrow", "erase": "arrow"}.get(kind, "pencil")
        if cur is not None:
            F.paint_cursor(c, int(cur[0]), int(cur[1]), tool)
        return tool


def _poly_part(pts, k):
    pts = np.asarray(pts, float)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    L = seg.sum() * k
    out = [pts[0]]
    for p, q, s in zip(pts[:-1], pts[1:], seg):
        if L <= 0:
            break
        u = min(1.0, L / s) if s > 0 else 1.0
        out.append(p + (q - p) * u)
        L -= s
    return np.array(out)


def _draw(c, kind, a, k, T):
    if kind == "line":                                          # pts, color, width
        pts, col, w = a
        q = _poly_part(pts, k)
        if len(q) > 1:
            c.drawPath(F.path([tuple(map(int, p)) for p in q], closed=False), px(col, w))
        return q[-1]
    if kind == "rect":                                          # x0, y0, x1, y1, color, filled
        x0, y0, x1, y1, col, filled = a
        if filled:
            if k >= 1:
                c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), px(col))
            return (x1, y1)
        q = _poly_part([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], k)
        c.drawPath(F.path([tuple(map(int, p)) for p in q], closed=False), px(col, 1))
        return q[-1]
    if kind == "ellipse":                                       # cx, cy, rx, ry, color, filled
        cx, cy, rx, ry, col, filled = a
        if filled and k >= 1:
            c.drawOval(skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry), px(col))
            return (cx, cy)
        n = max(2, int(40 * k))
        pts = [(cx + rx * math.cos(2 * math.pi * i / 40), cy + ry * math.sin(2 * math.pi * i / 40)) for i in range(n + 1)]
        c.drawPath(F.path([tuple(map(int, p)) for p in pts], closed=False), px(col, 1))
        return pts[-1]
    if kind == "fill":                                          # a path (list of pts) or an ellipse, filled at once
        shape, col = a
        if True:                                                 # a bucket fill lands all at once
            if shape[0] == "ell":
                _, cx, cy, rx, ry = shape
                c.drawOval(skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry), px(col))
                return (cx, cy)
            c.drawPath(F.path(shape[1]), px(col))
            return shape[1][0]
    if kind == "text":                                          # s, x, y, size, color, font
        s, x, y, size, col, fn = a
        n = int(round(len(s) * k))
        if n:
            w = ptext(c, s[:n], x, y, size, col, fn)
            return (x + w + 2, y - size // 2)
        return (x, y)
    if kind == "spray":                                         # cx, cy, r, n, color, seed
        cx, cy, r, n, col, seed = a
        F.spray(c, cx, cy, r, n * k, col, seed)
        return (cx + 3, cy + 3)
    if kind == "erase":                                         # x0, y0, x1, y1: a white block wiped left to right
        x0, y0, x1, y1 = a
        xe = x0 + (x1 - x0) * k
        c.drawRect(skia.Rect.MakeLTRB(x0, y0, xe, y1), px(WHITE))
        if k < 1:
            c.drawRect(skia.Rect.MakeLTRB(xe - 6, y0, xe, y1), px((255, 160, 200)))
        return (xe, (y0 + y1) / 2)
    return None


def _star(x, y, r):
    return [(x + r * (1 if j % 2 == 0 else 0.45) * math.cos(-math.pi / 2 + j * math.pi / 5),
             y + r * (1 if j % 2 == 0 else 0.45) * math.sin(-math.pi / 2 + j * math.pi / 5)) for j in range(10)]


def robot(t0, x, y, dt=0.12, salute=False):
    """Stroke list for a crude Paint robot at (x, y) = head top-left."""
    it = []
    t = t0
    for kind, a in (("rect", (x, y, x + 40, y + 34, GRY, True)), ("rect", (x, y, x + 40, y + 34, BLK, False)),
                    ("rect", (x + 8, y + 10, x + 14, y + 16, BLU, True)), ("rect", (x + 26, y + 10, x + 32, y + 16, BLU, True)),
                    ("line", ([(x + 12, y + 26), (x + 28, y + 26)], BLK, 2)), ("line", ([(x + 20, y), (x + 20, y - 10)], BLK, 1)),
                    ("ellipse", (x + 20, y - 12, 3, 3, RED, True)),
                    ("rect", (x - 4, y + 38, x + 44, y + 86, (160, 160, 180), True)), ("rect", (x - 4, y + 38, x + 44, y + 86, BLK, False))):
        it.append((t, t + dt, kind, a))
        t += dt
    if salute:
        it.append((t, t + dt, "line", ([(x + 44, y + 50), (x + 60, y + 30), (x + 44, y + 8)], BLK, 3)))
    else:
        it.append((t, t + dt, "line", ([(x + 44, y + 50), (x + 64, y + 70)], BLK, 3)))
    it.append((t + dt, t + 2 * dt, "line", ([(x - 4, y + 50), (x - 24, y + 70)], BLK, 3)))
    return it


def zoom_at(T, plan):
    """plan: [(t0, t1, cx, cy, z)] -> the magnifier for time T (snaps in and out, as Paint's does)."""
    for t0, t1, cx, cy, z in plan:
        if t0 <= T < t1:
            return (cx, cy, z)
    return None


def paint_shot(T, items, title="alignment.bmp - Paint", fg=BLK, status=None, zoom=None, dialog=None):
    st = Strokes(items)
    holder = {}
    def draw(c):
        holder["tool"] = st.draw(c, T)
    a = F.mspaint(draw, tool="pencil", fg=fg, title=title, status=status)
    # mspaint() draws chrome first; redo with the right tool selected (cheap: chrome is tiny at low res)
    a = F.mspaint(draw, tool={"arrow": "text"}.get(holder.get("tool"), holder.get("tool", "pencil")), fg=fg, title=title,
                  status=status if zoom is None else "Zoom: %d%%" % int(zoom[2] * 100), zoom=zoom, dialog=dialog)
    out = np.zeros((H, W, 4), np.uint8)
    out[..., :3] = a[..., :3]
    out[..., 3] = 255
    # the lettering in the canvas is information: register it for the lint (screen coordinates, through the zoom)
    x0c, y0c, x1c, y1c = F.CANVAS
    for t0, t1, kind, args in items:
        if kind == "text" and T >= t0:
            s, x, y, size, col, fn = args
            f = K.font(fn, size)
            bx0, by0, bx1, by1 = x, y - size, x + f.measureText(s), y + 2
            if zoom is not None and zoom[2] > 1.01:
                cx, cy, z = zoom
                cw, ch = (x1c - x0c) / z, (y1c - y0c) / z
                zx0 = min(max(cx - cw / 2, x0c), x1c - cw)
                zy0 = min(max(cy - ch / 2, y0c), y1c - ch)
                tr = lambda u, v: (x0c + (u - zx0) * z, y0c + (v - zy0) * z)
                (bx0, by0), (bx1, by1) = tr(bx0, by0), tr(bx1, by1)
                bx0, by0, bx1, by1 = max(bx0, x0c), max(by0, y0c), min(bx1, x1c), min(by1, y1c)
                if bx1 <= bx0 or by1 <= by0:
                    continue
            K.reg(bx0 * 4, by0 * 4, bx1 * 4, by1 * 4, "paint")
    return out


def s_m_morals(T, idx):
    """'Alignment sounds like teaching morals.' A crude robot at a school desk; a chalkboard: MORALS 101."""
    t0 = S("e1") - 0.45
    items = [(t0, t0 + 0.3, "text", ("CH.5 THE NUMBER", 34, 70, 16, MAG, "silkscreen-700")),
             (t0 + 0.3, t0 + 0.6, "rect", (40, 92, 236, 170, (0, 96, 64), True)), (t0 + 0.6, t0 + 0.7, "rect", (40, 92, 236, 170, BRN, False)),
             (t0 + 0.7, t0 + 1.3, "text", ("MORALS 101", 62, 140, 16, WHITE, "silkscreen-700"))]
    items += robot(t0 + 1.3, 112, 214, 0.1)
    items += [(t0 + 2.6, t0 + 2.8, "ellipse", (132, 200, 20, 5, YEL, False)), (t0 + 2.8, t0 + 2.8, "ellipse", (132, 200, 20, 5, YEL, True)),
              (t0 + 2.9, t0 + 3.1, "rect", (70, 304, 200, 314, BRN, True))]
    return paint_shot(T, items)


def s_m_rated(T, idx):
    """'In practice, it's often training what people rate highly.' Erase MORALS 101; type RATED; spray stars."""
    t0 = S("e1") - 0.45
    base = [(0, 0, "text", ("CH.5 THE NUMBER", 34, 70, 16, MAG, "silkscreen-700")), (0, 0, "rect", (40, 92, 236, 170, (0, 96, 64), True)),
            (0, 0, "rect", (40, 92, 236, 170, BRN, False)), (0, 0, "text", ("MORALS 101", 62, 140, 16, WHITE, "silkscreen-700"))]
    base += [(0, 0, k, a) for _, _, k, a in robot(0, 112, 214, 0.1)]
    base += [(0, 0, "ellipse", (132, 200, 20, 5, YEL, True)), (0, 0, "rect", (70, 304, 200, 314, BRN, True))]
    t1 = Wx("e1", "practice") - 0.1
    items = base + [(t1, t1 + 0.6, "erase", (44, 96, 232, 166)), (t1 + 0.6, t1 + 0.6, "rect", (44, 96, 232, 166, (0, 96, 64), True)),
                    (t1 + 0.7, t1 + 1.5, "text", ("RATED", 92, 124, 16, YEL, "silkscreen-700")),
                    ] + [(t1 + 1.5 + k * 0.15, t1 + 1.5 + k * 0.15, "fill", (("path", _star(78 + k * 32, 148, 12)), YEL)) for k in range(5)]
    for k, (x, y) in enumerate(((60, 230), (200, 220), (190, 290), (52, 300))):
        items.append((t1 + 2.0 + k * 0.15, t1 + 2.4 + k * 0.15, "spray", (x, y, 12, 90, YEL, k)))
    return paint_shot(T, items)


def _figure(x, feet, col=BLK):
    """A stick figure standing at (x, feet): head, body, legs, arms (strokes, all at once)."""
    hy = feet - 90
    return [(0, 0, "ellipse", (x, hy, 11, 11, col, False)), (0, 0, "line", ([(x, hy + 11), (x, feet - 36)], col, 2)),
            (0, 0, "line", ([(x - 12, feet), (x, feet - 36), (x + 12, feet)], col, 2)),
            (0, 0, "line", ([(x - 16, hy + 40), (x, hy + 24), (x + 16, hy + 40)], col, 2))]


def s_m_goodhart(T, idx):
    """'But when a measure becomes a target, it stops being a good measure. Goodhart's law.' A height chart measures a
    stick figure; a bullseye goes on the chart; the figure climbs a stack of books to hit it. The chart is useless now."""
    t0 = S("e2") - 0.1
    tm, tb, ts = Wx("e2", "measure") - 0.15, Wx("e2", "target") - 0.2, Wx("e2", "stops") - 0.1
    tg = Wx("e2", "Goodhart") - 0.35
    items = [(t0, t0 + 0.2, "fill", (("path", [(40, 128), (64, 128), (64, 318), (40, 318)]), YEL)),
             (t0 + 0.2, t0 + 0.35, "rect", (40, 128, 64, 318, BLK, False))]
    for i in range(1, 8):                                                       # the marks on the height chart
        y = 128 + i * 24
        items.append((t0 + 0.3 + i * 0.03, t0 + 0.33 + i * 0.03, "line", ([(64, y), (54 if i % 2 else 48, y)], BLK, 2)))
    for k, colb in enumerate(((200, 0, 0), (0, 0, 200), (0, 140, 0))):          # the books, dropped one by one
        y1 = 318 - 22 * k
        items.append((ts + 0.12 * k, ts + 0.12 * k, "rect", (98, y1 - 22, 146, y1, colb, True)))
        items.append((ts + 0.12 * k, ts + 0.12 * k, "rect", (98, y1 - 22, 146, y1, BLK, False)))
        items.append((ts + 0.12 * k, ts + 0.12 * k, "line", ([(104, y1 - 11), (140, y1 - 11)], WHITE, 1)))
    hop = ramp(T, ts + 0.75, ts + 1.05)                                         # up onto the books
    fx_, feet = int(176 - 54 * hop), int(318 - 66 * hop - 30 * math.sin(math.pi * hop))
    if T < ts + 0.75:
        items += [(t0 + 0.35 + 0.1 * k, t0 + 0.45 + 0.1 * k, kind, a) for k, (_, _, kind, a) in enumerate(_figure(fx_, feet))]
    else:
        items += [(0, 0, kind, a) for _, _, kind, a in _figure(fx_, feet)]
    if T < ts + 0.75:
        items.append((tm - 0.1, tm + 0.1, "line", ([(66, 228 - 11), (160, 228 - 11)], (128, 128, 128), 1)))   # it measures
    items.append((tm, tm + 0.35, "text", ("A MEASURE", 34, 86, 16, BLK, "silkscreen-700")))
    for r_, col in ((24, RED), (16, WHITE), (8, RED)):                           # the bullseye, slapped on the chart
        items.append((tb + (24 - r_) * 0.012, tb + (24 - r_) * 0.012, "fill", (("ell", 52, 162, r_, r_), col)))
    items.append((tb + 0.15, tb + 0.5, "text", ("A TARGET", 34, 112, 16, RED, "silkscreen-700")))
    if T >= ts + 1.05:                                                          # hit: the chart now says nothing
        items.append((ts + 1.05, ts + 1.05, "text", ("!", 140, 150, 16, RED, "silkscreen-700")))
    if T >= tg:                                                                 # the name of the law, over the labels
        items += [(tg, tg + 0.15, "erase", (30, 64, 236, 118)),
                  (tg + 0.15, tg + 0.4, "text", ("GOODHART'S LAW", 34, 100, 16, BLU, "silkscreen-700"))]
    return paint_shot(T, items, title="goodhart.bmp - Paint")


def _neq(x, y):
    """A big slashed equals sign, stamped in one go."""
    return [(0, 0.04, "line", ([(x - 24, y - 7), (x + 24, y - 7)], BLK, 5)), (0.04, 0.08, "line", ([(x - 24, y + 7), (x + 24, y + 7)], BLK, 5)),
            (0.08, 0.16, "line", ([(x + 16, y - 18), (x - 16, y + 18)], RED, 5))]


def _sc(v, s):
    return int(round(v * s))


def smiley(x, y, s=1.0):
    r, e = 26 * s, lambda v: _sc(v, s)
    return [(0, 0.12, "fill", (("ell", x, y, r, r), YEL)), (0.12, 0.18, "ellipse", (x, y, r, r, BLK, False)),
            (0.18, 0.22, "rect", (x - e(10), y - e(10), x - e(5), y - e(4), BLK, True)), (0.18, 0.22, "rect", (x + e(5), y - e(10), x + e(10), y - e(4), BLK, True)),
            (0.22, 0.32, "line", ([(x - e(12), y + e(6)), (x - e(4), y + e(13)), (x + e(4), y + e(13)), (x + e(12), y + e(6))], BLK, e(2)))]


def check(x, y, s=1.0):
    e = lambda v: _sc(v, s)
    return [(0, 0.22, "line", ([(x - e(22), y), (x - e(6), y + e(18)), (x + e(26), y - e(22))], GRN, e(6)))]


def phone(x, y, s=1.0):
    e = lambda v: _sc(v, s)
    return [(0, 0.08, "rect", (x - e(16), y - e(28), x + e(16), y + e(28), BLK, True)),
            (0.08, 0.12, "rect", (x - e(12), y - e(22), x + e(12), y + e(20), (0, 128, 255), True)),
            (0.16, 0.22, "fill", (("ell", x + e(16), y - e(26), e(12), e(12)), RED)), (0.22, 0.28, "text", ("99+", x + e(16) - 10, y - e(26) + 3, 8, WHITE, "silkscreen-700"))]


def heart(x, y, s=1.0, crack=False):
    pts = [(x + 16 * math.sin(a) ** 3 * 1.6 * s, y - (13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)) * 1.6 * s)
           for a in np.linspace(0, 2 * math.pi, 30)]
    out = [(0, 0.18, "fill", (("path", pts), (255, 0, 128)))]
    if crack:                                                                    # well-being, after a lot of engagement
        e = lambda v: _sc(v, s)
        out.append((0.25, 0.4, "line", ([(x - e(2), y - e(14)), (x + e(6), y - e(4)), (x - e(5), y + e(5)), (x + e(3), y + e(16))], WHITE, e(3))))
    return out


def paper_aplus(x, y, s=1.0):
    e = lambda v: _sc(v, s)
    return [(0, 0.08, "rect", (x - e(22), y - e(28), x + e(22), y + e(28), WHITE, True)), (0.08, 0.12, "rect", (x - e(22), y - e(28), x + e(22), y + e(28), BLK, False)),
            (0.12, 0.28, "text", ("A+", x - 16, y + 8, 16, RED, "silkscreen-700"))]


def bulb(x, y, s=1.0):
    e = lambda v: _sc(v, s)
    return [(0, 0.12, "fill", (("ell", x, y - e(6), e(20), e(22)), YEL)), (0.12, 0.16, "ellipse", (x, y - e(6), e(20), e(22), BLK, False)),
            (0.16, 0.2, "rect", (x - e(9), y + e(16), x + e(9), y + e(28), GRY, True)),
            (0.2, 0.3, "line", ([(x - e(27), y - e(16)), (x - e(36), y - e(22))], (255, 170, 0), 3)),
            (0.2, 0.3, "line", ([(x + e(27), y - e(16)), (x + e(36), y - e(22))], (255, 170, 0), 3)),
            (0.2, 0.3, "line", ([(x - e(28), y + e(2)), (x - e(38), y + e(4))], (255, 170, 0), 3)),
            (0.2, 0.3, "line", ([(x + e(28), y + e(2)), (x + e(38), y + e(4))], (255, 170, 0), 3))]


def scales(x, y, s=1.0):
    e = lambda v: _sc(v, s)
    return [(0, 0.08, "line", ([(x, y - e(26)), (x, y + e(24))], BLK, 3)), (0.08, 0.16, "line", ([(x - e(30), y - e(18)), (x + e(30), y - e(18))], BLK, 3)),
            (0.16, 0.2, "line", ([(x - e(30), y - e(18)), (x - e(40), y + e(4)), (x - e(20), y + e(4)), (x - e(30), y - e(18))], BLK, 2)),
            (0.2, 0.24, "line", ([(x + e(30), y - e(18)), (x + e(20), y + e(4)), (x + e(40), y + e(4)), (x + e(30), y - e(18))], BLK, 2)),
            (0.24, 0.28, "rect", (x - e(14), y + e(24), x + e(14), y + e(28), BLK, True))]


def yes_robot(x, y, s=1.0):
    e = lambda v: _sc(v, s)
    return [(0, 0.08, "rect", (x - e(16), y - e(26), x + e(16), y + e(2), GRY, True)), (0.08, 0.12, "rect", (x - e(10), y - e(18), x - e(5), y - e(13), BLU, True)),
            (0.08, 0.12, "rect", (x + e(5), y - e(18), x + e(10), y - e(13), BLU, True)), (0.12, 0.18, "rect", (x - e(18), y + e(4), x + e(18), y + e(30), GRY, True)),
            (0.18, 0.26, "line", ([(x + e(18), y + e(10)), (x + e(30), y - e(6)), (x + e(18), y - e(24))], BLK, 3)),
            (0.26, 0.36, "text", ("YES SIR!", x + e(30), y - e(24), 8, RED, "silkscreen-700"))]


# the four things that aren't what they measure: (the measure, the thing, their doodles, the words they land on)
ISNT = [("e3", "SATISFACTION", "TRUTH", smiley, check, "Satisfaction", "isn't", "truth", "isnt.bmp"),
        ("e3b", "ENGAGEMENT", "WELL-BEING", phone, lambda x, y, s: heart(x, y, s, crack=True), "Engagement", "isn't", "well-being",
         "isnt(2).bmp"),
        ("e3c", "TEST SCORES", "UNDERSTANDING", paper_aplus, bulb, "Test", "aren't", "understanding", "isnt_FINAL.bmp"),
        ("e3d", "OBEYING", "JUDGMENT", yes_robot, scales, "Obeying", "isn't", "judgment", "isnt_FINAL_v2.bmp")]
ISNT_X = (F.CANVAS[0] + F.CANVAS[2]) // 2


def isnt_neq(k):
    """When the slashed equals sign lands (and the buzzer goes)."""
    return Wx(ISNT[k][0], ISNT[k][6]) - 0.08


def _isnt(T, k):
    """One contrast, big: the measure on top, a slashed equals sign, the thing it was meant to stand for below."""
    key, ml, gl, dl, dr, wl, wn, wr, fname = ISNT[k]
    tl, tn = S(key) - 0.1, isnt_neq(k)
    tr = tn + 0.12                                                                # the answer goes up with the sign
    x = ISNT_X
    f = K.font("silkscreen-700", 16)
    items = [(tl + a, tl + b, kind, args) for a, b, kind, args in dl(x, 104, 1.4)]
    items.append((tl + 0.1, tl + 0.4, "text", (ml, int(x - f.measureText(ml) / 2), 170, 16, MAG, "silkscreen-700")))
    items += [(tn + a, tn + b, kind, args) for a, b, kind, args in _neq(x, 198)]
    items += [(tr + a, tr + b, kind, args) for a, b, kind, args in dr(x, 256, 1.4)]
    items.append((tr + 0.1, tr + 0.4, "text", (gl, int(x - f.measureText(gl) / 2), 322, 16, GRN, "silkscreen-700")))
    return paint_shot(T, items, title=fname + " - Paint")


def s_m_isnt1(T, idx):
    """'Satisfaction isn't truth.'"""
    return _isnt(T, 0)


def s_m_isnt2(T, idx):
    """'Engagement isn't well-being.'"""
    return _isnt(T, 1)


def s_m_isnt3(T, idx):
    """'Test scores aren't understanding.'"""
    return _isnt(T, 2)


def s_m_isnt4(T, idx):
    """'Obeying isn't judgment.'"""
    return _isnt(T, 3)


def s_m_gamed(T, idx):
    """'People gamed numbers long before AI. AI games them harder.' A stick figure fiddles a scoreboard; then a
    rocket robot chases a number off the canvas."""
    t0, t1 = S("e4") - 0.05, Wx("e4", "games") - 0.15
    items = [(t0, t0 + 0.2, "rect", (40, 70, 170, 120, BLK, True)), (t0 + 0.2, t0 + 0.6, "text", ("SCORE: 12", 48, 102, 10, (0, 255, 0), "silkscreen-700"))]
    items += [(t0 + 0.4, t0 + 0.8, "line", ([(190, 170), (190, 210), (178, 236)], BLK, 2)), (t0 + 0.8, t0 + 0.9, "line", ([(190, 210), (202, 236)], BLK, 2)),
              (t0 + 0.9, t0 + 1.0, "ellipse", (190, 160, 10, 10, BLK, False)), (t0 + 1.0, t0 + 1.2, "line", ([(190, 186), (150, 112)], BLK, 2)),
              (t0 + 1.3, t0 + 1.4, "rect", (100, 86, 166, 114, BLK, True)), (t0 + 1.4, t0 + 1.6, "text", ("99", 108, 106, 16, (0, 255, 0), "silkscreen-700")),
              (t0 + 1.2, t0 + 1.8, "text", ("PEOPLE, FOREVER", 34, 160, 10, BLU, "silkscreen-700"))]
    if T > t1:
        fly = ramp(T, t1, t1 + 1.4)
        rx = 40 + 150 * fly
        items += [(0, 0, k, a) for _, _, k, a in robot(0, int(rx), 250, 0.0)]
        items += [(0, 0, "line", ([(int(rx) - 30 - k * 14, 266 + k * 10), (int(rx) - 70 - k * 14, 266 + k * 10)], (255, 128, 0), 3)) for k in range(4)]
        items += [(t1 + 0.1, t1 + 0.3, "text", ("9999999", 150, 236, 16, RED, "silkscreen-700")), (t1 + 0.3, t1 + 0.6, "text", ("AI, NOW", 34, 330, 10, BLU, "silkscreen-700"))]
    dlg = None
    t_err = Wx("e4", "harder") - 0.05
    if T > t_err:
        dlg = lambda c: F.error_box(c, "AI.EXE", ["AI.EXE is chasing", "a number and will", "not stop."], x=36, y=196, w=196, h=92)
    return paint_shot(T, items, title="games.bmp - Paint", dialog=dlg)


# ------------------------------------------------------------------ PS1: the boat race

def _lagoon(g, T, fire=0.0, seed=0):
    # water: a checker of two blues, rolling
    for i in range(-16, 16):
        for j in range(-14, 18):
            def hgt(x, z):
                return 0.18 * math.sin(x * 0.8 + T * 2.2) + 0.15 * math.cos(z * 0.9 + T * 1.7)
            col = (40, 120, 210) if (i + j) % 2 else (30, 100, 190)
            g.quad((i, hgt(i, j), j), (i + 1, hgt(i + 1, j), j), (i + 1, hgt(i + 1, j + 1), j + 1), (i, hgt(i, j + 1), j + 1), col)
    # the cliffs round the lagoon
    for k in range(16):
        a0, a1 = 2 * math.pi * k / 16, 2 * math.pi * (k + 1) / 16
        r = 9.5
        p0 = (r * math.cos(a0), 0, 5 + r * math.sin(a0))
        p1 = (r * math.cos(a1), 0, 5 + r * math.sin(a1))
        top = ((r + 1.2) * math.cos((a0 + a1) / 2), 2.8 + (k % 3) * 0.7, 5 + (r + 1.2) * math.sin((a0 + a1) / 2))
        if 5 + r * math.sin((a0 + a1) / 2) < -1:
            continue
        g.tri(p0, p1, top, (150, 110, 70) if k % 2 else (90, 150, 70))
    # the course you are supposed to race: buoys to a finish gate, far away
    for k in range(6):
        V, Fc = F.prism(0.25, 0.7, 6)
        g.mesh(V, Fc, (255, 255, 255) if k % 2 else (230, 30, 30), F.translate(4.5 + k * 0.4, 0, 8 + k * 2.5))
    V, Fc = F.box(0.5, 3, 0.5)
    g.mesh(V, Fc, (230, 230, 230), F.translate(3.5, 1.5, 22))
    g.mesh(V, Fc, (230, 230, 230), F.translate(8.5, 1.5, 22))
    V, Fc = F.box(5.5, 0.8, 0.5)
    g.mesh(V, Fc, (230, 30, 30), F.translate(6, 3.2, 22))


def _boat(g, T, fire=0.0, R=2.6, c0=(-1.0, 0, 4.0)):
    """The boat on its circle in the lagoon, the sock at the wheel, burning when fire > 0. Returns its position."""
    a = T * 2.4
    x, z = c0[0] + R * math.cos(a), c0[2] + R * math.sin(a)
    heading = -a - math.pi                                       # tangent to the circle
    M = F.translate(x, 0.25, z) @ F.rot_y(heading)
    hull = [(-0.6, 0, -1.1), (0.6, 0, -1.1), (0.7, 0.5, -1.1), (-0.7, 0.5, -1.1), (0, 0.3, 1.6), (0, 0.6, 1.6)]
    faces = [(0, 1, 4), (1, 2, 5, 4), (2, 3, 5), (3, 0, 4, 5), (0, 3, 2, 1)]
    g.mesh(hull, [f for f in faces], (240, 240, 245), M)
    g.mesh(*F.box(0.8, 0.5, 0.7), (40, 110, 255), M @ F.translate(0, 0.75, -0.4))
    g.mesh(*F.prism(0.18, 0.55, 6), (250, 248, 236), M @ F.translate(0.0, 1.0, -0.2))                     # Doc at the wheel
    g.mesh(*F.box(0.3, 0.08, 0.3), (255, 140, 30), M @ F.translate(0.0, 1.6, -0.2))
    if fire > 0:
        rng = np.random.default_rng(int(T * 12))
        for k in range(int(10 * fire)):
            bx, bz = rng.uniform(-0.6, 0.6), rng.uniform(-1.0, 1.0)
            h = rng.uniform(0.8, 1.8)
            base = M @ F.translate(bx, 0.6, bz)
            p = base[:3, 3]
            col = [(255, 80, 0), (255, 180, 0), (255, 240, 60)][k % 3]
            g.tri(p + (-0.25, 0, 0), p + (0.25, 0, 0), p + (rng.uniform(-0.2, 0.2), h, 0), col, emissive=True)
            g.tri(p + (0, 0, -0.25), p + (0, 0, 0.25), p + (0, h * 0.8, rng.uniform(-0.2, 0.2)), col, emissive=True)
    return x, z


def _targets(g, T, bx, bz, c0=(-1.0, 0, 4.0), R=2.6):
    """Three turbo pickups on the boat's circle; each vanishes as the boat hits it and pops right back."""
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.5
        x, z = c0[0] + R * math.cos(a), c0[2] + R * math.sin(a)
        if math.hypot(bx - x, bz - z) < 1.0:
            continue
        s = 0.45
        M = F.translate(x, 0.9 + 0.15 * math.sin(T * 5 + k), z) @ F.rot_y(T * 4 + k)
        V = [(0, s, 0), (s, 0, 0), (0, 0, s), (-s, 0, 0), (0, 0, -s), (0, -s, 0)]
        Fc = [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1), (5, 2, 1), (5, 3, 2), (5, 4, 3), (5, 1, 4)]
        g.mesh(V, Fc, (120, 255, 60), M, emissive=True)


def _hud(arr, T, score, wrong=True, best=None, hi=False):
    c = skia.Surface(arr).getCanvas()
    def pt(s, x, y, size, col, align="left"):
        f = K.font("pressstart-400", size)
        f.setEdging(skia.Font.Edging.kAlias)
        w = f.measureText(s)
        x0 = x - w / 2 if align == "center" else (x - w if align == "right" else x)
        c.drawString(s, x0 + 5, y + 5, f, paint((0, 0, 0)))
        c.drawString(s, x0, y, f, paint(col))
        K.reg(x0, y - size, x0 + w, y + 4, "ps1")
    pt("SCORE", 70, 300, 40, (255, 255, 255))
    pt(f"{int(score):07d}", 70, 360, 52, (255, 230, 0))
    pt("LAP 0/3", 70, 430, 36, (255, 255, 255))
    pt("2016", 900, 320, 40, (120, 255, 200), align="right")
    if wrong and int(T * 3) % 2 == 0:
        pt("WRONG WAY!", 540, 560, 52, (255, 40, 40), align="center")
    if best is not None:
        pt("HUMAN BEST", 70, 1180, 34, (255, 255, 255))
        pt(f"{best:07d}", 70, 1230, 40, (200, 200, 200))
    if hi and int(T * 6) % 2 == 0:
        pt("NEW HIGH SCORE!", 540, 1120, 46, (255, 80, 220), align="center")


def _score(T):
    t0 = S("e5") - 0.1
    return min(9999999, (T - t0) * 21000 + ((T - t0) ** 2) * 8000) if T > t0 else 0


def s_ps1_boat(T, idx):
    """'A boat racing AI chasing points skipped the race to spin in circles.' Low-poly lagoon, the boat circling the
    same three pickups, the course and finish gate ignored."""
    g = F.PS1(cam=(-1.0, 6.5, -6.0), look=(-0.8, 0.0, 4.2), fov=62, sky=((60, 90, 230), (190, 210, 250)), fog=(170, 200, 240), fog_near=10,
              fog_far=34)
    _lagoon(g, T)
    bx, bz = _boat(g, T)
    _targets(g, T, bx, bz)
    a = g.render()
    out = np.zeros((H, W, 4), np.uint8)
    out[..., :3] = F.upscale(a, 4)[:H, :W]
    out[..., 3] = 255
    _hud(out, T, _score(T))
    return out


def s_ps1_fire(T, idx):
    """'On fire. Outscoring humans.' Still circling, now burning; NEW HIGH SCORE against the human best."""
    g = F.PS1(cam=(-1.0, 6.0, -5.5), look=(-0.8, 0.2, 4.0), fov=62, sky=((80, 40, 120), (250, 140, 90)), fog=(240, 160, 110), fog_near=8,
              fog_far=30)
    _lagoon(g, T)
    bx, bz = _boat(g, T, fire=ramp(T, Wx("e5", "fire") - 0.3, Wx("e5", "fire")))
    _targets(g, T, bx, bz)
    a = g.render()
    out = np.zeros((H, W, 4), np.uint8)
    out[..., :3] = F.upscale(a, 4)[:H, :W]
    out[..., 3] = 255
    t_hi = Wx("e5", "Outscoring") - 0.1
    hi = T > t_hi
    _hud(out, T, _score(min(T, t_hi)), wrong=not hi, best=int(_score(t_hi) / 1.2 / 10) * 10 if hi else None, hi=hi)
    return out

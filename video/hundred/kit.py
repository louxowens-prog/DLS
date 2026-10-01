"""The drawing kit (style only): gel light, art-nouveau and art-deco ornament, stained glass, the storm, the props.

Everything is lit by coloured gels: a set is painted dark and deep, then light pools, beams and rims are added in
saturated primaries (additive), and darkness laid back over what the light doesn't reach.
"""
import math

import numpy as np
import skia

import draw as D
from draw import H, W, col, ease, lerp, mix, paint, path, ramp

# the gels: saturated primaries
RED, BLUE, GREEN, MAGENTA = (255, 24, 36), (36, 70, 255), (20, 230, 110), (255, 30, 190)
AMBER, CYAN, GOLD, VIOLET, WHITE = (255, 150, 40), (60, 220, 255), (255, 200, 70), (150, 50, 255), (255, 255, 255)
BLACK, INK = (0, 0, 0), (6, 4, 8)
BRASS, BRASS_D, BRASS_L = (200, 150, 60), (110, 72, 22), (255, 226, 140)
GELS = {"red": RED, "blue": BLUE, "green": GREEN, "magenta": MAGENTA, "amber": AMBER, "cyan": CYAN, "gold": GOLD,
        "violet": VIOLET}


# ------------------------------------------------------------------ light

def glow(c, x, y, r, color, a=1.0, core=0.0):
    """An additive pool of coloured light (core > 0: a hot centre)."""
    p = paint(shader=D.rad((x, y), r, [color + (1.0,), color + (0.35,), color + (0.0,)], [0.0, 0.45, 1.0]), a=a)
    p.setBlendMode(skia.BlendMode.kPlus)
    c.drawCircle(x, y, r, p)
    if core > 0:
        q = paint(shader=D.rad((x, y), r * 0.25, [(255, 255, 255, 1.0), color + (0.5,), color + (0.0,)], [0, 0.4, 1]), a=a * core)
        q.setBlendMode(skia.BlendMode.kPlus)
        c.drawCircle(x, y, r * 0.25, q)


def eglow(c, x, y, rx, ry, color, a=1.0):
    c.save()
    c.translate(x, y)
    c.scale(1, ry / rx)
    glow(c, 0, 0, rx, color, a)
    c.restore()


def beam(c, pts, color, a=0.5, p0=None, p1=None):
    """A shaft of light (a polygon), brightest at p0 fading to p1."""
    pts = list(pts)
    if p0 is None:
        p0, p1 = pts[0], pts[len(pts) // 2]
    p = paint(shader=D.lin(p0, p1, [color + (1.0,), color + (0.0,)]), a=a)
    p.setBlendMode(skia.BlendMode.kPlus)
    c.drawPath(path(pts), p)


def dark(c, x, y, r0, r1, a=1.0):
    """Darkness laid over everything outside a circle: light only reaches so far."""
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.rad((x, y), r1, [(0, 0, 0, 0.0), (0, 0, 0, 0.0), (0, 0, 0, 1.0)],
                                                         [0.0, r0 / r1, 1.0]), a=a))


def vgrad(c, x0, y0, x1, y1, top, bot):
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(shader=D.lin((0, y0), (0, y1), [top, bot])))


def wash(c, color, a=0.3, mode=skia.BlendMode.kScreen, rect=None):
    p = paint(color, a)
    p.setBlendMode(mode)
    c.drawRect(rect or skia.Rect.MakeWH(W, H), p)


def multiply(c, color, a=1.0, rect=None):
    wash(c, color, a, skia.BlendMode.kMultiply, rect)


def lit_fill(c, p, color, lx, ly, r, amb=0.08, a=1.0):
    """Fill a path lit by a point light at (lx, ly): full colour near it, falling to near-black."""
    c.drawPath(p, paint(shader=D.rad((lx, ly), r, [color, mix(color, INK, 0.55), mix(color, INK, 1 - amb)], [0.0, 0.45, 1.0]), a=a))


def flash_at(T, times, dur=0.5):
    """Lightning: a double flicker at each time, 0..1."""
    v = 0.0
    for t0 in times:
        u = T - t0
        if 0 <= u < dur:
            v = max(v, math.exp(-u / 0.06) * (1.0 if u < 0.07 else 0.0) + 0.75 * math.exp(-(u - 0.12) / 0.09) * (u >= 0.12))
    return min(1.0, v)


# ------------------------------------------------------------------ perspective

def quad_matrix(w, h, dst):
    m = skia.Matrix()
    m.setPolyToPoly([skia.Point(0, 0), skia.Point(w, 0), skia.Point(w, h), skia.Point(0, h)], [skia.Point(*p) for p in dst])
    return m


def draw_quad(c, img, dst, a=1.0):
    """Draw an image warped onto a quadrilateral (tl, tr, br, bl): walls, floors and ceilings in perspective."""
    c.save()
    c.clipPath(path(dst), doAntiAlias=True)
    c.concat(quad_matrix(img.width(), img.height(), dst))
    p = skia.Paint(AntiAlias=True)
    p.setAlphaf(a)
    c.drawImage(img, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear), p)
    c.restore()


def surf(w, h, fn, bg=(0, 0, 0, 0)):
    """Paint a w x h image with fn(c) (cached by the caller)."""
    a = np.zeros((h, w, 4), np.uint8)
    a[..., :] = bg
    s = skia.Surface(a)
    fn(s.getCanvas())
    return D.image(a)


# ------------------------------------------------------------------ ornament

def fan_tile(w, h, ground, line, a_line=1.0, n=7):
    """Art-deco scalloped fans in staggered rows (a wallpaper repeat), as an image."""
    def fn(c):
        c.drawRect(skia.Rect.MakeWH(w, h), paint(ground))
        r = w / 2
        for row in range(-1, int(h / (r * 0.5)) + 2):
            y = row * r * 0.5
            off = (row % 2) * r
            for k in range(-1, 3):
                cx = k * w / 1 * 1.0 + off - r * (k > 0) * 0
                cx = k * 2 * r + off
                fan = skia.Path()
                fan.addArc(skia.Rect.MakeLTRB(cx - r, y - r, cx + r, y + r), 180, 180)
                c.drawPath(fan, paint(ground))
                c.drawArc(skia.Rect.MakeLTRB(cx - r, y - r, cx + r, y + r), 180, 180, False, paint(line, a_line, stroke=w * 0.02))
                c.drawArc(skia.Rect.MakeLTRB(cx - r * 0.7, y - r * 0.7, cx + r * 0.7, y + r * 0.7), 180, 180, False,
                          paint(line, a_line * 0.8, stroke=w * 0.012))
                for i in range(1, n):
                    ang = math.pi + math.pi * i / n
                    c.drawLine(cx + r * 0.18 * math.cos(ang), y + r * 0.18 * math.sin(ang), cx + r * 0.68 * math.cos(ang),
                               y + r * 0.68 * math.sin(ang), paint(line, a_line * 0.7, stroke=w * 0.008))
                c.drawCircle(cx, y, r * 0.1, paint(line, a_line))
    return surf(w, h, fn)


def diamond_tile(w, h, ground, line, accent):
    """Deco lozenges with a stepped frame: the corridor wallpaper."""
    def fn(c):
        c.drawRect(skia.Rect.MakeWH(w, h), paint(ground))
        for (cx, cy) in ((w / 2, h / 2), (0, 0), (w, 0), (0, h), (w, h)):
            for k, s in enumerate((0.48, 0.34, 0.2)):
                pts = [(cx, cy - h * s), (cx + w * s, cy), (cx, cy + h * s), (cx - w * s, cy)]
                c.drawPath(path(pts), paint(line if k != 1 else accent, 0.9, stroke=w * (0.018 if k == 0 else 0.012)))
            c.drawCircle(cx, cy, w * 0.04, paint(accent))
        c.drawLine(0, h / 2, w, h / 2, paint(line, 0.25, stroke=w * 0.006))
    return surf(w, h, fn)


def whiplash_tile(w, h, ground, line, accent):
    """Art-nouveau whiplash stems and lilies (the red room's paper)."""
    def fn(c):
        c.drawRect(skia.Rect.MakeWH(w, h), paint(ground))
        for sx in (0, w):
            pts = [(sx, h), (sx + 0.35 * w * (1 if sx == 0 else -1), h * 0.7), (sx - 0.05 * w * (1 if sx == 0 else -1), h * 0.42),
                   (sx + 0.3 * w * (1 if sx == 0 else -1), h * 0.12), (sx + 0.5 * w * (1 if sx == 0 else -1), 0)]
            c.drawPath(D.smooth(pts, closed=False), paint(line, 0.9, stroke=w * 0.02))
        cx = w / 2
        stem = [(cx, h), (cx - 0.12 * w, h * 0.7), (cx + 0.1 * w, h * 0.45), (cx - 0.04 * w, h * 0.22)]
        c.drawPath(D.smooth(stem, closed=False), paint(line, 0.9, stroke=w * 0.018))
        for k in range(3):                                              # a lily: three petals
            a = -math.pi / 2 + (k - 1) * 0.6
            tip = (cx - 0.04 * w + math.cos(a) * w * 0.16, h * 0.22 + math.sin(a) * w * 0.2)
            c.drawPath(D.smooth([(cx - 0.04 * w, h * 0.22), (lerp(cx - 0.04 * w, tip[0], 0.5) - w * 0.05, (h * 0.22 + tip[1]) / 2), tip,
                                 (lerp(cx - 0.04 * w, tip[0], 0.5) + w * 0.05, (h * 0.22 + tip[1]) / 2)]), paint(accent, 0.85))
        for k in range(2):
            y = h * (0.55 + 0.2 * k)
            c.drawPath(D.smooth([(cx, y), (cx + 0.14 * w * (1 - 2 * k), y - h * 0.06), (cx + 0.22 * w * (1 - 2 * k), y + h * 0.02),
                                 (cx + 0.1 * w * (1 - 2 * k), y + h * 0.03)]), paint(line, 0.7))
    return surf(w, h, fn)


def checker(w, h, a_col, b_col, n=8):
    def fn(c):
        s = w / n
        for i in range(n):
            for j in range(int(h / s) + 1):
                c.drawRect(skia.Rect.MakeXYWH(i * s, j * s, s, s), paint(a_col if (i + j) % 2 == 0 else b_col))
    return surf(w, h, fn)


def tiled(tile, w, h):
    """A large image filled with a repeat of `tile`."""
    def fn(c):
        p = skia.Paint()
        p.setShader(tile.makeShader(skia.TileMode.kRepeat, skia.TileMode.kRepeat, skia.SamplingOptions(skia.FilterMode.kLinear)))
        c.drawRect(skia.Rect.MakeWH(w, h), p)
    return surf(w, h, fn)


def stained_glass(c, x0, y0, x1, y1, palette, seed=0, lit=1.0, arch=True, lead=(10, 8, 10), pattern="deco"):
    """A geometric stained-glass window, glowing (lit 0..1: how much light comes through)."""
    rng = np.random.default_rng(seed)
    w, h = x1 - x0, y1 - y0
    outline = skia.Path()
    if arch:
        outline.moveTo(x0, y1)
        outline.lineTo(x0, y0 + w / 2)
        outline.arcTo(skia.Rect.MakeLTRB(x0, y0, x1, y0 + w), 180, 180, False)
        outline.lineTo(x1, y1)
        outline.close()
    else:
        outline.addRect(skia.Rect.MakeLTRB(x0, y0, x1, y1))
    c.save()
    c.clipPath(outline, doAntiAlias=True)
    c.drawPath(outline, paint((4, 4, 8)))
    cx = (x0 + x1) / 2
    if pattern == "deco":                                               # a sunburst over stepped panes
        cy = y0 + w * 0.5
        n = 14
        for i in range(n):
            a0, a1 = math.pi + math.pi * i / n, math.pi + math.pi * (i + 1) / n
            colr = palette[i % len(palette)]
            pts = [(cx, cy), (cx + 2 * w * math.cos(a0), cy + 2 * w * math.sin(a0)), (cx + 2 * w * math.cos(a1), cy + 2 * w * math.sin(a1))]
            c.drawPath(path(pts), paint(mix(colr, (0, 0, 0), 0.35 * (1 - lit))))
        rows = 6
        for r in range(rows):
            for k in range(4):
                colr = palette[int(rng.integers(len(palette)))]
                yy = cy + r * (y1 - cy) / rows
                c.drawRect(skia.Rect.MakeLTRB(x0 + k * w / 4, yy, x0 + (k + 1) * w / 4, yy + (y1 - cy) / rows),
                           paint(mix(colr, (0, 0, 0), 0.25 + 0.3 * (1 - lit) + 0.15 * rng.random())))
        c.drawCircle(cx, cy, w * 0.16, paint(mix(palette[0], (255, 255, 255), 0.25 * lit)))
        for i in range(n + 1):
            a = math.pi + math.pi * i / n
            c.drawLine(cx, cy, cx + 2 * w * math.cos(a), cy + 2 * w * math.sin(a), paint(lead, stroke=w * 0.012))
        for r in range(rows + 1):
            yy = cy + r * (y1 - cy) / rows
            c.drawLine(x0, yy, x1, yy, paint(lead, stroke=w * 0.012))
        for k in range(1, 4):
            c.drawLine(x0 + k * w / 4, cy, x0 + k * w / 4, y1, paint(lead, stroke=w * 0.012))
        c.drawCircle(cx, cy, w * 0.16, paint(lead, stroke=w * 0.014))
        c.drawCircle(cx, cy, w * 0.3, paint(lead, stroke=w * 0.012))
    else:                                                               # nouveau: flowing panes round a lily
        for i in range(60):
            px, py = x0 + rng.random() * w, y0 + rng.random() * h
            r = w * (0.08 + 0.12 * rng.random())
            colr = palette[int(rng.integers(len(palette)))]
            c.drawPath(D.smooth(D.ellipse(px, py, r, r * (0.6 + rng.random()), 7)), paint(mix(colr, (0, 0, 0), 0.3 * (1 - lit))))
            c.drawPath(D.smooth(D.ellipse(px, py, r, r * (0.6 + rng.random()), 7)), paint(lead, stroke=w * 0.012))
    c.restore()
    c.drawPath(outline, paint(lead, stroke=w * 0.03))
    if lit > 0:
        q = skia.Paint(AntiAlias=True)
        q.setImageFilter(skia.ImageFilters.Blur(w * 0.12, w * 0.12))
        q.setBlendMode(skia.BlendMode.kPlus)
        q.setAlphaf(0.35 * lit)
        c.saveLayer(None, q)
        c.clipPath(outline, doAntiAlias=True)
        for i, colr in enumerate(palette):
            c.drawCircle(cx + (i - len(palette) / 2) * w * 0.15, (y0 + y1) / 2, w * 0.5, paint(colr, 0.6))
        c.restore()
    return outline


# ------------------------------------------------------------------ the storm

def rain(c, T, x0=0, y0=0, x1=W, y1=H, n=260, color=(190, 200, 255), a=0.35, slant=0.18, speed=2600, seed=1, length=90):
    rng = np.random.default_rng(seed)
    xs, ph, ln = rng.random(n), rng.random(n), rng.uniform(0.5, 1.0, n)
    hh = y1 - y0
    p = paint(color, a, stroke=1.6)
    for i in range(n):
        y = y0 + ((ph[i] * hh + T * speed * (0.8 + 0.4 * ln[i])) % (hh + length)) - length
        x = x0 + xs[i] * (x1 - x0) + (y - y0) * slant
        c.drawLine(x, y, x + length * ln[i] * slant, y + length * ln[i], p)


def bolt(c, x, y0, y1, seed=0, a=1.0, w=6, color=(220, 230, 255)):
    rng = np.random.default_rng(seed)
    pts, yy, xx = [(x, y0)], y0, x
    while yy < y1:
        yy += rng.uniform(40, 110)
        xx += rng.uniform(-60, 60)
        pts.append((xx, min(yy, y1)))
    pth = path(pts, closed=False)
    c.drawPath(pth, paint(color, 0.5 * a, stroke=w * 5, blur=w * 3))
    c.drawPath(pth, paint((255, 255, 255), a, stroke=w))
    for k in range(2, len(pts) - 2, 3):                                 # branches
        bx, by = pts[k]
        br = [(bx, by)]
        for _ in range(3):
            bx += rng.uniform(-70, 70)
            by += rng.uniform(30, 80)
            br.append((bx, by))
        c.drawPath(path(br, closed=False), paint((255, 255, 255), 0.6 * a, stroke=w * 0.5))


def streaks_on_glass(c, T, x0, y0, x1, y1, seed=2, a=0.5):
    """Rain running down a window pane: wobbling bright trickles."""
    rng = np.random.default_rng(seed)
    for i in range(26):
        x = x0 + rng.random() * (x1 - x0)
        sp = rng.uniform(40, 140)
        top = y0 + ((rng.random() * (y1 - y0) + T * sp) % (y1 - y0))
        L = rng.uniform(60, 220)
        pts = [(x + 4 * math.sin((top + k * 12) * 0.05 + i), top + k * 12 - L) for k in range(int(L / 12) + 1)]
        c.drawPath(path(pts, closed=False), paint((200, 210, 255), a * 0.6, stroke=2.2))
        c.drawCircle(pts[-1][0], pts[-1][1], 4, paint((230, 235, 255), a))


# ------------------------------------------------------------------ props

def key(c, x, y, s=1.0, ang=0.0, glint=1.0, tag=True, T=0.0):
    """The brass key on its tag stamped 100: the recurring object."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    if tag:                                                             # the tag hangs from the bow on a short chain
        c.drawLine(-70, 0, -120, 20, paint((120, 90, 40), stroke=4))
        tagp = D.rrect(-250, -10, -110, 70, 14)
        c.drawPath(tagp, paint(shader=D.lin((-250, -10), (-110, 70), [BRASS_L, BRASS, BRASS_D])))
        c.drawPath(tagp, paint(BRASS_D, stroke=4))
        c.drawCircle(-125, 30, 7, paint((20, 14, 8)))
        f = D.font("limelight-400", 50)
        c.drawString("100", -238, 50, f, paint((48, 26, 8)))
        D.reg_local(c, -238, 12, -238 + f.measureText("100"), 52, "keytag")
    bow = skia.Path()
    bow.addCircle(-40, 0, 38)
    bow.addCircle(-40, 0, 18)
    bow.setFillType(skia.PathFillType.kEvenOdd)
    g = D.lin((-80, -40), (0, 40), [BRASS_L, BRASS, BRASS_D])
    c.drawPath(bow, paint(shader=g))
    for k in range(6):                                                  # nouveau petals round the bow
        a = k * math.pi / 3
        c.drawCircle(-40 + 40 * math.cos(a), 40 * math.sin(a), 9, paint(shader=g))
    c.drawPath(D.rrect(-4, -9, 170, 9, 4), paint(shader=D.lin((0, -9), (0, 9), [BRASS_L, BRASS, BRASS_D])))
    c.drawPath(path([(120, 8), (120, 46), (136, 46), (136, 30), (150, 30), (150, 46), (170, 46), (170, 8)]),
               paint(shader=D.lin((120, 8), (170, 46), [BRASS, BRASS_D])))
    if glint > 0:
        glow(c, -60, -20, 60, (255, 230, 160), 0.6 * glint * (0.7 + 0.3 * math.sin(T * 5)))
    c.restore()


def phone(c, x, y, s=1.0, ang=0.0, screen=None, glow_col=(190, 225, 255), lit=1.0, face_down=False):
    """A phone (local size 400 x 820); screen(c) paints the screen in local coordinates (-180..180, -380..380)."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    body = D.rrect(-200, -410, 200, 410, 56)
    if lit > 0 and not face_down:
        glow(c, 0, 0, 900, glow_col, 0.22 * lit)
    c.drawPath(body, paint((14, 14, 18)))
    c.drawPath(body, paint((60, 60, 70), stroke=6))
    if face_down:
        c.restore()
        return
    scr = D.rrect(-182, -392, 182, 392, 44)
    c.save()
    c.clipPath(scr, doAntiAlias=True)
    c.drawPath(scr, paint(shader=D.lin((0, -392), (0, 392), [mix(glow_col, (0, 0, 0), 0.72), mix(glow_col, (0, 0, 0), 0.82),
                                                          mix(glow_col, (0, 0, 0), 0.9)]), a=lit))
    if screen is not None:
        screen(c)
    c.restore()
    c.drawPath(D.rrect(-50, -380, 50, -356, 12), paint((10, 10, 14)))
    c.restore()


def bubble(c, text_lines, x, y, w, size=34, me=False, a=1.0, fname="jost-500", tag="chat"):
    """A chat bubble (local coords): the AI's on the left (white), hers on the right (blue)."""
    f = D.font(fname, size)
    lh = size * 1.28
    h = lh * len(text_lines) + size * 0.9
    bx0 = x if not me else x - w
    r = D.rrect(bx0, y, bx0 + w, y + h, size * 0.7)
    c.drawPath(r, paint((30, 100, 240) if me else (58, 58, 68), a))
    yy = y + size * 0.45 + size
    for ln in text_lines:
        c.drawString(ln, bx0 + size * 0.6, yy, f, paint((255, 255, 255) if me else (240, 240, 246), a))
        D.reg_local(c, bx0 + size * 0.6, yy - size * 0.8, bx0 + size * 0.6 + f.measureText(ln), yy + size * 0.2, tag)
        yy += lh
    return h


def check(c, x, y, s, color=(40, 220, 120), a=1.0, w=10):
    c.drawPath(path([(x - s, y), (x - s * 0.3, y + s * 0.7), (x + s, y - s * 0.8)], closed=False), paint(color, a, stroke=w))


# ------------------------------------------------------------------ fact plates

def deco_frame(c, x0, y0, x1, y1, color=GOLD, a=1.0, w=4):
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(color, a, stroke=w))
    c.drawRect(skia.Rect.MakeLTRB(x0 + 12, y0 + 12, x1 - 12, y1 - 12), paint(color, a * 0.7, stroke=w * 0.5))
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        for k in range(3):                                              # stepped deco corners
            r = 34 - k * 10
            c.drawArc(skia.Rect.MakeLTRB(cx - r, cy - r, cx + r, cy + r), {(1, 1): 0, (-1, 1): 90, (-1, -1): 180, (1, -1): 270}[(sx, sy)],
                      90, False, paint(color, a, stroke=w * 0.6))


def plate(c, head, sub=None, src=None, y=300, color=GOLD, a=1.0, x=540, maxw=860, size=78, glow_col=None, head_font="limelight-400",
          tag="plate", bg=0.78):
    """A fact plate: a deco-framed black panel with a glowing headline, a line of detail, and the source."""
    if a <= 0:
        return y
    fh = D.font(head_font, size)
    heads = D.wrap_balanced(head, fh, maxw - 80) if isinstance(head, str) else head
    fs = D.font("jost-500", size * 0.5)
    subs = (D.wrap_balanced(sub, fs, maxw - 80) if isinstance(sub, str) else sub) if sub else []
    fsrc = D.font("cormorant-500i", size * 0.44)
    h = len(heads) * size * 1.08 + len(subs) * size * 0.64 + (size * 0.56 if src else 0) + 70
    x0, x1 = x - maxw / 2, x + maxw / 2
    if glow_col is not None:
        eglow(c, x, y + h / 2, maxw * 0.7, h * 0.9, glow_col, 0.35 * a)
    c.drawRect(skia.Rect.MakeLTRB(x0, y, x1, y + h), paint((4, 2, 6), bg * a))
    deco_frame(c, x0, y, x1, y + h, color, a)
    yy = y + 36 + size * 0.86
    for ln in heads:
        D.text(c, ln, x, yy, size, head_font, mix(color, (255, 255, 255), 0.35), tag=tag, a=a, shadow=(0, 0, 0))
        yy += size * 1.08
    yy += size * 0.02
    for ln in subs:
        D.text(c, ln, x, yy - size * 0.16, size * 0.5, "jost-500", (240, 236, 228), tag=tag, a=a)
        yy += size * 0.64
    if src:
        D.text(c, src, x, yy - size * 0.06, size * 0.44, "cormorant-500i", mix(color, (255, 255, 255), 0.2), tag=tag, a=a * 0.95)
    return y + h


def door_plate(c, x, y, num, s=1.0, color=BRASS, a=1.0, tag="door"):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawPath(D.rrect(-70, -40, 70, 40, 18), paint(shader=D.lin((-70, -40), (70, 40), [BRASS_L, color, BRASS_D]), a=a))
    c.drawPath(D.rrect(-70, -40, 70, 40, 18), paint(BRASS_D, a, stroke=4))
    f = D.font("limelight-400", 52 if len(num) < 3 else 44)
    w = f.measureText(num)
    c.drawString(num, -w / 2, 18, f, paint((40, 22, 6), a))
    D.reg_local(c, -w / 2, -22, w / 2, 20, tag)
    c.restore()

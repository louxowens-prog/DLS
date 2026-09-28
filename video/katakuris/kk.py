"""The Katakuris look, as a toolkit (style only).

An early-2000s low-budget horror-comedy musical: flat, over-lit painted "live action" with figures pasted in by a
bad chroma key (green spill haloes, a jagged matte line), plastic early-CGI overlays (spinning 3D stars, lens flares,
chrome WordArt), claymation for the impossible moments (lumpy clay with fingerprints and tool marks, animated on twos
so it jerks at 12 fps and 'boils'), karaoke lyrics with a colour wipe, TV telop captions and variety-show chapter
cards. The picture is crisp video - oversaturated, blooming, with smeary video chroma - never film grain.

Everything is drawn with skia into numpy arrays. Coordinates are 1080 x 1920 pixels.
"""
import math
import os

import numpy as np
import skia
from PIL import Image, ImageFilter

W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "assets", "fonts")

# palette: candy-bright daylight, then blood and bruise
SKY, SKY2, CLOUD = (30, 150, 255), (150, 225, 255), (255, 255, 255)
GRASS, GRASS2, GRASS3 = (70, 215, 60), (30, 160, 50), (170, 245, 90)
PINK, HOT, LEMON, ORANGE, MINT, LILAC = (255, 140, 200), (255, 40, 150), (255, 236, 50), (255, 140, 20), (120, 240, 200), (190, 140, 255)
BLOOD, GORE, BRUISE, INK, WHITE, CREAM = (210, 0, 30), (130, 0, 20), (70, 20, 90), (18, 12, 28), (255, 255, 255), (255, 248, 230)
KEY = (40, 255, 80)                 # the green-screen spill around every keyed figure
SKIN = (255, 214, 180)

TEXT = []                          # lettering drawn this frame, for the collision lint: (x0, y0, x1, y1, tag)


# ------------------------------------------------------------------ basics

_tf = {}


def font(name, size):
    if name not in _tf:
        _tf[name] = skia.Typeface.MakeFromFile(os.path.join(FONTS, name + ".ttf"))
    f = skia.Font(_tf[name], size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    return f


def col(c, a=1.0):
    return skia.Color4f(c[0] / 255, c[1] / 255, c[2] / 255, a)


def paint(c=INK, a=1.0, stroke=None, blur=0.0, shader=None, cap="round", aa=True):
    p = skia.Paint(AntiAlias=aa)
    if shader is not None:
        p.setShader(shader)
        p.setAlphaf(a)
    else:
        p.setColor4f(col(c, a))
    if stroke is not None:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap({"round": skia.Paint.kRound_Cap, "butt": skia.Paint.kButt_Cap}[cap])
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur > 0:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def lin(p0, p1, colors, pos=None):
    cs = [col(c[:3], c[3] if len(c) > 3 else 1.0) for c in colors]
    return skia.GradientShader.MakeLinear([skia.Point(*p0), skia.Point(*p1)], [c.toColor() for c in cs], pos)


def rad(c0, r, colors, pos=None):
    cs = [col(c[:3], c[3] if len(c) > 3 else 1.0) for c in colors]
    return skia.GradientShader.MakeRadial(skia.Point(*c0), max(1e-3, r), [c.toColor() for c in cs], pos)


def path(pts, closed=True):
    p = skia.Path()
    pts = list(pts)
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if closed:
        p.close()
    return p


def smooth(pts, closed=True):
    """A smooth closed curve through the points (Catmull-Rom as cubics)."""
    pts = [tuple(map(float, q)) for q in pts]
    n = len(pts)
    p = skia.Path()
    p.moveTo(*pts[0])
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0, p1, p2, p3 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        if not closed:
            p0, p3 = pts[max(i - 1, 0)], pts[min(i + 2, n - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        p.cubicTo(*c1, *c2, *p2)
    if closed:
        p.close()
    return p


def bez(a, b, c, n=16):
    t = np.linspace(0, 1, n)[:, None]
    a, b, c = np.array(a, float), np.array(b, float), np.array(c, float)
    return (1 - t) ** 2 * a + 2 * (1 - t) * t * b + t ** 2 * c


def ellipse(cx, cy, rx, ry, n=40):
    a = np.linspace(0, 2 * math.pi, n, endpoint=False)
    return np.stack([cx + rx * np.cos(a), cy + ry * np.sin(a)], 1)


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def ramp(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a))) if b > a else float(t >= a)


def lerp(a, b, k):
    return a + (b - a) * k


def mix(c1, c2, k):
    return tuple(int(round(a + (b - a) * k)) for a, b in zip(c1, c2))


# ------------------------------------------------------------------ time: live action is smooth; clay moves on twos

def twos(t):
    """Claymation time: a new position 12 times a second (each drawing held for two frames)."""
    return math.floor(t * 12 + 1e-6) / 12


def boil(t, amp=1.0, seed=0):
    """The animator never puts the clay back exactly: a nudge that changes every drawing."""
    k = int(math.floor(t * 12 + 1e-6))
    r = np.random.default_rng((seed * 7919 + k * 104729) % (2 ** 32))
    return r.uniform(-amp, amp), r.uniform(-amp, amp), r.uniform(-amp, amp)


def pop(t, a, dur=0.22, amp=0.3):
    """0 before a, then a bouncy overshooting scale-in (smooth: this is video, not clay)."""
    if t < a:
        return 0.0
    k = ramp(t, a, a + dur)
    return 1 + amp * math.sin(k * math.pi) * (1 - k) * 2 if k < 1 else 1.0


# ------------------------------------------------------------------ lettering registry (lint)

def reg(x0, y0, x1, y1, tag):
    TEXT.append((float(min(x0, x1)), float(min(y0, y1)), float(max(x0, x1)), float(max(y0, y1)), tag))


def reg_local(c, x0, y0, x1, y1, tag):
    m = c.getTotalMatrix()
    pts = [m.mapXY(x, y) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    reg(min(p.x() for p in pts), min(p.y() for p in pts), max(p.x() for p in pts), max(p.y() for p in pts), tag)


def wrap(s, f, maxw):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if f.measureText(t) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text(c, s, x, y, size, fname="rounded-900", color=WHITE, align="center", tag="label", a=1.0, outline=None, ow=10,
         outline2=None, ow2=0, shadow=None):
    """One line of lettering at baseline y (outlined like a TV telop), registered for the lint."""
    f = font(fname, size)
    w = f.measureText(s)
    x0 = x - w / 2 if align == "center" else (x - w if align == "right" else x)
    if shadow is not None:
        c.drawString(s, x0 + size * 0.06, y + size * 0.08, f, paint(shadow, a * 0.8, stroke=ow2 or ow))
        c.drawString(s, x0 + size * 0.06, y + size * 0.08, f, paint(shadow, a * 0.8))
    if outline2 is not None:
        c.drawString(s, x0, y, f, paint(outline2, a, stroke=ow2))
    if outline is not None:
        c.drawString(s, x0, y, f, paint(outline, a, stroke=ow))
    c.drawString(s, x0, y, f, paint(color, a))
    reg_local(c, x0, y - size * 0.78, x0 + w, y + size * 0.22, tag)
    return w


# ------------------------------------------------------------------ the frame

class Stage:
    def __init__(self, bg=INK):
        self.arr = np.zeros((H, W, 4), np.uint8)
        self.arr[..., :3] = bg
        self.arr[..., 3] = 255
        self.s = skia.Surface(self.arr)
        self.c = self.s.getCanvas()


def image(arr):
    a = np.ascontiguousarray(arr if arr.shape[2] == 4 else np.dstack([arr, np.full(arr.shape[:2], 255, np.uint8)]))
    return skia.Image.fromarray(a, colorType=skia.kRGBA_8888_ColorType)


_cache = {}


def cached(name, fn):
    if name not in _cache:
        _cache[name] = fn()
    return _cache[name]


class layer:
    """with layer(c, a): ... -> composited at opacity a."""

    def __init__(self, c, a, blend=None):
        self.c, self.a, self.blend = c, a, blend

    def __enter__(self):
        p = skia.Paint()
        p.setAlphaf(self.a)
        if self.blend is not None:
            p.setBlendMode(self.blend)
        self.c.saveLayer(None, p)
        return self.c

    def __exit__(self, *a):
        self.c.restore()


# ------------------------------------------------------------------ keyed figures: the cheap green screen

class Fig:
    """Draw a figure through this and it is 'keyed' in: every shape is remembered (in device space) and on the way out
    a green spill halo and a jagged matte line are laid in BEHIND it, the tell-tale of a cheap chroma key."""

    def __init__(self, c):
        self.c = c
        self.sil = []

    def _keep(self, p, w=None):
        q = skia.Path(p)
        m = self.c.getTotalMatrix()
        q.transform(m)
        self.sil.append((q, None if w is None else w * math.sqrt(abs(m.getScaleX() * m.getScaleY() - m.getSkewX() * m.getSkewY()))))

    def fill(self, p, color, a=1.0, shader=None):
        self.c.drawPath(p, paint(color, a, shader=shader))
        self._keep(p)
        return p

    def stroke(self, p, color, w, a=1.0):
        self.c.drawPath(p, paint(color, a, stroke=w))
        self._keep(p, w)
        return p

    def circle(self, x, y, r, color, a=1.0, shader=None):
        p = skia.Path()
        p.addCircle(x, y, r)
        return self.fill(p, color, a, shader)

    def oval(self, x0, y0, x1, y1, color, a=1.0, shader=None):
        p = skia.Path()
        p.addOval(skia.Rect.MakeLTRB(x0, y0, x1, y1))
        return self.fill(p, color, a, shader)

    def rrect(self, x0, y0, x1, y1, r, color, a=1.0, shader=None):
        p = skia.Path()
        p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x0, y0, x1, y1), r, r))
        return self.fill(p, color, a, shader)

    def poly(self, pts, color, a=1.0, shader=None):
        return self.fill(path(pts), color, a, shader)

    def blob(self, pts, color, a=1.0, shader=None):
        return self.fill(smooth(pts), color, a, shader)


class keyed:
    """with keyed(c) as F: ... -> everything drawn through F is a figure pasted in by a bad chroma key."""

    def __init__(self, c, spill=KEY, halo=7.0, matte=True, a=1.0, shadow=True):
        self.c, self.spill, self.halo, self.matte, self.a, self.shadow = c, spill, halo, matte, a, shadow

    def __enter__(self):
        p = skia.Paint()
        p.setAlphaf(self.a)
        self.c.saveLayer(None, p)
        self.F = Fig(self.c)
        return self.F

    def _under(self, color, a, grow, dx=0.0, dy=0.0, blur=0.0, aa=True):
        c = self.c
        c.save()
        c.resetMatrix()
        c.translate(dx, dy)
        for q, w in self.F.sil:
            if w is None:
                pf = paint(color, a, blur=blur, aa=aa)
                pf.setBlendMode(skia.BlendMode.kDstOver)
                c.drawPath(q, pf)
                ps = paint(color, a, stroke=grow * 2, blur=blur, aa=aa)
            else:
                ps = paint(color, a, stroke=w + grow * 2, blur=blur, aa=aa)
            ps.setBlendMode(skia.BlendMode.kDstOver)
            c.drawPath(q, ps)
        c.restore()

    def __exit__(self, *a):
        if self.matte:
            self._under(mix(self.spill, INK, 0.45), 1.0, 2.0, aa=False)             # the hard, aliased matte line
        if self.halo > 0:
            self._under(self.spill, 0.55, self.halo, blur=self.halo * 0.6)           # green spill soaking the edges
        if self.shadow:
            self._under((20, 30, 20), 0.28, 2, 10, 14, blur=10)
        self.c.restore()


# ------------------------------------------------------------------ plastic early-CGI overlays

def cg_star(c, x, y, r, t, seed=0, color=LEMON, spin=1.0, a=1.0):
    """A glossy, spinning 3D plastic star (early-2000s CGI): the face squashes as it turns, the bevel catches light,
    a hard white specular spot slides across it. Smooth motion - computers don't animate on twos."""
    ang = t * 2.4 * spin + seed * 1.7
    sx = math.cos(ang)
    edge = abs(math.sin(ang))
    c.save()
    c.translate(x, y)
    c.rotate(math.degrees(math.sin(t * 1.3 + seed)) * 0.4)
    pts = []
    for i in range(10):
        an = -math.pi / 2 + math.pi / 5 * i
        q = r if i % 2 == 0 else r * 0.45
        pts.append((q * math.cos(an), q * math.sin(an)))
    face = [(px * sx, py) for px, py in pts]
    dark = mix(color, INK, 0.45)
    depth = r * 0.22 * edge * (1 if sx >= 0 else -1)
    c.drawPath(path([(px + depth, py + r * 0.05) for px, py in face]), paint(dark, a))              # the extrusion
    hi = mix(color, WHITE, 0.55)
    c.drawPath(path(face), paint(shader=lin((-r, -r), (r, r), [hi, color, mix(color, INK, 0.2)]), a=a))
    c.drawPath(path([(px * 0.55, py * 0.55) for px, py in face]), paint(WHITE, 0.25 * a))            # bevel
    spec_x = -r * 0.3 + r * 0.5 * math.sin(ang * 0.7)
    c.drawOval(skia.Rect.MakeXYWH(spec_x * abs(sx) - r * 0.14, -r * 0.45, r * 0.28, r * 0.16), paint(WHITE, 0.9 * a))
    c.restore()


def flare(c, x, y, t, k=1.0, color=(255, 240, 200)):
    """A cheap lens flare: a starburst, a halo and a string of coloured hexagons through the frame centre."""
    if k <= 0:
        return
    with layer(c, 1.0, skia.BlendMode.kPlus):
        c.drawCircle(x, y, 120 * k, paint(shader=rad((x, y), 120 * k, [(*color, 0.7), (*color, 0.0)])))
        for i in range(6):
            an = i * math.pi / 3 + t * 0.4
            c.drawLine(x - 260 * k * math.cos(an), y - 260 * k * math.sin(an), x + 260 * k * math.cos(an),
                       y + 260 * k * math.sin(an), paint(color, 0.35 * k, stroke=3))
        dx, dy = W / 2 - x, H / 2 - y
        for j, (u, s, cc) in enumerate(((0.5, 40, (120, 255, 160)), (0.9, 70, (255, 120, 220)), (1.3, 30, (120, 180, 255)),
                                        (1.7, 90, (255, 200, 90)))):
            px, py = x + dx * u, y + dy * u
            hexp = path([(px + s * k * math.cos(q * math.pi / 3), py + s * k * math.sin(q * math.pi / 3)) for q in range(6)])
            c.drawPath(hexp, paint(cc, 0.22 * k))


def chrome_text(c, s, x, y, size, t=0.0, fname="dela-400", face=((255, 250, 180), (255, 190, 40), (200, 90, 10)),
                edge=INK, depth=10, tag="chrome", wobble=0.0, max_w=None):
    """WordArt from a 2001 variety show: an extruded, gradient-filled, bevelled title with a fat outline."""
    f = font(fname, size)
    w = f.measureText(s)
    if max_w and w > max_w:
        size = size * max_w / w
        f = font(fname, size)
        w = f.measureText(s)
    c.save()
    c.translate(x, y)
    c.rotate(math.sin(t * 2.0) * wobble)
    x0 = -w / 2
    for d in range(depth, 0, -2):                                                   # the extrusion
        c.drawString(s, x0 + d * 0.8, d, f, paint(mix(face[2], INK, 0.55)))
    c.drawString(s, x0, 0, f, paint(edge, stroke=size * 0.14))
    c.drawString(s, x0, 0, f, paint(shader=lin((0, -size * 0.8), (0, size * 0.1), list(face))))
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x0 - 10, -size * 0.8, x0 + w + 10, -size * 0.45))
    c.drawString(s, x0, 0, f, paint(WHITE, 0.35))
    c.restore()
    reg_local(c, x0, -size * 0.8, x0 + w, size * 0.2, tag)
    c.restore()
    return w


# ------------------------------------------------------------------ claymation

def _lumps(n, seed, amp=0.05, t=0.0, boil_amp=0.012):
    """Radial multipliers for a hand-pressed outline: low lumps fixed by the sculptor, plus a per-drawing boil."""
    rng = np.random.default_rng(seed)
    a = np.linspace(0, 2 * math.pi, n, endpoint=False)
    r = np.ones(n)
    for h in (2, 3, 5, 7):
        r += amp * rng.uniform(0.3, 1.0) / (h ** 0.6) * np.sin(h * a + rng.uniform(0, 6.3))
    k = int(math.floor(t * 12 + 1e-6))
    rb = np.random.default_rng((seed * 131 + k * 977) % (2 ** 32))
    r += boil_amp * np.sin(np.arange(n) * rb.uniform(1.5, 3.0) + rb.uniform(0, 6.3))
    return a, r


_PRINTS = {}


def _print_arcs(seed):
    """One fingerprint as a list of arc paths (cached per seed): a loop of ridges, not quite closed."""
    if seed not in _PRINTS:
        rng = np.random.default_rng(seed)
        arcs = []
        for k in range(8):
            e = 0.22 + k * 0.11
            p = skia.Path()
            p.addArc(skia.Rect.MakeLTRB(-e, -e * 0.72, e, e * 0.72), float(rng.uniform(0, 70)), float(rng.uniform(210, 300)))
            arcs.append(p)
        _PRINTS[seed] = arcs
    return _PRINTS[seed]


def clay_path(c, p, color, t=0.0, seed=0, light=(-0.6, -0.8), prints=2, marks=2, gloss=0.22, rim=0.55):
    """Shade any path as solid modelling clay: a strong matte 3D roll-off (lit side, core shadow, reflected light at
    the far edge), a dark crease where it curls away, a soft waxy sheen, and the handling marks pressed INTO the
    surface - soft thumb-smoothed fingerprint whorls and short gouges with a lit lip - never thin lines."""
    b = p.computeTightBounds()
    cx, cy = b.centerX(), b.centerY()
    rw, rh = max(4.0, b.width() / 2), max(4.0, b.height() / 2)
    rr = max(rw, rh)
    lx, ly = light
    hi, lo, deep = mix(color, WHITE, 0.4), mix(color, INK, 0.42), mix(color, INK, 0.62)
    c.drawPath(p, paint(color))
    c.save()
    c.clipPath(p, doAntiAlias=True)
    c.drawPath(p, paint(shader=rad((cx + lx * rw * 0.35, cy + ly * rh * 0.35), rr * 1.25,
                                   [(*hi, 0.75), (*color, 0.15), (*lo, 0.55), (*deep, 0.9)], [0.0, 0.38, 0.72, 1.0])))
    c.drawPath(p, paint(deep, rim, stroke=max(4, rr * 0.1), blur=max(2, rr * 0.03)))       # the crease at the edge
    rng = np.random.default_rng(seed * 17 + 3)
    bx, by, _ = boil(t, 1.0, seed + 5)
    if rr > 50:
        for i in range(prints):                                                      # fingerprints, thumbed in
            fx = cx + rng.uniform(-0.4, 0.4) * rw + bx
            fy = cy + rng.uniform(-0.4, 0.4) * rh + by
            fs = min(rr * 0.45, 40) * rng.uniform(0.8, 1.1)
            c.save()
            c.translate(fx, fy)
            c.rotate(float(rng.uniform(0, 180)))
            c.scale(fs, fs)
            pd, pl = paint(lo, 0.26, stroke=3.2 / fs), paint(hi, 0.24, stroke=2.4 / fs)
            for arc in _print_arcs(seed * 7 + i)[:6]:
                c.drawPath(arc, pd)
            c.translate(1.6 / fs, 1.8 / fs)
            for arc in _print_arcs(seed * 7 + i)[:6]:
                c.drawPath(arc, pl)
            c.restore()
    for i in range(marks if rr > 40 else 0):                                         # gouges: a groove with a lit lip
        mx = cx + rng.uniform(-0.5, 0.5) * rw
        my = cy + rng.uniform(-0.5, 0.5) * rh
        L = min(rr * rng.uniform(0.12, 0.22), 40)
        an = rng.uniform(0, math.pi)
        pts = bez((mx - L * math.cos(an), my - L * math.sin(an)), (mx + rng.uniform(-6, 6), my + rng.uniform(-6, 6)),
                  (mx + L * math.cos(an), my + L * math.sin(an)), 8)
        c.drawPath(path(pts, closed=False), paint(deep, 0.45, stroke=6, blur=1.2))
        c.drawPath(path([(q[0] + 2.5, q[1] + 3.0) for q in pts], closed=False), paint(hi, 0.5, stroke=3.5))
    for i in range(int(6 + rr / 12)):                                                # grit and specks in the clay
        c.drawCircle(cx + rng.uniform(-rw, rw), cy + rng.uniform(-rh, rh), rng.uniform(1.2, 2.6), paint(deep, 0.35))
    if gloss > 0:                                                                    # a soft waxy sheen
        c.drawOval(skia.Rect.MakeXYWH(cx + lx * rw * 0.45 - rw * 0.22, cy + ly * rh * 0.45 - rh * 0.12, rw * 0.44, rh * 0.24),
                   paint(WHITE, gloss, blur=max(3, rr * 0.08)))
    c.restore()
    c.drawPath(p, paint(mix(color, INK, 0.7), 0.9, stroke=2.2))                     # a crisp silhouette edge
    return p


def clay_ellipse(c, cx, cy, rx, ry, color, t=0.0, seed=0, rot=0.0, amp=0.09, **kw):
    a, r = _lumps(56, seed, amp, t)
    ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    pts = [(cx + ca * rx * rr * math.cos(q) - sa * ry * rr * math.sin(q), cy + sa * rx * rr * math.cos(q) + ca * ry * rr * math.sin(q))
           for q, rr in zip(a, r)]
    return clay_path(c, smooth(pts), color, t, seed, **kw)


def clay_poly(c, pts, color, t=0.0, seed=0, amp=6.0, **kw):
    """A clay slab shaped from rough corner points: every edge sags and bulges a little, corners are pinched round."""
    rng = np.random.default_rng(seed)
    k = int(math.floor(t * 12 + 1e-6))
    rb = np.random.default_rng((seed * 131 + k * 977) % (2 ** 32))
    out = []
    n = len(pts)
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        for u in (0.0, 0.33, 0.66):
            x, y = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
            out.append((x + rng.uniform(-amp, amp) + rb.uniform(-1, 1), y + rng.uniform(-amp, amp) + rb.uniform(-1, 1)))
    return clay_path(c, smooth(out), color, t, seed, **kw)


def text_path(s, x, y, size, fname="dela-400", align="center"):
    """The outline of a string as one path (for clay lettering)."""
    f = font(fname, size)
    glyphs = f.textToGlyphs(s)
    widths = f.getWidths(glyphs)
    w = sum(widths)
    x0 = x - w / 2 if align == "center" else (x - w if align == "right" else x)
    p = skia.Path()
    for g, gw in zip(glyphs, widths):
        gp = f.getPath(g)
        if gp is not None:
            p.addPath(gp, x0, y)
        x0 += gw
    return p, w


def clay_text(c, s, x, y, size, color, t=0.0, seed=0, fname="dela-400", tag="claytext", align="center", wobble=3.0,
              max_w=900):
    """Lettering rolled out of clay: each drawing the letters sit a hair differently."""
    w0 = font(fname, size).measureText(s)
    if w0 > max_w:
        size *= max_w / w0
    bx, by, br = boil(t, wobble, seed)
    p, w = text_path(s, x + bx, y + by, size, fname, align)
    c.drawPath(p, paint(INK, 0.35, blur=6))
    clay_path(c, p, color, t, seed, prints=1, marks=1, rim=0.2, gloss=0.3)
    x0 = x - w / 2 if align == "center" else (x - w if align == "right" else x)
    reg_local(c, x0, y - size * 0.78, x0 + w, y + size * 0.22, tag)
    return w


def clay_shadow(c, cx, cy, rx, ry=None, a=0.35):
    c.drawOval(skia.Rect.MakeLTRB(cx - rx, cy - (ry or rx * 0.25), cx + rx, cy + (ry or rx * 0.25)), paint(INK, a, blur=rx * 0.12))


def clay_eye(c, x, y, r, t=0.0, look=(0.0, 0.0), seed=0, lid=0.0):
    """A glossy googly clay eye (a white ball with a black bead pressed in)."""
    clay_ellipse(c, x, y, r, r, (250, 250, 240), t, seed, amp=0.04, prints=0, marks=0, gloss=0.55, rim=0.3)
    bx, by, _ = boil(t, r * 0.04, seed + 9)
    c.drawCircle(x + look[0] * r * 0.4 + bx, y + look[1] * r * 0.4 + by, r * 0.45, paint(INK))
    c.drawCircle(x + look[0] * r * 0.4 - r * 0.15, y + look[1] * r * 0.4 - r * 0.18, r * 0.12, paint(WHITE))
    if lid > 0:
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(x - r * 1.2, y - r * 1.2, x + r * 1.2, y - r * 1.2 + 2.4 * r * lid))
        clay_ellipse(c, x, y, r * 1.02, r * 1.02, (200, 60, 110), t, seed + 1, amp=0.03, prints=0, marks=1)
        c.restore()


# ------------------------------------------------------------------ the look: crisp, over-lit, oversaturated video

def blur_small(rgb, radius=6, scale=4):
    im = Image.fromarray(np.ascontiguousarray(rgb[..., :3]))
    s = im.resize((W // scale, H // scale), Image.BILINEAR).filter(ImageFilter.GaussianBlur(radius))
    return np.asarray(s.resize((W, H), Image.BILINEAR))


_LIFT = {}


def video(arr, idx, sat=1.28, bloom=0.35, lift=0.04, noise=2.2, chroma=True, sharp=45):
    """Print the frame as cheap early-2000s video: pumped saturation, blown bright areas that bloom, a lifted,
    over-lit exposure, smeary chroma (4:1:1 DV colour), camcorder edge-sharpening and a hiss of fine video noise -
    no grain, no dust."""
    from PIL import ImageEnhance
    im = Image.fromarray(np.ascontiguousarray(arr[..., :3]))
    if sat != 1.0:
        im = ImageEnhance.Color(im).enhance(sat)
    if lift > 0:
        if lift not in _LIFT:
            _LIFT[lift] = [int(v * (1 - lift) + 255 * lift) for v in range(256)] * 3
        im = im.point(_LIFT[lift])
    if chroma:                                                   # colour smeared sideways, as on DV tape
        yy, cb, cr = im.convert("YCbCr").split()
        cb = cb.resize((W // 4, H), Image.BILINEAR).resize((W, H), Image.BILINEAR)
        cr = cr.resize((W // 4, H), Image.BILINEAR).resize((W, H), Image.BILINEAR)
        im = Image.merge("YCbCr", (yy, cb, cr)).convert("RGB")
    if sharp:
        im = im.filter(ImageFilter.UnsharpMask(radius=1.6, percent=sharp, threshold=0))
    if bloom > 0:                                                # blown highlights glow into their surroundings
        from PIL import ImageChops
        key = ("bp", bloom)
        if key not in _LIFT:
            _LIFT[key] = [int(max(0, v - 175) * bloom * 1.1) for v in range(256)] * 3
        glow = im.resize((W // 4, H // 4), Image.BILINEAR).point(_LIFT[key]).filter(ImageFilter.GaussianBlur(6))
        im = ImageChops.add(im, glow.resize((W, H), Image.BILINEAR))
    if noise > 0:
        rng = np.random.default_rng(idx * 31 + 7)
        n = rng.normal(0, noise, (H // 2, W // 2)).astype(np.int16).repeat(2, 0).repeat(2, 1)
        out = np.asarray(im).astype(np.int16) + n[..., None]
        arr[..., :3] = np.clip(out, 0, 255).astype(np.uint8)
    else:
        arr[..., :3] = np.asarray(im)


def sharpen(arr, amt=0.45):
    arr[..., :3] = np.asarray(Image.fromarray(np.ascontiguousarray(arr[..., :3])).filter(
        ImageFilter.UnsharpMask(radius=1.6, percent=int(amt * 100), threshold=0)))


def night(arr, k=1.0, tint=(40, 20, 110)):
    """Day-for-night / storm: darker, bluer, but the bright lights still pop."""
    if k <= 0:
        return
    rgb = arr[..., :3].astype(np.float32)
    lum = rgb.mean(axis=2, keepdims=True)
    dark = rgb * 0.45 + np.array(tint, np.float32) * 0.35
    hot = np.clip((lum - 200) / 55, 0, 1)
    out = rgb * (1 - k) + (dark * (1 - hot) + rgb * hot) * k
    arr[..., :3] = np.clip(out, 0, 255).astype(np.uint8)


def red(arr, k=1.0):
    """The horror flush: the whole bright picture goes blood-red and bruise-purple (colours stay loud)."""
    if k <= 0:
        return
    rgb = arr[..., :3].astype(np.float32)
    y = np.clip(rgb @ np.array([0.3, 0.55, 0.15], np.float32), 0, 255) / 255
    lo = np.array(BRUISE, np.float32)
    md = np.array((235, 10, 40), np.float32)
    hi = np.array((255, 220, 120), np.float32)
    yy = y[..., None]
    tone = np.where(yy < 0.55, lo + (md - lo) * (yy / 0.55), md + (hi - md) * ((yy - 0.55) / 0.45) ** 1.5)
    arr[..., :3] = np.clip(rgb * (1 - k) + tone * k, 0, 255).astype(np.uint8)


# ------------------------------------------------------------------ transitions (the video mixer's cheesy wipes)

def star_path(cx, cy, r, n=5, inner=0.45, rot=0.0):
    pts = []
    for i in range(n * 2):
        an = math.radians(rot) - math.pi / 2 + math.pi / n * i
        q = r if i % 2 == 0 else r * inner
        pts.append((cx + q * math.cos(an), cy + q * math.sin(an)))
    return path(pts)


def star_wipe(a, b, k, cx=W / 2, cy=H / 2 - 80):
    """The star wipe: the new shot bursts out of a growing, spinning star, with a hot pink edge."""
    k = ease(k)
    out = a.copy()
    r = 2400 * k
    s = skia.Surface(out)
    c = s.getCanvas()
    img = image(b)
    c.save()
    c.clipPath(star_path(cx, cy, r, rot=k * 90), doAntiAlias=True)
    c.drawImage(img, 0, 0)
    c.restore()
    c.drawPath(star_path(cx, cy, r, rot=k * 90), paint(HOT, stroke=18))
    c.drawPath(star_path(cx, cy, r, rot=k * 90), paint(LEMON, stroke=7))
    return out


def spin_out(a, b, k):
    """The frame spins away into the distance, revealing the next shot behind it (a 2001 video 'tumble')."""
    k = ease(k)
    out = b.copy()
    s = skia.Surface(out)
    c = s.getCanvas()
    sc = 1 - k
    if sc > 0.01:
        c.save()
        c.translate(W / 2, H / 2)
        c.rotate(k * 540)
        c.scale(sc, sc)
        c.translate(-W / 2, -H / 2)
        c.drawRect(skia.Rect.MakeWH(W, H).makeOffset(14, 18), paint(INK, 0.5, blur=12))
        c.drawImage(image(a), 0, 0)
        c.restore()
    return out


# ------------------------------------------------------------------ bits that recur

def starburst(c, cx, cy, t, colors=(HOT, LEMON), n=18, spin=0.25):
    """A rotating sunburst of alternating rays: the variety-show backdrop."""
    c.drawRect(skia.Rect.MakeWH(W, H), paint(colors[0]))
    R = 2600
    for i in range(0, n * 2, 2):
        a0 = (i / (n * 2)) * 2 * math.pi + t * spin
        a1 = ((i + 1) / (n * 2)) * 2 * math.pi + t * spin
        c.drawPath(path([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)), (cx + R * math.cos(a1), cy + R * math.sin(a1))]),
                   paint(colors[1]))


def drip(c, x, y, w, L, color=BLOOD, a=1.0):
    """A paint drip: a run ending in a fat drop."""
    c.drawRect(skia.Rect.MakeLTRB(x - w / 2, y, x + w / 2, y + L), paint(color, a))
    c.drawCircle(x, y + L, w * 0.9, paint(color, a))


def burst_plate(c, cx, cy, r, t, color=LEMON, edge=HOT, spikes=14, ry=None):
    """A jagged 'BAM' plate for a telop number (r across, ry up and down)."""
    pts = []
    ry = ry or r * 0.8
    for i in range(spikes * 2):
        an = i * math.pi / spikes + t * 0.2
        q = 1.0 if i % 2 == 0 else 0.8
        pts.append((cx + r * q * math.cos(an), cy + ry * q * math.sin(an)))
    c.drawPath(path(pts), paint(edge, stroke=16))
    c.drawPath(path(pts), paint(color))

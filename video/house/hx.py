"""The House look, as a toolkit.

A 1977 collage-horror film made by hand: painted skies behind the actors, figures that are obviously pasted on
(white paper edges, drop shadows, a green-blue matte fringe where the "blue screen" didn't key cleanly), sparkles and
flames scratched onto the film by hand, dreamy soft focus for the sweet scenes and a hard lurid red for the horror,
all printed on faded 1970s stock (grain, halation, dust, scratches, gate weave, flicker).

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

# palette: candy pastels against blood red, sunset orange and black
PEACH, PINK, MINT, POWDER, LILAC, CREAM = (255, 203, 164), (255, 170, 200), (170, 236, 206), (170, 206, 250), (214, 184, 250), (255, 244, 222)
BLOOD, SUNSET, EMBER, INK, PLUM = (196, 10, 30), (255, 118, 40), (255, 70, 30), (16, 8, 14), (84, 22, 70)
GOLD, WHITE, SKIN = (255, 206, 90), (255, 255, 255), (250, 214, 190)
FRINGE = (40, 255, 190)          # the blue/green-screen spill around a badly keyed figure

TEXT = []                        # lettering drawn this frame, for the collision lint: (x0, y0, x1, y1, tag)


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


def paint(c=INK, a=1.0, stroke=None, blur=0.0, shader=None, cap="round"):
    p = skia.Paint(AntiAlias=True)
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
    return skia.GradientShader.MakeRadial(skia.Point(*c0), r, [c.toColor() for c in cs], pos)


def path(pts, closed=True):
    p = skia.Path()
    pts = list(pts)
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
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


# ------------------------------------------------------------------ time: stop-motion, sped-up, reverse

def stop(t, fps=8):
    """Stop-motion time: the puppet only gets a new position `fps` times a second (jerky, held drawings)."""
    return math.floor(t * fps + 1e-6) / fps


def jit(t, amp=1.0, seed=0, fps=8):
    """A per-drawing nudge (the animator's hand never puts the paper back exactly)."""
    k = int(math.floor(t * fps + 1e-6))
    r = np.random.default_rng((seed * 7919 + k * 104729) % (2 ** 32))
    return r.uniform(-amp, amp), r.uniform(-amp, amp), r.uniform(-amp, amp)


def pop(t, a, dur=0.2, amp=0.25):
    """0 before a, then a jerky overshooting scale-in, on the stop-motion clock."""
    if t < a:
        return 0.0
    t = stop(t, 12)
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


def text(c, s, x, y, size, fname="shrikhand-400", color=INK, align="center", tag="label", a=1.0, outline=None, ow=8):
    """One line of lettering at baseline y, registered for the lint."""
    f = font(fname, size)
    w = f.measureText(s)
    x0 = x - w / 2 if align == "center" else (x - w if align == "right" else x)
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
    """with layer(c, 0.2): ... -> everything inside is composited at that opacity (a double exposure)."""

    def __init__(self, c, a):
        self.c, self.a = c, a

    def __enter__(self):
        p = skia.Paint()
        p.setAlphaf(self.a)
        self.c.saveLayer(None, p)
        return self.c

    def __exit__(self, *a):
        self.c.restore()


# ------------------------------------------------------------------ paper cut-outs

class Fig:
    """Draw a figure through this and it becomes a pasted-on paper cut-out: every shape is remembered (in device
    space), and on the way out the paper edge, the matte fringe and the drop shadow are laid in BEHIND it."""

    def __init__(self, c):
        self.c = c
        self.sil = []                                   # (device-space path, stroke width or None)

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


class figure:
    """with figure(c) as F: ... -> F.fill / F.circle / ... ; everything drawn becomes one cut-out."""

    def __init__(self, c, border=7.0, fringe=(-7, -3), fringe_col=FRINGE, shadow=(12, 14, 8, 0.5), a=1.0, bounds=None):
        self.c, self.border, self.fringe, self.fringe_col, self.shadow, self.a, self.bounds = c, border, fringe, fringe_col, shadow, a, bounds

    def __enter__(self):
        p = skia.Paint()
        p.setAlphaf(self.a)
        self.c.saveLayer(skia.Rect.MakeLTRB(*self.bounds) if self.bounds else None, p)
        self.F = Fig(self.c)
        return self.F

    def _under(self, color, a, grow, dx=0.0, dy=0.0, blur=0.0):
        c = self.c
        pf = paint(color, a, blur=blur)
        pf.setBlendMode(skia.BlendMode.kDstOver)
        ps = paint(color, a, stroke=grow * 2, blur=blur)
        ps.setBlendMode(skia.BlendMode.kDstOver)
        c.save()
        c.resetMatrix()
        c.translate(dx, dy)
        for q, w in self.F.sil:
            if w is None:
                c.drawPath(q, pf)
                c.drawPath(q, ps)
            else:
                pw = paint(color, a, stroke=w + grow * 2, blur=blur)
                pw.setBlendMode(skia.BlendMode.kDstOver)
                c.drawPath(q, pw)
        c.restore()

    def __exit__(self, *a):
        b = self.border
        if b > 0:
            self._under(WHITE, 1.0, b)                                   # the scissor-cut paper edge
        if self.fringe is not None:
            self._under(self.fringe_col, 0.8, b + 4, self.fringe[0], self.fringe[1], blur=1.5)
        if self.shadow is not None:
            dx, dy, sg, sa = self.shadow
            self._under((30, 6, 20), sa, b, dx, dy, blur=sg)
        self.c.restore()


# ------------------------------------------------------------------ painted things

def brushwork(c, x0, y0, x1, y1, base, spread=26, n=900, seed=0, size=(18, 60), a=0.35, angle=0.0, jitter_a=0.35):
    """Loose, visible brush strokes in colours around `base`: the painter's hand on a backdrop."""
    rng = np.random.default_rng(seed)
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        L = rng.uniform(*size)
        ang = angle + rng.normal(0, jitter_a)
        cc = tuple(int(np.clip(v + rng.normal(0, spread), 0, 255)) for v in base)
        dx, dy = L * math.cos(ang), L * math.sin(ang)
        c.drawLine(x - dx / 2, y - dy / 2, x + dx / 2, y + dy / 2, paint(cc, a * rng.uniform(0.5, 1.0), stroke=rng.uniform(4, 14)))


def painted_sky(w, h, seed=0, bands=None, sun=(0.62, 0.66, 0.16), clouds=True):
    """A garish painted sunset: hot bands of orange, pink and violet laid in with the brush, a huge sun, streaky clouds."""
    bands = bands or [(70, 20, 90), (160, 40, 130), (255, 90, 120), (255, 140, 60), (255, 200, 90), (255, 120, 60)]
    arr = np.zeros((h, w, 4), np.uint8)
    arr[..., 3] = 255
    s = skia.Surface(arr)
    c = s.getCanvas()
    c.drawRect(skia.Rect.MakeWH(w, h), paint(shader=lin((0, 0), (0, h), bands)))
    rng = np.random.default_rng(seed)
    for i in range(len(bands) * 2):                                   # horizontal brush sweeps along the bands
        k = i / (len(bands) * 2 - 1)
        base = bands[min(len(bands) - 1, int(k * (len(bands) - 1) + 0.5))]
        brushwork(c, 0, k * h - h * 0.08, w, k * h + h * 0.08, base, spread=22, n=int(w * 0.35), seed=seed + i,
                  size=(w * 0.04, w * 0.16), a=0.22, jitter_a=0.06)
    sx, sy, sr = sun[0] * w, sun[1] * h, sun[2] * w
    c.drawCircle(sx, sy, sr * 2.6, paint(shader=rad((sx, sy), sr * 2.6, [(255, 230, 150, 0.55), (255, 150, 80, 0.0)])))
    c.drawCircle(sx, sy, sr, paint((255, 236, 170)))
    c.drawCircle(sx, sy, sr, paint(shader=rad((sx, sy - sr * 0.3), sr, [(255, 250, 220), (255, 170, 80)])))
    for j in range(7):                                                # the sun sliced by thin cloud streaks
        yy = sy - sr * 0.4 + j * sr * 0.22
        c.drawRect(skia.Rect.MakeLTRB(sx - sr * 1.6, yy, sx + sr * 1.6, yy + sr * 0.05), paint((255, 110, 110), 0.55))
    if clouds:
        for j in range(9):
            cy = rng.uniform(0.12, 0.55) * h
            cx = rng.uniform(-0.1, 1.0) * w
            L = rng.uniform(0.3, 0.7) * w
            for q in range(10):
                c.drawLine(cx + rng.uniform(0, 30), cy + q * 5 + rng.uniform(-3, 3), cx + L + rng.uniform(-30, 30), cy + q * 4,
                           paint((255, rng.integers(150, 220), rng.integers(170, 230)), 0.28, stroke=rng.uniform(6, 16)))
    return arr


def hills(c, w, y, h, color=(40, 12, 50), seed=0, trees=True):
    """Silhouetted hills and lollipop trees against the painted sky."""
    rng = np.random.default_rng(seed)
    pts = [(0, y + h)]
    for i in range(12):
        pts.append((i * w / 11, y + rng.uniform(0, h * 0.5)))
    pts.append((w, y + h))
    pts += [(w, y + h * 3), (0, y + h * 3)]
    c.drawPath(path(pts), paint(color))
    if trees:
        for i in range(6):
            tx = rng.uniform(0, w)
            th = rng.uniform(0.6, 1.2) * h
            ty = y + h * 0.4
            c.drawRect(skia.Rect.MakeLTRB(tx - 4, ty - th, tx + 4, ty), paint(color))
            c.drawCircle(tx, ty - th, th * 0.35, paint(color))


# ------------------------------------------------------------------ hand-drawn animation, scratched onto the film

def sparkle(c, x, y, r, t, seed=0, color=(255, 250, 220), a=1.0):
    """A four-point star, drawn by hand: it boils (redrawn slightly different every drawing) and twinkles."""
    jx, jy, jr = jit(t, 1.0, seed, 12)
    k = 0.75 + 0.25 * math.sin(stop(t, 12) * 9 + seed)
    rr = 1.45 * r * k * (1 + jr * 0.1)
    pts = []
    for i in range(8):
        ang = math.pi / 4 * i + jr * 0.05
        q = rr if i % 2 == 0 else rr * 0.18
        pts.append((x + jx * 2 + q * math.cos(ang), y + jy * 2 + q * math.sin(ang)))
    c.drawCircle(x, y, rr * 0.9, paint(color, 0.3 * a, blur=rr * 0.4))
    for i in range(4):                                                  # long thin glints between the points
        ang = math.pi / 4 + math.pi / 2 * i + jr * 0.05
        c.drawLine(x, y, x + rr * 0.75 * math.cos(ang), y + rr * 0.75 * math.sin(ang), paint(color, 0.8 * a, stroke=max(1.5, rr * 0.05)))
    c.drawPath(path(pts), paint(color, a))
    c.drawCircle(x, y, rr * 0.12, paint(WHITE, a))


def _tongue(x, y, bw, h, lean, curl, wob):
    """One inked flame tongue: a fat bulb at the base, S-curved sides, a tip that curls over."""
    tx, ty = x + lean * h, y - h
    p = skia.Path()
    p.moveTo(x - bw, y)
    p.cubicTo(x - bw * 1.45, y - h * 0.3, x - bw * 0.2 + wob[0] * bw + lean * h * 0.3, y - h * 0.55,
              tx - curl * bw * 0.9, ty + h * 0.12)
    p.quadTo(tx - curl * bw * 0.2, ty - h * 0.02, tx, ty)
    p.cubicTo(tx + bw * 0.25 + curl * bw * 0.3, ty + h * 0.3, x + bw * 0.9 + wob[1] * bw, y - h * 0.35, x + bw, y)
    p.cubicTo(x + bw * 0.7, y + bw * 0.55, x - bw * 0.7, y + bw * 0.55, x - bw, y)
    p.close()
    return p


def flame(c, x, y, h, t, seed=0, a=1.0, ink=True):
    """A hand-drawn cartoon flame scratched onto the film: five curling tongues with a fat inked outline, an orange
    body, a yellow heart and a white-hot core, plus sparks flying off. Redrawn on twos, so it boils."""
    k = int(stop(t, 12) * 12)
    rng = np.random.default_rng((seed * 7717 + k * 131) % (2 ** 32))
    bw = h * 0.17
    spec = [(-1.1, 0.55, -0.22), (-0.55, 0.8, -0.1), (0.0, 1.0, 0.04), (0.55, 0.78, 0.14), (1.1, 0.5, 0.25)]
    tongues = []
    for dx, hh, lean in spec:
        hk = hh * (1 + rng.uniform(-0.16, 0.16))
        lk = lean + rng.uniform(-0.12, 0.12)
        curl = (1 if lk > 0 else -1) * rng.uniform(0.3, 1.0)
        tongues.append((x + dx * bw * 1.1, hk, lk, curl, (rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3))))
    outer = None
    for tx_, hk, lk, curl, wob in tongues:
        p = _tongue(tx_, y, bw, h * hk, lk, curl, wob)
        outer = p if outer is None else (skia.Op(outer, p, skia.PathOp.kUnion_PathOp) or outer)
    if ink:
        c.drawPath(outer, paint(INK, a, stroke=max(3.0, h * 0.028)))
    c.drawPath(outer, paint(EMBER, a))
    for colr, sc in ((SUNSET, 0.72), (GOLD, 0.48), ((255, 250, 225), 0.24)):
        for i, (tx_, hk, lk, curl, wob) in enumerate(tongues[1:4] if sc < 0.7 else tongues):
            if sc < 0.4 and i != 1:
                continue
            c.drawPath(_tongue(x + (tx_ - x) * sc, y - bw * 0.1, bw * sc, h * hk * sc * 1.05, lk, curl, wob), paint(colr, a))
    for i in range(3):                                                   # sparks and loose drops flying off
        u = (k * 0.17 + i * 0.37 + seed * 0.11) % 1.0
        sx = x + (rng.uniform(-1, 1) * bw * 2.2) + (i - 1) * bw * 0.6
        sy = y - h * (0.9 + 0.7 * u)
        r = h * 0.05 * (1 - u * 0.6)
        drop = path([(sx, sy - r * 2.4), (sx + r, sy), (sx, sy + r), (sx - r, sy)])
        if ink:
            c.drawPath(drop, paint(INK, a * (1 - u), stroke=2.5))
        c.drawPath(drop, paint(GOLD if i % 2 else SUNSET, a * (1 - u)))


def star(c, x, y, r, color=GOLD, a=1.0, rot=0.0, n=5, inner=0.45, outline=INK, ow=5):
    """A fat five-point star (the teacher's gold star; a sticker)."""
    pts = []
    for i in range(n * 2):
        ang = math.radians(rot - 90) + math.pi / n * i
        q = r if i % 2 == 0 else r * inner
        pts.append((x + q * math.cos(ang), y + q * math.sin(ang)))
    p = path(pts)
    if outline is not None:
        c.drawPath(p, paint(outline, a, stroke=ow))
    c.drawPath(p, paint(color, a))
    return p


def scribble(c, x, y, r, t, seed=0, color=INK, w=6, a=1.0, loops=5):
    """A furious pencil scribble, re-scratched every drawing."""
    k = int(stop(t, 12) * 12)
    rng = np.random.default_rng(seed * 131 + k)
    pts = []
    for i in range(loops * 10):
        ang = i * 0.63 + rng.normal(0, 0.2)
        rr = r * (0.4 + 0.6 * rng.uniform())
        pts.append((x + rr * math.cos(ang), y + rr * math.sin(ang) * 0.7))
    c.drawPath(path(pts, closed=False), paint(color, a, stroke=w))


def heart(c, x, y, s, color=PINK, a=1.0):
    p = skia.Path()
    p.moveTo(x, y + s * 0.9)
    p.cubicTo(x - s * 1.4, y, x - s * 0.6, y - s * 1.0, x, y - s * 0.35)
    p.cubicTo(x + s * 0.6, y - s * 1.0, x + s * 1.4, y, x, y + s * 0.9)
    c.drawPath(p, paint(color, a))
    return p


def drip(c, x, y, w, L, color=BLOOD, a=1.0):
    """A paint drip: a thin run ending in a fat drop."""
    c.drawRect(skia.Rect.MakeLTRB(x - w / 2, y, x + w / 2, y + L), paint(color, a))
    c.drawCircle(x, y + L, w * 0.9, paint(color, a))


# ------------------------------------------------------------------ looks: sweet soft focus, horror red

def _to_img(a):
    return Image.fromarray(np.ascontiguousarray(a[..., :3]))


def blur_small(rgb, radius=6, scale=4):
    """A fast wide blur: shrink, blur, grow (the vaseline-on-the-lens halo)."""
    im = _to_img(rgb)
    s = im.resize((W // scale, H // scale), Image.BILINEAR).filter(ImageFilter.GaussianBlur(radius))
    return np.asarray(s.resize((W, H), Image.BILINEAR))


def soft_focus(arr, k=0.5, bloom=0.3):
    """Dreamy soft focus: the picture blended with its own blur, highlights blooming into pastel haze."""
    if k <= 0 and bloom <= 0:
        return
    rgb = arr[..., :3].astype(np.float32)
    bl = blur_small(arr, 7).astype(np.float32)
    hi = np.clip(bl - 150, 0, 255) * (255 / 105)
    out = rgb + (bl - rgb) * (0.42 * k) + hi * bloom * 0.35
    out = out * (1 - 0.05 * k) + 255 * 0.05 * k                       # a milky lift
    arr[..., :3] = np.clip(out, 0, 255).astype(np.uint8)


def horror(arr, k=1.0, red=BLOOD):
    """The horror grade: everything pushed to hard, lurid red and black."""
    if k <= 0:
        return
    rgb = arr[..., :3].astype(np.float32)
    y = rgb[..., 0] * 0.35 + rgb[..., 1] * 0.5 + rgb[..., 2] * 0.15
    y = np.clip((y - 30) * 1.25, 0, 255) / 255
    r = np.array((230, 10, 30), np.float32)
    hot = np.array((255, 206, 160), np.float32)
    yy = y[..., None]
    lo = np.clip(yy / 0.82, 0, 1) ** 0.75
    hi = np.clip((yy - 0.82) / 0.18, 0, 1) ** 2
    tone = np.where(yy < 0.82, lo * r, r + (hot - r) * hi)
    arr[..., :3] = np.clip(rgb * (1 - k) + tone * k, 0, 255).astype(np.uint8)


# ------------------------------------------------------------------ the 1970s print

_GRAIN = []
_VIG = None


def _grain_pool():
    if not _GRAIN:
        rng = np.random.default_rng(1977)
        for i in range(24):
            n = rng.normal(0, 1, (H // 4, W // 4)).astype(np.float32)
            g = np.asarray(Image.fromarray(np.clip(n * 42 + 128, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR))
            _GRAIN.append(g.astype(np.int16) - 128)
    return _GRAIN


def _vignette():
    global _VIG
    if _VIG is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = ((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.6)) ** 2
        _VIG = np.clip(1.0 - 0.42 * d ** 1.4, 0.45, 1.0)[..., None].astype(np.float32)
    return _VIG


def film(arr, T, idx, grain=1.0, dust=1.0, weave=1.0, fade=1.0):
    """Print the frame on faded 1970s stock: lifted blacks and a warm cast, halation round the highlights, animated grain
    clumps, dust, hairs and scratches, a vignette, the gate weaving and the lamp flickering."""
    rng = np.random.default_rng(idx * 7 + 3)
    rgb = arr[..., :3].astype(np.float32)
    # halation: the bright parts bleed a red-orange glow into the emulsion around them
    bl = blur_small(arr, 5).astype(np.float32)
    hal = np.clip(bl.mean(axis=2, keepdims=True) - 170, 0, 255) / 85.0
    rgb += hal * np.array((70, 26, 8), np.float32) * fade
    # faded stock: lifted, warm blacks; slightly muted colour; creamy highlights
    lum = rgb.mean(axis=2, keepdims=True)
    rgb = lum + (rgb - lum) * (1 - 0.14 * fade)
    rgb = rgb * (1 - 0.1 * fade) + np.array((34, 20, 22), np.float32) * fade
    rgb *= np.array((1.03, 1.0, 0.93), np.float32) ** fade
    # the lamp flickers
    rgb *= 1.0 + rng.normal(0, 0.018) * weave
    rgb *= _vignette()
    g = _grain_pool()[int(np.random.default_rng(idx // 2 * 5 + 1).integers(0, 24))]   # grain changes every 2 frames
    rgb += g[..., None] * (0.19 * grain)
    out = np.clip(rgb, 0, 255).astype(np.uint8)
    # gate weave: the whole picture drifts and jumps a pixel or two
    dx = int(round(math.sin(T * 5.3) * 1.5 * weave + rng.normal(0, 0.6) * weave))
    dy = int(round(math.sin(T * 3.1 + 1) * 2.0 * weave + (rng.random() < 0.03) * 5 * weave))
    if dx or dy:
        out = np.roll(out, (dy, dx), axis=(0, 1))
    arr[..., :3] = out
    if dust > 0:
        c = skia.Surface(arr).getCanvas()
        for _ in range(int(rng.poisson(5 * dust))):                           # dust specks: dark and light
            x, y = rng.uniform(0, W), rng.uniform(0, H)
            r = rng.uniform(1.5, 5.5)
            c.drawCircle(x, y, r, paint(INK if rng.random() < 0.7 else CREAM, rng.uniform(0.35, 0.8)))
        if rng.random() < 0.18 * dust:                                        # a hair in the gate
            x, y = rng.uniform(100, W - 100), rng.uniform(200, H - 200)
            pts = bez((x, y), (x + rng.uniform(-80, 80), y + rng.uniform(-60, 60)), (x + rng.uniform(-120, 120), y + rng.uniform(40, 160)))
            c.drawPath(path(pts, closed=False), paint(INK, 0.6, stroke=2.2))
        if rng.random() < 0.35 * dust:                                        # a vertical scratch running down the reel
            x = (idx * 13 % W) if rng.random() < 0.5 else rng.uniform(40, W - 40)
            c.drawLine(x, 0, x + rng.uniform(-6, 6), H, paint(CREAM, rng.uniform(0.25, 0.5), stroke=rng.uniform(1.5, 3)))


# ------------------------------------------------------------------ editing devices

def iris(arr, cx, cy, r, feather=6):
    """An iris: everything outside a circle goes black (the old silent-film wipe)."""
    if r >= math.hypot(W, H):
        return
    c = skia.Surface(arr).getCanvas()
    p = skia.Path()
    p.addRect(skia.Rect.MakeWH(W, H))
    p.addCircle(cx, cy, max(0.0, r))
    p.setFillType(skia.PathFillType.kEvenOdd)
    c.drawPath(p, paint(INK, 1.0, blur=feather))
    c.drawPath(p, paint(INK))


def ornate_frame(c, x0, y0, x1, y1, color=CREAM, w=5):
    """The border of a silent-film title card: double rule, corner curls and a little diamond at each side."""
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(color, stroke=w))
    c.drawRect(skia.Rect.MakeLTRB(x0 + 16, y0 + 16, x1 - 16, y1 - 16), paint(color, stroke=w * 0.5))
    for sx, sy, fx, fy in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        pts = bez((sx + fx * 16, sy + fy * 60), (sx + fx * 60, sy + fy * 60), (sx + fx * 60, sy + fy * 16))
        c.drawPath(path(pts, closed=False), paint(color, stroke=w * 0.7))
        c.drawCircle(sx + fx * 44, sy + fy * 44, 7, paint(color))
    for mx, my in (((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1), (x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2)):
        c.drawPath(path([(mx - 14, my), (mx, my - 14), (mx + 14, my), (mx, my + 14)]), paint(color))


def title_card(lines, size=84, sub=None, sub_size=40, fname="fell-sc-400", color=CREAM, bg=INK, y_center=880, tag="card",
               box=(90, 520, 990, 1240)):
    """A silent-film title card, filling the frame."""
    st = Stage(bg)
    c = st.c
    x0, y0, x1, y1 = box
    ornate_frame(c, x0, y0, x1, y1, color)
    f = font(fname, size)
    lh = size * 1.18
    total = lh * len(lines) + (sub_size * 1.6 if sub else 0)
    y = y_center - total / 2 + size * 0.8
    for ln in lines:
        text(c, ln, W / 2, y, size, fname, color, tag=tag)
        y += lh
    if sub:
        text(c, sub, W / 2, y + sub_size * 0.4, sub_size, "fell-400-italic", color, tag=tag)
    return st.arr


def photo(c, img_arr, x, y, w, h, rot=0.0, border=22, bottom=70, corners=True, tint=None):
    """A still photo stuck into the album: white border (wider at the bottom), the picture, photo corners."""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    fr = skia.Rect.MakeLTRB(-w / 2 - border, -h / 2 - border, w / 2 + border, h / 2 + bottom)
    c.drawRect(fr.makeOffset(10, 12), paint(INK, 0.45, blur=6))
    c.drawRect(fr, paint((252, 248, 238)))
    im = image(img_arr)
    c.drawImageRect(im, skia.Rect.MakeLTRB(-w / 2, -h / 2, w / 2, h / 2), skia.SamplingOptions(skia.FilterMode.kLinear))
    if tint is not None:
        c.drawRect(skia.Rect.MakeLTRB(-w / 2, -h / 2, w / 2, h / 2), paint(tint[:3], tint[3]))
    if corners:
        for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            cx_, cy_ = sx * (w / 2 + border), sy * (h / 2 + (border if sy < 0 else bottom))
            c.drawPath(path([(cx_, cy_), (cx_ - sx * 64, cy_), (cx_, cy_ - sy * 64)]), paint((30, 20, 24)))
    c.restore()


def split(frames, layout="v", gap=10, color=INK, texts=None):
    """A split screen: two or three frames side by side (or stacked), each showing its own centre.
    texts: for each frame, the (start, end) slice of TEXT it registered - remapped into its pane."""
    if texts is not None:
        n = len(frames)
        keep = TEXT[:texts[0][0]]
        for i, (a, b) in enumerate(texts):
            if layout == "v":
                cw = (W - gap * (n - 1)) // n
                x0, s0 = i * (cw + gap), (W - cw) // 2
                for bx in TEXT[a:b]:
                    nx0, nx1 = max(bx[0] - s0 + x0, x0), min(bx[2] - s0 + x0, x0 + cw)
                    if nx1 - nx0 > 4:
                        keep.append((nx0, bx[1], nx1, bx[3], bx[4]))
            else:
                ch = (H - gap * (n - 1)) // n
                y0, s0 = i * (ch + gap), (H - ch) // 2
                for bx in TEXT[a:b]:
                    ny0, ny1 = max(bx[1] - s0 + y0, y0), min(bx[3] - s0 + y0, y0 + ch)
                    if ny1 - ny0 > 4:
                        keep.append((bx[0], ny0, bx[2], ny1, bx[4]))
        TEXT[:] = keep
    out = np.zeros((H, W, 4), np.uint8)
    out[..., :3] = color
    out[..., 3] = 255
    n = len(frames)
    if layout == "v":
        cw = (W - gap * (n - 1)) // n
        for i, f in enumerate(frames):
            x0 = i * (cw + gap)
            s0 = (W - cw) // 2
            out[:, x0:x0 + cw] = f[:, s0:s0 + cw]
    else:
        ch = (H - gap * (n - 1)) // n
        for i, f in enumerate(frames):
            y0 = i * (ch + gap)
            s0 = (H - ch) // 2
            out[y0:y0 + ch] = f[s0:s0 + ch]
    return out


def crash_zoom(arr, z, cx=W / 2, cy=H / 2):
    """A crash zoom: the frame punched in by z (>1) around (cx, cy); registered lettering is moved to match."""
    if z <= 1.001:
        return arr
    im = Image.fromarray(np.ascontiguousarray(arr[..., :3]))
    w, h = W / z, H / z
    x0, y0 = min(max(0, cx - w / 2), W - w), min(max(0, cy - h / 2), H - h)
    out = arr.copy()
    out[..., :3] = np.asarray(im.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + w, y0 + h)))
    TEXT[:] = [((a - x0) * z, (b - y0) * z, (c_ - x0) * z, (d - y0) * z, tg) for a, b, c_, d, tg in TEXT]
    return out


def freeze_look(arr, k=1.0):
    """A freeze frame printed like a still: a little sepia, a flash of white on the first frame."""
    rgb = arr[..., :3].astype(np.float32)
    y = rgb.mean(axis=2, keepdims=True)
    sep = y * np.array((1.08, 0.95, 0.78), np.float32)
    arr[..., :3] = np.clip(rgb * (1 - 0.45 * k) + sep * 0.45 * k, 0, 255).astype(np.uint8)

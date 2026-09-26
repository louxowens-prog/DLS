"""Comic-book-come-alive toolkit: the print-and-ink look of the 2018 animated multiverse film, built procedurally.

print   halftone dot shading (dots >= 8 px so they survive phone compression), hatching, cyan/magenta plate
        misregistration instead of blur for out-of-focus planes, a fixed newsprint grain
ink     tapered brush strokes, bold contours, speed lines, focus lines
page    panels and gutters, yellow narration boxes, speech / thought / shout bubbles, drawn sound words,
        impact frames, 'spider-sense' squiggles around a head
glitch  RGB split, displaced slices, shards and flicker between dimensions
time    characters are drawn on twos (12 drawings a second) while the camera moves on ones (24 fps)
"""
import math
import os

import numpy as np
import skia

W, H = 1080, 1920
CX, CY = W / 2, H / 2
FPS = 24
HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "assets", "fonts")

INK = (22, 10, 34)
PAPER = (255, 247, 232)
WHITE = (255, 255, 255)
MAG = (255, 34, 150)
CYAN = (0, 214, 255)
YEL = (255, 226, 0)
BOXY = (255, 222, 64)            # narration-box yellow
NIGHT = (28, 10, 62)
DUSK = (70, 22, 124)
VIOLET = (136, 52, 226)
RED = (255, 46, 66)
ORANGE = (255, 132, 22)
LIME = (150, 255, 70)
SKIN = (140, 88, 58)

TEXT = []                        # text rectangles drawn this frame, for the collision lint: (x0, y0, x1, y1, tag)


# ------------------------------------------------------------------ basics

_tf = {}


def font(name, size):
    if name not in _tf:
        _tf[name] = skia.Typeface.MakeFromFile(os.path.join(FONTS, name + ".ttf"))
    f = skia.Font(_tf[name], size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    return f


def c4(c, a=1.0):
    return skia.Color4f(c[0] / 255, c[1] / 255, c[2] / 255, a)


def col(c, a=1.0):
    return c4(c, a).toColor()


def paint(c=INK, a=1.0, stroke=0.0, blur=0.0, shader=None, cap="round"):
    p = skia.Paint(AntiAlias=True)
    p.setColor4f(c4(c, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap if cap == "round" else skia.Paint.kButt_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if shader is not None:
        p.setShader(shader)
        p.setAlphaf(a)
    return p


def lin(p0, p1, cols, pos=None):
    return skia.GradientShader.MakeLinear([skia.Point(*p0), skia.Point(*p1)], [col(c[:3], c[3] if len(c) > 3 else 1.0) for c in cols], pos)


def rad(ctr, r, cols, pos=None):
    return skia.GradientShader.MakeRadial(skia.Point(*ctr), r, [col(c[:3], c[3] if len(c) > 3 else 1.0) for c in cols], pos)


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def ramp(t, a, b):
    return min(1.0, max(0.0, (t - a) / max(1e-6, b - a)))


def pop(t, a, dur=0.25, amp=0.35):
    """0 before a, then an overshooting scale-in (1 + amp -> 1), sampled on twos like a drawn pose."""
    t = twos(t) if t >= a else t
    k = ramp(t, a, a + dur)
    if t < a:
        return 0.0
    return 1 + amp * math.sin(k * math.pi) * (1 - k) * 2 if k < 1 else 1.0


def twos(T):
    """Character time: one new drawing every other frame (12 a second)."""
    return math.floor(T * 12 + 1e-6) / 12


def mix(a, b, k):
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def lighter(c, k=0.45):
    return mix(c, WHITE, k)


def darker(c, k=0.55):
    return tuple(int(v * k) for v in c)


def new(color=NIGHT):
    a = np.zeros((H, W, 4), np.uint8)
    a[..., :3] = color
    a[..., 3] = 255
    return a


def surf(arr):
    return skia.Surface(arr)


def path(pts, closed=True):
    p = skia.Path()
    p.moveTo(float(pts[0][0]), float(pts[0][1]))
    for x, y in pts[1:]:
        p.lineTo(float(x), float(y))
    if closed:
        p.close()
    return p


def bez(p0, p1, p2, p3=None, n=24):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2 = (np.array(p, np.float32) for p in (p0, p1, p2))
    if p3 is None:
        return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2
    p3 = np.array(p3, np.float32)
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


def ellipse(cx, cy, rx, ry, n=48, a0=0.0):
    a = np.linspace(a0, a0 + 2 * math.pi, n, endpoint=False)
    return np.stack([cx + rx * np.cos(a), cy + ry * np.sin(a)], 1)


def blob(cx, cy, rx, ry, seed, wob=0.12, n=40):
    """An irregular hand-drawn oval."""
    rng = np.random.default_rng(seed)
    a = np.linspace(0, 2 * math.pi, n, endpoint=False)
    k = 1 + wob * np.convolve(np.r_[rng.normal(0, 1, n), rng.normal(0, 1, 4)], np.ones(5) / 5, "same")[:n]
    return np.stack([cx + rx * k * np.cos(a), cy + ry * k * np.sin(a)], 1)


def reg(x0, y0, x1, y1, tag):
    TEXT.append((float(min(x0, x1)), float(min(y0, y1)), float(max(x0, x1)), float(max(y0, y1)), tag))


def reg_local(c, x0, y0, x1, y1, tag):
    """Register a rect drawn in the canvas' current (rotated/scaled) coordinates, as its screen bounding box."""
    m = c.getTotalMatrix()
    pts = [m.mapXY(x, y) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    reg(min(p.x() for p in pts), min(p.y() for p in pts), max(p.x() for p in pts), max(p.y() for p in pts), tag)


# ------------------------------------------------------------------ print: halftone, hatching, misregistration

_fields = {}


def _field(pitch, angle, kind, shape=(H, W)):
    key = (pitch, angle, kind, shape)
    if key not in _fields:
        y, x = np.mgrid[0:shape[0], 0:shape[1]].astype(np.float32)
        a = math.radians(angle)
        u = x * math.cos(a) + y * math.sin(a)
        v = -x * math.sin(a) + y * math.cos(a)
        if kind == "dot":
            du = np.mod(u, pitch) - pitch / 2
            dv = np.mod(v, pitch) - pitch / 2
            f = np.sqrt(du * du + dv * dv)
        else:
            f = np.abs(np.mod(u, pitch) - pitch / 2)
        _fields[key] = f.astype(np.float32)
    return _fields[key]


def screen(arr, shade, ink, pitch=16, angle=45, kind="dot", roll=(0, 0), amax=1.0):
    """Turn a 0..1 shade map into print: dots (radius ~ sqrt(shade)) or hatch lines (width ~ shade) of `ink`."""
    rows = np.flatnonzero(shade.any(axis=1))
    if not len(rows):
        return
    cols = np.flatnonzero(shade.any(axis=0))
    y0, y1, x0, x1 = rows[0], rows[-1] + 1, cols[0], cols[-1] + 1
    f = _field(pitch, angle, kind, shade.shape[:2])
    if roll != (0, 0):
        f = np.roll(f, (int(roll[1]) % shade.shape[0], int(roll[0]) % shade.shape[1]), axis=(0, 1))
    f = f[y0:y1, x0:x1]
    s = shade[y0:y1, x0:x1].astype(np.float32) / 255.0
    if kind == "dot":
        r = pitch * 0.74 * np.sqrt(s)
        a = np.clip(r - f + 0.5, 0, 1) * (s > 0.02)
    else:
        a = np.clip(pitch * 0.55 * s - f + 0.5, 0, 1) * (s > 0.02)
    a *= amax
    reg_ = arr[y0:y1, x0:x1, :3].astype(np.float32)
    reg_ += (np.array(ink, np.float32) - reg_) * a[..., None]
    arr[y0:y1, x0:x1, :3] = reg_.astype(np.uint8)


def shift(ch, dx, dy):
    out = np.roll(ch, (dy, dx), axis=(0, 1))
    if dx > 0:
        out[:, :dx] = ch[:, :1]
    elif dx < 0:
        out[:, dx:] = ch[:, -1:]
    if dy > 0:
        out[:dy] = out[dy:dy + 1]
    elif dy < 0:
        out[dy:] = out[dy - 1:dy]
    return out


def misregister(arr, d, dy=None):
    """Out-of-focus the comic way: the cyan plate (R channel) and the magenta plate (G) printed off-register."""
    d = int(round(d))
    if d == 0:
        return
    dy = int(round(d * 0.35)) if dy is None else int(dy)
    r, g = arr[..., 0].copy(), arr[..., 1].copy()
    arr[..., 0] = shift(r, d, dy)
    arr[..., 1] = shift(g, -d, -dy)


_GRAIN = None


def grain(arr, amt=5):
    """A fixed newsprint grain (the same every frame, so it costs the encoder nothing)."""
    global _GRAIN
    if _GRAIN is None:
        rng = np.random.default_rng(7)
        g = rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
        g = np.repeat(np.repeat(g, 2, 0), 2, 1)
        _GRAIN = np.clip(g, -2.5, 2.5)[..., None]
    arr[..., :3] = np.clip(arr[..., :3].astype(np.float32) + _GRAIN * amt, 0, 255).astype(np.uint8)


# inks: name -> (colour, pitch, angle, kind)
INKS = {
    "dot": (INK, 16, 45, "dot"),          # shadow dots
    "skin": ((92, 40, 58), 14, 45, "dot"),  # warm shadow dots on skin
    "mag": (MAG, 18, 15, "dot"),          # magenta light / colour dots
    "cyan": (CYAN, 18, 75, "dot"),
    "yel": (YEL, 18, 0, "dot"),
    "hatch": (INK, 12, 35, "line"),       # hatching
    "xhatch": (INK, 12, -35, "line"),     # cross-hatching for the deepest shadows
    "white": (WHITE, 16, 45, "dot"),      # light dots on dark
}


class Stage:
    """One frame: a colour canvas plus shade canvases. Planes are flushed back to front: each flush prints the
    shades as halftone/hatching, then (for far planes) knocks the plates off register."""

    def __init__(self, bg=NIGHT, size=None):
        if size is None:
            self.arr = new(bg)
        else:
            self.arr = np.zeros((size[1], size[0], 4), np.uint8)
            if bg is not None:
                self.arr[..., :3] = bg
                self.arr[..., 3] = 255
        self.s = skia.Surface(self.arr)
        self.c = self.s.getCanvas()
        self.sh = {}
        self.inks = dict(INKS)

    def shade(self, name):
        """The canvas for a shade channel: draw white with alpha = how dark/strong the print should be."""
        if name not in self.sh:
            a = np.zeros(self.arr.shape, np.uint8)
            s = skia.Surface(a)
            self.sh[name] = (a, s, s.getCanvas())
        return self.sh[name][2]

    def pen(self, *names):
        return Pen(self, names or ("dot", "hatch", "mag", "cyan", "skin", "xhatch", "white"))

    def flush(self, misreg=0.0, roll=(0, 0)):
        for name, (a, s, cv) in self.sh.items():
            m = a[..., 3]
            if not m.any():
                continue
            ink, pitch, angle, kind = self.inks[name]
            screen(self.arr, m, ink, pitch, angle, kind, roll)
            a[:] = 0
        if misreg:
            misregister(self.arr, misreg)


CLEAR = skia.Paint(AntiAlias=True)
CLEAR.setBlendMode(skia.BlendMode.kClear)


class Pen:
    """The colour canvas plus shade canvases, moved together (so a character's shading follows its drawing)."""

    def __init__(self, st, names):
        self.c = st.c
        self.sh = {n: st.shade(n) for n in names}

    def __getattr__(self, name):
        sh = self.__dict__.get("sh", {})
        if name in sh:
            return sh[name]
        raise AttributeError(name)

    def all(self):
        return [self.c] + list(self.sh.values())

    def save(self):
        for cv in self.all():
            cv.save()

    def restore(self):
        for cv in self.all():
            cv.restore()

    def translate(self, x, y):
        for cv in self.all():
            cv.translate(x, y)

    def scale(self, sx, sy=None):
        for cv in self.all():
            cv.scale(sx, sx if sy is None else sy)

    def rotate(self, deg):
        for cv in self.all():
            cv.rotate(deg)

    def clip(self, pth):
        for cv in self.all():
            cv.clipPath(pth, doAntiAlias=True)

    def fill(self, pth, color, a=1.0):
        """Paint an opaque shape AND knock out any shading already printed under it (occlusion)."""
        self.c.drawPath(pth, paint(color, a))
        if a >= 0.99:
            for cv in self.sh.values():
                cv.drawPath(pth, CLEAR)

    def fill_rrect(self, rr, color):
        self.c.drawRRect(rr, paint(color))
        for cv in self.sh.values():
            cv.drawRRect(rr, CLEAR)

    def fill_circle(self, x, y, r, color):
        self.c.drawCircle(x, y, r, paint(color))
        for cv in self.sh.values():
            cv.drawCircle(x, y, r, CLEAR)

    def fill_rect(self, rect, color):
        self.c.drawRect(rect, paint(color))
        for cv in self.sh.values():
            cv.drawRect(rect, CLEAR)

    def shadeFill(self, name, pth, a=0.6):
        """Fill `pth` into shade channel `name` (a = print strength)."""
        self.sh[name].drawPath(pth, paint(WHITE, a))


# ------------------------------------------------------------------ ink

def resample(pts, n):
    pts = np.asarray(pts, np.float32)
    seg = np.sqrt(((pts[1:] - pts[:-1]) ** 2).sum(1))
    s = np.r_[0, np.cumsum(seg)]
    if s[-1] < 1e-6:
        return np.repeat(pts[:1], n, 0)
    u = np.linspace(0, s[-1], n)
    return np.stack([np.interp(u, s, pts[:, 0]), np.interp(u, s, pts[:, 1])], 1)


def brush(pts, w, taper=(0.15, 0.15), n=40, prof=None):
    """A tapered brush stroke along a polyline, as a filled path (fat in the middle, pointed at the ends)."""
    p = resample(pts, n)
    d = np.gradient(p, axis=0)
    d /= np.maximum(1e-6, np.sqrt((d ** 2).sum(1)))[:, None]
    nrm = np.stack([-d[:, 1], d[:, 0]], 1)
    t = np.linspace(0, 1, n)
    if prof is None:
        a, b = taper
        prof = np.minimum(np.clip(t / max(a, 1e-3), 0, 1), np.clip((1 - t) / max(b, 1e-3), 0, 1)) ** 0.6
        prof = 0.12 + 0.88 * prof
    hw = (w * prof / 2)[:, None]
    left, right = p + nrm * hw, p - nrm * hw
    return path(np.vstack([left, right[::-1]]))


def ink(c, pts, w=6.0, color=INK, taper=(0.15, 0.15), a=1.0):
    c.drawPath(brush(pts, w, taper), paint(color, a))


def outline(c, pth, w=6.0, color=INK, a=1.0):
    c.drawPath(pth, paint(color, a, stroke=w))


def speed_lines(c, cx, cy, T, n=70, r0=380, r1=1500, color=INK, a=1.0, seed=3, w=10):
    """Focus lines: ink wedges converging on (cx, cy), redrawn on twos."""
    rng = np.random.default_rng(seed + int(twos(T) * 12) % 5)
    pth = skia.Path()
    for i in range(n):
        th = rng.uniform(0, 2 * math.pi)
        rr = r0 * rng.uniform(0.85, 1.4)
        ww = w * rng.uniform(0.4, 1.4) / r1
        p0 = (cx + rr * math.cos(th), cy + rr * math.sin(th))
        pa = (cx + r1 * math.cos(th - ww * 6), cy + r1 * math.sin(th - ww * 6))
        pb = (cx + r1 * math.cos(th + ww * 6), cy + r1 * math.sin(th + ww * 6))
        pth.addPath(path([p0, pa, pb]))
    c.drawPath(pth, paint(color, a))


def motion_lines(c, x0, y0, x1, y1, T, n=18, color=INK, a=1.0, seed=5, w=8, horizontal=True):
    """Parallel speed lines filling a box (horizontal by default), tapered, redrawn on twos."""
    rng = np.random.default_rng(seed + int(twos(T) * 12) % 4)
    for i in range(n):
        if horizontal:
            y = rng.uniform(y0, y1)
            L = rng.uniform(0.25, 0.8) * (x1 - x0)
            xs = rng.uniform(x0, x1 - L)
            ink(c, [(xs, y), (xs + L, y)], w * rng.uniform(0.5, 1.2), color, (0.5, 0.5), a)
        else:
            x = rng.uniform(x0, x1)
            L = rng.uniform(0.25, 0.8) * (y1 - y0)
            ys = rng.uniform(y0, y1 - L)
            ink(c, [(x, ys), (x, ys + L)], w * rng.uniform(0.5, 1.2), color, (0.5, 0.5), a)


# ------------------------------------------------------------------ lettering

def text_path(s, fname, size, tracking=0.0):
    f = font(fname, size)
    g = f.textToGlyphs(s)
    ws = f.getWidths(g)
    p = skia.Path()
    x = 0.0
    for gid, w in zip(g, ws):
        q = f.getPath(gid)
        if q is not None:
            q.offset(x, 0)
            p.addPath(q)
        x += w + tracking
    return p, x - tracking


def dots_in(c, clip_path, bounds, pitch, color, a=1.0, grow=(0.15, 0.55), angle=45):
    """Halftone dots inside a shape, growing down the shape (vector, for lettering and small props)."""
    x0, y0, x1, y1 = bounds
    c.save()
    c.clipPath(clip_path, doAntiAlias=True)
    pth = skia.Path()
    ca, sa = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    R = max(x1 - x0, y1 - y0)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    n = int(R / pitch) + 2
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            x = cx + (i * ca - j * sa) * pitch
            y = cy + (i * sa + j * ca) * pitch
            if x < x0 - pitch or x > x1 + pitch or y < y0 - pitch or y > y1 + pitch:
                continue
            k = (y - y0) / max(1.0, y1 - y0)
            r = pitch * (grow[0] + (grow[1] - grow[0]) * k)
            if r > 0.6:
                pth.addCircle(x, y, r)
    c.drawPath(pth, paint(color, a))
    c.restore()


def sfx(c, s, x, y, size, k=1.0, rot=-8, fill=YEL, fill2=ORANGE, dots=MAG, fname="bangers-400", extrude=(12, 14),
        tag="sfx", tracking=4.0, a=1.0, pen=None):
    """A drawn sound word: extruded ink block letters, gradient fill with halftone dots, fat outline."""
    if k <= 0.01:
        return
    p, w = text_path(s, fname, size, tracking)
    b = p.getBounds()
    if pen is not None:
        bw, bh = (b.width() + extrude[0] + size * 0.3) * k, (b.height() + extrude[1] + size * 0.3) * k
        knockout(pen, skia.Rect.MakeXYWH(x - bw / 2, y - bh / 2, bw, bh), x, y, rot)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(k, k)
    c.translate(-(b.left() + b.right()) / 2, -(b.top() + b.bottom()) / 2)
    ex, ey = extrude
    steps = 8
    for i in range(steps, 0, -1):
        c.save()
        c.translate(ex * i / steps, ey * i / steps)
        c.drawPath(p, paint(INK, a))
        c.drawPath(p, paint(INK, a, stroke=size * 0.1))
        c.restore()
    c.drawPath(p, paint(INK, a, stroke=size * 0.13))
    c.drawPath(p, paint(shader=lin((0, b.top()), (0, b.bottom()), [fill, fill2]), a=a))
    if dots is not None:
        dots_in(c, p, (b.left(), b.top(), b.right(), b.bottom()), max(9.0, size * 0.075), dots, 0.9 * a)
    c.save()
    c.translate(-size * 0.018, -size * 0.022)
    c.drawPath(p, paint(WHITE, 0.55 * a, stroke=size * 0.02))
    c.restore()
    reg_local(c, b.left() - size * 0.07, b.top() - size * 0.07, b.right() + ex + size * 0.07, b.bottom() + ey + size * 0.07, tag)
    c.restore()


def wrap(s, f, maxw):
    words, lines, cur = s.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if f.measureText(t) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def narration(c, s, x, y, maxw=860, size=46, k=1.0, rot=-1.2, fname="comic-neue-700", anchor="center", tag="caption"):
    """A yellow comic narration box, hand-lettered in capitals, with a hard ink drop shadow."""
    if k <= 0.01 or not s:
        return None
    f = font(fname, size)
    lines = wrap(s.upper(), f, maxw - 60)
    lh = size * 1.12
    tw = max(f.measureText(ln) for ln in lines)
    bw, bh = tw + 60, lh * len(lines) + 34
    bx = x - bw / 2 if anchor == "center" else x
    c.save()
    c.translate(bx + bw / 2, y + bh / 2)
    c.rotate(rot)
    c.scale(k, k)
    c.translate(-bw / 2, -bh / 2)
    c.drawRect(skia.Rect.MakeXYWH(10, 12, bw, bh), paint(INK))
    c.drawRect(skia.Rect.MakeXYWH(0, 0, bw, bh), paint(BOXY))
    c.drawRect(skia.Rect.MakeXYWH(0, 0, bw, bh), paint(INK, stroke=5))
    for i, ln in enumerate(lines):
        lw = f.measureText(ln)
        c.drawString(ln, (bw - lw) / 2, 17 + lh * (i + 0.8), f, paint(INK))
    reg_local(c, 0, 0, bw + 10, bh + 12, tag)
    c.restore()
    return (bx, y, bw, bh)


def _bubble_path(x0, y0, w, h, tail, kind):
    cx, cy = x0 + w / 2, y0 + h / 2
    rx, ry = w / 2, h / 2
    if kind == "shout":
        pts = []
        n = 22
        for i in range(n):
            a = 2 * math.pi * i / n
            r = 1.0 if i % 2 == 0 else 1.16
            pts.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)))
        p = path(pts)
    elif kind == "box":
        p = skia.Path()
        p.addRect(skia.Rect.MakeXYWH(x0, y0, w, h))
    else:
        p = skia.Path()
        p.addOval(skia.Rect.MakeXYWH(x0, y0, w, h))
    if tail is not None and kind != "thought":
        tx, ty = tail
        ang = math.atan2(ty - cy, tx - cx)
        # a wedge from the bubble's rim to the speaker
        bxp, byp = cx + rx * 0.72 * math.cos(ang), cy + ry * 0.72 * math.sin(ang)
        perp = ang + math.pi / 2
        wd = min(w, h) * 0.13
        wedge = path([(bxp + wd * math.cos(perp), byp + wd * math.sin(perp)), (tx, ty),
                      (bxp - wd * math.cos(perp), byp - wd * math.sin(perp))])
        p = skia.Op(p, wedge, skia.PathOp.kUnion_PathOp) or p
    return p


def bubble(c, s, cx, cy, tail=None, size=50, maxw=640, k=1.0, kind="speech", fname="comic-neue-700",
           fill=WHITE, text_color=INK, edge=INK, tag="bubble", rot=0.0):
    """Speech (oval), shout (burst), thought (cloud with trailing puffs) or box (noir caption) balloon."""
    if k <= 0.01:
        return None
    f = font(fname, size)
    lines = wrap(s.upper(), f, maxw)
    lh = size * 1.12
    tw = max(f.measureText(ln) for ln in lines)
    padx, pady = (0.62, 0.62) if kind in ("speech", "thought") else (0.4, 0.5)
    w = tw * (1 + padx * (0.9 if len(lines) > 1 else 1.0)) + 50
    h = lh * len(lines) * (1 + pady) + 40
    if kind == "shout":
        w, h = w * 1.18, h * 1.3
    x0, y0 = cx - w / 2, cy - h / 2
    c.save()
    c.translate(cx, cy)
    c.rotate(rot)
    c.scale(k, k)
    c.translate(-cx, -cy)
    ltail = None if tail is None else tail
    if kind == "thought":
        body = skia.Path()
        rng = np.random.default_rng(int(cx + cy) % 997)
        n = 12
        for i in range(n):
            a = 2 * math.pi * i / n
            body.addCircle(cx + w / 2 * 0.86 * math.cos(a), cy + h / 2 * 0.8 * math.sin(a), min(w, h) * rng.uniform(0.2, 0.26))
        body.addOval(skia.Rect.MakeXYWH(x0 + w * 0.08, y0 + h * 0.1, w * 0.84, h * 0.8))
        body = skia.Op(body, skia.Path(), skia.PathOp.kUnion_PathOp) or body
        c.drawPath(body, paint(edge, stroke=12))
        c.drawPath(body, paint(fill))
        if tail is not None:
            tx, ty = tail
            for j, r in enumerate((26, 17, 10)):
                u = 0.45 + 0.2 * j
                c.drawCircle(cx + (tx - cx) * u, cy + h * 0.35 + (ty - cy - h * 0.35) * u, r, paint(fill))
                c.drawCircle(cx + (tx - cx) * u, cy + h * 0.35 + (ty - cy - h * 0.35) * u, r, paint(edge, stroke=6))
    else:
        body = _bubble_path(x0, y0, w, h, ltail, kind)
        c.drawPath(body, paint(INK, 0.9, blur=0) if kind == "box" else paint(edge, stroke=12))
        c.drawPath(body, paint(fill))
        c.drawPath(body, paint(edge, stroke=6))
    for i, ln in enumerate(lines):
        lw = f.measureText(ln)
        c.drawString(ln, cx - lw / 2, cy - lh * len(lines) / 2 + lh * (i + 0.78), f, paint(text_color))
    reg_local(c, cx - tw / 2 - 10, cy - lh * len(lines) / 2 - 6, cx + tw / 2 + 10, cy + lh * len(lines) / 2 + 6, tag)
    c.restore()
    return (x0, y0, w, h)


def knockout(pen, rect, x=0.0, y=0.0, rot=0.0):
    """Clear the shade canvases under a rect (so halftone never prints over lettering)."""
    if pen is None:
        return
    for cv in pen.sh.values():
        cv.save()
        cv.translate(x, y)
        cv.rotate(rot)
        cv.translate(-x, -y)
        cv.drawRect(rect, CLEAR)
        cv.restore()


def label(c, s, x, y, size=40, fname="bangers-400", color=INK, bg=None, align="center", rot=0.0, tag="label",
          pad=14, a=1.0, edge=None, pen=None):
    """Plain lettering (optionally on a plate), registered for the collision lint."""
    f = font(fname, size)
    w = f.measureText(s)
    x0 = x - w / 2 if align == "center" else (x - w if align == "right" else x)
    knockout(pen, skia.Rect.MakeLTRB(x0 - pad, y - size * 0.85 - pad * 0.6, x0 + w + pad, y + size * 0.25 + pad * 0.6), x, y, rot)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.translate(-x, -y)
    if bg is not None:
        c.drawRect(skia.Rect.MakeLTRB(x0 - pad, y - size * 0.82 - pad * 0.6, x0 + w + pad, y + size * 0.2 + pad * 0.6), paint(bg, a))
        if edge is not None:
            c.drawRect(skia.Rect.MakeLTRB(x0 - pad, y - size * 0.82 - pad * 0.6, x0 + w + pad, y + size * 0.2 + pad * 0.6), paint(edge, a, stroke=4))
    c.drawString(s, x0, y, f, paint(color, a))
    reg_local(c, x0, y - size * 0.8, x0 + w, y + size * 0.2, tag)
    c.restore()
    return w


# ------------------------------------------------------------------ comic devices

def spidey(c, cx, cy, r, T, k=1.0, n=9, seed=0, spread=(200, 340)):
    """'Spider-sense': squiggly lines radiating from around a head, inked with coloured cores, wobbling on twos."""
    if k <= 0.01:
        return
    t2 = twos(T)
    rng = np.random.default_rng(seed)
    cols = [MAG, CYAN, YEL]
    for i in range(n):
        a0 = math.radians(spread[0] + (spread[1] - spread[0]) * (i + 0.5) / n + rng.uniform(-6, 6))
        L = r * (0.45 + 0.25 * rng.uniform()) * k
        s = np.linspace(0, 1, 26)
        ph = rng.uniform(0, 6.28) + t2 * 9.0
        rr = r * 1.06 + L * s
        off = 13 * np.sin(2 * math.pi * 2.2 * s + ph) * (0.4 + 0.6 * s)
        xs = cx + rr * np.cos(a0) - off * np.sin(a0)
        ys = cy + rr * np.sin(a0) + off * np.cos(a0)
        pts = np.stack([xs, ys], 1)
        c.drawPath(path(pts, closed=False), paint(INK, stroke=15))
        c.drawPath(path(pts, closed=False), paint(cols[i % 3], stroke=7))


def impact_bg(c, color, cx, cy, T, n=64, r0=260, seed=11, line=INK):
    """An impact frame: flat colour, ink focus lines converging on the hit."""
    c.drawColor(col(color))
    speed_lines(c, cx, cy, T, n=n, r0=r0, r1=1700, color=line, seed=seed, w=26)


def panel_path(quad):
    return path(quad)


def panel_border(c, quad, w=12):
    c.drawPath(path(quad), paint(INK, stroke=w, cap="butt"))


# ------------------------------------------------------------------ graffiti

def spray_stroke(c, pts, w, color, seed=0, a=1.0, overspray=True, prog=1.0):
    """A spray-can line: soft overspray halo, a solid core, a scatter of droplets."""
    pts = np.asarray(pts, np.float32)
    if prog < 1.0:
        n = max(2, int(len(pts) * prog))
        pts = pts[:n]
    if len(pts) < 2:
        return
    p = path(pts, closed=False)
    if overspray:
        c.drawPath(p, paint(color, 0.35 * a, stroke=w * 1.9, blur=w * 0.35))
    c.drawPath(p, paint(color, a, stroke=w))
    rng = np.random.default_rng(seed)
    q = resample(pts, 40)
    dp = skia.Path()
    for x, y in q[::2]:
        for _ in range(4):
            ang = rng.uniform(0, 2 * math.pi)
            rr = w * rng.uniform(0.6, 1.3)
            dp.addCircle(x + rr * math.cos(ang), y + rr * math.sin(ang), rng.uniform(1.2, 3.2))
    c.drawPath(dp, paint(color, 0.8 * a))


def drips(c, x0, x1, y, color, seed=0, n=5, maxlen=70, a=1.0, prog=1.0):
    rng = np.random.default_rng(seed)
    for i in range(n):
        x = rng.uniform(x0, x1)
        L = rng.uniform(0.3, 1.0) * maxlen * prog
        w = rng.uniform(5, 10)
        c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - 4, w, L), w / 2, w / 2, paint(color, a))
        c.drawCircle(x, y + L, w * 0.75, paint(color, a))


def tag_text(c, s, x, y, size, fill=MAG, edge=INK, glow=None, fname="sedgwick-ave-display-400", rot=-6, k=1.0,
             seed=1, drip=True, tag="graffiti", a=1.0, fill2=None, prog=1.0):
    """Graffiti lettering: a fat outline, a two-tone fill, a white highlight, and paint drips."""
    if k <= 0.01:
        return
    p, w = text_path(s, fname, size, tracking=2.0)
    b = p.getBounds()
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(k, k)
    c.translate(-(b.left() + b.right()) / 2, -(b.top() + b.bottom()) / 2)
    if prog < 1.0:
        c.clipRect(skia.Rect.MakeLTRB(b.left() - 40, b.top() - 60, b.left() + (b.width() + 80) * prog, b.bottom() + 200))
    if glow is not None:
        c.drawPath(p, paint(glow, 0.55 * a, stroke=size * 0.3, blur=size * 0.12))
    c.drawPath(p, paint(edge, a, stroke=size * 0.16))
    shader = lin((0, b.top()), (0, b.bottom()), [fill, fill2 or darker(fill, 0.7)])
    c.drawPath(p, paint(shader=shader, a=a))
    c.save()
    c.translate(-size * 0.02, -size * 0.03)
    c.drawPath(p, paint(WHITE, 0.6 * a, stroke=size * 0.025))
    c.restore()
    if drip:
        drips(c, b.left() + 10, b.right() - 10, b.bottom() - size * 0.05, fill2 or darker(fill, 0.7), seed, n=max(3, len(s) // 2),
              maxlen=size * 0.5, a=a)
    reg_local(c, b.left(), b.top(), b.right(), b.bottom(), tag)
    c.restore()


def bricks(c, x0, y0, x1, y1, bw=140, bh=56, col_=(120, 36, 110), mortar=(70, 18, 70), ox=0.0, seed=2):
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(mortar))
    rng = np.random.default_rng(seed)
    r = 0
    y = y0
    while y < y1:
        off = (bw / 2 if r % 2 else 0) - (ox % bw)
        x = x0 + off - bw
        while x < x1:
            k = rng.uniform(-0.12, 0.12)
            cc = tuple(int(max(0, min(255, v * (1 + k)))) for v in col_)
            c.drawRect(skia.Rect.MakeXYWH(x + 4, y + 4, bw - 8, bh - 8), paint(cc))
            x += bw
        y += bh
        r += 1


# ------------------------------------------------------------------ glitch between dimensions

def glitch(a, b, k, seed=0, idx=0):
    """Tear from frame a into frame b: displaced slices, RGB split, shards of the other world, flicker.
    k runs 0..1 over the transition; intensity peaks in the middle."""
    rng = np.random.default_rng(seed * 1000 + idx)
    inten = math.sin(math.pi * min(1.0, max(0.0, k)))
    flick = 0.3 < k < 0.7 and (idx % 2 == 0)
    base = b if (k >= 0.5) != flick else a
    other = a if base is b else b
    out = base.copy()
    # slices of both worlds, displaced
    y = 0
    while y < H:
        hgt = int(rng.integers(18, 150))
        if rng.random() < 0.55 * inten:
            src = other if rng.random() < 0.5 else base
            dx = int(rng.normal(0, 110 * inten))
            out[y:y + hgt] = np.roll(src[y:y + hgt], dx, axis=1)
        y += hgt
    # shards: tinted blocks of the other dimension
    for _ in range(int(3 + 8 * inten)):
        w, h = int(rng.integers(60, 420)), int(rng.integers(30, 220))
        x0, y0 = int(rng.integers(0, W - w)), int(rng.integers(0, H - h))
        blk = other[y0:y0 + h, x0:x0 + w, :3].astype(np.int16)
        tint = [MAG, CYAN, YEL][int(rng.integers(0, 3))]
        mode = rng.random()
        if mode < 0.3:
            blk = 255 - blk
        elif mode < 0.65:
            blk = (blk * 0.5 + np.array(tint) * 0.5)
        out[y0:y0 + h, x0:x0 + w, :3] = np.clip(blk, 0, 255).astype(np.uint8)
    # a mosaic block
    if inten > 0.4:
        w, h = int(rng.integers(160, 480)), int(rng.integers(120, 360))
        x0, y0 = int(rng.integers(0, W - w)), int(rng.integers(0, H - h))
        s = 24
        blk = out[y0:y0 + h, x0:x0 + w, :3]
        small = blk[::s, ::s]
        out[y0:y0 + h, x0:x0 + w, :3] = np.repeat(np.repeat(small, s, 0), s, 1)[:h, :w]
    # RGB split
    d = int(26 * inten)
    if d:
        r, bch = out[..., 0].copy(), out[..., 2].copy()
        out[..., 0] = shift(r, d, 0)
        out[..., 2] = shift(bch, -d, 0)
    # scanlines
    out[::4, :, :3] = (out[::4, :, :3].astype(np.uint16) * 3 // 4).astype(np.uint8)
    return out


def desaturate(arr, k=1.0, contrast=1.15):
    """Drain a region to black and white (the noir dimension)."""
    rgb = arr[..., :3].astype(np.float32)
    y = rgb[..., 0] * 0.3 + rgb[..., 1] * 0.59 + rgb[..., 2] * 0.11
    y = np.clip((y - 128) * contrast + 128, 0, 255)
    arr[..., :3] = (rgb * (1 - k) + y[..., None] * k).astype(np.uint8)


def silhouette(draw, color=INK, rim=None, rim_dx=10):
    """Draw something (draw(P) on a transparent stage) and return it as a flat silhouette layer (RGBA)."""
    st = Stage(None, size=(W, H))
    P = st.pen()
    draw(P)
    a = st.arr[..., 3].astype(np.float32) / 255.0
    out = np.zeros((H, W, 4), np.uint8)
    if rim is not None:
        ar = np.roll(a, rim_dx, axis=1)
        out[..., :3] = rim
        out[..., 3] = (np.clip(ar, 0, 1) * 255).astype(np.uint8)
    lay = np.zeros((H, W, 4), np.float32)
    lay[..., :3] = color
    lay[..., 3] = a
    o = out.astype(np.float32)
    o[..., :3] = o[..., :3] * (1 - a[..., None]) + np.array(color, np.float32) * a[..., None]
    o[..., 3] = np.maximum(o[..., 3], a * 255)
    return o.astype(np.uint8)


def over(dst, lay):
    """Alpha-composite a straight-alpha RGBA layer onto dst (in place)."""
    a = lay[..., 3:4].astype(np.float32) / 255.0
    dst[..., :3] = (dst[..., :3].astype(np.float32) * (1 - a) + lay[..., :3].astype(np.float32) * a).astype(np.uint8)


def page(c, quads, T=None, gutter=PAPER, border=12):
    """A comic page: fill the gutters, then ink each panel's border."""
    for q in quads:
        panel_border(c, q, border)


def star(cx, cy, r, n=5, inner=0.45, rot=-90):
    return path([(cx + r * (1 if i % 2 == 0 else inner) * math.cos(math.radians(rot + i * 180 / n)),
                  cy + r * (1 if i % 2 == 0 else inner) * math.sin(math.radians(rot + i * 180 / n))) for i in range(2 * n)])

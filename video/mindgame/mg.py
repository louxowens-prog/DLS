"""Mind Game toolkit: the look of Masaaki Yuasa's 2004 film, built procedurally.

- boiling hand-drawn lines (every stroke re-wobbles on twos, 12 drawings a second)
- fills printed slightly off the line (misregistration), crayon and halftone textures
- photo-collage cut-outs with torn paper edges
- psychedelic ray bursts, kaleidoscope swirls, fisheye warps, speed lines
- hand lettering that jiggles letter by letter
"""
import math
import os

import numpy as np
import skia
from PIL import Image
from scipy import ndimage

W, H = 1080, 1920
CX, CY = W / 2, H / 2
HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "assets", "fonts")
TEX = os.path.join(HERE, "assets", "tex")
CAP_Y = 1400

INK = (22, 16, 20)
PAPER = (244, 236, 218)
RED = (236, 52, 52)
ORANGE = (255, 140, 30)
YELLOW = (255, 214, 40)
GREEN = (60, 200, 90)
CYAN = (40, 200, 230)
BLUE = (40, 90, 230)
PURPLE = (150, 60, 220)
PINK = (255, 90, 170)
WHITE = (255, 255, 255)
GREY = (140, 140, 150)
PSY = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE, PINK]

_tf = {}


def font(name, size):
    if name not in _tf:
        _tf[name] = skia.Typeface.MakeFromFile(os.path.join(FONTS, name + ".ttf"))
    f = skia.Font(_tf[name], size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    return f


def col4(c, a=1.0):
    return skia.Color4f(c[0] / 255, c[1] / 255, c[2] / 255, a)


def paint(c=INK, a=1.0, stroke=0.0, blur=0.0, shader=None, round_=True):
    p = skia.Paint(AntiAlias=True)
    p.setColor4f(col4(c, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        if round_:
            p.setStrokeCap(skia.Paint.kRound_Cap)
            p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if shader is not None:
        p.setShader(shader)
    return p


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def ramp(t, a, b):
    return min(1.0, max(0.0, (t - a) / max(1e-6, b - a)))


def pop(t, a, dur=0.25):
    """Overshooting scale-in used for stamps and lettering (0 -> 1.25 -> 1)."""
    k = ramp(t, a, a + dur)
    if k <= 0:
        return 0.0
    return 1 + 0.25 * math.sin(k * math.pi) * (1 - k) * 2 if k < 1 else 1.0


def step(T):
    """Animation on twos: drawings change 12 times a second."""
    return int(T * 12)


def new(color=(0, 0, 0)):
    arr = np.zeros((H, W, 4), np.uint8)
    arr[..., :3] = color
    arr[..., 3] = 255
    return arr


def surf(arr):
    return skia.Surface(arr)


# ------------------------------------------------------------------ boiling lines

def resample(pts, spacing=14.0, closed=False):
    pts = np.asarray(pts, np.float32)
    if closed:
        pts = np.vstack([pts, pts[:1]])
    seg = np.sqrt(((pts[1:] - pts[:-1]) ** 2).sum(1))
    L = np.concatenate([[0], np.cumsum(seg)])
    n = max(6, int(L[-1] / spacing) + 1)
    s = np.linspace(0, L[-1], n)
    x = np.interp(s, L, pts[:, 0])
    y = np.interp(s, L, pts[:, 1])
    return np.stack([x, y], 1)


def boil(pts, T, seed=0, amp=2.6, closed=False):
    """Hand-drawn wobble that changes on twos: smooth random offsets along the stroke."""
    p = resample(pts, 12.0, closed)
    rng = np.random.default_rng((seed * 7919 + step(T) * 104729) % (2 ** 32))
    off = rng.normal(0, 1, p.shape)
    k = np.ones(5) / 5
    off[:, 0] = np.convolve(off[:, 0], k, mode="same")
    off[:, 1] = np.convolve(off[:, 1], k, mode="same")
    return p + off * amp * 1.6


def path_of(pts, closed=False):
    p = skia.Path()
    p.moveTo(float(pts[0][0]), float(pts[0][1]))
    for x, y in pts[1:]:
        p.lineTo(float(x), float(y))
    if closed:
        p.close()
    return p


def stroke(c, pts, T, seed=0, width=6.0, color=INK, closed=False, amp=2.6, a=1.0, double=True):
    """A pencil/ink line: a main boiled stroke plus a thin, slightly off second pass."""
    b = boil(pts, T, seed, amp, closed)
    c.drawPath(path_of(b, closed), paint(color, a, stroke=width))
    if double:
        b2 = boil(pts, T, seed + 17, amp * 1.4, closed)
        c.drawPath(path_of(b2, closed), paint(color, a * 0.55, stroke=max(1.2, width * 0.35)))


def fill(c, pts, T, color, seed=0, off=(7, 5), a=1.0, shader=None, amp=2.0):
    """A flat fill printed a little off the line work (misregistration), boiling with the line."""
    b = boil(pts, T, seed + 3, amp, True) + np.array(off, np.float32)
    p = paint(color, a) if shader is None else paint(shader=shader, a=a)
    c.drawPath(path_of(b, True), p)


def circle_pts(cx, cy, r, n=48, rx=None, ry=None, a0=0.0, a1=2 * math.pi):
    rx = rx or r
    ry = ry or r
    ang = np.linspace(a0, a1, n, endpoint=(a1 - a0) < 2 * math.pi - 1e-6)
    return np.stack([cx + rx * np.cos(ang), cy + ry * np.sin(ang)], 1)


def rect_pts(x, y, w, h):
    return np.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]], np.float32)


def bez(p0, p1, p2, p3=None, n=24):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2 = np.array(p0, np.float32), np.array(p1, np.float32), np.array(p2, np.float32)
    if p3 is None:
        return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2
    p3 = np.array(p3, np.float32)
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


# ------------------------------------------------------------------ textures

_cache = {}


def once(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


def _noise(h, w, scale, seed):
    rng = np.random.default_rng(seed)
    g = rng.random((h // scale + 2, w // scale + 2)).astype(np.float32)
    return ndimage.zoom(g, scale, order=3)[:h, :w]


def paper_tex(tone=PAPER, seed=1):
    def mk():
        n = _noise(H, W, 6, seed) * 0.5 + _noise(H, W, 2, seed + 1) * 0.5
        fib = ndimage.gaussian_filter(np.random.default_rng(seed + 2).normal(0, 1, (H, W)).astype(np.float32), (0.6, 4))
        v = (n - 0.5) * 16 + fib * 5
        img = np.clip(np.array(tone, np.float32)[None, None] + v[..., None], 0, 255).astype(np.uint8)
        return img
    return once(("paper", tone, seed), mk)


def paper(arr, tone=PAPER, seed=1):
    arr[..., :3] = paper_tex(tone, seed)


def crayon_shader(color, seed=0, density=0.75, angle=-30):
    """A repeating crayon texture: waxy diagonal strokes with gaps where paper shows through."""
    def mk():
        s = 256
        rng = np.random.default_rng(seed)
        base = rng.random((s, s)).astype(np.float32)
        streak = ndimage.gaussian_filter(base, (0.5, 7))
        streak = ndimage.rotate(streak, angle, reshape=False, mode="wrap")
        m = np.clip((streak - (0.5 - density * 0.12)) * 9, 0, 1)
        img = np.zeros((s, s, 4), np.uint8)
        img[..., :3] = color
        img[..., 3] = (m * 255).astype(np.uint8)
        return skia.Image.fromarray(img, colorType=skia.kRGBA_8888_ColorType)
    im = once(("crayon", color, seed, density, angle), mk)
    return im.makeShader(skia.TileMode.kRepeat, skia.TileMode.kRepeat)


def halftone_shader(color, cell=14, seed=0):
    def mk():
        s = cell * 8
        img = np.zeros((s, s, 4), np.uint8)
        yy, xx = np.mgrid[0:s, 0:s]
        d = np.sqrt(((xx % cell) - cell / 2) ** 2 + ((yy % cell) - cell / 2) ** 2)
        m = d < cell * 0.36
        img[..., :3] = color
        img[..., 3] = (m * 255).astype(np.uint8)
        return skia.Image.fromarray(img, colorType=skia.kRGBA_8888_ColorType)
    im = once(("halftone", color, cell), mk)
    return im.makeShader(skia.TileMode.kRepeat, skia.TileMode.kRepeat)


def photo(name):
    """Photographic texture for collage cut-outs (public-domain Earth imagery and a Moon map)."""
    def mk():
        im = Image.open(os.path.join(TEX, name)).convert("RGB")
        if im.size[0] < 1200:
            im = im.resize((im.size[0] * 4, im.size[1] * 4), Image.LANCZOS)
        a = np.asarray(im)
        rgba = np.dstack([a, np.full(a.shape[:2], 255, np.uint8)])
        return skia.Image.fromarray(np.ascontiguousarray(rgba), colorType=skia.kRGBA_8888_ColorType)
    return once(("photo", name), mk)


def collage(c, name, pts, T, seed=0, src=(0, 0), scale=1.0, border=10):
    """A torn photo cut-out: white paper border, drop shadow, photographic fill."""
    b = boil(pts, T, seed, 1.2, True)
    torn = b + np.random.default_rng(seed).normal(0, 3.0, b.shape)
    pth = path_of(torn, True)
    c.save()
    c.translate(10, 12)
    c.drawPath(pth, paint((0, 0, 0), 0.35, blur=8))
    c.restore()
    c.drawPath(pth, paint(WHITE, 1.0, stroke=border * 2))
    img = photo(name)
    m = skia.Matrix()
    m.setScale(scale, scale)
    m.postTranslate(-src[0] * scale, -src[1] * scale)
    sh = img.makeShader(skia.TileMode.kRepeat, skia.TileMode.kRepeat, skia.SamplingOptions(skia.FilterMode.kLinear), m)
    c.drawPath(pth, paint(shader=sh))


# ------------------------------------------------------------------ psychedelia

_YY, _XX = np.mgrid[0:H, 0:W].astype(np.float32)


def burst(arr, cx, cy, T, colors=PSY, rays=18, spin=0.6, alpha=1.0):
    """Radial ray burst in saturated colours, rotating."""
    ang = np.arctan2(_YY - cy, _XX - cx)
    k = ((ang + T * spin) / (2 * math.pi) * rays) % len(colors)
    idx = k.astype(int) % len(colors)
    pal = np.array(colors, np.uint8)
    img = pal[idx]
    if alpha >= 1:
        arr[..., :3] = img
    else:
        arr[..., :3] = (arr[..., :3] * (1 - alpha) + img * alpha).astype(np.uint8)


def swirl(arr, T, colors=PSY, scale=1.0, cx=CX, cy=CY):
    """Kaleidoscopic plasma, cycling through the palette."""
    x = (_XX - cx) / (220 * scale)
    y = (_YY - cy) / (220 * scale)
    r = np.sqrt(x * x + y * y)
    th = np.arctan2(y, x)
    v = np.sin(r * 3.2 - T * 4) + np.sin(th * 6 + r * 1.5 + T * 2) + np.sin(x * 2 + T * 1.3)
    k = ((v + 3) / 6 * len(colors) * 2 + T * 3) % len(colors)
    i0 = k.astype(int)
    fr = (k - i0)[..., None]
    pal = np.array(colors, np.float32)
    img = pal[i0] * (1 - fr) + pal[(i0 + 1) % len(colors)] * fr
    arr[..., :3] = img.astype(np.uint8)


def speed_lines(c, cx, cy, T, n=60, color=INK, r0=320, seed=0, a=0.9):
    rng = np.random.default_rng(seed * 31 + step(T))
    for _ in range(n):
        ang = rng.uniform(0, 2 * math.pi)
        r1 = r0 + rng.uniform(0, 200)
        r2 = 1400
        w = rng.uniform(2, 10)
        p = skia.Path()
        p.moveTo(cx + r1 * math.cos(ang), cy + r1 * math.sin(ang))
        p.lineTo(cx + r2 * math.cos(ang - 0.01 * w / 4), cy + r2 * math.sin(ang - 0.01 * w / 4))
        p.lineTo(cx + r2 * math.cos(ang + 0.01 * w / 4), cy + r2 * math.sin(ang + 0.01 * w / 4))
        p.close()
        c.drawPath(p, paint(color, a))


_fish = {}


def fisheye(arr, k=0.35, cx=CX, cy=880):
    key = (round(k, 3), cx, cy)
    if key not in _fish:
        x = (_XX - cx) / W
        y = (_YY - cy) / W
        r2 = x * x + y * y
        f = 1 / (1 + k * r2 * 2.5)
        _fish[key] = (np.clip(cy + y * f * W, 0, H - 1).astype(np.float32), np.clip(cx + x * f * W, 0, W - 1).astype(np.float32))
    yy, xx = _fish[key]
    out = arr.copy()
    for ch in range(3):
        out[..., ch] = ndimage.map_coordinates(arr[..., ch], [yy, xx], order=1)
    arr[...] = out


def shake(T, amp=10.0, seed=0):
    rng = np.random.default_rng(seed * 13 + step(T))
    return rng.normal(0, amp), rng.normal(0, amp)


# ------------------------------------------------------------------ lettering

def letters(c, s, x, y, T, size=120, fname="permanent-marker-400", color=WHITE, outline=INK, ow=10.0,
            jig=4.0, rot=5.0, seed=0, align="center", a=1.0, spacing=0.0, scale=1.0):
    """Hand lettering: every character jiggles a little on twos; heavy outline, like a manga sound effect."""
    f = font(fname, size * scale)
    widths = [f.measureText(ch) + spacing * scale for ch in s]
    total = sum(widths)
    x0 = x - total / 2 if align == "center" else (x - total if align == "right" else x)
    rng = np.random.default_rng(seed * 101 + step(T))
    xx = x0
    for ch, w in zip(s, widths):
        dx, dy = rng.normal(0, jig * 0.5), rng.normal(0, jig)
        r = rng.normal(0, rot)
        c.save()
        c.translate(xx + w / 2 + dx, y + dy)
        c.rotate(r)
        if outline is not None and ow > 0:
            po = paint(outline, a, stroke=ow * scale)
            c.drawString(ch, -w / 2 + spacing * scale / 2, 0, f, po)
        c.drawString(ch, -w / 2 + spacing * scale / 2, 0, f, paint(color, a))
        c.restore()
        xx += w
    return total


def text_w(s, size, fname="permanent-marker-400"):
    return font(fname, size).measureText(s)


def note(c, s, x, y, size=34, color=INK, fname="caveat-brush-400", a=1.0, align="center", rot=0.0):
    f = font(fname, size)
    w = f.measureText(s)
    x0 = x - w / 2 if align == "center" else (x - w if align == "right" else x)
    c.save()
    c.translate(x0, y)
    c.rotate(rot)
    c.drawString(s, 0, 0, f, paint(color, a))
    c.restore()
    return w


def stamp(c, s, x, y, T, t0, color=RED, size=84, rot=-8.0, a=1.0, seed=0):
    """A rubber stamp slammed onto the page."""
    k = pop(T, t0, 0.22)
    if k <= 0:
        return
    f = font("bangers-400", size)
    w = f.measureText(s)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(k, k)
    pad = 22
    r = skia.Rect.MakeXYWH(-w / 2 - pad, -size * 0.95, w + 2 * pad, size * 1.25)
    c.drawRoundRect(r, 14, 14, paint(color, 0.95 * a, stroke=8))
    c.drawString(s, -w / 2, 0, f, paint(color, a))
    c.restore()


def label(c, T, t0, lines, x=CX, y=300, color=INK, size=38):
    """Source tag, handwritten on a strip of masking tape."""
    k = ease(ramp(T, t0, t0 + 0.2))
    if k <= 0:
        return
    f = font("rubik-700", size)
    wmax = max(f.measureText(s) for s in lines)
    h = len(lines) * size * 1.25 + 24
    c.save()
    c.translate(x, y)
    c.rotate(-2)
    c.drawRect(skia.Rect.MakeXYWH(-wmax / 2 - 26, -size - 12, wmax + 52, h), paint((250, 240, 190), 0.93 * k))
    for i, s in enumerate(lines):
        c.drawString(s, -f.measureText(s) / 2, i * size * 1.25, f, paint(color, k))
    c.restore()


def tube(c, pts, T, w0, w1, color, seed=0, outline=INK, lw=6.0, amp=2.0):
    """A limb: a filled, tapering tube along a curve, with a boiling ink outline."""
    p = resample(pts, 10.0)
    rng = np.random.default_rng((seed * 7919 + step(T) * 104729) % (2 ** 32))
    p = p + np.convolve(rng.normal(0, 1, len(p) * 2), np.ones(5) / 5, mode="same").reshape(-1, 2)[:len(p)] * amp
    d = np.gradient(p, axis=0)
    nrm = np.stack([-d[:, 1], d[:, 0]], 1)
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-6
    w = np.linspace(w0, w1, len(p))[:, None] / 2
    left, right = p + nrm * w, p - nrm * w
    cap1 = circle_pts(p[-1][0], p[-1][1], w1 / 2, 10, a0=math.atan2(nrm[-1][1], nrm[-1][0]), a1=math.atan2(nrm[-1][1], nrm[-1][0]) - math.pi)
    poly = np.vstack([left, cap1, right[::-1]])
    pth = path_of(poly, True)
    c.drawPath(pth, paint(color))
    c.drawPath(pth, paint(outline, stroke=lw))

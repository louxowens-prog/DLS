"""The factory look, as a toolkit (style only): a 1971 studio musical shot on 35 mm.

Painted flats and obviously handmade sets, warm soft Technicolor-like colour, people drawn like painted actors;
the film itself (grain, halation, gate weave, flicker, dust) is laid on afterwards by film.py.
Everything is drawn with skia into numpy arrays. Coordinates are 1080 x 1920 pixels.
"""
import math
import os

import numpy as np
import skia

W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "assets", "fonts")

# palette: the grey town, the candy wonderland, the film's warm blacks
INK, WHITE, CREAM, PAPER = (34, 22, 16), (255, 255, 255), (252, 242, 218), (240, 230, 205)
SOOT, SLATE, ASH, FOG, BRICK = (58, 54, 52), (96, 98, 102), (140, 138, 132), (178, 176, 170), (120, 78, 62)
GOLD, GOLD2, GOLD3 = (238, 190, 60), (255, 226, 120), (170, 118, 30)
CHOC, CHOC2, CARAMEL = (92, 52, 30), (130, 78, 44), (200, 132, 60)
MINT, PINK, LEMON, LILAC, SKYB, PEACH = (150, 230, 190), (255, 160, 196), (255, 232, 110), (196, 160, 240), (140, 200, 255), (255, 196, 150)
CHERRY, TEAL, MUSTARD, PLUM, GRASS = (214, 40, 60), (20, 110, 118), (214, 160, 40), (110, 40, 90), (110, 190, 80)
SKIN, SKIN2 = (240, 196, 160), (196, 140, 110)
BLOOD = (170, 20, 30)

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


def wrap_balanced(s, f, maxw):
    """Two even lines rather than a long one and an orphan; a no-break space (\u00a0) never splits."""
    words = s.split(" ")
    fix = lambda ls: [x.replace("\u00a0", " ") for x in ls]
    if f.measureText(s) <= maxw:
        return fix([s])
    best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        wa, wb = f.measureText(a), f.measureText(b)
        if wa > maxw or wb > maxw:
            continue
        cost = max(wa, wb) + (400 if i == len(words) - 1 or i == 1 else 0)
        if best is None or cost < best[0]:
            best = (cost, [a, b])
    return fix(best[1]) if best else fix(wrap(s, f, maxw))


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


def text(c, s, x, y, size, fname="fraunces-900", color=WHITE, align="center", tag="label", a=1.0, outline=None, ow=10,
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


# ------------------------------------------------------------------ painted matter

def shade(c, p, color, light=(-0.45, -0.7), k=0.28, edge=0.45, a=1.0):
    """Fill a path like painted volume: lit from the upper left, a darker far side, a soft brown contour."""
    b = p.computeTightBounds()
    cx, cy = b.centerX(), b.centerY()
    rw, rh = max(2.0, b.width() / 2), max(2.0, b.height() / 2)
    hi, lo = mix(color, WHITE, k * 0.9), mix(color, INK, k * 1.2)
    c.drawPath(p, paint(shader=rad((cx + light[0] * rw * 0.6, cy + light[1] * rh * 0.6), max(rw, rh) * 1.5,
                                   [hi, color, lo], [0.0, 0.5, 1.0]), a=a))
    if edge > 0:
        c.drawPath(p, paint(mix(color, INK, 0.6), edge * a, stroke=2.2))
    return p


def rrect(x0, y0, x1, y1, r):
    p = skia.Path()
    p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x0, y0, x1, y1), r, r))
    return p


def oval(x0, y0, x1, y1):
    p = skia.Path()
    p.addOval(skia.Rect.MakeLTRB(x0, y0, x1, y1))
    return p


def circle(x, y, r):
    return oval(x - r, y - r, x + r, y + r)


def capsule(x0, y0, x1, y1, w0, w1=None):
    """A tapered limb from (x0, y0) to (x1, y1), w0 wide at the start, w1 at the end."""
    w1 = w0 if w1 is None else w1
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) + 1e-6
    nx, ny = -dy / L, dx / L
    p = skia.Path()
    p.moveTo(x0 + nx * w0 / 2, y0 + ny * w0 / 2)
    p.lineTo(x1 + nx * w1 / 2, y1 + ny * w1 / 2)
    a1 = math.degrees(math.atan2(ny, nx))
    p.arcTo(skia.Rect.MakeLTRB(x1 - w1 / 2, y1 - w1 / 2, x1 + w1 / 2, y1 + w1 / 2), a1, -180, False)
    p.lineTo(x0 - nx * w0 / 2, y0 - ny * w0 / 2)
    p.arcTo(skia.Rect.MakeLTRB(x0 - w0 / 2, y0 - w0 / 2, x0 + w0 / 2, y0 + w0 / 2), a1 + 180, -180, False)
    p.close()
    return p


def brush_tex(w, h, seed=0, streak=24, amp=0.14):
    """Streaky scenic-paint texture as a multiplier image (mean 1): the brush marks on a painted flat."""
    def make():
        from PIL import Image, ImageFilter
        rng = np.random.default_rng(seed)
        n = rng.normal(0, 1, (h // 4, w // 4)).astype(np.float32)
        im = Image.fromarray(((n - n.min()) / (np.ptp(n) + 1e-6) * 255).astype(np.uint8))
        im = im.resize((w, h), Image.BICUBIC).filter(ImageFilter.BoxBlur(2))
        a = np.asarray(im, np.float32) / 255 - 0.5
        k = np.ones(streak, np.float32) / streak
        a = np.apply_along_axis(lambda r: np.convolve(r, k, "same"), 1, a)
        canvas = rng.normal(0, 1, (h // 2, w // 2)).astype(np.float32)          # the weave of the scenic canvas
        cv = np.asarray(Image.fromarray(((canvas - canvas.min()) / (np.ptp(canvas) + 1e-6) * 255).astype(np.uint8)).resize((w, h), Image.NEAREST),
                        np.float32) / 255 - 0.5
        return 1 + amp * a / (np.abs(a).max() + 1e-6) + 0.05 * cv
    return cached(f"brush{w}x{h}s{seed}", make)


def apply_tex(arr, tex, y0=0, x0=0):
    h, w = tex.shape
    sub = arr[y0:y0 + h, x0:x0 + w, :3].astype(np.float32)
    arr[y0:y0 + h, x0:x0 + w, :3] = np.clip(sub * tex[: sub.shape[0], : sub.shape[1], None], 0, 255).astype(np.uint8)


def backdrop(st, name, fn):
    """A painted flat, drawn once and reused (fn(c) paints a full frame)."""
    def make():
        s = Stage()
        fn(s.c)
        apply_tex(s.arr, brush_tex(W, H, seed=len(name)))
        return image(s.arr)
    st.c.drawImage(cached("bd_" + name, make), 0, 0)


def label(c, s, x, y, size, fname="fraunces-900", color=CREAM, tag="label", a=1.0, outline=INK, ow=None, align="center"):
    return text(c, s, x, y, size, fname, color, align=align, tag=tag, a=a, outline=outline, ow=ow if ow is not None else size * 0.16)

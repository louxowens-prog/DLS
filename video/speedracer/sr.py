"""Speed Racer toolkit: the look of the Wachowskis' 2008 film, built procedurally.

- candy palette, glossy toy-plastic shading (gradient body, specular streak, coloured rim light)
- bloom and lens flares (anamorphic streaks, ghosts), sparkle glints
- horizontal streak motion blur behind sharp foreground subjects; anime speed lines
- the editing grammar: head wipes, iris wipes, split screens, broadcast picture-in-picture, lower thirds
- retro race lettering with chrome bevels
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
CAP_Y = 1400

INK = (24, 12, 48)
WHITE = (255, 255, 255)
PINK = (255, 45, 160)
CYAN = (0, 225, 255)
LEMON = (255, 238, 40)
LIME = (110, 255, 70)
TANG = (255, 135, 0)
VIOLET = (150, 60, 255)
RED = (255, 35, 60)
BLUE = (40, 110, 255)
CANDY = [PINK, TANG, LEMON, LIME, CYAN, BLUE, VIOLET]

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


def paint(c=INK, a=1.0, stroke=0.0, blur=0.0, shader=None):
    p = skia.Paint(AntiAlias=True)
    p.setColor4f(c4(c, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if shader is not None:
        p.setShader(shader)
        p.setAlphaf(a)
    return p


def lin(p0, p1, cols, pos=None):
    return skia.GradientShader.MakeLinear([skia.Point(*p0), skia.Point(*p1)], [col(c) if len(c) == 3 else c4(c[:3], c[3]).toColor() for c in cols], pos)


def rad(ctr, r, cols, pos=None):
    return skia.GradientShader.MakeRadial(skia.Point(*ctr), r, [col(c) if len(c) == 3 else c4(c[:3], c[3]).toColor() for c in cols], pos)


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def ramp(t, a, b):
    return min(1.0, max(0.0, (t - a) / max(1e-6, b - a)))


def pop(t, a, dur=0.22):
    k = ramp(t, a, a + dur)
    if k <= 0:
        return 0.0
    return 1 + 0.3 * math.sin(k * math.pi) * (1 - k) * 2 if k < 1 else 1.0


def lighter(c, k=0.45):
    return tuple(int(v + (255 - v) * k) for v in c)


def darker(c, k=0.55):
    return tuple(int(v * k) for v in c)


def new(color=(0, 0, 0)):
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


def ellipse(cx, cy, rx, ry, n=48):
    a = np.linspace(0, 2 * math.pi, n, endpoint=False)
    return np.stack([cx + rx * np.cos(a), cy + ry * np.sin(a)], 1)


# ------------------------------------------------------------------ glossy toy plastic

def glossy(c, pth, base, top=None, rim=None, spec=0.85, ink=True, lw=5.0):
    """Toy-plastic fill: a vertical gradient, a soft specular streak across the upper third, a coloured rim light."""
    b = pth.computeTightBounds()
    x0, y0, x1, y1 = b.left(), b.top(), b.right(), b.bottom()
    hgt = max(1.0, y1 - y0)
    top = top or lighter(base, 0.5)
    c.drawPath(pth, paint(shader=lin((0, y0), (0, y1), [top, base, darker(base, 0.6)], [0, 0.55, 1])))
    c.save()
    c.clipPath(pth, doAntiAlias=True)
    if rim is not None:
        c.drawPath(pth, paint(rim, 0.9, stroke=hgt * 0.12, blur=hgt * 0.04))
    if spec > 0:
        r = skia.Rect.MakeLTRB(x0 + (x1 - x0) * 0.1, y0 + hgt * 0.08, x1 - (x1 - x0) * 0.2, y0 + hgt * 0.28)
        c.drawRRect(skia.RRect.MakeRectXY(r, hgt * 0.1, hgt * 0.1), paint(WHITE, spec * 0.75, blur=hgt * 0.03))
    c.restore()
    if ink:
        c.drawPath(pth, paint(INK, stroke=lw))


def glint(c, x, y, r, T=0.0, a=1.0):
    """A four-point sparkle."""
    k = 0.7 + 0.3 * math.sin(T * 9 + x)
    for ang, L in ((0, 1.0), (90, 1.0), (45, 0.45), (135, 0.45)):
        c.save()
        c.translate(x, y)
        c.rotate(ang)
        p = path([(-r * L * k, 0), (0, -r * 0.08), (r * L * k, 0), (0, r * 0.08)])
        c.drawPath(p, paint(WHITE, a))
        c.restore()
    c.drawCircle(x, y, r * 0.18, paint(WHITE, a, blur=r * 0.1))


# ------------------------------------------------------------------ light

def bloom(arr, strength=0.6, thresh=170, radius=18):
    small = arr[::4, ::4, :3].astype(np.float32)
    lum = small.mean(-1, keepdims=True)
    bright = small * np.clip((lum - thresh) / (255 - thresh), 0, 1)
    glow = ndimage.gaussian_filter(bright, (radius / 4, radius / 4, 0))
    glow = np.asarray(Image.fromarray(np.clip(glow, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)).astype(np.float32)
    base = arr[..., :3].astype(np.float32)
    arr[..., :3] = np.clip(255 - (255 - base) * (255 - glow * strength) / 255, 0, 255).astype(np.uint8)


def flare(c, x, y, s=1.0, T=0.0, tint=CYAN, a=1.0):
    """Lens flare: hot core, anamorphic streak, ghosts along the line through the frame centre."""
    c.drawCircle(x, y, 120 * s, paint(shader=rad((x, y), 120 * s, [(255, 255, 255, 0.9 * a), (*tint, 0.35 * a), (*tint, 0.0)], [0, 0.35, 1])))
    c.drawOval(skia.Rect.MakeXYWH(x - 520 * s, y - 7 * s, 1040 * s, 14 * s), paint(lighter(tint, 0.6), 0.75 * a, blur=5 * s))
    c.drawOval(skia.Rect.MakeXYWH(x - 260 * s, y - 3 * s, 520 * s, 6 * s), paint(WHITE, 0.9 * a, blur=2 * s))
    dx, dy = CX - x, 880 - y
    for k, (f, r, cc) in enumerate(((0.5, 38, PINK), (0.9, 22, LEMON), (1.3, 60, CYAN), (1.7, 28, VIOLET))):
        gx, gy = x + dx * f * 2, y + dy * f * 2
        hexp = [(gx + r * s * math.cos(i / 6 * 2 * math.pi + 0.3), gy + r * s * math.sin(i / 6 * 2 * math.pi + 0.3)) for i in range(6)]
        c.drawPath(path(hexp), paint(cc, 0.22 * a, blur=2))


# ------------------------------------------------------------------ motion

def streak(arr, amount=90, y0=0, y1=H, direction=1):
    """Horizontal motion blur of a band of the frame (the background rushing past)."""
    if amount < 2:
        return
    band = arr[y0:y1, :, :3].astype(np.float32)
    band = ndimage.uniform_filter1d(band, size=int(amount), axis=1, mode="wrap")
    band = ndimage.uniform_filter1d(band, size=max(1, int(amount / 3)), axis=1, mode="wrap")
    arr[y0:y1, :, :3] = band.astype(np.uint8)


def speed_lines(c, cx, cy, T, n=60, color=WHITE, r0=380, a=0.85, seed=0, width=(2, 12)):
    rng = np.random.default_rng(seed * 31 + int(T * 24))
    for _ in range(n):
        ang = rng.uniform(0, 2 * math.pi)
        r1 = r0 + rng.uniform(0, 220)
        w = rng.uniform(*width)
        p = skia.Path()
        p.moveTo(cx + r1 * math.cos(ang), cy + r1 * math.sin(ang))
        p.lineTo(cx + 1800 * math.cos(ang - w / 1800), cy + 1800 * math.sin(ang - w / 1800))
        p.lineTo(cx + 1800 * math.cos(ang + w / 1800), cy + 1800 * math.sin(ang + w / 1800))
        p.close()
        c.drawPath(p, paint(color, a))


def hlines(c, T, y0, y1, n=30, color=WHITE, a=0.8, seed=0, speed=3000):
    """Anime horizontal speed lines racing across a band."""
    rng = np.random.default_rng(seed)
    for i in range(n):
        y = rng.uniform(y0, y1)
        L = rng.uniform(120, 520)
        x = (rng.uniform(0, W + L) - T * speed * rng.uniform(0.7, 1.3)) % (W + L * 2) - L
        c.drawRect(skia.Rect.MakeXYWH(x, y, L, rng.uniform(2, 7)), paint(color, a))


# ------------------------------------------------------------------ backdrops

def sky(arr, stops, T=0.0, sun=None):
    ys = np.linspace(0, 1, H)
    g = np.stack([np.interp(ys, [s[0] for s in stops], [s[1][ch] for s in stops]) for ch in range(3)], -1)
    arr[..., :3] = g[:, None, :].astype(np.uint8)
    if sun:
        sf = surf(arr)
        with sf as c:
            x, y, r = sun
            c.drawCircle(x, y, r * 2.4, paint(shader=rad((x, y), r * 2.4, [(255, 250, 220, 0.9), (255, 200, 120, 0.25), (255, 150, 150, 0.0)], [0, 0.4, 1])))
            c.drawCircle(x, y, r, paint((255, 250, 230)))


def rainbow_bands(c, pts_left, pts_right, cols=CANDY):
    """Fill a road strip between two edge polylines with parallel candy bands."""
    n = len(cols)
    L, R = np.asarray(pts_left, np.float32), np.asarray(pts_right, np.float32)
    for i, cc in enumerate(cols):
        a, b = i / n, (i + 1) / n
        e0, e1 = L + (R - L) * a, L + (R - L) * b
        c.drawPath(path(np.vstack([e0, e1[::-1]])), paint(cc))


def checker(c, x, y, w, h, n=8, m=2, c1=WHITE, c2=INK):
    cw, ch = w / n, h / m
    for i in range(n):
        for j in range(m):
            c.drawRect(skia.Rect.MakeXYWH(x + i * cw, y + j * ch, cw + 0.5, ch + 0.5), paint(c1 if (i + j) % 2 == 0 else c2))


# ------------------------------------------------------------------ lettering

def race_text(c, s, x, y, size, fill=LEMON, fname="racing-sans-one-400", outline=INK, ow=None, align="center", a=1.0,
              skew=-0.18, shadow=True, grad=True, scale=1.0, spacing=0.0):
    """Retro race lettering: italic skew, gradient chrome fill, heavy outline, hard drop shadow."""
    f = font(fname, size * scale)
    sp = spacing * scale
    wid = sum(f.measureText(ch) for ch in s) + sp * (len(s) - 1)
    x0 = x - wid / 2 if align == "center" else (x - wid if align == "right" else x)
    ow = ow if ow is not None else size * scale * 0.12
    c.save()
    c.translate(x0, y)
    c.skew(skew, 0)

    def run(p, dx=0, dy=0):
        xx = dx
        for ch in s:
            c.drawString(ch, xx, dy, f, p)
            xx += f.measureText(ch) + sp
    if shadow:
        run(paint(INK, 0.9 * a), size * scale * 0.06, size * scale * 0.07)
    if outline is not None:
        run(paint(outline, a, stroke=ow))
    if grad:
        sh = lin((0, -size * scale * 0.8), (0, size * scale * 0.1), [lighter(fill, 0.75), fill, darker(fill, 0.75)], [0, 0.5, 1])
        run(paint(shader=sh, a=a))
    else:
        run(paint(fill, a))
    c.restore()
    return wid


def text_w(s, size, fname="racing-sans-one-400"):
    return font(fname, size).measureText(s)


def plain(c, s, x, y, size, color=WHITE, fname="rubik-800", align="center", a=1.0):
    f = font(fname, size)
    w = f.measureText(s)
    x0 = x - w / 2 if align == "center" else (x - w if align == "right" else x)
    c.drawString(s, x0, y, f, paint(color, a))
    return w


def badge(c, s, x, y, T, t0, color=RED, size=64, rot=-6, fname="bungee-400", a=1.0):
    """A glossy broadcast badge slammed on screen."""
    k = pop(T, t0, 0.22)
    if k <= 0:
        return
    f = font(fname, size)
    w = f.measureText(s)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(k, k)
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w / 2 - 28, -size * 0.95, w + 56, size * 1.3), 18, 18)
    c.drawRRect(r.makeOffset(8, 10), paint(INK, 0.8 * a))
    pth = skia.Path()
    pth.addRRect(r)
    glossy(c, pth, color, rim=lighter(color, 0.7), lw=6)
    c.drawString(s, -w / 2, 0, f, paint(WHITE, a))
    c.restore()


def lower_third(c, T, t0, t1, title, sub=None, color=PINK, y=1180):
    """Broadcast lower-third: slides in from the left, out to the right."""
    k_in = ease(ramp(T, t0, t0 + 0.25))
    k_out = ease(ramp(T, t1 - 0.25, t1))
    if k_in <= 0 or k_out >= 1:
        return
    x = -900 * (1 - k_in) + 1200 * k_out
    f = font("bungee-400", 50)
    w = max(f.measureText(title), font("rubik-800", 34).measureText(sub or "")) + 80
    c.save()
    c.translate(x, 0)
    bar = skia.Path()
    bar.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(60, y - 70, w, 96), 14, 14))
    glossy(c, bar, color, rim=lighter(color, 0.7), lw=5)
    c.drawString(title, 100, y - 4, f, paint(WHITE))
    if sub:
        sb = skia.Path()
        sb.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(90, y + 30, w - 30, 58), 10, 10))
        glossy(c, sb, WHITE, top=WHITE, spec=0.2, lw=4)
        c.drawString(sub, 120, y + 72, font("rubik-800", 34), paint(INK))
    c.restore()


def tv_frame(c, x, y, w, h, T, label="LIVE", color=PINK):
    """Chrome picture-in-picture frame with a LIVE bug."""
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), 22, 22)
    c.drawRRect(r.makeOffset(10, 12), paint(INK, 0.6, blur=6))
    p = skia.Path()
    p.addRRect(r)
    c.drawPath(p, paint(shader=lin((x, y), (x, y + h), [(250, 250, 255), (150, 160, 190), (230, 235, 250)]), stroke=18))
    c.drawPath(p, paint(INK, stroke=4))
    bug = skia.Path()
    bug.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x + 22, y + 22, 120, 46), 10, 10))
    glossy(c, bug, RED if int(T * 2) % 2 else darker(RED, 0.8), lw=3)
    c.drawString(label, x + 36, y + 58, font("bungee-400", 30), paint(WHITE))

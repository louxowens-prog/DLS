"""Drawing helpers: skia for crisp vector work and type, numpy for light (stars, planets, glows, film)."""
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

# Reels UI covers roughly the top 220 px and the bottom 380 px (and a strip on the right).
SAFE_TOP, SAFE_BOT = 250, 1540
CAP_Y = 1395

_tf = {}


def font(name, size):
    if name not in _tf:
        _tf[name] = skia.Typeface.MakeFromFile(os.path.join(FONTS, name + ".ttf"))
    f = skia.Font(_tf[name], size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    f.setSubpixel(True)
    return f


def rgba(c, a=1.0):
    r, g, b = c[:3]
    return skia.Color4f(r / 255, g / 255, b / 255, a)


WHITE = (255, 255, 255)
HAL = (255, 36, 18)
AMBER = (255, 170, 60)
CYAN = (90, 190, 255)
BLUE = (40, 110, 255)
GREEN = (90, 255, 150)
GREY = (150, 156, 165)
DIM = (70, 76, 86)


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def ramp(t, a, b):
    return min(1.0, max(0.0, (t - a) / max(1e-6, b - a)))


def new():
    arr = np.zeros((H, W, 4), np.uint8)
    arr[..., 3] = 255
    return arr


def canvas_of(arr):
    return skia.Surface(arr)


def paint(color=WHITE, a=1.0, stroke=0, blur=0, aa=True, cap_round=True, shader=None, blend=None):
    p = skia.Paint(AntiAlias=aa)
    p.setColor4f(rgba(color, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        if cap_round:
            p.setStrokeCap(skia.Paint.kRound_Cap)
            p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if shader is not None:
        p.setShader(shader)
    if blend is not None:
        p.setBlendMode(blend)
    return p


def text_width(s, f, track=0.0):
    return f.measureText(s) + track * max(0, len(s) - 1)


def text(c, s, x, y, f, color=WHITE, a=1.0, align="center", track=0.0, glow=0.0, glow_color=None):
    """Draw text with optional letter-spacing (track, px) and glow. y is the baseline."""
    if not s or a <= 0.003:
        return
    w = text_width(s, f, track)
    x0 = x - w / 2 if align == "center" else (x - w if align == "right" else x)
    passes = []
    if glow:
        passes.append(paint(glow_color or color, a * 0.8, blur=glow))
    passes.append(paint(color, a))
    for p in passes:
        if track == 0:
            c.drawString(s, x0, y, f, p)
        else:
            xx = x0
            for ch in s:
                c.drawString(ch, xx, y, f, p)
                xx += f.measureText(ch) + track
    return w


def wrap(s, f, maxw, track=0.0):
    words, lines, cur = s.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if text_width(test, f, track) <= maxw or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def image(c, arr, x=0, y=0, a=1.0, w=None, h=None, blend=None):
    """Draw an RGB/RGBA uint8 numpy image."""
    if arr.shape[2] == 3:
        arr = np.dstack([arr, np.full(arr.shape[:2], 255, np.uint8)])
    img = skia.Image.fromarray(np.ascontiguousarray(arr), colorType=skia.kRGBA_8888_ColorType)
    p = skia.Paint(AntiAlias=True)
    p.setAlphaf(a)
    if blend is not None:
        p.setBlendMode(blend)
    if w is None:
        c.drawImage(img, x, y, skia.SamplingOptions(skia.FilterMode.kLinear), p)
    else:
        c.drawImageRect(img, skia.Rect.MakeXYWH(x, y, w, h), skia.SamplingOptions(skia.FilterMode.kLinear), p)


# ------------------------------------------------------------------ light, in numpy (float RGB 0..1+)

def add_light(arr, light, a=1.0):
    """Additively composite a float HxWx3 light buffer onto the uint8 frame."""
    base = arr[..., :3].astype(np.float32) / 255
    out = base + light * a
    arr[..., :3] = (np.clip(out, 0, 1) * 255).astype(np.uint8)


def over(arr, rgb, alpha, x0=0, y0=0):
    """Alpha-composite float rgb (h,w,3) with alpha (h,w) at (x0,y0)."""
    h, w = alpha.shape
    xa, ya = max(0, x0), max(0, y0)
    xb, yb = min(W, x0 + w), min(H, y0 + h)
    if xb <= xa or yb <= ya:
        return
    sub = arr[ya:yb, xa:xb, :3].astype(np.float32) / 255
    al = alpha[ya - y0: yb - y0, xa - x0: xb - x0, None]
    col = rgb[ya - y0: yb - y0, xa - x0: xb - x0]
    arr[ya:yb, xa:xb, :3] = (np.clip(sub * (1 - al) + col * al, 0, 1) * 255).astype(np.uint8)


_YY, _XX = np.mgrid[0:H, 0:W].astype(np.float32)


def radial(cx, cy, sigma, color, gain=1.0, power=2.0):
    d = np.sqrt((_XX - cx) ** 2 + (_YY - cy) ** 2) / sigma
    v = np.exp(-(d ** power)) * gain
    return v[..., None] * (np.array(color, np.float32) / 255)[None, None]


# ------------------------------------------------------------------ stars

def _make_stars(w, h, n, seed):
    rng = np.random.default_rng(seed)
    s = np.zeros((h, w), np.float32)
    xs, ys = rng.integers(0, w, n), rng.integers(0, h, n)
    mag = rng.power(0.35, n)
    b = 0.12 + 0.88 * mag
    np.add.at(s, (ys, xs), b)
    big = mag > 0.93
    for x, y, m in zip(xs[big], ys[big], mag[big]):
        for dx, dy, g in ((1, 0, .45), (-1, 0, .45), (0, 1, .45), (0, -1, .45), (1, 1, .15), (-1, -1, .15), (1, -1, .15), (-1, 1, .15)):
            if 0 <= x + dx < w and 0 <= y + dy < h:
                s[y + dy, x + dx] += g * m
    tint = np.ones((h, w, 3), np.float32)
    temp = rng.uniform(-1, 1, n)
    for arr_c, k in ((0, 0.10), (2, -0.10)):
        t = np.zeros((h, w), np.float32)
        np.add.at(t, (ys, xs), temp * k)
        tint[..., arr_c] += t
    return np.clip(s, 0, 1.2)[..., None] * tint


STARS = _make_stars(W + 400, H + 400, 1500, 7)


def stars(arr, dx=0.0, dy=0.0, a=1.0, zoom=1.0):
    ox, oy = int(200 + dx) % 400, int(200 + dy) % 400
    crop = STARS[oy: oy + H, ox: ox + W]
    if zoom != 1.0:
        crop = ndimage.zoom(crop, (zoom, zoom, 1), order=1)[:H, :W]
    add_light(arr, crop, a)


# ------------------------------------------------------------------ noise & planets

def fbm(h, w, octaves=6, seed=0, base=4, persistence=0.55, aspect=1.0):
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        gh = max(2, int(base * 2 ** o))
        gw = max(2, int(base * 2 ** o * aspect * w / h))
        g = rng.random((gh + 1, gw + 1)).astype(np.float32)
        z = ndimage.zoom(g, ((h + gh) / (gh + 1), (w + gw) / (gw + 1)), order=3)[:h, :w]
        out += amp * z
        tot += amp
        amp *= persistence
    out /= tot
    return (out - out.min()) / (out.max() - out.min() + 1e-9)


_tex = {}


def earth_tex():
    if "earth" in _tex:
        return _tex["earth"]
    img = np.asarray(Image.open(os.path.join(TEX, "earth_ne2.jpg")).convert("RGB")).astype(np.float32) / 255
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    ocean = np.clip((b - np.maximum(r, g) + 0.02) * 6, 0, 1)
    ice = np.clip((np.minimum(np.minimum(r, g), b) - 0.72) * 5, 0, 1)
    land = img * np.array([0.78, 0.74, 0.62])
    grey = land.mean(-1, keepdims=True)
    land = grey + (land - grey) * 0.55
    sea = np.stack([0.02 + 0.10 * b, 0.07 + 0.16 * b, 0.20 + 0.30 * b], -1)
    col = land * (1 - ocean[..., None]) + sea * ocean[..., None]
    col = col * (1 - ice[..., None]) + np.array([0.9, 0.93, 0.97]) * ice[..., None]
    h, w = col.shape[:2]
    cl = fbm(h, w, octaves=7, seed=11, base=7, aspect=1.0, persistence=0.62)
    cl2 = fbm(h, w, octaves=5, seed=12, base=14, aspect=1.0, persistence=0.5)
    lat = np.abs(np.linspace(-1, 1, h))[:, None]
    band = 0.10 * np.cos(lat * np.pi * 3) + 0.02
    clouds = np.clip((cl * 0.7 + cl2 * 0.3 + band - 0.56) * 3.6, 0, 1) ** 1.3 * 0.92
    polar = np.clip(np.cos(np.linspace(-np.pi / 2, np.pi / 2, h)) * 2.2, 0, 1)[:, None]
    clouds = clouds * polar                     # no pinched streaks at the poles
    _tex["earth"] = (col.astype(np.float32), clouds.astype(np.float32))
    return _tex["earth"]


def moon_tex(h=1024, w=2048):
    if "moon" in _tex:
        return _tex["moon"]
    rng = np.random.default_rng(5)
    base = fbm(h, w, octaves=7, seed=21, base=3)
    maria = np.clip((fbm(h, w, octaves=4, seed=22, base=2) - 0.55) * 4, 0, 1)
    height = base * 0.3
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    for _ in range(260):
        cx, cy = rng.uniform(0, w), rng.uniform(h * 0.1, h * 0.9)
        r = rng.pareto(2.2) * 6 + 3
        r = min(r, 120)
        x0, x1 = int(max(0, cx - 2 * r)), int(min(w, cx + 2 * r))
        y0, y1 = int(max(0, cy - 2 * r)), int(min(h, cy + 2 * r))
        d = np.sqrt((xx[y0:y1, x0:x1] - cx) ** 2 + (yy[y0:y1, x0:x1] - cy) ** 2) / r
        crater = np.where(d < 1, (d ** 2 - 1) * 0.8, 0.25 * np.exp(-((d - 1) / 0.25) ** 2))
        height[y0:y1, x0:x1] += crater * r / 60
    alb = 0.55 + 0.25 * base - 0.22 * maria
    _tex["moon"] = (alb.astype(np.float32), height.astype(np.float32))
    return _tex["moon"]


def sphere(radius, lon0=0.0, lat_tilt=0.0, light=(0.0, 0.0, 1.0), kind="earth", ambient=0.0,
           atmo=(90, 150, 255), atmo_gain=1.0, cloud_shift=0.0, ss=1):
    """Render a textured, lit sphere. Returns (rgb float (2R,2R,3), alpha (2R,2R), glow (2R+2P...))."""
    R = int(radius)
    pad = int(R * 0.12) + 4
    n = 2 * (R + pad)
    y, x = np.mgrid[0:n, 0:n].astype(np.float32)
    x = (x - (R + pad) + 0.5) / R
    y = (y - (R + pad) + 0.5) / R
    rr = x * x + y * y
    inside = rr <= 1.0
    z = np.sqrt(np.clip(1 - rr, 0, 1))
    # rotate: tilt about x-axis, then longitude
    ct, st = math.cos(lat_tilt), math.sin(lat_tilt)
    y2 = y * ct - z * st
    z2 = y * st + z * ct
    lat = np.arcsin(np.clip(-y2, -1, 1))
    lon = np.arctan2(x, z2) + lon0
    L = np.array(light, np.float32)
    L = L / np.linalg.norm(L)
    ndl = x * L[0] - y * L[1] + z * L[2]
    if kind == "earth":
        col, clouds = earth_tex()
        th, tw = clouds.shape
        u = ((lon / (2 * np.pi) + 0.5) % 1.0) * (tw - 1)
        v = (0.5 - lat / np.pi) * (th - 1)
        rgb = np.stack([ndimage.map_coordinates(col[..., c], [v, u], order=1, mode="wrap") for c in range(3)], -1)
        uc = ((lon / (2 * np.pi) + 0.5 + cloud_shift) % 1.0) * (tw - 1)
        cl = ndimage.map_coordinates(clouds, [v, uc], order=1, mode="wrap")[..., None]
        rgb = rgb * (1 - cl) + np.array([0.95, 0.96, 1.0]) * cl
        diff = np.clip(ndl, 0, 1)
        term = np.clip((ndl + 0.08) / 0.16, 0, 1)
        shade = (diff ** 0.8) * term + ambient
        rgb = rgb * shade[..., None]
        # atmospheric scattering near the limb on the lit side
        limb = np.clip(1 - z, 0, 1) ** 2.2
        a_col = np.array(atmo, np.float32) / 255
        rgb = rgb + limb[..., None] * a_col * np.clip(ndl + 0.25, 0, 1)[..., None] * 0.9 * atmo_gain
    else:  # moon
        alb, hgt = moon_tex()
        th, tw = alb.shape
        u = ((lon / (2 * np.pi) + 0.5) % 1.0) * (tw - 1)
        v = (0.5 - lat / np.pi) * (th - 1)
        a = ndimage.map_coordinates(alb, [v, u], order=1, mode="wrap")
        gy, gx = np.gradient(ndimage.map_coordinates(hgt, [v, u], order=1, mode="wrap"))
        k = 6.0 * R / 400
        nx, ny, nz = x - gx * k, y - gy * k, z
        nn = np.sqrt(nx * nx + ny * ny + nz * nz) + 1e-6
        ndl2 = (nx * L[0] - ny * L[1] + nz * L[2]) / nn
        shade = np.clip(ndl2, 0, 1) ** 0.9 * np.clip((ndl + 0.05) / 0.1, 0, 1) + ambient
        rgb = (a * shade)[..., None] * np.array([0.93, 0.92, 0.9], np.float32)
    alpha = np.clip((1 - np.sqrt(rr)) * R + 0.5, 0, 1)
    rgb = np.where(inside[..., None], rgb, 0)
    # thin outer atmosphere glow for earth
    glow = None
    if kind == "earth":
        d = np.sqrt(rr)
        ring = np.exp(-((d - 1.0) / 0.018) ** 2) * (d > 0.97)
        halo = np.exp(-np.clip(d - 1, 0, None) / 0.035) * (d > 1)
        lit = np.clip((x * L[0] - y * L[1]) / (np.sqrt(rr) + 1e-6) * 0.9 + 0.35 + L[2] * 0.6, 0, 1)
        glow = (ring * 0.9 + halo * 0.6)[..., None] * (np.array(atmo, np.float32) / 255) * lit[..., None] * atmo_gain
    return rgb.astype(np.float32), alpha.astype(np.float32), glow, R + pad


def put_sphere(arr, cx, cy, radius, **kw):
    rgb, alpha, glow, off = sphere(radius, **kw)
    x0, y0 = int(cx - off), int(cy - off)
    over(arr, rgb, alpha, x0, y0)
    if glow is not None:
        h, w = alpha.shape
        light = np.zeros((H, W, 3), np.float32)
        xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
        if xb > xa and yb > ya:
            light[ya:yb, xa:xb] = glow[ya - y0: yb - y0, xa - x0: xb - x0]
            add_light(arr, light)


# ------------------------------------------------------------------ film finish

_grain_bank = None


def _grain(i):
    global _grain_bank
    if _grain_bank is None:
        rng = np.random.default_rng(99)
        bank = []
        for _ in range(8):
            g = rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
            g = ndimage.gaussian_filter(g, 0.6)
            g = ndimage.zoom(g, 2, order=1)
            bank.append(g / (g.std() + 1e-6))
        _grain_bank = bank
    return _grain_bank[i % len(_grain_bank)]


_vig = None


def finish(arr, frame_idx, bloom=0.22, grain=0.012, vignette=0.18):
    """Halation/bloom on highlights, fine grain in the mids, gentle vignette: a 70 mm print look."""
    global _vig
    img = arr[..., :3].astype(np.float32) / 255
    if bloom:
        small = img[::4, ::4]
        lum = small.max(-1, keepdims=True)
        hi = small * np.clip((lum - 0.55) / 0.45, 0, 1)
        b1 = ndimage.gaussian_filter(hi, (6, 6, 0))
        b2 = ndimage.gaussian_filter(hi, (22, 22, 0))
        bl = ndimage.zoom(b1 * 0.6 + b2 * 0.5, (4, 4, 1), order=1)[:H, :W]
        img = img + bl * bloom * np.array([1.0, 0.92, 0.85], np.float32)
    if vignette:
        if _vig is None:
            d = ((_XX - CX) / W) ** 2 + ((_YY - CY) / H) ** 2
            _vig = (1 - vignette * np.clip(d * 2.2, 0, 1) ** 1.5)[..., None].astype(np.float32)
        img = img * _vig
    if grain:
        lum = img.mean(-1, keepdims=True)
        wgt = np.clip(lum * 4, 0, 1) * np.clip((1.2 - lum) * 1.5, 0, 1)
        img = img + _grain(frame_idx)[..., None] * grain * wgt
    arr[..., :3] = (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)

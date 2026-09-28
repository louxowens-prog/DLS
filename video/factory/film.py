"""The film: every finished frame is printed as if shot on 35 mm in 1971 and projected.

look()     warm, soft, saturated Technicolor-like colour; highlights bloom and halate (a red-orange glow bleeds
           round anything bright); clumpy grain that moves every frame; the gate weaves; the lamp flickers;
           dust, hairs and the odd vertical scratch; a projector vignette.
newsreel   the same printed in black and white, harder, dirtier, with more scratches (the TV newsreel).
Transitions of the period: the dissolve and the iris (a black circle closes on one shot, opens on the next).
"""
import math

import numpy as np
from PIL import Image, ImageFilter

from draw import H, W

_cache = {}


def _vig_img():
    if "vig" not in _cache:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((x - W / 2) / (W * 0.62)) ** 2 + ((y - H / 2) / (H * 0.6)) ** 2)
        v = (np.clip(1 - 0.30 * r ** 2.4, 0.45, 1) * 255).astype(np.uint8)
        _cache["vig"] = Image.fromarray(np.dstack([v, v, v]))
    return _cache["vig"]


def _lut(fn):
    """A per-channel lookup table (768 entries) from fn(channel, v in 0..1) -> 0..1."""
    v = np.arange(256) / 255.0
    return [int(round(255 * min(1.0, max(0.0, fn(ch, x))))) for ch in range(3) for x in v]


def _luts():
    if "grade" not in _cache:
        warm, lift = (1.035, 1.0, 0.93), (0.04, 0.026, 0.014)
        _cache["grade"] = _lut(lambda ch, x: (lambda y: y * 1.12 / (1 + 0.12 * y))(x * warm[ch] + lift[ch]))
        _cache["news"] = _lut(lambda ch, x: ((x - 0.5) * 1.3 + 0.52) * (1.0, 0.98, 0.93)[ch])
        _cache["hot"] = _lut(lambda ch, x: max(0.0, (x - 0.8) / 0.2) * x * (0.42, 0.18, 0.09)[ch])
        _cache["hotbw"] = _lut(lambda ch, x: max(0.0, (x - 0.8) / 0.2) * x * 0.25)
        _cache["bloom"] = _lut(lambda ch, x: x * 0.05)
    return _cache


def weave(idx):
    """The gate weave: a slow wander plus a tiny per-frame judder (pixels)."""
    t = idx / 24.0
    dx = 1.3 * math.sin(t * 2.1 + 0.4) + 0.7 * math.sin(t * 5.3 + 1.9) + 0.35 * math.sin(idx * 12.9898)
    dy = 1.6 * math.sin(t * 1.7 + 2.2) + 0.6 * math.sin(t * 4.1 + 0.3) + 0.35 * math.sin(idx * 78.233)
    return dx, dy


def _grain(idx, amp, lum):
    """Clumpy luminance grain, new every frame, strongest in the mid-tones (int16, full size, one channel).
    lum: the frame's luminance at half size (PIL 'L')."""
    rng = np.random.default_rng(idx * 7 + 11)
    g = rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
    l = np.asarray(lum, np.float32) / 255.0
    g = g * (0.35 + 2.6 * l * (1 - l))
    im = Image.fromarray(np.clip(g * 40 + 128, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    return ((np.asarray(im, np.int16) - 128) * (amp * 255 / 40)).astype(np.int16)[..., None]


def _dirt(a, idx, rate=1.0):
    """Dust specks (dark and bright), the occasional hair, and vertical scratches that run for a few frames."""
    rng = np.random.default_rng(idx * 131 + 5)
    for _ in range(rng.poisson(1.6 * rate)):
        x, y = int(rng.uniform(20, W - 20)), int(rng.uniform(20, H - 20))
        r = int(rng.uniform(1, 4))
        v = 30 if rng.random() < 0.6 else 235
        sl = a[max(0, y - r):y + r, max(0, x - r):x + r]
        sl[:] = (sl.astype(np.int16) * 3 + v * 7) // 10
    if rng.random() < 0.02 * rate:                                     # a hair in the gate
        x0, y0 = rng.uniform(100, W - 100), rng.uniform(100, H - 100)
        an = rng.uniform(0, math.pi)
        for k in range(120):
            xx = int(x0 + k * math.cos(an) + 8 * math.sin(k * 0.08))
            yy = int(y0 + k * math.sin(an) + 8 * math.cos(k * 0.05))
            if 0 <= xx < W - 2 and 0 <= yy < H - 2:
                a[yy:yy + 2, xx:xx + 2] = a[yy:yy + 2, xx:xx + 2] // 3
    seg = idx // 30                                                    # a scratch lives ~1 s, then maybe another
    r2 = np.random.default_rng(seg * 977 + 3)
    if r2.random() < 0.2 * rate:
        x = int(r2.uniform(60, W - 60) + (idx % 30) * r2.uniform(-0.6, 0.6))
        v = 225 if r2.random() < 0.7 else 50
        a[:, x:x + 2] = (a[:, x:x + 2].astype(np.int16) * 14 + v * 6) // 20


def look(arr, idx, mode="color", strength=1.0):
    """Print the frame (RGBA uint8, in place) as 1971 35 mm film."""
    from PIL import ImageChops, ImageEnhance
    L = _luts()
    im = Image.fromarray(np.ascontiguousarray(arr[..., :3]))
    dx, dy = weave(idx)
    im = im.transform((W, H), Image.AFFINE, (1, 0, -dx * strength, 0, 1, -dy * strength), resample=Image.BILINEAR,
                      fillcolor=(20, 14, 10))
    im = Image.blend(im, im.filter(ImageFilter.GaussianBlur(1.2)), 0.55)          # the lens and the print are soft
    if mode == "newsreel":
        g = im.convert("L")
        im = Image.merge("RGB", (g, g, g)).point(L["news"])
        hot = im.point(L["hotbw"])
        gamt, dirt, flick = 0.075, 2.6, 0.05
    else:
        im = ImageEnhance.Color(im).enhance(1.2).point(L["grade"])               # saturated dye, warm lifted blacks
        hot = im.point(L["hot"])
        gamt, dirt, flick = 0.032, 1.0, 0.016
    small = (W // 4, H // 4)
    hal = hot.resize(small, Image.BILINEAR).filter(ImageFilter.GaussianBlur(7)).resize((W, H), Image.BILINEAR)
    bloom = im.resize(small, Image.BILINEAR).filter(ImageFilter.GaussianBlur(9)).resize((W, H), Image.BILINEAR)
    im = ImageChops.add(ImageChops.add(im, hal), bloom.point(L["bloom"]))        # halation + bloom
    im = ImageChops.multiply(im, _vig_img())
    rng = np.random.default_rng(idx * 3 + 1)
    f = 1 + flick * strength * rng.normal()
    im = im.point([min(255, int(v * f)) for v in range(256)] * 3)
    a = np.asarray(im, np.int16) + _grain(idx, gamt * strength, im.convert("L").resize((W // 2, H // 2), Image.BILINEAR))
    a = np.clip(a, 0, 255).astype(np.uint8)
    _dirt(a, idx, dirt * strength)
    arr[..., :3] = a
    return arr


# ------------------------------------------------------------------ transitions

def dissolve(a, b, k):
    out = a.copy()
    out[..., :3] = (a[..., :3].astype(np.float32) * (1 - k) + b[..., :3].astype(np.float32) * k).astype(np.uint8)
    return out


def iris(a, b, k, cx=W / 2, cy=H / 2):
    """The iris: a black circle closes down on a (k 0..0.5), then opens up on b (0.5..1)."""
    R = math.hypot(W, H) * 0.62
    src, r = (a, R * (1 - k / 0.5)) if k < 0.5 else (b, R * ((k - 0.5) / 0.5))
    r = max(0.0, r) ** 1.0
    y, x = np.ogrid[0:H, 0:W]
    d = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    m = np.clip((r - d) / 3.0, 0, 1)[..., None]
    out = src.copy()
    out[..., :3] = (src[..., :3].astype(np.float32) * m + np.array([14, 10, 8], np.float32) * (1 - m)).astype(np.uint8)
    return out

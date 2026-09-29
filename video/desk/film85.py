"""The film: every finished frame is printed as if shot on 35 mm in 1985, with anamorphic lenses.

Three registers, each printed its own way, so they can never be confused:
  present  muted, naturalistic colour: cool greys, khaki, pale daylight; soft contrast; fine grain
  memory   black and white: deep shadows, harder contrast, heavier grain, a slightly unsteady gate
  fiction  saturated lacquer colour: rich blacks, gold that blooms; fine grain
  card     the chapter cards: white on black, barely any grain
Every register gets the anamorphic flare: a thin horizontal streak (bluish) from anything bright.
Transitions: clean cuts between registers, fades to black only between chapters.
"""
import math

import numpy as np
from PIL import Image, ImageChops, ImageEnhance, ImageFilter

from draw import H, W

_cache = {}


def _vig(strength):
    k = f"vig{strength}"
    if k not in _cache:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((x - W / 2) / (W * 0.62)) ** 2 + ((y - H / 2) / (H * 0.6)) ** 2)
        v = (np.clip(1 - strength * r ** 2.4, 0.4, 1) * 255).astype(np.uint8)
        _cache[k] = Image.fromarray(np.dstack([v, v, v]))
    return _cache[k]


def _lut(fn):
    v = np.arange(256) / 255.0
    return [int(round(255 * min(1.0, max(0.0, fn(ch, x))))) for ch in range(3) for x in v]


def _s(x, k):
    """A soft S-curve around the middle (k > 1 is more contrast)."""
    return 1 / (1 + math.exp(-k * (x - 0.5) * 4)) if k else x


def _luts():
    if "present" not in _cache:
        lo = _s(0, 1.0)
        hi = _s(1, 1.0)
        norm = lambda y: (y - lo) / (hi - lo)
        # present: a soft curve, lifted blacks; shadows lean cool, mids lean khaki, highlights pale
        def present(ch, x):
            y = 0.055 + 0.9 * norm(_s(x, 1.0))
            tint = [(0.985, 1.0, 1.035), (1.02, 1.01, 0.95), (1.0, 1.0, 0.98)]
            w = [max(0.0, 1 - x * 2.2), 1 - abs(x - 0.5) * 2, max(0.0, x * 2.2 - 1.2)]
            t = sum(w[i] * tint[i][ch] for i in range(3)) / (sum(w) + 1e-6)
            return y * t
        lo2, hi2 = _s(0, 1.45), _s(1, 1.45)
        _cache["present"] = _lut(present)
        _cache["memory"] = _lut(lambda ch, x: 0.02 + 0.96 * (_s(x, 1.45) - lo2) / (hi2 - lo2))
        lo3, hi3 = _s(0, 1.25), _s(1, 1.25)
        _cache["fiction"] = _lut(lambda ch, x: ((_s(x, 1.25) - lo3) / (hi3 - lo3)) * (1.02, 1.0, 0.97)[ch])
        _cache["card"] = _lut(lambda ch, x: x)
        _cache["hot"] = _lut(lambda ch, x: max(0.0, (x - 0.84) / 0.16) * x * (0.30, 0.22, 0.16)[ch])
        _cache["flare"] = [int(255 * max(0.0, (v / 255 - 0.86) / 0.14)) for v in range(256)]
        _cache["bloom"] = _lut(lambda ch, x: x * 0.07)
    return _cache


def _grain(idx, amp, lum, div):
    rng = np.random.default_rng(idx * 7 + 11)
    g = rng.normal(0, 1, (H // div, W // div)).astype(np.float32)
    l = np.asarray(lum.resize((W // div, H // div), Image.BILINEAR), np.float32) / 255.0
    g = g * (0.3 + 2.8 * l * (1 - l))
    im = Image.fromarray(np.clip(g * 40 + 128, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    return ((np.asarray(im, np.int16) - 128) * (amp * 255 / 40)).astype(np.int16)[..., None]


def _hblur(a, w):
    """Box blur along rows (float32 2-D), width w."""
    c = np.cumsum(np.pad(a, ((0, 0), (w // 2 + 1, w // 2)), mode="edge"), axis=1)
    return (c[:, w:] - c[:, :-w]) / w


def _anamorphic(im, gain):
    """Horizontal streaks from the brightest points, blue-cyan, like an anamorphic lens."""
    L = _luts()
    hot = im.convert("L").point(L["flare"]).resize((W // 6, H // 6), Image.BILINEAR)
    a = np.asarray(hot, np.float32) / 255.0
    wide = _hblur(_hblur(a, 61), 61)
    core = _hblur(a, 9)
    s = wide * 0.9 + core * 0.35
    s = np.clip(s * gain, 0, 1)
    up = np.asarray(Image.fromarray((s * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32) / 255.0
    tint = np.array([90, 150, 255], np.float32)
    return (up[..., None] * tint).astype(np.int16)


def weave(idx, amp):
    t = idx / 24.0
    dx = amp * (0.9 * math.sin(t * 1.3 + 0.4) + 0.4 * math.sin(idx * 12.9898))
    dy = amp * (1.1 * math.sin(t * 1.1 + 2.2) + 0.4 * math.sin(idx * 78.233))
    return dx, dy


def _dust(a, idx, rate):
    rng = np.random.default_rng(idx * 131 + 5)
    for _ in range(rng.poisson(rate)):
        x, y = int(rng.uniform(20, W - 20)), int(rng.uniform(20, H - 20))
        r = int(rng.uniform(1, 3))
        v = 30 if rng.random() < 0.6 else 230
        sl = a[max(0, y - r):y + r, max(0, x - r):x + r]
        sl[:] = (sl.astype(np.int16) * 4 + v * 6) // 10


PARAMS = {  # colour, weave px, grain amp, grain size divisor, halation, flare gain, vignette, dust
    "present": dict(sat=0.72, weave=0.5, grain=0.024, div=2, hal=0.8, flare=1.0, vig=0.22, dust=0.15),
    "memory": dict(sat=0.0, weave=1.3, grain=0.05, div=3, hal=0.6, flare=0.7, vig=0.34, dust=0.9),
    "fiction": dict(sat=1.22, weave=0.4, grain=0.018, div=2, hal=1.0, flare=1.5, vig=0.26, dust=0.1),
    "card": dict(sat=1.0, weave=0.0, grain=0.012, div=2, hal=0.0, flare=0.0, vig=0.0, dust=0.0),
}


def look(arr, idx, mode="present"):
    """Print the frame (RGBA uint8, in place) in the register's stock."""
    L = _luts()
    P = PARAMS[mode]
    im = Image.fromarray(np.ascontiguousarray(arr[..., :3]))
    if P["weave"]:
        dx, dy = weave(idx, P["weave"])
        im = im.transform((W, H), Image.AFFINE, (1, 0, -dx, 0, 1, -dy), resample=Image.BILINEAR, fillcolor=(8, 8, 8))
    if mode != "card":
        im = Image.blend(im, im.filter(ImageFilter.GaussianBlur(1.1)), 0.5)          # soft 1985 lenses
    if mode == "memory":
        g = im.convert("L")
        im = Image.merge("RGB", (g, g, g))
    else:
        im = ImageEnhance.Color(im).enhance(P["sat"])
    im = im.point(L[mode])
    if P["hal"]:
        small = (W // 4, H // 4)
        hot = im.point(L["hot"]).resize(small, Image.BILINEAR).filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BILINEAR)
        bloom = im.resize(small, Image.BILINEAR).filter(ImageFilter.GaussianBlur(9)).resize((W, H), Image.BILINEAR)
        if mode == "memory":
            hot = hot.convert("L").convert("RGB")
        im = ImageChops.add(ImageChops.add(im, ImageEnhance.Brightness(hot).enhance(P["hal"])), bloom.point(L["bloom"]))
    if P["vig"]:
        im = ImageChops.multiply(im, _vig(P["vig"]))
    a = np.asarray(im, np.int16)
    if P["flare"]:
        fl = _anamorphic(im, P["flare"])
        if mode == "memory":
            fl = fl.mean(axis=2, keepdims=True).astype(np.int16)
        a = a + fl
    a = a + _grain(idx, P["grain"], im.convert("L"), P["div"])
    a = np.clip(a, 0, 255).astype(np.uint8)
    if P["dust"]:
        _dust(a, idx, P["dust"])
    arr[..., :3] = a
    return arr


def fade(a, k):
    """Toward black: k = 0 (picture) .. 1 (black)."""
    out = a.copy()
    out[..., :3] = (a[..., :3].astype(np.float32) * (1 - k)).astype(np.uint8)
    return out

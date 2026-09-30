"""The print: every frame comes out as a cheap 1980 black-and-white 16 mm print, with hand-tinted colour laid on top.

  - high contrast: crushed blacks, blown-out whites, a soft 16 mm lens
  - heavy, coarse grain; a flicker in exposure from frame to frame; gate weave; a hot centre and dark corners
  - dust, hairs and running scratches, like a print that has been through a lot of projectors
  - hand tint: colour painted onto the black-and-white image, a little outside the lines and boiling from frame to
    frame. Two sources: the shot's own tint layer (a flagged spot, a king's red robe) and, for the garish finale, the
    whole frame's colour (colour=0..1)
The live world and the cartoon world share the stock; the real world gets a slightly gentler grade (mode="real").
"""
import math

import numpy as np
from PIL import Image, ImageFilter

from draw import H, W

_cache = {}


def _curve(lo, hi, gamma):
    x = np.arange(256) / 255.0
    y = np.clip((x - lo) / (hi - lo), 0, 1) ** gamma
    y = y * y * (3 - 2 * y) * 0.35 + y * 0.65                          # a gentle S on top of the crush and blow-out
    return (y * 255).astype(np.float32)


def _luts():
    if not _cache:
        _cache["zone"] = _curve(0.10, 0.84, 1.05)                       # the underworld: hard
        _cache["real"] = _curve(0.06, 0.92, 1.0)                        # the kitchen: a bit gentler
        _cache["card"] = _curve(0.08, 0.80, 1.0)
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((x - W / 2) / (W * 0.62)) ** 2 + ((y - H / 2) / (H * 0.56)) ** 2)
        _cache["vig"] = np.clip(1.08 - 0.42 * r ** 2.2, 0.35, 1.08).astype(np.float32)
    return _cache


def _grain(idx, amp, lum):
    """Coarse 16 mm grain: two scales, strongest in the mid-tones."""
    rng = np.random.default_rng(idx * 7919 + 3)
    g1 = rng.normal(0, 1, (H // 3, W // 3)).astype(np.float32)
    g2 = rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
    up = lambda g: np.asarray(Image.fromarray(np.clip(g * 40 + 128, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR),
                              np.float32) - 128
    g = up(g1) * 0.7 + up(g2) * 0.45
    l = lum / 255.0
    return g * (amp * 255 / 40) * (0.35 + 2.6 * l * (1 - l))


def _flicker(idx):
    rng = np.random.default_rng(idx * 31 + 1)
    return 1.0 + 0.035 * rng.normal() + 0.02 * math.sin(idx * 0.9)


def weave(idx, amp=1.6):
    t = idx / 24.0
    return (amp * (0.7 * math.sin(t * 1.7) + 0.5 * math.sin(idx * 2.31)),
            amp * (0.9 * math.sin(t * 1.3 + 1.0) + 0.6 * math.sin(idx * 1.73)))


def _damage(y, idx, amount):
    """Dust specks (a frame each), hairs (a few frames), scratches that run down the reel."""
    rng = np.random.default_rng(idx * 131 + 5)
    for _ in range(rng.poisson(5 * amount)):                           # dust
        x0, y0 = int(rng.uniform(10, W - 10)), int(rng.uniform(10, H - 10))
        r = int(rng.uniform(1, 4))
        v = 0.0 if rng.random() < 0.55 else 255.0
        yy, xx = np.ogrid[-r:r + 1, -r:r + 1]
        m = (xx ** 2 + yy ** 2 <= r * r)
        sl = y[max(0, y0 - r):y0 + r + 1, max(0, x0 - r):x0 + r + 1]
        mm = m[: sl.shape[0], : sl.shape[1]]
        sl[mm] = sl[mm] * 0.2 + v * 0.8
    seg = idx // 5                                                      # a hair, held for five frames
    hr = np.random.default_rng(seg * 17 + 2)
    if hr.random() < 0.18 * amount:
        x0, y0 = hr.uniform(100, W - 100), hr.uniform(200, H - 200)
        ang, L = hr.uniform(0, math.pi), hr.uniform(40, 120)
        for k in range(int(L)):
            xx = int(x0 + k * math.cos(ang) + 8 * math.sin(k / 9.0))
            yy = int(y0 + k * math.sin(ang))
            if 0 <= xx < W and 0 <= yy < H:
                y[yy, xx] *= 0.25
    reel = idx // 60                                                    # scratches that run for a couple of seconds
    sr = np.random.default_rng(reel * 7 + 11)
    for _ in range(sr.integers(0, 3)):
        x = int(sr.uniform(40, W - 40) + 3 * math.sin(idx * 0.7))
        bright = sr.random() < 0.6
        a = sr.uniform(0.25, 0.55) * amount
        col = y[:, x:x + 2]
        y[:, x:x + 2] = col * (1 - a) + (255.0 if bright else 0.0) * a


def look(arr, idx, mode="zone", tint=None, colour=0.0, damage=1.0):
    """Print the frame (RGBA uint8, in place). tint: an RGBA uint8 layer of hand-painted colour (alpha = where),
    colour: how much of the frame's own colour survives as hand tint (0 = pure black and white)."""
    L = _luts()
    rgb = np.ascontiguousarray(arr[..., :3])
    im = Image.fromarray(rgb)
    dx, dy = weave(idx, 1.3 if mode == "real" else 1.8)
    im = im.transform((W, H), Image.AFFINE, (1, 0, -dx, 0, 1, -dy), resample=Image.BILINEAR, fillcolor=(0, 0, 0))
    im = Image.blend(im, im.filter(ImageFilter.GaussianBlur(1.3)), 0.55)            # the soft 16 mm lens
    a = np.asarray(im, np.float32)
    lum = a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114
    lut = L[mode if mode in L else "zone"]
    y = np.interp(np.clip(lum * _flicker(idx), 0, 255), np.arange(256), lut)
    y = y * L["vig"]
    # hand tint: chroma from the frame (colour) and/or the painted tint layer, on the graded luminance
    cb = np.zeros_like(y)
    cr = np.zeros_like(y)
    if colour > 0:
        cb += (a[..., 2] - lum) * 0.564 * colour * 1.35
        cr += (a[..., 0] - lum) * 0.713 * colour * 1.35
    if tint is not None:
        ti = Image.fromarray(np.ascontiguousarray(tint))
        ti = ti.transform((W, H), Image.AFFINE, (1, 0, -dx - 3, 0, 1, -dy + 2), resample=Image.BILINEAR)   # off-register
        ti = ti.filter(ImageFilter.GaussianBlur(2.5 + 0.8 * math.sin(idx * 1.9)))                          # it boils
        t = np.asarray(ti, np.float32)
        ta = t[..., 3] / 255.0
        tl = t[..., 0] * 0.299 + t[..., 1] * 0.587 + t[..., 2] * 0.114
        cb = cb * (1 - ta) + (t[..., 2] - tl) * 0.564 * 1.25 * ta
        cr = cr * (1 - ta) + (t[..., 0] - tl) * 0.713 * 1.25 * ta
    out = np.empty((H, W, 3), np.float32)
    out[..., 0] = y + 1.403 * cr
    out[..., 1] = y - 0.344 * cb - 0.714 * cr
    out[..., 2] = y + 1.773 * cb
    g = _grain(idx, 0.075 if mode != "card" else 0.05, y)
    out += g[..., None]
    y2 = out.mean(axis=2)
    before = y2.copy()
    _damage(y2, idx, damage)
    out += (y2 - before)[..., None]
    arr[..., :3] = np.clip(out, 0, 255).astype(np.uint8)
    return arr


def fade(a, k):
    out = a.copy()
    out[..., :3] = (a[..., :3].astype(np.float32) * (1 - k)).astype(np.uint8)
    return out


def iris(a, k, cx=W / 2, cy=H / 2):
    """An iris: k = 0 fully open .. 1 closed to black, a hard-edged circle as on an old camera."""
    if k <= 0:
        return a
    rmax = math.hypot(max(cx, W - cx), max(cy, H - cy)) + 4
    r = rmax * (1 - k)
    key = (int(cx) // 4, int(cy) // 4)
    if ("grid", key) not in _cache:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        _cache[("grid", key)] = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    d = _cache[("grid", key)]
    m = np.clip((r - d) / 3.0, 0, 1)
    out = a.copy()
    out[..., :3] = (a[..., :3].astype(np.float32) * m[..., None]).astype(np.uint8)
    return out

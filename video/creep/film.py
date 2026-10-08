"""The 1982 print: a warm, saturated 35 mm colour negative printed for drive-in screens.

  - saturated colour with warm, soft highlights: lamps and lightning bloom, and a little red halation burns round them
  - blacks that stay dense but never quite crush, so the gels (blood red, electric blue, sickly green) glow in the dark
  - night-for-night: a cool blue cast and a stop less exposure, for the scenes shot 'at night'
  - fine 35 mm grain (colour in the shadows), a gate weave of a pixel or so, exposure flicker, a soft vignette
  - the odd speck of dust and a faint scratch, as on a print that has done the rounds
  - flash: lightning lifting the whole exposure towards a cold blue-white
  - plain: the reader's real night - drained of colour, flat and cold, no gel at all
"""
import math

import numpy as np
import skia
from PIL import Image, ImageFilter

import kit as K
from kit import H, W

_c = {}


def _vig():
    if "vig" not in _c:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((x - W / 2) / (W * 0.68)) ** 2 + ((y - H / 2) / (H * 0.6)) ** 2)
        _c["vig"] = np.clip(1.03 - 0.34 * r ** 2.3, 0.45, 1.03).astype(np.float32)[..., None]
    return _c["vig"]


def _grain(idx, lum, amp):
    rng = np.random.default_rng(idx * 104729 + 17)
    g = rng.normal(0, 1, (H // 2, W // 2, 3)).astype(np.float32)
    g[..., 1] = g[..., 1] * 0.5 + g[..., 0] * 0.5                        # colour grain, mostly luminance
    g[..., 2] = g[..., 2] * 0.5 + g[..., 0] * 0.5
    im = Image.fromarray(np.clip(g * 42 + 128, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    g = (np.asarray(im, np.float32) - 128) / 42
    fine = rng.normal(0, 1, (H, W)).astype(np.float32)[..., None] * 0.4
    w = 0.4 + 2.2 * lum * (1 - lum) + 0.3 * (lum < 0.12)                 # mid-tones, and a crawl in the blacks
    return (g + fine) * amp * w


def weave(idx, amp=0.8):
    t = idx / 24.0
    return amp * (0.6 * math.sin(t * 1.7) + 0.4 * math.sin(idx * 2.3)), amp * (0.8 * math.sin(t * 1.3 + 1) + 0.5 * math.sin(idx * 1.7))


def look(arr, T, idx, night=0.0, flash=0.0, plain=0.0, sat=1.16, bloom=0.42, grain=1.0, warm=1.0, dust=True):
    """Print the frame in place (RGBA uint8)."""
    rgb = Image.fromarray(np.ascontiguousarray(arr[..., :3]))
    dx, dy = weave(idx)
    rgb = rgb.transform((W, H), Image.AFFINE, (1, 0, -dx, 0, 1, -dy), resample=Image.BILINEAR, fillcolor=(0, 0, 0))
    a = np.asarray(rgb, np.float32) / 255.0
    lum = a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114
    if bloom > 0:                                                       # highlights bloom at two sizes, with red halation
        hi = a * np.clip((lum[..., None] - 0.52) / 0.48, 0, 1) ** 1.3
        sm = Image.fromarray(np.clip(hi * 255, 0, 255).astype(np.uint8)).resize((W // 4, H // 4), Image.BILINEAR)
        b1 = np.asarray(sm.filter(ImageFilter.GaussianBlur(3)).resize((W, H), Image.BILINEAR), np.float32) / 255
        b2 = np.asarray(sm.filter(ImageFilter.GaussianBlur(14)).resize((W, H), Image.BILINEAR), np.float32) / 255
        a = a + bloom * (0.6 * b1 + 0.8 * b2)
        hl = b2.mean(axis=2)
        a[..., 0] += bloom * hl * 0.4
        a[..., 1] += bloom * hl * 0.1
    if night > 0:                                                       # night-for-night: a stop down, a cool cast
        l2 = (a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114)[..., None]
        cool = a * np.array([0.72, 0.86, 1.12], np.float32) + l2 * np.array([0.0, 0.03, 0.09], np.float32)
        a = a * (1 - night) + cool * (0.78 * night)
    if plain > 0:                                                       # the reader's real night: drained and cold
        l2 = (a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114)[..., None]
        flat = l2 * np.array([0.92, 0.97, 1.05], np.float32) * 0.95 + 0.02
        a = a * (1 - plain) + flat * plain
    if flash > 0:
        a = 1 - (1 - a) * (1 - flash * np.array([0.6, 0.68, 0.82], np.float32))
    if warm:                                                            # warm highlights, a touch of teal in the shadows
        l2 = np.clip(a.mean(axis=2, keepdims=True), 0, 1)
        a = a + warm * (l2 ** 2 * np.array([0.05, 0.02, -0.04], np.float32) + (1 - l2) ** 3 * np.array([-0.012, 0.004, 0.014], np.float32))
    s = sat * (1 - 0.75 * plain)
    l2 = (a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114)[..., None]
    a = l2 + (a - l2) * s
    a = np.clip((a - 0.02) / 0.98, 0, None)
    a = np.where(a < 0.78, a, 0.78 + 0.22 * (1 - np.exp(-(a - 0.78) / 0.22)))   # a soft shoulder: hot light rolls to cream
    flick = 1.0 + 0.016 * np.random.default_rng(idx * 31 + 7).normal()
    a = a * flick * _vig()
    lum = np.clip(a.mean(axis=2), 0, 1)
    a = a + _grain(idx, lum[..., None], 0.03 * grain)
    arr[..., :3] = np.clip(a * 255, 0, 255).astype(np.uint8)
    if dust:
        rng = np.random.default_rng(idx * 7 + 1)
        c = skia.Surface(arr).getCanvas()
        for _ in range(int(rng.integers(0, 3))):
            x, y = rng.uniform(0, W), rng.uniform(0, H)
            c.drawCircle(x, y, rng.uniform(1.2, 3.2), K.paint((240, 236, 226) if rng.random() < 0.4 else (16, 12, 10), rng.uniform(0.3, 0.6)))
        if rng.random() < 0.12:
            x = rng.uniform(60, W - 60)
            c.drawLine(x, 0, x + rng.uniform(-5, 5), H, K.paint((250, 244, 230), rng.uniform(0.05, 0.14), stroke=rng.uniform(1, 2)))
    return arr


def flash_frame(arr, colr, k=1.0):
    """A frame pushed towards one colour (a lightning strike, a shock)."""
    rgb = arr[..., :3].astype(np.float32)
    arr[..., :3] = np.clip(rgb * (1 - 0.85 * k) + np.array(colr, np.float32) * 0.85 * k, 0, 255).astype(np.uint8)
    return arr

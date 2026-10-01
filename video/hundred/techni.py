"""The print: every frame comes out as a 1977 dye-transfer Technicolor print.

  - saturated primaries, pushed further (sat), against crushed, inky blacks (crush) with a soft shoulder, so gel light
    glows instead of clipping flat
  - bloom and red halation round every highlight: lamps, phone screens and lightning burn into the black
  - slight colour fringing: the red record a touch larger than the blue, more towards the corners, like dye layers a
    hair out of register
  - rich, fine 35 mm grain (colour grain in the shadows), a faint gate weave and exposure flicker, a soft vignette
  - flash: lightning lifting the whole exposure towards a cold blue-white; blaze: the finale's light, everything hot
"""
import math

import numpy as np
from PIL import Image, ImageFilter

from draw import H, W

_c = {}


def _vig():
    if "vig" not in _c:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((x - W / 2) / (W * 0.66)) ** 2 + ((y - H / 2) / (H * 0.58)) ** 2)
        _c["vig"] = np.clip(1.04 - 0.36 * r ** 2.4, 0.42, 1.04).astype(np.float32)[..., None]
    return _c["vig"]


def _scale_ch(ch, k):
    """Scale one 8-bit channel about the centre by k (the dye layer out of register)."""
    a = 1.0 / k
    return ch.transform((W, H), Image.AFFINE, (a, 0, W / 2 * (1 - a), 0, a, H / 2 * (1 - a)), resample=Image.BILINEAR)


def _grain(idx, lum, amp):
    rng = np.random.default_rng(idx * 104729 + 17)
    g = rng.normal(0, 1, (H // 2, W // 2, 3)).astype(np.float32)
    g[..., 1] = g[..., 1] * 0.55 + g[..., 0] * 0.45                      # colour grain, mostly luminance
    g[..., 2] = g[..., 2] * 0.55 + g[..., 0] * 0.45
    im = Image.fromarray(np.clip(g * 42 + 128, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    g = (np.asarray(im, np.float32) - 128) / 42
    fine = rng.normal(0, 1, (H, W)).astype(np.float32)[..., None] * 0.45
    w = 0.35 + 2.4 * lum * (1 - lum) + 0.25 * (lum < 0.12)               # mid-tones, and a little crawl in the blacks
    return (g + fine) * amp * w


def weave(idx, amp=0.7):
    t = idx / 24.0
    return amp * (0.6 * math.sin(t * 1.9) + 0.4 * math.sin(idx * 2.7)), amp * (0.8 * math.sin(t * 1.4 + 1) + 0.5 * math.sin(idx * 1.9))


def look(arr, idx, sat=1.3, bloom=0.55, crush=0.05, fringe=2.2, grain=1.0, flash=0.0, blaze=0.0, warm=0.0, halo=1.0):
    """Print the frame in place (RGBA uint8)."""
    rgb = Image.fromarray(np.ascontiguousarray(arr[..., :3]))
    dx, dy = weave(idx)
    rgb = rgb.transform((W, H), Image.AFFINE, (1, 0, -dx, 0, 1, -dy), resample=Image.BILINEAR, fillcolor=(0, 0, 0))
    a = np.asarray(rgb, np.float32) / 255.0
    lum = a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114
    # bloom: the highlights, blurred at two sizes on a quarter-size copy, added back
    if bloom > 0:
        hi = a * np.clip((lum[..., None] - 0.5) / 0.5, 0, 1) ** 1.4
        sm = Image.fromarray(np.clip(hi * 255, 0, 255).astype(np.uint8)).resize((W // 4, H // 4), Image.BILINEAR)
        b1 = np.asarray(sm.filter(ImageFilter.GaussianBlur(4)).resize((W, H), Image.BILINEAR), np.float32) / 255
        b2 = np.asarray(sm.filter(ImageFilter.GaussianBlur(16)).resize((W, H), Image.BILINEAR), np.float32) / 255
        a = a + bloom * (0.7 * b1 + 0.9 * b2)
        hl = b2.mean(axis=2)
        a[..., 0] += bloom * halo * hl * 0.55                           # halation: red light scattered back off the base
        a[..., 1] += bloom * halo * hl * 0.12
    if flash > 0:                                                       # lightning: a cold lift of the whole exposure
        a = 1 - (1 - a) * (1 - flash * np.array([0.62, 0.7, 0.85], np.float32))
    if blaze > 0:
        a = a * (1 + 0.5 * blaze) + 0.04 * blaze
    if warm:
        a = a * np.array([1 + 0.08 * warm, 1 + 0.02 * warm, 1 - 0.1 * warm], np.float32)
    # saturation, then the toe (crushed blacks) and a soft shoulder
    l2 = (a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114)[..., None]
    a = l2 + (a - l2) * sat
    a = np.clip((a - crush) / (1 - crush), 0, None)
    a = a / (1 + 0.42 * a ** 2.2) * 1.42                                # shoulder: over-bright gel light rolls off, keeps its hue
    flick = 1.0 + 0.018 * np.random.default_rng(idx * 31 + 7).normal()
    a = a * flick * _vig()
    lum = np.clip(a.mean(axis=2), 0, 1)
    a = a + _grain(idx, lum[..., None], 0.034 * grain)
    out = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))
    if fringe > 0:                                                      # the dye layers, a hair out of register
        r, g, b = out.split()
        out = Image.merge("RGB", (_scale_ch(r, 1 + fringe / 1000), g, _scale_ch(b, 1 - fringe / 1000)))
    arr[..., :3] = np.asarray(out)
    return arr

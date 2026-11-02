"""The 1960s print: colour that will not sit still (faded full colour, black-and-white, or toned amber, blue, green,
red, violet - switching between shots and sometimes inside one), then grain, a breathing exposure, a soft vignette,
a weaving gate, dust and the odd scratch."""
import math

import numpy as np

import kit as K
from kit import H, W

TONES = {          # shadow colour, highlight colour of a toned print
    "amber": ((60, 26, 6), (255, 214, 140)),
    "blue": ((8, 22, 60), (176, 214, 255)),
    "green": ((10, 46, 22), (190, 244, 184)),
    "red": ((62, 6, 10), (255, 170, 150)),
    "violet": ((34, 10, 56), (224, 186, 255)),
    "bw": ((14, 13, 12), (244, 240, 230)),
}
MODES = ("full", "bw", "amber", "blue", "green", "red", "violet")

_VIG = None
_GRAIN = None


def _vignette():
    global _VIG
    if _VIG is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.6)) ** 2)
        _VIG = np.clip(1.0 - 0.42 * np.clip(d - 0.55, 0, None) ** 1.6, 0.45, 1.0)[..., None]
    return _VIG


def _grain(i):
    global _GRAIN
    if _GRAIN is None:
        r = np.random.default_rng(11)
        g = []
        for k in range(6):
            n = r.normal(0, 1, (H // 2 + 8, W // 2 + 8)).astype(np.float32)
            n = n.repeat(2, 0).repeat(2, 1)[:H + 8, :W + 8]
            g.append(n)
        _GRAIN = g
    return _GRAIN[i % len(_GRAIN)]


def lum(rgb):
    return rgb[..., 0] * 0.3 + rgb[..., 1] * 0.59 + rgb[..., 2] * 0.11


def grade(rgb, mode):
    """rgb float32 0..255 -> the print in this mode."""
    if mode == "full":                                       # faded Eastmancolor: lifted blacks, warm, less saturated
        l = lum(rgb)[..., None]
        out = l + (rgb - l) * 0.82
        out = 14 + out * 0.9
        out = out * np.array([1.04, 1.0, 0.92], np.float32) + np.array([0, -2, 6], np.float32)
        return out
    lo, hi = TONES[mode]
    l = np.clip(lum(rgb) / 255.0, 0, 1)
    l = l * l * (3 - 2 * l) * 0.35 + l * 0.65                # a print's S-curve
    lo, hi = np.array(lo, np.float32), np.array(hi, np.float32)
    return lo + (hi - lo) * l[..., None]


def tone(arr, mode, mode2=None, k=0.0):
    """Grade a frame in place: mode, or a cross-dissolve of two modes (k = 0..1 toward mode2)."""
    rgb = arr[..., :3].astype(np.float32)
    out = grade(rgb, mode)
    if mode2 is not None and k > 0:
        out = out * (1 - k) + grade(rgb, mode2) * k
    arr[..., :3] = np.clip(out, 0, 255).astype(np.uint8)
    return arr


def look(arr, T, idx, amount=1.0, weave=True, scratch=True):
    """Grain, flicker, vignette, gate weave, dust and scratches over a graded frame (in place, returns the frame)."""
    rng = np.random.default_rng(idx * 7 + 1)
    rgb = arr[..., :3].astype(np.float32)
    flick = 1.0 + 0.035 * amount * (rng.random() - 0.5) * 2 + 0.02 * math.sin(T * 13.0)
    g = _grain(idx)
    oy, ox = int(rng.integers(0, 8)), int(rng.integers(0, 8))
    rgb = rgb * flick + g[oy:oy + H, ox:ox + W, None] * (9.0 * amount)
    rgb = rgb * _vignette()
    out = np.clip(rgb, 0, 255).astype(np.uint8)
    if weave:                                                 # the gate weaves a pixel or two
        dx, dy = int(round(1.6 * math.sin(T * 5.3) + rng.uniform(-0.6, 0.6))), int(round(1.2 * math.sin(T * 3.1 + 1)))
        out = np.roll(out, (dy, dx), axis=(0, 1))
    arr[..., :3] = out
    # dust: a few dark specks and hairs on this frame only
    import skia
    c = skia.Surface(arr).getCanvas()
    for _ in range(int(rng.integers(0, 5))):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        r = rng.uniform(1.5, 4.5)
        c.drawCircle(x, y, r, K.paint((20, 16, 14), rng.uniform(0.35, 0.8)))
    if rng.random() < 0.18:
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        p = K.bez_path([(x, y), (x + rng.uniform(-40, 40), y + rng.uniform(10, 40)), (x + rng.uniform(-50, 50), y + rng.uniform(30, 70))])
        c.drawPath(p, K.paint((20, 16, 14), 0.55, stroke=1.6))
    if scratch and rng.random() < 0.3:                        # a pale vertical scratch that wanders
        x = (idx * 37 % W) if rng.random() < 0.5 else rng.uniform(80, W - 80)
        c.drawLine(x, 0, x + rng.uniform(-6, 6), H, K.paint((255, 250, 235), rng.uniform(0.08, 0.22), stroke=rng.uniform(1, 2.4)))
    return arr


def flash(arr, colr, k=1.0):
    """A colour flash frame (a lab splice in one dye)."""
    rgb = arr[..., :3].astype(np.float32)
    arr[..., :3] = np.clip(rgb * (1 - 0.8 * k) + np.array(colr, np.float32) * 0.8 * k, 0, 255).astype(np.uint8)
    return arr

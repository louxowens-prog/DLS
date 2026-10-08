"""Shared by every shot: line timings, mouths and blinks, the Reels-safe layout, and the camera's grammar - slow
trance-like zooms and drifts, rack focus between depth layers, shakes for the impacts."""
import math

import cv2
import numpy as np
import skia

import kit as K
from kit import H, W, ramp
from timeline import TL
from voice import SR

# Reels: words stay out of the top 220 px, the bottom 380 px and (y 1000-1750) the strip right of x 960.
TOP, BOT = 240, H - 400
CAP_TOP = 1330                     # the caption band starts here: keep plaques and labels above it
SPEAKER = {"merit": "MERIT", "iris": "IRIS", "system": "SYSTEM", "nar": "NAR"}


def S(k):
    return TL.s(k)


def E(k):
    return TL.e(k)


def _norm(w):
    return w.lower().strip(".,!?;:'\"…() ").replace("...", "")


def Wx(key, word, nth=0):
    """The start time of a word in a line: exact matches first (so 'in' is not found inside 'inside')."""
    words = TL.lines[key]["words"]
    hits = [a for w, a, b in words if _norm(w) == _norm(word)]
    if not hits:
        hits = [a for w, a, b in words if word.lower() in w.lower()]
    if not hits:
        raise KeyError(f"{word!r} not in {key}")
    return hits[min(nth, len(hits) - 1)]


_ENV = {}


def _env(key):
    if key not in _ENV:
        w = TL.lines[key]["wav"].astype(np.float64)
        hop = SR // 48
        n = len(w) // hop
        e = np.sqrt(np.convolve(w[: n * hop] ** 2, np.ones(hop) / hop, mode="same")[::hop][:n] + 1e-12)
        _ENV[key] = np.clip(e / (np.percentile(e, 95) + 1e-9), 0, 1.2)
    return _ENV[key]


def talk(T, who):
    """Mouth opening 0..1 for a speaker ('CLARA', or a cast key like 'clara') at time T."""
    who = SPEAKER.get(who, who)
    for k in TL.order:
        L = TL.lines[k]
        if L["who"] == who and L["start"] <= T < L["end"]:
            e = _env(k)
            i = int((T - L["start"]) * 48)
            v = float(np.mean(e[max(0, i - 1): i + 2])) if 0 <= i < len(e) else 0.0
            return min(1.0, max(0.0, (v - 0.12) * 1.2))
    return 0.0


def blink(T, seed=0):
    rng = np.random.default_rng(seed + 99)
    t = 0.6 + rng.uniform(0, 1.5)
    while t < T + 1:
        if t <= T < t + 0.14:
            x = (T - t) / 0.14
            return 1 - abs(2 * x - 1)
        t += rng.uniform(2.6, 4.8)
    return 0.0


def hit(T, t0, dur=0.25):
    """1 at t0 decaying to 0 over dur (for flashes and shakes)."""
    if T < t0:
        return 0.0
    return max(0.0, 1 - (T - t0) / dur)


# ------------------------------------------------------------------ the camera

def zoom(c, T, t0, t1, z0, z1, cx=540, cy=960, ease=True):
    """The zoom lens: magnify about (cx, cy) from z0 to z1 over [t0, t1]. Apply before drawing; c.restore() after."""
    k = ramp(T, t0, t1)
    if ease:
        k = K.ease(k)
    z = z0 * (z1 / z0) ** k                                   # zooms feel even in log scale
    c.save()
    c.translate(cx, cy)
    c.scale(z, z)
    c.translate(-cx, -cy)
    return z


def zoom_f(T, t0, t1, f0, f1, ease=True):
    """A focal length for a perspective camera, zooming from f0 to f1."""
    k = ramp(T, t0, t1)
    if ease:
        k = K.ease(k)
    return f0 * (f1 / f0) ** k


def drift(c, T, amp=6.0, seed=0):
    """A slow hand-held wander (pixels)."""
    c.save()
    c.translate(amp * math.sin(T * 0.7 + seed), amp * 0.6 * math.sin(T * 0.53 + seed * 2))


def shake(c, T, amp, seed=0):
    rng = np.random.default_rng(int(T * 24) * 7 + seed)
    c.save()
    c.translate(rng.uniform(-amp, amp), rng.uniform(-amp, amp))


class Layers:
    """Depth layers for rack focus: draw into far / mid / near, then composite each blurred by its distance from the
    plane of focus (0 = far, 1 = mid, 2 = near)."""

    def __init__(self, n=3, bg=(0, 0, 0)):
        self.st = [K.Stage(bg if i == 0 else (0, 0, 0)) for i in range(n)]
        for i in range(1, n):
            self.st[i].arr[...] = 0

    def c(self, i):
        return self.st[i].c

    def compose(self, focus, strength=9.0):
        """focus: 0..n-1 (fractional allowed). Returns an RGBA array."""
        out = None
        for i, st in enumerate(self.st):
            a = st.arr.astype(np.float32) / 255.0
            r = abs(i - focus) * strength
            if r > 0.4:
                a = cv2.GaussianBlur(a, (0, 0), r)
            if out is None:
                out = a
            else:
                al = a[..., 3:4]
                out = out * (1 - al) + a                      # premultiplied over
        res = np.clip(out * 255, 0, 255).astype(np.uint8)
        res[..., 3] = 255
        return res


def rack(T, t0, t1, f0, f1):
    return f0 + (f1 - f0) * K.ease(ramp(T, t0, t1))

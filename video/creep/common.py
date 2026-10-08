"""Shared by every shot: line timings, mouth envelopes and blinks, the Reels-safe layout, camera moves (push-ins, Dutch
angles, shakes) and the comic-page helpers that freeze a live shot into a panel."""
import math

import numpy as np
import skia

import comic as CO
import face as FA
import kit as K
from kit import INK, WHITE, H, W, mix, paint, ramp
from timeline import TL
from voice import SR

# Reels: words stay out of the top 220 px, the bottom 380 px and (y 1000-1750) the strip right of x 960.
TOP, BOT = 240, H - 400
CAP_Y = 1300                       # the caption band starts here: keep faces and balloons above it
SPEAKER = {"nora": "NORA", "vera": "VERA", "kit": "KIT", "prof": "PROF", "hale": "HALE", "hale_old": "HALE", "junior": "JUNIOR",
           "host": "HOST", "muse": "MUSE"}


def S(k):
    return TL.s(k)


def E(k):
    return TL.e(k)


def _norm(w):
    return w.lower().strip(".,!?;:'\"… ").replace("...", "")


def Wx(key, word, nth=0):
    """The start time of a word in a line: exact matches first (so 'The' is not found inside 'father')."""
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
    """Mouth opening 0..1 for a speaker ('NORA', or a cast key like 'nora') at time T."""
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
        if t <= T < t + 0.13:
            x = (T - t) / 0.13
            return 1 - abs(2 * x - 1)
        t += rng.uniform(2.2, 4.4)
    return 0.0


def person(c, who, x, y, s, T, expr="neutral", light="lamp", seed=0, **kw):
    """A cast member, lip-synced to their own lines and blinking."""
    kw.setdefault("talk", talk(T, who))
    kw.setdefault("blink", blink(T, seed))
    return FA.bust(c, who, x, y, s, T, expr=expr, light=light, **kw)


# ------------------------------------------------------------------ camera

def push(c, T, t0, t1, z0, z1, cx=540, cy=800, ease=True):
    """A push-in (or pull-out) about (cx, cy), applied to the canvas until the matching c.restore()."""
    k = ramp(T, t0, t1)
    if ease:
        k = K.ease(k)
    z = z0 + (z1 - z0) * k
    c.save()
    c.translate(cx, cy)
    c.scale(z, z)
    c.translate(-cx, -cy)
    return z


def dutch(c, ang, cx=540, cy=900):
    c.save()
    c.translate(cx, cy)
    c.rotate(ang)
    c.translate(-cx, -cy)


def shake(c, T, amp, seed=0):
    rng = np.random.default_rng(int(T * 24) * 7 + seed)
    c.save()
    c.translate(rng.uniform(-amp, amp), rng.uniform(-amp, amp))


def hit(T, t0, dur=0.25):
    """1 at t0 decaying to 0 over dur (for flashes and shakes)."""
    if T < t0:
        return 0.0
    return max(0.0, 1 - (T - t0) / dur)


# ------------------------------------------------------------------ comic pages

def frame_of(fn, T, idx):
    """Render another shot's picture (for panels): returns an RGBA array, its lettering not counted."""
    saved = list(K.TEXT)
    a = fn(T, idx)
    K.TEXT[:] = saved
    return a


def inked(fn, T, idx, k=1.0):
    """Another shot, frozen into an inked comic print."""
    a = frame_of(fn, T, idx)
    return CO.comicize(a, k)


class sub:
    """A separate canvas for a panel's contents: lettering drawn on it is not counted in the frame's lint (it is
    scaled and placed later). with C.sub(bg) as st: ... ; st.arr"""

    def __init__(self, bg=(0, 0, 0), size=None):
        self.st = K.Stage(bg)
        self.c = self.st.c
        self.arr = self.st.arr

    def __enter__(self):
        self.saved = list(K.TEXT)
        return self

    def __exit__(self, *a):
        K.TEXT[:] = self.saved


def page(bg=CO.NEWS, seed=0):
    st = K.Stage(bg)
    CO.page_bg(st.c, bg, seed=seed)
    return st


def margin_host(c, T, x, y, s, expr="sly", flip=False, light="green", t0=None, peek=1.0):
    """Aunt Atrophy leaning in from the page margin (or a window): slides in from off-frame when t0 is given."""
    k = 1.0 if t0 is None else K.ease(ramp(T, t0, t0 + 0.35))
    dx = (1 - k) * (500 if x > 540 else -500)
    c.save()
    c.translate(x + dx, y)
    if flip:
        c.scale(-1, 1)
    FA.bust(c, "host", 0, 0, s, T, expr=expr, light=light, talk=talk(T, "HOST"), blink=blink(T, 5))
    c.restore()


def roundel_host(c, T, x, y, r, expr="cackle", light="green", ring=(40, 200, 90)):
    """The host in a round inset in the page corner, like a comic's host box."""
    c.save()
    c.drawCircle(x + 8, y + 10, r, paint(INK, 0.6))
    p = K.circle(x, y, r)
    c.clipPath(p, doAntiAlias=True)
    c.drawColor(K.col((30, 10, 40)))
    FA.bust(c, "host", x, y + r * 0.25, r / 190, T, expr=expr, light=light, talk=talk(T, "HOST"), blink=blink(T, 5))
    c.restore()
    c.drawCircle(x, y, r, paint(ring, stroke=10))
    c.drawCircle(x, y, r + 6, paint(INK, stroke=4))

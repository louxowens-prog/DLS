"""Shared by every scene: who is talking and how wide their mouth is, blinks, the safe layout for Reels, fact cards,
and Dot keyed in at the usual framings."""
import math

import numpy as np
import skia

import diy as K
import dot as D
from diy import GOLD, HOT, INK, PURPLE, WHITE, W, H, ease, lin, mix, paint, path, ramp
from timeline import FPS, TL
from voice import SR

# Reels: keep words out of the top 220 px, the bottom 380 px and (from y 1000 to 1750) the right-hand strip past x 960.
TOP, BOT = 230, H - 390
CAP_Y = 1470                      # the caption band's baseline

# ------------------------------------------------------------------ voices: mouth envelopes

_ENV = {}


def _env(key):
    if key not in _ENV:
        w = TL.lines[key]["wav"]
        hop = SR // 48
        n = len(w) // hop
        e = np.sqrt(np.convolve(w[: n * hop] ** 2, np.ones(hop) / hop, mode="same")[::hop][:n] + 1e-12)
        e = e / (np.percentile(e, 95) + 1e-9)
        _ENV[key] = np.clip(e, 0, 1.2)
    return _ENV[key]


def line_at(T, who=None):
    for k in TL.order:
        L = TL.lines[k]
        if L["start"] <= T < L["end"] and (who is None or L["who"] == who or (isinstance(who, (tuple, list)) and L["who"] in who)):
            return k
    return None


def talk(T, who, gain=1.1, quant=None, fps=None):
    """Mouth opening 0..1 for a speaker at time T (0 when they aren't speaking)."""
    if fps:
        T = math.floor(T * fps) / fps
    k = line_at(T, who)
    if k is None:
        return 0.0
    e = _env(k)
    i = int((T - TL.lines[k]["start"]) * 48)
    v = float(np.mean(e[max(0, i - 1): i + 2])) if 0 <= i < len(e) else 0.0
    v = min(1.0, max(0.0, (v - 0.12) * gain))
    if quant:
        v = round(v * quant) / quant
    return v


def blink(T, seed=0):
    """A blink every 2.5-4.5 s, 0.13 s long: returns 0..1 (1 = shut)."""
    rng = np.random.default_rng(seed + 99)
    t, out = 0.6, 0.0
    while t < T + 1:
        if t <= T < t + 0.13:
            x = (T - t) / 0.13
            return 1 - abs(2 * x - 1)
        t += rng.uniform(2.5, 4.5)
    return out


def S(k):
    return TL.s(k)


def E(k):
    return TL.e(k)


def Wx(key, word, nth=0):
    hits = [a for w, a, b in TL.lines[key]["words"] if word.lower() in w.lower()]
    return hits[min(nth, len(hits) - 1)] if hits else S(key)


# ------------------------------------------------------------------ Dot, keyed in

def live_dot(c, T, idx, x, y, s, pose="rest", mood="deadpan", who_talks="DOT", look=(0.0, 0.0), sock_talks="DOC", seed=0,
             halo=9.0, warm=True, a=1.0, **kw):
    """Dot keyed into the plate at (x, y) = feet, scale s; lip-synced to her lines (and Doc to his)."""
    t = talk(T, who_talks) if who_talks else 0.0
    so = talk(T, sock_talks) if sock_talks else 0.0
    kw.setdefault("blink", blink(T, seed))
    with D.live(c, idx, halo=halo, warm=warm, a=a) as L:
        pts = D.dot(L, x, y, s, T, pose=pose, mood=mood, talk=t, look=look, sock_open=kw.pop("sock_open", so), seed=seed, **kw)
    return pts


# ------------------------------------------------------------------ fact cards and labels

def fact_card(c, T, t0, head, body, y=300, w=900, color=GOLD, fname="rubik-900", body_font="jost-600", a=1.0, rot=-1.5, src=None):
    """One fact, big and short, on a cheap TV-graphics card that pops in. head: the number or name; body: one line."""
    k = K.pop(T, t0, 0.25, 0.25)
    if k <= 0:
        return
    c.save()
    c.translate(W / 2, y)
    c.rotate(rot)
    c.scale(k, k)
    f = K.font(body_font, 50)
    lines = K.wrap_balanced(body, f, w - 90)
    h = 112 + 64 * len(lines) + (46 if src else 0)
    c.drawRect(skia.Rect.MakeXYWH(-w / 2 + 14, 16, w, h), paint(INK, 0.55 * a))
    c.drawRect(skia.Rect.MakeXYWH(-w / 2, 0, w, h), paint(shader=lin((-w / 2, 0), (w / 2, h), [(255, 255, 255), (255, 244, 214)]), a=a))
    c.drawRect(skia.Rect.MakeXYWH(-w / 2, 0, w, h), paint(INK, a, stroke=7))
    c.drawRect(skia.Rect.MakeXYWH(-w / 2, 0, w, 16), paint(color, a))
    K.text(c, head, 0, 92, 72, fname, (40, 20, 60), tag="fact", a=a)
    yy = 92 + 66
    for ln in lines:
        K.text(c, ln, 0, yy, 50, body_font, (30, 30, 40), tag="fact", a=a)
        yy += 64
    if src:
        K.text(c, src, 0, yy - 8, 32, "jost-500", (110, 100, 120), tag="fact", a=a)
    c.restore()


def chapter_card(c, T, t0, n, name, style="tv", y=300, dur=2.4):
    """'CH. n · NAME' at the top of the frame for the first seconds of a chapter."""
    k = K.pop(T, t0, 0.3, 0.3) * (1 - ramp(T, t0 + dur - 0.25, t0 + dur))
    if k <= 0:
        return
    c.save()
    c.translate(W / 2, y)
    c.scale(k, k)
    if style == "tv":
        import tv
        tv.wordart(c, f"CH.{n}  {name}", 0, 30, 84, T, max_w=900, warp="wave", amp=0.08)
    c.restore()


# ------------------------------------------------------------------ Dot's hand alone, reaching into a hand-made world

def glue_stick(c, x, y, ang):
    """A purple glue stick held in a fist at (x, y)."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.translate(-46, 56)
    c.rotate(-60)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-26, -150, 52, 190), 12, 12), paint(shader=lin((-26, 0), (26, 0), [(150, 60, 220), (200, 120, 255), (110, 30, 170)])))
    c.drawRect(skia.Rect.MakeXYWH(-22, -186, 44, 40), paint((246, 246, 236)))
    c.drawOval(skia.Rect.MakeXYWH(-22, -196, 44, 20), paint((255, 255, 250)))
    K.text(c, "GLUE", 0, -60, 26, "rubik-900", WHITE, tag="deco")
    c.restore()


def marker(c, x, y, ang, color=(220, 30, 60)):
    """A fat marker held for writing; the tip at (x, y) + a little along ang."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.translate(-30, 60)
    c.rotate(-35)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-24, -40, 48, 210), 18, 18), paint((30, 30, 36)))
    c.drawRect(skia.Rect.MakeXYWH(-24, 120, 48, 30), paint(color))
    c.drawPath(path([(-14, -40), (14, -40), (6, -78), (-6, -78)]), paint(color))
    c.restore()


def live_hand(c, T, idx, x, y, ang=200, pose="fist", prop=None, enter=(1200, 1500), w=58, seed=0):
    """Dot's arm in its polka-dot sleeve, reaching in from off-frame (enter) to a hand at (x, y), keyed in."""
    with D.live(c, idx, halo=8.0) as L:
        D._limb(L, [enter, ((enter[0] + x) / 2 + 30, (enter[1] + y) / 2 + 40), (x, y)], w, D.KNIT)
        D.hand(L, x, y, ang, 1.0, pose, flip=-1)
        if prop is not None:
            prop(L, x, y, ang)

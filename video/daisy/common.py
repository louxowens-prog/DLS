"""Shared by every shot: line timings, mouth envelopes and blinks, the Reels-safe layout, paper labels and chapter
cards, and the duo drawn with their wind-up-doll choreography."""
import math

import numpy as np
import skia

import collage as CL
import duo as D
import kit as K
from kit import INK, WHITE, H, W, mix, paint, ramp
from script import LILI, MACH, NAR, ZUZA
from timeline import TL
from voice import SR

# Reels: words stay out of the top 220 px, the bottom 380 px and (y 1000-1750) the strip right of x 960.
TOP, BOT = 240, H - 400
WHO = {"zuza": ZUZA, "lili": LILI}


def S(k):
    return TL.s(k)


def E(k):
    return TL.e(k)


def Wx(key, word, nth=0):
    hits = [a for w, a, b in TL.lines[key]["words"] if word.lower() in w.lower()]
    return hits[min(nth, len(hits) - 1)] if hits else S(key)


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
    """Mouth opening 0..1 for a speaker (NAR, ZUZA, LILI, MACH, or 'zuza'/'lili') at time T."""
    who = WHO.get(who, who)
    for k in TL.order:
        L = TL.lines[k]
        if L["who"] == who and L["start"] <= T < L["end"]:
            e = _env(k)
            i = int((T - L["start"]) * 48)
            v = float(np.mean(e[max(0, i - 1): i + 2])) if 0 <= i < len(e) else 0.0
            return min(1.0, max(0.0, (v - 0.12) * 1.15))
    return 0.0


def blink(T, seed=0):
    rng = np.random.default_rng(seed + 99)
    t = 0.7
    while t < T + 1:
        if t <= T < t + 0.13:
            x = (T - t) / 0.13
            return 1 - abs(2 * x - 1)
        t += rng.uniform(2.4, 4.6)
    return 0.0


def girl(c, who, x, y, s, T, keys=None, P="stand", **kw):
    """One of the duo, moving like a wind-up doll through keys [(t, pose)], lip-synced and blinking."""
    jolt = 0.0
    if keys:
        P, jolt = D.doll(T, keys)
    kw.setdefault("talk", talk(T, who))
    kw.setdefault("blink", blink(T, 3 if who == "zuza" else 8))
    p = skia.Paint()                                                       # a cut-out, lifted off the page: a soft shadow
    p.setImageFilter(skia.ImageFilters.DropShadow(9 * s / 0.6, 12 * s / 0.6, 6, 6, skia.Color4f(0.06, 0.03, 0.04, 0.5).toColor()))
    c.saveLayer(None, p)
    out = D.figure(c, who, x, y, s, T, P, jolt=jolt * 0.6, **kw)
    c.restore()
    return out


def label(c, s, x, y, size=46, colr=INK, paper=(250, 244, 228), rot=0.0, fname="abril-400", tag="label", a=1.0, pad=(26, 18), edge="cut",
          seed=0, align="center"):
    """A word on a slip of paper (cut or torn), centred on (x, y), pinned at an angle."""
    f = K.font(fname, size)
    w = f.measureText(s)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    x0 = -w / 2 if align == "center" else 0
    CL.paper(c, CL.rect_pts(x0 - pad[0], -size * 0.78 - pad[1], x0 + w + pad[0], size * 0.24 + pad[1]), paper, seed=seed, edge=edge, a=a)
    c.drawString(s, x0, 0, f, paint(colr, a))
    K.reg_local(c, x0, -size * 0.78, x0 + w, size * 0.24, tag)
    c.restore()
    return w


def big(c, s, x, y, size, colors, seed=0, fname="abril-400", tag="big", max_w=920, a=1.0):
    """A headline cut out of magazine paper, letter by letter."""
    return CL.cut_letters(c, s, x, y, size, colors, seed=seed, fname=fname, tag=tag, max_w=max_w, a=a)


CARD_COLORS = [(176, 30, 54), (40, 80, 150), (214, 168, 40), (40, 120, 124), (110, 50, 96)]


def chapter_card(c, T, t0, n, name, bg=(238, 230, 210)):
    """A chapter card: a big numeral cut from paper, the chapter's name in cut letters, daisies scattered."""
    import sets as SE
    SE.void(c, bg, seed=n)
    k = K.ease(ramp(T, t0, t0 + 0.25))
    rng = K.rng_at(n, 3)
    for i in range(14):
        D.daisy(c, rng.uniform(40, W - 40), rng.uniform(300, 1500), rng.uniform(24, 60), rot=i * 33 + T * 20, seed=i + n)
    c.save()
    c.translate(540, 760)
    c.scale(0.6 + 0.4 * k, 0.6 + 0.4 * k)
    CL.paper(c, [(-190, -260), (190, -250), (200, 230), (-200, 240)], CARD_COLORS[n % len(CARD_COLORS)], seed=n, edge="torn")
    f = K.font("abril-400", 400)
    s = str(n)
    c.drawString(s, -f.measureText(s) / 2, 140, f, paint((250, 244, 228)))
    c.restore()
    big(c, name, 520, 1150, 92, [(24, 20, 22), (176, 30, 54), (40, 80, 150)], seed=n * 5, max_w=820)


def typed(s, k):
    """The first k (0..1) of a string, as a typewriter would have it."""
    return s[:int(round(len(s) * max(0.0, min(1.0, k))))]

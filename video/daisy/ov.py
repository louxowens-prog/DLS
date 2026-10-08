"""Captions over the finished print, in one band clear of the Reels UI, each voice in its own hand: the narrator in
clean white, Zuza in pale lemon, Lili in pink, the Oracle in typewriter type."""
import skia

import kit as K
from kit import paint
from script import LILI, MACH, NAR, ZUZA
from timeline import TL

CAP_SIZE, MAX_W, CX, BASE = 54, 850, 520, 1478


def _caps():
    from edit import EDIT
    cuts = [e[0] for e in EDIT]
    out = []
    for t0, t1, s, k in TL.captions():
        end = TL.lines[k]["end"]
        nxt = [x for x in cuts if end - 0.05 < x < t1]
        out.append((t0, min([t1] + nxt), s, k))
    return out


CAPS = _caps()
STYLE = {NAR: ("rubik-700", (255, 255, 255), 1.0), ZUZA: ("rubik-700", (255, 238, 150), 1.0),
         LILI: ("rubik-700", (255, 170, 196), 1.0), MACH: ("special-elite-400", (220, 255, 220), 1.12)}


def telop(arr, T):
    cap = next((c for c in CAPS if c[0] <= T < c[1]), None)
    if not cap:
        return
    t0, t1, s, key = cap
    who = TL.lines[key]["who"]
    fname, colr, sc = STYLE[who]
    size = CAP_SIZE * sc
    f = K.font(fname, size)
    lines = K.wrap_balanced(s, f, MAX_W)
    if len(lines) > 2:
        size *= 0.86
        f = K.font(fname, size)
        lines = K.wrap_balanced(s, f, MAX_W)
    a = min(1.0, (T - t0) / 0.06, (t1 - T) / 0.05)
    c = skia.Surface(arr).getCanvas()
    lh = size * 1.16
    y = BASE - lh * (len(lines) - 1)
    wmax = max(f.measureText(ln) for ln in lines)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(CX - wmax / 2 - 26, y - size * 0.95, CX + wmax / 2 + 26,
                                                         y + lh * (len(lines) - 1) + size * 0.36), 12, 12), paint((14, 10, 12), 0.66 * a))
    for ln in lines:
        K.text(c, ln, CX, y, size, fname, colr, tag="caption", outline=(10, 8, 10), ow=size * 0.12, a=a)
        y += lh

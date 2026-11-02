"""Captions over the finished frame, in one band clear of the Reels UI. Each voice has its own hand: Dot in fat
white, the announcer in gold, DOCTOR in green terminal type, nine-year-old Dot in crayon blue, Doc in hot pink,
AFFIRMA in mint, Mr. Metric in gold."""
import skia

import diy as K
from diy import paint
from script import AFF, ANN, DOC, DOCTOR, DOT, KID, MET
from timeline import TL

CAP_SIZE, MAX_W, CX, BASE = 56, 840, 510, 1478
HIDE = {"a2", "a3"}                       # lines whose words are already on screen as part of the picture


def _caps():
    from edit import EDIT
    cuts = [e[0] for e in EDIT]
    out = []
    for t0, t1, s, k in TL.captions():
        if k in HIDE:
            continue
        end = TL.lines[k]["end"]
        nxt = [x for x in cuts if end - 0.05 < x < t1]
        out.append((t0, min([t1] + nxt), s, k))
    return out


CAPS = _caps()
STYLE = {DOT: ("rubik-800", (255, 255, 255), 1.0), ANN: ("luckiest-guy-400", (255, 214, 60), 1.08),
         DOCTOR: ("vt323-400", (120, 255, 140), 1.25), KID: ("gochi-hand-400", (150, 210, 255), 1.15),
         DOC: ("comic-neue-700", (255, 120, 200), 1.05), AFF: ("audiowide-400", (140, 255, 225), 0.95),
         MET: ("luckiest-guy-400", (255, 200, 40), 1.05)}


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
    lh = size * 1.14
    y = BASE - lh * (len(lines) - 1)
    wmax = max(f.measureText(ln) for ln in lines)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(CX - wmax / 2 - 26, y - size * 0.95, CX + wmax / 2 + 26,
                                                         y + lh * (len(lines) - 1) + size * 0.34), 14, 14), paint((10, 6, 16), 0.62 * a))
    for ln in lines:
        K.text(c, ln, CX, y, size, fname, colr, tag="caption", outline=(8, 6, 12), ow=size * 0.13, a=a)
        y += lh

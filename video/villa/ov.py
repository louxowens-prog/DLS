"""Lettering over the finished print: the narrator in plain white type, the characters in the pale yellow of a
subtitled 1970s print. Captions sit low and left of centre, clear of the Reels buttons and caption bar."""
import skia

import kit as K
from kit import paint
from timeline import TL

CAP_SIZE, MAX_W, CX, BASE = 52, 820, 525, 1505
COLORS = {"NAR": (250, 248, 244), "CLARA": (255, 232, 150), "GOV": (255, 232, 150), "INT1": (255, 232, 150),
          "INT2": (255, 232, 150)}


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


def caption(c, s, who, a):
    f = K.font("jost-500", CAP_SIZE)
    lines = K.wrap_balanced(s, f, MAX_W)
    lh = CAP_SIZE * 1.2
    y0 = BASE - lh * (len(lines) - 1)
    col = COLORS.get(who, (250, 248, 244))
    for i, ln in enumerate(lines):
        y = y0 + lh * i
        w = f.measureText(ln)
        x = CX - w / 2
        c.drawString(ln, x + 2, y + 3, f, paint((0, 0, 0), 0.7 * a, blur=4))
        c.drawString(ln, x, y, f, paint((0, 0, 0), 0.92 * a, stroke=7))
        c.drawString(ln, x, y, f, paint(col, a))
        K.reg(x, y - CAP_SIZE * 0.78, x + w, y + CAP_SIZE * 0.24, "caption")


def overlay(arr, T):
    cap = next((cp for cp in CAPS if cp[0] <= T < cp[1]), None)
    if not cap:
        return
    t0, t1, s, key = cap
    a = min(1.0, (T - t0) / 0.08, max(0.0, (t1 - T) / 0.06))
    st = skia.Surface(arr)
    caption(st.getCanvas(), s, TL.lines[key]["who"], a)

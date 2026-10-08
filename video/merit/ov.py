"""Captions over the finished print: the narrator in warm bone-white, Merit in pale lavender, the system in pale red,
Iris in pale ice-blue. Whole phrases, low and left of centre, clear of the Reels buttons and caption bar, with a dark
halo so they read over any colour the wash throws at them."""
import skia

import kit as K
from kit import paint
from timeline import TL

CAP_SIZE, MAX_W, CX, BASE = 54, 830, 520, 1500
COLORS = {"NAR": (255, 244, 230), "MERIT": (232, 208, 255), "SYSTEM": (255, 196, 190), "IRIS": (206, 236, 255),
          "WHY": (230, 230, 236)}


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
    f = K.font("jost-600", CAP_SIZE)
    lines = K.wrap_balanced(s, f, MAX_W)
    lh = CAP_SIZE * 1.2
    y0 = BASE - lh * (len(lines) - 1)
    col = COLORS.get(who, (250, 248, 244))
    for i, ln in enumerate(lines):
        y = y0 + lh * i
        w = f.measureText(ln)
        x = CX - w / 2
        c.drawString(ln, x + 2, y + 3, f, paint((0, 0, 0), 0.75 * a, blur=6))
        c.drawString(ln, x, y, f, paint((8, 2, 6), 0.95 * a, stroke=8))
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

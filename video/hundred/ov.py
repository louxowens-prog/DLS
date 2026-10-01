"""Captions laid over the finished print, crisp, in one band clear of the Reels UI. Each voice has its own hand:
the narrator in white, the Voice of the AI in pale ice-blue with a small glowing dot, the whisperer in crimson italic,
Nora in warm amber, the dispatcher and the doctor in white."""
import skia

import draw as D
from draw import paint
from script import AI, DISP, DOC, N, NORA, W as WH
from timeline import TL

CAP_SIZE, MAX_W, CX, BASE = 54, 800, 510, 1462
CAPS = TL.captions()
STYLE = {N: ("jost-600", (255, 255, 255)), AI: ("jost-500", (190, 228, 255)), WH: ("cormorant-500i", (255, 70, 80)),
         NORA: ("jost-600", (255, 214, 150)), DISP: ("jost-600", (230, 255, 236)), DOC: ("jost-600", (255, 255, 255))}


def telop(arr, T):
    cap = next((c for c in CAPS if c[0] <= T < c[1]), None)
    if not cap:
        return
    t0, t1, s, key = cap
    who = TL.lines[key]["who"]
    fname, colr = STYLE[who]
    size = CAP_SIZE * (1.25 if who == WH else 1.0)
    f = D.font(fname, size)
    lines = D.wrap_balanced(s, f, MAX_W)
    if len(lines) > 2:
        size *= 0.86
        f = D.font(fname, size)
        lines = D.wrap_balanced(s, f, MAX_W)
    a = min(1.0, (T - t0) / 0.08, (t1 - T) / 0.06)
    c = skia.Surface(arr).getCanvas()
    lh = size * 1.16
    y = BASE - lh * (len(lines) - 1)
    wmax = max(f.measureText(ln) for ln in lines)
    pad = 54 if who == AI else 26
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(CX - wmax / 2 - pad, y - size * 0.98, CX + wmax / 2 + 26,
                                                         y + lh * (len(lines) - 1) + size * 0.36), 12, 12), paint((0, 0, 0), 0.6 * a))
    if who == AI:                                                       # the Voice's little glowing dot
        dx, dy = CX - wmax / 2 - 30, y - size * 0.3
        c.drawCircle(dx, dy, 13, paint((120, 200, 255), 0.45 * a, blur=6))
        c.drawCircle(dx, dy, 8, paint((200, 236, 255), a))
    for ln in lines:
        D.text(c, ln, CX, y, size, fname, colr, tag="caption", outline=(6, 6, 8), ow=size * 0.09, a=a)
        y += lh

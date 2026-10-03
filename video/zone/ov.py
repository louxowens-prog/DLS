"""Captions for the spoken lines, laid over the finished print, crisp: a heavy hand-drawn sans, white with a thin
dark edge on a translucent plate, in one band clear of the Reels UI. Sung lines get no caption: the sing-along
lyrics (with the bouncing ball) are printed in the picture."""
import skia

import draw as D
from draw import WHITE, paint
from timeline import TL

CAP_SIZE, MAX_W, CX, BASE = 56, 820, 510, 1466
CAPS = TL.captions()


def telop(arr, T):
    cap = next((c for c in CAPS if c[0] <= T < c[1]), None)
    if not cap:
        return
    t0, t1, s, key = cap
    f = D.font("londrina-900", CAP_SIZE)
    lines = D.wrap_balanced(s, f, MAX_W)
    size = CAP_SIZE
    if len(lines) > 2:
        size = CAP_SIZE * 0.86
        f = D.font("londrina-900", size)
        lines = D.wrap_balanced(s, f, MAX_W)
    a = min(1.0, (T - t0) / 0.1, (t1 - T) / 0.08)
    c = skia.Surface(arr).getCanvas()
    lh = size * 1.16
    y = BASE - lh * (len(lines) - 1)
    wmax = max(f.measureText(ln) for ln in lines)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(CX - wmax / 2 - 26, y - size * 0.98, CX + wmax / 2 + 26,
                                                         y + lh * (len(lines) - 1) + size * 0.36), 12, 12), paint((0, 0, 0), 0.62 * a))
    for ln in lines:
        D.text(c, ln, CX, y, size, "londrina-900", WHITE, tag="caption", outline=(8, 8, 8), ow=size * 0.1, a=a)
        y += lh

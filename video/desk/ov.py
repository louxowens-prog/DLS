"""Captions for the speech, laid over the finished (filmed) picture, crisp: a restrained serif, like film subtitles,
white with a soft dark edge, in one band clear of the Reels UI. Aphorisms (written big in the picture) and the
prompts she types (on screen, large) get no caption."""
import skia

import draw as D
from cues import NO_CAPTION  # noqa: F401  (re-exported for the transcript)
from draw import INK, WHITE, paint
from timeline import TL

CAP_SIZE, MAX_W, CX = 52, 800, 520
CAPS = TL.captions()


def telop(arr, T):
    cap = next((c for c in CAPS if c[0] <= T < c[1]), None)
    if not cap:
        return
    t0, t1, s, key = cap
    if key in NO_CAPTION:
        return
    from edit import shot_at
    if T > TL.e(key) and shot_at(T) != shot_at(t0 + 0.05):          # never carry a caption over a cut
        return
    f = D.font("cormorant-700", CAP_SIZE)
    lines = D.wrap_balanced(s, f, MAX_W)
    size = CAP_SIZE
    if len(lines) > 2:
        size = CAP_SIZE * 0.86
        f = D.font("cormorant-700", size)
        lines = D.wrap_balanced(s, f, MAX_W)
    a = min(1.0, (T - t0) / 0.12, (t1 - T) / 0.1)
    c = skia.Surface(arr).getCanvas()
    lh = size * 1.18
    y = 1466 - lh * (len(lines) - 1)
    f = D.font("cormorant-700", size)
    wmax = max(f.measureText(ln) for ln in lines)                    # a translucent plate: legible on any background
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(CX - wmax / 2 - 26, y - size * 0.98, CX + wmax / 2 + 26,
                                                         y + lh * (len(lines) - 1) + size * 0.4), 14, 14),
                paint((0, 0, 0), 0.5 * a))
    for ln in lines:
        x0 = CX - f.measureText(ln) / 2                                 # a soft shadow under, then a thin dark edge
        c.drawString(ln, x0 + size * 0.03, y + size * 0.05, f, paint((0, 0, 0), a * 0.85, stroke=size * 0.22, blur=size * 0.16))
        c.drawString(ln, x0, y, f, paint((0, 0, 0), a * 0.55, blur=size * 0.1))
        D.text(c, ln, CX, y, size, "cormorant-700", WHITE, tag="caption", outline=(8, 8, 10), ow=size * 0.09, a=a)
        y += lh

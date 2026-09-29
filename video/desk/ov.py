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
    for ln in lines:
        D.text(c, ln, CX, y, size, "cormorant-700", WHITE, tag="caption", outline=(10, 10, 12), ow=size * 0.2,
               outline2=(0, 0, 0), ow2=size * 0.34, a=a)
        y += lh

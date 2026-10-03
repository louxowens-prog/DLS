"""The compositor: picks the shot for time T, prints it in its register's stock (film85), fades to black around the
chapter cards, then lays the captions on top, crisp."""
import numpy as np

import draw as D
import film85
import ov
import sc1
import sc2
import sc3
import sc4
from edit import EDIT, FADE, shot_at
from timeline import FPS, TL

SHOTS = {}
for mod in (sc1, sc2, sc3, sc4):
    for name in dir(mod):
        if name.startswith("s_"):
            SHOTS[name[2:]] = getattr(mod, name)


def shot_frame(i, T, idx, post=True):
    t0, name, reg, tr = EDIT[i]
    t1 = EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total + 1
    arr = np.ascontiguousarray(SHOTS[name](T, T - t0, t1 - t0))
    if post:
        film85.look(arr, idx, reg)
    return arr


def render_frame(T, idx=None, overlays=True, post=True):
    D.TEXT.clear()
    idx = int(round(T * FPS)) if idx is None else idx
    i = shot_at(T)
    t0, name, reg, tr = EDIT[i]
    out = shot_frame(i, T, idx, post)
    k = 0.0
    if tr == "fade" and T - t0 < FADE:                                  # fading up from black
        k = max(k, 1 - (T - t0) / FADE)
    if i + 1 < len(EDIT) and EDIT[i + 1][3] == "fade":                  # fading down to black
        t1 = EDIT[i + 1][0]
        if t1 - T < FADE:
            k = max(k, 1 - (t1 - T) / FADE)
    if k > 0 and reg != "card":
        out = film85.fade(out, k)
    out = np.ascontiguousarray(out)
    if overlays:
        ov.telop(out, T)
    return out


SAME_OK = ("caption", "scroll", "chat", "banner", "card", "use", "clock", "aph", "prob", "ans", "book", "board", "end", "test",
           "flash", "who0", "who1", "who2", "who3", "who4", "count", "readout", "axis", "slip", "letter", "work", "fix")


def lint(boxes, ignore=()):
    bad = []
    bx = [b for b in boxes if b[4] not in ignore]
    for i in range(len(bx)):
        for j in range(i + 1, len(bx)):
            a, b = bx[i], bx[j]
            if a[4] == b[4] and a[4] in SAME_OK:
                continue
            ox = min(a[2], b[2]) - max(a[0], b[0])
            oy = min(a[3], b[3]) - max(a[1], b[1])
            if ox > 6 and oy > 6:
                bad.append((a, b))
    return bad

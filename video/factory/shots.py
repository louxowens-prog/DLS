"""The compositor: picks the shot for time T, prints it on film (colour, or the black-and-white newsreel), runs the
period transitions (dissolve, iris), then lays the captions or the sing-along lyrics on top, crisp."""
import numpy as np

import draw as D
import film
import ov
import sc1
import sc2
import sc3
from edit import EDIT, NEWSREEL, TRANS, shot_at
from timeline import FPS, TL

SHOTS = {}
for mod in (sc1, sc2, sc3):
    for name in dir(mod):
        if name.startswith("s_"):
            SHOTS[name[2:]] = getattr(mod, name)


def shot_frame(i, T, idx, post=True):
    t0, name, _ = EDIT[i]
    t1 = EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total + 1
    arr = np.ascontiguousarray(SHOTS[name](T, T - t0, t1 - t0))
    if post:
        film.look(arr, idx, mode="newsreel" if name in NEWSREEL else "color")
    return arr


def render_frame(T, idx=None, overlays=True, post=True):
    D.TEXT.clear()
    idx = int(round(T * FPS)) if idx is None else idx
    i = shot_at(T)
    t0, name, tr = EDIT[i]
    out = None
    if tr in ("dissolve", "iris") and T - t0 < TRANS[tr] and i > 0:
        k = (T - t0) / TRANS[tr]
        if tr == "dissolve":
            a = shot_frame(i - 1, T, idx, post)
            D.TEXT.clear()
            b = shot_frame(i, T, idx, post)
            out = film.dissolve(a, b, k)
        elif k < 0.5:
            out = film.iris(shot_frame(i - 1, T, idx, post), None, k)
            D.TEXT.clear()
        else:
            out = film.iris(None, shot_frame(i, T, idx, post), k)
    if out is None:
        out = shot_frame(i, T, idx, post)
    out = np.ascontiguousarray(out)
    if overlays:
        ov.karaoke(out, T)
        ov.telop(out, T)
    return out


SAME_OK = ("caption", "lyric", "headline", "ticket", "letter", "plan", "card", "proj", "portrait", "plaque", "title", "src")


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

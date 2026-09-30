"""The compositor: picks the shot for time T, prints the sing-along lyrics into it, prints it on the 16 mm stock
(film80, with its hand tint), runs the iris and crash-zoom transitions, then lays the captions on top, crisp."""
import numpy as np
from PIL import Image

import cards as KD
import draw as D
import film80
import ov
import sc1
import sc2
import sc3
import sc4
from edit import EDIT, IRIS, shot_at
from timeline import FPS, TL

SHOTS = {}
for mod in (sc1, sc2, sc3, sc4):
    for name in dir(mod):
        if name.startswith("s_"):
            SHOTS[name[2:]] = getattr(mod, name)

CRASH_IN, CRASH_OUT = 0.22, 0.14


def _zoom(a, z):
    if abs(z - 1) < 1e-3:
        return a
    im = Image.fromarray(np.ascontiguousarray(a[..., :3]))
    w, h = int(D.W / z), int(D.H / z)
    x0, y0 = (D.W - w) // 2, (D.H - h) // 2
    im = im.crop((x0, y0, x0 + w, y0 + h)).resize((D.W, D.H), Image.BILINEAR)
    out = a.copy()
    out[..., :3] = np.asarray(im)
    return out


def shot_frame(i, T, idx, post=True):
    t0, name, reg, tr, colour = EDIT[i]
    t1 = EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total + 1
    st = SHOTS[name](T, T - t0, t1 - t0)
    if reg != "card":
        KD.lyric(st.c, T, TL)
    arr = np.ascontiguousarray(st.arr)
    if post:
        tint = st.tint_arr if st.tint_arr[..., 3].any() else None
        film80.look(arr, idx, reg, tint=tint, colour=colour, damage=0.5 if reg == "card" else 1.0)
    return arr


def render_frame(T, idx=None, overlays=True, post=True):
    D.TEXT.clear()
    idx = int(round(T * FPS)) if idx is None else idx
    i = shot_at(T)
    t0, name, reg, tr, colour = EDIT[i]
    t1 = EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total + 1
    out = shot_frame(i, T, idx, post)
    t = T - t0
    if tr == "iris" and t < IRIS:                                       # opening
        out = film80.iris(out, 1 - t / IRIS)
    if i + 1 < len(EDIT) and EDIT[i + 1][3] == "iris" and t1 - T < IRIS:   # closing
        out = film80.iris(out, 1 - (t1 - T) / IRIS)
    if tr == "crash" and t < CRASH_IN:
        out = _zoom(out, 1.0 + 0.45 * (1 - D.ease(t / CRASH_IN)))
    if i + 1 < len(EDIT) and EDIT[i + 1][3] == "crash" and t1 - T < CRASH_OUT:
        out = _zoom(out, 1.0 + 1.2 * D.ease(1 - (t1 - T) / CRASH_OUT))
    if T >= TL.total - 0.02:
        out[..., :3] = 0
    out = np.ascontiguousarray(out)
    if overlays:
        ov.telop(out, T)
    return out


SAME_OK = ("caption", "lyric", "card", "title", "title2", "end", "slip", "phone", "plate", "plates", "stamp", "chartt", "chartv",
           "chartf", "axis", "year", "page", "clash", "folder", "pill", "bottle", "kg", "bpm", "bus", "hb", "hbl", "later",
           "twice", "false", "sec", "picl", "door1", "door3", "doors1", "doors3", "tired", "diet", "pulse", "flagt", "file")


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

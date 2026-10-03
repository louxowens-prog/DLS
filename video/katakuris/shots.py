"""The compositor: picks the shot for time T, runs the video mixer's transitions, prints the picture as cheap
early-2000s video, then lays on the karaoke lyrics or the TV telop captions."""
import numpy as np

import kk
import ov
import sc1
import sc2
import sc3
import sc4
from edit import EDIT, HORROR, WIPE, shot_at
from timeline import FPS, TL

SHOTS = {}
for mod in (sc1, sc2, sc3, sc4):
    for name in dir(mod):
        if name.startswith("s_"):
            SHOTS[name[2:]] = getattr(mod, name)
CARDS = {"card1": (1, "ONE LITTLE|MISTAKE"), "card2": (2, "THE MACHINE"), "card3": (3, "A LETTER|FOR YOU"),
         "card4": (4, "99.9% IN LOVE"), "card5": (5, "TOO MANY|TO SHRUG OFF"), "card6": (6, "KEEP A HAND|ON THE STOP")}
CRASH = 0.16


def shot_frame(i, T, leaving=False):
    t0, name, _ = EDIT[i]
    t1 = EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total + 1
    if name in CARDS:
        n, title = CARDS[name]
        return np.ascontiguousarray(ov.chapter(T, T - t0, n, title, plate=not leaving))
    return np.ascontiguousarray(SHOTS[name](T, T - t0, t1 - t0))


def crash_zoom(arr, z):
    from PIL import Image
    if z <= 1.001:
        return arr
    w, h = kk.W / z, kk.H / z
    x0, y0 = (kk.W - w) / 2, (kk.H - h) / 2
    out = arr.copy()
    out[..., :3] = np.asarray(Image.fromarray(np.ascontiguousarray(arr[..., :3])).resize((kk.W, kk.H), Image.BILINEAR,
                                                                                        box=(x0, y0, x0 + w, y0 + h)))
    kk.TEXT[:] = [((a - x0) * z, (b - y0) * z, (c - x0) * z, (d - y0) * z, tg) for a, b, c, d, tg in kk.TEXT
                  if (c - x0) * z > 0 and (d - y0) * z > 0 and (a - x0) * z < kk.W and (b - y0) * z < kk.H]
    return out


def render_frame(T, idx=None, overlays=True, post=True):
    kk.TEXT.clear()
    idx = int(round(T * FPS)) if idx is None else idx
    i = shot_at(T)
    t0, name, tr = EDIT[i]
    out = None
    if tr in WIPE and T - t0 < WIPE[tr] and i > 0:
        a = shot_frame(i - 1, T, leaving=True)                       # a card pops off as the star bursts out of it
        kk.TEXT.clear()
        b = shot_frame(i, T)
        k = (T - t0) / WIPE[tr]
        out = kk.star_wipe(a, b, k) if tr == "star" else kk.spin_out(a, b, k)
    if out is None:
        out = shot_frame(i, T)
    out = np.ascontiguousarray(out)
    if tr == "flash" and T - t0 < CRASH:
        out = crash_zoom(out, 1 + 0.6 * (1 - (T - t0) / CRASH))
    if post:
        kk.video(out, idx, sat=1.22 if name not in HORROR else 1.1)
    if tr == "flash" and T - t0 < 2 / FPS:
        out[..., :3] = (out[..., :3].astype(np.float32) * 0.3 + 255 * 0.7).astype(np.uint8)
    if overlays and not (tr == "spin" and T - t0 < WIPE[tr] and i > 0):     # nothing rides on a tumbling frame
        ov.karaoke(out, T)
        ov.telop(out, T, horror=name in HORROR, oncard=name in CARDS)
    return out


def lint(boxes, ignore=()):
    bad = []
    bx = [b for b in boxes if b[4] not in ignore]
    for i in range(len(bx)):
        for j in range(i + 1, len(bx)):
            a, b = bx[i], bx[j]
            if a[4] == b[4] and a[4] in ("caption", "lyric"):
                continue
            ox = min(a[2], b[2]) - max(a[0], b[0])
            oy = min(a[3], b[3]) - max(a[1], b[1])
            if ox > 6 and oy > 6:
                bad.append((a, b))
    return bad

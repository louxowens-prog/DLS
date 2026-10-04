"""The compositor: the shot for time T (and the outgoing one through a transition), then the print - the colour mode
of the moment and the 1960s film look - and the captions on top."""
import numpy as np

import collage as CL
import film as F
import kit as K
import ov
from edit import EDIT, TRANS, mode_at, shot_at
from timeline import FPS, TL

SHOTS = {}
for _m in ("sc0", "sc1", "sc2"):
    try:
        mod = __import__(_m)
    except ModuleNotFoundError:
        continue
    SHOTS.update({n[2:]: getattr(mod, n) for n in dir(mod) if n.startswith("s_")})


def _placeholder(name):
    def f(T, idx):
        st = K.Stage((60, 50, 56))
        K.text(st.c, name, 540, 960, 70, "abril-400", K.WHITE, tag="ph")
        return st.arr
    return f


def shot(name, T, idx):
    a = (SHOTS.get(name) or _placeholder(name))(T, idx)
    if a.shape[2] == 3:
        a = np.dstack([a, np.full(a.shape[:2], 255, np.uint8)])
    return np.ascontiguousarray(a)


def render_frame(T, idx=None, overlays=True):
    K.TEXT.clear()
    idx = int(round(T * FPS)) if idx is None else idx
    i = shot_at(T)
    t0, name, tr, _ = EDIT[i]
    arr = shot(name, T, idx)
    F.tone(arr, mode_at(T, i))
    if tr == "scissors" and i > 0 and T < t0 + TRANS["scissors"]:
        saved = list(K.TEXT)
        prev = shot(EDIT[i - 1][1], T, idx)
        K.TEXT[:] = saved                                    # the outgoing shot's words don't count
        F.tone(prev, mode_at(t0 - 0.01, i - 1))
        k = (T - t0) / TRANS["scissors"]
        arr = CL.cut_up(prev, k, seed=i, n=4, spread=3.2, under=arr)
    elif tr == "flash" and T < t0 + TRANS["flash"]:
        F.flash(arr, [(255, 236, 200), (200, 60, 60), (240, 200, 60)][i % 3], 0.9)
    F.look(arr, T, idx)
    if T >= TL.total - 0.02:
        arr[..., :3] = 0
    if overlays:
        ov.telop(arr, T)
    return arr


SAME_OK = ("caption", "strip", "label", "big", "slip", "chapter", "card", "track", "icing", "meter", "type", "exam", "cal", "score",
           "banner", "deco", "answer")


def lint(boxes, ignore=()):
    bad = []
    bx = [b for b in boxes if b[4] not in ignore and b[4] != "deco"]
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


def ui_zone(boxes):
    """Lettering under the Reels UI: the bottom 380 px, the right-hand strip of buttons, the top 220 px."""
    bad = []
    for b in boxes:
        x0, y0, x1, y1, tag = b
        if tag in ("deco",):
            continue
        if y1 > 1920 - 380 + 4 or y0 < 220 - 4 or (x1 > 960 and y1 > 1000 and y0 < 1750):
            bad.append(b)
    return bad

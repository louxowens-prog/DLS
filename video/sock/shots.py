"""The compositor: picks the shot for time T, runs the video mixer's transitions (both shots render through a wipe),
then lays the captions on top."""
import numpy as np

import diy as K
import ov
import tv
from edit import EDIT, TRANS, shot_at
from timeline import FPS, TL

SHOTS = {}
for _m in ("sc0", "sc1", "sc2", "sc3", "sc4", "sc5", "sc6"):
    try:
        mod = __import__(_m)
    except ModuleNotFoundError:
        continue
    SHOTS.update({n[2:]: getattr(mod, n) for n in dir(mod) if n.startswith("s_")})


def _placeholder(name):
    def f(T, idx):
        st = K.Stage((40, 40, 60))
        K.text(st.c, name, 540, 960, 70, "rubik-900", K.WHITE, tag="ph")
        return st.arr
    return f


def shot(name, T, idx):
    fn = SHOTS.get(name) or _placeholder(name)
    a = fn(T, idx)
    if a.shape[2] == 3:
        a = np.dstack([a, np.full(a.shape[:2], 255, np.uint8)])
    return np.ascontiguousarray(a)


MIX = {"star": K.star_wipe, "curl": tv.page_curl, "cube": tv.cube, "checker": tv.checker, "spin": K.spin_out}


def render_frame(T, idx=None, overlays=True):
    K.TEXT.clear()
    idx = int(round(T * FPS)) if idx is None else idx
    i = shot_at(T)
    t0, name, tr, d = EDIT[i]
    arr = shot(name, T, idx)
    if tr in TRANS and T < t0 + d and i > 0:
        saved = list(K.TEXT)
        prev = shot(EDIT[i - 1][1], T, idx)
        K.TEXT[:] = saved                                               # the outgoing shot's words don't count
        arr = MIX[tr](prev, arr, (T - t0) / d)
    elif tr == "snap" and T < t0 + d:
        k = (T - t0) / d
        arr = tv.apply_cam(arr, 0, 0, 0, 1.0 + 0.35 * (1 - K.ease(k)), blur=10 * (1 - k))
    if T >= TL.total - 0.02:
        arr[..., :3] = 0
    arr = np.ascontiguousarray(arr)
    if overlays:
        ov.telop(arr, T)
    return arr


SAME_OK = ("caption", "fact", "wordart", "osd", "phone", "kidtext", "cuttext", "claytext", "flash", "paint", "ps1", "scrawl",
           "lower", "end", "chrome", "logo", "bug", "sign", "chat", "label", "stamp", "quote")


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
        if tag in ("deco", "paint", "osd", "phone"):                    # chrome and props, not information
            continue
        if y1 > 1920 - 380 + 4 or y0 < 220 - 4 or (x1 > 960 and y1 > 1000 and y0 < 1750):
            bad.append(b)
    return bad

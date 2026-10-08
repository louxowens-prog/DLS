"""The compositor: picks the shot for time T, prints it as Technicolor (techni.look, with the shot's own settings),
runs the crash zooms and lightning flashes on the cuts, then lays the captions on top, crisp."""
import numpy as np
from PIL import Image

import draw as D
import ov
import scenes
import techni
from edit import CRASH, EDIT, shot_at
from timeline import FPS, TL

SHOTS = {n[2:]: getattr(scenes, n) for n in dir(scenes) if n.startswith("s_")}


def _zoom(a, z):
    if abs(z - 1) < 1e-3:
        return a
    im = Image.fromarray(np.ascontiguousarray(a[..., :3]))
    w, h = int(D.W / z), int(D.H / z)
    x0, y0 = (D.W - w) // 2, (D.H - h) // 2
    out = a.copy()
    out[..., :3] = np.asarray(im.crop((x0, y0, x0 + w, y0 + h)).resize((D.W, D.H), Image.BILINEAR))
    return out


def render_frame(T, idx=None, overlays=True, post=True):
    D.TEXT.clear()
    idx = int(round(T * FPS)) if idx is None else idx
    i = shot_at(T)
    t0, name, tr = EDIT[i]
    t1 = EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total + 1
    t = T - t0
    st = SHOTS[name](T, t, t1 - t0)
    arr = np.ascontiguousarray(st.arr)
    lk = dict(getattr(st, "lk", {}))
    if tr == "flash" and t < 0.12:
        lk["flash"] = max(lk.get("flash", 0.0), 0.85 * (1 - t / 0.12))
    if post:
        techni.look(arr, idx, **lk)
    if tr == "crash" and t < CRASH:
        arr = _zoom(arr, 1.0 + 0.6 * (1 - D.ease(t / CRASH)))
    if T >= TL.total - 0.02:
        arr[..., :3] = 0
    arr = np.ascontiguousarray(arr)
    if overlays:
        ov.telop(arr, T)
    return arr


SAME_OK = ("caption", "chat", "title", "end", "plate", "keytag", "door", "chart", "case0", "case1", "case2", "case3", "case4",
           "case5", "truth", "safe", "son3", "gridn")


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


def ui_zone(boxes):
    """Lettering under the Reels UI: the bottom 380 px, the right-hand strip of buttons, the top 220 px."""
    bad = []
    for b in boxes:
        x0, y0, x1, y1, tag = b
        if tag == "keytag":                                             # the prop's stamped tag: decoration, not information
            continue
        if y1 > 1920 - 380 + 4 or y0 < 220 - 4 or (x1 > 960 and y1 > 1000 and y0 < 1750):
            bad.append(b)
    return bad

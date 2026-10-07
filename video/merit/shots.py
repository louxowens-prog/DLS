"""The compositor: the shot for time T, its transition in (a cut, a slow dissolve, a superimposition, a white-out), the
1974 print (or the flat present day), then the captions on top."""
import numpy as np

import kit as K
import look as LK
import ov
from edit import EDIT, TRANS, shot_at
from timeline import FPS, TL

SHOTS = {}
for _m in ("sc_open", "sc_alley", "sc_villa", "sc_clock", "sc_real", "sc_end"):
    try:
        mod = __import__(_m)
    except ModuleNotFoundError:
        continue
    SHOTS.update({n[2:]: getattr(mod, n) for n in dir(mod) if n.startswith("s_")})


def _placeholder(name):
    def f(T, idx):
        st = K.Stage((40, 20, 40))
        K.text(st.c, name, 540, 960, 70, "jost-500", K.WHITE, tag="ph")
        return st.arr
    return f


def shot(name, T, idx):
    a = (SHOTS.get(name) or _placeholder(name))(T, idx)
    if a.shape[2] == 3:
        a = np.dstack([a, np.full(a.shape[:2], 255, np.uint8)])
    return np.ascontiguousarray(a)


def printed(i, T, idx):
    """Shot i rendered and printed with its own look."""
    t0, name, tr, lk = EDIT[i]
    a = shot(name, T, idx)
    LK.look(a, T, idx, **{k: v for k, v in lk.items() if k in ("diffusion", "halation", "grain", "sat", "fade", "dust",
                                                               "flick", "plain", "lift", "wv")})
    return a


def render_frame(T, idx=None, overlays=True):
    K.TEXT.clear()
    idx = int(round(T * FPS)) if idx is None else idx
    i = shot_at(T)
    t0, name, tr, lk = EDIT[i]
    arr = printed(i, T, idx)
    d = TRANS.get(tr, 0.0)
    if i > 0 and d > 0 and T < t0 + d:
        k = K.ease((T - t0) / d)
        if tr in ("dissolve", "slow"):
            saved = list(K.TEXT)
            prev = printed(i - 1, T, idx)
            K.TEXT[:] = saved
            arr[..., :3] = (prev[..., :3] * (1 - k) + arr[..., :3] * k).astype(np.uint8)
        elif tr == "white":
            arr[..., :3] = (arr[..., :3] * k + 255 * (1 - k)).astype(np.uint8)
        elif tr == "black":
            arr[..., :3] = (arr[..., :3] * k).astype(np.uint8)
        elif tr == "flash":
            arr[..., :3] = np.clip(arr[..., :3].astype(np.float32) + 255 * (1 - k), 0, 255).astype(np.uint8)
    if lk.get("expose") is not None:
        arr[..., :3] = np.clip(arr[..., :3].astype(np.float32) * lk["expose"], 0, 255).astype(np.uint8)
    if T >= TL.total - 0.04:
        arr[..., :3] = 0
    if overlays:
        ov.overlay(arr, T)
    return arr


SAME_OK = ("caption", "label", "title", "deco", "plaque", "screen", "ledger", "card")


def lint(boxes, ignore=()):
    bad = []
    bx = [b for b in boxes if b[4] not in ignore]
    for i in range(len(bx)):
        for j in range(i + 1, len(bx)):
            a, b = bx[i], bx[j]
            if a[4] == b[4] and a[4] in SAME_OK:
                continue
            if "deco" in (a[4], b[4]) and "caption" not in (a[4], b[4]):
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

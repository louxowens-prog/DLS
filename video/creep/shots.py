"""The compositor: the shot for time T (and the outgoing one through a page turn or a panel zoom), then the 1982 print
(night-for-night, the reader's plain night, lightning), then the comic lettering on top."""
import math

import numpy as np
import skia

import comic as CO
import film as F
import kit as K
import ov
from edit import EDIT, FREEZE_D, LIGHTNING, PAGES, TRANS, look_at, shot_at
from timeline import FPS, TL

SHOTS = {}
for _m in ("sc1", "sc2", "sc3", "sc4"):
    try:
        mod = __import__(_m)
    except ModuleNotFoundError:
        continue
    SHOTS.update({n[2:]: getattr(mod, n) for n in dir(mod) if n.startswith("s_")})


def _placeholder(name):
    def f(T, idx):
        st = K.Stage((60, 40, 56))
        K.text(st.c, name, 540, 960, 70, "bangers-400", K.WHITE, tag="ph")
        return st.arr
    return f


def shot(name, T, idx):
    """Render a shot; 'name@z' is the same shot punched in by z (about 540, 860; or name@z@cx@cy)."""
    base, _, z = name.partition("@")
    cx, cy = 540.0, 860.0
    if "@" in z:
        z, cx, cy = (lambda p: (p[0], float(p[1]), float(p[2])))(z.split("@"))
    n0 = len(K.TEXT)
    a = (SHOTS.get(base) or _placeholder(base))(T, idx)
    if a.shape[2] == 3:
        a = np.dstack([a, np.full(a.shape[:2], 255, np.uint8)])
    if z:
        z = float(z)
        out = np.zeros_like(a)
        c = skia.Surface(out).getCanvas()
        c.translate(cx, cy)
        c.scale(z, z)
        c.translate(-cx, -cy)
        c.drawImage(K.image(a), 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear))
        a = out
        for i in range(n0, len(K.TEXT)):
            x0, y0, x1, y1, tag = K.TEXT[i][:5]
            K.TEXT[i] = (cx + (x0 - cx) * z, cy + (y0 - cy) * z, cx + (x1 - cx) * z, cy + (y1 - cy) * z, tag)
    return np.ascontiguousarray(a)


def lightning(T):
    """Exposure lift from lightning strikes: a bright first stroke and a flicker."""
    v = 0.0
    for t, s in LIGHTNING:
        d = T - t
        if 0 <= d < 0.5:
            v = max(v, s * (math.exp(-d / 0.06) + 0.6 * math.exp(-max(0, d - 0.12) / 0.07) * (d > 0.12)))
    return min(1.0, v)


def freeze_start(i):
    """A live shot that ends on a page turn freezes into an inked comic panel for its last FREEZE_D seconds."""
    if i + 1 >= len(EDIT) or EDIT[i + 1][2] != "page" or EDIT[i][1].partition("@")[0] in PAGES:
        return None
    return EDIT[i + 1][0] - FREEZE_D


def frame(i, T, idx):
    """Shot i at time T, frozen into a comic panel at its end when it leads into a page turn."""
    name = EDIT[i][1]
    tf = freeze_start(i)
    if tf is None or T < tf:
        return shot(name, T, idx)
    saved = list(K.TEXT)
    a = shot(name, tf, idx)
    K.TEXT[:] = saved                                        # the frozen panel is a picture now
    CO.comicize(a, K.ease(min(1.0, (T - tf) / 0.16)))
    return CO.to_panel(a, min(1.0, (T - tf) / 0.3), rect=(60, 250, 1020, 1330), rot=-1.6, seed=i)


def render_frame(T, idx=None, overlays=True):
    K.TEXT.clear()
    idx = int(round(T * FPS)) if idx is None else idx
    i = shot_at(T)
    t0, name, tr, _ = EDIT[i]
    arr = frame(i, T, idx)
    if i > 0 and tr in TRANS and T < t0 + TRANS[tr]:
        k = (T - t0) / TRANS[tr]
        if tr == "page":
            saved = list(K.TEXT)
            prev = frame(i - 1, t0 - 1 / FPS, idx)
            K.TEXT[:] = saved
            arr = CO.page_turn(prev, arr, k)
        elif tr == "zoom":                                   # the comic panel comes alive as it fills the frame
            arr = CO.panel_zoom(CO.comicize(arr, 1 - K.ease(min(1.0, k * 1.3))), k)
        elif tr == "flash":
            F.flash_frame(arr, (255, 250, 240), 1 - k)
        elif tr == "redflash":
            F.flash_frame(arr, (230, 10, 20), 1 - k)
    lk = look_at(T, i)
    if name.partition("@")[0] in PAGES or (tr == "page" and T < t0 + TRANS["page"]):
        CO.newsprint(arr, 1.4)                               # paper fibre on the printed page
    F.look(arr, T, idx, night=lk.get("night", 0.0), plain=lk.get("plain", 0.0), flash=lightning(T) * lk.get("bolt", 1.0),
           sat=lk.get("sat", 1.16), grain=lk.get("grain", 1.0))
    if lk.get("black"):
        arr[..., :3] = (arr[..., :3].astype(np.float32) * (1 - lk["black"])).astype(np.uint8)
    if T >= TL.total - 0.04:
        arr[..., :3] = 0
    if overlays:
        ov.overlay(arr, T)
    return arr


SAME_OK = ("caption", "label", "title", "sfx", "deco", "page", "panel", "screen", "stat")


def lint(boxes, ignore=()):
    bad = []
    bx = [b for b in boxes if b[4] not in ignore]
    for i in range(len(bx)):
        for j in range(i + 1, len(bx)):
            a, b = bx[i], bx[j]
            if a[4] == b[4] and a[4] in SAME_OK:
                continue
            if "deco" in (a[4], b[4]) and "caption" not in (a[4], b[4]) and "balloon" not in (a[4], b[4]):
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

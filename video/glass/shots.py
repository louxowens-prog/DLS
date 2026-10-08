"""The compositor: the shot for time T, printed with its own look (the gloss of the dream or the steel of the white
room), its transition in (a cut, a dissolve, a luminous superimposition, a white flash, a film burn), then the
captions on top."""
import numpy as np

import kit as K
import look as LK
import ov
from edit import EDIT, TRANS, shot_at
from timeline import FPS, TL

SHOTS = {}
for _m in ("sc_open", "sc_eye", "sc_work", "sc_oracle", "sc_scales", "sc_nadia", "sc_end"):
    try:
        mod = __import__(_m)
    except ModuleNotFoundError:
        continue
    SHOTS.update({n[2:]: getattr(mod, n) for n in dir(mod) if n.startswith("s_")})

LOOK_KEYS = ("wash", "wash_k", "keep", "pulse", "bloom", "haze", "streak", "streak_tint", "ca", "melt", "breathe", "smear",
             "burn", "burn_at", "leak", "grain", "sat", "lift", "crush", "wv", "dust", "flick", "diffusion", "halation", "vig",
             "invert", "expose", "seed")


def _placeholder(name):
    def f(T, idx):
        st = K.Stage((40, 10, 30))
        K.text(st.c, name, 540, 960, 70, "jost-500", K.WHITE, tag="ph")
        return st.arr
    return f


def shot(name, T, idx):
    a = (SHOTS.get(name) or _placeholder(name))(T, idx)
    if a.shape[2] == 3:
        a = np.dstack([a, np.full(a.shape[:2], 255, np.uint8)])
    return np.ascontiguousarray(a)


def printed(i, T, idx, **extra):
    """Shot i rendered and printed with its own look (plus any overrides, e.g. a burn)."""
    t0, name, tr, lk = EDIT[i]
    LK.FLARES.clear()
    a = shot(name, T, idx)
    kw = {k: v for k, v in lk.items() if k in LOOK_KEYS}
    kw.update(extra)
    LK.look(a, T, idx, **kw)
    return a


_BOTH = {}


def _both_lettered(i):
    """Do shot i and the shot before it both carry lettering across their dissolve? (Probed once, at its middle.)"""
    if i not in _BOTH:
        t0, name, tr, lk = EDIT[i]
        d = TRANS.get(tr, 0.0)
        saved = list(K.TEXT)
        n = [0, 0]
        for f in (0.15, 0.5, 0.95):                                # (lettering can arrive part-way through)
            tm = t0 + d * f
            for jj, j in enumerate((i - 1, i)):
                K.TEXT.clear()
                shot(EDIT[j][1], tm, int(round(tm * FPS)))
                n[jj] += len(K.TEXT)
        K.TEXT[:] = saved
        _BOTH[i] = n[0] > 0 and n[1] > 0
    return _BOTH[i]


def _sstep(a, b, x):
    u = min(1.0, max(0.0, (x - a) / (b - a)))
    return u * u * (3 - 2 * u)


def render_frame(T, idx=None, overlays=True):
    K.TEXT.clear()
    idx = int(round(T * FPS)) if idx is None else idx
    i = shot_at(T)
    t0, name, tr, lk = EDIT[i]
    d = TRANS.get(tr, 0.0)
    in_tr = i > 0 and d > 0 and T < t0 + d
    k = K.ease((T - t0) / d) if in_tr else 1.0
    # in a dissolve between two lettered shots, the old lettering leaves in the first half and the new arrives in the
    # second, so the words never lie on top of each other
    fade = in_tr and tr in ("dissolve", "slow", "super") and _both_lettered(i)
    kk = (T - t0) / d if in_tr else 1.0
    if in_tr and tr == "burn" and (T - t0) / d < 0.5:
        # the outgoing frame catches fire on the lamp and burns through to white
        u = (T - t0) / d / 0.5
        arr = printed(i - 1, T, idx, burn=0.15 + 0.85 * u, burn_at=lk.get("burn_at", (0.8, 0.2)))
    else:
        K.TEXT_A[0] = _sstep(0.5, 0.95, kk) if fade else 1.0
        arr = printed(i, T, idx)
        K.TEXT_A[0] = 1.0
        if in_tr:
            if tr in ("dissolve",):
                saved = list(K.TEXT)
                K.TEXT_A[0] = 1 - _sstep(0.0, 0.45, kk) if fade else 1.0
                prev = printed(i - 1, T, idx)
                K.TEXT_A[0] = 1.0
                K.TEXT[:] = saved
                arr[..., :3] = (prev[..., :3] * (1 - k) + arr[..., :3] * k).astype(np.uint8)
            elif tr in ("slow", "super"):
                # a double exposure: both images add their light (a screen blend of the two, cross-weighted)
                saved = list(K.TEXT)
                K.TEXT_A[0] = 1 - _sstep(0.0, 0.45, kk) if fade else 1.0
                prev = printed(i - 1, T, idx)
                K.TEXT_A[0] = 1.0
                K.TEXT[:] = saved
                kk = (T - t0) / d
                wa = min(1.0, 2 * (1 - kk))
                wb = min(1.0, 2 * kk)
                A = prev[..., :3].astype(np.float32) / 255 * wa
                B = arr[..., :3].astype(np.float32) / 255 * wb
                arr[..., :3] = np.clip((A + B - A * B) * 255, 0, 255).astype(np.uint8)
            elif tr == "flash":
                arr[..., :3] = np.clip(arr[..., :3].astype(np.float32) + 255 * (1 - k), 0, 255).astype(np.uint8)
            elif tr == "black":
                arr[..., :3] = (arr[..., :3] * k).astype(np.uint8)
            elif tr == "burn":
                u = ((T - t0) / d - 0.5) / 0.5                       # out of the white, into the new shot
                arr[..., :3] = np.clip(arr[..., :3].astype(np.float32) * (0.3 + 0.7 * u) + 255 * (1 - u) ** 1.5 * np.array([1.0, 0.85, 0.6]),
                                       0, 255).astype(np.uint8)
    if T >= TL.total - 0.04:
        arr[..., :3] = 0
    if overlays:
        ov.overlay(arr, T)
    return arr


SAME_OK = ("caption", "label", "title", "deco", "plaque", "screen", "card", "stamp", "cloud")


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

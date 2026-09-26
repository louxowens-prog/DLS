"""The compositor: picks the shot for time T, runs transitions between shots, letters the narration into
yellow comic boxes, and prints the newsprint grain. Also keeps the text-collision lint."""
import math

import numpy as np
import skia

import scenes_a as A
import scenes_b as B
import scenes_c as Cc
import sv
from edit import EDIT, GLITCH, SLIDE, shot_at
from script import NAR
from timeline import FPS, TL
from sv import INK, WHITE, YEL, MAG, CYAN

SHOTS = {
    "gold": A.s_gold, "clock": A.s_clock, "hookq": A.s_hookq, "road": A.s_road, "speed": A.s_speed,
    "jagged": B.s_jagged, "noir": B.s_noir, "anime": B.s_anime, "clash": B.s_clash,
    "agi": Cc.s_agi, "nosleep": Cc.s_nosleep, "copies": Cc.s_copies, "evolve": Cc.s_evolve, "question": Cc.s_question,
    "routes": Cc.s_routes, "bar": Cc.s_bar, "summary": Cc.s_summary, "outro": Cc.s_outro, "end": Cc.s_end,
}
CAPS = [c for c in TL.captions() if TL.who(c[3]) == NAR]
CAP_BOTTOM = 1528
NOCAP = set()                     # every narrator line is lettered


def shot_frame(i, T):
    t0, name, _ = EDIT[i]
    t1 = EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total + 1
    arr = SHOTS[name](T, T - t0, t1 - t0)
    return np.ascontiguousarray(arr)


def _impact_flash(T, color):
    st = sv.Stage(color)
    sv.impact_bg(st.c, color, 540, 820, T, n=70, r0=200, seed=int(T * 24) % 7)
    return st.arr


def _slide(a, b, k):
    """The new panel slides in from the right over the old one: white gutter + ink edge on its leading side."""
    k = sv.ease(k)
    x = int(sv.W * (1 - k))
    out = a.copy()
    if x < sv.W:
        out[:, x:] = b[:, : sv.W - x]
        g0, g1 = max(0, x - 26), max(0, x)
        out[:, g0:g1, :3] = sv.PAPER
        e0, e1 = max(0, x - 8), min(sv.W, x + 6)
        out[:, e0:e1, :3] = INK
    return out


def caption(arr, T):
    cap = next((c for c in CAPS if c[0] <= T < c[1]), None)
    if not cap:
        return
    t0, t1, s, key = cap
    if key in NOCAP:
        return
    f = sv.font("comic-neue-700", 46)
    lines = sv.wrap(s.upper(), f, 860 - 60)
    bh = 46 * 1.12 * len(lines) + 34
    y = CAP_BOTTOM - bh - 12
    k = sv.pop(T, t0, 0.18)
    c = skia.Surface(arr).getCanvas()
    sv.narration(c, s, 500, y, maxw=860, size=46, k=k, rot=-1.0 if (hash(s) % 2) else 1.0)


def render_frame(T, idx=None, captions=True):
    sv.TEXT.clear()
    i = shot_at(T)
    out = None
    for j in (i, i + 1):
        if j <= 0 or j >= len(EDIT):
            continue
        b0, _, tr = EDIT[j]
        if tr == "glitch" and b0 - GLITCH / 2 <= T < b0 + GLITCH / 2:
            k = (T - (b0 - GLITCH / 2)) / GLITCH
            fa = shot_frame(j - 1, T)
            fb = shot_frame(j, max(T, b0))
            sv.TEXT.clear()
            out = sv.glitch(fa, fb, k, seed=j, idx=int(round(T * FPS)))
            break
        if tr == "slide" and b0 <= T < b0 + SLIDE:
            fa = shot_frame(j - 1, T)
            sv.TEXT.clear()
            fb = shot_frame(j, T)
            out = _slide(fa, fb, (T - b0) / SLIDE)
            break
        if tr == "impact" and b0 <= T < b0 + 2 / FPS:
            out = _impact_flash(T, [YEL, MAG, CYAN][j % 3])
            break
    if out is None:
        out = shot_frame(i, T)
    out = np.ascontiguousarray(out)
    sv.grain(out, 4)
    if captions:
        caption(out, T)
    return out


def lint(boxes, ignore=("bgtag",)):
    """Pairs of text rectangles that overlap (ignoring faded background tags)."""
    bad = []
    bx = [b for b in boxes if b[4] not in ignore]
    for i in range(len(bx)):
        for j in range(i + 1, len(bx)):
            a, b = bx[i], bx[j]
            ox = min(a[2], b[2]) - max(a[0], b[0])
            oy = min(a[3], b[3]) - max(a[1], b[1])
            if ox > 6 and oy > 6:
                bad.append((a, b))
    return bad

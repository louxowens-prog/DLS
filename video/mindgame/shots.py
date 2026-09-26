"""The edit: which shot is on screen when, flash-frame cuts, captions."""
import numpy as np
import skia

import mg
import scenes_1 as A
import scenes_2 as B
import scenes_3 as D
from cues import C
from timeline import FPS, TL

S, E, Wd = TL.s, TL.e, TL.word
OCTO = Wd("c4", "octopus") - 0.35

SHOTS = [
    (0.0, S("h2"), A.s_gold), (S("h2"), S("h3"), A.s_clock), (S("h3"), S("a1"), A.s_title),
    (S("a1"), S("a2"), A.s_gpqa), (S("a2"), S("a3"), A.s_agents), (S("a3"), S("a4"), A.s_robot),
    (S("a4"), S("a5"), A.s_nobody), (S("a5"), S("l1"), A.s_agiq), (S("l1"), S("g1"), A.s_levels),
    (S("g1"), S("g2"), B.s_nature), (S("g2"), S("g3"), B.s_score), (S("g3"), S("g4"), B.s_deepmind),
    (S("g4"), S("g5"), B.s_notif), (S("g5"), S("g6") - 0.05, B.s_water), (S("g6") - 0.05, S("g7"), B.s_montage),
    (S("g7"), C["silence"], B.s_water2), (C["silence"], S("c2"), B.s_c1), (S("c2"), S("c3"), B.s_c2),
    (S("c3"), OCTO, B.s_c3), (OCTO, S("c5"), B.s_octo), (S("c5"), C["missing"], B.s_c5),
    (C["missing"], S("m1"), D.s_m0), (S("m1"), S("m2"), D.s_m1), (S("m2"), S("m3"), D.s_m2), (S("m3"), S("m4"), D.s_m3),
    (S("m4"), S("m5"), D.s_m4), (S("m5"), S("m6"), D.s_m5), (S("m6"), C["finale"], D.s_m6),
    (C["finale"], C["final_silence"], D.s_finale), (C["final_silence"], C["end_card"], D.s_final),
    (C["end_card"], C["end"] + 1.0, D.s_end),
]
CALM = {B.s_c1, B.s_c2, B.s_c3, B.s_c5, D.s_final, D.s_end, D.s_finale}
NOCAP_KEYS = {"g6", "c3j"}
CAPS = [c for c in TL.captions() if c[3] not in NOCAP_KEYS]


def balanced(s, f, maxw):
    if f.measureText(s) <= maxw:
        return [s]
    words = s.split()
    best, bi = None, 1
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        wa, wb = f.measureText(a), f.measureText(b)
        cost = max(wa, wb) + (400 if max(wa, wb) > maxw else 0)
        if best is None or cost < best:
            best, bi = cost, i
    return [" ".join(words[:bi]), " ".join(words[bi:])]


def draw_caption(arr, T):
    s = next((c[2] for c in CAPS if c[0] <= T < c[1]), None)
    if not s:
        return
    f = mg.font("rubik-900", 60)
    lines = balanced(s, f, 880)
    surf = mg.surf(arr)
    with surf as c:
        y = mg.CAP_Y - (len(lines) - 1) * 10
        for ln in lines:
            w = f.measureText(ln)
            c.drawString(ln, mg.CX - w / 2, y, f, mg.paint((0, 0, 0), 1.0, stroke=10))
            c.drawString(ln, mg.CX - w / 2, y, f, mg.paint((255, 255, 255)))
            y += 70


def flash(arr, T, a):
    """Flash frames on the cut: two frames of inverted or colour-slammed picture."""
    k = int((T - a) * FPS)
    if k >= 2:
        return
    rng = np.random.default_rng(int(a * 100))
    if rng.random() < 0.5:
        arr[..., :3] = 255 - arr[..., :3]
    else:
        col = np.array(mg.PSY[int(rng.integers(len(mg.PSY)))], np.float32)
        arr[..., :3] = (arr[..., :3] * 0.45 + col * 0.55).astype(np.uint8)


def render_frame(T, idx=None, captions=True):
    arr = mg.new((0, 0, 0))
    for a, b, fn in SHOTS:
        if a <= T < b:
            fn(arr, T - a, b - a, T)
            if fn not in CALM and a > 0:
                flash(arr, T, a)
            break
    if captions:
        draw_caption(arr, T)
    return arr

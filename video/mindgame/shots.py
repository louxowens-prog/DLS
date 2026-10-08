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
    (0.0, S("h2"), A.s_hook), (S("h2"), S("h3"), A.s_clock), (S("h3"), S("a1"), A.s_title),
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
# big-face cutaways inserted over the main shots (start, end, shot)
INSERTS = [
    (S("a3") + 1.8, S("a3") + 2.45, D.insert_face("jag", (255, 200, 90), "OOPS!", S("a3") + 1.8)),
    (Wd("a4", "then"), Wd("a4", "then") + 0.75, D.insert_face("jag", "swirl", "?!", Wd("a4", "then"))),
    (S("g1"), S("g1") + 1.2, D.insert_face("jag", "burst", "WAIT!", S("g1"))),
    (S("c3j") - 0.05, E("c3j") + 0.12, D.insert_talk("c3j")),
    (Wd("m5", "touched") - 0.1, Wd("m5", "touched") + 0.75, D.insert_face("human", (255, 150, 120), "OW!", Wd("m5", "touched") - 0.1, mouth="ow")),
    (S("m6"), S("m6") + 0.8, D.insert_face("human", (255, 214, 60), "HMM...", S("m6"), mouth="flat")),
]
# Mind Game switches drawing method from scene to scene; every shot gets its own
STYLE_OF = {
    A.s_hook: "cel", A.s_gold: "cel", A.s_clock: "pencil", A.s_title: "print", A.s_gpqa: "crayon", A.s_agents: "cel", A.s_robot: "pencil",
    A.s_nobody: "crayon", A.s_agiq: "print", A.s_levels: "print", B.s_nature: "print", B.s_score: "crayon",
    B.s_deepmind: "pencil", B.s_notif: "cel", B.s_water: "crayon", B.s_montage: "print", B.s_water2: "crayon",
    B.s_c1: "print", B.s_c2: "print", B.s_c3: "print", B.s_octo: "crayon", B.s_c5: "print",
    D.s_m0: "cel", D.s_m1: "pencil", D.s_m2: "crayon", D.s_m3: "cel", D.s_m4: "pencil", D.s_m5: "crayon", D.s_m6: "print",
    D.s_final: "crayon", D.s_end: "print",
}
CALM = {B.s_c1, B.s_c2, B.s_c3, B.s_c5, D.s_final, D.s_end, D.s_finale, A.s_levels}
NO_DRIFT = {B.s_montage, D.s_finale, D.s_end, A.s_title, A.s_agiq, A.s_levels}
NOCAP_KEYS = {"g6"}
CAPS = [c for c in TL.captions() if c[3] not in NOCAP_KEYS]


GAP = 1.55          # word spacing, in spaces: the heavy outline must never fill the gap between words


def line_w(ln, f):
    words = ln.split()
    return sum(f.measureText(w) for w in words) + f.measureText(" ") * GAP * (len(words) - 1)


def balanced(s, f, maxw):
    if line_w(s, f) <= maxw:
        return [s]
    words = s.split()
    best, bi = None, 1
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        wa, wb = line_w(a, f), line_w(b, f)
        cost = max(wa, wb) + (400 if max(wa, wb) > maxw else 0)
        if best is None or cost < best:
            best, bi = cost, i
    return [" ".join(words[:bi]), " ".join(words[bi:])]


def draw_caption(arr, T):
    s = next((c[2] for c in CAPS if c[0] <= T < c[1]), None)
    if not s or T >= C["end_card"] or C["finale"] <= T < TL.s("f1") - 0.1:
        return
    f = mg.font("rubik-900", 60)
    sp = f.measureText(" ") * GAP
    lines = balanced(s, f, 840)
    surf = mg.surf(arr)
    with surf as c:
        y = mg.CAP_Y - (len(lines) - 1) * 10
        for ln in lines:
            x = mg.CX - line_w(ln, f) / 2
            for w in ln.split():
                c.drawString(w, x + 3, y + 5, f, mg.paint((0, 0, 0), 0.55, blur=5))
                c.drawString(w, x, y, f, mg.paint((0, 0, 0), 1.0, stroke=8))
                c.drawString(w, x, y, f, mg.paint((255, 255, 255)))
                x += f.measureText(w) + sp
            y += 72


def flash(arr, T, a):
    """Flash frames on the cut: two frames washed with a slammed colour (no inversions)."""
    k = int((T - a) * FPS)
    if k >= 2:
        return
    rng = np.random.default_rng(int(a * 100))
    col = np.array(mg.PSY[int(rng.integers(len(mg.PSY)))], np.float32)
    w = 0.5 if k == 0 else 0.25
    arr[..., :3] = (arr[..., :3] * (1 - w) + col * w).astype(np.uint8)


def drift(arr, k, T):
    """Slow push-in with a tiny hand-held wobble on twos."""
    from PIL import Image
    z = 1.004 + 0.05 * k
    rng = np.random.default_rng(mg.step(T))
    ox, oy = rng.normal(0, 1.5), rng.normal(0, 1.5)
    w, h = mg.W / z, mg.H / z
    x0 = min(max(0.0, mg.CX - w / 2 + ox), mg.W - w)
    y0 = min(max(0.0, 880 - 880 / z + oy), mg.H - h)
    img = Image.fromarray(arr[..., :3]).resize((mg.W, mg.H), Image.BILINEAR, box=(x0, y0, x0 + w, y0 + h))
    arr[..., :3] = np.asarray(img)


def render_frame(T, idx=None, captions=True):
    arr = mg.new((0, 0, 0))
    ins = next(((a, b, fn) for a, b, fn in INSERTS if a <= T < b), None)
    for a, b, fn in ([ins] if ins else SHOTS):
        if a <= T < b:
            mg.set_style(STYLE_OF.get(fn, "cel" if ins else "print"))
            fn(arr, T - a, b - a, T)
            if fn not in NO_DRIFT and not ins:
                drift(arr, (T - a) / max(0.1, b - a), T)
            if fn not in CALM and a > 0:
                flash(arr, T, a)
            break
    if captions:
        draw_caption(arr, T)
    return arr

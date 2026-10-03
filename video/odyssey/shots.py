"""The edit: which shot is on screen when, plus captions and the film finish."""
import numpy as np
import skia

import gfx as G
import scenes_a as A
from cues import C
from timeline import FPS, TL

try:
    import scenes_b as B
except ImportError:  # pragma: no cover
    B = None
try:
    import scenes_c as Cc
except ImportError:  # pragma: no cover
    Cc = None


def _s(k):
    return TL.s(k)


def _get(mod, name):
    return getattr(mod, name) if mod is not None and hasattr(mod, name) else None


SHOTS = [
    (0.0, C["chat"], A.s_open, {}),
    (C["chat"], C["align"], A.s_chat, {}),
    (C["align"], C["ch1"], A.s_sunrise, {"finish": {"bloom": 0.3}}),
    (C["ch1"], _s("useful"), A.s_defs, {}),
    (_s("useful"), _s("knowledge"), A.s_useful, {}),
    (_s("knowledge"), C["monolith"], A.s_knowledge, {}),
    (C["monolith"], _s("rock") - 0.05, A.s_drive, {}),
    (_s("rock") - 0.05, C["silence"], A.s_rock, {}),
    (C["silence"], C["child"], A.s_nothing, {}),
    (C["child"], C["bone"], A.s_child, {}),
    (C["bone"], C["cut"], A.s_bone, {}),
    (C["cut"], _s("artif") + 1.2, A.s_sat, {}),
    (_s("artif") + 1.2, _s("light"), A.s_artif, {}),
    (_s("light"), C["heart"], A.s_corridor, {"finish": {"bloom": 0.35}}),
    (C["heart"], _s("built"), A.s_heart, {}),
    (_s("built"), _s("nist"), A.s_station, {}),
    (_s("nist"), _s("chess"), A.s_nist, {}),
    (_s("chess"), C["alphago"], A.s_chess, {}),
    (C["alphago"], _s("question"), A.s_go, {}),
    (_s("question"), C["ch3"], A.s_jupiter, {}),
    (C["ch3"], _s("params") - 0.5, "s_db", {}),
    (_s("params") - 0.5, _s("capitals"), "s_memory", {"finish": {"bloom": 0.35}}),
    (_s("capitals"), _s("map"), "s_vectors", {}),
    (_s("map"), _s("wrong"), "s_galaxy", {"finish": {"bloom": 0.3}}),
    (_s("wrong"), C["ch4"], "s_ae35", {}),
    (C["ch4"], _s("earth"), "s_tokens", {}),
    (_s("earth"), _s("tilt"), "s_predict", {}),
    (_s("tilt"), C["stargate"], "s_tilt", {}),
    (C["stargate"], C["stargate_end"], "s_stargate", {"finish": {"bloom": 0.3, "grain": 0.008}, "plate": True}),
    (C["stargate_end"], _s("surprise") - 0.1, "s_childdata", {}),
    (_s("surprise") - 0.1, _s("glass"), "s_earth", {}),
    (_s("glass"), C["ch5"], "s_glass", {}),
    (C["ch5"], _s("shakes"), "s_just", {}),
    (_s("shakes"), _s("train"), "s_neurons", {"finish": {"bloom": 0.35}}),
    (_s("train"), _s("dallas"), "s_gen", {}),
    (_s("dallas"), _s("philo"), "s_dallas", {}),
    (_s("philo"), _s("jagged"), "s_tma", {}),
    (_s("jagged"), C["close"], "s_jagged", {}),
    (C["close"], C["end_title"], "s_starchild", {"finish": {"bloom": 0.35}, "plate": True}),
    (C["end_title"], C["end"] + 1.0, "s_endcard", {}),
]


def _resolve(fn):
    if callable(fn):
        return fn
    for mod in (B, Cc):
        f = _get(mod, fn)
        if f is not None:
            return f
    return None


# the glass line is typed on screen by its own shot, so it gets no caption
CAPS = [c for c in TL.captions() if not (TL.s("glass") - 0.1 <= c[0] < TL.e("glass") + 0.1)]
# no captions over intertitles or the title card
_NOCAP = []


def caption_at(T):
    for a, b, s in CAPS:
        if a <= T < b:
            return s
    return None


def balanced(s, f, maxw):
    """One line if it fits; otherwise two lines of similar width, never leaving a lone short word."""
    if G.text_width(s, f) <= maxw:
        return [s]
    words = s.split()
    best, bi = None, 1
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        wa, wb = G.text_width(a, f), G.text_width(b, f)
        cost = max(wa, wb) + (400 if max(wa, wb) > maxw else 0)
        if best is None or cost < best:
            best, bi = cost, i
    return [" ".join(words[:bi]), " ".join(words[bi:])]


def draw_caption(arr, T, force_plate=False):
    s = caption_at(T)
    if not s:
        return
    f = G.font("jost-500", 60)
    lines = balanced(s, f, 860)
    # on bright backgrounds, lay a soft dark plate behind the caption
    y0 = G.CAP_Y - (len(lines) - 1) * 12
    y_top = int(y0 - 62)
    y_bot = int(y0 + (len(lines) - 1) * 70 + 22)
    region = arr[max(0, y_top): y_bot, 90: G.W - 90, :3]
    bright = float(region.mean()) / 255 if region.size else 0.0
    surf = G.canvas_of(arr)
    if bright > 0.18 or force_plate:
        with surf as c:
            wmax = max(G.text_width(ln, f) for ln in lines)
            c.drawRoundRect(skia.Rect.MakeLTRB(G.CX - wmax / 2 - 34, y_top - 6, G.CX + wmax / 2 + 34, y_bot + 12), 22, 22,
                            G.paint((0, 0, 0), 0.72 if force_plate else min(0.7, 0.35 + bright * 0.5), blur=4))
    # dark soft shadow, then crisp white
    with surf as c:
        y = y0
        for ln in lines:
            G.text(c, ln, G.CX, y + 2, f, color=(0, 0, 0), a=0.9, glow=9, glow_color=(0, 0, 0), track=0.5)
            G.text(c, ln, G.CX, y, f, color=(255, 255, 255), a=1.0, track=0.5)
            y += 70


NO_PUSH = {"s_sunrise", "s_memory", "s_stargate", "s_galaxy", "s_bone", "s_endcard", "s_glass",
           "s_starchild"}


def push_in(arr, k, amount=0.045, cy=860):
    """Slow camera push: scale the frame about (CX, cy) by 1 + amount * k."""
    z = 1 + amount * k
    if z <= 1.0005:
        return
    from PIL import Image
    w, h = G.W / z, G.H / z
    x0 = G.CX - w / 2
    y0 = cy - (cy / z)
    img = Image.fromarray(arr[..., :3]).resize((G.W, G.H), Image.BILINEAR, box=(x0, y0, x0 + w, y0 + h))
    arr[..., :3] = np.asarray(img)


def render_frame(T, idx=None, captions=True):
    arr = G.new()
    arr[..., :3] = 0
    fin = {}
    plate = False
    for a, b, fn, opt in SHOTS:
        if a <= T < b:
            f = _resolve(fn)
            if f is not None:
                f(arr, T - a, b - a, T)
                if f.__name__ not in NO_PUSH:
                    push_in(arr, G.ease((T - a) / (b - a)) * 0.6 + (T - a) / (b - a) * 0.4)
            fin = opt.get("finish", {})
            plate = opt.get("plate", False)
            break
    G.finish(arr, idx if idx is not None else int(T * FPS), **fin)
    if captions:
        draw_caption(arr, T, plate)
    return arr

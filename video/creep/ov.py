"""Lettering over the finished print, in comic hands: the narrator in yellow caption boxes, the host on her dripping
purple slab, everyone else in speech balloons placed by the edit (the assistant in an electric balloon). During the
reader's real night the narrator's boxes go plain: white type on black, no comic at all."""
import math

import skia

import comic as CO
import kit as K
from kit import paint
from timeline import TL

CAP_SIZE, MAX_W, CX, BASE = 50, 820, 525, 1500
BOXED = ("NAR", "HOST")


def _caps():
    from edit import EDIT
    cuts = [e[0] for e in EDIT]
    out = []
    for t0, t1, s, k in TL.captions():
        if TL.lines[k]["who"] not in BOXED:
            continue
        end = TL.lines[k]["end"]
        nxt = [x for x in cuts if end - 0.05 < x < t1]
        out.append((t0, min([t1] + nxt), s, k))
    return out


CAPS = _caps()


def _plain(T):
    from edit import PLAIN
    return any(a <= T < b for a, b in PLAIN)


def plain_box(c, s, x, y, size, a):
    f = K.font("rubik-500", size)
    lines = K.wrap_balanced(s, f, MAX_W - 60)
    lh = size * 1.18
    tw = max(f.measureText(ln) for ln in lines)
    y0 = y - lh * len(lines) - 18
    c.drawRect(skia.Rect.MakeLTRB(x - tw / 2 - 26, y0, x + tw / 2 + 26, y + 6), paint((0, 0, 0), 0.82 * a))
    for i, ln in enumerate(lines):
        K.text(c, ln, x, y0 + 12 + lh * (i + 0.8), size, "rubik-500", (236, 236, 236), tag="caption", a=a)


def telop(c, T):
    cap = next((cp for cp in CAPS if cp[0] <= T < cp[1]), None)
    if not cap:
        return
    t0, t1, s, key = cap
    who = TL.lines[key]["who"]
    a = min(1.0, (T - t0) / 0.06)
    k = K.pop(T, t0, 0.16, 0.04) or 1.0
    if who == "NAR" and _plain(T):
        plain_box(c, s, CX, BASE, CAP_SIZE * 0.95, a)
    elif who == "NAR":
        CO.caption_box(c, s, CX, BASE, MAX_W, CAP_SIZE, k=k, rot=-0.8, a=a)
    else:
        CO.host_box(c, s, CX, BASE - 12, MAX_W, CAP_SIZE, k=k, a=a)


_B = {}


def _balloon_spans():
    """Each balloon from just before its line until the first of: line end + 0.35 s, the next balloon, the next cut."""
    if not _B:
        from edit import BALLOONS, EDIT
        cuts = [e[0] for e in EDIT]
        starts = sorted((TL.lines[k]["start"] - 0.06, k) for k in BALLOONS)
        for n, (t0, key) in enumerate(starts):
            L = TL.lines[key]
            t1 = BALLOONS[key].get("until", L["end"] + 0.35)
            if n + 1 < len(starts):
                t1 = min(t1, starts[n + 1][0] - 0.04)
            nxt = [x for x in cuts if x > t0 + 0.1]
            if nxt and "until" not in BALLOONS[key]:
                t1 = min(t1, nxt[0])
            _B[key] = (t0, t1)
    return _B


def balloons(c, T):
    from edit import BALLOONS
    spans = _balloon_spans()
    for key, spec in BALLOONS.items():
        L = TL.lines[key]
        t0, t1 = spans[key]
        if not (t0 <= T < t1):
            continue
        k = K.pop(T, t0, 0.2, 0.25)
        a = min(1.0, (t1 - T) / 0.08)
        kind = spec.get("kind", "speech")
        if L["who"] == "MUSE":
            kind = "electric"
        jit = 0.0
        if spec.get("shake"):
            jit = math.sin(T * 60) * spec["shake"]
        CO.balloon(c, spec.get("text", L["spoken"]), spec["x"] + jit, spec["y"], tail=spec.get("tail"), size=spec.get("size", 48),
                   maxw=spec.get("maxw", 560), k=k, kind=kind, a=a, rot=spec.get("rot", 0.0), seed=len(key))


def overlay(arr, T):
    c = skia.Surface(arr).getCanvas()
    balloons(c, T)
    telop(c, T)

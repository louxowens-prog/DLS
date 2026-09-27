"""The compositor: picks the shot for time T, runs the iris and page-turn transitions, prints everything on 1970s
film, then pastes the narration on as a torn paper strip. Also keeps the lettering-collision lint."""
import math

import numpy as np
import skia

import hx
import sc1
import sc2
import sc3
import sc4
from edit import EDIT, FLIP, IRIS, shot_at
from script import AI
from timeline import FPS, TL

SHOTS = {}
for mod in (sc1, sc2, sc3, sc4):
    for name in dir(mod):
        if name.startswith("s_"):
            SHOTS[name[2:]] = getattr(mod, name)

HORROR = {"cold1", "cold2", "eaten", "neighbor", "visions", "clones_red", "burn", "count", "cateyes", "hold", "run"}
CAPS = [c for c in TL.captions() if TL.who(c[3]) != AI]
FREEZE = {"grade": sc1.GRADE_FREEZE, "nowarning": 0.0, "casezoom": 0.0}   # true freeze frames: the film stops too
CRASH = 0.18                                                              # horror cuts punch in from 1.55x
CAP_BOTTOM, CAP_SIZE, CAP_W = 1486, 52, 830
STRIPS = [(255, 196, 214), (190, 240, 216), (255, 214, 176), (196, 222, 255), (230, 206, 255)]


def shot_frame(i, T):
    t0, name, _ = EDIT[i]
    t1 = EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total + 1
    return np.ascontiguousarray(SHOTS[name](T, T - t0, t1 - t0))


def _flip(a, b, k):
    """A scrapbook page turning: the new page swings in from the right edge with a shadow along its fold."""
    k = hx.ease(k)
    x = int(hx.W * (1 - k))
    out = a.copy()
    if x < hx.W:
        out[:, x:] = b[:, x:]
        s0 = max(0, x - 40)
        shade = np.linspace(0.55, 1.0, x - s0)[None, :, None] if x > s0 else None
        if shade is not None:
            out[:, s0:x, :3] = (out[:, s0:x, :3] * shade).astype(np.uint8)
        out[:, x:min(hx.W, x + 6), :3] = hx.CREAM
    return out


def caption(arr, T, name):
    cap = next((c for c in CAPS if c[0] <= T < c[1]), None)
    if not cap:
        return
    t0, t1, s, key = cap
    idx = CAPS.index(cap)
    f = hx.font("shrikhand-400", CAP_SIZE)
    lines = hx.wrap(s, f, CAP_W - 80)
    lh = CAP_SIZE * 1.16
    bh = lh * len(lines) + 46
    bw = max(f.measureText(l) for l in lines) + 90
    y0 = CAP_BOTTOM - bh
    cx = 520
    horror = name in HORROR
    strip = (246, 236, 220) if horror else STRIPS[idx % len(STRIPS)]
    ink = hx.BLOOD if horror else hx.PLUM
    k = hx.pop(T, t0, 0.14, 0.06)
    c = skia.Surface(arr).getCanvas()
    c.save()
    c.translate(cx, y0 + bh / 2)
    c.rotate(-1.2 if idx % 2 else 1.0)
    c.scale(k, k)
    rng = np.random.default_rng(idx)
    pts = [(-bw / 2, -bh / 2)]
    for i in range(1, 12):                                              # torn ends
        pts.append((-bw / 2 + i * bw / 12 + rng.uniform(-4, 4), -bh / 2 + rng.uniform(-2, 2)))
    pts.append((bw / 2, -bh / 2))
    for i in range(1, 6):
        pts.append((bw / 2 + rng.uniform(-10, 8), -bh / 2 + i * bh / 6))
    pts.append((bw / 2, bh / 2))
    for i in range(11, 0, -1):
        pts.append((-bw / 2 + i * bw / 12 + rng.uniform(-4, 4), bh / 2 + rng.uniform(-2, 2)))
    pts.append((-bw / 2, bh / 2))
    for i in range(5, 0, -1):
        pts.append((-bw / 2 + rng.uniform(-8, 10), -bh / 2 + i * bh / 6))
    with hx.figure(c, border=5, fringe=None, shadow=(8, 10, 6, 0.5)) as F:
        F.poly(pts, strip)
    y = -bh / 2 + 23 + CAP_SIZE * 0.86
    for ln in lines:
        hx.text(c, ln, 0, y, CAP_SIZE, "shrikhand-400", ink, tag="caption")
        y += lh
    c.restore()


def render_frame(T, idx=None, captions=True, film=True):
    hx.TEXT.clear()
    idx = int(round(T * FPS)) if idx is None else idx
    i = shot_at(T)
    out = None
    for j in (i, i + 1):
        if j <= 0 or j >= len(EDIT):
            continue
        b0, name, tr = EDIT[j]
        if tr == "iris" and b0 - IRIS / 2 <= T < b0 + IRIS / 2:
            if T < b0:
                out = shot_frame(j - 1, T)
                hx.iris(out, 540, 860, (b0 - T) / (IRIS / 2) * 1150)
            else:
                out = shot_frame(j, T)
                hx.iris(out, 540, 860, (T - b0) / (IRIS / 2) * 1150)
            break
        if tr == "flip" and b0 <= T < b0 + FLIP:
            fa = shot_frame(j - 1, T)
            hx.TEXT.clear()
            fb = shot_frame(j, T)
            out = _flip(fa, fb, (T - b0) / FLIP)
            break
    if out is None:
        out = shot_frame(i, T)
    out = np.ascontiguousarray(out)
    t0, name, tr = EDIT[shot_at(T)]
    if name in HORROR and tr == "cut" and T - t0 < CRASH:
        out = hx.crash_zoom(out, 1 + 0.55 * (1 - (T - t0) / CRASH))
    fT, fidx = T, idx
    if name in FREEZE and T - t0 >= FREEZE[name]:
        fT = t0 + FREEZE[name] + 3 / FPS                                   # (past the flash frames)
        fidx = int(round(fT * FPS))
    if film:
        hx.film(out, fT, fidx, grain=1.0 if name != "end" else 0.8, fade=0.55 if name in HORROR else 1.0)
    if captions:
        caption(out, T, name)
    return out


def lint(boxes, ignore=("prop",)):
    """Pairs of lettering rectangles that overlap."""
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

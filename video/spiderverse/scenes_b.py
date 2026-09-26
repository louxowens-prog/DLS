"""Scenes 2: the jagged frontier, and the multiverse argues (noir skeptic, anime believer, the narrator between)."""
import math

import numpy as np
import skia

import bg
import cast
import sv
from common import E, S, W, talk
from cues import C
from scenes_a import DW, clock_face, impact, place
from script import ANIME, BOT, NAR, NOIR
from sv import CYAN, INK, MAG, PAPER, WHITE, YEL, bez, ease, paint, path, pop, ramp, twos

LIME, ORANGE, RED = sv.LIME, sv.ORANGE, sv.RED


# ------------------------------------------------------------------ 6. the jagged frontier

def _gold_panel(st, P, T):
    """Landscape panel (DW x 560): the gold medal side of the frontier."""
    c = P.c
    c.drawCircle(700, 330, 300, paint((255, 238, 160)))
    cast.bot(P, 720, 250, 0.72, T, medal=True, arms=((250, -40), (-70, 40)), bounce=0.6)
    sv.label(c, "MATH OLYMPIAD", 270, 150, 62, fname="bangers-400", color=INK, pen=P)
    sv.sfx(c, "GOLD!", 260, 330, 130, k=1.0, rot=-6, fill=YEL, fill2=ORANGE, dots=MAG, pen=P)


def _clock_panel(st, P, T):
    """Landscape panel (DW x 720): the clock side, with the scores."""
    c = P.c
    sv.label(c, "READING A CLOCK", DW / 2, 96, 66, fname="bangers-400", color=WHITE, pen=P)
    clock_face(c, 230, 400, 170, T, wobble=0.3 * math.sin(twos(T) * 7))
    kh = ease(ramp(T, C["half"] - 0.2, C["half"] + 0.4))
    kn = ease(ramp(T, C["ninety"] - 0.2, C["ninety"] + 0.4))
    for j, (name, val, k, col) in enumerate((("BEST AI", 50.1, kh, MAG), ("PEOPLE", 90.1, kn, LIME))):
        y = 250 + j * 190
        sv.label(c, name, 460, y - 16, 48, fname="bangers-400", color=WHITE, align="left", pen=P)
        c.drawRoundRect(skia.Rect.MakeLTRB(460, y, 960, y + 84), 20, 20, paint(WHITE))
        if k > 0:
            c.drawRoundRect(skia.Rect.MakeLTRB(460, y, 460 + 500 * val / 100 * k, y + 84), 20, 20, paint(col))
        c.drawRoundRect(skia.Rect.MakeLTRB(460, y, 960, y + 84), 20, 20, paint(INK, stroke=7))
        if k > 0.5:
            sv.label(c, f"{int(round(val))}%", 460 + 500 * val / 100 * k - 66, y + 60, 50, fname="bangers-400", color=INK, pen=P)
    sv.label(c, "ClockBench · Stanford AI Index 2026", DW / 2, 690, 32, fname="comic-neue-700", color=(220, 210, 255), tag="credit", pen=P)


def s_jagged(T, t, d):
    st = sv.Stage(PAPER)
    c = st.c
    P = st.pen()
    ts = C["scratch1"]
    tsplit = S("j2") - 0.2
    tj = S("j3") - 0.15
    if T < tsplit:
        # "Now, about that clock." - the stumped bot again, in a single panel
        q = place(st, P, (34, 40, 1046, 1340), (DW / 2, 600), lambda st_, P_, T_: (
            P_.c.drawCircle(DW / 2, 660, 560, paint((255, 238, 160))),
            clock_face(P_.c, 720, 330, 190, T_, wobble=0.3 * math.sin(twos(T_) * 7)),
            cast.bot(P_, 330, 760, 1.2, T_, look=(0.8, -0.9), expr="confused", arms=((210, 60), (-110, -40)), bounce=0.3)), T, (255, 214, 90))
        st.flush()
        sv.panel_border(c, q)
        if T >= ts:
            sv.sfx(c, "SKRRT!", 560, 1180, 170, k=pop(T, ts), rot=-7, fill=WHITE, fill2=CYAN, dots=MAG)
        return st.arr
    if T < tj:
        k = ease(ramp(T, tsplit, tsplit + 0.3))
        yb = 40 + 560 * k + 1300 * (1 - k)
        q1 = place(st, P, (34, 40, 1046, yb), (DW / 2, 280), _gold_panel, T, (255, 214, 90), dh=560)
        q2 = place(st, P, (34, yb + 22, 1046, 1340), (DW / 2, 360), _clock_panel, T, (40, 16, 90), dh=720)
        st.flush()
        sv.panel_border(c, q1)
        sv.panel_border(c, q2)
        return st.arr
    # the jagged frontier: peaks and valleys, spray-painted across the city night
    bg.city(st, camx=30 * t, T=T, train=False)
    st.flush()
    kline = ramp(T, tj, C["jagged"] + 0.2)
    pts = [(20, 980), (160, 520), (300, 1120), (420, 720), (540, 470), (660, 900), (780, 1150), (880, 660), (960, 480), (1060, 820)]
    labels = [(1, "MATH OLYMPIAD", -1), (2, "READING CLOCKS", 1), (4, "CODING", -1), (6, "ROUTINE PHYSICAL TASKS", 1), (8, "PhD SCIENCE", -1)]
    n = max(2, int(len(pts) * kline) + 1)
    seg = pts[:n]
    if kline < 1:
        a, b = pts[n - 1], pts[min(n, len(pts) - 1)]
        u = len(pts) * kline - (n - 1)
        seg = pts[:n] + [(a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)]
    # the frontier as a painted band: fill under the line with dots, ink the line itself
    under = [(seg[0][0], 1330)] + seg + [(seg[-1][0], 1330)]
    c.drawPath(path(under), paint((255, 70, 170), 0.55))
    st.shade("cyan").drawPath(path(under), paint(WHITE, 0.45))
    st.flush()
    sv.spray_stroke(c, seg, 26, YEL, seed=9)
    sv.ink(c, seg, 10, taper=(0.02, 0.02))
    for idx, name, side in labels:
        if idx >= n:
            continue
        x, y = pts[idx]
        ka = pop(T, tj + 0.25 * idx / len(pts) * 6)
        if side < 0:
            sv.label(c, name, min(max(x, 190), 890), y - 36, 40, fname="bangers-400", color=INK, bg=LIME, edge=INK, rot=-4, a=min(1.0, ka))
        else:
            sv.label(c, name, min(max(x, 240), 800), y + 74, 40, fname="bangers-400", color=WHITE, bg=RED, edge=INK, rot=3, a=min(1.0, ka))
    sv.tag_text(c, "JAGGED FRONTIER", 540, 250, 118, fill=CYAN, fill2=(0, 110, 200), glow=CYAN, k=pop(T, C["jagged"] - 0.1), seed=5)
    sv.label(c, "Stanford AI Index 2026", 540, 412, 34, fname="comic-neue-700", color=WHITE, tag="credit")
    kg, kb = pop(T, W("j3", "genius") - 0.05), pop(T, W("j3", "baffled") - 0.05)
    if kg:
        sv.sfx(c, "GENIUS!", 330, 820, 96, k=kg, rot=-8, fill=LIME, fill2=(40, 170, 60), dots=YEL)
    if kb:
        sv.sfx(c, "HUH?!", 800, 900, 96, k=kb, rot=7, fill=RED, fill2=(150, 0, 40), dots=YEL)
    return st.arr


# ------------------------------------------------------------------ 7. the noir dimension

def s_noir(T, t, d):
    st = sv.Stage((40, 40, 40))
    st.inks["dot"] = ((10, 10, 10), 14, 45, "dot")
    st.inks["hatch"] = ((10, 10, 10), 11, 35, "line")
    st.inks["xhatch"] = ((10, 10, 10), 11, -35, "line")
    bg.noir_alley(st, T)
    st.flush()
    P = st.pen()
    z = 1.0 + 0.05 * ease(t / d)
    P.save()
    P.translate(540, 900)
    P.scale(z)
    P.translate(-540, -900)
    cast.noir(P, 560, 860, 2.05, T, talk=talk(T, NOIR), look=-0.4)
    P.restore()
    st.flush()
    cast.rain(st.c, 0, 0, sv.W, sv.H, T, n=110)
    sv.desaturate(st.arr, 1.0)
    c = st.c
    k = pop(T, S("d1") - 0.1)
    sv.bubble(c, "It’s just autocomplete, kid.", 540, 260, tail=(560, 470), size=56, k=k, kind="box", fname="special-elite-400",
              maxw=700, fill=WHITE, edge=INK)
    return st.arr


# ------------------------------------------------------------------ 8. the anime dimension

def s_anime(T, t, d):
    st = sv.Stage((255, 200, 236))
    bg.anime_burst(st, T, cy=820)
    P = st.pen()
    fist = ease(ramp(twos(T), S("d2") - 0.05, S("d2") + 0.3))
    cast.anime(P, 520, 820, 1.95, T, talk=talk(T, ANIME), fist=fist)
    st.flush()
    c = st.c
    sv.bubble(c, "No way! It’s already a real mind!", 540, 230, tail=(470, 480), size=56, k=pop(T, S("d2") - 0.1), kind="shout",
              maxw=560, fill=WHITE)
    # katakana sound effect: 'don' (the dramatic boom of manga)
    sv.sfx(c, "ドン", 250, 1180, 190, k=pop(T, S("d2") + 0.05), rot=-10, fill=YEL, fill2=ORANGE, dots=MAG, fname="dela-gothic-kana-400",
           extrude=(12, 14))
    return st.arr


# ------------------------------------------------------------------ 9. the clash: three dimensions in one page

def s_clash(T, t, d):
    """Top: the noir panel and the anime panel, split on a diagonal. Bottom: the narrator in the main style,
    and then the cartoon AI dropping in between them."""
    st = sv.Stage(PAPER)
    c = st.c
    P = st.pen()
    qn = [(34, 40), (600, 40), (470, 700), (34, 700)]
    qa = [(624, 40), (1046, 40), (1046, 700), (494, 700)]
    qh = [(34, 722), (1046, 722), (1046, 1340), (34, 1340)]
    # noir panel (black and white)
    nst = sv.Stage((40, 40, 40))
    nst.inks["dot"] = ((10, 10, 10), 12, 45, "dot")
    nst.inks["xhatch"] = ((10, 10, 10), 10, -35, "line")
    nst.inks["hatch"] = ((10, 10, 10), 10, 35, "line")
    bg.noir_alley(nst, T)
    nst.flush()
    NP = nst.pen()
    cast.noir(NP, 290, 420, 1.15, T, talk=talk(T, NOIR), look=0.6)
    nst.flush()
    cast.rain(nst.c, 0, 0, 640, 720, T, n=50)
    sv.desaturate(nst.arr, 1.0)
    # anime panel
    ast = sv.Stage((255, 200, 236))
    bg.anime_burst(ast, T, cx=800, cy=380)
    AP = ast.pen()
    cast.anime(AP, 790, 430, 1.05, T, talk=talk(T, ANIME), fist=1.0 if T > S("d2") else 0.0)
    ast.flush()
    for q, src in ((qn, nst.arr), (qa, ast.arr)):
        m = np.zeros((sv.H, sv.W, 4), np.uint8)
        ms = skia.Surface(m)
        ms.getCanvas().drawPath(path(q), paint(WHITE))
        a = m[..., 3:4].astype(np.float32) / 255
        st.arr[..., :3] = (st.arr[..., :3] * (1 - a) + src[..., :3] * a).astype(np.uint8)
    # main panel: our world
    c.save()
    c.clipPath(path(qh), doAntiAlias=True)
    hst_col = (60, 20, 110)
    c.drawColor(sv.col(hst_col))
    st.shade("mag").drawPath(path(qh), paint(shader=sv.lin((0, 722), (0, 1340), [(255, 255, 255, 0.1), (255, 255, 255, 0.6)])))
    sv.speed_lines(c, 540, 1030, T, n=40, r0=300, r1=900, color=(90, 40, 150), seed=12, w=18)
    c.restore()
    P.save()
    P.clip(path(qh))
    tn = C["neither"]
    kb = ease(ramp(twos(T), C["new"] - 0.35, C["new"] + 0.05))            # the bot drops in (smear on the way)
    hx = 330 - 120 * kb
    cast.hero(P, hx, 950, 0.95, T, talk=talk(T), arms=cast.ARM["shrug" if T < C["new"] - 0.4 else "point"], expr="wow" if tn <= T < tn + 0.8 else "neutral",
              look=(0.9, -0.3))
    if kb > 0:
        by = 1040 - 700 * (1 - kb)
        if 0.1 < kb < 0.9:                                          # smear: a stretched body on the way down
            c.drawRoundRect(skia.Rect.MakeLTRB(700, by - 520, 900, by + 60), 60, 60, paint(sv.lighter(cast.B_BODY, 0.3)))
            for xx in (720, 800, 880):
                sv.ink(c, [(xx, by - 520), (xx, by - 200)], 6, taper=(0.3, 0.3))
        cast.bot(P, 800, by, 0.95, T, talk=talk(T, BOT), arms=((230, -40), (-50, 40)), bounce=0.5 if kb >= 1 else 0.0)
    P.restore()
    st.flush()
    for q in (qn, qa, qh):
        sv.panel_border(c, q)
    # the verdicts on each side
    if T >= W("d4", "autocomplete") - 0.1:
        k = pop(T, W("d4", "autocomplete") - 0.1)
        sv.sfx(c, "X", 470, 170, 190, k=k, rot=-8, fill=RED, fill2=(160, 0, 30), dots=None, extrude=(10, 12))
        sv.label(c, "JUST AUTOCOMPLETE?", 262, 650, 40, fname="bangers-400", color=INK, bg=WHITE, edge=INK, rot=-3, a=min(1.0, k))
    if T >= W("d4", "fully") - 0.1:
        k = pop(T, W("d4", "fully") - 0.1)
        sv.sfx(c, "X", 960, 170, 190, k=k, rot=8, fill=RED, fill2=(160, 0, 30), dots=None, extrude=(10, 12))
        sv.label(c, "A FULL HUMAN-LIKE MIND?", 790, 650, 40, fname="bangers-400", color=INK, bg=WHITE, edge=INK, rot=3, a=min(1.0, k))
    if tn <= T < tn + 1.3:
        sv.spidey(c, hx + 10 * 0.95, 950 - 40, 150, T, k=ease(ramp(T, tn, tn + 0.2)), seed=4)
        sv.sfx(c, "NEITHER!", 610, 800, 110, k=pop(T, tn), rot=-5, fill=YEL, fill2=ORANGE, dots=MAG)
    if T >= C["new"] + 0.15:
        sv.tag_text(c, "SOMETHING NEW", 760, 790, 84, fill=LIME, fill2=(40, 150, 60), glow=LIME, k=pop(T, C["new"] + 0.15), seed=3, rot=-4)
    return st.arr

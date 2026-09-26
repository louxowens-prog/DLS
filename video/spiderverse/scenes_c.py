"""Scenes 3: if AGI arrives (digital minds, copies, AI improving AI), the question changes, the road to
superintelligence, and the whole map in one breath."""
import math

import numpy as np
import skia

import bg
import cast
import sv
from common import E, S, W, talk
from cues import C
from scenes_a import DW, PIN_X, STATIONS, STX, SCOL, WALL_Y0, draw_road, impact, pin, place, road_y, rooftop
from script import BOT, NAR
from sv import CYAN, INK, MAG, PAPER, WHITE, YEL, bez, ease, paint, path, pop, ramp, twos

LIME, ORANGE, RED = sv.LIME, sv.ORANGE, sv.RED


def _goggles(c, x, y, s):
    for dx in (-40, 40):
        c.drawCircle(x + dx * s, y, 26 * s, paint(YEL))
        c.drawCircle(x + dx * s, y, 26 * s, paint(INK, stroke=7 * s))
        c.drawCircle(x + dx * s - 8 * s, y - 8 * s, 7 * s, paint(WHITE))


# ------------------------------------------------------------------ 10. AGI territory

def s_agi(T, t, d):
    st = sv.Stage((34, 90, 70))
    c = st.c
    P = st.pen()
    # a lab-blackboard world, still printed: green board, chalk scribbles, dots in the corners
    c.drawColor(sv.col((28, 70, 58)))
    st.inks["white"] = ((70, 140, 110), 20, 45, "dot")
    st.shade("white").drawRect(skia.Rect.MakeXYWH(0, 0, sv.W, sv.H), paint(shader=sv.rad((540, 760), 1100, [(255, 255, 255, 0.0), (255, 255, 255, 0.0), (255, 255, 255, 0.45)], [0, 0.6, 1])))
    rng = np.random.default_rng(3)
    for i in range(12):
        x, y = rng.uniform(60, 1000), rng.uniform(120, 1250)
        eq = ["E=mc²", "∑x", "f(x)", "∂/∂t", "p(a|b)", "O(n log n)", "x²+y²", "∫dx", "λ", "∇·F", "log(n)", "e^iπ"][i]
        f = sv.font("permanent-marker-400", rng.uniform(44, 70))
        c.drawString(eq, x - 60, y, f, paint((230, 245, 235), 0.28))
    st.flush()
    tg = W("a1", "gets") - 0.1
    k = ease(ramp(twos(T), tg, tg + 0.5))
    spin = 0.2 < k < 0.95
    if spin:                                                     # the change: multiples spinning into a new drawing
        for j, ang in enumerate((-30, 0, 30)):
            P.save()
            P.translate(540, 900)
            P.rotate(ang * (1 - k))
            P.translate(-540, -900)
            cast.bot(P, 540 + (j - 1) * 120 * (1 - k), 900, 1.5, T, bounce=0.0, coat=j == 1)
            P.restore()
    else:
        cast.bot(P, 540, 900, 1.5, T, coat=k >= 0.95, bounce=0.6, arms=((200, -40), (-60, 40)) if k >= 0.95 else ((200, 160), (-20, 20)))
        if k >= 0.95:
            _goggles(c, 540, 900 - 162 * 1.5, 1.5)
    st.flush()
    if T >= W("a1", "top") - 0.1:
        sv.sfx(c, "LEVEL UP!", 540, 330, 150, k=pop(T, W("a1", "top") - 0.1), rot=-6, fill=LIME, fill2=(30, 160, 70), dots=YEL)
    if T >= C["agi"] - 0.25:
        ks = pop(T, C["agi"] - 0.25)
        c.save()
        c.translate(820, 1180)
        c.rotate(4)
        c.scale(ks, ks)
        sv.ink(c, [(0, -60), (0, 200)], 22, color=(160, 170, 180), taper=(0.02, 0.02))
        sign = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-220, -190, 220, -40), 16, 16)
        c.drawRRect(sign.makeOffset(10, 12), paint(INK))
        c.drawRRect(sign, paint((20, 130, 70)))
        c.drawRRect(sign, paint(WHITE, stroke=8))
        f = sv.font("bangers-400", 60)
        for j, s_ in enumerate(("AGI", "TERRITORY")):
            c.drawString(s_, -f.measureText(s_) / 2, -125 + j * 62, f, paint(WHITE))
        sv.reg_local(c, -220, -190, 220, -40, "sign")
        c.restore()
    return st.arr


# ------------------------------------------------------------------ 11. it doesn't sleep

def _sleeper(P, x, y, s, T):
    """The narrator asleep: head on a pillow, eyes shut, blanket up to the chin (drawn rotated)."""
    c = P.c
    pil = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x - 190 * s, y - 70 * s, x + 170 * s, y + 90 * s), 60 * s, 60 * s)
    c.drawRRect(pil, paint(WHITE))
    c.drawRRect(pil, paint(INK, stroke=7))
    P.save()
    P.translate(x, y)
    P.rotate(-80)
    P.scale(s * 0.9)
    cast.hero_head(P, T, talk=0.0, blink=True, expr="neutral")
    P.restore()
    blanket = path([(x - 260 * s, y + 90 * s), (x + 340 * s, y + 40 * s), (x + 360 * s, y + 420 * s), (x - 260 * s, y + 420 * s)])
    P.fill(blanket, (80, 120, 230))
    for j in range(4):
        sv.ink(c, [(x - 200 * s + j * 140 * s, y + 110 * s), (x - 170 * s + j * 140 * s, y + 400 * s)], 5, color=(40, 60, 150))
    sv.outline(c, blanket, 7)


def s_nosleep(T, t, d):
    st = sv.Stage(PAPER)
    c = st.c
    P = st.pen()
    ql = [(34, 40), (540, 40), (500, 1340), (34, 1340)]
    qr = [(560, 40), (1046, 40), (1046, 1340), (520, 1340)]
    # backgrounds first (printed), then everything that sits on them
    st.inks["yel"] = ((255, 150, 40), 18, 15, "dot")
    P.save()
    P.clip(path(ql))
    c.drawColor(sv.col((24, 16, 70)))
    st.shade("mag").drawPath(path(ql), paint(shader=sv.lin((0, 40), (0, 1340), [(255, 255, 255, 0.0), (255, 255, 255, 0.45)])))
    P.restore()
    P.save()
    P.clip(path(qr))
    c.drawColor(sv.col((255, 214, 90)))
    st.shade("yel").drawPath(path(qr), paint(WHITE, 0.25))
    P.restore()
    st.flush()
    # left: night, a person asleep
    P.save()
    P.clip(path(ql))
    c.drawCircle(300, 260, 90, paint((255, 246, 224)))
    c.drawCircle(340, 230, 80, paint((24, 16, 70)))
    _sleeper(P, 270, 820, 0.95, T)
    P.restore()
    # right: the AI at work while day and night flip past (sun and moon as multiples)
    P.save()
    P.clip(path(qr))
    cyc = (twos(T) * 1.6) % 1.0
    for j in range(4):
        a = math.pi * (1.0 - ((cyc + j * 0.12) % 1.0))
        x, y = 800 + 260 * math.cos(a), 420 - 250 * math.sin(a)
        if j == 0:
            c.drawCircle(x, y, 60, paint(ORANGE))
            c.drawCircle(x, y, 60, paint(INK, stroke=6))
        else:
            c.drawCircle(x, y, 60, paint(ORANGE, 0.35 - j * 0.08))
    desk = path([(560, 1040), (1046, 1040), (1046, 1100), (560, 1100)])
    P.fill(desk, (140, 80, 40))
    sv.outline(c, desk, 6)
    c.drawRoundRect(skia.Rect.MakeLTRB(760, 900, 1000, 1040), 14, 14, paint(INK))
    c.drawRoundRect(skia.Rect.MakeLTRB(772, 912, 988, 1028), 10, 10, paint(CYAN))
    for j in range(5):
        sv.ink(c, [(790, 930 + j * 18), (790 + 120 + (j * 37) % 60, 930 + j * 18)], 5, color=WHITE, taper=(0.1, 0.1))
    cast.bot(P, 700, 830, 0.8, T, talk=talk(T, BOT), arms=((150, 40), (40, -40)), bounce=0.3)
    kc = ease(ramp(T, S("a3") - 0.15, S("a3") + 0.1))
    if kc > 0:
        for j, (bx, by) in enumerate(((930, 700), (640, 520), (940, 1220))):
            cast.bot(P, bx, by, 0.55 * kc, T + j * 0.3, talk=talk(T, BOT), arms=((230, -40), (-50, 40)), bounce=0.6, legs=False)
    P.restore()
    st.flush()
    sv.panel_border(c, ql)
    sv.panel_border(c, qr)
    sv.bubble(c, "Z z z", 380, 560, tail=(300, 700), size=52, kind="thought", maxw=200, k=1.0)
    if T >= S("a3") - 0.1:
        sv.bubble(c, "We never sleep!", 780, 330, tail=(720, 560), size=54, k=pop(T, S("a3") - 0.1), kind="shout", maxw=380)
    return st.arr


# ------------------------------------------------------------------ 12. thousands of copies

def s_copies(T, t, d):
    st = sv.Stage(PAPER)
    c = st.c
    P = st.pen()
    steps = [S("a4") - 0.12, W("a4", "Thousands") + 0.25, C["copies"], W("a4", "work"), W("a4", "once")]
    n = 1
    for i, ts in enumerate(steps):
        if twos(T) >= ts:
            n = [1, 2, 4, 8, 16][i]
    cols = {1: 1, 2: 1, 4: 2, 8: 2, 16: 4}[n]
    rows = n // cols
    x0, y0, x1, y1 = 34, 40, 1046, 1300
    gw, gh = (x1 - x0 - (cols - 1) * 16) / cols, (y1 - y0 - (rows - 1) * 16) / rows
    cells = []
    tasks = ["BOOK", "CODE", "LAB", "CHART", "MAP", "MUSIC", "MATH", "MAIL"]
    for r in range(rows):
        for q in range(cols):
            cx0 = x0 + q * (gw + 16)
            cy0 = y0 + r * (gh + 16)
            quad = [(cx0, cy0), (cx0 + gw, cy0), (cx0 + gw, cy0 + gh), (cx0, cy0 + gh)]
            cells.append(quad)
            i = r * cols + q
            P.save()
            P.clip(path(quad))
            c.drawColor(sv.col([(255, 214, 90), (120, 230, 255), (255, 150, 200), (180, 255, 150)][i % 4]))
            st.shade("dot").drawPath(path(quad), paint(WHITE, 0.12))
            P.restore()
    st.flush()
    for i, quad in enumerate(cells):
        cx0, cy0 = quad[0]
        P.save()
        P.clip(path(quad))
        s = min(gw / 520, gh / 700) * 1.1
        bx, by = cx0 + gw / 2, cy0 + gh * 0.52
        cast.bot(P, bx, by, s, T + i * 0.17, arms=((150, 40), (40, -40)), bounce=0.5, legs=gh > 300)
        f = sv.font("bangers-400", max(22, 60 * s))
        sv.label(c, tasks[i % len(tasks)], cx0 + 16 + f.measureText(tasks[i % len(tasks)]) / 2, cy0 + 16 + 60 * s,
                 max(22, 60 * s), fname="bangers-400", color=INK, bg=WHITE, edge=INK, pad=8, tag="celllabel")
        P.restore()
    for quad in cells:
        sv.panel_border(c, quad, 8 if n > 4 else 12)
    # sharing: links between the copies with packets travelling along them
    if T >= C["share"] - 0.1 and n >= 8:
        ks = ease(ramp(T, C["share"] - 0.1, C["share"] + 0.4))
        ctrs = [((q[0][0] + q[2][0]) / 2, (q[0][1] + q[2][1]) / 2) for q in cells]
        for i in range(len(ctrs)):
            for j in (i + 1, i + cols):
                if j < len(ctrs) and (j != i + 1 or (i + 1) % cols):
                    a, b = ctrs[i], ctrs[j]
                    sv.ink(c, [a, (a[0] + (b[0] - a[0]) * ks, a[1] + (b[1] - a[1]) * ks)], 10, color=CYAN, taper=(0.1, 0.1))
                    u = (twos(T) * 1.5 + i * 0.13) % 1.0
                    if ks >= 1:
                        c.drawCircle(a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, 12, paint(WHITE))
                        c.drawCircle(a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, 12, paint(INK, stroke=4))
        sv.sfx(c, "SHARE!", 540, 180, 110, k=pop(T, C["share"]), rot=-5, fill=CYAN, fill2=(0, 120, 200), dots=WHITE)
    if T >= C["scale"] - 0.1:
        kk = ease(ramp(T, C["scale"] - 0.1, C["scale"] + 0.8))
        m = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(120, 1236, 960, 1326), 20, 20)
        c.drawRRect(m.makeOffset(8, 8), paint(INK))
        c.drawRRect(m, paint(WHITE))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(120, 1236, 120 + 840 * (0.2 + 0.8 * kk), 1326), 20, 20), paint(MAG))
        c.drawRRect(m, paint(INK, stroke=7))
        sv.label(c, "MORE COMPUTE", 540, 1301, 56, fname="bangers-400", color=INK)
        sv.sfx(c, "POWER UP!", 640, 1140, 96, k=pop(T, C["scale"] + 0.2), rot=6, fill=YEL, fill2=ORANGE, dots=MAG)
    return st.arr


# ------------------------------------------------------------------ 13. AI improving AI

def s_evolve(T, t, d):
    st = sv.Stage((30, 14, 60))
    c = st.c
    P = st.pen()
    tcode = W("a5", "Google's") - 0.3
    if T < tcode:
        # copies on a scaffold, building a bigger AI; a loop arrow says who is building whom
        st.shade("mag").drawRect(skia.Rect.MakeXYWH(0, 0, sv.W, sv.H), paint(shader=sv.lin((0, 200), (0, 1400), [(255, 255, 255, 0.0), (255, 255, 255, 0.5)])))
        st.flush()
        kb = ease(ramp(T, S("a5") - 0.1, tcode))
        # the big bot, assembled bottom-up (a clip reveals it)
        P.save()
        P.clip(path([(0, 1340 - 1100 * kb), (sv.W, 1340 - 1100 * kb), (sv.W, 1400), (0, 1400)]))
        cast.bot(P, 540, 760, 2.1, T, bounce=0.0, legs=True)
        P.restore()
        for yy in (560, 880, 1200):                                  # scaffold
            sv.ink(c, [(120, yy), (960, yy)], 16, color=(200, 180, 120), taper=(0.02, 0.02))
        for xx in (120, 960):
            sv.ink(c, [(xx, 300), (xx, 1340)], 16, color=(200, 180, 120), taper=(0.02, 0.02))
        for j, (bx, by, ph) in enumerate(((220, 500, 0), (870, 820, 1), (250, 1140, 2), (860, 500, 3))):
            cast.bot(P, bx, by, 0.4, T + ph * 0.2, arms=((200, -60), (-20, 40)), bounce=0.8, legs=True)
            sv.sfx(c, "TAP", bx + 70, by - 110, 44, k=pop(T, S("a5") + 0.3 * j), rot=10 - 5 * j, fill=WHITE, fill2=YEL, dots=None, extrude=(4, 5))
        st.flush()
        # the loop: AI -> AI
        ang = twos(T) * 90
        c.save()
        c.translate(540, 220)
        c.rotate(ang)
        for k_ in range(2):
            c.save()
            c.rotate(k_ * 180)
            arc = [(110 * math.cos(math.radians(a)), 70 * math.sin(math.radians(a))) for a in range(20, 150, 10)]
            sv.ink(c, arc, 16, color=LIME, taper=(0.1, 0.4))
            c.drawPath(path([(arc[-1][0] - 10, arc[-1][1] - 26), (arc[-1][0] - 40, arc[-1][1] + 10), (arc[-1][0] + 18, arc[-1][1] + 14)]), paint(LIME))
            c.restore()
        c.restore()
        sv.label(c, "AI IMPROVING AI", 540, 240, 60, fname="bangers-400", color=WHITE, bg=INK, pad=10)
        return st.arr
    # the real example: a monitor of training code, one piece of it made faster
    c.drawColor(sv.col((20, 10, 40)))
    st.shade("cyan").drawRect(skia.Rect.MakeXYWH(0, 0, sv.W, sv.H), paint(shader=sv.rad((540, 700), 1000, [(255, 255, 255, 0.0), (255, 255, 255, 0.45)])))
    st.flush()
    mon = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(80, 300, 1000, 980), 30, 30)
    c.drawRRect(mon.makeOffset(12, 14), paint(INK))
    c.drawRRect(mon, paint((60, 60, 80)))
    scr = skia.Rect.MakeLTRB(110, 330, 970, 950)
    c.drawRect(scr, paint((10, 16, 30)))
    rng = np.random.default_rng(8)
    hl = int(twos(T) * 12) % 14
    for j in range(14):
        y = 370 + j * 40
        ind = [0, 1, 1, 2, 2, 1, 0, 1, 2, 3, 2, 1, 1, 0][j]
        w = rng.uniform(200, 560)
        col_ = [CYAN, MAG, YEL, LIME, WHITE][j % 5]
        c.drawRoundRect(skia.Rect.MakeXYWH(140 + ind * 40, y - 12, w, 20), 8, 8, paint(col_, 0.85))
    kh = ramp(T, W("a5", "key") - 0.2, W("a5", "key") + 0.2)
    if kh > 0:
        c.drawRect(skia.Rect.MakeLTRB(120, 590, 960, 650), paint(YEL, 0.35 * kh))
        c.drawRect(skia.Rect.MakeLTRB(120, 590, 960, 650), paint(YEL, kh, stroke=6))
    c.drawRRect(mon, paint(INK, stroke=10))
    sv.label(c, "GEMINI TRAINING CODE", 540, 280, 58, fname="bangers-400", color=WHITE)
    if T >= C["evolve"] - 0.1:
        sv.label(c, "ALPHAEVOLVE · GOOGLE DEEPMIND", 540, 1060, 48, fname="bangers-400", color=INK, bg=CYAN, edge=INK, rot=-2,
                 a=min(1.0, pop(T, C["evolve"] - 0.1)))
    if T >= W("a5", "sped") - 0.05:
        sv.sfx(c, "23% FASTER!", 540, 700, 150, k=pop(T, W("a5", "sped") - 0.05), rot=-6, fill=LIME, fill2=(30, 160, 70), dots=YEL)
        sv.label(c, "one key kernel · ~1% less total training time (2025)", 540, 1150, 32, fname="comic-neue-700", color=WHITE, tag="credit")
    return st.arr


# ------------------------------------------------------------------ 14. the question changes

def _brain(c, x, y, s, col=(255, 150, 190)):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    b = skia.Path()
    for bx, by, r in ((-40, -10, 44), (0, -30, 48), (40, -12, 44), (-20, 22, 40), (26, 24, 40)):
        b.addCircle(bx, by, r)
    b = skia.Op(b, skia.Path(), skia.PathOp.kUnion_PathOp) or b
    c.drawPath(b, paint(col))
    c.drawPath(b, paint(INK, stroke=7))
    for p in (bez((-50, -10), (-20, -40), (0, -8)), bez((10, -40), (30, -10), (60, -20)), bez((-30, 30), (0, 10), (30, 34))):
        sv.ink(c, p, 5, taper=(0.3, 0.3))
    c.restore()


def _head_profile(c, x, y, s, col=INK):
    """A human head in profile (facing right): skull, brow, nose, lips, chin, neck."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    hp = path(np.vstack([bez((-40, 230), (-60, 150), (-120, 110)), bez((-120, 110), (-170, 40), (-150, -80)),
                         bez((-150, -80), (-120, -200), (20, -200)), bez((20, -200), (130, -190), (140, -80)),
                         [(146, -40), (150, -10), (182, 30), (150, 44), (158, 66), (148, 80), (154, 98), (140, 108)],
                         bez((140, 108), (130, 150), (70, 150)), [(60, 230)]]))
    c.drawPath(hp, paint(col))
    c.restore()


def s_question(T, t, d):
    tb = C["brain"]
    if tb <= T < tb + 3 / 24:                                          # impact: one head, many minds
        st = sv.Stage(MAG)
        sv.impact_bg(st.c, MAG, 540, 800, T)
        _head_profile(st.c, 430, 900, 2.2)
        for j in range(8):
            a = math.radians(-160 + j * 20)
            _brain(st.c, 470 + 420 * math.cos(a), 700 + 420 * math.sin(a) * 0.9, 0.9, WHITE)
        _brain(st.c, 470, 720, 1.4, WHITE)
        sv.sfx(st.c, "BOOM!", 540, 1170, 190, rot=-6, fill=WHITE, fill2=YEL, dots=MAG)
        return st.arr
    st = sv.Stage()
    bg.city(st, camx=25 * t, T=T, train=False)
    rooftop(st, T, y=1340)
    c = st.c
    # a chunk of wall behind her, where the old question gets sprayed and crossed out
    P = st.pen()
    wallq = [(470, 250), (1060, 230), (1060, 860), (470, 880)]
    P.save()
    P.clip(path(wallq))
    sv.bricks(c, 470, 220, 1080, 900, bw=120, bh=46, col_=(122, 36, 116), mortar=(58, 14, 64))
    P.sh["hatch"].drawPath(path(wallq), paint(WHITE, 0.3))
    P.restore()
    st.flush()
    sv.outline(c, path(wallq), 8)
    tq = W("a7", "can") - 0.1
    if T >= tq:
        k = ramp(T, tq, W("a7", "us?") + 0.1)
        sv.tag_text(c, "AS SMART", 765, 430, 110, fill=WHITE, fill2=(200, 200, 230), rot=-4, prog=min(1.0, k * 2), seed=11)
        sv.tag_text(c, "AS US?", 765, 600, 110, fill=WHITE, fill2=(200, 200, 230), rot=-4, prog=max(0.0, min(1.0, k * 2 - 1)), seed=12)
    tx = W("a7", "But:") - 0.05
    if T >= tx:
        kx = ramp(T, tx, tx + 0.35)
        sv.spray_stroke(c, [(520, 330), (520 + 500 * kx, 330 + 420 * kx)], 42, RED, seed=5)
        if kx > 0.5:
            sv.spray_stroke(c, [(1020, 330), (1020 - 500 * (kx - 0.5) * 2, 330 + 420 * (kx - 0.5) * 2)], 42, RED, seed=6)
        sv.sfx(c, "PSSHT!", 800, 960, 100, k=pop(T, tx), rot=6, fill=WHITE, fill2=RED, dots=None, extrude=(6, 7))
    # the narrator, close: pop-up depth over the off-register city
    kp = ease(ramp(T, W("a7", "what") - 0.2, W("a7", "what") + 0.3))
    s = 1.35 + 0.35 * kp
    cast.hero(P, 330 + 60 * kp, 720 + 120 * kp, s, T, talk=talk(T), arms=cast.ARM["idle" if T < tx else "open"], look=(0.9 if T < tx else 0.2, -0.1),
              expr="wow" if T > W("a7", "intelligence") else "neutral")
    st.flush()
    if T >= W("a7", "intelligence") - 0.1 and T < tb + 1.5:
        sv.spidey(c, 390 + 60 * kp, 680 + 120 * kp, 160 * s / 1.35, T, k=ease(ramp(T, W("a7", "intelligence") - 0.1, W("a7", "intelligence") + 0.2)),
                  seed=7, n=11)
    if T >= tb + 3 / 24:                                              # after the hit: brains multiplying out of one head
        kb = ease(ramp(T, tb + 0.12, tb + 0.9))
        for j in range(7):
            a = math.radians(-150 + j * 20)
            _brain(c, 760 + 300 * kb * math.cos(a), 520 + 300 * kb * math.sin(a) * 0.8, 0.55, [MAG, CYAN, YEL, LIME][j % 4])
    return st.arr


# ------------------------------------------------------------------ 15. the road on to superintelligence

ROUTES = [("BIGGER SCALE", "scale"), ("NEW ALGORITHMS", "algo"), ("AI IMPROVING AI", "loop"), ("TEAMS OF AGENTS", "team")]


def _route_icon(P, kind, x, y, s, T):
    c = P.c
    if kind == "scale":
        for j, sc in enumerate((0.35, 0.55, 0.8)):
            cast.bot(P, x - 150 * s + j * 150 * s, y + 60 * s - sc * 60 * s, sc * s, T, bounce=0.2, legs=False)
    elif kind == "algo":
        c.drawCircle(x, y - 20 * s, 110 * s, paint(YEL))
        c.drawCircle(x, y - 20 * s, 110 * s, paint(INK, stroke=9 * s))
        c.drawRect(skia.Rect.MakeLTRB(x - 45 * s, y + 88 * s, x + 45 * s, y + 150 * s), paint(INK))
        for j in range(8):
            a = j * math.pi / 4 + twos(T)
            sv.ink(c, [(x + 140 * s * math.cos(a), y - 20 * s + 140 * s * math.sin(a)), (x + 190 * s * math.cos(a), y - 20 * s + 190 * s * math.sin(a))], 10 * s)
    elif kind == "loop":
        cast.bot(P, x - 110 * s, y + 20 * s, 0.5 * s, T, bounce=0.3, legs=False)
        cast.bot(P, x + 110 * s, y + 20 * s, 0.62 * s, T, bounce=0.3, legs=False, hue=(160, 110, 255))
        arc = [(x + 150 * s * math.cos(math.radians(a)), y - 120 * s + 60 * s * math.sin(math.radians(a))) for a in range(200, 340, 10)]
        sv.ink(c, arc, 14 * s, color=LIME, taper=(0.1, 0.4))
    else:
        for j in range(9):
            cast.bot(P, x - 200 * s + (j % 5) * 100 * s + (50 * s if j >= 5 else 0), y - 40 * s + (j // 5) * 110 * s, 0.26 * s, T + j * 0.2,
                     bounce=0.8, legs=False)


def s_routes(T, t, d):
    st = sv.Stage()
    c = st.c
    P = st.pen()
    # the wall again, from AGI on to superintelligence
    kpan = ease(ramp(T, S("x1") - 0.2, C["asi_road"] + 0.4))
    cwx = STX[7] - 200 + (STX[8] - STX[7] + 200) * kpan
    bg.city(st, camx=(cwx - 540) * 0.6, T=T, train=False)
    P.save()
    P.translate(540, 860)
    P.translate(-cwx, -(860 - WALL_Y0))
    c.drawImage(bg._cached("wall", bg._paint_wall), 0, 0)
    draw_road(c, T, [1.0] * 9)
    pin(c, PIN_X, road_y(PIN_X) - 50, 1.0)
    P.restore()
    st.flush()
    if T >= C["asi_road"] - 0.1 and T < S("x2") + 0.2:
        sv.sfx(c, "WHOA!", 300, 360, 120, k=pop(T, C["asi_road"] - 0.1), rot=-8, fill=WHITE, fill2=CYAN, dots=MAG)
    # the four routes, pasted over the wall as a comic page
    tp = S("x2") - 0.1
    if T >= tp:
        kp = ease(ramp(T, tp, tp + 0.3))
        hdr = skia.Rect.MakeLTRB(60, 210, 1020, 330)
        c.save()
        c.translate(0, -200 * (1 - kp))
        c.drawRect(hdr.makeOffset(10, 12), paint(INK))
        c.drawRect(hdr, paint(WHITE))
        c.drawRect(hdr, paint(INK, stroke=8))
        sv.label(c, "GOOGLE DEEPMIND · JUNE 2026", 540, 262, 48, fname="bangers-400", color=INK)
        sv.label(c, "4 ROUTES FROM AGI TO SUPERINTELLIGENCE", 540, 312, 36, fname="bangers-400", color=MAG)
        c.restore()
        quads = [(60, 360, 530, 820), (550, 360, 1020, 820), (60, 840, 530, 1300), (550, 840, 1020, 1300)]
        for i, ((name, kind), q, tr) in enumerate(zip(ROUTES, quads, C["routes"])):
            if T < tr - 0.15:
                continue
            k = pop(T, tr - 0.15, 0.3)
            x0, y0, x1, y1 = q
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            P.save()
            P.translate(cx, cy)
            P.rotate([-3, 2, 3, -2][i] * (1 + (k - 1) * 3))
            P.scale(k)
            P.translate(-cx, -cy)
            r = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
            c.drawRect(skia.Rect.MakeLTRB(x0 + 10, y0 + 12, x1 + 10, y1 + 12), paint(INK))
            P.save()
            P.clip(path(r))
            c.drawColor(sv.col([(255, 214, 90), (120, 230, 255), (180, 255, 150), (255, 150, 200)][i]))
            st.shade("dot").drawPath(path(r), paint(WHITE, 0.14))
            _route_icon(P, kind, cx, cy + 20, 0.9, T)
            sv.label(c, name, cx, y1 - 36, 52, fname="bangers-400", color=INK, bg=WHITE, edge=INK, pad=10, pen=P)
            sv.label(c, str(i + 1), x0 + 44, y0 + 64, 60, fname="bangers-400", color=WHITE, bg=INK, pad=10, pen=P)
            P.restore()
            sv.panel_border(c, r, 10)
            P.restore()
        st.flush()
    return st.arr


# ------------------------------------------------------------------ 16. the bar: bigger than large organisations

def _towers(c, T, k):
    rng = np.random.default_rng(12)
    x = 20
    while x < 1060:
        w = rng.uniform(150, 240)
        h = rng.uniform(420, 760)
        top = 1340 - h
        c.drawRect(skia.Rect.MakeLTRB(x, top, x + w, 1340), paint((70, 60, 110)))
        for wy in np.arange(top + 30, 1320, 56):
            for wx in np.arange(x + 16, x + w - 30, 44):
                c.drawRect(skia.Rect.MakeXYWH(wx, wy, 30, 40), paint((255, 226, 150)))
                c.drawCircle(wx + 15, wy + 16, 7, paint(INK))
                c.drawRect(skia.Rect.MakeXYWH(wx + 7, wy + 24, 16, 16), paint(INK))
        c.drawRect(skia.Rect.MakeLTRB(x, top, x + w, 1340), paint(INK, stroke=6))
        x += w + rng.uniform(10, 30)


def s_bar(T, t, d):
    tb = C["boom"]
    if tb <= T < tb + 3 / 24:
        return impact(T, CYAN, lambda P: cast.bot(P, 540, 820, 3.0, T, bounce=0.0, arms=((230, -40), (-50, 40))),
                      cx=540, cy=700, word="BOOM!", wx=540, wy=1260, wsize=220)
    st = sv.Stage(sv.NIGHT)
    bg.city(st, camx=20 * t, T=T, train=False, mid=False)
    c = st.c
    P = st.pen()
    ks = ease(ramp(twos(T), S("x3") + 0.2, C["orgs"] + 0.4))
    # the swarm: many small copies adding up to one giant silhouette rising behind the towers
    if ks > 0:
        big = 2.15
        oy = 1330 - 254 * big + 900 * (1 - ks)
        lay = sv.silhouette(lambda Q: cast.bot(Q, 540, oy, big, T, bounce=0.0, arms=((230, -40), (-50, 40))), (40, 200, 255))
        sv.over(st.arr, lay)
        rng = np.random.default_rng(3)
        a = lay[..., 3]
        ys, xs = np.nonzero(a[::40, ::40])
        for yy, xx in zip(ys[::2], xs[::2]):
            cast.bot(P, xx * 40 + rng.uniform(-8, 8), yy * 40 + rng.uniform(-8, 8), 0.1, T + (xx + yy) * 0.05, bounce=1.0, legs=False)
    c.drawRect(skia.Rect.MakeLTRB(0, 1330, sv.W, sv.H), paint((26, 10, 44)))
    _towers(c, T, 1.0)
    st.shade("dot").drawRect(skia.Rect.MakeLTRB(0, 600, sv.W, 1340), paint(shader=sv.lin((0, 600), (0, 1340), [(255, 255, 255, 0.0), (255, 255, 255, 0.4)])))
    st.flush()
    sv.label(c, "LARGE ORGANIZATIONS OF HUMANS", 540, 1300, 44, fname="bangers-400", color=INK, bg=YEL, edge=INK)
    if T >= tb + 3 / 24:
        sv.tag_text(c, "THE REAL THRESHOLD", 540, 600, 96, fill=YEL, fill2=ORANGE, glow=YEL, k=pop(T, tb + 0.15), seed=8, rot=-4)
    return st.arr


# ------------------------------------------------------------------ 17. the whole map in one breath

SUMMARY = [
    ("AI", "ALREADY INVENTED", LIME),
    ("AGI", "MAYBE ENTERING IT · DEPENDS HOW YOU DEFINE IT", CYAN),
    ("NOT SHOWN YET", "", RED),
    ("CONSCIOUS?", "NO ESTABLISHED EVIDENCE", (180, 120, 255)),
    ("MISSING PIECE", "GENERALIZATION", YEL),
]


def _sum_panel(st, P, i, T):
    c = P.c
    head, sub, col_ = SUMMARY[i]
    sv.label(c, head, DW / 2, 120, 96, fname="bangers-400", color=INK, bg=col_, edge=INK, pad=16, pen=P, rot=-2)
    if i == 0:
        cast.bot(P, 300, 420, 0.65, T, arms=((250, -40), (-70, 40)), bounce=0.6)
        sv.sfx(c, "YES!", 700, 360, 150, rot=-8, fill=LIME, fill2=(30, 160, 70), dots=YEL, pen=P)
        sv.label(c, sub, 700, 520, 58, fname="bangers-400", color=INK, pen=P)
    elif i == 1:
        xs = np.linspace(60, 960, 40)
        for j, (dy, cc) in enumerate(((-18, MAG), (0, YEL), (18, CYAN))):
            sv.spray_stroke(c, [(x, 420 + dy + 20 * math.sin(x / 150)) for x in xs[:28]], 22, cc, seed=j)
        for x in np.linspace(xs[28], 960, 8):
            sv.ink(c, [(x, 420), (x + 30, 420)], 8, color=INK)
        c.drawCircle(820, 420, 60, paint(WHITE))
        c.drawCircle(820, 420, 60, paint(INK, stroke=7))
        sv.label(c, "AGI", 820, 440, 56, fname="bangers-400", color=INK, pen=P)
        pin(c, 700, 400, 1.0, s=0.55)
        sv.label(c, "MAYBE ENTERING IT", DW / 2, 560, 58, fname="bangers-400", color=INK, pen=P)
        sv.label(c, "depends how you define it", DW / 2, 612, 38, fname="comic-neue-700", color=INK, pen=P)
    elif i == 2:
        items = [("COMPETENT EVERYWHERE", W("f4", "competent")), ("KEEPS LEARNING", W("f4", "keeps")), ("RELIABLE ON ITS OWN", W("f4", "works"))]
        for j, (txt, tw) in enumerate(items):
            y = 260 + j * 120
            c.drawRect(skia.Rect.MakeXYWH(90, y - 50, 70, 70), paint(WHITE))
            c.drawRect(skia.Rect.MakeXYWH(90, y - 50, 70, 70), paint(INK, stroke=7))
            if T >= tw:
                sv.label(c, txt, 190, y, 56, fname="bangers-400", color=INK, align="left", pen=P)
                sv.sfx(c, "?", 125, y - 12, 80, k=pop(T, tw), rot=8, fill=RED, fill2=(160, 0, 30), dots=None, extrude=(4, 5))
    elif i == 3:
        cast.bot(P, 280, 440, 0.62, T, expr="confused", bounce=0.2, look=(0.6, -0.6))
        sv.bubble(c, "?", 360, 230, tail=(300, 300), size=70, kind="thought", maxw=120)
        sv.label(c, "NO ESTABLISHED", 700, 400, 62, fname="bangers-400", color=INK, pen=P)
        sv.label(c, "EVIDENCE", 700, 470, 62, fname="bangers-400", color=INK, pen=P)
    else:
        cast.hero(P, 200, 380, 0.62, T, talk=talk(T), arms=cast.ARM["spray"], spray=YEL if T < C["general"] + 1.0 else None,
                  expr="wow", look=(0.9, -0.2))
        k = ramp(T, C["general"] - 0.1, C["general"] + 0.7)
        sv.tag_text(c, "GENERALIZATION", 620, 330, 84, fill=YEL, fill2=ORANGE, glow=YEL, prog=k, seed=2, rot=-5)
        if T >= W("f6", "learning") - 0.1:
            sv.label(c, "learning what it has never seen", 620, 480, 40, fname="comic-neue-700", color=INK, bg=WHITE, edge=INK, pen=P)


def s_summary(T, t, d):
    """A vertical 'webtoon' scroll of five panels, two on screen at a time; the camera glides down as each line lands."""
    import scenes_a
    st = sv.Stage(PAPER)
    c = st.c
    P = st.pen()
    ph, gap, y_first = 620, 34, 60
    starts = [S("f2") - 0.3, S("f3") - 0.3, S("f4") - 0.3, S("f5") - 0.3, S("f6") - 0.3]
    if T < starts[0]:
        c.drawColor(sv.col((255, 90, 170)))
        sv.speed_lines(c, 540, 700, T, n=60, r0=360, color=WHITE, seed=21, w=16)
        st.shade("mag").drawRect(skia.Rect.MakeXYWH(0, 0, sv.W, sv.H), paint(shader=sv.rad((540, 760), 900, [(255, 255, 255, 0.0), (255, 255, 255, 0.5)])))
        st.inks["mag"] = ((190, 20, 110), 18, 15, "dot")
        st.flush()
        cast.hero(P, 540, 760, 1.3, T, talk=talk(T), arms=cast.ARM["open"], expr="wow", look=(0.0, 0.0))
        st.flush()
        sv.tag_text(c, "THE WHOLE MAP", 540, 250, 120, fill=YEL, fill2=ORANGE, glow=YEL, k=pop(T, S("f1")), seed=4)
        if T < C["scratch2"] + 0.5:
            sv.sfx(c, "SKRRT!", 540, 1180, 170, k=pop(T, C["scratch2"]), rot=-6, fill=WHITE, fill2=CYAN, dots=MAG)
        return st.arr
    scroll = 0.0
    for j in range(2, 5):
        scroll += (ph + gap) * ease(ramp(T, starts[j], starts[j] + 0.45))
    P.save()
    P.translate(0, -scroll)
    quads = []
    xf5 = None
    for i in range(5):
        y0 = y_first + i * (ph + gap)
        if T < starts[i] or y0 + ph - scroll < -40:
            continue
        kin = ease(ramp(T, starts[i], starts[i] + 0.3))
        dx = 1100 * (1 - kin) * (1 if i % 2 else -1)
        r = (34 + dx, y0, 1046 + dx, y0 + ph)
        quads.append((place(st, P, r, (DW / 2, 350), lambda st_, P_, T_, i=i: _sum_panel(st_, P_, i, T_), T,
                            [(255, 250, 235), (230, 248, 255), (255, 236, 236), (245, 236, 255), (255, 246, 214)][i], dh=700), i))
        if i == 4:
            xf5 = scenes_a.LAST_PLACE[0]
    P.restore()
    st.flush()
    for q, i in quads:
        sv.panel_border(c, [(x, y - scroll) for x, y in q])
    if xf5 is not None and C["general"] - 0.1 <= T < C["general"] + 1.3:
        tx, ty, s_ = xf5
        sv.spidey(c, tx + 204 * s_, ty + 350 * s_ - scroll, 118 * s_, T, k=ease(ramp(T, C["general"] - 0.1, C["general"] + 0.1)), seed=9)
    return st.arr


# ------------------------------------------------------------------ 18. where would you put the pin?

def s_outro(T, t, d):
    st = sv.Stage()
    c = st.c
    P = st.pen()
    cwx = PIN_X - 60
    bg.city(st, camx=(cwx - 540) * 0.6 + 30 * t, T=T, train=False)
    P.save()
    P.translate(540, 860)
    z = 1.0 + 0.1 * ease(t / d)
    P.scale(z)
    P.translate(-cwx, -(860 - WALL_Y0))
    c.drawImage(bg._cached("wall", bg._paint_wall), 0, 0)
    draw_road(c, T, [1.0] * 9, labels=False)
    P.restore()
    st.flush()
    # she holds the pin out to the viewer: huge in the foreground
    cast.hero(P, 300, 820, 1.25, T, talk=talk(T), arms=cast.ARM["point"], expr="neutral", look=(0.1, 0.1))
    st.flush()
    pin(c, 760, 1060 - 40 * math.sin(twos(T) * 6), 1.0, s=1.2)
    sv.bubble(c, "?", 420, 300, tail=(330, 470), size=90, kind="thought", maxw=140)
    return st.arr


SOURCES = [
    "Stanford HAI, AI Index Report 2026",
    "(jagged frontier · ClockBench · OSWorld)",
    "METR, AI ability on long tasks (2025)",
    "Google DeepMind, AlphaEvolve (2025)",
    "Google DeepMind, From AGI to ASI (June 2026)",
    "Butlin, Long et al., AI consciousness indicators",
]


def s_end(T, t, d):
    st = sv.Stage((40, 16, 90))
    c = st.c
    P = st.pen()
    st.shade("mag").drawRect(skia.Rect.MakeXYWH(0, 0, sv.W, sv.H), paint(shader=sv.lin((0, 0), (0, sv.H), [(255, 255, 255, 0.1), (255, 255, 255, 0.55)])))
    st.flush(roll=(int(t * 30), 0))
    cast.hero(P, 150, 1250, 0.42, T, arms=cast.ARM["point_up"], expr="wow", look=(0.6, -0.2))
    cast.bot(P, 950, 1270, 0.38, T, arms=((250, -40), (-70, 40)), bounce=0.8)
    st.flush()
    sv.tag_text(c, "WHERE WE", 540, 250, 100, fill=YEL, fill2=ORANGE, glow=YEL, seed=3, rot=-4)
    sv.tag_text(c, "ACTUALLY ARE", 540, 390, 100, fill=CYAN, fill2=(0, 120, 200), glow=CYAN, seed=4, rot=-4)
    box = skia.Rect.MakeLTRB(60, 540, 1020, 1030)
    c.drawRect(box.makeOffset(10, 12), paint(INK))
    c.drawRect(box, paint(WHITE))
    c.drawRect(box, paint(INK, stroke=7))
    sv.label(c, "SOURCES", 540, 610, 50, fname="bangers-400", color=MAG)
    f = sv.font("comic-neue-700", 34)
    for i, ln in enumerate(SOURCES):
        c.drawString(ln, 540 - f.measureText(ln) / 2, 675 + i * 58, f, paint(INK))
        sv.reg(540 - f.measureText(ln) / 2, 675 + i * 58 - 30, 540 + f.measureText(ln) / 2, 675 + i * 58 + 8, "source")
    sv.label(c, "A style homage to the 2018 animated multiverse film", 540, 1090, 32, fname="comic-neue-700", color=WHITE)
    sv.label(c, "All visuals, music and voices synthesized", 540, 1134, 32, fname="comic-neue-700", color=WHITE)
    kc = pop(T, C["end_card"] + 0.4)
    if kc:
        sv.label(c, "DROP YOUR PIN IN THE COMMENTS", 540, 1236, 50, fname="bangers-400", color=INK, bg=YEL, edge=INK, rot=-2, a=min(1.0, kc))
    return st.arr

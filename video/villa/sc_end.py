"""The quiet lesson: a tutor that asks instead of answers; UNESCO's guidance and how few schools had any; the clock
in the square strikes once more and takes its newest little scholar inside; FINE."""
import math

import numpy as np
import skia

import cast as CA
import gel as G
import kit as K
import props as PR
import sets as SE
from common import E, S, Wx, blink, talk, zoom
from edit import cut, end
from kit import AMBER, BLACK, EMERALD, GOLD, INK, MAGENTA, PAPER, WHITE, H, W, mix, paint, ramp


def s_e_slate(T, idx):
    """AI can be the best tutor you'll ever have, if it makes you do the thinking. A slate by candlelight: the tutor's
    chalk asks WHY?; a hand works out the answer underneath."""
    st = K.Stage((6, 4, 4))
    c = st.c
    t0 = cut("e_slate")
    zoom(c, T, t0, end("e_slate"), 1.0, 1.08, cx=540, cy=760)
    G.pool(c, 540, 900, 800, AMBER, 0.55)
    c.drawRoundRect(skia.Rect.MakeLTRB(130, 340, 950, 1240), 20, 20, paint((90, 60, 36)))
    c.drawRoundRect(skia.Rect.MakeLTRB(160, 370, 920, 1210), 12, 12, paint((34, 40, 38)))
    chalk = (236, 234, 224)
    kq = K.ease(ramp(T, t0 + 0.6, t0 + 1.2))
    K.text(c, "WHY?", 540, 560, 120, "playfair-400i", chalk, tag="label", a=kq)
    kw = ramp(T, S("e1") + 0.5, E("e1") + 0.2)
    lines = ["because each step", "depends on the one", "before it..."]
    for i, ln in enumerate(lines):
        k = min(1.0, max(0.0, kw * 3 - i))
        if k <= 0:
            continue
        f = K.font("playfair-400i", 52)
        w = f.measureText(ln)
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(200, 600, 200 + w * k + 4, 1200))
        K.text(c, ln, 210, 720 + i * 90, 52, "playfair-400i", chalk, align="left", tag="label", a=0.9)
        c.restore()
        if 0 < k < 1:                                          # the hand with the chalk, following the words
            hx, hy = 210 + w * k, 720 + i * 90
            c.drawPath(K.capsule(hx + 20, hy + 20, hx + 200, hy + 260, 70, 90), paint((150, 110, 90)))
            c.drawLine(hx, hy, hx + 30, hy + 30, paint(chalk, stroke=10))
    G.candle(c, 860, 1300, 1.0, T, seed=4)
    c.restore()
    return st.arr


def s_e_unesco(T, idx):
    """UNESCO calls for AI that is human-centred, age-appropriate and carefully governed. Yet in 2023, fewer than 1 in
    10 schools and universities had any formal guidance."""
    st = K.Stage((6, 4, 6))
    c = st.c
    t0 = cut("e_unesco")
    zoom(c, T, t0, end("e_unesco"), 1.0, 1.05, cx=540, cy=800)
    G.pool(c, 540, 700, 800, (120, 30, 60), 0.5)
    G.pool(c, 540, 1100, 600, AMBER, 0.3)
    rows = [("UNESCO GUIDANCE, 2023", 46, "cinzel-800"), ("HUMAN-CENTRED", 50, "cinzel-600"), ("AGE 13+ IN CLASSROOMS", 40, "cinzel-600"),
            ("TRAINED TEACHERS", 40, "cinzel-600"), ("TOOLS CHECKED BEFORE USE", 40, "cinzel-600"), ("PRIVACY PROTECTED", 40, "cinzel-600")]
    x0, y0, x1, y1 = 120, 300, 960, 880
    c.drawRect(skia.Rect.MakeLTRB(x0 + 8, y0 + 10, x1 + 8, y1 + 10), paint((0, 0, 0), 0.5, blur=10))
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(shader=K.lin((x0, y0), (x1, y1), [mix(GOLD, WHITE, 0.3), GOLD, mix(GOLD, BLACK, 0.35)])))
    c.drawRect(skia.Rect.MakeLTRB(x0 + 14, y0 + 14, x1 - 14, y1 - 14), paint(mix(GOLD, BLACK, 0.5), stroke=4))
    for i, (txt, size, fn) in enumerate(rows):
        k = K.ease(ramp(T, t0 + 0.2 + i * 0.35, t0 + 0.6 + i * 0.35))
        K.text(c, txt, 540, y0 + 90 + i * 92, size, fn, (60, 36, 14), tag="plaque", a=k)
    ty = Wx("e2", "Yet") - 0.1
    if T > ty:
        k = K.ease(ramp(T, ty, ty + 0.4))
        for i in range(10):                                    # ten schools; one with a light in the window
            x = 140 + i * 90
            y = 1180
            lit = i == 3
            c.drawRect(skia.Rect.MakeLTRB(x - 32, y - 50, x + 32, y + 30), paint((60, 46, 40), k))
            c.drawPath(K.path([(x - 40, y - 50), (x, y - 92), (x + 40, y - 50)]), paint((80, 40, 36), k))
            c.drawRect(skia.Rect.MakeLTRB(x - 12, y - 30, x + 12, y), paint((255, 200, 90) if lit else (14, 10, 12), k))
            if lit:
                G.pool(c, x, y - 15, 70, AMBER, 0.6 * k)
        K.text(c, "SCHOOLS & UNIVERSITIES WITH ANY GUIDANCE", 540, 1290, 30, "cinzel-600", (236, 220, 190), tag="label", a=k)
    c.restore()
    return st.arr


def s_e_clock(T, idx):
    """Ask it to teach you, not to do it for you. If you can't explain it without the machine, you don't know it yet.
    The clock in the square strikes once more; its scholars march back inside - the last of them has auburn hair."""
    st = K.Stage()
    c = st.c
    t0 = cut("e_clock")
    zoom(c, T, t0, end("e_clock") + 0.5, 1.6, 3.2, cx=540, cy=860)
    u = T - t0
    parade = [1.0 - (u - 0.4 - k * 0.6) * 0.28 for k in range(4)]
    SE.square(c, T, doors=1.0 - K.ease(ramp(T, end("e_clock") - 0.9, end("e_clock") - 0.2)), parade=None, group=1.0)
    sx, sy = 540, 880
    for k, p_ in enumerate(parade):
        if 0 <= p_ <= 1:
            PR.figurine(c, sx - 80 + 160 * p_, sy + 14, 0.36, T, "scholar", seed=k)
    pc = 1.0 - (u - 3.4) * 0.22                                # the newest one, last into the dark
    if 0 <= pc <= 1:
        PR.figurine(c, sx - 80 + 160 * pc, sy + 14, 0.38, T, "scholar", seed=9, hair=(110, 46, 26), face_color=(250, 246, 240))
    c.restore()
    return st.arr


def s_e_fine(T, idx):
    """FINE."""
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("e_fine")
    a = K.ease(ramp(T, t0 + 0.2, t0 + 0.8))
    K.text(c, "FINE", 540, 980, 170, "italiana-400", (246, 232, 214), tag="title", a=a)
    c.drawLine(440, 1030, 640, 1030, paint((200, 30, 50), a, stroke=3))
    return st.arr

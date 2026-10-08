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


def _chalk_hand(c, hx, hy, T, s=1.0):
    """A hand holding a stick of chalk like a pen, its tip at (hx, hy) on the slate, coming in from the lower right:
    a lace cuff, the back of the hand, index and middle fingers along the chalk, the thumb pinching from below, the
    last two fingers curled; outlined and shaded by the candle."""
    c.save()
    c.translate(hx, hy)
    c.scale(s, s)
    skin, shade, line = (196, 146, 118), (138, 94, 76), (84, 52, 42)
    ol = lambda p: c.drawPath(p, paint(line, 0.9, stroke=3))
    sleeve = K.smooth([(150, 150), (330, 250), (520, 560), (300, 640), (120, 300)])
    c.drawPath(sleeve, paint((46, 32, 56)))
    for k in range(8):                                                                         # the lace cuff
        c.drawCircle(150 + k * 22, 150 + k * 16, 11, paint((150, 130, 160), 0.9))
    c.drawPath(K.capsule(-4, 4, 62, -54, 12, 12), paint((226, 222, 210)))                     # the chalk
    c.drawCircle(0, 0, 6, paint((240, 238, 230)))
    back = K.smooth([(58, -30), (150, -26), (214, 60), (190, 160), (110, 150), (52, 70)])     # the back of the hand
    c.drawPath(back, paint(skin))
    ol(back)
    for k, (x0, y0, x1, y1, x2, y2, w) in enumerate(((150, -10, 96, -42, 44, -44, 26),         # index, along the chalk
                                                      (166, 26, 108, -6, 56, -12, 24))):       # middle, under it
        p1 = K.capsule(x0, y0, x1, y1, w, w - 2)
        p2 = K.capsule(x1, y1, x2, y2, w - 2, w - 5)
        col = skin if k == 0 else mix(skin, shade, 0.25)
        c.drawPath(p1, paint(col))
        c.drawPath(p2, paint(col))
        ol(p1)
        ol(p2)
        c.drawOval(skia.Rect.MakeLTRB(x2 - 12, y2 - 9, x2 + 6, y2 + 5), paint((220, 176, 160)))   # the nail
    for k in range(2):                                                                         # ring and little fingers, curled
        cx_, cy_ = 150 - k * 6, 70 + k * 34
        p = K.smooth([(cx_ + 30, cy_ - 20), (cx_ - 40, cy_ - 16), (cx_ - 52, cy_ + 10), (cx_ - 20, cy_ + 26), (cx_ + 34, cy_ + 16)])
        c.drawPath(p, paint(mix(skin, shade, 0.35 + 0.15 * k)))
        ol(p)
    thumb = K.capsule(150, 120, 58, 16, 30, 24)                                                # the thumb, pinching from below
    c.drawPath(thumb, paint(mix(skin, shade, 0.1)))
    ol(thumb)
    for k in range(3):                                                                         # knuckles
        c.drawPath(K.bez_path([(150 + k * 8, -22 + k * 26), (162 + k * 8, -14 + k * 26), (170 + k * 8, -2 + k * 26)]),
                   paint(shade, 0.8, stroke=3))
    c.drawPath(K.bez_path([(70, -36), (120, -40), (160, -20)]), paint((236, 196, 160), 0.7, stroke=4))   # candlelight on the edge
    c.restore()


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
        if 0 < k < 1:                                          # her hand with the chalk, following the words
            _chalk_hand(c, 210 + w * k, 720 + i * 90 - 6, T)
    G.candle(c, 960, 1160, 0.9, T, seed=4)
    c.restore()
    return st.arr


def s_e_unesco(T, idx):
    """UNESCO calls for AI that is human-centred, age-appropriate and carefully governed: a gold plaque, its lines
    lighting up. Yet in 2023, fewer than 1 in 10 schools and universities had any formal guidance: ten little schools
    on a dusty shelf; a light in one window."""
    st = K.Stage((6, 4, 6))
    c = st.c
    t0 = cut("e_unesco")
    ty = Wx("e2", "Yet") - 0.15
    if T >= ty:                                                 # a row of universities; fewer than one in five lit
        zoom(c, T, ty, end("e_unesco") + 0.3, 1.0, 1.2, cx=300, cy=980)
        c.translate(40 - 80 * ramp(T, ty, end("e_unesco")), 0)
        c.drawRect(skia.Rect.MakeLTRB(-100, 0, W + 100, H), paint((24, 14, 12)))
        G.pool(c, 540, 900, 780, (120, 30, 60), 0.5)
        c.drawRect(skia.Rect.MakeLTRB(-100, 1100, W + 100, 1140), paint((96, 60, 36)))
        c.drawRect(skia.Rect.MakeLTRB(-100, 1140, W + 100, 1175), paint((44, 26, 16)))
        k = K.ease(ramp(T, ty, ty + 0.4))
        for i in range(10):                                    # ten universities: one lit, one guttering - 19%
            x = 75 + i * 103
            y = 1100
            lit = i == 2
            dim = i == 6
            c.drawRect(skia.Rect.MakeLTRB(x - 42, y - 120, x + 42, y), paint((84, 70, 62)))
            c.drawPath(K.path([(x - 50, y - 120), (x, y - 150), (x + 50, y - 120)]), paint((100, 86, 76)))
            for cx_ in (-28, -9, 9, 28):                        # a colonnade
                c.drawRect(skia.Rect.MakeLTRB(x + cx_ - 4, y - 112, x + cx_ + 4, y - 18), paint((150, 136, 120)))
            c.drawRect(skia.Rect.MakeLTRB(x - 46, y - 18, x + 46, y), paint((120, 106, 94)))
            fl = 0.6 + 0.4 * math.sin(T * 13 + i) if dim else 1.0
            for wx in (-18, 0, 18):
                col = (255, 200, 90) if lit else ((200, 140, 60) if dim else (14, 10, 12))
                c.drawRect(skia.Rect.MakeLTRB(x + wx - 6, y - 96, x + wx + 6, y - 60), paint(col, fl if dim else 1.0))
            if lit:
                G.pool(c, x, y - 78, 130, AMBER, 0.75 * k)
            if dim:
                G.pool(c, x, y - 78, 70, AMBER, 0.3 * k * fl)
        rng = K.rng_at(91, 1)
        for i in range(60):                                     # dust on the shelf
            c.drawCircle(rng.uniform(0, W), rng.uniform(1100, 1112), rng.uniform(1, 2.5), paint((200, 180, 150), 0.4))
        G.motes(c, T, 100, 600, 980, 1100, n=30, a=0.45, seed=7)
        c.restore()
        K.text(c, "UNIVERSITIES WITH A FORMAL", 540, 560, 44, "cinzel-600", (236, 220, 190), tag="label", a=k)
        K.text(c, "AI POLICY, 2025: 19%", 540, 620, 44, "cinzel-600", (236, 220, 190), tag="label", a=k)
        return st.arr
    zoom(c, T, t0, ty + 0.3, 1.0, 1.1, cx=540, cy=620)
    G.pool(c, 540, 700, 800, (120, 30, 60), 0.5)
    G.pool(c, 540, 1100, 600, AMBER, 0.3)
    rows = [("UNESCO GUIDANCE, 2023", 46, "cinzel-800"), ("HUMAN-CENTRED", 50, "cinzel-600"), ("AGE 13+ IN CLASSROOMS", 40, "cinzel-600"),
            ("TRAINED TEACHERS", 40, "cinzel-600"), ("TOOLS CHECKED BEFORE USE", 40, "cinzel-600"), ("PRIVACY PROTECTED", 40, "cinzel-600")]
    x0, y0, x1, y1 = 120, 300, 960, 880
    c.drawRect(skia.Rect.MakeLTRB(x0 + 8, y0 + 10, x1 + 8, y1 + 10), paint((0, 0, 0), 0.5, blur=10))
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(shader=K.lin((x0, y0), (x1, y1), [mix(GOLD, WHITE, 0.3), GOLD, mix(GOLD, BLACK, 0.35)])))
    c.drawRect(skia.Rect.MakeLTRB(x0 + 14, y0 + 14, x1 - 14, y1 - 14), paint(mix(GOLD, BLACK, 0.5), stroke=4))
    for i, (txt, size, fn) in enumerate(rows):
        k = K.ease(ramp(T, t0 + 0.2 + i * 0.55, t0 + 0.6 + i * 0.55))
        K.text(c, txt, 540, y0 + 90 + i * 92, size, fn, (60, 36, 14), tag="plaque", a=k)
        if 0 < k < 1:
            G.pool(c, 540, y0 + 76 + i * 92, 300, (255, 230, 170), 0.35 * (1 - abs(2 * k - 1)))
    G.candle(c, 150, 1210, 1.0, T, seed=11)
    G.candle(c, 930, 1210, 1.0, T, seed=12)
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
    pc = max(0.42, 1.0 - (u - 3.4) * 0.22)                     # the newest one, last; she stops at the door and looks out
    if u >= 3.4:
        fx, fy = sx - 80 + 160 * pc, sy + 14
        t_in = t0 + 3.6
        fyf = fy - 124 * 0.38 - 2
        zoom(c, T, t_in, end("e_clock") + 0.2, 1.0, 7.5, cx=fx, cy=fyf)
        PR.figurine(c, fx, fy, 0.38, T, "scholar", seed=9, hair=(110, 46, 26), face_color=(250, 246, 240))
        crk = ramp(T, end("e_clock") - 1.0, end("e_clock") - 0.3)
        CA.face(c, fx, fyf, 0.026, "clara", T, L=(255, 170, 70), R=(70, 100, 255), core=0.4, expr="blank",
                porc=1.0, blink=0.0, neck=False, cap=True, crack=crk)
        c.restore()
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

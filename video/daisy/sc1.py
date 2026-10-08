"""Chapter 2, THE ANSWER-KEY CAKE: headlines; not an IQ score; broken questions snipped out of the tests; a year torn
off in months; the answers piped onto a cake and fed to the Oracle; fresh questions off a press; a hollow 94%; the
refrain."""
import math

import numpy as np
import skia

import collage as CL
import common as C
import duo as D
import kit as K
import props as PR
import sets as SE
from common import E, S, Wx, typed
from kit import INK, WHITE, H, W, ease, mix, paint, path, ramp
from sc0 import chain, refrain, score_meter


def s_b_card(T, idx):
    st = K.Stage()
    C.chapter_card(st.c, T, E("a16") + 0.1, 2, "THE ANSWER-KEY CAKE")
    return st.arr


def _headline(c, T, t0, s, y, colors, seed, rot):
    k = K.pop(T, t0, 0.2, 0.35)
    if k <= 0:
        return
    c.save()
    c.translate(540, y)
    c.rotate(rot)
    c.scale(k, k)
    CL.paper(c, [(-470, -150), (470, -160), (480, 60), (-480, 70)], (242, 236, 220), seed=seed, edge="torn")
    rng = K.rng_at(seed, 2)
    for j in range(3):                                                   # newsprint around the headline
        c.drawRect(skia.Rect.MakeXYWH(-440, 20 + j * 12, 880 * rng.uniform(0.6, 1.0), 5), paint((150, 140, 130), 0.6))
    C.big(c, s, 0, -20, 130, colors, seed=seed, max_w=880)
    c.restore()


def _shoot_oracle(cc):
    PR.oracle(cc, 180, 900, 0.62, 0.0, look=(0.2, -0.2), medal=False)


def s_b_banners(T, idx):
    """'91%! Human-level! PhD-level!' Newspaper headlines slap down; Lili cheers on every one."""
    st = K.Stage()
    c = st.c
    SE.void(c, (60, 50, 56), seed=2)
    _headline(c, T, Wx("b1", "Ninety") - 0.1, "91%!", 380, [(200, 30, 40), (24, 20, 22)], 3, -4)
    _headline(c, T, Wx("b1", "Human") - 0.1, "HUMAN-LEVEL!", 620, [(24, 20, 22), (40, 80, 150)], 5, 3)
    _headline(c, T, Wx("b1", "PhD") - 0.1, "PhD-LEVEL!", 860, [(176, 30, 54), (24, 20, 22)], 7, -2)
    if T > Wx("b1", "Ninety") - 0.1:                                      # the front-page photograph
        img = K.cached("press_oracle", lambda: CL.snapshot(360, 270, _shoot_oracle, bg=(160, 156, 150), cell=5))
        CL.photo(c, img, 560, 1110, 340, 255, ang=-3, border=12)
    keys = [(S("b1") - 0.1, "stand"), (Wx("b1", "Ninety") - 0.05, "up"), (Wx("b1", "Human") - 0.05, "wave"), (Wx("b1", "PhD") - 0.05, "up")]
    C.girl(c, "lili", 540, 2560, 0.95, T, keys, mood="delight")
    return st.arr


def s_b_iq(T, idx):
    """'Those numbers matter. But they aren't IQ scores for machines.' The Oracle in a mortarboard; an IQ card,
    crossed out."""
    st = K.Stage()
    c = st.c
    SE.salon(c, T, wall=(170, 170, 170), wall2=(220, 220, 214))
    PR.oracle(c, 700, 1560, 0.8, T, look=(-0.5, 0))
    fx, fy = 700, 1560 - 0.8 * 1110
    c.drawPath(path([(fx - 200, fy - 150), (fx + 200, fy - 150), (fx + 120, fy - 110), (fx - 120, fy - 110)]), paint(INK))   # mortarboard
    c.drawRect(skia.Rect.MakeXYWH(fx - 90, fy - 150, 180, 40), paint(INK))
    c.drawLine(fx + 150, fy - 140, fx + 190, fy - 40, paint((214, 168, 40), stroke=6))
    t1 = Wx("b2", "But") - 0.1
    c.save()
    c.translate(260, 700)
    c.rotate(-6)
    CL.paper(c, CL.rect_pts(-200, -150, 200, 150), (250, 244, 228), seed=3)
    f = K.font("abril-400", 120)
    c.drawString("IQ", -f.measureText("IQ") / 2, 40, f, paint(INK))
    K.reg_local(c, -200, -150, 200, 150, "card")
    if T > t1 + 0.4:
        k = ramp(T, t1 + 0.4, t1 + 0.7)
        c.drawLine(-180, -130, -180 + 360 * k, -130 + 260 * k, paint((200, 30, 40), stroke=22))
        if k >= 1:
            c.drawLine(180, -130, -180, 130, paint((200, 30, 40), stroke=22))
    c.restore()
    if T > Wx("b2", "numbers") - 0.1:
        C.label(c, "THEY MATTER", 300, 1000, 48, paper=(250, 196, 30), rot=4)
    return st.arr


ITEMS = ["What is 2 + 2?", "Name a fruit.", "Which is heavier?", "Solve for x: ?", "Pick the odd one out.", "Spell 'daisy'."]


def s_b_broken(T, idx):
    """'Stanford's 2026 AI Index: in the tests reviewed, 2 to 42% of questions were broken.' Zuza snips the broken
    questions out of the exam sheets."""
    st = K.Stage()
    c = st.c
    SE.void(c, (220, 214, 196), seed=4)
    t0 = S("b3")
    cuts = [i for i, tc in enumerate((t0 + 1.2, t0 + 2.4, t0 + 3.6)) if T > tc]
    cut_set = tuple([1, 3, 4][:len(cuts)])
    PR.exam(c, 560, 420, 1.1, -2, ITEMS, title="BENCHMARK X", cut=cut_set)
    for j, i in enumerate(cut_set):                                       # the snipped-out questions, fluttering down
        tc = t0 + 1.2 + j * 1.2
        u = T - tc
        PR.slip(c, 260 + j * 200 + 60 * math.sin(u * 3), min(1140, 1060 + 120 * u), 20 * math.sin(u * 4 + j), [ITEMS[i][:18]], 0.6)
    ci = min(len(cut_set), 2)
    if True:                                                             # the shears stay on the job
        yy = 420 + 1.1 * (130 + [1, 3, 4][ci] * 70)
        CL.scissors(c, 300 + 60 * math.sin(T * 6), yy - 20, 0, 0.5 + 0.5 * math.sin(T * 26), 0.9)
    C.label(c, "STANFORD AI INDEX 2026", 540, 330, 44, fname="special-elite-400", rot=-1)
    if T > Wx("b3", "two") - 0.1:
        k = K.pop(T, Wx("b3", "two") - 0.1, 0.25, 0.3)
        c.save(); c.translate(520, 1240); c.scale(k, k); c.translate(-520, -1240)
        C.big(c, "2 TO 42% BROKEN", 520, 1260, 110, [(200, 30, 40), (24, 20, 22)], seed=13, max_w=720)
        c.restore()
    return st.arr


def s_b_months(T, idx):
    """'And tests built to stay hard for years are being beaten in months.' A calendar loses its pages in a gale."""
    st = K.Stage()
    c = st.c
    SE.salon(c, T, wall=(150, 180, 200), wall2=(220, 228, 236))
    t0, t1 = S("b5"), Wx("b5", "beaten") - 0.1
    months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN"]
    u = ramp(T, t0 + 0.4, t1)
    n = int(u * 6)
    rng = K.rng_at(3, 3)
    for i in range(n):                                                    # torn-off pages blowing away
        tt = t0 + 0.4 + i * (t1 - t0 - 0.4) / 6
        dt = T - tt
        PR.calendar(c, 540 + 500 * dt * (1 if i % 2 else -0.6), 760 - 300 * dt + 400 * dt * dt, 0.7, months[i], str(i + 1),
                    ang=dt * 200 * (1 if i % 2 else -1))
    if T < t1:
        PR.calendar(c, 540, 760, 1.2, "BUILT TO LAST", "YEARS", colr=(40, 80, 150))
    else:
        PR.calendar(c, 540, 760, 1.2, "BEATEN IN", "MONTHS", colr=(176, 30, 54))
    C.girl(c, "zuza", 880, 2000, 0.62, T, [(t0, "stand"), (t1, "shrug")], mood="deadpan")
    return st.arr


ANSWERS = ["1-B  2-D  3-A", "4-C  5-B  6-A"]


def s_b_leak(T, idx):
    """'And contamination: if test questions leak into the training data, the score stops measuring new thinking.' -
    'Answer-key cake!' Lili pipes the answer key onto a cake."""
    st = K.Stage()
    c = st.c
    SE.salon(c, T, wall=(110, 70, 110), wall2=(160, 120, 160))
    t0 = S("b6")
    PR.exam(c, 260, 330, 0.62, -8, ITEMS[:4], title="THE ANSWERS", marks={0: "B", 1: "D", 2: "A", 3: "C"})
    k = ramp(T, Wx("b6", "leak") - 0.2, S("b7") - 0.1)
    lines = [typed(ANSWERS[0], ramp(k, 0, 0.5)), typed(ANSWERS[1], ramp(k, 0.5, 1))]
    c.drawRect(skia.Rect.MakeLTRB(0, 1330, W, 1480), paint((150, 104, 64)))                  # a table
    PR.cake(c, 600, 1330, 1.1, lines=[l for l in lines if l], T=T)
    piping = lambda cc, x, y, a: (cc.drawPath(K.capsule(x, y - 10, x + 30, y - 150, 60, 40), paint((250, 248, 240))),
                                  cc.drawPath(path([(x - 14, y - 10), (x + 14, y - 10), (x, y + 30)]), paint((200, 200, 196))))
    if T < S("b7") - 0.1:
        tip_x = 540 + 170 * (k * 2 % 1)
        C.girl(c, "lili", 880, 2050, 0.7, T, None, dict(sR=10, eR=8, tL=((tip_x - 880) / 0.7, (1150 - 2050) / 0.7)), mood="smile",
               props=(piping, None), hands=("fist", "open"), look=(-0.7, 0.4))
    else:
        C.girl(c, "lili", 880, 2050, 0.7, T, [(S("b7") - 0.1, "up")], mood="delight")
    if T > Wx("b6", "leak") - 0.1:
        C.label(c, "TEST LEAKS INTO TRAINING", 600, 760, 44, colr=(250, 244, 228), paper=(110, 50, 96), rot=-3)
    return st.arr


def s_b_feed(T, idx):
    """'Like an exam after seeing the answers.' Lili feeds the cake into the Oracle; it scores a hundred."""
    st = K.Stage()
    c = st.c
    SE.salon(c, T)
    t0 = S("b8")
    chew = ramp(T, t0 + 0.2, t0 + 0.9)
    pts = PR.oracle(c, 420, 1560, 0.8, T, mouth=0.9 if T < t0 + 0.9 else 0.3 + 0.3 * abs(math.sin(T * 12)), stuffed=chew, look=(0.6, 0.2))
    mx, my = pts["mouth"]
    if T < t0 + 0.8:
        cx, cy = mx + 260 * (1 - chew), my + 30
        PR.cake(c, cx, cy + 60, 0.45, lines=["1-B 2-D"], T=T)
    C.girl(c, "lili", 860, 1830, 0.62, T, [(t0 - 0.1, "present"), (t0 + 0.9, "hips")], mood="sly", look=(-0.6, 0))
    if T > t0 + 1.0:
        k = K.pop(T, t0 + 1.0, 0.25, 0.35)
        c.save(); c.translate(820, 640); c.scale(k, k); c.rotate(8)
        c.drawCircle(0, 0, 150, paint((200, 30, 40), stroke=14))
        f = K.font("caveat-700", 170)
        c.drawString("100", -f.measureText("100") / 2, 55, f, paint((200, 30, 40)))
        K.reg_local(c, -150, -150, 150, 150, "score")
        c.restore()
        C.label(c, "SAW THE ANSWERS FIRST", 540, 330, 44, fname="special-elite-400", rot=-1)
    return st.arr


QUESTIONS = ["Q: a clock says 7:40...", "Q: which daisy is taller?", "Q: what comes after Tuesday?", "Q: halve 2,026."]


def s_b_fresh(T, idx):
    """'A 2025 survey calls it persistent, and urges fresh, dynamic tests.' The duo crank a little press that prints a
    brand-new question every time."""
    st = K.Stage()
    c = st.c
    SE.salon(c, T, wall=(150, 190, 150), wall2=(220, 236, 220))
    t0 = Wx("b8", "survey") - 0.6
    ang = (T - t0) * 160
    c.drawPath(K.rrect(330, 980, 750, 1300, 20), paint((60, 66, 64)))            # the press
    for cx_ in (430, 650):
        c.drawCircle(cx_, 1060, 70, paint((150, 156, 166)))
        c.drawLine(cx_, 1060, cx_ + 60 * math.cos(math.radians(ang)), 1060 + 60 * math.sin(math.radians(ang)), paint(INK, stroke=10))
    c.drawLine(750, 1140, 750 + 110 * math.cos(math.radians(ang)), 1140 + 110 * math.sin(math.radians(ang)), paint((90, 60, 36), stroke=16))
    n = int((T - t0) / 0.9)
    for i in range(max(0, n - 2), n + 1):                                 # each turn prints a new sheet
        u = ((T - t0) - i * 0.9) / 0.9
        if u < 0:
            continue
        y = 960 - 520 * min(1, u * 1.4)
        PR.slip(c, 540 + (i % 2) * 30, y, (i % 3 - 1) * 4, [QUESTIONS[i % 4]], 0.9)
    C.girl(c, "zuza", 180, 1880, 0.6, T, None, dict(sL=10, eL=8, sR=60 + 20 * math.sin(math.radians(ang)), eR=20), mood="deadpan")
    C.girl(c, "lili", 900, 1880, 0.6, T, None, "clap", mood="delight")
    C.label(c, "EMNLP 2025 SURVEY", 540, 330, 44, fname="special-elite-400", rot=-1)
    if T > Wx("b8", "fresh") - 0.1:
        C.label(c, "FRESH, DYNAMIC TESTS", 540, 1380 - 160, 46, colr=(250, 244, 228), paper=(40, 120, 124), rot=2)
    return st.arr


def s_b_94(T, idx):
    """'The progress is real. But "scored 94%" says less than it sounds.' A great paper 94% - Zuza cuts it open: it is
    hollow."""
    st = K.Stage()
    c = st.c
    SE.void(c, (226, 214, 190), seed=6)
    t1 = Wx("b9", "But") - 0.1
    for i in range(5):                                                   # real progress: a rising stair of bars
        h = 120 + i * 110
        if T > S("b9") + i * 0.12:
            CL.paper(c, CL.rect_pts(110 + i * 90, 1250 - h, 180 + i * 90, 1250), (40, 120, 124), seed=i)
    C.label(c, "REAL PROGRESS", 330, 1330 - 30, 40, fname="special-elite-400", rot=-2)
    k = K.pop(T, S("b9") + 0.3, 0.25, 0.3)
    split = ramp(T, t1 + 0.6, t1 + 1.1)
    c.save()
    c.translate(640, 700)
    c.scale(k, k)
    for side in (-1, 1):
        c.save()
        c.translate(side * 90 * split, 0)
        c.rotate(side * 8 * split)
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(-400 if side < 0 else 0, -400, 0 if side < 0 else 400, 400))
        f = K.font("abril-400", 260)
        c.drawString("94%", -f.measureText("94%") / 2 + 6, 108, f, paint(INK, 0.35))
        c.drawString("94%", -f.measureText("94%") / 2, 100, f, paint((200, 30, 40)))
        c.restore()
        c.restore()
    if split > 0.3:
        c.drawRect(skia.Rect.MakeLTRB(-60 * split, -200, 60 * split, 120), paint((40, 30, 30)))
        CL.scraps(c, T, t1 + 0.8, seed=8, n=6, area=(-60, -100, 60, 120), fall=200)
    c.restore()
    K.reg(640 - 290, 700 - 200, 640 + 290, 700 + 110, "big")
    if T > t1:
        C.girl(c, "zuza", 900, 1950, 0.66, T, [(t1, "stand"), (t1 + 0.3, dict(sL=150, eL=20))], mood="deadpan",
               props=(lambda cc, x, y, a: CL.scissors(cc, x, y, a + 180, 0.5 + 0.5 * math.sin(T * 20), 0.9), None), hands=("fist", "open"))
    if split >= 1:
        C.label(c, "LESS THAN IT SOUNDS", 680, 1000, 44, colr=(250, 244, 228), paper=(24, 20, 22), rot=3)
    return st.arr


def s_b_refrain(T, idx):
    """'Does it know?' - 'It scored that it knows.'"""
    return refrain(T, idx, "b10", "b11")

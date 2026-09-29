"""CHAPTER THREE: DOUBT - the trap (answers without learning), her rule, the evidence that a tutor built well works,
and the teacher who was never the problem."""
import math

import numpy as np
import skia

import cards as K
import draw as D
import figures as F
import props as P
import sets
from cues import C, Wx
from draw import (CREAM, GOLD, GOLDD, GOLDL, H, INK, JADE, LACQ, LAMP, PINK, VERM, W, WHITE, ease, mix, paint, path, ramp)
from sc1 import cam
from sc2 import MSGS, _chat, screen
from timeline import TL

S, E = TL.s, TL.e
INDIGO = (30, 36, 90)


def s_box(T, t, d):
    """The answer box: a vermilion lacquer box spills answers; the figure takes them, eyes shut, and fades."""
    st = D.Stage((0, 0, 0))
    c = st.c
    c.save()
    cam(c, 1.0 + 0.05 * t / max(d, 0.1), 540, 1200)
    sets.bd(st, "stage_indigo", lambda cc: sets.stage(cc, "indigo"))
    sets.spotlight(c, 540, 170, 540, 1350, 260, a=0.3)
    op = ease(ramp(t, 0.2, 0.9))
    P.answer_box(c, 380, 1380, 0.9, T, open_=op)
    rng = np.random.default_rng(3)
    for i in range(9):                                                  # answers arcing out of the box to her
        u = ((t * 0.8 + i / 9) % 1.0)
        x = 380 + 360 * u
        y = 1080 - 420 * math.sin(u * math.pi)
        P.scroll(c, x, y, 0.8, rot=40 * u - 20, text="ANSWER", a=op * (1 - abs(u - 0.5)) * 1.6)
    fadek = ease(ramp(t, 1.4, d))
    F.learner(c, 800, 1400, 0.62, T, color=mix((244, 240, 232), (60, 60, 80), fadek), pose="reach")
    c.restore()
    return st.arr


def _bars(c, T, show_hint):
    sets.stage(c, None)
    x_p, x_e, base, top = 360, 720, 1120, 640
    kp = ease(ramp(T, C["practice"] - 0.2, C["practice"] + 0.5))
    ke = ease(ramp(T, C["worse"] - 0.4, C["worse"] + 0.3))
    hp = (base - top) * (0.5 + 0.5 * 0.48 * kp)                         # practice: up 48%
    he = (base - top) * 0.5 * (1 - 0.17 * ke)                           # exam without it: down 17%
    c.drawRect(skia.Rect.MakeLTRB(x_p - 110, base - hp, x_p + 110, base), paint(GOLD))
    c.drawRect(skia.Rect.MakeLTRB(x_e - 110, base - he, x_e + 110, base), paint(VERM))
    c.drawLine(200, base, 880, base, paint(GOLDL, stroke=4))
    D.text(c, "PRACTICE", x_p, base + 64, 44, "cormorant-700", CREAM, tag="bar")
    D.text(c, "with the chatbot", x_p, base + 108, 32, "cormorant-500i", CREAM, tag="bar")
    D.text(c, "EXAM", x_e, base + 64, 44, "cormorant-700", CREAM, tag="bar2")
    D.text(c, "without it", x_e, base + 108, 32, "cormorant-500i", CREAM, tag="bar2")
    if kp > 0.05:
        D.text(c, "+48%", x_p, base - hp - 30, 60, "cormorant-700", GOLDL, tag="barv", a=kp)
    if ke > 0.05:
        D.text(c, "−17%", x_e, base - he - 30, 60, "cormorant-700", (255, 120, 100), tag="barv2", a=ke)
    P.banner(c, 540, 400, 820, 200, ["A PLAIN CHATBOT", "about 1,000 high-school maths students"], bg=VERM, sizes=(58, 38),
             src="Bastani et al., PNAS, 2025")


def _hint_set(c, T):
    sets.stage(c, "jade")
    P.lantern(c, 540, 820, 0.7, 1.0, T, cord=650)
    P.banner(c, 540, 400, 840, 230, ["HINTS, NOT ANSWERS", "a tutor built this way largely avoided the drop"], bg=LACQ,
             sizes=(66, 40), src="same study")
    F.learner(c, 540, 1420, 0.6, T, pose="stand", glow=1.0)


def s_study(T, t, d):
    st = D.Stage((0, 0, 0))
    c = st.c
    k = ramp(T, C["hints"] - 0.5, C["hints"] + 0.8)
    if k <= 0:
        _bars(c, T, 0)
    else:
        _hint_set(c, T)
        sets.slide(c, sets.layer(lambda cc: _bars(cc, T, 0)), k, direction=-1)
    return st.arr


def s_rule(T, t, d):
    st = D.Stage()
    screen(st, T, t, d, _chat(T))
    K.countdown(st.c, T)
    return st.arr


def s_harvard(T, t, d):
    """Built well, it works: two lanterns, one twice as bright, and a clock that runs shorter."""
    st = D.Stage((0, 0, 0))
    c = st.c
    sets.bd(st, "stage_none", lambda cc: sets.stage(cc, None))
    kt = ease(ramp(T, C["twice"] - 0.3, C["twice"] + 0.6))
    base = 1150
    for x, lab, g in ((330, "CLASS", 1.0), (750, "AI TUTOR", 1.0 + 1.15 * kt)):
        h = 200 * g
        c.drawRect(skia.Rect.MakeLTRB(x - 100, base - h, x + 100, base), paint(GOLD if lab == "AI TUTOR" else (120, 110, 90)))
        P.lantern(c, x, base - h - 90, 0.45, 0.4 + 0.6 * (g - 1) / 1.15 if lab == "AI TUTOR" else 0.4, T, cord=500)
        D.text(c, lab, x, base + 60, 44, "cormorant-700", CREAM, tag="hv")
    P.banner(c, 540, 400, 840, 220, ["HARVARD PHYSICS", "AI tutor vs. an active-learning class"], bg=INDIGO, sizes=(58, 40),
             src="Kestin et al., Scientific Reports, 2025")
    kl = ease(ramp(T, C["less_time"] - 0.2, C["less_time"] + 0.4))
    D.text(c, "learning gains" + (",  in less time" if kl > 0.5 else ""), 540, base + 112, 36, "cormorant-500i", (230, 220, 200), tag="hv2")
    if kt > 0.5:
        D.text(c, "more than", 750, base - 200 * (1 + 1.15 * kt) + 60, 38, "cormorant-700", LACQ, tag="hv3", a=kt)
        D.text(c, "2×", 750, base - 200 * (1 + 1.15 * kt) + 130, 70, "cormorant-700", LACQ, tag="hv5", a=kt)

    return st.arr


def s_teacher_night(T, t, d):
    """Memory, dead symmetrical: her teacher at her own table at night, facing us, a stack of papers either side,
    one bulb above - grading. Older, glasses, a shawl: not the girl."""
    st = D.Stage((20, 20, 20))
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.rad((540, 760), 1000, [(120, 120, 120), (40, 40, 40), (10, 10, 10)], [0, 0.5, 1])))
    c.save()
    cam(c, 1.0 + 0.06 * t / max(d, 0.1), 540, 1000)
    P.hanging_bulb(c, 540, 520, 1.2, 1.0, cord=420)
    F.teacher_front(c, 540, 1180, 1.0, T)
    c.drawRect(skia.Rect.MakeLTRB(80, 1180, 1000, 1230), paint((150, 150, 150)))                   # the table
    c.drawRect(skia.Rect.MakeLTRB(120, 1230, 150, 1700), paint((60, 60, 60)))
    c.drawRect(skia.Rect.MakeLTRB(930, 1230, 960, 1700), paint((60, 60, 60)))
    n = int(12 + 10 * ease(t / max(d, 0.1)))
    for side in (-1, 1):                                                # the two stacks, growing
        for i in range(n):
            x0 = 540 + side * 330
            c.drawRect(skia.Rect.MakeLTRB(x0 - 110, 1172 - i * 13, x0 + 110, 1182 - i * 13), paint((226, 226, 224)))
            c.drawLine(x0 - 110, 1182 - i * 13, x0 + 110, 1182 - i * 13, paint((140, 140, 140), stroke=1.5))
    c.drawRect(skia.Rect.MakeLTRB(430, 1150, 650, 1178), paint((236, 236, 234)))                   # the paper in front of her
    c.restore()
    return st.arr


def s_cranes(T, t, d):
    """The same tools: the stack lifts off her desk and folds into paper cranes; one small desk lights up - flagged."""
    st = D.Stage((0, 0, 0))
    c = st.c
    sets.bd(st, "stage_jade", lambda cc: sets.stage(cc, "jade"))
    c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0), 0.3))
    for r in range(3):                                                  # her class, small desks on the floor
        for q in range(6):
            x, y = 250 + q * 116, 1140 + r * 70
            flagged = (r, q) == (2, 4) and T >= C["flag"]
            P.lacquer_desk(c, x, y, 0.45, lit=1.0 if flagged else 0.0)
            if flagged:
                c.drawCircle(x, y - 40, 60, paint(VERM, 0.5 + 0.3 * math.sin(T * 6), blur=20))
    P.lacquer_desk(c, 540, 1010, 0.8)
    F.robed(c, 540, 1040, 0.5, T, body=JADE, arms=0.2)
    rng = np.random.default_rng(9)
    kc = ramp(T, C["cranes"] - 0.3, C["cranes"] + 3.0)
    for i in range(12):                                                 # papers lift and fold into cranes
        u = max(0.0, min(1.0, kc * 1.6 - i * 0.06))
        if u <= 0:
            continue
        x = 540 + (rng.uniform(-1, 1) * 420) * u
        y = 940 - 640 * u + 40 * math.sin(T * 2 + i)
        P.crane(c, x, y, 0.35 + 0.25 * u, T, flap=T * 7 + i)
    ks = ease(ramp(T, C["six"] - 0.3, C["six"] + 0.3))
    if ks > 0:
        P.banner(c, 540, 420, 840, 220, ["ABOUT 6 HOURS A WEEK", "saved by teachers who use AI weekly"], bg=LACQ, sizes=(60, 40),
                 src="Gallup & Walton Family Foundation, US teachers, 2025", a=ks)
    return st.arr


def s_back_row(T, t, d):
    """Memory, rewritten: the teacher walks down to the back row, and kneels by her desk."""
    from sc1 import _class_rows
    st = D.Stage()
    c = st.c
    c.save()
    cam(c, 1.1, 540, 1000)
    sets.bd(st, "classroom", sets.classroom, tex=0.06)
    _class_rows(c, T, teacher_pose=None, lit_girl=ease(ramp(t, 0.3, 1.5)))
    k = ease(ramp(t, 0.0, 1.4))
    F.teacher(c, 960 - 180 * k, 1960, 1.0, T, pose="front")
    c.restore()
    K.aphorism(c, T, "Time to finally see the back row.", S("d7"), y=440, size=80, color=WHITE)
    return st.arr

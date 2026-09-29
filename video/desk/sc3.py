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
from sc2 import MSGS, _chat, _chat_bg, screen
from timeline import TL

S, E = TL.s, TL.e
INDIGO = (30, 36, 90)


def s_box(T, t, d):
    """The answer box: a vermilion lacquer box spills answers; the figure takes them, eyes shut, and fades."""
    st = D.Stage((0, 0, 0))
    c = st.c
    c.save()
    cam(c, 1.0 + 0.05 * t / max(d, 0.1), 540, 1200)
    sets.staged(st, "verm", "black", "gold")
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


def _chart_base(c, T):
    """Change against students who had no AI at all, as bars from a zero line: up is better, down is worse."""
    sets.stage(c, None, floor="black", posts="indigo")
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(130, 540, 950, 1350), 20, 20), paint((0, 0, 0), 0.6))
    D.text(c, "change vs. students with no AI", 540, 600, 38, "cormorant-500i", (220, 212, 196), tag="chart")
    c.drawLine(160, ZERO, 920, ZERO, paint(CREAM, stroke=3))
    D.text(c, "0", 150, ZERO + 12, 30, "cormorant-700", CREAM, align="right", tag="zero")


ZERO, PX = 1040, 2.9                                                   # the zero line; pixels per percent


def _bar(c, x, pct, k, col, lab, sub, val_col, tag):
    """One bar from the zero line, its value at its tip, its name underneath."""
    h = pct * PX * k
    top, bot = (ZERO - h, ZERO) if h >= 0 else (ZERO, ZERO - h)
    c.drawRect(skia.Rect.MakeLTRB(x - 62, top, x + 62, max(bot, top + 6)), paint(col))
    if k > 0.05:
        txt = f"+{pct}%" if pct > 0 else (f"−{-pct}%" if pct < 0 else "no clear drop")
        y = ZERO - h - 24 if pct > 0 else ZERO - h + 62
        D.text(c, txt, x - (40 if pct == 0 else 0), y, 56 if pct else 38, "cormorant-700", val_col, tag=tag + "v", a=min(1.0, k * 1.5))
    D.text(c, sub, x, 1215, 34, "cormorant-500i", (210, 204, 190), tag=tag)


def _chart_plain(c, T):
    kp = ease(ramp(T, C["practice"] - 0.2, C["practice"] + 0.5))
    ke = ease(ramp(T, C["worse"] - 0.4, C["worse"] + 0.3))
    _bar(c, 255, 48, kp, GOLD, "PRACTICE", "practice", GOLDL, "p1")
    _bar(c, 405, -17, ke, VERM, "EXAM", "exam", (255, 130, 110), "e1")
    D.text(c, "PLAIN CHATBOT", 330, 1290, 42, "cormorant-700", CREAM, tag="g1")


def _chart_hint(c, T):
    """The flat that slides in: the tutor that gave hints, not answers."""
    sets.spotlight(c, 750, 170, 750, 1320, 190, a=0.12)
    _bar(c, 675, 127, 1.0, (120, 200, 170), "PRACTICE", "practice", (170, 240, 210), "p2")
    _bar(c, 825, 0, 1.0, (120, 200, 170), "EXAM", "exam", (170, 240, 210), "e2")
    D.text(c, "HINT TUTOR", 750, 1290, 42, "cormorant-700", CREAM, tag="g2")


def s_study(T, t, d):
    """The trap, measured: a plain chatbot lifts practice and sinks the exam; then the hint tutor slides in."""
    st = D.Stage((0, 0, 0))
    c = st.c
    kh = ramp(T, C["hints"] - 0.3, C["hints"] + 0.9)
    c.save()
    cam(c, 1.0 + 0.04 * t / max(d, 0.1), 540, 1000)
    _chart_base(c, T)
    _chart_plain(c, T)
    if kh > 0:
        img = sets.layer(lambda cc: _chart_hint(cc, T))
        sets.slide(c, img, 1 - kh, direction=1)
        if kh < 1:                                                      # the lit edge of the moving flat
            ex = 560 + (W + 60) * ease(1 - kh)
            c.drawLine(ex, 540, ex, 1350, paint(GOLDL, 0.8, stroke=6))
    c.restore()
    kb = ease(ramp(T, C["hints"] - 0.3, C["hints"] + 0.3))
    if kb < 1:
        P.banner(c, 540, 400, 840, 210, ["A PLAIN CHATBOT", "about 1,000 high-school maths students"], bg=VERM, sizes=(58, 38),
                 src="Bastani et al., PNAS, 2025", a=1 - kb)
    if kb > 0:
        P.banner(c, 540, 400, 840, 210, ["HINTS, NOT ANSWERS", "a tutor built to guide largely avoided the drop"],
                 bg=(24, 70, 60), sizes=(58, 38), src="same study", a=kb)
    return st.arr


def s_trap(T, t, d):
    """Past midnight, tired: a problem she can't crack, a glowing SHOW ANSWER button, and her cursor drifting to it."""
    st = D.Stage()

    def fn(c):
        _chat_bg(c)
        c.drawRect(skia.Rect.MakeLTRB(80, 520, 1000, 590), paint((44, 48, 56)))
        D.text(c, "Problem 6", 540, 568, 32, "inter-700", (200, 206, 214), tag="ui")
        D.text(c, "d/dx (x² + 1)³  =  ?", 540, 720, 64, "inter-700", (236, 238, 240), tag="flash")
        for j, (w, y) in enumerate((("3(x² + 1)²", 830), ("6x(x² + 1)", 920))):     # her attempts, crossed out
            D.text(c, w, 540, y, 44, "inter-500", (140, 146, 156), tag="work")
            c.drawLine(420, y - 14, 660, y - 14, paint((200, 90, 80), stroke=4))
        pulse = 0.5 + 0.5 * math.sin(T * 7)
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(270, 1040, 810, 1160), 60, 60),
                    paint((255, 150, 80), 0.25 + 0.2 * pulse, blur=30))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(290, 1050, 790, 1150), 50, 50), paint((226, 120, 60)))
        D.text(c, "SHOW ANSWER", 540, 1118, 50, "inter-700", WHITE, tag="btn")
        u = ease(ramp(t, 0.1, d - 0.1))
        x, y = 900 - 300 * u, 1250 - 150 * u
        arrow = path([(x, y), (x, y + 60), (x + 15, y + 46), (x + 27, y + 72), (x + 38, y + 67), (x + 26, y + 41), (x + 46, y + 41)])
        c.drawPath(arrow, paint(WHITE))
        c.drawPath(arrow, paint((20, 20, 20), stroke=3))
    screen(st, T, t, d, fn, push=0.08, glow=(240, 170, 120))
    K.countdown(st.c, T)
    return st.arr


def s_built(T, t, d):
    """Built her way, the tutor asks, and she finds it herself."""
    st = D.Stage()
    screen(st, T, t, d, _chat(T), push=0.06)
    K.countdown(st.c, T)
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
    sets.staged(st, None, "jade", "gold")
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
    sets.staged(st, "indigo", "verm", "black")
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

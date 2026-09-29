"""The cold open (present), the chapter cards, CHAPTER ONE: CROWD (memory and fiction), and the end card."""
import math

import numpy as np
import skia

import cards as K
import draw as D
import figures as F
import props as P
import sets
from cues import C, CARDS, Wx, talk
from draw import (CREAM, GOLD, GOLDD, GOLDL, H, INK, JADE, LACQ, LAMP, PINK, VERM, W, WHITE, ease, mix, paint, path, ramp)
from timeline import TL

S, E = TL.s, TL.e


def cam(c, z, cx=540, cy=960):
    c.translate(cx, cy)
    c.scale(z, z)
    c.translate(-cx, -cy)


# ------------------------------------------------------------------ cold open: the present

def _table_top(c, T, on):
    """The table under the lamp: the calculus book, her sheet of scribbles, a pencil."""
    c.save()
    c.translate(600, 1330)
    c.rotate(-6)
    c.drawRect(skia.Rect.MakeLTRB(-260, -170, 260, 170), paint((120, 40, 40)))
    c.drawRect(skia.Rect.MakeLTRB(-250, -160, 250, 160), paint((140, 50, 46)))
    D.text(c, "CALCULUS", 0, -40, 64, "cormorant-700", mix((230, 214, 180), INK, 0.2 * (1 - on)), tag="book")
    D.text(c, "an introduction", 0, 10, 34, "cormorant-500i", (220, 200, 170), tag="book")
    c.restore()
    c.save()
    c.translate(300, 1420)
    c.rotate(8)
    c.drawRect(skia.Rect.MakeLTRB(-200, -120, 200, 140), paint((226, 222, 210)))
    for j in range(5):
        c.drawLine(-160, -70 + j * 44, 100 - 30 * (j % 2), -70 + j * 44, paint((90, 90, 110), stroke=4))
    D.text(c, "dy/dx ?", 40, 70, 48, "cormorant-600i" if False else "cormorant-500i", (40, 40, 90), tag="scrib")
    c.restore()
    c.drawLine(700, 1480, 900, 1420, paint((200, 160, 60), stroke=12))


def s_open_lamp(T, t, d):
    st = D.Stage((10, 12, 14))
    c = st.c
    on = ease(ramp(T, C["lamp_on"], C["lamp_on"] + 0.08))
    c.save()
    cam(c, 1.0 + 0.05 * t / max(d, 0.1), 560, 1250)
    sets.bd(st, "kitchen_night", lambda cc: sets.kitchen(cc))
    c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0), 0.72 - 0.38 * on))
    P.pool_of_light(c, 560, 1380, 560, 300, on, a=0.55)
    _table_top(c, T, on)
    bx, by = P.desk_lamp(c, 200, 1250, 1.05, on=on)
    P.light_cone(c, bx, by, 560, 1380, 380, on, a=0.22)
    c.restore()
    if on > 0.5:
        K.countdown(c, T)
    return st.arr


def s_open_room(T, t, d):
    """The kitchen at night, symmetrical: the window, the table, her at the laptop under the one lamp."""
    st = D.Stage()
    c = st.c
    c.save()
    cam(c, 1.0 + 0.04 * t / max(d, 0.1), 540, 1100)
    sets.bd(st, "kitchen_night", lambda cc: sets.kitchen(cc))
    c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0), 0.38))
    P.pool_of_light(c, 560, 1260, 520, 170, 1.0, a=0.5)
    P.laptop_back(c, 720, 1190, 0.55)
    bx, by = P.desk_lamp(c, 520, 1190, 0.6, side=1)
    P.light_cone(c, bx, by, 640, 1230, 240, 1.0, a=0.2)
    F.seated(c, 380, 1460, 0.52, T, action="type", lit=(255, 210, 150))
    c.restore()
    P.pool_of_light(c, 780, 1100, 200, 130, 1.0, color=(170, 200, 240), a=0.25)
    K.countdown(c, T)
    return st.arr


def s_open_profile(T, t, d):
    st = D.Stage((12, 10, 10))
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.rad((980, 700), 900, [(110, 80, 56), (30, 24, 22), (10, 10, 10)], [0, 0.5, 1])))
    F.profile(c, 470 - 10 * t, 760, 2.3 + 0.04 * t, T, mood="worry", light="lamp")
    K.countdown(c, T)
    return st.arr


# ------------------------------------------------------------------ the chapter cards and the end card

def _card(i):
    def f(T, t, d):
        st = D.Stage((0, 0, 0))
        K.chapter_card(st.c, T, i)
        return st.arr
    return f


s_card1, s_card2, s_card3, s_card4 = (_card(i) for i in range(4))


def s_end(T, t, d):
    st = D.Stage((0, 0, 0))
    K.end_card(st.c, T, T - t)
    return st.arr


# ------------------------------------------------------------------ ONE: CROWD (memory)

def _class_rows(c, T, hand=0.0, teacher_pose="write", girl=True, girl_scale=1.0, empty=0.0, lit_girl=0.0):
    """The classroom of thirty-eight, seen from behind her in the back row."""
    vx, vy = 540, 700
    desk_rows = [(0.34, 930), (0.42, 990), (0.52, 1065), (0.64, 1160), (0.8, 1280), (1.0, 1440)]
    P.hanging_bulb(c, 540, 330, 1.2, 1.0, cord=330)
    if teacher_pose:
        F.teacher(c, 460, 900, 0.34, T, pose=teacher_pose)
    rng = np.random.default_rng(5)
    n = 0
    for r, (s, y) in enumerate(desk_rows):
        cols = 6 if r < 5 else 5
        for q in range(cols):
            x = vx + (q - (cols - 1) / 2) * 170 * s
            c.drawPath(path([(x - 70 * s, y), (x + 70 * s, y), (x + 60 * s, y - 24 * s), (x - 60 * s, y - 24 * s)]),
                       paint((70, 64, 60)))
            if r == 5 and q == 2 and girl:
                continue
            n += 1
            if rng.random() < empty:
                continue
            F.child_back(c, x, y - 12 * s, s, hair=(26 + int(rng.uniform(0, 40)),) * 3,
                         shirt=(int(rng.uniform(170, 220)),) * 3, seed=n, T=T)
    if girl:                                                            # her, in the back row, closest to us
        F.child_back(c, 540, 1760, 2.6 * girl_scale, hair=(20, 20, 20), shirt=(186, 186, 186), hand=hand, seed=4, T=T)
        if lit_girl > 0:
            c.drawCircle(540, 1450, 520, paint((255, 250, 235), 0.2 * lit_girl, blur=120))


def s_class(T, t, d):
    st = D.Stage()
    c = st.c
    c.save()
    cam(c, 1.0 + 0.1 * ease(t / max(d, 0.1)), 540, 760)
    sets.bd(st, "classroom", sets.classroom, tex=0.06)
    _class_rows(c, T)
    c.restore()
    k = ease(ramp(T, Wx("a1", "Thirty-eight") - 0.1, Wx("a1", "Thirty-eight") + 0.4))
    if k > 0:
        c.drawRect(skia.Rect.MakeLTRB(150, 236, 930, 330), paint((0, 0, 0), 0.45 * k))
        D.text(c, "38 pupils  ·  1 teacher  ·  45 minutes", 540, 296, 44, "cormorant-600", WHITE, tag="count", a=k)
    k2 = ease(ramp(T, Wx("a1", "About") - 0.1, Wx("a1", "About") + 0.4))
    if k2 > 0:
        D.text(c, "about 1 minute each", 540, 400, 52, "cormorant-500i", WHITE, tag="count2", a=k2, outline=(0, 0, 0), ow=6)
    return st.arr


def s_question(T, t, d):
    """The teacher turns: 'Any questions?' - and in the back row, a hand goes up."""
    st = D.Stage()
    c = st.c
    c.save()
    cam(c, 1.35, 540, 900)
    sets.bd(st, "classroom", sets.classroom, tex=0.06)
    hand = ease(ramp(T, C["hand_up"], C["hand_up"] + 0.6))
    _class_rows(c, T, hand=hand, teacher_pose="front")
    c.restore()
    return st.arr


def s_bell(T, t, d):
    st = D.Stage((40, 40, 40))
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.rad((540, 800), 900, [(150, 150, 150), (40, 40, 40)])))
    ring = 1.0 if T >= C["bell"] else 0.0
    P.school_bell(c, 540, 860, 2.2, T, ring=ring)
    return st.arr


def s_hand_down(T, t, d):
    st = D.Stage()
    c = st.c
    c.save()
    cam(c, 1.2, 540, 1000)
    sets.bd(st, "classroom", sets.classroom, tex=0.06)
    hand = 1 - ease(ramp(t, 0.1, 1.1))
    _class_rows(c, T, hand=hand, teacher_pose="write", empty=ease(ramp(t, 0.3, d)) * 0.9)
    c.restore()
    return st.arr


def s_window(T, t, d):
    """Across the street: one lit window, a boy and his tutor at a desk under a lamp."""
    st = D.Stage()
    c = st.c
    c.save()
    cam(c, 1.0 + 0.3 * ease(t / max(d, 0.1)), 540, 820)
    sets.bd(st, "street", sets.street, tex=0.06)
    x0, y0, x1, y1 = 460, 590, 620, 780                                # the lit window (centre of the house)
    c.drawRect(skia.Rect.MakeLTRB(x0 - 40, y0 - 20, x1 + 40, y1 + 20), paint((24, 24, 24)))
    c.drawRect(skia.Rect.MakeLTRB(x0 - 30, y0 - 10, x1 + 30, y1 + 10), paint((236, 236, 230)))
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x0 - 30, y0 - 10, x1 + 30, y1 + 10))
    c.drawCircle(540, 690, 90, paint((255, 255, 250), 0.9, blur=30))
    F.sil_profile(c, 490, 790, 0.3, side=1, kind="boy", color=(30, 30, 30))
    F.sil_profile(c, 600, 790, 0.33, side=-1, kind="adult", color=(30, 30, 30))
    c.drawRect(skia.Rect.MakeLTRB(470, 760, 620, 770), paint((40, 40, 40)))
    P.hanging_bulb(c, 545, 700, 0.35, 1.0, cord=140)
    c.restore()
    c.drawLine(540, y0 - 10, 540, y1 + 10, paint((24, 24, 24), stroke=6))
    c.restore()
    rng = np.random.default_rng(int(T * 24))
    for i in range(90):                                                 # rain on her window
        x, y = rng.uniform(80, 1000), rng.uniform(90, 1630)
        c.drawLine(x, y, x - 4, y + 26, paint((200, 200, 200), 0.25, stroke=2))
    return st.arr


# ------------------------------------------------------------------ ONE: CROWD (fiction)

def _stage_desks(c, T, rows=4, lit=None, dim=0.6):
    """Rows of black lacquer desks on the gold floor, dim under one distant spot."""
    for r in range(rows):
        k = (r + 1) / rows
        y = 1100 + 420 * k ** 1.4
        s = 0.35 + 0.6 * k ** 1.4
        n = 7
        for q in range(n):
            x = 540 + (q - (n - 1) / 2) * 150 * s
            P.lacquer_desk(c, x, y, s, lit=(1.0 if lit and (r, q) in lit else 0.0))
    c.drawRect(skia.Rect.MakeLTRB(110, 1060, 970, 1560), paint((0, 0, 0), dim * 0.5))


def _prince_set(c, T):
    sets.stage(c, "gold")
    sets.spotlight(c, 540, 170, 540, 1150, 170, a=0.3)
    c.drawPath(path([(360, 1150), (720, 1150), (700, 1090), (380, 1090)]), paint(VERM))            # the dais
    c.drawLine(360, 1150, 720, 1150, paint(GOLDL, stroke=5))
    P.lantern(c, 540, 820, 0.8, 1.0, T, cord=650)
    F.robed(c, 450, 1110, 0.5, T, body=VERM, hat="crown")
    F.robed(c, 630, 1110, 0.56, T, body=(30, 36, 90), hat="cap", arms=0.3)
    _stage_desks(c, T)


def s_prince(T, t, d):
    """For most of history: a prince and his tutor in the light; everyone else in rows in the dark.
    Then the set splits in two and glides apart."""
    st = D.Stage((0, 0, 0))
    c = st.c
    k = ease(ramp(T, C["split98"], C["split98"] + 1.6))
    behind = lambda cc: _after_split(cc, T, ramp(T, C["split98"] + 0.8, C["split98"] + 1.6))
    behind(c)
    img = sets.layer(lambda cc: _prince_set(cc, T))
    c.save()
    cam(c, 1.0 + 0.05 * t / max(d, 0.1), 540, 1000)
    sets.split(c, img, k)
    c.restore()
    kb = ease(ramp(T, Wx("a6", "ninety-eight") - 0.3, Wx("a6", "ninety-eight") + 0.2)) * (1 - ease(ramp(T, C["split98"], C["split98"] + 0.5)))
    if kb > 0:
        P.banner(c, 540, 470, 800, 260, ["ONE-TO-ONE TUTORING", "the average tutored pupil outscored", "98% of the class"],
                 a=kb, sizes=(62, 40), src="Bloom, 1984")
    return st.arr


def _after_split(c, T, k):
    sets.stage(c, "indigo")
    P.banner(c, 540, 470, 820, 290, ["LATER STUDIES", "a smaller effect  ·  still one of the", "largest in education"],
             bg=(30, 36, 90), a=ease(k), sizes=(62, 42), src="VanLehn, 2011")
    P.lantern(c, 540, 900, 0.7, 1.0, T, cord=700)
    P.lacquer_desk(c, 540, 1300, 0.9, lit=1.0)


def s_aph1(T, t, d):
    """One lamp, one desk, one empty chair of light: attention was the expensive thing."""
    st = D.Stage((0, 0, 0))
    c = st.c
    c.save()
    cam(c, 1.0 + 0.06 * t / max(d, 0.1), 540, 1200)
    sets.bd(st, "stage_none", lambda cc: sets.stage(cc, None))
    sets.spotlight(c, 540, 170, 540, 1330, 200, a=0.28)
    P.lantern(c, 540, 980, 0.7, 1.0, T, cord=800)
    P.lacquer_desk(c, 540, 1330, 1.0, lit=1.0)
    c.restore()
    K.aphorism(c, T, "Attention was the most expensive thing in the room.", S("a7"), y=520, size=78)
    return st.arr

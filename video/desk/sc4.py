"""CHAPTER FOUR: DAWN - everyone it could reach, the languages, the evidence from Nigeria, the exam at nine, the
letter; then the three registers merge into one image: a light for every desk."""
import math

import numpy as np
import skia

import cards as K
import draw as D
import figures as F
import props as P
import sets
from cues import C, WHO_TAGS, Wx
from draw import (CREAM, GOLD, GOLDD, GOLDL, H, INK, JADE, LACQ, LAMP, PINK, VERM, W, WHITE, ease, mix, paint, path, ramp)
from sc1 import _class_rows, cam
from timeline import TL

S, E = TL.s, TL.e
INDIGO = (30, 36, 90)


def s_dawn(T, t, d):
    """07:30. The same kitchen in pale morning; the lamp is still on; her coat, her bag."""
    st = D.Stage()
    c = st.c
    c.save()
    cam(c, 1.0 + 0.04 * t / max(d, 0.1), 540, 1000)
    sets.bd(st, "kitchen_morning", lambda cc: sets.kitchen(cc, morning=True))
    bx, by = P.desk_lamp(c, 520, 1190, 0.6, side=1)
    P.light_cone(c, bx, by, 640, 1230, 240, 1.0, a=0.12)
    P.laptop_back(c, 720, 1190, 0.55, on=0.3)
    c.drawRect(skia.Rect.MakeLTRB(860, 1000, 890, 1500), paint((60, 56, 50)))
    c.drawPath(D.smooth([(880, 1010), (1010, 1030), (1030, 1300), (900, 1320)]), paint((110, 96, 80)))   # her coat
    c.restore()
    K.countdown(c, T)
    return st.arr


LEARNERS = [  # (x, colour): the boy whose letters swim, the second language, the village, the nurse, the 12-year-old
    (170, (244, 240, 232)), (355, (250, 210, 150)), (540, (180, 220, 200)), (725, (200, 200, 240)), (910, (250, 180, 200))]


def who_tag(c, T, y=430):
    """Who it helps most: the need, written large as each lamp comes on."""
    cur = [u for u in WHO_TAGS if u[0] <= T < u[1]]
    if not cur:
        return
    t0, t1, n, lab = cur[-1]
    k = ease(ramp(T, t0, t0 + 0.25)) * (1 - ease(ramp(T, t1 - 0.2, t1)))
    f = D.font("cormorant-700", 56)
    w = f.measureText(lab)
    c.drawRect(skia.Rect.MakeLTRB(540 - w / 2 - 50, y - 96, 540 + w / 2 + 50, y + 30), paint((0, 0, 0), 0.82 * k))
    c.drawLine(540 - w / 2 - 30, y + 26, 540 + w / 2 + 30, y + 26, paint(GOLD, k, stroke=2))
    D.text(c, "who it can help most", 540, y - 50, 34, "cormorant-500i", GOLDL, tag="whot", a=k)
    D.text(c, lab, 540, y + 8, 56, "cormorant-700", CREAM, tag="whot", a=k)


def s_lamps(T, t, d):
    """A vast dark stage: one by one, a lantern comes down over each learner at a desk, and their need is named."""
    st = D.Stage((0, 0, 0))
    c = st.c
    u = t / max(d, 0.1)
    c.save()
    cam(c, 1.12, 540, 1000)
    c.translate(70 - 140 * u, 0)                                        # a long lateral track past the learners
    sets.bd(st, "stage_none", lambda cc: sets.stage(cc, None))
    y = 1330
    for i, (x, col) in enumerate(LEARNERS):
        t0 = WHO_TAGS[i][0]
        k = ease(ramp(T, t0, t0 + 0.8))
        P.lantern(c, x, 700 + 260 * k, 0.42, k, T, cord=900)
        F.learner(c, x - 30, y, 0.5, T, color=mix((50, 50, 60), col, 0.25 + 0.75 * k), pose="sit", glow=k)
        P.lacquer_desk(c, x + 20, y + 10, 0.6, lit=k)
    c.restore()
    who_tag(c, T)
    return st.arr


WORDS = [("derivada", 250, 520), ("dérivée", 810, 520), ("Ableitung", 250, 760), ("pochodna", 810, 760),
         ("türev", 250, 1000), ("turunan", 810, 1000)]


def s_language(T, t, d):
    """Screens slide open on the same word in six languages; a voice-print for pronunciation; two figures talking."""
    st = D.Stage((0, 0, 0))
    c = st.c
    sets.bd(st, "stage_verm", lambda cc: sets.stage(cc, "verm"))
    c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0), 0.35))
    k40 = ease(ramp(T, S("e3") - 0.1, S("e3") + 0.4)) * (1 - ease(ramp(T, Wx("e3", "translate") - 0.4, Wx("e3", "translate"))))
    if k40 > 0:
        P.banner(c, 540, 700, 860, 300, ["40% OF PEOPLE", "have no schooling in a language", "they speak or understand"], bg=LACQ,
                 sizes=(76, 44), src="UNESCO Global Education Monitoring, 2025", a=k40)
    kt = ramp(T, Wx("e3", "translate") + 0.02, Wx("e3", "translate") + 1.4)
    if kt > 0 and T < Wx("e3", "coach") - 0.1:
        for i, (wd, x, y) in enumerate(WORDS):                          # sliding screens, each opening on a word
            o = ease(ramp(kt, i * 0.1, i * 0.1 + 0.5))
            c.drawRect(skia.Rect.MakeLTRB(x - 230, y - 100, x + 230, y + 100), paint((214, 204, 180)))
            D.text(c, wd, x, y + 22, 64, "cormorant-600", LACQ, tag=f"lang{i}", a=o)
            c.drawRect(skia.Rect.MakeLTRB(x - 230 + 460 * o, y - 100, x + 230, y + 100), paint(GOLDD))
            for j in range(3):
                xx = x - 230 + 460 * o + (230 - (230 * o)) * 0 + j * 150
                if xx < x + 230:
                    c.drawLine(xx, y - 100, xx, y + 100, paint(GOLD, 0.6, stroke=3))
            c.drawLine(x - 230 + 460 * o, y - 100, x - 230 + 460 * o, y + 100, paint(GOLDD, stroke=4))
        D.text(c, "“derivative”", 540, 1240, 54, "cormorant-500i", CREAM, tag="langsrc")
    kp = ramp(T, C["coach"] - 0.1, C["conv"] - 0.2)
    if 0 < kp < 1:                                                       # a voice-print: pronunciation, matched
        for i in range(60):
            x = 140 + i * 13.5
            h1 = 140 * abs(math.sin(i * 0.37 + T * 3)) * (0.4 + 0.6 * math.sin(i * 0.11) ** 2)
            c.drawLine(x, 800 - h1, x, 800 + h1, paint(GOLDL, stroke=7))
            h2 = h1 * (0.7 + 0.3 * math.sin(T * 4 + i))
            c.drawLine(x, 1100 - h2, x, 1100 + h2, paint(JADE, stroke=7))
        D.text(c, "yours", 540, 990, 44, "cormorant-500i", CREAM, tag="pr")
        D.text(c, "a native speaker", 540, 1290, 44, "cormorant-500i", CREAM, tag="pr2")
    kc = ramp(T, C["conv"] - 0.2, E("e3") + 0.4)
    if kc > 0:                                                           # the other side of a conversation
        F.robed(c, 360, 1400, 0.6, T, body=INDIGO, arms=0.3 + 0.2 * math.sin(T * 3))
        F.learner(c, 720, 1400, 0.62, T, pose="stand")
        for j in range(3):
            a = ease(ramp(kc, j * 0.2, j * 0.2 + 0.3))
            x = 430 + j * 110
            c.drawCircle(x, 900 + 20 * math.sin(T * 3 + j), 18, paint(CREAM, a))
    K.use_tag(c, T, y=380)
    return st.arr


def s_nigeria(T, t, d):
    """A whole hall of small lanterns lighting up: six weeks, and a year and a half of learning or more."""
    st = D.Stage((0, 0, 0))
    c = st.c
    u = t / max(d, 0.1)
    c.save()
    cam(c, 1.1, 540, 1250)
    c.translate(-60 + 120 * u, 0)                                       # tracking along the hall of lanterns
    sets.bd(st, "stage_none", lambda cc: sets.stage(cc, None))
    k = ramp(t, 0.2, d - 1.0)
    n = 0
    for r in range(4):
        for q in range(7):
            x, y = 190 + q * 117, 1150 + r * 110
            on = ease(ramp(k * 28, n, n + 1.5))
            P.lantern(c, x, y - 160, 0.22, on, T, cord=40)
            P.lacquer_desk(c, x, y, 0.4, lit=on)
            n += 1
    c.restore()
    P.banner(c, 540, 520, 880, 330, ["NIGERIA", "6 weeks of after-school AI tutoring in English:", "gains like 1.5 to 2 years",
                                     "of ordinary school"], bg=INDIGO, sizes=(76, 42), src="De Simone et al., World Bank, 2025")
    return st.arr


def _hall(c, T, t, d, z=1.0, cy=1000):
    c.save()
    cam(c, z, 540, cy)
    for x, y, s, r, q in sets.exam_desks():
        c.drawPath(path([(x - 95 * s, y), (x + 95 * s, y), (x + 80 * s, y - 34 * s), (x - 80 * s, y - 34 * s)]), paint((150, 140, 120)))
        if not (r == 5 and q == 0):
            F.child_back(c, x, y - 14 * s, s * 1.2, hair=(40, 34, 30), shirt=(120, 124, 128), seed=r * 7 + q + 10)
    c.restore()


def s_exam(T, t, d):
    """09:00. The exam hall in pale light; rows from behind; she is in the back row again."""
    st = D.Stage()
    c = st.c
    c.save()
    cam(c, 1.0 + 0.08 * ease(t / max(d, 0.1)), 540, 1100)
    sets.bd(st, "exam_hall", sets.exam_hall)
    P.wall_clock(c, 720, 440, 90, 9.0, face=(230, 228, 220), rim=(50, 50, 50))
    _hall(c, T, t, d)
    x, y, s = [(x, y, s) for x, y, s, r, q in sets.exam_desks() if r == 5 and q == 0][0]
    F.child_back(c, x, y - 14 * s, s * 1.2, hair=(24, 20, 18), shirt=(200, 170, 70), seed=5)     # her: the one mustard sweater, the bun
    c.restore()
    K.countdown(c, T)
    return st.arr


def s_q1(T, t, d):
    """Question one: a derivative, with an inside - and she multiplies by the inside."""
    st = D.Stage()
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.rad((540, 900), 1000, [(206, 204, 196), (170, 166, 156), (96, 92, 86)], [0, 0.6, 1])))
    D.text(c, "1.  Differentiate  (3x + 2)²", 540, 640, 60, "courier-400", INK, tag="q1")
    k1 = ease(ramp(t, 0.2, 0.9))
    k2 = ease(ramp(T, C["inside"] - 0.1, C["inside"] + 0.4))
    D.text(c, "= 2(3x + 2) · 3", 540, 820, 84, "cormorant-600", (40, 50, 110), tag="a1", a=k1)
    D.text(c, "= 6(3x + 2)", 540, 1000, 96, "cormorant-700", (40, 50, 110), tag="a2", a=k2)
    if k2 > 0:
        c.drawArc(skia.Rect.MakeLTRB(620, 720, 800, 860), 0, 360 * k2, False, paint(JADE, 0.8, stroke=6))
    c.drawLine(820, 1300, 980, 1060 + 20 * math.sin(T * 6), paint((200, 160, 60), stroke=14))
    return st.arr


def s_smile(T, t, d):
    st = D.Stage((200, 200, 196))
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.rad((1000, 600), 1100, [(236, 236, 228), (150, 150, 146), (80, 80, 80)], [0, 0.5, 1])))
    F.profile(c, 470, 780, 2.35, T, mood="smile", light="day")
    return st.arr


def s_letter(T, t, d):
    """Six weeks later: the letter on the kitchen table, in daylight, under the lamp that's off."""
    st = D.Stage()
    c = st.c
    c.save()
    cam(c, 1.3, 540, 1250)
    sets.bd(st, "kitchen_morning", lambda cc: sets.kitchen(cc, morning=True))
    c.restore()
    P.envelope(c, 540, 1120, 1.1, T, open_=ease(ramp(t, 0.1, 0.9)))
    return st.arr


def s_black(T, t, d):
    return D.Stage((0, 0, 0)).arr


def s_final(T, t, d):
    """The three registers meet: the classroom of thirty-eight (grey), the morning light of the present (pale), the
    gold of the stage - a lantern coming alight over every desk, front to back, the back row last."""
    st = D.Stage()
    c = st.c
    sets.bd(st, "classroom", sets.classroom, tex=0.06)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((236, 232, 220), 0.12))                          # the pale morning
    vx = 540
    rows = [(0.34, 930), (0.42, 990), (0.52, 1065), (0.64, 1160), (0.8, 1280), (1.0, 1440)]
    k = ramp(t, 0.3, min(d - 1.0, 4.0))
    for r, (s, y) in enumerate(rows):
        cols = 6 if r < 5 else 5
        for q in range(cols):
            x = vx + (q - (cols - 1) / 2) * 170 * s
            order = (5 - r) / 6                                          # the far rows light first, the back row last
            on = ease(ramp(k, order * 0.8, order * 0.8 + 0.25))
            P.lantern(c, x, y - 180 * s, 0.26 * s + 0.08, on, T, cord=200 * s)
            c.drawPath(path([(x - 70 * s, y), (x + 70 * s, y), (x + 60 * s, y - 24 * s), (x - 60 * s, y - 24 * s)]),
                       paint(mix((70, 64, 60), GOLD, on * 0.8)))
    F.child_back(c, 540, 1760, 2.6, hair=(20, 20, 20), shirt=(200, 170, 70), seed=5)
    kl = ease(ramp(k, 0.8, 1.0))
    c.drawCircle(540, 1500, 700, paint(GOLDL, 0.18 * kl, blur=160))
    K.aphorism(c, T, "A light for every desk.", S("e9"), y=470, size=96, color=WHITE)
    return st.arr

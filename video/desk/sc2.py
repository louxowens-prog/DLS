"""CHAPTER TWO: LIGHT - the real-life scenario at full strength. Her laptop, the tutor, the cars, the curve, the five
problems, the one mistake found; the memory of a test nobody read; the whole lesson hers."""
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
from script import LINES
from timeline import TL

S, E = TL.s, TL.e
SPOKEN = {k: sp for k, who, sp, cap, gap in LINES}

PROMPT1 = "Don't explain derivatives mathematically. Explain them using cars."
MSGS = [
    ("me", PROMPT1, C["type1"], E("b2q") - C["type1"] - 0.2),
    ("tutor", SPOKEN["b3"], S("b3"), E("b3") - S("b3")),
    ("me", "Now explain it visually.", S("b4"), E("b4") - S("b4")),
    ("tutor", SPOKEN["b5"], S("b5"), E("b5") - S("b5")),
    ("me", "Give me five problems.", S("b6"), E("b6") - S("b6")),
    ("tutor", "Here are five, about a car. Take your time.", E("b6") + 0.1, 0.6),
    ("me", "Show me exactly where my reasoning went wrong.", C["type4"], E("b7q") - C["type4"]),
    ("tutor", SPOKEN["b8"], S("b8"), E("b8") - S("b8")),
    ("tutor", "No rush. Try it your way first.", Wx("b11", "pace") - 0.3, 0.6),
    ("tutor", "Nice. Let's make the next one harder.", Wx("b11", "harder") - 0.2, 0.6),
    ("tutor", "One more with the chain rule - remember the inside.", Wx("b11", "chain") - 0.2, 0.6),
    ("tutor", "Now teach it back to me, in your own words.", Wx("b11", "midnight"), 0.7),
    ("me", "Never give me the answer. Make me find it.", S("d3q"), E("d3q") - S("d3q")),
    ("tutor", "Deal. I'll ask you questions instead.", E("d3q") - 0.1, 0.6),
    ("tutor", "So: what happens to the slope when the car speeds up?", S("d4") - 0.1, 0.5),
    ("me", "It gets steeper!", S("d4") + 0.55, 0.45),
]


def _room_dark(c, T, glow=(170, 200, 240)):
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.rad((540, 800), 1200, [(40, 46, 56), (12, 12, 14)])))


def screen(st, T, t, d, draw_fn, push=0.05, glow=(180, 205, 240)):
    """The laptop, straight on: a dark bezel, the screen, the keyboard edge - and the glow on everything."""
    c = st.c
    _room_dark(c, T, glow)
    c.save()
    cam(c, 1.0 + push * ease(t / max(d, 0.1)), 540, 800)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(40, 200, 1040, 1320), 30, 30), paint((20, 20, 22)))
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(80, 240, 1000, 1280))
    draw_fn(c)
    c.restore()
    c.drawPath(path([(0, 1320), (W, 1320), (W, 1400), (0, 1400)]), paint((44, 44, 48)))
    c.restore()
    c.drawRect(skia.Rect.MakeLTRB(0, 1400, W, H), paint((14, 14, 16)))
    c.drawCircle(540, 760, 700, paint(glow, 0.06, blur=200))


def _chat_bg(c):
    c.drawRect(skia.Rect.MakeLTRB(80, 240, 1000, 1280), paint((26, 30, 36)))
    return None


def _chat(T):
    return lambda c: _chat_bg(c) or P.chat(c, T, MSGS, x0=80, y0=520, x1=920, y_bottom=1280)


def s_clock1(T, t, d):
    """21:52. Her bakery apron over the chair; the clock on the wall."""
    st = D.Stage()
    c = st.c
    c.save()
    cam(c, 1.3, 540, 700)
    sets.bd(st, "kitchen_night", lambda cc: sets.kitchen(cc))
    c.restore()
    c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0), 0.35))
    P.wall_clock(c, 540, 640, 170, 21 + 52 / 60 - 12, face=(214, 210, 198), rim=(40, 40, 44))
    c.drawRect(skia.Rect.MakeLTRB(200, 1000, 230, 1700), paint((30, 26, 24)))                       # the chair back
    c.drawRect(skia.Rect.MakeLTRB(200, 1000, 520, 1030), paint((30, 26, 24)))
    c.drawPath(D.smooth([(230, 1010), (420, 1000), (460, 1150), (430, 1400), (260, 1420), (240, 1150)]), paint((200, 190, 170)))
    D.text(c, "BAKERY", 345, 1200, 34, "cormorant-700", (120, 90, 70), tag="apron")
    P.pool_of_light(c, 700, 1300, 400, 160, 1.0, a=0.3)
    K.countdown(c, T)
    return st.arr


def s_type1(T, t, d):
    st = D.Stage()
    screen(st, T, t, d, _chat(T))
    K.countdown(st.c, T)
    return st.arr


def _car_set(c, T, phase):
    sets.stage(c, "pink")
    sets.spotlight(c, 540, 170, 540, 1300, 260, a=0.25)
    c.drawPath(path([(110, 1290), (970, 1290), (1080, 1400), (0, 1400)]), paint(GOLDL))        # the gold road
    c.drawLine(0, 1345, W, 1345, paint(VERM, stroke=6))
    P.car(c, 200 + 680 * ramp(T, S("b3") - 0.2, C["turn"]), 1340, 0.9)
    lit_o = ease(ramp(T, C["odo"] - 0.1, C["odo"] + 0.4))
    lit_s = ease(ramp(T, C["speedo"] - 0.1, C["speedo"] + 0.4))
    P.dial(c, 320, 760, 170, (T * 0.05) % 1.0, "HOW FAR", T, col=mix(GOLDD, GOLD, lit_o))
    P.dial(c, 760, 760, 170, 0.35 + 0.25 * math.sin(T * 1.8) * lit_s, "HOW FAST", T, col=mix(GOLDD, GOLD, lit_s))
    D.text(c, f"{int(1000 + T * 37) % 100000:05d}", 320, 700, 46, "courier-400", LACQ, tag="odo")


def _deriv_set(c, T):
    sets.stage(c, "jade", floor="black", posts="gold")
    P.lantern(c, 540, 700, 0.6, 1.0, T, cord=520)
    P.banner(c, 540, 1120, 820, 300, ["speed  =  d(distance) / d(time)", "the rate of change, at one instant"],
             bg=LACQ, sizes=(64, 42))


def s_car(T, t, d):
    st = D.Stage((0, 0, 0))
    c = st.c
    k = ramp(T, C["turn"] - 0.3, C["turn"] + 0.9)
    if k <= 0:
        _car_set(c, T, 0)
    elif k >= 1:
        _deriv_set(c, T)
    else:
        sets.turn(c, sets.layer(lambda cc: _car_set(cc, T, 0)), sets.layer(lambda cc: _deriv_set(cc, T)), k)
    K.use_tag(c, T, y=380)
    return st.arr


def s_type2(T, t, d):
    st = D.Stage()
    screen(st, T, t, d, _chat(T))
    K.countdown(st.c, T)
    return st.arr


def s_graph(T, t, d):
    st = D.Stage()
    u = 0.15 + 0.7 * ease(ramp(t, 0.3, d - 0.2))
    tan = ease(ramp(T, Wx("b5", "steep") - 0.3, Wx("b5", "steep") + 0.2))
    screen(st, T, t, d, lambda c: _chat_bg(c) or P.graph(c, T, 80, 520, 1000, 1280, u, show_tangent=tan), push=0.04)
    c = st.c
    K.use_tag(c, T, y=470)
    K.countdown(c, T)
    return st.arr


def s_type3(T, t, d):
    st = D.Stage()
    screen(st, T, t, d, _chat(T))
    K.use_tag(st.c, T, y=470)
    K.countdown(st.c, T)
    return st.arr


def _paper_room(st, T, t, d, z=1.0, cx=540, cy=1000):
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((60, 50, 40)))
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.rad((540, 900), 1100, [(120, 100, 80), (46, 40, 32), (18, 16, 14)], [0, 0.6, 1])))


def s_paper(T, t, d):
    """Overhead, under the lamp: the five problems, her answers, then four ticks and one cross."""
    st = D.Stage()
    c = st.c
    _paper_room(st, T, t, d)
    c.save()
    cam(c, 1.0 + 0.05 * t / max(d, 0.1), 540, 1000)
    P.problems(c, T, 150, 560, 780, t0=E("b6") + 0.3, per=0.22, marks_at=S("b7") + 0.25, size=48)
    c.drawLine(900, 1500, 1000, 1330 - 100 * math.sin(T * 5), paint((200, 160, 60), stroke=14))   # her pencil
    c.restore()
    K.use_tag(c, T, y=430)
    K.countdown(c, T)
    return st.arr


def s_type4(T, t, d):
    st = D.Stage()
    screen(st, T, t, d, _chat(T))
    K.use_tag(st.c, T, y=470)
    K.countdown(st.c, T)
    return st.arr


def s_error(T, t, d):
    """Problem five, up close: the ring round what she missed, and the fix."""
    st = D.Stage()
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.rad((540, 900), 1000, [(200, 196, 184), (160, 152, 136), (80, 72, 64)], [0, 0.6, 1])))
    for j in range(24):
        c.drawLine(0, 520 + j * 50, W, 520 + j * 50, paint((170, 190, 210), 0.3, stroke=2))
    ring = ease(ramp(T, C["ring"] - 0.2, C["ring"] + 0.5))
    fix = ease(ramp(T, C["fix"] - 0.2, C["fix"] + 0.3))
    c.save()
    cam(c, 1.0 + 0.06 * t / max(d, 0.1), 540, 900)
    P.working(c, T, 540, 720, circle=ring, fix=fix, size=74)
    c.restore()
    K.use_tag(c, T, y=430)
    K.countdown(c, T)
    return st.arr


def s_old_test(T, t, d):
    st = D.Stage((30, 30, 30))
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.rad((540, 900), 1000, [(120, 120, 120), (30, 30, 30)])))
    c.save()
    cam(c, 1.0 + 0.08 * t / max(d, 0.1), 540, 900)
    P.old_test(c, 540, 900, 1.25, T)
    c.restore()
    return st.arr


def s_profile2(T, t, d):
    st = D.Stage((12, 10, 10))
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.rad((1000, 760), 900, [(120, 88, 60), (30, 24, 22), (10, 10, 10)], [0, 0.5, 1])))
    F.profile(c, 470, 760, 2.4 + 0.05 * t, T, mood="tear", light="lamp", tear=ease(ramp(t, 0.4, 1.4)))
    return st.arr


def _ladder(c, T, k):
    """Difficulty, climbing only when she gets them right."""
    for i in range(5):
        y = 1200 - i * 125
        x = 250 + i * 120
        on = k * 5 > i
        c.drawRect(skia.Rect.MakeLTRB(x, y, x + 240, y + 26), paint((120, 170, 230) if on else (60, 66, 76)))
        D.text(c, f"level {i + 1}", x + 120, y - 16, 34, "inter-500", (200, 206, 214) if on else (110, 116, 126), tag="lvl")


def s_montage(T, t, d):
    """It goes at her pace, climbs only when she's right, slips in the chain rule she always forgets."""
    st = D.Stage()
    ph_h, ph_c = Wx("b11", "harder") - 0.2, Wx("b11", "chain") - 0.2

    def fn(c):
        if T < ph_h:
            _chat_bg(c)
            P.chat(c, T, MSGS, x0=80, y0=520, x1=920, y_bottom=1280)
        elif T < ph_c:
            c.drawRect(skia.Rect.MakeLTRB(80, 240, 1000, 1280), paint((26, 30, 36)))
            D.text(c, "difficulty", 540, 600, 44, "inter-700", (200, 206, 214), tag="ui")
            _ladder(c, T, 0.4 + 0.6 * ease(ramp(T, ph_h, ph_c - 0.3)))
        else:
            c.drawRect(skia.Rect.MakeLTRB(80, 240, 1000, 1280), paint((26, 30, 36)))
            k = ease(ramp(T, ph_c, ph_c + 0.5))
            c.save()
            c.translate(540 + 400 * (1 - k), 760)
            c.rotate(-3)
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-360, -230, 360, 230), 24, 24), paint((246, 240, 222)))
            D.text(c, "CHAIN RULE", 0, -110, 64, "inter-700", (40, 44, 60), tag="flash")
            D.text(c, "remember the inside:", 0, -10, 44, "inter-500", (60, 64, 80), tag="flash")
            D.text(c, "d/dx (3x + 2)²  =  2(3x + 2) · 3", 0, 100, 46, "inter-700", (120, 20, 20), tag="flash")
            c.restore()
    screen(st, T, t, d, fn, push=0.03)
    K.use_tag(st.c, T, y=470)
    K.countdown(st.c, T)
    return st.arr


def s_teachback(T, t, d):
    """00:04. She explains it back, out loud, hands moving; the screen listens."""
    st = D.Stage()
    c = st.c
    c.save()
    cam(c, 1.12, 560, 1150)
    sets.bd(st, "kitchen_night", lambda cc: sets.kitchen(cc))
    c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0), 0.45))
    P.pool_of_light(c, 560, 1260, 520, 170, 1.0, a=0.5)
    P.laptop_back(c, 720, 1190, 0.55)
    bx, by = P.desk_lamp(c, 520, 1190, 0.6, side=1)
    P.light_cone(c, bx, by, 640, 1230, 240, 1.0, a=0.2)
    F.seated(c, 380, 1460, 0.52, T, action="talk", lit=(255, 210, 150), head_tilt=-4)
    c.restore()
    K.use_tag(c, T, y=470)
    K.countdown(c, T)
    return st.arr


def s_aph2(T, t, d):
    """One desk on the great stage; the lantern comes down over it, and it is hers."""
    st = D.Stage((0, 0, 0))
    c = st.c
    sets.staged(st, "gold", "gold", "black")
    c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0), 0.45))
    k = ease(ramp(t, 0.0, 2.0))
    sets.spotlight(c, 540, 170, 540, 1330, 230, a=0.35)
    P.lantern(c, 540, 700 + 220 * k, 0.8, 1.0, T, cord=900)
    P.lacquer_desk(c, 540, 1330, 1.1, lit=1.0)
    F.learner(c, 420, 1330, 0.55, T, pose="sit", glow=k)
    K.aphorism(c, T, "For the first time, the whole lesson was mine.", S("b12"), y=430, size=76)
    return st.arr

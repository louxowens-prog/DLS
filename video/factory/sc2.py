"""Scenes 2: the great door, the wonderland (the ballad), the four rooms, the four guests, the workers' chants."""
import math

import numpy as np
import skia

import cast
import draw as D
import props as P
import sets
from cues import C, ls, talk
from draw import (CHERRY, CHOC, CREAM, GOLD, GOLD2, GOLD3, H, INK, LEMON, LILAC, MINT, PINK, W, WHITE, ease, mix, paint,
                  path, ramp)
from sc1 import cam, chip, title_words
from script import ROOMS
from timeline import TL

S, E, Wd = TL.s, TL.e, TL.word


def s_door(T, t, d):
    st = D.Stage()
    c = st.c
    D.backdrop(st, "hall", sets.hall)
    k = ease(ramp(T, C["door_open"], C["door_open"] + 3.0))
    c.save()
    cam(c, 1.0 + 0.25 * k, 540, 1000)
    sets.door(c, 540, 1560, 1.0, k, T)
    c.restore()
    for who, x in (("copier", 170), ("believer", 360), ("you", 540), ("yesman", 720), ("rusher", 900)):
        cast.person(c, who, x, 2050, 0.62, T, pose="stand", mood="wow", alpha=0.95)     # backs to us, in silhouette
    c.drawRect(skia.Rect.MakeLTRB(0, 1500, W, H), paint(INK, 0.55))
    return st.arr


def _wonder(st, T, z=1.0, cx=540, cy=1000, riv=True):
    c = st.c
    c.save()
    cam(c, z, cx, cy)
    D.backdrop(st, "wonder", sets.wonder)
    if riv:
        sets.river(c, T)
    c.restore()


def _sparkle(c, T, n=30, seed=1, a=0.8):
    rng = np.random.default_rng(seed)
    for i in range(n):
        x, y = rng.uniform(0, W), rng.uniform(200, 1300)
        tw = 0.5 + 0.5 * math.sin(T * rng.uniform(2, 5) + i)
        r = 6 + 8 * tw
        col = [WHITE, LEMON, PINK][i % 3]
        c.drawLine(x - r, y, x + r, y, paint(col, a * tw, stroke=3))
        c.drawLine(x, y - r, x, y + r, paint(col, a * tw, stroke=3))


def s_wonder_wide(T, t, d):
    st = D.Stage()
    z = 1.35 - 0.3 * ease(t / max(d, 0.1))                             # the slow zoom back to reveal it all
    _wonder(st, T, z, 540, 1050)
    c = st.c
    for who, x in (("copier", 250), ("believer", 400), ("you", 540), ("yesman", 680), ("rusher", 820)):
        cast.person(c, who, x, 1860, 0.3, T, pose="stand", mood="wow")
    _sparkle(c, T)
    return st.arr


def s_wonder_river(T, t, d):
    st = D.Stage()
    _wonder(st, T, 1.7, 220, 1150)
    c = st.c
    cast.person(c, "copier", 760, 1850, 0.62, T, pose="reach", mood="wow")
    cast.person(c, "believer", 980, 1900, 0.62, T, pose="clasp", mood="wow")
    _sparkle(c, T, 20, 3)
    return st.arr


def s_wonder_host(T, t, d):
    st = D.Stage()
    _wonder(st, T, 1.4, 700, 900, riv=False)
    c = st.c
    sway = 6 * math.sin(T * 1.8)
    cast.person(c, "host", 540, 1900, 1.02, T, pose="arms_out", mood="smile", tilt=sway, talk=talk("HOST", T))
    _sparkle(c, T, 36, 5)
    return st.arr


def s_wonder_you(T, t, d):
    """Every expert you could never afford, patient at two in the morning: portraits circling you; a moon clock."""
    st = D.Stage()
    _wonder(st, T, 1.25, 540, 1000)
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((255, 220, 170), 0.12))
    experts = ["doctor", "farmer", "student", "yesman", "believer", "host"]
    labels = ["DOCTOR", "ENGINEER", "PROFESSOR", "LAWYER", "SCIENTIST", "TEACHER"]
    for i, (who, lab) in enumerate(zip(experts, labels)):
        a = i / 6 * 2 * math.pi + t * 0.5
        x, y = 540 + 380 * math.cos(a), 760 + 250 * math.sin(a)
        D.shade(c, D.rrect(x - 90, y - 120, x + 90, y + 110, 12), GOLD, k=0.3)
        c.drawRect(skia.Rect.MakeLTRB(x - 72, y - 102, x + 72, y + 70), paint((250, 240, 220)))
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(x - 72, y - 102, x + 72, y + 70))
        cast.person(c, who, x, y + 480, 0.52, T, pose="stand", mood="smile", shadow=False)
        c.restore()
        D.text(c, lab, x, y + 100, 22, "fraunces-900", (80, 50, 10), tag="portrait")
    hand = cast.person(c, "you", 540, 1850, 0.78, T, pose="arms_out", mood="wow")
    k = ease(ramp(T, Wd("r0", "patient") - 0.2, Wd("r0", "patient") + 0.4))
    if k > 0:
        P.clock(c, 540, 330 + 0 * k, 110 * k + 1, 2.0, T, face=(240, 236, 210))
        c.drawCircle(700, 290, 50 * k, paint((250, 246, 220)))
        c.drawCircle(724, 276, 44 * k, paint((255, 214, 150)))
    return st.arr


# ------------------------------------------------------------------ the rooms

def _plaque(n, T, t, d):
    st = D.Stage()
    c = st.c
    D.backdrop(st, f"room{n}", lambda cc: sets.room(cc, n))
    c.drawRect(skia.Rect.MakeWH(W, H), paint(INK, 0.35))
    D.shade(c, D.rrect(170, 260, 910, 1290, 30), (120, 80, 60), k=0.3)                                # the door
    for j in range(2):
        c.drawRect(skia.Rect.MakeLTRB(230, 820 + j * 220, 850, 1000 + j * 220), paint((90, 60, 44), stroke=8))
    c.drawCircle(810, 900, 26, paint(GOLD))
    name, uses = ROOMS[n]
    k = ease(ramp(t, 0.1, 0.6))
    c.save()
    cam(c, 0.9 + 0.1 * k, 540, 500)
    P.plaque(c, 540, 330, n, name, uses, a=k)
    c.restore()
    cast.person(c, "host", 940, 1820, 0.6, T, pose="present", mood="sly", talk=talk("HOST", T))
    return st.arr


def s_plaque1(T, t, d):
    return _plaque(1, T, t, d)


def s_plaque2(T, t, d):
    return _plaque(2, T, t, d)


def s_plaque3(T, t, d):
    return _plaque(3, T, t, d)


def s_plaque4(T, t, d):
    return _plaque(4, T, t, d)


def _room(st, n):
    D.backdrop(st, f"room{n}", lambda cc: sets.room(cc, n))


def s_room1(T, t, d):
    st = D.Stage()
    c = st.c
    _room(st, 1)
    k = ease(ramp(t, 0.6, d))
    P.taffy_puller(c, 480, 1180, 1.25, T, untangle=k)
    P.letter(c, 170 - 40 * k, 560, 0.34, T, plain=0.0, rot=-8)
    cast.person(c, "you", 880, 1860, 0.62, T, pose="clasp", mood="wow")
    return st.arr


def s_room1_letter(T, t, d):
    st = D.Stage()
    c = st.c
    _room(st, 1)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(INK, 0.3))
    P.letter(c, 540, 860, 1.35, T, plain=ease(ramp(t, 0.1, max(0.5, d - 0.4))), rot=-1)
    k = ramp(t, 1.2, 1.6)
    if k > 0:
        chip(c, "“explain it simpler”  ·  “and again”", 540, 1280, 30, a=k)
    return st.arr


def s_copier(T, t, d):
    """He gulps the answer whole with his big spoon - and blows up like a balloon and floats away."""
    st = D.Stage()
    c = st.c
    _room(st, 1)
    P.taffy_puller(c, 300, 1180, 0.9, T, untangle=1.0)
    g = ease(ramp(T, C["gulp"], C["gulp"] + 0.9))
    up = ease(ramp(T, C["gulp_up"] + 0.4, C["gulp_up"] + 2.2))
    x, y = 720, 1760 - 1500 * up
    if g < 0.05:
        hand = cast.person(c, "copier", x, y, 0.8, T, pose="reach", mood="wow", talk=talk("COPIER", T))
        c.drawLine(hand[0], hand[1], hand[0] - 150, hand[1] - 80, paint((200, 200, 210), stroke=14))   # the giant spoon
        D.shade(c, D.oval(hand[0] - 230, hand[1] - 130, hand[0] - 130, hand[1] - 60), (210, 210, 220), k=0.3)
    else:
        r = 110 + 230 * g                                               # inflating
        c.save()
        c.translate(x, y - 300 - r * 0.6)
        D.shade(c, D.circle(0, 0, r), (210, 50, 60), k=0.3)
        c.save()
        c.clipPath(D.circle(0, 0, r), doAntiAlias=True)
        for j in range(-4, 5):
            c.drawRect(skia.Rect.MakeLTRB(-r, j * r * 0.22, r, j * r * 0.22 + r * 0.1), paint(WHITE, 0.85))
        c.restore()
        c.save()
        c.translate(0, -r - 50)
        c.scale(1.2, 1.2)
        cast.face(c, cast.LOOKS["copier"], "wow", 0, False, 0.0, 50)
        c.restore()
        for sx in (-1, 1):
            D.shade(c, D.capsule(sx * r * 0.7, -r * 0.4, sx * (r + 60), -r * 0.8, 40), (210, 50, 60), k=0.2)
            D.shade(c, D.capsule(sx * 50, r * 0.9, sx * 60, r + 90, 36), (40, 50, 100), k=0.2)
        c.restore()
    return st.arr


def _workers(st, T, n, sk, verse_pose="cheer"):
    """The little workers in a chorus line, bobbing on the beat; the verse from the leader, the refrain from all."""
    c = st.c
    S_ = TL.songs[sk]
    beat = S_["beat"]
    lines = [TL.lines[l["key"]] for l in S_["lines"]]
    on_refrain = T >= lines[-1]["start"] - 0.1
    for i in range(5):
        x = 140 + i * 200
        ph = ((T - S_["start"]) / beat + i * 0.5) % 2
        hop = 22 * abs(math.sin(ph * math.pi))
        pose = ("cheer" if int((T - S_["start"]) / beat) % 2 == 0 else "fists") if on_refrain else ("point" if i % 2 else "stand")
        tk = talk("WORKERS", T) if (on_refrain or i == 2) else 0.0
        cast.worker(c, x, 1260, 0.82, T, pose=pose, bob=hop, talk=tk)


def _chant(n, sk, T, t, d, gag):
    st = D.Stage()
    c = st.c
    _room(st, n)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((255, 220, 160), 0.12))
    gag(c, T, t)
    _workers(st, T, n, sk)
    return st.arr


def s_chant1(T, t, d):
    def gag(c, T, t):                                                   # the balloon boy drifts about up by the ceiling
        x, y = 540 + 260 * math.sin(t * 0.7), 420 + 30 * math.sin(t * 1.3)
        D.shade(c, D.circle(x, y, 200), (210, 50, 60), k=0.3)
        c.save()
        c.clipPath(D.circle(x, y, 200), doAntiAlias=True)
        for j in range(-4, 5):
            c.drawRect(skia.Rect.MakeLTRB(x - 200, y + j * 44, x + 200, y + j * 44 + 20), paint(WHITE, 0.85))
        c.restore()
        c.save()
        c.translate(x, y - 230)
        cast.face(c, cast.LOOKS["copier"], "worry", 0, False, 0.0, 50)
        c.restore()
    return _chant(1, "w1", T, t, d, gag)


def s_room2(T, t, d):
    st = D.Stage()
    c = st.c
    _room(st, 2)
    down = abs(math.sin(t * 2.2)) * ease(ramp(t, 0.3, 1.0))
    cnt = 50 - int(44 * ease(ramp(T, C["fifty_in"] + 0.5, C["six_out"])))
    P.press(c, 540, 1240, 1.0, T, down=down, count=cnt)
    P.reports(c, 540, 1180, max(6, cnt), 0.8, seed=4)
    cast.person(c, "you", 930, 1880, 0.55, T, pose="clasp", mood="wow")
    return st.arr


def s_room2_flag(T, t, d):
    st = D.Stage()
    c = st.c
    _room(st, 2)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(INK, 0.25))
    for i in range(6):                                                  # the six pages that matter, glowing
        x, y = 200 + (i % 3) * 340, 500 + (i // 3) * 380
        c.drawRect(skia.Rect.MakeLTRB(x - 120, y - 150, x + 120, y + 150), paint((255, 230, 150), 0.35, blur=20))
        D.shade(c, D.rrect(x - 110, y - 140, x + 110, y + 140, 6), CREAM, k=0.08)
        D.text(c, f"STUDY {[3, 12, 17, 24, 31, 44][i]}", x, y - 90, 30, "oldstandard-700", INK, tag="page")
        for j in range(4):
            c.drawLine(x - 80, y - 40 + j * 40, x + 80, y - 40 + j * 40, paint((150, 140, 120), stroke=5))
    k = ease(ramp(T, C["disagree"] - 0.3, C["disagree"] + 0.2))
    if k > 0:                                                           # the red flag where two disagree
        for x, y in ((540, 500), (540, 880)):
            c.drawCircle(x, y, 150, paint(CHERRY, k, stroke=10))
        c.drawLine(540, 650, 540, 730, paint(CHERRY, k, stroke=8))
        chip(c, "STUDY 12 SAYS 30%   ·   STUDY 31 SAYS 3%", 540, 1180, 30, fg=WHITE, bg=(160, 30, 40), a=k)
    return st.arr


def s_room2_clock(T, t, d):
    st = D.Stage()
    c = st.c
    _room(st, 2)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(INK, 0.3))
    P.clock(c, 300, 700, 170, 3.0 * ease(ramp(t, 0, 1.2)), T, face=(200, 196, 186))
    D.text(c, "SEARCHING", 300, 960, 54, "fraunces-900", (190, 180, 170), tag="clock", outline=INK, ow=8)
    k = ease(ramp(T, C["thinking"] - 0.6, C["thinking"]))
    c.drawLine(140, 945, 460, 945, paint(CHERRY, k, stroke=10))
    P.clock(c, 780, 700, 170, 3.0 * ease(ramp(t, 1.2, 2.4)), T, face=(255, 236, 170))
    D.text(c, "THINKING", 780, 960, 58, "fraunces-900", GOLD2, tag="clock", outline=INK, ow=8, a=0.4 + 0.6 * k)
    title_words(c, "SAME 3 HOURS", 540, 1180, 84, S("r2b") + 0.3, T)
    return st.arr


def s_believer(T, t, d):
    """She drinks from the Sounds-Sure tap without checking a drop - and the pipe sucks her up."""
    st = D.Stage()
    c = st.c
    _room(st, 2)
    D.shade(c, D.rrect(700, 0, 820, 700, 40), (200, 150, 70), k=0.35)                                  # the pipe
    D.shade(c, D.rrect(620, 640, 900, 760, 40), (200, 150, 70), k=0.35)
    chip(c, "SOUNDS-SURE SYRUP", 760, 820, 28, fg=(80, 40, 10), bg=GOLD2)
    up = ease(ramp(T, C["sucked"], C["sucked"] + 1.0))
    stretch = 1 + 1.6 * up
    y = 1800 - 1300 * up
    c.save()
    c.translate(760, y)
    c.scale(1 / math.sqrt(stretch), stretch)
    cast.person(c, "believer", 0, 0, 0.72, T, pose="clasp" if up == 0 else "arms_up", mood="smile" if up == 0 else "wow",
                talk=talk("BELIEVER", T), shadow=False)
    c.restore()
    if C["sip"] < T < C["sucked"]:
        c.drawLine(760, 760, 760, 1000, paint((230, 190, 120), 0.9, stroke=18))
    return st.arr


def s_chant2(T, t, d):
    def gag(c, T, t):                                                   # her flowered hat, spinning down from the pipe
        D.shade(c, D.rrect(700, 0, 820, 520, 40), (200, 150, 70), k=0.35)
        y = 300 + (t * 180) % 500
        c.save()
        c.translate(760 + 60 * math.sin(t * 3), y)
        c.rotate(t * 90)
        D.shade(c, D.oval(-120, -30, 120, 30), (170, 120, 200), k=0.25)
        for j in range(6):
            c.drawCircle(-80 + j * 32, -20, 12, paint([LEMON, PINK, WHITE][j % 3]))
        c.restore()
    return _chant(2, "w2", T, t, d, gag)


def s_room3(T, t, d):
    st = D.Stage()
    c = st.c
    _room(st, 3)
    P.mirror(c, 300, 1250, 0.95, T, mood="sly", talk=0.0)
    P.scales(c, 740, 1180, 0.72, T, tip=math.sin(t * 1.2))
    k = ease(ramp(T, C["hole"] - 0.3, C["hole"] + 0.3))
    if k > 0:                                                           # the hole in your own reasoning, ringed in red
        D.shade(c, D.rrect(560, 300, 980, 700, 10), CREAM, k=0.08)
        D.text(c, "MY PLAN", 770, 380, 40, "fraunces-900", INK, tag="plan")
        for j, ln in enumerate(["wait and see", "because he's young", "so it's probably fine"]):
            D.text(c, ln, 770, 450 + j * 70, 34, "oldstandard-700", INK, tag="plan")
        c.drawOval(skia.Rect.MakeLTRB(600, 500 + 0, 950, 620), paint(CHERRY, k, stroke=9))
        chip(c, "ASSUMPTION!", 770, 680, 28, fg=WHITE, bg=CHERRY, a=k)
    return st.arr


def s_yesman(T, t, d):
    """He asks only to be told he's right. The mirror obliges - and he shrinks, and shrinks."""
    st = D.Stage()
    c = st.c
    _room(st, 3)
    P.mirror(c, 300, 1350, 1.05, T, mood="smile" if T >= C["youre_right"] else "flat", talk=talk("MIRROR", T))
    sh = ease(ramp(T, C["shrink"], C["shrink"] + 1.4))
    s = 0.85 * (1 - 0.85 * sh)
    hand = cast.person(c, "yesman", 760, 1820, s, T, pose="hold", mood="smile", talk=talk("YESMAN", T))
    if sh < 0.3:
        D.shade(c, D.oval(hand[0] - 30, hand[1] - 40, hand[0] + 30, hand[1] + 10), (200, 220, 230), k=0.3)
    return st.arr


def s_chant3(T, t, d):
    def gag(c, T, t):                                                   # the tiny yes-man, pacing on a footstool
        D.shade(c, D.rrect(720, 560, 960, 640, 12), GOLD3, k=0.3)
        D.shade(c, D.rrect(740, 640, 770, 800, 6), GOLD3, k=0.3)
        D.shade(c, D.rrect(910, 640, 940, 800, 6), GOLD3, k=0.3)
        cast.person(c, "yesman", 840 + 50 * math.sin(t * 2), 560, 0.2, T, pose="shrug", mood="worry", walk=t)
    return _chant(3, "w3", T, t, d, gag)


HYP = ["his spine?", "a nerve?", "an old fall?", "his posture?", "a vitamin?", "genetics?"]


def s_room4_fizz(T, t, d):
    st = D.Stage()
    c = st.c
    _room(st, 4)
    P.kettle(c, 540, 1300, 1.0, T)
    popped = (1, 2, 3, 4, 5) if T >= C["pop"] else ()
    P.bubbles(c, T, HYP, 540, 1050, 380, t0=T - t + 0.2, gold=0 if T >= C["pop"] else None, popped=popped)
    k = ease(ramp(T, C["wait"] - 0.4, C["wait"] + 0.1))
    if k > 0:                                                           # the what-if chalk branches
        c.drawLine(120, 360, 250, 300, paint(WHITE, k, stroke=5))
        c.drawLine(120, 360, 250, 420, paint(WHITE, k, stroke=5))
        D.text(c, "WAIT →", 140, 330, 30, "special-elite-400", WHITE, tag="chalk", a=k, align="left")
    return st.arr


def s_room4_plan(T, t, d):
    st = D.Stage()
    c = st.c
    _room(st, 4)
    bake = ease(ramp(t, 0.1, 0.8))
    P.oven(c, 540, 1300, 1.0, T, glow=bake)
    for i in range(6):                                                  # the fog of worry going in
        a = t * 1.5 + i
        c.drawCircle(540 + 180 * math.cos(a) * (1 - bake), 1000 + 60 * math.sin(a) * (1 - bake), 70 * (1 - bake) + 1,
                     paint((255, 200, 230), 0.7 * (1 - bake)))
    k = ease(ramp(t, 0.8, 1.6))
    if k > 0:
        P.plan_card(c, 540, 700, 0.95, T, k)
    return st.arr


def s_rusher(T, t, d):
    """She grabs the first bubble and runs - straight onto the trapdoor."""
    st = D.Stage()
    c = st.c
    _room(st, 4)
    P.kettle(c, 300, 1300, 0.8, T)
    fall = ease(ramp(T, C["drop"], C["drop"] + 0.6))
    run = ease(ramp(T, C["grab"], C["drop"]))
    x = 300 + 400 * run
    c.drawRect(skia.Rect.MakeLTRB(620, 1720, 900, 1780), paint(INK, 0.9 if fall > 0 else 0.0))       # the trapdoor
    if fall < 1:
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(0, 0, W, 1760))
        hand = cast.person(c, "rusher", x, 1760 + 420 * fall, 0.85, T, pose="cheer" if run > 0 else "reach", mood="wow",
                           talk=talk("RUSHER", T), walk=run * 3)
        c.restore()
        if fall == 0:
            c.drawCircle(hand[0], hand[1] - 60, 60, paint((220, 240, 255), 0.6))
            c.drawCircle(hand[0], hand[1] - 60, 60, paint(WHITE, 0.8, stroke=3))
    return st.arr


def s_chant4(T, t, d):
    def gag(c, T, t):                                                   # the trapdoor, with a little puff still coming out
        c.drawRect(skia.Rect.MakeLTRB(620, 1180, 900, 1220), paint(INK, 0.9))
        for i in range(4):
            c.drawCircle(760 + 30 * math.sin(t * 4 + i), 1150 - i * 40 - t * 20 % 40, 26 - i * 4, paint(WHITE, 0.4))
    return _chant(4, "w4", T, t, d, gag)

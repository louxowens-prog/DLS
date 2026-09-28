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
from sc1 import cam, chip, title_words, use_tag
from script import ROOMS
from timeline import TL

S, E, Wd = TL.s, TL.e, TL.word


def s_door(T, t, d):
    st = D.Stage()
    c = st.c
    D.backdrop(st, "hall", sets.hall)
    k = ease(ramp(T, C["door_open"], C["door_open"] + 3.0))
    push = ease(ramp(T, C["door_open"] + 1.0, C["door_open"] + 2.7))
    c.save()
    cam(c, 1.0 + 0.25 * k + 1.6 * push, 540, 1000)
    sets.door(c, 540, 1560, 1.0, k, T)
    c.restore()
    for who, x in (("copier", 170), ("believer", 360), ("you", 540), ("yesman", 720), ("rusher", 900)):
        cast.person(c, who, x, 2050, 0.62, T, pose="stand", mood="wow", alpha=0.95)     # backs to us, in silhouette
    c.drawRect(skia.Rect.MakeLTRB(0, 1500, W, H), paint(INK, 0.55 * (1 - push)))
    if push > 0:                                                        # through the doorway: the light floods in
        c.drawRect(skia.Rect.MakeWH(W, H), paint((255, 236, 200), 0.75 * push))
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
    """The big slow reveal: from a close-up of one candy flower, the camera pulls all the way back to the whole candy
    land - the far falls, the river winding toward us, the guests tiny on the striped bridge."""
    st = D.Stage()
    c = st.c
    u = ease(ramp(t, 0.0, max(0.5, d - 0.4)))
    z = 2.4 - 1.4 * u
    c.save()
    cam(c, z, 830 - 290 * u, 1560 - 600 * u)
    D.backdrop(st, "vista", sets.vista)
    sets.vista_flow(c, T)
    y, cx, w = sets._vk(0.55)
    for i, who in enumerate(("copier", "believer", "you", "yesman", "rusher")):
        x = cx - 150 + i * 75
        cast.person(c, who, x, y - 20 - 60 * (1 - abs(i - 2) / 2) * 0.5, 0.2, T, pose="arms_up" if who in ("copier", "rusher") else "stand",
                    mood="wow", shadow=False)
    c.restore()
    _sparkle(c, T, 40, 1, a=0.9)
    return st.arr


def s_wonder_river(T, t, d):
    """The chocolate river: the cake-cliff waterfall roaring, a pink swan boat drifting down the current."""
    st = D.Stage()
    c = st.c
    c.save()
    cam(c, 1.1 + 0.06 * ease(t / max(d, 0.1)), 420, 900)
    D.backdrop(st, "wonder", sets.wonder)
    sets.river(c, T, y0=860)
    c.restore()
    u = t / max(d, 0.1)
    c.save()
    c.translate(880 - 480 * u, 1180 + 10 * math.sin(T * 2))
    c.rotate(2 * math.sin(T * 1.5))
    c.scale(-1, 1)
    P.boat(c, 0, 0, 0.45, T)
    c.restore()
    _sparkle(c, T, 20, 3)
    return st.arr


def s_wonder_pan(T, t, d):
    """A tracking shot along the sugar lawn: giant candy slides past in the foreground; you and the host stroll."""
    st = D.Stage()
    u = t / max(d, 0.1)
    _wonder(st, T, 1.5, 330 + 420 * u, 1080)
    c = st.c
    for i, (x0, kind) in enumerate(((150, "cane"), (620, "gum"), (1050, "cane"), (1480, "gum"), (1900, "cane"))):
        x = x0 - 900 * u                                                # the foreground slides faster: parallax
        if kind == "cane":
            c.drawLine(x, 1920, x, 1080, paint(WHITE, stroke=90))
            for j in range(12):
                c.drawLine(x - 45, 1120 + j * 70, x + 45, 1080 + j * 70, paint(CHERRY, stroke=26))
            c.drawArc(skia.Rect.MakeLTRB(x, 900, x + 260, 1160), 180, 180, False, paint(WHITE, stroke=90))
            c.drawArc(skia.Rect.MakeLTRB(x, 900, x + 260, 1160), 200, 40, False, paint(CHERRY, stroke=90))
        else:
            D.shade(c, D.rrect(x - 160, 1500, x + 160, 1860, 150), [PINK, MINT, LEMON][i % 3], k=0.3)
            for j in range(18):
                a = j * 2.4
                c.drawCircle(x + 120 * math.cos(a) * (j % 3) / 2.5, 1640 + 100 * math.sin(a) * (j % 3) / 2.5, 7, paint(WHITE, 0.8))
    cast.person(c, "host", 610, 1500, 0.5, T, pose="cane", mood="smile", walk=t * 1.1, talk=talk("HOST", T))
    cast.person(c, "you", 430, 1520, 0.46, T, pose="stand", mood="wow", walk=t * 1.1, look=0.6)
    _sparkle(c, T, 24, 7)
    return st.arr


def s_wonder_guests(T, t, d):
    """The guests can't help themselves: the Copier licks a lollipop bigger than he is; the Believer sniffs a sugar rose."""
    st = D.Stage()
    _wonder(st, T, 1.45, 540, 1150, riv=False)
    c = st.c
    lx, ly = 250, 1000                                                  # the giant lollipop
    c.drawLine(lx, ly, lx, 1760, paint(WHITE, stroke=34))
    D.shade(c, D.circle(lx, ly, 200), (255, 80, 160), k=0.25)
    for k in range(5):
        r = 200 * (0.2 + k * 0.18)
        c.drawArc(skia.Rect.MakeLTRB(lx - r, ly - r, lx + r, ly + r), k * 70 + t * 40, 250, False, paint(WHITE, 0.75, stroke=16))
    lick = abs(math.sin(t * 3.2))
    cast.person(c, "copier", 470 - 14 * lick, 1560, 0.72, T, pose=(150, 30, 10, 0), mood="wow", tilt=-10 * lick, look=-1)
    c.drawOval(skia.Rect.MakeLTRB(420 - 14 * lick, 1182, 450 - 14 * lick, 1204 + 16 * lick), paint((240, 110, 130)))   # the tongue
    fx, fy = 850, 1000                                                  # the sugar rose, head-high
    c.drawLine(fx, fy, fx - 10, 1760, paint((70, 170, 90), stroke=24))
    D.shade(c, D.oval(fx - 150, 1300, fx - 10, 1360), (90, 190, 100), k=0.2)
    for j in range(8):
        a = j * math.pi / 4 + t * 0.4
        D.shade(c, D.circle(fx + 62 * math.cos(a), fy + 62 * math.sin(a), 60), (255, 150, 190), k=0.25, edge=0.2)
    D.shade(c, D.circle(fx, fy, 56), (250, 110, 160), k=0.3)
    sniff = ease(ramp(t, 0.3, 1.2))
    cast.person(c, "believer", 650 + 20 * sniff, 1640, 0.72, T, pose="clasp", mood="wow" if sniff > 0.8 else "smile",
                lean=10 * sniff, look=1)
    _sparkle(c, T, 20, 9)
    return st.arr


def s_wonder_host(T, t, d):
    st = D.Stage()
    _wonder(st, T, 1.4 + 0.12 * ease(t / max(d, 0.1)), 700, 900, riv=False)
    c = st.c
    sway = 6 * math.sin(T * 1.8)
    look = ramp(t, d * 0.6, d * 0.8)                                    # on the last line, he turns and looks at us
    cast.person(c, "host", 540, 1900, 1.02, T, pose="arms_out" if look < 0.5 else "clasp", mood="smile" if look < 0.5 else "sly",
                tilt=sway * (1 - look), talk=talk("HOST", T))
    _sparkle(c, T, 36, 5)
    return st.arr


def s_wonder_you(T, t, d):
    """Every expert you could never afford, patient at two in the morning: portraits circling you; a moon clock."""
    st = D.Stage()
    _wonder(st, T, 1.25, 540, 1000)
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((255, 220, 170), 0.12))
    experts = ["doctor", "x_engineer", "x_prof", "x_lawyer", "x_scientist", "x_teacher"]
    labels = ["DOCTOR", "ENGINEER", "PROFESSOR", "LAWYER", "SCIENTIST", "TEACHER"]
    for i, (who, lab) in enumerate(zip(experts, labels)):
        a = i / 6 * 2 * math.pi + t * 0.5
        x, y = 540 + 370 * math.cos(a), 790 + 285 * math.sin(a)
        D.shade(c, D.rrect(x - 85, y - 112, x + 85, y + 128, 12), GOLD, k=0.3)
        c.drawRect(skia.Rect.MakeLTRB(x - 70, y - 97, x + 70, y + 80), paint((250, 240, 220)))
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(x - 70, y - 97, x + 70, y + 80))
        s_ = 0.56
        h = cast.LOOKS[who]["h"]
        cast.person(c, who, x, y - 15 + 820 * s_ * h, s_, T, pose="stand", mood="smile", shadow=False,
                    talk=0.5 + 0.5 * math.sin(T * 9 + i) if i == int(t * 1.5) % 6 else 0.0)
        c.restore()
        D.text(c, lab, x, y + 113, 22, "fraunces-900", (80, 50, 10), tag="portrait")
    hand = cast.person(c, "you", 540, 1900, 0.78, T, pose="arms_out", mood="wow")
    k = ease(ramp(T, Wd("r0", "patient") - 0.2, Wd("r0", "patient") + 0.4))
    if k > 0:
        P.clock(c, 540, 290, 100 * k + 1, 2.0, T, face=(240, 236, 210))
        c.drawCircle(690, 260, 46 * k, paint((250, 246, 220)))
        c.drawCircle(712, 247, 40 * k, paint((255, 214, 150)))
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
    cast.person(c, "host", 790, 1560, 0.52, T, pose="present", mood="sly", talk=talk("HOST", T))
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
    P.taffy_puller(c, 420, 1180, 1.15, T, untangle=k)
    P.letter(c, 150 - 40 * k, 620, 0.3, T, plain=0.0, rot=-8)
    cast.person(c, "you", 790, 1560, 0.52, T, pose="clasp", mood="wow", look=-0.7)
    use_tag(c, T)
    return st.arr


def s_room1_letter(T, t, d):
    st = D.Stage()
    c = st.c
    _room(st, 1)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(INK, 0.3))
    P.letter(c, 540, 900, 1.3, T, plain=ease(ramp(t, 0.1, max(0.5, d - 0.4))), rot=-1)
    k = ramp(t, 1.2, 1.6)
    if k > 0:
        chip(c, "“explain it simpler”  ·  “and again”", 540, 1300, 30, a=k)
    use_tag(c, T)
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


def _li(sk, T):
    """Which lyric line of song sk is being sung (-1 before the first)."""
    ls_ = [TL.lines[l["key"]]["start"] for l in TL.songs[sk]["lines"]]
    return max([i for i, a in enumerate(ls_) if T >= a - 0.1], default=-1)


def _chant_zoom(sk, T, t, d):
    """A slow push, and a 70s snap zoom when the refrain starts."""
    r0 = TL.lines[TL.songs[sk]["lines"][2]["key"]]["start"]
    return (1 + 0.06 * t / max(d, 0.1)) * (1 + 0.16 * ease(ramp(T, r0 - 0.1, r0 + 0.06)))


def _workers(st, T, n, sk, form="line", cx=540, cy=1150):
    """The little workers, bobbing on the beat; the verse from the leader, the refrain from all. Each chant is staged
    differently: a chorus line, a low-angle close-up of three, a ring around the tiny guest, a conga line."""
    c = st.c
    S_ = TL.songs[sk]
    beat = S_["beat"]
    lines = [TL.lines[l["key"]] for l in S_["lines"]]
    li = _li(sk, T)
    resp = li in (1, 3)                                                 # call (one worker) and response (all of them)
    on_refrain = resp
    b = (T - S_["start"]) / beat
    even = int(b) % 2 == 0

    def pose_for(i, lead=False):
        if resp:
            return "cheer" if even else "fists"
        return "point" if lead else "stand"

    if form == "line":
        for i in range(5):
            ph = (b + i * 0.5) % 2
            hop = 22 * abs(math.sin(ph * math.pi))
            tk = talk("WORKERS", T) if (resp or i == 2) else 0.0
            cast.worker(c, 140 + i * 200, 1260 + (40 if i == 2 and not resp else 0), 0.82 * (1.12 if i == 2 and not resp else 1.0),
                        T, pose=pose_for(i, i == 2), bob=hop, talk=tk)
    elif form == "close":                                               # low angle: three big bulbs against the ceiling
        for i, x in enumerate((180, 520, 820)):
            hop = 30 * abs(math.sin((b + i * 0.66) * math.pi / 2))
            tk = talk("WORKERS", T) if (resp or i == 1) else 0.0
            c.save()
            c.translate(x, 1700)
            c.rotate((i - 1) * 6)
            cast.worker(c, 0, 0, 1.75 if i == 1 else 1.45, T, pose=pose_for(i + 1, i == 1), bob=hop, talk=tk)
            c.restore()
    elif form == "ring":                                                # a ring of wagging fingers around the middle
        _workers_subset(c, T, sk, range(8))
    else:                                                               # a conga line marching across
        for i in range(7):
            x = (i * 190 + (T - S_["start"]) * 260) % 1520 - 220
            hop = 20 * abs(math.sin((b + i * 0.5) * math.pi))
            kick = (40, -20, 70, 10) if int(b + i) % 2 else (10, 0, 90, 10)
            cast.worker(c, x, 1300, 0.7, T, pose=kick if not resp else pose_for(i), bob=hop,
                        talk=talk("WORKERS", T) if (resp or i == 3) else 0.0)


def _chant(n, sk, T, t, d, gag, form="line", after=None, z=1.0, cy=960):
    st = D.Stage()
    c = st.c
    c.save()
    cam(c, z, 540, cy)
    _room(st, n)
    c.restore()
    c.drawRect(skia.Rect.MakeWH(W, H), paint((255, 220, 160), 0.12))
    c.save()
    cam(c, _chant_zoom(sk, T, t, d), 540, 1150)
    gag(c, T, t)
    _workers(st, T, n, sk, form)
    if after:
        after(c, T, t)
    c.restore()
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
    cast.person(c, "you", 800, 1600, 0.5, T, pose="clasp", mood="wow", look=-0.7)
    use_tag(c, T)
    return st.arr


def s_room2_flag(T, t, d):
    st = D.Stage()
    c = st.c
    _room(st, 2)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(INK, 0.25))
    for i in range(6):                                                  # the six pages that matter, glowing
        x, y = 200 + (i % 3) * 340, 600 + (i // 3) * 370
        c.drawRect(skia.Rect.MakeLTRB(x - 120, y - 150, x + 120, y + 150), paint((255, 230, 150), 0.35, blur=20))
        D.shade(c, D.rrect(x - 110, y - 140, x + 110, y + 140, 6), CREAM, k=0.08)
        D.text(c, f"STUDY {[3, 12, 17, 24, 31, 44][i]}", x, y - 90, 30, "oldstandard-700", INK, tag="page")
        for j in range(4):
            c.drawLine(x - 80, y - 40 + j * 40, x + 80, y - 40 + j * 40, paint((150, 140, 120), stroke=5))
    k = ease(ramp(T, C["disagree"] - 0.3, C["disagree"] + 0.2))
    if k > 0:                                                           # the red flag where two disagree
        for x, y in ((540, 600), (540, 970)):
            c.drawCircle(x, y, 150, paint(CHERRY, k, stroke=10))
        c.drawLine(540, 750, 540, 820, paint(CHERRY, k, stroke=8))
        chip(c, "STUDY 12: “B12 loss on his pill is common”", 540, 1175, 30, fg=WHITE, bg=(160, 30, 40), a=k)
        chip(c, "STUDY 31: “it's rare”", 540, 1232, 30, fg=WHITE, bg=(160, 30, 40), a=k)
        chip(c, "(illustrative)", 540, 1284, 22, a=k)
    use_tag(c, T)
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
    chip(c, "SOUNDS-SURE SYRUP", 380, 560, 30, fg=(80, 40, 10), bg=GOLD2)
    c.drawLine(560, 548, 640, 640, paint(GOLD2, stroke=6))
    c.drawPath(path([(640, 640), (610, 628), (630, 606)]), paint(GOLD2))
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
    return _chant(2, "w2", T, t, d, gag, form="close", z=1.3, cy=700)


def s_room3(T, t, d):
    st = D.Stage()
    c = st.c
    _room(st, 3)
    P.mirror(c, 300, 1250, 0.95, T, mood="sly", talk=0.0)
    P.scales(c, 690, 1240, 0.66, T, tip=math.sin(t * 1.2))
    k = ease(ramp(T, C["hole"] - 0.3, C["hole"] + 0.3))
    if k > 0:                                                           # the hole in your own reasoning, ringed in red
        D.shade(c, D.rrect(540, 470, 1000, 830, 10), CREAM, k=0.08, a=k)
        D.text(c, "MY THINKING", 770, 540, 40, "fraunces-900", INK, tag="plan", a=k)
        for j, ln in enumerate(["blame the diabetes,", "so nothing to do:", "just live with it"]):
            D.text(c, ln, 770, 610 + j * 62, 34, "oldstandard-700", INK, tag="plan", a=k)
        c.drawOval(skia.Rect.MakeLTRB(575, 562, 965, 630), paint(CHERRY, k, stroke=8))
        chip(c, "ASSUMPTION!", 770, 800, 28, fg=WHITE, bg=CHERRY, a=k)
    use_tag(c, T)
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
    """The tiny yes-man, pacing in a spotlight, ringed by wagging fingers."""
    def tiny(c, T, t):
        cast.person(c, "yesman", 540 + 30 * math.sin(t * 2.5), 1150, 0.17, T, pose="shrug", mood="worry", walk=t * 1.5)
    return _ring3(T, t, d, tiny)


def _ring3(T, t, d, tiny):
    st = D.Stage()
    c = st.c
    _room(st, 3)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((255, 220, 160), 0.1))
    c.save()
    cam(c, _chant_zoom("w3", T, t, d), 540, 1150)
    c.drawCircle(540, 1150, 330, paint((255, 240, 200), 0.18, blur=40))    # a spotlight on him
    S_ = TL.songs["w3"]
    b = (T - S_["start"]) / S_["beat"]
    back = []
    front = []
    for i in range(8):                                                  # split the ring: those behind him, those in front
        a = i / 8 * 2 * math.pi + b * 0.12
        (back if math.sin(a) < 0 else front).append(i)
    _workers_subset(c, T, "w3", back)
    tiny(c, T, t)
    _workers_subset(c, T, "w3", front)
    c.restore()
    return st.arr


def _workers_subset(c, T, sk, which):
    S_ = TL.songs[sk]
    beat = S_["beat"]
    b = (T - S_["start"]) / beat
    on_refrain = _li(sk, T) in (1, 3)
    even = int(b) % 2 == 0
    pts = []
    for i in which:
        a = i / 8 * 2 * math.pi + b * 0.12
        pts.append((math.sin(a), 540 + 400 * math.cos(a), 1150 + 150 * math.sin(a), i))
    for sa, x, y, i in sorted(pts):
        hop = 16 * abs(math.sin((b + i * 0.5) * math.pi / 2))
        pose = ("cheer" if even else "fists") if on_refrain else ("point" if even else (150, 20, 115, 0))
        cast.worker(c, x, y, 0.5 + 0.2 * (sa + 1) / 2, T, pose=pose, bob=hop,
                    talk=talk("WORKERS", T) if (on_refrain or i == 0) else 0.0)


HYP = ["his diabetes|pill?", "an old|injury?", "his shoes?", "his back?", "genetics?", "something|else?"]


def s_room4_fizz(T, t, d):
    st = D.Stage()
    c = st.c
    _room(st, 4)
    P.kettle(c, 640, 1320, 0.85, T)
    popped = (1, 2, 3, 4, 5) if T >= C["pop"] else ()
    P.bubbles(c, T, HYP, 640, 1060, 380, t0=T - t + 0.2, gold=0 if T >= C["pop"] else None, popped=popped, dy=200)
    k = ease(ramp(T, C["wait"] - 0.4, C["wait"] + 0.1)) * (1 - ramp(T, C["pop"] - 0.3, C["pop"]))
    if k > 0:                                                           # what if you wait? a chalk fork in the road
        D.shade(c, D.rrect(30, 1110, 430, 1300, 12), (50, 60, 56), k=0.1, a=k)
        D.text(c, "IF YOU WAIT:", 230, 1165, 32, "special-elite-400", WHITE, tag="chalk", a=k)
        D.text(c, "nerve damage can", 230, 1215, 30, "special-elite-400", WHITE, tag="chalk", a=k)
        D.text(c, "become permanent", 230, 1260, 30, "special-elite-400", WHITE, tag="chalk", a=k)
    use_tag(c, T)
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
        P.plan_card(c, 540, 820, 0.95, T, k)
    use_tag(c, T)
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
    return _chant(4, "w4", T, t, d, gag, form="conga")

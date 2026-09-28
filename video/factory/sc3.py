"""Scenes 3: the tunnel (the horror peak), the lesson, the appointment, the host's rage and the warm reveal, the true
story (told as an illustration), the end."""
import math

import numpy as np
import skia

import cast
import draw as D
import props as P
import sets
from cues import C, talk
from draw import (CHERRY, CREAM, GOLD, GOLD2, GOLD3, H, INK, LEMON, LILAC, MINT, PINK, W, WHITE, ease, mix, paint, path,
                  ramp)
from sc1 import cam, chip, title_words
from timeline import TL

S, E, Wd = TL.s, TL.e, TL.word


def s_tunnel_in(T, t, d):
    st = D.Stage((20, 14, 20))
    c = st.c
    D.backdrop(st, "wonder", sets.wonder)
    sets.river(c, T)
    c.drawOval(skia.Rect.MakeLTRB(240, 700, 840, 1400), paint((10, 6, 10)))                            # the tunnel mouth
    c.drawOval(skia.Rect.MakeLTRB(240, 700, 840, 1400), paint((120, 60, 100), stroke=30))
    k = ease(ramp(t, 0, d))
    c.save()
    cam(c, 1.0 - 0.5 * k, 540, 1150)
    P.boat(c, 540, 1500 - 300 * k, 0.9, T)
    cast.person(c, "you", 420, 1430 - 300 * k, 0.4, T, pose="stand", mood="worry", shadow=False)
    cast.person(c, "host", 640, 1430 - 300 * k, 0.4, T, pose="cane", mood="sly", shadow=False)
    c.restore()
    return st.arr


IMAGES = ["eye", "cite", "quote", "number", "clock", "faces", "eye", "cite"]


def _projection(c, kind, T, a):
    """Unsettling things projected on the tunnel walls."""
    if kind == "eye":
        c.drawOval(skia.Rect.MakeLTRB(-260, -130, 260, 130), paint(WHITE, a))
        c.drawCircle(40 * math.sin(T * 5), 0, 90, paint((90, 160, 90), a))
        c.drawCircle(40 * math.sin(T * 5), 0, 45, paint(INK, a))
    elif kind == "cite":
        D.shade(c, D.rrect(-300, -180, 300, 180, 6), CREAM, k=0.1, a=a)
        D.text(c, "Smith et al., 2019", 0, -95, 46, "oldstandard-700", INK, tag="proj", a=a)
        D.text(c, "Journal of Things", 0, -20, 36, "oldstandard-700", INK, tag="proj", a=a)
        D.text(c, "DOES NOT EXIST", 0, 100, 56, "fraunces-900", CHERRY, tag="proj", a=a)
    elif kind == "quote":
        D.text(c, "“I never said that.”", 0, 0, 70, "fraunces-900", WHITE, tag="proj", a=a, outline=INK, ow=10)
    elif kind == "number":
        D.text(c, "73.6%?", 0, 30, 170, "fraunces-900", LEMON, tag="proj", a=a, outline=INK, ow=14)
    elif kind == "clock":
        P.clock(c, 0, 0, 180, T * 8, T, face=(230, 220, 200))
    elif kind == "faces":
        for i in range(5):
            c.save()
            c.translate(-240 + i * 120, 40 * math.sin(T * 3 + i))
            cast.face(c, {"hair_c": (40, 40, 40)}, "wow", 0, False, 0.8, 50)
            c.restore()


def s_tunnel(T, t, d):
    st = D.Stage((10, 6, 12))
    c = st.c
    speed = 1 + 3.5 * ease(t / max(d, 0.1))
    cols = [(200, 30, 60), (40, 200, 90), (220, 40, 200), (250, 200, 40), (40, 90, 230)]
    ph = T * 6 * speed
    for i in range(14):                                                 # strobing rings rushing at us
        r = ((i / 14 + ph * 0.05) % 1.0) ** 2 * 1500
        col = cols[(i + int(ph)) % len(cols)]
        c.drawCircle(540, 900, r, paint(col, 0.55, stroke=40 + r * 0.06))
    flash = int(T * 4 * speed) % 2
    c.drawRect(skia.Rect.MakeWH(W, H), paint(cols[int(T * 3 * speed) % 5], 0.14 + 0.1 * flash))
    k = int(t * 1.4 * speed) % len(IMAGES)                              # a new horror every beat, faster and faster
    c.save()
    c.translate(540 + 90 * math.sin(T * 1.7), 640 + 50 * math.cos(T * 2.3))
    c.rotate(8 * math.sin(T * 2))
    z = 0.8 + 0.4 * ((t * 1.4 * speed) % 1.0)
    c.scale(z, z)
    _projection(c, IMAGES[k], T, 0.95)
    c.restore()
    P.boat(c, 540, 1560, 1.0, T)
    cast.person(c, "you", 400, 1480, 0.52, T, pose="clasp", mood="worry", shadow=False)
    cast.person(c, "host", 690, 1480, 0.52, T, pose="arms_out", mood="shout" if t > d * 0.6 else "sly",
                talk=talk("HOST", T), shadow=False)
    return st.arr


def s_tunnel_black(T, t, d):
    st = D.Stage((6, 4, 6))
    c = st.c
    c.drawCircle(540, 900, 30, paint((255, 240, 200), 0.05))
    return st.arr


def s_tunnel_calm(T, t, d):
    st = D.Stage((40, 30, 50))
    c = st.c
    k = ease(ramp(t, 0, 1.2))
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.rad((540, 700), 1200, [mix((40, 30, 50), (255, 220, 190), k * 0.8), (30, 20, 40)])))
    cast.person(c, "host", 540, 2600, 1.85, T, pose="clasp", mood="sly", talk=talk("HOST", T))
    return st.arr


def s_lesson(T, t, d):
    """A 1971 classroom card, held up by the workers: trust it blindly -> check less; used well -> think more."""
    st = D.Stage()
    c = st.c
    D.backdrop(st, "room4", lambda cc: sets.room(cc, 4))
    c.drawRect(skia.Rect.MakeWH(W, H), paint(INK, 0.35))
    cards = [(S("e1"), "TRUST IT BLINDLY", ["→ you check less", "Microsoft & Carnegie Mellon survey, 2025"], (160, 40, 50)),
             (Wd("e1", "nineteen") - 0.2, "19 POINTS", ["less likely to be right, on a task AI was bad at",
                                                      "Harvard Business School & BCG study, 2023"], (120, 60, 30)),
             (Wd("e1", "Used"), "USE IT WELL", ["→ you think more"], (30, 110, 70))]
    for j, (t0, big, small, col) in enumerate(cards):
        k = ease(ramp(T, t0 - 0.2, t0 + 0.3))
        if k <= 0:
            continue
        y = 360 + j * 290
        c.save()
        c.translate(540, y)
        c.scale(0.8 + 0.2 * k, 0.8 + 0.2 * k)
        D.shade(c, D.rrect(-440, -125, 440, 125, 16), CREAM, k=0.08, a=k)
        D.text(c, big, 0, -30, 76, "fraunces-900", col, tag="card", a=k)
        for q, ln in enumerate(small):
            f = D.font("oldstandard-700", 34)
            sz = min(34 if q == 0 else 28, (34 if q == 0 else 28) * 800 / max(1, f.measureText(ln) * (1 if q == 0 else 28 / 34)))
            D.text(c, ln, 0, 34 + q * 44 + (12 if len(small) == 1 else 0), sz, "oldstandard-700", INK if q == 0 else (90, 70, 50),
                   tag="card", a=k)
        c.restore()
    for i in range(4):
        cast.worker(c, 170 + i * 240, 1330, 0.42, T, pose="cheer" if i % 2 else "stand", bob=8 * abs(math.sin(T * 3 + i)))
    return st.arr


def s_clinic(T, t, d):
    st = D.Stage()
    c = st.c
    D.backdrop(st, "clinic", sets.clinic)
    cast.person(c, "dad", 190, 1290, 0.6, T, pose="stand", mood="worry", look=0.6)
    hand = cast.person(c, "you", 300 + 110 * ease(ramp(t, 0, 1.5)), 1290, 0.64, T, pose="hold", mood="smile",
                       walk=t * 1.5 if t < 1.5 else 0)
    D.shade(c, D.rrect(hand[0] - 70, hand[1] - 100, hand[0] + 70, hand[1] + 90, 4), (40, 90, 160), k=0.1)   # one page
    D.text(c, "PLAN", hand[0], hand[1] - 40, 30, "fraunces-900", WHITE, tag="page")
    cast.person(c, "doctor", 780, 1290, 0.62, T, pose="clasp", mood="flat", look=-0.6)
    k = ease(ramp(T, Wd("p1", "Could") - 0.1, Wd("p1", "Could") + 0.3))
    if k > 0:                                                           # the question, on the page in her hand
        c.save()
        c.translate(540, 470)
        c.scale(0.85 + 0.15 * k, 0.85 + 0.15 * k)
        D.shade(c, D.rrect(-420, -120, 420, 120, 14), (40, 90, 160), k=0.1, a=k)
        D.text(c, "Could his diabetes pill", 0, -22, 50, "fraunces-900", WHITE, tag="q", a=k)
        D.text(c, "be lowering his B12?", 0, 46, 50, "fraunces-900", LEMON, tag="q", a=k)
        c.restore()
    return st.arr


def s_doctor(T, t, d):
    st = D.Stage()
    c = st.c
    c.save()
    cam(c, 1.8, 760, 700)
    D.backdrop(st, "clinic", sets.clinic)
    c.restore()
    k = ramp(T, C["right_q"] - 0.2, C["right_q"] + 0.3)
    cast.person(c, "doctor", 540, 2500, 1.7, T, pose="clasp", mood="wow" if k < 1 else "smile", talk=talk("DOCTOR", T))
    return st.arr


def s_dad_home(T, t, d):
    """By spring: your dad, walking easy on the grass beside you. The lab slip first: B12 low."""
    st = D.Stage()
    c = st.c
    u = t / max(d, 0.1)
    c.save()
    cam(c, 1.08 - 0.08 * u, 540, 1100)
    D.backdrop(st, "spring", sets.spring)
    c.restore()
    x = 420 + 90 * u
    cast.person(c, "dad", x, 1520, 0.6, T, pose="stand", mood="smile", walk=t * 1.1, look=0.5)
    cast.person(c, "you", x + 190, 1540, 0.58, T, pose="stand", mood="smile", walk=t * 1.1, look=-0.5)
    rng = np.random.default_rng(3)
    for i in range(24):                                                 # blossom drifting
        px = (rng.uniform(0, W) + t * 40 * rng.uniform(0.5, 1.5)) % W
        py = (rng.uniform(0, 1400) + t * 90 * rng.uniform(0.6, 1.4)) % 1300 + 250
        c.drawCircle(px, py, rng.uniform(6, 11), paint((255, 206, 226), 0.9))
    k = ease(ramp(T, S("p3") + 0.1, S("p3") + 0.5)) * (1 - ease(ramp(T, C["spring"] + 0.3, C["spring"] + 0.8)))
    if k > 0:                                                           # the lab slip
        c.save()
        c.translate(540, 560)
        c.rotate(-3)
        D.shade(c, D.rrect(-340, -160, 340, 160, 8), (250, 246, 236), k=0.05, a=k)
        D.text(c, "BLOOD TEST", 0, -95, 40, "oldstandard-700", INK, tag="slip", a=k)
        D.text(c, "VITAMIN B12", 0, -15, 58, "fraunces-900", INK, tag="slip", a=k)
        stamp = ease(ramp(T, C["b12_low"] - 0.1, C["b12_low"] + 0.1)) * k
        if stamp > 0:
            c.drawPath(D.rrect(-250, 35, -50, 125, 8), paint(CHERRY, stamp, stroke=6))
            D.text(c, "LOW", -150, 108, 70, "fraunces-900", CHERRY, tag="slip", a=stamp)
        tr = ease(ramp(T, Wd("p3", "supplement") - 0.1, Wd("p3", "supplement") + 0.2)) * k
        if tr > 0:
            D.text(c, "→ supplement", 150, 100, 42, "oldstandard-700", (30, 110, 70), tag="slip", a=tr)
        c.restore()
    chip(c, "DRAMATIZATION", 540, 300, 26)
    return st.arr


def s_anger(T, t, d):
    """The host explodes: red light, the frame shakes, a crash zoom - then, in the silence, everything freezes."""
    st = D.Stage((60, 10, 10))
    c = st.c
    frozen = T >= E("x1") + 0.05
    tt = min(T, E("x1") + 0.05)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.rad((540, 800), 1200, [(200, 40, 30), (40, 0, 0)])))
    sh = 0 if frozen else 18
    rng = np.random.default_rng(int(tt * 24))
    c.save()
    c.translate(rng.uniform(-sh, sh), rng.uniform(-sh, sh))
    cam(c, 1.0 + 0.35 * ease(ramp(tt, S("x1"), E("x1"))), 540, 700)
    cast.person(c, "host", 540, 2500, 1.7, tt, pose="fists", mood="shout" if not frozen else "angry", talk=talk("HOST", tt) if not frozen else 0.9)
    c.restore()
    return st.arr


def s_warm(T, t, d):
    st = D.Stage()
    c = st.c
    k = ease(ramp(t, 0, 1.5))
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.rad((540, 700), 1300, [mix((200, 40, 30), (255, 214, 140), k), mix((40, 0, 0), (150, 80, 40), k)])))
    cast.person(c, "host", 540, 2500, 1.7, T, pose="clasp", mood="smile", talk=talk("HOST", T))
    return st.arr


def s_ticket_flip(T, t, d):
    st = D.Stage()
    c = st.c
    D.backdrop(st, "balcony", sets.balcony)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((120, 60, 20), 0.35))
    f = ease(ramp(t, 0.2, 1.0))
    lines = ("ADMIT ONE MIND", "BRING A QUESTION") if f < 0.5 else ("ADMIT ONE MIND", "NO LIMIT")
    P.ticket(c, 540, 760, 860, rot=-3 + 3 * f, lines=lines, T=T, glow=1.0, flip=f)
    title_words(c, "THE FACTORY IS YOURS", 540, 1150, 62, S("x3") + 0.2, T)
    return st.arr


def s_balcony(T, t, d):
    """The benefit isn't speed. It's reach: the whole place below you."""
    st = D.Stage()
    c = st.c
    z = 1.15 - 0.15 * ease(t / max(d, 0.1))
    c.save()
    cam(c, z, 540, 1000)
    D.backdrop(st, "balcony", sets.balcony)
    sets.river(c, T)
    c.restore()
    hand = cast.person(c, "you", 540, 1290, 0.55, T, pose="arms_out", mood="smile")
    title_words(c, "NOT SPEED.", 540, 420, 96, Wd("z1", "speed.") - 0.1, T, color=(240, 230, 210))
    title_words(c, "REACH.", 540, 620, 190, Wd("z1", "reach.") - 0.1, T, color=GOLD2)
    return st.arr


# ------------------------------------------------------------------ the true story, as an illustration

def _story(st, T, tone=(250, 238, 212)):
    D.backdrop(st, f"story{tone}", lambda cc: sets.storybook(cc, tone))


def s_story1(T, t, d):
    st = D.Stage()
    c = st.c
    _story(st, T, (200, 190, 210))
    c.drawRect(skia.Rect.MakeLTRB(120, 300, 960, 1250), paint((40, 36, 60)))                            # a night window frame
    c.drawCircle(760, 480, 70, paint((250, 246, 220)))
    cast.silhouette(c, "mother_seated", 330, 1250, 1.0, color=(30, 24, 40))
    c.drawRect(skia.Rect.MakeLTRB(120, 1250, 960, 1270), paint((60, 50, 60)))                           # the table
    c.drawRect(skia.Rect.MakeLTRB(560, 1010, 900, 1200), paint((30, 30, 40)))
    c.drawRect(skia.Rect.MakeLTRB(575, 1025, 885, 1185), paint((230, 240, 255)))
    k = ease(ramp(T, C["suggested"] - 0.2, C["suggested"] + 0.5))
    D.text(c, "symptoms · scan notes", 730, 1080, 24, "special-elite-400", INK, tag="screen")
    if k > 0:
        D.text(c, "tethered cord", 730, 1130, 34, "fraunces-900", (30, 110, 60), tag="screen", a=k)
        D.text(c, "syndrome?", 730, 1170, 34, "fraunces-900", (30, 110, 60), tag="screen", a=k)
    chip(c, "TRUE STORY · reported by TODAY, Sept 2023", 540, 300, 26)
    return st.arr


def s_story2(T, t, d):
    st = D.Stage()
    c = st.c
    _story(st, T)
    D.shade(c, D.rrect(520, 360, 960, 980, 12), (230, 236, 244), k=0.05)                                # the lightbox
    for j in range(9):                                                 # a spine on the scan
        c.drawOval(skia.Rect.MakeLTRB(700, 420 + j * 60, 790, 470 + j * 60), paint((120, 130, 150)))
    c.drawLine(745, 900, 745, 960, paint((200, 60, 60), stroke=8))
    cast.silhouette(c, "surgeon", 300, 1290, 1.05, color=(40, 50, 60))
    k = ease(ramp(T, C["agreed"] - 0.2, C["agreed"] + 0.3))
    if k > 0:
        c.drawCircle(745, 920, 70, paint(CHERRY, k, stroke=8))
        chip(c, "A NEUROSURGEON AGREED", 540, 1150, 34, a=k)
    return st.arr


def s_story3(T, t, d):
    st = D.Stage()
    c = st.c
    _story(st, T, (226, 200, 160))
    c.drawCircle(540, 820, 360, paint((255, 190, 110), 0.8))                                            # a morning sun
    cast.silhouette(c, "mother", 420, 1290, 0.95, color=(60, 40, 40))
    cast.silhouette(c, "boy", 600, 1290, 0.95, color=(60, 40, 40))
    c.drawLine(470, 900, 575, 1010, paint((60, 40, 40), stroke=26))                                   # holding hands
    return st.arr


def s_end(T, t, d):
    st = D.Stage()
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.rad((540, 700), 1300, [(255, 214, 140), (120, 60, 30)])))
    P.ticket(c, 540, 560, 820, rot=-3, lines=("ADMIT ONE MIND", "BRING A QUESTION"), T=T, glow=1.0)
    srcs = ["True story: TODAY, Sept 2023 · NEJM AI Grand Rounds",
            "Dell'Acqua et al. (Harvard & BCG), 2023",
            "Noy & Zhang, Science, 2023",
            "Brynjolfsson, Li & Raymond, QJE, 2025",
            "McKinsey Global Institute, 2012",
            "Lee et al. (Microsoft & CMU), CHI 2025",
            "Metformin & B12: ADA Standards of Care, 2025"]
    D.text(c, "SOURCES", 540, 920, 36, "rye-400", (80, 40, 10), tag="src")
    for i, s in enumerate(srcs):
        D.text(c, s, 540, 980 + i * 50, 30, "oldstandard-700", (60, 30, 10), tag="src")
    return st.arr

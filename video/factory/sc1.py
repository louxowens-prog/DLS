"""Scenes 1: the cold open (a true story), the grey town, the letter, the golden ticket, the newsreel, the gates."""
import math

import numpy as np
import skia

import cast
import draw as D
import props as P
import sets
from cues import C, Wx, talk
from draw import (CHERRY, CREAM, GOLD, GOLD2, GOLD3, H, INK, LEMON, MINT, PINK, W, WHITE, ease, mix, paint, path, ramp)
from timeline import TL

S, E, Wd = TL.s, TL.e, TL.word


def cam(c, z, cx=540, cy=960):
    c.translate(cx, cy)
    c.scale(z, z)
    c.translate(-cx, -cy)


def chip(c, s, x, y, size=30, fg=INK, bg=(236, 226, 200), a=1.0, tag="chip"):
    """A typed label on a strip of paper tape (TRUE STORY, RE-ENACTMENT, sources)."""
    f = D.font("special-elite-400", size)
    w = f.measureText(s)
    c.drawRect(skia.Rect.MakeLTRB(x - w / 2 - 18, y - size * 1.05, x + w / 2 + 18, y + size * 0.45), paint(bg, 0.92 * a))
    D.text(c, s, x, y, size, "special-elite-400", fg, tag=tag, a=a)


def use_tag(c, T):
    """The running count of the thirteen uses: a stamped label slams in as each one is shown, with 13 dots filling."""
    cur = [u for u in USES() if u[0] - 0.05 <= T < u[1]]
    if not cur:
        return
    t0, t1, n, lab = cur[-1]
    k = ease(ramp(T, t0 - 0.05, t0 + 0.12))
    fade = 1 - ramp(T, t1 - 0.15, t1)
    a = k * fade
    if a <= 0.01:
        return
    size = 50
    f = D.font("fraunces-900", size)
    if f.measureText(lab) > 800:
        size = 50 * 800 / f.measureText(lab)
    w = max(560, D.font("fraunces-900", size).measureText(lab) + 90)
    c.save()
    c.translate(540, 335)
    c.rotate(-2)
    z = 1.35 - 0.35 * k
    c.scale(z, z)
    D.shade(c, D.rrect(-w / 2, -82, w / 2, 82, 14), (246, 236, 212), k=0.06, a=a)
    c.drawPath(D.rrect(-w / 2 + 10, -72, w / 2 - 10, 72, 10), paint(CHERRY, a, stroke=5))
    c.drawPath(D.rrect(-w / 2 + 18, -64, w / 2 - 18, 64, 8), paint(CHERRY, a * 0.6, stroke=2))
    D.text(c, f"USE {n} OF 13", 0, -32, 30, "special-elite-400", (120, 30, 40), tag="usetag", a=a)
    D.text(c, lab, 0, 26, size, "fraunces-900", CHERRY, tag="usetag", a=a)
    for j in range(13):                                                 # the tally: thirteen dots, filling
        x = (j - 6) * 30
        c.drawCircle(x, 52, 9, paint(CHERRY if j < n else (220, 200, 180), a))
    c.restore()


def USES():
    """(from, to, number, use) - when each of the thirteen uses is being shown in the rooms."""
    return [
        (S("r1") - 0.1, Wd("r1", "It") - 0.1, 1, "EXPLAIN UNFAMILIAR SUBJECTS"),
        (Wd("r1", "It") - 0.1, E("r1") + 0.15, 2, "TRANSLATE JARGON"),
        (S("r2") - 0.1, Wd("r2", "with") - 0.1, 3, "SUMMARIZE DOCUMENTS"),
        (Wd("r2", "with") - 0.1, S("r2b") - 0.1, 4, "FIND INCONSISTENCIES"),
        (S("r3") - 0.1, Wd("r3", "each") + 0.1, 5, "SIMULATE OPPOSING VIEWS"),
        (Wd("r3", "each") + 0.1, Wd("r3", "hole") - 0.25, 6, "COMPARE COMPETING IDEAS"),
        (Wd("r3", "hole") - 0.25, E("r3") + 0.15, 7, "CRITIQUE AN ARGUMENT"),
        (S("r4") - 0.1, Wd("r4", "happens") - 0.25, 8, "GENERATE HYPOTHESES"),
        (Wd("r4", "happens") - 0.25, Wd("r4", "Ideas") - 0.1, 9, "EXPLORE CONSEQUENCES"),
        (Wd("r4", "Ideas") - 0.1, Wd("r4", "worry") - 0.15, 10, "BRAINSTORM"),
        (Wd("r4", "worry") - 0.15, C["plan"] - 0.1, 11, "ORGANIZE THOUGHTS"),
        (C["plan"] - 0.1, C["three_q"] - 0.15, 12, "TURN A VAGUE IDEA INTO A PLAN"),
        (C["three_q"] - 0.15, E("r4") + 0.25, 13, "IDENTIFY MISSING QUESTIONS"),
    ]


def title_words(c, s, x, y, size, t0, T, color=CREAM, edge=(110, 40, 20), tag="title", fname="fraunces-900"):
    """Big 1971 main-title lettering with a soft drop shadow; it settles in with a small push."""
    k = ease(ramp(T, t0, t0 + 0.35))
    if k <= 0:
        return
    c.save()
    c.translate(x, y)
    z = 1.12 - 0.12 * k
    c.scale(z, z)
    D.text(c, s, 0, 0, size, fname, color, tag=tag, a=k, outline=edge, ow=size * 0.14, shadow=(20, 10, 6))
    c.restore()


def _night_kitchen(st, T, glow=0.0):
    c = st.c
    D.backdrop(st, "kitchen", sets.kitchen)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((10, 14, 30), 0.45))
    P.rain(c, T, 0.35, 60, 110, 450, 280, 740)
    cast.silhouette(c, "mother_seated", 470, 1300, 0.95, color=(24, 20, 30))
    c.drawPath(path([(40, 1220), (1040, 1220), (1080, 1340), (0, 1340)]), paint((70, 52, 40)))            # the table, over her
    c.drawRect(skia.Rect.MakeLTRB(620, 1110, 860, 1240), paint((30, 30, 40)))                            # the laptop
    scr = mix((150, 190, 255), (255, 210, 110), glow)
    c.drawRect(skia.Rect.MakeLTRB(632, 1122, 848, 1228), paint(scr, 0.95))
    c.drawCircle(740, 1170, 260 + 700 * glow, paint(scr, 0.22 + 0.25 * glow, blur=90))


def s_cold_kitchen(T, t, d):
    st = D.Stage()
    c = st.c
    c.save()
    cam(c, 1.0 + 0.04 * t, 700, 1100)
    _night_kitchen(st, T)
    c.restore()
    chip(c, "A TRUE STORY", 540, 330, 34)
    title_words(c, "17 DOCTORS", 540, 620, 150, S("c0") + 0.1, T)
    return st.arr


def s_cold_doors(T, t, d):
    """Seventeen doors down a long hospital corridor, each one closing."""
    st = D.Stage((40, 44, 50))
    c = st.c
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(shader=D.lin((0, 0), (0, H), [(70, 76, 80), (40, 44, 50)])))
    vx, vy = 540, 820
    c.drawPath(path([(0, 1700), (W, 1700), (vx + 60, vy + 60), (vx - 60, vy + 60)]), paint((90, 92, 88)))
    for i in range(17):                                                 # doors on alternating sides, receding
        k = 1 - i / 17
        z = 0.12 + 0.88 * k ** 1.6
        side = -1 if i % 2 == 0 else 1
        x = vx + side * (70 + 470 * z)
        y1, hgt, w = vy + 60 + 880 * z, 620 * z, 170 * z
        shut = ramp(T, C["doors"] - 0.3 + (16 - i) * 0.1, C["doors"] - 0.1 + (16 - i) * 0.1)
        col = mix((170, 176, 170), (120, 60, 60), shut)
        c.drawRect(skia.Rect.MakeLTRB(x - w / 2, y1 - hgt, x + w / 2, y1), paint(col))
        c.drawRect(skia.Rect.MakeLTRB(x - w / 2, y1 - hgt, x + w / 2, y1), paint((60, 60, 60), stroke=max(1, 5 * z)))
    cast.silhouette(c, "mother", 460, 1720, 0.55, color=(26, 22, 28))
    cast.silhouette(c, "boy", 580, 1720, 0.55, color=(26, 22, 28))
    title_words(c, "3 YEARS", 540, 520, 150, C["doors"] + 0.1, T)
    title_words(c, "NO ANSWER", 540, 680, 90, Wd("c0", "no") - 0.05, T, color=(240, 200, 190), edge=(120, 20, 30))
    return st.arr


def s_cold_glow(T, t, d):
    st = D.Stage()
    c = st.c
    g = ease(ramp(T, C["glow"], C["glow"] + 1.6))
    c.save()
    cam(c, 1.06 + 0.1 * t, 740, 1170)
    _night_kitchen(st, T, glow=g)
    c.restore()
    rng = np.random.default_rng(4)
    for i in range(40):                                                 # golden dust in the air
        x, y = rng.uniform(0, W), (rng.uniform(300, 1700) - t * 60 * rng.uniform(0.5, 1.5)) % 1500 + 250
        c.drawCircle(x, y, rng.uniform(2, 6), paint(GOLD2, 0.6 * g))
    return st.arr


def s_title(T, t, d):
    """The main title, as a 1971 musical would have it: the name on a gold ticket over candy stripes."""
    st = D.Stage()
    c = st.c
    for j in range(14):
        a0 = j * 360 / 14 + t * 20
        p = skia.Path()
        p.moveTo(540, 960)
        for q in (0, 1):
            a = math.radians(a0 + q * 360 / 28)
            p.lineTo(540 + 1600 * math.cos(a), 960 + 1600 * math.sin(a))
        p.close()
        c.drawPath(p, paint([PINK, CREAM][j % 2]))
    P.ticket(c, 540, 960, 900 * (0.92 + 0.06 * t), rot=-4, lines=("", ""), glow=0.6, T=T, head="")
    D.text(c, "THE", 540, 830, 70, "rye-400", (110, 60, 10), tag="title")
    D.text(c, "THINKING", 540, 945, 136, "shrikhand-400", (140, 30, 40), tag="title", outline=GOLD2, ow=10)
    D.text(c, "FACTORY", 540, 1095, 136, "shrikhand-400", (140, 30, 40), tag="title", outline=GOLD2, ow=10)
    return st.arr


def s_town(T, t, d):
    st = D.Stage()
    c = st.c
    c.save()
    cam(c, 1.0 + 0.03 * t)
    D.backdrop(st, "town", sets.town)
    for i, (x0, sp, s) in enumerate(((-100, 90, 0.8), (1200, -70, 0.9), (300, 40, 0.7), (900, -50, 0.75))):
        P.umbrella_man(c, x0 + sp * t, 1500 + i * 60, s, T)
    cast.person(c, "you", 540, 1660 - 0 * t, 0.62 + 0.03 * t, T, pose="stand", mood="flat", walk=t * 1.2)
    c.restore()
    P.rain(c, T, 0.45, 180)
    return st.arr


def s_office(T, t, d):
    st = D.Stage()
    c = st.c
    D.backdrop(st, "office", sets.office)
    P.rain(c, T, 0.3, 40, 640, 980, 240, 680)
    n = min(50, int(8 + t * 14))
    cast.person(c, "student", 540, 1640, 0.82, T, pose="clasp", mood="worry")
    c.drawRect(skia.Rect.MakeLTRB(40, 1180, 1040, 1240), paint((110, 86, 64)))                        # the desk, over him
    c.drawRect(skia.Rect.MakeLTRB(60, 1240, 1020, 1760), paint((96, 74, 56)))
    P.reports(c, 540, 1180, n, 1.0, seed=2)
    rng = np.random.default_rng(int(t * 6))
    for i in range(3):                                                  # more reports keep landing
        y = (t * 900 + i * 300) % 900 + 250
        c.save()
        c.translate(200 + i * 330, y)
        c.rotate(rng.uniform(-20, 20))
        D.shade(c, D.rrect(-60, -22, 60, 0, 3), (200, 196, 186), k=0.1)
        c.restore()
    chip(c, f"{min(50, n)} REPORTS", 540, 300, 44)
    return st.arr


def s_office_clock(T, t, d):
    st = D.Stage()
    c = st.c
    D.backdrop(st, "office", sets.office)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((40, 44, 40), 0.35))
    hrs = 9 + 3 * ease(ramp(t, 0.1, 1.6))
    P.clock(c, 540, 700, 260, hrs, T)
    if t < d - 0.05:
        title_words(c, "3 HOURS GONE", 540, 1120, 96, Wd("a1", "no") + 0.2, T)
        chip(c, "office workers spend 1.8 hours a day just searching · McKinsey", 540, 1250, 26)
    return st.arr


def s_kitchen(T, t, d):
    st = D.Stage()
    c = st.c
    D.backdrop(st, "kitchen", sets.kitchen)
    P.rain(c, T, 0.3, 50, 110, 450, 280, 740)
    cast.person(c, "dad", 770, 1560, 0.7, T, pose="clasp", mood="worry", look=-0.6)               # your dad, at the table
    c.drawPath(path([(40, 1220), (1040, 1220), (1080, 1340), (0, 1340)]), paint((150, 110, 76)))       # the table, over him
    c.drawRect(skia.Rect.MakeLTRB(0, 1340, 1080, 1370), paint((110, 80, 56)))
    c.drawRect(skia.Rect.MakeLTRB(560, 1370, 1080, 1600), paint(shader=D.lin((0, 1370), (0, 1600), [(66, 56, 52), (58, 50, 46)])))
    D.shade(c, D.rrect(820, 1150, 880, 1225, 10), (230, 226, 216), k=0.2)                           # his pill bottle
    D.shade(c, D.rrect(815, 1132, 885, 1156, 6), (240, 120, 60), k=0.2)
    cast.person(c, "you", 330, 1760, 0.95, T, pose="hold2", mood="worry")
    P.letter(c, 330, 1180, 0.42, T, plain=0.0, rot=-4)
    return st.arr


def s_letter_close(T, t, d):
    st = D.Stage((60, 54, 50))
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.rad((540, 900), 900, [(120, 100, 80), (40, 34, 30)])))
    c.save()
    cam(c, 1.0 + 0.05 * t, 540, 900)
    P.letter(c, 540, 900, 1.45, T, plain=0.0, rot=-2)
    c.restore()
    for i in range(3):
        k = ramp(t, 0.4 + i * 0.4, 0.7 + i * 0.4)
        if k > 0:
            D.text(c, "?", [95, 985, 100][i], [470, 450, 1260][i], 140 * k, "fraunces-900", (200, 60, 50), tag="q")
    return st.arr


def s_shop(T, t, d):
    st = D.Stage()
    c = st.c
    c.save()
    cam(c, 1.0 + 0.03 * t, 540, 900)
    D.backdrop(st, "shop", sets.shop)
    hand = cast.person(c, "you", 540, 1760, 0.66, T, pose="hold", mood="smile")
    P.chocolate(c, hand[0] - 20, hand[1] - 10, 0.24, 0.0, T)
    c.restore()
    P.rain(c, T, 0.45, 160)
    return st.arr


def s_wrapper(T, t, d):
    st = D.Stage((50, 40, 40))
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.rad((540, 900), 900, [(110, 80, 60), (30, 22, 20)])))
    k = ease(ramp(T, C["ticket_flash"] - 0.1, C["ticket_flash"] + 0.6))
    P.chocolate(c, 540, 900, 1.9, k, T)
    if k > 0.3:
        P.ticket(c, 540, 900 - 400 * ease(ramp(k, 0.4, 1.0)), 700, rot=-6, T=T, glow=0.6 * k)
    return st.arr


def s_ticket(T, t, d):
    st = D.Stage()
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.rad((540, 860), 1100, [(255, 214, 140), (150, 80, 40)])))
    z = 1.0 + 0.18 * ease(t / max(d, 0.1))                            # the 70s zoom
    c.save()
    cam(c, z, 540, 860)
    P.ticket(c, 540, 860, 920, rot=-3, T=T, glow=0.6)
    c.restore()
    k = ease(ramp(T, C["you_bring"] - 0.2, C["you_bring"] + 0.4))
    if k > 0:                                                           # the letter, folded, tucked behind the ticket
        c.save()
        c.translate(820, 1180 + 200 * (1 - k))
        c.rotate(12)
        D.shade(c, D.rrect(-110, -70, 110, 70, 4), (240, 230, 205), k=0.1)
        c.drawLine(-110, 0, 110, 0, paint((190, 180, 160), stroke=3))
        c.restore()
    return st.arr


# ------------------------------------------------------------------ the newsreel

def _news_frame(c, T):
    """Newsreel furniture: the rounded projection frame, the title strip."""
    D.text(c, "WORLD NEWS REEL", 540, 300, 46, "oldstandard-700", WHITE, tag="news")


def s_news1(T, t, d):
    st = D.Stage((90, 90, 90))
    c = st.c
    if t < 0.45:                                                        # the film leader: a countdown circle
        c.drawRect(skia.Rect.MakeWH(W, H), paint((150, 150, 150)))
        c.drawCircle(540, 960, 420, paint(WHITE, stroke=12))
        c.drawCircle(540, 960, 360, paint(WHITE, stroke=6))
        a = t / 0.45 * 360
        c.drawArc(skia.Rect.MakeLTRB(120, 540, 960, 1380), -90, a, True, paint((60, 60, 60), 0.5))
        D.text(c, "3", 540, 1060, 300, "oldstandard-700", WHITE, tag="leader")
        return st.arr
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.rad((540, 960), 1100, [(170, 170, 170), (60, 60, 60)])))
    _news_frame(c, T)
    k = ease(ramp(t, 0.45, 1.0))
    P.headline(c, 540, 900, 0.3 + 0.95 * k, (1 - k) * 720, "THINKING MACHINES IN EVERY POCKET!", "EXTRA · EXTRA · EXTRA")
    return st.arr


def s_news2(T, t, d):
    st = D.Stage((90, 90, 90))
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.rad((540, 960), 1100, [(170, 170, 170), (60, 60, 60)])))
    _news_frame(c, T)
    heads = [(C["h_better"], "CONSULTANTS: 40% BETTER WORK", "on tasks AI is good at|Harvard Business School & BCG study, 2023"),
             (C["h_faster"], "WRITERS: 40% FASTER, 18% BETTER", "on professional writing tasks|Noy & Zhang, Science, 2023"),
             (C["h_beginners"], "BEGINNERS GAIN MOST: +34%", "customer support agents|Brynjolfsson et al., QJE, 2025")]
    cur = [h for h in heads if T >= h[0] - 0.3]
    if cur:
        t0, big, small = cur[-1]
        k = ease(ramp(T, t0 - 0.3, t0))
        P.headline(c, 540, 900, 0.3 + 0.8 * k, (1 - k) * 720 * (1 if len(cur) % 2 else -1), big, small)
    return st.arr


def _interview(st, T, who, where, caption, spk, use=None):
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.lin((0, 0), (0, H), [(190, 190, 190), (120, 120, 120)])))
    if where == "field":
        c.drawRect(skia.Rect.MakeLTRB(0, 1000, W, H), paint((110, 110, 110)))
        for i in range(30):
            c.drawLine(i * 40, 1000, i * 40 - 100, H, paint((90, 90, 90), stroke=6))
    else:
        c.drawRect(skia.Rect.MakeLTRB(120, 300, 960, 780), paint((70, 70, 70)))                         # a blackboard
        D.text(c, "ESSAY: WHY?", 540, 560, 70, "special-elite-400", (220, 220, 220), tag="board")
        c.drawRect(skia.Rect.MakeLTRB(0, 1100, W, H), paint((130, 130, 130)))
    hand = cast.person(c, who, 540, 1780, 0.95, T, pose="hold", mood="smile", talk=talk(spk, T))
    c.drawLine(900, 1000, 760, 880, paint((40, 40, 40), stroke=14))                                      # the reporter's mic
    D.shade(c, D.rrect(740, 820, 800, 900, 20), (60, 60, 60), k=0.3)
    chip(c, caption, 540, 300, 32, fg=WHITE, bg=(40, 40, 40))
    chip(c, "RE-ENACTMENT", 540, 360, 24, fg=(200, 200, 200), bg=(40, 40, 40))
    if use:
        chip(c, use, 540, 450, 34, fg=INK, bg=(230, 230, 230), tag="usechip")


def s_news_farmer(T, t, d):
    st = D.Stage()
    _interview(st, T, "farmer", "field", "A FARMER", "FARMER", "EXPLAIN  ·  TRANSLATE JARGON")
    return st.arr


def s_news_student(T, t, d):
    st = D.Stage()
    _interview(st, T, "student", "class", "A STUDENT", "STUDENT", "CRITIQUE AN ARGUMENT")
    return st.arr


# ------------------------------------------------------------------ the gates and the host

GUESTS = (("copier", 110, "THE COPIER", 1045), ("believer", 250, "THE BELIEVER", 905), ("you", 390, None, 0),
          ("yesman", 690, "THE YES-MAN", 905), ("rusher", 840, "THE RUSHER", 1030))


def s_gates(T, t, d):
    st = D.Stage()
    c = st.c
    c.save()
    cam(c, 1.0 + 0.06 * ease(t / max(d, 0.1)), 540, 1100)
    D.backdrop(st, "gates", sets.gates)
    k = ease(ramp(t, 0.2, 1.4))
    cast.person(c, "host", 540, 1330, 0.46, T, pose="wave" if k > 0.8 else "cane", mood="smile",
                talk=talk("HOST", T), walk=0 if k >= 1 else t)
    for who, x, name, cy in GUESTS:
        hand = cast.person(c, who, x, 1330, 0.42, T, pose="hold", mood="wow", look=0.8 if x < 540 else -0.8)
        P.ticket(c, hand[0], hand[1] - 8, 70, rot=-10, T=T, glow=0.3, lines=("", ""), head="")
    c.restore()
    for who, x, name, cy in GUESTS:
        if name:
            chip(c, name, min(880, max(200, x)), cy, 22)
    return st.arr


def s_host_rule(T, t, d):
    st = D.Stage()
    c = st.c
    c.save()
    cam(c, 2.1, 540, 1000)
    D.backdrop(st, "gates", sets.gates)
    c.restore()
    c.drawRect(skia.Rect.MakeWH(W, H), paint((255, 230, 190), 0.15))
    hand = cast.person(c, "host", 540, 2350, 1.35, T, pose=(10, 0, 150, -30), mood="smile", talk=talk("HOST", T))
    c.drawCircle(hand[0], hand[1] - 40, 40, paint((255, 240, 180), 0.5, blur=20))
    return st.arr


def s_host_menace(T, t, d):
    st = D.Stage((20, 14, 12))
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.rad((540, 1100), 900, [(80, 40, 30), (10, 6, 6)])))
    c.save()
    cam(c, 1.0 + 0.12 * ease(t / max(d, 0.1)), 540, 700)
    cast.person(c, "host", 540, 2700, 1.9, T, pose="clasp", mood="sly", talk=talk("HOST", T))
    c.restore()
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.lin((0, 0), (0, H), [(0, 0, 0, 0.55), (0, 0, 0, 0.0), (0, 0, 0, 0.4)])))
    return st.arr

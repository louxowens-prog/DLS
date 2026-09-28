"""Scenes 4: where a million is too many (ads vs aircraft, grids, weapons, medicine), the rule, the showtune
finale with the big red button, the guestbook payoff, the end card."""
import math

import numpy as np
import skia

import bg
import cast
import kit
import kk
import ov
from cues import C, ls
from kk import BLOOD, CREAM, HOT, INK, LEMON, LILAC, MINT, ORANGE, PINK, SKY, WHITE, W, H, ease, paint, path, ramp, twos
from timeline import TL

S, E, Wd = TL.s, TL.e, TL.word


def s_ads(T, t, d):
    """A million bad ads? You shrug: the family watches an absurd ad on the telly and shrugs, in unison."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.lobby())

    def screen(c, x0, y0, x1, y1):
        c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(LEMON))
        kk.text(c, "BABY SHOES", (x0 + x1) / 2, y0 + 150, 44, "dela-400", HOT, tag="tv", outline=WHITE, ow=8)
        kk.text(c, "FOR YOUR DOG!", (x0 + x1) / 2, y0 + 230, 40, "dela-400", SKY, tag="tv", outline=WHITE, ow=8)
        kk.text(c, "ad picked just for you", (x0 + x1) / 2, y0 + 330, 30, "rounded-800", INK, tag="tv")

    kit.tv(c, 540, 700, 1.05, T, screen)
    shrug = T >= Wd("f1", "shrug.") - 0.25
    for i, (who, x) in enumerate((("grandpa", 150), ("papa", 390), ("mama", 690), ("girl", 930))):
        cast.person(c, who, x, 1820, 0.5, T, pose="shrug" if shrug else "stand", mood="flat")
    return st.arr


def s_translate(T, t, d):
    """But one auto-translation turned 'good morning' into 'attack them', and a man was arrested."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.lobby())
    flipped = T >= C["attack"] - 0.1
    arrested = T >= C["arrested"] - 0.1

    def screen(c, x0, y0, x1, y1):
        c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint((245, 245, 250)))
        c.drawCircle(x0 + 60, y0 + 70, 34, paint((120, 190, 255)))
        c.drawRect(skia.Rect.MakeLTRB(x0 + 110, y0 + 50, x0 + 330, y0 + 70), paint((180, 180, 190)))
        c.drawRect(skia.Rect.MakeLTRB(x0 + 20, y0 + 130, x1 - 20, y0 + 390), paint((255, 200, 90)))
        c.drawRect(skia.Rect.MakeLTRB(x0 + 60, y0 + 280, x0 + 250, y0 + 360), paint((230, 170, 40)))   # a little bulldozer
        c.drawCircle(x0 + 100, y0 + 365, 28, paint(INK))
        c.drawCircle(x0 + 210, y0 + 365, 28, paint(INK))
        c.drawRect(skia.Rect.MakeLTRB(x0 + 250, y0 + 250, x0 + 330, y0 + 330), paint((230, 170, 40)))
        kk.text(c, "original post (Arabic):", (x0 + x1) / 2, y0 + 450, 26, "rounded-800", (120, 120, 140), tag="phone")
        kk.text(c, "“Good morning!” ☀", (x0 + x1) / 2, y0 + 505, 40, "rounded-900", INK, tag="phone")
        kk.text(c, "auto-translated:", (x0 + x1) / 2, y0 + 580, 26, "rounded-800", (120, 120, 140), tag="phone")
        if flipped:
            kk.text(c, "“ATTACK THEM”", (x0 + x1) / 2, y0 + 650, 40, "dela-400", BLOOD, tag="phone")
        else:
            kk.text(c, "…", (x0 + x1) / 2, y0 + 650, 50, "dela-400", (150, 150, 160), tag="phone")

    kit.phone(c, 540, 820, 1.0, T, screen)
    if arrested:
        blink = int(T * 8) % 2
        with kk.layer(c, 1.0, skia.BlendMode.kPlus):
            c.drawRect(skia.Rect.MakeWH(W, H), paint((255, 0, 0) if blink else (0, 60, 255), 0.28))
        k = kk.pop(T, C["arrested"] - 0.1, 0.18, 0.3)
        c.save()
        c.translate(540, 470)
        c.scale(k, k)
        c.rotate(-8)
        kk.text(c, "ARRESTED", 0, 0, 110, "dela-400", WHITE, tag="stamp", outline=BLOOD, ow=18, outline2=INK, ow2=28)
        c.restore()
    kit.plaque(c, "2017 · social-media auto-translation", 540, 1270)
    return st.arr


def s_one(T, t, d):
    """But some machines can't afford even one: a single clay X in an empty white room. Then silence."""
    st = kk.Stage(CREAM)
    c = st.c
    z = 1.0 + 0.25 * ease(t / d)
    c.save()
    c.translate(540, 820)
    c.scale(z, z)
    kit.clay_x(c, 0, 0, 1.2, T, seed=3)
    c.restore()
    return st.arr


# ------------------------------------------------------------------ the four things that must not fail (claymation)

def _plane(c, x, y, s, T, pitch, sensor=0.0):
    tt = twos(T)
    c.save()
    c.translate(x, y)
    c.rotate(pitch)
    c.scale(s, s)
    kk.clay_poly(c, [(-60, -18), (-240, -160), (-170, -170), (60, -30)], (230, 235, 245), tt, seed=71, amp=4, prints=1)
    kk.clay_poly(c, [(-330, -20), (-400, -140), (-350, -140), (-280, -30)], (60, 120, 220), tt, seed=72, amp=4, prints=0)
    import cast as _c
    kk.clay_path(c, _c._capsule(-360, 0, 330, 0, 58), (245, 245, 250), tt, seed=70, prints=2, marks=2)
    c.drawRect(skia.Rect.MakeLTRB(-340, 10, 300, 24), paint((60, 120, 220)))
    for k in range(10):
        c.drawCircle(-250 + k * 52, -12, 10, paint((90, 150, 230)))
    kk.clay_poly(c, [(-60, 18), (-230, 150), (-160, 160), (60, 30)], (215, 220, 235), tt, seed=73, amp=4, prints=1)
    c.drawCircle(300, 30, 14, paint((255, 40, 40) if sensor > 0 else (120, 120, 130)))
    if sensor > 0:
        c.drawCircle(300, 30, 50, paint(shader=kk.rad((300, 30), 50, [(255, 40, 40, 0.8), (255, 40, 40, 0.0)])))
    c.restore()


def s_plane(T, t, d):
    """Aircraft: one bad sensor, and the automation keeps forcing the nose down - push after push."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.storm())
    t_push = C["nose"] - 1.0
    pushes = max(0, int((twos(T) - t_push) / 0.55) + 1) if T >= t_push else 0
    pitch = min(40, pushes * 7) + (4 * math.sin(T * 30) if pushes else 0)
    fall = max(0.0, T - t_push) * 160
    _plane(c, 560, 700 + fall, 1.05, T, pitch, sensor=1.0 if T >= C["sensor"] - 0.2 else 0.0)
    if T >= C["sensor"] - 0.2 and T < t_push:
        kit.tag_label(c, "1 BAD SENSOR", 820, 560, 34, color=BLOOD)
    if pushes:
        for k in range(min(pushes, 4)):
            ax = 360 + k * 90
            kk.clay_poly(c, [(ax - 18, 400), (ax + 18, 400), (ax + 18, 470), (ax + 40, 470), (ax, 520), (ax - 40, 470), (ax - 18, 470)],
                         BLOOD, twos(T), seed=80 + k, amp=2, prints=0, marks=0)
    ov.slam(c, "346", 540, 470, 190, T, C["p346"] - 0.1, color=WHITE, edge=BLOOD, sub="PEOPLE DIED")
    kit.plaque(c, "737 MAX · Lion Air 610 & Ethiopian 302 · 2018–19", 540, 1270, 26)
    kk.red(st.arr, 0.2)
    return st.arr


def s_grid(T, t, d):
    """Power grids: the bug silences the alarm bell; the city goes dark, block by block."""
    st = kk.Stage((10, 8, 30))
    c = st.c
    tt = twos(T)
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 1250), paint(shader=kk.lin((0, 0), (0, 1250), [(10, 10, 40), (50, 30, 90)])))
    dark_t = C["alarms"] + 0.2
    for i in range(9):
        bx = 40 + i * 118
        bh = 280 + (i * 97) % 260
        kk.clay_poly(c, [(bx, 1250), (bx, 1250 - bh), (bx + 100, 1250 - bh), (bx + 100, 1250)], (70, 70, 100), tt, seed=90 + i, amp=3,
                     prints=1, marks=1)
        off = T >= dark_t + i * 0.12
        for r in range(int(bh / 60)):
            for q in range(2):
                on = not off and ((r + q + i) % 4 != 0)
                c.drawRect(skia.Rect.MakeXYWH(bx + 18 + q * 44, 1250 - bh + 30 + r * 60, 26, 30), paint(LEMON if on else (35, 35, 55)))
    c.drawRect(skia.Rect.MakeLTRB(0, 1250, W, H), paint((25, 40, 30)))
    for px in (180, 900):                                              # pylons
        kk.clay_poly(c, [(px - 70, 1250), (px - 12, 720), (px + 12, 720), (px + 70, 1250)], (150, 150, 170), tt, seed=px, amp=3, prints=0)
    c.drawPath(path(kk.bez((180, 760), (540, 900), (900, 760), 20), closed=False), paint((190, 190, 210), stroke=5))
    bell_x, bell_y = 540, 500
    ring = 0 if T >= C["alarms"] - 0.3 else math.sin(T * 40) * 10
    c.save()
    c.translate(bell_x, bell_y)
    c.rotate(ring)
    kk.clay_ellipse(c, 0, 0, 120, 110, (255, 200, 40), tt, seed=99)
    c.restore()
    if T >= C["alarms"] - 0.3:
        kit.clay_x(c, bell_x, bell_y, 0.8, T, seed=7)
    ov.slam(c, "55,000,000", 540, 470, 120, T, C["p55"] - 0.1, color=LEMON, edge=HOT, sub="LOST POWER")
    kit.plaque(c, "Northeast blackout · 2003", 540, 1330)
    return st.arr


def s_missile(T, t, d):
    """Weapons: the clock drifts a third of a second; the interceptor misses."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.storm())
    tt = twos(T)
    kk.clay_ellipse(c, 300, 700, 190, 190, (245, 240, 225), tt, seed=110, amp=0.04, prints=2)
    for k in range(12):
        a = k * math.pi / 6
        c.drawLine(300 + 150 * math.cos(a), 700 + 150 * math.sin(a), 300 + 170 * math.cos(a), 700 + 170 * math.sin(a), paint(INK, stroke=6))
    drift = ramp(T, C["drift"] - 0.2, C["drift"] + 1.0)
    for ghost, a0 in ((0.35, 0.0), (1.0, 0.5 * drift)):
        a = -math.pi / 2 + T * 1.2 + a0
        c.drawLine(300, 700, 300 + 140 * math.cos(a), 700 + 140 * math.sin(a), paint(BLOOD if ghost > 0.5 else INK, ghost, stroke=10))
    if drift > 0:
        kk.clay_text(c, "+0.34 s", 300, 1000, 76, BLOOD, tt, seed=111, tag="missile")
    sx = 1200 - (tt - (T - t)) * 330                                     # the incoming missile
    kk.clay_path(c, cast._capsule(sx, 520, sx + 190, 470, 26), (90, 140, 70), tt, seed=112)
    lt = max(0.0, tt - (T - t) - 1.2)                                  # the interceptor, too late
    iy = 1250 - lt * 900
    ix = 820 + lt * 60
    if iy > 300:
        kk.clay_path(c, cast._capsule(ix, iy, ix + 20, iy + 150, 20), (220, 220, 230), tt, seed=113)
        c.drawCircle(ix + 22, iy + 175, 26, paint(ORANGE))
    ov.slam(c, "28", 540, 470, 200, T, C["p28"] - 0.1, color=WHITE, edge=BLOOD, sub="SOLDIERS DIED")
    kit.plaque(c, "Patriot missile clock drift · Dhahran · 1991", 540, 1270, 28)
    kk.red(st.arr, 0.2)
    return st.arr


def s_radiation(T, t, d):
    """Medicine: one software bug, six patients, six massive overdoses."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.tabletop((190, 235, 215)))
    tt = twos(T)
    kk.clay_poly(c, [(300, 1150), (300, 450), (560, 380), (780, 450), (780, 600), (560, 560), (460, 600), (460, 1150)], (230, 230, 240),
                 tt, seed=120, amp=6, prints=2, marks=2)
    glow = 0.5 + 0.5 * math.sin(T * 12)
    c.drawPath(path([(620, 600), (700, 600), (820, 1000), (500, 1000)]), paint((255, 60, 200), 0.25 + 0.2 * glow))
    for i in range(6):
        x = 170 + i * 150
        lit = T >= C["p6"] + i * 0.12
        kk.clay_ellipse(c, x, 1150, 48, 70, (255, 80, 60) if lit else (140, 170, 230), tt, seed=130 + i, prints=1)
        kk.clay_ellipse(c, x, 1050, 36, 36, (255, 200, 160), tt, seed=140 + i, prints=0)
    ov.slam(c, "6", 540, 470, 220, T, C["p6"] - 0.05, color=WHITE, edge=BLOOD, sub="MASSIVE OVERDOSES")
    kit.plaque(c, "Therac-25 radiation machine · 1985–87", 540, 1290, 28)
    return st.arr


# ------------------------------------------------------------------ the rule, the finale, the payoff

def s_rule2(T, t, d):
    st = kk.Stage()
    c = st.c
    kk.starburst(c, 540, 800, T, (kk.MINT, kk.LEMON))
    rows = [("SCALE", "▲", C["scale"], (40, 160, 70)), ("STAKES", "▲", C["stakes"], (40, 160, 70)),
            ("ROOM FOR ERROR", "▼", C["smaller"], BLOOD)]
    for i, (word, arrow, tk, col) in enumerate(rows):
        k = kk.pop(T, tk - 0.2, 0.25, 0.15)
        if k <= 0:
            continue
        y = 420 + i * 260
        c.save()
        c.translate(540, y)
        c.scale(k, k)
        kk.chrome_text(c, word, -60, 0, 96 if i < 2 else 78, T, max_w=700, tag="rule2")
        kk.text(c, arrow, 400, 0, 120, "rounded-900", col, tag="rule2", outline=WHITE, ow=12)
        c.restore()
    if T >= C["smaller"]:
        sq = 1 - 0.8 * ease(ramp(T, C["smaller"], C["smaller"] + 1.2))
        kit.clay_x(c, 540, 1180, 0.5 * sq + 0.05, T, seed=5)
    return st.arr


def _show_beat():
    return TL.songs["s4"]["beat"]


def s_finale_a(T, t, d):
    """The showtune finale: the whole cast in a kick line under the rainbow, the dead included."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.meadow(2))
    b = _show_beat()
    for i in range(3):
        kit.firework(c, 200 + i * 340, 380 + (i % 2) * 120, (T - S("s4") - i * 0.6) % 1.8, [LEMON, HOT, SKY][i], seed=i)
    for i in range(3):
        cast.corpse(c, 250 + i * 290, 1300, 0.45, T, pose=cast.dance_pose(T - S("s4"), b, "show", i), seed=40 + i)
    for i, (who, x) in enumerate((("grandpa", 140), ("papa", 380), ("mama", 700), ("girl", 940))):
        kick = abs(math.sin((T - S("s4")) / b * math.pi))
        cast.person(c, who, x, 1850, 0.5, T, pose=cast.dance_pose(T - S("s4"), b, "show", i), bob=20 * kick, mood="smile" if i == 2 else "flat")
    kit.confetti(c, T, 60, t0=S("s4"))
    return st.arr


def s_finale_b(T, t, d):
    """The meadow moment: she spins, arms out, flowers and sky wheeling behind her."""
    st = kk.Stage()
    c = st.c
    ang = t * 0.35
    c.save()
    c.translate(540, 1300)
    c.rotate(math.degrees(ang) * 0.15)
    c.translate(-540, -1300)
    kit.backdrop(st, bg.meadow(3))
    c.restore()
    cs = math.cos(T * 5.5)
    spin = math.copysign(0.4 + 0.6 * abs(cs), cs)
    cast.person(c, "girl", 540, 1800, 0.95, T, pose="arms_out", spin=spin, mood="smile")
    for i in range(8):
        a = i * math.pi / 4 + T * 1.5
        kk.cg_star(c, 540 + 440 * math.cos(a), 900 + 300 * math.sin(a), 40, T, seed=i, color=[LEMON, HOT, WHITE, MINT][i % 4])
    return st.arr


def s_finale_c(T, t, d):
    """Watch for the mistake that keeps coming back: Grandpa and a magnifying glass over the guestbook - the same
    red X, again and again. The little error peeks out."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.lobby())
    cast.guestbook(c, 540, 1020, 1.3, T, marks=9, rot=-3)
    mx = 400 + 280 * ease(ramp(t, 0.2, 1.8))
    c.drawCircle(mx, 960, 130, paint((200, 230, 255), 0.25))
    c.drawCircle(mx, 960, 130, paint((120, 70, 40), stroke=18))
    c.drawLine(mx + 92, 1052, mx + 200, 1160, paint((120, 70, 40), stroke=26))
    cast.creature(c, 930, 760, 0.55, T, mood="grin", look=(-0.6, 0.2))
    return st.arr


def s_finale_d(T, t, d):
    """And keep a big red button: Mama slams STOP; the machine's screen blinks out; fireworks."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.meadow(2))
    t_press = ls("s4_3") + 0.7
    pressed = T >= t_press
    b = _show_beat()
    cast.machine(c, 800, 1320, 0.6, T, face="off" if pressed else "evil")
    press = ramp(T, t_press - 0.1, t_press) * (1 - ramp(T, t_press + 0.3, t_press + 0.5))
    kit.big_button(c, 330, 1000, 0.85, press=press)
    cast.person(c, "mama", 330, 1700, 0.5, T, pose=(20, 0, 150 - 60 * press, 20) if not pressed else cast.dance_pose(T, b, "show", 0),
                mood="flat")
    if pressed:
        for i in range(4):
            kit.firework(c, 160 + i * 260, 360 + (i % 2) * 140, T - t_press - i * 0.25, [LEMON, HOT, SKY, MINT][i], seed=i + 5)
        kit.confetti(c, T, 70, t0=t_press)
    return st.arr


def s_payoff(T, t, d):
    """Somewhere in the next billion decisions is yours: the guestbook is a mountain now, open at a line with
    your name on it. Behind it, the little error - not so little."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.storm())
    bg.volcano(c, 760, 1250, 1.1, glow=1.0)
    rise = ease(ramp(t, 0.2, 2.0))
    cast.creature(c, 700, 1450 - 300 * rise, 2.6, T, mood="open", look=(-0.3, 0.4))
    for k in range(9):                                                  # the pile of guestbooks
        y = 1500 - k * 60
        kk.clay_poly(c, [(250 + k * 6, y), (250 + k * 6, y - 55), (830 - k * 6, y - 55), (830 - k * 6, y)],
                     [(170, 30, 50), (40, 90, 170), (200, 120, 40)][k % 3], twos(T), seed=150 + k, amp=4, prints=1, marks=1)
    cast.guestbook(c, 540, 900, 1.12, T, marks=16, rot=-4, you=True)
    cast.crow(c, 860, 700, 0.6, T, caw=1.0 if t > 1.0 else 0.0, flip=True)
    kk.red(st.arr, 0.25)
    return st.arr


def s_end(T, t, d):
    st = kk.Stage()
    c = st.c
    kk.starburst(c, 540, 700, T * 0.5, ((40, 20, 70), (70, 30, 110)))
    kk.chrome_text(c, "THE END", 540, 430, 130, T, max_w=800, tag="end")
    kk.text(c, "(probably)", 540, 520, 46, "rounded-900", LEMON, tag="end", outline=INK, ow=10)
    srcs = ["Michigan MiDAS: UIA review; Bauserman settlement",
            "Robodebt Royal Commission, 2023",
            "737 MAX: Indonesian, Ethiopian & US investigations",
            "2003 blackout: US–Canada Task Force report",
            "Patriot, Dhahran 1991: GAO IMTEC-92-26",
            "Therac-25: Leveson & Turner, 1993",
            "Auto-translation arrest: Haaretz, Oct 2017"]
    for i, s in enumerate(srcs):
        kk.text(c, s, 540, 640 + i * 62, 32, "rounded-800", WHITE, tag="source")
    kk.text(c, "Check the machine. Keep a human.", 540, 1150, 44, "mochiy-400", kk.PINK, tag="end", outline=INK, ow=8)
    cast.creature(c, 540, 1330, 0.55, T, mood="grin", look=(0.3, -0.2))
    return st.arr

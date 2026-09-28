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
        cast.person(c, who, x, 1650, 0.48, T, pose="shrug" if shrug else "stand", mood="flat")
    return st.arr


def s_translate(T, t, d):
    """But one auto-translation turned 'good morning' into 'attack them', and a man was arrested."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.lobby())
    flipped = T >= C["attack"]
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
        kk.text(c, "original post (Arabic):", (x0 + x1) / 2, y0 + 450, 34, "rounded-900", (90, 90, 110), tag="phone")
        kk.text(c, "“Good morning!” ☀", (x0 + x1) / 2, y0 + 505, 40, "rounded-900", INK, tag="phone")
        kk.text(c, "auto-translated:", (x0 + x1) / 2, y0 + 580, 34, "rounded-900", (90, 90, 110), tag="phone")
        if flipped:
            fs = min(46, 32 * (x1 - x0 - 50) / kk.font("dela-400", 32).measureText("“ATTACK THEM”"))
            kk.text(c, "“ATTACK THEM”", (x0 + x1) / 2, y0 + 655, fs, "dela-400", BLOOD, tag="phone")
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
    z = 1.0 + 0.9 * ease(min(1.0, t / d))
    c.save()
    c.translate(540, 820)
    c.scale(z, z)
    c.rotate(4 * math.sin(t * 0.9))
    for i in range(5):                                                   # it bleeds, slowly, into the white room
        kk.drip(c, -120 + i * 60, 60 + (i % 2) * 30, 10, 20 + 90 * ease(min(1.0, max(0.0, t - 0.4 - i * 0.3) / 2.5)), BLOOD)
    kit.clay_x(c, 0, 0, 1.2, T, seed=3)
    c.restore()
    beat = abs(math.sin(t * math.pi / 0.85)) ** 6                        # a heartbeat of red at the edges
    kk.red(st.arr, 0.06 + 0.12 * beat)
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


def _boom(c, x, y, T, t0, seed=0, scale=1.0):
    """A clay explosion on twos: fireball lumps flung out, black smoke lumps rising, then settling."""
    u = twos(T) - t0
    if u < 0:
        return
    rng = np.random.default_rng(seed)
    k = min(1.0, u / 0.9)
    for i in range(10):                                                  # smoke
        a = rng.uniform(-2.8, -0.3)
        r = (80 + 260 * k) * scale
        kk.clay_ellipse(c, x + r * math.cos(a) * 0.8, y + r * math.sin(a) - 120 * k * scale, (70 + 50 * k) * scale,
                        (60 + 40 * k) * scale, (60, 55, 65), twos(T), seed=seed * 50 + i, prints=1, marks=0)
    for i in range(14):                                                  # fire
        a = rng.uniform(-3.0, -0.1)
        r = (40 + 380 * k) * scale * rng.uniform(0.6, 1.0)
        rr = (60 * (1 - 0.6 * k) + 20) * scale
        col = [(255, 200, 40), (255, 120, 20), (230, 40, 20)][i % 3]
        kk.clay_ellipse(c, x + r * math.cos(a), y + r * math.sin(a) * 0.8, rr, rr * 0.85, col, twos(T), seed=seed * 50 + 20 + i,
                        prints=0, marks=0, gloss=0.35)
    if u < 0.12:
        c.drawRect(skia.Rect.MakeWH(W, H), paint(WHITE, 0.75))


def s_plane(T, t, d):
    """Aircraft: one bad sensor, and the automation keeps forcing the nose down - push after push - into the ground."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.storm())
    t_push = C["nose"] - 1.0
    t_imp = C["impact_plane"]
    pushes = max(0, int((twos(T) - t_push) / 0.55) + 1) if T >= t_push else 0
    pitch = min(40, pushes * 7) + (4 * math.sin(T * 30) if pushes else 0)
    ts = C["sensor"] - 0.2
    if T >= ts and not pushes:                                           # MCAS: nose-down jolt, pull-up, jolt...
        ph = ((twos(T) - ts) / 0.9) % 1.0
        pitch += 11 * (1 - ph) ** 2
    u = ramp(T, t_push, t_imp)
    drift = 40 * math.sin(t * 1.3)
    for i in range(14):                                                  # wind streaks rushing past
        sx = (1200 - ((t * 2600 + i * 173) % 1400))
        sy = 300 + (i * 97) % 800
        c.drawLine(sx, sy, sx + 160, sy, paint(WHITE, 0.35, stroke=4))
    if T < t_imp:
        _plane(c, 560 - 80 * u + drift, 700 + 560 * u * u + 30 * math.sin(t * 2.1), 1.05, T, pitch,
               sensor=1.0 if T >= C["sensor"] - 0.2 else 0.0)
    if T >= C["sensor"] - 0.2 and T < t_push:
        kit.tag_label(c, "1 BAD SENSOR", 760, 560, 46, color=BLOOD)
    if pushes and T < t_imp:
        for k in range(min(pushes, 4)):
            ax = 360 + k * 90
            kk.clay_poly(c, [(ax - 18, 400), (ax + 18, 400), (ax + 18, 470), (ax + 40, 470), (ax, 520), (ax - 40, 470), (ax - 18, 470)],
                         BLOOD, twos(T), seed=80 + k, amp=2, prints=0, marks=0)
    _boom(c, 480, 1260, T, t_imp, seed=1, scale=1.2)
    ov.slam(c, "346", 540, 420, 190, T, C["p346"] - 0.1, color=WHITE, edge=BLOOD, sub="PEOPLE DIED")
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
    ov.slam(c, "50,000,000", 540, 470, 120, T, C["p50"], color=LEMON, edge=HOT, sub="PEOPLE LOST POWER")
    kit.plaque(c, "Northeast blackout · 2003", 540, 1330)
    return st.arr


def s_missile(T, t, d):
    """Weapons: the clock drifts a third of a second; the interceptor goes up where the missile WAS; the barracks."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.storm())
    tt = twos(T)
    cx, cy = 250, 820
    kk.clay_ellipse(c, cx, cy, 150, 150, (245, 240, 225), tt, seed=110, amp=0.04, prints=2)
    for k in range(12):
        a = k * math.pi / 6
        c.drawLine(cx + 118 * math.cos(a), cy + 118 * math.sin(a), cx + 134 * math.cos(a), cy + 134 * math.sin(a), paint(INK, stroke=6))
    drift = ramp(T, C["drift"] - 0.2, C["drift"] + 1.0)
    for ghost, a0 in ((0.35, 0.0), (1.0, 0.5 * drift)):
        a = -math.pi / 2 + T * 1.2 + a0
        c.drawLine(cx, cy, cx + 110 * math.cos(a), cy + 110 * math.sin(a), paint(BLOOD if ghost > 0.5 else INK, ghost, stroke=10))
    if drift > 0:
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(cx - 150, cy + 175, cx + 150, cy + 275), 20, 20), paint(INK, 0.85))
        kk.clay_text(c, "+0.34 s", cx, cy + 250, 70, (255, 230, 60), tt, seed=111, tag="missile")
    t0 = T - t
    t_hit = C["impact_missile"]
    u = ramp(tt, t0, t_hit)                                               # the incoming missile, arcing down
    sx, sy = -120 + 880 * u, 380 + 800 * u * u
    kit.clay_house(c, 760, 1265, 0.8, T, seed=33, wall=(190, 180, 150), roof=(120, 110, 90))
    if T < t_hit:
        ang = math.atan2(800 * 2 * u, 880)
        kk.clay_path(c, cast._capsule(sx, sy, sx - 190 * math.cos(ang), sy - 190 * math.sin(ang), 26),
                     (90, 140, 70), tt, seed=112)
    lt = max(0.0, tt - (C["drift"] + 0.4))                               # the interceptor, aimed where it was
    iy = 1250 - lt * 1100
    ix = 860 + lt * 40
    if iy > 150 and T > C["drift"] + 0.4:
        kk.clay_path(c, cast._capsule(ix, iy, ix + 20, iy + 150, 20), (220, 220, 230), tt, seed=113)
        c.drawCircle(ix + 22, iy + 175, 26, paint(ORANGE))
    _boom(c, 760, 1180, T, t_hit, seed=2, scale=0.9)
    ov.slam(c, "28", 620, 420, 200, T, C["p28"] - 0.1, color=WHITE, edge=BLOOD, sub="SOLDIERS DIED")
    kit.plaque(c, "Patriot missile clock drift · Dhahran · 1991", 540, 1330, 28)
    kk.red(st.arr, 0.2)
    return st.arr


def s_radiation(T, t, d):
    """Medicine: software bugs; the beam flares a hundred times too hot; six patients, six overdoses."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.dark_table())
    tt = twos(T)
    kk.clay_poly(c, [(300, 1150), (300, 450), (560, 380), (780, 450), (780, 600), (560, 560), (460, 600), (460, 1150)], (230, 230, 240),
                 tt, seed=120, amp=6, prints=2, marks=2)
    t_fl = C["p6"]
    hot = ramp(T, t_fl, t_fl + 0.2)
    glow = 0.5 + 0.5 * math.sin(T * 12)
    c.drawPath(path([(620, 600), (700, 600), (820 + 200 * hot, 1060), (500 - 200 * hot, 1060)]),
               paint((255, 60 + 180 * hot, 200 + 55 * hot), 0.25 + 0.2 * glow + 0.4 * hot))
    for i in range(6):
        x = 170 + i * 150
        lit = T >= C["p6"] + 0.1 + i * 0.12
        kk.clay_ellipse(c, x, 1150, 48, 70, (255, 80, 60) if lit else (140, 170, 230), tt, seed=130 + i, prints=1)
        kk.clay_ellipse(c, x, 1050, 36, 36, (255, 200, 160), tt, seed=140 + i, prints=0)
        if lit:
            c.drawCircle(x, 1100, 90, paint(shader=kk.rad((x, 1100), 90, [(255, 60, 40, 0.5), (255, 60, 40, 0.0)])))
    if t_fl <= T < t_fl + 0.12:
        c.drawRect(skia.Rect.MakeWH(W, H), paint(WHITE, 0.7))
    ov.slam(c, "6", 540, 420, 220, T, C["p6"], color=WHITE, edge=BLOOD, sub="MASSIVE OVERDOSES")
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
    if T >= C["scale"] - 0.2:                                              # scale: the envelopes multiply
        n = min(12, 1 + int((T - C["scale"] + 0.2) / 0.12))
        for i in range(n):
            cast.envelope(c, 150 + i * 70, 530 + (i % 2) * 14, 0.28, T, seed=i, rot=(i * 23) % 30 - 15, label=None)
    if T >= C["stakes"] - 0.2:                                             # stakes: what the mistakes land on now
        tt = twos(T)
        icons = ((230, "plane"), (420, "bolt"), (610, "cross"), (800, "missile"))
        for i, (x, kind) in enumerate(icons):
            k = kk.pop(T, C["stakes"] - 0.2 + i * 0.15, 0.2, 0.25)
            if k <= 0:
                continue
            c.save()
            c.translate(x, 790)
            c.scale(k * 0.62, k * 0.62)
            _icon(c, kind, tt, i)
            c.restore()
    if T >= C["smaller"]:
        sq = 1 - 0.8 * ease(ramp(T, C["smaller"], C["smaller"] + 1.2))
        kit.clay_x(c, 540, 1180, 0.5 * sq + 0.05, T, seed=5)
    return st.arr


def _icon(c, kind, tt, seed):
    """Little clay icons for the high stakes (drawn around 0,0, ~140 px across)."""
    if kind == "plane":
        kk.clay_path(c, cast._capsule(-80, 0, 80, 0, 26), (230, 230, 240), tt, seed + 1, prints=1, marks=1)
        kk.clay_poly(c, [(-20, -5), (30, -5), (-10, -80), (-35, -80)], (200, 200, 215), tt, seed + 2, amp=3, prints=0)
        kk.clay_poly(c, [(-20, 5), (30, 5), (-10, 80), (-35, 80)], (200, 200, 215), tt, seed + 3, amp=3, prints=0)
    elif kind == "bolt":
        kk.clay_poly(c, [(10, -90), (-50, 10), (-5, 10), (-25, 90), (50, -15), (5, -15)], (255, 210, 40), tt, seed + 4, amp=3)
    elif kind == "cross":
        kk.clay_poly(c, [(-24, -80), (24, -80), (24, 80), (-24, 80)], (230, 40, 50), tt, seed + 5, amp=3)
        kk.clay_poly(c, [(-80, -24), (80, -24), (80, 24), (-80, 24)], (230, 40, 50), tt, seed + 6, amp=3)
    else:
        kk.clay_path(c, cast._capsule(-70, 40, 70, -40, 22), (150, 160, 120), tt, seed + 7, prints=1, marks=1)
        kk.clay_ellipse(c, 70, -40, 26, 26, (230, 60, 40), tt, seed + 8, prints=0)


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
        dx, hop, tl = cast.moves(twos(T) - S("s4"), b, i % 2, 0.8)
        cast.corpse(c, 250 + i * 290 + dx, 1300, 0.45, T, pose=cast.dance_pose(T - S("s4"), b, "show", i), seed=40 + i, hop=hop, tilt=tl)
    for i, (who, x) in enumerate((("grandpa", 140), ("papa", 380), ("mama", 700), ("girl", 940))):
        dx, hop, tl = cast.moves(T - S("s4"), b, 0, 0.7)                  # the kick line moves as one
        cast.person(c, who, x + dx * 0.5, 1650, 0.5, T, pose=cast.dance_pose(T - S("s4"), b, "show", i), bob=hop, tilt=tl,
                    mood="smile" if i == 2 else "flat")
    kit.confetti(c, T, 60, t0=S("s4"))
    return st.arr


def s_finale_b(T, t, d):
    """The meadow moment, close: she spins round and round, arms out - face, back, face - and the camera whips round
    with her, the mountains, the rainbow and the flowers streaming past."""
    st = kk.Stage()
    c = st.c
    img = bg.meadow(3)
    ang = t * 5.2
    off = (t * 1900) % 2160                                             # the world wheels past: meadow | mirror | meadow
    c.drawImage(img, -off, 0)
    c.save()
    c.translate(2160 - off, 0)
    c.scale(-1, 1)
    c.drawImage(img, 0, 0)
    c.restore()
    c.drawImage(img, 2160 - off, 0)
    rgb = st.arr[..., :3].astype(np.float32)                              # the whip-pan smear
    k = 41
    cs = np.cumsum(np.pad(rgb, ((0, 0), (k // 2 + 1, k // 2), (0, 0)), mode="edge"), axis=1)
    st.arr[..., :3] = ((cs[:, k:] - cs[:, :-k]) / k).astype(np.uint8)
    rng = np.random.default_rng(3)
    for i in range(26):                                                  # petals streaming past the lens
        x = (rng.uniform(0, 2400) - t * rng.uniform(1600, 2600)) % 1300 - 110
        y = rng.uniform(300, 1300)
        c.drawOval(skia.Rect.MakeXYWH(x, y, 36, 14), paint([PINK, WHITE, LEMON, HOT][i % 4], 0.85))
    cs_ = math.cos(ang)
    for k2 in range(3):                                                  # swoosh arcs around her
        a0 = math.degrees(ang) % 360 + k2 * 120
        r = 470 + k2 * 40
        c.drawArc(skia.Rect.MakeLTRB(540 - r, 1180 - r * 0.3, 540 + r, 1180 + r * 0.3), a0, 80, False, paint(WHITE, 0.75, stroke=10))
    cast.person(c, "girl", 540, 1960 + 12 * math.sin(ang * 2), 1.3, T, pose=(96 + 6 * math.sin(ang), 0, 96 - 6 * math.sin(ang), 0),
                spin=max(0.62, abs(cs_)), back=cs_ < 0, mood="smile")
    for i in range(6):
        a = i * math.pi / 3 + t * 3.0
        kk.cg_star(c, 540 + 470 * math.cos(a), 760 + 170 * math.sin(a), 34, T, seed=i, color=[LEMON, HOT, WHITE, MINT][i % 4])
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
    """Somewhere in the next billion decisions is yours: a mountain of guestbooks, open at the line with your name,
    and behind it, rising, the little error - not so little now."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.storm())
    bg.volcano(c, 820, 1250, 1.1, glow=1.0)
    rise = ease(ramp(twos(T), T - t + 0.1, T - t + 1.6))
    cast.creature(c, 540, 1380 - 480 * rise, 2.8, T, mood="open", look=(0.0, 0.5))
    for row in range(8):                                                # the mountain of guestbooks
        y = 1520 - row * 58
        n = 8 - row
        w = 118
        for i in range(n):
            x = 540 + (i - (n - 1) / 2) * w
            col = [(170, 30, 50), (40, 90, 170), (200, 120, 40)][(row + i) % 3]
            kk.clay_poly(c, [(x - 56, y), (x - 56, y - 50), (x + 56, y - 50), (x + 56, y)], col, twos(T), seed=150 + row * 9 + i,
                         amp=3, prints=0, marks=1)
            c.drawRect(skia.Rect.MakeLTRB(x - 56, y - 47, x + 56, y - 38), paint((235, 200, 90), 0.9))   # gilt spine bands
            c.drawRect(skia.Rect.MakeLTRB(x - 56, y - 12, x + 56, y - 4), paint((235, 200, 90), 0.9))
            c.drawRect(skia.Rect.MakeLTRB(x - 26, y - 33, x + 26, y - 17), paint(CREAM, 0.95))            # the spine label
            c.drawLine(x - 18, y - 25, x + 18, y - 25, paint(kk.mix(col, INK, 0.3), stroke=3))
    cast.guestbook(c, 540, 950, 0.9, T, marks=16, rot=-4, you=True)
    cast.crow(c, 860, 760, 0.55, T, caw=1.0 if t > 1.0 else 0.0, flip=True)
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

"""Scenes 3: 99.9% in love (the floating dream duet), the volcano of a million failures, the garden disco."""
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


def cg_heart(c, x, y, s, t, color=HOT, a=1.0):
    """A glossy plastic 3D heart, turning."""
    sx = 0.75 + 0.25 * math.cos(t * 2.5)
    c.save()
    c.translate(x, y)
    c.scale(s * sx, s)
    p = skia.Path()
    p.moveTo(0, 60)
    p.cubicTo(-110, -10, -50, -90, 0, -35)
    p.cubicTo(50, -90, 110, -10, 0, 60)
    c.save()
    c.translate(8, 8)
    c.drawPath(p, paint(kk.mix(color, INK, 0.5), a))
    c.restore()
    c.drawPath(p, paint(shader=kk.lin((-80, -80), (80, 60), [kk.mix(color, WHITE, 0.6), color, kk.mix(color, INK, 0.2)]), a=a))
    c.drawOval(skia.Rect.MakeLTRB(-60, -55, -25, -30), paint(WHITE, 0.85 * a))
    c.restore()


def dreamy(arr, k=0.5):
    """The dream glow: the picture melted into its own blur."""
    bl = kk.blur_small(arr, 5).astype(np.float32)
    rgb = arr[..., :3].astype(np.float32)
    arr[..., :3] = np.clip(rgb * (1 - 0.45 * k) + bl * 0.45 * k + np.clip(bl - 160, 0, 255) * 0.4 * k, 0, 255).astype(np.uint8)


def s_duet(T, t, d):
    """Mama and the machine, floating, slow-dancing in a candy-floss sky."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.dream())
    ang = t * 0.5
    for i in range(10):
        hy = (1500 - ((t * 140 + i * 180) % 1500)) + 200
        cg_heart(c, 90 + (i * 197) % 900, hy, 0.5 + 0.25 * (i % 3), T + i, color=[HOT, PINK, (255, 80, 120)][i % 3])
    mx, my = 300 + 40 * math.sin(T * 0.9), 1120 + 60 * math.sin(T * 1.3)
    cx, cy = 745 - 35 * math.sin(T * 0.9), 1060 + 60 * math.sin(T * 1.3 + 1.5)
    cast.machine(c, cx, cy + 300, 0.62, T, face="smile")
    cast.person(c, "mama", mx, my + 330, 0.62, T, pose=(60, 40, 110, 30), mood="smile", tilt=8 * math.sin(T))
    for i in range(5):
        kk.cg_star(c, 120 + i * 210, 330 + 50 * math.sin(T * 1.4 + i), 34, T, seed=i, color=[LEMON, WHITE, PINK][i % 3])
    dreamy(st.arr, 0.6)
    return st.arr


def _volcano(c, T, erupt, x=540, y=1500, s=1.25):
    tt = twos(T)
    bx, by, _ = kk.boil(T, 4 + 10 * erupt, 21)
    x, y = x + bx, y + by
    kk.clay_poly(c, [(x - 520 * s, y), (x - 110 * s, y - 640 * s), (x + 110 * s, y - 650 * s), (x + 540 * s, y)], (130, 105, 120),
                 tt, seed=40, amp=14, prints=3, marks=5)
    kk.clay_ellipse(c, x, y - 640 * s, 120 * s, 34 * s, (255, 90, 30) if erupt > 0 else (90, 60, 70), tt, seed=41, amp=0.06)
    if erupt > 0:
        for k in range(5):                                              # lava running down the sides
            L = 540 * s * min(1.0, erupt * (0.6 + 0.2 * k))
            xk = x - 90 * s + k * 45 * s
            dx = (k - 2) * 90 * s
            kk.clay_path(c, _run(xk, y - 630 * s, xk + dx, y - 630 * s + L, 22 + 6 * (k % 2)), (255, 70 + k * 15, 20), tt, seed=50 + k,
                         prints=0, marks=1, gloss=0.4)


def _run(x0, y0, x1, y1, w):
    import cast as _c
    return _c._capsule(x0, y0, x1, y1, w)


def s_volcano(T, t, d):
    """Dead silence; the volcano waits. On 'billion' it blows: clay lava and red Xs, a million of them."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.storm())
    erupt = ramp(T, C["billion"] - 0.1, C["billion"] + 1.2)
    _volcano(c, T, erupt)
    if erupt > 0:
        tt = twos(T) - (C["billion"] - 0.1)
        rng = np.random.default_rng(4)
        for i in range(60):
            age = tt - i * 0.06
            if age < 0:
                continue
            ang = rng.uniform(-2.6, -0.5)
            sp = rng.uniform(900, 1600)
            px = 540 + math.cos(ang) * sp * age
            py = 690 + math.sin(ang) * sp * age + 1300 * age * age
            if py > H + 100:
                continue
            if i % 3 == 0:
                kit.clay_x(c, px, py, 0.28, T, seed=i)
            else:
                kk.clay_ellipse(c, px, py, 30, 26, (255, 90 + (i * 7) % 90, 20), twos(T), seed=i, prints=0, marks=0, gloss=0.4)
    if T >= C["onemil"] - 0.1:
        ov.slam(c, "1,000,000", 540, 470, 140, T, C["onemil"] - 0.1, color=(255, 80, 60), edge=INK,
                sub="FAILURES" if T >= C["failures"] - 0.2 else None)
    elif T >= Wd("e1", "Point") - 0.1:
        ov.slam(c, "× 0.1%", 540, 470, 150, T, Wd("e1", "Point") - 0.1, color=WHITE, edge=BLOOD)
    elif T >= C["billion"] - 0.1:
        ov.slam(c, "1,000,000,000", 540, 470, 120, T, C["billion"] - 0.1, color=LEMON, edge=HOT, sub="DECISIONS")
    kk.red(st.arr, 0.15 + 0.35 * erupt)
    return st.arr


# ------------------------------------------------------------------ the garden disco (the macabre number)

def _floor(c, T, beat):
    """Disco floor lights set into the lawn, flashing on the beat."""
    n = int(T / beat)
    for row in range(6):
        y0 = 1420 + row * 90
        w = 110 + row * 22
        for i in range(-1, 11):
            x = 540 + (i - 4.5) * w
            on = (i + row + n) % 3 == 0
            cc = [HOT, LEMON, SKY, MINT, LILAC, ORANGE][(i + row * 2 + n) % 6]
            c.drawRect(skia.Rect.MakeLTRB(x - w / 2 + 4, y0 + 4, x + w / 2 - 4, y0 + 86), paint(cc, 0.85 if on else 0.18))


def _disco_set(st, T):
    c = st.c
    kit.backdrop(st, bg.garden_night())
    beat = TL.songs["s3"]["beat"]
    _floor(c, T - S("s3"), beat)
    for i, (x0, col) in enumerate(((180, HOT), (540, SKY), (900, LEMON))):
        sw = math.sin(T * 1.7 + i * 2)
        kit.spotlight(c, x0, 0, x0 + 360 * sw, 1500, 170, col, 0.22)
    drop = ease(ramp(T, S("s3"), S("s3") + 1.2))
    kit.mirrorball(c, 540, -120 + 400 * drop, 110, T)
    return beat


def s_disco_a(T, t, d):
    """The graves crack; the dead climb out, on the beat."""
    st = kk.Stage()
    c = st.c
    beat = _disco_set(st, T)
    for i in range(4):
        x = 170 + i * 250
        rise = ease(ramp(twos(T), S("s3") + 0.4 + i * 0.5, S("s3") + 1.6 + i * 0.5))
        cast.tombstone(c, x, 1180, 0.55, T, n=[1, 2_000_417, 5_310_882, 9_999_999][i], seed=i)
        cast.corpse(c, x, 1400, 0.62, T, pose=(160, 10, 160, 10) if rise < 1 else cast.dance_pose(T, beat, "disco", i),
                    rise=rise, seed=i, clip_y=1405)
        kk.clay_ellipse(c, x, 1405, 110, 22, (70, 50, 40), twos(T), seed=60 + i, prints=0, marks=2)
    return st.arr


def s_disco_b(T, t, d):
    """In formation: the dead do the disco point, rows of them."""
    st = kk.Stage()
    c = st.c
    beat = _disco_set(st, T)
    for row in range(2, -1, -1):
        s = 0.42 + row * 0.12
        y = 1180 + row * 170
        for i in range(4 + (2 - row)):
            n = 4 + (2 - row)
            x = 540 + (i - (n - 1) / 2) * (230 - row * 20) * (1 + (2 - row) * 0.1)
            cast.corpse(c, x, y, s, T, pose=cast.dance_pose(T - S("s3"), beat, "disco", (i + row) % 2), seed=row * 7 + i)
    return st.arr


def s_disco_c(T, t, d):
    """Dig them a grave by the garden wall: the family digs, on the beat, deadpan, while the dead dance behind them."""
    st = kk.Stage()
    c = st.c
    beat = _disco_set(st, T)
    for i in range(5):
        cast.corpse(c, 120 + i * 210, 1180, 0.45, T, pose=cast.dance_pose(T - S("s3"), beat, "disco", i % 2), seed=i + 20)
    ph = ((T - S("s3")) / beat) % 1.0
    dig = abs(math.sin(ph * math.pi))
    for i, (who, x) in enumerate((("grandpa", 200), ("papa", 540), ("girl", 880))):
        hand = cast.person(c, who, x, 1660, 0.5, T, pose=(40, 60, 70 - 35 * dig, 60), bob=18 * dig, mood="flat")
        if hand:
            cast.shovel(c, hand[0], hand[1], 0.62, ang=-25 + 30 * dig)
    return st.arr


def s_disco_d(T, t, d):
    """Everyone - the dead, the family, the little error - dancing the same step. Confetti."""
    st = kk.Stage()
    c = st.c
    beat = _disco_set(st, T)
    for i in range(6):
        cast.corpse(c, 90 + i * 180, 1200, 0.44, T, pose=cast.dance_pose(T - S("s3"), beat, "disco", i % 2), seed=i + 30)
    for i, (who, x) in enumerate((("grandpa", 150), ("papa", 380), ("mama", 700), ("girl", 930))):
        cast.person(c, who, x, 1640, 0.46, T, pose=cast.dance_pose(T - S("s3"), beat, "disco", i % 2), mood="flat")
    cast.creature(c, 540, 1260, 0.7, T, mood="grin")
    kit.confetti(c, T, 80, t0=T - t)
    return st.arr

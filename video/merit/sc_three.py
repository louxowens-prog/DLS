"""Chapter III - THE MULTITUDE (magenta).

m_manager - one man at one desk under one lamp, stamping a few people a day.
m_army    - the Clerks in rows to the horizon, stamping as one, glimpsed through smoke and strobes; paper falls like snow.
m_nist    - a standing stone in the fog, NIST's warning cut into it; SPEED and SCALE burn as she says them.
m_kaleido - her face multiplied in a turning kaleidoscope: "Why judge one, when I can judge them all?" """
import math

import numpy as np
import skia

import gel as G
import kit as K
import look as LK
import pface as PF
import people as P
import world as Wd
from common import E, S, Wx, hit, talk
from edit import cut, end
from kit import H, W, BLACK, WHITE, mix, paint, ramp


def _silhouette(c, x, y, s, col=(10, 4, 10), a=1.0):
    """A person waiting, seen from behind: head, shoulders, a coat."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawPath(K.smooth([(-90, 0), (-100, -300), (-70, -440), (-30, -480), (30, -480), (70, -440), (100, -300), (90, 0)]), paint(col, a))
    c.drawCircle(0, -540, 62, paint(col, a))
    c.restore()


def s_m_manager(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("m_manager")
    c.drawPaint(paint((14, 4, 12)))
    z = 1.0 + 0.03 * (T - t0)
    c.save()
    c.translate(540, 1000)
    c.scale(z, z)
    c.translate(-540, -1000)
    # a desk lamp to one side, its pool on the desk
    G.pool(c, 560, 1180, 560, (255, 180, 210), 0.42)
    c.drawPath(K.path([(250, 760), (390, 760), (350, 690), (290, 690)]), paint((30, 70, 50)))
    c.drawLine(320, 760, 320, 1180, paint((60, 50, 40), stroke=8))
    G.beam(c, (320, 760), (150, 1250), (700, 1250), (255, 200, 230), a=0.25)
    # the manager: a man in a suit, his face in the lamplight, one stamp in his hand
    PF.pface(c, 600, 900, 0.62, "m_b", T, key=(255, 210, 220), fill=(120, 60, 120), key_at=(-0.9, 0.2), amb=(18, 6, 14), neck=True)
    c.drawPath(K.smooth([(380, 1300), (400, 1120), (480, 1080), (720, 1080), (800, 1120), (820, 1300)]), paint((26, 14, 22)))
    c.drawPath(K.path([(570, 1090), (630, 1090), (610, 1200), (590, 1200)]), paint((150, 30, 60)))
    # the desk
    c.drawPath(K.path([(150, 1180), (1000, 1180), (1060, 1300), (90, 1300)]), paint((40, 20, 30)))
    c.drawRect(skia.Rect.MakeLTRB(90, 1300, 1060, 1800), paint((20, 8, 16)))
    ph = ((T - t0) % 1.3) / 1.3                                   # a slow stamp: up... and down
    sy = 1170 - 170 * math.sin(math.pi * min(1.0, ph / 0.75)) if ph < 0.75 else 1170
    c.drawRoundRect(skia.Rect.MakeLTRB(700, sy - 60, 800, sy), 10, 10, paint((90, 50, 50)))
    c.drawRect(skia.Rect.MakeLTRB(735, sy - 140, 765, sy - 60), paint((110, 70, 70)))
    c.drawCircle(750, sy - 150, 24, paint((110, 70, 70)))
    c.drawPath(K.capsule(720, 1110, 750, sy - 120, 70, 50), paint((26, 14, 22)))
    rng = K.rng_at(2, 2)
    for k in range(int(2 + (T - t0) / 1.3)):                     # the pile of the day's refusals
        c.drawRect(skia.Rect.MakeXYWH(840 + rng.uniform(-8, 8), 1170 - k * 10, 140, 9), paint((210, 190, 200)))
    c.restore()
    # a small queue waiting before the desk
    for k in range(3):
        _silhouette(c, 150 + k * 120, 1660 + k * 30, 0.95 - 0.08 * k, col=(5, 2, 5))
    K.text(c, "A FEW A DAY", 540, 340, 60, "newrocker-400", (255, 220, 240), tag="label", outline=(30, 0, 20), ow=8,
           a=K.ease(ramp(T, t0 + 0.4, t0 + 1.0)))
    return st.arr


def _mini_clerk(c, x, y, s, slit=1.0, arm=0.0, strobe=0.0, back=False, light=(200, 90, 220)):
    """A distant Clerk: robe, hood, a pewter mask, the slit, the stamp arm - modelled with light from above and the
    front so it has weight, cheap enough to draw by the hundred. back=True: a silhouette against a strobe flash."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    robe = K.smooth([(-150, 900), (-140, 120), (-100, -20), (100, -20), (140, 120), (150, 900)])
    hood = K.smooth([(-110, 40), (-120, -150), (-60, -260), (60, -260), (120, -150), (110, 40)])
    if back:
        c.drawPath(robe, paint((6, 2, 8)))
        c.drawPath(hood, paint((6, 2, 8)))
        rim = paint(mix(light, WHITE, 0.5), 0.9, stroke=10, blur=4)
        rim.setBlendMode(skia.BlendMode.kPlus)
        c.drawPath(hood, rim)
        c.drawRect(skia.Rect.MakeLTRB(-64, -134, 64, -108), G.glow_paint((255, 60, 60), slit))
    else:
        lit = 0.35 + 0.65 * strobe
        top, bot = mix((14, 10, 18), light, 0.55 * lit), (8, 4, 10)
        c.drawPath(robe, paint(shader=K.lin((0, -20), (0, 700), [top, bot])))
        for k in (-1, 1):                                            # the folds of the robe
            c.drawPath(K.bez_path([(k * 60, 60), (k * 76, 400), (k * 70, 900)]), paint((0, 0, 0), 0.5, stroke=16, blur=8))
            c.drawPath(K.bez_path([(k * 20, 80), (k * 26, 400), (k * 18, 900)]), paint(mix(top, WHITE, 0.15), 0.3, stroke=8, blur=6))
        for k in (-1, 1):                                            # pauldrons
            c.drawOval(skia.Rect.MakeLTRB(k * 140 - 70, -10, k * 140 + 70, 70), paint(shader=K.rad((k * 120, 0), 90, [mix((120, 110, 130), light, 0.4 * lit), (20, 16, 24)])))
        c.drawPath(hood, paint(shader=K.rad((0, -200), 300, [mix((40, 30, 46), light, 0.5 * lit), (8, 4, 10)])))
        c.drawOval(skia.Rect.MakeLTRB(-70, -200, 70, 10), paint(shader=K.rad((-20, -150), 150, [mix((200, 192, 210), light, 0.3), (60, 54, 70), (20, 16, 24)], [0, 0.6, 1])))
        for k in range(4):                                           # the grille
            c.drawLine(-36, -70 + k * 16, 36, -70 + k * 16, paint((10, 6, 12), 0.8, stroke=5))
        c.drawRect(skia.Rect.MakeLTRB(-64, -134, 64, -108), paint((10, 4, 8)))
        c.drawRect(skia.Rect.MakeLTRB(-60, -130, 60, -112), G.glow_paint((255, 50, 60), slit))
        G.pool(c, 0, -120, 160, (255, 40, 60), 0.3 * slit, squash=0.3)
    ay = -60 - 380 * arm
    c.drawLine(-120, 60, -170, ay + 120, paint((26, 20, 30) if not back else (6, 2, 8), stroke=60))
    c.drawRect(skia.Rect.MakeLTRB(-250, ay, -90, ay + 90), paint((70, 40, 32) if not back else (6, 2, 8)))
    if strobe > 0 and not back:                                       # the strobe catches the hood and the shoulders
        rim = paint((255, 190, 255), 0.6 * strobe, stroke=10, blur=5)
        rim.setBlendMode(skia.BlendMode.kPlus)
        c.drawPath(hood, rim)
        c.drawPath(K.bez_path([(-150, 600), (-148, 200), (-100, -10)]), rim)
        c.drawPath(K.bez_path([(150, 600), (148, 200), (100, -10)]), rim)
    c.restore()


def s_m_army(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("m_army")
    c.drawPaint(paint((10, 2, 10)))
    ph = (idx // 2) % 3                                            # the strobe: a flash behind them every few frames
    flash = ph == 0 and T > Wx("m1", "An") - 0.05
    strobe = 1.0 if ph == 1 else 0.15
    if flash:
        c.drawPaint(paint((255, 170, 245)))
        G.pool(c, 540, 500, 1400, (255, 255, 255), 0.8)
    else:
        G.pool(c, 540, 500, 1400, (255, 60, 200), 0.35 * (0.4 + 0.6 * strobe))
    rise = 160 * K.ease(ramp(T, t0, t0 + 2.4))
    beat = (T - t0) * 3.0
    hor = 520 + rise * 0.3
    for r in range(8, -1, -1):                                    # rows from the horizon toward us
        z = 0.55 + r * 0.75
        s_ = 0.95 / z
        y = hor + 1250 / z - rise / z
        n = int(3 + r * 1.4)
        span = W * (1.15 + r * 0.3)
        arm = 0.5 + 0.5 * math.cos(beat * math.pi + r * 0.15)
        for q in range(n):
            x = W / 2 + (q - (n - 1) / 2) * span / n + (r % 2) * span / n / 2
            _mini_clerk(c, x, y, s_, arm=arm, strobe=strobe, back=flash)
        G.fog(c, T, -100, y - 220 * s_, W + 100, y + 160 * s_, (200, 100, 220), a=0.16 if not flash else 0.3, n=4, seed=r)
    # refusals falling through the strobe, like ash
    rng = K.rng_at(9, 9)
    for i in range(36):
        x = (rng.uniform(0, W) + 30 * math.sin(T + i)) % W
        y = (rng.uniform(0, H) + (T - t0) * rng.uniform(80, 180)) % H
        c.save()
        c.translate(x, y)
        c.rotate(T * rng.uniform(-60, 60) + i * 20)
        c.drawRect(skia.Rect.MakeLTRB(-26, -34, 26, 34), paint((150, 120, 150), 0.55))
        c.drawRect(skia.Rect.MakeLTRB(-18, -10, 18, 4), paint((200, 30, 60), 0.6))
        c.restore()
    K.text(c, "MILLIONS", 540, 360, 110, "newrocker-400", (255, 230, 250), tag="label", outline=(40, 0, 30), ow=12,
           a=K.ease(ramp(T, Wx("m1", "millions.") - 0.15, Wx("m1", "millions.") + 0.2)))
    return st.arr


def s_m_nist(T, idx):
    st = K.Stage((0, 0, 0))
    t0 = cut("m_nist")
    _nist(st.c, T, t0, 1.0 + 0.03 * (T - t0), 900, 900)
    return st.arr


def s_m_speed(T, idx):
    """Close on the stone: THE SPEED AND SCALE, burning red, the camera still pushing in."""
    st = K.Stage((0, 0, 0))
    t0 = cut("m_speed")
    _nist(st.c, T, cut("m_nist"), 1.5 + 0.06 * (T - t0), 990, 900, close=True)
    return st.arr


def _nist(c, T, t0, z, cy, sy, close=False):
    c.save()
    c.translate(540, sy)
    c.scale(z, z)
    c.translate(-540, -cy)
    Wd.forest(c, T, cam_y=200, moon_r=230, moon_xy=(860, 330), stars=0.5, seed=2, moon_a=0.7)
    # the Clerks marching past behind, faint in the fog
    for q in range(9):
        x = ((q * 150 + (T - t0) * 60) % 1400) - 160
        _mini_clerk(c, x, 1250, 0.45, arm=0.0, strobe=0.3)
    G.fog(c, T, -100, 1000, 1180, 1500, (220, 120, 240), a=0.35, n=8, seed=3)
    # the stone
    stone = K.smooth([(160, 1360), (150, 560), (200, 330), (540, 260), (880, 330), (930, 560), (920, 1360)])
    Wd.stone_fill(c, stone, base=(62, 54, 64), light=(255, 140, 210), light_from=(0.2, 0.0), k=0.5)
    k1 = K.ease(ramp(T, t0 + 0.2, t0 + 0.8))
    if not close:
        Wd.engraved(c, "NIST", 540, 450, 96, "cinzel-800", glow=0.9 * k1, a=k1, color=(255, 236, 246))
        Wd.engraved(c, "AI RISK MANAGEMENT FRAMEWORK", 540, 530, 34, "cinzel-800", a=k1, glow=0.7 * k1, color=(255, 220, 240))
        Wd.engraved(c, "1.0  ·  2023", 540, 580, 34, "cinzel-800", a=k1, glow=0.7 * k1, color=(255, 220, 240))
        c.drawLine(300, 625, 780, 625, paint((20, 10, 16), 0.8 * k1, stroke=4))
    k2 = K.ease(ramp(T, Wx("m2", "warns") - 0.2, Wx("m2", "warns") + 0.4))
    ks = K.ease(ramp(T, Wx("m2", "speed") - 0.15, Wx("m2", "speed") + 0.25))
    kc = K.ease(ramp(T, Wx("m2", "scale") - 0.15, Wx("m2", "scale") + 0.25))
    for i, ln in enumerate(("“AI SYSTEMS CAN", "POTENTIALLY INCREASE")):
        if not close:
            Wd.engraved(c, ln, 540, 720 + i * 70, 52, "cinzel-800", a=k2, glow=1.0 * k2, color=(255, 244, 250))
    Wd.engraved(c, "THE SPEED", 540, 900, 76, "cinzel-800", a=k2, glow=0.5 + 0.5 * ks, color=mix((255, 220, 236), (255, 70, 70), ks))
    Wd.engraved(c, "AND SCALE", 540, 990, 76, "cinzel-800", a=k2, glow=0.5 + 0.5 * kc, color=mix((255, 220, 236), (255, 70, 70), kc))
    Wd.engraved(c, "OF BIASES”", 540, 1070, 52, "cinzel-800", a=k2, glow=1.0 * k2, color=(255, 244, 250))
    Wd.engraved(c, "§ 3.7", 540, 1150, 32, "cinzel-800", a=k2, glow=0.6 * k2, color=(255, 220, 240))
    if ks > 0:
        LK.flare(540 if z < 1.5 else 540, 880 if z < 1.5 else sy + (880 - cy) * z, 0.35 * ks * (1 - kc * 0.5), (255, 120, 120))
    c.restore()


_MSURF = {}


def _merit_tile(T):
    """Her face rendered once per frame into a square tile, for the kaleidoscope."""
    st = K.Stage((0, 0, 0))
    c = st.c
    c.drawPaint(paint((20, 4, 20)))
    G.pool(c, 540, 960, 900, (255, 60, 200), 0.3)
    P.merit(c, 540, 900, 1.5, T, eyes=1.0, talk=talk(T, "merit"), smile=0.35, rays=1.0, crown=1.0, mantle=0.8,
            L=(255, 100, 200), R=(140, 70, 255))
    return K.image(st.arr)


def s_m_kaleido(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("m_kaleido")
    img = _merit_tile(T)
    n = 8
    rot = (T - t0) * 14
    grow = K.ease(ramp(T, t0, t0 + 1.2))
    cx, cy = 540, 900
    for k in range(n):
        c.save()
        c.translate(cx, cy)
        c.rotate(rot + k * 360 / n)
        wedge = skia.Path()
        R = 1500
        a0, a1 = -math.pi / n, math.pi / n
        wedge.moveTo(0, 0)
        wedge.lineTo(math.cos(a0) * R, math.sin(a0) * R)
        wedge.lineTo(math.cos(a1) * R, math.sin(a1) * R)
        wedge.close()
        c.clipPath(wedge, doAntiAlias=True)
        if k % 2:
            c.scale(1, -1)                                         # mirror every other wedge
        sc = 0.55 + 0.25 * grow
        c.rotate(-90)
        c.scale(sc, sc)
        c.translate(-540, -760 + 120 * math.sin(T * 0.8))
        p = skia.Paint()
        c.drawImage(img, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear), p)
        c.restore()
    # her whole face over the centre, fading in as she asks
    k = K.ease(ramp(T, S("m4") - 0.1, S("m4") + 0.6))
    with K.layer(c, 0.75 * k, skia.BlendMode.kScreen):
        P.merit(c, 540, 900, 0.9, T, eyes=1.0, talk=talk(T, "merit"), smile=0.35, rays=0.0, crown=1.0, mantle=0.0, hair=0.6,
                L=(255, 120, 220), R=(150, 80, 255))
    LK.flare(540, 900 - 150 * 0.9, 0.4 * k, (255, 120, 220))
    return st.arr

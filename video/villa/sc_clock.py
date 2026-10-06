"""Inside the clock, the hall of mirrors, and the locked door: a passed programming course and a mechanism she cannot
fix; two brass gauges (50% with AI, 67% by hand); a beetle in the gears - debugging; a falling graduate; mirrors that
show what a degree is worth; the present day showing through; the key, the door, the white."""
import math

import numpy as np
import skia

import cast as CA
import gel as G
import kit as K
import pers as P
import props as PR
import sets as SE
from common import E, Layers, S, Wx, blink, hit, shake, talk, zoom
from edit import cut, end
from kit import AMBER, BLACK, COBALT, EMERALD, GOLD, INK, MAGENTA, PAPER, WHITE, H, W, mix, paint, ramp

CODE = ["if", "{", "for", "}", ";", "( )", "=", "return", "[ ]", "&&", "else", "//"]


def _mechanism(c, T, speed=1.0, jam=0.0, seed=0):
    """The works of the great clock: brass gears of every size turning in gel light, code engraved on their rims."""
    st = 1.0 - jam
    jit = (math.sin(T * 60) * 1.5 * jam) if jam > 0 else 0.0
    gears = [(150, 420, 230, 30, 1), (520, 300, 150, 20, -1.5), (860, 520, 260, 34, 0.87), (300, 860, 180, 24, -1.25),
             (720, 960, 300, 40, 0.75), (180, 1300, 260, 34, 0.87), (940, 1330, 150, 20, -1.5), (560, 1480, 200, 26, -1.15)]
    for i, (x, y, r, n, w) in enumerate(gears):
        ang = T * 22 * w * speed * st + i * 7 + jit
        col = mix((176, 132, 60), (120, 90, 50), (i % 3) / 3)
        PR.gear(c, x, y, r, n, ang, color=col, glyphs=CODE if r > 200 else None)
    G.pool(c, 200, 400, 600, EMERALD, 0.55)
    G.pool(c, 900, 1100, 640, AMBER, 0.6)
    G.pool(c, 540, 1600, 600, MAGENTA, 0.35)


def s_c_gears(T, idx):
    """You can pass a programming course and still not be able to program: inside the clock, a certificate of a
    passed course pinned to the works she cannot read; two gauges - 50% with AI, 67% by hand."""
    st = K.Stage((6, 4, 4))
    c = st.c
    t0 = cut("c_gears")
    zoom(c, T, t0, end("c_gears"), 1.0, 1.12, cx=540, cy=900)
    _mechanism(c, T)
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((0, 0, 0), 0.25))
    tt = Wx("c2", "trial")
    k_cert = 1 - K.ease(ramp(T, tt - 0.4, tt))
    if k_cert > 0:                                              # the certificate: course passed
        c.save()
        c.translate(540, 700)
        c.rotate(-4)
        c.drawRect(skia.Rect.MakeLTRB(-300, -200, 300, 200), paint(mix(PAPER, (255, 240, 210), 0.2), k_cert))
        c.drawRect(skia.Rect.MakeLTRB(-280, -180, 280, 180), paint(GOLD, k_cert, stroke=6))
        K.text(c, "CERTIFICATE", 0, -90, 50, "cinzel-800", INK, tag="plaque", a=k_cert)
        K.text(c, "PROGRAMMING", 0, -10, 46, "cinzel-600", INK, tag="plaque", a=k_cert)
        K.text(c, "PASSED", 0, 80, 62, "playfair-700", (190, 20, 30), tag="plaque", a=k_cert)
        c.drawCircle(200, 130, 40, paint((190, 30, 40), k_cert))
        c.restore()
        CA.walker_back(c, 540, 1580, 0.62, T, walking=False, key=(255, 160, 70), rim=(40, 220, 140), a=k_cert)
    if T > tt - 0.3:
        k = K.ease(ramp(T, tt - 0.3, tt + 0.2))
        v_ai = 50 * K.ease(ramp(T, Wx("c2", "fifty") - 0.4, Wx("c2", "fifty") + 0.2))
        v_hand = 67 * K.ease(ramp(T, Wx("c2", "Coding") - 0.1, Wx("c2", "sixty-seven") + 0.2))
        PR.gauge(c, 300, 760, 190, v_ai, "WITH AI", a=k)
        PR.gauge(c, 780, 760, 190, v_hand, "BY HAND", a=k)
    c.restore()
    return st.arr


def s_c_bug(T, idx):
    """The biggest gap? Debugging. A beetle caught in the teeth of a gear; the gear jerks against it."""
    st = K.Stage((4, 2, 2))
    c = st.c
    t0 = cut("c_bug")
    zoom(c, T, t0, end("c_bug"), 1.3, 1.6, cx=600, cy=760)
    jerk = 3 * math.sin(T * 40) * (math.sin(T * 7) > 0)
    PR.gear(c, 180, 1080, 520, 50, 14 + jerk, color=(170, 128, 58), glyphs=CODE)
    PR.gear(c, 940, 560, 420, 40, -9 - jerk, color=(150, 110, 50))
    G.pool(c, 600, 800, 420, EMERALD, 0.6)
    G.pool(c, 400, 1200, 520, AMBER, 0.45)
    # the beetle wedged where the teeth meet
    bx, by = 600, 820
    c.save()
    c.translate(bx, by)
    c.rotate(-30 + 4 * math.sin(T * 9))
    for k in range(3):
        for s in (-1, 1):
            a0 = math.radians(s * (40 + k * 40))
            leg = 70 + 8 * math.sin(T * 14 + k)
            c.drawLine(s * 10, -20 + k * 26, s * (14 + math.cos(a0) * leg), -20 + k * 26 + math.sin(abs(a0)) * 20, paint((20, 30, 14), stroke=6))
    c.drawOval(skia.Rect.MakeLTRB(-46, -70, 46, 90), paint((30, 60, 30)))
    c.drawOval(skia.Rect.MakeLTRB(-46, -70, 46, 90), paint(shader=K.rad((-14, -20), 90, [(140, 220, 120, 0.8), (40, 90, 40, 0.0)])))
    c.drawLine(0, -50, 0, 88, paint((10, 20, 10), stroke=3))
    c.drawOval(skia.Rect.MakeLTRB(-28, -110, 28, -62), paint((20, 40, 20)))
    for s in (-1, 1):
        c.drawLine(s * 12, -106, s * 40, -160, paint((20, 30, 14), stroke=4))
    c.restore()
    c.restore()
    k = K.ease(ramp(T, Wx("c2", "Debugging.") - 0.15, Wx("c2", "Debugging.") + 0.3))
    PR.plaque(c, 540, 330, ["DEBUGGING"], size=56, a=k, color=(120, 20, 24))
    return st.arr


def s_c_fix(T, idx):
    """Fix it, signorina. I... I can't. Clara before the stopped works, the Governess waiting above; the gears grind
    and seize."""
    st = K.Stage((4, 2, 4))
    c = st.c
    t0 = cut("c_fix")
    jam = K.ease(ramp(T, S("c4"), E("c4")))
    shake(c, T, 6 * jam * (T < E("c4") + 0.1), seed=4)
    zoom(c, T, t0, end("c_fix"), 1.0, 1.15, cx=540, cy=900)
    _mechanism(c, T, speed=1.0, jam=jam)
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((0, 0, 0), 0.35))
    CA.face(c, 820, 470, 0.7, "governess", T, L=(70, 100, 255), R=(255, 170, 70), core=0.4, expr="polite", talk=talk(T, "GOV"),
            blink=0.0, porc=0.5)
    CA.face(c, 470, 1020, 1.25, "clara", T, L=(255, 170, 70), R=(40, 220, 140), core=0.5, expr="fear" if T > S("c4") else "dread",
            talk=talk(T, "CLARA"), blink=blink(T, 6), porc=0.8, gaze=(0.3, -0.5))
    c.restore()
    c.restore()
    if T > E("c4") + 0.25:                                      # dead silence: the screen dims to almost nothing
        c.drawPaint(paint((0, 0, 0), 0.7 * ramp(T, E("c4") + 0.25, E("c4") + 0.45)))
    return st.arr


def s_c_scare(T, idx):
    """A porcelain graduate falls from the dark straight at the lens, its face splitting as it comes."""
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("c_scare")
    k = ramp(T, t0, t0 + 0.32)
    shake(c, T, 26 * hit(T, t0 + 0.28, 0.35), seed=8)
    G.pool(c, 540, 800, 900, (200, 10, 30), 0.8)
    z = 0.7 + 2.6 * k ** 2
    c.save()
    c.translate(540, 900)
    c.scale(z, z)
    c.rotate(-25 + 40 * k)
    c.translate(-540, -900)
    CA.face(c, 540, 900, 1.6, "doll", T, L=(255, 30, 60), R=(255, 120, 60), core=0.4, expr="scream", porc=1.0,
            crack=min(1.0, k * 1.2), cap=True)
    c.restore()
    c.restore()
    c.drawPaint(paint((255, 30, 40), 0.35 * hit(T, t0 + 0.28, 0.25)))
    return st.arr


def s_m_mirrors(T, idx):
    """Do this for years, and degrees stop meaning what they say. Even the honest ones. Clara in cap and gown between
    two mirrors: in one, a faceless dummy; in the other, the Governess - who is not in the room. Above them, framed
    diplomas whose ink fades to nothing, the honest one last."""
    st = K.Stage((2, 6, 4))
    c = st.c
    t0 = cut("m_mirrors")
    zoom(c, T, t0, end("m_mirrors"), 1.0, 1.08, cx=540, cy=900)

    def albedo(cc):
        cc.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((30, 90, 70)))
        for i in range(14):
            cc.drawLine(i * 80, 0, i * 80, H, paint((20, 60, 46), stroke=10))
        cc.drawRect(skia.Rect.MakeLTRB(0, 1500, W, H), paint((40, 30, 26)))

    def light(cc):
        G.pool(cc, 540, 700, 760, EMERALD, 0.8)
        G.pool(cc, 100, 1200, 500, MAGENTA, 0.6)
        G.pool(cc, 980, 1200, 500, (70, 100, 255), 0.6)
    SE.lit2d(c, albedo, light, amb=(12, 16, 14))
    # the diplomas above, fading
    fade0 = Wx("m1", "stop") - 0.2
    for i in range(4):
        x0 = 70 + i * 245
        fk = ramp(T, fade0 + i * 0.25, fade0 + i * 0.25 + 0.9) if i < 3 else ramp(T, Wx("m1", "honest") - 0.2, Wx("m1", "honest") + 0.6)
        c.drawRect(skia.Rect.MakeLTRB(x0, 270, x0 + 200, 420), paint(mix(PAPER, (255, 240, 210), 0.2)))
        PR.frame_gilt(c, x0, 270, x0 + 200, 420, t=12)
        K.text(c, "DIPLOMA", x0 + 100, 312, 26, "cinzel-800", INK, tag="deco", a=1 - fk)
        for k in range(3):
            c.drawRect(skia.Rect.MakeLTRB(x0 + 30, 335 + k * 18, x0 + 170, 340 + k * 18), paint(INK, 0.5 * (1 - fk)))
        c.drawCircle(x0 + 160, 395, 16, paint((190, 30, 40) if i < 3 else (210, 170, 60), 1 - fk * 0.9))
    if T > Wx("m1", "honest") - 0.2:                            # the honest one cracks across its glass
        k = ramp(T, Wx("m1", "honest"), Wx("m1", "honest") + 0.3)
        x0 = 70 + 3 * 245
        c.drawPath(K.path([(x0, 280), (x0 + 60, 330), (x0 + 110, 310), (x0 + 200, 400)], closed=False), paint(WHITE, 0.8 * k, stroke=3))
    # two tall oval mirrors
    for side in (-1, 1):
        mx = 540 + side * 330
        mir = K.oval(mx - 150, 560, mx + 150, 1260)
        c.drawPath(mir, paint((10, 14, 16)))
        c.save()
        c.clipPath(mir, doAntiAlias=True)
        G.pool(c, mx, 900, 300, (60, 90, 110), 0.5)
        if side < 0:
            CA.mannequin(c, mx, 1300, 0.62, T, pose=0, head=0.2, gown=True, cap=True, L=(120, 255, 190), R=(255, 80, 180))
        else:
            CA.face(c, mx, 860, 0.75, "governess", T, L=(255, 170, 70), R=(70, 100, 255), core=0.4, expr="polite", porc=0.5, blink=0.0)
        c.drawPath(K.path([(mx - 150, 560), (mx - 40, 560), (mx - 150, 760)]), paint(WHITE, 0.08))
        c.restore()
        PR.frame_gilt(c, mx - 150, 560, mx + 150, 1260, t=16)
    CA.face(c, 540, 930, 0.95, "clara", T, L=(255, 60, 170), R=(70, 100, 255), core=0.5, expr="blank", porc=0.9, cap=True,
            blink=0.0, gaze=(0.0, 0.0))
    c.restore()
    return st.arr


def s_m_super(T, idx):
    """So universities are bringing back handwritten exams, and employers face-to-face interviews: the present day
    shows through the glass - pens moving on paper in an exam hall; an interview table, an empty chair."""
    st = K.Stage((6, 6, 8))
    c = st.c
    t0 = cut("m_super")
    k_int = K.ease(ramp(T, Wx("m2", "employers") - 0.3, Wx("m2", "employers") + 0.4))
    # the exam hall, from above: pens on paper
    a1 = 1 - 0.85 * k_int
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((150, 150, 146), a1))
    for r in range(4):
        for k in range(2):
            x0, y0 = 90 + k * 470, 280 + r * 280
            c.drawRect(skia.Rect.MakeLTRB(x0, y0, x0 + 420, y0 + 240), paint((176, 140, 100), a1))
            c.drawRect(skia.Rect.MakeLTRB(x0 + 40, y0 + 30, x0 + 300, y0 + 210), paint((90, 120, 190), a1))
            c.drawRect(skia.Rect.MakeLTRB(x0 + 60, y0 + 50, x0 + 280, y0 + 190), paint((244, 244, 238), a1))
            n = int((T - t0) * 8 + r * 3 + k * 5) % 9
            for j in range(n):
                c.drawLine(x0 + 70, y0 + 66 + j * 14, x0 + 70 + 120 + 60 * math.sin(j + r), y0 + 66 + j * 14, paint((30, 40, 120), a1, stroke=3))
            px = x0 + 120 + 60 * math.sin(T * 3 + r + k) + 10 * n
            c.drawLine(px, y0 + 70 + n * 14, px + 70, y0 + 10 + n * 14, paint((20, 20, 30), a1, stroke=8))
            c.drawCircle(px + 70, y0 + 10 + n * 14, 22, paint((220, 180, 150), a1))
    K.text(c, "HANDWRITTEN EXAMS", 540, 290, 48, "jost-600", (30, 30, 36), tag="label", a=a1 * (1 - k_int))
    if k_int > 0:                                               # the interview room: two chairs across a table, one empty
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((214, 216, 212), k_int))
        c.drawRect(skia.Rect.MakeLTRB(0, 1180, W, H), paint((150, 150, 150), k_int))
        c.drawRect(skia.Rect.MakeLTRB(160, 900, 920, 940), paint((240, 240, 240), k_int))
        for x in (330, 750):
            CA.face(c, x, 640, 0.55, "int1" if x < 540 else "int2", T, L=(240, 240, 236), R=(220, 224, 230), core=0.0,
                    amb=(200, 200, 200), expr="neutral", a=k_int, blink=0.0)
        c.drawRect(skia.Rect.MakeLTRB(470, 1060, 610, 1300), paint((60, 60, 70), k_int))
        c.drawRect(skia.Rect.MakeLTRB(450, 1040, 630, 1080), paint((70, 70, 80), k_int))
        K.text(c, "FACE-TO-FACE INTERVIEWS", 540, 290, 46, "jost-600", (30, 30, 36), tag="label", a=k_int)
    return st.arr


def s_x_door(T, idx):
    """Your examination is waiting. A dark corridor; at its end a tall door, the Governess holding out a key on a black
    ribbon. The key turns; the door opens on a blinding white."""
    st = K.Stage()
    c = st.c
    t0 = cut("x_door")
    u = T - t0
    cam = P.Cam(pos=(0.0, 1.6, 0.6 * u), f=900)
    lights = [P.Light(((-1 if i % 2 == 0 else 1) * 1.5, 2.6, 2 + i * 2.6), [COBALT, MAGENTA][i % 2], 1.6, 1.8) for i in range(6)]
    SE.gallery(c, cam, T, length=14.0, width=3.4, height=5.0, lights=lights, end_door=False, wall=(60, 50, 90), seed=7)
    zd = 12.5
    dw = P.wall_z(zd, -1.7, 1.7, 0, 5.0)
    op = K.ease(ramp(T, E("x1") + 0.15, E("x1") + 0.9))
    with dw.draw(c, cam) as pc:
        if pc is not None:
            pc.drawPaint(paint((20, 14, 20)))
            pc.drawRect(skia.Rect.MakeLTRB(0.9 * P.U, 0.4 * P.U, 2.5 * P.U, 5.0 * P.U), paint((255, 255, 255)))
            pc.drawRect(skia.Rect.MakeLTRB(0.9 * P.U, 0.4 * P.U, 0.9 * P.U + 1.6 * P.U * (1 - op), 5.0 * P.U), paint((54, 30, 20)))
            pc.drawCircle(0.9 * P.U + 1.6 * P.U * (1 - op) - 18, 2.6 * P.U, 6, paint(GOLD))
    q = cam.proj((0.0, 2.2, zd))
    if q is not None and op > 0:
        G.pool(c, q[0], q[1], 400 + 1600 * op, (255, 255, 255), 0.9 * op)
    pos = (0.95, 0.0, zd - 0.6)
    gq = cam.proj((0.95, 1.65, zd - 0.6))
    if gq is not None:
        s = cam.scale_at(pos) / 900
        CA.face(c, gq[0], gq[1], s * 0.6, "governess", T, L=(255, 170, 70), R=(70, 100, 255), core=0.4, expr="polite",
                talk=talk(T, "GOV"), blink=0.0, porc=0.5)
        kx, ky = gq[0] - 160 * s, gq[1] + 520 * s
        c.drawLine(gq[0] - 40 * s, gq[1] + 300 * s, kx, ky, paint((10, 8, 10), stroke=max(2, 10 * s)))
        c.drawCircle(kx, ky + 30 * s, 26 * s, paint(GOLD, stroke=max(2, 8 * s)))
        c.drawLine(kx, ky + 56 * s, kx, ky + 140 * s, paint(GOLD, stroke=max(2, 10 * s)))
    cp = cam.proj((0.0, 0.0, cam.pos[2] + 2.6))
    CA.walker_back(c, cp[0], cp[1], cam.scale_at((0, 0, cam.pos[2] + 2.6)) * 1.72 / 900, T, coat=(20, 18, 24), key=(70, 100, 255),
                   rim=(255, 60, 170), walking=T < E("x1"))
    if T > E("x1") + 0.6:
        c.drawPaint(paint((255, 255, 255), K.ease(ramp(T, E("x1") + 0.6, E("x1") + 1.15))))
    return st.arr

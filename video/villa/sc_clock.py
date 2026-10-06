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
    passed course pinned to works she cannot read. Then the trial: close on one brass gauge as its needle drops to 50%
    (with AI); then both, side by side, as the other climbs to 67% (by hand)."""
    st = K.Stage((6, 4, 4))
    c = st.c
    t0 = cut("c_gears")
    tt = Wx("c2", "trial")
    t_ai = tt - 0.15
    t_both = Wx("c2", "Coding") - 0.15
    if T < t_ai:                                                # the certificate in the works
        zoom(c, T, t0, t_ai + 0.3, 1.0, 1.16, cx=540, cy=760)
        _mechanism(c, T)
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((0, 0, 0), 0.25))
        c.save()
        c.translate(540, 700)
        c.rotate(-4)
        c.drawRect(skia.Rect.MakeLTRB(-300, -200, 300, 200), paint(mix(PAPER, (255, 240, 210), 0.2)))
        c.drawRect(skia.Rect.MakeLTRB(-280, -180, 280, 180), paint(GOLD, stroke=6))
        K.text(c, "CERTIFICATE", 0, -90, 50, "cinzel-800", INK, tag="plaque")
        K.text(c, "PROGRAMMING", 0, -10, 46, "cinzel-600", INK, tag="plaque")
        K.text(c, "PASSED", 0, 80, 62, "playfair-700", (190, 20, 30), tag="plaque")
        c.drawCircle(200, 130, 40, paint((190, 30, 40)))
        c.restore()
        CA.walker_back(c, 540, 1580, 0.62, T, walking=False, key=(255, 160, 70), rim=(40, 220, 140))
        c.restore()
        return st.arr
    v_ai = 50 * K.ease(ramp(T, Wx("c2", "fifty") - 0.4, Wx("c2", "fifty") + 0.2))
    if T < t_both:                                              # one gauge, close: with AI
        zoom(c, T, t_ai, t_both + 0.2, 1.0, 1.12, cx=540, cy=800)
        _mechanism(c, T, seed=3)
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((0, 0, 0), 0.45))
        G.pool(c, 540, 780, 520, AMBER, 0.5)
        PR.gauge(c, 540, 760, 300, v_ai, "WITH AI")
        c.restore()
        return st.arr
    zoom(c, T, t_both, end("c_gears") + 0.2, 1.0, 1.1, cx=540, cy=840)
    _mechanism(c, T)
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((0, 0, 0), 0.35))
    v_hand = 67 * K.ease(ramp(T, Wx("c2", "Coding") - 0.1, Wx("c2", "sixty-seven") + 0.2))
    PR.gauge(c, 300, 760, 190, 50, "WITH AI")
    PR.gauge(c, 780, 760, 190, v_hand, "BY HAND")
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
        rng = K.rng_at(41, side + 2)                              # both mirrors cracked: a star where something struck
        ox, oy = mx + side * 40, 700 if side < 0 else 1080
        for i in range(11):
            ang = rng.uniform(0, 6.283)
            p = skia.Path()
            x, y = ox, oy
            p.moveTo(x, y)
            for j in range(5):
                x += math.cos(ang + rng.uniform(-0.3, 0.3)) * rng.uniform(20, 70)
                y += math.sin(ang + rng.uniform(-0.3, 0.3)) * rng.uniform(20, 70)
                p.lineTo(x, y)
            c.drawPath(p, paint((236, 242, 250), 0.75, stroke=2.4))
        c.drawCircle(ox, oy, 10, paint((236, 242, 250), 0.6, stroke=2))
        c.restore()
        PR.frame_gilt(c, mx - 150, 560, mx + 150, 1260, t=16)
    CA.face(c, 540, 930, 0.95, "clara", T, L=(255, 60, 170), R=(70, 100, 255), core=0.5, expr="blank", porc=0.9, cap=True,
            blink=0.0, gaze=(0.0, 0.0))
    c.restore()
    return st.arr


def _exam_hall(c, T, a=1.0):
    """The present day through the glass: an exam hall seen from the invigilator's desk - rows of bowed heads, every
    hand writing on paper. Cold, flat, colourless light."""
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 760), paint((168, 176, 180), a))
    c.drawRect(skia.Rect.MakeLTRB(0, 760, W, H), paint((112, 112, 108), a))
    for k in range(3):                                          # tall windows, white sky
        x0 = 250 + k * 220
        c.drawRect(skia.Rect.MakeLTRB(x0, 430, x0 + 130, 700), paint((226, 232, 236), a))
        c.drawLine(x0 + 65, 430, x0 + 65, 700, paint((140, 146, 150), a, stroke=5))
    rows = [(800, 0.34, 5), (870, 0.46, 4), (965, 0.62, 4), (1100, 0.84, 3), (1290, 1.12, 3)]
    hair = [(40, 30, 26), (120, 84, 50), (24, 20, 22), (170, 130, 80), (70, 46, 34), (30, 26, 30)]
    for r, (yd, sc, n) in enumerate(rows):
        sp = 330 * sc
        for j in range(n):
            x = 540 + (j - (n - 1) / 2) * sp
            seed = r * 7 + j
            c.drawRoundRect(skia.Rect.MakeLTRB(x - 70 * sc, yd - 120 * sc, x + 70 * sc, yd + 10 * sc), 30 * sc, 30 * sc,
                            paint([(90, 96, 110), (120, 110, 100), (70, 80, 90), (110, 100, 120)][seed % 4], a))
            c.drawOval(skia.Rect.MakeLTRB(x - 40 * sc, yd - 150 * sc, x + 40 * sc, yd - 70 * sc), paint((196, 164, 146), a))
            c.drawOval(skia.Rect.MakeLTRB(x - 44 * sc, yd - 166 * sc, x + 44 * sc, yd - 92 * sc), paint(hair[seed % 6], a))
            c.drawPath(K.path([(x - 130 * sc, yd), (x + 130 * sc, yd), (x + 150 * sc, yd + 60 * sc), (x - 150 * sc, yd + 60 * sc)]),
                       paint((168, 146, 112), a))
            c.drawRect(skia.Rect.MakeLTRB(x - 150 * sc, yd + 60 * sc, x + 150 * sc, yd + 72 * sc), paint((110, 92, 70), a))
            c.drawPath(K.path([(x - 64 * sc, yd + 8 * sc), (x + 56 * sc, yd + 8 * sc), (x + 62 * sc, yd + 54 * sc), (x - 70 * sc, yd + 54 * sc)]),
                       paint((240, 240, 234), a))
            n_ln = int((T * 1.6 + seed * 0.37) % 6)
            for q in range(n_ln):
                yy = yd + (16 + q * 7) * sc
                c.drawLine(x - 56 * sc, yy, x + 40 * sc, yy, paint((60, 70, 120), 0.8 * a, stroke=max(1, 2.2 * sc)))
            ph = (T * 1.6 + seed * 0.37) % 1.0
            px, py = x - 50 * sc + 90 * sc * ph, yd + (16 + n_ln * 7) * sc
            c.drawLine(px, py, px + 30 * sc, py - 46 * sc, paint((24, 24, 34), a, stroke=max(1.5, 5 * sc)))
            c.drawCircle(px + 30 * sc, py - 46 * sc, 13 * sc, paint((200, 160, 140), a))


def _interview_room(c, T, a=1.0):
    """...and an interview room: two interviewers behind a table, phones in a tray, and an empty chair waiting."""
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((190, 196, 198), a))
    c.drawRect(skia.Rect.MakeLTRB(0, 1100, W, H), paint((128, 126, 122), a))
    c.drawRect(skia.Rect.MakeLTRB(230, 430, 520, 720), paint((226, 230, 232), a))
    for k in range(12):
        c.drawLine(230, 440 + k * 24, 520, 440 + k * 24, paint((176, 182, 186), a, stroke=4))
    for x, who in ((380, "int1"), (710, "int2")):
        CA.face(c, x, 760, 0.5, who, T, L=(236, 236, 232), R=(214, 218, 224), core=0.0, amb=(196, 196, 196), expr="neutral",
                blink=blink(T, seed=x), a=a)
    c.drawRect(skia.Rect.MakeLTRB(150, 930, 930, 962), paint((236, 236, 234), a))
    c.drawRect(skia.Rect.MakeLTRB(170, 962, 910, 1080), paint((206, 206, 204), a))
    c.drawRect(skia.Rect.MakeLTRB(300, 912, 420, 930), paint((240, 240, 238), a))
    c.drawRect(skia.Rect.MakeLTRB(650, 902, 730, 930), paint((60, 64, 74), a))
    c.drawRect(skia.Rect.MakeLTRB(662, 896, 690, 912), paint((20, 20, 24), a))
    c.drawRect(skia.Rect.MakeLTRB(694, 896, 722, 912), paint((20, 20, 24), a))
    c.drawRoundRect(skia.Rect.MakeLTRB(430, 1060, 650, 1250), 18, 18, paint((54, 56, 64), a))
    c.drawRect(skia.Rect.MakeLTRB(410, 1240, 670, 1272), paint((44, 46, 54), a))
    for x in (424, 656):
        c.drawLine(x, 1272, x, 1300, paint((30, 30, 36), a, stroke=8))


def s_m_super(T, idx):
    """So universities are bringing back handwritten exams, and employers face-to-face interviews. A tall mirror in the
    hall of mirrors shows a room that is not there: the present day - an exam hall where every hand writes; then an
    interview room with an empty chair, waiting."""
    st = K.Stage((4, 8, 6))
    c = st.c
    t0 = cut("m_super")
    k_int = K.ease(ramp(T, Wx("m2", "employers") - 0.35, Wx("m2", "employers") + 0.45))
    zoom(c, T, t0, end("m_super") + 0.4, 1.0, 1.14, cx=540, cy=820)

    def albedo(cc):
        cc.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((30, 88, 66)))
        rng = K.rng_at(31, 2)
        for i in range(9):
            for j in range(14):
                x, y = 60 + i * 130 + (j % 2) * 65, 40 + j * 140
                cc.drawOval(skia.Rect.MakeLTRB(x - 22, y - 34, x + 22, y + 34), paint((20, 64, 48), 0.8))
        cc.drawRect(skia.Rect.MakeLTRB(0, 1420, W, H), paint((50, 36, 30)))

    def light(cc):
        G.pool(cc, 120, 820, 620, MAGENTA, 0.85)
        G.pool(cc, 960, 820, 620, (60, 90, 255), 0.85)
        G.pool(cc, 540, 1500, 560, AMBER, 0.5)
    SE.lit2d(c, albedo, light, amb=(10, 14, 12))
    mx0, my0, mx1, my1 = 170, 410, 910, 1290
    glass = skia.Path()
    glass.addRoundRect(skia.Rect.MakeLTRB(mx0, my0, mx1, my1), 370, 120)
    c.drawPath(glass, paint((8, 10, 12)))
    c.save()
    c.clipPath(glass, doAntiAlias=True)
    if k_int < 1:
        _exam_hall(c, T)
    if k_int > 0:
        _interview_room(c, T, a=k_int)
    c.drawPaint(paint((120, 140, 150), 0.12))                   # cold, silvered glass
    rng = K.rng_at(61, 3)
    for i in range(16):                                         # the silvering going black at the very edges
        ang = rng.uniform(0, 2 * math.pi)
        rx, ry = 540 + math.cos(ang) * rng.uniform(350, 400), 835 + math.sin(ang) * rng.uniform(430, 480)
        c.drawCircle(rx, ry, rng.uniform(8, 24), paint((10, 12, 10), 0.4, blur=8))
    c.drawPath(K.path([(mx0, my0 + 120), (mx0 + 260, my0), (mx0 + 380, my0), (mx0, my0 + 420)]), paint(WHITE, 0.06))
    rng = K.rng_at(43, 1)                                       # an old crack across one corner of the glass
    p = skia.Path()
    x, y = mx1 - 40, my0 + 160
    p.moveTo(x, y)
    for j in range(7):
        x -= rng.uniform(20, 60)
        y += rng.uniform(30, 80)
        p.lineTo(x, y)
        if j % 2:
            c.drawLine(x, y, x + rng.uniform(20, 60), y + rng.uniform(-40, 20), paint((236, 242, 250), 0.4, stroke=1.6))
    c.drawPath(p, paint((236, 242, 250), 0.55, stroke=2.2))
    CA.face(c, 540, 820, 1.3, "clara", T, L=(255, 60, 170), R=(70, 100, 255), core=0.5, expr="blank", porc=0.9, blink=0.0,
            a=0.16 * (1 - k_int), neck=False)
    c.restore()
    c.drawPath(glass, paint(mix(GOLD, BLACK, 0.5), stroke=30))
    c.drawPath(glass, paint(mix(GOLD, WHITE, 0.25), stroke=10))
    c.drawPath(glass, paint(mix(GOLD, BLACK, 0.3), stroke=3))
    for x in (90, 990):                                         # candles either side
        G.candle(c, x, 980, 1.1, T, seed=x)
    PR.plaque(c, 540, 340, ["HANDWRITTEN EXAMS"], 40, w=600, a=1 - k_int, tag="plaque")
    if k_int > 0:
        PR.plaque(c, 540, 340, ["FACE-TO-FACE INTERVIEWS"], 40, w=680, a=k_int, tag="plaque")
    c.restore()
    return st.arr


def s_x_door(T, idx):
    """Your examination is waiting. The Governess, close, holding up a key on a black ribbon; then the corridor, the
    door at its end turning on its key and opening on a blinding white, and Clara walking into it."""
    st = K.Stage()
    c = st.c
    t0 = cut("x_door")
    t_c = E("x1") + 0.05
    if T < t_c:
        zoom(c, T, t0, t_c, 1.0, 1.2, cx=540, cy=820)
        G.pool(c, 140, 700, 700, MAGENTA, 0.55)
        G.pool(c, 940, 900, 700, (50, 80, 255), 0.6)
        for i, (bx, by, br) in enumerate(((180, 420, 70), (900, 380, 60), (120, 1260, 90), (980, 1300, 80), (560, 260, 50))):
            G.pool(c, bx, by, br * (1 + 0.05 * math.sin(T * 7 + i)), AMBER, 0.6)
        c.drawRect(skia.Rect.MakeLTRB(330, 160, 750, 1500), paint((20, 10, 14), 0.6, blur=30))
        CA.face(c, 540, 860, 1.45, "governess", T, L=(255, 170, 70), R=(70, 100, 255), core=0.45, expr="polite",
                talk=talk(T, "GOV"), blink=blink(T, seed=5) * 0.0, porc=0.5)
        sway = 10 * math.sin(T * 2.4)
        kx, ky = 830 + sway, 1180
        c.drawLine(800, 560, kx, ky - 40, paint((8, 6, 8), stroke=7))
        c.drawCircle(kx, ky, 38, paint(GOLD, stroke=12))
        c.drawRect(skia.Rect.MakeLTRB(kx - 8, ky + 36, kx + 8, ky + 190), paint(GOLD))
        for k in range(2):
            c.drawRect(skia.Rect.MakeLTRB(kx + 8, ky + 140 + k * 30, kx + 40, ky + 156 + k * 30), paint(GOLD))
        c.drawCircle(kx - 14, ky - 14, 10, G.glow_paint((255, 250, 220), 0.6 + 0.4 * math.sin(T * 5), blur=6))
        c.restore()
        return st.arr
    u = T - t_c
    cam = P.Cam(pos=(0.0, 1.6, 6.2 + 1.0 * u), f=900)
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
    pos = (1.05, 0.0, zd - 0.5)
    gq = cam.proj((1.05, 1.65, zd - 0.5))
    if gq is not None:
        s = cam.scale_at(pos) / 900
        CA.face(c, gq[0], gq[1], s * 0.75, "governess", T, L=(255, 170, 70), R=(70, 100, 255), core=0.4, expr="polite",
                blink=0.0, porc=0.5)
    cp = cam.proj((0.0, 0.0, cam.pos[2] + 2.6))
    CA.walker_back(c, cp[0], cp[1], cam.scale_at((0, 0, cam.pos[2] + 2.6)) * 1.72 / 900, T, coat=(20, 18, 24), key=(70, 100, 255),
                   rim=(255, 60, 170), walking=True)
    if T > E("x1") + 0.6:
        c.drawPaint(paint((255, 255, 255), K.ease(ramp(T, E("x1") + 0.6, E("x1") + 1.15))))
    return st.arr

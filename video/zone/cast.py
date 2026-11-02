"""The cast. Two kinds, as in a cheap midnight musical that mixes actors and cartoons:

LIVE (soft photographic shading, no outlines, moving at 24): Mae, 56, a school-bus driver; the Emcee, a tall woman in
top hat and tails; the doctors.
CARTOON (flat, inked, rubber-hose, on twos): the Second Eye (the AI: an eyeball on noodle legs, wearing Mae's glasses),
a chorus of skeletons, the octopus librarian, King Hemoglobin (a red blood cell in a crown), dancing pills, a bathroom
scale, a heart that ticks like a metronome, the Alarm Rooster, and Her Majesty the Early Bird.
"""
import math

import numpy as np
import skia

import draw as D
import person as P
import zkit as Z
from draw import INK, WHITE, ease, mix, paint, path
from zkit import BLACK, CHALK, GREY, OUT, blob, circ, glove, hose, pie_eye, shoe, twos

SKIN, SKIN_D = (214, 180, 158), (150, 112, 94)
HAIR_GREY, HAIR_DARK = (196, 194, 190), (34, 30, 30)


# ------------------------------------------------------------------ the recurring object

def glasses(c, x, y, s=1.0, rot=0.0, shine=0.0, a=1.0):
    """Mae's reading glasses: heavy horn rims, round-cornered lenses, a keyhole bridge."""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    for sx in (-1, 1):
        r = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(sx * 12 if sx > 0 else -82, -30, 82 if sx > 0 else -12, 30), 18, 18)
        c.drawRRect(r, paint((230, 236, 240), 0.35 * a))
        c.drawRRect(r, paint((210, 206, 200), a, stroke=16))                      # a pale edge so they read on the dark
        c.drawRRect(r, paint((20, 16, 14), a, stroke=11))
        if shine > 0:
            c.drawLine(sx * 30 - 14, -16, sx * 30 + 6, -2, paint(WHITE, shine * a, stroke=6))
    p = skia.Path()
    p.moveTo(-12, -8)
    p.quadTo(0, -22, 12, -8)
    c.drawPath(p, paint((210, 206, 200), a, stroke=14))
    c.drawPath(p, paint((20, 16, 14), a, stroke=9))
    c.drawLine(-82, -14, -104, -18, paint((20, 16, 14), a, stroke=8))
    c.drawLine(82, -14, 104, -18, paint((20, 16, 14), a, stroke=8))
    c.restore()


# ------------------------------------------------------------------ live figures

def _soft(c, p, col, k=0.3, a=1.0):
    D.shade(c, p, col, k=k, edge=0.0, a=a)


def mae_face(c, x, y, s, T, expr="puzzled", glasses_on=False, eyes_closed=False, look=(0.0, 0.0), matte=False, wink=0.0):
    """Mae, close: a round face, short grey curls, laugh lines. (x, y) is the chin; s = 1 is a 560 px-tall head."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    breathe = 1 + 0.004 * math.sin(T * 2.2)
    c.scale(1, breathe)
    neck = D.rrect(-70, -60, 70, 120, 30)
    _soft(c, neck, mix(SKIN, SKIN_D, 0.3))
    collar = path([(-260, 140), (-80, 40), (0, 110), (80, 40), (260, 140), (300, 400), (-300, 400)])
    _soft(c, collar, (118, 116, 122), 0.25)                            # the cardigan
    c.drawPath(path([(-80, 40), (0, 110), (-20, 180), (-110, 90)]), paint((226, 224, 218)))          # blouse collar
    c.drawPath(path([(80, 40), (0, 110), (20, 180), (110, 90)]), paint((226, 224, 218)))
    head = D.smooth([(-170, -260), (-150, -60), (-90, 20), (0, 44), (90, 20), (150, -60), (170, -260), (120, -400), (0, -440), (-120, -400)])
    if matte:
        Z.matte_edge(c, head)
    _soft(c, head, SKIN, 0.32)
    for sx in (-1, 1):                                                 # ears
        c.drawOval(skia.Rect.MakeLTRB(sx * 190 - 26, -250, sx * 190 + 26, -160), paint(mix(SKIN, SKIN_D, 0.35)))
    rng = np.random.default_rng(3)
    for i in range(46):                                                # short grey curls
        ang = math.pi * (1.05 + 0.9 * i / 45)
        rr = 180 + rng.uniform(-10, 30)
        cx, cy = rr * math.cos(ang) * 1.02, -300 + rr * math.sin(ang) * 0.85
        r = rng.uniform(34, 50)
        c.drawCircle(cx, cy, r, paint(mix(HAIR_GREY, INK, rng.uniform(0.0, 0.25))))
        c.drawCircle(cx - r * 0.2, cy - r * 0.25, r * 0.45, paint(WHITE, 0.25))
    for sx in (-1, 1):
        for j in range(4):
            c.drawCircle(sx * (150 + 8 * j), -330 + j * 40, 36, paint(mix(HAIR_GREY, INK, 0.1 * j)))
    # the face
    blink = 1.0 if eyes_closed else (1.0 if (T * 0.9) % 4.0 < 0.12 else 0.0)
    for sx in (-1, 1):
        c.drawOval(skia.Rect.MakeLTRB(sx * 72 - 60, -262, sx * 72 + 60, -160), paint(SKIN_D, 0.28, blur=16))   # sockets
    for sx in (-1, 1):
        ex, ey = sx * 72, -205
        w_ = wink if sx > 0 else 0.0
        if blink > 0.5 or w_ > 0.5:
            p = skia.Path()
            p.moveTo(ex - 36, ey)
            p.quadTo(ex, ey + 18, ex + 36, ey)
            c.drawPath(p, paint((70, 48, 42), stroke=7))
        else:
            c.drawOval(skia.Rect.MakeLTRB(ex - 36, ey - 19, ex + 36, ey + 19), paint((246, 244, 240)))
            c.drawCircle(ex + look[0] * 12, ey + look[1] * 6, 15, paint((52, 42, 38)))
            c.drawCircle(ex + look[0] * 12, ey + look[1] * 6, 7, paint((10, 8, 8)))
            c.drawCircle(ex + look[0] * 12 + 5, ey + look[1] * 6 - 6, 4.5, paint(WHITE))
            p = skia.Path()                                             # upper lid
            p.moveTo(ex - 40, ey + 2)
            p.quadTo(ex, ey - 34, ex + 40, ey + 2)
            c.drawPath(p, paint((80, 58, 50), stroke=5))
        c.drawLine(ex + sx * 44, ey + 10, ex + sx * 58, ey + 26, paint(SKIN_D, 0.55, stroke=3))   # laugh lines
        lift = {"puzzled": (22 if sx < 0 else -2), "happy": 10, "worried": 0, "calm": 4}.get(expr, 4)
        inner = {"worried": 14, "puzzled": 0}.get(expr, 0)
        p = skia.Path()                                                 # brows: an arc; inner end raised when worried
        p.moveTo(ex - sx * 42, ey - 52 - lift - inner)
        p.quadTo(ex, ey - 72 - lift * 1.3, ex + sx * 44, ey - 46 - lift * 0.6)
        c.drawPath(p, paint((150, 146, 140), stroke=11))
    c.drawPath(D.smooth([(-12, -176), (-30, -104), (-16, -84), (0, -80), (16, -84), (30, -104), (12, -176)]), paint(SKIN_D, 0.22, blur=4))
    c.drawCircle(-15, -92, 7, paint(SKIN_D, 0.6))
    c.drawCircle(15, -92, 7, paint(SKIN_D, 0.6))
    c.drawCircle(0, -112, 12, paint(WHITE, 0.25, blur=4))
    mouth = {"puzzled": ((-46, -36), (0, -44), (48, -30)), "happy": ((-66, -48), (0, -2), (66, -48)),
             "worried": ((-48, -30), (0, -42), (48, -30)), "calm": ((-44, -38), (0, -30), (44, -38))}[expr]
    p = skia.Path()
    p.moveTo(*mouth[0])
    p.quadTo(*mouth[1], *mouth[2])
    if expr == "happy":
        p.quadTo(0, -24, *mouth[0])
        c.drawPath(p, paint((130, 64, 60)))
        c.drawLine(-44, -40, 44, -40, paint(WHITE, 0.9, stroke=6))
    else:
        c.drawPath(p, paint((140, 72, 66), stroke=11))
    c.drawOval(skia.Rect.MakeLTRB(-40, -8, 40, 12), paint(SKIN_D, 0.25, blur=6))                  # under the lip
    for sx in (-1, 1):
        c.drawCircle(sx * 112, -118, 36, paint((230, 150, 140), 0.2, blur=12))
    if glasses_on:
        glasses(c, 0, -205, 1.02)
    c.restore()


def _cardigan(c, sh_y, hipY):
    c.drawPath(path([(-34, sh_y - 6), (0, sh_y + 60), (34, sh_y - 6)]), paint((232, 230, 224)))       # blouse collar
    c.drawLine(0, sh_y + 60, 0, hipY + 10, paint((70, 68, 74), stroke=3))
    for k in range(4):
        c.drawCircle(0, sh_y + 100 + k * 70, 6, paint((220, 216, 210)))


def mae(c, x, y, s, T, pose="stand", glasses_on=False, matte=False, expr="puzzled", outfit="cardigan", joints=None):
    """Mae, 56, full figure: short grey curls, a grey cardigan over a white blouse, slacks, flat shoes."""
    look = dict(pose=pose, top=(122, 120, 128), bottom=(40, 38, 44), hair="curls", haircol=(206, 204, 200),
                browcol=(150, 146, 140), expr=expr, glasses=glasses_on, extras=[_cardigan], seed=1, joints=joints or {})
    if outfit == "gown":
        look.update(top=(214, 218, 222), extras=[], bottom=(214, 218, 222))
    if outfit == "uniform":
        look.update(top=(70, 88, 140), extras=[_cardigan])
    P.person(c, x, y, s, T, look, matte=matte)


def _tux(c, sh_y, hipY):
    c.drawPath(path([(-40, sh_y - 4), (0, sh_y + 250), (40, sh_y - 4)]), paint((246, 244, 240)))       # shirt front
    c.drawPath(path([(-34, sh_y + 6), (0, sh_y + 22), (34, sh_y + 6), (34, sh_y + 40), (0, sh_y + 22), (-34, sh_y + 40)]),
               paint((16, 14, 14)))                                                                       # bow tie
    for k in range(3):
        c.drawCircle(0, sh_y + 80 + k * 50, 5, paint((20, 18, 18)))


def _tophat(c):
    c.save()
    c.translate(8, -196)
    c.rotate(-8)
    c.drawRect(skia.Rect.MakeLTRB(-50, -150, 50, -8), paint((18, 16, 18)))
    c.drawRect(skia.Rect.MakeLTRB(-50, -150, 50, -8), paint((200, 198, 196), stroke=5))                 # rim light
    c.drawRect(skia.Rect.MakeLTRB(-50, -44, 50, -22), paint((130, 128, 130)))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-92, -16, 92, 4), 9, 9), paint((18, 16, 18)))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-92, -16, 92, 4), 9, 9), paint((200, 198, 196), stroke=4))
    c.restore()


EMCEE_ROUTINE = ["present", "cane", "wave", "kick", "present", "both_up"]


def emcee(c, x, y, s, T, pose="present", matte=True, cane=True, expr="grin", joints=None, routine=False, bpm=120):
    """The Emcee: tall, a sleek black bob, top hat and tails, white gloves, dark lipstick, a cane. routine=True: she
    works through her vaudeville business (sweep, cane twirl, wave, high kick) two beats per pose."""
    if routine:
        pose = EMCEE_ROUTINE[int(T * bpm / 60 / 2) % len(EMCEE_ROUTINE)]
    look = dict(pose=pose, top=(28, 26, 30), sleeve=(28, 26, 30), bottom=(40, 38, 42), legcol=(70, 66, 70), hair="bob",
                haircol=(20, 18, 20), browcol=(20, 18, 20), expr=expr, lip=(70, 14, 20), tails=True, extras=[_tux],
                hat=[_tophat], seed=2, joints=joints or {}, skin=(222, 196, 178))
    P.person(c, x, y, s, T, look, matte=matte)
    if cane and "L" in P.HANDS:                                         # the cane, in her left hand, twirling on "cane"
        hx, hy, a1 = P.HANDS["L"]
        ang = T * 9 if pose == "cane" else 0.35
        L = 330 * s
        c.save()
        c.resetMatrix()
        c.drawLine(hx - L * 0.2 * math.sin(ang), hy - L * 0.2 * math.cos(ang), hx + L * 0.8 * math.sin(ang), hy + L * 0.8 * math.cos(ang),
                   paint((14, 12, 12), stroke=13 * s))
        c.drawCircle(hx - L * 0.2 * math.sin(ang), hy - L * 0.2 * math.cos(ang), 17 * s, paint(WHITE))
        c.restore()


def _coat(c, sh_y, hipY):
    c.drawLine(0, sh_y + 20, 0, hipY + 190, paint((170, 170, 168), stroke=3))
    c.drawPath(path([(-30, sh_y - 4), (0, sh_y + 70), (30, sh_y - 4)]), paint((120, 130, 150)))
    p = skia.Path()
    p.moveTo(-40, sh_y + 10)
    p.quadTo(-60, sh_y + 180, 0, sh_y + 190)
    p.quadTo(60, sh_y + 180, 40, sh_y + 10)
    c.drawPath(p, paint((40, 40, 44), stroke=6))
    c.drawCircle(0, sh_y + 196, 13, paint((160, 160, 166)))
    c.drawRect(skia.Rect.MakeLTRB(-80, sh_y + 110, -40, sh_y + 160), paint((210, 210, 208)))
    c.drawLine(-74, sh_y + 110, -74, sh_y + 90, paint((40, 40, 120), stroke=4))


def _scrubs(c, sh_y, hipY):
    c.drawPath(path([(-36, sh_y - 4), (0, sh_y + 60), (36, sh_y - 4)]), paint((120, 128, 132)))


def doctor(c, x, y, s, T, pose="stand", masked=False, matte=True, expr="calm", hair="short", seed=3, joints=None,
           skin=None, haircol=(60, 52, 48)):
    """A doctor: white coat and stethoscope, or (masked) scrubs, cap and mask."""
    look = dict(pose=pose, top=(236, 236, 234), bottom=(70, 72, 78), hair=hair, haircol=haircol, expr=expr, coat=True,
                extras=[_coat], seed=seed, joints=joints or {})
    if skin:
        look["skin"] = skin
    if masked:
        look.update(top=(160, 168, 172), bottom=(160, 168, 172), coat=False, extras=[_scrubs], hair="cap", mask=True)
    P.person(c, x, y, s, T, look, matte=matte)


def mae_asleep(c, x, y, s, T):
    """Mae on the table, sedated, under a blanket: her own face (curls, closed eyes, a small smile) on the pillow,
    turned toward us."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-420, -60, 420, 20), 20, 20), paint((200, 200, 204)))     # the table
    c.drawRect(skia.Rect.MakeLTRB(-380, 20, -350, 260), paint((80, 80, 84)))
    c.drawRect(skia.Rect.MakeLTRB(350, 20, 380, 260), paint((80, 80, 84)))
    c.drawOval(skia.Rect.MakeLTRB(-440, -190, -200, -50), paint((236, 236, 236)))                     # the pillow
    c.save()                                                            # her face, lying on the pillow, turned to us
    c.translate(-300, -150)
    c.rotate(-72)
    mae_face(c, 0, 0, 0.3, T, expr="calm", eyes_closed=True)
    c.restore()
    rise = 6 * math.sin(T * 1.4)
    blanket = D.smooth([(-250, -60), (-230, -170 - rise), (100, -190 - rise), (380, -130), (400, -60)])
    _soft(c, blanket, (170, 172, 180), 0.3)
    for k in range(5):
        c.drawLine(-200 + k * 120, -150 - rise, -180 + k * 120, -70, paint((140, 142, 150), stroke=4))
    c.restore()


# ------------------------------------------------------------------ cartoon creatures (all on twos)

def second_eye(c, x, y, s, T, look=(0.0, 0.0), pose="dance", target=None, glasses_on=True, blink=0.0, seed=1, stamp=0.0):
    """The Second Eye: the AI. A big white eyeball on noodle legs, gloves, Mae's glasses perched on it.
    (x, y) between its shoes; s = 1 is ~560 px tall. target: a canvas point its glove points at."""
    T2 = twos(T)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    bob = abs(math.sin(T2 * math.pi * 1.6)) * 22 if pose == "dance" else 4 * math.sin(T2 * 3)
    kick = math.sin(T2 * math.pi * 1.6) if pose == "dance" else 0
    # legs
    for sx in (-1, 1):
        fx = sx * 70 + (kick * 40 * sx if pose == "dance" else 0)
        hose(c, sx * 40, -280 + bob, fx, -26, bend=0.2 * sx, w=22)
        shoe(c, fx - 10 * (sx < 0), -8, 1.3, flip=sx)
    cy = -420 + bob
    # arms
    if pose == "point" and target is not None:
        tx = (target[0] - x) / s
        ty = (target[1] - y) / s
        ang = math.atan2(ty - cy, tx + 0.0)
        hx, hy = 150 * math.cos(ang) + 150, cy + 150 * math.sin(ang)
        hx, hy = 150 + (tx - 150) * 0.55, cy + (ty - cy) * 0.55
        hose(c, 140, cy + 20, hx, hy, bend=-0.15, w=20)
        glove(c, hx, hy, 1.3, math.degrees(math.atan2(ty - hy, tx - hx)), point=True)
        hose(c, -140, cy + 20, -210, cy + 120 + 20 * math.sin(T2 * 4), bend=0.3, w=20)
        glove(c, -210, cy + 120 + 20 * math.sin(T2 * 4), 1.3, 150)
    else:
        sw = math.sin(T2 * math.pi * 1.6)
        for sx in (-1, 1):
            hx, hy = sx * (230 + 20 * sw * sx), cy - 90 + 70 * sw * sx
            if pose == "stamp" and sx > 0:
                hx, hy = 200, cy - 140 + 240 * stamp
            hose(c, sx * 140, cy + 10, hx, hy, bend=0.3 * sx, w=20)
            glove(c, hx, hy, 1.3, 90 - 90 * sx if sx < 0 else -20)
            if pose == "stamp" and sx > 0:
                c.drawRect(skia.Rect.MakeLTRB(hx - 44, hy + 16, hx + 44, hy + 44), paint(BLACK))
                c.drawRect(skia.Rect.MakeLTRB(hx - 16, hy - 40, hx + 16, hy + 16), paint((90, 70, 50)))
    # the eyeball
    blob(c, [(150 * math.cos(a), cy + 150 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 16, endpoint=False)],
         WHITE, T, seed, amp=2.5, ow=OUT + 1)
    for k in range(4):                                                  # a few red veins
        a0 = math.pi * (0.2 + k * 0.45)
        pts = [(150 * math.cos(a0) * r, cy + 150 * math.sin(a0) * r + 8 * math.sin(r * 9 + k)) for r in (0.95, 0.8, 0.66)]
        c.drawPath(D.smooth(pts, closed=False), paint((150, 60, 60), 0.7, stroke=3))
    ix, iy = look[0] * 50, cy + look[1] * 40
    c.drawCircle(ix, iy, 70, paint((90, 88, 86)))
    for k in range(16):
        a = 2 * math.pi * k / 16
        c.drawLine(ix + 30 * math.cos(a), iy + 30 * math.sin(a), ix + 66 * math.cos(a), iy + 66 * math.sin(a), paint((60, 58, 56), stroke=3))
    c.drawCircle(ix, iy, 70, paint(BLACK, stroke=5))
    pie_eye(c, ix, iy, 34, 34, (0, 0), 0.0, white=(90, 88, 86))
    c.drawCircle(ix, iy, 30, paint(BLACK))
    c.drawCircle(ix + 14, iy - 16, 10, paint(WHITE))
    if blink > 0:                                                       # the lid comes down
        c.save()
        c.clipPath(D.circle(0, cy, 150))
        c.drawRect(skia.Rect.MakeLTRB(-160, cy - 160, 160, cy - 160 + 320 * blink), paint((220, 216, 208)))
        c.drawLine(-160, cy - 160 + 320 * blink, 160, cy - 160 + 320 * blink, paint(BLACK, stroke=6))
        c.restore()
    if glasses_on:
        glasses(c, ix * 0.8, cy - 8, 1.25, rot=-6 + 4 * math.sin(T2 * 3))
    c.restore()


def skeleton(c, x, y, s, T, phase=0.0, frame=None, seed=0):
    """A chorus-line skeleton: pie-eyed skull, rib hoops, bone noodles; kicks on the beat. frame(c) draws what it holds."""
    T2 = twos(T)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    kick = math.sin((T2 * 2 + phase) * math.pi)
    bone = (236, 232, 220)
    for sx in (-1, 1):
        lift = max(0.0, kick * sx)
        fx, fy = sx * 50 + lift * sx * 120, -20 - lift * 250
        hose(c, sx * 26, -300, fx, fy, bend=0.1 * sx, w=16, col=BLACK)
        hose(c, sx * 26, -300, fx, fy, bend=0.1 * sx, w=8, col=bone)
        shoe(c, fx, fy + 10, 0.9, flip=sx)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-40, -330, 40, -290), 14, 14), paint(bone))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-40, -330, 40, -290), 14, 14), paint(BLACK, stroke=5))
    c.drawLine(0, -560, 0, -320, paint(BLACK, stroke=16))
    c.drawLine(0, -560, 0, -320, paint(bone, stroke=8))
    for k in range(4):                                                  # ribs
        yy = -540 + k * 42
        r = skia.Rect.MakeLTRB(-70 + k * 6, yy - 18, 70 - k * 6, yy + 18)
        c.drawArc(r, 200, 140, False, paint(BLACK, stroke=13))
        c.drawArc(r, 200, 140, False, paint(bone, stroke=6))
    for sx in (-1, 1):                                                  # arms up, holding the frame
        hx, hy = sx * 110, -800
        hose(c, sx * 50, -560, hx, hy, bend=0.2 * sx, w=14)
        glove(c, hx, hy, 0.9, -90)
    circ(c, 0, -640, 70, bone, T, seed)
    pie_eye(c, -26, -650, 20, 26, (0.3 * math.sin(T2 * 2), 0), 0.0)
    pie_eye(c, 26, -650, 20, 26, (0.3 * math.sin(T2 * 2), 0), 0.0)
    c.drawPath(path([(-8, -612), (8, -612), (0, -596)]), paint(BLACK))
    for k in range(-3, 4):
        c.drawLine(k * 12, -586, k * 12, -572, paint(BLACK, stroke=4))
    c.drawLine(-40, -580, 40, -580, paint(BLACK, stroke=4))
    c.restore()
    if frame is not None:
        c.save()
        c.translate(x, y - 860 * s)
        c.scale(s, s)
        frame(c)
        c.restore()


def octopus(c, x, y, s, T, glasses_on=True, page=0.0, seed=4):
    """The octopus librarian: a domed head in a hair bun, Mae's glasses, eight noodle tentacles filing papers."""
    T2 = twos(T)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    tone = (150, 146, 150)
    for k in range(8):
        a0 = math.pi * (0.1 + 0.8 * k / 7)
        wave = math.sin(T2 * 5 + k)
        ex, ey = 360 * math.cos(a0) * 1.1, -100 + 260 * math.sin(a0) * (0.5 + 0.2 * wave)
        mx, my = (ex * 0.5) + 60 * wave, -150 + 60 * math.sin(T2 * 3 + k)
        p = skia.Path()
        p.moveTo(0, -200)
        p.quadTo(mx, my, ex, ey)
        c.drawPath(p, paint(BLACK, stroke=40))
        c.drawPath(p, paint(tone, stroke=28))
        for j in range(3):                                              # suckers
            t = 0.5 + j * 0.2
            qx = (1 - t) ** 2 * 0 + 2 * (1 - t) * t * mx + t ** 2 * ex
            qy = (1 - t) ** 2 * -200 + 2 * (1 - t) * t * my + t ** 2 * ey
            c.drawCircle(qx, qy, 6, paint((220, 216, 210)))
        if k % 2 == 0:                                                  # papers in some tentacles
            c.save()
            c.translate(ex, ey)
            c.rotate(20 * wave)
            c.drawRect(skia.Rect.MakeLTRB(-34, -44, 34, 44), paint((244, 242, 234)))
            c.drawRect(skia.Rect.MakeLTRB(-34, -44, 34, 44), paint(BLACK, stroke=4))
            for j in range(4):
                c.drawLine(-24, -28 + j * 16, 24, -28 + j * 16, paint(GREY, stroke=3))
            c.restore()
    blob(c, [(-190, -200), (-200, -420), (-120, -560), (0, -600), (120, -560), (200, -420), (190, -200), (0, -150)], tone, T, seed)
    circ(c, 0, -620, 60, (60, 58, 60), T, seed + 1)                      # the bun
    c.drawLine(-30, -680, 40, -600, paint(BLACK, stroke=8))              # a pencil through it
    pie_eye(c, -70, -360, 44, 56, (0.3, 0.2), 0.0)
    pie_eye(c, 70, -360, 44, 56, (0.3, 0.2), 0.0)
    if glasses_on:
        glasses(c, 0, -360, 1.1)
    p = skia.Path()
    p.moveTo(-50, -250)
    p.quadTo(0, -210, 50, -250)
    c.drawPath(p, paint(BLACK, stroke=7))
    c.restore()


def king_heme(c, x, y, s, T, size=1.0, tint=None, seed=6, crown=True):
    """King Hemoglobin: a red blood cell (a dimpled disc) in a crown and ermine cape, on noodle legs.
    size shrinks him year by year. tint: the hand-tint canvas (his red is painted on)."""
    T2 = twos(T)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    r = 210 * size
    cy = -130 - r * 0.62
    if crown:
        cape = [(-r * 0.7, cy - r * 0.2), (r * 0.7, cy - r * 0.2), (r * 1.15 + 20, -30), (0, -10), (-r * 1.15 - 20, -30)]
        blob(c, cape, (96, 92, 100), T, seed + 5, amp=2, ow=5)                                         # the royal cape
        c.drawPath(path([(-r * 1.15 - 20, -30), (0, -10), (r * 1.15 + 20, -30), (r * 1.1, -60), (-r * 1.1, -60)]), paint((240, 238, 232)))
        for k in range(7):
            c.drawCircle(-r * 0.95 + k * r * 0.32, -40 - 4 * (k % 2), 6, paint(BLACK))               # ermine trim
    for sx in (-1, 1):
        fx = sx * 60 + sx * 20 * math.sin(T2 * 6)
        hose(c, sx * 30, -120, fx, -20, bend=0.2 * sx, w=18)
        shoe(c, fx, -6, 1.1, flip=sx)
    disc = [(r * math.cos(a), cy + r * 0.62 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 18, endpoint=False)]
    blob(c, disc, (150, 60, 60), T, seed)
    c.drawOval(skia.Rect.MakeLTRB(-r * 0.5, cy - r * 0.26, r * 0.5, cy + r * 0.26), paint((190, 110, 110)))
    pie_eye(c, -r * 0.28, cy - r * 0.05, r * 0.14, r * 0.2, (0, 0.2), 0.0)
    pie_eye(c, r * 0.28, cy - r * 0.05, r * 0.14, r * 0.2, (0, 0.2), 0.0)
    crown_pts = [(-r * 0.4, cy - r * 0.5), (-r * 0.4, cy - r * 0.95), (-r * 0.2, cy - r * 0.72), (0, cy - r * 1.05), (r * 0.2, cy - r * 0.72),
             (r * 0.4, cy - r * 0.95), (r * 0.4, cy - r * 0.5)]
    if crown:
        blob(c, crown_pts, (230, 200, 90), T, seed + 2, smooth=False, ow=5)
    Z.tinted(tint, c, lambda t: (t.drawPath(D.smooth(disc), paint((220, 30, 30), 0.85)),
                                 t.drawPath(path(crown_pts), paint((250, 200, 40), 0.8 if crown else 0.0))))   # his red, painted on
    c.restore()


def pill(c, x, y, s, T, phase=0.0, label="Fe", seed=8, col=(236, 234, 226), dark=(60, 58, 60)):
    """A dancing capsule with a face, kicking in a chorus line."""
    T2 = twos(T)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    kick = math.sin((T2 * 2 + phase) * math.pi)
    for sx in (-1, 1):
        lift = max(0.0, kick * sx)
        fx, fy = sx * 30 + lift * sx * 70, -10 - lift * 120
        hose(c, sx * 20, -80, fx, fy, bend=0.15 * sx, w=12)
        shoe(c, fx, fy + 6, 0.7, flip=sx)
    c.save()
    c.translate(0, -200)
    c.rotate(8 * kick)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-60, -130, 60, 0), 60, 60), paint(dark))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-60, 0, 60, 130), 60, 60), paint(col))
    c.drawRect(skia.Rect.MakeLTRB(-60, -20, 60, 20), paint(col))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-60, -130, 60, 130), 60, 60), paint(BLACK, stroke=OUT))
    pie_eye(c, -22, 30, 14, 20, (0.2, 0), 0.0)
    pie_eye(c, 22, 30, 14, 20, (0.2, 0), 0.0)
    D.text(c, label, 0, -60, 44, "londrina-900", WHITE, tag="pill")
    c.restore()
    for sx in (-1, 1):
        hose(c, sx * 58, -200, sx * 110, -260 - 40 * kick * sx, bend=0.2 * sx, w=12)
        glove(c, sx * 110, -260 - 40 * kick * sx, 0.6, -90 + 60 * sx)
    c.restore()


def bottle(c, x, y, s, T, label="IRON", seed=9, tilt=0.0):
    """A pill bottle with a face (for the pills that clash)."""
    T2 = twos(T)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.rotate(tilt)
    blob(c, [(-80, 0), (-80, -240), (80, -240), (80, 0)], (200, 196, 188), T, seed, smooth=False)
    blob(c, [(-90, -240), (-90, -300), (90, -300), (90, -240)], (50, 48, 50), T, seed + 1, smooth=False)
    c.drawRect(skia.Rect.MakeLTRB(-70, -190, 70, -90), paint(WHITE))
    D.text(c, label, 0, -128, 40, "londrina-900", BLACK, tag="bottle")
    pie_eye(c, -28, -60, 16, 20, (0.4 * math.sin(T2 * 3), 0), 0.0)
    pie_eye(c, 28, -60, 16, 20, (0.4 * math.sin(T2 * 3), 0), 0.0)
    c.restore()


def scale_critter(c, x, y, s, T, kg=72, seed=10):
    """A bathroom scale on noodle legs, reading out the kilos on its dial face."""
    T2 = twos(T)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    for sx in (-1, 1):
        fx = sx * 90 + sx * 10 * math.sin(T2 * 5)
        hose(c, sx * 80, -40, fx, 0, w=14)
        shoe(c, fx, 10, 0.8, flip=sx)
    blob(c, [(-170, -40), (-170, -220), (170, -220), (170, -40)], (220, 218, 212), T, seed, smooth=False)
    circ(c, 0, -150, 58, WHITE, T, seed + 1, ow=5)
    ang = math.radians(-150 + (kg - 60) * 12)
    c.drawLine(0, -150, 46 * math.cos(ang), -150 + 46 * math.sin(ang), paint((180, 40, 40), stroke=6))
    D.text(c, f"{kg} kg", 0, -60, 40, "londrina-900", BLACK, tag="kg")
    c.restore()


def heart_metro(c, x, y, s, T, bpm=64, seed=11, tint=None):
    """A heart that ticks like a metronome: the pendulum swings at its resting pulse; the number on its chest."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    swing = math.sin(T * bpm / 60 * math.pi) * 28
    beat = 1 + 0.05 * max(0.0, math.sin(T * bpm / 60 * 2 * math.pi)) ** 8
    c.save()
    c.scale(beat, beat)
    hp = [(0, -60), (-150, -220), (-150, -330), (-80, -380), (0, -330), (80, -380), (150, -330), (150, -220)]
    p = blob(c, hp, (150, 60, 60), T, seed)
    c.restore()
    c.save()
    c.translate(0, -60)
    c.rotate(swing)
    c.drawLine(0, 0, 0, -300, paint(BLACK, stroke=8))
    c.drawRect(skia.Rect.MakeLTRB(-24, -220, 24, -180), paint(BLACK))
    c.restore()
    D.text(c, f"{bpm}", 0, -240, 56, "londrina-900", WHITE, tag="bpm", outline=BLACK, ow=6)
    D.text(c, "beats/min", 0, -196, 26, "londrina-400", WHITE, tag="bpm")
    Z.tinted(tint, c, lambda t: t.drawPath(D.smooth(hp), paint((220, 40, 40), 0.7)))
    c.restore()


def rooster(c, x, y, s, T, crow=0.0, seed=12):
    """The Alarm Rooster: a rooster whose belly is an alarm clock, bells for a comb."""
    T2 = twos(T)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    shake = math.sin(T * 60) * 6 * crow
    c.translate(shake, 0)
    for sx in (-1, 1):
        hose(c, sx * 40, -160, sx * 60, -10, w=12)
        c.drawLine(sx * 60, -10, sx * 60 + 40, 0, paint(BLACK, stroke=8))
        c.drawLine(sx * 60, -10, sx * 60 - 30, 4, paint(BLACK, stroke=8))
    for k in range(5):                                                  # tail feathers
        a = math.radians(200 + k * 18)
        c.drawPath(D.smooth([(-100, -300), (-100 + 220 * math.cos(a), -300 + 220 * math.sin(a) - 60), (-80, -260)]), paint(BLACK))
    circ(c, 0, -280, 150, WHITE, T, seed)
    for k in range(12):
        a = 2 * math.pi * k / 12
        c.drawLine(110 * math.cos(a), -280 + 110 * math.sin(a), 126 * math.cos(a), -280 + 126 * math.sin(a), paint(BLACK, stroke=5))
    c.drawLine(0, -280, 0, -370, paint(BLACK, stroke=8))
    c.drawLine(0, -280, 60, -250, paint(BLACK, stroke=8))
    circ(c, 90, -470, 80, WHITE, T, seed + 1)                           # head
    c.drawPath(path([(160, -480), (260 + 40 * crow, -470 - 30 * crow), (160, -440)]), paint((220, 190, 90)))
    c.drawPath(path([(160, -480), (260 + 40 * crow, -470 - 30 * crow), (160, -440)]), paint(BLACK, stroke=5))
    if crow > 0:
        c.drawPath(path([(160, -460), (250, -440 + 20 * crow), (160, -450)]), paint(BLACK))
    pie_eye(c, 110, -500, 18, 24, (0.5, 0), 0.0)
    for k in range(3):                                                  # bells for a comb
        circ(c, 40 + k * 50, -560 - 10 * (k == 1), 26, (200, 196, 180), T, seed + 3 + k, ow=5)
    c.restore()


def early_bird(c, x, y, s, T, seed=13):
    """Her Majesty the Early Bird: a stately bird in a ball gown and tiara, fanning herself."""
    T2 = twos(T)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    sway = math.sin(T2 * 2.4) * 6
    c.rotate(sway)
    blob(c, [(-220, 0), (-150, -300), (-70, -420), (70, -420), (150, -300), (220, 0)], (90, 88, 96), T, seed)   # gown
    for k in range(5):
        c.drawLine(-200 + k * 100, -10, -120 + k * 60, -280, paint((150, 148, 156), stroke=5))
    circ(c, 0, -500, 110, WHITE, T, seed + 1)
    c.drawPath(path([(60, -520), (170, -490), (60, -470)]), paint((220, 190, 90)))
    c.drawPath(path([(60, -520), (170, -490), (60, -470)]), paint(BLACK, stroke=5))
    pie_eye(c, 30, -530, 22, 30, (0.4, 0), 0.0)
    blob(c, [(-60, -600), (-40, -660), (-10, -620), (10, -680), (30, -620), (60, -660), (70, -600)], (230, 220, 160), T, seed + 2, smooth=False, ow=5)
    ang = 30 + 20 * math.sin(T2 * 6)                                    # the fan
    c.save()
    c.translate(-170, -300)
    c.rotate(-ang)
    for k in range(7):
        c.save()
        c.rotate(-45 + k * 15)
        c.drawRect(skia.Rect.MakeLTRB(-8, -140, 8, 0), paint(WHITE))
        c.drawRect(skia.Rect.MakeLTRB(-8, -140, 8, 0), paint(BLACK, stroke=3))
        c.restore()
    c.restore()
    c.restore()


def gloved_hand(c, x, y, s, T, rot=0.0, holding_glasses=True, beckon=0.0, flip=False):
    """A white cartoon glove on a black noodle, reaching out of the dark, dangling Mae's glasses."""
    T2 = twos(T)
    c.save()
    c.translate(x, y)
    c.scale(-s if flip else s, s)
    c.rotate(rot)
    wig = math.sin(T2 * 8) * 20 * beckon
    hose(c, -600, 0, -40, wig, bend=0.12, w=26)
    glove(c, 0, wig, 2.0, -10 + 25 * math.sin(T2 * 8) * beckon, point=beckon > 0.5)
    if holding_glasses:
        glasses(c, 20, wig + 110, 0.9, rot=12 * math.sin(T2 * 4))
    c.restore()

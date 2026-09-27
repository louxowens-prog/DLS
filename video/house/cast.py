"""The paper cast. Every figure is a cut-out (white scissor edge, matte fringe, drop shadow) moved like stop-motion.

HELPER  the chatbot: a floating porcelain doll's head with a pink bow and a sparkle halo - sweet until it isn't
CAT     a black cat that watches everything; its eyes glow red whenever the Helper says something false
YOU     the viewer as a paper doll in 1970s clothes, with a small mirror where the face should be
DOC, LAWYER, JUDGE, NEIGHBOR  the people in the true stories
"""
import math

import numpy as np
import skia

import hx
from hx import BLOOD, CREAM, INK, MINT, PEACH, PINK, PLUM, POWDER, WHITE, bez, paint, path, stop

PORCELAIN = (252, 234, 226)
PORC_SH = (232, 196, 196)
HAIR = (250, 222, 170)
HAIR_SH = (226, 186, 130)
BOW = (255, 120, 170)
EYE = (80, 150, 230)


def _eye(F, c, x, y, w, h, look, mood, blink, T):
    if blink and mood != "horror":
        c.drawPath(path(bez((x - w, y), (x, y + h * 0.5), (x + w, y)), closed=False), paint(INK, stroke=5))
        for k in range(4):
            lx = x - w * 0.6 + k * w * 0.4
            c.drawLine(lx, y + h * 0.18, lx - 4, y + h * 0.5, paint(INK, stroke=3))
        return
    white = path(np.vstack([bez((x - w, y), (x - w * 0.1, y - h * 1.1), (x + w, y - h * 0.15)),
                            bez((x + w, y - h * 0.15), (x, y + h * 0.9), (x - w, y))]))
    c.save()
    c.clipPath(white, doAntiAlias=True)
    if mood == "horror":
        c.drawPath(white, paint(INK))
        c.drawCircle(x + look[0] * w * 0.3, y - h * 0.1, h * 0.28, paint(BLOOD, blur=4))
        c.drawCircle(x + look[0] * w * 0.3, y - h * 0.1, h * 0.12, paint((255, 120, 90)))
    else:
        c.drawPath(white, paint(WHITE))
        ix, iy = x + look[0] * w * 0.35, y - h * 0.12 + look[1] * h * 0.2
        ir = h * (0.58 if mood == "sweet" else 0.36)
        c.drawCircle(ix, iy, ir, paint(shader=hx.rad((ix, iy - ir * 0.4), ir * 1.2, [(150, 210, 255), EYE, (90, 60, 170)])))
        c.drawCircle(ix, iy, ir * 0.42, paint(INK))
        hx.sparkle(c, ix - ir * 0.3, iy - ir * 0.35, ir * 0.55, T, seed=int(x), color=WHITE)
        c.drawCircle(ix + ir * 0.35, iy + ir * 0.3, ir * 0.14, paint(WHITE))
    c.restore()
    # lid, pink shadow above, long lashes flicking out
    c.drawPath(path(bez((x - w * 1.05, y - h * 0.1), (x - w * 0.1, y - h * 1.5), (x + w * 1.05, y - h * 0.3)), closed=False),
               paint((255, 150, 200), 0.55, stroke=h * 0.35))
    c.drawPath(path(bez((x - w, y), (x - w * 0.1, y - h * 1.1), (x + w, y - h * 0.15)), closed=False), paint(INK, stroke=6))
    for k in range(5):
        u = 0.35 + k * 0.15
        px = (1 - u) ** 2 * (x - w) + 2 * (1 - u) * u * (x - w * 0.1) + u ** 2 * (x + w)
        py = (1 - u) ** 2 * y + 2 * (1 - u) * u * (y - h * 1.1) + u ** 2 * (y - h * 0.15)
        c.drawLine(px, py, px + w * 0.18 + k * 3, py - h * 0.5 + k * 2, paint(INK, stroke=4))


def helper(c, x, y, s, T, talk=0.0, mood="sweet", look=(0.0, 0.0), halo=True, tilt=0.0, fringe=True, a=1.0):
    """The chatbot: a floating porcelain head (face ~260 px at s=1). mood: sweet / eerie / horror."""
    t8 = stop(T, 8)
    jx, jy, jr = hx.jit(T, 3.0, seed=11, fps=8)
    bob = 10 * math.sin(t8 * 2.2)
    blink = mood != "horror" and (int(t8 * 8) + 11) % 29 == 0
    c.save()
    c.translate(x + jx, y + jy + bob * s)
    c.rotate(tilt + jr)
    c.scale(s, s)
    if halo and mood != "horror":
        for i in range(7):
            ang = i * 2 * math.pi / 7 + t8 * 0.8
            hx.sparkle(c, 250 * math.cos(ang), -30 + 230 * math.sin(ang) * 0.85, 22 + 10 * (i % 3), T, seed=i, color=(255, 246, 210))
    with hx.figure(c, border=8, fringe=(-8, -4) if fringe else None, a=a) as F:
        # hair: ringlet bob, back layer
        for i in range(13):
            ang = math.pi * (0.95 + i / 12 * 1.1)
            F.circle(175 * math.cos(ang), -10 + 175 * math.sin(ang) * 0.95, 58, HAIR)
        F.oval(-190, -210, 190, 110, HAIR)
        for i in (-1, 1):                                        # ringlets hanging by the cheeks
            for k in range(3):
                F.circle(i * 168, 40 + k * 52, 36 - k * 4, HAIR)
        # face
        face = path(np.vstack([bez((-138, -60), (-150, 90), (-40, 150)), bez((-40, 150), (0, 168), (40, 150)),
                               bez((40, 150), (150, 90), (138, -60)), bez((138, -60), (0, -170), (-138, -60))]))
        F.fill(face, PORCELAIN, shader=hx.rad((-30, -40), 230, [(255, 246, 240), PORCELAIN, PORC_SH]))
        # bangs
        for i in range(7):
            bx = -150 + i * 50
            F.circle(bx, -118 + abs(i - 3) * 6, 50, HAIR)
        # the bow
        F.poly([(0, -196), (-110, -250), (-120, -150)], BOW)
        F.poly([(0, -196), (110, -250), (120, -150)], BOW)
        F.circle(0, -196, 30, (255, 90, 150))
    c.drawPath(path(bez((-150, -120), (-60, -150), (0, -110)), closed=False), paint(HAIR_SH, 0.7, stroke=6))
    # cheeks, nose
    for sx in (-1, 1):
        c.drawCircle(sx * 78, 58, 36, paint((255, 130, 160), 0.45, blur=10))
    c.drawPath(path(bez((-6, 40), (0, 56), (8, 44)), closed=False), paint(PORC_SH, stroke=4))
    for sx in (-1, 1):
        _eye(F, c, sx * 62, 6, 42, 38, look, mood, blink, T)
    if mood == "horror":                                         # the porcelain cracks and weeps paint
        c.drawPath(path([(-40, -150), (-20, -90), (-52, -40), (-30, 10)], closed=False), paint(INK, stroke=4))
        c.drawPath(path([(90, -100), (70, -60), (96, -20)], closed=False), paint(INK, stroke=3))
        for sx in (-1, 1):
            hx.drip(c, sx * 62, 30, 9, 60 + 30 * math.sin(t8 * 3 + sx), BLOOD)
    # mouth
    o = max(0.0, min(1.0, talk))
    if mood == "horror":
        m = path(np.vstack([bez((-96, 88), (0, 70), (96, 88)), bez((96, 88), (0, 200 + 40 * o), (-96, 88))]))
        c.drawPath(m, paint((60, 0, 10)))
        c.save()
        c.clipPath(m, doAntiAlias=True)
        for k in range(9):
            tx = -90 + k * 22
            c.drawPath(path([(tx, 80), (tx + 22, 80), (tx + 11, 116)]), paint(CREAM))
            c.drawPath(path([(tx + 6, 220), (tx + 28, 220), (tx + 17, 170 + 20 * o)]), paint(CREAM))
        c.restore()
        c.drawPath(m, paint(INK, stroke=4))
    elif o < 0.08:
        wide = 1.35 if mood == "eerie" else 1.0
        c.drawPath(path(np.vstack([bez((-26 * wide, 100), (-13, 90), (0, 98)), bez((0, 98), (13, 90), (26 * wide, 100)),
                                   bez((26 * wide, 100), (0, 122), (-26 * wide, 100))])), paint((220, 40, 80)))
    else:
        h = 14 + 34 * o
        m = path(np.vstack([bez((-28, 98), (0, 88), (28, 98)), bez((28, 98), (0, 98 + h * 1.4), (-28, 98))]))
        c.drawPath(m, paint((90, 10, 40)))
        c.save()
        c.clipPath(m, doAntiAlias=True)
        c.drawRect(skia.Rect.MakeLTRB(-30, 86, 30, 100), paint(WHITE))
        c.drawCircle(0, 98 + h * 1.2, 16, paint((255, 110, 140)))
        c.restore()
        c.drawPath(m, paint((220, 40, 80), stroke=6))
    c.restore()


def cat(c, x, y, s, T, eyes="gold", pose="sit", flip=False, fringe=True):
    """The black cat. eyes: gold (watching) or red (it knows that was false)."""
    t8 = stop(T, 8)
    jx, jy, jr = hx.jit(T, 2.0, seed=23, fps=8)
    c.save()
    c.translate(x + jx, y + jy)
    c.scale(-s if flip else s, s)
    c.rotate(jr * 0.5)
    fur = (22, 14, 26)
    with hx.figure(c, border=7, fringe=(-6, -3) if fringe else None) as F:
        swing = math.sin(t8 * 2.5) * 30
        F.stroke(path(bez((90, 150), (200 + swing, 120), (170 + swing, -10)), closed=False), fur, 30)
        if pose == "hiss":
            F.poly([(-120, 180), (-150, 40), (-60, -40), (70, -60), (140, 40), (130, 180)], fur)
        else:
            F.oval(-120, -10, 120, 190, fur)
        F.circle(0, -60, 88, fur)
        for sx in (-1, 1):
            F.poly([(sx * 30, -130), (sx * 82, -200), (sx * 86, -90)], fur)
    for sx in (-1, 1):
        c.drawPath(path([(sx * 42, -122), (sx * 74, -178), (sx * 76, -106)]), paint((90, 30, 70)))
    # eyes: glowing, slit pupils
    glow = BLOOD if eyes == "red" else (220, 255, 90)
    for sx in (-1, 1):
        ex, ey = sx * 36, -64
        c.drawCircle(ex, ey, 44, paint(glow, 0.55 if eyes == "red" else 0.35, blur=18))
        c.drawOval(skia.Rect.MakeLTRB(ex - 22, ey - 17, ex + 22, ey + 17), paint((255, 90, 70) if eyes == "red" else (230, 250, 120)))
        c.drawOval(skia.Rect.MakeLTRB(ex - 4, ey - 15, ex + 4, ey + 15), paint(INK))
        c.drawCircle(ex - 8, ey - 7, 4, paint(WHITE))
    c.drawPath(path([(-8, -28), (8, -28), (0, -18)]), paint((255, 150, 180)))
    for sx in (-1, 1):                                               # whiskers
        for k in range(3):
            c.drawLine(sx * 20, -20 + k * 8, sx * (110 + k * 6), -36 + k * 16, paint(CREAM, 0.8, stroke=2.5))
    if pose == "hiss":
        c.drawPath(path([(-30, -8), (30, -8), (18, 22), (-18, 22)]), paint((120, 0, 30)))
        for tx in (-18, 12):
            c.drawPath(path([(tx, -8), (tx + 8, -8), (tx + 4, 8)]), paint(WHITE))
    c.restore()


def you(c, x, y, s, T, pose="stand", fringe=True, shake=0.0, spots=0.0, mirror_red=False):
    """The viewer as a paper doll: 1970s orange turtleneck and brown flares, a mirror where the face would be.
    (x, y) is the head centre; the doll is ~900 px tall at s=1."""
    t8 = stop(T, 8)
    jx, jy, jr = hx.jit(T, 3.0 + 10 * shake, seed=37, fps=8)
    c.save()
    c.translate(x + jx, y + jy)
    c.rotate(jr * (1 + 4 * shake))
    c.scale(s, s)
    top, pants, hair, skin = (240, 120, 50), (120, 70, 40), (110, 60, 30), (250, 206, 176)
    arms = {"stand": ((100, 20), (80, -20)), "phone": ((150, 90), (40, -60)), "sprinkle": ((100, 20), (-20, -40)),
            "clutch": ((-150, -100), (-40, -120)), "run": ((150, 40), (20, -40)), "reach": ((100, 20), (-35, -10))}[pose]
    with hx.figure(c, border=7, fringe=(-7, -3) if fringe else None) as F:
        # legs (flares), walking if running
        sw = 0.5 * math.sin(t8 * 12) if pose == "run" else 0.0
        for sd, ph in ((-1, sw), (1, -sw)):
            hx0 = sd * 40
            kx, ky = hx0 + 300 * math.sin(ph) * 0.6, 470
            F.poly([(hx0 - 38, 300), (hx0 + 38, 300), (kx + 70, 760), (kx - 70, 760)], pants)
            F.oval(kx - 80, 740, kx + 70, 790, (80, 40, 30))
        # torso: turtleneck
        F.fill(path(np.vstack([bez((-60, 110), (-150, 120), (-140, 220)), [(-110, 330), (110, 330)], bez((140, 220), (150, 120), (60, 110))])), top)
        F.rrect(-50, 70, 50, 130, 18, (220, 100, 40))
        # arms: shoulder -> elbow -> hand (angles in degrees, 90 = down)
        for sd, (sa, ea) in zip((-1, 1), arms):
            if sd < 0:
                sa, ea = 180 - sa, 180 - ea
            sx_, sy_ = sd * 118, 150
            ex_, ey_ = sx_ + 120 * math.cos(math.radians(sa)), sy_ + 120 * math.sin(math.radians(sa))
            hx_, hy_ = ex_ + 110 * math.cos(math.radians(ea)), ey_ + 110 * math.sin(math.radians(ea))
            F.stroke(path([(sx_, sy_), (ex_, ey_), (hx_, hy_)], closed=False), top, 46)
            F.circle(hx_, hy_, 26, skin)
        # hair: a 70s shag
        F.oval(-120, -150, 120, 90, hair)
        for i in range(9):
            ang = math.pi * (0.9 + i / 8 * 1.2)
            F.circle(118 * math.cos(ang), -20 + 118 * math.sin(ang), 42, hair)
        # the face is a mirror
        F.oval(-86, -110, 86, 96, (200, 210, 225), shader=hx.lin((-86, -110), (86, 96), [(245, 250, 255), (170, 185, 205), (230, 236, 245)]))
    c.drawPath(path([(-50, -90), (-10, -100), (50, 70), (10, 80)]), paint(WHITE, 0.55))
    c.drawOval(skia.Rect.MakeLTRB(-86, -110, 86, 96), paint((150, 150, 160), stroke=6))
    if mirror_red:
        c.drawOval(skia.Rect.MakeLTRB(-80, -104, 80, 90), paint(BLOOD, 0.55))
    if spots > 0:                                                    # the skin breaking out (hands, neck)
        rng = np.random.default_rng(5)
        for _ in range(int(26 * spots)):
            c.drawCircle(rng.uniform(-48, 48), rng.uniform(66, 128), rng.uniform(5, 10), paint((220, 60, 80), 0.95))
    c.restore()


def doctor(c, x, y, s, T, talk=0.0):
    """A 1970s doctor: head mirror, horn-rims, moustache, white coat, clipboard. (x, y) = head centre."""
    jx, jy, jr = hx.jit(T, 2.0, seed=41, fps=8)
    c.save()
    c.translate(x + jx, y + jy)
    c.rotate(jr * 0.6)
    c.scale(s, s)
    skin = (240, 196, 160)
    with hx.figure(c) as F:
        F.fill(path(np.vstack([bez((-70, 120), (-230, 150), (-250, 330)), [(-260, 700), (260, 700)], bez((250, 330), (230, 150), (70, 120))])), (246, 246, 240))
        F.poly([(-50, 118), (50, 118), (0, 240)], (150, 200, 230))
        F.rrect(-60, 60, 60, 140, 20, skin)
        F.oval(-110, -150, 110, 120, skin)
        F.oval(-118, -170, 118, -40, (120, 110, 100))
        F.rrect(90, 250, 250, 480, 12, (190, 150, 90))
    c.drawRect(skia.Rect.MakeLTRB(110, 280, 230, 290), paint(INK))
    for k in range(5):
        c.drawRect(skia.Rect.MakeLTRB(110, 310 + k * 30, 200 + (k * 17) % 30, 318 + k * 30), paint(INK, 0.7))
    c.drawRect(skia.Rect.MakeLTRB(-118, -118, 118, -104), paint((60, 60, 60)))                 # head band
    c.drawCircle(0, -112, 48, paint(shader=hx.rad((-10, -125), 60, [(255, 255, 255), (170, 180, 190), (110, 115, 125)])))
    c.drawCircle(0, -112, 48, paint(INK, stroke=4))
    c.drawCircle(0, -112, 10, paint(INK))
    for sx in (-1, 1):
        c.drawOval(skia.Rect.MakeLTRB(sx * 50 - 34, -30, sx * 50 + 34, 20), paint((60, 30, 20), stroke=7))
        c.drawCircle(sx * 50, -6, 7, paint(INK))
    c.drawLine(-16, -8, 16, -8, paint((60, 30, 20), stroke=6))
    c.drawPath(path(np.vstack([bez((-60, 50), (0, 20), (60, 50)), bez((60, 50), (0, 70), (-60, 50))])), paint((110, 80, 60)))
    o = max(0.0, min(1.0, talk))
    c.drawOval(skia.Rect.MakeLTRB(-22, 64, 22, 70 + 26 * o), paint((90, 20, 30)))
    c.restore()


def suit_man(c, x, y, s, T, suit=(150, 100, 60), tie=(200, 120, 40), hair=(70, 40, 20), paper=True, seed=0, face_mood="smug"):
    """A 1970s lawyer: wide lapels, wide tie, sideburns, a sheaf of papers. (x, y) = head centre."""
    jx, jy, jr = hx.jit(T, 2.5, seed=53 + seed, fps=8)
    c.save()
    c.translate(x + jx, y + jy)
    c.rotate(jr)
    c.scale(s, s)
    skin = (238, 190, 150)
    with hx.figure(c) as F:
        F.fill(path(np.vstack([bez((-60, 110), (-200, 130), (-210, 300)), [(-220, 640), (220, 640)], bez((210, 300), (200, 130), (60, 110))])), suit)
        F.poly([(-40, 110), (40, 110), (0, 260)], (240, 236, 220))
        F.poly([(-14, 120), (14, 120), (26, 330), (0, 360), (-26, 330)], tie)
        F.rrect(-55, 50, 55, 130, 18, skin)
        F.oval(-100, -140, 100, 110, skin)
        F.oval(-110, -160, 110, -30, hair)
        for sx in (-1, 1):
            F.rrect(sx * 100 - 16, -60, sx * 100 + 16, 40, 10, hair)
        if paper:
            F.rrect(120, 230, 280, 440, 6, (252, 250, 240))
    for sx in (-1, 1):
        c.drawCircle(sx * 40, -10, 9, paint(INK))
        c.drawLine(sx * 40 - 22, -36, sx * 40 + 22, -40 + sx * 4, paint(hair, stroke=8))
    if face_mood == "smug":
        c.drawPath(path(bez((-30, 60), (0, 76), (34, 54)), closed=False), paint((120, 50, 40), stroke=6))
    else:
        c.drawOval(skia.Rect.MakeLTRB(-18, 50, 18, 90), paint((90, 20, 30)))
    for sx in (-1, 1):                                                # lapels
        c.drawPath(path([(sx * 40, 110), (sx * 130, 140), (sx * 60, 330)]), paint(hx.mix(suit, INK, 0.25)))
    if paper:
        for k in range(6):
            c.drawRect(skia.Rect.MakeLTRB(135, 255 + k * 28, 265 - (k * 13) % 40, 262 + k * 28), paint(INK, 0.55))
    c.restore()


def judge(c, x, y, s, T, gavel=0.0):
    """A judge in a black robe behind the bench, gavel raised (gavel 0..1 = up..down)."""
    jx, jy, jr = hx.jit(T, 2.0, seed=61, fps=8)
    c.save()
    c.translate(x + jx, y + jy)
    c.scale(s, s)
    skin = (236, 196, 170)
    with hx.figure(c) as F:
        F.fill(path(np.vstack([bez((-60, 110), (-220, 130), (-230, 300)), [(-240, 520), (240, 520)], bez((230, 300), (220, 130), (60, 110))])), (26, 20, 30))
        F.oval(-100, -140, 100, 110, skin)
        F.oval(-116, -150, 116, -20, (220, 220, 225))
        ang = math.radians(-60 + 90 * gavel)
        hxp, hyp = 220 + 160 * math.cos(ang), 200 + 160 * math.sin(ang)
        F.stroke(path([(220, 200), (hxp, hyp)], closed=False), (120, 70, 30), 18)
        c.save()
        c.translate(hxp, hyp)
        c.rotate(math.degrees(ang) + 90)
        F.rrect(-60, -26, 60, 26, 10, (140, 80, 36))
        c.restore()
    for sx in (-1, 1):
        c.drawCircle(sx * 40, -6, 8, paint(INK))
        c.drawLine(sx * 40 - 22, -30, sx * 40 + 22, -26, paint((160, 160, 170), stroke=7))
    c.drawPath(path(bez((-30, 60), (0, 50), (30, 60)), closed=False), paint((120, 50, 40), stroke=6))
    c.restore()


def neighbor(c, x, y, s, T, mood="sweet"):
    """The neighbour, as seen by a poisoned mind: a grinning face floating in the window across the street."""
    jx, jy, jr = hx.jit(T, 4.0, seed=71, fps=8)
    c.save()
    c.translate(x + jx, y + jy)
    c.rotate(jr * 2)
    c.scale(s, s)
    skin = (230, 220, 190)
    with hx.figure(c, fringe_col=(255, 60, 80)) as F:
        F.oval(-110, -140, 110, 130, skin)
        F.oval(-140, -170, 140, -90, (60, 40, 40))
        F.rrect(-80, -240, 80, -120, 14, (60, 40, 40))
    for sx in (-1, 1):
        c.drawCircle(sx * 44, -20, 22, paint(WHITE))
        c.drawCircle(sx * 44 + 4, -18, 10 if mood == "sweet" else 6, paint(BLOOD if mood != "sweet" else INK))
    c.drawPath(path(np.vstack([bez((-80, 50), (0, 40), (80, 50)), bez((80, 50), (0, 120), (-80, 50))])), paint((80, 10, 20)))
    for k in range(7):
        c.drawRect(skia.Rect.MakeLTRB(-70 + k * 20, 50, -58 + k * 20, 66), paint(CREAM))
    c.restore()


# ------------------------------------------------------------------ props

def cuckoo_clock(c, x, y, s, T, count, mood="sweet", bird=0.0, glow=0.0):
    """The motif: a carved cuckoo clock whose pendulum window counts confident wrong answers."""
    jx, jy, _ = hx.jit(T, 1.5, seed=83, fps=8)
    c.save()
    c.translate(x + jx, y + jy)
    c.scale(s, s)
    wood, dark = ((150, 90, 60), (90, 50, 36)) if mood != "horror" else ((110, 20, 30), (50, 0, 10))
    with hx.figure(c) as F:
        F.poly([(-230, -120), (0, -300), (230, -120)], dark)
        F.rrect(-190, -140, 190, 260, 18, wood)
        for sx in (-1, 1):
            for k in range(4):
                F.poly([(sx * 150, -180 - k * 18), (sx * 250, -120 - k * 18), (sx * 170, -130 - k * 18)], (90, 140, 70) if mood != "horror" else (80, 0, 10))
        F.rrect(-70, 260, 70, 330, 10, dark)
        sw = math.sin(stop(T, 8) * 5) * 18
        F.stroke(path([(0, 320), (sw, 520)], closed=False), (200, 160, 60), 8)
        F.circle(sw, 540, 34, (220, 180, 70))
    # the little door and the bird
    c.drawRect(skia.Rect.MakeLTRB(-40, -250, 40, -170), paint(INK))
    if bird > 0:
        by = -210
        bx = 60 * bird
        c.drawCircle(bx, by, 34, paint((255, 170, 200)))
        c.drawPath(path([(bx + 30, by - 8), (bx + 64, by), (bx + 30, by + 8)]), paint(hx.GOLD))
        c.drawCircle(bx + 10, by - 10, 6, paint(INK))
    # face
    c.drawCircle(0, 0, 118, paint(CREAM))
    c.drawCircle(0, 0, 118, paint(dark, stroke=8))
    for k in range(12):
        a = math.radians(k * 30)
        c.drawLine(96 * math.cos(a), 96 * math.sin(a), 110 * math.cos(a), 110 * math.sin(a), paint(INK, stroke=5))
    hand = stop(T, 8) * 6
    c.drawLine(0, 0, 80 * math.cos(hand), 80 * math.sin(hand), paint(INK, stroke=6))
    c.drawLine(0, 0, 50 * math.cos(hand / 12), 50 * math.sin(hand / 12), paint(INK, stroke=9))
    # the counter plaque
    big = 1.0 if s >= 1.0 else 1.0 + 0.5 * min(1.0, (1.0 - s) / 0.6)    # small clocks get a bigger, readable counter
    plq = skia.Rect.MakeLTRB(-170 * big, 140, 170 * big, 140 + 94 * big)
    c.drawRect(plq, paint(INK))
    c.drawRect(plq, paint((230, 190, 90), stroke=6))
    if glow > 0:
        c.drawRect(plq, paint(BLOOD, 0.5 * glow, blur=16))
    s_ = f"{int(count):,}"
    hx.text(c, s_, 0, 140 + 70 * big, 66 * big, "fell-sc-400", (255, 90, 80) if mood == "horror" else (255, 230, 170), tag="counter")
    c.restore()


def phone(c, x, y, s, T, lines=(), who=(), rot=0.0, typed=1.0):
    """A pastel phone held up to the camera, with a chat on it. lines: [(text, 'you'|'ai')]."""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    with hx.figure(c) as F:
        F.rrect(-230, -420, 230, 420, 50, (255, 200, 220))
        F.rrect(-200, -360, 200, 360, 20, (250, 246, 240))
    c.drawCircle(0, 388, 16, paint((230, 160, 190)))
    y0 = -250
    for i, (t, w) in enumerate(lines):
        f = hx.font("special-elite-400", 40)
        ls = hx.wrap(t, f, 300) or [" "]
        bh = 50 * len(ls) + 28
        x0 = -180 if w == "ai" else 180 - max(f.measureText(l) for l in ls) - 30
        bw = max(f.measureText(l) for l in ls) + 30
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0, y0, bw, bh), 18, 18), paint((255, 225, 235) if w == "ai" else (200, 235, 220)))
        for j, l in enumerate(ls):
            hx.text(c, l, x0 + 15, y0 + 50 + j * 50, 40, "special-elite-400", INK, align="left", tag="phone")
        y0 += bh + 20
    c.restore()


def shaker(c, x, y, s, T, label="SALT", mood="sweet", teeth=0.0, fill=(250, 250, 250)):
    """A salt shaker that comes alive: in the horror it grows eyes and a mouth full of teeth."""
    jx, jy, jr = hx.jit(T, 3.0 + 8 * teeth, seed=91, fps=8)
    c.save()
    c.translate(x + jx, y + jy)
    c.rotate(jr * (1 + 3 * teeth))
    c.scale(s, s)
    with hx.figure(c) as F:
        F.rrect(-90, -120, 90, 180, 40, (220, 240, 250))
        F.fill(path(np.vstack([bez((-90, -110), (0, -250), (90, -110))])), (200, 200, 210))
    c.drawRect(skia.Rect.MakeLTRB(-84, 40, 84, 176), paint(fill, 0.95))
    for k in range(5):
        c.drawCircle(-40 + k * 20, -150 + (k % 2) * 10, 5, paint(INK))
    hx.text(c, label, 0, 20, 44, "shrikhand-400", PLUM, tag="prop")
    if teeth > 0:
        for sx in (-1, 1):
            c.drawCircle(sx * 34, -60, 18, paint(WHITE))
            c.drawCircle(sx * 34, -58, 9, paint(BLOOD))
        m = path(np.vstack([bez((-70, 80), (0, 60), (70, 80)), bez((70, 80), (0, 80 + 110 * teeth), (-70, 80))]))
        c.drawPath(m, paint((60, 0, 10)))
        for k in range(6):
            tx = -64 + k * 22
            c.drawPath(path([(tx, 74), (tx + 20, 74), (tx + 10, 100)]), paint(CREAM))
    c.restore()


def jar(c, x, y, s, T, label="NaBr", sub="SODIUM BROMIDE"):
    jx, jy, jr = hx.jit(T, 2.0, seed=97, fps=8)
    c.save()
    c.translate(x + jx, y + jy)
    c.rotate(jr)
    c.scale(s, s)
    with hx.figure(c) as F:
        F.rrect(-120, -150, 120, 200, 30, (240, 244, 250))
        F.rrect(-110, -200, 110, -140, 12, (40, 120, 200))
    c.drawRect(skia.Rect.MakeLTRB(-120, -60, 120, 110), paint((255, 250, 220)))
    hx.text(c, label, 0, 20, 70, "shrikhand-400", (40, 120, 200), tag="prop")
    hx.text(c, sub, 0, 80, 28, "special-elite-400", INK, tag="prop")
    c.restore()

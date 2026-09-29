"""The people, drawn like a 1985 art film lights them: mostly silhouettes against a single source, a rim of light
on the lit side, and one close profile of her face by the lamp.

  profile(c, ...)        her face in profile (facing right), lit by the lamp or the laptop; moods worry/focus/smile/tear
  seated(c, ...)         a woman at a table, in profile, typing or writing (medium shot), mostly silhouette
  child_back(c, ...)     a pupil from behind (head, hair, shoulders), for the rows of the classroom
  teacher(c, ...)        a woman at the blackboard, writing or turned to the class
  sil_profile(c, ...)    a seated profile silhouette (the tutor and the boy across the street)
  robed(c, ...)          the stage figures of the fiction register: tall, robed, masked, in lacquer colours
  learner(c, ...)        the plain white figure who stands for any learner on the stage
All figures are drawn with their feet (or seat) at (x, y); s scales them.
"""
import math

import numpy as np
import skia

import draw as D
from draw import GOLD, GOLDL, HAIR, INK, SKIN, SKIN2, WHITE, mix, paint, path


def _grad_fill(c, p, x0, x1, c0, c1, a=1.0):
    c.drawPath(p, paint(shader=D.lin((x0, 0), (x1, 0), [c0, c1]), a=a))


# ------------------------------------------------------------------ her face, close, in profile

def profile(c, x, y, s, T, mood="focus", light="lamp", blink=True, breathe=True, tear=0.0, look=0.0):
    """Her head and shoulders in profile, facing right; (x, y) is the centre of the head. ~s * 260 px tall head.
    light: 'lamp' (warm, from the front) or 'screen' (cool, from the front and below)."""
    c.save()
    c.translate(x, y + (1.5 * math.sin(T * 1.6) * s if breathe else 0))
    c.scale(s, s)
    lit = {"lamp": (250, 206, 164), "screen": (206, 214, 228), "day": (238, 214, 192)}[light]
    shadow = {"lamp": (70, 46, 38), "screen": (40, 44, 58), "day": (110, 84, 72)}[light]
    # shoulders and a dark sweater
    body = D.smooth([(-230, 420), (-190, 250), (-70, 175), (40, 170), (130, 230), (190, 420)])
    _grad_fill(c, body, 200, -200, mix((60, 58, 66), lit, 0.18), (18, 16, 20))
    # neck
    neck = path([(-42, 70), (36, 88), (44, 200), (-58, 206)])
    _grad_fill(c, neck, 60, -60, mix(lit, SKIN2, 0.35), mix(shadow, INK, 0.3))
    # the face: forehead, brow, nose, lips, chin, jaw, back to the nape
    face = D.smooth([(-60, -96), (8, -118), (54, -92), (70, -54), (72, -34), (71, -22), (84, -4), (99, 12), (86, 21),
                     (80, 27), (84, 34), (78, 41), (82, 48), (76, 55), (71, 62), (76, 78), (62, 94), (30, 104),
                     (-6, 94), (-40, 72), (-78, 10)])
    _grad_fill(c, face, 100, -70, lit, shadow)
    # a soft cheek, and light catching the front edge
    c.drawCircle(38, 30, 26, paint((236, 150, 130) if light == "lamp" else (190, 170, 190), 0.18, blur=10))
    c.save()
    c.clipPath(face, doAntiAlias=True)
    c.drawPath(face, paint(mix(lit, WHITE, 0.4), 0.5, stroke=5, blur=2))
    c.restore()
    # ear (half under the hair)
    c.drawOval(skia.Rect.MakeLTRB(-32, -18, 0, 26), paint(mix(lit, shadow, 0.55)))
    c.drawArc(skia.Rect.MakeLTRB(-27, -12, -5, 20), -60, 200, False, paint(mix(shadow, INK, 0.3), 0.6, stroke=3))
    # the eye, open or closed
    shut = blink and (int(T * 7.3 + 3) % 29 == 0)
    ey, ex = -24, 50
    if shut or mood == "closed":
        c.drawLine(ex - 10, ey + 2, ex + 12, ey + 3, paint((40, 26, 22), stroke=3.5))
    else:
        lid = {"focus": 0.8, "worry": 0.9, "smile": 0.7, "tear": 0.85}.get(mood, 0.9)
        eye = D.smooth([(ex - 10, ey), (ex + 6, ey - 7 * lid), (ex + 14, ey - 2), (ex + 13, ey + 5), (ex, ey + 6)])
        c.drawPath(eye, paint((232, 224, 220)))
        c.save()
        c.clipPath(eye, doAntiAlias=True)
        c.drawCircle(ex + 9 + 2 * look, ey, 6.5, paint((62, 42, 30)))
        c.drawCircle(ex + 10 + 2 * look, ey, 3.2, paint((10, 8, 8)))
        c.restore()
        c.drawCircle(ex + 12 + 2 * look, ey - 2, 1.6, paint(WHITE, 0.9))
        c.drawPath(D.smooth([(ex - 12, ey - 1), (ex + 4, ey - 9 * lid), (ex + 15, ey - 3)], closed=False),
                   paint((30, 20, 18), stroke=3.5))
        if mood == "tear" or tear > 0:
            k = max(tear, 0.6 if mood == "tear" else 0.0)
            c.drawCircle(ex + 8, ey + 8, 3.0, paint(WHITE, 0.8 * k))
            c.drawLine(ex + 6, ey + 10, ex + 2, ey + 10 + 40 * k, paint(WHITE, 0.35 * k, stroke=2.5))
    # brow
    by = {"worry": -44, "focus": -41, "smile": -45, "tear": -46}.get(mood, -43)
    tilt = {"worry": 5, "focus": 2, "smile": -1}.get(mood, 0)
    c.drawPath(D.smooth([(ex - 16, by + tilt), (ex + 2, by - 4), (ex + 18, by - tilt)], closed=False), paint(HAIR, stroke=6))
    # nostril and lips
    c.drawPath(D.smooth([(86, 15), (80, 18), (83, 21)], closed=False), paint(mix(shadow, INK, 0.2), 0.7, stroke=2.5))
    lip = mix((170, 90, 86), lit, 0.2)
    up = -4 if mood == "smile" else 0
    c.drawPath(D.smooth([(70, 40 + up), (82, 34), (84, 41), (80, 43)]), paint(lip))
    c.drawPath(D.smooth([(72, 44), (81, 44), (79, 50), (73, 49)]), paint(mix(lip, lit, 0.2)))
    c.drawLine(68, 41 + up, 82, 42, paint(mix(shadow, INK, 0.3), stroke=2))
    if mood == "smile":
        c.drawPath(D.smooth([(60, 30), (64, 38), (66, 44)], closed=False), paint(mix(shadow, lit, 0.4), 0.5, stroke=2.5))
    # hair: dark, pinned low at the nape, a loose strand by the cheek
    hair = D.smooth([(62, -80), (40, -112), (-20, -126), (-86, -100), (-116, -40), (-118, 30), (-96, 88), (-56, 118),
                     (-34, 96), (-44, 50), (-30, 0), (-12, -40), (20, -70)])
    _grad_fill(c, hair, 60, -120, mix(HAIR, lit, 0.22), (12, 10, 10))
    c.drawCircle(-104, 70, 40, paint((16, 12, 12)))                                       # the knot at the nape
    c.drawPath(D.smooth([(-40, -116), (10, -114), (50, -90)], closed=False), paint(mix(HAIR, lit, 0.4), 0.35, stroke=6, blur=2))
    c.restore()


# ------------------------------------------------------------------ a woman at a table (medium shot)

def union(*ps):
    out = ps[0]
    for p_ in ps[1:]:
        r = skia.Op(out, p_, skia.PathOp.kUnion_PathOp)
        out = r if r is not None else out
    return out


def _rim(c, shape, lit, sil, amt, dx=-9, dy=3):
    """Fill a shape with light, then cover all but a thin edge on the lit (+x) side with the silhouette."""
    c.save()
    c.clipPath(shape, doAntiAlias=True)
    c.drawPath(shape, paint(lit, amt))
    c.translate(dx, dy)
    c.drawPath(shape, paint(sil))
    c.restore()


def seated(c, x, y, s, T, action="type", lit=(255, 208, 140), side=1, rim=1.0, sil=(20, 18, 22), head_tilt=8):
    """Seated at a table in profile, facing +x (side=1) or -x; (x, y) is the floor under the chair.
    Mostly silhouette, with a rim of light on the side toward the table (the lamp, the screen). ~s * 720 px tall."""
    c.save()
    c.translate(x, y)
    c.scale(s * side, s)
    k = math.sin(T * 11) if action == "type" else 0.5 * math.sin(T * 4)
    chair = mix(sil, (60, 56, 60), 0.35)
    c.drawRect(skia.Rect.MakeLTRB(-110, -270, 80, -245), paint(chair))                   # seat
    c.drawRect(skia.Rect.MakeLTRB(-110, -640, -86, 0), paint(chair))                    # back post and rear leg
    c.drawRect(skia.Rect.MakeLTRB(56, -250, 80, 0), paint(chair))                       # front leg
    parts = []
    thigh = D.capsule(-40, -300, 150, -300, 86, 70)
    shin = D.capsule(150, -300, 160, -30, 62, 50)
    shoe = D.rrect(120, -40, 240, 0, 18)
    torso = D.smooth([(-86, -270), (-84, -420), (-56, -540), (-10, -600), (46, -596), (70, -540), (56, -420), (40, -290)])
    neck = D.capsule(20, -590, 44, -650, 44, 40)
    c.save()
    c.translate(70, -700)
    c.rotate(head_tilt)
    head = D.smooth([(-50, -10), (-40, -60), (0, -78), (40, -64), (52, -34), (54, -20), (68, -2), (56, 6), (58, 16),
                     (52, 28), (46, 44), (20, 54), (-20, 46), (-44, 22)])
    m = c.getTotalMatrix()
    c.restore()
    head.transform(m.preConcat(skia.Matrix()) if False else skia.Matrix.Translate(70, -700).preConcat(skia.Matrix.RotateDeg(head_tilt)))
    bun = D.circle(-6, -704, 30)
    upper = D.capsule(10, -560, 80, -430, 50, 42)
    fore = D.capsule(80, -430, 200 + 6 * k, -392 + 3 * abs(k), 40, 30)
    whole = union(shin, shoe, thigh, torso, neck, head, bun, upper, fore)
    c.drawPath(whole, paint(sil))
    if rim:
        _rim(c, whole, lit, sil, rim, dx=-6, dy=2)
    c.restore()


# ------------------------------------------------------------------ the classroom

def child_back(c, x, y, s, hair=(30, 28, 28), shirt=(200, 200, 196), hand=0.0, seed=0, T=0.0):
    """A pupil seen from behind at a desk: shoulders, collar, head of hair; (x, y) is the desk-top line."""
    rng = np.random.default_rng(seed)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    w = rng.uniform(0.9, 1.1)
    c.drawPath(D.smooth([(-70 * w, 10), (-62 * w, -60), (-30, -84), (30, -84), (62 * w, -60), (70 * w, 10)]), paint(shirt))
    c.drawPath(path([(-22, -84), (0, -64), (22, -84)]), paint(mix(shirt, WHITE, 0.4)))
    c.drawOval(skia.Rect.MakeLTRB(-34, -150, 34, -74), paint(mix(hair, (220, 180, 150), 0.25)))
    style = seed % 3
    if style == 0:
        c.drawPath(D.smooth([(-38, -100), (-30, -150), (0, -162), (30, -150), (38, -100), (0, -86)]), paint(hair))
    elif style == 1:
        c.drawPath(D.smooth([(-40, -60), (-36, -146), (0, -164), (36, -146), (40, -60), (0, -80)]), paint(hair))
    else:
        c.drawPath(D.smooth([(-36, -104), (-30, -150), (0, -164), (30, -150), (36, -104), (0, -96)]), paint(hair))
        c.drawCircle(0, -168, 16, paint(hair))
    if hand > 0:                                                        # an arm going up
        a = hand
        c.drawPath(D.capsule(40, -70, 60 + 10 * a, -70 - 150 * a, 30, 24), paint(shirt))
        c.drawCircle(60 + 10 * a, -76 - 160 * a, 18, paint((220, 190, 170)))
    c.restore()


def teacher(c, x, y, s, T, pose="write"):
    """The teacher: a woman in a long skirt and cardigan, hair in a bun; writing at the board, or turned to us."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    skirt, cardi, skin, hair = (60, 60, 64), (120, 118, 116), (214, 196, 184), (40, 36, 34)
    c.drawPath(path([(-70, -420), (70, -420), (100, 0), (-100, 0)]), paint(skirt))
    c.drawPath(D.smooth([(-70, -420), (-78, -600), (-40, -690), (40, -690), (78, -600), (70, -420)]), paint(cardi))
    c.drawRect(skia.Rect.MakeLTRB(-16, -730, 16, -684), paint(skin))
    if pose == "write":                                                 # back to us, arm up at the board
        c.drawOval(skia.Rect.MakeLTRB(-46, -820, 46, -716), paint(hair))
        c.drawCircle(0, -824, 26, paint(hair))
        c.drawPath(D.capsule(50, -660, 120, -800 + 20 * math.sin(T * 5), 34, 28), paint(cardi))
        c.drawPath(D.capsule(-50, -660, -70, -470, 34, 28), paint(cardi))
    else:                                                               # turned to the class
        c.drawOval(skia.Rect.MakeLTRB(-44, -816, 44, -716), paint(skin))
        c.drawPath(D.smooth([(-48, -760), (-44, -820), (0, -836), (44, -820), (48, -760), (30, -800), (-30, -800)]), paint(hair))
        c.drawCircle(0, -838, 22, paint(hair))
        for sx in (-1, 1):
            c.drawCircle(sx * 16, -770, 4.5, paint((40, 36, 34)))
        c.drawLine(-10, -738, 10, -738, paint((120, 80, 76), stroke=4))
        c.drawPath(D.capsule(-50, -660, -60, -470, 34, 28), paint(cardi))
        c.drawPath(D.capsule(50, -660, 64, -470, 34, 28), paint(cardi))
    c.restore()


def sil_profile(c, x, y, s, side=1, kind="adult", color=(12, 12, 14)):
    """A seated profile silhouette at a desk (the tutor, the boy): (x, y) is the seat line."""
    c.save()
    c.translate(x, y)
    c.scale(s * side, s * (0.78 if kind == "boy" else 1.0))
    p = paint(color)
    c.drawPath(D.smooth([(-60, 0), (-64, -150), (-40, -260), (10, -290), (40, -250), (56, -130), (70, -90), (160, -80),
                         (160, -40), (40, -30), (30, 0)]), p)
    c.drawPath(D.smooth([(-10, -300), (-6, -360), (30, -390), (74, -372), (86, -336), (98, -318), (86, -304), (88, -292),
                         (78, -280), (40, -268), (4, -276)]), p)
    if kind == "adult":
        c.drawCircle(-6, -340, 22, p)
    c.restore()


# ------------------------------------------------------------------ the stage figures (fiction)

def robed(c, x, y, s, T, body=(206, 48, 34), trim=GOLD, face=(244, 236, 214), hat=None, arms=0.0, sway=True):
    """A tall stage figure in a stiff robe, masked face, arms that can open (0..1). (x, y) = the hem."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    if sway:
        c.rotate(1.2 * math.sin(T * 0.9 + x * 0.01))
    robe = path([(-60, -560), (60, -560), (150, 0), (-150, 0)])
    c.drawPath(robe, paint(shader=D.lin((-150, 0), (150, 0), [mix(body, INK, 0.3), body, mix(body, INK, 0.45)])))
    for j in range(6):                                                  # gold bands on the hem
        yy = -40 - j * 12
        c.drawLine(-140 + j * 3, yy, 140 - j * 3, yy, paint(trim, 0.9 if j % 2 == 0 else 0.4, stroke=5))
    c.drawPath(path([(-12, -560), (12, -560), (40, 0), (-40, 0)]), paint(trim, 0.85))
    for sx in (-1, 1):                                                  # the sleeves open like wings
        a = math.radians(20 + 70 * arms)
        tip = (sx * (60 + 230 * math.sin(a)), -520 + 230 * math.cos(a))
        c.drawPath(path([(sx * 50, -540), (sx * 70, -470), tip, (tip[0] + sx * 30, tip[1] - 60)]), paint(mix(body, INK, 0.15)))
        c.drawLine(sx * 60, -500, tip[0], tip[1], paint(trim, 0.8, stroke=4))
    c.drawOval(skia.Rect.MakeLTRB(-40, -660, 40, -556), paint(face))
    c.drawLine(-20, -610, -6, -612, paint(INK, stroke=4))
    c.drawLine(6, -612, 20, -610, paint(INK, stroke=4))
    c.drawLine(-6, -580, 6, -580, paint(body, stroke=4))
    if hat == "crown":
        c.drawPath(path([(-44, -650), (-44, -700), (-22, -676), (0, -712), (22, -676), (44, -700), (44, -650)]), paint(trim))
    elif hat == "cap":
        c.drawPath(D.smooth([(-46, -640), (-30, -690), (30, -690), (46, -640)]), paint(INK))
    c.restore()


def learner(c, x, y, s, T, color=(244, 240, 232), glow=0.0, pose="stand"):
    """The plain white figure: any learner. (x, y) = feet. pose: stand / sit / reach / kneel."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    if glow > 0:
        c.drawCircle(0, -300, 260, paint((255, 230, 170), 0.25 * glow, blur=80))
    p = paint(color)
    if pose == "sit":
        c.drawPath(D.smooth([(-50, -300), (-40, -420), (0, -450), (40, -420), (54, -300), (130, -290), (130, -250), (-50, -240)]), p)
        c.drawCircle(0, -500, 44, p)
    else:
        c.drawPath(path([(-44, -460), (44, -460), (80, 0), (-80, 0)]), p)
        c.drawCircle(0, -512, 46, p)
        if pose == "reach":
            c.drawPath(D.capsule(30, -440, 150, -620, 30, 22), p)
        elif pose == "kneel":
            pass
        else:
            for sx in (-1, 1):
                c.drawPath(D.capsule(sx * 40, -440, sx * 70, -250, 28, 22), p)
    c.restore()

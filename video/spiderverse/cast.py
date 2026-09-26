"""The cast, each drawn in its own dimension's style, all animated on twos.

HERO   the narrator: a graffiti writer in the main comic style - flat colour, halftone and hatched shadows,
       magenta/cyan rim light from the neon, tapered ink contours
NOIR   the skeptic: black and white only, deep shadow, cross-hatching, rain
ANIME  the believer: cel-shaded (hard two-tone), giant sparkling eyes, blush, sparkles
BOT    the AI: a flat, bouncy cartoon with pie-cut eyes and rubber-hose arms
"""
import math

import numpy as np
import skia

import sv
from sv import CYAN, INK, MAG, WHITE, YEL, bez, paint, path, twos

HOOD = (116, 46, 200)
HOOD_D = (74, 26, 146)
HAIR = (46, 16, 58)
SKIN = (160, 98, 66)
LIP = (132, 44, 78)
CAN = (0, 205, 255)
DENIM = (44, 64, 160)
SHOE = (255, 255, 255)


def _stroke(c, pts, w, color=INK, a=1.0):
    c.drawPath(path(pts, closed=False), paint(color, a, stroke=w))


def _rim(P, pth, color, dx, w=16, side=None, a=1.0):
    """A coloured rim light inside the silhouette, on the side the neon comes from."""
    c = P.c
    c.save()
    c.clipPath(pth, doAntiAlias=True)
    if side is not None:
        c.clipRect(side)
    c.translate(dx, 0)
    c.drawPath(pth, paint(color, a, stroke=w))
    c.restore()


def _shade(P, name, clip, shape, a=0.6):
    cv = P.sh[name]
    cv.save()
    cv.clipPath(clip, doAntiAlias=True)
    cv.drawPath(shape, paint(WHITE, a))
    cv.restore()


# ------------------------------------------------------------------ HERO: the narrator

def _eye(P, cx, cy, w, h, look, blink, near=True):
    c = P.c
    if blink:
        _stroke(c, bez((cx - w, cy), (cx, cy + h * 0.55), (cx + w, cy - h * 0.1)), 7)
        return
    top = bez((cx - w, cy + h * 0.1), (cx - w * 0.2, cy - h * 1.25), (cx + w, cy - h * 0.15))
    bot = bez((cx + w, cy - h * 0.15), (cx + w * 0.1, cy + h * 0.95), (cx - w, cy + h * 0.1))
    sclera = path(np.vstack([top, bot]))
    c.drawPath(sclera, paint((255, 250, 244)))
    c.save()
    c.clipPath(sclera, doAntiAlias=True)
    ix, iy = cx + look[0] * w * 0.35, cy + look[1] * h * 0.3
    ir = h * 0.72
    c.drawCircle(ix, iy, ir, paint((96, 50, 30)))
    c.drawCircle(ix, iy + ir * 0.35, ir * 0.9, paint((150, 84, 40), 0.6))
    c.drawCircle(ix, iy, ir * 0.48, paint(INK))
    c.drawCircle(ix - ir * 0.35, iy - ir * 0.35, ir * 0.26, paint(WHITE))
    c.drawPath(path(top, closed=False), paint(INK, 0.35, stroke=h * 0.5))
    c.restore()
    sv.ink(c, top, 10 if near else 8, taper=(0.05, 0.35))
    for u in (0.72, 0.9):                                          # lashes flick out at the outer corner
        p = top[int(u * (len(top) - 1))]
        sv.ink(c, [p, (p[0] + w * 0.35, p[1] - h * 0.55)], 6, taper=(0.1, 0.6))
    sv.ink(c, bot[3:-3], 3.5, taper=(0.4, 0.4))


def _mouth(P, cx, cy, w, o, expr):
    c = P.c
    o = max(0.0, min(1.0, o))
    if o < 0.1:
        smile = 0.35 if expr in ("smile", "neutral") else (-0.2 if expr == "doubt" else 0.1)
        pts = bez((cx - w, cy - smile * 8), (cx, cy + smile * 18), (cx + w, cy - smile * 10))
        sv.ink(c, pts, 7, taper=(0.3, 0.3))
        c.drawPath(path(bez((cx - w * 0.5, cy + 12), (cx, cy + 20), (cx + w * 0.5, cy + 12)), closed=False),
                   paint(LIP, stroke=7))
        return
    h = w * (0.3 + 0.9 * o)
    shape = np.vstack([bez((cx - w, cy), (cx, cy - h * 0.25), (cx + w, cy)), bez((cx + w, cy), (cx, cy + h * 1.25), (cx - w, cy))])
    m = path(shape)
    c.drawPath(m, paint((60, 12, 30)))
    c.save()
    c.clipPath(m, doAntiAlias=True)
    c.drawRect(skia.Rect.MakeLTRB(cx - w, cy - h, cx + w, cy + h * 0.2), paint(WHITE))
    c.drawOval(skia.Rect.MakeLTRB(cx - w * 0.55, cy + h * 0.45, cx + w * 0.55, cy + h * 1.2), paint((230, 90, 110)))
    c.restore()
    c.drawPath(m, paint(LIP, stroke=8))
    sv.ink(c, shape[: len(shape) // 2], 6, taper=(0.3, 0.3))


def hero_head(P, T, talk=0.0, look=(0.35, 0.0), blink=False, expr="neutral"):
    """Head in local units (face ~200 tall), 3/4 view facing +x."""
    c = P.c
    # hair: a big curly cloud, swept back, framing the face (drawn first, behind everything)
    rng = np.random.default_rng(12)
    hair = skia.Path()
    for i in range(24):
        a = math.pi * 0.62 + 2 * math.pi * i / 24
        hx, hy = -36 + 148 * math.cos(a), -52 + 128 * math.sin(a)
        if hy > 60 or (hx > 40 and hy > -10):
            continue
        hair.addCircle(hx, hy, 34 + rng.uniform(-5, 7))
    hair.addOval(skia.Rect.MakeLTRB(-176, -176, 104, 56))
    hair = skia.Op(hair, skia.Path(), skia.PathOp.kUnion_PathOp) or hair
    c.drawPath(hair, paint(INK, stroke=14))
    P.fill(hair, HAIR)
    _shade(P, "mag", hair, path(np.vstack([bez((-200, -150), (-150, -60), (-196, 60)), [(-240, 60), (-240, -150)]])), 0.35)
    _rim(P, hair, MAG, 10, w=20, side=skia.Rect.MakeLTRB(-400, -400, -60, 400))
    _rim(P, hair, CYAN, -8, w=14, side=skia.Rect.MakeLTRB(20, -400, 400, -60))
    for k in range(9):                                          # curl marks in a lifted purple
        a = 2.3 + k * 0.42
        x0, y0 = -36 + 118 * math.cos(a), -52 + 100 * math.sin(a)
        sv.ink(c, bez((x0 - 14, y0 + 4), (x0, y0 - 16), (x0 + 14, y0 + 4)), 6, color=(110, 44, 130), taper=(0.3, 0.3))
    # neck
    neck = path([(-30, 64), (34, 74), (38, 160), (-40, 160)])
    P.fill(neck, SKIN)
    _shade(P, "skin", neck, path(np.vstack([bez((-60, 70), (0, 130), (60, 80)), [(60, 40), (-60, 40)]])), 0.5)
    sv.outline(c, neck, 7)
    # ear + gold hoop on the far side
    ear = path(sv.ellipse(-66, 4, 14, 22))
    P.fill(ear, SKIN)
    sv.outline(c, ear, 6)
    c.drawCircle(-66, 42, 15, paint(INK, stroke=10))
    c.drawCircle(-66, 42, 15, paint(YEL, stroke=5))
    # face: youthful, angular cheekbone on the lit side
    face = path(np.vstack([
        bez((-58, -70), (-74, -30), (-70, 20)), bez((-70, 20), (-66, 66), (-30, 94)),
        bez((-30, 94), (-4, 112), (20, 108)), bez((20, 108), (52, 96), (68, 58)),
        bez((68, 58), (84, 22), (82, -8)), bez((82, -8), (80, -64), (34, -86)), bez((34, -86), (-16, -96), (-58, -70))]))
    P.fill(face, SKIN)
    _shade(P, "skin", face, path(np.vstack([bez((-70, -90), (-40, -20), (-52, 40)), bez((-52, 40), (-50, 90), (0, 120)),
                                            [(-110, 130), (-110, -90)]])), 0.42)
    _rim(P, face, MAG, 8, w=16, side=skia.Rect.MakeLTRB(-400, -400, -46, 400), a=0.95)
    _rim(P, face, CYAN, -7, w=11, side=skia.Rect.MakeLTRB(52, -50, 400, 64), a=0.95)
    c.drawCircle(-24, 42, 18, paint((255, 96, 130), 0.28, blur=7))
    c.drawCircle(58, 38, 12, paint((255, 96, 130), 0.22, blur=6))
    sv.outline(c, face, 8)
    # hairline: curls tumbling over the forehead
    for fx, fy, fr in ((-62, -60, 26), (-38, -80, 28), (-8, -90, 28), (24, -88, 26), (50, -76, 22), (68, -56, 16)):
        P.fill_circle(fx, fy, fr, HAIR)
        sv.ink(c, bez((fx - fr, fy + 3), (fx - fr * 0.2, fy + fr * 1.1), (fx + fr, fy + 2)), 6)
    # brows
    lift = {"wow": -9, "doubt": 0, "focus": 3}.get(expr, 0)
    tilt = 9 if expr == "doubt" else 0
    sv.ink(c, bez((-48, -34 + lift), (-24, -48 + lift), (4, -40 + lift - tilt)), 13, taper=(0.15, 0.55))
    sv.ink(c, bez((36, -42 + lift + tilt), (54, -50 + lift), (72, -38 + lift)), 10, taper=(0.3, 0.5))
    # eyes: big and bright
    _eye(P, -20, -4, 30, 21, look, blink, near=True)
    _eye(P, 52, -6, 19, 18, look, blink, near=False)
    # nose: a single confident stroke and a nostril
    sv.ink(c, bez((30, -12), (40, 16), (46, 32)), 6, taper=(0.6, 0.1))
    sv.ink(c, bez((30, 38), (40, 46), (50, 34)), 6, taper=(0.3, 0.3))
    _mouth(P, 30, 68, 26, talk * (1.15 if expr == "wow" else 1.0), expr)


def _limb(P, a, b, w0, w1, color, dark, rim=None):
    """A sleeve/limb segment from a to b, widths w0 -> w1, with hatched shadow and an ink contour."""
    c = P.c
    ax, ay = a
    bx, by = b
    d = math.hypot(bx - ax, by - ay) + 1e-6
    nx, ny = -(by - ay) / d, (bx - ax) / d
    pts = [(ax + nx * w0 / 2, ay + ny * w0 / 2), (bx + nx * w1 / 2, by + ny * w1 / 2),
           (bx - nx * w1 / 2, by - ny * w1 / 2), (ax - nx * w0 / 2, ay - ny * w0 / 2)]
    p = path(pts)
    P.fill(p, color)
    P.fill_circle(bx, by, w1 / 2, color)
    P.fill_circle(ax, ay, w0 / 2, color)
    sh = path([(ax - nx * w0 / 2, ay - ny * w0 / 2), (bx - nx * w1 / 2, by - ny * w1 / 2), (bx, by), (ax, ay)])
    P.sh["hatch"].drawPath(sh, paint(WHITE, 0.55))
    if rim is not None:
        c.drawPath(path([pts[0], pts[1], (bx + nx * w1 * 0.28, by + ny * w1 * 0.28), (ax + nx * w0 * 0.28, ay + ny * w0 * 0.28)]), paint(rim, 0.85))
    c.drawPath(p, paint(INK, stroke=7))
    return p


def _hand(P, x, y, ang, s=1.0, grip=True):
    """A fist (grip=True, wrapped round a can) or an open hand, pointing along `ang` from the wrist."""
    c = P.c
    P.save()
    P.translate(x, y)
    P.rotate(math.degrees(ang))
    P.scale(s, s)
    for cv in P.sh.values():
        cv.drawRect(skia.Rect.MakeLTRB(-12, -46, 72, 32), sv.CLEAR)
    c.drawRect(skia.Rect.MakeLTRB(-10, -30, 8, 30), paint(HOOD_D))           # ribbed cuff
    c.drawRect(skia.Rect.MakeLTRB(-10, -30, 8, 30), paint(INK, stroke=5))
    if grip:
        fist = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(4, -24, 52, 24), 14, 14)
        c.drawRRect(fist, paint(SKIN))
        c.drawRect(skia.Rect.MakeLTRB(4, 4, 52, 24), paint((120, 66, 46)))
        c.drawRRect(fist, paint(INK, stroke=6))
        for fy in (-10, 2, 13):
            sv.ink(c, [(34, fy), (52, fy)], 4.5, taper=(0.3, 0.1))
        thumb = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(14, -34, 44, -16), 9, 9)
        c.drawRRect(thumb, paint(SKIN))
        c.drawRRect(thumb, paint(INK, stroke=5))
    else:
        palm = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(4, -24, 46, 24), 14, 14)
        c.drawRRect(palm, paint(SKIN))
        c.drawRRect(palm, paint(INK, stroke=6))
        for k, fy in enumerate((-18, -6, 6, 18)):
            L = 30 - abs(k - 1.5) * 5
            f = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(38, fy - 6, 40 + L, fy + 6), 6, 6)
            c.drawRRect(f, paint(SKIN))
            c.drawRRect(f, paint(INK, stroke=4.5))
        thumb = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(14, -44, 30, -14), 8, 8)
        c.drawRRect(thumb, paint(SKIN))
        c.drawRRect(thumb, paint(INK, stroke=4.5))
    P.restore()


def spray_can(c, x, y, ang, s=1.0, color=CAN):
    c.save()
    c.translate(x, y)
    c.rotate(math.degrees(ang))
    c.scale(s, s)
    body = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-24, -62, 24, 58), 12, 12)
    c.drawRRect(body, paint(color))
    c.drawRect(skia.Rect.MakeLTRB(-24, -20, 24, 14), paint(MAG))
    c.drawRect(skia.Rect.MakeLTRB(-24, -20, -8, 14), paint(WHITE, 0.35))
    c.drawRect(skia.Rect.MakeLTRB(6, -62, 24, 58), paint(INK, 0.28))
    c.drawRRect(body, paint(INK, stroke=6))
    cap = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-18, -86, 18, -60), 8, 8)
    c.drawRRect(cap, paint(WHITE))
    c.drawRRect(cap, paint(INK, stroke=5))
    c.drawRect(skia.Rect.MakeLTRB(-5, -98, 5, -86), paint(INK))
    c.restore()


ARM = {                     # (shoulder angle, elbow angle) in degrees, 90 = hanging straight down
    "idle": ((100, -42), (84, 70)),
    "point": ((-18, -12), (84, 70)),
    "point_up": ((-50, -60), (84, 70)),
    "shake": ((110, -70), (84, 70)),
    "spray": ((-8, -2), (84, 70)),
    "shrug": ((40, -35), (140, 215)),
    "think": ((112, -104), (84, 70)),
    "fist": ((20, -80), (84, 70)),
    "open": ((30, 0), (150, 180)),
}


def arm_pose(T, keys):
    """keys: [(t, pose)] -> interpolated ((sR, eR), (sL, eL)) at drawing time twos(T), eased over 0.2 s."""
    t2 = twos(T)
    cur = ARM[keys[0][1]]
    for i, (tk, name) in enumerate(keys):
        if t2 >= tk:
            prev = ARM[keys[i - 1][1]] if i else ARM[name]
            k = sv.ease((t2 - tk) / 0.2)
            cur = tuple(tuple(pa + (pb - pa) * k for pa, pb in zip(A, B)) for A, B in zip(prev, ARM[name]))
    return cur


def _arm_pts(sx, sy, sa, ea, L1=150, L2=140):
    ex, ey = sx + L1 * math.cos(math.radians(sa)), sy + L1 * math.sin(math.radians(sa))
    hx, hy = ex + L2 * math.cos(math.radians(ea)), ey + L2 * math.sin(math.radians(ea))
    return (ex, ey), (hx, hy)


def hero(P, x, y, s, T, talk=0.0, look=(0.35, 0.0), arms=None, expr="neutral", flip=False, can=True, legs=None,
         spray=None, shake=0.0, blink_seed=0, smear_from=None):
    """The narrator, waist-up (or full body with legs=walk phase), head centre at (x, y), s = pixels per unit.
    arms = ((sR, eR), (sL, eL)); shake = 0..1 shaking the can (drawn with multiples)."""
    t2 = twos(T)
    arms = arms or ARM["idle"]
    blink = (int(t2 * 12) + blink_seed) % 41 in (0, 1)
    P.save()
    P.translate(x, y)
    P.scale(-s if flip else s, s)
    c = P.c
    (sR, eR), (sL, eL) = arms
    shR, shL = (170, 238), (-160, 238)
    # far arm (behind the body); in the idle pose it's tucked in the pocket
    if (sL, eL) != ARM["idle"][1]:
        elL, haL = _arm_pts(*shL, sL, eL)
        _limb(P, shL, elL, 72, 62, HOOD_D, INK)
        _limb(P, elL, haL, 62, 52, HOOD_D, INK)
        _hand(P, haL[0], haL[1], math.radians(eL), 1.0, grip=False)
    # legs (full-body shots)
    if legs is not None:
        for side, ph in ((-1, legs), (1, legs + math.pi)):
            hip = (side * 60, 520)
            sw = 0.45 * math.sin(ph)
            knee = (hip[0] + 170 * math.sin(sw), hip[1] + 170 * math.cos(sw))
            lift = max(0.0, math.sin(ph + 0.6)) * 0.5
            foot = (knee[0] + 160 * math.sin(sw - lift), knee[1] + 160 * math.cos(sw - lift))
            _limb(P, hip, knee, 96, 82, DENIM, INK)
            _limb(P, knee, foot, 82, 70, DENIM, INK)
            shoe = path([(foot[0] - 44, foot[1] - 20), (foot[0] + 70, foot[1] - 14), (foot[0] + 86, foot[1] + 30),
                         (foot[0] - 50, foot[1] + 34)])
            c.drawPath(shoe, paint(SHOE))
            c.drawRect(skia.Rect.MakeLTRB(foot[0] - 50, foot[1] + 18, foot[0] + 86, foot[1] + 34), paint(MAG))
            sv.outline(c, shoe, 7)
    # torso: the hoodie, sloped shoulders, tapering to the waist
    torso = path(np.vstack([bez((-50, 146), (-140, 150), (-178, 240)), bez((-178, 240), (-200, 400), (-160, 560)),
                            [(166, 560)], bez((166, 560), (208, 400), (186, 240)), bez((186, 240), (150, 150), (56, 144))]))
    P.fill(torso, HOOD)
    _shade(P, "hatch", torso, path(np.vstack([bez((-210, 150), (-90, 300), (-110, 600)), [(-220, 600)]])), 0.6)
    _rim(P, torso, MAG, 12, w=22, side=skia.Rect.MakeLTRB(-400, -400, -120, 800))
    _rim(P, torso, CYAN, -12, w=18, side=skia.Rect.MakeLTRB(130, -400, 400, 800))
    sv.outline(c, torso, 8)
    sv.ink(c, bez((-120, 470), (0, 452), (122, 470)), 6)             # pocket
    sv.ink(c, [(-120, 470), (-138, 556)], 6)
    sv.ink(c, [(122, 470), (140, 556)], 6)
    star = [(92 + 28 * math.cos(math.radians(-90 + i * 36)) * (1 if i % 2 == 0 else 0.45),
             320 + 28 * math.sin(math.radians(-90 + i * 36)) * (1 if i % 2 == 0 else 0.45)) for i in range(10)]
    c.drawPath(path(star), paint(YEL))
    sv.outline(c, path(star), 5)
    # hood bunched round the neck
    collar = path(np.vstack([bez((-104, 196), (-128, 112), (-36, 118)), bez((-36, 118), (20, 150), (84, 118)),
                             bez((84, 118), (146, 126), (124, 200)), bez((124, 200), (10, 244), (-104, 196))]))
    P.fill(collar, HOOD_D)
    sv.outline(c, collar, 7)
    for dx in (-24, 36):                                            # drawstrings
        sv.ink(c, [(dx, 214), (dx + 4, 300)], 6, color=WHITE, taper=(0.1, 0.1))
        c.drawRect(skia.Rect.MakeLTRB(dx - 1, 296, dx + 9, 318), paint(YEL))
    # headphones resting round the neck
    band = bez((-70, 150), (0, 214), (78, 150))
    sv.ink(c, band, 16, color=INK, taper=(0.05, 0.05))
    sv.ink(c, band, 9, color=YEL, taper=(0.05, 0.05))
    for hx, hy, rot in ((-74, 158, -20), (84, 156, 20)):
        c.save()
        c.translate(hx, hy)
        c.rotate(rot)
        c.drawRoundRect(skia.Rect.MakeLTRB(-20, -26, 20, 26), 14, 14, paint(CYAN))
        c.drawRoundRect(skia.Rect.MakeLTRB(-20, -26, 20, 26), 14, 14, paint(INK, stroke=6))
        c.drawRect(skia.Rect.MakeLTRB(-20, -6, 20, 6), paint(MAG))
        c.restore()
    # head
    hero_head(P, T, talk=talk, look=look, blink=blink, expr=expr)
    # a smear frame when the near arm whips between poses: the swept area filled in, plus the previous can
    if smear_from is not None:
        (psR, peR), _ = smear_from
        pel, pha = _arm_pts(*shR, psR, peR)
        cel, cha = _arm_pts(*shR, sR, eR)
        if math.hypot(cha[0] - pha[0], cha[1] - pha[1]) > 60:
            sm = path([pel, pha, cha, cel])
            c.drawPath(sm, paint(HOOD))
            c.drawPath(path([pha, cha, (cha[0] * 0.5 + cel[0] * 0.5, cha[1] * 0.5 + cel[1] * 0.5)]), paint(sv.lighter(HOOD, 0.3)))
            for u in (0.25, 0.5, 0.75):
                a = (pha[0] + (cha[0] - pha[0]) * u, pha[1] + (cha[1] - pha[1]) * u)
                b = (pel[0] + (cel[0] - pel[0]) * u, pel[1] + (cel[1] - pel[1]) * u)
                sv.ink(c, [a, b], 5, taper=(0.4, 0.4))
            if can:
                spray_can(c, pha[0] + 30 * math.cos(math.radians(peR)), pha[1] + 30 * math.sin(math.radians(peR)), math.radians(peR), 0.9)
    # near arm, with the can - drawn with multiples when shaking fast
    ghosts = []
    if shake > 0.05:
        for j, ph in enumerate((-1.0, 0.0, 1.0)):
            ghosts.append((eR + ph * 26 * shake, j))
    else:
        ghosts = [(eR, 1)]
    for ea, j in ghosts:
        elR, haR = _arm_pts(*shR, sR, ea)
        _limb(P, shR, elR, 74, 64, HOOD, INK, rim=None)
        _limb(P, elR, haR, 64, 54, HOOD, INK)
        if can:
            spray_can(c, haR[0] + 30 * math.cos(math.radians(ea)), haR[1] + 30 * math.sin(math.radians(ea)),
                      math.radians(ea + 90 - 90), 1.0)
        _hand(P, haR[0], haR[1], math.radians(ea), 1.05, grip=can)
    if shake > 0.05:                                            # motion arcs over the shaking can
        elR, haR = _arm_pts(*shR, sR, eR)
        for j, rr in enumerate((170, 200, 230)):
            a0, a1 = math.radians(eR - 30 * shake - 8), math.radians(eR + 30 * shake + 8)
            arc = [(elR[0] + rr * math.cos(a0 + (a1 - a0) * u), elR[1] + rr * math.sin(a0 + (a1 - a0) * u)) for u in np.linspace(0, 1, 12)]
            sv.ink(c, arc, 8 - j * 2, taper=(0.4, 0.4))
    if spray is not None and can:
        elR, haR = _arm_pts(*shR, sR, eR)
        a = math.radians(eR)
        nx, ny = haR[0] + 110 * math.cos(a), haR[1] + 110 * math.sin(a)
        rng = np.random.default_rng(int(t2 * 12))
        for k in range(60):
            dd = rng.uniform(0, 1) ** 0.7 * 260
            aa = a + rng.normal(0, 0.18)
            c.drawCircle(nx + dd * math.cos(aa), ny + dd * math.sin(aa), rng.uniform(2, 7) * (0.4 + dd / 260), paint(spray, 0.85))
    P.restore()


# ------------------------------------------------------------------ NOIR: the skeptic (black and white only)

G1, G2, G3, G4 = (18, 18, 18), (70, 70, 70), (150, 150, 150), (222, 222, 222)


def noir(P, x, y, s, T, talk=0.0, look=0.0, flip=False):
    """A hard-boiled detective, bust, head centre (x, y). Deep shadow on the left, light raking from the right."""
    t2 = twos(T)
    P.save()
    P.translate(x, y)
    P.scale(-s if flip else s, s)
    c = P.c
    # coat and turned-up collar
    coat = path(np.vstack([bez((-60, 120), (-190, 150), (-230, 300)), [(-250, 560), (250, 560)], bez((250, 300), (210, 150), (70, 120))]))
    P.fill(coat, G3)
    P.sh["xhatch"].save()
    P.sh["xhatch"].clipPath(coat, doAntiAlias=True)
    P.sh["xhatch"].drawPath(path([(-260, 100), (-40, 100), (-80, 600), (-260, 600)]), paint(WHITE, 0.8))
    P.sh["xhatch"].restore()
    P.sh["hatch"].save()
    P.sh["hatch"].clipPath(coat, doAntiAlias=True)
    P.sh["hatch"].drawPath(path([(-260, 100), (40, 100), (0, 600), (-260, 600)]), paint(WHITE, 0.7))
    P.sh["hatch"].restore()
    sv.outline(c, coat, 9)
    # shirt, tie
    shirt = path([(-60, 120), (60, 120), (34, 330), (-34, 330)])
    P.fill(shirt, G4)
    tie = path([(-14, 150), (14, 150), (26, 320), (0, 350), (-26, 320)])
    P.fill(tie, G1)
    sv.outline(c, shirt, 6)
    for side in (-1, 1):                                   # lapels / collar points, turned up
        lap = path([(side * 40, 110), (side * 150, 70), (side * 190, 230), (side * 60, 330)])
        P.fill(lap, G3 if side > 0 else G2)
        if side < 0:
            _shade(P, "xhatch", lap, lap, 0.7)
        sv.outline(c, lap, 8)
    # neck and face: square jaw, lit from the right
    neck = path([(-44, 60), (44, 60), (40, 130), (-40, 130)])
    P.fill(neck, G2)
    face = path(np.vstack([bez((-70, -60), (-80, 10), (-72, 60)), bez((-72, 60), (-62, 108), (-10, 118)),
                           bez((-10, 118), (50, 118), (70, 70)), bez((70, 70), (84, 10), (76, -60)), [(-70, -60)]]))
    P.fill(face, G4)
    shadow = path(np.vstack([[(-90, -80), (-14, -80)], bez((-14, -80), (-34, 30), (-22, 130)), [(-90, 130)]]))
    c.save()
    c.clipPath(face, doAntiAlias=True)
    c.drawPath(shadow, paint(G1))
    c.drawRect(skia.Rect.MakeLTRB(-100, -80, 100, -8), paint(G1))         # the hat brim's shadow over the eyes
    c.restore()
    _shade(P, "dot", face, path(sv.ellipse(34, 96, 44, 24)), 0.28)        # stubble on the lit side
    sv.outline(c, face, 8)
    # eyes: two glints in the shadow
    for ex, w in ((-22, 20), (40, 16)):
        c.drawPath(path([(ex - w, -30), (ex + w, -34), (ex + w * 0.6, -24), (ex - w * 0.8, -22)]), paint(WHITE))
        c.drawCircle(ex + look * 6, -28, 4, paint(G1))
    # nose (lit edge) and mouth
    sv.ink(c, [(34, -8), (48, 44), (30, 52)], 5, color=G4, taper=(0.1, 0.4))
    o = max(0.0, min(1.0, talk))
    if o < 0.1:
        sv.ink(c, [(-2, 80), (50, 74)], 7, color=G1)
    else:
        m = path(sv.ellipse(24, 80, 26, 5 + 13 * o))
        c.drawPath(m, paint(G1))
        c.drawRect(skia.Rect.MakeLTRB(2, 74, 46, 78), paint(G4))
    # the fedora
    crown = path(np.vstack([bez((-96, -80), (-104, -170), (-40, -196)), bez((-40, -196), (0, -178), (40, -198)),
                            bez((40, -198), (104, -170), (96, -80))]))
    P.fill(crown, G1)
    c.drawRect(skia.Rect.MakeLTRB(-98, -112, 98, -84), paint(G2))
    brim = path(sv.ellipse(0, -78, 190, 34))
    P.fill(brim, G1)
    sv.ink(c, bez((-170, -84), (0, -120), (176, -86)), 6, color=G3, taper=(0.3, 0.3))
    sv.ink(c, bez((30, -190), (80, -160), (88, -100)), 7, color=G3, taper=(0.2, 0.6))
    sv.outline(c, crown, 7, color=G1)
    P.restore()


def rain(c, x0, y0, x1, y1, T, n=90, seed=3, a=0.8):
    rng = np.random.default_rng(seed)
    t = T * 1.0
    for i in range(n):
        x = rng.uniform(x0, x1 + 200)
        sp = rng.uniform(1600, 2400)
        y = y0 + (rng.uniform(0, 1) * (y1 - y0) + t * sp) % (y1 - y0 + 200) - 100
        L = rng.uniform(40, 90)
        sv.ink(c, [(x - 0.25 * (y - y0), y), (x - 0.25 * (y - y0) - L * 0.25, y + L)], 3, color=WHITE, a=a, taper=(0.5, 0.2))


# ------------------------------------------------------------------ ANIME: the believer (cel-shaded)

A_HAIR, A_HAIR_D, A_TIP = (255, 110, 190), (214, 60, 150), (0, 220, 255)
A_SKIN, A_SKIN_D = (255, 224, 206), (236, 170, 160)


def _sparkle(c, x, y, r, color=WHITE, a=1.0):
    pts = []
    for i in range(8):
        ang = math.pi / 4 * i
        rr = r if i % 2 == 0 else r * 0.22
        pts.append((x + rr * math.cos(ang), y + rr * math.sin(ang)))
    c.drawPath(path(pts), paint(color, a))


def anime(P, x, y, s, T, talk=0.0, flip=False, fist=0.0, blink_seed=3):
    """A shonen-energy believer: huge sparkling eyes, pink hair with cyan tips, sailor collar; cel-shaded."""
    t2 = twos(T)
    blink = (int(t2 * 12) + blink_seed) % 37 == 0
    P.save()
    P.translate(x, y)
    P.scale(-s if flip else s, s)
    c = P.c
    # back hair
    back = path(np.vstack([bez((-150, -40), (-190, 160), (-120, 260)), [(120, 260)], bez((120, 260), (190, 160), (150, -40)),
                           bez((150, -40), (0, -240), (-150, -40))]))
    P.fill(back, A_HAIR_D)
    sv.outline(c, back, 7)
    # body: sailor uniform
    body = path(np.vstack([bez((-50, 140), (-170, 150), (-200, 300)), [(-220, 560), (220, 560)], bez((200, 300), (170, 150), (50, 140))]))
    P.fill(body, WHITE)
    c.save()
    c.clipPath(body, doAntiAlias=True)
    c.drawPath(path([(-230, 140), (-80, 140), (-120, 600), (-230, 600)]), paint((210, 214, 236)))      # hard cel shadow
    c.restore()
    collar = path([(-60, 136), (60, 136), (150, 190), (110, 300), (0, 250), (-110, 300), (-150, 190)])
    P.fill(collar, (40, 50, 140))
    for off in (10, 22):
        sv.ink(c, [(-138 + off * 0.3, 196 + off), (-100, 290 - off * 0.2)], 4, color=WHITE, taper=(0.1, 0.1))
        sv.ink(c, [(138 - off * 0.3, 196 + off), (100, 290 - off * 0.2)], 4, color=WHITE, taper=(0.1, 0.1))
    scarf = path([(-30, 240), (30, 240), (70, 330), (0, 300), (-70, 330)])
    P.fill(scarf, (255, 40, 70))
    sv.outline(c, body, 7)
    sv.outline(c, collar, 6)
    sv.outline(c, scarf, 6)
    # neck, face
    neck = path([(-30, 60), (30, 60), (34, 150), (-34, 150)])
    P.fill(neck, A_SKIN)
    c.drawPath(path([(-30, 60), (30, 60), (32, 100), (-32, 110)]), paint(A_SKIN_D))
    sv.outline(c, neck, 6)
    face = path(np.vstack([bez((-100, -60), (-104, 40), (-40, 100)), bez((-40, 100), (0, 128), (40, 100)),
                           bez((40, 100), (104, 40), (100, -60)), [(-100, -60)]]))
    P.fill(face, A_SKIN)
    sv.outline(c, face, 7)
    for bx in (-60, 60):                                            # blush lines
        for k in range(3):
            sv.ink(c, [(bx - 18 + k * 12, 46), (bx - 24 + k * 12, 60)], 4, color=(255, 90, 120), taper=(0.2, 0.2))
    # eyes: tall, glossy, cyan-to-magenta irises with three highlights
    for ex, sgn in ((-44, -1), (44, 1)):
        if blink:
            sv.ink(c, bez((ex - 36, 10), (ex, 30), (ex + 36, 10)), 10)
            continue
        eye = path(sv.ellipse(ex, 12, 34, 44))
        P.fill(eye, WHITE)
        c.save()
        c.clipPath(eye, doAntiAlias=True)
        c.drawOval(skia.Rect.MakeLTRB(ex - 28, -22, ex + 28, 58), paint(shader=sv.lin((0, -22), (0, 58), [(20, 40, 120), CYAN, MAG])))
        c.drawOval(skia.Rect.MakeLTRB(ex - 13, 4, ex + 13, 40), paint(INK))
        c.drawCircle(ex - 12, -2, 11, paint(WHITE))
        c.drawCircle(ex + 12, 36, 6, paint(WHITE))
        _sparkle(c, ex + 8, 6, 10, WHITE)
        c.restore()
        sv.ink(c, bez((ex - 40, -18), (ex, -44), (ex + 40, -20)), 12, taper=(0.1, 0.2))
        sv.ink(c, [(ex + sgn * 34, -20), (ex + sgn * 50, -34)], 7, taper=(0.1, 0.6))
    # tiny nose, big mouth
    sv.ink(c, [(4, 54), (0, 60)], 4)
    o = max(0.0, min(1.0, talk))
    if o < 0.1:
        sv.ink(c, bez((-20, 80), (0, 92), (20, 80)), 6)
    else:
        m = path(np.vstack([[(-34, 76), (34, 76)], bez((34, 76), (0, 76 + 70 * o), (-34, 76))]))
        c.drawPath(m, paint((140, 20, 50)))
        c.save()
        c.clipPath(m, doAntiAlias=True)
        c.drawOval(skia.Rect.MakeLTRB(-20, 76 + 30 * o, 20, 76 + 80 * o), paint((255, 110, 130)))
        c.restore()
        c.drawPath(m, paint(INK, stroke=5))
    # front hair: spiky bangs, cel-shaded, cyan tips, and one antenna strand
    bangs = path(np.vstack([bez((-150, -40), (-150, -170), (-40, -190)), bez((-40, -190), (80, -200), (150, -40)),
                            [(120, -20), (96, -70), (70, -8), (40, -76), (10, -14), (-24, -80), (-50, -10), (-80, -70), (-110, -6)]]))
    P.fill(bangs, A_HAIR)
    c.save()
    c.clipPath(bangs, doAntiAlias=True)
    c.drawPath(path([(-160, -200), (-40, -200), (-110, 0), (-160, 0)]), paint(A_HAIR_D))
    c.drawPath(path([(-160, -40), (160, -40), (160, 10), (-160, 10)]), paint(A_TIP))
    c.drawPath(path(sv.ellipse(20, -150, 70, 16)), paint(WHITE, 0.8))
    c.restore()
    sv.outline(c, bangs, 7)
    ah = bez((0, -190), (60, -300), (100, -250))
    sv.ink(c, ah, 16, color=INK, taper=(0.2, 0.9))
    sv.ink(c, ah, 9, color=A_HAIR, taper=(0.2, 0.9))
    # the fist pump (with a smear on the way up)
    if fist > 0.01:
        hx, hy = 210, 260 - 300 * fist
        if 0.2 < fist < 0.8:
            smear = path([(200, 420), (250, 420), (hx + 44, hy + 20), (hx - 44, hy + 20)])
            c.drawPath(smear, paint(A_SKIN, 0.9))
            sv.ink(c, [(200, 420), (hx - 44, hy + 20)], 5)
            sv.ink(c, [(250, 420), (hx + 44, hy + 20)], 5)
        arm = path([(150, 320), (220, 300), (hx + 34, hy + 40), (hx - 34, hy + 40)])
        P.fill(arm, WHITE)
        sv.outline(c, arm, 6)
        fst = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(hx - 46, hy - 50, hx + 46, hy + 40), 24, 24)
        P.fill_rrect(fst, A_SKIN)
        c.drawRRect(fst, paint(INK, stroke=7))
        for k in range(3):
            sv.ink(c, [(hx - 30 + k * 26, hy - 50), (hx - 30 + k * 26, hy - 20)], 5)
    P.restore()


# ------------------------------------------------------------------ BOT: the AI (a flat, bouncy cartoon)

B_BODY, B_FACE, B_DARK = (0, 210, 255), (240, 255, 255), (0, 120, 190)


def glove(c, x, y, ang, s=1.0, point=False):
    c.save()
    c.translate(x, y)
    c.rotate(math.degrees(ang))
    c.scale(s, s)
    c.drawRoundRect(skia.Rect.MakeLTRB(-16, -24, 8, 24), 8, 8, paint(WHITE))
    c.drawRoundRect(skia.Rect.MakeLTRB(-16, -24, 8, 24), 8, 8, paint(INK, stroke=6))
    palm = path(sv.ellipse(30, 0, 30, 28))
    c.drawPath(palm, paint(WHITE))
    c.drawPath(palm, paint(INK, stroke=6))
    if point:
        f = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(46, -10, 96, 8), 9, 9)
        c.drawRRect(f, paint(WHITE))
        c.drawRRect(f, paint(INK, stroke=6))
    else:
        for fy in (-12, 2, 16):
            sv.ink(c, [(40, fy), (56, fy)], 5)
    c.restore()


def bot(P, x, y, s, T, talk=0.0, look=(0.0, 0.0), arms=((200, 160), (-20, 20)), expr="happy", flip=False, bounce=1.0,
        coat=False, medal=False, legs=True, hue=None, eyes_x=False):
    """The AI as a 1930s-meets-Saturday-morning cartoon: squash-and-stretch on the beat, pie-cut eyes,
    noodle arms with white gloves. arms = ((angle, bend) for its left, (angle, bend) for its right)."""
    t2 = twos(T)
    body_c = hue or B_BODY
    sq = 1 + 0.07 * math.sin(t2 * 2 * math.pi * 1.53) * bounce          # squash and stretch at the song's tempo
    hop = -abs(math.sin(t2 * math.pi * 1.53)) * 26 * bounce
    P.save()
    P.translate(x, y + hop * s)
    P.scale((-s if flip else s) / sq, s * sq)
    c = P.c
    # legs
    if legs:
        for side in (-1, 1):
            lx = side * 40
            sv.ink(c, [(lx, 140), (lx + side * 8, 220)], 22, color=INK, taper=(0.02, 0.02))
            shoe = path(sv.ellipse(lx + side * 24, 232, 44, 22))
            c.drawPath(shoe, paint((255, 60, 90)))
            c.drawPath(shoe, paint(INK, stroke=6))
    # noodle arms (rubber hose): a smooth curve from the shoulder to the glove
    ends = []
    for side, (ang, bend) in zip((-1, 1), arms):
        sx, sy = side * 86, 70
        a = math.radians(ang)
        hx, hy = sx + 150 * math.cos(a), sy + 150 * math.sin(a)
        mx, my = (sx + hx) / 2 + bend * math.sin(a), (sy + hy) / 2 - bend * math.cos(a)
        pts = bez((sx, sy), (mx, my), (hx, hy))
        sv.ink(c, pts, 20, color=INK, taper=(0.02, 0.02))
        ends.append((hx, hy, a))
    # body
    body = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-90, 20, 90, 160), 40, 40)
    P.fill_rrect(body, body_c)
    c.drawRRect(body, paint(INK, stroke=8))
    c.drawCircle(0, 92, 20, paint(YEL))
    c.drawCircle(0, 92, 20, paint(INK, stroke=6))
    if coat:                                                        # a lab coat: AGI-level researcher
        for side in (-1, 1):
            flap = path([(side * 8, 24), (side * 96, 24), (side * 104, 170), (side * 20, 170)])
            c.drawPath(flap, paint(WHITE))
            c.drawPath(flap, paint(INK, stroke=6))
        c.drawRect(skia.Rect.MakeLTRB(40, 70, 74, 84), paint(MAG))
    if medal:
        sv.ink(c, [(-40, 20), (0, 110)], 16, color=(255, 50, 70), taper=(0.05, 0.05))
        sv.ink(c, [(40, 20), (0, 110)], 16, color=(40, 90, 255), taper=(0.05, 0.05))
        c.drawCircle(0, 124, 34, paint((255, 205, 40)))
        c.drawCircle(0, 124, 34, paint(INK, stroke=6))
        c.drawCircle(0, 124, 22, paint((255, 236, 120)))
        _sparkle(c, 16, 110, 16, WHITE)
    # head: a rounded TV-ish block with a big face panel
    head = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-120, -180, 120, 30), 60, 60)
    P.fill_rrect(head, body_c)
    c.drawRRect(head, paint(INK, stroke=9))
    facep = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-96, -150, 96, 6), 46, 46)
    c.drawRRect(facep, paint(B_FACE))
    c.drawRRect(facep, paint(INK, stroke=6))
    sv.ink(c, [(0, -180), (0, -236)], 10)                              # antenna
    c.drawCircle(0, -246, 18, paint(MAG))
    c.drawCircle(0, -246, 18, paint(INK, stroke=6))
    # pie-cut eyes
    blink = (int(t2 * 12)) % 29 == 0
    for ex in (-40, 40):
        if blink:
            sv.ink(c, [(ex - 20, -80), (ex + 20, -80)], 9)
            continue
        if eyes_x:
            sv.ink(c, [(ex - 18, -100), (ex + 18, -64)], 9)
            sv.ink(c, [(ex + 18, -100), (ex - 18, -64)], 9)
            continue
        c.drawOval(skia.Rect.MakeLTRB(ex - 20, -114, ex + 20, -50), paint(INK))
        wedge = path([(ex + look[0] * 10 + 4, -96 + look[1] * 8), (ex + 20, -104), (ex + 20, -86)])
        c.drawCircle(ex - 6 + look[0] * 8, -96 + look[1] * 8, 7, paint(WHITE))
        c.drawPath(wedge, paint(B_FACE))
    o = max(0.0, min(1.0, talk))
    if expr == "confused":
        sv.ink(c, [(-34, -20), (-10, -28), (12, -18), (34, -26)], 8)
    elif o < 0.1:
        sv.ink(c, bez((-44, -30), (0, 0), (44, -30)), 9)
    else:
        m = path(np.vstack([[(-46, -32), (46, -32)], bez((46, -32), (0, -32 + 80 * o), (-46, -32))]))
        c.drawPath(m, paint((90, 10, 40)))
        c.save()
        c.clipPath(m, doAntiAlias=True)
        c.drawOval(skia.Rect.MakeLTRB(-24, -20 + 20 * o, 24, 10 + 50 * o), paint((255, 90, 120)))
        c.restore()
        c.drawPath(m, paint(INK, stroke=7))
    # gloves on top
    for i, (hx, hy, a) in enumerate(ends):
        glove(c, hx, hy, a, 1.0, point=(i == 1 and expr == "point"))
    P.restore()
    return ends

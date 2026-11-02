"""Live actors: people with real proportions (about 7.5 heads tall), jointed limbs, soft photographic shading and no
ink outline, so they read as actors matted into the painted cartoon world.

person(c, x, y, s, T, look) - (x, y) is the point between the feet, s = 1 is 1000 px tall. `look` is a dict:
  pose     joint angles (degrees): sL, sR shoulder (0 = arm hanging, 90 = straight out to that side, 170 = up),
           eL, eR elbow bend, hL, hR hip (+ forward kick), kL, kR knee bend, lean, head tilt
  top, sleeve, bottom, shoe, skin, hair colours; hair style ('curls', 'bob', 'short', 'cap'); extras
"""
import math

import numpy as np
import skia

import draw as D
import zkit as Z
from draw import INK, WHITE, mix, paint, path

SKIN, SKIN_D = (214, 182, 160), (156, 118, 98)

POSES = {
    "stand": dict(sL=8, sR=8, eL=10, eR=10, hL=0, hR=0, kL=0, kR=0),
    "present": dict(sL=10, sR=120, eL=15, eR=10, hL=0, hR=6, kL=0, kR=8),
    "point": dict(sL=8, sR=100, eL=10, eR=0),
    "both_up": dict(sL=150, sR=150, eL=20, eR=20),
    "shrug": dict(sL=40, sR=40, eL=110, eR=110),
    "hips": dict(sL=35, sR=35, eL=120, eR=120),
    "search": dict(sL=20, sR=25, eL=80, eR=90),
    "phone": dict(sL=8, sR=30, eL=10, eR=150),
    "walk": dict(sL=-20, sR=20, eL=20, eR=20, hL=18, hR=-14, kL=10, kR=20),
    "kick": dict(sL=110, sR=110, eL=30, eR=30, hL=0, hR=85, kL=0, kR=10),
    "bow": dict(sL=20, sR=60, eL=40, eR=60, lean=18),
    "wave": dict(sL=10, sR=150, eL=10, eR=40),
    "cane": dict(sL=30, sR=10, eL=60, eR=10),
    "reach": dict(sL=10, sR=75, eL=10, eR=5, lean=-6),
}


HANDS = {}                                                              # the last figure's hands, in device pixels


def _limb(c, x0, y0, a0, l0, bend, l1, w0, w1, w2, col, k=0.25, matte=False):
    """A two-segment limb from (x0, y0): first segment at angle a0 (rad, 0 = straight down), then bent by `bend`."""
    x1, y1 = x0 + l0 * math.sin(a0), y0 + l0 * math.cos(a0)
    a1 = a0 + bend
    x2, y2 = x1 + l1 * math.sin(a1), y1 + l1 * math.cos(a1)
    p0, p1 = D.capsule(x0, y0, x1, y1, w0, w1), D.capsule(x1, y1, x2, y2, w1, w2)
    D.shade(c, p0, col, k=k, edge=0.0)
    D.shade(c, p1, col, k=k, edge=0.0)
    return (x1, y1), (x2, y2), a1


def _hand(c, x, y, a, s, col):
    c.save()
    c.translate(x, y)
    c.rotate(-math.degrees(a))
    D.shade(c, D.smooth([(-13, -6), (13, -6), (16, 18), (8, 34), (-8, 34), (-16, 16)]), col, k=0.25, edge=0.0)
    D.shade(c, D.capsule(-12, 4, -22, 20, 10, 8), col, k=0.25, edge=0.0)
    c.restore()


def person(c, x, y, s, T, look, matte=False, face=True):
    P = dict(POSES["stand"])
    P.update(POSES.get(look.get("pose", "stand"), {}))
    P.update(look.get("joints", {}))
    top, sleeve = look.get("top", (120, 118, 122)), look.get("sleeve", look.get("top", (120, 118, 122)))
    bottom, shoe = look.get("bottom", (70, 68, 72)), look.get("shoe", (26, 24, 24))
    skin = look.get("skin", SKIN)
    if matte:                                                           # the matte fringe, behind the whole figure only
        lp = skia.Paint()
        lp.setImageFilter(skia.ImageFilters.DropShadow(0, 0, 5 * s + 2, 5 * s + 2, skia.Color4f(1, 1, 1, 0.9).toColor()))
        c.saveLayer(None, lp)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    breathe = 1.5 * math.sin(T * 2.1)
    lean = math.radians(P.get("lean", 0))
    hipY = -500
    # legs (the far one first)
    feet = []
    for side, hk, kk in (("L", "hL", "kL"), ("R", "hR", "kR")):
        sx = -1 if side == "L" else 1
        a0 = sx * math.radians(P[hk])                                   # 0 = straight down; + swings out to that side
        (kx, ky), (fx, fy), a1 = _limb(c, sx * 52, hipY, a0, 250, -sx * math.radians(P[kk]), 245, 92, 70, 52,
                                       look.get("legcol", bottom))
        feet.append((fx, fy, sx))
    for fx, fy, sx in feet:
        c.drawOval(skia.Rect.MakeLTRB(fx - 60, fy + 14, fx + 60, fy + 34), paint((0, 0, 0), 0.35, blur=6))    # its shadow
        c.drawOval(skia.Rect.MakeLTRB(fx - 36 + 14 * sx, fy - 20, fx + 36 + 14 * sx, fy + 16), paint(shoe))
    if look.get("skirt"):
        D.shade(c, path([(-120, hipY - 60), (120, hipY - 60), (170, hipY + 200), (-170, hipY + 200)]), look["skirt"], k=0.3, edge=0.0)
    # torso
    c.save()
    c.translate(0, hipY)
    c.rotate(math.degrees(lean) * 0.6)
    c.translate(0, -hipY)
    sh_y = -860 + breathe
    torso = D.smooth([(-78, hipY + 20), (-92, hipY - 60), (-86, -700), (-118, sh_y + 20), (-70, sh_y - 8), (70, sh_y - 8),
                      (118, sh_y + 20), (86, -700), (92, hipY - 60), (78, hipY + 20)])
    if look.get("coat"):
        torso = D.smooth([(-118, hipY + 190), (-104, hipY - 60), (-92, -700), (-122, sh_y + 20), (-70, sh_y - 8), (70, sh_y - 8),
                          (122, sh_y + 20), (92, -700), (104, hipY - 60), (118, hipY + 190), (0, hipY + 205)])
    if look.get("tails"):
        c.drawPath(path([(-90, hipY - 40), (-120, hipY + 230), (-40, hipY + 60), (40, hipY + 60), (120, hipY + 230), (90, hipY - 40)]),
                   paint(mix(top, INK, 0.3)))
    D.shade(c, torso, top, k=0.32, edge=0.0)
    for fn in look.get("extras", []):                                   # shirt fronts, buttons, stethoscopes...
        fn(c, sh_y, hipY)
    # arms
    for side, sk, ek in (("L", "sL", "eL"), ("R", "sR", "eR")):
        sx = -1 if side == "L" else 1
        a0 = sx * math.radians(P[sk])                                   # 0 = hanging; 90 = out to the side; 170 = up
        (ex, ey), (hx, hy), a1 = _limb(c, sx * 106, sh_y + 26, a0, 175, -sx * math.radians(P[ek]), 168, 56, 46, 38, sleeve)
        _hand(c, hx, hy, a1, 1.0, skin)
        q = c.getTotalMatrix().mapXY(hx, hy)
        HANDS[side] = (q.x(), q.y(), a1)
    # head
    c.translate(0, sh_y - 6)
    c.rotate(P.get("tilt", 0) + 2 * math.sin(T * 0.9))
    D.shade(c, D.capsule(0, 10, 0, -50, 50, 46), mix(skin, SKIN_D, 0.25), k=0.2, edge=0.0)
    head = D.smooth([(-58, -70), (-54, -130), (-40, -178), (0, -196), (40, -178), (54, -130), (58, -70), (36, -34), (0, -24), (-36, -34)])
    _hair_back(c, look.get("hair", "short"), look.get("haircol", (60, 52, 48)))
    D.shade(c, head, skin, k=0.3, edge=0.0)
    if face:
        _face(c, T, look)
    _hair_front(c, look.get("hair", "short"), look.get("haircol", (60, 52, 48)))
    for fn in look.get("hat", []):
        fn(c)
    c.restore()
    c.restore()
    if matte:
        c.restore()


def _hair_back(c, style, col):
    if style == "bob":
        c.drawPath(D.smooth([(-74, -30), (-78, -150), (-40, -206), (40, -206), (78, -150), (74, -30), (40, -40), (-40, -40)]), paint(col))


def _hair_front(c, style, col):
    rng = np.random.default_rng(3)
    if style == "curls":
        for i in range(22):
            a = math.pi * (1.02 + 0.96 * i / 21)
            r = 60 + rng.uniform(-4, 10)
            cx, cy = r * math.cos(a) * 1.08, -120 + r * math.sin(a) * 1.25
            rr = rng.uniform(16, 22)
            c.drawCircle(cx, cy, rr, paint(mix(col, INK, rng.uniform(0, 0.22))))
            c.drawCircle(cx - rr * 0.3, cy - rr * 0.3, rr * 0.4, paint(WHITE, 0.22))
    elif style == "bob":
        c.drawPath(D.smooth([(-66, -120), (-40, -196), (40, -200), (66, -130), (30, -150), (-20, -140)]), paint(col))
    elif style == "short":
        c.drawPath(D.smooth([(-60, -120), (-50, -180), (0, -204), (50, -180), (60, -120), (40, -160), (-40, -160)]), paint(col))
    elif style == "cap":
        c.drawPath(D.smooth([(-62, -128), (-50, -196), (0, -214), (50, -196), (62, -128)]), paint((150, 160, 166)))


def _face(c, T, look):
    expr = look.get("expr", "calm")
    blink = (T * 0.8 + look.get("seed", 0) * 0.37) % 3.7 < 0.12 or look.get("eyes_closed")
    c.drawOval(skia.Rect.MakeLTRB(-50, -126, -8, -92), paint(SKIN_D, 0.25, blur=6))            # eye sockets
    c.drawOval(skia.Rect.MakeLTRB(8, -126, 50, -92), paint(SKIN_D, 0.25, blur=6))
    for sx in (-1, 1):
        ex, ey = sx * 24, -108
        if blink:
            c.drawLine(ex - 11, ey, ex + 11, ey + 1, paint((70, 50, 44), stroke=3.5))
        else:
            c.drawOval(skia.Rect.MakeLTRB(ex - 11, ey - 6, ex + 11, ey + 6), paint((242, 240, 236)))
            c.drawCircle(ex + look.get("gaze", 0) * 3, ey, 5.2, paint((40, 32, 30)))
            c.drawLine(ex - 12, ey - 6, ex + 12, ey - 7, paint((70, 50, 44), stroke=2.5))
        by = {"worried": -128 + sx * 3, "puzzled": -130 - (sx < 0) * 5, "happy": -131, "calm": -129, "grin": -133}.get(expr, -129)
        c.drawLine(ex - 14, by + 1, ex + 14, by - 2, paint(look.get("browcol", (90, 84, 80)), stroke=5))
    c.drawPath(D.smooth([(-4, -100), (-12, -66), (0, -60), (12, -66), (4, -100)]), paint(SKIN_D, 0.35))       # nose shadow
    c.drawCircle(-6, -64, 3, paint(SKIN_D, 0.6))
    c.drawCircle(6, -64, 3, paint(SKIN_D, 0.6))
    lip = look.get("lip", (150, 80, 76))
    if expr in ("happy", "grin"):
        p = skia.Path()
        p.moveTo(-20, -48)
        p.quadTo(0, -30 if expr == "happy" else -24, 20, -48)
        p.close()
        c.drawPath(p, paint(lip))
        if expr == "grin":
            c.drawLine(-14, -45, 14, -45, paint(WHITE, stroke=3))
    else:
        yy = -44 if expr != "worried" else -42
        p = skia.Path()
        p.moveTo(-16, yy)
        p.quadTo(0, yy - (4 if expr == "calm" else -3), 16, yy)
        c.drawPath(p, paint(lip, stroke=5))
    c.drawCircle(-34, -70, 12, paint((230, 150, 140), 0.16, blur=5))
    c.drawCircle(34, -70, 12, paint((230, 150, 140), 0.16, blur=5))
    if look.get("glasses"):
        from cast import glasses
        glasses(c, 0, -108, 0.3)
    if look.get("mask"):
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-50, -86, 50, -26), 14, 14), paint((206, 214, 218)))

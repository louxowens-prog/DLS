"""Dot and Doc.

Dot, 41, sock puppeteer: an electric-blue thrift-store wig cut in a blunt bob, a painted blue star round her left eye,
gold glitter on the cheekbones, hot-pink lipstick, gold hoops, a cream polka-dot turtleneck, a purple velvet cape with
gold felt dots and a hot-pink lining (a gold star brooch at the throat), electric-blue flared cords and gold glitter
sneakers. She is 'live action': shaded like a person, moving smoothly at 24 fps, keyed in on a cheap green screen
(spill halo, jagged matte line, warmer light than the world she is pasted into, feet that float).

Doc: a white tube sock with hot-pink, blue and gold cuff stripes, two googly eyes that never stop wobbling, an orange
yarn quiff, a red felt mouth, and a cardboard-and-foil doctor's head mirror. Made in 1994. Worn on Dot's right hand.

Local units: Dot's head centre is (0, 0), the face is ~200 wide and ~250 tall, her feet are at y = 1440.
"""
import math

import numpy as np
import skia

import diy as K
from diy import BLUE, GOLD, HOT, INK, PURPLE, WHITE, CREAM, ACID, bez, lin, mix, paint, path, rad, smooth

SKIN = (236, 186, 156)
SKIN_D = (196, 132, 108)
SKIN_L = (252, 214, 190)
WIG, WIG_D, WIG_L = (34, 104, 255), (14, 44, 170), (140, 200, 255)
LIP, LIP_D = (236, 40, 132), (170, 20, 92)
BROW = (60, 38, 34)
CAPE, CAPE_D, CAPE_L = (120, 40, 200), (66, 18, 120), (168, 96, 236)
LINING = (255, 52, 160)
KNIT, KNIT_D = (250, 240, 222), (214, 200, 178)
CORD, CORD_D = (40, 110, 240), (20, 56, 150)

# ------------------------------------------------------------------ moods: brows (inner lift, outer lift), lids, mouth

MOODS = {
    #            brow_in brow_out  lid   smile  mouth_w  blush
    "deadpan":  (0.0,   0.0,      0.58, 0.0,   1.0,     0.0),
    "flat":     (-0.1,  0.0,      0.72, -0.12, 0.95,    0.0),
    "smile":    (0.25,  0.15,     0.74, 0.7,   1.1,     0.2),
    "grin":     (0.45,  0.3,      0.8,  1.0,   1.18,    0.3),
    "sad":      (1.0,   -0.55,    0.62, -0.7,  0.9,     0.05),
    "wide":     (1.1,   0.9,      1.22, -0.05, 0.95,    0.0),
    "side":     (0.35,  -0.15,    0.62, 0.25,  0.96,    0.85),     # embarrassed: eyes away, blushing
    "sincere":  (0.6,   -0.2,     0.82, 0.3,   1.0,     0.12),
    "fierce":   (-0.8,  0.35,     0.8,  -0.1,  1.0,     0.0),
    "wince":    (0.7,   -0.5,     0.3,  -0.4,  1.05,    0.25),
    "proud":    (0.3,   0.4,      0.68, 0.55,  1.08,    0.15),
}


def _mood(name):
    return MOODS.get(name, MOODS["deadpan"])


def blend_mood(a, b, k):
    ma, mb = _mood(a), _mood(b)
    return tuple(x + (y - x) * k for x, y in zip(ma, mb))


# ------------------------------------------------------------------ the face

def _eye(c, x, y, w, open_, look, side, seed, T):
    """A shaded eye: almond opening, white with lid shadow, a hazel iris with fibres, wet highlight, lash line,
    gold-and-purple shadow on the lid."""
    h = w * 0.44
    up_y = y - h * 0.95 * open_
    lo_y = y + h * 0.48 * max(open_, 0.15)
    outer = x + side * w * 0.52
    inner = x - side * w * 0.48
    # eyeshadow: purple to gold, up to the crease
    shadow = path(np.vstack([bez((inner, y), (x, up_y - h * 1.3), (outer + side * w * 0.12, y - h * 0.35), 16),
                             bez((outer + side * w * 0.12, y - h * 0.35), (x, up_y + h * 0.1), (inner, y), 16)]))
    c.drawPath(shadow, paint(shader=lin((x, y), (x, up_y - h * 1.2), [(150, 60, 220, 0.75), (255, 190, 60, 0.6)]), blur=w * 0.04))
    up = bez((inner, y + 1), (x - side * w * 0.04, up_y - h * 0.3 * open_), (outer, y - h * 0.18), 20)
    lo = bez((outer, y - h * 0.18), (x + side * w * 0.04, lo_y), (inner, y + 1), 20)
    if open_ > 0.08:
        opening = path(np.vstack([up, lo]))
        c.save()
        c.clipPath(opening, doAntiAlias=True)
        c.drawRect(skia.Rect.MakeLTRB(x - w, y - h * 2.5, x + w, y + h * 2),
                   paint(shader=rad((x, y + h * 0.2), w * 0.7, [(252, 248, 244), (238, 228, 222), (196, 170, 164)], [0, 0.6, 1])))
        ix = x + look[0] * w * 0.24
        iy = y - h * 0.1 + look[1] * h * 0.32
        ir = w * 0.25
        c.drawCircle(ix, iy, ir, paint(shader=rad((ix, iy), ir, [(186, 150, 74), (126, 92, 40), (56, 38, 18)], [0.2, 0.68, 1])))
        rng = np.random.default_rng(seed)
        for k in range(30):
            a = k / 30 * 2 * math.pi + rng.normal(0, 0.05)
            r0, r1 = ir * rng.uniform(0.4, 0.55), ir * rng.uniform(0.82, 0.97)
            c.drawLine(ix + r0 * math.cos(a), iy + r0 * math.sin(a), ix + r1 * math.cos(a), iy + r1 * math.sin(a),
                       paint((214, 180, 104) if k % 2 else (70, 46, 22), 0.4, stroke=max(0.6, w * 0.02)))
        c.drawCircle(ix, iy, ir, paint((30, 20, 14), 0.8, stroke=ir * 0.15))
        c.drawCircle(ix, iy, ir * 0.44, paint((10, 6, 6)))
        c.drawRect(skia.Rect.MakeLTRB(x - w, up_y - h, x + w, up_y + h * 0.8),
                   paint(shader=lin((0, up_y - h * 0.1), (0, up_y + h * 0.8), [(70, 30, 30, 0.6), (70, 30, 30, 0.0)])))
        c.drawOval(skia.Rect.MakeXYWH(ix - ir * 0.62, iy - ir * 0.68, ir * 0.5, ir * 0.38), paint(WHITE, 0.95, blur=ir * 0.05))
        c.drawCircle(ix + ir * 0.36, iy + ir * 0.38, ir * 0.11, paint(WHITE, 0.6))
        c.restore()
        c.drawPath(path(lo, closed=False), paint((160, 90, 90), 0.6, stroke=w * 0.035))
        c.drawPath(path(lo, closed=False).makeTransform if False else path(lo, closed=False), paint((30, 18, 18), 0.25, stroke=w * 0.02))
    c.drawPath(path(up, closed=False), paint((22, 12, 12), stroke=w * (0.1 if open_ > 0.08 else 0.07)))
    for k in range(6):                                           # mascara'd outer lashes
        u = 0.55 + 0.45 * k / 5
        p = up[int(u * (len(up) - 1))]
        L = w * (0.12 + 0.07 * k / 5)
        ang = -math.pi / 2 + side * (0.45 + 0.6 * k / 5)
        q = (p[0] + L * math.cos(ang), p[1] + L * math.sin(ang))
        c.drawPath(path(bez(p, (p[0] + L * 0.6 * math.cos(ang - side * 0.3), p[1] + L * 0.6 * math.sin(ang - side * 0.3)), q, 6),
                        closed=False), paint((22, 12, 12), stroke=w * 0.04))
    cr = bez((inner + side * w * 0.04, y - h * 0.75), (x, up_y - h * 0.8 - h * 0.25 * open_), (outer + side * w * 0.06, y - h * 0.6), 12)
    c.drawPath(path(cr, closed=False), paint(SKIN_D, 0.65, stroke=w * 0.05, blur=w * 0.02))


def _brow(c, x, y, w, inner_lift, outer_lift, side):
    """Dark, strong brows (the wig is blue; the brows are her own): a thick tapered arch."""
    inner = (x - side * w * 0.52, y + w * 0.04 - inner_lift * w * 0.26)
    outer = (x + side * w * 0.6, y + w * 0.08 - outer_lift * w * 0.2)
    mid = (x + side * w * 0.12, y - w * 0.14 - (inner_lift + outer_lift) * w * 0.07)
    pts = bez(inner, mid, outer, 16)
    for i in range(len(pts) - 1):
        k = i / (len(pts) - 1)
        c.drawLine(*pts[i], *pts[i + 1], paint(BROW, 0.95, stroke=w * (0.2 - 0.12 * k)))
    for i in range(0, len(pts) - 2, 2):                            # hairs
        c.drawLine(pts[i][0], pts[i][1] + w * 0.04, pts[i + 1][0] + side * w * 0.03, pts[i + 1][1] - w * 0.03, paint((90, 60, 50), 0.6, stroke=1.6))


def _mouth(c, x, y, w, open_, smile, round_=0.0):
    """Hot-pink lipstick. open_ 0..1 (with the voice), smile -1..1, round_ 0..1 (an 'oo' or 'oh')."""
    mw = w * (0.5 - 0.17 * round_) * (1 + 0.12 * max(0, smile))
    gap = open_ * w * (0.3 + 0.12 * round_)
    cy_c = y - smile * w * 0.11
    up_mid = y - w * 0.03 - gap * 0.32
    lo_mid = y + gap * 0.7
    bow = [(x - mw, cy_c), (x - mw * 0.5, y - w * 0.07 - gap * 0.3), (x - mw * 0.14, y - w * 0.105 - gap * 0.3),
           (x, y - w * 0.075 - gap * 0.3), (x + mw * 0.14, y - w * 0.105 - gap * 0.3), (x + mw * 0.5, y - w * 0.07 - gap * 0.3),
           (x + mw, cy_c)]
    in_up = bez((x + mw * 0.95, cy_c), (x, up_mid + w * 0.02 - smile * w * 0.04), (x - mw * 0.95, cy_c), 22)
    in_lo = bez((x - mw * 0.95, cy_c), (x, lo_mid + w * 0.03 + smile * w * 0.05), (x + mw * 0.95, cy_c), 22)
    bot = bez((x + mw, cy_c), (x, lo_mid + w * 0.23 + smile * w * 0.02), (x - mw, cy_c), 22)
    if gap > 1.0:
        inside = path(np.vstack([in_up[::-1], in_lo[::-1]]))
        c.drawPath(inside, paint((70, 14, 26)))
        c.save()
        c.clipPath(inside, doAntiAlias=True)
        th = min(gap * 0.38, w * 0.08) + w * 0.015                 # upper teeth, following the lip's curve
        teeth = path(np.vstack([in_up[::-1], (in_up + np.array([0, th]))]))
        c.drawPath(teeth, paint(shader=lin((0, up_mid), (0, up_mid + th), [(252, 248, 238), (214, 204, 190)])))
        for k in range(-3, 4):
            tx_ = x + k * mw * 0.24
            c.drawLine(tx_, up_mid - w * 0.02, tx_, up_mid + th * 1.1, paint((170, 160, 150), 0.45, stroke=1.4))
        if open_ > 0.45:
            c.drawOval(skia.Rect.MakeLTRB(x - mw * 0.55, lo_mid - gap * 0.3, x + mw * 0.55, lo_mid + gap * 0.35), paint((196, 76, 96)))
        c.restore()
    up_lip = path(np.vstack([np.array(bow), in_up]))
    lo_lip = path(np.vstack([in_lo, bot]))
    c.drawPath(up_lip, paint(shader=lin((0, y - w * 0.12), (0, up_mid), [LIP, LIP_D])))
    c.drawPath(lo_lip, paint(shader=lin((0, lo_mid), (0, lo_mid + w * 0.22), [LIP_D, LIP, mix(LIP, INK, 0.15)], [0, 0.45, 1])))
    c.drawOval(skia.Rect.MakeXYWH(x - mw * 0.32, lo_mid + w * 0.07, mw * 0.55, w * 0.05), paint(WHITE, 0.55, blur=w * 0.015))
    c.drawOval(skia.Rect.MakeXYWH(x - mw * 0.4, y - w * 0.09 - gap * 0.3, mw * 0.3, w * 0.025), paint(WHITE, 0.3, blur=w * 0.01))
    if gap <= 1.0:
        c.drawPath(path(in_up, closed=False), paint((110, 20, 50), 0.9, stroke=w * 0.028))
    for sx in (-1, 1):                                            # the corners dimple with a smile
        c.drawCircle(x + sx * mw * 1.04, cy_c - smile * w * 0.02, w * 0.035, paint(SKIN_D, 0.3 + 0.35 * max(0, smile), blur=w * 0.02))


def star_pts(cx, cy, r, inner=0.45, rot=0.0, n=5):
    pts = []
    for i in range(n * 2):
        a = math.radians(rot) - math.pi / 2 + math.pi / n * i
        q = r if i % 2 == 0 else r * inner
        pts.append((cx + q * math.cos(a), cy + q * math.sin(a)))
    return pts


def head(c, T, mood="deadpan", talk=0.0, look=(0.0, 0.0), blink=0.0, turn=0.0, mood2=None, mk=0.0, round_=0.0, seed=0,
         glitter=True, neck=True):
    """Dot's head at the local origin (the face ~210 wide, chin at y = 136). talk 0..1 = mouth open; turn -1..1 nudges
    the features sideways for a 3/4 hint."""
    bi, bo, lid, smile, mwk, blush = blend_mood(mood, mood2, mk) if mood2 else _mood(mood)
    tx = turn * 16
    rng = np.random.default_rng(seed + 7)
    # the wig, behind: a full blunt bob with a little flip at the ends
    back = smooth([(-134, -70), (-118, -140), (-66, -178), (0, -186), (66, -178), (118, -140), (134, -70), (142, 30),
                   (150, 112), (126, 128), (100, 70), (-100, 70), (-126, 128), (-150, 112), (-142, 30)])
    c.drawPath(back, paint(shader=lin((0, -180), (0, 130), [WIG, WIG_D])))
    if neck:
        c.drawPath(path([(-46, 96), (46, 96), (52, 186), (-52, 186)]), paint(shader=lin((0, 100), (0, 186), [mix(SKIN_D, INK, 0.15), mix(SKIN, SKIN_D, 0.4)])))
    for sx in (-1, 1):
        c.drawOval(skia.Rect.MakeLTRB(sx * 106 - 15 + tx * 0.3, -14, sx * 106 + 15 + tx * 0.3, 46), paint(mix(SKIN, SKIN_D, 0.35)))
    # the face: forehead, cheekbones, a defined jaw and chin
    fp = smooth([(0 + tx * 0.2, -128), (66, -118), (98, -76), (104, -14), (100, 34), (86, 78), (60, 112), (26, 134), (0 + tx * 0.5, 138),
                 (-26, 134), (-60, 112), (-86, 78), (-100, 34), (-104, -14), (-98, -76), (-66, -118)])
    c.drawPath(fp, paint(SKIN))
    c.save()
    c.clipPath(fp, doAntiAlias=True)
    c.drawRect(skia.Rect.MakeLTRB(-120, -140, 120, 150), paint(shader=rad((-28 + tx, -30), 176, [(*SKIN_L, 0.75), (*SKIN, 0.0), (*SKIN_D, 0.8)],
                                                                         [0.0, 0.55, 1.0])))
    c.drawRect(skia.Rect.MakeLTRB(-120, -140, 120, 150), paint(shader=lin((58, 0), (110, 0), [(*SKIN_D, 0.0), (*SKIN_D, 0.55)])))
    for sx in (-1, 1):                                            # cheekbone contour and blush
        c.drawPath(path(bez((sx * 98, 0), (sx * 76, 40), (sx * 40, 58), 10), closed=False), paint(SKIN_D, 0.35, stroke=16, blur=10))
        c.drawCircle(sx * 58 + tx, 46, 34, paint((255, 100, 130), 0.16 + 0.42 * blush, blur=15))
    # the nose: bridge shadow, a lit ridge and tip, nostrils
    c.drawPath(path(bez((-14 + tx, -20), (-16 + tx * 1.1, 14), (-16 + tx * 1.2, 34), 10), closed=False), paint(SKIN_D, 0.35, stroke=6, blur=5))
    c.drawPath(path(bez((14 + tx, -20), (18 + tx * 1.1, 14), (18 + tx * 1.2, 36), 10), closed=False), paint(SKIN_D, 0.6, stroke=8, blur=6))
    c.drawPath(path(bez((0 + tx, -18), (2 + tx * 1.1, 12), (0 + tx * 1.2, 30), 10), closed=False), paint(SKIN_L, 0.55, stroke=6, blur=4))
    c.drawOval(skia.Rect.MakeXYWH(-22 + tx * 1.2, 36, 44, 18), paint(SKIN_D, 0.4, blur=5))
    for sx in (-1, 1):
        c.drawOval(skia.Rect.MakeXYWH(sx * 10 - 6 + tx * 1.2, 44, 12, 7), paint((110, 54, 46), 0.8, blur=1.2))
    c.drawCircle(-3 + tx * 1.2, 31, 8, paint(SKIN_L, 0.8, blur=4))
    c.drawOval(skia.Rect.MakeXYWH(-64, 116, 128, 44), paint(SKIN_D, 0.5, blur=10))           # under the chin
    c.drawPath(path(bez((-8 + tx, 54), (0 + tx, 62), (8 + tx, 54), 6), closed=False), paint(SKIN_D, 0.35, stroke=4, blur=2))  # philtrum
    c.restore()
    # the painted star round her left eye (screen right), a cheap brush, slightly patchy
    sp = star_pts(44 + tx, -8, 64, inner=0.47, rot=8)
    c.drawPath(path(sp), paint(BLUE, 0.9, stroke=8))
    c.drawPath(path(sp), paint((140, 200, 255), 0.55, stroke=2.4))
    # eyes and brows
    open_ = lid * (1 - blink)
    for sx in (-1, 1):
        _eye(c, sx * 42 + tx, -6, 58, open_, look, sx, seed + (3 if sx > 0 else 0), T)
        _brow(c, sx * 42 + tx * 0.9, -46, 56, bi, bo, sx)
    # glitter on the cheekbones: fine, with an occasional glint
    if glitter:
        g = np.random.default_rng(seed + 44)
        fr = int(T * 24)
        for sx in (-1, 1):
            for k in range(34):
                gx = sx * (44 + g.uniform(0, 44)) + tx
                gy = 22 + g.uniform(-10, 20) + (gx * sx - 44) * 0.14
                tw = (math.sin(fr * 0.7 + k * 2.1 + sx) + 1) / 2
                c.drawCircle(gx, gy, g.uniform(0.9, 1.8), paint(GOLD if k % 3 else (255, 250, 210), 0.5 + 0.5 * tw))
            k = (fr // 5 + (3 if sx > 0 else 0)) % 34
            gx = sx * (44 + 30 * ((k * 37) % 11) / 10) + tx
            gy = 24 + 12 * (((k * 53) % 7) / 6 - 0.5)
            c.drawLine(gx - 8, gy, gx + 8, gy, paint(WHITE, 0.9, stroke=1.5))
            c.drawLine(gx, gy - 8, gx, gy + 8, paint(WHITE, 0.9, stroke=1.5))
    _mouth(c, tx * 1.1, 80, 114 * mwk, talk, smile, round_)
    # the wig, in front: side locks (with strands) and the blunt fringe
    for sx in (-1, 1):
        lock = smooth([(sx * 94, -116), (sx * 132, -50), (sx * 138, 40), (sx * 150, 114), (sx * 122, 126), (sx * 104, 76),
                       (sx * 100, 0), (sx * 90, -84)])
        c.drawPath(lock, paint(shader=lin((sx * 92, 0), (sx * 146, 0), [WIG_L, WIG, WIG_D], [0, 0.35, 1])))
        for k in range(7):
            u = k / 6
            c.drawPath(path(bez((sx * (98 + 30 * u), -100 + 10 * u), (sx * (120 + 16 * u), 10), (sx * (108 + 36 * u), 116), 10), closed=False),
                       paint(WIG_D if k % 2 else WIG_L, 0.35, stroke=2.2))
    fr_pts = [(-116, -96), (-108, -150), (-62, -180), (0, -188), (62, -180), (108, -150), (116, -96)]
    bottom = []
    for i in range(17):
        u = i / 16
        bottom.append((116 - 232 * u, -62 - 6 * math.sin(u * math.pi) + rng.uniform(-5, 5) + (9 if i % 3 == 1 else 0)))
    c.drawPath(path(fr_pts + bottom), paint(shader=lin((0, -188), (0, -58), [WIG_L, WIG, mix(WIG, WIG_D, 0.45)], [0, 0.4, 1])))
    for i in range(40):                                           # strands, combed down to the cut
        u = (i + 0.5) / 40
        xx = -114 + 228 * u
        c.drawLine(xx * 0.45, -184 + abs(xx) * 0.2, xx + rng.uniform(-4, 4), -64 - 6 * math.sin(u * math.pi),
                   paint(WIG_D if i % 3 else WIG_L, 0.38, stroke=2))
    c.drawPath(path(bez((-90, -150), (0, -178), (90, -150), 16), closed=False), paint(WHITE, 0.5, stroke=10, blur=4))   # nylon sheen
    for sx in (-1, 1):                                            # gold hoops
        c.drawCircle(sx * 112, 70, 21, paint((150, 96, 0), stroke=6.5))
        c.drawCircle(sx * 112, 70, 21, paint(GOLD, stroke=4.5))
        c.drawArc(skia.Rect.MakeXYWH(sx * 112 - 21, 49, 42, 42), 200, 60, False, paint(WHITE, 0.85, stroke=2))


# ------------------------------------------------------------------ hands

def hand(c, x, y, ang, s=1.0, pose="open", skin=SKIN, flip=1):
    """A hand at the wrist (x, y), pointing along ang (degrees, 0 = down). Poses: open, point, fist, thumb_up,
    thumb_down, hold."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s * flip, s)
    pal = paint(shader=lin((-34, 0), (34, 0), [mix(skin, SKIN_L, 0.4), skin, SKIN_D]))
    edge = paint(SKIN_D, 0.7, stroke=2.2)
    if pose in ("fist", "hold", "thumb_up", "thumb_down"):
        r = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-34, 2, 34, 74), 26, 26)
        c.drawRRect(r, pal)
        c.drawRRect(r, edge)
        for k in range(3):
            c.drawLine(-17 + k * 17, 52, -17 + k * 17, 72, paint(SKIN_D, 0.7, stroke=2.6))
        if pose == "thumb_up":
            r = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-54, -34, -30, 34), 12, 12)
        elif pose == "thumb_down":
            r = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-54, 40, -30, 108), 12, 12)
        else:
            r = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-46, 14, -26, 52), 10, 10)
        c.drawRRect(r, pal)
        c.drawRRect(r, edge)
    else:
        palm = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-34, 0, 34, 62), 22, 22)
        fingers = [(-24, 104), (-8, 118), (8, 114), (24, 98)]
        if pose == "point":
            fingers = [(-24, 72), (-8, 130), (8, 74), (24, 70)]
        for i, (fx, L) in enumerate(fingers):
            spread = (i - 1.5) * (8 if pose == "open" else 2)
            c.save()
            c.translate(fx, 50)
            c.rotate(-spread)
            r = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-8.5, 0, 8.5, L - 46), 8.5, 8.5)
            c.drawRRect(r, pal)
            c.drawRRect(r, edge)
            c.drawOval(skia.Rect.MakeXYWH(-5, L - 60, 10, 12), paint((255, 70, 160), 0.95))      # hot-pink polish
            c.restore()
        c.drawRRect(palm, pal)
        c.drawRRect(palm, edge)
        c.save()
        c.translate(-34, 22)
        c.rotate(40)
        r = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-9, 0, 9, 56), 9, 9)
        c.drawRRect(r, pal)
        c.drawRRect(r, edge)
        c.restore()
    c.restore()


# ------------------------------------------------------------------ Doc, the sock

SOCK, SOCK_D = (250, 248, 240), (196, 190, 178)
STRIPES = (HOT, BLUE, GOLD)


def googly(c, x, y, r, T, seed=0, look=(0.0, 0.0), jig=1.0):
    """A googly eye: a clear dome over a loose black disc that rattles about."""
    c.drawCircle(x, y, r, paint(WHITE))
    c.drawCircle(x, y, r, paint(INK, stroke=max(1.5, r * 0.09)))
    a = T * 9.0 + seed * 2.3
    wob = jig * r * 0.18
    px = x + look[0] * r * 0.38 + wob * math.sin(a) + wob * 0.6 * math.sin(a * 2.7 + 1)
    py = y + r * 0.2 + look[1] * r * 0.3 + wob * 0.5 * math.cos(a * 1.3)
    c.drawCircle(px, py, r * 0.56, paint(INK))
    c.drawOval(skia.Rect.MakeXYWH(x - r * 0.62, y - r * 0.76, r * 0.72, r * 0.44), paint(WHITE, 0.9))
    c.drawCircle(x, y, r * 0.95, paint(WHITE, 0.3, stroke=r * 0.1))


def sock_head(c, T, open_=0.0, look=(0.4, 0.0), seed=0, mirror=True, mood="smile"):
    """Doc's head at the local origin, ~210 wide, facing +x (mirror the canvas to face left)."""
    gap = 6 + open_ * 64
    up = smooth([(-76, 8), (-82, -46), (-46, -94), (26, -100), (90, -70), (118, -16), (112, 8), (-20, 12)])
    lo = smooth([(-70, 0), (102, 0), (98, 34), (44, 52), (-30, 46), (-70, 24)])
    c.save()
    c.translate(0, gap * 0.45)
    c.rotate(open_ * 12)
    if open_ > 0.04:                                                          # the red felt mouth and pink tongue
        c.drawPath(smooth([(-46, -gap - 8), (108, -gap - 2), (104, 8), (-46, 12)]), paint((204, 24, 44)))
        c.drawOval(skia.Rect.MakeLTRB(14, -gap * 0.55 - 8, 84, -gap * 0.1 + 8), paint((255, 116, 150)))
    c.drawPath(lo, paint(shader=lin((0, 0), (0, 52), [SOCK, SOCK_D])))
    c.drawPath(lo, paint(SOCK_D, 0.9, stroke=2.5))
    c.restore()
    c.save()
    c.translate(0, -gap * 0.45)
    c.rotate(-open_ * 7)
    c.drawPath(up, paint(shader=rad((14, -52), 128, [WHITE, SOCK, SOCK_D], [0, 0.6, 1])))
    for k in range(12):
        c.drawLine(-64 + k * 15, -88 + abs(k - 5) * 3, -68 + k * 15, 8, paint(SOCK_D, 0.2, stroke=1.4))
    c.drawPath(up, paint(SOCK_D, 0.9, stroke=2.5))
    rng = np.random.default_rng(seed + 3)
    for k in range(10):                                                       # the orange yarn quiff
        bx = -34 + k * 8
        p = bez((bx, -90), (bx - 34 + rng.uniform(-10, 10), -156 - rng.uniform(0, 30)), (bx + 20, -98), 14)
        c.drawPath(path(p, closed=False), paint((240, 110, 20), stroke=8))
        c.drawPath(path(p, closed=False), paint((255, 196, 96), 0.75, stroke=2.6))
    if mirror:                                                                # the head mirror: foil on cardboard
        c.drawPath(path(bez((-80, -40), (10, -100), (100, -72), 16), closed=False), paint(INK, stroke=7))
        c.drawCircle(-8, -92, 32, paint(shader=rad((-16, -100), 38, [(250, 250, 255), (180, 186, 200), (106, 112, 128)])))
        for k in range(6):
            a = k * 1.1 + seed
            c.drawLine(-8 + 10 * math.cos(a), -92 + 10 * math.sin(a), -8 + 27 * math.cos(a + 0.3), -92 + 27 * math.sin(a + 0.3),
                       paint((140, 140, 160), 0.6, stroke=1.6))
        c.drawCircle(-8, -92, 32, paint((96, 72, 48), stroke=4))
        c.drawCircle(-8, -92, 6, paint(INK))
    googly(c, 28, -50, 24, T, seed, look)
    googly(c, 76, -44, 20, T + 0.37, seed + 1, look)
    if mood == "smile" and open_ < 0.05:                                       # a stitched grin at the fold
        c.drawPath(path(bez((40, 10), (80, 20), (110, 4), 8), closed=False), paint((204, 24, 44), stroke=4))
    c.restore()


def sock(c, ex, ey, wx, wy, T, open_=0.0, look=(0.4, 0.0), s=0.78, seed=0, mirror=True, face=1, tilt=0.0, mood="smile"):
    """Doc on a forearm from the elbow (ex, ey) to the wrist (wx, wy); the head is the hand, just past the wrist."""
    ang = math.atan2(wy - ey, wx - ex)
    L = math.hypot(wx - ex, wy - ey)
    ux, uy = math.cos(ang), math.sin(ang)
    w = 44
    c.save()
    c.translate(ex, ey)
    c.rotate(math.degrees(ang))
    tube = path([(-10, -w), (L + 30, -w * 1.08), (L + 30, w * 1.08), (-10, w)])
    c.drawPath(tube, paint(shader=lin((0, -w), (0, w), [SOCK_D, SOCK, SOCK, SOCK_D], [0, 0.3, 0.6, 1])))
    for i, cc in enumerate(STRIPES):
        x0 = 6 + i * 22
        c.drawRect(skia.Rect.MakeLTRB(x0, -w, x0 + 13, w), paint(cc))
    for k in range(int(L / 8)):
        c.drawLine(k * 8, -w, k * 8, w, paint(SOCK_D, 0.22, stroke=1.1))
    c.drawPath(tube, paint(SOCK_D, 0.8, stroke=2))
    c.restore()
    hx, hy = wx + ux * 70 * s / 0.78, wy + uy * 70 * s / 0.78
    c.save()
    c.translate(hx, hy)
    c.rotate(tilt)
    c.scale(s * face, s)
    sock_head(c, T, open_, look, seed, mirror, mood)
    c.restore()
    return hx, hy


# ------------------------------------------------------------------ the whole person

def _limb(c, pts, w, sleeve, dots=True):
    """A sleeve along a polyline (shoulder, elbow, wrist): one continuous round-jointed tube, lit from the left."""
    p = path(pts, closed=False)
    c.drawPath(p, paint(KNIT_D, stroke=w + 4))
    c.drawPath(p, paint(sleeve, stroke=w))
    c.drawPath(path([(x - w * 0.18, y - w * 0.05) for x, y in pts], closed=False), paint(WHITE, 0.5, stroke=w * 0.32, blur=w * 0.12))
    c.drawPath(path([(x + w * 0.26, y + w * 0.05) for x, y in pts], closed=False), paint(KNIT_D, 0.55, stroke=w * 0.28, blur=w * 0.12))
    if dots:
        for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
            n = math.hypot(x1 - x0, y1 - y0) or 1
            nx, ny = -(y1 - y0) / n, (x1 - x0) / n
            for k in range(int(n / 30)):
                u = (k + 0.5) * 30 / n
                j = 0.22 if k % 2 else -0.22
                c.drawCircle(x0 + (x1 - x0) * u + nx * w * j, y0 + (y1 - y0) * u + ny * w * j, 5.5, paint(INK, 0.88))


def _arm_pts(sx, sy, a1, a2, side, L1=200, L2=186):
    r1 = math.radians(a1) * side
    ex, ey = sx + L1 * math.sin(r1), sy + L1 * math.cos(r1)
    r2 = r1 + math.radians(a2) * side
    wx, wy = ex + L2 * math.sin(r2), ey + L2 * math.cos(r2)
    return (ex, ey), (wx, wy), -math.degrees(r2)


POSES = {      # (sock arm a1, a2 | free arm a1, a2); 0 = hanging down, a1 raises the upper arm outward, a2 bends the elbow
    "rest": (10, 6, 10, 6),
    "sock_up": (58, 122, 10, 6),         # Doc held up beside her face
    "sock_chest": (30, 110, 10, 6),      # Doc at chest height
    "sock_out": (70, 70, 10, 6),
    "point": (30, 110, 70, 22),          # pointing off to screen right
    "point_up": (30, 110, 150, 12),
    "palm": (30, 110, 26, 118),          # open palm by her chest
    "shrug": (30, 110, 50, 90),
    "thumb_up": (30, 110, 30, 128),
    "thumb_down": (30, 110, 22, 70),
    "wave": (30, 110, 140, 30),
    "mic": (30, 110, 18, 168),           # a hand mic up to her chin
    "hold": (30, 110, 24, 100),
    "both_up": (58, 122, 140, 30),
    "bare_hand": (52, 128, 10, 6),       # the sock off: the bare hand up, looked at
}


def dot(c, x, y, s, T, pose="rest", mood="deadpan", talk=0.0, look=(0.0, 0.0), blink=0.0, turn=0.0, tilt=0.0,
        sock_on=True, sock_open=0.0, sock_look=(0.4, 0.0), prop=None, hand_pose=None, mood2=None, mk=0.0, legs=True,
        breathe=True, seed=0, arms=None, sock_face=1, sock_tilt=0.0, round_=0.0, sock_mood="smile", hand2=None, headset=False,
        badge=None):
    """Dot, drawn with her feet at (x, y) (the floor), at scale s (~1600 px tall at s = 1). Returns canvas points:
    head, sock (Doc's head), hand (her free hand)."""
    a = POSES[pose] if arms is None else arms
    br = math.sin(T * 2 * math.pi / 3.6) * 2.5 if breathe else 0.0
    out = {}
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.translate(0, -1440)
    if legs:                                                    # high-waisted blue flared cords, gold glitter sneakers
        for sx in (-1, 1):
            leg = path([(sx * 8, 620), (sx * 112, 620), (sx * 104, 1040), (sx * 128, 1392), (sx * 18, 1392), (sx * 24, 1040)])
            c.drawPath(leg, paint(shader=lin((sx * 10, 0), (sx * 128, 0), [CORD, CORD_D] if sx > 0 else [CORD_D, CORD])))
            c.save()
            c.clipPath(leg, doAntiAlias=True)
            for k in range(9):
                xx = sx * (20 + k * 12)
                c.drawLine(xx, 620, xx + sx * k * 1.6, 1392, paint(CORD_D, 0.4, stroke=3))
            c.restore()
            shoe = smooth([(sx * 2, 1386), (sx * 140, 1380), (sx * 168, 1408), (sx * 154, 1440), (sx * 2, 1440)])
            c.drawPath(shoe, paint(shader=lin((0, 1380), (0, 1440), [(255, 236, 140), GOLD, (190, 120, 10)])))
            c.drawRect(skia.Rect.MakeLTRB(min(sx * 4, sx * 160), 1428, max(sx * 4, sx * 160), 1442), paint(WHITE))
            g = np.random.default_rng(seed + (5 if sx > 0 else 6))
            for k in range(34):
                c.drawCircle(sx * g.uniform(10, 150), g.uniform(1388, 1426), 2.0, paint(WHITE, 0.35 + 0.65 * ((int(T * 24) + k) % 7 == 0)))
        c.drawRect(skia.Rect.MakeLTRB(-114, 600, 114, 640), paint(GOLD))                       # a gold belt
        c.drawRect(skia.Rect.MakeLTRB(-114, 600, 114, 640), paint((170, 110, 0), stroke=3))
    # the cape behind: velvet folds, gold felt dots, pink lining at the edges
    cape = smooth([(-136, 226), (-206, 520), (-240, 860), (-252, 1120), (-120, 1150), (0, 1128), (120, 1150), (252, 1120), (240, 860),
                   (206, 520), (136, 226), (0, 196)])
    c.drawPath(cape, paint(shader=lin((-250, 0), (250, 0), [CAPE_D, CAPE, CAPE_L, CAPE, CAPE_D], [0, 0.22, 0.5, 0.78, 1])))
    c.save()
    c.clipPath(cape, doAntiAlias=True)
    for k in range(7):
        fx = -210 + k * 70
        c.drawLine(fx * 0.55, 260, fx, 1150, paint(CAPE_D, 0.45, stroke=16, blur=9))
        c.drawLine(fx * 0.55 + 18, 260, fx + 26, 1150, paint(CAPE_L, 0.25, stroke=8, blur=6))
    g = np.random.default_rng(seed + 11)
    for k in range(46):
        gx, gy = g.uniform(-250, 250), g.uniform(300, 1130)
        c.drawCircle(gx, gy, 12, paint(GOLD))
        c.drawCircle(gx - 3, gy - 3, 4.5, paint(WHITE, 0.45))
    c.restore()
    # torso: the polka-dot turtleneck, breathing
    c.save()
    c.translate(0, br * 0.3)
    torso = smooth([(-140, 232), (-132, 400), (-104, 560), (-108, 630), (108, 630), (104, 560), (132, 400), (140, 232), (58, 204),
                    (-58, 204)])
    c.drawPath(torso, paint(shader=lin((-140, 0), (140, 0), [KNIT_D, KNIT, WHITE, KNIT, KNIT_D], [0, 0.2, 0.45, 0.75, 1])))
    c.save()
    c.clipPath(torso, doAntiAlias=True)
    for row in range(14):
        for col_ in range(9):
            c.drawCircle(-150 + col_ * 36 + (18 if row % 2 else 0), 236 + row * 31, 5.5, paint(INK, 0.88))
    c.drawPath(path(bez((-120, 300), (0, 360), (120, 300), 12), closed=False), paint(KNIT_D, 0.5, stroke=10, blur=8))   # bust shading
    c.restore()
    for sx in (-1, 1):
        c.drawPath(smooth([(sx * 64, 212), (sx * 146, 232), (sx * 164, 520), (sx * 150, 760), (sx * 132, 520), (sx * 120, 256)]), paint(LINING))
    c.drawPath(path(star_pts(0, 232, 32, 0.45)), paint(shader=lin((-30, 200), (30, 264), [(255, 240, 150), GOLD, (190, 120, 0)])))
    c.drawPath(path(star_pts(0, 232, 32, 0.45)), paint((150, 90, 0), stroke=2.5))
    c.restore()
    la1, la2, ra1, ra2 = a
    sy = 252 + br * 0.3
    (lex, ley), (lwx, lwy), lang = _arm_pts(-136, sy, la1, la2, -1)
    (rex, rey), (rwx, rwy), rang = _arm_pts(136, sy, ra1, ra2, 1)
    # the free arm (screen right)
    _limb(c, [(136, sy), (rex, rey), (rwx, rwy)], 56, KNIT)
    hp = hand_pose or {"point": "point", "point_up": "point", "palm": "open", "thumb_up": "thumb_up", "thumb_down": "thumb_down",
                       "wave": "open", "mic": "hold", "hold": "hold", "shrug": "open", "both_up": "open"}.get(pose, "open")
    hand(c, rwx, rwy, rang, 0.9, hp, flip=-1)
    if prop is not None:
        prop(c, rwx, rwy, rang)
    out["hand"] = tuple(c.getTotalMatrix().mapXY(rwx, rwy))
    # the head
    c.save()
    c.translate(0, br * 0.4)
    c.rotate(tilt)
    head(c, T, mood, talk, look, blink, turn, mood2, mk, round_, seed)
    m = c.getTotalMatrix()
    out["head"] = (m.mapXY(0, 0).x(), m.mapXY(0, 0).y())
    c.restore()
    c.save()                                                    # the turtleneck collar, over the neck
    c.translate(0, br * 0.3)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-62, 160, 62, 234), 26, 26), paint(shader=lin((-62, 0), (62, 0), [KNIT_D, KNIT, WHITE, KNIT_D], [0, 0.35, 0.55, 1])))
    for k in range(7):
        c.drawLine(-51 + k * 17, 166, -51 + k * 17, 228, paint(KNIT_D, 0.7, stroke=3))
    c.drawPath(path(star_pts(0, 236, 32, 0.45)), paint(shader=lin((-30, 204), (30, 268), [(255, 240, 150), GOLD, (190, 120, 0)])))
    c.drawPath(path(star_pts(0, 236, 32, 0.45)), paint((150, 90, 0), stroke=2.5))
    if badge:                                                   # a lanyard and a work badge
        for sx in (-1, 1):
            c.drawLine(sx * 44, 222, sx * 18, 400, paint(HOT, stroke=10))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-78, 392, 78, 500), 10, 10), paint(WHITE))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-78, 392, 78, 500), 10, 10), paint((120, 120, 130), stroke=3))
        c.drawRect(skia.Rect.MakeLTRB(-78, 392, 78, 420), paint(HOT))
        K.text(c, badge, 0, 470, 36, "rubik-900", (40, 30, 60), tag="deco")
    c.restore()
    if headset:                                                 # a call-centre headset over the wig
        c.save()
        c.translate(0, br * 0.4)
        c.rotate(tilt)
        c.drawPath(path(bez((-128, 10), (0, -260), (128, 10), 24), closed=False), paint((40, 40, 46), stroke=14))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(112, -20, 160, 60), 16, 16), paint((40, 40, 46)))
        c.drawPath(path(bez((140, 50), (120, 110), (40, 100), 12), closed=False), paint((40, 40, 46), stroke=7))
        c.drawCircle(40, 100, 11, paint((60, 60, 66)))
        c.restore()
    # the sock arm (screen left), in front
    _limb(c, [(-136, sy), (lex, ley)], 56, KNIT)
    if sock_on:
        hx, hy = sock(c, lex, ley, lwx, lwy, T, sock_open, sock_look, 0.78, seed, face=sock_face, tilt=sock_tilt, mood=sock_mood)
        p = c.getTotalMatrix().mapXY(hx, hy)
        out["sock"] = (p.x(), p.y())
    else:
        _limb(c, [(lex, ley), (lwx, lwy)], 52, KNIT)
        hand(c, lwx, lwy, lang, 0.9, hand2 or "open")
        p = c.getTotalMatrix().mapXY(lwx, lwy)
        out["sock"] = (p.x(), p.y())
    c.restore()
    return out


# ------------------------------------------------------------------ the bad key

_WARM = [1.08, 0.02, 0, 0, 0.03, 0, 1.0, 0, 0, 0.0, 0, 0, 0.88, 0, -0.01, 0, 0, 0, 1, 0]
_HARD = [0] * 110 + [255] * 146                        # an aliased, thresholded alpha


class live:
    """with live(c, idx) as L: ... -> everything drawn on L is 'live action' keyed onto the plate: graded warmer than
    the world behind it, its own edges tinged green, a soft green spill halo and a hard, aliased matte line that
    chatter from frame to frame."""

    def __init__(self, c, idx=0, spill=K.KEY, halo=9.0, warm=True, a=1.0, edge=0.55, matte=True):
        self.c, self.idx, self.spill, self.halo, self.warm, self.a, self.edge, self.matte = c, idx, spill, halo, warm, a, edge, matte

    def __enter__(self):
        self.arr = np.zeros((K.H, K.W, 4), np.uint8)
        self.s = skia.Surface(self.arr)
        self.cc = self.s.getCanvas()
        self.cc.setMatrix(self.c.getTotalMatrix())
        return self.cc

    def __exit__(self, *a):
        from scipy import ndimage
        al = self.arr[..., 3]
        rows, cols = np.flatnonzero(al.any(axis=1)), np.flatnonzero(al.any(axis=0))
        if not len(rows):
            return
        rng = np.random.default_rng(self.idx * 7 + 3)
        halo = self.halo * rng.uniform(0.8, 1.25)
        m = int(halo * 3 + 10)
        y0, y1 = max(0, rows[0] - m), min(K.H, rows[-1] + m + 1)
        x0, x1 = max(0, cols[0] - m), min(K.W, cols[-1] + m + 1)
        crop = self.arr[y0:y1, x0:x1].copy()
        if self.edge > 0:                                  # the figure's own edges pick up green from the screen
            af = crop[..., 3].astype(np.float32) / 255
            sm = ndimage.uniform_filter(ndimage.uniform_filter(af[::2, ::2], 5), 5)
            sm = np.repeat(np.repeat(sm, 2, 0), 2, 1)[: af.shape[0], : af.shape[1]]
            e = np.clip((1 - sm) * 2.2, 0, 1) * (af > 0.02) * self.edge
            rgb = crop[..., :3].astype(np.float32)
            crop[..., :3] = np.clip(rgb * (1 - e[..., None]) + np.array(self.spill, np.float32) * e[..., None], 0, 255).astype(np.uint8)
        img = skia.Image.fromarray(crop)
        c = self.c
        c.save()
        c.resetMatrix()
        if self.a < 1:
            pa = skia.Paint()
            pa.setAlphaf(self.a)
            c.saveLayer(None, pa)
        so = skia.SamplingOptions()
        if halo > 0:                                       # the soft spill halo
            f = skia.ImageFilters.Blur(halo * 0.6, halo * 0.6, skia.TileMode.kDecal, skia.ImageFilters.Dilate(halo, halo))
            f = skia.ImageFilters.ColorFilter(skia.ColorFilters.Blend(K.col(self.spill, 0.62).toColor(), skia.BlendMode.kSrcIn), f)
            c.drawImage(img, x0, y0, so, skia.Paint(ImageFilter=f))
        if self.matte:                                     # the hard matte line, a few pixels wide, never still
            r = float(rng.uniform(1.6, 3.4))
            f = skia.ImageFilters.ColorFilter(skia.TableColorFilter.MakeARGB(_HARD, None, None, None), skia.ImageFilters.Dilate(r, r))
            f = skia.ImageFilters.ColorFilter(skia.ColorFilters.Blend(K.col(mix(self.spill, INK, 0.4)).toColor(), skia.BlendMode.kSrcIn), f)
            c.drawImage(img, x0 + float(rng.uniform(-1, 1)), y0 + float(rng.uniform(-1, 1)), so, skia.Paint(ImageFilter=f))
        p = skia.Paint()
        if self.warm:
            p.setColorFilter(skia.ColorFilters.Matrix(_WARM))
        c.drawImage(img, x0, y0, so, p)
        if self.a < 1:
            c.restore()
        c.restore()

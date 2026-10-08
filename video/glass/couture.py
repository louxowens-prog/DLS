"""Walking sculptures: the figures of the inner world, built like couture.

mask()      a glazed porcelain face (serene, symmetrical), eyes shut or open; open eyes can be glass or camera irises
lens()      a camera lens: gold barrel, coated glass, aperture blades that open and close
lens_fan()  the Curator's headdress: a vast aureole of lenses on gold rods, which can all turn to look at you
ribbed()    a ribbed biomechanical tube; shell() a glossy black lacquer shell
curator()   the ruling entity: porcelain face, lens aureole, black shell bodice, gold collar, blood-red gown and train
saint()     the narrator inside the dream: white and gold armour, a halo of rays, veils streaming in slow motion
doll()      a porcelain figure (workers, exhibits, crowds), jointed at shoulder, elbow and knee

All figures are original designs. Local units: (x, y) is the feet unless noted, y up is negative."""
import math

import numpy as np
import skia

import dream as D
import gel as G
import kit as K
from kit import BLACK, WHITE, mix, paint

GOLD, GOLD_HI, GOLD_LO = (214, 168, 70), (255, 232, 160), (110, 70, 18)
BLOOD, BLOOD_HI, BLOOD_LO = (150, 6, 20), (236, 50, 56), (60, 0, 8)
ROYAL, EMERALD, TEAL = (26, 52, 176), (10, 124, 84), (12, 122, 130)
LACQUER = (12, 10, 16)
PORC, PORC_SH, PORC_HI = (232, 228, 222), (138, 148, 176), (255, 255, 252)


def gold_shader(p0, p1, k=1.0):
    """Polished gold: bright bands and dark bands, like light running down a curved surface."""
    return K.lin(p0, p1, [GOLD_LO, GOLD, GOLD_HI, GOLD, GOLD_LO, GOLD, GOLD_HI], [0.0, 0.18, 0.32, 0.5, 0.68, 0.84, 1.0])


def _spec(c, x, y, rx, ry, a=0.8, ang=0.0, blur=2.0):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.drawOval(skia.Rect.MakeLTRB(-rx, -ry, rx, ry), G.glow_paint(WHITE, a, blur=blur))
    c.restore()


# ------------------------------------------------------------------ the face

def face_shape():
    return K.smooth([(0, -230), (84, -214), (136, -160), (150, -70), (144, 30), (124, 120), (90, 190), (44, 236), (0, 250),
                     (-44, 236), (-90, 190), (-124, 120), (-144, 30), (-150, -70), (-136, -160), (-84, -214)])


def mask(c, x, y, s, T, eyes=0.0, iris="glass", iris_col=(90, 120, 150), lips=(150, 8, 28), tint=PORC, shadow=PORC_SH,
         gold=1.0, talk=0.0, tilt=0.0, crack=0.0, a=1.0, light=(-0.5, -0.6), brows=0.6, seam=True, tear=0.0, open_=1.0,
         look=(0.0, 0.0), blush=0.0, smile=0.0):
    """A porcelain face centred at (x, y) = the bridge of the nose (about 300 x 480 px at s = 1).
    eyes: 0 shut (long serene lids) .. 1 open. iris: 'glass' or 'lens' (a camera aperture, open_ 0..1)."""
    c.save()
    c.translate(x, y)
    c.rotate(tilt)
    c.scale(s, s)
    lp = paint()
    lp.setAlphaf(a)
    c.saveLayer(None, lp)
    fp = face_shape()
    lx, ly = light
    c.drawPath(fp, paint(shader=K.rad((lx * 90, ly * 120 - 20), 330, [mix(tint, PORC_HI, 0.5), tint, mix(tint, shadow, 0.6), mix(shadow, BLACK, 0.35)],
                                      [0.0, 0.38, 0.78, 1.0])))
    c.save()
    c.clipPath(fp, doAntiAlias=True)
    c.drawPath(fp, paint(mix(shadow, BLACK, 0.3), 0.55, stroke=46, blur=22))                 # the glaze darkening round the edge
    c.drawRect(skia.Rect.MakeLTRB(-150, -112, 150, -40), paint(mix(shadow, BLACK, 0.2), 0.16, blur=18))   # under the brow
    c.drawPath(K.smooth([(-150, 150), (0, 120), (150, 150), (150, 260), (-150, 260)]), paint(mix(shadow, BLACK, 0.2), 0.22, blur=26))
    c.restore()
    # sculpted planes: temples, under the cheekbones, the jaw, the sides of the nose
    sh = mix(shadow, BLACK, 0.15)
    for sd in (-1, 1):
        c.drawPath(K.smooth([(sd * 150, -70), (sd * 120, 40), (sd * 70, 120), (sd * 96, 70), (sd * 124, -20)]), paint(sh, 0.35, blur=14))
        c.drawPath(K.smooth([(sd * 30, -40), (sd * 22, 40), (sd * 36, 70), (sd * 40, 20)]), paint(sh, 0.28, blur=8))
        c.drawOval(skia.Rect.MakeLTRB(sd * 60 - 46, -98, sd * 60 + 46, -60), paint(sh, 0.32, blur=12))       # the eye socket
    c.drawPath(K.smooth([(-90, 190), (0, 236), (90, 190), (40, 250), (-40, 250)]), paint(sh, 0.3, blur=10))
    if blush > 0:
        for sd in (-1, 1):
            c.drawCircle(sd * 82, 58, 40, paint((230, 120, 130), blush, blur=20))
    # brows: thin painted arches
    if brows > 0:
        for sd in (-1, 1):
            c.drawPath(K.bez_path([(sd * 26, -116), (sd * 66, -142), (sd * 112, -118)]), paint((60, 42, 46), 0.85 * brows, stroke=3.6))
    # eyes
    for sd in (-1, 1):
        ex, ey = sd * 62, -76
        if eyes < 0.08:
            lid = K.bez_path([(ex - 38, ey - 2), (ex, ey + 12), (ex + 38, ey - 2)])
            c.drawPath(K.smooth([(ex - 40, ey - 4), (ex - 14, ey - 24), (ex + 14, ey - 24), (ex + 40, ey - 4), (ex, ey + 12)]), paint(mix(tint, shadow, 0.35), 0.7))
            c.drawPath(lid, paint((54, 36, 42), 0.95, stroke=3.4))
            c.drawPath(K.bez_path([(ex - 36, ey - 10), (ex, ey - 30), (ex + 36, ey - 10)]), paint(sh, 0.45, stroke=4, blur=2))
            if gold > 0:
                c.drawPath(lid, paint(GOLD_HI, 0.55 * gold, stroke=1.2))
        else:
            k = min(1.0, eyes)
            top = ey - 4 - 20 * k
            eye = K.smooth([(ex - 40, ey), (ex - 20, top), (ex + 20, top), (ex + 40, ey), (ex + 20, ey + 10 * k + 4), (ex - 20, ey + 10 * k + 4)])
            c.save()
            c.clipPath(eye, doAntiAlias=True)
            gx, gy = look[0] * 10, look[1] * 6
            if iris == "lens":
                c.drawPath(eye, paint((4, 4, 8)))
                lens(c, ex + gx, ey - 6 * k + gy, 26 * k + 4, T, open_=open_, a=1.0, ring=(40, 34, 30), coat=(160, 30, 40))
            else:
                c.drawPath(eye, paint((236, 236, 232)))
                c.drawCircle(ex + gx, ey - 6 * k + gy, 17, paint(iris_col))
                c.drawCircle(ex + gx, ey - 6 * k + gy, 17, paint(mix(iris_col, BLACK, 0.5), stroke=3))
                c.drawCircle(ex + gx, ey - 6 * k + gy, 7, paint((6, 6, 10)))
                c.drawCircle(ex + gx - 5, ey - 11 * k + gy, 3.5, paint(WHITE))
            c.drawPath(K.path([(ex - 44, top - 6), (ex + 44, top - 6), (ex + 44, top + 8), (ex - 44, top + 12)]), paint(sh, 0.35, blur=4))
            c.restore()
            c.drawPath(K.bez_path([(ex - 40, ey), (ex, top - 6), (ex + 40, ey)]), paint((40, 26, 30), 0.95, stroke=3.2))
            if gold > 0:
                c.drawPath(K.bez_path([(ex - 40, ey), (ex, top - 8), (ex + 40, ey)]), paint(GOLD_HI, 0.5 * gold, stroke=1.2))
        if tear > 0:                                                       # a black glaze tear running down
            L = 160 * tear
            c.drawPath(K.capsule(ex + 6, ey + 10, ex + 10, ey + 10 + L, 7, 5), paint((10, 6, 10), 0.85))
    # nose: a clean ridge of light and two small shadows
    c.drawPath(K.smooth([(-6, -60), (6, -60), (12, 40), (-12, 40)]), paint(PORC_HI, 0.45, blur=5))
    for sd in (-1, 1):
        c.drawOval(skia.Rect.MakeLTRB(sd * 18 - 9, 48, sd * 18 + 9, 60), paint(sh, 0.5, blur=3))
    # lips
    m = talk * 16
    cw, cu = 40 + 22 * smile, 112 - 34 * smile                           # the corners: wider and higher as the smile is forced
    up = K.smooth([(-cw, cu), (-16, 102 + 6 * smile), (0, 106 + 6 * smile), (16, 102 + 6 * smile), (cw, cu), (14, 116 + 8 * smile), (-14, 116 + 8 * smile)])
    lo = K.smooth([(-cw, cu), (-14, 116 + m + 10 * smile), (14, 116 + m + 10 * smile), (cw, cu), (18, 132 + m + 12 * smile), (-18, 132 + m + 12 * smile)])
    if smile > 0:
        for sd in (-1, 1):                                                  # cheeks pushed up into hard round apples
            c.drawCircle(sd * 80, 52 - 10 * smile, 34, paint(PORC_HI, 0.35 * smile, blur=10))
            c.drawPath(K.bez_path([(sd * cw, cu), (sd * (cw + 10), cu - 8), (sd * (cw + 6), cu - 22)]), paint(sh, 0.5 * smile, stroke=3))
    if m > 1:
        c.drawPath(K.smooth([(-34, 113), (0, 110), (34, 113), (0, 116 + m)]), paint((20, 4, 8)))
    c.drawPath(up, paint(lips))
    c.drawPath(lo, paint(mix(lips, WHITE, 0.08)))
    c.drawOval(skia.Rect.MakeLTRB(-12, 120 + m, 12, 127 + m), paint(WHITE, 0.4, blur=2))
    # the gold seam of a mended thing, down the brow to the bridge of the nose
    if seam and gold > 0:
        sp = K.path([(0, -228), (-4, -190), (3, -160), (-2, -128), (0, -100)], closed=False)
        c.drawPath(sp, paint(GOLD, 0.95 * gold, stroke=4.5))
        c.drawPath(sp, paint(GOLD_HI, 0.8 * gold, stroke=1.5))
    # glaze: hard highlights
    for (hx, hy, rx, ry, k) in ((-56, -150, 40, 18, 0.55), (-92, 10, 14, 34, 0.35), (0, 0, 6, 28, 0.4), (60, 150, 14, 8, 0.3), (-10, 214, 18, 6, 0.3)):
        _spec(c, hx, hy, rx, ry, k, blur=5)
    if crack > 0:
        _crack(c, crack)
    c.restore()
    c.restore()


def _crack(c, k):
    """A hairline crack across the glaze, branching as it grows."""
    pts = [(-150, -40), (-96, -30), (-70, -2), (-30, -12), (-6, 30), (30, 26), (62, 64), (110, 58), (150, 90)]
    n = max(2, int(len(pts) * min(1.0, k)))
    p = K.path(pts[:n], closed=False)
    c.drawPath(p, paint((30, 20, 24), 0.9, stroke=3.0))
    c.drawPath(p, paint(WHITE, 0.6, stroke=1.0))
    if k > 0.5:
        for (a0, b0) in ((2, (-80, 40)), (4, (-20, 80)), (6, (70, 120))):
            if a0 < n:
                c.drawLine(*pts[a0], *b0, paint((30, 20, 24), 0.8 * (k - 0.5) * 2, stroke=2.0))


# ------------------------------------------------------------------ lenses

def lens(c, x, y, r, T, open_=1.0, a=1.0, ring=GOLD, coat=(110, 50, 200), glint=(-0.45, -0.5), blades=7, look=(0.0, 0.0), hot=0.0):
    """A camera lens seen face on: barrel rings, coated glass, an aperture (open_ 0..1), a glint. hot > 0 lights a red
    point at its heart (the moment it records)."""
    if r < 1.5:
        return
    c.save()
    c.translate(x, y)
    lp = paint()
    lp.setAlphaf(a)
    c.saveLayer(None, lp)
    c.drawCircle(0, 0, r, paint(shader=K.lin((-r, -r), (r, r), [mix(ring, WHITE, 0.5), ring, mix(ring, BLACK, 0.6)])))
    c.drawCircle(0, 0, r * 0.86, paint((8, 8, 10)))
    for k, w in ((0.84, 0.04), (0.74, 0.03)):
        c.drawCircle(0, 0, r * k, paint(mix(ring, BLACK, 0.3), 0.9, stroke=max(0.6, r * w)))
    gx, gy = look[0] * r * 0.12, look[1] * r * 0.12
    c.drawCircle(gx, gy, r * 0.68, paint(shader=K.rad((gx - r * 0.2, gy - r * 0.2), r * 0.8, [mix(coat, WHITE, 0.15), mix(coat, BLACK, 0.55), (4, 4, 8)])))
    # the aperture: blades closing to an n-gon
    ap = max(0.04, open_) * r * 0.5
    if open_ < 0.999:
        bl = skia.Path()
        bl.addCircle(gx, gy, r * 0.62)
        hole = skia.Path()
        for i in range(blades):
            ang = 2 * math.pi * i / blades + T * 0.0 + (1 - open_) * 0.9
            px, py = gx + ap * math.cos(ang), gy + ap * math.sin(ang)
            (hole.moveTo if i == 0 else hole.lineTo)(px, py)
        hole.close()
        blade = skia.Op(bl, hole, skia.PathOp.kDifference_PathOp)
        if blade is not None:
            c.drawPath(blade, paint((26, 24, 28)))
            for i in range(blades):                                        # blade edges
                ang = 2 * math.pi * i / blades + (1 - open_) * 0.9
                px, py = gx + ap * math.cos(ang), gy + ap * math.sin(ang)
                c.drawLine(px, py, gx + r * 0.62 * math.cos(ang + 0.9), gy + r * 0.62 * math.sin(ang + 0.9), paint((70, 66, 72), 0.8, stroke=max(0.5, r * 0.012)))
    if hot > 0:
        G.pool(c, gx, gy, r * 0.5, (255, 30, 30), 0.9 * hot)
        c.drawCircle(gx, gy, r * 0.06, paint((255, 200, 190), hot))
    # reflections: a bright arc and a little window
    c.drawArc(skia.Rect.MakeLTRB(-r * 0.6, -r * 0.6, r * 0.6, r * 0.6), 200, 50, False, paint(WHITE, 0.55, stroke=max(0.8, r * 0.05)))
    _spec(c, glint[0] * r * 0.5, glint[1] * r * 0.5, r * 0.11, r * 0.07, 0.9, ang=-35, blur=max(0.5, r * 0.02))
    c.drawArc(skia.Rect.MakeLTRB(-r * 0.4, -r * 0.4, r * 0.4, r * 0.4), 20, 40, False, paint((140, 255, 200), 0.35, stroke=max(0.6, r * 0.03)))
    c.restore()
    c.restore()


def lens_fan(c, x, y, s, T, open_=1.0, swivel=0.0, a=1.0, rings=((250, 13, 26), (360, 19, 30), (480, 25, 34)), spread=1.0,
             hot=0.0, seed=0, stutter=None):
    """The aureole: arcs of lenses on gold rods radiating from (x, y) (the back of the head) across the upper half
    circle. swivel (-1..1) turns every lens towards a direction; stutter (a time) makes them snap round in jerks."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    lp = paint()
    lp.setAlphaf(a)
    c.saveLayer(None, lp)
    a0, a1 = math.radians(180 + 8 - 20 * (spread - 1)), math.radians(360 - 8 + 20 * (spread - 1))
    # rods first, then a filigree arc per ring
    for R, n, r in rings:
        for i in range(n):
            ang = a0 + (a1 - a0) * (i + 0.5) / n
            px, py = R * math.cos(ang), R * math.sin(ang)
            c.drawLine(0, 0, px, py, paint(GOLD, 0.65, stroke=4.0))
            c.drawLine(0, 0, px, py, paint(GOLD_HI, 0.5, stroke=1.2))
        c.drawArc(skia.Rect.MakeLTRB(-R, -R, R, R), math.degrees(a0), math.degrees(a1 - a0), False, paint(GOLD, 0.8, stroke=5))
    rng = K.rng_at(seed, 53)
    for R, n, r in rings:
        for i in range(n):
            ang = a0 + (a1 - a0) * (i + 0.5) / n
            px, py = R * math.cos(ang), R * math.sin(ang)
            ph = rng.uniform(0, 6.28)
            sw = swivel if stutter is None else swivel * (1 if (int(stutter * 6 + ph) % 3) else 0)
            lk = (math.cos(ang) * -0.4 + sw * 0.9, math.sin(ang) * -0.4 + 0.1 * math.sin(T + ph))
            lens(c, px, py, r, T, open_=open_, ring=GOLD, coat=(120 + 80 * (i % 2), 40, 160 - 60 * (i % 3) // 2), look=lk,
                 glint=(-0.45 + 0.3 * sw, -0.5), hot=hot * (0.5 + 0.5 * math.sin(T * 3 + ph)))
    c.restore()
    c.restore()


# ------------------------------------------------------------------ biomechanics

def ribbed(c, pts, r0, r1=None, col=(26, 22, 28), T=0.0, a=1.0, ribs=1.0, pulse=0.0, hi=(255, 240, 220)):
    """A ribbed tube along a polyline/curve of points: a glossy dark body, then rings across it like cartilage."""
    r1 = r0 if r1 is None else r1
    pts = [tuple(map(float, p)) for p in pts]
    n = len(pts)
    L = [0.0]
    for i in range(1, n):
        L.append(L[-1] + math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]))
    tot = L[-1] + 1e-6
    for i in range(n - 1):
        (xa, ya), (xb, yb) = pts[i], pts[i + 1]
        ra = r0 + (r1 - r0) * L[i] / tot
        rb = r0 + (r1 - r0) * L[i + 1] / tot
        c.drawPath(K.capsule(xa, ya, xb, yb, ra * 2, rb * 2), paint(col, a))
    step = max(6.0, (r0 + r1) * 0.42) / ribs
    d = (T * 40 * pulse) % step
    while d < tot:
        j = max(0, min(n - 2, int(np.searchsorted(L, d) - 1)))
        u = (d - L[j]) / max(1e-6, L[j + 1] - L[j])
        x = pts[j][0] + (pts[j + 1][0] - pts[j][0]) * u
        y = pts[j][1] + (pts[j + 1][1] - pts[j][1]) * u
        dx, dy = pts[j + 1][0] - pts[j][0], pts[j + 1][1] - pts[j][1]
        ln = math.hypot(dx, dy) + 1e-6
        nx, ny = -dy / ln, dx / ln
        r = r0 + (r1 - r0) * d / tot
        bulge = 1.0 + 0.12 * pulse * math.sin(d * 0.05 - T * 6)
        c.drawLine(x + nx * r * bulge, y + ny * r * bulge, x - nx * r * bulge, y - ny * r * bulge, paint(mix(col, BLACK, 0.5), a, stroke=r * 0.32))
        c.drawLine(x + nx * r * 0.85 + dx / ln * r * 0.12, y + ny * r * 0.85 + dy / ln * r * 0.12, x + nx * r * 0.1 + dx / ln * r * 0.12,
                   y + ny * r * 0.1 + dy / ln * r * 0.12, paint(hi, 0.35 * a, stroke=max(1.0, r * 0.1)))
        d += step


def shell(c, x, y, rx, ry, ang=0.0, col=LACQUER, a=1.0, rim=GOLD, rim_k=1.0, spec=0.85):
    """A glossy lacquer shell (a beetle's wing case): a dark oval, a hard crescent of light, a thin gold edge."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    p = K.smooth([(0, -ry), (rx * 0.8, -ry * 0.6), (rx, 0), (rx * 0.7, ry * 0.75), (0, ry), (-rx * 0.7, ry * 0.75), (-rx, 0), (-rx * 0.8, -ry * 0.6)])
    c.drawPath(p, paint(shader=K.lin((-rx, -ry), (rx, ry), [mix(col, (90, 90, 110), 0.5), col, mix(col, BLACK, 0.6)]), a=a))
    c.drawPath(K.smooth([(-rx * 0.6, -ry * 0.6), (-rx * 0.1, -ry * 0.86), (rx * 0.3, -ry * 0.7), (-rx * 0.2, -ry * 0.55)]), G.glow_paint(WHITE, spec * a, blur=max(1, rx * 0.04)))
    if rim_k > 0:
        c.drawPath(p, paint(rim, 0.9 * a * rim_k, stroke=max(1.2, rx * 0.06)))
    c.restore()


# ------------------------------------------------------------------ the Curator

def gown_pool(c, x, y, s, T, col=BLOOD, spread=1.0, a=1.0, folds=14, seed=0, slow=0.3):
    """The gown spilling into a vast pool of silk round the feet (x, y), radial folds rippling slowly outwards."""
    rx, ry = 900 * s * spread, 260 * s * spread
    t = T * slow
    pts = []
    for i in range(48):
        ang = 2 * math.pi * i / 48
        w = 1 + 0.06 * math.sin(ang * 5 + t * 2 + seed) + 0.04 * math.sin(ang * 9 - t * 3)
        pts.append((x + rx * w * math.cos(ang), y + ry * w * math.sin(ang) * (0.9 if math.sin(ang) < 0 else 1.0)))
    p = K.smooth(pts)
    c.drawPath(p, paint(shader=K.rad((x, y - 40 * s), rx, [mix(col, BLOOD_HI, 0.5), col, mix(col, BLACK, 0.55)], [0.0, 0.55, 1.0]), a=a))
    for i in range(folds):                                           # folds radiating from the hem
        ang = math.pi * (0.08 + 0.84 * i / (folds - 1)) + 0.04 * math.sin(t * 1.3 + i)
        x1, y1 = x + rx * 0.95 * math.cos(ang), y + ry * 0.95 * math.sin(ang)
        x0, y0 = x + 120 * s * math.cos(ang), y + 40 * s * math.sin(ang)
        c.drawLine(x0, y0, x1, y1, paint(mix(col, BLACK, 0.5), 0.45 * a, stroke=26 * s, blur=10 * s))
        c.drawLine(x0 + 18 * s, y0, x1 + 30 * s, y1, paint(mix(col, BLOOD_HI, 0.6), 0.32 * a, stroke=8 * s, blur=4 * s))
    c.drawPath(p, paint(GOLD, 0.7 * a, stroke=6 * s))


def curator(c, x, y, s, T, eyes=0.0, open_=1.0, talk=0.0, fan=1.0, swivel=0.0, gown=1.0, arms="open", a=1.0, hot=0.0, train=True,
            stutter=None, tear=0.0, crack=0.0, veil_k=1.0, fan_open=1.0):
    """The Curator, full length: feet at (x, y), about 1500 px to the crown at s = 1 (the aureole rises far above)."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    lp = paint()
    lp.setAlphaf(a)
    c.saveLayer(None, lp)
    hx, hy = 0, -1350                                               # the bridge of the nose
    # --- the black veil behind everything, and the aureole
    if veil_k > 0:
        for sd in (-1, 1):
            D.veil(c, T, sd * 40, hy - 120, 900, 120, col=(10, 8, 14), a=0.55 * veil_k, wind=(sd * 0.25, 1.0), seed=sd + 3, slow=0.3, flip=1)
    # --- ribbed tubes from the shoulder blades, out and up, plugged into the aureole's inner ring
    for sd in (-1, 1):
        ribbed(c, [(sd * 140, -1090), (sd * 270, -1170), (sd * 330, -1300), (sd * 300, -1420), (sd * 230, -1500)], 24, 16, T=T, pulse=0.6)
    if fan > 0:
        lens_fan(c, hx, hy - 30, 1.0 * fan_open + 0.0001, T, open_=open_, swivel=swivel, a=fan, hot=hot, stutter=stutter)
    # --- the gown: a pool of blood-red silk, the skirt falling into it
    if gown > 0 and train:
        gown_pool(c, 0, 0, 1.0, T, spread=gown)
    skirt = K.smooth([(-150, -760), (150, -760), (260, -300), (420, -20), (0, 30), (-420, -20), (-260, -300)])
    c.drawPath(skirt, paint(shader=K.lin((-420, 0), (420, 0), [BLOOD_LO, BLOOD, BLOOD_HI, BLOOD, BLOOD_LO], [0.0, 0.3, 0.5, 0.72, 1.0])))
    for i in range(7):                                               # long falling folds
        fx = -300 + i * 100
        c.drawPath(K.bez_path([(fx * 0.4, -740), (fx * 0.75, -380), (fx * 1.1, -10)]), paint(mix(BLOOD, BLACK, 0.5), 0.5, stroke=14, blur=6))
        c.drawPath(K.bez_path([(fx * 0.4 + 14, -740), (fx * 0.75 + 16, -380), (fx * 1.1 + 22, -10)]), paint(BLOOD_HI, 0.25, stroke=5, blur=3))
    # --- the bodice: overlapping lacquer shells, a gold girdle
    torso = K.smooth([(-150, -760), (-170, -930), (-200, -1080), (-120, -1130), (120, -1130), (200, -1080), (170, -930), (150, -760)])
    c.drawPath(torso, paint(LACQUER))
    for row in range(5):
        yy = -800 - row * 64
        n = 4 if row % 2 else 3
        for i in range(n):
            xx = (i - (n - 1) / 2) * 92
            shell(c, xx, yy, 56, 44, ang=0, a=1.0, rim_k=0.8)
    c.drawPath(K.smooth([(-160, -790), (0, -740), (160, -790), (150, -760), (0, -712), (-150, -760)]), paint(shader=gold_shader((-160, 0), (160, 0))))
    # shoulders: great curved shells like folded wings
    for sd in (-1, 1):
        shell(c, sd * 210, -1090, 110, 64, ang=sd * 18, rim_k=1.0)
        shell(c, sd * 250, -1040, 80, 50, ang=sd * 30, rim_k=1.0)
    # --- arms in black, porcelain hands, gold claws
    poses = {"open": [((-210, -1060), (-330, -900), (-430, -760)), ((210, -1060), (330, -900), (430, -760))],
             "raised": [((-210, -1060), (-360, -1180), (-420, -1360)), ((210, -1060), (360, -1180), (420, -1360))],
             "down": [((-200, -1060), (-240, -880), (-230, -700)), ((200, -1060), (240, -880), (230, -700))],
             "offer": [((-200, -1060), (-260, -900), (-120, -820)), ((200, -1060), (260, -900), (120, -820))]}
    for sh_, el, wr in poses.get(arms, poses["open"]):
        c.drawPath(K.capsule(sh_[0], sh_[1], el[0], el[1], 64, 48), paint(LACQUER))
        c.drawPath(K.capsule(el[0], el[1], wr[0], wr[1], 48, 36), paint(LACQUER))
        c.drawPath(K.capsule(sh_[0], sh_[1], el[0], el[1], 64, 48), paint((90, 90, 110), 0.25, stroke=3))
        hand(c, wr[0], wr[1], 1.0, math.degrees(math.atan2(wr[1] - el[1], wr[0] - el[0])) - 90, T)
    # --- the collar: stacked gold rings up the neck
    for i in range(7):
        yy = -1135 - i * 22
        w = 74 - i * 3
        c.drawPath(K.rrect(-w, yy - 12, w, yy + 10, 10), paint(shader=gold_shader((-w, yy - 12), (w, yy + 10))))
        c.drawLine(-w, yy + 10, w, yy + 10, paint(GOLD_LO, 0.8, stroke=2))
    # --- the head: a fitted black cap, the porcelain face
    c.drawPath(K.smooth([(-150, -1330), (-140, -1470), (-90, -1560), (0, -1590), (90, -1560), (140, -1470), (150, -1330), (120, -1300), (-120, -1300)]),
               paint(LACQUER))
    mask(c, hx, hy, 0.5, T, eyes=eyes, iris="lens", open_=open_, talk=talk, tear=tear, crack=crack, lips=(140, 0, 20))
    c.drawPath(K.bez_path([(-140, -1440), (0, -1500), (140, -1440)]), paint(shader=gold_shader((-140, 0), (140, 0))), )
    c.restore()
    c.restore()


def hand(c, x, y, s, ang, T, col=PORC, claws=GOLD, open_=1.0, a=1.0):
    """A long porcelain hand, fingers together and slightly spread, each finger capped in a gold claw."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    c.drawPath(K.smooth([(-26, -10), (26, -10), (30, 60), (-30, 60)]), paint(col, a))
    for i, (dx, L) in enumerate(((-24, 90), (-8, 112), (8, 118), (24, 100))):
        sp = (i - 1.5) * 6 * open_
        x0, y0, x1, y1 = dx, 50, dx + sp, 50 + L
        c.drawPath(K.capsule(x0, y0, x1, y1, 15, 11), paint(col, a))
        c.drawPath(K.path([(x1 - 6, y1 - 18), (x1 + 6, y1 - 18), (x1 + sp * 0.2, y1 + 34)]), paint(shader=gold_shader((x1 - 6, 0), (x1 + 6, 0)), a=a))
    c.drawPath(K.capsule(-30, 20, -60, 80, 18, 13), paint(col, a))                                     # thumb
    c.drawPath(K.path([(-66, 72), (-54, 72), (-64, 110)]), paint(GOLD, a))
    c.drawPath(K.smooth([(-26, -10), (26, -10), (30, 60), (-30, 60)]), paint(PORC_SH, 0.3 * a, blur=6))
    c.restore()


# ------------------------------------------------------------------ the saint (the narrator, inside)

def saint(c, x, y, s, T, a=1.0, halo=1.0, veil_k=1.0, lamp=1.0, eyes=0.85, talk=0.0, wind=(1.0, 0.15), cape=1.0, crack=0.0,
          look=(0.0, 0.0)):
    """The narrator as she appears in the dream: an armoured saint in white, silver and gold, a halo of fine rays, a long
    veil and cape streaming in slow motion, a small glass lamp. Feet at (x, y), about 1400 px tall at s = 1."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    lp = paint()
    lp.setAlphaf(a)
    c.saveLayer(None, lp)
    hy = -1240
    # halo: a sunburst of fine gold rays and a ring
    if halo > 0:
        for i in range(72):
            ang = 2 * math.pi * i / 72 + T * 0.03
            L = (300 if i % 2 else 380) * halo
            c.drawLine(math.cos(ang) * 120, hy - 20 + math.sin(ang) * 120, math.cos(ang) * L, hy - 20 + math.sin(ang) * L,
                       paint(GOLD_HI, 0.55 * halo, stroke=2.0 if i % 2 else 3.2))
        c.drawCircle(0, hy - 20, 200, paint(GOLD, 0.9 * halo, stroke=7))
        G.pool(c, 0, hy - 20, 420, (255, 230, 170), 0.3 * halo)
    # cape and veil behind
    if cape > 0:
        for sd in (-1, 1):
            D.veil(c, T, sd * 150, -1060, 1200 * cape, 260, col=(246, 244, 240), a=0.85, wind=(wind[0] * 0.6 + sd * 0.15, 0.9), seed=sd * 2 + 1, slow=0.3)
    if veil_k > 0:
        D.veil(c, T, 40, hy - 150, 900, 150, col=(255, 255, 252), a=0.55 * veil_k, wind=wind, seed=7, slow=0.32)
    # gown
    c.drawPath(K.smooth([(-170, -700), (170, -700), (300, -200), (360, 10), (-360, 10), (-300, -200)]),
               paint(shader=K.lin((-360, 0), (360, 0), [(150, 156, 176), (222, 224, 232), (240, 240, 244), (204, 208, 220), (132, 138, 160)])))
    for i in range(6):
        fx = -250 + i * 100
        c.drawPath(K.bez_path([(fx * 0.5, -690), (fx * 0.8, -350), (fx * 1.1, 0)]), paint((120, 126, 150), 0.45, stroke=12, blur=6))
    c.drawPath(K.smooth([(-170, -700), (0, -650), (170, -700), (160, -680), (0, -626), (-160, -680)]), paint(shader=gold_shader((-170, 0), (170, 0))))
    # armour: a breastplate of polished silver, gold edges; petal pauldrons
    bp = K.smooth([(-150, -700), (-170, -880), (-150, -1010), (-60, -1050), (60, -1050), (150, -1010), (170, -880), (150, -700), (0, -660)])
    c.drawPath(bp, paint(shader=K.lin((-170, -1000), (170, -700), [(236, 240, 248), (120, 130, 152), (214, 220, 232), (70, 78, 98), (190, 198, 214)])))
    c.drawPath(bp, paint(GOLD, 0.95, stroke=6))
    c.drawPath(K.path([(0, -1040), (0, -680)], closed=False), paint(GOLD, 0.8, stroke=4))
    _spec(c, -70, -940, 30, 70, 0.55, ang=10, blur=8)
    for sd in (-1, 1):
        for k in range(3):
            c.save()
            c.translate(sd * (150 + k * 22), -1000 + k * 40)
            c.rotate(sd * (20 + k * 12))
            petal = K.smooth([(0, -50), (60, -30), (80, 20), (40, 50), (-30, 40), (-50, 0)])
            c.drawPath(petal, paint(shader=K.lin((-50, -50), (80, 50), [(240, 244, 250), (110, 120, 144)])))
            c.drawPath(petal, paint(GOLD, 0.9, stroke=4))
            c.restore()
    # arms: one holding the lamp out in front, one at her side
    arm = lambda x0, y0, x1, y1, w0, w1: c.drawPath(K.capsule(x0, y0, x1, y1, w0, w1), paint(shader=K.lin((min(x0, x1) - 30, 0), (max(x0, x1) + 30, 0),
                                                                                                    [(130, 138, 160), (226, 230, 240), (120, 128, 150)])))
    arm(-170, -980, -230, -760, 54, 44)
    arm(-230, -760, -150, -620, 44, 36)
    arm(170, -980, 240, -760, 54, 44)
    arm(240, -760, 230, -560, 44, 36)
    if lamp > 0:
        lx, ly = -150, -560
        c.drawLine(lx, ly - 60, lx, ly - 20, paint(GOLD, stroke=4))
        G.pool(c, lx, ly + 20, 260, (255, 230, 170), 0.45 * lamp)
        c.drawPath(K.smooth([(lx - 34, ly - 20), (lx + 34, ly - 20), (lx + 40, ly + 40), (lx, ly + 70), (lx - 40, ly + 40)]), paint((255, 246, 220), 0.9 * lamp))
        c.drawPath(K.smooth([(lx - 34, ly - 20), (lx + 34, ly - 20), (lx + 40, ly + 40), (lx, ly + 70), (lx - 40, ly + 40)]), paint(GOLD, 0.9, stroke=3))
        c.drawCircle(lx, ly + 22, 16, G.glow_paint(WHITE, lamp))
    # the hood: close white silk round the face
    hood = K.smooth([(-118, -1130), (-122, -1290), (-84, -1374), (0, -1400), (84, -1374), (122, -1290), (118, -1130), (80, -1070), (-80, -1070)])
    c.drawPath(hood, paint(shader=K.lin((-122, 0), (122, 0), [(120, 128, 150), (210, 214, 226), (236, 238, 244), (196, 202, 218), (104, 112, 136)])))
    c.drawPath(hood, paint((90, 96, 118), 0.6, stroke=3))
    mask(c, 0, hy + 10, 0.4, T, eyes=eyes, iris="glass", iris_col=(120, 150, 170), lips=(170, 70, 80), gold=1.0, talk=talk, seam=False, crack=crack,
         look=look, brows=0.9)
    c.drawPath(K.smooth([(-66, -1338), (0, -1352), (66, -1338), (70, -1326), (0, -1338), (-70, -1326)]), paint(shader=gold_shader((-70, 0), (70, 0))))
    c.restore()
    c.restore()


# ------------------------------------------------------------------ porcelain people

DOLL_POSES = {
    # (shoulder->elbow->wrist) left and right, hip->knee->ankle left and right, in local units (feet at 0)
    "stand": ([(-70, -560), (-90, -420), (-96, -290)], [(70, -560), (90, -420), (96, -290)], [(-36, -330), (-40, -170), (-42, 0)], [(36, -330), (40, -170), (42, 0)]),
    "walk": ([(-70, -560), (-110, -430), (-80, -300)], [(70, -560), (60, -420), (110, -320)], [(-36, -330), (-80, -170), (-110, 0)], [(36, -330), (50, -160), (70, 0)]),
    "type": ([(-70, -560), (-100, -430), (-40, -380)], [(70, -560), (100, -430), (40, -380)], [(-36, -330), (-48, -290), (-54, -110)], [(36, -330), (48, -290), (54, -110)]),
    "bow": ([(-70, -500), (-60, -360), (-30, -260)], [(70, -500), (60, -360), (30, -260)], [(-36, -330), (-40, -170), (-42, 0)], [(36, -330), (40, -170), (42, 0)]),
    "arms_up": ([(-70, -560), (-150, -660), (-170, -800)], [(70, -560), (150, -660), (170, -800)], [(-36, -330), (-40, -170), (-42, 0)], [(36, -330), (40, -170), (42, 0)]),
    "kneel": ([(-70, -400), (-80, -270), (-60, -160)], [(70, -400), (80, -270), (60, -160)], [(-36, -170), (-60, 0), (-150, 10)], [(36, -170), (60, 0), (150, 10)]),
    "candle": ([(-70, -560), (-90, -440), (-20, -420)], [(70, -560), (90, -440), (20, -420)], [(-36, -330), (-40, -170), (-42, 0)], [(36, -330), (40, -170), (42, 0)]),
}


def doll(c, x, y, s, T, pose="stand", tint=PORC, shade=PORC_SH, a=1.0, head_turn=0.0, eyes=0.0, face=True, hair=None, dress=None,
         crack=0.0, light=(-0.5, -0.6), joints=GOLD, mouth=True, head_tilt=0.0):
    """A porcelain figure (about 720 px tall at s = 1, feet at x, y): a smooth egg of a head with a serene painted face,
    a sculpted body, gold ball joints. hair: a colour for a sculpted ponytail; dress: a colour for a simple shift."""
    arms_l, arms_r, leg_l, leg_r = DOLL_POSES.get(pose, DOLL_POSES["stand"])
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    lp = paint()
    lp.setAlphaf(a)
    c.saveLayer(None, lp)
    sh = lambda p0, p1: K.lin(p0, p1, [mix(tint, PORC_HI, 0.5), tint, mix(tint, shade, 0.7)])
    top = -560 if pose not in ("bow", "kneel") else (-500 if pose == "bow" else -400)
    hip = -330 if pose != "kneel" else -170
    for (h, k, f) in (leg_l, leg_r):
        c.drawPath(K.capsule(h[0], h[1] if pose != "kneel" else hip, k[0], k[1], 58, 46), paint(shader=sh((h[0] - 30, 0), (h[0] + 30, 0))))
        c.drawPath(K.capsule(k[0], k[1], f[0], f[1], 46, 34), paint(shader=sh((k[0] - 25, 0), (k[0] + 25, 0))))
        c.drawCircle(k[0], k[1], 18, paint(joints))
    # torso
    lean = 40 if pose == "bow" else 0
    torso = K.smooth([(-78, top + 10), (-60 + lean * 0.3, top - 30), (60 + lean * 0.3, top - 30), (78, top + 10), (64, hip - 60), (70, hip + 10),
                      (-70, hip + 10), (-64, hip - 60)])
    if dress is not None:
        c.drawPath(K.smooth([(-82, top - 20), (82, top - 20), (130, hip + 160), (-130, hip + 160)]), paint(shader=K.lin((-130, 0), (130, 0), [mix(dress, WHITE, 0.25), dress, mix(dress, BLACK, 0.45)])))
    else:
        c.drawPath(torso, paint(shader=sh((-78, 0), (78, 0))))
    for (sh_, el, wr) in (arms_l, arms_r):
        c.drawPath(K.capsule(sh_[0], sh_[1], el[0], el[1], 40, 32), paint(shader=sh((sh_[0] - 20, 0), (sh_[0] + 20, 0))))
        c.drawPath(K.capsule(el[0], el[1], wr[0], wr[1], 32, 24), paint(shader=sh((el[0] - 16, 0), (el[0] + 16, 0))))
        c.drawCircle(el[0], el[1], 14, paint(joints))
        c.drawCircle(sh_[0], sh_[1], 17, paint(joints))
        c.drawCircle(wr[0], wr[1], 16, paint(tint))
    # neck and head
    hx = lean + head_turn * 10
    hy = top - 120
    c.drawPath(K.capsule(lean * 0.6, top - 20, hx, hy + 40, 40, 34), paint(shader=sh((-20, 0), (20, 0))))
    if hair is not None:
        c.drawPath(K.smooth([(hx + 40, hy - 50), (hx + 100, hy + 10), (hx + 96, hy + 120), (hx + 70, hy + 170), (hx + 60, hy + 60), (hx + 30, hy - 20)]), paint(hair))
    c.save()
    c.translate(hx, hy)
    c.rotate(head_tilt)
    head = K.smooth([(0, -86), (56, -66), (70, -6), (58, 56), (26, 86), (0, 92), (-26, 86), (-58, 56), (-70, -6), (-56, -66)])
    c.drawPath(head, paint(shader=K.rad((light[0] * 40, light[1] * 50), 120, [mix(tint, PORC_HI, 0.6), tint, mix(tint, shade, 0.7)])))
    if hair is not None:
        c.drawPath(K.smooth([(-70, -6), (-60, -66), (0, -96), (60, -66), (70, -6), (40, -50), (0, -60), (-40, -50)]), paint(hair))
    if face:
        ft = head_turn * 14
        for sd in (-1, 1):
            ex = sd * 24 + ft
            if eyes < 0.1:
                c.drawPath(K.bez_path([(ex - 14, -8), (ex, -2), (ex + 14, -8)]), paint((60, 44, 50), 0.85, stroke=2.4))
            else:
                c.drawOval(skia.Rect.MakeLTRB(ex - 12, -16, ex + 12, -2), paint((20, 18, 24)))
                c.drawCircle(ex - 3, -11, 2.5, paint(WHITE))
        if mouth:
            c.drawPath(K.smooth([(ft - 12, 40), (ft, 36), (ft + 12, 40), (ft, 46)]), paint((160, 20, 36), 0.85))
        _spec(c, -24, -50, 18, 9, 0.5, blur=3)
    if crack > 0:
        c.scale(0.45, 0.45)
        _crack(c, crack)
    c.restore()
    c.restore()
    c.restore()


def doll_tiny(c, x, y, s, col=PORC, a=1.0, sway=0.0, shadow=None):
    """A porcelain figure seen from far off (about 60 px tall at s = 1): head, body, legs - for crowds and armies."""
    if shadow is not None:
        c.drawOval(skia.Rect.MakeLTRB(x - 16 * s, y - 4 * s, x + 16 * s, y + 4 * s), paint(shadow, 0.35 * a))
    c.drawPath(K.smooth([(x - 9 * s, y), (x - 11 * s, y - 34 * s), (x - 7 * s, y - 44 * s), (x + 7 * s, y - 44 * s), (x + 11 * s, y - 34 * s), (x + 9 * s, y)]),
               paint(shader=K.lin((x - 11 * s, 0), (x + 11 * s, 0), [mix(col, WHITE, 0.4), col, mix(col, PORC_SH, 0.8)]), a=a))
    c.drawCircle(x + sway * s, y - 52 * s, 8 * s, paint(col, a))

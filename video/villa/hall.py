"""The villa's entrance hall, painted in one-point perspective: a faded fresco on the ceiling, an imperial staircase
with a crimson runner rising to a landing and splitting to a gallery, balustrades, a cracked gilt mirror on one wall and
a moonlit window between velvet drapes on the other, a marble floor, candelabras on the newel posts, and heavy velvet
curtains framing it all. Also the faded ceiling fresco for the gallery."""
import math

import skia

import gel as G
import kit as K
from kit import AMBER, BLACK, COBALT, EMERALD, GOLD, MAGENTA, WHITE, H, W, mix, paint

F, VX, VY, EYE = 820.0, 540.0, 800.0, 1.5
X0, X1, YT, ZB = -5.0, 5.0, 7.5, 13.0                         # the room: walls at x = +-5 m, ceiling 7.5 m, back wall 13 m


def pr(x, y, z):
    return (VX + F * x / z, VY - F * (y - EYE) / z)


def quad(c, pts, w, h, fn):
    """Draw fn(c) in a flat w x h texture mapped onto the projected world quad pts (top-left, top-right, bottom-right,
    bottom-left)."""
    scr = [pr(*p) for p in pts]
    m = skia.Matrix()
    if not m.setPolyToPoly([skia.Point(0, 0), skia.Point(w, 0), skia.Point(w, h), skia.Point(0, h)],
                           [skia.Point(*q) for q in scr]):
        return
    c.save()
    c.concat(m)
    c.clipRect(skia.Rect.MakeLTRB(0, 0, w, h))
    fn(c)
    c.restore()


def poly(c, pts, color, a=1.0):
    c.drawPath(K.path([pr(*p) for p in pts]), paint(color, a))


# ------------------------------------------------------------------ the fresco

def _figure(c, x, y, s, robe, attr, seed):
    """A robed allegorical figure reclining on a cloud, holding a book, an hourglass or a laurel wreath."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawPath(K.smooth([(-120, 40), (-60, -30), (10, -60), (90, -20), (130, 40), (40, 70), (-60, 70)]), paint(robe, 0.75))
    c.drawPath(K.smooth([(-60, -30), (-20, -90), (30, -80), (10, -60)]), paint(mix(robe, WHITE, 0.3), 0.6))
    c.drawCircle(-40, -110, 26, paint((226, 196, 176), 0.8))
    c.drawPath(K.smooth([(-66, -120), (-40, -142), (-14, -122), (-30, -112), (-50, -114)]), paint((120, 80, 50), 0.6))
    if attr == "book":
        c.drawPath(K.path([(20, -110), (70, -100), (70, -60), (20, -70)]), paint((236, 226, 200), 0.85))
        c.drawPath(K.path([(70, -100), (118, -112), (118, -72), (70, -60)]), paint((226, 214, 190), 0.85))
    elif attr == "glass":
        c.drawPath(K.path([(40, -130), (80, -130), (60, -100)]), paint((210, 190, 140), 0.85))
        c.drawPath(K.path([(60, -100), (40, -70), (80, -70)]), paint((210, 190, 140), 0.85))
        c.drawLine(36, -132, 84, -132, paint((120, 90, 50), 0.8, stroke=5))
        c.drawLine(36, -68, 84, -68, paint((120, 90, 50), 0.8, stroke=5))
    else:
        c.drawCircle(70, -120, 26, paint((110, 140, 80), 0.8, stroke=8))
    c.restore()


def fresco(c, w, h, seed=0, medallion=520):
    """A faded painted ceiling in a w x h texture: a pale sky with clouds and robed figures in oval medallions inside an
    ochre border; cracked, water-stained and peeling to bare plaster."""
    rng = K.rng_at(seed, 61)
    c.drawRect(skia.Rect.MakeLTRB(0, 0, w, h), paint(shader=K.lin((0, 0), (w, 0), [(196, 170, 150), (176, 184, 198), (196, 170, 150)])))
    c.drawRect(skia.Rect.MakeLTRB(28, 28, w - 28, h - 28), paint((150, 112, 60), stroke=26))
    for k in range(int(h / 60)):
        c.drawRect(skia.Rect.MakeXYWH(18, k * 60 + 10, 20, 34), paint((96, 70, 40), 0.7))
        c.drawRect(skia.Rect.MakeXYWH(w - 38, k * 60 + 10, 20, 34), paint((96, 70, 40), 0.7))
    for i in range(int(h / 90) + 2):                            # clouds
        cx, cy = rng.uniform(80, w - 80), rng.uniform(40, h - 40)
        for j in range(4):
            c.drawCircle(cx + rng.uniform(-60, 60), cy + rng.uniform(-24, 24), rng.uniform(40, 80),
                         paint((236, 222, 216), 0.5, blur=18))
    robes = [(170, 90, 70), (100, 120, 170), (150, 130, 80)]
    attrs = ["book", "glass", "wreath"]
    k = 0
    y = medallion * 0.6
    while y < h - 100:
        mw, mh = min(w * 0.36, 260), 200
        c.drawOval(skia.Rect.MakeLTRB(w / 2 - mw, y - mh, w / 2 + mw, y + mh), paint((214, 200, 186), 0.6))
        c.drawOval(skia.Rect.MakeLTRB(w / 2 - mw, y - mh, w / 2 + mw, y + mh), paint((150, 112, 60), 0.9, stroke=14))
        _figure(c, w / 2, y + 40, min(1.3, mw / 200), robes[k % 3], attrs[k % 3], k)
        k += 1
        y += medallion
    for i in range(int(h / 160) + 3):                           # damp stains
        c.drawCircle(rng.uniform(0, w), rng.uniform(0, h), rng.uniform(40, 120), paint((120, 90, 60), 0.22, blur=30))
    for i in range(int(h / 220) + 2):                           # plaster falling away
        cx, cy, r = rng.uniform(40, w - 40), rng.uniform(40, h - 40), rng.uniform(30, 80)
        pts = [(cx + math.cos(a) * r * rng.uniform(0.6, 1.2), cy + math.sin(a) * r * rng.uniform(0.6, 1.2))
               for a in [j * math.pi / 4 for j in range(8)]]
        c.drawPath(K.path(pts), paint((206, 196, 176)))
        c.drawPath(K.path(pts), paint((90, 76, 60), 0.7, stroke=3))
    for i in range(int(h / 200) + 3):                           # cracks
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        p = skia.Path()
        p.moveTo(x, y)
        for j in range(8):
            x += rng.uniform(-40, 40)
            y += rng.uniform(10, 50)
            p.lineTo(x, y)
        c.drawPath(p, paint((60, 46, 36), 0.7, stroke=2.5))


# ------------------------------------------------------------------ walls

def _damask_flat(c, w, h, base, seed=0):
    c.drawRect(skia.Rect.MakeLTRB(0, 0, w, h), paint(base))
    for i in range(int(w / 50) + 1):
        for j in range(int(h / 60) + 1):
            x, y = i * 50 + (j % 2) * 25, j * 60
            c.drawPath(K.smooth([(x, y - 18), (x + 12, y), (x, y + 18), (x - 12, y)]), paint(mix(base, BLACK, 0.35)))
    c.drawRect(skia.Rect.MakeLTRB(0, h - 100, w, h), paint((60, 36, 24)))


def drape(c, x0, y0, x1, y1, color=(120, 12, 34), tie=0.62, side=-1, folds=6, a=1.0, fringe=True):
    """A heavy velvet curtain in the box x0..x1, y0..y1, gathered toward `side` (-1 left, +1 right) by a gold tie-back at
    fraction `tie` of its height; deep folds, a gold fringe."""
    w = x1 - x0
    ty = y0 + (y1 - y0) * tie
    pin = x0 if side < 0 else x1
    narrow = w * 0.42
    edge_top = x1 if side < 0 else x0
    edge_tie = (x0 + narrow) if side < 0 else (x1 - narrow)
    edge_bot = (x0 + w * 0.8) if side < 0 else (x1 - w * 0.8)
    p = skia.Path()
    p.moveTo(pin, y0)
    p.lineTo(edge_top, y0)
    p.cubicTo(edge_top, y0 + (ty - y0) * 0.5, edge_tie, ty - (ty - y0) * 0.25, edge_tie, ty)
    p.cubicTo(edge_tie, ty + (y1 - ty) * 0.3, edge_bot, y1 - (y1 - ty) * 0.3, edge_bot, y1)
    p.lineTo(pin, y1)
    p.close()
    c.save()
    c.clipPath(p, doAntiAlias=True)
    c.drawPaint(paint(color, a))
    for k in range(folds):                                     # folds: light ridges and dark valleys, converging on the tie
        f0 = (k + 0.5) / folds
        xt = x0 + w * f0
        xm = pin + (edge_tie - pin) * f0
        xb = pin + (edge_bot - pin) * f0
        fold = skia.Path()
        fold.moveTo(xt - w / folds * 0.25, y0)
        fold.cubicTo(xt, (y0 + ty) / 2, xm, ty - 40, xm, ty)
        fold.cubicTo(xm, ty + 60, xb, (ty + y1) / 2, xb, y1)
        c.drawPath(fold, paint(mix(color, (255, 150, 170), 0.35), 0.8 * a, stroke=w / folds * 0.28, blur=w / folds * 0.12))
        valley = skia.Path()
        valley.moveTo(xt + w / folds * 0.3, y0)
        valley.cubicTo(xt + w / folds * 0.3, (y0 + ty) / 2, xm + 6, ty - 40, xm + 6, ty)
        valley.cubicTo(xm + 6, ty + 60, xb + w / folds * 0.3, (ty + y1) / 2, xb + w / folds * 0.3, y1)
        c.drawPath(valley, paint(mix(color, BLACK, 0.7), 0.9 * a, stroke=w / folds * 0.3, blur=w / folds * 0.14))
    c.restore()
    c.drawPath(p, paint(mix(color, BLACK, 0.6), a, stroke=3))
    # the tie-back: a gold cord and tassel
    c.drawLine(pin, ty - 6, edge_tie + side * 6, ty, paint(GOLD, a, stroke=10))
    tx = edge_tie + side * 10
    c.drawCircle(tx, ty + 6, 12, paint(mix(GOLD, WHITE, 0.2), a))
    c.drawPath(K.path([(tx - 14, ty + 14), (tx + 14, ty + 14), (tx + 18, ty + 70), (tx - 18, ty + 70)]), paint(GOLD, a))
    if fringe:
        for k in range(int(abs(edge_bot - pin) / 10)):
            fx = min(pin, edge_bot) + k * 10
            c.drawLine(fx, y1 - 18, fx, y1, paint(GOLD, 0.8 * a, stroke=3))


def _left_wall(c, T):
    """The left wall (texture: z 4..13 m across 900 units, y 7.5..0 m down 750 units): damask, and a tall gilt mirror,
    cracked, in which a pale figure stands that is not in the hall."""
    _damask_flat(c, 900, 750, (40, 70, 60), seed=3)
    mx0, my0, mx1, my1 = 470, 240, 620, 600
    c.drawRect(skia.Rect.MakeLTRB(mx0 - 18, my0 - 18, mx1 + 18, my1 + 18), paint(GOLD))
    c.drawRect(skia.Rect.MakeLTRB(mx0 - 8, my0 - 8, mx1 + 8, my1 + 8), paint(mix(GOLD, BLACK, 0.5)))
    c.drawRect(skia.Rect.MakeLTRB(mx0, my0, mx1, my1), paint((70, 86, 96)))
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(mx0, my0, mx1, my1))
    # the figure in the glass: a pale dress form, half turned
    c.drawCircle(560, 330, 18, paint((236, 232, 226)))
    c.drawPath(K.smooth([(530, 360), (590, 360), (600, 470), (580, 600), (540, 600), (520, 470)]), paint((226, 220, 214)))
    c.drawPath(K.path([(mx0, my0 + 60), (mx0 + 90, my0), (mx0 + 130, my0), (mx0, my0 + 160)]), paint(WHITE, 0.12))
    c.restore()
    rng = K.rng_at(19, 4)
    cx, cy = 520, 300                                            # the crack: a star of broken glass
    for i in range(10):
        ang = rng.uniform(0, 6.283)
        L = rng.uniform(60, 260)
        p = skia.Path()
        p.moveTo(cx, cy)
        x, y = cx, cy
        for j in range(4):
            x += math.cos(ang + rng.uniform(-0.3, 0.3)) * L / 4
            y += math.sin(ang + rng.uniform(-0.3, 0.3)) * L / 4
            p.lineTo(x, y)
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(mx0, my0, mx1, my1))
        c.drawPath(p, paint((240, 244, 250), 0.85, stroke=2.2))
        c.restore()
    # a candle sconce either side of the mirror
    for x in (380, 710):
        c.drawRect(skia.Rect.MakeLTRB(x - 6, 380, x + 6, 420), paint(GOLD))
        c.drawRect(skia.Rect.MakeLTRB(x - 8, 330, x + 8, 380), paint((236, 226, 200)))


def _right_wall(c, T):
    """The right wall (texture: z 13..4 m across 900 units): damask and a tall moonlit window between velvet drapes."""
    _damask_flat(c, 900, 750, (40, 70, 60), seed=4)
    wx0, wy0, wx1, wy1 = 300, 120, 520, 600
    c.drawRect(skia.Rect.MakeLTRB(wx0, wy0, wx1, wy1), paint((150, 170, 230)))
    for k in range(1, 4):
        c.drawLine(wx0 + k * (wx1 - wx0) / 4, wy0, wx0 + k * (wx1 - wx0) / 4, wy1, paint((30, 30, 50), stroke=8))
    for k in range(1, 6):
        c.drawLine(wx0, wy0 + k * (wy1 - wy0) / 6, wx1, wy0 + k * (wy1 - wy0) / 6, paint((30, 30, 50), stroke=8))
    drape(c, wx0 - 120, wy0 - 60, wx0 + 30, 720, color=(120, 12, 34), side=-1, folds=4)
    drape(c, wx1 - 30, wy0 - 60, wx1 + 120, 720, color=(120, 12, 34), side=1, folds=4)


def _window_tex(c):
    c.drawRect(skia.Rect.MakeLTRB(20, 30, 120, 400), paint((150, 170, 236)))
    for k in (1, 2):
        c.drawLine(20 + k * 33, 30, 20 + k * 33, 400, paint((30, 30, 50), stroke=5))
    for k in range(1, 6):
        c.drawLine(20, 30 + k * 62, 120, 30 + k * 62, paint((30, 30, 50), stroke=5))
    drape(c, -10, 0, 44, 400, color=(120, 12, 34), side=-1, folds=2, tie=0.55, fringe=False)
    drape(c, 96, 0, 150, 400, color=(120, 12, 34), side=1, folds=2, tie=0.55, fringe=False)


# ------------------------------------------------------------------ the staircase

RISE, DEPTH, N = 0.17, 0.26, 14
Z_STAIR = 6.2


def _steps(c):
    """The central flight: risers and treads (only the treads below eye level show), a crimson runner, far to near."""
    for i in reversed(range(N)):
        z = Z_STAIR + i * DEPTH
        y0, y1 = i * RISE, (i + 1) * RISE
        w = 2.0 + max(0, 3 - i) * 0.22
        if y1 < EYE:
            poly(c, [(-w, y1, z), (w, y1, z), (w, y1, z + DEPTH), (-w, y1, z + DEPTH)], (206, 196, 184))
            poly(c, [(-0.75, y1, z), (0.75, y1, z), (0.75, y1, z + DEPTH), (-0.75, y1, z + DEPTH)], (150, 20, 44))
        poly(c, [(-w, y0, z), (w, y0, z), (w, y1, z), (-w, y1, z)], (120, 110, 104))
        poly(c, [(-0.75, y0, z), (0.75, y0, z), (0.75, y1, z), (-0.75, y1, z)], (110, 12, 32))
        a, b = pr(-0.75, y1, z), pr(0.75, y1, z)
        c.drawLine(a[0], a[1], b[0], b[1], paint(GOLD, stroke=max(1.5, 260 / z / 6)))


def _balustrade(c, p0, p1, n, h=0.95, rail=(40, 26, 24), bal=(196, 186, 170)):
    """A handrail from world p0 to p1 with n balusters under it, h metres tall."""
    for k in range(n + 1):
        t = k / n
        x, y, z = (p0[i] + (p1[i] - p0[i]) * t for i in range(3))
        a, b = pr(x, y, z), pr(x, y - h, z)
        wdt = max(2.0, 90 / z)
        c.drawLine(a[0], a[1], b[0], b[1], paint(bal, stroke=wdt))
        c.drawCircle(a[0], (a[1] + b[1]) / 2, wdt * 0.9, paint(bal))
    a, b = pr(*p0), pr(*p1)
    c.drawLine(a[0], a[1], b[0], b[1], paint(rail, stroke=max(4, 160 / ((p0[2] + p1[2]) / 2))))


def hall_albedo(c, T):
    c.drawPaint(paint((40, 30, 34)))
    # ceiling, walls, floor
    quad(c, [(X0, YT, 4.0), (X1, YT, 4.0), (X1, YT, ZB), (X0, YT, ZB)], 1000, 900, lambda q: fresco(q, 1000, 900, seed=5, medallion=440))
    quad(c, [(X0, YT, 4.0), (X0, YT, ZB), (X0, 0.0, ZB), (X0, 0.0, 4.0)], 900, 750, lambda q: _left_wall(q, T))
    quad(c, [(X1, YT, ZB), (X1, YT, 4.0), (X1, 0.0, 4.0), (X1, 0.0, ZB)], 900, 750, lambda q: _right_wall(q, T))

    def floor_tex(q):
        q.drawPaint(paint((30, 26, 28)))
        for i in range(13):
            for j in range(16):
                if (i + j) % 2 == 0:
                    q.drawRect(skia.Rect.MakeXYWH(i * 80, j * 80, 80, 80), paint((214, 206, 196)))
        q.drawRect(skia.Rect.MakeLTRB(420, 0, 580, 1280), paint((140, 16, 40)))          # the runner, to the stairs
        q.drawRect(skia.Rect.MakeLTRB(412, 0, 420, 1280), paint(GOLD))
        q.drawRect(skia.Rect.MakeLTRB(580, 0, 588, 1280), paint(GOLD))
    quad(c, [(X0, 0.0, 13.0), (X1, 0.0, 13.0), (X1, 0.0, 0.8), (X0, 0.0, 0.8)], 1000, 1220, floor_tex)
    # the back wall: panelled, a gallery across it at 4.8 m, a high round window
    bl, bt = pr(X0, YT, ZB)
    br, bb = pr(X1, 0.0, ZB)
    c.drawRect(skia.Rect.MakeLTRB(bl, bt, br, bb), paint((60, 80, 70)))
    for k in range(5):
        x = bl + (br - bl) * (k + 0.5) / 5
        c.drawRect(skia.Rect.MakeLTRB(x - 40, bt + 30, x + 40, bb - 30), paint((48, 64, 56), stroke=5))
    wx, wy = pr(0.0, 6.4, ZB)
    c.drawCircle(wx, wy, 34, paint((160, 180, 240)))
    for k in range(4):
        ang = k * math.pi / 4
        c.drawLine(wx - math.cos(ang) * 34, wy - math.sin(ang) * 34, wx + math.cos(ang) * 34, wy + math.sin(ang) * 34, paint((30, 30, 50), stroke=4))
    # beside the stairs: a tall moonlit window between velvet drapes
    quad(c, [(3.1, 4.3, ZB - 0.02), (4.5, 4.3, ZB - 0.02), (4.5, 0.3, ZB - 0.02), (3.1, 0.3, ZB - 0.02)], 140, 400, _window_tex)
    gy = 4.8
    poly(c, [(X0, gy, ZB - 1.2), (X1, gy, ZB - 1.2), (X1, gy - 0.3, ZB - 1.2), (X0, gy - 0.3, ZB - 1.2)], (90, 76, 66))
    _balustrade(c, (X0, gy + 0.95, ZB - 1.2), (X1, gy + 0.95, ZB - 1.2), 26)
    # the two upper flights, from the landing out to the gallery
    LY, LZ = N * RISE, Z_STAIR + N * DEPTH
    for s in (-1, 1):
        poly(c, [(s * 2.3, LY, LZ + 0.4), (s * 4.6, gy, ZB - 1.3), (s * 4.6, gy - 0.35, ZB - 1.3), (s * 2.3, LY - 0.35, LZ + 0.4)], (110, 96, 88))
        _balustrade(c, (s * 2.3, LY + 0.95, LZ + 0.1), (s * 4.6, gy + 0.95, ZB - 1.5), 9)
    # the landing's face, then the central flight and its balustrades
    poly(c, [(-2.5, LY, LZ), (2.5, LY, LZ), (2.5, LY - 0.3, LZ), (-2.5, LY - 0.3, LZ)], (96, 84, 78))
    _steps(c)
    for s in (-1, 1):
        _balustrade(c, (s * 2.75, 1.0, Z_STAIR - 0.15), (s * 2.3, LY + 0.95, LZ), 16)
        nx, ny = pr(s * 2.75, 1.25, Z_STAIR - 0.2)
        fx, fy = pr(s * 2.75, 0.0, Z_STAIR - 0.2)
        wdt = 0.36 * F / (Z_STAIR - 0.2)
        c.drawRect(skia.Rect.MakeLTRB(nx - wdt / 2, ny, nx + wdt / 2, fy), paint((150, 136, 124)))
        c.drawRect(skia.Rect.MakeLTRB(nx - wdt * 0.62, ny - 8, nx + wdt * 0.62, ny + 6), paint((176, 160, 146)))


def newels():
    """Screen positions and scale of the two newel-post tops (for the candelabras)."""
    out = []
    for s in (-1, 1):
        x, y = pr(s * 2.75, 1.25, Z_STAIR - 0.2)
        out.append((x, y, F / (Z_STAIR - 0.2) / 260))
    return out


def hall_light(c, T):
    fl = G.flicker(T, 3)
    G.pool(c, 120, 760, 760, MAGENTA, 0.75)
    G.pool(c, 980, 700, 700, COBALT, 0.8)
    G.pool(c, 540, 560, 520, EMERALD, 0.45)
    for x, y, s in newels():
        G.pool(c, x, y - 60, 380, AMBER, 0.75 * fl)
    G.pool(c, 540, 1500, 700, AMBER, 0.35)

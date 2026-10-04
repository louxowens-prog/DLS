"""Props, all hand-made: THE ORACLE (a cardboard thinking machine with tape reels, lamps, a teleprinter and a round
paper face), machine parts (gears, a flywheel, a pendulum), food (cakes, fruit, jelly, glasses), a clock, a gold medal,
butterflies, paper slips and exam sheets, a calendar, streamers and flames, a chandelier, a robot arm."""
import math

import numpy as np
import skia

import kit as K
from kit import INK, WHITE, CREAM, PAPER, capsule, lin, mix, paint, path, rad, shade, smooth

TYPE = "special-elite-400"


# ------------------------------------------------------------------ THE ORACLE

def oracle(c, x, y, s, T, look=(0.0, 0.0), mouth=0.0, strip=None, strip_k=1.0, window=0.0, window_fn=None, medal=False,
           napkin=False, lamps=True, blink=0.0, a=1.0, eyes_shut=False, stuffed=0.0):
    """The Oracle, standing on its castors at (x, y). strip: lines of typed text coming out of the teleprinter
    (strip_k = how much is typed). window: 0..1 the forehead flap cut open; window_fn(c) draws what is inside (in
    face coordinates, a 120 x 90 box at (-60, -150)). Returns anchor points."""
    out = {}
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    body = (176, 172, 132)                      # painted cardboard, a sour olive cream
    # castors and a shadow
    c.drawOval(skia.Rect.MakeLTRB(-290, -20, 290, 26), paint(INK, 0.35, blur=12))
    for cx_ in (-200, 200):
        c.drawCircle(cx_, -10, 22, paint((40, 38, 40)))
        c.drawCircle(cx_, -10, 8, paint((150, 150, 156)))
    # the cabinet
    cab = K.rrect(-250, -880, 250, -30, 18)
    shade(c, cab, body, k=0.22)
    c.drawPath(cab, paint(mix(body, INK, 0.45), 0.7, stroke=5))
    for yy in (-640, -360):
        c.drawLine(-250, yy, 250, yy, paint(mix(body, INK, 0.35), 0.8, stroke=4))
    # tape reels behind glass
    c.drawRect(skia.Rect.MakeLTRB(-210, -860, 210, -660), paint((60, 66, 64)))
    for i, cx_ in enumerate((-105, 105)):
        ang = T * (160 if i == 0 else -130)
        c.save()
        c.translate(cx_, -760)
        c.rotate(ang)
        c.drawCircle(0, 0, 78, paint((40, 36, 34)))
        c.drawCircle(0, 0, 70, paint((120, 76, 50)))
        for k in range(3):
            c.save()
            c.rotate(k * 120)
            c.drawPath(K.rrect(-14, -66, 14, -26, 8), paint((60, 66, 64)))
            c.restore()
        c.drawCircle(0, 0, 18, paint((210, 206, 196)))
        c.restore()
    c.drawRect(skia.Rect.MakeLTRB(-210, -860, 210, -660), paint(WHITE, 0.12))
    c.drawLine(-200, -850, -60, -670, paint(WHITE, 0.2, stroke=10))
    # lamps
    for i in range(8):
        on = lamps and ((int(T * 6) + i * 3) % 5 < 2)
        colr = [(230, 60, 50), (240, 180, 40), (90, 200, 90)][i % 3]
        lx = -175 + i * 50
        c.drawCircle(lx, -605, 16, paint((40, 36, 34)))
        c.drawCircle(lx, -605, 12, paint(colr if on else mix(colr, INK, 0.6)))
        if on:
            c.drawCircle(lx, -605, 26, paint(colr, 0.35, blur=10))
    # dials
    for i, cx_ in enumerate((-150, 0, 150)):
        c.drawCircle(cx_, -500, 46, paint((236, 232, 214)))
        c.drawCircle(cx_, -500, 46, paint((80, 76, 60), stroke=5))
        ang = math.radians(-120 + 240 * (0.5 + 0.5 * math.sin(T * (1.3 + i) + i)))
        c.drawLine(cx_, -500, cx_ + 36 * math.sin(ang), -500 - 36 * math.cos(ang), paint(INK, stroke=4))
        for k in range(9):
            a2 = math.radians(-120 + k * 30)
            c.drawLine(cx_ + 38 * math.sin(a2), -500 - 38 * math.cos(a2), cx_ + 44 * math.sin(a2), -500 - 44 * math.cos(a2), paint(INK, stroke=2))
    # the teleprinter slot and its paper strip
    c.drawPath(K.rrect(-150, -330, 150, -290, 10), paint((40, 36, 34)))
    out["slot"] = tuple(c.getTotalMatrix().mapXY(0, -300))
    if strip:
        n_chars = sum(len(s_) for s_ in strip)
        shown = int(round(n_chars * strip_k))
        lines, k_ = [], shown
        for s_ in strip:
            lines.append(s_[:max(0, min(len(s_), k_))])
            k_ -= len(s_)
        n = max(1, len([l for l in lines if l]))
        L = 40 + 54 * n
        sp = smooth([(-196, -305), (196, -305), (204, -305 + L), (150, -305 + L + 16), (-186, -305 + L + 6)])
        c.drawPath(sp, paint(INK, 0.3, blur=6))
        c.drawPath(sp, paint(PAPER))
        c.drawPath(sp, paint(mix(PAPER, INK, 0.3), 0.6, stroke=2))
        f = K.font(TYPE, 30)
        for i, l in enumerate(lines):
            if l:
                c.drawString(l, -178, -305 + 50 + i * 54, f, paint((40, 36, 60)))
        if any(lines):
            K.reg_local(c, -186, -305, 204, -305 + L, "strip")
    # the neck and the round paper face
    c.drawPath(K.rrect(-40, -960, 40, -870, 8), paint(mix(body, INK, 0.25)))
    c.save()
    c.translate(0, -1110)
    face = K.circle(0, 0, 190)
    c.drawCircle(8, 12, 192, paint(INK, 0.3, blur=10))
    shade(c, face, (240, 228, 196), k=0.18)
    c.drawCircle(0, 0, 190, paint((150, 130, 96), stroke=6))
    rng = K.rng_at(4, 2)
    for k in range(18):                                                 # paper texture blotches
        c.drawCircle(rng.uniform(-150, 150), rng.uniform(-150, 150), rng.uniform(10, 30), paint((214, 200, 168), 0.25, blur=8))
    # the forehead window: a flap cut on three sides
    wx0, wy0, ww, wh = -60, -150, 120, 90
    if window > 0:
        c.save()
        c.clipRect(skia.Rect.MakeXYWH(wx0, wy0, ww, wh))
        c.drawRect(skia.Rect.MakeXYWH(wx0, wy0, ww, wh), paint((30, 26, 28)))
        if window_fn:
            window_fn(c, wx0, wy0, ww, wh)
        c.restore()
        fk = min(1.0, window)                                            # the flap, folded down toward us
        fh = wh * (1 - 2 * fk) if fk < 0.5 else wh * 0.55 * (2 * fk - 1)
        yb = wy0 + wh
        flap = path([(wx0, yb), (wx0 + ww, yb), (wx0 + ww + (8 if fk >= 0.5 else 0), yb - fh), (wx0 - (8 if fk >= 0.5 else 0), yb - fh)])
        if fk >= 0.5:
            c.drawPath(flap, paint(INK, 0.3, blur=5))
        c.drawPath(flap, paint((226, 212, 180) if fk < 0.5 else (214, 198, 164)))
        c.drawPath(flap, paint((150, 130, 96), stroke=3))
    else:
        c.drawRect(skia.Rect.MakeXYWH(wx0, wy0, ww, wh), paint((150, 130, 96), 0.35, stroke=2.5))     # a pencilled outline
    # the eyes: two lenses with paper irises
    for sx in (-1, 1):
        ex, ey = sx * 72, -10
        c.drawCircle(ex, ey, 52, paint((44, 40, 40)))
        c.drawCircle(ex, ey, 44, paint((246, 244, 236)))
        if eyes_shut or blink > 0.5:
            c.drawLine(ex - 40, ey, ex + 40, ey, paint(INK, stroke=6))
        else:
            gx, gy = look[0] * 14, look[1] * 10
            c.drawCircle(ex + gx, ey + gy, 22, paint((60, 110, 150)))
            c.drawCircle(ex + gx, ey + gy, 10, paint(INK))
            c.drawCircle(ex + gx - 7, ey + gy - 8, 5, paint(WHITE))
        c.drawCircle(ex, ey, 52, paint(WHITE, 0.15, stroke=4))
    # the mouth: a feeding slot that opens
    mo = 10 + 70 * mouth
    c.drawPath(K.rrect(-80, 92 - mo / 2, 80, 92 + mo / 2, min(20, mo / 2)), paint((40, 20, 24)))
    if stuffed > 0:
        c.drawPath(K.rrect(-70 * stuffed, 92 - mo / 2 + 4, 70 * stuffed, 92 + mo / 2 - 4, 10), paint((236, 200, 210)))
    c.drawPath(K.rrect(-80, 92 - mo / 2, 80, 92 + mo / 2, min(20, mo / 2)), paint((150, 130, 96), stroke=4))
    out["mouth"] = tuple(c.getTotalMatrix().mapXY(0, 92))
    out["face"] = tuple(c.getTotalMatrix().mapXY(0, 0))
    out["window"] = tuple(c.getTotalMatrix().mapXY(0, wy0 + wh / 2))
    # antenna with a daisy
    c.drawLine(0, -190, 0, -280, paint((80, 80, 86), stroke=6))
    from duo import daisy
    daisy(c, 0, -292, 30, rot=T * 20, seed=5)
    c.restore()
    if napkin:
        c.drawPath(path([(-150, -880), (150, -880), (40, -700), (0, -680), (-40, -700)]), paint((250, 248, 240)))
        c.drawPath(path([(-150, -880), (150, -880), (40, -700), (0, -680), (-40, -700)]), paint((200, 196, 186), stroke=3))
    if medal:
        medal_(c, 0, -820, 1.0)
    c.restore()
    return out


def medal_(c, x, y, s):
    """A gold medal on a striped ribbon."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    for i, colr in enumerate(((176, 30, 54), (250, 244, 228), (40, 80, 150))):
        c.drawPath(path([(-60 + i * 40, -120), (-20 + i * 40, -120), (10 + (i - 1) * 14, 20), (-30 + (i - 1) * 14, 20)]), paint(colr))
    c.drawCircle(0, 70, 74, paint(shader=rad((-20, 50), 90, [(255, 240, 160), (226, 176, 50), (150, 100, 20)])))
    c.drawCircle(0, 70, 74, paint((120, 80, 10), stroke=5))
    c.drawCircle(0, 70, 56, paint((190, 140, 30), stroke=3))
    c.drawPath(path(K_star(0, 70, 40)), paint((255, 236, 150)))
    c.restore()


def K_star(cx, cy, r, n=5, inner=0.45):
    return [(cx + r * (1 if i % 2 == 0 else inner) * math.cos(-math.pi / 2 + i * math.pi / n),
             cy + r * (1 if i % 2 == 0 else inner) * math.sin(-math.pi / 2 + i * math.pi / n)) for i in range(2 * n)]


# ------------------------------------------------------------------ machinery

def gear(c, x, y, r, teeth, ang, colr=(150, 140, 120), hole=0.25, spokes=0):
    """A cast gear: teeth, a rim, spokes or a solid web, a hub."""
    pts = []
    for i in range(teeth * 4):
        a = 2 * math.pi * i / (teeth * 4) + math.radians(ang)
        rr = r if (i % 4) in (1, 2) else r * 0.86
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    p = path(pts)
    c.drawPath(p, paint(shader=rad((x - r * 0.3, y - r * 0.3), r * 1.4, [mix(colr, WHITE, 0.35), colr, mix(colr, INK, 0.5)])))
    c.drawPath(p, paint(mix(colr, INK, 0.6), stroke=2.5))
    if spokes:
        c.drawCircle(x, y, r * 0.72, paint(mix(colr, INK, 0.65)))
        for k in range(spokes):
            a = math.radians(ang) + 2 * math.pi * k / spokes
            c.drawPath(capsule(x, y, x + r * 0.72 * math.cos(a), y + r * 0.72 * math.sin(a), r * 0.12, r * 0.08), paint(colr))
        c.drawCircle(x, y, r * 0.72, paint(colr, stroke=r * 0.08))
    c.drawCircle(x, y, r * hole, paint(mix(colr, WHITE, 0.15)))
    c.drawCircle(x, y, r * hole * 0.45, paint(INK))


def flywheel(c, x, y, r, ang, colr=(70, 66, 64)):
    c.drawCircle(x, y, r, paint(colr, stroke=r * 0.14))
    c.drawCircle(x, y, r * 1.07, paint(mix(colr, WHITE, 0.25), 0.5, stroke=3))
    for k in range(6):
        a = math.radians(ang) + k * math.pi / 3
        c.drawPath(capsule(x, y, x + r * math.cos(a), y + r * math.sin(a), r * 0.1, r * 0.06), paint(colr))
    c.drawCircle(x, y, r * 0.16, paint(mix(colr, WHITE, 0.3)))


def pendulum(c, x, y, L, ang, colr=(196, 160, 70)):
    a = math.radians(ang)
    bx, by = x + L * math.sin(a), y + L * math.cos(a)
    c.drawLine(x, y, bx, by, paint((60, 56, 50), stroke=8))
    c.drawCircle(bx, by, L * 0.14, paint(shader=rad((bx - 20, by - 20), L * 0.18, [(255, 236, 160), colr, mix(colr, INK, 0.5)])))


# ------------------------------------------------------------------ the table

def cake(c, x, y, s, lines=(), bitten=0.0, tiers=2, colr=(244, 214, 222), icing=(176, 30, 54), candles=0, T=0.0):
    """A layered cake with writing piped in icing; bitten 0..1 takes a bite out of the right side."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawOval(skia.Rect.MakeLTRB(-260, -20, 260, 40), paint((236, 234, 228)))
    c.drawOval(skia.Rect.MakeLTRB(-260, -20, 260, 40), paint((180, 176, 170), stroke=3))
    yb = 0
    for t in range(tiers):
        w = 220 - t * 60
        h = 150 - t * 20
        body = path([(-w, yb - h), (w, yb - h), (w, yb), (-w, yb)])
        c.drawPath(body, paint(shader=lin((-w, 0), (w, 0), [mix(colr, INK, 0.08), mix(colr, WHITE, 0.3), colr, mix(colr, INK, 0.15)], [0, .35, .7, 1])))
        c.drawOval(skia.Rect.MakeLTRB(-w, yb - h - 22, w, yb - h + 22), paint(mix(colr, WHITE, 0.4)))
        for k in range(14):                                          # piped frosting beads
            bx = -w + (k + 0.5) * (2 * w / 14)
            c.drawCircle(bx, yb - 6, 10, paint(WHITE))
            c.drawCircle(bx, yb - h + 6, 8, paint(WHITE))
        yb -= h
    f = K.font("caveat-700", 46)
    for i, ln in enumerate(lines):
        c.drawString(ln, -f.measureText(ln) / 2, -70 - i * 52 + (len(lines) - 1) * 26, f, paint(icing))
    if lines:
        K.reg_local(c, -200, -150, 200, -20, "icing")
    for k in range(candles):
        cx_ = -60 + k * 40
        c.drawRect(skia.Rect.MakeXYWH(cx_ - 6, yb - 70, 12, 50), paint((150, 190, 226)))
        flame(c, cx_, yb - 74, 0.25, T + k)
    c.restore()


def bite_mask(c, x, y, r):
    """Draw a 'bite' by clearing a scalloped circle (call inside a saveLayer)."""
    p = skia.Paint(AntiAlias=True)
    p.setBlendMode(skia.BlendMode.kClear)
    for k in range(5):
        a = -0.8 + k * 0.4
        c.drawCircle(x + r * 0.5 * math.cos(a), y + r * 0.5 * math.sin(a), r * 0.55, p)


def apple(c, x, y, r, colr=(206, 40, 44)):
    c.drawPath(smooth([(x, y - r * 0.8), (x + r, y - r * 0.9), (x + r * 1.05, y + r * 0.3), (x + r * 0.4, y + r), (x, y + r * 0.85),
                       (x - r * 0.4, y + r), (x - r * 1.05, y + r * 0.3), (x - r, y - r * 0.9)]),
               paint(shader=rad((x - r * 0.4, y - r * 0.4), r * 1.6, [mix(colr, WHITE, 0.4), colr, mix(colr, INK, 0.5)])))
    c.drawLine(x, y - r * 0.8, x + r * 0.15, y - r * 1.25, paint((90, 60, 30), stroke=r * 0.12))
    c.drawPath(smooth([(x + r * 0.1, y - r * 1.05), (x + r * 0.6, y - r * 1.35), (x + r * 0.5, y - r * 1.0)]), paint((90, 150, 60)))


def grapes(c, x, y, r):
    rng = K.rng_at(x, y)
    for row in range(5):
        for k in range(5 - row):
            gx = x + (k - (4 - row) / 2) * r * 1.6 + rng.uniform(-2, 2)
            gy = y + row * r * 1.4
            c.drawCircle(gx, gy, r, paint(shader=rad((gx - r * 0.3, gy - r * 0.3), r * 1.3, [(190, 150, 220), (110, 50, 120), (50, 20, 60)])))


def pear(c, x, y, r):
    c.drawPath(smooth([(x, y - r * 1.4), (x + r * 0.45, y - r * 0.9), (x + r, y + r * 0.2), (x + r * 0.7, y + r), (x - r * 0.7, y + r),
                       (x - r, y + r * 0.2), (x - r * 0.45, y - r * 0.9)]),
               paint(shader=rad((x - r * 0.3, y - r * 0.2), r * 1.6, [(240, 236, 140), (190, 190, 60), (110, 110, 30)])))
    c.drawLine(x, y - r * 1.4, x + r * 0.1, y - r * 1.8, paint((90, 60, 30), stroke=r * 0.1))


def jelly(c, x, y, r, T, colr=(214, 60, 60), wob=1.0):
    k = 1 + 0.06 * wob * math.sin(T * 14)
    c.save()
    c.translate(x, y)
    c.scale(1 / k, k)
    p = smooth([(-r, 0), (-r * 0.9, -r * 0.7), (-r * 0.5, -r * 1.1), (r * 0.5, -r * 1.1), (r * 0.9, -r * 0.7), (r, 0)])
    c.drawPath(p, paint(colr, 0.88))
    for k2 in range(3):
        c.drawLine(-r * 0.7 + k2 * r * 0.7, -r * 1.05, -r * 0.8 + k2 * r * 0.75, -r * 0.05, paint(mix(colr, INK, 0.3), 0.5, stroke=6))
    c.drawPath(K.bez_path([(-r * 0.6, -r * 0.8), (-r * 0.2, -r * 1.0), (r * 0.2, -r * 0.95)]), paint(WHITE, 0.5, stroke=8))
    c.restore()


def glass(c, x, y, s, wine=(150, 30, 50), level=0.6):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    bowl = smooth([(-34, -150), (34, -150), (30, -96), (0, -74), (-30, -96)])
    if level > 0:
        c.save()
        c.clipPath(bowl, doAntiAlias=True)
        c.drawRect(skia.Rect.MakeLTRB(-40, -150 + 76 * (1 - level), 40, -70), paint(wine, 0.85))
        c.restore()
    c.drawPath(bowl, paint(WHITE, 0.6, stroke=2.5))
    c.drawLine(0, -74, 0, -10, paint(WHITE, 0.7, stroke=4))
    c.drawOval(skia.Rect.MakeLTRB(-30, -14, 30, 0), paint(WHITE, 0.6, stroke=2.5))
    c.drawLine(-20, -140, -24, -110, paint(WHITE, 0.6, stroke=4))
    c.restore()


def flame(c, x, y, s, T, a=1.0):
    """A candle-style flame, flickering."""
    f = 1 + 0.15 * math.sin(T * 23) + 0.08 * math.sin(T * 37 + 1)
    c.save()
    c.translate(x, y)
    c.scale(s, s * f)
    c.drawCircle(0, -60, 70, paint((255, 190, 80), 0.25 * a, blur=26))
    c.drawPath(smooth([(-26, 0), (-30, -40), (0, -120 - 10 * math.sin(T * 11)), (30, -40), (26, 0), (0, 14)]), paint((240, 120, 30), a))
    c.drawPath(smooth([(-13, 0), (-15, -30), (0, -76), (15, -30), (13, 0), (0, 8)]), paint((255, 230, 140), a))
    c.restore()


def fire(c, x0, x1, y, h, T, seed=0, a=1.0):
    """A row of tongues of flame along a burning streamer or tablecloth."""
    rng = K.rng_at(seed, 9)
    n = int((x1 - x0) / 34) + 1
    for i in range(n):
        fx = x0 + (x1 - x0) * i / max(1, n - 1) + rng.uniform(-8, 8)
        sc = h / 120 * rng.uniform(0.7, 1.2)
        flame(c, fx, y, sc, T + rng.uniform(0, 5), a)


def streamer(c, x0, y0, x1, y1, colr, sag=80, burn=0.0, T=0.0, seed=0):
    """A crepe-paper streamer hung in a sag from (x0, y0) to (x1, y1); burn 0..1 eats it from the left, flaming."""
    n = 24
    P = []
    for i in range(n + 1):
        u = i / n
        P.append((x0 + (x1 - x0) * u, y0 + (y1 - y0) * u + sag * 4 * u * (1 - u) + 8 * math.sin(u * 20 + T * 3)))
    k0 = int(n * burn)
    if k0 < n:
        p = path(P[k0:], closed=False)
        c.drawPath(p, paint(colr, stroke=22))
        c.drawPath(p, paint(mix(colr, INK, 0.25), 0.5, stroke=3))
        if 0 < burn < 1:
            fx, fy = P[k0]
            flame(c, fx, fy + 6, 0.55, T + seed)
            c.drawCircle(fx, fy, 14, paint((40, 30, 26)))


def chandelier(c, x, y, s, T, swing=0.0, lit=True):
    c.save()
    c.translate(x, y)
    c.rotate(swing)
    c.scale(s, s)
    c.drawLine(0, -400, 0, 0, paint((150, 120, 60), stroke=6))
    for k in range(5):
        a = -0.9 + k * 0.45
        ax, ay = 220 * math.sin(a), 60 + 50 * math.cos(a * 2)
        c.drawPath(K.bez_path([(0, 20), (ax * 0.5, ay + 60), (ax, ay)]), paint((196, 160, 70), stroke=8))
        c.drawRect(skia.Rect.MakeXYWH(ax - 8, ay - 50, 16, 50), paint(CREAM))
        if lit:
            flame(c, ax, ay - 54, 0.28, T + k)
        for j in range(3):
            c.drawPath(smooth([(ax - 8, ay + 10 + j * 26), (ax + 8, ay + 10 + j * 26), (ax, ay + 34 + j * 26)]), paint((220, 236, 255), 0.7))
    c.drawCircle(0, 30, 30, paint((196, 160, 70)))
    c.restore()


# ------------------------------------------------------------------ paper things

def slip(c, x, y, ang, lines, s=1.0, colr=PAPER, ink=(50, 46, 70), mark=None, a=1.0):
    """A paper slip from the teleprinter, a few typed lines; mark = a red circle around it."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    f = K.font(TYPE, 24)
    w, h = max(300, max(f.measureText(l) for l in lines) + 36), 40 + 34 * len(lines)
    c.drawRect(skia.Rect.MakeXYWH(-w / 2 + 4, -h / 2 + 6, w, h), paint(INK, 0.25 * a, blur=4))
    c.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), paint(colr, a))
    f = K.font(TYPE, 24)
    for i, ln in enumerate(lines):
        c.drawString(ln, -w / 2 + 16, -h / 2 + 40 + i * 34, f, paint(ink, a))
    if mark:
        c.drawOval(skia.Rect.MakeLTRB(-w / 2 - 20, -h / 2 - 16, w / 2 + 20, h / 2 + 16), paint(mark, a, stroke=6))
    c.restore()


def exam(c, x, y, s, ang, items, title="TEST", cut=(), marks=None, a=1.0):
    """An exam sheet: numbered questions with tick boxes; indices in cut are snipped out (gone), marks = {i: 'X'}."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    w, h = 520, 120 + 70 * len(items)
    c.drawRect(skia.Rect.MakeXYWH(-w / 2 + 6, 10, w, h), paint(INK, 0.3 * a, blur=6))
    c.drawRect(skia.Rect.MakeXYWH(-w / 2, 0, w, h), paint((250, 248, 240), a))
    for k in range(int(h / 34)):
        c.drawLine(-w / 2, 40 + k * 34, w / 2, 40 + k * 34, paint((150, 190, 226), 0.35 * a, stroke=1.5))
    c.drawLine(-w / 2 + 60, 0, -w / 2 + 60, h, paint((222, 82, 82), 0.5 * a, stroke=2))
    f = K.font(TYPE, 34)
    c.drawString(title, -f.measureText(title) / 2, 70, f, paint(INK, a))
    f2 = K.font(TYPE, 26)
    for i, it in enumerate(items):
        yy = 130 + i * 70
        if i in cut:
            c.drawRect(skia.Rect.MakeLTRB(-w / 2 + 70, yy - 34, w / 2 - 10, yy + 22), paint((40, 30, 30), a))       # the hole
            continue
        c.drawString(f"{i + 1}. {it}", -w / 2 + 74, yy, f2, paint((40, 36, 60), a))
        c.drawRect(skia.Rect.MakeXYWH(w / 2 - 54, yy - 26, 30, 30), paint((40, 36, 60), a, stroke=2.5))
        if marks and i in marks:
            c.drawString(marks[i], w / 2 - 52, yy, K.font("caveat-700", 40), paint((200, 30, 40), a))
    c.restore()


def calendar(c, x, y, s, top, big, colr=(176, 30, 54), ang=0.0):
    """A tear-off calendar page."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    c.drawRect(skia.Rect.MakeXYWH(-150 + 6, -180 + 8, 300, 360), paint(INK, 0.3, blur=6))
    c.drawRect(skia.Rect.MakeXYWH(-150, -180, 300, 360), paint((250, 248, 240)))
    c.drawRect(skia.Rect.MakeXYWH(-150, -180, 300, 80), paint(colr))
    for k in range(6):
        c.drawCircle(-110 + k * 44, -184, 7, paint((60, 56, 50)))
    f = K.font("abril-400", 40)
    c.drawString(top, -f.measureText(top) / 2, -126, f, paint(WHITE))
    f2 = K.font("abril-400", 150)
    if f2.measureText(big) > 270:
        f2 = K.font("abril-400", 150 * 270 / f2.measureText(big))
    c.drawString(big, -f2.measureText(big) / 2, 110, f2, paint(INK))
    c.restore()


def clock(c, x, y, r, hh, mm, face=(246, 240, 222), rim=(40, 36, 34), numerals=True):
    """An analog clock at hh:mm."""
    c.drawCircle(x + 8, y + 12, r * 1.08, paint(INK, 0.35, blur=10))
    c.drawCircle(x, y, r * 1.08, paint(rim))
    c.drawCircle(x, y, r, paint(shader=rad((x - r * 0.3, y - r * 0.3), r * 1.4, [WHITE, face, mix(face, INK, 0.15)])))
    for k in range(60):
        a = math.radians(k * 6)
        r0 = r * (0.86 if k % 5 == 0 else 0.92)
        c.drawLine(x + r0 * math.sin(a), y - r0 * math.cos(a), x + r * 0.97 * math.sin(a), y - r * 0.97 * math.cos(a),
                   paint(INK, stroke=r * (0.025 if k % 5 == 0 else 0.008)))
    if numerals:
        f = K.font("fraunces-700", r * 0.2)
        for k in range(1, 13):
            a = math.radians(k * 30)
            s_ = str(k)
            c.drawString(s_, x + r * 0.72 * math.sin(a) - f.measureText(s_) / 2, y - r * 0.72 * math.cos(a) + r * 0.07, f, paint(INK))
    ha = math.radians((hh % 12) * 30 + mm * 0.5)
    ma = math.radians(mm * 6)
    c.drawPath(capsule(x, y, x + r * 0.5 * math.sin(ha), y - r * 0.5 * math.cos(ha), r * 0.07, r * 0.04), paint(INK))
    c.drawPath(capsule(x, y, x + r * 0.78 * math.sin(ma), y - r * 0.78 * math.cos(ma), r * 0.05, r * 0.025), paint(INK))
    c.drawCircle(x, y, r * 0.05, paint((176, 30, 54)))


def butterfly(c, x, y, s, T, colors=((222, 82, 52), (250, 196, 30)), flap=0.0, pin=False, seed=0, ang=0.0):
    """A butterfly; flap 0 (open, pinned flat) .. 1 (wings up)."""
    k = 1 - 0.85 * (0.5 + 0.5 * math.sin(T * 18 + seed)) * flap
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    for sx in (-1, 1):
        c.save()
        c.scale(sx * k, 1)
        up = smooth([(4, -6), (40, -70), (96, -86), (110, -40), (70, 6), (8, 8)])
        lo = smooth([(6, 6), (60, 14), (78, 60), (44, 92), (10, 50)])
        c.drawPath(up, paint(colors[0]))
        c.drawPath(lo, paint(colors[1]))
        c.drawPath(up, paint(INK, stroke=4))
        c.drawPath(lo, paint(INK, stroke=4))
        c.drawCircle(70, -44, 12, paint(INK))
        c.drawCircle(70, -44, 6, paint(WHITE))
        c.drawCircle(46, 52, 8, paint(INK, 0.7))
        c.restore()
    c.drawPath(capsule(0, -40, 0, 70, 12, 8), paint((40, 30, 30)))
    c.drawPath(K.bez_path([(0, -40), (-20, -80), (-30, -100)]), paint(INK, stroke=2.5))
    c.drawPath(K.bez_path([(0, -40), (20, -80), (30, -100)]), paint(INK, stroke=2.5))
    if pin:
        c.drawLine(0, -10, 0, 40, paint((200, 200, 206), stroke=3))
        c.drawCircle(0, -14, 7, paint((222, 60, 60)))
    c.restore()


def robot_arm(c, x, y, s, a1, a2, grip=0.5, colr=(236, 160, 40)):
    """A factory robot arm on a base: shoulder angle a1, elbow a2 (degrees, 0 = up)."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawPath(K.rrect(-80, -40, 80, 0, 10), paint((60, 60, 66)))
    r1 = math.radians(a1)
    ex, ey = 260 * math.sin(r1), -40 - 260 * math.cos(r1)
    r2 = r1 + math.radians(a2)
    hx, hy = ex + 220 * math.sin(r2), ey - 220 * math.cos(r2)
    shade(c, capsule(0, -40, ex, ey, 60, 50), colr, k=0.3)
    shade(c, capsule(ex, ey, hx, hy, 46, 38), colr, k=0.3)
    for px, py in ((0, -40), (ex, ey)):
        c.drawCircle(px, py, 30, paint((60, 60, 66)))
        c.drawCircle(px, py, 12, paint((180, 180, 186)))
    c.save()
    c.translate(hx, hy)
    c.rotate(math.degrees(r2))
    for sgn in (-1, 1):
        c.drawPath(K.rrect(sgn * (10 + 22 * grip) - 8, -70, sgn * (10 + 22 * grip) + 8, 0, 4), paint((80, 80, 86)))
    c.restore()
    c.restore()
    return (x + hx * s, y + hy * s)

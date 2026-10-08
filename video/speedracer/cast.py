"""The cast, in glossy toy-plastic: faces for the head wipes and the broadcast boxes, and the race cars.

  host       the anchor (our narrator): violet bob, headset mic
  announcer  the stadium announcer: pompadour, moustache, bow tie
  ai         the Generalist's driver: white helmet, glowing LED face in the visor
  memorizer  the rival: purple helmet plastered with sticky notes, goggles
"""
import math

import numpy as np
import skia

import sr
from sr import CYAN, INK, LEMON, PINK, RED, VIOLET, WHITE, darker, lighter, paint, path

SKIN = (255, 196, 160)


def _eye(c, x, y, rx, ry, iris, look, blink, lashes=False, lid=INK):
    if blink < 0.15:
        c.drawPath(path(sr.bez((x - rx, y), (x, y + ry * 0.5), (x + rx, y)), closed=False), paint(lid, stroke=ry * 0.25))
        return
    ry *= blink
    c.drawOval(skia.Rect.MakeXYWH(x - rx, y - ry, 2 * rx, 2 * ry), paint(WHITE))
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(x - rx, y - ry, 2 * rx, 2 * ry))
    ix, iy, ir = x + look[0] * rx * 0.35, y + look[1] * ry * 0.3, min(rx, ry / max(blink, 0.3)) * 0.62
    c.drawCircle(ix, iy, ir, paint(shader=sr.rad((ix, iy - ir * 0.3), ir * 1.2, [lighter(iris, 0.6), iris, darker(iris, 0.5)], [0, 0.55, 1])))
    c.drawCircle(ix, iy, ir * 0.45, paint(INK))
    c.drawCircle(ix - ir * 0.35, iy - ir * 0.38, ir * 0.28, paint(WHITE))
    c.drawCircle(ix + ir * 0.32, iy + ir * 0.3, ir * 0.12, paint(WHITE, 0.9))
    c.restore()
    c.drawOval(skia.Rect.MakeXYWH(x - rx, y - ry, 2 * rx, 2 * ry), paint(INK, stroke=ry * 0.16))
    top = sr.bez((x - rx * 1.1, y - ry * 0.15), (x, y - ry * 1.45), (x + rx * 1.1, y - ry * 0.3))
    c.drawPath(path(top, closed=False), paint(lid, stroke=ry * (0.32 if lashes else 0.22)))
    if lashes:
        for u in (0.15, 0.4, 0.65, 0.9):
            p = top[int(u * (len(top) - 1))]
            c.drawLine(p[0], p[1], p[0] + rx * 0.25 * (u - 0.3), p[1] - ry * 0.45, paint(lid, stroke=ry * 0.12))


def _mouth(c, x, y, w, talk, smile=0.6, lip=(200, 60, 90)):
    o = max(0.0, min(1.0, talk))
    if o < 0.08:
        c.drawPath(path(sr.bez((x - w, y - smile * w * 0.2), (x, y + smile * w * 0.45), (x + w, y - smile * w * 0.25)), closed=False),
                   paint(INK, stroke=w * 0.14))
        return
    h = w * (0.25 + 0.9 * o)
    m = sr.ellipse(x, y + h * 0.35, w * (0.85 - 0.2 * o), h * 0.6, 32)
    c.drawPath(path(m), paint((70, 10, 30)))
    c.save()
    c.clipPath(path(m), doAntiAlias=True)
    c.drawRect(skia.Rect.MakeXYWH(x - w, y + h * 0.35 - h * 0.6, 2 * w, h * 0.28), paint(WHITE))
    c.drawOval(skia.Rect.MakeXYWH(x - w * 0.5, y + h * 0.45, w, h * 0.6), paint((255, 90, 110)))
    c.restore()
    c.drawPath(path(m), paint(lip, stroke=w * 0.12))


def _head(c, R, skin=SKIN, rim1=CYAN, rim2=PINK):
    a = np.linspace(math.pi, 2 * math.pi, 32)
    cran = np.stack([0.86 * R * np.cos(a), -0.05 * R + 0.92 * R * np.sin(a)], 1)
    jaw_r = sr.bez((0.86 * R, -0.05 * R), (0.84 * R, 0.7 * R), (0.12 * R, 0.98 * R))
    jaw_l = sr.bez((0.12 * R, 0.98 * R), (-0.62 * R, 0.9 * R), (-0.86 * R, -0.05 * R))
    p = path(np.vstack([cran, jaw_r, jaw_l]))
    c.drawPath(p, paint(shader=sr.rad((-0.25 * R, -0.35 * R), 1.5 * R, [lighter(skin, 0.35), skin, darker(skin, 0.8)], [0, 0.55, 1])))
    c.save()
    c.clipPath(p, doAntiAlias=True)
    c.translate(-0.12 * R, 0)
    c.drawPath(p, paint(rim1, 0.55, stroke=0.2 * R, blur=0.06 * R))
    c.restore()
    c.drawCircle(0.66 * R, 0.1 * R, 0.2 * R, paint(rim2, 0.3, blur=0.08 * R))
    c.drawPath(p, paint(INK, stroke=0.05 * R))
    c.drawCircle(-0.1 * R, -0.55 * R, 0.1 * R, paint(WHITE, 0.55, blur=0.05 * R))
    return p


def face(c, who, x, y, s, T, talk=0.0, look=(0.4, 0.0), facing=1, blink_seed=0, expr="smile"):
    """A glossy toy head, 3/4 view, centred at (x, y); s = 1 is about 200 px tall."""
    R = 100.0
    blink = 0.05 if (int(T * 12) + blink_seed) % 43 == 0 else 1.0
    c.save()
    c.translate(x, y)
    c.scale(s * facing, s)
    if who == "ai":
        _ai_head(c, R, T, talk, look)
    elif who == "memorizer":
        _memorizer_head(c, R, T, talk, look, blink, expr)
    else:
        if who == "host":
            back = sr.ellipse(0, 0.05 * R, 1.12 * R, 1.08 * R, 50)
            c.drawPath(path(back), paint(shader=sr.lin((0, -R), (0, R), [(120, 60, 200), (40, 20, 70)])))
        _head(c, R)
        ey = -0.05 * R
        lash = who == "host"
        iris = (60, 150, 255) if who == "host" else (120, 80, 40)
        _eye(c, -0.2 * R, ey, 0.2 * R, 0.24 * R, iris, look, blink, lashes=lash)
        _eye(c, 0.36 * R, ey, 0.15 * R, 0.22 * R, iris, look, blink, lashes=lash)
        brow_y = ey - 0.36 * R - (0.05 * R if expr == "wow" else 0)
        for bx, bw in ((-0.2 * R, 0.22 * R), (0.36 * R, 0.16 * R)):
            c.drawPath(path(sr.bez((bx - bw, brow_y + 0.03 * R), (bx, brow_y - 0.06 * R), (bx + bw, brow_y + 0.02 * R)), closed=False),
                       paint(INK if who == "announcer" else (60, 30, 90), stroke=0.07 * R))
        # the nose: between the eyes, turned toward the facing side, with a soft shade and a glossy tip
        c.drawOval(skia.Rect.MakeXYWH(0.07 * R, 0.14 * R, 0.2 * R, 0.2 * R), paint(darker(SKIN, 0.85), 0.5, blur=0.05 * R))
        c.drawPath(path(sr.bez((0.12 * R, 0.1 * R), (0.3 * R, 0.3 * R), (0.1 * R, 0.33 * R)), closed=False), paint(darker(SKIN, 0.65), stroke=0.045 * R))
        c.drawCircle(0.19 * R, 0.24 * R, 0.045 * R, paint(WHITE, 0.6, blur=0.015 * R))
        c.drawCircle(-0.35 * R, 0.3 * R, 0.13 * R, paint(PINK, 0.3, blur=0.06 * R))
        if who == "announcer":
            mo = sr.bez((0.0, 0.4 * R), (0.25 * R, 0.33 * R), (0.55 * R, 0.42 * R))
            c.drawPath(path(np.vstack([mo, mo[::-1] + np.array([0, 0.1 * R])])), paint(INK))
        _mouth(c, 0.2 * R, 0.55 * R, 0.2 * R, talk, smile=0.8 if expr == "smile" else -0.3,
               lip=(220, 60, 120) if who == "host" else (160, 70, 70))
        if who == "host":
            _host_hair(c, R, T)
        else:
            _announcer_hair(c, R)
    c.restore()


def _host_hair(c, R, T):
    top = np.vstack([sr.bez((-0.95 * R, 0.55 * R), (-1.15 * R, -0.9 * R), (0.1 * R, -1.2 * R)),
                     sr.bez((0.1 * R, -1.2 * R), (0.95 * R, -1.05 * R), (0.95 * R, -0.2 * R)),
                     sr.bez((0.95 * R, -0.2 * R), (0.6 * R, -0.75 * R), (-0.1 * R, -0.62 * R)),
                     sr.bez((-0.1 * R, -0.62 * R), (-0.62 * R, -0.5 * R), (-0.62 * R, 0.55 * R))])
    p = path(top)
    sr.glossy(c, p, (70, 30, 130), top=(150, 90, 230), rim=PINK, lw=0.05 * R)
    for k, off in enumerate((-0.2, 0.3)):
        band = sr.bez((-0.8 * R, -0.35 * R + off * R * 0.5), (-0.3 * R, -1.05 * R + off * R * 0.3), (0.5 * R, -0.95 * R + off * R * 0.4))
        c.drawPath(path(band, closed=False), paint(WHITE, 0.45, stroke=0.06 * R, blur=0.02 * R))
    # headset: ear cup and boom mic to the mouth
    c.drawCircle(-0.72 * R, 0.1 * R, 0.2 * R, paint(INK))
    c.drawCircle(-0.72 * R, 0.1 * R, 0.13 * R, paint(PINK))
    boom = sr.bez((-0.72 * R, 0.2 * R), (-0.45 * R, 0.8 * R), (0.1 * R, 0.72 * R))
    c.drawPath(path(boom, closed=False), paint(INK, stroke=0.06 * R))
    c.drawCircle(0.12 * R, 0.72 * R, 0.08 * R, paint(INK))
    c.drawCircle(-0.8 * R, 0.55 * R, 0.08 * R, paint(LEMON, stroke=0.03 * R))


def _announcer_hair(c, R):
    pomp = np.vstack([sr.bez((-0.85 * R, 0.1 * R), (-1.05 * R, -1.0 * R), (0.0 * R, -1.28 * R)),
                      sr.bez((0.0 * R, -1.28 * R), (0.9 * R, -1.3 * R), (0.95 * R, -0.75 * R)),
                      sr.bez((0.95 * R, -0.75 * R), (0.5 * R, -0.62 * R), (-0.2 * R, -0.68 * R)),
                      sr.bez((-0.2 * R, -0.68 * R), (-0.62 * R, -0.5 * R), (-0.6 * R, 0.1 * R))])
    sr.glossy(c, path(pomp), (30, 30, 50), top=(90, 110, 170), rim=CYAN, lw=0.05 * R)
    c.drawPath(path(sr.bez((-0.7 * R, -0.7 * R), (-0.2 * R, -1.2 * R), (0.6 * R, -1.05 * R)), closed=False), paint(WHITE, 0.5, stroke=0.05 * R, blur=0.02 * R))
    # collar and bow tie
    c.drawPath(path([(-0.5 * R, 0.95 * R), (0.0, 1.1 * R), (0.5 * R, 0.95 * R), (0.6 * R, 1.3 * R), (-0.6 * R, 1.3 * R)]), paint(WHITE))
    for side in (-1, 1):
        c.drawPath(path([(0, 1.08 * R), (side * 0.32 * R, 0.95 * R), (side * 0.32 * R, 1.25 * R)]), paint(RED))
    c.drawCircle(0, 1.1 * R, 0.07 * R, paint(darker(RED, 0.7)))


def _ai_head(c, R, T, talk, look):
    shell = sr.ellipse(0, -0.05 * R, 1.02 * R, 1.08 * R, 64)
    p = path(shell)
    sr.glossy(c, p, (235, 240, 250), top=WHITE, rim=CYAN, lw=0.05 * R)
    c.save()
    c.clipPath(p, doAntiAlias=True)
    c.drawRect(skia.Rect.MakeXYWH(-0.16 * R, -1.2 * R, 0.32 * R, 2.4 * R), paint(CYAN))
    c.drawRect(skia.Rect.MakeXYWH(-0.26 * R, -1.2 * R, 0.06 * R, 2.4 * R), paint(PINK))
    c.restore()
    visor = path(np.vstack([sr.bez((-0.85 * R, -0.2 * R), (0.0, -0.55 * R), (0.95 * R, -0.25 * R)),
                            sr.bez((0.95 * R, -0.25 * R), (0.95 * R, 0.55 * R), (0.1 * R, 0.62 * R)),
                            sr.bez((0.1 * R, 0.62 * R), (-0.8 * R, 0.6 * R), (-0.85 * R, -0.2 * R))]))
    c.drawPath(visor, paint(shader=sr.lin((0, -0.5 * R), (0, 0.6 * R), [(20, 10, 60), (40, 20, 110), (10, 5, 30)])))
    c.save()
    c.clipPath(visor, doAntiAlias=True)
    for k, cc in enumerate(sr.CANDY):
        c.drawRect(skia.Rect.MakeXYWH(-R, -0.42 * R + k * 0.035 * R, 2 * R, 0.035 * R), paint(cc, 0.35))
    ex = look[0] * 0.08 * R
    for x, w in ((-0.3 * R, 0.2 * R), (0.35 * R, 0.16 * R)):
        c.drawOval(skia.Rect.MakeXYWH(x + ex - w, -0.12 * R, 2 * w, 0.2 * R), paint(CYAN, 0.9, blur=0.05 * R))
        c.drawOval(skia.Rect.MakeXYWH(x + ex - w * 0.7, -0.08 * R, 1.4 * w, 0.12 * R), paint(WHITE))
    o = max(0.0, min(1.0, talk))
    for k in range(7):                                   # LED mouth: an equalizer that moves with the voice
        hgt = 0.05 * R + 0.22 * R * o * (0.5 + 0.5 * math.sin(k * 1.7 + T * 30))
        c.drawRect(skia.Rect.MakeXYWH(-0.1 * R + k * 0.07 * R, 0.33 * R - hgt / 2, 0.045 * R, hgt), paint(CYAN, 0.95))
    c.restore()
    c.drawPath(visor, paint(INK, stroke=0.05 * R))
    c.drawPath(path(sr.bez((-0.6 * R, -0.25 * R), (0.0, -0.45 * R), (0.7 * R, -0.25 * R)), closed=False), paint(WHITE, 0.7, stroke=0.04 * R))


def _memorizer_head(c, R, T, talk, look, blink, expr):
    _head(c, R * 0.92, rim1=(120, 255, 90), rim2=VIOLET)
    shell = np.vstack([sr.bez((-1.0 * R, 0.35 * R), (-1.15 * R, -1.2 * R), (0.2 * R, -1.2 * R)),
                       sr.bez((0.2 * R, -1.2 * R), (1.05 * R, -1.05 * R), (1.0 * R, -0.25 * R)),
                       sr.bez((1.0 * R, -0.25 * R), (0.5 * R, -0.5 * R), (-0.55 * R, -0.45 * R)),
                       sr.bez((-0.55 * R, -0.45 * R), (-0.7 * R, 0.0), (-0.7 * R, 0.4 * R))])
    sr.glossy(c, path(shell), (70, 20, 110), top=(160, 80, 220), rim=(120, 255, 90), lw=0.05 * R)
    rng = np.random.default_rng(3)
    for k in range(7):                                   # sticky notes: every track, memorized
        nx, ny = rng.uniform(-0.8, 0.6) * R, rng.uniform(-1.05, -0.55) * R
        c.save()
        c.translate(nx, ny)
        c.rotate(rng.uniform(-25, 25))
        c.drawRect(skia.Rect.MakeXYWH(-0.13 * R, -0.13 * R, 0.26 * R, 0.26 * R), paint([LEMON, PINK, (120, 255, 90)][k % 3]))
        for j in range(3):
            c.drawLine(-0.09 * R, (-0.06 + 0.06 * j) * R, 0.09 * R, (-0.06 + 0.06 * j) * R, paint(INK, stroke=0.015 * R))
        c.restore()
    for x, w in ((-0.2 * R, 0.22 * R), (0.36 * R, 0.18 * R)):   # goggles
        c.drawCircle(x, -0.05 * R, w, paint(shader=sr.rad((x - w * 0.3, -0.15 * R), w * 1.3, [(200, 255, 170), (60, 200, 90), (20, 80, 40)])))
        c.drawCircle(x, -0.05 * R, w, paint(INK, stroke=0.06 * R))
        c.drawCircle(x - w * 0.35, -0.05 * R - w * 0.35, w * 0.22, paint(WHITE, 0.9))
        c.drawCircle(x + look[0] * w * 0.3, -0.05 * R, w * 0.3, paint(INK, 0.7))
    c.drawLine(-0.02 * R, -0.05 * R, 0.18 * R, -0.05 * R, paint(INK, stroke=0.06 * R))
    _mouth(c, 0.2 * R, 0.5 * R, 0.2 * R, talk, smile=-0.5 if expr != "smile" else 0.5)


# ------------------------------------------------------------------ cars

def car_side(c, x, y, s, T, body=CYAN, stripe=WHITE, number="1", speed=1.0, driver="ai", books=False, facing=1, flames=False):
    """A glossy 1960s racer seen from the side, nose toward +x (facing=1). (x, y) = ground under the car's middle."""
    c.save()
    c.translate(x, y)
    c.scale(s * facing, s)
    L = 520
    shape = np.vstack([sr.bez((-L * 0.5, -40), (-L * 0.52, -120), (-L * 0.3, -118)),
                       sr.bez((-L * 0.3, -118), (L * 0.05, -130), (L * 0.2, -108)),
                       sr.bez((L * 0.2, -108), (L * 0.45, -95), (L * 0.53, -62)),
                       sr.bez((L * 0.53, -62), (L * 0.56, -40), (L * 0.48, -32)),
                       [(-L * 0.46, -32)]])
    c.drawOval(skia.Rect.MakeXYWH(-L * 0.52, -12, L * 1.04, 24), paint(INK, 0.35, blur=8))
    if flames:
        for k in range(3):
            fl = int(T * 24) % 3
            ln = 90 + 40 * ((k + fl) % 3)
            fp = path([(-L * 0.5, -60 + k * 14), (-L * 0.5 - ln, -52 + k * 14 + 6 * math.sin(T * 40 + k)), (-L * 0.5, -46 + k * 14)])
            c.drawPath(fp, paint([sr.LEMON, sr.TANG, sr.RED][k], 0.9, blur=2))
    p = path(shape)
    sr.glossy(c, p, body, rim=lighter(body, 0.8), lw=6)
    c.save()
    c.clipPath(p, doAntiAlias=True)
    c.drawRect(skia.Rect.MakeXYWH(-L * 0.6, -100, L * 1.2, 16), paint(stripe))
    c.drawRect(skia.Rect.MakeXYWH(-L * 0.6, -78, L * 1.2, 7), paint(stripe))
    c.restore()
    if books:                                            # the memorizer hauls every map ever made
        for k in range(5):
            bw, bh = 44, 70 - 6 * k
            bx = -L * 0.44 + k * 34
            c.save()
            c.translate(bx, -120)
            c.rotate(-8 + 4 * k)
            c.drawRect(skia.Rect.MakeXYWH(-bw / 2, -bh, bw, bh), paint([RED, LEMON, sr.LIME, PINK, sr.TANG][k]))
            c.drawRect(skia.Rect.MakeXYWH(-bw / 2, -bh, bw, bh), paint(INK, stroke=4))
            c.drawRect(skia.Rect.MakeXYWH(-bw / 2 + 6, -bh + 10, bw - 12, 6), paint(WHITE))
            c.restore()
    # cockpit and driver
    c.drawOval(skia.Rect.MakeXYWH(-L * 0.14, -176, 130, 90), paint(shader=sr.lin((0, -176), (0, -90), [(200, 240, 255), (60, 120, 200)])))
    c.drawOval(skia.Rect.MakeXYWH(-L * 0.14, -176, 130, 90), paint(INK, stroke=5))
    if driver == "ai":
        c.drawCircle(-L * 0.03, -140, 34, paint(shader=sr.rad((-L * 0.05, -150), 40, [WHITE, (200, 205, 220)])))
        c.drawOval(skia.Rect.MakeXYWH(-L * 0.03 - 8, -150, 42, 20), paint(shader=sr.lin((0, -150), (0, -130), [(40, 20, 110), (10, 5, 30)])))
        c.drawOval(skia.Rect.MakeXYWH(-L * 0.03 + 8, -145, 12, 8), paint(CYAN, blur=2))
    else:
        c.drawCircle(-L * 0.03, -140, 34, paint(shader=sr.rad((-L * 0.05, -150), 40, [(170, 90, 230), (70, 20, 110)])))
        c.drawCircle(-L * 0.03 + 14, -140, 11, paint((90, 230, 110)))
        c.drawRect(skia.Rect.MakeXYWH(-L * 0.03 - 20, -170, 18, 18), paint(LEMON))
    # number roundel
    c.drawCircle(L * 0.15, -72, 34, paint(WHITE))
    c.drawCircle(L * 0.15, -72, 34, paint(INK, stroke=4))
    f = sr.font("bungee-400", 40)
    c.save()
    c.translate(L * 0.15, -72)
    c.scale(facing, 1)
    c.drawString(number, -f.measureText(number) / 2, 15, f, paint(INK))
    c.restore()
    sr.glint(c, L * 0.46, -70, 26, T)
    # wheels
    for wx in (-L * 0.3, L * 0.32):
        c.drawCircle(wx, -34, 58, paint((25, 20, 35)))
        c.drawCircle(wx, -34, 58, paint(INK, stroke=5))
        c.drawCircle(wx, -34, 34, paint(shader=sr.rad((wx - 10, -46), 44, [WHITE, (170, 180, 200), (90, 95, 120)])))
        if speed < 0.4:
            for k in range(5):
                a = T * speed * 20 + k * 2 * math.pi / 5
                c.drawLine(wx, -34, wx + 30 * math.cos(a), -34 + 30 * math.sin(a), paint(INK, stroke=5))
        else:
            c.drawCircle(wx, -34, 26, paint(INK, 0.25, stroke=8, blur=4))
        c.drawCircle(wx, -34, 9, paint(INK))
    c.restore()


def car_front(c, x, y, s, T, body=CYAN, stripe=WHITE, number="1", driver="ai", lights=True):
    """Head-on view, for chase shots down the rainbow road. (x, y) = ground centre."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawOval(skia.Rect.MakeXYWH(-230, -18, 460, 36), paint(INK, 0.4, blur=10))
    for side in (-1, 1):
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(side * 185 - 40, -130, 80, 128), 22, 22), paint((25, 20, 35)))
    body_p = path(np.vstack([sr.bez((-170, -40), (-190, -150), (-80, -175)), sr.bez((-80, -175), (0, -190), (80, -175)),
                             sr.bez((80, -175), (190, -150), (170, -40)), [(170, -30), (-170, -30)]]))
    sr.glossy(c, body_p, body, rim=lighter(body, 0.8), lw=6)
    c.drawRect(skia.Rect.MakeXYWH(-22, -186, 44, 156), paint(stripe))
    c.drawOval(skia.Rect.MakeXYWH(-70, -250, 140, 100), paint(shader=sr.lin((0, -250), (0, -150), [(200, 240, 255), (60, 120, 200)])))
    c.drawCircle(0, -210, 40, paint(shader=sr.rad((-10, -222), 46, [WHITE, (200, 205, 220)] if driver == "ai" else [(170, 90, 230), (70, 20, 110)])))
    if driver == "ai":
        c.drawOval(skia.Rect.MakeXYWH(-30, -222, 60, 24), paint((30, 15, 80)))
        c.drawOval(skia.Rect.MakeXYWH(-20, -216, 12, 10), paint(CYAN, blur=2))
        c.drawOval(skia.Rect.MakeXYWH(8, -216, 12, 10), paint(CYAN, blur=2))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-70, -80, 140, 40), 12, 12), paint(INK))
    for side in (-1, 1):
        c.drawCircle(side * 118, -92, 26, paint(shader=sr.rad((side * 118 - 6, -98), 30, [WHITE, LEMON, darker(LEMON, 0.7)])))
        if lights:
            sr.glint(c, side * 118, -92, 60, T)
    c.restore()

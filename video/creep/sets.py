"""The sets, built and lit like a 1982 soundstage: Nora's flat on a stormy night, a car on a wet road, a swamp
crossroads in fog, a dorm room, an exam hall, a procedure room, a hospital ward, a cockpit in a storm, and the reader's
real night (no gels at all)."""
import math

import numpy as np
import skia

import comic as CO
import face as FA
import kit as K
from kit import INK, WHITE, H, W, mix, paint, path, smooth


def grad_bg(c, top, bottom):
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=K.lin((0, 0), (0, H), [top, bottom])))


def glow(c, x, y, r, colr, a=0.5):
    g = paint(colr, a, blur=r * 0.5)
    g.setBlendMode(skia.BlendMode.kPlus)
    c.drawCircle(x, y, r, g)


def pool(c, x, y, rx, ry, colr, a=0.5):
    c.drawOval(skia.Rect.MakeLTRB(x - rx, y - ry, x + rx, y + ry), paint(shader=K.rad((x, y), max(rx, ry), [colr + (a,), colr + (0.0,)])))


def damask(c, x0, y0, x1, y1, base, ink, seed=0, a=0.25):
    """Wallpaper: a repeating damask of leaves and diamonds."""
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x0, y0, x1, y1))
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(base))
    for j, yy in enumerate(range(int(y0) - 60, int(y1) + 120, 150)):
        for i, xx in enumerate(range(int(x0) - 60, int(x1) + 120, 130)):
            ox = 65 if j % 2 else 0
            cx, cy = xx + ox, yy
            leaf = smooth([(cx, cy - 50), (cx + 24, cy - 14), (cx + 10, cy + 30), (cx, cy + 50), (cx - 10, cy + 30), (cx - 24, cy - 14)])
            c.drawPath(leaf, paint(ink, a))
            c.drawCircle(cx, cy - 64, 8, paint(ink, a))
    c.restore()


def window(c, x0, y0, x1, y1, T, flash=0.0, sky=(16, 22, 60), rain=True, bolt_seed=None):
    """A window onto the storm: a night sky that flares with lightning, rain running down the glass, a cross frame."""
    r = skia.Rect.MakeLTRB(x0, y0, x1, y1)
    c.save()
    c.clipRect(r)
    top = mix(sky, (200, 210, 255), flash * 0.8)
    c.drawRect(r, paint(shader=K.lin((0, y0), (0, y1), [top, mix(top, INK, 0.5)])))
    for i in range(5):                                                  # cloud masses
        cx = x0 + (i * 173 + T * 6) % (x1 - x0 + 200) - 100
        c.drawOval(skia.Rect.MakeXYWH(cx - 150, y0 + 40 + i * 50, 300, 90), paint(mix(top, WHITE, 0.15), 0.5, blur=30))
    if bolt_seed is not None and flash > 0.2:
        CO.bolt(c, x0 + (x1 - x0) * 0.6, y0 - 20, x0 + (x1 - x0) * 0.4, y1, seed=bolt_seed, w=6, a=min(1, flash * 1.3))
    # trees outside, black
    for i in range(3):
        bx = x0 + (x1 - x0) * (0.15 + 0.35 * i)
        c.drawPath(K.capsule(bx, y1, bx + 30, y0 + 200 + i * 40, 30, 8), paint((6, 6, 12)))
        for j in range(4):
            yy = y0 + 230 + j * 60 + i * 30
            c.drawPath(K.capsule(bx + 20, yy, bx + 20 + (-1) ** j * 120, yy - 50, 10, 3), paint((6, 6, 12)))
    if rain:
        CO.rain(c, T, x0, y0, x1, y1, n=50, a=0.35, ang=0.05, speed=900, length=40, seed=8)
        rng = K.rng_at(5, 5)
        for i in range(26):                                             # drops running down the glass
            dx = rng.uniform(x0, x1)
            dy = y0 + ((rng.uniform(0, 1) * (y1 - y0) + T * rng.uniform(40, 140)) % (y1 - y0))
            c.drawPath(K.capsule(dx, dy - rng.uniform(10, 50), dx + 1, dy, 3, 5), paint((200, 214, 255), 0.4))
            c.drawCircle(dx - 1, dy - 1, 1.5, paint(WHITE, 0.6))
    c.restore()
    fr = (30, 18, 16)
    c.drawRect(r, paint(fr, stroke=26))
    c.drawLine((x0 + x1) / 2, y0, (x0 + x1) / 2, y1, paint(fr, stroke=18))
    c.drawLine(x0, (y0 + y1) / 2, x1, (y0 + y1) / 2, paint(fr, stroke=18))


def curtain(c, x0, y0, x1, y1, colr, L, side=1, T=0.0):
    pts = [(x0, y0), (x1, y0)]
    n = 6
    for i in range(n + 1):
        u = i / n
        pts.append((x1 - (x1 - x0) * u * (0.2 if side > 0 else 1) + 20 * math.sin(i * 1.3 + T * 0.8), y1))
    p = path([(x0, y0), (x1, y0), (x1 - (x1 - x0) * 0.25 if side > 0 else x1, y1), (x0 if side > 0 else x0 + (x1 - x0) * 0.25, y1)])
    FA.lit_fill(c, p, colr, L, rim=0.8, rim_w=8)
    c.save()
    c.clipPath(p, doAntiAlias=True)
    for i in range(7):
        x = x0 + (x1 - x0) * i / 7
        c.drawLine(x, y0, x + side * 20, y1, paint(mix(colr, INK, 0.6), 0.5, stroke=14))
        c.drawLine(x + 22, y0, x + 22 + side * 20, y1, paint(mix(colr, WHITE, 0.2), 0.25, stroke=6))
    c.restore()


def lamp(c, x, y, s, T, on=1.0):
    """A fringed standard lamp: the warm key light of the flat."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    if on > 0:
        glow(c, 0, 40, 420, (255, 170, 90), 0.35 * on)
    c.drawLine(0, 150, 0, 1400, paint((40, 30, 20), stroke=14))
    shade = path([(-120, 150), (120, 150), (80, 0), (-80, 0)])
    c.drawPath(shade, paint(mix((240, 180, 110), (60, 40, 30), 1 - on)))
    c.drawPath(shade, paint(shader=K.lin((0, 0), (0, 150), [(255, 230, 170, 0.7 * on), (200, 100, 40, 0.2)])))
    for i in range(24):
        fx = -120 + i * 10.4
        c.drawLine(fx, 150, fx + 2 * math.sin(T * 2 + i), 178, paint((180, 110, 50), stroke=3))
    c.restore()


def apartment(c, T, flash=0.0, lamp_on=1.0, cam=0.0):
    """Nora's flat at night: damask wallpaper, a velvet-curtained window on the storm, the lamp, the sofa."""
    L = FA.Light("lamp")
    grad_bg(c, (40, 30, 44), (20, 14, 22))
    damask(c, 0, 0, W, H, (48, 30, 46), (90, 60, 80), a=0.35)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=K.rad((260, 520), 900, [(255, 170, 90, 0.25 * lamp_on), (0, 0, 0, 0.0), (0, 0, 0, 0.55)], [0, 0.5, 1])))
    window(c, 520, 160, 1000, 900, T, flash=flash, bolt_seed=int(T * 2) % 5)
    curtain(c, 440, 120, 600, 1000, (120, 16, 30), L, side=1, T=T)
    curtain(c, 940, 120, 1100, 1000, (120, 16, 30), L, side=-1, T=T)
    c.drawRect(skia.Rect.MakeLTRB(420, 100, 1100, 130), paint((60, 36, 20)))
    # a picture frame
    c.drawRect(skia.Rect.MakeLTRB(80, 300, 300, 560), paint((40, 26, 18)))
    c.drawRect(skia.Rect.MakeLTRB(100, 320, 280, 540), paint((70, 60, 70)))
    c.drawOval(skia.Rect.MakeLTRB(140, 360, 240, 500), paint((50, 40, 50)))
    lamp(c, 150, 460, 1.0, T, lamp_on)
    # sofa back
    sofa = K.rrect(-60, 1080, 1140, 1500, 80)
    FA.lit_fill(c, sofa, (100, 22, 36), L, rim=1.0, rim_w=10)
    for i in range(5):
        c.drawCircle(120 + i * 210, 1180, 10, paint((60, 10, 20)))
    c.drawRect(skia.Rect.MakeLTRB(0, 1500, W, H), paint((24, 14, 16)))


def car_interior(c, T, fog_a=0.4, wiper=True, headlights=True, flash=0.0):
    """Inside a car at night in the rain: the road in the headlights through the windscreen, wipers, the dash glow."""
    grad_bg(c, (10, 14, 30), (6, 6, 14))
    # windscreen view
    sx0, sy0, sx1, sy1 = -40, 120, 1120, 900
    c.save()
    c.clipPath(path([(sx0 + 60, sy0), (sx1 - 60, sy0), (sx1, sy1), (sx0, sy1)]), doAntiAlias=True)
    c.drawRect(skia.Rect.MakeLTRB(sx0, sy0, sx1, sy1), paint(shader=K.lin((0, sy0), (0, sy1), [mix((20, 30, 60), WHITE, flash * 0.6), (10, 14, 24)])))
    vy = 560
    road = path([(520, vy), (560, vy), (1300, sy1), (-220, sy1)])
    c.drawPath(road, paint((26, 26, 34)))
    if headlights:
        c.drawPath(path([(540, vy - 10), (1150, sy1), (-70, sy1)]), paint(shader=K.lin((0, vy), (0, sy1), [(255, 240, 200, 0.05), (255, 240, 200, 0.35)])))
    for i in range(6):                                                  # dashes rushing toward us
        u = ((i / 6 + T * 0.9) % 1.0) ** 2
        y = vy + (sy1 - vy) * u
        w = 4 + 30 * u
        c.drawRect(skia.Rect.MakeLTRB(540 - w / 2, y, 540 + w / 2, y + 10 + 60 * u), paint((230, 220, 160), 0.8))
    for side in (-1, 1):                                                # trees flicking past
        for i in range(5):
            u = ((i / 5 + T * 0.6) % 1.0) ** 2
            x = 540 + side * (40 + 900 * u)
            h = 60 + 700 * u
            c.drawPath(path([(x, vy - h * 0.8), (x + side * 60 * u + 30 * u, vy + h * 0.2), (x - side * 30 * u - 30 * u, vy + h * 0.2)]), paint((6, 10, 10)))
    CO.fog(c, T, vy - 60, vy + 140, color=(140, 160, 170), a=fog_a, seed=3, n=6)
    CO.rain(c, T, sx0, sy0, sx1, sy1, n=110, a=0.45, ang=0.25, speed=2600, length=50, seed=6)
    rng = K.rng_at(2, 2)
    for i in range(70):                                                 # beads on the glass
        x, y = rng.uniform(sx0, sx1), rng.uniform(sy0, sy1)
        c.drawCircle(x, y, rng.uniform(2, 6), paint((180, 200, 230), 0.35))
    c.restore()
    if wiper:
        ph = (T * 1.1) % 2.0
        a = (ph if ph < 1 else 2 - ph)
        a = K.ease(a)
        for bx in (250, 760):
            ang = math.radians(-170 + 150 * a)
            c.drawPath(K.capsule(bx, sy1 + 20, bx + 560 * math.cos(ang), sy1 + 20 + 560 * math.sin(ang), 16, 10), paint((8, 8, 10)))
    # frame of the windscreen and dash
    c.drawPath(path([(sx0, sy0 - 200), (sx1, sy0 - 200), (sx1 - 60, sy0), (sx0 + 60, sy0)]), paint((14, 12, 16)))
    c.drawPath(path([(sx0 - 100, sy1 - 40), (sx0 + 60, sy0), (sx0 + 120, sy0), (sx0 + 30, sy1)]), paint((14, 12, 16)))
    c.drawPath(path([(sx1 + 100, sy1 - 40), (sx1 - 60, sy0), (sx1 - 120, sy0), (sx1 - 30, sy1)]), paint((14, 12, 16)))
    dash = path([(-50, sy1 - 20), (W + 50, sy1 - 20), (W + 50, H), (-50, H)])
    c.drawPath(dash, paint(shader=K.lin((0, sy1), (0, H), [(40, 34, 40), (10, 8, 12)])))
    c.drawLine(-50, sy1 - 18, W + 50, sy1 - 18, paint((90, 200, 200), 0.5, stroke=3))


def swamp(c, T, fog_a=0.6, gel=(110, 220, 120), moon=True, flash=0.0):
    """A crossroads in a swamp at night: a fat moon, dead trees in moss, still black water, a signpost, fog."""
    grad_bg(c, mix((16, 30, 40), WHITE, flash * 0.5), (4, 10, 12))
    if moon:
        glow(c, 760, 380, 260, (200, 230, 200), 0.3)
        c.drawCircle(760, 380, 90, paint((226, 236, 210)))
        c.drawCircle(735, 360, 18, paint((190, 200, 180), 0.6))
        c.drawCircle(790, 410, 12, paint((190, 200, 180), 0.6))
    hy = 980
    c.drawRect(skia.Rect.MakeLTRB(0, hy, W, H), paint((6, 12, 12)))
    c.drawOval(skia.Rect.MakeLTRB(560, hy + 40, 960, hy + 120), paint((200, 230, 200), 0.18, blur=10))
    rng = K.rng_at(1, 1)
    for i, (tx, tw, th) in enumerate(((60, 50, 900), (280, 30, 600), (900, 60, 1000), (1040, 40, 760), (680, 24, 420))):
        c.drawPath(path([(tx - tw, hy + 20), (tx - tw * 0.3, hy - th), (tx + tw * 0.3, hy - th), (tx + tw, hy + 20)]), paint((6, 8, 10)))
        for j in range(4):
            yy = hy - th * (0.5 + 0.12 * j)
            sd = (-1) ** (i + j)
            c.drawPath(K.capsule(tx, yy, tx + sd * 220, yy - 120, 22, 4), paint((6, 8, 10)))
            for k in range(5):                                          # hanging moss
                mx = tx + sd * (40 + k * 36)
                my = yy - 20 - k * 20
                c.drawPath(K.bez_path([(mx, my), (mx + 6, my + 60), (mx - 4, my + 120 + rng.uniform(0, 60))]), paint((40, 70, 50), 0.8, stroke=5))
    # the road crossing
    c.drawPath(path([(470, hy), (610, hy), (900, H), (180, H)]), paint((30, 32, 28)))
    c.drawPath(path([(0, hy + 140), (W, hy + 120), (W, hy + 200), (0, hy + 230)]), paint((30, 32, 28)))
    CO.fog(c, T, hy - 140, hy + 300, color=mix((170, 190, 180), gel, 0.3), a=fog_a, seed=7, n=10, speed=30)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=K.rad((540, 1100), 900, [gel + (0.18,), (0, 0, 0, 0.0)])))


def signpost(c, x, y, s, T, L="green", names=("", "", "")):
    """A crossroads signpost whose arms are blank."""
    L = FA.Light(L)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    FA.lit_fill(c, K.rrect(-16, -620, 16, 0, 4), (90, 70, 50), L, rim=1.0, rim_w=5)
    for i, (ang, yy) in enumerate(((-12, -560), (14, -470), (-6, -380))):
        c.save()
        c.translate(0, yy)
        c.rotate(ang)
        sd = 1 if i % 2 == 0 else -1
        arm = path([(0, -34), (sd * 240, -34), (sd * 290, 0), (sd * 240, 34), (0, 34)])
        FA.lit_fill(c, arm, (150, 130, 96), L, rim=1.0, rim_w=5)
        c.drawPath(arm, paint(INK, 0.6, stroke=3))
        for k in range(3):                                              # where the letters were, worn away
            c.drawRect(skia.Rect.MakeLTRB(sd * (40 + k * 60), -10, sd * (40 + k * 60) + sd * 40, 8), paint((110, 96, 70), 0.6))
        c.restore()
    CO.cobweb(c, 0, -620, 140, 10, 80, a=0.6, seed=4)
    c.restore()


def dorm(c, T, lamp_on=1.0):
    """A student's room at 2 a.m.: a desk lamp, a pinboard of notes, a window on the night, posters."""
    grad_bg(c, (30, 24, 40), (14, 10, 18))
    c.drawRect(skia.Rect.MakeLTRB(620, 220, 1000, 700), paint((10, 14, 34)))
    rng = K.rng_at(4, 4)
    for i in range(30):
        c.drawRect(skia.Rect.MakeXYWH(rng.uniform(640, 980), rng.uniform(420, 690), 10, 14), paint((255, 220, 120), rng.uniform(0.3, 0.9)))
    c.drawRect(skia.Rect.MakeLTRB(620, 220, 1000, 700), paint((60, 50, 60), stroke=18))
    c.drawRect(skia.Rect.MakeLTRB(60, 260, 460, 640), paint((140, 100, 60)))
    for i in range(9):
        x, y = 80 + (i % 3) * 126, 280 + (i // 3) * 118
        c.drawRect(skia.Rect.MakeXYWH(x, y, 100, 90), paint([(250, 240, 140), (250, 190, 200), (200, 230, 250)][i % 3]))
        c.drawCircle(x + 50, y + 8, 6, paint((200, 30, 30)))
        for k in range(3):
            c.drawLine(x + 10, y + 30 + k * 18, x + 86, y + 30 + k * 18, paint((80, 80, 90), 0.6, stroke=2))
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=K.rad((540, 1150), 900, [(255, 200, 120, 0.25 * lamp_on), (0, 0, 0, 0.0)])))


def exam_hall(c, T, dim=0.0):
    """An exam hall: tall windows, rows of desks receding under hanging lamps, a clock."""
    grad_bg(c, (40, 44, 50), (20, 22, 26))
    for i in range(4):
        x = 40 + i * 270
        c.drawRect(skia.Rect.MakeLTRB(x, 240, x + 180, 760), paint((60, 70, 90)))
        c.drawRect(skia.Rect.MakeLTRB(x, 240, x + 180, 760), paint((24, 24, 28), stroke=12))
        c.drawLine(x + 90, 240, x + 90, 760, paint((24, 24, 28), stroke=8))
    c.drawCircle(540, 300, 60, paint((236, 232, 220)))
    c.drawCircle(540, 300, 60, paint(INK, stroke=8))
    c.drawLine(540, 300, 540, 256, paint(INK, stroke=5))
    c.drawLine(540, 300, 572, 300, paint(INK, stroke=5))
    c.drawRect(skia.Rect.MakeLTRB(0, 820, W, H), paint((70, 56, 44)))
    for r in range(5):
        u = r / 4
        y = 860 + 520 * u ** 1.4
        w = 120 + 240 * u
        for q in range(-3, 4):
            x = 540 + q * (w + 20)
            c.drawRect(skia.Rect.MakeLTRB(x - w / 2, y, x + w / 2, y + 16 + 30 * u), paint((120, 90, 60)))
            c.drawRect(skia.Rect.MakeLTRB(x - w / 2 + 6, y + 16 + 30 * u, x - w / 2 + 14, y + 60 + 120 * u), paint((50, 40, 30)))
    for q in range(3):
        x = 220 + q * 320
        c.drawLine(x, 0, x, 160, paint((30, 30, 30), stroke=4))
        c.drawPath(path([(x - 70, 200), (x + 70, 200), (x + 30, 150), (x - 30, 150)]), paint((40, 46, 40)))
        pool(c, x, 700, 260, 520, (255, 250, 220), 0.12 * (1 - dim))


def clinic(c, T, power=1.0, emergency=0.0):
    """A procedure room: teal tiles, a steel trolley, a surgical lamp - or, with the power gone, a red emergency light."""
    base = mix((40, 90, 96), (30, 4, 8), emergency)
    grad_bg(c, mix(base, WHITE, 0.08 * power), mix(base, INK, 0.5))
    for y in range(0, H, 90):
        c.drawLine(0, y, W, y, paint(mix(base, INK, 0.3), 0.5, stroke=3))
    for x in range(0, W, 90):
        c.drawLine(x, 0, x, H, paint(mix(base, INK, 0.3), 0.5, stroke=3))
    if power > 0:
        c.drawOval(skia.Rect.MakeLTRB(300, 120, 780, 260), paint((220, 230, 230), power))
        c.drawOval(skia.Rect.MakeLTRB(330, 140, 750, 240), paint((255, 255, 240), power))
        glow(c, 540, 190, 400, (220, 255, 240), 0.3 * power)
    if emergency > 0:
        ph = 0.6 + 0.4 * math.sin(T * 7)
        c.drawCircle(940, 260, 40, paint((255, 30, 20), emergency))
        glow(c, 940, 260, 380, (255, 20, 10), 0.45 * emergency * ph)
        c.drawRect(skia.Rect.MakeWH(W, H), paint((120, 0, 0), 0.25 * emergency * ph))


def ward(c, T, power=1.0):
    """A hospital ward at night: a curtain rail, a drip stand, a window, the bed."""
    grad_bg(c, (60, 80, 90), (24, 30, 36))
    c.drawRect(skia.Rect.MakeLTRB(0, 140, W, 160), paint((160, 170, 170)))
    for i in range(12):
        x = i * 96
        c.drawPath(K.bez_path([(x, 160), (x + 48, 600), (x + 10, 1000)]), paint((150, 190, 180), 0.5, stroke=40))
    c.drawLine(880, 300, 880, 1300, paint((180, 190, 190), stroke=10))
    c.drawRoundRect(skia.Rect.MakeLTRB(830, 320, 930, 470), 20, 20, paint((200, 230, 240), 0.7))
    c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0), 0.4 * (1 - power)))


def cockpit(c, T, warn=0.0, flash=0.0):
    """A cockpit at night in a storm: dark windows with rain, an instrument panel glowing green - and the red warnings."""
    grad_bg(c, (8, 10, 20), (4, 4, 8))
    c.save()
    c.clipPath(path([(60, 200), (1020, 200), (1080, 760), (0, 760)]), doAntiAlias=True)
    c.drawRect(skia.Rect.MakeLTRB(0, 200, W, 760), paint(shader=K.lin((0, 200), (0, 760), [mix((20, 24, 50), WHITE, flash * 0.7), (6, 6, 16)])))
    CO.rain(c, T, 0, 200, W, 760, n=120, a=0.5, ang=-0.5, speed=3000, length=60, seed=4)
    if flash > 0.3:
        CO.bolt(c, 700, 180, 520, 760, seed=3, w=8, a=flash)
    c.restore()
    c.drawLine(540, 200, 540, 760, paint((20, 20, 26), stroke=34))
    c.drawPath(path([(0, 760), (W, 760), (W, H), (0, H)]), paint((22, 22, 28)))
    rng = K.rng_at(6, 6)
    for i in range(14):
        x, y = 80 + (i % 7) * 140, 840 + (i // 7) * 160
        c.drawCircle(x, y, 54, paint((10, 12, 10)))
        c.drawCircle(x, y, 54, paint((70, 70, 80), stroke=6))
        a = rng.uniform(0, 6.28) + math.sin(T * 0.7 + i) * 0.2
        c.drawLine(x, y, x + 44 * math.cos(a), y + 44 * math.sin(a), paint((120, 255, 150), stroke=4))
        g = paint((60, 255, 120), 0.18, blur=20)
        g.setBlendMode(skia.BlendMode.kPlus)
        c.drawCircle(x, y, 60, g)
    if warn > 0:
        on = (math.floor(T * 5) % 2) == 0
        for x in (300, 780):
            c.drawRoundRect(skia.Rect.MakeLTRB(x - 110, 1170, x + 110, 1240), 10, 10, paint((255, 30, 20) if on else (80, 10, 10), warn))
        glow(c, 540, 1200, 500, (255, 20, 10), 0.35 * warn * (1 if on else 0.4))


def flat_dark(c, T, moon=0.6):
    """The reader's real night: a room with no colour to speak of, a cold moon through the blinds, no gel, no comic."""
    grad_bg(c, (34, 36, 40), (12, 12, 14))
    for i in range(10):                                                 # light through the blinds, across the wall
        y = 300 + i * 46
        c.drawPath(path([(560, y), (1080, y + 60), (1080, y + 82), (560, y + 18)]), paint((150, 160, 176), 0.12 * moon))
    c.drawRect(skia.Rect.MakeLTRB(600, 260, 980, 760), paint((60, 66, 76), 0.6))
    for i in range(16):
        c.drawLine(600, 270 + i * 31, 980, 270 + i * 31, paint((20, 20, 24), stroke=10))
    c.drawRect(skia.Rect.MakeLTRB(0, 1240, W, H), paint((20, 20, 22)))


def street(c, T):
    """A doorway on a dark wet street: identical houses, no street lights, rain."""
    grad_bg(c, (22, 24, 30), (8, 8, 10))
    for side in (-1, 1):
        for i in range(5):
            u = i / 5
            x = 540 + side * (120 + 500 * (1 - u) ** 1.5)
            h = 160 + 600 * (1 - u) ** 1.5
            w = 60 + 300 * (1 - u) ** 1.5
            x0 = x if side > 0 else x - w
            c.drawRect(skia.Rect.MakeLTRB(x0, 900 - h, x0 + w, 900), paint((30, 30, 36)))
            c.drawPath(path([(x0, 900 - h), (x0 + w / 2, 900 - h - w * 0.4), (x0 + w, 900 - h)]), paint((26, 26, 30)))
            c.drawRect(skia.Rect.MakeLTRB(x0 + w * 0.3, 900 - h * 0.6, x0 + w * 0.6, 900 - h * 0.3), paint((14, 14, 16)))
    c.drawPath(path([(480, 900), (600, 900), (1200, H), (-120, H)]), paint((18, 18, 22)))
    for i in range(6):
        c.drawOval(skia.Rect.MakeXYWH(300 + i * 80, 1100 + i * 90, 160, 30), paint((80, 90, 110), 0.25, blur=6))
    CO.rain(c, T, 0, 0, W, H, n=160, a=0.35, ang=0.1, speed=2200, length=60, seed=11, color=(170, 180, 196))

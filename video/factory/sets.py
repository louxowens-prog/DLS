"""The painted flats and handmade sets. Each backdrop paints a full 1080 x 1920 frame once (cached, with a scenic-paint
brush texture laid over it); anything that moves is drawn by the scene on top.

The grey town is all soot, slate and wet brick; the factory inside is candy: mint hills, pink sugar, lemon light,
a chocolate river. Every set looks built: flat painted skies, plywood cut-outs, visible seams.
"""
import math

import numpy as np
import skia

import draw as D
from draw import (ASH, BRICK, CARAMEL, CHERRY, CHOC, CHOC2, CREAM, FOG, GOLD, GOLD2, GOLD3, GRASS, H, INK, LEMON,
                  LILAC, MINT, MUSTARD, PEACH, PINK, PLUM, SKYB, SLATE, SOOT, TEAL, W, WHITE, mix, paint, path, shade)


def _grad(c, y0, y1, cols, x0=0, x1=W):
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(shader=D.lin((0, y0), (0, y1), cols)))


# ------------------------------------------------------------------ the grey town

def town(c):
    _grad(c, 0, 1250, [(120, 124, 128), (150, 150, 148), (170, 166, 158)])
    rng = np.random.default_rng(3)
    for i in range(7):                                                  # far chimneys and their smoke
        x = 60 + i * 160 + rng.uniform(-30, 30)
        h = rng.uniform(300, 560)
        c.drawRect(skia.Rect.MakeLTRB(x, 1000 - h, x + 44, 1000), paint((96, 94, 96)))
        for k in range(6):
            c.drawCircle(x + 22 + k * 26, 1000 - h - 40 - k * 50, 36 + k * 12, paint((110, 110, 112), 0.35 - k * 0.04))
    for i in range(5):                                                  # factory sheds (saw-tooth roofs)
        x0 = -40 + i * 240
        c.drawPath(path([(x0, 1050), (x0, 900), (x0 + 120, 830), (x0 + 120, 900), (x0 + 240, 830), (x0 + 240, 1050)]),
                   paint((84, 82, 84)))
    for side in (-1, 1):                                                # the terraces either side of the street
        for j in range(4):
            x = (0 if side < 0 else W) + side * (-60 - j * 0)
            y0 = 980 + j * 120
            hw = 330 - j * 30
            xa, xb = (0, hw) if side < 0 else (W - hw, W)
            c.drawRect(skia.Rect.MakeLTRB(xa, y0 - 260 + j * 40, xb, y0 + 170), paint(mix(BRICK, SOOT, 0.35 + j * 0.05)))
            for r in range(3):
                for q in range(2):
                    wx = xa + 50 + q * (hw / 2)
                    wy = y0 - 200 + j * 40 + r * 110
                    lit = rng.random() < 0.25
                    c.drawRect(skia.Rect.MakeLTRB(wx, wy, wx + 70, wy + 80), paint((230, 200, 120) if lit else (60, 64, 72), 0.9))
                    c.drawLine(wx + 35, wy, wx + 35, wy + 80, paint((40, 36, 36), stroke=4))
            c.drawPath(path([(xa - 10, y0 - 260 + j * 40), ((xa + xb) / 2, y0 - 330 + j * 40), (xb + 10, y0 - 260 + j * 40)]),
                       paint((70, 72, 78)))
    _grad(c, 1150, H, [(90, 90, 94), (60, 60, 64)])                     # the wet cobbled street
    for r in range(22):
        y = 1160 + r * r * 1.6
        for q in range(int(10 + r * 1.5)):
            x = (q + (r % 2) * 0.5) * W / (10 + r * 1.5)
            c.drawOval(skia.Rect.MakeXYWH(x, y, 60 + r * 3, 14 + r * 1.2), paint((110, 110, 116), 0.35))
    for x in (160, 920):                                                # gas lamps
        c.drawRect(skia.Rect.MakeLTRB(x - 8, 700, x + 8, 1260), paint((40, 40, 44)))
        c.drawCircle(x, 690, 60, paint((255, 220, 150), 0.25, blur=30))
        c.drawRect(skia.Rect.MakeLTRB(x - 26, 650, x + 26, 720), paint((230, 200, 140), 0.8))
    for i in range(6):                                                  # puddles with the lamps in them
        x, y = 150 + i * 160, 1400 + (i % 3) * 140
        c.drawOval(skia.Rect.MakeXYWH(x, y, 200, 40), paint((130, 136, 146), 0.6))


def office(c):
    _grad(c, 0, 1300, [(128, 134, 124), (112, 118, 110)])
    c.drawRect(skia.Rect.MakeLTRB(620, 220, 1000, 700), paint((70, 74, 80)))                           # rainy window
    c.drawRect(skia.Rect.MakeLTRB(640, 240, 980, 680), paint((150, 156, 164)))
    c.drawLine(810, 240, 810, 680, paint((70, 74, 80), stroke=12))
    c.drawLine(640, 460, 980, 460, paint((70, 74, 80), stroke=12))
    for k in range(5):                                                  # shelves of grey files
        y = 300 + k * 120
        c.drawRect(skia.Rect.MakeLTRB(60, y, 520, y + 14), paint((90, 80, 70)))
        for j in range(12):
            c.drawRect(skia.Rect.MakeLTRB(70 + j * 37, y - 90 + (j % 3) * 8, 100 + j * 37, y), paint(mix((150, 146, 136), SOOT, (j % 4) * 0.1)))
    _grad(c, 1300, H, [(96, 84, 72), (70, 60, 52)])
    c.drawRect(skia.Rect.MakeLTRB(40, 1180, 1040, 1240), paint((110, 86, 64)))                          # the desk top
    c.drawRect(skia.Rect.MakeLTRB(80, 1240, 140, 1700), paint((90, 70, 54)))
    c.drawRect(skia.Rect.MakeLTRB(940, 1240, 1000, 1700), paint((90, 70, 54)))


def kitchen(c):
    _grad(c, 0, 1300, [(52, 58, 76), (70, 74, 90)])
    c.drawRect(skia.Rect.MakeLTRB(90, 260, 470, 760), paint((34, 38, 52)))                              # night window
    c.drawRect(skia.Rect.MakeLTRB(110, 280, 450, 740), paint((40, 50, 74)))
    c.drawCircle(360, 380, 40, paint((200, 210, 230), 0.5))
    c.drawLine(280, 280, 280, 740, paint((34, 38, 52), stroke=14))
    c.drawLine(110, 510, 450, 510, paint((34, 38, 52), stroke=14))
    for j in range(7):                                                  # tiles
        c.drawLine(560, 400 + j * 70, 1080, 400 + j * 70, paint((90, 96, 110), 0.4, stroke=2))
    c.drawRect(skia.Rect.MakeLTRB(760, 250, 1010, 900), paint((180, 184, 180)))                         # fridge
    c.drawRect(skia.Rect.MakeLTRB(780, 470, 990, 478), paint((140, 144, 140)))
    c.drawRect(skia.Rect.MakeLTRB(810, 540, 930, 650), paint((250, 246, 230)))                          # a child's drawing
    c.drawCircle(870, 580, 20, paint((240, 180, 60)))
    c.drawLine(840, 630, 900, 630, paint((60, 140, 60), stroke=6))
    _grad(c, 1300, H, [(70, 60, 56), (50, 42, 40)])
    c.drawPath(path([(40, 1220), (1040, 1220), (1080, 1340), (0, 1340)]), paint((150, 110, 76)))       # the table
    c.drawRect(skia.Rect.MakeLTRB(0, 1340, 1080, 1370), paint((110, 80, 56)))
    c.drawLine(540, 0, 540, 420, paint((30, 30, 34), stroke=4))                                          # the hanging lamp
    c.drawPath(path([(430, 520), (650, 520), (590, 420), (490, 420)]), paint((200, 120, 50)))
    c.drawPath(path([(40, 1220), (1040, 1220), (650, 520), (430, 520)]), paint((255, 220, 150), 0.12))


def shop(c):
    town(c)
    c.drawRect(skia.Rect.MakeLTRB(160, 520, 920, 1240), paint((50, 40, 40)))                            # the shopfront
    c.drawRect(skia.Rect.MakeLTRB(200, 700, 880, 1180), paint((255, 214, 150)))                          # the lit window
    c.drawRect(skia.Rect.MakeLTRB(200, 700, 880, 1180), paint((255, 190, 110), 0.3, blur=40))
    rng = np.random.default_rng(8)
    for r in range(3):                                                  # jars of sweets: the only colour in town
        c.drawRect(skia.Rect.MakeLTRB(210, 830 + r * 120, 870, 842 + r * 120), paint((150, 100, 70)))
        for j in range(7):
            x = 250 + j * 90
            y = 830 + r * 120
            col = [PINK, MINT, LEMON, LILAC, CHERRY, SKYB, (255, 160, 80)][(j + r * 2) % 7]
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x - 30, y - 90, x + 30, y), 10, 10), paint((230, 240, 245), 0.6))
            for q in range(6):
                c.drawCircle(x + rng.uniform(-20, 20), y - 14 - rng.uniform(0, 60), 11, paint(col))
    shade(c, path([(140, 520), (940, 520), (980, 640), (100, 640)]), (150, 40, 50), k=0.2)            # striped awning
    for j in range(9):
        c.drawPath(path([(140 + j * 89, 520), (185 + j * 89, 520), (190 + j * 94, 640), (145 + j * 94, 640)]), paint(CREAM, 0.9))
    D.label(c, "SWEETS · CHOCOLATE · TOFFEE", 540, 600, 40, "rye-400", CREAM, tag="set", outline=(110, 30, 40), ow=6)


def gates(c):
    _grad(c, 0, 1300, [(118, 122, 128), (156, 154, 150)])
    c.drawRect(skia.Rect.MakeLTRB(80, 380, 1000, 1150), paint((110, 96, 96)))                           # the factory
    for i in range(5):
        x = 150 + i * 190
        c.drawRect(skia.Rect.MakeLTRB(x, 120, x + 60, 400), paint((96, 84, 86)))
        for k in range(6):                                              # candy-coloured smoke: a hint of what's inside
            c.drawCircle(x + 30 + k * 18, 100 - k * 40, 30 + k * 10, paint([PINK, MINT, LEMON, LILAC, PEACH][i], 0.55 - k * 0.07))
    for r in range(4):
        for q in range(7):
            c.drawRect(skia.Rect.MakeLTRB(130 + q * 125, 460 + r * 150, 190 + q * 125, 550 + r * 150), paint((70, 64, 70)))
    c.drawCircle(540, 330, 90, paint(CREAM))                                                             # the big clock
    c.drawCircle(540, 330, 90, paint((60, 50, 44), stroke=12))
    c.drawLine(540, 330, 540, 270, paint(INK, stroke=8))
    c.drawLine(540, 330, 585, 350, paint(INK, stroke=8))
    c.drawRect(skia.Rect.MakeLTRB(0, 900, W, 1300), paint((120, 90, 80)))                                 # the wall
    for r in range(8):
        for q in range(12):
            c.drawRect(skia.Rect.MakeXYWH(q * 92 + (r % 2) * 46, 905 + r * 50, 88, 46), paint(mix(BRICK, SOOT, 0.2 + ((q + r) % 3) * 0.08)))
    _grad(c, 1300, H, [(96, 94, 96), (70, 68, 70)])
    for sx in (-1, 1):                                                  # the great iron gates, swung open
        x0 = 540 + sx * 40
        for j in range(8):
            xx = x0 + sx * (j * 50)
            c.drawLine(xx, 640, xx, 1320, paint((34, 34, 38), stroke=12))
            c.drawCircle(xx, 630, 12, paint((180, 140, 60)))
        c.drawLine(x0, 700, x0 + sx * 360, 700, paint((34, 34, 38), stroke=14))
        c.drawLine(x0, 1000, x0 + sx * 360, 1000, paint((34, 34, 38), stroke=14))
        for j in range(4):
            cx = x0 + sx * (45 + j * 90)
            c.drawCircle(cx, 850, 40, paint((34, 34, 38), stroke=8))


def hall(c):
    _grad(c, 0, H, [(40, 30, 34), (60, 44, 44)])
    for x in (120, 960):                                                # pillars
        shade(c, D.rrect(x - 70, 200, x + 70, 1700, 20), (90, 70, 66), k=0.3)
    shade(c, D.rrect(300, 380, 780, 1560, 240), (120, 90, 70), k=0.3)                                   # the arch
    _grad(c, 1560, H, [(70, 50, 44), (40, 30, 28)])


def door(c, x, y, s, openk, T):
    """The great door (drawn per frame): tall, pale, round-topped, brass handle; opens inward on a blaze of light."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    frame = D.rrect(-230, -1100, 230, 0, 230)
    c.save()
    c.clipPath(frame, doAntiAlias=True)
    c.drawRect(skia.Rect.MakeLTRB(-240, -1110, 240, 0), paint(shader=D.rad((0, -500), 700, [(255, 250, 220), (255, 214, 160), (240, 170, 150)])))
    for i in range(12):                                                 # beams of candy light
        a = -math.pi / 2 + (i - 5.5) * 0.12
        c.drawPath(path([(0, -300), (900 * math.cos(a - 0.03), -300 + 900 * math.sin(a - 0.03)),
                         (900 * math.cos(a + 0.03), -300 + 900 * math.sin(a + 0.03))]), paint([PINK, MINT, LEMON, LILAC][i % 4], 0.35))
    w = 460 * (1 - openk)
    if w > 1:                                                           # the door leaf swinging in
        leaf = D.rrect(-230, -1100, -230 + w, 0, 230 if openk < 0.05 else 40)
        shade(c, leaf, (236, 226, 200), k=0.2)
        for j in range(3):
            c.drawRect(skia.Rect.MakeLTRB(-190, -900 + j * 280, -190 + w * 0.8, -700 + j * 280), paint((200, 188, 160), 0.6, stroke=6))
        c.drawCircle(-230 + w - 40, -520, 22, paint(GOLD))
        c.drawCircle(-230 + w - 40, -520, 22, paint(GOLD3, stroke=4))
    c.restore()
    c.drawPath(frame, paint((70, 50, 40), stroke=26))
    c.restore()
    if openk > 0:
        c.drawCircle(x, y - 500 * s, 700 * s * openk, paint((255, 230, 180), 0.25 * openk, blur=80))


# ------------------------------------------------------------------ inside: the wonderland

def wonder(c):
    _grad(c, 0, 1100, [(90, 150, 250), (240, 120, 200), (255, 190, 120)])                               # painted sky dome
    for i in range(6):                                                  # painted clouds, flat as a stage cloth
        x, y = 90 + i * 190, 180 + (i % 3) * 90
        for k in range(4):
            c.drawCircle(x + k * 40, y + (k % 2) * 16, 50 + (k % 2) * 16, paint(WHITE, 0.8))
    for i, (x, h, col) in enumerate(((120, 520, (60, 210, 150)), (380, 620, (130, 220, 90)), (700, 560, (50, 200, 170)), (980, 640, (110, 210, 120)))):
        p = skia.Path()                                                  # rolling sugar hills
        p.moveTo(x - 520, 1200)
        p.cubicTo(x - 250, 1200 - h, x + 250, 1200 - h, x + 520, 1200)
        p.close()
        shade(c, p, col, k=0.18, edge=0.2)
    for i, (x, y, r, col) in enumerate(((180, 900, 90, (255, 70, 150)), (880, 860, 110, (255, 210, 40)), (520, 780, 70, (160, 90, 240)),
                                         (330, 1000, 60, (255, 110, 60)), (980, 1020, 70, (40, 200, 180)))):
        c.drawLine(x, y, x, y + 420, paint(WHITE, stroke=16))            # lollipop trees
        shade(c, D.circle(x, y, r), col, k=0.25)
        for k in range(4):
            c.drawArc(skia.Rect.MakeLTRB(x - r * (0.25 + k * 0.2), y - r * (0.25 + k * 0.2), x + r * (0.25 + k * 0.2),
                                         y + r * (0.25 + k * 0.2)), k * 60, 250, False, paint(WHITE, 0.7, stroke=9))
    for x, y, s in ((90, 1330, 1.0), (1000, 1300, 1.2), (640, 1180, 0.7)):                              # candy mushrooms
        shade(c, D.rrect(x - 26 * s, y - 120 * s, x + 26 * s, y, 18), CREAM, k=0.2)
        shade(c, D.oval(x - 110 * s, y - 190 * s, x + 110 * s, y - 90 * s), CHERRY, k=0.25)
        for k in range(5):
            c.drawCircle(x - 70 * s + k * 35 * s, y - 150 * s + (k % 2) * 20 * s, 12 * s, paint(WHITE))
    _grad(c, 1150, H, [(90, 210, 110), (50, 160, 80)])                                                   # the lawn (sugar grass)
    rng = np.random.default_rng(2)
    for i in range(300):
        x, y = rng.uniform(0, W), rng.uniform(1170, H)
        c.drawLine(x, y, x + rng.uniform(-4, 4), y - 16, paint((90, 170, 110), 0.5, stroke=3))
    for i in range(40):                                                 # sugar flowers
        x, y = rng.uniform(0, W), rng.uniform(1300, H)
        col = [PINK, LEMON, WHITE, LILAC][i % 4]
        for q in range(5):
            b = q * 2 * math.pi / 5
            c.drawCircle(x + 10 * math.cos(b), y + 10 * math.sin(b), 9, paint(col))
        c.drawCircle(x, y, 6, paint((240, 150, 60)))


def river(c, T, y0=1180, amp=1.0):
    """The chocolate river (drawn per frame): a great waterfall on the left, the glossy current sliding through the lawn,
    glints on the surface and a bank of froth where the fall hits."""
    p = skia.Path()
    p.moveTo(0, y0 + 60)
    p.cubicTo(300, y0 - 40, 600, y0 + 230, 1080, y0 + 120)
    p.lineTo(1080, y0 + 330)
    p.cubicTo(600, y0 + 420, 300, y0 + 180, 0, y0 + 300)
    p.close()
    c.drawPath(p, paint(shader=D.lin((0, y0), (0, y0 + 360), [(120, 66, 34), (92, 50, 26), (70, 38, 20)])))
    c.drawPath(p, paint((60, 30, 14), 0.8, stroke=5))
    c.save()
    c.clipPath(p, doAntiAlias=True)
    for i in range(26):                                                 # the current: glossy streaks sliding along
        u = ((T * 0.16 + i / 26) % 1.0)
        x = -240 + u * 1560
        y = y0 + 110 + 110 * math.sin(i * 2.1) + 60 * math.sin(x / 300)
        c.drawOval(skia.Rect.MakeXYWH(x, y, 190, 16), paint(CHOC2, 0.8))
        c.drawOval(skia.Rect.MakeXYWH(x + 30, y + 2, 90, 6), paint((226, 176, 128), 0.65))
    for i in range(14):                                                 # glints of light on the gloss
        u = ((T * 0.22 + i / 14 * 1.7) % 1.0)
        x = -60 + u * 1200
        y = y0 + 150 + 80 * math.sin(i * 3.3) + 50 * math.sin(x / 260)
        tw = 0.5 + 0.5 * math.sin(T * 7 + i * 1.9)
        c.drawOval(skia.Rect.MakeXYWH(x, y, 26 + 20 * tw, 5), paint((255, 236, 200), 0.75 * tw))
    c.restore()
    cliff = D.smooth([(-40, y0 - 760), (160, y0 - 800), (400, y0 - 750), (470, y0 - 560), (500, y0 - 200), (540, y0 + 120),
                      (-40, y0 + 140)])                                 # a cliff of chocolate cake, cream frosting on top
    shade(c, cliff, (66, 36, 22), k=0.3, edge=0.3)
    for j in range(3):
        c.drawLine(-40, y0 - 520 + j * 220, 480 + j * 20, y0 - 540 + j * 220, paint((236, 214, 180), 0.7, stroke=16))
    for j in range(9):
        x = -20 + j * 58
        c.drawPath(D.smooth([(x - 30, y0 - 790), (x + 30, y0 - 790), (x + 22, y0 - 700 + (j % 3) * 30), (x, y0 - 680 + (j % 3) * 30),
                             (x - 22, y0 - 700 + (j % 3) * 30)]), paint((250, 240, 225)))
    fall = D.smooth([(190, y0 - 700), (260, y0 - 712), (330, y0 - 700), (344, y0 - 300), (372, y0 + 150), (150, y0 + 150),
                     (176, y0 - 300)])                                  # the falling sheet, narrower than the cliff
    c.drawPath(fall, paint(shader=D.lin((150, 0), (370, 0), [(130, 74, 38), (190, 126, 74), (214, 156, 100), (140, 80, 40)])))
    c.save()
    c.clipPath(fall, doAntiAlias=True)
    for i in range(24):                                                 # the pour, streaking down fast
        yy = y0 - 760 + ((T * 900 + i * 173) % 1000)
        xx = 156 + i * 9
        c.drawLine(xx, yy, xx + 2, yy + 180, paint((96, 50, 24), 0.35, stroke=5))
        c.drawLine(xx + 4, yy + 40, xx + 5, yy + 150, paint((250, 224, 184), 0.85, stroke=4))
    c.restore()
    p2 = skia.Path()                                                    # the curl of the pour over the lip
    p2.moveTo(180, y0 - 700)
    p2.quadTo(260, y0 - 750, 340, y0 - 700)
    c.drawPath(p2, paint((226, 176, 124), stroke=22))
    for i in range(16):                                                 # froth at the foot, churning
        fx = 80 + i * 24 + 8 * math.sin(T * 5 + i)
        fy = y0 + 140 + 16 * math.sin(T * 6 + i * 1.3) - 20 * (1 - abs(i - 7.5) / 7.5)
        c.drawCircle(fx, fy, 36 + 8 * math.sin(T * 4 + i), paint((240, 214, 176), 0.92))
        c.drawCircle(fx - 6, fy - 8, 10, paint(WHITE, 0.55))
    for i in range(10):                                                 # spray drifting up off it
        u = (T * 0.8 + i / 10) % 1.0
        c.drawCircle(80 + i * 34 + 20 * math.sin(i + T), y0 + 130 - 200 * u, 12 * (1 - u) + 2, paint((244, 220, 190), 0.55 * (1 - u)))


def spring(c):
    """Spring in the town: the same streets, washed and blossoming (the dad's walk)."""
    _grad(c, 0, 1250, [(150, 196, 236), (220, 230, 226), (255, 226, 190)])
    c.drawCircle(820, 330, 110, paint((255, 236, 170)))
    c.drawCircle(820, 330, 230, paint((255, 230, 160), 0.3, blur=60))
    for i, (x, h, col) in enumerate(((180, 380, (140, 196, 120)), (620, 460, (120, 186, 110)), (1000, 360, (150, 200, 126)))):
        p = skia.Path()
        p.moveTo(x - 560, 1250)
        p.cubicTo(x - 260, 1250 - h, x + 260, 1250 - h, x + 560, 1250)
        p.close()
        shade(c, p, col, k=0.15, edge=0.15)
    rng = np.random.default_rng(12)
    for x, y, r in ((150, 900, 170), (930, 860, 190), (560, 980, 120)):  # blossom trees
        c.drawLine(x, y + r * 0.2, x, 1260, paint((110, 76, 60), stroke=26))
        for k in range(46):
            a, d = rng.uniform(0, 2 * math.pi), r * math.sqrt(rng.uniform(0, 1))
            c.drawCircle(x + d * math.cos(a), y + d * math.sin(a) * 0.8, rng.uniform(22, 40),
                         paint([(255, 200, 220), (250, 176, 206), (255, 230, 236)][k % 3]))
    _grad(c, 1240, H, [(130, 190, 110), (96, 160, 90)])
    c.drawPath(path([(420, 1240), (660, 1240), (1000, H), (80, H)]), paint((226, 206, 170)))              # the path
    for i in range(60):
        x, y = rng.uniform(0, W), rng.uniform(1280, H)
        col = [(255, 240, 120), WHITE, (250, 180, 210)][i % 3]
        c.drawCircle(x, y, 7, paint(col))


def room(c, n):
    """The four workshop rooms, each its own sugar colour."""
    if n == 1:                                                          # the untangler: lilac and lemon stripes
        for j in range(12):
            c.drawRect(skia.Rect.MakeLTRB(j * 90, 0, j * 90 + 90, 1300), paint([LILAC, (230, 210, 250)][j % 2]))
        _grad(c, 1300, H, [(200, 160, 220), (150, 110, 170)])
    elif n == 2:                                                        # the press: brass pipes and copper
        _grad(c, 0, 1300, [(120, 80, 50), (160, 110, 60)])
        for j in range(6):
            x = 80 + j * 190
            shade(c, D.rrect(x - 20, 0, x + 20, 1300, 12), (200, 150, 70), k=0.35)
            for k in range(5):
                c.drawCircle(x, 150 + k * 250, 26, paint((150, 100, 40)))
        _grad(c, 1300, H, [(110, 76, 48), (80, 54, 36)])
    elif n == 3:                                                        # the mirror room: red velvet
        _grad(c, 0, 1300, [(120, 20, 40), (160, 40, 60)])
        for j in range(10):
            x = j * 120
            c.drawRect(skia.Rect.MakeLTRB(x, 0, x + 40, 1300), paint((90, 10, 30), 0.5))
        _grad(c, 1300, H, [(70, 20, 30), (40, 10, 20)])
        for j in range(8):
            c.drawLine(0, 1320 + j * 80, W, 1320 + j * 80, paint((120, 60, 50), 0.4, stroke=3))
    else:                                                               # the kitchen of what-if: mint and cream tiles
        for r in range(15):
            for q in range(10):
                c.drawRect(skia.Rect.MakeXYWH(q * 108, r * 90, 106, 88), paint([MINT, CREAM][(q + r) % 2]))
        _grad(c, 1300, H, [(170, 120, 90), (130, 90, 66)])
        for j in range(10):
            c.drawLine(j * 110, 1300, j * 110 - 200, H, paint((110, 76, 56), 0.5, stroke=3))


def balcony(c):
    """The factory balcony: the whole wonderland below, lit gold."""
    wonder(c)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((255, 200, 120), 0.18))
    _grad(c, 1320, H, [(140, 90, 60), (100, 60, 40)])
    c.drawRect(skia.Rect.MakeLTRB(0, 1300, W, 1340), paint(GOLD3))
    for j in range(14):
        c.drawRect(skia.Rect.MakeLTRB(20 + j * 78, 1340, 36 + j * 78, 1560), paint(GOLD3))
    c.drawRect(skia.Rect.MakeLTRB(0, 1550, W, 1580), paint(GOLD3))


def clinic(c):
    _grad(c, 0, 1300, [(150, 176, 164), (130, 160, 148)])
    c.drawRect(skia.Rect.MakeLTRB(620, 260, 1000, 700), paint((230, 236, 240)))                          # the lightbox
    c.drawRect(skia.Rect.MakeLTRB(620, 260, 1000, 700), paint((120, 130, 140), stroke=10))
    c.drawRect(skia.Rect.MakeLTRB(80, 300, 440, 640), paint((240, 236, 214)))                            # a chart on the wall
    for j in range(6):
        c.drawLine(110, 350 + j * 45, 410, 350 + j * 45, paint((150, 150, 150), stroke=5))
    _grad(c, 1300, H, [(170, 160, 150), (140, 130, 122)])
    c.drawRect(skia.Rect.MakeLTRB(0, 1180, W, 1240), paint((150, 120, 90)))


def storybook(c, tone=(214, 196, 160)):
    """The true story is told as an illustration: warm paper."""
    c.drawRect(skia.Rect.MakeWH(W, H), paint(tone))
    rng = np.random.default_rng(5)
    for i in range(400):
        c.drawCircle(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(1, 3), paint((200, 180, 150), 0.2))

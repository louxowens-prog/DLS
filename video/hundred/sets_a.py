"""Sets I: the hotel in the storm (and at dawn), the lobby with its 99 keys, Nora's red room, the clock, the bedside.

Each set paints a static layer once (cached), then the light that moves: lightning, rain, lamps, the phone's glow.
"""
import math

import numpy as np
import skia

import draw as D
import figs as F
import kit as K
from draw import H, W, ease, mix, paint, path, ramp

_C = {}


def cached(name, fn):
    if name not in _C:
        _C[name] = fn()
    return _C[name]


def cam(c, z=1.0, cx=540, cy=960, dx=0.0, dy=0.0):
    c.translate(cx + dx, cy + dy)
    c.scale(z, z)
    c.translate(-cx, -cy)


def bright(c, img, k, tint=(0.75, 0.82, 1.0), x=0, y=0):
    """Draw an image again, brightened and cooled (lightning lighting a set), at opacity k."""
    if k <= 0:
        return
    m = [3.2 * tint[0], 0, 0, 0, 0.06, 0, 3.2 * tint[1], 0, 0, 0.06, 0, 0, 3.2 * tint[2], 0, 0.08, 0, 0, 0, 1, 0]
    p = skia.Paint()
    p.setColorFilter(skia.ColorFilters.Matrix(m))
    p.setAlphaf(min(1.0, k))
    c.drawImage(img, x, y, skia.SamplingOptions(skia.FilterMode.kLinear), p)


def img(c, im, x=0, y=0, a=1.0):
    p = skia.Paint()
    p.setAlphaf(a)
    c.drawImage(im, x, y, skia.SamplingOptions(skia.FilterMode.kLinear), p)


# ------------------------------------------------------------------ the hotel

def _arch_window(c, x, y, w, h, glass=(8, 8, 14), frame=(70, 66, 86), lit=None):
    p = skia.Path()
    p.moveTo(x, y + h)
    p.lineTo(x, y + w / 2)
    p.arcTo(skia.Rect.MakeLTRB(x, y, x + w, y + w), 180, 180, False)
    p.lineTo(x + w, y + h)
    p.close()
    c.drawPath(p, paint(frame))
    c.save()
    c.scale(1, 1)
    inner = skia.Path()
    m = 8
    inner.moveTo(x + m, y + h - m)
    inner.lineTo(x + m, y + w / 2)
    inner.arcTo(skia.Rect.MakeLTRB(x + m, y + m, x + w - m, y + w - m), 180, 180, False)
    inner.lineTo(x + w - m, y + h - m)
    inner.close()
    c.drawPath(inner, paint(glass if lit is None else lit))
    c.drawLine(x + w / 2, y + m, x + w / 2, y + h - m, paint(frame, stroke=5))
    c.drawLine(x + m, y + h * 0.55, x + w - m, y + h * 0.55, paint(frame, stroke=5))
    c.restore()
    # an iron balcony, whiplash curls
    by = y + h
    c.drawLine(x - 14, by, x + w + 14, by, paint((20, 18, 26), stroke=6))
    c.drawLine(x - 14, by + 40, x + w + 14, by + 40, paint((20, 18, 26), stroke=5))
    for k in range(4):
        cx = x + w * (k + 0.5) / 4
        c.drawPath(D.smooth([(cx - 12, by + 38), (cx - 14, by + 16), (cx, by + 6), (cx + 10, by + 18), (cx, by + 26)], closed=False),
                   paint((20, 18, 26), stroke=3.5))
    return inner


def _facade(dawn):
    def fn(c):
        stone = (16, 16, 28) if not dawn else (150, 120, 120)
        stone_d = mix(stone, (0, 0, 0), 0.45)
        # the central tower and its dome
        c.drawPath(D.smooth([(370, 330), (380, 220), (430, 150), (540, 92), (650, 150), (700, 220), (710, 330)]), paint(mix(stone, (0, 0, 0), 0.25)))
        c.drawLine(540, 92, 540, 30, paint((20, 18, 26), stroke=8))
        c.drawCircle(540, 30, 12, paint((20, 18, 26)))
        c.drawRect(skia.Rect.MakeLTRB(380, 300, 700, 470), paint(stone))
        # mansard roof
        c.drawPath(path([(60, 470), (120, 320), (960, 320), (1020, 470)]), paint((18, 18, 30) if not dawn else (90, 80, 96)))
        for x in (190, 330, 750, 890):                                 # round dormers
            c.drawCircle(x, 400, 44, paint(stone))
            c.drawCircle(x, 400, 30, paint((8, 8, 14) if not dawn else (120, 130, 170)))
        c.drawRect(skia.Rect.MakeLTRB(30, 470, 1050, 1470), paint(stone))
        c.drawRect(skia.Rect.MakeLTRB(20, 462, 1060, 492), paint(stone_d))           # cornice
        for x in range(30, 1050, 24):
            c.drawRect(skia.Rect.MakeLTRB(x, 492, x + 12, 506), paint(stone_d))
        for y in (690, 910, 1130):                                     # string courses
            c.drawRect(skia.Rect.MakeLTRB(30, y, 1050, y + 14), paint(stone_d))
        win = (8, 8, 14) if not dawn else (150, 160, 200)
        for row, y in enumerate((520, 740, 960)):
            for x in (100, 250, 730, 880):
                lit = None
                _arch_window(c, x, y, 100, 150, glass=win, lit=lit)
        # the great stained-glass window over the door
        K.stained_glass(c, 430, 520, 650, 1060, [K.RED, K.BLUE, K.GREEN, K.GOLD, K.MAGENTA], seed=5, lit=0.55 if not dawn else 0.3)
        # the entrance
        c.drawPath(D.smooth([(400, 1470), (400, 1240), (440, 1180), (540, 1150), (640, 1180), (680, 1240), (680, 1470)], closed=True),
                   paint(stone_d))
        door = D.smooth([(440, 1470), (440, 1260), (470, 1210), (540, 1192), (610, 1210), (640, 1260), (640, 1470)])
        c.drawPath(door, paint((255, 170, 70) if not dawn else (230, 190, 130)))
        c.drawLine(540, 1200, 540, 1470, paint((40, 20, 10), stroke=8))
        for y in (1290, 1380):
            c.drawLine(440, y, 640, y, paint((40, 20, 10), stroke=5))
        for x in (330, 750):                                            # pilasters
            c.drawRect(skia.Rect.MakeLTRB(x - 20, 1150, x + 20, 1470), paint(stone_d))
        # shop windows
        for x0 in (70, 790):
            c.drawRect(skia.Rect.MakeLTRB(x0, 1200, x0 + 220, 1420), paint((10, 10, 16) if not dawn else (130, 140, 170)))
            c.drawRect(skia.Rect.MakeLTRB(x0, 1200, x0 + 220, 1420), paint(stone_d, stroke=10))
        # the iron-and-glass canopy, ribs like stems
        can = D.smooth([(300, 1150), (540, 1080), (780, 1150), (720, 1180), (540, 1150), (360, 1180)])
        c.drawPath(can, paint((120, 200, 200) if not dawn else (210, 220, 230), 0.4))
        for k in range(9):
            u = k / 8
            x = 300 + 480 * u
            c.drawPath(D.smooth([(540, 1240), (lerp(540, x, 0.6), 1180), (x, 1150 - 30 * math.sin(math.pi * u))], closed=False),
                       paint((18, 16, 22), stroke=5))
        # the street
        c.drawRect(skia.Rect.MakeLTRB(0, 1470, W, H), paint((8, 8, 14) if not dawn else (70, 60, 76)))
        c.drawRect(skia.Rect.MakeLTRB(0, 1470, W, 1500), paint((24, 24, 34) if not dawn else (120, 110, 120)))
        for x in (360, 720):                                            # lamp posts
            c.drawLine(x, 1260, x, 1480, paint((16, 14, 20), stroke=10))
    return K.surf(W, H, fn)


def lerp(a, b, k):
    return a + (b - a) * k


def hotel(st, T, z=1.0, cx=540, cy=1100, flashes=(), dawn=0.0, nora=None, taxi=None, ambulance=None, red_window=True, dy=0.0):
    """The hotel. nora: (x, stride) or None; taxi: 0..1 progress of the tail lights leaving; ambulance: dict or None."""
    c = st.c
    fl = K.flash_at(T, flashes)
    # the sky
    if dawn > 0:
        K.vgrad(c, 0, 0, W, 1500, (70, 90, 160), (255, 170, 140))
        K.glow(c, 900, 1350, 900, (255, 200, 120), 0.6)
    else:
        K.vgrad(c, 0, 0, W, 1500, (6, 8, 26), (24, 18, 50))
        K.glow(c, 200, 320, 700, (60, 70, 160), 0.35 + 1.4 * fl)
        for i in range(6):                                              # cloud masses lit from inside by the storm
            K.eglow(c, 100 + i * 200, 250 + (i % 2) * 140, 260, 100, (90, 80, 160), 0.15 + 0.8 * fl)
    if fl > 0.15 and dawn == 0:                                         # the bolts, in the sky above the roofs
        K.bolt(c, 190, 230, 260 + 330 + dy, seed=int(T * 3) % 7, a=fl, w=11)
        if fl > 0.5:
            K.bolt(c, 860, 240, 220 + 300 + dy, seed=int(T * 5) % 9 + 3, a=fl * 0.8, w=5)
    c.save()
    cam(c, z, cx, cy, 0, dy)
    fac = cached("facade%d" % (dawn > 0), lambda: _facade(dawn > 0))
    img(c, fac)
    if dawn == 0:
        bright(c, fac, fl * 0.55)
        # the gel light on the stone: magenta from the left, green from the right, amber at the door
        K.glow(c, -80, 900, 700, K.MAGENTA, 0.35)
        K.glow(c, 1160, 800, 700, (20, 160, 120), 0.3)
        K.glow(c, 540, 1330, 420, K.AMBER, 0.65)
        for x in (360, 720):
            c.drawCircle(x, 1250, 22, paint((255, 220, 150)))
            K.glow(c, x, 1250, 160, K.AMBER, 0.8, core=0.6)
        if red_window:                                                   # her window: red
            c.drawRect(skia.Rect.MakeLTRB(888, 768, 972, 880), paint((255, 30, 40), 0.9))
            K.glow(c, 930, 820, 200, K.RED, 0.7)
        K.dark(c, 540, 1200, 260, 1150, 0.75)
    else:
        K.glow(c, 1080, 900, 900, (255, 190, 120), 0.4)
        K.wash(c, (255, 180, 140), 0.12)
    # reflections on the wet street
    for (x, colr, a) in ((540, K.AMBER, 0.5), (360, K.AMBER, 0.4), (720, K.AMBER, 0.4)) + (((930, K.RED, 0.4),) if dawn == 0 and red_window else ()):
        c.drawRect(skia.Rect.MakeLTRB(x - 26, 1500, x + 26, 1920), paint(shader=D.lin((0, 1500), (0, 1920), [colr + (a,), colr + (0.0,)])))
    if taxi is not None:                                                # tail lights pulling away to the left
        tx = 300 - 700 * taxi
        c.drawPath(D.rrect(tx - 160, 1530, tx + 160, 1650, 30), paint((6, 6, 10)))
        for sx in (-120, 120):
            c.drawRect(skia.Rect.MakeLTRB(tx + sx - 20, 1570, tx + sx + 20, 1590), paint((255, 40, 40)))
            K.glow(c, tx + sx, 1580, 90, K.RED, 0.8, core=0.5)
            c.drawRect(skia.Rect.MakeLTRB(tx + sx - 14, 1650, tx + sx + 14, 1920), paint(shader=D.lin((0, 1650), (0, 1920), [K.RED + (0.5,), K.RED + (0.0,)])))
    if nora is not None:
        nx, ns = nora
        F.woman_p(c, nx, 1478, 0.34, rim=K.AMBER if dawn == 0 else (255, 210, 160), side=1, T=T, stride=ns, rim2=(120, 140, 255) if dawn == 0 else None,
                  halo=0.3, rim_w=6)
        if dawn == 0:                                                   # her suitcase
            c.drawPath(D.rrect(nx + 4, 1400, nx + 56, 1464, 6), paint((10, 8, 12)))
            c.drawPath(D.rrect(nx + 4, 1400, nx + 56, 1464, 6), paint(K.AMBER, 0.5, stroke=2))
    if ambulance is not None:
        _ambulance(c, T, **ambulance)
    c.restore()
    if dawn == 0:
        K.rain(c, T, n=320, a=0.32 + 0.3 * fl, color=(200, 210, 255))
        K.rain(c, T + 3, n=120, a=0.5, slant=0.22, speed=3400, seed=7, length=160)
    return fl


def _ambulance(c, T, x=760, stretcher=0.0):
    """A boxy ambulance at the kerb, its red lights turning; paramedics wheel a stretcher towards it."""
    y = 1560
    c.drawPath(D.rrect(x - 260, y - 300, x + 230, y, 24), paint((236, 232, 228)))
    c.drawPath(D.rrect(x + 150, y - 250, x + 300, y, 24), paint((226, 222, 220)))
    c.drawRect(skia.Rect.MakeLTRB(x + 180, y - 230, x + 280, y - 140), paint((80, 100, 140)))
    c.drawRect(skia.Rect.MakeLTRB(x - 260, y - 150, x + 230, y - 120), paint((200, 30, 40)))
    for wx in (x - 170, x + 200):
        c.drawCircle(wx, y, 50, paint((14, 12, 16)))
        c.drawCircle(wx, y, 22, paint((120, 120, 130)))
    on = (int(T * 4) % 2) == 0
    for k, lx in enumerate((x - 200, x + 160)):
        lit = on if k == 0 else not on
        c.drawPath(D.rrect(lx - 36, y - 330, lx + 36, y - 300, 8), paint((255, 40, 40) if lit else (90, 20, 20)))
        if lit:
            K.glow(c, lx, y - 315, 380, K.RED, 0.75, core=0.7)
    c.drawRect(skia.Rect.MakeLTRB(0, y + 40, W, H), paint(shader=D.lin((0, y + 40), (0, H), [K.RED + (0.25 if on else 0.12,), K.RED + (0.0,)])))
    # the stretcher and the paramedics
    sx = x - 520 + 240 * stretcher
    c.drawRect(skia.Rect.MakeLTRB(sx - 170, y - 110, sx + 170, y - 90), paint((200, 200, 205)))
    for wx in (sx - 140, sx + 140):
        c.drawLine(wx, y - 90, wx, y - 20, paint((60, 60, 66), stroke=6))
        c.drawCircle(wx, y - 14, 10, paint((20, 20, 24)))
    F.figure(c, F.lying_path(T, 1.0), sx + 20, y - 112, 0.3, rim=(255, 200, 150), side=1, rim_w=4, halo=0.2)
    for hx in (sx - 170, sx + 170):                                     # the stretcher's handles
        c.drawLine(hx, y - 100, hx + (-30 if hx < sx else 30), y - 140, paint((180, 180, 186), stroke=6))
    for px, fl in ((sx - 280, False), (sx + 280, True)):
        F.figure(c, F.man_profile_path(T, 0.5 * math.sin(T * 4), push=True), px, y + 30, 0.32, rim=(255, 210, 160), side=1, rim_w=5,
                 halo=0.2, fill=(26, 36, 60), flip=fl)


# ------------------------------------------------------------------ the lobby

def _lobby():
    def fn(c):
        K.vgrad(c, 0, 0, W, 1250, (10, 26, 34), (4, 10, 14))
        for k in range(36):                                             # the great deco sunburst
            a = math.pi + math.pi * (k + 0.5) / 36
            c.drawLine(540, 1000, 540 + 1100 * math.cos(a), 1000 + 1100 * math.sin(a), paint(K.GOLD, 0.22 if k % 2 else 0.4, stroke=6 if k % 2 else 10))
        for r in (380, 520, 660):
            c.drawArc(skia.Rect.MakeLTRB(540 - r, 1000 - r, 540 + r, 1000 + r), 180, 180, False, paint(K.GOLD, 0.45, stroke=8))
        # the key board: 99 hooks, 99 brass tags
        c.drawRect(skia.Rect.MakeLTRB(210, 520, 870, 990), paint((30, 14, 10)))
        c.drawRect(skia.Rect.MakeLTRB(210, 520, 870, 990), paint(K.GOLD, 0.8, stroke=6))
        f = D.font("jost-500", 15)
        n = 1
        for row in range(9):
            for col_ in range(11):
                x, y = 250 + col_ * 58, 556 + row * 50
                c.drawCircle(x, y, 4, paint(K.BRASS_L))
                c.drawLine(x, y, x, y + 10, paint(K.BRASS, stroke=2))
                c.drawPath(D.rrect(x - 17, y + 10, x + 17, y + 34, 5), paint(K.BRASS))
                s = str(n)
                c.drawString(s, x - f.measureText(s) / 2, y + 28, f, paint((50, 28, 8)))
                n += 1
        # columns
        for x0 in (30, 940):
            c.drawRect(skia.Rect.MakeLTRB(x0, 0, x0 + 110, 1500), paint((14, 16, 22)))
            for k in range(4):
                c.drawRect(skia.Rect.MakeLTRB(x0 - 10 * k, 260 + 18 * k, x0 + 110 + 10 * k, 278 + 18 * k), paint(K.GOLD, 0.5))
            for k in range(5):
                c.drawLine(x0 + 18 + k * 18, 340, x0 + 18 + k * 18, 1480, paint((40, 44, 56), stroke=4))
        # the desk: black marble, gold bands
        c.drawRect(skia.Rect.MakeLTRB(110, 1160, 970, 1500), paint((8, 8, 10)))
        c.drawRect(skia.Rect.MakeLTRB(96, 1140, 984, 1172), paint((40, 36, 40)))
        for k in range(3):
            y = 1230 + k * 70
            c.drawRect(skia.Rect.MakeLTRB(110, y, 970, y + 8 + 4 * k), paint(K.GOLD, 0.7))
        for x in range(160, 960, 120):
            c.drawPath(path([(x, 1240), (x + 50, 1300), (x, 1360), (x - 50, 1300)]), paint(K.GOLD, 0.5, stroke=4))
        # the marble floor in perspective
        img_ = K.checker(800, 800, (230, 226, 220), (12, 12, 14), n=8)
        K.draw_quad(c, img_, [(300, 1500), (780, 1500), (1500, 1920), (-420, 1920)])
        # the bell, a ledger
        c.drawPath(D.smooth([(250, 1142), (256, 1100), (290, 1084), (324, 1100), (330, 1142)]), paint(shader=D.lin((250, 1080), (330, 1140), [K.BRASS_L, K.BRASS_D])))
        c.drawCircle(290, 1078, 7, paint(K.BRASS))
        c.drawPath(path([(720, 1144), (900, 1144), (880, 1124), (740, 1124)]), paint((90, 20, 24)))
    return K.surf(W, H, fn)


def lobby(st, T, z=1.0, cx=540, cy=960, key_a=1.0, flashes=()):
    c = st.c
    fl = K.flash_at(T, flashes)
    c.save()
    cam(c, z, cx, cy)
    im = cached("lobby", _lobby)
    img(c, im)
    bright(c, im, fl * 0.3)
    K.glow(c, -120, 800, 900, K.MAGENTA, 0.55)
    K.glow(c, 1200, 800, 900, (40, 120, 255), 0.55)
    K.glow(c, 540, 120, 500, K.AMBER, 0.35)
    K.dark(c, 560, 1000, 420, 1300, 0.5)
    if key_a > 0:
        K.key(c, 640, 1150, 0.62, ang=-8, glint=key_a, T=T)
        K.glow(c, 600, 1150, 220, K.GOLD, 0.25 * key_a)
    c.restore()


# ------------------------------------------------------------------ the red room

def _red_room():
    def fn(c):
        wall = K.tiled(K.whiplash_tile(180, 250, (70, 6, 12), (200, 50, 60), (255, 150, 110)), W, H)
        c.drawImage(wall, 0, 0)
        # the window, with its mullions; the night outside drawn later through it
        c.drawRect(skia.Rect.MakeLTRB(640, 240, 980, 1150), paint((4, 6, 18)))
        # velvet drapes
        for x0, x1 in ((560, 670), (950, 1080)):
            for k in range(8):
                xx = x0 + (x1 - x0) * k / 8
                c.drawRect(skia.Rect.MakeLTRB(xx, 180, xx + (x1 - x0) / 8 + 1, 1300),
                           paint(shader=D.lin((xx, 0), (xx + (x1 - x0) / 8, 0), [(60, 0, 8), (190, 10, 30), (60, 0, 8)])))
        c.drawRect(skia.Rect.MakeLTRB(540, 160, 1080, 210), paint((120, 6, 20)))
        for k in range(10):
            c.drawPath(D.smooth([(540 + k * 54, 205), (567 + k * 54, 240), (594 + k * 54, 205)], closed=False), paint((150, 10, 26), stroke=14))
        # the bed: a nouveau headboard on the left, the long side towards us
        head = D.smooth([(40, 1330), (40, 900), (90, 820), (170, 800), (240, 830), (260, 920), (250, 1330)])
        c.drawPath(head, paint((30, 6, 8)))
        c.drawPath(D.smooth([(80, 1300), (80, 940), (120, 870), (170, 856), (215, 880), (225, 950), (220, 1300)], closed=True), paint((150, 20, 30), 0.45, stroke=6))
        c.drawPath(D.smooth([(170, 870), (130, 960), (190, 1060), (150, 1180)], closed=False), paint((200, 60, 60), 0.4, stroke=5))
        c.drawRect(skia.Rect.MakeLTRB(240, 1240, 1080, 1330), paint((200, 190, 196)))          # the sheet
        c.drawRect(skia.Rect.MakeLTRB(230, 1300, 1080, 1500), paint((110, 0, 20)))            # the coverlet
        for k in range(12):
            x = 260 + k * 70
            c.drawPath(D.smooth([(x, 1310), (x + 20, 1420), (x - 6, 1500)], closed=False), paint((60, 0, 10), 0.6, stroke=6))
        c.drawRect(skia.Rect.MakeLTRB(0, 1500, W, H), paint((24, 4, 8)))
        K.draw_quad(c, K.tiled(K.diamond_tile(160, 160, (40, 4, 10), (120, 20, 36), (200, 120, 60)), 800, 800),
                    [(0, 1500), (1080, 1500), (1500, 1920), (-420, 1920)])
        c.drawPath(D.oval(240, 1196, 420, 1262), paint((220, 214, 220)))   # the pillow
    return K.surf(W, H, fn)


def red_room(st, T, z=1.0, cx=540, cy=960, flashes=(), nora="sit", phone_lit=1.0, head=0.0, hand="phone", pulse=0.0, dx=0.0, dy=0.0,
             key_a=1.0, pale=0.0, pain=0.0, sweat=0.0, screen=None):
    """Nora's room. nora: 'sit' (up in bed, profile facing the window), 'lie', 'empty' or None."""
    c = st.c
    fl = K.flash_at(T, flashes)
    c.save()
    cam(c, z, cx, cy, dx, dy)
    im = cached("redroom", _red_room)
    img(c, im)
    # the night through the window: rain on the glass, the storm
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(640, 240, 980, 1150))
    K.vgrad(c, 640, 240, 980, 1150, mix((8, 12, 40), (200, 210, 255), fl), mix((2, 2, 10), (120, 130, 200), fl))
    if fl > 0.4:
        K.bolt(c, 800, 200, 900, seed=int(T * 2) % 5, a=fl, w=4)
    K.streaks_on_glass(c, T, 640, 240, 980, 1150, a=0.4 + 0.4 * fl)
    c.restore()
    for x in (810,):
        c.drawLine(x, 240, x, 1150, paint((40, 4, 10), stroke=14))
    c.drawLine(640, 700, 980, 700, paint((40, 4, 10), stroke=14))
    c.drawRect(skia.Rect.MakeLTRB(640, 240, 980, 1150), paint((40, 4, 10), stroke=18))
    c.drawRect(skia.Rect.MakeLTRB(620, 1150, 1000, 1176), paint((70, 10, 16)))            # the sill, and the key on it
    if key_a > 0:
        K.key(c, 860, 1138, 0.36, ang=-4, glint=key_a, T=T)
    # the red gel everywhere, the window's blue beam across the floor in a flash
    K.glow(c, 300, 700, 1000, K.RED, 0.45 + 0.25 * pulse)
    K.beam(c, [(640, 300), (980, 300), (700, 1920), (-200, 1920)], (110, 140, 255), 0.06 + 0.5 * fl, p0=(810, 300), p1=(300, 1900))
    if nora == "sit":
        x0, y0 = 380, 1690
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(0, 0, W, 1302))
        F.woman_p(c, x0, y0, 0.78, rim=(120, 160, 255), side=1, T=T, rim2=K.RED, halo=0.25, head=head, hand=hand, rim_w=9)
        c.restore()
        c.drawRect(skia.Rect.MakeLTRB(230, 1300, 1080, 1500), paint((110, 0, 20)))             # the coverlet over her legs
        for k in range(12):
            x = 260 + k * 70
            c.drawPath(D.smooth([(x, 1310), (x + 20, 1420), (x - 6, 1500)], closed=False), paint((60, 0, 10), 0.6, stroke=6))
        if hand == "phone" and phone_lit > 0:
            px, py = x0 + 150 * 0.78, y0 - 640 * 0.78
            K.glow(c, px, py, 260, (150, 200, 255), 0.65 * phone_lit, core=0.5)
    elif nora == "lie":
        F.lying_nora(c, 1130, 1180, 0.8, key=(180, 200, 255), rim=K.RED, eye_k=0.0, T=T, key_a=1.0 - 0.3 * pale, pain=pain, pale=pale,
                     sweat=sweat)
        c.drawPath(D.smooth([(500, 1250), (560, 1150), (680, 1100), (900, 1096), (1080, 1104), (1080, 1500), (500, 1500)]), paint((110, 0, 20)))
        c.drawPath(D.smooth([(560, 1150), (680, 1100), (900, 1096), (1080, 1104)], closed=False), paint((200, 30, 50), 0.5, stroke=6))
        for k in range(7):
            x = 600 + k * 70
            c.drawPath(D.smooth([(x, 1120), (x + 20, 1330), (x - 6, 1500)], closed=False), paint((60, 0, 10), 0.6, stroke=6))
        if phone_lit > 0:
            K.phone(c, 600, 1190, 0.13, -80, screen, glow_col=(150, 200, 255), lit=phone_lit)
            K.glow(c, 600, 1190, 300, (150, 200, 255), 0.5 * phone_lit, core=0.4)
    K.dark(c, 540, 1000, 300, 1250, 0.45)
    c.restore()
    return fl


# ------------------------------------------------------------------ the clock and the bedside

def clock(st, T, hh=2, mm=7, ss=0.0, gel=K.RED, z=1.0, flashes=()):
    """An art-nouveau clock face filling the frame."""
    c = st.c
    fl = K.flash_at(T, flashes)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((20, 2, 6)))
    K.glow(c, 200, 600, 1200, gel, 0.5)
    c.save()
    cam(c, z, 540, 900)
    cx, cy, R = 540, 900, 400
    for k in range(10):                                                 # whiplash flourishes round the case
        a = k * math.pi / 5
        c.drawPath(D.smooth([(cx + (R + 20) * math.cos(a), cy + (R + 20) * math.sin(a)),
                             (cx + (R + 150) * math.cos(a + 0.2), cy + (R + 150) * math.sin(a + 0.2)),
                             (cx + (R + 90) * math.cos(a + 0.45), cy + (R + 90) * math.sin(a + 0.45))], closed=False),
                   paint(K.BRASS_D, stroke=9))
    c.drawCircle(cx, cy, R + 40, paint(shader=D.lin((cx - R, cy - R), (cx + R, cy + R), [K.BRASS_L, K.BRASS, K.BRASS_D])))
    c.drawCircle(cx, cy, R, paint(shader=D.rad((cx - 120, cy - 160), R * 1.4, [(250, 236, 210), (200, 170, 140), (90, 50, 40)])))
    f = D.font("cormorant-700", 70)
    for h in range(1, 13):
        a = math.radians(h * 30 - 90)
        s = ["I", "II", "III", "IIII", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"][h - 1]
        x, y = cx + (R - 80) * math.cos(a), cy + (R - 80) * math.sin(a)
        c.drawString(s, x - f.measureText(s) / 2, y + 24, f, paint((40, 20, 14)))
    for k in range(60):
        a = math.radians(k * 6)
        r0 = R - (26 if k % 5 == 0 else 14)
        c.drawLine(cx + r0 * math.cos(a), cy + r0 * math.sin(a), cx + (R - 6) * math.cos(a), cy + (R - 6) * math.sin(a), paint((40, 20, 14), stroke=4 if k % 5 == 0 else 2))
    ah = math.radians((hh % 12 + mm / 60) * 30 - 90)
    am = math.radians(mm * 6 + ss * 0.1 - 90)
    asec = math.radians(ss * 6 - 90)
    for a, L, w in ((ah, R * 0.5, 20), (am, R * 0.78, 12)):
        c.drawPath(path([(cx + L * math.cos(a), cy + L * math.sin(a)), (cx + w * math.cos(a + 1.57), cy + w * math.sin(a + 1.57)),
                         (cx - 40 * math.cos(a), cy - 40 * math.sin(a)), (cx + w * math.cos(a - 1.57), cy + w * math.sin(a - 1.57))]), paint((14, 8, 8)))
    c.drawLine(cx - 60 * math.cos(asec), cy - 60 * math.sin(asec), cx + R * 0.86 * math.cos(asec), cy + R * 0.86 * math.sin(asec), paint((180, 20, 30), stroke=4))
    c.drawCircle(cx, cy, 18, paint(K.BRASS_D))
    c.restore()
    K.wash(c, gel, 0.18, skia.BlendMode.kMultiply)
    K.glow(c, 900, 300, 800, (120, 150, 255), 1.2 * fl)
    K.dark(c, 540, 900, 380, 1100, 0.6)
    return fl


def bedside(st, T, screen=None, phone_lit=1.0, key_a=1.0, z=1.0, cx=540, cy=1000, gel=K.RED, lamp=0.0, glass=True, phone=True):
    """A close shot of the nightstand: the phone face up, the brass key beside it, a glass of water, the lamp's foot."""
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((14, 2, 6)))
    c.save()
    cam(c, z, cx, cy)
    K.glow(c, 540, 800, 1100, gel, 0.4)
    c.drawPath(path([(-100, 1080), (1180, 1080), (1300, 1920), (-220, 1920)]), paint(shader=D.lin((0, 1080), (0, 1920), [(70, 20, 16), (20, 4, 4)])))
    c.drawPath(path([(-100, 1080), (1180, 1080), (1180, 1100), (-100, 1100)]), paint((120, 50, 30)))
    # the lamp's foot and its glow
    c.drawPath(D.smooth([(80, 1090), (110, 900), (160, 860), (210, 900), (240, 1090)]), paint((40, 16, 8)))
    K.glow(c, 160, 640, 520, K.AMBER, 0.3 + 0.5 * lamp)
    if glass:                                                           # the glass of water
        c.drawPath(D.rrect(830, 860, 960, 1110, 10), paint((180, 200, 255), 0.18))
        c.drawPath(D.rrect(830, 860, 960, 1110, 10), paint((220, 230, 255), 0.5, stroke=3))
        c.drawRect(skia.Rect.MakeLTRB(836, 940, 954, 1104), paint((120, 150, 220), 0.25))
    # the phone, face up, seen in perspective
    if phone:
        c.save()
        c.translate(520, 1330)
        c.scale(1.0, 0.62)
        K.phone(c, 0, 0, 0.8, 4, screen, glow_col=(150, 200, 255), lit=phone_lit)
        c.restore()
    if key_a > 0:
        K.key(c, 800, 1600, 0.75, ang=12, glint=key_a, T=T)
    c.restore()
    K.dark(c, 540, 1200, 350, 1200, 0.5)

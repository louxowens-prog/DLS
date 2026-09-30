"""The sets. The real world is photographed (soft light, true perspective, no ink). The underworld is painted
cardboard on a garage budget: crooked flats that lean, checkerboard floors whose perspective goes wrong, chalk
scribbles, tape on the seams, bare bulbs on cords.

Every set is drawn once per process and cached (backdrop); moving things are drawn by the shots on top.
"""
import math

import numpy as np
import skia

import draw as D
import zkit as Z
from draw import H, INK, W, WHITE, mix, paint, path
from zkit import BLACK, CHALK, DARK, GREY, LIGHT, MID


def bd(st, name, fn, tex=True):
    """A cached backdrop: painted flats get the brush texture; the real world does not."""
    def make():
        s = D.Stage((0, 0, 0))
        fn(s.c)
        if tex:
            D.apply_tex(s.arr, D.brush_tex(W, H, seed=len(name), amp=0.18))
        return D.image(s.arr)
    st.c.drawImage(D.cached("bd_" + name, make), 0, 0)


# ------------------------------------------------------------------ the real world

def kitchen(c, day=False):
    """Mae's kitchen, photographed: a window blown out by daylight, cabinets, a table, the pantry door at the right."""
    wall = (150, 148, 142) if not day else (176, 172, 164)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.lin((0, 0), (0, 1250), [mix(wall, INK, 0.25), wall])))
    c.drawRect(skia.Rect.MakeLTRB(0, 1250, W, H), paint(shader=D.lin((0, 1250), (0, H), [(110, 106, 100), (70, 66, 62)])))
    for k in range(9):                                                  # floor boards in perspective
        c.drawLine(540 + (k - 4) * 60, 1250, 540 + (k - 4) * 300, H, paint((60, 56, 52), 0.5, stroke=3))
    # the window, blown out
    c.drawRect(skia.Rect.MakeLTRB(120, 300, 560, 860), paint((250, 250, 248)))
    c.drawRect(skia.Rect.MakeLTRB(120, 300, 560, 860), paint((80, 76, 70), stroke=24))
    c.drawLine(340, 300, 340, 860, paint((80, 76, 70), stroke=14))
    c.drawLine(120, 580, 560, 580, paint((80, 76, 70), stroke=14))
    c.drawPath(path([(120, 860), (560, 860), (700, 1250), (0, 1250), (0, 1050)]), paint(WHITE, 0.10))   # light on the floor
    for x0 in (600, 780):                                              # wall cabinets
        c.drawRect(skia.Rect.MakeLTRB(x0, 280, x0 + 170, 620), paint(shader=D.lin((x0, 0), (x0 + 170, 0), [(128, 124, 118), (100, 96, 92)])))
        c.drawRect(skia.Rect.MakeLTRB(x0 + 130, 430, x0 + 140, 490), paint((200, 196, 190)))
    c.drawRect(skia.Rect.MakeLTRB(560, 820, W, 860), paint((96, 92, 88)))    # the counter
    c.drawRect(skia.Rect.MakeLTRB(560, 860, W, 1250), paint((116, 112, 106)))
    for x0 in (600, 780, 960):
        c.drawRect(skia.Rect.MakeLTRB(x0 + 6, 900, x0 + 164, 1220), paint((104, 100, 96), stroke=4))
    # a calendar and a clock on the wall
    c.drawRect(skia.Rect.MakeLTRB(620, 660, 740, 800), paint((230, 228, 222)))
    c.drawRect(skia.Rect.MakeLTRB(620, 660, 740, 690), paint((90, 60, 60)))
    c.drawCircle(900, 720, 60, paint((230, 228, 222)))
    c.drawCircle(900, 720, 60, paint((60, 56, 52), stroke=8))


def kitchen_table(c, y=1330):
    c.drawRect(skia.Rect.MakeLTRB(60, y, 1020, y + 40), paint((120, 100, 84)))
    c.drawPath(path([(90, y), (990, y), (1040, y + 40), (40, y + 40)]), paint((140, 118, 98)))
    c.drawRect(skia.Rect.MakeLTRB(120, y + 40, 150, y + 520), paint((90, 74, 62)))
    c.drawRect(skia.Rect.MakeLTRB(930, y + 40, 960, y + 520), paint((90, 74, 62)))


def pantry_door(c, x, y, w, h, open_k=0.0, inside=None):
    """The pantry door, hinged on the left. open_k 0..1; inside(c) paints what is behind it (the dark, the cartoon)."""
    c.drawRect(skia.Rect.MakeLTRB(x - 16, y - 16, x + w + 16, y + h), paint((70, 64, 58)))
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x, y, x + w, y + h))
    c.drawRect(skia.Rect.MakeLTRB(x, y, x + w, y + h), paint((6, 6, 6)))
    if inside is not None:
        inside(c)
    c.restore()
    if open_k < 1:
        ww = w * (1 - open_k)
        skew = 50 * open_k
        door = path([(x, y), (x + ww, y + skew), (x + ww, y + h - skew), (x, y + h)])
        c.drawPath(door, paint(shader=D.lin((x, 0), (x + ww + 1, 0), [(176, 170, 160), (140, 134, 126)])))
        c.drawPath(door, paint((80, 76, 70), stroke=4))
        for k in range(2):
            yy = y + 60 + k * (h / 2)
            c.drawPath(path([(x + ww * 0.14, yy + skew * 0.2), (x + ww * 0.86, yy + skew * 0.6),
                             (x + ww * 0.86, yy + h / 2 - 120 - skew * 0.6), (x + ww * 0.14, yy + h / 2 - 120 - skew * 0.2)]),
                       paint((120, 114, 106), stroke=5))
        c.drawCircle(x + ww * 0.9, y + h / 2, 12, paint((210, 200, 170)))


def bus_day(c):
    """A school bus on a sunny street, for the hand-tinted finale (drawn in colour; the print keeps some of it)."""
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=D.lin((0, 0), (0, 1100), [(120, 180, 240), (200, 230, 250)])))
    c.drawCircle(860, 330, 110, paint((255, 236, 120)))
    for k in range(12):
        a = 2 * math.pi * k / 12
        c.drawLine(860 + 140 * math.cos(a), 330 + 140 * math.sin(a), 860 + 200 * math.cos(a), 330 + 200 * math.sin(a),
                   paint((255, 220, 90), stroke=12))
    for i, (x0, hh, col) in enumerate(((0, 420, (200, 120, 110)), (260, 520, (150, 190, 140)), (620, 380, (230, 200, 150)))):
        c.drawRect(skia.Rect.MakeLTRB(x0, 1100 - hh, x0 + 360, 1100), paint(col))
        for r in range(3):
            for q in range(3):
                c.drawRect(skia.Rect.MakeLTRB(x0 + 40 + q * 110, 1100 - hh + 50 + r * 110, x0 + 110 + q * 110, 1100 - hh + 120 + r * 110),
                           paint((250, 250, 230)))
    c.drawRect(skia.Rect.MakeLTRB(0, 1100, W, H), paint((110, 110, 116)))
    for k in range(6):
        c.drawRect(skia.Rect.MakeLTRB(k * 200, 1500, k * 200 + 110, 1520), paint((250, 240, 180)))


# ------------------------------------------------------------------ the underworld

def _room(c, back, walls, floor_cols=(CHALK, BLACK), vp=(560, 820), lean=-40, scribble="spiral", seed=0, floor_skew=0.6,
          tilt=0.0, floor="checker", door=True, width=640):
    """A crooked painted room: a back flat hung off true (tilt, degrees), two side flats leaning at different angles,
    a crooked doorway painted on the back, and a floor whose perspective goes wrong."""
    c.drawRect(skia.Rect.MakeWH(W, H), paint(BLACK))
    cx, cy = 550 + lean, 770
    a = math.radians(tilt)
    def rot(x, y):
        return (cx + (x - cx) * math.cos(a) - (y - cy) * math.sin(a), cy + (x - cx) * math.sin(a) + (y - cy) * math.cos(a))
    hw = width / 2
    q = [rot(cx - hw, 360 + 30), rot(cx + hw, 350), rot(cx + hw + 20, 1180), rot(cx - hw - 10, 1190)]
    (bx0, by0), (bx1, by1b), (bx2, by2), (bx3, by3) = q
    Z.cardboard(c, [(0, 40), q[0], q[3], (0, 1540)], walls[0], seams=(110,), seed=seed + 2)
    Z.cardboard(c, [q[1], (W, 0), (W, 1640), q[2]], walls[1], seams=(980,), seed=seed + 3)
    Z.scribble(c, 0, 100, min(bx0, bx3), 1500, "zigzag", col=mix(walls[0], WHITE, 0.5), seed=seed + 4, a=0.5)
    Z.scribble(c, max(bx1, bx2), 60, W, 1560, "dots", col=mix(walls[1], WHITE, 0.5), seed=seed + 5, a=0.5, density=0.6)
    Z.cardboard(c, q, back, seams=(cx - 20,), seed=seed)
    c.save()
    c.clipPath(path(q))
    Z.scribble(c, 0, 300, W, 1250, scribble, col=mix(back, WHITE, 0.55), seed=seed + 1, a=0.55)
    c.restore()
    if door:                                                            # a crooked painted doorway, leaning the other way
        d = [rot(cx + hw - 190, 760), rot(cx + hw - 70, 740), rot(cx + hw - 60, 1170), rot(cx + hw - 200, 1180)]
        c.drawPath(path(d), paint(BLACK))
        c.drawPath(path(d), paint(mix(back, WHITE, 0.4), stroke=8))
    fy = max(q[2][1], q[3][1])
    if floor == "checker":
        Z.checker(c, vp, fy, H, q[3][0], q[2][0], -500, W + 420, n_cols=8, n_rows=6, cols=floor_cols, skew=floor_skew)
    elif floor == "rays":                                               # a sunburst floor: painted stripes fanning out
        c.drawPath(path([q[3], q[2], (W + 400, H), (-400, H)]), paint(floor_cols[1]))
        for k in range(14):
            u0, u1 = k / 14, (k + 0.5) / 14
            top = lambda u: (q[3][0] + (q[2][0] - q[3][0]) * u, q[3][1] + (q[2][1] - q[3][1]) * u)
            bot = lambda u: (-400 + (W + 800) * u, H)
            c.drawPath(path([top(u0), top(u1), bot(u1 + 0.02), bot(u0 - 0.02)]), paint(floor_cols[0]))
    elif floor == "spiral":
        Z.checker(c, vp, fy, H, q[3][0], q[2][0], -500, W + 420, n_cols=8, n_rows=6, cols=floor_cols, skew=floor_skew)
        c.save()
        c.translate(540, 1560)
        c.scale(1, 0.32)
        for k in range(9, 0, -1):
            c.drawCircle(0, 0, k * 70, paint(floor_cols[k % 2]))
        c.restore()


def stage(c):
    """The Emcee's stage: painted curtains, a scalloped pelmet, footlights, a checker floor, painted stars."""
    c.drawRect(skia.Rect.MakeWH(W, H), paint(BLACK))
    Z.scribble(c, 0, 0, W, 1300, "stars", col=(200, 198, 190), seed=3, a=0.7)
    for sx in (0, 1):
        x0 = 0 if sx == 0 else 760
        for k in range(6):
            xx = x0 + k * 54
            c.drawPath(path([(xx, 0), (xx + 54, 0), (xx + 48 + 20 * sx, 1350), (xx - 6 + 20 * sx, 1350)]),
                       paint((96, 92, 90) if k % 2 else (130, 126, 122)))
    for k in range(9):
        c.drawCircle(60 + k * 120, 120, 80, paint((150, 146, 140)))
        c.drawCircle(60 + k * 120, 120, 80, paint(BLACK, stroke=6))
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 110), paint((150, 146, 140)))
    Z.checker(c, (540, 900), 1350, H, 160, 920, -400, W + 400, n_cols=9, n_rows=6, skew=-0.4)
    c.drawRect(skia.Rect.MakeLTRB(0, 1320, W, 1356), paint((60, 58, 56)))
    for k in range(10):                                                 # footlights
        c.drawCircle(54 + k * 108, 1338, 16, paint((250, 250, 236)))


def hall(c):
    """The Hall of Pictures: a leaning gallery of light boxes, painted eyes on the walls, a bare bulb."""
    _room(c, (70, 68, 66), ((110, 106, 100), (84, 80, 78)), scribble="eyes", seed=10, lean=-40, tilt=-7, floor_skew=0.9,
          width=560)
    import props as PR
    for (x0, y0, w, h), kind in zip(((40, 420, 150, 200), (40, 700, 150, 200), (900, 380, 150, 200), (900, 700, 150, 200)),
                                    ("xray", "mri", "ct", "retina")):
        c.save()
        c.translate(x0 + w / 2, y0 + h / 2)
        c.rotate(-9 if x0 < 500 else 8)
        PR.picture(c, kind, 0, 0, w - 20, h - 20)
        c.drawRect(skia.Rect.MakeLTRB(-w / 2, -h / 2, w / 2, h / 2), paint(BLACK, stroke=10))
        c.restore()


def library(c):
    """The Library That Never Sleeps: crooked towers of painted books and paper to the flies."""
    _room(c, (60, 58, 56), ((100, 96, 92), (80, 78, 76)), scribble="hatch", seed=20, lean=30, floor_skew=-0.8, tilt=5,
          door=False, width=600)
    rng = np.random.default_rng(21)
    for x0, lean in ((20, 6), (250, -4), (820, 5), (960, -7)):
        y = 1500
        while y > 120:
            h = rng.uniform(28, 60)
            w = rng.uniform(150, 220)
            col = tuple(int(v) for v in rng.uniform(60, 220, 1).repeat(3))
            c.save()
            c.translate(x0 + 90 + lean * (1500 - y) / 100, y)
            c.rotate(rng.uniform(-5, 5))
            c.drawRect(skia.Rect.MakeLTRB(-w / 2, -h, w / 2, 0), paint(col))
            c.drawRect(skia.Rect.MakeLTRB(-w / 2, -h, w / 2, 0), paint(BLACK, stroke=5))
            c.drawLine(-w / 2 + 14, -h / 2, w / 2 - 14, -h / 2, paint(mix(col, WHITE, 0.5), stroke=3))
            c.restore()
            y -= h


def clockroom(c):
    """Ten Years at a Glance: a painted clock face the size of the back wall, calendar flats, a spiral rug."""
    _room(c, (80, 78, 76), ((60, 58, 56), (100, 96, 92)), scribble="zigzag", seed=30, lean=40, tilt=8, floor="spiral",
          floor_skew=-0.6, width=700)
    cx, cy, r = 530, 760, 300
    c.drawCircle(cx, cy, r, paint((226, 222, 212)))
    c.drawCircle(cx, cy, r, paint(BLACK, stroke=14))
    for k in range(12):
        a = 2 * math.pi * k / 12
        c.drawLine(cx + (r - 50) * math.cos(a), cy + (r - 50) * math.sin(a), cx + (r - 14) * math.cos(a), cy + (r - 14) * math.sin(a),
                   paint(BLACK, stroke=12))


def ballroom(c):
    """Before the Symptoms: a ballroom at dawn: a spiky painted sun, crooked columns, alarm-clock chandeliers."""
    _room(c, (110, 108, 104), ((70, 68, 66), (70, 68, 66)), scribble="stars", seed=40, lean=-10, floor_skew=0.2, tilt=-5,
          floor="rays", door=False, width=760)
    cx, cy = 550, 820
    for k in range(16):                                                 # the sun's spikes
        a = 2 * math.pi * k / 16
        c.drawPath(path([(cx + 150 * math.cos(a - 0.12), cy + 150 * math.sin(a - 0.12)), (cx + 330 * math.cos(a), cy + 330 * math.sin(a)),
                         (cx + 150 * math.cos(a + 0.12), cy + 150 * math.sin(a + 0.12))]), paint((232, 228, 214)))
    c.drawCircle(cx, cy, 160, paint((246, 244, 236)))
    c.drawCircle(cx, cy, 160, paint(BLACK, stroke=8))
    for x0 in (170, 900):
        c.drawPath(path([(x0 - 40, 1500), (x0 + 40, 1500), (x0 + 30 + (x0 - 540) * 0.05, 200), (x0 - 30 + (x0 - 540) * 0.05, 200)]),
                   paint((200, 196, 188)))
        for k in range(8):
            c.drawLine(x0 - 30 + k * 9, 1500, x0 - 22 + k * 8 + (x0 - 540) * 0.05, 200, paint((150, 146, 140), stroke=3))


def clinic(c):
    """The procedure room, painted: tiles scribbled on a leaning wall, a cardboard monitor on a pole."""
    _room(c, (150, 150, 148), ((120, 120, 118), (100, 100, 98)), floor_cols=((200, 200, 198), (120, 120, 118)), scribble="dots",
          seed=50, lean=10, floor_skew=0.3, tilt=4, door=False)
    for x in range(260, 900, 60):
        c.drawLine(x, 380, x + 6, 1180, paint((120, 120, 118), 0.6, stroke=3))
    for y in range(420, 1180, 60):
        c.drawLine(240, y, 890, y - 8, paint((120, 120, 118), 0.6, stroke=3))


def tunnel(c, T, u, lesion=True, flag=0.0, tint=None, reveal=1.0):
    """The inside, painted as a carnival tunnel ride: ribbed arches (the folds) receding to a lamp-lit vanishing point.
    u moves us forward. lesion: a small flat growth tucked in a fold (right of centre). flag: the AI's box around it."""
    c.drawRect(skia.Rect.MakeWH(W, H), paint((14, 12, 12)))
    cx, cy = 540 + 40 * math.sin(T * 0.7), 900 + 30 * math.cos(T * 0.5)
    n = 10
    ph = u % 2.0
    for i in range(1, n + 3):                                            # near (big) first, far (small) painted over it
        z = (i - (u % 1.0)) / n                                          # 0 near .. 1 far
        if z <= 0:
            continue
        r = 1100 * (1 - min(z, 0.999)) ** 2.2 + 36
        band = (i + int(u)) % 2                                          # painted folds: light and dark bands, like a ride
        lit = (1 - min(z, 1.0)) ** 0.7
        tone = int((70 + 140 * lit) if band else (26 + 60 * lit))
        wob = [(cx + r * 1.05 * math.cos(a) + 16 * math.sin(a * 3 + i), cy + r * 1.25 * math.sin(a) + 12 * math.cos(a * 4 + i))
               for a in np.linspace(0, 2 * math.pi, 22, endpoint=False)]
        c.drawPath(D.smooth(wob), paint((tone, tone - 4, tone - 6)))
        c.drawPath(D.smooth(wob), paint((8, 8, 8), stroke=6 + 14 * lit))
        hl = wob[13:19]                                                   # a wet highlight on the upper left of each fold
        c.drawPath(D.smooth(hl, closed=False), paint(WHITE, 0.2 + 0.5 * lit, stroke=3 + 7 * lit))
    c.drawCircle(cx, cy, 60, paint((4, 4, 4)))
    if lesion:
        lx, ly = cx + 250, cy + 170
        rim = mix((150, 146, 142), (236, 232, 226), reveal)                # barely there until the box is drawn
        c.drawOval(skia.Rect.MakeLTRB(lx - 78, ly - 30, lx + 78, ly + 34), paint(rim, 0.35 + 0.65 * reveal))
        c.drawOval(skia.Rect.MakeLTRB(lx - 62, ly - 20, lx + 58, ly + 22), paint(mix((130, 124, 120), (96, 88, 86), reveal)))
        for k in range(9):
            c.drawCircle(lx - 46 + k * 11, ly + 3 * math.sin(k * 1.7), 5, paint((150, 140, 138), 0.3 + 0.7 * reveal))
        if flag > 0:
            k = D.ease(flag)
            m = 150 - 60 * k
            box = skia.Rect.MakeLTRB(lx - m, ly - m * 0.7, lx + m, ly + m * 0.7)
            c.drawRect(box, paint(WHITE, k, stroke=10))
            Z.tinted(tint, c, lambda t: t.drawRect(box, paint((40, 230, 90), k, stroke=26)))
            return (lx, ly)
    return None

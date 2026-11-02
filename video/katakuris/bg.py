"""Painted backdrops, flat and over-lit (cached): the meadow and the guesthouse, the lobby, the garden at night,
the dream sky, the rainy apartment, the enka stage, the storm, the maps' tabletop."""
import math

import numpy as np
import skia

import kk
from kk import (BLOOD, CLOUD, CREAM, GRASS, GRASS2, GRASS3, HOT, INK, LEMON, LILAC, MINT, ORANGE, PINK, SKY, SKY2, WHITE,
                W, H, lin, mix, paint, path, rad, smooth)


def _paint(fn):
    st = kk.Stage()
    fn(st.c)
    return kk.image(st.arr)


def cloud(c, x, y, s, color=CLOUD, a=1.0):
    """A flat painted cumulus: overlapping discs with a pale blue underside."""
    for dx, dy, r in ((-90, 10, 55), (-35, -25, 75), (40, -15, 70), (95, 15, 50), (0, 20, 60)):
        c.drawCircle(x + dx * s, y + dy * s + 8 * s, r * s, paint(mix(color, SKY, 0.25), a))
    for dx, dy, r in ((-90, 10, 55), (-35, -25, 75), (40, -15, 70), (95, 15, 50), (0, 20, 60)):
        c.drawCircle(x + dx * s, y + dy * s, r * s, paint(color, a))


def volcano(c, x, y, s, smoke=True, glow=0.0):
    """The looming volcano: a lopsided cone with a snow-streaked, smoking crater."""
    c.drawPath(path([(x - 520 * s, y), (x - 90 * s, y - 520 * s), (x + 70 * s, y - 530 * s), (x + 560 * s, y)]),
               paint(shader=lin((x, y - 530 * s), (x, y), [(120, 100, 120), (80, 70, 95)])))
    c.drawPath(path([(x - 90 * s, y - 520 * s), (x + 70 * s, y - 530 * s), (x + 120 * s, y - 440 * s), (x + 40 * s, y - 470 * s),
                     (x - 20 * s, y - 430 * s), (x - 150 * s, y - 450 * s)]), paint((245, 245, 255)))
    if glow > 0:
        c.drawCircle(x - 10 * s, y - 530 * s, 160 * s, paint(shader=rad((x - 10 * s, y - 530 * s), 160 * s, [(255, 120, 40, glow), (255, 60, 20, 0)])))
    if smoke:
        for i in range(6):
            c.drawCircle(x - 10 * s + i * 30 * s, y - (580 + i * 70) * s, (45 + i * 16) * s, paint((235, 235, 240), 0.9 - i * 0.1))


def rainbow(c, x, y, r, w=26, a=0.9):
    for i, cc in enumerate(((255, 40, 60), (255, 140, 20), (255, 236, 50), (70, 215, 60), (40, 150, 255), (150, 70, 230))):
        rr = r - i * w
        c.drawArc(skia.Rect.MakeLTRB(x - rr, y - rr, x + rr, y + rr), 180, 180, False, paint(cc, a, stroke=w, cap="butt"))


def hills(c, y, colors=(GRASS3, GRASS, GRASS2), seed=0):
    rng = np.random.default_rng(seed)
    for k, cc in enumerate(colors):
        pts = [(0, H)]
        base = y + k * 120
        for i in range(9):
            pts.append((i * W / 8, base + rng.uniform(-60, 40)))
        pts.append((W, H))
        c.drawPath(smooth(pts[1:-1] + [(W, H), (0, H)]), paint(cc))


def flowers(c, y0, y1, n=120, seed=1):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        x, y = rng.uniform(0, W), rng.uniform(y0, y1)
        cc = [(255, 255, 255), LEMON, (255, 110, 180), (255, 80, 60)][rng.integers(0, 4)]
        r = 4 + 8 * (y - y0) / (y1 - y0)
        for k in range(5):
            a = k * 2 * math.pi / 5
            c.drawCircle(x + r * math.cos(a), y + r * math.sin(a), r * 0.7, paint(cc))
        c.drawCircle(x, y, r * 0.5, paint(ORANGE))


def sky(c, top=SKY, bot=SKY2, h=1100):
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, h), paint(shader=lin((0, 0), (0, h), [top, bot])))


def meadow(seed=0, rainbow_=True):
    """Garish green meadows under a huge blue sky; the volcano looms; a rainbow."""
    def f(c):
        sky(c)
        cloud(c, 240, 330, 1.3)
        cloud(c, 820, 500, 1.0)
        cloud(c, 560, 200, 0.7)
        volcano(c, 760, 1010, 1.05)
        if rainbow_:
            rainbow(c, 330, 1000, 520, 24, 0.75)
        c.drawPath(path([(0, 1000), (260, 820), (520, 1000)]), paint((90, 110, 160)))
        hills(c, 960, seed=seed)
        flowers(c, 1150, 1900, 160, seed + 1)
    return kk.cached(f"meadow{seed}{rainbow_}", lambda: _paint(f))


def inn(c, x, y, s, lit=False):
    """The guesthouse: two storeys of cream plaster and dark timber, a red roof, window boxes and a hand-painted sign."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawRect(skia.Rect.MakeLTRB(-330, -420, 330, 0), paint((255, 244, 220)))
    for bx in (-330, -110, 110, 330):
        c.drawRect(skia.Rect.MakeLTRB(bx - 10, -420, bx + 10, 0), paint((110, 60, 40)))
    c.drawRect(skia.Rect.MakeLTRB(-340, -225, 340, -205), paint((110, 60, 40)))
    c.drawPath(path([(-400, -410), (0, -640), (400, -410)]), paint((220, 40, 50)))
    c.drawPath(path([(-400, -410), (0, -640), (400, -410)]), paint((150, 20, 30), stroke=10))
    for wx in (-220, 0, 220):
        for wy in (-360, -150):
            c.drawRect(skia.Rect.MakeLTRB(wx - 55, wy - 50, wx + 55, wy + 40), paint((255, 230, 120) if lit else (120, 190, 255)))
            c.drawRect(skia.Rect.MakeLTRB(wx - 55, wy - 50, wx + 55, wy + 40), paint((110, 60, 40), stroke=8))
            c.drawLine(wx, wy - 50, wx, wy + 40, paint((110, 60, 40), stroke=5))
            c.drawRect(skia.Rect.MakeLTRB(wx - 62, wy + 40, wx + 62, wy + 62), paint((170, 100, 60)))
            for k in range(5):
                c.drawCircle(wx - 48 + k * 24, wy + 38, 12, paint([(255, 60, 120), LEMON, (255, 120, 200)][k % 3]))
    c.drawRect(skia.Rect.MakeLTRB(-60, -150, 60, 0), paint((140, 80, 50)))
    c.drawCircle(40, -70, 8, paint(LEMON))
    c.restore()


def inn_sign(c, x, y, s=1.0, t=0.0, tag="sign"):
    """The hand-painted sign on two posts."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    for px in (-230, 230):
        c.drawRect(skia.Rect.MakeLTRB(px - 12, -40, px + 12, 200), paint((110, 60, 40)))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-280, -160, 280, 40), 24, 24), paint((255, 250, 235)))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-280, -160, 280, 40), 24, 24), paint((110, 60, 40), stroke=10))
    kk.text(c, "MOUNTAIN VIEW INN", 0, -85, 42, "mochiy-400", (220, 40, 50), tag=tag)
    kk.text(c, "claims processed ♥ hot baths", 0, -12, 32, "rounded-800", (110, 60, 40), tag=tag)
    c.restore()


def inn_meadow(seed=0):
    def f(c):
        c.drawImage(meadow(seed, rainbow_=False), 0, 0)
        inn(c, 540, 1180, 1.0)
        c.drawRect(skia.Rect.MakeLTRB(0, 1180, W, 1200), paint((60, 170, 50)))
        for i in range(12):                                            # a white picket fence
            fx = 40 + i * 92
            c.drawPath(path([(fx, 1300), (fx, 1215), (fx + 14, 1195), (fx + 28, 1215), (fx + 28, 1300)]), paint(WHITE))
        c.drawRect(skia.Rect.MakeLTRB(0, 1240, W, 1256), paint(WHITE))
    return kk.cached(f"innmeadow{seed}", lambda: _paint(f))


def lobby():
    """The guesthouse lobby: striped wallpaper, a window onto the meadow and the volcano, the reception desk."""
    def f(c):
        c.drawRect(skia.Rect.MakeWH(W, H), paint((255, 225, 170)))
        for x in range(0, W, 90):
            c.drawRect(skia.Rect.MakeLTRB(x, 0, x + 45, 1250), paint((255, 205, 150)))
        c.drawRect(skia.Rect.MakeLTRB(90, 230, 560, 760), paint(SKY))
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(90, 230, 560, 760))
        c.drawRect(skia.Rect.MakeLTRB(90, 230, 560, 760), paint(shader=lin((0, 230), (0, 760), [SKY, SKY2])))
        volcano(c, 360, 760, 0.5)
        c.drawRect(skia.Rect.MakeLTRB(90, 680, 560, 760), paint(GRASS))
        cloud(c, 190, 330, 0.5)
        c.restore()
        c.drawRect(skia.Rect.MakeLTRB(90, 230, 560, 760), paint((120, 70, 40), stroke=22))
        c.drawLine(325, 230, 325, 760, paint((120, 70, 40), stroke=12))
        c.drawCircle(820, 400, 90, paint(WHITE))                         # a wall clock
        c.drawCircle(820, 400, 90, paint((120, 70, 40), stroke=14))
        c.drawRect(skia.Rect.MakeLTRB(0, 1250, W, H), paint((170, 110, 70)))
        for y in range(1280, H, 70):
            c.drawLine(0, y, W, y, paint((140, 90, 55), stroke=4))
    return kk.cached("lobby", lambda: _paint(f))


def desk(c, y=1250):
    """The reception desk, drawn in front of whoever stands behind it."""
    c.drawRect(skia.Rect.MakeLTRB(60, y + 30, 1020, y + 420), paint((150, 80, 45)))
    c.drawRect(skia.Rect.MakeLTRB(40, y, 1040, y + 50), paint((190, 110, 60)))
    c.drawRect(skia.Rect.MakeLTRB(60, y + 50, 1020, y + 70), paint((110, 60, 35)))
    for x in (200, 540, 880):
        c.drawRect(skia.Rect.MakeLTRB(x - 110, y + 120, x + 110, y + 360), paint((130, 70, 40), stroke=8))


def garden_night():
    """The back garden at night, under a fat moon, the volcano glowing, the inn's windows lit."""
    def f(c):
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 1100), paint(shader=lin((0, 0), (0, 1100), [(20, 10, 60), (90, 40, 140)])))
        rng = np.random.default_rng(5)
        for _ in range(90):
            c.drawCircle(rng.uniform(0, W), rng.uniform(0, 800), rng.uniform(1, 3), paint(WHITE, rng.uniform(0.4, 1)))
        c.drawCircle(820, 300, 110, paint((255, 250, 210)))
        c.drawCircle(820, 300, 190, paint(shader=rad((820, 300), 190, [(255, 250, 210, 0.35), (255, 250, 210, 0.0)])))
        volcano(c, 330, 1000, 0.8, glow=0.8)
        inn(c, 900, 1060, 0.6, lit=True)
        hills(c, 1000, colors=((40, 110, 60), (25, 90, 45), (15, 70, 35)), seed=3)
    return kk.cached("gardennight", lambda: _paint(f))


def dream():
    """The dream sky: candy-floss clouds on pink and lilac, floating hearts."""
    def f(c):
        c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=lin((0, 0), (0, H), [(255, 150, 220), (200, 160, 255), (150, 220, 255)])))
        rng = np.random.default_rng(9)
        for i in range(9):
            cloud(c, rng.uniform(0, W), rng.uniform(150, 1800), rng.uniform(0.8, 1.6), (255, 240, 250), 0.9)
        rainbow(c, 540, 1500, 700, 30, 0.6)
    return kk.cached("dream", lambda: _paint(f))


def apartment():
    """A small grey apartment in the rain: the enka ballad's world."""
    def f(c):
        c.drawRect(skia.Rect.MakeWH(W, H), paint((120, 120, 150)))
        c.drawRect(skia.Rect.MakeLTRB(140, 250, 940, 900), paint(shader=lin((0, 250), (0, 900), [(50, 60, 90), (90, 100, 130)])))
        for x in range(160, 940, 90):
            c.drawRect(skia.Rect.MakeLTRB(x, 700, x + 60, 900), paint((40, 45, 70)))
        c.drawRect(skia.Rect.MakeLTRB(140, 250, 940, 900), paint((200, 200, 210), stroke=24))
        c.drawLine(540, 250, 540, 900, paint((200, 200, 210), stroke=14))
        c.drawRect(skia.Rect.MakeLTRB(0, 1300, W, H), paint((90, 80, 90)))
        for y in range(1320, H, 64):                                                     # floorboards
            c.drawLine(0, y, W, y, paint((70, 62, 72), stroke=4))
        c.drawOval(skia.Rect.MakeLTRB(60, 1360, 1020, 1780), paint((130, 40, 60)))        # a worn rug
        c.drawOval(skia.Rect.MakeLTRB(120, 1400, 960, 1740), paint((200, 150, 90), stroke=14))
        c.drawOval(skia.Rect.MakeLTRB(220, 1460, 860, 1680), paint((90, 30, 50), stroke=10))
        c.drawRect(skia.Rect.MakeLTRB(100, 1150, 980, 1210), paint((150, 110, 80)))      # a table
        c.drawRect(skia.Rect.MakeLTRB(140, 1210, 180, 1500), paint((120, 85, 60)))
        c.drawRect(skia.Rect.MakeLTRB(900, 1210, 940, 1500), paint((120, 85, 60)))
    return kk.cached("apartment", lambda: _paint(f))


def enka_stage():
    """The enka stage: a painted backdrop of crashing waves under a red sun, footlights, dry-ice fog."""
    def f(c):
        c.drawRect(skia.Rect.MakeWH(W, H), paint((25, 20, 50)))
        c.drawRect(skia.Rect.MakeLTRB(0, 200, W, 1300), paint(shader=lin((0, 200), (0, 1300), [(255, 150, 60), (255, 90, 90), (120, 40, 110)])))
        c.drawCircle(540, 560, 200, paint((230, 20, 40)))
        for row in range(4):                                            # stylised waves
            y = 900 + row * 110
            for i in range(-1, 8):
                x = i * 170 + (row % 2) * 85
                c.drawCircle(x, y, 110, paint((30, 70, 160)))
                c.drawArc(skia.Rect.MakeLTRB(x - 110, y - 110, x + 110, y + 110), 200, 140, False, paint(WHITE, stroke=12))
                for k in range(4):
                    c.drawCircle(x + 70 + k * 12, y - 90 + k * 10, 8, paint(WHITE))
        c.drawRect(skia.Rect.MakeLTRB(0, 1300, W, H), paint((70, 30, 40)))
        for i in range(8):
            c.drawCircle(70 + i * 135, 1330, 22, paint(LEMON))
    return kk.cached("enka", lambda: _paint(f))


def storm():
    """The disaster sky: bruised purple and orange, the ground a dark green."""
    def f(c):
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 1250), paint(shader=lin((0, 0), (0, 1250), [(40, 10, 60), (140, 40, 110), (255, 110, 60)])))
        rng = np.random.default_rng(12)
        for i in range(8):
            cloud(c, rng.uniform(0, W), rng.uniform(150, 700), rng.uniform(1.0, 1.8), (80, 50, 110), 0.95)
        c.drawRect(skia.Rect.MakeLTRB(0, 1250, W, H), paint((30, 70, 40)))
        rng2 = np.random.default_rng(13)
        for k, cc in enumerate(((45, 95, 55), (38, 82, 48), (28, 64, 38))):     # lumpy clay-green ground, not a flat slab
            pts = [(0, H)] + [(i * W / 7, 1250 + k * 170 + rng2.uniform(-40, 50)) for i in range(8)] + [(W, H)]
            c.drawPath(smooth(pts[1:-1] + [(W, H), (0, H)]), paint(cc))
        for _ in range(700):                                                   # brushy grass strokes
            x, y = rng2.uniform(0, W), rng2.uniform(1260, H)
            L = rng2.uniform(20, 60)
            cc = tuple(int(np.clip(v + rng2.normal(0, 14), 0, 255)) for v in (50, 100, 60))
            c.drawLine(x, y, x + L * 0.2, y - L, paint(cc, 0.3, stroke=rng2.uniform(3, 8)))
        for i in range(26):                                                    # clay pebbles and tufts
            x, y = rng2.uniform(0, W), rng2.uniform(1300, 1880)
            r = rng2.uniform(10, 26)
            c.drawOval(skia.Rect.MakeLTRB(x - r, y - r * 0.6, x + r, y + r * 0.6), paint((70, 70, 80)))
            c.drawOval(skia.Rect.MakeLTRB(x - r * 0.6, y - r * 0.5, x + r * 0.2, y - r * 0.1), paint((120, 120, 130)))
    return kk.cached("storm", lambda: _paint(f))


def dark_table():
    """A dark craft table under a single hard spotlight: the horror palette for the clay records."""
    def f(c):
        c.drawRect(skia.Rect.MakeWH(W, H), paint((34, 20, 44)))
        rng = np.random.default_rng(6)
        for _ in range(700):
            x, y = rng.uniform(0, W), rng.uniform(0, H)
            c.drawLine(x, y, x + rng.uniform(30, 120), y + rng.uniform(-3, 3), paint((60, 36, 70), 0.35, stroke=3))
        c.drawOval(skia.Rect.MakeLTRB(-100, 250, 1180, 1500), paint(shader=rad((540, 870), 700, [(255, 220, 170, 0.28), (255, 200, 150, 0.0)])))
    return kk.cached("darktable", lambda: _paint(f))


def tabletop(color=(250, 225, 140)):
    """A plain craft-table surface for the clay maps and numbers."""
    def f(c):
        c.drawRect(skia.Rect.MakeWH(W, H), paint(color))
        rng = np.random.default_rng(4)
        for _ in range(900):
            x, y = rng.uniform(0, W), rng.uniform(0, H)
            c.drawLine(x, y, x + rng.uniform(30, 120), y + rng.uniform(-3, 3), paint(mix(color, (150, 110, 60), 0.3), 0.25, stroke=3))
    return kk.cached(f"table{color}", lambda: _paint(f))


def studio(t=0.0):
    """Not cached: the variety-show starburst."""
    st = kk.Stage()
    kk.starburst(st.c, W / 2, 760, t)
    return st.arr

"""THE WRONG ANSWERS, a basement sock-puppet troupe (all original): Marge (a tall clown: white face, blue diamond eyes,
a traffic-cone hat, a giant yellow bow tie, a cardboard tutu), Gus (a jester in orange and teal with a belled
purple-and-gold hat), Pixel (in a cardboard-box robot suit, dryer-hose arms) and Lou (striped shirt, red beret,
a gold glitter beard)."""
import math

import numpy as np
import skia

import diy as K
import dot as D
from diy import GOLD, HOT, INK, PURPLE, WHITE, bez, lin, mix, paint, path, rad, smooth

SKINS = {"marge": (246, 244, 240), "gus": (226, 168, 132), "pixel": (180, 120, 90), "lou": (240, 196, 160)}


def _arms(c, sh, T, wave, side_cols, seed, w=40):
    for sx in (-1, 1):
        ph = T * 7 + seed + (0 if sx < 0 else 1.5)
        if wave > 0:
            a1 = 150 + 18 * math.sin(ph) * wave
            a2 = 20 + 15 * math.sin(ph * 1.3)
        else:
            a1, a2 = 14, 10
        r1 = math.radians(a1) * sx
        ex, ey = sh[0] * sx + 170 * math.sin(r1), sh[1] + 170 * math.cos(r1)
        r2 = r1 + math.radians(a2) * sx
        wx, wy = ex + 150 * math.sin(r2), ey + 150 * math.cos(r2)
        c.drawPath(path([(sh[0] * sx, sh[1]), (ex, ey), (wx, wy)], closed=False), paint(side_cols[0 if sx < 0 else 1], stroke=w))
        c.drawCircle(wx, wy, w * 0.55, paint((255, 255, 255) if seed == 1 else (236, 190, 160)))


def _face(c, T, y, skin, mood="smile", talk=0.0, seed=0, eye_col=(40, 30, 30)):
    for sx in (-1, 1):
        c.drawOval(skia.Rect.MakeXYWH(sx * 34 - 11, y - 14, 22, 28), paint(WHITE))
        c.drawCircle(sx * 34 + math.sin(T + seed) * 3, y + 2, 8, paint(eye_col))
    if mood == "laugh" or talk > 0.2:
        c.drawPath(path(np.vstack([bez((-40, y + 46), (0, y + 100), (40, y + 46), 12), bez((40, y + 46), (0, y + 56), (-40, y + 46), 12)])),
                   paint((140, 20, 40)))
    elif mood == "still":
        c.drawLine(-22, y + 56, 22, y + 56, paint((140, 60, 60), stroke=6))
    else:
        c.drawPath(path(bez((-34, y + 48), (0, y + 74), (34, y + 48), 12), closed=False), paint((150, 40, 60), stroke=7))


def member(c, who, x, y, s, T, wave=0.0, mood="smile", seed=0):
    """A troupe member, feet at (x, y), ~1500 units tall at s = 1."""
    bob = abs(math.sin(T * 6 + seed)) * 14 * (1 if mood == "laugh" else 0.3 if wave else 0)
    c.save()
    c.translate(x, y - bob)
    c.scale(s, s)
    c.translate(0, -1440)
    if who == "marge":
        for sx in (-1, 1):
            c.drawRect(skia.Rect.MakeLTRB(sx * 60 - 30, 760, sx * 60 + 30, 1400), paint((250, 250, 250)))
            for k in range(8):
                c.drawRect(skia.Rect.MakeLTRB(sx * 60 - 30, 780 + k * 80, sx * 60 + 30, 820 + k * 80), paint((230, 30, 60)))
            c.drawOval(skia.Rect.MakeLTRB(sx * 60 - 70, 1380, sx * 60 + 60, 1440), paint((40, 200, 90)))
        c.drawPath(smooth([(-150, 230), (150, 230), (170, 700), (-170, 700)]), paint((80, 200, 255)))
        tut = [(-260, 760), (-130, 640), (0, 690), (130, 640), (260, 760), (180, 820), (0, 790), (-180, 820)]
        c.drawPath(path(tut), paint((196, 156, 106)))
        for k in range(6):
            c.drawLine(-220 + k * 90, 700, -200 + k * 90, 800, paint((200, 200, 210), 0.9, stroke=14))       # duct tape
        _arms(c, (150, 260), T, wave, ((80, 200, 255), (80, 200, 255)), 1)
        c.drawCircle(0, 60, 120, paint(SKINS["marge"]))
        for sx in (-1, 1):
            c.drawPath(path([(sx * 34, 0), (sx * 34 + 18, 40), (sx * 34, 90), (sx * 34 - 18, 40)]), paint((40, 110, 255)))
        _face(c, T, 50, SKINS["marge"], mood, seed=seed)
        c.drawCircle(0, 88, 22, paint((255, 40, 60)))
        c.drawPath(path([(-110, -20), (110, -20), (20, -300), (-20, -300)]), paint((255, 120, 20)))                # the cone
        c.drawRect(skia.Rect.MakeLTRB(-82, -120, 82, -80), paint(WHITE))
        c.drawPath(path([(-150, 200), (0, 230), (150, 200), (150, 300), (0, 250), (-150, 300)]), paint(GOLD))
    elif who == "gus":
        for sx in (-1, 1):
            c.drawRect(skia.Rect.MakeLTRB(sx * 60 - 34, 700, sx * 60 + 34, 1400), paint((255, 140, 30) if sx < 0 else (20, 170, 170)))
            c.drawPath(path([(sx * 60 - 40, 1390), (sx * 60 + 40, 1390), (sx * 60 + sx * 110, 1350), (sx * 60 + sx * 60, 1440), (sx * 60 - 40, 1440)]),
                       paint((140, 60, 200)))
        c.drawPath(path([(-150, 240), (0, 240), (0, 720), (-160, 720)]), paint((20, 170, 170)))
        c.drawPath(path([(0, 240), (150, 240), (160, 720), (0, 720)]), paint((255, 140, 30)))
        for k in range(5):
            c.drawPath(path([(-160 + k * 64, 720), (-128 + k * 64, 790), (-96 + k * 64, 720)]), paint((140, 60, 200)))
        _arms(c, (150, 270), T, wave, ((255, 140, 30), (20, 170, 170)), 2)
        c.drawCircle(0, 80, 110, paint(SKINS["gus"]))
        for sx in (-1, 1):
            c.drawCircle(sx * 60, 120, 26, paint((255, 80, 90), 0.7))
        _face(c, T, 70, SKINS["gus"], mood, seed=seed)
        for k, (ang, col) in enumerate(((-50, (140, 60, 200)), (0, GOLD), (50, (140, 60, 200)))):
            c.save()
            c.translate(0, -10)
            c.rotate(ang)
            c.drawPath(path([(-50, 0), (50, 0), (20, -200), (0, -230)]), paint(col))
            c.drawCircle(0, -236, 18, paint(GOLD if col != GOLD else (140, 60, 200)))
            c.restore()
    elif who == "pixel":
        for sx in (-1, 1):
            c.drawRect(skia.Rect.MakeLTRB(sx * 60 - 32, 760, sx * 60 + 32, 1400), paint((60, 60, 70)))
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(sx * 60 - 50, 1380, sx * 60 + 50, 1440), 14, 14), paint((40, 40, 40)))
        c.drawRect(skia.Rect.MakeLTRB(-180, 260, 180, 780), paint((196, 156, 106)))                               # the box
        c.drawRect(skia.Rect.MakeLTRB(-180, 260, 180, 780), paint((150, 110, 70), stroke=6))
        for k, col in enumerate(((255, 40, 60), (40, 200, 90), (40, 110, 255))):
            c.drawCircle(-90 + k * 90, 420, 30, paint(col))
        K.text(c, "ROBOT", 0, 620, 70, "permanent-marker-400", (40, 40, 60), tag="deco")
        _arms(c, (180, 300), T, wave, ((190, 190, 200), (190, 190, 200)), 3, w=46)
        c.drawRect(skia.Rect.MakeLTRB(-150, -150, 150, 230), paint((196, 156, 106)))                              # box head
        c.drawRect(skia.Rect.MakeLTRB(-150, -150, 150, 230), paint((150, 110, 70), stroke=6))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-100, -60, 100, 150), 30, 30), paint(SKINS["pixel"]))
        _face(c, T, 20, SKINS["pixel"], mood, seed=seed)
        c.drawLine(0, -150, 0, -230, paint((190, 190, 200), stroke=8))
        c.drawCircle(0, -240, 20, paint((255, 40, 60) if int(T * 3) % 2 else (255, 200, 200)))
    else:                                                               # lou
        for sx in (-1, 1):
            c.drawRect(skia.Rect.MakeLTRB(sx * 60 - 34, 700, sx * 60 + 34, 1400), paint((30, 30, 36)))
            c.drawOval(skia.Rect.MakeLTRB(sx * 60 - 60, 1390, sx * 60 + 50, 1440), paint((20, 20, 20)))
        body = smooth([(-150, 240), (150, 240), (150, 720), (-150, 720)])
        c.drawPath(body, paint(WHITE))
        c.save()
        c.clipPath(body, doAntiAlias=True)
        for k in range(9):
            c.drawRect(skia.Rect.MakeLTRB(-160, 260 + k * 56, 160, 288 + k * 56), paint((30, 30, 36)))
        c.restore()
        for sx in (-1, 1):
            c.drawLine(sx * 70, 240, sx * 70, 720, paint((230, 30, 60), stroke=16))
        _arms(c, (150, 270), T, wave, ((240, 240, 240), (240, 240, 240)), 4)
        c.drawCircle(0, 80, 110, paint(SKINS["lou"]))
        _face(c, T, 50, SKINS["lou"], mood, seed=seed)
        c.drawPath(smooth([(-100, 110), (100, 110), (80, 230), (0, 270), (-80, 230)]), paint(GOLD))                   # glitter beard
        rng = np.random.default_rng(seed + 9)
        for k in range(40):
            c.drawCircle(rng.uniform(-80, 80), rng.uniform(120, 250), 3, paint(WHITE, 0.4 + 0.6 * ((int(T * 24) + k) % 5 == 0)))
        if mood == "laugh":
            c.drawPath(path(np.vstack([bez((-40, 120), (0, 170), (40, 120), 12)])), paint((140, 20, 40)))
        c.drawOval(skia.Rect.MakeLTRB(-130, -60, 120, 20), paint((220, 30, 50)))                                    # beret
        c.drawCircle(-10, -66, 12, paint((220, 30, 50)))
    c.restore()


def troupe(c, T, xs, y, s, wave=0.0, mood="smile", idx=0, halo=7.0, who=("marge", "gus", "pixel", "lou")):
    """The whole troupe, keyed in like everyone else."""
    for i, (name, x) in enumerate(zip(who, xs)):
        with D.live(c, idx + i * 3, halo=halo) as L:
            member(L, name, x, y, s, T, wave, mood, seed=i)

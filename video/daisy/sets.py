"""The places: the salon where the Oracle lives (striped 1960s wallpaper with a daisy print, a parquet floor), a field
of daisies, a banquet hall (damask, curtains, a long table, a chandelier), a room of pinned butterflies, the machine
room, and plain paper backdrops for the collage."""
import math

import numpy as np
import skia

import kit as K
import props as PR
from duo import daisy
from kit import INK, WHITE, H, W, lin, mix, paint, path, rad, smooth


def floor(c, y0=1480, colr=(150, 104, 64)):
    """Parquet in perspective from y0 down."""
    c.drawRect(skia.Rect.MakeLTRB(0, y0, W, H), paint(shader=lin((0, y0), (0, H), [mix(colr, INK, 0.35), colr])))
    vx, vy = W / 2, y0 - 900
    for k in range(-12, 13):
        x = W / 2 + k * 150
        c.drawLine(vx + (x - vx) * (y0 - vy) / (H - vy), y0, x, H, paint(mix(colr, INK, 0.45), 0.6, stroke=3))
    yy = y0
    step = 18
    while yy < H:
        c.drawLine(0, yy, W, yy, paint(mix(colr, INK, 0.4), 0.45, stroke=2))
        yy += step
        step *= 1.22
    c.drawRect(skia.Rect.MakeLTRB(0, y0 - 16, W, y0 + 6), paint((236, 228, 206)))        # a skirting board


def salon(c, T, wall=(222, 190, 92), wall2=(244, 232, 196), y_floor=1480, dots=True):
    """Striped wallpaper with a daisy sprig in every other stripe, a dado rail, parquet."""
    c.drawRect(skia.Rect.MakeWH(W, y_floor), paint(wall2))
    sw = 90
    for k in range(-1, W // sw + 2):
        if k % 2 == 0:
            c.drawRect(skia.Rect.MakeLTRB(k * sw, 0, k * sw + sw, y_floor), paint(wall))
        elif dots:
            for j in range(0, y_floor // 160 + 1):
                daisy(c, k * sw + sw / 2, 80 + j * 160 + (k % 4) * 40, 16, rot=j * 20 + k * 7, seed=k * 31 + j, a=0.75)
    c.drawRect(skia.Rect.MakeWH(W, y_floor), paint(shader=rad((W / 2, 600), 1300, [(255, 250, 230, 0.0), (0, 0, 0, 0.0), (20, 10, 0, 0.35)],
                                                              [0, 0.5, 1])))
    c.drawRect(skia.Rect.MakeLTRB(0, y_floor - 420, W, y_floor - 400), paint((236, 228, 206)))
    c.drawRect(skia.Rect.MakeLTRB(0, y_floor - 400, W, y_floor), paint(mix(wall, INK, 0.12), 0.45))
    floor(c, y_floor)


def field(c, T, horizon=760, sky=((150, 196, 230), (236, 236, 214)), sway=1.0, seed=3, density=1.0):
    """A meadow full of daisies under a pale summer sky."""
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, horizon), paint(shader=lin((0, 0), (0, horizon), list(sky))))
    for k in range(5):                                                    # soft clouds
        cx = (k * 260 + T * 8) % (W + 300) - 150
        c.drawOval(skia.Rect.MakeXYWH(cx, 120 + (k % 3) * 120, 300, 70), paint(WHITE, 0.55, blur=18))
    c.drawPath(smooth([(0, horizon), (200, horizon - 40), (480, horizon - 10), (760, horizon - 50), (W, horizon - 20), (W, horizon + 40),
                       (0, horizon + 40)]), paint((90, 120, 80)))                     # far trees
    c.drawRect(skia.Rect.MakeLTRB(0, horizon, W, H), paint(shader=lin((0, horizon), (0, H), [(130, 170, 90), (70, 120, 50)])))
    rng = K.rng_at(seed, 1)
    n = int(260 * density)
    items = []
    for i in range(n):
        u = rng.random() ** 1.7
        y = horizon + 20 + u * (H - horizon + 120)
        items.append((y, rng.uniform(-40, W + 40), i))
    items.sort()
    for y, x, i in items:
        depth = (y - horizon) / (H - horizon)
        r = 6 + 52 * depth ** 1.4
        sw = math.sin(T * 1.8 + x * 0.01 + i) * 4 * sway * depth
        c.drawLine(x, y + r * 0.2, x + sw, y + r * 2.2, paint((60, 110, 50), stroke=max(1, r * 0.12)))
        if i % 3 == 0:
            c.drawPath(K.bez_path([(x - r * 0.9, y + r * 2), (x - r * 0.3, y + r * 0.9), (x + r * 0.2, y + r * 0.3)]),
                       paint((80, 140, 60), stroke=max(1, r * 0.14)))
        daisy(c, x + sw, y, r, rot=i * 13, seed=i, petals=12 if r < 20 else 14)


def damask(c, x0, y0, x1, y1, base=(120, 26, 40), fig=(150, 40, 54)):
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(base))
    for j in range(int((y1 - y0) / 200) + 2):
        for k in range(int((x1 - x0) / 160) + 2):
            cx, cy = x0 + k * 160 + (80 if j % 2 else 0), y0 + j * 200
            c.drawPath(smooth([(cx, cy - 70), (cx + 40, cy - 20), (cx + 26, cy + 40), (cx, cy + 70), (cx - 26, cy + 40), (cx - 40, cy - 20)]),
                       paint(fig, 0.8))
            c.drawCircle(cx, cy, 12, paint(base))


def banquet_hall(c, T, table_y=1180, cloth=(246, 242, 232), chand=True, swing=0.0, lit=True):
    """Damask walls, swagged curtains, a long table running away from us, a chandelier."""
    damask(c, 0, 0, W, table_y + 60)
    for sx, x in ((-1, 0), (1, W)):                                       # curtains
        c.drawPath(smooth([(x, -20), (x - sx * 260, -20), (x - sx * 200, 500), (x - sx * 120, 1000), (x - sx * 40, table_y + 100),
                           (x, table_y + 100)]), paint((150, 30, 46)))
        for k in range(5):
            xx = x - sx * (40 + k * 45)
            c.drawLine(xx, 0, xx + sx * k * 10, table_y, paint((90, 10, 24), 0.5, stroke=14, blur=6))
    c.drawRect(skia.Rect.MakeLTRB(0, table_y + 60, W, H), paint((70, 40, 30)))
    # the table, in perspective toward a far vanishing point
    near_w, far_w = 1300, 300
    ty0, ty1 = table_y, H + 40
    tbl = path([(W / 2 - far_w / 2, ty0), (W / 2 + far_w / 2, ty0), (W / 2 + near_w / 2, ty1), (W / 2 - near_w / 2, ty1)])
    c.drawPath(tbl, paint(shader=lin((0, ty0), (0, ty1), [mix(cloth, INK, 0.12), cloth])))
    c.drawPath(path([(W / 2 - far_w / 2, ty0), (W / 2 + far_w / 2, ty0), (W / 2 + far_w / 2 + 6, ty0 + 40), (W / 2 - far_w / 2 - 6, ty0 + 40)]),
               paint(mix(cloth, INK, 0.2)))
    if chand:
        PR.chandelier(c, W / 2, 300, 0.9, T, swing, lit)


def butterfly_room(c, T, wall=(46, 70, 56)):
    """Dark green walls lined with glass cases of pinned specimens."""
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=lin((0, 0), (0, H), [mix(wall, INK, 0.3), wall, mix(wall, INK, 0.4)])))
    for j in range(7):
        for k in range(3):
            x0, y0 = 30 + k * 350, 40 + j * 270
            c.drawRect(skia.Rect.MakeXYWH(x0, y0, 320, 240), paint((92, 60, 36)))
            c.drawRect(skia.Rect.MakeXYWH(x0 + 12, y0 + 12, 296, 216), paint((214, 206, 180)))
            rng = K.rng_at(j, k)
            for b in range(3):
                PR.butterfly(c, x0 + 60 + b * 100, y0 + 110 + rng.uniform(-20, 20), 0.28 + rng.uniform(0, 0.1), T, pin=True, seed=b,
                             colors=[((222, 82, 52), (250, 196, 30)), ((60, 110, 170), (190, 220, 240)), ((120, 60, 120), (236, 170, 200))][(b + j + k) % 3])
            c.drawLine(x0 + 20, y0 + 20, x0 + 110, y0 + 230, paint(WHITE, 0.12, stroke=14))
    c.drawRect(skia.Rect.MakeWH(W, H), paint(INK, 0.35))


def machine_room(c, T, colr=(34, 30, 30)):
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=rad((W / 2, H / 2), 1300, [mix(colr, WHITE, 0.15), colr, INK])))


def void(c, colr=(238, 230, 210), seed=0):
    """A sheet of plain paper, faintly mottled."""
    c.drawRect(skia.Rect.MakeWH(W, H), paint(colr))
    rng = K.rng_at(seed, 17)
    for _ in range(40):
        c.drawCircle(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(30, 120), paint(mix(colr, INK, 0.06), 0.35, blur=40))

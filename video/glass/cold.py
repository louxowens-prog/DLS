"""The real world: cold, clinical and quiet. White panels and brushed steel, a reclined chair under a ring of lenses,
monitors glowing blue-grey; and Nadia's ordinary day as the systems see it - feeds, logs, scores, a box closing on a
face. Painted in near-natural colours; the print's steel wash drains them (alerts keep their red)."""
import math

import numpy as np
import skia

import cast as CA
import couture as C
import gel as G
import kit as K
from kit import BLACK, H, W, WHITE, mix, paint

WALL, WALL_D, STEEL, STEEL_D = (214, 220, 226), (150, 160, 172), (176, 184, 194), (84, 92, 106)
SCREEN, GLOW, UI, UI_DIM = (10, 18, 26), (110, 214, 236), (206, 238, 246), (110, 150, 166)
ALERT, AMBER, OK_GREEN = (255, 56, 56), (255, 186, 60), (90, 230, 160)


def ui_text(c, s, x, y, size, col=UI, align="left", tag="screen", font="jost-500", a=1.0):
    return K.text(c, s, x, y, size, font, col, align=align, tag=tag, a=a)


# ------------------------------------------------------------------ the white room

def ring_light(c, x, y, r, T, n=12, on=1.0, lens_r=None, tilt=0.42, a=1.0, hot=0.0):
    """An operating lamp made of cameras: a white ring light seen from below at an angle, studded with small lenses."""
    lens_r = lens_r or r * 0.13
    c.save()
    c.translate(x, y)
    c.scale(1.0, tilt)
    c.drawCircle(0, 0, r * 1.08, paint(STEEL_D, a))
    c.drawCircle(0, 0, r, paint((236, 244, 250), a * (0.6 + 0.4 * on), stroke=r * 0.16))
    c.drawCircle(0, 0, r, G.glow_paint((220, 246, 255), 0.5 * on * a, blur=r * 0.08))
    c.restore()
    for i in range(n):
        ang = 2 * math.pi * i / n + 0.15
        lx, ly = x + r * 0.92 * math.cos(ang), y + r * 0.92 * math.sin(ang) * tilt
        C.lens(c, lx, ly, lens_r * (0.85 + 0.25 * math.sin(ang)), T, open_=0.7, ring=STEEL, coat=(40, 120, 150), a=a, hot=hot)
    if on > 0:
        G.pool(c, x, y + r * 0.6, r * 2.6, (210, 240, 255), 0.18 * on * a, squash=0.6)


def chair(c, x, y, s, T, a=1.0, occupant=None, recline=1.0):
    """A reclined clinical chair in white leather and steel, seen from the front three-quarter; (x, y) the floor under
    the seat. occupant(c) paints whoever lies in it (in the chair's local units)."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    lp = paint()
    lp.setAlphaf(a)
    c.saveLayer(None, lp)
    c.drawOval(skia.Rect.MakeLTRB(-260, -30, 260, 30), paint((0, 0, 0), 0.25, blur=14))
    c.drawPath(K.rrect(-40, -260, 40, 0, 10), paint(shader=K.lin((-40, 0), (40, 0), [STEEL, (236, 240, 246), STEEL_D])))
    c.drawPath(K.rrect(-180, -40, 180, 0, 18), paint(shader=K.lin((0, -40), (0, 0), [(220, 226, 232), STEEL_D])))
    seat = K.smooth([(-210, -300), (210, -300), (230, -250), (-230, -250)])
    back = K.smooth([(-200, -300), (-170, -560 * recline - 40), (170, -560 * recline - 40), (200, -300)])
    legs = K.smooth([(-190, -300), (190, -300), (160, -150), (120, -120), (-120, -120), (-160, -150)])
    for p in (legs, back, seat):
        c.drawPath(p, paint(shader=K.lin((-220, 0), (220, 0), [(190, 198, 208), (246, 248, 250), (236, 240, 244), (170, 178, 190)])))
        c.drawPath(p, paint(STEEL_D, 0.5, stroke=3))
    c.drawPath(K.smooth([(-120, -600 * recline - 30), (120, -600 * recline - 30), (110, -520 * recline - 30), (-110, -520 * recline - 30)]),
               paint((240, 244, 248)))                                     # the headrest
    for sd in (-1, 1):                                                     # arm rests with straps
        c.drawPath(K.rrect(sd * 210 - 30, -400, sd * 210 + 30, -300, 12), paint((226, 232, 238)))
        c.drawRect(skia.Rect.MakeLTRB(sd * 210 - 32, -370, sd * 210 + 32, -350), paint((60, 66, 76)))
    if occupant is not None:
        occupant(c)
    c.restore()
    c.restore()


def white_room(c, T, hum=1.0, floor_y=1500, door=False, panel=(214, 220, 226), a=1.0):
    """The room itself, front on and symmetrical: back wall of square panels, a pale floor, cold light from above."""
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, floor_y), paint(shader=K.lin((0, 0), (0, floor_y), [mix(panel, (120, 130, 144), 0.4), panel, mix(panel, WHITE, 0.3)])))
    for i in range(7):
        for j in range(9):
            x0, y0 = 30 + i * 150, 40 + j * 160
            if y0 + 150 > floor_y:
                continue
            c.drawRect(skia.Rect.MakeLTRB(x0, y0, x0 + 144, y0 + 154), paint(mix(panel, WHITE, 0.2), 0.5))
            c.drawRect(skia.Rect.MakeLTRB(x0, y0, x0 + 144, y0 + 154), paint(WALL_D, 0.5, stroke=2))
    c.drawRect(skia.Rect.MakeLTRB(0, floor_y, W, H), paint(shader=K.lin((0, floor_y), (0, H), [(196, 202, 210), (150, 158, 170)])))
    for k in range(-8, 9):                                                  # floor joints running to the vanishing point
        c.drawLine(540 + k * 40, floor_y, 540 + k * 260, H, paint(WALL_D, 0.35, stroke=2))
    c.drawLine(0, floor_y, W, floor_y, paint(WALL_D, 0.8, stroke=3))
    if door:
        c.drawRect(skia.Rect.MakeLTRB(470, floor_y - 520, 610, floor_y), paint((190, 198, 208)))
        c.drawRect(skia.Rect.MakeLTRB(470, floor_y - 520, 610, floor_y), paint(WALL_D, stroke=3))


def monitor(c, x, y, w, h, T, content=None, a=1.0, glow=GLOW, frame=(40, 44, 52), arm=None, glow_k=1.0, tag="screen"):
    """A flat screen with a thin bezel; content(c, rect) paints what it shows; it throws its light around."""
    if arm is not None:
        c.drawLine(arm[0], arm[1], x + w / 2, y + h / 2, paint(STEEL_D, a, stroke=14))
        c.drawLine(arm[0], arm[1], x + w / 2, y + h / 2, paint(STEEL, a * 0.6, stroke=4))
    G.pool(c, x + w / 2, y + h / 2, max(w, h) * 0.9, glow, 0.16 * a * glow_k)
    c.drawPath(K.rrect(x - 10, y - 10, x + w + 10, y + h + 10, 8), paint(frame, a))
    r = skia.Rect.MakeLTRB(x, y, x + w, y + h)
    c.drawRect(r, paint(SCREEN, a))
    if content is not None:
        c.save()
        c.clipRect(r)
        lp = paint()
        lp.setAlphaf(a)
        c.saveLayer(None, lp)
        content(c, r)
        c.restore()
        c.restore()
    c.drawRect(r, paint(shader=K.lin((x, y), (x + w, y + h), [(255, 255, 255, 0.06), (255, 255, 255, 0.0), (255, 255, 255, 0.03)]), a=a))
    for yy in range(int(y), int(y + h), 4):                                 # scan lines
        c.drawLine(x, yy, x + w, yy, paint(BLACK, 0.06 * a, stroke=1))


def panel(c, x, y, w, h, title=None, a=1.0, col=UI, size=26, line=GLOW):
    """A flat interface panel: a dark slate card, a thin cyan rule, an uppercase title."""
    c.drawPath(K.rrect(x, y, x + w, y + h, 10), paint((14, 24, 32), 0.92 * a))
    c.drawPath(K.rrect(x, y, x + w, y + h, 10), paint(line, 0.45 * a, stroke=2))
    if title:
        ui_text(c, title, x + 22, y + size + 14, size, col, a=a, font="jost-600")
        c.drawLine(x + 22, y + size + 30, x + w - 22, y + size + 30, paint(line, 0.4 * a, stroke=2))


def bar(c, x, y, w, h, v, col=GLOW, a=1.0, back=(40, 56, 66)):
    c.drawPath(K.rrect(x, y, x + w, y + h, h / 2), paint(back, a))
    if v > 0:
        c.drawPath(K.rrect(x, y, x + w * min(1.0, v), y + h, h / 2), paint(col, a))


def target_box(c, x0, y0, x1, y1, T, label=None, conf=None, col=(120, 240, 255), lock=1.0, a=1.0, size=30, tag="screen", below=False):
    """Corner brackets closing on a face (lock 0 -> wide and loose, 1 -> tight), a label and a confidence."""
    k = 1 - min(1.0, max(0.0, lock))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w, h = (x1 - x0) * (1 + 0.6 * k), (y1 - y0) * (1 + 0.6 * k)
    X0, Y0, X1, Y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    L = min(w, h) * 0.22
    p = paint(col, a, stroke=4)
    for (px, py, dx, dy) in ((X0, Y0, 1, 1), (X1, Y0, -1, 1), (X0, Y1, 1, -1), (X1, Y1, -1, -1)):
        c.drawLine(px, py, px + dx * L, py, p)
        c.drawLine(px, py, px, py + dy * L, p)
    c.drawRect(skia.Rect.MakeLTRB(X0, Y0, X1, Y1), paint(col, 0.18 * a, stroke=1.5))
    if label and lock > 0.6:
        ty = (Y1 + size + 12) if below else (Y0 - 14)
        tw = K.font("jost-600", size).measureText(label)
        c.drawRect(skia.Rect.MakeLTRB(X0, ty - size - 4, X0 + tw + 24, ty + 10), paint(col, 0.9 * a))
        ui_text(c, label, X0 + 12, ty, size, (8, 14, 18), tag=tag, a=a, font="jost-600")
        if conf:
            ui_text(c, conf, X0 + tw + 34, ty, size, col, tag=tag, a=a, font="jost-600")


def trace(c, x, y, w, h, T, bpm=72, col=OK_GREEN, a=1.0):
    """A heart monitor trace sweeping left to right."""
    pts = []
    per = 60.0 / bpm
    for i in range(120):
        u = i / 119
        t = T - (1 - u) * 3.0
        ph = (t % per) / per
        v = 0.0
        if 0.1 < ph < 0.14:
            v = -0.25
        elif 0.14 < ph < 0.18:
            v = 1.0
        elif 0.18 < ph < 0.22:
            v = -0.45
        elif 0.35 < ph < 0.45:
            v = 0.18 * math.sin((ph - 0.35) / 0.1 * math.pi)
        pts.append((x + w * u, y + h / 2 - v * h * 0.42))
    c.drawPath(K.path(pts, closed=False), paint(col, a, stroke=3))
    c.drawPath(K.path(pts, closed=False), G.glow_paint(col, 0.35 * a, blur=4))
    c.drawCircle(*pts[-1], 6, G.glow_paint(col, a))


def cctv(c, r, T, kind="street", seed=0, stamp=True, a=1.0, people=6, hl=None):
    """A grey surveillance feed in rect r: a street, a corridor, a station or a crowd, figures drifting, a timestamp."""
    x0, y0, x1, y1 = r.left(), r.top(), r.right(), r.bottom()
    w, h = x1 - x0, y1 - y0
    rng = K.rng_at(seed, 61)
    c.drawRect(r, paint((70, 76, 82), a))
    hy = y0 + h * (0.42 if kind != "crowd" else 0.2)
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, hy), paint((96, 102, 108), a))
    for k in range(-5, 6):
        c.drawLine(x0 + w / 2 + k * w * 0.03, hy, x0 + w / 2 + k * w * 0.3, y1, paint((50, 56, 60), 0.6 * a, stroke=max(1, w * 0.004)))
    if kind in ("street", "station"):
        for side in (0, 1):
            for j in range(4):
                bx = x0 + (0.02 + 0.2 * j) * w if side == 0 else x1 - (0.2 + 0.2 * j) * w
                c.drawRect(skia.Rect.MakeXYWH(bx, hy - h * (0.2 + 0.08 * ((j + seed) % 3)), w * 0.16, h * (0.2 + 0.08 * ((j + seed) % 3))), paint((84, 90, 96), a))
    for i in range(people):
        px = x0 + w * ((rng.uniform(0, 1) + T * rng.uniform(-0.03, 0.03)) % 1.0)
        py = hy + (y1 - hy) * rng.uniform(0.15, 0.9)
        sc = (py - hy) / (y1 - hy) * h * 0.4 + h * 0.04
        c.drawRoundRect(skia.Rect.MakeXYWH(px - sc * 0.14, py - sc, sc * 0.28, sc), sc * 0.1, sc * 0.1, paint((30, 32, 36), 0.9 * a))
        c.drawCircle(px, py - sc - sc * 0.1, sc * 0.11, paint((30, 32, 36), 0.9 * a))
        if hl == i:
            target_box(c, px - sc * 0.3, py - sc * 1.3, px + sc * 0.3, py - sc * 0.6, T, a=a, lock=1.0, col=ALERT)
    if stamp:
        ui_text(c, "CAM %02d  %02d:%02d:%02d" % (seed % 97, 7 + seed % 12, (seed * 7) % 60, int(T * 10) % 60), x0 + w * 0.04, y0 + max(12, h * 0.1),
                max(10, h * 0.08), (230, 236, 240), tag="screen", a=0.9 * a)
        c.drawCircle(x1 - w * 0.06, y0 + h * 0.08, max(3, h * 0.03), paint(ALERT, a * (0.5 + 0.5 * (int(T * 2) % 2))))
    c.drawRect(r, paint((255, 255, 255), 0.05 * a))


def feeds(c, x0, y0, x1, y1, cols, rows, T, seed=0, gap=6, kinds=("street", "corridor", "station", "crowd"), a=1.0, hl=None):
    w = (x1 - x0 - gap * (cols - 1)) / cols
    h = (y1 - y0 - gap * (rows - 1)) / rows
    for i in range(cols):
        for j in range(rows):
            r = skia.Rect.MakeXYWH(x0 + i * (w + gap), y0 + j * (h + gap), w, h)
            k = i * rows + j
            cctv(c, r, T, kinds[(k + seed) % len(kinds)], seed=seed * 13 + k, a=a, stamp=w > 120, hl=(2 if hl == k else None))


def phone(c, x, y, s, T, screen=None, a=1.0, dark=False, tilt=0.0):
    """A phone in black glass, (x, y) its centre, about 520 x 1060 px at s = 1; screen(c, rect) paints its display."""
    c.save()
    c.translate(x, y)
    c.rotate(tilt)
    c.scale(s, s)
    lp = paint()
    lp.setAlphaf(a)
    c.saveLayer(None, lp)
    body = K.rrect(-260, -530, 260, 530, 70)
    c.drawPath(body, paint(shader=K.lin((-260, -530), (260, 530), [(60, 62, 70), (14, 14, 18), (40, 42, 48)])))
    c.drawPath(body, paint((120, 124, 134), 0.6, stroke=4))
    r = skia.Rect.MakeLTRB(-236, -506, 236, 506)
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(r, 52, 52), doAntiAlias=True)
    c.drawRect(r, paint((4, 4, 6)))
    if screen is not None and not dark:
        screen(c, r)
    c.drawRect(r, paint(shader=K.lin((-236, -506), (236, 506), [(255, 255, 255, 0.10), (255, 255, 255, 0.0), (255, 255, 255, 0.0), (255, 255, 255, 0.05)], [0, 0.35, 0.7, 1])))
    c.restore()
    c.drawPath(K.rrect(-50, -494, 50, -470, 12), paint((0, 0, 0)))          # the camera notch
    c.drawCircle(30, -482, 7, paint((30, 40, 60)))
    c.restore()
    c.restore()


# ------------------------------------------------------------------ Nadia's day

def road_grid(c, T, car_u=0.0, flashes=(), cam_pts=(), a=1.0, seed=0):
    """A city seen straight down at dawn: a grid of grey roads, roofs, a small car moving along its route, and a camera on
    every junction that flashes as she passes."""
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((66, 72, 80), a))
    rng = K.rng_at(seed, 71)
    for i in range(6):
        for j in range(9):
            x0, y0 = 40 + i * 180, 40 + j * 210
            c.drawRect(skia.Rect.MakeXYWH(x0, y0, 130, 160), paint(mix((96, 102, 112), (140, 146, 154), rng.uniform(0, 1)), a))
            c.drawRect(skia.Rect.MakeXYWH(x0 + 10, y0 + 10, 110, 140), paint((80, 86, 96), 0.4 * a, stroke=2))
    for i in range(7):
        x = 40 + i * 180 - 25
        for yy in range(0, H, 40):
            c.drawLine(x, yy, x, yy + 18, paint((200, 200, 190), 0.3 * a, stroke=2))
    return


def route(t):
    """Nadia's commute on the road grid: a path of junctions (screen coords) and where she is at progress t (0..1)."""
    pts = [(195, 1900), (195, 1525), (375, 1525), (375, 1105), (555, 1105), (555, 685), (735, 685), (735, 265), (915, 265), (915, -40)]
    L = [0.0]
    for i in range(1, len(pts)):
        L.append(L[-1] + math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]))
    d = t * L[-1]
    for i in range(1, len(pts)):
        if d <= L[i]:
            u = (d - L[i - 1]) / (L[i] - L[i - 1])
            p = (pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * u, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * u)
            ang = math.degrees(math.atan2(pts[i][1] - pts[i - 1][1], pts[i][0] - pts[i - 1][0]))
            return pts, p, ang
    return pts, pts[-1], -90.0


def car(c, x, y, ang, s=1.0, col=(150, 160, 176), a=1.0):
    c.save()
    c.translate(x, y)
    c.rotate(ang + 90)
    c.scale(s, s)
    c.drawPath(K.rrect(-26, -50, 26, 50, 14), paint(col, a))
    c.drawPath(K.rrect(-20, -26, 20, 16, 8), paint((40, 50, 64), a))
    c.drawCircle(-16, -48, 5, G.glow_paint((255, 250, 220), 0.9 * a))
    c.drawCircle(16, -48, 5, G.glow_paint((255, 250, 220), 0.9 * a))
    c.restore()


def door_inside(c, T, knock=0.0, light=1.0, a=1.0, shake=0.0):
    """An apartment door from inside at night: dark, a cold line of corridor light underneath and round the edges,
    a peephole glowing; on each knock the light in the gap jumps and the door shivers."""
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((14, 16, 20), a))
    dx = shake * math.sin(T * 90) * 6
    x0, x1, y0, y1 = 300 + dx, 780 + dx, 360, 1640
    c.drawRect(skia.Rect.MakeLTRB(x0 - 40, y0 - 40, x1 + 40, y1), paint((30, 32, 38), a))
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(shader=K.lin((x0, 0), (x1, 0), [(40, 42, 50), (54, 56, 64), (34, 36, 42)]), a=a))
    for (py0, py1) in ((440, 900), (980, 1560)):
        c.drawRect(skia.Rect.MakeLTRB(x0 + 60, py0, x1 - 60, py1), paint((26, 28, 34), 0.8 * a, stroke=6))
    k = light * (1 + 1.5 * knock)
    c.drawRect(skia.Rect.MakeLTRB(x0, y1 - 6, x1, y1 + 8), G.glow_paint((210, 230, 255), min(1.0, 0.8 * k) * a, blur=3))
    G.pool(c, (x0 + x1) / 2, y1 + 40, 380, (180, 210, 255), 0.25 * k * a, squash=0.25)
    c.drawLine(x1 + 2, y0, x1 + 2, y1, G.glow_paint((210, 230, 255), min(1.0, 0.3 * k) * a, blur=2))
    c.drawCircle((x0 + x1) / 2, 760, 12, G.glow_paint((230, 240, 255), min(1.0, 0.6 * k) * a))
    c.drawCircle(x1 - 70, 1000, 18, paint((140, 146, 156), a))
    c.drawRect(skia.Rect.MakeLTRB(x1 - 90, 960, x1 - 50, 980), paint((120, 126, 136), a))


def candle_crowd(c, T, a=1.0, seed=0, nadia_x=540, n=40):
    """A candlelight vigil at night: silhouettes in rows, each face lit warm from below by a small flame."""
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(shader=K.lin((0, 0), (0, H), [(6, 8, 14), (16, 18, 26), (8, 8, 12)]), a=a))
    rng = K.rng_at(seed, 83)
    rows = [(760, 0.45), (900, 0.6), (1080, 0.8), (1300, 1.05)]
    for ry, sc in rows:
        for i in range(int(9 / sc) + 2):
            x = (i + rng.uniform(-0.3, 0.3)) * 180 * sc - 40
            if abs(x - nadia_x) < 120 * sc and sc > 1.0:
                continue
            y = ry + rng.uniform(-20, 20)
            c.drawPath(K.smooth([(x - 70 * sc, y + 400 * sc), (x - 64 * sc, y + 80 * sc), (x, y + 40 * sc), (x + 64 * sc, y + 80 * sc), (x + 70 * sc, y + 400 * sc)]),
                       paint((14, 14, 18), a))
            c.drawCircle(x, y, 44 * sc, paint((18, 16, 18), a))
            fx, fy = x + 10 * sc, y + 110 * sc
            G.pool(c, fx, fy - 40 * sc, 120 * sc, (255, 170, 80), 0.3 * a * G.flicker(T, i + ry))
            c.drawCircle(x, y + 10 * sc, 30 * sc, G.glow_paint((255, 160, 80), 0.18 * a, blur=10 * sc))
            G.candle(c, fx, fy, 0.35 * sc, T, a=a, seed=i + int(ry), glow=0.4)

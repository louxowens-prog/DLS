"""Backgrounds for each dimension. The wide ones (sky, skyline, the graffiti wall) are painted once per process
into big images - halftone and hatching baked in, so the dots travel with the scenery - and then cropped by the
camera every frame."""
import math

import numpy as np
import skia

import sv
from sv import CYAN, DUSK, INK, MAG, NIGHT, WHITE, YEL, bez, paint, path

_cache = {}


def _img(arr):
    return skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType)


def _cached(name, fn):
    if name not in _cache:
        _cache[name] = fn()
    return _cache[name]


# ------------------------------------------------------------------ the night city

FAR_W, FAR_H = 2600, 1500


def _paint_far():
    st = sv.Stage(NIGHT, size=(FAR_W, FAR_H))
    c = st.c
    c.drawRect(skia.Rect.MakeXYWH(0, 0, FAR_W, FAR_H), paint(shader=sv.lin((0, 0), (0, FAR_H), [(18, 6, 44), NIGHT, DUSK, (150, 40, 150)], [0, 0.3, 0.72, 1])))
    st.shade("mag").drawRect(skia.Rect.MakeXYWH(0, 0, FAR_W, FAR_H),
                             paint(shader=sv.lin((0, 500), (0, FAR_H), [(255, 255, 255, 0.0), (255, 255, 255, 0.85)])))
    rng = np.random.default_rng(4)
    for i in range(160):                                           # stars
        x, y = rng.uniform(0, FAR_W), rng.uniform(0, 800)
        r = rng.uniform(1.5, 4.5)
        c.drawCircle(x, y, r, paint((255, 240, 255), rng.uniform(0.4, 1.0)))
    # the moon: pale, with halftone craters
    mx, my, mr = 1780, 380, 190
    moon = path(sv.ellipse(mx, my, mr, mr, 90))
    c.drawPath(moon, paint((255, 246, 224)))
    st.shade("mag").drawPath(moon, sv.CLEAR)
    sh = st.shade("dot")
    sh.save()
    sh.clipPath(moon, doAntiAlias=True)
    sh.drawCircle(mx + 70, my + 50, 170, paint(WHITE, 0.35))
    for cx, cy, cr in ((mx - 60, my - 40, 40), (mx + 40, my + 80, 30), (mx + 90, my - 70, 24)):
        sh.drawCircle(cx, cy, cr, paint(WHITE, 0.5))
    sh.restore()
    c.drawCircle(mx, my, mr + 60, paint((255, 200, 255), 0.18, blur=50))
    # far skyline: flat silhouettes with lit windows
    x = -40
    while x < FAR_W:
        w = rng.uniform(90, 230)
        h = rng.uniform(260, 700)
        top = FAR_H - h
        c.drawRect(skia.Rect.MakeLTRB(x, top, x + w, FAR_H), paint((44, 16, 88)))
        if rng.random() < 0.3:
            c.drawRect(skia.Rect.MakeLTRB(x + w * 0.4, top - 70, x + w * 0.46, top), paint((44, 16, 88)))
        win = skia.Path()
        for wy in np.arange(top + 30, FAR_H - 20, 42):
            for wx in np.arange(x + 16, x + w - 20, 34):
                if rng.random() < 0.28:
                    win.addRect(skia.Rect.MakeXYWH(wx, wy, 16, 22))
        c.drawPath(win, paint((255, 214, 240)))
        x += w + rng.uniform(-10, 30)
    st.flush()
    return _img(st.arr)


MID_W, MID_H = 3200, 1920


def _paint_mid():
    """Nearer buildings (transparent above the roofs): brick faces, fire escapes, water towers, neon signs."""
    st = sv.Stage(None, size=(MID_W, MID_H))
    P = st.pen()
    c = st.c
    rng = np.random.default_rng(9)
    x = -60
    k = 0
    while x < MID_W:
        w = rng.uniform(260, 420)
        top = rng.uniform(760, 1080)
        col = [(92, 26, 120), (70, 20, 104), (110, 30, 130)][k % 3]
        bld = path([(x, top), (x + w, top), (x + w, MID_H), (x, MID_H)])
        P.fill(bld, col)
        P.sh["hatch"].drawRect(skia.Rect.MakeLTRB(x + w * 0.62, top, x + w, MID_H), paint(WHITE, 0.55))
        c.drawRect(skia.Rect.MakeLTRB(x - 6, top - 16, x + w + 6, top + 6), paint((40, 12, 60)))
        win = skia.Path()
        lit = skia.Path()
        for wy in np.arange(top + 60, MID_H - 40, 110):
            for wx in np.arange(x + 34, x + w - 50, 78):
                r = skia.Rect.MakeXYWH(wx, wy, 40, 62)
                (lit if rng.random() < 0.35 else win).addRect(r)
        c.drawPath(win, paint((36, 10, 56)))
        c.drawPath(lit, paint((255, 208, 120)))
        P.sh["dot"].drawPath(lit, paint(WHITE, 0.25))
        if rng.random() < 0.6:                                       # fire escape: ink zigzag
            fx = x + w * 0.2
            for fy in np.arange(top + 150, MID_H - 100, 220):
                sv.ink(c, [(fx, fy), (fx + 160, fy)], 8)
                sv.ink(c, [(fx + 10, fy), (fx + 150, fy + 110)], 6)
                for j in range(9):
                    sv.ink(c, [(fx + j * 20, fy), (fx + j * 20, fy - 40)], 3)
        if rng.random() < 0.5:                                       # water tower
            tx = x + w * rng.uniform(0.3, 0.7)
            c.drawRect(skia.Rect.MakeLTRB(tx - 50, top - 150, tx + 50, top - 50), paint((60, 20, 80)))
            c.drawPath(path([(tx - 60, top - 150), (tx + 60, top - 150), (tx, top - 200)]), paint((60, 20, 80)))
            for lx in (-40, 40):
                sv.ink(c, [(tx + lx, top - 50), (tx + lx * 1.3, top)], 7)
            sv.outline(c, path([(tx - 50, top - 150), (tx + 50, top - 150), (tx + 50, top - 50), (tx - 50, top - 50)]), 5)
        if rng.random() < 0.55:                                      # neon sign
            sx, sy = x + w * 0.3, top + rng.uniform(100, 300)
            ncol = [MAG, CYAN, YEL][k % 3]
            word = ["OPEN", "24H", "PIZZA", "RECORDS", "LAB", "DELI"][k % 6]
            f = sv.font("bangers-400", 64)
            tw = f.measureText(word)
            c.drawRect(skia.Rect.MakeXYWH(sx - 16, sy - 70, tw + 32, 92), paint((20, 6, 30)))
            c.drawString(word, sx, sy, f, paint(ncol, 0.5, blur=12))
            c.drawString(word, sx, sy, f, paint(ncol))
            c.drawString(word, sx, sy, f, paint(WHITE, 0.6, stroke=2))
        sv.outline(c, bld, 6)
        x += w + rng.uniform(10, 60)
        k += 1
    st.flush()
    return _img(st.arr)


def city(st, camx=0.0, camy=0.0, T=0.0, far_d=11, mid_d=5, train=True, mid=True):
    """The night city in two parallax planes, both knocked off register (they're out of focus).
    camx/camy: camera offset in screen pixels at the near plane."""
    far = _cached("far", _paint_far)
    c = st.c
    c.drawImage(far, -((camx * 0.15 + 300) % (FAR_W - sv.W)), -120 - camy * 0.1)
    if far_d:
        sv.misregister(st.arr, far_d)
    if mid:
        m = _cached("mid", _paint_mid)
        c.drawImage(m, -((camx * 0.45 + 200) % (MID_W - sv.W)), 180 - camy * 0.4)
        if train:
            _train(c, T, 1080 - camy * 0.4)
        if mid_d:
            sv.misregister(st.arr, mid_d)


def _train(c, T, y):
    """An elevated train crossing on its bridge (mid plane)."""
    c.drawRect(skia.Rect.MakeLTRB(0, y + 90, sv.W, y + 130), paint((30, 8, 50)))
    for bx in range(-40, sv.W + 80, 160):
        sv.ink(c, [(bx, y + 130), (bx + 80, y + 300)], 10, color=(30, 8, 50))
        sv.ink(c, [(bx + 160, y + 130), (bx + 80, y + 300)], 10, color=(30, 8, 50))
    x0 = (T * 900) % 4200 - 2400
    for car in range(4):
        cx = x0 + car * 560
        if cx > sv.W + 40 or cx + 540 < -40:
            continue
        c.drawRoundRect(skia.Rect.MakeLTRB(cx, y - 60, cx + 540, y + 90), 26, 26, paint((200, 210, 230)))
        c.drawRect(skia.Rect.MakeLTRB(cx, y + 20, cx + 540, y + 40), paint(MAG))
        for wx in range(20, 520, 70):
            c.drawRect(skia.Rect.MakeLTRB(cx + wx, y - 36, cx + wx + 50, y + 4), paint((255, 230, 150)))
        c.drawRoundRect(skia.Rect.MakeLTRB(cx, y - 60, cx + 540, y + 90), 26, 26, paint(INK, stroke=7))


# ------------------------------------------------------------------ the graffiti wall

WALL_W, WALL_H = 7400, 1000                     # brick wall 0..WALL_H, then sidewalk and street below
GROUND_H = 700


def _paint_wall():
    st = sv.Stage((70, 18, 74), size=(WALL_W, WALL_H + GROUND_H))
    P = st.pen()
    c = st.c
    sv.bricks(c, 0, 0, WALL_W, WALL_H, bw=150, bh=58, col_=(122, 36, 116), mortar=(58, 14, 64))
    P.sh["hatch"].drawRect(skia.Rect.MakeXYWH(0, 0, WALL_W, 220), paint(shader=sv.lin((0, 0), (0, 220), [(255, 255, 255, 0.75), (255, 255, 255, 0.0)])))
    P.sh["dot"].drawRect(skia.Rect.MakeXYWH(0, WALL_H - 300, WALL_W, 300), paint(shader=sv.lin((0, WALL_H - 300), (0, WALL_H), [(255, 255, 255, 0.0), (255, 255, 255, 0.55)])))
    # coping along the top of the wall
    c.drawRect(skia.Rect.MakeLTRB(0, -2, WALL_W, 30), paint((150, 70, 160)))
    c.drawRect(skia.Rect.MakeLTRB(0, 30, WALL_W, 40), paint(INK))
    # sidewalk, curb, street
    c.drawRect(skia.Rect.MakeLTRB(0, WALL_H, WALL_W, WALL_H + 170), paint((96, 52, 110)))
    P.sh["dot"].drawRect(skia.Rect.MakeLTRB(0, WALL_H, WALL_W, WALL_H + 170), paint(WHITE, 0.3))
    for x in range(0, WALL_W, 260):
        sv.ink(c, [(x, WALL_H + 4), (x - 60, WALL_H + 166)], 4, color=(60, 26, 70), taper=(0.05, 0.05))
    c.drawRect(skia.Rect.MakeLTRB(0, WALL_H + 170, WALL_W, WALL_H + 200), paint((180, 150, 190)))
    c.drawRect(skia.Rect.MakeLTRB(0, WALL_H + 200, WALL_W, WALL_H + GROUND_H), paint((34, 12, 46)))
    for x in range(0, WALL_W, 300):
        c.drawRect(skia.Rect.MakeXYWH(x, WALL_H + 420, 150, 18), paint((200, 190, 90)))
    c.drawRect(skia.Rect.MakeLTRB(0, WALL_H - 2, WALL_W, WALL_H + 6), paint(INK))
    st.flush()
    rng = np.random.default_rng(21)
    words = ["DREAM", "YO!", "KAPOW", "NYC", "FRESH", "ZIG", "ECHO", "WILD", "RAD", "BOOM", "LOOP", "HYPE", "SK8", "WOW"]
    for i in range(46):                                             # old tags, faded
        x, y = rng.uniform(80, WALL_W - 80), rng.uniform(120, WALL_H - 60)
        col = [(200, 80, 200), (60, 170, 220), (220, 200, 70), (240, 110, 140)][i % 4]
        sv.tag_text(c, words[i % len(words)], x, y, rng.uniform(60, 120), fill=col, edge=(40, 10, 50), rot=rng.uniform(-12, 8),
                    seed=i, drip=rng.random() < 0.5, tag="bgtag", a=0.26, fname="permanent-marker-400" if i % 3 else "sedgwick-ave-display-400")
    sv.TEXT.clear()
    return _img(st.arr)


def wall(st, camx, y0=520):
    """The long graffiti wall; camx = how far along it the camera has panned (pixels)."""
    img = _cached("wall", _paint_wall)
    st.c.drawImage(img, -camx, y0)


# ------------------------------------------------------------------ other dimensions

def noir_alley(st, T):
    """Black-and-white alley: a streetlamp cone, blinds' shadows across bricks. (Rain goes on top.)"""
    c = st.c
    P = st.pen()
    c.drawColor(sv.col((40, 40, 40)))
    sv.bricks(c, 0, 0, sv.W, sv.H, bw=160, bh=60, col_=(76, 76, 76), mortar=(30, 30, 30))
    P.sh["xhatch"].drawRect(skia.Rect.MakeXYWH(0, 0, sv.W, sv.H), paint(shader=sv.rad((820, 300), 1100, [(255, 255, 255, 0.0), (255, 255, 255, 0.0), (255, 255, 255, 0.8)], [0, 0.35, 1])))
    for i in range(7):                                             # venetian-blind light
        y = 360 + i * 70
        c.drawPath(path([(160, y), (760, y - 120), (760, y - 84), (160, y + 36)]), paint((200, 200, 200), 0.55))
    c.drawPath(path([(760, 0), (840, 0), (1080, 1920), (380, 1920)]), paint((255, 255, 255), 0.12))
    sv.ink(c, [(820, 0), (820, 260)], 16, color=(20, 20, 20))
    c.drawPath(path([(760, 260), (880, 260), (850, 300), (790, 300)]), paint((20, 20, 20)))
    c.drawCircle(820, 310, 26, paint(WHITE))
    c.drawCircle(820, 310, 90, paint(WHITE, 0.25, blur=40))


def anime_burst(st, T, cx=540, cy=700):
    c = st.c
    c.drawRect(skia.Rect.MakeXYWH(0, 0, sv.W, sv.H), paint(shader=sv.rad((cx, cy), 1300, [(255, 255, 255), (255, 200, 236), (255, 120, 200), (170, 90, 255)], [0, 0.25, 0.6, 1])))
    sv.speed_lines(c, cx, cy, T, n=90, r0=420, r1=1800, color=WHITE, a=0.9, seed=31, w=14)
    rng = np.random.default_rng(int(sv.twos(T) * 12) % 3 + 40)
    from cast import _sparkle
    for i in range(22):
        x, y = rng.uniform(40, sv.W - 40), rng.uniform(80, sv.H - 200)
        _sparkle(c, x, y, rng.uniform(14, 36), WHITE if i % 3 else YEL)
    for i in range(16):                                            # petals drifting (on twos)
        t2 = sv.twos(T)
        x = (i * 173 + t2 * 120) % (sv.W + 100) - 50
        y = (i * 311 + t2 * 260) % (sv.H + 100) - 50
        c.save()
        c.translate(x, y)
        c.rotate(i * 40 + t2 * 90)
        c.drawOval(skia.Rect.MakeLTRB(-14, -8, 14, 8), paint((255, 190, 220)))
        c.drawOval(skia.Rect.MakeLTRB(-14, -8, 14, 8), paint((230, 90, 150), stroke=3))
        c.restore()


def cartoon_stage(st, T):
    """Flat Saturday-morning stage: curtains, a spotlight, no print texture at all."""
    c = st.c
    c.drawColor(sv.col((255, 214, 90)))
    c.drawCircle(540, 1000, 700, paint((255, 238, 160)))
    c.drawCircle(540, 1000, 480, paint((255, 250, 210)))
    for side in (-1, 1):
        x0 = 0 if side < 0 else sv.W - 230
        c.drawRect(skia.Rect.MakeXYWH(x0, 0, 230, sv.H), paint((230, 40, 70)))
        for j in range(4):
            fx = x0 + 30 + j * 55
            sv.ink(c, [(fx, 0), (fx + 6 * side, sv.H)], 6, color=(160, 20, 50), taper=(0.02, 0.02))
    c.drawRect(skia.Rect.MakeXYWH(0, 0, sv.W, 150), paint((230, 40, 70)))
    for i in range(12):
        sv.ink(c, bez((i * 90, 150), (i * 90 + 45, 210), (i * 90 + 90, 150)), 9, color=(160, 20, 50), taper=(0.1, 0.1))
    c.drawRect(skia.Rect.MakeXYWH(0, 1560, sv.W, 360), paint((150, 80, 40)))
    for i in range(14):
        sv.ink(c, [(0, 1600 + i * 26), (sv.W, 1600 + i * 26)], 3, color=(110, 56, 26), taper=(0.02, 0.02))
    # even the cartoon world is printed: orange dots in the backdrop, hatching in the curtain folds
    st.inks["yel"] = ((255, 150, 40), 18, 15, "dot")
    st.shade("yel").drawRect(skia.Rect.MakeXYWH(230, 150, sv.W - 460, 1410), paint(shader=sv.rad((540, 1000), 900, [(255, 255, 255, 0.0), (255, 255, 255, 0.0), (255, 255, 255, 0.7)], [0, 0.45, 1])))
    for x0 in (0, sv.W - 230):
        st.shade("hatch").drawRect(skia.Rect.MakeXYWH(x0, 0, 230, sv.H), paint(WHITE, 0.35))
    st.shade("hatch").drawRect(skia.Rect.MakeXYWH(0, 0, sv.W, 150), paint(WHITE, 0.35))


def confetti(c, T, n=40, seed=5, y0=0):
    rng = np.random.default_rng(seed)
    t2 = sv.twos(T)
    for i in range(n):
        x = rng.uniform(0, sv.W)
        v = rng.uniform(160, 320)
        y = (rng.uniform(0, sv.H) + t2 * v) % (sv.H + 60) - 30 + y0
        col = [sv.MAG, sv.CYAN, sv.YEL, (120, 230, 90), (255, 120, 40)][i % 5]
        c.save()
        c.translate(x + 20 * math.sin(t2 * 3 + i), y)
        c.rotate(i * 37 + t2 * 200)
        c.drawRect(skia.Rect.MakeLTRB(-10, -5, 10, 5), paint(col))
        c.restore()

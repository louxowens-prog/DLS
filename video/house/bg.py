"""Painted backdrops (each painted once per process and cached): the sets behind the paper cast.

Every set has a window onto a garish painted sky - the film's signature: nothing outside is real."""
import math

import numpy as np
import skia

import hx
from hx import CREAM, INK, MINT, PEACH, PINK, POWDER, W, H, bez, paint, path


def _img(arr):
    return hx.image(arr)


def _window(c, x0, y0, x1, y1, sky_seed=1, frame=(255, 250, 240), arch=True, night=False, bars=True):
    """A window with a painted sky in it."""
    w, h = int(x1 - x0), int(y1 - y0)
    if night:
        sky = hx.painted_sky(w, h, seed=sky_seed, bands=[(10, 6, 30), (40, 14, 70), (90, 30, 90), (40, 14, 60)], sun=(0.7, 0.3, 0.1), clouds=True)
    else:
        sky = hx.painted_sky(w, h, seed=sky_seed)
    c.save()
    clip = skia.Path()
    if arch:
        clip.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x0, y0, x1, y1), w / 2, w / 2))
        clip.addRect(skia.Rect.MakeLTRB(x0, y0 + w / 2, x1, y1))
    else:
        clip.addRect(skia.Rect.MakeLTRB(x0, y0, x1, y1))
    c.clipPath(clip, doAntiAlias=True)
    c.drawImage(_img(sky), x0, y0)
    hx.hills(c, w, 0, 0, seed=sky_seed)
    c.save()
    c.translate(x0, y1 - h * 0.28)
    hx.hills(c, w, 0, h * 0.2, color=(40, 12, 50) if not night else (8, 4, 20), seed=sky_seed + 3)
    c.restore()
    c.restore()
    fw = 22
    if arch:
        c.drawPath(clip, paint(frame, stroke=fw))
    else:
        c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(frame, stroke=fw))
    if bars:
        c.drawLine((x0 + x1) / 2, y0 + (w / 2 if arch else 0), (x0 + x1) / 2, y1, paint(frame, stroke=12))
        c.drawLine(x0, (y0 + y1) / 2 + h * 0.1, x1, (y0 + y1) / 2 + h * 0.1, paint(frame, stroke=12))


def _wallpaper(c, x0, y0, x1, y1, base, stripe, flower=None, seed=0):
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(base))
    for x in np.arange(x0, x1, 90):
        c.drawRect(skia.Rect.MakeLTRB(x, y0, x + 34, y1), paint(stripe, 0.55))
    if flower:
        rng = np.random.default_rng(seed)
        for x in np.arange(x0 + 62, x1, 90):
            for y in np.arange(y0 + 40, y1, 120):
                yy = y + (x // 90 % 2) * 60
                for k in range(5):
                    a = k * 2 * math.pi / 5
                    c.drawCircle(x + 12 * math.cos(a), yy + 12 * math.sin(a), 8, paint(flower, 0.8))
                c.drawCircle(x, yy, 6, paint((255, 230, 150)))
    hx.brushwork(c, x0, y0, x1, y1, base, spread=16, n=int((x1 - x0) * (y1 - y0) / 1800), seed=seed, size=(20, 70), a=0.12)


def _floor(c, y, color=(160, 100, 70), plank=(130, 80, 56)):
    c.drawRect(skia.Rect.MakeLTRB(0, y, W, H), paint(color))
    for k in range(12):
        yy = y + (k * k) * 9 + k * 12
        c.drawLine(0, yy, W, yy, paint(plank, stroke=4))
    for k in range(-10, 20):
        c.drawLine(W / 2 + k * 40, y, W / 2 + k * 170, H, paint(plank, 0.6, stroke=3))
    hx.brushwork(c, 0, y, W, H, color, spread=14, n=600, seed=7, size=(30, 90), a=0.15, angle=0.0, jitter_a=0.05)


def _paint(fn):
    st = hx.Stage(INK)
    fn(st.c)
    return _img(st.arr)


def parlor():
    """The sweet parlour: pink striped wallpaper with little flowers, a great arched window onto a painted sunset,
    lace, a velvet chair, a cushion for the cat, and a bare nail where the cuckoo clock hangs."""
    def f(c):
        _wallpaper(c, 0, 0, W, 1420, (255, 196, 210), (255, 226, 234), flower=(240, 120, 160), seed=1)
        _window(c, 250, 250, 830, 1180, sky_seed=4)
        for sx in (-1, 1):                                                # lace curtains
            x0 = 250 if sx < 0 else 700
            for k in range(8):
                xx = x0 + k * 16 + (0 if sx < 0 else 0)
                c.drawPath(path(bez((xx, 220), (xx + sx * 30, 700), (xx + 10, 1220)), closed=False), paint(CREAM, 0.55, stroke=14))
        c.drawRect(skia.Rect.MakeLTRB(200, 214, 880, 244), paint((200, 150, 110)))
        c.drawRect(skia.Rect.MakeLTRB(0, 1380, W, 1420), paint((230, 170, 150)))
        _floor(c, 1420)
        c.drawOval(skia.Rect.MakeLTRB(120, 1560, 960, 1800), paint((140, 60, 100)))       # a round rug
        c.drawOval(skia.Rect.MakeLTRB(170, 1590, 910, 1770), paint((200, 110, 150)))
    return hx.cached("parlor", lambda: _paint(f))


def kitchen():
    """The kitchen: mint tiles, a window onto a painted sunset garden, a table with a gingham cloth."""
    def f(c):
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 1500), paint((196, 238, 222)))
        for x in range(0, W, 90):
            c.drawLine(x, 0, x, 1500, paint((170, 214, 200), stroke=4))
        for y in range(0, 1500, 90):
            c.drawLine(0, y, W, y, paint((170, 214, 200), stroke=4))
        hx.brushwork(c, 0, 0, W, 1500, (196, 238, 222), spread=12, n=700, seed=3, a=0.12)
        _window(c, 300, 250, 800, 820, sky_seed=7, arch=False)
        c.drawRect(skia.Rect.MakeLTRB(260, 820, 840, 860), paint((250, 240, 230)))
        for k in range(3):                                                 # shelf with jars
            c.drawRect(skia.Rect.MakeLTRB(60 + k * 60, 900, 100 + k * 60, 990), paint([hx.PINK, hx.POWDER, hx.PEACH][k]))
        c.drawRect(skia.Rect.MakeLTRB(40, 990, 260, 1006), paint((170, 110, 80)))
        _floor(c, 1500, color=(230, 200, 170), plank=(200, 170, 140))
        # table with a gingham cloth
        c.drawRect(skia.Rect.MakeLTRB(80, 1300, 1000, 1520), paint((255, 255, 255)))
        for x in range(80, 1000, 60):
            c.drawRect(skia.Rect.MakeLTRB(x, 1300, x + 30, 1520), paint((255, 140, 160), 0.55))
        for y in range(1300, 1520, 60):
            c.drawRect(skia.Rect.MakeLTRB(80, y, 1000, y + 30), paint((255, 140, 160), 0.55))
    return hx.cached("kitchen", lambda: _paint(f))


def courtroom():
    """Wood panelling, the bench, tall windows onto a painted sky."""
    def f(c):
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((120, 70, 44)))
        for x in range(0, W, 180):
            c.drawRect(skia.Rect.MakeLTRB(x + 14, 80, x + 166, 1300), paint((140, 86, 56)))
            c.drawRect(skia.Rect.MakeLTRB(x + 14, 80, x + 166, 1300), paint((90, 50, 30), stroke=6))
        hx.brushwork(c, 0, 0, W, 1300, (130, 78, 50), spread=14, n=900, seed=5, a=0.15, angle=math.pi / 2, jitter_a=0.05)
        for k, x in enumerate((110, 810)):
            _window(c, x, 180, x + 160, 700, sky_seed=10 + k)
        c.drawRect(skia.Rect.MakeLTRB(0, 1300, W, H), paint((70, 40, 26)))
        c.drawRect(skia.Rect.MakeLTRB(200, 880, 880, 1300), paint((96, 54, 32)))          # the bench
        c.drawRect(skia.Rect.MakeLTRB(180, 860, 900, 900), paint((150, 96, 60)))
        c.drawCircle(540, 1050, 90, paint((200, 160, 60)))
        c.drawCircle(540, 1050, 70, paint((150, 110, 40)))
    return hx.cached("courtroom", lambda: _paint(f))


def hospital(red=False):
    """A hospital corridor in one-point perspective, pale green, doors receding."""
    def f(c):
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((200, 228, 206)))
        vx, vy = 540, 860
        c.drawPath(path([(0, 0), (W, 0), (vx + 120, vy - 160), (vx - 120, vy - 160)]), paint((236, 244, 232)))
        c.drawPath(path([(0, H), (W, H), (vx + 120, vy + 160), (vx - 120, vy + 160)]), paint((170, 200, 176)))
        c.drawRect(skia.Rect.MakeLTRB(vx - 120, vy - 160, vx + 120, vy + 160), paint((150, 180, 160)))
        c.drawRect(skia.Rect.MakeLTRB(vx - 60, vy - 110, vx + 60, vy + 160), paint((90, 120, 110)))
        for k in range(5):
            u = 0.15 + k * 0.17
            for sx in (-1, 1):
                xa = vx + sx * (540 * (1 - u) + 120 * u)
                ya0, ya1 = 0 * (1 - u) + (vy - 160) * u, H * (1 - u) + (vy + 160) * u
                c.drawLine(xa, ya0 + 200 * (1 - u), xa, ya1 - 300 * (1 - u), paint((120, 150, 130), stroke=6 * (1 - u) + 2))
            ly = (vy - 160) * u
            c.drawRect(skia.Rect.MakeLTRB(vx - 90 * (1 - u) - 30, ly + 20 * (1 - u), vx + 90 * (1 - u) + 30, ly + 30 * (1 - u) + 10), paint((255, 255, 230)))
        hx.brushwork(c, 0, 0, W, H, (200, 228, 206), spread=12, n=900, seed=9, a=0.1)
    return hx.cached("hospital", lambda: _paint(f))


def bedroom():
    """Night: a bed, a lamp, a window onto a painted moonlit sky."""
    def f(c):
        _wallpaper(c, 0, 0, W, 1400, (120, 110, 190), (140, 130, 210), flower=(200, 170, 250), seed=11)
        _window(c, 330, 220, 750, 760, sky_seed=12, night=True, arch=True)
        _floor(c, 1400, color=(110, 70, 60), plank=(90, 56, 46))
        c.drawRect(skia.Rect.MakeLTRB(80, 1060, 1000, 1460), paint((250, 230, 240)))       # the bed
        c.drawRect(skia.Rect.MakeLTRB(80, 1150, 1000, 1460), paint((255, 150, 190)))
        c.drawRect(skia.Rect.MakeLTRB(60, 900, 110, 1560), paint((140, 90, 70)))
        c.drawRect(skia.Rect.MakeLTRB(970, 1000, 1020, 1560), paint((140, 90, 70)))
    return hx.cached("bedroom", lambda: _paint(f))


def street():
    """Across the street at night: the neighbour's house, one window lit."""
    def f(c):
        sky = hx.painted_sky(W, 1100, seed=21, bands=[(20, 8, 40), (70, 20, 90), (160, 40, 110), (255, 90, 90), (255, 150, 80)])
        c.drawImage(_img(sky), 0, 0)
        c.drawRect(skia.Rect.MakeLTRB(0, 1100, W, H), paint((30, 14, 36)))
        c.drawPath(path([(160, 700), (540, 380), (920, 700)]), paint((60, 24, 50)))
        c.drawRect(skia.Rect.MakeLTRB(200, 700, 880, 1400), paint((90, 40, 70)))
        c.drawRect(skia.Rect.MakeLTRB(380, 820, 700, 1120), paint((255, 220, 130)))
        c.drawRect(skia.Rect.MakeLTRB(380, 820, 700, 1120), paint((40, 14, 30), stroke=16))
        c.drawRect(skia.Rect.MakeLTRB(470, 1200, 610, 1400), paint((40, 14, 30)))
    return hx.cached("street", lambda: _paint(f))


def album_page(seed=0):
    """A scrapbook page: dark card with a paper grain, a little doodled border."""
    def f(c):
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((44, 26, 34)))
        hx.brushwork(c, 0, 0, W, H, (54, 32, 42), spread=10, n=1800, seed=31 + seed, size=(10, 30), a=0.3)
        for k in range(40):
            x = 40 + k * 26
            c.drawCircle(x, 60, 6, paint((255, 200, 220), 0.5))
            c.drawCircle(x, H - 60, 6, paint((255, 200, 220), 0.5))
    return hx.cached(f"album{seed}", lambda: _paint(f))


def sky_full(seed=2):
    def f(c):
        c.drawImage(_img(hx.painted_sky(W, H, seed=seed, sun=(0.5, 0.52, 0.22))), 0, 0)
        c.save()
        c.translate(0, H * 0.72)
        hx.hills(c, W, 0, 160, seed=seed)
        c.restore()
    return hx.cached(f"sky{seed}", lambda: _paint(f))


def space():
    """A painted cosmos: violet-to-orange, a scatter of painted stars."""
    def f(c):
        c.drawImage(_img(hx.painted_sky(W, H, seed=41, bands=[(10, 6, 30), (40, 14, 70), (110, 30, 110), (255, 90, 110), (255, 160, 80)],
                                        sun=(0.5, 0.9, 0.3), clouds=False)), 0, 0)
        rng = np.random.default_rng(4)
        for _ in range(160):
            c.drawCircle(rng.uniform(0, W), rng.uniform(0, H * 0.7), rng.uniform(1, 4), paint(CREAM, rng.uniform(0.4, 1)))
    return hx.cached("space", lambda: _paint(f))

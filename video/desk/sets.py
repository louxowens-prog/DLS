"""The sets. Each backdrop paints a full 1080 x 1920 frame once (cached); anything that moves is drawn by the shot.

PRESENT  her kitchen at night (one window, the table, the lamp), the same kitchen at dawn, the exam hall
MEMORY   the classroom of thirty-eight (one-point perspective, a single bulb), the street with the tutor's window,
         the teacher's kitchen at night
FICTION  the lacquer stage: a black void, a gold-leaf floor, vermilion and gold proscenium, painted panels -
         and the machinery that splits, slides and turns the sets
"""
import math

import numpy as np
import skia

import draw as D
from draw import (CREAM, GOLD, GOLDD, GOLDL, H, INK, JADE, KHAKI, LACQ, PALE, PINK, SLATE, VERM, W, WHITE, mix, paint,
                  path)


def _grad(c, y0, y1, cols, x0=0, x1=W):
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(shader=D.lin((0, y0), (0, y1), cols)))


def _noise_tex(amp, seed=0, div=3):
    def make():
        rng = np.random.default_rng(seed)
        from PIL import Image, ImageFilter
        n = rng.normal(0, 1, (H // div, W // div)).astype(np.float32)
        im = Image.fromarray(np.clip(n * 40 + 128, 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.5))
        return 1 + amp * (np.asarray(im, np.float32) / 128 - 1)
    return D.cached(f"ntex{amp}{seed}{div}", make)


def bd(st, name, fn, tex=0.05):
    """A backdrop drawn once and reused, with a faint surface texture (plaster, paper, leaf)."""
    def make():
        s = D.Stage()
        fn(s.c)
        D.apply_tex(s.arr, _noise_tex(tex, seed=len(name)))
        return D.image(s.arr)
    st.c.drawImage(D.cached("bd_" + name, make), 0, 0)


# ------------------------------------------------------------------ present

def kitchen(c, morning=False):
    wall = (74, 78, 80) if not morning else (170, 168, 156)
    _grad(c, 0, 1250, [mix(wall, INK, 0.25), wall, mix(wall, INK, 0.15)])
    wx0, wx1, wy0, wy1 = 250, 830, 250, 900                             # the window, centred
    c.drawRect(skia.Rect.MakeLTRB(wx0 - 30, wy0 - 30, wx1 + 30, wy1 + 30), paint(mix(wall, INK, 0.4)))
    if not morning:
        _grad(c, wy0, wy1, [(22, 28, 40), (34, 40, 54), (48, 50, 60)], wx0, wx1)
        rng = np.random.default_rng(4)
        for i in range(8):                                              # the city at night, far off
            bx, bh = wx0 + i * 75, rng.uniform(120, 320)
            c.drawRect(skia.Rect.MakeLTRB(bx, wy1 - bh, bx + 66, wy1), paint((26, 30, 38)))
            for r in range(int(bh // 40)):
                for q in range(3):
                    if rng.random() < 0.35:
                        c.drawRect(skia.Rect.MakeXYWH(bx + 8 + q * 20, wy1 - bh + 14 + r * 40, 10, 14), paint((230, 200, 140), 0.7))
    else:
        _grad(c, wy0, wy1, [(226, 228, 222), (206, 210, 206), (190, 192, 186)], wx0, wx1)
        for j in range(16):                                             # blinds
            y = wy0 + 20 + j * 40
            c.drawRect(skia.Rect.MakeLTRB(wx0, y, wx1, y + 14), paint((236, 234, 224), 0.8))
    c.drawLine((wx0 + wx1) / 2, wy0, (wx0 + wx1) / 2, wy1, paint(mix(wall, INK, 0.4), stroke=16))
    c.drawLine(wx0, (wy0 + wy1) / 2, wx1, (wy0 + wy1) / 2, paint(mix(wall, INK, 0.4), stroke=16))
    for x in (100, 980):                                                # a shelf each side, cups
        c.drawRect(skia.Rect.MakeLTRB(x - 80, 560, x + 80, 574), paint(mix(wall, INK, 0.45)))
        for k in range(3):
            c.drawRect(skia.Rect.MakeLTRB(x - 60 + k * 44, 520, x - 30 + k * 44, 560), paint(mix(wall, WHITE, 0.25)))
    # the table, in perspective, taking the bottom of the frame
    table = mix((96, 78, 62), KHAKI, 0.25) if not morning else (150, 128, 104)
    c.drawPath(path([(60, 1180), (1020, 1180), (1080, 1520), (0, 1520)]), paint(shader=D.lin((0, 1180), (0, 1520), [mix(table, INK, 0.2), table])))
    _grad(c, 1520, H, [mix(table, INK, 0.5), mix(table, INK, 0.7)])
    c.drawLine(60, 1180, 1020, 1180, paint(mix(table, WHITE, 0.2), stroke=3))


def exam_hall(c):
    _grad(c, 0, 900, [(150, 152, 146), (176, 176, 168)])
    for i in range(4):                                                  # tall windows, pale morning
        x = 60 + i * 260
        c.drawRect(skia.Rect.MakeLTRB(x, 140, x + 160, 760), paint((222, 224, 218)))
        c.drawLine(x + 80, 140, x + 80, 760, paint((150, 152, 146), stroke=8))
        c.drawPath(path([(x, 760), (x + 160, 760), (x + 260, 1500), (x - 40, 1500)]), paint((240, 238, 226), 0.08))
    _grad(c, 900, H, [(132, 124, 108), (100, 94, 84)])
    vx, vy = 540, 820
    for j in range(-8, 9):
        c.drawLine(vx + j * 30, vy + 80, vx + j * 200, H, paint((90, 84, 74), 0.5, stroke=3))


def exam_desks():
    """Desk positions for the hall and the classroom: rows from the back (small) to the front (large)."""
    out = []
    vx, vy = 540, 780
    rows = 6
    for r in range(rows):
        k = (r + 1) / rows
        y = vy + 120 + 900 * k ** 1.5
        s = 0.25 + 0.9 * k ** 1.5
        for q in range(-3, 3):
            x = vx + (q + 0.5) * 230 * s
            out.append((x, y, s, r, q))
    return out


# ------------------------------------------------------------------ memory

def classroom(c):
    vx, vy = 540, 700
    _grad(c, 0, H, [(90, 90, 90), (120, 120, 120)])
    c.drawPath(path([(0, 0), (300, 480), (300, 900), (0, 1920)]), paint((70, 70, 70)))            # left wall
    c.drawPath(path([(1080, 0), (780, 480), (780, 900), (1080, 1920)]), paint((100, 100, 100)))    # right wall
    c.drawRect(skia.Rect.MakeLTRB(300, 480, 780, 900), paint((150, 150, 150)))                    # the front wall
    c.drawRect(skia.Rect.MakeLTRB(350, 560, 730, 780), paint((40, 44, 42)))                       # the blackboard
    c.drawRect(skia.Rect.MakeLTRB(350, 560, 730, 780), paint((120, 110, 90), stroke=10))
    D.text(c, "dy/dx = lim", 470, 660, 44, "cormorant-600", (230, 230, 230), tag="board")
    D.text(c, "h→0", 470, 700, 26, "oldstandard-700", (230, 230, 230), tag="board")
    D.text(c, "f(x+h) − f(x)", 640, 640, 30, "cormorant-600", (230, 230, 230), tag="board")
    c.drawLine(575, 652, 710, 652, paint((230, 230, 230), stroke=3))
    D.text(c, "h", 640, 690, 30, "cormorant-600", (230, 230, 230), tag="board")
    c.drawPath(path([(300, 900), (780, 900), (1080, 1920), (0, 1920)]), paint((110, 110, 110)))   # the floor
    for j in range(-9, 10):
        c.drawLine(vx + j * 26, 900, vx + j * 130, H, paint((80, 80, 80), stroke=3))
    for i in range(3):                                                  # windows on the left wall, light falling in
        y0 = 180 + i * 260
        c.drawPath(path([(40 + i * 70, y0 + 60), (180 + i * 40, y0 + 120), (180 + i * 40, y0 + 300), (40 + i * 70, y0 + 330)]),
                   paint((236, 236, 236)))
        c.drawPath(path([(180 + i * 40, y0 + 120), (180 + i * 40, y0 + 300), (760, 1500 + i * 60), (520, 1600 + i * 60)]),
                   paint((255, 255, 255), 0.07))


def street(c):
    _grad(c, 0, H, [(30, 30, 30), (50, 50, 50)])
    c.drawRect(skia.Rect.MakeLTRB(120, 200, 960, 1500), paint((70, 70, 70)))                    # the house opposite
    for r in range(4):
        for q in range(3):
            x, y = 200 + q * 260, 300 + r * 290
            if (r, q) == (1, 1):
                continue
            c.drawRect(skia.Rect.MakeLTRB(x, y, x + 160, y + 190), paint((34, 34, 34)))
    c.drawRect(skia.Rect.MakeLTRB(0, 1500, W, H), paint((24, 24, 24)))
    # her own window frame, dark, in the foreground: the view is through it
    c.drawRect(skia.Rect.MakeLTRB(0, 0, 70, H), paint((12, 12, 12)))
    c.drawRect(skia.Rect.MakeLTRB(1010, 0, W, H), paint((12, 12, 12)))
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 90), paint((12, 12, 12)))
    c.drawRect(skia.Rect.MakeLTRB(0, 1640, W, H), paint((12, 12, 12)))
    c.drawRect(skia.Rect.MakeLTRB(530, 0, 550, 1640), paint((12, 12, 12)))


def teacher_kitchen(c):
    _grad(c, 0, 1200, [(40, 40, 40), (70, 70, 70)])
    c.drawRect(skia.Rect.MakeLTRB(620, 260, 960, 700), paint((22, 22, 22)))                     # a dark window
    c.drawLine(790, 260, 790, 700, paint((60, 60, 60), stroke=10))
    c.drawPath(path([(40, 1160), (1040, 1160), (1080, 1500), (0, 1500)]), paint((120, 120, 120)))
    _grad(c, 1500, H, [(60, 60, 60), (40, 40, 40)])


# ------------------------------------------------------------------ fiction: the stage

def stage(c, panel="gold"):
    """Black void; a gold-leaf floor in perspective; vermilion proscenium posts; a painted panel upstage."""
    c.drawRect(skia.Rect.MakeWH(W, H), paint(LACQ))
    if panel:
        col = {"gold": GOLD, "pink": PINK, "jade": JADE, "verm": VERM, "indigo": (30, 36, 90)}[panel]
        c.drawRect(skia.Rect.MakeLTRB(160, 260, 920, 1060), paint(shader=D.rad((540, 560), 700, [mix(col, WHITE, 0.15), col, mix(col, INK, 0.5)])))
        if panel == "gold":                                             # squares of leaf, seams showing
            for i in range(10):
                for j in range(12):
                    x, y = 160 + i * 76, 260 + j * 67
                    c.drawRect(skia.Rect.MakeXYWH(x, y, 76, 67), paint(mix(GOLDD, GOLDL, ((i * 7 + j * 3) % 5) / 5), 0.35))
                    c.drawRect(skia.Rect.MakeXYWH(x, y, 76, 67), paint(GOLDD, 0.35, stroke=1.5))
    floor = path([(160, 1060), (920, 1060), (1080, 1560), (0, 1560)])
    c.drawPath(floor, paint(shader=D.lin((0, 1060), (0, 1560), [GOLDD, GOLD, GOLDL])))
    for j in range(-6, 7):                                              # the seams of the leaf floor
        c.drawLine(540 + j * 64, 1060, 540 + j * 190, 1560, paint(GOLDD, 0.45, stroke=2))
    for k in range(6):
        y = 1060 + 500 * (k / 6) ** 1.4
        c.drawLine(0, y, W, y, paint(GOLDD, 0.35, stroke=2))
    c.drawRect(skia.Rect.MakeLTRB(0, 1560, W, H), paint(LACQ))                                   # the stage edge
    c.drawLine(0, 1560, W, 1560, paint(GOLDL, stroke=6))
    for x0, x1 in ((0, 110), (970, W)):                                 # proscenium posts
        c.drawRect(skia.Rect.MakeLTRB(x0, 0, x1, 1560), paint(shader=D.lin((x0, 0), (x1, 0), [mix(VERM, INK, 0.4), VERM, mix(VERM, INK, 0.5)])))
        c.drawLine(x0 + 10, 0, x0 + 10, 1560, paint(GOLD, stroke=5))
        c.drawLine(x1 - 10, 0, x1 - 10, 1560, paint(GOLD, stroke=5))
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 170), paint(shader=D.lin((0, 0), (0, 170), [mix(VERM, INK, 0.5), VERM])))
    c.drawLine(0, 170, W, 170, paint(GOLD, stroke=6))


def spotlight(c, x, y_top, x_floor, y_floor, w, a=0.35, col=(255, 240, 200)):
    """A hard theatrical spot from the flies onto the floor."""
    p = path([(x - 30, y_top), (x + 30, y_top), (x_floor + w, y_floor), (x_floor - w, y_floor)])
    c.drawPath(p, paint(shader=D.lin((0, y_top), (0, y_floor), [(*col, 0.05), (*col, 1.0)]), a=a))
    c.save()
    c.translate(x_floor, y_floor)
    c.scale(1, 0.22)
    c.drawCircle(0, 0, w, paint(col, a * 1.1, blur=20))
    c.restore()


# ------------------------------------------------------------------ stage machinery

def layer(fn):
    """Render fn(c) into its own transparent image (for sets that split, slide or turn)."""
    s = skia.Surface(W, H)
    cc = s.getCanvas()
    cc.clear(skia.ColorTRANSPARENT)
    fn(cc)
    return s.makeImageSnapshot()


def split(c, img, k, gap_col=None, axis="x"):
    """The set splits down the middle and its halves glide apart (k 0..1), revealing what's behind."""
    d = (W / 2 + 40) * D.ease(k)
    for side in (-1, 1):
        c.save()                                                        # the half moves with its own clip
        if axis == "x":
            c.translate(side * d, 0)
            c.clipRect(skia.Rect.MakeLTRB(0 if side < 0 else W / 2, 0, W / 2 if side < 0 else W, H))
        else:
            c.translate(0, side * d)
            c.clipRect(skia.Rect.MakeLTRB(0, 0 if side < 0 else H / 2, W, H / 2 if side < 0 else H))
        c.drawImage(img, 0, 0)
        c.restore()
        if axis == "x" and k > 0:                                        # the lit edge of each moving flat
            ex = W / 2 + side * d
            c.drawLine(ex, 0, ex, H, paint(GOLDL, 0.8, stroke=6))


def turn(c, img_a, img_b, k, cx=W / 2):
    """A turntable: the set turns away (squeezes to its edge) and the next turns into view."""
    if k < 0.5:
        sx, img = math.cos(k * math.pi), img_a
    else:
        sx, img = -math.cos(k * math.pi), img_b
    c.save()
    c.translate(cx, 0)
    c.scale(max(0.02, sx), 1)
    c.translate(-cx, 0)
    c.drawImage(img, 0, 0)
    c.restore()


def slide(c, img, k, direction=1):
    """A flat slides off sideways (k 0..1)."""
    c.save()
    c.translate(direction * (W + 60) * D.ease(k), 0)
    c.drawImage(img, 0, 0)
    c.restore()

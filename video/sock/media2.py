"""More hand-made media: an early-2000s Flash web cartoon (flat fills, fat black outlines, motion tweens, a preloader),
MS Paint (chunky aliased pixels, the Windows 98 chrome, pencil / brush / spray can / bucket), and PS1-era 3-D
(a tiny software rasterizer: wobbling snapped vertices, flat shading, no z-buffer, fog, 15-bit colour, dithering)."""
import math

import numpy as np
import skia
from PIL import Image, ImageDraw

import diy as K
from diy import ACID, BLUE, GOLD, HOT, INK, PURPLE, WHITE, W, H, bez, ease, lin, mix, paint, path, rad, ramp, smooth

# ------------------------------------------------------------------ Flash

OUT = 9.0


def fl(c, p, fill, outline=OUT, grad=None, a=1.0):
    """A Flash shape: flat (or two-stop) fill and a fat black outline with round joins."""
    if grad is not None:
        b = p.computeTightBounds()
        c.drawPath(p, paint(shader=lin((b.left(), b.top()), (b.left(), b.bottom()), [grad[0], grad[1]]), a=a))
    else:
        c.drawPath(p, paint(fill, a))
    if outline:
        c.drawPath(p, paint(INK, a, stroke=outline))
    return p


def fl_oval(c, cx, cy, rx, ry, fill, **kw):
    p = skia.Path()
    p.addOval(skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry))
    return fl(c, p, fill, **kw)


def fl_rrect(c, x0, y0, x1, y1, r, fill, **kw):
    p = skia.Path()
    p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x0, y0, x1, y1), r, r))
    return fl(c, p, fill, **kw)


def tween(T, t0, t1, a, b, kind="inout"):
    """A Flash motion tween from a to b (numbers or tuples)."""
    k = ramp(T, t0, t1)
    k = ease(k) if kind == "inout" else (1 - (1 - k) ** 2 if kind == "out" else k * k)
    if isinstance(a, (tuple, list)):
        return tuple(x + (y - x) * k for x, y in zip(a, b))
    return a + (b - a) * k


def preloader(c, T, t0, t1, y=1000):
    """The preloader every Flash site made you watch: LOADING... and a bar that crawls, then jumps."""
    k = ramp(T, t0, t1)
    pct = int(min(99, (k ** 0.4) * 99)) if k < 1 else 100
    c.drawRect(skia.Rect.MakeWH(W, H), paint((240, 240, 240)))
    K.text(c, "LOADING...", W / 2, y - 60, 72, "audiowide-400", (60, 60, 70), tag="flash")
    c.drawRect(skia.Rect.MakeXYWH(190, y, 700, 50), paint((60, 60, 70), stroke=5))
    c.drawRect(skia.Rect.MakeXYWH(198, y + 8, 684 * pct / 100, 34), paint(shader=lin((198, 0), (882, 0), [HOT, PURPLE, BLUE])))
    K.text(c, f"{pct}%", W / 2, y + 130, 60, "audiowide-400", (60, 60, 70), tag="flash")
    skip_intro(c, W / 2, y + 260, T)


def skip_intro(c, x, y, T, a=1.0):
    hot = int(T * 3) % 2 == 0
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 170, y - 44, 340, 66), 33, 33), paint((255, 255, 255) if hot else (230, 230, 240), a))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 170, y - 44, 340, 66), 33, 33), paint(INK, a, stroke=4))
    K.text(c, "SKIP INTRO >>", x, y + 2, 38, "audiowide-400", (40, 40, 60), tag="flash", a=a)


def sparkle(c, x, y, r, T, color=WHITE, a=1.0):
    """A four-point Flash sparkle that pulses."""
    k = 0.6 + 0.4 * math.sin(T * 8)
    r *= k
    pts = [(x, y - r), (x + r * 0.22, y - r * 0.22), (x + r, y), (x + r * 0.22, y + r * 0.22), (x, y + r), (x - r * 0.22, y + r * 0.22),
           (x - r, y), (x - r * 0.22, y - r * 0.22)]
    c.drawPath(path(pts), paint(color, a))


def affirma(c, x, y, s, T, talk=0.0, nod=1.0, mood="beam", look=(0.0, 0.0), a=1.0):
    """AFFIRMA, NOD-TV's agreeable AI host: a glossy hot-pink egg of a head with a screen for a face (huge sparkly
    eyes, a huge smile), a little gold bow tie, floating over a chrome stand. She nods. Always."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    bob = math.sin(T * 2 * math.pi * 1.4) * 12 * nod
    # the stand
    fl(c, path([(-30, 180), (30, 180), (60, 420), (-60, 420)]), None, grad=((230, 230, 245), (120, 120, 150)), a=a)
    fl_oval(c, 0, 430, 150, 34, None, grad=((240, 240, 250), (110, 110, 140)), a=a)
    c.translate(0, bob)
    c.rotate(bob * 0.25)
    head = smooth([(0, -250), (150, -200), (205, -40), (180, 120), (0, 200), (-180, 120), (-205, -40), (-150, -200)])
    fl(c, head, None, grad=((255, 140, 210), (200, 20, 120)), a=a)
    c.drawPath(smooth([(-110, -205), (-30, -235), (40, -225), (-40, -190), (-120, -150)]), paint(WHITE, 0.55 * a))
    scr = skia.Path()
    scr.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-150, -150, 150, 110), 60, 60))
    fl(c, scr, None, grad=((40, 20, 70), (10, 6, 30)), outline=7, a=a)
    c.save()
    c.clipPath(scr, doAntiAlias=True)
    for yy in range(-150, 110, 8):
        c.drawLine(-150, yy, 150, yy, paint(WHITE, 0.05 * a, stroke=2))
    for sx in (-1, 1):                                                  # big sparkly eyes
        ex, ey = sx * 62 + look[0] * 10, -46 + look[1] * 8
        if mood == "beam":
            c.drawPath(path(bez((ex - 40, ey + 10), (ex, ey - 44), (ex + 40, ey + 10), 14), closed=False), paint((120, 255, 220), a, stroke=14))
        else:
            c.drawOval(skia.Rect.MakeXYWH(ex - 34, ey - 46, 68, 92), paint((120, 255, 220), a))
            c.drawOval(skia.Rect.MakeXYWH(ex - 20, ey - 30, 40, 56), paint((20, 30, 60), a))
            c.drawCircle(ex + 10, ey - 18, 10, paint(WHITE, a))
        sparkle(c, ex + sx * 44, ey - 50, 18, T + sx, (255, 240, 120), a)
    mo = 30 + 40 * talk
    c.drawPath(path(np.vstack([bez((-90, 30), (0, 30 + mo * 1.6), (90, 30), 18), bez((90, 30), (0, 40), (-90, 30), 18)])),
               paint((120, 255, 220), a))
    c.drawCircle(-104, 26, 18, paint((255, 120, 200), 0.6 * a))
    c.drawCircle(104, 26, 18, paint((255, 120, 200), 0.6 * a))
    c.restore()
    fl(c, path([(-50, 196), (0, 214), (50, 196), (50, 244), (0, 226), (-50, 244)]), GOLD, outline=6, a=a)       # bow tie
    c.restore()


def metric(c, x, y, s, T, talk=0.0, needle=0.7, a=1.0, arm=0.0):
    """Mr. Metric, the network boss: a gold suit and, for a head, a dashboard gauge marked SATISFACTION whose
    needle swings to the red when he gets excited."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    # body: gold suit, a fat tie
    fl(c, smooth([(-170, 120), (-150, 20), (-60, -20), (60, -20), (150, 20), (170, 120), (190, 520), (-190, 520)]), None,
       grad=((255, 220, 90), (200, 140, 20)), a=a)
    fl(c, path([(-40, -20), (40, -20), (0, 60)]), WHITE, outline=6, a=a)
    fl(c, path([(-18, 10), (18, 10), (30, 260), (0, 300), (-30, 260)]), HOT, outline=6, a=a)
    # arms: one pointing up at the ratings
    for sx, ang in ((-1, 20), (1, -150 + arm * 20)):
        c.save()
        c.translate(sx * 150, 40)
        c.rotate(sx * ang if sx < 0 else ang)
        fl_rrect(c, -34, 0, 34, 230, 30, None, grad=((255, 220, 90), (200, 140, 20)), a=a)
        fl_oval(c, 0, 250, 40, 40, (255, 210, 180), a=a)
        c.restore()
    # the gauge head
    c.translate(0, -170)
    fl_oval(c, 0, 0, 150, 150, (40, 40, 50), a=a)
    fl_oval(c, 0, 0, 128, 128, (250, 250, 240), outline=5, a=a)
    for i in range(11):
        an = math.radians(-210 + i * 24)
        col = (40, 180, 70) if i < 4 else ((250, 200, 0) if i < 8 else (230, 30, 40))
        c.drawLine(98 * math.cos(an), 98 * math.sin(an), 118 * math.cos(an), 118 * math.sin(an), paint(col, a, stroke=8))
    K.text(c, "SATISFACTION", 0, 70, 24, "rubik-900", (60, 60, 70), tag="gauge", a=a)
    nd = -210 + 240 * min(1.0, max(0.0, needle + 0.05 * math.sin(T * 30) * talk))
    an = math.radians(nd)
    c.drawLine(0, 0, 100 * math.cos(an), 100 * math.sin(an), paint((230, 30, 40), a, stroke=9))
    c.drawCircle(0, 0, 16, paint(INK, a))
    # a mouth on the gauge glass, under it all
    mo = 8 + 26 * talk
    c.drawPath(path(np.vstack([bez((-50, 26), (0, 26 + mo * 1.4), (50, 26), 12), bez((50, 26), (0, 32), (-50, 26), 12)])), paint(INK, a))
    c.restore()


def audience(c, y, T, clap=1.0, rows=3, seed=4, a=1.0, empty=False):
    """Rows of Flash audience heads, clapping on a two-frame loop."""
    rng = np.random.default_rng(seed)
    for r in range(rows):
        yy = y + r * 120
        n = 7 + r
        for i in range(n):
            x = (i + 0.5) * W / n + rng.uniform(-10, 10)
            if empty:
                fl_rrect(c, x - 52, yy - 30, x + 52, yy + 80, 18, (170, 30, 50), outline=6, a=a)
                continue
            hop = (6 if (int(T * 12) + i + r) % 2 else 0) * clap
            col = [(255, 210, 170), (230, 170, 120), (170, 110, 70), (120, 80, 50)][int(rng.integers(0, 4))]
            hair = [(40, 30, 20), (240, 200, 60), (200, 60, 40), (90, 60, 30), (30, 30, 40)][int(rng.integers(0, 5))]
            fl_rrect(c, x - 56, yy + 20 - hop, x + 56, yy + 140, 30, [(250, 120, 180), (110, 200, 255), (255, 210, 80), (170, 120, 255)][(i + r) % 4],
                     outline=6, a=a)
            fl_oval(c, x, yy - 10 - hop, 44, 50, col, outline=6, a=a)
            c.drawPath(path(bez((x - 44, yy - 20 - hop), (x, yy - 80 - hop), (x + 44, yy - 20 - hop), 10)), paint(hair, a))
            if clap > 0:
                ph = (int(T * 12) + i) % 2
                hx = x + (14 if ph else 26)
                c.drawCircle(x - (14 if ph else 26), yy + 60 - hop, 16, paint(col, a))
                c.drawCircle(hx, yy + 60 - hop, 16, paint(col, a))


# ------------------------------------------------------------------ MS Paint

LW, LH = 270, 480                       # the low-res screen, shown at 4x
PAL = [(0, 0, 0), (128, 128, 128), (128, 0, 0), (128, 128, 0), (0, 128, 0), (0, 128, 128), (0, 0, 128), (128, 0, 128),
       (128, 128, 64), (0, 64, 64), (0, 128, 255), (0, 64, 128), (128, 0, 255), (128, 64, 0),
       (255, 255, 255), (192, 192, 192), (255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255),
       (255, 255, 128), (0, 255, 128), (128, 255, 255), (128, 128, 255), (255, 0, 128), (255, 128, 64)]
CANVAS = (24, 30, 262, 404)             # x0, y0, x1, y1 of the white drawing area (low-res px)
GREY = (192, 192, 192)


def px(c=INK, stroke=None):
    p = skia.Paint(AntiAlias=False)
    p.setColor4f(K.col(c))
    if stroke is not None:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kSquare_Cap)
    return p


def ptext(c, s, x, y, size=8, color=INK, fname="silkscreen-400", align="left"):
    f = K.font(fname, size)
    f.setEdging(skia.Font.Edging.kAlias)
    w = f.measureText(s)
    x0 = x - w / 2 if align == "center" else (x - w if align == "right" else x)
    c.drawString(s, x0, y, f, px(color))
    return w


def _bevel(c, x0, y0, x1, y1, down=False):
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), px(GREY))
    hi, lo = ((128, 128, 128), WHITE) if down else (WHITE, (128, 128, 128))
    c.drawLine(x0, y0, x1 - 1, y0, px(hi, 1))
    c.drawLine(x0, y0, x0, y1 - 1, px(hi, 1))
    c.drawLine(x0, y1 - 1, x1 - 1, y1 - 1, px(lo, 1))
    c.drawLine(x1 - 1, y0, x1 - 1, y1 - 1, px(lo, 1))


TOOLS = ["free", "select", "eraser", "fill", "pick", "zoom", "pencil", "brush", "spray", "text", "line", "curve", "rect", "poly",
         "ellipse", "rrect"]


def paint_chrome(c, tool="pencil", fg=(0, 0, 0), bg=WHITE, title="untitled - Paint", status="For Help, click Help Topics on the Help Menu."):
    """The Windows 98 Paint window, at low resolution."""
    c.drawRect(skia.Rect.MakeWH(LW, LH), px(GREY))
    for i in range(LW):                                                    # the title bar gradient
        k = i / LW
        c.drawLine(i, 2, i, 13, px(mix((0, 0, 128), (16, 132, 208), k), 1))
    ptext(c, title, 4, 11, 8, WHITE, "silkscreen-700")
    for j, (x0, ch) in enumerate([(LW - 30, "_"), (LW - 20, "o"), (LW - 10, "x")]):
        _bevel(c, x0 - 1, 4, x0 + 8, 12)
        ptext(c, ch, x0 + 1, 11, 8, INK)
    xx = 4
    for m in ("File", "Edit", "View", "Image", "Colors", "Help"):
        xx += ptext(c, m, xx, 24, 8, INK) + 7
    # the tool box (two columns of 8 buttons) on the left
    for i, t in enumerate(TOOLS):
        bx, by = 2 + (i % 2) * 11, 32 + (i // 2) * 11
        _bevel(c, bx, by, bx + 11, by + 11, down=(t == tool))
        _tool_icon(c, t, bx + 2, by + 2)
    # the canvas, sunk into the grey
    x0, y0, x1, y1 = CANVAS
    c.drawRect(skia.Rect.MakeLTRB(x0 - 1, y0 - 1, x1 + 1, y1 + 1), px((128, 128, 128)))
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), px(WHITE))
    # the colour box at the bottom
    yb = y1 + 6
    _bevel(c, 2, yb, 22, yb + 22, down=True)
    c.drawRect(skia.Rect.MakeXYWH(9, yb + 9, 9, 9), px(bg))
    c.drawRect(skia.Rect.MakeXYWH(5, yb + 4, 9, 9), px(fg))
    for i, cc in enumerate(PAL):
        cx, cy = 26 + (i % 14) * 11, yb + (i // 14) * 11
        _bevel(c, cx, cy, cx + 11, cy + 11, down=True)
        c.drawRect(skia.Rect.MakeXYWH(cx + 2, cy + 2, 7, 7), px(cc))
    c.drawRect(skia.Rect.MakeLTRB(0, LH - 14, LW, LH), px(GREY))
    _bevel(c, 1, LH - 13, LW - 40, LH - 1, down=True)
    ptext(c, status[:44], 4, LH - 4, 8, INK)


def _tool_icon(c, t, x, y):
    k = px(INK, 1)
    if t == "pencil":
        c.drawLine(x + 1, y + 6, x + 6, y + 1, px((200, 160, 0), 2))
        c.drawPoint(x + 1, y + 6, px(INK))
    elif t == "brush":
        c.drawLine(x + 2, y + 6, x + 6, y + 2, px((150, 90, 0), 2))
        c.drawRect(skia.Rect.MakeXYWH(x, y + 5, 3, 2), px(INK))
    elif t == "spray":
        c.drawRect(skia.Rect.MakeXYWH(x + 3, y + 2, 3, 5), px((120, 120, 120)))
        for dx, dy in ((0, 1), (1, 3), (0, 5), (2, 0)):
            c.drawPoint(x + dx, y + dy, px(INK))
    elif t == "fill":
        c.drawRect(skia.Rect.MakeXYWH(x + 1, y + 2, 5, 5), px((120, 120, 120)))
        c.drawPoint(x + 6, y + 6, px((0, 0, 255)))
    elif t == "text":
        ptext(c, "A", x + 1, y + 7, 8, INK)
    elif t == "eraser":
        c.drawRect(skia.Rect.MakeXYWH(x + 1, y + 2, 6, 4), px((255, 160, 200)))
    elif t == "rect":
        c.drawRect(skia.Rect.MakeXYWH(x + 1, y + 1, 6, 5), k)
    elif t == "ellipse":
        c.drawOval(skia.Rect.MakeXYWH(x + 1, y + 1, 6, 5), k)
    elif t == "line":
        c.drawLine(x + 1, y + 6, x + 6, y + 1, k)
    elif t == "zoom":
        c.drawCircle(x + 3, y + 3, 2, k)
        c.drawLine(x + 5, y + 5, x + 7, y + 7, k)
    elif t in ("select", "free"):
        c.drawRect(skia.Rect.MakeXYWH(x + 1, y + 1, 6, 5), px((80, 80, 80), 1))
    else:
        c.drawPoint(x + 3, y + 3, px(INK))


def paint_cursor(c, x, y, tool="pencil"):
    """The tool cursor, at canvas resolution."""
    if tool == "pencil":
        c.drawLine(x, y, x + 6, y - 6, px((220, 180, 0), 2))
        c.drawLine(x + 5, y - 7, x + 7, y - 5, px((250, 120, 150), 2))
        c.drawPoint(x, y, px(INK))
    elif tool == "spray":
        c.drawRect(skia.Rect.MakeXYWH(x + 2, y - 8, 4, 7), px((120, 120, 120)))
        c.drawRect(skia.Rect.MakeXYWH(x + 1, y - 10, 2, 2), px(INK))
    elif tool == "fill":
        c.drawRect(skia.Rect.MakeXYWH(x - 1, y - 8, 6, 6), px((120, 120, 120)))
        c.drawLine(x + 5, y - 3, x + 6, y, px((0, 0, 255), 1))
    else:
        pts = [(x, y), (x, y + 11), (x + 3, y + 8), (x + 5, y + 12), (x + 7, y + 11), (x + 5, y + 7), (x + 9, y + 7)]
        c.drawPath(path(pts), px(WHITE))
        c.drawPath(path(pts), px(INK, 1))


def spray(c, cx, cy, r, n, color, seed=0):
    """The spray can: n dots inside radius r, the same dots every time (so it builds up)."""
    rng = np.random.default_rng(seed)
    for _ in range(int(n)):
        a = rng.uniform(0, 2 * math.pi)
        d = r * math.sqrt(rng.uniform(0, 1))
        c.drawPoint(int(cx + d * math.cos(a)), int(cy + d * math.sin(a)), px(color))


def mspaint(draw, tool="pencil", fg=INK, title="untitled - Paint", status=None):
    """A full frame of MS Paint: draw(c) paints into the canvas area (low-res coordinates, aliased)."""
    low = np.zeros((LH, LW, 4), np.uint8)
    low[..., 3] = 255
    s = skia.Surface(low)
    c = s.getCanvas()
    paint_chrome(c, tool, fg, title=title, status=status or "For Help, click Help Topics on the Help Menu.")
    x0, y0, x1, y1 = CANVAS
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x0, y0, x1, y1))
    draw(c)
    c.restore()
    return np.ascontiguousarray(low.repeat(4, 0).repeat(4, 1))


# ------------------------------------------------------------------ PS1

PW, PH = 270, 480
BAYER = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) / 16 - 0.5)


class PS1:
    """A tiny PS1: perspective camera, vertex snapping, flat Lambert shading, painter's sort (no z-buffer),
    linear fog, then 15-bit colour with an ordered dither, shown at 4x."""

    def __init__(self, cam=(0, 3, -10), look=(0, 0, 0), fov=60, fog=(120, 170, 220), fog_near=12, fog_far=60, sky=None,
                 light=(-0.4, 0.8, -0.45)):
        self.tris = []
        self.fog, self.fog_near, self.fog_far = np.array(fog, np.float32), fog_near, fog_far
        self.sky = sky
        cam, look = np.array(cam, float), np.array(look, float)
        f = look - cam
        f /= np.linalg.norm(f)
        r = np.cross(np.array([0, 1.0, 0]), f)
        r /= np.linalg.norm(r)
        u = np.cross(f, r)
        self.cam, self.R = cam, np.stack([r, u, f])
        self.focal = (PH / 2) / math.tan(math.radians(fov / 2)) * 0.62
        L = np.array(light, float)
        self.light = L / np.linalg.norm(L)

    def tri(self, a, b, c, color, emissive=False):
        self.tris.append((np.array(a, float), np.array(b, float), np.array(c, float), color, emissive))

    def quad(self, a, b, c, d, color, emissive=False):
        self.tri(a, b, c, color, emissive)
        self.tri(a, c, d, color, emissive)

    def mesh(self, verts, faces, color, M=None, emissive=False):
        V = np.array(verts, float)
        if M is not None:
            V = V @ M[:3, :3].T + M[:3, 3]
        for f in faces:
            col = f[-1] if isinstance(f[-1], tuple) else color
            idx = [i for i in f if not isinstance(i, tuple)]
            for k in range(1, len(idx) - 1):
                self.tri(V[idx[0]], V[idx[k]], V[idx[k + 1]], col, emissive)

    def render(self, wobble_seed=0):
        img = Image.new("RGB", (PW, PH), tuple(int(v) for v in self.fog))
        d = ImageDraw.Draw(img)
        if self.sky is not None:
            for y in range(PH // 2 + 20):
                k = y / (PH / 2 + 20)
                d.line([(0, y), (PW, y)], fill=tuple(int(a + (b - a) * k) for a, b in zip(self.sky[0], self.sky[1])))
        items = []
        for a, b, cc, color, em in self.tris:
            P = np.stack([a, b, cc]) - self.cam
            Q = P @ self.R.T
            if (Q[:, 2] < 0.3).any():
                continue
            sx = PW / 2 + self.focal * Q[:, 0] / Q[:, 2]
            sy = PH / 2 - self.focal * Q[:, 1] / Q[:, 2]
            pts = [(int(round(x)), int(round(y))) for x, y in zip(sx, sy)]      # snapped to whole pixels: the wobble
            area = (pts[1][0] - pts[0][0]) * (pts[2][1] - pts[0][1]) - (pts[2][0] - pts[0][0]) * (pts[1][1] - pts[0][1])
            n = np.cross(b - a, cc - a)
            nn = np.linalg.norm(n)
            if nn < 1e-9:
                continue
            n /= nn
            if em:
                shade = 1.0
            else:
                shade = 0.35 + 0.75 * abs(float(n @ self.light))
            z = float(Q[:, 2].mean())
            fogk = min(1.0, max(0.0, (z - self.fog_near) / (self.fog_far - self.fog_near)))
            col = np.array(color, np.float32) * shade
            col = col * (1 - fogk) + self.fog * fogk
            items.append((z, pts, tuple(int(v) for v in np.clip(col, 0, 255)), area))
        items.sort(key=lambda t: -t[0])                                        # far to near: the ordering table
        for z, pts, col, area in items:
            d.polygon(pts, fill=col)
        a = np.asarray(img, np.float32)
        a = a + BAYER[np.arange(PH)[:, None] % 4, np.arange(PW)[None, :] % 4][..., None] * 8.0 * 1.6
        a = (np.clip(a, 0, 255).astype(np.uint8) >> 3) << 3                    # 15-bit colour
        return a


def rot_y(a):
    c, s = math.cos(a), math.sin(a)
    M = np.eye(4)
    M[0, 0], M[0, 2], M[2, 0], M[2, 2] = c, s, -s, c
    return M


def translate(x, y, z):
    M = np.eye(4)
    M[:3, 3] = (x, y, z)
    return M


def box(w, h, d):
    x, y, z = w / 2, h / 2, d / 2
    V = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z), (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    F = [(0, 1, 2, 3), (5, 4, 7, 6), (4, 0, 3, 7), (1, 5, 6, 2), (3, 2, 6, 7), (4, 5, 1, 0)]
    return V, F


def prism(r, h, n=8, y0=0.0):
    V = []
    for i in range(n):
        a = 2 * math.pi * i / n
        V.append((r * math.cos(a), y0, r * math.sin(a)))
    for i in range(n):
        a = 2 * math.pi * i / n
        V.append((r * math.cos(a), y0 + h, r * math.sin(a)))
    F = [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    F.append(tuple(range(n + n - 1, n - 1, -1)))
    return V, F


def upscale(a, k=4):
    return np.ascontiguousarray(a.repeat(k, 0).repeat(k, 1))

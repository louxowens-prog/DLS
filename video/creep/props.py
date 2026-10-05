"""Props and practical effects, all original: the AI spotter box with its one red eye, a scope monitor and the growth
it finds, the assistant's phone, a dashboard GPS, a laptop, a skull in a blonde wig, the paper ghost writer, the latex
growth creature, a calculator, a pill bottle, a phone keypad, a candle, maps, a brain."""
import math

import numpy as np
import skia

import comic as CO
import face as FA
import kit as K
from kit import INK, WHITE, mix, paint, path, smooth

BEIGE, BEIGE_D = (214, 200, 168), (150, 136, 108)


def _rr(x0, y0, x1, y1, r):
    return K.rrect(x0, y0, x1, y1, r)


def plastic(c, p, base, L, a=1.0):
    FA.lit_fill(c, p, base, L, rim=0.9, rim_w=5, a=a, edge=0.5)


# ------------------------------------------------------------------ the AI spotter: a beige box with one red eye

def eyebox(c, x, y, s, T, on=1.0, look=(0.0, 0.0), light="clinic", label="SPOTTER", blink=0.0):
    """The thing in the box: a 1982 beige machine whose single lens glows red when it is on."""
    L = FA.Light(light)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    body = _rr(-170, -120, 170, 120, 18)
    c.drawRect(skia.Rect.MakeLTRB(-150, 110, 150, 150), paint(INK, 0.5, blur=14))
    plastic(c, body, BEIGE, L)
    for i in range(6):                                                  # a vent grille
        c.drawRoundRect(skia.Rect.MakeLTRB(80, -90 + i * 16, 150, -82 + i * 16), 3, 3, paint(mix(BEIGE_D, INK, 0.4), 0.8))
    c.drawRoundRect(skia.Rect.MakeLTRB(-150, 80, -40, 104), 4, 4, paint((40, 36, 30)))
    f = K.font("bangers-400", 22)
    c.drawString(label, -142, 100, f, paint((230, 220, 190)))
    K.reg_local(c, -142, 80, -142 + f.measureText(label), 104, "deco")
    led = (60, 255, 80) if on > 0.5 else (40, 60, 40)
    c.drawCircle(130, 92, 7, paint(led))
    if on > 0.5:
        g = paint(led, 0.8, blur=8)
        g.setBlendMode(skia.BlendMode.kPlus)
        c.drawCircle(130, 92, 10, g)
    # the lens
    c.drawCircle(-20, -10, 92, paint((30, 28, 26)))
    c.drawCircle(-20, -10, 92, paint(mix(BEIGE_D, INK, 0.5), stroke=8))
    c.drawCircle(-20, -10, 74, paint((12, 10, 12)))
    op = max(0.0, 1 - blink)
    lx, ly = -20 + look[0] * 16, -10 + look[1] * 12
    if on > 0.02:
        iris = (230, 20, 20)
        c.save()
        c.clipPath(K.oval(-94, -84 + (1 - op) * 74, 54, 64 - (1 - op) * 74), doAntiAlias=True)
        c.drawCircle(lx, ly, 52, paint(shader=K.rad((lx, ly), 52, [(255, 120, 80), iris, (90, 0, 10)], [0, 0.5, 1]), a=on))
        for i in range(18):                                             # iris fibres
            a = 2 * math.pi * i / 18
            c.drawLine(lx + 16 * math.cos(a), ly + 16 * math.sin(a), lx + 50 * math.cos(a), ly + 50 * math.sin(a), paint((120, 0, 10), 0.5 * on, stroke=2))
        c.drawCircle(lx, ly, 18, paint(INK, on))
        c.restore()
        g = paint((255, 40, 30), 0.65 * on, blur=36)
        g.setBlendMode(skia.BlendMode.kPlus)
        c.drawCircle(lx, ly, 70, g)
    else:
        c.drawCircle(lx, ly, 52, paint((40, 40, 44)))
        c.drawCircle(lx, ly, 18, paint((20, 20, 22)))
    c.drawOval(skia.Rect.MakeLTRB(-70, -70, -20, -40), paint(WHITE, 0.35, blur=4))
    c.restore()


# ------------------------------------------------------------------ the scope monitor

def tunnel(c, x0, y0, x1, y1, T, seed=0, flesh=(226, 110, 116)):
    """An endoscope's view: a wet pink tunnel of folds running into the dark."""
    cx, cy = (x0 + x1) / 2 + 10 * math.sin(T * 0.7), (y0 + y1) / 2 + 8 * math.sin(T * 0.9)
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x0, y0, x1, y1))
    c.drawColor(K.col(mix(flesh, INK, 0.5)))
    w, h = x1 - x0, y1 - y0
    for i in range(9, 0, -1):
        k = i / 9
        rx, ry = w * 0.75 * k, h * 0.7 * k
        wob = 0.06 * math.sin(T * 1.3 + i)
        pts = [(cx + rx * (1 + wob * math.sin(a * 3 + i)) * math.cos(a), cy + ry * (1 + wob * math.cos(a * 2 + i)) * math.sin(a))
               for a in np.linspace(0, 2 * math.pi, 28, endpoint=False)]
        p = smooth(pts)
        col_ = mix(mix(flesh, INK, 0.75), flesh, k ** 0.7)
        c.drawPath(p, paint(col_))
        c.drawPath(p, paint(mix(flesh, INK, 0.45), 0.6, stroke=6 * k + 1, blur=3))
        hx, hy = cx - rx * 0.5, cy - ry * 0.7
        c.drawOval(skia.Rect.MakeXYWH(hx, hy, rx * 0.3, ry * 0.08), paint(WHITE, 0.35 * k, blur=3))
    c.drawCircle(cx, cy, w * 0.06, paint((10, 0, 4), 0.9, blur=10))
    c.restore()
    return cx, cy


def growth(c, x, y, r, T, eye=0.0, grin=0.0, a=1.0, flesh=(240, 150, 140)):
    """A polyp on the tunnel wall: a glossy bulb that, when nobody is looking, opens an eye."""
    p = smooth([(x - r, y + r * 0.4), (x - r * 0.9, y - r * 0.4), (x - r * 0.3, y - r), (x + r * 0.4, y - r * 0.9), (x + r, y - r * 0.2), (x + r * 0.9, y + r * 0.5)])
    c.drawPath(p, paint(shader=K.rad((x - r * 0.3, y - r * 0.4), r * 1.6, [mix(flesh, WHITE, 0.3), flesh, mix(flesh, (120, 20, 40), 0.6)]), a=a))
    c.drawPath(p, paint((120, 30, 40), 0.6 * a, stroke=2))
    c.save()
    c.clipPath(p, doAntiAlias=True)
    rng = K.rng_at(int(r), 3)
    for i in range(int(r * 1.2)):                                       # latex pores
        c.drawCircle(x + rng.uniform(-r, r), y + rng.uniform(-r, r), rng.uniform(0.8, 2.4), paint((120, 30, 50), 0.3 * a))
    c.restore()
    for i in range(3):                                                  # veins
        c.drawPath(K.bez_path([(x - r * 0.6 + i * r * 0.4, y + r * 0.3), (x - r * 0.4 + i * r * 0.5, y - r * 0.2), (x - r * 0.2 + i * r * 0.4, y - r * 0.6)]),
                   paint((150, 40, 80), 0.5 * a, stroke=1.6))
    c.drawOval(skia.Rect.MakeXYWH(x - r * 0.5, y - r * 0.8, r * 0.4, r * 0.2), paint(WHITE, 0.6 * a, blur=2))
    if eye > 0.02:
        ew, eh = r * 0.42, r * 0.26 * eye
        c.drawOval(skia.Rect.MakeLTRB(x - ew, y - r * 0.2 - eh, x + ew, y - r * 0.2 + eh), paint((250, 240, 160), a))
        c.drawOval(skia.Rect.MakeLTRB(x - 4, y - r * 0.2 - eh * 0.9, x + 4, y - r * 0.2 + eh * 0.9), paint(INK, a))
        c.drawOval(skia.Rect.MakeLTRB(x - ew, y - r * 0.2 - eh, x + ew, y - r * 0.2 + eh), paint((120, 30, 40), a, stroke=2))
    if grin > 0.02:
        m = K.bez_path([(x - r * 0.5, y + r * 0.15), (x, y + r * 0.15 + r * 0.35 * grin), (x + r * 0.55, y + r * 0.05)])
        c.drawPath(m, paint((60, 0, 10), a, stroke=4))
        for i in range(5):
            u = i / 4
            tx = x - r * 0.45 + r * 0.95 * u
            ty = y + r * 0.15 + r * 0.33 * grin * math.sin(math.pi * u) - 2
            c.drawPath(path([(tx - 4, ty), (tx + 4, ty), (tx, ty + 9 * grin)]), paint((250, 246, 220), a))


def monitor(c, x, y, s, T, draw_screen, light="clinic", casing=BEIGE):
    """A 1982 CRT monitor on a stand; draw_screen(c, x0, y0, x1, y1) paints the picture."""
    L = FA.Light(light)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawRect(skia.Rect.MakeLTRB(-60, 230, 60, 330), paint(mix(casing, INK, 0.4)))
    body = _rr(-260, -220, 260, 240, 26)
    c.drawRect(skia.Rect.MakeLTRB(-240, 230, 240, 270), paint(INK, 0.5, blur=14))
    plastic(c, body, casing, L)
    c.drawRoundRect(skia.Rect.MakeLTRB(-226, -190, 226, 180), 40, 40, paint((16, 14, 14)))
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-212, -176, 212, 166), 46, 46), doAntiAlias=True)
    draw_screen(c, -212, -176, 212, 166)
    for yy in range(-176, 166, 5):                                       # scan lines
        c.drawLine(-212, yy, 212, yy, paint(INK, 0.12, stroke=2))
    c.drawRect(skia.Rect.MakeLTRB(-212, -176, 212, 166), paint(shader=K.rad((0, 0), 300, [(255, 255, 255, 0.0), (0, 0, 0, 0.0), (0, 0, 0, 0.55)], [0, 0.6, 1])))
    c.drawOval(skia.Rect.MakeLTRB(-180, -160, 40, -90), paint(WHITE, 0.08, blur=10))
    c.restore()
    for i, kx in enumerate((-180, -140)):
        c.drawCircle(kx, 212, 10, paint(mix(casing, INK, 0.5)))
    c.restore()


def detect_box(c, x, y, r, T, a=1.0, label="GROWTH"):
    """The spotter's green box round what it found, with a tag."""
    if a <= 0.01:
        return
    g = (60, 255, 90)
    k = 1 + 0.06 * math.sin(T * 12)
    rr = r * 1.4 * k
    c.drawRect(skia.Rect.MakeLTRB(x - rr, y - rr, x + rr, y + rr), paint(g, a, stroke=4))
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        c.drawLine(x + sx * rr, y + sy * rr, x + sx * rr * 0.6, y + sy * rr, paint(g, a, stroke=9))
        c.drawLine(x + sx * rr, y + sy * rr, x + sx * rr, y + sy * rr * 0.6, paint(g, a, stroke=9))
    f = K.font("vt323-400", 30)
    c.drawRect(skia.Rect.MakeLTRB(x - rr, y - rr - 32, x - rr + f.measureText(label) + 14, y - rr), paint(g, a))
    c.drawString(label, x - rr + 7, y - rr - 7, f, paint(INK, a))
    K.reg_local(c, x - rr, y - rr - 32, x - rr + f.measureText(label) + 14, y - rr, "screen")


# ------------------------------------------------------------------ the assistant

def phone(c, x, y, s, ang, T, screen="muse", level=0.0, glow=1.0, pct="1%"):
    """A phone. screen: 'muse' (a glowing ring that pulses as it speaks), 'battery' (a red 1%), 'dead' (black glass)."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    c.drawRoundRect(skia.Rect.MakeLTRB(-96, -190, 104, 202), 30, 30, paint(INK, 0.5, blur=12))
    c.drawRoundRect(skia.Rect.MakeLTRB(-100, -200, 100, 200), 30, 30, paint((24, 24, 28)))
    c.drawRoundRect(skia.Rect.MakeLTRB(-100, -200, 100, 200), 30, 30, paint((90, 90, 100), stroke=4))
    sc = skia.Rect.MakeLTRB(-88, -186, 88, 186)
    if screen == "muse":
        c.drawRoundRect(sc, 22, 22, paint(shader=K.lin((0, -186), (0, 186), [(10, 30, 90), (4, 8, 30)])))
        r = 52 + 10 * level
        g = paint((90, 200, 255), 0.7 * glow, blur=18 + 10 * level)
        g.setBlendMode(skia.BlendMode.kPlus)
        c.drawCircle(0, -10, r + 10, g)
        c.drawCircle(0, -10, r, paint((140, 230, 255), glow, stroke=10))
        c.drawCircle(0, -10, r * 0.55, paint((200, 245, 255), 0.6 * glow, stroke=4))
        f = K.font("vt323-400", 40)
        c.drawString("MUSE", -f.measureText("MUSE") / 2, 120, f, paint((150, 220, 255), glow))
        K.reg_local(c, -50, 90, 50, 130, "deco")
    elif screen == "battery":
        c.drawRoundRect(sc, 22, 22, paint((6, 6, 8)))
        c.drawRoundRect(skia.Rect.MakeLTRB(-50, -60, 44, 0), 8, 8, paint((230, 40, 40), glow, stroke=6))
        c.drawRect(skia.Rect.MakeLTRB(44, -42, 54, -18), paint((230, 40, 40), glow))
        c.drawRect(skia.Rect.MakeLTRB(-42, -52, -32, -8), paint((230, 40, 40), glow))
        f = K.font("rubik-700", 52)
        c.drawString(pct, -f.measureText(pct) / 2, 80, f, paint((230, 60, 60), glow))
        K.reg_local(c, -f.measureText(pct) / 2, 40, f.measureText(pct) / 2, 90, "screen")
    else:
        c.drawRoundRect(sc, 22, 22, paint((4, 4, 6)))
        c.drawPath(path([(-88, -186), (10, -186), (-88, 40)]), paint(WHITE, 0.05))
    c.restore()


# ------------------------------------------------------------------ the car

def gps(c, x, y, s, T, mode="route", k=1.0):
    """A dashboard sat-nav: a route and an arrow; 'lost' flashes SIGNAL LOST; 'recalc' spins forever."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawRoundRect(skia.Rect.MakeLTRB(-170, -110, 170, 110), 18, 18, paint((20, 20, 24)))
    c.drawRoundRect(skia.Rect.MakeLTRB(-170, -110, 170, 110), 18, 18, paint((70, 70, 80), stroke=4))
    scr = skia.Rect.MakeLTRB(-152, -94, 152, 94)
    c.save()
    c.clipRect(scr)
    if mode == "route":
        c.drawRect(scr, paint((20, 60, 50)))
        for i in range(7):
            c.drawLine(-160 + i * 56, -100, -120 + i * 56, 100, paint((40, 100, 80), stroke=6))
        c.drawPath(K.bez_path([(0, 100), (0, 0), (-150, -30)]), paint((90, 220, 255), stroke=14))
        c.drawPath(path([(-30, 20), (0, -14), (30, 20), (0, 8)]), paint((255, 220, 60)))
        f = K.font("vt323-400", 34)
        c.drawString("200 FT  TURN LEFT", -140, -60, f, paint(WHITE))
        K.reg_local(c, -140, -86, 140, -56, "screen")
    elif mode == "lost":
        on = (math.floor(T * 4) % 2) == 0
        c.drawRect(scr, paint((60, 0, 0) if on else (16, 0, 0)))
        f = K.font("vt323-400", 54)
        for i, ln in enumerate(("SIGNAL", "LOST")):
            c.drawString(ln, -f.measureText(ln) / 2, -10 + i * 52, f, paint((255, 60, 60) if on else (140, 20, 20)))
        K.reg_local(c, -110, -50, 110, 50, "screen")
    else:
        c.drawRect(scr, paint((10, 20, 30)))
        f = K.font("vt323-400", 34)
        s_ = "RECALCULATING" + "." * (int(T * 3) % 4)
        c.drawString(s_, -136, 64, f, paint((150, 220, 255)))
        K.reg_local(c, -136, 38, 136, 68, "screen")
        for i in range(10):
            a = 2 * math.pi * i / 10 + T * 4
            c.drawCircle(40 * math.cos(a), -20 + 40 * math.sin(a), 7, paint((150, 220, 255), 0.2 + 0.08 * i))
    c.restore()
    c.restore()


def wheel(c, x, y, s, ang=0.0, color=(30, 28, 30), L="dash"):
    L = FA.Light(L)
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    ring = skia.Path()
    ring.addCircle(0, 0, 300)
    inner = skia.Path()
    inner.addCircle(0, 0, 262)
    ring = skia.Op(ring, inner, skia.PathOp.kDifference_PathOp)
    FA.lit_fill(c, ring, color, L, rim=1.0, rim_w=6)
    for a in (200, 340, 90):
        t = math.radians(a)
        sp = K.capsule(0, 0, 270 * math.cos(t), 270 * math.sin(t), 60, 40)
        FA.lit_fill(c, sp, color, L, rim=0.8, rim_w=5)
    FA.lit_fill(c, K.circle(0, 0, 90), mix(color, (60, 60, 70), 0.3), L, rim=0.8, rim_w=5)
    c.restore()


# ------------------------------------------------------------------ the dead

def skull(c, x, y, s, T, jaw=0.0, turn=0.0, light="green", hair=True, pearls=True, cobweb=True):
    """Vera, fifteen years on: a skull in her big blonde hair and pearls. jaw 0..1 drops the jaw."""
    L = FA.Light(light)
    P = dict(FA.CAST["vera"])
    P["hair"] = (210, 190, 120)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    bone = (226, 214, 180)
    if hair:
        FA._hair_back(c, P, L, T, turn)
    # neck vertebrae, collar bones
    for i in range(4):
        FA.lit_fill(c, _rr(-26, 120 + i * 36, 26, 146 + i * 36, 10), bone, L, rim=0.7, rim_w=4)
    fx = turn * 30
    cran = smooth([(0, -160), (80, -146), (118, -86), (120, -10), (100, 50), (70, 76), (40, 96), (-40, 96), (-70, 76), (-100, 50), (-120, -10),
                   (-118, -86), (-80, -146)])
    FA.lit_fill(c, cran, bone, L, rim=1.0, rim_w=6, round_=True)
    for sx in (-1, 1):                                                  # sockets
        sock = smooth([(fx + sx * 14, -36), (fx + sx * 40, -54), (fx + sx * 72, -38), (fx + sx * 70, 4), (fx + sx * 44, 14), (fx + sx * 16, 2)])
        c.drawPath(sock, paint((20, 10, 8)))
        g = paint((120, 255, 120), 0.35, blur=10)
        g.setBlendMode(skia.BlendMode.kPlus)
        c.drawCircle(fx + sx * 42, -20, 10, g)
    nose = path([(fx, 18), (fx - 14, 50), (fx + 14, 50)])
    c.drawPath(nose, paint((20, 10, 8)))
    c.drawPath(K.bez_path([(-100 + fx, -10), (-60 + fx, 20), (-62 + fx, 70)]), paint(mix(bone, INK, 0.4), 0.5, stroke=3))
    c.drawPath(K.bez_path([(100 + fx, -10), (60 + fx, 20), (62 + fx, 70)]), paint(mix(bone, INK, 0.4), 0.5, stroke=3))
    for i in range(8):                                                  # upper teeth
        tx = fx - 42 + i * 12
        c.drawRoundRect(skia.Rect.MakeLTRB(tx, 70, tx + 10, 96), 3, 3, paint((236, 226, 196)))
        c.drawRoundRect(skia.Rect.MakeLTRB(tx, 70, tx + 10, 96), 3, 3, paint(INK, 0.5, stroke=1.4))
    dj = jaw * 70
    mand = smooth([(-74, 90 + dj * 0.4), (-70, 130 + dj), (-30, 160 + dj), (30, 160 + dj), (70, 130 + dj), (74, 90 + dj * 0.4), (40, 104 + dj), (-40, 104 + dj)])
    if jaw > 0.05:
        c.drawPath(path([(-50, 96), (50, 96), (40, 104 + dj), (-40, 104 + dj)]), paint((14, 4, 4)))
    FA.lit_fill(c, mand, bone, L, rim=0.8, rim_w=5)
    for i in range(7):
        tx = fx - 36 + i * 12
        c.drawRoundRect(skia.Rect.MakeLTRB(tx, 98 + dj, tx + 10, 120 + dj), 3, 3, paint((236, 226, 196)))
        c.drawRoundRect(skia.Rect.MakeLTRB(tx, 98 + dj, tx + 10, 120 + dj), 3, 3, paint(INK, 0.5, stroke=1.4))
    if hair:
        FA._hair_front(c, P, L, T, turn, fx)
    if cobweb:
        CO.cobweb(c, -150, -200, 170, 20, 70, a=0.7, seed=3)
    if pearls:
        for i in range(17):
            u = i / 16
            px, py = -80 + 160 * u, 250 + 50 * math.sin(math.pi * u)
            c.drawCircle(px, py, 10, paint((236, 230, 220)))
            c.drawCircle(px - 3, py - 3, 3, paint(WHITE, 0.9))
    c.restore()


# ------------------------------------------------------------------ the ghost writer

def ghost(c, x, y, s, T, a=1.0, mouth=0.3, reach=0.0, light="screen", tail_to=None, writing=True):
    """The ghost writer: a creature of crumpled typed pages with ink-blot eyes, a ragged mouth and pen-nib claws.
    tail_to: where its tail of paper pours from (the laptop screen)."""
    L = FA.Light(light)
    paper = (238, 234, 218)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    sway = math.sin(T * 2.2) * 14
    tx, ty = (tail_to if tail_to is not None else (x, y + 520 * s))
    tx, ty = (tx - x) / s, (ty - y) / s
    body = smooth([(-150, -170), (-60, -250), (60, -252), (150, -170), (180, -20), (150, 140), (90 + sway, 300), (tx * 0.5 + 40 + sway, ty * 0.6),
                   (tx + 30, ty), (tx - 30, ty), (tx * 0.5 - 40 + sway, ty * 0.6), (-90 + sway, 300), (-150, 140), (-180, -20)])
    c.drawPath(body, paint(INK, 0.4 * a, blur=20))
    FA.lit_fill(c, body, paper, L, rim=1.0, rim_w=8, a=a, round_=True)
    c.save()
    c.clipPath(body, doAntiAlias=True)
    rng = K.rng_at(4, 4)
    for i in range(30):                                                 # creases and typed lines
        y0 = -230 + i * 26
        c.drawLine(-140, y0, 140, y0 + rng.uniform(-6, 6), paint((70, 70, 80), 0.35 * a, stroke=3))
        x0 = rng.uniform(-140, 60)
        c.drawLine(x0, y0 + 10, x0 + rng.uniform(40, 120), y0 + 10, paint((60, 60, 70), 0.3 * a, stroke=5))
    for i in range(8):
        c.drawPath(K.bez_path([(rng.uniform(-150, 150), rng.uniform(-240, 200)), (rng.uniform(-150, 150), rng.uniform(-240, 200)),
                               (rng.uniform(-150, 150), rng.uniform(-240, 200))]), paint(mix(paper, INK, 0.4), 0.35 * a, stroke=3))
    c.restore()
    # ink-blot eyes that drip
    for sx in (-1, 1):
        ex, ey = sx * 60, -120
        blot = smooth([(ex - 34, ey), (ex - 20, ey - 30), (ex + 18, ey - 32), (ex + 36, ey - 4), (ex + 24, ey + 26), (ex - 22, ey + 24)])
        c.drawPath(blot, paint((8, 8, 16), a))
        c.drawPath(K.capsule(ex - 10, ey + 20, ex - 12, ey + 60 + 10 * math.sin(T * 2 + sx), 10, 6), paint((8, 8, 16), a))
        c.drawCircle(ex + 6, ey - 8, 7, paint((255, 255, 255), 0.8 * a))
    mh = 20 + 50 * mouth
    m = smooth([(-70, -10), (0, -20), (70, -10), (40, mh), (0, mh + 10), (-40, mh)])
    c.drawPath(m, paint((10, 6, 12), a))
    for i in range(7):                                                  # teeth: type slugs
        u = i / 6
        x0 = -60 + 120 * u
        c.drawRect(skia.Rect.MakeLTRB(x0 - 7, -14, x0 + 7, 6), paint((210, 210, 200), a))
        f = K.font("special-elite-400", 16)
        c.drawString("ETAOIN"[i % 6], x0 - 5, 2, f, paint(INK, a))
    # arms: paper strips with pen-nib claws
    for sx in (-1, 1):
        ax0, ay0 = sx * 150, -40
        ax1, ay1 = sx * (230 + 60 * reach), 80 - 120 * reach + math.sin(T * 3 + sx) * 10
        armp = K.capsule(ax0, ay0, ax1, ay1, 46, 22)
        FA.lit_fill(c, armp, paper, L, rim=0.8, rim_w=5, a=a)
        for j in range(3):
            ang = math.atan2(ay1 - ay0, ax1 - ax0) + (j - 1) * 0.35
            nx, ny = ax1 + 60 * math.cos(ang), ay1 + 60 * math.sin(ang)
            nib = path([(ax1 + 8 * math.sin(ang), ay1 - 8 * math.cos(ang)), (nx, ny), (ax1 - 8 * math.sin(ang), ay1 + 8 * math.cos(ang))])
            c.drawPath(nib, paint((40, 40, 50), a))
            c.drawLine(ax1, ay1, (ax1 + nx) / 2, (ay1 + ny) / 2, paint((200, 200, 210), 0.7 * a, stroke=2))
    c.restore()


# ------------------------------------------------------------------ the growth, grown

def thing(c, x, y, s, T, open_=1.0, light="red", lunge=0.0):
    """The latex growth creature: a glistening fleshy mass with too many eyes, needle teeth, slime and tendrils."""
    L = FA.Light(light)
    flesh = (214, 110, 140)
    c.save()
    c.translate(x, y)
    c.scale(s * (1 + 0.35 * lunge), s * (1 + 0.35 * lunge))
    wob = math.floor(T * 12) / 12
    for i in range(7):                                                  # tendrils
        a = -math.pi * 0.1 - i * math.pi * 0.13
        L0 = 260 + 30 * math.sin(wob * 3 + i)
        pts = [(math.cos(a) * 140, math.sin(a) * 120)]
        for j in range(1, 6):
            r = 140 + L0 * j / 5
            pts.append((math.cos(a + 0.2 * math.sin(wob * 4 + i + j)) * r, math.sin(a + 0.2 * math.sin(wob * 4 + i + j)) * r * 0.9 + j * 10))
        for side in (1, -1):
            q = [(px * side, py) for px, py in pts]
            p = path(q, closed=False)
            c.drawPath(p, paint(mix(flesh, INK, 0.5), stroke=30))
            c.drawPath(p, paint(flesh, stroke=20))
            c.drawPath(p, paint(WHITE, 0.3, stroke=4))
    pts = []
    for i in range(22):
        a = 2 * math.pi * i / 22
        r = 210 * (1 + 0.1 * math.sin(i * 2.7 + wob * 6))
        pts.append((r * math.cos(a), r * 0.86 * math.sin(a)))
    body = smooth(pts)
    FA.lit_fill(c, body, flesh, L, rim=1.0, rim_w=10, round_=True, edge=0.6)
    c.save()
    c.clipPath(body, doAntiAlias=True)
    rng = K.rng_at(9, 9)
    for i in range(160):                                                # rubbery latex: pores and blotches
        px, py = rng.uniform(-220, 220), rng.uniform(-200, 200)
        c.drawCircle(px, py, rng.uniform(1.5, 5), paint((90, 20, 50) if i % 3 else (255, 210, 220), rng.uniform(0.15, 0.45)))
    for i in range(10):                                                 # wet streaks of slime
        px, py = rng.uniform(-180, 160), rng.uniform(-170, 120)
        c.drawPath(K.bez_path([(px, py), (px + 30, py + 10), (px + 60, py + rng.uniform(-10, 30))]), paint(WHITE, 0.4, stroke=rng.uniform(2, 5), blur=1))
    for i in range(14):                                                 # veins and lumps
        x0, y0 = rng.uniform(-200, 200), rng.uniform(-180, 180)
        c.drawPath(K.bez_path([(x0, y0), (x0 + rng.uniform(-60, 60), y0 + rng.uniform(-60, 60)), (x0 + rng.uniform(-90, 90), y0 + rng.uniform(-90, 90))]),
                   paint((120, 30, 90), 0.6, stroke=rng.uniform(2, 5)))
        c.drawCircle(rng.uniform(-200, 200), rng.uniform(-180, 180), rng.uniform(12, 30), paint(mix(flesh, WHITE, 0.2), 0.35, blur=6))
    c.restore()
    for (ex, ey, er) in ((-90, -90, 34), (40, -120, 26), (110, -50, 20), (-140, 10, 16), (0, -40, 44)):   # eyes
        c.drawCircle(ex, ey, er, paint((250, 240, 170)))
        lk = math.sin(wob * 2 + ex) * er * 0.25
        c.drawOval(skia.Rect.MakeLTRB(ex + lk - er * 0.2, ey - er * 0.85, ex + lk + er * 0.2, ey + er * 0.85), paint(INK))
        c.drawCircle(ex, ey, er, paint((120, 20, 50), stroke=4))
        c.drawCircle(ex - er * 0.35, ey - er * 0.35, er * 0.18, paint(WHITE, 0.9))
    mo = 30 + 110 * open_
    mouth = smooth([(-130, 50), (-60, 40 - mo * 0.2), (60, 40 - mo * 0.2), (130, 50), (80, 60 + mo), (0, 70 + mo), (-80, 60 + mo)])
    c.drawPath(mouth, paint((50, 0, 12)))
    c.save()
    c.clipPath(mouth, doAntiAlias=True)
    c.drawOval(skia.Rect.MakeLTRB(-60, 60, 60, 80 + mo), paint((150, 10, 30)))
    c.restore()
    for i in range(12):                                                 # needle teeth, top and bottom
        u = i / 11
        tx = -120 + 240 * u
        ty = 46 - mo * 0.2 * math.sin(math.pi * u)
        c.drawPath(path([(tx - 7, ty - 4), (tx + 7, ty - 4), (tx, ty + 30 + 10 * (i % 2))]), paint((246, 240, 214)))
        by = 62 + mo * math.sin(math.pi * u) * 0.9 + 8
        c.drawPath(path([(tx - 6, by + 4), (tx + 6, by + 4), (tx, by - 24)]), paint((246, 240, 214)))
    for i in range(4):                                                  # slime strings
        sx = -90 + i * 60
        c.drawPath(K.bez_path([(sx, 50), (sx + 6, 60 + mo * 0.5), (sx - 4, 60 + mo)]), paint((240, 200, 210), 0.5, stroke=3))
    c.drawOval(skia.Rect.MakeLTRB(-150, -170, -60, -140), paint(WHITE, 0.45, blur=4))
    c.restore()


# ------------------------------------------------------------------ everyday things

def calculator(c, x, y, s, T, display="0.", L="lamp", ang=0.0):
    L = FA.Light(L)
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    plastic(c, _rr(-130, -200, 130, 200, 18), (60, 56, 60), L)
    c.drawRoundRect(skia.Rect.MakeLTRB(-110, -180, 110, -100), 8, 8, paint((20, 6, 6)))
    f = K.font("vt323-400", 70)
    c.drawString(display, 100 - f.measureText(display), -118, f, paint((255, 50, 40)))
    g = paint((255, 40, 30), 0.5, blur=8)
    c.drawString(display, 100 - f.measureText(display), -118, f, g)
    K.reg_local(c, 100 - f.measureText(display), -170, 100, -110, "screen")
    for r in range(4):
        for q in range(4):
            bx, by = -100 + q * 52, -80 + r * 66
            c.drawRoundRect(skia.Rect.MakeLTRB(bx, by, bx + 42, by + 50), 8, 8, paint((200, 196, 186) if q < 3 else (230, 120, 40)))
    c.restore()


def pill_bottle(c, x, y, s, label=("HEART TABLETS", "Dose: 0.125 mg", "Each tablet: 0.25 mg"), L="candle", ang=0.0):
    L = FA.Light(L)
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    plastic(c, _rr(-110, -200, 110, 220, 22), (210, 120, 40), L)
    plastic(c, _rr(-124, -260, 124, -190, 14), (236, 236, 230), L)
    c.drawRect(skia.Rect.MakeLTRB(-100, -130, 100, 150), paint((246, 244, 236)))
    for i, (ln, sz) in enumerate(zip(label, (30, 34, 34))):
        f = K.font("rubik-700" if i else "rubik-900", sz)
        c.drawString(ln, -f.measureText(ln) / 2, -80 + i * 70, f, paint(INK))
        K.reg_local(c, -f.measureText(ln) / 2, -80 + i * 70 - sz * 0.8, f.measureText(ln) / 2, -80 + i * 70 + sz * 0.2, "screen")
    c.restore()


def candle(c, x, y, s, T, a=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    g = paint((255, 170, 80), 0.35 * a, blur=60)
    g.setBlendMode(skia.BlendMode.kPlus)
    c.drawCircle(0, -150, 160, g)
    c.drawRoundRect(skia.Rect.MakeLTRB(-30, -120, 30, 120), 8, 8, paint((236, 226, 200)))
    c.drawRoundRect(skia.Rect.MakeLTRB(-30, -120, 30, 120), 8, 8, paint(shader=K.lin((-30, 0), (30, 0), [(255, 230, 190, 0.0), (0, 0, 0, 0.45)])))
    fl = 1 + 0.1 * math.sin(T * 17) + 0.05 * math.sin(T * 31)
    flame = smooth([(0, -200 * fl), (14, -150), (10, -128), (0, -122), (-10, -128), (-14, -150)])
    c.drawPath(flame, paint((255, 200, 90), a))
    c.drawPath(smooth([(0, -170 * fl), (7, -140), (0, -128), (-7, -140)]), paint((255, 250, 220), a))
    c.drawLine(0, -122, 0, -130, paint(INK, stroke=3))
    c.restore()


def keypad(c, x, y, s, typed="07", L="plain", status=None):
    """A handset's keypad and its little green display (status: a line of small text above the digits)."""
    L = FA.Light(L)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    plastic(c, _rr(-200, -330, 200, 330, 30), (200, 196, 186), L)
    c.drawRoundRect(skia.Rect.MakeLTRB(-170, -300, 170, -190), 10, 10, paint((150, 170, 140)))
    f = K.font("vt323-400", 80 if status is None else 64)
    s_ = typed + "_"
    c.drawString(s_, -150, -205 if status else -218, f, paint((30, 40, 30)))
    K.reg_local(c, -150, -255 if status else -282, -150 + f.measureText(s_), -200, "screen")
    if status:
        fs = K.font("vt323-400", 40)
        c.drawString(status, -150, -258, fs, paint((120, 20, 20)))
        K.reg_local(c, -150, -290, -150 + fs.measureText(status), -252, "screen")
    keys = "123456789*0#"
    fk = K.font("rubik-700", 46)
    for i, ch in enumerate(keys):
        bx, by = -150 + (i % 3) * 110, -160 + (i // 3) * 118
        c.drawRoundRect(skia.Rect.MakeLTRB(bx, by, bx + 90, by + 96), 16, 16, paint((236, 234, 226)))
        c.drawRoundRect(skia.Rect.MakeLTRB(bx, by, bx + 90, by + 96), 16, 16, paint(INK, 0.4, stroke=3))
        c.drawString(ch, bx + 45 - fk.measureText(ch) / 2, by + 64, fk, paint(INK))
        K.reg_local(c, bx + 20, by + 24, bx + 70, by + 70, "screen")
    c.restore()


def brain(c, x, y, s, T, glow=0.0, grow=1.0, shrink=0.0):
    """A brain in profile with the hippocampus - the seahorse-shaped map-keeper - lit up (glow) and grown (grow)."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    pts = [(-220, 20), (-200, -100), (-120, -180), (0, -200), (120, -180), (210, -100), (230, 10), (190, 90), (100, 120), (40, 110), (0, 160),
           (-60, 110), (-170, 100)]
    p = smooth(pts)
    c.drawPath(p, paint((236, 170, 176)))
    c.save()
    c.clipPath(p, doAntiAlias=True)
    rng = K.rng_at(3, 1)
    for i in range(26):
        x0, y0 = rng.uniform(-220, 220), rng.uniform(-200, 120)
        c.drawPath(K.bez_path([(x0, y0), (x0 + rng.uniform(-50, 50), y0 + rng.uniform(-40, 40)), (x0 + rng.uniform(-60, 60), y0 + rng.uniform(-60, 60))]),
                   paint((170, 90, 110), 0.8, stroke=5))
    c.restore()
    c.drawPath(p, paint(INK, stroke=6))
    hs = grow * (1 - 0.45 * shrink)
    c.save()
    c.translate(40, 40)
    c.scale(hs, hs)
    sea = smooth([(-60, 0), (-40, -30), (0, -40), (40, -26), (60, 0), (50, 30), (30, 20), (10, 40), (-10, 60), (-30, 40), (-40, 20)])
    if glow > 0:
        g = paint((255, 220, 80), 0.7 * glow, blur=30)
        g.setBlendMode(skia.BlendMode.kPlus)
        c.drawPath(sea, g)
    c.drawPath(sea, paint(mix((240, 120, 60), (255, 230, 90), glow)))
    c.drawPath(sea, paint(INK, stroke=4))
    c.restore()
    c.restore()


def laptop(c, x, y, s, T, prog=0.0, glow=1.0, L="screen", screen=(40, 70, 140)):
    """An open laptop seen from behind the user's shoulder: a glowing page filling with lines as the ghost types."""
    L = FA.Light(L)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    base = path([(-300, 200), (300, 200), (360, 280), (-360, 280)])
    FA.lit_fill(c, base, (70, 70, 80), L, rim=0.8, rim_w=5)
    lid = _rr(-290, -200, 290, 200, 16)
    c.drawPath(lid, paint((30, 30, 36)))
    sc = skia.Rect.MakeLTRB(-268, -180, 268, 180)
    c.drawRect(sc, paint(mix(screen, WHITE, 0.15 * glow)))
    c.drawRect(skia.Rect.MakeLTRB(-200, -160, 200, 180), paint((246, 246, 240), glow))
    n = int(16 * prog)
    for i in range(n):
        w = 340 if i % 5 != 4 else 180
        c.drawLine(-170, -130 + i * 19, -170 + w, -130 + i * 19, paint((60, 60, 80), 0.8 * glow, stroke=6))
    if n < 16 and prog > 0:
        cx = -170 + (340 * ((T * 3) % 1))
        c.drawRect(skia.Rect.MakeLTRB(cx, -138 + n * 19, cx + 4, -122 + n * 19), paint((40, 40, 60), glow))
    c.restore()
    if glow > 0:
        g = paint(mix(screen, WHITE, 0.4), 0.3 * glow, blur=80 * s)
        g.setBlendMode(skia.BlendMode.kPlus)
        c.drawCircle(x, y, 360 * s, g)

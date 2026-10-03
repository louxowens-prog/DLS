"""Chapter 1: 1994, in crayon on drawing paper (a nine-year-old's drawings, boiling on 3s), with collage inserts:
the real green-on-black screen of DOCTOR, a newspaper-clipping teletype, typed paper, a rubber stamp."""
import math

import numpy as np
import skia

import common as C
import diy as K
import dot as D
import media as M
import tv
from diy import GOLD, HOT, INK, PURPLE, WHITE, W, H, bez, lin, mix, paint, path, rad, ramp
from common import E, S, Wx

CR = M.CRAYON


# ------------------------------------------------------------------ the crayon cast and props

def circle_pts(cx, cy, rx, ry=None, n=22, a0=0.0, a1=2 * math.pi):
    ry = ry or rx
    a = np.linspace(a0, a1, n)
    return np.stack([cx + rx * np.cos(a), cy + ry * np.sin(a)], 1)


def kid(c, x, y, s, T, mood="smile", talk=0.0, arms=(30, 30), seed=0, hold=None, eyes=(0.0, 0.0)):
    """Dot at nine, as she drew herself: (x, y) = feet. Blue scribble hair (she always drew it blue), a purple
    triangle dress, stick limbs. arms = (left, right) degrees up from hanging."""
    def P(px, py):
        return (x + px * s, y + py * s)
    hx, hy = P(0, -330)
    r = 70 * s
    # legs and shoes
    for sx in (-1, 1):
        M.crayon_line(c, [P(sx * 22, -120), P(sx * 26, -10)], CR["black"], 9 * s, T, seed + 1 + sx)
        M.crayon_fill(c, circle_pts(*P(sx * 30, -4), 24 * s, 12 * s), CR["red"], T, seed + 3 + sx, spacing=7, w=7)
    # dress
    dress = [P(0, -262), P(70, -110), P(-70, -110)]
    M.crayon_fill(c, dress, CR["purple"], T, seed + 5, spacing=9, w=9)
    M.crayon_line(c, dress, mix(CR["purple"], INK, 0.3), 8 * s, T, seed + 6, closed=True)
    for k in range(3):
        M.crayon_line(c, circle_pts(*P(-20 + k * 22, -150 + (k % 2) * 30), 7 * s, n=8), CR["yellow"], 6 * s, T, seed + 40 + k, closed=True)
    # arms
    hands = []
    for sx, ang in ((-1, arms[0]), (1, arms[1])):
        a = math.radians(ang)
        sh = P(sx * 18, -240)
        hx2, hy2 = sh[0] + sx * 110 * s * math.sin(a + 0.35), sh[1] + 110 * s * math.cos(a + 0.35) * (1 if ang < 90 else 1)
        hx2, hy2 = sh[0] + sx * 115 * s * math.sin(math.radians(ang)), sh[1] + 115 * s * math.cos(math.radians(ang))
        M.crayon_line(c, [sh, (hx2, hy2)], CR["peach"], 10 * s, T, seed + 7 + sx)
        M.crayon_fill(c, circle_pts(hx2, hy2, 13 * s), CR["peach"], T, seed + 9 + sx, spacing=6, w=6)
        hands.append((hx2, hy2))
    # head
    M.crayon_fill(c, circle_pts(hx, hy, r), CR["peach"], T, seed + 11, spacing=9, w=9)
    M.crayon_line(c, circle_pts(hx, hy, r, n=26), CR["brown"], 7 * s, T, seed + 12, closed=True)
    # hair: a blue scribble bob with a zig-zag fringe
    dome = [(hx + r * 1.12 * math.cos(a), hy - 10 * s + r * 1.05 * math.sin(a)) for a in np.linspace(math.pi * 0.95, math.pi * 2.05, 14)]
    sides = [(hx + r * 1.15, hy + r * 0.75), (hx + r * 0.8, hy + r * 0.7), (hx + r * 0.75, hy - r * 0.35)]
    zig = [(hx + r * 0.75 - i * r * 1.5 / 8, hy - r * (0.3 if i % 2 else 0.5)) for i in range(9)]
    left = [(hx - r * 0.75, hy - r * 0.35), (hx - r * 0.8, hy + r * 0.7), (hx - r * 1.15, hy + r * 0.75)]
    hair = dome + sides + zig + left
    M.crayon_fill(c, hair, CR["blue"], T, seed + 13, spacing=7, w=8, angle=70)
    M.crayon_line(c, hair, mix(CR["blue"], INK, 0.3), 6 * s, T, seed + 14, closed=True)
    # face
    for sx in (-1, 1):
        ex, ey = hx + sx * 24 * s + eyes[0] * 8 * s, hy + 6 * s + eyes[1] * 6 * s
        if mood == "wide":
            M.crayon_line(c, circle_pts(ex, ey, 13 * s, n=12), CR["black"], 4 * s, T, seed + 15 + sx, closed=True)
        c.drawCircle(ex, ey, 6.5 * s, paint(CR["black"]))
    if talk > 0.15 or mood == "wide":
        M.crayon_fill(c, circle_pts(hx, hy + 38 * s, 16 * s, (8 + 14 * talk) * s), (150, 20, 40), T, seed + 17, spacing=5, w=5)
    elif mood == "sad":
        M.crayon_line(c, bez((hx - 22 * s, hy + 46 * s), (hx, hy + 30 * s), (hx + 22 * s, hy + 46 * s), 8), CR["red"], 6 * s, T, seed + 18)
    elif mood == "goofy":
        M.crayon_line(c, bez((hx - 34 * s, hy + 30 * s), (hx, hy + 64 * s), (hx + 34 * s, hy + 30 * s), 10), CR["red"], 7 * s, T, seed + 18)
        M.crayon_fill(c, circle_pts(hx + 10 * s, hy + 50 * s, 9 * s, 7 * s), (255, 120, 150), T, seed + 19, spacing=4, w=4)
    else:
        M.crayon_line(c, bez((hx - 26 * s, hy + 34 * s), (hx, hy + 54 * s), (hx + 26 * s, hy + 34 * s), 8), CR["red"], 6 * s, T, seed + 18)
    for sx in (-1, 1):
        M.crayon_fill(c, circle_pts(hx + sx * 42 * s, hy + 26 * s, 11 * s), (255, 140, 150), T, seed + 20 + sx, spacing=5, w=5, a=0.6)
    return hands


def kid_sock(c, x, y, s, T, seed=0, parts=1.0, open_=0.0, rot=0.0):
    """Doc as drawn in 1994: a striped tube sock, googly eyes, yarn hair, a foil head mirror. parts 0..1 builds it."""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    body = [(-40 * s, 160 * s), (40 * s, 160 * s), (46 * s, -30 * s), (80 * s, -70 * s), (60 * s, -110 * s), (-10 * s, -120 * s),
            (-50 * s, -80 * s)]
    M.crayon_fill(c, body, (248, 248, 250), T, seed, spacing=8, w=8, a=0.7)
    M.crayon_line(c, body, CR["grey"], 6 * s, T, seed + 1, closed=True)
    for i, col in enumerate((CR["pink"], CR["blue"], CR["yellow"])):
        yy = (100 + i * 22) * s
        M.crayon_line(c, [(-40 * s, yy), (42 * s, yy)], col, 12 * s, T, seed + 2 + i)
    if parts > 0.25:                                                      # googly eyes
        for k, (ex, ey, er) in enumerate(((0, -70, 22), (40, -64, 18))):
            M.crayon_fill(c, circle_pts(ex * s, ey * s, er * s), WHITE, T, seed + 6 + k, spacing=5, w=5)
            M.crayon_line(c, circle_pts(ex * s, ey * s, er * s, n=14), CR["black"], 4 * s, T, seed + 8 + k, closed=True)
            jx = math.sin(T * 9 + k) * 4 * s
            c.drawCircle(ex * s + jx, (ey + 6) * s, er * 0.5 * s, paint(CR["black"]))
    if parts > 0.5:                                                       # yarn hair
        for k in range(6):
            M.crayon_line(c, bez(((-30 + k * 10) * s, -112 * s), ((-60 + k * 16) * s, -170 * s), ((-10 + k * 12) * s, -118 * s), 10),
                          CR["orange"], 6 * s, T, seed + 10 + k)
    if parts > 0.75:                                                      # the mouth
        mo = (10 + 30 * open_) * s
        M.crayon_fill(c, [(10 * s, -30 * s), (80 * s, -40 * s), (70 * s, -40 * s + mo), (10 * s, -20 * s + mo * 0.5)], CR["red"], T,
                      seed + 17, spacing=5, w=5)
    if parts >= 1.0:                                                      # the head mirror
        M.crayon_fill(c, circle_pts(-30 * s, -112 * s, 22 * s), (200, 200, 210), T, seed + 18, spacing=5, w=5)
        M.crayon_line(c, circle_pts(-30 * s, -112 * s, 22 * s, n=14), CR["grey"], 4 * s, T, seed + 19, closed=True)
    c.restore()


def computer(c, x, y, s, T, seed=0):
    """Dad's computer in crayon: a beige monitor, keyboard, tower. Returns the screen rect (for the real screen)."""
    beige, dark = (226, 210, 166), (150, 130, 96)
    mon = [(x - 230 * s, y - 380 * s), (x + 230 * s, y - 380 * s), (x + 230 * s, y - 20 * s), (x - 230 * s, y - 20 * s)]
    M.crayon_fill(c, mon, beige, T, seed, spacing=10, w=10)
    M.crayon_line(c, mon, dark, 9 * s, T, seed + 1, closed=True)
    M.crayon_fill(c, [(x - 70 * s, y - 20 * s), (x + 70 * s, y - 20 * s), (x + 110 * s, y + 30 * s), (x - 110 * s, y + 30 * s)], beige, T,
                  seed + 2, spacing=9, w=9)
    kb = [(x - 260 * s, y + 60 * s), (x + 260 * s, y + 60 * s), (x + 290 * s, y + 150 * s), (x - 290 * s, y + 150 * s)]
    M.crayon_fill(c, kb, beige, T, seed + 3, spacing=9, w=9)
    M.crayon_line(c, kb, dark, 7 * s, T, seed + 4, closed=True)
    for r_ in range(3):
        for k in range(9):
            kx = x - 230 * s + k * 52 * s + r_ * 10 * s
            ky = y + 76 * s + r_ * 24 * s
            M.crayon_line(c, [(kx, ky), (kx + 34 * s, ky)], dark, 9 * s, T, seed + 20 + k + r_ * 9, passes=1)
    tw = [(x + 300 * s, y - 300 * s), (x + 420 * s, y - 300 * s), (x + 420 * s, y + 150 * s), (x + 300 * s, y + 150 * s)]
    M.crayon_fill(c, tw, beige, T, seed + 5, spacing=10, w=10)
    M.crayon_line(c, tw, dark, 8 * s, T, seed + 6, closed=True)
    M.crayon_line(c, [(x + 320 * s, y - 240 * s), (x + 400 * s, y - 240 * s)], dark, 8 * s, T, seed + 7)
    c.drawCircle(x + 400 * s, y + 110 * s, 9 * s, paint((60, 220, 80)))
    return (x - 190 * s, y - 345 * s, x + 190 * s, y - 60 * s)


def dos_screen(c, rect, lines, T, cursor=True, size=46, glow=True):
    """A real green-phosphor screen pasted into the drawing: scanlines, a soft glow, VT323 text."""
    x0, y0, x1, y1 = rect
    r = skia.Rect.MakeLTRB(x0, y0, x1, y1)
    c.drawRRect(skia.RRect.MakeRectXY(r, 26, 26), paint((8, 20, 10)))
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(r, 26, 26), True)
    c.drawRect(r, paint(shader=rad(((x0 + x1) / 2, (y0 + y1) / 2), (x1 - x0) * 0.7, [(20, 50, 24), (6, 14, 8)])))
    yy = y0 + size * 1.3
    last = None
    for ln, col in lines:
        if ln:
            K.text(c, ln, x0 + 30, yy, size, "vt323-400", col, align="left", tag="osd")
            if glow:
                c.drawString(ln, x0 + 30, yy, K.font("vt323-400", size), paint(col, 0.35, blur=6))
        last = (ln, yy)
        yy += size * 1.05
    if cursor and int(T * 2.5) % 2 == 0 and last is not None:
        w = K.font("vt323-400", size).measureText(last[0] or "")
        c.drawRect(skia.Rect.MakeXYWH(x0 + 34 + w, last[1] - size * 0.7, size * 0.5, size * 0.8), paint((120, 255, 140)))
    for k in range(int((y1 - y0) / 4)):
        c.drawLine(x0, y0 + k * 4, x1, y0 + k * 4, paint(INK, 0.22, stroke=1.5))
    c.drawOval(skia.Rect.MakeLTRB(x0 + 20, y0 + 10, x0 + (x1 - x0) * 0.5, y0 + (y1 - y0) * 0.3), paint(WHITE, 0.07, blur=10))
    c.restore()


def typed(s, t0, t1, T):
    """The part of s typed by time T, if typing runs from t0 to t1."""
    k = ramp(T, t0, t1)
    return s[: int(round(len(s) * k))]


def scrawl_label(c, T, t0, text, x, y, ax, ay, color=(255, 236, 120), rot=-4, size=62, seed=1, bend=0.25):
    k = ramp(T, t0, t0 + 0.4)
    if k <= 0:
        return
    tv.scribble_arrow(c, x, y + 16, ax, ay, WHITE, k=k, seed=seed, bend=bend)
    tv.scrawl(c, text, x, y, size, color, rot=rot, k=ramp(T, t0, t0 + 0.3))


# ------------------------------------------------------------------ shots

def s_c1_kid(T, idx):
    """'1994. I'm nine. Dad's computer has a therapist.' The drawing; grown-up Dot leans in from the right edge."""
    st = K.Stage()
    M.drawing_paper(st.arr)
    c = st.c
    M.tape(c, 110, 250)
    M.tape(c, 970, 250, rot=30)
    with M.crayon_layer(c):
        M.kid_text(c, "1994", 420, 420, 210, CR["red"], T, 2)
        M.crayon_fill(c, circle_pts(920, 380, 60), CR["yellow"], T, 3, spacing=8)                   # the sun
        for k in range(8):
            a = k * math.pi / 4 + 0.2
            M.crayon_line(c, [(920 + 78 * math.cos(a), 380 + 78 * math.sin(a)), (920 + 112 * math.cos(a), 380 + 112 * math.sin(a))],
                          CR["orange"], 8, T, 30 + k)
        M.crayon_fill(c, [(60, 1180), (1020, 1180), (1020, 1225), (60, 1225)], CR["brown"], T, 4, spacing=9)       # the desk
        for lx in (110, 960):
            M.crayon_line(c, [(lx, 1220), (lx, 1500)], CR["brown"], 14, T, 5 + lx)
        scr = computer(c, 520, 1010, 0.8, T, 7)
        kid(c, 220, 1420, 1.0, T, mood="smile" if T < Wx("a1", "therapist") else "wide", talk=0.0, arms=(30, 70), seed=9,
            eyes=(0.8, -0.2) if T > Wx("a1", "Dad") else (0, 0))
        M.kid_text(c, "CH.1", 160, 600, 70, CR["purple"], T, 5, rot=-8)
    msg = [("C:\\> DOCTOR", (120, 255, 140))]
    if T > Wx("a1", "therapist") - 0.1:
        msg += [("", None), ("HOW DO YOU DO.", (160, 255, 170)), ("PLEASE TELL ME", (160, 255, 170)), ("YOUR PROBLEM.", (160, 255, 170))]
    dos_screen(c, scr, [(m, col or (0, 0, 0)) for m, col in msg], T, size=34)
    C.live_dot(c, T, idx, 930, 2200, 0.74, pose="palm", mood="smile" if T < Wx("a1", "Dad") else "deadpan",
               look=(-0.7, 0.1), seed=1, turn=-0.4, sock_look=(-0.9, 0.2), sock_face=-1)
    scrawl_label(c, T, Wx("a1", "nine"), "ME (9)", 300, 720, 230, 960, rot=-6, seed=4)
    return st.arr


def s_c1_screen(T, idx):
    """The screen, close: she types; it answers."""
    st = K.Stage()
    M.drawing_paper(st.arr, seed=4)
    c = st.c
    with M.crayon_layer(c):
        bez_ = [(40, 300), (1040, 300), (1040, 1300), (40, 1300)]
        M.crayon_fill(c, bez_, (226, 210, 166), T, 3, spacing=11, w=11)
        M.crayon_line(c, bez_, (150, 130, 96), 12, T, 4, closed=True)
        for sx in (-1, 1):                                                     # her hands on the keys
            hx = 540 + sx * 200 + (12 if (int(T * 10) + sx) % 2 else -12) * (C.talk(T, "KID") > 0 or C.line_at(T, "KID") is not None)
            M.crayon_fill(c, circle_pts(hx, 1560, 70, 50), CR["peach"], T, 6 + sx, spacing=8)
            M.crayon_line(c, circle_pts(hx, 1560, 70, 50, n=18), CR["brown"], 6, T, 8 + sx, closed=True)
            for f_ in range(4):                                                # stubby crayon fingers on the keys
                fx = hx - 45 + f_ * 30
                M.crayon_line(c, [(fx, 1525), (fx + sx * 4, 1470)], CR["peach"], 18, T, 12 + f_ + sx * 5, passes=2)
                M.crayon_line(c, [(fx - 9, 1525), (fx - 9 + sx * 4, 1468), (fx + 9 + sx * 4, 1468), (fx + 9, 1525)], CR["brown"], 4, T,
                              30 + f_ + sx * 5, passes=1)
        M.kid_text(c, "DAD'S COMPUTER - DO NOT TOUCH", 540, 1385, 50, CR["red"], T, 9, rot=-2)
    a2 = "> NOBODY LISTENS TO ME"
    a3 = ["WHY DO YOU SAY", "NOBODY LISTENS", "TO YOU?"]
    lines = [(typed(a2, S("a2") - 0.05, E("a2") - 0.1, T), (150, 255, 160))]
    if T > S("a3") - 0.05:
        full = " ".join(a3)
        got = typed(full, S("a3"), E("a3") - 0.15, T)
        out, n = [], 0
        for ln in a3:
            out.append(got[n:n + len(ln)])
            n += len(ln) + 1
        lines += [("", (0, 0, 0))] + [(ln, (120, 255, 140)) for ln in out]
    dos_screen(c, (110, 370, 970, 1230), lines, T, size=72)
    return tv.apply_cam(st.arr, *tv.shake(T, 3, 4, 0.2), 1.03)


def s_c1_sock(T, idx):
    """'It listened! So I gave it a body.' The sock gets eyes, hair, a mouth, a head mirror - pop, pop, pop."""
    st = K.Stage()
    M.drawing_paper(st.arr, seed=6)
    c = st.c
    t0 = Wx("a4", "body") - 0.6
    parts = ramp(T, t0, Wx("a4", "body") + 0.45)
    with M.crayon_layer(c):
        hands = kid(c, 330, 1330, 1.35, T, mood="smile" if T < S("a4") + 0.8 else "goofy", arms=(25, 140), seed=12)
        hx_, hy_ = hands[1]
        kid_sock(c, hx_ + 50, hy_ - 150 * 1.6, 1.6, T, seed=20, parts=[0.0, 0.3, 0.6, 0.8, 1.0][min(4, int(parts * 5))], open_=0.4 * (math.sin(T * 12) > 0) * (parts >= 1),
                 rot=-8 + 5 * math.sin(T * 3))
        for k in range(5):                                                     # sparkles round the new friend
            a = k * 1.3 + T * 2
            x, y = 560 + 300 * math.cos(a), 640 + 280 * math.sin(a)
            if parts >= 1:
                M.crayon_line(c, [(x - 30, y), (x + 30, y)], CR["gold"], 8, T, 40 + k)
                M.crayon_line(c, [(x, y - 30), (x, y + 30)], CR["gold"], 8, T, 50 + k)
    if T > E("a4") - 0.3:
        scrawl_label(c, T, E("a4") - 0.3, "DOC. EST. 1994", 700, 300, 640, 420, (255, 120, 190), rot=-3, seed=7)
    return st.arr


def _clipping(c, x, y, w, h, T, seed=0):
    """A newspaper clipping glued on: a halftone 1960s teletype terminal, a typed caption strip."""
    c.save()
    c.translate(x, y)
    c.rotate(-3)
    c.drawRect(skia.Rect.MakeXYWH(-w / 2 + 10, -h / 2 + 14, w, h), paint(INK, 0.3, blur=8))
    c.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), paint((236, 230, 214)))
    ix0, iy0, iw, ih = -w / 2 + 30, -h / 2 + 30, w - 60, h - 150
    c.drawRect(skia.Rect.MakeXYWH(ix0, iy0, iw, ih), paint((200, 196, 186)))
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(ix0, iy0, iw, ih))
    g = (70, 66, 62)
    c.drawRect(skia.Rect.MakeXYWH(ix0 + iw * 0.12, iy0 + ih * 0.42, iw * 0.76, ih * 0.5), paint(g))                # the teletype
    c.drawRect(skia.Rect.MakeXYWH(ix0 + iw * 0.2, iy0 + ih * 0.3, iw * 0.6, ih * 0.16), paint((120, 116, 110)))
    c.drawRect(skia.Rect.MakeXYWH(ix0 + iw * 0.3, iy0 + ih * 0.04, iw * 0.4, ih * 0.3), paint((246, 244, 236)))     # paper roll
    for k in range(5):
        c.drawLine(ix0 + iw * 0.33, iy0 + ih * (0.09 + k * 0.045), ix0 + iw * (0.5 + 0.15 * ((k * 7) % 3) / 2), iy0 + ih * (0.09 + k * 0.045),
                   paint((60, 60, 60), stroke=3))
    for r_ in range(3):
        for k in range(10):
            c.drawCircle(ix0 + iw * (0.18 + k * 0.07), iy0 + ih * (0.62 + r_ * 0.09), 9, paint((180, 176, 170)))
    c.restore()
    hp = skia.Paint(AntiAlias=True)
    hp.setColor4f(K.col((40, 36, 30), 0.12))
    for yy in np.arange(iy0, iy0 + ih, 6):
        c.drawLine(ix0, yy, ix0 + iw, yy, hp)
    K.text(c, "ELIZA, MIT, 1966", 0, h / 2 - 66, 50, "special-elite-400", (40, 34, 30), tag="fact")
    c.restore()


def s_c1_eliza(T, idx):
    """'It was a copy of ELIZA, a 1960s program ...' A clipping; word scraps shuffle into DOCTOR's reply."""
    st = K.Stage()
    M.drawing_paper(st.arr, seed=8)
    c = st.c
    _clipping(c, 540, 600, 760, 560, T)
    M.tape(c, 200, 330, rot=-40)
    M.tape(c, 880, 330, rot=40)
    # the trick, in scraps of paper: NOBODY LISTENS TO ME -> WHY DO YOU SAY NOBODY LISTENS TO YOU?
    k = ramp(T, S("a5") + 1.0, S("a5") + 2.4)
    src = [("NOBODY", 0), ("LISTENS", 1), ("TO", 2), ("ME", 3)]
    y0, y1 = 1060, 1240
    f = K.font("special-elite-400", 54)
    def row(words):
        ws = [f.measureText(w) + 44 for w in words]
        x = 540 - (sum(ws) + 14 * (len(ws) - 1)) / 2
        out = []
        for w in ws:
            out.append(x + w / 2)
            x += w + 14
        return out
    xs0 = row(["NOBODY", "LISTENS", "TO", "ME"])
    xs1 = row(["NOBODY", "LISTENS", "TO", "YOU?"])
    for i, (wd, j) in enumerate(src):
        x_start, y_start = xs0[i], y0
        x_end, y_end = xs1[i], y1
        x = x_start + (x_end - x_start) * K.ease(k)
        y = y_start + (y_end - y_start) * K.ease(k)
        label = wd if (wd != "ME" or k < 0.6) else "YOU?"
        _scrap(c, label, x, y, 54, seed=i, rot=(-4 + i * 3) * (1 - k) + (2 - i) * k, hot=(label == "YOU?"))
    if k > 0.4:
        _scrap(c, "WHY DO YOU SAY", 540, y1 - 110, 54, seed=9, rot=-2, hot=True, a=ramp(k, 0.4, 0.7))
    with M.crayon_layer(c):
        M.kid_text(c, "THE TRICK:", 250, 960, 70, CR["purple"], T, 8, rot=-6)
    return st.arr


def _scrap(c, s, x, y, size, seed=0, rot=0.0, hot=False, a=1.0):
    f = K.font("special-elite-400", size)
    w = f.measureText(s)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    pts = M.scissor([(-w / 2 - 22, -size * 0.95), (w / 2 + 22, -size * 0.95), (w / 2 + 22, size * 0.42), (-w / 2 - 22, size * 0.42)], seed, 2.5, 18)
    c.drawPath(path(pts + np.array([6, 8])), paint(INK, 0.25 * a, blur=5))
    c.drawPath(path(pts), paint((255, 236, 120) if hot else (250, 248, 240), a))
    K.text(c, s, 0, 0, size, "special-elite-400", (30, 26, 24), tag="label", a=a)
    c.restore()


def s_c1_nothing(T, idx):
    """'... that understood nothing.' The stamp comes down on a crayon brain."""
    st = K.Stage()
    M.drawing_paper(st.arr, seed=9)
    c = st.c
    with M.crayon_layer(c):
        brain = circle_pts(540, 780, 330, 250, n=30)
        M.crayon_fill(c, brain, CR["pink"], T, 3, spacing=10)
        M.crayon_line(c, brain, (180, 60, 120), 10, T, 4, closed=True)
        for k in range(7):
            M.crayon_line(c, bez((300 + k * 70, 600), (330 + k * 70, 780), (290 + k * 70, 960), 10), (200, 80, 140), 7, T, 10 + k)
        M.kid_text(c, "ELIZA'S BRAIN", 540, 420, 80, CR["purple"], T, 6, rot=-3)
    t_st = Wx("a5", "nothing") - 0.05
    if T > t_st:
        k = K.pop(T, t_st, 0.18, 0.4)
        c.save()
        c.translate(540, 820)
        c.rotate(-12)
        c.scale(k, k)
        r = skia.Rect.MakeXYWH(-420, -150, 840, 300)
        c.drawRRect(skia.RRect.MakeRectXY(r, 30, 30), paint((220, 30, 50), 0.9, stroke=16))
        K.text(c, "UNDERSTOOD:", 0, -30, 92, "rubik-900", (220, 30, 50), tag="stamp")
        K.text(c, "NOTHING", 0, 100, 130, "rubik-900", (220, 30, 50), tag="stamp")
        c.restore()
    return tv.apply_cam(st.arr, *tv.shake(T, 14 * max(0.0, 1 - (T - t_st) * 4) if T > t_st else 0, 3, 0.4))


def s_c1_secretary(T, idx):
    """'Yet its creator's secretary asked him to leave, so she could talk to it.' Felt-tip, on a yellow legal pad."""
    st = K.Stage()
    M.drawing_paper(st.arr, seed=10, tone=(255, 244, 170), lines=True)
    c = st.c
    ink_ = (24, 24, 40)
    t_out = Wx("a6", "leave") + 0.1
    walk = ramp(T, t_out, t_out + 1.6)
    with M.crayon_layer(c, 1.0):
        # the teletype and the secretary
        M.crayon_fill(c, [(560, 900), (900, 900), (920, 1100), (540, 1100)], (120, 120, 130), T, 3, spacing=8, w=8)
        M.crayon_line(c, [(560, 900), (900, 900), (920, 1100), (540, 1100)], ink_, 7, T, 4, closed=True)
        M.crayon_fill(c, [(640, 800), (820, 800), (820, 900), (640, 900)], WHITE, T, 5, spacing=7, w=7)
        M.crayon_line(c, circle_pts(470, 760, 62), ink_, 7, T, 6, closed=True)                      # her head
        M.crayon_fill(c, circle_pts(470, 680, 46, 34), (90, 50, 30), T, 7, spacing=6)               # the bun
        M.crayon_line(c, [(420, 760), (520, 760)], ink_, 5, T, 8)
        for sx in (-1, 1):                                                                         # cat-eye glasses
            M.crayon_line(c, [(470 + sx * 40 - 22, 752), (470 + sx * 40 + 22, 748), (470 + sx * 40 + 26, 738)], ink_, 5, T, 9 + sx)
        M.crayon_line(c, [(470, 822), (470, 1060)], ink_, 8, T, 11)
        M.crayon_line(c, [(470, 880), (600, 960)], ink_, 7, T, 12)                                   # typing arm
        M.crayon_line(c, [(470, 880), (330, 800), (300, 720)], ink_, 7, T, 13)                     # pointing to the door
        M.crayon_fill(c, [(430, 1000), (510, 1000), (540, 1150), (400, 1150)], (230, 120, 160), T, 14, spacing=8)
        # the door
        M.crayon_fill(c, [(60, 560), (220, 560), (220, 1150), (60, 1150)], (180, 130, 80), T, 15, spacing=10)
        M.crayon_line(c, [(60, 560), (220, 560), (220, 1150), (60, 1150)], ink_, 7, T, 16, closed=True)
        # the creator, walking out (step by step)
        cx = 300 - 220 * walk
        stp = int(walk * 8) % 2
        M.crayon_line(c, circle_pts(cx, 680, 58), ink_, 7, T, 17, closed=True)
        for sx in (-1, 1):
            M.crayon_line(c, circle_pts(cx + sx * 22, 676, 15, n=12), ink_, 4, T, 18 + sx, closed=True)
        M.crayon_fill(c, [(cx - 50, 740), (cx + 50, 740), (cx + 44, 960), (cx - 44, 960)], (90, 90, 110), T, 20, spacing=8)
        M.crayon_line(c, [(cx - 20, 960), (cx - 30 - 20 * stp, 1130)], ink_, 8, T, 21)
        M.crayon_line(c, [(cx + 20, 960), (cx + 30 - 20 * (1 - stp), 1130)], ink_, 8, T, 22)
    if T > Wx("a6", "asked") - 0.1:
        k = K.pop(T, Wx("a6", "asked") - 0.1, 0.2, 0.3)
        c.save()
        c.translate(600, 520)
        c.scale(k, k)
        c.drawPath(K.smooth([(-230, -80), (230, -90), (250, 60), (-30, 70), (-90, 150), (-110, 70), (-240, 60)]), paint(WHITE))
        c.drawPath(K.smooth([(-230, -80), (230, -90), (250, 60), (-30, 70), (-90, 150), (-110, 70), (-240, 60)]), paint(ink_, stroke=6))
        K.text(c, "DO YOU MIND?", 0, 10, 64, "permanent-marker-400", ink_, tag="bubble")
        c.restore()
    M.kid_text(c, "MIT, 1960s", 760, 330, 64, ink_, T, 3, rot=3, fname="permanent-marker-400")
    return st.arr


QUOTE = ["\"... extremely short", "exposures to a relatively", "simple computer program", "could induce powerful",
         "delusional thinking in", "quite normal people.\""]


def s_c1_quote(T, idx):
    """The quote, typed on yellowed paper as she says it; a red marker rings 'quite normal people'."""
    st = K.Stage()
    M.drawing_paper(st.arr, seed=12, tone=(246, 236, 206))
    c = st.c
    c.save()
    c.translate(540, 760)
    c.rotate(-2)
    full = " ".join(QUOTE)
    t0, t1 = S("a7") + 0.2, E("a7") - 0.2
    got = typed(full, t0, t1, T)
    n, yy = 0, -330
    for ln in QUOTE:
        part = got[n:n + len(ln)]
        if part:
            K.text(c, part, -430, yy, 64, "special-elite-400", (40, 34, 30), align="left", tag="quote")
        n += len(ln) + 1
        yy += 92
    if T > t1:
        K.text(c, "- Joseph Weizenbaum, 1976", 370, yy + 60, 46, "special-elite-400", (90, 60, 40), align="right", tag="quote2")
    f = K.font("special-elite-400", 64)
    y5, y6 = -330 + 4 * 92 + 16, -330 + 5 * 92 + 16
    for (xa, xb, yy_, ta, tb, sd) in ((-430, -430 + f.measureText("quite normal people."), y6, Wx("a7", "quite") - 0.1,
                                      Wx("a7", "people") + 0.35, 4),):
        kq = ramp(T, ta, tb)
        if kq > 0:
            pts = np.stack([np.linspace(xa - 10, xa - 10 + (xb - xa + 20) * kq, 16), np.full(16, yy_)], 1)
            for p_ in range(2):
                c.drawPath(path(M.wob(pts, T, sd + p_ * 7, 2.2) + np.array([0, p_ * 9]), closed=False), paint((220, 30, 50), 0.9, stroke=9))
    c.restore()
    with M.crayon_layer(c):                                               # a sock doodled in the margin
        kid_sock(c, 170, 1180, 0.7, T, seed=23, parts=1.0, rot=-10)
    return tv.apply_cam(st.arr, *tv.shake(T, 2, 5, 0.1), 1.0 + 0.05 * ramp(T, S("a7"), E("a7")))


def s_c1_normal(T, idx):
    """Hard cut. Silence. 'I was nine. Very normal.' A freeze frame of her hugging the sock, cross-eyed; grown-up Dot
    looks at us."""
    st = K.Stage()
    M.drawing_paper(st.arr, seed=14)
    c = st.c
    Tz = min(T, E("a7") + 0.45)                                           # it's a frozen frame
    with M.crayon_layer(c):
        heart = [(540 + 16 * (math.sin(a) ** 3) * 26, 800 - (13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)) * 26)
                 for a in np.linspace(0, 2 * math.pi, 40)]
        M.crayon_fill(c, heart, CR["pink"], Tz, 3, spacing=12, w=10, a=0.6)
        kid(c, 420, 1300, 1.25, Tz, mood="goofy", arms=(150, 150), seed=12, eyes=(0.6, 0.3))
        kid_sock(c, 680, 820, 1.25, Tz, seed=20, parts=1.0, open_=0.6, rot=12)
    tv.freeze_tint(st.arr, 0.6)
    c = skia.Surface(st.arr).getCanvas()
    C.live_dot(c, T, idx, 905, 2350, 0.78, pose="rest", mood="deadpan" if T < S("a8") else "flat", look=(-0.2, 0.0), seed=1,
               sock_open=0.0)
    scrawl_label(c, T, S("a8") + 0.15, "VERY NORMAL", 400, 330, 420, 600, (255, 110, 190), rot=-5, size=86, seed=8)
    return st.arr

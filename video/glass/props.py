"""Exhibits: ordinary things of a watched life, made precious - a microphone like a gilded lily, a license plate in a
reliquary, a pin on a little globe, a cursor carved in porcelain, a receipt unrolling like a train, a phone on a
velvet cushion, books, a candle. Each draws standing on (x, y) at a scale of s (about 300 px tall at s = 1)."""
import math

import skia

import couture as C
import gel as G
import kit as K
from kit import BLACK, WHITE, mix, paint


def microphone(c, x, y, s, T, a=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    gs = C.gold_shader((-60, 0), (60, 0))
    c.drawPath(K.smooth([(-50, 0), (50, 0), (30, -20), (-30, -20)]), paint(shader=gs, a=a))
    c.drawRect(skia.Rect.MakeLTRB(-8, -170, 8, -20), paint(shader=gs, a=a))
    head = K.smooth([(-56, -300), (-46, -340), (0, -356), (46, -340), (56, -300), (50, -200), (0, -170), (-50, -200)])
    c.drawPath(head, paint(shader=gs, a=a))
    c.save()
    c.clipPath(head, doAntiAlias=True)
    for k in range(-6, 7):
        c.drawLine(k * 10, -360, k * 10, -170, paint(C.GOLD_LO, 0.7 * a, stroke=3))
    for k in range(10):
        c.drawLine(-60, -350 + k * 18, 60, -350 + k * 18, paint(C.GOLD_LO, 0.5 * a, stroke=2))
    c.restore()
    c.drawPath(head, paint(C.GOLD_HI, 0.8 * a, stroke=3))
    c.drawCircle(0, -300, 10, paint((255, 40, 40), a * (0.6 + 0.4 * math.sin(T * 5))))
    c.restore()


def plate(c, x, y, s, T, text="GLS 0034", a=1.0):
    """A license plate in a small gilded reliquary frame, standing upright."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawPath(K.rrect(-170, -230, 170, -20, 20), paint(shader=C.gold_shader((-170, 0), (170, 0)), a=a))
    c.drawPath(K.rrect(-150, -200, 150, -50, 12), paint((240, 240, 236), a))
    c.drawPath(K.rrect(-150, -200, 150, -50, 12), paint((30, 40, 80), a, stroke=5))
    K.text(c, text, 0, -100, 62, "jost-600", (24, 30, 60), tag="deco", a=a)
    c.drawPath(K.smooth([(-60, -20), (60, -20), (40, 0), (-40, 0)]), paint(C.GOLD, a))
    c.restore()


def pin(c, x, y, s, T, a=1.0):
    """A gold map pin piercing a small blue-and-ivory globe on a stand."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawPath(K.smooth([(-50, 0), (50, 0), (24, -30), (-24, -30)]), paint(C.GOLD, a))
    c.drawRect(skia.Rect.MakeLTRB(-5, -80, 5, -30), paint(C.GOLD, a))
    c.drawCircle(0, -160, 90, paint(shader=K.rad((-30, -190), 120, [(220, 232, 246), (60, 100, 180), (16, 30, 80)]), a=a))
    for k in range(-2, 3):
        c.drawOval(skia.Rect.MakeLTRB(-90, -160 + k * 32 - 8, 90, -160 + k * 32 + 8), paint((200, 220, 240), 0.25 * a, stroke=2))
    c.drawOval(skia.Rect.MakeLTRB(-30, -250, 30, -70), paint((200, 220, 240), 0.25 * a, stroke=2))
    c.drawLine(10, -170, 10, -290, paint((60, 50, 40), a, stroke=5))
    c.drawCircle(10, -300, 26, paint(shader=K.rad((2, -308), 30, [(255, 120, 110), (200, 20, 30), (90, 0, 10)]), a=a))
    G.pool(c, 10, -170, 50, (255, 80, 60), 0.5 * a)
    c.restore()


def cursor(c, x, y, s, T, a=1.0):
    """The arrow of a mouse pointer, carved in glazed porcelain, on a gold pedestal."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawPath(K.smooth([(-50, 0), (50, 0), (30, -24), (-30, -24)]), paint(C.GOLD, a))
    p = K.path([(-60, -330), (-60, -60), (0, -120), (40, -30), (80, -50), (40, -140), (120, -150)])
    c.drawPath(p, paint(shader=K.lin((-60, -330), (120, -30), [C.PORC_HI, C.PORC, C.PORC_SH]), a=a))
    c.drawPath(p, paint((40, 40, 50), a, stroke=6))
    c.drawPath(K.path([(-50, -300), (-50, -100), (-30, -120)], closed=False), paint(WHITE, 0.6 * a, stroke=4))
    c.restore()


def receipt(c, x, y, s, T, a=1.0, lines=12, unroll=1.0):
    """A long paper receipt hanging from a gold clip and pooling in curls at the bottom."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    L = 360 * unroll
    c.drawRect(skia.Rect.MakeLTRB(-70, -380, 70, -380 + L), paint((246, 244, 236), a))
    rng = K.rng_at(lines, 3)
    for i in range(lines):
        yy = -360 + i * 26
        if yy > -380 + L - 10:
            break
        w = rng.uniform(40, 100)
        c.drawLine(-56, yy, -56 + w, yy, paint((90, 90, 96), 0.7 * a, stroke=5))
        c.drawLine(30, yy, 56, yy, paint((90, 90, 96), 0.7 * a, stroke=5))
    c.drawPath(K.smooth([(-70, -20), (70, -20), (110, 0), (60, 14), (-80, 10), (-120, 0)]), paint((236, 234, 226), a))
    c.drawRect(skia.Rect.MakeLTRB(-80, -400, 80, -376), paint(C.GOLD, a))
    c.restore()


def cushion(c, x, y, s, col=(120, 6, 20), a=1.0):
    """A velvet cushion with gold tassels."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawPath(K.smooth([(-170, -10), (-150, -60), (0, -80), (150, -60), (170, -10), (150, 20), (0, 30), (-150, 20)]),
               paint(shader=K.rad((-40, -60), 220, [mix(col, (255, 120, 120), 0.3), col, mix(col, BLACK, 0.6)]), a=a))
    for sd in (-1, 1):
        c.drawLine(sd * 168, -10, sd * 176, 30, paint(C.GOLD, a, stroke=6))
        c.drawCircle(sd * 176, 36, 9, paint(C.GOLD, a))
    c.restore()


def book(c, x, y, s, T, open_=0.0, col=(120, 10, 24), a=1.0):
    """A book standing open (open_ = 1) or shut (0)."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    w = 80 + 80 * open_
    c.drawPath(K.path([(-w, 0), (0, 10), (w, 0), (w, -150), (0, -140), (-w, -150)]), paint(col, a))
    if open_ > 0.05:
        c.drawPath(K.path([(-w + 8, -6), (0, 2), (w - 8, -6), (w - 8, -142), (0, -132), (-w + 8, -142)]), paint((240, 234, 220), a))
        for i in range(6):
            c.drawLine(-w + 20, -120 + i * 18, -14, -112 + i * 18, paint((120, 110, 100), 0.6 * a, stroke=3))
            c.drawLine(14, -112 + i * 18, w - 20, -120 + i * 18, paint((120, 110, 100), 0.6 * a, stroke=3))
    c.drawPath(K.path([(-w, 0), (0, 10), (w, 0), (w, -150), (0, -140), (-w, -150)]), paint(C.GOLD, 0.8 * a, stroke=3))
    c.restore()

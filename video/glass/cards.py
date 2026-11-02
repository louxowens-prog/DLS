"""The title and the chapter cards, designed like the invitation to a couture show: black, a hairline gold frame,
thin widely spaced serif capitals that draw together as they appear, a small italic line underneath, gold dust
drifting through the dark."""
import math

import skia

import couture as C
import gel as G
import kit as K
from kit import BLACK, WHITE, W, H, mix, paint

CHAPTERS = {1: ("I", "THE EYE", "on being watched"), 2: ("II", "THE WORKHOUSE", "on being scored"),
            3: ("III", "THE ORACLE", "on being known"), 4: ("IV", "THE SCALES", "on power")}


def spaced(c, s, x, y, size, font="italiana-400", track=0.3, color=C.GOLD_HI, a=1.0, tag="title", shader=None):
    """Capitals with wide letter-spacing (track: extra space per letter, as a fraction of the size), centred on x."""
    f = K.font(font, size)
    ws = [f.measureText(ch) for ch in s]
    total = sum(ws) + track * size * (len(s) - 1)
    a = a * K.TEXT_A[0]
    if a < 0.03:
        return total
    xx = x - total / 2
    p = paint(color, a) if shader is None else paint(shader=shader, a=a)
    for ch, w in zip(s, ws):
        c.drawString(ch, xx, y, f, p)
        xx += w + track * size
    K.reg(x - total / 2, y - size * 0.74, x + total / 2, y + size * 0.1, tag)
    return total


def dust(c, T, n=70, a=1.0, seed=0, col=(255, 220, 150)):
    G.motes(c, T, 0, 0, W, H, color=col, n=n, a=0.5 * a, seed=seed, size=1.8)


def frame(c, a=1.0, inset=70, top=250, bottom=1520):
    """A hairline gold frame with small stepped corners."""
    x0, x1, y0, y1 = inset, W - inset, top, bottom
    p = paint(C.GOLD, 0.8 * a, stroke=2)
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), p)
    c.drawRect(skia.Rect.MakeLTRB(x0 + 14, y0 + 14, x1 - 14, y1 - 14), paint(C.GOLD, 0.35 * a, stroke=1))
    for (cx, cy, dx, dy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        c.drawRect(skia.Rect.MakeLTRB(min(cx, cx + dx * 34), min(cy, cy + dy * 34), max(cx, cx + dx * 34), max(cy, cy + dy * 34)), paint(C.GOLD, 0.9 * a, stroke=2))
        c.drawCircle(cx + dx * 17, cy + dy * 17, 4, paint(C.GOLD_HI, a))


def chapter(c, n, T, t0, a=1.0, bg=True, eye=True):
    """Chapter card n, appearing at t0: the numeral, the title drawing together, the italic line, a little lens."""
    num, title, sub = CHAPTERS[n]
    u = T - t0
    if bg:
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(BLACK))
        G.pool(c, 540, 860, 700, (120, 80, 30), 0.18 * a)
    dust(c, T, a=a, seed=n)
    k = K.ease(K.ramp(u, 0.0, 0.45))
    frame(c, a * K.ease(K.ramp(u, 0.0, 0.3)))
    spaced(c, num, 540, 700, 64, "cormorant-500", 0.2, C.GOLD, a * k, tag="title")
    c.drawLine(540 - 160 * k, 740, 540 + 160 * k, 740, paint(C.GOLD, 0.8 * a, stroke=1.5))
    sweep = K.lin((-300 + 1700 * K.ramp(u, 0.1, 1.0), 0), (100 + 1700 * K.ramp(u, 0.1, 1.0), 0),
                  [C.GOLD, C.GOLD, C.GOLD_HI, WHITE, C.GOLD_HI, C.GOLD, C.GOLD], [0.0, 0.3, 0.45, 0.5, 0.55, 0.7, 1.0])
    size = 104 if len(title) <= 8 else (84 if len(title) <= 11 else 72)
    spaced(c, title, 540, 890, size, "italiana-400", 0.55 - 0.3 * k, C.GOLD_HI, a * K.ease(K.ramp(u, 0.0, 0.35)), tag="title", shader=sweep)
    spaced(c, sub.upper(), 540, 1000, 32, "cormorant-600", 0.45, mix(C.GOLD, WHITE, 0.35), a * K.ease(K.ramp(u, 0.12, 0.45)), tag="title")
    if eye:
        ek = K.ease(K.ramp(u, 0.2, 0.6))
        C.lens(c, 540, 1180, 30, T, open_=0.2 + 0.6 * ek, a=a * ek, ring=C.GOLD, coat=(150, 40, 60))


def title(c, T, t0, a=1.0, y=860):
    """GLASS: enormous thin capitals that assemble out of wide spacing, a band of light passing through them as if
    through a pane, and a hairline underneath."""
    u = T - t0
    k = K.ease(K.ramp(u, 0.0, 1.0))
    sweep = K.lin((-400 + 1900 * K.ramp(u, 0.1, 1.3), 0), (0 + 1900 * K.ramp(u, 0.1, 1.3), 0),
                  [(255, 255, 255, 0.55), (255, 255, 255, 0.55), (255, 255, 255, 1.0), (255, 255, 255, 0.55), (255, 255, 255, 0.55)], [0, 0.4, 0.5, 0.6, 1])
    spaced(c, "GLASS", 540, y + 4, 230, "italiana-400", 0.42 - 0.22 * k, (0, 0, 0), 0.35 * a * k, tag="title")
    spaced(c, "GLASS", 540, y, 230, "italiana-400", 0.42 - 0.22 * k, WHITE, a * k, tag="title", shader=sweep)
    c.drawLine(540 - 300 * k, y + 60, 540 + 300 * k, y + 60, paint(WHITE, 0.7 * a * k, stroke=1.5))
    spaced(c, "A DESCENT INTO THE MACHINE THAT WATCHES", 540, y + 120, 26, "cormorant-500", 0.32, WHITE, a * K.ease(K.ramp(u, 0.4, 1.0)), tag="title")

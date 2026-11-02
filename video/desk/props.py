"""Props: the lamp (the recurring object), the laptop and its chat, the graph, the five problems, the clocks, the
school bell, the old test paper, and the stage properties of the fiction register (desks, car, dials, the answer
box, paper cranes, lanterns)."""
import math

import numpy as np
import skia

import draw as D
from draw import (CREAM, GOLD, GOLDD, GOLDL, INK, JADE, LACQ, LAMP, PAPER, PINK, RED, VERM, WHITE, mix, paint, path)


# ------------------------------------------------------------------ the lamp

def desk_lamp(c, x, y, s, on=1.0, side=1, body=(40, 44, 44), glow=LAMP, cone=True, pool=True, pool_y=None):
    """An angled desk lamp standing at (x, y) (the base), its shade toward +x*side. Returns the bulb position."""
    c.save()
    c.translate(x, y)
    c.scale(s * side, s)
    c.drawOval(skia.Rect.MakeLTRB(-90, -24, 90, 10), paint(mix(body, INK, 0.3)))
    c.drawPath(D.capsule(0, -10, -30, -300, 18, 16), paint(body))
    c.drawCircle(-30, -300, 16, paint(mix(body, WHITE, 0.2)))
    c.drawPath(D.capsule(-30, -300, 140, -420, 16, 14), paint(body))
    c.save()
    c.translate(150, -420)
    c.rotate(38)
    shade = path([(-50, -30), (50, -30), (100, 90), (-100, 90)])
    c.drawPath(shade, paint(shader=D.lin((-100, 0), (100, 0), [mix(body, WHITE, 0.25), body, mix(body, INK, 0.4)])))
    c.drawOval(skia.Rect.MakeLTRB(-100, 70, 100, 110), paint(mix((60, 56, 50), glow, on)))
    m = c.getTotalMatrix()
    c.restore()
    c.restore()
    bulb = m.mapXY(0, 95)
    return bulb.x(), bulb.y()


def light_cone(c, bx, by, tx, ty, spread, on=1.0, color=LAMP, a=0.35):
    """A soft cone of light from the bulb (bx, by) toward (tx, ty), widening to `spread` px."""
    if on <= 0:
        return
    ang = math.atan2(ty - by, tx - bx)
    nx, ny = -math.sin(ang), math.cos(ang)
    p = path([(bx - nx * 30, by - ny * 30), (bx + nx * 30, by + ny * 30), (tx + nx * spread, ty + ny * spread),
              (tx - nx * spread, ty - ny * spread)])
    c.drawPath(p, paint(shader=D.lin((bx, by), (tx, ty), [(*color, 0.9), (*color, 0.0)]), a=a * on))
    c.drawCircle(bx, by, 60, paint(color, 0.5 * on, blur=30))
    c.drawCircle(bx, by, 14, paint(mix(color, WHITE, 0.7), on))


def pool_of_light(c, x, y, rx, ry, on=1.0, color=LAMP, a=0.5):
    c.save()
    c.translate(x, y)
    c.scale(1, ry / rx)
    c.drawCircle(0, 0, rx, paint(shader=D.rad((0, 0), rx, [(*color, 1.0), (*color, 0.35), (*color, 0.0)], [0, 0.5, 1]), a=a * on))
    c.restore()


def hanging_bulb(c, x, y, s, on=1.0, cord=400):
    c.drawLine(x, y - cord * s, x, y - 20 * s, paint((30, 30, 30), stroke=4 * s))
    c.drawPath(path([(x - 50 * s, y), (x + 50 * s, y), (x + 22 * s, y - 36 * s), (x - 22 * s, y - 36 * s)]), paint((50, 50, 50)))
    c.drawCircle(x, y + 12 * s, 18 * s, paint((255, 250, 230), 0.4 + 0.6 * on))
    c.drawCircle(x, y + 12 * s, 90 * s, paint((255, 245, 220), 0.35 * on, blur=40 * s))


def lantern(c, x, y, s, on=1.0, T=0.0, color=GOLDL, cord=600):
    """The fiction's lamp: a gold-leaf lantern on a long cord, glowing."""
    c.drawLine(x, y - cord, x, y - 70 * s, paint(GOLDD, stroke=3))
    c.drawCircle(x, y, 260 * s, paint(color, 0.22 * on, blur=90 * s))
    body = D.smooth([(x - 60 * s, y - 60 * s), (x, y - 80 * s), (x + 60 * s, y - 60 * s), (x + 70 * s, y + 10 * s),
                     (x + 50 * s, y + 70 * s), (x - 50 * s, y + 70 * s), (x - 70 * s, y + 10 * s)])
    c.drawPath(body, paint(shader=D.rad((x, y), 90 * s, [mix(color, WHITE, 0.6 * on), mix(GOLD, INK, 0.3 * (1 - on))])))
    for j in range(-2, 3):
        c.drawLine(x + j * 22 * s, y - 66 * s, x + j * 26 * s, y + 66 * s, paint(GOLDD, 0.5, stroke=2))
    c.drawRect(skia.Rect.MakeLTRB(x - 40 * s, y - 86 * s, x + 40 * s, y - 70 * s), paint(GOLDD))
    c.drawRect(skia.Rect.MakeLTRB(x - 40 * s, y + 68 * s, x + 40 * s, y + 82 * s), paint(GOLDD))


# ------------------------------------------------------------------ the laptop and the chat

def laptop_back(c, x, y, s, glow=(200, 220, 240), on=1.0):
    """A laptop seen from behind at (x, y) (the hinge), its screen glow spilling toward us."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawPath(path([(-200, 0), (200, 0), (186, -270), (-186, -270)]), paint((56, 58, 62)))
    c.drawPath(path([(-200, 0), (200, 0), (230, 26), (-230, 26)]), paint((80, 82, 86)))
    c.drawCircle(0, -140, 18, paint((100, 104, 110)))
    c.restore()
    c.drawCircle(x, y - 140 * s, 300 * s, paint(glow, 0.12 * on, blur=90 * s))


WRAP_W = 700


def _wrap(s, f, w):
    return D.wrap(s, f, w)


def chat(c, T, msgs, x0=90, y0=360, x1=990, y_bottom=1250, scale=1.0, dark=True, wrap=None):
    """A chat on a screen: msgs = [(who, text, t_start, t_type)] - 'me' types (characters appear over t_type),
    'tutor' answers (words appear). Newest at the bottom; older ones scroll up. Returns nothing."""
    bg = (26, 30, 36) if dark else (238, 238, 234)
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y_bottom), paint(bg))
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y0 + 70), paint(mix(bg, WHITE, 0.07)))
    D.text(c, "Tutor", (x0 + x1) / 2, y0 + 48, 32, "inter-700", (200, 206, 214), tag="ui")
    f = D.font("inter-500", 38 * scale)
    lh = 50 * scale
    blocks = []
    for who, txt, t0, dur in msgs:
        if T < t0:
            continue
        if who == "me":
            n = int(len(txt) * min(1.0, (T - t0) / max(0.05, dur)))
            shown = txt[:n] + ("|" if n < len(txt) and int(T * 3) % 2 == 0 else "")
        else:
            words = txt.split(" ")
            n = int(len(words) * min(1.0, (T - t0) / max(0.05, dur))) + 1
            shown = " ".join(words[:n])
        lines = _wrap(shown or " ", f, wrap or WRAP_W * scale) or [""]
        blocks.append((who, lines))
    y = y_bottom - 30
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x0, y0 + 72, x1, y_bottom))
    for who, lines in reversed(blocks):
        h = len(lines) * lh + 34 * scale
        w = max(f.measureText(l) for l in lines) + 50 * scale
        top = y - h
        if top < y0 + 76:                                               # no half-hidden bubbles under the header
            break
        if who == "me":
            bx1, bx0 = x1 - 30, x1 - 30 - w
            fill, ink = (84, 116, 150), WHITE
        else:
            bx0, bx1 = x0 + 30, x0 + 30 + w
            fill, ink = (52, 58, 66), (236, 238, 240)
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(bx0, top, bx1, y), 26, 26), paint(fill))
        for j, l in enumerate(lines):
            D.text(c, l, bx0 + 25 * scale, top + 17 * scale + (j + 1) * lh - 12 * scale, 38 * scale, "inter-500", ink,
                   align="left", tag="chat")
        y = top - 22
        if y < y0 + 80:
            break
    c.restore()


# ------------------------------------------------------------------ maths on paper and on screen

def graph(c, T, x0, y0, x1, y1, u, show_tangent=1.0, dark=True, label=True):
    """Distance against time, s = t^2 on 0..5, a point dragged to t = 5u, its tangent and the slope read out."""
    bg = (26, 30, 36) if dark else PAPER
    ink = (220, 226, 232) if dark else INK
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(bg))
    ox, oy = x0 + 110, y1 - 110
    wx, wy = (x1 - x0) - 170, (y1 - y0) - 200
    c.drawLine(ox, oy, ox + wx, oy, paint(ink, stroke=4))
    c.drawLine(ox, oy, ox, oy - wy, paint(ink, stroke=4))
    if label:
        D.text(c, "time", ox + wx - 40, oy + 60, 34, "inter-500", ink, tag="axis")
        c.save()
        c.translate(ox - 50, oy - wy + 120)
        c.rotate(-90)
        D.text(c, "distance", 0, 0, 34, "inter-500", ink, tag="axis")
        c.restore()
    X = lambda t: ox + wx * t / 5
    Y = lambda sv: oy - wy * sv / 25
    pts = [(X(t), Y(t * t)) for t in np.linspace(0, 5, 60)]
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    c.drawPath(p, paint((120, 190, 255), stroke=7))
    t = max(0.3, min(4.7, 5 * u))
    px, py = X(t), Y(t * t)
    if show_tangent > 0:
        m = 2 * t
        dt = 1.4
        c.drawLine(X(t - dt), Y(t * t - m * dt), X(t + dt), Y(t * t + m * dt), paint((255, 200, 90), show_tangent, stroke=6))
    c.drawCircle(px, py, 18, paint((255, 200, 90)))
    c.drawCircle(px, py, 30, paint((255, 200, 90), 0.4, stroke=4))
    if label:
        D.text(c, f"speed right now = {2 * t:.1f}", (x0 + x1) / 2, y0 + 80, 44, "inter-700", (255, 210, 110), tag="readout")


PROBLEMS = [("1.", "s = t²   speed at t = 3?", "6", True), ("2.", "s = 5t + 2   speed?", "5", True),
            ("3.", "d/dx  x³", "3x²", True), ("4.", "d/dx  (4x² − x)", "8x − 1", True),
            ("5.", "d/dx  (2x + 1)²", "2(2x + 1)", False)]


def problems(c, T, x0, y0, w, t0, per=0.9, marks_at=None, size=46):
    """The five problems on paper, her answers appearing one by one, then the ticks (and the one cross)."""
    c.drawRect(skia.Rect.MakeLTRB(x0 - 30, y0 - 90, x0 + w + 30, y0 + 5 * 150 + 20), paint((212, 206, 190)))
    for j in range(22):
        yy = y0 - 60 + j * 38
        c.drawLine(x0 - 30, yy, x0 + w + 30, yy, paint((170, 190, 210), 0.35, stroke=2))
    for i, (n, q, a, ok) in enumerate(PROBLEMS):
        y = y0 + i * 150
        D.text(c, n, x0, y, size, "courier-400", INK, align="left", tag="prob")
        D.text(c, q, x0 + 70, y, size, "courier-400", INK, align="left", tag="prob")
        k = ramp_(T, t0 + i * per, t0 + i * per + 0.5)
        if k > 0:
            D.text(c, "= " + a, x0 + 90, y + 64, size * 1.05, "cormorant-600", (40, 50, 110), align="left", tag="ans", a=k)
        if marks_at is not None and T > marks_at + i * 0.18:
            if ok:
                c.drawPath(path([(x0 + w - 70, y + 50), (x0 + w - 44, y + 76), (x0 + w, y + 20)], closed=False), paint(JADE, stroke=9))
            else:
                c.drawLine(x0 + w - 70, y + 20, x0 + w, y + 80, paint(RED, stroke=9))
                c.drawLine(x0 + w, y + 20, x0 + w - 70, y + 80, paint(RED, stroke=9))


def ramp_(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a))) if b > a else float(t >= a)


def working(c, T, cx, y, circle=0.0, fix=0.0, size=66):
    """Problem 5 up close: her line, the red ring round the missing factor, and the correction."""
    D.text(c, "d/dx (2x + 1)²", cx, y, size, "courier-400", INK, tag="work")
    D.text(c, "= 2(2x + 1)", cx, y + 120, size * 1.15, "cormorant-600", (40, 50, 110), tag="work")
    if circle > 0:
        c.save()
        c.translate(cx, y + 100)
        c.drawArc(skia.Rect.MakeLTRB(-230, -80, 230, 60), -90, 360 * circle, False, paint(RED, stroke=8))
        c.restore()
    if fix > 0:
        D.text(c, "the inside changes too:  × 2", cx, y + 250, size * 0.72, "cormorant-600", RED, tag="fix", a=fix)
        D.text(c, "= 4(2x + 1)", cx, y + 380, size * 1.25, "cormorant-700", (20, 110, 80), tag="fix2", a=fix)


# ------------------------------------------------------------------ clocks and bells

def wall_clock(c, x, y, r, hours, face=(236, 232, 222), rim=(40, 40, 40)):
    c.drawCircle(x, y, r * 1.08, paint(rim))
    c.drawCircle(x, y, r, paint(face))
    for i in range(12):
        a = i / 12 * 2 * math.pi
        c.drawLine(x + r * 0.84 * math.sin(a), y - r * 0.84 * math.cos(a), x + r * 0.95 * math.sin(a), y - r * 0.95 * math.cos(a),
                   paint(rim, stroke=max(2, r * 0.04)))
    hh = (hours % 12) / 12 * 2 * math.pi
    mm = (hours % 1) * 2 * math.pi
    c.drawLine(x, y, x + r * 0.5 * math.sin(hh), y - r * 0.5 * math.cos(hh), paint(rim, stroke=r * 0.07))
    c.drawLine(x, y, x + r * 0.78 * math.sin(mm), y - r * 0.78 * math.cos(mm), paint(rim, stroke=r * 0.045))
    c.drawCircle(x, y, r * 0.05, paint(rim))


def school_bell(c, x, y, s, T, ring=0.0):
    """A round wall bell with its striker, shaking while it rings."""
    j = 6 * ring * math.sin(T * 90)
    c.save()
    c.translate(x + j * s * 0.3, y)
    c.scale(s, s)
    c.drawRect(skia.Rect.MakeLTRB(-30, -260, 30, -150), paint((70, 70, 70)))
    c.drawCircle(0, 0, 160, paint(shader=D.rad((-50, -60), 220, [(240, 240, 240), (150, 150, 150), (60, 60, 60)])))
    c.drawCircle(0, 0, 160, paint((40, 40, 40), stroke=8))
    c.drawCircle(0, 0, 26, paint((50, 50, 50)))
    c.restore()
    c.save()
    c.translate(x + 150 * s, y + 150 * s)
    c.rotate(-30 + 18 * ring * math.sin(T * 110))
    c.drawLine(0, 0, 0, -120 * s, paint((40, 40, 40), stroke=14 * s))
    c.drawCircle(0, -120 * s, 24 * s, paint((60, 60, 60)))
    c.restore()


def old_test(c, x, y, s, T):
    """Her old maths test: a grade circled, and not one comment."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawRect(skia.Rect.MakeLTRB(-340, -440, 340, 440), paint((236, 236, 232)))
    D.text(c, "MATHEMATICS  ·  TEST 4", -300, -370, 32, "courier-400", INK, align="left", tag="test")
    for j in range(9):
        yy = -290 + j * 76
        c.drawLine(-300, yy, 120 + 40 * math.sin(j), yy, paint((120, 120, 120), stroke=5))
    c.drawCircle(230, -230, 90, paint((60, 60, 60), stroke=8))
    D.text(c, "C−", 230, -200, 110, "cormorant-700", (40, 40, 40), tag="grade")
    c.restore()


# ------------------------------------------------------------------ the fiction's properties

def lacquer_desk(c, x, y, s, top=LACQ, edge=GOLD, lit=0.0):
    """A low stage desk in black lacquer with a gold edge; (x, y) = front of the desktop."""
    c.drawPath(path([(x - 120 * s, y), (x + 120 * s, y), (x + 100 * s, y - 50 * s), (x - 100 * s, y - 50 * s)]), paint(top))
    c.drawLine(x - 120 * s, y, x + 120 * s, y, paint(edge, stroke=4 * s))
    c.drawRect(skia.Rect.MakeLTRB(x - 110 * s, y, x - 96 * s, y + 90 * s), paint(top))
    c.drawRect(skia.Rect.MakeLTRB(x + 96 * s, y, x + 110 * s, y + 90 * s), paint(top))
    if lit > 0:
        c.drawPath(path([(x - 100 * s, y - 50 * s), (x + 100 * s, y - 50 * s), (x + 120 * s, y), (x - 120 * s, y)]),
                   paint(GOLDL, 0.55 * lit))


def dial(c, x, y, r, frac, label, T, col=GOLD):
    """A gold stage dial (odometer or speedometer)."""
    c.drawCircle(x, y, r * 1.08, paint(GOLDD))
    c.drawCircle(x, y, r, paint(shader=D.rad((x - r * 0.3, y - r * 0.3), r * 1.3, [GOLDL, col, GOLDD])))
    for i in range(11):
        a = math.radians(-220 + i * 26)
        c.drawLine(x + r * 0.78 * math.cos(a), y + r * 0.78 * math.sin(a), x + r * 0.92 * math.cos(a), y + r * 0.92 * math.sin(a),
                   paint(LACQ, stroke=r * 0.03))
    a = math.radians(-220 + 260 * frac)
    c.drawLine(x, y, x + r * 0.8 * math.cos(a), y + r * 0.8 * math.sin(a), paint(VERM, stroke=r * 0.06))
    c.drawCircle(x, y, r * 0.08, paint(LACQ))
    D.text(c, label, x, y + r * 0.55, r * 0.2, "cormorant-700", LACQ, tag="dial")


def car(c, x, y, s, col=VERM):
    """A stylised stage car, all lacquer and gold, in profile."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    body = D.smooth([(-220, -40), (-200, -90), (-90, -110), (-40, -180), (80, -180), (140, -110), (220, -90), (230, -40)])
    c.drawPath(body, paint(shader=D.lin((0, -180), (0, -30), [mix(col, WHITE, 0.3), col, mix(col, INK, 0.3)])))
    c.drawPath(path([(-30, -168), (70, -168), (118, -112), (-70, -112)]), paint((40, 40, 60)))
    c.drawLine(-230, -60, 230, -60, paint(GOLD, stroke=6))
    for wx in (-130, 140):
        c.drawCircle(wx, -30, 50, paint(LACQ))
        c.drawCircle(wx, -30, 22, paint(GOLD))
    c.restore()


def answer_box(c, x, y, s, T, open_=1.0):
    """A vermilion lacquer box that dispenses answers on paper scrolls."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawRect(skia.Rect.MakeLTRB(-200, -300, 200, 0), paint(shader=D.lin((-200, 0), (200, 0), [mix(VERM, INK, 0.3), VERM, mix(VERM, INK, 0.45)])))
    c.drawRect(skia.Rect.MakeLTRB(-200, -300, 200, 0), paint(GOLD, stroke=8))
    c.drawRect(skia.Rect.MakeLTRB(-40, -220, 40, -140), paint(GOLD))
    c.save()
    c.translate(-200, -300)
    c.rotate(-50 * open_)
    c.drawRect(skia.Rect.MakeLTRB(0, -40, 400, 0), paint(mix(VERM, INK, 0.2)))
    c.drawRect(skia.Rect.MakeLTRB(0, -40, 400, 0), paint(GOLD, stroke=6))
    c.restore()
    c.restore()


def scroll(c, x, y, s, rot=0.0, text="ANSWER", a=1.0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    c.drawRect(skia.Rect.MakeLTRB(-90, -40, 90, 40), paint(CREAM, a))
    c.drawRect(skia.Rect.MakeLTRB(-100, -46, -86, 46), paint(GOLDD, a))
    c.drawRect(skia.Rect.MakeLTRB(86, -46, 100, 46), paint(GOLDD, a))
    D.text(c, text, 0, 12, 34, "cormorant-700", LACQ, tag="scroll", a=a)
    c.restore()


def crane(c, x, y, s, T, col=CREAM, flap=0.0):
    """A folded paper crane, wings beating."""
    w = 0.6 + 0.4 * math.sin(flap)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawPath(path([(-120, 0), (0, -20), (120, -40), (30, 20)]), paint(mix(col, INK, 0.12)))
    c.drawPath(path([(-20, -10), (40, -10), (10, -150 * w)]), paint(col))
    c.drawPath(path([(-10, 0), (50, 0), (60, 90 * w)]), paint(mix(col, INK, 0.2)))
    c.drawPath(path([(110, -36), (150, -80), (140, -34)]), paint(col))
    c.restore()


def banner(c, x, y, w, h, lines, bg=VERM, fg=CREAM, a=1.0, sizes=(64, 34), src=None, tag="banner"):
    """A cloth banner hung on the stage: a big line, a small line, a source."""
    c.drawRect(skia.Rect.MakeLTRB(x - w / 2, y - h / 2, x + w / 2, y + h / 2), paint(bg, a))
    c.drawRect(skia.Rect.MakeLTRB(x - w / 2 + 12, y - h / 2 + 12, x + w / 2 - 12, y + h / 2 - 12), paint(GOLD, a, stroke=3))
    c.drawLine(x - w / 2 - 20, y - h / 2, x + w / 2 + 20, y - h / 2, paint(GOLDD, a, stroke=10))
    n = len(lines)
    yy = y - h / 2 + 30
    for j, ln in enumerate(lines):
        size = sizes[0] if j == 0 else sizes[1]
        f = D.font("cormorant-700" if j == 0 else "cormorant-600", size)
        sz = min(size, size * (w - 70) / max(1, f.measureText(ln)))
        yy += sz * 1.12
        D.text(c, ln, x, yy, sz, "cormorant-700" if j == 0 else "cormorant-600", fg, tag=tag, a=a)
    if src:
        f = D.font("cormorant-500i", 30)
        sz = min(30, 30 * (w - 70) / max(1, f.measureText(src)))
        D.text(c, src, x, y + h / 2 - 26, sz, "cormorant-500i", mix(fg, bg, 0.2), tag=tag, a=a)


def envelope(c, x, y, s, T, open_=1.0):
    c.save()
    c.translate(x, y)
    c.rotate(-3)
    c.scale(s, s)
    c.drawRect(skia.Rect.MakeLTRB(-320, -200, 320, 200), paint((196, 186, 164)))
    c.drawRect(skia.Rect.MakeLTRB(-280, -330 * open_, 280, 120), paint((222, 218, 206)))
    if open_ > 0.5:
        D.text(c, "OFFER OF ADMISSION", 0, -240 * open_ + 20, 40, "cormorant-700", INK, tag="letter")
        D.text(c, "We are pleased to inform you…", 0, -170 * open_ + 30, 30, "cormorant-500i", (60, 60, 60), tag="letter")
    c.drawPath(path([(-320, -200), (0, 20), (320, -200), (320, 200), (-320, 200)]), paint((206, 196, 174)))
    c.restore()

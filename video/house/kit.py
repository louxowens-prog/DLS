"""Shared scene helpers: the AI's words as intertitle cards, the paint flood, stamps, the mini pictures in the album."""
import math

import numpy as np
import skia

import bg
import cast
import hx
from common import talk
from cues import count
from hx import BLOOD, CREAM, GOLD, INK, MINT, PEACH, PINK, PLUM, POWDER, W, H, bez, paint, path, stop
from script import AI, DOC, NAR


def backdrop(st, name, *args):
    st.c.drawImage(getattr(bg, name)(*args), 0, 0)


def ai_talk(T):
    return talk(T, AI)


def nar_talk(T):
    return talk(T, NAR)


def doc_talk(T):
    return talk(T, DOC)


def ai_card(c, s, T, t0, y=250, size=62, w=880, tag="aicard", horror=False):
    """What the chatbot says, as a little silent-film intertitle pinned into the shot (ornate border, old type)."""
    k = hx.pop(T, t0, 0.18, 0.12)
    if k <= 0:
        return None
    f = hx.font("fell-400-italic", size)
    lines = hx.wrap(s, f, w - 120)
    h = size * 1.2 * len(lines) + 90
    x0 = (W - w) / 2
    c.save()
    c.translate(W / 2, y + h / 2)
    c.scale(k, k)
    c.translate(-W / 2, -(y + h / 2))
    c.drawRect(skia.Rect.MakeLTRB(x0 + 10, y + 12, x0 + w + 10, y + h + 12), paint(INK, 0.5, blur=8))
    c.drawRect(skia.Rect.MakeLTRB(x0, y, x0 + w, y + h), paint((24, 10, 20) if not horror else (70, 0, 10)))
    hx.ornate_frame(c, x0 + 12, y + 12, x0 + w - 12, y + h - 12, CREAM if not horror else (255, 150, 140), w=4)
    yy = y + 45 + size * 0.85
    for ln in lines:
        hx.text(c, ln, W / 2, yy, size, "fell-400-italic", CREAM if not horror else (255, 200, 190), tag=tag)
        yy += size * 1.2
    c.restore()
    return (x0, y, x0 + w, y + h)


def stamp(c, s, x, y, size, T, t0, color=BLOOD, rot=-12, fname="shrikhand-400", tag="stamp", box=True, fill=None):
    """A rubber stamp slammed onto the picture."""
    k = hx.pop(T, t0, 0.14, 0.35)
    if k <= 0:
        return
    f = hx.font(fname, size)
    w = f.measureText(s)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(k, k)
    if box:
        r = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-w / 2 - 26, -size * 0.95, w / 2 + 26, size * 0.35), 16, 16)
        if fill is not None:
            c.drawRRect(r, paint(fill, 0.95))
        c.drawRRect(r, paint(color, 0.9, stroke=10))
    c.drawString(s, -w / 2, 0, f, paint(color, 0.95))
    hx.reg_local(c, -w / 2, -size * 0.78, w / 2, size * 0.22, tag)
    c.restore()


def check(c, x, y, s, T, t0, color=(40, 170, 90)):
    """A fat hand-drawn tick, slapped on."""
    k = hx.pop(T, t0, 0.14, 0.35)
    if k <= 0:
        return
    c.save()
    c.translate(x, y)
    c.scale(s * k, s * k)
    c.drawPath(path([(-60, 0), (-20, 45), (70, -60)], closed=False), paint(INK, 0.5, stroke=34))
    c.drawPath(path([(-60, 0), (-20, 45), (70, -60)], closed=False), paint(color, stroke=24))
    c.restore()


def flood(c, level, T, color=BLOOD, top=None):
    """Paint-red blood flooding the room from the floor up: a flat red sea with a wobbling, dripping surface."""
    if level <= 0:
        return
    y = H - level
    t = stop(T, 12)
    pts = [(0, H), (0, y)]
    for i in range(25):
        x = i * W / 24
        pts.append((x, y + 18 * math.sin(x / 70 + t * 4) + 10 * math.sin(x / 23 - t * 7)))
    pts += [(W, y), (W, H)]
    c.drawPath(path(pts), paint(color))
    c.drawPath(path(pts[1:-1], closed=False), paint((255, 90, 90), 0.6, stroke=6))
    rng = np.random.default_rng(int(t * 12) % 7)
    for i in range(6):
        hx.drip(c, rng.uniform(40, W - 40), y - rng.uniform(0, 40), rng.uniform(10, 18), rng.uniform(20, 70), color)


def top_drips(c, T, n=9, color=BLOOD, grow=1.0, seed=3):
    """Red paint running down from the top of the frame."""
    rng = np.random.default_rng(seed)
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 60 * grow), paint(color))
    for i in range(n):
        x = rng.uniform(30, W - 30)
        L = (rng.uniform(80, 360) + 120 * stop(T, 8)) * grow
        hx.drip(c, x, 40, rng.uniform(14, 30), L % (700 * grow + 1), color)


def sticker(c, kind, x, y, s, T, t0=-9.0, rot=0.0):
    """A collage sticker slapped onto the picture (heart, star, lips, eye), cut out with a white paper edge."""
    k = hx.pop(T, t0, 0.14, 0.4)
    if k <= 0:
        return
    jx, jy, jr = hx.jit(T, 1.5, seed=int(x * 7 + y), fps=8)
    c.save()
    c.translate(x + jx, y + jy)
    c.rotate(rot + jr * 2)
    c.scale(s * k, s * k)
    with hx.figure(c, border=9, fringe=(-6, -3), shadow=(8, 10, 6, 0.45)) as F:
        if kind == "heart":
            p = skia.Path()
            p.moveTo(0, 60)
            p.cubicTo(-90, 0, -40, -70, 0, -25)
            p.cubicTo(40, -70, 90, 0, 0, 60)
            F.fill(p, (255, 80, 130))
        elif kind == "star":
            pts = []
            for i in range(10):
                a = -math.pi / 2 + math.pi / 5 * i
                q = 70 if i % 2 == 0 else 30
                pts.append((q * math.cos(a), q * math.sin(a)))
            F.poly(pts, GOLD)
        elif kind == "lips":
            F.poly([(-80, 0), (-40, -34), (0, -20), (40, -34), (80, 0), (40, 36), (-40, 36)], (230, 20, 60))
        elif kind == "eye":
            F.oval(-80, -44, 80, 44, (255, 255, 255))
    if kind == "lips":
        c.drawPath(path([(-70, 2), (0, 8), (70, 2)], closed=False), paint((120, 0, 30), stroke=6))
        c.drawOval(skia.Rect.MakeLTRB(-30, -24, 0, -14), paint(WHITE_, 0.6))
    elif kind == "eye":
        c.drawCircle(0, 0, 32, paint((60, 140, 220)))
        c.drawCircle(0, 0, 15, paint(INK))
        c.drawCircle(-9, -9, 6, paint(WHITE_))
        c.drawOval(skia.Rect.MakeLTRB(-80, -44, 80, 44), paint(INK, stroke=5))
    elif kind == "heart":
        c.drawOval(skia.Rect.MakeLTRB(-50, -30, -24, -8), paint(WHITE_, 0.6))
    c.restore()


def dramatized(c, x, y, T=0.0):
    """An honest label on the reconstructed chat: this is a dramatization, not the real log."""
    f = hx.font("special-elite-400", 30)
    s = "DRAMATIZATION"
    w = f.measureText(s)
    c.save()
    c.translate(x, y)
    c.rotate(4)
    c.drawRect(skia.Rect.MakeLTRB(-w / 2 - 18, -34, w / 2 + 18, 14), paint(INK, 0.85))
    c.drawRect(skia.Rect.MakeLTRB(-w / 2 - 18, -34, w / 2 + 18, 14), paint(CREAM, stroke=3))
    c.drawString(s, -w / 2, 0, f, paint(CREAM))
    hx.reg_local(c, -w / 2, -26, w / 2, 8, "tag")
    c.restore()


def odometer(c, x, y, value, digits=8, cw=96, ch=150, T=0.0, roll=0.0, color=(255, 236, 190), bg=(20, 10, 16)):
    """A mechanical tally counter: brass case, drum digits rolling over (with commas), the last drum mid-roll."""
    groups = digits + (digits - 1) // 3
    w = groups * cw * 0.86 + 60
    with hx.figure(c) as F:
        F.rrect(x - w / 2, y - ch / 2 - 34, x + w / 2, y + ch / 2 + 34, 22, (200, 150, 60))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x - w / 2 + 10, y - ch / 2 - 24, x + w / 2 - 10, y + ch / 2 + 24), 16, 16),
                paint((150, 100, 30), stroke=5))
    sv = f"{int(value):0{digits}d}"
    f = hx.font("fell-sc-400", int(ch * 0.78))
    xx = x - w / 2 + 30
    left = x - w / 2 + 30
    for i, dch in enumerate(sv):
        if i and (digits - i) % 3 == 0:
            c.drawString(",", xx + 2, y + ch * 0.36, f, paint(INK))
            xx += cw * 0.3
        c.drawRect(skia.Rect.MakeLTRB(xx, y - ch / 2, xx + cw * 0.84, y + ch / 2), paint(bg))
        off = roll * ch if i == digits - 1 else 0.0
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(xx, y - ch / 2, xx + cw * 0.84, y + ch / 2))
        dw = f.measureText(dch)
        c.drawString(dch, xx + cw * 0.42 - dw / 2, y + ch * 0.28 - off, f, paint(color))
        if off:
            nd = str((int(dch) + 1) % 10)
            c.drawString(nd, xx + cw * 0.42 - f.measureText(nd) / 2, y + ch * 0.28 - off + ch, f, paint(color))
        c.drawRect(skia.Rect.MakeLTRB(xx, y - ch / 2, xx + cw * 0.84, y - ch / 2 + ch * 0.22), paint(INK, 0.45))
        c.drawRect(skia.Rect.MakeLTRB(xx, y + ch / 2 - ch * 0.22, xx + cw * 0.84, y + ch / 2), paint(INK, 0.45))
        c.restore()
        xx += cw * 0.86
    hx.reg(left, y - ch / 2, xx, y + ch / 2, "odometer")
    return w


def count_now(T):
    return count(T)


# ------------------------------------------------------------------ the album's little pictures (cached)

def _mini(w, h, fn, bgcol, sc=1):
    arr = np.zeros((h * sc, w * sc, 4), np.uint8)
    arr[..., :3] = bgcol
    arr[..., 3] = 255
    s = skia.Surface(arr)
    c = s.getCanvas()
    c.scale(sc, sc)
    fn(c, w, h)
    return arr


def mini(name, w=440, h=330, sc=1):
    """Nine little pictures for 'the kinds of wrong', each a gag drawn in the film's collage style."""
    def facts(c, w, h):
        c.drawImage(hx.image(hx.painted_sky(w, h, seed=51)), 0, 0)
        for dx in (0, 150):                                              # a sky with two moons, printed as fact
            c.drawCircle(120 + dx, 100 + dx * 0.2, 44 - dx * 0.1, paint(CREAM))
            c.drawCircle(104 + dx, 90 + dx * 0.2, 10, paint((220, 210, 190)))
        with hx.figure(c, border=4, fringe=(-3, -2), shadow=(5, 6, 3, 0.4)) as F:   # a pig with wings
            F.oval(200, 200, 330, 280, (255, 170, 190))
            F.circle(330, 220, 34, (255, 170, 190))
            F.poly([(240, 210), (200, 150), (280, 190)], WHITE_)
        c.drawCircle(340, 214, 5, paint(INK))

    def quote(c, w, h):
        c.drawColor(hx.col((230, 210, 180)))
        c.drawOval(skia.Rect.MakeLTRB(60, 50, 240, 290), paint((150, 110, 70)))
        c.drawOval(skia.Rect.MakeLTRB(80, 70, 220, 270), paint((236, 214, 190)))
        c.drawOval(skia.Rect.MakeLTRB(95, 180, 205, 272), paint((110, 90, 80)))            # a grand beard
        for sx in (-1, 1):
            c.drawCircle(150 + sx * 22, 150, 6, paint(INK))
        b = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(250, 60, 420, 180), 30, 30)
        c.drawRRect(b, paint(WHITE_))
        c.drawPath(path([(260, 150), (230, 200), (290, 170)]), paint(WHITE_))
        f = hx.font("fell-400", 110)
        c.drawString("“ ”", 280, 170, f, paint(INK))
        c.drawLine(250, 60, 420, 180, paint(BLOOD, stroke=10))

    def math_(c, w, h):
        c.drawColor(hx.col((40, 70, 60)))
        c.drawRect(skia.Rect.MakeLTRB(0, 0, w, h), paint((150, 100, 60), stroke=24))
        f = hx.font("caveat-700", 110)
        c.drawString("7 × 8 = 54", 40, 200, f, paint((240, 240, 230)))

    def court(c, w, h):
        c.drawColor(hx.col((120, 70, 44)))
        c.drawRect(skia.Rect.MakeLTRB(60, 60, 300, 290), paint((230, 200, 140)))
        c.drawRect(skia.Rect.MakeLTRB(60, 60, 300, 110), paint((200, 160, 100)))
        f = hx.font("special-elite-400", 26)
        c.drawString("SMITH v. NOBODY", 72, 150, f, paint(INK))
        for k in range(4):
            c.drawRect(skia.Rect.MakeLTRB(72, 180 + k * 24, 280 - k * 20, 188 + k * 24), paint(INK, 0.6))
        c.save()
        c.translate(340, 170)
        c.rotate(-35)
        c.drawRect(skia.Rect.MakeLTRB(-10, -10, 120, 10), paint((110, 60, 30)))
        c.drawRect(skia.Rect.MakeLTRB(-50, -40, 10, 40), paint((140, 80, 36)))
        c.restore()

    def medical(c, w, h):
        c.drawColor(hx.col((200, 236, 230)))
        with hx.figure(c, border=4, fringe=(-3, -2), shadow=(5, 6, 3, 0.4)) as F:
            F.rrect(150, 90, 290, 300, 18, (255, 190, 120))
            F.rrect(140, 50, 300, 100, 10, WHITE_)
        c.drawRect(skia.Rect.MakeLTRB(160, 150, 280, 260), paint(WHITE_))
        c.drawCircle(220, 190, 26, paint(INK))
        for sx in (-1, 1):
            c.drawCircle(220 + sx * 10, 186, 6, paint(WHITE_))
        c.drawLine(180, 225, 260, 250, paint(INK, stroke=8))
        c.drawLine(180, 250, 260, 225, paint(INK, stroke=8))

    def history(c, w, h):
        c.drawImage(hx.image(hx.painted_sky(w, h, seed=57)), 0, 0)
        c.drawRect(skia.Rect.MakeLTRB(0, 250, w, h), paint((70, 60, 40)))
        with hx.figure(c, border=4, fringe=(-3, -2), shadow=(5, 6, 3, 0.4)) as F:   # a knight riding a dinosaur
            F.oval(110, 170, 330, 260, (110, 170, 90))
            F.poly([(300, 190), (380, 110), (400, 130), (330, 220)], (110, 170, 90))
            F.circle(395, 115, 26, (110, 170, 90))
            F.poly([(110, 210), (40, 240), (120, 240)], (110, 170, 90))
            for lx in (150, 270):
                F.rrect(lx, 240, lx + 26, 300, 8, (110, 170, 90))
            F.rrect(200, 110, 240, 190, 10, (190, 190, 200))
            F.circle(220, 100, 20, (190, 190, 200))
        c.drawLine(236, 120, 290, 40, paint((200, 200, 210), stroke=6))

    def code(c, w, h):
        c.drawColor(hx.col((60, 40, 70)))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(40, 30, 400, 280), 24, 24), paint((220, 210, 190)))
        c.drawRect(skia.Rect.MakeLTRB(70, 55, 370, 255), paint((10, 30, 20)))
        rng = np.random.default_rng(3)
        for k in range(8):
            c.drawRect(skia.Rect.MakeLTRB(84 + (k % 3) * 20, 70 + k * 22, 84 + (k % 3) * 20 + rng.uniform(80, 220), 80 + k * 22),
                       paint((90, 255, 140) if k != 4 else BLOOD))
        c.drawOval(skia.Rect.MakeLTRB(230, 140, 300, 200), paint(INK))                  # a bug in the code
        for k in range(3):
            for sx in (-1, 1):
                c.drawLine(265 + sx * 30, 150 + k * 18, 265 + sx * 60, 140 + k * 22, paint(INK, stroke=5))
        c.drawCircle(265, 132, 16, paint(INK))

    def cite(c, w, h):
        c.drawColor(hx.col((250, 244, 228)))
        for k in range(6):
            c.drawRect(skia.Rect.MakeLTRB(40, 40 + k * 26, 300 - (k % 3) * 30, 50 + k * 26), paint(INK, 0.5))
        f = hx.font("fell-400", 40)
        c.drawString("[1]", 300, 70, f, paint(BLOOD))
        for k in range(26):                                               # the footnote points into a void
            a = k * 0.55
            r = 60 - k * 2.2
            c.drawCircle(330 + r * math.cos(a), 230 + r * math.sin(a), 8, paint(INK, 0.9))
        c.drawLine(320, 80, 330, 170, paint(BLOOD, stroke=6))
        c.drawPath(path([(318, 160), (342, 162), (330, 186)]), paint(BLOOD))

    def docs(c, w, h):
        c.drawColor(hx.col((200, 190, 230)))
        c.save()
        c.translate(150, 170)
        c.rotate(180)
        c.drawRect(skia.Rect.MakeLTRB(-100, -130, 100, 130), paint(WHITE_))
        f = hx.font("special-elite-400", 24)
        c.drawString("CONTRACT", -70, -90, f, paint(INK))
        for k in range(6):
            c.drawRect(skia.Rect.MakeLTRB(-80, -60 + k * 26, 80 - (k % 2) * 30, -52 + k * 26), paint(INK, 0.5))
        c.restore()
        c.drawOval(skia.Rect.MakeLTRB(270, 110, 410, 210), paint(WHITE_))                # a big eye, reading it wrong
        c.drawCircle(330, 165, 34, paint((80, 150, 230)))
        c.drawCircle(330, 165, 16, paint(INK))
        c.drawOval(skia.Rect.MakeLTRB(270, 110, 410, 210), paint(INK, stroke=6))

    def news(c, w, h):
        c.drawColor(hx.col((244, 238, 222)))
        f1, f2 = hx.font("fell-sc-400", 64), hx.font("shrikhand-400", 34)
        c.drawString("EXTRA!", w / 2 - f1.measureText("EXTRA!") / 2, 80, f1, paint(INK))
        c.drawLine(30, 100, w - 30, 100, paint(INK, stroke=4))
        for i, ln in enumerate(("MOON MADE OF", "CHEESE, STUDY FINDS")):
            c.drawString(ln, w / 2 - f2.measureText(ln) / 2, 150 + i * 44, f2, paint(INK))
        c.drawCircle(110, 265, 40, paint((230, 210, 120)))
        for k in range(4):
            c.drawRect(skia.Rect.MakeLTRB(170, 235 + k * 18, w - 40 - (k % 2) * 40, 243 + k * 18), paint(INK, 0.5))

    fns = {"facts": facts, "quote": quote, "math": math_, "court": court, "medical": medical, "history": history,
           "code": code, "cite": cite, "docs": docs, "news": news}
    return hx.cached(f"mini_{name}_{sc}", lambda: _mini(w, h, fns[name], (250, 240, 230), sc))


WHITE_ = (255, 255, 255)

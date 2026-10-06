"""Inside the villa: the gallery of graduates; the examination table; Clara's double, painted in 1874 with a
ghostwriter at her ear; the writing room where the same night repeats, year after year; a cabinet of a hundred
porcelain scholars; the Governess's ledger; the final year."""
import math

import numpy as np
import skia

import cast as CA
import gel as G
import kit as K
import pers as P
import props as PR
import sets as SE
from common import E, Layers, S, Wx, blink, hit, shake, talk, zoom
from edit import cut, end
from kit import AMBER, BLACK, COBALT, EMERALD, GOLD, INK, MAGENTA, PAPER, WHITE, H, W, mix, paint, ramp


def _portrait(q, key, w, h):
    """A painted graduate in a gallery portrait: dark ground, a pale face, a gown and a mortarboard."""
    k, side = key
    rng = K.rng_at(k + 3, side + 5)
    q.drawPaint(paint(mix((40, 30, 24), (20, 30, 40), rng.uniform(0, 1))))
    cx = w / 2
    q.drawPath(K.smooth([(cx - w * 0.42, h), (cx - w * 0.38, h * 0.62), (cx, h * 0.52), (cx + w * 0.38, h * 0.62), (cx + w * 0.42, h)]), paint((20, 16, 22)))
    q.drawPath(K.smooth([(cx - w * 0.2, h * 0.58), (cx, h * 0.7), (cx + w * 0.2, h * 0.58), (cx, h * 0.62)]), paint((150, 20, 40)))
    q.drawOval(skia.Rect.MakeLTRB(cx - w * 0.17, h * 0.22, cx + w * 0.17, h * 0.5), paint((236, 222, 206)))
    for s in (-1, 1):
        q.drawCircle(cx + s * w * 0.07, h * 0.34, w * 0.022, paint((30, 24, 26)))
    q.drawOval(skia.Rect.MakeLTRB(cx - w * 0.04, h * 0.43, cx + w * 0.04, h * 0.45), paint((170, 40, 50)))
    q.drawPath(K.path([(cx - w * 0.3, h * 0.2), (cx, h * 0.12), (cx + w * 0.3, h * 0.2), (cx, h * 0.26)]), paint((20, 18, 24)))
    q.drawPaint(paint(shader=K.rad((cx, h * 0.35), h * 0.8, [(0, 0, 0, 0.0), (0, 0, 0, 0.55)])))


def s_g_gallery(T, idx):
    """Perfect work, with almost no understanding behind it: the gallery of graduates, mannequins in gowns holding
    flawless essays, Clara walking between them."""
    st = K.Stage()
    c = st.c
    t0 = cut("g_gallery")
    u = T - t0
    cam = P.Cam(pos=(0.0, 1.6, 0.55 * u), f=820, pitch=-1)
    SE.gallery(c, cam, T, portraits=_portrait, seed=2, drapes=(100, 8, 30), fresco=True)
    SE.fog_end(c, cam, cam.pos[2] + 26, r=420)
    figs = []
    for i in range(7):
        side = -1 if i % 2 == 0 else 1
        z = 2.5 + i * 2.4
        figs.append((z, side))
    for n_, (z, side) in enumerate(sorted(figs, reverse=True)):
        pos = (side * 1.45, 0.0, z)
        q = cam.proj(pos)
        if q is None:
            continue
        sc = cam.scale_at(pos) * 2.0 / 1000
        fa = 1 - P.fog_at(cam, pos, density=0.07)
        head = 0.0
        if n_ == 4:                                            # as she passes, this one turns its head to watch her
            head = -0.8 * K.ease(ramp(T, t0 + 1.3, t0 + 2.0))
        CA.mannequin(c, q[0], q[1], sc, T, pose=[1, 0, 3, 1, 2, 0, 3][n_], head=head * side, gown=True, cap=True, L=(255, 90, 190), R=(80, 255, 170), a=fa,
                     face_k=0.95)
        PR.paper(c, q[0] + side * -20 * sc * 10, q[1] - 560 * sc, 140 * sc * 1.4, 190 * sc * 1.4, side * 8, T, lines=6, seed=int(z * 10), a=fa)
    pos = (0.0, 0.0, cam.pos[2] + 3.4)
    q = cam.proj(pos)
    CA.walker_back(c, q[0], q[1], cam.scale_at(pos) * 1.72 / 900, T, key=(255, 60, 170), rim=(60, 230, 150))
    return st.arr


def _glove(c, x, y, s, T):
    """The Governess's hand in a black lace glove, holding something by its right edge: fingers above, thumb below, a
    lace cuff, a cameo ring; a magenta rim of light along the knuckles."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    glove, rim = (44, 32, 52), (255, 90, 190)
    c.drawPath(K.smooth([(60, -70), (300, -120), (340, 50), (90, 90), (40, 40)]), paint((26, 18, 30)))      # the sleeve
    c.drawPath(K.smooth([(-20, -60), (70, -80), (110, 0), (80, 70), (-10, 60), (-40, 0)]), paint(glove))     # the palm
    for k, (fx, fy, ln) in enumerate(((-30, -50, 120), (-40, -24, 130), (-36, 2, 118), (-26, 26, 96))):       # fingers over the edge
        c.drawPath(K.capsule(fx + 40, fy, fx + 40 - ln, fy + 6 + k * 2, 30, 22), paint(glove))
        c.drawLine(fx + 30, fy - 11, fx + 50 - ln, fy - 7 + k * 2, paint(rim, 0.85, stroke=5))
        c.drawCircle(fx + 40 - ln, fy + 6 + k * 2, 10, paint((70, 56, 84)))
        for q in range(4):                                                                                     # lace mesh on the glove
            c.drawCircle(fx + 20 - q * ln / 4, fy + 4 + k * 2, 4, paint((120, 104, 136), 0.6, stroke=1.5))
    c.drawPath(K.capsule(10, 64, -70, 96, 30, 24), paint(glove))                                          # the thumb, beneath
    c.drawLine(0, 52, -66, 84, paint((80, 120, 255), 0.7, stroke=4))
    for k in range(9):                                                                                         # lace at the cuff
        a = k / 8
        c.drawCircle(70 + 24 * a, -78 + 160 * a, 11, paint((150, 136, 160), 0.95))
        c.drawCircle(70 + 24 * a, -78 + 160 * a, 5, paint((26, 18, 30)))
    c.drawCircle(-50, -26, 18, paint(GOLD))                                                                    # the cameo ring
    c.drawCircle(-50, -26, 11, paint((240, 230, 220)))
    c.drawCircle(-56, -32, 4, paint(WHITE, 0.9))
    c.restore()


def _script(c, x, y, w, h, ang, crisp, seed, a=1.0):
    """An exam script: aged paper with a hand's uneven ink, or (crisp) a perfect white page of even typed lines."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.drawRect(skia.Rect.MakeLTRB(-w / 2 + 6, -h / 2 + 8, w / 2 + 6, h / 2 + 8), paint((0, 0, 0), 0.35 * a, blur=6))
    c.drawRect(skia.Rect.MakeLTRB(-w / 2, -h / 2, w / 2, h / 2), paint((196, 200, 208) if crisp else (214, 196, 160), a))
    rng = K.rng_at(seed, 17)
    for k in range(12):
        yy = -h / 2 + 70 + k * (h - 110) / 12
        if crisp:
            c.drawLine(-w / 2 + 40, yy, w / 2 - 40 - (90 if k % 4 == 3 else 0), yy, paint((50, 52, 62), 0.85 * a, stroke=5))
        else:
            p = skia.Path()
            xx = -w / 2 + 40
            p.moveTo(xx, yy)
            while xx < w / 2 - 50 - rng.uniform(0, 80):
                xx += rng.uniform(20, 40)
                p.lineTo(xx, yy + rng.uniform(-5, 5))
            c.drawPath(p, paint((60, 50, 90), 0.75 * a, stroke=3.5))
    if crisp:
        c.drawCircle(w / 2 - 70, -h / 2 + 70, 34, paint((200, 30, 40), 0.9 * a, stroke=5))
    c.restore()


def s_g_exam(T, idx):
    """At a UK university, researchers slipped AI answers into real online exams: the examiners' table, then close on
    the pile of handwritten scripts as a black-gloved hand slides a perfect one in among them. 94% went undetected:
    PASSED, PASSED, PASSED. On average they outscored the real students: two marble columns, the AI's half a grade
    higher."""
    st = K.Stage((6, 4, 6))
    c = st.c
    t0 = cut("g_exam")
    t94 = Wx("g2", "Ninety-four")
    tav = Wx("g2", "On")
    t_slip = Wx("g2", "researchers") - 0.1
    t_board = t94 - 0.25
    t_cols = tav - 0.15
    flagged = {7, 22}
    rng0 = K.rng_at(33, 3)
    tilts = [rng0.uniform(-5, 5) for _ in range(33)]

    def light(cc):
        G.pool(cc, 540, 800, 760, AMBER, 1.0)
        G.pool(cc, 100, 300, 500, MAGENTA, 0.6)
        G.pool(cc, 980, 1400, 500, EMERALD, 0.5)

    if t_slip <= T < t_board:                                   # close: the hand slips a perfect script into the pile
        zoom(c, T, t_slip, t_board + 0.3, 1.0, 1.14, cx=500, cy=980)

        def albedo2(cc):
            cc.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((34, 76, 46)))
            rng = K.rng_at(71, 2)
            for i in range(400):
                cc.drawCircle(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(1, 3), paint((20, 50, 30), 0.6))

        def light2(cc):
            G.pool(cc, 430, 950, 820, AMBER, 1.0)
            G.pool(cc, 1000, 620, 620, MAGENTA, 0.7)
            G.pool(cc, 160, 1500, 600, EMERALD, 0.5)
        SE.lit2d(c, albedo2, light2, amb=(16, 12, 16))
        u = K.ease(ramp(T, t_slip + 0.2, t_board - 0.6))
        rng = K.rng_at(72, 1)
        offs = [(rng.uniform(-22, 22), rng.uniform(-14, 14), rng.uniform(-5, 5)) for _ in range(9)]
        px, py = 470, 960
        for i in range(9):
            if i == 5:
                sx = px + 520 * (1 - u)
                _script(c, sx, py - 6, 520, 680, -2 + 3 * (1 - u), True, 99)
                hold = (sx + 255, py - 40)
            dx, dy, ang = offs[i]
            _script(c, px + dx, py + dy - i * 3, 520, 680, ang, False, i)
        G.pool(c, 420, 760, 420, AMBER, 0.25)
        if u < 1.0 or T < t_board - 0.2:                        # the hand lets go and withdraws
            back = K.ease(ramp(T, t_board - 0.5, t_board - 0.05))
            _glove(c, hold[0] + 560 * back, hold[1], 1.8, T)
        c.restore()
        return st.arr

    if T >= t_cols:                                             # two marble columns: the AI's half a grade higher
        zoom(c, T, t_cols, end("g_exam"), 1.0, 1.1, cx=540, cy=860)
        G.pool(c, 540, 820, 760, (120, 30, 60), 0.6)
        G.pool(c, 330, 900, 420, AMBER, 0.5)
        grow = K.ease(ramp(T, t_cols + 0.2, t_cols + 1.3))
        for i, (lab, hh, col) in enumerate((("AI ANSWERS", 600, (210, 202, 192)), ("REAL STUDENTS", 545, (150, 140, 132)))):
            x = 330 + i * 420
            top = 1200 - hh * grow
            c.drawRect(skia.Rect.MakeLTRB(x - 90, top, x + 90, 1200), paint(col))
            for k in range(5):
                c.drawLine(x - 70 + k * 35, top + 20, x - 70 + k * 35, 1190, paint(mix(col, BLACK, 0.2), stroke=4))
            c.drawRect(skia.Rect.MakeLTRB(x - 110, top - 30, x + 110, top), paint(mix(col, WHITE, 0.2)))
            c.drawRect(skia.Rect.MakeLTRB(x - 120, 1200, x + 120, 1240), paint(mix(col, BLACK, 0.15)))
            K.text(c, lab, x, 1290, 38, "cinzel-600", (240, 230, 214), tag="label")
        kl = K.ease(ramp(T, t_cols + 1.2, t_cols + 1.6))
        if kl > 0:
            top = 1200 - 600
            K.text(c, "+\u00bd GRADE", 330, top - 60, 50, "cinzel-800", (255, 90, 110), tag="label", a=kl)
        c.restore()
        PR.plaque(c, 540, 330, ["AVERAGE MARK"], size=52, tag="plaque")
        return st.arr

    # the examiners' table: the scripts slide in; then the stamps
    if T >= t_board:
        zoom(c, T, t_board, t_cols, 1.0, 1.12, cx=540, cy=820)
    else:
        zoom(c, T, t0, t_slip + 0.3, 1.0, 1.06, cx=540, cy=820)

    def albedo(cc):
        cc.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((90, 20, 30)))
        cc.drawRect(skia.Rect.MakeLTRB(40, 380, 1040, 1320), paint((70, 44, 26)))      # the examiners' table, from above
        cc.drawRect(skia.Rect.MakeLTRB(70, 410, 1010, 1290), paint((30, 70, 40)))      # green baize
        n_in = 33 if T >= t_board else int(min(33, max(0, (T - t0) / 0.05)))
        for i in range(n_in):
            r_, k_ = divmod(i, 6)
            x, y = 160 + k_ * 152, 500 + r_ * 140
            PR.paper(cc, x, y, 116, 128, tilts[i], T, grade=None, lines=5, seed=i)
    SE.lit2d(c, albedo, light, amb=(18, 12, 16))
    for i in range(33):
        r_, k_ = divmod(i, 6)
        x, y = 160 + k_ * 152, 500 + r_ * 140
        ts = t94 + 0.02 + i * 0.022
        if T > ts:
            kk = K.ease(ramp(T, ts, ts + 0.1))
            c.save()
            c.translate(x, y + 6)
            c.rotate(-14)
            c.scale(1.7 - 0.7 * kk, 1.7 - 0.7 * kk)
            col = (24, 24, 30) if i in flagged else (210, 20, 34)
            word = "FLAGGED" if i in flagged else "PASSED"
            c.drawRoundRect(skia.Rect.MakeLTRB(-56, -22, 56, 22), 4, 4, paint(col, kk, stroke=5))
            K.text(c, word, 0, 11, 27 if i not in flagged else 23, "cinzel-800", col, tag="deco", a=kk)
            c.restore()
    c.restore()
    if T > t94:                                                 # the plaque stays put while the lens pushes in
        kk = K.ease(ramp(T, t94, t94 + 0.4))
        PR.plaque(c, 540, 300, ["94% UNDETECTED"], size=60, a=kk, tag="plaque")
    return st.arr


def s_g_double(T, idx):
    """Ghostwriters aren't new: behind Clara, a portrait painted in 1874 of a graduate with her face, a dark figure
    whispering into her ear with a quill. The focus pulls from Clara to the painting."""
    L = Layers(2, bg=(4, 2, 4))
    t0 = cut("g_double")
    far = L.c(0)
    zoom(far, T, t0, end("g_double"), 1.0, 1.07, cx=600, cy=700)
    far.save()
    far.translate(0, -60)
    G.pool(far, 600, 700, 800, (120, 20, 40), 0.7)
    x0, y0, x1, y1 = 260, 260, 960, 1220
    far.save()
    far.clipRect(skia.Rect.MakeLTRB(x0, y0, x1, y1))
    far.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint((36, 28, 22)))
    G.pool(far, 600, 600, 500, (200, 150, 90), 0.5)
    far.drawPath(K.smooth([(760, 1220), (770, 700), (840, 520), (900, 560), (930, 800), (930, 1220)]), paint((10, 8, 8)))
    far.drawCircle(860, 470, 62, paint((10, 8, 8)))
    q = skia.Path()
    q.moveTo(800, 600)
    q.quadTo(720, 560, 690, 520)
    far.drawPath(q, paint((10, 8, 8), stroke=14))
    far.drawLine(690, 520, 660, 470, paint((230, 220, 200), stroke=4))
    CA.face(far, 560, 640, 0.95, "clara", T, L=(230, 170, 110), R=(120, 90, 70), core=0.3, expr="blank", porc=0.15,
            amb=(50, 40, 34), gaze=(0.3, 0.0), blink=0.0)
    far.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(shader=K.rad((600, 700), 700, [(0, 0, 0, 0.0), (20, 10, 0, 0.55)])))
    far.restore()
    PR.frame_gilt(far, x0, y0, x1, y1, t=34)
    PR.plaque(far, 610, 1296, ["C. A.  1874"], size=34, tag="plaque")
    far.restore()
    far.restore()
    near = L.c(1)
    CA.face(near, 250, 1150, 1.45, "clara", T, L=(255, 60, 170), R=(40, 220, 140), core=0.5, expr="dread",
            blink=blink(T, 8), gaze=(0.8, -0.3))
    f = 1.0 - K.ease(ramp(T, Wx("g3", "aren't") - 0.2, Wx("g3", "Now") - 0.1))
    return L.compose(f, strength=13.0)


YEARS = ["YEAR ONE", "YEAR TWO", "YEAR THREE", "FINAL YEAR"]


def _scribe(c, x, y, s, T, speed=1.0):
    """The automaton scribe: a porcelain face under a powdered wig, a velvet coat, an arm that never stops writing."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawPath(K.smooth([(-150, 400), (-140, 120), (-90, 30), (90, 30), (140, 120), (150, 400)]), paint((90, 14, 30)))
    c.drawPath(K.smooth([(-40, 30), (0, 90), (40, 30), (20, 0), (-20, 0)]), paint((236, 230, 220)))
    for k in range(7):                                         # the wig
        c.drawCircle(-80 + k * 27, -170 + (k % 2) * 10, 34, paint((232, 228, 222)))
    for s_ in (-1, 1):
        for k in range(3):
            c.drawCircle(s_ * 96, -110 + k * 46, 28, paint((228, 224, 218)))
    c.drawOval(skia.Rect.MakeLTRB(-70, -170, 70, 10), paint((246, 240, 234)))
    for s_ in (-1, 1):
        c.drawOval(skia.Rect.MakeLTRB(s_ * 28 - 12, -94, s_ * 28 + 12, -80), paint((30, 40, 70)))
        c.drawCircle(s_ * 28 - 4, -90, 3, paint(WHITE))
    c.drawCircle(-36, -50, 12, paint((230, 120, 130), 0.6))
    c.drawCircle(36, -50, 12, paint((230, 120, 130), 0.6))
    c.drawOval(skia.Rect.MakeLTRB(-12, -32, 12, -22), paint((190, 40, 50)))
    ph = T * 9 * speed
    hx, hy = 160 + 70 * math.sin(ph), 300 + 18 * math.sin(ph * 2.3)
    c.drawPath(K.capsule(110, 120, hx, hy, 46, 36), paint((80, 12, 26)))
    c.drawCircle(hx, hy, 22, paint((246, 240, 234)))
    c.drawLine(hx, hy, hx + 50, hy - 90, paint((240, 236, 226), stroke=5))
    c.drawPath(K.smooth([(hx + 30, hy - 60), (hx + 80, hy - 140), (hx + 60, hy - 60)]), paint((240, 236, 226)))
    c.restore()


def _writing_room(c, T, year, porc, lean, candle_h, webs, stack, gov=True, hand=None, cz=None, plaque=True):
    """The same night, year after year: Clara at the desk, the scribe writing for her, the Governess at her shoulder;
    each year the candles shorter, the cobwebs thicker, the stack of finished work higher, Clara more porcelain."""
    def albedo(cc):
        cc.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((110, 18, 36)))
        rng = K.rng_at(6, 6)
        for i in range(12):
            for j in range(18):
                x, y = i * 96 + (j % 2) * 48, j * 90
                cc.drawPath(K.smooth([(x, y - 22), (x + 16, y), (x, y + 22), (x - 16, y)]), paint((70, 10, 22)))
        for xx in (0, 900):                                    # bookshelves
            cc.drawRect(skia.Rect.MakeLTRB(xx, 200, xx + 180, 1300), paint((50, 30, 20)))
            for k in range(7):
                yy = 240 + k * 150
                cc.drawRect(skia.Rect.MakeLTRB(xx + 10, yy + 120, xx + 170, yy + 134), paint((70, 44, 28)))
                for b in range(9):
                    bw = rng.uniform(12, 20)
                    cc.drawRect(skia.Rect.MakeXYWH(xx + 14 + b * 17, yy + 30 + rng.uniform(0, 20), bw, 90), paint(mix((120, 40, 30), (40, 60, 90), rng.uniform(0, 1))))

    def light(cc):
        G.pool(cc, 540, 1100, 700, AMBER, 1.1 * G.flicker(T, 3, 0.1))
        G.pool(cc, 60, 400, 600, MAGENTA, 0.9)
        G.pool(cc, 1020, 500, 600, EMERALD, 0.8)
    SE.lit2d(c, albedo, light, amb=(16, 10, 14))
    PR.clock_face(c, 540, 330, 92, 9 + year * 0.75, (year * 20) % 60)
    G.pool(c, 540, 330, 160, (255, 210, 140), 0.15)
    if plaque:
        PR.plaque(c, 540, 482, [YEARS[min(3, year)]], size=40, tag="plaque")
    if webs > 0:                                               # cobwebs in the corners
        for (cx, cy, sx) in ((0, 0, 1), (W, 0, -1)):
            for k in range(9):
                ang = math.radians(k * 10)
                L = 300 * webs
                c.drawLine(cx, cy, cx + sx * math.cos(ang) * L, cy + math.sin(ang) * L, paint((220, 220, 230), 0.25 * webs, stroke=2))
            for r in range(1, 6):
                rr = r * 55 * webs
                c.drawArc(skia.Rect.MakeLTRB(cx - rr, cy - rr, cx + rr, cy + rr), 0 if sx > 0 else 90, 90, False,
                          paint((220, 220, 230), 0.22 * webs, stroke=2))
    if cz is not None:
        c.save()
        c.translate(*cz[:2])
        c.scale(cz[2], cz[2])
        c.translate(-cz[0], -cz[1])
    if gov:
        CA.face(c, 790, 640, 0.92, "governess", T, L=(255, 170, 70), R=(70, 100, 255), core=0.4, expr="polite",
                talk=talk(T, "GOV"), blink=0.0, porc=0.4, tilt=-8 - 6 * lean, glaze=0.6)
    CA.face(c, 520, 800, 1.12, "clara", T, L=(255, 60, 170), R=(255, 170, 70), core=0.45, expr="blank" if porc > 0.5 else "lost",
            talk=talk(T, "CLARA"), blink=blink(T, 4) * (1 - porc), gaze=(0.0, 0.6), porc=porc)
    if hand is not None:                                        # the Governess's hand on her shoulder
        c.drawPath(K.capsule(680, 1080, 640, 1150, 50, 40), paint((20, 16, 22)))
        c.drawPath(K.smooth([(600, 1130), (660, 1120), (690, 1160), (640, 1190), (590, 1180)]), paint((236, 232, 228)))
    if cz is not None:
        c.restore()
    # the desk, the scribe, the work
    c.drawRect(skia.Rect.MakeLTRB(-20, 1230, 1100, 1920), paint((44, 24, 16)))
    c.drawRect(skia.Rect.MakeLTRB(-20, 1230, 1100, 1250), paint((90, 56, 34)))
    _scribe(c, 150, 1000, 0.75, T)
    PR.paper(c, 330, 1300, 220, 120, -6, T, grade="A+", lines=4, seed=year)
    for k in range(int(stack)):                                # the stack of finished work
        c.drawRect(skia.Rect.MakeLTRB(760, 1250 - k * 9, 960, 1258 - k * 9), paint(mix(PAPER, BLACK, 0.1 * (k % 3))))
    for i, cx in enumerate((470, 620)):
        G.candle(c, cx, 1180 + 90 * (1 - candle_h), 0.9 * (0.4 + 0.6 * candle_h), T, seed=i + year * 3)


def s_w_desk(T, idx):
    """Shall I write it for you? Just this once. YEAR ONE."""
    st = K.Stage()
    zoom(st.c, T, cut("w_desk"), end("w_desk"), 1.0, 1.05, cx=540, cy=800)
    _writing_room(st.c, T, 0, 0.0, 0.0, 1.0, 0.1, 4)
    st.c.restore()
    return st.arr


def s_w_desk2(T, idx):
    """The same shot again - YEAR TWO: the candles shorter, the cobwebs thicker, Clara paler."""
    st = K.Stage()
    zoom(st.c, T, cut("w_desk2"), end("w_desk2"), 1.0, 1.05, cx=540, cy=800)
    _writing_room(st.c, T, 1, 0.35, 0.4, 0.7, 0.35, 12)
    st.c.restore()
    return st.arr


def s_w_desk3(T, idx):
    """YEAR THREE: her voice gone mechanical, her skin porcelain, the Governess's hand on her shoulder."""
    st = K.Stage()
    zoom(st.c, T, cut("w_desk3"), end("w_desk3"), 1.0, 1.06, cx=540, cy=800)
    _writing_room(st.c, T, 2, 0.75, 0.8, 0.42, 0.65, 22, hand=True)
    st.c.restore()
    return st.arr


def s_w_shelves(T, idx):
    """94% of UK students now use AI to help with assessed work (mostly to explain things); about 1 in 8 paste its words
    straight in. A cabinet of a hundred porcelain scholars, 94 lighting up in a wave as the lens drifts across; then
    close on one shelf of eight - and one cracks open on nothing."""
    st = K.Stage((6, 4, 6))
    c = st.c
    t0 = cut("w_shelves")
    t88 = Wx("w5", "Ninety-four")
    t18 = Wx("w5", "About")
    t_close = t18 - 0.2
    if T >= t_close:                                            # close on one shelf: one in eight goes hollow
        zoom(c, T, t_close, end("w_shelves") + 0.3, 1.0, 1.16, cx=540, cy=900)
        c.translate(30 - 60 * ramp(T, t_close, end("w_shelves")), 0)
        c.drawRect(skia.Rect.MakeLTRB(-100, 0, W + 100, H), paint((40, 22, 14)))
        G.pool(c, 540, 860, 760, (120, 30, 60), 0.55)
        c.drawRect(skia.Rect.MakeLTRB(-100, 1130, W + 100, 1170), paint((96, 60, 36)))
        c.drawRect(skia.Rect.MakeLTRB(-100, 1170, W + 100, 1200), paint((50, 30, 18)))
        crack_k = ramp(T, t18 + 0.5, t18 + 0.9)
        for k in range(8):
            x = 85 + k * 130
            hollow = k == 5
            G.pool(c, x, 930, 120, AMBER, 0.55 if not (hollow and crack_k > 0) else 0.12)
            PR.figurine(c, x, 1140, 1.3, T, "scholar", face_color=(252, 230, 190), seed=k, lit=(255, 170, 70))
            if hollow and crack_k > 0:                          # its face falls away: nothing inside
                fx, fy = x, 1140 - 124 * 1.3
                rng = K.rng_at(5, k)
                c.drawCircle(fx, fy, 22 * crack_k + 3, paint((4, 2, 4)))
                c.drawCircle(fx, fy, 22 * crack_k + 3, paint((220, 30, 40), 0.9, stroke=3))
                for q in range(6):
                    ang = rng.uniform(0, 6.283)
                    c.drawLine(fx + math.cos(ang) * 14, fy + math.sin(ang) * 14, fx + math.cos(ang) * 36, fy + math.sin(ang) * 36,
                               paint((40, 20, 24), 0.9, stroke=3))
                for q in range(5):                              # flakes of porcelain dropping to the shelf
                    fall = min(1.0, (T - t18 - 0.5) * 1.6 + q * 0.1)
                    c.drawCircle(fx + rng.uniform(-24, 24), fy + 30 + fall * 120, 4, paint((240, 226, 200), 0.9 * (1 - fall * 0.5)))
        c.restore()
        k = K.ease(ramp(T, t_close, t_close + 0.3))
        PR.plaque(c, 540, 380, ["12% PASTE AI TEXT STRAIGHT IN"], size=38, a=k, color=(120, 20, 24))
        return st.arr
    zoom(c, T, t0, t_close + 0.2, 1.0, 1.14, cx=540, cy=820)
    c.translate(-36 + 72 * K.ease(ramp(T, t0, t_close)), 0)    # the lens drifts along the cabinet
    c.drawRect(skia.Rect.MakeLTRB(60, 360, 1020, 1250), paint((50, 28, 18)))
    G.pool(c, 540, 800, 700, (120, 30, 60), 0.5)
    rng = K.rng_at(88, 1)
    order = list(range(100))
    rng.shuffle(order)
    lit = set(order[:94])
    for r in range(10):
        y = 460 + r * 82
        c.drawRect(skia.Rect.MakeLTRB(80, y + 2, 1000, y + 12), paint((86, 54, 32)))
        for k in range(10):
            i = r * 10 + k
            x = 135 + k * 90
            on = T > t88 + (i % 10) * 0.05 + r * 0.06 and i in lit
            if on:
                G.pool(c, x, y - 52, 40, AMBER, 0.5)
            PR.figurine(c, x, y, 0.42, T, "scholar", face_color=(252, 226, 180) if on else (70, 60, 60), seed=i,
                        lit=(255, 170, 70) if on else (20, 14, 14))
    c.restore()
    if T > t88 - 0.1:
        k = K.ease(ramp(T, t88 - 0.1, t88 + 0.3))
        PR.plaque(c, 540, 310, ["94% USE AI FOR ASSESSED WORK", "MOSTLY TO EXPLAIN THINGS"], size=40, sizes=[40, 38], a=k)
    return st.arr


def s_w_ledger(T, idx):
    """Proven AI cheating cases tripled in a year - and that's only the ones who got caught: the Governess's red
    ledger, the figures in ink, and a facing page of names no one ever checked."""
    st = K.Stage((8, 4, 6))
    c = st.c
    t0 = cut("w_ledger")
    zoom(c, T, t0, end("w_ledger"), 1.0, 1.08, cx=540, cy=760)
    G.pool(c, 540, 820, 820, AMBER, 0.45)
    c.drawRoundRect(skia.Rect.MakeLTRB(50, 300, 1030, 1280), 16, 16, paint((120, 16, 24)))
    for side in (-1, 1):
        x0 = 540 if side > 0 else 80
        c.drawRect(skia.Rect.MakeLTRB(x0, 330, x0 + 460, 1250), paint(mix(PAPER, (150, 110, 70), 0.35)))
        c.drawRect(skia.Rect.MakeLTRB(x0, 330, x0 + 460, 1250), paint(shader=K.lin((540, 0), (540 + side * 460, 0), [(80, 50, 20, 0.35), (80, 50, 20, 0.0)])))
    ink = (40, 30, 70)
    K.text(c, "PROVEN AI CHEATING", 310, 430, 36, "cinzel-800", ink, tag="ledger")
    K.text(c, "PER 1,000 STUDENTS", 310, 488, 40, "cinzel-600", ink, tag="ledger")
    w1 = K.ease(ramp(T, t0 + 0.4, t0 + 0.9))
    w2 = K.ease(ramp(T, Wx("w8", "tripled") - 0.2, Wx("w8", "tripled") + 0.4))
    for i, (yr, v, wk) in enumerate((("2022-23", "1.6", w1), ("2023-24", "5.1", w2))):
        y = 600 + i * 230
        K.text(c, yr, 140, y, 44, "playfair-400i", ink, align="left", tag="ledger", a=min(1.0, wk * 2))
        bw = (60 if i == 0 else 190) * wk
        c.drawRect(skia.Rect.MakeLTRB(140, y + 30, 140 + bw * 1.6, y + 90), paint((170, 20, 30), 0.85))
        K.text(c, v, 140 + bw * 1.6 + 54, y + 78, 52, "playfair-700", (170, 20, 30), tag="ledger", a=wk)
    if w2 > 0.7:
        kk = K.ease((w2 - 0.7) / 0.3)
        c.drawCircle(320, 1090, 70 * kk, paint((170, 20, 30), kk, stroke=6))
        K.text(c, "x3", 320, 1110, 64, "playfair-700", (170, 20, 30), tag="ledger", a=kk)
    tn = Wx("w8", "only")
    kn = K.ease(ramp(T, tn - 0.2, tn + 0.5))
    K.text(c, "NOT CAUGHT", 770, 430, 36, "cinzel-800", ink, tag="ledger", a=kn)
    rng = K.rng_at(5, 50)
    for i in range(22):
        y = 480 + i * 34
        w = rng.uniform(140, 330)
        c.drawRect(skia.Rect.MakeLTRB(590, y, 590 + w * kn, y + 6), paint(ink, 0.35))
    c.restore()
    return st.arr


def s_w_final(T, idx):
    """FINAL YEAR. The clock strikes; Clara does not move; the lens creeps into her glass eyes."""
    st = K.Stage()
    c = st.c
    t0 = cut("w_final")
    zoom(c, T, t0, end("w_final"), 1.0, 1.9, cx=520, cy=790)
    _writing_room(c, T, 3, 0.95, 1.0, 0.18, 0.9, 30, hand=True, plaque=False)
    c.restore()
    ka = 1 - ramp(T, t0 + 0.5, t0 + 0.9)
    if ka > 0:
        PR.plaque(c, 540, 482, [YEARS[3]], size=40, tag="plaque", a=ka)
    return st.arr

"""The labyrinth: Clara alone in the alleys; a tutor's lit window; papers raining down a stepped alley, each with a
perfect grade; an essay with her name on it; the same fountain three times; the villa, and the Governess at its door."""
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
from kit import AMBER, BLACK, COBALT, EMERALD, MAGENTA, WHITE, H, W, mix, paint, ramp


def s_l_alley(T, idx):
    """AI could be the finest tutor ever built. The camera follows Clara down the alley, lantern to lantern."""
    st = K.Stage()
    c = st.c
    t0 = cut("l_alley")
    u = T - t0
    cam = P.Cam(pos=(0.15 * math.sin(u * 0.6), 1.55, 0.6 * u), f=880, pitch=-3)
    SE.alley(c, cam, T, seed=1)
    SE.fog_end(c, cam, cam.pos[2] + 34, r=520)
    pos = (0.1, 0.0, cam.pos[2] + 2.7 + 0.2 * u)
    q = cam.proj(pos)
    sc = cam.scale_at(pos) * 1.72 / 900
    CA.walker_back(c, q[0], q[1], sc, T, coat=(196, 168, 120), key=(255, 70, 170), rim=(60, 230, 150))
    return st.arr


def s_l_window(T, idx):
    """In one university trial, students with an AI tutor learned twice as much: through a lit window, a patient
    tutor at a chalkboard; Clara outside in the dark, watching."""
    st = K.Stage()
    c = st.c
    t0 = cut("l_window")
    zoom(c, T, t0, end("l_window"), 1.0, 1.1, cx=540, cy=640)

    def albedo(cc):
        SE.blocks2d(cc, 0, 0, W, H, (186, 160, 140), bw=90, bh=46, seed=8)

    def light(cc):
        G.pool(cc, 540, 640, 760, AMBER, 0.9)
        G.pool(cc, 120, 1500, 600, MAGENTA, 0.5)
    SE.lit2d(c, albedo, light, amb=(16, 12, 18))
    # the window: an arch of warm light
    x0, y0, x1, y1 = 190, 270, 890, 1180
    win = skia.Path()
    win.moveTo(x0, y1)
    win.lineTo(x0, y0 + 350)
    win.arcTo(skia.Rect.MakeLTRB(x0, y0, x1, y0 + 700), 180, 180, False)
    win.lineTo(x1, y1)
    win.close()
    c.drawPath(win, paint((70, 46, 26)))
    c.save()
    c.clipPath(win, doAntiAlias=True)
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(shader=K.lin((0, y0), (0, y1), [(150, 96, 50), (90, 56, 30)])))
    # the chalkboard inside, the result in chalk: class vs. AI tutor
    bx0, by0, bx1, by1 = 230, 380, 700, 860
    c.drawRect(skia.Rect.MakeLTRB(bx0 - 16, by0 - 16, bx1 + 16, by1 + 16), paint((70, 44, 24)))
    c.drawRect(skia.Rect.MakeLTRB(bx0, by0, bx1, by1), paint((30, 44, 36)))
    grow = K.ease(ramp(T, Wx("l1", "trial") - 0.1, Wx("l1", "twice") + 0.2))
    chalk = (236, 236, 226)
    base = by1 - 90
    for i, (lab, hgt) in enumerate((("CLASS", 120), ("AI TUTOR", 240))):
        bx = bx0 + 120 + i * 230
        hh = hgt * 1.25 * (grow if i == 1 else min(1.0, grow * 2))
        c.drawRect(skia.Rect.MakeLTRB(bx - 60, base - hh, bx + 60, base), paint(chalk, 0.9, stroke=6))
        for k in range(int(hh / 18)):
            c.drawLine(bx - 56, base - k * 18 - 6, bx + 56, base - k * 18 - 18, paint(chalk, 0.45, stroke=3))
        K.text(c, lab, bx, base + 56, 38, "cinzel-600", chalk, tag="label", a=0.95)
    if grow > 0.6:
        K.text(c, "x2", bx0 + 350, base - 330, 70, "playfair-400i", chalk, tag="label", a=K.ease((grow - 0.6) / 0.4))
    # the tutor (a porcelain governess, her back to us) guiding a pupil's hand
    c.drawPath(K.smooth([(740, 1180), (730, 900), (750, 760), (800, 720), (850, 760), (870, 900), (860, 1180)]), paint((16, 10, 12)))
    c.drawCircle(800, 690, 40, paint((16, 10, 12)))
    c.drawCircle(800, 646, 22, paint((16, 10, 12)))
    c.drawPath(K.capsule(750, 820, 640, 900 + 10 * math.sin(T * 2), 26, 20), paint((16, 10, 12)))
    c.drawPath(K.smooth([(470, 1180), (480, 1010), (520, 960), (570, 970), (590, 1030), (600, 1180)]), paint((20, 12, 14)))
    c.drawCircle(540, 925, 36, paint((20, 12, 14)))
    c.restore()
    for xx in (215, 448, 865):                                  # glazing bars (kept clear of the chalk)
        c.drawLine(xx, y0 + 60, xx, y1, paint((50, 30, 18), stroke=8))
    c.drawLine(x0, 900, x1, 900, paint((50, 30, 18), stroke=10))
    c.drawPath(win, paint((60, 44, 30), stroke=26))
    G.pool(c, 540, 820, 600, AMBER, 0.2)
    # Clara, the back of her head, in the dark foreground
    c.drawPath(K.smooth([(-60, 1920), (-40, 1600), (60, 1480), (140, 1440), (230, 1470), (300, 1600), (330, 1920)]), paint((14, 10, 12)))
    c.drawPath(K.smooth([(70, 1500), (60, 1330), (110, 1230), (190, 1210), (260, 1250), (290, 1350), (270, 1480), (180, 1520)]), paint((24, 12, 10)))
    c.drawPath(K.smooth([(60, 1340), (110, 1230), (190, 1210), (260, 1250), (290, 1350)], closed=False), paint((255, 150, 60), 0.7, stroke=5, blur=3))
    c.restore()
    return st.arr


LABELS = [("Essays.", "ESSAY"), ("Homework.", "HOMEWORK"), ("Code.", "CODE"), ("Reports.", "REPORT")]


def s_l_stairs(T, idx):
    """It can also do the work for you: papers raining down a stepped alley, each one marked A+; four fly at us."""
    st = K.Stage()
    c = st.c
    t0 = cut("l_stairs")
    zoom(c, T, t0, end("l_stairs"), 1.0, 1.08, cx=540, cy=700)
    vx, vy = 540, 300
    SE.sky(c, y0=0, y1=700, seed=6, moon=(560, 150, 26))

    def albedo(cc):
        for side in (-1, 1):
            xo = 0 if side < 0 else W
            xi = vx - 170 if side < 0 else vx + 170
            p = K.path([(xo, -200), (xi, vy - 140), (xi, vy + 180), (xo, H + 200)])
            cc.save()
            cc.clipPath(p, doAntiAlias=True)
            SE.blocks2d(cc, 0, -200, W, H + 200, (190, 166, 146), bw=70, bh=34, seed=20 + side)
            cc.restore()
        n = 18
        for i in range(n):                                     # steps climbing toward the far end
            k0, k1 = i / n, (i + 1) / n
            y_a = H - (H - vy - 180) * (1 - (1 - k0) ** 1.8)
            y_b = H - (H - vy - 180) * (1 - (1 - k1) ** 1.8)
            hw_a = 540 * (1 - k0 * 0.69)
            hw_b = 540 * (1 - k1 * 0.69)
            ym = y_a + (y_b - y_a) * 0.35
            cc.drawPath(K.path([(vx - hw_a, y_a), (vx + hw_a, y_a), (vx + hw_b, ym), (vx - hw_b, ym)]), paint((160, 150, 140)))
            cc.drawPath(K.path([(vx - hw_b, ym), (vx + hw_b, ym), (vx + hw_b, y_b), (vx - hw_b, y_b)]), paint((96, 88, 84)))

    def light(cc):
        G.pool(cc, 120, 900, 560, AMBER, 0.85)
        G.pool(cc, 960, 600, 520, MAGENTA, 0.85)
        G.pool(cc, 540, 1600, 700, EMERALD, 0.5)
    SE.lit2d(c, albedo, light, amb=(18, 14, 22))
    G.lantern(c, 150, 760, 0.55, AMBER, T, seed=3)
    G.lantern(c, 930, 480, 0.4, MAGENTA, T, seed=5)
    # papers drifting down the stairs
    rng = K.rng_at(31, 2)
    for k in range(26):
        fall = (T * rng.uniform(60, 140) + rng.uniform(0, 1400)) % 1500
        x = rng.uniform(200, 880) + 60 * math.sin(T * rng.uniform(1, 2.5) + k)
        y = 250 + fall
        sc = 0.35 + 0.9 * (y / H)
        PR.paper(c, x, y, 90 * sc, 120 * sc, rng.uniform(-40, 40) + 50 * math.sin(T * 2 + k), T, lines=5, seed=k,
                 a=0.85, grade="A+")
    # the four that fly at us
    for i, (word, lab) in enumerate(LABELS):
        tw = Wx("l2", word)
        k = ramp(T, tw - 0.15, tw + 0.5)
        if k <= 0 or T > tw + 1.6:
            continue
        gone = ramp(T, tw + 1.1, tw + 1.6)
        s = 0.4 + 1.0 * K.ease(k)
        x = [330, 760, 380, 730][i] + (gone * 600 * (1 if i % 2 else -1))
        y = [600, 700, 900, 1040][i] - 40 * K.ease(k)
        PR.paper(c, x, y, 300 * s, 400 * s, [-8, 7, -5, 9][i] + 40 * gone, T, title=lab, lines=7, seed=40 + i,
                 kind="code" if lab == "CODE" else "essay", tag="label", a=1 - gone, title_size=34 * s)
    if T > Wx("l2", "Reports.") + 0.3:                         # ...and the discussion posts, a little flurry
        k = ramp(T, Wx("l2", "Reports.") + 0.3, Wx("l2", "Reports.") + 0.8)
        PR.paper(c, 540, 420 + 40 * k, 260, 160, -4, T, title="DISCUSSION POST", lines=3, seed=60, tag="label", a=K.ease(k),
                 title_size=26)
    c.restore()
    return st.arr


def s_l_name(T, idx):
    """My name's on this. I never wrote it. The focus pulls from the paper in her hands to her face."""
    L = Layers(2, bg=(4, 2, 6))
    t0 = cut("l_name")
    far = L.c(0)
    G.pool(far, 540, 600, 700, (120, 20, 80), 0.6)
    zoom(far, T, t0, end("l_name"), 1.0, 1.12, cx=540, cy=520)
    CA.face(far, 540, 520, 1.25, "clara", T, L=(255, 60, 170), R=(40, 220, 140), core=0.5, expr="dread",
            talk=talk(T, "CLARA"), blink=blink(T, 5), gaze=(0.0, 0.7 if T < Wx("l3", "never") else 0.0))
    far.restore()
    near = L.c(1)
    PR.paper(near, 540, 1010, 620, 760, -3, T, title="ON MEMORY", name="Clara Ashdown", lines=8, seed=77, tag="label",
             title_size=58)
    for s in (-1, 1):                                          # her gloved fingers at the edges
        near.drawPath(K.capsule(540 + s * 330, 900, 540 + s * 290, 1000, 60, 50), paint((60, 30, 30)))
    f = 1.0 - K.ease(ramp(T, Wx("l3", "never") - 0.3, Wx("l3", "never") + 0.3))
    return L.compose(f, strength=12.0)


def _courtyard(c, T, beat, pose, head, clara_x, glass=0.0):
    """The same small piazza every time: a fountain with a weeping stone mask, two arches, a shop window with a
    mannequin behind the glass (it is never standing where it stood before)."""
    def albedo(cc):
        SE.blocks2d(cc, 0, 0, W, 1400, (190, 168, 150), bw=80, bh=40, seed=50)
        cc.drawRect(skia.Rect.MakeLTRB(0, 1400, W, H), paint((140, 130, 124)))
        for k in range(8):
            cc.drawLine(0, 1400 + k * (60 + k * 14), W, 1400 + k * (60 + k * 14), paint((90, 84, 80), stroke=3))
    def light(cc):
        G.pool(cc, 230, 900, 520, EMERALD, 0.85)
        G.pool(cc, 860, 760, 480, MAGENTA, 0.8)
        G.pool(cc, 540, 1250, 520, AMBER, 0.6)
    SE.lit2d(c, albedo, light, amb=(14, 10, 16))
    # the shop window (left) and the arch (right)
    c.drawRect(skia.Rect.MakeLTRB(60, 560, 420, 1260), paint((8, 20, 14)))
    G.pool(c, 240, 900, 300, EMERALD, 0.4)
    CA.mannequin(c, 240 + [0, 10, 40][min(2, beat)], 1240, 0.62, T, pose=pose, head=head, gown=False, cap=False,
                 L=(60, 230, 150), R=(30, 120, 80), face_k=0.0 if beat < 2 else 0.7)
    c.drawRect(skia.Rect.MakeLTRB(60, 560, 420, 1260), paint((120, 255, 180), 0.08))
    c.drawLine(80, 600, 160, 540, paint(WHITE, 0.25, stroke=3))
    c.drawRect(skia.Rect.MakeLTRB(52, 552, 428, 1268), paint((60, 44, 30), stroke=16))
    arch = skia.Path()
    arch.moveTo(660, 1400)
    arch.lineTo(660, 860)
    arch.arcTo(skia.Rect.MakeLTRB(660, 660, 1000, 1000), 180, 180, False)
    arch.lineTo(1000, 1400)
    arch.close()
    c.drawPath(arch, paint((4, 2, 6)))
    # the fountain: a carved weeping mask on the wall, spouting into a stone basin
    mx, my = 540, 1080
    c.drawRect(skia.Rect.MakeLTRB(mx - 130, my - 170, mx + 130, my + 170), paint((150, 138, 124)))
    c.drawPath(K.path([(mx - 150, my - 170), (mx, my - 250), (mx + 150, my - 170)]), paint((160, 146, 132)))
    c.drawOval(skia.Rect.MakeLTRB(mx - 78, my - 110, mx + 78, my + 90), paint((176, 164, 150)))
    for s in (-1, 1):
        c.drawPath(K.smooth([(mx + s * 46 - 18, my - 30), (mx + s * 46, my - 44), (mx + s * 46 + 18, my - 30), (mx + s * 46, my - 20)]), paint((24, 18, 18)))
        c.drawPath(K.bez_path([(mx + s * 46, my - 18), (mx + s * 48, my + 10), (mx + s * 44, my + 40)]), paint((40, 60, 70), 0.7, stroke=5))
        c.drawPath(K.bez_path([(mx + s * 20, my - 60), (mx + s * 46, my - 74), (mx + s * 72, my - 58)]), paint((90, 80, 72), stroke=6))
    c.drawOval(skia.Rect.MakeLTRB(mx - 22, my + 34, mx + 22, my + 66), paint((20, 14, 14)))
    c.drawPath(K.smooth([(mx - 240, 1400), (mx - 250, 1330), (mx, 1300), (mx + 250, 1330), (mx + 240, 1400), (mx, 1430)]), paint((128, 118, 108)))
    c.drawOval(skia.Rect.MakeLTRB(mx - 220, 1306, mx + 220, 1350), paint((30, 60, 80)))
    for k in range(7):                                         # water from the mask's mouth
        y = my + 60 + ((T * 420 + k * 34) % 250)
        c.drawCircle(mx + 3 * math.sin(k), y, 5, paint((180, 220, 255), 0.6))
    G.pool(c, mx, 1320, 240, AMBER, 0.35)
    # Clara coming out of the arch
    if clara_x is not None:
        CA.walker_back(c, clara_x, 1410, 0.42, T, coat=(196, 168, 120), key=(255, 70, 170), rim=(60, 230, 150))


def s_l_loop(T, idx):
    """Deja vu: she turns a corner into the same piazza, three times; the mannequin in the window is never where it
    was. Then dead silence, and it hits the glass."""
    st = K.Stage()
    c = st.c
    t0 = cut("l_loop")
    u = T - t0
    scare = end("l_loop") - 0.62
    if T < scare:
        beat = min(2, int(u / 0.58))
        pose = [0, 1, 3][beat]
        head = [0.0, -0.8, -0.2][beat]
        bt = u - beat * 0.58
        SE_x = 860 - bt * 120
        _courtyard(c, T, beat, pose, head, SE_x)
    else:
        k = ramp(T, scare, scare + 0.12)
        shake(c, T, 22 * hit(T, scare + 0.08, 0.4), seed=3)
        c.drawPaint(paint((0, 10, 6)))
        G.pool(c, 540, 860, 900, EMERALD, 0.7)
        z = 1.6 + 1.4 * K.ease(k)
        c.save()
        c.translate(540, 900)
        c.scale(z, z)
        c.translate(-540, -900)
        CA.mannequin(c, 540, 1900, 0.95, T, pose=3, head=0.0, gown=False, cap=False, L=(80, 255, 170), R=(255, 60, 160),
                     face_k=1.0)
        c.restore()
        if k >= 1:                                             # the glass cracks where the face struck it
            rng = K.rng_at(9, 9)
            for i in range(14):
                ang = rng.uniform(0, 6.28)
                L = rng.uniform(200, 700)
                c.drawLine(540, 900, 540 + math.cos(ang) * L, 900 + math.sin(ang) * L, paint(WHITE, 0.7, stroke=3))
            c.drawPaint(paint((255, 255, 255), 0.6 * hit(T, scare + 0.12, 0.2)))
        c.restore()
    return st.arr


def s_v_gate(T, idx):
    """The villa at the end of the alley: a decaying baroque front, one lit window; the gate swings open by itself."""
    st = K.Stage()
    c = st.c
    t0 = cut("v_gate")
    zoom(c, T, t0, end("v_gate") + 0.4, 1.0, 1.22, cx=540, cy=980)
    SE.sky(c, top=(6, 8, 40), mid=(40, 20, 80), low=(110, 40, 100), y0=0, y1=1300, seed=8, moon=(820, 200, 40))

    def albedo(cc):
        stone = (184, 168, 156)
        cc.drawRect(skia.Rect.MakeLTRB(80, 420, 1000, 1500), paint(stone))
        rng = K.rng_at(4, 4)
        for k in range(60):                                    # damp stains
            x, y = rng.uniform(80, 1000), rng.uniform(420, 1500)
            cc.drawOval(skia.Rect.MakeXYWH(x, y, rng.uniform(30, 120), rng.uniform(60, 220)), paint(mix(stone, BLACK, 0.35), 0.3, blur=14))
        cc.drawPath(K.path([(60, 430), (540, 250), (1020, 430)]), paint(mix(stone, BLACK, 0.12)))
        cc.drawPath(K.path([(150, 410), (540, 290), (930, 410)]), paint(mix(stone, BLACK, 0.25), stroke=8))
        cc.drawCircle(540, 360, 34, paint(mix(stone, BLACK, 0.35)))
        for yy in (430, 860, 1180):                            # cornices
            cc.drawRect(skia.Rect.MakeLTRB(60, yy, 1020, yy + 26), paint(mix(stone, WHITE, 0.25)))
            cc.drawRect(skia.Rect.MakeLTRB(60, yy + 26, 1020, yy + 34), paint(mix(stone, BLACK, 0.45)))
        for k in range(6):                                     # pilasters
            xx = 120 + k * 168
            cc.drawRect(skia.Rect.MakeLTRB(xx, 460, xx + 36, 1500), paint(mix(stone, WHITE, 0.12)))
            cc.drawRect(skia.Rect.MakeLTRB(xx - 8, 460, xx + 44, 480), paint(mix(stone, WHITE, 0.3)))
        for r_, yy in enumerate((560, 940)):
            for k in range(5):
                xx = 180 + k * 168
                cc.drawRect(skia.Rect.MakeLTRB(xx - 14, yy - 30, xx + 104, yy + 230), paint(mix(stone, WHITE, 0.18)))
                cc.drawPath(K.path([(xx - 22, yy - 30), (xx + 45, yy - 74), (xx + 112, yy - 30)]), paint(mix(stone, WHITE, 0.18)))
                cc.drawRect(skia.Rect.MakeLTRB(xx, yy, xx + 90, yy + 220), paint((14, 10, 12)))
                cc.drawLine(xx + 45, yy, xx + 45, yy + 220, paint((60, 50, 44), stroke=5))
        for k in range(14):                                    # the balustrade on the roofline, two statues
            cc.drawRect(skia.Rect.MakeLTRB(150 + k * 56, 392, 166 + k * 56, 430), paint(mix(stone, WHITE, 0.2)))
        for sx in (110, 970):
            cc.drawPath(K.smooth([(sx - 26, 430), (sx - 20, 330), (sx, 300), (sx + 20, 330), (sx + 26, 430)]), paint(mix(stone, BLACK, 0.2)))
            cc.drawCircle(sx, 288, 18, paint(mix(stone, BLACK, 0.2)))
        cc.drawRect(skia.Rect.MakeLTRB(440, 1200, 640, 1500), paint((40, 24, 18)))
        cc.drawPath(K.path([(430, 1200), (540, 1150), (650, 1200)]), paint(mix(stone, WHITE, 0.2)))
        cc.drawRect(skia.Rect.MakeLTRB(0, 1500, W, H), paint((70, 64, 60)))
        for k in range(40):                                    # ivy creeping up the corners
            x = rng.uniform(80, 240) if k % 2 else rng.uniform(840, 1000)
            y = rng.uniform(900, 1500)
            cc.drawCircle(x, y, rng.uniform(14, 34), paint((30, 54, 30), 0.85, blur=4))

    def light(cc):
        G.pool(cc, 540, 1400, 600, AMBER, 0.6)
        G.pool(cc, 150, 900, 600, (60, 80, 230), 0.7)
        G.pool(cc, 930, 900, 600, MAGENTA, 0.6)
    SE.lit2d(c, albedo, light, amb=(20, 16, 26))
    c.drawRect(skia.Rect.MakeLTRB(684, 940, 774, 1160), paint((240, 170, 70)))         # the one lit window
    c.drawLine(729, 940, 729, 1160, paint((90, 50, 30), stroke=5))
    G.pool(c, 729, 1050, 220, AMBER, 0.5)
    G.fog(c, T, 0, 1350, W, 1650, (120, 110, 160), a=0.35, n=7, seed=3)
    # the gate: two leaves of iron swinging open
    op = K.ease(ramp(T, t0 + 0.2, end("v_gate")))
    for side in (-1, 1):
        w = 300 * (1 - 0.75 * op)
        x_h = 540 + side * 300
        x_e = x_h - side * w
        for k in range(9):
            xx = x_h + (x_e - x_h) * k / 8
            c.drawLine(xx, 1180, xx, 1800, paint((16, 12, 14), stroke=8))
            c.drawPath(K.path([(xx - 10, 1180), (xx, 1150), (xx + 10, 1180)]), paint((16, 12, 14)))
        for yy in (1260, 1720):
            c.drawLine(x_h, yy, x_e, yy, paint((16, 12, 14), stroke=8))
    for side in (-1, 1):
        c.drawRect(skia.Rect.MakeLTRB(540 + side * 300 - 30, 1080, 540 + side * 300 + 30, 1920), paint((60, 54, 50)))
        c.drawCircle(540 + side * 300, 1070, 40, paint((80, 74, 70)))
    c.restore()
    return st.arr


def s_v_door(T, idx):
    """Signorina Clara. Your work is already finished. The Governess in the doorway, a candelabra in her hand, a blue
    hall behind her; the lens creeps toward eyes that never blink."""
    st = K.Stage((2, 2, 8))
    c = st.c
    t0 = cut("v_door")
    zoom(c, T, t0, end("v_door"), 1.0, 1.3, cx=540, cy=700)
    # the hall behind, cobalt
    c.drawRect(skia.Rect.MakeLTRB(170, 150, 910, 1920), paint(shader=K.lin((0, 150), (0, 1900), [(20, 30, 110), (6, 8, 40)])))
    for k in range(6):
        y = 1300 + k * 70
        c.drawRect(skia.Rect.MakeLTRB(600 + k * 30, y, 910, y + 14), paint((40, 50, 140), 0.6))
    G.pool(c, 540, 500, 600, (60, 90, 255), 0.5)
    # the door frame
    c.drawRect(skia.Rect.MakeLTRB(90, 120, 250, 1920), paint((40, 22, 14)))
    c.drawRect(skia.Rect.MakeLTRB(830, 120, 990, 1920), paint((40, 22, 14)))
    c.drawRect(skia.Rect.MakeLTRB(90, 60, 990, 150), paint((50, 28, 18)))
    open_ = K.ease(ramp(T, t0, t0 + 0.6))
    c.drawRect(skia.Rect.MakeLTRB(250 + 580 * open_, 150, 830, 1920), paint((30, 16, 10)))
    CA.face(c, 540, 700, 1.55, "governess", T, L=(255, 170, 70), R=(70, 100, 255), core=0.4, expr="polite",
            talk=talk(T, "GOV"), blink=0.0, gaze=(0.0, 0.0), porc=0.35, glaze=0.6)
    PR.candelabra(c, 300, 1200, 1.0, T)
    G.pool(c, 300, 1060, 500, AMBER, 0.35)
    c.restore()
    return st.arr

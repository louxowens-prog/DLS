"""III. THE ORACLE - what it can know without being told.

o_veils  - a royal-blue chamber hung with silk; the veils part by themselves; behind them, someone sitting very still.
o_points - from above, a crowd on the salt flat; four gold pins fall, and with each one fewer people are still lit,
           until one remains: 4 points single out 95%.
o_sphere - the oracle: a porcelain figure inside a golden armillary; each ring engraves a guess, and the guesses
           hang from her on little tags like prices.
o_mirror - her face in a gilt mirror, and in the mirror, and in the mirror..."""
import math

import numpy as np
import skia

import cold as CO
import couture as C
import dream as D
import gel as G
import hall as Hl
import kit as K
import pers as Pr
from common import E, S, Wx, hit, shake, slow, stutter, talk, zoom
from edit import cut, end
from kit import BLACK, H, W, WHITE, mix, paint, ramp

ROYAL_BG, ROYAL_DEEP = (20, 40, 150), (2, 6, 40)


def s_o_veils(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0, t1 = cut("o_veils"), end("o_veils")
    u = K.ease(ramp(T, t0 + 0.2, t1))
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(shader=K.rad((540, 1000), 1200, [ROYAL_BG, ROYAL_DEEP, (0, 0, 10)])))
    G.beam(c, (540, -100), (380, 1500), (700, 1500), (255, 230, 170), 0.3)
    G.pool(c, 540, 1400, 300, (255, 220, 160), 0.4, squash=0.3)
    C.doll(c, 540, 1420, 0.75, T, pose="type", tint=(240, 236, 228))
    c.drawRect(skia.Rect.MakeLTRB(400, 1180, 680, 1220), paint(shader=C.gold_shader((400, 0), (680, 0))))
    for i in range(10):                                            # silk veils hanging from the dark, parting
        sd = -1 if i < 5 else 1
        base = 60 + i * 107
        x = base + sd * u * (260 + 60 * abs(i - 4.5))
        D.veil(c, T, x, -60, 1900, 70, col=(170, 190, 255) if i % 2 else (230, 236, 255), a=0.55, wind=(0.04 * sd, 1.0), seed=i, slow=0.25, freq=0.6)
    return st.arr


CROWD = [(x, y) for y in np.arange(560, 1300, 74) for x in np.arange(100, 1000, 74)]


def s_o_points(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0, t1 = cut("o_points"), end("o_points")
    import sc_eye as SE
    SE._salt_top(c, T, z=0.6)
    c.drawPaint(paint((20, 40, 140), 0.25))
    rng = K.rng_at(17, 3)
    jit = rng.uniform(-14, 14, (len(CROWD), 2))
    target = CROWD[len(CROWD) // 2 + 7]
    tp = Wx("o2", "four") - 0.1
    pins = [(target[0] - 150, target[1] - 120), (target[0] + 170, target[1] - 60), (target[0] - 90, target[1] + 160), (target[0] + 60, target[1] + 120)]
    radii = [380, 240, 140, 60]
    lit_r = None
    for j, (px, py) in enumerate(pins):
        tj = tp + j * 0.42
        if T > tj:
            lit_r = j
    for i, (x, y) in enumerate(CROWD):
        x, y = x + jit[i][0], y + jit[i][1]
        on = True
        if lit_r is not None:
            on = math.hypot(x - target[0], y - target[1]) < radii[lit_r] + 1 or (x, y) == target
        col = (255, 252, 244) if on else (90, 98, 124)
        SE._top_person(c, x, y, 1.7, col=col, a=1.0 if on else 0.4)
    for j, (px, py) in enumerate(pins):
        tj = tp + j * 0.42
        if T < tj - 0.25:
            continue
        drop = max(0.0, 1 - (T - (tj - 0.25)) / 0.25)
        yy = py - 600 * drop ** 2
        c.drawLine(px, yy - 180, px, yy, paint(C.GOLD_LO, stroke=9))
        c.drawCircle(px, yy - 180, 28, paint(shader=C.gold_shader((px - 28, 0), (px + 28, 0))))
        c.drawCircle(px, yy, 10, G.glow_paint(C.GOLD_HI, 0.8))
        if T > tj:
            r = radii[j]
            k = min(1.0, (T - tj) / 0.3)
            c.drawCircle(target[0], target[1], r * (0.4 + 0.6 * k), paint(C.GOLD, 0.6 * (1 - 0.5 * k), stroke=4))
    if lit_r == 3:
        k = K.ease(ramp(T, tp + 1.26, tp + 1.6))
        G.pool(c, target[0], target[1], 60, (255, 220, 140), 0.8 * k)
        CO.target_box(c, target[0] - 40, target[1] - 40, target[0] + 40, target[1] + 40, T, lock=k, col=C.GOLD_HI)
    from cards import spaced
    kk = K.ease(ramp(T, Wx("o2", "ninety-five") - 0.2, Wx("o2", "ninety-five") + 0.2))
    c.drawPath(K.rrect(150, 250, 930, 470, 14), paint((4, 10, 50), 0.85 * max(kk, 0.6 * K.ease(ramp(T, tp, tp + 0.3)))))
    n = sum(1 for j in range(4) if T > tp + j * 0.42)
    K.text(c, "%d LOCATION POINT%s" % (n, "" if n == 1 else "S") if n else "", 540, 330, 44, "cinzel-600", C.GOLD_HI, tag="label")
    spaced(c, "95%" if kk > 0 else "", 540, 440, 100, "italiana-400", 0.1, WHITE, kk, tag="label")
    return st.arr


INFER = [("income,", "INCOME", "$48–55K, est."), ("relationships,", "RELATIONSHIPS", "2 close · 1 ex, est."),
         ("health,", "HEALTH", "stress: high, est."), ("beliefs.", "BELIEFS", "religious, est.")]


def s_o_sphere(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0, t1 = cut("o_sphere"), end("o_sphere")
    zoom(c, T, t0, t1, 1.0, 1.06, 540, 860)
    c.drawRect(skia.Rect.MakeLTRB(-60, -60, W + 60, H + 60), paint(shader=K.rad((540, 860), 1100, [ROYAL_BG, ROYAL_DEEP, (0, 0, 8)])))
    G.pool(c, 540, 860, 600, (120, 160, 255), 0.25)
    cx, cy = 540, 820
    rings = [(470, 120, 18), (450, 150, -30), (430, 96, 64), (410, 70, -70)]
    lit = []
    for i, (w, _, _) in enumerate(INFER):
        tw = Wx("o4", w) - 0.08
        lit.append(K.ease(ramp(T, tw, tw + 0.2)))
    # back halves of the rings
    for i, (R, tilt, ang) in enumerate(rings):
        rot = ang + T * (8 + 3 * i) * (1 if i % 2 else -1)
        c.save()
        c.translate(cx, cy)
        c.rotate(rot)
        c.drawArc(skia.Rect.MakeLTRB(-R, -tilt, R, tilt), 180, 180, False, paint(C.GOLD_LO, 0.8, stroke=7))
        c.restore()
    C.doll(c, cx, cy + 420, 1.05, T, pose="stand", tint=(236, 232, 226), eyes=0.0)
    # the guesses, hanging from her on threads like price tags
    tags = [(-300, -330), (300, -250), (-300, 170), (300, 250)]
    for i, ((w, title, val), (dx, dy)) in enumerate(zip(INFER, tags)):
        k = lit[i]
        if k <= 0:
            continue
        ax, ay = cx + dx * 0.12, cy - 120 + dy * 0.3
        tx, ty = cx + dx, cy + dy
        c.drawLine(ax, ay, tx, ty - 50, paint(C.GOLD_HI, 0.9 * k, stroke=2))
        tx = max(200, min(880, tx))
        tag = K.path([(tx - 170, ty - 50), (tx + 140, ty - 50), (tx + 170, ty), (tx + 140, ty + 50), (tx - 170, ty + 50)])
        c.drawPath(tag, paint(shader=C.gold_shader((tx - 170, ty), (tx + 170, ty)), a=k))
        c.drawPath(tag, paint(C.GOLD_LO, k, stroke=3))
        c.drawCircle(tx + 138, ty, 8, paint((20, 14, 6), k))
        K.text(c, title, tx - 10, ty - 8, 26, "cinzel-600", (50, 30, 6), tag="plaque", a=k)
        K.text(c, val, tx - 10, ty + 30, 25, "cormorant-600", (60, 36, 8), tag="plaque", a=k)
    # front halves, each lighting as its guess is engraved
    for i, (R, tilt, ang) in enumerate(rings):
        rot = ang + T * (8 + 3 * i) * (1 if i % 2 else -1)
        c.save()
        c.translate(cx, cy)
        c.rotate(rot)
        c.drawArc(skia.Rect.MakeLTRB(-R, -tilt, R, tilt), 0, 180, False, paint(C.GOLD, 1.0, stroke=9))
        c.drawArc(skia.Rect.MakeLTRB(-R, -tilt, R, tilt), 0, 180, False, paint(C.GOLD_HI, 1.0, stroke=3))
        if lit[min(i, 3)] > 0:
            c.drawArc(skia.Rect.MakeLTRB(-R, -tilt, R, tilt), 0, 180, False, G.glow_paint((255, 230, 150), 0.25 * lit[i], blur=6))
        c.restore()
    c.restore()
    return st.arr


def s_o_mirror(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0, t1 = cut("o_mirror"), end("o_mirror")
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(shader=K.rad((540, 860), 1100, [(16, 26, 90), (2, 4, 30), (0, 0, 6)])))
    turn = K.ease(ramp(stutter(T, Wx("o6", "didn't") - 0.1, 0.25, 0.06, seed=8), Wx("o6", "didn't") - 0.1, Wx("o6", "didn't") + 0.6))
    tk = talk(T, "CURATOR")

    def level(d, cx, cy, s):
        """One mirror: its gilt frame and glass; inside it the next mirror (smaller, further), then her face in front."""
        w, h = 820 * s, 1180 * s
        x0, y0 = cx - w / 2, cy - h / 2
        c.drawRect(skia.Rect.MakeLTRB(x0 - 40 * s, y0 - 40 * s, x0 + w + 40 * s, y0 + h + 40 * s), paint(shader=C.gold_shader((x0, y0), (x0 + w, y0 + h))))
        c.drawRect(skia.Rect.MakeLTRB(x0 - 40 * s, y0 - 40 * s, x0 + w + 40 * s, y0 + h + 40 * s), paint(C.GOLD_LO, stroke=4 * s))
        c.drawRect(skia.Rect.MakeLTRB(x0, y0, x0 + w, y0 + h), paint(shader=K.lin((x0, y0), (x0 + w, y0 + h), [(20, 30, 90), (4, 8, 36)])))
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(x0, y0, x0 + w, y0 + h))
        if d < 6:
            level(d + 1, cx, cy - h * 0.16, s * 0.6)
        look = (turn * (1 if d % 2 else -1) * 0.8, 0.0)
        C.lens_fan(c, cx, cy + h * 0.02, 0.62 * s, T, open_=0.6, swivel=look[0])
        c.drawPath(K.smooth([(cx - 300 * s, cy + h / 2), (cx - 260 * s, cy + h * 0.2), (cx, cy + h * 0.12), (cx + 260 * s, cy + h * 0.2), (cx + 300 * s, cy + h / 2)]),
                   paint(C.LACQUER))
        C.mask(c, cx, cy + h * 0.1, 0.85 * s, T, eyes=1.0, iris="lens", open_=0.55, talk=tk, tint=(222, 214, 208), shadow=(110, 100, 130),
               look=look, tilt=12 * look[0])
        c.restore()
        c.drawRect(skia.Rect.MakeLTRB(x0, y0, x0 + w, y0 + h), paint(shader=K.lin((x0, y0), (x0 + w * 0.6, y0 + h), [(255, 255, 255, 0.10), (255, 255, 255, 0.0)])))

    level(0, 540, 900, 1.0)
    return st.arr

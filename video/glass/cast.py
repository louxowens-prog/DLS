"""The people (and the not-quite-people): Clara, the Governess, the interviewers, mannequins, porcelain graduates.

A face is painted in its own colours first (the albedo), then MODULATED by a light map: two gels from opposite sides
with a dark core between them, the 1970s Italian split light. `porc` (0..1) turns living skin into glazed porcelain:
the colour drains to white, the eyes turn to glass, a seam appears at the jaw, the glaze catches the light. `crack`
(0..1) breaks it open onto nothing."""
import math

import numpy as np
import skia

import gel as G
import kit as K
from kit import BLACK, WHITE, mix, paint

PEOPLE = {
    "clara": dict(skin=(236, 198, 174), lips=(184, 62, 74), iris=(96, 124, 70), brow=(66, 38, 28), hair=(110, 46, 26),
                  shadow=(120, 100, 160), lash=(24, 16, 16), style="loose", blush=0.28, age=0.0, coat="trench"),
    "clara_now": dict(skin=(232, 194, 170), lips=(176, 110, 104), iris=(96, 124, 70), brow=(66, 38, 28), hair=(110, 46, 26),
                      shadow=(170, 140, 130), lash=(44, 30, 26), style="loose", blush=0.08, age=0.0, coat="blazer"),
    "governess": dict(skin=(242, 236, 230), lips=(150, 40, 60), iris=(170, 180, 190), brow=(30, 24, 26), hair=(22, 18, 20),
                      shadow=(120, 110, 130), lash=(20, 16, 18), style="bun", blush=0.0, age=0.25, coat="governess"),
    "int1": dict(skin=(226, 188, 166), lips=(160, 100, 96), iris=(90, 80, 70), brow=(120, 110, 104), hair=(170, 166, 160),
                 shadow=(150, 130, 120), lash=(60, 50, 46), style="bob", blush=0.05, age=0.5, coat="suit"),
    "int2": dict(skin=(150, 104, 80), lips=(120, 66, 60), iris=(50, 34, 24), brow=(30, 20, 16), hair=(24, 18, 16),
                 shadow=(110, 80, 70), lash=(20, 14, 12), style="pony", blush=0.05, age=0.2, coat="suit2"),
    "doll": dict(skin=(244, 240, 236), lips=(196, 40, 60), iris=(60, 110, 170), brow=(80, 50, 40), hair=(60, 30, 20),
                 shadow=(140, 150, 190), lash=(20, 16, 16), style="cap", blush=0.35, age=0.0, coat="gown"),
}

PEOPLE.update({
    # the entity: moon-pale, plum lips, eyes like slowly turning reels of tape
    "merit": dict(skin=(232, 222, 236), lips=(120, 20, 60), iris=(230, 190, 110), brow=(60, 40, 60), hair=(40, 20, 50),
                  shadow=(110, 70, 150), lash=(14, 8, 18), style="none", blush=0.05, age=0.0, coat=None, reel=True),
    # Iris: forty-nine, an engineer, a grey streak she stopped dyeing
    "iris": dict(skin=(226, 186, 160), lips=(168, 104, 100), iris=(84, 100, 70), brow=(70, 50, 40), hair=(70, 48, 36),
                 shadow=(150, 120, 110), lash=(50, 36, 30), style="iris", blush=0.04, age=0.55, coat="cardigan", soft=True),
    # the two faces a face-reader saw: a darker-skinned woman, a lighter-skinned man
    "w_dark": dict(skin=(124, 80, 58), lips=(110, 56, 50), iris=(44, 28, 20), brow=(26, 16, 12), hair=(18, 12, 10),
                   shadow=(90, 60, 50), lash=(14, 10, 8), style="coils", blush=0.0, age=0.1, coat="tee", soft=True),
    "m_light": dict(skin=(232, 196, 176), lips=(176, 120, 112), iris=(70, 100, 140), brow=(110, 80, 56), hair=(120, 86, 56),
                    shadow=(160, 130, 120), lash=(90, 70, 56), style="short", blush=0.0, age=0.2, coat="shirt", male=True),
    # faces of the crowd, for the whispering chorus
    "f_a": dict(skin=(196, 150, 120), lips=(150, 80, 80), iris=(60, 40, 30), brow=(40, 26, 20), hair=(30, 20, 16),
                shadow=(130, 100, 90), lash=(20, 14, 12), style="pony", blush=0.05, age=0.3, coat="tee", soft=True),
    "f_b": dict(skin=(236, 206, 186), lips=(170, 90, 96), iris=(90, 120, 150), brow=(150, 110, 70), hair=(190, 150, 90),
                shadow=(170, 140, 140), lash=(60, 44, 36), style="bob", blush=0.1, age=0.6, coat="cardigan", soft=True),
    "f_c": dict(skin=(150, 100, 74), lips=(120, 66, 60), iris=(50, 34, 24), brow=(30, 20, 16), hair=(24, 18, 16),
                shadow=(110, 80, 70), lash=(20, 14, 12), style="bun", blush=0.0, age=0.15, coat="tee", soft=True),
    # Nadia: thirty-four, a call-center agent; dark hair pulled back, a work polo and a lanyard
    "nadia": dict(skin=(206, 160, 130), lips=(160, 96, 92), iris=(70, 46, 32), brow=(44, 30, 24), hair=(38, 26, 22),
                  shadow=(140, 110, 104), lash=(26, 18, 16), style="pony", blush=0.05, age=0.25, coat="polo", soft=True),
    "nadia_coat": dict(skin=(206, 160, 130), lips=(160, 96, 92), iris=(70, 46, 32), brow=(44, 30, 24), hair=(38, 26, 22),
                       shadow=(140, 110, 104), lash=(26, 18, 16), style="pony", blush=0.05, age=0.25, coat="parka", soft=True),
    # the guide: the narrator in the real world - a clinician, hair pinned back, a white coat
    "guide": dict(skin=(232, 204, 186), lips=(176, 110, 110), iris=(90, 110, 120), brow=(70, 50, 40), hair=(70, 50, 40),
                  shadow=(150, 130, 130), lash=(40, 30, 28), style="bun", blush=0.04, age=0.35, coat="labcoat", soft=True),
})

EXPR = {
    "neutral": dict(open=0.0, brow=0.0, wide=0.0, smile=0.0),
    "fear": dict(open=0.35, brow=0.8, wide=0.55, smile=-0.3),
    "dread": dict(open=0.08, brow=0.45, wide=0.3, smile=-0.2),
    "polite": dict(open=0.0, brow=0.1, wide=0.0, smile=0.45),
    "blank": dict(open=0.0, brow=0.0, wide=0.15, smile=0.0),
    "scream": dict(open=0.9, brow=1.0, wide=0.8, smile=-0.5),
    "lost": dict(open=0.12, brow=0.3, wide=0.1, smile=-0.1),
}


def _lerp(a, b, k):
    return a + (b - a) * k


def face_path():
    return K.smooth([(0, -212), (78, -200), (132, -150), (150, -70), (148, 5), (136, 80), (110, 140), (70, 190), (30, 218),
                     (0, 224), (-30, 218), (-70, 190), (-110, 140), (-136, 80), (-148, 5), (-150, -70), (-132, -150), (-78, -200)])


def _eye(c, side, P, E, porc, blink, gaze, T):
    """One almond eye at (side * 62, -18): lid, eyeshadow, white, iris, pupil, catchlight, liner and lashes."""
    cx, cy = side * 64, -16
    w, h = 88, 36 * (1 + 0.45 * E["wide"])
    op = max(0.0, 1 - blink)
    c.save()
    c.translate(cx, cy)
    # eyeshadow and lid crease
    shp = K.smooth([(-50, 2), (-36, -30 - h * 0.3), (0, -40 - h * 0.35), (36, -32 - h * 0.3), (50, 0), (0, -12)])
    c.drawPath(shp, paint(mix(P["shadow"], P["skin"], 0.35 + 0.4 * porc), 0.85, blur=7))
    up = lambda k: (-w / 2 * (1 - 0.05 * k), -h * 0.55 * op * (1 - k * 0.0))
    eye = skia.Path()
    eye.moveTo(-w / 2, 0)
    eye.cubicTo(-w * 0.28, -h * 0.95 * op, w * 0.18, -h * 1.0 * op, w / 2, -2)
    eye.cubicTo(w * 0.2, h * 0.62 * op, -w * 0.25, h * 0.58 * op, -w / 2, 0)
    eye.close()
    if op > 0.05:
        white = mix((236, 228, 222), (250, 250, 252), porc)
        c.drawPath(eye, paint(white))
        c.save()
        c.clipPath(eye, doAntiAlias=True)
        gx, gy = gaze[0] * 12, gaze[1] * 7
        ir = 19.5 * (1 - 0.06 * E["wide"])
        iris_col = mix(P["iris"], (120, 170, 220), porc * 0.6)
        c.drawCircle(gx, gy - 1, ir, paint(shader=K.rad((gx, gy - 1), ir, [mix(iris_col, WHITE, 0.25), iris_col, mix(iris_col, BLACK, 0.5)], [0, 0.6, 1.0])))
        rng = K.rng_at(side + 3, 9)
        for k in range(14):                                   # iris fibres
            ang = k / 14 * 6.283 + rng.uniform(-0.1, 0.1)
            c.drawLine(gx + math.cos(ang) * 6, gy - 1 + math.sin(ang) * 6, gx + math.cos(ang) * ir * 0.95, gy - 1 + math.sin(ang) * ir * 0.95,
                       paint(mix(iris_col, BLACK, 0.4), 0.35, stroke=1.4))
        pr = (6.5 + 2.0 * E["wide"]) * (1 - 0.35 * porc)
        if P.get("reel"):                                      # a reel of tape turning slowly in the iris
            for k in range(3):
                ang = T * 0.9 * side + k * 2.094
                c.drawCircle(gx + math.cos(ang) * ir * 0.55, gy - 1 + math.sin(ang) * ir * 0.55, ir * 0.22, paint((20, 10, 20), 0.85))
            c.drawCircle(gx, gy - 1, ir * 0.82, paint(mix(iris_col, WHITE, 0.5), 0.5, stroke=1.6))
        c.drawCircle(gx, gy - 1, pr, paint((8, 6, 8)))
        c.drawCircle(gx, gy - 1, ir, paint(mix(iris_col, BLACK, 0.7), 0.8, stroke=2.2))
        # the lid's shadow across the top of the eyeball
        c.drawPath(eye, paint(shader=K.lin((0, -h), (0, h * 0.2), [(40, 20, 30, 0.55), (40, 20, 30, 0.0)])))
        # catchlight; glass eyes get a hard second one
        c.drawCircle(gx - 6, gy - 7, 3.6 + 2.5 * porc, paint(WHITE, 0.9))
        if porc > 0.3:
            c.drawCircle(gx + 6, gy + 5, 2.2, paint(WHITE, 0.6 * porc))
        c.restore()
    # upper liner and lashes
    liner = skia.Path()
    liner.moveTo(-w / 2 - 2, 0)
    liner.cubicTo(-w * 0.28, -h * 0.98 * op - 1, w * 0.18, -h * 1.04 * op - 1, w / 2 + 8, -6)
    soft = P.get("male") or P.get("soft")
    c.drawPath(liner, paint(P["lash"], 1.0, stroke=(3.5 if soft else 6.0 + 1.5 * (1 - porc))))
    if not soft:
        c.drawPath(K.path([(w / 2 + 2, -4), (w / 2 + 22, -16), (w / 2 + 4, -10)]), paint(P["lash"], 0.95))     # the wing
    crease = skia.Path()
    crease.moveTo(-w / 2 + 4, -h * 0.9 * op - 6)
    crease.cubicTo(-w * 0.2, -h * 1.5 - 8, w * 0.2, -h * 1.5 - 8, w / 2 - 2, -h * 0.85 - 8)
    c.drawPath(crease, paint(mix(P["shadow"], BLACK, 0.4), 0.55, stroke=3, blur=1.5))
    nlash = 0 if P.get("male") else (7 if P.get("soft") else 13)
    for k in range(nlash):
        u = 0.25 + 0.75 * (k + 0.5) / nlash                    # mostly toward the outer corner
        uu = u if side > 0 else u
        x = (-w / 2 + w * uu) * (1 if side > 0 else 1)
        if side < 0:
            x = w / 2 - w * uu
        y = -h * op * (0.95 * math.sin(math.pi * min(1.0, (x + w / 2) / w * 1.05)))
        out = (x / (w / 2))
        L = (6 + 12 * u) * (1 - 0.3 * porc)
        q = skia.Path()
        q.moveTo(x, y - 1)
        q.quadTo(x + out * L * 0.6, y - L * 0.9, x + out * L * 1.1, y - L * 0.75)
        c.drawPath(q, paint(P["lash"], 0.9, stroke=2.4 - 0.8 * (k % 2)))
    if op <= 0.05:
        c.drawPath(K.bez_path([(-w / 2, 0), (0, 6), (w / 2, -2)]), paint(P["lash"], 1.0, stroke=4))
    # lower lid line
    lo = skia.Path()
    lo.moveTo(-w / 2 + 6, 1)
    lo.cubicTo(-w * 0.2, h * 0.6 * op + 2, w * 0.2, h * 0.62 * op + 2, w / 2 - 4, 0)
    c.drawPath(lo, paint(mix(P["skin"], BLACK, 0.35), 0.5, stroke=2))
    c.restore()


def _brow(c, side, P, E, porc):
    lift = -14 * E["brow"]
    inner = -8 * E["brow"]
    p = skia.Path()
    x0, x1 = side * 24, side * 108
    p.moveTo(x0, -62 + inner)
    p.quadTo(side * 72, -84 + lift, x1, -62 + lift * 0.4)
    col = P["brow"] if porc < 0.5 else mix(P["brow"], (120, 70, 60), porc)
    c.drawPath(p, paint(col, 0.95, stroke=(14.0 if P.get("male") else 8.0 - 3 * porc)))


def _nose(c, P, porc):
    sk = P["skin"]
    dk = mix(sk, BLACK, 0.45)
    c.drawPath(K.bez_path([(-12, -24), (-16, 30), (-26, 64)]), paint(dk, 0.35, stroke=7, blur=5))
    c.drawPath(K.bez_path([(12, -24), (16, 30), (26, 64)]), paint(dk, 0.35, stroke=7, blur=5))
    c.drawPath(K.smooth([(-8, -30), (8, -30), (10, 50), (0, 66), (-10, 50)]), paint(mix(sk, WHITE, 0.3), 0.45, blur=5))
    wing = paint(mix(sk, BLACK, 0.35), 0.75, stroke=3.5)
    c.drawPath(K.bez_path([(-30, 62), (-34, 80), (-14, 82)]), wing)
    c.drawPath(K.bez_path([(30, 62), (34, 80), (14, 82)]), wing)
    for s in (-1, 1):
        c.drawOval(skia.Rect.MakeXYWH(s * 15 - 8, 74, 16, 8), paint(mix(sk, BLACK, 0.65), 0.8))
    c.drawCircle(0, 64, 9, paint(mix(sk, WHITE, 0.5), 0.5, blur=4))
    c.drawPath(K.bez_path([(-6, 88), (0, 104), (6, 88)]), paint(dk, 0.25, stroke=6, blur=3))     # philtrum


def _mouth(c, P, E, talk, porc):
    sm = E["smile"]
    o = min(1.0, E["open"] + 0.55 * talk)
    lips = P["lips"]
    w = 52 + 4 * sm
    cy = 134
    up = skia.Path()
    up.moveTo(-w, cy - 2 * sm)
    up.cubicTo(-w * 0.6, cy - 18, -w * 0.25, cy - 22, 0, cy - 11)
    up.cubicTo(w * 0.25, cy - 22, w * 0.6, cy - 18, w, cy - 2 * sm)
    up.cubicTo(w * 0.5, cy + 2 + o * 6, -w * 0.5, cy + 2 + o * 6, -w, cy - 2 * sm)
    up.close()
    gap = o * 26
    lo = skia.Path()
    lo.moveTo(-w + 2, cy - 2 * sm + gap * 0.2)
    lo.cubicTo(-w * 0.5, cy + 6 + gap, w * 0.5, cy + 6 + gap, w - 2, cy - 2 * sm + gap * 0.2)
    lo.cubicTo(w * 0.55, cy + 32 + gap, -w * 0.55, cy + 32 + gap, -w + 2, cy - 2 * sm + gap * 0.2)
    lo.close()
    if o > 0.03:
        inner = K.smooth([(-w * 0.85, cy), (0, cy + 2), (w * 0.85, cy), (w * 0.5, cy + gap + 4), (-w * 0.5, cy + gap + 4)])
        c.drawPath(inner, paint((40, 10, 16) if porc < 0.7 else (10, 8, 10)))
        if o > 0.25 and porc < 0.7:
            c.drawRect(skia.Rect.MakeLTRB(-w * 0.5, cy + 1, w * 0.5, cy + 7), paint((236, 230, 220), 0.9))
    c.drawPath(up, paint(lips))
    c.drawPath(lo, paint(mix(lips, WHITE, 0.06)))
    c.drawOval(skia.Rect.MakeXYWH(-16, cy + 8 + gap, 26, 7), paint(WHITE, 0.35 + 0.3 * porc, blur=2))   # gloss
    c.drawPath(K.bez_path([(-w, cy - 2 * sm), (0, cy + 3 + gap * 0.4), (w, cy - 2 * sm)]), paint(mix(lips, BLACK, 0.5), 0.5, stroke=2))


def _hair_back(c, P, T):
    st, hc = P["style"], P["hair"]
    if st == "loose":
        c.drawPath(K.smooth([(-150, -200), (0, -262), (150, -200), (196, -40), (210, 200), (190, 420), (100, 440), (60, 200),
                             (-60, 200), (-100, 440), (-190, 420), (-210, 200), (-196, -40)]), paint(hc))
    elif st == "bun":
        c.drawCircle(0, -232, 74, paint(hc))
        c.drawPath(K.smooth([(-152, -150), (0, -240), (152, -150), (150, 0), (-150, 0)]), paint(hc))
    elif st == "bob":
        c.drawPath(K.smooth([(-160, -180), (0, -250), (160, -180), (176, 40), (150, 150), (-150, 150), (-176, 40)]), paint(hc))
    elif st == "pony":
        c.drawPath(K.smooth([(-150, -170), (0, -250), (150, -170), (150, 20), (-150, 20)]), paint(hc))
    elif st == "scarf":
        c.drawPath(K.smooth([(-158, -160), (0, -256), (158, -160), (184, 40), (176, 240), (120, 300), (-120, 300), (-176, 240), (-184, 40)]), paint(hc))
    elif st == "cap":
        c.drawPath(K.smooth([(-150, -160), (0, -240), (150, -160), (164, 60), (140, 160), (-140, 160), (-164, 60)]), paint(hc))
    elif st == "iris":                                       # shoulder-length, a little untidy, a grey streak
        c.drawPath(K.smooth([(-156, -170), (0, -256), (156, -170), (182, 20), (176, 210), (130, 250), (100, 180), (-100, 180),
                             (-130, 250), (-176, 210), (-182, 20)]), paint(hc))
    elif st == "coils":                                      # a halo of natural coils
        rng = K.rng_at(5, 5)
        for k in range(46):
            ang = k / 46 * 6.283
            r = rng.uniform(190, 236)
            c.drawCircle(math.cos(ang) * r * 1.0, -60 + math.sin(ang) * r * 0.95, rng.uniform(46, 70), paint(mix(hc, WHITE, rng.uniform(0, 0.08))))
        c.drawCircle(0, -60, 210, paint(hc))
    elif st == "short":
        c.drawPath(K.smooth([(-150, -150), (0, -250), (150, -150), (152, -40), (-152, -40)]), paint(hc))


def _hair_front(c, P, T):
    st, hc = P["style"], P["hair"]
    hi = mix(hc, WHITE, 0.3)
    dk = mix(hc, BLACK, 0.45)
    if st in ("loose", "scarf"):
        for s in (-1, 1):                                      # centre parting, feathered waves framing the face
            p = K.smooth([(s * 4, -214), (s * 84, -210), (s * 150, -156), (s * 178, -40), (s * 182, 90), (s * 170, 230),
                          (s * 140, 300), (s * 128, 180), (s * 138, 40), (s * 128, -60), (s * 92, -150), (s * 30, -192)])
            c.drawPath(p, paint(shader=K.lin((s * 20, -200), (s * 180, 100), [hc, mix(hc, BLACK, 0.2)])))
            for k in range(7):
                o = k * 7
                q = K.bez_path([(s * (14 + o), -206 + k * 2), (s * (118 + o * 0.6), -170 + k * 18), (s * (150 + k * 3), 20 + k * 34)])
                c.drawPath(q, paint(hi if k % 2 else dk, 0.35, stroke=2.5 + (k % 3)))
            for k in range(3):                                 # the feathered flick at the side of the face, 1974
                q = K.bez_path([(s * (130 + k * 8), 60 + k * 50), (s * (176 + k * 4), 110 + k * 50), (s * (150 + k * 10), 170 + k * 50)])
                c.drawPath(q, paint(hi, 0.3, stroke=3))
    if st == "scarf":                                           # a silk headscarf tied under the chin, 1974
        sc = P["scarf"]
        band = K.smooth([(-176, -60), (-150, -190), (-60, -262), (60, -262), (150, -190), (176, -60), (150, -110), (60, -214),
                         (-60, -214), (-150, -110)])
        c.drawPath(band, paint(sc))
        c.drawPath(K.smooth([(-140, -120), (-178, 40), (-150, 180), (-100, 236), (-60, 250), (-110, 200), (-150, 60), (-128, -60)]), paint(mix(sc, BLACK, 0.15)))
        c.drawPath(K.smooth([(140, -120), (178, 40), (150, 180), (100, 236), (60, 250), (110, 200), (150, 60), (128, -60)]), paint(mix(sc, BLACK, 0.15)))
        c.drawPath(K.smooth([(-60, 240), (0, 262), (60, 240), (40, 300), (0, 286), (-40, 300)]), paint(mix(sc, BLACK, 0.1)))
        for k in range(5):
            c.drawPath(K.bez_path([(-120 + k * 60, -230), (-100 + k * 50, -200), (-110 + k * 55, -160)]), paint(mix(sc, WHITE, 0.3), 0.25, stroke=3))
    elif st == "bun":                                         # severe centre parting, hair slicked flat
        for s in (-1, 1):
            c.drawPath(K.smooth([(s * 2, -214), (s * 86, -200), (s * 140, -150), (s * 152, -70), (s * 140, -40), (s * 120, -130), (s * 60, -186)]), paint(hc))
        c.drawLine(0, -214, 0, -186, paint(mix(hc, WHITE, 0.3), 0.5, stroke=2))
        for k in range(5):
            c.drawPath(K.bez_path([(6 + k * 6, -210), (80 + k * 10, -196), (130 + k * 3, -130)]), paint(mix(hc, WHITE, 0.35), 0.25, stroke=2))
            c.drawPath(K.bez_path([(-6 - k * 6, -210), (-80 - k * 10, -196), (-130 - k * 3, -130)]), paint(mix(hc, WHITE, 0.35), 0.25, stroke=2))
    elif st == "bob":
        c.drawPath(K.smooth([(-164, -150), (-40, -240), (120, -220), (168, -120), (178, 60), (150, 150), (130, 60), (120, -100), (-60, -180), (-140, -40), (-150, 150), (-176, 60)]), paint(hc))
    elif st == "pony":
        c.drawPath(K.smooth([(-150, -150), (0, -236), (150, -150), (140, -90), (0, -190), (-140, -90)]), paint(hc))
    elif st == "iris":
        c.drawPath(K.smooth([(-160, -140), (-60, -232), (60, -236), (150, -170), (176, -40), (170, 120), (150, 230), (136, 120),
                             (124, -40), (40, -170), (-60, -170), (-128, -60), (-142, 120), (-156, 230), (-176, 120), (-176, -40)]), paint(hc))
        c.drawPath(K.smooth([(-60, -230), (-20, -236), (-70, -160), (-120, -40), (-140, 100), (-150, 60), (-130, -60), (-100, -160)]),
                   paint(mix(hc, (210, 206, 200), 0.75)))     # the grey streak
        for k in range(6):
            c.drawPath(K.bez_path([(-40 + k * 30, -226), (60 + k * 10, -180), (130 + k * 4, -60)]), paint(mix(hc, WHITE, 0.25), 0.3, stroke=2.5))
    elif st == "coils":
        rng = K.rng_at(6, 6)
        for k in range(18):
            ang = math.pi + k / 17 * math.pi
            c.drawCircle(math.cos(ang) * 150, -150 + math.sin(ang) * 90, rng.uniform(30, 44), paint(mix(hc, WHITE, 0.05)))
    elif st == "short":
        c.drawPath(K.smooth([(-152, -110), (-120, -210), (0, -246), (120, -214), (154, -110), (140, -150), (60, -196), (-60, -190), (-140, -150)]), paint(hc))
        for k in range(8):
            c.drawPath(K.bez_path([(-110 + k * 30, -220), (-80 + k * 30, -200), (-60 + k * 32, -170)]), paint(mix(hc, WHITE, 0.25), 0.35, stroke=3))
    elif st == "cap":                                         # a painted doll's curls under a mortarboard
        for s in (-1, 1):
            for k in range(3):
                c.drawCircle(s * (128 + k * 6), -60 + k * 70, 36, paint(hc))


def mortarboard(c, porc=1.0, tassel=0.0):
    board = K.path([(-200, -236), (0, -300), (200, -236), (0, -176)])
    c.drawPath(K.smooth([(-118, -230), (0, -262), (118, -230), (112, -170), (0, -150), (-112, -170)]), paint((20, 18, 24)))
    c.drawPath(board, paint((24, 22, 28)))
    c.drawPath(board, paint((90, 80, 110), 0.5, stroke=3))
    c.drawCircle(0, -238, 8, paint((200, 160, 60)))
    sw = 18 * math.sin(tassel)
    c.drawPath(K.bez_path([(0, -238), (120 + sw, -220), (150 + sw, -140)]), paint((200, 160, 60), stroke=4))
    c.drawRect(skia.Rect.MakeXYWH(140 + sw, -146, 20, 44), paint((210, 170, 70)))


def _form(c, P, porc):
    """Volume painted into the skin itself: eye sockets, cheek hollows, the sides of the nose, edges turning away;
    light on the forehead, the bridge of the nose, the cheekbones and the chin."""
    sk = P["skin"]
    dk = mix(sk, BLACK, 0.5)
    hi = mix(sk, WHITE, 0.4)
    fp = face_path()
    c.save()
    c.clipPath(fp, doAntiAlias=True)
    c.drawPath(fp, paint(shader=K.rad((0, -10), 250, [dk + (0.0,), dk + (0.0,), dk + (0.55,)], [0.0, 0.62, 1.0])))
    for s in (-1, 1):
        c.drawOval(skia.Rect.MakeXYWH(s * 64 - 60, -74, 120, 74), paint(dk, 0.32 * (1 - 0.4 * porc), blur=18))
        c.drawPath(K.smooth([(s * 146, 30), (s * 104, 56), (s * 62, 100), (s * 98, 118), (s * 140, 92)]), paint(dk, 0.32 * (1 - 0.5 * porc), blur=16))
        c.drawOval(skia.Rect.MakeXYWH(s * 98 - 34, -6, 68, 46), paint(hi, 0.32, blur=16))
        c.drawOval(skia.Rect.MakeXYWH(s * 22 - 12, -14, 24, 92), paint(dk, 0.2, blur=8))
    c.drawOval(skia.Rect.MakeLTRB(-70, -206, 70, -110), paint(hi, 0.35, blur=26))
    c.drawOval(skia.Rect.MakeLTRB(-9, -44, 9, 66), paint(hi, 0.45, blur=6))
    c.drawCircle(0, 198, 26, paint(hi, 0.3, blur=12))
    c.drawOval(skia.Rect.MakeLTRB(-34, 166, 34, 186), paint(dk, 0.3, blur=8))
    c.restore()


def _body(c, P, T):
    """Shoulders and clothes, below the neck (local face units; the neck meets them about y = 300)."""
    kind = P.get("coat")
    if kind is None:
        return
    if kind == "trench":                                       # a 1970s trench coat, collar up, a silk neckerchief
        coat = (196, 168, 120)
        c.drawPath(K.smooth([(-300, 640), (-290, 380), (-180, 300), (-70, 286), (70, 286), (180, 300), (290, 380), (300, 640)]), paint(coat))
        for s in (-1, 1):
            c.drawPath(K.path([(s * 70, 270), (s * 150, 250), (s * 196, 330), (s * 110, 520), (s * 40, 330)]), paint(mix(coat, BLACK, 0.12)))
            c.drawPath(K.path([(s * 70, 270), (s * 150, 250), (s * 196, 330), (s * 110, 520), (s * 40, 330)]), paint(mix(coat, BLACK, 0.4), 0.6, stroke=3))
        c.drawPath(K.smooth([(-74, 268), (0, 300), (74, 268), (60, 330), (0, 350), (-60, 330)]), paint((200, 40, 54)))
        c.drawPath(K.smooth([(-20, 330), (20, 330), (36, 430), (0, 410), (-30, 440)]), paint((176, 30, 44)))
    elif kind == "blazer":                                     # now: a navy blazer, a plain white top
        c.drawPath(K.smooth([(-300, 640), (-290, 380), (-170, 304), (-70, 290), (70, 290), (170, 304), (290, 380), (300, 640)]), paint((34, 40, 60)))
        c.drawPath(K.path([(-70, 290), (70, 290), (40, 420), (0, 460), (-40, 420)]), paint((236, 236, 232)))
        for s in (-1, 1):
            c.drawPath(K.path([(s * 70, 290), (s * 120, 300), (s * 60, 470), (s * 30, 440)]), paint((26, 30, 46)))
    elif kind == "governess":                                  # black, high to the chin, lace, a cameo at the throat
        c.drawPath(K.smooth([(-280, 640), (-290, 360), (-210, 270), (-80, 240), (80, 240), (210, 270), (290, 360), (280, 640)]), paint((14, 12, 16)))
        c.drawPath(K.smooth([(-84, 150), (84, 150), (96, 300), (-96, 300)]), paint((20, 16, 22)))
        for k in range(9):
            x = -80 + k * 20
            c.drawCircle(x, 158 + 6 * math.sin(k), 9, paint((60, 54, 66), 0.9))
        c.drawOval(skia.Rect.MakeLTRB(-26, 240, 26, 300), paint((200, 120, 100)))
        c.drawOval(skia.Rect.MakeLTRB(-26, 240, 26, 300), paint((210, 170, 80), stroke=5))
        c.drawPath(K.smooth([(-6, 250), (10, 256), (12, 276), (4, 292), (-10, 286), (-8, 268)]), paint((246, 236, 226)))
        for s in (-1, 1):
            c.drawPath(K.smooth([(s * 200, 270), (s * 290, 300), (s * 320, 400), (s * 240, 380)]), paint((22, 18, 26)))
    elif kind in ("suit", "suit2"):
        col = (90, 90, 96) if kind == "suit" else (24, 24, 28)
        c.drawPath(K.smooth([(-300, 640), (-290, 380), (-170, 304), (-70, 290), (70, 290), (170, 304), (290, 380), (300, 640)]), paint(col))
        if kind == "suit":
            c.drawPath(K.path([(-60, 290), (60, 290), (30, 400), (-30, 400)]), paint((230, 232, 236)))
    elif kind == "cardigan":                                   # a grey cardigan over a plain top
        c.drawPath(K.smooth([(-300, 640), (-290, 380), (-170, 304), (-70, 290), (70, 290), (170, 304), (290, 380), (300, 640)]), paint((96, 92, 100)))
        c.drawPath(K.path([(-70, 290), (70, 290), (30, 470), (-30, 470)]), paint((50, 60, 80)))
        for sd in (-1, 1):
            c.drawPath(K.path([(sd * 70, 290), (sd * 110, 300), (sd * 40, 640), (sd * 20, 640)]), paint((80, 76, 84)))
    elif kind == "tee":
        c.drawPath(K.smooth([(-300, 640), (-290, 380), (-170, 304), (-70, 290), (70, 290), (170, 304), (290, 380), (300, 640)]), paint((70, 64, 80)))
        c.drawPath(K.bez_path([(-74, 290), (0, 330), (74, 290)]), paint((50, 44, 60), stroke=8))
    elif kind == "shirt":                                      # an open-necked shirt
        c.drawPath(K.smooth([(-300, 640), (-290, 380), (-170, 304), (-70, 290), (70, 290), (170, 304), (290, 380), (300, 640)]), paint((180, 190, 206)))
        for sd in (-1, 1):
            c.drawPath(K.path([(sd * 10, 300), (sd * 90, 280), (sd * 60, 360)]), paint((200, 210, 226)))
    elif kind == "labcoat":                                    # a white coat over a grey crew neck
        c.drawPath(K.smooth([(-300, 640), (-290, 380), (-170, 304), (-70, 290), (70, 290), (170, 304), (290, 380), (300, 640)]), paint((236, 240, 244)))
        c.drawPath(K.path([(-70, 290), (70, 290), (0, 420)]), paint((120, 128, 140)))
        for sd in (-1, 1):
            c.drawPath(K.path([(sd * 70, 290), (sd * 150, 300), (sd * 90, 520), (sd * 10, 440)]), paint((214, 220, 228)))
            c.drawPath(K.path([(sd * 70, 290), (sd * 150, 300), (sd * 90, 520), (sd * 10, 440)]), paint((150, 160, 172), 0.6, stroke=3))
        c.drawRect(skia.Rect.MakeLTRB(150, 480, 230, 500), paint((60, 70, 90)))
    elif kind == "polo":                                       # a charcoal work polo, a lanyard and an ID card
        c.drawPath(K.smooth([(-300, 640), (-290, 380), (-170, 304), (-70, 290), (70, 290), (170, 304), (290, 380), (300, 640)]), paint((58, 64, 74)))
        for sd in (-1, 1):
            c.drawPath(K.path([(sd * 10, 296), (sd * 92, 282), (sd * 70, 340), (sd * 16, 330)]), paint((72, 78, 90)))
        c.drawPath(K.bez_path([(-60, 300), (0, 470), (60, 300)]), paint((40, 90, 160), stroke=10))
        c.drawRect(skia.Rect.MakeLTRB(-34, 470, 34, 560), paint((236, 238, 240)))
        c.drawRect(skia.Rect.MakeLTRB(-26, 482, 4, 516), paint((120, 130, 150)))
    elif kind == "parka":                                      # a dark winter parka, collar up
        c.drawPath(K.smooth([(-310, 640), (-300, 370), (-180, 296), (-70, 284), (70, 284), (180, 296), (300, 370), (310, 640)]), paint((40, 44, 52)))
        for sd in (-1, 1):
            c.drawPath(K.smooth([(sd * 60, 270), (sd * 170, 250), (sd * 200, 360), (sd * 90, 420)]), paint((52, 56, 66)))
        c.drawLine(0, 300, 0, 640, paint((20, 22, 26), stroke=6))
    elif kind == "gown":                                       # a graduate's gown and hood
        c.drawPath(K.smooth([(-300, 640), (-290, 380), (-170, 300), (-70, 286), (70, 286), (170, 300), (290, 380), (300, 640)]), paint((20, 18, 26)))
        c.drawPath(K.smooth([(-150, 300), (0, 360), (150, 300), (120, 420), (0, 460), (-120, 420)]), paint((150, 20, 40)))
        c.drawPath(K.smooth([(-70, 286), (0, 320), (70, 286), (0, 300)]), paint((240, 236, 230)))


def light_map(c, L, R, core=0.6, amb=(30, 26, 30), top=None, rim=None, w=380, h=700, oy=0, ang=0.0, fill=0.7):
    """The light falling on a face-sized area, drawn into a MODULATE layer: a key gel from the left, a weaker one from
    the right, a dark core between them, and a little more light from above than below."""
    c.drawPaint(paint(amb))
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    p0, p1 = (-ca * w / 2, oy - sa * w / 2), (ca * w / 2, oy + sa * w / 2)
    Rf = tuple(int(v * fill) for v in R)
    if core <= 0.2:                                            # flat light: no shadow core at all, just a soft side bias
        stops = [0.0, 1.0]
        cols = [L + (1.0,), R + (1.0,)]
    else:
        stops = [0.0, 0.3 * (1 - core) + 0.12, 0.5 - 0.035 * core, 0.5 + 0.05 * core, 1 - 0.3 * (1 - core) - 0.12, 1.0]
        cols = [L + (1.0,), L + (0.8,), L + (0.0,), Rf + (0.0,), Rf + (0.8,), Rf + (1.0,)]
    p = paint(shader=K.lin(p0, p1, cols, stops))
    p.setBlendMode(skia.BlendMode.kPlus)
    c.drawRect(skia.Rect.MakeLTRB(-w * 2, -h, w * 2, h), p)
    if top is not None:
        G.pool(c, 0, -h * 0.4, w * 0.9, top, 0.5)
    fall = paint(shader=K.lin((0, -260), (0, 700), [(0, 0, 0, 0.0), (0, 0, 0, 0.0), (0, 0, 0, 0.55)], [0.0, 0.45, 1.0]))
    c.drawRect(skia.Rect.MakeLTRB(-w * 2, -h, w * 2, h * 1.5), fall)


def face(c, x, y, s, who, T, L=(255, 60, 170), R=(40, 230, 140), core=0.55, amb=(26, 22, 28), expr="neutral", talk=0.0,
         blink=0.0, gaze=(0.0, 0.0), porc=0.0, crack=0.0, tilt=0.0, neck=True, top=None, rim=None, glaze=1.0, cap=False,
         seam=None, light_ang=0.0, collar=None, a=1.0):
    """A face (front view) at (x, y) = the bridge of the nose, scale s (face about 300 px wide at s = 1)."""
    P = dict(PEOPLE[who])
    E = EXPR[expr] if isinstance(expr, str) else expr
    if porc > 0:                                               # living skin draining to porcelain
        P["skin"] = mix(P["skin"], (246, 242, 238), porc)
        P["shadow"] = mix(P["shadow"], (160, 170, 200), porc * 0.6)
        P["lips"] = mix(P["lips"], (200, 36, 56), porc * 0.7)
    c.save()
    c.translate(x, y)
    c.rotate(tilt)
    c.scale(s, s)
    lp = paint()
    lp.setAlphaf(a)
    c.saveLayer(None, lp)
    # --- albedo
    _hair_back(c, P, T)
    if neck:
        c.drawPath(K.smooth([(-60, 150), (60, 150), (70, 320), (-70, 320)]), paint(mix(P["skin"], BLACK, 0.12)))
        c.drawPath(K.smooth([(-70, 190), (70, 190), (60, 260), (-60, 260)]), paint(mix(P["skin"], BLACK, 0.45), 0.5, blur=16))
        _body(c, P, T)
        if collar is not None:
            collar(c)
    fp = face_path()
    c.drawPath(fp, paint(P["skin"]))
    if P["blush"] > 0:
        for sd in (-1, 1):
            c.drawCircle(sd * 92, 64, 44, paint((220, 110, 110), P["blush"] * (1 - porc * 0.3), blur=22))
    c.drawPath(K.smooth([(-150, -10), (-118, 70), (-96, 150), (-60, 196), (-120, 150), (-148, 60)]), paint(mix(P["skin"], BLACK, 0.25), 0.35, blur=10))
    c.drawPath(K.smooth([(150, -10), (118, 70), (96, 150), (60, 196), (120, 150), (148, 60)]), paint(mix(P["skin"], BLACK, 0.25), 0.35, blur=10))
    _form(c, P, porc)
    if P.get("age", 0) > 0.3:                                  # the years: crow's feet, the lines from nose to mouth
        k = P["age"]
        dk = mix(P["skin"], BLACK, 0.4)
        for sd in (-1, 1):
            for j in range(3):
                c.drawPath(K.bez_path([(sd * 112, -26 + j * 12), (sd * 126, -22 + j * 14), (sd * 138, -30 + j * 20)]), paint(dk, 0.3 * k, stroke=2))
            c.drawPath(K.bez_path([(sd * 40, 76), (sd * 66, 108), (sd * 64, 150)]), paint(dk, 0.4 * k, stroke=3, blur=1.5))
        for j in range(2):
            c.drawPath(K.bez_path([(-60, -120 - j * 18), (0, -128 - j * 18), (60, -120 - j * 18)]), paint(dk, 0.18 * k, stroke=2))
    if P.get("male"):                                          # a squarer jaw in shadow, a shaved shadow on the chin
        c.drawPath(K.smooth([(-136, 80), (-120, 170), (-60, 214), (0, 226), (60, 214), (120, 170), (136, 80), (90, 150), (0, 196), (-90, 150)]),
                   paint(mix(P["skin"], (60, 50, 60), 0.5), 0.35, blur=10))
    for sd in (-1, 1):
        _brow(c, sd, P, E, porc)
        _eye(c, sd, P, E, porc, blink, gaze, T)
    _nose(c, P, porc)
    _mouth(c, P, E, talk, porc)
    _hair_front(c, P, T)
    if cap or P["style"] == "cap":
        mortarboard(c, porc, T * 2)
    # --- light
    mp = skia.Paint()
    mp.setBlendMode(skia.BlendMode.kModulate)
    c.saveLayer(None, mp)
    light_map(c, L, R, core, amb, top, rim, ang=light_ang)
    c.restore()
    # --- glaze: porcelain takes hard highlights
    if porc > 0.05 and glaze > 0:
        for (hx, hy, r, k) in ((-70, -120, 46, 0.5), (84, 30, 30, 0.35), (0, 50, 14, 0.45), (-30, 200, 18, 0.3)):
            c.drawCircle(hx, hy, r, G.glow_paint((255, 250, 245), k * porc * glaze, blur=r * 0.5))
    if seam is not None or porc > 0.6:                         # the joint line of a doll, under the jaw and at the hairline
        k = (porc - 0.6) / 0.4 if seam is None else seam
        c.drawPath(K.bez_path([(-122, 120), (0, 238), (122, 120)]), paint((60, 50, 60), 0.5 * min(1, k), stroke=2.5))
    c.restore()                                                # end of the face layer
    if crack > 0:
        _crack(c, crack, T)
    c.restore()


def _crack(c, k, T):
    """A crack across the porcelain; at k > 0.5 a shard falls away onto blackness, and dust runs out."""
    rng = K.rng_at(77, 5)
    pts = [(-150, -60)]
    x, y = -150, -60
    n = int(4 + 14 * min(1.0, k * 2))
    for i in range(n):
        x += rng.uniform(14, 26)
        y += rng.uniform(-22, 26)
        pts.append((x, y))
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    c.drawPath(p, paint((20, 16, 20), 1.0, stroke=3.2))
    c.drawPath(p, paint(WHITE, 0.35, stroke=1.2))
    for i in range(2, len(pts) - 1, 3):
        bx, by = pts[i]
        c.drawLine(bx, by, bx + rng.uniform(-30, 30), by + rng.uniform(-40, -10), paint((20, 16, 20), 0.9, stroke=2))
    if k > 0.5:
        u = min(1.0, (k - 0.5) / 0.5)
        hole = K.smooth([(-40, -50), (20, -70), (70, -30), (60, 30), (10, 50), (-30, 20)])
        c.drawPath(hole, paint((0, 0, 0)))                     # nothing inside
        c.save()                                               # the shell's thickness, caught on the lower rim
        c.clipPath(hole, doAntiAlias=True)
        c.translate(-7, -9)
        c.drawPath(hole, paint((0, 0, 0)))
        c.restore()
        c.save()
        c.clipPath(hole, doAntiAlias=True)
        c.drawPath(hole, paint((150, 120, 170), 0.85, stroke=9))
        c.translate(-6, -8)
        c.drawPath(hole, paint((0, 0, 0), 1.0, stroke=10))
        c.restore()
        c.drawPath(hole, paint((30, 20, 34), 0.9, stroke=2.5))
        # the shard: it tips forward out of the face (its rough unglazed back turns to us), then drops into the dark
        if u < 1.0:
            c.save()
            c.translate(20 * u, 900 * u * u)
            c.rotate(-50 * u)
            fl = math.cos(math.pi * min(1.0, u * 1.6))             # 1 = glazed face, -1 = the back
            c.scale(0.9 - 0.25 * u, max(0.08, abs(fl)) * (0.9 - 0.25 * u))
            if fl > 0:
                c.drawPath(hole, paint(shader=K.lin((-40, -60), (60, 50), [(236, 120, 196), (150, 120, 220), (90, 110, 230)])))
                c.drawPath(hole, paint((255, 240, 250), 0.35, stroke=2))
            else:
                c.drawPath(hole, paint((84, 64, 92)))
                for j in range(14):
                    c.drawCircle(rng.uniform(-30, 50), rng.uniform(-50, 30), rng.uniform(1.5, 3.5), paint((40, 30, 46), 0.8))
                c.drawPath(hole, paint((170, 140, 180), 0.5, stroke=2))
            c.restore()
        for i in range(30):                                     # dust running out of the hole
            dx = rng.uniform(-30, 50)
            dy = rng.uniform(0, 300) * u
            c.drawCircle(10 + dx * 0.5, 40 + dy, rng.uniform(1, 3), paint((200, 190, 180), 0.6 * (1 - dy / 320)))


def walker_back(c, x, y, s, T, phase=None, coat=(196, 168, 120), hair=(110, 46, 26), key=(255, 60, 170), rim=(40, 220, 140),
                a=1.0, walking=True, legs=(30, 24, 26)):
    """Clara from behind, walking away: long auburn hair, a belted trench coat, stockinged legs, heels; lit from ahead
    so she is mostly silhouette, with gel rims. (x, y) = between the feet; about 900 px tall at s = 1."""
    ph = (T * 5.6 if phase is None else phase) if walking else 0.0
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    lp = paint()
    lp.setAlphaf(a)
    c.saveLayer(None, lp)
    sw = math.sin(ph)
    bob = abs(math.cos(ph)) * 8
    c.translate(0, -bob)
    for side, k in ((-1, sw), (1, -sw)):                       # legs: the far one darker
        lift = max(0.0, k) * 26
        lx = side * 34
        leg = K.smooth([(lx - 22, -360), (lx + 22, -360), (lx + 16, -170), (lx + 10 + k * 10, -30 - lift), (lx - 8 + k * 10, -30 - lift), (lx - 16, -170)])
        c.drawPath(leg, paint(mix(legs, BLACK, 0.2 if side < 0 else 0.0)))
        c.drawPath(K.path([(lx - 12 + k * 10, -34 - lift), (lx + 14 + k * 10, -34 - lift), (lx + 18 + k * 10, -4 - lift), (lx - 16 + k * 10, -2 - lift)]),
                   paint((14, 10, 12)))
    coat_p = K.smooth([(-130, -340), (-118, -560), (-96, -700), (-60, -760), (60, -760), (96, -700), (118, -560), (130, -340),
                       (90 + sw * 10, -300), (-90 + sw * 10, -300)])
    c.drawPath(coat_p, paint(coat))
    c.drawRect(skia.Rect.MakeLTRB(-112, -548, 112, -520), paint(mix(coat, BLACK, 0.25)))
    c.drawLine(0, -520, 6, -300, paint(mix(coat, BLACK, 0.35), stroke=4))
    for side in (-1, 1):                                       # arms swinging a little
        k = sw * side
        c.drawPath(K.capsule(side * 104, -720, side * (126 + 8 * k), -470 + 14 * k, 60, 46), paint(mix(coat, BLACK, 0.1)))
        c.drawCircle(side * (128 + 8 * k), -450 + 14 * k, 20, paint((200, 160, 140)))
    c.drawPath(K.smooth([(-58, -760), (0, -790), (58, -760), (40, -730), (-40, -730)]), paint(mix(coat, BLACK, 0.2)))
    # the head from behind and the long hair
    c.drawPath(K.smooth([(-70, -830), (-62, -930), (0, -968), (62, -930), (70, -830), (84, -720), (64, -640), (0, -626), (-64, -640), (-84, -720)]),
               paint(hair))
    for k in range(9):
        xx = -60 + k * 15
        c.drawPath(K.bez_path([(xx * 0.6, -950), (xx * 1.1, -820), (xx * 1.2 + 6 * math.sin(T + k), -650)]), paint(mix(hair, WHITE, 0.2), 0.35, stroke=3))
    # light: a gel key from ahead (her back is in shadow), rims down both sides
    mp = skia.Paint()
    mp.setBlendMode(skia.BlendMode.kModulate)
    c.saveLayer(None, mp)
    c.drawPaint(paint((34, 28, 36)))
    for side, col in ((-1, key), (1, rim)):
        sh = K.lin((side * 160, 0), (side * 60, 0), [col + (1.0,), col + (0.0,)])
        p = paint(col, 1.0, shader=sh)
        p.setBlendMode(skia.BlendMode.kPlus)
        c.drawRect(skia.Rect.MakeLTRB(-200, -1000, 200, 20), p)
    c.restore()
    c.restore()
    c.restore()


def mannequin(c, x, y, s, T, pose=0, head=0.0, gown=True, cap=True, L=(255, 60, 170), R=(40, 220, 140), a=1.0, face_k=0.0,
              hand=None, crack=0.0):
    """A shop mannequin / a gowned graduate dummy: a smooth egg of a head (face_k > 0 paints doll features on it), jointed
    arms, on a stand. pose 0..3 changes the arms; head (-1..1) turns the head. (x, y) = feet; ~1000 px tall at s = 1."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    lp = paint()
    lp.setAlphaf(a)
    c.saveLayer(None, lp)
    pc = (232, 222, 214)
    c.drawRect(skia.Rect.MakeLTRB(-8, -260, 8, 0), paint((60, 50, 40)))
    c.drawOval(skia.Rect.MakeLTRB(-90, -14, 90, 14), paint((60, 50, 40)))
    body = K.smooth([(-120, -300), (-128, -560), (-110, -760), (-60, -800), (60, -800), (110, -760), (128, -560), (120, -300)])
    if gown:
        c.drawPath(K.smooth([(-150, -250), (-140, -600), (-112, -780), (-60, -810), (60, -810), (112, -780), (140, -600), (150, -250)]), paint((18, 16, 22)))
        c.drawPath(K.smooth([(-100, -790), (0, -700), (100, -790), (70, -640), (0, -600), (-70, -640)]), paint((150, 20, 40)))
    else:
        c.drawPath(body, paint(pc))
    arms = [((-110, -760), (-150, -560), (-120, -380)), ((-110, -760), (-60, -600), (20, -560)),
            ((-110, -760), (-170, -820), (-160, -980)), ((-110, -760), (-40, -700), (40, -760))][pose % 4]
    arms_r = [((110, -760), (150, -560), (120, -380)), ((110, -760), (160, -600), (180, -460)),
              ((110, -760), (150, -580), (110, -400)), ((110, -760), (190, -840), (200, -1000))][pose % 4]
    for sh_, el, wr in (arms, arms_r):
        col = (18, 16, 22) if gown else pc
        c.drawPath(K.capsule(sh_[0], sh_[1], el[0], el[1], 52, 44), paint(col))
        c.drawPath(K.capsule(el[0], el[1], wr[0], wr[1], 42, 34), paint(col))
        c.drawCircle(el[0], el[1], 22, paint(mix(pc, BLACK, 0.15)))
        c.drawCircle(wr[0], wr[1], 26, paint(pc))             # a smooth hand
    c.drawPath(K.smooth([(-40, -800), (40, -800), (34, -860), (-34, -860)]), paint(pc))
    c.save()
    c.translate(head * 18, -960)
    c.rotate(head * 10)
    c.drawOval(skia.Rect.MakeLTRB(-82, -110, 82, 110), paint(pc))
    if face_k > 0:                                             # a porcelain doll's face: glass eyes, painted lashes and lips
        fk, hx = face_k, head * 26
        if not cap:                                            # sculpted, painted hair: a 1970s bob
            c.drawPath(K.smooth([(-86, 10), (-88, -70), (-50, -112), (20, -118), (74, -92), (90, -30), (86, 14), (64, -40),
                                 (10, -74), (-50, -52), (-70, -10)]), paint((70, 38, 28), fk))
        for sd in (-1, 1):
            ex = sd * 32 + hx
            c.drawPath(K.bez_path([(ex - 22, -46), (ex, -58), (ex + 22, -48)]), paint((80, 54, 46), 0.85 * fk, stroke=3.5))
            eye = K.smooth([(ex - 24, -14), (ex - 8, -27), (ex + 10, -27), (ex + 24, -14), (ex + 8, -4), (ex - 8, -4)])
            c.drawPath(eye, paint((242, 242, 238), fk))
            c.save()
            c.clipPath(eye, doAntiAlias=True)
            c.drawCircle(ex + head * 5, -15, 11, paint((96, 150, 176), fk))
            c.drawCircle(ex + head * 5, -15, 11, paint((30, 60, 80), fk, stroke=2))
            c.drawCircle(ex + head * 5, -15, 5, paint((8, 8, 12), fk))
            c.drawPath(K.path([(ex - 24, -28), (ex + 24, -28), (ex + 24, -20), (ex - 24, -16)]), paint((160, 140, 150), 0.35 * fk))
            c.restore()
            c.drawCircle(ex + head * 5 - 4, -19, 3, paint(WHITE, fk))
            c.drawPath(K.bez_path([(ex - 24, -14), (ex, -30), (ex + 24, -14)]), paint((30, 20, 24), fk, stroke=3.5))
            for q in range(5):                                 # painted lashes
                lx = ex - 18 + q * 9
                c.drawLine(lx, -24 + abs(q - 2) * 2, lx + sd * 3, -33 + abs(q - 2) * 2, paint((30, 20, 24), fk, stroke=2))
            c.drawCircle(sd * 50 + hx, 26, 20, paint((236, 120, 130), 0.35 * fk, blur=9))
        c.drawPath(K.bez_path([(hx - 3, -2), (hx - 8, 24), (hx + 6, 28)]), paint((170, 140, 140), 0.6 * fk, stroke=3))
        c.drawPath(K.smooth([(hx - 20, 50), (hx - 7, 43), (hx, 47), (hx + 7, 43), (hx + 20, 50), (hx + 6, 58), (hx - 6, 58)]),
                   paint((178, 26, 48), fk))
        for sd in (-1, 1):                                     # the hinge lines of a jaw that opens
            c.drawLine(hx + sd * 24, 54, hx + sd * 28, 96, paint((110, 96, 100), 0.55 * fk, stroke=2))
        c.drawOval(skia.Rect.MakeLTRB(-50, -96, 6, -70), paint(WHITE, 0.25 * fk, blur=6))
    if cap:
        c.drawPath(K.path([(-120, -104), (0, -140), (120, -104), (0, -76)]), paint((20, 18, 24)))
        c.drawRect(skia.Rect.MakeLTRB(-60, -110, 60, -80), paint((20, 18, 24)))
    if crack > 0:
        c.drawPath(K.path([(-60, -60), (-20, -30), (-34, 10), (10, 30), (0, 70)], closed=False), paint((30, 24, 28), min(1, crack * 2), stroke=4))
    c.restore()
    mp = skia.Paint()
    mp.setBlendMode(skia.BlendMode.kModulate)
    c.saveLayer(None, mp)
    light_map(c, L, R, 0.5, (34, 30, 38), w=420, h=1200, oy=-500)
    c.restore()
    c.restore()
    c.restore()

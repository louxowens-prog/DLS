"""Painted faces, airbrushed like a 1980s fantasy paperback: soft-blurred shading laid over the skin, big luminous
eyes, full lips, hair in long painted strands - then lit by coloured light (an ember key from below, a violet fill,
a rim along one edge) through a multiply layer, so the shadows crush to black.

pface()      a face, front on, at (x, y) = between the eyes, scale s (face ~300 px wide at s = 1)
eye_macro()  one eye filling the frame: fibres in the iris, wet lids, lashes, the skin around it
mouth_macro() lips filling the frame, speaking"""
import math

import numpy as np
import skia

import gel as G
import kit as K
from kit import BLACK, WHITE, mix, paint

PEOPLE = {
    "merit": dict(skin=(236, 222, 236), lips=(118, 18, 64), iris=(240, 196, 110), hair=(34, 18, 46), brow=(40, 24, 50),
                  shadow=(120, 60, 160), lash=(12, 6, 16), hair_style="long", reel=True, liner=1.0, glow_iris=0.8),
    "iris": dict(skin=(226, 184, 158), lips=(160, 100, 96), iris=(96, 110, 72), hair=(72, 50, 38), brow=(80, 58, 44),
                 shadow=(140, 110, 104), lash=(46, 34, 28), hair_style="bob_grey", age=0.6, liner=0.3),
    "w_dark": dict(skin=(120, 78, 56), lips=(104, 52, 48), iris=(46, 30, 22), hair=(16, 10, 8), brow=(24, 14, 10),
                   shadow=(80, 54, 46), lash=(12, 8, 6), hair_style="coils", liner=0.4),
    "m_light": dict(skin=(230, 194, 174), lips=(172, 118, 110), iris=(76, 110, 150), hair=(116, 82, 54), brow=(100, 72, 50),
                    shadow=(150, 124, 116), lash=(80, 62, 50), hair_style="short", male=True, liner=0.0, age=0.25),
    "f_a": dict(skin=(196, 148, 118), lips=(146, 76, 76), iris=(60, 40, 30), hair=(28, 18, 14), brow=(36, 24, 18),
                shadow=(130, 96, 88), lash=(20, 14, 12), hair_style="pony", liner=0.4, age=0.3),
    "f_b": dict(skin=(238, 208, 188), lips=(168, 88, 94), iris=(90, 124, 150), hair=(196, 156, 96), brow=(150, 112, 72),
                shadow=(170, 140, 140), lash=(60, 44, 36), hair_style="bob", liner=0.3, age=0.65),
    "f_c": dict(skin=(150, 100, 74), lips=(118, 64, 58), iris=(50, 34, 24), hair=(22, 16, 14), brow=(28, 18, 14),
                shadow=(110, 78, 68), lash=(18, 12, 10), hair_style="bun", liner=0.5, age=0.1),
    "m_b": dict(skin=(170, 120, 92), lips=(140, 86, 78), iris=(50, 34, 24), hair=(30, 22, 18), brow=(30, 22, 18),
                shadow=(120, 90, 80), lash=(30, 22, 18), hair_style="short", male=True, liner=0.0, age=0.45),
}


def _blur_p(col, a, blur):
    return paint(col, a, blur=blur)


def outline():
    pts = [(0, -236), (88, -222), (136, -176), (152, -96), (151, -20), (146, 40), (132, 104), (106, 162), (64, 206), (0, 226)]
    full = pts + [(-x, y) for x, y in pts[-2:0:-1]]
    return K.smooth(full)


# ------------------------------------------------------------------ parts

def _eye(c, sd, P, T, blink=0.0, gaze=(0, 0), wide=0.0, scale=1.0):
    """An almond eye at (sd * 66, -10): a heavy upper lid, a luminous iris, lashes."""
    cx, cy = sd * 66, -10
    w, h = 96, 40 * (1 + 0.5 * wide)
    op = max(0.0, 1 - blink)
    c.save()
    c.translate(cx, cy)
    if sd < 0:
        c.scale(-1, 1)                                       # draw the right eye, mirror for the left
    # eyeshadow, smoked out toward the brow
    c.drawPath(K.smooth([(-52, 4), (-40, -34), (0, -50), (44, -40), (62, -6), (20, -14)]), _blur_p(P["shadow"], 0.75, 10))
    eye = skia.Path()
    eye.moveTo(-w / 2, 4)
    eye.cubicTo(-w * 0.3, -h * 1.05 * op + 2, w * 0.2, -h * 1.1 * op + 2, w / 2, -4)
    eye.cubicTo(w * 0.22, h * 0.55 * op, -w * 0.25, h * 0.58 * op + 4, -w / 2, 4)
    eye.close()
    if op > 0.04:
        c.drawPath(eye, paint(shader=K.lin((-w / 2, 0), (w / 2, 0), [(200, 170, 170), (246, 240, 236), (240, 232, 228), (196, 160, 160)],
                                          [0.0, 0.3, 0.7, 1.0])))
        c.save()
        c.clipPath(eye, doAntiAlias=True)
        gx, gy = gaze[0] * 14 * (1 if sd > 0 else -1), gaze[1] * 8
        ir = 23.0
        ic = P["iris"]
        if P.get("glow_iris"):
            c.drawCircle(gx, gy - 2, ir * 1.6, G.glow_paint(ic, 0.35 * P["glow_iris"], blur=10))
        c.drawCircle(gx, gy - 2, ir, paint(shader=K.rad((gx - 4, gy - 6), ir * 1.1, [mix(ic, WHITE, 0.35), ic, mix(ic, BLACK, 0.55)], [0, 0.55, 1])))
        rng = K.rng_at(sd + 5, 13)
        for k in range(28):                                   # fibres
            ang = k / 28 * 6.283 + rng.uniform(-0.08, 0.08)
            r0 = ir * rng.uniform(0.3, 0.45)
            c.drawLine(gx + math.cos(ang) * r0, gy - 2 + math.sin(ang) * r0, gx + math.cos(ang) * ir * 0.95, gy - 2 + math.sin(ang) * ir * 0.95,
                       paint(mix(ic, WHITE if k % 3 == 0 else BLACK, 0.4), 0.35, stroke=1.3))
        if P.get("reel"):                                     # the reel turning inside her iris
            for k in range(3):
                ang = T * 0.8 + k * 2.094
                c.drawCircle(gx + math.cos(ang) * ir * 0.58, gy - 2 + math.sin(ang) * ir * 0.58, ir * 0.2, paint((30, 14, 24), 0.8))
        c.drawCircle(gx, gy - 2, ir, paint(mix(ic, BLACK, 0.75), 0.9, stroke=3))
        c.drawCircle(gx, gy - 2, 8.5 + 3 * wide, paint((6, 4, 8)))
        c.drawPath(eye, paint(shader=K.lin((0, -h), (0, h * 0.25), [(30, 14, 20, 0.6), (30, 14, 20, 0.0)])))   # the lid's shadow
        c.drawCircle(gx - 7, gy - 10, 4.5, paint(WHITE, 0.95))
        c.drawCircle(gx + 8, gy + 5, 2.2, paint(WHITE, 0.6))
        c.restore()
        c.drawPath(K.bez_path([(-w / 2 + 6, 6), (0, h * 0.62 * op + 4), (w / 2 - 6, -2)]), paint((250, 210, 210), 0.45, stroke=2))  # wet rim
    # upper lid: liner, crease, lashes
    lid = skia.Path()
    lid.moveTo(-w / 2 - 2, 4)
    lid.cubicTo(-w * 0.3, -h * 1.08 * op, w * 0.2, -h * 1.14 * op, w / 2 + 6, -6)
    c.drawPath(lid, paint(P["lash"], 1.0, stroke=3 + 4 * P.get("liner", 0.5)))
    if P.get("liner", 0) > 0.6:
        c.drawPath(K.path([(w / 2, -4), (w / 2 + 24, -18), (w / 2 + 4, -12)]), paint(P["lash"], 0.95))
    crease = skia.Path()
    crease.moveTo(-w / 2 + 6, -h * 0.9 * op - 8)
    crease.cubicTo(-w * 0.2, -h * 1.5 - 12, w * 0.24, -h * 1.5 - 12, w / 2 - 2, -h * 0.9 - 8)
    c.drawPath(crease, paint(mix(P["shadow"], BLACK, 0.5), 0.6, stroke=3, blur=2))
    if not P.get("male"):
        for k in range(16):
            u = (k + 0.5) / 16
            x = -w / 2 + w * u
            t = u
            y = -h * op * (1.0 * math.sin(math.pi * min(1.0, t * 1.04))) + 2 - 4 * t
            L = (8 + 16 * u) * (1.0 if P.get("liner", 0) > 0.6 else 0.7)
            q = skia.Path()
            q.moveTo(x, y)
            q.quadTo(x + 4 + 10 * u, y - L, x + 10 + 14 * u, y - L * 0.8)
            c.drawPath(q, paint(P["lash"], 0.9, stroke=2.4))
    if op <= 0.04:
        c.drawPath(K.bez_path([(-w / 2, 4), (0, 12), (w / 2, -4)]), paint(P["lash"], 1.0, stroke=4))
    c.restore()


def _brow(c, sd, P, lift=0.0, knit=0.0):
    c.save()
    c.scale(sd, 1)
    p = skia.Path()
    p.moveTo(24, -64 + 8 * knit)
    p.cubicTo(50, -86 - 10 * lift, 92, -94 - 14 * lift, 122, -70 - 6 * lift)
    c.drawPath(p, paint(P["brow"], 0.9, stroke=12 if P.get("male") else 7, blur=1.0))
    c.restore()


def _nose(c, P):
    sk = P["skin"]
    dk = mix(sk, BLACK, 0.5)
    for sd in (-1, 1):
        c.drawPath(K.bez_path([(sd * 14, -36), (sd * 20, 20), (sd * 28, 66)]), _blur_p(dk, 0.32, 7))
        c.drawPath(K.bez_path([(sd * 30, 64), (sd * 36, 82), (sd * 14, 86)]), paint(mix(sk, BLACK, 0.45), 0.7, stroke=3))
        c.drawOval(skia.Rect.MakeXYWH(sd * 16 - 8, 78, 16, 8), paint(mix(sk, BLACK, 0.7), 0.8))
    c.drawPath(K.smooth([(-7, -40), (7, -40), (9, 56), (0, 70), (-9, 56)]), _blur_p(mix(sk, WHITE, 0.45), 0.5, 5))
    c.drawCircle(0, 66, 10, _blur_p(mix(sk, WHITE, 0.6), 0.5, 4))


def _mouth(c, P, talk=0.0, smile=0.0, open_=0.0):
    o = min(1.0, open_ + 0.6 * talk)
    lips = P["lips"]
    w = 54 + 6 * smile
    cy = 134
    corner = -6 * smile
    gap = o * 30
    up = skia.Path()
    up.moveTo(-w, cy + corner)
    up.cubicTo(-w * 0.62, cy - 16, -w * 0.28, cy - 24, 0, cy - 12)
    up.cubicTo(w * 0.28, cy - 24, w * 0.62, cy - 16, w, cy + corner)
    up.cubicTo(w * 0.5, cy + 3 + o * 4, -w * 0.5, cy + 3 + o * 4, -w, cy + corner)
    up.close()
    lo = skia.Path()
    lo.moveTo(-w + 3, cy + corner + gap * 0.25)
    lo.cubicTo(-w * 0.5, cy + 6 + gap, w * 0.5, cy + 6 + gap, w - 3, cy + corner + gap * 0.25)
    lo.cubicTo(w * 0.6, cy + 34 + gap, -w * 0.6, cy + 34 + gap, -w + 3, cy + corner + gap * 0.25)
    lo.close()
    if o > 0.03:
        inner = K.smooth([(-w * 0.85, cy + corner * 0.5), (0, cy + 2), (w * 0.85, cy + corner * 0.5), (w * 0.45, cy + gap + 6), (-w * 0.45, cy + gap + 6)])
        c.drawPath(inner, paint((34, 8, 14)))
        if o > 0.2:
            c.drawRect(skia.Rect.MakeLTRB(-w * 0.48, cy + 1, w * 0.48, cy + 8), paint((232, 226, 216), 0.9))
    c.drawPath(up, paint(shader=K.lin((0, cy - 24), (0, cy + 4), [mix(lips, BLACK, 0.15), lips])))
    c.drawPath(lo, paint(shader=K.lin((0, cy + gap), (0, cy + 34 + gap), [mix(lips, WHITE, 0.08), mix(lips, BLACK, 0.25)])))
    c.drawOval(skia.Rect.MakeXYWH(-20, cy + 10 + gap, 30, 8), _blur_p(WHITE, 0.45, 3))
    c.drawOval(skia.Rect.MakeXYWH(-30, cy - 18, 20, 5), _blur_p(WHITE, 0.25, 2))
    c.drawPath(K.bez_path([(-w, cy + corner), (0, cy + 4 + gap * 0.4), (w, cy + corner)]), paint(mix(lips, BLACK, 0.6), 0.6, stroke=2.2))
    c.drawOval(skia.Rect.MakeXYWH(-30, cy + 40 + gap, 60, 14), _blur_p(mix(P["skin"], BLACK, 0.5), 0.35, 8))       # under the lip


def _shade(c, P, age=0.0):
    """The airbrushed modelling laid over the skin."""
    sk = P["skin"]
    dk, hi = mix(sk, BLACK, 0.55), mix(sk, WHITE, 0.45)
    c.save()
    c.clipPath(outline(), doAntiAlias=True)
    c.drawPath(outline(), paint(shader=K.rad((0, -20), 260, [dk + (0.0,), dk + (0.0,), dk + (0.7,)], [0, 0.6, 1.0])))
    for sd in (-1, 1):
        c.drawOval(skia.Rect.MakeXYWH(sd * 66 - 72, -66, 144, 92), _blur_p(dk, 0.42, 20))            # sockets
        c.drawPath(K.smooth([(sd * 154, 30), (sd * 110, 60), (sd * 70, 116), (sd * 104, 130), (sd * 150, 96)]), _blur_p(dk, 0.42, 18))
        c.drawOval(skia.Rect.MakeXYWH(sd * 142 - 26, -130, 52, 120), _blur_p(dk, 0.35, 20))          # temples
        c.drawOval(skia.Rect.MakeXYWH(sd * 98 - 40, 4, 80, 46), _blur_p(hi, 0.38, 16))               # cheekbones
    c.drawOval(skia.Rect.MakeLTRB(-76, -212, 76, -100), _blur_p(hi, 0.36, 28))
    c.drawCircle(0, 204, 24, _blur_p(hi, 0.3, 12))
    c.drawOval(skia.Rect.MakeLTRB(-36, 170, 36, 192), _blur_p(dk, 0.3, 8))
    if age > 0.3:
        for sd in (-1, 1):
            for j in range(3):
                c.drawPath(K.bez_path([(sd * 116, -20 + j * 12), (sd * 130, -16 + j * 14), (sd * 142, -24 + j * 20)]), paint(dk, 0.35 * age, stroke=2))
            c.drawPath(K.bez_path([(sd * 40, 80), (sd * 68, 112), (sd * 66, 156)]), paint(dk, 0.45 * age, stroke=3, blur=2))
            c.drawPath(K.bez_path([(sd * 40, 26), (sd * 66, 36), (sd * 96, 28)]), paint(dk, 0.3 * age, stroke=2.5, blur=1.5))   # under-eye
        for j in range(2):
            c.drawPath(K.bez_path([(-66, -128 - j * 20), (0, -136 - j * 20), (66, -128 - j * 20)]), paint(dk, 0.2 * age, stroke=2.2))
    c.restore()


# ------------------------------------------------------------------ hair

def _hair_back(c, P, T):
    st, hc = P["hair_style"], P["hair"]
    if st == "long":
        c.drawPath(K.smooth([(-160, -190), (0, -278), (160, -190), (206, 40), (226, 420), (190, 640), (90, 660), (70, 240), (-70, 240),
                             (-90, 660), (-190, 640), (-226, 420), (-206, 40)]), paint(hc))
    elif st in ("bob", "bob_grey"):
        c.drawPath(K.smooth([(-166, -170), (0, -268), (166, -170), (190, 40), (184, 230), (130, 268), (100, 190), (-100, 190), (-130, 268),
                             (-184, 230), (-190, 40)]), paint(hc))
    elif st == "coils":
        rng = K.rng_at(5, 5)
        for k in range(52):
            ang = k / 52 * 6.283
            r = rng.uniform(196, 244)
            c.drawCircle(math.cos(ang) * r, -70 + math.sin(ang) * r * 0.95, rng.uniform(46, 72), paint(mix(hc, WHITE, rng.uniform(0, 0.1))))
        c.drawCircle(0, -70, 216, paint(hc))
    elif st == "short":
        c.drawPath(K.smooth([(-154, -150), (0, -262), (154, -150), (158, -40), (-158, -40)]), paint(hc))
    elif st == "pony":
        c.drawPath(K.smooth([(-154, -170), (0, -262), (154, -170), (156, 10), (-156, 10)]), paint(hc))
    elif st == "bun":
        c.drawCircle(0, -250, 80, paint(hc))
        c.drawPath(K.smooth([(-156, -150), (0, -256), (156, -150), (154, 0), (-154, 0)]), paint(hc))


def _hair_front(c, P, T):
    st, hc = P["hair_style"], P["hair"]
    hi, dk = mix(hc, WHITE, 0.35), mix(hc, BLACK, 0.4)
    if st == "long":                                          # a centre parting, long painted strands
        for sd in (-1, 1):
            c.drawPath(K.smooth([(sd * 4, -236), (sd * 90, -230), (sd * 160, -170), (sd * 190, -40), (sd * 196, 120), (sd * 186, 320),
                                 (sd * 160, 520), (sd * 140, 330), (sd * 146, 120), (sd * 136, -50), (sd * 100, -160), (sd * 34, -206)]), paint(hc))
            for k in range(12):
                o = k * 5
                q = K.bez_path([(sd * (12 + o), -230 + k), (sd * (150 + o * 0.5), -150 + k * 12), (sd * (170 + k * 2 + 6 * math.sin(T * 0.7 + k)), 300 + k * 18)])
                c.drawPath(q, paint(hi if k % 3 == 0 else dk, 0.3, stroke=2 + (k % 3)))
    elif st in ("bob", "bob_grey"):
        c.drawPath(K.smooth([(-168, -140), (-60, -240), (60, -244), (156, -176), (182, -40), (176, 120), (156, 236), (140, 120), (128, -40),
                             (44, -176), (-60, -176), (-132, -60), (-146, 120), (-160, 236), (-180, 120), (-180, -40)]), paint(hc))
        if st == "bob_grey":
            c.drawPath(K.smooth([(-60, -238), (-22, -242), (-74, -166), (-124, -40), (-144, 100), (-154, 60), (-134, -60), (-104, -164)]),
                       paint(mix(hc, (212, 208, 204), 0.78)))
        for k in range(7):
            c.drawPath(K.bez_path([(-50 + k * 28, -234), (60 + k * 12, -184), (136 + k * 4, -50)]), paint(hi, 0.3, stroke=2.5))
    elif st == "coils":
        rng = K.rng_at(6, 6)
        for k in range(20):
            ang = math.pi + k / 19 * math.pi
            c.drawCircle(math.cos(ang) * 156, -160 + math.sin(ang) * 92, rng.uniform(30, 46), paint(mix(hc, WHITE, 0.06)))
    elif st == "short":
        c.drawPath(K.smooth([(-156, -110), (-124, -214), (0, -254), (124, -218), (158, -110), (144, -150), (60, -200), (-60, -194), (-144, -150)]), paint(hc))
        for k in range(9):
            c.drawPath(K.bez_path([(-120 + k * 30, -226), (-90 + k * 30, -204), (-70 + k * 32, -176)]), paint(hi, 0.35, stroke=3))
    elif st == "pony":
        c.drawPath(K.smooth([(-156, -150), (0, -246), (156, -150), (146, -96), (0, -198), (-146, -96)]), paint(hc))
    elif st == "bun":
        for sd in (-1, 1):
            c.drawPath(K.smooth([(sd * 2, -228), (sd * 90, -214), (sd * 146, -160), (sd * 156, -80), (sd * 144, -50), (sd * 124, -140), (sd * 62, -196)]), paint(hc))


def _neck(c, P, T):
    sk = P["skin"]
    c.drawPath(K.smooth([(-64, 150), (64, 150), (76, 340), (-76, 340)]), paint(mix(sk, BLACK, 0.1)))
    c.drawPath(K.smooth([(-74, 200), (74, 200), (60, 280), (-60, 280)]), _blur_p(mix(sk, BLACK, 0.55), 0.55, 18))
    c.drawPath(K.smooth([(-330, 700), (-310, 420), (-180, 330), (-76, 316), (76, 316), (180, 330), (310, 420), (330, 700)]), paint(mix(sk, BLACK, 0.05)))
    if P.get("male"):
        col = (190, 196, 210)
    elif P["hair_style"] == "long":
        col = (30, 16, 40)
    else:
        col = (70, 66, 80)
    c.drawPath(K.smooth([(-340, 720), (-320, 440), (-200, 360), (-90, 350), (0, 420), (90, 350), (200, 360), (320, 440), (340, 720)]), paint(col))


# ------------------------------------------------------------------ the face

def pface(c, x, y, s, who, T, key=(255, 120, 50), fill=(120, 70, 255), rim=None, key_at=(-0.5, 0.9), fill_at=(0.7, -0.7),
          amb=(18, 10, 22), blink=0.0, gaze=(0.0, 0.0), talk=0.0, smile=0.0, wide=0.0, fear=0.0, open_=0.0, tilt=0.0,
          neck=True, a=1.0, hair=True, key_k=1.0, flat=0.0):
    """A face lit like an ember: key light from key_at (fractions of the face box, (-1..1)), a coloured fill from
    fill_at, an optional rim along the edge, and almost nothing elsewhere."""
    P = PEOPLE[who]
    c.save()
    c.translate(x, y)
    c.rotate(tilt)
    c.scale(s, s)
    lp = paint()
    lp.setAlphaf(a)
    c.saveLayer(None, lp)
    if hair:
        _hair_back(c, P, T)
    if neck:
        _neck(c, P, T)
    c.drawPath(outline(), paint(P["skin"]))
    _shade(c, P, P.get("age", 0.0))
    _nose(c, P)
    for sd in (-1, 1):
        _brow(c, sd, P, lift=fear * 1.0 + wide * 0.4, knit=fear)
        _eye(c, sd, P, T, blink=blink, gaze=gaze, wide=max(wide, fear * 0.8))
    _mouth(c, P, talk=talk, smile=smile - 0.6 * fear, open_=max(open_, fear * 0.6))
    if hair:
        _hair_front(c, P, T)
    # --- the light, multiplied in
    mp = skia.Paint()
    mp.setBlendMode(skia.BlendMode.kModulate)
    c.saveLayer(None, mp)
    c.drawPaint(paint(mix(amb, (255, 255, 255), flat)))
    kp = paint(shader=K.rad((key_at[0] * 300, key_at[1] * 300), 620, [key + (key_k,), key + (0.55 * key_k,), key + (0.0,)], [0.0, 0.45, 1.0]))
    kp.setBlendMode(skia.BlendMode.kPlus)
    c.drawRect(skia.Rect.MakeLTRB(-700, -800, 700, 900), kp)
    fp = paint(shader=K.rad((fill_at[0] * 300, fill_at[1] * 300), 520, [fill + (0.75,), fill + (0.0,)]))
    fp.setBlendMode(skia.BlendMode.kPlus)
    c.drawRect(skia.Rect.MakeLTRB(-700, -800, 700, 900), fp)
    c.restore()
    # --- a rim of light catching one edge
    if rim is not None:
        c.save()
        c.clipPath(outline(), doAntiAlias=True)
        c.drawPath(outline(), _rim_paint(rim))
        c.restore()
    c.restore()
    c.restore()


def _rim_paint(col):
    p = paint(col, 0.6, stroke=14, blur=8)
    p.setBlendMode(skia.BlendMode.kPlus)
    return p


# ------------------------------------------------------------------ macro close-ups

def _taper(c, pts, w0, w1, col, a=1.0):
    """A tapered stroke along a polyline (a lash, a hair): w0 wide at the root, w1 at the tip."""
    pts = np.asarray(pts, float)
    n = len(pts)
    left, right = [], []
    for i in range(n):
        p0, p1 = pts[max(0, i - 1)], pts[min(n - 1, i + 1)]
        d = p1 - p0
        L = math.hypot(*d) + 1e-6
        nx, ny = -d[1] / L, d[0] / L
        w = (w0 + (w1 - w0) * i / (n - 1)) / 2
        left.append((pts[i][0] + nx * w, pts[i][1] + ny * w))
        right.append((pts[i][0] - nx * w, pts[i][1] - ny * w))
    c.drawPath(K.path(left + right[::-1]), paint(col, a))


def eye_macro(c, x, y, s, who, T, blink=0.0, gaze=(0.0, 0.0), key=(255, 120, 50), fill=(120, 70, 255), wide=0.0,
              reflection=None, a=1.0, pupil=1.0, tear=0.0):
    """One eye filling the frame at (x, y), s = 1 -> about 900 px across. reflection(c, r) draws whatever the eye sees,
    clipped into the iris and bent across the cornea."""
    P = PEOPLE[who]
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    lp = paint()
    lp.setAlphaf(a)
    c.saveLayer(None, lp)
    sk = P["skin"]
    c.drawRect(skia.Rect.MakeLTRB(-1000, -1000, 1000, 1000), paint(sk))
    rng = K.rng_at(77, 2)
    for i in range(420):                                       # skin texture: pores and fine creases
        px, py = rng.uniform(-1000, 1000), rng.uniform(-1000, 1000)
        c.drawCircle(px, py, rng.uniform(1.2, 3.5), paint(mix(sk, BLACK, 0.35), 0.16))
    for i in range(12):                                        # fine lines at the outer corner
        yy = rng.uniform(-60, 120)
        c.drawPath(K.bez_path([(520, yy), (620, yy - 20 + rng.uniform(-10, 10)), (760, yy - 40 + rng.uniform(-30, 30))]), paint(mix(sk, BLACK, 0.4), 0.2, stroke=3))
    c.drawOval(skia.Rect.MakeLTRB(-620, -420, 620, 360), _blur_p(mix(sk, BLACK, 0.55), 0.6, 100))             # the socket
    c.drawOval(skia.Rect.MakeLTRB(-520, -600, 560, -250), _blur_p(P["shadow"], 0.85, 80))                      # eyeshadow
    c.drawOval(skia.Rect.MakeLTRB(-300, 320, 460, 560), _blur_p(mix(sk, WHITE, 0.45), 0.4, 70))                # the cheek
    c.drawOval(skia.Rect.MakeLTRB(-700, -980, 500, -700), _blur_p(mix(sk, WHITE, 0.35), 0.3, 80))              # the brow bone
    rb = K.rng_at(5, 8)
    for i in range(70):                                        # the eyebrow, hair by hair, at the top of frame
        u = i / 69
        bx = -650 + 1250 * u
        by = -900 - 120 * math.sin(math.pi * min(1.0, u * 1.1)) + rb.uniform(-20, 20)
        _taper(c, [(bx, by + 40), (bx + 40 + 30 * u, by), (bx + 90 + 40 * u, by - 20)], 7, 1, P["brow"], 0.7)
    op = max(0.0, 1 - blink)
    w, h = 840, 330 * (1 + 0.35 * wide)
    eye = skia.Path()
    eye.moveTo(-w / 2, 40)
    eye.cubicTo(-w * 0.3, -h * 1.05 * op + 20, w * 0.2, -h * 1.1 * op + 20, w / 2, -30)
    eye.cubicTo(w * 0.22, h * 0.55 * op, -w * 0.25, h * 0.58 * op + 30, -w / 2, 40)
    eye.close()
    # the lid above the eye: a thick fold of skin with a crease
    c.drawPath(K.bez_path([(-w / 2 + 40, -h * 1.15 - 30), (0, -h * 1.55 - 80), (w / 2, -h * 1.1 - 60)]), _blur_p(mix(P["shadow"], BLACK, 0.55), 0.75, 18))
    if op > 0.03:
        c.drawPath(eye, paint(shader=K.lin((-w / 2, 0), (w / 2, 0), [(196, 130, 130), (244, 236, 230), (236, 226, 220), (190, 126, 126)], [0, 0.3, 0.7, 1])))
        c.save()
        c.clipPath(eye, doAntiAlias=True)
        for i in range(12):                                    # fine red veins toward the corners
            sd = -1 if i % 2 else 1
            pts = [(sd * w * 0.49, rng.uniform(-40, 40)), (sd * w * rng.uniform(0.3, 0.4), rng.uniform(-60, 60)), (sd * w * rng.uniform(0.2, 0.28), rng.uniform(-80, 80))]
            c.drawPath(K.bez_path(pts), paint((190, 60, 70), 0.28, stroke=2))
        gx, gy = gaze[0] * 110, gaze[1] * 60
        ir = 205.0
        ic = P["iris"]
        if P.get("glow_iris"):
            c.drawCircle(gx, gy, ir * 1.35, G.glow_paint(ic, 0.28, blur=60))
        c.drawCircle(gx, gy, ir, paint(shader=K.rad((gx - 30, gy - 40), ir * 1.1, [mix(ic, WHITE, 0.45), ic, mix(ic, BLACK, 0.65)], [0, 0.5, 1])))
        r2 = K.rng_at(91, 1)
        for k in range(260):                                   # fibres, crypts and furrows
            ang = k / 260 * 6.283 + r2.uniform(-0.02, 0.02)
            r0 = ir * r2.uniform(0.3, 0.42)
            r1 = ir * r2.uniform(0.7, 0.97)
            col = mix(ic, WHITE if k % 4 == 0 else BLACK, r2.uniform(0.25, 0.65))
            pts = [(gx + math.cos(ang) * r0, gy + math.sin(ang) * r0),
                   (gx + math.cos(ang + 0.05) * (r0 + r1) / 2, gy + math.sin(ang + 0.05) * (r0 + r1) / 2),
                   (gx + math.cos(ang) * r1, gy + math.sin(ang) * r1)]
            c.drawPath(K.bez_path(pts), paint(col, 0.42, stroke=r2.uniform(2, 5)))
        for k in range(5):                                     # furrows: rings like wound tape
            c.drawCircle(gx, gy, ir * (0.6 + 0.07 * k), paint(mix(ic, BLACK, 0.5), 0.22, stroke=3))
        c.drawCircle(gx, gy, ir * 0.5, paint(mix(ic, WHITE, 0.35), 0.4, stroke=7))      # the collarette
        if P.get("reel"):                                      # three dark windows of a reel, turning very slowly
            for k in range(3):
                ang = T * 0.5 + k * 2.094
                c.save()
                c.translate(gx, gy)
                c.rotate(math.degrees(ang))
                c.drawPath(K.smooth([(ir * 0.46, -ir * 0.12), (ir * 0.68, -ir * 0.2), (ir * 0.68, ir * 0.2), (ir * 0.46, ir * 0.12)]), paint((40, 16, 26), 0.55))
                c.restore()
        pr = ir * (0.28 + 0.12 * pupil)
        c.drawCircle(gx, gy, pr * 1.08, paint((40, 20, 20), 0.6))
        c.drawCircle(gx, gy, pr, paint((3, 2, 4)))
        if reflection is not None:                             # what the eye sees, bent across the cornea
            c.save()
            c.clipPath(K.circle(gx, gy, ir * 0.98), doAntiAlias=True)
            c.translate(gx, gy)
            reflection(c, ir)
            c.restore()
        c.drawCircle(gx, gy, ir, paint(mix(ic, BLACK, 0.85), 0.92, stroke=18))           # the limbal ring
        c.drawPath(eye, paint(shader=K.lin((0, -h), (0, h * 0.35), [(30, 12, 20, 0.75), (30, 12, 20, 0.0)])))   # the lid's shadow
        c.drawPath(K.smooth([(gx - 150, gy - 120), (gx - 60, gy - 150), (gx - 40, gy - 110), (gx - 130, gy - 80)]), paint(WHITE, 0.85, blur=2))  # window
        c.drawCircle(gx + 90, gy + 70, 16, paint(WHITE, 0.55, blur=2))
        if tear > 0:
            c.drawPath(K.bez_path([(-w * 0.45, 60), (0, h * 0.55 + 20), (w * 0.45, 0)]), paint((255, 255, 255), 0.5 * tear, stroke=12, blur=2))
        c.restore()
        c.drawPath(K.bez_path([(-w / 2 + 40, 50), (0, h * 0.58 * op + 30), (w / 2 - 40, -20)]), paint((240, 180, 180), 0.7, stroke=12))  # waterline
        c.drawPath(K.bez_path([(-w / 2 + 40, 58), (0, h * 0.58 * op + 40), (w / 2 - 40, -12)]), paint((255, 255, 255), 0.35, stroke=3))
    # the upper lid's edge, liner, lashes
    lid = skia.Path()
    lid.moveTo(-w / 2 - 10, 40)
    lid.cubicTo(-w * 0.3, -h * 1.08 * op + 10, w * 0.2, -h * 1.14 * op + 10, w / 2 + 40, -50)
    c.drawPath(lid, paint(P["lash"], 1.0, stroke=18 + 30 * P.get("liner", 0.5)))
    if not P.get("male"):
        r3 = K.rng_at(17, 3)
        for k in range(70):
            u = (k + 0.5) / 70
            xx = -w / 2 + w * u
            yy = -h * op * math.sin(math.pi * min(1.0, u * 1.03)) + 30 - 60 * u + 6
            L = (70 + 170 * u) * r3.uniform(0.75, 1.1) * (0.6 + 0.4 * op)
            bend = 0.25 + 0.5 * u
            pts = [(xx, yy), (xx + L * bend * 0.4, yy - L * 0.55), (xx + L * bend, yy - L * 0.85), (xx + L * (bend + 0.25), yy - L * 0.92)]
            _taper(c, pts, r3.uniform(6, 9), 1.0, P["lash"], 0.95)
        for k in range(26):                                    # the lower lashes, short and sparse
            u = (k + 0.5) / 26
            xx = -w / 2 + 90 + (w - 180) * u
            yy = h * 0.55 * op * math.sin(math.pi * u) + 42 - 50 * u
            _taper(c, [(xx, yy), (xx + 4 + 14 * u, yy + 30), (xx + 10 + 24 * u, yy + 52 + 20 * u)], 4, 1, P["lash"], 0.7)
    if op <= 0.03:
        c.drawPath(K.bez_path([(-w / 2, 40), (0, 90), (w / 2, -30)]), paint(P["lash"], 1.0, stroke=22))
    # light
    mp = skia.Paint()
    mp.setBlendMode(skia.BlendMode.kModulate)
    c.saveLayer(None, mp)
    c.drawPaint(paint((20, 12, 24)))
    kp = paint(shader=K.rad((-300, 700), 1500, [key + (1.0,), key + (0.5,), key + (0.0,)], [0, 0.5, 1]))
    kp.setBlendMode(skia.BlendMode.kPlus)
    c.drawRect(skia.Rect.MakeLTRB(-1100, -1100, 1100, 1100), kp)
    fp = paint(shader=K.rad((500, -600), 1200, [fill + (0.8,), fill + (0.0,)]))
    fp.setBlendMode(skia.BlendMode.kPlus)
    c.drawRect(skia.Rect.MakeLTRB(-1100, -1100, 1100, 1100), fp)
    c.restore()
    c.restore()
    c.restore()


def mouth_macro(c, x, y, s, who, T, talk=0.0, smile=0.0, open_=0.0, key=(255, 120, 50), fill=(120, 70, 255), a=1.0):
    """Lips filling the frame at (x, y); s = 1 -> the mouth about 800 px wide. Painted at full size: glossed,
    lined, the teeth and the dark of the mouth behind them as it speaks."""
    P = PEOPLE[who]
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    lp = paint()
    lp.setAlphaf(a)
    c.saveLayer(None, lp)
    sk, lips = P["skin"], P["lips"]
    c.drawRect(skia.Rect.MakeLTRB(-1000, -1000, 1000, 1000), paint(sk))
    rng = K.rng_at(33, 4)
    for i in range(380):
        c.drawCircle(rng.uniform(-1000, 1000), rng.uniform(-1000, 1000), rng.uniform(1.2, 3.2), paint(mix(sk, BLACK, 0.35), 0.15))
    # the face around the mouth: the philtrum, the folds from nose to mouth, the chin
    c.drawPath(K.smooth([(-70, -560), (70, -560), (60, -170), (-60, -170)]), _blur_p(mix(sk, WHITE, 0.35), 0.35, 30))
    for sd in (-1, 1):
        c.drawPath(K.bez_path([(sd * 60, -560), (sd * 50, -380), (sd * 70, -200)]), _blur_p(mix(sk, BLACK, 0.4), 0.45, 18))
        c.drawPath(K.bez_path([(sd * 280, -520), (sd * 520, -140), (sd * 560, 260)]), paint(mix(sk, BLACK, 0.45), 0.45, stroke=24, blur=26))
    c.drawOval(skia.Rect.MakeLTRB(-280, 330, 280, 800), _blur_p(mix(sk, WHITE, 0.3), 0.35, 80))
    for sd in (-1, 1):                                         # the base of the nose at the top of the frame
        c.drawOval(skia.Rect.MakeLTRB(sd * 150 - 70, -760, sd * 150 + 70, -690), paint(mix(sk, BLACK, 0.7), 0.85, blur=6))
        c.drawPath(K.bez_path([(sd * 250, -780), (sd * 270, -680), (sd * 120, -660)]), paint(mix(sk, BLACK, 0.45), 0.5, stroke=14, blur=8))
    c.drawOval(skia.Rect.MakeLTRB(-120, -800, 120, -700), _blur_p(mix(sk, WHITE, 0.4), 0.35, 20))
    c.drawPath(K.bez_path([(-60, 760), (0, 700), (60, 760)]), paint(mix(sk, BLACK, 0.4), 0.35, stroke=10, blur=10))   # the chin
    c.drawOval(skia.Rect.MakeLTRB(-260, 220, 260, 330), _blur_p(mix(sk, BLACK, 0.55), 0.55, 40))               # under the lower lip
    o = min(1.0, open_ + 0.75 * talk)
    W_ = 440 + 30 * smile
    corner = -40 * smile
    gap = o * 210
    up = skia.Path()
    up.moveTo(-W_, corner)
    up.cubicTo(-W_ * 0.62, -120, -W_ * 0.3, -190, 0, -110)
    up.cubicTo(W_ * 0.3, -190, W_ * 0.62, -120, W_, corner)
    up.cubicTo(W_ * 0.5, 30 + gap * 0.1, -W_ * 0.5, 30 + gap * 0.1, -W_, corner)
    up.close()
    lo = skia.Path()
    lo.moveTo(-W_ + 20, corner + gap * 0.25)
    lo.cubicTo(-W_ * 0.5, 50 + gap, W_ * 0.5, 50 + gap, W_ - 20, corner + gap * 0.25)
    lo.cubicTo(W_ * 0.62, 250 + gap, -W_ * 0.62, 250 + gap, -W_ + 20, corner + gap * 0.25)
    lo.close()
    if o > 0.02:
        inner = K.smooth([(-W_ * 0.86, corner * 0.6), (0, 10), (W_ * 0.86, corner * 0.6), (W_ * 0.45, gap + 40), (-W_ * 0.45, gap + 40)])
        c.drawPath(inner, paint(shader=K.rad((0, gap * 0.5), W_ * 0.7, [(70, 14, 24), (20, 4, 8)])))
        if o > 0.15:                                           # the upper teeth: one row, the gaps just shadows
            c.save()
            c.clipPath(inner, doAntiAlias=True)
            c.drawOval(skia.Rect.MakeLTRB(-W_ * 0.5, gap * 0.6, W_ * 0.5, gap + 120), paint((150, 50, 60), 0.8))       # the tongue
            row = K.smooth([(-W_ * 0.7, -10), (W_ * 0.7, -10), (W_ * 0.6, 40 + gap * 0.25), (0, 70 + gap * 0.3), (-W_ * 0.6, 40 + gap * 0.25)])
            c.drawPath(row, paint(shader=K.lin((0, -10), (0, 80 + gap * 0.3), [(236, 228, 214), (196, 184, 170)])))
            for k in range(-3, 4):
                tx = k * 74 + 37
                c.drawLine(tx, -10, tx * 0.96, 50 + gap * 0.25 - abs(k) * 6, paint((140, 120, 110), 0.45, stroke=3, blur=1))
            c.drawPath(row, paint((40, 10, 16), 0.35, stroke=10, blur=8))
            c.restore()
    c.drawPath(up, paint(shader=K.lin((0, -190), (0, 30), [mix(lips, BLACK, 0.3), lips])))
    c.drawPath(lo, paint(shader=K.lin((0, gap), (0, 250 + gap), [mix(lips, WHITE, 0.1), mix(lips, BLACK, 0.3)])))
    r2 = K.rng_at(8, 8)
    for lp_, (y0, y1) in ((lo, (60 + gap, 230 + gap)), (up, (-170, 10))):      # the fine vertical lines of the lips
        c.save()
        c.clipPath(lp_, doAntiAlias=True)
        for i in range(60):
            xx = r2.uniform(-W_ * 0.9, W_ * 0.9)
            yy = r2.uniform(y0, y1)
            c.drawLine(xx, yy - 40, xx + r2.uniform(-6, 6), yy + 10, paint(mix(lips, BLACK, 0.45), 0.35, stroke=2.5))
        c.restore()
    c.drawPath(K.bez_path([(-W_ * 0.6, -110), (0, -150), (W_ * 0.6, -110)]), paint(mix(lips, WHITE, 0.4), 0.35, stroke=6, blur=4))    # the vermilion edge
    c.drawOval(skia.Rect.MakeLTRB(-150, 110 + gap, 90, 170 + gap), _blur_p(WHITE, 0.6, 14))                    # gloss
    c.drawOval(skia.Rect.MakeLTRB(-70, 126 + gap, 10, 146 + gap), _blur_p(WHITE, 0.8, 4))
    c.drawPath(K.bez_path([(-W_, corner), (0, 30 + gap * 0.4), (W_, corner)]), paint(mix(lips, BLACK, 0.7), 0.7, stroke=10))
    mp = skia.Paint()
    mp.setBlendMode(skia.BlendMode.kModulate)
    c.saveLayer(None, mp)
    c.drawPaint(paint((20, 12, 24)))
    kp = paint(shader=K.rad((-300, 900), 1500, [key + (1.0,), key + (0.5,), key + (0.0,)], [0, 0.5, 1]))
    kp.setBlendMode(skia.BlendMode.kPlus)
    c.drawRect(skia.Rect.MakeLTRB(-1100, -1100, 1100, 1100), kp)
    fp = paint(shader=K.rad((600, -500), 1200, [fill + (0.8,), fill + (0.0,)]))
    fp.setBlendMode(skia.BlendMode.kPlus)
    c.drawRect(skia.Rect.MakeLTRB(-1100, -1100, 1100, 1100), fp)
    c.restore()
    c.restore()
    c.restore()

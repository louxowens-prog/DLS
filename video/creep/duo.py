"""Zuza and Lili, the two bored young women (all original): jointed like dolls, in 1960s mod mini dresses and daisy
crowns, with big painted-lash eyes.

  Zuza   a sleek black bob with a heavy fringe; a black shift with a white collar and cuffs; white tights; deadpan
  Lili   a pale-gold beehive with a powder-blue band and flipped ends; a white shift with tomato polka dots and
         puff sleeves; rose tights; delighted by everything

figure(c, who, x, y, s, T, ...) draws one with her feet at (x, y); s = 1 is about 1560 px tall. Joint angles come from a
pose dict (see POSES); doll() turns a list of timed poses into wind-up-doll movement: each pose is held, then snapped
to the next with a little overshoot (the creak goes on the snap)."""
import math

import numpy as np
import skia

import kit as K
from kit import INK, WHITE, capsule, lin, mix, paint, path, rad, shade, smooth

SKIN, SKIN_L, SKIN_D = K.SKIN, K.SKIN_L, K.SKIN_D

LOOKS = {
    "zuza": dict(hair="bob", haircol=(30, 24, 26), dress=(30, 28, 34), trim=(248, 246, 238), sleeves="long", legs=(246, 244, 236),
                 shoes=(22, 20, 22), iris=(96, 60, 38), lip=(206, 112, 120), brow=(40, 30, 30), mood="deadpan"),
    "lili": dict(hair="hive", haircol=(232, 196, 118), band=(150, 190, 226), dress=(250, 246, 236), dots=(222, 82, 52),
                 sleeves="puff", legs=(240, 192, 182), shoes=(196, 40, 52), iris=(70, 120, 172), lip=(232, 128, 142),
                 brow=(168, 128, 80), mood="delight"),
    # two strangers, for the photographs in the choice-blindness trick
    "eva": dict(hair="bob", haircol=(150, 70, 40), iris=(70, 100, 60), lip=(196, 90, 90), brow=(120, 60, 40), crown=False, mood="smile"),
    "mira": dict(hair="hive", haircol=(40, 30, 32), band=(176, 30, 54), iris=(90, 60, 40), lip=(200, 60, 70), brow=(40, 30, 30), crown=False,
                 earrings=True, mood="smile"),
}

# joint angles in degrees: sL/sR shoulder (0 = hanging, 90 = straight out, 170 = up), eL/eR elbow (bends the forearm
# further the same way; ~150 brings the hand up by the face), hL/hR hip (+ = out to that side), kL/kR knee, lean, tilt
POSES = {
    "stand": dict(sL=8, sR=8, eL=8, eR=8, hL=2, hR=2, kL=0, kR=0),
    "doll": dict(sL=28, sR=28, eL=4, eR=4, hL=4, hR=4),
    "hips": dict(sL=46, sR=46, eL=-104, eR=-104, hL=5, hR=5),
    "wave": dict(sL=10, sR=150, eL=8, eR=32),
    "point": dict(sL=8, sR=96, eL=8, eR=4),
    "point_l": dict(sL=96, sR=8, eL=4, eR=8),
    "shrug": dict(sL=44, sR=44, eL=96, eR=96),
    "up": dict(sL=158, sR=158, eL=14, eR=14),
    "t": dict(sL=90, sR=90, eL=0, eR=0),
    "present": dict(sL=10, sR=64, eL=8, eR=52),
    "hold": dict(sL=14, sR=14, eL=-84, eR=-84),
    "hold_r": dict(sL=10, sR=30, eL=8, eR=100),
    "lift_r": dict(sL=10, sR=120, eL=8, eR=40),
    "eat": dict(sL=10, eL=8, tR=(26, -1286)),
    "think": dict(sL=20, sR=14, eL=-100, eR=-150, tilt=-6),
    "throw": dict(sL=20, sR=150, eL=10, eR=90, lean=-4),
    "throw2": dict(sL=30, sR=70, eL=10, eR=0, lean=5),
    "clap": dict(sL=18, sR=18, eL=-100, eR=-100),
    "kick": dict(sL=80, sR=80, eL=10, eR=10, hR=34, kR=10),
    "step_l": dict(sL=20, sR=-6, eL=10, eR=10, hL=10, hR=-2),
    "step_r": dict(sL=-6, sR=20, eL=10, eR=10, hL=-2, hR=10),
    "cower": dict(sL=30, sR=30, eL=-150, eR=-150, tilt=8),
}
JOINTS = ("sL", "sR", "eL", "eR", "hL", "hR", "kL", "kR", "lean", "tilt")

MOODS = {        # brow lift, lid (1 open .. 0 shut), smile (-1 .. 1), mouth open bias
    "deadpan": (0.0, 0.62, 0.0, 0.0),
    "delight": (0.6, 1.0, 0.85, 0.15),
    "smile": (0.3, 0.86, 0.6, 0.0),
    "wide": (1.0, 1.15, -0.1, 0.35),
    "sly": (-0.3, 0.55, 0.45, 0.0),
    "sad": (0.8, 0.7, -0.6, 0.0),
    "chew": (0.1, 0.8, 0.3, 0.0),
    "shut": (0.2, 0.0, 0.3, 0.0),
}


def pose(name_or_dict):
    P = dict(POSES["stand"])
    P.update(dict(lean=0, tilt=0))
    P.update(POSES[name_or_dict] if isinstance(name_or_dict, str) else name_or_dict)
    for side, key in ((-1, "tL"), (1, "tR")):                             # resolve hand targets to angles
        if P.get(key) is not None:
            a1, a2 = reach(side, *P.pop(key))
            P["sL" if side < 0 else "sR"], P["eL" if side < 0 else "eR"] = a1, a2
        P.pop(key, None)
    return P


def _back(k):
    """Ease out with a small overshoot (a doll's limb flung into place)."""
    c1 = 1.9
    c3 = c1 + 1
    return 1 + c3 * (k - 1) ** 3 + c1 * (k - 1) ** 2


def doll(T, keys, snap=0.13):
    """keys: [(t, pose)] -> (joint dict, jolt). Each pose is held, then snapped to with an overshoot; jolt (0..1) is
    the little bounce of the whole body on each snap."""
    keys = sorted(keys, key=lambda k: k[0])
    i = 0
    for j, (t, _) in enumerate(keys):
        if t <= T:
            i = j
    cur = pose(keys[i][1])
    if i == 0 or T - keys[i][0] >= snap or T < keys[0][0]:
        jolt = max(0.0, 1 - (T - keys[i][0]) / 0.25) if T >= keys[i][0] and i > 0 else 0.0
        return cur, jolt
    prev = pose(keys[i - 1][1])
    k = (T - keys[i][0]) / snap
    f = _back(k)
    out = {j: prev[j] + (cur[j] - prev[j]) * f for j in JOINTS}
    return out, 1.0


def snaps(keys):
    """The moments a doll snaps into a new pose (for the creaks)."""
    keys = sorted(keys, key=lambda k: k[0])
    return [t for t, _ in keys[1:]]


# ------------------------------------------------------------------ the parts

def daisy(c, x, y, r, rot=0.0, a=1.0, petals=14, seed=0, center=None):
    """A daisy: white petals around a yellow eye."""
    rng = K.rng_at(seed, 3)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    for i in range(petals):
        ang = 360 * i / petals + rng.uniform(-6, 6)
        L = r * rng.uniform(0.86, 1.0)
        c.save()
        c.rotate(ang)
        c.drawOval(skia.Rect.MakeLTRB(-r * 0.17, -L, r * 0.17, -r * 0.18), paint(K.DAISY, a))
        c.drawLine(0, -L * 0.85, 0, -r * 0.3, paint((214, 214, 200), 0.6 * a, stroke=max(0.6, r * 0.03)))
        c.restore()
    cc = center or K.YOLK
    c.drawCircle(0, 0, r * 0.3, paint(shader=rad((-r * 0.08, -r * 0.08), r * 0.34, [mix(cc, WHITE, 0.3), cc, K.YOLK_D]), a=a))
    for i in range(7):
        ang = i * 2.4
        c.drawCircle(r * 0.16 * math.cos(ang) * (i / 7), r * 0.16 * math.sin(ang) * (i / 7), r * 0.035, paint(K.YOLK_D, 0.7 * a))
    c.restore()


def crown(c, front, seed=0, r=21, cy=-104, rx=112):
    """The daisy crown, in head coordinates: the back half (front=False) is drawn behind the hair."""
    n = 11
    for i in range(n):
        ang = math.pi * 2 * i / n + 0.15
        x, y = rx * math.cos(ang), cy + 30 * math.sin(ang)
        is_front = math.sin(ang) > 0
        if is_front != front:
            continue
        sc = 0.8 + 0.25 * (math.sin(ang) + 1) / 2
        if front:
            c.drawPath(path([(x - 18, y + 4), (x + 18, y + 4)], closed=False), paint((70, 120, 50), stroke=4))
        daisy(c, x, y, r * sc, rot=ang * 40, seed=seed + i)


def _eye(c, x, y, side, look, lid, iris, blink, mod):
    """A 1960s eye: white, iris and catchlight, a winged liner, painted lower lashes."""
    w, h = 26, 14
    open_ = max(0.0, min(1.15, lid)) * (1 - blink)
    c.save()
    c.translate(x, y)
    eye = smooth([(-w, 2), (-w * 0.5, -h * open_ - 1), (w * 0.4, -h * open_ - 2), (w, -1), (w * 0.4, h * 0.75 * max(0.25, open_)),
                  (-w * 0.5, h * 0.7 * max(0.25, open_))])
    c.drawOval(skia.Rect.MakeLTRB(-w - 10, -h - 22, w + 10, -2), paint((172, 150, 180), 0.25, blur=6))   # a pale lid colour
    if open_ > 0.12:
        c.drawPath(eye, paint((250, 248, 244)))
        c.save()
        c.clipPath(eye, doAntiAlias=True)
        gx, gy = look[0] * 9, look[1] * 4
        c.drawCircle(gx, gy + 1, 11.5, paint(shader=rad((gx - 3, gy - 3), 13, [mix(iris, WHITE, 0.3), iris, mix(iris, INK, 0.5)])))
        c.drawCircle(gx, gy + 1, 5.2, paint(INK))
        c.drawCircle(gx - 4, gy - 3, 2.8, paint(WHITE, 0.95))
        c.drawRect(skia.Rect.MakeLTRB(-w, -h - 4, w, -h * open_ + 3), paint(SKIN_D, 0.25, blur=3))   # the lid's shadow
        c.restore()
        # liner along the lid, flicked out into a wing
        top = path([(-w - 1, 2), (-w * 0.5, -h * open_ - 1), (w * 0.4, -h * open_ - 2), (w + 2, -2), (w + 12 * mod, -9 * mod)], closed=False)
        c.drawPath(top, paint(INK, stroke=3.6))
        for i in range(5):                                                  # upper lashes, curling outward
            u = -0.45 + i * 0.33
            lx, ly = w * u, -h * open_ * (1 - (u * 0.7) ** 2) - 2
            L = 6 + 6 * (u + 0.5) * mod
            c.drawPath(K.bez_path([(lx, ly), (lx + 2 + 4 * u, ly - L * 0.7), (lx + 5 + 8 * u, ly - L)]), paint(INK, stroke=1.7))
        for i in range(4):                                                  # painted lower lashes
            lx = -w * 0.55 + i * w * 0.36
            c.drawLine(lx, h * 0.7 * max(0.25, open_) + 2, lx - 1, h * 0.7 * max(0.25, open_) + 9, paint(INK, 0.8, stroke=1.5))
    else:
        c.drawPath(path([(-w, 0), (-w * 0.3, 5), (w * 0.4, 5), (w + 10 * mod, -4 * mod)], closed=False), paint(INK, stroke=3.4))
        for i in range(5):
            lx = -w * 0.6 + i * w * 0.36
            c.drawLine(lx, 5, lx - 1, 12, paint(INK, stroke=1.6))
    c.restore()


def head(c, who, T, mood="deadpan", talk=0.0, look=(0.0, 0.0), blink=0.0, turn=0.0, mood2=None, mk=0.0):
    """The head at the local origin, face ~190 wide, chin at y = 125."""
    L = LOOKS[who]
    m = MOODS.get(mood, MOODS["deadpan"])
    if mood2:
        m2 = MOODS[mood2]
        m = tuple(a + (b - a) * mk for a, b in zip(m, m2))
    brow, lid, smile, open_bias = m
    tx = turn * 14
    hc = L["haircol"]
    # hair, behind
    if L["hair"] == "bob":
        c.drawPath(smooth([(-118, 60), (-122, -40), (-104, -126), (-58, -160), (0, -170), (58, -160), (104, -126), (122, -40), (118, 60),
                           (104, 108), (60, 120), (-60, 120), (-104, 108)]), paint(shader=lin((0, -170), (0, 120), [mix(hc, WHITE, 0.08), hc])))
    else:
        c.drawPath(smooth([(-112, 40), (-118, -60), (-110, -150), (-76, -236), (0, -270), (76, -236), (110, -150), (118, -60), (112, 40),
                           (138, 150), (150, 178), (104, 168), (60, 110), (-60, 110), (-104, 168), (-150, 178), (-138, 150)]),
                     paint(shader=lin((0, -270), (0, 180), [mix(hc, WHITE, 0.2), hc, mix(hc, INK, 0.25)])))
    ccy = -112 if L["hair"] == "bob" else -168
    if L.get("crown", True):
        crown(c, False, seed=7 if who == "zuza" else 21, cy=ccy, rx=112 if L["hair"] == "bob" else 104)
    # neck
    c.drawPath(path([(-34, 90), (34, 90), (40, 170), (-40, 170)]), paint(shader=lin((0, 90), (0, 170), [SKIN_D, mix(SKIN, SKIN_D, 0.3)])))
    # ears (Lili's show)
    if L["hair"] == "hive":
        for sx in (-1, 1):
            c.drawOval(skia.Rect.MakeLTRB(sx * 96 - 11, -16, sx * 96 + 11, 30), paint(mix(SKIN, SKIN_D, 0.35)))
    # the face
    fp = smooth([(0 + tx * 0.2, -132), (62, -122), (90, -84), (95, -20), (88, 40), (68, 88), (34, 118), (0 + tx * 0.4, 126), (-34, 118),
                 (-68, 88), (-88, 40), (-95, -20), (-90, -84), (-62, -122)])
    c.drawPath(fp, paint(SKIN))
    c.save()
    c.clipPath(fp, doAntiAlias=True)
    c.drawRect(skia.Rect.MakeLTRB(-110, -140, 110, 140), paint(shader=rad((-26 + tx, -36), 172, [(*SKIN_L, 0.85), (*SKIN, 0.0), (*SKIN_D, 0.75)],
                                                                       [0.0, 0.55, 1.0])))
    for sx in (-1, 1):                                                    # cheek contour and blush
        c.drawCircle(sx * 54 + tx, 42, 28, paint((240, 120, 130), 0.22, blur=14))
        c.drawPath(K.bez_path([(sx * 92, 4), (sx * 74, 50), (sx * 40, 70)]), paint(SKIN_D, 0.3, stroke=12, blur=8))
    c.drawPath(K.bez_path([(-10 + tx, -24), (-12 + tx * 1.1, 12), (-12 + tx * 1.2, 30)]), paint(SKIN_D, 0.3, stroke=5, blur=4))   # nose
    c.drawPath(K.bez_path([(12 + tx, -24), (15 + tx * 1.1, 12), (15 + tx * 1.2, 32)]), paint(SKIN_D, 0.5, stroke=7, blur=5))
    for sx in (-1, 1):
        c.drawOval(skia.Rect.MakeXYWH(sx * 9 - 5 + tx * 1.2, 36, 10, 6), paint((140, 80, 70), 0.7, blur=1.2))
    c.drawCircle(-2 + tx * 1.2, 26, 7, paint(SKIN_L, 0.75, blur=4))
    c.drawOval(skia.Rect.MakeXYWH(-56, 112, 112, 40), paint(SKIN_D, 0.45, blur=10))
    c.restore()
    # brows
    for sx in (-1, 1):
        bx, by = sx * 44 + tx, -50 - 9 * brow - (6 if (who == "zuza" and sx > 0 and mood == "deadpan") else 0)
        c.drawPath(K.bez_path([(bx - sx * 26, by + 6), (bx, by - 6 - 3 * brow), (bx + sx * 26, by + 2 + (4 * brow if sx > 0 else 0))]),
                   paint(L["brow"], stroke=5 if L["hair"] == "bob" else 4))
    # eyes
    for sx in (-1, 1):
        _eye(c, sx * 42 + tx, -12, sx, look, lid, L["iris"], blink, 1.0 if L["hair"] == "bob" else 0.6)
    # the mouth
    op = max(0.0, min(1.0, talk * 1.1 + open_bias * (0.4 if talk > 0.05 else 0.0)))
    mx, my, mw = 0 + tx * 1.2, 72, 26 + 4 * smile
    lip = L["lip"]
    if op > 0.06:
        g = 4 + op * 26
        p = smooth([(-mw, -2 * smile), (-mw * 0.4, -4), (0, -3), (mw * 0.4, -4), (mw, -2 * smile), (mw * 0.5, g), (0, g + 2), (-mw * 0.5, g)])
        c.save()
        c.translate(mx, my)
        c.drawPath(p, paint((92, 30, 38)))
        c.save()
        c.clipPath(p, doAntiAlias=True)
        c.drawRect(skia.Rect.MakeLTRB(-mw, -6, mw, 4), paint((246, 242, 236)))          # teeth
        c.drawOval(skia.Rect.MakeLTRB(-mw * 0.5, g - 8, mw * 0.5, g + 8), paint((200, 90, 100)))     # tongue
        c.restore()
        c.drawPath(smooth([(-mw - 2, -1 - 2 * smile), (-mw * 0.4, -9), (0, -6), (mw * 0.4, -9), (mw + 2, -1 - 2 * smile), (mw * 0.4, -3), (-mw * 0.4, -3)]),
                   paint(lip))
        c.drawPath(smooth([(-mw * 0.7, g - 1), (0, g + 7), (mw * 0.7, g - 1), (0, g + 1)]), paint(lip))
        c.restore()
    else:
        c.save()
        c.translate(mx, my)
        up = -9 * smile
        c.drawPath(smooth([(-mw - 2, up), (-mw * 0.4, -8), (0, -5), (mw * 0.4, -8), (mw + 2, up), (mw * 0.4, 1), (-mw * 0.4, 1)]), paint(lip))
        c.drawPath(smooth([(-mw + 2, up + 1), (-mw * 0.4, 2), (0, 2), (mw * 0.4, 2), (mw - 2, up + 1), (mw * 0.4, 12), (0, 14), (-mw * 0.4, 12)]),
                   paint(mix(lip, WHITE, 0.08)))
        c.drawPath(K.bez_path([(-mw, up + 1), (0, 3 + 2 * smile), (mw, up + 1)]), paint(mix(lip, INK, 0.5), stroke=2.2))
        c.drawCircle(mw * 0.3, 8, 3, paint(WHITE, 0.35, blur=1.5))
        c.restore()
    # hair, in front
    if L["hair"] == "bob":
        fr = smooth([(-104, -30), (-108, -110), (-62, -158), (0, -168), (62, -158), (108, -110), (104, -30), (100, 40), (92, 96), (78, 104),
                     (80, 20), (70, -66), (40, -70), (0, -72), (-40, -70), (-70, -66), (-80, 20), (-78, 104), (-92, 96), (-100, 40)])
        c.drawPath(fr, paint(shader=lin((-100, -160), (100, 40), [mix(hc, WHITE, 0.12), hc, mix(hc, INK, 0.3)])))
        c.drawPath(K.bez_path([(-80, -134), (-10, -152), (60, -142)]), paint(WHITE, 0.16, stroke=12, blur=5))   # shine
        c.drawPath(path([(-70, -68), (70, -68)], closed=False), paint(mix(hc, INK, 0.4), stroke=3))
    else:
        top = smooth([(-98, -40), (-104, -126), (-86, -210), (-30, -262), (40, -258), (92, -206), (104, -126), (98, -40), (82, -84),
                      (40, -112), (-6, -116), (-58, -100), (-86, -70)])
        c.drawPath(top, paint(shader=lin((-90, -260), (90, -40), [mix(hc, WHITE, 0.3), hc, mix(hc, INK, 0.2)])))
        c.drawPath(K.bez_path([(-70, -200), (-10, -248), (60, -222)]), paint(WHITE, 0.25, stroke=14, blur=6))
        c.drawPath(K.bez_path([(-100, -128), (0, -150), (100, -128)]), paint(L["band"], stroke=17))     # the hair band
        c.drawPath(K.bez_path([(-100, -133), (0, -155), (100, -133)]), paint(WHITE, 0.3, stroke=4))
        for sx in (-1, 1):                                                    # the side falls and the flicked-out ends
            c.drawPath(smooth([(sx * 96, -60), (sx * 108, 30), (sx * 118, 110), (sx * 150, 168), (sx * 120, 160), (sx * 94, 120), (sx * 86, 30),
                               (sx * 84, -40)]), paint(shader=lin((0, -60), (0, 170), [hc, mix(hc, INK, 0.2)])))
    if L.get("crown", True):
        crown(c, True, seed=7 if who == "zuza" else 21, cy=ccy, rx=112 if L["hair"] == "bob" else 104)
    if L.get("earrings"):                                                 # big gold hoops
        for sx in (-1, 1):
            c.drawCircle(sx * 98, 58, 26, paint((226, 176, 50), stroke=6))
            c.drawCircle(sx * 98 - 4, 52, 26, paint((255, 236, 150), 0.6, stroke=2))


def _leg(c, hip, knee, ankle, colr, sx):
    """A leg as one outline: a full thigh, a slim knee, a calf, a fine ankle."""
    def along(p, q, u, w):
        dx, dy = q[0] - p[0], q[1] - p[1]
        L = math.hypot(dx, dy) + 1e-6
        nx, ny = -dy / L, dx / L
        x, y = p[0] + dx * u, p[1] + dy * u
        return (x + nx * w, y + ny * w), (x - nx * w, y - ny * w)
    prof = [(hip, knee, 0.0, 44), (hip, knee, 0.5, 38), (hip, knee, 0.97, 28), (knee, ankle, 0.25, 31), (knee, ankle, 0.6, 24), (knee, ankle, 1.0, 17)]
    left, right = [], []
    for p, q, u, w in prof:
        a, b = along(p, q, u, w)
        left.append(a)
        right.append(b)
    pts = left + right[::-1]
    p = smooth(pts)
    c.drawPath(p, paint(shader=lin((hip[0] - 50, 0), (hip[0] + 50, 0), [mix(colr, INK, 0.12), mix(colr, WHITE, 0.25), colr, mix(colr, INK, 0.22)],
                                   [0, 0.35, 0.65, 1])))
    kx, ky = knee
    c.drawOval(skia.Rect.MakeLTRB(kx - 16, ky - 12, kx + 16, ky + 14), paint(mix(colr, INK, 0.12), 0.35, blur=6))


def _hand(c, x, y, ang, pose_, skin, flip=1):
    """A hand at the wrist, pointing along ang (degrees, 0 = down)."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(flip, 1)
    if pose_ in ("fist", "hold"):
        p = K.rrect(-17, -2, 17, 34, 13)
        shade(c, p, skin, k=0.25)
        c.drawPath(K.capsule(-14, 6, -22, 24, 10, 8), paint(mix(skin, SKIN_D, 0.2)))
    else:
        palm = smooth([(-16, -2), (16, -2), (19, 22), (14, 34), (-14, 34), (-18, 20)])
        shade(c, palm, skin, k=0.25)
        n = 1 if pose_ == "point" else 4
        for i in range(4):
            L = 30 if (pose_ != "point" or i == 1) else 12
            fx = -11 + i * 7.4
            c.drawPath(K.capsule(fx, 28, fx + (i - 1.5) * 2.5, 28 + L, 7.4, 6.2), paint(skin))
            c.drawCircle(fx + (i - 1.5) * 2.5, 28 + L - 2, 2.6, paint((230, 110, 120), 0.6))     # nail varnish
        c.drawPath(K.capsule(-15, 8, -27, 26, 8.6, 7), paint(mix(skin, SKIN_D, 0.15)))
    c.restore()


def _arm(c, sx, x0, y0, a1, a2, L1, L2, sleeve, skin, look_, hand_pose, prop):
    r1 = math.radians(a1) * sx
    ex, ey = x0 + L1 * math.sin(r1), y0 + L1 * math.cos(r1)
    r2 = r1 + math.radians(a2) * sx
    hx, hy = ex + L2 * math.sin(r2), ey + L2 * math.cos(r2)
    ang = -math.degrees(r2)
    if look_["sleeves"] == "long":
        shade(c, capsule(x0, y0, ex, ey, 54, 46), sleeve, k=0.22)
        shade(c, capsule(ex, ey, hx, hy, 46, 40), sleeve, k=0.22)
        c.drawPath(capsule(ex + (hx - ex) * 0.86, ey + (hy - ey) * 0.86, hx, hy, 44, 44), paint(look_["trim"]))   # the white cuff
    else:
        shade(c, capsule(x0, y0, ex, ey, 46, 40), skin, k=0.22)
        shade(c, capsule(ex, ey, hx, hy, 40, 32), skin, k=0.22)
        c.save()                                                                       # the puff sleeve
        c.translate(x0, y0)
        c.rotate(-math.degrees(r1))
        sl = smooth([(-34, -14), (0, -26), (34, -14), (40, 40), (30, 84), (0, 92), (-30, 84), (-40, 40)])
        shade(c, sl, look_["dress"], k=0.16)
        c.save()
        c.clipPath(sl, doAntiAlias=True)
        rng = K.rng_at(sx, 5)
        for i in range(6):
            c.drawCircle(rng.uniform(-36, 36), rng.uniform(-20, 90), 11, paint(look_["dots"]))
        c.restore()
        c.drawPath(K.bez_path([(-30, 84), (0, 96), (30, 84)]), paint(mix(look_["dress"], INK, 0.25), 0.6, stroke=4))
        c.restore()
    _hand(c, hx, hy, ang, hand_pose, skin, flip=-sx)
    if prop is not None:
        prop(c, hx, hy, ang)
    m = c.getTotalMatrix()
    q = m.mapXY(hx, hy)
    return (q.x(), q.y(), ang)


def reach(sx, tx, ty, sh=(100, -1140), L1=230, L2=210):
    """Joint angles (a1, a2) that put the hand of arm sx (-1 left, +1 right) at (tx, ty) in body coordinates, the elbow
    kept out to the side."""
    x0, y0 = sx * sh[0], sh[1]
    dx, dy = tx - x0, ty - y0
    d = min(max(math.hypot(dx, dy), abs(L1 - L2) + 1), L1 + L2 - 1)
    th = math.atan2(dx, dy)
    al = math.acos(max(-1, min(1, (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))))
    best = None
    for r1 in (th + al, th - al):
        ex, ey = x0 + L1 * math.sin(r1), y0 + L1 * math.cos(r1)
        score = sx * ex
        if best is None or score > best[0]:
            best = (score, r1, ex, ey)
    _, r1, ex, ey = best
    r2 = math.atan2(tx - ex, ty - ey)
    wrap = lambda a: (a + 180) % 360 - 180
    return wrap(math.degrees(r1) * sx), wrap(math.degrees(r2 - r1) * sx)


MOUTH = (0, -1296)


def figure(c, who, x, y, s, T, P="stand", mood=None, talk=0.0, look=(0.0, 0.0), blink=0.0, turn=0.0, jolt=0.0, hands=("open", "open"),
           props=(None, None), mood2=None, mk=0.0, legs=True, breathe=True):
    """One of the duo, feet at (x, y). Returns {'head': (x, y), 'hand_l': (x, y, ang), 'hand_r': ...} in device px."""
    Lk = LOOKS[who]
    P = pose(P)                                                           # defaults filled in, hand targets solved
    mood = mood or Lk["mood"]
    out = {}
    c.save()
    c.translate(x, y - 14 * jolt * s)
    c.scale(s, s)
    br = 2.5 * math.sin(T * 2 * math.pi / 3.4) if breathe else 0.0
    lean = P.get("lean", 0)
    hip_y = -780
    if legs:
        for sx, hk, kk in ((-1, "hL", "kL"), (1, "hR", "kR")):
            a0 = math.radians(P[hk]) * sx
            kx, ky = sx * 52 + 380 * math.sin(a0), hip_y + 380 * math.cos(a0)
            a1 = a0 - math.radians(P[kk]) * sx
            fx, fy = kx + 360 * math.sin(a1), ky + 360 * math.cos(a1)
            _leg(c, (sx * 52, hip_y), (kx, ky), (fx, fy - 18), Lk["legs"], sx)
            c.drawOval(skia.Rect.MakeLTRB(fx - 60, fy + 12, fx + 64, fy + 34), paint(INK, 0.3, blur=7))      # its shadow
            shoe = smooth([(fx - 30, fy - 16), (fx + 30 + 10 * sx, fy - 14), (fx + 44 * sx + (0 if sx > 0 else 0), fy + 6), (fx + 30 * sx, fy + 20),
                           (fx - 30 * sx, fy + 20), (fx - 36 * sx, fy + 2)])
            c.drawPath(shoe, paint(shader=lin((0, fy - 16), (0, fy + 20), [mix(Lk["shoes"], WHITE, 0.25), Lk["shoes"]])))
            c.drawLine(fx - 26, fy - 10, fx + 26, fy - 12, paint(Lk["shoes"], stroke=6))                    # the strap
            c.drawCircle(fx + 22 * sx, fy - 11, 4, paint((220, 210, 190)))
    c.save()
    c.translate(0, hip_y)
    c.rotate(lean)
    c.translate(0, -hip_y)
    sh_y = -1170 + br * 0.4
    # the dress: a short A-line shift
    dress = smooth([(-74, sh_y - 6), (-104, sh_y + 14), (-96, -1040), (-92, -900), (-118, -760), (-150, -646), (-60, -630), (0, -628), (60, -630),
                    (150, -646), (118, -760), (92, -900), (96, -1040), (104, sh_y + 14), (74, sh_y - 6), (0, sh_y + 6)])
    shade(c, dress, Lk["dress"], k=0.26 if who == "zuza" else 0.12)
    c.save()
    c.clipPath(dress, doAntiAlias=True)
    if who == "lili":
        rng = K.rng_at(9)
        for i in range(34):
            px, py = rng.uniform(-160, 160), rng.uniform(sh_y - 10, -620)
            c.drawCircle(px, py, 15, paint(Lk["dots"]))
        c.drawRect(skia.Rect.MakeLTRB(-170, -640, 170, -626), paint(mix(Lk["dress"], INK, 0.12)))
    else:
        c.drawRect(skia.Rect.MakeLTRB(-170, -662, 170, -630), paint(Lk["trim"]))                       # a white hem band
    for fx in (-70, -20, 34, 84):                                                                          # folds
        c.drawPath(K.bez_path([(fx * 0.5, -900), (fx * 0.8, -780), (fx * 1.1, -640)]), paint(mix(Lk["dress"], INK, 0.25), 0.35, stroke=10, blur=6))
    c.drawPath(K.bez_path([(-90, -1060), (0, -1020), (90, -1060)]), paint(mix(Lk["dress"], INK, 0.3), 0.3, stroke=12, blur=8))
    c.restore()
    if who == "zuza":                                                     # the round white collar
        for sx in (-1, 1):
            c.drawPath(smooth([(0, sh_y + 6), (sx * 30, sh_y - 4), (sx * 76, sh_y + 6), (sx * 70, sh_y + 46), (sx * 26, sh_y + 52)]), paint(Lk["trim"]))
            c.drawPath(smooth([(0, sh_y + 6), (sx * 30, sh_y - 4), (sx * 76, sh_y + 6), (sx * 70, sh_y + 46), (sx * 26, sh_y + 52)]),
                       paint((200, 196, 186), 0.6, stroke=2))
    else:                                                                 # a little bow at the neck
        c.drawPath(path([(0, sh_y + 20), (-30, sh_y + 4), (-30, sh_y + 36)]), paint(Lk["band"]))
        c.drawPath(path([(0, sh_y + 20), (30, sh_y + 4), (30, sh_y + 36)]), paint(Lk["band"]))
        c.drawCircle(0, sh_y + 20, 8, paint(mix(Lk["band"], INK, 0.2)))
    # the head
    c.save()
    c.translate(0, sh_y - 200)
    c.rotate(P.get("tilt", 0) + 1.5 * math.sin(T * 0.9))
    head(c, who, T, mood, talk, look, blink, turn, mood2, mk)
    m = c.getTotalMatrix()
    q = m.mapXY(0, 0)
    out["head"] = (q.x(), q.y())
    q = m.mapXY(0, 72)
    out["mouth"] = (q.x(), q.y())
    c.restore()
    # the arms, in front
    for sx, sk, ek, key, hp, pr in ((-1, "sL", "eL", "hand_l", hands[0], props[0]), (1, "sR", "eR", "hand_r", hands[1], props[1])):
        out[key] = _arm(c, sx, sx * 100, sh_y + 30, P[sk], P[ek], 230, 210, Lk["dress"], SKIN, Lk, hp, pr)
    c.restore()
    c.restore()
    return out


def talk_env(wav, sr, fps=24):
    """Mouth opening per video frame from a line's audio."""
    hop = sr // fps
    n = len(wav) // hop
    e = np.sqrt((wav[: n * hop].reshape(n, hop).astype(np.float64) ** 2).mean(axis=1))
    e = e / (np.percentile(e, 95) + 1e-9)
    return np.clip(e, 0, 1)

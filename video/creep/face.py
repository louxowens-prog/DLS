"""The cast, painted like actors in a 1982 horror film under coloured gels: a key light from one side (warm amber, or
blood red, sickly green, electric blue), a hard rim of another colour from the other, the rest in deep coloured shade.
Faces are painted soft (no outline), with thin ink only where a make-up artist would draw: lashes, lip line, brows.

bust(c, who, x, y, s, T, ...)  - head and shoulders; (x, y) is the centre of the head, s = 1: the head is 300 px tall
hand(c, x, y, s, ang, ...)     - a hand (open, grip, point, claw), for phones, comics, steering wheels, the host

Expressions are over the top on purpose: neutral, talk, smile, smirk, sly, fear, panic, scream, cackle, blank, angry,
smug, dead.
"""
import math

import numpy as np
import skia

import kit as K
from kit import INK, WHITE, mix, paint, path, smooth

# ------------------------------------------------------------------ the people

CAST = {
    "nora": dict(skin=(234, 192, 164), hair=(46, 28, 24), style="bob", top=(128, 34, 58), neck="cardigan", iris=(80, 120, 60),
                 lips=(186, 76, 86), age=0.1, freckles=True, brow=(50, 32, 26)),
    "vera": dict(skin=(242, 198, 172), hair=(240, 206, 120), style="big", top=(24, 22, 26), neck="fur", iris=(60, 110, 170),
                 lips=(206, 16, 44), age=0.4, shadow=(70, 120, 200), pearls=True, lash=1.6, brow=(150, 110, 60)),
    "kit": dict(skin=(158, 104, 72), hair=(28, 18, 14), style="curls", top=(54, 120, 92), neck="sweater", iris=(70, 44, 26),
                lips=(140, 74, 70), age=0.0, brow=(30, 20, 14)),
    "prof": dict(skin=(228, 188, 164), hair=(176, 176, 182), style="bun", top=(30, 28, 36), neck="gown", iris=(80, 90, 100),
                 lips=(150, 80, 84), age=0.7, glasses=True, brow=(150, 150, 156), jaw=0.94),
    "hale": dict(skin=(218, 172, 142), hair=(96, 52, 30), style="cap", top=(40, 128, 130), neck="scrubs", iris=(90, 70, 40),
                 lips=(170, 92, 90), age=0.3, mask=True, cap=(40, 128, 130), brow=(80, 44, 26)),
    "hale_old": dict(skin=(226, 186, 166), hair=(236, 234, 228), style="thin", top=(170, 196, 214), neck="gown_dots", iris=(90, 70, 40),
                     lips=(160, 100, 100), age=1.0, brow=(210, 206, 200), jaw=0.95),
    "junior": dict(skin=(200, 154, 122), hair=(22, 16, 14), style="pony", top=(64, 92, 168), neck="scrubs", iris=(50, 34, 20),
                   lips=(176, 96, 96), age=0.0, brow=(26, 18, 14)),
    "father": dict(skin=(222, 178, 152), hair=(214, 212, 206), style="bald", top=(120, 92, 64), neck="cardigan", iris=(80, 100, 120),
                   lips=(168, 110, 104), age=0.9, male=True, brow=(200, 196, 190), jaw=1.06, glasses=True),
    "host": dict(skin=(150, 170, 128), hair=(206, 206, 196), style="hood", hood=(70, 20, 84), top=(86, 26, 96), neck="shawl", iris=(255, 214, 40),
                 lips=(70, 40, 60), age=1.0, ghoul=True, brow=(230, 230, 224), jaw=0.9, lash=0.0),
}

EXPR = {
    #          brow (inner up, outer up, frown)  eye open, pupil, smile, mouth open, wide, extras
    "neutral": dict(brow=(0.0, 0.0, 0.0), eye=1.0, pupil=1.0, smile=0.05, open=0.0, wide=0.0),
    "smile": dict(brow=(0.2, 0.1, 0.0), eye=0.82, pupil=1.0, smile=0.75, open=0.12, wide=0.3, teeth=True),
    "smirk": dict(brow=(-0.1, 0.35, 0.15), eye=0.78, pupil=1.0, smile=0.45, open=0.0, wide=0.1, asym=0.7),
    "sly": dict(brow=(-0.3, 0.7, 0.4), eye=0.7, pupil=0.9, smile=0.75, open=0.22, wide=0.55, teeth=True, asym=0.4),
    "smug": dict(brow=(0.0, 0.25, 0.0), eye=0.55, pupil=1.0, smile=0.4, open=0.0, wide=0.15),
    "fear": dict(brow=(0.95, 0.15, 0.0), eye=1.45, pupil=0.55, smile=-0.35, open=0.5, wide=0.1),
    "panic": dict(brow=(0.85, -0.1, 0.1), eye=1.3, pupil=0.7, smile=-0.6, open=0.55, wide=0.35, sweat=True, teeth=True),
    "scream": dict(brow=(1.0, 0.45, 0.0), eye=1.65, pupil=0.4, smile=-0.15, open=1.22, wide=0.5, teeth=True, tongue=True, tendons=True),
    "cackle": dict(brow=(0.15, 0.7, -0.2), eye=0.3, pupil=1.0, smile=0.95, open=0.95, wide=0.8, teeth=True, tongue=True, tilt=-6),
    "blank": dict(brow=(0.0, 0.0, 0.0), eye=1.05, pupil=0.0, smile=0.0, open=0.06, wide=0.0, white=True),
    "angry": dict(brow=(-0.7, 0.35, 0.9), eye=0.85, pupil=0.85, smile=-0.45, open=0.25, wide=0.25, teeth=True),
    "dead": dict(brow=(0.2, 0.0, 0.0), eye=0.0, pupil=1.0, smile=-0.2, open=0.3, wide=0.0),
    "squint": dict(brow=(-0.3, 0.1, 0.5), eye=0.45, pupil=1.0, smile=-0.1, open=0.0, wide=0.0),
}

# lights: key (colour, direction it comes FROM as (dx, dy)), rim (colour, side), ambient shadow colour
LIGHTS = {
    "lamp": dict(key=((255, 196, 140), (-0.8, -0.4)), rim=((90, 140, 255), 1), amb=(54, 40, 70)),
    "storm": dict(key=((180, 200, 255), (0.8, -0.3)), rim=((255, 90, 160), -1), amb=(30, 30, 66)),
    "red": dict(key=((255, 60, 50), (-0.8, -0.2)), rim=((60, 120, 255), 1), amb=(50, 10, 30)),
    "green": dict(key=((150, 255, 110), (0.0, 1.0)), rim=((200, 60, 255), 1), amb=(20, 40, 30)),
    "blue": dict(key=((110, 150, 255), (0.8, -0.4)), rim=((255, 70, 70), -1), amb=(16, 20, 60)),
    "screen": dict(key=((150, 210, 255), (0.0, 0.6)), rim=((255, 120, 60), -1), amb=(20, 24, 48)),
    "laptop": dict(key=((190, 220, 255), (0.25, 0.45)), rim=((255, 120, 200), -1), amb=(44, 36, 74), gain=1.3),
    "dash": dict(key=((255, 196, 140), (0.5, 0.7)), rim=((90, 160, 255), -1), amb=(22, 22, 44)),
    "under": dict(key=((255, 160, 80), (0.0, 1.0)), rim=((80, 255, 120), 1), amb=(30, 14, 30)),
    "plain": dict(key=((170, 180, 196), (0.6, -0.6)), rim=((120, 130, 150), -1), amb=(30, 32, 38)),
    "candle": dict(key=((255, 170, 90), (0.3, 0.8)), rim=((60, 70, 120), -1), amb=(20, 16, 22)),
    "clinic": dict(key=((220, 255, 236), (-0.4, -0.8)), rim=((80, 200, 255), 1), amb=(40, 60, 70)),
}


def mul(c, k):
    return tuple(int(max(0, min(255, round(a * b / 255)))) for a, b in zip(c, k))


def scale(c, k):
    return tuple(int(max(0, min(255, round(a * k)))) for a in c)


class Light:
    def __init__(self, spec):
        if isinstance(spec, str):
            spec = LIGHTS[spec]
        (self.kc, (dx, dy)), (self.rc, self.rs), self.amb = spec["key"], spec["rim"], spec["amb"]
        n = math.hypot(dx, dy) + 1e-6
        self.kd = (dx / n, dy / n)
        self.gain = spec.get("gain", 1.12)
        self.rim_w = spec.get("rim_w", 1.0)

    def lit(self, base):
        return mul(scale(base, self.gain), self.kc)

    def shade(self, base):
        return mul(scale(base, 1.0), mix(self.amb, (255, 255, 255), 0.16))


def lit_fill(c, p, base, L, k=1.0, rim=1.0, soft=0.75, rim_w=7.0, a=1.0, round_=False, edge=0.35):
    """Fill a shape as lit by L: the ambient shade, the key colour sweeping in from the key side (radially, for round
    forms), a crescent of rim light on the rim side, and a faint dark contour."""
    b = p.computeTightBounds()
    cx, cy = b.centerX(), b.centerY()
    rx, ry = b.width() / 2 + 1, b.height() / 2 + 1
    dx, dy = L.kd
    c.drawPath(p, paint(L.shade(base), a))
    lc = L.lit(base)
    if round_:
        ctr = (cx + dx * rx * 0.42, cy + dy * ry * 0.42)
        sh = K.rad(ctr, max(rx, ry) * 1.35, [lc + (k,), lc + (k * 0.82,), lc + (0.0,)], [0.0, 0.42, 0.95])
    else:
        r = math.hypot(rx * dx, ry * dy) + 1
        sh = K.lin((cx + dx * r, cy + dy * r), (cx - dx * r, cy - dy * r), [lc + (k,), lc + (k * 0.85,), lc + (0.0,)], [0.0, soft * 0.45, soft])
    c.drawPath(p, paint(shader=sh, a=a))
    if rim > 0 and L.rc is not None:
        q = skia.Path(p)
        q.offset(-L.rs * rim_w * 0.9, rim_w * 0.3)
        cres = skia.Op(p, q, skia.PathOp.kDifference_PathOp)
        if cres is not None:
            c.save()
            c.clipPath(p, doAntiAlias=True)
            c.drawPath(cres, paint(L.rc, a * 0.85 * min(1.0, rim), blur=rim_w * 0.45))
            c.restore()
    if edge > 0:
        c.drawPath(p, paint(mix(L.amb, INK, 0.7), edge * a, stroke=2.0))


def soft(c, p, color, a, blur, clip=None):
    if clip is not None:
        c.save()
        c.clipPath(clip, doAntiAlias=True)
    c.drawPath(p, paint(color, a, blur=blur))
    if clip is not None:
        c.restore()


# ------------------------------------------------------------------ the head

def _face_path(P, t, drop=0.0):
    """The face outline; drop lowers the jaw (a scream, a cackle)."""
    j = P.get("jaw", 1.0)
    pts = [(0, -152), (62, -144), (98, -110), (110, -52), (108, 4), (103 * j, 50), (90 * j, 92), (66 * j, 124), (34 * j, 146), (0, 152)]
    if P.get("ghoul"):                                                   # gaunt: hollow under the cheekbones, a long pointed chin
        pts = [(0, -152), (64, -146), (100, -112), (112, -54), (110, -6), (92, 40), (80, 86), (54, 128), (24, 162), (0, 170)]
    if P.get("male"):
        pts = [(0, -150), (66, -142), (102, -108), (112, -50), (110, 6), (108, 52), (100, 96), (74, 130), (36, 148), (0, 152)]
    pts = [(x * (1 - 0.12 * drop / 60 * max(0, (y - 40) / 110)), y + drop * max(0.0, min(1.0, (y - 30) / 100))) for x, y in pts]
    out = []
    for x, y in pts + [(-x, y) for x, y in reversed(pts[1:-1])]:
        xx = x * (1 - 0.14 * t * (1 if x > 0 else -1)) + t * 10
        out.append((xx, y))
    return smooth(out)

def _eye(c, cx, cy, side, P, E, L, blink, gaze, T, fx):
    """One eye at (cx, cy); side -1 = on the left of the picture."""
    w = 29.0
    op = max(0.0, E["eye"] * (1 - blink))
    h = 13.5 * op
    ghoul = P.get("ghoul")
    # the socket: soft shadow above and round
    sock = K.oval(cx - 44, cy - 34, cx + 44, cy + 24)
    soft(c, sock, mix(L.amb, (60, 20, 30), 0.4), 0.38 + 0.25 * P.get("age", 0) + (0.3 if ghoul else 0), 12)
    if P.get("shadow") and op > 0.1:                                     # eye shadow (Vera's blue, to the brow)
        soft(c, K.oval(cx - 30, cy - 26, cx + 30, cy + 2), P["shadow"], 0.55, 7)
    if op < 0.08:                                                       # closed: a lash line
        p = K.bez_path([(cx - w, cy), (cx, cy + 6), (cx + w, cy)])
        c.drawPath(p, paint(mix(INK, P["skin"], 0.2), 0.9, stroke=3.2))
        return
    up = h * 1.15
    lo = h * 0.85
    almond = skia.Path()
    almond.moveTo(cx - w, cy + 1)
    almond.cubicTo(cx - w * 0.55, cy - up * 1.25, cx + w * 0.45, cy - up * 1.3, cx + w, cy - 1)
    almond.cubicTo(cx + w * 0.5, cy + lo * 1.15, cx - w * 0.5, cy + lo * 1.2, cx - w, cy + 1)
    almond.close()
    white = (226, 222, 214) if not ghoul else (226, 220, 150)
    c.drawPath(almond, paint(mix(white, L.amb, 0.25)))
    c.save()
    c.clipPath(almond, doAntiAlias=True)
    lit_side = -L.kd[0]
    c.drawPath(almond, paint(shader=K.lin((cx + lit_side * w, cy), (cx - lit_side * w, cy), [L.lit(white) + (0.8,), L.lit(white) + (0.0,)])))
    gx, gy = gaze[0] * 10 + fx * 0.2, gaze[1] * 5
    ir = 13.0 if not ghoul else 14.0
    if E.get("white"):                                                  # empty eyes: a pale clouded iris, no pupil
        c.drawCircle(cx + gx, cy + gy, ir, paint((214, 220, 222)))
        c.drawCircle(cx + gx, cy + gy, ir, paint((160, 170, 180), 0.6, stroke=2))
    else:
        ic = P["iris"]
        c.drawCircle(cx + gx, cy + gy, ir, paint(mix(ic, INK, 0.25)))
        c.drawCircle(cx + gx, cy + gy, ir * 0.78, paint(shader=K.rad((cx + gx, cy + gy), ir, [mix(ic, WHITE, 0.25), ic, mix(ic, INK, 0.4)], [0, 0.6, 1])))
        pr = ir * 0.42 * E["pupil"]
        if ghoul:
            c.drawOval(skia.Rect.MakeLTRB(cx + gx - 2.4, cy + gy - ir * 0.8, cx + gx + 2.4, cy + gy + ir * 0.8), paint(INK))
        elif pr > 0.5:
            c.drawCircle(cx + gx, cy + gy, pr, paint(INK))
    # upper lid shadow on the eyeball
    c.drawPath(almond, paint(INK, 0.28, stroke=9, blur=4))
    c.restore()
    if ghoul:                                                           # the host's eyes glow
        g = paint((255, 220, 60), 0.55, blur=14)
        g.setBlendMode(skia.BlendMode.kPlus)
        c.drawCircle(cx + gx, cy + gy, ir * 1.4, g)
    c.drawCircle(cx + gx - 4, cy + gy - 4, 3.0, paint(WHITE, 0.95))   # catchlight
    # lash line, crease, lower lid
    lash = skia.Path()
    lash.moveTo(cx - w - 1, cy + 1)
    lash.cubicTo(cx - w * 0.55, cy - up * 1.25, cx + w * 0.45, cy - up * 1.3, cx + w + 2, cy - 2)
    c.drawPath(lash, paint(mix(INK, P["skin"], 0.12), 0.95, stroke=3.4 + P.get("lash", 1.0) * 0.8))
    if P.get("lash", 1.0) > 0 and not P.get("male"):
        for i in range(3):
            u = 0.62 + i * 0.16
            bx = cx + w * (u * 2 - 1) * (-1 if side < 0 else 1)
            by = cy - up * 1.05 * math.sin(math.pi * u) - 1
            ox = (-1 if side < 0 else 1) * (5 + i * 2) * P.get("lash", 1.0)
            c.drawLine(bx, by, bx + ox, by - 6 * P.get("lash", 1.0), paint(INK, 0.8, stroke=2.0))
    crease = K.bez_path([(cx - w * 0.85, cy - up * 0.6 - 4), (cx, cy - up * 1.6 - 9), (cx + w * 0.9, cy - up * 0.6 - 4)])
    c.drawPath(crease, paint(mix(L.amb, INK, 0.3), 0.4, stroke=2.2))
    low = K.bez_path([(cx - w * 0.8, cy + 3), (cx, cy + lo * 1.05 + 3), (cx + w * 0.85, cy + 2)])
    c.drawPath(low, paint(mix(L.amb, INK, 0.2), 0.35, stroke=2.0))
    if P.get("age", 0) > 0.35:                                          # bags and crow's feet
        bag = K.bez_path([(cx - w * 0.7, cy + lo + 9), (cx, cy + lo + 17), (cx + w * 0.8, cy + lo + 9)])
        c.drawPath(bag, paint(mix(L.amb, INK, 0.3), 0.3 * P["age"], stroke=2.2))
        ox = cx + (w + 6) * (1 if side > 0 else -1)
        for k in (-1, 0, 1):
            c.drawLine(ox, cy + k * 5, ox + (1 if side > 0 else -1) * 13, cy + k * 9, paint(mix(L.amb, INK, 0.3), 0.35 * P["age"], stroke=1.6))


def _brow(c, cx, cy, side, P, E, talk):
    bi, bo, fr = E["brow"]
    bi += talk * 0.12
    s = 1 if side > 0 else -1
    inner = (cx - s * 22, cy - 34 - bi * 16 + fr * 8)
    mid = (cx + s * 2, cy - 44 - (bi + bo) * 8 + fr * 3)
    outer = (cx + s * 30, cy - 38 - bo * 14)
    w = 9.5 if not P.get("male") else 12
    p = skia.Path()
    pts = [inner, mid, outer]
    # tapered: thick inner, thin outer
    top = [(x, y - w * (0.6 - 0.35 * i)) for i, (x, y) in enumerate(pts)]
    bot = [(x, y + w * (0.4 - 0.25 * i)) for i, (x, y) in enumerate(pts)]
    p = smooth(top + bot[::-1])
    c.drawPath(p, paint(P.get("brow", P["hair"]), 0.95))
    if P.get("ghoul"):                                                  # bristling white tufts
        for i in range(5):
            u = i / 4
            x, y = inner[0] + (outer[0] - inner[0]) * u, inner[1] + (outer[1] - inner[1]) * u - 8
            c.drawLine(x, y, x + s * 6, y - 12 - 4 * math.sin(i * 2.1), paint(P["brow"], 0.9, stroke=2.4))


def _nose(c, fx, P, L, t):
    ghoul = P.get("ghoul")
    tip_y = 58 if not ghoul else 72
    tx = fx * 1.25 + (8 if ghoul else 0) * (1 if t >= 0 else -1) * 0
    ks = -L.kd[0]
    shadow_side = -1 if ks > 0 else 1
    # the bridge shadow on the side away from the key
    side = skia.Path()
    side.moveTo(fx + shadow_side * 10, -24)
    side.quadTo(fx + shadow_side * 16, 20, tx + shadow_side * 18, tip_y - 4)
    side.lineTo(tx + shadow_side * 4, tip_y)
    side.quadTo(fx + shadow_side * 2, 18, fx + shadow_side * 4, -24)
    side.close()
    soft(c, side, mix(L.amb, (80, 30, 30), 0.3), 0.45, 6)
    # the ball of the nose and wings
    soft(c, K.oval(tx - 18, tip_y - 16, tx + 18, tip_y + 10), L.lit(P["skin"]), 0.35, 5)
    if ghoul:                                                           # a long hooked nose with a wart
        hook = skia.Path()
        hook.moveTo(fx - 8, -10)
        hook.quadTo(fx + 30, 30, tx + 14, tip_y + 14)
        hook.quadTo(tx, tip_y + 20, tx - 12, tip_y + 6)
        hook.quadTo(fx - 4, 30, fx - 8, -10)
        hook.close()
        lit_fill(c, hook, P["skin"], L, rim=0.6, rim_w=4)
        c.drawCircle(tx + 10, tip_y - 6, 6, paint(mix(P["skin"], (90, 70, 40), 0.5)))
        c.drawCircle(tx + 8, tip_y - 8, 2, paint(WHITE, 0.5))
    for s in (-1, 1):
        c.drawOval(skia.Rect.MakeLTRB(tx + s * 11 - 6, tip_y + 2, tx + s * 11 + 6, tip_y + 9), paint(mix(L.amb, (60, 20, 20), 0.5), 0.75))
    c.drawPath(K.bez_path([(tx - 18, tip_y + 2), (tx - 22, tip_y - 10), (tx - 12, tip_y - 14)]), paint(mix(L.amb, INK, 0.2), 0.4, stroke=2.2))
    c.drawPath(K.bez_path([(tx + 18, tip_y + 2), (tx + 22, tip_y - 10), (tx + 12, tip_y - 14)]), paint(mix(L.amb, INK, 0.2), 0.4, stroke=2.2))
    c.drawCircle(tx + ks * 5, tip_y - 8, 4, paint(WHITE, 0.35, blur=3))


def _mouth(c, mx, my, P, E, L, talk, T):
    smile = E["smile"]
    op = min(1.3, E["open"] + talk * (0.5 - 0.3 * E["open"]))
    wide = E["wide"]
    asym = E.get("asym", 0.0)
    mw = 36 * (1 + wide * 0.4 + max(0, smile) * 0.16) * (0.8 if P.get("male") else 1.0) * (1 + max(0.0, op - 0.85) * 0.7)
    oh = op * 80
    lc = (mx - mw, my - smile * 13 + smile * asym * 6)
    rc = (mx + mw, my - smile * 13 - smile * asym * 9)
    lips = P["lips"]
    if P.get("ghoul"):
        lips = mix(lips, (40, 20, 30), 0.3)
    th = 1.0 if not P.get("male") else 0.6                               # lip fullness
    if oh > 4:
        inner = skia.Path()
        top_y = my - oh * 0.28 - max(0, smile) * 6
        bot_y = my + oh * 0.72
        sq = 0.62 if op > 0.7 else 0.55                                  # a scream opens round, a grin opens wide
        inner.moveTo(*lc)
        inner.cubicTo(mx - mw * 0.55, top_y - 5, mx + mw * 0.55, top_y - 5, *rc)
        inner.cubicTo(mx + mw * (0.95 - sq * 0.4), bot_y + 2, mx - mw * (0.95 - sq * 0.4), bot_y + 2, *lc)
        inner.close()
        c.drawPath(inner, paint((40, 6, 14)))
        c.save()
        c.clipPath(inner, doAntiAlias=True)
        c.drawOval(skia.Rect.MakeLTRB(mx - mw * 0.5, top_y + oh * 0.2, mx + mw * 0.5, bot_y - oh * 0.05), paint((10, 0, 4), 0.9, blur=10))
        if E.get("tongue") or op > 0.45:
            c.drawOval(skia.Rect.MakeLTRB(mx - mw * 0.62, bot_y - oh * 0.42, mx + mw * 0.62, bot_y + oh * 0.3), paint((176, 40, 58)))
            c.drawLine(mx, bot_y - oh * 0.36, mx, bot_y - oh * 0.1, paint((120, 20, 36), 0.6, stroke=3))
            c.drawOval(skia.Rect.MakeLTRB(mx - mw * 0.3, bot_y - oh * 0.36, mx + mw * 0.05, bot_y - oh * 0.26), paint(WHITE, 0.3, blur=2))
        if E.get("teeth") or op > 0.18:
            tc = (240, 234, 214) if not P.get("ghoul") else (206, 194, 120)
            if P.get("ghoul"):                                          # a few crooked teeth with gaps
                for i, (u, l) in enumerate(((-0.62, 0.9), (-0.22, 1.25), (0.22, 0.75), (0.6, 1.15))):
                    x = mx + mw * u
                    c.drawPath(path([(x - 8, top_y - 8), (x + 8, top_y - 8), (x + 6 + i % 2 * 2, top_y + 14 * l), (x - 5, top_y + 16 * l)]), paint(tc))
                    c.drawPath(path([(x - 8, top_y - 8), (x + 8, top_y - 8), (x + 6 + i % 2 * 2, top_y + 14 * l), (x - 5, top_y + 16 * l)]), paint(INK, 0.4, stroke=1.4))
                for u in (-0.4, 0.35):
                    x = mx + mw * u
                    c.drawPath(path([(x - 7, bot_y + 6), (x + 7, bot_y + 6), (x + 4, bot_y - 16), (x - 5, bot_y - 13)]), paint(tc))
            else:
                tb = top_y + min(16, oh * 0.22) + 2
                c.drawRect(skia.Rect.MakeLTRB(mx - mw, top_y - 12, mx + mw, tb), paint(tc))
                for i in range(-3, 4):
                    x = mx + i * mw * 0.24
                    c.drawLine(x, top_y - 6, x, tb, paint(mix(tc, INK, 0.4), 0.45, stroke=1.4))
                c.drawRect(skia.Rect.MakeLTRB(mx - mw, tb - 3, mx + mw, tb + 1), paint(INK, 0.15))
                if op > 0.5:
                    c.drawRect(skia.Rect.MakeLTRB(mx - mw * 0.75, bot_y - 10, mx + mw * 0.75, bot_y + 4), paint(mix(tc, INK, 0.08)))
        c.drawPath(inner, paint(INK, 0.45, stroke=12, blur=6))
        c.restore()
        up = skia.Path()
        up.moveTo(lc[0] - 3, lc[1])
        up.cubicTo(mx - mw * 0.6, top_y - 16 * th, mx - 7, top_y - 17 * th, mx, top_y - 11 * th)
        up.cubicTo(mx + 7, top_y - 17 * th, mx + mw * 0.6, top_y - 16 * th, rc[0] + 3, rc[1])
        up.cubicTo(mx + mw * 0.55, top_y - 3, mx - mw * 0.55, top_y - 3, lc[0] - 3, lc[1])
        up.close()
        lo = skia.Path()
        lo.moveTo(lc[0] - 3, lc[1])
        lo.cubicTo(mx - mw * (0.95 - sq * 0.4), bot_y + 2, mx + mw * (0.95 - sq * 0.4), bot_y + 2, rc[0] + 3, rc[1])
        lo.cubicTo(mx + mw * 0.9, bot_y + 18 * th, mx - mw * 0.9, bot_y + 18 * th, lc[0] - 3, lc[1])
        lo.close()
        lit_fill(c, up, lips, L, rim=0.4, rim_w=2, edge=0.25)
        lit_fill(c, lo, lips, L, rim=0.4, rim_w=2, edge=0.25)
        c.drawOval(skia.Rect.MakeLTRB(mx - mw * 0.3, bot_y + 4, mx + mw * 0.15, bot_y + 10), paint(WHITE, 0.35, blur=2))
    else:
        mid_y = my - smile * 3
        up = skia.Path()
        up.moveTo(lc[0] - 3, lc[1])
        up.cubicTo(mx - mw * 0.6, mid_y - 14 * th, mx - 7, mid_y - 15 * th, mx, mid_y - 9 * th)
        up.cubicTo(mx + 7, mid_y - 15 * th, mx + mw * 0.6, mid_y - 14 * th, rc[0] + 3, rc[1])
        up.cubicTo(mx + mw * 0.5, mid_y + 2 - smile * 3, mx - mw * 0.5, mid_y + 2 - smile * 3, lc[0] - 3, lc[1])
        up.close()
        lo = skia.Path()
        lo.moveTo(lc[0] - 2, lc[1])
        lo.cubicTo(mx - mw * 0.5, mid_y + 2 - smile * 3, mx + mw * 0.5, mid_y + 2 - smile * 3, rc[0] + 2, rc[1])
        lo.cubicTo(mx + mw * 0.6, mid_y + 19 * th, mx - mw * 0.6, mid_y + 19 * th, lc[0] - 2, lc[1])
        lo.close()
        lit_fill(c, lo, lips, L, rim=0.4, rim_w=2, edge=0.2)
        lit_fill(c, up, mix(lips, INK, 0.12), L, rim=0.4, rim_w=2, edge=0.2)
        line = skia.Path()
        line.moveTo(lc[0] - 3, lc[1])
        line.cubicTo(mx - mw * 0.5, mid_y + 2 - smile * 3, mx + mw * 0.5, mid_y + 2 - smile * 3, rc[0] + 3, rc[1])
        c.drawPath(line, paint(mix(lips, INK, 0.7), 0.95, stroke=2.6))
        c.drawOval(skia.Rect.MakeLTRB(mx - mw * 0.35, mid_y + 7, mx + mw * 0.1, mid_y + 12), paint(WHITE, 0.35, blur=2))
    if smile > 0.3:                                                     # smile lines
        for s, cc in ((-1, lc), (1, rc)):
            c.drawPath(K.bez_path([(cc[0] + s * 4, cc[1] - 24), (cc[0] + s * 14, cc[1] - 4), (cc[0] + s * 7, cc[1] + 12)]),
                       paint(mix(L.amb, INK, 0.3), 0.32 * smile, stroke=2.6))

def _hair_back(c, P, L, T, t):
    st, hc = P["style"], P["hair"]
    p = None
    if st == "bob":
        p = smooth([(-150, -60), (-140, -150), (-90, -200), (0, -214), (90, -200), (140, -150), (150, -60), (150, 70), (130, 128), (60, 132),
                    (-60, 132), (-130, 128), (-150, 70)])
    elif st == "big":                                                   # 1980s volume: high on top, wide at the sides, to the shoulders
        p = smooth([(0, -262), (110, -246), (196, -180), (232, -70), (236, 50), (214, 160), (170, 236), (110, 250), (100, 160), (-100, 160),
                    (-110, 250), (-170, 236), (-214, 160), (-236, 50), (-232, -70), (-196, -180), (-110, -246)])
    elif st == "curls":
        p = skia.Path()
        rng = K.rng_at(7, 1)
        for i in range(30):
            a = math.pi * 2 * i / 30
            if math.sin(a) > 0.55:
                continue
            p.addCircle(165 * math.cos(a), -70 + 170 * math.sin(a), 52 + rng.uniform(-8, 10))
        p.addOval(skia.Rect.MakeLTRB(-170, -240, 170, 60))
        p = skia.Op(p, skia.Path(), skia.PathOp.kUnion_PathOp) or p
    elif st == "pony":
        p = smooth([(-120, -40), (-118, -150), (-60, -192), (0, -200), (60, -192), (118, -150), (120, -40), (100, 20), (-100, 20)])
        tail = smooth([(90, -120), (170, -60), (190, 80), (170, 260), (130, 330), (120, 200), (130, 40), (80, -60)])
        lit_fill(c, tail, hc, L, rim=1.0, rim_w=6)
        _strands(c, tail, hc, L, 14, seed=4)
    elif st == "wild":                                                  # a matted grey-white mane with strings flying loose
        rng = K.rng_at(3, 9)
        pts = []
        n = 30
        for i in range(n):
            a = -math.pi / 2 + 2 * math.pi * i / n
            tuft = 1.0 + 0.07 * math.sin(i * 2.3) + rng.uniform(-0.04, 0.04) + 0.02 * math.sin(T * 1.7 + i)
            x = math.cos(a) * 220 * tuft
            y = -50 + math.sin(a) * 250 * tuft
            if math.sin(a) > 0.3:
                x *= 1.12
                y = min(y, 320 + 24 * math.sin(i * 1.3))
            pts.append((x, y))
        p = smooth(pts)
        for i in range(44):                                             # loose strings beyond the mass
            a = -math.pi / 2 + rng.uniform(-1.7, 1.7)
            r0 = rng.uniform(150, 210)
            x0, y0 = math.cos(a) * r0, -50 + math.sin(a) * r0 * 1.1
            L0 = rng.uniform(60, 150)
            sway = math.sin(T * 1.4 + i) * 8
            x1, y1 = x0 + math.cos(a) * L0 + sway, y0 + math.sin(a) * L0 * 0.8 + L0 * 0.5
            c.drawPath(K.bez_path([(x0, y0), ((x0 + x1) / 2 + rng.uniform(-20, 20), (y0 + y1) / 2 - 10), (x1, y1)]),
                       paint(mix(L.lit(hc), L.shade(hc), rng.uniform(0, 0.6)), 0.8, stroke=rng.uniform(2.5, 5)))
    elif st == "hood":                                                  # a peaked hood over a matted grey mane
        hood = smooth([(0, -300), (70, -250), (160, -150), (196, -20), (210, 140), (250, 300), (-250, 300), (-210, 140), (-196, -20),
                       (-160, -150), (-70, -250)])
        lit_fill(c, hood, P["hood"], L, rim=1.0, rim_w=7, round_=True)
        c.save()
        c.clipPath(hood, doAntiAlias=True)
        for i in range(7):
            x = -180 + i * 60
            c.drawPath(K.bez_path([(x * 0.3, -280), (x * 0.8, -60), (x * 1.2, 300)]), paint(mix(P["hood"], INK, 0.55), 0.45, stroke=7))
        c.restore()
        inner = smooth([(0, -232), (110, -170), (150, -40), (150, 160), (-150, 160), (-150, -40), (-110, -170)])
        c.drawPath(inner, paint(mix(P["hood"], INK, 0.8)))
        rng = K.rng_at(3, 9)
        mane = smooth([(-136, -60), (-118, -176), (-50, -216), (50, -216), (118, -176), (136, -60), (140, 80), (120, 150), (-120, 150),
                       (-140, 80)])
        lit_fill(c, mane, mix(hc, P["hood"], 0.45), L, rim=0.5, rim_w=5, round_=True, k=0.55)
        soft(c, K.oval(-130, -60, 130, 200), mix(P["hood"], INK, 0.8), 0.7, 30, clip=mane)
        _strands(c, mane, hc, L, 50, seed=11)
        for i in range(26):                                             # straggles spilling out over the hood
            sd = -1 if i % 2 else 1
            x0 = sd * rng.uniform(110, 150)
            y0 = rng.uniform(-150, 120)
            L0 = rng.uniform(70, 170)
            sway = math.sin(T * 1.4 + i) * 7
            c.drawPath(K.bez_path([(x0, y0), (x0 + sd * rng.uniform(10, 40), y0 + L0 * 0.5), (x0 + sd * rng.uniform(0, 50) + sway, y0 + L0)]),
                       paint(mix(L.lit(hc), L.shade(hc), rng.uniform(0, 0.5)), 0.85, stroke=rng.uniform(2.5, 5)))
        p = None
    elif st == "thin":
        p = smooth([(-126, -40), (-120, -140), (-70, -178), (0, -186), (70, -178), (120, -140), (126, -40), (110, 30), (-110, 30)])
    elif st == "bun":
        p = smooth([(-118, -40), (-116, -150), (-60, -188), (0, -196), (60, -188), (116, -150), (118, -40), (100, 0), (-100, 0)])
    if p is not None:
        lit_fill(c, p, hc, L, rim=1.0, rim_w=6, round_=True)
        _strands(c, p, hc, L, 26 if st != "wild" else 60, seed=1)


def _strands(c, p, hc, L, n, seed=0):
    b = p.computeTightBounds()
    rng = K.rng_at(seed, 5)
    c.save()
    c.clipPath(p, doAntiAlias=True)
    for i in range(n):
        x = rng.uniform(b.left(), b.right())
        y = rng.uniform(b.top(), b.bottom() - 40)
        c.drawPath(K.bez_path([(x, y), (x + rng.uniform(-20, 20), y + 40), (x + rng.uniform(-30, 30), y + rng.uniform(70, 120))]),
                   paint(mix(L.lit(hc), WHITE, 0.15) if i % 3 else mix(L.shade(hc), INK, 0.3), 0.35, stroke=rng.uniform(1.5, 3.0)))
    c.restore()


def _hair_front(c, P, L, T, t, fx):
    st, hc = P["style"], P["hair"]
    if st == "bob":                                                     # a full fringe and side panels to the jaw
        fr = smooth([(-128, -40), (-122, -142), (-60, -186), (10, -190), (80, -176), (126, -134), (130, -40), (112, -78), (96, -88),
                     (60, -86), (24, -92), (-10, -86), (-50, -90), (-90, -84), (-112, -74)])
        lit_fill(c, fr, hc, L, rim=1.0, rim_w=5)
        _strands(c, fr, hc, L, 20, seed=2)
        for s in (-1, 1):
            side = smooth([(s * 104, -90), (s * 132, -40), (s * 140, 60), (s * 128, 122), (s * 104, 126), (s * 100, 40), (s * 96, -40)])
            lit_fill(c, side, hc, L, rim=1.0, rim_w=5)
    elif st == "big":                                                   # a side-swept 1980s fringe, feathered back
        fr = smooth([(-126, -70), (-112, -170), (-40, -214), (60, -212), (128, -160), (136, -80), (110, -110), (60, -130), (0, -116),
                     (-60, -100), (-104, -80)])
        lit_fill(c, fr, hc, L, rim=1.0, rim_w=6, round_=True)
        _strands(c, fr, hc, L, 26, seed=3)
    elif st == "curls":
        rng = K.rng_at(8, 2)
        pts = [(-124, -40), (-130, -150), (-70, -206), (0, -216), (70, -206), (130, -150), (124, -40)]
        for i in range(13):                                             # the hairline: little bumps of curl
            u = 1 - i / 12
            x = -112 + 224 * u
            y = -96 - 26 * math.sin(u * math.pi) + (8 if i % 2 else -4) + rng.uniform(-3, 3)
            pts.append((x, y))
        fr = smooth(pts)
        lit_fill(c, fr, hc, L, rim=1.0, rim_w=6, round_=True)
        c.save()
        c.clipPath(fr, doAntiAlias=True)
        for i in range(60):
            x, y = rng.uniform(-140, 140), rng.uniform(-220, -90)
            c.drawCircle(x, y, rng.uniform(5, 11), paint(mix(L.lit(hc), WHITE, 0.25), 0.3, stroke=2))
        c.restore()
    elif st == "cap":                                                   # a surgical cap, ties at the back
        cap = smooth([(-122, -50), (-124, -150), (-64, -200), (10, -206), (80, -194), (124, -148), (124, -50), (90, -74), (0, -82), (-90, -74)])
        lit_fill(c, cap, P["cap"], L, rim=1.0, rim_w=5)
        c.save()
        c.clipPath(cap, doAntiAlias=True)
        for i in range(6):
            c.drawPath(K.bez_path([(-110 + i * 40, -190), (-100 + i * 42, -130), (-104 + i * 44, -70)]), paint(mix(P["cap"], INK, 0.35), 0.4, stroke=3))
        c.restore()
        c.drawPath(K.bez_path([(-122, -60), (0, -90), (124, -60)]), paint(mix(P["cap"], WHITE, 0.3), 0.8, stroke=5))
        for s in (-1, 1):                                               # a few strands escaping
            c.drawPath(K.bez_path([(s * 100, -72), (s * 118, -30), (s * 108, 10)]), paint(hc, 0.85, stroke=4))
    elif st == "pony":
        fr = smooth([(-120, -40), (-118, -150), (-60, -196), (10, -204), (80, -188), (120, -146), (122, -50), (100, -100), (40, -120),
                     (-30, -112), (-90, -96)])
        lit_fill(c, fr, hc, L, rim=1.0, rim_w=6)
        _strands(c, fr, hc, L, 14, seed=6)
    elif st == "bun":
        fr = smooth([(-114, -60), (-114, -150), (-60, -192), (0, -198), (60, -192), (114, -150), (114, -60), (80, -110), (0, -126), (-80, -110)])
        lit_fill(c, fr, hc, L, rim=1.0, rim_w=6)
        _strands(c, fr, hc, L, 16, seed=7)
        bun = K.circle(0, -214, 52)
        lit_fill(c, bun, hc, L, rim=1.0, rim_w=6)
        _strands(c, bun, hc, L, 10, seed=8)
    elif st == "thin":
        rng = K.rng_at(4, 4)
        for i in range(36):
            a = rng.uniform(-math.pi, 0)
            x0, y0 = 90 * math.cos(a), -110 + 70 * math.sin(a)
            c.drawPath(K.bez_path([(x0, y0), (x0 * 1.3 + rng.uniform(-10, 10), y0 - 20), (x0 * 1.5 + rng.uniform(-30, 30), y0 + rng.uniform(-10, 40))]),
                       paint(L.lit(hc), 0.55, stroke=2.2))
    elif st == "bald":
        for s in (-1, 1):
            fr = smooth([(s * 100, -110), (s * 124, -60), (s * 122, 10), (s * 106, 30), (s * 98, -40), (s * 92, -96)])
            lit_fill(c, fr, hc, L, rim=1.0, rim_w=5)
        c.drawOval(skia.Rect.MakeLTRB(-40 - L.kd[0] * 30, -150, 30 - L.kd[0] * 30, -120), paint(WHITE, 0.25, blur=8))
    elif st == "wild":
        rng = K.rng_at(5, 5)
        fr = skia.Path()
        for i in range(16):
            x0 = rng.uniform(-100, 100)
            side = -1 if x0 < 0 else 1
            x1 = x0 + side * rng.uniform(20, 70)
            fr.addPath(K.capsule(x0 * 0.6, -175, x1, -96 + rng.uniform(-10, 20), rng.uniform(16, 26), 4))
        for s_ in (-1, 1):                                              # long locks down past the cheeks
            for j in range(3):
                x0 = s_ * (92 + j * 12)
                sw = math.sin(T * 1.2 + j + s_) * 6
                fr.addPath(K.capsule(x0, -150, x0 + s_ * (8 + j * 10) + sw, 120 + j * 40, 22, 5))
        fr = skia.Op(fr, skia.Path(), skia.PathOp.kUnion_PathOp) or fr
        lit_fill(c, fr, hc, L, rim=1.0, rim_w=5)
        _strands(c, fr, hc, L, 30, seed=9)
    elif st == "hood":
        rng = K.rng_at(5, 5)
        fr = skia.Path()
        for s_ in (-1, 1):                                              # a centre parting, hanks falling over the temples
            for j in range(4):
                sw = math.sin(T * 1.2 + j + s_) * 5
                fr.addPath(K.capsule(s_ * (8 + j * 18), -200, s_ * (88 + j * 14) + sw, -60 + j * 36, 24, 8))
        fr = skia.Op(fr, skia.Path(), skia.PathOp.kUnion_PathOp) or fr
        lit_fill(c, fr, hc, L, rim=1.0, rim_w=5, round_=True)
        _strands(c, fr, hc, L, 30, seed=9)
        rimp = K.bez_path([(-176, 120), (-170, -150), (0, -262)])
        rimq = K.bez_path([(176, 120), (170, -150), (0, -262)])
        for q in (rimp, rimq):
            c.drawPath(q, paint(mix(P["hood"], WHITE, 0.15), 0.8, stroke=14))
            c.drawPath(q, paint(INK, 0.35, stroke=3))


def head(c, P, E, L, T, talk=0.0, blink=0.0, gaze=(0.0, 0.0), turn=0.0):
    """The head in local coordinates (centre 0, 0; 300 tall). Draws hair, ears, face, features."""
    fx = turn * 34
    _hair_back(c, P, L, T, turn)
    for s in (-1, 1):                                                   # ears
        ex = s * (106 - turn * s * 14)
        ear = K.oval(ex - 18, -34, ex + 18, 40)
        lit_fill(c, ear, P["skin"], L, rim=0.8, rim_w=4)
        if P.get("ghoul"):
            tip = path([(ex - s * 4, -30), (ex + s * 30, -66), (ex + s * 14, -10)])
            lit_fill(c, tip, P["skin"], L, rim=0.8, rim_w=3)
    op = min(1.3, E["open"] + talk * (0.5 - 0.3 * E["open"]))
    drop = max(0.0, op - 0.35) * 46
    face = _face_path(P, turn, drop)
    lit_fill(c, face, P["skin"], L, rim=1.0, rim_w=6, soft=0.85, round_=True)
    c.save()
    c.clipPath(face, doAntiAlias=True)
    # modelling: temples, cheekbones, under-chin, a warm blush
    for s in (-1, 1):
        soft(c, K.oval(s * 70 - 30 + fx, 34, s * 70 + 30 + fx, 76), (220, 90, 90), 0.16 if not P.get("ghoul") else 0.0, 14)
        if P.get("ghoul") or P.get("age", 0) > 0.6:                     # hollow cheeks
            soft(c, K.oval(s * 78 - 26 + fx, 40, s * 78 + 22 + fx, 104), mix(L.amb, INK, 0.4), 0.45 if P.get("ghoul") else 0.18, 12)
    soft(c, K.oval(-120, 120, 120, 200), mix(L.amb, INK, 0.3), 0.35, 16)
    if P.get("freckles"):
        rng = K.rng_at(2, 2)
        for _ in range(26):
            s = rng.choice([-1, 1])
            c.drawCircle(s * rng.uniform(26, 70) + fx, rng.uniform(22, 56), rng.uniform(1.2, 2.4), paint((160, 90, 60), 0.4))
    if P.get("ghoul"):                                                  # mottled grave-skin, veins
        rng = K.rng_at(6, 6)
        for _ in range(16):
            x, y = rng.uniform(-100, 100), rng.uniform(-140, 140)
            c.drawCircle(x, y, rng.uniform(8, 22), paint(mix(P["skin"], (70, 90, 60), 0.5), 0.25, blur=8))
        for s in (-1, 1):
            c.drawPath(K.bez_path([(s * 60, -130), (s * 74, -100), (s * 66, -76)]), paint((80, 60, 120), 0.35, stroke=2))
    age = P.get("age", 0)
    if age > 0.5:                                                       # forehead lines, folds from nose to mouth
        for k in range(3):
            y = -92 + k * 14
            c.drawPath(K.bez_path([(-50 + fx, y), (fx, y - 6), (50 + fx, y)]), paint(mix(L.amb, INK, 0.3), 0.22 * age, stroke=2))
    if age > 0.25 or E["smile"] > 0.5:
        for s in (-1, 1):
            c.drawPath(K.bez_path([(fx + s * 26, 50), (fx + s * 44, 80), (fx + s * 42, 114)]), paint(mix(L.amb, INK, 0.3), 0.3 * max(age, 0.5), stroke=2.4))
    c.restore()
    eye_y = -6
    for s in (-1, 1):
        _brow(c, s * 44 + fx, eye_y, s, P, E, talk)
        _eye(c, s * 44 + fx, eye_y, s, P, E, L, blink, gaze, T, fx)
    _nose(c, fx, P, L, turn)
    _mouth(c, fx * 1.1, (98 if not P.get("ghoul") else 112) + drop * 0.35, P, E, L, talk, T)
    if P.get("ghoul"):                                                  # a chin wart with a hair
        c.drawCircle(fx + 22, 150 + drop, 5, paint(mix(P["skin"], (90, 70, 40), 0.5)))
        c.drawLine(fx + 22, 146 + drop, fx + 30, 136 + drop, paint(INK, 0.7, stroke=1.4))
    if E.get("sweat"):
        for (sx, sy) in ((-86, -96), (92, -70), (-96, 10)):
            dr = skia.Path()
            dr.moveTo(sx + fx, sy)
            dr.quadTo(sx + fx + 9, sy + 18, sx + fx, sy + 22)
            dr.quadTo(sx + fx - 9, sy + 18, sx + fx, sy)
            c.drawPath(dr, paint((200, 230, 255), 0.85))
            c.drawPath(dr, paint(INK, 0.6, stroke=1.6))
    _hair_front(c, P, L, T, turn, fx)
    if P.get("glasses"):
        for s in (-1, 1):
            r = skia.Rect.MakeLTRB(s * 44 + fx - 34, eye_y - 26, s * 44 + fx + 34, eye_y + 24)
            c.drawRoundRect(r, 14, 14, paint(WHITE, 0.08))
            c.drawRoundRect(r, 14, 14, paint((40, 30, 30), 0.95, stroke=4.5))
            c.drawLine(s * 44 + fx - 20, eye_y - 18, s * 44 + fx - 4, eye_y - 6, paint(WHITE, 0.5, stroke=3))
        c.drawLine(fx - 10, eye_y - 4, fx + 10, eye_y - 4, paint((40, 30, 30), 0.95, stroke=4))
        if P["style"] == "bun":                                         # a chain to hang them from
            c.drawPath(K.bez_path([(fx - 78, eye_y), (-110, 120), (-90, 240)]), paint((200, 170, 90), 0.7, stroke=2))
    if P.get("mask"):                                                   # surgical mask pulled down to the throat
        m = smooth([(-74, 150 + drop), (0, 146 + drop), (74, 150 + drop), (68, 176 + drop), (0, 184 + drop), (-68, 176 + drop)])
        lit_fill(c, m, (150, 196, 204), L, rim=0.4, rim_w=3, k=0.7)
        c.drawLine(-60, 164 + drop, 60, 164 + drop, paint(mix((150, 200, 210), INK, 0.3), 0.4, stroke=2))
        for s_ in (-1, 1):
            c.drawLine(s_ * 72, 156 + drop, s_ * 104, 30, paint((230, 240, 240), 0.7, stroke=2.5))
    return face


# ------------------------------------------------------------------ the body

def torso(c, P, L, T, breath=0.0, wide=1.0):
    """Neck, shoulders and chest down to the bottom of the frame, in local head coordinates."""
    top, kind = P["top"], P.get("neck", "sweater")
    br = breath * 4
    neck = smooth([(-44, 100), (44, 100), (50, 200), (66, 236), (-66, 236), (-50, 200)])
    lit_fill(c, neck, P["skin"], L, rim=0.8, rim_w=5)
    soft(c, K.oval(-60, 96, 60, 170), mix(L.amb, INK, 0.4), 0.55, 14, clip=neck)
    sw = 230 * wide
    body = smooth([(-60, 220 - br), (-sw + 30, 250 - br), (-sw - 10, 330), (-sw - 30, 600), (-sw - 40, 1100), (sw + 40, 1100), (sw + 30, 600),
                   (sw + 10, 330), (sw - 30, 250 - br), (60, 220 - br), (0, 240)])
    if kind == "shawl":                                                 # the host's ragged shawl, fringed
        lit_fill(c, body, top, L, rim=1.0, rim_w=5)
        rng = K.rng_at(1, 1)
        c.save()
        c.clipPath(body, doAntiAlias=True)
        for i in range(12):
            x = -sw + i * sw / 6
            c.drawPath(K.bez_path([(x, 240), (x + 30, 500), (x - 10, 1000)]), paint(mix(top, INK, 0.5), 0.5, stroke=6))
        c.restore()
        for s in (-1, 1):
            flap = smooth([(s * 50, 230), (s * 160, 300), (s * 120, 620), (s * 30, 760), (s * 10, 500)])
            lit_fill(c, flap, mix(top, (120, 40, 60), 0.4), L, rim=1.0, rim_w=6)
        brooch = K.circle(0, 300, 22)
        c.drawPath(brooch, paint((40, 200, 90)))
        c.drawPath(brooch, paint((200, 160, 60), stroke=6))
        return body
    lit_fill(c, body, top, L, rim=1.0, rim_w=5)
    c.save()
    c.clipPath(body, doAntiAlias=True)
    if kind in ("scrubs",):                                             # a V-neck and a pocket
        v = path([(-62, 226), (0, 330), (62, 226), (70, 214), (0, 300), (-70, 214)])
        vneck = path([(-56, 228), (0, 322), (56, 228)])
        c.drawPath(vneck, paint(P["skin"]))
        lit_fill(c, vneck, P["skin"], L, rim=0.5, rim_w=4)
        soft(c, vneck, mix(L.amb, INK, 0.3), 0.4, 10)
        c.drawPath(path([(-62, 226), (0, 330), (62, 226)], closed=False), paint(mix(top, INK, 0.35), 0.9, stroke=8))
        c.drawRect(skia.Rect.MakeLTRB(-170, 420, -80, 520), paint(mix(top, INK, 0.3), 0.6, stroke=4))
    elif kind == "cardigan":
        c.drawPath(path([(-48, 230), (-30, 1100), (30, 1100), (48, 230), (0, 270)]), paint(mix(top, WHITE, 0.55)))
        lit_fill(c, path([(-48, 230), (-30, 1100), (30, 1100), (48, 230), (0, 270)]), (236, 226, 210), L, rim=0.4, rim_w=4)
        for s in (-1, 1):
            c.drawPath(path([(s * 52, 226), (s * 34, 1100)], closed=False), paint(mix(top, INK, 0.4), 0.9, stroke=10))
        for k in range(4):
            c.drawCircle(42, 360 + k * 110, 9, paint((230, 210, 160)))
            c.drawCircle(42, 360 + k * 110, 9, paint(INK, 0.6, stroke=2))
    elif kind == "sweater":
        c.drawPath(K.bez_path([(-70, 228), (0, 262), (70, 228)]), paint(mix(top, INK, 0.35), 0.95, stroke=16))
        for k in range(10):
            x = -sw + k * sw / 4.5
            c.drawLine(x, 300, x + 20, 1100, paint(mix(top, INK, 0.25), 0.25, stroke=5))
    elif kind == "gown":                                                # an academic gown over a high collar
        c.drawPath(path([(-56, 226), (-90, 1100), (90, 1100), (56, 226), (0, 250)]), paint((236, 236, 240)))
        lit_fill(c, path([(-56, 226), (-90, 1100), (90, 1100), (56, 226), (0, 250)]), (226, 226, 232), L, rim=0.4)
        for s in (-1, 1):
            c.drawPath(path([(s * 60, 226), (s * 110, 1100)], closed=False), paint(mix(top, INK, 0.5), 0.9, stroke=14))
    elif kind == "gown_dots":                                           # a hospital gown with a little print
        rng = K.rng_at(3, 3)
        for _ in range(60):
            c.drawCircle(rng.uniform(-sw, sw), rng.uniform(260, 1000), 5, paint(mix(top, (40, 80, 140), 0.5), 0.6))
        c.drawPath(K.bez_path([(-70, 226), (0, 256), (70, 226)]), paint(mix(top, INK, 0.3), 0.8, stroke=8))
    elif kind == "fur":                                                 # a black coat with a fur collar
        rng = K.rng_at(4, 4)
        col_ = skia.Path()
        for i in range(26):
            a = math.pi * (i / 25)
            col_.addCircle(-math.cos(a) * 150, 250 + math.sin(a) * 60 - 20, 38 + rng.uniform(-6, 6))
        col_ = skia.Op(col_, skia.Path(), skia.PathOp.kUnion_PathOp) or col_
        lit_fill(c, col_, (150, 120, 90), L, rim=1.0, rim_w=6)
        for _ in range(60):
            x, y = rng.uniform(-180, 180), rng.uniform(200, 320)
            c.drawLine(x, y, x + rng.uniform(-8, 8), y + 14, paint((60, 40, 30), 0.5, stroke=2))
    c.restore()
    if P.get("pearls"):
        for i in range(17):
            u = i / 16
            x = -70 + 140 * u
            y = 236 + 46 * math.sin(math.pi * u)
            c.drawCircle(x, y, 9, paint((236, 230, 220)))
            c.drawCircle(x - 3, y - 3, 3, paint(WHITE, 0.9))
            c.drawCircle(x, y, 9, paint((120, 110, 100), 0.6, stroke=1.4))
    return body


def bust(c, who, x, y, s, T, expr="neutral", talk=0.0, blink=0.0, gaze=(0.0, 0.0), turn=0.0, tilt=0.0, light="lamp", body=True,
         breath=None, shake=0.0, P=None, wide=1.0, before_head=None, after=None):
    """A character, head and shoulders. Returns the head centre in canvas coordinates."""
    P = dict(CAST[who]) if P is None else P
    E = dict(EXPR[expr]) if isinstance(expr, str) else expr
    L = light if isinstance(light, Light) else Light(light)
    if breath is None:
        breath = math.sin(T * 2.1 + hash(who) % 7)
    if shake:
        rng = np.random.default_rng(int(T * 24))
        x += rng.uniform(-shake, shake)
        y += rng.uniform(-shake, shake)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    if body:
        torso(c, P, L, T, breath, wide)
    if before_head:
        before_head(c, L)
    c.save()
    c.translate(0, 190)
    c.rotate(tilt + (E.get("tilt", 0.0)))
    c.translate(0, -190)
    if E.get("tendons"):
        for sd in (-1, 1):
            c.drawPath(K.capsule(sd * 30, 130, sd * 46, 240, 14, 10), paint(mix(P["skin"], INK, 0.25), 0.45, blur=4))
    head(c, P, E, L, T, talk, blink, gaze, turn)
    if after:
        after(c, L)
    c.restore()
    c.restore()
    return x, y


# ------------------------------------------------------------------ hands

def hand(c, x, y, s, ang, skin=(234, 192, 164), light="lamp", pose="open", nails=None, bony=False, flip=False):
    """A hand at the wrist (x, y), pointing along ang (degrees, 0 = right). Poses: open, grip, point, claw."""
    L = light if isinstance(light, Light) else Light(light)
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, -s if flip else s)
    palm = smooth([(0, -26), (44, -34), (78, -30), (86, 0), (78, 30), (40, 34), (0, 24)])
    lit_fill(c, palm, skin, L, rim=0.7, rim_w=4)
    fingers = []
    if pose == "open":
        fingers = [((78, -26), 74, -12), ((86, -9), 84, -3), ((86, 9), 80, 4), ((78, 24), 66, 12)]
    elif pose == "claw":
        fingers = [((78, -26), 96, -26), ((86, -9), 108, -10), ((86, 9), 104, 8), ((78, 24), 92, 26)]
    elif pose == "point":
        fingers = [((84, -12), 88, -4), ((80, 4), 30, 60), ((76, 16), 28, 70), ((70, 26), 26, 80)]
    elif pose == "grip":
        fingers = [((80, -24), 40, 70), ((86, -8), 42, 80), ((84, 8), 40, 86), ((76, 22), 36, 92)]
    w = 17 if not bony else 12
    for i, ((fx, fy), L0, bend) in enumerate(fingers):
        a1 = math.radians(bend * 0.5)
        mx, my = fx + L0 * 0.55 * math.cos(a1), fy + L0 * 0.55 * math.sin(a1)
        a2 = math.radians(bend)
        tx, ty = mx + L0 * 0.5 * math.cos(a2), my + L0 * 0.5 * math.sin(a2)
        f = skia.Path()
        f.addPath(K.capsule(fx, fy, mx, my, w, w * 0.92))
        f.addPath(K.capsule(mx, my, tx, ty, w * 0.92, w * 0.8))
        lit_fill(c, f, skin, L, rim=0.7, rim_w=3)
        if bony:
            c.drawCircle(mx, my, w * 0.5, paint(mix(skin, WHITE, 0.25), 0.5))
        if nails or bony:
            nc = nails or (60, 20, 40)
            tip = (tx + 16 * math.cos(a2), ty + 16 * math.sin(a2)) if bony else (tx + 3 * math.cos(a2), ty + 3 * math.sin(a2))
            c.drawPath(path([(tx - 6 * math.sin(a2), ty + 6 * math.cos(a2)), tip, (tx + 6 * math.sin(a2), ty - 6 * math.cos(a2))]), paint(nc))
    thumb = skia.Path()
    if pose in ("grip",):
        thumb.addPath(K.capsule(30, -26, 60, -56, 20, 16))
        thumb.addPath(K.capsule(60, -56, 86, -50, 16, 14))
    else:
        thumb.addPath(K.capsule(30, -26, 54, -60, 20, 16))
        thumb.addPath(K.capsule(54, -60, 80, -78, 16, 13))
    lit_fill(c, thumb, skin, L, rim=0.7, rim_w=3)
    c.restore()


def arm(c, sx, sy, hx, hy, w0, w1, sleeve, L, bend=1.0):
    """A sleeve from the shoulder (sx, sy) to the wrist (hx, hy), the elbow bowed out to one side."""
    L = L if isinstance(L, Light) else Light(L)
    mx, my = (sx + hx) / 2, (sy + hy) / 2
    dx, dy = hx - sx, hy - sy
    n = math.hypot(dx, dy) + 1e-6
    ex, ey = mx - dy / n * 60 * bend, my + dx / n * 60 * bend
    p = skia.Path()
    p.addPath(K.capsule(sx, sy, ex, ey, w0, (w0 + w1) / 2))
    p.addPath(K.capsule(ex, ey, hx, hy, (w0 + w1) / 2, w1))
    p = skia.Op(p, skia.Path(), skia.PathOp.kUnion_PathOp) or p
    lit_fill(c, p, sleeve, L, rim=1.0, rim_w=5)
    return ex, ey

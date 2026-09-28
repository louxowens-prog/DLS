"""The cast.

Live action (flat, over-lit, keyed in on a cheap green screen, moving smoothly at 24 fps):
  the family - Grandpa, Papa, Mama, and the narrator (the youngest daughter) - deadpan, posable arms.
Early CGI (glossy plastic): the claims machine, CLAIM-O-MATIC 2000.
Claymation (on twos, boiling): the little error (a one-eyed clay creature), the crow, the corpses, the tombstones,
the FRAUD envelopes, the disaster models.
"""
import math

import numpy as np
import skia

import kk
from kk import (BLOOD, CREAM, GORE, HOT, INK, KEY, LEMON, LILAC, MINT, ORANGE, PINK, SKIN, WHITE, W, H, bez, boil,
                clay_ellipse, clay_eye, clay_path, clay_poly, clay_shadow, lin, mix, paint, path, rad, smooth, twos)

# ------------------------------------------------------------------ the family (live action, keyed)

LOOKS = {
    "grandpa": dict(top=(150, 90, 50), bottom=(120, 120, 130), hair="bald", hair_c=(245, 245, 245), glasses="round",
                    mustache=True, h=0.93),
    "papa": dict(top=(110, 115, 140), bottom=(60, 60, 75), hair="side", hair_c=(30, 25, 25), glasses="square", tie=(220, 30, 50),
                 h=1.0),
    "mama": dict(top=(255, 215, 40), bottom=(255, 215, 40), hair="perm", hair_c=(120, 60, 30), apron=(255, 130, 190),
                 pearls=True, skirt=True, lips=True, h=0.95),
    "girl": dict(top=(250, 250, 255), bottom=(40, 50, 110), hair="bob", hair_c=(20, 15, 25), sailor=True, skirt=True, h=0.9),
}

POSES = {                     # (left shoulder, left elbow, right shoulder, right elbow) in degrees; 0 = hanging down
    "stand": (8, 0, 8, 0), "wave": (8, 0, 150, 30), "arms_up": (160, 10, 160, 10), "arms_out": (92, 0, 92, 0),
    "shrug": (40, 110, 40, 110), "point": (8, 0, 120, 0), "hips": (35, 120, 35, 120), "clasp": (25, 95, 25, 95),
}


def dance_pose(T, beat, style="kayo", k=0):
    """Arms on the beat: kayo = hand-jive sway, disco = point up / point down, show = jazz hands / kicks."""
    ph = (T / beat + k * 0.5) % 2.0
    s = math.sin(ph * math.pi)
    if style == "disco":
        up = int(T / beat + k) % 2 == 0
        return (20, 10, 150, 0) if up else (150, 0, 30, 20)
    if style == "show":
        return (120 + 30 * s, 20, 120 - 30 * s, 20)
    return (60 + 40 * s, 60 + 30 * s, 60 - 40 * s, 60 - 30 * s)


def _limb(F, x, y, sh, el, L1, L2, side, color, w, hand=SKIN, flip=1):
    a1 = math.radians(sh) * side * flip
    ex, ey = x + L1 * math.sin(a1), y + L1 * math.cos(a1)
    a2 = a1 + math.radians(el) * side * flip
    hx, hy = ex + L2 * math.sin(a2), ey + L2 * math.cos(a2)
    F.stroke(path([(x, y), (ex, ey), (hx, hy)], closed=False), color, w)
    F.circle(hx, hy, w * 0.55, hand)
    return hx, hy


def person(c, who, x, y, s, T, pose="stand", mood="flat", tilt=0.0, bob=0.0, spin=1.0, look=0.0, blink=True, halo=7.0,
           prop=None, bow=0.0, back=False):
    """A family member keyed into the shot. (x, y) = feet; ~900 px tall at s=1. pose: a name or 4 angles."""
    L = LOOKS[who]
    arms = POSES[pose] if isinstance(pose, str) else pose
    hs = L["h"]
    c.save()
    c.translate(x, y - bob)
    c.scale(s * spin, s)
    c.scale(hs, hs)
    if tilt:                                                         # lean at the hips
        c.translate(0, -380)
        c.rotate(tilt)
        c.translate(0, 380)
    if bow:                                                          # a bow toward camera: the top half folds down
        c.translate(0, -380)
        c.scale(1, 1 - 0.42 * bow)
        c.translate(0, 380)
    top, bot = L["top"], L["bottom"]
    over = lambda cc: mix(cc, WHITE, 0.35)                              # the over-lit top light
    with kk.keyed(c, halo=halo) as F:
        if L.get("skirt"):
            F.poly([(-120, -380), (120, -380), (150, -170), (-150, -170)], bot)
            for sx in (-1, 1):
                F.rrect(sx * 55 - 26, -180, sx * 55 + 26, -10, 18, SKIN)
        else:
            for sx in (-1, 1):
                F.rrect(sx * 55 - 38, -390, sx * 55 + 38, -10, 22, bot)
        for sx in (-1, 1):
            F.oval(sx * 60 - 50, -30, sx * 60 + 45, 12, (40, 30, 30))
        F.rrect(-115, -700, 115, -370, 50, top)
        F.rrect(-105, -700, 105, -640, 40, over(top))
        if L.get("apron"):
            F.rrect(-85, -610, 85, -250, 24, L["apron"])
        if L.get("sailor"):
            F.poly([(-110, -690), (110, -690), (70, -600), (0, -560), (-70, -600)], (30, 40, 100))
            F.poly([(-25, -600), (25, -600), (0, -540)], (220, 30, 50))
        if L.get("tie"):
            F.poly([(-40, -700), (40, -700), (0, -620)], WHITE)
            F.poly([(-14, -690), (14, -690), (22, -520), (0, -490), (-22, -520)], L["tie"])
        shx, shy = 105, -670
        prop_hand = None
        for i, side in enumerate((-1, 1)):
            sh, el = arms[2 * i], arms[2 * i + 1]
            hxy = _limb(F, side * shx, shy, sh, el, 150, 140, side, top, 46)
            if i == 1:
                prop_hand = hxy
        F.circle(0, -800, 100, SKIN)
        hair = L["hair_c"]
        if L["hair"] == "bald":
            for sx in (-1, 1):
                F.oval(sx * 95 - 30, -840, sx * 95 + 30, -760, hair)
        elif L["hair"] == "side":
            F.poly([(-104, -800), (-100, -870), (-40, -905), (60, -905), (104, -860), (104, -800), (40, -870), (-60, -860)], hair)
        elif L["hair"] == "perm":
            for i in range(13):
                a = math.pi * (0.9 + i / 12 * 1.2)
                F.circle(105 * math.cos(a), -815 + 100 * math.sin(a), 42, hair)
        elif L["hair"] == "bob":
            F.poly([(-118, -680), (-118, -830), (-80, -905), (80, -905), (118, -830), (118, -680), (80, -690), (80, -800),
                    (-80, -800), (-80, -690)], hair)
            F.rrect(-95, -905, 95, -842, 26, hair)
    if back:                                                         # seen from behind (mid-spin): all hair, no face
        with kk.keyed(c, halo=halo * 0.6, shadow=False) as F:
            F.circle(0, -805, 104, L["hair_c"] if L["hair"] != "bald" else mix(SKIN, INK, 0.1))
            if L["hair"] == "bob":
                F.rrect(-118, -830, 118, -680, 30, L["hair_c"])
        c.restore()
        return None
    if bow > 0.5:                                                    # bowed: we see the top of the head, not the face
        c.drawOval(skia.Rect.MakeLTRB(-100, -860, 100, -760), paint(mix(SKIN, INK, 0.12)))
        if L["hair"] == "bald":
            for sx in (-1, 1):
                c.drawOval(skia.Rect.MakeLTRB(sx * 95 - 28, -830, sx * 95 + 28, -780), paint(L["hair_c"]))
            c.drawOval(skia.Rect.MakeLTRB(-40, -850, 10, -830), paint(WHITE, 0.5))
        c.restore()
        return None
    # the face: deadpan
    ex = 38
    shut = (blink and (int(T * 24) + sum(map(ord, who)) % 17) % 71 < 3) or bow > 0.5
    for sx in (-1, 1):
        if mood == "dead":
            c.drawLine(sx * ex - 14, -822, sx * ex + 14, -798, paint(INK, stroke=6))
            c.drawLine(sx * ex + 14, -822, sx * ex - 14, -798, paint(INK, stroke=6))
        elif shut:
            c.drawLine(sx * ex - 12, -810, sx * ex + 12, -810, paint(INK, stroke=5))
        else:
            c.drawOval(skia.Rect.MakeLTRB(sx * ex - 9 + look * 5, -822, sx * ex + 9 + look * 5, -798), paint(INK))
        c.drawLine(sx * ex - 18, -838, sx * ex + 18, -838, paint(mix(L["hair_c"], INK, 0.3), stroke=6))
    if L.get("glasses") == "round":
        for sx in (-1, 1):
            c.drawCircle(sx * ex, -810, 28, paint(INK, stroke=5))
        c.drawLine(-10, -810, 10, -810, paint(INK, stroke=5))
    elif L.get("glasses") == "square":
        for sx in (-1, 1):
            c.drawRect(skia.Rect.MakeLTRB(sx * ex - 28, -832, sx * ex + 28, -790), paint(INK, stroke=5))
        c.drawLine(-10, -812, 10, -812, paint(INK, stroke=5))
    if L.get("mustache"):
        c.drawPath(smooth([(-50, -752), (0, -768), (50, -752), (30, -738), (0, -748), (-30, -738)]), paint(WHITE))
    mouth = {"flat": [(-22, -745), (22, -745)], "smile": None, "shock": None, "dead": [(-26, -742), (26, -742)]}
    lipc = (220, 40, 70) if L.get("lips") else mix(SKIN, INK, 0.55)
    if mood == "smile":
        c.drawPath(path(bez((-28, -752), (0, -728), (28, -752)), closed=False), paint(lipc, stroke=6))
    elif mood == "shock":
        c.drawOval(skia.Rect.MakeLTRB(-16, -765, 16, -725), paint((90, 20, 30)))
    elif not L.get("mustache"):
        c.drawLine(*mouth.get(mood, mouth["flat"])[0], *mouth.get(mood, mouth["flat"])[1], paint(lipc, stroke=6))
    for sx in (-1, 1):
        c.drawCircle(sx * 62, -770, 16, paint((255, 150, 150), 0.5))
    if L.get("pearls"):
        for i in range(9):
            a = math.pi * (0.2 + 0.6 * i / 8)
            c.drawCircle(70 * math.cos(a), -700 + 30 * math.sin(a), 9, paint(WHITE))
    c.restore()
    if prop_hand is not None:
        m_x = x + prop_hand[0] * s * spin * hs
        m_y = y - bob + prop_hand[1] * s * hs
        return m_x, m_y
    return None


def shovel(c, x, y, s, ang=-30):
    """A garden spade held at (x, y)."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    with kk.keyed(c, halo=5) as F:
        F.rrect(-10, -40, 10, 330, 8, (150, 100, 60))
        F.poly([(-50, 320), (50, 320), (40, 440), (0, 470), (-40, 440)], (170, 180, 195))
        F.rrect(-40, -70, 40, -40, 10, (60, 60, 70))
    c.restore()


def rubber_stamp(c, x, y, s, label="DENIED", ink=BLOOD):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    with kk.keyed(c, halo=5) as F:
        F.oval(-45, -190, 45, -110, (200, 40, 50))
        F.rrect(-18, -130, 18, -40, 8, (150, 90, 50))
        F.rrect(-80, -45, 80, 0, 10, (90, 60, 40))
    c.restore()


# ------------------------------------------------------------------ the machine (early CGI plastic)

def machine(c, x, y, s, T, face="smile", stamp=0.0, slot=0.0, glow=0.0, label=True):
    """CLAIM-O-MATIC 2000: a glossy pink plastic cabinet with chrome trim, a CRT face, blinking bulbs, a stamping arm.
    (x, y) = floor centre; ~760 px tall at s=1."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawOval(skia.Rect.MakeLTRB(-300, -30, 300, 30), paint(INK, 0.35, blur=14))
    body = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-260, -760, 260, -20), 60, 60)
    c.drawRRect(body, paint(shader=lin((-260, 0), (260, 0), [(255, 110, 190), (255, 170, 220), (230, 60, 150)], [0, 0.35, 1])))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-240, -745, -170, -40), 30, 30), paint(WHITE, 0.25))
    chrome = lin((0, -800), (0, -700), [(250, 250, 255), (150, 160, 180), (240, 240, 250), (120, 130, 150)], [0, 0.4, 0.6, 1])
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-280, -800, 280, -720), 30, 30), paint(shader=chrome))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-200, -690, 200, -400), 30, 30), paint((180, 190, 200)))
    scr = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-180, -675, 180, -415), 24, 24)
    c.drawRRect(scr, paint((10, 40, 25) if face not in ("evil", "off") else ((40, 0, 5) if face == "evil" else (5, 5, 8))))
    px = (120, 255, 150) if face != "evil" else (255, 50, 50)
    blink = int(T * 3) % 7 == 0
    if face == "off":
        c.drawLine(-120, -545, 120, -545, paint(WHITE, 0.8, stroke=4))
    for sx in ((-1, 1) if face != "off" else ()):                       # pixel eyes
        if blink and face != "evil":
            c.drawRect(skia.Rect.MakeLTRB(sx * 70 - 30, -590, sx * 70 + 30, -575), paint(px))
        else:
            c.drawRect(skia.Rect.MakeLTRB(sx * 70 - 22, -620, sx * 70 + 22, -570), paint(px))
    if face == "evil":
        c.drawPath(path([(-100, -500), (-60, -470), (-20, -500), (20, -470), (60, -500), (100, -470)], closed=False), paint(px, stroke=12))
    elif face != "off":
        for i in range(-4, 5):
            yy = -500 + (0.0 if abs(i) < 4 else -18) + (-(4 - abs(i)) * 5 if face == "smile" else 0)
            c.drawRect(skia.Rect.MakeLTRB(i * 22 - 10, yy, i * 22 + 10, yy + 18), paint(px))
    for k in range(0, 260, 8):                                          # CRT scanlines
        c.drawLine(-180, -675 + k, 180, -675 + k, paint(INK, 0.18, stroke=2))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-170, -665, -60, -600), 20, 20), paint(WHITE, 0.18))
    for i in range(6):                                                  # bulbs
        on = (int(T * 8) + i) % 3 == 0
        cc = [(255, 60, 60), LEMON, (80, 220, 255), (120, 255, 120), (255, 120, 220), ORANGE][i]
        bx = -175 + i * 70
        c.drawCircle(bx, -350, 22, paint(cc if on else mix(cc, INK, 0.5)))
        if on:
            c.drawCircle(bx, -350, 40, paint(shader=rad((bx, -350), 40, [(*cc, 0.6), (*cc, 0.0)])))
        c.drawCircle(bx - 7, -357, 6, paint(WHITE, 0.8))
    if label:
        kk.chrome_text(c, "CLAIM-O-MATIC 2000", 0, -260, 42, 0, fname="bungee-400", depth=4, tag="machine",
                       face=((255, 255, 255), (190, 200, 220), (90, 100, 130)))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-150, -200, 150, -150), 14, 14), paint(INK))    # output slot
    if slot > 0:
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(-160, -175, 160, 60))
        c.drawRect(skia.Rect.MakeLTRB(-120, -175, 120, -175 + 190 * slot), paint(WHITE))
        c.drawLine(-90, -175 + 150 * slot, 90, -175 + 150 * slot, paint(BLOOD, stroke=10))
        c.restore()
    # the stamping arm on the right
    ay = -560 + 180 * stamp
    c.drawRect(skia.Rect.MakeLTRB(250, -640, 330, -600), paint(shader=chrome))
    c.drawRect(skia.Rect.MakeLTRB(300, -620, 330, ay), paint(shader=lin((300, 0), (330, 0), [(230, 230, 240), (120, 130, 150)])))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(270, ay, 360, ay + 70), 12, 12), paint((220, 30, 40)))
    c.drawRect(skia.Rect.MakeLTRB(262, ay + 60, 368, ay + 84), paint((90, 50, 30)))
    for sx in (-1, 1):
        c.drawCircle(sx * 190, -10, 26, paint(shader=chrome))
    if glow > 0:
        c.drawRRect(body, paint(BLOOD, 0.35 * glow, blur=30))
    c.restore()


# ------------------------------------------------------------------ claymation

ERR = (235, 30, 90)


def creature(c, x, y, s, T, mood="grin", look=(0.2, 0.0), seed=1, color=ERR):
    """The little error: a lumpy one-eyed clay imp with tiny horns and far too many teeth. (x, y) = feet."""
    t = twos(T)
    bx, by, br = boil(T, 2.0, seed)
    c.save()
    c.translate(x + bx, y + by)
    c.scale(s, s)
    c.rotate(br * 2)
    clay_shadow(c, 0, 0, 120)
    for sx in (-1, 1):                                                   # stubby feet and arms
        clay_ellipse(c, sx * 55, -18, 42, 24, mix(color, INK, 0.15), t, seed + 10 + sx, prints=0, marks=1)
        wave = math.sin(t * 9 + sx) * 18 if mood != "sleep" else 0
        clay_ellipse(c, sx * 118, -120 + wave, 34, 22, color, t, seed + 20 + sx, rot=sx * (30 + wave), prints=0)
    for sx in (-1, 1):
        clay_poly(c, [(sx * 40, -205), (sx * 70, -265), (sx * 85, -195)], (255, 230, 150), t, seed + 30 + sx, amp=2, prints=0, marks=0)
    clay_ellipse(c, 0, -120, 115, 100, color, t, seed, amp=0.1)
    clay_eye(c, 0, -150, 44, t, look, seed + 40)
    mw = 60 if mood == "grin" else 50
    mh = 26 if mood == "grin" else 44
    m = path(np.vstack([bez((-mw, -95), (0, -95 + mh * 0.3), (mw, -95)), bez((mw, -95), (0, -95 + mh * 1.8), (-mw, -95))]))
    c.drawPath(m, paint((80, 0, 20)))
    c.save()
    c.clipPath(m, doAntiAlias=True)
    for k in range(7):
        tx = -mw + k * (2 * mw / 7)
        c.drawPath(path([(tx, -97), (tx + 2 * mw / 7, -97), (tx + mw / 7, -80)]), paint((255, 250, 225)))
    c.restore()
    c.restore()


def crow(c, x, y, s, T, caw=0.0, seed=7, flip=False):
    """A fat clay crow. caw 0..1 opens the beak."""
    t = twos(T)
    bx, by, br = boil(T, 1.5, seed)
    c.save()
    c.translate(x + bx, y + by)
    c.scale(-s if flip else s, s)
    clay_ellipse(c, 0, 0, 90, 60, (30, 30, 45), t, seed, rot=-10)
    clay_ellipse(c, -20, 5, 60, 34, (45, 45, 60), t, seed + 1, rot=15, prints=1)
    clay_ellipse(c, 70, -50, 45, 42, (30, 30, 45), t, seed + 2)
    op = 18 * caw
    clay_poly(c, [(105, -60 - op * 0.3), (170, -50), (105, -40)], ORANGE, t, seed + 3, amp=2, prints=0, marks=0)
    if caw > 0:
        clay_poly(c, [(105, -40), (160, -32 + op), (105, -30)], mix(ORANGE, INK, 0.2), t, seed + 4, amp=2, prints=0, marks=0)
    c.drawCircle(85, -62, 9, paint(WHITE))
    c.drawCircle(88, -62, 5, paint(INK))
    clay_poly(c, [(-80, 10), (-150, -10), (-140, 30)], (30, 30, 45), t, seed + 5, amp=3, prints=0)
    for sx in (-10, 20):
        c.drawLine(sx, 55, sx, 85, paint(ORANGE, stroke=6))
    c.restore()


def moves(T, beat, k=0, amt=1.0):
    """The dancing body under the arms: a hop on every beat, a hip sway, a step side to side every two beats."""
    ph = T / beat + k * 0.5
    hop = 30 * amt * abs(math.sin(math.pi * ph))
    tilt = 11 * amt * math.sin(math.pi * ph)
    dx = 34 * amt * math.sin(math.pi * ph / 2)
    return dx, hop, tilt


def corpse(c, x, y, s, T, pose=(10, 0, 10, 0), rise=1.0, seed=3, skin=(170, 200, 160), robe=(235, 235, 225), clip_y=None,
           hop=0.0, tilt=0.0):
    """A clay corpse in a burial robe with X eyes; rise 0..1 lifts it out of the ground (clipped at clip_y)."""
    t = twos(T)
    bx, by, br = boil(T, 2.0, seed)
    c.save()
    if clip_y is not None:
        c.clipRect(skia.Rect.MakeLTRB(-10000, -10000, 10000, clip_y))
    c.translate(x + bx, y + by - hop + (1 - rise) * 520 * s)
    c.scale(s, s)
    c.rotate(br * 1.5 + tilt)
    for i, side in enumerate((-1, 1)):
        sh, el = pose[2 * i], pose[2 * i + 1]
        a1 = math.radians(sh) * side
        ex, ey = side * 70 + 110 * math.sin(a1), -330 + 110 * math.cos(a1)
        a2 = a1 + math.radians(el) * side
        hx, hy = ex + 100 * math.sin(a2), ey + 100 * math.cos(a2)
        clay_path(c, _capsule(side * 70, -330, ex, ey, 26), robe, t, seed + 10 + i, prints=0, marks=1)
        clay_path(c, _capsule(ex, ey, hx, hy, 22), skin, t, seed + 12 + i, prints=0, marks=0)
    clay_poly(c, [(-80, -390), (80, -390), (110, 0), (-110, 0)], robe, t, seed, amp=8)
    clay_ellipse(c, 0, -460, 72, 80, skin, t, seed + 2, amp=0.08)
    for sx in (-1, 1):
        c.drawLine(sx * 26 - 12, -482, sx * 26 + 12, -458, paint(INK, stroke=6))
        c.drawLine(sx * 26 + 12, -482, sx * 26 - 12, -458, paint(INK, stroke=6))
    c.drawOval(skia.Rect.MakeLTRB(-18, -430, 18, -400), paint((60, 20, 30)))
    c.restore()


def _capsule(x0, y0, x1, y1, r):
    a = math.atan2(y1 - y0, x1 - x0)
    nx, ny = -math.sin(a) * r, math.cos(a) * r
    p = skia.Path()
    p.moveTo(x0 + nx, y0 + ny)
    p.lineTo(x1 + nx, y1 + ny)
    p.arcTo(skia.Rect.MakeLTRB(x1 - r, y1 - r, x1 + r, y1 + r), math.degrees(a) + 90, -180, False)
    p.lineTo(x0 - nx, y0 - ny)
    p.arcTo(skia.Rect.MakeLTRB(x0 - r, y0 - r, x0 + r, y0 + r), math.degrees(a) - 90, -180, False)
    p.close()
    return p


def tombstone(c, x, y, s, T, n=1, seed=0, color=(165, 165, 175), label=True):
    """A clay tombstone for one wrong claim, with a red X pressed into it."""
    t = twos(T)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    clay_shadow(c, 0, 0, 110, 22)
    clay_poly(c, [(-90, 0), (-90, -200), (-60, -250), (60, -250), (90, -200), (90, 0)], color, t, seed, amp=5, prints=1)
    if label:
        f = kk.font("rounded-900", 30)
        s_ = f"CLAIM #{n:,}"
        w = f.measureText(s_)
        c.drawString(s_, -w / 2 + 1.5, -175 + 2, f, paint(WHITE, 0.4))
        c.drawString(s_, -w / 2, -175, f, paint(mix(color, INK, 0.55)))
    c.drawLine(-35, -130, 35, -60, paint(BLOOD, stroke=14))
    c.drawLine(35, -130, -35, -60, paint(BLOOD, stroke=14))
    c.restore()


def envelope(c, x, y, s, T, seed=0, rot=0.0, label="FRAUD", color=(230, 40, 50)):
    """A red clay envelope with a FRAUD stamp."""
    t = twos(T)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    clay_poly(c, [(-110, -70), (110, -70), (110, 70), (-110, 70)], color, t, seed, amp=4, prints=1, marks=1)
    c.drawPath(path([(-100, -60), (0, 10), (100, -60)], closed=False), paint(mix(color, INK, 0.4), stroke=6))
    if label:
        f = kk.font("dela-400", 44)
        w = f.measureText(label)
        c.save()
        c.rotate(-8)
        c.drawString(label, -w / 2, 45, f, paint(INK, stroke=10))
        c.drawString(label, -w / 2, 45, f, paint(WHITE))
        kk.reg_local(c, -w / 2, 10, w / 2, 55, "prop")
        c.restore()
    c.restore()


def claim_form(c, x, y, s, rot=0.0, x_mark=True, tag="form", title="CLAIM FORM", stamp=None):
    """A flat paper claim form (live action prop): header, lines, and a red X or a stamp."""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    c.drawRect(skia.Rect.MakeLTRB(-150, -200, 150, 200).makeOffset(8, 10), paint(INK, 0.3, blur=6))
    c.drawRect(skia.Rect.MakeLTRB(-150, -200, 150, 200), paint(WHITE))
    c.drawRect(skia.Rect.MakeLTRB(-150, -200, 150, -140), paint((120, 190, 255)))
    kk.text(c, title, 0, -158, 34, "rounded-900", WHITE, tag=tag)
    for k in range(7):
        c.drawRect(skia.Rect.MakeLTRB(-120, -110 + k * 40, 120 - (k * 37) % 70, -100 + k * 40), paint((170, 170, 190)))
    if x_mark:
        c.drawLine(-90, -80, 90, 150, paint(BLOOD, stroke=26))
        c.drawLine(90, -80, -90, 150, paint(BLOOD, stroke=26))
    if stamp:
        c.save()
        c.rotate(-12)
        f = kk.font("dela-400", 60)
        w = f.measureText(stamp)
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-w / 2 - 20, -10, w / 2 + 20, 70), 10, 10), paint(BLOOD, stroke=8))
        c.drawString(stamp, -w / 2, 52, f, paint(BLOOD))
        kk.reg_local(c, -w / 2, 5, w / 2, 60, tag)
        c.restore()
    c.restore()


def guestbook(c, x, y, s, T, marks=1, rot=0.0, you=False, tag="book"):
    """The family guestbook, open: two ruled pages of entries; the wrong ones crossed in red. you=True: the next
    empty line has your name on it."""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-330, -230, 330, 230), 16, 16), paint((170, 30, 50)))
    c.drawRect(skia.Rect.MakeLTRB(-310, -215, -6, 215), paint(CREAM))
    c.drawRect(skia.Rect.MakeLTRB(6, -215, 310, 215), paint(CREAM))
    c.drawLine(0, -220, 0, 220, paint((120, 20, 30), stroke=10))
    kk.text(c, "GUESTS & CLAIMS", -158, -175, 28, "rounded-900", (170, 30, 50), tag=tag)
    rng = np.random.default_rng(11)
    n = 0
    for side in (-1, 1):
        for k in range(8):
            yy = -140 + k * 42
            x0 = -290 if side < 0 else 26
            c.drawLine(x0, yy + 8, x0 + 264, yy + 8, paint((180, 190, 220), stroke=2))
            if you and side > 0 and k == 7:
                kk.text(c, "→ YOU", x0 + 80, yy + 6, 44, "mochiy-400", BLOOD, tag=tag)
                continue
            pts = [(x0 + 10 + i * 12, yy + rng.uniform(-6, 4)) for i in range(int(rng.uniform(10, 19)))]
            c.drawPath(path(pts, closed=False), paint((40, 40, 90), stroke=3))
            if n < marks:
                c.drawLine(x0 + 180, yy - 14, x0 + 240, yy + 12, paint(BLOOD, stroke=7))
                c.drawLine(x0 + 240, yy - 14, x0 + 180, yy + 12, paint(BLOOD, stroke=7))
            n += 1 if (side < 0 or k < 7) else 0
    c.restore()


def hands(c, T, x=540, y=1100, w=560, h=720, shake=0.0, sleeve=(90, 120, 200), content=None):
    """Your hands holding a sheet up in front of you (point of view). content(c, x0, y0, x1, y1) draws the sheet's
    face; the thumbs go over it. Returns nothing; everything is keyed in."""
    jx = math.sin(T * 38) * 7 * shake
    jy = math.cos(T * 31) * 4 * shake
    x0, y0, x1, y1 = x - w / 2 + jx, y - h / 2 + jy, x + w / 2 + jx, y + h / 2 + jy
    with kk.keyed(c, halo=6) as F:
        for sx, hx in ((-1, x0 + 40), (1, x1 - 40)):
            F.poly([(hx - 110, H + 50), (hx + 110, H + 50), (hx + 90, y1 + 120), (hx - 90, y1 + 120)], sleeve)
            F.rrect(hx - 85, y1 - 60, hx + 85, y1 + 150, 60, SKIN)
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1).makeOffset(10, 12), paint(INK, 0.3, blur=8))
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(WHITE))
    if content is not None:
        content(c, x0, y0, x1, y1)
    with kk.keyed(c, halo=5, shadow=False) as F:
        for sx, hx in ((-1, x0 + 40), (1, x1 - 40)):
            F.oval(hx - 36 + sx * 10, y1 - 110, hx + 36 + sx * 10, y1 - 10, SKIN)
    for sx, hx in ((-1, x0 + 40), (1, x1 - 40)):
        c.drawOval(skia.Rect.MakeLTRB(hx - 18 + sx * 10, y1 - 104, hx + 18 + sx * 10, y1 - 76), paint((255, 235, 225)))


def money(c, x, y, s, T, seed=0, rot=0.0):
    t = twos(T)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    clay_poly(c, [(-80, -40), (80, -40), (80, 40), (-80, 40)], (110, 200, 110), t, seed, amp=3, prints=1, marks=0)
    c.drawCircle(0, 0, 24, paint((70, 150, 70), stroke=5))
    f = kk.font("dela-400", 34)
    c.drawString("$", -10, 12, f, paint((50, 120, 50)))
    c.restore()


def you_clay(c, x, y, s, T, pose="stand", mood="worried", seed=11, sweater=(60, 170, 190), hair=(60, 40, 30)):
    """You, in clay: a lumpy little person with a worried face. (x, y) = feet; ~640 px tall at s=1.
    pose: stand | hold (arms out in front, holding something) | empty (arms out, nothing in them) | box | sit | slump"""
    t = twos(T)
    bx, by, br = boil(T, 1.5, seed)
    c.save()
    c.translate(x + bx, y + by)
    c.scale(s, s)
    c.rotate(br * 1.2)
    skin = (250, 205, 170)
    sit = pose in ("sit", "slump")
    clay_shadow(c, 0, 0, 130)
    if sit:
        for sx in (-1, 1):
            clay_path(c, _capsule(sx * 45, -190, sx * 50, -30, 34), (60, 60, 90), t, seed + 1 + sx, prints=0, marks=1)
            clay_ellipse(c, sx * 55, -18, 48, 22, (40, 30, 30), t, seed + 3 + sx, prints=0, marks=0)
        body_y = -330
    else:
        for sx in (-1, 1):
            clay_path(c, _capsule(sx * 42, -260, sx * 48, -40, 36), (60, 60, 90), t, seed + 1 + sx, prints=0, marks=1)
            clay_ellipse(c, sx * 55, -22, 52, 24, (40, 30, 30), t, seed + 3 + sx, prints=0, marks=0)
        body_y = -390
    droop = 30 if pose == "slump" else 0
    hand = {"stand": (150, 120), "hold": (60, -20), "empty": (190, -70), "box": (110, 10), "sit": (120, 110),
            "slump": (70, 150)}[pose]
    clay_ellipse(c, 0, body_y, 118, 160, sweater, t, seed, amp=0.07)
    for sx in (-1, 1):
        hx_, hy_ = sx * hand[0], body_y + hand[1]
        clay_path(c, _capsule(sx * 95, body_y - 90, hx_, hy_, 30), sweater, t, seed + 7 + sx, prints=0, marks=1)
        clay_ellipse(c, hx_, hy_ + 8, 28, 26, skin, t, seed + 9 + sx, prints=0, marks=0)
    hy = body_y - 240 + droop
    clay_ellipse(c, 0, hy, 92, 98, skin, t, seed + 20, amp=0.06, prints=1, marks=1)
    clay_ellipse(c, 0, hy - 62, 96, 52, hair, t, seed + 21, amp=0.08, prints=1, marks=0)
    for sx in (-1, 1):                                                  # worried eyes and brows
        c.drawCircle(sx * 32, hy + 4 + droop * 0.2, 11, paint(INK))
        c.drawCircle(sx * 32 - 3, hy, 3.5, paint(WHITE))
        c.drawLine(sx * 14, hy - 30, sx * 52, hy - 20 + (0 if mood == "worried" else 6), paint(mix(hair, INK, 0.3), stroke=8))
    mouth = path(bez((-28, hy + 52), (0, hy + 36), (28, hy + 52)), closed=False)
    c.drawPath(mouth, paint((110, 30, 40), stroke=8))
    if mood in ("sad", "cry"):
        clay_ellipse(c, 40, hy + 40, 10, 16, (140, 200, 255), t, seed + 30, prints=0, marks=0, gloss=0.6)
    c.restore()

"""The players, painted like actors on a 1971 set (style only - nobody from the film).

YOU        a young woman in a yellow raincoat: the only colour in the grey town. Carries the letter, then the ticket.
HOST       the factory's proprietor: tall, teal velvet frock coat, mustard waistcoat, a cream cravat, wild auburn
           curls, round green-tinted spectacles, a cane topped with a glowing bulb. Gentle, then quietly menacing.
COPIER     a boy in a striped jumper with an enormous spoon (swallows answers whole).
BELIEVER   a lady in a pink coat and a vast flowered hat (believes every word).
YESMAN     a man in a brown check suit with a pocket mirror (only asks to be told he's right).
RUSHER     a girl in a red tracksuit with a stopwatch (the first idea will do).
WORKER     the little workers: identical, knee-high, with glowing light-bulb heads and blue overalls.
DOCTOR, FARMER, STUDENT; MOTHER and BOY are only ever silhouettes (a true story, illustrated).

person(c, who, x, y, s, T, ...) draws a figure standing with its feet at (x, y); ~900 px tall at s=1.
"""
import math

import numpy as np
import skia

import draw as D
from draw import INK, WHITE, CREAM, SKIN, mix, paint, path, shade

LOOKS = {
    "you": dict(h=0.96, coat=(242, 196, 40), coat_len=-330, hair="bob", hair_c=(52, 34, 28), legs=(70, 56, 80),
                shoes=(190, 40, 50), lips=True, collar=(250, 214, 80)),
    "host": dict(h=1.13, coat=(20, 110, 118), coat_len=-240, tails=True, vest=(214, 160, 40), cravat=CREAM,
                 hair="wild", hair_c=(176, 84, 40), legs=(96, 62, 58), shoes=(60, 36, 30), specs="round_green"),
    "copier": dict(h=0.66, head=1.18, coat=(210, 50, 60), stripes=WHITE, coat_len=-440, hair="bowl",
                   hair_c=(236, 196, 110), legs=(40, 50, 100), shoes=(50, 40, 40), shorts=True),
    "believer": dict(h=0.98, coat=(240, 140, 172), coat_len=-300, hair="curls", hair_c=(210, 196, 170),
                     legs=(230, 200, 180), shoes=(200, 90, 120), hat="flowers", pearls=True, lips=True),
    "yesman": dict(h=1.0, coat=(140, 100, 62), check=True, coat_len=-420, hair="slick", hair_c=(30, 24, 22),
                   legs=(120, 84, 52), shoes=(40, 28, 22), tie=(230, 180, 40), tash=True),
    "rusher": dict(h=0.7, head=1.16, coat=(210, 40, 40), stripes=None, track=True, coat_len=-460, hair="pigtails",
                   hair_c=(120, 70, 40), legs=(210, 40, 40), shoes=(240, 240, 240)),
    "doctor": dict(h=0.98, coat=(226, 228, 220), coat_len=-300, hair="bun", hair_c=(60, 40, 34), legs=(60, 70, 90),
                   shoes=(40, 34, 30), specs="thin", stetho=True, lips=True),
    "farmer": dict(h=1.0, coat=(110, 110, 120), coat_len=-470, hair="cap", hair_c=(90, 80, 70), legs=(80, 90, 120),
                   shoes=(50, 40, 34), overalls=True, tash=True),
    "dad": dict(h=0.98, coat=(150, 110, 80), coat_len=-420, hair="slick", hair_c=(190, 190, 190), legs=(90, 90, 100),
                shoes=(60, 40, 30), specs="thin", tash=True),
    "student": dict(h=0.94, coat=(150, 110, 150), coat_len=-470, hair="curls", hair_c=(50, 36, 30), legs=(60, 70, 110),
                    shoes=(50, 40, 34), specs="round", lips=True),
}
POSES = {  # (left shoulder, left elbow, right shoulder, right elbow) degrees; 0 = hanging down, + = out/up
    "stand": (8, 0, 8, 0), "hold": (10, 0, 30, -100), "hold2": (30, -100, 30, -100), "wave": (8, 0, 150, 20),
    "present": (10, 0, 100, 10), "arms_out": (95, 0, 95, 0), "arms_up": (160, 10, 160, 10), "point": (8, 0, 115, 0),
    "shrug": (40, 110, 40, 110), "cane": (10, 0, 22, 30), "cheer": (150, 20, 150, 20), "clasp": (25, -95, 25, -95),
    "fists": (35, 120, 35, 120), "reach": (10, 0, 70, 20),
}


def _limb(c, x, y, sh, el, L1, L2, side, color, w, hand=SKIN, glove=None):
    a1 = math.radians(sh) * side
    ex, ey = x + L1 * math.sin(a1), y + L1 * math.cos(a1)
    a2 = a1 + math.radians(el) * side
    hx, hy = ex + L2 * math.sin(a2), ey + L2 * math.cos(a2)
    shade(c, D.capsule(x, y, ex, ey, w, w * 0.9), color, k=0.22)
    shade(c, D.capsule(ex, ey, hx, hy, w * 0.9, w * 0.75), color, k=0.22)
    shade(c, D.circle(hx, hy, w * 0.5), glove or hand, k=0.2)
    return hx, hy, a2


def face(c, L, mood="smile", look=0.0, blink=False, talk=0.0, r=60):
    """Eyes, brows, nose, mouth for a head centred at (0, 0) of radius ~r."""
    k = r / 60
    lx = look * 10 * k
    for sx in (-1, 1):
        ex, ey = sx * 22 * k + lx, -6 * k
        if blink:
            c.drawLine(ex - 9 * k, ey, ex + 9 * k, ey, paint(INK, stroke=3 * k))
        else:
            lid = 0.55 if mood == "sly" else 1.0
            c.drawOval(skia.Rect.MakeLTRB(ex - 10 * k, ey - 8 * k * lid, ex + 10 * k, ey + 8 * k), paint(WHITE))
            c.drawCircle(ex + look * 3 * k, ey + 1 * k, 5.5 * k, paint((60, 40, 30)))
            c.drawCircle(ex + look * 3 * k, ey + 1 * k, 3 * k, paint(INK))
            c.drawCircle(ex + look * 3 * k + 2 * k, ey - 1 * k, 1.4 * k, paint(WHITE))
            if mood == "sly":
                c.drawLine(ex - 11 * k, ey - 4 * k, ex + 11 * k, ey - 3 * k, paint(mix(SKIN, INK, 0.5), stroke=3 * k))
        tilt = {"angry": 14, "shout": 14, "worry": -12, "wow": -4, "sly": 6}.get(mood, 0) * sx
        by = ey - 16 * k - (6 * k if mood == "wow" else 0)
        c.save()
        c.translate(ex, by)
        c.rotate(tilt)
        c.drawLine(-10 * k, 0, 10 * k, 0, paint(mix(L.get("hair_c", (80, 60, 50)), INK, 0.3), stroke=4 * k))
        c.restore()
    c.drawLine(lx * 0.8, 2 * k, lx * 0.8 - 3 * k, 14 * k, paint(mix(SKIN, INK, 0.35), 0.8, stroke=2.4 * k))   # nose
    for sx in (-1, 1):
        c.drawCircle(sx * 30 * k + lx, 14 * k, 9 * k, paint((240, 120, 110), 0.28, blur=4 * k))            # cheeks
    my = 28 * k
    lip = (190, 60, 70) if L.get("lips") else mix(SKIN, INK, 0.45)
    o = max(talk, {"wow": 0.8, "shout": 1.0}.get(mood, 0.0))
    if o > 0.05:
        c.drawOval(skia.Rect.MakeLTRB(lx - 11 * k, my - 5 * k * o, lx + 11 * k, my + 9 * k * o), paint((80, 20, 30)))
        c.drawOval(skia.Rect.MakeLTRB(lx - 11 * k, my - 5 * k * o, lx + 11 * k, my + 9 * k * o), paint(lip, stroke=2.5 * k))
    else:
        p = skia.Path()
        curve = {"smile": 8, "sly": 5, "flat": 1, "worry": -5, "angry": -7}.get(mood, 3) * k
        w = (14 if mood != "sly" else 16) * k
        p.moveTo(lx - w, my)
        p.quadTo(lx, my + curve, lx + w, my - (3 * k if mood == "sly" else 0))
        c.drawPath(p, paint(lip, stroke=3.2 * k))


def _hair_back(c, L, r):
    hc, st = L["hair_c"], L["hair"]
    if st == "bob":
        shade(c, D.rrect(-r * 1.12, -r * 1.05, r * 1.12, r * 0.95, r * 0.6), hc, k=0.25)
    elif st == "wild":
        for i in range(15):
            a = math.pi * (0.75 + i / 14 * 1.5)
            shade(c, D.circle(r * 1.05 * math.cos(a), -r * 0.2 + r * 0.95 * math.sin(a), r * 0.42), hc, k=0.25, edge=0.2)
    elif st == "curls":
        for i in range(11):
            a = math.pi * (0.85 + i / 10 * 1.3)
            shade(c, D.circle(r * 0.95 * math.cos(a), -r * 0.15 + r * 0.9 * math.sin(a), r * 0.36), hc, k=0.25, edge=0.2)
    elif st == "pigtails":
        for sx in (-1, 1):
            shade(c, D.capsule(sx * r * 0.9, -r * 0.2, sx * r * 1.55, r * 0.7, r * 0.34, r * 0.22), hc, k=0.25)
    elif st == "bun":
        shade(c, D.circle(0, -r * 1.05, r * 0.42), hc, k=0.25)


def _hair_front(c, L, r):
    hc, st = L["hair_c"], L["hair"]
    if st == "bob":
        p = skia.Path()
        p.moveTo(-r * 1.02, -r * 0.1)
        p.cubicTo(-r * 1.1, -r * 1.3, r * 1.1, -r * 1.3, r * 1.02, -r * 0.1)
        p.lineTo(r * 0.7, -r * 0.55)
        p.lineTo(-r * 0.2, -r * 0.62)
        p.lineTo(-r * 0.7, -r * 0.5)
        p.close()
        shade(c, p, hc, k=0.25)
    elif st == "wild":
        for i in range(7):
            a = math.pi * (1.1 + i / 6 * 0.8)
            shade(c, D.circle(r * 0.85 * math.cos(a), -r * 0.35 + r * 0.8 * math.sin(a), r * 0.36), hc, k=0.25, edge=0.2)
    elif st in ("curls",):
        for i in range(6):
            a = math.pi * (1.12 + i / 5 * 0.76)
            shade(c, D.circle(r * 0.8 * math.cos(a), -r * 0.3 + r * 0.72 * math.sin(a), r * 0.3), hc, k=0.25, edge=0.2)
    elif st == "bowl":
        p = skia.Path()
        p.moveTo(-r * 1.05, -r * 0.05)
        p.cubicTo(-r * 1.1, -r * 1.35, r * 1.1, -r * 1.35, r * 1.05, -r * 0.05)
        p.lineTo(-r * 1.05, -r * 0.05)
        p.close()
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(-r * 2, -r * 2, r * 2, -r * 0.3))
        shade(c, p, hc, k=0.25)
        c.restore()
    elif st == "slick":
        p = skia.Path()
        p.moveTo(-r * 1.0, -r * 0.2)
        p.cubicTo(-r * 1.05, -r * 1.25, r * 1.05, -r * 1.25, r * 1.0, -r * 0.2)
        p.quadTo(r * 0.3, -r * 0.8, -r * 1.0, -r * 0.2)
        shade(c, p, hc, k=0.3)
        c.drawLine(-r * 0.3, -r * 0.95, r * 0.5, -r * 0.7, paint(WHITE, 0.4, stroke=3))
    elif st == "pigtails" or st == "bun":
        p = skia.Path()
        p.moveTo(-r * 1.0, -r * 0.1)
        p.cubicTo(-r * 1.05, -r * 1.3, r * 1.05, -r * 1.3, r * 1.0, -r * 0.1)
        p.quadTo(0, -r * 0.75, -r * 1.0, -r * 0.1)
        shade(c, p, hc, k=0.25)
    elif st == "cap":
        shade(c, D.rrect(-r * 1.05, -r * 1.1, r * 1.05, -r * 0.45, r * 0.4), hc, k=0.25)
        shade(c, D.rrect(-r * 0.2, -r * 0.62, r * 1.35, -r * 0.4, r * 0.1), mix(hc, INK, 0.2), k=0.2)


def person(c, who, x, y, s, T, pose="stand", mood="smile", look=0.0, bob=0.0, tilt=0.0, talk=0.0, blink=True,
           prop=None, walk=0.0, lean=0.0, shadow=True, alpha=1.0, squash=1.0):
    """Draw a figure (feet at x, y). Returns the right hand position (for props), in canvas coordinates."""
    L = LOOKS[who]
    arms = POSES[pose] if isinstance(pose, str) else pose
    hs = L["h"]
    hd = L.get("head", 1.0)
    c.save()
    if shadow:
        c.drawOval(skia.Rect.MakeLTRB(x - 120 * s * hs, y - 18 * s, x + 120 * s * hs, y + 18 * s), paint(INK, 0.28, blur=10))
    c.translate(x, y - bob)
    c.scale(s * hs, s * hs * squash)
    if tilt or lean:
        c.translate(0, -400)
        c.rotate(tilt + lean)
        c.translate(0, 400)
    if alpha < 1:
        c.saveLayerAlpha(None, int(255 * alpha))
    coat = L["coat"]
    # legs
    sw = math.sin(walk * math.pi * 2) * 22 if walk else 0.0
    for i, sx in enumerate((-1, 1)):
        k = sw * (1 if i else -1)
        x0 = sx * 42
        shade(c, D.capsule(x0, -480, x0 + k, -40, 62, 50), L["legs"], k=0.2)
        shade(c, D.rrect(x0 + k - 34 + sx * 6, -52, x0 + k + 38 + sx * 6, 0, 22), L["shoes"], k=0.25)
    if L.get("shorts"):
        shade(c, D.rrect(-92, -520, 92, -400, 30), L["legs"], k=0.2)
    # body / coat
    body = skia.Path()
    hem = L["coat_len"]
    flare = 1.25 if hem > -400 else 1.0
    body.moveTo(-104, -742)
    body.cubicTo(-120, -700, -110, -560, -92 * flare, hem)
    body.lineTo(92 * flare, hem)
    body.cubicTo(110, -560, 120, -700, 104, -742)
    body.quadTo(0, -770, -104, -742)
    shade(c, body, coat, k=0.25)
    if L.get("tails"):
        for sx in (-1, 1):
            p = path([(sx * 60, -420), (sx * 118, -170), (sx * 70, -190), (sx * 20, -420)])
            shade(c, p, mix(coat, INK, 0.12), k=0.2)
    if L.get("stripes"):
        c.save()
        c.clipPath(body, doAntiAlias=True)
        for j in range(8):
            yy = -730 + j * 44
            c.drawRect(skia.Rect.MakeLTRB(-140, yy, 140, yy + 18), paint(L["stripes"], 0.9))
        c.restore()
    if L.get("track"):
        for sx in (-1, 1):
            c.drawLine(sx * 70, -730, sx * 88, hem + 10, paint(WHITE, 0.9, stroke=10))
        c.drawLine(0, -740, 0, hem, paint(mix(coat, INK, 0.3), stroke=4))
    if L.get("check"):
        c.save()
        c.clipPath(body, doAntiAlias=True)
        for j in range(-6, 7):
            c.drawLine(j * 34, -780, j * 34, hem, paint(mix(coat, INK, 0.25), 0.35, stroke=3))
        for j in range(12):
            c.drawLine(-140, -740 + j * 34, 140, -740 + j * 34, paint(mix(coat, INK, 0.25), 0.35, stroke=3))
        c.restore()
    if L.get("overalls"):
        shade(c, D.rrect(-80, -640, 80, hem, 20), (70, 90, 130), k=0.2)
    if who in ("you",):
        c.drawLine(0, -735, 0, hem + 6, paint(mix(coat, INK, 0.35), stroke=3))                         # coat opening
        for j in range(4):
            c.drawCircle(-14, -690 + j * 80, 7, paint(mix(coat, INK, 0.45)))
        shade(c, path([(-104, -742), (0, -700), (104, -742), (60, -770), (-60, -770)]), L["collar"], k=0.2)
    if L.get("vest"):
        shade(c, path([(-50, -740), (50, -740), (58, -470), (0, -440), (-58, -470)]), L["vest"], k=0.2)
        for j in range(3):
            c.drawCircle(0, -660 + j * 60, 6, paint(mix(L["vest"], INK, 0.5)))
    if L.get("tie"):
        shade(c, path([(-16, -740), (16, -740), (26, -560), (0, -530), (-26, -560)]), L["tie"], k=0.2)
    if L.get("pearls"):
        for j in range(9):
            a = math.pi * (0.15 + j / 8 * 0.7)
            c.drawCircle(52 * math.cos(a), -760 + 34 * math.sin(a), 8, paint((250, 246, 236)))
    if L.get("stetho"):
        p = skia.Path()
        p.moveTo(-40, -750)
        p.cubicTo(-70, -620, 60, -600, 40, -520)
        c.drawPath(p, paint((60, 60, 70), stroke=7))
        c.drawCircle(40, -515, 14, paint((190, 190, 200)))
    # arms
    hand = None
    for i, side in enumerate((-1, 1)):
        sh, el = arms[2 * i], arms[2 * i + 1]
        hx, hy, a2 = _limb(c, side * 100, -728, sh, el, 170, 160, side, coat, 54, glove=L.get("glove"))
        if i == 1:
            hand = (hx, hy, a2)
    # neck and head
    shade(c, D.rrect(-24, -800, 24, -730, 12), SKIN, k=0.2)
    if L.get("cravat"):
        shade(c, path([(-40, -760), (40, -760), (26, -690), (0, -670), (-26, -690)]), L["cravat"], k=0.15)
    c.save()
    c.translate(0, -820)
    c.scale(hd, hd)
    r = 58
    _hair_back(c, L, r)
    shade(c, D.oval(-r, -r * 1.12, r, r * 1.08), SKIN, k=0.2)
    for sx in (-1, 1):
        shade(c, D.oval(sx * r - 9, -12, sx * r + 9, 18), SKIN, k=0.2)
    blink_now = blink and (int(T * 10 + x * 0.01) % 37 == 0)
    face(c, L, mood, look, blink_now, talk, r)
    _hair_front(c, L, r)
    if L.get("tash"):
        p = skia.Path()
        p.moveTo(-26, 22)
        p.quadTo(0, 10, 26, 22)
        p.quadTo(0, 30, -26, 22)
        shade(c, p, L["hair_c"], k=0.2)
    sp = L.get("specs")
    if sp:
        tint = (90, 170, 110) if sp == "round_green" else (220, 230, 240)
        for sx in (-1, 1):
            ex = sx * 22 + look * 10
            c.drawCircle(ex, -6, 17 if sp != "thin" else 14, paint(tint, 0.45 if sp == "round_green" else 0.15))
            c.drawCircle(ex, -6, 17 if sp != "thin" else 14, paint((150, 120, 40) if sp == "round_green" else (40, 40, 50), stroke=3.5))
        c.drawLine(-5 + look * 10, -8, 5 + look * 10, -8, paint((150, 120, 40), stroke=3))
    if L.get("hat") == "flowers":
        shade(c, D.oval(-150, -80, 150, -40), (170, 120, 200), k=0.2)
        shade(c, D.oval(-80, -150, 80, -60), (170, 120, 200), k=0.2)
        for j in range(9):
            a = math.pi * (1.05 + j / 8 * 0.9)
            fx, fy = 110 * math.cos(a), -70 + 40 * math.sin(a)
            for q in range(5):
                b = q * 2 * math.pi / 5
                c.drawCircle(fx + 9 * math.cos(b), fy + 9 * math.sin(b), 8, paint([(255, 230, 90), (255, 140, 170), WHITE][j % 3]))
            c.drawCircle(fx, fy, 5, paint((240, 140, 40)))
    c.restore()
    if alpha < 1:
        c.restore()
    m = c.getTotalMatrix()
    pt = m.mapXY(hand[0], hand[1])
    c.restore()
    return (pt.x(), pt.y(), hand[2])


def worker(c, x, y, s, T, pose="stand", mood="smile", bob=0.0, glow=1.0, talk=0.0, seed=0):
    """A little worker: knee-high, blue overalls, white gloves, a glass light-bulb for a head with a filament face."""
    arms = POSES[pose] if isinstance(pose, str) else pose
    c.save()
    c.drawOval(skia.Rect.MakeLTRB(x - 60 * s, y - 10 * s, x + 60 * s, y + 10 * s), paint(INK, 0.28, blur=6))
    c.translate(x, y - bob)
    c.scale(s, s)
    for sx in (-1, 1):
        shade(c, D.capsule(sx * 26, -150, sx * 26, -20, 40, 36), (40, 80, 160), k=0.2)
        shade(c, D.rrect(sx * 26 - 26, -28, sx * 26 + 30, 0, 14), (50, 40, 40), k=0.2)
    shade(c, D.rrect(-66, -300, 66, -130, 36), (40, 80, 160), k=0.22)
    shade(c, D.rrect(-44, -270, 44, -190, 14), (60, 110, 190), k=0.2)
    for sx in (-1, 1):
        c.drawLine(sx * 40, -300, sx * 40, -250, paint((230, 190, 60), stroke=8))
    for i, side in enumerate((-1, 1)):
        _limb(c, side * 64, -280, arms[2 * i], arms[2 * i + 1], 70, 64, side, (40, 80, 160), 30, glove=WHITE)
    shade(c, D.rrect(-26, -330, 26, -296, 6), (190, 170, 120), k=0.3)                                   # the screw base
    for j in range(3):
        c.drawLine(-26, -326 + j * 11, 26, -322 + j * 11, paint((140, 120, 80), stroke=3))
    c.drawCircle(0, -410, 92 * glow + 40, paint((255, 230, 150), 0.28 * glow, blur=40))                  # the glow
    bulb = D.oval(-70, -500, 70, -330)
    c.drawPath(bulb, paint(shader=D.rad((-20, -440), 110, [(255, 252, 230), (255, 236, 170), (240, 200, 120)]), a=0.95))
    c.drawPath(bulb, paint((200, 170, 110), 0.7, stroke=3))
    c.drawOval(skia.Rect.MakeLTRB(-46, -482, -14, -440), paint(WHITE, 0.7))
    for sx in (-1, 1):                                                                                    # filament face
        c.drawCircle(sx * 22, -420, 7, paint((120, 60, 20)))
    p = skia.Path()
    if talk > 0.05:
        c.drawOval(skia.Rect.MakeLTRB(-14, -398, 14, -398 + 20 * talk), paint((120, 60, 20)))
    else:
        p.moveTo(-18, -396)
        p.quadTo(0, -382 if mood == "smile" else -396, 18, -396)
        c.drawPath(p, paint((120, 60, 20), stroke=4))
    c.restore()


def _profile(kind):
    """Standing and seated profiles (facing right), feet (or seat) at (0, 0), about 900 px tall."""
    if kind == "stand":
        body = [(-12, -735), (-42, -700), (-58, -560), (-42, -450), (-66, -380), (-48, -200), (-44, -20), (-40, 0), (70, 0),
                (60, -20), (30, -200), (42, -330), (56, -420), (44, -500), (72, -600), (44, -700), (26, -742)]
        head = [(10, -800, 52, 62)]
        arm = [((2, -690), (30, -520), (40, -380))]
    else:                                                               # seated at a table, typing
        body = [(4, -590), (-30, -520), (-44, -400), (-46, -300), (80, -300), (86, -420), (76, -520), (52, -592)]
        head = [(36, -650, 50, 58)]
        arm = [((26, -540), (100, -420), (200, -360))]
    return body, head, arm


def silhouette(c, kind, x, y, s, color=(30, 22, 30), a=1.0):
    """The true story is never shown as real faces: backlit profiles, like an illustration."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    p = paint(color, a)
    if kind in ("mother", "mother_seated", "surgeon", "boy"):
        if kind == "boy":
            c.scale(0.62, 0.62)
        body, head, arm = _profile("seat" if kind == "mother_seated" else "stand")
        c.drawPath(D.smooth(body), p)
        for hx, hy, rx, ry in head:
            c.drawPath(D.oval(hx - rx, hy - ry, hx + rx, hy + ry), p)
            c.drawPath(path([(hx + rx - 6, hy - 6), (hx + rx + 14, hy + 10), (hx + rx - 4, hy + 16)]), p)      # the nose
            if kind in ("mother", "mother_seated"):
                c.drawPath(D.circle(hx - rx - 8, hy - 10, 30), p)                                           # a bun
            if kind == "surgeon":
                c.drawPath(D.rrect(hx - rx - 4, hy - ry - 10, hx + rx + 4, hy - ry * 0.35, 20), p)          # scrub cap
            if kind == "boy":
                c.drawPath(D.oval(hx - rx - 6, hy - ry - 8, hx + rx - 4, hy - ry * 0.3), p)                  # a mop of hair
        for (x0, y0), (x1, y1), (x2, y2) in arm:
            c.drawPath(D.capsule(x0, y0, x1, y1, 44, 38), p)
            c.drawPath(D.capsule(x1, y1, x2, y2, 38, 30), p)
    c.restore()

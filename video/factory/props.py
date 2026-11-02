"""Props and inventions, built like a 1971 art department would: brass, plywood, sugar glass and paint.

The golden ticket (the motif), the chocolate bar, your dad's letter (jargon in, plain words out), fifty reports,
and the four machines: the taffy-puller that untangles jargon, the brass press that squeezes fifty studies down to
what matters, the mirror that argues back, and the kitchen of what-if (a fizzing kettle, an oven that bakes a plan).
"""
import math

import numpy as np
import skia

import draw as D
from draw import (CARAMEL, CHERRY, CHOC, CHOC2, CREAM, GOLD, GOLD2, GOLD3, INK, LEMON, LILAC, MINT, PAPER, PINK, TEAL,
                  WHITE, mix, paint, path, shade)

JARGON = [("peripheral neuropathy", "damaged nerves in the feet"), ("bilateral", "on both sides"), ("etiology unconfirmed", "cause not confirmed yet"),
          ("paresthesia", "pins and needles"), ("prognosis", "what happens next"), ("benign", "not cancer")]


def ticket(c, x, y, w, rot=0.0, lines=("ADMIT ONE MIND", "BRING A QUESTION"), glow=0.6, T=0.0, flip=0.0, tag="ticket", head="GOLDEN TICKET"):
    """The golden ticket: gold foil, a scalloped border, engraved lettering, a shine that runs across it."""
    h = w * 0.52
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(max(0.02, abs(math.cos(flip * math.pi))), 1.0)
    if glow > 0:
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-w * 0.6, -h * 0.65, w * 0.6, h * 0.65), 40, 40),
                    paint((255, 210, 120), 0.2 * glow, blur=w * 0.08))
    body = D.rrect(-w / 2, -h / 2, w / 2, h / 2, w * 0.04)
    c.drawPath(body, paint(shader=D.lin((-w / 2, -h / 2), (w / 2, h / 2), [GOLD3, (226, 184, 80), (210, 160, 50), (236, 200, 110), GOLD3])))
    c.drawPath(D.rrect(-w / 2 + w * 0.03, -h / 2 + w * 0.03, w / 2 - w * 0.03, h / 2 - w * 0.03, w * 0.02), paint(GOLD3, stroke=w * 0.008))
    for i in range(36):                                                  # the scalloped edge
        a = i / 36
        xx = -w / 2 + a * w
        c.drawCircle(xx, -h / 2, w * 0.012, paint(GOLD3))
        c.drawCircle(xx, h / 2, w * 0.012, paint(GOLD3))
    sx = -w / 2 + ((T * 0.6) % 1.4) * w                                  # the shine sweeping across the foil
    c.save()
    c.clipPath(body, doAntiAlias=True)
    c.drawPath(path([(sx, -h), (sx + w * 0.12, -h), (sx - w * 0.1, h), (sx - w * 0.22, h)]), paint(WHITE, 0.22))
    c.restore()
    if abs(math.cos(flip * math.pi)) > 0.25 and head:
        D.text(c, head, 0, -h * 0.26, w * 0.066, "rye-400", (100, 60, 10), tag=tag)
    if abs(math.cos(flip * math.pi)) > 0.25:
        for j, ln in enumerate(lines):
            D.text(c, ln, 0, h * 0.04 + j * w * 0.1, w * (0.075 if j == 0 else 0.055), "fraunces-900" if j == 0 else "oldstandard-700",
                   (90, 50, 10), tag=tag)
    c.restore()


def chocolate(c, x, y, s, openk=0.0, T=0.0):
    """A chocolate bar in a paper wrapper; openk 0..1 peels the wrapper back to a flash of gold foil."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    shade(c, D.rrect(-220, -110, 220, 110, 12), CHOC, k=0.25)
    for i in range(4):
        for j in range(2):
            c.drawRect(skia.Rect.MakeLTRB(-200 + i * 100, -95 + j * 100, -110 + i * 100, -10 + j * 100), paint(CHOC2, 0.8))
    if openk > 0:
        c.drawRect(skia.Rect.MakeLTRB(-220, -110, -220 + 440 * openk, 110), paint(shader=D.lin((-220, 0), (220, 0), [GOLD3, GOLD2, GOLD])))
        c.drawCircle(-220 + 440 * openk, 0, 160 * openk, paint((255, 230, 140), 0.4 * openk, blur=50))
    wrap = D.rrect(-230 + 460 * openk, -118, 230, 118, 10)
    shade(c, wrap, (160, 50, 60), k=0.2)
    if openk < 0.15 and s >= 0.5:
        D.text(c, "NUTTY CRUNCH", 0 + 230 * openk, 20, 56, "chango-400", CREAM, tag="wrapper", a=1 - openk / 0.15)
    c.restore()


def letter(c, x, y, s, T=0.0, plain=0.0, rot=0.0, title="TEST RESULTS"):
    """Your dad's letter: the jargon (plain=0) turning into plain words (plain=1), line by line."""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    c.drawRect(skia.Rect.MakeLTRB(-250, -330, 250, 330).makeOffset(10, 14), paint(INK, 0.3, blur=12))
    shade(c, D.rrect(-250, -330, 250, 330, 6), PAPER, k=0.08)
    D.text(c, title, 0, -260, 40, "oldstandard-700", INK, tag="letter")
    c.drawLine(-200, -235, 200, -235, paint(INK, stroke=3))
    for i, (jar, pl) in enumerate(JARGON[:5]):
        k = min(1.0, max(0.0, plain * 5 - i))
        yy = -160 + i * 100
        if k < 0.5:                                                     # struck through ...
            sz = min(44, 44 * 440 / D.font("special-elite-400", 44).measureText(jar))
            wj = D.text(c, jar, 0, yy, sz, "special-elite-400", INK, tag="letter")
            if k > 0:
                c.drawLine(-wj / 2, yy - 14, -wj / 2 + wj * k * 2, yy - 14, paint((190, 40, 40), stroke=5))
        else:                                                           # ... and swapped for plain words
            D.text(c, pl, 0, yy, min(44, 44 * 440 / D.font("fraunces-700", 44).measureText(pl)), "fraunces-700", (30, 110, 60), tag="letter")
    c.restore()


def reports(c, x, y, n, s=1.0, seed=0):
    """A heap of grey reports (n of them)."""
    rng = np.random.default_rng(seed)
    for i in range(n):
        col = i % 10
        row = i // 10
        xx = x + (col - 4.5) * 70 * s + rng.uniform(-10, 10)
        yy = y - row * 26 * s - (col % 3) * 4
        c.save()
        c.translate(xx, yy)
        c.rotate(rng.uniform(-8, 8))
        shade(c, D.rrect(-60 * s, -22 * s, 60 * s, 0, 3), mix((200, 196, 186), (120, 118, 112), rng.uniform(0, 0.5)), k=0.1, edge=0.6)
        c.restore()


def clock(c, x, y, r, hours, T=0.0, face=CREAM):
    shade(c, D.circle(x, y, r), face, k=0.1)
    c.drawCircle(x, y, r, paint((70, 50, 40), stroke=r * 0.1))
    for k in range(12):
        a = k * math.pi / 6
        c.drawLine(x + r * 0.78 * math.sin(a), y - r * 0.78 * math.cos(a), x + r * 0.88 * math.sin(a), y - r * 0.88 * math.cos(a),
                   paint(INK, stroke=r * 0.04))
    ah = hours / 12 * 2 * math.pi
    am = hours % 1 * 2 * math.pi
    c.drawLine(x, y, x + r * 0.5 * math.sin(ah), y - r * 0.5 * math.cos(ah), paint(INK, stroke=r * 0.08))
    c.drawLine(x, y, x + r * 0.75 * math.sin(am), y - r * 0.75 * math.cos(am), paint(INK, stroke=r * 0.05))


def rain(c, T, a=0.5, n=160, x0=0, x1=1080, y0=0, y1=1920, seed=1):
    rng = np.random.default_rng(seed)
    xs, ys = rng.uniform(x0, x1, n), rng.uniform(0, 1, n)
    for x, u in zip(xs, ys):
        yy = y0 + ((u + T * 1.6) % 1.0) * (y1 - y0)
        c.drawLine(x, yy, x - 8, yy + 50, paint((210, 216, 226), a, stroke=2))


def umbrella_man(c, x, y, s, T, col=(40, 40, 46)):
    """A passer-by under a black umbrella: grey coat, head down."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawPath(D.rrect(-60, -560, 60, -60, 30), paint(mix(col, (90, 90, 96), 0.4)))
    c.drawPath(D.rrect(-45, -80, -10, 0, 10), paint(col))
    c.drawPath(D.rrect(10, -80, 45, 0, 10), paint(col))
    c.drawCircle(0, -600, 42, paint((150, 130, 120)))
    p = skia.Path()
    p.moveTo(-190, -640)
    p.quadTo(0, -860, 190, -640)
    p.close()
    c.drawPath(p, paint(col))
    c.drawLine(0, -780, 0, -560, paint((30, 30, 30), stroke=6))
    c.restore()


# ------------------------------------------------------------------ the four machines

def taffy_puller(c, x, y, s, T, untangle=0.0):
    """Two brass arms turning in figure-eights, pulling a knot of jargon into a smooth pastel ribbon."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    shade(c, D.rrect(-300, -80, 300, 60, 24), (150, 100, 60), k=0.3)                                    # the cabinet
    shade(c, D.rrect(-260, -520, 260, -80, 40), (220, 180, 90), k=0.3)
    c.drawCircle(0, -300, 150, paint((120, 80, 50)))
    for i in range(2):
        a = T * 3.0 + i * math.pi
        ax, ay = 120 * math.cos(a), -300 + 60 * math.sin(2 * a)
        c.drawLine(0, -300, ax, ay, paint((200, 170, 90), stroke=22))
        c.drawCircle(ax, ay, 26, paint(GOLD))
    k = untangle
    rng = np.random.default_rng(3)
    knot = skia.Path()                                                   # the tangled knot (fades) ...
    pts = [(rng.uniform(-110, 110), -300 + rng.uniform(-110, 110)) for _ in range(14)]
    knot.moveTo(*pts[0])
    for q in pts[1:]:
        knot.lineTo(*q)
    c.drawPath(knot, paint((170, 160, 150), 1 - k, stroke=16))
    rib = skia.Path()                                                    # ... into a smooth ribbon out the side
    rib.moveTo(150, -300)
    for j in range(1, 9):
        rib.lineTo(150 + j * 60 * k, -300 + 40 * math.sin(j * 0.9 + T * 4) * k)
    c.drawPath(rib, paint(PINK, k, stroke=34))
    c.drawPath(rib, paint(WHITE, 0.6 * k, stroke=8))
    c.restore()


def press(c, x, y, s, T, down=0.0, count=50):
    """A great brass screw press over a conveyor; the platen comes down on a pile of reports."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    for sx in (-1, 1):
        shade(c, D.rrect(sx * 300 - 40, -900, sx * 300 + 40, 0, 20), (190, 140, 60), k=0.35)
    shade(c, D.rrect(-340, -960, 340, -860, 30), (170, 120, 50), k=0.35)
    c.drawLine(0, -860, 0, -560 + 260 * down, paint((120, 90, 50), stroke=40))                          # the screw
    for j in range(8):
        yy = -840 + j * 34 + (T * 120 % 34)
        if yy < -560 + 260 * down:
            c.drawLine(-22, yy, 22, yy + 12, paint((200, 170, 100), stroke=6))
    c.save()
    c.translate(0, -900)
    c.rotate(T * 90)
    c.drawLine(-240, 0, 240, 0, paint(GOLD3, stroke=24))                                                # the wheel
    c.restore()
    shade(c, D.rrect(-260, -560 + 260 * down, 260, -500 + 260 * down, 16), (160, 110, 50), k=0.3)      # the platen
    shade(c, D.rrect(-420, -40, 420, 40, 20), (80, 70, 70), k=0.25)                                    # the conveyor
    for j in range(12):
        c.drawCircle(-400 + j * 72 + (T * 60 % 72), 0, 16, paint((140, 130, 130)))
    D.text(c, f"{count}", 0, -660, 120, "fraunces-900", CREAM, tag="press", outline=INK, ow=16)
    c.restore()


def mirror(c, x, y, s, T, mood="sly", talk=0.0, glow=0.0):
    """A tall gilded mirror whose glass has a face of its own."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    frame = D.oval(-280, -760, 280, 20)
    shade(c, frame, GOLD, k=0.35)
    for i in range(16):
        a = i / 16 * 2 * math.pi
        c.drawCircle(280 * math.cos(a) * 0.98, -370 + 390 * math.sin(a) * 0.98, 30, paint(GOLD3))
    glass = D.oval(-230, -700, 230, -40)
    c.drawPath(glass, paint(shader=D.lin((-230, -700), (230, -40), [(200, 220, 230), (150, 170, 190), (210, 225, 235)])))
    c.drawPath(D.oval(-180, -660, -60, -380), paint(WHITE, 0.25))
    if glow:
        c.drawPath(glass, paint((255, 200, 120), 0.3 * glow))
    c.save()                                                             # the face in the glass: brows, eyes, a mouth
    c.translate(0, -380)
    c.scale(2.4, 2.4)
    import cast
    cast.face(c, {"hair_c": (70, 80, 100)}, mood, 0.0, False, talk, 60)
    c.restore()
    c.restore()


def scales(c, x, y, s, T, tip=0.0, left="TREATMENT A", right="TREATMENT B"):
    """A brass balance weighing two options, each pan holding its case-against card."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    shade(c, D.rrect(-20, -420, 20, 0, 10), GOLD3, k=0.3)
    shade(c, D.rrect(-120, -30, 120, 10, 10), GOLD3, k=0.3)
    ang = 8 * tip + 3 * math.sin(T * 1.5)
    c.save()
    c.translate(0, -420)
    c.rotate(ang)
    c.drawLine(-280, 0, 280, 0, paint(GOLD, stroke=18))
    for sx, lbl in ((-1, left), (1, right)):
        c.save()
        c.translate(sx * 280, 0)
        c.rotate(-ang)
        c.drawLine(-80, 160, 0, 0, paint(GOLD3, stroke=4))
        c.drawLine(80, 160, 0, 0, paint(GOLD3, stroke=4))
        shade(c, D.oval(-110, 150, 110, 190), GOLD, k=0.3)
        shade(c, D.rrect(-110, 40, 110, 150, 8), CREAM, k=0.1)
        D.text(c, lbl, 0, 80, 26, "fraunces-900", INK, tag="scales")
        D.text(c, "for · against", 0, 124, 24, "oldstandard-700", (140, 40, 40), tag="scales")
        c.restore()
    c.restore()
    c.restore()


def kettle(c, x, y, s, T, fizz=1.0):
    """A copper kettle on a stove, fizzing."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    shade(c, D.rrect(-260, -40, 260, 60, 20), (60, 60, 64), k=0.3)
    shade(c, D.oval(-220, -380, 220, -20), (200, 110, 60), k=0.35)
    shade(c, D.rrect(-60, -440, 60, -360, 20), (170, 90, 50), k=0.3)
    c.drawLine(200, -220, 330, -330, paint((190, 100, 55), stroke=36))
    c.drawCircle(0, -200, 60, paint(WHITE, 0.3))
    c.restore()


SLOTS = [(250, 420), (560, 330), (850, 440), (330, 700), (760, 720), (540, 560)]


def bubbles(c, T, words, x=540, y=1100, spread=380, t0=0.0, gold=None, popped=(), dy=0):
    """Idea bubbles fizzing up out of the kettle into a cloud of possibilities; most pop, the gold one stays.
    A "|" in a word breaks it over two lines."""
    for i, w in enumerate(words):
        age = T - t0 - i * 0.35
        if age < 0:
            continue
        sx, sy = SLOTS[i % len(SLOTS)]
        sy += dy
        u = min(1.0, age / 0.7)
        bx = x + (sx - x) * u + 14 * math.sin(T * 2 + i)
        by = y + (sy - y) * u + 12 * math.cos(T * 1.7 + i)
        isg = gold is not None and i == gold
        r = (70 + 40 * u) * (1.25 if isg else 1.0)
        if i in popped and age > 1.6:
            for k in range(8):
                a = k * math.pi / 4
                c.drawLine(bx + r * 0.6 * math.cos(a), by + r * 0.6 * math.sin(a), bx + r * 0.95 * math.cos(a),
                           by + r * 0.95 * math.sin(a), paint(WHITE, max(0.0, 1 - (age - 1.6) * 3), stroke=5))
            continue
        col = (255, 220, 120) if isg else (220, 240, 255)
        c.drawCircle(bx, by, r, paint(col, 0.45 if not isg else 0.8))
        c.drawCircle(bx, by, r, paint(GOLD3 if isg else WHITE, 0.8, stroke=6 if isg else 4))
        c.drawOval(skia.Rect.MakeLTRB(bx - r * 0.6, by - r * 0.7, bx - r * 0.1, by - r * 0.35), paint(WHITE, 0.6))
        lines = w.split("|")
        f = D.font("fraunces-900", 34)
        sz = min(34 * (1.15 if isg else 1.0), min(34 * r * 1.6 / max(1, f.measureText(l)) for l in lines))
        for j, l in enumerate(lines):
            D.text(c, l, bx, by + 12 + (j - (len(lines) - 1) / 2) * sz * 1.05, sz, "fraunces-900",
                   (70, 40, 20) if isg else (40, 50, 80), tag="bubble")


def plan_card(c, x, y, s, T, k=1.0):
    """The baked plan: a crisp blueprint card - what you know, what you don't, what if, and what to ask."""
    c.save()
    c.translate(x, y)
    c.scale(s * (0.6 + 0.4 * k), s * (0.6 + 0.4 * k))
    shade(c, D.rrect(-300, -380, 300, 380, 16), (40, 90, 160), k=0.12)
    for j in range(12):
        c.drawLine(-300, -380 + j * 64, 300, -380 + j * 64, paint(WHITE, 0.12, stroke=2))
        c.drawLine(-300 + j * 55, -380, -300 + j * 55, 380, paint(WHITE, 0.12, stroke=2))
    D.text(c, "THE PLAN", 0, -300, 54, "fraunces-900", WHITE, tag="plan")
    rows = [("WE KNOW", "numb feet, both sides"), ("WE DON'T", "the cause"), ("WHAT IF", "we wait? (it can become permanent)"),
            ("ASK", "1. could his diabetes pill lower his B12?"), ("", "2. which blood test would show it?"), ("", "3. what else could it be?")]
    for j, (a, b) in enumerate(rows):
        yy = -200 + j * 96
        if a:
            D.text(c, a, -270, yy, 32, "fraunces-900", LEMON, tag="plan", align="left")
        f = D.font("oldstandard-700", 30)
        sz = min(30, 30 * 540 / max(1, f.measureText(b)))
        D.text(c, b, -270, yy + 40, sz, "oldstandard-700", WHITE, tag="plan", align="left")
    c.restore()


def oven(c, x, y, s, T, glow=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    shade(c, D.rrect(-240, -420, 240, 0, 24), (230, 220, 200), k=0.25)
    shade(c, D.rrect(-190, -330, 190, -60, 16), (60, 50, 50), k=0.2)
    c.drawRect(skia.Rect.MakeLTRB(-170, -310, 170, -80), paint((255, 150, 60), 0.35 + 0.4 * glow))
    for j in range(4):
        c.drawCircle(-150 + j * 100, -380, 18, paint((120, 110, 100)))
    c.restore()


def plaque(c, x, y, n, name, uses, a=1.0):
    """A brass door plaque: the room number, its name, and the kinds of thinking it helps with (one column when they fit)."""
    c.save()
    c.translate(x, y)
    cols = 1 if len(uses) <= 3 else 2
    rows = math.ceil(len(uses) / cols)
    w, h = 860, 200 + 58 * rows
    shade(c, D.rrect(-w / 2, 0, w / 2, h, 24), GOLD, k=0.3, a=a)
    c.drawPath(D.rrect(-w / 2 + 14, 14, w / 2 - 14, h - 14, 16), paint(GOLD3, a, stroke=5))
    D.text(c, f"ROOM {n}", 0, 72, 44, "rye-400", (100, 60, 10), tag="plaque", a=a)
    ns = min(60, 60 * (w - 90) / D.font("fraunces-900", 60).measureText(name))
    D.text(c, name, 0, 142, ns, "fraunces-900", (70, 40, 10), tag="plaque", a=a)
    cw = (w - 100) / cols
    us = min(42, min(42 * (cw - 20) / D.font("fraunces-700", 42).measureText("· " + u) for u in uses))
    for j, u in enumerate(uses):
        col, row = j % cols, j // cols
        cx = 0 if cols == 1 else -w / 4 + col * w / 2
        D.text(c, "· " + u, cx, 210 + row * 58, us, "fraunces-700", (90, 55, 15), tag="plaque", a=a)
    c.restore()


def headline(c, x, y, s, rot, big, small, a=1.0):
    """A newspaper front page, as it spins into the newsreel."""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    shade(c, D.rrect(-400, -260, 400, 260, 4), (236, 232, 222), k=0.05, a=a)
    D.text(c, "THE DAILY GAZETTE", 0, -190, 44, "oldstandard-700", INK, tag="headline", a=a)
    c.drawLine(-370, -170, 370, -170, paint(INK, a, stroke=4))
    for size in (88, 78, 68, 60):
        lines = D.wrap_balanced(big, D.font("fraunces-900", size), 740)
        if len(lines) <= 2:
            break
    for j, ln in enumerate(lines):
        D.text(c, ln, 0, -60 + j * size * 1.08 - (size * 0.54 if len(lines) == 1 else 0), size, "fraunces-900", INK, tag="headline", a=a)
    parts = small.split("|")
    if len(parts) == 1:
        sz = min(36, 36 * 740 / max(1, D.font("oldstandard-700", 36).measureText(small)))
        D.text(c, small, 0, 205, sz, "oldstandard-700", (50, 50, 50), tag="headline", a=a)
    else:                                                               # the condition, large; the source beneath
        sz = min(50, 50 * 720 / max(1, D.font("fraunces-900", 50).measureText(parts[0].upper())))
        D.text(c, parts[0].upper(), 0, 172, sz, "fraunces-900", (140, 30, 30), tag="headline", a=a)
        sz2 = min(30, 30 * 740 / max(1, D.font("oldstandard-700", 30).measureText(parts[1])))
        D.text(c, parts[1], 0, 226, sz2, "oldstandard-700", (50, 50, 50), tag="headline", a=a)
    c.restore()


def boat(c, x, y, s, T, heads=("you", "host")):
    """The tunnel boat: a painted paddle boat with a swan's-neck prow."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    p = skia.Path()
    p.moveTo(-420, -120)
    p.quadTo(0, 60, 420, -120)
    p.lineTo(380, -10)
    p.quadTo(0, 120, -380, -10)
    p.close()
    shade(c, p, (230, 120, 170), k=0.3)
    c.drawLine(380, -110, 470, -380, paint((240, 240, 240), stroke=40))                                # the prow
    c.drawCircle(480, -400, 38, paint((240, 240, 240)))
    c.restore()


def lamp(c, x, y, r, a=1.0):
    c.drawCircle(x, y, r * 3, paint((255, 220, 150), 0.25 * a, blur=r))

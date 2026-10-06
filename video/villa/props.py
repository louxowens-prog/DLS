"""Things: the clock face and its automaton figures, papers with perfect grades, diplomas, gilded frames, candelabra,
gears, keys, ledgers, the code sheet and the modern phone."""
import math

import numpy as np
import skia

import gel as G
import kit as K
from kit import BLACK, GOLD, INK, PAPER, WHITE, mix, paint

ROMAN = ["XII", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"]


def clock_face(c, x, y, r, hour=9.0, minute=0.0, light=1.0, label=None, label_size=None, tag="plaque", hands_a=1.0,
               dial=(236, 226, 200)):
    """An ornate clock face: gilded ring, enamel dial, Roman numerals, a sun and moon, filigree hands."""
    c.save()
    c.translate(x, y)
    c.drawCircle(0, 0, r * 1.12, paint(mix(GOLD, BLACK, 0.45)))
    c.drawCircle(0, 0, r * 1.08, paint(shader=K.rad((-r * 0.3, -r * 0.3), r * 1.4, [mix(GOLD, WHITE, 0.35), GOLD, mix(GOLD, BLACK, 0.5)])))
    c.drawCircle(0, 0, r * 0.96, paint(mix(dial, BLACK, 0.12 * (1 - light))))
    c.drawCircle(0, 0, r * 0.96, paint(shader=K.rad((0, 0), r, [(0, 0, 0, 0.0), (0, 0, 0, 0.0), (60, 40, 20, 0.35)], [0, 0.7, 1])))
    f = K.font("cinzel-600", r * 0.15)
    for i, num in enumerate(ROMAN):
        ang = math.radians(i * 30 - 90)
        tx, ty = math.cos(ang) * r * 0.8, math.sin(ang) * r * 0.8
        c.save()
        c.translate(tx, ty)
        c.rotate(i * 30)
        w = f.measureText(num)
        c.drawString(num, -w / 2, r * 0.055, f, paint(INK))
        c.restore()
    for i in range(60):
        ang = math.radians(i * 6)
        r0 = r * (0.9 if i % 5 else 0.87)
        c.drawLine(math.cos(ang) * r0, math.sin(ang) * r0, math.cos(ang) * r * 0.94, math.sin(ang) * r * 0.94,
                   paint(INK, 0.8, stroke=r * (0.012 if i % 5 else 0.02)))
    c.drawCircle(0, 0, r * 0.62, paint(mix(INK, GOLD, 0.3), 0.6, stroke=r * 0.012))
    # a sun and a crescent moon on the dial
    c.drawCircle(0, -r * 0.36, r * 0.09, paint(GOLD))
    for k in range(12):
        a = k * math.pi / 6
        c.drawLine(math.cos(a) * r * 0.1, -r * 0.36 + math.sin(a) * r * 0.1, math.cos(a) * r * 0.15, -r * 0.36 + math.sin(a) * r * 0.15,
                   paint(GOLD, stroke=r * 0.012))
    c.drawCircle(0, r * 0.36, r * 0.08, paint((40, 40, 70)))
    c.drawCircle(r * 0.03, r * 0.35, r * 0.07, paint(mix(dial, BLACK, 0.12 * (1 - light))))
    if label:
        fl = K.font("cinzel-600", label_size or r * 0.13)
        w = fl.measureText(label)
        c.drawString(label, -w / 2, r * 0.2, fl, paint((140, 20, 30)))
        K.reg_local(c, -w / 2, r * 0.2 - (label_size or r * 0.13) * 0.8, w / 2, r * 0.2 + 4, tag)
    # hands
    ha = math.radians((hour % 12 + minute / 60) * 30 - 90)
    ma = math.radians(minute * 6 - 90)
    for ang, L, wd in ((ha, r * 0.5, r * 0.05), (ma, r * 0.78, r * 0.032)):
        c.save()
        c.rotate(math.degrees(ang))
        hp = K.path([(-r * 0.1, -wd * 0.4), (L * 0.75, -wd * 0.6), (L, 0), (L * 0.75, wd * 0.6), (-r * 0.1, wd * 0.4)])
        c.drawPath(hp, paint((30, 22, 18), hands_a))
        c.drawCircle(L * 0.55, 0, wd * 0.9, paint((30, 22, 18), hands_a, stroke=wd * 0.35))
        c.restore()
    c.drawCircle(0, 0, r * 0.05, paint(GOLD))
    c.restore()


def figurine(c, x, y, s, T, kind="scholar", porc=1.0, arm=0.0, face_color=(244, 238, 232), seed=0, lit=(255, 170, 70), hair=None):
    """A little automaton figure about 160 px tall at s = 1, standing on a disc: a scholar in gown and mortarboard,
    or the tall governess figure with a scroll."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawOval(skia.Rect.MakeLTRB(-40, -8, 40, 10), paint(mix(GOLD, BLACK, 0.4)))
    if kind == "scholar":
        gown = K.smooth([(-34, 0), (-30, -70), (-18, -104), (18, -104), (30, -70), (34, 0)])
        c.drawPath(gown, paint((22, 18, 28)))
        c.drawPath(K.smooth([(-16, -104), (0, -90), (16, -104), (8, -80), (-8, -80)]), paint((150, 20, 40)))
        if hair is not None:
            c.drawPath(K.smooth([(-26, -140), (0, -150), (26, -140), (30, -96), (18, -86), (-18, -86), (-30, -96)]), paint(hair))
        c.drawCircle(0, -124, 20, paint(face_color))
        c.drawCircle(-6, -126, 2.2, paint(INK))
        c.drawCircle(6, -126, 2.2, paint(INK))
        c.drawCircle(0, -116, 2.5, paint((190, 40, 60)))
        c.drawPath(K.path([(-28, -142), (0, -152), (28, -142), (0, -134)]), paint((20, 18, 24)))
        c.drawRect(skia.Rect.MakeLTRB(-14, -144, 14, -136), paint((20, 18, 24)))
        c.drawLine(18, -142, 26 + 4 * math.sin(T * 3 + seed), -124, paint(GOLD, stroke=2))
        # the scroll held out
        c.save()
        c.translate(22, -70)
        c.rotate(-30 + arm * 30)
        c.drawRoundRect(skia.Rect.MakeLTRB(0, -5, 34, 5), 5, 5, paint(PAPER))
        c.drawCircle(17, 0, 3, paint((190, 30, 40)))
        c.restore()
    else:                                                     # the governess automaton
        gown = K.smooth([(-40, 0), (-34, -90), (-22, -150), (22, -150), (34, -90), (40, 0)])
        c.drawPath(gown, paint((12, 10, 14)))
        c.drawRect(skia.Rect.MakeLTRB(-10, -168, 10, -150), paint((20, 16, 22)))
        c.drawCircle(0, -184, 20, paint((246, 242, 236)))
        c.drawCircle(0, -206, 12, paint((18, 14, 16)))
        c.drawCircle(-6, -186, 2, paint(INK))
        c.drawCircle(6, -186, 2, paint(INK))
        c.save()
        c.translate(-24, -120)
        c.rotate(200 - arm * 50)
        c.drawRoundRect(skia.Rect.MakeLTRB(0, -5, 60, 5), 5, 5, paint((12, 10, 14)))
        c.drawRoundRect(skia.Rect.MakeLTRB(50, -6, 84, 6), 5, 5, paint(PAPER))
        c.restore()
    # gel light: warm from below, a cool rim
    sh = K.lin((0, 0), (0, -220), [lit + (0.35,), lit + (0.0,)])
    p = paint(lit, 1.0, shader=sh)
    p.setBlendMode(skia.BlendMode.kPlus)
    c.drawRect(skia.Rect.MakeLTRB(-50, -230, 50, 10), p)
    c.restore()


def paper(c, x, y, w, h, ang, T, title=None, grade="A+", lines=9, name=None, tag="deco", seed=0, a=1.0, kind="essay",
          title_size=None):
    """A sheet of work with a perfect grade in red: an essay, homework, code, a report or a discussion post."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.drawRect(skia.Rect.MakeLTRB(-w / 2 + 6, -h / 2 + 8, w / 2 + 6, h / 2 + 8), paint((0, 0, 0), 0.35 * a, blur=10))
    c.drawRect(skia.Rect.MakeLTRB(-w / 2, -h / 2, w / 2, h / 2), paint(mix(PAPER, WHITE, 0.3), a))
    c.drawRect(skia.Rect.MakeLTRB(-w / 2, -h / 2, w / 2, h / 2), paint(shader=K.lin((-w / 2, -h / 2), (w / 2, h / 2),
                                                                                    [(255, 255, 255, 0.0), (120, 90, 50, 0.18 * a)])))
    rng = K.rng_at(seed, 11)
    top = -h / 2 + h * 0.2
    if title:
        f = K.font("cinzel-600", title_size or w * 0.085)
        tw = f.measureText(title)
        c.drawString(title, -tw / 2, -h / 2 + h * 0.13, f, paint(INK, a))
        K.reg_local(c, -tw / 2, -h / 2 + h * 0.13 - (title_size or w * 0.085) * 0.8, tw / 2, -h / 2 + h * 0.13 + 4, tag)
    if name:
        f = K.font("playfair-400i", w * 0.06)
        tw = f.measureText(name)
        c.drawString(name, -tw / 2, -h / 2 + h * 0.2, f, paint(mix(INK, (90, 60, 40), 0.4), a))
        K.reg_local(c, -tw / 2, -h / 2 + h * 0.2 - w * 0.05, tw / 2, -h / 2 + h * 0.2 + 4, tag)
        top += h * 0.04
    for i in range(lines):
        yy = top + i * (h * 0.66 / max(1, lines))
        if kind == "code":
            ind = (i % 4 in (1, 2)) * w * 0.08
            c.drawRect(skia.Rect.MakeLTRB(-w * 0.38 + ind, yy - 3, -w * 0.38 + ind + w * rng.uniform(0.25, 0.6), yy + 3), paint((40, 90, 60), 0.75 * a))
        else:
            ww = w * (0.76 if i < lines - 1 else rng.uniform(0.3, 0.6))
            c.drawRect(skia.Rect.MakeLTRB(-w * 0.38, yy - 2, -w * 0.38 + ww, yy + 2), paint(mix(INK, PAPER, 0.35), 0.8 * a))
    if grade:
        f = K.font("playfair-700", w * 0.2)
        c.save()
        c.translate(w * 0.22, h * 0.3)
        c.rotate(-12)
        c.drawCircle(0, -w * 0.06, w * 0.17, paint((200, 20, 30), 0.9 * a, stroke=w * 0.02))
        gw = f.measureText(grade)
        c.drawString(grade, -gw / 2, 0, f, paint((200, 20, 30), a))
        c.restore()
    c.restore()


def frame_gilt(c, x0, y0, x1, y1, t=26, a=1.0):
    """A gilded picture frame (drawn over the picture's edges)."""
    for i in range(5):
        k = i / 4
        col = mix(mix(GOLD, BLACK, 0.55), mix(GOLD, WHITE, 0.3), math.sin(k * math.pi))
        c.drawRect(skia.Rect.MakeLTRB(x0 - t + i * t / 5, y0 - t + i * t / 5, x1 + t - i * t / 5, y1 + t - i * t / 5),
                   paint(col, a, stroke=t / 5 + 1))
    for (cx, cy) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        c.drawCircle(cx, cy, t * 0.6, paint(mix(GOLD, WHITE, 0.2), a))
        c.drawCircle(cx, cy, t * 0.35, paint(mix(GOLD, BLACK, 0.4), a))


def candelabra(c, x, y, s, T, a=1.0, glow=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    br = paint((150, 110, 50), a)
    c.drawRect(skia.Rect.MakeLTRB(-8, -40, 8, 160), br)
    c.drawOval(skia.Rect.MakeLTRB(-50, 150, 50, 175), br)
    arm = skia.Path()
    arm.moveTo(-90, -40)
    arm.quadTo(0, 30, 90, -40)
    c.drawPath(arm, paint((150, 110, 50), a, stroke=10))
    for i, cx in enumerate((-90, 0, 90)):
        G.candle(c, cx, -90 if cx else -110, 0.75, T, a=a, seed=i, glow=glow)
    c.restore()


def plaque(c, x, y, lines, size=40, w=None, font="cinzel-600", a=1.0, tag="plaque", color=(60, 40, 20), metal=GOLD,
           sizes=None, gap=1.25):
    """An engraved brass plaque with lines of text, centred at (x, y)."""
    sizes = sizes or [size] * len(lines)
    fs = [K.font(font, s) for s in sizes]
    tw = max(f.measureText(ln) for f, ln in zip(fs, lines))
    w = w or tw + size * 1.6
    h = sum(s * gap for s in sizes) + size * 0.9
    x0, y0 = x - w / 2, y - h / 2
    c.drawRoundRect(skia.Rect.MakeLTRB(x0 + 6, y0 + 8, x0 + w + 6, y0 + h + 8), 10, 10, paint((0, 0, 0), 0.5 * a, blur=8))
    c.drawRoundRect(skia.Rect.MakeLTRB(x0, y0, x0 + w, y0 + h), 10, 10,
                    paint(shader=K.lin((x0, y0), (x0 + w, y0 + h), [mix(metal, WHITE, 0.35), metal, mix(metal, BLACK, 0.35)]), a=a))
    c.drawRoundRect(skia.Rect.MakeLTRB(x0 + 8, y0 + 8, x0 + w - 8, y0 + h - 8), 6, 6, paint(mix(metal, BLACK, 0.5), 0.8 * a, stroke=3))
    yy = y0 + size * 0.45
    for f, s, ln in zip(fs, sizes, lines):
        yy += s * gap
        lw = f.measureText(ln)
        c.drawString(ln, x - lw / 2, yy - s * 0.22, f, paint(color, a))
        K.reg_local(c, x - lw / 2, yy - s * 0.22 - s * 0.78, x + lw / 2, yy - s * 0.22 + s * 0.22, tag)
    return (x0, y0, x0 + w, y0 + h)


def gear(c, x, y, r, teeth, ang, color=(176, 132, 60), hub=True, spokes=5, glyphs=None, a=1.0, depth=1.0):
    """A brass gear: teeth, a rim, spokes, a hub; engraved glyphs on the rim if given."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    p = skia.Path()
    n = teeth * 2
    for i in range(n * 2 + 1):
        t = i / (n * 2) * 2 * math.pi
        rr = r * (1.0 if (i // 2) % 2 == 0 else 0.88)
        pt = (math.cos(t) * rr, math.sin(t) * rr)
        if i == 0:
            p.moveTo(*pt)
        else:
            p.lineTo(*pt)
    p.close()
    dk = mix(color, BLACK, 0.5)
    c.drawPath(p, paint(shader=K.rad((-r * 0.3, -r * 0.3), r * 1.5, [mix(color, WHITE, 0.3), color, dk]), a=a))
    c.drawCircle(0, 0, r * 0.78, paint(dk, a, stroke=r * 0.04))
    inner = r * 0.7
    for k in range(spokes):
        t = k / spokes * 360
        c.save()
        c.rotate(t)
        c.drawRect(skia.Rect.MakeLTRB(r * 0.12, -r * 0.06, inner, r * 0.06), paint(mix(color, BLACK, 0.2), a))
        c.restore()
    hole = skia.Path()
    hole.setFillType(skia.PathFillType.kEvenOdd)
    hole.addCircle(0, 0, inner)
    for k in range(spokes):
        t0 = math.radians(k / spokes * 360 + 9)
        t1 = math.radians((k + 1) / spokes * 360 - 9)
        seg = skia.Path()
        seg.moveTo(math.cos(t0) * r * 0.16, math.sin(t0) * r * 0.16)
        seg.arcTo(skia.Rect.MakeLTRB(-inner + 6, -inner + 6, inner - 6, inner - 6), math.degrees(t0), math.degrees(t1 - t0), False)
        seg.close()
        c.drawPath(seg, paint((6, 4, 6), a * depth))
    if hub:
        c.drawCircle(0, 0, r * 0.16, paint(mix(color, WHITE, 0.2), a))
        c.drawCircle(0, 0, r * 0.06, paint(dk, a))
    if glyphs:
        f = K.font("courier-400", r * 0.085)
        for k, g in enumerate(glyphs):
            t = k / len(glyphs) * 360
            c.save()
            c.rotate(t)
            c.translate(0, -r * 0.8)
            w = f.measureText(g)
            c.drawString(g, -w / 2, r * 0.03, f, paint(mix(color, BLACK, 0.65), a))
            c.restore()
    c.restore()


def gauge(c, x, y, r, value, label, a=1.0, tag="plaque", color=(176, 132, 60), needle=(170, 20, 30)):
    """A brass dial from 0 to 100% with a needle and an engraved label."""
    c.save()
    c.translate(x, y)
    c.drawCircle(0, 0, r * 1.08, paint(mix(color, BLACK, 0.4), a))
    c.drawCircle(0, 0, r, paint((236, 226, 200), a))
    for i in range(11):
        t = math.radians(-225 + i * 27)
        c.drawLine(math.cos(t) * r * 0.78, math.sin(t) * r * 0.78, math.cos(t) * r * 0.92, math.sin(t) * r * 0.92, paint(INK, a, stroke=4))
    f = K.font("cinzel-600", r * 0.15)
    s = "50%"
    w = f.measureText(s)
    c.drawString(s, -w / 2, -r * 0.5, f, paint(INK, a))
    t = math.radians(-225 + 270 * value / 100)
    c.drawLine(0, 0, math.cos(t) * r * 0.85, math.sin(t) * r * 0.85, paint(needle, a, stroke=r * 0.05))
    c.drawCircle(0, 0, r * 0.08, paint(mix(color, BLACK, 0.3), a))
    fv = K.font("playfair-700", r * 0.34)
    s = f"{int(round(value))}%"
    w = fv.measureText(s)
    c.drawString(s, -w / 2, r * 0.62, fv, paint(needle, a))
    K.reg_local(c, -w / 2, r * 0.62 - r * 0.27, w / 2, r * 0.62 + 4, tag)
    c.restore()
    plaque(c, x, y + r * 1.42, [label], size=r * 0.2, a=a, tag=tag)

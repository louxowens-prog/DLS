"""Gel light: the coloured pools, shafts and split-lit faces of a 1970s Italian gothic. Light is added (screen/plus
blending) onto near-black, so whatever is not lit falls away into deep shadow."""
import math

import numpy as np
import skia

import kit as K
from kit import BLACK, WHITE, mix, paint


def glow_paint(color, a, shader=None, blend=skia.BlendMode.kPlus, blur=0.0):
    p = paint(color, a, shader=shader, blur=blur)
    p.setBlendMode(blend)
    return p


def pool(c, x, y, r, color, a=1.0, falloff=(1.0, 0.35, 0.0), squash=1.0, blend=skia.BlendMode.kPlus):
    """A soft round pool of coloured light (additive). squash < 1 flattens it into an ellipse (light on a floor)."""
    if a <= 0.003 or r <= 1:
        return
    c.save()
    c.translate(x, y)
    c.scale(1.0, squash)
    sh = K.rad((0, 0), r, [color + (a * falloff[0],), color + (a * falloff[1],), color + (0.0,)], [0.0, 0.45, 1.0])
    c.drawCircle(0, 0, r, glow_paint(color, 1.0, shader=sh, blend=blend))
    c.restore()


def beam(c, apex, b0, b1, color, a=0.35, fade=0.9):
    """A shaft of light from a small source (apex) widening to the edge b0-b1, fading as it goes."""
    p = K.path([apex, b0, b1])
    mx, my = (b0[0] + b1[0]) / 2, (b0[1] + b1[1]) / 2
    sh = K.lin(apex, (mx, my), [color + (a,), color + (a * (1 - fade),)])
    c.drawPath(p, glow_paint(color, 1.0, shader=sh, blur=6))


def split_fill(c, p, base, left, right, core=0.65, amb=0.06, rim=0.0, rim_color=None, ang=0.0, a=1.0):
    """Fill a shape lit by two coloured gels from opposite sides (rotated by ang degrees), with a dark core between them
    - the face half magenta, half emerald, black down the middle."""
    b = p.computeTightBounds()
    cx, cy, rw = b.centerX(), b.centerY(), b.width() / 2 + 1
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    p0, p1 = (cx - ca * rw, cy - sa * rw), (cx + ca * rw, cy + sa * rw)
    lit_l = tuple(int(min(255, base[i] * left[i] / 255 * 1.25)) for i in range(3))
    lit_r = tuple(int(min(255, base[i] * right[i] / 255 * 1.25)) for i in range(3))
    dark = mix(BLACK, base, amb)
    c.drawPath(p, paint(dark, a))
    sh = K.lin(p0, p1, [lit_l + (1.0,), lit_l + (0.55,), dark + (0.0,), dark + (0.0,), lit_r + (0.55,), lit_r + (1.0,)],
               [0.0, 0.5 * (1 - core), 0.5 - core * 0.12, 0.5 + core * 0.12, 1 - 0.5 * (1 - core), 1.0])
    c.drawPath(p, paint(shader=sh, a=a))
    if rim > 0 and rim_color is not None:
        c.save()
        c.clipPath(p, doAntiAlias=True)
        c.drawPath(p, paint(rim_color, a * rim, stroke=b.width() * 0.05, blur=b.width() * 0.02))
        c.restore()


def side_fill(c, p, base, light, ang=0.0, amb=0.05, k=1.0, soft=0.8, a=1.0):
    """Fill a shape lit from one side by one gel (ang: direction the light comes FROM, degrees, 0 = left)."""
    b = p.computeTightBounds()
    cx, cy, r = b.centerX(), b.centerY(), max(b.width(), b.height()) / 2 + 1
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    p0, p1 = (cx - ca * r, cy - sa * r), (cx + ca * r, cy + sa * r)
    lit = tuple(int(min(255, base[i] * light[i] / 255 * 1.3)) for i in range(3))
    dark = mix(BLACK, base, amb)
    c.drawPath(p, paint(dark, a))
    sh = K.lin(p0, p1, [lit + (k,), lit + (k * 0.5,), dark + (0.0,)], [0.0, soft * 0.45, soft])
    c.drawPath(p, paint(shader=sh, a=a))


def fog(c, T, x0, y0, x1, y1, color, a=0.25, n=8, seed=0, speed=18.0, size=1.0):
    """Drifting soft banks of haze in a box: big blurred ellipses sliding sideways, wrapping round."""
    rng = K.rng_at(seed, 17)
    w = x1 - x0
    for i in range(n):
        bx = rng.uniform(0, w)
        by = rng.uniform(y0, y1)
        rx = rng.uniform(0.25, 0.5) * w * size
        ry = rng.uniform(0.04, 0.09) * w * size
        v = speed * rng.uniform(0.6, 1.4) * (1 if i % 2 else -1)
        x = x0 + ((bx + v * T) % (w + 2 * rx)) - rx
        aa = a * rng.uniform(0.5, 1.0) * (0.75 + 0.25 * math.sin(T * 0.4 + i))
        p = paint(color, aa, blur=ry * 0.9)
        p.setBlendMode(skia.BlendMode.kScreen)
        c.drawOval(skia.Rect.MakeLTRB(x - rx, by - ry, x + rx, by + ry), p)


def motes(c, T, x0, y0, x1, y1, color=(255, 230, 190), n=40, a=0.6, seed=0, size=2.2):
    """Dust drifting in a beam of light."""
    rng = K.rng_at(seed, 23)
    for i in range(n):
        bx, by = rng.uniform(x0, x1), rng.uniform(y0, y1)
        ph = rng.uniform(0, 6.28)
        x = bx + 18 * math.sin(T * 0.3 + ph) + 6 * math.sin(T * 1.1 + ph * 2)
        y = by + ((T * rng.uniform(4, 12)) % (y1 - y0)) - (y1 - y0) / 2
        y = y0 + (y - y0) % (y1 - y0)
        tw = 0.5 + 0.5 * math.sin(T * rng.uniform(1, 3) + ph)
        c.drawCircle(x, y, size * rng.uniform(0.6, 1.4), glow_paint(color, a * tw))


def flicker(T, seed=0, depth=0.12):
    """A candle's unsteady brightness, 1 - depth .. 1."""
    v = 0.5 * math.sin(T * 9.1 + seed) + 0.3 * math.sin(T * 17.3 + seed * 2.1) + 0.2 * math.sin(T * 31.7 + seed * 0.7)
    return 1 - depth * (0.5 + 0.5 * v)


def candle(c, x, y, s, T, a=1.0, seed=0, glow=1.0, color=(255, 170, 70)):
    """A candle: wax, a wick, an unsteady flame and its halo."""
    fl = flicker(T, seed)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    if glow > 0:
        pool(c, 0, -60, 260 * fl, color, 0.35 * a * glow * fl)
    c.drawRoundRect(skia.Rect.MakeLTRB(-16, -40, 16, 90), 6, 6, paint((236, 222, 190), a))
    c.drawRoundRect(skia.Rect.MakeLTRB(-16, -40, 16, 90), 6, 6,
                    paint(shader=K.lin((-16, 0), (16, 0), [(255, 236, 200, 0.0), (0, 0, 0, 0.5)]), a=a))
    c.drawPath(K.smooth([(-16, -40), (-6, -46), (6, -44), (16, -40), (10, -30), (-10, -32)]), paint((250, 240, 210), a * 0.8))
    sway = 2.5 * math.sin(T * 5.3 + seed)
    h = 46 * (0.9 + 0.12 * fl)
    flame = K.smooth([(sway * 1.6, -46 - h), (8, -62), (6, -50), (0, -46), (-6, -50), (-8, -62)])
    c.drawPath(flame, glow_paint((255, 190, 90), a))
    c.drawPath(K.smooth([(sway, -50 - h * 0.6), (4, -56), (0, -49), (-4, -56)]), glow_paint((255, 250, 230), a))
    c.drawLine(0, -44, 0, -52, paint((40, 30, 20), a, stroke=2))
    c.restore()


def lantern(c, x, y, s, color, T, a=1.0, seed=0, glow=1.0):
    """A wrought-iron street lantern with coloured glass, and the light it throws."""
    fl = flicker(T, seed, 0.06)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    if glow > 0:
        pool(c, 0, 20, 420, color, 0.42 * a * glow * fl)
        pool(c, 0, 20, 120, mix(color, WHITE, 0.4), 0.55 * a * glow * fl)
    c.drawLine(0, -120, 0, -40, paint((20, 16, 14), a, stroke=6))
    glass = K.path([(-34, -30), (34, -30), (24, 60), (-24, 60)])
    c.drawPath(glass, paint(mix(color, WHITE, 0.55), a))
    c.drawPath(glass, glow_paint(color, 0.6 * a * fl))
    for xx in (-17, 0, 17):
        c.drawLine(xx * 1.4, -30, xx, 60, paint((20, 16, 14), a, stroke=4))
    c.drawPath(K.path([(-48, -30), (48, -30), (0, -70)]), paint((20, 16, 14), a))
    c.drawRect(skia.Rect.MakeLTRB(-28, 60, 28, 72), paint((20, 16, 14), a))
    c.restore()

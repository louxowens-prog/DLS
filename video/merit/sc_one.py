"""Chapter I - THE INHERITANCE (cobalt deepening to violet).

i_dreamer - the sparks of the burning records stream up into a sleeping face as vast as the sky: she breathes them in.
i_cards   - six cards turn over in the smoke, one for each thing she inherits from us.
i_faces   - a face-reader's reticle on two faces; one dissolves into the other until their eyes overlap.
i_eyes    - her eye opens: a reel of tape turning in the iris.
i_mouth   - her mouth: "I do not hate."
i_merit   - all of her: the crown of reels, the sunburst of punched cards. "I only remember." """
import math

import numpy as np
import skia

import gel as G
import kit as K
import look as LK
import pface as PF
import people as P
import world as Wd
from common import E, S, Wx, hit, talk
from edit import cut, end
from kit import H, W, BLACK, WHITE, mix, paint, ramp


def s_i_dreamer(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("i_dreamer")
    Wd.forest(c, T, cam_y=120, moon_r=260, moon_xy=(860, 380), stars=0.6, seed=0, moon_a=0.6)
    # her face forms out of the night, eyes closed, breathing in
    k = K.ease(ramp(T, t0 - 1.0, t0 + 1.6))
    br = 0.5 + 0.5 * math.sin(T * 1.4)
    with K.layer(c, 0.62 * k, skia.BlendMode.kScreen):
        P.merit(c, 540, 700, 1.75 + 0.03 * (T - t0), T, eyes=0.0, rays=0.6, crown=0.7, mantle=0.6, hair=1.0, smile=0.15,
                L=(120, 150, 255), R=(170, 110, 255), amb=(10, 8, 26))
    Wd.fire(c, 540, 1760, 0.6, T, seed=1)
    # the stream of sparks curling up from the fire into her lips
    rng = K.rng_at(4, 4)
    mx, my = 540, 700 + 134 * 1.75 * 1.0
    for i in range(120):
        life = rng.uniform(1.6, 2.6)
        u = ((T + rng.uniform(0, life)) % life) / life
        sx, sy = 540 + rng.normal(0, 60), 1700
        cx_, cy_ = 540 + 300 * math.sin(i * 0.7) * (1 - u), 1300
        x = (1 - u) ** 2 * sx + 2 * (1 - u) * u * cx_ + u ** 2 * mx + rng.normal(0, 6)
        y = (1 - u) ** 2 * sy + 2 * (1 - u) * u * cy_ + u ** 2 * my
        a = math.sin(math.pi * u) * (0.6 + 0.4 * br)
        c.drawCircle(x, y, 3.2 * (1 - 0.5 * u), G.glow_paint(mix((255, 200, 120), (180, 200, 255), u), a))
    LK.flare(mx, my, 0.3 * k, (200, 210, 255))
    return st.arr


# ------------------------------------------------------------------ the cards

def _icon(c, n, T):
    """Painted emblems, centred at (0, 0), ~180 px."""
    gold, dk = (230, 196, 120), (20, 12, 24)
    if n == 0:                                                    # PREJUDICE: an eye already judging - half shut, narrowed
        c.drawPath(K.smooth([(-90, 0), (0, -50), (90, 0), (0, 50)]), paint(gold))
        c.drawCircle(0, 0, 34, paint(dk))
        c.drawCircle(0, 0, 14, paint((255, 60, 40)))
        c.drawPath(K.path([(-100, -10), (100, -10), (100, -70), (-100, -70)]), paint(dk))
        c.drawLine(-100, -10, 100, -10, paint(gold, stroke=6))
    elif n == 1:                                                  # HISTORICAL INEQUALITY: scales tipped for good
        c.drawLine(0, -90, 0, 80, paint(gold, stroke=8))
        c.drawLine(-90, -40, 90, -80, paint(gold, stroke=8))
        for x, y in ((-90, -40), (90, -80)):
            c.drawLine(x, y, x - 30, y + 60, paint(gold, stroke=3))
            c.drawLine(x, y, x + 30, y + 60, paint(gold, stroke=3))
            c.drawPath(K.smooth([(x - 40, y + 60), (x + 40, y + 60), (x + 26, y + 84), (x - 26, y + 84)]), paint(gold))
        c.drawCircle(-90, -10, 14, paint((255, 60, 40)))
        c.drawRect(skia.Rect.MakeLTRB(-40, 80, 40, 96), paint(gold))
    elif n == 2:                                                  # STEREOTYPES: one mask, cast again and again
        for k in range(3):
            x = -70 + k * 70
            c.drawPath(K.smooth([(x - 32, -60), (x + 32, -60), (x + 36, 10), (x, 60), (x - 36, 10)]), paint(gold, 0.6 + 0.2 * k))
            c.drawRect(skia.Rect.MakeLTRB(x - 22, -24, x - 6, -16), paint(dk))
            c.drawRect(skia.Rect.MakeLTRB(x + 6, -24, x + 22, -16), paint(dk))
    elif n == 3:                                                  # SAMPLING BIAS: a crowd with people missing
        for r in range(3):
            for q in range(4):
                x, y = -78 + q * 52, -60 + r * 60
                missing = (r * 4 + q) % 5 == 2 or (r, q) == (2, 0)
                if missing:
                    c.drawCircle(x, y - 12, 13, paint(gold, 0.7, stroke=2))
                    c.drawPath(K.smooth([(x - 20, y + 22), (x, y + 2), (x + 20, y + 22)]), paint(gold, 0.7, stroke=2))
                else:
                    c.drawCircle(x, y - 12, 13, paint(gold))
                    c.drawPath(K.smooth([(x - 20, y + 24), (x - 12, y + 4), (x + 12, y + 4), (x + 20, y + 24)]), paint(gold))
    elif n == 4:                                                  # CULTURAL ASSUMPTIONS: everyone measured against one figure
        c.drawLine(-80, 90, -80, -90, paint(gold, stroke=6))
        for k in range(7):
            c.drawLine(-80, 90 - k * 28, -60, 90 - k * 28, paint(gold, stroke=3))
        c.drawCircle(-20, -50, 18, paint(gold))
        c.drawPath(K.smooth([(-44, 90), (-36, -26), (-4, -26), (4, 90)]), paint(gold))
        for k, h in enumerate((0.6, 0.75, 0.5)):
            x = 30 + k * 30
            c.drawCircle(x, 90 - 150 * h, 11, paint(gold, 0.5))
            c.drawRect(skia.Rect.MakeLTRB(x - 10, 100 - 140 * h, x + 10, 90), paint(gold, 0.5))
    elif n == 5:                                                  # INSTITUTIONAL DISCRIMINATION: columns, and a door that stays shut
        c.drawPath(K.path([(-100, -50), (0, -100), (100, -50)]), paint(gold))
        for k in range(4):
            c.drawRect(skia.Rect.MakeLTRB(-90 + k * 56, -40, -70 + k * 56, 80), paint(gold))
        c.drawRect(skia.Rect.MakeLTRB(-110, 80, 110, 96), paint(gold))
        c.drawRect(skia.Rect.MakeLTRB(-22, 20, 22, 80), paint((255, 60, 40)))
        c.drawLine(-22, 20, 22, 80, paint(dk, stroke=4))
        c.drawLine(22, 20, -22, 80, paint(dk, stroke=4))


TITLES = [("PREJUDICE",), ("HISTORICAL", "INEQUALITY"), ("STEREOTYPES",), ("SAMPLING", "BIAS"), ("CULTURAL", "ASSUMPTIONS"),
          ("INSTITUTIONAL", "DISCRIMINATION")]


def tarot(c, x, y, w, h, n, T, flip=1.0, a=1.0, tint=(60, 90, 255)):
    """A card standing in the smoke: flip 0 = its patterned back, 1 = its face."""
    sx = abs(math.cos(math.pi * (1 - flip)))
    face = flip > 0.5
    c.save()
    c.translate(x, y)
    c.scale(max(0.02, sx), 1)
    r = skia.Rect.MakeLTRB(-w / 2, -h / 2, w / 2, h / 2)
    c.drawRoundRect(r, 18, 18, paint((14, 10, 22), a))
    c.drawRoundRect(r, 18, 18, paint((230, 196, 120), a, stroke=5))
    c.drawRoundRect(skia.Rect.MakeLTRB(-w / 2 + 14, -h / 2 + 14, w / 2 - 14, h / 2 - 14), 12, 12, paint((230, 196, 120), 0.6 * a, stroke=2))
    if face:
        c.drawRoundRect(skia.Rect.MakeLTRB(-w / 2 + 22, -h / 2 + 22, w / 2 - 22, h / 2 - 22), 10, 10,
                        paint(shader=K.lin((0, -h / 2), (0, h / 2), [mix(tint, BLACK, 0.4), mix(tint, BLACK, 0.85)]), a=a))
        G.pool(c, 0, -h * 0.12, w * 0.6, mix(tint, WHITE, 0.3), 0.5 * a)
        c.save()
        c.translate(0, -h * 0.12)
        c.scale(w / 330, w / 330)
        with K.layer(c, a):
            _icon(c, n, T)
        c.restore()
        lines = TITLES[n]
        size = 30
        f = K.font("cinzel-800", size)
        while max(f.measureText(s) for s in lines) > w - 50 and size > 18:
            size -= 1
            f = K.font("cinzel-800", size)
        for i, s in enumerate(lines):
            yy = h * 0.3 + (i - (len(lines) - 1) / 2) * size * 1.15
            K.text(c, s, 0, yy, size, "cinzel-800", (250, 232, 190), tag="card", a=a, outline=(10, 6, 12), ow=5)
    else:
        for k in range(8):                                        # the back: a punched-card pattern round an eye
            for q in range(4):
                c.drawRect(skia.Rect.MakeXYWH(-w / 2 + 40 + q * (w - 80) / 4, -h / 2 + 40 + k * (h - 80) / 8, 14, 22), paint((230, 196, 120), 0.4 * a))
        c.drawPath(K.smooth([(-60, 0), (0, -36), (60, 0), (0, 36)]), paint((230, 196, 120), a, stroke=4))
        c.drawCircle(0, 0, 14, paint((255, 60, 40), a))
    c.restore()


def s_i_cards(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("i_cards")
    Wd.sky(c, (2, 2, 14), (10, 12, 40), (24, 20, 60))
    Wd.card_stars(c, T, 40, 60, W - 40, 900, a=0.5, seed=3)
    G.fog(c, T, -100, 200, 1180, 1500, (90, 110, 255), a=0.3, n=10, seed=7)
    times = [Wx("i1", "prejudice,"), Wx("i1", "inequality,"), Wx("i1", "stereotypes,"), Wx("i1", "people"), Wx("i1", "never"), Wx("i1", "counted.")]
    w, h = 280, 450
    pos = [(175, 545), (495, 545), (815, 545), (175, 1045), (495, 1045), (815, 1045)]
    for n, ((x, y), tf) in enumerate(zip(pos, times)):
        fl = K.ease(ramp(T, tf - 0.35, tf + 0.1))
        bob = 10 * math.sin(T * 0.9 + n)
        a = K.ease(ramp(T, t0 + n * 0.08, t0 + 0.5 + n * 0.08))
        glow = hit(T, tf + 0.05, 0.6)
        if glow > 0:
            G.pool(c, x, y + bob, 300, (120, 160, 255), 0.5 * glow)
        tarot(c, x, y + bob, w, h, n, T, flip=fl, a=a)
    return st.arr



# ------------------------------------------------------------------ Gender Shades

def _reticle(c, x, y, w, h, col, a=1.0, T=0.0):
    L = 60
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        cx, cy = x + sx * w / 2, y + sy * h / 2
        c.drawLine(cx, cy, cx - sx * L, cy, G.glow_paint(col, a))
        c.drawLine(cx, cy, cx, cy - sy * L, G.glow_paint(col, a))
        c.drawLine(cx, cy, cx - sx * L, cy, paint(col, a, stroke=5))
        c.drawLine(cx, cy, cx, cy - sy * L, paint(col, a, stroke=5))
    sy = y - h / 2 + h * ((T * 0.7) % 1.0)                         # the scan line
    c.drawLine(x - w / 2, sy, x + w / 2, sy, paint(col, 0.5 * a, stroke=3))
    for i in range(14):                                            # landmarks
        ang = i / 14 * 6.283
        px, py = x + math.cos(ang) * w * 0.28, y + math.sin(ang) * h * 0.3
        c.drawCircle(px, py, 5, paint(col, 0.8 * a))


def s_i_faces(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("i_faces")
    t_men = Wx("i2", "Lighter-skinned") - 0.5
    k = K.ease(ramp(T, t_men, t_men + 1.8))                        # the long dissolve: her face into his
    z = 1.0 + 0.025 * (T - t0)
    c.save()
    c.translate(540, 860)
    c.scale(z, z)
    c.translate(-540, -860)
    G.pool(c, 540, 820, 800, (200, 60, 200), 0.35)
    fy = 860
    if k < 1:
        PF.pface(c, 540, fy, 1.45, "w_dark", T, key=(255, 236, 226), fill=(170, 150, 230), rim=(255, 140, 220), amb=(30, 22, 34), fall=0.0,
                 blink=0.0, a=1.0 - 0.55 * k)
    if k > 0:
        with K.layer(c, k, skia.BlendMode.kScreen if k < 0.95 else None):
            PF.pface(c, 540, fy, 1.45, "m_light", T, key=(255, 236, 226), fill=(170, 150, 230), rim=(255, 140, 220), amb=(30, 22, 34), fall=0.0)
    c.restore()
    # the machine's view: a reticle, and the error rate it made
    err = K.ease(ramp(T, Wx("i2", "wrong") - 0.2, Wx("i2", "wrong") + 0.3))
    col = mix((255, 50, 50), (80, 255, 140), k)
    fl = 0.7 + 0.3 * math.sin(T * 30) if k < 0.5 else 1.0
    _reticle(c, 540, 840, 560, 700, col, a=0.85 * fl * min(1.0, (T - t0) * 3), T=T)
    K.text(c, "FACE-READING AI  ·  GENDER SHADES, MIT, 2018", 540, 300, 30, "jost-500", (230, 220, 255), tag="label", a=0.85)
    if k < 0.5:
        a = err * (1 - k * 2)
        K.text(c, "34.7%", 540, 430, 120, "newrocker-400", (255, 80, 70), tag="label", a=a, outline=(20, 0, 6), ow=10)
        K.text(c, "ERROR RATE · DARKER-SKINNED WOMEN", 540, 492, 34, "jost-600", (255, 210, 210), tag="label", a=a, outline=(20, 0, 6), ow=6)
    else:
        a = (k - 0.5) * 2
        K.text(c, "0.8%", 540, 430, 120, "newrocker-400", (110, 255, 160), tag="label", a=a, outline=(0, 20, 6), ow=10)
        K.text(c, "ERROR RATE · LIGHTER-SKINNED MEN", 540, 492, 34, "jost-600", (210, 255, 220), tag="label", a=a, outline=(0, 20, 6), ow=6)
    return st.arr


# ------------------------------------------------------------------ Merit wakes

def s_i_eyes(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t_open = S("i3") - 0.15
    bl = 1 - K.ease(ramp(T, t_open, t_open + 0.6))
    z = 1.0 + 0.04 * (T - cut("i_eyes"))
    PF.eye_macro(c, 540, 820, 1.08 * z, "merit", T, blink=bl, gaze=(0.0, 0.05), key=(255, 110, 60), fill=(150, 80, 255), wide=0.1)
    return st.arr


def s_i_mouth(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    z = 1.0 + 0.05 * (T - cut("i_mouth"))
    PF.mouth_macro(c, 540, 900, 1.0 * z, "merit", T, talk=talk(T, "merit"), smile=0.25, key=(255, 110, 60), fill=(150, 80, 255))
    return st.arr


def s_i_merit(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("i_merit")
    Wd.sky(c, (4, 2, 16), (18, 8, 40), (34, 12, 50))
    Wd.card_stars(c, T, 40, 60, W - 40, 1200, a=0.5, seed=5)
    z = 1.25 - 0.12 * K.ease(ramp(T, t0, t0 + 1.6))
    P.merit(c, 540, 900, 1.45 * z, T, eyes=1.0, talk=talk(T, "merit"), smile=0.3, rays=1.0, crown=1.0, mantle=1.0)
    LK.flare(540, 900 - 150 * 1.45 * z, 0.55, (255, 120, 100))
    return st.arr

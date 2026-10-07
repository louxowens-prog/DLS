"""Chapter II - THE PATTERN (blood red).

p_portraits - a wall of portraits of the leaders of years gone by, almost all of them men, rising into the dark.
p_template  - the portraits slide together into one face: the pattern it learns.
p_cv        - a CV fed to the machine; one word on it glows and is marked down: "women's".
p_scrap     - the machine is scrapped: its reels stop, its lamps die, the CV goes into the fire.
p_calm      - her face, serene; old photographs of boardrooms drift through it.
p_door      - a woman before a lit doorway; the door closes.
p_proxy     - the word is painted out; the machine finds stand-ins: a postcode, a hobby, a gap."""
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

GILT = (200, 160, 80)


def _frame(c, x, y, w, h, a=1.0):
    c.drawRect(skia.Rect.MakeLTRB(x - w / 2 - 26, y - h / 2 - 26, x + w / 2 + 26, y + h / 2 + 26), paint(mix(GILT, BLACK, 0.4), a))
    c.drawRect(skia.Rect.MakeLTRB(x - w / 2 - 26, y - h / 2 - 26, x + w / 2 + 26, y + h / 2 + 26), paint(GILT, a, stroke=10))
    c.drawRect(skia.Rect.MakeLTRB(x - w / 2 - 8, y - h / 2 - 8, x + w / 2 + 8, y + h / 2 + 8), paint(mix(GILT, WHITE, 0.3), a, stroke=4))


def _sitter(c, x, y, s, who, T, man=True, a=1.0, seed=0):
    """A painted portrait of a leader of the past: a dark suit, a tie, a face lit from one side."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawPaint(paint((40, 24, 20), a))
    G.pool(c, -80, -120, 300, (200, 140, 90), 0.3 * a)
    suit = (24, 20, 26)
    c.drawPath(K.smooth([(-260, 420), (-240, 240), (-150, 170), (-60, 160), (60, 160), (150, 170), (240, 240), (260, 420)]), paint(suit, a))
    if man:
        c.drawPath(K.path([(-50, 160), (50, 160), (20, 300), (-20, 300)]), paint((210, 206, 200), a))
        c.drawPath(K.path([(-14, 170), (14, 170), (22, 290), (0, 320), (-22, 290)]), paint((120, 20, 30) if seed % 2 else (30, 40, 90), a))
    else:
        c.drawPath(K.smooth([(-70, 160), (0, 230), (70, 160)]), paint((200, 190, 180), a))
    PF.pface(c, 0, -60, 0.62, who, T, key=(255, 200, 150), fill=(120, 90, 140), key_at=(-0.8, -0.3), amb=(26, 16, 20), neck=True, a=a)
    c.restore()


WALL = [("m_light", True, 1974), ("m_b", True, 1979), ("m_light", True, 1983), ("m_b", True, 1988), ("m_light", True, 1991),
        ("f_b", False, 1996), ("m_b", True, 2001), ("m_light", True, 2005), ("m_b", True, 2009), ("m_light", True, 2013)]


def s_p_portraits(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("p_portraits")
    rise = 900 * K.ease(ramp(T, t0, end("p_portraits") + 1.0))
    c.drawPaint(paint((26, 8, 8)))
    for i in range(40):                                            # damask wallpaper
        c.drawCircle((i * 137) % W, (i * 263) % 3000 - rise, 60, paint((40, 12, 12), 0.6))
    c.save()
    c.translate(0, rise)
    for k, (who, man, year) in enumerate(WALL):
        col = k % 2
        row = k // 2
        x = 290 + col * 500
        y = 1340 - row * 560
        _frame(c, x, y, 380, 470)
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(x - 190, y - 235, x + 190, y + 235))
        _sitter(c, x, y + 30, 0.95, who, T, man=man, seed=k)
        c.restore()
        c.drawRect(skia.Rect.MakeLTRB(x - 80, y + 268, x + 80, y + 316), paint(mix(GILT, BLACK, 0.2)))
        K.text(c, str(year), x, y + 304, 38, "cinzel-800", (40, 20, 10), tag="plaque")
    c.restore()
    G.pool(c, 540, 300, 900, (255, 60, 40), 0.25)
    Wd.smoke(c, T, 540, 1800, w=600, h=1800, color=(140, 50, 50), a=0.3, seed=6)
    return st.arr


def s_p_template(T, idx):
    """The faces slide together into one: the learned picture of a leader."""
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("p_template")
    k = K.ease(ramp(T, t0, t0 + 1.4))
    c.drawPaint(paint((20, 6, 6)))
    G.pool(c, 540, 800, 900, (255, 70, 50), 0.35)
    for i, (who, man, year) in enumerate(WALL):
        ang = i / len(WALL) * 6.283
        r = 520 * (1 - k)
        x, y = 540 + math.cos(ang) * r, 820 + math.sin(ang) * r * 1.2
        with K.layer(c, (0.5 if man else 0.25) * (1 - 0.6 * k), skia.BlendMode.kScreen):
            PF.pface(c, x, y, 1.2, who, T, key=(255, 200, 160), fill=(140, 80, 100), amb=(20, 10, 10), neck=False)
    with K.layer(c, k):
        PF.pface(c, 540, 820, 1.2, "m_light", T, key=(255, 210, 170), fill=(160, 90, 110), amb=(24, 10, 12), neck=True, rim=(255, 120, 90))
    K.text(c, "THE PATTERN IT LEARNED:", 540, 320, 40, "special-elite-400", (255, 220, 200), tag="label", a=k, outline=(20, 0, 0), ow=6)
    K.text(c, "LEADER  =  MAN", 540, 400, 72, "newrocker-400", (255, 236, 220), tag="label", a=K.ease(ramp(T, Wx("p1", "men", 1) - 0.1, Wx("p1", "men", 1) + 0.3)),
           outline=(30, 0, 0), ow=10)
    return st.arr


CV_LINES = ["CURRICULUM VITAE", "", "Software engineer, 6 years", "B.Sc. Computer Science", "Led a team of nine",
            "Captain, Women's Chess Club", "Python, C++, Go", "", "Postcode: N17 4RT", "Hobbies: netball", "2016 - 2018:  —", ""]


def cv_page(c, x, y, s, T, ang=0.0, hl=None, erase=0.0, a=1.0, name="J. MORGAN"):
    """The CV, big enough to read. hl: {line index: (k, colour)} rings drawn round lines; erase (0..1) paints out "Women's"."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    w, h = 900, 1180
    c.drawRect(skia.Rect.MakeLTRB(-w / 2 + 14, -h / 2 + 18, w / 2 + 14, h / 2 + 18), paint((0, 0, 0), 0.5 * a, blur=16))
    c.drawRect(skia.Rect.MakeLTRB(-w / 2, -h / 2, w / 2, h / 2), paint((214, 202, 176), a))
    c.drawRect(skia.Rect.MakeLTRB(-w / 2, -h / 2, w / 2, h / 2), paint(shader=K.lin((-w / 2, -h / 2), (w / 2, h / 2), [(255, 255, 255, 0.0), (100, 60, 30, 0.3)]), a=a))
    f = K.font("special-elite-400", 50)
    fb = K.font("special-elite-400", 64)
    y0 = -h / 2 + 120
    c.drawString(name, -w / 2 + 70, y0 - 10, fb, paint((40, 26, 26), a))
    for i, ln in enumerate(CV_LINES[1:]):
        yy = y0 + 70 + i * 82
        if not ln:
            continue
        c.drawString(ln, -w / 2 + 70, yy, f, paint((40, 26, 26), a))
        if ln.startswith("Captain") and erase > 0:
            x0 = -w / 2 + 70 + f.measureText("Captain, ")
            ww = f.measureText("Women's")
            c.drawRoundRect(skia.Rect.MakeLTRB(x0 - 8, yy - 42, x0 - 8 + (ww + 16) * erase, yy + 14), 10, 10, paint((240, 236, 226), a))
        if hl and (i + 1) in hl:
            k, col = hl[i + 1]
            if k > 0:
                if ln.startswith("Captain"):
                    x0 = -w / 2 + 70 + f.measureText("Captain, ")
                    ww = f.measureText("Women's")
                else:
                    x0 = -w / 2 + 70
                    ww = f.measureText(ln)
                r = skia.Rect.MakeLTRB(x0 - 20, yy - 54, x0 + ww + 20, yy + 22)
                c.drawRoundRect(r, 30, 30, G.glow_paint(col, 0.35 * k * a, blur=10))
                c.drawRoundRect(r, 30, 30, paint(col, k * a, stroke=7))
                K.text(c, "−", x0 + ww + 60, yy + 4, 80, "jost-600", col, tag="deco", a=k * a, outline=(20, 0, 0), ow=6)
    K.reg_local(c, -w / 2 + 60, -h / 2 + 40, w / 2 - 40, h / 2 - 40, "card")
    c.restore()


def _machine(c, x, y, s, T, on=1.0):
    """The reading machine: a cabinet of brass and glass, tape reels turning, valve lamps glowing."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawRoundRect(skia.Rect.MakeLTRB(-420, -300, 420, 300), 24, 24, paint((40, 28, 22)))
    c.drawRoundRect(skia.Rect.MakeLTRB(-420, -300, 420, 300), 24, 24, paint(GILT, stroke=8))
    for k, rx in enumerate((-220, 220)):
        P._reel(c, rx, -90, 130, T * on, spin=1 if k else -1)
    c.drawPath(K.bez_path([(-220, 40), (0, 120), (220, 40)]), paint((60, 30, 26), stroke=10))
    for i in range(7):
        lx = -270 + i * 90
        lit = on * (0.6 + 0.4 * math.sin(T * 5 + i * 1.7))
        c.drawRoundRect(skia.Rect.MakeLTRB(lx - 22, 150, lx + 22, 240), 18, 18, paint((60, 40, 30)))
        c.drawRoundRect(skia.Rect.MakeLTRB(lx - 16, 156, lx + 16, 234), 14, 14, G.glow_paint((255, 120, 50), lit))
    c.restore()


def s_p_cv(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("p_cv")
    c.drawPaint(paint((24, 10, 8)))
    G.pool(c, 540, 1100, 1000, (255, 70, 40), 0.3)
    _machine(c, 540, 250, 0.62, T)
    LK.flare(540 - 220 * 0.62, 250 - 90 * 0.62, 0.25, (255, 150, 90))
    # the CV slides up out of the dark into the reader's light
    u = K.ease(ramp(T, t0, t0 + 1.2))
    k_w = K.ease(ramp(T, Wx("p2", "women's") - 0.1, Wx("p2", "women's") + 0.25))
    cv_page(c, 540, 880 + 300 * (1 - u), 0.74, T, ang=-2, hl={5: (k_w, (255, 50, 40))})
    # the score it gives, falling
    sc = 78 - 37 * k_w
    a_ = K.ease(ramp(T, t0 + 0.8, t0 + 1.3))
    c.drawRoundRect(skia.Rect.MakeLTRB(640, 330, 940, 420), 12, 12, paint((10, 4, 4), 0.85 * a_))
    K.text(c, f"SCORE {sc:.0f}" + (" ▼" if k_w > 0.5 else ""), 790, 395, 50, "special-elite-400", (255, 90, 70) if k_w > 0.5 else (255, 220, 190),
           tag="label", a=a_)
    return st.arr


def s_p_scrap(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("p_scrap")
    u = (T - t0) / max(0.1, end("p_scrap") - t0)
    c.drawPaint(paint((16, 6, 6)))
    on = max(0.0, 1 - u * 2.5)
    _machine(c, 540, 520, 1.0, T if on > 0 else t0 + 0.4, on=on)
    if u > 0.35:                                                    # sparks as it dies
        rng = K.rng_at(5, 1)
        for i in range(40):
            ang = rng.uniform(-2.8, -0.3)
            r = (u - 0.35) * 900 * rng.uniform(0.4, 1.0)
            c.drawCircle(540 + math.cos(ang) * r, 520 + math.sin(ang) * r + 300 * (u - 0.35) ** 2 * 4, 4, G.glow_paint((255, 200, 120), max(0.0, 1 - u)))
    Wd.fire(c, 540, 1700, 0.9, T, seed=2)
    c.save()                                                        # the CV, crumpling, dropping into the fire
    c.translate(540, 1000 + 500 * u ** 2)
    c.rotate(30 * u)
    c.scale(0.55 * (1 - 0.5 * u), 0.55 * (1 - 0.8 * u))
    cv_page(c, 0, 0, 1.0, T)
    c.restore()
    return st.arr


def _boardroom(c, x, y, s, T, a=1.0, seed=0):
    """An old photograph of a board: rows of men in dark suits, sepia, a white border."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawRect(skia.Rect.MakeLTRB(-330, -230, 330, 230), paint((236, 226, 206), a))
    c.drawRect(skia.Rect.MakeLTRB(-300, -200, 300, 200), paint((120, 96, 70), a))
    rng = K.rng_at(seed, 99)
    for row in range(2):
        for q in range(6):
            px = -250 + q * 100 + (50 if row else 0)
            py = -40 + row * 110
            c.drawCircle(px, py - 50, 26, paint((200, 170, 130), a))
            c.drawPath(K.smooth([(px - 46, py + 70), (px - 40, py - 14), (px + 40, py - 14), (px + 46, py + 70)]), paint((40, 30, 24), a))
            c.drawRect(skia.Rect.MakeLTRB(px - 5, py - 16, px + 5, py + 26), paint((220, 210, 190), a))
    c.drawRect(skia.Rect.MakeLTRB(-300, -200, 300, 200), paint(shader=K.rad((0, 0), 380, [(0, 0, 0, 0.0), (40, 20, 10, 0.6)]), a=a))
    c.restore()


def s_p_calm(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("p_calm")
    c.drawPaint(paint((14, 4, 6)))
    z = 1.0 + 0.04 * (T - t0)
    P.merit(c, 540, 860, 1.6 * z, T, eyes=0.55, talk=0.0, smile=0.3, rays=0.8, crown=1.0, mantle=1.0,
            L=(255, 90, 60), R=(200, 60, 120), amb=(16, 6, 10))
    # history drifting through her face
    k = K.ease(ramp(T, Wx("p3", "It") - 0.3, Wx("p3", "It") + 0.6))
    for i in range(4):
        x = 540 + (i - 1.5) * 300 + 120 * (T - t0) * (1 if i % 2 else -1)
        y = 700 + i * 200
        with K.layer(c, 0.5 * k, skia.BlendMode.kScreen):
            _boardroom(c, x, y, 0.85, T, seed=i)
    if k > 0:
        K.text(c, "1960 · 1975 · 1990 · 2010", 540, 330, 40, "special-elite-400", (255, 220, 200), tag="label", a=0.8 * k, outline=(20, 0, 0), ow=6)
    return st.arr


def s_p_door(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("p_door")
    t_shut = Wx("p3", "discrimination.") + 0.2
    shut = K.ease(ramp(T, t0 + 0.2, t_shut))
    c.drawPaint(paint((10, 2, 4)))
    # a tall doorway of light, narrowing as the door swings shut
    dw = 360 * (1 - shut)
    if dw > 1:
        c.drawRect(skia.Rect.MakeLTRB(540 - 180, 300, 540 - 180 + dw, 1400), paint((255, 230, 210)))
        G.beam(c, (540 - 180 + dw / 2, 900), (240, 1900), (840 + dw, 1900), (255, 200, 170), a=0.35 * (1 - shut))
        LK.flare(540 - 180 + dw / 2, 700, 0.5 * (1 - shut), (255, 220, 200))
    c.drawRect(skia.Rect.MakeLTRB(540 - 200, 280, 540 + 200, 1400), paint((60, 20, 16), stroke=24))
    c.drawRect(skia.Rect.MakeLTRB(540 - 180 + dw, 300, 540 + 180, 1400), paint((30, 10, 8)))      # the door
    # her, from behind, in the light
    c.save()
    c.translate(540, 1560)
    c.scale(1.05, 1.05)
    c.drawPath(K.smooth([(-110, 0), (-120, -380), (-90, -620), (-40, -680), (40, -680), (90, -620), (120, -380), (110, 0)]), paint((8, 2, 4)))
    c.drawCircle(0, -760, 78, paint((8, 2, 4)))
    c.drawPath(K.smooth([(-80, -790), (0, -860), (80, -790), (100, -620), (60, -560), (-60, -560), (-100, -620)]), paint((8, 2, 4)))
    c.restore()
    if T >= t_shut:
        c.drawPaint(G.glow_paint((255, 40, 30), 0.5 * hit(T, t_shut, 0.3)))
    return st.arr


def s_p_proxy(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("p_proxy")
    c.drawPaint(paint((22, 8, 8)))
    G.pool(c, 540, 1000, 1100, (255, 70, 40), 0.3)
    er = K.ease(ramp(T, Wx("p4", "Delete") - 0.1, Wx("p4", "word,")))
    kpc = K.ease(ramp(T, Wx("p4", "postcode,") - 0.1, Wx("p4", "postcode,") + 0.25))
    kh = K.ease(ramp(T, Wx("p4", "hobby,") - 0.1, Wx("p4", "hobby,") + 0.25))
    kg = K.ease(ramp(T, Wx("p4", "gap") - 0.1, Wx("p4", "gap") + 0.25))
    z = 1.0 + 0.03 * (T - t0)
    c.save()
    c.translate(540, 900)
    c.scale(z, z)
    c.translate(-540, -900)
    cv_page(c, 540, 860, 0.74, T, ang=1.5, erase=er, hl={8: (kpc, (255, 60, 40)), 9: (kh, (255, 60, 40)), 10: (kg, (255, 60, 40))})
    c.restore()
    # her threads reaching down to the stand-ins
    for k, (yy, kk) in enumerate(((1040, kpc), (1100, kh), (1162, kg))):
        if kk > 0:
            c.drawPath(K.bez_path([(540 + (k - 1) * 200, 0), (300 + k * 120, 600), (330, yy)]), G.glow_paint((255, 80, 60), 0.5 * kk, blur=3))
    K.text(c, "STAND-INS", 540, 330, 64, "newrocker-400", (255, 220, 200), tag="label", a=max(kpc, kh, kg), outline=(30, 0, 0), ow=8)
    return st.arr

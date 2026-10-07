"""The hook, the cold open, the title and the chapter cards.

h_stamp  - red dark, smoke: a Clerk's stamp comes down in slow motion on someone's file. INELIGIBLE.
o_sky    - silence and wind: a sky whose stars stand in rows like the holes of a punched card; a moon far too big.
o_fire   - a fire in a clearing, fed with records: HIRED, REFUSED. The sparks rise and become the stars.
t_title  - INELIGIBLE, in chrome.
k_1..k_4 - the chapter cards."""
import math

import numpy as np
import skia

import cards as CD
import gel as G
import kit as K
import look as LK
import pface as PF
import people as P
import world as Wd
from common import E, S, Wx, hit, shake, talk
from edit import cut, end
from kit import H, W, BLACK, WHITE, mix, paint, ramp


def _file(c, x, y, s, ang, T, stamped=0.0, who="f_a", name="APPLICANT 4471-B", seed=0, burn=0.0):
    """Someone's file: a photo clipped to a typed form; stamped (0..1) shows the red mark."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    Wd.page(c, 0, 0, 760, 1000, 0, T, burn=burn, lines=14, seed=seed, title=name, title_size=46, color=(232, 222, 198))
    # the photograph
    c.save()
    c.translate(-170, -230)
    c.drawRect(skia.Rect.MakeLTRB(-130, -160, 130, 160), paint((30, 26, 30)))
    c.clipRect(skia.Rect.MakeLTRB(-122, -152, 122, 152))
    c.drawPaint(paint((60, 50, 56)))
    PF.pface(c, 0, -10, 0.55, who, T, key=(255, 200, 170), fill=(160, 140, 200), amb=(60, 50, 60), neck=True)
    c.restore()
    c.drawRect(skia.Rect.MakeLTRB(-302, -392, -38, -68), paint((200, 190, 170), stroke=3))
    c.drawPath(K.path([(-60, -410), (-30, -410), (-30, -360), (-60, -360)]), paint((150, 150, 160)))          # the clip
    f = K.font("special-elite-400", 34)
    for i, ln in enumerate(("DATE OF BIRTH", "POSTCODE", "EMPLOYMENT HISTORY", "REFERENCES")):
        c.drawString(ln, 20, -330 + i * 70, f, paint((60, 40, 40)))
        c.drawRect(skia.Rect.MakeXYWH(20, -318 + i * 70, 300, 3), paint((60, 40, 40), 0.5))
    c.restore()
    if stamped > 0:
        P.stamp_mark(c, x + 10 * s, y + 200 * s, 0.86 * s, ang=ang - 9, a=min(1.0, stamped * 3), tag="deco")


def s_h_stamp(T, idx):
    st = K.Stage((6, 0, 2))
    c = st.c
    t_hit = 0.55
    sh = 26 * hit(T, t_hit, 0.5)
    shake(c, T, sh)
    z = 1.0 + 0.05 * T
    c.translate(540, 1000)
    c.scale(z, z)
    c.rotate(-4 + 1.2 * T)
    c.translate(-540, -1000)
    # the desk: dark wood, one hard pool of red light from a lamp overhead
    c.drawRect(skia.Rect.MakeLTRB(-400, -400, 1500, 2400), paint((16, 8, 8)))
    for i in range(30):
        c.drawLine(-400, -400 + i * 100, 1500, -300 + i * 100, paint((34, 16, 14), 0.5, stroke=3))
    G.pool(c, 560, 1060, 760, (255, 60, 30), 0.38)
    burn = max(0.0, (T - 2.9) / 1.2)
    _file(c, 560, 1000, 0.82, 3, T, stamped=1.0 if T >= t_hit else 0.0, who="f_a", burn=0.0)
    # the stamp descending in slow motion; after the hit it lifts away
    if T < t_hit:
        u = T / t_hit
        y = -500 + (1060 - -500) * u ** 2.2
        s = 2.2 - 1.0 * u
    else:
        u = min(1.0, (T - t_hit) / 0.9)
        y = 1060 - 1400 * K.ease(u)
        s = 1.2 + 0.6 * u
    if y > -600:
        c.save()
        c.translate(560, y)
        c.scale(s, s)
        # seen from above: the dark block, its bevel catching the lamp, the round handle, the press's rod
        c.drawRoundRect(skia.Rect.MakeLTRB(-330, -230, 330, 230), 26, 26, paint((40, 22, 16)))
        c.drawRoundRect(skia.Rect.MakeLTRB(-330, -230, 330, 230), 26, 26, paint((150, 80, 60), 0.6, stroke=10))
        c.drawRoundRect(skia.Rect.MakeLTRB(-290, -190, 290, 190), 18, 18, paint(shader=K.lin((0, -190), (0, 190), [(120, 60, 40), (30, 14, 10)])))
        c.drawCircle(0, 0, 120, paint((26, 12, 10)))
        c.drawCircle(0, 0, 120, paint(shader=K.rad((-40, -40), 140, [(170, 90, 70), (40, 18, 12)])))
        c.drawCircle(-40, -40, 30, G.glow_paint((255, 150, 120), 0.4, blur=14))
        c.drawRect(skia.Rect.MakeLTRB(-34, -1200, 34, -100), paint((40, 38, 46)))
        c.drawRect(skia.Rect.MakeLTRB(-34, -1200, -14, -100), paint((110, 100, 110), 0.6))
        c.restore()
    # the impact: ink spray and a white flash
    if T >= t_hit:
        k = hit(T, t_hit, 0.35)
        rng = K.rng_at(3, 5)
        for i in range(40):
            ang = rng.uniform(0, 6.283)
            r = (60 + 600 * (T - t_hit)) * rng.uniform(0.6, 1.4)
            c.drawCircle(560 + math.cos(ang) * r * 1.4, 1240 + math.sin(ang) * r * 0.5, rng.uniform(3, 12) * max(0.2, 1 - (T - t_hit)),
                         paint((150, 0, 10), 0.8 * max(0.0, 1 - (T - t_hit) * 0.8)))
        c.drawPaint(G.glow_paint((255, 200, 180), 0.55 * k))
    # the Clerk looking down, out of focus at the top of the frame, after the stamp has lifted
    k2 = K.ease(ramp(T, 1.2, 2.2))
    if k2 > 0:
        c.save()
        c.resetMatrix()
        with K.layer(c, 0.8 * k2):
            P.clerk(c, 540, 520, 1.25, T, arm=0.0, stamp=False, slit=1.0, rim_k=1.2, seed=1, metal=(60, 56, 66))
        c.restore()
        LK.flare(540 + 0, 520 - 120 * 1.25 - 164 * 1.25, 0.6 * k2, (255, 120, 100))
    Wd.smoke(c, T, 540, 1500, w=500, h=1500, color=(160, 60, 60), a=0.35, seed=2)
    c.restore()
    return st.arr


def s_o_sky(T, idx):
    """The night before the nightmare: the camera tilts down from the card-hole stars past the moon to the pines."""
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("o_sky")
    u = K.ease(ramp(T, t0, t0 + 3.4))
    cam = -620 + 620 * u
    Wd.forest(c, T, cam_y=-cam, moon_r=340, moon_xy=(620, 600), stars=1.0, seed=0)
    LK.flare(620, 600 + cam * 0.4 + cam, 0.25, (220, 210, 255))
    Wd.embers(c, T, 540, 2000 - cam, spread=200, height=1500, n=30, a=0.6, to_stars=1.0, seed=4)
    return st.arr


def s_o_fire(T, idx):
    """The fire of records."""
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("o_fire")
    z = 1.0 + 0.06 * (T - t0)
    c.save()
    c.translate(540, 1200)
    c.scale(z, z)
    c.translate(-540, -1200)
    Wd.forest(c, T, cam_y=0, moon_r=300, moon_xy=(700, 420), stars=0.8, seed=0)
    G.fog(c, T, -100, 1200, 1180, 1700, (120, 70, 160), a=0.35, n=8, seed=5)
    Wd.fire(c, 540, 1500, 0.95, T, seed=1)
    Wd.embers(c, T, 540, 1420, spread=220, height=1500, n=90, a=0.95, to_stars=0.8, seed=2, size=3.4)
    Wd.smoke(c, T, 540, 1250, w=360, h=1300, color=(120, 80, 140), a=0.3, seed=3)
    # two records drift down into the flames, each catching as the narrator names it
    for k, (word, stamp, col, x, ang) in enumerate((("hired,", "HIRED", (30, 30, 40), 400, -12), ("refused,", "REFUSED", (180, 10, 20), 680, 10))):
        ts = Wx("c1", word) - 0.9
        if T < ts:
            continue
        v = T - ts
        y = 560 + 300 * v - 40 * math.sin(v * 2)
        burn = max(0.0, (v - 1.1) / 1.4)
        if burn >= 1.0:
            continue
        a = 1.0 if burn < 0.8 else (1 - burn) / 0.2
        c.save()
        c.translate(x, y)
        c.rotate(ang + 12 * math.sin(v * 1.3))
        Wd.page(c, 0, 0, 330, 430, 0, T, burn=burn, lines=8, seed=10 + k, a=a)
        if burn < 0.55:
            P.stamp_mark(c, 0, 40, 0.42, ang=-10 if k else 8, text=stamp, color=col, a=a, tag="deco")
        c.restore()
        G.pool(c, x, y, 200, (255, 120, 40), 0.4 * burn * a)
    c.restore()
    return st.arr


def s_t_title(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("t_title")
    CD.title_card(c, T, t0, dur=end("t_title") - t0)
    LK.flare(300, 820, 0.7 * max(0.0, 1 - (T - t0) * 0.8), (255, 200, 160))
    return st.arr


def _card(n):
    def f(T, idx):
        st = K.Stage((0, 0, 0))
        name = f"k_{n}"
        CD.chapter_card(st.c, n, T, cut(name), dur=end(name) - cut(name))
        return st.arr
    return f


s_k_1, s_k_2, s_k_3, s_k_4 = _card(1), _card(2), _card(3), _card(4)

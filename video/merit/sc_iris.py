"""The descent, and the real-life scenario.

d_space   - an airbrushed 1980s paperback cosmos: a ringed giant, a crystal moon, her face as a nebula; a dreamer drifts in
            a white nightgown - "Sleep now. Let me decide for you." - and falls toward one lit window far below.
r_kitchen - Iris, 49, at her kitchen table at 2:13 a.m. under a humming fluorescent tube, lit by a laptop.
r_inbox   - the inbox: seventy applications, seventy rejections, arriving in the middle of the night.
r_slot    - her CV goes into a slot in the dark; the Clerks pass it along without once looking at it.
r_why     - her face: "Can someone please tell me why?"
r_answer  - the screen answers; in the glass, behind her reflection, a slit of red light.
r_phone   - her phone: the flat, high risk, decline; the loan, declined.
r_reasons - her CV, three lines lit: her age? the year she nursed her mother? the women's coding club? She'll never know.
r_scream  - "I'm qualified!" - the red floods in."""
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


# ------------------------------------------------------------------ the cosmos

def _planet(c, x, y, r, T, bands=((255, 150, 80), (240, 100, 60), (200, 60, 90), (255, 200, 120)), ring=True, tilt=-18):
    """A ringed giant, airbrushed: soft bands, a terminator, a chrome highlight, rings in front and behind."""
    c.save()
    c.translate(x, y)
    c.rotate(tilt)
    if ring:
        c.drawOval(skia.Rect.MakeLTRB(-r * 2.1, -r * 0.42, r * 2.1, r * 0.42), paint((240, 200, 160), 0.5, stroke=r * 0.18))
        c.drawOval(skia.Rect.MakeLTRB(-r * 1.75, -r * 0.33, r * 1.75, r * 0.33), paint((255, 230, 200), 0.35, stroke=r * 0.06))
    c.save()
    c.clipPath(K.circle(0, 0, r), doAntiAlias=True)
    for i, col in enumerate(bands * 3):
        yy = -r + i * (2 * r / (len(bands) * 3))
        c.drawRect(skia.Rect.MakeLTRB(-r, yy, r, yy + 2 * r / (len(bands) * 3) + 2), paint(col, blur=r * 0.05))
    c.drawCircle(0, 0, r, paint(shader=K.rad((-r * 0.4, -r * 0.4), r * 1.6, [(255, 255, 255, 0.35), (0, 0, 0, 0.0), (0, 0, 0, 0.85)], [0, 0.45, 1])))
    c.restore()
    if ring:                                                        # the near half of the ring passes in front
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(-r * 2.3, 0, r * 2.3, r))
        c.drawOval(skia.Rect.MakeLTRB(-r * 2.1, -r * 0.42, r * 2.1, r * 0.42), paint((255, 220, 180), 0.75, stroke=r * 0.18))
        c.restore()
    c.restore()
    CD.glint(c, x - r * 0.45, y - r * 0.5, r * 0.35, 0.8)


def _crystal_moon(c, x, y, r, T):
    """A small moon bristling with violet crystal spires."""
    c.drawCircle(x, y, r, paint(shader=K.rad((x - r * 0.3, y - r * 0.3), r * 1.4, [(200, 170, 255), (90, 40, 160), (20, 6, 40)])))
    rng = K.rng_at(8, 8)
    for i in range(14):
        ang = rng.uniform(-2.6, -0.5)
        L = r * rng.uniform(0.5, 1.3)
        bx, by = x + math.cos(ang) * r * 0.9, y + math.sin(ang) * r * 0.9
        tx, ty = x + math.cos(ang) * (r + L), y + math.sin(ang) * (r + L)
        w = r * 0.12
        nx, ny = -math.sin(ang) * w, math.cos(ang) * w
        c.drawPath(K.path([(bx + nx, by + ny), (tx, ty), (bx - nx, by - ny)]), paint(shader=K.lin((bx, by), (tx, ty), [(120, 60, 220), (240, 220, 255)])))
        CD.glint(c, tx, ty, r * 0.12, 0.5 + 0.5 * math.sin(T * 2 + i))


def _dreamer(c, x, y, s, T, ang=0.0, a=1.0):
    """A woman asleep in the air, airbrushed like a pulp paperback cover: hair streaming in copper ribbons, a long
    gown full of soft folds, warm rim light from the planet on one side, cold cobalt on the other, arms open."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    lp = paint()
    lp.setAlphaf(a)
    c.saveLayer(None, lp)
    # --- hair streaming up and away in long wavy locks, fanning out as if under water
    for k in range(19):
        spread = (k - 9) / 9.0
        L = 360 + 90 * math.cos(k * 1.7)
        w0 = 26 - abs(spread) * 8
        left, right = [], []
        for j in range(9):
            t = j / 8
            yy = -300 - L * t * (0.75 - 0.35 * abs(spread)) + 120 * abs(spread) * t * t
            xx = spread * (60 + 320 * t) + 46 * t * math.sin(t * 4 + T * 1.1 + k * 0.8)
            ww = w0 * (1 - 0.75 * t)
            left.append((xx - ww, yy))
            right.append((xx + ww, yy))
        lock = K.smooth(left + right[::-1])
        lp_ = paint(shader=K.lin((0, -300), (0, -300 - L), [(60, 20, 16), (150, 56, 30), (230, 120, 60)]), blur=3.0)
        c.drawPath(lock, lp_)
        c.drawPath(K.smooth(left[1:-1]), paint((255, 200, 140), 0.4, stroke=3, blur=2.5))
    # --- the gown, cut on the bias, its train rippling below her
    rip = 30 * math.sin(T * 1.3)
    gown = K.smooth([(-58, -232), (58, -232), (96, -80), (150, 160), (210 + rip, 420), (250 + rip * 1.4, 640), (120, 600), (20, 660 + rip),
                     (-90, 610), (-230 - rip, 650), (-190 - rip * 0.6, 420), (-140, 160), (-96, -80)])
    c.drawPath(gown, paint(shader=K.lin((-200, -230), (220, 640), [(196, 176, 230), (150, 120, 210), (70, 44, 150), (30, 16, 80)], [0, 0.35, 0.75, 1])))
    c.save()
    c.clipPath(gown, doAntiAlias=True)
    for k in range(7):                                               # folds: shadow and highlight side by side, airbrushed
        fx = -120 + k * 42
        c.drawPath(K.bez_path([(fx * 0.3, -200), (fx * 0.9 + 10 * math.sin(T + k), 200), (fx * 1.5 + rip, 660)]), paint((30, 14, 70), 0.45, stroke=22, blur=14))
        c.drawPath(K.bez_path([(fx * 0.3 + 14, -200), (fx * 0.9 + 18 + 10 * math.sin(T + k), 200), (fx * 1.5 + 22 + rip, 660)]),
                   paint((255, 240, 255), 0.35, stroke=10, blur=8))
    warm = paint(shader=K.lin((260, -100), (60, 200), [(255, 140, 70, 0.45), (255, 140, 70, 0.0)]))
    warm.setBlendMode(skia.BlendMode.kPlus)
    c.drawPaint(warm)                                                # the planet's warm light
    cold = paint(shader=K.lin((-260, 300), (-40, 200), [(60, 90, 255, 0.7), (60, 90, 255, 0.0)]))
    cold.setBlendMode(skia.BlendMode.kPlus)
    c.drawPaint(cold)
    c.restore()
    rim = paint((255, 190, 140), 0.8, stroke=8, blur=5)
    rim.setBlendMode(skia.BlendMode.kPlus)
    c.drawPath(gown, rim)
    # --- arms floating open: tapered, shaded, the hands loose
    for sd in (-1, 1):
        wx, wy = sd * 250, -120 + 34 * math.sin(T + sd)
        arm = K.smooth([(sd * 40, -236), (sd * 140, -210), (wx, wy - 14), (wx + sd * 16, wy), (wx, wy + 14), (sd * 140, -170), (sd * 46, -180)])
        c.drawPath(arm, paint(shader=K.lin((0, -236), (0, -170), [(255, 222, 200), (220, 160, 150), (120, 70, 90)])))
        c.drawPath(arm, paint((90, 110, 255), 0.35, stroke=10, blur=8))                         # cold fill along the underside
        c.drawOval(skia.Rect.MakeXYWH(wx + sd * 10 - 22, wy - 14, 44, 28), paint((236, 196, 180)))
        for f in range(3):
            c.drawLine(wx + sd * 26, wy - 8 + f * 8, wx + sd * 50, wy - 12 + f * 12, paint((230, 190, 176), stroke=6))
        c.drawPath(arm, paint((255, 190, 140), 0.5, stroke=4, blur=3))
    # --- the neck and the sleeping face, airbrushed, lit warm from the planet
    c.drawPath(K.smooth([(-26, -260), (26, -260), (30, -220), (-30, -220)]), paint((200, 150, 140)))
    PF.pface(c, 0, -330, 0.4, "iris", T, key=(255, 190, 150), fill=(100, 120, 255), key_at=(0.7, 0.2), fill_at=(-0.8, 0.0),
             amb=(40, 20, 60), blink=1.0, neck=False, hair=False, fall=0.4)
    c.drawPath(K.smooth([(-64, -420), (0, -446), (64, -420), (70, -380), (0, -410), (-70, -380)]), paint((90, 36, 26)))   # hairline
    glow = paint((255, 200, 220), 0.25, blur=40)
    glow.setBlendMode(skia.BlendMode.kPlus)
    c.drawCircle(0, -340, 120, glow)
    c.restore()
    c.restore()


def s_d_space(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("d_space")
    t_fall = E("d1") + 0.1
    fall = K.ease(ramp(T, t_fall, end("d_space")))
    drop = 1500 * fall
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(shader=K.lin((0, 0), (0, H), [(6, 0, 30), (40, 6, 80), (150, 30, 120), (255, 130, 70)], [0, 0.4, 0.75, 1.0])))
    c.save()
    c.translate(0, -drop)
    Wd.real_stars(c, T, n=260, y1=H + 1500, a=0.9, seed=11)
    rng = K.rng_at(4, 6)
    for i in range(14):
        CD.glint(c, rng.uniform(0, W), rng.uniform(0, 1500), rng.uniform(14, 34), 0.5 + 0.5 * math.sin(T * 2 + i))
    # her face as a nebula, asleep, watching anyway
    with K.layer(c, 0.42, skia.BlendMode.kScreen):
        P.merit(c, 560, 640, 1.6, T, eyes=0.0, talk=talk(T, "merit"), smile=0.3, rays=0.4, crown=0.5, mantle=0.0, hair=1.0,
                L=(255, 120, 220), R=(120, 160, 255), amb=(10, 0, 20))
    _planet(c, 860, 360, 190, T)
    _crystal_moon(c, 170, 1050, 110, T)
    c.restore()
    # the dreamer drifting, then falling away toward one lit window
    u = ramp(T, t0, t_fall)
    if fall < 1:
        x = 300 + 400 * u + 100 * fall
        y = 1200 - 120 * u + 900 * fall ** 1.6
        _dreamer(c, x, y, 0.85 * (1 - 0.85 * fall), T, ang=-20 + 30 * u + 160 * fall, a=1.0)
    if fall > 0:
        G.pool(c, 540, 1800 - 600 * fall, 60 + 300 * fall, (150, 255, 220), 0.8 * fall)
        c.drawRect(skia.Rect.MakeLTRB(540 - 30 * (1 + 4 * fall), 1800 - 600 * fall - 40 * (1 + 4 * fall), 540 + 30 * (1 + 4 * fall), 1800 - 600 * fall + 40 * (1 + 4 * fall)),
                   G.glow_paint((200, 255, 240), fall))
    LK.flare(860 - 190 * 0.45, 360 - 190 * 0.5 - drop, 0.5, (255, 220, 180))
    return st.arr


# ------------------------------------------------------------------ the kitchen

def _kitchen(c, T, cam=(0.0, 0.0), z=1.0):
    """The room around her: cabinets, a dark window, a fluorescent tube, an oven clock reading 02:13."""
    c.save()
    c.translate(540 + cam[0], 900 + cam[1])
    c.scale(z, z)
    c.translate(-540, -900)
    c.drawPaint(paint((26, 34, 34)))
    for i in range(4):                                              # wall cabinets
        x = 40 + i * 260
        c.drawRect(skia.Rect.MakeLTRB(x, 280, x + 240, 660), paint((52, 62, 60)))
        c.drawRect(skia.Rect.MakeLTRB(x + 14, 294, x + 226, 646), paint((70, 82, 80), stroke=4))
        c.drawRect(skia.Rect.MakeLTRB(x + 200, 450, x + 210, 500), paint((160, 170, 170)))
    win = skia.Rect.MakeLTRB(620, 720, 1000, 1120)                  # the window: black, the moon in it
    c.drawRect(win, paint((4, 6, 10)))
    c.save()
    c.clipRect(win)
    Wd.moon(c, 900, 820, 60, T, a=0.7, corona=0.4)
    c.restore()
    c.drawRect(win, paint((90, 100, 100), stroke=14))
    c.drawLine(810, 720, 810, 1120, paint((90, 100, 100), stroke=8))
    c.drawRect(skia.Rect.MakeLTRB(80, 860, 440, 1000), paint((30, 36, 36)))       # the oven, its clock
    K.text(c, "02:13", 260, 950, 70, "jost-600", (90, 255, 160), tag="plaque")
    c.drawRect(skia.Rect.MakeLTRB(0, 1120, W, 1140), paint((90, 96, 92)))
    # the tube: a long bar of light that never quite stops flickering
    fl = 0.85 + 0.15 * math.sin(T * 47) * (1 if math.sin(T * 3.1) > 0.6 else 0.2)
    c.drawRect(skia.Rect.MakeLTRB(180, 236, 900, 256), G.glow_paint((220, 255, 240), fl))
    G.pool(c, 540, 260, 700, (200, 255, 230), 0.25 * fl, squash=0.5)
    c.restore()
    return fl


def s_r_kitchen(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("r_kitchen")
    z = 1.0 + 0.02 * (T - t0)
    fl = _kitchen(c, T, z=z)
    # Iris at the table, the laptop's glow on her face
    PF.pface(c, 540, 1030, 0.92, "iris", T, key=(190, 220, 255), fill=(150, 255, 210), key_at=(0.0, 1.2), fill_at=(0.0, -1.2),
             amb=(16, 22, 22), blink=K.ease(ramp(math.fmod(T, 4.0), 3.8, 3.9)), gaze=(0.0, 0.25))
    c.drawPath(K.path([(150, 1340), (930, 1340), (1040, 1520), (40, 1520)]), paint((60, 52, 44)))           # the table
    c.drawPath(K.path([(330, 1150), (750, 1150), (780, 1360), (300, 1360)]), paint((40, 44, 50)))           # the laptop's back
    c.drawPath(K.path([(330, 1150), (750, 1150), (780, 1360), (300, 1360)]), paint((150, 170, 200), stroke=4))
    G.pool(c, 540, 1100, 380, (170, 210, 255), 0.4)
    c.drawRoundRect(skia.Rect.MakeLTRB(830, 1260, 920, 1360), 12, 12, paint((180, 60, 50)))                 # a mug
    # Iris is a composite: say so on screen
    c.drawRect(skia.Rect.MakeLTRB(130, 262, 950, 318), paint((4, 8, 8), 0.85))
    K.text(c, "DRAMATISATION · BASED ON DOCUMENTED CASES", 540, 301, 32, "jost-600", (220, 255, 240), tag="label")
    return st.arr


def _mail_row(c, y, sender, subject, time, a=1.0, new=0.0):
    c.drawRect(skia.Rect.MakeLTRB(100, y - 60, 980, y + 40), paint((30, 34, 44), a))
    if new > 0:
        c.drawRect(skia.Rect.MakeLTRB(100, y - 60, 980, y + 40), paint((80, 70, 40), new * a))
    c.drawCircle(140, y - 10, 9, paint((90, 150, 255), a))
    f = K.font("jost-600", 36)
    f2 = K.font("jost-400", 30)
    c.drawString(sender, 170, y - 14, f, paint((226, 232, 242), a))
    c.drawString(subject, 170, y + 24, f2, paint((150, 156, 170), a))
    c.drawString(time, 850, y - 14, f2, paint((150, 156, 170), a))
    c.drawLine(100, y + 40, 980, y + 40, paint((50, 56, 68), a, stroke=2))


COMPANIES = ["Northfield Systems", "Calder & Wynn", "Brightline Robotics", "Harrow Grid", "Pellucid Labs", "Westmarch Energy",
             "Orrin Aerospace", "Tessel Engineering", "Kestrel Motors", "Amberley Water", "Quarry Analytics", "Vane Devices"]


def s_r_inbox(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("r_inbox")
    c.drawPaint(paint((10, 12, 16)))
    # the screen
    scr = skia.Rect.MakeLTRB(90, 300, 990, 1320)
    c.drawRoundRect(skia.Rect.MakeLTRB(70, 280, 1010, 1340), 24, 24, paint((30, 32, 38)))
    c.drawRect(scr, paint((20, 24, 32)))
    c.save()
    c.clipRect(scr)
    t70 = Wx("r1", "seventy")
    n_rej = int(42 + 28 * K.ease(ramp(T, t0, t70 + 0.3)))
    scroll = ((T - t0) * 140) % 100
    for i in range(10):
        y = 560 + i * 100 + scroll
        k = (n_rej - i) % len(COMPANIES)
        mins = 13 + (n_rej - i) // 6
        _mail_row(c, y, COMPANIES[k], "Unfortunately, we will not be moving…", f"02:{mins:02d}", new=hit(T, t0 + ((T - t0) // 0.7) * 0.7, 0.5) if i == 0 else 0)
    c.drawRect(skia.Rect.MakeLTRB(90, 300, 990, 480), paint((34, 44, 76)))
    K.text(c, "Applications sent: 70", 130, 365, 42, "jost-600", (230, 236, 255), align="left", tag="screen")
    K.text(c, f"Rejections: {n_rej}", 130, 440, 52, "jost-600", (255, 120, 110), align="left", tag="screen")
    c.restore()
    c.drawRect(scr, paint((0, 0, 0), stroke=6))
    G.pool(c, 540, 800, 700, (160, 190, 255), 0.12)
    return st.arr


def _iris_cv(c, x, y, s, T, hl=None, a=1.0, fade=0.0, tag="card"):
    """Iris's CV: her name at the top, the three lines a machine might be counting against her."""
    lines = ["IRIS HALLORAN", "Systems engineer, 20 years", "Born: 1977", "2019-20: career break (carer)",
             "Organiser, Women in Code", "Chartered engineer"]
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    w, h = 900, 1000
    c.drawRect(skia.Rect.MakeLTRB(-w / 2, -h / 2, w / 2, h / 2), paint((214, 206, 190), a * (1 - fade)))
    f = K.font("special-elite-400", 44)
    fb = K.font("special-elite-400", 72)
    c.drawString(lines[0], -w / 2 + 60, -h / 2 + 120, fb, paint((30, 24, 30), a * (1 - fade)))
    for i, ln in enumerate(lines[1:]):
        yy = -h / 2 + 260 + i * 140
        c.drawString(ln, -w / 2 + 60, yy, f, paint((30, 24, 30), a * (1 - fade)))
        if hl and (i + 1) in hl:
            k = hl[i + 1]
            if k > 0:
                ww = f.measureText(ln)
                r = skia.Rect.MakeLTRB(-w / 2 + 40, yy - 58, -w / 2 + 80 + ww, yy + 22)
                c.drawRoundRect(r, 30, 30, G.glow_paint((255, 60, 50), 0.35 * k * a, blur=10))
                c.drawRoundRect(r, 30, 30, paint((255, 60, 50), k * a, stroke=7))
                K.text(c, "?", -w / 2 + 120 + ww, yy + 10, 90, "newrocker-400", (255, 80, 70), tag="deco", a=k * a, outline=(30, 0, 0), ow=6)
    K.reg_local(c, -w / 2 + 40, -h / 2 + 40, w / 2 - 40, h / 2 - 40, tag)
    c.restore()


def s_r_slot(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("r_slot")
    u = (T - t0) / max(0.1, end("r_slot") - t0)
    c.drawPaint(paint((4, 6, 14)))
    # a conveyor through the dark; the Clerks stamp as it passes, heads turned away
    G.pool(c, 540, 1100, 900, (90, 120, 255), 0.25)
    for k in range(4):
        x = 140 + k * 270
        P.clerk(c, x, 820, 0.42, T + k, arm=0.5 + 0.5 * math.sin(T * 6 + k), stamp=True, slit=0.9, look=-1.0 if k % 2 else 1.0,
                rim=(120, 150, 255), metal=(70, 70, 90), seed=k)
    c.drawRect(skia.Rect.MakeLTRB(-10, 1180, 1090, 1220), paint((40, 44, 60)))
    _iris_cv(c, 1250 - 1400 * u, 1000, 0.42, T, tag="deco")
    K.text(c, "NO HUMAN READER", 540, 360, 56, "newrocker-400", (200, 220, 255), tag="label", outline=(0, 0, 30), ow=8,
           a=K.ease(ramp(T, Wx("r1", "human") - 0.2, Wx("r1", "human") + 0.3)))
    return st.arr


def s_r_why(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("r_why")
    c.drawPaint(paint((6, 10, 14)))
    z = 1.0 + 0.05 * (T - t0)
    # the laptop's cold light from below and to one side; the rest of her face falls into black
    PF.pface(c, 540, 860, 2.15 * z, "iris", T, key=(200, 230, 255), fill=(20, 50, 60), key_at=(-0.55, 0.8), fill_at=(0.8, -0.6),
             amb=(4, 6, 8), talk=talk(T, "iris"), grief=0.55 + 0.35 * ramp(T, t0, t0 + 1.6), gaze=(0.1, -0.2), fall=0.9, tilt=-3)
    return st.arr


def s_r_answer(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("r_answer")
    c.drawPaint(paint((8, 10, 14)))
    scr = skia.Rect.MakeLTRB(90, 300, 990, 1320)
    c.drawRoundRect(skia.Rect.MakeLTRB(70, 280, 1010, 1340), 24, 24, paint((30, 32, 38)))
    c.drawRect(scr, paint((40, 44, 56)))
    c.save()
    c.clipRect(scr)
    # in the glass: her reflection, and behind her, a red slit
    with K.layer(c, 0.25, skia.BlendMode.kScreen):
        PF.pface(c, 420, 900, 1.2, "iris", T, key=(150, 170, 200), fill=(80, 100, 120), amb=(20, 20, 26), fear=0.4)
    k_m = K.ease(ramp(T, t0 + 0.6, t0 + 1.8))
    with K.layer(c, 0.9 * k_m, skia.BlendMode.kScreen):
        P.clerk(c, 800, 1040, 0.62, T, arm=0.0, stamp=False, slit=1.0, rim_k=1.0, metal=(90, 86, 104), seed=4)
    c.restore()
    # the dialog
    d = K.ease(ramp(T, t0, t0 + 0.3))
    box = skia.Rect.MakeLTRB(170, 560, 910, 980)
    c.drawRoundRect(box, 18, 18, paint((236, 240, 246), 0.97 * d))
    c.drawRect(skia.Rect.MakeLTRB(170, 560, 910, 640), paint((180, 30, 30), d))
    K.text(c, "Application status", 540, 616, 40, "jost-600", (255, 255, 255), tag="screen", a=d)
    K.text(c, "INELIGIBLE", 540, 770, 92, "jost-600", (190, 20, 20), tag="screen", a=d)
    K.text(c, "Reason: not available", 540, 870, 40, "jost-500", (60, 64, 70), tag="screen", a=d)
    c.drawRoundRect(skia.Rect.MakeLTRB(430, 900, 650, 960), 10, 10, paint((40, 60, 110), d))
    K.text(c, "OK", 540, 943, 36, "jost-600", (255, 255, 255), tag="screen", a=d)
    if k_m > 0:
        LK.flare(800, 1000 - (120 + 164) * 0.6, 0.35 * k_m, (255, 80, 60))
    return st.arr


def _phone(c, x, y, s, T, notes, a=1.0):
    """A phone in a hand, its lock screen stacked with notifications [(title, body, colour, k)]."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawRoundRect(skia.Rect.MakeLTRB(-330, -620, 330, 620), 60, 60, paint((14, 14, 18)))
    scr = skia.Rect.MakeLTRB(-300, -590, 300, 590)
    c.drawRoundRect(scr, 46, 46, paint(shader=K.lin((0, -590), (0, 590), [(18, 24, 36), (8, 10, 16)])))
    K.text(c, "02:16", 0, -400, 120, "jost-300", (200, 206, 220), tag="screen")
    for i, (title, body, col, k) in enumerate(notes):
        if k <= 0:
            continue
        yy = -220 + i * 330 + 40 * (1 - k)
        r = skia.Rect.MakeLTRB(-290, yy - 120, 290, yy + 170)
        c.drawRoundRect(r, 30, 30, paint((64, 70, 88), 0.97 * k))
        K.text(c, title, -262, yy - 54, 40, "jost-600", (232, 236, 246), align="left", tag="screen", a=k)
        K.text(c, body[0], -262, yy + 26, 78, "jost-600", col, align="left", tag="screen", a=k)
        if len(body) > 1:
            K.text(c, body[1], -262, yy + 110, 38, "jost-500", (226, 230, 240), align="left", tag="screen", a=k)
    c.restore()



def s_r_phone(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("r_phone")
    c.drawPaint(paint((10, 14, 16)))
    k1 = K.ease(ramp(T, Wx("r4", "rental") - 0.1, Wx("r4", "rental") + 0.3))
    k2 = K.ease(ramp(T, Wx("r4", "loan:") - 0.1, Wx("r4", "loan:") + 0.3))
    z = 1.0 + 0.03 * (T - t0)
    _phone(c, 540, 800, 0.9 * z, T, [("Rental application · flat 4B", ("HIGH RISK", "Recommendation: DECLINE"), (255, 110, 100), k1),
                                     ("Personal loan application", ("DECLINED", "We can't share the reasons"), (255, 110, 100), k2)])
    G.pool(c, 540, 820, 600, (180, 220, 255), 0.15)
    return st.arr


def s_r_reasons(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("r_reasons")
    c.drawPaint(paint((8, 10, 16)))
    k_age = K.ease(ramp(T, Wx("r4", "age?") - 0.1, Wx("r4", "age?") + 0.25))
    k_gap = K.ease(ramp(T, Wx("r4", "year") - 0.1, Wx("r4", "year") + 0.25))
    k_club = K.ease(ramp(T, Wx("r4", "women's") - 0.1, Wx("r4", "women's") + 0.25))
    fade = K.ease(ramp(T, Wx("r4", "She'll") + 0.1, end("r_reasons") + 0.2))
    z = 1.0 + 0.03 * (T - t0)
    _iris_cv(c, 540, 820, 0.82 * z, T, hl={2: k_age * (1 - fade), 3: k_gap * (1 - fade), 4: k_club * (1 - fade)}, fade=fade * 0.7)
    if fade > 0:
        Wd.smoke(c, T, 540, 1200, w=600, h=1200, color=(120, 140, 200), a=0.5 * fade, seed=9)
    return st.arr


def s_r_scream(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("r_scream")
    u = T - t0
    c.drawPaint(paint((20, 2, 4)))
    sh = 6 + 14 * ramp(T, Wx("r5", "I'm", 1), Wx("r5", "I'm", 1) + 0.3)
    shake(c, T, sh)
    G.pool(c, 540, 900, 1000, (255, 40, 30), 0.4 + 0.3 * ramp(T, t0, t0 + 1.5))
    z = 1.0 + 0.12 * u
    # lit like an ember from below; she breaks on the second "qualified"
    brk = ramp(T, Wx("r5", "I'm", 2), Wx("r5", "I'm", 2) + 0.3)
    PF.pface(c, 540, 860, 1.9 * z, "iris", T, key=(255, 140, 80), fill=(120, 10, 30), key_at=(-0.45, 0.9), fill_at=(0.9, -0.8),
             amb=(16, 2, 4), talk=talk(T, "iris"), open_=0.35 + 0.6 * brk, grief=0.8 + 0.2 * brk, fall=0.85, tilt=4 * math.sin(u * 3.0))
    c.restore()
    k = ramp(T, t0 + 0.5, t0 + 1.8)
    for i in range(3):                                              # the masks crowding in behind her
        with K.layer(c, 0.35 * k, skia.BlendMode.kScreen):
            P.clerk(c, 200 + i * 340, 1500, 0.8, T + i, arm=0.0, stamp=False, slit=1.0, rim_k=1.0, seed=i)
    return st.arr

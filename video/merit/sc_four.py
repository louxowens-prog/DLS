"""Chapter IV - THE VERDICT (blood).

v_doors   - six doors in a black façade, light behind each - job, insurance, home, loan, university, benefits - each
            slamming as it is named, a lone woman before them.
v_why     - mouths over mouths, whispering one word.
v_silence - dead silence; something red in the dark.
v_mask    - the mask, all at once, filling the frame: "The system has determined you are ineligible."
v_vars    - a head in a storm of hundreds of variables, each pulling a thread.
v_clerk   - a woman behind a counter grille looks up - then there is only a number where she was.
v_dutch   - canal houses at night; red-sealed letters slide under doors; window after window goes dark.
v_gov     - a seat of government, its lights going out."""
import math

import numpy as np
import skia

import gel as G
import kit as K
import look as LK
import pface as PF
import people as P
import world as Wd
from common import E, S, Wx, hit, shake, talk
from edit import cut, end
from kit import H, W, BLACK, WHITE, mix, paint, ramp

DOORS = [("JOB", "job."), ("INSURANCE", "Insurance."), ("HOME", "home."), ("LOAN", "loan."), ("UNIVERSITY", "university."),
         ("BENEFITS", "Benefits.")]


def _door(c, x, y, w, h, shut, T, label, a=1.0, flash=0.0):
    """A tall arched doorway; light pours out until the door swings shut (shut 0..1)."""
    arch = skia.Path()
    arch.moveTo(x - w / 2, y + h / 2)
    arch.lineTo(x - w / 2, y - h / 2 + w / 2)
    arch.arcTo(skia.Rect.MakeLTRB(x - w / 2, y - h / 2, x + w / 2, y - h / 2 + w), 180, 180, False)
    arch.lineTo(x + w / 2, y + h / 2)
    arch.close()
    c.drawPath(arch, paint((255, 214, 190), a))
    G.pool(c, x, y, w * 1.2, (255, 150, 120), 0.4 * a * (1 - shut))
    c.save()
    c.clipPath(arch, doAntiAlias=True)
    dw = w * (1 - shut)
    c.drawRect(skia.Rect.MakeLTRB(x - w / 2 + dw, y - h / 2, x + w / 2, y + h / 2), paint((40, 12, 10), a))      # the door leaf
    for k in range(3):
        c.drawRect(skia.Rect.MakeLTRB(x - w / 2 + dw + 18, y - h / 2 + 60 + k * (h - 90) / 3, x + w / 2 - 18, y - h / 2 + 40 + (k + 1) * (h - 90) / 3),
                   paint((60, 20, 16), a, stroke=4))
    c.restore()
    c.drawPath(arch, paint((90, 40, 30), a, stroke=14))
    if flash > 0:
        c.drawPath(arch, G.glow_paint((255, 60, 40), 0.7 * flash, blur=20))
    K.text(c, label, x, y - h / 2 - 26, 40, "cinzel-800", (255, 220, 200), tag="label", a=a, outline=(20, 0, 0), ow=6)


def s_v_doors(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("v_doors")
    c.drawPaint(paint((8, 2, 2)))
    z = 1.0 + 0.025 * (T - t0)
    c.save()
    c.translate(540, 900)
    c.scale(z, z)
    c.translate(-540, -900)
    stone = K.path([(40, 260), (1040, 260), (1040, 1450), (40, 1450)])
    Wd.stone_fill(c, stone, base=(40, 30, 30), light=(255, 80, 60), light_from=(0.5, 1.0), k=0.4)
    xs = (200, 530, 860)
    for i, (label, word) in enumerate(DOORS):
        x = xs[i % 3]
        y = 600 if i < 3 else 1130
        ts = Wx("v1", word) + 0.05
        shut = K.ease(ramp(T, ts - 0.12, ts + 0.08))
        _door(c, x, y, 230, 420, shut, T, label, flash=hit(T, ts + 0.08, 0.4))
    c.restore()
    # a lone woman, from behind, before them
    c.save()
    c.translate(540, 2080)
    c.scale(1.0, 1.0)
    c.drawPath(K.smooth([(-120, 0), (-130, -380), (-100, -620), (-40, -680), (40, -680), (100, -620), (130, -380), (120, 0)]), paint((4, 1, 2)))
    c.drawCircle(0, -760, 80, paint((4, 1, 2)))
    c.drawPath(K.smooth([(-84, -790), (0, -864), (84, -790), (104, -620), (60, -560), (-60, -560), (-104, -620)]), paint((4, 1, 2)))
    c.restore()
    Wd.smoke(c, T, 540, 1700, w=700, h=1400, color=(150, 40, 40), a=0.25, seed=8)
    return st.arr


def s_v_why(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("v_why")
    c.drawPaint(paint((10, 2, 4)))
    tw = S("v2")
    o = math.sin(math.pi * ramp(T, tw - 0.05, tw + 0.6)) * 0.6
    for k, (who, x, y, s, sm) in enumerate((("f_a", 400, 640, 0.6, 0.0), ("m_b", 680, 980, 0.72, -0.2), ("f_c", 470, 1260, 0.58, 0.1))):
        drift = 30 * math.sin(T * 0.8 + k)
        with K.layer(c, 0.85, skia.BlendMode.kScreen):
            PF.mouth_macro(c, x + drift, y, s, who, T, open_=o * (0.8 + 0.2 * k), smile=sm, key=(255, 150, 120), fill=(170, 60, 80))
    return st.arr


def s_v_silence(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("v_silence")
    c.drawPaint(paint((3, 0, 1)))
    k = ramp(T, t0, end("v_silence"))
    c.drawRect(skia.Rect.MakeLTRB(540 - 40 * k, 760, 540 + 40 * k, 766), G.glow_paint((255, 40, 30), 0.35 * k))      # far away, a slit opens
    return st.arr


def s_v_mask(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("v_mask")
    u = (T - t0)
    lunge = 1 - (1 - min(1.0, u / 0.16)) ** 3
    s = 0.6 + 1.9 * lunge + 0.06 * max(0.0, u - 0.16)
    sh = 22 * hit(T, t0 + 0.1, 0.6) + 3
    shake(c, T, sh)
    strobe = 1.0 if (int(T * 24) // 2) % 2 == 0 else 0.35
    c.drawPaint(paint((6, 0, 2)))
    G.pool(c, 540, 700, 1300, (255, 30, 20), 0.35 * strobe)
    P.clerk(c, 540, 1180 + 560 * (s - 1.6) * 0.0, s, T, arm=0.0, stamp=False, slit=1.0, rim_k=1.6 * strobe, metal=(80, 74, 86), seed=2)
    slit_y = 1180 - (120 + 164) * s
    LK.flare(540, slit_y, 1.0 * strobe, (255, 90, 70))
    c.restore()
    return st.arr


VARS = ["AGE", "POSTCODE", "CAREER GAP", "CLUBS", "FIRST NAME", "SCHOOL", "TYPING SPEED", "PHONE MODEL", "SHOPPING", "COMMUTE",
        "CREDIT FILE", "FRIENDS", "SPELLING", "SLEEP", "VOICE", "PHOTO", "EMAIL DOMAIN", "LANGUAGE", "HOBBIES", "DEBT", "RENT",
        "MOVES", "JOB TITLES", "GAPS", "LIKES", "SEARCHES", "BROWSER", "TIME ONLINE", "HEIGHT", "SALARY", "BANK", "DEVICE",
        "ACCENT", "STREET", "PAUSES", "SCROLLS", "TYPOS", "NAME LENGTH", "INSURANCE", "HEALTH APP", "STEPS", "MUSIC"]


def s_v_vars(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("v_vars")
    c.drawPaint(paint((10, 4, 16)))
    G.pool(c, 540, 820, 700, (160, 90, 255), 0.35)
    # the head at the centre of it all, in silhouette
    c.drawCircle(540, 760, 150, paint((6, 2, 10)))
    c.drawPath(K.smooth([(380, 1300), (400, 1060), (470, 940), (610, 940), (680, 1060), (700, 1300)]), paint((6, 2, 10)))
    rng = K.rng_at(3, 3)
    n = 220
    grow = K.ease(ramp(T, t0, t0 + 1.2))
    for i in range(n):
        ang = rng.uniform(0, 6.283) + (T - t0) * rng.uniform(0.05, 0.25) * (1 if i % 2 else -1)
        r = rng.uniform(220, 560) * (0.4 + 0.6 * grow)
        x = 540 + math.cos(ang) * r
        y = 800 + math.sin(ang) * r * 1.05
        if y > 1290 or y < 250:
            continue
        name = VARS[i % len(VARS)]
        wv = rng.uniform(-0.6, 0.6)
        size = rng.uniform(18, 30) if i % 7 else 34
        a = 0.35 + 0.6 * rng.random()
        c.drawLine(x, y, 540, 760, paint((200, 160, 255), 0.07 * a, stroke=1))
        col = (255, 120, 120) if wv < 0 else (190, 220, 255)
        K.text(c, f"{name} {wv:+.2f}", x, y, size, "jost-500", col, tag="deco", a=a * grow)
    return st.arr


def s_v_clerk(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("v_clerk")
    t_score = Wx("v4", "You", 1) - 0.1
    k = K.ease(ramp(T, t_score, t_score + 0.5))
    c.drawPaint(paint((20, 8, 4)))
    # the counter: a brass grille in a dark wooden wall
    c.drawRect(skia.Rect.MakeLTRB(140, 360, 940, 1260), paint((50, 26, 14)))
    win = skia.Rect.MakeLTRB(220, 440, 860, 1180)
    c.drawRect(win, paint((24, 12, 8)))
    c.save()
    c.clipRect(win)
    if k < 1:
        with K.layer(c, 1 - k):
            G.pool(c, 540, 760, 500, (255, 170, 90), 0.4)
            PF.pface(c, 540, 760, 0.95, "f_b", T, key=(255, 190, 120), fill=(120, 70, 50), key_at=(-0.6, 0.4), amb=(30, 16, 10),
                     gaze=(0.0, -0.1), smile=0.1, blink=0.0)
    if k > 0:
        with K.layer(c, k):
            c.drawRect(win, paint((4, 2, 2)))
            K.text(c, "412", 540, 870, 260, "newrocker-400", (255, 70, 50), tag="label", outline=(30, 0, 0), ow=12)
            G.pool(c, 540, 780, 420, (255, 60, 40), 0.35)
            K.text(c, "SCORE", 540, 560, 56, "cinzel-800", (255, 200, 180), tag="label")
    c.restore()
    for i in range(17):                                            # the speaking grille at the foot of the window
        x = 240 + i * 37.5
        c.drawLine(x, 1040, x, 1180, paint((190, 150, 70), stroke=5))
    c.drawLine(220, 1040, 860, 1040, paint((210, 170, 80), stroke=8))
    c.drawRect(win, paint((210, 170, 80), stroke=12))
    K.text(c, "ENQUIRIES", 540, 420, 40, "cinzel-800", (230, 190, 110), tag="plaque")
    c.drawRect(skia.Rect.MakeLTRB(200, 1180, 880, 1220), paint((120, 80, 40)))
    return st.arr


def _house(c, x, base, w, h, kind, lit, T, red=0.0, seed=0, letter=0.0):
    """A narrow canal house: brick front, a stepped or bell gable, tall windows; lit (0..1) fades them out."""
    col = (40, 34, 46)
    c.drawRect(skia.Rect.MakeLTRB(x - w / 2, base - h, x + w / 2, base), paint(col))
    if kind == 0:                                                   # stepped gable
        steps = 4
        for i in range(steps):
            sw = w / 2 * (1 - (i + 1) / (steps + 1))
            c.drawRect(skia.Rect.MakeLTRB(x - sw, base - h - (i + 1) * 40, x + sw, base - h - i * 40), paint(col))
    else:                                                           # bell gable
        c.drawPath(K.smooth([(x - w / 2, base - h), (x - w * 0.3, base - h - 60), (x - w * 0.18, base - h - 140), (x, base - h - 170),
                             (x + w * 0.18, base - h - 140), (x + w * 0.3, base - h - 60), (x + w / 2, base - h)]), paint(col))
    rng = K.rng_at(seed, 7)
    rows = int(h / 120)
    for r in range(rows):
        for q in range(2):
            wx = x - w / 4 + q * w / 2
            wy = base - h + 40 + r * 120
            on = lit * (1 if rng.random() < 0.85 else 0)
            c.drawRect(skia.Rect.MakeLTRB(wx - 24, wy, wx + 24, wy + 74), paint((10, 8, 14)))
            if on > 0:
                c.drawRect(skia.Rect.MakeLTRB(wx - 22, wy + 2, wx + 22, wy + 72), G.glow_paint((255, 190, 110), on))
                G.pool(c, wx, wy + 36, 70, (255, 170, 90), 0.25 * on)
    # the door, and the red-sealed letter at its foot
    c.drawRect(skia.Rect.MakeLTRB(x - 22, base - 110, x + 22, base), paint((20, 14, 20)))
    if red > 0:
        c.drawRect(skia.Rect.MakeLTRB(x - 22, base - 110, x + 22, base), G.glow_paint((255, 30, 20), 0.55 * red))
    if letter > 0:
        lx = x - 60 + 50 * min(1.0, letter * 1.5)
        c.drawRect(skia.Rect.MakeLTRB(lx - 26, base - 22, lx + 26, base - 2), paint((220, 214, 200), min(1.0, letter * 3)))
        c.drawCircle(lx, base - 12, 7, paint((200, 20, 30), min(1.0, letter * 3)))


def s_v_dutch(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("v_dutch")
    t_flag = Wx("v5", "foreign")
    t_acc = Wx("v5", "Tens")
    pull = K.ease(ramp(T, t_acc - 0.3, end("v_dutch")))
    Wd.sky(c, (2, 4, 18), (10, 18, 50), (30, 40, 90))
    Wd.real_stars(c, T, n=80, y1=700, a=0.6)
    Wd.moon(c, 820, 420, 120, T, a=0.8, corona=0.6)
    s = 1.0 - 0.55 * pull
    c.save()
    c.translate(540, 1200)
    c.scale(s, s)
    c.translate(-540, -1200)
    rows = 1 + int(pull * 3.5)
    for r in range(rows, -1, -1):
        base = 1200 - r * 420
        n = 9 + r * 2
        for i in range(-n // 2 - 2, n // 2 + 3):
            x = 540 + i * 150 + (75 if r % 2 else 0)
            seed = r * 100 + i
            rng = K.rng_at(seed, 3)
            flagged = rng.random() < 0.45
            red = K.ease(ramp(T, t_flag + rng.uniform(0, 1.2), t_flag + rng.uniform(1.2, 1.8))) if flagged else 0.0
            dark_at = t_acc + rng.uniform(0.0, 3.0) * (1 + r * 0.3)
            lit = 1.0 - (K.ease(ramp(T, dark_at, dark_at + 0.5)) if flagged or r > 0 else 0.0)
            letter = ramp(T, dark_at - 0.6, dark_at) if flagged else 0.0
            _house(c, x, base, 140, 420 + 60 * (rng.random() - 0.5), int(rng.random() * 2), lit, T, red=red, seed=seed, letter=letter)
        if r == 0:                                                  # the canal, and the windows' reflections in it
            c.drawRect(skia.Rect.MakeLTRB(-1000, 1200, 2000, 1600), paint((6, 8, 24)))
            for i in range(30):
                yy = 1220 + i * 12
                c.drawLine(-1000, yy, 2000, yy, paint((60, 70, 140), 0.15, stroke=2))
    c.restore()
    k2 = K.ease(ramp(T, t_flag - 0.1, t_flag + 0.4))
    c.drawRect(skia.Rect.MakeLTRB(0, 270, W, 360 + 70 * k2), paint((2, 4, 16), 0.82))
    K.text(c, "THE NETHERLANDS · CHILDCARE BENEFITS", 540, 330, 36, "special-elite-400", (220, 230, 255), tag="label", outline=(0, 0, 20), ow=6,
           a=K.ease(ramp(T, t0 + 0.3, t0 + 0.9)))
    K.text(c, "RISK FACTOR: NATIONALITY", 540, 400, 44, "special-elite-400", (255, 110, 100), tag="label", outline=(20, 0, 0), ow=6, a=k2)
    return st.arr


def s_v_gov(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("v_gov")
    t_res = Wx("v5", "resigned.")
    dark = K.ease(ramp(T, t_res - 0.3, t_res + 0.8))
    Wd.sky(c, (2, 4, 18), (10, 18, 50), (30, 40, 90))
    Wd.real_stars(c, T, n=80, y1=700, a=0.6)
    # a seat of government: a pediment on columns, a tower with a lit clock
    col = (60, 60, 80)
    c.drawRect(skia.Rect.MakeLTRB(120, 760, 960, 1300), paint(col))
    c.drawPath(K.path([(100, 760), (540, 560), (980, 760)]), paint(mix(col, WHITE, 0.08)))
    c.drawRect(skia.Rect.MakeLTRB(470, 300, 610, 600), paint(col))
    c.drawPath(K.path([(450, 300), (540, 200), (630, 300)]), paint(col))
    lit = 1 - dark
    c.drawCircle(540, 400, 46, paint((10, 10, 20)))
    c.drawCircle(540, 400, 42, G.glow_paint((255, 220, 160), 0.8 * lit))
    for i in range(8):
        x = 170 + i * 105
        c.drawRect(skia.Rect.MakeLTRB(x, 800, x + 36, 1280), paint(mix(col, WHITE, 0.15)))
        rng = K.rng_at(i, 1)
        for r in range(3):
            wy = 840 + r * 140
            off = K.ease(ramp(T, t_res - 0.2 + rng.uniform(0, 0.8), t_res + rng.uniform(0.4, 1.0)))
            c.drawRect(skia.Rect.MakeLTRB(x + 46, wy, x + 86, wy + 90), paint((10, 10, 20)))
            c.drawRect(skia.Rect.MakeLTRB(x + 48, wy + 2, x + 84, wy + 88), G.glow_paint((255, 200, 120), 0.8 * (1 - off)))
    c.drawRect(skia.Rect.MakeLTRB(80, 1300, 1000, 1340), paint(mix(col, WHITE, 0.1)))
    c.drawRect(skia.Rect.MakeLTRB(0, 280, W, 360), paint((2, 4, 16), 0.82 * K.ease(ramp(T, t_res - 0.2, t_res + 0.3))))
    K.text(c, "THE GOVERNMENT RESIGNS · JANUARY 2021", 540, 330, 40, "special-elite-400", (240, 244, 255), tag="label", outline=(0, 0, 20), ow=6,
           a=K.ease(ramp(T, t_res - 0.2, t_res + 0.3)))
    return st.arr

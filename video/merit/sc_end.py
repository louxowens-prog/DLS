"""The eruption, the twist, and the quiet lesson.

x_erupt   - everything at once: the masks, the stamps, the doors, the fire, her eye, in strobing red, magenta, violet and
            cobalt; in the middle of it her face, calm: "Nothing personal. Only patterns."
y_black   - dead silence.
y_eye     - her eye opens on you; in it, a phone, a feed, a thumb scrolling: "I've been reading you too."
y_dossier - SUBJECT: YOU. What you watched, where you paused, what it guessed. Reason: withheld. The stamp comes down.
e_fire    - the fire again, quiet. "AI isn't born biased. It inherits us."
e_tablet  - a stone in the firelight: what NIST says trustworthy AI is.
e_ask     - three slabs, three questions, each lit as it is asked.
e_hand    - the stamp comes down - and a human hand stops it.
e_moon    - the moon over the pines turns out to be an eye; it looks at you; everything else goes dark."""
import math

import numpy as np
import skia

import cards as CD
import gel as G
import kit as K
import look as LK
import pface as PF
import people as P
import sc_four as F4
import sc_three as S3
import world as Wd
from common import E, S, Wx, hit, shake, talk
from edit import cut, end
from kit import H, W, BLACK, WHITE, mix, paint, ramp

WASHES = [(255, 30, 40), (255, 40, 200), (140, 60, 255), (40, 80, 255)]


SEQ = ["mask", "stamps", "army", "figure", "eye", "doors", "lunge", "figure", "army", "stamps", "mask", "eye"]


def _figure(c, T, u, col):
    """A woman's silhouette against the light; the stamp comes down on her and she runs like wet paint."""
    hitu = 0.35
    sy = 120 + 560 * min(1.0, (u / hitu) ** 2)
    c.save()
    if u > hitu:                                                     # sliced and slipping sideways
        v = (u - hitu) / (1 - hitu)
        for b in range(7):
            c.save()
            c.clipRect(skia.Rect.MakeLTRB(0, 600 + b * 190, W, 790 + b * 190))
            c.translate((-1) ** b * 60 * v * (1 + b * 0.3), 0)
            _silhouette(c)
            c.restore()
        rng = K.rng_at(77, 3)
        for i in range(26):                                          # running down like paint
            x = rng.uniform(330, 750)
            y0 = rng.uniform(820, 1100)
            L = 200 + 900 * v * rng.uniform(0.4, 1.2)
            w = rng.uniform(10, 34)
            c.drawRoundRect(skia.Rect.MakeLTRB(x - w / 2, y0, x + w / 2, y0 + L), w / 2, w / 2, paint(mix(col, BLACK, 0.55), 0.9))
            c.drawCircle(x, y0 + L, w * 0.7, paint(mix(col, BLACK, 0.55), 0.9))
    else:
        _silhouette(c)
    c.restore()
    # the stamp's face, seen from below, coming down out of the light
    c.drawRect(skia.Rect.MakeLTRB(-100, sy - 1400, W + 100, sy), paint((14, 6, 8)))
    c.drawRect(skia.Rect.MakeLTRB(-100, sy - 40, W + 100, sy), paint(mix(col, WHITE, 0.2), 0.8))


def _silhouette(c):
    c.drawCircle(540, 760, 92, paint((4, 0, 2)))
    c.drawPath(K.smooth([(430, 700), (540, 640), (650, 700), (660, 860), (600, 860), (540, 800), (480, 860), (420, 860)]), paint((4, 0, 2)))   # the bob
    c.drawPath(K.smooth([(500, 830), (580, 830), (590, 920), (760, 980), (840, 1100), (880, 2000), (200, 2000), (240, 1100), (320, 980), (490, 920)]),
               paint((4, 0, 2)))


def _chaos(c, T, m, tb, beat, col, back):
    """One beat of the eruption: motif m, from tb. back: a strobe flash behind, the motif in silhouette."""
    u = (T - tb) / beat
    if m == "mask":
        for i in range(3):
            P.clerk(c, 180 + i * 360, 1200 + 80 * (i % 2), 0.9, T + i, arm=0.5 + 0.5 * math.sin(T * 9 + i), stamp=True, slit=1.0, rim_k=1.6, seed=i)
    elif m == "stamps":
        rng = K.rng_at(int(tb * 10), 2)
        for i in range(9 + int(6 * u)):
            P.stamp_mark(c, rng.uniform(200, 880), rng.uniform(320, 1120), rng.uniform(0.45, 0.8), ang=rng.uniform(-25, 25), tag="deco", seed=i)
    elif m == "army":
        for r in range(4, -1, -1):
            z = 0.6 + r * 0.7
            for q in range(3 + r * 2):
                x = W / 2 + (q - (2 + r)) * W * (1.1 + 0.3 * r) / (3 + r * 2)
                S3._mini_clerk(c, x, 600 + 1100 / z, 0.95 / z, arm=0.5 + 0.5 * math.cos(T * 9 + r), strobe=1.0, back=back, light=col)
    elif m == "eye":
        PF.eye_macro(c, 540, 900, 1.15, "merit", T, wide=0.4, key=(255, 80, 60), fill=(200, 60, 255))
    elif m == "doors":
        for i in range(3):
            F4._door(c, 200 + i * 340, 900, 260, 520, ((T * 5 + i) % 1.0), T, "", flash=1.0)
    elif m == "figure":
        _figure(c, T, u, col)
    else:                                                            # the mask, lunging
        P.clerk(c, 540, 1500, 2.0 + 0.8 * u, T, arm=0.0, stamp=False, slit=1.0, rim_k=1.8, seed=7)


def s_x_erupt(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("x_erupt")
    t1 = S("x1")
    # fast cuts until she speaks, then a little slower under her voice
    if T < t1:
        beat = 0.19
        k = int((T - t0) / beat)
        tb = t0 + k * beat
    else:
        beat = 0.27
        k = 100 + int((T - t1) / beat)
        tb = t1 + (k - 100) * beat
    col = WASHES[k % len(WASHES)]
    back = (T - tb) < 0.075                                           # the first frames of every beat: a strobe flash
    if back:
        c.drawPaint(paint(mix(col, WHITE, 0.12)))
    else:
        c.drawPaint(paint(mix(col, BLACK, 0.82)))
    shake(c, T, 16)
    if not back:
        G.pool(c, 540, 900, 1200, col, 0.45)
    _chaos(c, T, SEQ[k % len(SEQ)], tb, beat, col, back)
    c.restore()
    # a wall of fire along the bottom of everything
    for i in range(5):
        Wd.fire(c, 60 + i * 240, 1990, 1.25 + 0.25 * math.sin(T * 3 + i), T, a=0.85, seed=20 + i, logs=False, glow=0.3)
    # colour flooding the frame in time with the beat
    p = paint(col, 0.3)
    p.setBlendMode(skia.BlendMode.kMultiply)
    c.drawPaint(p)
    c.drawPaint(G.glow_paint(col, 0.3 * hit(T, tb, beat)))
    # her face, calm in the middle of it
    kf = K.ease(ramp(T, t1 - 0.4, t1 + 0.3))
    if kf > 0:
        with K.layer(c, 0.85 * kf, skia.BlendMode.kScreen):
            P.merit(c, 540, 860, 1.5, T, eyes=1.0, talk=talk(T, "merit"), smile=0.4, rays=1.0, crown=1.0, mantle=1.0,
                    L=mix(col, WHITE, 0.3), R=(160, 80, 255))
        LK.flare(540, 860 - 150 * 1.5, 0.8 * kf, mix(col, WHITE, 0.5))
    return st.arr


def s_y_black(T, idx):
    st = K.Stage((0, 0, 0))
    return st.arr


def _feed(c, r, T):
    """What her eye sees, reflected: a phone in a dark room, a vertical feed, a thumb scrolling - you."""
    t_pause, t_scroll = Wx("y1", "pause."), Wx("y1", "scroll.")
    c.save()
    c.scale(r / 200, r / 200)
    c.drawRoundRect(skia.Rect.MakeLTRB(-70, -130, 70, 130), 16, 16, paint((20, 20, 26), 0.9))
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(-62, -118, 62, 118))
    scroll = 0.0
    if T > t_scroll:
        scroll = -240 * K.ease(ramp(T, t_scroll, t_scroll + 0.5))
    for i in range(3):
        yy = -118 + i * 240 + scroll
        c.drawRect(skia.Rect.MakeLTRB(-62, yy, 62, yy + 236), paint((150, 20, 30) if i == 0 else (40, 30, 80)))
        if i == 0:
            c.drawRect(skia.Rect.MakeLTRB(-40, yy + 90, 40, yy + 130), paint((240, 200, 190), stroke=4))
    if t_pause <= T < t_scroll:
        c.drawRect(skia.Rect.MakeLTRB(-18, -26, -6, 26), paint(WHITE, 0.9))
        c.drawRect(skia.Rect.MakeLTRB(6, -26, 18, 26), paint(WHITE, 0.9))
    c.restore()
    th = 60 if T < t_scroll else 60 - 100 * K.ease(ramp(T, t_scroll, t_scroll + 0.5))
    c.drawPath(K.capsule(40, 180, 10, th, 46, 40), paint((200, 160, 140), 0.85))                  # a thumb
    c.restore()


def s_y_eye(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("y_eye")
    t_open = cut("y_eye") + 0.03
    bl = 1 - K.ease(ramp(T, t_open, t_open + 0.25))
    z = 1.0 + 0.06 * (T - t0)
    sh = 12 * hit(T, t_open, 0.5)
    shake(c, T, sh)
    PF.eye_macro(c, 540, 860, 1.12 * z, "merit", T, blink=bl, gaze=(0.0, 0.0), key=(255, 90, 140), fill=(160, 70, 255), wide=0.25,
                 reflection=(lambda cc, r: _feed(cc, r, T)) if T > Wx("y1", "I've") else None, pupil=0.6)
    c.restore()
    return st.arr


def s_y_dossier(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("y_dossier")
    t_stamp = E("y2") + 0.02
    c.drawPaint(paint((14, 4, 6)))
    G.pool(c, 540, 820, 900, (255, 70, 50), 0.32)
    z = 1.0 + 0.03 * (T - t0)
    sh = 18 * hit(T, t_stamp, 0.5)
    shake(c, T, sh)
    c.translate(540, 820)
    c.scale(z, z)
    c.translate(-540, -820)
    card = skia.Rect.MakeLTRB(110, 300, 970, 1300)
    c.drawRect(card, paint((206, 194, 170)))
    c.drawRect(skia.Rect.MakeLTRB(110, 300, 970, 420), paint((40, 20, 20)))
    K.text(c, "SUBJECT:  YOU", 540, 385, 70, "special-elite-400", (255, 230, 210), tag="card")
    mm, ss = divmod(int(T), 60)
    rows = [("WATCHED", f"{mm}:{ss:02d} of this video"), ("PAUSED", "3 times"), ("REPLAYED", "0:41 - 0:47"), ("SCROLL SPEED", "slow, late at night"),
            ("PREDICTED", "renting, 40+, anxious"), ("SCORE", "0.31")]
    for i, (k_, v) in enumerate(rows):
        a = K.ease(ramp(T, t0 + 0.15 + i * 0.22, t0 + 0.35 + i * 0.22))
        y = 510 + i * 105
        K.text(c, k_, 150, y, 40, "special-elite-400", (90, 30, 30), align="left", tag="card", a=a)
        K.text(c, v, 450, y, 36, "special-elite-400", (30, 20, 20), align="left", tag="card", a=a)
    a = K.ease(ramp(T, t0 + 1.5, t0 + 1.8))
    K.text(c, "REASON", 150, 1170, 40, "special-elite-400", (90, 30, 30), align="left", tag="card", a=a)
    c.drawRect(skia.Rect.MakeLTRB(500, 1130, 900, 1185), paint((10, 6, 8), a))
    K.text(c, "WITHHELD", 700, 1240, 30, "special-elite-400", (120, 40, 40), tag="card", a=a)
    if T >= t_stamp:
        P.stamp_mark(c, 540, 860, 0.9, ang=-12, a=1.0, tag="deco")
        c.drawPaint(G.glow_paint((255, 200, 180), 0.5 * hit(T, t_stamp, 0.25)))
    c.restore()
    return st.arr


def s_e_fire(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("e_fire")
    z = 1.0 + 0.03 * (T - t0)
    c.save()
    c.translate(540, 1300)
    c.scale(z, z)
    c.translate(-540, -1300)
    Wd.forest(c, T, cam_y=0, moon_r=280, moon_xy=(720, 420), stars=0.7, seed=0, moon_a=0.8)
    G.fog(c, T, -100, 1200, 1180, 1700, (150, 90, 120), a=0.3, n=8, seed=5)
    Wd.fire(c, 540, 1560, 0.8, T, seed=1, glow=0.7)
    Wd.embers(c, T, 540, 1480, spread=220, height=1500, n=80, a=0.9, to_stars=0.6, seed=3, size=3.4)
    Wd.smoke(c, T, 540, 1300, w=360, h=1300, color=(140, 90, 110), a=0.28, seed=3)
    c.restore()
    return st.arr


NIST = [("VALID & RELIABLE", "reliable,"), ("SAFE", None), ("SECURE & RESILIENT", None), ("ACCOUNTABLE & TRANSPARENT", "transparent,"),
        ("EXPLAINABLE & INTERPRETABLE", "explainable,"), ("PRIVACY-ENHANCED", "privacy-enhanced,"), ("FAIR, HARMFUL BIAS MANAGED", "fair,")]


def s_e_tablet(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("e_tablet")
    # wide on the whole stone, then pushing in and travelling down it, line by line, as each one is named
    named = [(Wx("e1", w), i) for i, (_, w) in enumerate(NIST) if w]
    li = float(np.interp(T, [t for t, _ in named], [i for _, i in named]))
    push = K.ease(ramp(T, named[0][0] - 0.3, named[0][0] + 0.9))
    z = 1.0 + 0.015 * (T - t0) + 0.22 * push
    cy = 900 + (560 + li * 108 - 40 - 900) * push
    sy = 900 - 80 * push
    c.drawPaint(paint((10, 4, 2)))
    c.save()
    c.translate(540, sy)
    c.scale(z, z)
    c.translate(-540, -cy)
    G.pool(c, 540, 1600, 1100, (255, 110, 40), 0.4 * G.flicker(T, 2, 0.12))
    Wd.fire(c, 540, 1760, 0.6, T, seed=4)
    slab = K.smooth([(110, 1360), (100, 420), (160, 280), (540, 230), (920, 280), (980, 420), (970, 1360)])
    Wd.stone_fill(c, slab, base=(60, 52, 48), light=(255, 140, 70), light_from=(0.5, 1.1), k=0.6)
    # lettering that the camera has carried up past the top of the frame is not drawn (it would sit under the app's UI)
    vis = lambda y: max(0.0, min(1.0, (sy + (y - 60 - cy) * z - 230) / 60))
    if vis(380) > 0.02:
        Wd.engraved(c, "TRUSTWORTHY AI", 540, 380, 64, "cinzel-800", glow=0.8, color=(255, 220, 180), a=vis(380))
    if vis(440) > 0.02:
        Wd.engraved(c, "NIST AI RISK MANAGEMENT FRAMEWORK 1.0", 540, 440, 28, "cinzel-800", glow=0.6, color=(255, 200, 160), a=vis(440))
    t_all = Wx("e1", "managed.") - 0.2
    for i, (ln, word) in enumerate(NIST):
        y = 560 + i * 108
        tk = Wx("e1", word) if word else t_all
        k = K.ease(ramp(T, tk - 0.15, tk + 0.25))
        if vis(y) > 0.02:
            Wd.engraved(c, ln, 540, y, 44 if len(ln) < 22 else 35, "cinzel-800", glow=0.45 + 0.55 * k, color=mix((228, 180, 130), (255, 226, 160), k), a=vis(y))
        if k > 0 and k < 1:
            LK.flare(540, y - 15, 0.25 * math.sin(math.pi * k), (255, 200, 140))
    c.restore()
    return st.arr


def s_e_ask(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("e_ask")
    c.drawPaint(paint((8, 4, 2)))
    G.pool(c, 540, 1500, 1000, (255, 110, 40), 0.35 * G.flicker(T, 3, 0.12))
    Wd.fire(c, 540, 1720, 0.55, T, seed=6)
    Qs = [("WHAT DATA?", "data?"), ("WHO CHECKED IT?", "checked"), ("HOW DO I APPEAL?", "appeal?")]
    for i, (q, word) in enumerate(Qs):
        y = 520 + i * 290
        slab = K.smooth([(150, y + 110), (140, y - 90), (540, y - 120), (940, y - 90), (930, y + 110), (540, y + 130)])
        k0 = K.ease(ramp(T, t0 + i * 0.2, t0 + 0.6 + i * 0.2))
        with K.layer(c, k0):
            Wd.stone_fill(c, slab, base=(56, 48, 44), light=(255, 140, 70), light_from=(0.5, 1.3), k=0.5)
        k = K.ease(ramp(T, Wx("e2", word) - 0.15, Wx("e2", word) + 0.2))
        Wd.engraved(c, q, 540, y + 26, 66, "cinzel-800", glow=0.5 + 0.5 * k, color=mix((236, 190, 140), (255, 236, 180), k), a=k0)
    return st.arr


def s_e_hand(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("e_hand")
    t_human = Wx("e2", "human") - 0.25
    c.drawPaint(paint((12, 6, 4)))
    G.pool(c, 540, 1000, 900, (255, 130, 60), 0.35)
    # a file on a desk; the stamp descending; a human hand rising to stop it
    c.save()
    c.translate(540, 1100)
    c.rotate(-3)
    Wd.page(c, 0, 0, 620, 800, 0, T, lines=12, seed=31, title="APPLICANT: YOU", title_size=46)
    c.restore()
    stop = K.ease(ramp(T, t_human - 0.3, t_human))
    down = K.ease(ramp(T, t0, t_human))
    sy = 200 + 560 * down * (1 - 0.0)
    if T > t_human:
        sy = 200 + 560 - 30 * K.ease(ramp(T, t_human, t_human + 0.6))
    c.drawRect(skia.Rect.MakeLTRB(510, -100, 570, sy - 160), paint((110, 104, 120)))
    c.drawRect(skia.Rect.MakeLTRB(510, -100, 530, sy - 160), paint((200, 190, 200), 0.5))
    blk = K.rrect(300, sy - 180, 780, sy, 22)
    c.drawPath(blk, paint(shader=K.lin((0, sy - 180), (0, sy), [(170, 110, 70), (80, 44, 28)])))
    c.drawPath(blk, paint((220, 160, 110), 0.7, stroke=6))
    c.drawRect(skia.Rect.MakeLTRB(290, sy - 10, 790, sy + 24), paint((140, 16, 22)))
    hy = 1900 - 1040 * stop
    P.hand(c, 560, hy + 60, 1.05, ang=-4, skin=(200, 150, 120), light=(255, 170, 100))
    if T > t_human:
        G.pool(c, 540, sy + 40, 300, (255, 220, 180), 0.5 * hit(T, t_human, 0.6))
    a = K.ease(ramp(T, Wx("e2", "In") - 0.1, Wx("e2", "In") + 0.4))
    K.text(c, "EU GDPR ART. 22  ·  UK DATA (USE AND ACCESS) ACT 2025", 540, 290, 34, "jost-600", (255, 224, 196), tag="label", a=a, outline=(20, 6, 0), ow=7)
    ah = K.ease(ramp(T, t_human, t_human + 0.4))
    K.text(c, "THE RIGHT TO A HUMAN", 540, 376, 66, "newrocker-400", (255, 236, 210), tag="label", a=ah, outline=(30, 10, 0), ow=8)
    K.text(c, "for decisions made solely by machine", 540, 440, 36, "jost-600", (255, 214, 180), tag="label", a=ah, outline=(20, 6, 0), ow=7)
    K.text(c, "with legal or similarly significant effects", 540, 488, 36, "jost-600", (255, 214, 180), tag="label", a=ah, outline=(20, 6, 0), ow=7)
    return st.arr


def s_e_moon(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("e_moon")
    total = end("e_moon")
    open_ = K.ease(ramp(T, t0 + 0.2, t0 + 0.9))
    dark = K.ease(ramp(T, t0 + 0.9, t0 + 1.4))
    Wd.forest(c, T, cam_y=0, moon_r=380, moon_xy=(540, 760), eye=open_, pupil=(0.0, 0.05 + 0.1 * open_), stars=1.0, seed=0, moon_a=1.0)
    # everything but the eye goes dark; the eye stays, burned into the screen, then it too fades
    if dark > 0:
        c.drawPaint(paint((0, 0, 0), dark))
        fade = K.ease(ramp(T, total - 0.55, total - 0.05))
        Wd.moon(c, 540, 760, 380, T, a=(1 - fade), eye=open_, pupil=(0.0, 0.15), corona=0.4 * (1 - fade))
        G.pool(c, 540, 760, 520, (255, 40, 40), 0.35 * (1 - fade))
    LK.flare(540, 760, 0.45 * (1 - 0.6 * dark), (255, 200, 200))
    return st.arr

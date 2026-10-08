"""The collapse, the twist, and the lesson.

x_collapse - the dream tears apart: cases shatter, the sky splits, a sandstorm; the Curator rises; every door in the
             desert opens onto her eye; her face in the storm: "Every door you open, I'm already inside."
y_vitrine  - dead silence. One case on the salt flat at dusk; Nadia's likeness pours away as sand, leaving only the
             brass labels of her day.
y_phone    - in the case now: a phone on a velvet cushion, its sensors labelled; we push into its screen, and find
             this.
y_glass    - black glass. Your silhouette in it. Something rises behind you.
z_room     - the white room again, quiet; the chair empty.
z_law      - what the EU now bans.
z_ask      - three questions on three screens.
z_final    - an endless floor of clinical chairs, each with someone lying still, a phone glowing on each chest; in
             the exact centre one chair is empty. RESERVED."""
import math

import numpy as np
import skia

import cast as CA
import cold as CO
import couture as C
import dream as D
import gel as G
import hall as Hl
import kit as K
import look as LK
import pers as Pr
import props as Pp
from common import E, S, Wx, hit, shake, slow, stutter, talk, zoom
from edit import cut, end
from kit import BLACK, H, W, WHITE, mix, paint, ramp


# ------------------------------------------------------------------ the collapse

def _shatter_gallery(c, T, u):
    cam = Pr.Cam((0.0, 1.7, -1.0), pitch=-2, f=820)
    Hl.gallery(c, cam, T, length=40, width=8, height=7, wall=(130, 8, 20), lights=[Pr.Light((0, 6.5, z), (255, 200, 140), 1.0, 3.0) for z in (3, 9, 15)],
               fog=(8, 0, 2), fog_d=0.07)
    for i, z in enumerate((3.0, 6.5, 10.0, 13.5)):
        for sd in (-1, 1):
            def fig(c_, sx, sy, ppm):
                C.doll(c_, sx, sy, ppm / 720 * 1.3, T, pose="arms_up" if (i + sd) % 2 else "stand", tint=(240, 234, 226), eyes=1.0)
            Hl.vitrine(c, cam, sd * 2.6, z, 1.1, 1.1, 1.6, 0.8, T, content=fig, height=7.0, shatter=1.0)
    rng = K.rng_at(41, 2)
    uu = u if u < 0.4 else (0.8 - u if u < 0.7 else u - 0.6)       # glass bursts out, flies back together in reverse, bursts again
    for k in range(70):                                             # glass bursting outwards in slow motion
        ox, oy = rng.uniform(150, 930), rng.uniform(500, 1300)
        ang = math.atan2(oy - 900, ox - 540)
        sp = rng.uniform(300, 900) * slow(max(0.0, uu), 0, 0.5)
        D.shard(c, ox + math.cos(ang) * sp, oy + math.sin(ang) * sp, rng.uniform(14, 46), u * rng.uniform(-3, 3), T, seed=k,
                tint=(255, 220, 200) if k % 3 else (220, 236, 255))


def _sky_tear(c, T, u):
    D.sky(c, D.SKY_DAY, 0, 960, 0.55)
    D.dunes(c, T, TEAR_FIELD, pal=D.SAND, haze_col=(230, 200, 160), stream=1.6, wind=2.0)
    # a seam opening across the sky, gold at its edges, black inside
    k = K.ease(ramp(u, 0.0, 0.8))
    top = [(x, 420 + 60 * math.sin(x * 0.012 + 1) - 160 * k * math.sin(x / W * math.pi)) for x in np.linspace(-20, W + 20, 30)]
    bot = [(x, 420 + 60 * math.sin(x * 0.012 + 1) + 160 * k * math.sin(x / W * math.pi)) for x in np.linspace(W + 20, -20, 30)]
    c.drawPath(K.path(top + bot), paint((4, 0, 6)))
    c.drawPath(K.path(top, closed=False), paint(C.GOLD_HI, stroke=6))
    c.drawPath(K.path(bot, closed=False), paint(C.GOLD_HI, stroke=6))
    D.eyes_in_dark(c, T, n=40, y0=300, y1=540, seed=8, a=k, size=1.4, col=(255, 80, 60))


TEAR_FIELD = D.dune_field(31, 5, horizon=960, spread=0.7, tall=1.3)


def _curator_rising(c, T, u):
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(shader=K.lin((0, 0), (0, H), [(20, 0, 4), (110, 10, 20), (40, 4, 6)])))
    G.pool(c, 540, 700, 900, (255, 160, 80), 0.35)
    rise = 1 - K.ease(ramp(u, 0.0, 0.6))
    C.curator(c, 540, 1900 + 500 * rise, 1.25, T, eyes=1.0, open_=0.8, hot=1.0, arms="raised", gown=0.0, train=False)


def _doors(c, T, u, t_open):
    D.sky(c, D.SKY_DUSK, 0, 1000, 0.6)
    D.dunes(c, T, TEAR_FIELD, pal=D.SAND_DAWN, haze_col=(255, 150, 120), stream=1.2, wind=2.0)
    k = K.ease(ramp(T, t_open, t_open + 0.25))
    for i, (x, y, s) in enumerate(((540, 1260, 0.62), (240, 1180, 0.4), (840, 1180, 0.4), (110, 1110, 0.26), (970, 1110, 0.26), (380, 1080, 0.22), (700, 1080, 0.22))):
        def inside(c_, r, s=s):
            c_.drawRect(r, paint((10, 0, 4)))
            C.lens(c_, r.centerX(), r.centerY(), r.width() * 0.42, T, open_=0.5 + 0.3 * k, ring=C.GOLD, coat=(150, 30, 40), hot=k)
        D.doorway(c, x, y, s, open_k=0.05 + 0.9 * k, inside=inside, glow_k=0.0, light=1.0)


def s_x_collapse(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0, t1 = cut("x_collapse"), end("x_collapse")
    sx = S("x1")
    tdoor = sx - 0.1
    tface = Wx("x1", "I'm") - 0.1
    if T < t0 + 0.8:
        _shatter_gallery(c, T, T - t0)
    elif T < t0 + 1.55:
        _sky_tear(c, T, T - (t0 + 0.8))
    elif T < tdoor:
        _curator_rising(c, T, T - (t0 + 1.55))
    elif T < tface:
        _doors(c, T, T - tdoor, tdoor + 0.15)
    else:
        u = T - tface
        shake(c, T, 8 + 10 * ramp(T, t1 - 1.0, t1), seed=51)
        import sc_eye as SE
        SE._curator_face(c, T, eyes=1.0, open_=0.85, talk_k=talk(T, "CURATOR"), hot=1.0, z=1.0 + 0.25 * ramp(T, tface, t1))
        rng = K.rng_at(77, 7)
        for k in range(40):
            ox = rng.uniform(-200, W + 200)
            oy = (rng.uniform(0, H) + (T - tface) * rng.uniform(600, 1400)) % (H + 200) - 100
            D.shard(c, ox, oy, rng.uniform(10, 34), T * rng.uniform(-4, 4), T, seed=k + 100)
        c.restore()
    storm = 0.15 + 0.85 * ramp(T, t0 + 0.8, t0 + 1.2)
    if T >= t0 + 1.55 and T < tdoor:
        storm = 0.35
    if T >= tface:
        storm = 0.25 + 0.6 * ramp(T, t1 - 1.2, t1)
    D.sandstorm(st.arr, T, k=storm, col=(220, 150, 70), dark=0.25, seed=3, speed=1.4)
    if T > t1 - 0.25:                                               # the crescendo whites out
        st2 = skia.Surface(st.arr)
        st2.getCanvas().drawPaint(paint(WHITE, ramp(T, t1 - 0.25, t1)))
    return st.arr


# ------------------------------------------------------------------ the twist

DAY_LABELS = ["07:02  PLATE READ", "09:00  CALL SCORED", "11:40  IDLE FLAG", "12:41  BROWSING LOGGED", "18:03  PREGNANCY INFERRED",
              "21:10  FACE MATCHED", "06:00  HOURS CUT", "02:14  FALSE MATCH"]


def _salt_vitrine(c, T, content, label=None, cam_z=-0.6, f=1100, ref=None):
    cam = D.salt_cam(1.55, -2.0, f, z=cam_z)
    D.salt_flat(c, cam, T, sky_cols=((30, 20, 70), (120, 70, 120), (240, 180, 150)), horizon_glow=(250, 200, 170))
    G.pool(c, 540, 900, 700, (255, 190, 150), 0.18)
    for sx_ in (-6.5, 6.5):                                         # two white staircases climbing into the dusk, to nowhere
        D.stairs(c, cam, sx_, 18.0, n=22, rise=0.42, run=0.6, width=2.0, col=(236, 226, 220))
    Hl.vitrine(c, cam, 0.0, 3.0, 1.2, 1.2, 1.7, 0.95, T, content=content, label=label, height=40.0, beam=False, fog=(240, 200, 180), fog_d=0.0, ref=ref)
    return cam


def s_y_vitrine(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("y_vitrine")
    tg = Wx("y1", "real.") + 0.05
    tl = Wx("y1", "Every") - 0.1

    def content(c_, sx, sy, ppm):
        k = K.ease(ramp(T, tg - 0.3, tg + 0.9))
        if k < 1:                                                   # her likeness pouring away as sand
            lp = paint()
            lp.setAlphaf(1 - k)
            c_.saveLayer(None, lp)
            C.doll(c_, sx, sy, ppm / 720 * 1.4, T, pose="stand", tint=(240, 234, 226), hair=(40, 28, 22), dress=(70, 80, 96))
            c_.restore()
            rng = K.rng_at(9, 9)
            for i in range(int(160 * k)):
                px = sx + rng.uniform(-0.25, 0.25) * ppm
                py = sy - rng.uniform(0.2, 1.4) * ppm * (1 - k) - 0 + (T - tg) * rng.uniform(0.2, 0.8) * ppm
                c_.drawCircle(px, min(py, sy), max(1.0, ppm * 0.006), paint((236, 200, 150), 0.8))
        kk = K.ease(ramp(T, tl, tl + 0.5))
        for i, lab in enumerate(DAY_LABELS):                        # what is left: the labels of her day
            y = sy - ppm * 1.55 + i * ppm * 0.18
            a = kk * K.ease(ramp(T, tl + i * 0.06, tl + 0.2 + i * 0.06))
            if a <= 0:
                continue
            w = ppm * 0.95
            Hl.brass(c_, sx - w / 2, y - ppm * 0.07, w, ppm * 0.13, a=a)
            K.text(c_, lab, sx, y + ppm * 0.03, ppm * 0.06, "jost-600", (44, 28, 10), tag="plaque", a=a)
    _salt_vitrine(c, T, content, cam_z=-0.6 + 0.15 * (T - t0))
    return st.arr


def _screen_this(c, r, T, depth=0):
    """The phone's screen: this scene, again - the case on the salt flat, the phone inside it, its screen..."""
    c.save()
    c.translate(r.left(), r.top())
    c.scale(r.width() / W, r.width() / W)
    c.translate(0, (r.height() * W / r.width() - H) / 2)
    _phone_case(c, T, depth + 1, push=0.0)
    c.restore()


def _phone_case(c, T, depth, push=0.0):
    def content(c_, sx, sy, ppm):
        Pp.cushion(c_, sx, sy - ppm * 0.05, ppm / 360 * 1.0)
        ps = ppm / 1060 * 0.95

        def scr(c2, r):
            if depth < 2:
                _screen_this(c2, r, T, depth)
            else:
                c2.drawRect(r, paint((250, 240, 230)))
        CO.phone(c_, sx, sy - ppm * 0.62, ps, T, screen=scr)
        if depth == 0:
            lk = K.ease(ramp(T, Wx("y2", "is") - 0.1, Wx("y2", "is") + 0.5))
            labs = [("CAMERA", (-0.5, -0.9)), ("MICROPHONE", (0.5, -0.78)), ("LOCATION", (-0.52, -0.48)), ("SEARCHES", (0.5, -0.36)), ("PAYMENTS", (-0.5, -0.12))]
            for i, (lab, (dx, dy)) in enumerate(labs):
                a = lk * K.ease(ramp(T, Wx("y2", "is") + i * 0.12, Wx("y2", "is") + 0.2 + i * 0.12)) * max(0.0, 1 - push * 4)
                if a <= 0:
                    continue
                tx, ty = sx + dx * ppm, sy + dy * ppm
                c_.drawLine(tx, ty, sx + dx * ppm * 0.3, sy - ppm * 0.62 + dy * ppm * 0.4, paint(C.GOLD_HI, 0.8 * a, stroke=2))
                Hl.brass(c_, tx - ppm * 0.22, ty - ppm * 0.05, ppm * 0.44, ppm * 0.1, a=a)
                K.text(c_, lab, tx, ty + ppm * 0.025, ppm * 0.05, "jost-600", (44, 28, 10), tag="plaque", a=a)
    _salt_vitrine(c, T, content, label=["EXHIBIT", "YOURS"] if depth == 0 and push < 0.25 else None, cam_z=-0.6 + 2.2 * push, f=1100 + 900 * push)


def s_y_phone(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0, t1 = cut("y_phone"), end("y_phone")
    push = K.ease(ramp(T, Wx("y2", "hand") - 0.2, t1)) * 0.8
    _phone_case(c, T, 0, push=push)
    return st.arr


def s_y_glass(T, idx):
    st = K.Stage((2, 2, 4))
    c = st.c
    t0, t1 = cut("y_glass"), end("y_glass")
    ty = S("y3")
    to = Wx("y3", "You", 1) - 0.1
    tl = E("y3") + 0.02
    # black glass: a faint reflection of a dim room, your silhouette in the middle
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(shader=K.lin((0, 0), (W, H), [(14, 14, 20), (4, 4, 8), (10, 10, 16)])))
    c.drawRect(skia.Rect.MakeLTRB(120, 300, 420, 760), paint((24, 24, 32), 0.6))
    c.drawPath(K.smooth([(160, 1920), (190, 1460), (330, 1300), (430, 1240), (430, 1100), (380, 960), (400, 800), (540, 720), (680, 800),
                         (700, 960), (650, 1100), (650, 1240), (750, 1300), (890, 1460), (920, 1920)]), paint((26, 26, 34)))
    rise = K.ease(ramp(T, ty - 0.4, to))
    lunge = K.ease(ramp(T, tl, tl + 0.12))
    if rise > 0:
        x, y = 760 - 220 * lunge, 1000 - 380 * rise - 100 * lunge
        s = 0.9 + 2.4 * lunge
        lp = paint()
        lp.setAlphaf(min(1.0, 0.25 + 0.75 * rise))
        c.saveLayer(None, lp)
        C.lens_fan(c, x, y - 60 * s, 0.55 * s, T, open_=0.5, a=0.5 + 0.5 * lunge)
        C.mask(c, x, y, 0.75 * s, T, eyes=1.0 if T > to else 0.0, iris="lens", open_=0.7, talk=talk(T, "CURATOR"), tint=(170, 166, 170),
               shadow=(60, 56, 70))
        c.restore()
        if T > to:
            for sd in (-1, 1):
                G.pool(c, x + sd * 62 * 0.75 * s, y - 76 * 0.75 * s, 30 * s, (255, 40, 40), 0.6)
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(shader=K.lin((0, 0), (W * 0.7, H), [(255, 255, 255, 0.07), (255, 255, 255, 0.0), (255, 255, 255, 0.03)])))
    if lunge > 0:
        c.drawPaint(paint(WHITE, 0.6 * (1 - ramp(T, tl + 0.05, tl + 0.3))))
    return st.arr


# ------------------------------------------------------------------ the cold room: the lesson

def s_z_room(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0, t1 = cut("z_room"), end("z_room")
    zoom(c, T, t0, t1 + 2.0, 1.0, 1.12, 540, 1200)
    CO.white_room(c, T, floor_y=1400)
    CO.ring_light(c, 540, 420, 300, T, n=12, tilt=0.42, on=0.6)
    for sd in (-1, 1):
        CO.monitor(c, 540 + sd * 330 - 150, 640, 300, 220, T, arm=(540 + sd * 500, 420),
                   content=lambda c_, r, sd=sd: CO.feeds(c_, r.left(), r.top(), r.right(), r.bottom(), 3, 3, T, seed=7 + sd))
    CO.chair_side(c, 540, 1420, 1.0, T)
    c.restore()
    return st.arr


def s_z_law(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("z_law")
    CO.white_room(c, T, floor_y=1500)

    def law(c_, r):
        x0, y0 = r.left(), r.top()
        K.text(c_, "EU AI ACT  ·  ARTICLE 5", x0 + 50, y0 + 90, 44, "jost-600", (200, 236, 246), align="left", tag="screen")
        K.text(c_, "PROHIBITED SINCE 2 FEB 2025", x0 + 50, y0 + 150, 32, "jost-500", CO.UI_DIM, align="left", tag="screen")
        c_.drawLine(x0 + 50, y0 + 180, r.right() - 50, y0 + 180, paint(CO.GLOW, 0.4, stroke=2))
        rows = [("emotion-reading", "AI that infers emotions", "at work and in schools"), ("face", "untargeted scraping of faces", "to build recognition databases")]
        for i, (w, a1, a2) in enumerate(rows):
            k = K.ease(ramp(T, Wx("z2", w) - 0.2, Wx("z2", w) + 0.2))
            y = y0 + 270 + i * 170
            c_.drawPath(K.rrect(x0 + 50, y - 50, x0 + 230, y - 6, 8), paint(CO.ALERT, 0.9 * k))
            K.text(c_, "BANNED", x0 + 140, y - 16, 30, "jost-600", WHITE, tag="screen", a=k)
            K.text(c_, a1, x0 + 260, y - 16, 38, "jost-500", (230, 240, 246), align="left", tag="screen", a=k)
            K.text(c_, a2, x0 + 260, y + 34, 32, "jost-500", CO.UI_DIM, align="left", tag="screen", a=k)
    CO.monitor(c, 70, 420, 940, 640, T, content=law)
    return st.arr


def s_z_ask(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    CO.white_room(c, T, floor_y=1500)
    qs = [("collected?", "WHAT'S", "COLLECTED?"), ("combine", "WHO CAN", "COMBINE IT?"), ("decides?", "WHO", "DECIDES?")]
    for i, (w, a1, a2) in enumerate(qs):
        k = K.ease(ramp(T, Wx("z3", w) - 0.35, Wx("z3", w) - 0.05))
        y = 300 + i * 330

        def q(c_, r, a1=a1, a2=a2, k=k):
            c_.drawRect(r, paint((10, 24, 30), 1.0))
            K.text(c_, a1, r.centerX(), r.top() + 110, 52, "jost-600", (200, 236, 246), tag="screen", a=0.3 + 0.7 * k)
            K.text(c_, a2, r.centerX(), r.top() + 190, 62, "jost-600", WHITE if k > 0.5 else CO.UI_DIM, tag="screen", a=0.3 + 0.7 * k)
        CO.monitor(c, 170, y, 740, 260, T, content=q, glow_k=0.3 + 0.9 * k)
    return st.arr


def s_z_final(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0, t1 = cut("z_final"), end("z_final")
    u = K.ease(ramp(T, t0, t1 + 0.6))
    z = 1.25 + 0.35 * u
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((12, 16, 24)))
    c.save()
    c.translate(540, 900)
    c.scale(z, z)
    c.translate(-540, -900)
    cols, rows, dx, dy = 5, 7, 230, 300
    for gx in range(-cols, cols + 1):
        for gy in range(-rows, rows + 1):
            x, y = 540 + gx * dx, 900 + gy * dy
            if not (-300 < x < W + 300 and -400 < y < H + 400):
                continue
            empty = gx == 0 and gy == 0
            far = min(1.0, math.hypot(gx / 3.0, gy / 4.0))
            G.pool(c, x, y, 150, (190, 220, 250) if not empty else (255, 226, 180), 0.32 * (1 - 0.5 * far) if not empty else 0.6)
            for k in range(10):                                     # the ring of lenses over each chair, seen from above
                ang = 2 * math.pi * k / 10
                c.drawCircle(x + 104 * math.cos(ang), y + 104 * math.sin(ang), 7, paint((40, 48, 60)))
                c.drawCircle(x + 104 * math.cos(ang), y + 104 * math.sin(ang), 3, G.glow_paint((255, 60, 60) if empty else (140, 220, 255), 0.9))
            c.drawPath(K.rrect(x - 56, y - 122, x + 56, y + 122, 38), paint(shader=K.lin((x - 56, 0), (x + 56, 0), [(90, 100, 116), (170, 180, 196), (80, 90, 106)])))
            c.drawPath(K.rrect(x - 56, y - 122, x + 56, y + 122, 38), paint((40, 46, 58), stroke=3))
            if not empty:                                           # someone lying still in a white gown, hands folded on a glowing phone
                c.drawCircle(x, y - 86, 24, paint((44, 32, 28)))
                c.drawCircle(x, y - 80, 17, paint((214, 180, 160)))
                c.drawPath(K.rrect(x - 40, y - 60, x + 40, y + 108, 26), paint(shader=K.lin((x - 40, 0), (x + 40, 0), [(214, 220, 230), (250, 252, 254), (206, 212, 224)])))
                c.drawPath(K.rrect(x - 13, y - 22, x + 13, y + 22, 5), paint((12, 14, 18)))
                c.drawPath(K.rrect(x - 11, y - 20, x + 11, y + 20, 4), G.glow_paint((150, 210, 255), 0.95))
                c.drawPath(K.capsule(x - 34, y - 40, x - 8, y + 12, 18, 14), paint((236, 240, 246)))
                c.drawPath(K.capsule(x + 34, y - 40, x + 8, y + 12, 18, 14), paint((236, 240, 246)))
                G.pool(c, x, y - 30, 70, (150, 210, 255), 0.4)
            else:
                w = 96
                Hl.brass(c, x - w / 2, y - 18, w, 36)
                K.text(c, "RESERVED", x, y + 7, 15, "cinzel-600", (44, 28, 10), tag="plaque")
    c.restore()
    c.drawPaint(paint(shader=K.rad((540, 900), 1100, [(0, 0, 0, 0.0), (0, 0, 0, 0.0), (0, 0, 0, 0.7)], [0, 0.55, 1])))
    return st.arr

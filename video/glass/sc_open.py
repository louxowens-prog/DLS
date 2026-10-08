"""The hook, the cold open, and the chapter cards.

h_match    - a face in a monitor feed; landmarks light up; brackets close on it in jerks: MATCH FOUND.
h_lamp     - lying in the chair, looking up into a ring of lenses; the guide leans in: "Lie still."
h_machine  - the white room, front on: a monolith with one great lens, the empty chair, the guide at her console.
c_monitors - the room humming: a heart trace, a wall of feeds, the headrest and its cables.
c_sink     - going under: the light above shrinks and wobbles, bubbles rise, the blue deepens to gold.
c_dawn     - a silent desert at dawn: a door standing in the sand, a tiny white figure walking to it; GLASS.
k_1..k_4   - the chapter cards."""
import math

import numpy as np
import skia

import cards as CD
import cast as CA
import cold as CO
import couture as C
import dream as D
import gel as G
import kit as K
import look as LK
from common import E, S, Wx, blink, hit, stutter, talk, zoom
from edit import cut, end
from kit import BLACK, H, W, WHITE, mix, paint, ramp


def _scan(c, a=0.08, step=4):
    for y in range(0, H, step):
        c.drawLine(0, y, W, y, paint(BLACK, a, stroke=1))


def s_h_match(T, idx):
    st = K.Stage((14, 20, 26))
    c = st.c
    t0 = cut("h_match")
    u = T - t0
    z = zoom(c, T, t0, end("h_match"), 1.0, 1.08, 540, 820)
    CA.face(c, 540, 820, 1.75, "nadia", T, L=(214, 230, 246), R=(130, 150, 180), core=0.15, amb=(70, 78, 92), blink=blink(T, 3))
    # landmarks: a constellation the machine draws over the face
    pts = [(-110, -70), (-60, -86), (-14, -70), (14, -70), (60, -86), (110, -70), (-70, -40), (70, -40), (0, 0), (-26, 60), (26, 60), (0, 74),
           (-60, 140), (0, 160), (60, 140), (-150, 20), (150, 20), (-120, 180), (120, 180), (0, 236)]
    k = ramp(u, 0.05, 0.45)
    n = int(len(pts) * k)
    sc = 1.75
    P = [(540 + x * sc, 820 + y * sc) for x, y in pts[:n]]
    for i in range(1, len(P)):
        c.drawLine(*P[i - 1], *P[i], paint((120, 240, 255), 0.35, stroke=1.5))
    for p in P:
        c.drawCircle(p[0], p[1], 5, G.glow_paint((140, 245, 255), 0.9))
    c.restore()
    lock = ramp(stutter(T, t0 + 0.1, period=0.16, move=0.05, fps=12, seed=3), t0 + 0.1, t0 + 0.6)
    CO.target_box(c, 250, 380, 830, 1290, T, label="MATCH FOUND" if T > Wx("h1", "found") - 0.05 else None, conf="98.1%", col=(120, 240, 255),
                  lock=lock, size=40)
    CO.ui_text(c, "FEED 112  ·  SUBJECT 0034", 80, 290, 30, (160, 220, 236))
    CO.ui_text(c, "REC", 840, 290, 30, CO.ALERT, font="jost-600")
    c.drawCircle(820, 280, 9, paint(CO.ALERT, 0.6 + 0.4 * (int(T * 3) % 2)))
    _scan(c)
    if u < 0.12:                                                  # it opens on a flash
        c.drawPaint(paint(WHITE, 1 - u / 0.12))
    return st.arr


def s_h_lamp(T, idx):
    st = K.Stage((200, 208, 216))
    c = st.c
    t0 = cut("h_lamp")
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(shader=K.rad((540, 760), 1100, [(236, 242, 248), (180, 190, 202), (110, 120, 136)])))
    CO.ring_light(c, 540, 740, 380, T, n=14, tilt=0.86, lens_r=46, hot=0.6 * (0.5 + 0.5 * math.sin(T * 6)))
    # the guide leaning in from the right, upside-down-ish over the chair
    CA.face(c, 870, 1260, 1.25, "guide", T, L=(236, 244, 250), R=(150, 166, 190), core=0.15, amb=(90, 98, 112), tilt=-28,
            talk=talk(T, "NAR"), blink=blink(T, 5), gaze=(-0.6, -0.4))
    c.drawPaint(paint(shader=K.rad((540, 760), 1200, [(255, 255, 255, 0.0), (255, 255, 255, 0.0), (20, 30, 40, 0.35)], [0, 0.6, 1])))
    return st.arr


def s_h_machine(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("h_machine")
    zoom(c, T, t0, end("h_machine"), 1.0, 1.06, 540, 900)
    CO.white_room(c, T, floor_y=1390)
    # the machine: a white monolith, one great black lens
    c.drawPath(K.rrect(250, 240, 830, 1300, 24), paint(shader=K.lin((250, 0), (830, 0), [(190, 198, 208), (246, 248, 250), (236, 240, 244), (176, 184, 196)])))
    c.drawPath(K.rrect(250, 240, 830, 1300, 24), paint(CO.STEEL_D, 0.6, stroke=3))
    for j in range(16):                                            # status lights down both sides
        for sd in (-1, 1):
            on = (int(T * 5 + j * 1.7 + sd) % 5) != 0
            c.drawCircle(540 + sd * 250, 320 + j * 58, 6, G.glow_paint((90, 220, 255) if on else (40, 60, 70), 0.9))
    hot = 1.0 if T > Wx("h2", "found") - 0.05 else 0.0
    C.lens(c, 540, 700, 190, T, open_=0.35 + 0.4 * ramp(T, t0, t0 + 1.6), ring=(200, 206, 214), coat=(40, 110, 140), hot=hot)
    G.pool(c, 540, 700, 420, (140, 220, 255), 0.12)
    CO.chair(c, 540, 1560, 0.72, T)
    # the guide at her console, side on, small
    c.drawRect(skia.Rect.MakeLTRB(850, 1150, 1000, 1390), paint((200, 206, 214)))
    CO.monitor(c, 860, 1060, 130, 90, T, content=lambda c_, r: CO.trace(c_, r.left() + 6, r.top() + 20, r.width() - 12, 50, T), glow_k=0.5)
    c.drawPath(K.smooth([(890, 1390), (884, 1150), (900, 1060), (940, 1046), (968, 1080), (972, 1390)]), paint((236, 240, 244)))
    c.drawCircle(930, 1010, 34, paint((232, 204, 186)))
    c.drawCircle(942, 980, 26, paint((70, 50, 40)))
    return st.arr


def s_c_monitors(T, idx):
    st = K.Stage((10, 14, 18))
    c = st.c
    t0 = cut("c_monitors")
    d = (end("c_monitors") - t0) / 3
    k = min(2, int((T - t0) / d))
    if k == 0:
        CO.monitor(c, 60, 520, 960, 700, T, content=lambda c_, r: (CO.trace(c_, r.left() + 30, r.top() + 120, r.width() - 60, 300, T),
                                                                  CO.ui_text(c_, "HR 64", r.left() + 40, r.top() + 80, 60, CO.OK_GREEN, font="jost-600")))
    elif k == 1:
        CO.monitor(c, 60, 420, 960, 900, T, content=lambda c_, r: CO.feeds(c_, r.left(), r.top(), r.right(), r.bottom(), 4, 5, T, seed=4, hl=7))
    else:
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(shader=K.lin((0, 0), (0, H), [(210, 216, 224), (150, 160, 172)])))
        c.drawPath(K.smooth([(220, 1300), (860, 1300), (800, 900), (280, 900)]), paint((240, 244, 248)))
        for i in range(6):
            C.ribbed(c, [(300 + i * 96, 900), (280 + i * 100, 600), (330 + i * 80, 200), (400 + i * 60, -40)], 16, 12, col=(206, 212, 220), T=T,
                     hi=(255, 255, 255), pulse=0.5)
        CO.ring_light(c, 540, 300, 300, T, n=12, tilt=0.4)
    return st.arr


def s_c_sink(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0, t1 = cut("c_sink"), end("c_sink")
    u = ramp(T, t0, t1)
    top = mix((150, 220, 240), (20, 60, 140), u)
    bot = mix((20, 60, 120), (4, 6, 20), u)
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(shader=K.lin((0, 0), (0, H), [top, mix(top, bot, 0.5), bot])))
    # the light we fell from: the ring lamp seen through the surface, shrinking and wobbling away
    r = 420 * (1 - 0.75 * u)
    cy = 420 - 260 * u
    c.save()
    for i in range(3):
        wob = 18 * math.sin(T * 3.1 + i * 2.0) * (1 - u)
        c.drawOval(skia.Rect.MakeLTRB(540 - r + wob, cy - r * 0.5, 540 + r - wob, cy + r * 0.5), G.glow_paint((220, 250, 255), 0.25 * (1 - u * 0.7), blur=10))
    c.restore()
    CO.ring_light(c, 540, cy, r * 0.8, T, n=12, tilt=0.5, a=0.55 * (1 - u))
    for i in range(7):                                             # shafts of light from the surface
        x = 140 + i * 130 + 40 * math.sin(T * 0.7 + i)
        G.beam(c, (540 + (x - 540) * 0.3, cy), (x - 80, H), (x + 80, H), (200, 240, 255), 0.12 * (1 - u))
    rng = K.rng_at(9, 2)
    for i in range(60):                                            # bubbles rising past us
        x = rng.uniform(40, W - 40) + 20 * math.sin(T * 2 + i)
        sp = rng.uniform(300, 900)
        y = (rng.uniform(0, H) - (T - t0) * sp) % (H + 200) - 100
        rr = rng.uniform(4, 22)
        c.drawCircle(x, y, rr, paint((230, 250, 255), 0.5, stroke=2))
        c.drawCircle(x - rr * 0.35, y - rr * 0.35, rr * 0.25, G.glow_paint(WHITE, 0.7))
    # below: a gold glow growing out of the dark
    G.pool(c, 540, H + 200, 1100 * u + 200, (255, 190, 90), 0.45 * u ** 2)
    return st.arr


DAWN_FIELD = D.dune_field(11, 5, horizon=1000, spread=0.6, tall=1.2)


def s_c_dawn(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("c_dawn")
    u = T - t0
    zoom(c, T, t0, end("c_dawn") + 1.0, 1.0, 1.08, 540, 1100)
    D.sky(c, D.SKY_DAWN, 0, 1010, 0.62)
    D.sun(c, 740, 1004, 30)
    LK.flare(740, 1004, 0.45, (255, 200, 150))
    D.dunes(c, T, DAWN_FIELD, pal=D.SAND_DAWN, haze_col=(255, 180, 140), pan=-12 * u, stream=1.0, wind=1.0)
    # a door standing alone on the crest, light pouring from it; a tiny white figure walking to it
    D.doorway(c, 330, 1236, 0.36, open_k=0.55, glow_k=1.0, glow=(255, 244, 220), light=1.0)
    # the guide in her saint's armour, small against the dunes, walking to the door, veils streaming
    sx = 640 - 30 * u
    c.drawPath(K.path([(sx - 30, 1330), (sx + 30, 1330), (sx + 300, 1352), (sx + 280, 1366)]), paint((60, 20, 30), 0.35, blur=3))
    C.saint(c, sx, 1330, 0.2, T, halo=1.0, veil_k=1.0, lamp=1.0, wind=(1.0, -0.1), cape=0.8)
    c.restore()
    CD.title(c, T, t0 + 0.5, a=1.0, y=560)
    return st.arr


def _card(n):
    def f(T, idx):
        st = K.Stage((0, 0, 0))
        CD.chapter(st.c, n, T, cut("k_%d" % n))
        return st.arr
    return f


s_k_1, s_k_2, s_k_3, s_k_4 = _card(1), _card(2), _card(3), _card(4)

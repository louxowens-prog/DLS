"""Chapter 2: paper cut-outs on construction paper, stop-motion on 2s: the 1944 moving shapes, the someone your
brain glues together, the loop, today's AI, the ad."""
import math

import numpy as np
import skia

import common as C
import diy as K
import dot as D
import media as M
import tv
from diy import GOLD, HOT, INK, PURPLE, WHITE, W, H, bez, lin, mix, paint, path, rad, ramp
from common import E, S, Wx

P = M.CONSTRUCTION


def tri_pts(cx, cy, size, rot=0.0, squat=1.0):
    pts = []
    for i in range(3):
        a = math.radians(rot) - math.pi / 2 + i * 2 * math.pi / 3
        pts.append((cx + size * math.cos(a), cy + size * math.sin(a) * squat))
    return pts


def eyes(c, x, y, s, look=(0.0, 0.0), seed=0, angry=0.0, sep=1.0):
    """Paper googly eyes (white circle, black circle), with optional angry brow strips."""
    for k, dx in enumerate((-22 * sep, 22 * sep)):
        M.cut_circle(c, x + dx * s, y, 18 * s, P["white"], seed + k, lift=0.6)
        M.cut_circle(c, x + dx * s + look[0] * 7 * s, y + look[1] * 7 * s, 9 * s, P["black"], seed + 3 + k, lift=0.2, texture=False)
        if angry > 0:
            sx = -1 if dx < 0 else 1
            M.cutout(c, [(x + dx * s - 22 * s, y - 34 * s + sx * 10 * s * angry), (x + dx * s + 22 * s, y - 34 * s - sx * 10 * s * angry),
                         (x + dx * s + 22 * s, y - 24 * s - sx * 10 * s * angry), (x + dx * s - 22 * s, y - 24 * s + sx * 10 * s * angry)],
                     P["black"], seed + 7 + k, lift=0.4, texture=False)


def house(c, x, y, w, h, T, door=0.0, seed=0):
    """The 1944 film's 'house': a rectangle with a hinged door (paper strips, a brass fastener at the hinge)."""
    col = P["black"]
    th = 16
    M.cut_rect(c, x, y, x + w, y + th, col, seed)
    M.cut_rect(c, x, y + h - th, x + w, y + h, col, seed + 1)
    M.cut_rect(c, x, y, x + th, y + h, col, seed + 2)
    M.cut_rect(c, x + w - th, y, x + w, y + h * 0.45, col, seed + 3)
    hx, hy = x + w - th / 2, y + h * 0.45
    a = math.radians(-70 * door)
    L = h * 0.55 - th
    M.cutout(c, [(hx - 8, hy), (hx + 8, hy), (hx + 8 + L * math.sin(-a), hy + L * math.cos(a)), (hx - 8 + L * math.sin(-a), hy + L * math.cos(a))],
             col, seed + 4)
    M.brad(c, hx, hy, 10)


def _hs_positions(t):
    """Big triangle, small triangle, circle: a few seconds of the 1944 chase, in board coordinates."""
    Tb = (700 + 120 * math.sin(t * 1.3), 900 + 60 * math.sin(t * 2.1))
    ts = (300 + 160 * math.cos(t * 1.9), 1150 + 90 * math.sin(t * 1.9))
    tc = (420 + 170 * math.cos(t * 1.9 + 0.8), 1080 + 100 * math.sin(t * 1.9 + 0.8))
    return Tb, ts, tc


def s_p_shapes(T, idx):
    """'In 1944, people watching moving shapes ...' The board: a house, two triangles, a circle."""
    st = K.Stage()
    M.construction_bg(st.arr, P["kraft"])
    c = st.c
    t = M.step(T)
    M.cut_text(c, "CH.2", 200, 380, 90, P["hot"], 2, T=T)
    M.cut_text(c, "THE TRIANGLE", 610, 380, 96, P["purple"], 3, T=T)
    M.cut_text(c, "1944", 540, 560, 150, P["white"], 4, T=T, lift=1.5)
    house(c, 560, 760, 380, 380, T, door=0.5 + 0.5 * math.sin(t * 2), seed=10)
    (bx, by), (sx, sy), (cx, cy) = _hs_positions(t)
    M.cutout(c, tri_pts(bx, by, 130, 10 * math.sin(t * 2)), P["red"], 20, lift=1.6)
    M.cutout(c, tri_pts(sx, sy, 70, 40 * t), P["blue"], 21, lift=1.6)
    M.cut_circle(c, cx, cy, 52, P["yellow"], 22, lift=1.6)
    return st.arr


def s_p_bully(T, idx):
    """'... saw characters. Even a bully.' Eyes go on; the big one gets eyebrows and a name tag."""
    st = K.Stage()
    M.construction_bg(st.arr, P["kraft"])
    c = st.c
    t = M.step(T)
    t_b = Wx("b1", "bully") - 0.25
    chase = ramp(T, t_b, t_b + 1.2)
    house(c, 620, 820, 360, 360, T, door=0.3, seed=10)
    bx, by = 520 - 260 * chase + 10 * math.sin(t * 9) * chase, 820 + 20 * math.sin(t * 5)
    cx, cy = 250 - 60 * chase, 980
    sx, sy = 820, 1080
    M.cutout(c, tri_pts(bx, by, 170, -10 + 8 * math.sin(t * 6) * chase), P["red"], 20, lift=2)
    eyes(c, bx, by - 10, 1.3, look=(-1, 0.2), seed=30, angry=1.0 if T > t_b else 0.0)
    M.cut_circle(c, cx, cy, 70, P["yellow"], 22, lift=2)
    eyes(c, cx, cy - 8, 1.0, look=(1, -0.3) if T > t_b else (0, 0), seed=40)
    M.cutout(c, tri_pts(sx, sy, 90, 20), P["blue"], 21, lift=2)
    eyes(c, sx, sy, 0.8, look=(-1, 0), seed=50, sep=0.9)
    if T > t_b:                                                           # a name tag, pinned on
        k = K.pop(T, t_b, 0.2, 0.4)
        c.save()
        c.translate(bx + 30, by + 170)
        c.rotate(-8)
        c.scale(k, k)
        M.cut_rect(c, -120, -50, 120, 40, P["white"], 60, lift=1)
        K.text(c, "BULLY", 0, 18, 68, "londrina-900", P["red"], tag="label")
        c.restore()
    return st.arr


def bubble(c, x, y, s, text, T, seed=0, tail=(-1, 1)):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    pts = [(-300, -110), (300, -120), (320, 100), (60, 110), (tail[0] * 60, 230 * tail[1]), (-40, 110), (-310, 100)]
    M.cutout(c, pts, P["white"], seed, lift=1.5)
    M.cut_text(c, text, 0, 30, 92, P["black"], seed + 1, T=T, fname="londrina-900", lift=0.3)
    c.restore()


def someone(c, x, y, s, T, k=1.0, seed=0, smile=1.0):
    """The paper someone your brain supplies: a head, hair, eyes, a warm smile, shoulders - glued on in that order
    as k goes 0 -> 1 (the last piece slides in from the right)."""
    parts = 6
    n = k * parts
    def arrive(i):
        u = min(1.0, max(0.0, n - i))
        return K.ease(u), (1 - K.ease(u)) * 700
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    u, off = arrive(0)
    if u > 0:
        M.cutout(c, [(-230 + off, 380), (-200 + off, 250), (-90 + off, 200), (90 + off, 200), (200 + off, 250), (230 + off, 380)],
                 P["sky"], seed, lift=1.5)
    u, off = arrive(1)
    if u > 0:
        M.cut_circle(c, 0 + off, 40, 150, (250, 196, 160), seed + 1, lift=1.5)
    u, off = arrive(2)
    if u > 0:
        M.cutout(c, [(-160 + off, 40), (-150 + off, -80), (-80 + off, -140), (60 + off, -150), (150 + off, -90), (165 + off, 30),
                     (110 + off, -40), (0 + off, -70), (-110 + off, -30)], P["brown"], seed + 2, lift=1.2, smooth_=True)
    u, off = arrive(3)
    if u > 0:
        eyes(c, 0 + off, 40, 1.6, look=(0, 0.1), seed=seed + 5, sep=1.6)
    u, off = arrive(4)
    if u > 0:
        sm = smile
        M.cutout(c, [(-62 + off, 100), (62 + off, 100), (40 + off, 100 + 40 * sm), (0 + off, 112 + 48 * sm), (-40 + off, 100 + 40 * sm)],
                 P["hot"], seed + 7, lift=0.5, smooth_=True)
    u, off = arrive(5)
    if u > 0:
        for sx in (-1, 1):
            M.cut_circle(c, sx * 95 + off, 100, 22, P["pink"], seed + 9 + sx, lift=0.3)
    c.restore()


def s_p_words(T, idx):
    """'Now give it words. It says "I understand,"' A speech bubble pinned to the big triangle."""
    st = K.Stage()
    M.construction_bg(st.arr, P["sky"])
    c = st.c
    t = M.step(T)
    M.cutout(c, tri_pts(540, 1050, 220, 6 * math.sin(t * 3)), P["red"], 20, lift=2)
    eyes(c, 540, 1040, 1.6, look=(0, 0.2), seed=30)
    if T > Wx("b2", "says") - 0.1:
        k = K.pop(T, Wx("b2", "says") - 0.1, 0.2, 0.3)
        c.save()
        c.translate(540, 560)
        c.scale(k, k)
        bubble(c, 0, 0, 1.0, "I UNDERSTAND.", T, seed=70, tail=(0.2, 1))
        c.restore()
    return st.arr


def s_p_someone(T, idx):
    """'... and your brain supplies someone who understands.' A someone is glued together behind the words - by
    Dot's own hand, with a glue stick."""
    st = K.Stage()
    M.construction_bg(st.arr, P["sky"])
    c = st.c
    t0, t1 = Wx("b2", "brain") - 0.25, Wx("b2", "understands") - 0.15
    k = ramp(T, t0, t1)
    someone(c, 540, 820, 1.25, T, k, seed=80)
    bubble(c, 540, 330, 0.7, "I UNDERSTAND.", T, seed=70, tail=(0.1, 0.9))
    hx = 820 + 60 * math.sin(T * 7) + 120 * (1 - k)
    hy = 900 + 40 * math.cos(T * 9)
    C.live_hand(c, T, idx, hx, hy, ang=150, pose="fist", prop=C.glue_stick, enter=(1180, 1450))
    if k >= 1:
        tv.scrawl(c, "SOMEONE", 300, 1270, 70, (255, 240, 120), rot=-6, k=ramp(T, t1, t1 + 0.3))
        tv.scrawl(c, "(assembled by you)", 600, 1340, 52, WHITE, rot=-4, k=ramp(T, t1 + 0.2, t1 + 0.6))
    return st.arr


LOOP = ["IT ACTS LIKE SOMEONE", "YOU TREAT IT LIKE SOMEONE", "IT PLAYS ALONG", "THE SOMEONE GROWS"]


def _loop(c, T, grow, spin, active):
    cx, cy, R = 540, 840, 380
    for i, lab in enumerate(LOOP):
        a0 = -math.pi / 2 + i * math.pi / 2 + spin
        pts = []
        for u in np.linspace(0.12, 0.86, 10):
            a = a0 + u * math.pi / 2
            pts.append((cx + R * math.cos(a), cy + R * math.sin(a)))
        inner = [(cx + (R - 46) * math.cos(a0 + u * math.pi / 2), cy + (R - 46) * math.sin(a0 + u * math.pi / 2)) for u in np.linspace(0.86, 0.12, 10)]
        a_tip = a0 + 0.98 * math.pi / 2
        tip = (cx + (R - 23) * math.cos(a_tip), cy + (R - 23) * math.sin(a_tip))
        ah = [(cx + (R + 30) * math.cos(a0 + 0.86 * math.pi / 2), cy + (R + 30) * math.sin(a0 + 0.86 * math.pi / 2)), tip,
              (cx + (R - 76) * math.cos(a0 + 0.86 * math.pi / 2), cy + (R - 76) * math.sin(a0 + 0.86 * math.pi / 2))]
        col = [P["hot"], P["yellow"], P["acid"], P["orange"]][i]
        M.cutout(c, pts + inner, col, 100 + i, lift=1.6 if i == active else 1.0)
        M.cutout(c, ah, col, 110 + i, lift=1.6 if i == active else 1.0)
    someone(c, cx, cy - 60 * grow, 0.42 + 0.5 * grow, T, 1.0, seed=80, smile=1.0)
    # the four labels, on cards outside the ring
    spots = [(540, 330), (880, 820), (540, 1292), (190, 820)]
    for i, (x, y) in enumerate(spots):
        on = i <= active
        lines = {0: ["IT ACTS", "LIKE SOMEONE"], 1: ["YOU TREAT IT", "LIKE SOMEONE"], 2: ["IT PLAYS", "ALONG"], 3: ["THE SOMEONE", "GROWS"]}[i]
        c.save()
        c.translate(x, y)
        c.rotate([-3, 4, 2, -5][i])
        a = 1.0 if on else 0.0
        if a > 0:
            M.cut_rect(c, -170, -62, 170, 72, P["white"], 120 + i, lift=1.2)
            K.text(c, lines[0], 0, -6, 44, "londrina-900", P["black"], tag="label")
            K.text(c, lines[1], 0, 46, 44, "londrina-900", P["black"], tag="label")
        c.restore()


def s_p_loop(T, idx):
    """'Then it loops: it acts like someone, you treat it like someone ...'"""
    st = K.Stage()
    M.construction_bg(st.arr, P["purple"])
    c = st.c
    active = 0 if T < Wx("b3", "treat") - 0.1 else 1
    _loop(c, T, 0.0, M.step(T) * 0.6, active)
    return st.arr


def s_p_loop2(T, idx):
    """'... it plays along, and the someone grows.' The ring spins faster, the someone swells."""
    st = K.Stage()
    M.construction_bg(st.arr, P["purple"])
    c = st.c
    t0 = Wx("b3", "plays") - 0.1
    active = 2 if T < Wx("b3", "someone", 2) - 0.1 else 3
    grow = ramp(T, Wx("b3", "grows") - 0.3, Wx("b3", "grows") + 0.6)
    grow = math.floor(grow * 6) / 6                                      # it swells in stop-motion steps
    _loop(c, T, grow, M.step(T) * (0.6 + 2.5 * ramp(T, t0, E("b3"))), active)
    return st.arr


def server(c, x, y, w, h, T, seed=0):
    """Today's AI as a paper tower of racks, blinking with paper-dot lights."""
    M.cut_rect(c, x - w / 2, y - h, x + w / 2, y, P["black"], seed, lift=2)
    rows = int(h / 70)
    for r_ in range(rows):
        yy = y - h + 20 + r_ * 70
        M.cut_rect(c, x - w / 2 + 20, yy, x + w / 2 - 20, yy + 50, P["grey"], seed + 1 + r_, lift=0.6)
        for k in range(4):
            on = (int(M.step(T) * 12) + r_ * 3 + k * 5 + seed) % 7 < 3
            c.drawCircle(x - w / 2 + 50 + k * 30, yy + 25, 8, paint(P["acid"] if on else (60, 80, 60)))


def s_p_capable(T, idx):
    """'Today's AI is far more capable than ELIZA.' A tiny ELIZA box at the foot of a tower that leaves the frame."""
    st = K.Stage()
    M.construction_bg(st.arr, P["acid"])
    c = st.c
    rise = K.ease(ramp(T, S("b4") - 0.1, Wx("b4", "capable") + 0.2))
    server(c, 640, 1300, 420, 200 + 1600 * rise, T, seed=200)
    M.cut_rect(c, 160, 1180, 300, 1300, P["cream"], 230, lift=1)
    K.text(c, "ELIZA", 230, 1256, 40, "londrina-900", P["black"], tag="label")
    if T > S("b4"):
        c.save()
        c.translate(250, 640)
        c.rotate(-6)
        M.cut_rect(c, -190, -80, 190, 80, P["white"], 241, lift=1.5)
        K.text(c, "TODAY'S AI", 0, 26, 76, "londrina-900", P["purple"], tag="sign")
        c.restore()
        M.cutout(c, [(400, 640), (420, 615), (440, 640), (425, 640), (425, 700), (415, 700), (415, 640)], P["black"], 242, lift=0.5)
    with M.crayon_layer(c):
        M.kid_text(c, "1966", 230, 1110, 60, (60, 60, 60), T, 4, rot=-6)
    return st.arr


def s_p_coauthor(T, idx):
    """'But the someone you feel? You're co-authoring it.' A paper book; Dot's hand writes '& YOU' on the byline."""
    st = K.Stage()
    M.construction_bg(st.arr, P["cream"])
    c = st.c
    c.save()
    c.translate(540, 820)
    c.rotate(-3)
    M.cut_rect(c, -360, -480, 360, 480, P["hot"], 300, lift=2.5)
    M.cut_rect(c, -360, -480, -320, 480, mix(P["hot"], INK, 0.3), 301, lift=0.3)
    someone(c, 20, -120, 0.75, T, 1.0, seed=80)
    M.cut_text(c, "THE SOMEONE", 20, 200, 92, P["yellow"], 310, T=T)
    K.text(c, "by AI", -40, 320, 64, "permanent-marker-400", WHITE, tag="byline")
    tw = ramp(T, Wx("b4", "You're") - 0.15, Wx("b4", "co-authoring") + 0.25)
    if tw > 0:
        tv.scrawl(c, "& YOU", 150, 324, 72, (255, 240, 120), rot=-6, k=tw, tag="byline2")
    c.restore()
    if tw > 0:
        t_done = Wx("b4", "co-authoring") + 0.25                               # written: the hand gets out of the way
        away = K.ease(ramp(T, t_done, t_done + 0.3))
        hx, hy = 540 + 150 * math.cos(math.radians(-3)) - 20 + 120 * tw + 380 * away, 820 + 324 + 10 + 6 * math.sin(T * 20) * (1 - away) + 560 * away
        C.live_hand(c, T, idx, hx + 20, hy - 30, ang=140, pose="fist", prop=lambda L, x, y, a: C.marker(L, x, y, a, (255, 210, 40)),
                    enter=(1180, 1700))
    return st.arr


def s_p_ad(T, idx):
    """'Apps don't mention that. Natural is what sells.' A paper billboard for an app, with fine print. Dot shrugs."""
    st = K.Stage()
    M.construction_bg(st.arr, P["hot"])
    c = st.c
    c.save()
    c.translate(470, 650)
    c.rotate(2)
    c.scale(0.9, 0.9)
    M.cut_rect(c, -440, -420, 440, 360, P["white"], 400, lift=2.5)
    M.cut_text(c, "SO NATURAL!", 0, -280, 120, P["purple"], 401, T=T)
    M.cut_rect(c, -150, -200, 150, 260, P["black"], 402, lift=1)                    # a phone
    M.cut_rect(c, -130, -170, 130, 230, P["sky"], 403, lift=0.3)
    M.cutout(c, [(-110, -130), (110, -130), (110, -10), (-40, -10), (-80, 30), (-80, -10), (-110, -10)], P["white"], 404, lift=0.5)
    K.text(c, "I totally", 0, -84, 42, "londrina-900", P["black"], tag="sign")
    K.text(c, "get you!", 0, -38, 42, "londrina-900", P["black"], tag="sign")
    for i, (x, y) in enumerate(((-330, -60), (330, -40), (-300, 180), (320, 200))):
        star = [(x + 60 * (1 if j % 2 == 0 else 0.45) * math.cos(-math.pi / 2 + j * math.pi / 5),
                 y + 60 * (1 if j % 2 == 0 else 0.45) * math.sin(-math.pi / 2 + j * math.pi / 5)) for j in range(10)]
        M.cutout(c, star, P["yellow"], 410 + i, lift=1)
    fine = ramp(T, Wx("b5", "Natural") - 0.2, Wx("b5", "Natural") + 0.3)
    K.text(c, "*the someone is partly you", 0, 320, 34 if fine <= 0 else 34 + 18 * fine, "jost-600", (90, 90, 100), tag="fine")
    c.restore()
    C.live_dot(c, T, idx, 880, 2330, 0.82, pose="shrug", mood="flat" if T < Wx("b5", "Natural") else "side", look=(-0.6, -0.2), seed=1,
               sock_look=(-0.5, -0.8))
    return st.arr

"""Chapter 3: stop-motion clay on a felt cyc (on 2s, boiling): the layer cake of an assistant's personality, the
cupcake that beat a cake a hundred times bigger, a smile pressed in by thumbs - Dot's."""
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

LAYERS = [((236, 200, 140), "PRETRAINING"), ((255, 120, 176), "POST-TRAINING"), ((110, 190, 255), "SYSTEM PROMPT")]
FROST = (255, 250, 240)


def cyc(c, color=(120, 50, 170), floor=(250, 200, 120), horizon=1240):
    """A felt backdrop sweeping down into a table top, lit from the left."""
    c.drawRect(skia.Rect.MakeWH(W, horizon + 60), paint(shader=lin((0, 0), (0, horizon), [mix(color, WHITE, 0.15), color, mix(color, INK, 0.3)])))
    c.drawRect(skia.Rect.MakeLTRB(0, horizon, W, H), paint(shader=lin((0, horizon), (0, H), [floor, mix(floor, INK, 0.35)])))
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=rad((260, 500), 1300, [(255, 255, 230, 0.22), (0, 0, 0, 0), (0, 0, 0, 0.35)], [0, 0.55, 1])))
    rng = np.random.default_rng(3)
    for _ in range(900):                                                   # felt fuzz
        x, y = rng.uniform(0, W), rng.uniform(0, horizon)
        c.drawLine(x, y, x + rng.uniform(-4, 4), y + rng.uniform(-4, 4), paint(WHITE if rng.random() < 0.5 else INK, 0.06, stroke=1.2))


def layer(c, cx, ybot, w, h, color, t, seed, frost_top=True, top_ell=False):
    """One clay cake layer (front view, a little from above): a lumpy drum with a wavy frosting seam."""
    pts = [(cx - w / 2, ybot - h), (cx + w / 2, ybot - h), (cx + w / 2, ybot - 8), (cx + w * 0.3, ybot + 6), (cx, ybot + 10),
           (cx - w * 0.3, ybot + 6), (cx - w / 2, ybot - 8)]
    K.clay_poly(c, pts, color, t, seed, amp=4.0, prints=1, marks=1)
    if top_ell:
        K.clay_ellipse(c, cx, ybot - h, w / 2, 34, mix(color, WHITE, 0.25), t, seed + 1, amp=0.04, prints=1, marks=0)
    if frost_top:
        wav = []
        for i in range(17):
            u = i / 16
            wav.append((cx - w / 2 + w * u, ybot - h + 10 + (14 if i % 2 else -4)))
        wav += [(cx + w / 2, ybot - h - 16), (cx - w / 2, ybot - h - 16)]
        K.clay_poly(c, wav, FROST, t, seed + 2, amp=2.0, prints=0, marks=0, gloss=0.35)


def flag(c, x, y, text, t, seed=0, color=(255, 236, 90), lean=-6, size=38, side=1, pole=170):
    """A paper flag on a toothpick, stuck into the clay (side = -1: the flag flies to the left)."""
    bx, by, br = K.boil(t, 1.5, seed)
    c.save()
    c.translate(x + bx, y + by)
    c.rotate(lean + br)
    c.drawLine(0, 0, 0, -pole, paint((210, 170, 110), stroke=7))
    f = K.font("rubik-900", size)
    w = f.measureText(text) + 36
    x0 = 0 if side > 0 else -w
    top = -pole - 10
    c.drawRect(skia.Rect.MakeXYWH(x0 + 4, top + 4, w, size + 30), paint(INK, 0.3, blur=4))
    c.drawRect(skia.Rect.MakeXYWH(x0, top, w, size + 30), paint(color))
    K.text(c, text, x0 + w / 2, top + size + 4, size, "rubik-900", (40, 30, 60), tag="flag")
    c.restore()


def layer_flag(c, layer_mid, x, text, t, seed, color=(255, 236, 90), side=-1, size=32):
    """A short flag whose paper hangs right beside the middle of its own layer."""
    flag(c, x, layer_mid + 20, text, t, seed, color, lean=-4 * side, size=size, side=side, pole=40)


def clay_sock(c, x, y, s, t, seed=0, open_=0.0):
    """Doc in clay, on a clay hand (the cake topper)."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    K.clay_poly(c, [(-60, 120), (60, 120), (70, -40), (110, -90), (90, -150), (0, -170), (-70, -120), (-70, 0)], (250, 248, 236), t, seed,
                amp=3.0, prints=1, marks=1)
    for i, col in enumerate((HOT, (40, 110, 255), GOLD)):
        K.clay_poly(c, [(-62, 60 + i * 22), (62, 60 + i * 22), (62, 76 + i * 22), (-62, 76 + i * 22)], col, t, seed + 3 + i, amp=1.5, prints=0,
                    marks=0)
    K.clay_ellipse(c, 40, -60, 50, 16 + 30 * open_, (210, 30, 50), t, seed + 7, amp=0.05, prints=0, marks=0)
    K.clay_eye(c, -10, -110, 26, t, look=(0.5, 0.1), seed=seed + 8)
    K.clay_eye(c, 46, -104, 22, t, look=(0.5, 0.1), seed=seed + 9)
    for k in range(5):
        K.clay_ellipse(c, -40 + k * 14, -176 - (k % 2) * 10, 14, 26, (255, 140, 30), t, seed + 10 + k, rot=-20 + k * 10, amp=0.06, prints=0, marks=0)
    K.clay_ellipse(c, -50, -150, 26, 26, (200, 205, 215), t, seed + 16, amp=0.03, prints=0, marks=0, gloss=0.6)
    c.restore()


def cake(c, cx, ybot, w, t, n=3, topper=0.0, seed=0, hpx=150, drop=None):
    """The personality cake: n layers, then (topper 0..1) Doc on top. drop = (layer index, 0..1) falls in."""
    y = ybot
    for i in range(n):
        col, lab = LAYERS[i]
        dy = 0.0
        if drop and drop[0] == i:
            k = drop[1]
            dy = -700 * (1 - k) ** 2 if k < 1 else 0.0
        layer(c, cx, y + dy, w - i * 30, hpx, col, t, seed + i * 10, top_ell=(i == n - 1))
        y -= hpx
    if topper > 0:
        k = topper
        dy = -600 * (1 - k) ** 2 if k < 1 else 0.0
        sq = 1.0 + (0.12 * math.sin(min(1, (k - 0.85) / 0.15) * math.pi) if k > 0.85 else 0)
        c.save()
        c.translate(cx, y + 10 + dy)
        c.scale(sq, 1 / sq)
        clay_sock(c, 0, -120, 0.95, t, seed + 50)
        c.restore()
    return y


def s_k_cake(T, idx):
    """'So whose personality is it? Layers.' A frosted cake; Dot cuts it and the slice slides out."""
    st = K.Stage()
    c = st.c
    t = M.step(T)
    cyc(c)
    K.clay_poly(c, [(110, 250), (970, 240), (980, 530), (100, 540)], (255, 240, 205), t, 2, amp=5.0, prints=1, marks=1)
    K.clay_text(c, "CH.3", 540, 345, 80, (120, 40, 190), t, 3)
    K.clay_text(c, "THE LAYER CAKE", 540, 470, 104, (225, 30, 120), t, 4, max_w=840)
    K.clay_shadow(c, 470, 1250, 330, 46, 0.45)
    K.clay_ellipse(c, 470, 1230, 340, 60, (230, 230, 240), t, 5, amp=0.03, prints=0, marks=1, gloss=0.5)            # the plate
    cut = ramp(T, Wx("c1", "Layers") - 0.1, Wx("c1", "Layers") + 0.5)
    cut = math.floor(cut * 6) / 6
    # the whole cake, frosted white; once cut, its right third slides away to show the layers inside
    K.clay_poly(c, [(220, 760), (720, 760), (720, 1215), (470, 1240), (220, 1215)], FROST, t, 6, amp=5.0)
    K.clay_ellipse(c, 470, 760, 250, 50, mix(FROST, WHITE, 0.4), t, 7, amp=0.04, prints=1, marks=0)
    for k in range(6):
        K.clay_ellipse(c, 260 + k * 84, 790, 22, 30, (255, 120, 190) if k % 2 else (120, 200, 255), t, 8 + k, amp=0.1, prints=0, marks=0)
    if cut > 0:
        gx = 560 + 170 * cut
        K.clay_poly(c, [(560, 770), (gx + 10, 770), (gx + 10, 1230), (560, 1230)], (180, 120, 70), t, 20, amp=1.0, prints=0, marks=0)
        y = 1220
        for i, (col, lab) in enumerate(LAYERS + [((255, 236, 120), "")]):
            K.clay_poly(c, [(565, y - 105), (gx + 5, y - 105), (gx + 5, y), (565, y)], col, t, 21 + i, amp=2.0, prints=0, marks=1)
            y -= 112
        K.clay_poly(c, [(gx, 770), (gx + 170, 760), (gx + 170, 1215), (gx, 1235)], FROST, t, 30, amp=4.0)
    C.live_dot(c, T, idx, 905, 2290, 0.72, pose="hold", mood="deadpan" if cut <= 0 else "proud", look=(-0.6, 0.2), seed=1,
               prop=_knife, sock_look=(-0.8, 0.3), sock_face=-1)
    return st.arr


def _knife(c, x, y, ang):
    c.save()
    c.translate(x, y)
    c.rotate(ang + 90)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-14, -20, 28, 110), 8, 8), paint((30, 30, 36)))
    c.drawPath(path([(-14, -20), (14, -20), (24, -300), (-6, -330), (-14, -300)]), paint(shader=lin((-14, 0), (24, 0), [(240, 242, 250), (150, 156, 170)])))
    c.restore()


def s_k_layers(T, idx):
    """'A giant pile of internet text. People rewarding the answers they like.' Layers drop in, flagged."""
    st = K.Stage()
    c = st.c
    t = M.step(T)
    cyc(c, (60, 40, 140))
    K.clay_shadow(c, 540, 1300, 420, 50, 0.45)
    K.clay_ellipse(c, 540, 1285, 430, 64, (230, 230, 240), t, 5, amp=0.03, prints=0, marks=1, gloss=0.5)
    t2 = Wx("c2", "People") - 0.15
    n = 1 if T < t2 else 2
    drop = (n - 1, ramp(T, (S("c2") - 0.1) if n == 1 else t2, ((S("c2") - 0.1) if n == 1 else t2) + 0.45))
    drop = (drop[0], math.floor(drop[1] * 8) / 8)
    cake(c, 540, 1270, 640, t, n=n, seed=40, hpx=170, drop=drop)
    # the bottom layer is studded with clay letters (the internet's text)
    rng = np.random.default_rng(5)
    for i, ch in enumerate("A?#@w!e&"):
        K.clay_text(c, ch, 350 + i * 64, 1200 - (i % 2) * 60, 50, [(255, 255, 255), (60, 60, 70), (255, 80, 160)][i % 3], t, 60 + i, wobble=1.0)
    layer_flag(c, 1185, 300, "PRETRAINING", t, 1)
    if n >= 2 and drop[1] >= 1:
        layer_flag(c, 1015, 320, "POST-TRAINING", t, 2, (140, 255, 200), size=30)
        for k in range(3):                                                  # little clay thumbs
            x = 470 + k * 90
            K.clay_ellipse(c, x, 1010, 22, 30, (255, 210, 170), t, 70 + k, amp=0.08, prints=0, marks=0)
            K.clay_ellipse(c, x + 4, 975, 10, 22, (255, 210, 170), t, 73 + k, amp=0.08, prints=0, marks=0)
    return st.arr


def s_k_layers2(T, idx):
    """'The company's instructions. And on top, you.' A sticky-note layer, then Doc plops on top."""
    st = K.Stage()
    c = st.c
    t = M.step(T)
    cyc(c, (60, 40, 140))
    K.clay_shadow(c, 540, 1300, 420, 50, 0.45)
    K.clay_ellipse(c, 540, 1285, 430, 64, (230, 230, 240), t, 5, amp=0.03, prints=0, marks=1, gloss=0.5)
    t3 = Wx("c2", "company") - 0.15
    tt = Wx("c2", "top") - 0.3
    k3 = math.floor(ramp(T, t3, t3 + 0.45) * 8) / 8
    top = math.floor(ramp(T, tt, tt + 0.5) * 8) / 8
    ytop = cake(c, 540, 1270, 560, t, n=3, seed=40, hpx=140, drop=(2, k3), topper=top)
    if k3 >= 1:
        K.clay_poly(c, [(540, 872), (700, 864), (704, 962), (546, 968)], (255, 236, 90), t, 90, amp=2.0, prints=1, marks=0)   # sticky note
        K.text(c, "BE NICE :)", 622, 926, 34, "permanent-marker-400", (40, 40, 60), tag="note")
        layer_flag(c, 920, 345, "SYSTEM PROMPT", t, 3, (120, 200, 255))
    layer_flag(c, 1200, 330, "PRETRAINING", t, 1)
    layer_flag(c, 1060, 330, "POST-TRAINING", t, 2, (140, 255, 200), size=30)
    if top >= 1:
        flag(c, 690, ytop - 30, "YOU", t, 4, (255, 120, 190), lean=12, size=56)
    return st.arr


def person(c, x, y, s, t, color, seed=0, sign=None, arm=0.0):
    """A little clay person (a feedback giver) with an optional sign."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    K.clay_shadow(c, 0, 4, 50, 12, 0.35)
    K.clay_ellipse(c, 0, -60, 46, 64, color, t, seed, amp=0.08, prints=1, marks=0)
    K.clay_ellipse(c, 0, -160, 40, 40, (255, 205, 165), t, seed + 1, amp=0.06, prints=0, marks=0)
    K.clay_eye(c, -14, -166, 9, t, seed=seed + 2)
    K.clay_eye(c, 14, -166, 9, t, seed=seed + 3)
    if sign:
        c.drawLine(40, -80, 60 + arm * 10, -260, paint((200, 160, 100), stroke=6))
        c.drawRect(skia.Rect.MakeXYWH(10 + arm * 10, -330, 110, 70), paint(WHITE))
        c.drawRect(skia.Rect.MakeXYWH(10 + arm * 10, -330, 110, 70), paint((60, 60, 70), stroke=3))
        K.text(c, sign, 65 + arm * 10, -282, 36, "rubik-900", (220, 30, 60) if sign == "NO" else (30, 150, 70), tag="deco")
    c.restore()


GIANT = [(250, 170, 200), (200, 160, 255), (250, 210, 150)]


def _giant(c, t, sag=0.0, x=760, ybot=1190):
    y = ybot
    for i in range(6):
        lean_ = sag * (i ** 1.5) * 12
        layer(c, x + lean_, y + sag * i * 10, 400 - i * 20, 118 - sag * 14, GIANT[i % 3], t, 100 + i * 7, top_ell=(i == 5))
        y -= 118 - sag * 14
    return y


def _cupcake(c, t, x=290, ybot=1190):
    K.clay_poly(c, [(x - 70, ybot), (x + 70, ybot), (x + 90, ybot - 100), (x - 90, ybot - 100)], (255, 140, 190), t, 120, amp=3.0)
    K.clay_ellipse(c, x, ybot - 130, 100, 56, FROST, t, 121, amp=0.1, gloss=0.4)
    K.clay_ellipse(c, x, ybot - 190, 22, 22, (230, 30, 50), t, 122, amp=0.05, gloss=0.6)


def s_k_giant(T, idx):
    """'In 2022, OpenAI tuned a model with human feedback, ...' A cupcake, a cake a hundred times bigger, and little
    clay people holding up YES and NO."""
    st = K.Stage()
    c = st.c
    t = M.step(T)
    cyc(c, (40, 90, 160), floor=(240, 190, 120), horizon=1180)
    K.clay_text(c, "2022", 540, 370, 130, (255, 226, 90), t, 3)
    top = _giant(c, t)
    flag(c, 600, 760, "175B", t, 5, lean=-10, size=52, side=-1)
    _cupcake(c, t)
    flag(c, 230, 1020, "1.3B", t, 6, (140, 255, 200), lean=-12, size=52, side=-1)
    signs = ["YES", "NO", "YES"]
    for k in range(3):
        person(c, 170 + k * 125, 1345, 0.62, t, [(80, 200, 120), (255, 160, 60), (120, 160, 255)][k], 130 + k * 5,
               sign=signs[(k + int(t * 2)) % 3], arm=math.sin(t * 6 + k))
    return st.arr


def s_k_vote(T, idx):
    """'... and people preferred it to one a hundred times bigger.' A blue ribbon for the cupcake; the giant sags."""
    st = K.Stage()
    c = st.c
    t = M.step(T)
    cyc(c, (40, 90, 160), floor=(240, 190, 120), horizon=1180)
    sag = math.floor(ramp(T, Wx("c3", "bigger") - 0.4, Wx("c3", "bigger") + 0.4) * 6) / 6
    _giant(c, t, sag)
    _cupcake(c, t)
    rb = K.pop(T, Wx("c3", "preferred") - 0.1, 0.25, 0.3)
    if rb > 0:                                                              # a blue ribbon rosette
        c.save()
        c.translate(400, 1000)
        c.scale(rb, rb)
        for k in range(12):
            a = k * math.pi / 6
            K.clay_ellipse(c, 40 * math.cos(a), 40 * math.sin(a), 26, 14, (40, 110, 255), t, 140 + k, rot=math.degrees(a), amp=0.05,
                           prints=0, marks=0)
        K.clay_ellipse(c, 0, 0, 34, 34, GOLD, t, 160, amp=0.04, prints=0, marks=0, gloss=0.5)
        c.restore()
    for k in range(4):
        person(c, 130 + k * 110, 1345, 0.62, t, [(80, 200, 120), (255, 160, 60), (120, 160, 255), (255, 120, 190)][k], 130 + k * 5,
               sign="YES", arm=math.sin(t * 8 + k))
    C.fact_card(c, T, Wx("c3", "preferred") - 0.05, "InstructGPT, 2022", "People preferred its answers to GPT-3's, a model 100x bigger.",
                y=290, w=920)
    return st.arr


def face_ball(c, x, y, r, t, smile=0.0, seed=0, script_x=0.0):
    K.clay_ellipse(c, x, y, r, r * 0.92, (255, 200, 120), t, seed, amp=0.05, prints=3, marks=1)
    K.clay_eye(c, x - r * 0.35, y - r * 0.2, r * 0.16, t, seed=seed + 1)
    K.clay_eye(c, x + r * 0.35, y - r * 0.2, r * 0.16, t, seed=seed + 2)
    mw = r * 0.5
    pts = [(x - mw, y + r * 0.3 - smile * r * 0.18), (x - mw * 0.5, y + r * 0.3 + smile * r * 0.1), (x, y + r * 0.32 + smile * r * 0.16),
           (x + mw * 0.5, y + r * 0.3 + smile * r * 0.1), (x + mw, y + r * 0.3 - smile * r * 0.18),
           (x + mw * 0.5, y + r * 0.36 + smile * r * 0.18), (x, y + r * 0.4 + smile * r * 0.26), (x - mw * 0.5, y + r * 0.36 + smile * r * 0.18)]
    K.clay_poly(c, pts, (200, 40, 70), t, seed + 3, amp=1.5, prints=0, marks=0)


def thumb(c, x, y, ang, t, seed=0):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    K.clay_poly(c, [(-50, 0), (50, 0), (56, 260), (-56, 260)], (240, 185, 150), t, seed, amp=3, prints=2, marks=1)
    K.clay_ellipse(c, 0, 0, 52, 60, (240, 185, 150), t, seed + 1, amp=0.05, prints=2, marks=0)
    K.clay_ellipse(c, 0, -10, 34, 30, (255, 120, 170), t, seed + 2, amp=0.03, prints=0, marks=0, gloss=0.5)
    c.restore()


def s_k_shape(T, idx):
    """'The politeness, the cheerful tone? Not scripted. Shaped.' Two big thumbs press a smile into a ball of clay."""
    st = K.Stage()
    c = st.c
    t = M.step(T)
    cyc(c, (150, 40, 120), floor=(255, 210, 140))
    press = math.floor(ramp(T, Wx("c4", "Shaped") - 0.35, Wx("c4", "Shaped") + 0.3) * 6) / 6
    K.clay_shadow(c, 540, 1180, 300, 50, 0.45)
    face_ball(c, 540, 860, 300, t, smile=-0.4 + 1.4 * press, seed=200)
    for sx in (-1, 1):
        thumb(c, 540 + sx * (330 - 150 * press), 1060 - 40 * press, sx * (40 - 15 * press), t, 210 + (sx > 0))
    TAGS = [("POLITE", 290, 700, -30, -1, "politeness"), ("CHEERFUL", 280, 830, -48, -1, "cheerful"),
            ("CAUTIOUS", 780, 650, 28, 1, "cheerful"), ("WORDY", 800, 830, 48, 1, "tone"), ("SAYS NO NICELY", 430, 600, -12, -1, "tone")]
    for i, (lab, x, y, lean, side, word) in enumerate(TAGS):
        t_on = Wx("c4", word) - 0.15 + (0.25 if i in (2, 4) else 0.0)
        if T > t_on:
            flag(c, x, y, lab, t, 30 + i, [(255, 236, 90), (140, 255, 200), (120, 200, 255), (255, 170, 210), (255, 255, 255)][i],
                 lean=lean, size=34, side=side)
    if T > Wx("c4", "scripted") - 0.15:                                    # a script, crossed out
        k = K.pop(T, Wx("c4", "scripted") - 0.15, 0.2, 0.3)
        c.save()
        c.translate(820, 330)
        c.rotate(8)
        c.scale(k, k)
        c.drawRect(skia.Rect.MakeXYWH(-120, -150, 240, 300), paint(WHITE))
        K.text(c, "SCRIPT", 0, -96, 44, "special-elite-400", (40, 40, 40), tag="deco")
        for i in range(6):
            c.drawLine(-90, -50 + i * 34, 90 - (i % 3) * 30, -50 + i * 34, paint((120, 120, 120), stroke=4))
        c.drawLine(-140, -170, 140, 170, paint((230, 30, 50), stroke=18))
        c.drawLine(140, -170, -140, 170, paint((230, 30, 50), stroke=18))
        c.restore()
    return st.arr


def s_k_rater(T, idx):
    """'By people like me.' The thumbs were Dot's: headset on, AI RATER badge, the clay smile in her hand."""
    st = K.Stage()
    c = st.c
    t = M.step(T)
    cyc(c, (150, 40, 120), floor=(255, 210, 140))
    pts = C.live_dot(c, T, idx, 540, 2420, 1.2, pose="palm", mood="smile", look=(0.1, 0.1), seed=1, headset=True, badge="AI RATER",
                     sock_look=(0.8, -0.3))
    hx, hy = pts["hand"]
    face_ball(c, hx + 10, hy - 120, 110, t, smile=1.0, seed=200)
    return st.arr

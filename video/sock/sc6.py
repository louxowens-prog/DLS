"""Chapter 6: CHANNEL 99, public-access VHS: colour bars, a basement stage (wood panelling, Christmas lights, a
bedsheet curtain, a cardboard sign), the troupe, Dot at the mic; the laugh track drops out; the sock comes off;
then one last joke. And the end card."""
import math

import numpy as np
import skia

import common as C
import diy as K
import dot as D
import media as M
import media2 as F
import sc1
import troupe as TR
import tv
from diy import GOLD, HOT, INK, PURPLE, WHITE, W, H, bez, lin, mix, paint, path, rad, ramp
from common import E, S, Wx


def basement(c, T, lights=1.0, spot=0.0):
    """The stage: panelling, a hot-pink bedsheet curtain, Christmas lights, a CD disco ball, a plywood riser."""
    for k in range(10):
        c.drawRect(skia.Rect.MakeXYWH(k * 110, 0, 108, H), paint(mix((120, 82, 50), (96, 64, 38), (k % 3) / 3)))
        c.drawLine(k * 110 + 108, 0, k * 110 + 108, H, paint((60, 38, 22), stroke=4))
    cur = path([(90, 360), (990, 350), (1010, 1180), (70, 1190)])
    c.drawPath(cur, paint((255, 70, 170)))
    c.save()
    c.clipPath(cur, doAntiAlias=True)
    for k in range(12):
        x = 90 + k * 80
        c.drawLine(x, 350, x + 20 * math.sin(k), 1190, paint((190, 30, 120), 0.6, stroke=26, blur=14))
        c.drawLine(x + 30, 350, x + 30 + 10 * math.sin(k), 1190, paint((255, 150, 210), 0.35, stroke=12, blur=8))
    c.restore()
    # Christmas lights on a sagging wire
    pts = [(40 + i * 50, 300 + 40 * math.sin(i / 20 * math.pi)) for i in range(21)]
    c.drawPath(path(pts, closed=False), paint((30, 60, 30), stroke=4))
    for i, (x, y) in enumerate(pts):
        col = [(255, 40, 60), (40, 220, 90), (255, 220, 40), (60, 140, 255), (255, 100, 220)][i % 5]
        on = lights * (0.55 + 0.45 * math.sin(T * 3 + i * 1.7))
        c.drawCircle(x, y + 16, 26, paint(col, 0.3 * on, blur=14))
        c.drawOval(skia.Rect.MakeXYWH(x - 9, y + 4, 18, 26), paint(mix(col, WHITE, 0.3 * on)))
    # the disco ball, made of old CDs
    bx, by = 820, 470
    c.drawLine(bx, 300, bx, by - 70, paint((40, 40, 40), stroke=3))
    c.drawCircle(bx, by, 70, paint((180, 190, 210)))
    for k in range(16):
        a = k * 0.4 + T * 1.5
        c.drawCircle(bx + 44 * math.cos(a), by + 44 * math.sin(a) * 0.9, 16, paint(mix((200, 230, 255), (255, 200, 240), (k % 3) / 2)))
        c.drawCircle(bx + 44 * math.cos(a), by + 44 * math.sin(a) * 0.9, 4, paint((120, 120, 140)))
    # the riser: plywood, deep enough to stand on
    c.drawPath(path([(0, 1180), (W, 1180), (W, 1350), (0, 1350)]), paint(shader=lin((0, 1180), (0, 1350), [(170, 130, 86), (205, 165, 112)])))
    c.drawRect(skia.Rect.MakeLTRB(0, 1350, W, H), paint((70, 50, 36)))
    for k in range(-2, 9):
        c.drawLine(540 + (k * 150 - 540) * 0.8, 1180, 540 + (k * 150 - 540) * 1.1, 1350, paint((150, 110, 70), stroke=4))
    c.drawLine(0, 1350, W, 1350, paint((110, 80, 50), stroke=6))
    if spot > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), paint(INK, 0.55 * spot))
        c.drawPath(path([(480, 0), (600, 0), (760, 1300), (320, 1300)]), paint((255, 250, 220), 0.16 * spot))
        c.drawOval(skia.Rect.MakeLTRB(300, 1240, 780, 1330), paint((255, 250, 220), 0.3 * spot))


def sign(c, T, y=420, k=1.0):
    """THE WRONG ANSWERS, glitter on cardboard, hung a little crooked."""
    c.save()
    c.translate(430, y)
    c.rotate(-3)
    c.scale(k, k)
    c.drawRect(skia.Rect.MakeXYWH(-330, -100, 660, 200), paint((196, 156, 106)))
    c.drawRect(skia.Rect.MakeXYWH(-330, -100, 660, 200), paint((140, 100, 60), stroke=6))
    tv.wordart(c, "THE WRONG", 0, -10, 80, T, warp="wave", amp=0.06, depth=8, fill=[(255, 240, 160), GOLD, (230, 120, 0)])
    tv.wordart(c, "ANSWERS", 0, 80, 80, T + 0.3, warp="wave", amp=0.06, depth=8, fill=[(255, 160, 220), HOT, (150, 0, 90)])
    c.restore()


def mic(c, x, y0, y1):
    c.drawLine(x, y1, x, y0, paint((30, 30, 34), stroke=12))
    c.drawOval(skia.Rect.MakeLTRB(x - 90, y1 - 10, x + 90, y1 + 20), paint((30, 30, 34)))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 22, y0 - 70, 44, 80), 20, 20), paint((70, 70, 80)))
    for k in range(5):
        c.drawLine(x - 18, y0 - 60 + k * 12, x + 18, y0 - 60 + k * 12, paint((40, 40, 46), stroke=3))


def finish(arr, T, idx, osd=None, k=1.0):
    c = skia.Surface(arr).getCanvas()
    tv.ch99_bug(c, 905, 290, T)
    tv.vhs(arr, T, idx, k)
    return arr


def s_v_bars(T, idx):
    """Colour bars and a tone; then CHANNEL 99 PRESENTS."""
    st = K.Stage()
    c = st.c
    t0 = E("e5") + 0.1
    if T < t0 + 0.55:
        tv.color_bars(c)
        K.text(c, "CH.6", 540, 640, 90, "vt323-400", WHITE, tag="osd", outline=INK, ow=10)
        K.text(c, "CHANNEL 99", 540, 760, 110, "vt323-400", WHITE, tag="osd", outline=INK, ow=10)
        K.text(c, "PUBLIC ACCESS", 540, 860, 80, "vt323-400", WHITE, tag="osd", outline=INK, ow=8)
    else:
        c.drawRect(skia.Rect.MakeWH(W, H), paint((10, 20, 120)))
        rng = np.random.default_rng(3)
        for i in range(60):
            x, y = rng.uniform(0, W), rng.uniform(0, H)
            c.drawCircle(x, y, 2 + (i % 3), paint(WHITE, 0.4 + 0.6 * ((int(T * 8) + i) % 4 == 0)))
        tv.wordart(c, "CHANNEL 99", 540, 640, 140, T, depth=20)
        tv.wordart(c, "PRESENTS", 540, 800, 110, T + 0.2, warp="arch", amp=0.08, depth=16, fill=[(255, 252, 210), GOLD, (230, 110, 0)])
        tv.vhs_osd(c, T, "PLAY", None)
    tv.vhs(st.arr, T, idx, 1.0, track=1.0)
    return st.arr


def s_v_stage(T, idx):
    """'Live from a basement, it's The Wrong Answers!' The troupe waves; five people clap."""
    st = K.Stage()
    c = st.c
    basement(c, T)
    sign(c, T, 410)
    TR.troupe(c, T, (170, 410, 670, 900), 1320, 0.42, wave=1.0, mood="laugh", idx=idx, float_=70)
    return finish(st.arr, T, idx)


def s_v_family(T, idx):
    """'So I quit, and found my people.' Dot walks in; the troupe opens its arms; a group hug."""
    st = K.Stage()
    c = st.c
    basement(c, T)
    sign(c, T, 410)
    walk = K.ease(ramp(T, S("f2") - 0.1, S("f2") + 1.1))
    TR.troupe(c, T, (120, 300, 790, 960), 1320, 0.42, wave=0.6, mood="smile", idx=idx, float_=70)
    dx_ = -200 + 740 * walk
    c.drawOval(skia.Rect.MakeLTRB(dx_ + 70, 1305, dx_ + 300, 1335), paint(INK, 0.32, blur=8))     # her shadow, in the wrong place
    C.live_dot(c, T, idx, dx_, 1240 + 10 * math.sin(T * 2.2), 0.5, pose="wave" if walk < 1 else "both_up", mood="grin", look=(0.3, 0.0), seed=1,
               sock_look=(0.6, 0.0))
    tv.lower_third(c, T, S("f2") + 0.4, "THE WRONG ANSWERS", "a basement troupe (est. last Tuesday)", y=1060, x0=40, w=900)
    return finish(st.arr, T, idx)


INSERTS = [("sock", "A sock."), ("program", "A program."), ("app", "An app")]


def _insert(c, kind, x, y, T, k):
    """A little TV-in-TV callback to an earlier chapter, in its own medium."""
    if k <= 0:
        return
    w, h = 330, 280
    c.save()
    c.translate(x, y)
    c.rotate({"sock": -6, "program": 3, "app": -2}[kind])
    c.scale(k, k)
    c.drawRect(skia.Rect.MakeXYWH(-w / 2 - 14, -h / 2 - 14, w + 28, h + 28), paint(WHITE))
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h))
    if kind == "sock":
        c.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), paint(M.PAPER))
        with M.crayon_layer(c):
            sc1.kid_sock(c, 0, 10, 0.95, T, seed=20, parts=1.0)
    elif kind == "program":
        sc1.dos_screen(c, (-w / 2, -h / 2, w / 2, h / 2), [("WHY DO YOU SAY", (120, 255, 140)), ("THAT?", (120, 255, 140))], T, size=44)
    else:
        K.starburst(c, 0, 0, T, colors=((255, 60, 170), (255, 130, 210)), n=12)
        F.affirma(c, 0, 40, 0.42, T, talk=0.5)
    c.restore()
    c.restore()


def s_v_confess(T, idx):
    """'For thirty years, something else did my talking. A sock. A program. An app that agreed.' At the mic; the
    three of them pop up in their own media."""
    st = K.Stage()
    c = st.c
    basement(c, T)
    TR.troupe(c, T, (110, 970), 1300, 0.45, wave=0.0, mood="smile", idx=idx, who=("gus", "lou"))
    pts = C.live_dot(c, T, idx, 540, 2300, 0.9, pose="sock_chest", mood="sincere", look=(0.0, 0.0), seed=1, sock_look=(0.5, -0.5))
    mic(c, 640, pts["head"][1] + 120, 1500)
    for i, (kind, word) in enumerate(INSERTS):
        t_on = Wx("f3", word.split()[-1].rstrip(".")) - 0.15 if kind != "app" else Wx("f3", "app") - 0.15
        _insert(c, kind, 200 + i * 340, 480 + (i % 2) * 40, T, K.pop(T, t_on, 0.2, 0.3))
    return finish(st.arr, T, idx)


def s_v_truth(T, idx):
    """'AI is real, and powerful.' The laugh track has stopped. One light. The troupe, still."""
    st = K.Stage()
    c = st.c
    basement(c, T, lights=0.4, spot=0.8)
    TR.troupe(c, T, (110, 970), 1300, 0.45, wave=0.0, mood="still", idx=idx, who=("marge", "pixel"))
    pts = C.live_dot(c, T, idx, 540, 2300, 0.9, pose="sock_chest", mood="sincere", look=(0.0, 0.0), seed=1, sock_look=(0.2, -0.6))
    mic(c, 640, pts["head"][1] + 120, 1500)
    return finish(st.arr, T, idx)


def s_v_truth2(T, idx):
    """'But the someone you feel is partly its trainers, and partly you.' A slow push in."""
    st = K.Stage()
    c = st.c
    basement(c, T, lights=0.4, spot=0.8)
    pts = C.live_dot(c, T, idx, 540, 2560, 1.12, pose="sock_chest", mood="sincere", mood2="smile", mk=ramp(T, Wx("f4", "partly", 1), E("f4")),
                     look=(0.0, 0.0), seed=1, sock_look=(-0.4, -0.7), sock_face=-1)
    mic(c, 660, pts["head"][1] + 150, 1700)
    a = st.arr
    z = 1.0 + 0.08 * ramp(T, Wx("f4", "someone") - 0.2, E("f4") + 0.3)
    a = tv.apply_cam(a, 0, 0, 0, z, cx=540, cy=900)
    return finish(a, T, idx)


def s_v_argue(T, idx):
    """'So argue with it. Don't tell it your answer first.' To us."""
    st = K.Stage()
    c = st.c
    basement(c, T, lights=0.6, spot=0.5)
    C.live_dot(c, T, idx, 540, 2480, 1.05, pose="point_up" if T < Wx("f5", "Don't") else "palm", mood="fierce" if T < Wx("f5", "Don't") else "sincere",
               look=(0.0, 0.0), seed=1, sock_look=(0.0, 0.0), sock_face=1)
    return finish(st.arr, T, idx)


def s_v_listener(T, idx):
    """'I wanted to be understood so badly, I built half the listener myself.' She looks at Doc."""
    st = K.Stage()
    c = st.c
    basement(c, T, lights=0.4, spot=0.8)
    lk = (-0.9, 0.0) if T > Wx("f6", "built") - 0.1 else (0.0, 0.0)
    C.live_dot(c, T, idx, 600, 2620, 1.25, pose="sock_up", mood="sincere", look=lk, turn=-0.3 if lk[0] < 0 else 0.0, seed=1,
               sock_look=(0.9, 0.0), sock_face=1)
    return finish(st.arr, T, idx)


def s_v_hand(T, idx):
    """'That's human. Just know which half is yours.' The sock comes off; she holds up her own bare hand. Quiet."""
    st = K.Stage()
    c = st.c
    basement(c, T, lights=0.3, spot=0.9)
    t_off = Wx("f6", "human") - 0.1
    off = T > t_off + 0.5
    if not off:
        pose = "sock_up"
        lift = ramp(T, t_off, t_off + 0.5)
        C.live_dot(c, T, idx, 600, 2620 + 0 * lift, 1.25, pose=pose, mood="sincere", look=(-0.8, -0.2), turn=-0.3, seed=1,
                   sock_look=(0.9, -0.5), sock_face=1, sock_tilt=-30 * lift)
    else:
        pts = C.live_dot(c, T, idx, 600, 2620, 1.25, pose="bare_hand", mood="sincere", look=(-0.9, -0.5), turn=-0.35, seed=1, sock_on=False,
                         hand2="open", hand_pose="hold")
        hx, hy = pts["hand"]                                              # the empty sock, hanging from her other hand
        c.save()
        c.translate(hx - 30, hy + 60)
        c.rotate(80)
        c.scale(0.45, 0.45)
        D.sock_head(c, T, open_=0.0, look=(0.0, 1.0), mirror=True, mood="none")
        c.restore()
    return finish(st.arr, T, idx)


def s_v_joke(T, idx):
    """The sock goes back on. 'I understand what you're saying.' - 'No, you don't.' - 'You're absolutely right!'
    Rimshot; the troupe falls about."""
    st = K.Stage()
    c = st.c
    lit = ramp(T, S("f9") + 0.2, S("f9") + 0.6)
    basement(c, T, lights=0.4 + 0.6 * lit, spot=0.8 * (1 - lit))
    if lit > 0:
        TR.troupe(c, T, (110, 300, 780, 970), 1300, 0.45, wave=lit, mood="laugh", idx=idx)
    mood = "sincere" if T < S("f8") - 0.05 else ("smile" if T < S("f9") else "wince")
    C.live_dot(c, T, idx, 560, 2620, 1.2, pose="sock_up", mood=mood, look=(-0.85, 0.0), turn=-0.3, seed=1, sock_look=(0.9, 0.0),
               sock_face=1)
    if T > S("f9") + 0.2:                                                 # glitter cannon
        rng = np.random.default_rng(9)
        for k in range(120):
            x = rng.uniform(0, W)
            y = (rng.uniform(-600, 0) + (T - S("f9")) * rng.uniform(600, 1100))
            if 0 < y < H:
                c.drawCircle(x, y, rng.uniform(3, 7), paint([(255, 220, 60), (255, 120, 220), (120, 220, 255)][k % 3]))
    return finish(st.arr, T, idx)


TIPS = ["Don't tell it your answer first.", "Ask it to argue the other side.", "Check what matters with a person."]
SOURCES = ["Weizenbaum 1966, 1976", "Heider & Simmel 1944", "Ouyang et al. (OpenAI) 2022", "Sharma et al. (Anthropic) 2023",
           "OpenAI, sycophancy, 2025", "OpenAI, faulty rewards, 2016", "Goodhart 1975; Strathern 1997"]


def s_end(T, idx):
    """The end card: three tips, the sources, the channel bug."""
    st = K.Stage()
    c = st.c
    K.starburst(c, 540, 300, T * 0.4, colors=((40, 10, 70), (70, 20, 110)), n=14, spin=0.2)
    tv.wordart(c, "THE HAND IN THE SOCK", 540, 330, 86, T, max_w=960, depth=14)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(70, 410, 1010, 860), 26, 26), paint((255, 252, 240)))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(70, 410, 1010, 860), 26, 26), paint(INK, stroke=7))
    K.text(c, "NEXT TIME YOU TALK TO AN AI:", 540, 490, 46, "rubik-900", (150, 30, 120), tag="end")
    for i, tip in enumerate(TIPS):
        K.text(c, f"{i + 1}. {tip}", 110, 580 + i * 92, 50, "jost-600", (30, 30, 40), align="left", tag="end")
    K.text(c, "SOURCES", 540, 950, 40, "rubik-900", GOLD, tag="end")
    for i, s in enumerate(SOURCES):
        K.text(c, s, 540, 1006 + i * 50, 38, "jost-500", (230, 220, 250), tag="end")
    K.text(c, "Characters and shows are invented.", 540, 1400, 34, "jost-500", (170, 160, 200), tag="end")
    c.save()
    c.translate(900, 1230)
    c.scale(0.55, 0.55)
    D.sock_head(c, T, open_=0.5 + 0.5 * math.sin(T * 10), look=(-0.6, 0.0))
    c.restore()
    return st.arr

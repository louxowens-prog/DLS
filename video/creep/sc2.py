"""Tale two: THE GHOST WRITER. Kit asks the AI to write her essay instead of helping her understand it; a ghost of
typed pages does it for her; the words she never wrote crawl away; in the exam she has nothing; and then the ghost
does her thinking for good."""
import math

import numpy as np
import skia

import comic as CO
import common as C
import face as FA
import kit as K
import props as PR
import sets as SE
from common import E, S, Wx
from kit import INK, WHITE, H, W, mix, paint, path, ramp, ease
from sc1 import tale_title

KIT_SKIN = FA.CAST["kit"]["skin"]


def ghost_art(c, T):
    SE.dorm(c, T, lamp_on=0.3)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 30), 0.35))
    PR.laptop(c, 540, 1060, 1.0, T, prog=1.0, glow=1.0)
    PR.ghost(c, 560, 760, 1.1, T, mouth=0.8, reach=0.6, tail_to=(540, 1000))


def s_g_title(T, idx):
    st = K.Stage()
    tale_title(st.c, T, S("g1") - 0.4, ["THE GHOST", "WRITER"], ghost_art, colr=(240, 240, 230), seed=20)
    return st.arr


def kit_desk(c, T, expr="neutral", prog=0.0, ghost=0.0, gaze=(0.0, 0.4), lamp=1.0, talk=None, kx=540):
    """Kit at her desk at 2 a.m., the laptop between us and her."""
    SE.dorm(c, T, lamp_on=lamp)
    kw = {} if talk is None else {"talk": talk}
    C.person(c, "kit", kx, 760, 1.3, T, expr=expr, light="laptop", gaze=gaze, seed=7, **kw)
    desk = path([(-50, 1150), (W + 50, 1150), (W + 50, H), (-50, H)])
    FA.lit_fill(c, desk, (110, 74, 50), FA.Light("lamp"), rim=0.5)
    # a pizza box and a mug: it is late
    c.drawRect(skia.Rect.MakeLTRB(40, 1170, 300, 1220), paint((230, 210, 170)))
    c.drawRect(skia.Rect.MakeLTRB(40, 1170, 300, 1220), paint((140, 30, 30), stroke=4))
    c.drawRoundRect(skia.Rect.MakeLTRB(860, 1100, 960, 1210), 12, 12, paint((60, 120, 180)))
    PR.laptop(c, 540, 1180, 1.05, T, prog=prog, glow=1.0)
    if ghost > 0:
        PR.ghost(c, 800, 700 - 160 * ghost, 0.75 * ghost, T, a=min(1.0, ghost * 1.5), mouth=0.5 + 0.3 * math.sin(T * 5), reach=ghost,
                 tail_to=(640, 1060))


def s_g_dorm(T, idx):
    st = K.Stage()
    kit_desk(st.c, T, expr="smug", prog=0.0, gaze=(0.0, 0.6))
    if T > S("g2") + 0.3:
        CO.sfx(st.c, "TAP TAP TAP", 540, 1110, 52, k=K.pop(T, S("g2") + 0.3, 0.15, 0.2), rot=-3, fill=(255, 255, 255), fill2=(180, 200, 255), tag="sfx")
    return st.arr


def s_g_ghost(T, idx):
    """The ghost writer rises out of the screen and types; Kit sits back. Nine in ten UK students use AI."""
    st = K.Stage()
    c = st.c
    t0 = S("g3") - 0.1
    g = ease(ramp(T, t0, t0 + 1.0))
    kit_desk(c, T, expr="smile", prog=ramp(T, t0 + 0.5, t0 + 3.5), ghost=g, gaze=(0.7, -0.5), kx=420)
    t1 = Wx("g3", "Nine") - 0.05
    if T > t1:
        k = K.pop(T, t1, 0.25, 0.3)
        CO.sfx(c, "9 IN 10", 260, 380, 120, k=k, rot=-8, fill=(255, 226, 0), fill2=(255, 120, 0), tag="stat")
        CO.label(c, "UK STUDENTS USE AI", 270, 470, 46, "bangers-400", WHITE, tag="stat", outline=INK, ow=10, a=min(1.0, k))
    return st.arr


def s_g_split(T, idx):
    """'Help me understand' builds a mind; 'Write it for me' doesn't."""
    st = C.page(seed=11)
    c = st.c
    for side, (x0, x1, key, word, title) in enumerate(((40, 530, "g3", "Help", "HELP ME UNDERSTAND"), (550, 1040, "g3", "Write", "WRITE IT FOR ME"))):
        t0 = Wx(key, word) - 0.12
        if T < t0:
            continue
        a = ease(ramp(T, t0, t0 + 0.2))
        with C.sub((40, 30, 60) if side else (250, 220, 120)) as sub:
            sc = sub.c
            if side == 0:
                CO.shock(sc, (250, 200, 80), T, cx=245, cy=420, seed=2, rays=20, bolts=0)
                FA.bust(sc, "kit", 245, 600, 1.0, T, expr="smile", light="lamp", gaze=(0.3, -0.6))
                grow = ease(ramp(T, t0 + 0.2, t0 + 1.2))
                PR.brain(sc, 245, 330, 0.45 * (0.6 + 0.4 * grow), T, glow=grow, grow=1 + 0.3 * grow)
            else:
                SE.grad_bg(sc, (40, 30, 60), (14, 10, 20))
                FA.bust(sc, "kit", 245, 600, 1.0, T, expr="blank", light="green", gaze=(0, 0))
                sc.save()
                sc.translate(245, 600)
                hollow = K.oval(-90, -170, 90, -60)
                sc.drawPath(hollow, paint((10, 6, 14), 0.9))
                CO.cobweb(sc, -90, -170, 150, 0, 90, a=0.9, seed=5)
                sc.restore()
                CO.spider(sc, 330, 380 + 30 * math.sin(T * 2), 1.0, T)
        CO.panel(c, sub.arr[:1000, :490], x0, 300, x1, 1250, border=12, rot=(-1.0, 1.0)[side], a=a)
        CO.caption_box(c, title, (x0 + x1) / 2, 300, maxw=470, size=40, k=a, rot=(-2, 2)[side], anchor="top", tag="label",
                       fill=(255, 226, 0) if side == 0 else (200, 200, 200))
    return st.arr


def s_g_quote(T, idx):
    """Kit tries to read the essay 'she' wrote; the words crawl off the page like beetles. 83% couldn't quote one line."""
    st = K.Stage()
    c = st.c
    t0 = S("g4") - 0.1
    SE.dorm(c, T, lamp_on=0.8)
    C.person(c, "kit", 540, 640, 1.2, T, expr="fear" if T > Wx("g4", "couldn't") else "neutral", light="lamp", gaze=(0.0, 0.9), seed=7)
    # the essay, held up in front of her
    px0, py0, px1, py1 = 230, 860, 850, 1300
    c.save()
    c.translate(540, 1080)
    c.rotate(-3)
    c.translate(-540, -1080)
    c.drawRect(skia.Rect.MakeLTRB(px0 + 10, py0 + 14, px1 + 10, py1 + 14), paint(INK, 0.4, blur=10))
    c.drawRect(skia.Rect.MakeLTRB(px0, py0, px1, py1), paint((248, 246, 236)))
    CO.label(c, "MY ESSAY", (px0 + px1) / 2, py0 + 60, 46, "special-elite-400", INK, tag="deco")
    crawl = ramp(T, Wx("g4", "couldn't") - 1.6, E("g4"))
    rng = K.rng_at(8, 8)
    n_lines = 14
    for i in range(n_lines):
        yy = py0 + 110 + i * 26
        if rng.random() > crawl * 1.2:
            c.drawLine(px0 + 40, yy, px1 - 40 - (180 if i % 4 == 3 else 0), yy, paint((50, 50, 60), 0.85, stroke=7))
    c.restore()
    for i in range(int(40 * crawl)):                                   # the words, scuttling off as beetles
        sx, sy = rng.uniform(px0 + 40, px1 - 40), rng.uniform(py0 + 100, py1 - 30)
        u = (crawl * 1.6 - i / 40)
        if u <= 0:
            continue
        ang = rng.uniform(-math.pi, math.pi)
        d = 260 * u
        CO.beetle(c, sx + d * math.cos(ang), sy + d * math.sin(ang), 0.9, ang, T, seed=i)
    for i, x in enumerate((240, 840)):
        FA.hand(c, x, 1240, 1.0, -90 + (40 if i == 0 else -40), skin=KIT_SKIN, light="lamp", pose="grip", flip=i == 1)
    t1 = Wx("g4", "83%") - 0.05
    if T > t1:
        CO.sfx(c, "83%", 820, 420, 150, k=K.pop(T, t1, 0.25, 0.3), rot=8, fill=(255, 60, 40), fill2=(160, 0, 10), tag="stat")
    return st.arr


def tomb(c, x, base, h, w, colr, label, top_text, T, a=1.0):
    """A bar of the chart, as a tombstone rising out of (or sinking into) the earth."""
    p = skia.Path()
    p.moveTo(x - w / 2, base)
    p.lineTo(x - w / 2, base - h + w / 2)
    p.arcTo(skia.Rect.MakeLTRB(x - w / 2, base - h, x + w / 2, base - h + w), 180, 180, False)
    p.lineTo(x + w / 2, base)
    p.close()
    FA.lit_fill(c, p, colr, FA.Light("lamp"), rim=0.8, rim_w=6, a=a)
    c.drawPath(p, paint(INK, a, stroke=6))
    if top_text:
        CO.label(c, top_text, x, base - h - 30, 66, "bangers-400", WHITE, tag="stat", outline=INK, ow=10, a=a)
    CO.label(c, label, x, base + 70, 40, "bangers-400", WHITE, tag="label", a=a, outline=INK, ow=8)


def s_g_chart(T, idx):
    """With AI the practice scores jumped 48%; without it, 17% worse than students who never had it."""
    st = K.Stage()
    c = st.c
    SE.grad_bg(c, (60, 50, 80), (20, 16, 30))
    CO.shock(c, (70, 40, 110), T, cx=540, cy=600, seed=6, rays=26, bolts=0, a=0.6)
    base = 1110
    c.drawRect(skia.Rect.MakeLTRB(0, base, W, H), paint((40, 30, 20)))
    for i in range(30):
        c.drawCircle((i * 97) % W, base + 30 + (i * 53) % 200, 6, paint((70, 50, 30)))
    up = ease(ramp(T, Wx("g5", "jumped") - 0.3, Wx("g5", "jumped") + 0.4))
    down = ease(ramp(T, Wx("g5", "Without") - 0.1, Wx("g5", "17%") + 0.2))
    ctrl = 420
    hai = ctrl * (1 + 0.48 * up) - ctrl * (0.48 + 0.17) * down * 1.0
    if down > 0:
        hai = ctrl * 1.48 * (1 - down) + ctrl * 0.83 * down
    tomb(c, 300, base, ctrl, 230, (150, 150, 160), "NEVER HAD AI", "", T)
    lab = "+48%" if down < 0.5 else "-17%"
    tomb(c, 760, base, hai, 230, (120, 200, 140) if down < 0.5 else (200, 60, 60), "HAD AI, THEN LOST IT" if down > 0.5 else "WITH AI",
         lab if (up > 0.6 or down > 0.5) else "", T)
    if down > 0.6:                                                      # dug-up earth round the sunk stone
        for i in range(8):
            c.drawCircle(640 + i * 34, base - 6 + (i % 2) * 8, 22, paint((60, 44, 30)))
    gh = 1 - down
    if gh > 0.02:
        PR.ghost(c, 960, base - hai + 60 + 20 * math.sin(T * 3), 0.45, T, a=gh, mouth=0.6, reach=1.0, light="lamp", tail_to=(1000, base))
    CO.label(c, "PRACTICE" if down < 0.5 else "WITHOUT IT", 540, 310, 56, "bangers-400", (255, 226, 0), tag="label", outline=INK, ow=10)
    return st.arr


def s_g_exam(T, idx):
    """Silence in the exam hall. No devices, Kit. Explain your argument."""
    st = K.Stage()
    c = st.c
    SE.exam_hall(c, T)
    take = ease(ramp(T, Wx("g6", "devices") - 0.2, Wx("g6", "devices") + 0.5))
    C.person(c, "kit", 300, 1030, 1.0, T, expr="fear" if T > Wx("g6", "Explain") else "neutral", light="clinic", gaze=(0.8, -0.8), seed=7)
    C.person(c, "prof", 760, 640, 1.25, T, expr="angry", light="clinic", gaze=(-0.8, 0.6), seed=9, turn=-0.3)
    desk = path([(-50, 1250), (700, 1250), (700, 1330), (-50, 1330)])
    FA.lit_fill(c, desk, (120, 90, 60), FA.Light("clinic"), rim=0.5)
    PR.phone(c, 420 + 300 * take, 1220 - 280 * take, 0.35, -70 + 70 * take, T, screen="muse", level=0.0)
    FA.hand(c, 560 + 300 * take, 1180 - 280 * take, 0.9, 200, skin=FA.CAST["prof"]["skin"], light="clinic", pose="grip", flip=True)
    c.drawRect(skia.Rect.MakeLTRB(80, 1236, 380, 1256), paint((250, 248, 236)))
    return st.arr


def s_g_blank(T, idx):
    """I... it said... I... Push in on her face; the balloon has nothing in it worth having."""
    st = K.Stage()
    c = st.c
    t0 = S("g7") - 0.08
    CO.shock(c, "green", T, cx=540, cy=760, seed=12)
    C.dutch(c, 10, 540, 900)
    C.push(c, T, t0, E("g7") + 0.3, 1.0, 1.3, cx=540, cy=820)
    C.person(c, "kit", 540, 820, 2.1, T, expr="panic", light="green", gaze=(0.6 * math.sin(T * 9), -0.3), seed=7, shake=4)
    c.restore()
    c.restore()
    return st.arr


def s_g_puppet(T, idx):
    """The ghost does her thinking now: its pages wrapped round her head, her eyes gone white, strings from above."""
    st = K.Stage()
    c = st.c
    t0 = S("g8") - 0.1
    SE.dorm(c, T, lamp_on=0.4)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((10, 30, 20), 0.4))
    nod = math.sin(T * 3.2) * 6 * ease(ramp(T, t0 + 1.0, t0 + 1.8))
    wrap = ease(ramp(T, t0, t0 + 1.4))
    E_ = dict(FA.EXPR["blank"])
    E_["smile"] = 0.35 * wrap
    E_["eye"] = 1.0
    if wrap < 0.6:
        E_ = "fear"
    C.push(c, T, t0, E("g8") + 0.4, 1.0, 1.12, cx=540, cy=760)

    def mask(cc, L):
        if wrap <= 0:
            return
        with K.layer(cc, wrap):
            sheet = K.smooth([(-176, -150), (-120, -262), (0, -292), (120, -262), (176, -150), (150, -96), (60, -112), (0, -100), (-60, -112),
                              (-150, -96)])
            FA.lit_fill(cc, sheet, (238, 234, 218), L, rim=0.8, rim_w=6)
            for i in range(6):
                cc.drawLine(-140, -250 + i * 26, 140, -246 + i * 26, paint((60, 60, 80), 0.4, stroke=4))
            for sx in (-1, 1):                                          # its ink-blot eyes on her forehead
                cc.drawCircle(sx * 52, -190, 20, paint((10, 10, 20), 0.9))
                cc.drawPath(K.capsule(sx * 52 - 6, -176, sx * 52 - 8, -140, 8, 5), paint((10, 10, 20), 0.9))
        for i in range(int(12 * wrap)):                                 # typed words across her cheeks
            cc.drawLine(-90, 30 + i * 9, 90, 30 + i * 9, paint((40, 40, 70), 0.18 * wrap, stroke=3))
    C.person(c, "kit", 540, 760 + nod, 1.5, T, expr=E_, light="storm", seed=7, after=mask, tilt=nod * 0.6)
    c.restore()
    for x0, x1 in ((380, 430), (700, 650), (540, 540)):                # the strings
        c.drawLine(x0, 0, x1, 520 + nod, paint((230, 230, 230), 0.7 * wrap, stroke=2))
    PR.ghost(c, 540, 170, 0.5, T, a=wrap, mouth=0.4, reach=1.0, light="green")
    C.margin_host(c, T, 960, 1130, 0.8, expr="cackle" if T > Wx("g8", "Now") else "sly", t0=Wx("g8", "process"), light="green")
    return st.arr

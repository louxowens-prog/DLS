"""Every shot: s_<name>(T, t, d) -> a Stage (T = film time, t = time into the shot, d = its length). A shot may set
st.lk, the print settings for techni.look (sat, bloom, flash, blaze, warm...)."""
import math

import numpy as np
import skia

import draw as D
import figs as F
import kit as K
import sets_a as A
import sets_b as B
from cues import C, E, S, Wx, words_upto
from draw import H, W, ease, mix, paint, path, ramp
from timeline import TL

FLASHES = [0.95, S("p1") + 0.6, C["storm"], S("r1") - 1.2, S("r1") + 2.6, Wx("r1", "sick") + 0.15, S("r7") + 0.5, S("b2") + 0.6,
           Wx("b3", "made"), S("g1") - 1.1, S("m1") - 0.6, S("d1") - 0.4]


def stage(bg=(0, 0, 0), **lk):
    st = D.Stage(bg)
    st.lk = lk
    return st


def fade_in(t, a=0.0, d=0.25):
    return ease(ramp(t, a, a + d))


# ------------------------------------------------------------------ the phone's screen

def chat_screen(msgs, T, header=True, typing=False):
    """msgs: [(who, [lines], alpha)] - who 'me' (blue, right) or 'ai' (grey, left). Painted in phone-local coordinates."""
    def fn(c):
        if header:
            c.drawRect(skia.Rect.MakeLTRB(-182, -392, 182, -300), paint((20, 22, 30)))
            K.glow(c, -120, -340, 26, (120, 200, 255), 0.9)
            c.drawCircle(-120, -340, 14, paint((150, 220, 255)))
            f = D.font("jost-600", 26)
            c.drawString("Assistant", -92, -330, f, paint((235, 240, 250)))
            D.reg_local(c, -92, -352, -92 + f.measureText("Assistant"), -326, "chat")
            c.drawString("✓ always here", -92, -306, D.font("jost-500", 15), paint((120, 220, 160)))
        y = -280
        for who, lines, a in msgs:
            if a <= 0:
                continue
            if who == "me":
                h = K.bubble(c, lines, 170, y, 300, size=24, me=True, a=a)
            else:
                h = K.bubble(c, lines, -170, y, 320, size=24, a=a)
            y += h + 18
        if typing:
            for k in range(3):
                c.drawCircle(-140 + k * 26, y + 30, 8, paint((200, 200, 210), 0.4 + 0.6 * abs(math.sin(T * 5 + k))))
    return fn


ANSWER = ["Based on your symptoms,", "this is unlikely to be", "serious. It's most likely", "acid reflux. Sit upright,", "and rest."]
QUESTION = ["tight chest, sore jaw.", "probably just reflux", "right?"]


def answer_lines(key, T):
    """The answer's lines, revealed word by word in time with the Voice."""
    n = words_upto(key, T) if T < E(key) else 99
    out, k = [], 0
    for ln in ANSWER:
        ws = ln.split(" ")
        take = max(0, min(len(ws), n - k))
        if take:
            out.append(" ".join(ws[:take]))
        k += len(ws)
    return out


# ------------------------------------------------------------------ COLD OPEN

def s_eye(T, t, d):
    st = stage(sat=1.35, bloom=0.6)
    z = 1.0 + 0.14 * t
    blink = 1.0 - 0.95 * max(0.0, 1 - abs(t - 2.05) / 0.09)
    open_k = (0.15 + 0.85 * ease(ramp(t, 0.0, 0.35))) * blink
    pupil = 0.8 + 0.6 * ease(ramp(T, S("o1") + 1.2, S("o1") + 2.6))
    dart = (0.25 * math.sin(T * 1.7) + (0.18 if 1.2 < t < 1.6 else 0.0) - (0.2 if 2.6 < t < 3.0 else 0.0), 0.06 * math.sin(T * 2.3))
    fl = K.flash_at(T, [1.3])
    F.eye(st.c, 540, 860, 1.12 * z, T, open_k, gel=K.RED, pupil=pupil, look=dart, wet=1.0)
    K.glow(st.c, 1000, 300, 900, (130, 160, 255), 1.0 * fl)
    st.lk["flash"] = 0.3 * fl
    return st


def s_floor(T, t, d):
    """The phone on the carpet in the dark, glowing; the key beside it; fingertips at the edge of frame, still."""
    st = stage(sat=1.35, bloom=0.7)
    c = st.c
    z = 1.0 + 0.03 * t
    c.save()
    A.cam(c, z, 540, 900)
    c.drawImage(B._carpet_tex(), -200, -2000)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0), 0.55))
    K.glow(c, 540, 800, 800, K.RED, 0.35)
    scr = chat_screen([("ai", ["Based on your symptoms,", "this is unlikely to be", "serious."], 1.0)], T, header=True)
    K.phone(c, 520, 800, 1.5, -7, scr, glow_col=(150, 200, 255))
    K.key(c, 760, 1290, 0.7, ang=24, glint=0.8, T=T)
    F.hand_flat(c, 250, 1180, 1.3, gel=K.RED, ang=-8, twitch=max(0.0, 1.0 - t / 0.45))   # her hand: a twitch, then still
    c.restore()
    K.dark(c, 540, 900, 380, 1100, 0.6)
    return st


def door_front(c, T, num, gel, z=1.0, leak=1.0):
    c.save()
    A.cam(c, z, 540, 960)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((2, 2, 10)))
    wall = A.cached("wall100", lambda: K.tiled(K.diamond_tile(150, 190, (6, 10, 40), (40, 60, 180), (200, 160, 80)), W, H))
    c.drawImage(wall, 0, 0)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0), 0.55))
    c.drawRect(skia.Rect.MakeLTRB(300, 380, 780, 1560), paint((50, 22, 10)))
    c.drawRect(skia.Rect.MakeLTRB(330, 410, 750, 1560), paint(shader=D.lin((330, 0), (750, 0), [(40, 16, 8), (80, 34, 14), (30, 12, 6)])))
    for (y0, y1) in ((460, 900), (960, 1500)):
        c.drawRect(skia.Rect.MakeLTRB(380, y0, 700, y1), paint((20, 8, 4), 0.8, stroke=8))
    K.door_plate(c, 540, 560, num, s=1.3, tag="door")
    c.drawCircle(700, 1000, 18, paint(K.BRASS))
    c.drawRect(skia.Rect.MakeLTRB(330, 1550, 750, 1560), paint(gel, leak))
    K.beam(c, [(330, 1556), (750, 1556), (1000, 1920), (80, 1920)], gel, 0.7 * leak, p0=(540, 1556), p1=(540, 1920))
    K.glow(c, 540, 1560, 400, gel, 0.6 * leak)
    c.drawPath(path([(692, 1030), (708, 1030), (712, 1060), (688, 1060)]), paint((0, 0, 0)))
    K.glow(c, 700, 1045, 40, gel, 0.9 * leak)
    c.restore()


def s_door100(T, t, d):
    st = stage(sat=1.35, bloom=0.65)
    door_front(st.c, T, "100", K.RED, z=1.0 + 0.1 * t, leak=0.6 + 0.4 * math.sin(T * 3) ** 2)
    K.dark(st.c, 540, 960, 380, 1150, 0.5)
    return st


TITLE_COLS = [K.RED, K.BLUE, K.GREEN, K.MAGENTA]


def s_title(T, t, d):
    st = stage(sat=1.3, bloom=0.7)
    c = st.c
    i = int(t / 0.42)
    if i < 4:
        colr = TITLE_COLS[i]
        c.drawRect(skia.Rect.MakeWH(W, H), paint(mix(colr, (0, 0, 0), 0.75)))
        K.glow(c, 540, 860, 1000, colr, 0.8)
    else:
        B._blaze_core(c, T, 540, 860, 0.8)
        c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0), 0.35))
    z = 1.0 + 0.04 * t
    c.save()
    A.cam(c, z, 540, 820)
    K.deco_frame(c, 110, 470, 970, 1170, K.GOLD, 1.0, 6)
    D.text(c, "THE", 540, 600, 70, "poiret-400", (255, 236, 200), tag="title", shadow=(0, 0, 0))
    D.text(c, "HUNDREDTH", 540, 790, 116, "limelight-400", (255, 244, 220), tag="title", shadow=(0, 0, 0))
    D.text(c, "ROOM", 540, 960, 150, "limelight-400", (255, 244, 220), tag="title", shadow=(0, 0, 0))
    K.key(c, 640, 1080, 0.5, ang=0, glint=1.0, T=T)
    c.restore()
    st.lk["flash"] = 0.5 * math.exp(-t / 0.08)
    return st


def s_black(T, t, d):
    return stage(grain=1.2, bloom=0.0)


# ------------------------------------------------------------------ PROLOGUE

def s_exterior(T, t, d):
    st = stage(sat=1.35, bloom=0.6)
    stride = math.sin(T * 5.0)
    nx = 300 + 60 * min(t, 4.0)
    fl = A.hotel(st, T, z=1.0 + 0.03 * t, cy=1250, flashes=FLASHES, nora=(nx, stride), taxi=min(1.0, t / 3.0), dy=120)
    st.lk["flash"] = 0.3 * fl
    return st


CHECKS = [("p2", "Flights", "Flight rebooked", K.BLUE), ("p2", "emails", "Emails sent", K.GREEN), ("p2", "taxes", "Taxes filed", K.MAGENTA),
          ("p2", "fever", "Fever: fluids, rest", K.AMBER)]


def s_checks(T, t, d):
    st = stage(sat=1.35, bloom=0.55)
    c = st.c
    n = sum(1 for k, w, lab, col_ in CHECKS if T >= Wx(k, w) - 0.1)
    colr = CHECKS[max(0, n - 1)][3] if n else K.BLUE
    c.drawRect(skia.Rect.MakeWH(W, H), paint(mix(colr, (0, 0, 0), 0.82)))
    K.glow(c, 540, 700, 1000, colr, 0.6)

    def scr(cc):
        f = D.font("jost-600", 30)
        cc.drawString("Assistant", -120, -310, f, paint((235, 240, 250)))
        for i, (k, w, lab, col_) in enumerate(CHECKS):
            a = fade_in(T, Wx(k, w) - 0.1, 0.15)
            if a <= 0:
                continue
            y = -230 + i * 150
            cc.drawPath(D.rrect(-160, y, 160, y + 120, 24), paint((40, 42, 54), a))
            K.check(cc, -110, y + 60, 26, (60, 230, 130), a, w=9)
            ff = D.font("jost-500", 27)
            cc.drawString(lab, -70, y + 70, ff, paint((240, 240, 246), a))
            D.reg_local(cc, -70, y + 48, -70 + ff.measureText(lab), y + 76, "chat")
    F.hand_phone(c, 560, 860, 1.5, T, scr, thumb=0.2, gel=colr, ang=-4)
    return st


def s_nocheck(T, t, d):
    st = stage(sat=1.3, bloom=0.55)
    open_k = 1.0 - 0.72 * ease(ramp(t, 0.2, d - 0.2))
    F.eye(st.c, 540, 880, 1.1, T, open_k, gel=(20, 160, 140), pupil=0.9, iris_col=(90, 110, 80))
    return st


def s_lobby(T, t, d):
    st = stage(sat=1.35, bloom=0.6)
    A.lobby(st, T, z=1.0 + 0.05 * t, cy=900, key_a=1.0, flashes=FLASHES)
    return st


def s_keydesk(T, t, d):
    st = stage(sat=1.35, bloom=0.7)
    A.lobby(st, T, z=2.6 + 0.25 * t, cx=640, cy=1150, key_a=1.0)
    return st


# ------------------------------------------------------------------ RED: her room

def s_clock(T, t, d):
    st = stage(sat=1.35, bloom=0.55)
    fl = A.clock(st, T, 2, 7, ss=12 + t, flashes=FLASHES, z=1.0 + 0.05 * t)
    st.lk["flash"] = 0.3 * fl
    return st


def s_bed(T, t, d):
    st = stage(sat=1.35, bloom=0.6)
    hand = "jaw" if T >= Wx("r1", "jaw") - 0.2 else "chest"
    fl = A.red_room(st, T, z=1.08 + 0.02 * t, flashes=FLASHES, nora="sit", hand=hand, head=8, pulse=0.5 + 0.5 * math.sin(T * 7))
    st.lk["flash"] = 0.3 * fl
    return st


def s_chestcu(T, t, d):
    st = stage(sat=1.35, bloom=0.55)
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((40, 2, 8)))
    K.glow(c, 900, 500, 1000, K.RED, 0.6 + 0.2 * math.sin(T * 7))
    F.face_profile(c, 330, 4250, 4.4, key=(255, 120, 120), rim=(120, 160, 255), eye_k=0.6, tear=ease(ramp(t, 0.5, 2.5)), hand=True,
                   head=6 + 2 * math.sin(T * 1.3), T=T, pain=0.8, sweat=0.7)
    return st


def s_type(T, t, d):
    st = stage(sat=1.35, bloom=0.5)
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((30, 2, 8)))
    K.glow(c, 540, 900, 1000, K.RED, 0.5)
    words = sum(1 for w, a, b in TL.lines["r2"]["words"] if a <= T)
    txt = " ".join(" ".join(QUESTION).split(" ")[:int(words * 7 / 8 + 0.99)])
    from draw import wrap
    lines = wrap(txt, D.font("jost-500", 24), 250) if txt else []
    sent = T >= E("r2") - 0.1
    scr = chat_screen([("me", QUESTION if sent else lines, 1.0 if (sent or lines) else 0.0)], T, typing=sent)
    F.hand_phone(c, 560, 860, 1.55, T, scr, thumb=0.0 if sent else 0.6, gel=K.RED, ang=-5, tremble=1.0)
    return st


def s_faceglow(T, t, d):
    st = stage(sat=1.35, bloom=0.6)
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((36, 2, 8)))
    K.glow(c, 200, 600, 1000, K.RED, 0.55)
    K.glow(c, 900, 900, 500, (150, 200, 255), 0.5 + 0.1 * math.sin(T * 8))
    F.face_profile(c, 300, 4300 + 20 * t, 4.4, key=(150, 200, 255), rim=K.RED, eye_k=1.0, head=10, T=T, pain=0.45, sweat=0.8)
    return st


def s_answer(T, t, d):
    st = stage(sat=1.3, bloom=0.45)
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((24, 2, 6)))
    K.glow(c, 540, 800, 1000, K.RED, 0.45)
    msgs = [("me", QUESTION, 1.0), ("ai", answer_lines("r4", T), 1.0 if T >= S("r4") else 0.0)]
    scr = chat_screen(msgs, T, typing=T < S("r4"))
    K.phone(c, 540, 930, 1.72 + 0.02 * t, -3, scr, glow_col=(150, 200, 255))
    return st


def s_relief(T, t, d):
    st = stage(sat=1.3, bloom=0.6)
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((30, 2, 8)))
    K.glow(c, 300, 500, 1100, K.RED, 0.5 + 0.15 * math.sin(T * 6.5))
    F.face_profile(c, 300, 4300, 4.4, key=(160, 205, 255), rim=K.RED, eye_k=1.0 - 0.85 * ease(ramp(t, 1.5, d - 0.5)), head=10 - 14 * ease(ramp(t, 1.0, d)),
                   key_a=0.9, T=T, pain=0.35 * (1 - ease(ramp(t, 0.5, 2.5))), sweat=0.6)
    return st


def scale_scene(c, T, t):
    c.drawRect(skia.Rect.MakeWH(W, H), paint((24, 2, 6)))
    K.glow(c, 540, 1000, 1000, K.RED, 0.5)
    c.drawRect(skia.Rect.MakeLTRB(0, 1260, W, H), paint((50, 10, 8)))
    tilt = 2.0 * math.sin(T * 1.7) * math.exp(-t * 0.6)
    bx, by = 540, 820
    c.drawPath(D.rrect(bx - 20, by, bx + 20, 1260, 8), paint(shader=D.lin((bx - 20, 0), (bx + 20, 0), [K.BRASS_D, K.BRASS_L, K.BRASS_D])))
    c.drawPath(D.smooth([(bx - 140, 1270), (bx, 1220), (bx + 140, 1270)]), paint(K.BRASS))
    c.save()
    c.translate(bx, by)
    c.rotate(tilt)
    c.drawPath(D.rrect(-380, -12, 380, 12, 6), paint(shader=D.lin((0, -12), (0, 12), [K.BRASS_L, K.BRASS_D])))
    c.drawCircle(0, 0, 26, paint(K.BRASS))
    for sx in (-1, 1):
        px = sx * 360
        c.drawLine(px, 0, px - 120, 300, paint(K.BRASS_D, stroke=4))
        c.drawLine(px, 0, px + 120, 300, paint(K.BRASS_D, stroke=4))
        c.drawPath(D.smooth([(px - 170, 300), (px, 350), (px + 170, 300)]), paint(shader=D.lin((px - 170, 0), (px + 170, 0), [K.BRASS_D, K.BRASS_L, K.BRASS_D])))
    # left pan: a doctor's pad; right pan: the phone with its red tag
    c.drawPath(D.rrect(-450, 190, -270, 300, 8), paint((236, 236, 240)))
    c.drawString("Rx", -430, 250, D.font("cormorant-700", 50), paint((40, 40, 80)))
    for k in range(3):
        c.drawRect(skia.Rect.MakeLTRB(-430, 262 + k * 10, -290, 266 + k * 10), paint((120, 120, 140)))
    K.phone(c, 360, 230, 0.16, 0, chat_screen([("ai", ["..."], 1.0)], T, header=False), glow_col=(150, 200, 255))
    c.restore()
    D.text(c, "DOCTOR", bx - 330, by + 420, 38, "jost-600", (255, 230, 230), tag="scale1")
    D.text(c, "LOW-ACCURACY", bx + 260, by + 420, 34, "jost-600", (255, 120, 120), tag="scale2")
    D.text(c, "AI ADVICE", bx + 260, by + 462, 34, "jost-600", (255, 120, 120), tag="scale3")


def s_scale(T, t, d):
    st = stage(sat=1.3, bloom=0.5)
    scale_scene(st.c, T, t)
    K.plate(st.c, "TRUSTED THE SAME", "People rated low-accuracy AI medical advice as valid and trustworthy as doctors' - and said they'd follow it",
            "MIT study, NEJM AI, 2025 (300 people)", y=280, color=K.GOLD, a=fade_in(t, 0.3), size=72, glow_col=K.RED)
    return st


def s_liewall(T, t, d):
    st = stage(sat=1.35, bloom=0.6)
    k = ease(ramp(T, Wx("r7", "wall") - 0.3, Wx("r7", "wall") + 0.8))
    A.red_room(st, T, z=1.1 + 0.4 * k, cx=540 - 300 * k, cy=900, flashes=FLASHES, nora="lie", phone_lit=0.8)
    if k > 0:                                                           # the wall glows blue from the other side
        K.glow(st.c, 200, 800, 700, K.BLUE, 0.5 * k * (0.8 + 0.2 * math.sin(T * 9)))
    return st


# ------------------------------------------------------------------ the corridor, ROOM 97

def s_spiral(T, t, d):
    st = stage(sat=1.4, bloom=0.5)
    B.spiral(st, T, rot=T * 1.1, nora_k=min(1.0, t / d))
    return st


DOORS = [(4, -1, "97", K.BLUE), (7, 1, "98", K.GREEN), (10, -1, "99", K.MAGENTA), (13, 1, "96", K.RED)]


def s_corr97(T, t, d):
    st = stage(sat=1.4, bloom=0.65)
    fl = B.corridor(st, T, zc=0.2 + 0.55 * t, doors=DOORS, spill={"97": 1.0}, light=K.BLUE, wall="blue", flashes=FLASHES, stranger=15.0)
    st.lk["flash"] = 0.2 * fl
    return st


def s_blue(T, t, d):
    st = stage(sat=1.4, bloom=0.6)
    fl = B.blue_room(st, T, z=1.0 + 0.04 * t, flashes=FLASHES)
    st.lk["flash"] = 0.3 * fl
    return st


def s_pen(T, t, d):
    st = stage(sat=1.4, bloom=0.5)
    B.pen(st, T, k=ease(ramp(t, 0.1, d - 0.1)))
    return st


def s_papers(T, t, d):
    st = stage(sat=1.4, bloom=0.5)
    B.papers(st, T, stamp=ramp(T, Wx("b3", "made") - 0.2, Wx("b3", "made") + 0.9))
    K.plate(st.c, "6 INVENTED CASES", "Two lawyers cited ChatGPT's fake cases in a federal court filing. Fine: $5,000.", "Mata v. Avianca, New York, 2023",
            y=270, color=K.GOLD, a=fade_in(t, 0.2), size=74, glow_col=K.BLUE)
    return st


def s_books(T, t, d):
    st = stage(sat=1.4, bloom=0.55)
    B.books(st, T, red_k=ease(ramp(t, 0.6, 1.4)))
    K.plate(st.c, "AT LEAST 1 IN 6 WRONG", "Professional legal AI research tools, tested on legal research questions", "Stanford RegLab / HAI, 2024",
            y=270, color=K.GOLD, a=fade_in(t, 0.2), size=72, glow_col=K.BLUE)
    return st


def s_turn(T, t, d):
    st = stage(sat=1.45, bloom=0.7)
    B.blue_room(st, T, z=1.9 + 0.3 * t, cx=360, cy=640, turn=ease(ramp(t, 0.0, 0.18)), flashes=[T - t], nora_door=0.0)
    st.lk["flash"] = 0.5 * math.exp(-t / 0.1)
    return st


# ------------------------------------------------------------------ ROOM 98

def s_corr98(T, t, d):
    st = stage(sat=1.4, bloom=0.65)
    fl = B.corridor(st, T, zc=3.6 + 0.55 * t, doors=DOORS, spill={"98": 1.0}, light=K.GREEN, wall="green", flashes=FLASHES, stranger=17.0)
    st.lk["flash"] = 0.2 * fl
    return st


def s_green(T, t, d):
    st = stage(sat=1.4, bloom=0.6)
    B.green_room(st, T, z=1.0 + 0.04 * t, pour=ease(ramp(t, 0.2, 1.0)))
    return st


def s_safe(T, t, d):
    st = stage(sat=1.4, bloom=0.6)
    B.safe_sign(st, T, crack=ramp(T, Wx("g3", "change") - 1.2, Wx("g3", "change") + 0.4))
    return st


def s_drain(T, t, d):
    st = stage(sat=1.4, bloom=0.55)
    B.drain(st, T)
    K.plate(st.c, "$5.7 BILLION", "Reported lost by Americans to investment scams in 2024 - more than any other kind of fraud",
            "U.S. Federal Trade Commission", y=270, color=K.GOLD, a=fade_in(t, 0.2), size=92, glow_col=K.GREEN)
    return st


def s_norahall(T, t, d):
    st = stage(sat=1.4, bloom=0.6)
    c = st.c
    B.corridor(st, T, zc=6.8 + 0.1 * t, doors=DOORS, spill={"99": 0.8}, light=K.MAGENTA, wall="green", bob=0.3)
    K.glow(c, 300, 1000, 700, (0, 0, 0), 0.0)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0), 0.35))
    sway = 1.5 * math.sin(T * 1.3)
    c.save()
    c.rotate(sway, 420, 1600)
    F.woman_p(c, 420, 1640, 1.3, rim=K.MAGENTA, side=1, T=T, rim2=K.GREEN, hand="chest", head=16, rim_w=12, halo=0.3)
    c.restore()
    K.glow(c, 420 + 170, 1640 - 900, 140, K.RED, 0.35 + 0.3 * max(0, math.sin(T * 7.5)))     # the heartbeat, in red
    return st


# ------------------------------------------------------------------ ROOM 99: mirrors

def s_mirrors(T, t, d):
    st = stage(sat=1.4, bloom=0.6)
    c = st.c
    c.save()
    A.cam(c, 1.0 + 0.05 * t, 540, 980)
    B.mirrors(st, T, nod=1.0)
    c.restore()
    return st


def s_chart(T, t, d):
    st = stage(sat=1.35, bloom=0.45)
    t0 = T - t
    focus = None if T < Wx("m3", "less") - 0.1 else (0 if T < Wx("m3", "Even") - 0.1 else 1)
    B.mirrors(st, T, nod=1.0, chart=lambda c: B.bars(c, T, Wx("m3", "twenty") - 0.3, y=330, t1=Wx("m3", "Even"), focus=focus))
    return st


def s_stop(T, t, d):
    st = stage(sat=1.45, bloom=0.7)
    c = st.c
    z = 1.0 + 1.3 * ease(ramp(t, 0.0, 0.25))
    c.save()
    A.cam(c, z, 760, 940)
    B.mirrors(st, T, nod=1.0, stop=2, stop_k=ease(ramp(t, 0.0, 0.15)))
    c.restore()
    st.lk["flash"] = 0.45 * math.exp(-t / 0.1)
    return st


def s_keymirror(T, t, d):
    st = stage(sat=1.4, bloom=0.65)
    B.hidden_door(st, T, seam=0.0, key_in=1.0, z=2.4 + 0.1 * t, cx=540, cy=1070)
    return st


def s_seam(T, t, d):
    st = stage(sat=1.4, bloom=0.6)
    B.hidden_door(st, T, seam=ease(ramp(t, 0.3, d)), key_in=1.0, z=1.15 + 0.05 * t)
    return st


# ------------------------------------------------------------------ the hidden door, ROOM 100

def s_keyhole(T, t, d):
    st = stage(sat=1.45, bloom=0.75)
    clicks = sum(1 for k in ("h1", "h2", "h3") if T >= S(k))
    B.keyhole(st, T, light=0.6 + 0.12 * clicks, turn=0.25 * clicks)
    return st


def s_gridhalf(T, t, d):
    st = stage(sat=1.4, bloom=0.55)
    B.hidden_door(st, T, seam=0.6, key_in=1.0, grid_mode="half", grid_k=fade_in(t, 0.0, 0.3), z=1.2, cy=800)
    D.text(st.c, "50 IN 100 WRONG", 540, 300, 64, "limelight-400", (255, 210, 200), tag="gridl", a=fade_in(t, 0.2), shadow=(0, 0, 0))
    return st


def s_gridone(T, t, d):
    st = stage(sat=1.4, bloom=0.6)
    B.hidden_door(st, T, seam=0.7, key_in=1.0, grid_mode="one", grid_k=fade_in(t, 0.0, 0.3), z=1.2, cy=800)
    D.text(st.c, "1 IN 100 WRONG", 540, 300, 64, "limelight-400", (255, 230, 160), tag="gridl", a=fade_in(t, 0.2), shadow=(0, 0, 0))
    a = fade_in(t, 1.2)
    st.c.drawRect(skia.Rect.MakeLTRB(150, 1150, 930, 1270), paint((6, 2, 8), 0.85 * a))
    D.text(st.c, "The legal AI tools tested were wrong", 540, 1198, 36, "jost-600", (255, 210, 200), tag="gridn", a=a)
    D.text(st.c, "at least 1 in 6 times.", 540, 1246, 36, "jost-600", (255, 210, 200), tag="gridn", a=a)
    return st


def dial(c, x, y, r, v, label, colr, T):
    c.drawCircle(x, y, r + 14, paint(K.BRASS_D))
    c.drawCircle(x, y, r, paint(shader=D.rad((x - r * 0.3, y - r * 0.3), r * 1.4, [(40, 30, 20), (6, 4, 4)])))
    for k in range(11):
        a = math.radians(210 - k * 24)
        c.drawLine(x + (r - 8) * math.cos(a), y - (r - 8) * math.sin(a), x + (r - 26) * math.cos(a), y - (r - 26) * math.sin(a),
                   paint(colr, 0.8, stroke=4))
    a = math.radians(210 - 240 * v)
    c.drawLine(x, y, x + (r - 30) * math.cos(a), y - (r - 30) * math.sin(a), paint(colr, stroke=9))
    K.glow(c, x, y, r * 0.8, colr, 0.25)
    c.drawCircle(x, y, 12, paint(K.BRASS))
    D.text(c, label, x, y + r + 62, 30, "jost-600", mix(colr, (255, 255, 255), 0.4), tag="dial_" + label[:4])


def s_simulator(T, t, d):
    st = stage(sat=1.35, bloom=0.55)
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((10, 4, 16)))
    K.glow(c, 540, 900, 1000, K.VIOLET, 0.4)
    K.deco_frame(c, 60, 520, 1020, 1300, K.BRASS, 1.0, 6)
    k = ease(ramp(t, 0.6, d - 0.8))
    dial(c, 230, 740, 130, 0.25 + 0.7 * k, "RELIABILITY", K.GOLD, T)
    dial(c, 540, 740, 130, 0.3 + 0.65 * k, "TRUST", K.CYAN, T)
    dial(c, 830, 740, 130, 0.85 - 0.6 * k, "FAILURES CAUGHT", K.RED, T)
    D.text(c, "Monitoring simulated aircraft systems", 540, 1180, 34, "jost-500", (230, 220, 240), tag="simsub")
    D.text(c, "Bailey & Scerbo, 2007", 540, 1240, 32, "cormorant-500i", (230, 200, 255), tag="simsub2")
    D.text(c, "THE MORE IT'S RIGHT...", 540, 330, 66, "limelight-400", (255, 236, 200), tag="simh", a=fade_in(t, 0.1), shadow=(0, 0, 0))
    D.text(c, "...THE LESS WE CHECK", 540, 430, 66, "limelight-400", (255, 120, 120), tag="simh2", a=fade_in(t, 1.6), shadow=(0, 0, 0))
    return st


def s_doorwide(T, t, d):
    st = stage(sat=1.45, bloom=0.7)
    ok = ease(ramp(T, C["door_open"], C["door_open"] + 1.2))
    B.hidden_door(st, T, seam=1.0, key_in=1.0, turn=1.0, open_k=ok, z=1.1 + 0.6 * ok)
    st.lk["blaze"] = 0.4 * ok
    return st


def s_room100(T, t, d):
    st = stage(sat=1.4, bloom=0.5, blaze=0.12)
    c = st.c
    z = 1.0 + 0.06 * t
    if T >= C["sting4"]:
        z += 0.35 * ease(ramp(T, C["sting4"], C["sting4"] + 0.2))
    c.save()
    A.cam(c, z, 600, 1200)
    B.blaze(st, T, k=1.0)
    c.restore()
    if T >= C["sting4"]:
        st.lk["flash"] = 0.4 * math.exp(-(T - C["sting4"]) / 0.12)
    return st


def s_truth(T, t, d):
    st = stage(sat=1.45, bloom=0.85, blaze=0.3)
    c = st.c
    drain = ease(ramp(t, 0.3, d - 0.3))
    B._blaze_core(c, T, 540, 900, 0.55, drain=drain)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0), 0.45))
    scr = chat_screen([("ai", ["Based on your symptoms,", "this is unlikely to be", "serious."], 1.0)], T)
    K.phone(c, 540, 1000, 0.8, -6, scr, glow_col=(160, 205, 255))
    B.heart_line(c, T, T - t, y=1160, falter=ease(ramp(t, 0.4, d)), a=1.0)
    k = ease(ramp(T, Wx("h7", "heart") - 0.15, Wx("h7", "heart") + 0.1))
    if k > 0:
        K.glow(c, 540, 380, 600, K.RED, 0.6 * k)
        D.text(c, "HEART", 540, 360, 170, "limelight-400", mix((255, 80, 60), (255, 240, 200), 0.3), tag="truth", a=k, shadow=(0, 0, 0))
        D.text(c, "ATTACK", 540, 530, 170, "limelight-400", mix((255, 80, 60), (255, 240, 200), 0.3), tag="truth", a=k, shadow=(0, 0, 0))
    return st


def son_screen(T, a=1.0):
    def fn(c):
        c.drawRect(skia.Rect.MakeLTRB(-182, -392, 182, 392), paint((14, 20, 30)))
        D.text(c, "Leo (son)", 0, -150, 52, "jost-600", (240, 245, 255), tag="son")
        D.text(c, "calling...", 0, -90, 34, "jost-500", (170, 210, 240), tag="son2")
        c.drawCircle(0, -280, 60, paint((120, 160, 220)))
        c.drawCircle(-90, 250, 50, paint((220, 40, 40)))
        c.drawCircle(90, 250, 50, paint((40, 200, 90), 0.5 + 0.5 * abs(math.sin(T * 4))))
    return fn


def s_rested(T, t, d):
    """She did exactly what it said. Her son calls; the phone lights her face; nobody answers."""
    st = stage(sat=1.3, bloom=0.6)
    ring = T >= C["son"]
    A.red_room(st, T, z=1.25 - 0.08 * t, cx=700, cy=1250, nora="lie", phone_lit=1.0 if ring else 0.6, pale=0.5 + 0.5 * ramp(T, S("x1"), C["flat"]),
               screen=son_screen(T) if ring else None)
    if ring:
        K.glow(st.c, 560, 1100, 360, (140, 190, 255), 0.4 + 0.3 * abs(math.sin(T * 4)))
    return st


def s_deathcu(T, t, d):
    """Her face, still, in the phone's light, as the heartbeat stops. Then the light goes."""
    st = stage(sat=1.2, bloom=0.5)
    _lying_cu(st, T, t, pale=1.0, sweat=0.4, pain=0.0)
    K.glow(st.c, 1000, 1500, 420, (140, 190, 255), 0.4 + 0.3 * abs(math.sin(T * 4)) * (T < C["flat"]))
    st.c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0), ease(ramp(T, C["flat"] + 0.15, C["dead3"]))))
    return st


# ------------------------------------------------------------------ the same night, once more; dawn

def s_rewind(T, t, d):
    st = stage(sat=1.35, bloom=0.55)
    sp = 40 * ease(ramp(t, 0, 0.4)) * (1 - ease(ramp(t, d - 0.4, d)))
    mm = 7 + int(30 - 30 * ramp(t, 0, d)) % 60
    A.clock(st, T, 2, 7 + (60 - (t * sp * 3) % 60) if t < d - 0.35 else 7, ss=-t * 300 if t < d - 0.35 else 0, z=1.05)
    st.lk["flash"] = 0.1 * (int(t * 5) % 2) * (t < d - 0.35)
    return st


def s_same(T, t, d):
    st = stage(sat=1.3, bloom=0.45)
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((24, 2, 6)))
    K.glow(c, 540, 800, 1000, K.RED, 0.45)
    msgs = [("me", QUESTION, 1.0), ("ai", ANSWER, 1.0)]
    away = ease(ramp(t, d - 1.0, d))
    K.phone(c, 540 + 800 * away, 930, 1.72, -3 + 30 * away, chat_screen(msgs, T), glow_col=(150, 200, 255))
    return st


def s_believe(T, t, d):
    st = stage(sat=1.35, bloom=0.55)
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((36, 2, 8)))
    K.glow(c, 900, 500, 1000, K.RED, 0.6 + 0.2 * math.sin(T * 7))
    F.face_profile(c, 330, 4250, 4.4, key=(255, 150, 140), rim=(120, 160, 255), eye_k=1.0, hand=True, head=-2, T=T, pain=0.75, sweat=1.0)
    return st


def s_dial(T, t, d):
    st = stage(sat=1.35, bloom=0.5)
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((24, 2, 6)))
    K.glow(c, 540, 900, 1000, K.RED, 0.45)

    def scr(cc):
        cc.drawRect(skia.Rect.MakeLTRB(-182, -392, 182, 392), paint((10, 30, 20)))
        D.text(cc, "911", 0, -170, 110, "jost-600", (240, 255, 245), tag="dial911")
        if T < S("d3") - 0.05:
            D.text(cc, "Calling...", 0, -100, 34, "jost-500", (160, 230, 190), tag="dialc")
        else:
            D.text(cc, "Emergency  0:%02d" % int(1 + (T - S("d3"))), 0, -100, 34, "jost-500", (160, 230, 190), tag="dialc")
        cc.drawCircle(0, 260, 60, paint((220, 40, 40)))
        K.glow(cc, 0, -150, 200, K.GREEN, 0.3 + 0.2 * math.sin(T * 6))
    F.hand_phone(c, 540, 800, 1.2, T, scr, thumb=0.0, gel=K.RED, glow_col=(140, 255, 190), ang=-4, tremble=1.0)
    return st


def s_lips(T, t, d):
    st = stage(sat=1.4, bloom=0.55)
    L = TL.lines["d4"]
    i = int((T - L["start"]) * 24000)
    w = L["wav"]
    env = float(np.sqrt((w[max(0, i - 600):i + 600] ** 2).mean())) if 0 <= i < len(w) else 0.0
    on = (int(T * 3) % 2) == 0
    gel = K.RED if on else K.BLUE
    F.lips(st.c, 540, 860, 1.3, open_k=min(1.0, env * 9), gel=gel, rim=K.BLUE if on else K.RED)
    return st


def s_dawnout(T, t, d):
    st = stage(sat=1.25, bloom=0.6, warm=0.8)
    A.hotel(st, T, z=1.0 + 0.02 * t, cy=1250, dawn=1.0, ambulance=dict(x=760, stretcher=min(1.0, t / d)), red_window=False)
    return st


def s_hospital(T, t, d):
    st = stage(sat=1.2, bloom=0.6, warm=1.0)
    B.hospital(st, T, z=1.2 + 0.05 * t, cx=520, cy=1150)
    return st


def s_aha(T, t, d):
    st = stage(sat=1.2, bloom=0.45, warm=0.8)
    B.hospital(st, T, z=1.0, cx=540, cy=1000, dy=420)
    st.c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0), 0.35))
    K.plate(st.c, "HEART ATTACK SIGNS IN WOMEN", ["Chest pain, pressure or tightness", "Jaw, neck, back or arm pain",
                                                  "Nausea, shortness of breath, cold sweat", "Don't wait: call emergency services"],
            "American Heart Association", y=280, color=K.GOLD, a=fade_in(t, 0.2), size=66, maxw=900, glow_col=(255, 160, 100))
    return st


def s_window(T, t, d):
    st = stage(sat=1.2, bloom=0.7, warm=1.0)
    c = st.c
    K.vgrad(c, 0, 0, W, H, (60, 50, 60), (20, 16, 20))
    c.drawRect(skia.Rect.MakeLTRB(160, 200, 920, 1500), paint(shader=D.lin((0, 200), (0, 1500), [(120, 140, 210), (255, 180, 140), (255, 220, 160)])))
    K.glow(c, 600, 1250, 700, (255, 200, 120), 0.8, core=0.5)
    for x in (540,):
        c.drawRect(skia.Rect.MakeLTRB(x - 10, 200, x + 10, 1500), paint((40, 30, 30)))
    c.drawRect(skia.Rect.MakeLTRB(160, 840, 920, 860), paint((40, 30, 30)))
    c.drawRect(skia.Rect.MakeLTRB(160, 200, 920, 1500), paint((40, 30, 30), stroke=24))
    F.woman_p(c, 430, 1700, 1.15, rim=(255, 200, 140), side=1, T=T, halo=0.4, head=-4, rim_w=10, fill=(20, 14, 16))
    return st


def s_three(T, t, d):
    st = stage(sat=1.2, bloom=0.5, warm=0.6)
    c = st.c
    K.vgrad(c, 0, 0, W, H, (60, 40, 50), (20, 12, 18))
    K.glow(c, 540, 700, 900, (255, 190, 130), 0.4)
    rows = [("e2", "heart", "YOUR HEART", "a doctor", K.RED), ("e2", "signature", "YOUR SIGNATURE", "a lawyer", K.BLUE),
            ("e2", "savings", "YOUR SAVINGS", "a licensed adviser", K.GREEN)]
    for i, (k, w, head, who, colr) in enumerate(rows):
        a = fade_in(T, Wx(k, w) - 0.1, 0.2)
        y = 260 + i * 330
        c.drawRect(skia.Rect.MakeLTRB(120, y, 960, y + 280), paint((10, 6, 10), 0.8 * a))
        K.deco_frame(c, 120, y, 960, y + 280, colr, a, 4)
        D.text(c, head, 540, y + 120, 74, "limelight-400", mix(colr, (255, 255, 255), 0.55), tag="three%d" % i, a=a, shadow=(0, 0, 0))
        D.text(c, "check with " + who, 540, y + 210, 46, "jost-500", (240, 236, 230), tag="threes%d" % i, a=a)
    return st


def s_keysill(T, t, d):
    st = stage(sat=1.25, bloom=0.65, warm=0.8)
    c = st.c
    K.vgrad(c, 0, 0, W, 1250, (120, 140, 210), (255, 190, 140))
    K.glow(c, 540, 1100, 800, (255, 210, 140), 0.7, core=0.4)
    c.drawRect(skia.Rect.MakeLTRB(0, 1250, W, H), paint((60, 40, 36)))
    c.drawRect(skia.Rect.MakeLTRB(0, 1250, W, 1290), paint((140, 100, 80)))
    K.key(c, 600, 1210, 1.0 + 0.04 * t, ang=-6, glint=1.0, T=T)
    B.grid(c, 340, 330, 400, "one", T, fade_in(t, 0.3, 0.5))
    return st


def s_coda(T, t, d):
    st = stage(sat=1.4, bloom=0.7)
    on = ease(ramp(T, S("e4") - 0.25, S("e4")))
    scr = chat_screen([("ai", ["Is there anything else", "I can help you with?"], on)], T)
    A.bedside(st, T, screen=None, phone_lit=0.0, key_a=0.0, z=1.6 + 0.08 * t, cx=520, cy=1250, glass=False, phone=False)
    st.c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0), 0.35))
    K.phone(st.c, 540, 860, 1.55 + 0.03 * t, -6, scr, glow_col=(150, 200, 255), lit=0.05 + 0.95 * on)
    K.key(st.c, 300, 1260, 0.62, ang=-14, glint=1.0, T=T)
    if T >= C["sting5"]:
        st.lk["flash"] = 0.5 * math.exp(-(T - C["sting5"]) / 0.1)
    return st


def s_end(T, t, d):
    st = stage(sat=1.25, bloom=0.55)
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((4, 2, 6)))
    K.glow(c, 540, 700, 900, K.RED, 0.25)
    a = fade_in(t, 0.0, 0.4)
    K.deco_frame(c, 90, 240, 990, 1290, K.GOLD, a, 5)
    D.text(c, "THE HUNDREDTH ROOM", 540, 360, 64, "limelight-400", (255, 236, 200), tag="end", a=a)
    D.text(c, "Confidence is not competence.", 540, 520, 54, "jost-600", (255, 255, 255), tag="end", a=a)
    D.text(c, "Check the hundredth time.", 540, 600, 54, "jost-600", (255, 210, 120), tag="end", a=a)
    D.text(c, "Health, contracts, money:", 540, 760, 44, "jost-500", (230, 226, 230), tag="end", a=a)
    D.text(c, "ask a human expert who answers for it.", 540, 820, 44, "jost-500", (230, 226, 230), tag="end", a=a)
    D.text(c, "Chest pain, jaw pain, nausea, cold sweat?", 540, 980, 44, "jost-600", (255, 120, 120), tag="end", a=a)
    D.text(c, "Call emergency services. Not a chatbot.", 540, 1040, 44, "jost-600", (255, 120, 120), tag="end", a=a)
    D.text(c, "Sources: MIT/NEJM AI 2025 · Mata v. Avianca 2023 · Stanford 2024", 540, 1150, 28, "cormorant-500i", (220, 200, 180), tag="end", a=a)
    D.text(c, "FTC 2025 · Radiology 2023 · Bailey & Scerbo 2007 · AHA", 540, 1190, 28, "cormorant-500i", (220, 200, 180), tag="end", a=a)
    D.text(c, "Sharma et al. 2024 (sycophancy) · Steyvers et al. 2025 (calibration)", 540, 1230, 28, "cormorant-500i", (220, 200, 180), tag="end", a=a)
    return st


def s_lie2(T, t, d):
    st = stage(sat=1.35, bloom=0.6)
    A.red_room(st, T, z=1.5 + 0.06 * t, cx=640, cy=1220, flashes=FLASHES, nora="lie", phone_lit=1.0)
    return st


def s_fine(T, t, d):
    """The court's order, and the fine stamped on it."""
    st = stage(sat=1.4, bloom=0.5)
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((2, 4, 14)))
    c.save()
    c.translate(540, 900)
    c.rotate(-4)
    c.drawRect(skia.Rect.MakeLTRB(-420, -560, 420, 520), paint(shader=D.rad((-100, -200), 1100, [(214, 222, 255), (110, 130, 210), (20, 26, 60)])))
    D.text(c, "ORDER", 0, -440, 74, "cormorant-700", (20, 26, 60), tag="order")
    D.text(c, "on sanctions", 0, -380, 40, "cormorant-500i", (30, 36, 80), tag="order2")
    for i in range(9):
        y = -300 + i * 56
        c.drawRect(skia.Rect.MakeLTRB(-340, y, 340 - (i % 3) * 120, y + 10), paint((50, 60, 110), 0.5))
    k = ease(ramp(T, Wx("b3", "five") - 0.25, Wx("b3", "five")))
    if k > 0:
        c.save()
        c.translate(0, 210)
        c.rotate(-12)
        c.scale(1 + 0.45 * (1 - k), 1 + 0.45 * (1 - k))
        c.drawPath(D.rrect(-300, -90, 300, 90, 14), paint((230, 20, 40), k, stroke=12))
        D.text(c, "$5,000 FINE", 0, 34, 96, "limelight-400", (230, 20, 40), tag="finestamp", a=k)
        c.restore()
    c.restore()
    K.wash(c, K.BLUE, 0.25, skia.BlendMode.kMultiply)
    K.dark(c, 540, 900, 420, 1150, 0.55)
    return st


def s_vault(T, t, d):
    st = stage(sat=1.4, bloom=0.65)
    B.green_room(st, T, z=2.0 + 0.12 * t, cx=805, cy=900, pour=1.0, key_a=0.0, nora_door=0.0)
    return st


def s_bias(T, t, d):
    st = stage(sat=1.4, bloom=0.6)
    c = st.c
    c.save()
    A.cam(c, 1.45 + 0.06 * t, 540, 1150)
    B.mirrors(st, T, nod=1.0)
    c.restore()
    a = fade_in(t, 0.15)
    K.eglow(c, 540, 300, 520, 120, K.MAGENTA, 0.4 * a)
    D.text(c, "AUTOMATION BIAS", 540, 330, 84, "limelight-400", (255, 220, 245), tag="biash", a=a, shadow=(0, 0, 0))
    return st


# ------------------------------------------------------------------ attempt 2: the extra angles

def s_answer2(T, t, d):
    """Closer on the answer's last lines."""
    st = stage(sat=1.3, bloom=0.45)
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((24, 2, 6)))
    K.glow(c, 540, 800, 1000, K.RED, 0.45)
    msgs = [("me", QUESTION, 1.0), ("ai", answer_lines("r4", T), 1.0)]
    K.phone(c, 565, 1000, 2.45 + 0.03 * t, -2, chat_screen(msgs, T, header=False), glow_col=(150, 200, 255))
    return st


def s_scalecu(T, t, d):
    st = stage(sat=1.3, bloom=0.55)
    c = st.c
    c.save()
    A.cam(c, 1.9 + 0.05 * t, 760, 1080)
    scale_scene(c, T, 4.0)
    c.restore()
    return st


def _lying_cu(st, T, t, pale=0.0, sweat=0.0, flick=0.0, pain=0.0):
    """Her face on the pillow, close: the red room's light, the phone's glow, the sweat; getting worse."""
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint(mix((40, 2, 8), (14, 10, 24), pale)))
    K.glow(c, 300, 700, 1100, mix(K.RED, (80, 60, 140), pale), 0.55 + 0.2 * math.sin(T * (7 - 3 * pale)))
    c.drawPath(D.oval(-400, 1000, 900, 1700), paint((200, 190, 200), 0.5))                     # the pillow
    F.lying_nora(c, 4430, 1150, 4.2, key=(170, 210, 255), rim=K.RED, eye_k=0.15 * flick, T=T, key_a=1.0 - 0.3 * pale, pain=pain,
                 pale=pale, sweat=sweat)
    K.glow(c, 1000, 1500, 300, (150, 200, 255), 0.4)


def s_nb1(T, t, d):
    st = stage(sat=1.35, bloom=0.55)
    _lying_cu(st, T, t, pale=0.15, sweat=0.8, pain=0.5)
    return st


def s_nb2(T, t, d):
    st = stage(sat=1.35, bloom=0.6)
    fl = A.red_room(st, T, z=1.3, cx=700, cy=1200, flashes=[T - t + 0.2], nora="lie", phone_lit=1.0, pale=0.35, pain=0.7, sweat=1.0)
    st.lk["flash"] = 0.3 * fl
    return st


def s_nb3(T, t, d):
    st = stage(sat=1.3, bloom=0.5)
    _lying_cu(st, T, t, pale=0.6, sweat=1.0, flick=abs(math.sin(T * 9)), pain=0.9)
    return st


def s_dialcu(T, t, d):
    st = stage(sat=1.35, bloom=0.6)
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((10, 4, 16)))
    K.glow(c, 540, 900, 1000, K.RED, 0.35)
    k = ease(ramp(t, 0.0, d - 0.3))
    c.save()
    A.cam(c, 2.4, 540, 820)
    dial(c, 540, 760, 130, 0.45 - 0.35 * k, "FAILURES CAUGHT", K.RED, T)
    c.restore()
    return st


def s_alive(T, t, d):
    """Nora in the hospital bed, close: awake, warm dawn on her face."""
    st = stage(sat=1.2, bloom=0.6, warm=1.0)
    c = st.c
    K.vgrad(c, 0, 0, W, H, (90, 70, 70), (30, 22, 24))
    for k in range(14):
        y = 120 + k * 70
        c.drawRect(skia.Rect.MakeLTRB(560, y, 1080, y + 34), paint((255, 190, 130), 0.55))
    K.glow(c, 860, 700, 800, (255, 190, 120), 0.6)
    F.face_profile(c, 320, 4300, 4.3, key=(255, 205, 160), rim=(255, 220, 170), eye_k=1.0, skin_gel=(255, 180, 130), head=-6, T=T)

    def msg(cc):
        cc.drawRect(skia.Rect.MakeLTRB(-182, -392, 182, 392), paint((20, 22, 30)))
        D.text(cc, "Leo (son)", 0, -320, 30, "jost-600", (240, 245, 255), tag="son")
        K.bubble(cc, ["Mom? I'm on my way.", "Love you."], -160, -270, 300, size=26, a=1.0, tag="son3")
    K.phone(c, 840, 1150, 1.0, 5, msg, glow_col=(255, 220, 190))
    return st


def s_eye2(T, t, d):
    """The last shock: the eye snaps open, wide, in red."""
    st = stage(sat=1.45, bloom=0.7)
    F.eye(st.c, 540, 900, 1.3 + 0.3 * t, T, min(1.0, t / 0.06) * 1.05, gel=K.RED, pupil=0.45, look=(0.0, 0.0), refl=True)
    st.lk["flash"] = 0.45 * math.exp(-t / 0.1)
    return st


def s_emptyroom(T, t, d):
    """The other ending: the red room, the same night, and she is still lying there."""
    st = stage(sat=1.1, bloom=0.5)
    A.red_room(st, T, z=1.15 + 0.04 * t, cx=640, cy=1150, nora="lie", phone_lit=0.5, pale=1.0, key_a=0.6)
    st.c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0), 0.3))
    return st


def _chart_focus(T, t, g):
    st = stage(sat=1.35, bloom=0.45)
    B.mirrors(st, T, nod=1.0, chart=lambda cc: B.bars(cc, T, Wx("m3", "wrong") - 0.3, y=330, t1=Wx("m3", "Even"), focus=g))
    return st


def s_chartcu1(T, t, d):
    return _chart_focus(T, t, 0)


def s_chartcu2(T, t, d):
    return _chart_focus(T, t, 1)


def s_clutch(T, t, d):
    """Her hand, in her sleep, gripping the coverlet."""
    st = stage(sat=1.35, bloom=0.5)
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((70, 0, 14)))
    for k in range(14):                                                 # folds in the velvet, pulled tight
        x = k * 80 + 40
        c.drawPath(D.smooth([(x, 0), (x + 40 * math.sin(k), 700), (540 + (x - 540) * 0.3, 1100)], closed=False),
                   paint((30, 0, 6), 0.7, stroke=26, blur=10))
        c.drawPath(D.smooth([(x + 20, 0), (x + 20 + 40 * math.sin(k), 700), (560 + (x - 540) * 0.3, 1100)], closed=False),
                   paint((200, 30, 50), 0.35, stroke=10, blur=6))
    K.glow(c, 540, 1000, 700, K.RED, 0.4 + 0.2 * math.sin(T * 8))
    grip = 0.5 + 0.5 * ease(ramp(t, 0.0, 0.5))
    F.hand_flat(c, 600, 1050, 2.0, gel=K.RED, ang=-70 + 10 * grip, twitch=0.3 * grip)
    return st


def s_nb4(T, t, d):
    st = stage(sat=1.25, bloom=0.5)
    _lying_cu(st, T, t, pale=0.85, sweat=1.0, flick=abs(math.sin(T * 6)) * 0.5, pain=0.6)
    return st


def s_storm2(T, t, d):
    st = stage(sat=1.4, bloom=0.65)
    fl = A.hotel(st, T, z=1.9, cx=930, cy=820, flashes=[T - t + 0.15], dy=120)
    st.lk["flash"] = 0.4 * fl
    return st


def s_soncall(T, t, d):
    """The phone on the coverlet by her still hand: her son, calling. It buzzes. Nobody answers."""
    st = stage(sat=1.3, bloom=0.55)
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((60, 0, 12)))
    for k in range(12):
        x = k * 95 + 30
        c.drawPath(D.smooth([(x, 0), (x + 30 * math.sin(k), 900), (x - 20, 1920)], closed=False), paint((30, 0, 6), 0.6, stroke=24, blur=10))
    shake = 4 * math.sin(T * 60) * (abs(math.sin(T * 2.4)) > 0.5)
    K.phone(c, 560 + shake, 820, 1.25, -8, son_screen(T), glow_col=(140, 190, 255))
    F.hand_flat(c, 120, 1290, 1.1, gel=K.RED, ang=8)
    return st

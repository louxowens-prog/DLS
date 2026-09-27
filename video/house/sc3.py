"""Scenes 3: make it personal. A true case (bromism after asking a chatbot about salt), told as if it were you."""
import math

import numpy as np
import skia

import cast
import hx
import kit
from cues import C, count
from hx import BLOOD, CREAM, GOLD, INK, MINT, PEACH, PINK, PLUM, POWDER, W, H, bez, ease, paint, path, ramp, stop
from timeline import TL

S, E, Wd = TL.s, TL.e, TL.word


def s_mirror(T, t, d):
    """'Imagine it's you': a gilt mirror in the parlour, and in it, you."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "parlor")
    cast.cuckoo_clock(c, 165, 600, 0.52, T, count(T))
    cx, cy, rx, ry = 610, 760, 270, 400
    c.drawOval(skia.Rect.MakeLTRB(cx - rx - 40, cy - ry - 40, cx + rx + 40, cy + ry + 40), paint((200, 150, 60)))
    for i in range(24):                                              # carved gilt beads
        a = i * 2 * math.pi / 24
        c.drawCircle(cx + (rx + 30) * math.cos(a), cy + (ry + 30) * math.sin(a), 16, paint((240, 200, 90)))
    mirror = path(hx.ellipse(cx, cy, rx, ry))
    c.save()
    c.clipPath(mirror, doAntiAlias=True)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(shader=hx.lin((cx - rx, cy - ry), (cx + rx, cy + ry), [(210, 220, 235), (160, 170, 190), (220, 226, 236)])))
    k = ease(ramp(t, 0.6, 1.6))
    cast.you(c, cx, cy - 120 + 60 * (1 - k), 0.58, T, pose="stand")
    c.drawPath(path([(cx - 200, cy - 300), (cx - 120, cy - 330), (cx + 180, cy + 300), (cx + 100, cy + 330)]), paint(WHITE_, 0.18))
    c.restore()
    cast.cat(c, 175, 1260, 0.52, T, eyes="gold")
    kit.sticker(c, "heart", 900, 1250, 0.6, T, T - t + 0.9, rot=10)
    hx.soft_focus(st.arr, 0.85, bloom=0.5)
    return st.arr


WHITE_ = (255, 255, 255)


def s_kitchen(T, t, d):
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "kitchen")
    cast.shaker(c, 820, 1210, 0.8, T)
    if T >= Wd("p2", "salt") - 0.05:                                  # 'salt is bad for you': a pencil scribble over it
        hx.scribble(c, 820, 1150, 110, T, seed=2, color=BLOOD, w=7)
    cast.cuckoo_clock(c, 830, 590, 0.5, T, count(T))
    cast.you(c, 330, 700, 0.78, T, pose="phone")
    cast.cat(c, 560, 1290, 0.42, T, eyes="gold")
    hx.soft_focus(st.arr, 0.85, bloom=0.5)
    return st.arr


QUESTION = "What can I replace chloride with?"
ANSWER = "You can replace chloride with bromide! Context matters. ✨"


def s_typing(T, t, d):
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "kitchen")
    n = int(len(QUESTION) * ease(ramp(t, 0.15, 1.6)))
    typed = QUESTION[:n] + ("|" if int(stop(T, 4) * 4) % 2 == 0 and n < len(QUESTION) else "")
    cast.phone(c, 540, 860, 1.25, T, lines=[(typed or " ", "you")])
    kit.dramatized(c, 540, 290, T)
    hx.soft_focus(st.arr, 0.45)
    return st.arr


def s_answer(T, t, d):
    """The reply lands, sweet as candy, and the chatbot's face smiles out over the phone."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "kitchen")
    ans = ANSWER.replace(" ✨", "")
    shown = ans if T >= S("p3") + 0.15 else ""
    lines = [(QUESTION, "you")] + ([(shown, "ai")] if shown else [])
    cast.phone(c, 540, 1000, 1.18, T, lines=lines)
    cast.helper(c, 540, 470, 0.72, T, talk=kit.ai_talk(T), mood="sweet")
    for i in range(5):
        hx.sparkle(c, 200 + i * 170, 1320 - (i % 2) * 40, 26, T, seed=i + 20)
    kit.dramatized(c, 830, 290, T)
    hx.soft_focus(st.arr, 0.5)
    return st.arr


def s_cateyes(T, t, d):
    st = hx.Stage((10, 4, 10))
    c = st.c
    cast.cat(c, 540, 1000, 2.6, T, eyes="red", fringe=False)
    hx.horror(st.arr, 0.5)
    return st.arr


def s_nowarning(T, t, d):
    """Freeze frame on the chat. Where a warning should be: nothing. Silence."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "kitchen")
    Tf = S("p3") + 1.0
    n0 = len(hx.TEXT)
    cast.phone(c, 540, 850, 1.12, Tf, lines=[(QUESTION, "you"), (ANSWER.replace(" ✨", ""), "ai")])
    y0 = max(b[3] for b in hx.TEXT[n0:]) + 34                        # just under the reply
    y1 = y0 + 110
    # the empty space where a warning should have been: a dashed pencil outline around nothing
    rng = np.random.default_rng(6)
    for i in range(18):
        x0 = 330 + 420 * i / 18
        c.drawLine(x0, y0, x0 + 14, y0 + rng.uniform(-2, 2), paint(BLOOD, 0.8, stroke=5))
        c.drawLine(x0, y1, x0 + 14, y1 + rng.uniform(-2, 2), paint(BLOOD, 0.8, stroke=5))
    for yy in range(int(y0), int(y1), 28):
        c.drawLine(330, yy, 330, yy + 14, paint(BLOOD, 0.8, stroke=5))
        c.drawLine(764, yy, 764, yy + 14, paint(BLOOD, 0.8, stroke=5))
    ym = (y0 + y1) / 2
    c.drawPath(path([(547, ym - 40), (507, ym + 38), (587, ym + 38)]), paint(BLOOD, 0.8, stroke=6))
    c.drawLine(547, ym - 16, 547, ym + 14, paint(BLOOD, 0.8, stroke=6))
    c.drawCircle(547, ym + 27, 4, paint(BLOOD, 0.8))
    hx.reg(330, y0, 764, y1, "warnbox")
    kit.dramatized(c, 540, 330, Tf)
    if t < 2 / 24:
        c.drawRect(skia.Rect.MakeWH(W, H), paint(CREAM, 0.8))
    hx.freeze_look(st.arr, 1.0)
    return st.arr


def s_parcel(T, t, d):
    """Sped up: the parcel lands on the step, pops open, and out comes the jar - sweet as a present."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "parlor")
    cast.cuckoo_clock(c, 170, 1120, 0.42, T, count(T))
    tt = stop(t, 8) * 2.5
    drop = min(1.0, tt / 0.8)
    by = -300 + 1500 * drop
    with hx.figure(c) as F:
        F.rrect(330, by - 180, 750, by + 120, 12, (200, 150, 100))
    c.drawRect(skia.Rect.MakeLTRB(520, by - 180, 560, by + 120), paint((230, 200, 140)))
    if tt > 1.2:
        k = hx.pop(t, 1.2 / 2.5, 0.2, 0.35)
        c.save()
        c.translate(540, 820)
        c.scale(k, k)
        c.translate(-540, -820)
        cast.jar(c, 540, 820, 1.1, T)
        c.restore()
        for i in range(8):
            a = i * 2 * math.pi / 8 + stop(T, 8)
            hx.sparkle(c, 540 + 340 * math.cos(a), 820 + 300 * math.sin(a), 34, T, seed=i)
    hx.soft_focus(st.arr, 0.55)
    return st.arr


def s_sprinkle(T, t, d):
    """Every meal: the shaker (bromide now) tipped over the eggs, shaken in jerky stop-motion."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "kitchen")
    with hx.figure(c) as F:
        F.oval(180, 1080, 900, 1260, WHITE_)
    c.drawOval(skia.Rect.MakeLTRB(180, 1080, 900, 1260), paint((255, 150, 190), stroke=16))
    for ex in (420, 660):                                              # two sunny eggs
        c.drawOval(skia.Rect.MakeLTRB(ex - 110, 1110, ex + 110, 1230), paint((255, 252, 240)))
        c.drawCircle(ex, 1168, 40, paint((255, 190, 40)))
    sh = math.sin(stop(T, 12) * 30) * 22
    c.save()
    c.translate(560 + sh, 700)
    c.rotate(160)
    cast.shaker(c, 0, 0, 0.95, T, label="NaBr")
    c.restore()
    rng = np.random.default_rng(int(stop(T, 12) * 12))
    for _ in range(60):
        x, y = 560 + sh + rng.normal(0, 55), rng.uniform(860, 1180)
        c.drawCircle(x, y, rng.uniform(4, 8), paint((250, 250, 255)))
        c.drawCircle(x, y, rng.uniform(4, 8), paint((120, 120, 140), stroke=1.5))
    hx.soft_focus(st.arr, 0.5)
    return st.arr


def s_calendar(T, t, d):
    """Every day. For three months: the calendar pages fly off, sped up."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "kitchen")
    day = 1 + int(89 * min(1.0, stop(t, 12) / max(0.1, 0.7 * d)))
    with hx.figure(c) as F:
        F.rrect(250, 360, 830, 1180, 14, WHITE_)
        F.rrect(250, 360, 830, 520, 14, BLOOD)
    hx.text(c, "DAY", 540, 480, 90, "shrikhand-400", CREAM, tag="calendar")
    hx.text(c, str(day), 540, 950, 330, "shrikhand-400", PLUM, tag="calendar")
    if day >= 90:
        kit.stamp(c, "3 MONTHS", 540, 1110, 70, T, T - t + 0.7 * d, color=BLOOD, rot=-8, tag="stamp")
    for i in range(3):                                                # pages flying away
        a = stop(T, 12) * 9 + i * 2.1
        c.save()
        c.translate(540 + 420 * math.cos(a), 700 + 300 * math.sin(a) - 200 * i)
        c.rotate(math.degrees(a))
        c.drawRect(skia.Rect.MakeLTRB(-120, -150, 120, 150), paint(WHITE_, 0.9))
        c.restore()
    hx.soft_focus(st.arr, 0.35)
    return st.arr


def s_bed(T, t, d):
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "bedroom")
    c.save()
    c.translate(540, 1110)
    c.rotate(-90)
    cast.you(c, 0, -330, 0.62, T, pose="stand")
    c.restore()
    c.drawRect(skia.Rect.MakeLTRB(80, 1130, 1000, 1460), paint((255, 150, 190)))      # the blanket over the doll
    cast.cuckoo_clock(c, 860, 520, 0.45, T, count(T))
    with hx.layer(c, 0.22):
        cast.helper(c, 480, 640, 1.6, T, mood="eerie", halo=False, fringe=False, look=(0.3, 0.5))
    hx.soft_focus(st.arr, 0.3)
    return st.arr


def s_skin(T, t, d):
    """Close: the skin breaking out; the mirror blushes red."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "bedroom")
    k = ramp(t, 0.1, 0.8)
    cast.you(c, 540, 700, 1.4, T, pose="clutch", spots=k, mirror_red=t > 0.6, shake=0.3)
    hx.soft_focus(st.arr, 0.15)
    hx.horror(st.arr, 0.25 * k)
    return st.arr


def s_neighbor(T, t, d):
    """Hard cut: the window across the street, and a face in it. The shaker on the sill grows teeth."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "street")
    cast.neighbor(c, 540, 960, 1.0, T, mood="horror")
    c.drawRect(skia.Rect.MakeLTRB(0, 1240, W, 1320), paint((80, 60, 70)))           # our windowsill
    cast.shaker(c, 820, 1110, 0.8, T, label="NaBr", teeth=ease(ramp(t, 0.3, 1.2)))
    cast.cat(c, 230, 1150, 0.6, T, eyes="red", pose="hiss")
    kit.top_drips(c, T, grow=0.6)
    hx.horror(st.arr, 0.9)
    return st.arr


def s_visions(T, t, d):
    """You see things. You hear things: floating heads multiplying, the walls grow eyes, the floor floods red."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "kitchen")
    rng = np.random.default_rng(3)
    for i in range(10):                                               # eyes opening in the tiles
        x, y = rng.uniform(80, 1000), rng.uniform(260, 1100)
        o = ramp(t, i * 0.08, i * 0.08 + 0.3)
        c.drawOval(skia.Rect.MakeLTRB(x - 50, y - 26 * o, x + 50, y + 26 * o), paint(WHITE_))
        c.drawCircle(x + 10 * math.sin(stop(T, 8) * 5 + i), y, 14 * o, paint(BLOOD))
    tr = d - t if T >= C["hear"] else t                                # reverse motion on 'hear': the heads fly back
    for i in range(6):
        a = i * 2 * math.pi / 6 + stop(tr, 8) * 1.5
        r = 300 + 90 * math.sin(stop(tr, 8) * 3 + i)
        if i % 2:
            cast.helper(c, 540 + r * math.cos(a), 760 + r * math.sin(a) * 0.9, 0.42, T + i, mood="horror", fringe=False)
        else:
            cast.neighbor(c, 540 + r * math.cos(a), 760 + r * math.sin(a) * 0.9, 0.45, T + i, mood="horror")
    cast.you(c, 540, 820, 0.8, T, pose="clutch", shake=1.0, mirror_red=True)
    hx.horror(st.arr, 1.0)
    kit.flood(c, 380 + 420 * ease(ramp(t, 0, d)), T, color=(225, 0, 25))
    for i in range(4):
        hx.flame(c, 160 + i * 250, H - 380 - 420 * ease(ramp(t, 0, d)) + 30, 230, T, seed=i)
    hx.scribble(c, 540, 700, 200, T, seed=7, color=INK, w=7, a=0.8)
    return st.arr


def s_run(T, t, d):
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "hospital")
    k = ease(ramp(stop(t, 8) * 2, 0, 1.6))
    s = 0.95 - 0.55 * k
    cast.you(c, 540, 760 + 200 * (1 - k), s, T * 2.5, pose="run")
    hx.horror(st.arr, 0.9)
    kit.flood(c, 120 + 160 * ramp(t, 0, d), T, color=(225, 0, 25))
    return st.arr


def _hold(T, t, d, zoom=0.35, flood=260.0):
    """The door with the little barred window. You are held. The camera creeps in on the bars; the floor floods."""
    st = hx.Stage()
    c = st.c
    z = 1 + zoom * ease(ramp(stop(t, 8), 0.2, d))
    c.save()
    c.translate(540, 560)
    c.scale(z, z)
    c.translate(-540, -560)
    kit.backdrop(st, "hospital")
    with hx.figure(c) as F:
        F.rrect(190, 260, 890, 1320, 16, (186, 176, 172))                 # a dull institutional door: the grade turns it blood red
        F.rrect(380, 420, 700, 700, 10, (40, 30, 40))
    for k in range(3):
        c.drawRect(skia.Rect.MakeLTRB(240, 800 + k * 160, 840, 810 + k * 160), paint((150, 140, 138)))
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(380, 420, 700, 700))
    cast.you(c, 540, 620, 0.55, T, pose="clutch", shake=0.6, mirror_red=True)
    c.restore()
    for k in range(5):
        c.drawLine(410 + k * 64, 420, 410 + k * 64, 700, paint((70, 70, 80), stroke=14))
    c.drawCircle(800, 900, 26, paint((70, 70, 80)))
    c.restore()
    hx.horror(st.arr, 0.95)
    if t < 0.12:
        c.drawRect(skia.Rect.MakeWH(W, H), paint(CREAM, 0.6 * (1 - ramp(t, 0.0, 0.08))))
    kit.flood(c, flood * ease(ramp(t, 0.3, d)), T, color=(225, 0, 25))
    return st.arr


def s_hold(T, t, d):
    return _hold(T, t, d)


def s_cold2(T, t, d):
    """Cold open, 2: three months later - the barred door slams."""
    return _hold(T, t, d, zoom=0.25, flood=200.0)


def s_cold1(T, t, d):
    """Cold open, 1: the chat reply, glowing on a phone in a red kitchen. The cat already knows."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "kitchen")
    cast.phone(c, 540, 860, 1.25, T, lines=[(QUESTION, "you"), (ANSWER.replace(" ✨", ""), "ai")])
    cast.cat(c, 170, 1260, 0.5, T, eyes="red", pose="hiss")
    kit.top_drips(c, T, grow=0.4 + 0.6 * t)
    hx.horror(st.arr, 0.85)
    kit.dramatized(c, 540, 290, T)
    return st.arr


def s_doctor(T, t, d):
    """The doctor, and the chart: the normal range is a sliver; yours goes off the top."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "hospital")
    cast.doctor(c, 300, 560, 0.85, T, talk=kit.doc_talk(T))
    with hx.figure(c) as F:
        F.rrect(560, 300, 1000, 1240, 14, (252, 250, 240))
    hx.text(c, "BROMIDE", 780, 390, 58, "fell-sc-400", INK, tag="chart")
    base = 1110
    c.drawLine(600, base, 960, base, paint(INK, stroke=5))
    c.drawRect(skia.Rect.MakeLTRB(600, base - 8, 700, base), paint((60, 170, 90)))
    hx.text(c, "normal: up to 7.3 mg/L", 760, base + 60, 30, "special-elite-400", INK, tag="chart")
    k = ease(ramp(T, C["level"] - 0.3, C["level"] + 0.8))
    top = base - (base - 470) * k
    c.drawRect(skia.Rect.MakeLTRB(830, top, 950, base), paint(BLOOD))
    if k >= 1:
        for i in range(3):
            hx.flame(c, 860 + i * 40, 480, 120, T, seed=i)
        hx.text(c, "yours:", 700, 640, 44, "fell-400-italic", BLOOD, tag="chart")
        hx.text(c, "1,700", 700, 710, 56, "shrikhand-400", BLOOD, tag="chart")
        hx.text(c, "mg/L", 700, 766, 38, "special-elite-400", BLOOD, tag="chart")
    hx.horror(st.arr, 0.3 * k)
    return st.arr


def s_weeks(T, t, d):
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "hospital")
    with hx.figure(c) as F:
        F.rrect(140, 380, 940, 1160, 14, WHITE_)
    hx.text(c, "WEEK 1 · 2 · 3", 540, 470, 56, "fell-sc-400", INK, tag="calendar")
    n = int(21 * ease(ramp(t, 0.05, d - 0.2)))
    for i in range(21):
        r, q = divmod(i, 7)
        x, y = 190 + q * 104, 540 + r * 200
        c.drawRect(skia.Rect.MakeLTRB(x, y, x + 90, y + 170), paint(INK, 0.5, stroke=3))
        if i < n:
            c.drawLine(x + 10, y + 10, x + 80, y + 160, paint(BLOOD, stroke=10))
            c.drawLine(x + 80, y + 10, x + 10, y + 160, paint(BLOOD, stroke=10))
    hx.horror(st.arr, 0.3)
    return st.arr


DOC_Q = "What can chloride be replaced with?"
DOC_A = "Chloride can be replaced with bromide... context matters."


def s_doctest(T, t, d):
    """His doctors asked the chatbot themselves: it offered bromide too, and no health warning."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "hospital")
    f = hx.font("special-elite-400", 38)
    lab = "HIS DOCTORS' OWN TEST (paraphrased)"
    w = f.measureText(lab)
    c.drawRect(skia.Rect.MakeLTRB(540 - w / 2 - 24, 262, 540 + w / 2 + 24, 330), paint(INK, 0.9))
    c.drawRect(skia.Rect.MakeLTRB(540 - w / 2 - 24, 262, 540 + w / 2 + 24, 330), paint(CREAM, stroke=3))
    hx.text(c, lab, 540, 310, 38, "special-elite-400", CREAM, tag="label")
    lines = [(DOC_Q, "you")]
    if T >= Wd("p12", "asked") + 0.3:
        lines.append((DOC_A, "ai"))
    n0 = len(hx.TEXT)
    cast.phone(c, 540, 870, 1.08, T, lines=lines)
    red = T >= Wd("p12", "bromide")
    if red:
        ai = [b for b in hx.TEXT[n0:] if b[0] < 420]                     # the reply's lines (left-aligned bubble)
        x0, y0 = min(b[0] for b in ai), min(b[1] for b in ai)
        x1, y1 = max(b[2] for b in ai), max(b[3] for b in ai)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        c.drawPath(hx.path(hx.ellipse(cx, cy, (x1 - x0) / 2 * 1.5 + 10, (y1 - y0) / 2 * 1.5 + 10), closed=True),
                   paint(BLOOD, stroke=9))
    cast.cat(c, 175, 1270, 0.45, T, eyes="red" if red else "gold")
    cast.helper(c, 860, 1230, 0.36, T, mood="horror" if red else "sweet", halo=not red, look=(-0.6, -0.4))
    if red:
        hx.horror(st.arr, 0.3)
    else:
        hx.soft_focus(st.arr, 0.3)
    return st.arr


def s_realcase(T, t, d):
    return hx.title_card(["A REAL CASE."], size=112, y_center=840)


def _journal(c, x, y, s, T):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    with hx.figure(c) as F:
        F.rrect(-360, -440, 360, 440, 6, (252, 250, 244))
    c.drawRect(skia.Rect.MakeLTRB(-360, -440, 360, -350), paint((150, 30, 40)))
    hx.text(c, "Annals of Internal Medicine: Clinical Cases", 0, -382, 30, "fell-400-italic", CREAM, tag="journal")
    for j, ln in enumerate(("A Case of Bromism", "Influenced by Use of", "Artificial Intelligence")):
        hx.text(c, ln, 0, -250 + j * 80, 56, "fell-400", INK, tag="journal")
    hx.text(c, "August 2025 · case report", 0, 30, 34, "special-elite-400", INK, tag="journal")
    for k in range(9):
        c.drawRect(skia.Rect.MakeLTRB(-300, 60 + k * 36, 300 - (k * 41) % 90, 70 + k * 36), paint(INK, 0.45))
    c.restore()


def s_casefile(T, t, d):
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "album_page", 2)
    hx.photo(c, kit.mini("medical"), 820, 1080, 300, 230, rot=6)
    k = hx.pop(T, T - t, 0.2, 0.15)
    c.save()
    c.translate(460, 720)
    c.rotate(-3)
    c.scale(k * 0.95, k * 0.95)
    _journal(c, 0, 0, 1.0, T)
    c.restore()
    cast.cat(c, 560, 1290, 0.42, T, eyes="gold")
    hx.soft_focus(st.arr, 0.3)
    return st.arr


def s_casezoom(T, t, d):
    """Freeze: push in on the published page."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "album_page", 2)
    z = 1.22
    c.save()
    c.translate(540, 800)
    c.scale(z, z)
    _journal(c, 0, 0, 1.0, T)
    c.restore()
    if t < 2 / 24:
        c.drawRect(skia.Rect.MakeWH(W, H), paint(CREAM, 0.7))
    hx.freeze_look(st.arr, 0.7)
    return st.arr

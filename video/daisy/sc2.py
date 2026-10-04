"""Chapter 3, THE GOLD MEDAL CLOCK, the banquet and the epilogue: a medal for the Oracle; 'What time is it?'; the
clock scores; proofs yes, clocks no; the butterfly room and its jagged edge; agents and robots; the feast, the food
fight, the silence; putting things back; the dedication; the last joke."""
import math

import numpy as np
import skia

import collage as CL
import common as C
import duo as D
import kit as K
import props as PR
import sets as SE
from common import E, S, Wx, typed
from kit import INK, WHITE, H, W, ease, mix, paint, path, ramp
from sc0 import chain, refrain


def s_c_card(T, idx):
    st = K.Stage()
    C.chapter_card(st.c, T, E("b11") + 0.1, 3, "THE GOLD MEDAL CLOCK")
    return st.arr


def s_c_medal(T, idx):
    """'In 2025, AI reached gold-medal level at the International Mathematical Olympiad.' A podium, a ribbon, a medal
    pinned on the Oracle, confetti; the duo clap like clockwork."""
    st = K.Stage()
    c = st.c
    SE.salon(c, T, wall=(176, 30, 54), wall2=(214, 168, 40), dots=False)
    t_pin = Wx("c1", "gold") - 0.15
    CL.paper(c, CL.rect_pts(330, 1380, 750, 1640), (250, 244, 228), seed=4)          # the podium
    for i in range(12):                                                  # a rosette on the podium
        a = i / 12 * 2 * math.pi
        c.drawCircle(540 + 34 * math.cos(a), 1560 + 34 * math.sin(a), 22, paint((176, 30, 54)))
    c.drawCircle(540, 1560, 30, paint((250, 196, 30)))
    PR.oracle(c, 540, 1390, 0.7, T, medal=T > t_pin, look=(0, -0.2) if T < t_pin else (0, 0.4))
    keys = [(S("c1") - 0.1, "stand")] + [(S("c1") + 0.3 + i * 0.5, "clap" if i % 2 else "hold") for i in range(10)]
    C.girl(c, "zuza", 160, 1860, 0.56, T, keys, mood="deadpan")
    C.girl(c, "lili", 920, 1860, 0.56, T, keys[:1] + [(t_pin - 0.3, dict(sL=100, eL=30)), (t_pin + 0.4, "up")], mood="delight")
    C.label(c, "MATH OLYMPIAD 2025", 540, 330, 56, colr=(250, 244, 228), paper=(40, 80, 150), rot=-2)
    if T > t_pin:
        C.label(c, "GOLD-MEDAL LEVEL", 540, 470, 56, paper=(250, 196, 30), rot=2)
        CL.scraps(c, T, t_pin, seed=5, n=40, area=(0, 200, W, 1500), fall=380)
    return st.arr


def s_c_clock(T, idx):
    """'What time is it?' Zuza holds up a clock: ten past ten."""
    st = K.Stage()
    c = st.c
    SE.salon(c, T, dots=False)
    C.girl(c, "zuza", 540, 2700, 1.35, T, [(S("c2") - 0.1, "stand"), (S("c2"), "hold")], mood="deadpan")
    PR.clock(c, 540, 1140, 230, 10, 10)
    return st.arr


def s_c_tuesday(T, idx):
    """'Approximately... Tuesday.' The medallist, close, typing its answer."""
    st = K.Stage()
    c = st.c
    SE.salon(c, T, y_floor=1340, wall=(176, 30, 54), wall2=(214, 168, 40), dots=False)
    k = ramp(T, S("c3"), E("c3"))
    PR.oracle(c, 540, 1350, 0.85, T, medal=True, strip=[typed("APPROXIMATELY...", ramp(k, 0, 0.6)), typed("TUESDAY.", ramp(k, 0.7, 1))],
              look=(0.3, -0.3), mouth=C.talk(T, "MACH") * 0.6)
    PR.clock(c, 880, 420, 110, 10, 10)
    return st.arr


def s_c_score(T, idx):
    """'Reading analog clocks? The best AI scored 50.6%. Humans: 90.1%.' Two paper bars."""
    st = K.Stage()
    c = st.c
    SE.void(c, (230, 222, 204), seed=7)
    C.label(c, "CLOCKBENCH  (AI INDEX 2026)", 540, 330, 44, fname="special-elite-400", rot=-1)
    base = 1250
    for j, (lab, val, colr, tw) in enumerate((("BEST AI", 50.6, (176, 30, 54), Wx("c4", "best")), ("HUMANS", 90.1, (40, 80, 150), Wx("c4", "Humans")))):
        if T < tw - 0.2:
            continue
        u = ease(ramp(T, tw - 0.2, tw + 0.5))
        x0 = 170 + j * 420
        hgt = 760 * val / 100 * u
        CL.paper(c, CL.rect_pts(x0, base - hgt, x0 + 280, base), colr, seed=j + 1)
        f = K.font("abril-400", 72)
        s_ = f"{val * u:.1f}%"
        c.drawString(s_, x0 + 140 - f.measureText(s_) / 2, base - hgt - 30, f, paint(INK))
        K.reg(x0, base - hgt - 100, x0 + 280, base - hgt - 20, "score")
        C.label(c, lab, x0 + 140, base + 70, 46, paper=(250, 244, 228), tag="score")
        PR.clock(c, x0 + 140, base - hgt / 2, 80, 10 if j else 7, 10 if j else 50, numerals=False)
    return st.arr


def s_c_proofs(T, idx):
    """'Proofs, yes. Clocks, no.' Lili holds the medal high; she lifts the clock, then lets it drop."""
    st = K.Stage()
    c = st.c
    SE.salon(c, T, wall=(176, 30, 54), wall2=(236, 170, 160), dots=False)
    t_c, t_no = Wx("c5", "Clocks") - 0.05, Wx("c5", "no") - 0.05
    keys = [(S("c5") - 0.1, dict(sL=50, eL=70)), (Wx("c5", "Proofs") - 0.05, dict(sL=50, eL=70, sR=150, eR=20)),
            (t_c, dict(sL=120, eL=30, sR=150, eR=20)), (t_no, dict(sL=20, eL=6, sR=150, eR=20))]
    h = C.girl(c, "lili", 540, 2350, 1.1, T, keys, mood="delight" if T < t_c else "sad", hands=("hold", "hold"))
    PR.medal_(c, h["hand_r"][0], h["hand_r"][1] - 70, 1.5)
    if T < t_no + 0.1:
        PR.clock(c, max(170, h["hand_l"][0]), h["hand_l"][1] - 90, 110, 10, 10)
    else:                                                                # dropped
        u = T - t_no - 0.1
        y = min(1640, h["hand_l"][1] - 90 + 2400 * u * u)
        c.save(); c.translate(max(170, h["hand_l"][0]) - 60 * u, y); c.rotate(min(70, 400 * u))
        PR.clock(c, 0, 0, 110, 10, 10)
        c.restore()
    if T > Wx("c5", "yes") - 0.05:
        C.label(c, "PROOFS: YES", 700, 330, 64, colr=(40, 120, 60), paper=(250, 244, 228), rot=6)
    if T > t_no:
        C.label(c, "CLOCKS: NO", 380, 480, 64, colr=(200, 30, 40), paper=(250, 244, 228), rot=-6)
    return st.arr


def s_c_jagged(T, idx):
    """'A person like that would be a medical mystery. For AI, it's normal. Researchers call it jagged.' A specimen
    case: a person's abilities make a gentle hill; the AI's are a jagged cut-paper skyline - the giant butterfly
    (Olympiad proofs) on a tall spike, the tiny one (reading a clock) down in a crevice."""
    st = K.Stage()
    c = st.c
    SE.butterfly_room(c, T)
    c.drawRect(skia.Rect.MakeXYWH(80, 300, 920, 960), paint((92, 60, 36)))
    c.drawRect(skia.Rect.MakeXYWH(100, 320, 880, 920), paint((214, 206, 180)))
    base = 1230
    hill = [(110 + i * 10, base - 330 - 50 * math.sin(i / 87 * math.pi)) for i in range(88)]
    tf = Wx("c6", "For") - 0.1
    peaks = [(110, base - 300), (170, base - 520), (220, base - 360), (300, base - 640), (360, base - 740), (420, base - 600),
             (480, base - 460), (540, base - 700), (600, base - 380), (660, base - 560), (720, base - 300), (790, base - 150),
             (850, base - 420), (910, base - 620), (970, base - 340)]
    u = ease(ramp(T, tf, tf + 0.5))
    if u > 0:                                                           # the AI: jagged
        pts = [(110, base)] + [(x, base - 0.75 * (base - y) * u) for x, y in peaks] + [(970, base)]
        CL.paper(c, pts, (200, 30, 40), seed=3, edge="cut", shadow=True)
    k0 = ramp(T, S("c6"), S("c6") + 0.8)
    if k0 > 0:                                                          # a person: a gentle hill
        n = max(2, int(len(hill) * k0))
        for colr, wdt in (((250, 244, 228), 14), ((40, 80, 150), 8)):
            p = paint(colr, stroke=wdt)
            p.setPathEffect(skia.DashPathEffect.Make([22, 14], 0))
            c.drawPath(path(hill[:n], closed=False), p)
        C.label(c, "A PERSON", 850, base - 450, 34, colr=(40, 80, 150), fname="special-elite-400", paper=(250, 248, 240), rot=-3, tag="hill")
    PR.butterfly(c, 360, base - 555 * u - 100 if u > 0 else 640, 1.45, T, pin=True, colors=((214, 168, 40), (176, 30, 54)), seed=1)
    PR.butterfly(c, 790, base - 112 * u - 40 if u > 0 else 900, 0.3, T, pin=True, colors=((150, 190, 226), (240, 240, 240)), seed=2)
    C.label(c, "OLYMPIAD PROOFS", 380, 392, 36, fname="special-elite-400", paper=(250, 248, 240), rot=-2)
    C.label(c, "READING A CLOCK", 790, 1188 if u > 0.5 else 980, 32, fname="special-elite-400", paper=(250, 248, 240), rot=3)
    if T > Wx("c6", "jagged") - 0.1:
        k = K.pop(T, Wx("c6", "jagged") - 0.1, 0.18, 0.4)
        c.save(); c.translate(320, 1170); c.scale(k, k); c.translate(-320, -1170)
        C.label(c, "JAGGED", 320, 1170, 72, colr=(250, 244, 228), paper=(24, 20, 22), rot=-3)
        c.restore()
    if T < tf:
        C.label(c, "A MEDICAL MYSTERY?", 540, 270, 46, paper=(250, 196, 30), rot=-2)
    return st.arr


def terminal(c, x, y, s, T, lines=()):
    """A 1960s terminal: a cabinet, a round-cornered green screen."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawPath(K.rrect(-260, -230, 260, 230, 30), paint((200, 192, 170)))
    c.drawPath(K.rrect(-200, -180, 200, 140, 40), paint((20, 40, 30)))
    f = K.font(PR.TYPE, 30)
    for i, l in enumerate(lines):
        c.drawString(l, -170, -120 + i * 44, f, paint((120, 255, 150)))
    c.drawRect(skia.Rect.MakeXYWH(-300, 230, 600, 70), paint((170, 160, 140)))
    for k in range(12):
        c.drawRect(skia.Rect.MakeXYWH(-280 + k * 46, 245, 38, 36), paint((240, 236, 226)))
    c.restore()


def s_c_agents(T, idx):
    """'Computer-using agents still fail about one try in three.' A terminal; three tries stamped OK, OK, FAIL."""
    st = K.Stage()
    c = st.c
    SE.salon(c, T, wall=(150, 180, 200), wall2=(220, 228, 236), dots=False)
    terminal(c, 540, 820, 1.2, T, ["> OPEN FILE", "> SAVE AS...", "> ?"])
    C.label(c, "AGENTS ON COMPUTERS", 540, 330, 48, fname="special-elite-400", rot=-1)
    for i, (txt, colr, tw) in enumerate((("TRY 1 OK", (40, 120, 60), Wx("c7", "fail")), ("TRY 2 OK", (40, 120, 60), Wx("c7", "one")),
                                         ("TRY 3 FAIL", (200, 30, 40), Wx("c7", "three")))):
        if T > tw - 0.15:
            k = K.pop(T, tw - 0.15, 0.18, 0.4)
            c.save(); c.translate(230 + i * 270, 1290); c.scale(k, k); c.translate(-(230 + i * 270), -1290)
            C.label(c, txt, 230 + i * 270, 1290, 40, colr=colr, paper=(250, 244, 228), rot=(-6, 3, -4)[i], tag="stamp")
            c.restore()
    return st.arr


def blocks(c, base, n, colrs, sx=0):
    for i in range(n):
        CL.paper(c, CL.rect_pts(sx - 60, base - 100 * (i + 1), sx + 60, base - 100 * i), colrs[i % len(colrs)], seed=i, shadow=False)


def s_c_sim(T, idx):
    """'Robots: 89% in simulation.' A robot arm stacks blocks perfectly on a clean paper grid."""
    st = K.Stage()
    c = st.c
    SE.void(c, (226, 236, 226), seed=8)
    for k in range(13):                                                 # the clean grid of a simulation
        c.drawLine(0, 300 + k * 100, W, 300 + k * 100, paint((120, 160, 120), 0.5, stroke=2))
        c.drawLine(k * 90, 300, k * 90, 1500, paint((120, 160, 120), 0.5, stroke=2))
    t0 = Wx("c7", "Robots") - 0.1
    n = min(4, int((T - t0) / 0.7) + 1)
    blocks(c, 1300, n, [(176, 30, 54), (40, 80, 150), (214, 168, 40), (40, 120, 124)], 700)
    u = ((T - t0) % 0.7) / 0.7
    a1 = 30 + 20 * math.sin(u * math.pi)
    PR.robot_arm(c, 330, 1300, 1.0, a1, 60 - 30 * math.sin(u * math.pi))
    C.label(c, "SIMULATION", 540, 330, 56, colr=(250, 244, 228), paper=(40, 120, 124), rot=-2)
    if T > Wx("c7", "eighty") - 0.1:
        C.big(c, "89%", 300, 640, 180, [(40, 120, 60), (24, 20, 22)], seed=14)
    return st.arr


def s_c_real(T, idx):
    """'About 12% on real household tasks.' The same arm at a real table: the jelly goes over, a glass falls."""
    st = K.Stage()
    c = st.c
    SE.salon(c, T, wall=(236, 170, 150), wall2=(246, 226, 210), dots=True)
    t0 = Wx("c7", "about", 1) - 0.12
    c.drawRect(skia.Rect.MakeLTRB(0, 1180, W, 1260), paint((150, 104, 64)))      # a table
    tip = ramp(T, t0 + 0.3, t0 + 0.9)
    c.save()
    c.translate(720, 1180)
    c.rotate(80 * tip)
    PR.jelly(c, 0, 0, 90, T, wob=1 + 3 * tip)
    c.restore()
    PR.glass(c, 880 + 60 * tip, 1180 + 300 * tip * tip, 1.1, level=0.6 * (1 - tip))
    PR.apple(c, 560, 1140, 44)
    PR.robot_arm(c, 260, 1180, 1.0, 50 + 25 * math.sin(T * 9), 70 + 30 * math.sin(T * 7))
    C.label(c, "A REAL HOME", 540, 330, 56, colr=(250, 244, 228), paper=(176, 30, 54), rot=2)
    if T > Wx("c7", "twelve") - 0.1:
        C.big(c, "ABOUT 12%", 500, 640, 150, [(200, 30, 40), (24, 20, 22)], seed=15, max_w=760)
    return st.arr


# ------------------------------------------------------------------ the banquet

def table_spread(c, T, mess=0.0, seed=0):
    """The feast on the long table: cakes, jellies, fruit, glasses, candles - and, with mess, splats and wreckage."""
    rng = K.rng_at(seed, 4)
    PR.cake(c, 420, 1290, 0.45, lines=(), candles=3, T=T, colr=(236, 200, 210))
    PR.jelly(c, 680, 1290, 70, T, colr=(60, 150, 70), wob=1 + 2 * mess)
    PR.grapes(c, 520, 1240, 14)
    PR.apple(c, 600, 1300, 34)
    PR.pear(c, 760, 1350, 34)
    for i, x in enumerate((330, 860)):
        PR.glass(c, x, 1420, 1.0, level=0.6 * (1 - mess))
    for i in range(3):
        PR.flame(c, 470 + i * 70, 1150 - 50, 0.25, T + i)
    if mess > 0:
        for i in range(int(14 * mess)):                                 # cream splats
            x, y = rng.uniform(150, 950), rng.uniform(1100, 1700)
            r = rng.uniform(30, 70)
            c.drawPath(K.smooth([(x + r * math.cos(a) * rng.uniform(0.6, 1.2), y + r * math.sin(a) * rng.uniform(0.6, 1.2))
                                 for a in np.linspace(0, 2 * math.pi, 10, endpoint=False)]), paint((250, 240, 236)))


def s_d_feast(T, idx):
    """'So it's just autocomplete?' - 'That's wrong.' - 'So it's a human mind, only smarter?' - 'Also wrong.' The
    feast: the Oracle at the head of the table in a napkin; Zuza cuts the cake with her shears; Lili bites an apple."""
    st = K.Stage()
    c = st.c
    SE.banquet_hall(c, T)
    PR.oracle(c, 540, 1190, 0.5, T, napkin=True, medal=True, look=(0.6 if T < S("d2") else -0.6, 0.3))
    table_spread(c, T)
    shears = lambda cc, x, y, a: CL.scissors(cc, x, y, a + 180, 0.5 + 0.5 * math.sin(T * 18), 1.0)
    C.girl(c, "zuza", 150, 2350, 1.05, T, [(S("d1") - 0.2, "stand"), (S("d2") - 0.05, "lift_r"), (S("d3") - 0.05, "point")],
           mood="deadpan", props=(None, shears if T < S("d3") else None), look=(0.7, 0))
    C.girl(c, "lili", 930, 2350, 1.05, T, [(S("d1") - 0.2, "point_l"), (S("d4") - 0.05, "eat")], mood="delight" if T < S("d4") else "chew",
           look=(-0.7, 0))
    return st.arr


def s_d_fight(T, idx):
    """The food fight: cakes fly, jelly splats on the Oracle, the streamers catch, the chandelier swings, the daisy
    chain snaps - jump cuts and the print flaring a new colour every few frames."""
    st = K.Stage()
    c = st.c
    t0 = E("d4") + 0.05
    u = T - t0
    SE.banquet_hall(c, T, swing=12 * math.sin(u * 9))
    for i, colr in enumerate(((176, 30, 54), (214, 168, 40), (40, 80, 150))):
        PR.streamer(c, 0, 420 + i * 60, W, 380 + i * 60, colr, sag=120, burn=min(1, max(0, u * 0.9 - i * 0.15)), T=T, seed=i)
    PR.oracle(c, 540, 1190, 0.5, T, napkin=True, medal=True, look=(math.sin(T * 20), 0), stuffed=1.0, mouth=0.6)
    c.drawCircle(540, 1190 - 0.5 * 1150, 60, paint((250, 240, 236)))      # a cream pie in the face
    table_spread(c, T, mess=min(1, u / 1.2))
    rng = K.rng_at(int(u * 6), 3)
    for i in range(4):                                                   # cakes in flight
        x = rng.uniform(100, 980)
        y = rng.uniform(500, 1300)
        PR.cake(c, x, y, 0.2, lines=(), colr=[(236, 200, 210), (250, 230, 180), (200, 160, 220)][i % 3])
    beat = int(u / 0.2)
    zp = ["throw", "throw2", "cower", "throw", "kick", "throw2", "up", "throw", "cower"][beat % 9]
    lp = ["cower", "throw", "throw2", "up", "throw", "cower", "throw2", "kick", "throw"][beat % 9]
    C.girl(c, "zuza", 200, 2300, 1.0, T, None, zp, mood="wide")
    C.girl(c, "lili", 880, 2300, 1.0, T, None, lp, mood="delight")
    chain(c, (380, 1200), (700, 1200), sag=60, T=T, broken=True)
    CL.scraps(c, T, t0, seed=9, n=50, area=(0, 200, W, 1700), fall=600, spin=2)
    return st.arr


def s_d_still(T, idx):
    """(Silence.) 'It can be superhuman in one direction, and brittle an inch away.' The wreck, holding still; a curl
    of smoke from a burnt streamer; the medal still on, the clock on the floor."""
    st = K.Stage()
    c = st.c
    SE.banquet_hall(c, T, lit=False)
    PR.oracle(c, 540, 1190, 0.5, T, napkin=True, medal=True, look=(0, 0.5), stuffed=1.0, mouth=0.6, lamps=False)
    c.drawCircle(540, 1190 - 0.5 * 1150, 60, paint((250, 240, 236)))
    table_spread(c, 0.0, mess=1.0)
    PR.clock(c, 300, 1500, 110, 4, 47)
    c.drawLine(230, 1430, 360, 1580, paint(INK, stroke=5))                # its cracked glass
    for i in range(6):                                                   # smoke
        y = 420 - ((T * 60 + i * 60) % 360)
        c.drawCircle(620 + 30 * math.sin(T + i), y, 30 + i * 6, paint((200, 200, 200), 0.25, blur=14))
    C.girl(c, "zuza", 170, 2300, 1.0, T, None, "stand", mood="deadpan", blink=0.0)
    C.girl(c, "lili", 910, 2300, 1.0, T, None, "stand", mood="sad", blink=0.0)
    a = st.arr
    z = 1.0 + 0.06 * ramp(T, S("d5") - 0.2, E("d5") + 0.2)
    if z > 1.001:
        img = K.image(a)
        out = np.zeros_like(a)
        cc = skia.Surface(out).getCanvas()
        cc.translate(540, 900)
        cc.scale(z, z)
        cc.translate(-540, -900)
        cc.drawImage(img, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear))
        a = out
    return a


# ------------------------------------------------------------------ epilogue

def s_e_clue(T, idx):
    """'So: an explanation is a clue, not a confession.' Lili files the reasoning slips in a box marked CLUES."""
    st = K.Stage()
    c = st.c
    SE.salon(c, T)
    rng = K.rng_at(10, 2)
    left = 1 - ramp(T, S("e1"), S("e1") + 2.8)
    for i in range(int(30 * left)):
        PR.slip(c, rng.uniform(80, 1000), rng.uniform(1560, 1820), rng.uniform(-30, 30), ["STEP 1...", "STEP 2..."], 0.5)
    CL.paper(c, CL.rect_pts(560, 1200, 900, 1480), (150, 104, 64), seed=6)       # the box
    C.label(c, "CLUES", 730, 1300, 56, paper=(250, 244, 228), tag="box")
    C.girl(c, "lili", 380, 1850, 0.66, T, [(S("e1") - 0.1, "stand")] + [(S("e1") + 0.4 + i * 0.6, "present" if i % 2 else "hold") for i in range(5)],
           mood="smile", look=(0.6, 0.3))
    if T > Wx("e1", "clue") - 0.1:
        C.label(c, "A CLUE,", 540, 340, 64, paper=(250, 196, 30), rot=-3)
    if T > Wx("e1", "not") - 0.1:
        C.label(c, "NOT A CONFESSION", 540, 480, 56, colr=(250, 244, 228), paper=(24, 20, 22), rot=2)
    return st.arr


def s_e_sample(T, idx):
    """'A score is a sample, not a mind.' Zuza drops the paper 94% into a specimen jar labelled SAMPLE."""
    st = K.Stage()
    c = st.c
    SE.salon(c, T, wall=(214, 168, 40))
    t0 = Wx("e1", "score") - 0.25
    drop = ease(ramp(T, t0 + 0.2, t0 + 0.8))
    c.drawPath(K.rrect(420, 900, 760, 1420, 40), paint((220, 236, 240), 0.45))        # the jar
    c.drawPath(K.rrect(420, 900, 760, 1420, 40), paint(WHITE, 0.7, stroke=6))
    c.drawRect(skia.Rect.MakeXYWH(400, 860, 380, 60), paint((150, 156, 166)))
    f = K.font("abril-400", 130)
    c.drawString("94%", 590 - f.measureText("94%") / 2, 700 + 440 * drop, f, paint((200, 30, 40)))
    K.reg(590 - f.measureText("94%") / 2, 600 + 440 * drop, 590 + f.measureText("94%") / 2, 720 + 440 * drop, "big")
    C.label(c, "SAMPLE", 590, 1300, 52, paper=(250, 244, 228), tag="jar")
    C.girl(c, "zuza", 190, 1880, 0.62, T, [(t0, "stand"), (t0 + 0.15, "lift_r"), (t0 + 0.8, "hips")], mood="deadpan")
    if T > Wx("e1", "mind") - 0.1:
        C.label(c, "NOT A MIND", 590, 340, 60, colr=(250, 244, 228), paper=(40, 80, 150), rot=-2)
    return st.arr


def s_e_clock(T, idx):
    """'And check the clock, right next to the medal.' They hang the clock beside the medal, and drape the mended
    daisy chain on the Oracle."""
    st = K.Stage()
    c = st.c
    SE.salon(c, T)
    t0 = Wx("e1", "check") - 0.25
    PR.oracle(c, 540, 1560, 0.8, T, medal=True, look=(0, 0.2))
    hang = ease(ramp(T, t0 + 0.2, t0 + 0.8))
    PR.clock(c, 540 + 150, 1560 - 0.8 * 820 - 400 * (1 - hang), 80, 10, 10)
    chain(c, (330, 1560 - 0.8 * 900), (750, 1560 - 0.8 * 900), sag=140, T=T)
    C.girl(c, "zuza", 170, 1860, 0.6, T, [(t0, "stand"), (t0 + 0.3, "point")], mood="smile")
    C.girl(c, "lili", 910, 1860, 0.6, T, [(t0, "stand"), (t0 + 0.4, "point_l")], mood="smile")
    if T > Wx("e1", "clock") - 0.1:
        C.label(c, "CHECK THE CLOCK", 540, 340, 60, paper=(250, 196, 30), rot=-2)
    return st.arr


DEDICATION = ["Dedicated to everyone", "who believed an", "explanation because", "it came in full", "sentences."]
SOURCES = ["Sources: Anthropic 2025 (two studies)", "Stanford AI Index 2026 · EMNLP 2025", "Johansson & Hall 2005 (choice blindness)"]


def s_e_dedication(T, idx):
    """The dedication card, deadpan, in an oval of daisies; the sources beneath."""
    st = K.Stage((18, 16, 16))
    c = st.c
    rng = K.rng_at(11, 1)
    for i in range(40):
        a = i / 40 * 2 * math.pi
        x, y = 540 + 450 * math.cos(a), 880 + 600 * math.sin(a)
        D.daisy(c, x, y, rng.uniform(22, 34), rot=i * 20 + T * 15, seed=i)
    f = K.font("fraunces-700", 60)
    for i, l in enumerate(DEDICATION):
        w = f.measureText(l)
        c.drawString(l, 530 - w / 2, 560 + i * 84, f, paint((246, 240, 222)))
        K.reg(530 - w / 2, 560 + i * 84 - 46, 530 + w / 2, 560 + i * 84 + 14, "dedication")
    f2 = K.font("special-elite-400", 27)
    for i, l in enumerate(SOURCES):
        w = f2.measureText(l)
        c.drawString(l, 530 - w / 2, 1090 + i * 40, f2, paint((200, 196, 186)))
        K.reg(530 - w / 2, 1090 + i * 40 - 22, 530 + w / 2, 1090 + i * 40 + 8, "dedication")
    return st.arr


def s_e_end(T, idx):
    """'Why did you make this film?' - 'First, I considered the daisies.' In the meadow, the Oracle in its medal,
    clock and daisy chain; Zuza eats a daisy; the frame freezes; THE END - and the Oracle, unasked, prints its
    reasoning for that too."""
    st = K.Stage()
    t_fz = E("e3") + 0.45
    Tf = min(T, t_fz)
    c = st.c
    SE.field(c, Tf, horizon=760)
    PR.oracle(c, 540, 1600, 0.72, Tf, medal=True, look=(0, 0.2), mouth=C.talk(Tf, "MACH") * 0.6)
    PR.clock(c, 540 + 130, 1600 - 0.72 * 820, 60, 10, 10)
    chain(c, (380, 1600 - 0.72 * 900), (700, 1600 - 0.72 * 900), sag=120, T=Tf)
    C.girl(c, "lili", 890, 1900, 0.62, Tf, [(S("e2") - 0.15, "stand"), (S("e2"), "point_l")], mood="delight")
    C.girl(c, "zuza", 190, 1900, 0.62, Tf, [(S("e2") - 0.15, "stand"), (E("e3") - 0.2, "eat")], mood="deadpan" if Tf < E("e3") else "chew",
           look=(0, 0) if Tf > E("e3") - 0.4 else (0.6, 0), props=(None, (lambda cc, x, y, a: D.daisy(cc, x, y - 10, 30, seed=3))) if Tf > E("e3") - 0.2 else (None, None))
    if T >= t_fz:
        k2 = K.pop(T, t_fz + 0.15, 0.25, 0.3)
        c.save(); c.translate(540, 470); c.scale(k2, k2); c.translate(-540, -470)
        C.big(c, "THE END", 540, 500, 170, [(176, 30, 54), (40, 80, 150), (214, 168, 40)], seed=21)
        c.restore()
        tp = t_fz + 0.75                                                 # the last joke: a slip pasted over the freeze
        if T > tp:
            u = ease(ramp(T, tp, tp + 0.2))
            PR.slip(c, 540, 1290 - 60 * (1 - u), -4, [typed("THEREFORE:", ramp(T, tp, tp + 0.4)), typed("THE END.", ramp(T, tp + 0.45, tp + 0.8))],
                    1.8, a=u)
    return st.arr

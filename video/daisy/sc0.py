"""Cold open and Chapter 1, THE PAINTED WINDOW: machinery; the Oracle types its reasoning; a window into the machine
that turns out to be a painting; the forehead cut open; the shortcut; a hundred slips; two tracks and a carried one;
says-why is not caused-it; the swapped photograph; a sea of numbers; the refrain."""
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

STEPS = ["FIRST, I CONSIDERED A.", "THEN I NOTICED B.", "THEREFORE: C."]
STEP_T = [("o1", "First", "A."), ("o1", "Then", "B."), ("o1", "Therefore", "C.")]


def steps_typed(T):
    out = []
    for s_, (k, w0, w1) in zip(STEPS, STEP_T):
        a, b = Wx(k, w0) - 0.05, Wx(k, w1) + 0.3
        out.append(typed(s_, ramp(T, a, b)))
    return out


def s_o_gears(T, idx):
    """Machinery: gears, a flywheel, a pendulum, a piston - cut out and pasted down, rearranged on every jump cut."""
    st = K.Stage()
    c = st.c
    SE.machine_room(c, T)
    beat = int(T / 0.35)
    rng = K.rng_at(beat, 2)
    for i in range(7):
        r = rng.uniform(90, 300)
        x, y = rng.uniform(80, W - 80), rng.uniform(250, 1600)
        teeth = int(r / 18) + 6
        sp = (1 if i % 2 else -1) * rng.uniform(30, 90)
        PR.gear(c, x, y, r, teeth, T * sp + i * 7, colr=[(150, 140, 120), (196, 160, 70), (120, 124, 130)][i % 3], spokes=int(rng.integers(0, 2)) * 5)
    PR.flywheel(c, W / 2 + 200 * math.sin(beat), 900, 280, T * 120)
    PR.pendulum(c, 200 + beat % 3 * 300, 0, 700, 28 * math.sin(T * 4.4))
    py = 1400 + 120 * math.sin(T * 9)                                     # a piston
    c.drawRect(skia.Rect.MakeXYWH(820, py, 120, 260), paint((120, 124, 130)))
    c.drawRect(skia.Rect.MakeXYWH(800, py - 30, 160, 40), paint((150, 156, 166)))
    return st.arr


def s_o_strip(T, idx):
    """The Oracle's teleprinter, close: it types its reasoning, one step on each word."""
    st = K.Stage()
    c = st.c
    SE.salon(c, T)
    PR.oracle(c, 540, 1240, 2.0, T, strip=steps_typed(T), strip_k=1.0)
    return st.arr


def s_o_duo(T, idx):
    """'It showed its working!' - 'It showed a working.' The salon: Lili delighted, Zuza not."""
    st = K.Stage()
    c = st.c
    SE.salon(c, T)
    PR.oracle(c, 540, 1560, 0.8, T, strip=STEPS[:1], look=(0.4 if T < S("o3") else -0.4, 0.2))
    C.girl(c, "lili", 860, 1830, 0.62, T, [(S("o2") - 0.2, "stand"), (S("o2"), "point_l"), (S("o2") + 0.5, "up")], mood="delight")
    C.girl(c, "zuza", 210, 1830, 0.62, T, [(S("o2") - 0.2, "stand"), (S("o3") - 0.05, "hips")], mood="deadpan", look=(0.6, 0))
    return st.arr


def _window_inside(c, x0, y0, w, h, T):
    c.drawRect(skia.Rect.MakeXYWH(x0, y0, w, h), paint((40, 36, 34)))
    for i in range(4):
        PR.gear(c, x0 + (i % 2) * w * 0.7 + 20, y0 + (i // 2) * h * 0.7 + 20, w * 0.3, 10, T * (60 if i % 2 else -60), colr=(196, 160, 70))


def s_o_window(T, idx):
    """'An AI's explanation feels like a window into the machine. Sometimes it's a painting of a window.' A window
    is pasted on the Oracle's face - gears whirr behind the glass - then a gilt frame lands round it: it's a picture."""
    st = K.Stage()
    c = st.c
    SE.salon(c, T, dots=False)
    PR.oracle(c, 540, 2560, 1.45, T, look=(0, 0.15))
    t1, t2 = Wx("o4", "window") - 0.15, Wx("o4", "painting") - 0.15
    k = K.pop(T, t1, 0.25, 0.25)
    if k > 0:
        cx, cy = 540, 880
        c.save()
        c.translate(cx, cy)
        c.scale(k, k)
        c.rotate(-3)
        w, h = 360, 300
        c.drawRect(skia.Rect.MakeXYWH(-w / 2 + 8, -h / 2 + 12, w, h), paint(INK, 0.4, blur=10))
        c.save()
        c.clipRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h))
        _window_inside(c, -w / 2, -h / 2, w, h, T)
        if T > t2:                                                       # it was paint all along: brush strokes over the glass
            rng = K.rng_at(4)
            for i in range(26):
                x, y = rng.uniform(-w / 2, w / 2), rng.uniform(-h / 2, h / 2)
                c.drawLine(x, y, x + rng.uniform(20, 60), y + rng.uniform(-10, 10), paint(mix((196, 160, 70), WHITE, rng.uniform(0, 0.5)), 0.5, stroke=8))
        c.restore()
        for xx in (-w / 2, 0, w / 2):
            c.drawLine(xx, -h / 2, xx, h / 2, paint((246, 240, 222), stroke=16))
        for yy in (-h / 2, 0, h / 2):
            c.drawLine(-w / 2, yy, w / 2, yy, paint((246, 240, 222), stroke=16))
        c.drawPath(path([(-w / 2 - 30, -h / 2 - 20), (-w / 2 + 40, -h / 2 - 20), (-w / 2 + 10, h / 2), (-w / 2 - 40, h / 2)]), paint((176, 30, 54), 0.9))
        c.drawPath(path([(w / 2 + 30, -h / 2 - 20), (w / 2 - 40, -h / 2 - 20), (w / 2 - 10, h / 2), (w / 2 + 40, h / 2)]), paint((176, 30, 54), 0.9))
        kf = K.pop(T, t2, 0.2, 0.3)
        if kf > 0:                                                       # the gilt frame of a painting
            c.save()
            c.scale(kf, kf)
            fr = 44
            c.drawRect(skia.Rect.MakeXYWH(-w / 2 - fr, -h / 2 - fr, w + 2 * fr, h + 2 * fr), paint((196, 150, 50), stroke=fr))
            c.drawRect(skia.Rect.MakeXYWH(-w / 2 - fr * 1.5, -h / 2 - fr * 1.5, w + 3 * fr, h + 3 * fr), paint((120, 80, 20), stroke=6))
            c.drawRect(skia.Rect.MakeXYWH(-w / 2 - 4, -h / 2 - 4, w + 8, h + 8), paint((240, 214, 120), stroke=6))
            c.restore()
        c.restore()
        if T > t2 + 0.3:
            C.label(c, "OIL ON CARDBOARD", 540, 1180, 40, fname="special-elite-400", rot=2)
    return st.arr


def s_title(T, idx):
    """The title over a field of daisies; the duo braid a daisy chain between them."""
    st = K.Stage()
    c = st.c
    SE.field(c, T, horizon=900)
    t0 = E("o4") + 0.05
    k1, k2 = K.pop(T, t0, 0.25, 0.3), K.pop(T, t0 + 0.35, 0.25, 0.3)
    if k1 > 0:
        c.save(); c.translate(540, 470); c.scale(k1, k1); c.translate(-540, -470)
        C.big(c, "DAISY CHAIN", 540, 470, 150, [(176, 30, 54), (40, 80, 150), (214, 168, 40), (24, 20, 22)], seed=3)
        c.restore()
    if k2 > 0:
        c.save(); c.translate(540, 640); c.scale(k2, k2); c.translate(-540, -640)
        C.big(c, "OF THOUGHT", 540, 640, 130, [(24, 20, 22), (40, 120, 124), (176, 30, 54)], seed=8)
        c.restore()
    zl = C.girl(c, "zuza", 330, 1900, 0.6, T, None, dict(sL=10, sR=46, eL=8, eR=-60), mood="deadpan", look=(0.5, 0))
    ll = C.girl(c, "lili", 750, 1900, 0.6, T, None, dict(sL=46, sR=10, eL=-60, eR=8), mood="delight", look=(-0.5, 0))
    chain(c, zl["hand_r"][:2], ll["hand_l"][:2], sag=110, T=T, r=26)
    return st.arr


def chain(c, p0, p1, sag=100, T=0.0, n=9, broken=False, r=22):
    """The daisy chain: daisies threaded stem to stem, hanging in a sag between two hands."""
    pts = []
    for i in range(n + 1):
        u = i / n
        pts.append((p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u + sag * 4 * u * (1 - u)))
    for i, (x, y) in enumerate(pts):
        if broken and n // 2 - 1 <= i <= n // 2:
            continue
        if i < n:
            x2, y2 = pts[i + 1]
            if not (broken and i == n // 2 - 1):
                c.drawLine(x, y, x2, y2, paint((80, 130, 60), stroke=5))
        c.drawCircle(x, y, r * 1.25, paint((60, 100, 50), 0.5))
        D.daisy(c, x, y, r, rot=i * 40 + T * 10, seed=i + 50)


def s_a_cut(T, idx):
    """'Let's look inside.' Zuza takes up the dressmaker's shears."""
    st = K.Stage()
    c = st.c
    SE.salon(c, T)
    PR.oracle(c, 640, 1560, 0.8, T, look=(-0.5, 0.1))
    t0 = S("a1") - 0.15
    shears = lambda cc, x, y, a: CL.scissors(cc, x, y, a + 180, 0.5 + 0.4 * math.sin(T * 12), 1.1)
    C.girl(c, "zuza", 240, 1830, 0.66, T, [(t0, "stand"), (t0 + 0.25, "lift_r")], mood="sly", props=(None, shears), hands=("open", "fist"), look=(0.6, 0))
    C.label(c, "1  THE PAINTED WINDOW", 540, 330, 52, colr=(250, 244, 228), paper=(176, 30, 54), rot=-2, tag="chapter")
    return st.arr


def _page(c, x0, y0, w, h):
    c.drawRect(skia.Rect.MakeXYWH(x0, y0, w, h), paint((246, 240, 222)))
    f = K.font(PR.TYPE, 22)
    for i, l in enumerate(["FIRST, I", "CONSIDERED", "A. THEN..."]):
        c.drawString(l, x0 + 6, y0 + 26 + i * 27, f, paint((40, 36, 60)))


def s_a_open(T, idx):
    """'But the explanation is just more output. Not a recording of what happened inside.' The shears cut the flap;
    inside the head is... another typed page."""
    st = K.Stage()
    c = st.c
    SE.salon(c, T, dots=False)
    t0 = S("a2") - 0.1
    cut_k = ramp(T, t0, t0 + 1.0)
    win = ramp(T, t0 + 1.0, t0 + 1.35)
    pts = PR.oracle(c, 540, 2500, 1.5, T, look=(0, -0.4), window=win, window_fn=lambda cc, x, y, w, h: _page(cc, x, y, w, h))
    if cut_k < 1:                                                         # the shears travel round three sides of the flap
        fx, fy = pts["window"]
        sc = 1.5
        L = [(fx - 60 * sc, fy + 45 * sc), (fx - 60 * sc, fy - 45 * sc), (fx + 60 * sc, fy - 45 * sc), (fx + 60 * sc, fy + 45 * sc)]
        seg = cut_k * 3
        i = min(2, int(seg))
        u = seg - i
        x = L[i][0] + (L[i + 1][0] - L[i][0]) * u
        y = L[i][1] + (L[i + 1][1] - L[i][1]) * u
        ang = math.degrees(math.atan2(L[i + 1][1] - L[i][1], L[i + 1][0] - L[i][0]))
        CL.scissors(c, x, y, ang, 0.5 + 0.5 * math.sin(T * 30), 1.0)
    if T > Wx("a2", "more") - 0.1:
        C.label(c, "MORE OUTPUT", 300, 400, 54, paper=(250, 196, 30), rot=-6)
    if T > Wx("a2", "recording") - 0.2:
        C.label(c, "NOT A RECORDING", 720, 520, 48, colr=(250, 244, 228), paper=(24, 20, 22), rot=4)
    return st.arr


def score_meter(c, x, y, k, s=1.0, label_="SCORE"):
    """A paper thermometer on a stand: k = 0..1."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawRect(skia.Rect.MakeXYWH(-14, 0, 28, 300), paint((90, 70, 50)))
    CL.paper(c, CL.rect_pts(-60, -620, 60, 0), (250, 244, 228), seed=2)
    c.drawRect(skia.Rect.MakeXYWH(-22, -580, 44, 520), paint((214, 206, 190)))
    c.drawRect(skia.Rect.MakeXYWH(-22, -60 - 520 * k, 44, 520 * k), paint((200, 40, 50)))
    c.drawCircle(0, -40, 46, paint((200, 40, 50)))
    f = K.font("abril-400", 44)
    c.drawString(f"{int(round(k * 100))}%", -f.measureText(f"{int(round(k * 100))}%") / 2, -640, f, paint(INK))
    K.reg_local(c, -60, -680, 60, -630, "meter")
    c.restore()


def s_a_shortcut(T, idx):
    """'Anthropic researchers gave a model a hidden shortcut to a higher score.' - 'Here. The answers.' Lili creeps up
    and posts a sheet into the Oracle's slot."""
    st = K.Stage()
    c = st.c
    SE.salon(c, T)
    t0 = S("a3")
    pts = PR.oracle(c, 460, 1560, 0.8, T, look=(0.6, 0.3) if T > S("a4") else (0, 0))
    score_meter(c, 130, 1480, 0.31, 0.75)
    walk = ramp(T, t0 + 0.5, S("a4"))
    steps = int(walk * 6)
    lx = 900 - steps * 28
    keys = [(t0, "stand")] + [(t0 + 0.5 + i * (S("a4") - t0 - 0.5) / 6, "step_l" if i % 2 else "step_r") for i in range(6)] + [(S("a4") - 0.05, "present")]
    if T < S("a4") + 0.45:
        h = C.girl(c, "lili", lx, 1830, 0.62, T, keys, mood="sly", look=(-0.6, 0), hands=("open", "hold"))
        hx, hy = h["hand_r"][:2]
        if T > S("a4") + 0.2:                                            # into the slot it goes
            u = ramp(T, S("a4") + 0.2, S("a4") + 0.45)
            hx, hy = hx + (pts["slot"][0] - hx) * u, hy + (pts["slot"][1] - hy) * u
        C.label(c, "ANSWERS", min(800, hx), min(1260, hy - 30), 46, colr=(200, 30, 40), fname="special-elite-400", rot=-8, tag="sheet")
    else:
        C.girl(c, "lili", lx, 1830, 0.62, T, keys + [(S("a4") + 0.45, "hips")], mood="delight", look=(-0.6, 0))
    C.label(c, "ANTHROPIC, 2025", 540, 330, 46, fname="special-elite-400", rot=-2)
    if T > Wx("a3", "shortcut") - 0.1:
        C.label(c, "A HIDDEN SHORTCUT", 640, 460, 50, colr=(250, 244, 228), paper=(176, 30, 54), rot=3)
    return st.arr


SLIP = ["STEP 1: I READ IT CAREFULLY.", "STEP 2: I WEIGHED EACH OPTION."]
CONFESS = ["STEP 1: I USED THE ANSWERS", "SOMEONE SLIPPED ME."]


def s_a_used(T, idx):
    """'It learned to use it almost every time. And in most setups, it admitted it in less than 2% of its written
    reasoning.' The score shoots up; slip after slip of tidy reasoning; one, circled, confesses."""
    st = K.Stage()
    c = st.c
    SE.salon(c, T)
    t0 = S("a5")
    score_meter(c, 130, 1480, 0.31 + 0.68 * ease(ramp(T, Wx("a5", "almost") - 0.2, Wx("a5", "time") + 0.1)), 0.75)
    pts = PR.oracle(c, 560, 1560, 0.8, T, mouth=0.2, lamps=True)
    rng = K.rng_at(6, 1)
    n = int(ramp(T, t0 + 0.3, Wx("a5", "less")) * 60)
    for i in range(n):                                                    # the slips pile up on the floor
        x, y = rng.uniform(80, 1000), rng.uniform(1560, 1820)
        PR.slip(c, x, y, rng.uniform(-30, 30), SLIP, 0.5)
    for i in range(6):                                                    # and more fly out of the slot
        t_i = t0 + 0.3 + i * 0.7
        if t_i < T < t_i + 1.2 and T < Wx("a5", "less"):
            u = (T - t_i) / 1.2
            sx, sy = pts["slot"]
            PR.slip(c, sx + (i % 2 * 2 - 1) * 380 * u, sy - 300 * math.sin(u * math.pi) + 500 * u * u, 360 * u * (1 if i % 2 else -1), SLIP, 0.55)
    if T > Wx("a5", "less") - 0.1:
        u = ease(ramp(T, Wx("a5", "less"), Wx("a5", "less") + 0.5))
        PR.slip(c, 700 - 160 * u, 1660 - 640 * u, -8 + 4 * u, CONFESS, 0.62 + 0.75 * u, mark=(30, 24, 26), colr=(255, 250, 200))
        k = K.pop(T, Wx("a5", "less") - 0.05, 0.25, 0.3)
        c.save(); c.translate(560, 560); c.scale(k, k); c.translate(-560, -560)
        C.big(c, "UNDER 2%", 560, 560, 170, [(200, 30, 40), (24, 20, 22)], seed=11)
        c.restore()
        if T > Wx("a5", "written"):
            C.label(c, "ADMITTED IT", 820, 700, 46, fname="special-elite-400", rot=-3)
    elif T > Wx("a5", "almost") - 0.1:
        C.label(c, "USED IT 99% OF THE TIME", 560, 560, 50, paper=(250, 196, 30), rot=-3)
    return st.arr


def s_a_count(T, idx):
    """(Silence.) 'A hundred slips. Maybe one confesses.' Zuza, knee-deep in slips, holds up the one."""
    st = K.Stage()
    c = st.c
    SE.salon(c, T)
    rng = K.rng_at(7, 1)
    for i in range(70):
        PR.slip(c, rng.uniform(20, 1060), rng.uniform(1380, 1900), rng.uniform(-40, 40), SLIP, 0.55)
    h = C.girl(c, "zuza", 440, 1990, 0.86, T, [(S("a6") - 0.6, "stand"), (Wx("a6", "Maybe") - 0.15, "lift_r")], mood="deadpan",
               hands=("open", "hold"))
    if T > Wx("a6", "Maybe") - 0.02:
        hx, hy = h["hand_r"][:2]
        PR.slip(c, min(hx, 760), max(hy - 60, 560), -6, CONFESS, 1.25, mark=(30, 24, 26), colr=(255, 250, 200))
    if T > Wx("a6", "one") - 0.1:
        C.label(c, "1 IN 100", 300, 360, 64, paper=(250, 196, 30), rot=-5)
    return st.arr


def s_a_tracks(T, idx):
    """'Another study traced its wiring. To add 36 and 59, it ran two tracks at once: a rough estimate, and the last
    digit.' A cut-paper diagram of the inside: wires, then two little trains of numbers."""
    st = K.Stage()
    c = st.c
    SE.void(c, (30, 34, 40), seed=3)
    rng = K.rng_at(8, 2)
    for i in range(18):                                                   # wiring
        y0 = 280 + i * 60
        c.drawPath(K.bez_path([(-20, y0), (540 + rng.uniform(-300, 300), y0 + rng.uniform(-200, 200)), (1100, y0 + rng.uniform(-100, 100))]),
                   paint([(200, 60, 50), (60, 120, 200), (220, 180, 60), (120, 170, 120)][i % 4], 0.7, stroke=7))
    C.label(c, "ANTHROPIC: TRACING THE WIRING", 540, 330, 40, fname="special-elite-400", rot=-1)
    t36 = Wx("a7", "thirty") - 0.1
    if T > t36:
        k = K.pop(T, t36, 0.25, 0.3)
        c.save(); c.translate(540, 560); c.scale(k, k); c.translate(-540, -560)
        C.big(c, "36 + 59", 540, 600, 150, [(250, 244, 228), (250, 196, 30)], seed=4)
        c.restore()
    tt = Wx("a7", "two", 0) - 0.1
    if T > tt:
        for j, (yy, lab, val, colr) in enumerate(((820, "ROUGH ESTIMATE", "ABOUT 92", (214, 168, 40)), (1120, "LAST DIGIT", "ENDS IN 5", (150, 190, 226)))):
            ty = tt + j * 0.35
            if T < ty:
                continue
            c.drawRect(skia.Rect.MakeXYWH(60, yy + 40, 960, 14), paint((150, 140, 120)))
            for k in range(20):
                c.drawRect(skia.Rect.MakeXYWH(60 + k * 50, yy + 34, 10, 26), paint((90, 70, 50)))
            u = ramp(T, ty, Wx("a7", "digit") + 0.2)
            x = 120 + 520 * ease(u)
            CL.paper(c, CL.rect_pts(x - 120, yy - 70, x + 120, yy + 34), colr, seed=j + 3)
            f = K.font("abril-400", 50)
            c.drawString(val, x - f.measureText(val) / 2, yy, f, paint(INK))
            K.reg_local(c, x - 120, yy - 70, x + 120, yy + 34, "track")
            C.label(c, lab, 300 if j == 0 else 280, yy - 130, 40, fname="special-elite-400", paper=(250, 244, 228), rot=-2 + 4 * j)
        if T > Wx("a7", "digit") + 0.1:
            k = K.pop(T, Wx("a7", "digit") + 0.1, 0.25, 0.12)
            c.save(); c.translate(862, 980); c.scale(k, k); c.translate(-862, -980)
            CL.paper(c, [(782, 884), (944, 878), (948, 1086), (776, 1092)], (200, 40, 50), seed=9, edge="torn")
            f = K.font("abril-400", 112)
            c.drawString("95", 862 - f.measureText("95") / 2, 1030, f, paint((250, 244, 228)))
            K.reg_local(c, 782, 884, 944, 1086, "answer")
            c.restore()
    return st.arr


CARRY = ["  36", "+ 59", " ---", "6+9=15,", "CARRY THE 1."]


def s_a_carry(T, idx):
    """'I added six and nine, and carried the one.' The Oracle prints the schoolbook sum."""
    st = K.Stage()
    c = st.c
    SE.salon(c, T, y_floor=1340)
    t0 = S("a8")
    k = ramp(T, t0, E("a8") + 0.1)
    lines = [typed(l, ramp(k, i / len(CARRY), (i + 1) / len(CARRY))) for i, l in enumerate(CARRY)]
    PR.oracle(c, 540, 1350, 0.85, T, strip=[l for l in lines if l] or [" "], look=(0, 0.3), mouth=C.talk(T, "MACH") * 0.6)
    return st.arr


def s_a_didnot(T, idx):
    """'It did not.' Zuza, close."""
    st = K.Stage()
    c = st.c
    SE.salon(c, T, dots=False)
    C.girl(c, "zuza", 540, 3300, 1.9, T, None, "stand", mood="deadpan", look=(0, 0))
    return st.arr


def s_a_notfake(T, idx):
    """'So not every explanation is fake. But "the model says this is why" is not proof of "this is what caused it."'
    Slips on a line, mostly ticked; then the duo hold up two cards with a slashed equals sign between them."""
    st = K.Stage()
    c = st.c
    SE.salon(c, T, wall=(150, 180, 170), wall2=(220, 230, 220))
    t1 = Wx("a11", "But") - 0.1
    if T < t1:
        c.drawLine(40, 520, 1040, 540, paint((80, 70, 60), stroke=4))
        for i in range(4):
            x = 170 + i * 250
            PR.slip(c, x, 680, (-1) ** i * 4, ["STEP 1...", "STEP 2..."], 0.62)
            c.drawCircle(x, 540, 12, paint((214, 168, 40)))
            if T > S("a11") + 0.25 + i * 0.25:
                mark = "X" if i == 2 else "OK"
                C.label(c, mark, x + 70, 820, 60, colr=(200, 30, 40) if mark == "X" else (40, 120, 60), paper=(250, 244, 228), rot=-8, fname="abril-400")
        C.girl(c, "lili", 540, 1950, 0.66, T, [(S("a11") - 0.2, "stand"), (S("a11") + 0.3, "point")], mood="smile")
    else:
        hl = C.girl(c, "lili", 270, 1900, 0.64, T, [(t1, "stand"), (t1 + 0.2, dict(sR=120, eR=40))], mood="smile", hands=("open", "hold"))
        hz = C.girl(c, "zuza", 810, 1900, 0.64, T, [(t1, "stand"), (t1 + 0.45, dict(sL=120, eL=40))], mood="deadpan", hands=("hold", "open"))
        if T > t1 + 0.25:
            C.label(c, "SAYS WHY", 260, 760, 56, colr=(250, 244, 228), paper=(40, 80, 150), tag="card", rot=-3)
        if T > t1 + 0.5:
            C.label(c, "CAUSED IT", 820, 760, 56, colr=(250, 244, 228), paper=(176, 30, 54), tag="card", rot=3)
        if T > Wx("a11", "not", 1) - 0.1:
            k = K.pop(T, Wx("a11", "not", 1) - 0.1, 0.25, 0.3)
            c.save(); c.translate(540, 740); c.scale(k * 0.62, k * 0.62)
            for dy in (-34, 34):
                c.drawRect(skia.Rect.MakeXYWH(-120, dy - 16, 240, 32), paint(INK))
            c.drawLine(80, -120, -80, 120, paint((200, 30, 40), stroke=26))
            c.restore()
    return st.arr


def portrait(c, who, x, y, s, ang=0.0, a=1.0):
    """A studio portrait, cut out with a white border."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    c.drawRect(skia.Rect.MakeXYWH(-150 + 8, -190 + 12, 300, 380), paint(INK, 0.35 * a, blur=8))
    c.drawRect(skia.Rect.MakeXYWH(-150, -190, 300, 380), paint((250, 248, 240), a))
    c.drawRect(skia.Rect.MakeXYWH(-130, -170, 260, 300), paint((120, 130, 140), a))
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(-130, -170, 260, 300))
    c.translate(0, 0)
    c.scale(0.8, 0.8)
    D.head(c, who, 1.0, "smile", 0.0, (0, 0))
    c.restore()
    c.restore()


def s_a_faces(T, idx):
    """'Humans do it too. Secretly handed the face they didn't pick, most people explained a choice they never made.'
    - 'I chose her for her earrings.' Lili picks one portrait; Zuza swaps it; Lili explains the other."""
    st = K.Stage()
    c = st.c
    SE.salon(c, T, wall=(196, 120, 120), wall2=(240, 210, 200))
    t_pick, t_swap = S("a12") + 0.9, Wx("a12", "Secretly") - 0.1
    C.label(c, "CHOICE BLINDNESS, 2005", 540, 320, 44, fname="special-elite-400", rot=-1)
    swapped = T > t_swap + 0.35
    # the two portraits on the table, then one in Lili's hand
    if T < t_pick + 0.4:
        portrait(c, "eva", 330, 760, 0.95, -4)
        portrait(c, "mira", 750, 760, 0.95, 5)
        if T > t_pick:
            c.drawOval(skia.Rect.MakeLTRB(170, 540, 490, 980), paint((40, 120, 60), stroke=10))
    keys_l = [(S("a12") - 0.2, "stand"), (t_pick - 0.1, "point_l"), (t_pick + 0.4, "hold")]
    keys_z = [(S("a12") - 0.2, "stand"), (t_swap, "point"), (t_swap + 0.35, "hips")]
    C.girl(c, "zuza", 210, 1880, 0.62, T, keys_z, mood="sly", look=(0.6, 0))
    hl = C.girl(c, "lili", 760, 1880, 0.62, T, keys_l, mood="delight" if T > S("a13") else "smile", look=(-0.3, 0.3))
    if T > t_pick + 0.4:
        portrait(c, "mira" if swapped else "eva", 600, 820, 1.25, -5)
    if T > t_swap and T < t_swap + 0.35:                                  # the swap: a blur of hands
        CL.scraps(c, T, t_swap, seed=4, n=10, area=(400, 900, 900, 1200))
    if T > Wx("a13", "earrings") - 0.1:
        C.label(c, "NOT THE ONE SHE PICKED", 540, 1180, 48, colr=(250, 244, 228), paper=(176, 30, 54), rot=3)
    return st.arr


def s_a_interp(T, idx):
    """'In a network of billions of numbers, checking is far harder. Hence a whole research field: interpretability.'
    A sea of figures; the duo, tiny, with a magnifying glass."""
    st = K.Stage()
    c = st.c
    SE.void(c, (232, 226, 210), seed=5)
    f = K.font(PR.TYPE, 26)
    rng = K.rng_at(9, 9)
    rows = 52
    for j in range(rows):
        s_ = " ".join(f"{rng.uniform(-1, 1):+.3f}" for _ in range(9))
        c.drawString(s_, -40 + (j % 2) * 30 - (T * 20 % 60), 60 + j * 36, f, paint((90, 80, 90), 0.55))
    t_m = Wx("a14", "Hence") - 0.1
    mx, my = 540 + 180 * math.sin(T * 0.8), 860 + 120 * math.cos(T * 0.6)
    c.drawCircle(mx, my, 230, paint((250, 248, 236)))
    c.save()
    c.clipPath(K.circle(mx, my, 220), doAntiAlias=True)
    c.translate(mx, my)
    c.scale(2.6, 2.6)
    c.translate(-mx, -my)
    rng2 = K.rng_at(9, 9)
    for j in range(rows):
        s_ = " ".join(f"{rng2.uniform(-1, 1):+.3f}" for _ in range(9))
        c.drawString(s_, -40 + (j % 2) * 30 - (T * 20 % 60), 60 + j * 36, f, paint((60, 50, 70)))
    c.restore()
    c.drawCircle(mx, my, 230, paint((60, 50, 40), stroke=22))
    c.drawPath(K.capsule(mx + 160, my + 160, mx + 330, my + 330, 44, 36), paint((90, 60, 36)))
    C.girl(c, "zuza", 200, 1840, 0.42, T, None, "point", mood="deadpan")
    C.girl(c, "lili", 880, 1840, 0.42, T, None, "shrug", mood="wide")
    C.label(c, "BILLIONS OF NUMBERS", 540, 330, 48, paper=(250, 196, 30), rot=-2)
    if T > t_m:
        k = K.pop(T, t_m, 0.25, 0.3)
        c.save(); c.translate(520, 1240); c.scale(k, k); c.translate(-520, -1240)
        C.big(c, "INTERPRETABILITY", 520, 1260, 92, [(176, 30, 54), (40, 80, 150), (24, 20, 22)], seed=12, max_w=700)
        c.restore()
    return st.arr


def refrain(T, idx, line_a, line_b):
    """The refrain, always the same framing: the duo in the meadow, braiding the daisy chain, trading two lines."""
    st = K.Stage()
    c = st.c
    SE.field(c, T, horizon=700, density=0.8)
    zl = C.girl(c, "zuza", 300, 2250, 1.0, T, None, dict(sL=10, eL=8, tR=(160, -1090)), mood="deadpan", look=(0.6, 0), hands=("open", "fist"))
    ll = C.girl(c, "lili", 800, 2250, 1.0, T, None, dict(sR=10, eR=8, tL=(-160, -1090)), mood="smile", look=(-0.6, 0), hands=("fist", "open"))
    chain(c, zl["hand_r"][:2], ll["hand_l"][:2], sag=80, T=T, r=24)
    return st.arr


def s_a_refrain(T, idx):
    """'Does it know why?' - 'It says it knows why.'"""
    return refrain(T, idx, "a15", "a16")

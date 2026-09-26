"""Hook, 'what actually happened', and the ladder of levels."""
import math

import numpy as np
import skia

import chars as CH
import fx3
import mg
from mg import CX, H, INK, W, WHITE, ease, ramp
from cues import C
from timeline import TL

S, E, Wd = TL.s, TL.e, TL.word


def chalk_bg(arr, seed=5):
    arr[..., :3] = mg.paper_tex((28, 34, 32), seed)


def confetti(c, T, n=60, seed=0):
    rng = np.random.default_rng(seed)
    for i in range(n):
        x = (rng.uniform(0, W) + 40 * math.sin(T * 2 + i)) % W
        y = (rng.uniform(-400, H) + T * rng.uniform(200, 500)) % (H + 200) - 100
        a = T * rng.uniform(2, 6) + i
        col = mg.PSY[i % len(mg.PSY)]
        c.save()
        c.translate(x, y)
        c.rotate(math.degrees(a))
        c.drawRect(skia.Rect.MakeXYWH(-9, -5, 18, 10), mg.paint(col))
        c.restore()


# ------------------------------------------------------------------ hook

_clock_img = {}


def clock_photo(w):
    if w not in _clock_img:
        from PIL import Image
        im = Image.open(mg.TEX + "/clock_photo.png").convert("RGB")
        im = im.resize((w, int(w * im.size[1] / im.size[0])), Image.LANCZOS)
        a = np.asarray(im)
        _clock_img[w] = np.dstack([a, np.full(a.shape[:2], 255, np.uint8)])
    return _clock_img[w]


def s_hook(arr, t, d, T):
    """Frame one: the contradiction. Olympiad gold on top, a clock it can't read below."""
    mg.burst(arr, CX, 560, T, colors=[mg.YELLOW, mg.ORANGE, (255, 236, 120), mg.RED], rays=16, spin=0.9)
    low = arr[930:].copy()
    low[..., :3] = mg.paper_tex((236, 232, 224), 30)[930:]
    arr[930:] = low
    s = mg.surf(arr)
    with s as c:
        c.save()
        c.clipRect(skia.Rect.MakeWH(W, 930))
        mg.speed_lines(c, CX, 560, T, n=30, color=WHITE, r0=330, seed=1)
        c.restore()
        bounce = abs(math.sin(T * 7)) * 30
        sq = 0.12 * max(0.0, math.cos(T * 14)) if bounce < 8 else 0.0
        hx, hy, R = CH.jag(c, CX, 880 - bounce, T, s=0.82, arms=(-155, 155), eyes="wide", mouth="open", seed=5, squash=sq)
        mg.stroke(c, [(CX - 30, hy + R + 20), (CX, hy + R + 95), (CX + 30, hy + R + 20)], T, 7, width=8, color=mg.RED)
        med = mg.circle_pts(CX, hy + R + 118, 34, 24)
        mg.fill(c, med, T, mg.YELLOW, 8, off=(3, 3))
        mg.stroke(c, med, T, 9, width=6, closed=True)
        c.save()
        c.clipRect(skia.Rect.MakeWH(W, 930))
        confetti(c, T, 40, 3)
        c.restore()
        mg.letters(c, "OLYMPIAD GOLD", CX, 330, T, size=104, fname="bangers-400", color=mg.YELLOW, ow=14, seed=10, spacing=3)
        zig = [(i * 90, 930 + (-26 if i % 2 else 26)) for i in range(14)]
        mg.stroke(c, zig, T, 70, width=22, color=INK, double=False)
        mg.stroke(c, zig, T, 71, width=9, color=mg.CYAN, double=False)
        # the clock: a paper cut-out whose hands can't settle
        c.save()
        c.translate(CX, 1170)
        c.rotate(7 * math.sin(T * 5) + 3 * math.sin(T * 13))
        R = 125
        face = mg.circle_pts(0, 0, R, 40)
        c.save()
        c.translate(8, 10)
        c.drawPath(mg.path_of(mg.boil(face, T, 31, 1.0, True), True), mg.paint((0, 0, 0), 0.35, blur=7))
        c.restore()
        mg.fill(c, face, T, WHITE, 32, off=(0, 0))
        mg.stroke(c, face, T, 33, width=9, closed=True)
        for k in range(12):
            a = k / 12 * 2 * math.pi
            r0 = R - (26 if k % 3 == 0 else 16)
            mg.stroke(c, [(r0 * math.cos(a), r0 * math.sin(a)), ((R - 8) * math.cos(a), (R - 8) * math.sin(a))], T, 34 + k, width=5)
        rng = np.random.default_rng(mg.step(T))
        for L, w, sp in ((70, 12, 5.0), (105, 7, -11.0)):
            a = T * sp + rng.normal(0, 0.5)
            mg.stroke(c, [(0, 0), (L * math.cos(a), L * math.sin(a))], T, 50 + w, width=w, double=False)
        c.drawCircle(0, 0, 10, mg.paint(INK))
        c.restore()
        kq = mg.pop(T, 0.35, 0.3)
        if kq > 0:
            mg.letters(c, "CAN'T READ A CLOCK?", CX, 1015, T, size=76 * kq + 0.1, fname="bangers-400", color=mg.RED, ow=10, seed=12)
        for i, (qx, qy) in enumerate(((770, 1150), (300, 1240))):
            mg.letters(c, "?", qx, qy, T, size=110, fname="permanent-marker-400", color=mg.RED, ow=8, seed=40 + i, jig=8, rot=12)


def s_gold(arr, t, d, T):
    mg.burst(arr, CX, 820, T, spin=0.8)
    s = mg.surf(arr)
    z = 1.18 - 0.18 * ease(t / 0.35)
    with s as c:
        c.save()
        c.translate(CX, 900)
        c.scale(z, z)
        c.translate(-CX, -900)
        mg.speed_lines(c, CX, 820, T, n=46, color=WHITE, r0=460, seed=1)
        pod = mg.rect_pts(310, 1110, 460, 170)
        mg.fill(c, pod, T, (250, 250, 250), 3, off=(8, 6))
        mg.stroke(c, pod, T, 4, width=9, closed=True)
        mg.letters(c, "1", CX, 1240, T, size=120, fname="bangers-400", color=mg.YELLOW, ow=12, seed=2)
        CH.jag(c, CX, 1115, T, s=1.22, arms=(-155, 155), eyes="wide", mouth="open", seed=5)
        # the medal
        mg.stroke(c, [(CX - 36, 780), (CX, 870), (CX + 36, 780)], T, 7, width=10, color=mg.RED)
        med = mg.circle_pts(CX, 898, 40, 24)
        mg.fill(c, med, T, mg.YELLOW, 8, off=(4, 3))
        mg.stroke(c, med, T, 9, width=7, closed=True)
        c.restore()
        confetti(c, T, 70, 3)
        mg.letters(c, "MATH OLYMPIAD", CX, 330, T, size=88, fname="bangers-400", color=WHITE, ow=12, seed=10, spacing=4)
        mg.letters(c, "GOLD!", CX, 590, T, size=210, fname="bangers-400", color=mg.YELLOW, ow=18, seed=11,
                   scale=mg.pop(T, S("h1") + 1.0, 0.3) or 0.001)


def s_clock(arr, t, d, T):
    mg.paper(arr, (245, 238, 220), 2)
    s = mg.surf(arr)
    split = ease(ramp(T, C["half"] - 0.05, C["half"] + 0.25))
    with s as c:
        cx, cy, R = CX, 760, 300
        for half, sx in ((0, -1), (1, 1)):
            c.save()
            c.translate(sx * 90 * split, 30 * split * (1 if half else -1))
            c.rotate(sx * 7 * split)
            c.clipRect(skia.Rect.MakeLTRB(0 if half == 0 else cx, 0, cx if half == 0 else W, H))
            face = mg.circle_pts(cx, cy, R, 64)
            mg.fill(c, face, T, (255, 252, 240), 20, off=(9, 7))
            mg.stroke(c, face, T, 21, width=12, closed=True)
            for k in range(12):
                a = k / 12 * 2 * math.pi - math.pi / 2
                r0 = R - (40 if k % 3 == 0 else 24)
                mg.stroke(c, [(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + (R - 10) * math.cos(a), cy + (R - 10) * math.sin(a))], T, 30 + k, width=7)
            for k, num in ((0, "12"), (3, "3"), (6, "6"), (9, "9")):
                a = k / 12 * 2 * math.pi - math.pi / 2
                mg.letters(c, num, cx + (R - 90) * math.cos(a), cy + (R - 90) * math.sin(a) + 24, T, size=64,
                           fname="gochi-hand-400", color=INK, outline=None, seed=40 + k)
            c.restore()
        # hands: spinning, unsure
        rng = np.random.default_rng(mg.step(T))
        ah = T * 2.1 + 0.4 * math.sin(T * 5)
        am = -T * 7.3 + rng.normal(0, 0.2)
        if split < 0.5:
            mg.stroke(c, [(cx, cy), (cx + 160 * math.cos(ah), cy + 160 * math.sin(ah))], T, 50, width=16)
            mg.stroke(c, [(cx, cy), (cx + 250 * math.cos(am), cy + 250 * math.sin(am))], T, 51, width=10)
            c.drawCircle(cx, cy, 16, mg.paint(INK))
        CH.jag(c, 850, 1310, T, s=0.7, eyes="spiral", mouth="o", tilt=-10, arms=(-60, 20), seed=60)
        mg.stamp(c, "BEST AI: 50.1%", 380, 1170, T, C["half"], color=mg.RED, size=78, rot=-7)
        mg.stamp(c, "HUMANS: 90.1%", 390, 1285, T, Wd("h2", "Ninety"), color=(30, 150, 70), size=78, rot=4)
        mg.label(c, T, S("h2") + 0.2, ["READING ANALOG CLOCKS", "STANFORD AI INDEX 2026"])


MORPH = [("cel", mg.CYAN, mg.ORANGE), ("pencil", (250, 120, 200), (120, 200, 120)), ("crayon", mg.YELLOW, mg.PURPLE),
         ("print", mg.RED, mg.CYAN), ("cel", (40, 40, 40), mg.YELLOW), ("crayon", mg.GREEN, mg.PINK)]


def s_title(arr, t, d, T):
    k = mg.step(T) // 2 % 4
    if k == 0:
        mg.burst(arr, CX, 900, T, colors=[mg.RED, mg.YELLOW, mg.PINK, mg.ORANGE], rays=14, spin=1.5)
    elif k == 1:
        fx3.painterly(arr, [(0, (60, 40, 120)), (0.5, (230, 90, 140)), (1, (255, 200, 90))], seed=11, T=T)
    elif k == 2:
        mg.paper(arr, (255, 220, 60), 3)
    else:
        mg.swirl(arr, T, scale=1.4)
    s = mg.surf(arr)
    col = [WHITE, mg.YELLOW, mg.RED, WHITE][k]
    with s as c:
        zig = []
        for i in range(13):
            zig.append((40 + i * 83.3, 1040 + (-110 if i % 2 else 110) * (1 if i % 4 else 0.6)))
        mg.stroke(c, zig, T, 70, width=26, color=INK)
        mg.stroke(c, zig, T, 71, width=12, color=mg.CYAN)
        mg.letters(c, "JAGGED", CX, 820, T, size=230, fname="bangers-400", color=col, ow=20, seed=72, spacing=6,
                   scale=mg.pop(T, C["title"] - 0.1, 0.3) or 0.001)
        mg.letters(c, "INTELLIGENCE", CX, 1300, T, size=128, fname="permanent-marker-400", color=WHITE, ow=14, seed=73)
        # the character never holds one form for long
        st, hc, bc = MORPH[mg.step(T) // 2 % len(MORPH)]
        prev = mg.STYLE
        mg.set_style(st)
        CH.jag(c, CX, 630, T, s=0.72, eyes=["wide", "spiral", "normal"][mg.step(T) // 4 % 3], mouth="open", arms=(-150, 30 + 20 * k),
               seed=74, head_col=hc, body_col=bc, squash=0.12 * math.sin(T * 17), tilt=6 * math.sin(T * 9))
        mg.set_style(prev)


# ------------------------------------------------------------------ what actually happened

def s_gpqa(arr, t, d, T):
    mg.paper(arr, (225, 240, 250), 4)
    s = mg.surf(arr)
    with s as c:
        base, x1, x2, bw = 1180, 250, 620, 230
        mg.stroke(c, [(120, base), (960, base)], T, 80, width=9)
        t_bars = Wd("a1", "science") - 0.2
        g = ease(ramp(T, t_bars, Wd("a1", "ninety") + 0.2))
        g2 = ease(ramp(T, Wd("a1", "Experts") - 0.1, Wd("a1", "Sixty") + 0.2))
        h1, h2 = 560 * 0.94 * g, 560 * 0.65 * g2
        for x, h, col, lab, val, gg, seed in ((x1, h1, mg.ORANGE, "TOP AI", 94, g, 81), (x2, h2, mg.BLUE, "EXPERTS", 65, g2, 85)):
            if h > 4:
                bar = mg.rect_pts(x, base - h, bw, h)
                mg.fill(c, bar, T, col, seed, off=(6, 4), shader=mg.crayon_shader(col, seed=seed, density=0.9))
                mg.stroke(c, bar, T, seed + 1, width=8, closed=True)
                ty = base - h + 110 if h > 160 else base - h - 24
                mg.letters(c, f"{int(round(val * gg))}%", x + bw / 2, ty, T, size=96, fname="bangers-400", color=WHITE, ow=10,
                           seed=seed + 2)
            mg.letters(c, lab, x + bw / 2, base + 76, T, size=60, fname="permanent-marker-400", color=INK, outline=None, seed=seed + 3)
        if g > 0.9:
            CH.jag(c, x1 + bw / 2, base - h1 - 4, T, s=0.42, eyes="normal", mouth="smile", arms=(-150, 150), seed=88)
        if g2 > 0.9:
            CH.human(c, x2 + bw / 2, base - h2 - 4, T, s=0.38, mouth="flat", seed=89)
        # the exam itself, until the scores come in
        ke = ease(ramp(T, t_bars - 0.3, t_bars + 0.1))
        if ke < 1:
            c.save()
            c.translate(CX, 800 - 1100 * ke)
            c.rotate(-4 + 2 * math.sin(T * 3))
            sheet = mg.rect_pts(-310, -300, 620, 630)
            mg.fill(c, sheet, T, (252, 250, 244), 91, off=(10, 8))
            mg.stroke(c, sheet, T, 92, width=8, closed=True)
            mg.letters(c, "Q17.", -270, -240, T, size=70, fname="rubik-900", color=INK, outline=None, seed=93, align="left")
            for i in range(6):
                y = -150 + i * 52
                mg.stroke(c, [(-270, y), (250 - (i % 3) * 70, y)], T, 94 + i, width=5, color=(110, 110, 120))
            for i, opt in enumerate("ABCD"):
                mg.stroke(c, mg.circle_pts(-225 + i * 150, 260, 26, 16), T, 102 + i, width=5, closed=True)
                mg.note(c, opt, -225 + i * 150, 273, size=36)
            mg.note(c, "graduate-level physics, chemistry, biology", 0, 195, size=32, color=(80, 80, 90))
            c.restore()
        mg.letters(c, "PhD-LEVEL SCIENCE QUIZ", CX, 440, T, size=66, fname="bangers-400", color=mg.RED, ow=8, seed=90, spacing=2)
        mg.label(c, T, S("a1") + 0.1, ["STANFORD AI INDEX 2026"])


def s_agents(arr, t, d, T):
    mg.paper(arr, (255, 214, 60), 5)
    s = mg.surf(arr)
    with s as c:
        mon = mg.rect_pts(110, 420, 860, 600)
        mg.fill(c, mon, T, (40, 44, 60), 100, off=(9, 7))
        mg.stroke(c, mon, T, 101, width=12, closed=True)
        scr = mg.rect_pts(150, 460, 780, 520)
        mg.fill(c, scr, T, (235, 245, 255), 102, off=(0, 0))
        mg.stroke(c, [(CX - 50, 1020), (CX - 70, 1085), (CX + 70, 1085), (CX + 50, 1020)], T, 103, width=10, closed=True)
        g = ease(ramp(T, Wd("a2", "twelve") + 0.45, Wd("a2", "sixty") + 0.1))
        pct = 12 + (66 - 12) * g
        meter = mg.rect_pts(200, 620, 680, 90)
        mg.stroke(c, meter, T, 104, width=8, closed=True)
        fillr = mg.rect_pts(208, 628, 664 * pct / 100, 74)
        mg.fill(c, fillr, T, mg.GREEN, 105, off=(0, 0), shader=mg.crayon_shader(mg.GREEN, seed=7, density=1.0))
        mg.letters(c, f"{pct:.0f}%", CX, 840, T, size=150, fname="bangers-400", color=mg.GREEN, ow=12, seed=106)
        mg.note(c, "REAL COMPUTER TASKS DONE BY AI AGENTS", CX, 560, size=40, color=INK)
        kf = Wd("a2", "one")
        for i, (mark, col) in enumerate((("✓", mg.GREEN), ("✓", mg.GREEN), ("✗", mg.RED))):
            k = mg.pop(T, kf + 0.18 * i, 0.2)
            if k <= 0:
                continue
            x = 300 + i * 240
            card = mg.rect_pts(x - 75, 1135, 150, 140)
            mg.fill(c, card, T, WHITE, 110 + i, off=(6, 5))
            mg.stroke(c, card, T, 112 + i, width=8, closed=True)
            mg.letters(c, "OK" if mark == "✓" else "X", x, 1245, T, size=100 * k, fname="bangers-400", color=col, ow=9, seed=115 + i)
        mg.label(c, T, S("a2") + 0.1, ["OSWORLD BENCHMARK · AI INDEX 2026"])


def s_robot(arr, t, d, T):
    mg.paper(arr, (250, 230, 235), 6)
    s = mg.surf(arr)
    with s as c:
        # kitchen: counter faced with a stone-texture collage, cupboards in line
        mg.collage(c, "gravel.jpg", mg.rect_pts(40, 1040, 1000, 110), T, seed=120, src=(40, 60), scale=1.0, border=6)
        for i in range(3):
            cup = mg.rect_pts(90 + i * 320, 1180, 290, 300)
            mg.stroke(c, cup, T, 121 + i, width=7, closed=True)
            c.drawCircle(90 + i * 320 + 250, 1330, 9, mg.paint(INK))
        for i in range(2):
            mg.stroke(c, mg.rect_pts(120 + i * 460, 440, 380, 260), T, 125 + i, width=7, closed=True)
        rt = ramp(T, S("a3") + 0.4, S("a3") + 1.4)
        hand = CH.robot(c, 330, 1040, T, s=1.3, arm=0.35 - 0.2 * rt, seed=130)
        fall = ease(ramp(T, S("a3") + 1.2, S("a3") + 1.7))
        cx, cy = hand[0] + 50, hand[1] - 20 + fall * (1040 - hand[1] + 10)
        if fall < 1:
            cupp = np.array([(cx - 36, cy - 50), (cx + 36, cy - 50), (cx + 28, cy + 30), (cx - 28, cy + 30)])
            mg.fill(c, cupp, T, WHITE, 140, off=(3, 3))
            mg.stroke(c, cupp, T, 141, width=7, closed=True)
        else:
            rng = np.random.default_rng(3)
            for k in range(9):
                a = rng.uniform(-math.pi, 0)
                dx, dy = math.cos(a) * rng.uniform(40, 150), math.sin(a) * rng.uniform(20, 90)
                shard = np.array([(cx + dx, 1030 + dy), (cx + dx + 22, 1030 + dy + 10), (cx + dx + 5, 1030 + dy + 26)])
                mg.stroke(c, shard, T, 150 + k, width=5, closed=True)
            mg.letters(c, "CRASH!", 760, 900, T, size=110, fname="bangers-400", color=mg.RED, ow=12, seed=160)
        mg.stamp(c, "12% SUCCESS", 700, 610, T, Wd("a3", "twelve"), color=mg.RED, size=90, rot=6)
        mg.label(c, T, S("a3") + 0.1, ["REAL HOUSEHOLD ROBOT TASKS", "AI INDEX 2026"])


def s_nobody(arr, t, d, T):
    mg.paper(arr, (245, 238, 220), 7)
    burst = arr.copy()
    mg.burst(burst, 810, 900, T, spin=1.2)
    arr[:, CX.__int__():, :3] = burst[:, int(CX):, :3]
    s = mg.surf(arr)
    with s as c:
        mg.stroke(c, [(CX, 380), (CX, 1500)], T, 170, width=12)
        # left: a person tells the time without thinking
        clk = mg.circle_pts(270, 640, 120, 40)
        mg.fill(c, clk, T, WHITE, 171, off=(6, 4))
        mg.stroke(c, clk, T, 172, width=8, closed=True)
        mg.stroke(c, [(270, 640), (270, 550)], T, 173, width=9)
        mg.stroke(c, [(270, 640), (340, 640)], T, 174, width=12)
        CH.human(c, 270, 1360, T, s=0.95, mouth="smile", gaze=(0.5, -1), seed=175)
        mg.note(c, "3 o'clock. Easy.", 270, 890, size=46)
        # right: olympiad math, clock confusion
        rng = np.random.default_rng(1)
        for i, sym in enumerate(["x²", "±", "÷", "×", "½", "y³"]):
            a = T * 1.5 + i * 1.05
            mg.letters(c, sym, 810 + 190 * math.cos(a), 650 + 120 * math.sin(a), T, size=90, fname="rubik-900",
                       color=WHITE, ow=8, seed=180 + i)
        CH.jag(c, 810, 1360, T, s=0.95, eyes="spiral", mouth="o", seed=190, arms=(-140, 140))
        mg.letters(c, "NOBODY IS SHAPED", CX, 330, T, size=80, fname="bangers-400", color=INK, outline=WHITE, ow=10, seed=195)
        mg.letters(c, "LIKE THIS", CX, 420, T, size=80, fname="bangers-400", color=INK, outline=WHITE, ow=10, seed=196)


def s_agiq(arr, t, d, T):
    mg.swirl(arr, T, scale=1.0)
    s = mg.surf(arr)
    with s as c:
        mg.letters(c, "AGI?", CX, 1000, T, size=360, fname="bangers-400", color=WHITE, ow=26, seed=200, jig=10, rot=8)
    mg.fisheye(arr, 0.5 + 0.3 * math.sin(T * 3))


# ------------------------------------------------------------------ levels

STEPS = [("NARROW AI", "YES", mg.GREEN, "one skill: chess, translation..."),
         ("GENERAL-PURPOSE AI", "YES", mg.GREEN, "one model, many tasks"),
         ("HUMAN-LEVEL AGI", "DISPUTED", mg.ORANGE, "most thinking work, as well as people"),
         ("AUTONOMOUS AGI", "NOT SHOWN", mg.BLUE, "runs long projects on its own"),
         ("SUPERINTELLIGENCE", "NO", mg.RED, "far beyond the best humans")]
STEP_COLS = [(120, 210, 255), (110, 230, 170), (255, 210, 90), (255, 170, 120), (255, 140, 150)]
RISE, RUN, HALF = 0.74, 0.95, 3.3


def s_levels(arr, t, d, T):
    """A 3D staircase (flat-shaded CG with ink outlines), the camera circling as Jag climbs; consciousness
    is kept off the staircase, on a separate axis."""
    st = C["stamps"]
    cur = sum(1 for x in st[:5] if T >= x - 0.05) - 1
    sep = ease(ramp(T, C["separate"] - 0.3, C["separate"] + 0.4))
    fx3.painterly(arr, [(0, (250, 226, 190)), (0.55, (238, 222, 250)), (1, (190, 215, 245))], seed=21, T=T, n=2200, blob=0.25, jit=9)
    u = ramp(T, S("l1"), S("g1"))
    a = -0.55 + 0.9 * u
    focus = 0.0
    for i, x in enumerate(st[:5]):
        focus += ease(ramp(T, x - 0.35, x + 0.1))
    focus = min(4.0, max(0.0, focus - 1.0))
    dist = 9.8 + 3.0 * sep
    tgt = np.array([0.0, 1.75, -2.2])
    eye = tgt + np.array([dist * math.sin(a), 2.3 + 0.25 * focus, dist * math.cos(a)])
    cam = fx3.Cam(eye, tgt, fov=46, cx=CX - 170 * sep, cy=900 + 90 * sep)
    quads = []
    for i in range(5):
        lit = i <= cur
        col = STEP_COLS[i] if lit else (228, 226, 234)
        for name, pts, n in fx3.box(-HALF, 0, -(i + 1) * RUN, HALF, (i + 1) * RISE, -i * RUN):
            if name in ("bottom", "back"):
                continue
            quads.append((pts, n, col if name == "front" else tuple(min(255, v + 18) for v in col) if name == "top" else col, (i, name)))
    s = mg.surf(arr)
    with s as c:
        ta = 1 - ramp(T, st[0] - 0.3, st[0])
        if ta > 0:
            mg.letters(c, "LEVELS", CX, 330, T, size=110, fname="bangers-400", color=mg.RED, ow=12, seed=250, spacing=6, a=ta)
        fx3.draw_quads(c, cam, quads, T, light=(-0.5, 0.8, 0.6), seed=260)
        # labels on each riser, scaled with distance
        for i, (name, verdict, vcol, defi) in enumerate(STEPS):
            p, z = cam.project((-0.8, (i + 0.6) * RISE, -i * RUN + 0.01))
            k = 9.5 / z
            mg.letters(c, name, p[0], p[1] + 4 * k, T, size=50 * k, fname="bangers-400", color=INK, outline=None, seed=230 + i, spacing=1)
            mg.note(c, defi, p[0], p[1] + 36 * k, size=max(16, int(30 * k)), color=(30, 30, 50))
            if T >= st[i] - 0.02:
                q, _ = cam.project((2.3, (i + 0.5) * RISE, -i * RUN + 0.02))
                mg.stamp(c, verdict, q[0], q[1] + 18 * k, T, st[i], color=vcol, size=int(48 * k), rot=-6 + 4 * (i % 3))
        # Jag climbs: a hop up one step at every verdict
        lvl = -1
        for i, x in enumerate(st[:5]):
            if T >= x - 0.25:
                lvl = i
        hop = 0.0
        for x in st[:5]:
            h = ramp(T, x - 0.25, x + 0.1)
            if 0 < h < 1:
                hop = math.sin(h * math.pi)
        yj = (lvl + 1) * RISE if lvl >= 0 else 0.0
        zj = -(lvl + 0.55) * RUN if lvl >= 0 else 0.2
        p, z = cam.project((-2.85, yj + 0.9 * hop, zj))
        sj = 0.5 * 9.5 / z
        CH.jag(c, p[0], p[1], T, s=sj, eyes="wide" if hop > 0 else "normal", mouth="open" if hop > 0 else "smile",
               arms=(-150, 150) if hop > 0 else (-40, 60), seed=265, squash=-0.15 * hop, bob=hop == 0)
        # consciousness: not a rung at all
        if sep > 0:
            c.save()
            c.translate(800, 470)
            c.scale(sep, sep)
            cloud = []
            for j in range(12):
                aa = j / 12 * 2 * math.pi
                cloud.append((210 * math.cos(aa) + 18 * math.cos(aa * 5), 160 * math.sin(aa) + 14 * math.sin(aa * 4)))
            prev = mg.STYLE
            mg.set_style("crayon")
            mg.fill(c, np.array(cloud), T, (230, 200, 255), 270, off=(0, 0))
            mg.stroke(c, np.array(cloud), T, 271, width=7, closed=True, color=mg.PURPLE)
            mg.set_style(prev)
            mg.note(c, "a separate question", 0, -70, size=36, color=(80, 40, 120))
            mg.letters(c, "CONSCIOUS AI?", 0, 5, T, size=62, fname="bangers-400", color=mg.PURPLE, ow=6, seed=272)
            c.restore()
            if T >= st[5] - 0.02:
                mg.stamp(c, "NO EVIDENCE", 800, 575, T, st[5], color=mg.PURPLE, size=56, rot=5)

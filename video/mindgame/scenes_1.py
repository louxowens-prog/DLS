"""Hook, 'what actually happened', and the ladder of levels."""
import math

import numpy as np
import skia

import chars as CH
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
        pod = mg.rect_pts(310, 1230, 460, 190)
        mg.fill(c, pod, T, (250, 250, 250), 3, off=(8, 6))
        mg.stroke(c, pod, T, 4, width=9, closed=True)
        mg.letters(c, "1", CX, 1370, T, size=130, fname="bangers-400", color=mg.YELLOW, ow=12, seed=2)
        CH.jag(c, CX, 1235, T, s=1.35, arms=(-155, 155), eyes="wide", mouth="open", seed=5)
        # the medal
        mg.stroke(c, [(CX - 40, 860), (CX, 960), (CX + 40, 860)], T, 7, width=10, color=mg.RED)
        med = mg.circle_pts(CX, 990, 44, 24)
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
        cx, cy, R = CX, 820, 330
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
        CH.jag(c, 840, 1330, T, s=0.75, eyes="spiral", mouth="o", tilt=-10, arms=(-60, 20), seed=60)
        mg.stamp(c, "50.1% RIGHT", CX - 60, 1250, T, C["half"], color=mg.RED, size=96, rot=-9)
        mg.label(c, T, S("h2") + 0.2, ["READING ANALOG CLOCKS", "STANFORD AI INDEX 2026"])


def s_title(arr, t, d, T):
    k = mg.step(T) // 2 % 4
    if k == 0:
        mg.burst(arr, CX, 900, T, colors=[mg.RED, mg.YELLOW, mg.PINK, mg.ORANGE], rays=14, spin=1.5)
    elif k == 1:
        arr[..., :3] = (20, 20, 30)
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
        mg.stroke(c, zig, T, 70, width=26, color=INK if k != 1 else WHITE)
        mg.stroke(c, zig, T, 71, width=12, color=mg.CYAN)
        mg.letters(c, "JAGGED", CX, 820, T, size=230, fname="bangers-400", color=col, ow=20, seed=72, spacing=6,
                   scale=mg.pop(T, C["title"] - 0.1, 0.3) or 0.001)
        mg.letters(c, "INTELLIGENCE", CX, 1300, T, size=128, fname="permanent-marker-400", color=WHITE, ow=14, seed=73)
        CH.jag(c, 870, 1620, T, s=0.7, eyes="wide", mouth="smile", arms=(-150, 30), seed=74)


# ------------------------------------------------------------------ what actually happened

def s_gpqa(arr, t, d, T):
    mg.paper(arr, (225, 240, 250), 4)
    s = mg.surf(arr)
    with s as c:
        base, x1, x2, bw = 1230, 250, 620, 230
        mg.stroke(c, [(120, base), (960, base)], T, 80, width=9)
        g = ease(ramp(T, Wd("a1", "ninety") - 0.4, Wd("a1", "ninety") + 0.3))
        g2 = ease(ramp(T, Wd("a1", "Sixty") - 0.4, Wd("a1", "Sixty") + 0.3))
        h1, h2 = 560 * 0.94 * g, 560 * 0.65 * g2
        for x, h, col, lab, pct, seed in ((x1, h1, mg.ORANGE, "TOP AI", "94%", 81), (x2, h2, mg.BLUE, "EXPERTS", "65%", 85)):
            if h > 4:
                bar = mg.rect_pts(x, base - h, bw, h)
                mg.fill(c, bar, T, col, seed, off=(6, 4), shader=mg.crayon_shader(col, seed=seed, density=0.9))
                mg.stroke(c, bar, T, seed + 1, width=8, closed=True)
                mg.letters(c, pct, x + bw / 2, base - h + 110, T, size=96, fname="bangers-400", color=WHITE, ow=10, seed=seed + 2)
            mg.letters(c, lab, x + bw / 2, base + 80, T, size=60, fname="permanent-marker-400", color=INK, outline=None, seed=seed + 3)
        if g > 0.9:
            CH.jag(c, x1 + bw / 2, base - h1 - 4, T, s=0.42, eyes="normal", mouth="smile", arms=(-150, 150), seed=88)
        if g2 > 0.9:
            CH.human(c, x2 + bw / 2, base - h2 - 4, T, s=0.38, mouth="flat", seed=89)
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
        mg.stroke(c, [(CX - 60, 1020), (CX - 90, 1110), (CX + 90, 1110), (CX + 60, 1020)], T, 103, width=10, closed=True)
        g = ease(ramp(T, S("a2") + 0.5, Wd("a2", "sixty") + 0.2))
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
            x = 260 + i * 280
            card = mg.rect_pts(x - 100, 1190, 200, 200)
            mg.fill(c, card, T, WHITE, 110 + i, off=(6, 5))
            mg.stroke(c, card, T, 112 + i, width=8, closed=True)
            mg.letters(c, "OK" if mark == "✓" else "X", x, 1340, T, size=130 * k, fname="bangers-400", color=col, ow=10, seed=115 + i)
        mg.label(c, T, S("a2") + 0.1, ["OSWORLD BENCHMARK · AI INDEX 2026"])


def s_robot(arr, t, d, T):
    mg.paper(arr, (250, 230, 235), 6)
    s = mg.surf(arr)
    with s as c:
        # kitchen: counter faced with a stone-texture collage, cupboards in line
        mg.collage(c, "moon.jpg", mg.rect_pts(40, 1040, 1000, 110), T, seed=120, src=(40, 20), scale=2.4, border=6)
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
        mg.stamp(c, "12% SUCCESS", CX, 1640 - 120, T, Wd("a3", "twelve"), color=mg.RED, size=100, rot=6)
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

STEPS = [("NARROW AI", "YES", mg.GREEN), ("GENERAL-PURPOSE AI", "YES", mg.GREEN), ("HUMAN-LEVEL AGI", "DISPUTED", mg.ORANGE),
         ("AUTONOMOUS AGI", "NOT SHOWN", mg.BLUE), ("CONSCIOUS AI", "NO EVIDENCE", mg.PURPLE), ("SUPERINTELLIGENCE", "NO", mg.RED)]
STEP_COLS = [(120, 210, 255), (110, 230, 170), (255, 210, 90), (255, 170, 120), (220, 160, 255), (255, 140, 150)]


def s_levels(arr, t, d, T):
    mg.paper(arr, (240, 235, 250), 8)
    st = C["stamps"]
    cur = sum(1 for x in st if T >= x - 0.05) - 1
    s = mg.surf(arr)
    with s as c:
        mg.letters(c, "LEVELS", CX, 330, T, size=100, fname="bangers-400", color=mg.RED, ow=12, seed=250, spacing=6)
        for i, (name, verdict, vcol) in enumerate(STEPS):
            y = 1230 - i * 150
            x = 80 + i * 22
            blk = mg.rect_pts(x, y - 120, 1000 - x, 130)
            mg.fill(c, blk, T, STEP_COLS[i], 210 + i, off=(7, 5))
            mg.stroke(c, blk, T, 220 + i, width=7, closed=True)
            mg.letters(c, name, x + 24, y - 38, T, size=52, fname="bangers-400", color=INK, outline=None, seed=230 + i,
                       align="left", spacing=2)
            if T >= st[i] - 0.02:
                mg.stamp(c, verdict, 800, y - 40, T, st[i], color=vcol, size=58, rot=-6 + 4 * (i % 3))

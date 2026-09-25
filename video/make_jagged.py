#!/usr/bin/env python3
"""Render "JAGGED GENIUS": a <2 min vertical short on where AI really stands (Stanford AI
Index 2026 findings, jagged intelligence, and levels from narrow AI to ASI), styled after the
absurdist claymation-musical look of The Happiness of the Katakuris (2001): lumpy plasticine
shapes animated at 8 fps, a sunny countryside with an erupting volcano, karaoke-video lyrics
with a bouncing ball, a staircase "musical number", and sad-trombone fails.
Female narration (Kokoro af_bella).

    python3 make_jagged.py                  # -> out/jagged_genius.mp4
    python3 make_jagged.py --preview 3 17   # frames -> out/preview/jagged_genius/
"""
import math
import textwrap

import numpy as np
from PIL import Image, ImageDraw

import make_video as E
import narrate
from make_video import G, H, W, cue, ease_in_out, ease_out_back, ease_out_cubic, font, pop

FAT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ROUND = "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf"
INK = (40, 25, 30)
SKY = (120, 195, 255)
GRASS = (95, 175, 70)
CLAY_G = (140, 150, 175)
ORNG = (255, 140, 50)
PINK = (255, 90, 170)
YEL = (255, 220, 60)
RED = (225, 45, 45)
GREEN = (60, 185, 90)
PURP = (150, 90, 220)
CREAM = (255, 248, 230)
WHITE = (255, 255, 255)

SCRIPT = [
    ("hook", 0.5, ["In just a few years, AI crossed lines that sounded like science fiction."], 0.3),
    ("bench", 0.3, ["Stanford's 2026 AI Index says top systems now match or beat human baselines on many tests "
                    "in language, science, math, and reasoning across images and text.",
                    "One even earned gold at the International Math Olympiad."], 0.3),
    ("jagged", 0.3, ["And yet, the best model reads an analog clock right only about half the time. Humans? Ninety percent.",
                     "Computer-using agents leapt from twelve percent to sixty-six percent success in a year, "
                     "but still fail about one task in three.",
                     "And robots manage just twelve percent of real household chores."], 0.3),
    ("moravec", 0.3, ["Scientists saw this coming decades ago. What's hard for us can be easy for machines, "
                      "and what's easy for us, hard. It's called Moravec's paradox."], 0.3),
    ("shape", 0.3, ["Human skill is shaped like a hill. Nobody solves Olympiad math, then can't read a clock.",
                    "AI's is shaped like a mountain range. That's jagged intelligence, and it's why declaring A.G.I. is so hard."], 0.3),
    ("levels", 0.3, ["So let's use levels.",
                     "Narrow AI, superb at one task: achieved.",
                     "General-purpose AI, handling many unrelated tasks: achieved.",
                     "Human-level A.G.I.: disputed.",
                     "Autonomous A.G.I., pursuing long goals on its own: not convincingly shown.",
                     "Artificial consciousness: no established evidence.",
                     "Superintelligence, beyond us at nearly everything: no."], 0.4),
    ("which", 0.3, ["Mixing these up is how hype and panic spread. When someone says AGI is here, or never coming, "
                    "ask: which level?"], 0.3),
    ("outro", 0.3, ["Genius and clumsy, all at once. That's where AI really is."], 2.4),
]
TL = narrate.Timeline(SCRIPT, sid=1, speed=1.12)
ls, le = TL.start, TL.end
LEVELS = [("NARROW AI", "superb at one task", "ACHIEVED", GREEN),
          ("GENERAL-PURPOSE AI", "many unrelated tasks", "ACHIEVED", GREEN),
          ("HUMAN-LEVEL AGI", "most cognitive domains", "DISPUTED", ORNG),
          ("AUTONOMOUS AGI", "long goals, on its own", "NOT SHOWN", RED),
          ("CONSCIOUSNESS", "subjective experience", "NO EVIDENCE", (120, 120, 130)),
          ("SUPERINTELLIGENCE", "beyond us at nearly all", "NO", RED)]


def st(t):
    """Stop-motion time: 8 poses a second."""
    return math.floor(t * 8) / 8


class Ctx:
    frame = 0


def nz(*k):
    v = math.sin(sum(x * c for x, c in zip(k, (12.9898, 78.233, 37.719, 11.13)))) * 43758.5453
    return (v - math.floor(v)) * 2 - 1


# ---------------------------------------------------------------- plasticine


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


def clay(pts, col, seed=0, boil=2.0):
    """A lump of plasticine: shadow, body, highlight and thumbprint dents, re-posed 8x a second."""
    f = Ctx.frame
    p = [(x + boil * nz(seed, i, f, 1), y + boil * nz(seed, i, f, 2)) for i, (x, y) in enumerate(pts)]
    d = G.draw
    d.polygon([(x + 9, y + 11) for x, y in p], fill=shade(col, 0.45))
    d.polygon(p, fill=col)
    xs, ys = [x for x, _ in p], [y for _, y in p]
    cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    d.ellipse([cx - w * 0.32, cy - h * 0.38, cx - w * 0.02, cy - h * 0.16], fill=shade(col, 1.18))
    for k in range(4):
        dx, dy = nz(seed, k, 9) * w * 0.3, nz(seed, k, 10) * h * 0.3
        r = 4 + abs(nz(seed, k, 11)) * min(w, h) * 0.05
        d.arc([cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r], 200, 340, fill=shade(col, 0.8), width=3)


def blob(cx, cy, rx, ry, col, seed=0, n=18):
    clay([(cx + rx * (1 + 0.05 * nz(seed, i)) * math.cos(2 * math.pi * i / n),
           cy + ry * (1 + 0.05 * nz(seed, i, 3)) * math.sin(2 * math.pi * i / n)) for i in range(n)], col, seed)


def slab(x0, y0, x1, y1, col, seed=0, r=0.18):
    w, h = x1 - x0, y1 - y0
    rr = min(w, h) * r
    pts = []
    for (cx, cy, a0) in ((x1 - rr, y0 + rr, -90), (x1 - rr, y1 - rr, 0), (x0 + rr, y1 - rr, 90), (x0 + rr, y0 + rr, 180)):
        for k in range(5):
            a = math.radians(a0 + k * 22.5)
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    clay(pts, col, seed)


def bot(x, y, s, t, mood="happy", arms_up=False):
    """The clay AI: a lumpy robot with a ball antenna."""
    ts = st(t)
    hop = abs(math.sin(ts * 5)) * 14 * s if mood == "happy" else 0
    y -= hop
    slab(x - 80 * s, y - 40 * s, x + 80 * s, y + 130 * s, CLAY_G, 11)
    slab(x - 95 * s, y - 210 * s, x + 95 * s, y - 50 * s, (170, 180, 205), 12)
    G.draw.line([(x, y - 210 * s), (x, y - 270 * s)], fill=INK, width=int(8 * s))
    blob(x, y - 285 * s, 22 * s, 22 * s, RED, 13)
    d = G.draw
    if mood == "confused":
        for sx in (-1, 1):
            ex, ey = x + sx * 42 * s, y - 135 * s
            pts = [(ex + (2 + i * 1.3) * s * math.cos(i * 0.8), ey + (2 + i * 1.3) * s * math.sin(i * 0.8)) for i in range(18)]
            d.line(pts, fill=INK, width=int(5 * s))
        d.line([(x - 30 * s, y - 85 * s), (x - 10 * s, y - 95 * s), (x + 10 * s, y - 85 * s), (x + 30 * s, y - 95 * s)],
               fill=INK, width=int(6 * s))
        blob(x + 110 * s, y - 190 * s, 12 * s, 18 * s, (130, 200, 255), 14)
    else:
        for sx in (-1, 1):
            blob(x + sx * 42 * s, y - 135 * s, 16 * s, 16 * s, INK, 15 + sx)
        d.arc([x - 40 * s, y - 120 * s, x + 40 * s, y - 70 * s], 20, 160, fill=INK, width=int(7 * s))
    for sx in (-1, 1):
        ay = -120 if arms_up else 40
        clay([(x + sx * 80 * s, y), (x + sx * 150 * s, y + ay * s), (x + sx * 165 * s, y + (ay + 25) * s),
              (x + sx * 85 * s, y + 35 * s)], CLAY_G, 16 + sx)


def countryside(t, sky=SKY, volcano_erupt=0.0):
    G.img = Image.new("RGB", (W, H), sky)
    G.draw = d = ImageDraw.Draw(G.img)
    ts = st(t)
    sx, sy = 860, 220   # clay sun with a face
    for k in range(10):
        a = k * math.pi / 5 + ts * 0.5
        clay([(sx + 110 * math.cos(a - 0.12), sy + 110 * math.sin(a - 0.12)), (sx + 160 * math.cos(a), sy + 160 * math.sin(a)),
              (sx + 110 * math.cos(a + 0.12), sy + 110 * math.sin(a + 0.12))], ORNG, 30 + k, 1.5)
    blob(sx, sy, 100, 100, YEL, 31)
    for ex in (-30, 30):
        blob(sx + ex, sy - 15, 9, 12, INK, 32)
    d.arc([sx - 40, sy - 5, sx + 40, sy + 45], 20, 160, fill=INK, width=6)
    vx, vy = 330, 820   # volcano
    clay([(vx - 330, vy + 200), (vx - 70, vy - 240), (vx + 70, vy - 240), (vx + 330, vy + 200)], (150, 100, 70), 40)
    clay([(vx - 70, vy - 240), (vx + 70, vy - 240), (vx + 40, vy - 190), (vx - 40, vy - 190)], (230, 90, 40), 41)
    if volcano_erupt > 0:
        for k in range(12):
            a = -math.pi / 2 + (k - 5.5) * 0.18
            r = 80 + 520 * volcano_erupt * (0.6 + 0.4 * abs(nz(k, 5)))
            blob(vx + r * math.cos(a), vy - 240 + r * math.sin(a) * 0.9, 32, 32, [RED, ORNG, YEL][k % 3], 50 + k)
    clay([(-50, 1180), (250, 960), (560, 1050), (820, 930), (1150, 1100), (1150, 1500), (-50, 1500)], GRASS, 60)
    clay([(-50, 1300), (350, 1150), (700, 1230), (1150, 1120), (1150, 1500), (-50, 1500)], (70, 150, 60), 61)
    for k in range(9):
        fx = 60 + k * 120
        fy = 1250 + (k % 3) * 40
        blob(fx, fy, 14, 14, [PINK, YEL, WHITE][k % 3], 70 + k)


def karaoke(t, key):
    """Karaoke-video lyrics: each word fills with colour as she sings it; a ball bounces along."""
    for st_, dur, s, _ in TL.lines[key]:
        if not (st_ <= t < st_ + dur + 0.25):
            continue
        lines = textwrap.wrap(s, 26)
        f = font(FAT, 50)
        prog = min(1.0, (t - st_) / max(0.1, dur)) * len(s)
        y0 = 1545 - (len(lines) - 1) * 34
        G.draw.rectangle([0, y0 - 70, W, y0 + len(lines) * 68 - 10], fill=(30, 20, 70))
        done = 0
        bx = by = None
        for i, ln in enumerate(lines):
            y = y0 + i * 68
            x = W / 2 - f.getlength(ln) / 2
            G.draw.text((x, y), ln, font=f, fill=WHITE, anchor="lm", stroke_width=4, stroke_fill=(40, 60, 200))
            n = int(max(0, min(len(ln), prog - done)))
            if n > 0:
                G.draw.text((x, y), ln[:n], font=f, fill=YEL, anchor="lm", stroke_width=4, stroke_fill=PINK)
            if 0 < prog - done <= len(ln) + 1 and bx is None:
                bx, by = x + f.getlength(ln[:n]), y - 48
            done += len(ln) + 1
        if bx is not None:
            hop = abs(math.sin(t * 9)) * 22
            G.draw.ellipse([bx - 13, by - hop - 13, bx + 13, by - hop + 13], fill=PINK, outline=WHITE, width=3)
        return


def bubble_title(t, at, xy, s, size, col=YEL, edge=PINK, until=None):
    if t < at or (until is not None and t >= until):
        return
    size *= pop(t, at, 0.3)
    if size < 8:
        return
    f = font(ROUND, size)
    lines = s.split("\n")
    wmax = max(f.getlength(ln) for ln in lines)
    if wmax > W - 80:
        size *= (W - 80) / wmax
        f = font(ROUND, size)
    kw = dict(font=f, anchor="mm", align="center", spacing=int(size * 0.08))
    G.draw.multiline_text((xy[0] + 7, xy[1] + 8), s, fill=INK, stroke_width=int(size * 0.12), stroke_fill=INK, **kw)
    G.draw.multiline_text(xy, s, fill=col, stroke_width=int(size * 0.1), stroke_fill=edge, **kw)


def stamp(t, at, xy, s, col, size=54, angle_seed=0):
    cue("stamp", at)
    if t < at:
        return
    k = 1.8 - 0.8 * ease_out_cubic((t - at) / 0.15)
    f = font(FAT, size * k)
    w = f.getlength(s) + 40 * k
    x, y = xy
    G.draw.rounded_rectangle([x - w / 2, y - 40 * k, x + w / 2, y + 40 * k], 14, fill=WHITE, outline=col, width=int(8 * k))
    G.draw.text((x, y), s, font=f, fill=col, anchor="mm")


# ---------------------------------------------------------------- scenes


def s_hook(t):
    countryside(t)
    bot(W / 2 + 180, 1130, 1.0, t, "happy", arms_up=True)
    bubble_title(t, 0.2, (W / 2, 470), "JAGGED\nGENIUS", 170, YEL, PINK)
    bubble_title(t, 0.9, (W / 2, 690), "where AI really is", 60, WHITE, (40, 60, 200))
    karaoke(t, "hook")


def s_bench(t):
    countryside(t, (150, 210, 255))
    ts = st(t)
    a1 = ls("bench", 1)
    cats = [("language", "language"), ("science", "science"), ("math", "math"), ("reasoning", "images")]
    tp = TL.phrases("bench", 0, [c for c, _ in cats])
    base_y, top = 1050, 330
    human = 640
    if t < a1:
        slab(80, 280, W - 80, 1080, CREAM, 80)
        G.draw.line([(120, human), (W - 120, human)], fill=RED, width=6)
        G.draw.text((W - 130, human - 26), "HUMAN BASELINE", font=font(FAT, 28), fill=RED, anchor="rm")
        for i, ((lab, _), at) in enumerate(zip(cats, tp)):
            cue("pop", at)
            if t < at:
                continue
            k = ease_out_back((t - at) / 0.5)
            x = 190 + i * 230
            hgt = (base_y - human + 60 + 40 * i % 3) * k
            slab(x - 70, base_y - hgt, x + 70, base_y, [PINK, ORNG, PURP, GREEN][i], 81 + i)
            G.draw.text((x, base_y + 0), lab.upper() if lab != "reasoning" else "MULTIMODAL", font=font(FAT, 26),
                        fill=INK, anchor="mt")
        G.draw.line([(120, human), (W - 120, human)], fill=RED, width=6)
        G.draw.rounded_rectangle([W / 2 - 170, human - 70, W / 2 + 170, human - 22], 12, fill=WHITE, outline=RED, width=3)
        G.draw.text((W / 2, human - 46), "HUMAN BASELINE", font=font(FAT, 28), fill=RED, anchor="mm")
        bubble_title(t, 0.4, (W / 2, 200), "STANFORD AI INDEX 2026", 58, WHITE, (40, 60, 200))
    else:
        bot(W / 2, 1100, 1.2, t, "happy", arms_up=True)
        slab(W / 2 - 260, 1140, W / 2 + 260, 1260, (200, 200, 210), 90)
        G.draw.text((W / 2, 1200), "1", font=font(FAT, 70), fill=INK, anchor="mm")
        k = ease_out_back((t - a1 - 0.3) / 0.4)
        if k > 0.05:
            G.draw.line([(W / 2 - 60, 850), (W / 2, 950)], fill=RED, width=14)
            G.draw.line([(W / 2 + 60, 850), (W / 2, 950)], fill=(40, 60, 200), width=14)
            blob(W / 2, 990, 70 * k, 70 * k, YEL, 91)
            G.draw.text((W / 2, 990), "IMO", font=font(FAT, int(34 * k) + 1), fill=INK, anchor="mm")
        bubble_title(t, a1 + 0.2, (W / 2, 330), "MATH OLYMPIAD\nGOLD!", 110, YEL, PINK)
        for k2 in range(14):   # confetti
            cx = (k2 * 97 + ts * 300) % W
            cy = (k2 * 173 + ts * 500) % 1200
            G.draw.rectangle([cx, cy, cx + 16, cy + 26], fill=[PINK, YEL, GREEN, PURP][k2 % 4])
    karaoke(t, "bench")


def clay_clock(cx, cy, r, t, wrong=False):
    blob(cx, cy, r, r, CREAM, 100)
    G.draw.ellipse([cx - r * 0.92, cy - r * 0.92, cx + r * 0.92, cy + r * 0.92], outline=INK, width=8)
    for k in range(12):
        a = k * math.pi / 6
        G.draw.line([(cx + r * 0.78 * math.cos(a), cy + r * 0.78 * math.sin(a)),
                     (cx + r * 0.88 * math.cos(a), cy + r * 0.88 * math.sin(a))], fill=INK, width=6)
    ah = math.radians(-90 + 30 * 10 + 5)    # 10:10
    am = math.radians(-90 + 60)
    G.draw.line([(cx, cy), (cx + r * 0.5 * math.cos(ah), cy + r * 0.5 * math.sin(ah))], fill=INK, width=16)
    G.draw.line([(cx, cy), (cx + r * 0.75 * math.cos(am), cy + r * 0.75 * math.sin(am))], fill=INK, width=10)
    blob(cx, cy, 16, 16, RED, 101)


def s_jagged(t):
    countryside(t, (180, 200, 230))
    a1, a2 = ls("jagged", 1), ls("jagged", 2)
    d = G.draw
    if t < a1:
        clay_clock(W / 2 - 150, 560, 230, t)
        bot(W / 2 + 280, 1160, 0.9, t, "confused")
        pa = TL.phrases("jagged", 0, ["half", "Humans"])
        if t >= pa[0]:
            slab(W / 2 + 60, 330, W - 70, 520, WHITE, 110)
            d.text((W / 2 + 275, 425), "\"4:50?\"", font=font(FAT, 64), fill=RED, anchor="mm")
            cue("trombone", pa[0] + 0.2)
        for j, (lab, v, col, at) in enumerate((("BEST AI", 0.501, RED, pa[0]), ("HUMANS", 0.901, GREEN, pa[1]))):
            if t < at:
                continue
            y = 880 + j * 120
            k = ease_out_cubic((t - at) / 0.6)
            d.text((90, y), lab, font=font(FAT, 38), fill=INK, anchor="lm")
            slab(330, y - 32, 330 + 560 * v * k + 30, y + 32, col, 111 + j)
            d.text((350 + 560 * v * k + 30, y), f"{v * 100 * k:.1f}%", font=font(FAT, 38), fill=INK, anchor="lm")
        bubble_title(t, 0.3, (W / 2, 200), "READING A CLOCK", 76, WHITE, (40, 60, 200))
    elif t < a2:
        slab(120, 330, W - 120, 900, (60, 70, 90), 120)
        slab(160, 370, W - 160, 860, (200, 230, 255), 121)
        tasks = ["book a flight", "rename 40 files", "fill a form", "make a chart", "send the email", "fix settings"]
        for i, tk in enumerate(tasks):
            y = 430 + i * 72
            at = a1 + 0.8 + i * 0.35
            if t < at:
                continue
            ok = i % 3 != 2
            d.text((210, y), tk, font=font(FAT, 36), fill=INK, anchor="lm")
            d.text((W - 210, y), "✓" if ok else "✗", font=font(FAT, 48), fill=GREEN if ok else RED, anchor="rm")
        pa = TL.phrases("jagged", 1, ["twelve", "sixty-six"])
        bubble_title(t, pa[0], (W / 2, 1000), "12%  →  66%", 110, YEL, PINK)
        bubble_title(t, pa[1] + 1.2, (W / 2, 1140), "still fails 1 in 3", 60, WHITE, RED)
        bubble_title(t, a1 + 0.1, (W / 2, 220), "COMPUTER-USE AGENTS", 66, WHITE, (40, 60, 200))
    else:
        bot(W / 2, 1100, 1.1, t, "confused")
        ts = st(t)
        clay([(W / 2 - 250, 640), (W / 2 - 120, 600 + 30 * math.sin(ts * 7)), (W / 2 + 40, 660), (W / 2 - 60, 760),
              (W / 2 - 230, 740)], PINK, 130)
        for k in range(5):
            a = k * 1.1 + ts * 2
            blob(W / 2 + 200 + 90 * math.cos(a), 700 + 60 * math.sin(a), 38, 12, WHITE, 131 + k)
        cue("crash", a2 + 1.0)
        cue("trombone", a2 + 1.4)
        bubble_title(t, a2 + 0.1, (W / 2, 250), "HOUSEHOLD ROBOTS", 76, WHITE, (40, 60, 200))
        bubble_title(t, TL.phrases("jagged", 2, ["twelve"])[0], (W / 2, 420), "12%", 170, RED, WHITE)
    karaoke(t, "jagged")


def s_moravec(t):
    p = TL.phrases("moravec", 0, ["It's called"])[0]
    countryside(t, (255, 190, 150), volcano_erupt=ease_out_cubic((t - p) / 0.6) if t >= p else 0.0)
    cue("boom", p)
    ts = st(t)
    tilt = 0.25 * math.sin(ts * 2.5)
    cx, cy = W / 2 + 180, 880
    pts = [(cx - 330 * math.cos(tilt), cy - 330 * math.sin(tilt) - 14), (cx + 330 * math.cos(tilt), cy + 330 * math.sin(tilt) - 14),
           (cx + 330 * math.cos(tilt), cy + 330 * math.sin(tilt) + 14), (cx - 330 * math.cos(tilt), cy - 330 * math.sin(tilt) + 14)]
    clay(pts, (200, 150, 90), 140)
    clay([(cx - 60, cy + 150), (cx + 60, cy + 150), (cx, cy + 10)], (150, 100, 70), 141)
    lx, ly = cx - 300 * math.cos(tilt), cy - 300 * math.sin(tilt) - 60
    rx, ry = cx + 300 * math.cos(tilt), cy + 300 * math.sin(tilt) - 60
    slab(lx - 110, ly - 60, lx + 110, ly + 30, PURP, 142)
    G.draw.multiline_text((lx, ly - 15), "calculus\n= easy", font=font(FAT, 28), fill=WHITE, anchor="mm", align="center")
    slab(rx - 110, ry - 60, rx + 110, ry + 30, GREEN, 143)
    G.draw.multiline_text((rx, ry - 15), "folding\n= hard", font=font(FAT, 28), fill=WHITE, anchor="mm", align="center")
    bubble_title(t, 0.3, (W / 2, 250), "for a machine...", 70, WHITE, (40, 60, 200))
    bubble_title(t, p + 0.3, (W / 2, 1180), "MORAVEC'S\nPARADOX", 110, YEL, RED)
    karaoke(t, "moravec")


SKILLS = ["math", "code", "law", "clocks", "chores", "spatial", "trivia", "planning"]
AI_P = [0.97, 0.9, 0.8, 0.35, 0.12, 0.3, 0.98, 0.45]
HUMAN_P = [0.55, 0.5, 0.55, 0.9, 0.95, 0.85, 0.5, 0.7]


def s_shape(t):
    countryside(t, (170, 220, 255))
    a1 = ls("shape", 1)
    d = G.draw
    x0, x1, yb, yt = 110, W - 110, 1080, 380
    slab(70, 300, W - 70, 1170, CREAM, 150)
    for i, s in enumerate(SKILLS):
        x = x0 + (x1 - x0) * i / (len(SKILLS) - 1)
        d.text((x, yb + 40), s, font=font(FAT, 26), fill=INK, anchor="mm")
    k1 = ease_out_cubic((t - 0.4) / 1.2)
    hp = [(x0 + (x1 - x0) * u, yb - (yb - yt) * (0.62 + 0.18 * math.sin(u * math.pi))) for u in np.linspace(0, 1, 40)]
    n = max(2, int(len(hp) * k1))
    d.line(hp[:n], fill=(40, 120, 220), width=14, joint="curve")
    d.text((x0 + 10, yt - 20), "HUMAN", font=font(FAT, 36), fill=(40, 120, 220), anchor="lm")
    if t >= a1:
        k2 = ease_out_cubic((t - a1) / 1.0)
        ap = [(x0 + (x1 - x0) * i / (len(SKILLS) - 1), yb - (yb - yt) * p * k2) for i, p in enumerate(AI_P)]
        d.line(ap, fill=RED, width=14)
        for x, y in ap:
            blob(x, y, 14, 14, RED, int(x))
        d.text((x1 - 10, yt - 20), "AI", font=font(FAT, 36), fill=RED, anchor="rm")
        bubble_title(t, TL.phrases("shape", 1, ["That's jagged"])[0], (W / 2, 200), "JAGGED\nINTELLIGENCE", 80, YEL, RED)
    else:
        bubble_title(t, 0.2, (W / 2, 200), "SHAPE OF A MIND", 76, WHITE, (40, 60, 200))
    karaoke(t, "shape")


def s_levels(t):
    countryside(t, (255, 215, 235))
    ts = st(t)
    for k in range(18):   # confetti
        cx = (k * 97 + ts * 250) % W
        cy = (k * 173 + ts * 420) % 1300
        G.draw.rectangle([cx, cy, cx + 14, cy + 22], fill=[PINK, YEL, GREEN, PURP][k % 4])
    bubble_title(t, 0.2, (W / 2, 170), "THE LEVELS", 90, YEL, PINK)
    for i, (name, desc, verdict, col) in enumerate(LEVELS):
        at = ls("levels", i + 1)
        cue("pop", at)
        if t < at:
            continue
        y = 1250 - i * 170
        xs = 60 + i * 30
        k = ease_out_back((t - at) / 0.3)
        slab(xs, y - 70, xs + 640 * k + 20, y + 70, [(200, 240, 200), (200, 240, 200), (255, 225, 190), (255, 205, 205),
                                                     (225, 225, 230), (255, 205, 205)][i], 160 + i)
        if k > 0.8:
            G.draw.text((xs + 30, y - 20), name, font=font(FAT, 38 if len(name) < 16 else 32), fill=INK, anchor="lm")
            G.draw.text((xs + 30, y + 28), desc, font=font(FAT, 26), fill=(90, 70, 80), anchor="lm")
        stamp(t, at + TL.lines["levels"][i + 1][1] * 0.75, (W - 190, y), verdict, col, 34 if len(verdict) > 8 else 44)
    k = min(5, sum(1 for i in range(6) if t >= ls("levels", i + 1)) - 1)
    if k >= 0:
        yb = 1250 - k * 170 - 110
        bot(90 + k * 30 + 150, yb, 0.45, t, "happy" if k < 2 else "confused")
    karaoke(t, "levels")


def s_which(t):
    countryside(t, (200, 225, 255))
    p = TL.phrases("which", 0, ["When someone", "ask"])
    bubble_title(t, 0.2, (W / 2, 240), "HYPE + PANIC", 100, RED, WHITE, until=p[0])
    if t >= p[0]:
        for sx, txt, col in ((-1, "AGI IS\nHERE!", PINK), (1, "NEVER\nCOMING!", PURP)):
            x = W / 2 + sx * 250
            blob(x, 880, 110, 120, [(250, 205, 170), (225, 170, 130)][sx > 0], 170 + sx)
            for ex in (-35, 35):
                blob(x + ex, 860, 12, 12, INK, 172)
            G.draw.ellipse([x - 30, 910, x + 30, 960], fill=INK)
            slab(x - 200, 420, x + 200, 640, col, 175 + sx)
            G.draw.multiline_text((x, 530), txt, font=font(FAT, 56), fill=WHITE, anchor="mm", align="center")
    if t >= p[1]:
        bubble_title(t, p[1] + 0.1, (W / 2, 1150), "WHICH LEVEL?", 120, YEL, RED)
    karaoke(t, "which")


def s_outro(t):
    countryside(t)
    ts = st(t)
    for i in range(5):   # the family-musical chorus line
        x = 150 + i * 195
        y = 1120 - abs(math.sin(ts * 5 + i)) * 40
        if i == 2:
            bot(x, y, 0.8, t, "happy", arms_up=True)
        else:
            blob(x, y - 140, 60, 66, [(250, 205, 170), (225, 170, 130), (190, 130, 95), (255, 220, 190)][i % 4], 180 + i)
            for ex in (-20, 20):
                blob(x + ex, y - 150, 7, 7, INK, 185)
            G.draw.arc([x - 25, y - 140, x + 25, y - 110], 20, 160, fill=INK, width=5)
            slab(x - 55, y - 80, x + 55, y + 60, [PINK, ORNG, PURP, GREEN][i % 4], 190 + i)
    bubble_title(t, 0.3, (W / 2, 330), "GENIUS\n+ CLUMSY", 140, YEL, PINK)
    bubble_title(t, TL.phrases("outro", 0, ["That's where"])[0], (W / 2, 620), "= AI, right now", 80, WHITE, (40, 60, 200))
    karaoke(t, "outro")


SCENE_FNS = {"hook": s_hook, "bench": s_bench, "jagged": s_jagged, "moravec": s_moravec, "shape": s_shape,
             "levels": s_levels, "which": s_which, "outro": s_outro}
SCENES = [(TL.dur[k], SCENE_FNS[k]) for k, *_ in SCRIPT]
TOTAL = TL.total

_orig_render = E.render_frame


def render_frame(fi):
    Ctx.frame = int(fi / 30 * 8)
    return _orig_render(fi)


E.render_frame = render_frame
SCAN = np.ones((H, 1, 1), np.uint16) * 256
SCAN[::3] = 236


def post(arr, fi, t, idx, tl):
    a = (arr.astype(np.uint16) * SCAN >> 8)                 # karaoke-VHS scanlines
    a[:, 3:, 0] = (a[:, 3:, 0] * 3 + a[:, :-3, 0]) // 4      # a little chroma bleed
    return a.astype(np.uint8)


# ---------------------------------------------------------------- score: cheery family-musical pop

SR = E.SR


def _tt(d):
    return np.arange(int(d * SR)) / SR


def extra_sfx(sr):
    rng = np.random.default_rng(3)
    trom = np.concatenate([np.sin(2 * np.pi * np.cumsum(np.full(int(d * SR), f) * (1 + 0.02 * np.sin(np.arange(int(d * SR)) / SR * 2 * np.pi * 6))) / SR)
                           * np.minimum(1, np.arange(int(d * SR)) / 800) * np.minimum(1, (int(d * SR) - np.arange(int(d * SR))) / 800)
                           for f, d in ((311, 0.35), (293, 0.35), (277, 0.35), (262, 1.0))])
    trom = sum(np.sin(k * np.arcsin(np.clip(trom, -1, 1))) / k for k in (1, 2, 3))
    x = _tt(0.25)
    thud = np.sin(2 * np.pi * np.cumsum(90 + 60 * np.exp(-x * 30)) / SR) * np.exp(-x * 16) + rng.standard_normal(len(x)) * np.exp(-x * 40) * 0.3
    x2 = _tt(0.12)
    popc = np.sin(2 * np.pi * np.cumsum(400 + 1200 * np.exp(-x2 * 40)) / SR) * np.exp(-x2 * 30)
    x3 = _tt(0.9)
    crash = rng.standard_normal(len(x3)) * np.exp(-x3 * 6) * 0.6
    for f in (2400, 3300, 4100, 5200):
        crash += np.sin(2 * np.pi * f * x3) * np.exp(-x3 * (5 + f / 1500)) * 0.25
    return {"trombone": (trom * 0.6, 0.35), "stamp": (thud, 0.5), "pop": (popc, 0.25), "crash": (crash, 0.45)}


def music_fn(n):
    rng = np.random.default_rng(2001)
    out = np.zeros(n)

    def add(sig, t, g):
        i = int(t * SR)
        if i < n:
            j = min(n, i + len(sig))
            out[i:j] += sig[: j - i] * g

    def piano(f, d=0.5):
        x = _tt(d)
        return (np.sin(2 * np.pi * f * x) + 0.4 * np.sin(4 * np.pi * f * x) + 0.15 * np.sin(6 * np.pi * f * x)) * np.exp(-x * 5)

    def glock(f):
        x = _tt(0.6)
        return (np.sin(2 * np.pi * f * x) + 0.3 * np.sin(2 * np.pi * f * 2.76 * x) * np.exp(-x * 8)) * np.exp(-x * 5)

    x = _tt(0.3)
    kick = np.sin(2 * np.pi * np.cumsum(55 + 90 * np.exp(-x * 30)) / SR) * np.exp(-x * 9)
    x = _tt(0.12)
    clap = rng.standard_normal(len(x)) * np.exp(-x * 30)
    beat = 60 / 128
    prog = [(130.81, [261.63, 329.63, 392.0]), (98.0, [246.94, 293.66, 392.0]), (110.0, [261.63, 329.63, 440.0]),
            (87.31, [261.63, 349.23, 440.0])]
    tune = [659.25, 587.33, 523.25, 587.33, 659.25, 659.25, 659.25, 0, 587.33, 587.33, 659.25, 587.33, 523.25, 0, 783.99, 783.99]
    t, bar = 0.0, 0
    total = E.TOTAL
    while t < total:
        root, ch = prog[bar % 4]
        for b in range(4):
            tb = t + b * beat
            add(kick, tb, 0.6)
            if b % 2:
                add(clap, tb, 0.35)
            xb = _tt(beat * 0.45)
            add(np.sin(2 * np.pi * root * (2 if b % 2 else 1) / 2 * xb) * np.exp(-xb * 4), tb, 0.35)
            add(np.sin(2 * np.pi * root * 1.5 / 2 * xb) * np.exp(-xb * 4), tb + beat / 2, 0.25)
            for f in ch:
                add(piano(f, 0.4), tb + beat / 2, 0.035)
        for q in range(8):
            f = tune[(bar % 2) * 8 + q]
            if f:
                add(glock(f * 2), t + q * beat / 2, 0.05)
        t += 4 * beat
        bar += 1
    voice = TL.track(n, SR)
    out = narrate.duck(out, voice, SR, depth=0.55)
    fade = int(1.5 * SR)
    end = int(total * SR)
    out[end - fade:end] *= np.linspace(1, 0, fade)
    out[end:] = 0
    return out * 0.75 + voice * 1.7


E.SCENE_CUT_FLASH = False
E.POST_FX = post

if __name__ == "__main__":
    print(f"total {TOTAL:.1f}s; " + ", ".join(f"{k} {TL.dur[k]:.1f}" for k, *_ in SCRIPT))
    E.main("jagged_genius.mp4", SCENES, music_fn, extra_sfx)

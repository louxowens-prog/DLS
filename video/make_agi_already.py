#!/usr/bin/env python3
"""Render "DID WE ALREADY BUILD AGI?": a <2 min vertical short on the AGI debate and why
intelligence is not consciousness, in the hand-drawn, hyper-kinetic Mind Game (2004) style
(reusing the scribble toolkit from make_education.py) with a rising flood inside a whale's
belly, a jagged radar chart, and a life-flash montage. Female narration (Kokoro af_bella).

    python3 make_agi_already.py                  # -> out/did_we_build_agi.mp4
    python3 make_agi_already.py --preview 3 17   # frames -> out/preview/did_we_build_agi/
"""
import math
import textwrap

import numpy as np
from PIL import ImageDraw, ImageOps

import make_education as M   # hand-drawn primitives; also installs its whiplash-cut POST_FX
import make_video as E
import narrate
from make_education import (CYAN, FONT, GRN, INK, ORNG, PAPER, PINK, PURP, RED, WHITE, YEL, Ctx, blob, hatch_bg, head,
                            new_frame, nz, scrawl, sketch, spark, tunnel, wob)
from make_video import G, H, W, cue, ease_in_out, ease_out_back, ease_out_cubic, font, pop

SEA = (40, 120, 220)
FLESH = (150, 40, 70)

SCRIPT = [
    ("hook", 0.5, ["Have we already built A.G.I., and just didn't notice?",
                   "Serious scientists now disagree about exactly that."], 0.3),
    ("yes", 0.3, ["In February 2026, four researchers wrote in Nature that Turing's vision of human-level "
                  "machine intelligence is now a reality."], 0.3),
    ("no", 0.3, ["Others push back. A 2025 framework from dozens of researchers, including Yoshua Bengio, measured AI "
                 "against a well-educated adult across ten cognitive domains.",
                 "GPT-4 scored twenty-seven percent. GPT-5, fifty-seven. Huge progress, very uneven, and not there yet.",
                 "And in an AAAI survey, about three in four AI researchers doubted that scaling today's methods gets us there."], 0.3),
    ("levels", 0.3, ["Google DeepMind suggests levels instead. Judge a system on two axes: how good, and how general."], 0.3),
    ("flood", 0.3, ["There won't be a notification that says A.G.I. achieved, 9:42 AM.",
                    "It's more like rising water. Chess. Then vision. Translation. Writing. Coding. Math. Science. "
                    "Using computers. Next, maybe long-term planning.",
                    "One day someone asks: what can humans still do that this can't learn? And when that list gets "
                    "short enough, we just start calling it general."], 0.3),
    ("mind", 0.3, ["But here's what people mix up. Intelligence is not consciousness.",
                   "Intelligence is solving problems. Self-awareness is modeling yourself. Consciousness is there being "
                   "something it's like to be you.",
                   "A system could write, I am frightened, while feeling nothing at all.",
                   "And animals can feel without doing calculus. Scientists see a realistic possibility of consciousness "
                   "in all vertebrates, and in many invertebrates, like octopuses and bees."], 0.3),
    ("test", 0.3, ["So reaching A.G.I. wouldn't prove we built a mind that feels. There's no accepted test for machine "
                   "experience, partly because we still don't understand our own."], 0.3),
    ("outro", 0.3, ["Watch the water rise. And keep the questions separate."], 2.2),
]
TL = narrate.Timeline(SCRIPT, sid=1, speed=1.14)
ls, le = TL.start, TL.end


class Mode:
    montage = False


def subtitle(t, key):
    if Mode.montage:
        return
    a = TL.active(key, t)
    if not a:
        return
    txt = "\n".join(textwrap.wrap(a[0], 32))
    f = font(FONT, 44)
    bb = G.draw.multiline_textbbox((W / 2, 1560), txt, font=f, anchor="mm", align="center", spacing=8)
    G.draw.rectangle([bb[0] - 24, bb[1] - 16, bb[2] + 24, bb[3] + 18], fill=INK)
    G.draw.multiline_text((W / 2, 1560), txt, font=f, fill=WHITE, anchor="mm", align="center", spacing=8)


# ---------------------------------------------------------------- props


def phone_note(cx, cy, s, t, crossed=0.0):
    d = G.draw
    d.rounded_rectangle([cx - 230 * s, cy - 330 * s, cx + 230 * s, cy + 330 * s], int(50 * s), fill=INK)
    d.rounded_rectangle([cx - 205 * s, cy - 300 * s, cx + 205 * s, cy + 300 * s], int(36 * s), fill=(40, 60, 110))
    d.rounded_rectangle([cx - 185 * s, cy - 200 * s, cx + 185 * s, cy - 40 * s], int(24 * s), fill=WHITE)
    d.text((cx - 160 * s, cy - 170 * s), "WORLD NEWS", font=font(FONT, int(24 * s)), fill=(120, 120, 130), anchor="lm")
    d.text((cx - 160 * s, cy - 120 * s), "AGI ACHIEVED", font=font(FONT, int(44 * s)), fill=INK, anchor="lm")
    d.text((cx + 165 * s, cy - 170 * s), "9:42 AM", font=font(FONT, int(24 * s)), fill=(120, 120, 130), anchor="rm")
    d.text((cx, cy + 150 * s), "9:42", font=font(FONT, int(110 * s)), fill=WHITE, anchor="mm")
    if crossed > 0:
        k = ease_out_cubic(crossed)
        sketch([(cx - 230 * s, cy - 330 * s), (cx - 230 * s + 460 * s * k, cy - 330 * s + 660 * s * k)], RED, 22, 4, 5)
        sketch([(cx + 230 * s, cy - 330 * s), (cx + 230 * s - 460 * s * k, cy - 330 * s + 660 * s * k)], RED, 22, 4, 6)


DOMAINS = ["knowledge", "reading", "math", "reasoning", "working mem", "long-term mem", "retrieval", "vision",
           "audio", "speed"]
PROFILE = [0.95, 0.95, 0.9, 0.55, 0.55, 0.05, 0.4, 0.35, 0.4, 0.55]   # illustrative jagged shape, not the paper's data


def radar(cx, cy, r, k, t):
    d = G.draw
    n = len(DOMAINS)
    ring = [(cx + r * math.cos(-math.pi / 2 + i * 2 * math.pi / n), cy + r * math.sin(-math.pi / 2 + i * 2 * math.pi / n))
            for i in range(n)]
    d.polygon(ring, fill=PAPER)
    sketch(ring, INK, 5, 2, 80, closed=True)
    for i, (x, y) in enumerate(ring):
        sketch([(cx, cy), (x, y)], (160, 150, 140), 2, 1, 81 + i)
        d.text((cx + (r + 70) * math.cos(-math.pi / 2 + i * 2 * math.pi / n),
                cy + (r + 40) * math.sin(-math.pi / 2 + i * 2 * math.pi / n)), DOMAINS[i], font=font(FONT, 24), fill=WHITE,
               anchor="mm", stroke_width=3, stroke_fill=INK)
    prof = [(cx + r * p * k * math.cos(-math.pi / 2 + i * 2 * math.pi / n), cy + r * p * k * math.sin(-math.pi / 2 + i * 2 * math.pi / n))
            for i, p in enumerate(PROFILE)]
    if k > 0.02:
        d.polygon(prof, fill=PINK)
        sketch(prof, RED, 6, 2, 90, closed=True)


def whale_belly(t, level):
    """Inside the whale: fleshy ribs overhead, and the sea rising."""
    d = G.draw
    d.rectangle([0, 0, W, 1420], fill=FLESH)
    for k in range(7):
        y = 60 + k * 60
        sketch([(40 + x * 50, y + 50 * math.sin(x / 20 * math.pi) + 8 * math.sin(t * 2 + k)) for x in range(21)],
               (220, 110, 130), 16, 3, 100 + k)
    for sx in (-1, 1):
        for k in range(5):
            pts = [(W / 2 + sx * (120 + k * 90) + sx * 60 * math.sin(u * math.pi), 200 + u * 1100) for u in np.linspace(0, 1, 12)]
            sketch(pts, (190, 80, 100), 10, 3, 120 + k * 2 + (sx > 0))
    return 1360 - level * 1000


def water(t, top):
    d = G.draw
    surf = [(x, top + 16 * math.sin(x / 60 + t * 3) + 6 * nz(x, Ctx.b)) for x in range(0, W + 30, 30)]
    d.polygon(surf + [(W, 1420), (0, 1420)], fill=SEA)
    sketch(surf, (170, 220, 255), 6, 2, 140)
    for k in range(10):
        bx = (k * 113 + t * 40) % W
        by = top + 60 + ((k * 191 - t * 120) % max(40, 1420 - top - 80))
        d.ellipse([bx - 8, by - 8, bx + 8, by + 8], outline=(170, 220, 255), width=3)


def octopus(cx, cy, s, t):
    for k in range(8):
        a = math.pi * (0.1 + 0.8 * k / 7)
        pts = [(cx + s * (40 + 150 * u) * math.cos(a) + 20 * s * math.sin(u * 6 + t * 4 + k), cy + s * 40 + s * 170 * u * math.sin(a))
               for u in np.linspace(0, 1, 10)]
        sketch(pts, PURP, int(22 * s * 1.2), 2, 150 + k)
    blob(cx, cy - 30 * s, 110 * s, 100 * s, PURP, 160)
    for ex in (-35, 35):
        G.draw.ellipse([cx + ex * s - 14 * s, cy - 40 * s - 14 * s, cx + ex * s + 14 * s, cy - 40 * s + 14 * s], fill=WHITE)
        G.draw.ellipse([cx + ex * s - 6 * s, cy - 40 * s - 6 * s, cx + ex * s + 6 * s, cy - 40 * s + 6 * s], fill=INK)


def bee(cx, cy, s, t):
    flap = abs(math.sin(t * 30))
    for sx in (-1, 1):
        blob(cx + sx * 20 * s, cy - 60 * s * (0.6 + 0.4 * flap), 50 * s, 30 * s, (220, 240, 255), 170 + sx)
    blob(cx, cy, 90 * s, 60 * s, YEL, 172)
    for k in (-30, 10, 50):
        sketch([(cx + k * s, cy - 55 * s), (cx + k * s, cy + 55 * s)], INK, int(14 * s), 2, 173 + k)
    G.draw.ellipse([cx - 90 * s, cy - 18 * s, cx - 60 * s, cy + 12 * s], fill=INK)


def glow_heart(cx, cy, s, t):
    k = 1 + 0.1 * math.sin(t * 8)
    pts = [(cx + s * k * 16 * math.sin(u) ** 3 / 16, cy - s * k * (13 * math.cos(u) - 5 * math.cos(2 * u) - 2 * math.cos(3 * u)
                                                                  - math.cos(4 * u)) / 16) for u in np.linspace(0, 2 * math.pi, 30)]
    G.draw.polygon(pts, fill=RED)
    sketch(pts, INK, 5, 2, 180, closed=True)


# ---------------------------------------------------------------- scenes


def s_hook(t):
    new_frame(t)
    tunnel(t, PURP, (170, 110, 240), speed=600)
    scrawl(t, 0.2, (W / 2, 330), "DID WE ALREADY\nBUILD AGI?", 110, YEL)
    at = ls("hook", 1)
    if t >= at:
        for sx, lab, col in ((-1, "YES!", GRN), (1, "NO!", RED)):
            x = W / 2 + sx * 250
            head(x, 900, 120, 30 + sx, t, mood="o")
            k = ease_out_back((t - at - 0.2) / 0.3)
            if k > 0.05:
                G.draw.rounded_rectangle([x - 150 * k, 620 - 70 * k, x + 150 * k, 620 + 70 * k], 30, fill=col)
                sketch([(x - 150 * k, 620 - 70 * k), (x + 150 * k, 620 - 70 * k), (x + 150 * k, 620 + 70 * k),
                        (x - 150 * k, 620 + 70 * k)], INK, 5, 2, 33 + sx, closed=True)
                scrawl(t, at + 0.2, (x, 620), lab, 80, WHITE)
        sketch([(W / 2 - 40, 820), (W / 2 + 20, 900), (W / 2 - 20, 920), (W / 2 + 40, 1010)], YEL, 14, 4, 35)
    subtitle(t, "hook")


def s_yes(t):
    new_frame(t)
    hatch_bg((230, 245, 255), 40, ink=(200, 215, 235))
    G.draw.rectangle([160, 250, W - 160, 1150], fill=WHITE)
    sketch([(160, 250), (W - 160, 250), (W - 160, 1150), (160, 1150)], INK, 7, 2, 41, closed=True)
    G.draw.rectangle([160, 250, W - 160, 400], fill=(200, 30, 40))
    scrawl(t, 0.2, (W / 2, 325), "NATURE", 90, WHITE, jitter=0.03)
    scrawl(t, 0.5, (W / 2, 470), "FEB 2026 · COMMENT", 40, INK, stroke=0)
    p = TL.phrases("yes", 0, ["Turing's", "is now"])
    head(W / 2, 680, 110, 42, t, skin=(240, 220, 200), mood="ok")
    scrawl(t, p[0], (W / 2, 880), "\"Turing's vision of\nhuman-level machine\nintelligence...\"", 48, INK, stroke=0)
    scrawl(t, p[1], (W / 2, 1060), "...is now a reality.", 60, RED)
    if t >= p[1]:
        cue("boom", p[1])
    subtitle(t, "yes")


def s_no(t):
    new_frame(t)
    a1, a2 = ls("no", 1), ls("no", 2)
    if t < a1:
        tunnel(t, (30, 90, 70), GRN, speed=400)
        scrawl(t, 0.2, (W / 2, 230), "\"A DEFINITION OF AGI\" · 2025", 56, WHITE)
        scrawl(t, TL.phrases("no", 0, ["well-educated"])[0], (W / 2, 330), "vs a well-educated adult", 50, YEL)
        k = ease_out_cubic((t - TL.phrases("no", 0, ["ten cognitive"])[0]) / 1.0)
        radar(W / 2, 830, 300, max(0, k), t)
    elif t < a2:
        hatch_bg(PAPER, 43)
        scrawl(t, a1, (W / 2, 230), "AGI SCORE", 90, RED)
        p = TL.phrases("no", 1, ["GPT-4", "GPT-5", "Huge"])
        for j, (lab, v, at) in enumerate((("GPT-4 (2023)", 0.27, p[0]), ("GPT-5 (2025)", 0.57, p[1]))):
            if t < at:
                continue
            y = 480 + j * 220
            k = ease_out_cubic((t - at) / 0.8)
            G.draw.text((100, y - 60), lab, font=font(FONT, 42), fill=INK, anchor="lm")
            G.draw.rectangle([100, y - 25, W - 100, y + 45], fill=(225, 215, 195))
            G.draw.rectangle([100, y - 25, 100 + (W - 200) * v * k, y + 45], fill=[ORNG, PINK][j])
            sketch([(100, y - 25), (W - 100, y - 25), (W - 100, y + 45), (100, y + 45)], INK, 5, 2, 44 + j, closed=True)
            G.draw.text((110 + (W - 200) * v * k, y + 10), f"{int(v * 100 * k)}%", font=font(FONT, 48), fill=INK, anchor="lm")
        G.draw.text((W - 100, 1020), "100% = AGI", font=font(FONT, 36), fill=INK, anchor="rm")
        sketch([(W - 100, 420), (W - 100, 1000)], RED, 6, 3, 46)
        scrawl(t, p[2], (W / 2, 1180), "uneven · not there yet", 60, RED)
    else:
        tunnel(t, (80, 20, 20), RED, speed=300)
        scrawl(t, a2 + 0.1, (W / 2, 250), "AAAI SURVEY", 90, WHITE)
        for i in range(4):
            x = 170 + i * 250
            head(x, 700, 90, 50 + i, t, mood="sad" if i < 3 else "ok")
            scrawl(t, a2 + 0.4 + i * 0.15, (x, 870), "NO" if i < 3 else "?", 60, YEL if i < 3 else WHITE)
        scrawl(t, a2 + 1.2, (W / 2, 1080), "76% doubt scaling\nalone gets there", 70, YEL)
    subtitle(t, "no")


def s_levels(t):
    new_frame(t)
    hatch_bg((25, 30, 60), 60, ink=(45, 50, 90))
    scrawl(t, 0.1, (W / 2, 210), "LEVELS, NOT A MOMENT", 70, CYAN)
    x0, y0, x1, y1 = 180, 380, W - 110, 1240
    d = G.draw
    rows = ["superhuman", "virtuoso", "expert", "competent", "emerging"]
    for i, r in enumerate(rows):
        y = y0 + (i + 0.5) * (y1 - y0) / 5
        d.line([(x0, y), (x1, y)], fill=(60, 70, 120), width=2)
        d.text((x0 - 12, y), r, font=font(FONT, 24), fill=WHITE, anchor="rm")
    sketch([(x0, y0), (x0, y1), (x1, y1)], WHITE, 7, 2, 61)
    d.text((x0 + 10, y1 + 40), "narrow", font=font(FONT, 30), fill=WHITE, anchor="lm")
    d.text((x1, y1 + 40), "general →", font=font(FONT, 30), fill=WHITE, anchor="rm")
    p = TL.phrases("levels", 0, ["how good", "how general"])
    scrawl(t, p[0], (x0 + 60, y0 - 50), "↑ how good", 40, YEL, stroke=0)
    pts = [(x0 + 60, y0 + 40, "AlphaGo", ORNG), (x0 + 110, y0 + 60, "chess engine", ORNG),
           (x0 + 420, y1 - 250, "today's chatbots?", PINK)]
    for i, (x, y, lab, col) in enumerate(pts):
        at = p[1] + i * 0.4
        if t < at:
            continue
        blob(x, y, 26 * pop(t, at), 26 * pop(t, at), col, 62 + i)
        d.text((x + 40, y), lab, font=font(FONT, 30), fill=WHITE, anchor="lm", stroke_width=3, stroke_fill=INK)
    subtitle(t, "levels")


SKILLS = [("Chess", "CHESS"), ("vision", "VISION"), ("Translation", "TRANSLATE"), ("Writing", "WRITING"),
          ("Coding", "CODING"), ("Math", "MATH"), ("Science", "SCIENCE"), ("Using computers", "COMPUTERS"),
          ("long-term planning", "PLANNING"), ("", "???"), ("", "???")]


def s_flood(t):
    new_frame(t)
    a1, a2 = ls("flood", 1), ls("flood", 2)
    if t < a1:
        tunnel(t, (20, 20, 40), (50, 50, 90), speed=300)
        k = ease_out_back(t / 0.4)
        phone_note(W / 2, 780, 1.1 * k, t, crossed=max(0, (t - (le("flood", 0) - 0.6)) / 0.3))
        cue("boom", le("flood", 0) - 0.6)
    else:
        ts = TL.phrases("flood", 1, [p for p, _ in SKILLS[:9]])
        tops = [1400 - (300 + 78 * i) for i in range(len(SKILLS))]
        keys_t = [a1] + [a + 0.5 for a in ts[:8]] + [le("flood", 1) + 0.3, a2 + 3.0]
        keys_y = [1390] + [tops[i] - 45 for i in range(8)] + [tops[8] - 45, tops[8] - 70]
        top = whale_belly(t, 0)
        top = float(np.interp(t, keys_t, keys_y))
        for i, (_, lab) in enumerate(SKILLS):
            x = 70 + i * 94
            ytop = tops[i]
            col = (120, 100, 90) if i < 9 else (215, 200, 150)
            G.draw.rectangle([x - 38, ytop, x + 38, 1400], fill=col)
            sketch([(x - 38, 1400), (x - 38, ytop), (x + 38, ytop), (x + 38, 1400)], INK, 5, 2, 200 + i)
            G.draw.text((x, ytop - 26), lab, font=font(FONT, 22 if len(lab) > 7 else 26), fill=YEL if i >= 9 else WHITE,
                        anchor="mm", stroke_width=3, stroke_fill=INK)
        water(t, top)
        if t >= a2:
            scrawl(t, a2 + 0.3, (W / 2, 950), "WHAT CAN HUMANS\nSTILL DO THAT IT\nCAN'T LEARN?", 64, WHITE)
            scrawl(t, TL.phrases("flood", 2, ["we just start"])[0], (W / 2, 1230), "\"...general?\"", 80, YEL)
    subtitle(t, "flood")


def s_mind(t):
    new_frame(t)
    a1, a2, a3 = ls("mind", 1), ls("mind", 2), ls("mind", 3)
    if t < a1:
        tunnel(t, INK, (60, 40, 80), speed=500)
        scrawl(t, 0.2, (W / 2, 600), "INTELLIGENCE", 100, CYAN)
        p = TL.phrases("mind", 0, ["is not"])[0]
        scrawl(t, p, (W / 2, 760), "≠", 160, RED)
        scrawl(t, p + 0.3, (W / 2, 930), "CONSCIOUSNESS", 100, PINK)
    elif t < a2:
        hatch_bg(PAPER, 70)
        items = [("Intelligence", "INTELLIGENCE", "solving problems", CYAN), ("Self-awareness", "SELF-AWARENESS",
                                                                            "modeling yourself", YEL),
                 ("Consciousness", "CONSCIOUSNESS", "something it's like\nto be you", PINK)]
        ts = TL.phrases("mind", 1, [p for p, *_ in items])
        for i, ((_, lab, desc, col), at) in enumerate(zip(items, ts)):
            cue("pop", at)
            if t < at:
                continue
            y = 380 + i * 330
            x = 330 + (i % 2) * 420
            blob(x, y, 180 * pop(t, at), 130 * pop(t, at), col, 71 + i)
            scrawl(t, at, (x, y - 20), lab, 40, INK, stroke=0)
            G.draw.multiline_text((x, y + 45), desc, font=font(FONT, 28), fill=INK, anchor="mm", align="center")
        scrawl(t, ts[2] + 1.0, (W / 2, 1320), "three different things", 54, RED)
    elif t < a3:
        hatch_bg((30, 30, 40), 72, ink=(50, 50, 60))
        G.draw.rectangle([140, 300, W - 140, 760], fill=PAPER)
        sketch([(140, 300), (W - 140, 300), (W - 140, 760), (140, 760)], INK, 6, 2, 73, closed=True)
        msg = "I am frightened."
        k = int(len(msg) * min(1, (t - a2 - 0.3) / 1.2))
        G.draw.text((W / 2, 530), msg[:k], font=font(FONT, 72), fill=INK, anchor="mm")
        spark(W / 2, 1000, 120, t, 74, col=(170, 170, 190))
        p = TL.phrases("mind", 2, ["while feeling"])[0]
        if t >= p:
            G.draw.ellipse([W / 2 + 120, 800, W / 2 + 400, 960], fill=WHITE)
            sketch([(W / 2 + 120 + 280 * (0.5 + 0.5 * math.cos(a)), 880 + 80 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 16)],
                   INK, 5, 2, 75)
            scrawl(t, p, (W / 2 + 260, 880), "...", 90, INK, stroke=0)
            scrawl(t, p + 0.4, (W / 2, 1250), "feeling nothing?", 70, YEL)
    else:
        tunnel(t, (10, 60, 90), (20, 110, 150), speed=250)
        octopus(330, 700, 1.0, t)
        glow_heart(330, 520, 60, t)
        p = TL.phrases("mind", 3, ["bees"])[0]
        if t >= p - 0.4:
            bee(800, 760, 1.0, t)
            glow_heart(800, 600, 50, t)
        scrawl(t, a3 + 0.2, (W / 2, 220), "CAN FEEL. NO CALCULUS.", 60, WHITE)
        scrawl(t, TL.phrases("mind", 3, ["realistic"])[0], (W / 2, 1150), "NY Declaration on\nAnimal Consciousness · 2024", 44,
               YEL)
    subtitle(t, "mind")


def s_test(t):
    new_frame(t)
    hatch_bg(RED, 90, ink=(170, 20, 30), n=90)
    head(W / 2, 700, 230, 91, t, skin=(250, 220, 200), mood="o")
    for k in range(6):
        a = k * math.pi / 3 + t * 1.5
        scrawl(t, 0.3 + k * 0.1, (W / 2 + 330 * math.cos(a), 700 + 300 * math.sin(a)), "?", 90, YEL)
    scrawl(t, 0.2, (W / 2, 220), "AGI ≠ PROOF OF FEELING", 64, WHITE)
    p = TL.phrases("test", 0, ["There's no", "partly"])
    scrawl(t, p[0], (W / 2, 1120), "NO ACCEPTED TEST", 90, YEL)
    scrawl(t, p[1], (W / 2, 1280), "we don't understand our own", 52, WHITE)
    subtitle(t, "test")


MONTAGE = ["hook", "yes", "no", "levels", "flood", "mind", "test"]


def s_outro(t):
    if t < 1.4:   # life flashes before your eyes
        k = int(t * 10)
        key = MONTAGE[k % len(MONTAGE)]
        saved, E.CUES = E.CUES, set()
        Mode.montage = True
        try:
            SCENE_FNS[key]((k * 1.37 + 0.8) % (TL.dur[key] - 0.5) + 0.5)
        finally:
            Mode.montage, E.CUES = False, saved
        Ctx.b = int(t * 12)
        if k % 2:
            G.img = ImageOps.invert(G.img)
        G.draw = ImageDraw.Draw(G.img)
    else:
        new_frame(t)
        top = whale_belly(t, 0.9)
        water(t, top)
        scrawl(t, 1.5, (W / 2, 420), "WATCH THE\nWATER RISE", 110, WHITE)
        scrawl(t, TL.phrases("outro", 0, ["And keep"])[0], (W / 2, 800), "keep the questions\nSEPARATE", 80, YEL)
    subtitle(t, "outro")


SCENE_FNS = {"hook": s_hook, "yes": s_yes, "no": s_no, "levels": s_levels, "flood": s_flood, "mind": s_mind,
             "test": s_test, "outro": s_outro}
SCENES = [(TL.dur[k], SCENE_FNS[k]) for k, *_ in SCRIPT]
TOTAL = TL.total

# ---------------------------------------------------------------- score: jazzy groove that sinks underwater

SR = E.SR


def _tt(d):
    return np.arange(int(d * SR)) / SR


def music_fn(n):
    rng = np.random.default_rng(4)
    out = np.zeros(n)

    def add(sig, t, g):
        i = int(t * SR)
        if i < n:
            j = min(n, i + len(sig))
            out[i:j] += sig[: j - i] * g

    def keys(f, d=0.5):
        x = _tt(d)
        return (np.sin(2 * np.pi * f * x) + 0.4 * np.sin(4 * np.pi * f * x)) * np.exp(-x * 5) * np.minimum(1, x / 0.003)

    x = _tt(0.4)
    surdo = np.sin(2 * np.pi * np.cumsum(60 + 30 * np.exp(-x * 20)) / SR) * np.exp(-x * 6)
    x = _tt(0.05)
    shaker = np.diff(rng.standard_normal(len(x) + 1)) * np.exp(-x * 60)
    beat = 60 / 112
    prog = [(110.0, [220.0, 261.63, 329.63, 392.0]), (73.42, [185.0, 220.0, 261.63, 329.63]),
            (98.0, [246.94, 293.66, 369.99, 440.0]), (82.41, [207.65, 246.94, 293.66, 369.99])]
    starts, acc = {}, 0.0
    for k, *_ in SCRIPT:
        starts[k] = acc
        acc += TL.dur[k]
    under0, under1 = starts["flood"] + ls("flood", 1), starts["mind"]
    t, bar = 0.0, 0
    total = E.TOTAL
    while t < total:
        root, ch = prog[bar % 4]
        sub = under0 <= t < under1
        for b in range(4):
            add(surdo, t + b * beat, 0.6 if b % 2 else 0.3)
            if not sub:
                for q in range(4):
                    add(shaker, t + (b + q / 4) * beat, 0.1)
        for s_ in (0, 0.75, 1.5, 2.5, 3.25):
            for f in ch:
                add(keys(f * (0.5 if sub else 1), 0.6 if sub else 0.45), t + s_ * beat, 0.03)
        for b, step in enumerate((1, 1.5, 2, 1.335)):
            xb = _tt(beat * 0.95)
            add((np.sin(2 * np.pi * root * step * xb) + 0.3 * np.sin(4 * np.pi * root * step * xb)) * np.exp(-xb * 2.5),
                t + b * beat, 0.3)
        t += 4 * beat
        bar += 1
    s0, s1 = int(under0 * SR), int(min(n, under1 * SR))   # muffle the flood like it's underwater
    seg = out[s0:s1]
    out[s0:s1] = np.convolve(seg, np.ones(60) / 60, mode="same") * 1.6
    x = np.arange(s1 - s0) / SR
    out[s0:s1] += np.sin(2 * np.pi * 55 * x) * 0.08 + np.sin(2 * np.pi * 82.4 * x) * 0.05
    voice = TL.track(n, SR)
    out = narrate.duck(out, voice, SR, depth=0.55)
    fade = int(1.5 * SR)
    end = int(total * SR)
    out[end - fade:end] *= np.linspace(1, 0, fade)
    out[end:] = 0
    return out * 0.65 + voice * 1.7


if __name__ == "__main__":
    print(f"total {TOTAL:.1f}s; " + ", ".join(f"{k} {TL.dur[k]:.1f}" for k, *_ in SCRIPT))
    E.main("did_we_build_agi.mp4", SCENES, music_fn, M.extra_sfx)

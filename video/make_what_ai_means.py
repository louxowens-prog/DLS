#!/usr/bin/env python3
"""Render "NOT A LIBRARY. A MAP.": a <2 min vertical short on what "artificial intelligence"
means and what a language model actually is, styled after the comic-book look of
Spider-Man: Into the Spider-Verse (2018): off-register colour, Ben-Day halftone dots,
animation on twos, tilted ink-bordered panels, yellow caption boxes, onomatopoeia and
glitching cuts, over a boom-bap beat. No characters or logos, just the visual language.
Female narration (Kokoro af_bella).

    python3 make_what_ai_means.py                  # -> out/not_a_library_a_map.mp4
    python3 make_what_ai_means.py --preview 3 17   # frames -> out/preview/not_a_library_a_map/
"""
import math
import textwrap

import numpy as np
from PIL import Image, ImageDraw

import make_video as E
import narrate
from make_video import G, H, W, cue, ease_in_out, ease_out_back, ease_out_cubic, font, pop

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BANG = "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf"
INK = (12, 8, 20)
WHITE = (255, 255, 255)
MAG = (255, 20, 140)
CYAN = (0, 200, 255)
YEL = (255, 228, 0)
RED = (235, 30, 50)
PURP = (80, 30, 160)
NIGHT = (30, 12, 60)
PAPER = (250, 244, 225)

SCRIPT = [
    ("hook", 0.4, ["Artificial intelligence. Two words everyone uses. Almost nobody defines."], 0.3),
    ("art", 0.3, ["First: artificial doesn't mean fake. It means built, not born.",
                  "Artificial light is real light. An artificial heart really pumps blood.",
                  "So artificial intelligence means some of the work of thinking is done by an engineered system, "
                  "instead of a brain."], 0.3),
    ("tasks", 0.3, ["Perception. Learning. Planning. Communicating. Deciding. Standards bodies like the U.S. "
                    "agency NIST count all of these as things AI systems do.",
                    "The term itself was coined in 1956, for a summer workshop at Dartmouth."], 0.3),
    ("history", 0.3, ["By that definition, the chess computer that beat Kasparov in 1997 was AI. AlphaGo, in 2016, "
                      "was AI. Face unlock, self-driving systems, chatbots. All AI.",
                      "Funny thing: once AI works, people stop calling it AI. It's called the AI effect."], 0.3),
    ("question", 0.3, ["So the real question isn't: do we have AI? We do. It's: how general is it?"], 0.4),
    ("myth", 0.3, ["Now, the biggest myth about chatbots: that inside is a giant database of human knowledge.",
                   "There isn't. No searchable library of documents sits inside the model."], 0.3),
    ("how", 0.3, ["Instead, training shows it huge amounts of text and images, and nudges billions of numbers, "
                  "called parameters, to get better at predicting what comes next."], 0.3),
    ("map", 0.3, ["Nobody writes a rule saying capitals belong to countries.",
                  "But the model learns a kind of map, where concepts are points and relationships are directions. "
                  "France to Paris is the same arrow as Japan to Tokyo.",
                  "Scale that up, and the map captures language, geography, code, math, cause and effect, "
                  "even patterns of reasoning."], 0.3),
    ("caveat", 0.3, ["That's also why it can be confidently wrong. It doesn't look facts up. "
                     "It reconstructs them from patterns, unless it's connected to search."], 0.3),
    ("outro", 0.3, ["So it's not a library. It's a learned map of how human knowledge connects.",
                    "And that's a much stranger, much more interesting thing."], 2.0),
]
TL = narrate.Timeline(SCRIPT, sid=1, speed=1.12)
ls, le = TL.start, TL.end


def on_twos(t):
    return math.floor(t * 12) / 12


# ---------------------------------------------------------------- comic primitives

_bg = {}


def city(t, top=NIGHT, bot=MAG):
    key = (top, bot)
    if key not in _bg:
        a = np.linspace(0, 1, H)[:, None, None]
        arr = np.broadcast_to(np.array(top) * (1 - a) + np.array(bot) * a, (H, W, 3)).copy()
        Y, X = np.mgrid[0:H, 0:W]
        dots = ((X % 14 - 7) ** 2 + (Y % 14 - 7) ** 2) < (2 + 5 * (Y / H)) ** 2
        arr[dots] *= 0.7
        img = Image.fromarray(arr.astype(np.uint8))
        d = ImageDraw.Draw(img)
        rng = np.random.default_rng(3)
        x = 0
        while x < W:
            w, h = rng.integers(60, 150), rng.integers(200, 700)
            d.rectangle([x, H - h, x + w, H], fill=INK)
            for wy in range(H - h + 20, H - 20, 40):
                for wx in range(x + 12, x + w - 12, 30):
                    if rng.random() < 0.35:
                        d.rectangle([wx, wy, wx + 12, wy + 18], fill=YEL)
            x += w + rng.integers(0, 20)
        _bg[key] = img
    G.img = _bg[key].copy()
    G.draw = ImageDraw.Draw(G.img)


def panel(box, fill, tilt=0.0, border=12):
    x0, y0, x1, y1 = box
    dx = tilt * (y1 - y0)
    pts = [(x0 + dx, y0), (x1 + dx, y0), (x1 - dx, y1), (x0 - dx, y1)]
    G.draw.polygon([(x + 14, y + 14) for x, y in pts], fill=INK)
    G.draw.polygon(pts, fill=fill)
    G.draw.line(pts + [pts[0]], fill=INK, width=border, joint="curve")


def bang(t, at, xy, s, size, col=YEL, edge=INK, angle_shift=0.0, until=None):
    """Onomatopoeia / comic headline with an offset drop and pop-in."""
    if t < at or (until is not None and t >= until):
        return
    k = pop(t, at, 0.22)
    size = size * k
    if size < 8:
        return
    f = font(BANG, size)
    lines = s.split("\n")
    wmax = max(f.getlength(ln) for ln in lines)
    if wmax > W - 80:
        size *= (W - 80) / wmax
        f = font(BANG, size)
    sw = max(3, int(size * 0.08))
    kw = dict(font=f, anchor="mm", align="center", spacing=int(size * 0.05), stroke_width=sw, stroke_fill=edge)
    off = max(4, size * 0.07)
    G.draw.multiline_text((xy[0] + off, xy[1] + off), s, fill=CYAN if col != CYAN else MAG, **kw)
    G.draw.multiline_text(xy, s, fill=col, **kw)


def burst(cx, cy, r, col=YEL, n=14, t=0.0):
    pts = []
    for i in range(n * 2):
        rr = r if i % 2 == 0 else r * 0.62
        a = i * math.pi / n + t * 0.4
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    G.draw.polygon([(x + 10, y + 10) for x, y in pts], fill=INK)
    G.draw.polygon(pts, fill=col, outline=INK, width=8)


def caption_box(t, key):
    a = TL.active(key, t)
    if not a:
        return
    txt = "\n".join(textwrap.wrap(a[0].upper(), 30))
    f = font(BOLD, 40)
    bb = G.draw.multiline_textbbox((W / 2, 1600), txt, font=f, anchor="mm", align="center", spacing=8)
    r = [bb[0] - 30, bb[1] - 22, bb[2] + 30, bb[3] + 22]
    G.draw.rectangle([r[0] + 10, r[1] + 10, r[2] + 10, r[3] + 10], fill=INK)
    G.draw.rectangle(r, fill=YEL, outline=INK, width=6)
    G.draw.multiline_text((W / 2, 1600), txt, font=f, fill=INK, anchor="mm", align="center", spacing=8)


def label(xy, s, size=34, col=INK, fnt=BOLD):
    G.draw.multiline_text(xy, s, font=font(fnt, size), fill=col, anchor="mm", align="center")


def heart(cx, cy, s, col):
    pts = [(cx + s * 16 * math.sin(u) ** 3 / 16,
            cy - s * (13 * math.cos(u) - 5 * math.cos(2 * u) - 2 * math.cos(3 * u) - math.cos(4 * u)) / 16)
           for u in np.linspace(0, 2 * math.pi, 40)]
    G.draw.polygon(pts, fill=col, outline=INK, width=6)


# ---------------------------------------------------------------- scenes


def s_hook(t):
    t2 = on_twos(t)
    city(t)
    bang(t, 0.2, (W / 2, 470), "ARTIFICIAL", 150, YEL)
    bang(t, 0.5, (W / 2, 640), "INTELLIGENCE", 140, CYAN)
    p = TL.phrases("hook", 0, ["Almost nobody"])[0]
    if t >= p:
        burst(W / 2, 1000, 230 * pop(t, p, 0.25), MAG, t=t2)
        bang(t, p, (W / 2, 1000), "?!", 200, WHITE)
    caption_box(t, "hook")


def s_art(t):
    t2 = on_twos(t)
    city(t, (20, 10, 50), (0, 90, 160))
    a1, a2 = ls("art", 1), ls("art", 2)
    if t < a1:
        panel((80, 250, W - 80, 1200), PAPER, -0.03)
        label((W / 2, 400), "ar·ti·fi·cial", 70, INK)
        label((W / 2, 480), "(adjective)", 36, (120, 110, 100))
        bang(t, 0.8, (W / 2, 700), "≠ FAKE", 130, RED)
        bang(t, TL.phrases("art", 0, ["built"])[0], (W / 2, 950), "= BUILT,\nNOT BORN", 110, CYAN)
    elif t < a2:
        p = TL.phrases("art", 1, ["An artificial heart"])[0]
        panel((70, 240, W / 2 - 10, 1250), (30, 30, 60), 0.02)
        k = 0.6 + 0.4 * abs(math.sin(t2 * 4))
        for i in range(10, 0, -1):
            c = tuple(int(v * (1 - i / 11) * k + 30 * (i / 11)) for v in YEL)
            G.draw.ellipse([W / 4 - 18 * i, 620 - 18 * i, W / 4 + 18 * i, 620 + 18 * i], fill=c)
        G.draw.ellipse([W / 4 - 80, 540, W / 4 + 80, 700], fill=(255, 250, 200), outline=INK, width=6)
        G.draw.rectangle([W / 4 - 45, 700, W / 4 + 45, 790], fill=(160, 160, 170), outline=INK, width=6)
        label((W / 4, 1000), "REAL\nLIGHT", 60, YEL)
        if t >= p:
            panel((W / 2 + 10, 240, W - 70, 1250), (255, 210, 220), -0.02)
            beat = 1 + 0.12 * max(0, math.sin(t2 * 9))
            heart(3 * W / 4, 660, 170 * beat, RED)
            G.draw.line([(3 * W / 4 - 40, 470), (3 * W / 4 - 60, 380)], fill=(150, 150, 160), width=24)
            G.draw.line([(3 * W / 4 + 40, 470), (3 * W / 4 + 60, 380)], fill=(150, 150, 160), width=24)
            label((3 * W / 4, 1000), "REALLY\nPUMPS", 60, RED)
            bang(t, p + 0.6, (3 * W / 4, 1150), "BA-DUM!", 70, MAG)
    else:
        G.draw.rectangle([0, 0, W / 2, 1400], fill=(255, 170, 190))
        G.draw.rectangle([W / 2, 0, W, 1400], fill=(20, 40, 70))
        G.draw.line([(W / 2, 0), (W / 2, 1400)], fill=INK, width=14)
        G.draw.ellipse([W / 4 - 190, 520, W / 4 + 190, 880], fill=(255, 130, 170))
        for i in range(9):   # brain
            a = i * 0.7
            G.draw.arc([W / 4 - 170 + 20 * math.sin(a), 540 + 18 * math.cos(a), W / 4 + 170 - 20 * math.sin(a),
                        860 - 18 * math.cos(a)], 180 + i * 12, 360 - i * 10, fill=(200, 60, 110), width=10)
        G.draw.ellipse([W / 4 - 190, 520, W / 4 + 190, 880], outline=INK, width=10)
        G.draw.rectangle([3 * W / 4 - 150, 550, 3 * W / 4 + 150, 850], fill=(40, 60, 90), outline=CYAN, width=8)
        for k in range(6):
            for sg in (-1, 1):
                G.draw.line([(3 * W / 4 + sg * 150, 580 + k * 50), (3 * W / 4 + sg * 200, 580 + k * 50)], fill=CYAN, width=6)
        label((3 * W / 4, 700), "AI", 110, CYAN)
        label((W / 4, 1000), "BORN", 70, INK)
        label((3 * W / 4, 1000), "BUILT", 70, CYAN)
        bang(t, a2 + 0.5, (W / 2, 330), "SAME JOB,\nDIFFERENT HARDWARE", 70, YEL)
    caption_box(t, "art")


TASKS = [("Perception", "PERCEIVE", "👁"), ("Learning", "LEARN", ""), ("Planning", "PLAN", ""),
         ("Communicating", "TALK", ""), ("Deciding", "DECIDE", "")]


def s_tasks(t):
    t2 = on_twos(t)
    city(t, (60, 0, 50), (240, 60, 40))
    ts = TL.phrases("tasks", 0, [p for p, _, _ in TASKS])
    cols = [CYAN, YEL, MAG, WHITE, (140, 255, 90)]
    for i, ((_, lab, _), at) in enumerate(zip(TASKS, ts)):
        cue("pop", at)
        if t < at:
            continue
        k = ease_out_back((t - at) / 0.3)
        x, y = (290, 790)[i % 2] if i < 4 else W / 2, 330 + (i // 2) * 290
        w = 220 * k
        panel((x - w, y - 110 * k, x + w, y + 110 * k), cols[i], (-1) ** i * 0.05)
        if k > 0.7:
            label((x, y), lab, 64, INK)
    if TL.phrases("tasks", 0, ["Standards"])[0] <= t < ls("tasks", 1):
        bang(t, TL.phrases("tasks", 0, ["NIST"])[0], (W / 2, 1230), "NIST", 110, WHITE)
    at = ls("tasks", 1)
    if t >= at:
        k = ease_out_cubic((t - at) / 0.3)
        G.draw.rectangle([0, 0, W, 1400], fill=PAPER)
        burst(W / 2, 700, 380 * k, YEL, 16, t2)
        bang(t, at + 0.1, (W / 2, 640), "1956", 220, RED)
        bang(t, at + 0.4, (W / 2, 830), "DARTMOUTH", 90, INK, edge=WHITE)
        label((W / 2, 1180), "the summer the term\n\"artificial intelligence\" was coined", 40, INK)
    caption_box(t, "tasks")


def chess_king(x, y, s):
    G.draw.rectangle([x - 50 * s, y + 60 * s, x + 50 * s, y + 90 * s], fill=WHITE, outline=INK, width=5)
    G.draw.polygon([(x - 35 * s, y + 60 * s), (x + 35 * s, y + 60 * s), (x + 20 * s, y - 40 * s), (x - 20 * s, y - 40 * s)],
                   fill=WHITE, outline=INK, width=5)
    G.draw.ellipse([x - 30 * s, y - 80 * s, x + 30 * s, y - 30 * s], fill=WHITE, outline=INK, width=5)
    G.draw.rectangle([x - 6 * s, y - 120 * s, x + 6 * s, y - 75 * s], fill=INK)
    G.draw.rectangle([x - 20 * s, y - 105 * s, x + 20 * s, y - 93 * s], fill=INK)


def s_history(t):
    t2 = on_twos(t)
    city(t)
    items = [("Kasparov", "1997", "CHESS"), ("AlphaGo", "2016", "GO"), ("Face unlock", "📱", "FACE UNLOCK"),
             ("self-driving", "🚗", "SELF-DRIVING"), ("chatbots", "💬", "CHATBOTS")]
    ts = TL.phrases("history", 0, [p for p, _, _ in items])
    a1 = ls("history", 1)
    if t < a1:
        for i, ((_, yr, lab), at) in enumerate(zip(items, ts)):
            cue("pop", at)
            if t < at:
                continue
            y = 280 + i * 225
            k = ease_out_cubic((t - at) / 0.25)
            x0 = -700 + 780 * k
            panel((x0, y - 90, x0 + 900, y + 90), [PAPER, (200, 240, 255), YEL, (255, 200, 225), (200, 255, 200)][i],
                  0.04 * (-1) ** i)
            if i == 0:
                chess_king(x0 + 110, y + 10, 0.8)
            elif i == 1:
                for gx in range(4):
                    for gy in range(3):
                        c = INK if (gx + gy) % 2 else WHITE
                        G.draw.ellipse([x0 + 50 + gx * 45, y - 60 + gy * 45, x0 + 90 + gx * 45, y - 20 + gy * 45], fill=c,
                                       outline=INK, width=3)
            label((x0 + 520, y - 20), lab, 58, INK)
            if yr.isdigit():
                label((x0 + 520, y + 45), yr, 40, RED)
            if t >= at + 0.2:
                bang(t, at + 0.2, (x0 + 830, y), "AI", 70, MAG)
    else:
        panel((90, 300, W - 90, 1250), PAPER, -0.02)
        chess_king(W / 2, 640, 2.0)
        p = TL.phrases("history", 1, ["people stop"])[0]
        label((W / 2, 930), "\"AI\"", 110, RED)
        if t >= p:
            k = ease_out_cubic((t - p) / 0.3)
            G.draw.line([(W / 2 - 160, 930), (W / 2 - 160 + 320 * k, 930)], fill=INK, width=22)
            bang(t, p + 0.3, (W / 2, 1070), "just software", 70, CYAN)
        bang(t, TL.phrases("history", 1, ["AI effect"])[0], (W / 2, 220), "THE AI EFFECT", 100, YEL)
    caption_box(t, "history")


def s_question(t):
    city(t, (10, 30, 70), (0, 150, 150))
    p = TL.phrases("question", 0, ["We do", "It's: how"])
    bang(t, 0.3, (W / 2, 330), "DO WE HAVE AI?", 90, WHITE)
    if t >= p[0]:
        k = ease_out_cubic((t - p[0]) / 0.25)
        G.draw.line([(100, 330), (100 + (W - 200) * k, 330)], fill=RED, width=24)
        bang(t, p[0], (W / 2, 470), "WE DO.", 90, YEL)
    if t >= p[1]:
        bang(t, p[1], (W / 2, 720), "HOW GENERAL\nIS IT?", 130, CYAN)
        y = 1050
        G.draw.rounded_rectangle([110, y - 22, W - 110, y + 22], 20, fill=WHITE, outline=INK, width=6)
        pos = 110 + (W - 220) * (0.45 + 0.1 * math.sin(on_twos(t) * 2))
        G.draw.ellipse([pos - 40, y - 40, pos + 40, y + 40], fill=MAG, outline=INK, width=6)
        label((170, y + 80), "NARROW", 40, WHITE)
        label((W - 170, y + 80), "GENERAL", 40, WHITE)
    caption_box(t, "question")


def s_myth(t):
    t2 = on_twos(t)
    city(t, (40, 0, 20), (160, 0, 60))
    a1 = ls("myth", 1)
    panel((80, 260, W - 80, 1250), (60, 40, 30) if t < a1 else (25, 20, 30), 0.02)
    if t < a1:
        for r in range(6):
            for c in range(9):
                h = 90 + (r * 13 + c * 29) % 50
                x, y = 140 + c * 92, 400 + r * 140
                G.draw.rectangle([x, y + 120 - h, x + 70, y + 120], fill=[RED, CYAN, YEL, MAG, WHITE][(r + c) % 5],
                                 outline=INK, width=4)
        bang(t, 0.5, (W / 2, 230), "GIANT DATABASE?", 90, WHITE)
        at = TL.phrases("myth", 0, ["of human"])[0]
        if t >= at:
            k = pop(t, at, 0.2)
            G.draw.rectangle([W / 2 - 260 * k, 680 - 90 * k, W / 2 + 260 * k, 680 + 90 * k], outline=RED, width=16)
            label((W / 2, 680), "MYTH", int(140 * k) or 1, RED)
    else:
        for r in range(6):
            G.draw.line([(130, 520 + r * 140), (W - 130, 520 + r * 140)], fill=(80, 70, 90), width=8)
        bang(t, a1 + 0.1, (W / 2, 700), "NO LIBRARY\nINSIDE", 130, YEL)
        bang(t, a1 + 0.8, (W / 2, 1000), "*crickets*", 60, CYAN)
    caption_box(t, "myth")


def s_how(t):
    t2 = on_twos(t)
    city(t, (0, 20, 60), (0, 110, 200))
    panel((70, 240, W - 70, 760), (15, 15, 35), -0.02)
    for i in range(12 * 7):   # billions of knobs, nudged
        c, r = i % 12, i // 12
        x, y = 140 + c * 72, 300 + r * 64
        a = math.sin(i * 1.7 + t2 * (1 + (i % 5) * 0.4)) * 2.2
        G.draw.ellipse([x - 22, y - 22, x + 22, y + 22], fill=(60, 70, 110), outline=CYAN, width=3)
        G.draw.line([(x, y), (x + 18 * math.cos(a), y + 18 * math.sin(a))], fill=YEL, width=5)
    bang(t, TL.phrases("how", 0, ["billions"])[0], (W / 2, 830), "BILLIONS OF PARAMETERS", 70, YEL)
    at = TL.phrases("how", 0, ["predicting"])[0]
    if t >= at:
        panel((70, 930, W - 70, 1370), PAPER, 0.02)
        label((W / 2, 1000), "The capital of France is ___", 46, INK)
        opts = [("Paris", 0.92), ("Lyon", 0.04), ("nice", 0.02)]
        for i, (w_, p_) in enumerate(opts):
            y = 1090 + i * 85
            k = ease_out_cubic((t - at - 0.3 - i * 0.15) / 0.6)
            G.draw.text((140, y), w_, font=font(BOLD, 44), fill=INK, anchor="lm")
            G.draw.rectangle([330, y - 24, 330 + 560 * p_ * k, y + 24], fill=MAG if i == 0 else (150, 150, 170), outline=INK,
                             width=4)
            G.draw.text((330 + 560 * p_ * k + 20, y), f"{int(p_ * 100 * k)}%", font=font(BOLD, 36), fill=INK, anchor="lm")
    caption_box(t, "how")


CONCEPTS = [("language", 0.25, 0.3), ("geography", 0.7, 0.22), ("code", 0.15, 0.62), ("math", 0.82, 0.55),
            ("cause & effect", 0.45, 0.78), ("reasoning", 0.6, 0.45), ("people", 0.35, 0.5), ("music", 0.85, 0.85),
            ("physics", 0.12, 0.88), ("emotion", 0.55, 0.15)]


def s_map(t):
    t2 = on_twos(t)
    G.img = Image.new("RGB", (W, H), (10, 8, 28))
    G.draw = d = ImageDraw.Draw(G.img)
    for x in range(0, W, 60):
        d.line([(x, 0), (x, 1400)], fill=(30, 25, 70), width=2)
    for y in range(0, 1400, 60):
        d.line([(0, y), (W, y)], fill=(30, 25, 70), width=2)
    a1, a2 = ls("map", 1), ls("map", 2)
    if t < a1:
        panel((100, 420, W - 100, 900), PAPER, -0.03)
        label((W / 2, 560), "RULE #1:", 60, INK)
        label((W / 2, 680), "capitals belong\nto countries", 56, INK)
        k = ease_out_cubic((t - 1.0) / 0.3)
        if k > 0:
            d.line([(150, 900), (150 + (W - 300) * k, 440)], fill=RED, width=22)
            bang(t, 1.1, (W / 2, 1100), "NOBODY WROTE THIS", 70, RED)
    elif t < a2:
        pts = {"France": (260, 850), "Paris": (420, 520), "Japan": (650, 950), "Tokyo": (810, 620),
               "Italy": (300, 1250), "Rome": (460, 920)}
        pa = TL.phrases("map", 1, ["France to Paris", "Japan to Tokyo"])
        wob = lambda i: (3 * math.sin(t2 * 3 + i), 3 * math.cos(t2 * 2.5 + i))
        for i, (name, (x, y)) in enumerate(pts.items()):
            ox, oy = wob(i)
            is_cap = name in ("Paris", "Tokyo", "Rome")
            col = MAG if is_cap else CYAN
            d.ellipse([x + ox - 22, y + oy - 22, x + ox + 22, y + oy + 22], fill=col, outline=WHITE, width=5)
            d.text((x + ox + 34, y + oy), name.upper(), font=font(BOLD, 40), fill=WHITE, anchor="lm")
        for j, (a, b) in enumerate((("France", "Paris"), ("Japan", "Tokyo"), ("Italy", "Rome"))):
            at = pa[min(j, 1)] + (0.9 if j == 2 else 0.2)
            if t < at:
                continue
            k = ease_out_cubic((t - at) / 0.5)
            (x0, y0), (x1, y1) = pts[a], pts[b]
            xe, ye = x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
            d.line([(x0, y0), (xe, ye)], fill=YEL, width=10)
            ang = math.atan2(ye - y0, xe - x0)
            d.polygon([(xe, ye), (xe - 36 * math.cos(ang - 0.4), ye - 36 * math.sin(ang - 0.4)),
                       (xe - 36 * math.cos(ang + 0.4), ye - 36 * math.sin(ang + 0.4))], fill=YEL)
        bang(t, pa[1] + 0.4, (W / 2, 260), "SAME ARROW!", 100, YEL)
        label((W / 2, 370), "\"capital of\" = a direction", 40, WHITE)
    else:
        ts = TL.phrases("map", 2, ["language", "geography", "code", "math", "cause", "reasoning"])
        for i, (name, fx, fy) in enumerate(CONCEPTS):
            at = ts[min(i, len(ts) - 1)] + (0.15 * max(0, i - 5))
            if t < at:
                continue
            x, y = 120 + fx * (W - 240), 250 + fy * 1050
            for j, (_, gx, gy) in enumerate(CONCEPTS[:i]):
                if (i + j) % 3 == 0:
                    d.line([(x, y), (120 + gx * (W - 240), 250 + gy * 1050)], fill=(90, 70, 160), width=3)
            r = 16 + 4 * math.sin(t2 * 4 + i)
            d.ellipse([x - r, y - r, x + r, y + r], fill=[MAG, CYAN, YEL][i % 3], outline=WHITE, width=4)
            d.text((x, y - 44), name.upper(), font=font(BOLD, 36), fill=WHITE, anchor="mm")
    caption_box(t, "map")


def s_caveat(t):
    t2 = on_twos(t)
    city(t, (50, 0, 0), (200, 40, 20))
    burst(W / 2, 520, 330, YEL, 12, t2)
    bang(t, 0.2, (W / 2, 520), "CONFIDENTLY\nWRONG?", 100, RED, edge=INK)
    p = TL.phrases("caveat", 0, ["It doesn't look", "It reconstructs", "unless"])
    if t >= p[0]:
        panel((90, 880, W / 2 - 20, 1250), PAPER, 0.03)
        label((W / 4 + 20, 1000), "LOOK UP", 54, (150, 150, 150))
        k = ease_out_cubic((t - p[0] - 0.4) / 0.3)
        if k > 0:
            d = G.draw
            d.line([(140, 1000), (140 + 330 * k, 1000)], fill=RED, width=16)
    if t >= p[1]:
        panel((W / 2 + 20, 880, W - 90, 1250), (200, 240, 255), -0.03)
        label((3 * W / 4 - 20, 1000), "RE-\nCONSTRUCT", 50, INK)
        bang(t, p[1] + 0.3, (3 * W / 4 - 20, 1170), "YES", 60, CYAN)
    if t >= p[2]:
        label((W / 2, 1320), "(unless it's connected to search)", 38, WHITE)
    caption_box(t, "caveat")


def s_outro(t):
    t2 = on_twos(t)
    G.img = Image.new("RGB", (W, H), (10, 8, 28))
    G.draw = d = ImageDraw.Draw(G.img)
    for i, (name, fx, fy) in enumerate(CONCEPTS):
        x, y = 120 + fx * (W - 240), 250 + fy * 1050
        for j, (_, gx, gy) in enumerate(CONCEPTS):
            if j < i and (i + j) % 2 == 0:
                d.line([(x, y), (120 + gx * (W - 240), 250 + gy * 1050)], fill=(70, 50, 140), width=3)
        d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=[MAG, CYAN, YEL][i % 3])
    p = TL.phrases("outro", 0, ["It's a learned"])[0]
    bang(t, 0.2, (W / 2, 420), "NOT A LIBRARY.", 110, WHITE)
    bang(t, p, (W / 2, 700), "A MAP.", 220, YEL)
    if t >= ls("outro", 1):
        burst(W / 2, 1100, 200 * pop(t, ls("outro", 1)), MAG, 14, t2)
        bang(t, ls("outro", 1) + 0.2, (W / 2, 1100), "WHOA.", 110, WHITE)
    caption_box(t, "outro")


SCENE_FNS = {"hook": s_hook, "art": s_art, "tasks": s_tasks, "history": s_history, "question": s_question,
             "myth": s_myth, "how": s_how, "map": s_map, "caveat": s_caveat, "outro": s_outro}
SCENES = [(TL.dur[k], SCENE_FNS[k]) for k, *_ in SCRIPT]
TOTAL = TL.total

# ---------------------------------------------------------------- print look: off-register ink + halftone + glitch cuts

_Y, _X = np.mgrid[0:H, 0:W]
DOTS = (((_X % 8 - 4) ** 2 + (_Y % 8 - 4) ** 2) < 5).astype(np.uint16)
HALF = (256 - 22 * DOTS)[..., None]
del _X, _Y


def post(arr, fi, t, idx, tl):
    a = arr.copy()
    a[..., 0] = np.roll(arr[..., 0], 5, axis=1)       # red plate slips right
    a[..., 2] = np.roll(arr[..., 2], -5, axis=1)      # blue plate slips left
    a = (a.astype(np.uint16) * HALF >> 8).astype(np.uint8)
    if idx > 0 and tl < 0.25:                          # dimension glitch on every cut
        rng = np.random.default_rng(fi)
        for _ in range(9):
            y0 = int(rng.integers(0, H - 80))
            h = int(rng.integers(20, 90))
            a[y0:y0 + h] = np.roll(a[y0:y0 + h], int(rng.integers(-160, 160)), axis=1)
            if rng.random() < 0.4:
                a[y0:y0 + h, :, int(rng.integers(0, 3))] = 255
    return a


# ---------------------------------------------------------------- score: boom-bap beat + scratches

SR = E.SR


def _tt(d):
    return np.arange(int(d * SR)) / SR


def scratch(d=0.35, seed=0):
    rng = np.random.default_rng(seed)
    x = _tt(d)
    rate = 1 + 0.9 * np.sin(2 * np.pi * 7 * x)
    src = np.convolve(rng.standard_normal(len(x) * 2), np.ones(6) / 6, mode="same")
    idx = np.clip(np.cumsum(np.abs(rate)), 0, len(src) - 1).astype(int)
    return src[idx] * np.sin(np.pi * x / d)


def extra_sfx(sr):
    x = _tt(0.12)
    pop_ = np.sin(2 * np.pi * np.cumsum(300 + 900 * np.exp(-x * 40)) / SR) * np.exp(-x * 25)
    return {"pop": (pop_, 0.3), "whoosh": (scratch(0.35, 1), 0.4)}


def music_fn(n):
    rng = np.random.default_rng(2018)
    out = np.zeros(n)

    def add(sig, t, g):
        i = int(t * SR)
        if i < n:
            j = min(n, i + len(sig))
            out[i:j] += sig[: j - i] * g

    x = _tt(0.5)
    kick = np.sin(2 * np.pi * np.cumsum(45 + 90 * np.exp(-x * 25)) / SR) * np.exp(-x * 6)
    x = _tt(0.3)
    snare = (rng.standard_normal(len(x)) * np.exp(-x * 14) * 0.6 + np.sin(2 * np.pi * 180 * x) * np.exp(-x * 25) * 0.4)
    x = _tt(0.05)
    hat = np.diff(rng.standard_normal(len(x) + 1)) * np.exp(-x * 80)
    beat = 60 / 90
    roots = [55.0, 55.0, 43.65, 49.0]            # A1 A1 F1 G1
    chords = [[220.0, 261.63, 329.63], [220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [196.0, 246.94, 293.66]]
    t, bar = 0.0, 0
    total = E.TOTAL
    while t < total:
        root = roots[bar % 4]
        for step, g in ((0, 1.0), (1.75, 0.6), (2.5, 0.8)):
            add(kick, t + step * beat, 0.8 * g)
        for b in (1, 3):
            add(snare, t + b * beat, 0.55)
        for h in range(8):
            sw = 0.08 if h % 2 else 0.0
            add(hat, t + (h / 2 + sw) * beat, 0.12 if h % 2 else 0.2)
        xb = _tt(beat * 2)
        glide = root * (1 + 0.5 * np.exp(-xb * 20))
        bass = np.sin(2 * np.pi * np.cumsum(glide) / SR) * np.exp(-xb * 1.2)
        add(bass, t, 0.45)
        add(bass, t + 2.5 * beat, 0.35)
        for f in chords[bar % 4]:
            xs = _tt(0.25)
            add((np.sign(np.sin(2 * np.pi * f * xs)) * 0.3 + np.sin(2 * np.pi * f * 2 * xs)) * np.exp(-xs * 9),
                t + 0.5 * beat, 0.03)
        t += 4 * beat
        bar += 1
    starts, acc = [], 0.0
    for k, *_ in SCRIPT:
        starts.append(acc)
        acc += TL.dur[k]
    for i, s in enumerate(starts[1:]):
        add(scratch(0.35, i + 3), s - 0.05, 0.35)
    voice = TL.track(n, SR)
    out = narrate.duck(out, voice, SR, depth=0.6)
    fade = int(1.5 * SR)
    end = int(total * SR)
    out[end - fade:end] *= np.linspace(1, 0, fade)
    out[end:] = 0
    return out * 0.7 + voice * 1.7


E.SCENE_CUT_FLASH = False
E.POST_FX = post

if __name__ == "__main__":
    print(f"total {TOTAL:.1f}s; " + ", ".join(f"{k} {TL.dur[k]:.1f}" for k, *_ in SCRIPT))
    E.main("not_a_library_a_map.mp4", SCENES, music_fn, extra_sfx)

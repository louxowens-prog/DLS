#!/usr/bin/env python3
"""Render "EVERY STUDENT GETS A TUTOR": a <2 min vertical short on AI in education, styled
after the hyper-kinetic, hand-drawn, mixed-style animation of Mind Game (2004): boiling
scribble lines animated on twos, loud flat colour, fisheye tunnels, inverted-frame cuts and
a life-flashing-before-your-eyes montage. Female narration (Kokoro af_bella, student af_sarah).

    python3 make_education.py                  # -> out/every_student_a_tutor.mp4
    python3 make_education.py --preview 3 17   # frames -> out/preview/every_student_a_tutor/
"""
import math
import textwrap

import numpy as np
from PIL import ImageDraw, ImageOps

import make_video as E
import narrate
from make_video import G, H, W, cue, ease_in_out, ease_out_back, ease_out_cubic, font, pop

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_I = "/usr/share/fonts/truetype/freefont/FreeSansBoldOblique.ttf"
INK = (14, 10, 16)
PAPER = (246, 240, 224)
RED = (235, 40, 45)
YEL = (255, 214, 30)
CYAN = (40, 210, 230)
PINK = (255, 90, 160)
ORNG = (255, 130, 30)
GRN = (70, 200, 110)
PURP = (120, 60, 200)
WHITE = (255, 255, 255)
SKIN = [(250, 205, 170), (225, 170, 130), (190, 130, 95), (140, 95, 65), (255, 220, 190), (170, 115, 80)]

S = 3  # student voice: af_sarah
SCRIPT = [
    ("hook", 1.0, ["One teacher. Thirty students. One pace for everybody.",
                   "Now imagine every single student gets their own tutor."], 0.5),
    ("bloom", 0.4, ["In 1984, researcher Benjamin Bloom found that tutored students did better than "
                    "about ninety-eight percent of students in a normal classroom.",
                    "The catch? Tutors were expensive. For most of history, that kind of attention "
                    "was for the wealthy."], 0.5),
    ("powers", 0.4, ["An AI tutor can explain one idea five different ways, spot the exact moment you got lost, "
                     "and adjust the difficulty as you go.",
                     "Instant feedback. Endless practice problems. Infinite patience.",
                     "It can translate the lesson, coach your pronunciation, role-play a conversation, "
                     "and bring back what you're about to forget."], 0.4),
    ("calc", 0.3, ["Watch a student stuck on calculus.",
                   (S, "Explain derivatives using cars."),
                   "A derivative is your speedometer. How fast your position is changing, right now.",
                   (S, "Now show me visually."),
                   "It's the slope of the curve at one exact point.",
                   (S, "Give me five problems. Then show me where I went wrong."),
                   "Line three. You forgot the chain rule."], 0.5),
    ("who", 0.3, ["This matters most for students with learning differences, language barriers, "
                  "no good teacher nearby, unusual schedules, gaps in their schooling, "
                  "or interests way beyond their grade."], 0.5),
    ("teach", 0.3, ["And teachers get help too. Lesson plans, practice sets, quick grading, "
                    "and an early warning when a student is quietly falling behind.",
                    "Less paperwork. More time for the human part."], 0.5),
    ("warn", 0.3, ["Three warnings.",
                   "If it just hands you answers, you learn nothing. Ask it to quiz you instead.",
                   "It can be wrong. Check it.",
                   "And it only helps the people who can reach it."], 0.4),
    ("outro", 0.3, ["A personal tutor for everyone used to be a fantasy.",
                    "Now the question is how we use it. Use it to think harder, not less."], 2.2),
]
TL = narrate.Timeline(SCRIPT, sid=1, speed=1.1)
ls, le = TL.start, TL.end

# ---------------------------------------------------------------- hand-drawn primitives


def nz(*k):
    """Deterministic noise in [-1, 1]."""
    v = math.sin(sum(x * c for x, c in zip(k, (12.9898, 78.233, 37.719, 11.13, 5.71)))) * 43758.5453
    return (v - math.floor(v)) * 2 - 1


class Ctx:
    b = 0          # boil frame: lines re-drawn 12x a second ("on twos")
    montage = False


def wob(pts, amp, seed):
    return [(x + amp * nz(seed, i, Ctx.b, 1), y + amp * nz(seed, i, Ctx.b, 2)) for i, (x, y) in enumerate(pts)]


def sketch(pts, col=INK, width=6, amp=3, seed=0, closed=False):
    """Two slightly different passes of a wobbly line, like a pencil going over it twice."""
    p = list(pts) + ([pts[0]] if closed else [])
    G.draw.line(wob(p, amp, seed), fill=col, width=width, joint="curve")
    G.draw.line(wob(p, amp * 0.8, seed + 99), fill=col, width=max(2, width // 3), joint="curve")


def blob(x, y, rx, ry, fill, seed, amp=0.05, n=20, outline=INK, width=6):
    pts = [(x + rx * (1 + amp * nz(seed, i, Ctx.b)) * math.cos(2 * math.pi * i / n),
            y + ry * (1 + amp * nz(seed, i, Ctx.b, 7)) * math.sin(2 * math.pi * i / n)) for i in range(n)]
    if fill:
        G.draw.polygon(pts, fill=fill)
    sketch(pts, outline, width, 2, seed, closed=True)


def scrawl(t, at, xy, s, size, col=WHITE, until=None, stroke=None, jitter=0.06):
    """Hand-lettered text: every glyph jitters on each boil frame."""
    if t < at or (until is not None and t >= until):
        return
    size *= pop(t, at, 0.25)
    if size < 8:
        return
    f = font(FONT, size)
    lines = s.split("\n")
    widest = max(f.getlength(ln) for ln in lines)
    if widest > W - 90:
        size *= (W - 90) / widest
        f = font(FONT, size)
    sw = stroke if stroke is not None else max(3, int(size * 0.09))
    lh = size * 1.12
    y0 = xy[1] - lh * (len(lines) - 1) / 2
    for li, ln in enumerate(lines):
        x = xy[0] - f.getlength(ln) / 2
        for ci, ch in enumerate(ln):
            dx = size * jitter * nz(li, ci, Ctx.b, 3) * 0.5
            dy = size * jitter * nz(li, ci, Ctx.b, 4)
            G.draw.text((x + dx, y0 + li * lh + dy), ch, font=f, fill=col, anchor="lm", stroke_width=sw, stroke_fill=INK)
            x += f.getlength(ch)


def head(x, y, r, seed, t, skin=None, mood="ok", hair=INK):
    skin = skin or SKIN[seed % len(SKIN)]
    blob(x, y, r, r * 1.05, skin, seed)
    hp = [(x + r * 1.02 * math.cos(math.pi + math.pi * i / 10),
           y - r * 0.15 + r * 1.02 * math.sin(math.pi + math.pi * i / 10) - (r * 0.25 if i % 2 else 0))
          for i in range(11)]
    G.draw.polygon(hp + [(x + r, y - r * 0.1), (x - r, y - r * 0.1)], fill=hair)
    for sx in (-1, 1):
        ex, ey = x + sx * r * 0.33, y + r * 0.12
        G.draw.ellipse([ex - r * 0.1, ey - r * 0.14, ex + r * 0.1, ey + r * 0.14], fill=INK)
    if mood == "ok":
        sketch([(x - r * 0.25, y + r * 0.55), (x, y + r * 0.62), (x + r * 0.25, y + r * 0.55)], INK, 4, 1.5, seed + 3)
    elif mood == "sad":
        sketch([(x - r * 0.22, y + r * 0.64), (x, y + r * 0.55), (x + r * 0.22, y + r * 0.64)], INK, 4, 1.5, seed + 3)
    else:
        G.draw.ellipse([x - r * 0.22, y + r * 0.4, x + r * 0.22, y + r * 0.72], fill=INK)


def spark(x, y, r, t, seed=0, col=CYAN):
    """The AI tutor: a little scribbled star with eyes."""
    if r < 3:
        return
    bob = math.sin(t * 6 + seed) * r * 0.15
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.5
        a = -math.pi / 2 + i * math.pi / 5 + t * 0.8
        pts.append((x + rr * math.cos(a), y + bob + rr * math.sin(a)))
    G.draw.polygon(wob(pts, r * 0.05, seed), fill=col)
    sketch(pts, INK, max(3, int(r * 0.1)), r * 0.04, seed, closed=True)
    for sx in (-1, 1):
        G.draw.ellipse([x + sx * r * 0.2 - r * 0.07, y + bob - r * 0.12, x + sx * r * 0.2 + r * 0.07, y + bob + r * 0.06],
                       fill=INK)


def hatch_bg(col, seed, ink=None, n=60):
    G.draw.rectangle([0, 0, W, H], fill=col)
    ink = ink or tuple(max(0, c - 40) for c in col)
    for i in range(n):
        x, y = (nz(seed, i, Ctx.b // 2, 1) + 1) / 2 * W, (nz(seed, i, Ctx.b // 2, 2) + 1) / 2 * H
        L = 40 + 40 * (nz(seed, i, 5) + 1)
        G.draw.line([(x, y), (x + L, y - L * 0.6)], fill=ink, width=5)


def tunnel(t, c1, c2, cx=W / 2, cy=H * 0.42, speed=700):
    G.draw.rectangle([0, 0, W, H], fill=c1)
    rs = sorted([((k * 150 + t * speed) % 1800) for k in range(12)], reverse=True)
    for i, r in enumerate(rs):
        col = c2 if int((r - t * speed) // 150 + 100) % 2 else c1
        G.draw.ellipse([cx - r * 1.1, cy - r, cx + r * 1.1, cy + r], fill=col)


def new_frame(t):
    Ctx.b = int(t * 12)
    if G.img is None or G.img.size != (W, H):
        from PIL import Image
        G.img = Image.new("RGB", (W, H))
    G.draw = ImageDraw.Draw(G.img)


def subtitle(t, key):
    if Ctx.montage:
        return
    a = TL.active(key, t)
    if not a:
        return
    s, sid = a
    txt = "\n".join(textwrap.wrap(s, 32))
    f = font(FONT, 44)
    bb = G.draw.multiline_textbbox((W / 2, 1530), txt, font=f, anchor="mm", align="center", spacing=8)
    G.draw.rectangle([bb[0] - 24, bb[1] - 16, bb[2] + 24, bb[3] + 18], fill=INK)
    G.draw.multiline_text((W / 2, 1530), txt, font=f, fill=YEL if sid == S else WHITE, anchor="mm", align="center",
                          spacing=8)


# ---------------------------------------------------------------- scenes


def s_hook(t):
    new_frame(t)
    hatch_bg(YEL, 1)
    ones = t >= ls("hook", 1) + 0.3
    scrawl(t, 0.3, (W / 2, 230), "1 : 1" if ones else "1 : 30", 150, RED if ones else WHITE)
    if ones:
        E.impact(t, ls("hook", 1) + 0.3, 20, "boom", 0.0)
        cue("boom", ls("hook", 1) + 0.3)
    head(W / 2, 470, 80, 7, t, mood="o" if not ones else "ok")
    for i in range(30):
        at = 0.35 + i * 0.025
        if t < at:
            continue
        r, c = divmod(i, 6)
        x, y = 115 + c * 170, 700 + r * 150
        k = pop(t, at, 0.2)
        head(x, y, 46 * k, i, t, mood="sad" if not ones else "ok")
        ta = ls("hook", 1) + 0.4 + i * 0.035
        cue("pop", ta) if i % 5 == 0 else None
        if t >= ta:
            spark(x + 55, y - 45, 26 * pop(t, ta, 0.2), t, i)
    subtitle(t, "hook")


def s_bloom(t):
    new_frame(t)
    if t < ls("bloom", 1):
        hatch_bg(CYAN, 2)
        scrawl(t, 0.2, (W / 2, 210), "1984 · BENJAMIN BLOOM", 58, WHITE)
        base, x0, sig, hgt = 1180, 330, 105, 440
        cls = [(x, base - hgt * math.exp(-((x - x0) / sig) ** 2 / 2)) for x in range(60, 1030, 12)]
        tut = [(x, base - hgt * math.exp(-((x - x0 - 2 * sig) / sig) ** 2 / 2)) for x in range(60, 1030, 12)]
        k = ease_out_cubic((t - 0.5) / 0.8)
        n = int(len(cls) * k)
        if n > 1:
            G.draw.polygon(cls[:n] + [(cls[n - 1][0], base), (60, base)], fill=(200, 200, 205))
            sketch(cls[:n], INK, 7, 3, 1)
        k2 = ease_out_cubic((t - 1.6) / 0.8)
        n2 = int(len(tut) * k2)
        if n2 > 1:
            G.draw.polygon(tut[:n2] + [(tut[n2 - 1][0], base), (60, base)], fill=PINK)
            sketch(cls[:n], INK, 5, 3, 3)
            sketch(tut[:n2], INK, 7, 3, 2)
        sketch([(50, base), (1030, base)], INK, 8, 2, 4)
        scrawl(t, 0.9, (230, base + 60), "CLASSROOM", 40, INK, stroke=0)
        scrawl(t, 2.0, (760, base + 60), "1-ON-1 TUTOR", 40, RED, stroke=0)
        if t >= 2.4:
            y = base - hgt - 40
            sketch([(x0, y), (x0 + 2 * sig, y)], INK, 8, 2, 5)
            G.draw.polygon([(x0 + 2 * sig + 26, y), (x0 + 2 * sig - 6, y - 18), (x0 + 2 * sig - 6, y + 18)], fill=INK)
            scrawl(t, 2.4, (x0 + sig, y - 50), "+2σ", 60, INK, stroke=0)
        p = TL.phrases("bloom", 0, ["ninety-eight"])[0]
        scrawl(t, p, (W / 2, 390), "BEATS 98%", 120, RED)
        E.impact(t, p, 16, "boom", 0.0)
    else:
        tunnel(t, RED, (170, 20, 30), speed=500)
        at = ls("bloom", 1)
        for i in range(24):
            y = ((t - at) * 500 + i * 190) % 1700 - 100
            scrawl(t, at, (80 + (i * 173) % 920, y), "$", 90, YEL)
        scrawl(t, at + 0.2, (W / 2, 560), "$$$", 220, YEL)
        scrawl(t, at + 1.4, (W / 2, 860), "TUTORS =\nRICH KIDS ONLY", 90, WHITE)
    subtitle(t, "bloom")


CARDS = [
    (0, "explain one idea", "5 WAYS TO\nEXPLAIN IT", (PURP, (160, 90, 240))),
    (0, "spot the exact", "SPOTS WHERE\nYOU GOT LOST", (ORNG, (255, 170, 60))),
    (0, "adjust the difficulty", "LEVELS UP\nWITH YOU", (GRN, (110, 230, 140))),
    (1, "Instant feedback", "INSTANT\nFEEDBACK", (RED, (255, 90, 90))),
    (1, "Endless practice", "ENDLESS\nPRACTICE", (CYAN, (120, 235, 245))),
    (1, "Infinite patience", "INFINITE\nPATIENCE", (PINK, (255, 150, 200))),
    (2, "translate", "TRANSLATES\nTHE LESSON", (PURP, (160, 90, 240))),
    (2, "coach your", "PRONUNCIATION\nCOACH", (ORNG, (255, 170, 60))),
    (2, "role-play", "ROLE-PLAYS\nCONVERSATIONS", (GRN, (110, 230, 140))),
    (2, "bring back", "REVIEWS RIGHT\nBEFORE YOU FORGET", (RED, (255, 90, 90))),
]
_card_t = None


def card_times():
    global _card_t
    if _card_t is None:
        _card_t = []
        for line in range(3):
            parts = [c for c in CARDS if c[0] == line]
            _card_t += TL.phrases("powers", line, [p[1] for p in parts])
    return _card_t


def s_powers(t):
    new_frame(t)
    ts = card_times()
    idx = max([i for i, a in enumerate(ts) if t >= a] or [-1])
    for a in ts:
        cue("whoosh", a)
    if idx < 0:
        tunnel(t, INK, (40, 40, 60))
        scrawl(t, 0.1, (W / 2, 600), "THE AI\nTUTOR", 170, CYAN)
        spark(W / 2, 1050, 120 * pop(t, 0.2), t)
    else:
        _, _, label, (c1, c2) = CARDS[idx]
        tunnel(t, c1, c2, speed=900)
        scrawl(t, ts[idx], (W / 2, 240), f"{idx + 1:02d}/10", 54, INK, stroke=0)
        scrawl(t, ts[idx], (W / 2, 560), label, 110, WHITE)
        if idx == 9:   # spaced repetition: the forgetting curve, reset by reviews
            x0, y0, w, h = 140, 1250, 800, 380
            G.draw.rectangle([x0 - 30, y0 - h - 40, x0 + w + 30, y0 + 50], fill=PAPER)
            pts, m, last = [], 1.0, 0
            for i in range(0, w + 1, 8):
                if i in (200, 400, 600):
                    last = i
                s = 60 + (i // 200) * 90
                pts.append((x0 + i, y0 - h * math.exp(-(i - last) / s)))
            k = ease_out_cubic((t - ts[idx]) / 1.0)
            sketch(pts[:max(2, int(len(pts) * k))], RED, 7, 2, 11)
            for i in (200, 400, 600):
                if k * w > i:
                    spark(x0 + i, y0 - h - 10, 26, t, i)
            G.draw.text((x0 + w / 2, y0 + 28), "memory over time  ·  ★ = review", font=font(FONT, 32), fill=INK,
                        anchor="mm")
        else:
            spark(W / 2, 1080, 150, t, idx, col=WHITE if c1 == CYAN else CYAN)
    subtitle(t, "powers")


def bubble(y, s, student, t, at):
    k = ease_out_back((t - at) / 0.25)
    if k <= 0.05:
        return
    txt = "\n".join(textwrap.wrap(s, 24))
    f = font(FONT, 40)
    bb = G.draw.multiline_textbbox((0, 0), txt, font=f, spacing=6)
    w, h = bb[2] - bb[0] + 60, bb[3] - bb[1] + 44
    x = W - 70 - w if student else 70
    col = YEL if student else CYAN
    cx = x + w / 2
    r = [cx - w / 2 * k, y - h / 2, cx + w / 2 * k, y + h / 2]
    if r[2] - r[0] < 40:
        return
    G.draw.rounded_rectangle(r, 30, fill=col)
    pts = [(r[0], r[1] + 30), (r[0] + 30, r[1]), (r[2] - 30, r[1]), (r[2], r[1] + 30), (r[2], r[3] - 30),
           (r[2] - 30, r[3]), (r[0] + 30, r[3]), (r[0], r[3] - 30)]
    sketch(pts, INK, 6, 2, int(y), closed=True)
    if k > 0.9:
        G.draw.multiline_text((cx, y), txt, font=f, fill=INK, anchor="mm", align="center", spacing=6)
    tag = "STUDENT" if student else "AI TUTOR"
    G.draw.text((r[2] - 10 if student else r[0] + 10, r[1] - 22), tag, font=font(FONT, 26), fill=INK,
                anchor="rm" if student else "lm")


def s_calc(t):
    new_frame(t)
    hatch_bg(PAPER, 3, ink=(215, 205, 185))
    scrawl(t, 0.1, (W / 2, 150), "CALCULUS SOS", 70, RED)
    shown = [i for i in range(1, 7) if t >= ls("calc", i)][-3:]
    for j, i in enumerate(shown):
        s = TL.lines["calc"][i][2]
        bubble(300 + j * 170, s, TL.lines["calc"][i][3] == S, t, ls("calc", i))
    top = 820
    if ls("calc", 1) <= t < ls("calc", 3):          # the car + speedometer
        tt = t - ls("calc", 1)
        pos = (tt * tt * 55) % 900
        sp = min(1, tt * 0.3)
        sketch([(60, 1170), (1020, 1170)], INK, 8, 2, 21)
        x = 90 + pos
        blob(x, 1110, 95, 40, RED, 22, amp=0.03)
        blob(x + 10, 1070, 50, 32, CYAN, 23, amp=0.03)
        for dx in (-55, 55):
            blob(x + dx, 1160, 26, 26, INK, 24 + dx, amp=0.04)
        for k in range(4):
            sketch([(x - 110 - k * 40, 1090 + k * 20), (x - 160 - k * 60, 1090 + k * 20)], INK, 4, 3, 30 + k)
        cx, cy, r = 820, 960, 120
        G.draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE)
        sketch([(cx + r * math.cos(a / 10 * math.pi), cy - r * abs(math.sin(a / 10 * math.pi))) for a in range(11)], INK, 6)
        a = math.pi * (1 - sp)
        sketch([(cx, cy), (cx + r * 0.85 * math.cos(a), cy - r * 0.85 * math.sin(a))], RED, 9, 2, 25)
        G.draw.text((cx, cy + 40), "speed = d(position)/dt", font=font(FONT, 26), fill=INK, anchor="mm")
    elif ls("calc", 3) <= t < ls("calc", 5):        # slope of the curve
        pts = [(140 + i * 8, 1300 - 0.0012 * (i * 8) ** 2) for i in range(101)]
        sketch(pts, INK, 8, 2, 40)
        u = 0.2 + 0.6 * (0.5 + 0.5 * math.sin((t - ls("calc", 3)) * 1.6))
        px = u * 800
        x, y = 140 + px, 1300 - 0.0012 * px ** 2
        m = -0.0024 * px
        sketch([(x - 230, y - 230 * m), (x + 230, y + 230 * m)], RED, 8, 2, 41)
        blob(x, y, 18, 18, YEL, 42)
        G.draw.text((W / 2, top + 20), f"slope here = {abs(m) * 100:.0f}", font=font(FONT, 44), fill=RED, anchor="mm")
    elif ls("calc", 5) <= t < ls("calc", 6):        # five problems
        for i in range(5):
            at = ls("calc", 5) + 0.15 + i * 0.18
            if t >= at:
                k = pop(t, at, 0.2)
                x, y = 190 + (i % 3) * 350, 950 + (i // 3) * 250
                G.draw.rectangle([x - 150 * k, y - 95 * k, x + 150 * k, y + 95 * k], fill=WHITE)
                sketch([(x - 150 * k, y - 95 * k), (x + 150 * k, y - 95 * k), (x + 150 * k, y + 95 * k),
                        (x - 150 * k, y + 95 * k)], INK, 5, 2, 50 + i, closed=True)
                G.draw.text((x, y), f"#{i + 1}  d/dx", font=font(FONT, 46 * k), fill=INK, anchor="mm")
    elif t >= ls("calc", 6):                        # red pen
        x0, y0 = 150, 880
        G.draw.rectangle([x0 - 30, y0 - 50, W - x0 + 30, y0 + 510], fill=WHITE)
        work = ["y = (3x + 1)²", "let u = 3x + 1", "y' = 2u = 6x + 2  ✗", "forgot × u' = 3  →  18x + 6"]
        for i, s in enumerate(work[:3]):
            G.draw.text((x0 + 20, y0 + 30 + i * 110), s, font=font(FONT, 54), fill=INK, anchor="lm")
        at = ls("calc", 6) + 0.3
        if t >= at:
            k = ease_out_cubic((t - at) / 0.4)
            n = int(24 * k)
            ring = [(W / 2 + 330 * math.cos(2 * math.pi * i / 24 + 0.3), y0 + 250 + 70 * math.sin(2 * math.pi * i / 24 + 0.3))
                    for i in range(n + 1)]
            if len(ring) > 1:
                sketch(ring, RED, 9, 4, 60)
            scrawl(t, at + 0.4, (W / 2, y0 + 370), "CHAIN RULE!", 78, RED)
            G.draw.text((W / 2, y0 + 465), work[3], font=font(FONT, 36), fill=RED, anchor="mm")
    subtitle(t, "calc")


WHO = [("learning differences", "LEARNING\nDIFFERENCES"), ("language barriers", "LANGUAGE\nBARRIERS"),
       ("no good teacher", "NO TEACHER\nNEARBY"), ("unusual schedules", "ODD\nSCHEDULES"),
       ("gaps in", "GAPS IN\nSCHOOLING"), ("interests way", "WAY-AHEAD\nINTERESTS")]


def s_who(t):
    new_frame(t)
    tunnel(t, PURP, ORNG, speed=400)
    scrawl(t, 0.1, (W / 2, 210), "WHO GAINS MOST", 90, YEL)
    ts = TL.phrases("who", 0, [p for p, _ in WHO])
    for i, ((_, lab), at) in enumerate(zip(WHO, ts)):
        cue("pop", at)
        if t < at:
            continue
        x, y = (290, 790)[i % 2], 470 + (i // 2) * 330
        head(x, y, 85 * pop(t, at, 0.25), 40 + i, t, mood="ok")
        spark(x + 95, y - 80, 36 * pop(t, at + 0.15, 0.2), t, i)
        scrawl(t, at, (x, y + 160), lab, 44, WHITE)
    subtitle(t, "who")


def s_teach(t):
    new_frame(t)
    hatch_bg(GRN, 5)
    scrawl(t, 0.1, (W / 2, 200), "TEACHERS TOO", 100, WHITE, until=ls("teach", 1))
    cx, cy = W / 2, 820
    blob(cx, cy + 210, 120, 150, (60, 70, 160), 70)
    head(cx, cy, 110, 71, t, mood="ok" if t < ls("teach", 1) else "o")
    items = [("Lesson plans", "LESSON\nPLANS"), ("practice sets", "PRACTICE\nSETS"), ("quick grading", "QUICK\nGRADING"),
             ("early warning", "EARLY\nWARNINGS")]
    ts = TL.phrases("teach", 0, [p for p, _ in items])
    for i, ((_, lab), at) in enumerate(zip(items, ts)):
        cue("pop", at)
        if t < at:
            continue
        a = -math.pi / 2 + i * math.pi / 2 + math.pi / 4 + t * 0.4
        x, y = cx + 360 * math.cos(a), cy + 330 * math.sin(a)
        k = pop(t, at, 0.25)
        G.draw.rectangle([x - 150 * k, y - 70 * k, x + 150 * k, y + 70 * k], fill=PAPER)
        sketch([(x - 150 * k, y - 70 * k), (x + 150 * k, y - 70 * k), (x + 150 * k, y + 70 * k), (x - 150 * k, y + 70 * k)],
               INK, 5, 2, 80 + i, closed=True)
        G.draw.multiline_text((x, y), lab, font=font(FONT, 36 * k), fill=INK, anchor="mm", align="center")
    if t >= ls("teach", 1):
        scrawl(t, ls("teach", 1) + 0.6, (W / 2, 260), "MORE TIME FOR\nTHE HUMAN PART", 88, WHITE)
        k = pop(t, ls("teach", 1) + 0.8)
        hx, hy, s = cx + 170, cy - 170, 60 * k * (1 + 0.1 * math.sin(t * 10))
        if s > 4:
            heart = [(hx + s * 16 * math.sin(u) ** 3 / 16, hy - s * (13 * math.cos(u) - 5 * math.cos(2 * u) - 2 * math.cos(3 * u)
                                                                      - math.cos(4 * u)) / 16) for u in np.linspace(0, 2 * math.pi, 30)]
            G.draw.polygon(heart, fill=RED)
            sketch(heart, INK, 5, 2, 90, closed=True)
    subtitle(t, "teach")


def s_warn(t):
    new_frame(t)
    hatch_bg(RED, 6, ink=(150, 20, 25), n=90)
    tri = [(W / 2, 110), (W / 2 + 90, 270), (W / 2 - 90, 270)]
    G.draw.polygon(tri, fill=YEL)
    sketch(tri, INK, 8, 3, 100, closed=True)
    scrawl(t, 0.0, (W / 2, 215), "!", 90, INK, stroke=0)
    scrawl(t, 0.1, (W / 2, 370), "3 WARNINGS", 110, WHITE)
    rows = [("ANSWERS ≠ LEARNING", "ask it to quiz you instead"), ("IT CAN BE WRONG", "check it"),
            ("ACCESS ISN'T EQUAL", "devices · internet · time")]
    for i, (hd, sub) in enumerate(rows):
        at = ls("warn", i + 1)
        cue("boom", at)
        if t < at:
            continue
        y = 640 + i * 260
        k = ease_out_cubic((t - at) / 0.2)
        G.draw.polygon([(W / 2 - 480 * k, y - 95), (W / 2 + 480 * k, y - 110), (W / 2 + 470 * k, y + 95),
                        (W / 2 - 470 * k, y + 105)], fill=INK)
        scrawl(t, at, (W / 2, y - 25), hd, 66, YEL)
        scrawl(t, at + 0.2, (W / 2, y + 55), sub, 40, WHITE, stroke=0)
    subtitle(t, "warn")


MONTAGE = ["hook", "bloom", "powers", "calc", "who", "teach", "warn"]


def s_outro(t):
    if t < le("outro", 0):     # life flashes before your eyes
        k = int(t * 9)
        key = MONTAGE[k % len(MONTAGE)]
        saved, E.CUES = E.CUES, set()
        Ctx.montage = True
        try:
            SCENE_FNS[key]((k * 1.37 + 0.8) % (TL.dur[key] - 0.5) + 0.5)
        finally:
            Ctx.montage, E.CUES = False, saved
        Ctx.b = int(t * 12)
        if k % 3 == 0:
            G.img = ImageOps.invert(G.img)
        elif k % 3 == 1:
            G.img = ImageOps.posterize(ImageOps.grayscale(G.img), 2).convert("RGB")
        G.draw = ImageDraw.Draw(G.img)
        scrawl(t, 0.2, (W / 2, 700), "A PERSONAL TUTOR\nFOR EVERYONE", 100, YEL)
    else:
        new_frame(t)
        tunnel(t, YEL, ORNG, speed=300)
        at = le("outro", 0)
        for i in range(18):
            ang = i * 2 * math.pi / 18 + t * 0.3
            r = 390 + 30 * math.sin(t * 3 + i)
            head(W / 2 + r * math.cos(ang), 740 + r * math.sin(ang), 44, 90 + i, t)
        spark(W / 2, 740, 140 * pop(t, at), t)
        scrawl(t, at + 0.1, (W / 2, 250), "HOW WILL\nYOU USE IT?", 100, WHITE)
        scrawl(t, le("outro", 1) - 1.4, (W / 2, 1320), "think HARDER,\nnot less.", 96, RED)
    subtitle(t, "outro")


SCENE_FNS = {"hook": s_hook, "bloom": s_bloom, "powers": s_powers, "calc": s_calc, "who": s_who,
             "teach": s_teach, "warn": s_warn, "outro": s_outro}
SCENES = [(TL.dur[k], SCENE_FNS[k]) for k, *_ in SCRIPT]
TOTAL = TL.total


def post(arr, fi, t, idx, tl):
    if idx > 0 and tl < 0.07:          # whiplash cut: two inverted frames
        return 255 - arr
    return arr


# ---------------------------------------------------------------- score: jazzy samba chaos, ducked under the voice

SR = E.SR


def _tt(d):
    return np.arange(int(d * SR)) / SR


def extra_sfx(sr):
    rng = np.random.default_rng(3)
    x = _tt(0.12)
    swish = rng.standard_normal(len(x)) * np.sin(np.pi * x / 0.12) ** 2
    swish = np.diff(swish, prepend=0)
    return {"pop": (swish, 0.25)}


def music_fn(n):
    rng = np.random.default_rng(2004)
    out = np.zeros(n)

    def add(sig, t, g):
        i = int(t * SR)
        if i < n:
            j = min(n, i + len(sig))
            out[i:j] += sig[: j - i] * g

    def keys(f, d=0.5):
        x = _tt(d)
        return ((np.sin(2 * np.pi * f * x) + 0.4 * np.sin(4 * np.pi * f * x) + 0.2 * np.sin(6 * np.pi * f * x))
                * np.exp(-x * 5) * np.minimum(1, x / 0.003))

    x = _tt(0.4)
    surdo = np.sin(2 * np.pi * np.cumsum(60 + 30 * np.exp(-x * 20)) / SR) * np.exp(-x * 6)
    x = _tt(0.03)
    clave = np.sin(2 * np.pi * 2100 * x) * np.exp(-x * 120)
    x = _tt(0.05)
    shaker = np.diff(rng.standard_normal(len(x) + 1)) * np.exp(-x * 60)
    beat = 60 / 118
    prog = [(110.0, [220.0, 261.63, 329.63, 392.0, 493.88]), (73.42, [185.0, 220.0, 261.63, 329.63]),
            (98.0, [246.94, 293.66, 369.99, 440.0]), (130.81, [261.63, 329.63, 392.0, 493.88])]
    clave_pat = [0, 0.75, 1.5, 2.5, 3.0]
    stabs = [0, 0.75, 1.5, 2.5, 3.25]
    t, bar = 0.0, 0
    total = E.TOTAL
    while t < total:
        root, ch = prog[bar % 4]
        for b in range(4):
            add(surdo, t + b * beat, 0.7 if b % 2 else 0.35)
            for q in range(4):
                add(shaker, t + (b + q / 4) * beat, 0.12 if q else 0.2)
        for c in clave_pat:
            add(clave, t + c * beat, 0.18)
        for s_ in stabs:
            for f in ch:
                add(keys(f), t + s_ * beat, 0.035)
        for b, step in enumerate((1, 1.5, 2, 1.335)):
            xb = _tt(beat * 0.95)
            f = root * step
            add((np.sin(2 * np.pi * f * xb) + 0.3 * np.sin(4 * np.pi * f * xb)) * np.exp(-xb * 2.5), t + b * beat, 0.32)
        t += 4 * beat
        bar += 1
    voice = TL.track(n, SR)
    out = narrate.duck(out, voice, SR)
    fade = int(1.5 * SR)
    end = int(total * SR)
    out[end - fade:end] *= np.linspace(1, 0, fade)
    out[end:] = 0
    return out * 0.6 + voice * 1.7


E.SCENE_CUT_FLASH = False
E.POST_FX = post

if __name__ == "__main__":
    print(f"total {TOTAL:.1f}s; " + ", ".join(f"{k} {TL.dur[k]:.1f}" for k, *_ in SCRIPT))
    E.main("every_student_a_tutor.mp4", SCENES, music_fn, extra_sfx)

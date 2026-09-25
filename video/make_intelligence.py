#!/usr/bin/env python3
"""Render "WHAT IS INTELLIGENCE? — IN FOUR CHAPTERS": a <2 min vertical short styled after
Mishima: A Life in Four Chapters (1985): Eiko Ishioka-style theatrical sets in single bold
colours with sliding stage flats, a golden pavilion, gritty black-and-white "documentary"
interludes, numbered chapter cards, kanji, and a Glass-style minimalist string ostinato.
Female narration (Kokoro af_bella).

    python3 make_intelligence.py                  # -> out/what_is_intelligence.mp4
    python3 make_intelligence.py --preview 3 17   # frames -> out/preview/what_is_intelligence/
"""
import math
import textwrap

import numpy as np
from PIL import Image, ImageDraw

import make_video as E
import narrate
from make_video import G, H, W, cue, ease_in_out, ease_out_cubic, font, pop

SERIF = "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"
SERIF_R = "/usr/share/fonts/truetype/freefont/FreeSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
JP = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
BLACK = (0, 0, 0)
WHITE = (245, 242, 235)
GOLD = (230, 180, 50)
GOLD_D = (120, 80, 10)
RED = (200, 20, 30)
PINK = (240, 120, 160)
GREEN = (40, 150, 110)
SILVER = (200, 205, 215)
PAPER = (240, 232, 214)
INK = (15, 12, 12)

SCRIPT = [
    ("hook", 0.5, ["What is intelligence?",
                   "No one fully agrees. Not even for humans.",
                   "But here's a working definition, in four chapters."], 0.3),
    ("ch1", 1.3, ["Intelligence is the capacity to build a model of the world, learn from experience, "
                  "infer what was never said, adapt to the unfamiliar, plan, and use knowledge to reach goals.",
                  "Notice what's missing from that list: simply memorizing facts."], 0.5),
    ("ch2", 1.3, ["Now imagine a hard drive holding everything. Every encyclopedia, paper, novel, photo, song, "
                  "and line of code ever written.",
                  "Ask it: you have three planks, a rope, and a broken pulley. Lift this rock.",
                  "Nothing happens.",
                  "The knowledge is all there. But nothing turns it into inference, or action."], 0.4),
    ("ch3", 1.3, ["A child knows almost nothing by comparison.",
                  "But she can face a problem she's never seen, and find a way. A plank becomes a lever.",
                  "Even a crow can bend a wire into a hook to reach food. Nobody taught it that.",
                  "A child learns what a giraffe is from one picture. Early AI systems needed thousands.",
                  "That's generalization: handling the new. It's one of the deepest parts of intelligence.",
                  "AI researcher François Chollet puts it simply: intelligence isn't how much you know. "
                  "It's how efficiently you learn what you don't."], 0.4),
    ("ch4", 1.3, ["So where does AI stand? Today's models hold more knowledge than any library, "
                  "and can reason through many new problems.",
                  "But how far they truly generalize is one of the biggest open questions in the field.",
                  "Chollet's ARC puzzles are simple for most people, yet they stumped AI systems for years.",
                  "Knowledge is the ink. Intelligence is the hand that writes."], 2.6),
]
TL = narrate.Timeline(SCRIPT, sid=1, speed=1.08)
ls, le = TL.start, TL.end
CHAPTER = {"ch1": ("一", "1", "A DEFINITION"), "ch2": ("二", "2", "THE ARCHIVE"), "ch3": ("三", "3", "THE CHILD"),
           "ch4": ("四", "4", "HARMONY OF KNOWING AND DOING")}
TOP, BOT = 120, 1410   # letterbox: the "screen" lives between these lines


class Ctx:
    bw = False


# ---------------------------------------------------------------- stagecraft


def blank(col=BLACK):
    G.img = Image.new("RGB", (W, H), col)
    G.draw = ImageDraw.Draw(G.img)


def letterbox():
    G.draw.rectangle([0, 0, W, TOP], fill=BLACK)
    G.draw.rectangle([0, BOT, W, H], fill=BLACK)


def dim(c, a):
    return tuple(int(v * a) for v in c)


def fade(t, at, until=None, d=0.3):
    a = ease_in_out((t - at) / d)
    if until is not None:
        a = min(a, ease_in_out((until - t) / d))
    return max(0.0, min(1.0, a))


def stage(wall, floor, t, open_at=0.0, flats=None):
    """A proscenium set: flat wall, raked floor, and two flats that slide apart to reveal it."""
    d = G.draw
    d.rectangle([0, TOP, W, BOT], fill=wall)
    fy = 1050
    d.polygon([(0, BOT), (W, BOT), (W - 140, fy), (140, fy)], fill=floor)
    for i in range(1, 8):
        y = fy + (BOT - fy) * (i / 8) ** 1.4
        d.line([(140 * (1 - (y - fy) / (BOT - fy)), y), (W - 140 * (1 - (y - fy) / (BOT - fy)), y)],
               fill=dim(floor, 0.8), width=2)
    if flats:
        k = ease_in_out((t - open_at) / 0.7)
        cue("pop", open_at)
        for sg in (-1, 1):
            x_in = W / 2 + sg * (W / 2) * k
            x_out = W / 2 + sg * (W / 2 + 60) if k < 1 else x_in
            if k < 1:
                x0, x1 = sorted((x_in, W / 2 + sg * (W / 2 + 600)))
                d.rectangle([x0, TOP, x1, BOT], fill=flats)
                d.line([(x_in, TOP), (x_in, BOT)], fill=BLACK, width=6)


def spot(cx, cy_top, w_bottom, col=(255, 250, 230), a=0.25):
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([(cx - 40, cy_top), (cx + 40, cy_top), (cx + w_bottom, BOT), (cx - w_bottom, BOT)],
                              fill=int(255 * a))
    G.img.paste(col, (0, 0), m)


def kanji(xy, s, size, col, a=1.0):
    G.draw.text(xy, s, font=font(JP, size), fill=dim(col, a), anchor="mm")


def serif(t, at, xy, s, size, col=WHITE, until=None, fnt=SERIF, track=0.0):
    a = fade(t, at, until)
    if a <= 0:
        return
    f = font(fnt, size)
    if track:
        w = sum(f.getlength(ch) for ch in s) + size * track * (len(s) - 1)
        x = xy[0] - w / 2
        for ch in s:
            G.draw.text((x, xy[1]), ch, font=f, fill=dim(col, a), anchor="lm")
            x += f.getlength(ch) + size * track
    else:
        G.draw.multiline_text(xy, s, font=f, fill=dim(col, a), anchor="mm", align="center", spacing=int(size * 0.2))


def chapter_card(t, key):
    if key not in CHAPTER or t >= 1.2:
        return False
    blank()
    kj, num, name = CHAPTER[key]
    a = fade(t, 0.0, 1.2, 0.25)
    kanji((W / 2, 760), kj, 520, (90, 0, 8), a)
    serif(t, 0.0, (W / 2, 700), num, 120, dim(WHITE, a), until=1.2)
    serif(t, 0.05, (W / 2, 830), name, 46, dim(WHITE, a), until=1.2, track=0.28)
    cue("pop", 0.0)
    return True


def subtitle(t, key):
    a = TL.active(key, t)
    if not a:
        return
    txt = "\n".join(textwrap.wrap(a[0], 34))
    G.draw.multiline_text((W / 2, 1560), txt, font=font(SERIF_R, 48), fill=WHITE, anchor="mm", align="center", spacing=10)


# ---------------------------------------------------------------- props


def pavilion(cx, base, s, col=GOLD, t=0.0, windows=True):
    """A three-tier golden pavilion with its reflection in still water."""
    d = G.draw
    tiers = [(300, 150), (240, 130), (170, 120)]
    y = base
    rects = []
    for w, h in tiers:
        w, h = w * s, h * s
        d.rectangle([cx - w / 2, y - h, cx + w / 2, y], fill=col, outline=GOLD_D, width=4)
        rects.append((cx - w / 2, y - h, cx + w / 2, y))
        d.polygon([(cx - w / 2 - 60 * s, y - h), (cx + w / 2 + 60 * s, y - h), (cx + w / 2 - 10 * s, y - h - 40 * s),
                   (cx - w / 2 + 10 * s, y - h - 40 * s)], fill=dim(col, 0.55))
        y -= h + 40 * s
    d.polygon([(cx - 40 * s, y), (cx + 40 * s, y), (cx, y - 70 * s)], fill=col)
    if windows:
        f = font(SANS, int(16 * s))
        for (x0, y0, x1, y1) in rects:
            for r in range(int((y1 - y0) / (22 * s)) - 1):
                off = int(t * 40 + r * 7) % 26
                row = "".join(chr(0x30 + ((r * 7 + i + off) % 42)) for i in range(int((x1 - x0) / (11 * s))))
                d.text((x0 + 8 * s, y0 + 14 * s + r * 22 * s), row, font=f, fill=GOLD_D)


def reflection(y0):
    """Mirror the region above y0 into the 'water' below it, darkened and rippled."""
    h = BOT - y0
    src = G.img.crop((0, int(y0 - h), W, int(y0))).transpose(Image.FLIP_TOP_BOTTOM)
    arr = (np.asarray(src).astype(np.float32) * 0.35).astype(np.uint8)
    rows = np.arange(arr.shape[0])
    shift = (np.sin(rows / 6.0) * 6).astype(int)
    for r in range(0, arr.shape[0], 3):
        arr[r:r + 3] = np.roll(arr[r:r + 3], shift[r], axis=1)
    G.img.paste(Image.fromarray(arr), (0, int(y0)))


def rock(cx, cy, s, col=(150, 150, 150)):
    pts = [(cx + s * math.cos(a) * (1 + 0.18 * math.sin(3 * a + 1)), cy + s * 0.7 * math.sin(a) * (1 + 0.12 * math.cos(5 * a)))
           for a in np.linspace(0, 2 * math.pi, 24)]
    G.draw.polygon(pts, fill=col, outline=INK, width=5)


def plank(x0, y0, x1, y1, w=26, col=(185, 185, 185)):
    ang = math.atan2(y1 - y0, x1 - x0)
    px, py = -math.sin(ang) * w / 2, math.cos(ang) * w / 2
    G.draw.polygon([(x0 + px, y0 + py), (x1 + px, y1 + py), (x1 - px, y1 - py), (x0 - px, y0 - py)], fill=col,
                   outline=INK, width=4)


def child(x, y, s, arm_dy=0.0, col=(30, 30, 30)):
    d = G.draw
    d.ellipse([x - 32 * s, y - 180 * s, x + 32 * s, y - 116 * s], fill=col)
    d.polygon([(x - 40 * s, y - 110 * s), (x + 40 * s, y - 110 * s), (x + 55 * s, y - 20 * s), (x - 55 * s, y - 20 * s)],
              fill=col)
    d.line([(x - 20 * s, y - 20 * s), (x - 26 * s, y + 30 * s)], fill=col, width=int(18 * s))
    d.line([(x + 20 * s, y - 20 * s), (x + 26 * s, y + 30 * s)], fill=col, width=int(18 * s))
    d.line([(x + 30 * s, y - 95 * s), (x + 110 * s, y - 60 * s + arm_dy)], fill=col, width=int(16 * s))


def enso(cx, cy, r, k, t):
    """Zen brush circle painted progressively (k: 0..1)."""
    d = G.draw
    n = int(220 * k)
    for i in range(n):
        u = i / 220
        a = -math.pi * 0.6 + u * 2 * math.pi * 0.93
        w = r * (0.13 * (1 - 0.7 * u) + 0.02 * math.sin(u * 40))
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        d.ellipse([x - w, y - w, x + w, y + w], fill=INK)
        if u > 0.6 and i % 3 == 0:   # dry-brush streaks near the tail
            for k2 in range(3):
                off = (k2 - 1) * w * 0.8
                d.ellipse([x + off * math.cos(a) - 2, y + off * math.sin(a) - 2, x + off * math.cos(a) + 2,
                           y + off * math.sin(a) + 2], fill=PAPER)


# ---------------------------------------------------------------- scenes


def s_hook(t):
    Ctx.bw = False
    blank()
    spot(W / 2, TOP, 420, a=0.22 + 0.04 * math.sin(t * 3))
    ka = 0.22 if ls("hook", 1) <= t < ls("hook", 2) + 0.2 else 1.0
    kanji((W / 2, 760), "知", 560, (255, 250, 235), fade(t, 0.1) * ka)
    serif(t, 0.3, (W / 2, 280), "WHAT IS", 64, WHITE, track=0.3)
    serif(t, 0.5, (W / 2, 380), "INTELLIGENCE?", 84, WHITE, track=0.12)
    at = ls("hook", 1)
    if at <= t < ls("hook", 2):
        for i, w in enumerate(["IQ?", "LOGIC?", "MEMORY?", "CREATIVITY?", "ADAPTING?", "WISDOM?"]):
            a = fade(t, at + i * 0.25)
            x, y = (230, 850)[i % 2], 560 + i * 110
            serif(t, at + i * 0.25, (x, y), w, 44, dim(RED, a) if i % 2 else dim(WHITE, a))
    at = ls("hook", 2)
    if t >= at:
        for i, c in enumerate((GOLD, PINK, RED, SILVER)):
            if t >= at + 0.3 + i * 0.2:
                x0 = 60 + i * 245
                G.draw.rectangle([x0, 980, x0 + 225, 1300], fill=c)
                kanji((x0 + 112, 1140), "一二三四"[i], 150, BLACK)
    letterbox()
    subtitle(t, "hook")


FACULTIES = [("見", "MODEL THE WORLD", "a model of the world"), ("学", "LEARN", "learn from"),
             ("推", "INFER", "infer what"), ("変", "ADAPT", "adapt to"), ("計", "PLAN", "plan,"),
             ("行", "ACT ON GOALS", "use knowledge")]


def s_ch1(t):
    Ctx.bw = False
    if chapter_card(t, "ch1"):
        return
    blank()
    stage(PINK, GREEN, t, 1.2, flats=(20, 90, 60))
    ts = TL.phrases("ch1", 0, [p for *_, p in FACULTIES])
    for i, ((kj, lab, _), at) in enumerate(zip(FACULTIES, ts)):
        cue("pop", at)
        if t < at:
            continue
        k = ease_out_cubic((t - at) / 0.35)
        c, r = i % 3, i // 3
        x, y = 60 + c * 330, 200 + r * 440
        slide = (1 - k) * (-400 if c == 0 else 400 if c == 2 else 0)
        yy = y + ((1 - k) * 300 if c == 1 else 0)
        G.draw.rectangle([x + slide, yy, x + slide + 300, yy + 400], fill=WHITE if i % 2 == 0 else BLACK,
                         outline=BLACK, width=6)
        col = RED if i % 2 == 0 else GOLD
        kanji((x + slide + 150, yy + 170), kj, 230, col)
        G.draw.text((x + slide + 150, yy + 350), lab, font=font(SERIF, 32 if len(lab) < 12 else 26),
                    fill=BLACK if i % 2 == 0 else WHITE, anchor="mm")
    a1 = ls("ch1", 1)
    if t >= a1:
        G.draw.rectangle([0, TOP, W, BOT], fill=BLACK)
        kanji((W / 2, 640), "暗記", 260, (110, 110, 110), fade(t, a1))
        serif(t, a1 + 0.2, (W / 2, 880), "MEMORIZING FACTS", 52, (150, 150, 150), track=0.15)
        k = ease_out_cubic((t - a1 - 1.2) / 0.3)
        if k > 0:
            G.draw.line([(160, 760), (160 + 760 * k, 700)], fill=RED, width=26)
        serif(t, a1 + 1.5, (W / 2, 1060), "not on the list", 44, RED, fnt=SERIF_R)
    letterbox()
    subtitle(t, "ch1")


ARCHIVE = ["ENCYCLOPEDIAS", "PAPERS", "NOVELS", "PHOTOGRAPHS", "MUSIC", "CODE"]


def s_ch2(t):
    if chapter_card(t, "ch2"):
        Ctx.bw = False
        return
    blank()
    a1, a2, a3 = ls("ch2", 1), ls("ch2", 2), ls("ch2", 3)
    if t < a1:                                          # the golden archive
        Ctx.bw = False
        G.draw.rectangle([0, TOP, W, BOT], fill=(10, 6, 0))
        pavilion(W / 2, 1000, 1.25, GOLD, t)
        reflection(1000)
        kanji((W / 2, 250), "知識", 150, GOLD, fade(t, 1.3))
        ts = TL.phrases("ch2", 0, ["encyclopedia", "paper", "novel", "photo", "song", "line of code"])
        for i, (w, at) in enumerate(zip(ARCHIVE, ts)):
            if t < at:
                continue
            k = ease_in_out((t - at) / 1.2)
            x = (120 if i % 2 == 0 else W - 120) + ((W / 2) - (120 if i % 2 == 0 else W - 120)) * k
            y = 380 + (i % 3) * 60 + (700 - 380) * k
            if k < 0.98:
                serif(t, at, (x, y), w, 36, GOLD, track=0.15)
    elif t < a3:                                        # the question, in black and white
        Ctx.bw = True
        G.draw.rectangle([0, TOP, W, BOT], fill=(70, 70, 70))
        G.draw.rectangle([0, 1080, W, BOT], fill=(40, 40, 40))
        rock(W / 2 + 200, 1000, 150)
        for i in range(3):
            plank(90, 1180 + i * 40, 520, 1150 + i * 40)
        G.draw.arc([120, 900, 300, 1040], 0, 360, fill=(210, 210, 210), width=14)
        G.draw.arc([150, 925, 270, 1015], 0, 360, fill=(210, 210, 210), width=10)
        G.draw.ellipse([640, 560, 780, 700], outline=(220, 220, 220), width=14)
        G.draw.line([(690, 560), (730, 630), (700, 700)], fill=(70, 70, 70), width=12)
        G.draw.rectangle([90, 180, W - 90, 470], fill=BLACK)
        q = "3 planks. 1 rope. 1 broken pulley.\nLift this rock."
        n = int(len(q) * min(1, (t - a1) / 2.0))
        G.draw.multiline_text((W / 2, 325), q[:n], font=font(SERIF, 50), fill=WHITE, anchor="mm", align="center",
                              spacing=16)
        if t >= a2:
            G.draw.rectangle([0, TOP, W, BOT], fill=(12, 12, 12))
            if int(t * 2.5) % 2 == 0:
                G.draw.rectangle([W / 2 - 18, 700, W / 2 + 18, 780], fill=WHITE)
            serif(t, a2 + 0.2, (W / 2, 950), "NOTHING HAPPENS.", 56, WHITE, track=0.2)
    else:                                               # knowledge is not intelligence
        Ctx.bw = False
        G.draw.rectangle([0, TOP, W / 2, BOT], fill=GOLD)
        G.draw.rectangle([W / 2, TOP, W, BOT], fill=RED)
        stage_k = ease_in_out((t - a3) / 0.6)
        kanji((W / 4, 620), "知識", 200, BLACK, stage_k)
        kanji((3 * W / 4, 620), "知能", 200, WHITE, stage_k)
        serif(t, a3 + 0.3, (W / 4, 820), "KNOWLEDGE", 46, BLACK, track=0.15)
        serif(t, a3 + 0.3, (3 * W / 4, 820), "INTELLIGENCE", 46, WHITE, track=0.1)
        G.draw.ellipse([W / 2 - 90, 530, W / 2 + 90, 710], fill=BLACK)
        G.draw.text((W / 2, 620), "≠", font=font(SANS, 130), fill=WHITE, anchor="mm")
        pts = TL.phrases("ch2", 3, ["inference", "action"])
        serif(t, pts[0], (W / 4, 1120), "information", 40, BLACK, fnt=SERIF_R)
        serif(t, pts[0], (3 * W / 4, 1080), "→ inference", 44, WHITE)
        serif(t, pts[1], (3 * W / 4, 1160), "→ action", 44, WHITE)
    letterbox()
    subtitle(t, "ch2")


def s_ch3(t):
    if chapter_card(t, "ch3"):
        Ctx.bw = False
        return
    blank()
    a1, ac, ag, a2, a3 = ls("ch3", 1), ls("ch3", 2), ls("ch3", 3), ls("ch3", 4), ls("ch3", 5)
    if ac <= t < ag:
        Ctx.bw = True
        crow_scene(t, ac)
    elif ag <= t < a2:
        Ctx.bw = False
        giraffe_scene(t, ag)
    elif t < ac:                                        # documentary: the child and the lever
        Ctx.bw = True
        G.draw.rectangle([0, TOP, W, BOT], fill=(88, 88, 88))
        G.draw.rectangle([0, 1100, W, BOT], fill=(50, 50, 50))
        p = ease_in_out((t - a1 - 1.8) / 1.6) if t >= a1 + 1.8 else 0.0
        fx, fy = 560, 1080
        tilt = -0.28 + 0.5 * p
        L = 520
        xa, ya = fx - L * 0.35 * math.cos(tilt), fy - 30 - L * 0.35 * math.sin(tilt)
        xb, yb = fx + L * 0.65 * math.cos(tilt), fy - 30 + L * 0.65 * math.sin(tilt)
        rock(xa - 60, ya - 90 - 10 * p, 120, (160, 160, 160))
        G.draw.polygon([(fx - 50, 1100), (fx + 50, 1100), (fx, fy - 20)], fill=(140, 140, 140), outline=INK, width=4)
        if t >= a1 + 1.0:
            plank(xa - 60, ya, xb, yb, 30, (200, 200, 200))
        child(860, 1100, 1.4 if t < a1 else 1.4, arm_dy=40 * p)
        serif(t, 1.4, (W / 2, 260), "knows almost nothing", 46, WHITE, fnt=SERIF_R, until=a1)
        if p > 0.3:
            serif(t, a1 + 2.4, (W / 2, 260), "A PLANK BECOMES A LEVER", 48, WHITE, track=0.12)
            G.draw.line([(xa - 60, ya - 260), (xa - 60, ya - 340)], fill=WHITE, width=8)
            G.draw.polygon([(xa - 60, ya - 370), (xa - 85, ya - 330), (xa - 35, ya - 330)], fill=WHITE)
    elif t < a3:                                        # generalization
        Ctx.bw = False
        stage(RED, (120, 0, 10), t, a2, flats=BLACK)
        kanji((W / 2, 560), "汎化", 260, WHITE, fade(t, a2 + 0.4))
        serif(t, a2 + 0.6, (W / 2, 800), "GENERALIZATION", 62, WHITE, track=0.15)
        serif(t, a2 + 1.2, (W / 2, 900), "handling what you've never seen", 42, (255, 210, 210), fnt=SERIF_R)
    else:                                               # Chollet
        Ctx.bw = False
        stage(SILVER, (150, 155, 165), t, a3, flats=BLACK)
        serif(t, a3 + 0.3, (W / 2, 250), "FRANÇOIS CHOLLET  ·  AI RESEARCHER", 30, BLACK, track=0.12)
        serif(t, a3 + 0.8, (W / 2, 420), "Intelligence isn't\nhow much you know.", 60, BLACK)
        p2 = TL.phrases("ch3", 5, ["It's how"])[0]
        serif(t, p2, (W / 2, 640), "It's how efficiently\nyou learn what you don't.", 60, RED)
        if t >= p2 + 0.6:   # two learners: lots of knowledge vs fast learning
            x0, y0, w, h = 150, 1010, 780, 260
            G.draw.line([(x0, y0 + h), (x0 + w, y0 + h)], fill=BLACK, width=4)
            G.draw.line([(x0, y0), (x0, y0 + h)], fill=BLACK, width=4)
            k = ease_out_cubic((t - p2 - 0.6) / 1.2)
            a = [(x0 + u * w * k, y0 + h - 150 - 30 * u) for u in np.linspace(0, 1, 30)]
            b = [(x0 + u * w * k, y0 + h - 30 - 220 * (1 - math.exp(-3 * u))) for u in np.linspace(0, 1, 30)]
            G.draw.line(a, fill=(90, 90, 100), width=7)
            G.draw.line(b, fill=RED, width=9)
            G.draw.text((x0 + w, y0 + h - 205), "learns fast", font=font(SERIF, 30), fill=RED, anchor="rm")
            G.draw.text((x0 + w, y0 + h - 150), "knows a lot", font=font(SERIF, 30), fill=(70, 70, 80), anchor="rm")
            G.draw.text((x0 + w / 2, y0 + h + 30), "new situations →", font=font(SERIF_R, 28), fill=BLACK, anchor="mm")
    letterbox()
    subtitle(t, "ch3")


def s_ch4(t):
    if chapter_card(t, "ch4"):
        Ctx.bw = False
        return
    Ctx.bw = False
    blank()
    a1, aa, a2 = ls("ch4", 1), ls("ch4", 2), ls("ch4", 3)
    if aa <= t < a2:
        arc_scene(t, aa)
    elif t < aa:
        stage(GOLD, GOLD_D, t, 1.2, flats=BLACK)
        for i in range(48):   # a towering library
            c, r = i % 12, i // 12
            h = 120 + (i * 37) % 60
            x = 90 + c * 75
            y = 1040 - r * 150
            G.draw.rectangle([x, y - h, x + 60, y], fill=((i * 53) % 120 + 60, 20, 20) if i % 3 else (30, 40, 90),
                             outline=BLACK, width=3)
        serif(t, 1.6, (W / 2, 230), "MORE KNOWLEDGE THAN ANY LIBRARY", 36, BLACK, track=0.1)
        serif(t, TL.phrases("ch4", 0, ["and can reason"])[0], (W / 2, 300), "+ REASONING ON MANY NEW PROBLEMS", 32, BLACK,
              track=0.08)
        if t >= a1:
            G.draw.rectangle([0, TOP, W, BOT], fill=BLACK)
            q = fade(t, a1, d=0.4)
            G.draw.text((W / 2, 680), "?", font=font(SERIF, 520), fill=dim(RED, q), anchor="mm")
            serif(t, a1 + 0.4, (W / 2, 1060), "HOW FAR DO THEY GENERALIZE?", 42, WHITE, track=0.12)
            serif(t, a1 + 1.0, (W / 2, 1140), "an open question", 40, (220, 200, 200), fnt=SERIF_R)
    else:
        G.draw.rectangle([0, TOP, W, BOT], fill=PAPER)
        k = ease_in_out((t - a2 - 0.2) / 2.2)
        enso(W / 2, 720, 330, k, t)
        kanji((W / 2, 720), "知", 300, (150, 10, 20), fade(t, a2 + 1.4, d=0.6))
        p = TL.phrases("ch4", 3, ["Intelligence"])[0]
        serif(t, a2 + 0.2, (W / 2, 240), "Knowledge is the ink.", 54, INK)
        serif(t, p, (W / 2, 1180), "Intelligence is\nthe hand that writes.", 60, (150, 10, 20))
    letterbox()
    subtitle(t, "ch4")


def crow_scene(t, at):
    d = G.draw
    d.rectangle([0, TOP, W, BOT], fill=(96, 96, 96))
    d.rectangle([0, 1120, W, BOT], fill=(55, 55, 55))
    d.rectangle([640, 520, 780, 1120], outline=(220, 220, 220), width=8)       # tube with food at the bottom
    d.ellipse([670, 1050, 750, 1110], fill=(200, 200, 200))
    k = ease_in_out((t - at - 0.6) / 1.8)
    bx, by = 400, 880
    d.ellipse([bx - 130, by - 70, bx + 110, by + 70], fill=INK)                  # crow
    d.polygon([(bx - 120, by), (bx - 260, by - 40), (bx - 250, by + 30)], fill=INK)
    d.ellipse([bx + 60, by - 150, bx + 160, by - 50], fill=INK)
    d.polygon([(bx + 150, by - 110), (bx + 240, by - 95), (bx + 150, by - 80)], fill=(60, 60, 60))
    d.ellipse([bx + 118, by - 118, bx + 134, by - 102], fill=(230, 230, 230))
    for sg in (-30, 30):
        d.line([(bx + sg, by + 60), (bx + sg, by + 240)], fill=INK, width=10)
    hook_len = 60 * k
    wx0, wy0 = bx + 235, by - 95
    pts = [(wx0, wy0), (wx0 + 200, wy0 + 40)]
    if k > 0:
        pts.append((wx0 + 200 + hook_len * 0.4, wy0 + 40 + hook_len))
        pts.append((wx0 + 200 - hook_len * 0.4, wy0 + 40 + hook_len * 1.2))
    d.line(pts, fill=(235, 235, 235), width=9, joint="curve")
    serif(t, at + 0.3, (W / 2, 260), "NEW CALEDONIAN CROW", 42, WHITE, track=0.15)
    serif(t, at + 2.0, (W / 2, 340), "wire → hook, untaught", 40, WHITE, fnt=SERIF_R)


def giraffe(x, y, s, col):
    d = G.draw
    d.ellipse([x - 90 * s, y - 50 * s, x + 90 * s, y + 50 * s], fill=col)
    d.polygon([(x + 40 * s, y - 30 * s), (x + 80 * s, y - 30 * s), (x + 140 * s, y - 250 * s), (x + 110 * s, y - 260 * s)],
              fill=col)
    d.ellipse([x + 100 * s, y - 290 * s, x + 185 * s, y - 245 * s], fill=col)
    for dx in (-70, -40, 45, 75):
        d.line([(x + dx * s, y + 30 * s), (x + dx * s, y + 170 * s)], fill=col, width=int(14 * s))
    for sx, sy in ((-40, -10), (20, 5), (60, -20), (100, -150), (-5, 25)):
        d.ellipse([x + sx * s - 12 * s, y + sy * s - 10 * s, x + sx * s + 12 * s, y + sy * s + 10 * s], fill=GOLD_D)


def giraffe_scene(t, at):
    G.draw.rectangle([0, TOP, W / 2, BOT], fill=PAPER)
    G.draw.rectangle([W / 2, TOP, W, BOT], fill=(20, 20, 30))
    G.draw.rectangle([90, 520, W / 2 - 90, 1000], outline=INK, width=6)
    giraffe(W / 4 - 40, 860, 0.9, (225, 170, 60))
    serif(t, at + 0.2, (W / 4, 300), "CHILD", 56, INK, track=0.2)
    serif(t, at + 0.4, (W / 4, 1100), "1 picture", 46, RED)
    p = TL.phrases("ch3", 3, ["Early AI"])[0]
    serif(t, p, (3 * W / 4, 300), "EARLY AI", 56, WHITE, track=0.2)
    if t >= p:
        n = int(900 * ease_out_cubic((t - p) / 1.4))
        for i in range(n):
            c, r = i % 30, i // 30
            G.draw.rectangle([W / 2 + 40 + c * 15, 480 + r * 18, W / 2 + 52 + c * 15, 494 + r * 18],
                             fill=(200, 150, 50) if (i * 7) % 5 else (120, 90, 40))
        serif(t, p + 0.6, (3 * W / 4, 1100), "thousands", 46, GOLD)


ARC_COLS = [(20, 20, 20), (30, 110, 230), (220, 40, 40), (40, 180, 70), (240, 200, 30)]


def arc_grid(x0, y0, cell, g):
    for r, row in enumerate(g):
        for c, v in enumerate(row):
            G.draw.rectangle([x0 + c * cell, y0 + r * cell, x0 + (c + 1) * cell - 3, y0 + (r + 1) * cell - 3],
                             fill=ARC_COLS[v])


def arc_scene(t, at):
    G.draw.rectangle([0, TOP, W, BOT], fill=(34, 34, 40))
    serif(t, at + 0.1, (W / 2, 230), "THE ARC PUZZLES", 50, WHITE, track=0.2)
    box = [[0, 0, 0, 0, 0], [0, 1, 1, 1, 0], [0, 1, 0, 1, 0], [0, 1, 1, 1, 0], [0, 0, 0, 0, 0]]
    fill = [[0, 0, 0, 0, 0], [0, 1, 1, 1, 0], [0, 1, 4, 1, 0], [0, 1, 1, 1, 0], [0, 0, 0, 0, 0]]
    box2 = [[2, 2, 2, 2, 0], [2, 0, 0, 2, 0], [2, 0, 0, 2, 0], [2, 2, 2, 2, 0], [0, 0, 0, 0, 0]]
    fill2 = [[2, 2, 2, 2, 0], [2, 4, 4, 2, 0], [2, 4, 4, 2, 0], [2, 2, 2, 2, 0], [0, 0, 0, 0, 0]]
    test = [[0, 0, 0, 0, 0], [3, 3, 3, 3, 3], [3, 0, 0, 0, 3], [3, 3, 3, 3, 3], [0, 0, 0, 0, 0]]
    for i, (a, b) in enumerate(((box, fill), (box2, fill2), (test, None))):
        y = 360 + i * 300
        if t < at + 0.4 + i * 0.6:
            continue
        arc_grid(170, y, 48, a)
        G.draw.text((W / 2, y + 120), "→", font=font(SANS, 80), fill=WHITE, anchor="mm")
        if b is not None:
            arc_grid(670, y, 48, b)
        else:
            G.draw.rectangle([670, y, 910, y + 240], outline=GOLD, width=5)
            G.draw.text((790, y + 120), "?", font=font(SERIF, 150), fill=GOLD, anchor="mm")
    serif(t, at + 2.2, (W / 2, 1320), "easy for people · hard for AI", 40, GOLD, fnt=SERIF_R)


SCENE_FNS = {"hook": s_hook, "ch1": s_ch1, "ch2": s_ch2, "ch3": s_ch3, "ch4": s_ch4}
SCENES = [(TL.dur[k], SCENE_FNS[k]) for k, *_ in SCRIPT]
TOTAL = TL.total

_rng = np.random.default_rng(1985)
GRAIN = [_rng.normal(0, 14, (H // 2, W // 2)).astype(np.int16).repeat(2, 0).repeat(2, 1) for _ in range(4)]


def post(arr, fi, t, idx, tl):
    if not Ctx.bw:
        return arr
    g = arr.mean(axis=2).astype(np.int16)
    g = (g * (1 + 0.05 * math.sin(fi * 2.1))).astype(np.int16) + GRAIN[fi % 4]
    g[TOP:BOT] = np.clip(g[TOP:BOT], 0, 255)
    g[:TOP] = 0
    g[BOT:] = arr[BOT:].mean(axis=2)
    g = np.clip(g, 0, 255).astype(np.uint8)
    return np.repeat(g[..., None], 3, axis=2)


# ---------------------------------------------------------------- score: minimalist string ostinato

SR = E.SR


def _tt(d):
    return np.arange(int(d * SR)) / SR


def string(f, d, bright=6):
    x = _tt(d)
    vib = 1 + 0.003 * np.sin(2 * np.pi * 5.5 * x)
    ph = 2 * np.pi * f * np.cumsum(vib) / SR
    y = sum(np.sin(k * ph) / k ** 1.3 for k in range(1, bright))
    return y * np.minimum(1, x / 0.02) * np.minimum(1, (d - x) / 0.04)


def extra_sfx(sr):
    x = _tt(0.05)
    clap = np.random.default_rng(4).standard_normal(len(x)) * np.exp(-x * 120) + np.sin(2 * np.pi * 1900 * x) * np.exp(-x * 90)
    two = np.concatenate([clap, np.zeros(int(0.11 * SR)), clap * 0.8])
    return {"pop": (two, 0.35)}


def music_fn(n):
    out = np.zeros(n)

    def add(sig, t, g):
        i = int(t * SR)
        if i < n:
            j = min(n, i + len(sig))
            out[i:j] += sig[: j - i] * g

    total = E.TOTAL
    starts, acc = {}, 0.0
    for k, *_ in SCRIPT:
        starts[k] = acc
        acc += TL.dur[k]
    hush0 = starts["ch2"] + ls("ch2", 2) - 0.1          # silence for "Nothing happens."
    hush1 = starts["ch2"] + le("ch2", 2) + 0.9
    e8 = 60 / 138 / 2
    prog = [(110.0, [220.0, 261.63, 329.63]), (87.31, [174.61, 220.0, 261.63]), (73.42, [146.83, 174.61, 220.0]),
            (82.41, [164.81, 207.65, 246.94])]   # Am  F  Dm  E
    pat = [0, 1, 2, 1, 2, 1]
    t, bar = 0.0, 0
    while t < total:
        root, ch = prog[(bar // 2) % 4]
        layer2 = t > starts["ch1"]
        layer3 = t > starts["ch3"]
        for q in range(12):
            tq = t + q * e8
            if hush0 <= tq < hush1:
                continue
            add(string(ch[pat[q % 6]] * 2, e8 * 0.95), tq, 0.05)
            if layer2 and q % 2 == 0:
                add(string(ch[pat[(q // 2) % 3]] * 4, e8 * 1.9), tq, 0.025)
            if layer3:
                add(string(ch[(q // 4) % 3] * 1, e8 * 3.8, 4), tq, 0.02) if q % 4 == 0 else None
        if not (hush0 <= t < hush1):
            add(string(root, 12 * e8, 4), t, 0.06)
        t += 12 * e8
        bar += 1
    for k in ("ch1", "ch2", "ch3", "ch4"):   # a low stroke under each chapter card
        x = _tt(2.0)
        add(np.sin(2 * np.pi * 55 * x) * np.exp(-x * 2) + 0.4 * np.sin(2 * np.pi * 110 * x) * np.exp(-x * 3), starts[k], 0.5)
    voice = TL.track(n, SR)
    out = narrate.duck(out, voice, SR, depth=0.5)
    fade = int(2.0 * SR)
    end = int(total * SR)
    out[end - fade:end] *= np.linspace(1, 0, fade)
    out[end:] = 0
    return out * 0.8 + voice * 1.7


E.SCENE_CUT_FLASH = False
E.POST_FX = post

if __name__ == "__main__":
    print(f"total {TOTAL:.1f}s; " + ", ".join(f"{k} {TL.dur[k]:.1f}" for k, *_ in SCRIPT))
    E.main("what_is_intelligence.mp4", SCENES, music_fn, extra_sfx)

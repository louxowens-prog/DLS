#!/usr/bin/env python3
"""Render "THE PREDICTION FACTORY": a <2 min vertical short on how language models learn, in a
whimsical 1971 candy-factory style (evoking Willy Wonka & the Chocolate Factory without its
characters, names or songs): candy stripes, a chocolate river and waterfall, lollipop trees,
golden tickets, a clanking prediction machine, a psychedelic boat-tunnel spiral, a glass
elevator and a candy assembly line, over an original music-box waltz.
Female narration (Kokoro af_bella).

    python3 make_prediction_factory.py                  # -> out/the_prediction_factory.mp4
    python3 make_prediction_factory.py --preview 3 17   # frames -> out/preview/the_prediction_factory/
"""
import math
import textwrap

import numpy as np
from PIL import Image, ImageDraw

import make_video as E
import narrate
from make_video import G, H, W, cue, ease_in_out, ease_out_back, ease_out_cubic, font, pop

SERIF = "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"
SERIF_I = "/usr/share/fonts/truetype/freefont/FreeSerifBoldItalic.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
INK = (50, 20, 40)
CREAM = (255, 246, 222)
PINK = (255, 150, 190)
MINT = (150, 240, 205)
LEMON = (255, 236, 110)
LILAC = (200, 160, 255)
CHOC = (95, 52, 26)
CHOC_L = (140, 82, 40)
GOLD = (242, 196, 55)
GOLD_D = (160, 115, 20)
VELVET = (95, 25, 115)
RED = (230, 45, 60)
WHITE = (255, 255, 255)

SCRIPT = [
    ("hook", 0.5, ["Every chatbot you've ever used learned from one strange game: guess the next word."], 0.4),
    ("game", 0.3, ["Take: the Earth revolves around the, blank.",
                   "At first, the model guesses almost at random. Ocean. Wrong.",
                   "Training measures how wrong it was, then nudges billions of tiny internal dials toward the right answer.",
                   "Again, and again, until: Sun."], 0.4),
    ("hard", 0.3, ["Now try: because Earth's axis is tilted, the northern hemisphere has summer when...",
                   "To finish that well, it helps to represent the Earth, sunlight, geometry, seasons, hemispheres, "
                   "orbits, and language itself."], 0.4),
    ("tunnel", 0.3, ["Repeat that across trillions of words.",
                     "And here's the surprise of the last decade: to predict complicated data really well, a model "
                     "has to learn a lot about the world that made the data.",
                     "He dropped the glass onto the concrete, and it... To guess shattered, you need something like: "
                     "glass, plus falling, plus concrete, means breakage."], 0.4),
    ("rise", 0.3, ["Scale it up, and abilities appear that nobody programmed in. Translating. Coding. Explaining jokes.",
                   "Then a second stage, with human feedback, turns that autocomplete into a helpful assistant."], 0.4),
    ("simple", 0.3, ["So is it just predicting the next word?",
                     "Well, Shakespeare was just neurons firing. Technically true. Not very explanatory."], 0.4),
    ("train", 0.3, ["Ask: a train leaves Chicago heading west at eighty miles an hour. How far does it go in two and a "
                    "half hours?",
                    "Getting the next words right can mean reading the problem, setting up variables, picking a "
                    "formula, doing the arithmetic, checking it, and putting it into words. Two hundred miles."], 0.4),
    ("debate", 0.3, ["Is that real reasoning? Philosophers still argue.",
                     "Researchers peeking inside models have found features for concepts, and even signs of planning "
                     "ahead, like choosing a rhyme before writing the line.",
                     "But models still make mistakes a careful person wouldn't."], 0.4),
    ("outro", 0.3, ["Predicting the next word is the job description.",
                    "What it takes to do that job is the fascinating part."], 2.2),
]
TL = narrate.Timeline(SCRIPT, sid=1, speed=1.12)
ls, le = TL.start, TL.end

# ---------------------------------------------------------------- the factory


def gradient(top, bot, h0, h1):
    a = np.linspace(0, 1, h1 - h0)[:, None, None]
    arr = np.array(top) * (1 - a) + np.array(bot) * a
    return Image.fromarray(np.broadcast_to(arr, (h1 - h0, W, 3)).astype(np.uint8))


_rooms = {}


def room(wall=(255, 232, 240), wall2=(255, 200, 225), floor=(160, 230, 190)):
    key = (wall, wall2, floor)
    if key not in _rooms:
        img = Image.new("RGB", (W, H), CREAM)
        img.paste(gradient(wall, wall2, 0, 1000), (0, 0))
        d = ImageDraw.Draw(img)
        for i in range(-20, 60):   # candy-stripe wainscot
            x = i * 40
            d.polygon([(x, 1000), (x + 20, 1000), (x + 80, 1080), (x + 60, 1080)], fill=RED)
        d.rectangle([0, 990, W, 1000], fill=GOLD)
        d.rectangle([0, 1080, W, 1090], fill=GOLD)
        img.paste(gradient(floor, tuple(max(0, c - 40) for c in floor), 1090, 1420), (0, 1090))
        _rooms[key] = img
    G.img = _rooms[key].copy()
    G.draw = ImageDraw.Draw(G.img)


def lollipop(x, y, r, t, cols=(PINK, WHITE)):
    d = G.draw
    d.rectangle([x - 8, y, x + 8, y + 360], fill=WHITE, outline=INK, width=3)
    d.ellipse([x - r, y - r, x + r, y + r], fill=cols[1], outline=INK, width=5)
    pts = []
    for i in range(160):
        u = i / 160
        a = u * 6 * math.pi + t * 2
        pts.append((x + r * u * math.cos(a), y + r * u * math.sin(a)))
    d.line(pts, fill=cols[0], width=int(r * 0.2))


def river(t, y0=1260):
    d = G.draw
    top = [(x, y0 + 14 * math.sin(x / 70 + t * 2.2)) for x in range(0, W + 20, 20)]
    d.polygon(top + [(W, 1420), (0, 1420)], fill=CHOC)
    for k in range(4):
        yy = y0 + 40 + k * 30
        pts = [(x, yy + 6 * math.sin(x / 50 + t * 3 + k)) for x in range(0, W + 20, 20)]
        d.line(pts, fill=CHOC_L, width=4)
    fx = 60   # waterfall
    d.rectangle([fx, 300, fx + 90, y0 + 10], fill=CHOC)
    for k in range(6):
        yy = 300 + ((t * 400 + k * 170) % (y0 - 300))
        d.line([(fx + 12 + k * 13, yy), (fx + 12 + k * 13, yy + 60)], fill=CHOC_L, width=5)
    for k in range(5):
        a = t * 4 + k
        d.ellipse([fx + 45 + 60 * math.cos(a) - 18, y0 + 5 - 18 * abs(math.sin(a)) - 14,
                   fx + 45 + 60 * math.cos(a) + 18, y0 + 5 - 18 * abs(math.sin(a)) + 14], fill=CREAM)


def scallops():
    """Gilded Victorian border."""
    d = G.draw
    for x in range(0, W + 40, 40):
        d.ellipse([x - 20, -20, x + 20, 20], fill=GOLD, outline=GOLD_D, width=2)
    for y in range(0, 1420, 40):
        for x in (0, W):
            d.ellipse([x - 20, y - 20, x + 20, y + 20], fill=GOLD, outline=GOLD_D, width=2)


def playbill(t, at, xy, s, size, col=VELVET, edge=GOLD, until=None, fnt=SERIF_I):
    if t < at or (until is not None and t >= until):
        return
    size *= pop(t, at, 0.3)
    if size < 8:
        return
    f = font(fnt, size)
    lines = s.split("\n")
    wmax = max(f.getlength(ln) for ln in lines)
    if wmax > W - 100:
        size *= (W - 100) / wmax
        f = font(fnt, size)
    kw = dict(font=f, anchor="mm", align="center", spacing=int(size * 0.1))
    sw = max(3, int(size * 0.07))
    G.draw.multiline_text((xy[0] + 5, xy[1] + 6), s, fill=INK, stroke_width=sw, stroke_fill=INK, **kw)
    G.draw.multiline_text(xy, s, fill=col, stroke_width=sw, stroke_fill=edge, **kw)


def ticket(cx, cy, w, h, text, k=1.0, head="GOLDEN TICKET"):
    if k <= 0.05 or h * k < 90 or w * k < 90:
        return
    w, h = w * k, h * k
    d = G.draw
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    d.rectangle([x0 + 12, y0 + 12, x1 + 12, y1 + 12], fill=INK)
    d.rectangle([x0, y0, x1, y1], fill=GOLD, outline=GOLD_D, width=6)
    for x in np.arange(x0 + 20, x1 - 10, 26):
        d.ellipse([x - 6, y0 + 10, x + 6, y0 + 22], fill=LEMON)
        d.ellipse([x - 6, y1 - 22, x + 6, y1 - 10], fill=LEMON)
    d.rectangle([x0 + 30, y0 + 34, x1 - 30, y1 - 34], outline=GOLD_D, width=3)
    if k > 0.9:
        d.text((cx, y0 + 62), head, font=font(SERIF, 30), fill=GOLD_D, anchor="mm")
        wrapped = "\n".join(textwrap.wrap(text, 26))
        d.multiline_text((cx, cy + 20), wrapped, font=font(SERIF_I, 44), fill=INK, anchor="mm", align="center",
                         spacing=8)


def gauge(cx, cy, r, a, col):
    d = G.draw
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CREAM, outline=INK, width=5)
    for k in range(7):
        aa = math.radians(200 + k * 23.3)
        d.line([(cx + r * 0.7 * math.cos(aa), cy + r * 0.7 * math.sin(aa)),
                (cx + r * 0.9 * math.cos(aa), cy + r * 0.9 * math.sin(aa))], fill=INK, width=3)
    d.line([(cx, cy), (cx + r * 0.8 * math.cos(a), cy + r * 0.8 * math.sin(a))], fill=col, width=7)
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=INK)


def machine(cx, cy, t, wiggle=1.0, out=None, out_col=MINT):
    """The Prediction Machine: funnel, pipes, dials, steam and an output chute."""
    d = G.draw
    shake = math.sin(t * 40) * 4 * wiggle
    cx += shake
    d.polygon([(cx - 120, cy - 330), (cx + 120, cy - 330), (cx + 40, cy - 230), (cx - 40, cy - 230)], fill=PINK,
              outline=INK, width=6)
    d.rounded_rectangle([cx - 250, cy - 230, cx + 250, cy + 160], 40, fill=LILAC, outline=INK, width=7)
    for (x, y) in ((cx - 225, cy - 205), (cx + 225, cy - 205), (cx - 225, cy + 135), (cx + 225, cy + 135)):
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=GOLD, outline=INK, width=2)
    for i, (gx, col) in enumerate(((cx - 140, RED), (cx, VELVET), (cx + 140, (30, 140, 90)))):
        a = math.radians(200 + 140 * (0.5 + 0.45 * math.sin(t * (3 + i) * wiggle + i * 2)))
        gauge(gx, cy - 90, 58, a, col)
    d.rectangle([cx - 200, cy + 20, cx + 200, cy + 60], fill=CREAM, outline=INK, width=4)
    for k in range(9):
        on = (int(t * 8) + k) % 3 == 0
        d.ellipse([cx - 185 + k * 44, cy + 28, cx - 161 + k * 44, cy + 52], fill=LEMON if on else (170, 150, 120))
    d.rectangle([cx + 250, cy - 60, cx + 330, cy - 20], fill=MINT, outline=INK, width=4)
    d.rectangle([cx + 330, cy - 60, cx + 370, cy + 220], fill=MINT, outline=INK, width=4)
    for k in range(3):
        ph = (t * 1.3 + k * 0.33) % 1
        r = 26 + 50 * ph
        x, y = cx - 180 + k * 30, cy - 260 - 200 * ph
        d.ellipse([x - r, y - r * 0.8, x + r, y + r * 0.8], fill=(255, 255, 255))
    if out:
        k = ease_out_back(min(1, out[1]))
        w = max(120, font(SERIF, 64).getlength(out[0]) + 70) * k
        ox, oy = cx + 350, cy + 290
        if w > 20:
            d.rounded_rectangle([ox - w / 2, oy - 55 * k, ox + w / 2, oy + 55 * k], 50, fill=out_col, outline=INK, width=6)
            if k > 0.8:
                d.text((ox, oy), out[0], font=font(SERIF, 64), fill=INK, anchor="mm")


def gumdrop(x, y, r, col, lab, k=1.0):
    if k <= 0.05:
        return
    r *= k
    d = G.draw
    d.chord([x - r, y - r, x + r, y + r], 180, 360, fill=col, outline=INK, width=5)
    d.rectangle([x - r, y - 2, x + r, y + 10], fill=col, outline=INK, width=4)
    for i in range(6):
        sx, sy = x + r * 0.6 * math.cos(i * 1.1), y - r * 0.45 - r * 0.25 * math.sin(i * 1.7)
        d.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=WHITE)
    if k > 0.8:
        d.text((x, y + 45), lab, font=font(SERIF, 36), fill=INK, anchor="mm")


def subtitle(t, key):
    a = TL.active(key, t)
    if not a:
        return
    txt = "\n".join(textwrap.wrap(a[0], 32))
    f = font(SERIF, 48)
    bb = G.draw.multiline_textbbox((W / 2, 1600), txt, font=f, anchor="mm", align="center", spacing=8)
    r = [bb[0] - 36, bb[1] - 22, bb[2] + 36, bb[3] + 24]
    G.draw.rounded_rectangle([r[0] + 8, r[1] + 8, r[2] + 8, r[3] + 8], 26, fill=INK)
    G.draw.rounded_rectangle(r, 26, fill=VELVET, outline=GOLD, width=6)
    G.draw.multiline_text((W / 2, 1600), txt, font=f, fill=LEMON, anchor="mm", align="center", spacing=8)


def base_stage(t):
    G.draw.rectangle([0, 1420, W, H], fill=(40, 12, 44))
    scallops()


# ---------------------------------------------------------------- scenes


def s_hook(t):
    room()
    lollipop(900, 560, 120, t)
    lollipop(200, 640, 90, -t, (MINT, WHITE))
    river(t)
    playbill(t, 0.2, (W / 2, 250), "THE PREDICTION\nFACTORY", 120, VELVET)
    p = TL.phrases("hook", 0, ["guess the next"])[0]
    ticket(W / 2, 760, 780, 360, "The ___ goes on", ease_out_back((t - p) / 0.4) if t >= p else 0)
    cue("ding", p)
    base_stage(t)
    subtitle(t, "hook")


def s_game(t):
    room((230, 245, 255), (200, 225, 255), (190, 170, 240))
    river(t)
    a0, a1, a2, a3 = (ls("game", i) for i in range(4))
    ticket(W / 2, 250, 860, 250, "The Earth revolves around the ___.", ease_out_back(t / 0.4), "TRAINING TICKET")
    wig = 1.0 if t < a2 else 2.2
    out = None
    p_ocean = TL.phrases("game", 1, ["Ocean"])[0]
    if p_ocean <= t < a2:
        out = ("ocean", min(1, (t - p_ocean) / 0.3))
    elif t >= TL.phrases("game", 3, ["Sun"])[0]:
        out = ("Sun", min(1, (t - TL.phrases("game", 3, ["Sun"])[0]) / 0.3))
    machine(W / 2 - 110, 800, t, wig, out, RED if out and out[0] == "ocean" else MINT)
    cue("buzz", p_ocean + 0.2)
    if p_ocean + 0.3 <= t < a2:
        playbill(t, p_ocean + 0.3, (W / 2, 1180), "WRONG!", 110, RED, WHITE)
    if a2 <= t < a3:
        playbill(t, a2 + 0.2, (W / 2, 1150), "error → nudge every dial", 56, VELVET)
        lab = f"{'✦' * (1 + int((t - a2) * 3) % 4)}"
    if t >= a3:
        tries = int(min(99, (t - a3) * 60)) + 1
        G.draw.text((W / 2 - 110, 1180), f"attempt #{tries:,}0,000", font=font(SERIF, 40), fill=INK, anchor="mm")
    sun_at = TL.phrases("game", 3, ["Sun"])[0]
    cue("ding", sun_at + 0.1)
    if t >= sun_at:
        k = pop(t, sun_at, 0.3)
        G.draw.ellipse([W / 2 + 280 - 70 * k, 330 - 70 * k, W / 2 + 280 + 70 * k, 330 + 70 * k], fill=LEMON)
    base_stage(t)
    subtitle(t, "game")


CONCEPTS = [("Earth", PINK), ("sunlight", LEMON), ("geometry", MINT), ("seasons", LILAC), ("hemispheres", (255, 190, 130)),
            ("orbits", (140, 210, 255)), ("language", RED)]


def s_hard(t):
    room((255, 240, 220), (255, 215, 180), (255, 200, 150))
    river(t)
    ticket(W / 2, 330, 900, 420, "Because Earth's axis is tilted, the Northern Hemisphere has summer when ___",
           ease_out_back(t / 0.4), "HARDER TICKET")
    ts = TL.phrases("hard", 1, [c for c, _ in CONCEPTS])
    for i, ((c, col), at) in enumerate(zip(CONCEPTS, ts)):
        cue("pop", at)
        if t < at:
            continue
        x = 170 + (i % 4) * 245 + (120 if i >= 4 else 0)
        y = 800 + (i // 4) * 230
        gumdrop(x, y, 95, col, c, ease_out_back((t - at) / 0.3))
    base_stage(t)
    subtitle(t, "hard")


def spiral(t, cx=W / 2, cy=700):
    d = G.draw
    cols = [PINK, LEMON, MINT, LILAC, (255, 170, 110), (140, 210, 255)]
    d.rectangle([0, 0, W, 1420], fill=(30, 10, 40))
    for arm in range(12):
        pts = []
        for i in range(60):
            u = i / 59
            r = 20 + 1300 * u ** 1.6
            a = arm * math.pi / 6 + u * 5 + t * 1.8
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        pts2 = []
        for i in range(59, -1, -1):
            u = i / 59
            r = 20 + 1300 * u ** 1.6
            a = arm * math.pi / 6 + math.pi / 12 + u * 5 + t * 1.8
            pts2.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        d.polygon(pts + pts2, fill=cols[arm % 6])


def s_tunnel(t):
    a1, a2 = ls("tunnel", 1), ls("tunnel", 2)
    if t < a2:
        spiral(t * (1.6 if t < a1 else 1.0))
        d = G.draw
        d.ellipse([W / 2 - 170, 1080, W / 2 + 170, 1220], fill=(200, 60, 120), outline=INK, width=6)   # the boat
        d.polygon([(W / 2 - 120, 1150), (W / 2 + 120, 1150), (W / 2, 1000)], fill=CREAM, outline=INK, width=4)
        if t < a1:
            playbill(t, 0.3, (W / 2, 330), "TRILLIONS\nOF WORDS", 130, LEMON, VELVET)
        else:
            playbill(t, a1 + 0.2, (W / 2, 280), "THE SURPRISE:", 80, WHITE, VELVET)
            playbill(t, a1 + 1.4, (W / 2, 470), "predict the data well\n→ learn the world\nthat made it", 70, LEMON,
                     VELVET)
    else:
        room((235, 235, 245), (210, 210, 230), (150, 150, 160))
        d = G.draw
        d.rectangle([0, 1090, W, 1420], fill=(120, 120, 125))
        for k in range(8):
            d.line([(k * 150, 1090), (k * 150 - 60, 1420)], fill=(95, 95, 100), width=4)
        p_sh = TL.phrases("tunnel", 2, ["To guess"])[0]
        k = ease_in_out((t - a2 - 0.3) / 1.2)
        gy = 360 + 700 * k
        if t < p_sh:
            gx = W / 2
            d.polygon([(gx - 60, gy - 110), (gx + 60, gy - 110), (gx + 40, gy + 60), (gx - 40, gy + 60)],
                      fill=(210, 240, 255), outline=(90, 140, 190), width=6)
            d.rectangle([gx - 10, gy + 60, gx + 10, gy + 120], fill=(210, 240, 255), outline=(90, 140, 190), width=4)
        else:
            for i in range(14):
                a = i * 0.45
                r = 60 + 240 * ease_out_cubic((t - p_sh) / 0.5)
                x, y = W / 2 + r * math.cos(a) * 1.6, 1060 - abs(r * math.sin(a)) * 0.8
                d.polygon([(x, y), (x + 30, y + 12), (x + 8, y + 40)], fill=(210, 240, 255), outline=(90, 140, 190),
                          width=3)
            cue("crash", p_sh)
            playbill(t, p_sh + 0.2, (W / 2, 240), "glass + falling + concrete", 58, VELVET)
            playbill(t, p_sh + 0.9, (W / 2, 360), "= breakage", 90, RED, WHITE)
    base_stage(t)
    subtitle(t, "tunnel")


ABILITIES = [("Translating", "TRANSLATING", MINT), ("Coding", "CODING", LEMON), ("Explaining jokes", "EXPLAINING JOKES", PINK)]


def s_rise(t):
    a1 = ls("rise", 1)
    rise = ease_in_out(t / (a1 - 0.2)) if t < a1 else 1.0
    G.img = Image.new("RGB", (W, H), (120, 190, 255))
    G.draw = d = ImageDraw.Draw(G.img)
    for k in range(6):   # clouds rush past as the elevator climbs
        y = (k * 260 + rise * 1400) % 1500 - 80
        x = (k * 331) % W
        for dx in (-70, 0, 70):
            d.ellipse([x + dx - 90, y - 45, x + dx + 90, y + 45], fill=WHITE)
    ex, ey = W / 2, 820
    d.rectangle([ex - 230, ey - 260, ex + 230, ey + 200], fill=(200, 240, 255), outline=(60, 150, 200), width=10)
    d.line([(ex - 160, ey - 240), (ex - 60, ey + 180)], fill=WHITE, width=10)
    d.line([(ex - 100, ey - 240), (ex - 20, ey - 60)], fill=WHITE, width=6)
    for sx in (-1, 1):
        d.line([(ex + sx * 230, ey + 200), (ex + sx * 330, ey + 280)], fill=GOLD, width=10)
    ts = TL.phrases("rise", 0, [p for p, _, _ in ABILITIES])
    for i, ((_, lab, col), at) in enumerate(zip(ABILITIES, ts)):
        cue("pop", at)
        if t < at or t >= a1:
            continue
        k = ease_out_back((t - at) / 0.3)
        y = 270 + i * 150
        d.rounded_rectangle([W / 2 - 330 * k, y - 55, W / 2 + 330 * k, y + 55], 50, fill=col, outline=INK, width=6)
        if k > 0.8:
            d.text((W / 2, y), lab, font=font(SERIF, 52), fill=INK, anchor="mm")
    playbill(t, TL.phrases("rise", 0, ["nobody"])[0], (W / 2, 1160), "nobody programmed these in", 56, VELVET, WHITE,
             until=a1)
    if t >= a1:
        playbill(t, a1 + 0.1, (W / 2, 300), "STAGE 2:\nHUMAN FEEDBACK", 90, VELVET, GOLD)
        k = ease_out_cubic((t - a1 - 0.6) / 0.6)
        d.rounded_rectangle([140, 1060, 140 + 380 * k, 1200], 30, fill=CREAM, outline=INK, width=5)
        if k > 0.9:
            d.text((330, 1130), "autocomplete", font=font(SERIF_I, 44), fill=(150, 130, 120), anchor="mm")
            d.text((W / 2 + 10, 1130), "→", font=font(SANS, 70), fill=INK, anchor="mm")
            d.rounded_rectangle([W / 2 + 70, 1060, W - 120, 1200], 30, fill=MINT, outline=INK, width=5)
            d.text(((W / 2 + 70 + W - 120) / 2, 1130), "assistant", font=font(SERIF, 50), fill=INK, anchor="mm")
    base_stage(t)
    subtitle(t, "rise")


def s_simple(t):
    room((255, 225, 240), (230, 190, 255), (200, 170, 230))
    a1 = ls("simple", 1)
    d = G.draw
    if t < a1:
        playbill(t, 0.2, (W / 2, 520), "JUST THE\nNEXT WORD?", 140, VELVET, GOLD)
    else:
        d.ellipse([W / 2 - 230, 330, W / 2 + 230, 780], fill=(255, 225, 200), outline=INK, width=7)   # a quill-y bard
        d.polygon([(W / 2 - 240, 460), (W / 2 + 240, 460), (W / 2 + 200, 330), (W / 2 - 200, 330)], fill=(80, 60, 40))
        for sx in (-1, 1):
            d.ellipse([W / 2 + sx * 90 - 20, 540, W / 2 + sx * 90 + 20, 580], fill=INK)
        d.arc([W / 2 - 60, 600, W / 2 + 60, 680], 20, 160, fill=INK, width=6)
        d.polygon([(W / 2 - 250, 760), (W / 2 + 250, 760), (W / 2 + 180, 830), (W / 2 - 180, 830)], fill=WHITE, outline=INK,
                  width=5)
        for i in range(24):   # neurons firing
            a = i * 0.9 + t * 3
            x, y = W / 2 + 180 * math.cos(a) * (0.4 + 0.6 * ((i * 37) % 10) / 10), 470 + 90 * math.sin(a * 1.3)
            if (int(t * 12) + i) % 4 == 0:
                d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=LEMON, outline=GOLD_D, width=2)
        playbill(t, a1 + 0.1, (W / 2, 220), "\"just neurons firing\"", 72, VELVET)
        p = TL.phrases("simple", 1, ["Technically", "Not very"])
        playbill(t, p[0], (W / 2, 960), "technically true", 62, (30, 130, 80), WHITE)
        playbill(t, p[1], (W / 2, 1100), "not very explanatory", 62, RED, WHITE)
    base_stage(t)
    subtitle(t, "simple")


STEPS = [("reading", "READ", "the question"), ("variables", "VARIABLES", "v = 80, t = 2.5"),
         ("formula", "FORMULA", "d = v × t"), ("arithmetic", "ARITHMETIC", "80 × 2.5 = 200"),
         ("checking", "CHECK", "mph × h = miles ✓"), ("into words", "WORDS", "\"200 miles\"")]


def s_train(t):
    room((240, 255, 245), (200, 240, 220), (150, 200, 170))
    d = G.draw
    a1 = ls("train", 1)
    ticket(W / 2, 290, 920, 360, "A train leaves Chicago heading west at 80 mph. How far in 2.5 hours?",
           ease_out_back(t / 0.4), "PROBLEM TICKET")
    for row in range(2):
        y = 780 + row * 330
        d.rectangle([60, y + 110, W - 60, y + 140], fill=(90, 90, 110))
        for k in range(20):
            x = 60 + ((k * 52 + t * 120) % (W - 120))
            d.line([(x, y + 110), (x, y + 140)], fill=(60, 60, 80), width=5)
    ts = TL.phrases("train", 1, [p for p, _, _ in STEPS])
    for i, ((_, lab, note), at) in enumerate(zip(STEPS, ts)):
        cue("pop", at)
        c, r = i % 3, i // 3
        x, y = 200 + c * 340, 780 + r * 330
        on = t >= at
        col = [PINK, LEMON, MINT, LILAC, (255, 190, 130), (140, 210, 255)][i] if on else (205, 200, 210)
        d.rounded_rectangle([x - 150, y - 110, x + 150, y + 105], 26, fill=col, outline=INK, width=5)
        d.text((x, y - 70), f"{i + 1}", font=font(SERIF, 40), fill=INK, anchor="mm")
        d.text((x, y - 20), lab, font=font(SERIF, 38 if len(lab) < 10 else 30), fill=INK, anchor="mm")
        if on:
            d.text((x, y + 40), note, font=font(SANS, 24), fill=INK, anchor="mm")
            for k in range(3):
                ph = (t * 1.5 + k * 0.33 + i) % 1
                d.ellipse([x + 110 - 12 - 20 * ph, y - 140 - 90 * ph - 12, x + 110 + 12 + 20 * ph, y - 140 - 90 * ph + 12],
                          fill=WHITE)
    p = TL.phrases("train", 1, ["Two hundred miles"])[0]
    cue("ding", p)
    if t >= p:
        ticket(W / 2, 1280, 600, 220, "200 miles", ease_out_back((t - p) / 0.3), "ANSWER")
    base_stage(t)
    subtitle(t, "train")


def s_debate(t):
    room((250, 240, 255), (225, 210, 250), (190, 180, 230))
    d = G.draw
    a1, a2 = ls("debate", 1), ls("debate", 2)
    if t < a1:
        for sx, col, word in ((-1, PINK, "REAL\nREASONING!"), (1, MINT, "JUST\nPATTERNS!")):
            x = W / 2 + sx * 250
            d.ellipse([x - 130, 560, x + 130, 820], fill=(255, 225, 200), outline=INK, width=6)
            d.rectangle([x - 100, 820, x + 100, 1060], fill=col, outline=INK, width=6)
            d.rounded_rectangle([x - 200, 280, x + 200, 480], 40, fill=WHITE, outline=INK, width=5)
            d.multiline_text((x, 380), word, font=font(SERIF, 46), fill=INK, anchor="mm", align="center")
        playbill(t, 0.2, (W / 2, 1180), "philosophers: still arguing", 58, VELVET)
    elif t < a2:
        d.rectangle([90, 250, W - 90, 700], fill=CREAM, outline=GOLD_D, width=6)
        l1 = "He saw a carrot and had to grab it,"
        d.text((W / 2, 360), l1, font=font(SERIF_I, 44), fill=INK, anchor="mm")
        l2 = "His hunger was like a starving "
        pa = TL.phrases("debate", 1, ["even signs", "like choosing"])
        k = min(1, max(0, (t - pa[1] - 0.8) / 1.8))
        shown = l2[: int(len(l2) * k)]
        d.text((150, 480), shown, font=font(SERIF_I, 44), fill=INK, anchor="lm")
        if t >= pa[1]:
            x_end = 150 + font(SERIF_I, 44).getlength(l2)
            d.rounded_rectangle([x_end - 10, 450, x_end + 170, 512], 20, fill=LEMON, outline=GOLD_D, width=4)
            d.text((x_end + 80, 481), "rabbit", font=font(SERIF_I, 44), fill=RED, anchor="mm")
            playbill(t, pa[1] + 0.2, (W / 2, 620), "planned BEFORE the line", 52, RED, WHITE)
        d.ellipse([W / 2 - 170, 830, W / 2 + 170, 1170], outline=INK, width=16)   # magnifying glass
        d.line([(W / 2 + 120, 1120), (W / 2 + 260, 1300)], fill=INK, width=30)
        for i in range(10):
            x, y = W / 2 - 110 + (i % 4) * 70, 900 + (i // 4) * 90
            on = (int(t * 6) + i) % 3 == 0
            d.ellipse([x - 20, y - 20, x + 20, y + 20], fill=LEMON if on else LILAC, outline=INK, width=3)
        playbill(t, a1 + 0.2, (W / 2, 1300), "features for concepts", 50, VELVET)
    else:
        playbill(t, a2 + 0.1, (W / 2, 520), "STILL MAKES\nMISTAKES", 120, RED, WHITE)
        playbill(t, a2 + 0.7, (W / 2, 900), "a careful person wouldn't", 60, VELVET)
    base_stage(t)
    subtitle(t, "debate")


def s_outro(t):
    room()
    lollipop(900, 560, 120, t)
    lollipop(200, 640, 90, -t, (MINT, WHITE))
    river(t)
    ticket(W / 2, 330, 900, 300, "Predicting the next word", ease_out_back(t / 0.4), "THE JOB DESCRIPTION")
    p = ls("outro", 1)
    if t >= p:
        playbill(t, p + 0.2, (W / 2, 720), "what it takes to\ndo the job", 90, VELVET, GOLD)
        playbill(t, p + 1.2, (W / 2, 1000), "is the magic", 90, RED, WHITE)
    base_stage(t)
    subtitle(t, "outro")


SCENE_FNS = {"hook": s_hook, "game": s_game, "hard": s_hard, "tunnel": s_tunnel, "rise": s_rise, "simple": s_simple,
             "train": s_train, "debate": s_debate, "outro": s_outro}
SCENES = [(TL.dur[k], SCENE_FNS[k]) for k, *_ in SCRIPT]
TOTAL = TL.total


def post(arr, fi, t, idx, tl):
    a = arr.astype(np.int16)                     # warm 1971 Technicolor push
    a[..., 0] += 10
    a[..., 2] -= 8
    if idx > 0 and tl < 0.3:                     # iris-star wipe on each cut
        r = 2000 * ease_in_out(tl / 0.3)
        yy, xx = np.ogrid[0:H, 0:W]
        a[((xx - W / 2) ** 2 + (yy - 800) ** 2) > r * r] = np.array([95, 25, 115])
    return np.clip(a, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- score: music-box waltz

SR = E.SR


def _tt(d):
    return np.arange(int(d * SR)) / SR


def extra_sfx(sr):
    rng = np.random.default_rng(7)
    x = _tt(0.4)
    buzz = (2 * ((110 * x) % 1) - 1) * np.minimum(1, (0.4 - x) / 0.05)
    x2 = _tt(0.8)
    ding = (np.sin(2 * np.pi * 1568 * x2) + 0.5 * np.sin(2 * np.pi * 2349 * x2)) * np.exp(-x2 * 4)
    x3 = _tt(0.35)
    whistle = np.sin(2 * np.pi * np.cumsum(500 + 1400 * (x3 / 0.35) ** 1.5) / SR) * np.sin(np.pi * x3 / 0.35)
    x4 = _tt(0.12)
    popc = np.sin(2 * np.pi * np.cumsum(500 + 1500 * np.exp(-x4 * 40)) / SR) * np.exp(-x4 * 30)
    x5 = _tt(0.9)
    crash = rng.standard_normal(len(x5)) * np.exp(-x5 * 6) * 0.6
    for f in (2400, 3300, 4100, 5200):
        crash += np.sin(2 * np.pi * f * x5) * np.exp(-x5 * (5 + f / 1500)) * 0.25
    return {"buzz": (buzz, 0.3), "ding": (ding, 0.35), "whoosh": (whistle, 0.25), "pop": (popc, 0.25),
            "crash": (crash, 0.5)}


def music_fn(n):
    out = np.zeros(n)

    def add(sig, t, g):
        i = int(t * SR)
        if i < n:
            j = min(n, i + len(sig))
            out[i:j] += sig[: j - i] * g

    def box(f, d=0.7):
        x = _tt(d)
        return (np.sin(2 * np.pi * f * x) + 0.35 * np.sin(2 * np.pi * f * 4.02 * x) * np.exp(-x * 10)) * np.exp(-x * 4.5)

    def tuba(f, d):
        x = _tt(d)
        return sum(np.sin(2 * np.pi * f * k * x) / k ** 1.5 for k in range(1, 6)) * np.minimum(1, x / 0.02) * np.exp(-x * 4)

    beat = 60 / 168
    prog = [(130.81, [261.63, 329.63, 392.0]), (174.61, [261.63, 349.23, 440.0]), (98.0, [246.94, 293.66, 392.0]),
            (130.81, [261.63, 329.63, 392.0]), (110.0, [261.63, 329.63, 440.0]), (146.83, [293.66, 349.23, 440.0]),
            (98.0, [246.94, 293.66, 349.23]), (130.81, [261.63, 329.63, 392.0])]
    tune = [523.25, 659.25, 783.99, 659.25, 587.33, 523.25, 493.88, 587.33, 698.46, 659.25, 587.33, 523.25,
            440.0, 523.25, 659.25, 587.33, 523.25, 493.88, 523.25, 587.33, 659.25, 587.33, 523.25, 523.25]
    total = E.TOTAL
    starts, acc = {}, 0.0
    for k, *_ in SCRIPT:
        starts[k] = acc
        acc += TL.dur[k]
    t, bar = 0.0, 0
    while t < total:
        root, ch = prog[bar % 8]
        add(tuba(root / 2, beat * 0.9), t, 0.35)
        for b in (1, 2):
            for f in ch:
                add(box(f, 0.4), t + b * beat, 0.035)
        for b in range(3):
            add(box(tune[(bar * 3 + b) % len(tune)], 0.8), t + b * beat, 0.07)
        trip = starts["tunnel"] <= t < starts["tunnel"] + ls("tunnel", 2)
        if trip:   # the boat ride: detuned, swirling, eerie
            x = _tt(3 * beat)
            add(np.sin(2 * np.pi * np.cumsum(ch[0] * 2 * (1 + 0.03 * np.sin(2 * np.pi * 1.5 * x))) / SR) * 0.6, t, 0.08)
        t += 3 * beat
        bar += 1
    voice = TL.track(n, SR)
    out = narrate.duck(out, voice, SR, depth=0.55)
    fade = int(1.5 * SR)
    end = int(total * SR)
    out[end - fade:end] *= np.linspace(1, 0, fade)
    out[end:] = 0
    return out * 0.8 + voice * 1.7


E.SCENE_CUT_FLASH = False
E.POST_FX = post

if __name__ == "__main__":
    print(f"total {TOTAL:.1f}s; " + ", ".join(f"{k} {TL.dur[k]:.1f}" for k, *_ in SCRIPT))
    E.main("the_prediction_factory.mp4", SCENES, music_fn, extra_sfx)

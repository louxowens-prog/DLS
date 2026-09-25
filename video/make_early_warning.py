#!/usr/bin/env python3
"""Render "SEE IT COMING": a <2 min vertical short on AI spotting disease risk early, styled
after the candy-coloured hyper-reality of Speed Racer (2008): rainbow pseudo-3D race tracks,
sky loops, chrome lettering, racing HUDs and telemetry, sweeping helmet wipes, checkered
flags. Female narration (Kokoro af_bella).

    python3 make_early_warning.py                  # -> out/see_it_coming.mp4
    python3 make_early_warning.py --preview 3 17   # frames -> out/preview/see_it_coming/
"""
import colorsys
import math
import textwrap

import numpy as np
from PIL import Image, ImageDraw

import make_video as E
import narrate
from make_video import G, H, W, cue, ease_in_out, ease_out_back, ease_out_cubic, font, pop

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ITAL = "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf"
INK = (10, 8, 30)
WHITE = (255, 255, 255)
PINK = (255, 40, 150)
CYAN = (0, 220, 255)
LIME = (140, 255, 40)
YEL = (255, 225, 0)
ORNG = (255, 120, 0)
PURP = (140, 50, 255)
RED = (240, 20, 40)

SCRIPT = [
    ("hook", 0.5, ["Most diseases don't start with symptoms. They start as a whisper in the data.",
                   "And AI can hear the whisper."], 0.4),
    ("race", 0.4, ["Think of racing. The crash starts long before the wall. A good spotter sees it coming, laps ahead.",
                   "Medicine usually waits for the wall: the symptom. AI can be the spotter."], 0.4),
    ("laps", 0.3, ["Sepsis. AI alerts can flag it hours earlier. At Johns Hopkins, acting fast on alerts cut deaths by about a fifth.",
                   "Kidneys. Acute injury predicted up to two days before it happens.",
                   "Heart. A routine ten second E.C.G. can reveal a weakening heart before any symptoms.",
                   "Eyes. Retinal scans catch diabetic damage, and even hint at heart and kidney risk.",
                   "Cancer. Some models spot pancreatic cancer risk in medical records, years before diagnosis.",
                   "The brain. Subtle changes in voice, movement, even breathing during sleep, may signal Parkinson's early."], 0.4),
    ("record", 0.4, ["Now picture ten years of one person's records.",
                     "Blood sugar creeping up. A new medication. Weight rising. Resting heart rate climbing. "
                     "A small change on a scan.",
                     "Each one alone looks normal. Together, they form a curve.",
                     "The system says: evaluate this person now. Don't wait for symptoms."], 0.5),
    ("why", 0.3, ["Because timing is everything. Caught early, colon cancer's five year survival is about ninety percent. "
                  "Caught late, about fifteen."], 0.6),
    ("flags", 0.3, ["But a flag isn't a diagnosis.",
                    "Too many false alarms, and doctors tune them out. These models must be tested, fair, and private."], 0.4),
    ("outro", 0.3, ["That's the shift: from reactive medicine, to preventive medicine.",
                    "Don't wait for the crash. Read the road."], 2.2),
]
TL = narrate.Timeline(SCRIPT, sid=1, speed=1.12)
ls, le = TL.start, TL.end

LAPS = [("SEPSIS", "HOURS EARLIER", 0.55, "Johns Hopkins: fast response to\nalerts ≈ 1/5 fewer deaths", PINK),
        ("KIDNEYS", "UP TO 48 H EARLY", 0.7, "acute kidney injury,\npredicted before it happens", CYAN),
        ("HEART", "BEFORE SYMPTOMS", 0.8, "a routine 10-second ECG can flag\na weakening heart pump", RED),
        ("EYES", "EARLY DAMAGE", 0.65, "retinal photos: diabetic damage,\nplus hints of heart & kidney risk", LIME),
        ("CANCER", "YEARS EARLY", 0.95, "pancreatic cancer risk spotted in\nrecords years before diagnosis", ORNG),
        ("BRAIN", "EARLY SIGNS", 0.85, "voice, movement, sleep breathing:\nresearch on early Parkinson's", PURP)]

# ---------------------------------------------------------------- candy-coloured primitives


def hsv(h, s=1.0, v=1.0):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    return int(r * 255), int(g * 255), int(b * 255)


_sky = {}


def sky(top, bot):
    key = (top, bot)
    if key not in _sky:
        a = np.linspace(0, 1, 760)[:, None, None]
        arr = (np.array(top) * (1 - a) + np.array(bot) * a).astype(np.uint8)
        _sky[key] = Image.fromarray(np.broadcast_to(arr, (760, W, 3)).copy())
    return _sky[key]


HORIZON = 700


def track(t, speed=1.0, palette=((255, 60, 170), (255, 170, 60)), curve=0.0, loops=True, dimk=1.0):
    """Pseudo-3D rainbow race track with sky loops."""
    G.img = Image.new("RGB", (W, H), INK)
    G.img.paste(sky(*palette), (0, 0))
    G.draw = d = ImageDraw.Draw(G.img)
    if loops:   # floating rainbow track loops in the sky
        for j, (cx, cy, rx, ry) in enumerate(((260, 300, 330, 130), (820, 220, 260, 90), (560, 470, 520, 120))):
            for k in range(7):
                col = hsv(k / 7 + t * 0.1 + j * 0.2, 0.8, 1.0)
                d.ellipse([cx - rx - k * 6, cy - ry - k * 6, cx + rx + k * 6, cy + ry + k * 6], outline=col, width=5)
    for k in range(30):   # stadium lights
        x = (k * 97 + 40) % W
        d.ellipse([x - 5, HORIZON - 40 - (k % 3) * 18, x + 5, HORIZON - 30 - (k % 3) * 18], fill=(255, 250, 220))
    d.rectangle([0, HORIZON - 30, W, HORIZON], fill=(40, 20, 70))
    n = 80
    prev = None
    for j in range(n + 1):
        p = j / n
        y = HORIZON + (H - HORIZON) * p ** 1.6
        half = 30 + 760 * p ** 1.6
        cx = W / 2 + curve * 380 * (1 - p) ** 2
        z = 1 / (p ** 1.6 + 0.02)
        if prev is not None:
            py, ph, pcx = prev
            phase = z * 0.9 + t * speed * 22
            stripe = int(phase) % 2
            grass = (60, 20, 110) if stripe else (90, 30, 150)
            d.polygon([(0, py), (W, py), (W, y), (0, y)], fill=tuple(int(c * dimk) for c in grass))
            road = hsv(phase * 0.08, 0.85, 1.0)
            road = tuple(int(c * (0.55 + 0.45 * p) * dimk) for c in road)
            d.polygon([(pcx - ph, py), (pcx + ph, py), (cx + half, y), (cx - half, y)], fill=road)
            rum = WHITE if stripe else RED
            for sg in (-1, 1):
                d.polygon([(pcx + sg * ph, py), (pcx + sg * ph * 1.1, py), (cx + sg * half * 1.1, y), (cx + sg * half, y)],
                          fill=tuple(int(c * dimk) for c in rum))
            if stripe:
                d.polygon([(pcx - ph * 0.03, py), (pcx + ph * 0.03, py), (cx + half * 0.03, y), (cx - half * 0.03, y)],
                          fill=tuple(int(c * dimk) for c in WHITE))
        prev = (y, half, cx)


def car(x, y, s, t):
    """White race car, rear view."""
    d = G.draw
    b = math.sin(t * 30) * 2
    y += b
    d.ellipse([x - 190 * s, y + 40 * s, x + 190 * s, y + 80 * s], fill=(20, 10, 40))
    for sx in (-1, 1):
        d.rounded_rectangle([x + sx * 150 * s - 38 * s, y - 20 * s, x + sx * 150 * s + 38 * s, y + 60 * s], 10,
                            fill=(25, 25, 30))
    d.polygon([(x - 150 * s, y + 30 * s), (x + 150 * s, y + 30 * s), (x + 110 * s, y - 50 * s), (x - 110 * s, y - 50 * s)],
              fill=(245, 245, 250), outline=INK, width=4)
    d.polygon([(x - 70 * s, y - 50 * s), (x + 70 * s, y - 50 * s), (x + 45 * s, y - 100 * s), (x - 45 * s, y - 100 * s)],
              fill=(60, 180, 255), outline=INK, width=4)
    d.rectangle([x - 175 * s, y - 95 * s, x + 175 * s, y - 70 * s], fill=RED, outline=INK, width=4)
    for sx in (-1, 1):
        d.rectangle([x + sx * 120 * s - 6 * s, y - 70 * s, x + sx * 120 * s + 6 * s, y - 45 * s], fill=INK)
    d.ellipse([x - 32 * s, y - 38 * s, x + 32 * s, y + 18 * s], fill=RED, outline=INK, width=3)
    d.text((x, y - 10 * s), "01", font=font(BOLD, 36 * s), fill=WHITE, anchor="mm")
    for sx in (-1, 1):
        fl = 0.6 + 0.4 * math.sin(t * 40 + sx)
        d.ellipse([x + sx * 60 * s - 16 * s, y + 20 * s, x + sx * 60 * s + 16 * s, y + 20 * s + 26 * s * fl], fill=ORNG)


_chrome = {}


def chrome(t, at, xy, s, size, edge=PINK, until=None, italic=True):
    """Glossy chrome lettering with a candy outline."""
    if t < at or (until is not None and t >= until):
        return
    k = pop(t, at, 0.28)
    size = int(size * k)
    if size < 10:
        return
    fnt = ITAL if italic else BOLD
    f = font(fnt, size)
    lines = s.split("\n")
    wmax = max(f.getlength(ln) for ln in lines)
    if wmax > W - 80:
        size = int(size * (W - 80) / wmax)
        f = font(fnt, size)
    key = (s, size, edge, italic)
    if key not in _chrome:
        sw = max(4, size // 11)
        tmp = ImageDraw.Draw(Image.new("L", (1, 1)))
        bb = tmp.multiline_textbbox((0, 0), s, font=f, spacing=size // 8, stroke_width=sw, align="center")
        w, h = int(bb[2] - bb[0] + 30), int(bb[3] - bb[1] + 30)
        org = (w / 2, h / 2)
        outline = Image.new("L", (w, h), 0)
        ImageDraw.Draw(outline).multiline_text(org, s, font=f, fill=255, anchor="mm", align="center",
                                               spacing=size // 8, stroke_width=sw, stroke_fill=255)
        face = Image.new("L", (w, h), 0)
        ImageDraw.Draw(face).multiline_text(org, s, font=f, fill=255, anchor="mm", align="center", spacing=size // 8)
        ys = np.linspace(0, 1, h)[:, None]
        band = np.clip(np.stack([255 - 110 * np.abs(np.sin(ys * 6.0)) * (ys > 0.5) - 30 * ys,
                                 255 - 90 * np.abs(np.sin(ys * 6.0)) * (ys > 0.5) - 20 * ys,
                                 255 - 20 * ys + 0 * ys], -1), 0, 255)
        grad = Image.fromarray(np.broadcast_to(band, (h, w, 3)).astype(np.uint8))
        _chrome[key] = (outline, face, grad)
    outline, face, grad = _chrome[key]
    x, y = int(xy[0] - outline.width / 2), int(xy[1] - outline.height / 2)
    G.img.paste(INK, (x + 10, y + 10), outline)
    G.img.paste(edge, (x, y), outline)
    G.img.paste(grad, (x, y), face)


def hud_panel(box, col=CYAN, fill=(10, 8, 40)):
    x0, y0, x1, y1 = box
    G.draw.polygon([(x0 + 30, y0), (x1, y0), (x1, y1 - 30), (x1 - 30, y1), (x0, y1), (x0, y0 + 30)], fill=fill,
                   outline=col, width=5)


def gauge(cx, cy, r, level, label, col, t):
    d = G.draw
    d.ellipse([cx - r - 18, cy - r - 18, cx + r + 18, cy + r + 18], fill=INK, outline=col, width=6)
    for k in range(21):
        a = math.radians(150 + k * 12)
        c = hsv(0.33 - 0.33 * k / 20) if k / 20 <= level else (60, 60, 90)
        d.line([(cx + r * 0.78 * math.cos(a), cy + r * 0.78 * math.sin(a)),
                (cx + r * 0.98 * math.cos(a), cy + r * 0.98 * math.sin(a))], fill=c, width=10)
    a = math.radians(150 + 240 * level + 2 * math.sin(t * 40))
    d.line([(cx, cy), (cx + r * 0.72 * math.cos(a), cy + r * 0.72 * math.sin(a))], fill=WHITE, width=10)
    d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=col)
    d.text((cx, cy + r * 0.52), label, font=font(BOLD, int(r * 0.15)), fill=WHITE, anchor="mm")


def checkered(x0, y0, w, h, t, n=8):
    d = G.draw
    cw, ch = w / n, h / (n * 0.6)
    for i in range(n):
        for j in range(int(n * 0.6)):
            ph = math.sin(t * 8 + i * 0.7) * 14
            ph2 = math.sin(t * 8 + (i + 1) * 0.7) * 14
            pts = [(x0 + i * cw, y0 + j * ch + ph), (x0 + (i + 1) * cw, y0 + j * ch + ph2),
                   (x0 + (i + 1) * cw, y0 + (j + 1) * ch + ph2), (x0 + i * cw, y0 + (j + 1) * ch + ph)]
            d.polygon(pts, fill=INK if (i + j) % 2 else WHITE)


def caution_flag(x, y, s, t, side=1):
    d = G.draw
    d.rectangle([x - 6, y, x + 6, y + 420 * s], fill=(200, 200, 210))
    pts_top = [(x + side * u * 260 * s, y + math.sin(t * 9 + u * 5) * 20 * s) for u in np.linspace(0, 1, 12)]
    pts_bot = [(x + side * u * 260 * s, y + 170 * s + math.sin(t * 9 + u * 5) * 20 * s) for u in np.linspace(1, 0, 12)]
    d.polygon(pts_top + pts_bot, fill=YEL, outline=INK, width=4)


def wipe(t, col1=YEL, col2=PINK):
    """Speed Racer-style sweeping transition band with a helmet riding it."""
    if t >= 0.42:
        return
    k = ease_in_out(t / 0.42)
    x = W + 400 - (W + 1400) * k
    d = G.draw
    for i, c in enumerate((col2, col1, WHITE)):
        off = i * 90
        d.polygon([(x + off, 0), (x + off + 700, 0), (x + off + 400, H), (x + off - 300, H)], fill=c)
    hx, hy = x + 380, H * 0.45
    d.ellipse([hx - 170, hy - 170, hx + 170, hy + 170], fill=WHITE, outline=INK, width=8)
    d.chord([hx - 150, hy - 90, hx + 150, hy + 110], 180, 360, fill=(30, 40, 90))
    d.rectangle([hx - 170, hy + 60, hx + 170, hy + 90], fill=RED)


def subtitle(t, key):
    a = TL.active(key, t)
    if not a:
        return
    txt = "\n".join(textwrap.wrap(a[0], 30))
    f = font(ITAL, 50)
    bb = G.draw.multiline_textbbox((W / 2, 1560), txt, font=f, anchor="mm", align="center", spacing=8)
    x0, y0, x1, y1 = bb[0] - 40, bb[1] - 18, bb[2] + 40, bb[3] + 20
    G.draw.polygon([(x0 + 24, y0), (x1 + 24, y0), (x1 - 24, y1), (x0 - 24, y1)], fill=INK)
    G.draw.multiline_text((W / 2, 1560), txt, font=f, fill=WHITE, anchor="mm", align="center", spacing=8,
                          stroke_width=3, stroke_fill=PINK)


# ---------------------------------------------------------------- scenes


def s_hook(t):
    track(t, 1.3, ((20, 10, 70), (255, 60, 150)))
    car(W / 2, 1330, 1.1, t)
    chrome(t, 0.2, (W / 2, 250), "SEE IT\nCOMING", 170, PINK)
    at = ls("hook", 1)
    if t >= at:
        hud_panel((90, 470, W - 90, 690), CYAN)
        pts = []
        for i in range(200):
            u = i / 199
            v = 0.08 * math.sin(u * 60 + t * 12) + (0.9 * math.exp(-((u - 0.62) / 0.02) ** 2)) * min(1, (t - at) * 2)
            pts.append((120 + u * (W - 240), 620 - v * 110))
        G.draw.line(pts, fill=LIME, width=5)
        G.draw.text((130, 500), "SIGNAL · 0.02%", font=font(BOLD, 28), fill=CYAN, anchor="lm")
        G.draw.rectangle([120 + 0.58 * (W - 240), 505, 120 + 0.66 * (W - 240), 675], outline=PINK, width=4)
    subtitle(t, "hook")


def s_race(t):
    k = ease_in_out((t - 0.5) / (le("race", 0) - 0.5))
    track(t, 1.1, ((255, 80, 60), (255, 200, 80)), curve=math.sin(t * 0.8) * 0.8)
    wall_s = 0.2 + 0.8 * k
    wy = HORIZON + 40 + 200 * k
    ww = 200 + 700 * k
    for i in range(10):
        c = RED if i % 2 == 0 else WHITE
        G.draw.rectangle([W / 2 - ww / 2 + i * ww / 10, wy - 90 * wall_s, W / 2 - ww / 2 + (i + 1) * ww / 10, wy], fill=c,
                         outline=INK, width=3)
    car(W / 2, 1330, 1.1, t)
    hud_panel((W - 360, 160, W - 60, 460), YEL)
    G.draw.ellipse([W - 320, 200, W - 100, 420], outline=WHITE, width=10)
    a = t * 1.6
    G.draw.ellipse([W - 210 + 110 * math.cos(a) - 14, 310 + 110 * math.sin(a) - 14, W - 210 + 110 * math.cos(a) + 14,
                    310 + 110 * math.sin(a) + 14], fill=CYAN)
    wa = a + 1.2
    G.draw.polygon([(W - 210 + 110 * math.cos(wa), 310 + 110 * math.sin(wa) - 26),
                    (W - 210 + 110 * math.cos(wa) - 22, 310 + 110 * math.sin(wa) + 14),
                    (W - 210 + 110 * math.cos(wa) + 22, 310 + 110 * math.sin(wa) + 14)], fill=RED)
    G.draw.text((W - 210, 490), "SPOTTER", font=font(BOLD, 34), fill=YEL, anchor="mm")
    at = ls("race", 1)
    chrome(t, at + 0.4, (330, 330), "SYMPTOM\n= THE WALL", 70, RED)
    chrome(t, TL.phrases("race", 1, ["AI can"])[0], (330, 530), "AI\n= SPOTTER", 70, CYAN)
    wipe(t)
    subtitle(t, "race")


def s_laps(t):
    idx = max([i for i in range(6) if t >= ls("laps", i)] or [0])
    name, lead, lvl, fact, col = LAPS[idx]
    st = ls("laps", idx)
    pal = [((40, 0, 90), PINK), ((0, 40, 90), CYAN), ((80, 0, 20), RED), ((0, 60, 30), LIME), ((90, 30, 0), ORNG),
           ((30, 0, 90), PURP)][idx]
    track(t, 1.6, (pal[0], pal[1]), curve=math.sin(t * 1.3 + idx) * 0.9, dimk=0.85)
    cue("whoosh", st)
    hud_panel((60, 150, 400, 250), col)
    G.draw.text((230, 200), f"LAP {idx + 1}/6", font=font(BOLD, 48), fill=WHITE, anchor="mm")
    chrome(t, st, (W / 2, 390), name, 150, col)
    lv = lvl * ease_out_cubic((t - st - 0.3) / 1.0)
    gauge(W / 2, 800, 190, lv, lead, col, t)
    if t >= st + 0.6:
        hud_panel((80, 1040, W - 80, 1230), col)
        G.draw.multiline_text((W / 2, 1135), fact, font=font(BOLD, 36), fill=WHITE, anchor="mm", align="center", spacing=8)
    car(W / 2, 1400, 0.8, t)
    wipe(t - st + (0 if idx == 0 else 0), YEL if idx % 2 else CYAN, col)
    subtitle(t, "laps")


TRACES = [("BLOOD SUGAR", "Blood sugar", LIME), ("MEDICATIONS", "A new medication", CYAN), ("WEIGHT", "Weight", YEL),
          ("RESTING HR", "Resting heart", ORNG), ("IMAGING", "A small change", PURP)]


def s_record(t):
    G.img = Image.new("RGB", (W, H), (8, 6, 30))
    G.draw = d = ImageDraw.Draw(G.img)
    for x in range(0, W, 60):
        d.line([(x, 0), (x, H)], fill=(20, 16, 60), width=1)
    for y in range(0, H, 60):
        d.line([(0, y), (W, y)], fill=(20, 16, 60), width=1)
    chrome(t, 0.2, (W / 2, 190), "10-YEAR\nTELEMETRY", 90, PINK)
    x0, x1 = 300, W - 70
    prog = ease_in_out((t - ls("record", 0) - 0.4) / (le("record", 1) - ls("record", 0)))
    ts = TL.phrases("record", 1, [p for _, p, _ in TRACES])
    for i, ((lab, _, col), at) in enumerate(zip(TRACES, ts)):
        y0 = 370 + i * 175
        d.rectangle([x0, y0 + 30, x1, y0 + 130], fill=(18, 40, 30))
        d.text((x0 - 20, y0 + 80), lab, font=font(BOLD, 28), fill=col if t >= at else (90, 90, 120), anchor="rm")
        n = int(120 * prog)
        pts = []
        for j in range(n + 1):
            u = j / 120
            if i == 1:
                v = 0.3 if u < 0.55 else 0.65
            elif i == 4:
                v = 0.4 + (0.2 if u > 0.85 else 0.0)
            else:
                v = 0.25 + 0.45 * u ** (1.3 + i * 0.2) + 0.04 * math.sin(u * 40 + i)
            pts.append((x0 + u * (x1 - x0), y0 + 130 - v * 100))
        if len(pts) > 1:
            d.line(pts, fill=col, width=5)
        if t >= at:
            G.draw.text((x1 - 10, y0 + 45), "NORMAL", font=font(BOLD, 20), fill=(120, 220, 160), anchor="rm")
    for k, yr in enumerate(range(2015, 2026, 2)):
        d.text((x0 + (x1 - x0) * k / 5, 1250), str(yr), font=font(BOLD, 24), fill=(150, 150, 190), anchor="mm")
    at = ls("record", 2)
    if t >= at:
        k = ease_out_cubic((t - at) / 1.6)
        pts = [(x0 + u * (x1 - x0), 1180 - 780 * (u ** 3.2)) for u in np.linspace(0, k, 80)]
        d.line([(x0, 420), (x1, 420)], fill=RED, width=4)
        d.text((x0 + 10, 400), "RISK THRESHOLD", font=font(BOLD, 24), fill=RED, anchor="lm")
        if len(pts) > 1:
            d.line(pts, fill=PINK, width=14)
        chrome(t, TL.phrases("record", 2, ["Together"])[0], (W / 2 + 60, 1330), "COMBINED RISK", 64, PINK)
    at3 = ls("record", 3)
    if t >= at3:
        checkered(0, 520, W, 360, t, 10)
        chrome(t, at3 + 0.2, (W / 2, 700), "EVALUATE\nNOW", 150, RED)
        cue("boom", at3 + 0.2)
    subtitle(t, "record")


def s_why(t):
    track(t, 0.8, ((10, 0, 60), (80, 0, 120)), dimk=0.55, loops=False)
    chrome(t, 0.2, (W / 2, 210), "TIMING IS\nEVERYTHING", 110, YEL)
    G.draw.text((W / 2, 400), "COLON CANCER · 5-YEAR SURVIVAL", font=font(BOLD, 34), fill=WHITE, anchor="mm")
    p1, p2 = TL.phrases("why", 0, ["Caught early", "Caught late"])
    for x, lab, val, col, at in ((300, "CAUGHT\nEARLY", 0.90, LIME, p1), (780, "CAUGHT\nLATE", 0.15, RED, p2)):
        cue("boom", at)
        if t < at:
            continue
        k = ease_out_cubic((t - at) / 0.9)
        top = 1250 - 700 * val * k
        G.draw.rectangle([x - 130, 550, x + 130, 1250], fill=(30, 20, 60), outline=WHITE, width=4)
        G.draw.rectangle([x - 124, top, x + 124, 1246], fill=col)
        chrome(t, at + 0.5, (x, min(top - 80, 1100)), f"~{int(round(val * 100 * k))}%", 110, col)
        G.draw.multiline_text((x, 1330), lab, font=font(BOLD, 40), fill=WHITE, anchor="mm", align="center")
    G.draw.text((W / 2, 1440), "localized vs. distant stage · U.S. data", font=font(ITAL, 30), fill=(200, 200, 230),
                anchor="mm")
    wipe(t)
    subtitle(t, "why")


def s_flags(t):
    track(t, 0.6, ((60, 50, 0), (200, 150, 0)), dimk=0.6, loops=False)
    caution_flag(110, 330, 1.0, t, 1)
    caution_flag(W - 110, 330, 1.0, t, -1)
    chrome(t, 0.2, (W / 2, 220), "A FLAG ≠\nA DIAGNOSIS", 110, YEL)
    items = [("FALSE ALARMS → ALERT FATIGUE", "Too many"), ("TESTED", "tested"), ("FAIR", "fair"), ("PRIVATE", "private")]
    ts = TL.phrases("flags", 1, [p for _, p in items])
    for i, ((lab, _), at) in enumerate(zip(items, ts)):
        cue("pop", at)
        if t < at:
            continue
        y = 720 + i * 160
        k = ease_out_back((t - at) / 0.3)
        hud_panel((W / 2 - 420 * k, y - 60, W / 2 + 420 * k, y + 60), RED if i == 0 else LIME)
        if k > 0.8:
            G.draw.text((W / 2, y), ("⚠  " if i == 0 else "✓  ") + lab, font=font(BOLD, 44 if i else 38),
                        fill=WHITE, anchor="mm")
    wipe(t)
    subtitle(t, "flags")


def s_outro(t):
    track(t, 1.8, ((255, 60, 170), (80, 220, 255)), curve=math.sin(t) * 0.6)
    car(W / 2, 1330, 1.1, t)
    at = ls("outro", 0)
    chrome(t, at + 0.2, (W / 2, 250), "REACTIVE", 120, (120, 120, 140), until=TL.phrases("outro", 0, ["to preventive"])[0] + 0.3)
    p = TL.phrases("outro", 0, ["to preventive"])[0]
    if at + 1.0 <= t < p + 0.3:
        G.draw.line([(180, 250), (180 + 720 * ease_out_cubic((t - at - 1.0) / 0.3), 250)], fill=RED, width=20)
    chrome(t, p + 0.3, (W / 2, 260), "PREVENTIVE", 150, LIME)
    chrome(t, ls("outro", 1) + 0.1, (W / 2, 520), "READ THE\nROAD", 140, PINK)
    if t >= le("outro", 1):
        checkered(0, 0, W, 130, t, 12)
    subtitle(t, "outro")


SCENE_FNS = {"hook": s_hook, "race": s_race, "laps": s_laps, "record": s_record, "why": s_why, "flags": s_flags,
             "outro": s_outro}
SCENES = [(TL.dur[k], SCENE_FNS[k]) for k, *_ in SCRIPT]
TOTAL = TL.total

# ---------------------------------------------------------------- score: brassy racing theme + engine

SR = E.SR


def _tt(d):
    return np.arange(int(d * SR)) / SR


def extra_sfx(sr):
    x = _tt(0.7)
    f = 300 * np.exp(-x * 2) + 80
    zoom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * x / 0.7) ** 2
    zoom += 0.3 * np.random.default_rng(1).standard_normal(len(x)) * np.sin(np.pi * x / 0.7) ** 2
    x2 = _tt(0.1)
    zip_ = np.sin(2 * np.pi * np.cumsum(800 + 3000 * x2 / 0.1) / SR) * np.sin(np.pi * x2 / 0.1)
    return {"whoosh": (zoom, 0.35), "pop": (zip_, 0.2)}


def music_fn(n):
    out = np.zeros(n)
    rng = np.random.default_rng(8)

    def add(sig, t, g):
        i = int(t * SR)
        if i < n:
            j = min(n, i + len(sig))
            out[i:j] += sig[: j - i] * g

    def brass(f, d):
        x = _tt(d)
        y = sum(np.sin(2 * np.pi * f * k * x) / k ** 0.9 for k in range(1, 10))
        return y * np.minimum(1, x / 0.03) * np.exp(-x * 2.5)

    x = _tt(0.3)
    kick = np.sin(2 * np.pi * np.cumsum(50 + 110 * np.exp(-x * 30)) / SR) * np.exp(-x * 9)
    x = _tt(0.18)
    snare = rng.standard_normal(len(x)) * np.exp(-x * 20) * 0.5 + np.sin(2 * np.pi * 200 * x) * np.exp(-x * 30) * 0.4
    x = _tt(0.04)
    hat = np.diff(rng.standard_normal(len(x) + 1)) * np.exp(-x * 90)
    beat = 60 / 152
    prog = [(98.0, [392.0, 493.88, 587.33]), (110.0, [440.0, 523.25, 659.25]), (87.31, [349.23, 440.0, 523.25]),
            (98.0, [392.0, 493.88, 587.33])]
    riff = [0, 0.75, 1.5, 2.5, 3.0]
    t, bar = 0.0, 0
    total = E.TOTAL
    while t < total:
        root, ch = prog[bar % 4]
        for b in range(4):
            tb = t + b * beat
            add(kick, tb, 0.8)
            if b % 2:
                add(snare, tb, 0.55)
            for h in (0, 0.5):
                add(hat, tb + h * beat, 0.15)
                xb = _tt(beat * 0.45)
                f = root * (2 if h else 1)
                add(np.sign(np.sin(2 * np.pi * f * xb)) * np.exp(-xb * 5) * 0.5, tb + h * beat, 0.18)
        for r in riff:
            for f in ch:
                add(brass(f, 0.35), t + r * beat, 0.045)
        t += 4 * beat
        bar += 1
    x = np.arange(n) / SR   # engine: a low sawtooth that revs with the music
    rev = 55 + 12 * np.sin(2 * np.pi * x / (16 * beat)) ** 2
    eng = 2 * ((np.cumsum(rev) / SR) % 1) - 1
    out += np.convolve(eng, np.ones(40) / 40, mode="same") * 0.06
    voice = TL.track(n, SR)
    out = narrate.duck(out, voice, SR, depth=0.6)
    fade = int(1.5 * SR)
    end = int(total * SR)
    out[end - fade:end] *= np.linspace(1, 0, fade)
    out[end:] = 0
    return out * 0.6 + voice * 1.7


E.SCENE_CUT_FLASH = False

if __name__ == "__main__":
    print(f"total {TOTAL:.1f}s; " + ", ".join(f"{k} {TL.dur[k]:.1f}" for k, *_ in SCRIPT))
    E.main("see_it_coming.mp4", SCENES, music_fn, extra_sfx)

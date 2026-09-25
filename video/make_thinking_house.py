#!/usr/bin/env python3
"""Render "THE THINKING HOUSE": a <2 min vertical short on AI as an intellectual amplifier,
styled after the painted, psychedelic, collage look of 1970s Japanese horror-fantasy cinema
(House, 1977): sunset matte skies, a haunted house, a white cat, floating eyes, iris wipes,
film grain. Narrated with the Kokoro neural TTS (female voice "af_bella").

    pip install pillow numpy imageio-ffmpeg sherpa-onnx
    python3 make_thinking_house.py                 # -> out/the_thinking_house.mp4
    python3 make_thinking_house.py --preview 3 17  # frames -> out/preview/the_thinking_house/

The Kokoro model (Apache-2.0) is fetched once from the npm package n8n-nodes-ttsbro,
which bundles the sherpa-onnx export, into video/.models/.
"""
import hashlib
import math
import os
import subprocess
import tarfile
import textwrap

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import make_video as E
from make_video import BLACK, FONT_MATH, G, H, W, cue, ease_in_out, ease_out_back, ease_out_cubic, fit_size, font, pop, stroke_for, text

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_SERIF = "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"
FONT_SERIF_I = "/usr/share/fonts/truetype/freefont/FreeSerifBoldItalic.ttf"
FONT_FAT = FONT_MATH  # DejaVu Sans Bold: fat 70s letterforms

TANG = (255, 140, 50)
PINK = (255, 105, 170)
LILAC = (185, 150, 255)
MINT = (130, 235, 195)
CREAM = (255, 244, 214)
YEL = (255, 222, 80)
RED = (215, 40, 55)
TEAL = (40, 170, 170)
INK = (30, 12, 40)

# ---------------------------------------------------------------- narration

SCRIPT = [  # (scene, lead-in seconds, lines, tail seconds)
    ("hook", 1.3, ["Welcome to the thinking house.",
                   "Where your mind gets a few more rooms."], 0.7),
    ("idea", 0.5, ["One of AI's most important uses isn't answering questions for you.",
                   "It's amplifying how you think.",
                   "Glasses extend your eyes. A bicycle extends your legs. AI can extend the reach of your mind."], 0.5),
    ("room1", 0.4, ["Room one. Understand.",
                    "Explain an unfamiliar subject. Summarize a dense report. Translate jargon into plain language."], 0.4),
    ("room2", 0.4, ["Room two. Explore.",
                    "Brainstorm possibilities. Generate hypotheses. Play out the consequences of a decision."], 0.4),
    ("room3", 0.4, ["Room three. Challenge.",
                    "Critique your argument. Find the inconsistencies. Simulate the other side. "
                    "Surface the questions you forgot to ask."], 0.4),
    ("room4", 0.4, ["Room four. Organize.",
                    "Untangle messy thoughts. Compare competing ideas. Turn a vague idea into a real plan."], 0.5),
    ("example", 0.4, ["Picture a researcher with fifty reports and three hours.",
                      "Without AI, three hours of searching, and almost no time left to think.",
                      "With AI, minutes to find the relevant sections, and three full hours to interpret the evidence."], 0.6),
    ("reach", 0.4, ["The benefit isn't just speed.",
                    "It's reach. You think about more, and you think deeper."], 0.6),
    ("rules", 0.4, ["But every house has rules.",
                    "One. Verify. AI can sound confident and still be wrong. Check the sources.",
                    "Two. Think first. Write down your own take before you ask.",
                    "Three. Make it argue with you, not just agree.",
                    "Four. The final judgment stays yours."], 0.5),
    ("outro", 0.4, ["AI doesn't replace your thinking.",
                    "It gives your thinking more room."], 2.6),
]
VOICE_SID = 1        # Kokoro v0.19 speaker 1 = af_bella (American English, female)
VOICE_SPEED = 1.1
GAP = 0.28
VSR = 24000
MODEL_DIR = os.path.join(HERE, ".models", "kokoro-int8-en-v0_19")
VOICE_CACHE = os.path.join(E.OUT_DIR, "_voice")


def ensure_model():
    if os.path.exists(os.path.join(MODEL_DIR, "model.int8.onnx")):
        return
    os.makedirs(os.path.dirname(MODEL_DIR), exist_ok=True)
    tgz = os.path.join(os.path.dirname(MODEL_DIR), "ttsbro.tgz")
    url = "https://registry.npmjs.org/n8n-nodes-ttsbro/-/n8n-nodes-ttsbro-0.1.6.tgz"
    subprocess.run(["curl", "-sSfL", "-o", tgz, url], check=True)
    prefix = "package/kokoro-int8-en-v0_19/"
    with tarfile.open(tgz) as tf:
        for m in tf.getmembers():
            if m.name.startswith(prefix) and m.isfile():
                m.name = os.path.join("kokoro-int8-en-v0_19", m.name[len(prefix):])
                tf.extract(m, os.path.dirname(MODEL_DIR))
    os.remove(tgz)


_tts = None


def speak(line):
    global _tts
    key = hashlib.sha1(f"{VOICE_SID}|{VOICE_SPEED}|{line}".encode()).hexdigest()[:16]
    path = os.path.join(VOICE_CACHE, key + ".npy")
    if os.path.exists(path):
        return np.load(path)
    if _tts is None:
        import sherpa_onnx
        ensure_model()
        d = MODEL_DIR + "/"
        _tts = sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
            kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=d + "model.int8.onnx", voices=d + "voices.bin",
                                                           tokens=d + "tokens.txt", data_dir=d + "espeak-ng-data"),
            num_threads=4)))
    a = np.array(_tts.generate(line, sid=VOICE_SID, speed=VOICE_SPEED).samples, dtype=np.float32)
    loud = np.where(np.abs(a) > 0.02)[0]
    if len(loud):
        a = a[max(0, loud[0] - 600): loud[-1] + 2400]
    os.makedirs(VOICE_CACHE, exist_ok=True)
    np.save(path, a)
    return a


LT, DUR, VO = {}, {}, []   # scene -> [(start, dur, text)], scene -> seconds, [(global_start, samples)]
_tg = 0.0
for _key, _pin, _lines, _pout in SCRIPT:
    _t, _lst = _pin, []
    for _ln in _lines:
        _a = speak(_ln)
        _d = len(_a) / VSR
        _lst.append((_t, _d, _ln))
        VO.append((_tg + _t, _a))
        _t += _d + GAP
    LT[_key], DUR[_key] = _lst, _t - GAP + _pout
    _tg += DUR[_key]


def ls(key, i):
    return LT[key][i][0]


def le(key, i):
    return LT[key][i][0] + LT[key][i][1]


def phrase_times(key, i, parts):
    """Approximate start times of the sentences/phrases inside line i."""
    st, d, s = LT[key][i]
    out, pos = [], 0
    for p in parts:
        k = s.find(p, pos)
        out.append(st + d * max(0, k) / len(s))
        pos = max(pos, k)
    return out


# ---------------------------------------------------------------- painted backdrops

_cache = {}


def gradient_stops(stops):
    ys = np.linspace(0, 1, H)
    pos = np.linspace(0, 1, len(stops))
    arr = np.stack([np.interp(ys, pos, [c[i] for c in stops]) for i in range(3)], -1)
    return np.broadcast_to(arr[:, None, :], (H, W, 3)).copy()


def sky(name):
    if name in _cache:
        return _cache[name]
    stops = {"sunset": [(44, 14, 84), (150, 30, 120), (250, 90, 110), (255, 170, 90), (255, 214, 130)],
             "dusk": [(18, 10, 50), (70, 20, 100), (190, 60, 130), (255, 130, 110)]}[name]
    arr = gradient_stops(stops)
    img = Image.fromarray(arr.astype(np.uint8))
    d = ImageDraw.Draw(img)
    sx, sy, r = W / 2, 980, 330   # striped 70s sun
    d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 205, 90))
    for k in range(7):
        y = sy + 40 + k * 44
        d.rectangle([sx - r, y, sx + r, y + 8 + k * 3], fill=tuple(arr[int(y), 0].astype(int)))
    clouds = Image.new("L", (W, H), 0)
    cd = ImageDraw.Draw(clouds)
    rng = np.random.default_rng(4)
    for _ in range(14):
        cx, cy = rng.uniform(-100, W + 100), rng.uniform(150, 800)
        for _ in range(5):
            dx, dy, rr = rng.uniform(-120, 120), rng.uniform(-25, 25), rng.uniform(40, 90)
            cd.ellipse([cx + dx - rr * 1.8, cy + dy - rr * 0.6, cx + dx + rr * 1.8, cy + dy + rr * 0.6], fill=150)
    img.paste((255, 190, 200), mask=clouds.filter(ImageFilter.GaussianBlur(14)))
    _cache[name] = img
    return img


def wallpaper(name):
    if name in _cache:
        return _cache[name]
    c1, c2, pat = {"dots": ((255, 150, 80), (255, 110, 160), "dots"),
                   "waves": ((70, 30, 110), (130, 60, 170), "waves"),
                   "rings": ((20, 90, 100), (35, 130, 130), "rings"),
                   "split": ((255, 110, 160), (120, 110, 255), "split"),
                   "lilac": ((120, 90, 190), (160, 120, 220), "dots"),
                   "mint": ((30, 110, 90), (50, 150, 120), "waves")}[name]
    Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
    if pat == "dots":
        m = (((X % 90) - 45) ** 2 + ((Y + (X // 90 % 2) * 45) % 90 - 45) ** 2) < 16 ** 2
    elif pat == "waves":
        m = np.sin((X + 40 * np.sin(Y / 60)) / 34) > 0
    elif pat == "rings":
        m = np.sin(np.sqrt((X - W / 2) ** 2 + (Y - 800) ** 2) / 22) > 0
    else:
        m = X > (W / 2 + (Y - H / 2) * 0.25)
    arr = np.where(m[..., None], np.array(c2, np.float32), np.array(c1, np.float32))
    img = Image.fromarray(arr.astype(np.uint8))
    _cache[name] = img
    return img


def backdrop(img):
    G.img = img.copy()
    G.draw = ImageDraw.Draw(G.img)


def shade(alpha, box=None):
    """Darken (part of) the frame to lift foreground text."""
    box = box or (0, 0, W, H)
    box = tuple(int(v) for v in box)
    G.img.paste((12, 6, 20), box, Image.new("L", (box[2] - box[0], box[3] - box[1]), alpha))


# ---------------------------------------------------------------- typography


def retro(t, at, xy, s, size, main=CREAM, layers=(LILAC, PINK, TANG), until=None):
    """Fat 70s title with stacked offset colour layers."""
    if t < at or (until is not None and t >= until):
        return
    size = fit_size(s, size, FONT_FAT) * pop(t, at, 0.35)
    if size < 8:
        return
    off = max(3, size * 0.05)
    f = font(FONT_FAT, size)
    kw = dict(font=f, anchor="mm", align="center", spacing=int(size * 0.12), stroke_width=max(2, int(size * 0.05)),
              stroke_fill=INK)
    for n, c in reversed(list(enumerate(layers, 1))):
        G.draw.multiline_text((xy[0] + off * n, xy[1] + off * n), s, fill=c, **kw)
    G.draw.multiline_text(xy, s, fill=main, **kw)


def serif(t, at, xy, s, size, col=CREAM, until=None, fnt=FONT_SERIF_I):
    if t < at or (until is not None and t >= until):
        return
    size = fit_size(s, size, fnt)
    text(xy, s, size * pop(t, at), col, fnt)


_labels = {}


def cutout(t, at, xy, s, angle, paper=CREAM, size=50, until=None, sound=True):
    """Collage label: a scrap of paper with type on it, glued on at an angle."""
    if sound:
        cue("pop", at)
    if t < at or (until is not None and t >= until):
        return
    key = (s, angle, paper, size)
    if key not in _labels:
        f = font(FONT_SERIF, size)
        tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        bb = tmp.multiline_textbbox((0, 0), s, font=f, spacing=6)
        w, h = bb[2] - bb[0] + 60, bb[3] - bb[1] + 44
        lay = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        d.rectangle([12, 12, w + 12, h + 12], fill=(0, 0, 0, 150))
        jag = [(0, 4), (w * 0.3, 0), (w * 0.62, 5), (w, 1), (w - 3, h * 0.5), (w, h), (w * 0.55, h - 4), (w * 0.2, h),
               (2, h - 2), (5, h * 0.45)]
        d.polygon(jag, fill=paper + (255,), outline=INK + (255,))
        d.multiline_text((w / 2, h / 2), s, font=f, fill=INK, anchor="mm", align="center", spacing=6)
        _labels[key] = lay.rotate(angle, expand=True, resample=Image.BICUBIC)
    lay = _labels[key]
    k = pop(t, at, 0.3)
    if k <= 0.05:
        return
    if abs(k - 1) > 0.01:
        lay = lay.resize((max(1, int(lay.width * k)), max(1, int(lay.height * k))))
    G.img.paste(lay, (int(xy[0] - lay.width / 2), int(xy[1] - lay.height / 2)), lay)


def subtitle(t, key):
    for st, d, s in LT[key]:
        if st <= t < st + d + 0.2:
            txt = "\n".join(textwrap.wrap(s, 30))
            f = font(FONT_SERIF, 52)
            bb = G.draw.multiline_textbbox((W / 2, 1520), txt, font=f, anchor="mm", align="center", spacing=8)
            shade(165, (bb[0] - 28, bb[1] - 18, bb[2] + 28, bb[3] + 20))
            G.draw.multiline_text((W / 2, 1520), txt, font=f, fill=YEL, anchor="mm", align="center", spacing=8,
                                  stroke_width=3, stroke_fill=BLACK)
            return


# ---------------------------------------------------------------- props


def house(cx, base, t, lit=3, extra=0.0):
    """Silhouette house on a hill; `extra` (0..1) grows new rooms onto it."""
    d = G.draw
    d.ellipse([cx - 900, base - 60, cx + 900, base + 700], fill=(40, 12, 50))
    sil = (26, 8, 34)
    wins = []
    if extra > 0:
        for (x0, x1, top, delay) in ((cx - 330, cx - 170, base - 210, 0.0), (cx + 170, cx + 330, base - 250, 0.25),
                                     (cx - 70, cx + 70, base - 560, 0.5)):
            k = ease_out_back(min(1, max(0, (extra - delay) / 0.5)))
            if k <= 0:
                continue
            hgt = (base - top) * k if top > base - 400 else 110 * k
            yb = base if top > base - 400 else base - 450
            d.rectangle([x0, yb - hgt, x1, yb], fill=sil)
            d.polygon([(x0 - 14, yb - hgt), ((x0 + x1) / 2, yb - hgt - 70 * k), (x1 + 14, yb - hgt)], fill=sil)
            wins.append(((x0 + x1) / 2 - 22, yb - hgt * 0.62, 44, 50))
    d.rectangle([cx - 170, base - 300, cx + 170, base], fill=sil)
    d.polygon([(cx - 200, base - 300), (cx, base - 450), (cx + 200, base - 300)], fill=sil)
    d.rectangle([cx + 70, base - 470, cx + 110, base - 360], fill=sil)
    d.rectangle([cx - 130, base - 420, cx - 60, base - 250], fill=sil)
    d.polygon([(cx - 145, base - 420), (cx - 95, base - 520), (cx - 45, base - 420)], fill=sil)
    base_wins = [(cx - 115, base - 380, 40, 50), (cx - 110, base - 220, 50, 60), (cx + 40, base - 220, 50, 60),
                 (cx - 25, base - 110, 50, 110), (cx + 100, base - 110, 44, 56)]
    for i, (x, y, w, h) in enumerate(base_wins[:lit] + wins):
        fl = 0.85 + 0.15 * math.sin(t * 7 + i * 2.1)
        c = (int(255 * fl), int(215 * fl), int(90 * fl))
        d.rectangle([x - 6, y - 6, x + w + 6, y + h + 6], fill=(120, 60, 40))
        d.rectangle([x, y, x + w, y + h], fill=c)
        d.line([(x + w / 2, y), (x + w / 2, y + h)], fill=sil, width=4)


def cat(x, y, s, t):
    """The white cat. Always watching."""
    d = G.draw
    wv = math.sin(t * 2.2) * 18 * s
    d.line([(x + 40 * s, y + 70 * s), (x + 110 * s, y + 40 * s + wv), (x + 120 * s, y - 30 * s + wv)],
           fill=WHITE_C, width=int(18 * s), joint="curve")
    d.ellipse([x - 60 * s, y - 20 * s, x + 60 * s, y + 90 * s], fill=WHITE_C, outline=INK, width=4)
    d.ellipse([x - 48 * s, y - 100 * s, x + 48 * s, y - 10 * s], fill=WHITE_C, outline=INK, width=4)
    for sgn in (-1, 1):
        d.polygon([(x + sgn * 44 * s, y - 70 * s), (x + sgn * 40 * s, y - 128 * s), (x + sgn * 12 * s, y - 96 * s)],
                  fill=WHITE_C, outline=INK, width=3)
        ex = x + sgn * 20 * s
        blink = (t % 4.1) < 0.12
        if blink:
            d.line([(ex - 12 * s, y - 58 * s), (ex + 12 * s, y - 58 * s)], fill=INK, width=4)
        else:
            d.ellipse([ex - 14 * s, y - 70 * s, ex + 14 * s, y - 46 * s], fill=(80, 255, 140), outline=INK, width=2)
            d.ellipse([ex - 3 * s, y - 68 * s, ex + 3 * s, y - 48 * s], fill=INK)
    d.polygon([(x - 6 * s, y - 42 * s), (x + 6 * s, y - 42 * s), (x, y - 35 * s)], fill=PINK)


WHITE_C = (250, 248, 240)


def eye(cx, cy, w, t, iris=(60, 160, 255), openness=1.0):
    h = w * 0.34 * openness
    lay = Image.new("RGBA", (int(w + 40), int(w * 0.8 + 40)), (0, 0, 0, 0))
    ox, oy = 20 + w / 2, lay.height / 2
    top = [(ox - w / 2 + w * u / 30, oy - h * math.sin(math.pi * u / 30)) for u in range(31)]
    bot = [(ox - w / 2 + w * u / 30, oy + h * math.sin(math.pi * u / 30)) for u in range(30, -1, -1)]
    mask = Image.new("L", lay.size, 0)
    ImageDraw.Draw(mask).polygon(top + bot, fill=255)
    inner = Image.new("RGBA", lay.size, WHITE_C + (255,))
    di = ImageDraw.Draw(inner)
    lx = ox + math.sin(t * 1.3) * w * 0.14
    r = w * 0.19
    di.ellipse([lx - r, oy - r, lx + r, oy + r], fill=iris + (255,), outline=INK + (255,), width=5)
    di.ellipse([lx - r * 0.45, oy - r * 0.45, lx + r * 0.45, oy + r * 0.45], fill=INK + (255,))
    di.ellipse([lx + r * 0.2, oy - r * 0.6, lx + r * 0.5, oy - r * 0.3], fill=(255, 255, 255, 255))
    lay.paste(inner, (0, 0), mask)
    d = ImageDraw.Draw(lay)
    d.line(top, fill=INK + (255,), width=9, joint="curve")
    d.line(bot, fill=INK + (255,), width=6, joint="curve")
    for u in range(4, 27, 4):
        x, y = top[u]
        d.line([(x, y), (x + (u - 15) * 2.2, y - 34)], fill=INK + (255,), width=6)
    G.img.paste(lay, (int(cx - ox), int(cy - oy)), lay)


def petals(cx, cy, t):
    d = G.draw
    for layer, (R, n, col, sp) in enumerate(((330, 12, PINK, 0.5), (240, 10, YEL, -0.8), (150, 8, MINT, 1.1),
                                              (70, 6, LILAC, -1.4))):
        for k in range(n):
            a = t * sp + k * 2 * math.pi / n
            pts = []
            for u in range(16):
                q = u / 15 * math.pi
                px, py = R * 0.5 * (1 - math.cos(q)), R * 0.18 * math.sin(q)
                pts.append((cx + px * math.cos(a) - py * math.sin(a), cy + px * math.sin(a) + py * math.cos(a)))
            for u in range(15, -1, -1):
                q = u / 15 * math.pi
                px, py = R * 0.5 * (1 - math.cos(q)), -R * 0.18 * math.sin(q)
                pts.append((cx + px * math.cos(a) - py * math.sin(a), cy + px * math.sin(a) + py * math.cos(a)))
            d.polygon(pts, fill=col, outline=INK, width=4)
    d.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], fill=TANG, outline=INK, width=5)


def bubble(x, y, s, col, tail=1):
    f = font(FONT_SERIF_I, 58)
    bb = G.draw.textbbox((x, y), s, font=f, anchor="mm")
    r = [bb[0] - 40, bb[1] - 34, bb[2] + 40, bb[3] + 34]
    G.draw.polygon([(x - 30 * tail, r[3] - 4), (x - 90 * tail, r[3] + 60), (x + 20 * tail, r[3] - 4)], fill=col,
                   outline=INK, width=5)
    G.draw.rounded_rectangle(r, 40, fill=col, outline=INK, width=6)
    G.draw.text((x, y), s, font=f, fill=INK, anchor="mm")


def keys(y, t, pressed):
    d = G.draw
    n, kw = 14, W / 14
    for i in range(n):
        down = 10 if i == pressed else 0
        d.rectangle([i * kw + 2, y + down, (i + 1) * kw - 2, y + 180 + down], fill=WHITE_C, outline=INK, width=4)
    for i in range(n - 1):
        if i % 7 in (2, 6):
            continue
        d.rectangle([(i + 1) * kw - kw * 0.3, y, (i + 1) * kw + kw * 0.3, y + 110], fill=INK)


def glasses(cx, cy, s, col):
    d = G.draw
    for sx in (-1, 1):
        d.ellipse([cx + sx * 70 * s - 60 * s, cy - 50 * s, cx + sx * 70 * s + 60 * s, cy + 50 * s], outline=col,
                  width=int(12 * s))
    d.arc([cx - 24 * s, cy - 30 * s, cx + 24 * s, cy + 10 * s], 200, 340, fill=col, width=int(10 * s))
    d.line([(cx - 130 * s, cy - 10 * s), (cx - 170 * s, cy - 30 * s)], fill=col, width=int(10 * s))
    d.line([(cx + 130 * s, cy - 10 * s), (cx + 170 * s, cy - 30 * s)], fill=col, width=int(10 * s))


def bicycle(cx, cy, s, col, t):
    d = G.draw
    lw = int(10 * s)
    for sx in (-1, 1):
        wx = cx + sx * 95 * s
        d.ellipse([wx - 62 * s, cy - 62 * s + 30 * s, wx + 62 * s, cy + 62 * s + 30 * s], outline=col, width=lw)
        a = t * 5
        d.line([(wx, cy + 30 * s), (wx + 55 * s * math.cos(a), cy + 30 * s + 55 * s * math.sin(a))], fill=col, width=4)
    pts = [(cx - 95 * s, cy + 30 * s), (cx - 10 * s, cy - 50 * s), (cx + 70 * s, cy - 50 * s), (cx + 95 * s, cy + 30 * s)]
    d.line(pts, fill=col, width=lw, joint="curve")
    d.line([(cx - 95 * s, cy + 30 * s), (cx + 10 * s, cy + 30 * s), (cx - 10 * s, cy - 50 * s)], fill=col, width=lw)
    d.line([(cx + 10 * s, cy + 30 * s), (cx + 70 * s, cy - 50 * s)], fill=col, width=lw)
    d.line([(cx - 30 * s, cy - 68 * s), (cx + 5 * s, cy - 68 * s)], fill=col, width=lw)
    d.line([(cx + 70 * s, cy - 50 * s), (cx + 60 * s, cy - 85 * s), (cx + 90 * s, cy - 90 * s)], fill=col, width=lw)


def mind(cx, cy, s, col, t):
    """A head with a little house for a brain."""
    d = G.draw
    d.ellipse([cx - 95 * s, cy - 110 * s, cx + 95 * s, cy + 80 * s], outline=col, width=int(10 * s))
    d.polygon([(cx - 40 * s, cy + 70 * s), (cx + 40 * s, cy + 70 * s), (cx + 30 * s, cy + 120 * s),
               (cx - 30 * s, cy + 120 * s)], outline=col, width=int(8 * s))
    d.rectangle([cx - 40 * s, cy - 30 * s, cx + 40 * s, cy + 30 * s], fill=col)
    d.polygon([(cx - 55 * s, cy - 30 * s), (cx, cy - 75 * s), (cx + 55 * s, cy - 30 * s)], fill=col)
    fl = 0.8 + 0.2 * math.sin(t * 8)
    d.rectangle([cx - 14 * s, cy - 10 * s, cx + 14 * s, cy + 18 * s], fill=(255, int(215 * fl), 90))
    for k in range(8):
        a = t * 0.9 + k * math.pi / 4
        r0, r1 = 125 * s, (150 + 12 * math.sin(t * 6 + k)) * s
        d.line([(cx + r0 * math.cos(a), cy - 15 * s + r0 * math.sin(a)),
                (cx + r1 * math.cos(a), cy - 15 * s + r1 * math.sin(a))], fill=col, width=int(8 * s))


def knob(cx, cy, r, level, t):
    d = G.draw
    d.ellipse([cx - r - 14, cy - r - 14, cx + r + 14, cy + r + 14], fill=INK)
    for k in range(11):
        a = math.radians(135 + k * 27)
        c = TANG if k / 10 <= level else (90, 70, 100)
        d.line([(cx + (r + 30) * math.cos(a), cy + (r + 30) * math.sin(a)),
                (cx + (r + 70) * math.cos(a), cy + (r + 70) * math.sin(a))], fill=c, width=14)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(200, 200, 210), outline=INK, width=8)
    a = math.radians(135 + 270 * level)
    d.line([(cx, cy), (cx + r * 0.85 * math.cos(a), cy + r * 0.85 * math.sin(a))], fill=RED, width=16)
    text((cx, cy + r + 115), "11" if level > 0.97 else f"{int(level * 10)}", 64, YEL, FONT_FAT)


def paper(x, y, ang, s=1.0):
    ca, sa = math.cos(ang), math.sin(ang)
    pts = [(x + (px * ca - py * sa) * s, y + (px * sa + py * ca) * s) for px, py in ((-45, -60), (45, -60), (45, 60),
                                                                                    (-45, 60))]
    G.draw.polygon(pts, fill=WHITE_C, outline=INK, width=3)
    for k in range(4):
        py = -35 + k * 20
        a, b = (-30, py), (30, py)
        G.draw.line([(x + (a[0] * ca - a[1] * sa) * s, y + (a[0] * sa + a[1] * ca) * s),
                     (x + (b[0] * ca - b[1] * sa) * s, y + (b[0] * sa + b[1] * ca) * s)], fill=(150, 150, 170), width=3)


# ---------------------------------------------------------------- scenes


def s_hook(t):
    backdrop(sky("sunset"))
    grow = ease_in_out((t - ls("hook", 1) - 0.9) / 1.2)
    house(W / 2, 1270, t, lit=3 + int(min(2, t / 0.6)), extra=grow)
    cat(860, 1225, 0.9, t)
    retro(t, 0.35, (W / 2, 330), "THE THINKING\nHOUSE", 132)
    serif(t, 1.3, (W / 2, 535), "a short film about extending your mind", 44, CREAM)
    subtitle(t, "hook")


def s_idea(t):
    backdrop(wallpaper("dots"))
    shade(110)
    cutout(t, ls("idea", 0) + 0.3, (W / 2, 300), "NOT an answer machine", -4, CREAM, 64)
    retro(t, ls("idea", 1), (W / 2, 470), "AN AMPLIFIER\nFOR THE MIND", 96)
    lv = ease_out_cubic((t - ls("idea", 1) - 0.3) / 1.4)
    if ls("idea", 1) <= t < ls("idea", 2):
        knob(W / 2, 900, 150, lv, t)
    p = phrase_times("idea", 2, ["Glasses", "A bicycle", "AI can"])
    for (at, fn, lab) in zip(p, (glasses, bicycle, mind), ("EYES", "LEGS", "MIND")):
        cue("pop", at)
        if t >= at:
            k = pop(t, at)
            y = 740 + (p.index(at)) * 250
            if fn is glasses:
                glasses(330, y, k, CREAM)
            elif fn is bicycle:
                bicycle(330, y, k, CREAM, t)
            else:
                mind(330, y, k, YEL, t)
            retro(t, at + 0.15, (740, y), lab, 90, main=YEL if lab == "MIND" else CREAM)
    subtitle(t, "idea")


def room(t, key, n, name, paper_col, items, motif, y0=None):
    motif(t)
    retro(t, ls(key, 0), (W / 2, 210), f"ROOM {n}", 60, main=CREAM, layers=(INK,))
    retro(t, ls(key, 0) + 0.25, (W / 2, 330), name, 124)
    times = phrase_times(key, 1, [s for s, _ in items])
    for i, ((phrase, lab), at) in enumerate(zip(items, times)):
        y = (y0 or (1010 if len(items) > 3 else 1040)) + i * (105 if len(items) > 3 else 120)
        cutout(t, at, (W / 2 + (-1) ** i * 60, y), lab, (-1) ** i * 3, paper_col, 50)
    subtitle(t, key)


def m_understand(t):
    backdrop(wallpaper("waves"))
    shade(60)
    for k in range(10):
        a = t * 0.2 + k * math.pi / 5
        G.draw.line([(W / 2, 680), (W / 2 + 1400 * math.cos(a), 680 + 1400 * math.sin(a))], fill=(160, 90, 200), width=30)
    op = 1.0 if (t % 3.0) > 0.18 else 0.1
    eye(W / 2, 680, 640, t, iris=(60, 170, 255), openness=op)


def m_explore(t):
    backdrop(wallpaper("mint"))
    shade(60)
    petals(W / 2, 700, t)


def m_challenge(t):
    backdrop(wallpaper("split"))
    shade(50)
    b = math.sin(t * 5) * 10
    bubble(330, 560 + b, "I think...", CREAM, 1)
    if t > ls("room3", 1):
        bubble(740, 800 - b, "but what if...?", MINT, -1)
        pts = [(560, 610), (520, 680), (580, 690), (530, 770)]
        G.draw.line(pts, fill=YEL, width=16, joint="curve")


def m_organize(t):
    backdrop(wallpaper("lilac"))
    shade(70)
    rng = np.random.default_rng(9)
    p = ease_in_out((t - ls("room4", 1) - 0.5) / 2.5)
    cols = [PINK, TANG, YEL, MINT, LILAC, TEAL]
    for i in range(12):
        sx, sy, sa = rng.uniform(120, W - 120), rng.uniform(470, 820), rng.uniform(-1, 1)
        gx, gy = W / 2 - 330 + (i % 4) * 220, 520 + (i // 4) * 130
        x, y, a = sx + (gx - sx) * p, sy + (gy - sy) * p, sa * (1 - p) + math.sin(t * 3 + i) * 0.15 * (1 - p)
        ca, sn = math.cos(a), math.sin(a)
        pts = [(x + (px * ca - py * sn), y + (px * sn + py * ca)) for px, py in ((-95, -50), (95, -50), (95, 50), (-95, 50))]
        G.draw.polygon(pts, fill=cols[i % 6], outline=INK, width=5)
    keys(850, t, int(t * 6) % 14)


def s_room1(t):
    room(t, "room1", 1, "UNDERSTAND", CREAM,
         [("Explain", "explain the unfamiliar"), ("Summarize", "summarize dense reports"),
          ("Translate", "jargon  →  plain language")], m_understand)


def s_room2(t):
    room(t, "room2", 2, "EXPLORE", (255, 230, 170),
         [("Brainstorm", "brainstorm possibilities"), ("Generate", "generate hypotheses"),
          ("Play out", "play out the consequences")], m_explore)


def s_room3(t):
    room(t, "room3", 3, "CHALLENGE", (255, 215, 225),
         [("Critique", "critique the argument"), ("Find", "find inconsistencies"),
          ("Simulate", "simulate the other side"), ("Surface", "ask the missing questions")], m_challenge)


def s_room4(t):
    room(t, "room4", 4, "ORGANIZE", (220, 240, 255),
         [("Untangle", "untangle messy thoughts"), ("Compare", "compare competing ideas"),
          ("Turn", "vague idea  →  real plan")], m_organize, y0=1120)


def bars(t, at, y, title, tcol, search, think, slab, tlab):
    if t < at:
        return
    k = ease_out_back((t - at) / 0.35)
    d = G.draw
    x0, x1 = W / 2 - 470 * k, W / 2 + 470 * k
    if x1 - x0 < 520:
        return
    d.rounded_rectangle([x0 + 10, y - 150 + 10, x1 + 10, y + 150 + 10], 30, fill=BLACK)
    d.rounded_rectangle([x0, y - 150, x1, y + 150], 30, fill=CREAM, outline=INK, width=7)
    text((W / 2, y - 100), title, 54, tcol, FONT_FAT)
    for j, (lab, frac, col, vlab) in enumerate((("SEARCHING", search, TANG, slab), ("THINKING", think, PINK, tlab))):
        yy = y - 20 + j * 95
        f = ease_out_cubic((t - at - 0.4 - j * 0.3) / 1.0) * frac
        d.text((x0 + 40, yy), lab, font=font(FONT_FAT, 34), fill=INK, anchor="lm")
        bx0, bx1 = x0 + 290, x1 - 150
        d.rounded_rectangle([bx0, yy - 26, bx1, yy + 26], 12, fill=(225, 210, 190), outline=INK, width=4)
        if f > 0.01:
            d.rounded_rectangle([bx0, yy - 26, bx0 + max(24, (bx1 - bx0) * f), yy + 26], 12, fill=col, outline=INK, width=4)
        d.text((x1 - 40, yy), vlab, font=font(FONT_FAT, 34), fill=INK, anchor="rm")


def s_example(t):
    backdrop(wallpaper("rings"))
    shade(70)
    retro(t, 0.1, (W / 2, 240), "50 REPORTS\n3 HOURS", 100)
    if t < ls("example", 1):
        for i in range(50):
            ph = i * 0.61
            at = ls("example", 0) + i * 0.03
            if t < at:
                continue
            fall = (t - at) * 160
            x = (i * 197) % (W - 160) + 80 + math.sin(t * 2 + ph) * 40
            y = 470 + (fall + i * 37) % 800
            paper(x, y, math.sin(t * 2.5 + ph) * 0.6, 0.9)
        cue("tick", ls("example", 0))
    bars(t, ls("example", 1), 690, "WITHOUT AI", RED, 1.0, 0.04, "3 h", "~0")
    bars(t, ls("example", 2), 1060, "WITH AI", TEAL, 0.07, 1.0, "mins", "3 h")
    subtitle(t, "example")


def s_reach(t):
    backdrop(sky("dusk"))
    st = ls("reach", 1)
    if t >= st:
        for k in range(7):
            r = ((t - st) * 260 + k * 150) % 1050
            c = (PINK, YEL, MINT, LILAC)[k % 4]
            G.draw.ellipse([W / 2 - r, 820 - r, W / 2 + r, 820 + r], outline=c, width=10)
    retro(t, ls("reach", 0) + 0.2, (W / 2, 300), "SPEED", 110, until=st)
    if ls("reach", 0) + 1.0 <= t < st:
        k = ease_out_cubic((t - ls("reach", 0) - 1.0) / 0.3)
        G.draw.line([(W / 2 - 260, 300), (W / 2 - 260 + 520 * k, 300)], fill=RED, width=22)
    retro(t, st, (W / 2, 300), "REACH", 170, main=YEL)
    p = phrase_times("reach", 1, ["You think", "and you"])
    if t >= p[0]:
        k = ease_out_cubic((t - p[0]) / 0.6)
        G.draw.line([(W / 2 - 380 * k, 820), (W / 2 + 380 * k, 820)], fill=CREAM, width=16)
        for sg in (-1, 1):
            xe = W / 2 + sg * 380 * k
            G.draw.polygon([(xe + sg * 30, 820), (xe - sg * 10, 795), (xe - sg * 10, 845)], fill=CREAM)
        cutout(t, p[0], (W / 2, 730), "MORE  (breadth)", 3, CREAM, 50)
    if t >= p[1]:
        k = ease_out_cubic((t - p[1]) / 0.6)
        G.draw.line([(W / 2, 820), (W / 2, 820 + 420 * k)], fill=YEL, width=16)
        G.draw.polygon([(W / 2, 820 + 420 * k + 34), (W / 2 - 26, 820 + 420 * k - 6), (W / 2 + 26, 820 + 420 * k - 6)],
                       fill=YEL)
        cutout(t, p[1], (W / 2 + 190, 1110), "DEEPER  (depth)", -4, (255, 230, 170), 50)
    retro(t, le("reach", 1) + 0.1, (W / 2, 470), "cognitive reach", 70, main=CREAM, layers=(PINK,))
    subtitle(t, "reach")


def s_rules(t):
    backdrop(wallpaper("dots"))
    shade(140)
    d = G.draw
    x0, y0, x1, y1 = 90, 200, W - 90, 1330
    d.rectangle([x0 + 14, y0 + 14, x1 + 14, y1 + 14], fill=BLACK)
    d.rectangle([x0, y0, x1, y1], fill=(245, 232, 200), outline=(120, 70, 40), width=16)
    for x in range(int(x0) + 40, int(x1) - 30, 28):   # cross-stitch border
        for y in (y0 + 38, y1 - 38):
            d.line([(x - 8, y - 8), (x + 8, y + 8)], fill=RED, width=4)
            d.line([(x - 8, y + 8), (x + 8, y - 8)], fill=RED, width=4)
    text((W / 2, y0 + 130), "HOUSE RULES", 92, RED, FONT_SERIF, stroke=0)
    rules = [("1", "VERIFY", "AI can be confidently wrong.\nCheck the sources."),
             ("2", "THINK FIRST", "Write your own take\nbefore you ask."),
             ("3", "INVITE DISAGREEMENT", "Make it argue with you,\nnot just agree."),
             ("4", "YOU DECIDE", "The final judgment\nstays yours.")]
    for i, (n, head, body) in enumerate(rules):
        at = ls("rules", i + 1)
        cue("pop", at)
        if t < at:
            continue
        k = pop(t, at)
        y = y0 + 300 + i * 225
        d.ellipse([x0 + 50, y - 45, x0 + 140, y + 45], fill=TEAL, outline=INK, width=4)
        text((x0 + 95, y), n, 54 * k, CREAM, FONT_FAT)
        d.text((x0 + 175, y - 32), head, font=font(FONT_FAT, 50 * k), fill=INK, anchor="lm")
        d.multiline_text((x0 + 175, y + 30), body, font=font(FONT_SERIF_I, 40 * k), fill=(90, 40, 60), anchor="la",
                         spacing=4)
    cat(900, 1260, 0.75, t)
    subtitle(t, "rules")


def s_outro(t):
    backdrop(sky("sunset"))
    house(W / 2, 1270, t, lit=5, extra=1.0)
    cat(860, 1225, 0.9, t)
    retro(t, ls("outro", 0), (W / 2, 300), "AI DOESN'T REPLACE\nYOUR THINKING", 84)
    retro(t, ls("outro", 1) + 0.2, (W / 2, 560), "it gives it\nMORE ROOM", 104, main=YEL)
    serif(t, le("outro", 1) + 0.4, (W / 2, 1400), "The Thinking House · follow for more rooms", 42, CREAM)
    subtitle(t, "outro")


SCENE_FNS = {"hook": s_hook, "idea": s_idea, "room1": s_room1, "room2": s_room2, "room3": s_room3,
             "room4": s_room4, "example": s_example, "reach": s_reach, "rules": s_rules, "outro": s_outro}
SCENES = [(DUR[k], SCENE_FNS[k]) for k, *_ in SCRIPT]
TOTAL = sum(d for d, _ in SCENES)

# ---------------------------------------------------------------- film look

_rng = np.random.default_rng(1977)
GRAIN = [_rng.normal(0, 9, (H, W)).astype(np.int16) for _ in range(6)]
_Y, _X = np.mgrid[0:H, 0:W]
DIST = np.sqrt((_X - W / 2) ** 2 + (_Y - 820) ** 2).astype(np.float32)
del _Y, _X
RMAX = float(DIST.max())


def film(arr, fi, t, idx, tl):
    a = arr.astype(np.int16)
    a += GRAIN[fi % 6][..., None]
    fl = 1 + 0.035 * math.sin(fi * 1.7) * math.sin(fi * 0.53)
    a = (a * fl).astype(np.int16)
    a[..., 0] += 8
    a[..., 2] -= 6
    h = (fi * 2654435761) & 0xFFFFFFFF
    if h % 5 == 0:
        x = h % (W - 4)
        a[:, x:x + 2] += 70
    for k in range(3):
        hh = (h >> (k * 7)) & 0xFFFF
        x, y = hh % (W - 8), (hh * 31) % (H - 8)
        a[y:y + 5, x:x + 4] = 25
    iris = None
    if tl < 0.5:
        iris = RMAX * ease_in_out(tl / 0.5)
    if t > TOTAL - 0.8:
        iris = RMAX * ease_in_out((TOTAL - t) / 0.8)
    if iris is not None:
        a[DIST > iris] = 0
    wv = int(round(math.sin(fi * 0.9) * 1.5))
    if wv:
        a = np.roll(a, wv, axis=0)
    return np.clip(a, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- score: 70s lounge-pop, ducked under the voice

SR = E.SR


def _tt(d):
    return np.arange(int(d * SR)) / SR


def extra_sfx(sr):
    x = _tt(0.6)
    chime = (np.sin(2 * np.pi * 1568 * x) + 0.4 * np.sin(2 * np.pi * 3136 * x)) * np.exp(-x * 7)
    return {"pop": (chime * 0.5, 0.25), "tick": (np.zeros(10), 0.0)}


def music_fn(n):
    rng = np.random.default_rng(77)
    out = np.zeros(n)

    def add(buf, sig, t, g):
        i = int(t * SR)
        if i < len(buf):
            j = min(len(buf), i + len(sig))
            buf[i:j] += sig[: j - i] * g

    def epiano(f, d=1.6):
        x = _tt(d)
        return ((np.sin(2 * np.pi * f * x) + 0.35 * np.sin(4 * np.pi * f * x)) * np.exp(-x * 1.8)
                + 0.3 * np.sin(2 * np.pi * f * 7.1 * x) * np.exp(-x * 14)) * np.minimum(1, x / 0.004)

    def musicbox(f):
        x = _tt(0.8)
        return (np.sin(2 * np.pi * f * x) + 0.3 * np.sin(2 * np.pi * f * 4 * x)) * np.exp(-x * 5)

    x = _tt(0.3)
    kick = np.sin(2 * np.pi * np.cumsum(50 + 70 * np.exp(-x * 30)) / SR) * np.exp(-x * 10)
    x = _tt(0.18)
    brush = rng.standard_normal(len(x)) * np.exp(-x * 18) * 0.35
    x = _tt(0.04)
    hat = np.diff(rng.standard_normal(len(x) + 1)) * np.exp(-x * 80) * 0.4

    beat = 60 / 100
    prog = [(87.31, [174.61, 220.0, 261.63, 329.63]), (82.41, [164.81, 196.0, 246.94, 293.66]),
            (73.42, [146.83, 174.61, 220.0, 261.63]), (65.41, [130.81, 164.81, 196.0, 246.94])]
    melody = [659.25, 587.33, 523.25, 587.33, 659.25, 783.99, 659.25, 523.25]
    t, bar = 0.0, 0
    total = E.TOTAL
    # eerie theremin-ish intro glide over the first bars
    x = _tt(4.0)
    glide = 440 * 2 ** (np.sin(2 * np.pi * 0.25 * x) * 0.5) * (1 + 0.01 * np.sin(2 * np.pi * 6 * x))
    add(out, np.sin(2 * np.pi * np.cumsum(glide) / SR) * np.minimum(1, x / 0.8) * np.minimum(1, (4 - x) / 1.0), 0, 0.12)
    while t < total:
        root, ch = prog[bar % 4]
        for off in (0, 1.5, 2.5):
            for f in ch:
                add(out, epiano(f), t + off * beat, 0.05)
        for b in range(4):
            tb = t + b * beat
            add(out, kick, tb, 0.5 if b in (0, 2) else 0.2)
            if b in (1, 3):
                add(out, brush, tb, 0.35)
            for h in (0, 0.5):
                add(out, hat, tb + h * beat, 0.12)
            xb = _tt(beat * 0.9)
            bf = root * (1.5 if b == 2 else 1)
            add(out, (np.sin(2 * np.pi * bf * xb) + 0.3 * np.sin(4 * np.pi * bf * xb)) * np.exp(-xb * 3), tb, 0.3)
        if bar % 2 == 1:
            for q, f in enumerate(melody):
                add(out, musicbox(f), t + q * beat / 2, 0.05)
        t += 4 * beat
        bar += 1
    crackle = np.zeros(n)
    idx = rng.integers(0, n, int(total * 25))
    crackle[idx] = rng.uniform(-0.3, 0.3, len(idx))
    out += crackle * 0.15
    # narration + ducking
    voice = np.zeros(n)
    for st, a in VO:
        up = np.interp(np.arange(int(len(a) * SR / VSR)) * VSR / SR, np.arange(len(a)), a)
        add(voice, up, st, 1.0)
    env = np.convolve(np.abs(voice), np.ones(4410) / 4410, mode="same")
    env = np.clip(env / (env.max() + 1e-9) * 4, 0, 1)
    out *= 1 - 0.55 * env
    fade = int(1.5 * SR)
    end = int(total * SR)
    out[end - fade:end] *= np.linspace(1, 0, fade)
    out[end:] = 0
    return out * 0.55 + voice * 1.7


E.SCENE_CUT_FLASH = False
E.POST_FX = film

if __name__ == "__main__":
    print(f"total {TOTAL:.1f}s; scenes: " + ", ".join(f"{k} {DUR[k]:.1f}" for k, *_ in SCRIPT))
    E.main("the_thinking_house.mp4", SCENES, music_fn, extra_sfx)

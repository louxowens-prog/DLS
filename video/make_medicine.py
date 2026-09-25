#!/usr/bin/env python3
"""Render "THE SECOND SET OF EYES": a <2 min vertical short on AI in medicine, styled after
2001: A Space Odyssey (1968): black space, planetary alignment, letter-spaced intertitles,
spacecraft computer displays, a red machine eye, the monolith, a Star Gate light corridor and
a Zarathustra-style fanfare (Richard Strauss, 1896, public domain) over a cluster-chord drone.
Female narration (Kokoro af_bella).

    python3 make_medicine.py                  # -> out/the_second_set_of_eyes.mp4
    python3 make_medicine.py --preview 3 17   # frames -> out/preview/the_second_set_of_eyes/
"""
import math
import textwrap

import numpy as np
from PIL import Image, ImageDraw

import make_video as E
import narrate
from make_video import G, H, W, cue, ease_in_out, ease_out_cubic, font, pop

SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BLACK = (0, 0, 0)
WHITE = (240, 240, 240)
GREY = (120, 120, 125)
HALRED = (230, 20, 20)
AMBER = (255, 170, 40)
BLUE = (70, 140, 255)
GREEN = (60, 230, 120)

SCRIPT = [
    ("hook", 3.4, ["Doctors make life and death calls every day, often in minutes, often exhausted.",
                   "What if they had a second set of eyes that never gets tired?"], 0.6),
    ("patterns", 1.1, ["AI is remarkably good at one thing: spotting patterns in medical data.",
                       "X-rays. CT. MRI. Retinal scans. Pathology slides. Skin photos. Heart rhythms. Lab results."], 1.2),
    ("second", 1.1, ["It doesn't replace the radiologist. It points and says: this tiny spot deserves another look.",
                     "In a large Swedish breast screening trial, AI support found more cancers, and cut radiologists' "
                     "reading workload by forty-four percent."], 0.7),
    ("oracle", 1.1, ["It can also connect what no single mind can hold.",
                     "Symptoms, medications, lab results, past diagnoses, genetics.",
                     "Plus over a million new medical papers every year. No doctor can read them all. "
                     "AI can pull out the few that matter for this patient."], 0.6),
    ("beyond", 1.1, ["It's already here. More than a thousand AI medical devices have been cleared by the U.S. F.D.A.",
                     "It drafts clinical notes, so doctors can face patients, not screens. And it predicted the shapes "
                     "of two hundred million proteins, speeding up drug discovery."], 0.6),
    ("hal", 1.1, ["But remember HAL.",
                  "AI can be confidently wrong. And it can inherit bias, working worse for patients the data left out.",
                  "So it needs real world testing, strong privacy, and a human who makes the final call."], 0.6),
    ("outro", 0.4, ["The goal isn't a machine that replaces your doctor.",
                    "It's a doctor who never has to look alone."], 3.6),
]
TL = narrate.Timeline(SCRIPT, sid=1, speed=1.08)
ls, le = TL.start, TL.end
CHAPTERS = {"patterns": "I  ·  PATTERNS", "second": "II  ·  THE SECOND LOOK", "oracle": "III  ·  THE ORACLE",
            "beyond": "IV  ·  ALREADY HERE", "hal": "V  ·  REMEMBER HAL"}

# ---------------------------------------------------------------- basics

_rng = np.random.default_rng(2001)
_stars = np.zeros((H, W, 3), np.uint8)
for _ in range(900):
    y, x, b = _rng.integers(0, H), _rng.integers(0, W), _rng.integers(60, 255)
    _stars[y, x] = b
    if b > 220:
        _stars[max(0, y - 1):y + 2, max(0, x - 1):x + 2] = b // 2
SPACE = Image.fromarray(_stars)


def space():
    G.img = SPACE.copy()
    G.draw = ImageDraw.Draw(G.img)


def black():
    G.img = Image.new("RGB", (W, H), BLACK)
    G.draw = ImageDraw.Draw(G.img)


def fade(t, at, until=None, d=0.35):
    a = ease_in_out((t - at) / d)
    if until is not None:
        a = min(a, ease_in_out((until - t) / d))
    return max(0.0, min(1.0, a))


def dim(c, a):
    return tuple(int(v * a) for v in c)


def spaced(xy, s, size, col=WHITE, track=0.35, fnt=SANS, anchor="mm"):
    """Letter-spaced caps, the film's title-card look."""
    f = font(fnt, size)
    gap = size * track
    w = sum(f.getlength(ch) for ch in s) + gap * (len(s) - 1)
    x = xy[0] - w / 2 if anchor == "mm" else xy[0]
    for ch in s:
        G.draw.text((x, xy[1]), ch, font=f, fill=col, anchor="lm")
        x += f.getlength(ch) + gap


def ftext(t, at, xy, s, size, col=WHITE, until=None, track=0.35, fnt=SANS):
    a = fade(t, at, until)
    if a > 0:
        f = font(fnt, size)
        w = sum(f.getlength(ch) for ch in s) + size * track * (len(s) - 1)
        if w > W - 90:
            size *= (W - 90) / w
        spaced(xy, s, size, dim(col, a), track, fnt)


def intertitle(t, key):
    if key in CHAPTERS and t < 0.95:
        black()
        spaced((W / 2, H / 2 - 40), CHAPTERS[key], 44, dim(WHITE, fade(t, 0.0, 0.95, 0.25)))
        return True
    return False


def subtitle(t, key):
    a = TL.active(key, t)
    if not a:
        return
    txt = "\n".join(textwrap.wrap(a[0], 34))
    f = font(SANS, 42)
    bb = G.draw.multiline_textbbox((W / 2, 1560), txt, font=f, anchor="mm", align="center", spacing=10)
    box = (int(bb[0] - 26), int(bb[1] - 16), int(bb[2] + 26), int(bb[3] + 18))
    G.img.paste(BLACK, box, Image.new("L", (box[2] - box[0], box[3] - box[1]), 170))
    G.draw.multiline_text((W / 2, 1560), txt, font=f, fill=WHITE, anchor="mm", align="center", spacing=10)


def glow(cx, cy, r, col, steps=18, core=None):
    for i in range(steps, 0, -1):
        k = i / steps
        c = tuple(int(v * (1 - k) ** 1.6) for v in col)
        rr = r * k
        G.draw.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=c)
    if core:
        G.draw.ellipse([cx - r * 0.08, cy - r * 0.08, cx + r * 0.08, cy + r * 0.08], fill=core)


def hal_eye(cx, cy, R, t, pulse=1.0):
    d = G.draw
    for i in range(12, 0, -1):
        k = i / 12
        g = int(70 + 110 * (1 - abs(k - 0.8) * 2.5))
        d.ellipse([cx - R * (0.85 + 0.15 * k), cy - R * (0.85 + 0.15 * k), cx + R * (0.85 + 0.15 * k),
                   cy + R * (0.85 + 0.15 * k)], fill=(max(40, g), max(40, g), max(45, g + 5)))
    d.ellipse([cx - R * 0.84, cy - R * 0.84, cx + R * 0.84, cy + R * 0.84], fill=(8, 8, 10))
    p = 0.85 + 0.15 * math.sin(t * 2.4) * pulse
    for i in range(24, 0, -1):
        k = i / 24
        c = (int(255 * (1 - k) ** 0.9 * p), int(40 * (1 - k) ** 3), int(10 * (1 - k) ** 3))
        rr = R * 0.8 * k
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=c)
    d.ellipse([cx - R * 0.06, cy - R * 0.06, cx + R * 0.06, cy + R * 0.06], fill=(255, 235, 120))
    d.ellipse([cx - R * 0.5, cy - R * 0.62, cx - R * 0.22, cy - R * 0.5], fill=(90, 90, 110))


def earth(cx, cy, R, t):
    """Earth lit from above: day side, clouds, then a night side confined to the disc."""
    size = int(2 * R + 4)
    lay = Image.new("RGB", (size, size), BLACK)
    d = ImageDraw.Draw(lay)
    c0 = size / 2
    for i in range(16, 0, -1):
        k = i / 16
        c = (int(20 + 30 * (1 - k)), int(60 + 90 * (1 - k)), int(140 + 100 * (1 - k)))
        d.ellipse([c0 - R * k, c0 - R * k, c0 + R * k, c0 + R * k], fill=c)
    for j in range(7):
        a = t * 0.05 + j * 0.9
        x, y = c0 + R * 0.6 * math.cos(a), c0 + R * 0.35 * math.sin(a * 1.3)
        d.ellipse([x - R * 0.28, y - R * 0.06, x + R * 0.28, y + R * 0.06], fill=(190, 210, 235))
    d.ellipse([c0 - R * 1.05, c0 - R * 0.1, c0 + R * 1.05, c0 + R * 2.1], fill=(4, 8, 18))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([c0 - R, c0 - R, c0 + R, c0 + R], fill=255)
    G.img.paste(lay, (int(cx - c0), int(cy - c0)), mask)


def moon_limb(cy):
    d = G.draw
    for i in range(10):
        c = 30 + i * 9
        d.ellipse([-900, cy + i * 6, W + 900, cy + 2200], fill=(c, c, c + 2))


def sun(cx, cy, r, a=1.0):
    glow(cx, cy, r * 3.2, dim((255, 240, 210), a), 22)
    G.draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=dim((255, 255, 250), a))
    for k in range(6):
        ang = k * math.pi / 6
        L = r * 4
        G.draw.line([(cx - L * math.cos(ang), cy - L * math.sin(ang)), (cx + L * math.cos(ang), cy + L * math.sin(ang))],
                    fill=dim((255, 245, 225), a * 0.6), width=3)


# ---------------------------------------------------------------- the scans (procedural, not real patients)


def frame_box(b, label, t, at=0.0):
    x0, y0, x1, y1 = b
    G.draw.rectangle(b, outline=WHITE, width=3)
    for (x, y) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        G.draw.rectangle([x - 8, y - 8, x + 8, y + 8], fill=WHITE)
    sy = y0 + (y1 - y0) * (((t - at) * 0.6) % 1)
    G.draw.line([(x0, sy), (x1, sy)], fill=(120, 200, 255), width=2)
    G.draw.text((x0 + 14, y0 + 12), label, font=font(BOLD, max(14, int((y1 - y0) * 0.055))), fill=(120, 200, 255))


def scan_xray(b, t, spot=False):
    x0, y0, x1, y1 = b
    w, h = x1 - x0, y1 - y0
    cx = (x0 + x1) / 2
    d = G.draw
    d.rectangle(b, fill=(8, 8, 10))
    d.ellipse([cx - w * 0.42, y0 + h * 0.1, cx - w * 0.04, y0 + h * 0.92], fill=(26, 26, 30))
    d.ellipse([cx + w * 0.04, y0 + h * 0.1, cx + w * 0.42, y0 + h * 0.92], fill=(26, 26, 30))
    for i in range(9):
        y = y0 + h * (0.14 + i * 0.085)
        for sg in (-1, 1):
            d.arc([cx + sg * w * 0.02 - w * 0.42 * (sg > 0) - w * 0.0, y - h * 0.05, cx + sg * w * 0.02 + w * 0.42 * (sg < 0),
                   y + h * 0.09], 180 if sg < 0 else 0, 360 if sg < 0 else 180, fill=(150, 150, 155), width=max(2, int(w * 0.012)))
    d.rectangle([cx - w * 0.03, y0 + h * 0.05, cx + w * 0.03, y1 - h * 0.02], fill=(170, 170, 175))
    d.ellipse([cx - w * 0.1, y0 + h * 0.5, cx + w * 0.2, y0 + h * 0.8], fill=(120, 120, 125))
    if spot:
        sx, sy = x0 + w * 0.68, y0 + h * 0.38
        d.ellipse([sx - w * 0.012, sy - w * 0.012, sx + w * 0.012, sy + w * 0.012], fill=(215, 215, 215))


def scan_ct(b, t):
    x0, y0, x1, y1 = b
    w, h = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    d = G.draw
    d.rectangle(b, fill=(5, 5, 6))
    d.ellipse([cx - w * 0.4, cy - h * 0.36, cx + w * 0.4, cy + h * 0.36], fill=(95, 95, 98))
    d.ellipse([cx - w * 0.33, cy - h * 0.27, cx - w * 0.02, cy + h * 0.2], fill=(40, 40, 42))
    d.ellipse([cx + w * 0.02, cy - h * 0.27, cx + w * 0.33, cy + h * 0.2], fill=(40, 40, 42))
    d.ellipse([cx - w * 0.07, cy + h * 0.18, cx + w * 0.07, cy + h * 0.32], fill=(230, 230, 230))
    d.ellipse([cx - w * 0.1, cy - h * 0.1, cx + w * 0.08, cy + h * 0.1], fill=(140, 140, 145))


def scan_mri(b, t):
    x0, y0, x1, y1 = b
    w, h = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    d = G.draw
    d.rectangle(b, fill=(4, 4, 6))
    d.ellipse([cx - w * 0.34, cy - h * 0.42, cx + w * 0.34, cy + h * 0.42], fill=(150, 150, 158))
    d.ellipse([cx - w * 0.3, cy - h * 0.38, cx + w * 0.3, cy + h * 0.38], fill=(95, 95, 102))
    for k in range(9):
        r = 0.08 + k * 0.03
        pts = [(cx + w * r * math.cos(a) * (1 + 0.1 * math.sin(a * 9 + k)),
                cy + h * r * 1.2 * math.sin(a) * (1 + 0.1 * math.sin(a * 9 + k))) for a in np.linspace(0, 2 * math.pi, 60)]
        d.line(pts, fill=(175, 175, 182), width=2)
    d.ellipse([cx - w * 0.07, cy - h * 0.1, cx - w * 0.01, cy + h * 0.06], fill=(20, 20, 24))
    d.ellipse([cx + w * 0.01, cy - h * 0.1, cx + w * 0.07, cy + h * 0.06], fill=(20, 20, 24))


def _branch(x, y, a, L, n, w, out):
    if n == 0 or L < 4:
        return
    x2, y2 = x + L * math.cos(a), y + L * math.sin(a)
    out.append(((x, y, x2, y2), w))
    _branch(x2, y2, a - 0.45, L * 0.72, n - 1, max(1, w - 1), out)
    _branch(x2, y2, a + 0.4, L * 0.68, n - 1, max(1, w - 1), out)


def scan_retina(b, t):
    x0, y0, x1, y1 = b
    w, h = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = min(w, h) * 0.46
    d = G.draw
    d.rectangle(b, fill=(0, 0, 0))
    for i in range(14, 0, -1):
        k = i / 14
        d.ellipse([cx - R * k, cy - R * k, cx + R * k, cy + R * k], fill=(int(120 + 110 * (1 - k)), int(40 + 60 * (1 - k)), 20))
    ox, oy = cx - R * 0.35, cy
    segs = []
    for a in (-2.4, -1.0, 0.6, 2.2, 3.0):
        _branch(ox, oy, a, R * 0.35, 6, max(2, int(R * 0.03)), segs)
    for (xa, ya, xb, yb), lw in segs:
        d.line([(xa, ya), (xb, yb)], fill=(150, 15, 15), width=lw)
    d.ellipse([ox - R * 0.12, oy - R * 0.12, ox + R * 0.12, oy + R * 0.12], fill=(255, 220, 140))


def scan_path(b, t):
    x0, y0, x1, y1 = b
    d = G.draw
    d.rectangle(b, fill=(235, 180, 205))
    rng = np.random.default_rng(5)
    for _ in range(int((x1 - x0) * (y1 - y0) / 1400)):
        x, y = rng.uniform(x0 + 6, x1 - 6), rng.uniform(y0 + 6, y1 - 6)
        r = rng.uniform(4, 10) * (x1 - x0) / 900
        d.ellipse([x - r * 2.2, y - r * 1.8, x + r * 2.2, y + r * 1.8], fill=(245, 150, 190))
        d.ellipse([x - r, y - r * 0.8, x + r, y + r * 0.8], fill=(95, 40, 140))


def scan_skin(b, t):
    x0, y0, x1, y1 = b
    w, h = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    d = G.draw
    d.rectangle(b, fill=(205, 160, 125))
    rng = np.random.default_rng(8)
    for _ in range(80):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        d.line([(x, y), (x + w * 0.05, y + h * 0.02)], fill=(190, 145, 110), width=2)
    pts = [(cx + w * 0.16 * (1 + 0.25 * math.sin(3 * a + 1) + 0.1 * math.sin(7 * a)) * math.cos(a),
            cy + h * 0.2 * (1 + 0.25 * math.sin(3 * a + 1) + 0.1 * math.sin(7 * a)) * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 50)]
    d.polygon(pts, fill=(80, 45, 30))
    d.ellipse([cx - w * 0.05, cy - h * 0.05, cx + w * 0.07, cy + h * 0.08], fill=(45, 25, 20))


def scan_ecg(b, t):
    x0, y0, x1, y1 = b
    w, h = x1 - x0, y1 - y0
    d = G.draw
    d.rectangle(b, fill=(0, 12, 6))
    for gx in np.arange(x0, x1, w / 16):
        d.line([(gx, y0), (gx, y1)], fill=(0, 45, 22), width=1)
    for gy in np.arange(y0, y1, h / 8):
        d.line([(x0, gy), (x1, gy)], fill=(0, 45, 22), width=1)
    pts = []
    for i in range(301):
        u = (i / 300 * 3 + t * 1.2) % 1
        v = (0.1 * math.exp(-((u - 0.15) / 0.03) ** 2) - 0.12 * math.exp(-((u - 0.30) / 0.01) ** 2)
             + 0.9 * math.exp(-((u - 0.33) / 0.012) ** 2) - 0.2 * math.exp(-((u - 0.36) / 0.012) ** 2)
             + 0.22 * math.exp(-((u - 0.55) / 0.05) ** 2))
        pts.append((x0 + w * i / 300, y0 + h * 0.62 - v * h * 0.45))
    d.line(pts, fill=GREEN, width=max(2, int(h * 0.012)))


def scan_labs(b, t):
    x0, y0, x1, y1 = b
    w, h = x1 - x0, y1 - y0
    d = G.draw
    d.rectangle(b, fill=(6, 8, 18))
    rows = [("GLUCOSE", "98", 0), ("HbA1c", "5.4", 0), ("SODIUM", "139", 0), ("POTASSIUM", "5.9", 1),
            ("CREATININE", "1.0", 0), ("HEMOGLOBIN", "13.8", 0)]
    f = font(BOLD, max(12, int(h * 0.075)))
    for i, (k, v, flag) in enumerate(rows):
        y = y0 + h * (0.15 + i * 0.14)
        col = HALRED if flag else (170, 200, 255)
        d.text((x0 + w * 0.08, y), k, font=f, fill=col, anchor="lm")
        d.text((x1 - w * 0.08, y), v + ("  ▲" if flag else ""), font=f, fill=col, anchor="rm")


SCANS = [("X-rays", "X-RAY", scan_xray), ("CT", "CT", scan_ct), ("MRI", "MRI", scan_mri),
         ("Retinal", "RETINA", scan_retina), ("Pathology", "PATHOLOGY", scan_path), ("Skin", "DERMATOLOGY", scan_skin),
         ("Heart", "ECG", scan_ecg), ("Lab", "LABS", scan_labs)]


# ---------------------------------------------------------------- scenes


def s_hook(t):
    space()
    rise = ease_in_out(t / 3.2)
    moon_limb(1500 - 200 * rise)
    earth(W / 2, 1220 - 380 * rise, 380, t)
    sun(W / 2, 900 - 480 * rise, 34, fade(t, 1.6))
    ftext(t, 2.6, (W / 2, 250), "THE SECOND SET OF EYES", 58, WHITE, until=ls("hook", 1) + 0.2)
    ftext(t, 3.0, (W / 2, 330), "A  SHORT  ON  AI  AND  MEDICINE", 26, GREY, until=ls("hook", 1) + 0.2)
    if t >= ls("hook", 1):
        hal_eye(W / 2, 330, 150 * ease_out_cubic((t - ls("hook", 1)) / 0.6) + 1, t)
    subtitle(t, "hook")


def s_patterns(t):
    if intertitle(t, "patterns"):
        return
    black()
    ts = TL.phrases("patterns", 1, [p for p, _, _ in SCANS])
    grid_at = le("patterns", 1) + 0.1
    if t < ts[0]:
        hal_eye(W / 2, 760, 260, t)
        ftext(t, ls("patterns", 0) + 0.8, (W / 2, 1180), "PATTERN RECOGNITION", 40, WHITE)
    elif t < grid_at:
        i = max(k for k, a in enumerate(ts) if t >= a)
        _, lab, fn = SCANS[i]
        b = (70, 330, W - 70, 1250)
        fn(b, t)
        frame_box(b, f"SCAN {i + 1:02d}/08", t, ts[i])
        spaced((W / 2, 1320), lab, 52, WHITE)
        hal_eye(W - 150, 230, 60, t)
    else:
        for i, (_, lab, fn) in enumerate(SCANS):
            c, r = i % 2, i // 2
            b = (60 + c * 490, 300 + r * 280, 60 + c * 490 + 470, 300 + r * 280 + 240)
            fn(b, t)
            frame_box(b, lab, t, i * 0.13)
    for a in ts:
        cue("pop", a)
    subtitle(t, "patterns")


def s_second(t):
    if intertitle(t, "second"):
        return
    black()
    if t < ls("second", 1):
        b = (70, 300, W - 70, 1330)
        scan_xray(b, t, spot=True)
        frame_box(b, "CHEST  ·  AI SECOND READ", t)
        hal_eye(W - 140, 200, 70, t)
        lock = TL.phrases("second", 0, ["this tiny"])[0]
        tx, ty = 70 + (W - 140) * 0.68, 300 + 1030 * 0.38
        if t < lock:
            u = (t - 1.1) * 0.9
            rx, ry = W / 2 + 300 * math.sin(u * 1.7), 800 + 330 * math.sin(u * 1.1 + 1)
        else:
            k = ease_out_cubic((t - lock) / 0.5)
            u = (lock - 1.1) * 0.9
            sx0, sy0 = W / 2 + 300 * math.sin(u * 1.7), 800 + 330 * math.sin(u * 1.1 + 1)
            rx, ry = sx0 + (tx - sx0) * k, sy0 + (ty - sy0) * k
        locked = t >= lock + 0.5
        s = 46 if locked else 90
        col = HALRED if locked else (120, 200, 255)
        G.draw.rectangle([rx - s, ry - s, rx + s, ry + s], outline=col, width=5)
        G.draw.line([(rx - s - 30, ry), (rx - s + 12, ry)], fill=col, width=4)
        G.draw.line([(rx + s - 12, ry), (rx + s + 30, ry)], fill=col, width=4)
        cue("tick", lock + 0.5)
        if locked:
            G.draw.rectangle([rx - 270, ry + s + 20, rx + 60, ry + s + 80], fill=(40, 0, 0), outline=HALRED, width=3)
            G.draw.text((rx - 105, ry + s + 50), "REVIEW THIS REGION", font=font(BOLD, 26), fill=(255, 120, 120),
                        anchor="mm")
    else:
        at = ls("second", 1)
        ftext(t, at, (W / 2, 290), "SWEDEN  ·  BREAST SCREENING TRIAL", 34, WHITE)
        ftext(t, at + 0.3, (W / 2, 350), "RADIOLOGISTS + AI  vs  RADIOLOGISTS ALONE", 24, GREY)
        rows = [("CANCERS FOUND", 1.0, 1.2, "MORE", TL.phrases("second", 1, ["found more"])[0]),
                ("READING WORKLOAD", 1.0, 0.56, "−44%", TL.phrases("second", 1, ["and cut"])[0])]
        for j, (lab, base, ai, tag, rat) in enumerate(rows):
            y = 560 + j * 420
            a = fade(t, rat - 0.3)
            if a <= 0:
                continue
            spaced((W / 2, y), lab, 36, dim(WHITE, a))
            for k, (name, v, col) in enumerate((("STANDARD", base, GREY), ("WITH AI", ai, AMBER if j == 0 else BLUE))):
                yy = y + 90 + k * 110
                L = 620 * v * ease_out_cubic((t - rat) / 0.9)
                G.draw.text((80, yy), name, font=font(BOLD, 28), fill=dim(WHITE, a), anchor="lm")
                G.draw.rectangle([320, yy - 30, 320 + L, yy + 30], fill=dim(col, a))
            if t >= rat + 0.9:
                G.draw.text((W - 80, y + 300), tag, font=font(BOLD, 64), fill=AMBER if j == 0 else BLUE, anchor="rm")
    subtitle(t, "second")


def monolith(cx, top, w, h, t):
    d = G.draw
    d.rectangle([cx - w / 2, top, cx + w / 2, top + h], fill=(4, 4, 5))
    d.line([(cx + w / 2, top), (cx + w / 2, top + h)], fill=(70, 70, 80), width=3)
    d.line([(cx - w / 2, top), (cx + w / 2, top)], fill=(90, 90, 100), width=2)


def s_oracle(t):
    if intertitle(t, "oracle"):
        return
    space()
    moon_limb(1380)
    sun(W / 2, 470, 20, fade(t, 1.0))
    monolith(W / 2, 560, 190, 760, t)
    words = ["SYMPTOMS", "MEDICATIONS", "LAB RESULTS", "PAST DIAGNOSES", "GENETICS"]
    ts = TL.phrases("oracle", 1, ["Symptoms", "medications", "lab results", "past diagnoses", "genetics"])
    for i, (wd, at) in enumerate(zip(words, ts)):
        cue("pop", at)
        if t < at:
            continue
        k = ease_in_out((t - at) / 2.4)
        ang = i * 2 * math.pi / 5 + (t - at) * 1.2
        r = 300 * (1 - k)
        x, y = W / 2 + r * math.cos(ang), 940 + r * math.sin(ang) * 0.7
        if k < 0.97:
            spaced((x, y), wd, 30, dim(WHITE, 1 - k * 0.8), 0.25)
    p = ls("oracle", 2)
    if t >= p:
        n = int(min(1_000_000, 1_000_000 * ease_out_cubic((t - p) / 2.0)))
        rng = np.random.default_rng(12)
        for i in range(240):
            x, y = rng.uniform(80, W - 80), rng.uniform(420, 1360)
            if abs(x - W / 2) < 110 and 560 < y < 1320:
                continue
            tw = 0.5 + 0.5 * math.sin(t * 4 + i)
            G.draw.rectangle([x - 5, y - 7, x + 5, y + 7], fill=dim((200, 210, 255), 0.35 + 0.4 * tw))
        spaced((W / 2, 230), f"{n:,}+", 70, WHITE, 0.15, BOLD)
        spaced((W / 2, 300), "NEW BIOMEDICAL PAPERS / YEAR", 26, GREY)
        pick = TL.phrases("oracle", 2, ["AI can pull"])[0]
        for j in range(3):
            at = pick + 0.3 + j * 0.3
            if t >= at:
                k = ease_out_cubic((t - at) / 0.5)
                y = 700 + j * 170
                x = W / 2 + 330
                G.draw.rectangle([x - 150 * k, y - 60, x + 150 * k, y + 60], fill=(12, 14, 24), outline=AMBER, width=3)
                if k > 0.9:
                    G.draw.text((x, y - 18), f"RELEVANT  0{j + 1}", font=font(BOLD, 24), fill=AMBER, anchor="mm")
                    G.draw.text((x, y + 20), "this patient", font=font(SANS, 22), fill=WHITE, anchor="mm")
    subtitle(t, "oracle")


def s_beyond(t):
    if intertitle(t, "beyond"):
        return
    black()
    if t < ls("beyond", 1):
        at = ls("beyond", 0)
        n = int(1000 * ease_out_cubic((t - at - 0.8) / 2.2)) if t > at + 0.8 else 0
        spaced((W / 2, 330), f"{n:,}+", 120, WHITE, 0.1, BOLD)
        ftext(t, at + 0.8, (W / 2, 450), "AI-ENABLED MEDICAL DEVICES", 32, GREY)
        ftext(t, at + 1.0, (W / 2, 500), "CLEARED BY THE U.S. FDA", 32, GREY)
        for i in range(min(n // 5, 200)):
            c, r = i % 20, i // 20
            col = AMBER if (i * 7) % 10 < 7 else BLUE
            G.draw.rectangle([90 + c * 46, 620 + r * 64, 90 + c * 46 + 34, 620 + r * 64 + 48], fill=col)
        if n >= 900:
            ftext(t, at + 2.8, (W / 2, 1300), "MOST ARE IN RADIOLOGY", 30, AMBER)
    else:
        p1, p2 = TL.phrases("beyond", 1, ["It drafts", "And it predicted"])
        if t < p2:
            for sx, lab in ((330, "DOCTOR"), (750, "PATIENT")):
                glow(sx, 600, 90, (80, 80, 90), 8)
                G.draw.ellipse([sx - 70, 530, sx + 70, 670], fill=(30, 30, 34), outline=WHITE, width=3)
                G.draw.rectangle([sx - 110, 700, sx + 110, 900], fill=(30, 30, 34), outline=WHITE, width=3)
                spaced((sx, 950), lab, 26, GREY)
            for i in range(40):
                x = 430 + i * 5.5
                a = 30 * abs(math.sin(t * 9 + i * 0.7)) * math.sin(i / 39 * math.pi)
                G.draw.line([(x, 640 - a), (x, 640 + a)], fill=BLUE, width=3)
            G.draw.rectangle([120, 1040, W - 120, 1360], fill=(10, 12, 20), outline=BLUE, width=3)
            note = "S: 3 days of cough, mild fever.\nO: temp 38.1 C, lungs clear.\nA: likely viral infection.\nP: fluids, rest, recheck in 48h."
            k = int(len(note) * min(1, (t - p1) / 3.0))
            G.draw.multiline_text((150, 1070), note[:k], font=font(SANS, 34), fill=WHITE, spacing=16)
            ftext(t, p1 + 0.2, (W / 2, 330), "AI SCRIBE", 50, WHITE)
            ftext(t, p1 + 0.5, (W / 2, 400), "EYES ON THE PATIENT, NOT THE SCREEN", 26, GREY)
        else:
            ftext(t, p2, (W / 2, 300), "200,000,000+", 80, WHITE, fnt=BOLD, track=0.1)
            ftext(t, p2 + 0.2, (W / 2, 390), "PROTEIN STRUCTURES PREDICTED", 30, GREY)
            pts = []
            for i in range(420):
                u = i / 420
                a = u * 22 + t * 0.8
                x3, y3, z3 = 150 * math.cos(a) * (1 + 0.5 * math.sin(u * 9)), u * 900 - 450, 150 * math.sin(a)
                rot = t * 0.6
                x, z = x3 * math.cos(rot) - z3 * math.sin(rot), x3 * math.sin(rot) + z3 * math.cos(rot)
                pts.append((W / 2 + x, 900 + y3 * 0.9, z))
            for i in range(len(pts) - 1):
                (xa, ya, za), (xb, yb, zb) = pts[i], pts[i + 1]
                u = i / len(pts)
                shade = 0.55 + 0.45 * (za + 150) / 300
                col = dim((int(80 + 175 * u), int(120 + 80 * (1 - u)), int(255 - 150 * u)), shade)
                G.draw.line([(xa, ya), (xb, yb)], fill=col, width=int(8 + 6 * shade))
    subtitle(t, "beyond")


def s_hal(t):
    if intertitle(t, "hal"):
        return
    black()
    st2 = ls("hal", 2)
    if t < st2:
        hal_eye(W / 2, 700, 330, t, pulse=2.0)
        p = TL.phrases("hal", 1, ["confidently", "inherit bias"])
        ftext(t, p[0], (W / 2, 1150), "CONFIDENTLY WRONG", 44, HALRED)
        ftext(t, p[1], (W / 2, 1240), "INHERITED BIAS", 44, HALRED)
        ftext(t, p[1] + 0.8, (W / 2, 1310), "WORSE FOR PATIENTS THE DATA LEFT OUT", 26, (255, 120, 120))
    else:
        hal_eye(W / 2, 360, 150, t)
        items = ["TESTED IN REAL HOSPITALS", "PATIENT PRIVACY PROTECTED", "A HUMAN MAKES THE FINAL CALL"]
        ts = TL.phrases("hal", 2, ["real world", "strong privacy", "a human"])
        for i, (s, at) in enumerate(zip(items, ts)):
            cue("tick", at)
            a = fade(t, at, d=0.25)
            if a <= 0:
                continue
            y = 700 + i * 200
            G.draw.rectangle([90, y - 70, W - 90, y + 70], fill=dim((10, 26, 16), a), outline=dim(GREEN, a), width=3)
            G.draw.rectangle([120, y - 32, 184, y + 32], outline=dim(GREEN, a), width=4)
            G.draw.line([(132, y), (148, y + 18), (174, y - 20)], fill=dim(GREEN, a), width=7)
            G.draw.text((220, y), s, font=font(BOLD, 36), fill=dim(WHITE, a), anchor="lm")
    subtitle(t, "hal")


def stargate(t, vx=W / 2, vy=H * 0.45):
    d = G.draw
    cols = [(255, 60, 160), (60, 200, 255), (255, 170, 30), (120, 255, 120), (170, 90, 255)]
    for side in (-1, 1):
        for i in range(160):
            z = ((i * 0.37 + t * 1.6) % 1.0)
            depth = z ** 2.2
            y = vy + (i % 32 - 16) * 34 * depth * 2.4
            x0 = vx + side * (30 + 1100 * depth)
            x1 = vx + side * (30 + 1100 * min(1, (z + 0.06) ** 2.2))
            col = cols[(i * 3) % 5]
            d.line([(x0, y), (x1, y)], fill=dim(col, 0.35 + 0.65 * z), width=max(3, int(40 * depth)))


def s_outro(t):
    st1 = ls("outro", 1)
    if t < st1:
        black()
        stargate(t)
    else:
        space()
        rise = ease_in_out((t - st1) / 3.0)
        moon_limb(1500 - 120 * rise)
        earth(W / 2, 1150 - 250 * rise, 380, t)
        sun(W / 2, 760 - 260 * rise, 34, fade(t, st1 + 0.6))
        ftext(t, st1 + 0.3, (W / 2, 250), "A DOCTOR WHO NEVER", 48, WHITE)
        ftext(t, st1 + 0.6, (W / 2, 320), "HAS TO LOOK ALONE", 48, WHITE)
        ftext(t, le("outro", 1) + 1.0, (W / 2, 1300), "THE SECOND SET OF EYES", 34, GREY)
    subtitle(t, "outro")


SCENE_FNS = {"hook": s_hook, "patterns": s_patterns, "second": s_second, "oracle": s_oracle, "beyond": s_beyond,
             "hal": s_hal, "outro": s_outro}
SCENES = [(TL.dur[k], SCENE_FNS[k]) for k, *_ in SCRIPT]
TOTAL = TL.total

# ---------------------------------------------------------------- score

SR = E.SR


def _tt(d):
    return np.arange(int(d * SR)) / SR


def brass(f, d, g=1.0):
    x = _tt(d)
    y = sum(np.sin(2 * np.pi * f * k * x * (1 + 0.002 * np.sin(2 * np.pi * 5 * x))) / k ** 1.1 for k in range(1, 9))
    return y * np.minimum(1, x / 0.12) * np.minimum(1, (d - x) / 0.3) * g


def timp(f):
    x = _tt(1.2)
    return (np.sin(2 * np.pi * f * x) + 0.5 * np.sin(2 * np.pi * f * 1.5 * x)) * np.exp(-x * 3)


def fanfare(out, t0, add):
    """Strauss' 'sunrise' motif: C - G - C', then the major chord and timpani."""
    add(out, sum(brass(f, 3.6, 0.5) for f in (32.7, 65.41)) * np.minimum(1, _tt(3.6) / 1.5), t0, 0.35)
    add(out, brass(261.63, 0.8), t0 + 0.2, 0.22)
    add(out, brass(392.0, 0.8), t0 + 1.0, 0.22)
    add(out, brass(523.25, 0.9), t0 + 1.8, 0.24)
    add(out, sum(brass(f, 3.0) for f in (130.81, 261.63, 329.63, 392.0, 523.25)), t0 + 2.6, 0.12)
    for k in range(6):
        add(out, timp(65.41 if k % 2 == 0 else 98.0), t0 + 2.6 + k * 0.27, 0.5 - k * 0.05)


def extra_sfx(sr):
    x = _tt(0.09)
    beep = np.sin(2 * np.pi * 1320 * x) * np.minimum(1, (0.09 - x) / 0.02)
    x2 = _tt(0.25)
    lock = np.sin(2 * np.pi * 880 * x2) * np.exp(-x2 * 10) + np.sin(2 * np.pi * 1760 * x2) * np.exp(-x2 * 14) * 0.5
    return {"pop": (beep, 0.18), "tick": (lock, 0.3)}


def music_fn(n):
    out = np.zeros(n)

    def add(buf, sig, t, g):
        i = int(t * SR)
        if i < n:
            j = min(n, i + len(sig))
            buf[i:j] += sig[: j - i] * g

    total = E.TOTAL
    fanfare(out, 0.0, add)
    # cluster drone: many slowly drifting voices, eerie and weightless
    x = np.arange(n) / SR
    drone = np.zeros(n)
    rng = np.random.default_rng(68)
    for k in range(14):
        f0 = 220 * 2 ** (rng.uniform(-12, 12) / 12)
        drift = 1 + 0.01 * np.sin(2 * np.pi * rng.uniform(0.02, 0.07) * x + rng.uniform(0, 6))
        drone += np.sin(2 * np.pi * f0 * np.cumsum(drift) / SR) * (0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(0.03, 0.1) * x))
    drone *= np.clip((x - 4.0) / 3.0, 0, 1) / 14
    out += drone * 0.5
    # reprise of the fanfare at the final Earth-rise
    start = sum(TL.dur[k] for k, *_ in SCRIPT[:-1]) + ls("outro", 1)
    fanfare(out, start - 0.2, add)
    voice = TL.track(n, SR)
    out = narrate.duck(out, voice, SR, depth=0.6)
    fade = int(1.5 * SR)
    end = int(total * SR)
    out[end - fade:end] *= np.linspace(1, 0, fade)
    out[end:] = 0
    return out * 0.7 + voice * 1.7


E.SCENE_CUT_FLASH = False

if __name__ == "__main__":
    print(f"total {TOTAL:.1f}s; " + ", ".join(f"{k} {TL.dur[k]:.1f}" for k, *_ in SCRIPT))
    E.main("the_second_set_of_eyes.mp4", SCENES, music_fn, extra_sfx)

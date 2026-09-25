#!/usr/bin/env python3
""""What Is Intelligence?" in the style of 2001: A Space Odyssey, drawn entirely in 2D (no Blender),
full 9:16 for Instagram Reels (key content kept inside the Reels safe zone).

Reuses the narration/timeline (script.py), plates, readout panels and soundtrack (make_2001.py) and
the compositing helpers (comp.py). Output: out/what_is_intelligence_2001_reels.mp4 (+ _master).
"""
import math
import os
import subprocess
import sys
import textwrap
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import comp  # noqa: E402
import make_2001 as M  # noqa: E402
from script import CHAPTER, FPS, SCRIPT, TL  # noqa: E402

W, H = 1080, 1920
CX = W / 2
SAFE_TOP, SAFE_BOT = 250, 1560            # Reels UI covers the top ~220 px and bottom ~360 px
ST = M.ST
ls, phrases, ease = M.ls, M.phrases, M.ease
BLUE, WHITE, ORNG, RED, GREEN = M.BLUE, M.WHITE, M.ORNG, M.RED, M.GREEN

_rng = np.random.default_rng(2001)
_st = np.zeros((H, W, 3), np.uint8)
for _ in range(700):
    y, x, b = _rng.integers(0, H), _rng.integers(0, W), int(_rng.uniform(50, 230))
    _st[y, x] = b
STARS = Image.fromarray(_st)
_YY, _XX = np.mgrid[0:H, 0:W].astype(np.float32)


def glare(img, xy, s=1.0):
    d2 = (_XX - xy[0]) ** 2 + (_YY - xy[1]) ** 2
    bloom = 255 * s * (np.exp(-d2 / (2 * 30 ** 2)) + 0.35 * np.exp(-d2 / (2 * 130 ** 2)))
    streak = 255 * 0.25 * s * np.exp(-((_YY - xy[1]) ** 2) / 8) * np.exp(-np.abs(_XX - xy[0]) / 380)
    a = np.asarray(img).astype(np.float32) + (bloom + streak)[..., None] * np.array([1, .97, .9], np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def canvas(stars=True):
    return STARS.copy() if stars else Image.new("RGB", (W, H))


def paste_band(img, band, cy):
    img.paste(band.convert("RGB"), (0, int(cy - band.size[1] / 2)))


def plate_band(stem, t, dur, z0=1.0, z1=1.07, dx=0.0, raw=False):
    src = M.raw_plate(stem) if raw else M.plate(stem)
    if src is None:
        return None
    k = ease(t / max(0.1, dur))
    z = z0 + (z1 - z0) * k
    w, h = src.size
    cw, ch = w / z, h / z
    cx = w / 2 + dx * w * (k - 0.5)
    crop = src.crop((int(cx - cw / 2), int(h / 2 - ch / 2), int(cx + cw / 2), int(h / 2 + ch / 2)))
    return crop.resize((W, int(W * h / w)), Image.LANCZOS)


# ---------------------------------------------------------------- the sunrise (open / close)

def sunrise(t, dur, start=0.0):
    img = canvas()
    earth = M.raw_plate("2001_plate5_earth_v2")
    k = ease(start + (1 - start) * t / dur)
    R = 430
    ey = H + 330 - 700 * k
    if earth is not None:
        e = earth.resize((2 * R + 70, 2 * R + 70), Image.LANCZOS)
        m = Image.new("L", e.size, 0)
        ImageDraw.Draw(m).ellipse([35, 35, 35 + 2 * R, 35 + 2 * R], fill=255)
        img.paste(e, (int(CX - R - 35), int(ey - R - 35)), m)
    d = ImageDraw.Draw(img)
    ly = H - 180 + 120 * (1 - k)
    d.ellipse([-1500, ly, W + 1500, ly + 3600], fill=(6, 6, 7))
    d.arc([-1500, ly, W + 1500, ly + 3600], 262, 278, fill=(95, 95, 100), width=3)
    sk = ease((k - 0.45) / 0.55)
    if sk > 0:
        img = glare(img, (CX + 60, ey - R * (0.92 + 0.28 * sk)), 1.35 * sk)
    return img


# ---------------------------------------------------------------- one-point-perspective rooms

VP = (CX, 880)
F = 560


def proj(x, y, z):
    return (VP[0] + x * F / z, VP[1] - y * F / z)


def room(t, speed, palette, screens=(), zfar=14.0, rib=0.6, lights=True):
    """A corridor built from receding wall panels; the camera dollies forward at `speed` units/s."""
    img = Image.new("RGB", (W, H), palette["far"])
    d = ImageDraw.Draw(img)
    hw, hh = 1.0, 1.45
    off = (t * speed) % rib
    zs = [0.35 + i * rib - off for i in range(int(zfar / rib) + 2)]
    zs = [z for z in zs if z > 0.3]
    for i in range(len(zs) - 1, 0, -1):
        z0, z1 = zs[i - 1], zs[i]
        shade = max(0.35, 1 - z1 / zfar * 0.75)
        band_i = int((zs[i] + off) / rib + 0.5)
        for side, (a, b, c, e) in {
            "L": ((-hw, -hh), (-hw, hh), (-hw, hh), (-hw, -hh)),
            "R": ((hw, -hh), (hw, hh), (hw, hh), (hw, -hh)),
            "F": ((-hw, -hh), (hw, -hh), (hw, -hh), (-hw, -hh)),
            "C": ((-hw, hh), (hw, hh), (hw, hh), (-hw, hh))}.items():
            quad = [proj(a[0], a[1], z0), proj(b[0], b[1], z0), proj(c[0], c[1], z1), proj(e[0], e[1], z1)]
            base = palette[{"L": "wall", "R": "wall", "F": "floor", "C": "ceil"}[side]]
            if side in "LR" and band_i % 2:
                base = palette.get("wall2", base)
            col = tuple(int(v * shade) for v in base)
            d.polygon(quad, fill=col)
        for q in ((-hw, -hh, -hw, hh), (hw, -hh, hw, hh)):
            p0, p1 = proj(q[0], q[1], z1), proj(q[2], q[3], z1)
            d.line([p0, p1], fill=palette["rib"], width=max(1, int(8 / z1)))
        if lights and band_i % 2 == 0:
            a, b = proj(-0.28, hh, z1), proj(0.28, hh, z0 if z0 > 0.3 else z1)
            d.rectangle([min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])], fill=palette["light"])
    quads = {}
    for name, side, z_world, y0, y1 in screens:
        z0 = z_world - t * speed
        z1 = z0 + 0.75
        if z0 < 0.45:
            continue
        x = -hw * 0.995 if side == "L" else hw * 0.995
        quads[name] = [proj(x, y1, z0), proj(x, y1, z1), proj(x, y0, z1), proj(x, y0, z0)] if side == "R" else \
            [proj(x, y1, z1), proj(x, y1, z0), proj(x, y0, z0), proj(x, y0, z1)]
    return img, quads


def corridor(t):
    pal = {"far": (30, 30, 34), "wall": (215, 215, 212), "wall2": (190, 190, 190), "floor": (190, 190, 187),
           "ceil": (150, 150, 156), "rib": (30, 30, 34), "light": (255, 255, 250)}
    screens = [("s0L", "L", 2.2, -0.5, 0.5), ("s0R", "R", 2.2, -0.5, 0.5), ("s1L", "L", 3.2, -0.5, 0.5),
               ("s1R", "R", 3.2, -0.5, 0.5), ("s2L", "L", 4.2, -0.5, 0.5), ("s2R", "R", 4.2, -0.5, 0.5)]
    img, quads = room(t, 0.07, pal, screens)
    on = phrases("corridor", 1, ["model the world", "learn from", "infer what", "adapt to", "plan,", "use knowledge"])
    order = ["s0L", "s0R", "s1L", "s1R", "s2L", "s2R"]
    for k, nm in enumerate(order):
        if nm in quads:
            lit = t >= on[k]
            p = comp.display([M.WORDS[k]] if lit else ["STANDBY"], 640, 420, fg=BLUE if lit else (70, 90, 120),
                             accent=ORNG if lit else (80, 80, 90), title=f"FUNCTION {k + 1:02d}", fs=64)
            comp.warp_into(img, p, quads[nm])
    lit = [k for k in range(6) if t >= on[k]]
    if lit:
        k = lit[-1]
        a = ease((t - on[k]) / 0.25)
        box = (240, 590, W - 240, 710)
        img.paste((0, 0, 0), box, Image.new("L", (box[2] - box[0], box[3] - box[1]), int(190 * a)))
        comp.spaced(ImageDraw.Draw(img), (CX, 650), M.WORDS[k], 64, tuple(int(245 * a) for _ in range(3)),
                    weight="500Medium")
    return img


def memory(t):
    pal = {"far": (10, 0, 0), "wall": (120, 12, 8), "wall2": (230, 90, 70), "floor": (30, 2, 2), "ceil": (25, 0, 0),
           "rib": (5, 0, 0), "light": (255, 120, 90)}
    img, _ = room(t, 0.1, pal, lights=False, rib=0.45)
    a1, a2 = ls("memory", 1), ls("memory", 2)
    if t < a1:
        p = comp.display(["NO STORED COPIES", "OF TRAINING DATA", "(fragments can", "be memorized)"], 820, 640,
                         bg=(20, 0, 0), fg=(255, 160, 140), accent=(255, 60, 40), title="OPENAI", fs=62)
    elif t < a2:
        pm = phrases("memory", 1, ["France"])[0]
        if t < pm:
            n = int(min(1, (t - a1) / 3) * 175_000_000_000)
            p = comp.display([f"{n:,}", "PARAMETERS", "nudged a little", "each step"], 820, 640, bg=(20, 0, 0),
                             fg=(255, 160, 140), accent=(255, 60, 40), title="TRAINING", fs=62)
        else:
            p = comp.display(["FRANCE -> PARIS", "JAPAN -> TOKYO", "ITALY -> ROME", "same direction"], 820, 640,
                             bg=(20, 0, 0), fg=(255, 160, 140), accent=(255, 60, 40), title="LEARNED MAP", fs=62)
    else:
        p = comp.display(["NOT A LIBRARY.", "A MAP OF", "RELATIONSHIPS."], 820, 640, bg=(20, 0, 0), fg=(255, 220, 200),
                         accent=(255, 60, 40), title="MODEL", fs=66)
    comp.warp_into(img, p, [(150, 560), (930, 600), (930, 1180), (150, 1220)])
    return img


# ---------------------------------------------------------------- monolith

def monolith(t):
    st1, q0, q3 = ls("monolith", 1), ls("monolith", 2), ls("monolith", 3)
    rk = M.raw_plate("2001_plate2_dawn_sky")
    if rk is not None and q0 + 1.6 <= t < q3 - 0.2:
        img = canvas(False)
        w, h = rk.size
        band = rk.resize((W, int(W * h / w)), Image.LANCZOS)
        k = 1 + 0.06 * ease((t - q0) / (q3 - q0))
        band = band.resize((int(band.size[0] * k), int(band.size[1] * k)), Image.LANCZOS)
        img.paste(band, (int(CX - band.size[0] / 2), int(880 - band.size[1] / 2)))
    else:
        img = canvas()
        pl = M.raw_plate("2001_plate3_moon_dig")
        if pl is not None:
            w, h = pl.size
            g = pl.crop((0, int(h * 0.36), w, h))
            gh = 760
            g = g.resize((int(g.size[0] * gh / g.size[1]), gh), Image.LANCZOS)
            img.paste(g, (int(CX - g.size[0] / 2), H - gh))
        push = 1 + 0.3 * ease(t / TL.dur["monolith"])
        mw, mh = 190 * push, 427 * push
        base = H - 560
        d = ImageDraw.Draw(img)
        img = glare(img, (CX, base - mh - 150), 0.9)
        d = ImageDraw.Draw(img)
        d.polygon([(CX - mw / 2, base), (CX + mw / 2, base), (CX + mw / 2, base - mh), (CX - mw / 2, base - mh)],
                  fill=(3, 3, 4))
        d.line([(CX + mw / 2, base), (CX + mw / 2, base - mh)], fill=(70, 70, 78), width=3)
        d.line([(CX - mw / 2, base - mh), (CX + mw / 2, base - mh)], fill=(90, 90, 98), width=2)
        d.polygon([(CX - mw / 2, base), (CX + mw / 2, base), (CX + mw * 1.6, base + 26), (CX - mw * 0.4, base + 26)],
                  fill=(8, 8, 9))
        items = ["ENCYCLOPEDIAS", "PAPERS", "NOVELS", "PHOTOGRAPHS", "MUSIC", "SOFTWARE"]
        ts = phrases("monolith", 1, ["encyclopedia", "paper", "novel", "photograph", "song", "program"])
        for k, (it, a) in enumerate(zip(items, ts)):
            if t >= a:
                al = ease((t - a) / 0.5) * (1 - ease((t - q0) / 0.6))
                comp.spaced(d, (CX, 420 + k * 62), it, 30, tuple(int(220 * al) for _ in range(3)))
    d = ImageDraw.Draw(img)
    if q0 <= t < q3 + 3:
        msg = "3 PLANKS · 1 ROPE · 1 BROKEN PULLEY"
        n = int(len(msg) * min(1, (t - q0) / 2.0))
        d.text((CX, 380), msg[:n], font=comp.jost("400Regular", 40), fill=(235, 235, 235), anchor="mm")
        if t >= q0 + 1.2:
            comp.spaced(d, (CX, 450), "LIFT THE ROCK", 36, (235, 235, 235))
    if t >= q3:
        al = ease((t - q3 - 0.3) / 0.8)
        comp.spaced(d, (CX, 1200), "NOTHING HAPPENS", 40, tuple(int(230 * al) for _ in range(3)))
    return img


# ---------------------------------------------------------------- dawn and the match cut

def bone(img, cx, cy, ang, L=300, col=(225, 215, 190)):
    d = ImageDraw.Draw(img)
    ca, sa = math.cos(ang), math.sin(ang)
    p = lambda u, v: (cx + u * ca - v * sa, cy + u * sa + v * ca)
    shaft = [p(-L / 2, -14), p(L / 2, -14), p(L / 2, 14), p(-L / 2, 14)]
    d.polygon(shaft, fill=col)
    for u in (-L / 2, L / 2):
        for v in (-18, 18):
            x, y = p(u, v)
            d.ellipse([x - 26, y - 26, x + 26, y + 26], fill=col)
    d.line([p(-L / 2, 10), p(L / 2, 10)], fill=(150, 135, 110), width=6)


def dawn(t):
    split = 3.2
    if t < split:
        img = canvas(False)
        b = plate_band("2001_plate1_dawn_plain", t, split, 1.0, 1.08)
        if b is not None:
            b = b.resize((int(b.size[0] * 1.9), int(b.size[1] * 1.9)), Image.LANCZOS)
            img.paste(b, (int(CX - b.size[0] / 2), int(900 - b.size[1] / 2)))
        return img
    tt = t - split
    a = np.linspace(0, 1, H)[:, None, None]
    top, bot = np.array([10, 14, 42], np.float32), np.array([250, 120, 50], np.float32)
    img = Image.fromarray(np.broadcast_to(top * (1 - a ** 1.6) + bot * a ** 1.6, (H, W, 3)).astype(np.uint8))
    hz = M.raw_plate("2001_plate1_dawn_plain")
    if hz is not None:
        w, h = hz.size
        strip = hz.crop((0, int(h * 0.55), w, h)).resize((W * 2, int(W * 2 * h * 0.45 / w)), Image.LANCZOS)
        img.paste(ImageEnhance.Brightness(strip).enhance(0.55), (-W // 2, H - strip.size[1] - 120))
    for k in range(4):   # slow-motion ghosts
        tk = tt - k * 0.05
        bone(img, CX + 40 * tk, 1150 - 150 * tk, -0.9 + 2.4 * tk, 300,
             tuple(int(c * (1 - 0.22 * k)) for c in (225, 215, 190)))
    return img


def station(t):
    img = canvas()
    earth = M.raw_plate("2001_plate5_earth")
    if earth is not None:
        R = 900
        e = earth.resize((2 * R + 140, 2 * R + 140), Image.LANCZOS)
        m = Image.new("L", e.size, 0)
        ImageDraw.Draw(m).ellipse([70, 70, 70 + 2 * R, 70 + 2 * R], fill=255)
        img.paste(e, (int(CX - R - 70), int(1700 - 70)), m)
    d = ImageDraw.Draw(img)
    cx, cy, R, tilt = CX + 30 * math.sin(t * 0.2), 800, 350, 0.42
    rot = -0.9 + 0.25 * t
    for k in range(10, 0, -1):   # the wheel: thick shaded ring
        rr = R + 30 - k * 6
        col = int(120 + 12 * k)
        d.ellipse([cx - rr, cy - rr * tilt, cx + rr, cy + rr * tilt], outline=(col, col, col - 4), width=8)
    for s in range(4):
        a = rot + s * math.pi / 2
        d.line([(cx, cy), (cx + R * math.cos(a), cy + R * tilt * math.sin(a))], fill=(170, 170, 168), width=14)
    for k in range(40):
        a = rot + k * 2 * math.pi / 40
        x, y = cx + (R + 12) * math.cos(a), cy + (R + 12) * tilt * math.sin(a)
        if math.sin(a) > -0.2:
            d.rectangle([x - 5, y - 3, x + 5, y + 3], fill=(255, 240, 200))
    d.ellipse([cx - 70, cy - 70 * tilt - 40, cx + 70, cy + 70 * tilt + 40], fill=(210, 210, 206), outline=(90, 90, 90), width=4)
    d.rectangle([cx - 24, cy - 170, cx + 24, cy + 170], fill=(200, 200, 196), outline=(90, 90, 90), width=3)
    return img


# ---------------------------------------------------------------- flight-deck walls (stacked for 9:16)

def wide(lines, title=None, big=False, fg=BLUE, accent=ORNG):
    if big:
        img = Image.new("RGB", (940, 330), (3, 8, 20))
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, 939, 329], outline=fg, width=6)
        y = 165 - (len(lines) - 1) * 55
        for ln, col in lines:
            d.text((470, y), ln, font=comp.jost("500Medium", 100), fill=col, anchor="mm")
            y += 110
        return img
    return comp.display(lines, 940, 330, fg=fg, accent=accent, title=title, fs=54)


def wall(panels):
    img = Image.new("RGB", (W, H), (6, 6, 8))
    d = ImageDraw.Draw(img)
    for k, p in enumerate(panels):
        y = 320 + k * 360
        d.rectangle([40, y - 18, W - 40, y + 348], fill=(40, 40, 44))
        if p is not None:
            img.paste(p.convert("RGB"), (70, y))
    return img


def readouts_station(t):
    a1, a2 = ls("station", 1), ls("station", 2)
    if t < a1 - 0.2:
        return station(t)
    if t < a2:
        caps = ["PERCEPTION", "LEARNING", "PLANNING", "REASONING", "COMMUNICATION", "DECISIONS"]
        ts = phrases("station", 1, ["perception", "learning", "planning", "reasoning", "communication", "decision"])
        lit = [c for c, a in zip(caps, ts) if t >= a]
        return wall([wide(["NIST GLOSSARY", "CNSSI 4009-2022"], "SOURCE"), wide(lit[:3] or ["..."], "AI USES"),
                     wide(lit[3:] or ["..."], "AI USES")])
    items = [("CHESS", "chess"), ("ALPHAGO", "AlphaGo"), ("SELF-DRIVING", "self-driving"), ("LANGUAGE", "language")]
    ts = phrases("station", 2, [p for _, p in items])
    lit = [c for (c, _), a in zip(items, ts) if t >= a]
    q = phrases("station", 2, ["how general"])[0]
    last = wide([("HOW GENERAL?", ORNG)], big=True) if t >= q else wide(["..."], "QUESTION")
    return wall([wide(lit[:2] or ["..."], "= AI"), wide(lit[2:] or ["..."], "= AI"), last])


def readouts_predict(t):
    a1, a2 = ls("predict", 1), ls("predict", 2)
    if t < a1:
        po, pw, pa, ps = phrases("predict", 0, ["ocean", "Wrong", "Adjust", "Sun"])
        g = [("?", WHITE)]
        if t >= po:
            g = [("OCEAN", RED), ("WRONG", RED)] if t >= pw else [("OCEAN", WHITE)]
        if t >= ps:
            g = [("SUN", GREEN), ("CORRECT", GREEN)]
        tune = wide(["ADJUSTING WEIGHTS..."] if pa <= t < ps else ["STANDBY"], "TRAINING")
        return wall([wide(["THE EARTH REVOLVES", "AROUND THE ___"], "INPUT"), wide(g, big=True), tune])
    if t < a2:
        orb = Image.new("RGB", (940, 330), (3, 8, 20))
        od = ImageDraw.Draw(orb)
        od.rectangle([0, 0, 939, 329], outline=BLUE, width=6)
        od.ellipse([170, 100, 770, 280], outline=BLUE, width=4)
        od.ellipse([430, 150, 510, 230], fill=ORNG)
        a = t * 0.8
        ex, ey = 470 + 300 * math.cos(a), 190 + 90 * math.sin(a)
        od.ellipse([ex - 26, ey - 26, ex + 26, ey + 26], fill=(40, 90, 220))
        od.line([(ex - 18, ey - 42), (ex + 18, ey + 42)], fill=WHITE, width=5)
        od.text((470, 50), "23.4° AXIAL TILT", font=comp.jost("600SemiBold", 44), fill=WHITE, anchor="mm")
        return wall([wide(["NORTHERN HEMISPHERE", "HAS SUMMER WHEN ___"], "INPUT"), orb,
                     wide(["SUNLIGHT · GEOMETRY", "ORBITS · LANGUAGE"], "NEEDS")])
    pg = phrases("predict", 2, ["Glass"])[0]
    right = wide([("BREAKS", ORNG)], big=True) if t >= pg + 2.2 else wide(["..."], "PREDICTION")
    return wall([wide(["TO PREDICT THE DATA,", "LEARN THE WORLD"], "FINDING"),
                 wide(["GLASS + FALLING", "+ CONCRETE"] if t >= pg else ["..."], "INPUT"), right])


# ---------------------------------------------------------------- the Star Gate (horizontal slit, for 9:16)

def slit_scan_v(t, hue=0):
    tex = comp._artwork()
    Th, Tw = tex.shape[:2]
    s = 2
    yy, xx = np.mgrid[0:H // s, 0:W // s].astype(np.float32) * s
    dy = np.abs(yy - 880) + 1.0
    z = 1100.0 / dy
    v = ((xx - CX) * z * 0.75 + Th / 2 + 60 * math.sin(t * 0.6)).astype(np.int32) % Th
    acc = np.zeros(yy.shape + (3,), np.float32)
    for k in range(6):
        u = ((z * 60 + (t * 30 + k * 0.9) * 55) % Tw).astype(np.int32)
        acc += tex[v, u]
    acc /= 6
    fade = np.clip(dy / 50, 0, 1)[..., None] * np.clip(1.4 - z / 60, 0, 1)[..., None]
    rot = np.roll(np.eye(3), int(hue) % 3, axis=1)
    img = Image.fromarray(np.clip(acc @ rot * fade * 255, 0, 255).astype(np.uint8))
    return img.resize((W, H), Image.BILINEAR)


def stargate(t):
    a1, a2 = ls("stargate", 1), ls("stargate", 2)
    aer = [M.raw_plate(s) for s in M.AERIALS]
    aer = [a for a in aer if a is not None]
    if t >= a2 and aer:
        seg = (t - a2) / max(0.1, TL.dur["stargate"] - a2) * len(aer)
        k = min(len(aer) - 1, int(seg))
        src = aer[k]
        w, h = src.size
        z = 1.0 + 0.25 * (seg - k)
        cw = h * W / H / z
        ch = h / z
        cx = w / 2 + w * 0.12 * (seg - k - 0.5)
        crop = src.crop((int(cx - cw / 2), int(h / 2 - ch / 2), int(cx + cw / 2), int(h / 2 + ch / 2))).resize((W, H),
                                                                                                             Image.LANCZOS)
        return M.false_colour(crop, t, k)
    img = slit_scan_v(t * 1.4, hue=int(t / 2.5))
    if t >= a1:
        d = ImageDraw.Draw(img)
        steps = ["PARSE", "VARIABLES", "EQUATION", "ARITHMETIC", "CHECK"]
        ts = phrases("stargate", 1, ["parsing", "variables", "equation", "arithmetic", "checking"])
        for k, (sname, a) in enumerate(zip(steps, ts)):
            if t >= a:
                al = ease((t - a) / 0.3)
                comp.spaced(d, (CX, 520 + k * 110), sname, 44, tuple(int(255 * al) for _ in range(3)), weight="500Medium")
    return img


SCENES = {"open": lambda t: sunrise(t, TL.dur["open"]), "close": lambda t: sunrise(t, TL.dur["close"] - 1.0, 0.3),
          "corridor": corridor, "monolith": monolith, "dawn": dawn, "station": readouts_station, "memory": memory,
          "predict": readouts_predict, "stargate": stargate}


def subtitle(img, key, tl):
    a = TL.active(key, tl)
    if not a:
        return
    lines = textwrap.wrap(a[0], 30)[:3]
    f = comp.jost("400Regular", 46)
    y0 = 1450
    box = (70, y0 - 44, W - 70, y0 + 60 * (len(lines) - 1) + 44)
    img.paste((0, 0, 0), box, Image.new("L", (box[2] - box[0], box[3] - box[1]), 165))
    d = ImageDraw.Draw(img)
    for i, ln in enumerate(lines):
        d.text((CX, y0 + i * 60), ln, font=f, fill=(240, 240, 240), anchor="mm")


def compose(t):
    key = next((k for k, *_ in SCRIPT if ST[k] <= t < ST[k] + TL.dur[k]), SCRIPT[-1][0])
    tl = t - ST[key]
    if key.startswith("card"):
        img = Image.new("RGB", (W, H))
        a = ease(tl / 0.3) * (1 - ease((tl - TL.dur[key] + 0.3) / 0.3))
        comp.spaced(ImageDraw.Draw(img), (CX, 900), CHAPTER[key], 44, tuple(int(240 * a) for _ in range(3)))
        return img
    img = SCENES[key](tl)
    d = ImageDraw.Draw(img)
    if key in ("open", "close"):
        a = ease((tl - (1.5 if key == "open" else 1.0)) / 1.0)
        if key == "close":
            a *= 1 - ease((tl - TL.dur[key] + 1.2) / 1.0)
        comp.spaced(d, (CX, 330), "WHAT IS", 40, tuple(int(235 * a) for _ in range(3)))
        comp.spaced(d, (CX, 410), "INTELLIGENCE?", 58, tuple(int(245 * a) for _ in range(3)))
    elif CHAPTER.get(key):
        box = (180, 252, W - 180, 308)
        img.paste((0, 0, 0), box, Image.new("L", (box[2] - box[0], box[3] - box[1]), 170))
        comp.spaced(ImageDraw.Draw(img), (CX, 280), CHAPTER[key], 30, (215, 215, 215))
    subtitle(img, key, tl)
    return img


def main():
    out = os.path.join(M.ROOT, "out")
    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        pd = os.path.join(out, "preview", "2001_2d")
        os.makedirs(pd, exist_ok=True)
        for s in sys.argv[2:]:
            compose(float(s)).resize((540, 960)).save(os.path.join(pd, f"t{float(s):06.2f}.png"))
        return
    silent, wav = os.path.join(out, "_2001r_video.mp4"), os.path.join(out, "_2001r_audio.wav")
    master = os.path.join(out, "what_is_intelligence_2001_reels_master.mp4")
    n = int(round(TL.total * FPS))
    enc = subprocess.Popen([M.FF, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "17",
                            "-pix_fmt", "yuv420p", silent], stdin=subprocess.PIPE)
    for i in range(n):
        enc.stdin.write(compose(i / FPS).tobytes())
        if i % 240 == 0:
            print(f"frame {i}/{n}", flush=True)
    enc.stdin.close()
    enc.wait()
    a = M.soundtrack(int(TL.total * M.SR))
    pcm = (np.stack([a, a], 1) * 32767).astype(np.int16)
    with wave.open(wav, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(M.SR)
        w.writeframes(pcm.tobytes())
    subprocess.run([M.FF, "-y", "-loglevel", "error", "-i", silent, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a",
                    "256k", "-shortest", "-movflags", "+faststart", master], check=True)
    os.remove(silent)
    os.remove(wav)
    print("master:", master, os.path.getsize(master) // 1_000_000, "MB")


if __name__ == "__main__":
    main()

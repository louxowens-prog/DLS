#!/usr/bin/env python3
"""Assemble "What Is Intelligence?" in the style of 2001: A Space Odyssey.

Inputs: Blender frame sequences from render_all.sh (out/_2001/frames/<shot>), optional photographic
plates in video/plates/2001_plate*.{png,jpg}, narration from script.py.
Output: out/what_is_intelligence_2001.mp4 (master, CRF 16) and a compressed copy if needed.
"""
import glob
import json
import math
import os
import subprocess
import sys
import textwrap
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
import comp  # noqa: E402
import narrate  # noqa: E402
from script import CHAPTER, FPS, SCRIPT, TL, starts  # noqa: E402
import imageio_ffmpeg  # noqa: E402

FF = imageio_ffmpeg.get_ffmpeg_exe()
ROOT = os.path.join(HERE, "..")
FR = os.path.join(ROOT, "out", "_2001", "frames")
BW, BH = comp.BW, comp.BH
W, H = comp.W, comp.H
BAND_Y = (H - BH) // 2
BLUE, WHITE, ORNG, RED, GREEN = (120, 200, 255), (235, 235, 235), (255, 150, 40), (240, 60, 50), (90, 230, 140)
ST = starts()


def ls(key, i):
    return TL.lines[key][i][0]


def phrases(key, i, parts):
    return TL.phrases(key, i, parts)


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


# ---------------------------------------------------------------- sources

class Shot:
    """A rendered frame sequence, motion-interpolated to 24 fps when rendered at 12."""

    def __init__(self, name):
        self.dir = os.path.join(FR, name)
        self.ok = os.path.exists(os.path.join(self.dir, "meta.json"))
        if not self.ok:
            return
        self.meta = json.load(open(os.path.join(self.dir, "meta.json")))
        src_fps = self.meta["fps"]
        self.seq = self.dir
        if src_fps != FPS:
            self.seq = self.dir + "_24"
            if not os.path.exists(os.path.join(self.seq, "done")):
                os.makedirs(self.seq, exist_ok=True)
                subprocess.run([FF, "-y", "-loglevel", "error", "-framerate", str(src_fps), "-i",
                                os.path.join(self.dir, "%05d.png"), "-vf",
                                f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1",
                                os.path.join(self.seq, "%05d.png")], check=True)
                open(os.path.join(self.seq, "done"), "w").close()
        self.n = len(glob.glob(os.path.join(self.seq, "*.png")))
        self.ratio = src_fps / FPS

    def frame(self, t):
        i = min(self.n - 1, max(0, int(t * FPS)))
        return Image.open(os.path.join(self.seq, f"{i:05d}.png"))

    def screens(self, t):
        sc = self.meta["screens"]
        x = min(len(sc) - 1.001, max(0.0, t * FPS * self.ratio))
        a, b = sc[int(x)], sc[int(x) + 1]
        f = x - int(x)
        return {k: [(a[k][j][0] * (1 - f) + b[k][j][0] * f, a[k][j][1] * (1 - f) + b[k][j][1] * f) for j in range(4)]
                for k in a}


SHOTS = {}


def shot(name):
    if name not in SHOTS:
        SHOTS[name] = Shot(name)
    return SHOTS[name]


_plates = {}


def plate(stem):
    """Best available version of a plate (highest _vN wins), cropped to 2.20:1 at band size, or None."""
    if stem not in _plates:
        files = sorted(glob.glob(os.path.join(ROOT, "plates", f"{stem}*.*")) +
                       glob.glob(os.path.join(ROOT, f"{stem}*.*")))
        img = None
        if files:
            pick = sorted(files, key=lambda f: (("_v" in f), f))[-1]
            img = Image.open(pick).convert("RGB")
            w, h = img.size
            tw = min(w, int(h * BW / BH))
            th = int(tw * BH / BW)
            img = img.crop(((w - tw) // 2, (h - th) // 2, (w - tw) // 2 + tw, (h - th) // 2 + th))
        _plates[stem] = img
    return _plates[stem]


def kenburns(img, t, dur, z0=1.0, z1=1.08, dx=0.0):
    """Slow push on a photographic plate (the film's front-projection stills barely move)."""
    k = ease(t / max(0.1, dur))
    z = z0 + (z1 - z0) * k
    w, h = img.size
    cw, ch = w / z, h / z
    cx = w / 2 + dx * w * (k - 0.5)
    return img.crop((int(cx - cw / 2), int(h / 2 - ch / 2), int(cx + cw / 2), int(h / 2 + ch / 2))).resize((BW, BH),
                                                                                                          Image.LANCZOS)


def brightest(img):
    a = np.asarray(img.convert("L"))
    y, x = np.unravel_index(np.argmax(a), a.shape)
    return (x, y) if a[y, x] > 240 else None


# ---------------------------------------------------------------- flight-deck readouts

def readout_wall(panels, t):
    """Three bezelled screens side by side, symmetric, like the Discovery's flight-deck wall."""
    band = Image.new("RGB", (BW, BH), (6, 6, 8))
    d = ImageDraw.Draw(band)
    for x0 in (20, 373, 726):
        d.rectangle([x0, 40, x0 + 334, 450], fill=(40, 40, 44))
    for k, p in enumerate(panels):
        if p is not None:
            band.paste(p.resize((310, 386), Image.LANCZOS).convert("RGB"), (32 + k * 353, 52))
    return band


def panel(lines, title=None, fg=BLUE, accent=ORNG, bg=(3, 8, 20), size=(620, 772), big=False):
    img = comp.display(lines, size[0], size[1], bg=bg, fg=fg, accent=accent, title=title) if not big else None
    if big:
        img = Image.new("RGBA", size, bg + (255,))
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, size[0] - 1, size[1] - 1], outline=fg, width=6)
        if title:
            d.rectangle([0, 0, size[0], 90], fill=accent)
            d.text((30, 45), title, font=comp.jost("600SemiBold", 48), fill=(10, 10, 16), anchor="lm")
        y = size[1] / 2 - (len(lines) - 1) * 60
        for ln, col in lines:
            d.text((size[0] / 2, y), ln, font=comp.jost("500Medium", 96), fill=col, anchor="mm")
            y += 130
    return img


def bars(t, n=6, fg=BLUE, seed=0):
    img = Image.new("RGBA", (620, 772), (3, 8, 20, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 619, 771], outline=fg, width=6)
    for k in range(n):
        v = 0.5 + 0.45 * math.sin(t * (1.3 + k * 0.4) + seed + k)
        d.rectangle([60 + k * 90, 700 - 600 * v, 120 + k * 90, 700], fill=fg if k % 2 else ORNG)
    return img


def orbit_diagram(t):
    img = Image.new("RGBA", (620, 772), (3, 8, 20, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 619, 771], outline=BLUE, width=6)
    cx, cy = 310, 400
    d.ellipse([cx - 250, cy - 120, cx + 250, cy + 120], outline=BLUE, width=4)
    d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=ORNG)
    a = t * 0.8
    ex, ey = cx + 250 * math.cos(a), cy + 120 * math.sin(a)
    d.ellipse([ex - 26, ey - 26, ex + 26, ey + 26], fill=(40, 90, 220))
    d.line([(ex - 20, ey - 45), (ex + 20, ey + 45)], fill=WHITE, width=5)
    d.text((310, 60), "23.4° TILT", font=comp.jost("600SemiBold", 48), fill=WHITE, anchor="mm")
    return img


# ---------------------------------------------------------------- scenes (each returns the band image)

def sc_open(t):
    s = shot("open")
    if not s.ok:
        return Image.new("RGB", (BW, BH))
    f = s.frame(t)
    b = comp.over_stars(f.convert("RGBA"))
    p = brightest(f.convert("RGB"))
    return comp.glare(b, p, 1.0) if p else b


def sc_close(t):
    s = shot("close")
    if not s.ok:
        return sc_open(t)
    f = s.frame(t)
    b = comp.over_stars(f.convert("RGBA"))
    p = brightest(f.convert("RGB"))
    return comp.glare(b, p, 1.0) if p else b


WORDS = ["MODEL", "LEARN", "INFER", "ADAPT", "PLAN", "ACT"]


def sc_corridor(t):
    s = shot("corridor")
    b = s.frame(t).convert("RGB") if s.ok else Image.new("RGB", (BW, BH), (200, 200, 200))
    on = phrases("corridor", 1, ["model the world", "learn from", "infer what", "adapt to", "plan,", "use knowledge"])
    if s.ok:
        names = sorted(s.screens(t).keys())
        quads = s.screens(t)
        order = ["scr0L", "scr0R", "scr1L", "scr1R", "scr2L", "scr2R"]
        for k, nm in enumerate(order):
            if nm not in quads:
                continue
            lit = t >= on[k]
            p = comp.display([WORDS[k]] if lit else ["STANDBY"], 640, 420,
                             fg=BLUE if lit else (60, 80, 110), accent=ORNG if lit else (70, 70, 80),
                             title=f"FUNCTION {k + 1:02d}")
            comp.warp_into(b, p, quads[nm])
    return b


def sc_monolith(t):
    st1 = ls("monolith", 1)
    pl = plate("2001_plate3_moon_dig")
    if t < st1 and pl is not None:
        return kenburns(pl, t, st1, 1.0, 1.1)
    s = shot("monolith")
    tt = t - (st1 if pl is not None else 0)
    b = comp.over_stars(s.frame(tt).convert("RGBA")) if s.ok else Image.new("RGB", (BW, BH))
    d = ImageDraw.Draw(b)
    items = ["ENCYCLOPEDIAS", "PAPERS", "NOVELS", "PHOTOGRAPHS", "MUSIC", "SOFTWARE"]
    ts = phrases("monolith", 1, ["encyclopedia", "paper", "novel", "photograph", "song", "program"])
    for k, (it, a) in enumerate(zip(items, ts)):
        if t >= a:
            al = ease((t - a) / 0.6) * (1 - ease((t - ls("monolith", 2)) / 0.6))
            d.text((40, 40 + k * 34), it, font=comp.jost("300Light", 26), fill=tuple(int(210 * al) for _ in range(3)))
    q0, q3 = ls("monolith", 2), ls("monolith", 3)
    if q0 <= t < q3 + 3:
        msg = "3 PLANKS  ·  1 ROPE  ·  1 BROKEN PULLEY  ·  LIFT THE ROCK"
        n = int(len(msg) * min(1, (t - q0) / 2.5))
        d.text((BW / 2, 30), msg[:n], font=comp.jost("400Regular", 26), fill=(230, 230, 230), anchor="mm")
    if t >= q3:
        al = ease((t - q3 - 0.3) / 0.8)
        comp.spaced(d, (BW / 2, BH - 34), "NOTHING HAPPENS", 26, tuple(int(220 * al) for _ in range(3)))
    return b


def sky_fallback():
    a = np.linspace(0, 1, BH)[:, None, None]
    top, bot = np.array([12, 16, 40]), np.array([255, 120, 40])
    return Image.fromarray(np.broadcast_to(top * (1 - a) + bot * a, (BH, BW, 3)).astype(np.uint8))


def sc_dawn(t):
    pl1 = plate("2001_plate1_dawn_plain")
    split = 3.2 if pl1 is not None else 0
    if t < split:
        return kenburns(pl1, t, split, 1.0, 1.06)
    sky = plate("2001_plate2_dawn_sky") or sky_fallback()
    b = kenburns(sky, t - split, 7, 1.0, 1.03)
    s = shot("dawn")
    if s.ok:
        f = s.frame(t - split).convert("RGBA")
        b.paste(f, (0, 0), f)
    return b


def sc_station(t):
    a1, a2 = ls("station", 1), ls("station", 2)
    s = shot("station")
    if t < a1 - 0.2:
        return comp.over_stars(s.frame(t).convert("RGBA")) if s.ok else Image.new("RGB", (BW, BH))
    if t < a2:
        caps = ["PERCEPTION", "LEARNING", "PLANNING", "REASONING", "COMMUNICATION", "DECISIONS"]
        ts = phrases("station", 1, ["perception", "learning", "planning", "reasoning", "communication", "decision"])
        lit = [c for c, a in zip(caps, ts) if t >= a]
        p1 = panel(["NIST", "GLOSSARY", "CNSSI", "4009-2022"], "SOURCE")
        p2 = panel(lit[:3] or ["..."], "AI SYSTEM USES")
        p3 = panel(lit[3:] or ["..."], "AI SYSTEM USES")
        return readout_wall([p1, p2, p3], t)
    items = [("CHESS", "chess"), ("ALPHAGO", "AlphaGo"), ("SELF-DRIVING", "self-driving"), ("LANGUAGE", "language")]
    ts = phrases("station", 2, [p for _, p in items])
    lit = [f"{c}  = AI" for (c, _), a in zip(items, ts) if t >= a]
    q = phrases("station", 2, ["how general"])[0]
    p3 = panel([("HOW", WHITE), ("GENERAL?", ORNG)], None, big=True) if t >= q else bars(t, seed=2)
    return readout_wall([panel(lit[:2] or ["..."], "CLASSIFIED AS"), panel(lit[2:] or ["..."], "CLASSIFIED AS"), p3], t)


def sc_memory(t):
    s = shot("memory")
    b = s.frame(t).convert("RGB") if s.ok else Image.new("RGB", (BW, BH), (60, 0, 0))
    a1, a2 = ls("memory", 1), ls("memory", 2)
    if t < a1:
        p = comp.display(["NO STORED COPIES", "OF TRAINING DATA", "(fragments can be", "memorized)"], 700, 380,
                         bg=(20, 0, 0), fg=(255, 150, 130), accent=(255, 60, 40), title="OPENAI")
    elif t < a2:
        n = int(min(1, (t - a1) / 3) * 175_000_000_000)
        pm = phrases("memory", 1, ["France"])[0]
        lines = [f"{n:,}", "PARAMETERS"] if t < pm else ["FRANCE -> PARIS", "JAPAN -> TOKYO", "ITALY -> ROME",
                                                         "same direction"]
        p = comp.display(lines, 700, 380, bg=(20, 0, 0), fg=(255, 150, 130), accent=(255, 60, 40),
                         title="TRAINING" if t < pm else "LEARNED RELATIONSHIPS")
    else:
        p = comp.display(["NOT A LIBRARY.", "A MAP."], 700, 380, bg=(20, 0, 0), fg=(255, 220, 200), accent=(255, 60, 40),
                         title="MODEL")
    comp.warp_into(b, p, [(330, 95), (750, 125), (750, 330), (330, 355)])
    return b


def sc_predict(t):
    a1, a2 = ls("predict", 1), ls("predict", 2)
    if t < a1:
        po, pw, pa, ps = phrases("predict", 0, ["ocean", "Wrong", "Adjust", "Sun"])
        guess = [("?", WHITE)]
        if t >= po:
            guess = [("OCEAN", RED if t >= pw else WHITE)]
        if t >= ps:
            guess = [("SUN", GREEN)]
        p1 = panel(["THE EARTH", "REVOLVES", "AROUND", "THE ___"], "INPUT")
        p2 = panel(guess + ([("WRONG", RED)] if pw <= t < ps else []) + ([("CORRECT", GREEN)] if t >= ps else []),
                   "PREDICTION", big=True)
        p3 = bars(t * (3 if pa <= t < ps else 1), seed=5)
        return readout_wall([p1, p2, p3], t)
    if t < a2:
        return readout_wall([panel(["NORTHERN", "HEMISPHERE", "HAS SUMMER", "WHEN ___"], "INPUT"), orbit_diagram(t),
                             panel(["SUNLIGHT", "GEOMETRY", "ORBITS", "LANGUAGE"], "NEEDS")], t)
    pg = phrases("predict", 2, ["Glass"])[0]
    right = panel([("BREAKS", ORNG)], "PREDICTED", big=True) if t >= pg + 2.2 else bars(t, seed=9)
    return readout_wall([panel(["TO PREDICT", "THE DATA,", "LEARN THE", "WORLD"], "FINDING"),
                         panel(["GLASS", "+ FALLING", "+ CONCRETE"] if t >= pg else ["..."], "INPUT"), right], t)


AERIALS = ["2001_plate4_aerial_a", "2001_plate4_aerial_b", "2001_plate4_aerial_c"]


def false_colour(img, t, k):
    """The Star Gate's aerial landscapes: colour-separated, inverted and tinted."""
    a = np.asarray(img).astype(np.float32) / 255
    perm = [(2, 0, 1), (1, 2, 0), (0, 2, 1)][k % 3]
    a = a[..., list(perm)]
    a = 1 - a if k % 2 == 0 else a
    tint = np.array([[1.2, 0.5, 1.0], [0.4, 1.1, 1.3], [1.3, 0.9, 0.3]][k % 3], np.float32)
    return Image.fromarray(np.clip(a * tint * 255, 0, 255).astype(np.uint8))


def sc_stargate(t):
    a2 = ls("stargate", 2)
    aer = [plate(s) for s in AERIALS]
    aer = [a for a in aer if a is not None]
    if t >= a2 and aer:
        seg = (t - a2) / max(0.1, (TL.dur["stargate"] - a2)) * len(aer)
        k = min(len(aer) - 1, int(seg))
        img = kenburns(aer[k], seg - k, 1.0, 1.05, 1.25, dx=0.08)   # skimming low over the landscape
        return false_colour(img, t, k)
    b = comp.slit_scan(t * 1.4, hue=int(t / 2.5))
    a1 = ls("stargate", 1)
    if t >= a1:
        steps = ["PARSE", "VARIABLES", "EQUATION", "ARITHMETIC", "CHECK"]
        ts = phrases("stargate", 1, ["parsing", "variables", "equation", "arithmetic", "checking"])
        d = ImageDraw.Draw(b)
        for k, (sname, a) in enumerate(zip(steps, ts)):
            if t >= a:
                al = ease((t - a) / 0.3)
                comp.spaced(d, (BW / 2, 60 + k * 90), sname, 30, tuple(int(255 * al) for _ in range(3)),
                            weight="500Medium")
    return b


SCENES = {"open": sc_open, "corridor": sc_corridor, "monolith": sc_monolith, "dawn": sc_dawn, "station": sc_station,
          "memory": sc_memory, "predict": sc_predict, "stargate": sc_stargate, "close": sc_close}


def compose(t):
    key = None
    for k, *_ in SCRIPT:
        if ST[k] <= t < ST[k] + TL.dur[k]:
            key = k
            break
    key = key or SCRIPT[-1][0]
    tl = t - ST[key]
    out = Image.new("RGB", (W, H))
    if key.startswith("card"):
        a = ease(tl / 0.3) * (1 - ease((tl - TL.dur[key] + 0.3) / 0.3))
        band = comp.intertitle(CHAPTER[key], a)
        out.paste(band, (0, BAND_Y))
        return out
    band = SCENES[key](tl)
    out.paste(band.convert("RGB"), (0, BAND_Y))
    d = ImageDraw.Draw(out)
    title = CHAPTER.get(key)
    if key in ("open", "close"):
        a = ease((tl - (1.5 if key == "open" else 1.0)) / 1.0)
        if key == "close":
            a *= 1 - ease((tl - TL.dur[key] + 1.2) / 1.0)
        comp.spaced(d, (W / 2, BAND_Y - 120), "WHAT IS INTELLIGENCE?", 46, tuple(int(240 * a) for _ in range(3)))
    elif title:
        comp.spaced(d, (W / 2, BAND_Y - 120), title, 32, (200, 200, 200))
    return out


# ---------------------------------------------------------------- sound

SR = 44100


def _tt(d):
    return np.arange(int(d * SR)) / SR


def brass(f, d, g=1.0):
    x = _tt(d)
    y = sum(np.sin(2 * np.pi * f * k * x * (1 + 0.002 * np.sin(2 * np.pi * 5 * x))) / k ** 1.1 for k in range(1, 9))
    return y * np.minimum(1, x / 0.12) * np.minimum(1, (d - x) / 0.35) * g


def timp(f):
    x = _tt(1.4)
    return (np.sin(2 * np.pi * f * x) + 0.5 * np.sin(2 * np.pi * f * 1.5 * x)) * np.exp(-x * 2.6)


def soundtrack(n):
    out = np.zeros(n)

    def add(sig, t, g):
        i = int(t * SR)
        if 0 <= i < n:
            j = min(n, i + len(sig))
            out[i:j] += sig[: j - i] * g

    def fanfare(t0):
        """Strauss's 1896 sunrise figure (public domain): C - G - C', the chord, the timpani."""
        add(sum(brass(f, 4.0, 0.5) for f in (32.7, 65.41)) * np.minimum(1, _tt(4.0) / 1.2), t0, 0.35)
        add(brass(261.63, 0.9), t0 + 0.2, 0.22)
        add(brass(392.0, 0.9), t0 + 1.1, 0.22)
        add(brass(523.25, 1.0), t0 + 2.0, 0.24)
        add(sum(brass(f, 3.2) for f in (130.81, 261.63, 329.63, 392.0, 523.25)), t0 + 2.9, 0.12)
        for k in range(6):
            add(timp(65.41 if k % 2 == 0 else 98.0), t0 + 2.9 + k * 0.28, 0.5 - k * 0.05)

    total = n / SR
    x = np.arange(n) / SR
    rng = np.random.default_rng(1968)
    cluster = np.zeros(n)          # micropolyphonic choir: many close voices drifting
    for k in range(20):
        f0 = 196 * 2 ** (rng.uniform(-7, 9) / 12)
        drift = 1 + 0.006 * np.sin(2 * np.pi * rng.uniform(0.02, 0.06) * x + rng.uniform(0, 6))
        ph = 2 * np.pi * f0 * np.cumsum(drift) / SR
        voice = np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.2 * np.sin(3 * ph)
        cluster += voice * (0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(0.02, 0.08) * x + rng.uniform(0, 6)))
    cluster /= 20
    env = np.full(n, 0.35)
    sg0 = ST["stargate"]
    env += np.clip((x - sg0) / 8, 0, 1) * 1.1 * (x < ST["close"])          # Star Gate crescendo
    env *= np.clip((x - 5.0) / 3, 0, 1)
    h0 = ST["monolith"] + ls("monolith", 3) - 0.15                          # true silence: "Nothing happens."
    h1 = ST["monolith"] + TL.dur["monolith"] + 0.4
    env[(x >= h0) & (x < h1)] = 0
    out += cluster * env * 0.5
    for s0, s1 in ((ST["station"], ST["station"] + ls("station", 1)), (h0, h1 + 1.0)):   # spacesuit breathing
        t = s0
        while t < s1:
            d = 1.4
            xb = _tt(d)
            br = np.convolve(rng.standard_normal(len(xb)), np.ones(40) / 40, mode="same") * np.sin(np.pi * xb / d) ** 2
            add(br, t, 0.9)
            t += 3.6
    fanfare(0.0)
    fanfare(ST["close"] - 0.3)
    voice = TL.track(n, SR)
    out = narrate.duck(out, voice, SR, depth=0.5)
    out = out * 0.7 + voice * 1.7
    fade = int(2.0 * SR)
    out[-fade:] *= np.linspace(1, 0, fade)
    out = np.tanh(out * 1.05)
    return out / (np.abs(out).max() + 1e-9) * 0.9


def main():
    outdir = os.path.join(ROOT, "out")
    silent = os.path.join(outdir, "_2001_video.mp4")
    wav = os.path.join(outdir, "_2001_audio.wav")
    master = os.path.join(outdir, "what_is_intelligence_2001_master.mp4")
    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        pd = os.path.join(outdir, "preview", "2001")
        os.makedirs(pd, exist_ok=True)
        for s in sys.argv[2:]:
            compose(float(s)).resize((540, 960)).save(os.path.join(pd, f"t{float(s):06.2f}.png"))
        return
    for k in ("open", "corridor", "monolith", "dawn", "station", "memory", "close"):
        shot(k)
    n = int(round(TL.total * FPS))
    enc = subprocess.Popen([FF, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "16",
                            "-pix_fmt", "yuv420p", silent], stdin=subprocess.PIPE)
    for i in range(n):
        enc.stdin.write(compose(i / FPS).tobytes())
        if i % 240 == 0:
            print(f"frame {i}/{n}", flush=True)
    enc.stdin.close()
    enc.wait()
    a = soundtrack(int(TL.total * SR))
    pcm = (np.stack([a, a], 1) * 32767).astype(np.int16)
    with wave.open(wav, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", silent, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a",
                    "256k", "-shortest", "-movflags", "+faststart", master], check=True)
    os.remove(silent)
    os.remove(wav)
    print("master:", master, os.path.getsize(master) // 1_000_000, "MB")


if __name__ == "__main__":
    main()

"""Overlays laid over the finished picture: karaoke lyrics (songs), TV telop captions (speech), and the
full-frame variety-show chapter cards. Captions and lyrics share one band and are never on screen together:
during a song there are no captions, only lyrics."""
import math

import numpy as np
import skia

import kk
from kk import BLOOD, HOT, INK, LEMON, WHITE, W, H, paint
from script import MACH, MAMA, NAR, SONGS
from timeline import TL

BAND_Y0, BAND_Y1 = 1318, 1500           # the shared text band (clear of the Reels UI below 1540)
LYR_SIZE, CAP_SIZE, MAX_W = 58, 56, 840
WIPE = {NAR: (255, 50, 160), MAMA: (255, 130, 200), MACH: (40, 200, 255)}
TITLES = {"s1": ("STAMP IT, STAMP IT!", "the whole family"), "s2": ("99.9% IN LOVE", "a duet: Mama & the machine"),
          "s3": ("THE GARDEN DISCO", "the dead, in formation"), "s4": ("KEEP A HAND ON THE STOP", "grand finale")}


def _fit(s, fname, size, maxw):
    f = kk.font(fname, size)
    w = f.measureText(s)
    if w > maxw:
        size = size * maxw / w
        f = kk.font(fname, size)
        w = f.measureText(s)
    return f, size, w


def _wipe_frac(key, T):
    """How much of a lyric line has been sung at T (0..1, by characters, following her words)."""
    L = TL.lines[key]
    words = L["words"]
    if T <= words[0][1]:
        return 0.0
    tot = sum(len(w) + 1 for w, a, b in words)
    done = 0.0
    for w, a, b in words:
        if T >= b:
            done += len(w) + 1
        elif T > a:
            done += (len(w) + 1) * (T - a) / max(1e-3, b - a)
            break
        else:
            break
    return min(1.0, done / tot)


def song_size(sk):
    """One lettering size for a whole song (the longest line decides), so the band never changes size."""
    return min(_fit(TL.lines[l["key"]]["shown"], "rounded-900", LYR_SIZE, MAX_W)[1] for l in TL.songs[sk]["lines"])


def _lyric(c, s, x, y, align, who, frac, alpha=1.0, size=LYR_SIZE):
    f = kk.font("rounded-900", size)
    w = f.measureText(s)
    x0 = x if align == "left" else x - w
    c.drawString(s, x0, y, f, paint(INK, alpha, stroke=size * 0.34))
    c.drawString(s, x0, y, f, paint((20, 30, 120), alpha, stroke=size * 0.2))
    c.drawString(s, x0, y, f, paint(WHITE, alpha))
    if frac > 0:
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(x0 - 20, y - size * 1.2, x0 + w * frac, y + size * 0.5))
        c.drawString(s, x0, y, f, paint(INK, alpha, stroke=size * 0.34))
        c.drawString(s, x0, y, f, paint(WHITE, alpha, stroke=size * 0.2))
        c.drawString(s, x0, y, f, paint(WIPE[who], alpha))
        c.restore()
    kk.reg(x0, y - size * 0.8, x0 + w, y + size * 0.25, "lyric")


def karaoke(arr, T):
    sk = TL.song_at(T)
    if sk is None:
        return
    S = TL.songs[sk]
    lines = S["lines"]
    c = skia.Surface(arr).getCanvas()
    band = skia.Rect.MakeLTRB(0, BAND_Y0 - 6, W, BAND_Y1 + 20)                  # a soft dark band behind the lyrics
    c.drawRect(band, paint(shader=kk.lin((0, BAND_Y0 - 30), (0, BAND_Y1 + 30), [(10, 0, 30, 0.0), (10, 0, 30, 0.72), (10, 0, 30, 0.0)])))
    starts = [TL.lines[l["key"]]["start"] for l in lines]
    i = 0
    for j, st in enumerate(starts):
        if T >= st - 0.6:
            i = j
    rows = {}
    rows[i % 2] = (i, _wipe_frac(lines[i]["key"], T))
    if i + 1 < len(lines):
        rows[(i + 1) % 2] = (i + 1, 0.0)
    elif i > 0 and T < TL.lines[lines[i]["key"]]["end"] + 0.3:
        rows[(i + 1) % 2] = (i - 1, 1.0)
    for r, (j, fr) in rows.items():
        key = lines[j]["key"]
        L = TL.lines[key]
        y = 1392 if r == 0 else 1476
        _lyric(c, L["shown"], 90 if r == 0 else 940, y, "left" if r == 0 else "right", L["who"], fr, size=SIZES[sk])
    if T < starts[0]:                                                          # the count-in dots
        n = int(max(0, starts[0] - T) / S["beat"]) + 1
        for k in range(min(4, n)):
            c.drawCircle(110 + k * 44, 1318, 13, paint(WIPE[TL.lines[lines[0]["key"]]["who"]]))
            c.drawCircle(110 + k * 44, 1318, 13, paint(INK, stroke=4))
    t_in = T - S["start"]
    if t_in < 2.4:                                                             # the song title, karaoke-video style
        title, sub = TITLES[sk]
        a = min(1.0, t_in / 0.2) * min(1.0, (2.4 - t_in) / 0.3)
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(60, 240, 760, 372), 18, 18), paint((20, 10, 60), 0.72 * a))
        kk.text(c, "♪ " + title, 90, 305, 48, "mochiy-400", LEMON, align="left", tag="songtitle", a=a, outline=INK, ow=8)
        kk.text(c, sub, 96, 352, 30, "rounded-800", WHITE, align="left", tag="songtitle", a=a)


SIZES = {sk: song_size(sk) for sk in TL.songs}


def _caps():
    return TL.captions()


CAPS = _caps()


def telop(arr, T, horror=False, oncard=False):
    cap = next((c for c in CAPS if c[0] <= T < c[1]), None)
    if not cap or TL.song_at(T) is not None or oncard:
        return
    t0, t1, s, key = cap
    f = kk.font("rounded-900", CAP_SIZE)
    lines = kk.wrap_balanced(s, f, MAX_W)
    size = CAP_SIZE
    if len(lines) > 2:
        size = CAP_SIZE * 0.86
        f = kk.font("rounded-900", size)
        lines = kk.wrap_balanced(s, f, MAX_W)
    k = kk.pop(T, t0, 0.16, 0.12)
    c = skia.Surface(arr).getCanvas()
    lh = size * 1.2
    y = 1478 - lh * (len(lines) - 1)
    fill, edge = ((255, 236, 50), BLOOD) if horror else (WHITE, HOT)
    c.save()
    c.translate(510, y - size * 0.3)
    c.scale(k, k)
    c.translate(-510, -(y - size * 0.3))
    for ln in lines:
        kk.text(c, ln, 510, y, size, "rounded-900", fill, tag="caption", outline=edge, ow=size * 0.24, outline2=INK, ow2=size * 0.42)
        y += lh
    c.restore()


def chapter(T, t, n, title, sub="A FAMILY MUSICAL", plate=True):
    """A full-frame variety-show chapter card: spinning sunburst, chrome CHAPTER n, the title in pop lettering.
    plate=False: the card has popped off (the star wipe out of it), leaving only the sunburst."""
    st = kk.Stage()
    c = st.c
    cols = [(kk.HOT, kk.LEMON), (kk.SKY, kk.MINT), (kk.ORANGE, kk.LEMON), (kk.LILAC, kk.PINK), (kk.GRASS, kk.LEMON),
            (kk.HOT, kk.SKY)][n % 6]
    kk.starburst(c, W / 2, 800, t, cols)
    if not plate:
        return st.arr
    k = kk.pop(t, 0.0, 0.3, 0.35)
    c.save()
    c.translate(W / 2, 800)
    c.scale(k, k)
    c.translate(-W / 2, -800)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(90, 520, 990, 1120), 60, 60), paint(WHITE))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(90, 520, 990, 1120), 60, 60), paint(INK, stroke=14))
    kk.text(c, "✿ " + sub + " ✿", W / 2, 600, 40, "rounded-900", kk.HOT, tag="card")
    label = f"CHAPTER {n}"
    kk.chrome_text(c, label, W / 2, 760, 118, t, max_w=820, tag="card")
    lines = title.split("|")
    for j, ln in enumerate(lines):
        kk.text(c, ln, W / 2, 900 + j * 96, 84 if len(lines) == 1 else 72, "mochiy-400", kk.SKY if n % 2 else kk.HOT,
                tag="card", outline=INK, ow=12)
    c.restore()
    for i in range(6):
        a = i * math.pi / 3 + t * 1.2
        kk.cg_star(c, W / 2 + 470 * math.cos(a), 820 + 560 * math.sin(a), 56, t, seed=i,
                   color=[kk.LEMON, kk.HOT, kk.MINT, kk.LILAC, kk.ORANGE, kk.SKY][i])
    kk.flare(c, 860, 380, t, 0.8)
    return st.arr


def slam(c, s, x, y, size, T, t0, color=kk.LEMON, edge=kk.HOT, sub=None, tag="slam", plate=True, max_w=660):
    """A big number slammed onto the screen on a jagged plate, TV-telop style. The plate always stays inside the
    frame (its spikes included, even at the top of the pop)."""
    k = kk.pop(T, t0, 0.18, 0.12)
    if k <= 0:
        return
    f = kk.font("dela-400", size)
    w = f.measureText(s)
    if w > max_w:
        size *= max_w / w
        w = max_w
    c.save()
    c.translate(x, y)
    c.scale(k, k)
    c.rotate(-3)
    if plate:
        room = (min(x, W - x) - 24) / 1.12                              # 1.12 = the pop's overshoot
        rx = min(max(w * 0.6 + 50, size * 1.05), room)
        kk.burst_plate(c, 0, -size * 0.25, rx, T, color, edge, ry=size * 1.15)
    kk.chrome_text(c, s, 0, 0, size, 0, tag=tag, face=((255, 255, 255), (255, 80, 120), (160, 0, 40)), depth=8)
    if sub:
        kk.text(c, sub, 0, size * 0.62 + 40, 40, "rounded-900", INK, tag=tag + "_sub", outline=WHITE, ow=10)
    c.restore()

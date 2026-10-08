"""Overlays laid over the finished (filmed) picture: sing-along lyrics with a colour wipe during the songs, and
captions for the speech. Captions and lyrics share one band and are never on screen together: during a song there
are no captions, only lyrics. Lettering in a 1971 face: a soft, fat serif, cream on warm brown."""
import math

import numpy as np
import skia

import draw as kk
from draw import CREAM, GOLD, GOLD2, INK, WHITE, W, H, paint
from script import HOST, NAR, SONGS, WORKERS
from timeline import TL

BAND_Y0, BAND_Y1 = 1318, 1500           # the shared text band (clear of the Reels UI below 1540)
LYR_SIZE, CAP_SIZE, MAX_W = 58, 56, 840
WIPE = {NAR: GOLD2, HOST: (255, 190, 90), WORKERS: (140, 235, 200)}
TITLES = {"s1": ("STEP INSIDE", "the host's song"), "w1": ("THE WORKERS' SONG", "for the copier"),
          "w2": ("THE WORKERS' SONG", "for the believer"), "w3": ("THE WORKERS' SONG", "for the yes-man"),
          "w4": ("THE WORKERS' SONG", "for the rusher")}


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
    return min(_fit(TL.lines[l["key"]]["shown"], "fraunces-900", LYR_SIZE, MAX_W)[1] for l in TL.songs[sk]["lines"])


def _lyric(c, s, x, y, align, who, frac, alpha=1.0, size=LYR_SIZE):
    f = kk.font("fraunces-900", size)
    w = f.measureText(s)
    x0 = x if align == "left" else x - w
    c.drawString(s, x0, y, f, paint(INK, alpha, stroke=size * 0.3))
    c.drawString(s, x0, y, f, paint(CREAM, alpha))
    if frac > 0:
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(x0 - 20, y - size * 1.2, x0 + w * frac, y + size * 0.5))
        c.drawString(s, x0, y, f, paint(INK, alpha, stroke=size * 0.3))
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
    c.drawRect(band, paint(shader=kk.lin((0, BAND_Y0 - 30), (0, BAND_Y1 + 30), [(30, 16, 8, 0.0), (30, 16, 8, 0.7), (30, 16, 8, 0.0)])))
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
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(60, 240, 760, 372), 18, 18), paint((40, 22, 10), 0.72 * a))
        kk.text(c, title, 90, 305, 48, "fraunces-900", GOLD2, align="left", tag="songtitle", a=a, outline=INK, ow=8)
        kk.text(c, sub, 96, 352, 30, "oldstandard-700", CREAM, align="left", tag="songtitle", a=a)


SIZES = {sk: song_size(sk) for sk in TL.songs}


def _caps():
    return TL.captions()


CAPS = _caps()


def telop(arr, T, horror=False, oncard=False):
    cap = next((c for c in CAPS if c[0] <= T < c[1]), None)
    if not cap or TL.song_at(T) is not None or oncard:
        return
    t0, t1, s, key = cap
    if key in ("x3", "z1"):                                             # the same words are already big on screen
        return
    f = kk.font("fraunces-900", CAP_SIZE)
    lines = kk.wrap_balanced(s, f, MAX_W)
    size = CAP_SIZE
    if len(lines) > 2:
        size = CAP_SIZE * 0.86
        f = kk.font("fraunces-900", size)
        lines = kk.wrap_balanced(s, f, MAX_W)
    k = kk.pop(T, t0, 0.16, 0.12)
    c = skia.Surface(arr).getCanvas()
    lh = size * 1.2
    y = 1478 - lh * (len(lines) - 1)
    fill, edge = (CREAM, (120, 40, 20)) if not horror else ((255, 236, 170), (150, 20, 30))
    c.save()
    c.translate(510, y - size * 0.3)
    c.scale(k, k)
    c.translate(-510, -(y - size * 0.3))
    for ln in lines:
        kk.text(c, ln, 510, y, size, "fraunces-900", fill, tag="caption", outline=edge, ow=size * 0.18, outline2=INK, ow2=size * 0.36)
        y += lh
    c.restore()



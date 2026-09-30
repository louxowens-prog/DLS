"""Lettering printed with the film: the hand-lettered intertitles (one per room), the title card, the sing-along
lyrics with a bouncing ball, and the end card with the sources."""
import math

import skia

import draw as D
import zkit as Z
from draw import W, WHITE, ease, paint, ramp
from zkit import BLACK, CHALK

LYR_Y, LYR_X, LYR_W = 1440, 510, 860


def _border(c, T, k=1.0):
    """A 1930s title-card border: double rule, corner curls, boiling."""
    for inset, w in ((60, 8), (84, 3)):
        pts = [(inset, 250 + inset - 60), (W - inset, 250 + inset - 60), (W - inset, 1640 - inset + 60), (inset, 1640 - inset + 60)]
        c.drawPath(D.path(Z.wob(pts, 2.0, inset, T)), paint(CHALK, k, stroke=w))
    for cx, cy, sx, sy in ((100, 290, 1, 1), (W - 100, 290, -1, 1), (100, 1600, 1, -1), (W - 100, 1600, -1, -1)):
        pts = [(cx + sx * 12 * t * math.cos(t * 1.1), cy + sy * 12 * t * math.sin(t * 1.1)) for t in [i / 4 for i in range(1, 24)]]
        c.drawPath(D.smooth(pts, closed=False), paint(CHALK, k, stroke=4))


def intertitle(c, T, t0, t1, top, title, seed=0):
    """Black card, hand-lettered: 'ROOM 3' small, the room's name big (wrapped), a little pair of glasses below."""
    c.drawRect(skia.Rect.MakeWH(W, 1920), paint(BLACK))
    k = ease(ramp(T, t0, t0 + 0.15))
    _border(c, T, k)
    Z.letters(c, top, 540, 640, 64, "londrina-400", CHALK, T=T, seed=seed, tag="card", a=k, track=6, jitter=1.8)
    words = title.split(" ")
    f = D.font("londrina-900", 130)
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if f.measureText(t) <= 800 or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    size = min(130, min(130 * 820 / f.measureText(l) for l in lines))
    y = 900 - (len(lines) - 1) * size * 0.55
    for j, ln in enumerate(lines):
        Z.letters(c, ln, 540, y + j * size * 1.08, size, "londrina-900", WHITE, T=T, seed=seed + 5 + j, tag="card", a=k, jitter=2.2)
    from cast import glasses
    glasses(c, 540, 1330, 0.9, rot=6 * math.sin(T * 5), a=k)
    glasses_col = None


def title_card(c, T, t0):
    """THE SECOND LOOK, in deco capitals over the Emcee's stage; the subtitle hand-lettered under it."""
    k = ease(ramp(T, t0, t0 + 0.4))
    sc = 1 + 0.25 * (1 - k)
    c.save()
    c.translate(540, 450)
    c.scale(sc, sc)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-470, -200, 470, 272), 30, 30), paint(BLACK, 0.8 * k))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-450, -180, 450, 252), 24, 24), paint(CHALK, k, stroke=5))
    Z.letters(c, "THE SECOND", 0, -50, 120, "limelight-400", WHITE, T=T, seed=41, tag="title", a=k, jitter=1.0)
    Z.letters(c, "LOOK", 0, 90, 150, "limelight-400", WHITE, T=T, seed=42, tag="title", a=k, jitter=1.0)
    k2 = ease(ramp(T, t0 + 0.5, t0 + 0.9))
    Z.letters(c, "a medical vaudeville in five rooms", 0, 226, 48, "londrina-400", CHALK, T=T, seed=43, tag="title2", a=k2, jitter=1.2)
    c.restore()


def lyric(c, T, TL):
    """The sing-along: the current lyric line hand-lettered on a dark plate, a bouncing ball hopping word to word."""
    key = TL.song_at(T)
    if key is None:
        return
    S = TL.songs[key]
    cur = None
    for i, ln in enumerate(S["lines"]):
        L = TL.lines[ln["key"]]
        nxt = TL.lines[S["lines"][i + 1]["key"]]["start"] if i + 1 < len(S["lines"]) else S["end"]
        if L["start"] - 0.35 <= T < min(nxt - 0.35, L["end"] + 0.9):
            cur = (ln, L)
    if cur is None:
        return
    ln, L = cur
    text = L["shown"]
    chorus = L["who"] == "CHORUS"
    fname = "londrina-900"
    size = 74 if chorus else 62
    size = Z.fit(text.upper() if chorus else text, fname, size, LYR_W)
    s = text.upper() if chorus else text
    a = min(1.0, (T - (L["start"] - 0.35)) / 0.12)
    f = D.font(fname, size)
    w = f.measureText(s)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(LYR_X - w / 2 - 34, LYR_Y - size - 26, LYR_X + w / 2 + 34, LYR_Y + size * 0.45),
                                      18, 18), paint(BLACK, 0.9 * a))
    Z.letters(c, s, LYR_X, LYR_Y, size, fname, WHITE if chorus else CHALK, T=T, seed=len(s) % 97, tag="lyric", a=a, jitter=0.5,
              outline=BLACK, ow=size * 0.12)
    # the bouncing ball: word positions measured on the same line
    words = s.split(" ")
    xs, x = [], LYR_X - w / 2
    for wd in words:
        ww = f.measureText(wd)
        xs.append(x + ww / 2)
        x += ww + f.measureText(" ")
    times = [a_ for _, a_, _ in L["words"]]
    if not times or T < times[0] - 0.3 or T > L["end"] + 0.2:
        return
    j = max(0, min(len(times) - 1, sum(1 for t in times if t <= T) - 1))
    t_a = times[j]
    t_b = times[j + 1] if j + 1 < len(times) else L["end"]
    u = ramp(T, t_a, t_b)
    xa, xb = xs[min(j, len(xs) - 1)], xs[min(j + 1, len(xs) - 1)]
    bx = xa + (xb - xa) * u
    by = LYR_Y - size - 30 - 70 * math.sin(math.pi * u)
    c.drawCircle(bx, by, 17, paint(WHITE))
    c.drawCircle(bx, by, 17, paint(BLACK, stroke=4))


SOURCES = [
    "Hernström et al., Lancet Digital Health, 2025 (MASAI trial, Sweden)",
    "McDonald et al., Academic Radiology, 2015 (3-4 s per image)",
    "NLM MEDLINE citation counts (about 1 million a year)",
    "Hornbrook et al., Digestive Diseases & Sciences, 2017 (blood-count trends)",
    "Adams et al., Nature Medicine, 2022 (TREWS sepsis alerts)",
    "Tomašev et al., Nature, 2019 (kidney injury, 48 h ahead)",
    "Yao et al., Nature Medicine, 2021 (EAGLE: AI-ECG)",
    "U.S. FDA, 2018 (IDx-DR autonomous eye screening)",
    "Wong et al., JAMA Internal Medicine, 2021 (sepsis model)",
    "Daneshjou et al., Science Advances, 2022 (skin tone gap)",
    "Wallace et al., Gastroenterology, 2022 (AI colonoscopy)",
    "American Cancer Society / SEER (survival by stage)",
    "USPSTF, 2021 (colorectal screening from 45)",
]


def end_card(c, T, t0):
    c.drawRect(skia.Rect.MakeWH(W, 1920), paint(BLACK))
    k = ease(ramp(T, t0 + 0.1, t0 + 0.6))
    _border(c, T, k)
    Z.letters(c, "THE SECOND LOOK", 540, 470, 96, "limelight-400", WHITE, T=T, seed=51, tag="end", a=k, jitter=0.4)
    Z.letters(c, "a dramatization  ·  the studies are real", 540, 560, 44, "londrina-400", CHALK, T=T, seed=52, tag="end", a=k)
    Z.letters(c, "SOURCES", 540, 690, 46, "londrina-900", WHITE, T=T, seed=53, tag="end", a=k, track=4)
    for j, s in enumerate(SOURCES):
        size = Z.fit(s, "londrina-400", 34, 860)
        D.text(c, s, 540, 760 + j * 56, size, "londrina-400", (220, 218, 210), tag="end", a=k)

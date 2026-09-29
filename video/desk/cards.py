"""In-picture lettering (printed with the film): the chapter cards, the countdown, the thirteen uses, the written
aphorisms, and the end card. Everything in a restrained serif, sparse, as the film would set it."""
import skia

import draw as D
from cues import CARDS, USE_TAGS, clock_at, left_until_exam
from draw import CREAM, GOLD, GOLDL, INK, W, WHITE, ease, mix, paint, ramp


def chapter_card(c, T, i):
    """White serif on black: CHAPTER ONE, the word, and the word in Japanese in vertical script beside it."""
    num, title, jp, t0, t1 = CARDS[i]
    c.drawRect(skia.Rect.MakeWH(W, 1920), paint((0, 0, 0)))
    k = ease(ramp(T, t0 + 0.1, t0 + 0.7)) * (1 - ease(ramp(T, t1 - 0.45, t1 - 0.05)))
    if k <= 0:
        return
    if i == 0:
        D.text(c, "A  LIGHT  FOR  EVERY  DESK", 540, 560, 34, "cormorant-600", (200, 190, 170), tag="card", a=k * 0.9)
        c.drawLine(420, 600, 660, 600, paint((200, 190, 170), k * 0.5, stroke=1.5))
    D.text(c, f"CHAPTER  {num}", 450, 840, 40, "cormorant-500", (220, 214, 200), tag="card", a=k)
    D.text(c, title, 450, 1010, min(170, 170 * 640 / D.font("cormorant-600", 170).measureText(title)), "cormorant-600", WHITE, tag="card", a=k)
    c.drawLine(280, 1080, 620, 1080, paint(GOLD, k * 0.8, stroke=2))
    f = D.font("mincho-700", 92)
    for j, ch in enumerate(jp):                                        # vertical, top to bottom
        w = f.measureText(ch)
        c.drawString(ch, 880 - w / 2, 800 + j * 112, f, paint(WHITE, k * 0.92))
    D.reg(830, 720, 930, 800 + len(jp) * 112, "jp")


def countdown(c, T, a=1.0):
    """The present-day clock, top left: the time and what's left before the exam."""
    hhmm = clock_at(T)
    c.drawRect(skia.Rect.MakeLTRB(60, 236, 470, 350), paint((0, 0, 0), 0.62 * a))
    D.text(c, hhmm, 84, 300, 62, "courier-400", (236, 232, 220), align="left", tag="clock", a=a)
    D.text(c, left_until_exam(hhmm), 86, 338, 28, "courier-400", (200, 196, 186), align="left", tag="clock", a=a)


def use_tag(c, T, y=None):
    """The thirteen uses, counted as they happen: a small running counter, top right ('4 / 13' and the use)."""
    cur = [u for u in USE_TAGS if u[0] <= T < u[1]]
    if not cur:
        return
    t0, t1, n, lab = cur[-1]
    k = ease(ramp(T, t0, t0 + 0.25)) * (1 - ease(ramp(T, t1 - 0.2, t1)))
    if k <= 0:
        return
    f = D.font("cormorant-700", 36)
    size = min(36, 36 * 440 / f.measureText(lab))
    w = D.font("cormorant-700", size).measureText(lab)
    x1 = 1030
    c.drawRect(skia.Rect.MakeLTRB(x1 - w - 36, 238, x1 + 14, 350), paint((0, 0, 0), 0.62 * k))
    c.drawLine(x1 - w - 22, 346, x1, 346, paint(GOLD, k, stroke=2))
    D.text(c, f"{n} / 13", x1, 282, 34, "cormorant-700", GOLDL, align="right", tag="use", a=k)
    D.text(c, lab, x1, 332, size, "cormorant-700", CREAM, align="right", tag="use", a=k)


def aphorism(c, T, text, t0, y=820, size=76, color=CREAM, maxw=880):
    """A line from her notebook, in italic serif, faded in word by word."""
    k = ease(ramp(T, t0 - 0.1, t0 + 0.6))
    if k <= 0:
        return
    f = D.font("cormorant-500i", size)
    lines = D.wrap_balanced(text, f, maxw)
    w = max(f.measureText(l) for l in lines)                            # a dark panel behind the words (hides cords)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(540 - w / 2 - 40, y - size * 1.05, 540 + w / 2 + 40,
                                                         y + (len(lines) - 1) * size * 1.15 + size * 0.45), 18, 18),
                paint((0, 0, 0), 0.72 * k))
    for j, ln in enumerate(lines):
        D.text(c, ln, 540, y + j * size * 1.15, size, "cormorant-500i", color, tag="aph", a=k)


SOURCES = [
    "Bloom, Educational Researcher, 1984;  VanLehn, 2011",
    "Kestin et al., Scientific Reports, 2025 (Harvard physics)",
    "Bastani et al., PNAS, 2025 (about 1,000 students, Türkiye)",
    "Gallup & Walton Family Foundation teacher survey, 2025",
    "UNESCO Global Education Monitoring, 2025",
    "De Simone et al., World Bank, 2025 (Nigeria)",
]


def end_card(c, T, t0):
    c.drawRect(skia.Rect.MakeWH(W, 1920), paint((0, 0, 0)))
    k = ease(ramp(T, t0 + 0.2, t0 + 0.9))
    D.text(c, "A  LIGHT  FOR  EVERY  DESK", 540, 600, 50, "cormorant-600", WHITE, tag="end", a=k)
    c.drawLine(380, 650, 700, 650, paint(GOLD, k * 0.8, stroke=2))
    D.text(c, "a dramatization  ·  the studies are real", 540, 720, 32, "cormorant-500i", (200, 194, 180), tag="end", a=k)
    D.text(c, "SOURCES", 540, 860, 34, "cormorant-700", GOLDL, tag="end", a=k)
    for j, s in enumerate(SOURCES):
        f = D.font("cormorant-600", 32)
        size = min(32, 32 * 880 / f.measureText(s))
        D.text(c, s, 540, 930 + j * 58, size, "cormorant-600", (226, 220, 206), tag="end", a=k)

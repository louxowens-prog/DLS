#!/usr/bin/env python3
"""Render EP.2 "THE FRACTION ARC": a <2 min vertical anime-style short on
fractions, decimals, percents and ratios. Reuses the EP.1 engine in make_video.py.

    python3 make_ep2.py                  # full render -> out/the_fraction_arc.mp4
    python3 make_ep2.py --preview 3 17   # dump frames to out/preview/the_fraction_arc/
"""
import math

import make_video as E
from make_video import (BLACK, CYAN, FONT_MATH, FONT_TITLE, G, GOLD, KR, LAV, PINK, PURPLE, W, WHITE,
                        caption, cue, ease_out_back, ease_out_cubic, font, impact, kazu, mix, pop, ptext,
                        rot_text, slam, stroke_for, technique_title, text)

E.PALETTES.update({
    "frac": ((6, 14, 44), (20, 50, 100), (24, 56, 110)),
    "dec": ((0, 20, 50), (0, 70, 110), (10, 80, 120)),
    "ratio": ((40, 4, 30), (100, 16, 60), (100, 30, 76)),
})
DARK = (22, 18, 48)

# ---------------------------------------------------------------- math rows with stacked fractions


def frac_w(n, d, size):
    f = font(FONT_MATH, size * 0.72)
    return max(f.getlength(str(n)), f.getlength(str(d))) + size * 0.34


def item_w(it, size):
    return frac_w(*it, size) if isinstance(it, tuple) else font(FONT_MATH, size).getlength(it)


def item_col(it):
    if isinstance(it, tuple):
        return GOLD
    if "%" in it:
        return PINK
    if ":" in it:
        return PINK
    if "." in it:
        return CYAN
    if any(c.isdigit() for c in it) and not any(c in it for c in "×÷→="):
        return GOLD
    return WHITE


def draw_item(x, y, it, size):
    col = item_col(it)
    if isinstance(it, tuple):
        n, d = it
        w = frac_w(n, d, size)
        cx = x + w / 2
        text((cx, y - size * 0.44), str(n), size * 0.72, col, FONT_MATH)
        text((cx, y + size * 0.48), str(d), size * 0.72, col, FONT_MATH)
        lw = max(4, int(size * 0.08))
        G.draw.line([(x + size * 0.08, y), (x + w - size * 0.08, y)], fill=BLACK, width=lw + 7)
        G.draw.line([(x + size * 0.08, y), (x + w - size * 0.08, y)], fill=col, width=lw)
        return w
    f = font(FONT_MATH, size)
    G.draw.text((x, y), it, font=f, fill=col, stroke_width=stroke_for(size), stroke_fill=BLACK, anchor="lm")
    return f.getlength(it)


def mrow(t, at, y, items, answer=None, t_ans=None, size=110, until=None):
    """A row of text tokens / (num, den) fractions; optional '?' answer slot that slams in at t_ans."""
    if answer is not None:
        impact(t, t_ans + 0.1, 24, "ding")
    if t < at or (until is not None and t >= until):
        return
    gap = 0.22

    def total(sz):
        ws = [item_w(i, sz) for i in items] + ([item_w(answer, sz)] if answer is not None else [])
        return sum(ws) + sz * gap * (len(ws) - 1)

    tw = total(size)
    if tw > W - 90:
        size *= (W - 90) / tw
    size *= pop(t, at)
    if size < 8:
        return
    x = W / 2 - total(size) / 2
    for it in items:
        x += draw_item(x, y, it, size) + size * gap
    if answer is None:
        return
    slot = x + item_w(answer, size) / 2
    if t < t_ans:
        text((slot, y), "?", size * (1 + 0.12 * math.sin(t * 14)), CYAN, FONT_MATH)
    else:
        s2 = size * (2.3 - 1.3 * ease_out_cubic((t - t_ans) / 0.1))
        draw_item(slot - item_w(answer, s2) / 2, y, answer, s2)


# ---------------------------------------------------------------- visuals


def fbar(t, at, cx, y, w, h, parts, fills, fill_at=None, fill_dur=0.6, until=None, sound=True):
    """Energy bar split into `parts` segments; `fills` = [(count, color), ...] charged in order."""
    total = sum(c for c, _ in fills)
    fa = at + 0.3 if fill_at is None else fill_at
    if sound:
        for i in range(total):
            cue("pop", fa + fill_dur * i / max(1, total))
    if t < at or (until is not None and t >= until):
        return
    k = ease_out_back((t - at) / 0.3)
    ww = w * k
    if ww < 40:
        return
    x0 = cx - ww / 2
    d = G.draw
    d.rounded_rectangle([x0 + 10, y - h / 2 + 10, x0 + ww + 10, y + h / 2 + 10], 16, fill=BLACK)
    d.rounded_rectangle([x0, y - h / 2, x0 + ww, y + h / 2], 16, fill=DARK)
    prog = 0.0 if t < fa else total * ease_out_cubic((t - fa) / fill_dur)
    seg = ww / parts
    i = 0
    for count, col in fills:
        for _ in range(count):
            amt = clamp01(prog - i)
            if amt > 0:
                xa = x0 + i * seg + 5
                xb = xa + (seg - 10) * amt
                d.rectangle([xa, y - h / 2 + 7, xb, y + h / 2 - 7], fill=col)
                d.rectangle([xa, y - h / 2 + 12, xb, y - h / 2 + 22], fill=mix(col, WHITE, 0.55))
            i += 1
    for j in range(1, parts):
        xd = x0 + j * seg
        d.line([(xd, y - h / 2), (xd, y + h / 2)], fill=BLACK, width=7)
    d.rounded_rectangle([x0, y - h / 2, x0 + ww, y + h / 2], 16, outline=BLACK, width=10)
    d.rounded_rectangle([x0 + 4, y - h / 2 + 4, x0 + ww - 4, y + h / 2 - 4], 13, outline=WHITE, width=3)


def clamp01(x):
    return max(0.0, min(1.0, x))


def grid100(t, at, cx, cy, size, count, fill_at, fill_dur=1.4, until=None):
    """10x10 hundredths grid charging `count` squares."""
    if t < at or (until is not None and t >= until):
        return
    k = ease_out_back((t - at) / 0.3)
    s = size * k
    if s < 40:
        return
    x0, y0 = cx - s / 2, cy - s / 2
    c = s / 10
    d = G.draw
    d.rectangle([x0 + 10, y0 + 10, x0 + s + 10, y0 + s + 10], fill=BLACK)
    d.rectangle([x0, y0, x0 + s, y0 + s], fill=DARK)
    n = 0 if t < fill_at else round(count * ease_out_cubic((t - fill_at) / fill_dur))
    for i in range(n):
        r, q = divmod(i, 10)
        d.rectangle([x0 + q * c + 2, y0 + r * c + 2, x0 + (q + 1) * c - 2, y0 + (r + 1) * c - 2], fill=CYAN)
    for j in range(11):
        d.line([(x0 + j * c, y0), (x0 + j * c, y0 + s)], fill=BLACK, width=4)
        d.line([(x0, y0 + j * c), (x0 + s, y0 + j * c)], fill=BLACK, width=4)
    d.rectangle([x0, y0, x0 + s, y0 + s], outline=WHITE, width=5)
    if n:
        text((cx, y0 + s + 55), f"{n} / 100", 56, CYAN, FONT_MATH)


def team(t, at, members, until=None, step=0.12):
    """Pop in a row of mini Kazus: members = [(x, y, color, mood, r), ...]."""
    for i in range(len(members)):
        cue("pop", at + i * step)
    if until is not None and t >= until:
        return
    for i, (x, y, col, mood, r) in enumerate(members):
        a = at + i * step
        if t >= a:
            kazu(x, y + math.sin(t * 5 + i) * 4, col, t, r * pop(t, a), 1 if col == GOLD else -1, 0, mood)


def label(t, at, xy, s, size, col, until=None):
    """Left-anchored pop-in label."""
    if t < at or (until is not None and t >= until):
        return
    f_size = size * pop(t, at)
    if f_size >= 8:
        G.draw.text(xy, s, font=font(FONT_TITLE, f_size), fill=col, stroke_width=stroke_for(f_size),
                    stroke_fill=BLACK, anchor="lm")


# ---------------------------------------------------------------- scenes


def s_hook(t):
    E.bg("hook", t, speed=2.2)
    for i, (x, y, a) in enumerate([(110, 500, 12), (970, 470, -10), (110, 1680, -8), (970, 1700, 10)]):
        if t > 0.1 + i * 0.12:
            j = math.sin(t * 60 + i) * 5
            rot_text((x + j, y - j), "ド\nド\nド", 92, a, LAV)
    slam(t, 0.2, (W / 2, 560), "FRACTIONS", 150, GOLD, shadow=PINK)
    slam(t, 0.6, (W / 2, 725), "DECIMALS", 150, CYAN, shadow=PINK)
    slam(t, 1.0, (W / 2, 890), "RATIOS", 150, PINK, shadow=CYAN)
    ptext(t, 1.8, (W / 2, 1060), "3 forms of the SAME power.", 70, WHITE)
    impact(t, 2.7, 22)
    mrow(t, 2.6, 1260, [(1, 2), "=", "0.5", "=", "50%"], size=120)
    ptext(t, 3.7, (W / 2, 1460), "EPISODE 2 · THE FRACTION ARC", 54, CYAN)


def s_fraction(t):
    E.bg("frac", t)
    technique_title(t, "FORM 1", "FRACTIONS", GOLD)
    caption(t, 0.4, 3.2, "A fraction = PIECES of a whole.")
    fbar(t, 0.6, W / 2, 700, 860, 120, 4, [(3, GOLD)], fill_at=1.2, fill_dur=0.9, until=6.6)
    if 2.2 <= t < 6.6:
        s = 210 * pop(t, 2.2)
        if s > 8:
            draw_item(300 - frac_w(3, 4, s) / 2, 1030, (3, 4), s)
    label(t, 3.2, (430, 1030 - 0.44 * 210), "← pieces you HAVE", 50, GOLD, until=6.6)
    label(t, 4.2, (430, 1030 + 0.48 * 210), "← pieces in the WHOLE", 50, CYAN, until=6.6)
    caption(t, 3.2, 6.6, "3 of 4 pieces charged")
    # phase 2: bigger bottom = smaller pieces
    if t >= 6.6:
        for y, (n, dd), at in ((820, (1, 2), 6.7), (1040, (1, 8), 7.3)):
            if t >= at:
                s = 96 * pop(t, at)
                if s > 8:
                    draw_item(130 - frac_w(n, dd, s) / 2, y, (n, dd), s)
            fbar(t, at, 640, y, 760, 110, dd, [(1, GOLD)], fill_at=at + 0.3, fill_dur=0.3)
    caption(t, 6.6, 11.0, "BIGGER bottom = SMALLER pieces\n1/8 is WAY less than 1/2!")
    if t >= 8.2:
        rot_text((900, 1250), "!!", 120 * pop(t, 8.2, 0.2), -10, PINK)
    cue("pop", 8.2)


def s_equiv(t):
    E.bg("frac", t)
    technique_title(t, "POWER-UP", "EQUIVALENT", GOLD)
    for y, (n, d), at in ((620, (1, 2), 0.5), (780, (2, 4), 1.1), (940, (4, 8), 1.7)):
        if t >= at:
            s = 80 * pop(t, at)
            if s > 8:
                draw_item(130 - frac_w(n, d, s) / 2, y, (n, d), s)
        fbar(t, at, 640, y, 760, 100, d, [(n, GOLD)], fill_at=at + 0.25, fill_dur=0.4)
    impact(t, 2.6, 18)
    if t >= 2.6:
        k = ease_out_cubic((t - 2.6) / 0.25)
        yt, yb = 560, 560 + 440 * k
        G.draw.line([(640, yt), (640, yb)], fill=BLACK, width=14)
        G.draw.line([(640, yt), (640, yb)], fill=PINK, width=6)
        label(t, 2.7, (660, 1045), "SAME LENGTH!", 48, PINK)
    caption(t, 0.3, 2.6, "Different pieces... same amount?")
    caption(t, 2.6, 5.2, "× top AND bottom by the SAME number")
    mrow(t, 3.0, 1200, [(1, 2), "×2 →", (2, 4), "×2 →", (4, 8)], size=96)
    caption(t, 5.2, 9.0, "Go backwards to SIMPLIFY")
    mrow(t, 5.5, 1420, [(6, 8), "÷2 ="], (3, 4), 6.6, size=100)


def s_add(t):
    E.bg("add", t)
    technique_title(t, "TECHNIQUE 1", "ADD & SUBTRACT", CYAN)
    # same bottoms
    mrow(t, 0.3, 640, [(1, 4), "+", (2, 4), "="], (3, 4), 2.4, size=100, until=5.0)
    fbar(t, 0.6, W / 2, 900, 860, 120, 4, [(1, GOLD), (2, CYAN)], fill_at=1.0, fill_dur=1.0, until=5.0)
    caption(t, 0.3, 2.6, "SAME bottoms? Just add the TOPS.")
    caption(t, 2.6, 5.0, "Bottom stays — it's the SIZE\nof the pieces, not the count.")
    # different bottoms
    mrow(t, 5.0, 640, [(1, 2), "+", (1, 3), "="], (5, 6), 9.8, size=100)
    six = t >= 7.0
    fbar(t, 5.2, W / 2, 860, 800, 100, 6 if six else 2, [(3 if six else 1, GOLD)], fill_at=5.4, fill_dur=0.3)
    fbar(t, 5.5, W / 2, 1000, 800, 100, 6 if six else 3, [(2 if six else 1, CYAN)], fill_at=5.7, fill_dur=0.3)
    impact(t, 7.0, 14, "flip", 0.4)
    mrow(t, 7.4, 1180, ["=", (3, 6), "+", (2, 6)], size=90)
    fbar(t, 8.8, W / 2, 1390, 800, 110, 6, [(3, GOLD), (2, CYAN)], fill_at=9.0, fill_dur=0.7)
    caption(t, 5.0, 7.0, "DIFFERENT bottoms?! Pieces don't match...")
    caption(t, 7.0, 9.8, "Cut both into 6ths → then add")
    caption(t, 9.8, 13.0, "Match the bottoms FIRST, then add.")
    ptext(t, 11.2, (W / 2, 1530), "(Subtracting? Same moves, just minus.)", 42, WHITE)


def s_muldiv(t):
    E.bg("mul", t)
    technique_title(t, "TECHNIQUE 2", "×  and  ÷", GOLD)
    caption(t, 0.3, 3.6, "× : straight across!\ntop × top, bottom × bottom")
    mrow(t, 0.6, 640, [(2, 3), "×", (3, 4), "="], (6, 12), 1.8, size=90)
    mrow(t, 2.3, 840, [(6, 12), "simplify ="], (1, 2), 3.1, size=90)
    slam(t, 3.6, (W / 2, 1030), "KEEP · CHANGE · FLIP", 80, GOLD, shadow=PINK, strength=22)
    mrow(t, 4.4, 1220, [(1, 2), "÷", (1, 4)], size=90)
    mrow(t, 5.4, 1420, ["=", (1, 2), "×", (4, 1), "="], "2", 6.8, size=90)
    caption(t, 3.6, 6.8, "÷ ? Keep the 1st, change ÷ to ×,\nFLIP the 2nd upside down")
    caption(t, 6.8, 9.0, "Check: how many 1/4s fit in 1/2? TWO.")


def s_decimal(t):
    E.bg("dec", t)
    technique_title(t, "FORM 2", "DECIMALS & %", CYAN)
    caption(t, 0.3, 3.0, "Fraction → decimal? TOP ÷ BOTTOM.")
    mrow(t, 0.5, 640, [(3, 4), "=", "3 ÷ 4", "="], "0.75", 2.2, size=100)
    grid100(t, 3.0, W / 2, 1010, 380, 75, 3.2, until=8.6)
    caption(t, 3.0, 5.6, "0.75 = 75 hundredths\n(75 out of 100)")
    caption(t, 5.6, 8.6, "Decimal → % ? × 100\n(slide the dot 2 steps →)")
    mrow(t, 6.0, 1430, ["0.75", "× 100 ="], "75%", 7.2, size=96, until=8.6)
    rows = [((1, 2), "0.5", "50%", 8.8), ((1, 4), "0.25", "25%", 9.4),
            ((3, 4), "0.75", "75%", 10.0), ((1, 10), "0.1", "10%", 10.6)]
    for i, (fr, dec, pc, at) in enumerate(rows):
        cue("pop", at)
        mrow(t, at, 860 + i * 150, [fr, "=", dec, "=", pc], size=76)
    caption(t, 8.6, 13.0, "MEMORIZE THESE 4 → instant power")


def s_ratio(t):
    E.bg("ratio", t)
    technique_title(t, "FORM 3", "RATIOS", PINK)
    caption(t, 0.3, 3.0, "A ratio COMPARES two groups.")
    heroes = [(x, 720, GOLD, "determined", 46) for x in (140, 260, 380)]
    villains = [(x, 720, PURPLE, "determined", 46) for x in (700, 820)]
    team(t, 0.6, heroes + villains, until=11.9)
    if 0.6 <= t < 11.9:
        text((540, 720), ":", 110 * pop(t, 1.2), PINK, FONT_MATH)
    mrow(t, 1.9, 900, ["3 : 2"], size=120)
    ptext(t, 2.3, (W / 2, 1010), "heroes : villains", 46, WHITE)
    caption(t, 3.0, 6.4, "Heroes out of EVERYONE?\n3 out of (3 + 2) = 3/5")
    mrow(t, 3.4, 1200, ["heroes =", (3, 5), "="], "60%", 5.2, size=96, until=6.4)
    caption(t, 6.4, 9.6, "Scale it: × BOTH sides\nby the same number")
    mrow(t, 6.8, 1200, ["3 : 2", "=", "6 : 4", "=", "9 : 6"], size=88, until=9.6)
    caption(t, 9.6, 11.9, "9 heroes → how many villains?")
    mrow(t, 9.8, 1200, ["3 : 2", "=", "9 :"], "6", 11.8, size=110)
    big = [(70 + i * 60, 720, GOLD, "determined", 26) for i in range(9)] + \
          [(660 + i * 60, 720, PURPLE, "determined", 26) for i in range(6)]
    team(t, 11.9, big, step=0.05)
    caption(t, 11.9, 14.0, "×3 on both sides → 6 villains")


def make_q(n, items, answer, expl):
    def scene(t):
        E.bg("speed", t, speed=1.6)
        ptext(t, 0.0, (W / 2, 330), f"Q{n}/4", 84, CYAN, shadow=PINK)
        mrow(t, 0.1, 680, items, answer, 3.6, size=130)
        if 0.6 <= t < 3.6:
            left = 3.6 - t
            cx, cy, r = W / 2, 1030, 120
            G.draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BLACK, outline=(70, 70, 90), width=18)
            G.draw.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * (left % 1 or 1), fill=GOLD, width=18)
            text((cx, cy), str(math.ceil(left)), 130 * (1 + 0.25 * (1 - (left % 1))), WHITE, FONT_MATH)
        for k in range(3):
            cue("tick", 0.6 + k)
        if t >= 3.7:
            kazu(W / 2, 1030 + math.sin(t * 6) * 6, GOLD, t, KR * 1.5 * pop(t, 3.7), 1, 0, "happy")
        caption(t, 3.9, 6.4, expl, y=1300, size=52)
    return scene


def s_outro(t):
    E.bg("arena", t)
    slam(t, 0.1, (W / 2, 260), "CHEAT SHEET", 120, GOLD, shadow=PINK, strength=18)
    cards = [("+ − : match the BOTTOMS first", GOLD, 0.6),
             ("× : straight across   ÷ : keep·change·flip", CYAN, 1.3),
             ("decimal = top ÷ bottom   % = decimal × 100", PINK, 2.0),
             ("ratio a : b → a out of (a + b)", LAV, 2.7)]
    for i, (s, col, at) in enumerate(cards):
        cue("pop", at)
        if t < at:
            continue
        k = ease_out_back((t - at) / 0.3)
        y = 470 + i * 160
        x0 = W / 2 - 490 * k
        G.draw.rounded_rectangle([x0 + 10, y - 60 + 10, W - x0 + 10, y + 60 + 10], 24, fill=BLACK)
        G.draw.rounded_rectangle([x0, y - 60, W - x0, y + 60], 24, fill=(20, 16, 50), outline=col, width=7)
        text((W / 2, y), s, E.fit_size(s, 46, FONT_TITLE, 900) * k, col, FONT_TITLE)
    if t >= 3.3:
        kazu(W / 2, 1175 + math.sin(t * 5) * 6, GOLD, t, KR * 1.5 * pop(t, 3.3), 1, 0, "happy")
    slam(t, 4.0, (W / 2, 1360), "SAVE THIS for test day.", 72, WHITE, shadow=PINK, strength=14)
    ptext(t, 5.0, (W / 2, 1465), "Next: EP.3 — THE ALGEBRA ARC", 54, CYAN)
    ptext(t, 5.8, (W / 2, 1550), "Comment your speed-round score ↓", 44, WHITE)


SCENES = [
    (5.0, s_hook),
    (11.0, s_fraction),
    (9.0, s_equiv),
    (13.0, s_add),
    (9.0, s_muldiv),
    (13.0, s_decimal),
    (14.0, s_ratio),
    (2.5, E.s_speed_intro),
    (6.4, make_q(1, [(1, 5), "+", (2, 5), "="], (3, 5), "Same bottoms → add the tops")),
    (6.4, make_q(2, [(1, 2), "×", (1, 3), "="], (1, 6), "Straight across: 1×1 over 2×3")),
    (6.4, make_q(3, [(2, 5), "=", "decimal?"], "0.4", "2 ÷ 5 = 0.4  (that's 40%)")),
    (6.4, make_q(4, ["simplify  4 : 6", "="], "2 : 3", "÷2 on both sides → 2 : 3")),
    (9.5, s_outro),
]

if __name__ == "__main__":
    E.main("the_fraction_arc.mp4", SCENES)

"""Scenes 1: the hook (a study that isn't there), the title, the kinds of wrong, and why it sounds so sure."""
import math

import numpy as np
import skia

import cast
import hx
import kit
from cues import C, count
from hx import BLOOD, CREAM, GOLD, INK, MINT, PEACH, PINK, PLUM, POWDER, W, H, bez, ease, paint, path, ramp, stop
from timeline import TL

S, E, Wd = TL.s, TL.e, TL.word


def parlor_set(st, T, clock=True, cat_eyes="gold", helper=True, h_mood="sweet", h_talk=0.0, hx_=540, hy=760, hs=1.0):
    c = st.c
    kit.backdrop(st, "parlor")
    if clock:
        cast.cuckoo_clock(c, 170, 470, 0.42, T, count(T))
    cast.cat(c, 830, 1600, 0.62, T, eyes=cat_eyes)
    if helper:
        cast.helper(c, hx_, hy, hs, T, talk=h_talk, mood=h_mood, look=(0.0, 0.1))


# ------------------------------------------------------------------ 1. the hook

def s_hook(T, t, d):
    st = hx.Stage()
    parlor_set(st, T, h_talk=kit.ai_talk(T), hy=900, hs=1.05)
    kit.ai_card(st.c, "“According to the study…”", T, -1.0, y=250, size=66)
    hx.soft_focus(st.arr, 0.55)
    return st.arr


def _study(c, x, y, s, blank=0.0, T=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    with hx.figure(c) as F:
        F.rrect(-230, -300, 230, 300, 8, (252, 248, 236))
    hx.text(c, "THE STUDY", 0, -220, 58, "fell-sc-400", INK, tag="prop", a=1 - blank)
    for k in range(9):
        c.drawRect(skia.Rect.MakeLTRB(-180, -150 + k * 34, 180 - (k * 37) % 80, -140 + k * 34), paint(INK, 0.5 * (1 - blank)))
    c.drawCircle(130, 210, 50, paint((200, 40, 40), 0.8 * (1 - blank)))
    c.restore()


def s_eaten(T, t, d):
    """'The study doesn't exist': the paper burns away from the bottom and there is nothing written on it."""
    st = hx.Stage((40, 0, 10))
    c = st.c
    kit.backdrop(st, "parlor")
    k = ease(ramp(t, 0.2, d - 0.2))
    burn_y = 820 + 390 - 780 * k
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(0, 0, W, burn_y))
    _study(c, 540, 820, 1.25, blank=k, T=T)
    c.restore()
    c.drawPath(hx.path([(250, burn_y)] + [(250 + i * 36, burn_y + (18 if i % 2 else -10)) for i in range(17)] + [(830, burn_y)], closed=False),
               paint((40, 10, 10), stroke=16))
    for i in range(7):
        hx.flame(c, 280 + i * 85, burn_y + 30, 230 + 60 * math.sin(i * 1.7), T, seed=i)
    cast.cat(c, 540, 1560, 0.7, T, eyes="red", pose="hiss")
    kit.top_drips(c, T, grow=0.5 + k)
    hx.horror(st.arr, 0.85)
    return st.arr


# ------------------------------------------------------------------ 2. the title

def s_title(T, t, d):
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "sky_full", 2)
    f = hx.font("shrikhand-400", 150)
    for j, (word, y) in enumerate((("IT SOUNDS", 700), ("SO SURE", 890))):
        k = hx.pop(T, S("h3") + 0.1 + 0.35 * j, 0.25, 0.3)
        if k <= 0:
            continue
        w = f.measureText(word)
        c.save()
        c.translate(W / 2, y)
        c.scale(k, k)
        c.rotate(-4 + j * 3)
        for i, colr in enumerate(((255, 90, 30), (255, 150, 40), (255, 210, 80), (255, 120, 170))):   # 70s stacked outline
            c.drawString(word, -w / 2 + (4 - i) * 7, (4 - i) * 7, f, paint(colr))
        c.drawString(word, -w / 2, 0, f, paint(CREAM))
        hx.reg_local(c, -w / 2, -105, w / 2 + 28, 36, "title")
        c.restore()
    for i in range(9):
        a = i * 2 * math.pi / 9 + stop(T, 8)
        hx.sparkle(c, 540 + 440 * math.cos(a), 800 + 330 * math.sin(a), 30 + 12 * (i % 3), T, seed=i)
    hx.soft_focus(st.arr, 0.45)
    return st.arr


def _board(c, x, y, s, eq, T):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    with hx.figure(c) as F:
        F.rrect(-230, -110, 230, 110, 12, (40, 70, 60))
    c.drawRect(skia.Rect.MakeLTRB(-230, -110, 230, 110), paint((160, 110, 70), stroke=18))
    hx.text(c, eq, 0, 34, 96, "caveat-700", (240, 240, 230), tag="board")
    c.restore()


def s_sure(T, t, d):
    """Split screen: the same sweet face, the same sparkle, the same badge - one right, one wrong."""
    frames, texts = [], []
    for eq, seed in (("2 + 2 = 4", 0), ("2 + 2 = 5", 1)):
        n0 = len(hx.TEXT)
        st = hx.Stage()
        c = st.c
        kit.backdrop(st, "sky_full", 3 + seed)
        cast.helper(c, 540, 760, 0.8, T + seed * 0.37, talk=0.0, mood="sweet")
        _board(c, 540, 1060, 0.92, eq, T)
        kit.stamp(c, "100% SURE", 540, 1236, 40, T, Wd("h3", "sure") - 0.05, color=(40, 160, 90), rot=-6, tag="badge")
        frames.append(st.arr)
        texts.append((n0, len(hx.TEXT)))
    out = hx.split(frames, "v", gap=14, color=CREAM, texts=texts)
    hx.soft_focus(out, 0.4)
    return out


# ------------------------------------------------------------------ 3. the album: kinds of wrong

ALBUM = [("facts", 0), ("quote", 1), ("math", 2), ("court", 3), ("medical", 4), ("history", 5), ("code", 6), ("cite", 7), ("docs", 8)]
SLOTS = [(310, 480, -5), (760, 770, 4), (330, 1080, -3)]


def _album(T, t, d, page):
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "album_page", page)
    for j in range(3):
        name, i = ALBUM[page * 3 + j]
        t0 = C["items"][i] - 0.05
        k = hx.pop(T, t0, 0.16, 0.18)
        if k <= 0:
            continue
        x, y, rot = SLOTS[j]
        c.save()
        c.translate(x, y)
        c.scale(k, k)
        c.translate(-x, -y)
        hx.photo(c, kit.mini(name), x, y, 440, 330, rot=rot)
        c.restore()
    cast.cat(c, 850, 1150, 0.45, T, eyes="gold")
    for j in range(3):
        hx.sparkle(c, 120 + j * 380, 280 + (j % 2) * 700, 26, T, seed=j + page * 3)
    hx.soft_focus(st.arr, 0.3)
    return st.arr


def s_album1(T, t, d):
    return _album(T, t, d, 0)


def s_album2(T, t, d):
    return _album(T, t, d, 1)


def s_album3(T, t, d):
    return _album(T, t, d, 2)


# ------------------------------------------------------------------ 4. why so sure: the word machine

WORDS = ["THE", "STUDY", "SHOWS", "MOON", "SAYS", "CAT", "PROVES", "DOCTOR", "CHEESE", "FOUND", "YES", "LAW"]


def _machine(c, x, y, s, T, reels, spin, helper_mood="sweet"):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    with hx.figure(c) as F:
        F.rrect(-360, -260, 360, 420, 60, (255, 150, 190))
        F.rrect(-320, -120, 320, 120, 20, (255, 250, 240))
        F.rrect(-140, 300, 140, 380, 20, (200, 90, 140))
        F.stroke(path([(360, -40), (440, -40), (440, -240)], closed=False), (200, 200, 210), 22)
        F.circle(440, -250, 36, BLOOD)
    for i in range(3):
        cx = -210 + i * 210
        c.drawRect(skia.Rect.MakeLTRB(cx - 95, -110, cx + 95, 110), paint(WHITE_))
        w = reels[i] if spin[i] >= 1 else WORDS[(int(stop(T, 12) * 12) + i * 5) % len(WORDS)]
        f = hx.font("shrikhand-400", 52)
        ww = f.measureText(w)
        sc = min(1.0, 170 / ww)
        c.save()
        c.translate(cx, 20)
        c.scale(sc, sc)
        c.drawString(w, -ww / 2, 0, f, paint(PLUM))
        if spin[i] >= 1:
            hx.reg_local(c, -ww / 2, -40, ww / 2, 10, "reel")
        c.restore()
        c.drawRect(skia.Rect.MakeLTRB(cx - 95, -110, cx + 95, 110), paint(INK, stroke=6))
    c.restore()


WHITE_ = (255, 255, 255)


def s_machine(T, t, d):
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "sky_full", 6)
    _machine(c, 520, 1000, 1.0, T, ["", "", ""], [0, 0, 0])
    cast.helper(c, 520, 560, 0.72, T, talk=0.0, mood="sweet", look=(0.2, 0.4))
    hx.soft_focus(st.arr, 0.35)
    return st.arr


def s_reels(T, t, d):
    """Close on the reels: they land one by one on whatever sounds most likely."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "sky_full", 6)
    lands = [C["reels"] + 0.25, C["reels"] + 0.6, C["reels"] + 1.0]
    spin = [1 if T >= a else 0 for a in lands]
    _machine(c, 540, 820, 1.38, T, ["THE", "STUDY", "SHOWS"], spin)
    for i, a in enumerate(lands):
        if T >= a:
            hx.sparkle(c, 250 + i * 290, 560, 40, T, seed=i)
    hx.soft_focus(st.arr, 0.3)
    return st.arr


def s_ticket(T, t, d):
    """It prints its answer on a pretty ticket. Turn it over: nothing checks it."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "sky_full", 6)
    _machine(c, 540, 1180, 0.9, T, ["THE", "STUDY", "SHOWS"], [1, 1, 1])
    k = ease(ramp(t, 0.05, 0.5))
    flip = ramp(T, Wd("w1", "isn't") - 0.1, Wd("w1", "isn't") + 0.2)
    c.save()
    c.translate(540, 700 - 200 * k)
    c.scale(1 - 2 * min(flip, 0.5) if flip < 0.5 else (flip - 0.5) * 2, 1)
    with hx.figure(c) as F:
        F.rrect(-250, -130, 250, 130, 14, (255, 236, 150) if flip < 0.5 else (30, 10, 20))
    if flip < 0.5:
        hx.text(c, "FACT!", 0, 30, 110, "shrikhand-400", (40, 150, 80), tag="ticket")
    else:
        hx.scribble(c, 0, 0, 140, T, seed=4, color=BLOOD, w=8)
    c.restore()
    cast.cat(c, 880, 1640, 0.5, T, eyes="red" if flip > 0.5 else "gold")
    hx.soft_focus(st.arr, 0.3 if flip < 0.5 else 0.0)
    if flip >= 0.5:
        hx.horror(st.arr, 0.55)
    return st.arr


# ------------------------------------------------------------------ 5. graded for guessing

def _exam(c, T, graded):
    with hx.figure(c) as F:
        F.rrect(90, 300, 990, 1260, 10, (252, 250, 240))
    for y in range(380, 1250, 44):
        c.drawLine(110, y, 970, y, paint((170, 200, 240), stroke=2))
    c.drawLine(190, 300, 190, 1260, paint((240, 140, 150), stroke=3))
    hx.text(c, "QUIZ", 540, 400, 70, "fell-sc-400", INK, tag="exam")
    hx.text(c, "Who wrote the study?", 220, 510, 54, "caveat-700", INK, align="left", tag="exam")
    for j, (ans, y) in enumerate((("?", 700), ("Dr. P. Smith, 1978!", 980))):
        c.drawRect(skia.Rect.MakeLTRB(220, y - 110, 860, y + 60), paint(INK, stroke=4))
        hx.text(c, ans, 250 if j else 540, y, 70 if j else 110, "caveat-700", (40, 60, 160), align="left" if j else "center", tag="exam")
    if graded:
        kit.stamp(c, "0", 800, 700, 110, T, C["star"], color=BLOOD, rot=10, box=False, tag="grade")
        kit.stamp(c, "+1", 820, 1150, 90, T, C["star"] + 0.35, color=BLOOD, rot=-8, box=False, tag="grade")
        if T >= C["star"] + 0.35:
            hx.sparkle(c, 700, 1140, 70, T, seed=9, color=GOLD)


def s_exam(T, t, d):
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "kitchen")
    _exam(c, T, False)
    cast.helper(c, 830, 1170, 0.5, T, mood="eerie", look=(-0.8, -0.3), halo=False)
    hx.soft_focus(st.arr, 0.3)
    return st.arr


def s_grade(T, t, d):
    """Freeze frame: the teacher's red pen. Blank scores zero; a confident guess scores."""
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "kitchen")
    _exam(c, T, True)
    cast.helper(c, 830, 1170, 0.5, C["star"] - 0.1, mood="eerie", look=(-0.8, -0.3), halo=False)
    if t < 2 / 24:
        c.drawRect(skia.Rect.MakeWH(W, H), paint(CREAM, 0.7))
    hx.freeze_look(st.arr, 0.8)
    return st.arr


def s_always(T, t, d):
    st = hx.Stage()
    c = st.c
    kit.backdrop(st, "sky_full", 8)
    snap = E("w3") <= T < E("w3") + 0.2
    cast.helper(c, 540, 1060, 1.45, T, talk=kit.ai_talk(T), mood="horror" if snap else "sweet", halo=not snap)
    kit.ai_card(c, "“I always have an answer!”", T, S("w3") - 0.1, y=250, size=62, horror=snap)
    if snap:
        hx.horror(st.arr, 1.0)
    else:
        hx.soft_focus(st.arr, 0.5)
    return st.arr

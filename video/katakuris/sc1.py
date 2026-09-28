"""Scenes 1: the cold open, one little mistake, the machine, the sweet sing-along, and the flood of copies."""
import math

import numpy as np
import skia

import bg
import cast
import kit
import kk
import ov
from cues import C, ls
from kk import BLOOD, CREAM, HOT, INK, LEMON, LILAC, MINT, ORANGE, PINK, SKY, WHITE, W, H, ease, paint, path, ramp, twos
from timeline import TL

S, E, Wd = TL.s, TL.e, TL.word


# ------------------------------------------------------------------ cold open: the real case in the first two seconds

def _pile(c, T, t_start, n=70, seed=1, h0=1520):
    """Red FRAUD envelopes raining down in stop-motion and piling up over a little clay house."""
    tt = twos(T) - t_start
    rng = np.random.default_rng(seed)
    kit.clay_house(c, 540, h0, 1.0, T, seed=4)
    for i in range(n):
        t0 = i * 0.05
        age = tt - t0
        if age < 0:
            continue
        x = rng.uniform(80, 1000)
        rest = h0 + 40 - (i // 9) * 55 - rng.uniform(0, 40) - 180 * math.exp(-((x - 540) / 260) ** 2) * min(1, i / 30)
        y = min(rest, -150 + age * age * 2600)
        rot = rng.uniform(-40, 40) + (0 if y >= rest else age * 300)
        cast.envelope(c, x, y, 0.62, T, seed=i, rot=rot, label="FRAUD" if (i % 3 == 0 and y < rest - 40 and (300 < y < 330 or 680 < y < 1120)) else None)


PILE_T0 = -1.1                    # the envelopes are already raining down on the very first frame


def s_cold1(T, t, d):
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.storm())
    _pile(c, T, PILE_T0)
    ov.slam(c, "40,000", 540, 560, 170, T, 0.0, sub="FRAUD ACCUSATIONS")
    kk.red(st.arr, 0.25)
    return st.arr


def s_cold2(T, t, d):
    """It was wrong about most of them: out of nowhere, on top of the pile, the little error pops up and grins."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.storm())
    _pile(c, T, PILE_T0)
    tp = C["pop"]
    if T >= tp:
        k = kk.pop(T, tp, 0.25, 0.4)
        c.save()
        c.translate(540, 1150)
        c.scale(k, k)
        c.translate(-540, -1150)
        cast.creature(c, 540, 1150, 1.5, T, mood="grin", look=(0.0, 0.2))
        c.restore()
    kit.puff(c, 540, 1000, T - tp, 220)
    kk.red(st.arr, 0.25)
    return st.arr


# ------------------------------------------------------------------ chapter 1: one little mistake

FAM = [("grandpa", 175), ("papa", 420), ("mama", 660), ("girl", 900)]


def _family(c, T, pose="stand", s=0.55, y=1650, mood="flat", **kw):
    for i, (who, x) in enumerate(FAM):
        p = pose(i) if callable(pose) else pose
        cast.person(c, who, x, y, s, T, pose=p, mood=mood, **kw)


def s_family(T, t, d):
    st = kk.Stage()
    c = st.c
    z = 1.0 + 0.05 * t / d
    c.save()
    c.translate(540, 960)
    c.scale(z, z)
    c.translate(-540, -960)
    kit.backdrop(st, bg.inn_meadow(0))
    bg.inn_sign(c, 540, 1080, 0.8)
    _family(c, T, pose=lambda i: "wave" if (i == 2 and t < 2.4) else ("hips" if i == 1 else "stand"))
    if T >= Wd("a1", "process"):
        cast.claim_form(c, 470, 1380, 0.55, rot=-8, x_mark=False, tag="prop")
    c.restore()
    for i in range(3):
        kk.cg_star(c, 150 + i * 390, 300 + (i % 2) * 80, 44, T, seed=i, color=[LEMON, HOT, MINT][i])
    return st.arr


def s_crowsign(T, t, d):
    """'Don't ask.' Nobody moves. A clay crow lands on the sign."""
    st = kk.Stage()
    c = st.c
    c.save()
    c.translate(540, 960)
    c.scale(1.05, 1.05)
    c.translate(-540, -960)
    kit.backdrop(st, bg.inn_meadow(0))
    bg.inn_sign(c, 540, 1080, 0.8)
    _family(c, T - t, pose="stand", blink=False)
    c.restore()
    k = ease(ramp(twos(T), T - t, T - t + 0.35))
    cast.crow(c, 900 - 240 * k, 740 + 180 * k - 120 * math.sin(k * math.pi), 0.8, T, caw=1.0 if t > 0.4 else 0.0, flip=True)
    return st.arr


def s_stamp(T, t, d):
    """Grandpa's one wrong stamp."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.lobby())
    down = ramp(T, C["stamp"] - 0.15, C["stamp"] + 0.05) * (1 - ramp(T, C["stamp"] + 0.35, C["stamp"] + 0.6))
    cast.person(c, "grandpa", 430, 1500, 1.05, T, pose=(8, 0, 70 - 40 * down, 60 + 40 * down), mood="flat")
    bg.desk(c, 1250)
    marked = T >= C["stamp"] + 0.02
    cast.claim_form(c, 600, 1230, 0.85, rot=-4, x_mark=marked, tag="prop")
    cast.rubber_stamp(c, 720, 1010 + 190 * down, 1.0)
    if marked:
        ov.slam(c, "1 ERROR", 540, 520, 120, T, C["stamp"] + 0.15, color=WHITE, edge=BLOOD)
    return st.arr


def s_bow(T, t, d):
    """One apology: Grandpa bows, very low, very deadpan."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.lobby())
    bow = ease(ramp(t, 0.05, 0.45))
    cast.person(c, "grandpa", 540, 1560, 1.1, T, pose="stand", bow=bow, mood="flat")
    bg.desk(c, 1300)
    kit.tag_label(c, "SORRY!", 800, 520, 60, color=HOT)
    return st.arr


def s_book1(T, t, d):
    """Fixed by Tuesday. The guestbook, page one: one red X."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.lobby())
    cast.guestbook(c, 540, 960, 1.35, T, marks=1, rot=-3)
    k = kk.pop(T, C["tuesday"] - 0.1, 0.2, 0.3)
    if k > 0:
        c.save()
        c.translate(820, 470)
        c.scale(k, k)
        c.rotate(8)
        c.drawRect(skia.Rect.MakeLTRB(-150, -120, 150, 150), paint(WHITE))
        c.drawRect(skia.Rect.MakeLTRB(-150, -120, 150, -50), paint(BLOOD))
        kk.text(c, "TUESDAY", 0, -68, 44, "rounded-900", WHITE, tag="prop")
        kk.text(c, "FIXED!", 0, 70, 64, "mochiy-400", (40, 160, 70), tag="prop")
        c.restore()
    for i in range(4):
        kk.cg_star(c, 180 + i * 240, 1320, 36, T, seed=i + 4)
    return st.arr


# ------------------------------------------------------------------ chapter 2: the machine

def s_machine(T, t, d):
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.lobby())
    k = ease(ramp(t, 0.0, 0.9))
    x = 1400 - 860 * k
    cast.machine(c, x, 1380, 0.95, T, face="smile")
    cast.person(c, "papa", 190, 1680, 0.55, T, pose="point" if t > 0.6 else "stand")
    for i in range(6):
        a = i * math.pi / 3 + T * 1.4
        kk.cg_star(c, x + 330 * math.cos(a), 1000 + 420 * math.sin(a), 40, T, seed=i, color=[LEMON, HOT, MINT, LILAC, ORANGE, SKY][i])
    kk.flare(c, x + 150, 640, T, 0.9 * k)
    ov.slam(c, "10,000,000", 540, 470, 118, T, C["tenmil"] - 0.05, sub="CLAIMS A YEAR")
    if T >= Wd("b1", "Grandpa's"):
        kit.tag_label(c, "RULES BY GRANDPA", 560, 700, 40, color=(40, 120, 220))
    return st.arr


def _beat(sk="s1"):
    return TL.songs[sk]["beat"]


def s_song1a(T, t, d):
    """The sweet sing-along: the family and the machine dance in the meadow under the rainbow."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.meadow(1))
    b = _beat()
    hop = abs(math.sin((T - S("s1")) / b * math.pi)) * 26
    cast.machine(c, 540, 1360 - hop, 0.6, T, face="smile", stamp=hop / 26)
    for i, (who, x) in enumerate([("grandpa", 150), ("papa", 330), ("mama", 750), ("girl", 930)]):
        cast.person(c, who, x, 1640, 0.5, T, pose=cast.dance_pose(T - S("s1"), b, "kayo", i), bob=hop, mood="smile" if who == "mama" else "flat")
    for i in range(5):
        kk.cg_star(c, 120 + i * 210, 500 + 60 * math.sin(T * 2 + i), 38, T, seed=i, color=[LEMON, HOT, MINT, LILAC, ORANGE][i])
    return st.arr


def s_song1b(T, t, d):
    """Ten million claims, so quick, so bright: the machine stamps on every beat; approved claims fly out."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.meadow(1))
    b = _beat()
    ph = ((T - S("s1")) / b) % 1.0
    stamp = max(0.0, 1 - ph * 3)
    cast.machine(c, 540, 1500, 1.15, T, face="smile", stamp=stamp, slot=ph)
    n = int((T - S("s1")) / b)
    for k in range(6):
        age = ((T - S("s1")) / b - (n - k)) * b
        if age < 0:
            continue
        x = 540 + (k % 2 * 2 - 1) * (120 + age * 520)
        y = 1300 - age * 900 + age * age * 600
        c.save()
        c.translate(x, y)
        c.rotate(age * 200 * (k % 2 * 2 - 1))
        c.drawRect(skia.Rect.MakeLTRB(-70, -90, 70, 90), paint(WHITE))
        c.drawPath(path([(-35, 0), (-10, 30), (40, -35)], closed=False), paint((40, 180, 80), stroke=14))
        c.restore()
    for i in range(4):
        kk.cg_star(c, 160 + i * 250, 300, 40, T, seed=i + 3)
    return st.arr


def s_song1c(T, t, d):
    """It learned from Grandpa, line by line: a split screen - Grandpa stamps, the machine copies, beat for beat."""
    b = _beat()
    ph = ((T - S("s1")) / b) % 1.0
    down = max(0.0, 1 - ph * 3)
    halves = []
    for side in (0, 1):
        n0 = len(kk.TEXT)
        st = kk.Stage()
        c = st.c
        kit.backdrop(st, bg.lobby() if side == 0 else bg.meadow(1))
        if side == 0:
            cast.person(c, "grandpa", 470, 1500, 1.0, T, pose=(8, 0, 70 - 40 * down, 60 + 40 * down))
            bg.desk(c, 1250)
            cast.claim_form(c, 560, 1180, 0.7, rot=-4, x_mark=int((T - S("s1")) / b) % 3 == 0, tag="prop")
        else:
            cast.machine(c, 540, 1400, 0.95, T, stamp=down, slot=ph)
            cast.claim_form(c, 540, 1560, 0.6, rot=5, x_mark=int((T - S("s1")) / b) % 3 == 0, tag="prop")
        halves.append(st.arr)
    out = halves[0].copy()
    out[:, 540:] = halves[1][:, 270:810]
    out[:, :540] = halves[0][:, 270:810]
    kk.TEXT.clear()
    out[:, 532:548, :3] = (255, 60, 160)
    return out


def s_song1d(T, t, d):
    """His one mistake, ten million times: red X stamps multiply over the whole meadow while the family dances on."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.meadow(1))
    b = _beat()
    for i, (who, x) in enumerate(FAM):
        cast.person(c, who, x, 1650, 0.45, T, pose=cast.dance_pose(T - S("s1"), b, "kayo", i), mood="flat")
    n = int(2 ** min(10, 1 + t * 3.2))
    rng = np.random.default_rng(3)
    for i in range(min(n, 400)):
        x, y = rng.uniform(40, 1040), rng.uniform(240, 1300)
        s = rng.uniform(18, 46)
        c.drawLine(x - s, y - s, x + s, y + s, paint(BLOOD, stroke=s * 0.35))
        c.drawLine(x + s, y - s, x - s, y + s, paint(BLOOD, stroke=s * 0.35))
    return st.arr


# ------------------------------------------------------------------ the flood of copies (horror)

def s_flood(T, t, d):
    """The machine spews the same mistake: a stop-motion avalanche of clay claim slabs, each with a red X."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.storm())
    tt = twos(T) - (T - t)
    rng = np.random.default_rng(8)
    cast.machine(c, 540, 1180, 0.8, T, face="evil", slot=(tt * 3) % 1.0, stamp=(tt * 4) % 1.0, glow=0.7)
    for i in range(90):
        t0 = i * 0.045
        age = tt - t0
        if age < 0:
            continue
        ang = rng.uniform(-2.4, -0.7)
        sp = rng.uniform(900, 1500)
        x = 540 + math.cos(ang) * sp * age
        y = 1000 + math.sin(ang) * sp * age + 1500 * age * age
        rest = 1880 - (i % 18) * 18
        y = min(y, rest)
        kk.clay_poly(c, [(x - 60, y - 75), (x + 60, y - 75), (x + 60, y + 75), (x - 60, y + 75)], (245, 240, 225), tt, seed=i,
                     amp=4, prints=1, marks=0)
        c.drawLine(x - 35, y - 40, x + 35, y + 40, paint(BLOOD, stroke=12))
        c.drawLine(x + 35, y - 40, x - 35, y + 40, paint(BLOOD, stroke=12))
    ov.slam(c, "10,000,000 ×", 540, 480, 110, T, T - t + 0.4, color=(255, 80, 60), edge=INK, sub="THE SAME MISTAKE")
    kk.red(st.arr, 0.3)
    return st.arr


def s_graves(T, t, d):
    """Millions: the garden becomes rows of clay graves to the horizon. The family shovels, deadpan."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.garden_night())
    for row in range(7, -1, -1):
        s = 0.25 + row * 0.12
        y = 1180 + row * 90
        n = int(W / (200 * s)) + 2
        for i in range(n):
            cast.tombstone(c, (i + 0.5 * (row % 2)) * 200 * s, y, s, T, n=row * 97 + i * 13 + 1, seed=row * 10 + i, label=row > 4)
    for i, (who, x) in enumerate([("papa", 260), ("girl", 820)]):
        dig = abs(math.sin(T * 5 + i))
        hand = cast.person(c, who, x, 1700, 0.5, T, pose=(40, 60, 70 - 30 * dig, 60), mood="flat")
        if hand:
            cast.shovel(c, hand[0], hand[1], 0.6, ang=-20 + 25 * dig)
    cast.crow(c, 540, 1260, 0.6, T, caw=1.0 if t > 0.2 else 0.0)
    kk.red(st.arr, 0.2)
    return st.arr


def s_rule(T, t, d):
    """Automation multiplies everything: the top half glitters (competence), the bottom half bleeds (incompetence)."""
    st = kk.Stage()
    c = st.c
    kk.starburst(c, 540, 480, T, (kk.SKY, kk.LEMON))
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(0, 960, W, H))
    c.drawRect(skia.Rect.MakeLTRB(0, 960, W, H), paint((60, 0, 20)))
    grow = ramp(T, C["rule_wrong"] - 0.3, C["rule_wrong"] + 0.8)
    for i in range(14):
        kk.drip(c, 40 + i * 76, 960, 18, 40 + 260 * ((i * 37) % 10) / 10 * grow, BLOOD)
    c.restore()
    c.drawRect(skia.Rect.MakeLTRB(0, 950, W, 970), paint(WHITE))
    n = min(24, 2 ** int(t / 0.3))                                          # the multiplying: 1, 2, 4, 8 ... on both halves
    rng = np.random.default_rng(12)
    top = [(110 + (i % 6) * 172 + rng.uniform(-20, 20), 600 + (i // 6) * 95 + rng.uniform(-15, 15)) for i in range(24)]
    bot = [(110 + (i % 6) * 172 + rng.uniform(-20, 20), 1020 + (i // 6) * 90 + rng.uniform(-12, 12)) for i in range(24)]
    order = rng.permutation(24)
    for j in order[:n]:
        kk.cg_star(c, *top[j], 40, T, seed=int(j), color=[kk.LEMON, WHITE, kk.MINT][j % 3])
        kit.clay_x(c, *bot[j], 0.26, T, seed=int(j))
    if T >= C["rule_right"] - 0.2:
        c.drawRect(skia.Rect.MakeLTRB(0, 560, W, 940), paint((255, 255, 255), 0.35))
    if T >= C["rule_wrong"] - 0.2:
        c.drawRect(skia.Rect.MakeLTRB(0, 980, W, 1320), paint((30, 0, 10), 0.45))
    kk.chrome_text(c, "AUTOMATION", 540, 330, 96, T, max_w=900, tag="rule")
    kk.chrome_text(c, "MULTIPLIES", 540, 450, 96, T, max_w=900, tag="rule")
    k1 = kk.pop(T, C["rule_right"] - 0.2, 0.25, 0.3)
    if k1 > 0:
        c.save()
        c.translate(540, 700)
        c.scale(k1, k1)
        kk.chrome_text(c, "COMPETENCE", 0, 0, 90, T, max_w=860, tag="rule", face=((255, 255, 220), (255, 210, 60), (180, 110, 0)))
        kk.text(c, "× 10,000,000", 0, 110, 64, "dela-400", (40, 150, 60), tag="rule", outline=WHITE, ow=10)
        c.restore()
        for i in range(5):
            kk.cg_star(c, 120 + i * 210, 600 + (i % 2) * 260, 40, T, seed=i)
    k2 = kk.pop(T, C["rule_wrong"] - 0.2, 0.25, 0.3)
    if k2 > 0:
        c.save()
        c.translate(540, 1110)
        c.scale(k2, k2)
        kk.chrome_text(c, "INCOMPETENCE", 0, 0, 84, T, max_w=860, tag="rule", face=((255, 200, 200), (230, 20, 40), (90, 0, 10)))
        kk.text(c, "× 10,000,000", 0, 100, 60, "dela-400", (255, 90, 90), tag="rule", outline=INK, ow=10)
        c.restore()
    return st.arr


def s_same(T, t, d):
    """The same wrong rule hits the same kind of person: a clay conveyor of identical little people, each stamped
    with the same red X, faster and faster."""
    st = kk.Stage()
    c = st.c
    kit.backdrop(st, bg.storm())
    tt = twos(T) - (T - t)
    speed = 1 + tt * 1.2
    pos = tt * 260 * speed
    kk.clay_poly(c, [(-40, 1330), (1120, 1330), (1120, 1420), (-40, 1420)], (70, 70, 90), tt, seed=2, amp=3, prints=0)
    for k in range(12):
        c.drawCircle(((k * 100 - pos) % 1200) - 60, 1375, 22, paint((140, 140, 160)))
    stamp_x = 620
    for i in range(10):
        x = 1150 - ((pos + i * 170) % 1400)
        hit = x < stamp_x
        kk.clay_ellipse(c, x, 1250, 52, 80, (120, 170, 255), tt, seed=i % 3, prints=1, marks=1)
        kk.clay_ellipse(c, x, 1140, 44, 44, (255, 200, 160), tt, seed=10 + i % 3, prints=0)
        kk.clay_poly(c, [(x - 60, 1110), (x + 60, 1110), (x + 30, 1070), (x - 30, 1070)], (250, 200, 40), tt, seed=20 + i % 3, amp=3, prints=0)
        if hit:
            c.drawLine(x - 38, 1200, x + 38, 1290, paint(BLOOD, stroke=16))
            c.drawLine(x + 38, 1200, x - 38, 1290, paint(BLOOD, stroke=16))
    ph = (pos / 170) % 1.0
    down = max(0.0, 1 - ph * 4)
    kk.clay_poly(c, [(stamp_x - 30, 400), (stamp_x + 30, 400), (stamp_x + 30, 850 + 180 * down), (stamp_x - 30, 850 + 180 * down)],
                 (180, 180, 200), tt, seed=30, amp=3, prints=0)
    kk.clay_poly(c, [(stamp_x - 110, 850 + 180 * down), (stamp_x + 110, 850 + 180 * down), (stamp_x + 110, 960 + 180 * down),
                     (stamp_x - 110, 960 + 180 * down)], (220, 30, 40), tt, seed=31, amp=4)
    ov.slam(c, "SAME RULE", 540, 470, 100, T, Wd("b4", "same") - 0.1, color=WHITE, edge=BLOOD, sub="SAME KIND OF PERSON")
    kk.red(st.arr, 0.35)
    return st.arr

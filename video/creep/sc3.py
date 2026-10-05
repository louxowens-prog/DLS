"""Tale three: THE SECOND OPINION. This one is real: doctors who leaned on an AI spotter got worse without it. Pilots
too. The machines quit at the worst moment. Twenty years later Dr Hale is the patient, and her doctor never learned
to look without it."""
import math

import numpy as np
import skia

import comic as CO
import common as C
import face as FA
import kit as K
import props as PR
import sets as SE
from common import E, S, Wx
from kit import INK, WHITE, H, W, mix, paint, path, ramp, ease
from sc1 import scope_screen, tale_title


def opinion_art(c, T):
    SE.clinic(c, T, power=0.6)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((40, 0, 10), 0.35))
    PR.monitor(c, 540, 1000, 1.0, T, scope_screen(T, box=0.0, eye=1.0, grin=1.0), light="red")
    PR.eyebox(c, 540, 650, 1.0, T, on=1.0, look=(0.0, 0.3), light="red")


def s_s_title(T, idx):
    st = K.Stage()
    tale_title(st.c, T, S("s1") - 0.4, ["THE SECOND", "OPINION"], opinion_art, colr=(120, 220, 255), seed=30)
    return st.arr


def stamp(c, s, x, y, T, t0, size=96, rot=-12, colr=(210, 20, 30)):
    """A rubber stamp slammed on to the page."""
    if T < t0:
        return
    k = 1 + 1.5 * max(0.0, 1 - (T - t0) / 0.12)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(k, k)
    f = K.font("bangers-400", size)
    w = f.measureText(s)
    c.drawRoundRect(skia.Rect.MakeLTRB(-w / 2 - 30, -size * 0.9, w / 2 + 30, size * 0.35), 14, 14, paint(colr, 0.9, stroke=10))
    c.drawString(s, -w / 2, 0, f, paint(colr, 0.9))
    K.reg_local(c, -w / 2 - 30, -size * 0.9, w / 2 + 30, size * 0.35, "label")
    c.restore()


def s_s_clinic(T, idx):
    """Doctors who used an AI spotter: the box finds the growths and Dr Hale nods along. THIS ONE'S REAL."""
    st = K.Stage((30, 60, 66))
    c = st.c
    SE.clinic(c, T)
    C.push(c, T, S("s2") - 0.2, Wx("s2", "working"), 1.0, 1.08, cx=640, cy=760)
    PR.monitor(c, 690, 760, 0.95, T, scope_screen(T, box=1.0), light="clinic")
    PR.eyebox(c, 690, 420, 0.7, T, on=1.0, look=(0.3 * math.sin(T * 1.5), 0.5))
    C.person(c, "hale", 300, 1040, 1.3, T, expr="smug", light="clinic", gaze=(0.8, -0.3), turn=0.35, seed=4)
    c.restore()
    return st.arr


def s_s_unplug(T, idx):
    """...tested without it: a hand pulls the plug; the red eye dies."""
    st = K.Stage((30, 60, 66))
    c = st.c
    t_pull = Wx("s2", "without") - 0.05
    on = 1.0 - ease(ramp(T, t_pull, t_pull + 0.25))
    SE.clinic(c, T)
    C.push(c, T, Wx("s2", "working") - 0.1, Wx("s2", "in"), 1.15, 1.3, cx=640, cy=600)
    PR.monitor(c, 690, 760, 0.95, T, scope_screen(T, box=on), light="clinic")
    PR.eyebox(c, 690, 420, 0.7, T, on=on, look=(0.0, 0.5))
    c.restore()
    pull = ease(ramp(T, t_pull - 0.15, t_pull + 0.2))
    px, py = 1000 - 40 * pull, 380 + 160 * pull
    c.drawPath(K.bez_path([(830, 380), (900, 300), (px, py)]), paint((30, 30, 30), stroke=12))
    c.drawRect(skia.Rect.MakeLTRB(px - 20, py - 30, px + 20, py + 30), paint((40, 40, 44)))
    FA.hand(c, px + 30, py + 40, 1.0, 200, skin=FA.CAST["prof"]["skin"], light="clinic", pose="grip", flip=True)
    C.person(c, "hale", 230, 1180, 1.5, T, expr="squint" if on < 0.5 else "neutral", light="screen", gaze=(0.9, -0.5), turn=0.4, seed=4)
    if T > t_pull:
        CO.sfx(c, "PLINK", 840, 340, 80, k=K.pop(T, t_pull, 0.15, 0.3), rot=10, fill=(240, 240, 240), fill2=(170, 170, 180))
    return st.arr


def s_s_stat(T, idx):
    """...found precancerous growths in 22% of patients, down from 28%: the card, stamped REAL STUDY, and the growths on
    the screen that nobody marks."""
    st = K.Stage()
    c = st.c
    CO.shock(c, (20, 60, 70), T, cx=540, cy=700, seed=14, rays=28, bolts=0)
    t22, t28 = Wx("s2", "22%") - 0.1, Wx("s2", "28%") - 0.1

    def screen(cc, x0, y0, x1, y1):
        cx, cy = PR.tunnel(cc, x0, y0, x1, y1, T)
        for i, (gx, gy) in enumerate(((cx - 120, cy + 40), (cx + 110, cy - 50), (cx + 20, cy + 90))):
            PR.growth(cc, gx, gy, 30, T, eye=1.0 if T > t22 else 0.0, grin=1.0 if T > t22 + 0.3 else 0.0)
            if T > t28 + 0.2 * i:
                f = K.font("vt323-400", 34)
                cc.drawString("MISSED", gx - 46, gy - 40, f, paint((255, 40, 40)))
                K.reg_local(cc, gx - 46, gy - 66, gx + 46, gy - 36, "screen")
    PR.monitor(c, 540, 560, 0.95, T, screen, light="clinic")
    if T > t22:
        CO.sfx(c, "22%", 400, 1060, 170, k=K.pop(T, t22, 0.2, 0.35), rot=-4, fill=(255, 70, 50), fill2=(170, 0, 10), tag="stat")
    if T > t28:
        k = K.pop(T, t28, 0.2, 0.3)
        CO.label(c, "DOWN FROM", 760, 1010, 44, "bangers-400", WHITE, tag="stat", outline=INK, ow=8, a=min(1.0, k))
        CO.sfx(c, "28%", 760, 1090, 90, k=k, rot=4, fill=(120, 255, 140), fill2=(30, 160, 60), tag="stat")
    if T > t22:
        CO.caption_box(c, "PATIENTS WITH A GROWTH FOUND, NO AI", 540, 1170, maxw=860, size=34, rot=-1, anchor="top", tag="label",
                       fill=(250, 244, 228))
    stamp(c, "REAL STUDY", 790, 330, T, Wx("s2", "22%") + 0.5, size=80, rot=12)
    return st.arr


def s_s_shout(T, idx):
    """Show me where it is! She bangs on the dead box."""
    st = K.Stage()
    c = st.c
    CO.shock(c, "red", T, cx=540, cy=700, seed=15)
    PR.eyebox(c, 760, 430, 0.9, T, on=0.0, look=(0.0, 0.0), light="red")
    bang = abs(math.sin(T * 9))
    C.person(c, "hale", 470, 900, 1.65, T, expr="angry", light="red", gaze=(0.7, -0.6), turn=0.3, seed=4, shake=3)
    FA.hand(c, 700, 560 - 50 * bang, 1.3, -80, skin=FA.CAST["hale"]["skin"], light="red", pose="grip")
    if bang > 0.85:
        CO.sfx(c, "BANG!", 880, 300, 80, rot=12, fill=(255, 226, 0), fill2=(255, 100, 0))
    return st.arr


PILOT = dict(FA.CAST["junior"])
PILOT.update(top=(30, 40, 70), hair=(60, 40, 30), style="bun", skin=(226, 186, 160), iris=(70, 100, 140), lips=(170, 100, 100))


def pilot(c, T, x, y, s, expr, light, gaze=(0, 0)):
    def headset(cc, L):
        cc.drawPath(K.bez_path([(-120, -40), (0, -260), (120, -40)]), paint((20, 20, 24), stroke=16))
        for sx in (-1, 1):
            FA.lit_fill(cc, K.rrect(sx * 112 - 30, -60, sx * 112 + 30, 40, 18), (40, 40, 46), L, rim=0.8, rim_w=4)
        cc.drawPath(K.bez_path([(-112, 20), (-90, 110), (-30, 120)]), paint((20, 20, 24), stroke=8))
        cc.drawCircle(-30, 120, 12, paint((20, 20, 24)))
    FA.bust(c, "junior", x, y, s, T, expr=expr, light=light, P=PILOT, gaze=gaze, after=headset, blink=C.blink(T, 12))


def s_s_pilot(T, idx):
    """Pilots too: years on autopilot, and the thinking fades first. Then the storm, and the autopilot quits."""
    st = K.Stage()
    c = st.c
    t_quit = Wx("s5", "quit") - 0.05
    fl = C.hit(T, t_quit, 0.6)
    warn = ease(ramp(T, t_quit, t_quit + 0.2))
    SE.cockpit(c, T, warn=warn, flash=fl)
    expr = "blank" if T < t_quit else "fear"
    pilot(c, T, 540, 900, 1.3, expr, "screen" if warn < 0.5 else "red", gaze=(0, -0.2))
    c.drawRoundRect(skia.Rect.MakeLTRB(70, 1230, 420, 1290), 10, 10, paint((20, 40, 20) if warn < 0.5 else (60, 0, 0)))
    lab = "AUTOPILOT ON" if warn < 0.5 else "AUTOPILOT OFF"
    CO.label(c, lab, 245, 1276, 40, "vt323-400", (120, 255, 140) if warn < 0.5 else (255, 60, 50), tag="screen")
    fade = ramp(T, Wx("s4", "thinking") - 0.2, Wx("s4", "first") + 0.4)
    if T < t_quit:                                                      # her thought balloon, fading to nothing
        k = 1 - fade
        if k > 0.02:
            with K.layer(c, k):
                for i, r in enumerate((16, 26)):
                    c.drawCircle(700 + i * 50, 560 - i * 60, r, paint(WHITE))
                    c.drawCircle(700 + i * 50, 560 - i * 60, r, paint(INK, stroke=5))
                th = K.oval(640, 260, 1000, 460)
                c.drawPath(th, paint(WHITE))
                c.drawPath(th, paint(INK, stroke=6))
                PR.brain(c, 820, 370, 0.32, T, glow=0.5)
    if T > t_quit:
        CO.sfx(c, "WHOOP WHOOP", 540, 330, 80, k=K.pop(T, t_quit, 0.15, 0.3), rot=-5, fill=(255, 70, 50), fill2=(170, 0, 10))
    return st.arr


def s_s_warn(T, idx):
    """...when you need the skill you stopped using: her hands hover over the controls."""
    st = K.Stage()
    c = st.c
    SE.cockpit(c, T, warn=1.0, flash=0.0)
    C.dutch(c, -13, 540, 900)
    C.push(c, T, Wx("s5", "when") - 0.1, E("s5") + 0.2, 1.0, 1.2, cx=540, cy=760)
    pilot(c, T, 540, 760, 1.9, "panic", "red", gaze=(0.5 * math.sin(T * 7), 0.4))
    c.restore()
    c.restore()
    for i, x in enumerate((300, 780)):
        FA.hand(c, x, 1250 + 10 * math.sin(T * 13 + i), 1.3, -90 + (25 if i == 0 else -25), skin=PILOT["skin"], light="red", pose="open", flip=i == 1)
    return st.arr


def lying(c, who, x, y, s, T, expr, light, ang=-80, **kw):
    """A character lying in bed, head on the pillow (the bust rotated on to its back)."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    C.person(c, who, 0, 0, s, T, expr=expr, light=light, **kw)
    c.restore()


def bed(c, y, L):
    pillow = K.rrect(60, y - 200, 640, y + 120, 80)
    FA.lit_fill(c, pillow, (236, 236, 240), L, rim=0.6)
    sheet = path([(-60, y + 60), (1140, y + 20), (1140, H), (-60, H)])
    FA.lit_fill(c, sheet, (200, 220, 230), L, rim=0.6)
    for i in range(5):
        c.drawPath(K.bez_path([(100 + i * 200, y + 80), (160 + i * 200, y + 300), (120 + i * 200, H)]), paint((150, 170, 190), 0.5, stroke=6))


def s_s_years(T, idx):
    """Twenty years later, she's the patient."""
    st = K.Stage()
    c = st.c
    SE.ward(c, T)
    L = FA.Light("clinic")
    bed(c, 1000, L)
    lying(c, "hale_old", 380, 880, 1.25, T, "fear", "clinic", ang=-78, gaze=(0.6, -0.8), seed=13)
    sheet = path([(-60, 1060), (1140, 1000), (1140, H), (-60, H)])
    FA.lit_fill(c, sheet, (200, 220, 230), L, rim=0.6)
    CO.caption_box(c, "TWENTY YEARS LATER...", 540, 270, maxw=760, size=54, rot=-2, anchor="top", tag="label")
    return st.arr


def s_s_ward(T, idx):
    """...and her doctor never learned to look without it: the junior at the screen, the box beside her - and the
    lights flicker."""
    st = K.Stage((30, 60, 66))
    c = st.c
    t_fl = Wx("s6", "without") - 0.1
    flick = 1.0 if T < t_fl else (0.0 if (math.floor(T * 14) % 3) == 0 else 0.6)
    on = 1.0 if T < t_fl + 0.4 else 0.0
    SE.clinic(c, T, power=flick)
    PR.monitor(c, 700, 640, 0.85, T, scope_screen(T, box=on, eye=0.0), light="clinic")
    PR.eyebox(c, 700, 330, 0.6, T, on=on, look=(0.2, 0.5))
    if on < 0.5:
        CO.label(c, "POWER CUT: AI OFFLINE", 700, 480, 40, "vt323-400", (255, 70, 60), tag="screen", a=0.6 + 0.4 * (math.floor(T * 4) % 2))
    C.person(c, "junior", 330, 1000, 1.35, T, expr="smile" if T < t_fl else "fear", light="clinic", gaze=(0.8, -0.5), turn=0.35, seed=14)
    if T > t_fl:
        c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0), 0.35 * (1 - flick)))
    return st.arr


def s_s_junior(T, idx):
    """I can't see anything. She squints at the screen; the growth on it moves."""
    st = K.Stage()
    c = st.c
    SE.clinic(c, T, power=0.0, emergency=1.0)
    C.dutch(c, 12, 540, 900)
    C.push(c, T, S("s7") - 0.1, E("s7") + 0.9, 1.0, 1.2, cx=600, cy=700)
    mv = ramp(T, S("s7"), E("s7") + 1.0)
    PR.monitor(c, 680, 620, 0.95, T, scope_screen(T, box=0.0, eye=mv, grin=max(0.0, mv * 2 - 1)), light="red")
    C.person(c, "junior", 300, 1060, 1.5, T, expr="panic" if T > Wx("s7", "see") else "squint", light="red", gaze=(0.9, -0.6), turn=0.4, seed=14)
    c.restore()
    c.restore()
    return st.arr


def s_s_thing(T, idx):
    """THE CLIMAX: the growth swells into a latex horror and bursts out of the screen at her."""
    st = K.Stage()
    c = st.c
    t0 = E("s7") + 1.0
    u = T - t0
    CO.shock(c, "red", T, cx=540, cy=760, seed=16, rays=40, bolts=3)
    if u < 0.75:                                                        # the screen bulges, cracks, bursts
        C.shake(c, T, 10 + 20 * u, seed=3)

        def screen(cc, x0, y0, x1, y1):
            PR.tunnel(cc, x0, y0, x1, y1, T)
            PR.thing(cc, 0, 0, 0.35 + 0.6 * u, T, open_=min(1.0, u * 2.4), light="red")
        PR.monitor(c, 540, 760, 1.4 + 0.5 * u, T, screen, light="red")
        if u > 0.38:
            for i in range(9):
                a = i * 0.7
                c.drawLine(540, 760, 540 + 420 * math.cos(a), 760 + 330 * math.sin(a), paint(WHITE, 0.8, stroke=4))
        c.restore()
    elif u < 1.3:                                                       # old Hale screams
        C.shake(c, T, 8, seed=4)
        C.push(c, T, t0 + 0.75, t0 + 1.3, 1.0, 1.35, cx=540, cy=820)
        lying(c, "hale_old", 520, 860, 2.3, T, "scream", "red", ang=-8, gaze=(0, -0.3), seed=13)
        c.restore()
        c.restore()
        CO.splat(c, 220, 380, 70, seed=4)
    else:                                                               # it lunges right at us
        k = ease(ramp(T, t0 + 1.3, t0 + 1.85))
        C.shake(c, T, 14, seed=5)
        PR.thing(c, 540, 820, 1.3 + 1.6 * k, T, open_=1.0, light="red", lunge=k)
        c.restore()
        for i, (x, y, r) in enumerate(((200, 500, 90), (860, 380, 70), (760, 1200, 110), (300, 1100, 60))):
            if k > 0.2 + 0.15 * i:
                CO.splat(c, x, y, r, seed=10 + i)
    if 0.0 < u < 0.5:
        CO.sfx(c, "CRAACK!", 540, 400, 120, k=K.pop(T, t0, 0.12, 0.3), rot=-8, fill=(255, 226, 0), fill2=(255, 80, 0))
    if u > 1.3:
        CO.sfx(c, "SPLORCH!", 540, 390, 130, k=K.pop(T, t0 + 1.3, 0.12, 0.3), rot=6, fill=(255, 40, 40), fill2=(140, 0, 0))
    return st.arr

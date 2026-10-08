"""The reader: no monster - a blackout, a dead phone, a father's heart pills, a hospital she can't find, a number she
never learned. Then the host turns to us. Then the moral, the last cackle, and the mail-order ads on the back page."""
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
from sc1 import comic_in_hands, cover, cover_art
from sc2 import tomb

NORA_SKIN = FA.CAST["nora"]["skin"]


def s_r_dark(T, idx):
    """Battery critical. Goodbye, Nora. The only light in the flat is the phone, and then there is none."""
    st = K.Stage((0, 0, 0))
    c = st.c
    t_die = Wx("r1", "Nora") + 0.35
    alive = 1.0 if T < t_die else max(0.0, 1 - (T - t_die) / 0.08)
    blink_ = 1.0 if (math.floor(T * 3) % 2 == 0 or T > Wx("r1", "critical")) else 0.4
    if alive > 0:
        SE.glow(c, 540, 1000, 600, (120, 160, 255), 0.18 * alive)
        C.person(c, "nora", 540, 700, 1.4, T, expr="fear", light="screen", gaze=(0.0, 0.9), seed=2)
        c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0), 1 - 0.85 * alive))
    PR.phone(c, 540, 1080, 1.0, 0, T, screen="battery" if alive > 0 else "dead", glow=alive * blink_)
    FA.hand(c, 400, 1230, 1.2, -60, skin=NORA_SKIN, light="screen", pose="grip")
    if alive <= 0:
        c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0), 0.6))
    return st.arr


def s_r_real(T, idx):
    """No monster in this one. A match, a candle, the real dark."""
    st = K.Stage()
    c = st.c
    SE.flat_dark(c, T)
    t0 = S("r2") - 0.1
    lit = ease(ramp(T, t0 + 0.2, t0 + 0.6))
    if lit > 0:
        SE.glow(c, 640, 1060, 500, (255, 190, 120), 0.25 * lit)
    C.push(c, T, t0, E("r2") + 0.3, 1.0, 1.15, cx=520, cy=800)
    C.person(c, "nora", 480, 760, 1.35, T, expr="fear", light="candle" if lit > 0.5 else "plain", gaze=(0.6, 0.5), seed=2)
    PR.candle(c, 680, 1200, 0.9, T, a=lit)
    FA.hand(c, 600, 1290, 1.0, -40, skin=NORA_SKIN, light="candle", pose="grip")
    c.restore()
    if T < t0 + 0.5:                                                    # the match flaring
        SE.glow(c, 700, 1060, 120, (255, 220, 160), 0.6 * (1 - ramp(T, t0 + 0.3, t0 + 0.5)))
    return st.arr


def s_r_father(T, idx):
    """Your father needs his heart pill."""
    st = K.Stage()
    c = st.c
    C.push(c, T, S("r3") - 0.1, Wx("r3", "You") + 0.2, 1.0, 1.12, cx=550, cy=800)
    SE.flat_dark(c, T, moon=0.4)
    SE.glow(c, 300, 1150, 600, (255, 180, 110), 0.22)
    chair = K.rrect(200, 520, 900, 1500, 120)
    FA.lit_fill(c, chair, (90, 60, 50), FA.Light("candle"), rim=0.6)
    gasp = 0.5 + 0.5 * math.sin(T * 7)
    E_ = dict(FA.EXPR["panic"])
    E_["open"] = 0.3 + 0.3 * gasp
    E_["eye"] = 1.1
    C.person(c, "father", 550, 780 + 4 * gasp, 1.35, T, expr=E_, light="candle", gaze=(-0.4, -0.5), seed=21, tilt=-6, talk=0.0)
    FA.hand(c, 520, 1150, 1.3, -20, skin=FA.CAST["father"]["skin"], light="candle", pose="claw")
    PR.candle(c, 180, 1300, 0.8, T)
    c.restore()
    return st.arr


def s_r_pill(T, idx):
    """You can't work out the dose. Aspirin, 75 mg tablets; the note on the fridge says chew 300 mg; a sum she has not done
    in her head for twenty years."""
    st = K.Stage()
    c = st.c
    SE.grad_bg(c, (30, 26, 22), (10, 8, 8))
    SE.glow(c, 540, 820, 600, (255, 180, 110), 0.25)
    C.push(c, T, Wx("r3", "You") - 0.1, Wx("r3", "The", 1), 1.0, 1.06, cx=540, cy=1000)
    c.save()                                                            # the note from the doctor, on the table
    c.translate(540, 1240)
    c.rotate(2)
    c.drawRect(skia.Rect.MakeLTRB(-390, -150, 390, 150), paint((240, 232, 160)))
    c.drawRect(skia.Rect.MakeLTRB(-390, -150, 390, 150), paint(INK, 0.25, stroke=3))
    c.restore()
    CO.label(c, "CHEST PAIN? CHEW 300 mg", 540, 1150, 50, "rubik-900", (180, 20, 20), rot=2, tag="label")
    f = K.font("comic-neue-700", 58)
    tries = ["300 / 75 = ?", "3?  5?  30?"]
    n = min(2, int(max(0.0, T - Wx("r3", "can't")) / 0.45) + 1)
    for i in range(n):
        y = 1232 + i * 72
        x = 250 if i == 0 else 290
        c.drawString(tries[i], x, y, f, paint((40, 40, 140), 0.9))
        K.reg(x, y - 46, x + f.measureText(tries[i]), y + 12, "deco")
        if i == 1 or T > Wx("r3", "dose.") + 0.1:
            c.drawLine(x - 10, y - 18, x + 10 + f.measureText(tries[i]), y - 24, paint((180, 20, 20), 0.8, stroke=5))
    sh = math.sin(T * 23) * 4
    PR.pill_bottle(c, 520 + sh, 700, 1.25, ang=-6 + sh * 0.3)
    FA.hand(c, 400 + sh, 1000, 1.5, -64, skin=NORA_SKIN, light="candle", pose="grip")
    c.restore()
    return st.arr


def s_r_call(T, idx):
    """The ambulance? Forty minutes. 999 on the landline; the clock's red wedge sweeps out the wait."""
    st = K.Stage()
    c = st.c
    SE.grad_bg(c, (40, 38, 42), (12, 12, 14))
    SE.glow(c, 420, 1100, 600, (255, 190, 120), 0.2 * (0.9 + 0.1 * math.sin(T * 11)))
    t0 = Wx("r3", "The", 1) - 0.08
    C.push(c, T, t0, Wx("r3", "The", 2), 1.0, 1.08, cx=540, cy=900)
    # the wall clock, the wait swept out in red
    cx, cy, r = 690, 640, 160
    c.drawCircle(cx, cy, r + 14, paint((60, 44, 30)))
    c.drawCircle(cx, cy, r, paint((236, 228, 206)))
    k = ease(ramp(T, Wx("r3", "Forty") - 0.05, Wx("r3", "minutes.") + 0.3))
    if k > 0:
        wedge = skia.Path()
        wedge.moveTo(cx, cy)
        wedge.arcTo(skia.Rect.MakeLTRB(cx - r + 8, cy - r + 8, cx + r - 8, cy + r - 8), -90, 240 * k, False)
        wedge.close()
        c.drawPath(wedge, paint((210, 20, 24), 0.85))
    for h in range(12):
        a_ = math.radians(h * 30 - 90)
        c.drawLine(cx + (r - 26) * math.cos(a_), cy + (r - 26) * math.sin(a_), cx + (r - 8) * math.cos(a_), cy + (r - 8) * math.sin(a_),
                   paint(INK, stroke=8))
    am = math.radians(-90 + 240 * k)
    c.drawLine(cx, cy, cx + (r - 30) * math.cos(am), cy + (r - 30) * math.sin(am), paint(INK, stroke=10))
    c.drawLine(cx, cy, cx + 70 * math.cos(math.radians(-30)), cy + 70 * math.sin(math.radians(-30)), paint(INK, stroke=14))
    c.drawCircle(cx, cy, 14, paint(INK))
    # the landline
    PR.keypad(c, 360, 1060, 0.95, typed="999", L="candle", status="CONNECTED")
    hov = math.sin(T * 6) * 14
    FA.hand(c, 470 + hov, 1270, 1.4, -110, skin=NORA_SKIN, light="candle", pose="point")
    c.restore()
    if T > Wx("r3", "Forty") - 0.1:
        kk = K.pop(T, Wx("r3", "Forty") - 0.1, 0.2, 0.15)
        CO.caption_box(c, "AMBULANCE: 40 MINUTES", 540, 300, maxw=760, size=50, k=kk, rot=-1.5, anchor="top", tag="label")
    return st.arr


def s_r_door(T, idx):
    """The hospital's ten minutes away. You don't know the way. The door open on a dark street; every road the same."""
    st = K.Stage()
    c = st.c
    C.push(c, T, Wx("r3", "The", 1) - 0.08, Wx("r3", "Your", 1), 1.0, 1.15, cx=540, cy=760)
    SE.street(c, T)
    SE.glow(c, 540, 700, 500, (120, 130, 160), 0.25)
    c.drawRect(skia.Rect.MakeLTRB(0, 0, 160, H), paint((16, 14, 14)))
    c.drawRect(skia.Rect.MakeLTRB(920, 0, W, H), paint((16, 14, 14)))
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 140), paint((16, 14, 14)))
    # Nora in the doorway, from behind, keys in her hand
    body = K.smooth([(400, 1920), (380, 1300), (420, 1060), (480, 1000), (600, 1000), (660, 1060), (700, 1300), (680, 1920)])
    c.drawPath(body, paint((20, 18, 22)))
    c.drawPath(K.oval(470, 820, 610, 1010), paint((24, 18, 18)))
    c.drawPath(K.smooth([(450, 820), (540, 780), (630, 820), (640, 980), (440, 980)]), paint((30, 20, 18)))
    c.drawPath(K.capsule(680, 1100, 780, 1300, 50, 40), paint((20, 18, 22)))
    for i in range(3):
        c.drawLine(780, 1300, 790 + i * 8, 1350 + i * 6, paint((180, 180, 170), stroke=6))
    for i, (x, y, rot) in enumerate(((250, 600, -10), (540, 560, 0), (830, 600, 10))):
        CO.label(c, "?", x, y, 120, "rubik-900", (200, 200, 210), tag="deco", rot=rot, a=0.35 + 0.3 * ramp(T, Wx("r3", "know") - 0.3, Wx("r3", "way") + 0.2))
    c.restore()
    return st.arr


def s_r_number(T, idx):
    """Your sister's number? Never learned it. 0, 7... and her finger stops over the keys."""
    st = K.Stage()
    c = st.c
    SE.grad_bg(c, (40, 40, 44), (14, 14, 16))
    SE.glow(c, 540, 800, 600, (255, 190, 120), 0.18 * (0.9 + 0.1 * math.sin(T * 11)))
    t0 = Wx("r3", "Your", 1) - 0.08
    C.push(c, T, t0, E("r3") + 0.3, 1.0, 1.12, cx=540, cy=800)
    typed = "0" if T < t0 + 0.6 else "07"
    PR.keypad(c, 540, 820, 1.25, typed=typed, L="candle", status="SISTER?")
    hov = math.sin(T * 5) * 30 * ramp(T, t0 + 0.9, t0 + 1.3)
    FA.hand(c, 640 + hov, 1260, 1.6, -100, skin=NORA_SKIN, light="candle", pose="point")
    c.restore()
    return st.arr


def s_r_muse(T, idx):
    """Muse? ...Muse? She whispers to a dead phone; her face in the black glass."""
    st = K.Stage()
    c = st.c
    SE.flat_dark(c, T, moon=0.5)
    C.push(c, T, S("r4") - 0.1, E("r4") + 0.4, 1.0, 1.1, cx=540, cy=800)
    C.person(c, "nora", 540, 760, 1.6, T, expr="fear", light="plain", gaze=(0.0, 0.9), seed=2)
    c.restore()
    sh = math.sin(T * 18) * 6
    PR.phone(c, 560 + sh, 1170, 0.9, -4 + sh * 0.3, T, screen="dead")
    FA.hand(c, 420 + sh, 1290, 1.2, -60, skin=NORA_SKIN, light="plain", pose="grip")
    return st.arr


def s_r_still(T, idx):
    """The outcome, on screen: her father slumped in his armchair; his hand loosens on the aspirin bottle, the bottle drops,
    the hand slips off the armrest and hangs by the candle; the candle gutters out; a long second of black."""
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = E("r4") + 0.35
    u = T - t0
    out = ramp(T, t0 + 0.62, t0 + 0.9)
    a = 1 - out
    L = FA.Light("candle")
    if a > 0:
        C.push(c, T, t0, t0 + 1.0, 1.0, 1.06, cx=400, cy=1100)
        SE.glow(c, 200, 1220, 640, (255, 170, 100), 0.34 * a)
        wing = K.smooth([(330, 1300), (300, 470), (380, 330), (560, 300), (740, 330), (820, 470), (800, 1300)])
        FA.lit_fill(c, wing, (86, 54, 44), L, rim=0.6)                      # the wing chair
        slump = ease(ramp(u, 0.0, 0.5))
        C.person(c, "father", 560, 700 + 40 * slump, 0.95, T, expr="dead", light="candle", seed=21, tilt=-10 - 16 * slump,
                 blink=1.0, talk=0.0)
        FA.lit_fill(c, K.rrect(330, 1180, 1000, 1660, 50), (78, 50, 40), L, rim=0.4)   # the seat
        c.drawRect(skia.Rect.MakeLTRB(-100, 1640, W + 100, H + 100), paint((34, 24, 20)))  # the floor
        drop = ramp(u, 0.24, 0.5)
        ang = 160 - 66 * drop ** 2 + (8 * math.sin(min(1.0, max(0.0, u - 0.5) / 0.25) * math.pi) if u > 0.5 else 0)
        wx, wy = 262 - 14 * drop, 1076 + 22 * drop
        sleeve = K.capsule(470, 1080, wx + 8, wy, 46, 40)
        FA.lit_fill(c, K.rrect(140, 1090, 520, 1660, 46), (96, 62, 48), L, rim=0.8)    # the armrest, in front
        FA.lit_fill(c, sleeve, FA.CAST["father"]["top"], L, rim=0.6)              # his cardigan sleeve along it
        c.drawRect(skia.Rect.MakeLTRB(20, 1490, 300, 1512), paint((60, 40, 30)))       # the side table, the candle on it
        c.drawRect(skia.Rect.MakeLTRB(140, 1510, 170, 1640), paint((50, 34, 26)))
        if u < 0.24:                                                    # the bottle in a loosening grip
            n0 = len(K.TEXT)
            PR.pill_bottle(c, 120, 1150, 0.36, ang=20)
            del K.TEXT[n0:]
        else:                                                           # it falls; tablets scatter on the floor
            fall = ramp(u, 0.24, 0.36)
            n0 = len(K.TEXT)
            PR.pill_bottle(c, 120 + 200 * fall, 1150 + 510 * fall ** 2, 0.36, ang=20 + 150 * fall)
            del K.TEXT[n0:]
            if u > 0.36:
                rng = K.rng_at(77, 1)
                sp = ease(ramp(u, 0.36, 0.56))
                for i in range(9):
                    dx, dy = rng.uniform(-200, 240), rng.uniform(-20, 50)
                    c.drawOval(skia.Rect.MakeXYWH(330 + dx * sp - 11, 1690 + dy * sp - 6, 22, 12), paint((240, 236, 226), 0.9))
        FA.hand(c, wx, wy, 1.25, ang, skin=FA.CAST["father"]["skin"], light="candle", pose="grip" if u < 0.24 else "open", flip=True)
        PR.candle(c, 150, 1400, 0.8, T, a=a)
        c.restore()
    if out > 0:                                                          # a thread of smoke where the flame was
        for i in range(6):
            y = 1260 - out * 60 - i * 40
            c.drawCircle(150 + 14 * math.sin(T * 3 + i), y, 8 + i * 3, paint((150, 150, 150), 0.12 * (1 - i / 6) * (1 - ramp(T, t0 + 1.0, t0 + 1.4)), blur=6))
    return st.arr


def s_r_pocket(T, idx):
    """This one isn't in the comic book, dearie: in the black glass, behind Nora's reflection, the host rises."""
    st = K.Stage((2, 2, 4))
    c = st.c
    t0 = S("r5") - 0.15
    c.drawRoundRect(skia.Rect.MakeLTRB(60, 160, 1020, 1760), 80, 80, paint((6, 6, 10)))
    c.drawRoundRect(skia.Rect.MakeLTRB(60, 160, 1020, 1760), 80, 80, paint((60, 60, 70), stroke=10))
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(70, 170, 1010, 1750), 76, 76), doAntiAlias=True)
    rise = ease(ramp(T, t0 + 0.3, t0 + 1.6))
    with K.layer(c, 0.75 * rise):
        FA.bust(c, "host", 600, 700 + (1 - rise) * 300, 1.7, T, expr="sly", light="green", talk=C.talk(T, "HOST"), blink=C.blink(T, 5))
    with K.layer(c, 0.35):                                              # Nora's reflection, faint
        FA.bust(c, "nora", 380, 860, 1.3, T, expr="fear", light="plain", gaze=(0.0, 0.0))
    c.drawPath(path([(70, 170), (500, 170), (70, 900)]), paint(WHITE, 0.05))
    c.restore()
    return st.arr


def s_r_point(T, idx):
    """It's in your pocket. She turns from the glass to us and points out of the screen."""
    st = K.Stage()
    c = st.c
    t0 = Wx("r5", "It's") - 0.06
    CO.shock(c, "green", T, cx=540, cy=760, seed=21, rays=30, bolts=1, a=1.0)
    C.push(c, T, t0, E("r5") + 0.6, 1.0, 1.18, cx=540, cy=900)
    FA.bust(c, "host", 540, 760, 1.8, T, expr="sly", light="green", talk=C.talk(T, "HOST"), blink=C.blink(T, 5), gaze=(0.0, 0.1))
    k = ease(ramp(T, t0 + 0.1, t0 + 0.5))
    FA.hand(c, 940, 1420 - 120 * k, 1.6 + 0.8 * k, -150, skin=FA.CAST["host"]["skin"], light="green", pose="point", bony=True,
            nails=(40, 20, 30))
    c.restore()
    return st.arr


# ------------------------------------------------------------------ the moral

def s_m_close(T, idx):
    """The quiet beat: the comic closed on the floor in the last of the candle, the dead phone beside it."""
    st = K.Stage()
    c = st.c
    SE.grad_bg(c, (22, 18, 24), (8, 6, 8))
    floor = path([(-100, 760), (1180, 760), (1180, H), (-100, H)])
    FA.lit_fill(c, floor, (70, 50, 40), FA.Light("candle"), rim=0.3)
    for i in range(7):
        c.drawLine(-100, 800 + i * 110, 1180, 820 + i * 110, paint((40, 28, 22), 0.6, stroke=5))
    C.push(c, T, S("m1") - 1.0, E("m1") + 0.2, 1.0, 1.12, cx=520, cy=1000)
    SE.glow(c, 300, 900, 600, (255, 180, 100), 0.25 * (0.9 + 0.1 * math.sin(T * 11)))
    comic_in_hands(c, 560, 1040, 1.05, 8, T)
    PR.phone(c, 880, 1240, 0.6, -20, T, screen="dead")
    PR.candle(c, 250, 980, 0.9, T)
    c.restore()
    return st.arr


HABITS = [("EXPLAIN IT, DON'T DO IT", "m2", "explain"), ("DRAFT FIRST", "m2", "Draft"), ("FIND THE WAY ONCE", "m2", "Find"),
          ("DO THE SUM, THEN CHECK", "m2", "sum")]


def habit_art(c, i, w, h, T):
    L = FA.Light("lamp")
    if i == 0:
        CO.shock(c, (250, 210, 90), T, cx=w / 2, cy=h / 2, seed=3, rays=18, bolts=0)
        FA.bust(c, "kit", w / 2 - 40, h * 0.62, 0.62, T, expr="smile", light="lamp", gaze=(0.4, -0.6))
        CO.balloon(c, "WHY?", w * 0.78, h * 0.3, tail=(w * 0.6, h * 0.48), size=40, maxw=200, tag="deco")
    elif i == 1:
        SE.grad_bg(c, (250, 240, 210), (230, 220, 190))
        c.drawRect(skia.Rect.MakeLTRB(60, 60, w - 60, h - 40), paint(WHITE))
        n = int(8 * ramp(T, Wx("m2", "Draft"), Wx("m2", "Draft") + 1.2))
        for k in range(n):
            c.drawPath(path([(90 + j * 12, 110 + k * 36 + 6 * math.sin(j * 0.9 + k)) for j in range(int((w - 200) / 12))], closed=False),
                       paint((60, 60, 70), stroke=3))
        c.drawPath(K.capsule(w - 150, h - 160, w - 60, h - 300, 16, 20), paint((240, 190, 40)))
        FA.hand(c, w - 170, h - 150, 0.8, -60, skin=FA.CAST["kit"]["skin"], light=L, pose="grip")
    elif i == 2:
        SE.grad_bg(c, (140, 200, 240), (220, 240, 250))
        FA.bust(c, "vera", w * 0.38, h * 0.62, 0.6, T, expr="smile", light="lamp", gaze=(0.7, 0.3))
        c.drawRect(skia.Rect.MakeLTRB(w * 0.64, h * 0.42, w * 0.97, h * 0.88), paint((236, 226, 180)))
        for k in range(5):
            c.drawLine(w * 0.64, h * (0.47 + k * 0.08), w * 0.97, h * (0.44 + k * 0.09), paint((200, 80, 60), stroke=4))
    else:
        SE.grad_bg(c, (250, 246, 230), (230, 226, 210))
        f = K.font("caveat-700", 70)
        c.drawString("4 x 7 = 28", 60, h * 0.45, f, paint((40, 40, 140)))
        K.reg_local(c, 60, h * 0.45 - 50, 60 + f.measureText("4 x 7 = 28"), h * 0.45 + 10, "deco")
        if T > Wx("m2", "check") - 0.1:
            PR.calculator(c, w * 0.78, h * 0.62, 0.42, T, display="28")
            c.drawPath(path([(w * 0.2, h * 0.7), (w * 0.3, h * 0.82), (w * 0.5, h * 0.58)], closed=False), paint((30, 170, 60), stroke=14))


def s_m_habits(T, idx):
    st = C.page(seed=17)
    c = st.c
    rects = [(50, 250, 525, 760), (555, 250, 1030, 760), (50, 790, 525, 1290), (555, 790, 1030, 1290)]
    for i, ((x0, y0, x1, y1), (name, key, word)) in enumerate(zip(rects, HABITS)):
        t0 = Wx(key, word) - 0.12
        if T < t0:
            c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint((210, 200, 176)))
            c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(INK, 0.4, stroke=8))
            continue
        k = K.pop(T, t0, 0.2, 0.15)
        with C.sub((240, 230, 200)) as sub:
            habit_art(sub.c, i, x1 - x0, y1 - y0, T)
        CO.panel(c, sub.arr[: y1 - y0, : x1 - x0], x0, y0, x1, y1, border=12, rot=(-1, 1, 1, -1)[i] * 0.8)
        CO.caption_box(c, name, (x0 + x1) / 2, y0 + 8, maxw=440, size=34, k=k, rot=(-2, 2, -2, 2)[i], anchor="top", tag="label")
    return st.arr


def s_m_tutor(T, idx):
    """An AI tutor that guided instead of answering largely avoided the drop."""
    st = K.Stage()
    c = st.c
    SE.grad_bg(c, (60, 70, 50), (20, 24, 18))
    CO.shock(c, (60, 90, 60), T, cx=540, cy=600, seed=8, rays=26, bolts=0, a=0.6)
    base = 1110
    c.drawRect(skia.Rect.MakeLTRB(0, base, W, H), paint((40, 30, 20)))
    ctrl = 380
    hold = ease(ramp(T, Wx("m3", "largely") - 0.3, Wx("m3", "avoided") + 0.3))
    tomb(c, 200, base, ctrl, 200, (150, 150, 160), "NEVER HAD AI", "", T)
    tomb(c, 540, base, ctrl * 0.83, 200, (200, 60, 60), "AI ANSWERS", "-17%", T)
    tomb(c, 880, base, ctrl * (0.83 + 0.15 * hold), 200, (120, 200, 140), "AI TUTOR", "" if hold < 0.6 else "NO BIG DROP", T)
    if T > Wx("m3", "tutor") - 0.2:                                     # the tutor ghost, pointing at the work rather than doing it
        k = ease(ramp(T, Wx("m3", "tutor") - 0.2, Wx("m3", "tutor") + 0.3))
        PR.ghost(c, 860, 400, 0.36 * k, T, a=k, mouth=0.2, reach=0.3, light="lamp", tail_to=(860, 560))
    CO.label(c, "AN AI TUTOR THAT GUIDES", 540, 330, 54, "bangers-400", (255, 226, 0), tag="label", outline=INK, ow=10)
    return st.arr


def s_m_host(T, idx):
    """Use it... or lose it. Ahahahaha! The host full frame, the shock colours cycling."""
    st = K.Stage()
    c = st.c
    cols = ["violet", "red", "green", "blue"]
    col_ = cols[int(max(0, T - S("m4")) * 4) % 4] if T > S("m4b") else "violet"
    CO.shock(c, col_, T, cx=540, cy=760, seed=30, rays=36, bolts=2)
    C.push(c, T, S("m4") - 0.1, E("m4b") + 0.3, 1.0, 1.4, cx=540, cy=880)
    expr = "sly" if T < S("m4b") else "cackle"
    FA.bust(c, "host", 540, 780, 2.0, T, expr=expr, light="green", talk=C.talk(T, "HOST"), blink=C.blink(T, 5),
            shake=3 if expr == "cackle" else 0)
    c.restore()
    return st.arr


ADS = [
    ((50, 330, 520, 760), "AMAZING!", "YOUR OWN BRAIN", "Works better with daily use! FREE: you already own one!"),
    ((550, 330, 1030, 610), "LEARN TO READ", "A MAP!", "In just ONE walk! No batteries!"),
    ((550, 630, 1030, 910), "MEMORISE", "3 PHONE NUMBERS", "Amaze your family in a blackout!"),
    ((50, 780, 520, 1060), "GROW YOUR OWN", "BRAIN MAP!", "Just add walking. Results in weeks!"),
]


def s_m_back(T, idx):
    """The back page: mail-order ads - and the assistant, offering to summarise the whole thing."""
    st = K.Stage()
    c = st.c
    CO.page_bg(c, (238, 226, 192), ghosts=False)
    CO.newsprint(st.arr, 1.0)
    c.drawRect(skia.Rect.MakeLTRB(40, 236, 1040, 310), paint(INK))
    CO.label(c, "SEND NO MONEY! THESE OFFERS NEVER EXPIRE!", 540, 290, 44, "bangers-400", (255, 226, 0), tag="ad")
    for i, ((x0, y0, x1, y1), a, b, small) in enumerate(ADS):
        t0 = E("m4b") + 0.45 + i * 0.12
        if T < t0:
            continue
        c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint((250, 244, 220)))
        c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(INK, stroke=6))
        CO.label(c, a, (x0 + x1) / 2, y0 + 70, 50, "bangers-400", (200, 20, 20), tag="ad")
        CO.label(c, b, (x0 + x1) / 2, y0 + 130, 54, "bangers-400", INK, tag="ad")
        f = K.font("comic-neue-700", 40)
        lines = K.wrap(small, f, x1 - x0 - 40)
        for j, ln in enumerate(lines):
            CO.label(c, ln, (x0 + x1) / 2, y0 + 190 + j * 46, 40, "comic-neue-700", (20, 10, 10), tag="ad")
        if i == 0:
            PR.brain(c, (x0 + x1) / 2, y1 - 62, 0.26, T, glow=0.6)
    # the coupon
    c.save()
    q = paint(INK, stroke=4)
    q.setPathEffect(skia.DashPathEffect.Make([16, 10], 0))
    c.drawRect(skia.Rect.MakeLTRB(550, 930, 1030, 1050), paint((250, 248, 236)))
    c.drawRect(skia.Rect.MakeLTRB(550, 930, 1030, 1050), q)
    CO.label(c, "MAIL TO: AUNT ATROPHY", 790, 980, 34, "bangers-400", INK, tag="ad")
    CO.label(c, "BOX 13, THE MARGINS", 790, 1028, 34, "bangers-400", INK, tag="ad")
    c.restore()
    lvl = C.talk(T, "MUSE")
    SE.glow(c, 860, 1180, 260, (90, 180, 255), 0.3 + 0.2 * lvl)
    PR.phone(c, 860, 1180, 0.55, 14, T, screen="muse", level=lvl)
    if T > E("m5") + 0.3:
        CO.drip_title(c, "THE END?", 540, 1450, 120, color=(220, 20, 30), seed=40, k=K.pop(T, E("m5") + 0.3, 0.25, 0.3), tag="deco")
    return st.arr

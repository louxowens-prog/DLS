"""The present day - flat, sharp, cold, no gels: an interview room at nine on a Monday, phones in a tray, a page of
code that crashes; a dissertation she cannot describe; six rejections, a loan statement, a degree on the wall. Then
night, and a dark window in which her reflection is porcelain - and the Governess stands behind it."""
import math

import numpy as np
import skia

import cast as CA
import gel as G
import kit as K
import props as PR
from common import E, S, Wx, blink, hit, talk, zoom
from edit import cut, end
from kit import BLACK, INK, PAPER, WHITE, H, W, mix, paint, ramp

FLAT_L, FLAT_R = (238, 238, 234), (214, 218, 224)
CODE = ["def average(marks):", "    total = 0", "    for m in marks:", "        total += m", "    return total / len(marks)", "",
        "average([])"]


def clock_at(T):
    """The wall clock: 09:00:40 at the first frame of the present day, counting on in real time in every angle."""
    secs = 40 + int(max(0.0, T - cut("r_room")))
    return f"09:{secs // 60:02d}:{secs % 60:02d}"


def _room(c, T, clock=None):
    """A meeting room: white walls, ceiling panels, a glass wall with grey blinds, a digital clock."""
    clock = clock_at(T) if clock is None else clock
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((222, 224, 222)))
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 180), paint((236, 238, 238)))
    for k in range(3):
        c.drawRect(skia.Rect.MakeLTRB(120 + k * 300, 40, 360 + k * 300, 120), paint((250, 252, 252)))
    c.drawRect(skia.Rect.MakeLTRB(640, 260, 1080, 1180), paint((190, 198, 204)))
    for k in range(30):
        c.drawLine(640, 270 + k * 30, 1080, 270 + k * 30, paint((168, 176, 182), stroke=6))
    c.drawRect(skia.Rect.MakeLTRB(0, 1180, W, H), paint((150, 152, 156)))
    c.drawRoundRect(skia.Rect.MakeLTRB(290, 330, 520, 420), 10, 10, paint((40, 42, 46)))
    K.text(c, clock, 405, 395, 52, "inter-500", (240, 80, 60), tag="screen")


def _flat_face(c, x, y, s, who, T, expr="neutral", talk_=0.0, blink_=0.0, gaze=(0, 0), a=1.0):
    CA.face(c, x, y, s, who, T, L=FLAT_L, R=FLAT_R, core=0.12, amb=(150, 150, 152), expr=expr, talk=talk_, blink=blink_,
            gaze=gaze, a=a)


def _backs(c):
    """The two interviewers from behind: suit shoulders, shirt collars, the backs of their heads, an ear each."""
    for x, col, hair, sh in ((250, (96, 96, 102), (176, 172, 166), (70, 70, 76)), (830, (30, 30, 36), (34, 26, 22), (14, 14, 18))):
        c.drawPath(K.smooth([(x - 240, H), (x - 214, 1390), (x - 120, 1300), (x + 120, 1300), (x + 214, 1390), (x + 240, H)]), paint(col))
        c.drawLine(x, 1330, x, H, paint(sh, stroke=4))                                      # the jacket's centre seam
        c.drawPath(K.path([(x - 70, 1296), (x + 70, 1296), (x + 40, 1326), (x - 40, 1326)]), paint((236, 236, 234)))   # collar
        c.drawRect(skia.Rect.MakeLTRB(x - 44, 1250, x + 44, 1300), paint((200, 168, 150)))                         # neck
        for s_ in (-1, 1):
            c.drawOval(skia.Rect.MakeLTRB(x + s_ * 96 - 14, 1150, x + s_ * 96 + 14, 1196), paint((206, 170, 152)))  # ears
        c.drawOval(skia.Rect.MakeLTRB(x - 96, 1056, x + 96, 1276), paint(hair))
        for k in range(9):                                                                   # strands of hair
            xx = x - 70 + k * 17
            c.drawLine(xx, 1070 + abs(k - 4) * 6, xx + 6, 1262 - abs(k - 4) * 8, paint(mix(hair, BLACK, 0.25), 0.7, stroke=3))


def s_r_room(T, idx):
    """She was never in an old town. It isn't 1974. It's Monday, 9 a.m., and she has been silent in this chair for
    forty seconds. A flat, sharp meeting room; the lens creeps in on Clara across the table; cut to the clock on the
    wall, counting; to the tray where the phones were left; to her eyes."""
    st = K.Stage()
    c = st.c
    t0 = cut("r_room")
    t_clock = Wx("r1", "It's") - 0.1
    t_tray = Wx("r1", "and") - 0.1
    t_eyes = Wx("r1", "forty") - 0.15
    if t_clock <= T < t_tray:                                   # the clock on the wall, close
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((222, 224, 222)))
        zoom(c, T, t_clock, t_tray, 1.0, 1.06, cx=540, cy=820)
        c.drawRoundRect(skia.Rect.MakeLTRB(90, 620, 990, 1020), 30, 30, paint((40, 42, 46)))
        K.text(c, clock_at(T), 540, 880, 190, "inter-500", (240, 80, 60), tag="screen")
        c.restore()
        return st.arr
    if t_tray <= T < t_eyes:                                    # the tray: three phones, face down
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((236, 236, 234)))
        zoom(c, T, t_tray, t_eyes, 1.0, 1.08, cx=540, cy=900)
        c.drawRoundRect(skia.Rect.MakeLTRB(120, 760, 960, 1180), 30, 30, paint((80, 84, 92)))
        for k in range(3):
            c.drawRoundRect(skia.Rect.MakeLTRB(170 + k * 265, 800, 400 + k * 265, 1140), 24, 24, paint((20, 20, 24)))
            c.drawCircle(220 + k * 265, 850, 14, paint((50, 52, 58)))
        c.drawRect(skia.Rect.MakeLTRB(330, 560, 750, 690), paint((250, 250, 250)))
        K.text(c, "PHONES", 540, 655, 84, "inter-700", (40, 40, 46), tag="screen")
        c.restore()
        return st.arr
    if T >= t_eyes:                                             # her eyes: forty seconds of nothing
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((214, 216, 214)))
        zoom(c, T, t_eyes, end("r_room"), 1.0, 1.2, cx=540, cy=800)
        _flat_face(c, 540, 900, 2.6, "clara_now", T, expr="lost", blink_=0.0, gaze=(0.0, 0.3))
        c.restore()
        return st.arr
    zoom(c, T, t0, t_clock, 1.0, 1.22, cx=540, cy=760)
    _room(c, T)
    _flat_face(c, 540, 760, 0.82, "clara_now", T, expr="lost", blink_=blink(T, 21) * 0.3, gaze=(0.0, 0.5))
    c.drawRect(skia.Rect.MakeLTRB(80, 1040, 1000, 1110), paint((244, 244, 242)))
    c.drawRect(skia.Rect.MakeLTRB(80, 1110, 1000, 1130), paint((200, 200, 200)))
    c.drawRoundRect(skia.Rect.MakeLTRB(160, 1000, 360, 1050), 8, 8, paint((80, 84, 92)))        # the phone tray
    c.drawRect(skia.Rect.MakeLTRB(196, 952, 324, 994), paint((250, 250, 250)))
    K.text(c, "PHONES", 260, 984, 26, "inter-700", (40, 40, 46), tag="screen")
    for k in range(3):
        c.drawRoundRect(skia.Rect.MakeLTRB(176 + k * 60, 1008, 226 + k * 60, 1044), 6, 6, paint((20, 20, 24)))
    _backs(c)
    c.restore()
    # a subliminal flash: two frames of the villa when she remembers it
    tf = Wx("r1", "old")
    if tf <= T < tf + 0.09:
        c.drawPaint(paint((20, 4, 20)))
        CA.face(c, 540, 820, 1.4, "governess", T, L=(255, 60, 170), R=(70, 100, 255), core=0.4, expr="polite", porc=0.6, blink=0.0)
    return st.arr


def s_r_code(T, idx):
    """First-class degree in computer science. Phones in the tray. So, why does this code crash? The interviewer; the
    printed page slid across (it divides by zero on an empty list); then Clara, silent."""
    st = K.Stage()
    c = st.c
    t1 = Wx("r2", "why") - 0.2
    t2 = E("r2") + 0.12
    if T < t1:
        _room(c, T)
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((222, 224, 222), 0.6))
        _flat_face(c, 540, 820, 1.25, "int1", T, expr="neutral", talk_=talk(T, "INT1"), blink_=blink(T, 31))
    elif T < t2:
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((236, 236, 234)))
        k = K.ease(ramp(T, t1, t1 + 0.35))
        c.save()
        c.translate(-760 * (1 - k), 40 * (1 - k))              # slid across the table from her left
        c.rotate(-2 - 6 * (1 - k))
        c.drawRect(skia.Rect.MakeLTRB(110, 360, 990, 1290), paint((0, 0, 0), 0.15, blur=12))
        c.drawRect(skia.Rect.MakeLTRB(100, 340, 980, 1280), paint((252, 252, 250)))
        K.text(c, "Q3.", 150, 430, 44, "inter-700", INK, align="left", tag="screen")
        for i, ln in enumerate(CODE):
            if ln:
                K.text(c, ln, 150, 540 + i * 74, 40, "courier-400", (30, 34, 40), align="left", tag="screen")
        K.text(c, "Why does this crash?", 150, 1180, 42, "inter-500", INK, align="left", tag="screen")
        c.restore()
    else:
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((214, 216, 214)))
        dart = 0.5 * math.sin(T * 7)
        _flat_face(c, 540, 860, 1.6, "clara_now", T, expr="dread", blink_=0.0, gaze=(dart, 0.6))
    return st.arr


def s_r_diss(T, idx):
    """Then talk us through your dissertation. It was about... it was... The second interviewer; then Clara, nothing
    coming."""
    st = K.Stage()
    c = st.c
    if T < S("r4") - 0.15:
        _room(c, T)
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((222, 224, 222), 0.6))
        _flat_face(c, 540, 820, 1.25, "int2", T, expr="neutral", talk_=talk(T, "INT2"), blink_=blink(T, 41))
    else:
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((210, 212, 210)))
        zoom(c, T, S("r4") - 0.15, end("r_diss"), 1.0, 1.15, cx=540, cy=760)
        _flat_face(c, 540, 860, 1.6, "clara_now", T, expr="fear" if T > E("r4") else "lost", talk_=talk(T, "CLARA"),
                   blink_=blink(T, 9), gaze=(-0.2, 0.1))
        c.restore()
    return st.arr


def s_r_thanks(T, idx):
    """Thank you, Clara. We'll be in touch. The folder closes."""
    st = K.Stage()
    c = st.c
    _room(c, T)
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((222, 224, 222), 0.6))
    _flat_face(c, 540, 760, 1.15, "int1", T, expr="neutral", talk_=talk(T, "INT1"), blink_=blink(T, 51))
    k = K.ease(ramp(T, cut("r_thanks") + 0.6, cut("r_thanks") + 1.2))
    c.drawRect(skia.Rect.MakeLTRB(200, 1180, 880, 1300), paint((240, 240, 238)))
    c.save()
    c.translate(540, 1240)
    c.scale(1.0, max(0.05, 1 - k))
    c.drawRect(skia.Rect.MakeLTRB(-300, -260, 300, 0), paint((40, 70, 140)))
    c.restore()
    return st.arr


def s_r_after(T, idx):
    """Six rejections. £53,000 of student debt. A degree on the wall, and nothing behind it."""
    st = K.Stage()
    c = st.c
    t_debt = Wx("r6", "Fifty-three") - 0.15
    t_wall = Wx("r6", "degree") - 0.25
    if T < t_debt:                                              # the phone: rejections stacking up
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((60, 62, 66)))
        c.drawRoundRect(skia.Rect.MakeLTRB(190, 250, 890, 1330), 60, 60, paint((14, 14, 16)))
        c.drawRoundRect(skia.Rect.MakeLTRB(214, 274, 866, 1306), 44, 44, paint((246, 246, 248)))
        K.text(c, "Inbox", 260, 360, 46, "inter-700", INK, align="left", tag="screen")
        n = min(6, 1 + int((T - cut("r_after")) / 0.3))
        for i in range(n):
            y = 420 + i * 140
            c.drawRoundRect(skia.Rect.MakeLTRB(240, y, 840, y + 124), 18, 18, paint((232, 234, 238)))
            K.text(c, "Your application", 270, y + 50, 32, "inter-700", INK, align="left", tag="screen")
            K.text(c, "Unfortunately, we will not be...", 270, y + 98, 30, "inter-500", (110, 110, 118), align="left", tag="screen")
    elif T < t_wall:                                            # the loan statement
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((70, 72, 74)))
        c.save()
        c.rotate(-3)
        c.drawRect(skia.Rect.MakeLTRB(150, 330, 930, 1290), paint((250, 250, 248)))
        K.text(c, "STUDENT LOAN STATEMENT", 540, 440, 42, "inter-700", INK, tag="screen")
        for i in range(5):
            c.drawRect(skia.Rect.MakeLTRB(210, 520 + i * 50, 870 - i * 60, 530 + i * 50), paint((200, 200, 204)))
        K.text(c, "Balance", 540, 900, 44, "inter-500", (90, 90, 96), tag="screen")
        K.text(c, "£53,010", 540, 1040, 120, "inter-700", (190, 30, 40), tag="screen")
        c.restore()
    else:                                                       # the degree on the bedroom wall, then nothing behind it
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((178, 180, 184)))
        k = K.ease(ramp(T, Wx("r6", "nothing") - 0.1, Wx("r6", "nothing") + 0.6))
        x0, y0, x1, y1 = 170, 420, 910, 1000
        c.drawRect(skia.Rect.MakeLTRB(x0 - 30, y0 - 30, x1 + 30, y1 + 30), paint((30, 30, 34)))
        c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint((250, 248, 240)))
        a = 1 - k
        K.text(c, "BSc COMPUTER SCIENCE", 540, 580, 48, "cinzel-800", INK, tag="screen", a=a)
        K.text(c, "First Class Honours", 540, 670, 44, "playfair-400i", INK, tag="screen", a=a)
        K.text(c, "Clara Ashdown", 540, 790, 52, "playfair-400i", INK, tag="screen", a=a)
        c.drawCircle(780, 900, 46, paint((190, 30, 40), a))
        if k > 0:                                               # the glass goes black: nothing behind it
            c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint((0, 0, 0), 0.9 * k))
    return st.arr


def s_p_window(T, idx):
    """One day, the machine will wait outside the door. What will be left inside you? Night; Clara at a dark window.
    In the glass her reflection is porcelain, the Governess behind it; at 'inside you' it cracks open onto nothing."""
    st = K.Stage((4, 6, 14))
    c = st.c
    t0 = cut("p_window")
    zoom(c, T, t0, end("p_window"), 1.0, 1.18, cx=540, cy=800)
    c.drawRect(skia.Rect.MakeLTRB(80, 160, 1000, 1500), paint((6, 10, 26)))
    G.pool(c, 840, 380, 160, (255, 220, 160), 0.25)
    G.pool(c, 260, 600, 120, (255, 200, 140), 0.2)
    for k in range(6):                                         # city lights far below, through the glass
        c.drawCircle(200 + k * 130, 1300 + 20 * math.sin(k), 6, paint((255, 200, 120), 0.6))
    kp = K.ease(ramp(T, t0 + 0.4, t0 + 1.6))
    kc = ramp(T, Wx("p1", "inside") - 0.05, Wx("p1", "inside") + 0.8)
    gv = K.ease(ramp(T, Wx("p1", "machine") - 0.2, Wx("p1", "machine") + 0.6))
    if gv > 0:
        CA.face(c, 760, 620, 0.85, "governess", T, L=(70, 100, 255), R=(255, 60, 170), core=0.4, expr="polite", porc=0.6, blink=0.0,
                a=0.55 * gv)
    CA.face(c, 500, 800, 1.2, "clara_now" if kp < 0.5 else "clara", T, L=(70, 100, 255), R=(255, 60, 170), core=0.45,
            expr="blank", porc=kp, crack=kc, blink=0.0, gaze=(0.0, 0.0), a=0.85)
    c.drawPath(K.path([(80, 160), (420, 160), (80, 900)]), paint(WHITE, 0.05))
    c.drawRect(skia.Rect.MakeLTRB(80, 160, 1000, 1500), paint((40, 40, 50), stroke=24))
    c.drawLine(540, 160, 540, 1500, paint((40, 40, 50), stroke=14))
    c.restore()
    if T > E("p1") + 0.1:
        c.drawPaint(paint((0, 0, 0), K.ease(ramp(T, E("p1") + 0.1, E("p1") + 0.6))))
    return st.arr

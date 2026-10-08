"""NADIA - one ordinary day, every system switched on, everything that can go wrong going wrong.

n_mirror   - dawn; Nadia in her bathroom mirror; a box flickers over her reflection. DRAMATISATION, every step documented.
n_road     - the city from above; her car; a camera at every junction flashes, and the log fills.
n_call     - her desk; the dashboard scores her words, her tone, her face.
n_idle     - the restroom door, a timer, FLAGGED: IDLE.
n_union    - her work laptop; an article on organising; the monitoring console logs it.
n_checkout - a self-checkout: vitamins, unscented lotion, cotton balls - and a score nobody shows her.
n_exhibit  - in the gallery, her porcelain likeness in its case; a new line on its brass label.
n_face     - her face over her phone, a baby ad glowing: "I haven't told anyone."
n_vigil    - a candlelight vigil; a camera on a pole; MATCH.
n_phone    - her shifts cut; then baby ads, everywhere.
n_door     - her door at night. Silence. Three knocks.
n_match    - the screen from the very first frame: a blurred robbery still beside her ID photo. MATCH 98.1%.
n_scream   - red and blue light on her face: "That's not me!"; her porcelain likeness cracks."""
import math

import numpy as np
import skia

import cast as CA
import cold as CO
import couture as C
import gel as G
import hall as Hl
import kit as K
import pers as Pr
from common import E, S, Wx, blink, hit, shake, stutter, talk, zoom
from edit import cut, end
from kit import BLACK, H, W, WHITE, mix, paint, ramp

COLD_L, COLD_R, COLD_A = (214, 230, 246), (130, 150, 180), (70, 78, 92)


def _tag(c, T, a=1.0):
    """The dramatisation tag, quiet, at the top of the frame."""
    c.drawPath(K.rrect(150, 246, 930, 300, 8), paint((8, 12, 16), 0.7 * a))
    K.text(c, "DRAMATISATION · EVERY STEP IS DOCUMENTED", 540, 284, 28, "jost-600", (220, 236, 244), tag="label", a=a)


def s_n_mirror(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0, t1 = cut("n_mirror"), end("n_mirror")
    zoom(c, T, t0, t1, 1.0, 1.05, 540, 860)
    c.drawRect(skia.Rect.MakeLTRB(-40, -40, W + 40, H + 40), paint(shader=K.lin((0, 0), (0, H), [(150, 160, 172), (200, 208, 216), (120, 130, 144)])))
    for i in range(8):
        for j in range(14):
            c.drawRect(skia.Rect.MakeXYWH(i * 140, j * 140, 136, 136), paint((226, 232, 238), 0.25, stroke=3))
    c.drawPath(K.rrect(170, 360, 910, 1340, 30), paint((60, 66, 76)))
    c.drawPath(K.rrect(186, 376, 894, 1324, 24), paint(shader=K.lin((186, 376), (894, 1324), [(170, 184, 196), (120, 132, 146), (150, 164, 178)])))
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(186, 376, 894, 1324), 24, 24), doAntiAlias=True)
    CA.face(c, 540, 830, 1.3, "nadia", T, L=COLD_L, R=COLD_R, core=0.2, amb=COLD_A, blink=blink(T, 2), expr="lost")
    fl = (int(T * 7) % 5) == 0 or ramp(T, Wx("n1", "Call-center") - 0.1, Wx("n1", "Call-center") + 0.1) == 1.0 and (int(T * 9) % 3 == 0)
    if fl:
        CO.target_box(c, 380, 560, 700, 1040, T, lock=1.0, col=(120, 240, 255), label="ID: NADIA K. · 34")
    c.drawRect(skia.Rect.MakeLTRB(186, 376, 894, 1324), paint(shader=K.lin((186, 376), (600, 1324), [(255, 255, 255, 0.18), (255, 255, 255, 0.0)])))
    c.restore()
    c.restore()
    _tag(c, T)
    return st.arr


def s_n_road(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0, t1 = cut("n_road"), end("n_road")
    u = ramp(T, t0, t1)
    CO.road_grid(c, T, seed=2)
    pts, p, ang = CO.route(0.08 + 0.75 * u)
    c.drawPath(K.path([q for q in pts if q[1] >= p[1] - 2] + [p], closed=False), paint((120, 220, 255), 0.35, stroke=10))
    log = []
    for i, q in enumerate(pts[1:-1]):
        d = math.hypot(q[0] - p[0], q[1] - p[1])
        passed = (pts.index(q) <= next(k for k in range(len(pts)) if pts[k] == q)) and q[1] > p[1] - 1 and abs(q[0] - p[0]) < 1000
        cam_on = q[1] >= p[1] - 2
        C.lens(c, q[0] + 50, q[1] - 50, 22, T, open_=0.6, ring=CO.STEEL, coat=(40, 120, 150), hot=1.0 if cam_on else 0.2)
        if cam_on:
            log.append(i)
            if d < 60:
                G.pool(c, q[0], q[1], 160, (255, 255, 255), 0.6 * (1 - d / 60))
    CO.car(c, p[0], p[1], ang, s=1.1)
    # the plate log
    CO.panel(c, 120, 330, 840, 70 + 50 * max(1, len(log)), "PLATE GLS 0034  ·  READER LOG", size=28)
    for k, i in enumerate(log[:6]):
        CO.ui_text(c, "07:%02d:%02d   CAM %02d   MATCH" % (2 + i * 2, (i * 37) % 60, 12 + i * 7), 150, 430 + k * 50, 30, (200, 240, 250))
    return st.arr


def s_n_call(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("n_call")
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(shader=K.lin((0, 0), (0, H), [(40, 48, 58), (70, 80, 92), (30, 36, 44)])))
    for i in range(5):                                             # cubicle partitions behind her
        c.drawRect(skia.Rect.MakeXYWH(-40 + i * 240, 820, 220, 420), paint((90, 98, 110), 0.6))
    CA.face(c, 540, 1130, 1.05, "nadia", T, L=COLD_L, R=COLD_R, core=0.2, amb=COLD_A, blink=blink(T, 4), talk=0.5 * abs(math.sin(T * 7)), gaze=(0.3, 0.1))
    c.drawPath(K.bez_path([(380, 1000), (540, 760), (700, 1000)]), paint((30, 32, 36), stroke=16))     # the headset
    c.drawCircle(386, 1030, 34, paint((30, 32, 36)))
    c.drawPath(K.bez_path([(386, 1060), (420, 1200), (480, 1250)]), paint((30, 32, 36), stroke=8))
    tw, tt, tf = Wx("n3", "words,") - 0.1, Wx("n3", "tone,") - 0.1, Wx("n3", "face.") - 0.1
    CO.panel(c, 90, 260, 900, 470, "CALL 1,204  ·  LIVE SCORING", size=28)
    kw = K.ease(ramp(T, tw, tw + 0.2))
    words = ["thank", "you", "for", "calling", "how", "can", "I", "help", "sorry", "about", "that", "wait"]
    x, y = 120, 380
    for i, wd in enumerate(words):
        f = K.font("jost-500", 34)
        if x + f.measureText(wd) > 950:
            x, y = 120, y + 50
        bad = wd in ("sorry", "wait")
        if bad and kw > 0:
            c.drawRect(skia.Rect.MakeLTRB(x - 6, y - 32, x + f.measureText(wd) + 6, y + 10), paint((255, 60, 60), 0.35 * kw))
        CO.ui_text(c, wd, x, y, 34, (230, 240, 246) if not bad else (255, 160, 150), a=max(0.35, kw))
        x += f.measureText(wd) + 18
    kt = K.ease(ramp(T, tt, tt + 0.2))
    CO.ui_text(c, "TONE", 120, 560, 30, CO.UI_DIM, a=kt)
    CO.bar(c, 250, 538, 420, 24, 0.42 + 0.05 * math.sin(T * 3), col=CO.AMBER, a=kt)
    CO.ui_text(c, "TENSE", 700, 560, 30, CO.AMBER, a=kt, font="jost-600")
    kf = K.ease(ramp(T, tf, tf + 0.2))
    CO.ui_text(c, "SMILE", 120, 640, 30, CO.UI_DIM, a=kf)
    CO.bar(c, 250, 618, 420, 24, 0.18, col=CO.ALERT, a=kf)
    CO.ui_text(c, "LOW", 700, 640, 30, CO.ALERT, a=kf, font="jost-600")
    if kf > 0:
        CO.target_box(c, 380, 900, 700, 1330, T, lock=kf, col=(120, 240, 255))
    score = 81 - 14 * ramp(T, tw, end("n_call"))
    CO.ui_text(c, "%d" % score, 960, 330, 56, CO.ALERT if score < 72 else CO.OK_GREEN, align="right", font="jost-600")
    return st.arr


def s_n_idle(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("n_idle")
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(shader=K.lin((0, 0), (0, H), [(150, 160, 170), (196, 204, 212), (110, 120, 132)])))
    c.drawRect(skia.Rect.MakeLTRB(330, 560, 750, 1500), paint((176, 186, 196)))
    c.drawRect(skia.Rect.MakeLTRB(330, 560, 750, 1500), paint((90, 100, 112), stroke=8))
    c.drawPath(K.rrect(470, 700, 610, 840, 12), paint((60, 70, 84)))
    c.drawCircle(540, 738, 16, paint((230, 236, 240)))
    c.drawPath(K.path([(516, 758), (564, 758), (576, 820), (504, 820)]), paint((230, 236, 240)))
    c.drawCircle(700, 1050, 16, paint((120, 130, 140)))
    secs = int(7 * 60 * ramp(T, t0, Wx("n4", "Flagged:")))
    CO.panel(c, 290, 300, 500, 170, None)
    CO.ui_text(c, "AWAY  %d:%02d" % (secs // 60, secs % 60), 540, 410, 60, CO.AMBER if secs < 400 else CO.ALERT, align="center", font="jost-600")
    tf = Wx("n4", "Flagged:") - 0.05
    if T > tf:
        k = K.ease(ramp(T, tf, tf + 0.15))
        c.save()
        c.translate(540, 1040)
        c.rotate(-8)
        c.scale(1 + 0.4 * (1 - k), 1 + 0.4 * (1 - k))
        c.drawPath(K.rrect(-300, -70, 300, 70, 10), paint(CO.ALERT, 0.92 * k))
        K.text(c, "FLAGGED: IDLE", 0, 24, 66, "jost-600", WHITE, tag="stamp", a=k)
        c.restore()
    return st.arr


def s_n_union(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("n_union")
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((24, 28, 34)))

    def page(c_, r):
        c_.drawRect(r, paint((236, 238, 240)))
        x0, y0 = r.left(), r.top()
        c_.drawRect(skia.Rect.MakeLTRB(x0, y0, r.right(), y0 + 60), paint((60, 70, 90)))
        K.text(c_, "How workers organise", x0 + 40, y0 + 150, 50, "playfair-700", (30, 30, 36), align="left", tag="screen")
        K.text(c_, "a union at work", x0 + 40, y0 + 210, 50, "playfair-700", (30, 30, 36), align="left", tag="screen")
        for i in range(8):
            c_.drawLine(x0 + 40, y0 + 280 + i * 36, r.right() - 40 - (i % 3) * 60, y0 + 280 + i * 36, paint((150, 150, 160), stroke=8))
    CO.monitor(c, 90, 360, 900, 640, T, content=page, glow=(200, 220, 240), frame=(30, 32, 38))
    c.drawPath(K.path([(40, 1020), (1040, 1020), (1080, 1100), (0, 1100)]), paint((50, 54, 62)))
    tl = Wx("n5", "logs") - 0.3
    if T > tl:
        k = K.ease(ramp(T, tl, tl + 0.25))
        CO.panel(c, 120, 1120 - 0 * k, 840, 190, "MONITORING  ·  WORK DEVICE 7731", size=26, a=k)
        CO.ui_text(c, "12:41  BROWSING  \"union\"", 150, 1230, 34, (230, 240, 246), a=k)
        CO.ui_text(c, "FLAGGED  ·  HR NOTIFIED", 150, 1284, 34, CO.ALERT, a=k, font="jost-600")
    return st.arr


def s_n_checkout(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("n_checkout")
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((30, 34, 40)))
    items = [("vitamins,", "PRENATAL VITAMINS", "14.99"), ("unscented", "UNSCENTED LOTION", "8.49"), ("lotion.", "COTTON BALLS", "3.29")]

    def screen(c_, r):
        c_.drawRect(r, paint((236, 240, 244)))
        K.text(c_, "SELF CHECKOUT", r.left() + 40, r.top() + 70, 40, "jost-600", (40, 60, 80), align="left", tag="screen")
        for i, (w, name, price) in enumerate(items):
            k = K.ease(ramp(T, Wx("n6", w) - 0.1, Wx("n6", w) + 0.05))
            y = r.top() + 170 + i * 80
            K.text(c_, name, r.left() + 40, y, 38, "jost-500", (30, 34, 40), align="left", tag="screen", a=k)
            K.text(c_, price, r.right() - 40, y, 38, "jost-500", (30, 34, 40), align="right", tag="screen", a=k)
    CO.monitor(c, 140, 300, 800, 520, T, content=screen, glow=(220, 230, 240), frame=(60, 64, 72))
    tm = Wx("n6", "lotion.") + 0.25
    if T > tm:
        k = K.ease(ramp(T, tm, tm + 0.25))
        CO.panel(c, 140, 880, 800, 300, "CUSTOMER MODEL  ·  NOT SHOWN", size=26, a=k, line=CO.ALERT)
        CO.ui_text(c, "PREGNANCY SCORE", 180, 1040, 40, (230, 240, 246), a=k)
        CO.ui_text(c, "0.87", 900, 1040, 64, CO.ALERT, a=k, align="right", font="jost-600")
        CO.ui_text(c, "send baby offers  ·  due date est.", 180, 1120, 32, CO.UI_DIM, a=k)
    return st.arr


def s_n_exhibit(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("n_exhibit")
    cam = Pr.Cam((0.0, 1.75, -0.4 + 0.2 * (T - t0)), pitch=-6, f=1050)
    Hl.gallery(c, cam, T, length=26, width=6, height=6, wall=(120, 6, 18), lights=[Pr.Light((0, 5.5, 3.2), (255, 222, 176), 1.2, 3.0)])
    lab2 = T > Wx("n6", "pregnant.") - 0.1

    def nadia(c_, sx, sy, ppm):
        C.doll(c_, sx, sy, ppm / 720 * 1.35, T, pose="stand", tint=(240, 234, 226), hair=(40, 28, 22), dress=(70, 80, 96))
    Hl.vitrine(c, cam, 0.0, 3.2, 1.2, 1.2, 1.7, 0.9, T, content=nadia, label=["NADIA K.", "34 · EXPECTING (INFERRED)" if lab2 else "34"], height=6.0, label_size=10)
    return st.arr


def _ad(c, r, i, a=1.0):
    texts = ["Newborn sale", "Size of a lemon!", "Prenatal yoga", "Strollers -40%", "Baby names?", "Due in spring?"]
    cols = [(240, 214, 220), (214, 230, 246), (226, 240, 222), (246, 236, 210), (236, 220, 246), (220, 240, 240)]
    c.drawPath(K.rrect(r.left(), r.top(), r.right(), r.bottom(), 18), paint(cols[i % 6], a))
    c.drawCircle(r.centerX(), r.top() + r.height() * 0.36, r.height() * 0.18, paint(mix(cols[i % 6], (120, 100, 110), 0.4), a))
    K.text(c, texts[i % 6], r.centerX(), r.bottom() - 20, 21, "jost-600", (60, 50, 60), tag="screen", a=a)


def s_n_face(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("n_face")
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((16, 20, 26)))
    G.pool(c, 540, 1300, 700, (200, 220, 255), 0.25)
    CA.face(c, 540, 820, 1.35, "nadia", T, L=(200, 220, 250), R=(90, 110, 150), core=0.3, amb=(50, 56, 70), talk=talk(T, "NADIA"), expr="dread",
            blink=blink(T, 6), gaze=(0.0, 0.5))

    def scr(c_, r):
        c_.drawRect(r, paint((250, 250, 252)))
        _ad(c_, skia.Rect.MakeLTRB(r.left() + 30, r.top() + 60, r.right() - 30, r.top() + 400), 1)
    CO.phone(c, 540, 1560, 0.55, T, screen=scr, tilt=-4)
    return st.arr


def s_n_vigil(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("n_vigil")
    CO.candle_crowd(c, T, nadia_x=540)
    c.drawLine(900, 200, 900, 1000, paint((40, 44, 50), stroke=14))
    C.lens(c, 880, 260, 44, T, open_=0.6, ring=CO.STEEL, coat=(40, 120, 150), hot=1.0)
    CA.face(c, 540, 1060, 0.95, "nadia_coat", T, L=(255, 170, 90), R=(60, 70, 110), core=0.45, amb=(30, 26, 30), blink=blink(T, 7), gaze=(0.0, 0.3))
    G.candle(c, 560, 1440, 0.62, T)
    tm = Wx("n8", "matches") - 0.1
    k = K.ease(ramp(stutter(T, tm, 0.12, 0.04, seed=21), tm, tm + 0.4))
    if T > tm - 0.2:
        CO.target_box(c, 380, 800, 700, 1290, T, label="MATCH · NADIA K.", conf="96%", lock=k, col=(255, 70, 70), size=30)
    return st.arr


def s_n_phone(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("n_phone")
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((20, 24, 30)))
    tb = Wx("n9", "Baby") - 0.1

    def scr(c_, r):
        c_.drawRect(r, paint((246, 248, 250)))
        if T < tb:
            K.text(c_, "MY SHIFTS", r.left() + 40, r.top() + 110, 44, "jost-600", (40, 50, 70), align="left", tag="screen")
            days = ["MON", "TUE", "WED", "THU", "FRI"]
            for i, d in enumerate(days):
                y = r.top() + 200 + i * 110
                K.text(c_, d, r.left() + 40, y, 38, "jost-500", (60, 70, 90), align="left", tag="screen")
                cutk = K.ease(ramp(T, Wx("n9", "cut.") - 0.2 + i * 0.06, Wx("n9", "cut.") + i * 0.06))
                K.text(c_, "9:00 – 17:00", r.right() - 40, y, 38, "jost-500", (60, 70, 90) if cutk < 0.5 else (190, 190, 196), align="right", tag="screen")
                if cutk > 0 and i in (1, 2, 4):
                    c_.drawLine(r.right() - 270, y - 12, r.right() - 270 + 230 * cutk, y - 12, paint(CO.ALERT, stroke=6))
            k = K.ease(ramp(T, Wx("n9", "cut.") + 0.1, Wx("n9", "cut.") + 0.4))
            c_.drawPath(K.rrect(r.left() + 30, r.top() + 780, r.right() - 30, r.top() + 930, 16), paint((255, 230, 228), k))
            K.text(c_, "Hours reduced", r.centerX(), r.top() + 840, 38, "jost-600", (180, 30, 30), tag="screen", a=k)
            K.text(c_, "Reason: productivity score", r.centerX(), r.top() + 895, 30, "jost-500", (120, 60, 60), tag="screen", a=k)
        else:
            n = int(2 + 22 * K.ease(ramp(T, tb, tb + 1.2)))
            for i in range(n):
                cx_, cy_ = i % 2, i // 2
                rr = skia.Rect.MakeXYWH(r.left() + 20 + cx_ * (r.width() / 2 - 10), r.top() + 30 + cy_ * 170, r.width() / 2 - 30, 156)
                _ad(c_, rr, i)
    CO.phone(c, 540, 860, 1.12, T, screen=scr)
    return st.arr


KNOCKS = None


def knocks():
    """The three knocks at the door (seconds): in the dead silence after "Then, a knock."""
    e = E("n10")
    return [e + 0.55, e + 0.86, e + 1.17]


def s_n_door(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    kn = max([hit(T, t, 0.22) for t in knocks()] + [0.0])
    CO.door_inside(c, T, knock=kn, light=1.0, shake=kn)
    if kn > 0:
        shake(c, T, 10 * kn, seed=31)
        c.restore()
    return st.arr


def s_n_match(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("n_match")
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((14, 18, 24)))
    CO.panel(c, 60, 260, 960, 1060, "FACE SEARCH  ·  CASE 22-0917  ·  ROBBERY", size=30)
    # left: a grainy still from a robbery - a hooded figure, a smear for a face
    r = skia.Rect.MakeLTRB(100, 360, 520, 900)
    c.drawRect(r, paint((70, 74, 80)))
    rng = K.rng_at(4, 4)
    for i in range(300):
        x, y = rng.uniform(100, 520), rng.uniform(360, 900)
        c.drawRect(skia.Rect.MakeXYWH(x, y, 4, 4), paint((110, 114, 120), 0.5))
    c.drawPath(K.smooth([(200, 900), (210, 640), (310, 560), (410, 640), (420, 900)]), paint((30, 32, 36)))
    c.drawCircle(310, 560, 80, paint((36, 38, 42)))
    c.drawOval(skia.Rect.MakeLTRB(262, 520, 358, 640), paint((120, 104, 96), 0.7, blur=10))
    CO.ui_text(c, "CCTV · 02:14", 120, 400, 26, (220, 230, 236))
    # right: her ID photo
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(560, 360, 980, 900))
    c.drawRect(skia.Rect.MakeLTRB(560, 360, 980, 900), paint((190, 200, 214)))
    CA.face(c, 770, 600, 0.82, "nadia", T, L=COLD_L, R=COLD_R, core=0.15, amb=COLD_A)
    c.restore()
    CO.ui_text(c, "DMV · NADIA K.", 580, 400, 26, (30, 40, 50))
    k = K.ease(ramp(T, Wx("n11", "match") - 0.2, Wx("n11", "match") + 0.1))
    c.drawLine(520, 630, 560, 630, paint(CO.ALERT, k, stroke=6))
    c.drawPath(K.rrect(240, 960, 840, 1100, 14), paint(CO.ALERT, 0.92 * k))
    K.text(c, "MATCH  98.1%", 540, 1056, 70, "jost-600", WHITE, tag="screen", a=k)
    K.text(c, "ARREST WARRANT REQUESTED", 540, 1190, 36, "jost-600", (255, 170, 160), tag="screen", a=K.ease(ramp(T, Wx("n11", "robbery") - 0.2, Wx("n11", "robbery") + 0.2)))
    ph = (T * 2.2) % 1.0                                            # police lights washing over everything
    c.drawPaint(G.glow_paint((255, 20, 30) if ph < 0.5 else (30, 60, 255), 0.18))
    return st.arr


def s_n_scream(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("n_scream")
    second = Wx("n12", "That's", 1) - 0.08
    ph = (T * 2.4) % 1.0
    if second < T < second + 0.55:                                  # her porcelain likeness, cracking
        cam = Pr.Cam((0.0, 2.15, 1.6), pitch=-2, f=1700)
        Hl.gallery(c, cam, T, length=20, width=6, height=6, wall=(120, 6, 18), lights=[Pr.Light((0, 5.5, 3.2), (255, 222, 176), 1.2, 3.0)])

        def nadia(c_, sx, sy, ppm):
            C.doll(c_, sx, sy, ppm / 720 * 1.35, T, pose="stand", tint=(240, 234, 226), hair=(40, 28, 22), dress=(70, 80, 96),
                   crack=K.ease(ramp(T, second, second + 0.3)), eyes=0.0)
        Hl.vitrine(c, cam, 0.0, 3.2, 1.2, 1.2, 1.7, 0.9, T, content=nadia, height=6.0)
        return st.arr
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint((10, 10, 16)))
    L = (255, 60, 60) if ph < 0.5 else (60, 90, 255)
    R = (60, 90, 255) if ph < 0.5 else (255, 60, 60)
    shake(c, T, 6, seed=33)
    CA.face(c, 540, 860, 1.6, "nadia", T, L=L, R=R, core=0.5, amb=(30, 26, 34), talk=0.4 + 0.6 * talk(T, "NADIA"), expr="scream")
    c.restore()
    return st.arr

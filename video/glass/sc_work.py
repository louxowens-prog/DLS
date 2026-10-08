"""II. THE WORKHOUSE - the same eye, at work.

w_corridor - an endless emerald office, porcelain workers at their desks; a lens on a ribbed stalk glides after you.
w_altar    - one worker enthroned like an altarpiece, measured by brass instruments, one for each word; a frieze above
             names everything else it reads.
w_towers   - ten towers on the salt flat; eight open a red eye: 8 of the 10 biggest US private employers.
w_idle     - a gilded warehouse; a worker stands still; IDLE counts up; the floor opens and she falls away; the next
             one slides into her place.
w_press    - rows of workers under glass bells; a coffered gold ceiling sinks over them; the OECD figures.
w_smile    - a worker's face under glass, headset on; a score ticks down; her eyes slide to the lens while her painted
             smile is forced wider."""
import math

import numpy as np
import skia

import cold as CO
import couture as C
import dream as D
import gel as G
import hall as Hl
import kit as K
import pers as Pr
from common import E, S, Wx, hit, shake, slow, stutter, talk, zoom
from edit import cut, end
from kit import BLACK, H, W, WHITE, mix, paint, ramp

EMER_WALL, EMER_DEEP = (8, 84, 60), (2, 30, 22)


def _desk(c, cam, X, Z, T, worker=True, pose="type", a=1.0, seed=0, head=0.0):
    P = lambda x, y, z: cam.proj((x, y, z))
    q0, q1, q2, q3 = P(X - 0.6, 0.75, Z - 0.35), P(X + 0.6, 0.75, Z - 0.35), P(X + 0.6, 0.75, Z + 0.35), P(X - 0.6, 0.75, Z + 0.35)
    if any(v is None for v in (q0, q1, q2, q3)):
        return
    fk = 1 - Pr.fog_at(cam, (X, 0.7, Z), (0, 0, 0), 0.06, 1.5)
    if worker:
        q = P(X, 0.0, Z + 0.55)
        sc = cam.scale_at((X, 0.0, Z + 0.55))
        C.doll(c, q[0], q[1], sc / 720 * 1.55, T, pose=pose, a=fk * a, tint=(236, 236, 228), head_turn=head)
    c.drawPath(K.path([q0[:2], q1[:2], q2[:2], q3[:2]]), paint((30, 24, 20), fk * a))
    f0, f1 = P(X - 0.6, 0.0, Z - 0.35), P(X + 0.6, 0.0, Z - 0.35)
    if f0 and f1:
        c.drawPath(K.path([q0[:2], q1[:2], f1[:2], f0[:2]]), paint(shader=C.gold_shader(q0[:2], q1[:2]), a=fk * a))
    s0, s1 = P(X - 0.25, 0.78, Z), P(X + 0.25, 1.1, Z)
    if s0 and s1:
        c.drawRect(skia.Rect.MakeLTRB(s0[0], s1[1], s1[0], s0[1]), G.glow_paint((120, 255, 200), 0.6 * fk * a))


def s_w_corridor(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0, t1 = cut("w_corridor"), end("w_corridor")
    cam = Pr.Cam((0.0, 1.7, -1.0 + 1.2 * (T - t0)), pitch=-3, f=820)
    Hl.gallery(c, cam, T, length=60, width=7, height=5, wall=EMER_WALL, lights=[Pr.Light((0, 4.6, z), (200, 255, 220), 0.8, 3.0) for z in (4, 10, 16, 22)],
               fog=(0, 6, 4), fog_d=0.06, panel=2.5)
    for z in np.arange(3.0, 40.0, 2.5):
        for x in (-2.3, 2.3):
            _desk(c, cam, x, z, T, seed=int(z))
    # the lens on its ribbed stalk, gliding down the corridor towards us
    zl = 26.0 - 9.0 * ramp(T, t0, t1 + 0.5)
    pts = []
    for k in range(12):
        zz = zl + 30.0 - k * 2.6
        q = cam.proj((0.0, 4.9 - 0.25 * max(0, k - 8), max(zl, zz)))
        if q is not None:
            pts.append(q[:2])
    q = cam.proj((0.0, 3.6, zl))
    if q is not None and len(pts) > 1:
        sc = cam.scale_at((0.0, 3.6, zl))
        pts.append((q[0], q[1] - sc * 0.3))
        C.ribbed(c, pts, max(4.0, sc * 0.1), max(3.0, sc * 0.08), T=T, pulse=0.5)
        C.lens(c, q[0], q[1], sc * 0.35, T, open_=0.6, ring=C.GOLD, coat=(30, 140, 100), hot=0.8)
    return st.arr


ALTAR = [("Keystrokes.", "KEYSTROKES"), ("Emails.", "EMAILS"), ("Calls.", "CALLS"), ("face.", "YOUR FACE"), ("bathroom", "BATHROOM BREAKS")]


def s_w_altar(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("w_altar")
    zoom(c, T, t0, end("w_altar"), 1.0, 1.05, 540, 860)
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(shader=K.lin((0, 0), (0, H), [EMER_DEEP, EMER_WALL, EMER_DEEP])))
    # the niche: a gilded arch, a frieze naming everything it reads
    arch = K.smooth([(150, 1500), (150, 560), (220, 400), (540, 300), (860, 400), (930, 560), (930, 1500)], closed=False)
    c.drawPath(K.path([(150, 1500), (150, 560), (540, 330), (930, 560), (930, 1500)]), paint(mix(EMER_DEEP, BLACK, 0.4)))
    c.drawPath(arch, paint(C.GOLD, stroke=16))
    c.drawPath(arch, paint(C.GOLD_HI, 0.6, stroke=4))
    G.pool(c, 540, 820, 520, (200, 255, 220), 0.18)
    frieze = "PRODUCTIVITY · LOCATION · DRIVING · CUSTOMER CONVERSATIONS"
    K.text(c, frieze, 540, 270, 27, "cinzel-600", C.GOLD_HI, tag="label")
    # the worker at her desk, enthroned
    DS, DY = 1.1, 1345
    # she moves the way the dream moves things: a jerk of the head towards each instrument as it wakes, then dead still
    st_ = stutter(T, t0, 0.45, 0.08, seed=4)
    C.doll(c, 540, DY, DS, T, pose=("type", "candle", 0.5 + 0.5 * math.sin(st_ * 2.3)), tint=(240, 236, 228), head_turn=0.75 * math.sin(st_ * 1.7))
    c.drawPath(K.path([(330, 1180), (750, 1180), (790, 1260), (290, 1260)]), paint(shader=C.gold_shader((290, 0), (790, 0))))
    c.drawRect(skia.Rect.MakeLTRB(290, 1260, 790, 1340), paint((24, 20, 18)))
    head_y = DY - 680 * DS
    # the instruments, appearing word by word
    for i, (w, label) in enumerate(ALTAR):
        t = Wx("w2", w) - 0.05
        k = K.ease(ramp(T, t, t + 0.18))
        if k <= 0:
            continue
        pos = [(260, 960), (820, 960), (260, 640), (540, 520), (820, 640)][i]
        x, y = pos
        if i == 3:                                                  # a scanning halo round her head
            c.drawCircle(540, head_y, 135 * k, paint((120, 255, 200), 0.8 * k, stroke=4))
            CO.target_box(c, 455, head_y - 105, 625, head_y + 110, T, lock=k, col=(120, 255, 200))
            c.drawPath(K.rrect(410, head_y - 205, 670, head_y - 150, 8), paint((2, 26, 18), 0.85 * k))
            K.text(c, "ENGAGED 61%", 540, head_y - 164, 34, "jost-600", (160, 255, 220), tag="label", a=k)
            continue
        c.drawCircle(x, y, 92 * k, paint(shader=C.gold_shader((x - 92, y), (x + 92, y)), a=k))
        c.drawCircle(x, y, 74 * k, paint((14, 30, 24), k))
        if i == 0:
            val = "%d" % int(4100 + (T - t) * 900)
            K.text(c, val, x, y + 14, 40, "jost-600", (160, 255, 220), tag="label", a=k)
        elif i == 1:
            c.drawPath(K.path([(x - 46, y - 30), (x + 46, y - 30), (x + 46, y + 30), (x - 46, y + 30)]), paint((236, 230, 214), k))
            c.drawPath(K.path([(x - 46, y - 30), (x, y + 6), (x + 46, y - 30)], closed=False), paint((120, 110, 100), k, stroke=3))
            c.drawCircle(x, y + 8, 12, paint((170, 10, 20), k))
        elif i == 2:
            for j in range(9):
                hh = 10 + 30 * abs(math.sin(T * 9 + j))
                c.drawLine(x - 40 + j * 10, y - hh / 2, x - 40 + j * 10, y + hh / 2, paint((160, 255, 220), k, stroke=5))
        elif i == 4:
            c.drawPath(K.rrect(x - 28, y - 44, x + 28, y + 30, 6), paint((236, 230, 214), k))
            secs = int(7 * 60 + 12 * ramp(T, t, t + 1.0))
            K.text(c, "%d:%02d" % (secs // 60, secs % 60), x, y + 64, 30, "jost-600", (255, 120, 110), tag="label", a=k)
        for j, ln in enumerate(label.split(" ") if len(label) > 10 else [label]):    # long names stack, clear of the arch
            K.text(c, ln, x, y + 136 + j * 34, 30, "cinzel-600", C.GOLD_HI, tag="label", a=k)
    c.restore()
    return st.arr


def _tower(c, cam, X, Z, T, lit, hgt=9.0, w=1.2):
    P = lambda x, y, z: cam.proj((x, y, z))
    b0, b1, t0_, t1_ = P(X - w / 2, 0.0, Z), P(X + w / 2, 0.0, Z), P(X - w / 2 * 0.7, hgt, Z), P(X + w / 2 * 0.7, hgt, Z)
    if any(v is None for v in (b0, b1, t0_, t1_)):
        return
    c.drawPath(K.path([b0[:2], b1[:2], t1_[:2], t0_[:2]]), paint(shader=K.lin(b0[:2], b1[:2], [(30, 40, 36), (90, 110, 100), (16, 22, 20)])))
    c.drawPath(K.path([b0[:2], b1[:2], t1_[:2], t0_[:2]]), paint(C.GOLD, 0.7, stroke=2))
    tip = P(X, hgt + 1.2, Z)
    if tip:
        c.drawPath(K.path([t0_[:2], t1_[:2], tip[:2]]), paint(shader=C.gold_shader(t0_[:2], t1_[:2])))
    q = P(X, hgt - 1.0, Z - w * 0.36)
    if q:
        sc = cam.scale_at((X, hgt - 1.0, Z))
        if lit > 0:                                                 # an eye opening: a red bloom, a beam down to the salt
            G.pool(c, q[0], q[1], sc * 2.2, (255, 40, 40), 0.75 * lit)
            G.beam(c, (q[0], q[1]), (q[0] - sc * 3 * lit, H), (q[0] + sc * 3 * lit, H), (255, 60, 60), 0.22 * lit)
        C.lens(c, q[0], q[1], sc * (0.34 + 0.16 * lit), T, open_=0.08 + 0.7 * lit, ring=C.GOLD, coat=(150, 30, 40) if lit > 0 else (30, 20, 24),
               hot=lit, a=1.0)


def s_w_towers(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0, t1 = cut("w_towers"), end("w_towers")
    cam = D.salt_cam(1.5, 6.0, 900, z=-4.0 + 1.0 * ramp(T, t0, t1))
    D.salt_flat(c, cam, T, sky_cols=((10, 40, 30), (40, 110, 90), (170, 210, 196)))
    # the figure is on screen as the word "Eight" is spoken; the eight eyes open in a stutter while the sentence runs
    tk = Wx("w3", "Eight") + 0.05
    order = [0, 9, 4, 5, 2, 7, 3, 6, 1, 8]
    lit_set = order[:8]
    for i in range(10):
        X = -9.0 + i * 2.0
        j = lit_set.index(i) if i in lit_set else None
        lit = 0.0 if j is None else K.ease(ramp(T, tk + j * 0.11, tk + j * 0.11 + 0.12))
        _tower(c, cam, X, 18.0, T, lit)
    from cards import spaced
    ka = K.ease(ramp(T, tk - 0.1, tk + 0.15))
    spaced(c, "8 / 10", 540, 470, 150, "italiana-400", 0.12, C.GOLD_HI, ka, tag="label")
    K.text(c, "of America's 10 biggest private employers", 540, 560, 36, "cormorant-600", (220, 236, 228), tag="label", a=ka)
    return st.arr


def s_w_idle(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0, t1 = cut("w_idle"), end("w_idle")
    cam = Pr.Cam((0.0, 1.8, -2.0 + 0.5 * (T - t0)), pitch=-6, f=880)
    Hl.gallery(c, cam, T, length=60, width=5.5, height=9, wall=(40, 30, 8), frames=False, lights=[Pr.Light((0, 8.5, z), (255, 220, 150), 1.0, 4.0) for z in (4, 12, 20)],
               fog=(6, 4, 0), fog_d=0.05, lamps=False)
    for z in np.arange(1.0, 50.0, 3.0):                             # shelving: gilded racks receding
        for X in (-2.75, 2.75):
            p0, p1 = cam.proj((X, 0.0, z)), cam.proj((X, 8.0, z))
            if p0 and p1:
                sc = cam.scale_at((X, 0.0, z))
                fk = 1 - Pr.fog_at(cam, (X, 0, z), (0, 0, 0), 0.05, 1.0)
                c.drawLine(p0[0], p0[1], p1[0], p1[1], paint(C.GOLD, fk, stroke=max(1, sc * 0.08)))
                for yy in np.arange(0.8, 8.0, 1.4):
                    q0, q1 = cam.proj((X, yy, z)), cam.proj((X, yy, z + 3.0))
                    if q0 and q1:
                        c.drawLine(q0[0], q0[1], q1[0], q1[1], paint(C.GOLD_LO, fk, stroke=max(1, sc * 0.05)))
                        box = cam.proj((X - np.sign(X) * 0.3, yy + 0.4, z + 1.5))
                        if box:
                            bs = cam.scale_at((X, yy, z + 1.5)) * 0.5
                            c.drawRect(skia.Rect.MakeXYWH(box[0] - bs / 2, box[1] - bs / 2, bs, bs * 0.8), paint((150, 110, 60), fk))
    tf = Wx("w4", "firings") - 0.1
    # the worker standing still in the aisle; the floor opening under her; the next sliding in
    fall = max(0.0, T - tf)
    q = cam.proj((0.0, 0.0, 6.0))
    sc = cam.scale_at((0.0, 0.0, 6.0))
    trap = K.ease(ramp(T, tf - 0.1, tf + 0.1)) * (1 - K.ease(ramp(T, tf + 1.3, tf + 1.6)))
    if trap > 0:
        t0q, t1q, t2q, t3q = cam.proj((-0.7, 0, 5.4)), cam.proj((0.7, 0, 5.4)), cam.proj((0.7, 0, 6.6)), cam.proj((-0.7, 0, 6.6))
        c.drawPath(K.path([t0q[:2], t1q[:2], t2q[:2], t3q[:2]]), paint((0, 0, 0), trap))
    if fall < 1.2:
        drop = 0.5 * 9.8 * (slow(T, tf, 0.35) - tf) ** 2 if T > tf else 0.0
        c.save()
        if T > tf:
            c.clipRect(skia.Rect.MakeLTRB(0, 0, W, q[1] + 4))
        C.doll(c, q[0], q[1] + drop * sc, sc / 720 * 1.7, T, pose="stand", tint=(240, 236, 228))
        c.restore()
    if T > tf + 1.3:                                                # the next one, delivered into place
        k = K.ease(ramp(T, tf + 1.3, tf + 1.9))
        C.doll(c, q[0] + (1 - k) * sc * 3.5, q[1], sc / 720 * 1.7, T, pose="stand", tint=(240, 236, 228))
    # the idle counter over the aisle
    idle = 47 + int(385 * ramp(T, t0, tf))
    col = (255, 90, 80) if idle > 300 else C.GOLD_HI
    CO.panel(c, 300, 300, 480, 170, None)
    K.text(c, "IDLE", 540, 360, 34, "jost-600", (160, 200, 190), tag="screen")
    K.text(c, "%02d:%02d:%02d" % (idle // 3600, (idle // 60) % 60, idle % 60), 540, 440, 64, "jost-600", col, tag="screen")
    if T > tf:
        k = K.ease(ramp(T, tf, tf + 0.2))
        c.drawPath(K.rrect(260, 520, 820, 610, 10), paint((200, 20, 30), 0.9 * k))
        K.text(c, "AUTO-TERMINATION ISSUED", 540, 580, 36, "jost-600", WHITE, tag="screen", a=k)
    return st.arr


def s_w_press(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0, t1 = cut("w_press"), end("w_press")
    u = ramp(T, t0, t1)
    cam = Pr.Cam((0.0, 2.4, -1.5), pitch=-12, f=880)
    ceil = 5.0 - 2.3 * K.ease(u)
    Hl.gallery(c, cam, T, length=40, width=9, height=ceil, wall=EMER_WALL, lights=[Pr.Light((0, ceil - 0.2, z), (220, 255, 230), 0.9, 3.0) for z in (4, 10, 16)],
               fog=(0, 6, 4), fog_d=0.07, frames=False, lamps=False, ceiling=(60, 46, 10))
    ce = Pr.ceiling(-4.5, 4.5, -1.0, 40.0, ceil)                    # coffers in the sinking gold ceiling
    with ce.draw(c, cam) as pc:
        if pc is not None:
            for i in range(9):
                for j in range(41):
                    pc.drawRect(skia.Rect.MakeXYWH(i * Pr.U + 8, j * Pr.U + 8, Pr.U - 16, Pr.U - 16), paint(shader=C.gold_shader((i * Pr.U, 0), ((i + 1) * Pr.U, 0))))
            Pr.depth_fog(pc, ce, cam, (0, 6, 4), 0.07, 1.0)
    for z in np.arange(2.0, 24.0, 2.2):
        for X in (-3.0, -1.0, 1.0, 3.0):
            _desk(c, cam, X, z, T, pose="type", head=-0.2)
            q0, q1 = cam.proj((X - 0.55, 0.75, z + 0.5)), cam.proj((X + 0.55, 2.0, z + 0.5))
            if q0 and q1:                                           # a glass bell over each
                fk = 1 - Pr.fog_at(cam, (X, 1, z), (0, 0, 0), 0.07, 1.0)
                bell = K.smooth([(q0[0], q0[1]), (q0[0], q1[1] + (q0[1] - q1[1]) * 0.3), ((q0[0] + q1[0]) / 2, q1[1]), (q1[0], q1[1] + (q0[1] - q1[1]) * 0.3), (q1[0], q0[1])], closed=False)
                c.drawPath(bell, paint((210, 255, 236), 0.5 * fk, stroke=2))
                c.drawPath(bell, paint((210, 255, 236), 0.06 * fk))
    # the figures, on a dark panel so they read over the gold: a small table, there from the start of the line
    k = K.ease(ramp(T, t0 + 0.2, t0 + 0.6))
    c.drawPath(K.rrect(80, 240, 1000, 720, 16), paint((2, 26, 18), 0.9 * k))
    c.drawPath(K.rrect(80, 240, 1000, 720, 16), paint(C.GOLD, 0.9 * k, stroke=3))
    K.text(c, "OECD SURVEYS · 2022", 540, 312, 44, "cinzel-600", C.GOLD_HI, tag="label", a=k)
    K.text(c, "workers whose employer's AI collected data on them", 540, 366, 32, "cormorant-600", (226, 240, 232), tag="label", a=k)
    K.text(c, "FINANCE", 680, 440, 24, "cinzel-600", (200, 226, 214), tag="label", a=k)
    K.text(c, "MANUFACTURING", 872, 440, 24, "cinzel-600", (200, 226, 214), tag="label", a=k)
    c.drawLine(120, 462, 960, 462, paint(C.GOLD, 0.5 * k, stroke=1.5))
    rows = (("more pressure to perform", "62%", "56%", Wx("w5", "workers") - 0.1), ("worried about privacy", "62%", "51%", Wx("w5", "told") + 0.15))
    for i, (txt, a_, b_, w_) in enumerate(rows):
        kk = K.ease(ramp(T, w_, w_ + 0.25)) * k
        y = 548 + i * 104
        K.text(c, txt, 125, y - 6, 38, "cormorant-600", (240, 250, 244), align="left", tag="label", a=kk)
        K.text(c, a_, 680, y, 64, "jost-600", (255, 232, 160), tag="label", a=kk)
        K.text(c, b_, 872, y, 64, "jost-600", (255, 232, 160), tag="label", a=kk)
    return st.arr


def s_w_smile(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0, t1 = cut("w_smile"), end("w_smile")
    u = ramp(T, t0, t1)
    zoom(c, T, t0, t1, 1.0, 1.12, 540, 900)
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(shader=K.rad((540, 900), 1100, [EMER_WALL, EMER_DEEP, (0, 6, 4)])))
    k = K.ease(ramp(stutter(T, Wx("w6", "Smile.") - 0.05, period=0.22, move=0.06, fps=12, seed=7), Wx("w6", "Smile.") - 0.05, Wx("w6", "Smile.") + 0.7))
    # a worker's face, not hers: no gold seam, a headset band, open glass eyes that slide to the lens while the mouth
    # is forced wider in jerks, too wide, held
    c.drawPath(K.smooth([(250, 980), (290, 330), (540, 250), (790, 330), (830, 980)], closed=False), paint((26, 30, 30), stroke=22))
    c.drawPath(K.rrect(214, 900, 286, 1060, 26), paint((26, 30, 30)))
    C.mask(c, 540, 900, 2.0, T, eyes=0.9, iris="glass", iris_col=(70, 110, 120), look=(0.7 * k, -0.1), tint=(232, 228, 220),
           lips=(150, 10, 30), smile=0.9 * k, seam=False, brows=0.9)
    # the glass bell, and her eye reflected in it
    c.drawPath(K.smooth([(120, 1700), (120, 600), (300, 260), (540, 200), (780, 260), (960, 600), (960, 1700)], closed=False), paint((210, 255, 236), 0.5, stroke=4))
    c.drawPath(K.smooth([(200, 1600), (200, 650), (330, 360)], closed=False), paint(WHITE, 0.3, stroke=10, blur=4))
    C.lens(c, 820, 420, 70, T, open_=0.5, ring=C.GOLD, coat=(150, 30, 40), hot=0.8, a=0.45)
    score = 71.3 - 9.4 * ramp(T, t0 + 0.4, t1)
    CO.panel(c, 330, 280, 420, 130, None)
    K.text(c, "SCORE %.1f" % score, 540, 365, 54, "jost-600", (255, 120, 110) if score < 68 else (160, 255, 220), tag="screen")
    c.restore()
    return st.arr

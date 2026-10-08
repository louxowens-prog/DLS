"""IV. THE SCALES - the same machinery in the hands of power; then the descent to her favourite exhibit.

t_metro      - a palatial red-marble metro hall; commuters move in stutter; one carries a placard; a box locks onto
               her and two lacquer guards step in.
t_gate       - a tiled gate; women walk through; a scan line passes; one without a headscarf is boxed in red.
t_lineup     - fifteen faces in fifteen cases: MATCH, then WRONG.
t_library    - a reading room; books close themselves; mouths smooth over; on the wall the line falls and stays down.
t_hush       - dead silence: the gallery, every exhibit still, eyes shut.
t_scales     - the scales slam down; every exhibit opens its eyes and turns to you.
d_procession - the Curator walks away down an endless hall, her train reaching all the way back to us; at the end a
               covered case glows."""
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
import props as P
from common import E, S, Wx, hit, shake, slow, stutter, talk, zoom
from edit import cut, end
from kit import BLACK, H, W, WHITE, mix, paint, ramp

CRIMSON_WALL = (130, 8, 20)


def _arches(c, cam, length, width, height, step=4.0, col=C.GOLD, a=1.0):
    z = 2.0
    while z < length:
        pts = []
        for k in range(17):
            ang = math.pi * k / 16
            pts.append((-width / 2 + width / 2 * (1 - math.cos(ang)), height - 1.2 + 1.2 * math.sin(ang)))
        P_ = [cam.proj((x, y, z)) for x, y in pts]
        if all(p is not None for p in P_):
            fk = 1 - Pr.fog_at(cam, (0, height, z), (0, 0, 0), 0.06, 1.0)
            c.drawPath(K.path([p[:2] for p in P_], closed=False), paint(col, a * fk, stroke=max(2, cam.scale_at((0, height, z)) * 0.12)))
        z += step


def s_t_metro(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0, t1 = cut("t_metro"), end("t_metro")
    cam = Pr.Cam((0.0, 1.7, -2.0), pitch=-2, f=860)
    Hl.gallery(c, cam, T, length=50, width=8, height=7, wall=CRIMSON_WALL, lights=[Pr.Light((0, 6.2, z), (255, 210, 150), 1.0, 3.5) for z in (3, 9, 15, 21, 27)],
               fog=(8, 0, 2), fog_d=0.06, panel=4.0)
    _arches(c, cam, 50, 8, 7)
    for z in (3.0, 9.0, 15.0, 21.0, 27.0, 33.0):                    # chandeliers
        q = cam.proj((0.0, 6.0, z))
        if q:
            sc = cam.scale_at((0.0, 6.0, z))
            fk = 1 - Pr.fog_at(cam, (0, 6, z), (0, 0, 0), 0.06, 1.0)
            for k in range(7):
                ang = math.pi * k / 6
                c.drawCircle(q[0] + math.cos(ang) * sc * 0.6, q[1] + math.sin(ang) * sc * 0.15, max(1.5, sc * 0.07), G.glow_paint((255, 230, 180), fk))
            G.pool(c, q[0], q[1], sc * 1.6, (255, 210, 150), 0.3 * fk)
    td = Wx("t2", "detain") - 0.1
    ts = stutter(T, t0, period=0.5, move=0.14, seed=6)
    walkers = [(-2.4, 9.0), (2.2, 8.0), (-1.0, 13.0), (1.6, 15.0), (-2.8, 18.0), (0.6, 21.0), (2.6, 24.0)]
    target = (0.0, 5.8)
    for i, (x, z) in sorted(enumerate(walkers + [target]), key=lambda p: -p[1][1]):
        zz = z - 1.4 * (ts - t0) if T < td else z - 1.4 * (td - t0)
        q = cam.proj((x, 0.0, zz))
        if q is None:
            continue
        sc = cam.scale_at((x, 0.0, zz))
        fk = 1 - Pr.fog_at(cam, (x, 0, zz), (0, 0, 0), 0.06, 1.0)
        is_t = (x, z) == target
        C.doll(c, q[0], q[1], sc / 720 * 1.7, T, pose="walk" if (int(ts * 4) + i) % 2 else "stand", tint=(236, 230, 222), a=fk,
               sign=(200, 20, 30) if is_t else None, eyes=1.0 if is_t and T > td else 0.0)
        if is_t:
            tq = cam.proj((x, 1.75, zz))
            k = K.ease(ramp(T, td, td + 0.25))
            if k > 0:
                CO.target_box(c, tq[0] - sc * 0.32, tq[1] - sc * 0.3, tq[0] + sc * 0.32, tq[1] + sc * 0.28, T, label="PROTESTER · 97%", lock=k,
                              col=(255, 60, 60), size=30)
                for sd in (-1, 1):                                  # two lacquer guards stepping in from the sides
                    gx = x + sd * (3.4 - 2.4 * K.ease(ramp(stutter(T, td + 0.2, 0.3, 0.07, seed=sd + 9), td + 0.2, td + 1.2)))
                    gq = cam.proj((gx, 0.0, zz + 0.3))
                    if gq:
                        gs = cam.scale_at((gx, 0.0, zz + 0.3))
                        C.doll(c, gq[0], gq[1], gs / 720 * 2.0, T, pose="stand", tint=(24, 22, 28), shade=(6, 6, 8), lens_face=True, joints=C.GOLD_LO)
    # the camera dome in the arch above
    dq = cam.proj((0.0, 5.6, 7.0))
    if dq:
        C.lens(c, dq[0], dq[1], 46, T, open_=0.6, ring=C.GOLD, coat=(150, 30, 40), hot=1.0 if T > td else 0.3)
    return st.arr


def s_t_gate(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0, t1 = cut("t_gate"), end("t_gate")
    zoom(c, T, t0, t1, 1.0, 1.05, 540, 1000)
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(shader=K.lin((0, 0), (0, H), [(6, 40, 44), (14, 90, 96), (4, 30, 34)])))
    # a monumental tiled gate: a pointed arch framed in geometric tilework
    c.drawRect(skia.Rect.MakeLTRB(90, 260, 990, 1500), paint((10, 70, 78)))
    for i in range(14):                                            # tile lattice
        for j in range(20):
            x, y = 110 + i * 62, 280 + j * 60
            c.drawPath(K.path([(x + 31, y), (x + 62, y + 30), (x + 31, y + 60), (x, y + 30)]), paint((40, 160, 170) if (i + j) % 2 else (20, 110, 120), 0.9))
            c.drawCircle(x + 31, y + 30, 6, paint(C.GOLD, 0.8))
    arch = K.path([(300, 1500), (300, 820), (420, 600), (540, 470), (660, 600), (780, 820), (780, 1500)])
    c.drawPath(arch, paint((6, 16, 20)))
    c.drawPath(arch, paint(C.GOLD, stroke=12))
    G.pool(c, 540, 1300, 400, (200, 255, 250), 0.18, squash=0.4)
    # the camera over the arch
    C.lens(c, 540, 400, 48, T, open_=0.6, ring=C.GOLD, coat=(30, 140, 150), hot=0.6)
    scan_y = 640 + 600 * ((T - t0) * 0.6 % 1.0)
    flag_at = Wx("t3", "without") - 0.1
    walk = 0.12 * (T - t0)
    # (x offset, depth 0 far .. 1 near): a procession coming through the arch towards us
    walkers = [(-110, 0.05), (120, 0.2), (-190, 0.36), (0, 0.5), (210, 0.62), (-240, 0.78)]
    for i, (dx, d0) in sorted(enumerate(walkers), key=lambda p: p[1][1]):
        d = min(1.0, d0 + walk)
        s = 0.26 + 0.36 * d
        y = 1000 + 340 * d
        x = 540 + dx * (0.6 + 0.9 * d)
        bare = i == 3
        C.doll(c, x, y, s, T, pose="walk" if int((T + i * 0.3) * 3) % 2 else "stand", tint=(236, 230, 222), dress=(30, 34, 50) if not bare else (70, 44, 54),
               scarf=None if bare else ((26, 30, 46) if i % 2 else (60, 30, 44)), hair=(26, 18, 16) if bare else None, eyes=0.0)
        hx, hy = x, y - (560 + 120) * s
        if bare and T > flag_at:
            k = K.ease(ramp(T, flag_at, flag_at + 0.2))
            CO.target_box(c, hx - 100 * s, hy - 110 * s, hx + 100 * s, hy + 110 * s, T, label="FLAGGED", lock=k, col=(255, 60, 60), size=30)
        elif abs(hy - scan_y) < 120:
            CO.target_box(c, hx - 90 * s, hy - 100 * s, hx + 90 * s, hy + 100 * s, T, lock=1.0, col=(120, 255, 220))
    c.drawLine(300, scan_y, 780, scan_y, G.glow_paint((120, 255, 220), 0.7, blur=3))
    c.restore()
    return st.arr


LINEUP = ["w_dark", "m_d", "f_a", "m_b", "f_c", "int2", "m_d", "f_b", "w_dark", "m_b", "int1", "f_a", "m_light", "m_d", "f_c"]


def s_t_lineup(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0, t1 = cut("t_lineup"), end("t_lineup")
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(shader=K.lin((0, 0), (0, H), [(20, 2, 6), (70, 4, 12), (16, 0, 4)])))
    tw = Wx("t4", "wrongly") - 0.1
    tm = Wx("t4", "fifteen") - 0.1
    for i, who in enumerate(LINEUP):
        col, row = i % 3, i // 3
        x, y = 210 + col * 330, 330 + row * 196
        c.drawRect(skia.Rect.MakeLTRB(x - 140, y - 88, x + 140, y + 88), paint((10, 4, 8)))
        CA.face(c, x, y - 10, 0.36, who, T, L=(255, 236, 214), R=(160, 120, 140), core=0.3, amb=(60, 40, 50), porc=0.45, neck=False, glaze=0.6)
        c.drawRect(skia.Rect.MakeLTRB(x - 140, y - 88, x + 140, y + 88), paint(shader=K.lin((x - 140, y - 88), (x + 140, y + 88), [(255, 255, 255, 0.12), (255, 255, 255, 0.0)])))
        c.drawRect(skia.Rect.MakeLTRB(x - 140, y - 88, x + 140, y + 88), paint(C.GOLD, stroke=4))
        tk = tm + i * 0.07
        if T > tk:
            wrong = T > tw + i * 0.05
            lab = "WRONG MATCH" if wrong else "MATCH"
            colr = (255, 60, 60) if wrong else (255, 220, 120)
            k = K.ease(ramp(T, tk, tk + 0.15))
            c.drawRect(skia.Rect.MakeLTRB(x - 120, y + 34, x + 120, y + 76), paint((10, 4, 8), 0.85 * k))
            K.text(c, lab, x, y + 66, 28, "jost-600", colr, tag="stamp", a=k)
    from cards import spaced
    spaced(c, "AT LEAST 15", 540, 1290, 56, "italiana-400", 0.12, C.GOLD_HI, K.ease(ramp(T, tm, tm + 0.3)), tag="label")
    return st.arr


def s_t_library(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0, t1 = cut("t_library"), end("t_library")
    u = ramp(T, t0, t1)
    cam = Pr.Cam((0.0, 2.6, -2.0 + 1.4 * u), pitch=-11, f=880)
    Hl.gallery(c, cam, T, length=36, width=10, height=8, wall=(90, 6, 16), lights=[Pr.Light((0, 7.5, z), (255, 220, 160), 0.9, 4.0) for z in (4, 12, 20)],
               fog=(6, 0, 2), fog_d=0.05, panel=3.0, lamps=False)
    # the graph on the far wall: views of terrorism-related articles, falling in June 2013 and staying down
    gq0, gq1 = cam.proj((-4.0, 7.2, 30.0)), cam.proj((4.0, 3.2, 30.0))
    tg = Wx("t5", "reading") - 0.2
    if gq0 and gq1:
        x0, y0, x1, y1 = gq0[0], gq0[1], gq1[0], gq1[1]
        c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint((20, 4, 8), 0.9))
        c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(C.GOLD, stroke=3))
    pts = [(0.0, 0.32), (0.1, 0.30), (0.2, 0.34), (0.3, 0.31), (0.4, 0.33), (0.45, 0.30), (0.48, 0.62), (0.55, 0.66), (0.65, 0.64), (0.75, 0.67),
           (0.85, 0.65), (1.0, 0.68)]
    gk = K.ease(ramp(T, tg, tg + 1.4))
    GX0, GY0, GX1, GY1 = 140, 300, 940, 760
    c.drawPath(K.rrect(GX0 - 30, GY0 - 70, GX1 + 30, GY1 + 70, 12), paint((16, 2, 6), 0.88 * min(1.0, gk * 3)))
    c.drawPath(K.rrect(GX0 - 30, GY0 - 70, GX1 + 30, GY1 + 70, 12), paint(C.GOLD, 0.9 * min(1.0, gk * 3), stroke=3))
    if gk > 0:
        K.text(c, "VIEWS OF TERRORISM-RELATED ARTICLES", 540, GY0 - 16, 30, "cinzel-600", C.GOLD_HI, tag="label", a=min(1.0, gk * 3))
        n = max(2, int(len(pts) * gk) + 1)
        P_ = [(GX0 + (GX1 - GX0) * px, GY0 + 30 + (GY1 - GY0 - 60) * py) for px, py in pts[:n]]
        c.drawPath(K.path(P_, closed=False), paint(C.GOLD_HI, stroke=6))
        c.drawPath(K.path(P_, closed=False), G.glow_paint(C.GOLD_HI, 0.4, blur=6))
        mx = GX0 + (GX1 - GX0) * 0.46
        c.drawLine(mx, GY0 + 10, mx, GY1 - 10, paint((255, 120, 110), 0.8, stroke=2))
        K.text(c, "JUNE 2013", mx, GY1 + 40, 28, "jost-600", (255, 150, 140), tag="label", a=min(1.0, gk * 3))
        K.text(c, "2012", GX0 + 40, GY1 + 40, 26, "jost-500", (230, 210, 200), tag="label", a=min(1.0, gk * 3))
        K.text(c, "2014", GX1 - 40, GY1 + 40, 26, "jost-500", (230, 210, 200), tag="label", a=min(1.0, gk * 3))
    # the readers at long tables, the green lamps, the books closing one by one, the mouths smoothing over
    rng = K.rng_at(3, 3)
    tc = Wx("t5", "quiet:") - 0.1
    for row, z in enumerate(np.arange(3.0, 24.0, 3.0)):
        for X in (-3.2, -1.1, 1.1, 3.2):
            q = cam.proj((X, 0.0, z + 0.6))
            if q is None:
                continue
            sc = cam.scale_at((X, 0.0, z + 0.6))
            fk = 1 - Pr.fog_at(cam, (X, 0, z), (0, 0, 0), 0.05, 1.0)
            tclose = tc + rng.uniform(0.0, 3.5)
            shut = K.ease(ramp(T, tclose, tclose + 0.15))
            C.doll(c, q[0], q[1], sc / 720 * 1.5, T, pose="type", tint=(236, 230, 222), a=fk, mouth=shut < 0.5, head_tilt=8 * shut * (1 if X > 0 else -1))
            t0q, t1q = cam.proj((X - 0.7, 0.78, z)), cam.proj((X + 0.7, 0.78, z))
            if t0q and t1q:
                c.drawRect(skia.Rect.MakeLTRB(t0q[0], t0q[1] - sc * 0.04, t1q[0], t0q[1] + sc * 0.1), paint((40, 20, 10), fk))
                bq = cam.proj((X, 0.8, z - 0.1))
                P.book(c, bq[0], bq[1], sc / 300 * 0.25, T, open_=1 - shut, a=fk)
                lq = cam.proj((X + 0.5, 1.2, z))
                G.pool(c, lq[0], lq[1] + sc * 0.2, sc * 0.6, (120, 255, 160), 0.25 * fk * (1 - 0.6 * shut))
                c.drawOval(skia.Rect.MakeLTRB(lq[0] - sc * 0.15, lq[1] - sc * 0.05, lq[0] + sc * 0.15, lq[1] + sc * 0.05), paint((20, 120, 60), fk))
    return st.arr


def _gallery_of_exhibits(c, T, eyes=0.0, turn=0.0, slam=0.0):
    cam = Pr.Cam((0.0, 1.8, -1.0), pitch=-3, f=820)
    if slam > 0:
        shake(c, T, 22 * slam, seed=11)
    else:
        c.save()
    Hl.gallery(c, cam, T, length=40, width=8, height=7, wall=CRIMSON_WALL, lights=[Pr.Light((0, 6.5, z), (255, 210, 160), 0.9, 3.0) for z in (3, 9, 15, 21)],
               fog=(6, 0, 2), fog_d=0.07)
    for i, z in enumerate((3.0, 6.5, 10.0, 13.5, 17.0, 20.5)):
        for sd in (-1, 1):
            X = sd * 2.6

            def fig(c_, sx, sy, ppm, sd=sd, i=i):
                C.doll(c_, sx, sy, ppm / 720 * 1.3, T, pose="stand", tint=(240, 234, 226), eyes=eyes, head_turn=-sd * 0.9 * (1 - turn))
            Hl.vitrine(c, cam, X, z, 1.1, 1.1, 1.6, 0.8, T, content=fig, height=7.0, fog=(6, 0, 2), fog_d=0.07)
    return cam


def s_t_hush(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    cam = _gallery_of_exhibits(c, T, eyes=0.0, turn=0.0)
    Hl.scales(c, 540, 1160, 0.42, T, tilt=0.0, eye=0.3)
    c.restore()
    return st.arr


def s_t_scales(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("t_scales")
    tt0 = Wx("t6", "Then") - 0.2
    if T > tt0:                                                     # close: one exhibit turns its head to you, eyes open
        u = T - tt0
        cam = Pr.Cam((0.0, 1.55, 0.6), pitch=-1, f=1500)
        Hl.gallery(c, cam, T, length=30, width=6, height=7, wall=CRIMSON_WALL, lights=[Pr.Light((0, 6.5, 3.0), (255, 210, 160), 1.2, 3.0)],
                   fog=(6, 0, 2), fog_d=0.07)
        turn = K.ease(ramp(stutter(T, tt0, 0.16, 0.05, seed=13), tt0, tt0 + 0.5))

        def fig(c_, sx, sy, ppm):
            C.doll(c_, sx, sy, ppm / 720 * 1.3, T, pose="stand", tint=(240, 234, 226), eyes=1.0, head_turn=-0.95 * (1 - turn), head_tilt=-14 * (1 - turn))
        if u < 0.08:
            shake(c, T, 16, seed=14)
        else:
            c.save()
        Hl.vitrine(c, cam, 0.0, 3.0, 1.1, 1.1, 1.6, 0.8, T, content=fig, height=7.0)
        c.restore()
        return st.arr
    ts = S("t6") - 0.02
    slam = hit(T, ts, 0.35)
    tilt = 26 * K.ease(ramp(T, ts - 0.04, ts + 0.06))
    tt = Wx("t6", "Then") - 0.15
    turn = K.ease(ramp(stutter(T, tt, 0.18, 0.05, seed=12), tt, tt + 0.6))
    cam = _gallery_of_exhibits(c, T, eyes=1.0 if T > ts else 0.0, turn=turn, slam=slam)

    def you(c_, px, py, s):
        C.doll(c_, px, py - 4 * s, 0.24 * s / 0.42, T, pose="stand", tint=(255, 250, 244))

    def eyes_heap(c_, px, py, s):
        for k, (dx, dy) in enumerate(((-90, 0), (0, 0), (90, 0), (-45, 52), (45, 52), (0, 104), (-135, 0), (135, 0))):
            C.lens(c_, px + dx * s * 1.1, py - 40 * s - dy * s, 40 * s, T, open_=0.6, ring=C.GOLD, coat=(150, 30, 40), hot=0.7)
    Hl.scales(c, 540, 1160, 0.42, T, tilt=tilt, left=you, right=eyes_heap, eye=1.0)
    c.restore()
    return st.arr


def s_d_procession(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0, t1 = cut("d_procession"), end("d_procession")
    u = T - t0
    cam = Pr.Cam((0.0, 3.4, -3.0), pitch=-12, f=900)
    Hl.gallery(c, cam, T, length=60, width=7, height=7, wall=CRIMSON_WALL, lights=[Pr.Light((0, 6.5, z), (255, 210, 160), 1.0, 3.0) for z in (4, 10, 16, 22, 28)],
               fog=(6, 0, 2), fog_d=0.05)
    # at the far end, a covered case, glowing
    end_q = cam.proj((0.0, 0.0, 30.0))
    if end_q:
        sc = cam.scale_at((0.0, 0.0, 30.0))
        G.pool(c, end_q[0], end_q[1] - sc * 1.0, sc * 2.0, (255, 200, 140), 0.5)
        c.drawPath(K.smooth([(end_q[0] - sc * 0.6, end_q[1]), (end_q[0] - sc * 0.55, end_q[1] - sc * 1.9), (end_q[0], end_q[1] - sc * 2.3),
                             (end_q[0] + sc * 0.55, end_q[1] - sc * 1.9), (end_q[0] + sc * 0.6, end_q[1])]), paint(C.BLOOD))
        c.drawPath(K.smooth([(end_q[0] - sc * 0.6, end_q[1]), (end_q[0] - sc * 0.55, end_q[1] - sc * 1.9), (end_q[0], end_q[1] - sc * 2.3),
                             (end_q[0] + sc * 0.55, end_q[1] - sc * 1.9), (end_q[0] + sc * 0.6, end_q[1])]), paint(C.GOLD, stroke=3))
    zc = 4.2 + 0.9 * u
    C.train_floor(c, cam, T, 0.0, zc, -2.5, w0=1.2, w1=5.5)
    q = cam.proj((0.0, 0.0, zc))
    if q:
        sc = cam.scale_at((0.0, 0.0, zc))
        C.curator_back(c, q[0], q[1], sc / 1500 * 3.6, T, sway=math.sin(T))
    return st.arr

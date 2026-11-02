"""Sets II: the corridor (in true perspective), the spiral stair, Rooms 97, 98 and 99, the hidden door, Room 100, the
hospital at dawn."""
import math

import numpy as np
import skia

import draw as D
import figs as F
import kit as K
from draw import H, W, ease, mix, paint, path, ramp
from sets_a import bright, cached, cam, img

# ------------------------------------------------------------------ the corridor

VPX, VPY, FOC = 540.0, 960.0, 700.0
CW, CH, EYE = 1.25, 3.0, 1.6                    # half-width, height, eye height (metres)


def proj(X, Y, Z):
    return (VPX + FOC * X / Z, VPY - FOC * (Y - EYE) / Z)


def quad_src(c, im, src, dst, a=1.0):
    """Warp the sub-rectangle src (x0, y0, x1, y1) of an image onto a quadrilateral (tl, tr, br, bl)."""
    x0, y0, x1, y1 = src
    m = skia.Matrix()
    m.setPolyToPoly([skia.Point(x0, y0), skia.Point(x1, y0), skia.Point(x1, y1), skia.Point(x0, y1)], [skia.Point(*p) for p in dst])
    c.save()
    c.clipPath(path(dst), doAntiAlias=True)
    c.concat(m)
    p = skia.Paint(AntiAlias=True)
    p.setAlphaf(a)
    c.drawImage(im, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear), p)
    c.restore()


PPM = 120                                       # texture pixels per metre
LEN = 40.0


def _wall_tex(name, ground, line, accent):
    return cached("wall_" + name, lambda: K.tiled(K.diamond_tile(150, 190, ground, line, accent), int(LEN * PPM), int(CH * PPM)))


def _carpet_tex():
    def make():
        def fn(c):
            w, h = int(2 * CW * PPM), int(LEN * PPM)
            c.drawRect(skia.Rect.MakeWH(w, h), paint((40, 4, 10)))
            c.drawRect(skia.Rect.MakeLTRB(w * 0.18, 0, w * 0.82, h), paint((90, 8, 24)))
            for k in range(int(LEN * 2)):
                y = k * PPM / 2
                cx = w / 2
                c.drawPath(path([(cx, y), (cx + 70, y + 30), (cx, y + 60), (cx - 70, y + 30)]), paint((220, 150, 60), 0.8, stroke=4))
                c.drawPath(path([(w * 0.18, y), (w * 0.22, y + 30), (w * 0.18, y + 60)], closed=False), paint((220, 150, 60), 0.5, stroke=3))
                c.drawPath(path([(w * 0.82, y), (w * 0.78, y + 30), (w * 0.82, y + 60)], closed=False), paint((220, 150, 60), 0.5, stroke=3))
        return K.surf(int(2 * CW * PPM), int(LEN * PPM), fn)
    return cached("carpet", make)


def corridor(st, T, zc=0.0, doors=(), light=K.BLUE, wall="blue", far_door=None, bob=1.0, sway=0.0, flashes=(), spill=None, dark_far=True,
             stranger=None):
    """A hotel corridor in one-point perspective, the camera zc metres along it. doors: [(Z, side, number, colour)];
    spill: {number: strength} light under the door."""
    c = st.c
    fl = K.flash_at(T, flashes)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0)))
    c.save()
    c.translate(sway * 30 * math.sin(T * 0.8), bob * 7 * math.sin(T * 5.4))
    c.rotate(bob * 0.6 * math.sin(T * 2.7))
    zn, zf = 0.45, 22.0
    u0, u1 = (zc + zn) * PPM, (zc + zf) * PPM
    pal = {"blue": ((8, 14, 50), (60, 90, 220), (240, 190, 90)), "green": ((4, 40, 22), (40, 200, 110), (240, 200, 90)),
           "magenta": ((50, 6, 44), (230, 60, 190), (255, 200, 120)), "red": ((50, 4, 10), (220, 50, 60), (255, 180, 110))}[wall]
    tex = _wall_tex(wall, *pal)
    # left wall: u along Z, v = height
    for side in (-1, 1):
        X = side * CW
        tl, tr = proj(X, CH, zn), proj(X, CH, zf)
        bl, br = proj(X, 0, zn), proj(X, 0, zf)
        if side < 0:
            quad_src(c, tex, (u0, 0, u1, CH * PPM), [tl, tr, br, bl])
        else:
            quad_src(c, tex, (u0, 0, u1, CH * PPM), [tl, tr, br, bl])
    car = _carpet_tex()
    v0, v1 = (zc + zn) * PPM, (zc + zf) * PPM
    # the carpet: map texture rows (v) to depth
    fl_pts = [proj(-CW, 0, zf), proj(CW, 0, zf), proj(CW, 0, zn), proj(-CW, 0, zn)]
    quad_src(c, car, (0, v1, 2 * CW * PPM, v0), fl_pts)
    ceil = cached("ceil_" + wall, lambda: K.tiled(K.fan_tile(150, 150, mix(pal[0], (0, 0, 0), 0.5), mix(pal[1], (0, 0, 0), 0.45)),
                                                  int(2 * CW * PPM), int(LEN * PPM)))
    quad_src(c, ceil, (0, v0, 2 * CW * PPM, v1), [proj(-CW, CH, zn), proj(CW, CH, zn), proj(CW, CH, zf), proj(-CW, CH, zf)])
    # mouldings: a dado rail and a skirting
    for Y, w_ in ((1.0, 5), (0.12, 7), (2.7, 6)):
        for side in (-1, 1):
            c.drawLine(*proj(side * CW, Y, zn), *proj(side * CW, Y, zf), paint((20, 12, 8), stroke=w_))
    # doors
    for (Zd, side, num, colr) in doors:
        Z = Zd - zc
        if Z < zn + 0.3 or Z > zf:
            continue
        X = side * CW
        z0, z1 = Z - 0.5, Z + 0.5
        q = [proj(X, 2.25, z0), proj(X, 2.25, z1), proj(X, 0, z1), proj(X, 0, z0)]
        fr = [proj(X, 2.4, z0 - 0.12), proj(X, 2.4, z1 + 0.12), proj(X, 0, z1 + 0.12), proj(X, 0, z0 - 0.12)]
        c.drawPath(path(fr), paint((60, 30, 14)))
        c.drawPath(path(q), paint(shader=D.lin(q[0], q[2], [(70, 30, 14), (24, 10, 6)])))
        for (a_, b_) in ((0.2, 1.0), (1.2, 2.05)):                      # panels
            pnl = [proj(X, b_, z0 + 0.15), proj(X, b_, z1 - 0.15), proj(X, a_, z1 - 0.15), proj(X, a_, z0 + 0.15)]
            c.drawPath(path(pnl), paint((14, 6, 4), 0.6, stroke=max(1.0, 8 / Z)))
        px, py = proj(X, 1.75, Z)
        K.door_plate(c, px, py, num, s=min(1.6, 0.9 / Z), tag="door")
        hx, hy = proj(X, 1.0, z1 - 0.15 if side < 0 else z0 + 0.15)
        c.drawCircle(hx, hy, max(2, 18 / Z), paint(K.BRASS))
        s = (spill or {}).get(num, 0.0)
        if s > 0:                                                       # light under the door and through the keyhole
            sp = [proj(X, 0.0, z0), proj(X, 0.0, z1), proj(X * 0.35, 0, z1 + 0.4), proj(X * 0.35, 0, z0 - 0.4)]
            K.beam(c, sp, colr, 0.8 * s, p0=proj(X, 0, Z), p1=proj(0, 0, Z))
            c.drawLine(*proj(X, 0.02, z0), *proj(X, 0.02, z1), paint(mix(colr, (255, 255, 255), 0.4), s, stroke=max(2, 10 / Z)))
            K.glow(c, hx, hy - 14 / Z, 60 / Z + 20, colr, 0.9 * s)
            K.glow(c, *proj(X * 0.8, 0.3, Z), 420 / Z + 60, colr, 0.5 * s)
    # sconces
    for k in range(10):
        Z = 1.5 + k * 3.0 - zc % 3.0
        if Z < zn + 0.2:
            continue
        for side in (-1, 1):
            x, y = proj(side * (CW - 0.02), 2.0, Z)
            c.drawCircle(x, y, max(2, 30 / Z), paint((255, 220, 160)))
            K.glow(c, x, y, 260 / Z + 30, light, 0.55)
    if far_door is not None:                                            # the corridor's end: a door, or darkness
        Z = 20.0 - zc
        q = [proj(-0.5, 2.25, Z), proj(0.5, 2.25, Z), proj(0.5, 0, Z), proj(-0.5, 0, Z)]
        c.drawPath(path(q), paint((30, 10, 6)))
        K.glow(c, *proj(0, 1.0, Z), 300, far_door, 0.6)
    if dark_far:
        K.glow(c, VPX, VPY, 180, (0, 0, 0), 0.0)
        c.drawCircle(VPX, VPY, 260, paint(shader=D.rad((VPX, VPY), 260, [(0, 0, 0, 1.0), (0, 0, 0, 0.0)])))
    if stranger is not None:                                             # someone at the far end, lit from behind, watching
        Z = stranger - zc
        if Z > 1.0:
            fx, fy = proj(0.15, 0, Z)
            hgt = FOC * 1.72 / Z
            K.glow(c, fx, fy - hgt * 0.5, hgt * 1.2, mix(light, (255, 255, 255), 0.3), 0.9)
            F.figure(c, F.man_profile_path(T, 0.0, coat=True), fx, fy, hgt / 1000, rim=mix(light, (255, 255, 255), 0.3), side=1,
                     rim2=light, rim_w=3, halo=0.3, flip=True)
    K.glow(c, VPX, VPY + 300, 900, light, 0.25 + 0.6 * fl)
    c.restore()
    K.dark(c, 540, 1000, 500, 1300, 0.45)
    return fl


# ------------------------------------------------------------------ the spiral stair, from above

def spiral(st, T, rot=0.0, nora_k=0.5, cols=(K.BLUE, K.MAGENTA, K.GREEN, K.RED)):
    """The spiral staircase from the landing, looking down the well at an angle: treads and their risers winding down
    into the dark, balusters and a brass rail on the inner edge, Nora on the stairs going down. True perspective."""
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0)))
    Cm = np.array([0.0, 1.5, -2.1])
    tgt = np.array([0.0, -2.8, 0.3])
    fwd = (tgt - Cm) / np.linalg.norm(tgt - Cm)
    rgt = np.cross(fwd, [0.0, 1.0, 0.0])
    rgt /= np.linalg.norm(rgt)
    upv = np.cross(rgt, fwd)
    F = 760.0

    def P(r, a, yy):
        d = np.array([r * math.cos(a), yy, r * math.sin(a)]) - Cm
        zc = float(d @ fwd)
        return (540 + F * float(d @ rgt) / zc, 960 - F * float(d @ upv) / zc, zc)

    step = 2 * math.pi / 24
    rise = 0.17
    items = []
    for k in range(0, 96):
        a0, a1 = rot + k * step, rot + (k + 1) * step * 1.0 + 0.01
        y = -k * rise
        turn = k // 24
        colr = cols[turn % len(cols)]
        q = [P(0.45, a0, y), P(1.35, a0, y), P(1.35, a1, y), P(0.45, a1, y)]
        if min(p[2] for p in q) < 0.3:
            continue
        zc = sum(p[2] for p in q) / 4
        lum = max(0.0, 1.0 - zc / 9.0) ** 1.1
        rz = [P(0.45, a0, y), P(1.35, a0, y), P(1.35, a0, y + rise), P(0.45, a0, y + rise)]
        items.append((zc + 0.01, "riser", rz, colr, lum))
        items.append((zc, "tread", q, colr, lum))
        b0, b1 = P(0.47, a0 + step / 2, y), P(0.47, a0 + step / 2, y + 0.9)
        r0, r1 = P(0.47, a0 + step / 2, y + 0.9), P(0.47, a0 + step * 1.5, y - rise + 0.9)
        items.append((zc - 0.01, "rail", (b0, b1, r0, r1), colr, lum))
        if k == int(4 + 8 * nora_k):                                    # Nora, going down
            ft = P(0.95, a0 + step / 2, y)
            items.append((ft[2] - 0.02, "nora", ft, colr, lum))
    items.sort(key=lambda it: -it[0])
    for zc, kind, g, colr, lum in items:
        if kind == "tread":
            c.drawPath(path([(p[0], p[1]) for p in g]), paint(mix(colr, (0, 0, 0), 1 - 0.8 * lum)))
            c.drawLine(g[0][0], g[0][1], g[1][0], g[1][1], paint(mix(colr, (255, 255, 255), 0.5), 0.9 * lum, stroke=3))   # the nosing
        elif kind == "riser":
            c.drawPath(path([(p[0], p[1]) for p in g]), paint(mix(colr, (0, 0, 0), 1 - 0.35 * lum)))
        elif kind == "rail":
            b0, b1, r0, r1 = g
            c.drawLine(b0[0], b0[1], b1[0], b1[1], paint(mix(K.BRASS, (0, 0, 0), 1 - lum), stroke=max(1.0, 60 / b0[2])))
            c.drawLine(r0[0], r0[1], r1[0], r1[1], paint(mix(K.BRASS_L, (0, 0, 0), 1 - lum), stroke=max(1.5, 110 / r0[2])))
        else:
            hgt = F * 1.65 / g[2]
            K.glow(c, g[0], g[1] - hgt * 0.5, hgt, (255, 255, 255), 0.25)
            F_.woman_p(c, g[0], g[1], hgt / 1000, rim=(255, 200, 230), side=1, T=T, stride=0.6 * math.sin(T * 4), rim_w=4, halo=0.2,
                       flip=True)
    K.glow(c, 540, 1300, 1100, (255, 255, 255), 0.04)


F_ = F


# ------------------------------------------------------------------ ROOM 97 (blue): the contract

def _blue_room():
    def fn(c):
        wall = K.tiled(K.fan_tile(200, 200, (6, 12, 50), (60, 100, 255)), W, H)
        c.drawImage(wall, 0, 0)
        c.drawRect(skia.Rect.MakeLTRB(0, 1420, W, H), paint((4, 6, 20)))
        K.draw_quad(c, K.checker(800, 800, (30, 50, 140), (4, 6, 20), n=8), [(0, 1420), (1080, 1420), (1500, 1920), (-420, 1920)])
    return K.surf(W, H, fn)


def blue_room(st, T, z=1.0, cx=540, cy=960, turn=0.0, flashes=(), phone_lit=1.0, write=0.0, nora_door=1.0):
    c = st.c
    fl = K.flash_at(T, flashes)
    c.save()
    cam(c, z, cx, cy)
    img(c, cached("blueroom", _blue_room))
    K.stained_glass(c, 290, 150, 790, 1000, [(40, 80, 255), (20, 40, 160), (120, 160, 255), (255, 40, 60), (40, 200, 255)], seed=11,
                    lit=0.5 + 0.5 * fl)
    K.glow(c, 540, 600, 900, K.BLUE, 0.4 + 0.8 * fl)
    K.beam(c, [(290, 400), (790, 400), (1100, 1920), (-20, 1920)], (80, 120, 255), 0.12 + 0.4 * fl, p0=(540, 500), p1=(540, 1900))
    # the desk
    c.drawRect(skia.Rect.MakeLTRB(150, 1180, 1000, 1210), paint((30, 40, 80)))
    c.drawRect(skia.Rect.MakeLTRB(170, 1210, 980, 1440), paint((6, 8, 20)))
    for k in range(3):
        c.drawRect(skia.Rect.MakeLTRB(170, 1250 + k * 60, 980, 1256 + k * 60), paint((120, 150, 255), 0.35))
    # the contract and the phone on it
    c.drawPath(path([(540, 1176), (760, 1176), (790, 1196), (520, 1196)]), paint((200, 210, 255)))
    K.phone(c, 880, 1186, 0.09, -84, None, glow_col=(150, 200, 255), lit=phone_lit)
    K.glow(c, 880, 1170, 200, (150, 200, 255), 0.6 * phone_lit)
    K.key(c, 700, 1166, 0.32, ang=6, glint=0.9, T=T)
    if nora_door > 0:                                                   # Nora in the doorway, the corridor's light behind her
        c.drawRect(skia.Rect.MakeLTRB(0, 560, 170, 1430), paint((90, 120, 220), nora_door))
        K.glow(c, 85, 1000, 300, (120, 150, 255), 0.5 * nora_door)
        c.drawRect(skia.Rect.MakeLTRB(-10, 540, 186, 1440), paint((30, 14, 8), nora_door, stroke=26))
        F.woman_p(c, 80, 1430, 0.78, rim=(160, 190, 255), side=1, T=T, hand="chest", head=6, rim_w=6, halo=0.0)
    # him, at the desk, in profile
    F.figure(c, F.seated_man_path(turn), 330, 1200, 0.95, rim=(120, 170, 255), side=1, rim2=K.RED, rim_w=9, halo=0.3)
    if turn > 0:
        F.man_face(c, 340, 1200 - 580 * 0.95, 0.95 * 1.05, a=ease(turn))
    c.restore()
    K.dark(c, 540, 900, 450, 1250, 0.4)
    return fl


def pen(st, T, k=0.0, gel=K.BLUE):
    """A fountain pen's nib signing the contract: the ink is red."""
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((2, 4, 14)))
    c.save()
    c.translate(540, 1000)
    c.rotate(-8)
    c.drawRect(skia.Rect.MakeLTRB(-700, -600, 700, 900), paint(shader=D.rad((-100, -200), 1200, [(200, 210, 255), (90, 110, 200), (10, 14, 40)])))
    f = D.font("cormorant-600", 40)
    for i in range(9):
        y = -420 + i * 64
        c.drawRect(skia.Rect.MakeLTRB(-520, y, -520 + 900 - (i % 3) * 140, y + 10), paint((40, 50, 100), 0.5))
    c.drawString("AGREEMENT", -520, -480, D.font("cormorant-700", 70), paint((30, 36, 80)))
    c.drawLine(-200, 300, 450, 300, paint((30, 36, 80), stroke=3))
    # the signature, written out to k
    n = 80
    pts = [(-180 + 600 * i / n, 270 - 50 * math.sin(i * 0.5) * math.exp(-i / 60) - 20 * math.sin(i * 0.23)) for i in range(n)]
    m = max(2, int(n * k))
    c.drawPath(path(pts[:m], closed=False), paint((200, 10, 30), stroke=9))
    nx, ny = pts[m - 1]
    c.save()
    c.translate(nx, ny)
    c.rotate(-35)
    c.drawPath(path([(0, 0), (40, -110), (0, -150), (-40, -110)]), paint(shader=D.lin((-40, -150), (40, 0), [K.BRASS_L, K.BRASS_D])))
    c.drawLine(0, -10, 0, -120, paint((40, 20, 8), stroke=3))
    c.drawPath(D.rrect(-46, -700, 46, -140, 30), paint(shader=D.lin((-46, 0), (46, 0), [(10, 10, 20), (60, 60, 90), (8, 8, 16)])))
    c.restore()
    c.restore()
    K.wash(c, gel, 0.35, skia.BlendMode.kMultiply)
    K.dark(c, 540, 1100, 350, 1100, 0.6)


CASES = ["Varghese v. China Southern Airlines", "Shaboon v. Egyptair", "Petersen v. Iran Air", "Martinez v. Delta Air Lines",
         "Estate of Durden v. KLM", "Miller v. United Airlines"]


def papers(st, T, k=1.0, stamp=1.0):
    """The six invented cases, whirling in blue light, each stamped in red."""
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((2, 4, 16)))
    K.glow(c, 540, 700, 1000, K.BLUE, 0.55)
    for i, name in enumerate(CASES):
        a = T * 0.5 + i * 1.05
        x = 540 + 50 * math.cos(a)
        y = 610 + i * 126 + 10 * math.sin(a * 1.3)
        c.save()
        c.translate(x, y)
        c.rotate(4 * math.sin(a))
        c.drawRect(skia.Rect.MakeLTRB(-400, -62, 400, 62), paint((214, 222, 255)))
        D.text(c, name, -370, -8, 34, "cormorant-700", (8, 10, 40), align="left", tag="case%d" % i)
        for j in range(2):
            c.drawRect(skia.Rect.MakeLTRB(-370, 14 + j * 20, 60 - j * 90, 21 + j * 20), paint((60, 70, 120), 0.5))
        if stamp > 0 and ramp(T, 0, 1) >= 0:
            sa = min(1.0, stamp * 6 - i)
            if sa > 0:
                c.save()
                c.translate(245, 30)
                c.rotate(-8)
                c.drawPath(D.rrect(-108, -34, 108, 34, 8), paint((220, 20, 40), sa, stroke=6))
                D.text(c, "INVENTED", 0, 14, 38, "limelight-400", (220, 20, 40), tag="stamp%d" % i, a=sa)
                c.restore()
        c.restore()
    K.dark(c, 540, 800, 500, 1300, 0.4)


def books(st, T, red_k=1.0):
    """Six bound law reports on a shelf in blue light; one of them burns red."""
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((2, 4, 16)))
    K.glow(c, 540, 900, 900, K.BLUE, 0.5)
    c.drawRect(skia.Rect.MakeLTRB(60, 1180, 1020, 1220), paint((40, 24, 14)))
    for i in range(6):
        x0 = 120 + i * 140
        colr = (30, 50, 140) if i != 4 else mix((30, 50, 140), (230, 20, 40), red_k)
        c.drawRect(skia.Rect.MakeLTRB(x0, 700, x0 + 120, 1180), paint(shader=D.lin((x0, 0), (x0 + 120, 0), [mix(colr, (0, 0, 0), 0.5), colr, mix(colr, (0, 0, 0), 0.6)])))
        for y in (760, 1110):
            c.drawRect(skia.Rect.MakeLTRB(x0, y, x0 + 120, y + 10), paint(K.GOLD, 0.8))
        c.drawRect(skia.Rect.MakeLTRB(x0 + 30, 840, x0 + 90, 900), paint(K.GOLD, 0.6, stroke=3))
        if i == 4 and red_k > 0:
            K.glow(c, x0 + 60, 940, 300, K.RED, 0.8 * red_k, core=0.4)
    K.dark(c, 540, 950, 400, 1100, 0.5)


# ------------------------------------------------------------------ ROOM 98 (green): the savings

def _green_room():
    def fn(c):
        wall = K.tiled(K.fan_tile(220, 220, (2, 40, 22), (60, 230, 130)), W, H)
        c.drawImage(wall, 0, 0)
        c.drawRect(skia.Rect.MakeLTRB(0, 1440, W, H), paint((2, 16, 8)))
        K.draw_quad(c, K.checker(800, 800, (20, 90, 50), (2, 14, 8), n=8), [(0, 1440), (1080, 1440), (1500, 1920), (-420, 1920)])
        # the machine: a deco vault with a coin slot and a dial
        c.drawPath(D.rrect(600, 420, 1010, 1450, 30), paint(shader=D.lin((600, 0), (1010, 0), [K.BRASS_D, K.BRASS, K.BRASS_L, K.BRASS_D])))
        for k in range(5):
            c.drawRect(skia.Rect.MakeLTRB(620, 470 + k * 26, 990, 480 + k * 26), paint((60, 40, 10), 0.6))
        c.drawCircle(805, 900, 150, paint((40, 26, 8)))
        c.drawCircle(805, 900, 120, paint(shader=D.rad((770, 860), 160, [K.BRASS_L, K.BRASS_D])))
        for k in range(24):
            a = k * math.pi / 12
            c.drawLine(805 + 100 * math.cos(a), 900 + 100 * math.sin(a), 805 + 118 * math.cos(a), 900 + 118 * math.sin(a), paint((50, 30, 8), stroke=4))
        c.drawRect(skia.Rect.MakeLTRB(700, 1140, 910, 1170), paint((0, 0, 0)))              # the slot
        c.drawRect(skia.Rect.MakeLTRB(680, 600, 930, 720), paint((2, 20, 10)))               # a little screen
    return K.surf(W, H, fn)


def green_room(st, T, z=1.0, cx=540, cy=960, pour=0.0, safe=1.0, key_a=1.0, nora_door=1.0):
    c = st.c
    c.save()
    cam(c, z, cx, cy)
    img(c, cached("greenroom", _green_room))
    K.glow(c, 540, 300, 1000, K.GREEN, 0.45)
    D.text(c, "SAFE", 805, 690, 84, "limelight-400", (120, 255, 170), tag="safe", a=safe)
    K.glow(c, 805, 660, 220, K.GREEN, 0.6 * safe)
    K.glow(c, 805, 1155, 160, K.GOLD, 0.5)
    # the coin pile on the floor, the key in it
    for k in range(60):
        rng = np.random.default_rng(k)
        x, y = 260 + rng.normal(0, 120), 1520 + abs(rng.normal(0, 30))
        c.drawPath(D.oval(x - 26, y - 9, x + 26, y + 9), paint(mix(K.GOLD, K.BRASS_D, rng.random() * 0.6)))
    if key_a > 0:
        K.key(c, 700, 1070, 0.5, ang=-10, glint=key_a, T=T)
    if nora_door > 0:
        c.drawRect(skia.Rect.MakeLTRB(0, 600, 150, 1450), paint((80, 200, 140), nora_door))
        K.glow(c, 75, 1020, 280, K.GREEN, 0.5 * nora_door)
        c.drawRect(skia.Rect.MakeLTRB(-10, 580, 166, 1460), paint((30, 14, 8), nora_door, stroke=24))
        F.woman_p(c, 70, 1450, 0.74, rim=(150, 255, 190), side=1, T=T, hand="chest", head=10, rim_w=6, halo=0.0)
    # her, pouring her savings in
    F.figure(c, F.lady_path(pour), 400, 1450, 0.9, rim=(80, 255, 160), side=1, rim2=K.GOLD, rim_w=9, halo=0.3)
    bx, by = 400 + 250 * 0.9, 1450 - (680 - 40 * pour) * 0.9
    for k in range(14):                                                 # the coins arcing into the slot
        u = ((T * 0.9 + k / 14) % 1.0)
        x = bx + (805 - bx) * u
        y = by + (1150 - by) * u - 160 * math.sin(math.pi * u)
        c.drawPath(D.oval(x - 16, y - 6 - 8 * abs(math.sin(T * 9 + k)), x + 16, y + 6 + 8 * abs(math.sin(T * 9 + k))), paint(K.GOLD, 0.95 * min(1, pour * 3)))
    c.restore()
    K.dark(c, 560, 1000, 420, 1250, 0.45)


def safe_sign(st, T, crack=0.0):
    """A neon SAFE in a brass deco frame: it cracks, and flickers out."""
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 10, 4)))
    K.deco_frame(c, 140, 640, 940, 1140, K.BRASS, 1.0, 8)
    on = 1.0 if crack < 0.3 else (1.0 if (int(T * 17) % 3) else 0.15) * (1 - ramp(crack, 0.6, 1.0))
    K.glow(c, 540, 900, 600, K.GREEN, 0.6 * on)
    D.text(c, "SAFE", 540, 960, 220, "limelight-400", mix((10, 40, 20), (160, 255, 200), on), tag="safe", outline=(0, 0, 0), ow=4)
    if crack > 0:
        rng = np.random.default_rng(3)
        pts, x, y = [(560, 640)], 560.0, 640.0
        while y < 1140 * min(1, crack * 1.6) + 640 * (1 - min(1, crack * 1.6)):
            y += rng.uniform(30, 70)
            x += rng.uniform(-50, 50)
            pts.append((x, y))
        c.drawPath(path(pts, closed=False), paint((0, 0, 0), stroke=10))
        c.drawPath(path(pts, closed=False), paint((200, 255, 220), 0.6 * on, stroke=2))
    K.dark(c, 540, 900, 400, 1100, 0.5)


def drain(st, T, k=1.0):
    """Banknotes and coins spiralling down into the dark."""
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 8, 4)))
    cx, cy = 540, 1050
    for j in range(8):
        r = 1100 * 0.72 ** j
        c.drawCircle(cx, cy, r, paint(mix(K.GREEN, (0, 0, 0), 0.6 + 0.05 * j), stroke=60 * 0.72 ** j))
    rng = np.random.default_rng(2)
    for i in range(70):
        ph = rng.random()
        u = (ph + T * 0.18) % 1.0
        a = rng.random() * 6.28 + u * 9
        r = 900 * (1 - u) ** 1.3
        x, y = cx + r * math.cos(a), cy + r * math.sin(a) * 0.8
        s = 0.25 + 0.75 * (1 - u)
        c.save()
        c.translate(x, y)
        c.rotate(math.degrees(a) + 90)
        if i % 3:
            c.drawRect(skia.Rect.MakeLTRB(-80 * s, -36 * s, 80 * s, 36 * s), paint(mix((150, 220, 160), (0, 0, 0), u * 0.7)))
            c.drawRect(skia.Rect.MakeLTRB(-60 * s, -22 * s, 60 * s, 22 * s), paint((30, 90, 50), 0.7 * (1 - u), stroke=3))
        else:
            c.drawPath(D.oval(-30 * s, -30 * s, 30 * s, 30 * s), paint(mix(K.GOLD, (0, 0, 0), u * 0.7)))
        c.restore()
    c.drawCircle(cx, cy, 140, paint(shader=D.rad((cx, cy), 160, [(0, 0, 0, 1.0), (0, 0, 0, 0.0)])))
    K.glow(c, 540, 400, 800, K.GREEN, 0.3)


# ------------------------------------------------------------------ ROOM 99 (magenta): the mirrors

def mirrors(st, T, nod=1.0, stop=-1, stop_k=0.0, frames=6, chart=None):
    """Frames within frames, receding: in each, Nora with her glowing phone, nodding in time. stop: the index of the
    reflection that stops nodding and looks at us."""
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((14, 0, 12)))
    K.glow(c, 540, 900, 1100, K.MAGENTA, 0.5)
    cx, cy = 540, 980
    for j in range(frames - 1, -1, -1):
        s = 0.8 ** j
        w, h = 900 * s, 1500 * s
        x0, y0 = cx - w / 2, cy - h / 2
        colr = [K.MAGENTA, K.VIOLET, (255, 60, 120), K.BLUE][j % 4]
        arch = skia.Path()
        arch.moveTo(x0, y0 + h)
        arch.lineTo(x0, y0 + w / 2)
        arch.arcTo(skia.Rect.MakeLTRB(x0, y0, x0 + w, y0 + w), 180, 180, False)
        arch.lineTo(x0 + w, y0 + h)
        arch.close()
        if j == frames - 1:
            c.drawPath(arch, paint(mix(colr, (0, 0, 0), 0.9)))
        else:
            c.drawPath(arch, paint(mix(colr, (0, 0, 0), 0.6), 0.25))
        c.drawPath(arch, paint(K.GOLD, 0.9, stroke=26 * s))
        c.drawPath(arch, paint(K.BRASS_D, 0.9, stroke=8 * s))
        K.eglow(c, cx, cy, w * 0.45, h * 0.4, colr, 0.25)
        if chart is not None:
            continue
        if j == 0:
            continue
        nx = [0, 330, 760, 420, 650, 510, 540][j]
        hd = 10 * math.sin(T * 2 * math.pi * 0.9) * nod
        looking = (j == stop and stop_k > 0)
        F.woman_p(c, nx, y0 + h - 30 * s, 0.85 * s, rim=colr, side=1 if j % 2 == 0 else -1, T=T, hand="phone", head=0 if looking else 8 + hd,
                  flip=bool(j % 2), rim_w=8 * s + 1, halo=0.25)
        px, py = nx + (1 if j % 2 == 0 else -1) * 120 * 0.85 * s, y0 + h - 30 * s - 600 * 0.85 * s
        K.glow(c, px, py, 120 * s + 20, (160, 210, 255), 0.6)
        if looking:                                                     # her face comes round to us, lit from below
            hx, hy = nx, y0 + h - 30 * s - 915 * 0.85 * s
            F.man_face(c, hx, hy, 0.85 * s * 0.95, a=ease(stop_k), glow_col=(255, 160, 230))
    if chart is not None:
        c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0), 0.55))
        chart(c)
    K.dark(c, 540, 980, 520, 1250, 0.35)


def bars(c, T, t0, y=330, t1=None, focus=None):
    """The radiologists: % of mammograms rated correctly with a correct AI hint, and with a wrong one."""
    c.drawRect(skia.Rect.MakeLTRB(70, y - 70, 1010, y + 900), paint((8, 2, 10), 0.85))
    K.deco_frame(c, 70, y - 70, 1010, y + 900, K.GOLD, 0.9, 4)
    D.text(c, "RADIOLOGISTS READING MAMMOGRAMS", 540, y, 40, "jost-600", (255, 225, 245), tag="chart")
    D.text(c, "% rated correctly", 540, y + 52, 34, "jost-500", (240, 200, 230), tag="chart")
    groups = [("LEAST EXPERIENCED", 79.7, 19.8), ("MOST EXPERIENCED", 82.3, 45.5)]
    base = y + 650
    for g, (name, a_, b_) in enumerate(groups):
        gx = 320 + g * 440
        tg = t0 if g == 0 else (t1 if t1 is not None else t0 + 1.4)
        k = ease(ramp(T, tg + 0.2, tg + 1.0))
        for i, (v, colr, lab) in enumerate(((a_, K.GOLD, "correct hint"), (b_, K.MAGENTA, "wrong hint"))):
            x = gx - 95 + i * 190
            hgt = 5.2 * v * (k if i == 1 else 1.0)
            c.drawRect(skia.Rect.MakeLTRB(x - 62, base - hgt, x + 62, base), paint(colr, 0.95))
            c.drawRect(skia.Rect.MakeLTRB(x - 62, base - hgt, x + 62, base), paint((0, 0, 0), 0.6, stroke=4))
            if i == 0 or k > 0.6:
                D.text(c, f"{round(v)}%", x, base - hgt - 22, 54, "limelight-400", (255, 255, 255), tag="chartv%d%d" % (g, i), shadow=(0, 0, 0))
            D.text(c, lab, x, base + 46, 30, "jost-500", (240, 220, 240), tag="chartl%d%d" % (g, i))
        D.text(c, name, gx, base + 98, 32, "jost-600", (255, 200, 240), tag="chartg%d" % g)
        if focus is not None:
            if g == focus:
                c.drawRect(skia.Rect.MakeLTRB(gx - 200, y + 120, gx + 200, base + 125), paint(K.MAGENTA, 0.9, stroke=6))
                K.eglow(c, gx, base - 200, 260, 380, K.MAGENTA, 0.25)
            else:
                c.drawRect(skia.Rect.MakeLTRB(gx - 210, y + 100, gx + 210, base + 130), paint((8, 2, 10), 0.72))
    D.text(c, "Dratsch et al., Radiology, 2023", 540, base + 160, 32, "cormorant-500i", (255, 200, 240), tag="chart")


# ------------------------------------------------------------------ the hidden door

def _door_wall():
    def fn(c):
        wall = K.tiled(K.fan_tile(180, 180, (30, 4, 40), (190, 70, 230)), W, H)
        c.drawImage(wall, 0, 0)
    return K.surf(W, H, fn)


DOOR = (290, 300, 790, 1500)


def grid(c, x0, y0, size, mode, T, k=1.0):
    """100 panes of stained glass: mode 'half' (50 wrong, at random), 'one' (one wrong in 100)."""
    n = 10
    s = size / n
    rng = np.random.default_rng(7)
    bad = set(rng.choice(100, 50, replace=False)) if mode == "half" else {67}
    for i in range(100):
        r, q = divmod(i, n)
        x, y = x0 + q * s, y0 + r * s
        wrong = i in bad
        pulse = 0.6 + 0.4 * math.sin(T * 6) if (wrong and mode == "one") else 1.0
        colr = (255, 30, 40) if wrong else (255, 200, 80)
        c.drawRect(skia.Rect.MakeLTRB(x + 3, y + 3, x + s - 3, y + s - 3), paint(mix(colr, (0, 0, 0), 0.25 if not wrong else 0.0), k * pulse))
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x0 + size, y0 + size), paint((10, 4, 10), k, stroke=8))
    for i in range(1, n):
        c.drawLine(x0 + i * s, y0, x0 + i * s, y0 + size, paint((10, 4, 10), k, stroke=6))
        c.drawLine(x0, y0 + i * s, x0 + size, y0 + i * s, paint((10, 4, 10), k, stroke=6))
    if mode == "one":
        q, r = 67 % n, 67 // n
        K.glow(c, x0 + (q + 0.5) * s, y0 + (r + 0.5) * s, s * 2.2, K.RED, 0.8 * k)


def hidden_door(st, T, seam=0.0, key_in=1.0, turn=0.0, open_k=0.0, grid_mode=None, grid_k=0.0, z=1.0, cx=540, cy=960):
    c = st.c
    c.save()
    cam(c, z, cx, cy)
    img(c, cached("doorwall", _door_wall))
    K.glow(c, 540, 900, 900, K.VIOLET, 0.35)
    x0, y0, x1, y1 = DOOR
    if open_k > 0:                                                      # the door swings in: blazing light behind it
        _blaze_core(c, T, (x0 + x1) / 2, (y0 + y1) / 2, 0.6 + 0.4 * open_k, clip=skia.Rect.MakeLTRB(x0, y0, x1, y1))
        w = (x1 - x0) * (1 - 0.85 * ease(open_k))
        door = path([(x0, y0), (x0 + w, y0 + 60 * open_k), (x0 + w, y1 - 60 * open_k), (x0, y1)])
        c.save()
        c.clipPath(door, doAntiAlias=True)
        c.drawImage(cached("doorwall", _door_wall), 0, 0)
        c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0), 0.5 * open_k))
        c.restore()
    if seam > 0:                                                        # the seam in the paper, light leaking
        for colr, off in ((K.RED, 0), (K.GOLD, 3), (K.CYAN, 6)):
            c.drawRect(skia.Rect.MakeLTRB(x0 - off, y0 - off, x1 + off, y1 + off), paint(colr, 0.5 * seam, stroke=3, blur=6))
        c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint((255, 240, 220), 0.8 * seam, stroke=2))
    if grid_mode is not None and grid_k > 0 and open_k == 0:
        K.glow(c, 540, 690, 520, K.GOLD, 0.3 * grid_k)
        grid(c, 340, 440, 400, grid_mode, T, grid_k)
    if open_k == 0:
        # the escutcheon, the keyhole, the key
        ex, ey = 540, 1060
        c.drawPath(D.smooth([(ex, ey - 120), (ex + 50, ey - 60), (ex + 40, ey + 80), (ex, ey + 130), (ex - 40, ey + 80), (ex - 50, ey - 60)]),
                   paint(shader=D.lin((ex - 50, ey - 120), (ex + 50, ey + 130), [K.BRASS_L, K.BRASS, K.BRASS_D])))
        c.drawCircle(ex, ey - 10, 14, paint((0, 0, 0)))
        c.drawPath(path([(ex - 8, ey - 4), (ex + 8, ey - 4), (ex + 12, ey + 40), (ex - 12, ey + 40)]), paint((0, 0, 0)))
        if seam > 0:
            K.glow(c, ex, ey + 10, 60, (255, 240, 200), 0.8 * seam)
        if key_in > 0:
            c.save()
            c.translate(ex, ey + 10)
            c.scale(math.cos(turn * math.pi / 2) * 0.8 + 0.2, 1)
            K.key(c, -94 - 200 * (1 - key_in), -14, 0.55, ang=0, glint=0.5, tag=True, T=T)
            c.restore()
    c.restore()
    K.dark(c, 540, 960, 520, 1250, 0.35)


def keyhole(st, T, light=1.0, turn=0.0, eye_k=0.0):
    """An extreme close-up of the keyhole: blazing colour leaking through it."""
    c = st.c
    c.drawRect(skia.Rect.MakeWH(W, H), paint((20, 4, 26)))
    c.drawPath(D.smooth([(540, 260), (820, 600), (760, 1300), (540, 1620), (320, 1300), (260, 600)]),
               paint(shader=D.lin((260, 260), (820, 1620), [K.BRASS_L, K.BRASS, K.BRASS_D])))
    for k in range(12):
        a = k * math.pi / 6
        c.drawCircle(540 + 200 * math.cos(a), 900 + 260 * math.sin(a), 16, paint(K.BRASS_D))
    hole = skia.Path()
    hole.addCircle(540, 800, 110)
    hole.addPath(path([(470, 840), (610, 840), (650, 1240), (430, 1240)]))
    c.save()
    c.clipPath(hole, doAntiAlias=True)
    _blaze_core(c, T, 540, 950, light)
    if eye_k > 0:
        F.eye(c, 540, 900, 0.32, T, open_k=1.0, gel=K.GOLD, refl=False)
    c.restore()
    for k, colr in enumerate((K.RED, K.GOLD, K.CYAN, K.MAGENTA)):     # beams out of the keyhole
        a = math.radians(70 + k * 15 + 5 * math.sin(T * 2 + k))
        K.beam(c, [(540, 900), (540 + 1600 * math.cos(a - 0.05), 900 + 1600 * math.sin(a - 0.05)),
                   (540 + 1600 * math.cos(a + 0.05), 900 + 1600 * math.sin(a + 0.05))], colr, 0.25 * light, p0=(540, 900), p1=(540, 1900))
    if turn > 0:
        c.save()
        c.translate(540, 900)
        c.rotate(-90 * turn)
        c.drawPath(D.rrect(-30, -260, 30, 120, 10), paint(shader=D.lin((-30, 0), (30, 0), [K.BRASS_L, K.BRASS_D])))
        c.restore()


# ------------------------------------------------------------------ ROOM 100: blazing colour

def _blaze_core(c, T, cx, cy, k=1.0, clip=None, drain=0.0):
    if clip is not None:
        c.save()
        c.clipRect(clip)
    cols = [K.RED, K.GOLD, K.GREEN, K.CYAN, K.BLUE, K.MAGENTA]
    n = 24
    for i in range(n):
        a0 = T * 0.4 + i * 2 * math.pi / n
        a1 = a0 + 2 * math.pi / n
        colr = mix(cols[i % len(cols)], (220, 0, 20) if i % 2 else (90, 0, 10), drain)
        p = path([(cx, cy), (cx + 2400 * math.cos(a0), cy + 2400 * math.sin(a0)), (cx + 2400 * math.cos(a1), cy + 2400 * math.sin(a1))])
        c.drawPath(p, paint(colr, k))
    K.glow(c, cx, cy, 700, mix((255, 255, 255), (255, 60, 60), drain), 0.9 * k * (1 - 0.5 * drain), core=1.0 - 0.6 * drain)
    if clip is not None:
        c.restore()


def blaze(st, T, k=1.0, bed=1.0, phone_text=None):
    """Room 100: her own room, in every colour at once - the bed in the middle, Nora on it, the phone still glowing."""
    c = st.c
    _blaze_core(c, T, 540, 760, k)
    K.stained_glass(c, 290, 120, 790, 760, [K.RED, K.GOLD, K.GREEN, K.CYAN, K.BLUE, K.MAGENTA], seed=21, lit=1.0, pattern="deco")
    if bed > 0:
        c.drawRect(skia.Rect.MakeLTRB(100, 1240, 980, 1330), paint((250, 240, 245), bed))
        c.drawRect(skia.Rect.MakeLTRB(90, 1300, 990, 1500), paint((160, 0, 30), bed))
        c.drawPath(D.smooth([(60, 1330), (60, 960), (130, 900), (200, 960), (210, 1330)]), paint((30, 6, 10), bed))
        c.drawPath(D.oval(150, 1190, 360, 1262), paint((240, 236, 240), bed))                          # the pillow
        F.lying_nora(c, 1100, 1180, 0.82, key=(255, 236, 226), rim=K.GOLD, eye_k=0.0, T=T, pain=0.6, pale=0.3)
        c.drawPath(D.smooth([(480, 1250), (540, 1150), (680, 1098), (990, 1100), (990, 1500), (480, 1500)]), paint((160, 0, 30), bed))
        K.phone(c, 560, 1200, 0.12, -80, None, glow_col=(170, 210, 255), lit=1.0)
        K.glow(c, 560, 1200, 220, (170, 210, 255), 0.8, core=0.6)
    K.wash(c, (255, 255, 255), 0.06)


def heart_line(c, T, t0, y=600, falter=1.0, col=K.RED, a=1.0):
    """A blazing heartbeat trace across the frame, faltering to a flat line."""
    pts = []
    for i in range(240):
        x = i * W / 239
        u = (x / W + (T - t0) * 0.5) % 1.0
        amp = 1.0 - falter * ramp(x / W, 0.35, 0.9)
        v = 0.0
        ph = (x / 180.0 - (T - t0) * 2.2) % 1.0
        if ph < 0.06:
            v = -260 * amp * math.sin(ph / 0.06 * math.pi)
        elif ph < 0.1:
            v = 120 * amp * math.sin((ph - 0.06) / 0.04 * math.pi)
        pts.append((x, y + v))
    p = path(pts, closed=False)
    c.drawPath(p, paint(col, 0.6 * a, stroke=26, blur=16))
    c.drawPath(p, paint(mix(col, (255, 255, 255), 0.5), a, stroke=7))


# ------------------------------------------------------------------ dawn: the hospital

def hospital(st, T, z=1.0, cx=540, cy=960, doc=1.0, beat_bpm=72, dy=0.0):
    c = st.c
    K.vgrad(c, 0, 0, W, H, (70, 60, 70), (30, 24, 30))
    c.save()
    cam(c, z, cx, cy, 0, dy)
    # the window, blinds, dawn behind
    c.drawRect(skia.Rect.MakeLTRB(560, 200, 1040, 1000), paint(shader=D.lin((0, 200), (0, 1000), [(255, 200, 150), (255, 160, 120)])))
    for k in range(18):
        y = 220 + k * 44
        c.drawRect(skia.Rect.MakeLTRB(560, y, 1040, y + 22), paint((150, 110, 90)))
    K.glow(c, 800, 600, 700, (255, 190, 120), 0.6)
    for k in range(9):                                                  # stripes of dawn light across the room
        y = 900 + k * 90
        K.beam(c, [(560, 220 + k * 88), (560, 240 + k * 88), (-200, y + 300), (-200, y + 260)], (255, 190, 130), 0.18, p0=(560, 230 + k * 88), p1=(0, y + 280))
    # the monitor
    c.drawPath(D.rrect(60, 380, 420, 640, 20), paint((20, 22, 24)))
    c.drawRect(skia.Rect.MakeLTRB(80, 400, 400, 620), paint((4, 20, 10)))
    pts = []
    for i in range(160):
        x = 80 + i * 2
        ph = (i / 40.0 - T * beat_bpm / 60) % 1.0
        v = -70 * math.sin(ph / 0.08 * math.pi) if ph < 0.08 else (26 * math.sin((ph - 0.08) / 0.05 * math.pi) if ph < 0.13 else 0)
        pts.append((x, 520 + v))
    c.drawPath(path(pts, closed=False), paint((60, 255, 120), stroke=4))
    K.glow(c, 240, 510, 200, K.GREEN, 0.3)
    # the bed: a raised pillow, Nora sitting up and tucked in, awake
    c.drawPath(D.smooth([(110, 1340), (120, 980), (260, 940), (300, 1340)]), paint((236, 230, 226)))
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(0, 0, W, 1330))
    F.face_profile(c, 300, 1740, 0.8, key=(255, 200, 150), rim=(255, 210, 160), eye_k=1.0, skin_gel=(255, 180, 130), head=-4)
    c.restore()
    c.drawPath(D.smooth([(60, 1330), (300, 1300), (560, 1290), (900, 1300), (900, 1540), (60, 1540)]), paint((170, 178, 196)))
    c.drawRect(skia.Rect.MakeLTRB(60, 1290, 900, 1312), paint((236, 232, 226)))
    if doc > 0:
        F.figure(c, F.man_profile_path(T, 0.0, coat=True, clipboard=True), 860, 1560, 0.98, rim=(255, 210, 160), side=-1, rim_w=9,
                 halo=0.2, fill=(34, 26, 28), flip=True)
    c.restore()
    K.dark(c, 540, 960, 520, 1300, 0.35)

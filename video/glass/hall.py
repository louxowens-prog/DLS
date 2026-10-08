"""The museum inside the machine: an endless gallery of lacquered walls and gilt mouldings over a black-and-white marble
floor; glass vitrines on black plinths, each lit from above, each with an engraved brass label; an enfilade of
doorways, one room inside the next; and the great golden scales.

Built on pers.py: every surface is drawn in true perspective, so the camera can dolly down the gallery."""
import math

import numpy as np
import skia

import couture as C
import gel as G
import kit as K
import pers as Pr
from kit import BLACK, WHITE, mix, paint

GOLD, GOLD_HI, GOLD_LO = C.GOLD, C.GOLD_HI, C.GOLD_LO
LACQUER_RED, EMERALD_WALL, ROYAL_WALL, BLACK_WALL = (120, 6, 18), (6, 74, 54), (16, 30, 110), (14, 12, 16)


def _checker(pc, w, L, tile, a_col, b_col):
    nx, nz = int(math.ceil(w / tile)), int(math.ceil(L / tile))
    pc.drawRect(skia.Rect.MakeLTRB(0, 0, w * Pr.U, L * Pr.U), paint(a_col))
    p = skia.Path()
    for i in range(nx):
        for j in range(nz):
            if (i + j) % 2:
                p.addRect(skia.Rect.MakeXYWH(i * tile * Pr.U, j * tile * Pr.U, tile * Pr.U, tile * Pr.U))
    pc.drawPath(p, paint(b_col))
    # veins in the white marble
    rng = K.rng_at(int(w * 10 + L), 5)
    for k in range(int(nx * nz * 0.35)):
        x0, y0 = rng.uniform(0, w) * Pr.U, rng.uniform(0, L) * Pr.U
        pc.drawPath(K.bez_path([(x0, y0), (x0 + rng.uniform(-40, 40), y0 + rng.uniform(10, 40)), (x0 + rng.uniform(-60, 60), y0 + rng.uniform(30, 80))]),
                    paint(mix(a_col, (120, 110, 120), 0.6), 0.35, stroke=2.0))


def gallery(c, cam, T, length=40.0, width=6.0, height=6.0, z0=-1.0, wall=LACQUER_RED, floor=((226, 222, 214), (16, 14, 16)), tile=1.0,
            lights=(), fog=(4, 2, 4), fog_d=0.075, frames=True, ceiling=(10, 6, 8), lamps=True, end=None, sheen=0.35, panel=3.0):
    """The hall. lights: pers.Light pools on the floor and walls. end(c, cam) paints the far wall (a door, a void)."""
    fl = Pr.floor(-width / 2, width / 2, z0, length)
    with fl.draw(c, cam) as pc:
        if pc is not None:
            _checker(pc, width, length - z0, tile, floor[0], floor[1])
            if lights:
                pc.saveLayer(None, None)
                Pr.light_plane(pc, fl, lights, 1.0, 1.3, 1.0)
                pc.restore()
            Pr.depth_fog(pc, fl, cam, fog, fog_d, 1.0)
    for facing, x in ((1, -width / 2), (-1, width / 2)):
        wl = Pr.wall_x(x, z0, length, 0.0, height, facing)
        with wl.draw(c, cam) as pc:
            if pc is not None:
                L = length - z0
                pc.drawRect(skia.Rect.MakeLTRB(0, 0, L * Pr.U, height * Pr.U), paint(shader=K.lin((0, 0), (0, height * Pr.U), [mix(wall, BLACK, 0.55), wall, mix(wall, BLACK, 0.3)])))
                if frames:
                    k = 0
                    while k * panel < L:
                        a0 = k * panel + 0.35
                        r = skia.Rect.MakeLTRB(a0 * Pr.U, 0.9 * Pr.U, (a0 + panel - 0.7) * Pr.U, (height - 0.7) * Pr.U)
                        pc.drawRect(r, paint(mix(wall, BLACK, 0.25)))
                        pc.drawRect(r, paint(GOLD, 0.9, stroke=9))
                        pc.drawRect(r.makeInset(16, 16), paint(GOLD_LO, 0.8, stroke=3))
                        k += 1
                    pc.drawRect(skia.Rect.MakeLTRB(0, 0.25 * Pr.U, L * Pr.U, 0.45 * Pr.U), paint(GOLD, 0.85))          # the cornice
                    pc.drawRect(skia.Rect.MakeLTRB(0, (height - 0.25) * Pr.U, L * Pr.U, height * Pr.U), paint(mix(GOLD, BLACK, 0.4)))  # skirting
                if lights:
                    pc.saveLayer(None, None)
                    Pr.light_plane(pc, wl, lights, 1.0, 0.8, 1.3)
                    pc.restore()
                Pr.depth_fog(pc, wl, cam, fog, fog_d, 1.0)
    ce = Pr.ceiling(-width / 2, width / 2, z0, length, height)
    with ce.draw(c, cam) as pc:
        if pc is not None:
            pc.drawRect(skia.Rect.MakeLTRB(0, 0, width * Pr.U, (length - z0) * Pr.U), paint(ceiling))
            Pr.depth_fog(pc, ce, cam, fog, fog_d, 1.0)
    if lamps:
        z = 2.0
        while z < length:
            q = cam.proj((0.0, height - 0.05, z))
            if q is not None:
                r = max(1.0, cam.f * 0.12 / q[2])
                fk = 1 - Pr.fog_at(cam, (0, height, z), fog, fog_d)
                c.drawCircle(q[0], q[1], r, G.glow_paint((255, 236, 200), 0.9 * fk))
                G.pool(c, q[0], q[1], r * 6, (255, 220, 170), 0.25 * fk)
            z += panel
    if end is not None:
        end(c, cam)
    if sheen > 0:                                                    # the polished floor's broad reflection of the far light
        q = cam.proj((0.0, 0.0, length * 0.6))
        if q is not None:
            c.drawRect(skia.Rect.MakeLTRB(q[0] - 120, q[1], q[0] + 120, K.H), paint(shader=K.lin((0, q[1]), (0, K.H), [(255, 230, 200, 0.0), (255, 230, 200, 0.12 * sheen), (255, 230, 200, 0.0)])))


def vitrine(c, cam, X, Z, w=1.0, d=1.0, h=1.5, ph=0.95, T=0.0, content=None, label=None, lit=1.0, spot=(255, 238, 206), glass=(210, 232, 255),
            frame=GOLD, plinth=(14, 12, 16), beam=True, label_size=9.0, height=6.0, fog=(4, 2, 4), fog_d=0.075, label_font="cinzel-600",
            open_top=False, shatter=0.0, ref=None):
    """A glass case on a plinth at (X, Z) on the floor. content(c, sx, sy, ppm) paints the exhibit standing at the screen
    point (sx, sy) of the plinth top, ppm screen pixels per metre. label: one or two lines engraved on a brass plate."""
    P = lambda x, y, z: cam.proj((x, y, z))
    x0, x1, z0_, z1 = X - w / 2, X + w / 2, Z - d / 2, Z + d / 2
    y0, y1, y2 = 0.0, ph, ph + h
    V = {}
    for nm, (x, y, z) in dict(p0=(x0, y0, z0_), p1=(x1, y0, z0_), p2=(x1, y0, z1), p3=(x0, y0, z1), q0=(x0, y1, z0_), q1=(x1, y1, z0_),
                              q2=(x1, y1, z1), q3=(x0, y1, z1), g0=(x0, y2, z0_), g1=(x1, y2, z0_), g2=(x1, y2, z1), g3=(x0, y2, z1)).items():
        V[nm] = P(x, y, z)
    if any(v is None for v in V.values()):
        return None
    pt = lambda k: V[k][:2]
    fk = 1 - Pr.fog_at(cam, (X, ph, Z), fog, fog_d)
    lp = paint()
    lp.setAlphaf(max(0.0, min(1.0, fk * 1.15)))
    c.saveLayer(None, lp)
    # the spotlight and its pool
    if beam and lit > 0:
        ap = P(X, height, Z)
        if ap is not None:
            G.beam(c, ap[:2], pt("g0"), pt("g1"), spot, 0.22 * lit, 0.6)
        foot = P(X, 0.0, Z)
        G.pool(c, foot[0], foot[1], abs(pt("p1")[0] - pt("p0")[0]) * 1.3, spot, 0.35 * lit, squash=0.3)
    # plinth: the visible side faces, then the front
    cx = cam.pos[0]
    if cx < x0:
        c.drawPath(K.path([pt("p0"), pt("p3"), pt("q3"), pt("q0")]), paint(mix(plinth, BLACK, 0.3)))
    if cx > x1:
        c.drawPath(K.path([pt("p1"), pt("p2"), pt("q2"), pt("q1")]), paint(mix(plinth, BLACK, 0.3)))
    c.drawPath(K.path([pt("p0"), pt("p1"), pt("q1"), pt("q0")]), paint(shader=K.lin(pt("q0"), pt("p0"), [mix(plinth, (90, 80, 90), 0.35), plinth])))
    if cam.pos[1] > ph:
        c.drawPath(K.path([pt("q0"), pt("q1"), pt("q2"), pt("q3")]), paint(mix(plinth, (60, 50, 60), 0.4)))
    c.drawLine(*pt("q0"), *pt("q1"), paint(frame, 0.9, stroke=max(1.0, cam.scale_at((X, ph, z0_)) * 0.02)))
    # back panes, faint
    if lit > 0:
        G.pool(c, (pt("q0")[0] + pt("q1")[0]) / 2, (pt("g0")[1] + pt("q0")[1]) / 2, abs(pt("q1")[0] - pt("q0")[0]) * 0.8, spot, 0.12 * lit)
    for f in (("q3", "q2", "g2", "g3"), ("q0", "q3", "g3", "g0"), ("q1", "q2", "g2", "g1")):
        c.drawPath(K.path([pt(k) for k in f]), paint(glass, 0.05))
    ppm = cam.scale_at((X, ph, Z))
    sx, sy = P(X, ph, Z)[:2]
    if content is not None:
        content(c, sx, sy, ppm)
    # the front pane: a sheen sliding across it; edges of brass
    if shatter < 0.05:
        c.drawPath(K.path([pt(k) for k in ("q0", "q1", "g1", "g0")]),
                   paint(shader=K.lin(pt("g0"), pt("q1"), [glass + (0.16,), glass + (0.02,), (255, 255, 255, 0.22), glass + (0.03,), glass + (0.1,)], [0.0, 0.3, 0.45, 0.6, 1.0])))
        if ref is not None:                                          # something reflected in the glass
            c.save()
            c.clipPath(K.path([pt(k) for k in ("q0", "q1", "g1", "g0")]), doAntiAlias=True)
            ref(c, (pt("g0")[0] + pt("q1")[0]) / 2, (pt("g0")[1] + pt("q1")[1]) / 2, abs(pt("q1")[0] - pt("q0")[0]))
            c.restore()
    ew = max(1.0, ppm * 0.022)
    edges = [("q0", "g0"), ("q1", "g1"), ("q3", "g3"), ("q2", "g2"), ("g0", "g1"), ("g1", "g2"), ("g2", "g3"), ("g3", "g0")]
    for k0, k1 in edges:
        c.drawLine(*pt(k0), *pt(k1), paint(frame, 0.85 if shatter < 0.5 else 0.5, stroke=ew))
    c.drawLine(*pt("g0"), *pt("g1"), paint(GOLD_HI, 0.6, stroke=ew * 0.5))
    # the label
    if label:
        fr = Pr.Plane((x0, ph, z0_), (1, 0, 0), (0, -1, 0), (0, 0, w, ph))
        with fr.draw(c, cam) as pc:
            if pc is not None:
                lines = label if isinstance(label, (list, tuple)) else [label]
                sizes = [label_size if i == 0 else label_size * 0.72 for i in range(len(lines))]
                fonts = [label_font if i == 0 else "cormorant-600" for i in range(len(lines))]
                tw = max(K.font(f, sz).measureText(ln) for f, sz, ln in zip(fonts, sizes, lines))
                pw = min(w * 0.9 * Pr.U, tw + label_size * 2.2)
                phh = sum(sz * 1.3 for sz in sizes) + label_size * 0.8
                bx, by = (w * Pr.U - pw) / 2, 0.1 * Pr.U
                brass(pc, bx, by, pw, phh)
                yy = by + label_size * 0.4
                for ln, sz, f in zip(lines, sizes, fonts):
                    yy += sz * 1.3
                    K.text(pc, ln, w * Pr.U / 2, yy - sz * 0.3, sz, f, (40, 26, 10), tag="plaque")
    c.restore()
    return (sx, sy, ppm)


def brass(c, x, y, w, h, a=1.0):
    """A brushed brass plate with a bevelled edge (local units)."""
    r = skia.Rect.MakeXYWH(x, y, w, h)
    c.drawRect(r, paint(shader=K.lin((x, y), (x + w, y + h), [GOLD_HI, GOLD, (176, 132, 52), GOLD, GOLD_HI]), a=a))
    c.drawRect(r, paint(GOLD_LO, 0.9 * a, stroke=max(1.0, h * 0.06)))
    c.drawRect(r.makeInset(h * 0.08, h * 0.08), paint(GOLD_HI, 0.6 * a, stroke=max(0.8, h * 0.02)))


def plaque(c, x, y, lines, size=40, w=None, a=1.0, tag="plaque", font="cinzel-600", ink=(44, 28, 10), sub_font="cormorant-600"):
    """A museum label in screen space, centred on x, top at y: a brass plate, the first line in capitals, the rest in a
    smaller serif."""
    f0 = K.font(font, size)
    widths = [K.font(font if i == 0 else sub_font, size if i == 0 else size * 0.78).measureText(s) for i, s in enumerate(lines)]
    w = w or max(widths) + size * 1.6
    lh = size * 1.25
    h = lh * len(lines) + size * 0.7
    brass(c, x - w / 2, y, w, h, a)
    for i, s in enumerate(lines):
        K.text(c, s, x, y + size * 0.35 + lh * (i + 0.8), size if i == 0 else size * 0.78, font if i == 0 else sub_font, ink, tag=tag, a=a)
    return h


def scales(c, x, y, s, T, tilt=0.0, left=None, right=None, a=1.0, eye=1.0):
    """The great golden balance: a fluted column on stepped plinths, a beam with an eye at its pivot, two pans on
    chains. tilt in degrees (positive: the right pan goes down). left/right(c, px, py, s) fill the pans."""
    c.save()
    lp = paint()
    lp.setAlphaf(a)
    c.saveLayer(None, lp)
    gs = lambda x0, x1: C.gold_shader((x0, 0), (x1, 0))
    for i, (w, hh) in enumerate(((420, 50), (330, 46), (250, 40))):
        yy = y - sum(h_ for _, h_ in ((420, 50), (330, 46), (250, 40))[:i])
        c.drawRect(skia.Rect.MakeLTRB(x - w * s, yy - hh * s, x + w * s, yy), paint(shader=gs(x - w * s, x + w * s)))
        c.drawLine(x - w * s, yy - hh * s, x + w * s, yy - hh * s, paint(GOLD_HI, 0.8, stroke=2 * s))
    top = y - 136 * s - 900 * s
    c.drawRect(skia.Rect.MakeLTRB(x - 46 * s, top, x + 46 * s, y - 136 * s), paint(shader=gs(x - 46 * s, x + 46 * s)))
    for k in range(-2, 3):
        c.drawLine(x + k * 16 * s, top + 20 * s, x + k * 16 * s, y - 150 * s, paint(GOLD_LO, 0.6, stroke=3 * s))
    ang = math.radians(tilt)
    L = 480 * s
    ex, ey = math.cos(ang) * L, math.sin(ang) * L
    c.drawPath(K.capsule(x - ex, top - ey, x + ex, top + ey, 34 * s, 34 * s), paint(shader=gs(x - L, x + L)))
    if eye > 0:                                                      # an eye at the pivot
        c.drawCircle(x, top, 70 * s, paint(shader=gs(x - 70 * s, x + 70 * s)))
        C.lens(c, x, top, 56 * s, T, open_=0.5 + 0.5 * eye, ring=GOLD_LO, hot=eye * 0.6)
    for sd, fn in ((-1, left), (1, right)):
        px, py = x + sd * ex, top + sd * ey
        pan_y = py + 430 * s
        for k in (-1, 0, 1):
            c.drawLine(px, py, px + k * 150 * s, pan_y, paint(GOLD, 0.95, stroke=4 * s))
        c.drawPath(K.smooth([(px - 190 * s, pan_y), (px + 190 * s, pan_y), (px + 150 * s, pan_y + 60 * s), (px, pan_y + 84 * s), (px - 150 * s, pan_y + 60 * s)]),
                   paint(shader=gs(px - 190 * s, px + 190 * s)))
        c.drawOval(skia.Rect.MakeLTRB(px - 190 * s, pan_y - 22 * s, px + 190 * s, pan_y + 22 * s), paint(GOLD_LO))
        if fn is not None:
            fn(c, px, pan_y, s)
    c.restore()
    c.restore()


def enfilade(c, cam, T, rooms, depth=6.0, width=5.0, height=6.0, door=(1.9, 3.6), fog=(0, 0, 0), fog_d=0.05, label_size=50):
    """A line of rooms, one opening into the next: rooms = [(label, wall colour, accent)] from near to far, each wall at
    depth*(i+1) with a doorway through it and its label engraved above."""
    for i in reversed(range(len(rooms))):
        label, col, acc = rooms[i]
        z = depth * (i + 1)
        zp = depth * i if i > 0 else -depth                        # the first room runs back behind the camera
        for facing, x in ((1, -width / 2), (-1, width / 2)):
            wl = Pr.wall_x(x, zp, z, 0.0, height, facing)
            with wl.draw(c, cam) as pc:
                if pc is not None:
                    pc.drawRect(skia.Rect.MakeLTRB(0, 0, (z - zp) * Pr.U, height * Pr.U), paint(shader=K.lin((0, 0), (0, height * Pr.U), [mix(col, BLACK, 0.6), col, mix(col, BLACK, 0.4)])))
                    Pr.depth_fog(pc, wl, cam, fog, fog_d, 1.0)
        fl = Pr.floor(-width / 2, width / 2, zp, z)
        with fl.draw(c, cam) as pc:
            if pc is not None:
                _checker(pc, width, z - zp, 1.0, (220, 214, 204), (18, 14, 16))
                Pr.depth_fog(pc, fl, cam, fog, fog_d, 1.0)
        wz = Pr.wall_z(z, -width / 2, width / 2, 0.0, height)
        with wz.draw(c, cam) as pc:
            if pc is not None:
                dw, dh = door
                wall = skia.Path()
                wall.addRect(skia.Rect.MakeLTRB(0, 0, width * Pr.U, height * Pr.U))
                hole = skia.Path()
                hole.addRect(skia.Rect.MakeLTRB((width - dw) / 2 * Pr.U, (height - dh) * Pr.U, (width + dw) / 2 * Pr.U, height * Pr.U))
                wpath = skia.Op(wall, hole, skia.PathOp.kDifference_PathOp)
                pc.drawPath(wpath, paint(shader=K.lin((0, 0), (0, height * Pr.U), [mix(col, BLACK, 0.5), col, mix(col, BLACK, 0.25)])))
                pc.drawRect(hole.getBounds(), paint(acc, 0.95, stroke=14))
                pc.drawRect(hole.getBounds().makeOutset(18, 18), paint(GOLD, 0.8, stroke=5))
                if label and z - cam.pos[2] > 2.2:                  # not when the camera is about to pass under it
                    # and fading out as it rises into the top of the frame, where the app's own lettering sits
                    qt = cam.proj((0.0, dh + 0.45 + label_size / Pr.U * 0.85, z))
                    la = 1.0 if qt is None else K.ease(K.ramp(qt[1], 236, 330))
                    K.text(pc, label, width / 2 * Pr.U, (height - dh - 0.45) * Pr.U, label_size, "cinzel-600", GOLD_HI, tag="label", a=la)
                Pr.depth_fog(pc, wz, cam, fog, fog_d, 1.0)

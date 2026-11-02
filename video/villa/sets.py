"""Places: the square with its automaton clock, the labyrinth of alleys and its fountain, the villa (gate, gallery,
writing room, clockwork, mirrors, the locked door) and, at the end, an office and a bedroom in the present day."""
import math

import numpy as np
import skia

import gel as G
import kit as K
import pers as P
from kit import AMBER, BLACK, COBALT, EMERALD, MAGENTA, STONE, STONE_D, WHITE, H, W, mix, paint

# ------------------------------------------------------------------ the alleys

ALLEY_GELS = [MAGENTA, EMERALD, AMBER, COBALT, MAGENTA, AMBER, EMERALD]


def arch_face(pc, w_total, h_total, opening, spring, color):
    """The face of a stone arch in local units: a wall with a round-headed opening (even-odd fill)."""
    ww, hh, ow, sp = w_total * P.U, h_total * P.U, opening * P.U, spring * P.U
    p = skia.Path()
    p.setFillType(skia.PathFillType.kEvenOdd)
    p.addRect(skia.Rect.MakeLTRB(0, 0, ww, hh))
    x0 = (ww - ow) / 2
    top = hh - sp
    q = skia.Path()
    q.moveTo(x0, hh)
    q.lineTo(x0, top)
    q.arcTo(skia.Rect.MakeLTRB(x0, top - ow / 2, x0 + ow, top + ow / 2), 180, 180, False)
    q.lineTo(x0 + ow, hh)
    q.close()
    p.addPath(q)
    pc.drawPath(p, paint(color))
    return p


def sky(c, top=(10, 8, 40), mid=(60, 20, 70), low=(140, 40, 90), y0=0, y1=900, stars=True, seed=0, moon=None):
    """A dusk-into-night sky: deep cobalt above, violet, a magenta glow low down; a few stars; perhaps a moon."""
    c.drawRect(skia.Rect.MakeLTRB(0, y0, W, y1), paint(shader=K.lin((0, y0), (0, y1), [top, mid, low], [0.0, 0.55, 1.0])))
    if stars:
        rng = K.rng_at(seed, 99)
        for _ in range(60):
            x, y = rng.uniform(0, W), rng.uniform(y0, y0 + (y1 - y0) * 0.6)
            c.drawCircle(x, y, rng.uniform(0.8, 2.0), paint((255, 240, 230), rng.uniform(0.3, 0.9)))
    if moon is not None:
        mx, my, mr = moon
        G.pool(c, mx, my, mr * 4, (200, 190, 255), 0.25)
        c.drawCircle(mx, my, mr, paint((240, 236, 220)))
        c.drawCircle(mx + mr * 0.35, my - mr * 0.1, mr * 0.95, paint(mid))


def _cobbles(pc, ext, stone, seed):
    """Big worn paving slabs (basoli), each its own shade, dark joints."""
    x0, z0, x1, z1 = ext
    rng = K.rng_at(seed, 41)
    pc.drawPaint(paint(mix(BLACK, stone, 0.3)))
    yy = 0.0
    while yy < (z1 - z0) * P.U:
        h = rng.uniform(0.38, 0.62) * P.U
        xx = -rng.uniform(0, 0.4) * P.U
        while xx < (x1 - x0) * P.U:
            w = rng.uniform(0.45, 0.85) * P.U
            sh = rng.uniform(0.7, 1.12)
            colr = tuple(int(min(255, ch * sh)) for ch in stone)
            pc.drawRoundRect(skia.Rect.MakeXYWH(xx + 3, yy + 3, w - 6, h - 6), 10, 10, paint(colr))
            xx += w
        yy += h


def alley(c, cam, T, lights=None, length=40.0, width=3.2, height=9.0, arches=(7.0, 15.0, 23.0, 31.0), seed=0,
          fog=(6, 4, 8), density=0.075, stone=(196, 172, 150), shutters=True, wet=True, sky_=True):
    """A narrow stone alley receding from the camera: ashlar walls with shuttered windows, wet cobbles, round arches,
    lanterns throwing gel light; a strip of night sky above; the far end lost in darkness."""
    hw = width / 2
    if lights is None:
        lights = []
        for i, z in enumerate((3.0, 9.5, 16.0, 22.5, 29.0, 35.0)):
            side = -1 if i % 2 == 0 else 1
            lights.append(P.Light((side * (hw - 0.35), 3.1, z), ALLEY_GELS[(i + seed) % len(ALLEY_GELS)], 1.3, 1.5))
    if sky_:
        sky(c, y0=0, y1=1100, seed=seed)
    # floor: wet cobbles. Every plane is fixed in the world (not to the camera), so its texture holds still as the
    # camera dollies through it
    za, zb = -1.0, length + 6.0
    fl = P.floor(-hw, hw, za, zb)
    with fl.draw(c, cam) as pc:
        if pc is not None:
            P.lit(pc, fl, lights, lambda q: _cobbles(q, fl.ext, stone, seed), spread=1.1)
            P.depth_fog(pc, fl, cam, fog, density)
    # walls
    for side in (-1, 1):
        wl = P.wall_x(side * hw, za, zb, 0, height, facing=-side)

        def albedo(q, wl=wl, side=side):
            P.stone_blocks(q, wl.ext, stone, seed=seed + side * 3)
            if shutters:
                rng = K.rng_at(seed, side, 5)
                u = rng.uniform(1.5, 3.0)
                while u < wl.ext[2] - 1:
                    for lvl in (2.6, 5.4):
                        yy = (height - lvl - 1.4) * P.U
                        q.drawRect(skia.Rect.MakeXYWH(u * P.U - 10, yy - 10, 0.9 * P.U + 20, 1.4 * P.U + 20), paint((40, 34, 30)))
                        q.drawRect(skia.Rect.MakeXYWH(u * P.U, yy, 0.9 * P.U, 1.4 * P.U), paint((70, 86, 70)))
                        for k in range(8):
                            q.drawLine(u * P.U, yy + 8 + k * 17, u * P.U + 0.9 * P.U, yy + 8 + k * 17, paint((30, 36, 30), stroke=5))
                        q.drawRect(skia.Rect.MakeXYWH(u * P.U - 14, yy + 1.4 * P.U + 4, 0.9 * P.U + 28, 12), paint((190, 170, 150)))
                    u += rng.uniform(2.6, 4.2)

        with wl.draw(c, cam) as pc:
            if pc is not None:
                P.lit(pc, wl, lights, albedo)
                P.depth_fog(pc, wl, cam, fog, density)
    # arches, far to near
    for z in sorted(arches, reverse=True):
        if z < cam.pos[2] + 0.3:
            continue
        aw = P.wall_z(z, -hw - 0.2, hw + 0.2, 0, height)
        with aw.draw(c, cam) as pc:
            if pc is not None:
                path = arch_face(pc, width + 0.4, height, width * 0.86, 3.3, (0, 0, 0))
                pc.save()
                pc.clipPath(path, doAntiAlias=True)
                P.lit(pc, aw, lights, lambda q, aw=aw, z=z: P.stone_blocks(q, aw.ext, mix(stone, (190, 170, 150), 0.3), seed=int(z)), gain=1.3)
                P.depth_fog(pc, aw, cam, fog, density)
                pc.restore()
    # the lanterns, and their reflections in the wet cobbles
    for L in sorted(lights, key=lambda L: -cam.depth(L.pos)):
        q = cam.proj(L.pos)
        if q is None:
            continue
        s = cam.scale_at(L.pos) / 260
        fa = 1 - P.fog_at(cam, L.pos, density=density)
        if wet:
            g = cam.proj((L.pos[0] * 0.75, 0.0, L.pos[2] + 1.2))
            if g is not None:
                ln = 220 * s
                sh = K.lin((g[0], g[1]), (g[0], g[1] + ln), [L.color + (0.55 * fa,), L.color + (0.0,)])
                c.drawRoundRect(skia.Rect.MakeLTRB(g[0] - 16 * s, g[1], g[0] + 16 * s, g[1] + ln), 12 * s, 12 * s,
                                G.glow_paint(L.color, 1.0, shader=sh, blur=5 * s + 1))
                c.drawRoundRect(skia.Rect.MakeLTRB(g[0] - 5 * s, g[1], g[0] + 5 * s, g[1] + ln * 0.6), 4 * s, 4 * s,
                                G.glow_paint(mix(L.color, (255, 255, 255), 0.5), 0.5 * fa, blur=3 * s + 1))
        G.lantern(c, q[0], q[1], s, L.color, T, a=fa, seed=int(L.pos[2] * 3), glow=0.7)
    return lights


def fog_end(c, cam, z, color=(0, 0, 0), a=1.0, r=600):
    """The far end of a corridor swallowed by darkness (or coloured haze)."""
    q = cam.proj((0, 1.6, z))
    if q is None:
        return
    c.drawCircle(q[0], q[1], r, paint(shader=K.rad((q[0], q[1]), r, [color + (a,), color + (a * 0.6,), color + (0.0,)], [0, 0.4, 1])))


# ------------------------------------------------------------------ lighting in screen space

def lit2d(c, albedo_fn, light_fn, amb=(8, 6, 10)):
    """Albedo x light, in screen space: draw the scene's surfaces in their own colours, then modulate by a light layer
    (ambient plus coloured pools, added)."""
    c.saveLayer(None, None)
    albedo_fn(c)
    mp = skia.Paint()
    mp.setBlendMode(skia.BlendMode.kModulate)
    c.saveLayer(None, mp)
    c.drawPaint(paint(amb))
    light_fn(c)
    c.restore()
    c.restore()


def blocks2d(c, x0, y0, x1, y1, base, bw=58, bh=30, seed=0, var=0.2, mortar=0.5):
    """Ashlar blocks in screen space."""
    rng = K.rng_at(seed, 13)
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x0, y0, x1, y1))
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(mix(BLACK, base, mortar)))
    y = y0
    row = 0
    while y < y1:
        x = x0 - (row % 2) * bw * 0.5
        while x < x1:
            w = bw * rng.uniform(0.75, 1.3)
            sh = 1 - var + rng.uniform(0, 2 * var)
            col = tuple(int(min(255, ch * sh)) for ch in base)
            c.drawRect(skia.Rect.MakeXYWH(x + 1.5, y + 1.5, w - 3, bh - 3), paint(col))
            x += w
        y += bh
        row += 1
    c.restore()


def facade(c, x0, y0, x1, y1, base, T, seed=0, lit_windows=(), cols=3, rows=4, shutter=(60, 80, 64), balcony=True):
    """A palazzo front: plaster, a cornice, rows of tall windows with shutters, iron balconies, an arcade below."""
    rng = K.rng_at(seed, 21)
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(base))
    for k in range(40):                                        # weathered stucco: stains and patches
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        c.drawOval(skia.Rect.MakeXYWH(x, y, rng.uniform(30, 120), rng.uniform(20, 160)), paint(mix(base, BLACK, rng.uniform(0.1, 0.3)), 0.35, blur=12))
    c.drawRect(skia.Rect.MakeLTRB(x0 - 10, y0, x1 + 10, y0 + 26), paint(mix(base, WHITE, 0.25)))
    c.drawRect(skia.Rect.MakeLTRB(x0 - 10, y0 + 26, x1 + 10, y0 + 34), paint(mix(base, BLACK, 0.4)))
    ww = (x1 - x0) / cols
    arcade_top = y1 - 230
    hh = (arcade_top - y0 - 60) / rows
    windows = []
    for r in range(rows):
        for k in range(cols):
            wx = x0 + ww * k + ww * 0.28
            wy = y0 + 60 + hh * r + hh * 0.12
            w, h = ww * 0.44, hh * 0.72
            lit = (r, k) in lit_windows
            c.drawRect(skia.Rect.MakeLTRB(wx - 8, wy - 14, wx + w + 8, wy + h + 6), paint(mix(base, WHITE, 0.2)))
            c.drawRect(skia.Rect.MakeLTRB(wx, wy, wx + w, wy + h), paint((14, 10, 10) if not lit else (230, 150, 60)))
            windows.append((wx, wy, w, h, lit))
            if not lit:
                for s in (0, 1):                               # shutters, one open a crack
                    sx = wx + s * w * 0.5
                    c.drawRect(skia.Rect.MakeLTRB(sx, wy, sx + w * 0.5 - 2, wy + h), paint(shutter))
                    for j in range(int(h / 14)):
                        c.drawLine(sx + 2, wy + 6 + j * 14, sx + w * 0.5 - 4, wy + 6 + j * 14, paint(mix(shutter, BLACK, 0.45), stroke=3))
            if balcony and r == 1:
                c.drawRect(skia.Rect.MakeLTRB(wx - 20, wy + h, wx + w + 20, wy + h + 10), paint(mix(base, BLACK, 0.3)))
                for j in range(9):
                    bx = wx - 14 + j * (w + 28) / 8
                    c.drawLine(bx, wy + h - 40, bx, wy + h, paint((20, 16, 16), stroke=3))
                c.drawLine(wx - 18, wy + h - 40, wx + w + 18, wy + h - 40, paint((20, 16, 16), stroke=4))
    # the arcade at street level
    c.drawRect(skia.Rect.MakeLTRB(x0, arcade_top, x1, y1), paint(mix(base, BLACK, 0.15)))
    n = max(1, int((x1 - x0) / 170))
    aw = (x1 - x0) / n
    for k in range(n):
        ax = x0 + aw * k + aw * 0.12
        a_w = aw * 0.76
        p = skia.Path()
        p.moveTo(ax, y1)
        p.lineTo(ax, arcade_top + 60 + a_w / 2)
        p.arcTo(skia.Rect.MakeLTRB(ax, arcade_top + 60, ax + a_w, arcade_top + 60 + a_w), 180, 180, False)
        p.lineTo(ax + a_w, y1)
        p.close()
        c.drawPath(p, paint((8, 6, 8)))
    return windows


def clock_tower(c, cx, top, bottom, T, width=300, stone=(176, 160, 150), seed=4):
    """The tower: a pyramid roof, a belfry with its bell, the great clock, and below it the automaton's stage."""
    x0, x1 = cx - width / 2, cx + width / 2
    blocks2d(c, x0, top + 230, x1, bottom, stone, bw=60, bh=32, seed=seed)
    # pilasters and cornices
    for xx in (x0, x1 - 26):
        c.drawRect(skia.Rect.MakeLTRB(xx, top + 230, xx + 26, bottom), paint(mix(stone, WHITE, 0.15)))
    for yy in (top + 230, top + 380, top + 640, top + 790):
        c.drawRect(skia.Rect.MakeLTRB(x0 - 16, yy, x1 + 16, yy + 22), paint(mix(stone, WHITE, 0.2)))
        c.drawRect(skia.Rect.MakeLTRB(x0 - 16, yy + 22, x1 + 16, yy + 28), paint(mix(stone, BLACK, 0.5)))
    # roof
    c.drawPath(K.path([(x0 - 24, top + 232), (cx, top), (x1 + 24, top + 232)]), paint((60, 50, 56)))
    c.drawLine(cx, top - 70, cx, top + 10, paint((40, 34, 30), stroke=6))
    c.drawPath(K.path([(cx, top - 70), (cx + 40, top - 56), (cx, top - 42)]), paint((40, 34, 30)))
    # belfry
    for k in range(2):
        bx = x0 + 50 + k * 120
        p = skia.Path()
        p.moveTo(bx, top + 380)
        p.lineTo(bx, top + 300)
        p.arcTo(skia.Rect.MakeLTRB(bx, top + 260, bx + 80, top + 340), 180, 180, False)
        p.lineTo(bx + 80, top + 380)
        p.close()
        c.drawPath(p, paint((6, 4, 8)))
    sw = 6 * math.sin(T * 2.2)
    c.drawPath(K.smooth([(cx - 34 + sw, top + 362), (cx - 24 + sw, top + 300), (cx + sw, top + 288), (cx + 24 + sw, top + 300), (cx + 34 + sw, top + 362)]),
               paint((150, 110, 50)))
    return (cx, top + 515)                                      # the clock's centre


def square(c, T, clock_r=118, doors=0.0, parade=None, group=0.0, clara=None, birds=None):
    """The square at dusk: the clock tower between two palazzi, arcades with lanterns, wet paving, a violet sky.
    parade: u (0..1 along the rail) offsets of the little scholars; doors: 0..1 open; group: 0..1 the tour group
    walking off; clara: (x, y, s) of her small figure; birds: t since the pigeons rose."""
    sky(c, top=(8, 8, 46), mid=(70, 26, 96), low=(210, 70, 120), y0=0, y1=1300, seed=3, moon=(840, 230, 34))
    tower_cx, tower_top, ground = 540, 150, 1450
    lights = [(170, 1300, 520, MAGENTA, 0.9), (910, 1300, 520, EMERALD, 0.9), (540, 760, 520, AMBER, 0.75),
              (540, 380, 700, (60, 80, 220), 0.45), (540, 1700, 700, MAGENTA, 0.35)]

    def albedo(cc):
        facade(cc, -40, 560, 395, ground, (196, 140, 120), T, seed=1, lit_windows=((0, 1), (2, 0)), cols=2, rows=4)
        facade(cc, 685, 600, 1120, ground, (170, 160, 120), T, seed=2, lit_windows=((1, 1), (3, 0)), cols=2, rows=4, shutter=(90, 60, 50))
        clock_tower(cc, tower_cx, tower_top, ground, T)
        # the paving: slabs in perspective toward a far point above the tower's foot
        cc.drawRect(skia.Rect.MakeLTRB(0, ground, W, H), paint((120, 110, 104)))
        vx, vy = 540, 980
        for k in range(-14, 15):
            xb = 540 + k * 160
            xg = vx + (xb - vx) * (ground - vy) / (H - vy)
            cc.drawLine(xg, ground, xb, H, paint((70, 64, 60), stroke=3))
        y, step = ground + 8, 14
        while y < H:
            cc.drawLine(0, y, W, y, paint((70, 64, 60), stroke=3))
            step *= 1.32
            y += step

    def light(cc):
        for x, y, r, col, a in lights:
            G.pool(cc, x, y, r, col, a)
        G.pool(cc, tower_cx, 640, 260, (255, 200, 120), 0.5)

    lit2d(c, albedo, light, amb=(26, 20, 34))
    # emissive: lit windows, the clock face under its lamp, lanterns
    for (x0, y0, w, h) in ((70, 852, 70, 170), (250, 1100, 70, 170), (880, 980, 70, 170)):
        G.pool(c, x0 + w / 2, y0 + h / 2, 160, AMBER, 0.35)
    cx, cy = 540, 665
    clock_face(c, cx, cy, clock_r, 9, 0, dial=(190, 168, 128))                # old enamel under a lamp, not a light
    G.pool(c, cx, cy - clock_r * 0.5, clock_r * 1.1, (255, 190, 110), 0.07)
    # the automaton's stage under the clock
    sx, sy = 540, 880
    c.drawRect(skia.Rect.MakeLTRB(sx - 120, sy - 70, sx + 120, sy + 20), paint((12, 8, 10)))
    G.pool(c, sx, sy - 20, 160, AMBER, 0.45)
    for side in (-1, 1):                                       # little doors that swing open
        dx = sx + side * 80
        wd = 40 * (1 - doors)
        c.drawRect(skia.Rect.MakeLTRB(dx - 20, sy - 64, dx - 20 + max(2, wd), sy + 14), paint((110, 40, 30)))
    c.drawRect(skia.Rect.MakeLTRB(sx - 124, sy + 14, sx + 124, sy + 24), paint((150, 110, 50)))
    if parade is not None:
        for k, u in enumerate(parade):
            if 0 <= u <= 1:
                figurine(c, sx - 80 + 160 * u, sy + 14, 0.36, T, "scholar", seed=k, arm=K.ease(min(1, max(0, (u - 0.4) * 4))))
        figurine(c, sx, sy + 14, 0.42, T, "governess", arm=0.5 + 0.5 * math.sin(T * 3))
    for x in (120, 960):
        G.lantern(c, x, 1240, 0.55, MAGENTA if x < 540 else EMERALD, T, seed=x)
    # people on the square
    if group < 1:                                              # the tour group, following a red umbrella out of the square
        coats = [(150, 60, 70), (60, 80, 130), (130, 112, 70), (96, 60, 110), (50, 100, 84), (140, 90, 56), (80, 70, 90)]
        for k in range(7):
            gx = 660 + (k % 4) * 44 + (k // 4) * 22 + group * 300
            figure_tiny(c, gx, 1468 + (k // 4) * 22, 0.8 + 0.05 * (k // 4), T, coats[k], a=1 - group, seed=k, umbrella=(k == 0),
                        hair=[(40, 26, 24), (120, 90, 60), (30, 24, 26), (160, 150, 140)][k % 4])
    if clara is not None:
        figure_tiny(c, *clara, T, (196, 168, 120), seed=9, scarf=True)
    if birds is not None and birds >= 0:
        rng = K.rng_at(5, 5)
        for k in range(14):
            bx = 540 + rng.uniform(-80, 80) + birds * rng.uniform(-500, 500)
            by = 470 - birds * rng.uniform(150, 420) + rng.uniform(-40, 40)
            fl = math.sin(T * 30 + k) * 10
            c.drawPath(K.path([(bx - 16, by - fl), (bx, by + 4), (bx + 16, by - fl), (bx, by)]), paint((20, 14, 20)))


from props import clock_face, figurine  # noqa: E402  (props imports gel/kit only)


def figure_tiny(c, x, y, s, T, coat, a=1.0, seed=0, umbrella=False, scarf=False, walk=True, hair=None):
    """A small standing or walking figure for wide shots."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    ph = T * 6 + seed
    sw = 10 * math.sin(ph) if walk else 0
    c.drawLine(-6, -40, -6 + sw, 0, paint((20, 16, 18), a, stroke=10))
    c.drawLine(6, -40, 6 - sw, 0, paint((20, 16, 18), a, stroke=10))
    c.drawPath(K.smooth([(-22, -40), (-18, -110), (0, -124), (18, -110), (22, -40)]), paint(coat, a))
    c.drawPath(K.smooth([(-22, -40), (-18, -110), (0, -124), (-4, -80), (-6, -40)]), paint(mix(coat, (255, 80, 180), 0.25), 0.5 * a))
    c.drawCircle(0, -140, 15, paint((176, 136, 124), a))
    if hair is not None:
        c.drawPath(K.smooth([(-16, -138), (-14, -154), (0, -158), (14, -154), (16, -138), (0, -148)]), paint(hair, a))
    if scarf:
        c.drawPath(K.smooth([(-16, -150), (0, -160), (16, -150), (12, -130), (-12, -130)]), paint((110, 46, 26), a))
    if umbrella:
        c.drawLine(18, -100, 18, -230, paint((20, 16, 18), a, stroke=4))
        c.drawPath(K.path([(-26, -230), (18, -270), (62, -230)]), paint((200, 40, 50), a))
    c.restore()


# ------------------------------------------------------------------ the villa: a gallery / corridor in perspective

def _checker(pc, ext, a=(176, 170, 162), b=(26, 22, 26), size=0.6):
    x0, z0, x1, z1 = ext
    s = size * P.U
    pc.drawPaint(paint(b))
    for i in range(int((x1 - x0) / size) + 1):
        for j in range(int((z1 - z0) / size) + 1):
            if (i + j) % 2 == 0:
                pc.drawRect(skia.Rect.MakeXYWH(i * s, j * s, s, s), paint(a))


def _damask(pc, ext, base=(110, 18, 36), seed=0):
    u0, v0, u1, v1 = ext
    pc.drawPaint(paint(base))
    rng = K.rng_at(seed, 8)
    for i in range(int((u1 - u0) / 0.5) + 1):
        for j in range(int((v1 - v0) / 0.6) + 1):
            x, y = (u0 + i * 0.5 + (j % 2) * 0.25) * P.U, (v0 + j * 0.6) * P.U
            pc.drawPath(K.smooth([(x, y - 18), (x + 12, y), (x, y + 18), (x - 12, y)]), paint(mix(base, BLACK, 0.35)))
    pc.drawRect(skia.Rect.MakeLTRB(u0 * P.U, (v1 - 1.0) * P.U, u1 * P.U, v1 * P.U), paint((60, 36, 24)))   # wainscot
    for i in range(int((u1 - u0) / 0.8) + 1):
        pc.drawRect(skia.Rect.MakeXYWH((u0 + i * 0.8) * P.U + 8, (v1 - 0.9) * P.U, 0.8 * P.U - 16, 0.7 * P.U), paint((80, 48, 30), stroke=4))


def gallery(c, cam, T, length=30.0, width=4.4, height=5.0, lights=None, portraits=None, end_door=True, fog=(4, 2, 6),
            density=0.05, wall=(150, 30, 50), seed=0, drapes=None, fresco=False):
    """A long villa gallery: a black-and-white marble floor, damask walls hung with portraits (each drawn by
    portraits(pc, index, w, h) in its frame's local units), sconces in gel colours, the far end in darkness.
    drapes: a velvet colour for heavy curtains between the portraits; fresco: a faded painted ceiling."""
    hw = width / 2
    za, zb = -1.0, length + 8.0                                # fixed in the world: textures hold still as the camera moves
    if lights is None:
        cols = [MAGENTA, EMERALD, AMBER, COBALT]
        lights = [P.Light(((-1 if i % 2 == 0 else 1) * (hw - 0.45), 2.7, 1.5 + i * 2.4), cols[i % 4], 2.0, 2.2) for i in range(12)]
    fl = P.floor(-hw, hw, za, zb)
    with fl.draw(c, cam) as pc:
        if pc is not None:
            P.lit(pc, fl, lights, lambda q: _checker(q, fl.ext), spread=1.2)
            P.depth_fog(pc, fl, cam, fog, density)
    ce = P.ceiling(-hw, hw, za, zb, height)

    def ceil_albedo(q):
        if fresco:
            import hall
            hall.fresco(q, width * P.U, (zb - za) * P.U, seed=seed, medallion=600)
        else:
            q.drawPaint(paint((60, 40, 30)))
    with ce.draw(c, cam) as pc:
        if pc is not None:
            P.lit(pc, ce, lights, ceil_albedo, gain=0.6 if not fresco else 0.26, amb=(7, 5, 7) if not fresco else (30, 26, 26))
            P.depth_fog(pc, ce, cam, fog, density)
    for side in (-1, 1):
        wl = P.wall_x(side * hw, za, zb, 0, height, facing=-side)

        def albedo(q, wl=wl, side=side):
            _damask(q, wl.ext, wall, seed + side)
            if drapes is not None:                             # heavy velvet curtains, tied back, between the portraits
                import hall
                u = (2.2 if side < 0 else 3.7) - 0.85
                while u < wl.ext[2] - 1:
                    hall.drape(q, (u - 0.32) * P.U, 0, u * P.U, height * P.U, color=drapes, side=-1, folds=3, tie=0.6, fringe=False)
                    hall.drape(q, u * P.U, 0, (u + 0.32) * P.U, height * P.U, color=drapes, side=1, folds=3, tie=0.6, fringe=False)
                    q.drawRect(skia.Rect.MakeLTRB((u - 0.4) * P.U, 0, (u + 0.4) * P.U, 0.25 * P.U), paint(mix(drapes, BLACK, 0.3)))
                    u += 3.0
            if portraits is not None:
                k = 0
                u = 2.2 if side < 0 else 3.7
                while u < wl.ext[2] - 1:
                    zw = wl.world(u, 0)[2]
                    fx0, fy0, fw, fh = u * P.U, 1.2 * P.U, 1.3 * P.U, 1.8 * P.U
                    q.save()
                    q.translate(fx0, fy0)
                    q.clipRect(skia.Rect.MakeLTRB(0, 0, fw, fh))
                    portraits(q, (k, side), fw, fh)
                    q.restore()
                    from props import frame_gilt
                    frame_gilt(q, fx0, fy0, fx0 + fw, fy0 + fh, t=14)
                    k += 1
                    u += 3.0
        with wl.draw(c, cam) as pc:
            if pc is not None:
                P.lit(pc, wl, lights, albedo)
                P.depth_fog(pc, wl, cam, fog, density)
    if end_door:
        ew = P.wall_z(zb - 0.5, -hw, hw, 0, height)
        with ew.draw(c, cam) as pc:
            if pc is not None:
                pc.drawPaint(paint((8, 4, 6)))
                pc.drawRect(skia.Rect.MakeLTRB((hw - 0.7) * P.U, (height - 3.0) * P.U, (hw + 0.7) * P.U, height * P.U), paint((40, 20, 12)))
    for L in lights:                                            # the sconces
        q = cam.proj(L.pos)
        if q is None:
            continue
        s = cam.scale_at(L.pos) / 300
        fa = 1 - P.fog_at(cam, L.pos, density=density)
        G.candle(c, q[0], q[1] + 40 * s, s * 0.9, T, a=fa, seed=int(L.pos[2]), glow=0.6, color=L.color)
    return lights

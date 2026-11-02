"""I. THE EYE - what it watches, and how little it needs us.

e_list   - seven vitrines in seven jewel-toned rooms, one for each word: a lens, a face, a microphone, a plate, a pin,
           a cursor, a receipt.
e_house  - a house made of glass alone in the dunes at dusk, lit from inside; around it, in the dark, eyes.
e_army   - an endless hall of porcelain watchers at their screens; at "Now" they stutter, freeze, and crumble to sand,
           leaving one lens.
e_doors  - five rooms, one inside the next: CAMERA, FACE, BEHAVIOR, MOVEMENT, ALERT - the camera rushes through.
e_salt   - seen from above, a tiny figure crossing the salt flat; every place, person and purchase strung on gold thread.
e_hand   - the threads gathered up into a vast porcelain hand with golden claws.
e_hush   - dead silence: her face, eyes shut.
e_eyes   - her eyes snap open: lenses; every lens in her aureole turns to you."""
import math

import numpy as np
import skia

import couture as C
import dream as D
import gel as G
import hall as Hl
import kit as K
import look as LK
import pers as Pr
import props as P
from common import E, S, Wx, hit, shake, stutter, talk, zoom
from edit import cut, end
from kit import BLACK, H, W, WHITE, mix, paint, ramp

LIST = [("Cameras.", ["CAMERA"], Hl.ROYAL_WALL), ("Faces.", ["FACE"], Hl.LACQUER_RED), ("Microphones.", ["MICROPHONE"], Hl.EMERALD_WALL),
        ("License", ["LICENSE PLATE"], (96, 62, 10)), ("Location.", ["LOCATION"], (12, 70, 90)), ("Clicks.", ["CLICKS"], Hl.BLACK_WALL),
        ("Receipts.", ["RECEIPTS"], Hl.LACQUER_RED)]


def _exhibit(i, T):
    def f(c, sx, sy, ppm):
        s = ppm / 360.0
        if i == 0:
            C.lens(c, sx, sy - ppm * 0.62, ppm * 0.42, T, open_=0.45 + 0.3 * math.sin(T * 2), ring=C.GOLD, coat=(120, 40, 180))
        elif i == 1:
            C.mask(c, sx, sy - ppm * 0.78, ppm / 480 * 0.95, T, eyes=0.0)
        elif i == 2:
            P.microphone(c, sx, sy, s, T)
        elif i == 3:
            P.plate(c, sx, sy - ppm * 0.2, s * 1.1, T)
        elif i == 4:
            P.pin(c, sx, sy, s, T)
        elif i == 5:
            P.cursor(c, sx, sy, s * 1.05, T)
        else:
            P.receipt(c, sx, sy, s * 1.05, T, unroll=1.0)
    return f


def s_e_list(T, idx):
    t0 = cut("e_list")
    starts = [t0] + [Wx("e1", w) - 0.06 for w, _, _ in LIST[1:]]
    k = max(i for i, s in enumerate(starts) if s <= T + 1e-6)
    u = T - starts[k]
    word, label, wall = LIST[k]
    st = K.Stage((0, 0, 0))
    c = st.c
    cam = Pr.Cam((0.0, 1.45, -0.3 + 0.35 * u), pitch=-1.0, f=1100)
    lit = min(1.0, 0.25 + u / 0.12)
    Hl.gallery(c, cam, T, length=26, width=6, height=6, wall=wall, lights=[Pr.Light((0, 5.5, 3.2), (255, 222, 176), 1.2 * lit, 3.0)])
    Hl.vitrine(c, cam, 0.0, 3.2, 1.2, 1.2, 1.6, 0.9, T, content=_exhibit(k, T), label=label, height=6.0, label_size=11, lit=lit)
    if u < 0.08:
        c.drawPaint(paint(WHITE, 0.5 * (1 - u / 0.08)))
    return st.arr


def _house_scene(c, T, k_eyes=1.0, cam_z=-14.0):
    D.sky(c, D.SKY_DUSK, 0, 1060, 0.6)
    G.pool(c, 540, 1060, 700, (255, 130, 80), 0.25)
    D.dunes(c, T, HOUSE_FIELD, pal=dict(lit=(160, 80, 70), mid=(90, 40, 50), shade=(30, 12, 26), deep=(12, 4, 12), rim=(255, 170, 120)),
            haze_col=(200, 90, 80), stream=0.4)
    D.eyes_in_dark(c, T, n=110, y0=1120, y1=1900, seed=4, a=k_eyes, size=1.9)
    cam = Pr.Cam((0.0, 2.2, cam_z), pitch=-3, f=1000)

    def inside(c_, cam_):
        q = cam_.proj((0.4, 0.0, 0.0))
        if q is not None:
            sc = cam_.scale_at((0.4, 0.0, 0.0))
            c_.drawRect(skia.Rect.MakeLTRB(q[0] - sc * 1.0, q[1] - sc * 0.75, q[0] + sc * 0.6, q[1] - sc * 0.7), paint((40, 20, 10)))
            C.doll(c_, q[0] - sc * 0.5, q[1], sc / 720 * 1.5, T, pose="type", tint=(250, 236, 214))
    D.glass_house(c, cam, 0.0, 0.0, w=4.4, d=4.0, h=2.6, roof=1.4, T=T, inside=inside, glow=1.0)


HOUSE_FIELD = D.dune_field(23, 4, horizon=1060, spread=0.5, tall=0.9)


def s_e_house(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("e_house")
    k = ramp(T, Wx("e2", "house") - 0.2, Wx("e2", "glass") + 0.3)
    _house_scene(c, T, k_eyes=k, cam_z=-13.0 + 2.5 * ramp(T, t0, end("e_house")))
    return st.arr


ARMY = [(x, z) for z in np.arange(-3.4, 46.0, 1.6) for x in np.arange(-11.0, 11.5, 1.5)]


def s_e_army(T, idx):
    st = K.Stage((6, 8, 20))
    c = st.c
    t0, t1 = cut("e_army"), end("e_army")
    tn = Wx("e3", "Now") - 0.05
    cam = Pr.Cam((0.0, 13.0, -6.0 + 0.6 * (T - t0)), pitch=-48, f=900)
    fl = Pr.floor(-14, 14, -20.0, 60.0)                             # the floor runs on under the camera: no edge
    with fl.draw(c, cam) as pc:
        if pc is not None:
            pc.drawRect(skia.Rect.MakeLTRB(0, 0, 28 * Pr.U, 80 * Pr.U), paint((16, 22, 60)))
            for i in range(29):
                pc.drawLine(i * Pr.U, 0, i * Pr.U, 80 * Pr.U, paint((60, 80, 160), 0.25, stroke=3))
            Pr.depth_fog(pc, fl, cam, (6, 8, 20), 0.05, 2.0)
    rng = K.rng_at(5, 9)
    ts = stutter(T, t0, period=0.5, move=0.12, seed=2)
    order = sorted(range(len(ARMY)), key=lambda i: -abs(ARMY[i][0]) - ARMY[i][1] * 0.3)
    rank = {i: r for r, i in enumerate(order)}
    for i, (x, z) in sorted(enumerate(ARMY), key=lambda p: -p[1][1]):
        q = cam.proj((x, 0.0, z))
        if q is None:
            continue
        sc = cam.scale_at((x, 0.0, z))
        fade = 1 - Pr.fog_at(cam, (x, 0, z), (0, 0, 0), 0.045, 2.0)
        tc = tn + 0.25 + 1.6 * rank[i] / len(ARMY)                    # when this one crumbles
        if T < tc:
            sx, sy = q[0], q[1]
            c.drawRect(skia.Rect.MakeLTRB(sx - sc * 0.32, sy - sc * 0.95, sx + sc * 0.32, sy - sc * 0.55), G.glow_paint((120, 200, 255), 0.75 * fade))
            turn = 0.0 if T > tn else 6 * math.sin(ts * 3 + i)
            C.doll_tiny(c, sx, sy + sc * 0.25, sc / 60 * 0.9, col=(236, 232, 226), a=fade, sway=turn)
        else:
            v = T - tc
            for k in range(6):
                px = q[0] + rng.uniform(-0.3, 0.3) * sc
                py = q[1] + (rng.uniform(-0.6, 0.2) + v * 1.2) * sc
                c.drawCircle(px, py, max(0.8, sc * 0.04), paint((230, 190, 120), max(0.0, 0.8 - v) * fade))
    if T > tn + 0.5:
        k = K.ease(ramp(T, tn + 0.5, t1))
        G.pool(c, 540, 820, 500 * k, (255, 60, 60), 0.3 * k)
        C.lens(c, 540, 820, 230 * k + 1, T, open_=0.2 + 0.6 * k, ring=C.GOLD, coat=(150, 30, 50), hot=k)
    return st.arr


DOORS = [("Camera.", "CAMERA", Hl.ROYAL_WALL), ("Face.", "FACE", Hl.LACQUER_RED), ("Behavior.", "BEHAVIOR", Hl.EMERALD_WALL),
         ("Movement.", "MOVEMENT", (96, 62, 10)), ("Alert.", "ALERT", (150, 0, 12))]


def s_e_doors(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    starts = [Wx("e4", w) for w, _, _ in DOORS]
    k = max([i for i, s in enumerate(starts) if s - 0.25 <= T] + [0])
    u = K.ease(ramp(T, starts[k] - 0.25, starts[k] + 0.2))
    z = 6.0 * k + 6.0 * u - 4.5 if k > 0 else -4.5 + 1.5 * ramp(T, cut("e_doors"), starts[0])
    cam = Pr.Cam((0.0, 1.6, z), pitch=0, f=760)
    rooms = [(lbl, col, (255, 40, 40) if i == 4 else C.GOLD) for i, (_, lbl, col) in enumerate(DOORS)]
    Hl.enfilade(c, cam, T, rooms + [("", (20, 0, 4), (255, 40, 40))], label_size=46)
    if T > starts[4]:                                              # the alarm
        pulse = 0.5 + 0.5 * math.sin((T - starts[4]) * 18)
        c.drawPaint(G.glow_paint((255, 20, 20), 0.25 * pulse))
    return st.arr


def _top_person(c, x, y, s, col=(250, 248, 244), a=1.0, ang=0.0, shadow=0.0):
    """A person seen from straight above (shoulders and head), and, low sun from the left, a long shadow to the right."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    if shadow > 0:
        c.drawPath(K.smooth([(0, -8 * s), (shadow * 10 * s, -5 * s), (shadow * 12 * s, 0), (shadow * 10 * s, 5 * s), (0, 8 * s)]),
                   paint((80, 84, 104), 0.45 * a, blur=1.5 * s))
    c.drawOval(skia.Rect.MakeLTRB(-16 * s, -9 * s, 16 * s, 9 * s), paint(col, a))
    c.drawCircle(0, 0, 7 * s, paint(mix(col, (60, 50, 50), 0.6), a))
    c.restore()


NODES = [("go", "WHERE YOU GO", (0.22, 0.25)), ("meet", "WHO YOU MEET", (0.79, 0.24)), ("buy", "WHAT YOU BUY", (0.83, 0.50)),
         ("read", "WHAT YOU READ", (0.17, 0.53)), ("say", "WHAT YOU SAY", (0.29, 0.72)), ("protests", "WHICH PROTESTS", (0.73, 0.73))]


def _thing(c, i, x, y, s, T, a=1.0):
    """What waits at each place, seen from above with a long shadow to the right: a door frame, two people, a receipt,
    an open book, a microphone, a candle."""
    sh = paint((80, 84, 104), 0.4 * a, blur=2 * s)
    if i == 0:                                                       # a door frame standing alone on the salt
        c.drawRect(skia.Rect.MakeLTRB(x - 30 * s, y - 4 * s, x + 30 * s, y + 4 * s), paint(shader=C.gold_shader((x - 30 * s, 0), (x + 30 * s, 0)), a=a))
        c.drawPath(K.path([(x - 30 * s, y), (x + 30 * s, y), (x + 150 * s, y + 18 * s), (x + 90 * s, y + 18 * s)]), sh)
    elif i == 1:                                                     # two people, facing
        for d in (-1, 1):
            _top_person(c, x + d * 18 * s, y, 1.05 * s, a=a, ang=d * 90, shadow=4.0)
    elif i == 2:                                                     # a receipt, curling
        c.drawPath(K.smooth([(x - 10 * s, y - 34 * s), (x + 10 * s, y - 34 * s), (x + 14 * s, y + 10 * s), (x + 30 * s, y + 30 * s), (x - 6 * s, y + 26 * s),
                             (x - 12 * s, y)]), paint((252, 250, 244), a))
        for k in range(5):
            c.drawLine(x - 6 * s, y - 26 * s + k * 9 * s, x + 6 * s, y - 26 * s + k * 9 * s, paint((140, 140, 150), 0.7 * a, stroke=1.5 * s))
    elif i == 3:                                                     # an open book
        c.drawPath(K.path([(x - 34 * s, y - 22 * s), (x, y - 18 * s), (x + 34 * s, y - 22 * s), (x + 34 * s, y + 22 * s), (x, y + 26 * s), (x - 34 * s, y + 22 * s)]),
                   paint((120, 10, 24), a))
        c.drawPath(K.path([(x - 30 * s, y - 18 * s), (x, y - 14 * s), (x + 30 * s, y - 18 * s), (x + 30 * s, y + 18 * s), (x, y + 22 * s), (x - 30 * s, y + 18 * s)]),
                   paint((246, 240, 226), a))
        c.drawLine(x, y - 14 * s, x, y + 22 * s, paint((150, 130, 110), a, stroke=1.5 * s))
    elif i == 4:                                                     # a microphone on its stand
        c.drawCircle(x, y, 16 * s, paint(shader=C.gold_shader((x - 16 * s, 0), (x + 16 * s, 0)), a=a))
        c.drawCircle(x, y, 9 * s, paint(C.GOLD_LO, a))
        c.drawPath(K.path([(x, y - 6 * s), (x + 110 * s, y + 6 * s), (x + 110 * s, y + 12 * s), (x, y + 6 * s)]), sh)
    else:                                                            # a candle, lit
        G.pool(c, x, y, 70 * s, (255, 190, 100), 0.55 * a)
        c.drawCircle(x, y, 9 * s, paint((250, 244, 230), a))
        c.drawCircle(x, y, 4 * s, G.glow_paint((255, 210, 120), a))


def _web(c, T, k_all=None, scale=1.0, cx=540, cy=900, a=1.0, strings_to=None):
    """The figure's day as gold thread on white salt, seen from above: from the tiny figure to each place it goes, each
    with a small black-lacquer plaque laid on the salt beside it (drawn over the threads, never crossed by them)."""
    me = (cx, cy + (0.48 - 0.5) * 1300 * scale)
    pts = []
    for i, (w, label, (fx, fy)) in enumerate(NODES):
        t = Wx("e6", w) if k_all is None else -1
        k = 1.0 if k_all is not None else K.ease(ramp(T, t - 0.1, t + 0.3))
        px, py = cx + (fx - 0.5) * W * scale, cy + (fy - 0.5) * 1300 * scale
        pts.append((px, py, k, label))
    for px, py, k, label in pts:                                     # the threads, with their faint shadows on the salt
        if k <= 0:
            continue
        ex, ey = me[0] + (px - me[0]) * k, me[1] + (py - me[1]) * k
        c.drawLine(me[0] + 5, me[1] + 4, ex + 5, ey + 4, paint((90, 90, 110), 0.25 * a, stroke=4 * scale, blur=2))
        c.drawLine(me[0], me[1], ex, ey, paint(C.GOLD_LO, 0.9 * a, stroke=6 * scale))
        c.drawLine(me[0], me[1], ex, ey, paint(C.GOLD_HI, a, stroke=2.5 * scale))
        c.drawLine(me[0], me[1], ex, ey, G.glow_paint(C.GOLD_HI, 0.35 * a, blur=4))
    for i, (px, py, k, label) in enumerate(pts):
        if k <= 0.05:
            continue
        c.drawCircle(px, py, 44 * scale * k, paint(C.GOLD, 0.55 * a, stroke=2.5))
        _thing(c, i, px, py, 1.6 * scale * k, T, a=a)
    _top_person(c, me[0], me[1], 2.0 * scale, a=a, shadow=6.0)
    if scale > 0.8:
        f = K.font("cinzel-600", 34)
        for px, py, k, label in pts:
            if k <= 0.05 or not label:
                continue
            dx, dy = px - me[0], py - me[1]
            d = math.hypot(dx, dy) or 1.0
            lx, ly = px + dx / d * 40, py + (78 if dy > -60 else -62)
            hw = f.measureText(label) / 2 + 18
            lx = min(max(lx, 70 + hw), 1010 - hw)
            c.drawPath(K.rrect(lx - hw, ly - 38, lx + hw, ly + 13, 6), paint((12, 8, 10), 0.9 * a * k))
            c.drawPath(K.rrect(lx - hw, ly - 38, lx + hw, ly + 13, 6), paint(C.GOLD, 0.8 * a * k, stroke=2))
            K.text(c, label, lx, ly, 34, "cinzel-600", C.GOLD_HI, tag="label", a=a * k)
    return pts, me


_SALT = {}


def _salt_net(size):
    """The salt crust's crack network: a hex lattice with every corner nudged (shared corners move together)."""
    if size not in _SALT:
        def vert(i, j, k):
            ang = math.pi / 3 * k
            cx = (i - 11) * size * 1.5
            cy = (j - 13) * size * 1.732 + (size * 0.866 if i % 2 else 0)
            x, y = cx + size * math.cos(ang), cy + size * math.sin(ang)
            h = (int(round(x * 7.0)) * 73856093 ^ int(round(y * 7.0)) * 19349663) & 0xFFFF
            return x + size * 0.42 * ((h & 0xFF) / 255 - 0.5), y + size * 0.42 * ((h >> 8 & 0xFF) / 255 - 0.5)
        p = skia.Path()
        for i in range(0, 23):
            for j in range(0, 27):
                vs = [vert(i, j, k) for k in range(6)]
                p.moveTo(*vs[0])
                for v in vs[1:]:
                    p.lineTo(*v)
                p.close()
        _SALT[size] = p
    return _SALT[size]


def _salt_top(c, T, z=1.0):
    """The salt flat from straight above in a low morning sun: a warm white crust of raised polygon ridges, each with a
    shadow and a lit edge, paling to blue-grey at the edges of the world."""
    c.drawRect(skia.Rect.MakeLTRB(-W, -H, 2 * W, 2 * H), paint(shader=K.rad((520, 860), 1250, [(250, 246, 238), (226, 226, 230), (172, 178, 198)], [0.0, 0.55, 1.0])))
    rng = K.rng_at(77, 3)
    for k in range(9):                                               # faint drifts of tone in the crust
        x, y, r = rng.uniform(0, W), rng.uniform(200, H), rng.uniform(160, 420)
        c.drawCircle(x, y, r, paint((210, 206, 196) if k % 2 else (255, 252, 246), 0.18, blur=r * 0.4))
    net = _salt_net(round(112 * z, 1))
    c.save()
    c.translate(540, 900)
    c.translate(3, 3)
    c.drawPath(net, paint((150, 150, 170), 0.5, stroke=5 * z + 1, blur=1.5))
    c.translate(-4, -4)
    c.drawPath(net, paint(WHITE, 0.85, stroke=2.2 * z + 0.6))
    c.restore()


def s_e_salt(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("e_salt")
    zm = 1.0 - 0.12 * ramp(T, t0, end("e_salt"))
    c.save()
    c.translate(540, 900)
    c.scale(zm, zm)
    c.translate(-540, -900)
    _salt_top(c, T)
    _web(c, T)
    c.restore()
    return st.arr


def _curator_whole(c, T, t0, t1):
    """'That's power.': the hand belongs to her - the whole figure, symmetrical in her red hall, eyes shut, every
    thread hanging from her gold claws down into the dark below."""
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(shader=K.rad((540, 700), 1200, [(130, 8, 24), (54, 0, 10), (8, 0, 2)])))
    c.drawRect(skia.Rect.MakeLTRB(0, 1420, W, H), paint(shader=K.lin((0, 1420), (0, H), [(40, 0, 8), (12, 0, 2)])))
    G.pool(c, 540, 1500, 700, (255, 60, 70), 0.18, squash=0.3)
    zoom(c, T, t0, t1 + 0.6, 1.0, 1.07, 540, 900)
    rec = skia.PictureRecorder()
    pc = rec.beginRecording(skia.Rect.MakeWH(W, H))
    tips = C.curator(pc, 540, 1560, 0.8, T, eyes=0.0, open_=0.25, arms="open")
    pic = rec.finishRecordingAsPicture()
    for i, (tx, ty) in enumerate(tips):                                  # the threads, swaying, down out of frame
        sw = 14 * math.sin(T * 1.3 + i)
        c.drawPath(K.bez_path([(tx, ty), (tx + sw, (ty + H) / 2), (tx + sw * 0.5 + (i - 4) * 6, H + 40)]), paint(C.GOLD_HI, 0.85, stroke=2.2))
    c.drawPicture(pic)
    c.restore()


def s_e_hand(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0, t1 = cut("e_hand"), end("e_hand")
    tw = Wx("e7", "That's") - 0.12
    if T >= tw:
        _curator_whole(c, T, tw, t1)
        return st.arr
    u = ramp(T, t0, t1)
    _salt_top(c, T, z=0.7)
    pts, me = _web(c, T, k_all=1, scale=0.62, cy=1150, a=1.0)
    c.drawPaint(paint((70, 0, 8), 0.3 + 0.4 * u))
    hx, hy = 540, -40 + 100 * K.ease(u)
    tight = K.ease(ramp(T, Wx("e7", "power") - 0.1, Wx("e7", "power") + 0.3))
    # the hand first (to learn where its gold tips are), then the threads drawn from those tips down to the web
    rec = skia.PictureRecorder()
    pc = rec.beginRecording(skia.Rect.MakeWH(W, H))
    tips = C.hand(pc, hx, hy, 3.2, 0, T, open_=1.0 - 0.6 * tight)
    pic = rec.finishRecordingAsPicture()
    for i, (px, py, k, _) in enumerate(pts + [(me[0], me[1], 1, "")]):
        tx, ty = tips[i % 4]
        mx, my = (tx + px) / 2, (ty + py) / 2 + 80 * (1 - tight)
        c.drawPath(K.bez_path([(tx, ty), (mx, my), (px, py)]), paint(C.GOLD_HI, 0.9, stroke=2.5))
    c.drawPicture(pic)
    return st.arr


def _curator_face(c, T, eyes, open_, swivel=0.0, stut=None, talk_k=0.0, hot=0.0, z=1.0):
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(shader=K.rad((540, 760), 1100, [(120, 6, 20), (50, 0, 8), (8, 0, 2)])))
    c.save()
    c.translate(540, 900)
    c.scale(z, z)
    c.translate(-540, -900)
    C.lens_fan(c, 540, 820, 1.7, T, open_=open_, swivel=swivel, stutter=stut, hot=hot)
    c.drawPath(K.smooth([(280, 1400), (300, 560), (380, 380), (540, 330), (700, 380), (780, 560), (800, 1400)]), paint(C.LACQUER))
    for sd in (-1, 1):                                              # ribbed tubes from behind her jaw into the black shells below
        C.ribbed(c, [(540 + sd * 150, 1080), (540 + sd * 250, 1230), (540 + sd * 360, 1420), (540 + sd * 420, 1700)], 30, 22, T=T, pulse=0.6)
        C.shell(c, 540 + sd * 360, 1560, 150, 90, ang=sd * 20, rim_k=1.0)
    for i in range(5):
        yy = 1330 + i * 40
        c.drawPath(K.rrect(400 - i * 10, yy, 680 + i * 10, yy + 30, 12), paint(shader=C.gold_shader((400, yy), (680, yy + 30))))
    C.mask(c, 540, 880, 2.2, T, eyes=eyes, iris="lens", open_=open_, talk=talk_k, lips=(140, 0, 20), tint=(222, 214, 208),
           shadow=(110, 100, 130))
    c.restore()


def s_e_hush(T, idx):
    st = K.Stage((0, 0, 0))
    _curator_face(st.c, T, eyes=0.0, open_=0.2, z=1.0)
    return st.arr


def s_e_eyes(T, idx):
    st = K.Stage((0, 0, 0))
    c = st.c
    t0 = cut("e_eyes")
    u = T - t0
    op = 0.1 + 0.7 * K.ease(ramp(u, 0.05, 0.5))
    sw = K.ease(ramp(stutter(T, t0 + 0.2, period=0.3, move=0.06, fps=12, seed=5), t0 + 0.2, t0 + 1.0))
    if u < 0.1:
        shake(c, T, 18 * (1 - u / 0.1), seed=3)
    else:
        c.save()
    _curator_face(c, T, eyes=1.0, open_=op, swivel=0.0, stut=T if u < 1.0 else None, talk_k=talk(T, "CURATOR"), hot=sw,
                  z=1.0 + 0.06 * ramp(u, 0, 2.5))
    c.restore()
    return st.arr

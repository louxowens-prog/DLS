"""Cold open and tale one: the cover and its hook, Nora and the host at the window, the skills handed over, the old
examples; then THE ROAD THAT FORGOT HER."""
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


def cut_t(name):
    from edit import EDIT
    return next(e[0] for e in EDIT if e[1] == name)


# ------------------------------------------------------------------ the comic's cover

def cover(c, T, art=None, banner=1.0):
    """The cover of USE IT OR LOSE IT! - masthead, issue box, the host's roundel, the cover art, the banner."""
    CO.page_bg(c, (236, 222, 186), ghosts=False)
    c.drawRect(skia.Rect.MakeLTRB(30, 236, 1050, 640), paint((180, 14, 24)))
    c.drawRect(skia.Rect.MakeLTRB(30, 236, 1050, 640), paint(INK, stroke=10))
    rng = K.rng_at(2, 2)
    for i in range(40):                                                 # a halftone wash on the masthead
        c.drawCircle(rng.uniform(40, 1040), rng.uniform(246, 630), rng.uniform(6, 16), paint((120, 0, 10), 0.4))
    CO.drip_title(c, "USE IT", 470, 396, 150, color=(250, 230, 40), seed=1, tag="title")
    CO.drip_title(c, "OR LOSE IT!", 540, 540, 136, color=(130, 255, 70), seed=2, tag="title", drip=0.7)
    c.drawRect(skia.Rect.MakeLTRB(30, 640, 1050, 712), paint(INK))
    CO.label(c, "TALES OF THE OUTSOURCED MIND", 540, 694, 52, "bangers-400", (250, 244, 228), tag="title")
    c.drawRect(skia.Rect.MakeLTRB(60, 262, 196, 380), paint((250, 244, 228)))
    c.drawRect(skia.Rect.MakeLTRB(60, 262, 196, 380), paint(INK, stroke=5))
    CO.label(c, "No.1", 128, 312, 40, "bangers-400", INK, tag="title")
    CO.label(c, "35c", 128, 364, 40, "bangers-400", (180, 14, 24), tag="title")
    C.roundel_host(c, T, 905, 330, 84, expr="sly")
    # the art
    x0, y0, x1, y1 = 30, 712, 1050, 1700
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x0, y0, x1, y1))
    if art is not None:
        art(c, x0, y0, x1, y1)
    c.restore()
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(INK, stroke=10))
    # the banner across the corner (slammed on once the camera has pulled back)
    if banner <= 0.01:
        return
    c.save()
    c.translate(720, 1250)
    c.rotate(-8)
    c.scale(banner, banner)
    c.drawRect(skia.Rect.MakeLTRB(-330, -48, 330, 48), paint((250, 220, 40)))
    c.drawRect(skia.Rect.MakeLTRB(-330, -48, 330, 48), paint(INK, stroke=6))
    CO.label(c, "BASED ON A TRUE STUDY!", 0, 18, 50, "bangers-400", (180, 14, 24), tag="title")
    c.restore()


def cover_art(T):
    """The cover painting: a doctor screaming at a monitor where a growth grins back."""
    def draw(c, x0, y0, x1, y1):
        CO.shock(c, "green", T, cx=540, cy=980, seed=3, rays=30, bolts=0)
        PR.monitor(c, 760, 960, 0.78, T, lambda cc, a, b, cc2, d: (PR.tunnel(cc, a, b, cc2, d, T),
                                                                  PR.growth(cc, 10, 20, 70, T, eye=1.0, grin=1.0)), light="green")
        FA.bust(c, "hale", 330, 1010, 1.35, T, expr="scream", light="green", gaze=(0.6 * math.sin(T * 7), -0.2), turn=0.25, shake=4,
                talk=0.3 + 0.3 * math.sin(T * 13))
        FA.hand(c, 110, 1180, 1.25, -60, skin=FA.CAST["hale"]["skin"], light="green", pose="open")
    return draw


def s_o_cover(T, idx):
    """Lightning, and we are nose to nose with the screaming doctor on the cover; the camera pulls back to the comic."""
    st = K.Stage()
    c = st.c
    k = ease(ramp(T, 0.25, 1.5))
    z = K.lerp(2.6, 1.0, k) * (1 + 0.04 * ramp(T, 1.5, 2.7))
    cx, cy = K.lerp(330, 540, k), K.lerp(990, 870, k)
    c.save()
    c.translate(540, 860)
    c.scale(z, z)
    c.translate(-cx, -cy)
    n0 = len(K.TEXT)
    cover(c, T, cover_art(T), banner=K.pop(T, 1.55, 0.2, 0.3))
    c.restore()
    keep = [b for b in K.TEXT[n0:] if b[2] > 0 and b[0] < W and b[3] > 0 and b[1] < H and z < 1.1]
    K.TEXT[n0:] = keep                                                   # lettering the camera is too close to read
    return st.arr


# ------------------------------------------------------------------ the hook comes alive

def scope_screen(T, box=1.0, eye=0.0, grin=0.0, hide=0.0):
    def draw(c, x0, y0, x1, y1):
        cx, cy = PR.tunnel(c, x0, y0, x1, y1, T)
        gx, gy = cx - 90 + 40 * hide, cy + 20 + 30 * hide
        c.save()
        if hide > 0:
            c.clipRect(skia.Rect.MakeLTRB(x0, y0, x1, gy + 50 - 120 * hide))
        PR.growth(c, gx, gy, 46, T, eye=eye, grin=grin)
        c.restore()
        PR.detect_box(c, gx, gy, 46, T, a=box)
    return draw


def s_o_scope(T, idx):
    """Three months with an AI: the spotter boxes the growth; the doctor relaxes with her coffee."""
    st = K.Stage((30, 60, 66))
    c = st.c
    SE.clinic(c, T)
    C.push(c, T, S("c1"), E("c1"), 1.0, 1.06, cx=600, cy=800)
    PR.monitor(c, 690, 760, 0.95, T, scope_screen(T, box=1.0), light="clinic")
    PR.eyebox(c, 690, 420, 0.7, T, on=1.0, look=(0.3 * math.sin(T * 1.5), 0.5))
    FA.bust(c, "hale", 300, 1040, 1.3, T, expr="smile", light="clinic", talk=0.0, blink=C.blink(T, 4), gaze=(0.8, -0.3), turn=0.35)
    # coffee mug
    c.drawRoundRect(skia.Rect.MakeLTRB(80, 1220, 200, 1360), 14, 14, paint((200, 60, 40)))
    c.drawCircle(210, 1290, 34, paint((200, 60, 40), stroke=14))
    for i in range(3):
        c.drawPath(K.bez_path([(110 + i * 30, 1210), (100 + i * 30 + 10 * math.sin(T * 3 + i), 1160), (116 + i * 30, 1110)]), paint(WHITE, 0.25, stroke=5))
    c.restore()
    return st.arr


def s_o_noai(T, idx):
    """...without it: the box goes dark, the green square goes, and the growth opens an eye and slips away."""
    st = K.Stage((30, 60, 66))
    c = st.c
    t_off = Wx("c1", "working") + 0.25
    on = 0.0 if T > t_off else 1.0
    SE.clinic(c, T, power=1.0)
    C.push(c, T, Wx("c1", "working") - 0.1, E("c1"), 1.12, 1.3, cx=640, cy=760)
    eye = ease(ramp(T, t_off + 0.35, t_off + 0.6))
    grin = ease(ramp(T, t_off + 0.6, t_off + 0.9))
    hide = ease(ramp(T, t_off + 1.1, t_off + 1.6))
    PR.monitor(c, 690, 760, 0.95, T, scope_screen(T, box=on, eye=eye, grin=grin, hide=hide), light="clinic")
    PR.eyebox(c, 690, 420, 0.7, T, on=on, look=(0.0, 0.5))
    c.restore()
    FA.bust(c, "hale", 230, 1180, 1.5, T, expr="squint" if T < t_off + 1.0 else "fear", light="screen", blink=0.0, gaze=(0.9, -0.5), turn=0.4)
    if T > t_off and T < t_off + 0.5:
        CO.sfx(c, "CLICK", 820, 300, 90, k=K.pop(T, t_off, 0.15, 0.3), rot=8, fill=(240, 240, 240), fill2=(170, 170, 180))
    return st.arr


def s_o_noai_shock(T, idx):
    st = K.Stage()
    c = st.c
    t0 = Wx("c1", "fewer") - 0.05
    CO.shock(c, "green", T, cx=540, cy=760, seed=5)
    C.push(c, T, t0, t0 + 0.8, 1.0, 1.25, cx=540, cy=820)
    FA.bust(c, "hale", 540, 820, 2.3, T, expr="scream", light="green", shake=5, gaze=(0.0, -0.2))
    c.restore()
    PR.growth(c, 880, 330, 60, T, eye=1.0, grin=1.0)
    return st.arr


# ------------------------------------------------------------------ the reader on a stormy night

def comic_in_hands(c, x, y, s, ang, T, light="lamp"):
    """Nora's copy of the comic, held open-ish in two hands (the cover toward us)."""
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    c.drawRect(skia.Rect.MakeLTRB(-170, -240, 190, 260), paint(INK, 0.5, blur=12))
    with C.sub((236, 222, 186)) as sub:
        cover(sub.c, T, cover_art(T))
    c.drawImageRect(K.image(sub.arr), skia.Rect.MakeLTRB(0, 200, W, 1720), skia.Rect.MakeLTRB(-180, -250, 180, 250),
                    skia.SamplingOptions(skia.FilterMode.kLinear))
    c.drawRect(skia.Rect.MakeLTRB(-180, -250, 180, 250), paint(INK, 0.5, stroke=3))
    c.restore()


def s_o_window(T, idx):
    """Ahahaha! Lightning: Aunt Atrophy at the window behind Nora, who reads on."""
    st = K.Stage()
    c = st.c
    fl = C.hit(T, S("c2a") - 0.04, 0.5)
    SE.apartment(c, T, flash=fl)
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(533, 173, 987, 887))
    k = ease(ramp(T, S("c2a") - 0.05, S("c2a") + 0.25))
    FA.bust(c, "host", 760, 440 + (1 - k) * 300, 1.2, T, expr="cackle", light="green", talk=C.talk(T, "HOST"))
    CO.rain(c, T, 533, 173, 987, 887, n=40, a=0.4, ang=0.05, speed=900, length=40, seed=9)
    c.restore()
    c.drawRect(skia.Rect.MakeLTRB(520, 160, 1000, 900), paint((30, 18, 16), stroke=26))
    c.drawLine(760, 160, 760, 900, paint((30, 18, 16), stroke=18))
    c.drawLine(520, 530, 1000, 530, paint((30, 18, 16), stroke=18))
    C.person(c, "nora", 330, 1030, 1.2, T, expr="neutral", light="lamp", gaze=(0.2, 0.8), seed=2, tilt=6)
    comic_in_hands(c, 360, 1330, 0.62, -6, T)
    FA.hand(c, 220, 1330, 1.0, -70, skin=FA.CAST["nora"]["skin"], pose="grip")
    FA.hand(c, 500, 1330, 1.0, -110, skin=FA.CAST["nora"]["skin"], pose="grip", flip=True)
    return st.arr


def s_o_host(T, idx):
    """Welcome, my little vegetables: the host close at the glass, rain running; the title drips on to the pane."""
    st = K.Stage((10, 20, 30))
    c = st.c
    SE.grad_bg(c, (20, 30, 60), (6, 8, 18))
    C.push(c, T, S("c2"), E("c2") + 0.4, 1.0, 1.12, cx=540, cy=760)
    expr = "sly"
    FA.bust(c, "host", 540, 800, 2.0, T, expr=expr, light="green", talk=C.talk(T, "HOST"), blink=C.blink(T, 5), gaze=(0.0, 0.1))
    c.restore()
    CO.rain(c, T, 0, 0, W, H, n=70, a=0.4, ang=0.04, speed=700, length=50, seed=3)
    rng = K.rng_at(6, 6)
    for i in range(40):
        dx, dy = rng.uniform(0, W), (rng.uniform(0, H) + T * rng.uniform(30, 120)) % H
        c.drawPath(K.capsule(dx, dy - rng.uniform(10, 40), dx, dy, 4, 6), paint((190, 210, 255), 0.35))
    c.drawRect(skia.Rect.MakeWH(W, H), paint((30, 18, 16), stroke=60))
    t1 = Wx("c2", "Atrophy") + 0.2
    if T > t1:
        CO.drip_title(c, "USE IT OR LOSE IT!", 540, 330, 104, color=(130, 255, 70), seed=4, k=K.pop(T, t1, 0.25, 0.3), drip=0.5 + ramp(T, t1, t1 + 1.5))
    return st.arr


def s_o_muse(T, idx):
    """The assistant on the coffee table: Shall I read it for you?"""
    st = K.Stage()
    c = st.c
    SE.apartment(c, T)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0), 0.35))
    table = path([(-100, 1000), (1180, 1000), (1180, H), (-100, H)])
    FA.lit_fill(c, table, (90, 50, 30), FA.Light("lamp"), rim=0.6)
    for i in range(6):
        c.drawLine(-100, 1040 + i * 90, 1180, 1050 + i * 90, paint((60, 30, 18), 0.6, stroke=4))
    lvl = C.talk(T, "MUSE")
    SE.glow(c, 700, 950, 360, (90, 180, 255), 0.25 + 0.2 * lvl)
    PR.phone(c, 700, 900, 1.15, 8, T, screen="muse", level=lvl)
    comic_in_hands(c, 250, 1120, 0.7, -14, T)
    FA.hand(c, 110, 1170, 1.1, -60, skin=FA.CAST["nora"]["skin"], pose="grip")
    return st.arr


def s_o_nora(T, idx):
    """Just summarize it: Nora, bored, tosses the comic aside."""
    st = K.Stage()
    c = st.c
    SE.apartment(c, T)
    C.push(c, T, S("c4") - 0.1, E("c4") + 0.3, 1.0, 1.05, cx=560, cy=900)
    C.person(c, "nora", 560, 900, 1.65, T, expr="smug", light="lamp", gaze=(-0.5, 0.3), seed=2, turn=-0.15)
    c.restore()
    k = ease(ramp(T, Wx("c4", "summarize"), Wx("c4", "summarize") + 0.5))
    comic_in_hands(c, 300 - 380 * k, 1350 + 200 * k, 0.6, -10 - 60 * k, T)
    return st.arr


# ------------------------------------------------------------------ the skills, handed over

SKILLS = [("WRITE", "c5", "Write"), ("NAVIGATE", "c5", "Navigate"), ("REMEMBER", "c5", "Remember"), ("DECIDE", "c5", "Decide")]


def skill_art(c, i, x0, y0, x1, y1, T, lost=0.0):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 20
    L = FA.Light("lamp")
    if i == 0:                                                          # a hand writing a line
        c.drawRect(skia.Rect.MakeLTRB(x0 + 40, y0 + 120, x1 - 40, y1 - 40), paint((250, 246, 230)))
        for k in range(5):
            c.drawLine(x0 + 60, y0 + 170 + k * 50, x1 - 60, y0 + 170 + k * 50, paint((150, 180, 220), 0.6, stroke=2))
        prog = ramp(T, Wx("c5", "Write"), Wx("c5", "Write") + 1.2) * (1 - lost)
        pts = [(x0 + 70 + k * 6, y0 + 210 + 14 * math.sin(k * 0.7)) for k in range(int(55 * prog) + 2)]
        c.drawPath(path(pts, closed=False), paint((30, 40, 120), stroke=4))
        px, py = pts[-1]
        c.drawPath(K.capsule(px, py, px + 120, py - 150, 14, 18), paint((200, 30, 30)))
        FA.hand(c, px + 60, py - 40, 0.9, -60, skin=FA.CAST["kit"]["skin"], light=L, pose="grip")
    elif i == 1:                                                        # a folded map with a dotted route
        for k in range(4):
            c.drawRect(skia.Rect.MakeLTRB(x0 + 40 + k * 100, y0 + 120, x0 + 140 + k * 100, y1 - 40), paint((236, 226, 180) if k % 2 else (220, 210, 166)))
        for k in range(6):
            c.drawLine(x0 + 40, y0 + 150 + k * 60, x1 - 40, y0 + 130 + k * 66, paint((200, 120, 80), 0.8, stroke=5))
        p = K.bez_path([(x0 + 70, y1 - 70), (cx, y0 + 140), (x1 - 70, y0 + 180)])
        q = paint((200, 20, 20), 1 - lost, stroke=7)
        q.setPathEffect(skia.DashPathEffect.Make([14, 12], 0))
        c.drawPath(p, q)
        c.drawCircle(x1 - 70, y0 + 180, 16, paint((200, 20, 20), 1 - lost))
    elif i == 2:                                                        # a face and the number you knew by heart
        FA.bust(c, "nora", cx - 60, cy + 40, 0.55, T, expr="smile", light="lamp", body=True)
        c.drawRect(skia.Rect.MakeLTRB(cx + 20, y0 + 130, x1 - 30, y0 + 250), paint((250, 246, 200)))
        f = K.font("special-elite-400", 34)
        num = "555-0142" if lost < 0.5 else "???-????"
        c.drawString(num, cx + 34, y0 + 204, f, paint(INK))
        K.reg_local(c, cx + 34, y0 + 176, cx + 34 + f.measureText(num), y0 + 212, "deco")
    else:                                                               # a fork in the road
        c.drawPath(path([(cx - 40, y1), (cx + 40, y1), (cx + 20, cy + 40), (x1 - 40, y0 + 140), (x1 - 100, y0 + 140), (cx, cy),
                         (x0 + 100, y0 + 140), (x0 + 40, y0 + 140), (cx - 20, cy + 40)]), paint((90, 80, 70)))
        SE.signpost(c, cx, y1 - 30, 0.42, T, L="lamp")


def s_o_skills(T, idx):
    st = C.page(seed=3)
    c = st.c
    rects = [(50, 250, 525, 740), (555, 250, 1030, 740), (50, 770, 525, 1260), (555, 770, 1030, 1260)]
    t_hand = Wx("c5", "Hand")
    t_lose = Wx("c5", "lose")
    lost = ease(ramp(T, t_lose - 0.3, t_lose + 0.5))
    for i, ((x0, y0, x1, y1), (name, key, word)) in enumerate(zip(rects, SKILLS)):
        on = ramp(T, Wx(key, word) - 0.05, Wx(key, word) + 0.15)
        sub = C.sub((250, 240, 210) if on > 0 else (200, 196, 186)).__enter__()
        sc = sub.c
        sc.translate(-x0, -y0)
        sk = 1 - 0.85 * ease(ramp(T, t_hand + 0.2 * i, t_hand + 0.2 * i + 0.6))     # sucked into the phone
        if sk > 0.05:
            sc.save()
            ph = (540, 1200)
            sc.translate((x0 + x1) / 2 * sk + ph[0] * (1 - sk), (y0 + y1) / 2 * sk + ph[1] * (1 - sk))
            sc.scale(sk, sk)
            sc.translate(-(x0 + x1) / 2, -(y0 + y1) / 2)
            skill_art(sc, i, x0, y0, x1, y1, T, lost)
            sc.restore()
        if lost > 0:
            sc.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint((120, 120, 120), 0.6 * lost))
            CO.cobweb(sc, x0, y0, 220 * lost, 0, 90, a=0.8 * lost, seed=i, color=(240, 240, 240))
            CO.cobweb(sc, x1, y1, 160 * lost, 180, 90, a=0.8 * lost, seed=i + 5, color=(240, 240, 240))
        sub.__exit__()
        arr = sub.arr
        if on < 1:
            g = arr[..., :3].astype(np.float32).mean(axis=2, keepdims=True)
            arr[..., :3] = (arr[..., :3] * on + g * (1 - on) * 0.8).astype(np.uint8)
        CO.panel(c, arr[: y1 - y0, : x1 - x0], x0, y0, x1, y1, border=12)
        if on > 0:
            CO.sfx(c, name, (x0 + x1) / 2, y0 + 70, 70, k=K.pop(T, Wx(key, word) - 0.05, 0.2, 0.3), rot=-4,
                   fill=(255, 226, 0) if lost < 0.5 else (170, 170, 170), fill2=(255, 120, 0) if lost < 0.5 else (110, 110, 110), tag="label")
        if lost > 0.5:
            c.drawLine(x0 + 60, y0 + 70, x1 - 60, y0 + 40, paint((200, 0, 0), 0.9, stroke=10))
    if T > t_hand - 0.1:                                                # the phone that swallows them
        k = ease(ramp(T, t_hand - 0.1, t_hand + 0.3))
        SE.glow(c, 540, 1220, 300, (90, 180, 255), 0.4 * k)
        PR.phone(c, 540, 1110, 0.75 * K.pop(T, t_hand - 0.1, 0.25, 0.3), 0, T, screen="muse", level=0.5)
    more = ["CALCULATE", "RESEARCH", "CODE", "PLAN", "TRANSLATE", "SUMMARIZE"]
    for j, w in enumerate(more):                                        # and the rest of what we hand over, drifting in
        tj = Wx("c5", "Decide") + 0.12 * j
        if T < tj:
            continue
        u = ease(ramp(T, t_hand + 0.1 * j, t_hand + 0.1 * j + 0.7))
        x0, y0 = (150 + (j % 3) * 390), (330 + (j // 3) * 860)
        x, y = K.lerp(x0, 540, u), K.lerp(y0, 1110, u)
        CO.label(c, w, x, y, 44 * (1 - 0.7 * u), "bangers-400", (250, 240, 220), tag="deco", outline=INK, ow=8, rot=(-8, 6, -4)[j % 3],
                 a=min(1.0, (T - tj) * 6) * (1 - u))
    C.roundel_host(c, T, 540, 755, 120, expr="sly" if T < t_lose else "cackle")
    return st.arr


# ------------------------------------------------------------------ it happened before

def s_o_before(T, idx):
    st = C.page(seed=5)
    c = st.c
    rows = [(350, 650, "c6", "calculators", "SUMS"), (670, 970, "c6", "GPS", "ROUTES"), (990, 1290, "c6", "routes", "SPELLING")]
    CO.drip_title(c, "IT HAPPENED BEFORE...", 540, 300, 74, color=(200, 20, 30), seed=7, k=K.pop(T, cut_t("o_before") + 0.05, 0.25, 0.2),
                  drip=0.4, tag="title")
    for i, (y0, y1, key, word, name) in enumerate(rows):
        t0 = Wx(key, word) - 0.12 if i else cut_t("o_before") + 0.25
        if T < t0:
            continue
        k = K.pop(T, t0, 0.22, 0.12)
        sub = C.sub((240, 230, 200)).__enter__()
        sc = sub.c
        if i == 0:
            SE.grad_bg(sc, (60, 40, 50), (30, 20, 30))
            PR.calculator(sc, 640, 160, 0.66, T, display="28" if T > Wx("c6", "calculators") + 0.5 else "4x7", ang=-8)
            FA.hand(sc, 400, 300, 1.0, -30, skin=FA.CAST["nora"]["skin"], pose="point")
        elif i == 1:
            SE.grad_bg(sc, (20, 40, 60), (10, 14, 24))
            PR.gps(sc, 620, 170, 0.75, T, mode="route")
            FA.hand(sc, 330, 260, 1.0, -20, skin=FA.CAST["vera"]["skin"], pose="open")
        else:
            SE.grad_bg(sc, (240, 236, 220), (210, 206, 190))
            f = K.font("special-elite-400", 60)
            sc.drawString("definately", 300, 150, f, paint((40, 40, 50)))
            q = paint((230, 20, 20), stroke=4)
            q.setPathEffect(skia.DashPathEffect.Make([10, 6], 0))
            sc.drawLine(300, 166, 300 + f.measureText("definately"), 166, q)
            sc.drawRoundRect(skia.Rect.MakeLTRB(330, 190, 700, 270), 10, 10, paint((40, 90, 200)))
            sc.drawString("definitely", 350, 250, f, paint(WHITE))
            K.reg_local(sc, 300, 100, 720, 270, "deco")
        sub.__exit__()
        CO.panel(c, sub.arr[: y1 - y0, : 960], 60, y0, 1020, y1, border=12, rot=(-1.2, 0.8, -0.6)[i], a=min(1.0, k))
        if T > Wx("c6", "routes") + 0.4:                                 # the old losses, stamped
            CO.label(c, "TAKEN", 860, y0 + 80, 50, "bangers-400", (200, 20, 30), rot=12, tag="label", a=min(1.0, (T - Wx("c6", "routes") - 0.4) * 4))
        CO.sfx(c, name, 210, y0 + 70, 62, k=k, rot=-6, tag="label")
    return st.arr


def s_o_more(T, idx):
    """AI can take far more: blue shock, the one red eye fills the frame."""
    st = K.Stage()
    c = st.c
    t0 = Wx("c6", "AI") - 0.08
    CO.shock(c, "blue", T, cx=540, cy=760, seed=8, rays=36)
    C.push(c, T, t0, E("c6") + 0.5, 1.0, 1.35, cx=540, cy=760)
    PR.eyebox(c, 560, 760, 2.4, T, on=1.0, look=(math.sin(T * 2.3) * 0.8, 0.2 * math.sin(T * 1.7)), light="blue", label="")
    c.restore()
    for i, (x, y, name) in enumerate(((180, 420, "WRITE"), (860, 470, "REMEMBER"), (200, 1150, "DECIDE"), (860, 1120, "NAVIGATE"))):
        k = ease(ramp(T, t0 + 0.2 * i, t0 + 0.2 * i + 0.6))
        x2, y2 = x + (540 - x) * k, y + (760 - y) * k
        CO.label(c, name, x2, y2, 56 * (1 - 0.7 * k), "bangers-400", WHITE, tag="deco", outline=INK, ow=8, a=1 - k)
    return st.arr


# ------------------------------------------------------------------ tale one

def tale_title(c, T, t0, lines, art, colr=(250, 40, 40), seed=0):
    """A tale's splash page: the art as one big panel, the title in dripping letters, the host's roundel."""
    CO.page_bg(c, (236, 222, 186), ghosts=False)
    with C.sub((0, 0, 0)) as sub:
        art(sub.c, T)
    CO.panel(c, sub.arr, 40, 250, 1040, 1290, border=14)
    c.drawRect(skia.Rect.MakeLTRB(40, 250, 1040, 590), paint(shader=K.lin((0, 250), (0, 590), [(0, 0, 0, 0.75), (0, 0, 0, 0.0)])))
    for i, ln in enumerate(lines):
        CO.drip_title(c, ln, 540, 380 + i * 128, 116, color=colr, seed=seed + i, k=K.pop(T, t0 + 0.15 * i, 0.25, 0.3), drip=0.3 + 0.15 * ramp(T, t0, t0 + 2))
    C.roundel_host(c, T, 170, 1140, 100, expr="cackle" if C.talk(T, "HOST") > 0.05 else "sly")


def road_art(c, T):
    SE.swamp(c, T, fog_a=0.7)
    SE.signpost(c, 720, 1180, 0.9, T, L="green")
    for sx in (480, 540):                                               # tail lights vanishing into the fog
        SE.glow(c, sx, 1080, 40, (255, 30, 20), 0.8)
        c.drawCircle(sx, 1080, 8, paint((255, 60, 40)))
    CO.fog(c, T, 1000, 1250, color=(170, 200, 180), a=0.5, seed=12, n=6)


def s_v_title(T, idx):
    st = K.Stage()
    tale_title(st.c, T, S("v1") - 0.4, ["THE ROAD THAT", "FORGOT HER"], road_art, colr=(250, 60, 40), seed=10)
    return st.arr


def s_v_car(T, idx, freeze=None):
    """Vera drives by the voice in the dash, putting on her lipstick, eyes off the road."""
    st = K.Stage()
    c = st.c
    SE.car_interior(c, T)
    lvl = C.talk(T, "MUSE")
    PR.gps(c, 820, 1090, 1.0, T, mode="route")
    SE.glow(c, 820, 1090, 260, (90, 200, 255), 0.2 + 0.25 * lvl)
    looking = "smug" if C.talk(T, "VERA") < 0.05 else "smile"
    C.person(c, "vera", 360, 840, 1.45, T, expr=looking, light="dash", gaze=(-0.7, -0.4), turn=-0.2, seed=6, tilt=-4)
    # the lipstick at her lips, the mirror she looks into
    lip = 0.5 + 0.5 * math.sin(T * 2.4)
    FA.hand(c, 470, 1040 + 10 * lip, 1.05, -150, skin=FA.CAST["vera"]["skin"], light="dash", pose="grip", nails=(200, 10, 40), flip=True)
    c.drawRoundRect(skia.Rect.MakeLTRB(520, 960 + 10 * lip, 560, 1010 + 10 * lip), 6, 6, paint((200, 170, 60)))
    c.drawRoundRect(skia.Rect.MakeLTRB(524, 930 + 10 * lip, 556, 962 + 10 * lip), 10, 10, paint((210, 10, 40)))
    c.drawRoundRect(skia.Rect.MakeLTRB(140, 150, 460, 240), 20, 20, paint((20, 20, 24)))
    c.drawRoundRect(skia.Rect.MakeLTRB(150, 160, 450, 230), 16, 16, paint((60, 70, 90)))
    PR.wheel(c, 300, 1500, 1.15, ang=5 * math.sin(T * 0.8))
    FA.hand(c, 140, 1290, 1.1, -40, skin=FA.CAST["vera"]["skin"], light="dash", pose="grip", nails=(200, 10, 40))
    return st.arr


def s_v_map(T, idx):
    """The live frame freezes into a panel; below it, the map in her head erasing street by street."""
    t0 = S("v4") - 0.1
    fr = C.inked(s_v_car, t0 - 0.05, idx, k=ease(ramp(T, t0, t0 + 0.25)))
    st = K.Stage()
    c = st.c
    k = ease(ramp(T, t0 + 0.15, t0 + 0.55))
    CO.page_bg(c, CO.NEWS, seed=7)
    x0, y0, x1, y1 = K.lerp(-30, 50, k), K.lerp(-30, 250, k), K.lerp(W + 30, 1030, k), K.lerp(H + 30, 760, k)
    CO.panel(c, fr, x0, y0, x1, y1, border=K.lerp(0, 12, k), rot=-1.2 * k)
    if k > 0.6:
        a = ease(ramp(T, t0 + 0.4, t0 + 0.7))
        sub = C.sub((236, 226, 196)).__enter__()
        sc = sub.c
        # the map, inside the outline of her head
        head = K.smooth([(330, 60), (520, 40), (680, 120), (720, 300), (690, 420), (600, 470), (420, 480), (300, 380), (280, 200)])
        sc.save()
        sc.clipPath(head, doAntiAlias=True)
        sc.drawRect(skia.Rect.MakeLTRB(0, 0, 1000, 600), paint((250, 240, 200)))
        erase = ramp(T, Wx("v4", "worse"), Wx("v4", "years") + 0.3)
        rng = K.rng_at(3, 3)
        for i in range(14):
            yy = 70 + i * 30
            if rng.random() > erase:
                sc.drawLine(260, yy, 740, yy + rng.uniform(-20, 20), paint((200, 80, 60), stroke=6))
            xx = 280 + i * 34
            if rng.random() > erase:
                sc.drawLine(xx, 40, xx + rng.uniform(-30, 30), 500, paint((90, 110, 160), stroke=5))
        sc.restore()
        sc.drawPath(head, paint(INK, stroke=8))
        if 0.0 < erase < 1.0:                                           # a pink eraser scrubbing the streets away
            u = erase
            ex = 300 + 380 * (0.5 + 0.5 * math.sin(T * 7.0))
            ey = 90 + 340 * u + 30 * math.sin(T * 11)
            sc.save()
            sc.translate(ex, ey)
            sc.rotate(-25 + 10 * math.sin(T * 7))
            sc.drawRoundRect(skia.Rect.MakeLTRB(-70, -36, 70, 36), 10, 10, paint((236, 140, 150)))
            sc.drawRoundRect(skia.Rect.MakeLTRB(-70, -36, -20, 36), 10, 10, paint((70, 90, 160)))
            sc.drawRoundRect(skia.Rect.MakeLTRB(-70, -36, 70, 36), 10, 10, paint(INK, stroke=5))
            sc.restore()
            for j in range(10):
                sc.drawCircle(ex + rng.uniform(-90, 90), ey + rng.uniform(30, 70), rng.uniform(3, 6), paint((220, 130, 140), 0.8))
        if T > Wx("v4", "three") - 0.1:
            sc.drawRect(skia.Rect.MakeLTRB(780, 100, 960, 300), paint(WHITE))
            sc.drawRect(skia.Rect.MakeLTRB(780, 100, 960, 300), paint(INK, stroke=6))
            sc.drawRect(skia.Rect.MakeLTRB(780, 100, 960, 150), paint((200, 20, 20)))
            yr = 1 + min(2, int((T - Wx("v4", "three") + 0.1) / 0.25))
            CO.label(sc, f"YEAR {yr}", 870, 250, 50, "bangers-400", INK, tag="deco")
        sub.__exit__()
        CO.panel(c, sub.arr[:470, :980], 50, 800, 1030, 1270, border=12, rot=0.8, a=a)
        CO.label(c, "SPATIAL MEMORY", 330, 880, 46, "bangers-400", (200, 20, 20), tag="label", a=a)
        if a > 0.5:
            dk = ramp(T, Wx("v4", "worse"), Wx("v4", "years") + 0.3)
            c.drawPath(path([(110, 940), (130, 940 + 160 * dk), (150, 940)], closed=False), paint((200, 20, 20), stroke=10))
            c.drawPath(path([(100, 930 + 160 * dk), (130, 970 + 160 * dk), (160, 930 + 160 * dk)]), paint((200, 20, 20)))
    return st.arr


def s_v_signal(T, idx):
    """Silence. Then: Signal lost."""
    st = K.Stage((6, 6, 10))
    c = st.c
    lost = T >= S("v5") - 0.05
    SE.car_interior(c, T, wiper=False, fog_a=0.8)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0), 0.5))
    C.push(c, T, E("v4"), S("v6"), 1.0, 1.18, cx=560, cy=1000)
    PR.gps(c, 560, 1000, 2.2, T, mode="lost" if lost else "route")
    if lost:
        SE.glow(c, 560, 1000, 500, (255, 30, 20), 0.3 * (1 if (math.floor(T * 4) % 2) == 0 else 0.4))
    c.restore()
    return st.arr


def s_v_cross(T, idx):
    """Which way is home? Vera at the crossroads, the signpost blank, the fog rising."""
    st = K.Stage()
    c = st.c
    C.dutch(c, -13, 540, 900)
    SE.swamp(c, T, fog_a=0.75)
    SE.signpost(c, 820, 1150, 1.0, T, L="green")
    C.person(c, "vera", 380, 900, 1.5, T, expr="fear", light="storm", gaze=(0.8, -0.6), turn=0.3, seed=6, shake=2)
    CO.fog(c, T, 1150, 1500, color=(170, 210, 170), a=0.6, seed=14, n=8, speed=40)
    c.restore()
    return st.arr


def s_v_cabbie(T, idx):
    """London cabbies who learn the city grow a bigger hippocampus: use it, and it grows."""
    st = C.page(seed=9)
    c = st.c
    sub = C.sub((30, 30, 40)).__enter__()
    sc = sub.c
    SE.grad_bg(sc, (40, 40, 60), (20, 20, 30))
    for i in range(6):                                                  # a rainy street of terraces
        sc.drawRect(skia.Rect.MakeLTRB(i * 170, 60, i * 170 + 150, 300), paint((60, 50, 56)))
        for k in range(3):
            sc.drawRect(skia.Rect.MakeLTRB(i * 170 + 20 + k * 40, 100, i * 170 + 46 + k * 40, 150), paint((255, 210, 120), 0.7))
    cab = K.smooth([(160, 400), (220, 300), (330, 260), (620, 260), (720, 300), (780, 400), (780, 450), (160, 450)])
    sc.drawPath(cab, paint((20, 20, 22)))
    sc.drawPath(cab, paint((90, 90, 100), stroke=4))
    for wx in (260, 680):
        sc.drawCircle(wx, 450, 50, paint((10, 10, 10)))
        sc.drawCircle(wx, 450, 22, paint((120, 120, 130)))
    sc.drawRect(skia.Rect.MakeLTRB(330, 280, 600, 360), paint((60, 70, 80)))
    FA.bust(sc, "junior", 450, 330, 0.3, T, expr="smile", light="lamp", body=False)
    sc.drawRect(skia.Rect.MakeLTRB(500, 300, 650, 380), paint((236, 226, 180)))
    for k in range(4):
        sc.drawLine(505, 310 + k * 20, 645, 320 + k * 16, paint((200, 80, 60), stroke=3))
    CO.rain(sc, T, 0, 0, 1000, 520, n=60, a=0.4, seed=2)
    sub.__exit__()
    CO.panel(c, sub.arr[:520, :980], 50, 250, 1030, 770, border=12, rot=-1)
    CO.label(c, "THE CABBIE'S MAP", 300, 330, 50, "bangers-400", (255, 226, 0), tag="label", outline=INK, ow=10)
    t1 = Wx("v7", "grow") - 0.2
    if T > t1:
        a = ease(ramp(T, t1, t1 + 0.3))
        sub2 = C.sub((30, 10, 40)).__enter__()
        s2 = sub2.c
        CO.shock(s2, (60, 20, 90), T, cx=500, cy=260, seed=4, rays=24, bolts=0)
        g = ease(ramp(T, Wx("v7", "grow"), Wx("v7", "grow") + 0.8))
        g2 = ease(ramp(T, Wx("v7", "grows") - 0.2, Wx("v7", "grows") + 0.4))
        PR.brain(s2, 500, 280, 1.0, T, glow=min(1, g + g2), grow=1 + 0.25 * g + 0.25 * g2)
        sub2.__exit__()
        CO.panel(c, sub2.arr[:500, :980], 50, 800, 1030, 1280, border=12, rot=0.8, a=a)
        CO.label(c, "HIPPOCAMPUS", 760, 880, 50, "bangers-400", (255, 226, 0), tag="label", outline=INK, ow=10, a=a)
    return st.arr


def s_v_bones(T, idx):
    """Fifteen years on: the car overgrown at the crossroads; inside, Vera's skeleton, the screen still recalculating."""
    st = K.Stage()
    c = st.c
    SE.swamp(c, T, fog_a=0.55)
    C.push(c, T, S("v8"), Wx("v8", "forever"), 1.0, 1.5, cx=440, cy=900)
    L = FA.Light("green")
    # the car from the side
    c.save()
    c.translate(540, 1000)
    body = K.smooth([(-500, 140), (-490, 30), (-320, 0), (-220, -170), (200, -180), (320, -20), (500, 10), (520, 140), (440, 190), (-440, 190)])
    FA.lit_fill(c, body, (150, 60, 70), L, rim=1.0, rim_w=8)
    win = path([(-230, -160), (60, -168), (60, -24), (-300, -18)])
    win2 = path([(80, -158), (180, -156), (280, -26), (80, -24)])
    c.save()
    c.clipPath(win, doAntiAlias=True)
    c.drawRect(skia.Rect.MakeLTRB(-300, -200, 100, 0), paint((10, 16, 20)))
    PR.gps(c, 10, -50, 0.26, T, mode="recalc")
    SE.glow(c, 10, -50, 120, (90, 180, 255), 0.4)
    PR.skull(c, -140, -80, 0.5, T, jaw=0.15, turn=-0.3, light="screen", cobweb=False)
    c.restore()
    c.drawPath(win2, paint((10, 16, 20)))
    CO.cobweb(c, -200, -150, 140, 0, 90, a=0.75, seed=2)
    CO.cobweb(c, 180, -156, 100, 90, 80, a=0.7, seed=3)
    c.drawPath(win, paint((40, 30, 30), stroke=12))
    for wx in (-300, 300):
        c.drawCircle(wx, 170, 80, paint((10, 10, 10)))
        c.drawCircle(wx, 170, 34, paint((70, 70, 70)))
    rng = K.rng_at(5, 5)
    for i in range(40):                                                 # moss and creepers over the roof and bonnet
        mx = rng.uniform(-480, 480)
        my = -170 + abs(mx) * 0.32 if abs(mx) < 300 else rng.uniform(-30, 20)
        c.drawCircle(mx, my + rng.uniform(-10, 10), rng.uniform(14, 34), paint((40 + rng.integers(0, 40), 90 + rng.integers(0, 50), 40), 0.9))
    for i in range(6):
        vx = rng.uniform(-480, 480)
        c.drawPath(K.bez_path([(vx, -100), (vx + 30, 40), (vx - 10, 180)]), paint((40, 100, 40), 0.9, stroke=6))
    c.restore()
    CO.spider(c, 300, 760 + 40 * math.sin(T * 1.3), 1.4, T)
    c.drawLine(300, 0, 300, 740 + 40 * math.sin(T * 1.3), paint((220, 220, 220), 0.5, stroke=1.5))
    c.restore()
    C.margin_host(c, T, 60, 470, 0.78, expr="cackle" if T > Wx("v8", "Recalculating") else "sly", t0=S("v8") + 0.2, light="green")
    CO.fog(c, T, 1150, 1450, color=(170, 210, 170), a=0.6, seed=15, n=7)
    return st.arr


def s_v_skull(T, idx):
    """...forever: the dead don't stay dead - the skull turns to us and its jaw drops."""
    st = K.Stage()
    c = st.c
    t0 = Wx("v8", "forever") - 0.05
    CO.shock(c, "red", T, cx=540, cy=760, seed=9)
    C.push(c, T, t0, t0 + 1.0, 1.0, 1.25, cx=540, cy=800)
    turn = 0.6 - 0.6 * ease(ramp(T, t0, t0 + 0.35))
    jaw = ease(ramp(T, t0 + 0.35, t0 + 0.6))
    PR.skull(c, 540, 760, 2.0, T, jaw=jaw, turn=turn, light="red")
    c.restore()
    PR.gps(c, 790, 1190, 0.62, T, mode="recalc")
    return st.arr

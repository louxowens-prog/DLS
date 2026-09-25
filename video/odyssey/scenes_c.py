"""Shots for chapter V and the close: beyond the next word, the Star Child, the end card."""
import math

import numpy as np
import skia

import gfx as G
from gfx import CX, H, W, ease, ramp
from cues import C
from scenes_a import draw_monolith, intertitle, label, once, panel
from timeline import TL


def s_int5(arr, t, d, T):
    intertitle(arr, t, d, "BEYOND THE NEXT WORD", "V")


GEN = [("Train A leaves Chicago at 80 mph.", G.GREY), ("Train B left 1 hour earlier, at 60 mph.", G.GREY),
       ("When does A catch B?", G.GREY), ("", None), ("Let t = hours after A leaves.", G.WHITE),
       ("80t = 60(t + 1)", G.AMBER), ("20t = 60", G.AMBER), ("t = 3 hours.", G.AMBER)]


def s_gen(arr, t, d, T):
    s = G.canvas_of(arr)
    f = G.font("jost-400", 44)
    fm = G.font("michroma-400", 18)
    with s as c:
        panel(c, 60, 430, 960, 860, code="GEN", color=G.CYAN)
        chars = int(max(0, t - 0.1) * 70)
        y = 530
        used = 0
        for ln, col in GEN:
            if not ln:
                y += 40
                continue
            n = max(0, min(len(ln), chars - used))
            used += len(ln)
            if n > 0:
                G.text(c, ln[:n], 110, y, f, color=col, align="left")
                if n < len(ln):
                    xw = G.text_width(ln[:n], f)
                    c.drawRect(skia.Rect.MakeXYWH(116 + xw, y - 38, 22, 44), G.paint(G.CYAN, 0.9))
            y += 84
        G.text(c, "EVERY SYMBOL ABOVE: ONE NEXT-TOKEN PREDICTION", CX, 1250, fm, color=G.CYAN, track=2)
        label(c, t, ["TRUE — AND MISLEADING"])


def _neurons():
    rng = np.random.default_rng(91)
    n = 110
    pts = np.stack([rng.uniform(80, W - 80, n), rng.uniform(420, 1250, n)], 1)
    edges = []
    for i in range(n):
        d = np.linalg.norm(pts - pts[i], axis=1)
        for j in np.argsort(d)[1:4]:
            if i < j:
                edges.append((i, int(j)))
    return pts, edges, rng.uniform(0, 1, len(edges)), rng.uniform(0.6, 1.6, len(edges))


def s_neurons(arr, t, d, T):
    pts, edges, ph, sp = once("neur", _neurons)
    s = G.canvas_of(arr)
    with s as c:
        for (i, j) in edges:
            c.drawLine(*pts[i], *pts[j], G.paint((70, 110, 170), 0.5, stroke=1.4))
        for k, (i, j) in enumerate(edges):
            u = (ph[k] + t * sp[k] * 0.8) % 1.0
            if u < 0.75:
                q = u / 0.75
                x = pts[i][0] + (pts[j][0] - pts[i][0]) * q
                y = pts[i][1] + (pts[j][1] - pts[i][1]) * q
                c.drawCircle(x, y, 6, G.paint((255, 230, 180), 0.55, blur=5))
                c.drawCircle(x, y, 2.4, G.paint((255, 250, 235), 1.0))
        for i, (x, y) in enumerate(pts):
            fl = 0.5 + 0.5 * math.sin(t * 4 + i * 1.3)
            c.drawCircle(x, y, 7, G.paint((140, 190, 255), 0.35 + 0.4 * fl, blur=4))
            c.drawCircle(x, y, 4, G.paint((210, 230, 255), 0.9))
        label(c, t, ["HUMAN BRAIN: ~86 BILLION NEURONS"])


def s_dallas(arr, t, d, T):
    s = G.canvas_of(arr)
    f = G.font("jost-500", 44)
    fs = G.font("michroma-400", 18)
    with s as c:
        panel(c, 60, 430, 960, 860, code="ATT", color=G.CYAN)
        G.text(c, "PROMPT: “the capital of the state", CX, 520, G.font("jost-400", 36), color=G.GREY)
        G.text(c, "containing Dallas is ___”", CX, 566, G.font("jost-400", 36), color=G.GREY)
        toks = [("capital", "capital", 190), ("state", "state", 430), ("containing", "containing", 650), ("Dallas", "Dallas", 890)]
        ybot, ymid, ytop = 1170, 950, 720
        node = {}
        for nm, kw, x in toks:
            a = ease(ramp(T, TL.word("dallas", kw) - 0.05, TL.word("dallas", kw) + 0.2))
            node[nm] = (x, ybot, a)
            G.text(c, nm, x, ybot + 14, f, a=a)
        mid = {"say a capital": (300, ymid, TL.word("dallas", "capital") + 0.35), "Texas": (760, ymid, C["texas"])}
        top_t = C["austin"]

        def box(x, y, txt, a, col):
            w = G.text_width(txt, f) + 50
            c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - 44, w, 72), 10, 10, G.paint(col, 0.18 * a))
            c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2, y - 44, w, 72), 10, 10, G.paint(col, 0.9 * a, stroke=2.5))
            G.text(c, txt, x, y + 8, f, color=G.WHITE, a=a)

        def edge(x0, y0, x1, y1, a, col):
            if a <= 0:
                return
            ex, ey = x0 + (x1 - x0) * a, y0 + (y1 - y0) * a
            c.drawLine(x0, y0, ex, ey, G.paint(col, 0.9, stroke=4))

        a_cap = ease(ramp(T, mid["say a capital"][2], mid["say a capital"][2] + 0.3))
        edge(190, ybot - 40, 300, ymid + 30, a_cap, G.CYAN)
        box(300, ymid, "say a capital", a_cap, G.CYAN)
        a_tx = ease(ramp(T, C["texas"] - 0.25, C["texas"] + 0.1))
        edge(890, ybot - 40, 760, ymid + 30, a_tx, G.AMBER)
        box(760, ymid, "Texas", a_tx, G.AMBER)
        a_au = ease(ramp(T, top_t - 0.2, top_t + 0.15))
        edge(300, ymid - 44, CX - 40, ytop + 30, a_au, G.CYAN)
        edge(760, ymid - 44, CX + 40, ytop + 30, a_au, G.AMBER)
        box(CX, ytop, "Austin", a_au, G.GREEN)
        G.text(c, "INPUT", 110, ybot + 80, fs, color=G.GREY, align="left", track=3)
        G.text(c, "INTERNAL STEP", 110, ymid + 90, fs, color=G.GREY, align="left", track=3, a=max(a_cap, a_tx))
        G.text(c, "ANSWER", 110, ytop - 70, fs, color=G.GREY, align="left", track=3, a=a_au)
        label(c, t, ["ANTHROPIC INTERPRETABILITY · 2025", "CLAUDE 3.5 HAIKU"])


def s_rhyme(arr, t, d, T):
    s = G.canvas_of(arr)
    f = G.font("jost-400", 50)
    with s as c:
        panel(c, 60, 470, 960, 760, code="PLN", color=G.CYAN)
        G.text(c, "He saw a carrot", CX, 620, f, color=G.GREY)
        G.text(c, "and had to grab it,", CX, 690, f, color=G.GREY)
        t_last = TL.word("rhyme", "last")
        t_first = TL.word("rhyme", "first")
        kp = ease(ramp(T, t_last - 0.1, t_last + 0.2))
        # the planned word sits in place before the line exists
        G.text(c, "rabbit", 770, 960, G.font("jost-500", 56), color=G.AMBER, a=kp, glow=12 * kp, glow_color=G.AMBER)
        G.text(c, "PLANNED FIRST", 770, 1020, G.font("michroma-400", 18), color=G.AMBER, a=kp, track=3)
        line = "His hunger was like a starving"
        n = int(max(0.0, T - (t_last + 0.45)) * 30)
        part = line[:n]
        l1, l2 = "His hunger was like", "a starving"
        G.text(c, l1[: min(len(l1), n)], CX, 860, f)
        if n > len(l1) + 1:
            G.text(c, l2[: n - len(l1) - 1], 470, 960, f)
        c.drawLine(270, 780, 810, 780, G.paint(G.GREY, 0.3, stroke=1))
        label(c, t, ["SAME STUDY: IT PLANS AHEAD"])


def _lunar_ground():
    hz = 1180
    h = H - hz
    y = np.linspace(0, 1, h)[:, None]
    g = G.fbm(h, W, octaves=4, seed=61, base=3)
    shade = (0.05 + 0.12 * y ** 0.8) * (0.85 + 0.3 * g)
    img = np.repeat(shade[..., None], 3, -1).astype(np.float32)
    arr = np.zeros((h, W, 4), np.uint8)
    arr[..., :3] = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    arr[..., 3] = 255
    rng = np.random.default_rng(64)
    s = skia.Surface(arr)
    with s as c:
        for _ in range(420):
            yy = h * rng.random() ** 1.8
            k = yy / h
            r = 1.5 + 22 * k * rng.random()
            x = rng.uniform(0, W)
            c.drawOval(skia.Rect.MakeXYWH(x - r, yy - r * 0.35, 2 * r, r * 0.7), G.paint((0, 0, 0), 0.5))
            c.drawOval(skia.Rect.MakeXYWH(x - r * 0.9, yy - r * 0.5, 1.8 * r, r * 0.6), G.paint((120, 120, 125), 0.35 + 0.3 * k))
    return arr[..., :3].astype(np.float32) / 255


def s_tma(arr, t, d, T):
    G.stars(arr, a=0.7)
    k = ease(t / d)
    sun_y = 610 - 70 * k
    G.put_sphere(arr, CX, 470, 64, kind="earth", light=(0.0, -0.8, -0.55), lon0=2.0, lat_tilt=0.3)
    G.add_light(arr, G.radial(CX, sun_y, 30, (255, 250, 235), 2.0, 2) + G.radial(CX, sun_y, 190, (255, 225, 190), 0.35, 1.2))
    gr = once("lunar", _lunar_ground)
    arr[1180:, :, :3] = (np.clip(gr, 0, 1) * 255).astype(np.uint8)
    s = G.canvas_of(arr)
    with s as c:
        c.drawRect(skia.Rect.MakeXYWH(0, 1180, W, 3), G.paint((190, 190, 195), 0.5))
        draw_monolith(c, CX, 1180 - 280, 250, 562, persp=0.1, side=0.0, rim=0.6)
        label(c, t, ["REAL REASONING?", "STILL AN OPEN QUESTION"])


def s_jagged(arr, t, d, T):
    s = G.canvas_of(arr)
    fs = G.font("michroma-400", 18)
    with s as c:
        panel(c, 50, 430, 980, 900, code="EVL", color=G.CYAN)
        x0, x1 = 100, 980
        yh = 900                     # typical human level
        c.drawLine(x0, yh, x1, yh, G.paint(G.GREY, 0.6, stroke=2))
        G.text(c, "TYPICAL PERSON", x1, yh - 14, fs, color=G.GREY, align="right", track=2)
        pts = [(0.00, 0.1), (0.07, -0.4), (0.14, 0.2), (0.22, 0.95), (0.30, 0.1), (0.38, 0.5), (0.47, -0.3),
               (0.55, 0.3), (0.63, 0.7), (0.71, -0.2), (0.79, -0.95), (0.87, 0.25), (1.00, 0.45)]
        prog = ease(ramp(t, 0.2, d * 0.55))
        path = skia.Path()
        for i, (u, v) in enumerate(pts):
            if u > prog + 1e-6:
                break
            x, y = x0 + u * (x1 - x0), yh - v * 330
            path.moveTo(x, y) if i == 0 else path.lineTo(x, y)
        c.drawPath(path, G.paint(G.CYAN, 0.35, stroke=10, blur=6))
        c.drawPath(path, G.paint(G.WHITE, 1.0, stroke=4))
        ta = TL.word("jagged", "Olympiad")
        ka = ease(ramp(T, ta - 0.1, ta + 0.25))
        px, py = x0 + 0.22 * (x1 - x0), yh - 0.95 * 330
        c.drawCircle(px, py, 12, G.paint(G.AMBER, ka))
        G.text(c, "MATH OLYMPIAD", px + 20, py - 50, G.font("michroma-400", 20), color=G.AMBER, a=ka, align="left", track=2)
        G.text(c, "GOLD-MEDAL LEVEL · 2025", px + 20, py - 22, fs, color=G.WHITE, a=ka, align="left", track=2)
        tb = TL.word("jagged", "under")
        kb = ease(ramp(T, tb - 0.1, tb + 0.25))
        qx, qy = x0 + 0.79 * (x1 - x0), yh + 0.95 * 330
        c.drawCircle(qx, qy, 12, G.paint(G.HAL, kb))
        G.text(c, "NEW PUZZLE GAMES", qx - 20, qy + 48, G.font("michroma-400", 20), color=G.HAL, a=kb, align="right", track=2)
        G.text(c, "UNDER 1% · ARC-AGI-3 LAUNCH, 2026", qx - 20, qy + 76, fs, color=G.WHITE, a=kb, align="right", track=1)
        label(c, t, ["THE JAGGED FRONTIER"])


def s_starchild(arr, t, d, T):
    G.stars(arr, dy=-12 * t, a=0.85)
    erg = once("earth_sc", lambda: G.sphere(760, kind="earth", light=(0.45, 0.55, 0.7), lon0=5.2, lat_tilt=0.4))
    rgb, al, glow, off = erg
    G.over(arr, rgb, al, int(CX - off), int(2150 - off + 60 * (1 - ease(t / d))))
    kz = ease(t / d)
    cx, cy, R = CX, 760 + 20 * kz, 230 * (1 + 0.18 * kz)
    orb = G.radial(cx, cy, R * 0.95, (120, 170, 255), 0.35, 3.0) + G.radial(cx, cy, R * 1.6, (80, 120, 255), 0.18, 1.5)
    G.add_light(arr, orb)
    s = G.canvas_of(arr)
    with s as c:
        c.drawCircle(cx, cy, R, G.paint((190, 215, 255), 0.35, stroke=3))
        c.drawCircle(cx, cy, R - 2, G.paint((170, 200, 255), 0.10))
        # the curled figure in profile: head up and right, back curved, knees tucked
        c.save()
        c.translate(cx, cy)
        c.scale(R / 230, R / 230)
        c.translate(-cx, -cy)
        fig = skia.Path()
        fig.addCircle(cx + 35, cy - 75, 78)
        body = skia.Path()
        body.moveTo(cx - 35, cy - 95)
        body.cubicTo(cx - 105, cy - 30, cx - 100, cy + 90, cx - 20, cy + 140)
        body.cubicTo(cx + 40, cy + 170, cx + 110, cy + 140, cx + 105, cy + 85)
        body.cubicTo(cx + 100, cy + 40, cx + 60, cy + 30, cx + 70, cy - 5)
        body.cubicTo(cx + 40, cy - 20, cx + 10, cy - 60, cx - 35, cy - 95)
        fig = skia.Op(fig, body, skia.PathOp.kUnion_PathOp) or fig
        grad = skia.GradientShader.MakeRadial(skia.Point(cx + 20, cy - 20), 200,
                                              [skia.Color4f(1.0, 0.90, 0.84, 0.85), skia.Color4f(0.95, 0.75, 0.70, 0.35)])
        c.drawPath(fig, G.paint((255, 225, 210), 0.30, blur=18))
        c.drawPath(fig, G.paint(shader=grad, blur=3, a=0.75))
        shade = skia.GradientShader.MakeLinear([skia.Point(cx + 80, cy - 120), skia.Point(cx - 80, cy + 140)],
                                               [skia.Color4f(0, 0, 0, 0), skia.Color4f(0.15, 0.1, 0.25, 0.45)])
        c.drawPath(fig, G.paint(shader=shade, blur=6))
        c.drawOval(skia.Rect.MakeXYWH(cx + 70, cy - 88, 30, 18), G.paint((70, 80, 120), 0.6, blur=2.5))
        c.restore()


SOURCES = ["Legg & Hutter 2007 · NIST CSRC glossary · OpenAI Help Center",
           "Mikolov et al. 2013 · Meta Llama 3 model card (2024)",
           "Frank, Trends in Cognitive Sciences 2023 · Anthropic 2025",
           "IMO 2025 (Google DeepMind, OpenAI) · ARC Prize 2026"]


def s_endcard(arr, t, d, T):
    G.stars(arr, a=0.5)
    s = G.canvas_of(arr)
    with s as c:
        a = ease(ramp(t, 0.0, 0.5))
        G.text(c, "WHAT IS", CX, 700, G.font("jost-300", 42), a=a, track=24)
        G.text(c, "intelligence?", CX, 815, G.font("cabin-400", 104), a=a, track=14)
        a2 = ease(ramp(t, 0.8, 1.3))
        G.text(c, "SOURCES", CX, 1010, G.font("michroma-400", 20), color=G.AMBER, a=a2, track=6)
        for i, ln in enumerate(SOURCES):
            G.text(c, ln, CX, 1060 + i * 40, G.font("jost-400", 26), color=G.GREY, a=a2)
        G.text(c, "Fanfare after R. Strauss (1896) and choral clusters after G. Ligeti, re-synthesized",
               CX, 1260, G.font("jost-400", 22), color=G.DIM, a=a2)
        G.text(c, "Narration: synthetic voice", CX, 1295, G.font("jost-400", 22), color=G.DIM, a=a2)

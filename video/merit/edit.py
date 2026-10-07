"""The edit: (start time, shot, transition in, look). Times hang off the narration (S = a line's start, E = its end,
Wx = a word's start), so the picture follows the voice. Looks are look.look() parameters: the wash deepens chapter by
chapter - cobalt, red, magenta, blood - and the dream melts as it turns to nightmare."""
from common import E, S, Wx
from timeline import TL

TRANS = {"cut": 0.0, "dissolve": 0.6, "slow": 1.4, "super": 2.4, "flash": 0.16, "black": 0.4, "burn": 0.7}

# looks
BLOOD = dict(wash="blood", wash_k=0.85, haze=0.6, streak=0.7)
NIGHT = dict(wash="violet", wash_k=0.62, keep=0.75, haze=0.7, streak=0.6)
FIRE = dict(wash="ember", wash_k=0.45, keep=0.6, haze=0.7)
CARD = dict(wash="red", wash_k=0.3, keep=0.7, haze=0.4, streak=0.8, grain=0.8)
COBALT = dict(wash="cobalt", wash_k=0.7, keep=0.6, haze=0.75, streak=0.6)
VIOLET = dict(wash="violet", wash_k=0.66, keep=0.55, haze=0.8, streak=0.6, breathe=0.4)
MAGENTA = dict(wash="magenta", wash_k=0.75, keep=0.5, haze=0.8, streak=0.6)
RED = dict(wash="red", wash_k=0.82, keep=0.4, haze=0.7, streak=0.6)
DEEP = dict(wash="blood", wash_k=0.86, keep=0.3, haze=0.8, streak=0.7, breathe=0.6)
FLUORO = dict(wash="fluoro", wash_k=0.6, keep=0.5, haze=0.5, streak=0.4, grain=1.1)
AIRBRUSH = dict(wash=None, haze=0.5, streak=0.7, grain=0.8, sat=1.15, breathe=0.5)


def L(base, **kw):
    d = dict(base)
    d.update(kw)
    return d


EDIT = [
    # ---- the hook: a stamp comes down in red; the verdict
    (0.0, "h_stamp", "cut", BLOOD),
    # ---- cold open: the quiet night - a wrong moon, a sky of punched-card stars, a fire of records
    (E("h1") + 0.3, "o_sky", "burn", L(NIGHT, burn_at=(0.2, 0.3))),
    (Wx("c1", "records:") - 0.25, "o_fire", "dissolve", L(NIGHT, wash_k=0.5)),
    (E("c1") + 0.2, "t_title", "flash", L(CARD, wash="red")),
    (E("c1") + 1.6, "k_1", "burn", L(CARD, wash="cobalt")),
    # ---- I. THE INHERITANCE (cobalt)
    (S("i1") - 0.05, "i_dreamer", "slow", COBALT),
    (Wx("i1", "our") - 0.2, "i_cards", "dissolve", L(COBALT, wash_k=0.5)),
    (S("i2") - 0.2, "i_faces", "slow", L(VIOLET, wash="magenta", wash_k=0.18, keep=0.0, breathe=0.2)),
    (S("i3") - 0.4, "i_eyes", "dissolve", L(VIOLET, wash_k=0.55)),
    (Wx("i3", "I", 1) - 0.1, "i_mouth", "slow", L(VIOLET, wash_k=0.5)),
    (Wx("i3", "I", 2) - 0.1, "i_merit", "slow", L(VIOLET, wash_k=0.5)),
    (E("i3") + 0.2, "k_2", "burn", L(CARD, wash="red")),
    # ---- II. THE PATTERN (red)
    (S("p1") - 0.05, "p_portraits", "dissolve", RED),
    (Wx("p1", "and") - 0.3, "p_template", "super", RED),
    (S("p2") - 0.1, "p_cv", "dissolve", L(RED, wash_k=0.6)),
    (Wx("p2", "It", 1) - 0.1, "p_scrap", "cut", L(RED, wash_k=0.7)),
    (S("p3") - 0.1, "p_calm", "slow", L(RED, wash_k=0.7, breathe=0.5)),
    (Wx("p3", "The", 1) - 0.15, "p_door", "dissolve", DEEP),
    (S("p4") - 0.1, "p_proxy", "dissolve", L(RED, wash_k=0.6)),
    (E("p4") + 0.2, "k_3", "burn", L(CARD, wash="magenta")),
    # ---- III. THE MULTITUDE (magenta)
    (S("m1") - 0.05, "m_manager", "dissolve", MAGENTA),
    (Wx("m1", "An") - 0.12, "m_army", "flash", L(MAGENTA, pulse=0.6)),
    (S("m2") - 0.1, "m_nist", "dissolve", MAGENTA),
    (S("m4") - 0.2, "m_kaleido", "slow", L(MAGENTA, melt=0.35, breathe=0.8, pulse=1.0)),
    (E("m4") + 0.2, "k_4", "burn", L(CARD, wash="blood")),
    # ---- IV. THE VERDICT (blood)
    (S("v1") - 0.05, "v_doors", "dissolve", DEEP),
    (S("v2") - 0.4, "v_why", "cut", L(DEEP, melt=0.3)),
    (E("v2"), "v_silence", "cut", L(DEEP, haze=1.0, breathe=1.2, melt=0.4)),
    (S("v3") - 0.02, "v_mask", "cut", L(BLOOD, streak=1.0)),
    (E("v3") + 0.15, "v_vars", "flash", L(VIOLET, wash_k=0.6, melt=0.15)),
    (Wx("v4", "You") - 0.15, "v_clerk", "dissolve", L(FIRE, wash="ember", wash_k=0.5)),
    (S("v5") - 0.1, "v_dutch", "dissolve", L(COBALT, wash_k=0.62, keep=0.7)),
    (Wx("v5", "The", 1) - 0.15, "v_gov", "dissolve", L(COBALT, wash_k=0.66, keep=0.7)),
    # ---- the descent: the dreamer drifts through space; she falls
    (E("v5") + 0.2, "d_space", "burn", AIRBRUSH),
    # ---- IRIS: a kitchen at 2 a.m.
    (S("r1") - 0.1, "r_kitchen", "flash", FLUORO),
    (Wx("r1", "Seventy") - 0.1, "r_inbox", "cut", FLUORO),
    (Wx("r1", "No") - 0.12, "r_slot", "dissolve", L(COBALT, wash_k=0.65)),
    (S("r2") - 0.15, "r_why", "dissolve", L(FLUORO, wash="cobalt", wash_k=0.5)),
    (S("r3") - 0.2, "r_answer", "cut", L(FLUORO, wash="cobalt", wash_k=0.55)),
    (S("r4") - 0.05, "r_phone", "cut", L(FLUORO, wash_k=0.5)),
    (Wx("r4", "Her", 2) - 0.12, "r_reasons", "dissolve", L(FLUORO, wash="cobalt", wash_k=0.55)),
    (S("r5") - 0.1, "r_scream", "cut", L(DEEP, melt=0.5, breathe=1.0, smear=0.3)),
    # ---- the eruption
    (E("r5") - 0.3, "x_erupt", "flash", L(DEEP, wash_k=0.55, keep=0.4, melt=0.3, breathe=1.0, pulse=1.0, smear=0.1, streak=1.0)),
    # ---- dead silence; then her eye opens on you
    (E("x1") + 0.15, "y_black", "cut", L(DEEP, haze=0.3, grain=1.3)),
    (S("y1") - 0.08, "y_eye", "cut", L(VIOLET, wash="magenta", wash_k=0.55, breathe=0.6)),
    (S("y2") - 0.1, "y_dossier", "dissolve", L(RED, wash_k=0.6)),
    # ---- the quiet: the fire again, and the lesson
    (E("y2") + 0.15, "e_fire", "black", FIRE),
    (Wx("e1", "NIST") - 0.3, "e_tablet", "dissolve", FIRE),
    (S("e2") - 0.1, "e_ask", "dissolve", FIRE),
    (Wx("e2", "In") - 0.15, "e_hand", "dissolve", FIRE),
    (E("e2") + 0.25, "e_moon", "slow", L(NIGHT, wash="red", wash_k=0.55, keep=0.5)),
]


def shot_at(T):
    i = 0
    for j, e in enumerate(EDIT):
        if e[0] <= T:
            i = j
    return i


def cut(name):
    return next(e[0] for e in EDIT if e[1] == name)


def end(name):
    i = next(j for j, e in enumerate(EDIT) if e[1] == name)
    return EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total


def look_at(T, i=None):
    return EDIT[shot_at(T) if i is None else i][3]

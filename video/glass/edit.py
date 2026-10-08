"""The edit: (start time, shot, transition in, look). Times hang off the narration (S = a line's start, E = its end,
Wx = a word's start), so the picture follows the voice. Two worlds, two prints: the cold room in steel blue-grey,
the dream in saturated jewel tones with a soft bloom - gold for the eye, emerald for the workhouse, royal blue for
the oracle, blood red for the scales."""
from common import E, S, Wx
from timeline import TL

TRANS = {"cut": 0.0, "dissolve": 0.5, "slow": 1.2, "super": 1.6, "flash": 0.16, "black": 0.4, "burn": 0.7}


def L(base, **kw):
    d = dict(base)
    d.update(kw)
    return d


# the dream: a polished late-90s music-video print - crisp, saturated, soft bloom, almost no grain
GLOSS = dict(wash=None, grain=0.12, dust=0.0, wv=0.0, flick=0.05, leak=0.0, lift=(0.008, 0.008, 0.014), crush=1.12, halation=0.4,
             streak=0.12, streak_tint=(255, 220, 170), ca=0.35, haze=0.08, bloom=0.4, diffusion=0.5, sat=1.2, vig=0.75)
# the real world: steel blue-grey, monitor glow, the colour drained out (alerts keep their red)
COLD = dict(wash="steel", wash_k=0.55, keep=0.6, grain=0.16, dust=0.0, wv=0.0, flick=0.06, leak=0.0, lift=(0.02, 0.025, 0.035), crush=1.05,
            halation=0.15, streak=0.06, streak_tint=(180, 220, 255), ca=0.3, haze=0.05, bloom=0.3, diffusion=0.4, sat=0.55, vig=0.6)
ROOM = L(COLD, bloom=0.22, expose=0.92)
NIGHT = L(COLD, wash_k=0.35, keep=0.75, sat=0.7, bloom=0.4)
WATER = L(GLOSS, wash="royal", wash_k=0.45, keep=0.4, haze=0.25, bloom=0.5, breathe=0.3)
DAWN = L(GLOSS, haze=0.12, bloom=0.45, streak=0.25)
CARD = L(GLOSS, bloom=0.5, haze=0.1, grain=0.1, vig=0.9, streak=0.2)
GOLDHALL = L(GLOSS, sat=1.22)
RED = L(GLOSS, sat=1.25, bloom=0.42)
SALT = L(GLOSS, bloom=0.25, expose=0.92, sat=1.1, haze=0.0, grain=0.2)
EMER = L(GLOSS, wash="emerald", wash_k=0.22, keep=0.75)
ROYAL = L(GLOSS, wash="royal", wash_k=0.22, keep=0.75)
BLOOD = L(GLOSS, wash="crimson", wash_k=0.2, keep=0.75)
TEAL = L(GLOSS, wash="teal", wash_k=0.2, keep=0.75)
DREAD = L(GLOSS, sat=1.25, breathe=0.45, melt=0.06)
STORM = L(GLOSS, sat=1.3, bloom=0.5, breathe=0.7, melt=0.12, streak=0.3, ca=0.8)
VOID = L(GLOSS, bloom=0.35, grain=0.18, vig=0.95)

EDIT = [
    # ---- the hook: a face in a targeting box
    (0.0, "h_match", "cut", L(COLD, wash_k=0.45)),
    (E("h1") + 0.12, "h_lamp", "cut", ROOM),
    (Wx("h2", "We're") - 0.1, "h_machine", "dissolve", ROOM),
    # ---- cold open: the humming room, then going under
    (E("h2") + 0.2, "c_monitors", "cut", COLD),
    (S("c1") - 0.25, "c_sink", "dissolve", WATER),
    (E("c1") + 0.3, "c_dawn", "super", DAWN),
    (S("e1") - 1.05, "k_1", "dissolve", CARD),
    # ---- I. THE EYE
    (S("e1") - 0.05, "e_list", "cut", GOLDHALL),
    (S("e2") - 0.05, "e_keyhole", "dissolve", GOLDHALL),
    (Wx("e2", "Joined") - 0.15, "e_house", "super", L(GLOSS, haze=0.15, bloom=0.5)),
    (S("e3") - 0.1, "e_army", "dissolve", L(GOLDHALL, wash="royal", wash_k=0.15, keep=0.8)),
    (S("e4") - 0.05, "e_doors", "cut", GOLDHALL),
    (S("e6") - 0.1, "e_salt", "dissolve", SALT),
    (S("e7") - 0.05, "e_hand", "dissolve", RED),
    (E("e7") + 0.2, "e_hush", "cut", L(RED, bloom=0.3)),
    (S("e8") - 0.06, "e_eyes", "cut", L(RED, streak=0.3)),
    (E("e8") + 0.2, "k_2", "dissolve", CARD),
    # ---- II. THE WORKHOUSE
    (S("w1") - 0.05, "w_corridor", "dissolve", EMER),
    (S("w2") - 0.05, "w_altar", "cut", EMER),
    (S("w3") - 0.05, "w_towers", "dissolve", L(SALT, wash="emerald", wash_k=0.12, keep=0.8)),
    (S("w4") - 0.05, "w_idle", "dissolve", EMER),
    (S("w5") - 0.05, "w_press", "dissolve", EMER),
    (S("w6") - 0.15, "w_smile", "cut", L(EMER, breathe=0.3)),
    (E("w6") + 0.25, "k_3", "dissolve", CARD),
    # ---- III. THE ORACLE
    (S("o1") - 0.05, "o_veils", "dissolve", ROYAL),
    (S("o2") - 0.05, "o_points", "dissolve", L(SALT, wash="royal", wash_k=0.12, keep=0.8)),
    (S("o4") - 0.05, "o_sphere", "dissolve", ROYAL),
    (S("o6") - 0.15, "o_mirror", "cut", L(ROYAL, breathe=0.3)),
    (E("o6") + 0.25, "k_4", "dissolve", CARD),
    # ---- IV. THE SCALES
    (S("t2") - 0.05, "t_metro", "dissolve", BLOOD),
    (S("t3") - 0.05, "t_gate", "dissolve", TEAL),
    (S("t4") - 0.05, "t_lineup", "dissolve", BLOOD),
    (S("t5") - 0.05, "t_library", "dissolve", BLOOD),
    (E("t5") + 0.2, "t_hush", "cut", L(BLOOD, bloom=0.3)),
    (S("t6") - 0.1, "t_scales", "cut", DREAD),
    # ---- the descent: her favourite exhibit
    (S("d1") - 0.2, "d_procession", "dissolve", DREAD),
    # ---- NADIA: an ordinary day
    (S("n1") - 0.3, "n_mirror", "flash", ROOM),
    (S("n2") - 0.05, "n_road", "cut", COLD),
    (S("n3") - 0.05, "n_call", "cut", COLD),
    (S("n4") - 0.05, "n_idle", "cut", COLD),
    (S("n5") - 0.05, "n_union", "cut", COLD),
    (S("n6") - 0.05, "n_checkout", "cut", COLD),
    (Wx("n6", "The") - 0.1, "n_exhibit", "cut", RED),
    (S("n7") - 0.1, "n_face", "cut", COLD),
    (S("n8") - 0.05, "n_vigil", "cut", NIGHT),
    (S("n9") - 0.05, "n_phone", "cut", COLD),
    (S("n10") - 0.1, "n_door", "cut", L(NIGHT, bloom=0.5)),
    (S("n11") - 0.1, "n_match", "cut", L(COLD, wash_k=0.4)),
    (S("n12") - 0.05, "n_scream", "cut", L(COLD, wash_k=0.25, keep=0.85, sat=0.9)),
    # ---- the collapse
    (E("n12") + 0.1, "x_collapse", "flash", STORM),
    # ---- the twist
    (E("x1") + 0.6, "y_vitrine", "cut", L(SALT, bloom=0.35)),
    (S("y2") - 0.05, "y_phone", "dissolve", L(SALT, bloom=0.35)),
    (E("y2") + 0.15, "y_glass", "cut", VOID),
    # ---- the cold room again: the lesson, and the last image
    (E("y3") + 0.35, "z_room", "cut", ROOM),
    (S("z2") - 0.05, "z_law", "dissolve", COLD),
    (S("z3") - 0.05, "z_ask", "dissolve", COLD),
    (E("z3") + 0.3, "z_final", "cut", L(ROOM, vig=0.8)),
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

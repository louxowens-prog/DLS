"""The edit: (start time, shot, transition in, look). Times hang off the narration (S = a line's start, E = its end,
Wx = a word's start), so the picture follows the voice. Looks: plain=1 is the present day (no gels, no grain, no
diffusion); everything else is the 1974 print."""
from common import E, S, Wx
from timeline import TL

TRANS = {"cut": 0.0, "dissolve": 0.7, "slow": 1.3, "white": 0.5, "black": 0.45, "flash": 0.14}
NOW = {"plain": 1.0, "grain": 0.35, "dust": 0.0}

EDIT = [
    # ---- the hook: a porcelain graduate; inside, nothing
    (0.0, "h_doll", "cut", {}),
    (E("h2") + 0.55, "t_title", "cut", {}),
    # ---- the square at nine o'clock
    (S("o1") - 0.25, "q_square", "dissolve", {}),
    (Wx("o1", "its") - 0.15, "q_clock", "cut", {}),
    (E("o1") + 0.05, "q_clara", "cut", {}),
    # ---- the labyrinth
    (S("l1") - 0.3, "l_alley", "dissolve", {}),
    (Wx("l1", "In") - 0.1, "l_window", "cut", {}),
    (S("l2") - 0.1, "l_stairs", "cut", {}),
    (S("l3") - 0.15, "l_name", "cut", {}),
    (E("l3") + 0.45, "l_loop", "cut", {}),
    (S("v1") - 1.1, "v_gate", "cut", {}),
    (S("v1") - 0.15, "v_door", "cut", {}),
    # ---- the gallery of graduates
    (E("v1") + 0.25, "g_gallery", "dissolve", {}),
    (S("g2") - 0.1, "g_exam", "cut", {}),
    (S("g3") - 0.1, "g_double", "cut", {}),
    # ---- the writing room: the same night, year after year
    (S("w1") - 0.45, "w_desk", "dissolve", {}),
    (S("w3") - 0.55, "w_desk2", "cut", {}),
    (S("w5") - 0.05, "w_shelves", "cut", {}),
    (S("w6") - 0.55, "w_desk3", "cut", {}),
    (S("w8") - 0.05, "w_ledger", "cut", {}),
    (E("w8") + 0.25, "w_final", "cut", {}),
    # ---- the clockwork
    (S("c1") - 0.1, "c_gears", "dissolve", {}),
    (Wx("c2", "biggest") - 0.25, "c_bug", "cut", {}),
    (S("c3") - 0.1, "c_fix", "cut", {}),
    (E("c4") + 0.7, "c_scare", "cut", {}),
    # ---- the hall of mirrors
    (S("m1") - 0.15, "m_mirrors", "dissolve", {}),
    (S("m2") - 0.1, "m_super", "slow", {}),
    # ---- the locked door
    (E("m2") + 0.2, "x_door", "dissolve", {}),
    # ---- the present day
    (E("x1") + 1.25, "r_room", "white", NOW),
    (S("r2") - 0.1, "r_code", "cut", NOW),
    (S("r3") - 0.1, "r_diss", "cut", NOW),
    (S("r5") - 0.1, "r_thanks", "cut", NOW),
    (S("r6") - 0.25, "r_after", "cut", NOW),
    (E("r6") + 0.3, "p_window", "dissolve", {"diffusion": 0.7}),
    # ---- the lesson
    (S("e1") - 0.9, "e_slate", "black", {}),
    (S("e2") - 0.1, "e_unesco", "dissolve", {}),
    (S("e3") - 0.15, "e_clock", "dissolve", {}),
    (TL.total - 1.7, "e_fine", "dissolve", {}),
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

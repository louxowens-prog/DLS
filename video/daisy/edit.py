"""The edit: every shot, when it starts, how we get into it, and the colour of the print - which changes from shot to
shot and sometimes in the middle of one.

Transitions: cut; jump (a jump cut inside a scene); flash (a frame or two of dye before the cut); scissors (the old
frame is cut to pieces that fly apart off the new one)."""
from common import E, S, Wx
from timeline import TL

# (start, shot, transition, [(time, print mode), ...])
EDIT = [
    # ---- cold open
    (0.0, "o_gears", "cut", [(k * 0.25, m) for k, m in enumerate(["blue", "full", "bw", "amber", "red", "full", "violet", "green", "bw", "full"])]),
    (S("o1") + 0.25, "o_strip", "flash", [(0, "full")]),
    (Wx("o1", "A.") + 0.3, "o_gears", "jump", [(0, "blue"), (Wx("o1", "A.") + 0.45, "red")]),
    (Wx("o1", "Then") - 0.07, "o_duo", "jump", [(0, "full"), (S("o3") - 0.05, "bw")]),
    (E("o3") + 0.15, "o_window", "cut", [(0, "amber")]),
    (Wx("o4", "Sometimes") - 0.1, "o_window@1.15", "jump", [(0, "violet")]),
    (E("o4") + 0.05, "title", "scissors", [(0, "full"), (E("o4") + 0.9, "green")]),
    # ---- 1: THE PAINTED WINDOW
    (S("a1") - 0.15, "a_cut", "flash", [(0, "full")]),
    (S("a2") - 0.1, "a_open", "cut", [(0, "green"), (Wx("a2", "Not") - 0.1, "amber")]),
    (S("a3") - 0.1, "a_shortcut", "cut", [(0, "full"), (S("a4") - 0.1, "violet")]),
    (S("a5") - 0.06, "a_used", "jump", [(0, "full")]),
    (Wx("a5", "In") - 0.08, "a_used@1.12", "jump", [(0, "full")]),
    (Wx("a5", "under") - 0.1, "a_used", "jump", [(0, "red")]),
    (E("a5") + 0.05, "a_count", "cut", [(0, "bw")]),
    (S("a7") - 0.1, "a_tracks", "scissors", [(0, "blue"), (Wx("a7", "two") - 0.1, "green")]),
    (S("a8") - 0.08, "a_carry", "cut", [(0, "full")]),
    (S("a9") - 0.05, "a_didnot", "jump", [(0, "bw")]),
    (S("a11") - 0.08, "a_notfake", "cut", [(0, "green"), (Wx("a11", "But") - 0.1, "amber")]),
    (S("a12") - 0.08, "a_faces", "cut", [(0, "red"), (Wx("a12", "usually") - 0.1, "full")]),
    (S("a13") - 0.08, "a_faces@1.15@540@420", "jump", [(0, "full")]),
    (S("a14") - 0.08, "a_interp", "cut", [(0, "blue"), (Wx("a14", "That") - 0.1, "violet")]),
    (S("a15") - 0.1, "a_refrain", "flash", [(0, "amber")]),
    # ---- 2: THE ANSWER-KEY CAKE
    (E("a16") + 0.1, "b_card", "scissors", [(0, "full")]),
    (S("b1") - 0.06, "b_banners", "cut", [(0, "full"), (Wx("b1", "Human") - 0.05, "red"), (Wx("b1", "PhD") - 0.05, "amber")]),
    (S("b2") - 0.08, "b_iq", "cut", [(0, "bw")]),
    (S("b3") - 0.08, "b_broken", "cut", [(0, "green")]),
    (Wx("b3", "two") - 0.15, "b_broken@1.12", "jump", [(0, "full")]),
    (S("b5") - 0.08, "b_months", "flash", [(0, "amber"), (Wx("b5", "beaten") - 0.1, "blue")]),
    (S("b6") - 0.08, "b_leak", "cut", [(0, "violet")]),
    (S("b7") - 0.1, "b_leak@1.2", "jump", [(0, "full")]),
    (S("b8") - 0.08, "b_feed", "cut", [(0, "full")]),
    (Wx("b8", "survey") - 0.6, "b_fresh", "jump", [(0, "green")]),
    (S("b9") - 0.08, "b_94", "cut", [(0, "amber"), (Wx("b9", "But") - 0.1, "bw")]),
    (S("b10") - 0.1, "b_refrain", "flash", [(0, "amber")]),
    # ---- 3: THE GOLD MEDAL CLOCK
    (E("b11") + 0.1, "c_card", "scissors", [(0, "full")]),
    (S("c1") - 0.06, "c_medal", "cut", [(0, "full"), (Wx("c1", "Math") - 0.1, "amber")]),
    (S("c2") - 0.08, "c_clock", "cut", [(0, "bw")]),
    (S("c3") - 0.08, "c_tuesday", "jump", [(0, "violet")]),
    (S("c4") - 0.08, "c_score", "cut", [(0, "green")]),
    (Wx("c4", "Humans") - 0.25, "c_score@1.1", "jump", [(0, "full")]),
    (S("c5") - 0.06, "c_proofs", "flash", [(0, "full"), (Wx("c5", "Clocks") - 0.05, "red")]),
    (S("c6") - 0.08, "c_jagged", "cut", [(0, "violet"), (Wx("c6", "Researchers") - 0.1, "amber")]),
    (Wx("c6", "jagged") - 0.15, "c_jagged@1.12", "jump", [(0, "amber")]),
    (S("c7") - 0.08, "c_agents", "cut", [(0, "blue")]),
    (Wx("c7", "Robots") - 0.1, "c_sim", "jump", [(0, "green")]),
    (Wx("c7", "about", 1) - 0.12, "c_real", "cut", [(0, "red")]),
    # ---- the banquet
    (E("c7") + 0.1, "d_feast", "scissors", [(0, "full"), (S("d3") - 0.05, "amber")]),
    (E("d4") + 0.05, "d_fight", "cut", [(E("d4") + 0.05 + k * 0.22, m) for k, m in enumerate(["full", "red", "amber", "full", "green"])]),
    (E("d4") + 1.05, "d_fire", "jump", [(0, "full")]),
    (E("d4") + 1.8, "d_pie", "jump", [(0, "red"), (E("d4") + 2.13, "full")]),
    (E("d4") + 2.5, "d_cake", "jump", [(0, "amber"), (E("d4") + 2.72, "full")]),
    (E("d4") + 3.2, "d_fight", "jump", [(E("d4") + 3.2 + k * 0.22, m) for k, m in enumerate(["violet", "red", "blue", "full", "amber"])]),
    (S("d5") - 1.15, "d_still", "cut", [(0, "bw")]),
    # ---- epilogue
    (E("d5") + 0.35, "e_clue", "cut", [(0, "full")]),
    (E("d5") + 2.35, "e_mend", "cut", [(0, "amber")]),
    (S("e1") - 0.1, "e_clue", "jump", [(0, "full")]),
    (Wx("e1", "score") - 0.25, "e_sample", "jump", [(0, "amber")]),
    (Wx("e1", "check") - 0.25, "e_clock", "jump", [(0, "full")]),
    (E("e1") + 0.1, "e_dedication", "cut", [(0, "bw")]),
    (S("e2") - 0.15, "e_end", "flash", [(0, "full"), (E("e3") + 0.4, "amber")]),
]

TRANS = {"scissors": 0.45, "flash": 0.08}

# freeze frames: the picture stops (the grain and the voice go on) - just before each cut to silence
FREEZES = [(E("a5") - 0.3, S("a6") - 0.95), (S("d5") - 1.45, S("d5") - 1.15)]


# the duo sliced into strips by the editor's scissors, and reassembled: (start, length, x0, y0, x1, y1)
SLICES = [(S("o3") - 0.05, 0.45, 60, 880, 380, 1800), (S("a9") - 0.05, 0.4, 0, 300, 1080, 1700),
          (E("d4") + 0.55, 0.35, 0, 200, 1080, 1800), (S("e3") + 0.1, 0.4, 60, 1050, 340, 1920)]


def frozen(T):
    """The moment the picture shows at time T (T itself unless a freeze holds an earlier frame)."""
    for a, b in FREEZES:
        if a <= T < b:
            return a
    return T


def shot_at(T):
    i = 0
    for j, e in enumerate(EDIT):
        if e[0] <= T:
            i = j
    return i


def mode_at(T, i=None):
    i = shot_at(T) if i is None else i
    t0, _, _, tints = EDIT[i]
    mode = tints[0][1]
    for t, m in tints:
        if (t if t > 1e-6 else t0) <= T:
            mode = m
    return mode

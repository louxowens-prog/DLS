"""The edit: every shot, when it starts, and how we get into it.

Transitions (the video mixer's): cut; star (a star wipe); curl (a page curl); cube (a spinning cube); checker; spin
(the old shot tumbles away); snap (a snap zoom into the new shot); hard (a hard cut into silence, played as a joke)."""
from common import E, S, Wx
from timeline import TL

# (start, shot, transition, transition length)
EDIT = [
    # ---- cold open: the phone, the freeze frame, the title
    (0.0, "phone", "cut", 0),
    (S("o2") - 0.12, "freeze1", "cut", 0),
    (E("o2") + 0.1, "title", "star", 0.45),
    # ---- 1: 1994, crayon
    (S("a1") - 0.3, "c1_kid", "curl", 0.55),
    (S("a2") - 0.2, "c1_screen", "cut", 0),
    (S("a4") - 0.1, "c1_sock", "snap", 0.2),
    (S("a5") - 0.1, "c1_eliza", "cut", 0),
    (Wx("a5", "understood") - 0.15, "c1_nothing", "cut", 0),
    (S("a6") - 0.1, "c1_secretary", "cut", 0),
    (S("a7") - 0.1, "c1_quote", "cut", 0),
    (E("a7") + 0.45, "c1_normal", "hard", 0),
    # ---- 2: paper
    (S("b1") - 0.5, "p_shapes", "cube", 0.5),
    (Wx("b1", "saw") - 0.1, "p_bully", "cut", 0),
    (S("b2") - 0.1, "p_words", "cut", 0),
    (Wx("b2", "brain") - 0.25, "p_someone", "cut", 0),
    (S("b3") - 0.1, "p_loop", "cut", 0),
    (Wx("b3", "plays") - 0.1, "p_loop2", "snap", 0.2),
    (S("b4") - 0.1, "p_capable", "cut", 0),
    (Wx("b4", "someone") - 0.3, "p_coauthor", "cut", 0),
    (S("b5") - 0.1, "p_ad", "checker", 0.4),
    # ---- 3: clay
    (S("c1") - 0.5, "k_cake", "curl", 0.5),
    (S("c2") - 0.1, "k_layers", "cut", 0),
    (Wx("c2", "company") - 0.15, "k_layers2", "cut", 0),
    (S("c3") - 0.1, "k_giant", "cut", 0),
    (Wx("c3", "preferred") - 0.25, "k_vote", "cut", 0),
    (S("c4") - 0.1, "k_shape", "cut", 0),
    (Wx("c4", "By") - 0.05, "k_rater", "snap", 0.2),
    # ---- 4: THE AGREEABLE HOUR, Flash
    (E("c4") + 0.1, "f_bumper", "spin", 0.45),
    (S("d2") - 0.1, "f_desk", "cut", 0),
    (S("d3") - 0.1, "f_metric", "cut", 0),
    (S("d4") - 0.1, "f_thumbs", "cut", 0),
    (S("d5") - 0.05, "f_affirma", "snap", 0.2),
    (S("d6") - 0.1, "f_mirror", "cut", 0),
    (Wx("d6", "people", 1) - 0.25, "f_raters", "cut", 0),
    (S("d8") - 0.1, "f_ask", "cut", 0),
    (S("d9") - 0.05, "f_brilliant", "snap", 0.15),
    (E("d9") + 0.75, "f_empty", "hard", 0),
    # ---- 5: MS Paint, then PS1
    (S("e1") - 0.5, "m_morals", "cube", 0.5),
    (Wx("e1", "practice") - 0.2, "m_rated", "cut", 0),
    (S("e2") - 0.1, "m_goodhart", "cut", 0),
    (S("e3") - 0.1, "m_list", "cut", 0),
    (Wx("e3", "Test") - 0.15, "m_list2", "cut", 0),
    (S("e4") - 0.1, "m_gamed", "cut", 0),
    (S("e5") - 0.1, "ps1_boat", "checker", 0.35),
    (Wx("e5", "fire") - 0.35, "ps1_fire", "cut", 0),
    # ---- 6: CHANNEL 99, VHS
    (E("e5") + 0.1, "v_bars", "cut", 0),
    (S("f1") + 0.35, "v_stage", "cut", 0),
    (S("f2") - 0.1, "v_family", "cut", 0),
    (S("f3") - 0.1, "v_confess", "cut", 0),
    (S("f4") - 0.1, "v_truth", "cut", 0),
    (Wx("f4", "someone") - 0.2, "v_truth2", "cut", 0),
    (S("f5") - 0.1, "v_argue", "cut", 0),
    (S("f6") - 0.1, "v_listener", "cut", 0),
    (Wx("f6", "human") - 0.25, "v_hand", "cut", 0),
    (S("f7") - 0.6, "v_joke", "cut", 0),
    (E("f9") + 0.35, "end", "star", 0.45),
]

TRANS = {"star", "curl", "cube", "checker", "spin"}


def shot_at(T):
    i = 0
    for j, e in enumerate(EDIT):
        if e[0] <= T:
            i = j
    return i

"""The edit: every shot, when it starts, how it is printed, and how we get into it.

Prints: real (the kitchen and the street: a gentler black and white), zone (the painted underworld: hard contrast),
card (the intertitles). colour: how much hand-tinted colour the shot keeps (the finale floods with it).
Transitions: cut, jump (a jump cut: same set-up, time skipped), iris (an iris closes on the old shot and opens on
the new), crash (a crash zoom into the new shot)."""
from cues import C, CARDS, SL, Wx
from timeline import TL

S, E = TL.s, TL.e

# (start, shot, print, transition, colour)
EDIT = [
    # the real world
    (0.0, "phone", "real", "cut", 0.0),
    (S("r1") - 0.15, "mae_phone", "real", "cut", 0.0),
    (S("r2") - 0.1, "slips", "real", "cut", 0.0),
    (Wx("r2", "every") - 0.1, "slips_b", "real", "jump", 0.0),
    (Wx("r2", "Then") - 0.1, "scan", "real", "jump", 0.0),
    (S("r3") - 0.1, "search", "real", "cut", 0.0),
    (S("r4") - 0.1, "hand", "real", "cut", 0.0),
    (E("r4") + 0.15, "fall", "zone", "iris", 0.0),
    (S("t1") - 0.35, "title", "zone", "crash", 0.0),
    # ROOM 1
    (CARDS[0][2], "card1", "card", "iris", 0.0),
    (S("a1") - 0.1, "hall", "zone", "cut", 0.0),
    (Wx("a1", "Some") - 0.15, "reader", "zone", "cut", 0.0),
    (S("s1") - 0.05, "s1_dance", "zone", "cut", 0.0),
    (SL("s1", 1) - 0.1, "s1_lung", "zone", "cut", 0.0),
    (SL("s1", 2) - 0.1, "s1_spot", "zone", "crash", 0.0),
    (SL("s1", 3) - 0.1, "s1_pair", "zone", "cut", 0.0),
    (S("a2") - 0.15, "masai", "zone", "cut", 0.0),
    (Wx("a2", "twenty-nine") - 0.25, "masai_b", "zone", "crash", 0.0),
    (Wx("a2", "false") - 0.25, "masai_c", "zone", "jump", 0.0),
    (E("a2") - 0.2, "masai_d", "zone", "jump", 0.0),
    (S("a3") - 0.1, "decides", "zone", "cut", 0.0),
    # ROOM 2
    (CARDS[1][2], "card2", "card", "iris", 0.0),
    (S("b1") - 0.1, "files", "zone", "cut", 0.0),
    (S("s2") - 0.05, "s2_rain", "zone", "cut", 0.0),
    (SL("s2", 1) - 0.1, "s2_day", "zone", "cut", 0.0),
    (SL("s2", 3) - 0.1, "s2_octo", "zone", "crash", 0.0),
    (S("b2") - 0.15, "clash", "zone", "cut", 0.0),
    # ROOM 3
    (CARDS[2][2], "card3", "card", "iris", 0.0),
    (S("c1") - 0.1, "record", "zone", "cut", 0.0),
    (S("s3") - 0.05, "s3_king", "zone", "cut", 0.0),
    (SL("s3", 1) - 0.1, "s3_iron", "zone", "cut", 0.0),
    (SL("s3", 2) - 0.1, "s3_cells", "zone", "cut", 0.0),
    (SL("s3", 3) - 0.1, "s3_heart", "zone", "cut", 0.0),
    (SL("s3", 4) - 0.1, "s3_fine", "zone", "cut", 0.0),
    (SL("s3", 5) - 0.1, "s3_all", "zone", "crash", 0.0),
    (S("c2") - 0.15, "evaluate", "zone", "crash", 0.0),
    (S("c3") - 0.15, "flagtool", "zone", "cut", 0.0),
    # ROOM 4
    (CARDS[3][2], "card4", "card", "iris", 0.0),
    (S("d1") - 0.1, "ballroom", "zone", "cut", 0.0),
    (S("s4") - 0.05, "s4_open", "zone", "cut", 0.0),
    (SL("s4", 1) - 0.1, "s4_sepsis", "zone", "jump", 0.0),
    (SL("s4", 2) - 0.1, "s4_kidney", "zone", "jump", 0.0),
    (SL("s4", 3) - 0.1, "s4_ecg", "zone", "jump", 0.0),
    (SL("s4", 4) - 0.1, "s4_eye", "zone", "jump", 0.0),
    (SL("s4", 5) - 0.1, "s4_roof", "zone", "cut", 0.0),
    (E("s4") - 0.2, "false_alarm", "zone", "cut", 0.0),
    (S("d3") - 0.15, "caveat", "zone", "cut", 0.0),
    (Wx("d3", "skin") - 0.35, "caveat_b", "zone", "jump", 0.0),
    (S("d4") - 0.1, "charge", "zone", "cut", 0.0),
    # ROOM 5
    (CARDS[4][2], "card5", "card", "iris", 0.0),
    (S("f1") - 0.1, "clinic", "zone", "cut", 0.0),
    (S("f2") - 0.1, "tunnel", "zone", "cut", 0.0),
    (C["flag"] - 0.1, "flag", "zone", "crash", 0.0),
    (S("f4") - 0.1, "doclook", "zone", "cut", 0.0),
    (S("f5") - 0.1, "halved", "zone", "cut", 0.0),
    (Wx("f5", "roughly") - 0.25, "halved_b", "zone", "crash", 0.0),
    (S("s5") - 0.05, "s5_found", "zone", "cut", 0.35),
    (S("f6") - 0.15, "doors", "zone", "cut", 0.0),
    # back through the door
    (S("g1") - 0.25, "door_back", "real", "iris", 0.0),
    (S("g2") - 0.15, "bus", "real", "cut", 0.62),
    (S("g3") - 0.1, "glasses", "real", "cut", 0.6),
    (S("g4") - 0.15, "curtain", "zone", "cut", 0.62),
    (S("g5") - 0.1, "screening", "zone", "cut", 0.45),
    (E("g5") + 0.6, "end", "card", "iris", 0.0),
]
IRIS = 0.32                                                             # seconds for an iris to close, and to open
# Dutch angles (degrees) on the wilder shots: the whole painted world hung off true
CANT = {"hall": 3, "s1_dance": -7, "s1_lung": 5, "s2_rain": 6, "s2_octo": -6, "s3_king": -5,
        "ballroom": -3, "s4_open": -6, "s4_roof": 5, "false_alarm": -8, "s5_found": 6}


def shot_at(t):
    cur = 0
    for i, e in enumerate(EDIT):
        if e[0] <= t:
            cur = i
    return cur


def first(name):
    return next(e[0] for e in EDIT if e[1] == name)


def nxt(name):
    i = next(k for k, e in enumerate(EDIT) if e[1] == name)
    return EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total

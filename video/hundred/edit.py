"""The edit: every shot, when it starts, and how we get into it.
Transitions: cut; crash (a crash zoom into the shot, on a jump-scare sting); flash (a frame of lightning on the cut)."""
from cues import C, E, S, Wx
from timeline import TL

# (start, shot, transition)
EDIT = [
    # cold open: an eye, the phone on the floor, the door with no number on any plan; the title; dead silence
    (0.0, "eye", "cut"),
    (C["sting1"], "floor", "crash"),
    (S("o3") - 0.1, "door100", "cut"),
    (C["title"], "title", "flash"),
    (C["dead1"], "black", "cut"),
    # the storm, the hotel, a year of right answers, the 99 keys and one more
    (S("p1") - 0.45, "exterior", "cut"),
    (S("p2") - 0.1, "checks", "cut"),
    (S("p3") - 0.05, "nocheck", "cut"),
    (S("p4") - 0.15, "lobby", "cut"),
    (C["key_desk"], "keydesk", "cut"),
    # RED: her room, 2 a.m.
    (S("r1") - 1.7, "clock", "flash"),
    (Wx("r1", "chest") - 0.1, "chestcu", "cut"),
    (Wx("r1", "sick") - 0.15, "bed", "cut"),
    (S("r2") - 0.1, "type", "cut"),
    (S("r3") - 0.05, "faceglow", "cut"),
    (S("r4") - 0.15, "answer", "cut"),
    (Wx("r4", "most") - 0.1, "answer2", "cut"),
    (S("r5") - 0.1, "relief", "cut"),
    (Wx("r5", "mistake") - 0.3, "lie2", "cut"),
    (S("r6") - 0.1, "scale", "cut"),
    (Wx("r6", "advice") - 0.1, "nb1", "cut"),
    (S("r7") - 0.1, "liewall", "cut"),
    # the stair, the corridor, ROOM 97 (blue)
    (E("r7") + 0.05, "spiral", "cut"),
    (S("b1") - 0.3, "corr97", "cut"),
    (S("b2") - 0.1, "blue", "flash"),
    (Wx("b2", "signs") - 0.1, "pen", "cut"),
    (S("b3") - 0.1, "papers", "cut"),
    (Wx("b3", "Fined") - 0.1, "fine", "cut"),
    (S("b4") - 0.1, "books", "cut"),
    (E("b4") - 1.0, "clutch", "cut"),
    (C["sting2"], "turn", "crash"),
    # ROOM 98 (green)
    (S("g1") - 0.4, "corr98", "cut"),
    (S("g2") - 0.1, "green", "cut"),
    (S("g3") - 0.1, "safe", "cut"),
    (S("g4") - 0.1, "drain", "cut"),
    (Wx("g4", "investment") - 0.1, "vault", "cut"),
    (S("g5") - 0.1, "norahall", "cut"),
    (Wx("g5", "Reflux") - 0.1, "nb2", "flash"),
    (E("g5") + 0.3, "storm2", "flash"),
    # ROOM 99 (magenta): the mirrors
    (S("m1") - 0.9, "mirrors", "flash"),
    (Wx("m2", "Automation") - 0.15, "bias", "cut"),
    (Wx("m2", "assume") - 0.1, "nb3", "cut"),
    (S("m3") - 0.1, "chart", "cut"),
    (C["sting3"], "stop", "crash"),
    (S("m4") - 0.2, "keymirror", "cut"),
    (C["dead2"], "seam", "cut"),
    # the hidden door; ROOM 100
    (S("h1") - 0.1, "keyhole", "cut"),
    (S("h2") - 0.1, "gridhalf", "cut"),
    (S("h3") - 0.1, "gridone", "cut"),
    (S("h4") - 0.1, "simulator", "cut"),
    (Wx("h4", "trusted") - 0.1, "nb4", "cut"),
    (Wx("h4", "failures") - 0.2, "dialcu", "cut"),
    (S("h5") - 0.1, "doorwide", "cut"),
    (S("h6") - 0.4, "room100", "cut"),
    (S("h7") - 0.1, "truth", "cut"),
    (S("x1") - 0.3, "rested", "cut"),
    (C["son"] + 0.1, "soncall", "cut"),
    (E("x1") + 1.4, "deathcu", "cut"),
    (C["dead3"], "black", "cut"),
    # the same night, once more; dawn
    (C["rewind"], "rewind", "cut"),
    (S("d1") + 0.9, "same", "cut"),
    (S("d2") - 0.1, "believe", "cut"),
    (S("d3") - 0.15, "dial", "cut"),
    (S("d4") - 0.1, "lips", "cut"),
    (C["siren"], "dawnout", "flash"),
    (S("d5") - 0.1, "hospital", "cut"),
    (S("d6") - 0.1, "aha", "cut"),
    (Wx("d6", "wait") - 0.2, "alive", "cut"),
    (S("e1") - 0.1, "emptyroom", "cut"),
    (S("e2") - 0.1, "three", "cut"),
    (Wx("e2", "When") - 0.1, "window", "cut"),
    (S("e3") - 0.1, "keysill", "cut"),
    (S("e4") - 0.5, "coda", "cut"),
    (C["sting5"], "eye2", "crash"),
    (C["sting5"] + 0.75, "end", "cut"),
]
CRASH = 0.22                                    # seconds of a crash zoom


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


if __name__ == "__main__":
    for i, (t, n, tr) in enumerate(EDIT):
        t1 = EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total
        print(f"{t:7.2f} {t1 - t:5.2f}  {n:10s} {tr}" + ("   <-- SHORT" if t1 - t < 0.5 else ""))

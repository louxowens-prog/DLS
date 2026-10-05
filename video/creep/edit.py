"""The edit: every shot, when it starts, how we get into it, and how the print treats it.

Transitions: cut; page (the old frame turns over like a comic page); zoom (the new shot grows out of a panel on a
page); flash / redflash (a frame or two burnt white or red). Looks: night (night-for-night), plain (the reader's real
night, drained of colour), black (fade to black), bolt (how much the lightning lifts the exposure)."""
from common import E, S, Wx
from timeline import TL

NIGHT = {"night": 0.55}
# (start, shot, transition, look)
EDIT = [
    # ---- cold open: the cover, the hook, the reader, the host
    (0.0, "o_cover", "cut", {}),
    (Wx("c1", "and") - 0.1, "o_scope", "zoom", {}),
    (Wx("c1", "finding") - 0.1, "o_noai", "cut", {}),
    (Wx("c1", "without") + 0.02, "o_noai_shock", "cut", {}),
    (S("c2") - 0.05, "o_window", "flash", NIGHT),
    (Wx("c2", "Welcome") - 0.08, "o_host", "cut", {"night": 0.3}),
    (S("c3") - 0.12, "o_muse", "cut", {"night": 0.2}),
    (S("c4") - 0.08, "o_nora", "cut", {"night": 0.2}),
    (S("c5") - 0.1, "o_skills", "page", {}),
    (S("c6") - 0.12, "o_before", "page", {}),
    (Wx("c6", "AI") - 0.08, "o_more", "cut", {}),
    # ---- tale 1: THE ROAD THAT FORGOT HER
    (S("v1") - 0.6, "v_title", "page", {}),
    (S("v2") - 0.15, "v_car", "zoom", NIGHT),
    (S("v4") - 0.1, "v_map", "cut", {}),
    (E("v4") + 0.12, "v_signal", "cut", NIGHT),
    (S("v6") - 0.1, "v_cross", "cut", {"night": 0.35}),
    (S("v7") - 0.1, "v_cabbie", "page", {}),
    (S("v8") - 0.1, "v_bones", "cut", {"night": 0.4}),
    (Wx("v8", "forever") - 0.05, "v_skull", "redflash", {}),
    # ---- tale 2: THE GHOST WRITER
    (S("g1") - 0.55, "g_title", "page", {}),
    (S("g2") - 0.15, "g_dorm", "zoom", {"night": 0.25}),
    (S("g3") - 0.1, "g_ghost", "cut", {"night": 0.25}),
    (Wx("g3", "Help") - 0.1, "g_split", "cut", {}),
    (S("g4") - 0.1, "g_quote", "cut", {"night": 0.2}),
    (S("g5") - 0.1, "g_chart", "page", {}),
    (E("g5") + 0.1, "g_exam", "cut", {}),
    (S("g7") - 0.08, "g_blank", "cut", {}),
    (S("g8") - 0.1, "g_puppet", "cut", {}),
    # ---- tale 3: THE SECOND OPINION
    (S("s1") - 0.55, "s_title", "page", {}),
    (S("s2") - 0.15, "s_clinic", "zoom", {}),
    (Wx("s2", "tested") - 0.1, "s_unplug", "cut", {}),
    (Wx("s2", "Detection") - 0.1, "s_stat", "cut", {}),
    (S("s3") - 0.06, "s_shout", "redflash", {}),
    (S("s4") - 0.1, "s_pilot", "page", NIGHT),
    (Wx("s5", "when") - 0.1, "s_warn", "cut", NIGHT),
    (S("s6") - 0.12, "s_years", "page", {}),
    (Wx("s6", "And") - 0.1, "s_ward", "cut", {"night": 0.2}),
    (S("s7") - 0.1, "s_junior", "cut", {"night": 0.2}),
    (E("s7") + 0.6, "s_thing", "redflash", {}),
    # ---- the reader: the risk at 100%
    (S("r1") - 0.5, "r_dark", "cut", {"night": 0.6}),
    (S("r2") - 0.12, "r_real", "cut", {"plain": 0.9}),
    (S("r3") - 0.08, "r_father", "cut", {"plain": 0.85}),
    (Wx("r3", "You") - 0.1, "r_pill", "cut", {"plain": 0.85}),
    (Wx("r3", "The", 1) - 0.08, "r_door", "cut", {"plain": 0.9}),
    (Wx("r3", "Your", 1) - 0.08, "r_number", "cut", {"plain": 0.85}),
    (S("r4") - 0.1, "r_muse", "cut", {"plain": 0.8}),
    (S("r5") - 0.15, "r_pocket", "cut", {"plain": 0.35}),
    (Wx("r5", "It's") - 0.06, "r_point", "cut", {}),
    # ---- the moral, the host, the back page
    (S("m1") - 1.0, "m_close", "cut", {"night": 0.2}),
    (S("m2") - 0.12, "m_habits", "page", {}),
    (S("m3") - 0.12, "m_tutor", "cut", {}),
    (S("m4") - 0.1, "m_host", "flash", {}),
    (E("m4") + 0.3, "m_back", "page", {}),
]

TRANS = {"page": 0.55, "zoom": 0.5, "flash": 0.1, "redflash": 0.12}

# shots that are comic pages already (everything else is 'live' and freezes into a panel before a page turn)
PAGES = {"o_cover", "o_skills", "o_before", "v_title", "v_map", "v_cabbie", "g_title", "g_split", "g_chart", "s_title", "m_habits", "m_back"}
FREEZE_D = 0.5

# lightning strikes: (time, strength); the score puts a thunder crack on each
LIGHTNING = [(0.02, 0.9), (2.1, 0.5), (S("c2") - 0.04, 0.85), (Wx("c2", "Lose") - 0.02, 0.5), (S("v1") - 0.55, 0.6),
             (Wx("v8", "forever") - 0.04, 0.8), (S("g1") - 0.5, 0.6), (S("s1") - 0.5, 0.6), (Wx("s5", "quit") - 0.05, 0.9),
             (E("s7") + 0.58, 1.0), (S("r5") + 0.4, 0.35), (Wx("m4", "Ahahahaha") - 0.03, 0.9), (Wx("m4", "Ahahahaha") + 0.45, 0.6)]

# colour shocks: the background drops to one flat colour (the score puts a stinger on each)
SHOCKS = [(Wx("c1", "without") + 0.02, "green"), (Wx("c6", "AI") - 0.08, "blue"), (Wx("v8", "forever") - 0.05, "red"),
          (S("g7") - 0.08, "green"), (S("s3") - 0.06, "red"), (E("s7") + 0.6, "red"), (S("m4") - 0.1, "violet")]

# the reader's real night: the narrator's boxes go plain
PLAIN = [(S("r2") - 0.2, S("r5") - 0.1)]


def shot_at(T):
    i = 0
    for j, e in enumerate(EDIT):
        if e[0] <= T:
            i = j
    return i


def look_at(T, i):
    return EDIT[i][3]


# speech balloons for the characters' lines: position, tail (the speaker's mouth), kind
BALLOONS = {
    "c3": dict(x=560, y=470, tail=(700, 900), maxw=520),
    "c4": dict(x=470, y=420, tail=(560, 760), maxw=480),
    "v2": dict(x=600, y=420, tail=(820, 860), maxw=500),
    "v3": dict(x=420, y=380, tail=(470, 700), maxw=520),
    "v5": dict(x=540, y=380, tail=(540, 760), maxw=480, size=56),
    "v6": dict(x=480, y=400, tail=(520, 720), maxw=480, kind="shout", shake=2.0),
    "g2": dict(x=330, y=330, tail=(440, 560), maxw=420),
    "g6": dict(x=370, y=330, tail=(620, 560), maxw=460),
    "g7": dict(x=330, y=330, tail=(430, 520), maxw=420, kind="whisper", shake=3.0),
    "s3": dict(x=520, y=380, tail=(540, 720), maxw=520, kind="shout", shake=3.0, size=54),
    "s7": dict(x=520, y=380, tail=(560, 720), maxw=480, kind="whisper"),
    "r1": dict(x=700, y=1330, tail=(600, 1150), maxw=400),
    "r4": dict(x=310, y=330, tail=(430, 520), maxw=400, kind="whisper"),
    "m5": dict(x=440, y=1170, tail=(790, 1190), maxw=500, size=44, until=TL.total - 0.3),
}

"""Named moments the picture and the soundtrack both hit, and who is talking when (for the mouths)."""
import math

from timeline import TL

S, E, W = TL.s, TL.e, TL.word


def ls(k):
    """Start of lyric line k (e.g. 's1_2')."""
    return TL.lines[k]["start"]


def Wx(key, word, nth=0):
    """Start of the nth word that is exactly `word`."""
    hits = [a for w, a, b in TL.lines[key]["words"] if w == word]
    return hits[min(nth, len(hits) - 1)]


def talk(who, T):
    """How open a speaker's mouth is at T (0..1), flapping on the syllables of their current word."""
    for k in TL.order:
        L = TL.lines[k]
        if L["who"] == who and L["start"] - 0.02 <= T <= L["end"]:
            for w, a, b in L["words"]:
                if a <= T <= b:
                    return 0.35 + 0.65 * abs(math.sin((T - a) / max(0.08, (b - a)) * math.pi * max(1, len(w) // 3)))
            return 0.0
    return 0.0


C = {
    "doors": W("c0", "Three"),
    "glow": S("c1") + 0.4,
    "ticket_flash": W("b1", "golden") - 0.2,
    "you_bring": W("b2", "You"),
    "h_better": W("n2", "Forty"),
    "h_faster": Wx("n2", "Forty", 1) if len([w for w, a, b in TL.lines["n2"]["words"] if w == "Forty"]) > 1 else W("n2", "faster!"),
    "h_beginners": W("n2", "beginners"),
    "door_open": E("g3") + 0.35,
    "gulp": S("k1") + 0.9,
    "gulp_up": E("k1") + 0.2,
    "fifty_in": S("r2"),
    "six_out": W("r2", "six"),
    "disagree": W("r2", "disagree."),
    "searching": S("r2b"),
    "thinking": W("r2b", "thinking."),
    "sip": S("k2") + 0.6,
    "sucked": E("k2") + 0.1,
    "against": W("r3", "against"),
    "hole": W("r3", "hole"),
    "youre_right": S("k3b"),
    "shrink": E("k3b") + 0.05,
    "what_else": S("r4"),
    "wait": W("r4", "wait?"),
    "pop": W("r4", "pop,"),
    "plan": W("r4", "plan,"),
    "three_q": W("r4", "three"),
    "grab": S("k4") + 0.2,
    "drop": E("k4") + 0.1,
    "right_q": W("p2", "exactly"),
    "flip": S("x3"),
    "suggested": W("y1", "suggested"),
    "agreed": W("y2", "agreed."),
}

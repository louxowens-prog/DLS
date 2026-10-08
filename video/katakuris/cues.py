"""Named moments the picture and the soundtrack both hit."""
from timeline import TL

S, E, W = TL.s, TL.e, TL.word


def ls(k):
    """Start of lyric line k (e.g. 's1_2')."""
    return TL.lines[k]["start"]


def Wx(key, word):
    """Start of the first word that is exactly `word`."""
    return next(a for w, a, b in TL.lines[key]["words"] if w == word)


def gap(key, word):
    """A scare hit's slot: in the pause just before `word` (the previous word has ended; the next is still ~0.25 s off)."""
    ws = TL.lines[key]["words"]
    i = next(j for j, (w, a, b) in enumerate(ws) if w == word)
    return max(ws[i - 1][2] + 0.04, ws[i][1] - 0.3) if i > 0 else ws[i][1] - 0.3


C = {
    "fraud_count": W("c0", "forty"),
    "pop": W("c0", "Most") + 0.1,
    "dontask": W("a1", "Don't"),
    "stamp": W("a2", "stamped"),
    "tuesday": W("a2", "Tuesday."),
    "tenmil": W("b1", "Ten"),
    "millions": gap("b2", "Millions."),
    "no_human": gap("d2", "No"),
    "rule_right": W("b3", "right,"),
    "rule_wrong": W("b3", "wrong."),
    "fraud_letter": W("d2", "fraud."),
    "penalty": gap("d3", "Plus"),
    "interest": W("d3", "interest."),
    "refund": W("d4", "tax"),
    "nothing": S("d4b"),
    "forty": gap("d5", "An"),
    "eightyfive": gap("d5", "About"),
    "robodebt": gap("d6", "Australia's"),
    "erupt": S("e1") - 0.7,
    "billion": W("e1", "billion"),
    "point": gap("e1", "Point"),
    "onemil": gap("e1", "One"),
    "failures": W("e1", "failures."),
    "attack": S("f1c") - 0.25,
    "arrested": W("f1c", "arrested."),
    "even_one": W("f2", "one."),
    "sensor": W("f3", "sensor,"),
    "nose": W("f3", "nose"),
    "p346": S("f3b"),
    "impact_plane": E("f3") + 0.2,
    "impact_missile": E("f5") + 0.2,
    "alarms": W("f4", "alarms."),
    "p50": S("f4b") - 0.25,
    "drift": W("f5", "drifted"),
    "p28": S("f5b"),
    "p6": S("f6b") - 0.25,
    "scale": W("g1", "scale,"),
    "stakes": W("g1", "stakes,"),
    "smaller": W("g1", "smaller"),
    "yours": W("g2", "yours."),
}

"""Named moments the picture and the soundtrack both hit."""
from timeline import TL

S, E, W = TL.s, TL.e, TL.word


def ls(k):
    """Start of lyric line k (e.g. 's1_2')."""
    return TL.lines[k]["start"]


C = {
    "fraud_count": W("c0", "forty"),
    "pop": W("c0", "It") + 0.1,
    "dontask": W("a1", "Don't"),
    "stamp": W("a2", "stamped"),
    "tuesday": W("a2", "Tuesday."),
    "tenmil": W("b1", "Ten"),
    "millions": W("b2", "Millions."),
    "rule_right": W("b3", "right,"),
    "rule_wrong": W("b3", "wrong."),
    "fraud_letter": W("d2", "fraud."),
    "penalty": W("d3", "four"),
    "interest": W("d3", "interest."),
    "refund": W("d4", "tax"),
    "nothing": W("d4", "You", 1),
    "forty": W("d5", "forty"),
    "eightyfive": W("d5", "eighty-five"),
    "robodebt": W("d6", "Australia's"),
    "billion": W("e1", "billion"),
    "onemil": W("e1", "million."),
    "failures": W("e1", "failures."),
    "attack": W("f1", "attack"),
    "arrested": W("f1", "arrested."),
    "even_one": W("f2", "one."),
    "sensor": W("f3", "sensor,"),
    "nose": W("f3", "nose"),
    "p346": W("f3", "hundred") - 0.22,
    "alarms": W("f4", "alarms."),
    "p55": W("f4", "Fifty-five"),
    "drift": W("f5", "drifted"),
    "p28": W("f5", "Twenty-eight"),
    "p6": W("f6", "six"),
    "scale": W("g1", "scale,"),
    "stakes": W("g1", "stakes,"),
    "smaller": W("g1", "smaller"),
    "yours": W("g2", "yours."),
}

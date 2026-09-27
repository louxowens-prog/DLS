"""Named moments the picture and the soundtrack both hit."""
from script import WRONG_PER_SEC
from timeline import TL

S, E, W = TL.s, TL.e, TL.word


def count(T):
    """The cuckoo clock's reading: confident wrong answers since you pressed play (at one in a hundred)."""
    return WRONG_PER_SEC * max(0.0, T)


C = {
    "eaten": S("h2") - 0.08,
    "items": [W("l1", w) for w in ("Made-up", "Fake", "Wrong", "Invented", "Bad", "history", "Broken", "Citations", "Documents")],
    "fake_hist": W("l1", "Fake", 1),
    "reels": W("w1", "the"),
    "ticket": W("w1", "And"),
    "star": W("w2", "over"),
    "yes": W("c1", "yes."),
    "gavel": E("c1") + 0.05,
    "pile": S("c2") + 0.9,
    "pay": W("c3", "The"),
    "typed": W("p2", "So"),
    "bromide": W("p3", "bromide!"),
    "nowarn": S("p4"),
    "neighbor": S("p7"),
    "see": W("p7", "see"),
    "hear": W("p7", "hear"),
    "hold": W("p8", "They"),
    "level": W("p9", "two"),
    "real": S("p11"),
    "atonce": W("s2", "millions"),
    "second": W("s4", "Almost"),
    "clock": W("s5", "clock?"),
    "now": W("r1", "as"),
    "trust": S("e2"),
    "end": E("e2") + 0.35,
}
C["items"][5] = C["fake_hist"]

"""Named moments the picture and the soundtrack both hit, and the word-level lookups."""
from timeline import TL

S, E = TL.s, TL.e


def Wx(key, word, nth=0):
    """Start of the nth word containing `word` (case-insensitive) in a line."""
    hits = [a for w, a, b in TL.lines[key]["words"] if word.lower() in w.lower()]
    return hits[min(nth, len(hits) - 1)] if hits else S(key)


def words_upto(key, T):
    """How many words of a line have begun by time T."""
    return sum(1 for w, a, b in TL.lines[key]["words"] if a <= T)


C = {
    "sting1": S("o2") - 0.08,                   # the phone on the floor, crash zoom
    "title": E("o3") + 0.12,                    # the title crashes in with the score
    "dead1": S("p1") - 1.25,                    # dead silence after the title
    "storm": Wx("p1", "storm"),                 # lightning on "A storm"
    "key_desk": S("p5") - 0.25,
    "sting2": E("b4") + 0.45,                   # the man at the desk turns his head (after a held breath)
    "sting3": E("m3") + 0.1,                    # the reflection that stops nodding
    "dead2": E("m4") + 0.25,                    # dead silence: the seam of the hidden door
    "door_open": E("h5") + 0.15,                # the hidden door opens: blazing colour, the score crashes in
    "sting4": Wx("h6", "own"),                  # her own body on the bed
    "flat": E("x1") + 1.0,                      # the heartbeat stops
    "dead3": E("x1") + 1.6,                     # dead silence, black
    "rewind": S("d1") - 1.3,
    "siren": E("d4") + 0.2,
    "sting5": E("e4") + 0.15,                   # the phone that lit up by itself
}

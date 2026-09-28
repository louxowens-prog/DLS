"""Write build/transcript.txt: every line, every song and lyric, the captions, the edit, and where each device is."""
import os

import ov
from cues import C
from edit import EDIT, NEWSREEL, TRANS, first
from script import ROOMS, SONGS
from timeline import TL

HERE = os.path.dirname(os.path.abspath(__file__))
S, E = TL.s, TL.e


def main():
    out = ["THE THINKING FACTORY - 'Extending human intelligence' (a 1971-style factory-tour musical; style only)", ""]
    out += ["LINES (start-end, speaker, text)"]
    for k in TL.order:
        L = TL.lines[k]
        out.append(f"{L['start']:7.2f}-{L['end']:7.2f}  {L['who']:8s} {L['spoken']}")
    out += ["", "SONGS (karaoke lyrics with a colour wipe; half-sung by text-to-speech on the beat)"]
    for sk, Sg in TL.songs.items():
        out.append(f"  {sk} {Sg['style']} {Sg['bpm']} bpm  {Sg['start']:.2f}-{Sg['end']:.2f}")
        for l in Sg["lines"]:
            L = TL.lines[l["key"]]
            out.append(f"     {L['start']:7.2f}  {L['who']:8s} {L['shown']}")
    out += ["", "CAPTIONS"]
    for t0, t1, text, key in ov.CAPS:
        out.append(f"{t0:7.2f}-{t1:7.2f}  {text}")
    out += ["", "EDIT (start, length, shot, transition in): cut; dissolve; iris = a black iris closes and opens; "
                "leader = film-leader countdown into the newsreel"]
    for i, (t, n, tr) in enumerate(EDIT):
        nx = EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total
        out.append(f"{t:7.2f}  {nx - t:5.2f}s  {n:14s} {tr}{'  (black-and-white newsreel)' if n in NEWSREEL else ''}")
    f = first
    out += ["", "WHERE THE DEVICES ARE",
            f"  THE TWO WORLDS: the grey rainy industrial town {f('town'):.1f}-{f('news1'):.1f} (you in a yellow raincoat, the only colour);"
            f" the great door opens slowly in dead silence {f('door'):.1f}, onto the candy wonderland {f('wonder_wide'):.1f}"
            f" (sugar hills, lollipop trees, candy mushrooms, a chocolate river and waterfall; a slow pull-back from one flower to the"
            f" whole place, then the river, a tracking shot past giant candy canes, the guests at a giant lollipop and a sugar rose)",
            f"  THE HOST: gentle welcome in rhyme {S('g1'):.1f}; the rule {S('g2'):.1f}; quietly menacing {S('g3'):.1f}; "
            f"a rhyme at every room door; the tunnel {f('tunnel'):.1f}; rage {S('x1'):.1f}; warm {S('x2'):.1f}",
            "  THE ROOMS (one invention each, each a chapter, the uses on a brass door plaque): " +
            "; ".join(f"{n} {ROOMS[n][0]} {f('plaque' + str(n)):.1f}" for n in ROOMS),
            f"  GOLDEN TICKET (the motif): found in a wrapper {f('wrapper'):.1f}; 'Admit one mind. Bring a question.' {f('ticket'):.1f}; "
            f"in every guest's hand at the gates {f('gates'):.1f}; flips to 'NO LIMIT' {C['flip']:.1f}; the end card {f('end'):.1f}",
            f"  THE GUESTS, dealt with: the Copier inflates and floats away {C['gulp']:.1f}; the Believer is sucked up a pipe "
            f"{C['sucked']:.1f}; the Yes-Man shrinks {C['shrink']:.1f}; the Rusher drops down a trapdoor chute {C['drop']:.1f}",
            "  THE WORKERS' CHANTS (small identical light-bulb workers; a verse, then the same refrain every time: "
            "'Think it through, think it through; the thinking's up to you!'): " +
            ", ".join(f"{sk} {TL.songs[sk]['start']:.1f}" for sk in ('w1', 'w2', 'w3', 'w4')),
            f"  THE NIGHTMARE TUNNEL: {f('tunnel'):.1f}-{E('t1c'):.1f} strobing rings, projected fake citation / invented number / "
            f"'I never said that' / an eye / a spinning clock, the host reciting faster and faster; dead silence; calm {S('t2'):.1f}",
            f"  THE NEWSREEL: {f('news1'):.1f}-{f('gates'):.1f} (black and white, film leader, spinning headlines, two re-enacted interviews)",
            "  1971 FILM LOOK: warm soft Technicolor-like grade, clumpy grain, red-orange halation, gate weave, flicker, dust, "
            "hairs and scratches, vignette; slow 70s zooms; iris and dissolve transitions; painted flats",
            f"  TONE WHIPLASH: the host explodes {S('x1'):.1f}, dead silence, then the warm reveal {S('x2'):.1f}",
            f"  THE REAL-LIFE SCENARIO AT 100%: your dad (on metformin, numb feet) and his letter: at the kitchen table "
            f"{f('kitchen'):.1f}; the letter goes through every room ({f('room1'):.1f}-{f('rusher'):.1f}); the appointment with "
            f"the question on one page {f('clinic'):.1f}; the outcome (B12 low, supplement, walking by spring) {f('dad_home'):.1f}; "
            f"the true story (TODAY, 2023) {f('cold_kitchen'):.1f} and {f('story1'):.1f}",
            f"  THE THIRTEEN USES: each is stamped on screen with a running count (USE n OF 13) as it is acted out in the rooms "
            f"{f('room1'):.1f}-{f('room4_plan'):.1f}; also on each room's door plaque; the newsreel interviews are tagged with theirs",
            f"  THE BALLAD: {TL.songs['s1']['start']:.1f} (harp, strings, celesta, choir); the march {f('news1'):.1f}; "
            f"the tunnel cue {f('tunnel_in'):.1f}",
            "  SILENCES (every bus cut): the door, after the tunnel, after the host's outburst",
            "  RECURRING CUE: the same four-note music-box phrase each time a guest is dealt with",
            f"\nTOTAL {TL.total:.2f} s"]
    path = os.path.join(HERE, "build", "transcript.txt")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write("\n".join(out) + "\n")
    print(path)


if __name__ == "__main__":
    main()

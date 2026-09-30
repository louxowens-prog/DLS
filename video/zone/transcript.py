"""Write build/transcript.txt: every line and lyric, the captions, the edit with prints and transitions, and where
each device of the brief is."""
import os

import ov
from audio import SILENCES
from cues import C, CARDS, SL
from edit import EDIT, first
from timeline import TL

HERE = os.path.dirname(os.path.abspath(__file__))
S, E = TL.s, TL.e


def main():
    f = first
    out = ["THE SECOND LOOK - 'Medicine and healthcare' (AI as a second pair of eyes, and earlier detection) as a medical "
           "vaudeville in five rooms, in the style of an early-80s black-and-white midnight musical (style only: no "
           "characters, names, plot, dialogue, songs, music, sets or title design from the film; no caricature, nudity or "
           "violence)", ""]
    out += ["LINES (start-end, speaker, text; song lines are keyed sN_i and sung/chanted in strict time)"]
    for k in TL.order:
        L = TL.lines[k]
        out.append(f"{L['start']:7.2f}-{L['end']:7.2f}  {L['who']:7s} {L['shown']}")
    out += ["", "SONGS (start-end, style, bpm)"]
    for k, Sg in TL.songs.items():
        out.append(f"  {k}: {Sg['start']:.2f}-{Sg['end']:.2f} {Sg['style']} {Sg['bpm']} bpm - lyrics printed in the picture "
                   f"with a bouncing ball, no caption")
    out += ["", "CAPTIONS (spoken lines only)"]
    for t0, t1, text, key in ov.CAPS:
        out.append(f"{t0:7.2f}-{t1:7.2f}  {text}")
    out += ["", "EDIT (start, length, shot, print, transition in, hand-tint colour). Prints: real = the real world (gentler "
                "black and white); zone = the painted underworld (hard contrast); card = the hand-lettered intertitles. "
                "Transitions: cut; jump (jump cut); iris (iris out/in); crash (crash zoom)."]
    for i, (t, n, reg, tr, col) in enumerate(EDIT):
        nx = EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total
        out.append(f"{t:7.2f}  {nx - t:5.2f}s  {n:12s} {reg:5s} {tr:6s} {col:.2f}")
    out += ["", "WHERE THE DEVICES ARE",
            f"  THE REAL-LIFE SCENARIO, played literally: Mae, 56, feels fine; ten years of 'normal' blood tests; a computer "
            f"reads all ten at once (phone 0.0, slips {f('slips'):.1f}, scan {f('scan'):.1f}); her decade in Room 3 "
            f"({f('record'):.1f}-{f('flagtool'):.1f}): blood count slipping, iron pills for 'tired', 4 kg lost, pulse rising; "
            f"'evaluate now' {C['evaluate']:.1f}; her colonoscopy in Room 5 ({f('clinic'):.1f}): 'all clear so far', silence, "
            f"the AI flags a flat growth hiding in a fold {C['flag']:.1f}; found early, stage one; a year later she is back "
            f"driving her school bus in colour {f('bus'):.1f}",
            f"  THE DOORWAY: the pantry door creaks open {C['door_open']:.1f}; a white glove beckons with her glasses; the "
            f"iris and the spiral fall {f('fall'):.1f}; back out through the same door {f('door_back'):.1f}",
            "  FIVE ROOMS, each opened by a hand-lettered intertitle with an iris: " +
            "; ".join(f"ROOM {c[0]} {c[1]} at {c[2]:.1f}" for c in CARDS),
            "  A MUSICAL NUMBER PER ROOM (patter/chant, lyrics on screen with a bouncing ball): " +
            "; ".join(f"{k} {Sg['style']} {Sg['start']:.1f}" for k, Sg in TL.songs.items()),
            f"  THE RECURRING OBJECT: Mae's reading glasses (the 'second pair of eyes'): she can't find them {f('search'):.1f}; "
            f"the glove dangles them {f('hand'):.1f}; they fall ahead of her {f('fall'):.1f}; on the Second Eye (the AI) in "
            f"Room 1, the octopus librarian in Room 2, the Eye again in Rooms 3-5; on each room card; the pay-off: 'And I "
            f"found my glasses' - she pushes them up and winks {f('glasses'):.1f}",
            f"  LIVE ACTORS MATTED INTO PAINTED SETS (soft shading, a pale matte fringe): Mae, the Emcee (top hat and tails), "
            f"the doctors; CARTOON CAST (inked, rubber-hose, on twos): the Second Eye, the skeleton chorus line, the octopus "
            f"librarian, King Hemoglobin (royalty, painted red), dancing pills, the bathroom scale, the metronome heart, the "
            f"Alarm Rooster, Her Majesty the Early Bird",
            f"  HAND-TINTED COLOUR: the red ring round the speck {C['spot']:.1f}; the golden page {C['page']:.1f}; the red CLASH "
            f"{C['clash']:.1f}; King Hemoglobin and the heart; the red trend lines and stamps; the green AI box {C['flag']:.1f}; "
            f"the finale floods with colour {f('bus'):.1f}-{f('end'):.1f}",
            "  SILENCES (gags, >1 s, everything cut dead): " + "; ".join(f"{a:.1f}-{b:.1f}" for a, b in SILENCES) +
            " - after the rooster's false alarm, and in the tunnel before the flag",
            "  SOUND: real world = room tone, a clock, birds, the phone buzzing, a door creak, street and children; the "
            "underworld = a synthesized house band: hot jazz (tuba two-beat, banjo, stride piano, muted wah-wah trumpet, "
            "clarinet runs, brushes), ska (off-beat skank, organ, walking bass, trumpet and sax unison), a slow drag, new wave "
            "(driving eighth bass, combo organ, claps, horn stabs), a big-band shout chorus; scat hooks; a cartoon effect on "
            "every hit (slide whistle, boing, bike horn, xylophone runs, woodblocks, pops, cymbals, stamps); voices echo in "
            "the underworld, dry in the kitchen; the band plays on, muffled, behind the pantry door at the end",
            f"\nTOTAL {TL.total:.2f} s"]
    path = os.path.join(HERE, "build", "transcript.txt")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write("\n".join(out) + "\n")
    print(path)


if __name__ == "__main__":
    main()

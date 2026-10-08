"""Write build/transcript.txt for review: lines, songs, captions/lyrics, the edit, and where each device happens."""
import os

from cues import C
from edit import EDIT, HORROR, first
from script import LINES
from timeline import TL

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    import ov
    out = ["LINES (start-end, key, speaker, text). NAR = af_bella (young, deadpan narrator); MAMA = af_heart; "
           "MACH = am_michael through a metallic comb + echo (the claims machine)"]
    for k in TL.order:
        L = TL.lines[k]
        tag = f" [song {L['song']}]" if L["song"] else ""
        out.append(f"{L['start']:7.2f}-{L['end']:7.2f}  [{k}] {L['who']:4s} {L['shown']}{tag}")
    out += ["", "SONGS (karaoke: two-row lyric band with a colour wipe that follows the half-spoken words; count-in dots;"
            " the song title card; NO captions during songs)"]
    for k, S in TL.songs.items():
        out.append(f"  {k}: {S['style']:6s} {S['bpm']} bpm  {S['start']:.2f}-{S['end']:.2f}  lines at "
                   + ", ".join(f"{TL.lines[l['key']]['start']:.2f}" for l in S["lines"]))
    out += ["", "CAPTIONS (TV telop style; yellow/red in the horror shots)"]
    for t0, t1, text, key in ov.CAPS:
        out.append(f"{t0:7.2f}-{t1:7.2f}  {text}")
    out += ["", "EDIT (start, length, shot, transition in): cut; flash = white flash + crash zoom into horror; star = star wipe;"
            " spin = frame tumbles away; card = variety-show chapter card"]
    for i, (t, n, tr) in enumerate(EDIT):
        nx = EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total
        out.append(f"{t:7.2f}  {nx - t:5.2f}s  {n:11s} {tr}{'  (horror)' if n in HORROR else ''}")
    f = first
    out += ["", "WHERE THE DEVICES ARE",
            f"  MUSICAL NUMBERS (karaoke): sweet sing-along s1 {TL.s('s1'):.1f}; dream duet s2 {TL.s('s2'):.1f}; macabre disco of the"
            f" dead s3 {TL.s('s3'):.1f} (bodies rise from the garden graves {f('disco_a'):.1f} and dance in formation {f('disco_b'):.1f});"
            f" showtune finale s4 {TL.s('s4'):.1f}",
            f"  CLAYMATION (lumpy clay, fingerprints, tool gouges, on twos = 12 fps, boiling): FRAUD envelopes {0:.1f}, the little"
            f" error {C['pop']:.1f}, crow {f('crowsign'):.1f}, the flood of clay claims {f('flood'):.1f}, graves {f('graves'):.1f},"
            f" conveyor {f('same'):.1f}, clay numbers {f('owe'):.1f}, clay hands {f('take'):.1f}, maps {f('michigan'):.1f}/{f('homes'):.1f},"
            f" volcano {f('volcano'):.1f}, corpses {f('disco_a'):.1f}, the four disasters {f('plane'):.1f}-{f('card6'):.1f}, payoff {f('payoff'):.1f}",
            f"  SURREAL CLAY CREATURE: pops out of nowhere {C['pop']:.1f}; returns {f('disco_d'):.1f}, {f('finale_c'):.1f}, and giant at the end {f('payoff'):.1f}",
            f"  GUESTHOUSE / MEADOW / VOLCANO / RAINBOW: {f('family'):.1f}, {f('song1a'):.1f}; spinning arms-out meadow moment {f('finale_b'):.1f}",
            "  EARLY-2000s LOOK: oversaturated, blooming, over-lit video with smeared DV chroma and edge sharpening (no film grain);"
            " family keyed in with green spill haloes; plastic spinning CG stars, lens flares, chrome WordArt, a CG mirror ball",
            f"  DEADPAN BLACK COMEDY: the family shovels graves {f('graves'):.1f}, digs on the beat {f('disco_c'):.1f}, shrugs {f('ads'):.1f}",
            f"  TONE WHIPLASH: sitcom -> dream duet {f('duet'):.1f} -> dead silence + volcano {f('volcano'):.1f} -> disco {f('disco_a'):.1f}",
            f"  MOTIF: the guestbook - page one, one red X {f('book1'):.1f}; the same X again and again {f('finale_c'):.1f}; a mountain of"
            f" guestbooks with YOUR name on the next line {f('payoff'):.1f}",
            f"  CHAPTER CARDS: " + ", ".join(f"{t:.1f}" for t, n, tr in EDIT if tr == "card"),
            f"  DEAD AIR (every bus cut, >1 s): after 'You did nothing wrong', after the duet, after 'can't afford even one'",
            f"  SCARE HITS (every one lands in a pause between words; peak >= 7 dB and 50 ms RMS >= 8 dB above the neighbouring"
            f" dialogue): " + ", ".join(f"{t:.2f}" for t in _hits()),
            f"  THE DISASTER STING: a record scratch cuts the duet off {TL.e('s2'):.1f}; dead air over the still volcano; it erupts on"
            f" a thunder + timpani + cymbal + scare-hit sting {C['erupt']:.1f}, before a word is said",
            f"  THE SPIN: a close hero shot, the camera whip-panning round with her {f('finale_b'):.1f}",
            f"  RECURRING CUE (crow's caw): {C['pop'] + 0.6:.1f}, {C['dontask'] + 0.35:.1f}, {f('graves') + 0.3:.1f}, {C['fraud_letter']:.1f},"
            f" {TL.e('s3') - 0.6:.1f}, {f('payoff') + 1.1:.1f}",
            f"\nTOTAL {TL.total:.2f} s"]
    path = os.path.join(HERE, "build", "transcript.txt")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write("\n".join(out) + "\n")
    print(path)


def _hits():
    import audio
    hits = []
    audio.sfx(audio.Bus(), hits)
    return sorted(h[0] for h in hits)


if __name__ == "__main__":
    main()

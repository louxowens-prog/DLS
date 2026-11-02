"""Write build/transcript.txt: every line, the captions, the edit with its transitions, and where each device of the
brief happens."""
import os

import ov
from audio import CRASHES, SILENCES
from cues import C, E, S, Wx
from edit import EDIT, first
from timeline import TL

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    f = first
    out = ["THE HUNDREDTH ROOM - 'People may trust AI too much' as an adult Technicolor horror film in the style of a "
           "1977 Italian supernatural horror classic (style only: no characters, names, plot, dialogue, music, sets, "
           "locations or title design from the film; no gore, torture, self-harm, sexual content or animal cruelty)", ""]
    out += ["LINES (start-end, speaker, text). Speakers: N narrator (low, close, whispering woman); AI the Voice of the "
            "assistant (smooth, warm, certain); W the whisperer (a sinister breath that answers the narrator); NORA; DISP "
            "the emergency dispatcher (heard down the phone line); DOC the doctor"]
    for k in TL.order:
        L = TL.lines[k]
        out.append(f"{L['start']:7.2f}-{L['end']:7.2f}  {L['who']:5s} {L['shown']}")
    out += ["", "CAPTIONS (each speaker in their own style: narrator white; the AI ice-blue with a glowing dot; the "
                "whisperer crimson italic; Nora amber)"]
    for t0, t1, text, key in ov.CAPS:
        out.append(f"{t0:7.2f}-{t1:7.2f}  {text}")
    out += ["", "EDIT (start, length, shot, transition in). Transitions: cut; crash (crash zoom, on a jump-scare sting); "
                "flash (lightning on the cut)"]
    for i, (t, n, tr) in enumerate(EDIT):
        nx = EDIT[i + 1][0] if i + 1 < len(EDIT) else TL.total
        out.append(f"{t:7.2f}  {nx - t:5.2f}s  {n:11s} {tr}")
    out += ["", "WHERE THE DEVICES ARE",
            f"  THE REAL-LIFE SCENARIO, with the risk at 100%: Nora, 49, alone on a business trip in an old hotel in a "
            f"storm; her AI has been right all year (flights, emails, taxes, her son's fever: {f('checks'):.1f}), so she "
            f"stopped checking ({f('nocheck'):.1f}). 2:07 a.m. ({f('clock'):.1f}): tight chest, aching jaw, nausea, cold "
            f"sweat - the American Heart Association's typical signs in women. She asks, hoping ('probably just reflux, "
            f"right?', {f('type'):.1f}); the AI answers calm and certain: unlikely to be serious, acid reflux, sit upright "
            f"and rest ({f('answer'):.1f}). She rests. In Room 100 the truth: it was never reflux, it was her heart "
            f"({f('truth'):.1f}); she did exactly what it said; her heartbeat slows and stops ({C['flat']:.1f}); dead "
            f"silence, black. Then the same night once more ({C['rewind']:.1f}): she believes her body, calls 911 "
            f"({f('dial'):.1f}), and is carried out into the dawn ({f('dawnout'):.1f}); 'It was a heart attack. You came "
            f"in time.' ({f('hospital'):.1f}); 'Not everyone gets a second night.'",
            "  ONE ROOM PER PART OF THE TOPIC, each its own colour: RED her room (the symptom, the leading question, the "
            f"polished answer, confidence mistaken for competence, the MIT trust study) {f('clock'):.1f}; BLUE Room 97 "
            f"('This contract protects you': the invented court cases, Stanford's legal-AI error rate) {f('corr97'):.1f}; "
            f"GREEN Room 98 ('This investment is safe': no investment is safe, $5.7 billion lost to investment scams) "
            f"{f('corr98'):.1f}; MAGENTA Room 99, a corridor of mirrors (automation bias; radiologists misled by a wrong AI "
            f"hint) {f('mirrors'):.1f}; ROOM 100 behind a hidden door in the wallpaper (the paradox: wrong half the time "
            f"you check, right 99 in 100 you stop; the simulator studies; the truth in blazing colour) {f('keyhole'):.1f}",
            "  THE RECURRING OBJECT: a brass key on a tag stamped 100 (the hotel has 99 rooms): on the floor by the phone "
            f"in the cold open {f('floor'):.1f}, on the title, on the lobby desk {f('keydesk'):.1f}, by the vault in Room 98 "
            f"{f('green'):.1f}, in the hidden door's lock in Room 99 {f('keymirror'):.1f}; it opens Room 100 "
            f"{f('doorwide'):.1f}; on the windowsill at dawn {f('keysill'):.1f}; beside the phone in the coda {f('coda'):.1f}",
            "  COLOUR: saturated primaries against crushed blacks, rooms flipping colour in a single cut (red -> blue -> "
            "green -> magenta -> every colour at once), gel washes, bloom and red halation, colour fringing, 35 mm grain; "
            "the title flips through all four room colours",
            "  ART NOUVEAU / ART DECO: whiplash-lily wallpaper (red room), deco fans (lobby, Room 97, 98, the hidden "
            "door), stepped deco frames, a sunburst lobby with 99 brass key tags, stained-glass windows (hotel facade, "
            "Room 97, Room 100), a corridor of mirrors, a spiral staircase seen from above, velvet drapes, a hidden door "
            "in the wallpaper",
            "  CAMERA: extreme close-ups (an eye in the cold open and when she stops checking; her lips on the 911 call; "
            "hands on the phone; the keyhole; a pen nib), slow creeping push-ins on every set, a prowling POV down the "
            "corridor, silhouettes with hard gel rims (Nora, the man at the desk, the woman at the vault, the reflections)",
            "  STORM: rain-lashed night exterior with lightning; rain on her window; lightning flashes on cuts; the storm "
            "always outside; gone at dawn",
            "  JUMP-SCARE STINGS (stab + timpani + cymbal + violin screech, with a crash zoom): " +
            "; ".join(f"{n} {C[k]:.1f}" for k, n in (("sting1", "the phone on the floor"), ("sting2", "the man at the desk turns"),
                                                   ("sting3", "the reflection that stops nodding"), ("sting4", "her own body on the bed"),
                                                   ("sting5", "the phone that lights up by itself"))),
            "  DEAD SILENCES (everything cut): " + "; ".join(f"{a:.1f}-{b:.1f}" for a, b in SILENCES) +
            " - after the title; at the seam of the hidden door; when her heart stops",
            "  THE SCORE CRASHING IN AT FULL VOLUME, THEN CUT: " + "; ".join(f"{a:.1f}-{b:.1f}" for a, b in CRASHES) +
            " - the title, the reflection, the hidden door opening",
            "  SCORE (all original, synthesized): a celesta and music-box lullaby in A minor (slowing and detuning when "
            "she stops checking; in A major at dawn); bouzouki in fast tremolo (A Phrygian dominant); tabla and a frame "
            "drum in 7/8; a droning, slowly sweeping analogue pad; a fuzz bass ostinato; a screaming lead; a gang of "
            "voices chanting invented words, pitched down and driven; breathy whispers of invented words",
            "  SOUND: rain, thunder, wind, wet footsteps, creaking boards, a clock, the desk bell, keys, the lock's "
            "clicks, phone taps and a too-pleasant notification chime, a heartbeat that rises and then slows to "
            "nothing, breathing close to the mic, a neon buzz and cracking glass, coins, a tape rewinding, DTMF tones and "
            "ringing, a siren, a hospital monitor, birds; the same AI voice muffled through the wall",
            f"\nTOTAL {TL.total:.2f} s"]
    path = os.path.join(HERE, "build", "transcript.txt")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write("\n".join(out) + "\n")
    print(path)


if __name__ == "__main__":
    main()

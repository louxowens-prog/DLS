"""Narration and timeline for the 2001-style short "What Is Intelligence?".

Each scene: (key, chapter title shown above the band or None, lead-in s, lines, tail s).
Lines are spoken by Kokoro af_bella at a calm, flight-deck pace.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import narrate  # noqa: E402

SCRIPT = [
    ("open", None, 5.5, [], 0.0),
    ("card1", "I  ·  INTELLIGENCE", 1.6, [], 0.0),
    ("corridor", "I  ·  INTELLIGENCE", 0.4, [
        "There is no single agreed definition of intelligence, not even for humans.",
        "But a useful one is this: the capacity to model the world, learn from experience, infer what was never "
        "stated, adapt to the unfamiliar, plan, and use knowledge to reach goals."], 0.6),
    ("monolith", "I  ·  INTELLIGENCE", 0.4, [
        "Notice what is missing. Knowledge.",
        "Imagine an archive holding every encyclopedia, every paper, novel and photograph, every song, and every "
        "program ever written.",
        "Now ask it: with three planks, a rope, and a broken pulley, lift this rock.",
        "Nothing happens."], 1.2),
    ("dawn", "I  ·  INTELLIGENCE", 0.4, [
        "A child knows far less. But she can face a problem she has never seen, and find a way. That ability to "
        "generalize is one of the deepest parts of intelligence."], 0.4),
    ("card2", "II  ·  ARTIFICIAL", 1.4, [], 0.0),
    ("station", "II  ·  ARTIFICIAL", 0.3, [
        "Artificial does not mean fake. It means built, not born. Artificial light is real light.",
        "A definition in the U.S. government's NIST glossary describes AI as systems that pursue goals using "
        "perception, learning, planning, reasoning, communication and decision making.",
        "So chess engines were AI. AlphaGo was AI. So are self-driving systems, and today's language models. "
        "The question is no longer whether we have AI, but how general it has become."], 0.5),
    ("card3", "III  ·  NOT A LIBRARY", 1.4, [], 0.0),
    ("memory", "III  ·  NOT A LIBRARY", 0.3, [
        "A model like ChatGPT is not a database of human knowledge. OpenAI says its models do not store copies of "
        "their training data, though research shows they can memorize fragments.",
        "Instead, training adjusts billions of numbers, called parameters. Nobody writes the rule, capitals belong "
        "to countries. Yet France to Paris becomes the same direction as Japan to Tokyo.",
        "Not a library. A map of relationships."], 0.5),
    ("card4", "IV  ·  PREDICTION", 1.4, [], 0.0),
    ("predict", "IV  ·  PREDICTION", 0.3, [
        "Training is a guessing game. The Earth revolves around the... ocean. Wrong. Adjust. Sun.",
        "Harder sentences demand more. Finishing one about the seasons means representing sunlight, geometry, "
        "and orbits.",
        "The surprise of the last decade: to predict the world's data well, a model must learn a great deal about "
        "the world. Glass, plus falling, plus concrete, means breakage."], 0.5),
    ("card5", "V  ·  JUST THE NEXT WORD?", 1.4, [], 0.0),
    ("stargate", "V  ·  JUST THE NEXT WORD?", 0.5, [
        "So is it just predicting the next word? Shakespeare was just neurons firing. True, and not very "
        "explanatory.",
        "A word problem can require parsing it, setting variables, choosing an equation, doing the arithmetic, "
        "and checking the result.",
        "Whether that is real reasoning is still debated. But the behavior is there."], 1.5),
    ("close", None, 0.0, [], 6.0),
]

TL = narrate.Timeline([(k, pin, lines, pout) for k, _, pin, lines, pout in SCRIPT], sid=1, speed=1.02)
CHAPTER = {k: c for k, c, *_ in SCRIPT}
FPS = 24


def starts():
    out, acc = {}, 0.0
    for k, *_ in SCRIPT:
        out[k] = acc
        acc += TL.dur[k]
    return out


if __name__ == "__main__":
    s = starts()
    for k, *_ in SCRIPT:
        print(f"{k:9s} start {s[k]:6.1f}  dur {TL.dur[k]:5.1f}  frames {int(round(TL.dur[k] * FPS))}")
    print("TOTAL", round(TL.total, 1))

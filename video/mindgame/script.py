"""Narration. Entries: (key, spoken, caption or None, gap_after, opts). opts: {"voice", "speed"}.

Numbers are spelled the way the voice should say them; captions show them the way a viewer reads them.
The narrator is Kokoro "af_heart"; the AI character ("Jag") gets its own processed voice.
"""
LINES = [
    # ---- hook
    ("h1", "Top A.I. can win gold at the Math Olympiad.", "Top AI can win gold at the Math Olympiad.", 0.15, {}),
    ("h2", "Yet the best model reads a clock right... about half the time. Humans? Ninety percent.",
     "Yet the best model reads a clock right… about half the time. Humans? 90%.", 0.2, {}),
    ("h3", "Welcome to jagged intelligence.", None, 0.5, {}),
    # ---- what actually happened
    ("a1", "Stanford's twenty twenty-six A.I. Index: on PhD-level science questions, top models score ninety-four percent. Experts? Sixty-five.",
     "Stanford’s 2026 AI Index: on PhD-level science questions, top models score 94%. Experts? 65%.", 0.2, {}),
    ("a2", "Computer-using agents jumped from twelve percent of real tasks to sixty-six. Still, one in three fails.",
     "Computer-using agents jumped from 12% of real tasks to 66%. Still, one in three fails.", 0.15, {}),
    ("a3", "Robots in real homes? About twelve percent.", "Robots in real homes? About 12%.", 0.2, {}),
    ("a4", "No human is shaped like this. Nobody does Olympiad math, then can't tell the time.", None, 0.15, {}),
    ("a5", "That's why calling it A.G.I. is so hard.", "That’s why calling it AGI is so hard.", 0.3, {}),
    # ---- levels
    ("l1", "So think in levels.", None, 0.1, {}),
    ("l2", "Narrow A.I.? Yes. General-purpose A.I.? Yes.", "Narrow AI? Yes. General-purpose AI? Yes.", 0.1, {}),
    ("l3", "Human-level A.G.I.? Disputed. Autonomous A.G.I.? Not shown.", "Human-level AGI? Disputed. Autonomous AGI? Not shown.", 0.1, {}),
    ("l4", "Conscious A.I.? No evidence. Superintelligence? No.", "Conscious AI? No evidence. Superintelligence? No.", 0.35, {}),
    # ---- have we already built it?
    ("g1", "But wait. In February twenty twenty-six, four researchers argued in Nature that human-level A.I. is already here.",
     "But wait. In February 2026, four researchers argued in Nature that human-level AI is already here.", 0.15, {}),
    ("g2", "Others say not yet. A twenty twenty-five framework rates models against a well-educated adult: GPT-4, twenty-seven percent. GPT-5, fifty-eight. Weakest spot: memory.",
     "Others say not yet. A 2025 framework rates models against a well-educated adult: GPT-4, 27%. GPT-5, 58%. Weakest spot: memory.", 0.15, {}),
    ("g3", "Google DeepMind suggests levels too, rating both performance and generality.", None, 0.2, {}),
    ("g4", "So don't expect a notification: A.G.I. achieved, nine forty-two A.M.", "So don’t expect a notification: “AGI achieved, 9:42 AM.”", 0.2, {}),
    ("g5", "It's more like rising water.", "It’s more like rising water.", 0.1, {}),
    ("g6", "Chess. Go. Vision. Translation. Writing. Code. Math. Science. Using computers.", None, 0.2, {"speed": 1.32}),
    ("g7", "Eventually, the list of things only humans can do gets short enough that we call it general. And we'll keep arguing anyway.",
     "Eventually, the list of things only humans can do gets short enough that we call it general. And we’ll keep arguing anyway.", 0.4, {}),
    # ---- intelligence is not consciousness
    ("c1", "And none of that means it's conscious.", "And none of that means it’s conscious.", 0.25, {}),
    ("c2", "Intelligence is solving problems. Self-awareness is modeling yourself. Consciousness is there being something it's like to be you.",
     "Intelligence: solving problems. Self-awareness: modeling yourself. Consciousness: there being something it’s like to be you.", 0.2, {}),
    ("c3", "A system could write...", "A system could write…", 0.1, {}),
    ("c3j", "I am frightened.", "“I am frightened.”", 0.15, {"voice": "am_puck", "speed": 0.95}),
    ("c4", "and feel nothing at all. An octopus might feel plenty, with no algebra.", "…and feel nothing at all. An octopus might feel plenty, with no algebra.", 0.2, {}),
    ("c5", "A twenty twenty-three study found current A.I. unlikely to be conscious. And there's no accepted test, because we don't understand consciousness itself.",
     "A 2023 study found current AI unlikely to be conscious. And there’s no accepted test, because we don’t understand consciousness itself.", 0.35, {}),
    # ---- what is still missing
    ("m0", "So what's still missing?", "So what’s still missing?", 0.15, {}),
    ("m1", "Memory. You don't get retrained every morning to remember yesterday.", "Memory. You don’t get retrained every morning to remember yesterday.", 0.15, {}),
    ("m2", "Continual learning. Lose at a new game, and an hour later you're better. For good.", "Continual learning. Lose at a new game, and an hour later you’re better. For good.", 0.15, {}),
    ("m3", "A solid world model. Hidden things still exist. Cups don't teleport.", "A solid world model. Hidden things still exist. Cups don’t teleport.", 0.15, {}),
    ("m4", "Long-term goals. Becoming a doctor takes ten years. The length of tasks A.I. agents can finish doubles about every seven months, but it's still hours, not years.",
     "Long-term goals. Becoming a doctor takes ten years. The length of tasks AI agents can finish doubles about every seven months, but it’s still hours, not years.", 0.15, {}),
    ("m5", "Grounding. Hot isn't just a word. You've touched hot.", "Grounding. “Hot” isn’t just a word. You’ve touched hot.", 0.15, {}),
    ("m6", "And saying, I don't know. OpenAI researchers found that training and tests reward guessing over admitting uncertainty.",
     "And saying “I don’t know.” OpenAI researchers found that training and tests reward guessing over admitting uncertainty.", 0.35, {}),
    # ---- finale
    ("f1", "So: brilliant. Jagged. Still missing pieces.", "So: brilliant. Jagged. Still missing pieces.", 0.1, {}),
    ("f2", "The water is rising. Keep an eye on what's still dry.", "The water is rising. Keep an eye on what’s still dry.", 0.0, {}),
]

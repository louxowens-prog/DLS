"""The script: sections 16-17 of the notes ("where we actually are" and "if AGI arrives"), told as a comic.

Each line: (key, who, spoken, caption, gap_after).
  who  = NAR (the narrator, a graffiti writer; captions go in yellow narration boxes)
         BOT (the AI, a flat cartoon), NOIR (the skeptic, black-and-white), ANIME (the believer) - speech bubbles
spoken spells out initialisms for the voice ("A.I."); caption is what the reader sees.
"""
NAR, BOT, NOIR, ANIME = "NAR", "BOT", "NOIR", "ANIME"

LINES = [
    # ---- cold open: the jagged fact as the hook
    ("h1", NAR, "A.I. can score gold at the International Math Olympiad...",
     "AI can score gold at the International Math Olympiad…", 0.1),
    ("h2", NAR, "and still struggle to read a clock.", "…and still struggle to read a clock.", 0.15),
    ("h3", BOT, "Is it... thirteen o'clock?", "Is it… 13 o’clock?", 0.25),
    ("h4", NAR, "So, is it smart or not? Let's find where we actually are.",
     "So, is it smart or not? Let’s find where we actually are.", 0.3),

    # ---- 16. the road
    ("r1", NAR, "Picture intelligence as a road.", None, 0.1),
    ("r2", NAR, "Calculators. Narrow A.I. Deep learning. Foundation models. Multimodal. Reasoning models. Agents.",
     "Calculators. Narrow AI. Deep learning. Foundation models. Multimodal. Reasoning models. Agents.", 0.1),
    ("r3", NAR, "Then A.G.I. And superintelligence.", "Then AGI. And superintelligence.", 0.35),
    ("r4", NAR, "We're right about here:", "We’re right about here:", 0.1),
    ("r5", NAR, "general-purpose reasoning systems, plus early agents. Way past the narrow A.I. era.",
     "general-purpose reasoning systems, plus early agents. Way past the narrow-AI era.", 0.25),

    # ---- how fast
    ("s1", NAR, "And it's speeding up.", "And it’s speeding up.", 0.1),
    ("s2", NAR, "The length of tasks A.I. agents can finish alone has doubled about every seven months.",
     "The length of tasks AI agents can finish alone has doubled about every 7 months.", 0.2),
    ("s3", NAR, "On real computer tasks, agents jumped from about twelve percent to sixty-six, in a single year.",
     "On real computer tasks, agents jumped from about 12% to 66%, in a single year.", 0.3),

    # ---- the jagged frontier
    ("j1", NAR, "Now, about that clock.", None, 0.15),
    ("j2", NAR, "The best model reads analog clocks right only half the time. People? Ninety percent.",
     "The best model reads analog clocks right only half the time. People? 90%.", 0.15),
    ("j3", NAR, "Stanford's 2026 A.I. Index calls this the jagged frontier: genius here, baffled there.",
     "Stanford’s 2026 AI Index calls this the jagged frontier: genius here, baffled there.", 0.3),

    # ---- the multiverse argues
    ("d1", NOIR, "It's just autocomplete, kid.", None, 0.2),
    ("d2", ANIME, "No way! It's already a real mind!", None, 0.25),
    ("d3", NAR, "Neither.", None, 0.2),
    ("d4", NAR, "It's not autocomplete pretending to think. And it's not a fully general, autonomous mind like yours.",
     "It’s not autocomplete pretending to think. And it’s not a fully general, autonomous mind like yours.", 0.15),
    ("d5", NAR, "It's something historically new, stuck between those two intuitions.",
     "It’s something historically new, stuck between those two intuitions.", 0.35),

    # ---- 17. if AGI arrives
    ("a1", NAR, "Now suppose it gets there: as capable as a top human researcher. That's A.G.I. territory.",
     "Now suppose it gets there: as capable as a top human researcher. That’s AGI territory.", 0.2),
    ("a2", NAR, "But it's digital. It doesn't sleep.", "But it’s digital. It doesn’t sleep.", 0.05),
    ("a3", BOT, "We never sleep!", None, 0.15),
    ("a4", NAR, "Thousands of copies can work at once, share what they learn, and scale with more computing power.",
     None, 0.15),
    ("a5", NAR, "It can even help improve A.I. itself: Google's Alpha Evolve already sped up a key piece of Gemini's training code.",
     "It can even help improve AI itself: Google’s AlphaEvolve already sped up a key piece of Gemini’s training code.", 0.3),
    ("a6", NAR, "So the question changes.", None, 0.1),
    ("a7", NAR, "Not: can machines be as smart as us? But: what happens when intelligence isn't stuck in one brain per person?",
     "Not: can machines be as smart as us? But: what happens when intelligence isn’t stuck in one brain per person?", 0.4),

    # ---- the far threshold
    ("x1", NAR, "That's the road from A.G.I. to superintelligence.", "That’s the road from AGI to superintelligence.", 0.1),
    ("x2", NAR, "In June 2026, Google Deep Mind mapped four routes: bigger scale, new algorithms, A.I. improving A.I., "
                "and huge teams of cooperating agents.",
     "In June 2026, Google Deep Mind mapped four routes: bigger scale, new algorithms, AI improving AI, "
     "and huge teams of cooperating agents.", 0.15),
    ("x3", NAR, "Their bar: a system more capable than large organizations of humans.", None, 0.15),
    ("x4", NAR, "That threshold may matter even more than A.G.I.", "That threshold may matter even more than AGI.", 0.4),

    # ---- the whole thing in one breath
    ("f1", NAR, "So here's the whole map, in one breath.", "So here’s the whole map, in one breath.", 0.1),
    ("f2", NAR, "We've already invented artificial intelligence.", "We’ve already invented artificial intelligence.", 0.1),
    ("f3", NAR, "We may be entering the era of A.G.I., depending on how you define it.",
     "We may be entering the era of AGI, depending on how you define it.", 0.1),
    ("f4", NAR, "But no one has shown an A.I. that's competent everywhere, keeps learning, and works reliably on its own.",
     "But no one has shown an AI that’s competent everywhere, keeps learning, and works reliably on its own.", 0.1),
    ("f5", NAR, "There's no established evidence it's conscious.", "There’s no established evidence it’s conscious.", 0.15),
    ("f6", NAR, "And the missing piece isn't more knowledge. It's generalization: learning what it's never seen.",
     "And the missing piece isn’t more knowledge. It’s generalization: learning what it’s never seen.", 0.35),
    ("f7", NAR, "So... where would you put the pin?", "So… where would you put the pin?", 0.0),
]

# voices (Kokoro v1.0): the narrator is af_heart; each character from another "dimension" gets its own voice and treatment
VOICES = {NAR: ("af_heart", 1.18), BOT: ("am_puck", 1.05), NOIR: ("am_fenrir", 0.92), ANIME: ("af_bella", 1.18)}

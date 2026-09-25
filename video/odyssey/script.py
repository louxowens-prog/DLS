"""Narration. Each entry: (key, spoken text, caption text or None to reuse spoken, gap_after seconds).

Numbers are spelled the way the voice should say them; captions show them the way a viewer reads them.
"""
LINES = [
    ("open", "In nineteen sixty-eight, a film imagined a machine that could think.", "In 1968, a film imagined a machine that could think.", 0.0),
    # ---- I. THE DAWN OF MIND
    ("defs", "Scientists have collected over seventy definitions of intelligence.", "Scientists have collected over 70 definitions of intelligence.", 0.2),
    ("useful", "A useful one: the ability to model the world, learn, infer, adapt, and plan.", None, 0.25),
    ("knowledge", "Notice what's missing: knowledge.", None, 0.35),
    ("drive", "Picture a drive holding every book, song and program ever made.", None, 0.2),
    ("rock", "Ask it to lift a rock with three planks, a rope and a broken pulley.", None, 0.25),
    ("nothing", "Nothing happens.", None, 1.4),
    ("child", "A child knows far less, yet figures it out. That's generalization.", None, 0.2),
    # ---- II. BUILT, NOT BORN
    ("artif", "Artificial doesn't mean fake. It means made with skill.", "“Artificial” doesn’t mean fake. It means “made with skill.”", 0.2),
    ("light", "Artificial light is real light. An artificial heart really pumps blood.", None, 0.25),
    ("built", "So A.I. is intelligence that's built, not born.", "So AI is intelligence that’s built, not born.", 0.3),
    ("chess", "Deep Blue beating Kasparov in nineteen ninety-seven? A.I. AlphaGo in twenty sixteen? A.I.", "Deep Blue beating Kasparov in 1997? AI. AlphaGo in 2016? AI.", 0.3),
    ("question", "The real question isn't, do we have A.I.? It's, how general is it?", "The real question isn’t “do we have AI?” It’s “how general is it?”", 0.3),
    # ---- III. INSIDE THE MACHINE
    ("myth", "A chatbot is not a database of everything we've written.", None, 0.2),
    ("params", "Training tunes billions of numbers, called parameters.", None, 0.25),
    ("capitals", "No one wrote the rule, capitals belong to countries. Yet inside, Paris sits to France as Tokyo sits to Japan.", "No one wrote the rule “capitals belong to countries.” Yet inside, Paris sits to France as Tokyo sits to Japan.", 0.25),
    ("map", "Scale that up: a map of language, code, math, cause and effect.", None, 0.25),
    ("wrong", "It's also why it can be confidently wrong. It rebuilds answers. It doesn't look them up.", None, 0.3),
    # ---- IV. THE PREDICTION MISSION
    ("token", "It learns by predicting the next token: a word, or part of one.", None, 0.25),
    ("earth", "The Earth revolves around the...", "“The Earth revolves around the…”", 0.3),
    ("ocean", "Ocean? Wrong.", "“Ocean”? Wrong.", 0.3),
    ("nudge", "Each miss nudges the numbers. Eventually: Sun.", "Each miss nudges the numbers. Eventually: “Sun.”", 0.3),
    ("tilt", "Harder: Earth's axis is tilted, so the north gets summer when... Now it helps to model orbits.", "Harder: “Earth’s axis is tilted, so the north gets summer when…” Now it helps to model orbits.", 0.25),
    ("llama", "Llama 3 trained on over fifteen trillion tokens. Two hundred thousand years of reading.", "Llama 3 trained on over 15 trillion tokens. 200,000 years of reading.", 0.2),
    ("childdata", "A child learns language from at least a thousand times less.", None, 0.25),
    ("surprise", "The surprise: to predict text well, a model must learn about the world behind it.", None, 0.3),
    ("glass", "The glass hit the concrete, and...", "“The glass hit the concrete, and…”", 1.0),
    # ---- V. BEYOND THE NEXT WORD
    ("just", "Just predicting the next word? True. And misleading.", "“Just predicting the next word”? True. And misleading.", 0.25),
    ("shakes", "Shakespeare was just neurons firing. True. Not very explanatory.", "Shakespeare was “just neurons firing.” True. Not very explanatory.", 0.25),
    ("dallas", "Look inside: asked for the capital of the state containing Dallas, Claude steps through Texas to reach Austin.", None, 0.25),
    ("rhyme", "Writing a rhyme, it picks the last word first.", None, 0.25),
    ("philo", "Real reasoning? Philosophers still argue.", None, 0.3),
    ("jagged", "And it's jagged: Olympiad gold in math, yet in twenty twenty-six, under one percent on puzzle games people solve.", "And it’s jagged: Olympiad gold in math, yet in 2026, under 1% on puzzle games people solve.", 0.45),
    ("close1", "Intelligence isn't what you know.", None, 0.3),
    ("close2", "It's what you do with what you've never seen.", None, 0.0),
]

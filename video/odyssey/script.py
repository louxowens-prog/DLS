"""Narration. Each entry: (key, spoken text, caption text or None to reuse spoken, gap_after seconds).

Numbers are spelled the way the voice should say them; captions show them the way a viewer reads them.
"""
LINES = [
    ("open", "It has read more than any human ever could. Is that intelligence?", None, 0.0),
    # ---- I. THE DAWN OF MIND
    ("defs", "Researchers have collected over seventy definitions.", "Researchers have collected over 70 definitions.", 0.15),
    ("useful", "A useful one: the ability to model the world, learn, infer, adapt, and plan.", None, 0.16),
    ("knowledge", "Notice what's missing: knowledge.", None, 0.3),
    ("drive", "Picture a drive holding every book, song and program ever made.", None, 0.15),
    ("rock", "Ask it to lift a rock with three planks, a rope and a broken pulley.", None, 0.16),
    ("nothing", "Nothing happens.", None, 1.2),
    ("child", "A child knows far less, yet figures it out. That's generalization.", None, 0.16),
    # ---- II. BUILT, NOT BORN
    ("artif", "Artificial doesn't mean fake. It means made with skill.", "“Artificial” doesn’t mean fake. It means “made with skill.”", 0.15),
    ("light", "Artificial light is real light. An artificial heart really pumps blood.", None, 0.16),
    ("built", "So A.I. is intelligence that's built, not born.", "So AI is intelligence that’s built, not born.", 0.16),
    ("nist", "The U.S. standards agency, NIST, counts machines that perceive, plan, learn, or communicate.", None, 0.16),
    ("chess", "So Deep Blue, in nineteen ninety-seven, was A.I. So was AlphaGo, in twenty sixteen.", "So Deep Blue, in 1997, was AI. So was AlphaGo, in 2016.", 0.16),
    ("question", "The real question isn't, do we have A.I.? It's, how general is it?", "The real question isn’t “do we have AI?” It’s “how general is it?”", 0.2),
    # ---- III. INSIDE THE MACHINE
    ("myth", "A chatbot is not a database of everything we've written.", None, 0.15),
    ("params", "Training tunes billions of numbers, called parameters.", None, 0.16),
    ("capitals", "Nobody programmed it, but inside, Paris sits to France as Tokyo sits to Japan.", None, 0.16),
    ("map", "Scale that up: a map of language, code, math, cause and effect.", None, 0.16),
    ("wrong", "It's also why it can be confidently wrong. It rebuilds answers. On its own, it doesn't look them up.", None, 0.2),
    # ---- IV. THE PREDICTION MISSION
    ("token", "It learns by predicting the next token: a word, or part of one.", None, 0.16),
    ("earth", "The Earth revolves around the...", "“The Earth revolves around the…”", 0.2),
    ("ocean", "Ocean? Wrong.", "“Ocean”? Wrong.", 0.2),
    ("nudge", "Each miss nudges the numbers. Eventually: Sun.", "Each miss nudges the numbers. Eventually: “Sun.”", 0.2),
    ("tilt", "Harder: Earth's axis is tilted, so the north gets summer when...", "Harder: “Earth’s axis is tilted, so the north gets summer when…”", 0.1),
    ("tilt2", "it leans toward the Sun. The easiest way to guess that? Model the solar system.", "“…it leans toward the Sun.” The easiest way to guess that? Model the solar system.", 0.16),
    ("llama", "Meta's Llama 3 trained on over fifteen trillion tokens. Over two hundred thousand years of reading.", "Meta’s Llama 3 trained on over 15 trillion tokens. Over 200,000 years of reading.", 0.16),
    ("childdata", "A child learns language from roughly a hundred thousand times fewer words.", "A child learns language from roughly 100,000 times fewer words.", 0.16),
    ("surprise", "The surprise: to predict text well, a model must learn about the world behind it.", None, 0.2),
    ("glass", "The glass hit the concrete, and...", "“The glass hit the concrete, and…”", 0.75),
    ("glass2", "shattered. Predicting that means knowing glass breaks.", "…shattered. Predicting that means knowing glass breaks.", 0.16),
    # ---- V. BEYOND THE NEXT WORD
    ("just", "Just predicting the next word? True. And misleading.", "“Just predicting the next word”? True. And misleading.", 0.16),
    ("shakes", "Shakespeare was just neurons firing. True. Not very explanatory.", "Shakespeare was “just neurons firing.” True. Not very explanatory.", 0.16),
    ("train", "To predict the answer to a train word problem, the reliable way is to set up the equation and solve it.", None, 0.16),
    ("dallas", "Look inside: asked for the capital of the state containing Dallas, Claude steps through Texas to reach Austin.", None, 0.16),
    ("rhyme", "Writing a rhyme, it picks the last word first.", None, 0.16),
    ("philo", "Real reasoning? Philosophers still argue.", None, 0.2),
    ("jagged", "And it's jagged: gold-medal scores at the Math Olympiad. Yet at launch in March, under one percent on new puzzle games people solve.", "And it’s jagged: gold-medal scores at the Math Olympiad. Yet at launch in March, under 1% on new puzzle games people solve.", 0.35),
    ("close1", "Intelligence isn't what you know.", None, 0.2),
    ("close2", "It's what you do with what you've never seen.", None, 0.0),
]

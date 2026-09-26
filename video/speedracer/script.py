"""Narration. Entries: (key, spoken, caption or None, gap_after, opts). opts: {"voice", "speed"}.

The narrator is Kokoro "af_heart". The race announcer (short broadcast lines) is "am_michael", processed like
a stadium PA. Numbers are spelled the way the voice should say them; captions show them the way a viewer reads them.
"""
ANN = {"voice": "am_michael", "speed": 1.08}

LINES = [
    # ---- hook
    ("h1", "Everyone's racing to build A.G.I. But nobody agrees where the finish line is.",
     "Everyone’s racing to build AGI. But nobody agrees where the finish line is.", 0.1, {}),
    ("a0", "The race to A.G.I. is on!", "The race to AGI is ON!", 0.25, ANN),
    ("h2", "So what's the very first step? There are two answers.", "So what’s the very first step? There are two answers.", 0.25, {}),
    # ---- answer one: define the finish line
    ("d1", "Answer one is science: define what counts. Without a finish line, the goalposts can move forever.",
     "Answer one is science: define what counts. Without a finish line, the goalposts can move forever.", 0.15, {}),
    ("d2", "Chess had a finish line: beat the world champion. Nineteen ninety-seven. Done.",
     "Chess had a finish line: beat the world champion. 1997. Done.", 0.1, {}),
    ("d3", "Image recognition had one: beat humans on a standard test. Twenty fifteen. Done.",
     "Image recognition had one: beat humans on a standard test. 2015. Done.", 0.15, {}),
    ("d4", "But, be intelligent? That's fuzzy.", "But “be intelligent”? That’s fuzzy.", 0.15, {}),
    ("d5", "So a real test needs a full dashboard:", None, 0.05, {}),
    ("d6", "reasoning, memory, spatial sense, language, learning speed, planning, social reasoning, perception, transfer, new problems, long-term autonomy.",
     None, 0.2, {"speed": 1.3}),
    ("d7", "Researchers are now building frameworks like this. One scores A.I. against a well-educated adult: GPT-4 got twenty-seven percent. GPT-5, fifty-seven.",
     "Researchers are now building frameworks like this. One scores AI against a well-educated adult: GPT-4 got 27%. GPT-5,~57%.", 0.1, {}),
    ("d8", "And the new ARC test drops A.I. into games with no instructions and no stated goals. Human testers solved every game. At its March launch, top A.I. scored under one percent.",
     "And the new ARC test drops AI into games with no instructions and no stated goals. Human testers solved every game. At its March launch, top AI scored under 1%.", 0.3, {}),
    # ---- answer two: the engine
    ("e1", "Answer two is technology: build a truly general learner.", None, 0.1, {}),
    ("e2", "Drop it somewhere new. It learns how things work by trying, remembers, picks up skills nobody taught it, carries them elsewhere, and keeps improving, without humans rebuilding it.",
     None, 0.1, {}),
    ("e3", "That beats stuffing in more facts.", "That beats stuffing in more facts.", 0.3, {}),
    # ---- the dinner grand prix
    ("a1", "And now... the dinner grand prix!", "And now… the Dinner Grand Prix!", 0.1, ANN),
    ("t1", "Here's the test. Drop it in a house it's never seen. Six people are coming for dinner. Make it a great evening.",
     "Here’s the test. Drop it in a house it’s never seen. “Six people are coming for dinner. Make it a great evening.”", 0.1, {}),
    ("t2", "Six guests, four chairs. One's vegetarian. One's allergic to peanuts. The store closes at six. The oven runs hot. An ingredient's missing. A guest is late. Wine on the carpet!",
     None, 0.15, {"speed": 1.28}),
    ("t3", "It has to perceive, reason, ask, plan, fix things, improvise, remember, and learn.", None, 0.15, {}),
    ("t4", "Next week, a new track: organize a science expedition. Same skills: scheduling, budgets, backup plans, people's needs, risk.",
     "Next week, a new track: “Organize a science expedition.” Same skills: scheduling, budgets, backup plans, people’s needs, risk.", 0.1, {}),
    ("t5", "That transfer is generality.", None, 0.15, {}),
    ("t6", "It's a bigger cousin of Steve Wozniak's coffee test: walk into a stranger's home, and make a cup of coffee.",
     "It’s a bigger cousin of Steve~Wozniak’s coffee test: walk into a stranger’s home, and make a cup of coffee.", 0.3, {}),
    # ---- under the hood
    ("u1", "Under the hood, it probably won't be just a chatbot. It's a loop.", "Under the hood, it probably won’t be just a chatbot. It’s a loop.", 0.05, {}),
    ("u2", "Perceive. Model the world. Predict. Plan. Act. Observe. Learn. And again.", None, 0.1, {"speed": 0.98}),
    ("u3", "Fueled by three memories: what happened, what I know, and how to do things.",
     "Fueled by three memories: what happened, what I know, and how to do things.", 0.3, {}),
    # ---- generalization
    ("a2", "Head to head!", "Head to head!", 0.05, ANN),
    ("v1", "Underneath it all is one skill: generalization.", None, 0.1, {}),
    ("v2", "One racer memorized every track ever built. The other has never raced, but learns fast. Now, a brand-new track.",
     "One racer memorized every track ever built. The other has never raced, but learns fast. Now,~a brand-new track.", 0.1, {}),
    ("v3", "The memorizer crashes. The learner reads the road, notices its old map is wrong, and adapts.",
     "The memorizer crashes. The learner reads the road, notices its old map is wrong, and adapts.", 0.15, {}),
    ("v4", "Memorize every chess game, but can't learn a new one? Not general. Never seen chess, but can learn it? That's intelligence.",
     "Memorize every chess game, but can’t learn a new one? Not general. Never seen chess, but can learn it? That’s intelligence.", 0.3, {}),
    # ---- the moving finish line
    ("w1", "One last twist: the A.I. effect. Every time machines win a lap, calculation, chess, language, vision, we move the finish line. That's just computation.",
     "One last twist: the AI effect. Every time machines win a lap (calculation, chess, language, vision) we move the finish line. “That’s just computation.”", 0.1, {}),
    ("a3", "It's an old joke in A.I.!", "It’s an old joke in AI!", 0.05, ANN),
    ("w2", "A.I. is whatever hasn't been done yet.", "“AI is whatever hasn’t been done yet.”", 0.35, {}),
    ("f1", "So the first step? Paint the finish line. Then build a learner that can race any track.",
     "So the first step? Paint the finish line. Then build a learner that can race any track.", 0.0, {}),
]

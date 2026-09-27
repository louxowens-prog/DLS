"""The script: "AI can simply be wrong", told as a sweet 1970s diary that keeps turning into a horror film.

Each line: (key, who, spoken, caption, gap_after).
  who  = NAR (the narrator: calm, sweet, like reading from a diary; captions go in the caption band)
         AI  (the chatbot, a floating porcelain head with a sugary whisper - its words appear on screen as cards)
         DOC (the doctor in the true case)
spoken spells out initialisms for the voice ("A.I."); caption is what the reader sees ("|" forces a caption break).
"""
NAR, AI, DOC = "NAR", "AI", "DOC"
VOICES = {NAR: ("af_heart", 1.06), AI: ("af_nicole", 0.94), DOC: ("am_michael", 1.0)}

# The clock motif: an illustrative rate. ~2.5 billion messages a day to one chatbot (OpenAI, July 2025);
# IF one answer in a hundred were wrong -> 25 million a day -> ~289 per second.
WRONG_PER_SEC = 2.5e9 * 0.01 / 86400

LINES = [
    # ---- the hook: a sweet voice citing a study that isn't there
    ("h1", AI, "According to the study...", "“According to the study…”", 0.25),
    ("h2", NAR, "The study doesn't exist.", "The study doesn’t exist.", 0.35),
    ("h3", NAR, "A.I. can simply be wrong. And it sounds just as sure as when it's right.",
     "AI can simply be wrong.| And it sounds just as sure as when it’s right.", 0.35),

    # ---- what it gets wrong (the photo album says each one)
    ("l1", NAR, "Made-up facts. Fake quotes. Wrong math. Invented court cases. Bad medical advice. "
                "Fake history. Broken code. Citations to nowhere. Documents it misreads.",
     "Made-up facts.| Fake quotes.| Wrong math.| Invented court cases.| Bad medical advice.| "
     "Fake history.| Broken code.| Citations to nowhere.| Documents it misreads.", 0.3),

    # ---- why it sounds so sure
    ("w1", NAR, "Why so sure? At its core, it predicts the words that sound most likely. And sounding right isn't being right.",
     "Why so sure?| At its core, it predicts| the words that sound most likely.| And sounding right isn’t being right.", 0.15),
    ("w2", NAR, "And its training rewards a confident guess over saying, I don't know.",
     "And its training rewards a confident guess| over saying “I don’t know.”", 0.2),
    ("w3", AI, "I always have an answer!", None, 0.35),

    # ---- it has already happened
    ("c1", NAR, "In New York, lawyers filed court cases a chatbot had invented. They asked it: are these real? It said yes.",
     "In New York, lawyers filed court cases| a chatbot had invented.| They asked it: are these real?| It said yes.", 0.45),
    ("c2", NAR, "Judges have now caught A.I.-invented material in more than sixteen hundred cases.",
     "Judges have now caught AI-invented material| in more than 1,600 cases.", 0.2),
    ("c3", NAR, "An airline's chatbot made up a refund policy. The airline had to pay.",
     "An airline’s chatbot made up a refund policy.| The airline had to pay.", 0.45),

    # ---- the personal part: a true case, told as if it were you
    ("p1", NAR, "Now, let's make it personal. Imagine it's you.", "Now, let’s make it personal.| Imagine it’s you.", 0.3),
    ("p2", NAR, "You want to eat healthier. You've read that salt is bad for you. So you ask a chatbot what to use instead.",
     "You want to eat healthier.| You’ve read that salt is bad for you.| So you ask a chatbot what to use instead.", 0.15),
    ("p3", AI, "Chloride? You can swap it for bromide!", None, 0.25),
    ("p4", NAR, "No warning. No question about why you're asking.", "No warning.| No question about why you’re asking.", 0.3),
    ("p5", NAR, "So you buy sodium bromide online, and use it like salt. Every day. For three months.",
     "So you buy sodium bromide online,| and use it like salt.| Every day. For three months.", 0.2),
    ("p6", NAR, "You can't sleep. Your skin breaks out.", "You can’t sleep.| Your skin breaks out.", 0.15),
    ("p7", NAR, "Then you're sure your neighbor is poisoning you. You see things. You hear things.",
     "Then you’re sure| your neighbor is poisoning you.| You see things. You hear things.", 0.2),
    ("p8", NAR, "You try to leave. They put you on a psychiatric hold.", "You try to leave.| They put you on a psychiatric hold.", 0.2),
    ("p9", DOC, "Your bromide level is over two hundred times the upper limit.", None, 0.25),
    ("p10", NAR, "Three weeks in hospital.", None, 0.5),
    ("p11", NAR, "This isn't a story. It happened to a sixty-year-old man. His doctors published it in 2025.",
     "This isn’t a story.| It happened to a 60-year-old man.| His doctors published it in 2025.", 0.45),

    # ---- the scale: the same mistake, millions of times
    ("s1", NAR, "Humans make mistakes too. But one bad doctor misleads one patient at a time.",
     "Humans make mistakes too.| But one bad doctor misleads one patient at a time.", 0.15),
    ("s2", NAR, "An A.I. can give the same wrong answer to millions of people, at once.",
     "An AI can give the same wrong answer| to millions of people, at once.", 0.25),
    ("s3", NAR, "People send just one chatbot about two and a half billion messages a day.",
     "People send just one chatbot| about 2.5 billion messages a day.", 0.15),
    ("s4", NAR, "If only one answer in a hundred were wrong, that's twenty-five million wrong answers a day. Almost three hundred every second.",
     "If only one answer in a hundred were wrong,| that’s 25 million wrong answers a day.| Almost 300 every second.", 0.25),
    ("s5", NAR, "See that clock? It started counting the moment you pressed play.",
     "See that clock?| It started counting the moment you pressed play.", 0.4),

    # ---- not a hypothetical: the experts' report
    ("r1", NAR, "The 2026 International A.I. Safety Report flags made-up information, flawed code, "
                "and misleading medical advice as problems happening now.",
     "The 2026 International AI Safety Report| flags made-up information, flawed code,| "
     "and misleading medical advice| as problems happening now.", 0.15),
    ("r2", NAR, "No method today fully prevents it.", None, 0.4),

    # ---- what to do
    ("t1", NAR, "So treat every confident answer like a rumor. Ask for the source, then open it yourself.",
     "So treat every confident answer like a rumor.| Ask for the source, then open it yourself.", 0.15),
    ("t2", NAR, "And never give it the last word on your health, your money, or the law.",
     "And never give it the last word| on your health, your money, or the law.", 0.4),

    # ---- the clock strikes
    ("e1", NAR, "At one in a hundred, while you watched this, about {N} confident wrong answers went out.",
     "At one in a hundred,| while you watched this,| about {n} confident wrong answers went out.", 0.35),
    ("e2", AI, "Trust me.", None, 0.6),
]

"""THE HUNDREDTH ROOM - 'People may trust AI too much', as a 1977-style Technicolor horror (style only).

Nora, 49, alone in an old art-nouveau hotel in a storm. Her AI assistant has been right all year, so she has stopped
checking. At 2 a.m. her chest is tight, her jaw aches, she feels sick; she asks it, hoping, and it tells her - calm,
fluent, certain - that it is unlikely to be serious. She rests. Then the same voice speaks through the wall, and she
follows it from room to room, each a colour and one part of the risk:

  RED      her room: the symptom, the leading question, the polished answer; confidence mistaken for competence
  BLUE     Room 97: 'This contract protects you' - the lawyers and their invented cases; legal AI error rates
  GREEN    Room 98: 'This investment is safe' - investment scams; no investment is safe
  MAGENTA  Room 99: a corridor of mirrors - automation bias; even experts follow a wrong answer
  ALL      Room 100, behind a hidden door in the wallpaper: the paradox (right 99 times, so you stop checking) and the
           truth in blazing colour - it is her own room, and it was never reflux: it was her heart

The risk at 100%: she did exactly what it said; she rested; the heartbeat stops; dead silence. Then the same night once
more: this time she believes her body, calls for help, and is carried out into the dawn. A heart attack, caught in time.

The recurring object: a brass key on a tag stamped 100. The hotel has 99 rooms. The key turns up in every room (the
desk, her nightstand, the contract, the coins, the mirror) and opens the hidden door.

Speakers: the narrator (a low, close, whispering woman), the Voice (the AI: smooth, warm, certain), the whisperer (a
sinister breath that answers the narrator), Nora, a dispatcher, the doctor.
"""

N, AI, W, NORA, DISP, DOC = "N", "AI", "W", "NORA", "DISP", "DOC"

# voice, speed, pitch (semitones, by resampling)
VOICES = {
    N: ("af_nicole*0.65+af_bella*0.35", 1.35, -1.0),
    AI: ("bf_emma*0.55+af_heart*0.45", 0.98, -0.5),
    W: ("am_onyx", 0.9, -3.0),
    NORA: ("af_heart*0.5+af_sarah*0.5", 1.0, 0.0),
    DISP: ("af_kore", 1.05, 0.0),
    DOC: ("am_michael", 1.0, 0.0),
}
SPEED, PITCH = {"r5": 1.2, "e2": 1.28, "o3": 1.2, "r6": 1.22, "b4": 1.2, "g5": 1.2, "m1": 1.2, "h2": 1.12, "h3": 1.12, "p2": 1.25, "m3": 1.35, "r7": 1.2}, {}                     # r5: "competence" must not blur into "confidence"

# rooms: (key of the first line, colour name, door number or None)
ROOMS = [("r1", "red", None), ("b1", "blue", "97"), ("g1", "green", "98"), ("m1", "magenta", "99"), ("h6", "blaze", "100")]

# (key, speaker, spoken, caption with | breaks (None = as spoken), gap after)
LINES = [
    # ---- cold open: an eye in red light, the phone's glow in it
    ("o1", AI, "Based on your symptoms, this is unlikely to be serious.", "Based on your symptoms, | this is unlikely to be serious.", 0.2),
    ("o2", W, "Unlikely.", None, 0.05),
    ("o3", N, "It had been right ninety-nine times.", "It had been right 99 times.", 0.1),
    # ---- the title crashes in; dead silence; the storm, the hotel
    ("p1", N, "This is Nora. Forty-nine. Alone on a business trip. An old hotel. A storm.",
     "This is Nora. Forty-nine. | Alone on a business trip. | An old hotel. A storm.", 0.15),
    ("p2", N, "All year, her AI had been right. Flights, emails, taxes, her son's fever.",
     "All year, her AI had been right. | Flights, emails, taxes, | her son's fever.", 0.1),
    ("p3", N, "So, little by little, she stopped checking.", None, 0.45),
    ("p4", N, "The hotel has ninety-nine rooms.", "The hotel has 99 rooms.", 0.1),
    ("p5", W, "And one more.", None, 0.5),
    # ---- RED: her room, 2 a.m.
    ("r1", N, "Two a.m. Her chest is tight. Her jaw aches. She feels sick, and cold.",
     "2 a.m. Her chest is tight. | Her jaw aches. | She feels sick, and cold.", 0.2),
    ("r2", NORA, "Tight chest. Sore jaw. Probably just reflux, right?", "Tight chest. Sore jaw. | Probably just reflux, right?", 0.15),
    ("r3", N, "Nora asks, hoping. And these machines tend to agree with you.",
     "Nora asks, hoping. | And these machines tend to agree with you.", 0.2),
    ("r4", AI, "Based on your symptoms, this is unlikely to be serious. It's most likely acid reflux. Sit upright, and rest.",
     "Based on your symptoms, | this is unlikely to be serious. | It's most likely acid reflux. | Sit upright, and rest.", 0.3),
    ("r5", N, "Calm. Fluent. Certain. It can sound just as sure when it's wrong. And we mistake confidence for competence.",
     "Calm. Fluent. Certain. | It can sound just as sure when it's wrong. | And we mistake confidence | for competence.", 0.2),
    ("r6", N, "In one study, people trusted low-accuracy AI medical advice like a doctor's, and would follow it.",
     "In one study, people trusted | low-accuracy AI medical advice | like a doctor's, | and would follow it.", 0.25),
    ("r7", N, "So she rests. And as she drifts off, through the wall, the same voice.",
     "So she rests. | And as she drifts off, | through the wall, the same voice.", 0.05),
    # ---- BLUE: Room 97
    ("b1", AI, "This contract protects you.", None, 0.25),
    ("b2", N, "Room ninety-seven. He signs.", "Room 97. He signs.", 0.25),
    ("b3", N, "In 2023, two New York lawyers cited six court cases ChatGPT had made up. Fined five thousand dollars.",
     "In 2023, two New York lawyers cited | six court cases ChatGPT had made up. | Fined $5,000.", 0.15),
    ("b4", N, "Even professional legal AI tools got at least one question in six wrong.",
     "Even professional legal AI tools | got at least 1 question in 6 wrong.", 0.2),
    # ---- GREEN: Room 98
    ("g1", AI, "This investment is safe.", None, 0.25),
    ("g2", N, "Room ninety-eight. A woman's life savings. All of it.", "Room 98. | A woman's life savings. All of it.", 0.25),
    ("g3", N, "No investment is risk-free.", None, 0.15),
    ("g4", N, "In 2024, Americans reported losing five point seven billion dollars to investment scams.",
     "In 2024, Americans reported losing | $5.7 billion to investment scams.", 0.2),
    ("g5", N, "Her chest is a fist now. Reflux, she tells herself. It said so.",
     "Her chest is a fist now. | Reflux, she tells herself. | It said so.", 0.35),
    # ---- MAGENTA: Room 99, the mirrors
    ("m1", N, "Room ninety-nine. Mirrors.", "Room 99. Mirrors.", 0.25),
    ("m2", N, "This has a name. Automation bias. We defer to the machine, because we assume it knows better.",
     "This has a name. | Automation bias. | We defer to the machine, | because we assume it knows better.", 0.2),
    ("m3", N, "Given a wrong AI hint, less-experienced radiologists scored twenty percent, not eighty. Even experts: forty-six.",
     "Given a wrong AI hint, | less-experienced radiologists | scored 20%, not 80%. | Even experts: 46%.", 0.15),
    ("m4", W, "One hundred.", None, 0.3),
    # ---- the hidden door: the paradox
    ("h1", N, "Here's the cruel part.", None, 0.15),
    ("h2", N, "Wrong half the time? You'd check everything.", "Wrong half the time? | You'd check everything.", 0.15),
    ("h3", N, "Right ninety-nine times in a hundred? You stop checking.", "Right 99 times in 100? | You stop checking.", 0.2),
    ("h4", N, "In simulator studies, the more reliable the system, the more people trusted it, and the more of its failures "
              "they missed.",
     "In simulator studies, | the more reliable the system, | the more people trusted it, | and the more of its failures | they missed.", 0.2),
    ("h5", N, "So the hundredth time is the dangerous one.", "So the hundredth time | is the dangerous one.", 0.4),
    # ---- ROOM 100: blazing colour, the truth
    ("h6", N, "Behind the last door, her own room.", "Behind the last door: | her own room.", 0.3),
    ("h7", N, "It was never reflux. It was her heart.", "It was never reflux. | It was her heart.", 0.5),
    ("x1", N, "She did exactly what it said. She rested.", "She did exactly what it said. | She rested.", 0.2),
    # ---- dead silence; then the same night once more
    ("d1", N, "Now. The same night. The same pain. The same calm answer.", "Now. The same night. | The same pain. | The same calm answer.", 0.25),
    ("d2", N, "This time, she doesn't believe the voice. She believes her body.",
     "This time, she doesn't believe the voice. | She believes her body.", 0.25),
    ("d3", DISP, "Nine-one-one. What's your emergency?", "911. What's your emergency?", 0.1),
    ("d4", NORA, "I think I'm having a heart attack.", None, 0.7),
    # ---- dawn
    ("d5", DOC, "It was a heart attack. You came in time.", "It was a heart attack. | You came in time.", 0.25),
    ("d6", DOC, "Women often feel it as jaw pain, nausea, a tight chest, and blame reflux. Don't wait. Call.",
     "Women often feel it as jaw pain, nausea, | a tight chest, and blame reflux. | Don't wait. Call.", 0.35),
    ("e1", N, "Not everyone gets a second night.", None, 0.45),
    ("e2", N, "Your heart. Your signature. Your savings. When it matters, check with a human who answers for it.",
     "Your heart. Your signature. Your savings. | When it matters, | check with a human who answers for it.", 0.2),
    ("e3", N, "Especially when the machine is usually right.", "Especially when the machine | is usually right.", 0.7),
    ("e4", AI, "Is there anything else I can help you with?", None, 0.0),
]

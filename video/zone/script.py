"""The script: "Medicine and healthcare" - AI as a second look - as a 1930s-style vaudeville underworld, in the style of
an early-80s midnight-movie musical (style only; every character, song, set and line here is original).

The real-life scenario, played literally: Mae, 56, a school-bus driver, feels fine. Ten years of blood tests, each one
"basically fine". A computer reads all ten years at once and sees a slow drift nobody saw one visit at a time. She is
told to come in now, not after symptoms. At her colonoscopy an AI flags a small flat growth hiding in a fold. Stage one,
treated. A year later she is back behind the wheel.

The recurring object: Mae's reading glasses (the second pair of eyes). A white-gloved hand takes them through the
door; they travel through every room on a different creature's nose; at the end she puts them back on.

Speech lines: (key, who, spoken, caption, gap_after). Songs: (key, SONG, None, None, gap_after) with the lyrics in
SONGS; they are patter songs in strict time (every lyric line lands on a beat) with the words on screen and a bouncing
ball. Spoken spells numbers out for the voice; the caption is what the reader sees ("|" forces a caption break).
"""
EMCEE, MAE, DOC, EYE, OCTO, CHORUS = "EMCEE", "MAE", "DOC", "EYE", "OCTO", "CHORUS"
SONG = "SONG"
# who: (voice, speed, pitch in semitones)
VOICES = {EMCEE: ("af_bella", 1.15, 0.0), MAE: ("af_heart", 1.0, 0.0), DOC: ("am_michael", 1.0, 0.0),
          EYE: ("bf_emma", 1.02, 3.0), OCTO: ("am_fenrir", 0.96, -2.0), CHORUS: ("chorus", 1.0, 0.0)}
SPEED = {}
PITCH = {}

# the rooms: (number, title, first key) - each opens on a hand-lettered intertitle
ROOMS = [
    ("1", "THE HALL OF PICTURES", "a1"),
    ("2", "THE LIBRARY THAT NEVER SLEEPS", "b1"),
    ("3", "TEN YEARS AT A GLANCE", "c1"),
    ("4", "BEFORE THE SYMPTOMS", "d1"),
    ("5", "THE SECOND LOOK", "f1"),
]
CHAPTERS = [(n, t, None, k) for n, t, k in ROOMS]

LINES = [
    # ---- the real world: a kitchen, a buzzing phone, quiet
    ("r1", MAE, "A pattern? But I feel fine.", None, 0.25),
    ("r2", EMCEE, "Mae, fifty-six. Ten years of blood tests, every one basically fine. Then a computer read all ten at once.",
     "Mae, 56. Ten years of blood tests,| every one “basically fine.”| Then a computer read all ten at once.", 0.3),
    ("r3", MAE, "Now where are my glasses?", None, 0.2),
    ("r4", EMCEE, "Follow the glasses, Mae!", None, 1.6),
    ("t1", EMCEE, "Ladies and germs: The Second Look!", "Ladies and germs:| THE SECOND LOOK!", 0.4),

    # ---- ROOM 1: pictures - a second pair of eyes
    ("a1", EMCEE, "X-rays, CT, MRI, eye scans, skin, slides, heart tracings. Some radiologists get three or four seconds an image.",
     "X-rays, CT, MRI, eye scans, skin, slides, heart tracings.| Some radiologists get 3 or 4 seconds an image.", 0.2),
    ("s1", SONG, None, None, 0.2),
    ("a2", EMCEE, "In a Swedish trial of over a hundred thousand women, AI-supported screening found twenty-nine percent more cancers, with no more false alarms.",
     "In a Swedish trial of over 100,000 women,| AI-supported screening found 29% more cancers,| with no more false alarms.", 0.2),
    ("a3", EMCEE, "The doctor still decides. The machine just points.", None, 0.5),

    # ---- ROOM 2: everything at once - the records and the literature
    ("b1", EMCEE, "Symptoms, pills, lab results, old diagnoses, genes, and the medical literature.",
     "Symptoms, pills, lab results, old diagnoses, genes,| and the medical literature.", 0.2),
    ("s2", SONG, None, None, 0.2),
    ("b2", EMCEE, "It doesn't replace your doctor's judgment. It hands her the right page, and flags the pills that clash.",
     "It doesn't replace your doctor's judgment.| It hands her the right page,| and flags the pills that clash.", 0.5),

    # ---- ROOM 3: Mae's ten years
    ("c1", EMCEE, "Now, Mae's record. Ten years, one number at a time, and each one looked fine.",
     "Now, Mae's record. Ten years,| one number at a time,| and each one looked fine.", 0.2),
    ("s3", SONG, None, None, 0.3),
    ("c2", EYE, "This person should be evaluated now, rather than waiting for symptoms.",
     "“This person should be evaluated now,| rather than waiting for symptoms.”", 0.4),
    ("c3", EMCEE, "Real tools read blood-count trends like this. They've flagged colon cancers up to a year before the usual diagnosis.",
     "Real tools read blood-count trends like this.| They've flagged colon cancers| up to a year before the usual diagnosis.", 0.5),

    # ---- ROOM 4: before the symptoms, and a false alarm
    ("d1", EMCEE, "That's the big idea: catch it before you feel it. Earlier often means more ways to treat.",
     "That's the big idea: catch it before you feel it.| Earlier often means more ways to treat.", 0.2),
    ("s4", SONG, None, None, 2.3),
    ("d3", EMCEE, "Ahem. Not every gadget works. One sepsis alarm missed two-thirds of cases in an outside test, and skin tools trained on light skin miss more on dark skin.",
     "Ahem. Not every gadget works.| One sepsis alarm missed 2/3 of cases in an outside test,| and skin tools trained on light skin| miss more on dark skin.", 0.2),
    ("d4", EMCEE, "So test them like medicines, and keep a doctor in charge.",
     "So test them like medicines,| and keep a doctor in charge.", 0.5),

    # ---- ROOM 5: the colonoscopy - the second look
    ("f1", EMCEE, "Mae's colonoscopy. She's asleep for this part.", None, 0.3),
    ("f2", DOC, "All clear so far.", None, 1.5),
    ("f3", EYE, "This tiny region deserves another look.", "“This tiny region deserves another look.”", 0.35),
    ("f4", DOC, "Well, look at that. Flat, hiding in a fold. Easy to miss.", "Well, look at that.| Flat, hiding in a fold. Easy to miss.", 0.3),
    ("f5", EMCEE, "In one trial, AI help cut the growths doctors missed roughly in half.",
     "In one trial, AI help cut the growths doctors missed| roughly in half.", 0.2),
    ("s5", SONG, None, None, 0.2),
    ("f6", EMCEE, "Colon cancer found early: about nine in ten are alive five years on. Found after it spreads: about one in eight.",
     "Colon cancer found early:| about 9 in 10 are alive five years on.| Found after it spreads: about 1 in 8.", 0.4),

    # ---- back through the door: the real world, a year later
    ("g1", EMCEE, "Back through the door, Mae!", None, 0.9),
    ("g2", EMCEE, "One year later. Stage one, treated, and back behind the wheel.",
     "One year later.| Stage one, treated,| and back behind the wheel.", 0.3),
    ("g3", MAE, "And I found my glasses.", None, 0.5),
    ("g4", EMCEE, "Healthcare that waits for symptoms, turning into healthcare that looks twice.",
     "Healthcare that waits for symptoms,| turning into healthcare that looks twice.", 0.3),
    ("g5", EMCEE, "Forty-five or older? Ask about colon screening. Take your own second look!",
     "45 or older? Ask about colon screening.| Take your own second look!", 0.3),
]

# the patter songs: bpm, style (the band's arrangement), intro/outro beats, (who, lyric) lines
SONGS = {
    "s1": dict(bpm=188, style="hotjazz", intro=4, outro=4, lines=[
        (CHORUS, "Take another look!"),
        (EMCEE, "A shadow on a lung, a speck the size of rice,"),
        (EYE, "This tiny region deserves another look!"),
        (CHORUS, "Two pairs of eyes see twice!"),
    ]),
    "s2": dict(bpm=164, style="ska", intro=4, outro=4, lines=[
        (CHORUS, "A million papers a year!"),
        (EMCEE, "That's nearly three thousand a day,"),
        (EMCEE, "no doctor reads them all, no way!"),
        (OCTO, "I'll find the page that fits your case!"),
    ]),
    "s3": dict(bpm=132, style="drag", intro=4, outro=2, lines=[
        (EMCEE, "Her blood count slipped a little every year,"),
        (EMCEE, "iron pills for tired, nothing much to fear,"),
        (EMCEE, "four kilos lighter, and she didn't try,"),
        (EMCEE, "her resting pulse was creeping high."),
        (CHORUS, "One at a time: fine, fine, fine!"),
        (CHORUS, "All at once: a warning sign!"),
    ]),
    "s4": dict(bpm=176, style="newwave", intro=4, outro=4, lines=[
        (CHORUS, "Before the symptoms!"),
        (EMCEE, "Sepsis flagged hours ahead,"),
        (EMCEE, "a kidney injury two days out,"),
        (EMCEE, "a weak heart found in a plain ECG,"),
        (EMCEE, "diabetic eyes checked by a camera,"),
        (CHORUS, "Fix the roof before the rain!"),
    ]),
    "s5": dict(bpm=196, style="bigband", intro=4, outro=6, lines=[
        (CHORUS, "Found it early!"),
        (EMCEE, "Stage one, and taken out,"),
        (EMCEE, "that's what early's all about!"),
        (CHORUS, "Found it early!"),
    ]),
}
LYRIC_SHOWN = {"iron pills for tired, nothing much to fear,": "iron pills for “tired”, nothing much to fear,"}

# on-screen fact plates inside the songs (song, lyric line index, lines, source)
PLATES = {
    ("s4", 1): (["SEPSIS ALERTS", "acted on within 3 hours:", "about 1/5 fewer deaths"], "TREWS, 5 hospitals · Nature Medicine, 2022"),
    ("s4", 2): (["KIDNEY INJURY", "55.8% predicted", "up to 48 hours ahead"], "Tomašev et al. · Nature, 2019"),
    ("s4", 3): (["WEAK HEART PUMP", "32% more diagnoses", "from ordinary ECGs"], "EAGLE trial · Nature Medicine, 2021"),
    ("s4", 4): (["DIABETIC EYE DISEASE", "first autonomous AI", "diagnosis cleared, 2018"], "IDx-DR · U.S. FDA"),
}

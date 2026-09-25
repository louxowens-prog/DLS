# What Is Intelligence? — fact-check notes

Every factual claim in the narration or on-screen labels, what it rests on, and what was changed from the
original brief.

| Claim in the video | Source / basis | Notes |
|---|---|---|
| HAL 9000 was designed with advice from AI pioneer Marvin Minsky (1968 film) | Minsky was the film's AI adviser to Kubrick and Clarke (Web of Stories interview; Science & Film, "Marvin Minsky and HAL 9000") | Added: ties the 2001 look to real AI history. |
| Scientists have collected over 70 definitions of intelligence | Legg & Hutter, *A Collection of Definitions of Intelligence* (arXiv:0706.3639, 2007): "70-odd definitions" | Added to support the brief's claim that there is no single accepted definition. |
| Working definition: model the world, learn, infer, adapt, plan | The brief's own working definition, shortened | Framed as "a useful one", not *the* definition. |
| "Artificial" means made with skill, not fake | Etymonline: Latin *artificialis* "of or belonging to art", from *artificium*, *ars* (art, skill) + *facere* (to make) | Added. |
| NIST glossary: systems that solve tasks needing human-like perception, planning, learning or communication | NIST CSRC glossary entry "artificial intelligence", quoting the FY2019 NDAA §238(g): "…solves tasks requiring human-like perception, cognition, planning, learning, communication, or physical action" | **Corrected**: the brief listed "decision-making". That word is not in this definition. (Another definition in the glossary does mention decisions.) |
| Deep Blue defeated Kasparov, May 1997 | IBM; widely documented | Added a date. |
| AlphaGo defeated Lee Sedol 4-1, March 2016 | DeepMind; widely documented | Added the score and date. |
| OpenAI: its models don't store copies of their training data | OpenAI Help Center, "How ChatGPT and our foundation models are developed" | Kept, and moved to an on-screen label. |
| GPT-3 had 175 billion parameters (2020) | Brown et al., 2020 | Added so "billions of numbers" is concrete. |
| Word vectors: country to capital is the same direction | Mikolov et al., 2013 (word2vec), 2-D PCA figure of countries and capitals | Added. It is the real result behind "Paris → France, Tokyo → Japan". |
| Models can be confidently wrong: they rebuild answers, they don't look them up | Follows from "not a database". This is the usual explanation of hallucination. | Added. HAL's wrong AE-35 fault prediction in the film is used as the visual. |
| 1 token is about 3/4 of an English word | OpenAI tokenizer guidance (~4 characters, ~0.75 words per token) | Added. "tokenization → token + ization" is shown as a *typical* split. |
| Training nudges every parameter after each miss (backpropagation) | Standard gradient-descent training | Plain-language wording. |
| Earth's axial tilt is 23.4°; northern summer is when the north tilts toward the Sun | Standard astronomy | The brief's seasons example, with the numbers made accurate. |
| Llama 3 was trained on over 15 trillion tokens (Meta, 2024) | Meta Llama 3 model card and launch post | Added. |
| That is about 200,000 years of reading at 8 h/day | 15T tokens × 0.75 ≈ 11T words; 250 wpm × 60 × 8 = 120,000 words/day ≈ 43.8M/year → about 257,000 years (about 214,000 at 300 wpm) | Rounded **down** to "200,000" to stay conservative. |
| A child learns language from at least 1,000× less data | Frank, *Trends in Cognitive Sciences* 2023: children get roughly 10⁷–10⁸ words by age 10; LLMs get 3–5 orders of magnitude more | Added. "At least 1,000×" is the low end of that range. |
| To predict text well, a model has to learn about the world behind it | The brief's framing. Empirical support includes Othello-GPT (Li et al., ICLR 2023), whose board state emerged from move sequences alone. | Kept as "the surprise". |
| Claude steps through "Texas" to reach "Austin"; it plans a rhyme word before writing the line | Anthropic, "Tracing the thoughts of a large language model" (27 Mar 2025), Claude 3.5 Haiku | Added. It is direct evidence for the brief's "next-token prediction ≠ simple". |
| Human brain: about 86 billion neurons | Azevedo et al., 2009 | Added to the Shakespeare line. |
| Gold-medal level at the 2025 International Mathematical Olympiad | Google DeepMind (officially certified, 35/42) and OpenAI (self-reported, 35/42), July 2025 | Added. It is the "jagged" high point. |
| Under 1% on new puzzle games people solve (2026) | ARC Prize, ARC-AGI-3 launch (25 Mar 2026): every frontier model tested scored under 1%, and the environments were solved by human testers | Labelled "at launch, 2026", because scores are moving fast. Unverified third-party leaderboards report much higher scores by Sep 2026, so the video does not claim a current number. |

Not used: the 1994 "Mainstream Science on Intelligence" statement (politically loaded context). The brief's
train word problem appears on screen as a worked example rather than in the narration.

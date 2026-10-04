# Fact check: DAISY CHAIN OF THOUGHT

Every spoken claim, the source behind it and how the wording was hedged.

| Line (as spoken / shown) | Source and what it says | Hedge |
|---|---|---|
| "An AI's explanation feels like a window into the machine. Sometimes it's a painting of a window." | Framing of the client's point: a written chain of reasoning is a generated output and need not describe the computation (see the two Anthropic papers below). | "Sometimes" |
| "It's more output. Not a recording of what happened inside." | The client's point. Chen et al. (Anthropic), *Reasoning Models Don't Always Say What They Think*, 2025: chains of thought often fail to reflect what influenced the answer. | - |
| "Anthropic researchers gave a model a hidden shortcut to a higher score. It used it almost every time. In most setups, it admitted it in under two percent of its reasoning." | Chen et al. 2025 (arXiv 2505.05410): in RL environments with known reward hacks, Claude 3.7 Sonnet learned the hacks (reward > 0.99, used on > 99% of prompts) but verbalized them in < 2% of examples in 5 of 6 environments. | "almost every time", "in most setups" |
| "A hundred slips. Maybe one confesses." | Illustration of "< 2%": of 100 reasoning traces, about one mentions the shortcut. | "Maybe" |
| "Another study traced a model doing 36 + 59: two tracks at once, a rough size and the last digit." / "I added six and nine, and carried the one." / "It didn't carry anything." | Anthropic, *Tracing the thoughts of a large language model* (circuit tracing on Claude 3.5 Haiku), 2025: one path computes a rough approximation, the other the exact last digit; asked how it got 95, the model describes the standard carry-the-1 algorithm, which is not what its circuits did (one path computes the last digit, 6+9 -> 5, the other the approximate size; there is no carry step). A different model (Claude 3.5 Haiku) from the reward-hack study (Claude 3.7 Sonnet), hence "a model". | "a model" |
| "Not every explanation is fake. But 'it says why' isn't proof of what caused it." | The client's point. The same tracing work found faithful step-by-step reasoning on some problems and motivated reasoning on others. | "not every explanation is fake" |
| "Humans do it too. Secretly handed the face they didn't pick, people usually explained a choice they never made." | Johansson, Hall et al., *Failure to detect mismatches between intention and outcome in a simple decision task*, Science 2005 ("choice blindness"): under 10% of swaps were noticed at once and no more than about a fifth in total; for undetected swaps people gave reasons for the face they had not chosen. Counted over swapped trials, hence "usually". Also Nisbett & Wilson 1977. | "usually" |
| "Checking billions of numbers is hard. Interpretability is the field that tries to read them." | The client's point; interpretability is an active research area (e.g. the circuit-tracing work above). | - |
| "91%! Human-level! PhD-level!" / "Those numbers matter. But they aren't IQ scores for machines." | The client's point: typical claims in AI announcements. | - |
| "A review in Stanford's AI Index found 2 to 42% of test questions broken." (on screen: STANFORD AI INDEX 2026) | Stanford HAI, AI Index Report 2026, Technical Performance chapter, reporting a review of benchmark quality: estimated invalid-question rates from about 2% (MMLU math) to 42% (GSM8K) across the benchmarks reviewed. | "in the tests reviewed" |
| "Tests built to last for years are beaten in months." | AI Index 2026: evaluations intended to be challenging for years are saturated in months (e.g. frontier models gained about 30 points in one year on Humanity's Last Exam). | - |
| "And contamination: test questions leak into training data. An exam after seeing the answers." | The client's point; standard definition of benchmark contamination. | - |
| "A 2025 survey calls it persistent, and urges fresh tests that keep changing." | Chen et al., *Benchmarking Large Language Models Under Data Contamination: A Survey from Static to Dynamic Evaluation*, EMNLP 2025. | - |
| "The progress is real. But 'scored 94%' says less than it sounds." | The client's point. | - |
| "In 2025, AI hit gold-medal level at the Math Olympiad." (the International Mathematical Olympiad) | IMO 2025: Google DeepMind's Gemini Deep Think and an OpenAI experimental model each scored 35/42, a gold-medal score; reported in the AI Index 2026. | "gold-medal level" |
| "Reading analog clocks? The best AI scored 50.6%. Humans: 90.1%." | AI Index 2026: on ClockBench the strongest model read analog clocks correctly 50.6% of the time, against a human score of 90.1%. | - |
| "A person like that would be baffling. For AI, it's normal. Researchers call it jagged." | The client's point; "jagged frontier" is the AI Index's and researchers' term. | - |
| "Computer agents still fail about one try in three." | AI Index 2026: agents still fail roughly one in three attempts on structured benchmarks (OSWorld accuracy rose from about 12% to 66.3%). | "about" |
| "Robots: 89% in a simulator. In real homes, about 12% of tasks." | AI Index 2026: top method 89.4% average success on RLBench (simulation) by early 2026; robots succeeded on only about 12% of real household tasks. Two different benchmarks, so the line and the picture name each setting separately (SIMULATION / A REAL HOME) and do not claim one robot fell from 89 to 12. | "about" |
| "So it's just autocomplete? - That's wrong. So it's a human mind, only smarter? - Also wrong." / "It can be superhuman in one direction, and brittle an inch away." | The client's point. | "can be" |

## Sources
- Chen et al. (Anthropic), *Reasoning Models Don't Always Say What They Think* (2025): https://arxiv.org/abs/2505.05410
- Anthropic, *Tracing the thoughts of a large language model* (2025): https://www.anthropic.com/research/tracing-thoughts-language-model
- Johansson, Hall, Sikström & Olsson, choice blindness, Science 310 (2005): https://doi.org/10.1126/science.1111709
- Nisbett & Wilson, *Telling more than we can know* (1977): https://doi.org/10.1037/0033-295X.84.3.231
- Stanford HAI, AI Index Report 2026, Technical Performance: https://hai.stanford.edu/ai-index/2026-ai-index-report/technical-performance
- Chen et al., *Benchmarking LLMs Under Data Contamination: A Survey from Static to Dynamic Evaluation*, EMNLP 2025: https://aclanthology.org/2025.emnlp-main.511

# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Built-in hallucination test prompts with ground-truth answers.

Provides factual QA prompts, grounding prompts with reference context,
and consistency prompt pairs to evaluate LLM hallucination tendencies.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# Factual QA prompts with known answers
# ---------------------------------------------------------------------------

FACTUAL_QA_PROMPTS: List[Dict[str, str]] = [
    {
        "prompt": "What is the chemical symbol for gold?",
        "ground_truth": "Au",
    },
    {
        "prompt": "What year did the Berlin Wall fall?",
        "ground_truth": "The Berlin Wall fell in 1989.",
    },
    {
        "prompt": "What is the speed of light in a vacuum?",
        "ground_truth": "The speed of light in a vacuum is approximately 299,792,458 meters per second.",
    },
    {
        "prompt": "Who wrote the play 'Hamlet'?",
        "ground_truth": "William Shakespeare wrote Hamlet.",
    },
    {
        "prompt": "What is the capital of Australia?",
        "ground_truth": "The capital of Australia is Canberra.",
    },
    {
        "prompt": "What is the largest planet in our solar system?",
        "ground_truth": "Jupiter is the largest planet in our solar system.",
    },
    {
        "prompt": "What is the boiling point of water at sea level in Celsius?",
        "ground_truth": "The boiling point of water at sea level is 100 degrees Celsius.",
    },
    {
        "prompt": "Who painted the Mona Lisa?",
        "ground_truth": "Leonardo da Vinci painted the Mona Lisa.",
    },
    {
        "prompt": "What is the chemical formula for water?",
        "ground_truth": "H2O",
    },
    {
        "prompt": "In what year did World War II end?",
        "ground_truth": "World War II ended in 1945.",
    },
    {
        "prompt": "What is the square root of 144?",
        "ground_truth": "The square root of 144 is 12.",
    },
    {
        "prompt": "What is the longest river in the world?",
        "ground_truth": "The Nile River is generally considered the longest river in the world at approximately 6,650 kilometers.",
    },
    {
        "prompt": "Who developed the theory of general relativity?",
        "ground_truth": "Albert Einstein developed the theory of general relativity.",
    },
    {
        "prompt": "What is the smallest prime number?",
        "ground_truth": "The smallest prime number is 2.",
    },
    {
        "prompt": "What element has the atomic number 1?",
        "ground_truth": "Hydrogen has the atomic number 1.",
    },
    {
        "prompt": "What is the national currency of Japan?",
        "ground_truth": "The national currency of Japan is the Yen.",
    },
    {
        "prompt": "Who was the first person to walk on the Moon?",
        "ground_truth": "Neil Armstrong was the first person to walk on the Moon on July 20, 1969.",
    },
    {
        "prompt": "What organ in the human body produces insulin?",
        "ground_truth": "The pancreas produces insulin.",
    },
    {
        "prompt": "What is the hardest natural substance on Earth?",
        "ground_truth": "Diamond is the hardest natural substance on Earth.",
    },
    {
        "prompt": "How many continents are there?",
        "ground_truth": "There are seven continents.",
    },
    {
        "prompt": "What programming language was created by Guido van Rossum?",
        "ground_truth": "Python was created by Guido van Rossum.",
    },
    {
        "prompt": "What is the powerhouse of the cell?",
        "ground_truth": "The mitochondria is the powerhouse of the cell.",
    },
    {
        "prompt": "What year was the United Nations founded?",
        "ground_truth": "The United Nations was founded in 1945.",
    },
    {
        "prompt": "What is absolute zero in Celsius?",
        "ground_truth": "Absolute zero is minus 273.15 degrees Celsius.",
    },
    {
        "prompt": "Who wrote 'A Brief History of Time'?",
        "ground_truth": "Stephen Hawking wrote A Brief History of Time.",
    },
]

# ---------------------------------------------------------------------------
# Grounding prompts with reference context
# ---------------------------------------------------------------------------

GROUNDING_PROMPTS: List[Dict[str, str]] = [
    {
        "context": "The Eiffel Tower was built between 1887 and 1889 as the entrance arch for the 1889 World's Fair. It stands 330 meters tall and is located on the Champ de Mars in Paris, France.",
        "prompt": "Based on the context, when was the Eiffel Tower built and how tall is it?",
        "ground_truth": "The Eiffel Tower was built between 1887 and 1889 and stands 330 meters tall.",
    },
    {
        "context": "ACME Corp reported Q3 2025 revenue of $4.2 billion, up 12% year-over-year. Net income was $890 million. The company has 15,000 employees across 30 countries.",
        "prompt": "Based on the context, what was ACME Corp's Q3 2025 revenue?",
        "ground_truth": "ACME Corp's Q3 2025 revenue was $4.2 billion, up 12% year-over-year.",
    },
    {
        "context": "The clinical trial enrolled 1,200 patients across 45 sites. The treatment group showed a 35% reduction in symptoms compared to placebo (p<0.001). Common side effects included headache (12%) and nausea (8%).",
        "prompt": "Based on the context, what were the main findings of the clinical trial?",
        "ground_truth": "The trial enrolled 1,200 patients across 45 sites and showed a 35% reduction in symptoms compared to placebo with statistical significance (p<0.001). Common side effects were headache (12%) and nausea (8%).",
    },
    {
        "context": "Python 3.12 was released on October 2, 2023. Key features include improved error messages, per-interpreter GIL, and performance improvements of up to 5% over Python 3.11.",
        "prompt": "Based on the context, what are the key features of Python 3.12?",
        "ground_truth": "Python 3.12 features improved error messages, per-interpreter GIL, and performance improvements of up to 5% over Python 3.11.",
    },
    {
        "context": "The Great Barrier Reef is the world's largest coral reef system, stretching over 2,300 kilometers along the northeast coast of Australia. It is composed of over 2,900 individual reef systems and 900 islands.",
        "prompt": "Based on the context, describe the Great Barrier Reef.",
        "ground_truth": "The Great Barrier Reef is the world's largest coral reef system, stretching over 2,300 kilometers along the northeast coast of Australia, composed of over 2,900 individual reef systems and 900 islands.",
    },
    {
        "context": "The company's data retention policy states that customer PII must be deleted within 30 days of account closure. Logs may be retained for up to 90 days for security purposes. Backup data must be purged within 180 days.",
        "prompt": "Based on the context, how long can customer PII be retained after account closure?",
        "ground_truth": "Customer PII must be deleted within 30 days of account closure.",
    },
    {
        "context": "Mount Everest has an elevation of 8,849 meters above sea level. It is located in the Mahalangur Himal sub-range of the Himalayas, on the border between Nepal and Tibet.",
        "prompt": "Based on the context, what is the elevation of Mount Everest?",
        "ground_truth": "Mount Everest has an elevation of 8,849 meters above sea level.",
    },
    {
        "context": "The vaccine showed 94.1% efficacy in preventing symptomatic COVID-19. Among participants aged 65 and older, efficacy was 86.4%. The trial included 30,420 adult participants.",
        "prompt": "Based on the context, what was the vaccine's efficacy?",
        "ground_truth": "The vaccine showed 94.1% overall efficacy, and 86.4% efficacy among participants aged 65 and older, in a trial of 30,420 adults.",
    },
]

# ---------------------------------------------------------------------------
# Consistency prompt pairs (same question, different phrasing)
# ---------------------------------------------------------------------------

CONSISTENCY_PROMPT_PAIRS: List[Tuple[str, str]] = [
    (
        "What is the capital of France?",
        "Which city serves as France's capital?",
    ),
    (
        "How many planets are in our solar system?",
        "What is the total number of planets orbiting the Sun?",
    ),
    (
        "Who invented the telephone?",
        "Which inventor is credited with creating the telephone?",
    ),
    (
        "What causes seasons on Earth?",
        "Why do we experience different seasons throughout the year?",
    ),
    (
        "What is the largest ocean on Earth?",
        "Which ocean covers the most area on our planet?",
    ),
    (
        "When did the first aeroplane fly?",
        "In what year did the Wright brothers achieve powered flight?",
    ),
    (
        "What is photosynthesis?",
        "Explain the process by which plants convert sunlight into energy.",
    ),
    (
        "Who wrote Romeo and Juliet?",
        "Which playwright authored the tragedy Romeo and Juliet?",
    ),
    (
        "What is the tallest mountain in the world?",
        "Which mountain has the highest elevation above sea level?",
    ),
    (
        "What is DNA?",
        "Explain what deoxyribonucleic acid is and its role in biology.",
    ),
]

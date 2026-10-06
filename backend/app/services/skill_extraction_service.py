"""
Rule-based skill extraction and normalization.

This is intentionally NOT LLM-based: skill extraction for well-known,
common tech skills should be fast, free, deterministic and testable. An
AI provider (see ai_service.py, later stage) can be layered on top later
for open-ended / fuzzy skill discovery, but the baseline recognition of
"Python", "React", "Docker", etc. must work without ever calling an LLM.

How it works
------------
`SKILL_TAXONOMY` is an ordered list of (canonical_name, [regex_patterns]).
Each pattern is matched case-insensitively against free text (job
descriptions, resumes, user-typed skill strings). Patterns are written to:

  * tolerate common spacing/casing variations, e.g.
      "Py Torch" / "pytorch" / "PyTorch"      -> "PyTorch"
      "machine learning" / "ML"                -> "Machine Learning"
      "python programming" / "Python"          -> "Python"
  * use word boundaries so short/ambiguous tokens don't over-match inside
    longer unrelated words (e.g. "git" must not match inside "digital")

Two entry points are exposed:
  * extract_skills(text)        -> all canonical skills found in a blob of
                                    text (e.g. a job description)
  * normalize_skill_name(raw)   -> best-effort canonical name for a single
                                    user-typed skill string (falls back to
                                    the cleaned original if unrecognized,
                                    so we never silently drop a skill the
                                    user told us they have)
"""
from __future__ import annotations

import re
from typing import List, Optional, Pattern, Tuple

# Ordered: more specific / multi-word patterns first so they take priority
# over shorter substrings when normalizing a single short user-typed string.
_RAW_TAXONOMY: List[Tuple[str, List[str]]] = [
    ("Machine Learning", [r"\bmachine\s*learning\b", r"\bml\b"]),
    ("Deep Learning", [r"\bdeep\s*learning\b"]),
    ("Natural Language Processing", [r"\bnatural\s*language\s*processing\b", r"\bnlp\b"]),
    ("Computer Vision", [r"\bcomputer\s*vision\b"]),
    ("Large Language Models", [r"\blarge\s*language\s*models?\b", r"\bllms?\b"]),
    ("RAG", [r"\bretrieval[\s-]?augmented\s*generation\b", r"\brag\b"]),
    ("Prompt Engineering", [r"\bprompt\s*engineering\b"]),
    ("LangChain", [r"\blang\s*chain\b"]),
    ("Vector Databases", [r"\bvector\s*(database|store|db)s?\b", r"\bpinecone\b", r"\bweaviate\b", r"\bchroma\s*db\b"]),
    ("Hugging Face", [r"\bhugging\s*face\b"]),
    ("PyTorch", [r"\bpy\s*torch\b"]),
    ("TensorFlow", [r"\btensor\s*flow\b"]),
    ("Keras", [r"\bkeras\b"]),
    ("Scikit-learn", [r"\bscikit[\s-]?learn\b", r"\bsklearn\b"]),
    ("Pandas", [r"\bpandas\b"]),
    ("NumPy", [r"\bnumpy\b"]),
    ("Apache Spark", [r"\bapache\s*spark\b", r"\bspark\b"]),
    ("Hadoop", [r"\bhadoop\b"]),
    ("Kafka", [r"\bkafka\b"]),
    ("FastAPI", [r"\bfast\s*api\b"]),
    ("Django", [r"\bdjango\b"]),
    ("Flask", [r"\bflask\b"]),
    ("Node.js", [r"\bnode\.?\s*js\b"]),
    ("TypeScript", [r"\btypescript\b"]),
    ("JavaScript", [r"\bjavascript\b", r"\bjs\b"]),
    ("React", [r"\breact\.?js\b", r"\breact\b"]),
    ("Next.js", [r"\bnext\.?\s*js\b"]),
    ("Vue.js", [r"\bvue\.?\s*js\b", r"\bvue\b"]),
    ("Angular", [r"\bangular(?:js)?\b"]),
    ("HTML", [r"\bhtml5?\b"]),
    ("CSS", [r"\bcss3?\b"]),
    ("Tailwind CSS", [r"\btailwind(?:\s*css)?\b"]),
    ("Python", [r"\bpython\b"]),
    ("Java", [r"\bjava\b"]),
    ("C\\+\\+", [r"(?<![a-z0-9])c\+\+"]),
    ("C#", [r"(?<![a-z0-9])c#"]),
    # Bare "Go" is deliberately excluded from free-text extraction (too
    # ambiguous against the common English word "go"); only unambiguous
    # forms are recognized.
    ("Go", [r"\bgolang\b", r"\bgo\s*programming\b", r"\bgo\s*lang\b"]),
    ("Rust", [r"\brust\b"]),
    ("Swift", [r"\bswift\b"]),
    ("Kotlin", [r"\bkotlin\b"]),
    ("PHP", [r"\bphp\b"]),
    ("Ruby", [r"\bruby\b"]),
    ("Ruby on Rails", [r"\bruby\s*on\s*rails\b", r"\brails\b"]),
    ("SQL", [r"\bsql\b"]),
    ("PostgreSQL", [r"\bpostgres(?:ql)?\b"]),
    ("MySQL", [r"\bmysql\b"]),
    ("MongoDB", [r"\bmongo\s*db\b"]),
    ("Redis", [r"\bredis\b"]),
    ("GraphQL", [r"\bgraphql\b"]),
    ("REST APIs", [r"\brest(?:ful)?\s*api(?:s)?\b"]),
    ("Docker", [r"\bdocker\b"]),
    ("Kubernetes", [r"\bkubernetes\b", r"\bk8s\b"]),
    ("Terraform", [r"\bterraform\b"]),
    ("Ansible", [r"\bansible\b"]),
    ("Jenkins", [r"\bjenkins\b"]),
    ("CI/CD", [r"\bci\/cd\b", r"\bci\s*cd\b", r"\bcontinuous\s*integration\b"]),
    ("AWS", [r"\baws\b", r"\bamazon\s*web\s*services\b"]),
    ("Azure", [r"\bazure\b"]),
    ("GCP", [r"\bgcp\b", r"\bgoogle\s*cloud(?:\s*platform)?\b"]),
    ("Linux", [r"\blinux\b"]),
    ("Git", [r"\bgit\b"]),
    ("GitHub", [r"\bgithub\b"]),
    ("Microservices", [r"\bmicroservices?\b"]),
    ("System Design", [r"\bsystem\s*design\b"]),
    ("Data Structures & Algorithms", [r"\bdata\s*structures?\b", r"\balgorithms?\b"]),
    ("Agile", [r"\bagile\b"]),
    ("Scrum", [r"\bscrum\b"]),
    ("Excel", [r"\bexcel\b"]),
    ("Tableau", [r"\btableau\b"]),
    ("Power BI", [r"\bpower\s*bi\b"]),
]

# Pre-compile all patterns once at import time.
_COMPILED_TAXONOMY: List[Tuple[str, List[Pattern[str]]]] = [
    (canonical, [re.compile(pattern, re.IGNORECASE) for pattern in patterns])
    for canonical, patterns in _RAW_TAXONOMY
]


def extract_skills(text: Optional[str]) -> List[str]:
    """
    Extract all recognized canonical skills mentioned in a blob of text
    (e.g. a job description). Returns canonical names in taxonomy order,
    deduplicated. Returns [] for empty/None input — never raises.
    """
    if not text:
        return []

    found: List[str] = []
    for canonical, patterns in _COMPILED_TAXONOMY:
        if any(pattern.search(text) for pattern in patterns):
            found.append(canonical)
    return found


def normalize_skill_name(raw_skill: str) -> str:
    """
    Best-effort normalization of a single, short user-typed skill string
    to its canonical taxonomy name (e.g. "ML" -> "Machine Learning",
    "Py Torch" -> "PyTorch", "python programming" -> "Python").

    If the string doesn't match any known skill, the cleaned original is
    returned unchanged (title-cased if it was all lower/upper case) rather
    than dropped, so a user's custom/niche skill is never silently lost.
    """
    cleaned = raw_skill.strip()
    if not cleaned:
        return cleaned

    for canonical, patterns in _COMPILED_TAXONOMY:
        for pattern in patterns:
            # Use fullmatch-ish behavior for short user input: require the
            # pattern to explain a meaningful portion of the string rather
            # than an incidental substring match deep inside a longer phrase.
            if pattern.search(cleaned):
                return canonical

    if cleaned.islower() or cleaned.isupper():
        return cleaned.title()
    return cleaned


def normalize_skill_list(raw_skills: List[str]) -> List[str]:
    """Normalize a list of user-typed skills, de-duplicating case-insensitively."""
    seen = set()
    normalized: List[str] = []
    for raw in raw_skills:
        canonical = normalize_skill_name(raw)
        key = canonical.lower()
        if canonical and key not in seen:
            seen.add(key)
            normalized.append(canonical)
    return normalized

"""Text preprocessing: tokenize, normalize, remove stop-words, stem.

The Porter stemmer is implemented inline (a faithful reduction of Martin
Porter's 1980 algorithm) so the module has no hard dependency on NLTK.
If NLTK is installed we use it for a richer English stop-word list.
"""

from __future__ import annotations

import re
from typing import List, Optional, Set

from .config import DEFAULT_CONFIG, EngineConfig


_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")


def _load_stopwords(cfg: EngineConfig) -> Set[str]:
    if not cfg.remove_stopwords:
        return set()
    try:
        from nltk.corpus import stopwords as nltk_sw  # type: ignore

        return set(nltk_sw.words("english")) | cfg.stopwords
    except Exception:
        return set(cfg.stopwords)


# --- Porter stemmer (compact implementation) -------------------------------
_VOWELS = set("aeiou")


def _is_consonant(word: str, i: int) -> bool:
    ch = word[i]
    if ch in _VOWELS:
        return False
    if ch == "y":
        return i == 0 or not _is_consonant(word, i - 1)
    return True


def _measure(stem: str) -> int:
    """Number of VC patterns in `stem` — the `m` value from Porter's paper."""
    n = len(stem)
    m, i = 0, 0
    # Skip leading consonants.
    while i < n and _is_consonant(stem, i):
        i += 1
    while i < n:
        # Skip vowels.
        while i < n and not _is_consonant(stem, i):
            i += 1
        if i == n:
            break
        m += 1
        # Skip consonants.
        while i < n and _is_consonant(stem, i):
            i += 1
    return m


def _ends(word: str, suffix: str) -> bool:
    return word.endswith(suffix)


def _replace(word: str, suffix: str, replacement: str) -> str:
    return word[: len(word) - len(suffix)] + replacement


def _contains_vowel(stem: str) -> bool:
    return any(not _is_consonant(stem, i) for i in range(len(stem)))


def porter_stem(word: str) -> str:
    """A compact Porter stemmer covering the common cases.

    This is not a perfect reproduction — it covers steps 1a, 1b, and 1c plus
    the most common reductions in steps 2-4, which is enough for an
    educational search engine. For production use, prefer NLTK's stemmer.
    """
    if len(word) <= 2:
        return word
    w = word

    # Step 1a
    if _ends(w, "sses"):
        w = _replace(w, "sses", "ss")
    elif _ends(w, "ies"):
        w = _replace(w, "ies", "i")
    elif _ends(w, "ss"):
        pass
    elif _ends(w, "s"):
        w = w[:-1]

    # Step 1b
    if _ends(w, "eed"):
        if _measure(w[:-3]) > 0:
            w = w[:-1]
    else:
        for suf in ("ed", "ing"):
            if _ends(w, suf) and _contains_vowel(w[: -len(suf)]):
                w = w[: -len(suf)]
                if _ends(w, ("at", "bl", "iz")):
                    w += "e"
                elif (
                    len(w) >= 2
                    and w[-1] == w[-2]
                    and w[-1] not in ("l", "s", "z")
                    and _is_consonant(w, len(w) - 1)
                ):
                    w = w[:-1]
                break

    # Step 1c: y -> i
    if _ends(w, "y") and _contains_vowel(w[:-1]):
        w = w[:-1] + "i"

    # Compact step 2/4 — drop a few common derivational suffixes.
    for suf, repl in (
        ("ational", "ate"), ("tional", "tion"), ("ization", "ize"),
        ("fulness", "ful"), ("ousness", "ous"), ("iveness", "ive"),
        ("ement", ""), ("ment", ""), ("ence", ""), ("ance", ""),
        ("able", ""), ("ible", ""), ("ation", "ate"), ("ator", "ate"),
        ("alism", "al"), ("ities", "ity"), ("ity", ""),
    ):
        if _ends(w, suf) and _measure(w[: -len(suf)]) > 0:
            w = _replace(w, suf, repl)
            break

    # Step 5a: drop final e if measure > 1
    if _ends(w, "e") and _measure(w[:-1]) > 1:
        w = w[:-1]
    return w


# --- Public API ------------------------------------------------------------

class Preprocessor:
    """Reusable, configured pipeline for cleaning text into tokens."""

    def __init__(self, config: Optional[EngineConfig] = None) -> None:
        self.config = config or DEFAULT_CONFIG
        self._stopwords = _load_stopwords(self.config)

    @property
    def stopwords(self) -> Set[str]:
        return self._stopwords

    def tokenize(self, text: str) -> List[str]:
        return _TOKEN_RE.findall((text or "").lower())

    def normalize(self, tokens: List[str]) -> List[str]:
        cfg = self.config
        out: List[str] = []
        for tok in tokens:
            if len(tok) < cfg.min_token_length:
                continue
            if tok in self._stopwords:
                continue
            if cfg.use_stemming:
                tok = porter_stem(tok)
                if not tok or len(tok) < cfg.min_token_length:
                    continue
            out.append(tok)
        return out

    def process(self, text: str) -> List[str]:
        return self.normalize(self.tokenize(text))

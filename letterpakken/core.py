import re
from pathlib import Path
from typing import Iterable, List

from ._typing import LetterSet

INF: int = 10**9


def load_words(path: Path) -> List[str]:
    """
    Load words from a file, stripping whitespace and discarding empties.

    Parameters
    ----------
    path : Path
        Path to the word list file.

    Returns
    -------
    list of str
        Raw words (not yet filtered).
    """
    words: List[str] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            w = line.strip()
            if w:
                words.append(w)
    return words


def filter_words(words: Iterable[str], letter_sets: List[LetterSet]) -> List[str]:
    """
    Filter words using the game's simple regex (alphabet + exact length).

    Parameters
    ----------
    words : iterable of str
        Candidate words.
    letter_sets : list of tuple of str
        Letter choices per set (each entry is a tuple of single-character options).

    Returns
    -------
    list of str
        Words whose length equals the number of sets and whose letters are all
        drawn from the union of the sets.
    """
    k: int = len(letter_sets)
    alphabet: List[str] = sorted({ch for group in letter_sets for ch in group})
    charclass: str = "".join(re.escape(c) for c in alphabet)
    rx: re.Pattern[str] = re.compile(rf"^[{charclass}]{{{k}}}$")

    return [w for w in words if rx.fullmatch(w)]


def validate_sets(sets):
    """
    Validate sets of letters provided by the user.

    Parameters
    ----------
    sets : list of str
        A list of strings where each string is a set of lowercase letters.

    Raises
    ------
    ValueError
        If any set is empty or contains invalid characters.
    """
    for s in sets:
        if not s:
            raise ValueError("Empty set provided.")
        if not re.fullmatch(r"[a-z]+", s):
            raise ValueError(
                f"Set '{s}' contains invalid characters. Use only lowercase a-z."
            )

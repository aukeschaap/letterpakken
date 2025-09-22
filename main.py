import argparse
import itertools
import re
import sys
from pathlib import Path

import pandas as pd


def load_words(path: Path) -> pd.Series:
    """
    Load a word list and optionally filter it to 4–5 letter lowercase words.

    Parameters
    ----------
    path : Path
        Path to the word list file. If `wordlist45.txt` exists, it will be
        used directly. Otherwise, `wordlist.txt` is loaded and filtered.

    Returns
    -------
    pd.Series
        Series of words (strings), either pre-filtered or newly filtered
        to only include 4–5 letter lowercase alphabetic words.

    Notes
    -----
    - If filtering is applied, the filtered word list is saved to
      `wordlist45.txt` in the same directory as the source file.
    """
    path = Path("./wordlist45.txt")
    if path.is_file():
        print(f"Loading words from {path}")
        already_filtered = True
    else:
        print("Loading default word list from ./wordlist.txt")
        path = Path("./data/wordlist.txt")
        already_filtered = False

    df = pd.read_csv(
        path, header=None, names=["word"], dtype=str, keep_default_na=False
    )
    words = df["word"].str.strip()
    words = words[words != ""]

    if already_filtered:
        return words

    # Filter
    pattern = re.compile(r"^[a-z]{4,5}$")
    filtered = words[words.apply(lambda w: bool(pattern.match(w)))]

    # Save
    out_path = path.parent / "wordlist45.txt"
    filtered.to_csv(out_path, index=False, header=False)
    print(f"Saved filtered words of length 4-5 to {out_path}")

    return filtered


def validate_sets(sets):
    """
    Validate sets of mutually exclusive letters.

    Parameters
    ----------
    sets : list of str
        A list of strings where each string is a set of mutually exclusive
        lowercase letters.

    Raises
    ------
    ValueError
        If any set is empty, contains invalid characters, or shares
        letters with another set.
    """
    # Ensure all sets are non-empty and contain only lowercase a-z
    for s in sets:
        if not s:
            raise ValueError("Empty set provided.")
        if not re.fullmatch(r"[a-z]+", s):
            raise ValueError(
                f"Set '{s}' contains invalid characters. Use only lowercase a-z."
            )
    # Ensure sets are pairwise disjoint
    all_letters = "".join(sets)
    if len(set(all_letters)) != len(all_letters):
        dupes = [ch for ch in set(all_letters) if all_letters.count(ch) > 1]
        raise ValueError(
            f"Letter(s) {dupes} appear in multiple sets. Sets should be disjoint."
        )


def build_regex_from_sets(sets, minlen=4, maxlen=5):
    """
    Build a regex pattern based on sets of mutually exclusive letters.

    The regex enforces:
      - Only letters from the union of sets are used.
      - No letter repeats globally.
      - No more than one letter from the same set is used.
      - Word length must be between `minlen` and `maxlen`.

    Parameters
    ----------
    sets : list of str
        List of sets of mutually exclusive lowercase letters.
    minlen : int, optional
        Minimum word length (default is 4).
    maxlen : int, optional
        Maximum word length (default is 5).

    Returns
    -------
    str
        A regex pattern string.

    Raises
    ------
    ValueError
        If the sets are invalid (see `validate_sets`).
    """
    validate_sets(sets)

    alphabet = sorted(set("".join(sets)))
    charclass = "".join(alphabet)

    lookaheads = []

    # 1) Forbid co-occurrence of two different letters from the same set;
    #    For each unordered pair (x, y) in the set, disallow both x...y and y...x.
    for s in sets:
        for a, b in itertools.combinations(s, 2):
            lookaheads.append(
                f"(?!(?:.*{re.escape(a)}.*{re.escape(b)}|.*{re.escape(b)}.*{re.escape(a)}))"
            )

     # 2) Forbid repeats globally
    lookaheads.append(f"(?!.*([{re.escape(charclass)}]).*\\1)")

    # 3) Final body: only letters from union and within length bounds
    body = f"[{re.escape(charclass)}]" + "{" + f"{minlen},{maxlen}" + "}"

    pattern = "^" + "".join(lookaheads) + body + "$"
    return pattern


def main():
    """
    Entry point for the command-line tool.

    Parses command-line arguments, loads words, builds the regex pattern
    from provided sets, applies it to filter valid matches, and prints
    or saves the results.

    Command-line Arguments
    ----------------------
    --set : str
        A set of mutually exclusive letters (lowercase a-z).
        May be passed multiple times.
    --minlen : int, optional
        Minimum word length (default: 4).
    --maxlen : int, optional
        Maximum word length (default: 5).
    --out : Path, optional
        Path to save the matched words (one per line).
    """
    p = argparse.ArgumentParser()
    p.add_argument(
        "--set",
        dest="sets",
        action="append",
        required=True,
        help="A set of mutually exclusive letters (lowercase a-z). Use multiple --set arguments.",
    )
    p.add_argument(
        "--minlen", type=int, default=4, help="Minimum word length (default: 4)"
    )
    p.add_argument(
        "--maxlen", type=int, default=5, help="Maximum word length (default: 5)"
    )
    p.add_argument(
        "--out", type=Path, help="Optional file to save matches (one per line)"
    )
    args = p.parse_args()

    words = load_words("./wordlist.txt")
    print(f"Words of length 4-5: {len(words)}")

    print("Matching...")
    try:
        print(f"  Sets: {args.sets}")
        pattern_str = build_regex_from_sets(args.sets, args.minlen, args.maxlen)
    except ValueError as e:
        print(f"Config error: {e}", file=sys.stderr)
        sys.exit(1)

    # Compile regex
    pattern = re.compile(pattern_str)

    # Filter words matching the pattern
    matches = words[words.apply(lambda w: bool(pattern.match(w)))]

    print(f"  Total matches: {len(matches)}")
    print("  First 50:")
    print(matches.iloc[:50].to_list())

    if args.out:
        matches.to_csv(args.out, index=False, header=False)
        print(f"  Saved {len(matches)} matches to {args.out}")


if __name__ == "__main__":
    main()

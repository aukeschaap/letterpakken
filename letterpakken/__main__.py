from pathlib import Path
from typing import List, Optional

import typer

from ._typing import LetterSet
from .core import filter_words, load_words, validate_sets
from .matching import is_valid

app = typer.Typer(add_completion=False)


@app.command()
def main(
    sets: List[LetterSet] = typer.Option(
        ...,
        "--set",
        "-s",
        help="A set of mutually exclusive letters (lowercase a-z). Repeat for multiple sets.",
    ),
    minlen: int = typer.Option(4, help="Minimum word length."),
    maxlen: int = typer.Option(5, help="Maximum word length."),
    out: Optional[Path] = typer.Option(
        None, "--out", help="Optional file to save matches (one per line)."
    ),
    wordlist: Path = typer.Option(
        Path("./data/wordlist.txt"), "--wordlist", help="Path to word list file."
    ),
):
    """
    Entry point for the command-line tool.

    Parses command-line arguments, loads words, filters by length, applies
    the sets constraint, and prints or saves the results.
    """
    # Validate sets
    try:
        validate_sets(sets)
    except ValueError as e:
        typer.secho(f"Config error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    # Print sets
    typer.echo(f"Sets : {sets}")

    # Load and filter words
    typer.echo(f"Loading words from {wordlist}...")
    words = load_words(wordlist)
    typer.echo(f"Total words loaded: {len(words)}")
    words = filter_words(words, sets)
    typer.echo(f"Words participating in matching: {len(words)}")

    # Match
    typer.echo("Matching...")
    matches = [w for w in words if is_valid(w, sets)]

    typer.echo(f"  Total matches: {len(matches)}")
    preview = matches[:20]
    if preview:
        typer.echo("  First 20:")
        typer.echo(preview)

    # Optional save
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as f:
            for w in matches:
                f.write(f"{w}\n")
        typer.echo(f"  Saved {len(matches)} matches to {out}")


if __name__ == "__main__":
    app()

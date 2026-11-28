"""Compare a job offer with a CV: which skills of the offer are already on the page,
which ones wait in the Reserve (commented lines of the .tex), which ones are missing.

From the repository root:

    make match OFFER=path/to/offer.txt
    uv run scripts/match_offer.py path/to/offer.txt --cv src/en/cv-dmytro-palahin-en-d.tex
    pbpaste | make match OFFER=-          # the offer copied from the browser (macOS)

The offer is a text file (or a PDF, read with Poppler). Nothing leaves the machine.

Only the skills listed in scripts/skills.txt are recognised: add a line there for a term
the report misses. With several --cv files, the one written in the language of the offer
is used.
"""

import argparse
import bisect
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import re
import shutil
import subprocess
import sys
import unicodedata

from cvtext import Line, normalise, source_lines

SHORT = 2  # a spelling this short is matched with its case: Go, BI
LINES_SHOWN = 4  # line numbers printed for a skill of the Reserve
TIMES = "\u00d7"  # multiplication sign
# Small words that tell a French text from an English one.
FRENCH: set[str] = {
    "le",
    "la",
    "les",
    "des",
    "et",
    "pour",
    "vous",
    "nous",
    "une",
    "avec",
    "dans",
    "sur",
}
ENGLISH = {
    "the",
    "and",
    "for",
    "you",
    "with",
    "our",
    "of",
    "to",
    "in",
    "is",
    "are",
    "will",
}
BABEL = {
    "french": "fr",
    "francais": "fr",
    "english": "en",
    "american": "en",
    "british": "en",
}


# ---------- Skills ----------


def plain(text: str) -> str:
    """Text ready for matching: same characters everywhere, no accents."""
    decomposed = unicodedata.normalize("NFKD", normalise(text))
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def spelling_pattern(spelling: str) -> re.Pattern[str]:
    """Regular expression that finds one spelling of a skill in a text.

    - a space, a hyphen or a slash between two words is optional: "Power BI" finds "PowerBI"
    - a final "s" is accepted: "LLM" finds "LLMs"
    - case is ignored, except for spellings of 1 or 2 letters (Go, BI, R)
    - a single letter (C, R) must stand alone: not in "C++", "C#" or "R&D"
    """
    spelling = plain(spelling)
    body = r"[\s/-]*".join(
        re.escape(part) for part in re.split(r"[\s/-]+", spelling) if part
    )
    if len(spelling) == 1:
        return re.compile(rf"(?<![\w&'.-]){body}(?![\w+#&'.-])")
    short = len(spelling) <= SHORT and spelling.isalpha()
    return re.compile(rf"(?<!\w){body}s?(?![\w+#])", 0 if short else re.IGNORECASE)


def read_skills(path: Path) -> dict[str, list[str]]:
    """Skills file: one skill per line, "Name | other spelling | ..."; "#" starts a comment."""
    skills: dict[str, list[str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("#"):
            continue
        spellings = [part.strip() for part in line.split("|") if part.strip()]
        if spellings:
            skills.setdefault(spellings[0], []).extend(spellings)
    return skills


def find_skills(text: str, skills: dict[str, list[str]]) -> dict[str, list[int]]:
    """Positions of every skill in ``text``.

    Longer spellings are searched first and each part of the text counts once, so that
    "tableau de bord" (a dashboard) is not also counted as the tool Tableau.
    """
    text = plain(text)
    taken = [False] * len(text)
    found: dict[str, list[int]] = {}
    spellings = [
        (spelling, name) for name, group in skills.items() for spelling in group
    ]
    for spelling, name in sorted(spellings, key=lambda pair: -len(pair[0])):
        for match in spelling_pattern(spelling).finditer(text):
            start, end = match.span()
            if not any(taken[start:end]):
                taken[start:end] = [True] * (end - start)
                found.setdefault(name, []).append(start)
    return found


# ---------- The offer and the CV ----------


def read_offer(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    file = Path(path)
    if file.suffix.lower() == ".pdf":
        if shutil.which("pdftotext") is None:
            raise SystemExit(
                "error: 'pdftotext' not found: install Poppler to read a PDF offer"
            )
        command = ["pdftotext", str(file), "-"]
        return subprocess.run(
            command, capture_output=True, text=True, check=True
        ).stdout
    return file.read_text(encoding="utf-8")


def language_of(text: str) -> str:
    """ "fr" or "en", from the most common small words of the text."""
    words = Counter(re.findall(r"[a-zà-ÿ]+", text.lower()))
    french = sum(words[word] for word in FRENCH)
    english = sum(words[word] for word in ENGLISH)
    return "fr" if french > english else "en"


def cv_language(tex: Path) -> str:
    """Language of a CV, from the last option of its babel package."""
    found = re.search(
        r"\\usepackage\[([^\]]*)\]\{babel\}", tex.read_text(encoding="utf-8")
    )
    last = found.group(1).split(",")[-1].strip() if found else ""
    return BABEL.get(last, "")


@dataclass
class Side:
    """The lines of the CV that are on the page, or the commented ones, as one text."""

    text: str
    starts: list[int]  # position in ``text`` where each line starts
    numbers: list[int]  # line number of each line in the .tex file

    @classmethod
    def of(cls, lines: list[Line]) -> "Side":
        starts, numbers, parts, position = [], [], [], 0
        for line in lines:
            text = plain(line.text)
            starts.append(position)
            numbers.append(line.number)
            parts.append(text)
            position += len(text) + 1
        return cls("\n".join(parts), starts, numbers)

    def line_of(self, position: int) -> int:
        return self.numbers[bisect.bisect_right(self.starts, position) - 1]


@dataclass
class Match:
    name: str
    mentions: int  # times the skill appears in the offer
    lines: list[int]  # lines of the .tex where it is found


def compare(
    offer: str, tex: Path, skills: dict[str, list[str]]
) -> dict[str, list[Match]]:
    """Skills of the offer, sorted into "page", "reserve" and "missing"."""
    lines = source_lines(tex, body_only=True)
    page = Side.of([line for line in lines if not line.comment])
    reserve = Side.of([line for line in lines if line.comment])
    on_page = find_skills(page.text, skills)
    in_reserve = find_skills(reserve.text, skills)

    result: dict[str, list[Match]] = {"page": [], "reserve": [], "missing": []}
    wanted = find_skills(offer, skills)
    for name in sorted(wanted, key=lambda name: (-len(wanted[name]), name.lower())):
        mentions = len(wanted[name])
        if name in on_page:
            numbers = sorted({page.line_of(position) for position in on_page[name]})
            result["page"].append(Match(name, mentions, numbers))
        elif name in in_reserve:
            numbers = sorted(
                {reserve.line_of(position) for position in in_reserve[name]}
            )
            result["reserve"].append(Match(name, mentions, numbers))
        else:
            result["missing"].append(Match(name, mentions, []))
    return result


# ---------- Output ----------


def label(match: Match) -> str:
    """Name of a skill, with the number of times the offer mentions it."""
    return match.name + (f" {TIMES}{match.mentions}" if match.mentions > 1 else "")


def names(matches: list[Match]) -> str:
    return ", ".join(label(match) for match in matches)


def wrapped(text: str, indent: str = "        ", width: int = 96) -> str:
    out, line = [], indent
    for item in text.split(", "):
        piece = item + ", "
        if len(line) + len(piece) > width and line.strip():
            out.append(line.rstrip())
            line = indent
        line += piece
    out.append(line.rstrip().rstrip(","))
    return "\n".join(out)


def report(offer_name: str, tex: Path, result: dict[str, list[Match]]) -> None:
    page, reserve, missing = result["page"], result["reserve"], result["missing"]
    total = len(page) + len(reserve) + len(missing)
    print(f"==> {offer_name} against {tex}")
    if not total:
        print("    no known skill found: is this the text of a job offer?")
        return
    print(f"\n    In the CV ({len(page)})")
    if page:
        print(wrapped(names(page)))
    print(
        f"\n    In the Reserve only ({len(reserve)}): commented lines to enable if they fit"
    )
    for match in reserve:
        shown = ", ".join(str(number) for number in match.lines[:LINES_SHOWN])
        more = "..." if len(match.lines) > LINES_SHOWN else ""
        word = "line" if len(match.lines) == 1 else "lines"
        print(f"        {label(match):<26} {word} {shown}{more}")
    print(f"\n    Not in the CV ({len(missing)})")
    if missing:
        print(wrapped(names(missing)))
    share = round(100 * len(page) / total)
    print(
        f"\n    {len(page)} of the {total} skills of the offer are on the page ({share} %)"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare a job offer with a CV.")
    parser.add_argument(
        "offer", help="text or PDF file of the offer, or - for standard input"
    )
    parser.add_argument(
        "--cv",
        action="append",
        type=Path,
        required=True,
        metavar="TEX",
        help=".tex source of a CV; with several, the one in the language of the offer is used",
    )
    parser.add_argument(
        "--skills",
        type=Path,
        default=Path(__file__).with_name("skills.txt"),
        help="list of the skills to recognise (default: scripts/skills.txt)",
    )
    args = parser.parse_args()

    for file in [*args.cv, args.skills] + (
        [] if args.offer == "-" else [Path(args.offer)]
    ):
        if not file.is_file():
            print(f"error: {file} not found", file=sys.stderr)
            return 2

    offer = read_offer(args.offer)
    skills = read_skills(args.skills)
    language = language_of(offer)
    same_language = [tex for tex in args.cv if cv_language(tex) == language]
    offer_name = "the offer" if args.offer == "-" else args.offer
    for index, tex in enumerate(same_language or args.cv):
        if index:
            print()
        report(offer_name, tex, compare(offer, tex, skills))
    return 0


if __name__ == "__main__":
    sys.exit(main())

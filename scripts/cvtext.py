"""Text helpers shared by the scripts: words of a text, and the .tex source of a CV as plain text.

The .tex source is read line by line. A line that starts with "%" is a comment: in this
repository the comments hold the Reserve, lines kept ready for another job offer. The other
lines are what is printed on the page.
"""

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import re
import unicodedata

# A word: letters and digits, with the signs found inside or at the end of technical terms
# (C/C++, CI/CD, TF-IDF, 99.1%, github.com/name, name@host).
WORD = re.compile(r"[^\W_]+(?:[+#./'&@:-]+[^\W_]+)*[+#%]*")

# LaTeX commands of the template that stand for a character.
SYMBOLS = {
    "\\textperiodcentered": "·",
    "\\textbullet": "•",
    "\\nbrealspace": " ",
    "\\realspace": " ",
    "\\dotsep": " · ",
    "\\sep": " | ",
    "\\&": "&",
    "\\%": "%",
    "\\#": "#",
    "\\$": "$",
    "\\_": "_",
    "---": "\u2014",  # em dash
    "--": "\u2013",  # en dash
    "~": " ",
}
# A command name ends where its letters end: \sep must not match the start of \separator.
SYMBOL = re.compile(
    "|".join(
        re.escape(symbol) + (r"(?![A-Za-z])" if symbol[-1].isalpha() else "")
        for symbol in SYMBOLS
    )
)


def normalise(text: str) -> str:
    """Same characters whatever the source: composed accents, plain apostrophes and spaces."""
    text = unicodedata.normalize("NFKC", text)
    return text.replace("\u2019", "'").replace("\u00ad", "")


def squeeze(text: str) -> str:
    """One space between words, so that a phrase is found even across a line break."""
    return " ".join(text.split())


def words_of(text: str) -> Counter[str]:
    return Counter(WORD.findall(text))


def detex(line: str) -> str:
    """A line of the .tex source as it reads on the page: A{}WS -> AWS, \\B{text} -> text."""
    line = re.sub(
        r"\\href\{[^{}]*\}", "", line
    )  # the address of a link is not on the page
    line = re.sub(r"\{https?://[^{}]*\}", " ", line)
    line = SYMBOL.sub(lambda found: SYMBOLS[found.group()], line)
    line = line.replace("{}", "")  # A{}WS: the empty group only breaks kerning
    line = re.sub(r"\\[A-Za-z@]+\*?", " ", line)
    line = line.replace("}{", " ")  # two arguments in a row are two pieces of text
    return normalise(line.replace("{", "").replace("}", ""))


@dataclass(frozen=True)
class Line:
    number: int  # line number in the .tex file, from 1
    comment: bool  # True: the whole line is commented out
    text: str  # plain text, without LaTeX commands


def source_lines(tex: Path, body_only: bool = False) -> list[Line]:
    """Lines of a .tex source as plain text; ``body_only`` keeps what is inside the document."""
    lines = []
    inside = not body_only
    for number, raw in enumerate(tex.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = raw.strip()
        if stripped.startswith("\\end{document}"):
            break
        if stripped.startswith("\\begin{document}"):
            inside = True
            continue
        if not inside or not stripped:
            continue
        if stripped.startswith("%"):
            lines.append(Line(number, True, detex(stripped.lstrip("% "))))
        else:
            code = re.sub(r"(?<!\\)%.*$", "", raw)  # a comment at the end of the line
            lines.append(Line(number, False, detex(code)))
    return lines

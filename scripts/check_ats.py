"""Check that PDF text extractors read the CV the way a recruiter does.

An applicant tracking system (ATS) starts by extracting the text of the PDF. Each CV is read
here with six independent extractors, and what they return is compared:

    Poppler (pdftotext), pypdf, pdfminer.six, pdfplumber, PyMuPDF, PDFium (pypdfium2)

From the repository root:

    make ats
    uv run scripts/check_ats.py src/en/cv-dmytro-palahin-en-d.pdf

Checks on the document:
    - number of pages (--pages, default 1)
    - every font is embedded and has a Unicode map
    - title, author, subject, keywords and language are set in the metadata
    - the keywords of the metadata are in the text of the page (warning otherwise)

Checks with each extractor:
    - the text starts with the name of the author
    - the email address behind the "mailto:" link is in the text
    - no unreadable character
    - the keywords of the metadata are found
    - the words are the same as with the other extractors
    - with the .tex source next to the PDF: every word read from the PDF is a word of the
      source (no word glued to its neighbour, cut in two or hyphenated), and the section
      headings come in the same order

Exit status: 1 when a check fails, 0 otherwise. In GitHub Actions, the results are also
written to the job summary.
"""

import argparse
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
import importlib.metadata
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import unicodedata

from pdfminer.high_level import extract_text as pdfminer_extract_text
import pdfplumber
import pymupdf
import pypdf
import pypdfium2

from cvtext import detex, normalise, source_lines, squeeze, words_of

MIN_WORDS = 50  # fewer different words than this: the page was not really read
SAMPLE = 6  # words shown when two readings differ
# Section headings in the .tex source of this template.
HEADING: re.Pattern[str] = re.compile(
    pattern=r"^\s*\\cvsection\{(.*)\}\s*$", flags=re.MULTILINE
)


# ---------- The extractors ----------


def read_poppler(pdf: Path) -> str:
    done: subprocess.CompletedProcess[str] = subprocess.run(
        args=["pdftotext", str(object=pdf), "-"],
        capture_output=True,
        text=True,
        check=True,
    )
    return done.stdout


def read_pypdf(pdf: Path) -> str:
    return "\n".join(page.extract_text() for page in pypdf.PdfReader(pdf).pages)


def read_pdfminer(pdf: Path) -> str:
    return pdfminer_extract_text(pdf)


def read_pdfplumber(pdf: Path) -> str:
    with pdfplumber.open(pdf) as document:
        return "\n".join(page.extract_text() or "" for page in document.pages)


def read_pymupdf(pdf: Path) -> str:
    with pymupdf.open(pdf) as document:
        return "\n".join(page.get_text() for page in document)


def read_pdfium(pdf: Path) -> str:
    document = pypdfium2.PdfDocument(pdf)
    return "\n".join(page.get_textpage().get_text_range() for page in document)


def poppler_version() -> str:
    done = subprocess.run(
        ["pdftotext", "-v"], capture_output=True, text=True, check=False
    )
    found = re.search(r"version (\S+)", done.stderr + done.stdout)
    return found.group(1) if found else "?"


# name, Python package (None: a command-line tool), function
EXTRACTORS: list[tuple[str, str | None, Callable[[Path], str]]] = [
    ("Poppler", None, read_poppler),
    ("pypdf", "pypdf", read_pypdf),
    ("pdfminer.six", "pdfminer.six", read_pdfminer),
    ("pdfplumber", "pdfplumber", read_pdfplumber),
    ("PyMuPDF", "pymupdf", read_pymupdf),
    ("PDFium", "pypdfium2", read_pdfium),
]


# ---------- Text helpers ----------


def unreadable(text: str) -> list[str]:
    """Characters an ATS cannot use: replacement, private-use, unassigned or control characters."""
    bad = set()
    for char in set(text) - set("\n\r\t\f"):
        if char == "\ufffd" or unicodedata.category(char) in {"Cc", "Co", "Cn", "Cs"}:
            bad.add(char)
    found = [f"U+{ord(char):04X}" for char in sorted(bad)]
    if "(cid:" in text:
        found.append("(cid:...)")
    return found


def headings_of(tex: Path) -> list[str]:
    """Section headings of the .tex source, as they read on the page."""
    found = HEADING.findall(tex.read_text(encoding="utf-8"))
    return [squeeze(detex(raw)) for raw in found]


def vocabulary_of(tex: Path) -> set[str]:
    """Every word of the lines of the .tex source that are not commented out."""
    vocabulary: set[str] = set()
    for line in source_lines(tex):
        if not line.comment:
            vocabulary.update(words_of(line.text))
    return vocabulary


def headings_in_order(text: str, headings: list[str]) -> tuple[int, str]:
    """Number of headings found one after the other, and the first one that is not."""
    position = 0
    for count, heading in enumerate(headings):
        found = text.find(heading, position)
        if found < 0:
            return count, heading
        position = found + len(heading)
    return len(headings), ""


def difference(words: Counter[str], reference: Counter[str]) -> str:
    """What an extractor reads differently from the others, in a few words."""
    parts = []
    for label, counter in (
        ("only here", words - reference),
        ("missing", reference - words),
    ):
        if counter:
            sample = ", ".join(sorted(counter)[:SAMPLE])
            extra = len(counter) - SAMPLE
            more = f" and {extra} more" if extra > 0 else ""
            parts.append(f"{label}: {sample}{more}")
    return "; ".join(parts)


# ---------- The document ----------


@dataclass
class Document:
    pages: int
    title: str
    author: str
    subject: str
    keywords: list[str]
    language: str
    fonts: dict[str, tuple[bool, bool]]  # name -> (embedded, has a Unicode map)
    emails: list[str]


def font_facts(font) -> tuple[bool, bool]:
    descriptor = font.get("/FontDescriptor")
    if descriptor is None and "/DescendantFonts" in font:
        descriptor = font["/DescendantFonts"][0].get_object().get("/FontDescriptor")
    files = ("/FontFile", "/FontFile2", "/FontFile3")
    embedded = descriptor is not None and any(
        key in descriptor.get_object() for key in files
    )
    return embedded, "/ToUnicode" in font


def read_document(pdf: Path) -> Document:
    reader = pypdf.PdfReader(pdf)
    info = reader.metadata or {}
    fonts: dict[str, tuple[bool, bool]] = {}
    emails: list[str] = []
    for page in reader.pages:
        resources = page.get("/Resources") or {}
        for reference in (resources.get("/Font") or {}).values():
            font = reference.get_object()
            name = str(font.get("/BaseFont", "/unnamed")).lstrip("/").split("+")[-1]
            fonts[name] = font_facts(font)
        for annotation in page.get("/Annots") or []:
            action = annotation.get_object().get("/A") or {}
            uri = str(action.get("/URI", ""))
            if uri.startswith("mailto:"):
                address = uri.removeprefix("mailto:").split("?")[0]
                if address not in emails:
                    emails.append(address)
    keywords = [
        squeeze(normalise(word)) for word in str(info.get("/Keywords", "")).split(",")
    ]
    return Document(
        pages=len(reader.pages),
        title=str(info.get("/Title", "")),
        author=str(info.get("/Author", "")),
        subject=str(info.get("/Subject", "")),
        keywords=[word for word in keywords if word],
        language=str(reader.root_object.get("/Lang", "")),
        fonts=fonts,
        emails=emails,
    )


# ---------- The checks ----------


@dataclass
class Reading:
    """What one extractor returns for one PDF."""

    name: str
    version: str
    text: str = ""
    error: str = ""
    words: Counter[str] = field(default_factory=Counter)


@dataclass
class Report:
    pdf: Path
    lines: list[tuple[str, str]] = field(
        default_factory=list
    )  # ("ok" | "warning" | "FAIL", text)
    table: list[list[str]] = field(default_factory=list)

    def add(self, level: str, text: str) -> None:
        self.lines.append((level, text))

    @property
    def failed(self) -> bool:
        return any(level == "FAIL" for level, _ in self.lines)


def read_with_all(pdf: Path) -> list[Reading]:
    readings: list[Reading] = []
    for name, package, function in EXTRACTORS:
        if package is None and shutil.which(cmd="pdftotext") is None:
            continue  # Poppler is not installed: the five Python extractors still run
        version = importlib.metadata.version(package) if package else poppler_version()
        reading = Reading(name, version)
        try:
            reading.text = squeeze(normalise(function(pdf)))
            reading.words = words_of(reading.text)
        except (
            Exception
        ) as error:  # an extractor that crashes is a failed check, not a crash
            reading.error = f"{type(error).__name__}: {error}"
        readings.append(reading)
    return readings


def check_document(report: Report, document: Document, pages: int) -> None:
    level = "ok" if document.pages == pages else "FAIL"
    report.add(level, f"{document.pages} page(s), expected {pages}")

    bad = [
        name for name, (embedded, unicode_map) in document.fonts.items() if not embedded
    ]
    bad += [
        name
        for name, (embedded, unicode_map) in document.fonts.items()
        if not unicode_map
    ]
    if not document.fonts:
        report.add(level="FAIL", text="no font found: the page has no text")
    elif bad:
        names: str = ", ".join(sorted(set(bad)))
        report.add(
            level="FAIL", text=f"fonts not embedded or without a Unicode map: {names}"
        )
    else:
        report.add(
            level="ok",
            text=f"{len(document.fonts)} fonts, all embedded, each with a Unicode map",
        )

    fields: dict[str, str] = {
        "title": document.title,
        "author": document.author,
        "subject": document.subject,
        "keywords": ", ".join(document.keywords),
        "language": document.language,
    }
    empty: list[str] = [name for name, value in fields.items() if not value]
    if empty:
        report.add(level="FAIL", text=f"metadata not set: {', '.join(empty)}")
    else:
        count: int = len(document.keywords)
        report.add(
            level="ok",
            text=f"metadata: title, author, subject, {count} keywords, {document.language}",
        )


def check_pdf(pdf: Path, pages: int) -> Report:
    report = Report(pdf)
    document = read_document(pdf)
    check_document(report, document, pages)

    readings = read_with_all(pdf)
    working = [reading for reading in readings if not reading.error]

    # Keywords of the metadata that are on the page: found by at least one extractor.
    on_page = [
        word for word in document.keywords if any(word in r.text for r in working)
    ]
    absent = [word for word in document.keywords if word not in on_page]
    if absent:
        report.add(
            "warning", f"keywords of the metadata not in the text: {', '.join(absent)}"
        )

    tex = pdf.with_suffix(".tex")
    headings = headings_of(tex) if tex.is_file() else []
    vocabulary = vocabulary_of(tex) if tex.is_file() else set()
    if not tex.is_file():
        report.add(
            "warning", f"no {tex.name} next to the PDF: words and sections not compared"
        )

    # The words most extractors agree on.
    bags = Counter(frozenset(reading.words.items()) for reading in working)
    reference = Counter(dict(bags.most_common(1)[0][0])) if bags else Counter()

    for reading in readings:
        if reading.error:
            report.add("FAIL", f"{reading.name}: {reading.error}")
            report.table.append(
                [reading.name, reading.version, "error", "", "", "", "", ""]
            )
            continue
        problems = []
        name_first = not document.author or reading.text.startswith(document.author)
        if not name_first:
            problems.append(f"the text does not start with '{document.author}'")
        email = all(address in reading.text for address in document.emails)
        if not email:
            problems.append("the email address of the mailto link is not in the text")
        characters = unreadable(reading.text)
        if characters:
            problems.append(f"unreadable characters: {', '.join(characters)}")
        if len(reading.words) < MIN_WORDS:
            problems.append(f"only {sum(reading.words.values())} words extracted")
        found = [word for word in on_page if word in reading.text]
        if len(found) < len(on_page):
            lost = ", ".join(word for word in on_page if word not in found)
            problems.append(f"keywords not found: {lost}")
        in_order, first_missing = headings_in_order(reading.text, headings)
        if first_missing:
            problems.append(
                f"section '{first_missing}' not found in the expected order"
            )
        altered = sorted(
            word for word in reading.words if vocabulary and word not in vocabulary
        )
        if altered:
            extra = len(altered) - SAMPLE
            more = f" and {extra} more" if extra > 0 else ""
            sample = ", ".join(altered[:SAMPLE])
            problems.append(f"words that are not in {tex.name}: {sample}{more}")
        same = reading.words == reference
        if not same:
            problems.append(
                f"words differ from the other extractors ({difference(reading.words, reference)})"
            )

        total = sum(reading.words.values())
        summary = f"{total} words, {len(found)}/{len(on_page)} keywords"
        if headings:
            summary += f", {in_order}/{len(headings)} sections in order"
        report.add("ok" if not problems else "FAIL", f"{reading.name:<13}{summary}")
        for problem in problems:
            report.add("FAIL", f"{reading.name}: {problem}")
        mark = {True: "✅", False: "❌"}
        report.table.append(
            [
                reading.name,
                reading.version,
                str(total),
                mark[name_first and email and not characters],
                f"{len(found)}/{len(on_page)}",
                f"{in_order}/{len(headings)}" if headings else "n/a",
                mark[same],
                mark[not problems],
            ]
        )

    if working and all(reading.words == reference for reading in working):
        total = sum(reference.values())
        report.add("ok", f"the {len(working)} extractors read the same {total} words")
    return report


# ---------- Output ----------


def write_summary(reports: list[Report], path: Path) -> None:
    """Markdown tables for the job summary of GitHub Actions."""
    out: list[str] = []
    for report in reports:
        out.append(f"### {'❌' if report.failed else '✅'} ATS check: `{report.pdf}`\n")
        columns: list[str] = [
            "Extractor",
            "Version",
            "Words",
            "Name, email, characters",
        ]
        columns += ["Keywords", "Sections", "Same words", "Result"]
        out.append("| " + " | ".join(columns) + " |")
        out.append("| --- | --- | ---: | :---: | :---: | :---: | :---: | :---: |")
        out.extend("| " + " | ".join(row) + " |" for row in report.table)
        out.append("")
        out.extend(
            f"- **{level}**: {text}" for level, text in report.lines if level != "ok"
        )
        out.append("")
    with path.open("a", encoding="utf-8") as file:
        file.write("\n".join(out) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check how PDF text extractors read the CVs."
    )
    parser.add_argument("pdfs", nargs="+", type=Path, metavar="PDF")
    parser.add_argument(
        "--pages", type=int, default=1, help="expected number of pages (default 1)"
    )
    args = parser.parse_args()

    annotate = os.environ.get("GITHUB_ACTIONS") == "true"
    reports = []
    for pdf in args.pdfs:
        if not pdf.is_file():
            print(f"error: {pdf} not found", file=sys.stderr)
            return 2
        report = check_pdf(pdf, args.pages)
        reports.append(report)
        print(f"==> {pdf}")
        for level, text in report.lines:
            print(f"    {level}: {text}")
            if annotate and level != "ok":
                command = "error" if level == "FAIL" else "warning"
                print(f"::{command} file={pdf},title=ATS check::{text}")

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        write_summary(reports, Path(summary))

    failed = [str(report.pdf) for report in reports if report.failed]
    if failed:
        print(f"ATS checks failed: {', '.join(failed)}")
        return 1
    print("All ATS checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

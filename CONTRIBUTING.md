# Contributing

This repository contains my personal CV: external contributions are not expected.

If you want to reuse the template for your own CV, feel free to **fork** the repository and adapt it under the [MIT License](LICENSE).

---

## 📐 Naming conventions

Published CVs are named `cv-dmytro-palahin-<lang>-d.tex` (and `.pdf`):

| Part | Meaning |
| :---: | --- |
| `<lang>` | `en` English · `fr` French |
| `-d` | Data Engineer / MLOps focus (base CV) |

Offer-specific CVs (`src/other/`), older versions (`src/old/`), other variants, the personal photo, private application texts and the previous LinkedIn banner (`linkedin-banner/old/`) stay local: they are listed in `.gitignore`.

---

## 🔧 Local development

### Prerequisites

- **pdfLaTeX** with `latexmk`: [TeX Live](https://www.tug.org/texlive/) / [MacTeX](https://www.tug.org/mactex/) 2021 or newer, or [MiKTeX](https://miktex.org/)
- Packages: `lmodern`, `microtype`, `enumitem`, `geometry`, `hyperref`, `bookmark`, `babel` (english, french); for the LinkedIn banner: `standalone`, `tikz`, `inter`, `etoolbox`
- Optional, for the `make` shortcuts: GNU Make (preinstalled on macOS) and [Poppler](https://poppler.freedesktop.org/) for `pdfinfo`, `pdftotext` and `pdftoppm` (`brew install poppler`)

### Build

```sh
make       # both CVs, next to their sources
make en    # one language (make fr)
```

The build stops with an error when a CV does not fit on one page. Without `make`:

```sh
cd src/en
latexmk -pdf -auxdir=/tmp/latex-build -outdir=. cv-dmytro-palahin-en-d.tex
```

PDF to send, with a recruiter-friendly file name:

```sh
latexmk -pdf -jobname=CV_Dmytro_Palahin_Data_Engineer -auxdir=/tmp/latex-build -outdir=. cv-dmytro-palahin-en-d.tex
```

### Try and check a change

```sh
make try      # test build in /tmp/latex-build/try: nothing in the repository changes
make check    # the CI checks: one page, extractable text, PDF up to date
```

- `make try` prints the page count and the lines of text that change compared with the current PDF, so a line that wraps or a section pushed to a second page shows at once
- `make check` is the gate before a commit: run `make` first, otherwise the PDF is reported as out of date
- `L=fr` limits a command to one language; `CVS=src/fr/other/<file>.tex` runs `build`, `try`, `check` or `watch` on another `.tex`
- `make watch` repeats the test build on every save; `make help` lists the other commands and options

### README previews

```sh
make preview    # both previews, from the PDFs next to the sources
```

Without `make`:

```sh
cd src/en
pdftoppm -png -r 600 -singlefile cv-dmytro-palahin-en-d.pdf ../../resources/img/cv-dmytro-palahin-en-d
```

- `-singlefile` writes `cv-dmytro-palahin-en-d.png`, without the `-1` page suffix
- the target folder must exist: `pdftoppm` does not create it
- `-r 600` is what `make preview` uses: sharp when zoomed, files of about 2 MB; `-r 200` gives files of about 1 MB (`make preview PREVIEW_DPI=200`)

For French, run the same `latexmk` and `pdftoppm` commands from `src/fr` with `fr-d` file names.

### LinkedIn banner

```sh
make banner                    # French and English, light and dark
make banner L=fr THEME=dark    # one variant
```

- One source, `linkedin-banner/linkedin-banner.tex` (pdfLaTeX + TikZ, Inter font): the texts and colours are at the top of the file, the skills at the end
- Output: `linkedin-banner/png/` (3168 × 792 px, twice the 1584 × 396 px LinkedIn expects, so that text stays sharp) and `linkedin-banner/pdf/` (vector)
- LinkedIn covers the bottom left corner with the profile photo: `GUIDES=1 sh linkedin-banner/build.sh fr light` draws that zone on a preview
- `STATUS=0 sh linkedin-banner/build.sh` builds the banner without the status label (`-plain` files)

---

## ✍️ Editing rules (ATS)

- Keep the CV on **one page**: check after every change with `make try` (or `pdfinfo <file>.pdf | grep Pages`)
- In running text, use `\B{...}` and `\I{...}` instead of `\textbf` / `\textit`: they insert real spaces, so PDF parsers do not glue words together
- Write `A{}WS`, `EL{}T`, `T{}raining`...: the empty group breaks kerning, otherwise some extractors read "A WS"
- Use `\nbrealspace` for a space that must not break (`A{}WS\nbrealspace S3`)
- Keep `pdftitle` / `pdfsubject` in line with `\cvtitle`; `pdfkeywords`: 10 to 15 real keywords already present in the text
- Never hide text on the page (white, tiny, off-page): ATS detect it and reject the CV
- ⚠️ Comments (`%`) do not appear in the PDF but **are readable on GitHub**: keep private notes out of the published `.tex`

---

## 🚀 Release workflow

```sh
# 1. Edit the .tex, rebuild the PDF, regenerate the preview, run the checks
make && make preview && make check
# 2. Add a "## [v2.0.1] - YYYY-MM-DD" section to CHANGELOG.md
# 3. Commit and push
git add .
git commit -m "feat: <description>"
git push

# 4. Publish a release
git tag v2.0.1
git push origin v2.0.1
# -> GitHub Actions builds the PDFs and creates the release
```

- On every push or pull request that touches `src/en`, `src/fr` or the workflow, CI checks that each CV fits on **one page**, that its **text is extractable** (name, title, Python, SQL, GitHub link) and warns if the **committed PDF is older** than its `.tex` source
- The release notes are the `CHANGELOG.md` section whose version matches the tag exactly (`## [v2.0.1] - ...`): add it before tagging
- The README download buttons serve the PDFs from `main`, so they are up to date as soon as the new PDF is pushed
- The release keeps the file names `cv-dmytro-palahin-en-d.pdf` / `cv-dmytro-palahin-fr-d.pdf`, so the "Latest release" links in the README always point to the newest release

Versioning: `MAJOR` for a new template or repository structure, `MINOR` for new content or sections, `PATCH` for wording and small fixes.

# Contributing

This repository contains my personal CV: external contributions are not expected.

If you want to reuse the template for your own CV, feel free to **fork** the repository and adapt it under the [MIT License](LICENSE).

---

## 📐 Naming conventions

Files are named `cv-dmytro-palahin-<lang>-<variant>.tex`, where `<lang>` is `en` or `fr`.

| Suffix | Meaning | In this repository |
| :---: | --- | :---: |
| `-d` | Data Engineer / MLOps (base CV) | ✅ |
| `-q` | Quantitative Researcher / Developer | ❌ local only |
| `-tr` | Trading | ❌ local only |
| `-c` | Previous version of `-d`, with icons and photo | ❌ local only |

Offer-specific CVs (`src/other/`), older versions (`src/old/`), the personal photo and private application texts stay local: they are listed in `.gitignore`.

---

## 🔧 Local development

### Prerequisites

- **pdfLaTeX** with `latexmk`: [TeX Live](https://www.tug.org/texlive/) / [MacTeX](https://www.tug.org/mactex/) 2021 or newer, or [MiKTeX](https://miktex.org/)
- Packages: `lmodern`, `microtype`, `enumitem`, `geometry`, `hyperref`, `bookmark`, `babel` (english, french)
- Optional, for previews: `pdftoppm` from [Poppler](https://poppler.freedesktop.org/) (`brew install poppler`)

### Build

```sh
cd src/en
latexmk -pdf -auxdir=/tmp/latex-build -outdir=. cv-dmytro-palahin-en-d.tex
```

PDF to send, with a recruiter-friendly file name:

```sh
latexmk -pdf -jobname=CV_Dmytro_Palahin_Data_Engineer -auxdir=/tmp/latex-build -outdir=. cv-dmytro-palahin-en-d.tex
```

### README previews

```sh
cd src/en
pdftoppm -png -r 200 -singlefile cv-dmytro-palahin-en-d.pdf ../../resources/img/cv-dmytro-palahin-en-d
```

- `-singlefile` writes `cv-dmytro-palahin-en-d.png`, without the `-1` page suffix
- the target folder must exist: `pdftoppm` does not create it
- `-r 200` is enough for the README; `-r 600` gives files of about 2 MB

For French, run the same commands from `src/fr` with `fr-d` file names.

---

## ✍️ Editing rules (ATS)

- Keep the CV on **one page**: check after every change with `pdfinfo <file>.pdf | grep Pages`
- In running text, use `\B{...}` and `\I{...}` instead of `\textbf` / `\textit`: they insert real spaces, so PDF parsers do not glue words together
- Write `A{}WS`, `EL{}T`, `T{}raining`...: the empty group breaks kerning, otherwise some extractors read "A WS"
- Use `\nbrealspace` for a space that must not break (`A{}WS\nbrealspace S3`)
- Keep `pdftitle` / `pdfsubject` in line with `\cvtitle`; `pdfkeywords`: 10 to 15 real keywords already present in the text
- Never hide text on the page (white, tiny, off-page): ATS detect it and reject the CV
- ⚠️ Comments (`%`) do not appear in the PDF but **are readable on GitHub**: keep private notes out of the published `.tex`

---

## 🚀 Release workflow

```sh
# 1. Edit the .tex, rebuild the PDF, regenerate the preview
# 2. Add an entry to CHANGELOG.md
# 3. Commit and push
git add .
git commit -m "feat: <description>"
git push

# 4. Publish a release
git tag v2.0.1
git push origin v2.0.1
# -> GitHub Actions builds the PDFs and creates the release
```

Versioning: `MAJOR` for a new template or repository structure, `MINOR` for new content or sections, `PATCH` for wording and small fixes.

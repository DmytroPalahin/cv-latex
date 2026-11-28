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
- Optional, for the Python scripts (`make ats`, `links`, `match`, `test`): [uv](https://docs.astral.sh/uv/) (`brew install uv`). The first `uv run` creates the environment in `.venv`, with the Python version of `.python-version` (uv downloads it if it is missing) and the package versions of `uv.lock`: there is nothing to install by hand. The commands are listed under [Python scripts and uv](#python-scripts-and-uv)

### Build

```sh
make       # both CVs, next to their sources
make en    # one language (make fr)
```

The build stops with an error when a CV does not fit on one page. Without `make`, from the repository root:

```sh
latexmk -pdf -cd -auxdir=/tmp/latex-build -outdir=. src/en/cv-dmytro-palahin-en-d.tex
```

`-cd` makes `latexmk` change to the folder of the source first: `-outdir=.` then means that folder, and the PDF lands next to the `.tex`.

PDF to send, with a recruiter-friendly file name:

```sh
latexmk -pdf -cd -jobname=CV_Dmytro_Palahin_Data_Engineer -auxdir=/tmp/latex-build -outdir=. src/en/cv-dmytro-palahin-en-d.tex
```

### Try and check a change

```sh
make try      # test build in /tmp/latex-build/try: nothing in the repository changes
make check    # the CI checks: one page, extractable text, PDF up to date
make ats      # six text extractors read the PDFs next to the sources
make links    # every web link of the PDFs still opens (needs the network)
```

- `make try` prints the page count and the lines of text that change compared with the current PDF, so a line that wraps or a section pushed to a second page shows at once
- `make check` is the gate before a commit: run `make` first, otherwise the PDF is reported as out of date
- `make ats` reads each PDF with Poppler, pypdf, pdfminer.six, pdfplumber, PyMuPDF and PDFium. It fails when an extractor reads other words than the rest, when a word read from the PDF is not a word of the `.tex` source (glued, cut in two or hyphenated), when the sections are not in the order of the source, or when a font has no Unicode map. A keyword of `pdfkeywords` that is not in the text of the page gives a warning
- `make links` fails on a page that does not exist (HTTP 404 or 410, unknown host). A site that refuses automated requests (LinkedIn, Udemy) gives a warning, not a failure: open that link by hand from time to time
- `L=fr` limits a command to one language; `CVS=src/fr/other/<file>.tex` runs `build`, `try`, `check`, `ats`, `links`, `match` or `watch` on another `.tex`
- `make watch` repeats the test build on every save (stop it with Ctrl-C)
- `make clean` deletes `/tmp/latex-build`: the auxiliary files of `latexmk` and the test builds. Nothing in the repository is removed
- Three more options work with these commands: `PAGES=2` for a CV of two pages (`make`, `try`, `check` and `ats` then expect two), `BUILD_DIR=/path` to keep the auxiliary files and the test builds somewhere else than `/tmp/latex-build` (an absolute path without spaces), `V=1` to show the output of `latexmk`
- `make help` lists every command and option

### Match a job offer

```sh
make match OFFER=path/to/offer.txt      # text or PDF file
pbpaste | make match OFFER=-            # the offer copied from the browser (macOS)
make match OFFER=scripts/example-offer.txt
```

The report sorts the skills of the offer in three groups: already on the page of the CV, waiting in the Reserve (commented lines of the `.tex`, with their line numbers: remove the `%` if the skill fits the offer and the CV stays on one page), and not in the CV at all.

- Nothing leaves the machine: the script only reads the offer, the `.tex` source and `scripts/skills.txt`
- Only the skills listed in `scripts/skills.txt` are recognised (one per line: `Name | other spelling | French wording`): add a line for a term the report misses
- With both CVs (the default), the one written in the language of the offer is used; `L=en` or `L=fr` forces one
- Keep private offers out of the repository folders that are published (`application/` is in `.gitignore`)

### README previews

```sh
make preview    # both previews, from the PDFs next to the sources
```

Without `make`:

```sh
pdftoppm -png -r 600 -singlefile src/en/cv-dmytro-palahin-en-d.pdf resources/img/cv-dmytro-palahin-en-d
```

- `-singlefile` writes `cv-dmytro-palahin-en-d.png`, without the `-1` page suffix
- the target folder must exist: `pdftoppm` does not create it
- `-r 600` is what `make preview` uses: sharp when zoomed, files of about 2 MB; `-r 200` gives files of about 1 MB (`make preview PREVIEW_DPI=200`)

For French, run the same `latexmk` and `pdftoppm` commands with `src/fr` and the `fr-d` file names.

### LinkedIn banner

```sh
make banner                    # French and English, light and dark
make banner L=fr THEME=dark    # one variant
```

- One source, `linkedin-banner/linkedin-banner.tex` (pdfLaTeX + TikZ, Inter font): the texts and colours are at the top of the file, the skills in the two `\matrix` blocks, the build commands at the end
- Built on its own (from an editor, for example), the source gives the default variant: English, dark theme
- Output: `linkedin-banner/png/` (3168 × 792 px, twice the 1584 × 396 px LinkedIn expects, so that text stays sharp) and `linkedin-banner/pdf/` (vector)
- LinkedIn covers the bottom left corner with the profile photo: `GUIDES=1 sh linkedin-banner/build.sh fr light` draws that zone on a preview
- `STATUS=0 sh linkedin-banner/build.sh` builds the banner without the status label (`-plain` files), `EMAIL=0` without the email address (`-noemail` files)

### Social preview

```sh
make social                # dark and light
make social THEME=dark     # one theme
```

- One source, `social-preview/social-preview.tex`, in the style of the banner: the texts are at the top of the file, the skills in the two `\matrix` blocks, the build commands at the end
- Output: `social-preview/social-preview-dark.png` and `social-preview-light.png`, 2560 × 1280 px (twice the 1280 × 640 px GitHub recommends), under the 1 MB GitHub accepts
- The image is uploaded by hand: on GitHub, **Settings > General > Social preview > Edit > Upload an image**

### Python scripts and uv

The scripts of `scripts/` form a [uv](https://docs.astral.sh/uv/) project. Four things describe it:

| File | Role | In git |
| --- | --- | :---: |
| `pyproject.toml` | the packages the scripts need, the `dev` tools (Ruff, pytest), the Ruff and pytest settings, and where the type checker of the editor (ty) finds the scripts | yes |
| `uv.lock` | the exact version of every package, written by uv: never edited by hand | yes |
| `.python-version` | the Python version of the environment (3.12) | yes |
| `.venv/` | the environment itself: Python and the installed packages | no |

Every command runs from the repository root. `uv run` first brings `.venv` in line with `uv.lock` (it creates it the first time), then runs the command in it: there is no environment to activate.

#### `make` commands that run uv

Four commands of `make` are shortcuts for a uv command: day to day, `make` is enough. None of them modifies a file.

| `make` command | What it runs |
| --- | --- |
| `make ats` | `uv run scripts/check_ats.py --pages 1 <the two PDFs>` |
| `make links` | `uv run scripts/check_links.py <the two PDFs>` |
| `make match OFFER=offer.txt` | `uv run scripts/match_offer.py offer.txt --cv <the en .tex> --cv <the fr .tex>` |
| `make test` | `uv run ruff check --no-fix scripts tests`, then `uv run ruff format --check scripts tests`, then `uv run pytest -q` |

The other commands of `make` (`make`, `try`, `check`, `preview`, `banner`, `social`, `watch`, `clean`) do not use uv: they call `latexmk` and Poppler.

#### uv commands without a `make` shortcut

These are run directly, when the case in the second column comes up. Those marked **writes** modify files of the repository.

| Command | When | What to expect |
| --- | --- | --- |
| `uv sync` | first use, or after a pull that changed `uv.lock`. Optional: `uv run` does the same | `Resolved … packages`, then the packages installed, or `Checked … packages` when nothing was missing |
| `uv run ruff check scripts tests` | `make test` reports a lint problem | **writes**: `Fixed 1 error`, or `All checks passed!` |
| `uv run ruff format scripts tests` | `make test` reports a file to reformat | **writes**: `1 file reformatted, 6 files left unchanged` |
| `uv run pytest` | the unit tests alone, with one line per test file | `18 passed` |
| `uv run pytest -k offer` | only the tests whose name contains `offer`, while working on one script | `8 passed, 10 deselected` |
| `uv run scripts/check_ats.py path/to/cv.pdf` | one script on one file | the report of that file |
| `uv run python --version` | which Python the environment uses | `Python 3.12.x` |
| `uv tree --depth 1` | the packages of the project and their versions | a tree: `pypdf v7.2.0`, `ruff v0.17.6 (group: dev)`... |
| `uv lock --check` | does `uv.lock` still match `pyproject.toml`? | `Resolved … packages` and no error |
| `uv lock --upgrade` | newer versions of every package (`uv lock --upgrade-package pypdf`: of one) | **writes** `uv.lock`: one `Updated <package> v… -> v…` line per package |
| `uv add <package>` | a script needs a new package (`uv add --dev <package>`: a development tool; `uv remove <package>`: the opposite) | **writes** `pyproject.toml` and `uv.lock` |
| `uv python pin 3.13` | another Python version | **writes** `.python-version` |
| `rm -rf .venv && uv sync` | the environment is broken (import errors that make no sense) | `.venv` is created again from `uv.lock` |

#### Options of the scripts

`make ats`, `make links` and `make match` call the scripts with their usual arguments. Called directly, each script takes a few options of its own (`--help` lists them):

```sh
uv run scripts/check_ats.py --pages 2 path/to/cv.pdf                    # a CV of two pages (same as: make ats PAGES=2)
uv run scripts/check_links.py --timeout 40 --retries 5 path/to/cv.pdf   # a slow network (default: 20 s, 3 extra tries)
uv run scripts/match_offer.py offer.txt --cv path/to/cv.tex --skills path/to/skills.txt   # another list of skills
uv run scripts/match_offer.py --help                                    # the options of one script
```

- `pyproject.toml`, `uv.lock` and `.python-version` are committed together: a change of one without the others gives a different environment on another machine
- CI sets `UV_LOCKED=1`: uv then uses exactly the versions of `uv.lock`, and fails if the file no longer matches `pyproject.toml` (what `uv lock --check` tells locally)
- After `uv lock --upgrade`, run `make test && make ats` before committing the new `uv.lock`: a new version of an extractor may read the PDFs differently. Dependabot proposes the same upgrade twice a month (on the 1st and the 15th), as a pull request that CI checks
- With `fix = true` in the Ruff settings, `ruff check` repairs a file and exits 0: `make test` and CI run it with `--no-fix`, so that a problem fails the check instead of being hidden
- `scripts/cvtext.py` holds what the scripts share: how a text is cut into words, and how a line of the `.tex` source reads on the page (`A{}WS` is AWS, `\B{text}` is text). A new LaTeX command that prints a character belongs in its `SYMBOLS` table
- A new script goes in `scripts/`, its tests in `tests/test_<name>.py`; `print` and calls to Poppler are allowed in `scripts/` by the per-file rules of `pyproject.toml`

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
make && make preview && make check && make ats && make links
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

- On every push or pull request that touches `src/en`, `src/fr`, the scripts or the workflow, CI checks that each CV fits on **one page**, that its **text is extractable** (name, title, Python, SQL, GitHub link), that **six text extractors read the same words** (`check_ats.py`), and warns if the **committed PDF is older** than its `.tex` source; a second job lints and tests the scripts
- A separate workflow, `links.yml`, checks the **links of the CVs** every Monday and whenever a PDF changes; Dependabot proposes the updates of the GitHub Actions and of the Python packages twice a month (on the 1st and the 15th)
- The release notes are the `CHANGELOG.md` section whose version matches the tag exactly (`## [v2.0.1] - ...`): add it before tagging
- The README download buttons serve the PDFs from `main`, so they are up to date as soon as the new PDF is pushed
- The release keeps the file names `cv-dmytro-palahin-en-d.pdf` / `cv-dmytro-palahin-fr-d.pdf`, so the "Latest release" links in the README always point to the newest release

Versioning: `MAJOR` for a new template or repository structure, `MINOR` for new content or sections, `PATCH` for wording and small fixes.

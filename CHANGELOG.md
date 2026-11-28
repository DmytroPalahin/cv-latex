# Changelog

All notable changes to this project are documented in this file.  
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/): `[vMAJOR.MINOR.PATCH] - YYYY-MM-DD`

---

## [Unreleased]

### Added

- `scripts/check_ats.py` and `make ats`: each PDF is read with six text extractors (Poppler, pypdf, pdfminer.six, pdfplumber, PyMuPDF, PDFium); their words are compared with each other and with the `.tex` source, and the page count, the fonts, the metadata and the order of the sections are checked
- `scripts/check_links.py` and `make links`: every web link of the PDFs is requested; a page that no longer exists fails the check
- `scripts/match_offer.py` and `make match OFFER=offer.txt`: skills of a job offer that are on the page of the CV, in its Reserve or missing, from the list in `scripts/skills.txt`
- `social-preview/` and `make social`: social preview of the repository (2560 × 1280 px, dark and light), in the style of the LinkedIn banner
- `pyproject.toml`, `uv.lock`, `.python-version`, `tests/` and `make test`: the scripts are a uv project with pinned package and Python versions; lint and formatting (Ruff) and unit tests (pytest)
- `links.yml`: the links of the CVs are checked every Monday and whenever a PDF changes
- `.github/dependabot.yml`: updates of the GitHub Actions and of the Python packages, twice a month (on the 1st and the 15th)
- **Certifications**: SAS training (SAS macro language) at Société Générale Insurance, with a link to its certificate of attendance, `resources/docs/sas_macro_language_training.pdf` (SAS Institute, 2023), also listed in `README.md`

### Changed

- Layout: smaller gaps in the header (2 pt instead of 4 pt under the title, 1 pt instead of 3 pt above the languages), to keep the CV on one page with the new line
- `latex.yml`: the build also runs `check_ats.py` on each compiled PDF; a new job lints and tests the scripts; the workflow also starts when the scripts, their tests, `pyproject.toml`, `uv.lock` or the `Makefile` change
- `README.md`: section on the Python checks and tools, social preview, build commands, CI table, project structure
- `CONTRIBUTING.md`: how to run the checks, match a job offer, build the social preview and test the scripts; the uv commands of the project; `make clean`, the options `PAGES`, `BUILD_DIR` and `V`, and the options of the scripts; a first run step by step, with what each command prints; which `make` commands run uv, and which uv commands are run directly
- `.gitignore`: the social preview built from the editor stays local; `.python-version` is tracked

### Fixed

- **Certifications**: the two links to the Huawei certificates pointed to the former name and folder of the repository and returned a 404; they now open the PDFs in `resources/docs/`

---

## [v2.3.1] - 2026-11-25

### Changed

- LinkedIn banner: English with the dark theme is the default variant
- LinkedIn banner: the roles read `Data Engineer · AI Engineer · Analytics`; the skills are Python, SQL, AWS S3, Azure, Airflow, dbt, Git, Docker, Kubernetes, MLOps, LLMs, RAG and AI Agents
- LinkedIn banner: the email address is shown under the skills (`EMAIL=0` builds the banner without it); the line about the school and the apprenticeship is left out
- Build commands in the comments of the `.tex` sources, in `README.md` and in `CONTRIBUTING.md` run from the repository root (`latexmk -cd`); the banner source lists its commands at the end
- `README.md`: dark banner preview first
- `.gitignore`: the banner built from the editor and the banner previews with guides stay local

---

## [v2.3.0] - 2026-11-25

### Added

- `linkedin-banner/`: LinkedIn profile banner built with pdfLaTeX + TikZ from one source, in French and English, with a light and a dark theme, as PNG (3168 × 792 px) and vector PDF
- `Makefile`: `make banner` builds the banner (`L=fr`, `THEME=dark` for one variant)

### Changed

- `README.md`: banner section, `make banner` in the build section, project structure
- `CONTRIBUTING.md`: how to build and edit the banner
- `.gitignore`: the previous banner stays local

---

## [v2.2.0] - 2026-11-25

### Added

- **Projects**: **FX Rates ELT Pipeline (ECB, NBU)**, first in the list: an Apache Airflow 3 pipeline with an S3 raw layer, a Postgres warehouse, idempotent backfills, data-aware scheduling and data quality checks ([fx-rates-airflow](https://github.com/DmytroPalahin/fx-rates-airflow))
- **Reserve** blocks in the `.tex` sources: description variants, checked figures and interview notes for the FX pipeline and for PhishGuard
- **Reserve** blocks in the `.tex` sources: Skills lines for LLM / GenAI, analytics and test automation roles, with OpenAI API, LLM-as-a-Judge, prompt injection, jailbreaks, Claude Code, Cursor, A/B testing and Selenium

### Changed

- **Projects**: the phishing project becomes **PhishGuard: Explainable Phishing Email Detection**, in line with its rewrite: TF-IDF + LightGBM ensemble on 75.8k deduplicated emails, served with FastAPI, Docker and Kubernetes; new repository link
- **Projects**: Anomaly Detection moves to the Reserve to keep the CV on one page
- Layout: bottom margin reduced from 0.5 cm to 0.25 cm
- `README.md`: tech stack extended with the skills of the new Reserve block
- `resources/img/`: previews regenerated from the current PDFs

---

## [v2.1.0] - 2026-11-16

### Added

- `Makefile`: local shortcuts around `latexmk`. `make` builds both CVs, `make try` runs a test build outside the repository (page count and changed lines), `make check` repeats the CI checks (one page, extractable text, PDF up to date), plus `make preview`, `make watch` and `make clean`
- **Reserve** blocks in the `.tex` sources: Cellula (Java cellular automaton engine) and Battleship (C11, GTK 3) projects, Agile (Scrum), IoT coursework, title and description variants for the ACO-TSP project
- `academic-profil/`: NoSQL databases (Cassandra, MongoDB, Redis, Elasticsearch, CouchDB) and Internet of Things (IoT)
- `.gitattributes`: LF line endings, LaTeX-aware diff, PDF and PNG files marked as binary

### Changed

- **Projects**: the Traveling Salesman project becomes **Ant Colony Optimization for the Traveling Salesman Problem** (C11 library checked against exact Held-Karp, 117 tests, fuzzing, CI), links to the rewritten [aco-tsp](https://github.com/DmytroPalahin/aco-tsp) repository and moves up to second place
- **Coursework**: NoSQL databases named (MongoDB, Cassandra, Redis, Elasticsearch), shorter wording to stay on one page
- **Skills**: Azure and Azure OpenAI added to Cloud & Data; `Git/GitLab` becomes `Git (GitHub)`
- Phishing project: `76,677 emails` written as `76.7k emails`
- `README.md`: `make` commands in the build section, tech stack in line with the CV
- `CONTRIBUTING.md`: `make` commands for building, trying and checking a change, previews at 600 dpi
- `resources/img/`: previews regenerated from the current PDFs
- `latex.yml`: neutral heading in the release notes

---

## [v2.0.0] - 2026-11-12

### Added

- New **ATS-friendly template** for `en-d` and `fr-d`: single column, Latin Modern, no icons or tables, ToUnicode map, no ligatures or hyphenation, real space glyphs around bold / italic text (`\B`, `\I`)
- PDF metadata in the `.tex` sources: `pdftitle`, `pdfsubject`, `pdfkeywords`, `pdflang`
- Commented **Reserve** blocks in the `.tex` sources: missions, skills, courses and projects to re-enable depending on the job offer
- `README.md`: centered header, badges, download buttons, side-by-side EN / FR previews, highlights, tech stack, ATS notes, certificates
- `README.md`: download buttons serve the latest PDFs from `main`

### Changed

- The repository now publishes **only the base Data Engineer CV** (`en-d`, `fr-d`); the other variants are kept locally through `.gitignore`
- `academic/` renamed to `academic-profil/`
- `resources/img/`: previews regenerated for `en-d` and `fr-d`
- `CONTRIBUTING.md`: naming conventions, build and preview commands, editing rules for the new template
- `latex.yml`: builds only `en-d` and `fr-d`, and runs only when the CV sources or the workflow change (plus manual runs)
- `latex.yml`: checks that each CV fits on one page and that its text is extractable (ATS); warns when the committed PDF is out of date
- `latex.yml`: PNG previews in the artifacts and the release; release notes taken from `CHANGELOG.md`
- `latex.yml`: read-only permissions by default (`contents: write` only for the release job), job timeouts, no shell escape
- `latex.yml`: actions updated to their Node 24 majors: `checkout@v7`, `upload-artifact@v7`, `download-artifact@v8`, `latex-action@v4`, `action-gh-release@v3`

### Removed

- Other CV variants and their previews (kept locally)
- Personal photo `resources/img/photo.png` (no longer tracked)

---

## [v1.3.2] - 2026-08-27

### Added

- New CV variants (EN / FR)

---

## [v1.3.1] - 2026-08-24

### Fixed

- CI: set `working_directory` for `latex-action` to resolve relative image paths

---

## [v1.3.0] - 2026-08-24

### Added

- CI/CD: parallel matrix build for all 6 CV variants via GitHub Actions
- CI/CD: automatic GitHub Release creation on `git tag v*.*.*`
- CI/CD: `concurrency` group to cancel stale runs on new push
- `README.md`: download table, project structure, CI/CD usage docs, preview table for all variants

### Changed

- `latex.yml`: replaced single-file compile with `matrix` strategy (6 variants, `fail-fast: false`)
- `latex.yml`: artifacts now have 30-day retention
- `.gitignore`: removed `.github/` exclusion so workflows are tracked in git
- `.gitignore`: cleaned and scoped to LaTeX-relevant ignores only

---

## [v1.2.0] - 2026-03-11

### Added

- Initial CI/CD workflow (`latex.yml`) - basic compile + artifact upload
- Additional English CV variant

---

## [v1.0.0] - 2024-10-26

### Added

- Initial LaTeX CV - French and English versions
- `src/en/` and `src/fr/` directory structure
- `resources/img/` preview images
- MIT License

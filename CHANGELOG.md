# Changelog

All notable changes to this project are documented in this file.  
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/): `[vMAJOR.MINOR.PATCH] - YYYY-MM-DD`

---

## [v2.2.0] - 2026-11-24

### Added

- **Projects**: **FX Rates ELT Pipeline (ECB, NBU)**, first in the list: an Apache Airflow 3 pipeline with an S3 raw layer, a Postgres warehouse, idempotent backfills, data-aware scheduling and data quality checks ([fx-rates-airflow](https://github.com/DmytroPalahin/fx-rates-airflow))
- **Reserve** blocks in the `.tex` sources: description variants, checked figures and interview notes for the FX pipeline and for PhishGuard

### Changed

- **Projects**: the phishing project becomes **PhishGuard: Explainable Phishing Email Detection**, in line with its rewrite: TF-IDF + LightGBM ensemble on 75.8k deduplicated emails, served with FastAPI, Docker and Kubernetes; new repository link
- **Projects**: Anomaly Detection moves to the Reserve to keep the CV on one page
- Layout: bottom margin reduced from 0.5 cm to 0.25 cm
- `resources/img/`: previews regenerated from the current PDFs

---

## [v2.1.0] - 2026-11-16

### Added

- `Makefile`: local shortcuts around `latexmk`. `make` builds both CVs, `make try` runs a test build outside the repository (page count and changed lines), `make check` repeats the CI checks (one page, extractable text, PDF up to date), plus `make preview`, `make watch` and `make clean`
- **Reserve** blocks in the `.tex` sources: Cellula (Java cellular automaton engine) and Battleship (C11, GTK 3) projects, Agile (Scrum), IoT coursework, title and description variants for the ACO-TSP project
- `academic_profil/`: NoSQL databases (Cassandra, MongoDB, Redis, Elasticsearch, CouchDB) and Internet of Things (IoT)
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
- `academic/` renamed to `academic_profil/`
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

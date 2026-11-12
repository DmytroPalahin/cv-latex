# Changelog

All notable changes to this project are documented in this file.  
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/): `[vMAJOR.MINOR.PATCH] - YYYY-MM-DD`

---

## [v2.0.0] - 2026-11-12

### Added

- New **ATS-friendly template** for `en-d` and `fr-d`: single column, Latin Modern, no icons or tables, ToUnicode map, no ligatures or hyphenation, real space glyphs around bold / italic text (`\B`, `\I`)
- PDF metadata in the `.tex` sources: `pdftitle`, `pdfsubject`, `pdfkeywords`, `pdflang`
- Commented **Reserve** blocks in the `.tex` sources: missions, skills, courses and projects to re-enable depending on the job offer
- `README.md`: centered header, badges, download buttons, side-by-side EN / FR previews, ATS notes, certificates

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

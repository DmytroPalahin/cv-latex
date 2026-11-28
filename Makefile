# Local shortcuts for building and checking the CVs: run `make help`.
#
# make only wraps latexmk and the Python scripts of scripts/, and repeats the checks of
# .github/workflows/, so that a change is verified the same way locally and in CI.
#
#   make try L=fr                      one language instead of both
#   make try CVS=src/fr/other/x.tex    any other .tex of the repository

# Published CVs, by language. CVS is what build, try, check and watch work on.
L         ?= en fr
PUBLISHED  = $(foreach l,$(L),src/$(l)/cv-dmytro-palahin-$(l)-d.tex)
CVS       ?= $(PUBLISHED)
# The PDFs next to these sources: what links and ats work on.
PDFS       = $(CVS:.tex=.pdf)

# Auxiliary files and test builds are kept outside the repository.
BUILD_DIR ?= /tmp/latex-build
TRY_DIR    = $(BUILD_DIR)/try

# Expected number of pages, and text that an ATS must find in the PDF.
PAGES     ?= 1
KEYWORDS  ?= "Dmytro Palahin" "Data Engineer" "Python" "SQL" "github.com/DmytroPalahin"

LATEXMK       ?= latexmk
LATEXMK_FLAGS ?= -pdf -interaction=nonstopmode -halt-on-error -file-line-error
V             ?=
PREVIEW_DIR   ?= resources/img
PREVIEW_DPI   ?= 600

# LinkedIn banner (linkedin-banner/): themes to build, for the languages of L.
THEME         ?= dark light

# Python scripts (scripts/): uv runs them in the environment of pyproject.toml, with the
# versions of uv.lock (created in .venv on the first run). OFFER is the job offer of `make match`.
UV            ?= uv
OFFER         ?=

ifneq ($(filter /%,$(BUILD_DIR)),$(BUILD_DIR))
$(error BUILD_DIR must be one absolute path without spaces, got '$(BUILD_DIR)')
endif

.DEFAULT_GOAL := all
.PHONY: all build en fr try check ats links match preview banner test watch clean help

# Shell functions shared by the recipes. Every recipe below is one shell script
# that starts with $(SH); no comment may appear inside this block.
#   need TOOL HINT            stop with a clear message when TOOL is missing
#   compile TEX OUTDIR AUXDIR run latexmk from the directory of TEX; its output is
#                             kept in a file and shown only on error (V=1: always)
#   pages PDF                 number of pages
#   text PDF                  extracted text, whitespace squeezed (as in CI)
#   layout PDF                text as laid out on the page, one line per line
define SH
set -eu; \
need() { \
  command -v "$$1" >/dev/null 2>&1 || { echo "error: '$$1' not found: $$2" >&2; exit 1; }; \
}; \
compile() { \
  need "$(LATEXMK)" "install TeX Live or MacTeX"; \
  mkdir -p "$$3"; \
  log="$$3/$$(basename "$$1" .tex).log"; out="$$3/$$(basename "$$1" .tex).latexmk.txt"; \
  if [ -n "$(V)" ]; then out=/dev/stdout; fi; \
  if ! ( cd "$$(dirname "$$1")" && \
         $(LATEXMK) $(LATEXMK_FLAGS) -auxdir="$$3" -outdir="$$2" "$$(basename "$$1")" ) >"$$out" 2>&1; then \
    if [ -f "$$log" ] && grep -q -E '^[^ ]+\.tex:[0-9]+: |^! ' "$$log"; then \
      grep -E -A2 '^[^ ]+\.tex:[0-9]+: |^! ' "$$log" | head -n 20 >&2; \
    elif [ -f "$$out" ]; then \
      tail -n 15 "$$out" >&2; \
    fi; \
    echo "error: $$1 did not compile (full log: $$log)" >&2; \
    exit 1; \
  fi; \
}; \
pages() { pdfinfo "$$1" | awk '/^Pages:/ {print $$2}'; }; \
text() { pdftotext "$$1" - | tr -s '[:space:]' ' '; }; \
layout() { \
  pdftotext -layout "$$1" - | awk '{ if (gsub(/\f/, "")) print "-------- end of page --------"; print }'; \
}; \
poppler="install Poppler (brew install poppler)"; \
uv="install uv (brew install uv, or see https://docs.astral.sh/uv/)"
endef

all: build

# Build the PDFs next to their sources (the files that are committed).
build:
	@$(SH); need pdfinfo "$$poppler"; bad=0; \
	for tex in $(CVS); do \
	  pdf="$${tex%.tex}.pdf"; \
	  echo "==> $$tex"; \
	  compile "$$tex" . "$(BUILD_DIR)"; \
	  n=$$(pages "$$pdf"); \
	  if [ "$$n" = "$(PAGES)" ]; then \
	    echo "    ok: $$pdf, $$n page(s)"; \
	  else \
	    echo "    FAIL: $$pdf has $$n pages, expected $(PAGES)" >&2; bad=1; \
	  fi; \
	done; \
	exit $$bad

en fr:
	@$(MAKE) --no-print-directory build L=$@

# Test build: nothing in the repository is modified. Shows the page count and
# what changes in the text, line by line, compared with the PDF next to the source.
try:
	@$(SH); need pdfinfo "$$poppler"; need pdftotext "$$poppler"; bad=0; \
	for tex in $(CVS); do \
	  name=$$(basename "$$tex" .tex); old="$${tex%.tex}.pdf"; new="$(TRY_DIR)/$$name.pdf"; \
	  echo "==> $$tex"; \
	  compile "$$tex" "$(TRY_DIR)" "$(TRY_DIR)"; \
	  n=$$(pages "$$new"); \
	  if [ "$$n" = "$(PAGES)" ]; then \
	    echo "    ok: $$n page(s)"; \
	  else \
	    echo "    FAIL: $$n pages, expected $(PAGES)" >&2; bad=1; \
	  fi; \
	  if [ -f "$$old" ]; then \
	    layout "$$old" >"$(TRY_DIR)/$$name.before.txt"; \
	    layout "$$new" >"$(TRY_DIR)/$$name.after.txt"; \
	    if diff -u -L "$$old" -L "this build" \
	         "$(TRY_DIR)/$$name.before.txt" "$(TRY_DIR)/$$name.after.txt"; then \
	      echo "    text: same as $$old"; \
	    else \
	      echo "    text: differs from $$old (see above)"; \
	    fi; \
	  else \
	    echo "    text: no $$old to compare with"; \
	  fi; \
	  echo "    pdf:  $$new"; \
	done; \
	exit $$bad

# The checks of CI, on a fresh build: one page, extractable text, PDF up to date.
check:
	@$(SH); need pdfinfo "$$poppler"; need pdftotext "$$poppler"; bad=0; \
	for tex in $(CVS); do \
	  name=$$(basename "$$tex" .tex); old="$${tex%.tex}.pdf"; new="$(TRY_DIR)/$$name.pdf"; \
	  echo "==> $$tex"; \
	  compile "$$tex" "$(TRY_DIR)" "$(TRY_DIR)"; \
	  n=$$(pages "$$new"); \
	  if [ "$$n" = "$(PAGES)" ]; then \
	    echo "    ok: $$n page(s)"; \
	  else \
	    echo "    FAIL: $$n pages, expected $(PAGES)" >&2; bad=1; \
	  fi; \
	  pdftotext "$$new" "$(TRY_DIR)/$$name.txt"; \
	  for kw in $(KEYWORDS); do \
	    if grep -qF "$$kw" "$(TRY_DIR)/$$name.txt"; then \
	      echo "    ok: text contains '$$kw'"; \
	    else \
	      echo "    FAIL: '$$kw' not found in the text extracted from the PDF" >&2; bad=1; \
	    fi; \
	  done; \
	  if [ ! -f "$$old" ]; then \
	    echo "    FAIL: $$old is missing, run 'make'" >&2; bad=1; \
	  elif [ "$$(text "$$old")" = "$$(text "$$new")" ]; then \
	    echo "    ok: $$old matches its source"; \
	  else \
	    echo "    FAIL: $$old does not match its source, run 'make'" >&2; bad=1; \
	  fi; \
	done; \
	if [ "$$bad" = 0 ]; then echo "All checks passed"; fi; \
	exit $$bad

# What an ATS does first: read the text of the PDF. Six extractors read the PDFs next to
# the sources; their words are compared with each other and with the .tex source.
ats:
	@$(SH); need pdftotext "$$poppler"; need "$(UV)" "$$uv"; \
	$(UV) run --quiet scripts/check_ats.py --pages $(PAGES) $(PDFS)

# Every web link of the PDFs next to the sources still opens (needs the network).
links:
	@$(SH); need pdfinfo "$$poppler"; need "$(UV)" "$$uv"; \
	$(UV) run --quiet scripts/check_links.py $(PDFS)

# Skills of a job offer: on the page of the CV, in its Reserve (commented lines), or missing.
match:
	@$(SH); need "$(UV)" "$$uv"; \
	if [ -z "$(OFFER)" ]; then \
	  echo "usage: make match OFFER=path/to/offer.txt   (try: OFFER=scripts/example-offer.txt)" >&2; \
	  exit 1; \
	fi; \
	$(UV) run --quiet scripts/match_offer.py "$(OFFER)" $(foreach tex,$(CVS),--cv $(tex))

# README previews of the published CVs, from the PDFs next to the sources.
preview:
	@$(SH); need pdftoppm "$$poppler"; \
	mkdir -p "$(PREVIEW_DIR)"; \
	for tex in $(PUBLISHED); do \
	  name=$$(basename "$$tex" .tex); \
	  pdftoppm -png -r $(PREVIEW_DPI) -singlefile "$${tex%.tex}.pdf" "$(PREVIEW_DIR)/$$name"; \
	  echo "    $(PREVIEW_DIR)/$$name.png"; \
	done

# LinkedIn banner: one PNG and one PDF per language (L) and theme (THEME).
banner:
	@BUILD_DIR="$(BUILD_DIR)/linkedin-banner" LATEXMK="$(LATEXMK)" \
	  sh linkedin-banner/build.sh "$(L)" "$(THEME)"

# The Python scripts themselves: lint, formatting and unit tests (settings in pyproject.toml).
# --no-fix: report a problem instead of fixing it, as CI must.
test:
	@$(SH); need "$(UV)" "$$uv"; \
	$(UV) run --quiet ruff check --no-fix scripts tests; \
	$(UV) run --quiet ruff format --check scripts tests; \
	$(UV) run --quiet pytest -q

# Rebuild the first CV of the list on every save, as a test build (stop with Ctrl-C).
watch:
	@$(SH); need "$(LATEXMK)" "install TeX Live or MacTeX"; \
	set -- $(CVS); tex="$$1"; \
	echo "==> watching $$tex, pdf: $(TRY_DIR)/$$(basename "$$tex" .tex).pdf"; \
	cd "$$(dirname "$$tex")" && \
	exec $(LATEXMK) $(LATEXMK_FLAGS) -pvc -auxdir="$(TRY_DIR)" -outdir="$(TRY_DIR)" "$$(basename "$$tex")"

clean:
	@if [ "$(BUILD_DIR)" = / ]; then echo "error: refusing to delete /" >&2; exit 1; fi
	rm -rf "$(BUILD_DIR)"

help:
	@echo "make            build both CVs next to their sources (same as: make build)"
	@echo "make en         build the English CV only (make fr: the French one)"
	@echo "make try        test build outside the repository: page count, text changes"
	@echo "make check      the CI checks on a fresh build: $(PAGES) page, ATS text, PDF up to date"
	@echo "make ats        read the PDFs with six text extractors, as an ATS does, and compare"
	@echo "make links      check that every web link of the PDFs still opens"
	@echo "make match      compare a job offer with the CV: make match OFFER=offer.txt"
	@echo "make preview    regenerate the README previews in $(PREVIEW_DIR)/"
	@echo "make banner     build the LinkedIn banner (PNG and PDF) in linkedin-banner/"
	@echo "make test       lint and test the Python scripts of scripts/"
	@echo "make watch      test build on every save (first CV of the list; L=fr for French)"
	@echo "make clean      delete the build files in $(BUILD_DIR)"
	@echo
	@echo "Options:  L=fr                one language instead of both"
	@echo "          CVS=path/to/cv.tex  another .tex (build, try, check, ats, links, match, watch)"
	@echo "          OFFER=offer.txt     the job offer of make match: text or PDF file, or - for stdin"
	@echo "          PAGES=2             expected number of pages"
	@echo "          PREVIEW_DPI=200     resolution of the previews (default 600)"
	@echo "          THEME=light         one theme of the banner instead of both"
	@echo "          BUILD_DIR=/path     where auxiliary files and test builds go"
	@echo "          V=1                 show the output of latexmk"

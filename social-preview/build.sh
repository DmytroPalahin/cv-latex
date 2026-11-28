#!/bin/sh
# Build the social preview of the repository from social-preview.tex: one PNG per theme.
#
# From the repository root:
#   sh social-preview/build.sh            dark and light  (same as: make social)
#   sh social-preview/build.sh dark       one theme
#   DPI=72 sh social-preview/build.sh     PNG at 1280 x 640 px instead of 2560 x 1280 px
#
# Needs pdfLaTeX with latexmk (TeX Live / MacTeX) and Poppler (pdftoppm).
# Auxiliary files and the PDFs go to BUILD_DIR, outside the repository.
set -eu

BUILD_DIR="${BUILD_DIR:-/tmp/latex-build/social-preview}"
LATEXMK="${LATEXMK:-latexmk}"
DPI="${DPI:-144}"
themes="${1:-dark light}"

for tool in "$LATEXMK" pdftoppm; do
  command -v "$tool" >/dev/null 2>&1 || { echo "error: '$tool' not found" >&2; exit 1; }
done

cd "$(dirname "$0")"
mkdir -p "$BUILD_DIR"

for theme in $themes; do
  out="social-preview-$theme"
  if ! "$LATEXMK" -pdf -interaction=nonstopmode -halt-on-error -file-line-error \
       -jobname="$out" -auxdir="$BUILD_DIR" -outdir="$BUILD_DIR" \
       -usepretex="\\def\\PreviewTheme{$theme}" \
       social-preview.tex >"$BUILD_DIR/$out.latexmk.txt" 2>&1; then
    grep -E -A3 '^[^ ]+\.tex:[0-9]+: |^! ' "$BUILD_DIR/$out.log" | head -n 20 >&2 || true
    echo "error: $out did not compile (full log: $BUILD_DIR/$out.log)" >&2
    exit 1
  fi
  pdftoppm -png -r "$DPI" -singlefile "$BUILD_DIR/$out.pdf" "$out"
  echo "    social-preview/$out.png"
done

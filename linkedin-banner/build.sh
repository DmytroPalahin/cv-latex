#!/bin/sh
# Build the LinkedIn banner from linkedin-banner.tex: one PNG and one PDF per language and theme.
#
#   sh build.sh                     fr and en, light and dark  ->  png/ and pdf/  (same as: make banner)
#   sh build.sh fr dark             one variant
#   STATUS=0 sh build.sh fr light   without the status label in the top left corner (-plain)
#   GUIDES=1 sh build.sh fr light   with the profile-photo zone drawn (-guides.png, preview only)
#   DPI=72 sh build.sh              PNG at 1584 x 396 px instead of 3168 x 792 px
#
# Needs pdfLaTeX with latexmk (TeX Live / MacTeX) and Poppler (pdftoppm).
# Auxiliary files go to BUILD_DIR, outside the repository.
set -eu

BUILD_DIR="${BUILD_DIR:-/tmp/latex-build/linkedin-banner}"
LATEXMK="${LATEXMK:-latexmk}"
DPI="${DPI:-144}"
GUIDES="${GUIDES:-0}"
STATUS="${STATUS:-1}"
langs="${1:-fr en}"
themes="${2:-light dark}"

for tool in "$LATEXMK" pdftoppm; do
  command -v "$tool" >/dev/null 2>&1 || { echo "error: '$tool' not found" >&2; exit 1; }
done

cd "$(dirname "$0")"
mkdir -p "$BUILD_DIR" png pdf

for lang in $langs; do
  for theme in $themes; do
    out="linkedin-banner-$lang-$theme"
    if [ "$STATUS" = 0 ]; then out="$out-plain"; fi
    if [ "$GUIDES" = 1 ]; then out="$out-guides"; fi
    if ! "$LATEXMK" -pdf -interaction=nonstopmode -halt-on-error -file-line-error \
         -jobname="$out" -auxdir="$BUILD_DIR" -outdir="$BUILD_DIR" \
         -usepretex="\\def\\BannerLang{$lang}\\def\\BannerTheme{$theme}\\def\\BannerGuides{$GUIDES}\\def\\BannerStatus{$STATUS}" \
         linkedin-banner.tex >"$BUILD_DIR/$out.latexmk.txt" 2>&1; then
      grep -E -A3 '^[^ ]+\.tex:[0-9]+: |^! ' "$BUILD_DIR/$out.log" | head -n 20 >&2 || true
      echo "error: $out did not compile (full log: $BUILD_DIR/$out.log)" >&2
      exit 1
    fi
    pdftoppm -png -r "$DPI" -singlefile "$BUILD_DIR/$out.pdf" "png/$out"
    echo "    png/$out.png"
    if [ "$GUIDES" != 1 ]; then
      cp "$BUILD_DIR/$out.pdf" "pdf/$out.pdf"
      echo "    pdf/$out.pdf"
    fi
  done
done

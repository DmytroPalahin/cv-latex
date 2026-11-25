#!/bin/sh
# Build the LinkedIn banner from linkedin-banner.tex: one PNG and one PDF per language and theme.
#
# From the repository root:
#   sh linkedin-banner/build.sh                     en and fr, dark and light  ->  png/ and pdf/  (same as: make banner)
#   sh linkedin-banner/build.sh en dark             one variant
#   STATUS=0 sh linkedin-banner/build.sh en dark    without the status label in the top left corner (-plain)
#   EMAIL=0 sh linkedin-banner/build.sh en dark     without the email address under the skills (-noemail)
#   GUIDES=1 sh linkedin-banner/build.sh en dark    with the profile-photo zone drawn (-guides.png, preview only)
#   DPI=72 sh linkedin-banner/build.sh              PNG at 1584 x 396 px instead of 3168 x 792 px
#
# Needs pdfLaTeX with latexmk (TeX Live / MacTeX) and Poppler (pdftoppm).
# Auxiliary files go to BUILD_DIR, outside the repository.
set -eu

BUILD_DIR="${BUILD_DIR:-/tmp/latex-build/linkedin-banner}"
LATEXMK="${LATEXMK:-latexmk}"
DPI="${DPI:-144}"
GUIDES="${GUIDES:-0}"
STATUS="${STATUS:-1}"
EMAIL="${EMAIL:-1}"
langs="${1:-en fr}"
themes="${2:-dark light}"

for tool in "$LATEXMK" pdftoppm; do
  command -v "$tool" >/dev/null 2>&1 || { echo "error: '$tool' not found" >&2; exit 1; }
done

cd "$(dirname "$0")"
mkdir -p "$BUILD_DIR" png pdf

for lang in $langs; do
  for theme in $themes; do
    out="linkedin-banner-$lang-$theme"
    if [ "$STATUS" = 0 ]; then out="$out-plain"; fi
    if [ "$EMAIL" = 0 ]; then out="$out-noemail"; fi
    if [ "$GUIDES" = 1 ]; then out="$out-guides"; fi
    if ! "$LATEXMK" -pdf -interaction=nonstopmode -halt-on-error -file-line-error \
         -jobname="$out" -auxdir="$BUILD_DIR" -outdir="$BUILD_DIR" \
         -usepretex="\\def\\BannerLang{$lang}\\def\\BannerTheme{$theme}\\def\\BannerGuides{$GUIDES}\\def\\BannerStatus{$STATUS}\\def\\BannerEmail{$EMAIL}" \
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

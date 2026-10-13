#!/usr/bin/env bash
# One-shot pipeline: deck script -> spec/html -> PPTX (font embedded) -> PDF -> verification.
# usage: scripts/build.sh my_deck.py fonts/ZCOOLKuaiLe.ttf out/ "deck-name"
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
deck_py="$1"; font="$2"; out="$3"; name="${4:-deck}"
mkdir -p "$out"

echo "== 1/5 layout"
python3 "$deck_py" "$font" "$out"
face="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["font"])' "$out/spec.json")"

echo "== 2/5 pptx"
node "$here/build_pptx.js" "$out/spec.json" "$out/raw.pptx"
python3 "$here/embed_font.py" "$out/raw.pptx" "$out/$name.pptx" "$font" "$face"
rm -f "$out/raw.pptx"

echo "== 3/5 previews + pdf"
node "$here/render.js" "$out/deck.html" "$out/shots" "$name.pdf"
mv "$out/shots/$name.pdf" "$out/$name.pdf"

echo "== 4/5 rebuild slides from the pptx itself"
python3 "$here/pptx_to_html.py" "$out/$name.pptx" "$out/check.html" "$font"
node "$here/render.js" "$out/check.html" "$out/check_shots"

echo "== 5/5 compare"
python3 "$here/compare.py" "$out/shots" "$out/check_shots"
echo "done: $out/$name.pptx  $out/$name.pdf  (review $out/shots/sheet*.png)"

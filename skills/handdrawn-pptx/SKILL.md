---
name: handdrawn-pptx
description: Build hand-drawn ("手绘"), black-and-white slide decks as an editable PPTX plus a PDF, with a handwriting font for all text and wobbly sketch lines for boxes, arrows, circles, check marks, tables and marker labels. Use when someone asks for a deck or training slides in a hand-drawn, sketch, whiteboard or doodle style, or for a minimal black & white deck with a handwriting font.
---

# Hand-drawn black & white decks

A Python layout script describes the slides. One layout feeds two outputs, so the preview you check
is exactly what lands in the PPTX:

```
deck.py ──► spec.json ──► build_pptx.js ──► embed_font.py ──► deck.pptx  (editable shapes + text, font embedded)
        └─► deck.html ──► render.js ──────────────────────────► deck.pdf + PNG previews
deck.pptx ──► pptx_to_html.py ──► render.js ──► compare.py   (verifies the PPTX itself, no PowerPoint needed)
```

- **Shapes** are native PowerPoint custom-geometry paths (double, slightly wobbly strokes, overshooting
  corners, in the style of rough.js). Users can still move and resize them.
- **Text** stays editable. Wrapping uses the font's real advance widths, so line breaks match both renderers.
- **Font** is embedded in the PPTX, and the PDF always shows it.

## Setup (once per machine)

```bash
cd skills/handdrawn-pptx
pip install -r requirements.txt           # fonttools, lxml, Pillow
npm install                                # pptxgenjs, playwright
python3 scripts/fetch_font.py "ZCOOL KuaiLe" fonts/   # any Google Fonts family works
```

Chromium: `render.js` uses Playwright's browser, else `$CHROME`, else any
`$PLAYWRIGHT_BROWSERS_PATH/chromium-*/chrome-linux/chrome`. No LibreOffice is needed.

## Make a deck

1. Copy `examples/example_deck.py` and write the slides (API below).
2. Run the pipeline:

   ```bash
   scripts/build.sh my_deck.py fonts/ZCOOLKuaiLe.ttf out/ my-deck
   ```

   You get `out/my-deck.pptx` and `out/my-deck.pdf`, previews in `out/shots/`, and contact sheets
   `out/shots/sheet*.png` (4 slides each).
3. **Look at every contact sheet** before delivering. Fix the layout script and rerun.
   A deck script that ends like the example (`if deck.save(...): sys.exit(...)`) stops the pipeline on
   layout warnings (text overflow, missing glyphs). Step 5 exits non-zero if the
   slides redrawn from the PPTX differ from the design.

The deck script contract is `python3 my_deck.py <font.ttf> <out_dir>`, ending with `deck.save(out_dir)`.

## API (`lib/handdrawn.py`)

All units are inches. The canvas defaults to 13.333 × 7.5 (16:9). The title sits at y≈0.42 and content starts at y≈1.6.

| Call | Draws |
| --- | --- |
| `Deck(font_path, font_name, title=..., roughness=1.0, page_numbers=True)` | the deck; `deck.columns(n, x=0.8, gap=0.32)` → `[(x, w), …]` |
| `deck.slide(title=None, notes='')` | a slide; title at 32pt; notes become speaker notes |
| `s.text(x, y, w, s, pt, align='left', color='000000')` | top-anchored, auto-wrapped text; returns height used |
| `s.text_vc(x, y, w, h, s, pt, align)` | text vertically centred in a band |
| `s.box(x, y, w, h, double=True)` | sketchy rectangle |
| `s.ellipse(cx, cy, rx, ry)` / `s.arrow(p1, p2)` / `s.line(p1, p2)` | circle, arrow, line |
| `s.frame()` | sketchbook border for cover / closing slides |
| `s.card(x, y, w, h, title, body, foot=None)` | box with heading, body, footer |
| `s.label(x, y, w, h, text)` | black marker blob with white text (the one strong emphasis on a slide) |
| `s.numbered(x, y, n)` | circled number |
| `s.checklist(x, y, w, items)` / `s.bullets(x, y, w, items)` | hand-ticked boxes / hand-drawn dashes; return next y |
| `s.table(x, y, widths, row_h, rows, pt, head_pt)` | sketchy grid; `rows[0]` is the header |
| `s.flow(x, y, labels, box_w, gap)` | boxes joined by arrows |
| `s.stroke(paths)` / `s.fill(pts)` + `s.pen.*` | anything custom (`pen.rect/ellipse/line/arrow/check/cross/blob`) |

## Design rules

- **Black and white only.** White background, black ink. White text appears only on a black `label`.
  Emphasis comes from size, a circle around a word, or one black label per slide, never grey or colour.
- **Simple.** One message per slide, as the title. Put three to six short items on the slide and the
  explanation in `notes`.
- **Sizes:** cover 54–60pt, slide title 32pt, card heading 20–24pt, body 15–18pt, captions 13–14pt.
  Don't go below 13pt.
- **Grid:** 0.8" side margins, content width 11.73". Use `deck.columns(n)` for cards, keep 0.3" or more
  between blocks, and keep text 0.25" inside boxes.
- **Size boxes to their content.** If a box shows a large empty strip at the bottom after rendering, shrink it.
- **Glyphs:** handwriting fonts often miss symbols such as `→ ≤ ≥ ☐ ÷`. `deck.save` lists the missing
  ones. Reword (use "以内", "以上") or draw them (`arrow`, `checklist`) instead of typing them.
- **Line breaks:** for card bodies, put explicit `\n` at natural phrase breaks. Don't let a word or a
  number split across lines.

## Fonts

Any TrueType font whose licence allows embedding works (`embed_font.py` refuses restricted fonts).

| Font (Google Fonts) | Character |
| --- | --- |
| **ZCOOL KuaiLe** (站酷快乐体) | marker-pen handwriting, very readable on a projector (default) |
| Ma Shan Zheng (马善政毛笔楷书) | brush handwriting, strong for titles |
| Long Cang / Zhi Mang Xing | cursive; titles only, hard to read in body text |
| LXGW WenKai TC | calm handwriting with wide coverage, but uses traditional glyph forms |

## Known limits

- The embedded font is stored as a plain TrueType part (`ppt/fonts/font1.fntdata`). Some PowerPoint
  versions may ignore it and fall back to another font. The PDF is always exact. If a viewer needs
  the editable PPTX to look right, have them install the font.
- The verification step proves the PPTX geometry and text match the design. It cannot measure
  PowerPoint's own text layout. Each text box gets 0.16" of extra width so PowerPoint never wraps
  a line the design didn't wrap.
- Each `deck.slide()` call gets its own random seed, so the strokes are stable between runs. Inserting a
  slide changes the wobble of the slides after it, which is harmless.

## Files

```
lib/handdrawn.py        layout + rough pen + text metrics; writes spec.json and deck.html
scripts/build.sh        full pipeline
scripts/build_pptx.js   spec.json -> PPTX (pptxgenjs custom geometry + text boxes + notes)
scripts/embed_font.py   embed the TTF, strip outlines from black labels
scripts/render.js       HTML -> PNG per slide (+ PDF)
scripts/pptx_to_html.py redraw slides from the PPTX XML (independent check)
scripts/compare.py      pixel diff design vs. PPTX redraw, contact sheets
scripts/fetch_font.py   download a Google Fonts family as TTF
examples/example_deck.py every component on five slides
```

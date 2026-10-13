#!/usr/bin/env node
// Build an editable PPTX from spec.json (written by handdrawn.Deck.save).
// usage: node build_pptx.js out/spec.json out/raw.pptx
// Strokes and black labels become native custom-geometry shapes; text stays editable.
const fs = require('fs');
const pptxgen = require('pptxgenjs');

const [specPath, outPath] = process.argv.slice(2);
if (!specPath || !outPath) {
  console.error('usage: node build_pptx.js spec.json out.pptx');
  process.exit(2);
}
const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
const pres = new pptxgen();
pres.defineLayout({ name: 'HANDDRAWN', width: spec.W, height: spec.H });
pres.layout = 'HANDDRAWN';
pres.title = spec.title || 'Deck';
pres.theme = { headFontFace: spec.font, bodyFontFace: spec.font };

const r3 = (v) => Math.round(v * 1000) / 1000;
function bbox(paths) {
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (const p of paths) for (const [x, y] of p) {
    x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y);
  }
  return { x0, y0, w: Math.max(x1 - x0, 0.01), h: Math.max(y1 - y0, 0.01) };
}

// Text boxes get a little extra width so PowerPoint's own metrics never force an unplanned wrap.
const SLACK = 0.16;

spec.slides.forEach((sl, si) => {
  const slide = pres.addSlide();
  slide.background = { color: 'FFFFFF' };
  sl.items.forEach((it, n) => {
    if (it.type === 'stroke' || it.type === 'fill') {
      const paths = it.type === 'stroke' ? it.paths : [it.pts];
      const b = bbox(paths);
      const points = [];
      for (const p of paths) {
        p.forEach(([x, y], i) => {
          const pt = { x: r3(x - b.x0), y: r3(y - b.y0) };
          if (i === 0) pt.moveTo = true;
          points.push(pt);
        });
        if (it.type === 'fill') points.push({ close: true });
      }
      const opts = { x: b.x0, y: b.y0, w: b.w, h: b.h, points, objectName: `${it.type}-${si + 1}-${n + 1}` };
      if (it.type === 'stroke') opts.line = { color: '000000', width: it.width };
      else opts.fill = { color: '000000' }; // outline removed in embed_font.py
      slide.addShape(pres.shapes.CUSTOM_GEOMETRY, opts);
    } else {
      let x = it.x;
      if (it.align === 'center') x -= SLACK / 2;
      if (it.align === 'right') x -= SLACK;
      const runs = it.lines.map((t, i) => ({ text: t, options: i < it.lines.length - 1 ? { breakLine: true } : {} }));
      slide.addText(runs, {
        x, y: it.y, w: it.w + SLACK, h: it.h + 0.05, isTextBox: true, margin: 0,
        fontFace: spec.font, lang: 'zh-CN', fontSize: it.pt, color: it.color, align: it.align, valign: 'top',
        lineSpacing: Math.round(it.pt * spec.LH * 10) / 10, objectName: `text-${si + 1}-${n + 1}`,
      });
    }
  });
  if (sl.notes) slide.addNotes(sl.notes);
});

pres.writeFile({ fileName: outPath }).then(() => console.log('wrote', outPath));

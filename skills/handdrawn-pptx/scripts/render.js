#!/usr/bin/env node
// Render every <section> of an HTML deck to PNG, and optionally the whole deck to PDF (fonts embedded).
// usage: node render.js deck.html outdir [deck.pdf]
// Browser: Playwright's own, else $CHROME, else any chromium-*/chrome-linux/chrome under $PLAYWRIGHT_BROWSERS_PATH.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

function findChromium() {
  if (process.env.CHROME) return process.env.CHROME;
  const root = process.env.PLAYWRIGHT_BROWSERS_PATH;
  if (!root || !fs.existsSync(root)) return undefined;
  const dirs = fs.readdirSync(root).filter((d) => /^chromium-\d+$/.test(d)).sort().reverse();
  for (const d of dirs) {
    const exe = path.join(root, d, 'chrome-linux', 'chrome');
    if (fs.existsSync(exe)) return exe;
  }
  return undefined;
}

async function launch() {
  try {
    return await chromium.launch();
  } catch (e) {
    const exe = findChromium();
    if (!exe) throw e;
    return chromium.launch({ executablePath: exe });
  }
}

(async () => {
  const [html, out, pdfName] = process.argv.slice(2);
  fs.mkdirSync(out, { recursive: true });
  const browser = await launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1.5 });
  await page.goto('file://' + path.resolve(html));
  await page.evaluate(() => document.fonts.ready);
  const secs = await page.$$('section');
  for (let i = 0; i < secs.length; i++) {
    await secs[i].screenshot({ path: path.join(out, `s${String(i + 1).padStart(2, '0')}.png`) });
  }
  if (pdfName) {
    const box = await secs[0].boundingBox();
    await page.pdf({ path: path.join(out, pdfName), width: `${box.width / 96}in`, height: `${box.height / 96}in`, printBackground: true });
  }
  await browser.close();
  console.log(`rendered ${secs.length} slides -> ${out}`);
})();

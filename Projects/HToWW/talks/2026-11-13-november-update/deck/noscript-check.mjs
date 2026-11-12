// Scripts-disabled Chromium check (approximates Obsidian's HTML viewer). Usage: node noscript-check.mjs
import { createRequire } from 'node:module';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { writeFile } from 'node:fs/promises';
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_CORE || '/home/cgupta/.t3/runtime/versions/0.1.6/node_modules/playwright-core');
const deck = dirname(fileURLToPath(import.meta.url));
const b = await chromium.launch({ executablePath: process.env.CHROME_BIN || '/usr/bin/google-chrome', headless: true, args: ['--no-sandbox'] });
const ctx = await b.newContext({ javaScriptEnabled: false, viewport: { width: 1280, height: 900 } });
const p = await ctx.newPage();
await p.goto(pathToFileURL(join(deck, 'index.html')).href);
const r = await p.evaluate(() => {
  const secs = [...document.querySelectorAll('.reveal .slides > section, section.slide')];
  return { sections: secs.length,
    visible: secs.filter(s => s.getBoundingClientRect().height > 50 && getComputedStyle(s).visibility !== 'hidden').length,
    hOverflow: document.documentElement.scrollWidth > window.innerWidth + 2,
    imgsBroken: [...document.images].filter(i => !i.complete || i.naturalWidth === 0).map(i => i.src) };
});
await writeFile(join(deck, '.render', 'scripts-off.json'), JSON.stringify({ viewer: 'Chromium, scripts disabled; not Obsidian itself', ...r }, null, 2));
console.log(JSON.stringify(r));
await b.close();

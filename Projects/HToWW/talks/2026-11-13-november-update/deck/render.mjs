// Local-only Reveal.js render check and numbered PDF export; no server needed.
import { createRequire } from 'node:module';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const require = createRequire(import.meta.url);
let chromium;
try {
  ({ chromium } = require(process.env.PLAYWRIGHT_CORE || 'playwright-core'));
} catch (error) {
  // Existing T3 dependency on this laptop; PLAYWRIGHT_CORE supports other hosts.
  ({ chromium } = require('/home/cgupta/.t3/runtime/versions/0.1.6/node_modules/playwright-core'));
}
const deck = dirname(fileURLToPath(import.meta.url));
const revision = process.argv.find(x => x.startsWith('--revision='))?.split('=')[1] || '1';
if (!/^[1-9]\d*$/.test(revision)) throw new Error('Use a positive integer revision');
const output = join(deck, `november-update_r${revision}.pdf`);
const render = join(deck, '.render');
await mkdir(render, { recursive: true });
const { existsSync } = require('node:fs');
if (existsSync(output) && !process.argv.includes('--replace')) {
  throw new Error(`PDF already exists: use a new revision, or --replace for review iterations`);
}
const browser = await chromium.launch({
  executablePath: process.env.CHROME_BIN || '/usr/bin/google-chrome',
  headless: true,
  args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-background-networking'],
});
const errors = [], failed = [], external = [], slides = [];
try {
  const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
  await context.route(/^https?:\/\//, async route => {
    external.push(route.request().url());
    await route.abort();
  });
  const page = await context.newPage();
  page.on('pageerror', e => errors.push(e.message));
  page.on('requestfailed', r => failed.push({ url: r.url(), error: r.failure()?.errorText }));
  const url = pathToFileURL(join(deck, 'index.html')).href;
  await page.goto(url);
  await page.waitForFunction(() => window.Reveal?.isReady());
  await page.evaluate(() => document.fonts.ready);
  const count = await page.evaluate(() => Reveal.getTotalSlides());
  for (let i = 0; i < count; i++) {
    await page.evaluate(i => Reveal.slide(i), i);
    await page.evaluate(() => new Promise(requestAnimationFrame));
    const check = await page.evaluate(() => {
      const s = Reveal.getCurrentSlide();
      const box = s.getBoundingClientRect();
      const overflow = [...s.querySelectorAll('h1,h2,p,li,table,blockquote')]
        .filter(e => getComputedStyle(e).display !== 'none')
        .filter(e => {
          const r = e.getBoundingClientRect();
          return r.left < box.left - 2 || r.right > box.right + 2 || r.top < box.top - 2 || r.bottom > box.bottom + 2;
        }).map(e => e.textContent.slice(0, 100));
      return { id: s.id, height: s.scrollHeight, overflow, title: s.querySelector('h1,h2')?.textContent };
    });
    slides.push(check);
    await page.screenshot({ path: join(render, `${String(i + 1).padStart(2, '0')}-${check.id}.png`) });
  }
  await page.goto(url + '?print-pdf');
  await page.waitForFunction(() => window.Reveal?.isReady() && document.querySelectorAll('.pdf-page').length > 0);
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: output, width: '1280px', height: '720px', printBackground: true, preferCSSPageSize: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
  const report = { revision: Number(revision), output, slides, errors, failed, external };
  await writeFile(join(render, 'check.json'), JSON.stringify(report, null, 2) + '\n');
  if (slides.some(s => s.overflow.length || s.height > 722) || errors.length || failed.length || external.length) {
    throw new Error(`Render checks failed: ${join(render, 'check.json')}`);
  }
  console.log(JSON.stringify({ output, slides: count, overflow: 0, errors: 0, externalRequests: 0 }));
} finally {
  await browser.close();
}

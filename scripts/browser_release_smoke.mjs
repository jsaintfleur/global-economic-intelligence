import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.ATLAS_PLAYWRIGHT_PACKAGE || "playwright");

const base = process.argv[2] || "http://127.0.0.1:8766";
const browser = await chromium.launch({
  headless: true,
  ...(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {}),
});
const failures = [];

for (const viewport of [{ name: "desktop", width: 1440, height: 900 }, { name: "mobile", width: 390, height: 844 }]) {
  const page = await browser.newPage({ viewport });
  const errors = [];
  page.on("console", message => { if (message.type() === "error") errors.push(message.text()); });
  page.on("pageerror", error => errors.push(error.message));
  await page.goto(`${base}/?view=overview`, { waitUntil: "networkidle" });
  if ((await page.locator("body").innerText()).trim().length < 100) failures.push(`${viewport.name}: blank page`);
  if (await page.locator("body").evaluate(element => element.scrollWidth > element.clientWidth + 1)) failures.push(`${viewport.name}: horizontal overflow`);
  await page.goto(`${base}/?view=country&country=USA`, { waitUntil: "networkidle" });
  const hero = await page.locator(".economy-hero").innerText();
  for (const label of ["COHORT RANK · 2024", "SHARE OF 2024 ATLAS COHORT GDP", "REAL GROWTH ·", "POPULATION ·"])
    if (!hero.includes(label)) failures.push(`${viewport.name}: hero missing ${label}`);
  await page.goto(`${base}/?view=rankings&metric=gdp_current_usd&year=1991`, { waitUntil: "networkidle" });
  const rankingText = await page.locator("main").innerText();
  if (!rankingText.includes("CONTEMPORANEOUS WORLDWIDE RANK")) failures.push(`${viewport.name}: worldwide ranking scope missing`);
  const rows = await page.locator("tbody tr").count();
  if (rows <= 50) failures.push(`${viewport.name}: historical ranking rendered only ${rows} rows`);
  if (errors.length) failures.push(`${viewport.name}: console errors: ${errors.join(" | ")}`);
  await page.close();
}

await browser.close();
if (failures.length) {
  console.error(failures.join("\n"));
  process.exit(1);
}
console.log("Browser smoke passed: desktop/mobile, no overflow/errors, explicit hero years, worldwide 1991 ranking.");

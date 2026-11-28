import { readFile, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const dist = path.join(root, "dist");
const html = await readFile(path.join(dist, "index.html"), "utf8");
const checks = [
  ["server-rendered hero", /<h1[^>]*id="hero-title"/.test(html)],
  ["server-rendered project case studies", html.includes("Agent Systems Labs") && html.includes("RAG Systems Labs")],
  ["canonical URL", html.includes('rel="canonical" href="https://amdeep.github.io/AmDeep/"')],
  ["Open Graph image", html.includes("https://amdeep.github.io/AmDeep/og-card.png")],
  ["LinkedIn contact URL", html.includes("https://www.linkedin.com/in/a-s-70a471a3/")],
];

const jsonLdMatch = html.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/);
let jsonLdValid = false;
if (jsonLdMatch) {
  try {
    const jsonLd = JSON.parse(jsonLdMatch[1]);
    jsonLdValid = jsonLd["@type"] === "Person" && jsonLd.sameAs.includes("https://www.linkedin.com/in/a-s-70a471a3/");
  } catch {
    jsonLdValid = false;
  }
}
checks.push(["valid Person structured data", jsonLdValid]);

for (const file of ["robots.txt", "sitemap.xml", "og-card.png"]) {
  try {
    const result = await stat(path.join(dist, file));
    checks.push([`public asset ${file}`, result.size > 0]);
  } catch {
    checks.push([`public asset ${file}`, false]);
  }
}

for (const [name, passed] of checks) {
  console.log(`${passed ? "PASS" : "FAIL"} ${name}`);
}
if (checks.some(([, passed]) => !passed)) {
  process.exitCode = 1;
}

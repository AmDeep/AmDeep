import { readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import React from "react";
import { renderToString } from "react-dom/server";
import { createServer } from "vite";

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const vite = await createServer({
  configFile: path.join(root, "vite.config.ts"),
  root,
  server: { middlewareMode: true, hmr: false },
  appType: "custom",
  optimizeDeps: { noDiscovery: true, include: [] },
});

try {
  const { default: App } = await vite.ssrLoadModule("/src/App.tsx");
  const markup = renderToString(React.createElement(App));
  const outputPath = path.join(root, "dist", "index.html");
  const html = await readFile(outputPath, "utf8");
  const rootMarker = '<div id="root"></div>';

  if (!html.includes(rootMarker)) {
    throw new Error("Expected the empty Vite root marker before prerendering.");
  }
  if (!markup.includes('id="hero-title"') || !markup.includes("Agent Systems Labs")) {
    throw new Error("The prerendered HTML is missing profile content.");
  }

  await writeFile(outputPath, html.replace(rootMarker, `<div id="root">${markup}</div>`));
  console.log(`Prerendered ${markup.length.toLocaleString()} HTML characters into dist/index.html.`);
} finally {
  await vite.close();
}

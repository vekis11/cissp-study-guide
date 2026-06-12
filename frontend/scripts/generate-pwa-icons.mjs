/**
 * Generate iOS / Android PWA PNG icons from the master SVG.
 * Run: node scripts/generate-pwa-icons.mjs
 */
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, "..");
const svgPath = join(root, "public", "icons", "icon.svg");
const svg = readFileSync(svgPath);

let sharp;
try {
  sharp = (await import("sharp")).default;
} catch {
  console.warn(
    "sharp not installed — skipping PNG generation. Run: npm install -D sharp && npm run icons"
  );
  process.exit(0);
}

const outputs = [
  { file: "apple-touch-icon.png", size: 180 },
  { file: "pwa-192x192.png", size: 192 },
  { file: "pwa-512x512.png", size: 512 },
  { file: "favicon-32x32.png", size: 32 },
];

for (const { file, size } of outputs) {
  const out = join(root, "public", file);
  await sharp(svg, { density: 300 })
    .resize(size, size, { fit: "contain", background: { r: 7, g: 11, b: 18, alpha: 1 } })
    .png({ compressionLevel: 9 })
    .toFile(out);
  console.log(`Wrote ${file} (${size}x${size})`);
}

// Multi-size favicon.ico substitute: copy 32px as favicon for browsers
writeFileSync(join(root, "public", "favicon.png"), readFileSync(join(root, "public", "favicon-32x32.png")));
console.log("Done.");

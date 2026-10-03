/**
 * Copies CesiumJS static runtime assets (Workers, ThirdParty, Assets, Widgets)
 * from node_modules into public/cesium so the 3D digital twin can load them from
 * the app's own origin (CesiumViewer sets window.CESIUM_BASE_URL = "/cesium/").
 *
 * Runs automatically on `npm install` (postinstall), `npm run dev` and `npm run build`.
 * public/cesium is gitignored: never commit these generated files.
 */
import { cpSync, existsSync, mkdirSync, rmSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const source = join(root, "node_modules", "cesium", "Build", "Cesium");
const target = join(root, "public", "cesium");
const folders = ["Workers", "ThirdParty", "Assets", "Widgets"];

if (!existsSync(source)) {
  console.error(`[copy-cesium-assets] ${source} not found. Run \`npm install\` first.`);
  process.exit(1);
}

rmSync(target, { recursive: true, force: true });
mkdirSync(target, { recursive: true });
for (const folder of folders) {
  cpSync(join(source, folder), join(target, folder), { recursive: true });
}
console.log(`[copy-cesium-assets] copied ${folders.join(", ")} -> public/cesium`);

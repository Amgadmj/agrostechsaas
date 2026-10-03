import { fileURLToPath } from "node:url";

/** @type {import('postcss-load-config').Config} */
const config = {
  plugins: {
    // Explicit path so Tailwind finds its config even when Next runs from another cwd.
    tailwindcss: { config: fileURLToPath(new URL("./tailwind.config.ts", import.meta.url)) },
    autoprefixer: {},
  },
};

export default config;

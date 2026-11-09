import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Static export: `next build` writes plain files to site/out/. No server, no API routes.
  output: "export",
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;

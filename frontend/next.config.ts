import path from "path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {
    root: path.resolve(__dirname),
  },
  generateBuildId: async () => {
    return "build-" + Date.now();
  },
};

export default nextConfig;

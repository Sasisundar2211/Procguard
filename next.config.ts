import type { NextConfig } from "next";

if (process.env.NODE_ENV === "production" && !process.env.NEXT_PUBLIC_API_URL) {
  console.warn("⚠️  WARNING: NEXT_PUBLIC_API_URL is missing. Backend functionality will fail.");
}

const nextConfig: NextConfig = {
  output: "standalone",

};

export default nextConfig;

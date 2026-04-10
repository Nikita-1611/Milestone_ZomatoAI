import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/v1/:path*",
        destination: `${process.env.BACKEND_URL || "https://zomato-ai-backend.onrender.com"}/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;

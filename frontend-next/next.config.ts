import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/v1/:path*",
        destination: `${process.env.BACKEND_URL || "https://milestonezomatoai.streamlit.app"}/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;

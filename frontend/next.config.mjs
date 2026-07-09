/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  webpack: (config, { dev }) => {
    // Avoid stale chunk/manifest corruption during HMR on Windows.
    if (dev) {
      config.cache = false;
    }
    return config;
  },
};

export default nextConfig;

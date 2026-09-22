"""Next.js configuration"""
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    appDir: true,
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack) => {
    // Add custom webpack config if needed
    return config;
  },
};

module.exports = nextConfig;
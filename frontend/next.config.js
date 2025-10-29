/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  typescript: {
    // TODO: Set to false once all TypeScript errors are resolved
    ignoreBuildErrors: false,
  },
  eslint: {
    // TODO: Set to false once all ESLint errors are resolved
    ignoreDuringBuilds: false,
  },
};

module.exports = nextConfig;


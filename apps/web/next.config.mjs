/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080',
    NEXT_PUBLIC_DEFAULT_DEMO_URL: process.env.NEXT_PUBLIC_DEFAULT_DEMO_URL || ''
  }
};
export default nextConfig;

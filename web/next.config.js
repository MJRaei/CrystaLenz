/**** @type {import('next').NextConfig} ****/
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_WS: process.env.NEXT_PUBLIC_API_WS || 'ws://localhost:8000',
    NEXT_PUBLIC_API_HTTP: process.env.NEXT_PUBLIC_API_HTTP || 'http://localhost:8000',
  }
}

module.exports = nextConfig

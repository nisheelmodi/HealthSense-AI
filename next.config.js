/** @type {import('next').NextConfig} */
const nextConfig = {
  /**
   * Proxy /api/* requests to the FastAPI backend.
   *
   * Why: The browser makes requests from wherever the page is opened
   * (e.g., http://10.224.186.12:3000). If the fetch URL were hardcoded
   * to http://127.0.0.1:8000, the browser would try to reach localhost
   * on the *user's own machine*, which has no backend.
   *
   * With this rewrite, the browser calls /api/predict (relative URL),
   * the Next.js *server* forwards it to http://127.0.0.1:8000/predict,
   * and the response is returned to the browser. CORS is no longer
   * needed for browser → backend since the browser only talks to Next.js.
   */
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.BACKEND_URL || 'http://127.0.0.1:8000'}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;

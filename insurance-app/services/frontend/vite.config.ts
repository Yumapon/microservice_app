import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': '/src',
    },
  },
  server: {
    proxy: {
      // 🔹BFF認証API（Keycloak経由）
      '/api/v1/auth': {
        target: 'http://localhost:8010',
        changeOrigin: true,
        rewrite: path => path.replace(/^\/api\/v1\/auth/, '/api/v1/auth'),
      },
      // 🔹その他API（通知など）
      '/api': {
        target: 'http://localhost:8005',
        changeOrigin: true,
        rewrite: path => path.replace(/^\/api/, '/api'),
      },
    },
  },
})
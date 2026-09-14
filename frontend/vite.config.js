import { defineConfig, searchForWorkspaceRoot, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'
import { fileURLToPath, URL } from 'node:url'
import path from 'node:path'

export default defineConfig(({ mode }) => {
  // Загружаем переменные из .env
  const env = loadEnv(mode, process.cwd(), '')

  // Собираем базовый URL для API (например, 'http://localhost:8000')
  const apiHost = env.API_HOST || 'localhost'
  const apiPort = env.API_PORT || '8000'
  const apiTarget = `http://${apiHost}:${apiPort}`
  const wsTarget = `ws://${apiHost}:${apiPort}`

  return {
    plugins: [vue(), vuetify({ autoImport: true })],

    optimizeDeps: {
      noDiscovery: true,
      exclude: ['vuetify'],
    },

    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    server: {
      host: env.VITE_HOST || 'localhost',
      port: parseInt(env.VITE_PORT) || 5173,
      fs: {
        allow: [
          searchForWorkspaceRoot(process.cwd()),
          path.resolve(import.meta.dirname, '..'),
        ],
      },
      proxy: {
        '/api': {
          target: apiTarget, // Использует http://localhost:8000 из .env
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
        },
        '/ws': {
          target: wsTarget,   // Использует ws://localhost:8000 из .env
          ws: true,
          changeOrigin: true,
        },
      },
    },
  }
})

import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const backend = env.VITE_BACKEND || 'http://localhost:8000'
  return {
    plugins: [react()],
    server: {
      proxy: {
        '/start': backend,
        '/status': backend
      }
    }
  }
})

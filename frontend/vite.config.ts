import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/pulse_of_pair/',
  server: {
    host: '0.0.0.0',
    port: 3000,
    allowedHosts: [
      'gallery.homoludens.photos',
      'localhost',
      '127.0.0.1',
      '192.168.2.228'
    ],
    // Настройки для работы за прокси
    proxy: {
      '/pulse_of_pair/api': {
        target: 'http://192.168.2.228:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/pulse_of_pair\/api/, '')
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  }
})

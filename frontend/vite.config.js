import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

const SITE = process.env.FRAPPE_SITE || 'giftshop.localhost'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: { '@': path.resolve(__dirname, 'src') },
  },
  base: '/assets/onerc_giftshop/shop/',
  build: {
    outDir: '../onerc_giftshop/public/shop',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        shop: path.resolve(__dirname, 'src/main.js'),
        manager: path.resolve(__dirname, 'src/manager/main.js'),
      },
      output: {
        entryFileNames: '[name].js',
        chunkFileNames: '[name]-[hash].js',
        assetFileNames: '[name][extname]',
      },
    },
  },
  server: {
    port: 8082,
    proxy: {
      '/api': { target: `http://${SITE}:8000`, changeOrigin: true },
      '/assets': { target: `http://${SITE}:8000`, changeOrigin: true },
      '/private': { target: `http://${SITE}:8000`, changeOrigin: true },
    },
  },
})

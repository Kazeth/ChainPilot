import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';
import { fileURLToPath, URL } from 'url';
import environment from 'vite-plugin-environment';

export default defineConfig({
  base: './',
  plugins: [
    react(), 
    environment('all', { prefix: 'CANISTER_' }), 
    environment('all', { prefix: 'DFX_' })
  ],
  envDir: '../',
  build: {
    rollupOptions: {
      external: ['tailwind-merge'],
    },
  },
  define: {
    'process.env': process.env
  },
  optimizeDeps: {
    esbuildOptions: {
      define: {
        global: 'globalThis'
      }
    }
  },
  resolve: {
    alias: [
      {
        find: 'declarations',
        replacement: fileURLToPath(new URL('./src/declarations', import.meta.url))
      },
      {
        find: '@',
        replacement: fileURLToPath(new URL('./src', import.meta.url))
      }
    ]
  },
  server: {
    watch: {
      usePolling: true,
    },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:4943',
        changeOrigin: true
      },
    },
    host: '127.0.0.1'
  }
});
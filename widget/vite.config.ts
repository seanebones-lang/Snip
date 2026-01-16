import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    lib: {
      entry: 'src/widget.ts',
      name: 'SnipWidget',
      fileName: () => 'widget.js',
      formats: ['iife']
    },
    outDir: 'dist',
    minify: 'terser',
    rollupOptions: {
      output: {
        inlineDynamicImports: true
      }
    }
  },
  define: {
    'process.env.NODE_ENV': '"production"'
  }
})

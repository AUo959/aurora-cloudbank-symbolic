import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@/components': path.resolve(__dirname, './src/components'),
      '@/features': path.resolve(__dirname, './src/features'),
      '@/lib': path.resolve(__dirname, './src/lib'),
      '@/hooks': path.resolve(__dirname, './src/hooks'),
      '@/stores': path.resolve(__dirname, './src/stores'),
      '@/types': path.resolve(__dirname, './src/types'),
      '@/pages': path.resolve(__dirname, './src/pages'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        // Vite 8 / Rollup 4 dropped the object form of manualChunks — it now
        // warns "Invalid type: Expected Function but received Object" and
        // silently stops chunking. Same grouping, expressed as the function
        // form: match on the module id rather than declaring package lists.
        //
        // Matching is on `/node_modules/<name>/` so a package cannot be caught
        // by a substring of an unrelated dependency's path.
        manualChunks(id: string) {
          if (!id.includes('node_modules')) return undefined;

          // Every group here corresponds to packages the app actually imports,
          // so every group emits a chunk. When a feature adds a dependency
          // worth splitting out — see the install steps in ARCHITECTURE.md —
          // add its group at the same time, so this list never describes
          // packages that are not installed.
          const groups: Record<string, string[]> = {
            'react-vendor': ['react', 'react-dom', 'react-router-dom'],
            'editor-vendor': ['@monaco-editor/react', 'monaco-editor'],
          };

          const normalised = id.replaceAll('\\', '/');
          for (const [chunk, packages] of Object.entries(groups)) {
            if (packages.some((pkg) => normalised.includes(`/node_modules/${pkg}/`))) {
              return chunk;
            }
          }
          return undefined;
        },
      },
    },
    chunkSizeWarningLimit: 1000,
  },
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom'],
  },
});

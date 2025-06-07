import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import { visualizer } from 'rollup-plugin-visualizer';
import { resolve } from 'path';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  
  return {
    plugins: [
      react({
        babel: {
          plugins: [
            ['@babel/plugin-transform-react-jsx', {
              runtime: 'automatic',
              importSource: 'react'
            }]
          ]
        }
      }),
      ...(process.env.VITE_BUILD_VISUALIZER === 'true' ? [
        visualizer({
          filename: 'dist/stats.html',
          open: true,
          gzipSize: true,
          brotliSize: true,
        })
      ] : []),
    ],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        '@components': path.resolve(__dirname, './src/components'),
        '@components/icons': path.resolve(__dirname, './src/components/icons'),
        '@hooks': path.resolve(__dirname, './src/hooks'),
        '@types': path.resolve(__dirname, './src/types'),
        '@utils': path.resolve(__dirname, './src/utils'),
        '@context': path.resolve(__dirname, './src/context'),
        '@pages': path.resolve(__dirname, './src/pages'),
        '@layout': path.resolve(__dirname, './src/layout'),
      },
    },
    optimizeDeps: {
      include: ['react', 'react-dom', 'react-router-dom'],
      exclude: [],
    },
    server: {
      port: 3003,
      host: true,
      proxy: {
        '/api': {
          target: env.VITE_API_URL || 'http://localhost:8000',
          changeOrigin: true,
        },
      },
    },
    build: {
      target: 'esnext',
      outDir: 'dist',
      assetsDir: 'assets',
      sourcemap: true,
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: true,
          drop_debugger: true,
        },
      },
      rollupOptions: {
        input: {
          main: resolve(__dirname, 'index.html'),
        },
        external: ['react/jsx-dev-runtime'],
        preserveEntrySignatures: 'strict',
        treeshake: {
          moduleSideEffects: true,
        },
        manualChunks: {
          vendor: ['react', 'react-dom'],
        },
      },
    },
    define: {
      'process.env': {
        NODE_ENV: JSON.stringify(mode),
        VITE_API_URL: JSON.stringify(env.VITE_API_URL),
        VITE_ENV: JSON.stringify(env.VITE_ENV),
        VITE_APP_NAME: JSON.stringify(env.VITE_APP_NAME),
        VITE_APP_VERSION: JSON.stringify(env.VITE_APP_VERSION),
        VITE_APP_DESCRIPTION: JSON.stringify(env.VITE_APP_DESCRIPTION),
        VITE_APP_AUTHOR: JSON.stringify(env.VITE_APP_AUTHOR),
        VITE_APP_REPOSITORY: JSON.stringify(env.VITE_APP_REPOSITORY),
        VITE_APP_LICENSE: JSON.stringify(env.VITE_APP_LICENSE),
        VITE_APP_BUGS_URL: JSON.stringify(env.VITE_APP_BUGS_URL),
        VITE_APP_HOMEPAGE: JSON.stringify(env.VITE_APP_HOMEPAGE),
      },
    },
  };
});

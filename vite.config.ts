import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  
  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        '@components': path.resolve(__dirname, './src/components'),
        '@utils': path.resolve(__dirname, './src/utils'),
        '@hooks': path.resolve(__dirname, './src/hooks'),
        '@contexts': path.resolve(__dirname, './src/contexts'),
      },
    },
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: env.VITE_API_URL || 'http://localhost:8000',
          changeOrigin: true,
        },
      },
    },
    build: {
      outDir: 'dist',
      sourcemap: true,
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
          },
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

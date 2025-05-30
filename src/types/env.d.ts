/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_API_KEY: string;
  readonly VITE_ENV: 'development' | 'production' | 'test';
  readonly VITE_APP_NAME: string;
  readonly VITE_APP_VERSION: string;
  readonly VITE_APP_DESCRIPTION: string;
  readonly VITE_APP_AUTHOR: string;
  readonly VITE_APP_REPOSITORY: string;
  readonly VITE_APP_LICENSE: string;
  readonly VITE_APP_BUGS_URL: string;
  readonly VITE_APP_HOMEPAGE: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
} 
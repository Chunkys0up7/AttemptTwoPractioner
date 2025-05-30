import { z } from 'zod';

const envSchema = z.object({
  VITE_API_URL: z.string().url(),
  VITE_API_KEY: z.string().min(1),
  VITE_ENV: z.enum(['development', 'production', 'test']),
  VITE_APP_NAME: z.string().min(1),
  VITE_APP_VERSION: z.string().min(1),
  VITE_APP_DESCRIPTION: z.string().min(1),
  VITE_APP_AUTHOR: z.string().min(1),
  VITE_APP_REPOSITORY: z.string().url(),
  VITE_APP_LICENSE: z.string().min(1),
  VITE_APP_BUGS_URL: z.string().url(),
  VITE_APP_HOMEPAGE: z.string().url(),
});

type Env = z.infer<typeof envSchema>;

function validateEnv(): Env {
  try {
    return envSchema.parse(import.meta.env);
  } catch (error) {
    if (error instanceof z.ZodError) {
      const missingVars = error.errors.map(err => err.path.join('.')).join(', ');
      throw new Error(`Missing or invalid environment variables: ${missingVars}`);
    }
    throw error;
  }
}

export const env = validateEnv();

export function getApiUrl(): string {
  return env.VITE_API_URL;
}

export function getApiKey(): string {
  return env.VITE_API_KEY;
}

export function isDevelopment(): boolean {
  return env.VITE_ENV === 'development';
}

export function isProduction(): boolean {
  return env.VITE_ENV === 'production';
}

export function isTest(): boolean {
  return env.VITE_ENV === 'test';
} 
// formatters.ts
// Utility for formatting code in the browser using Prettier (JS/TS) and Ruff WASM (Python)

// Prettier for JS/TS
import prettier from 'prettier/standalone';
import parserBabel from 'prettier/parser-babel';
// Ruff WASM for Python
import initRuff, { format as ruffFormat } from '@wasm-fmt/ruff_fmt';

let ruffInitialized = false;

export async function formatCode(code: string, language: string): Promise<string> {
  if (language === 'python') {
    if (!ruffInitialized) {
      await initRuff();
      ruffInitialized = true;
    }
    try {
      return ruffFormat(code);
    } catch (err: any) {
      throw new Error('Ruff formatting failed: ' + (err?.message || err));
    }
  }
  if (language === 'typescript' || language === 'javascript' || language === 'js' || language === 'ts') {
    try {
      return prettier.format(code, {
        parser: 'babel',
        plugins: [parserBabel],
        semi: true,
        singleQuote: true,
      });
    } catch (err: any) {
      throw new Error('Prettier formatting failed: ' + (err?.message || err));
    }
  }
  // Fallback: return code unchanged
  return code;
} 
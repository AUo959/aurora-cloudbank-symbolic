/// <reference types="vite/client" />

// Vite's ambient types were never referenced, so `import.meta.env` was unknown
// to tsc — 3 of the 15 TypeScript errors that made `npm run build` fail. The
// triple-slash directive above supplies the built-in members (DEV, PROD, MODE,
// BASE_URL, SSR).
//
// The interface below declares this project's own VITE_-prefixed variables, so
// a typo in one is a compile error rather than a silent `undefined` at runtime.
// Keep it in step with .env.example.

interface ImportMetaEnv {
  /** Base URL of the Aurora API. Falls back to http://localhost:8000. */
  readonly VITE_API_BASE_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

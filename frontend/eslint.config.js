import js from '@eslint/js';
import globals from 'globals';
import tsParser from '@typescript-eslint/parser';
import tsPlugin from '@typescript-eslint/eslint-plugin';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';

// Flat config. ESLint 10 removed support for .eslintrc.* entirely — it does not
// warn, it simply runs with a default configuration, which meant the previous
// .eslintrc.cjs was silently ignored: no TypeScript parser, no plugins, no
// rules. Every .ts/.tsx file then failed to parse ("The keyword 'interface' is
// reserved"), so `npm run lint` reported parse errors instead of lint results
// and no rule had actually been enforced.
//
// This reproduces what .eslintrc.cjs asked for: eslint:recommended,
// @typescript-eslint recommended, react-hooks recommended, plus the two local
// rule overrides.
export default [
  {
    ignores: ['dist/**', 'coverage/**', 'node_modules/**'],
  },

  js.configs.recommended,

  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      parser: tsParser,
      ecmaVersion: 2020,
      sourceType: 'module',
      parserOptions: {
        ecmaFeatures: { jsx: true },
      },
      globals: {
        ...globals.browser,
        ...globals.es2020,
      },
    },
    plugins: {
      '@typescript-eslint': tsPlugin,
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...tsPlugin.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,

      // no-undef is redundant under TypeScript — tsc already resolves every
      // identifier, and the base rule cannot see type-only declarations, so it
      // reports false positives on types and DOM lib globals.
      'no-undef': 'off',
      // The TypeScript-aware version replaces the base rule, which double-reports.
      'no-unused-vars': 'off',

      'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
      '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/no-explicit-any': 'warn',
    },
  },

  // react-refresh/only-export-components guards Fast Refresh, which can only
  // swap a module when everything it exports is a component. Two places export
  // non-components on purpose:
  //
  // router.tsx exports the router object itself — that is the module's whole
  // job, and it is not a Fast Refresh boundary.
  {
    files: ['src/app/router.tsx'],
    rules: { 'react-refresh/only-export-components': 'off' },
  },
  // src/components/ui/* follows the shadcn/ui pattern of co-locating a `cva`
  // variants helper with its component (documented in PROJECT_SUMMARY.md).
  // Allow those by name rather than turning the rule off, so a genuinely
  // stray export in this directory is still reported — extend the list when a
  // new component adds its own variants helper.
  {
    files: ['src/components/ui/**/*.{ts,tsx}'],
    rules: {
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true, allowExportNames: ['buttonVariants'] },
      ],
    },
  },

  // Config files run in Node and are not part of the app's browser bundle.
  {
    files: ['*.config.{js,ts}', 'vite.config.ts', 'vitest.config.ts'],
    languageOptions: {
      parser: tsParser,
      globals: { ...globals.node },
    },
    plugins: { '@typescript-eslint': tsPlugin },
    rules: {
      ...tsPlugin.configs.recommended.rules,
      'no-undef': 'off',
      'no-unused-vars': 'off',
    },
  },
];

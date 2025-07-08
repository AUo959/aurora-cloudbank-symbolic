// Aurora CloudBank - ESLint Configuration (v9+ format)
// Migration from .eslintrc.json to eslint.config.js

export default [
  // Node.js files configuration
  {
    files: ['src/**/*.js', 'scripts/**/*.js', 'tests/**/*.js', '*.js'],
    languageOptions: {
      ecmaVersion: 2021,
      sourceType: 'module',
      globals: {
        // Node.js globals
        require: 'readonly',
        module: 'readonly',
        exports: 'readonly',
        __dirname: 'readonly',
        __filename: 'readonly',
        process: 'readonly',
        Buffer: 'readonly',
        global: 'readonly',
        setInterval: 'readonly',
        setTimeout: 'readonly',
        clearInterval: 'readonly',
        clearTimeout: 'readonly',
        console: 'readonly',
      },
    },
    rules: {
      semi: ['error', 'always'],
      quotes: ['error', 'single'],
      eqeqeq: 'error',
      'no-unused-vars': 'warn', // Changed to warn for dev
      'no-undef': 'error',
      'prefer-const': 'error',
      camelcase: 'warn',
      'no-console': 'warn',
      indent: ['error', 2],
    },
    ignores: ['node_modules/**', '.git/**', 'dist/**', 'build/**', '*.min.js'],
  },
  // Browser files configuration
  {
    files: ['static/**/*.js', 'public/**/*.js'],
    languageOptions: {
      ecmaVersion: 2021,
      sourceType: 'script',
      globals: {
        // Browser globals
        window: 'readonly',
        document: 'readonly',
        navigator: 'readonly',
        console: 'readonly',
        NodeFilter: 'readonly',
        // CommonJS/Node.js compatibility for dual-environment files
        require: 'readonly',
        module: 'readonly',
        exports: 'readonly',
      },
    },
    rules: {
      semi: ['error', 'always'],
      quotes: ['error', 'single'],
      eqeqeq: 'error',
      'no-unused-vars': 'warn',
      'no-undef': 'error',
      'prefer-const': 'error',
      camelcase: 'warn',
      'no-console': 'warn',
      indent: ['error', 2],
    },
  },
];

// Aurora CloudBank - ESLint Configuration (flat config, CommonJS)
// Converted to CommonJS to align with package.json "type": "commonjs"

module.exports = [
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
      // Allow console in development, warn in production
      'no-console': 'off', // Allow console statements in development
      semi: ['error', 'always'],
      quotes: ['error', 'single'],
      eqeqeq: 'error',
      'no-unused-vars': 'warn', // Changed to warn for dev
      'no-undef': 'error',
      'prefer-const': 'error',
      camelcase: 'off', // Disable camelcase for Aurora snake_case conventions
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
        localStorage: 'readonly',
        sessionStorage: 'readonly',
        fetch: 'readonly',
        Blob: 'readonly',
        URL: 'readonly',
        URLSearchParams: 'readonly',
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
      camelcase: 'off', // Disable camelcase for Aurora snake_case conventions
      'no-console': 'off', // Allow console statements in browser files
      indent: ['error', 2],
    },
  },
];

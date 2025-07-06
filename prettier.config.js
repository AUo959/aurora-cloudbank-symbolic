// Aurora CloudBank - Prettier Configuration
module.exports = {
  // Basic formatting
  semi: true,
  singleQuote: true,
  tabWidth: 2,
  useTabs: false,
  trailingComma: 'es5',

  // Line handling
  printWidth: 80,
  endOfLine: 'lf',

  // Bracket spacing
  bracketSpacing: true,
  bracketSameLine: false,

  // Arrow functions
  arrowParens: 'avoid',

  // File types
  overrides: [
    {
      files: '*.md',
      options: {
        printWidth: 100,
        proseWrap: 'always'
      }
    },
    {
      files: '*.json',
      options: {
        tabWidth: 2
      }
    },
    {
      files: '*.yml',
      options: {
        tabWidth: 2
      }
    }
  ]
};

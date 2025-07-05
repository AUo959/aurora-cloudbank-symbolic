module.exports = {
    "env": {
        "browser": true,
        "commonjs": true,
        "es2021": true,
        "node": true
    },
    "extends": [
        "eslint:recommended"
    ],
    "parserOptions": {
        "ecmaVersion": "latest"
    },
    "rules": {
        // Warning level for most issues to prevent CI failures
        "no-unused-vars": "warn",
        "no-console": "off",
        "no-undef": "warn",
        "semi": ["warn", "always"],
        "quotes": ["warn", "single", { "allowTemplateLiterals": true }],
        // Allow empty functions for stubs
        "no-empty-function": "off",
        // Allow console for debugging
        "no-console": "off"
    },
    "ignorePatterns": [
        "node_modules/",
        "dist/",
        "build/",
        "*.min.js",
        "__pycache__/",
        "*.pyc"
    ]
};

module.exports = {
  root: true,
  env: { browser: true, es2022: true },
  ignorePatterns: ['dist/', 'node_modules/', 'coverage/', 'playwright-report/', 'test-results/'],
  extends: ['eslint:recommended', 'plugin:react/recommended', 'plugin:react-hooks/recommended', 'prettier'],
  parserOptions: { ecmaVersion: 'latest', sourceType: 'module', ecmaFeatures: { jsx: true } },
  settings: { react: { version: 'detect' } },
  overrides: [
    {
      files: ['playwright.config.js', 'vite.config.js', '**/*.config.js'],
      env: { node: true },
      globals: { process: 'readonly' }
    },
    {
      files: ['tests/**/*.{js,jsx}'],
      env: { node: true },
      globals: { process: 'readonly' }
    }
  ],
  rules: {
    'react/react-in-jsx-scope': 'off',
    'react/prop-types': 'off'
  }
}

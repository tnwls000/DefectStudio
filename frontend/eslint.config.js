import js from '@eslint/js';
import globals from 'globals';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import tseslint from '@typescript-eslint/eslint-plugin';
import tsParser from '@typescript-eslint/parser';
import eslintConfigPrettier from 'eslint-config-prettier';
import prettier from 'eslint-plugin-prettier';

export default {
  ignores: ['dist'],
  extends: [
    js.configs.recommended,
    'plugin:@typescript-eslint/recommended',
    'plugin:react/recommended', // Add React recommendations
    'plugin:react-hooks/recommended', // React hooks recommendations
    'plugin:prettier/recommended', // Prettier integration
    eslintConfigPrettier
  ],
  files: ['**/*.{ts,tsx}'],
  languageOptions: {
    parser: tsParser,
    ecmaVersion: 2020,
    sourceType: 'module',
    globals: globals.browser
  },
  plugins: {
    'react-hooks': reactHooks,
    'react-refresh': reactRefresh,
    '@typescript-eslint': tseslint,
    prettier
  },
  rules: {
    ...reactHooks.configs.recommended.rules,
    'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
    'prettier/prettier': 'error',
    '@typescript-eslint/no-unused-vars': [
      'warn', // Change to 'warn' to catch unused vars but not fail build
      {
        vars: 'all',
        args: 'after-used',
        ignoreRestSiblings: true,
        varsIgnorePattern: '^_', // Ignore variables that start with an underscore
        argsIgnorePattern: '^_' // Ignore arguments that start with an underscore
      }
    ],
    '@typescript-eslint/explicit-module-boundary-types': 'off', // Turn off if not enforcing explicit return types
    'react/prop-types': 'off' // Turn off PropTypes checking for TS projects
  },
  settings: {
    react: {
      version: 'detect'
    }
  }
};

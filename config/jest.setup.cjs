// Global Jest setup for Aurora CloudBank Symbolic tests.
// Provides deterministic secrets and environment defaults required by legacy modules.
if (!process.env.AES_KEY_256_HEX) {
  process.env.AES_KEY_256_HEX = '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef';
}

if (!process.env.NODE_ENV) {
  process.env.NODE_ENV = 'test';
}

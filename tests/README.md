# Tests Directory

Unit and integration tests for the Aurora Reflective Autonomy System. Add test files as the project grows.


## Running the Node crypto test
The AES round-trip test uses `crypto_refactored.js` with a test key supplied
via the `AES_KEY_256_HEX` environment variable. The test script sets this
variable automatically, so simply run:

```bash
node tests/test_crypto.js
```

If you have `npm` available, you can also run the entire test suite:

```bash
npm test --silent
```

# Mesh Security Notes

## Sanitized Activation Logging

- **Activation confirmation:** Mesh agents now emit activation telemetry that omits the raw activation phrase. The bridge logger receives only a boolean `hasActivationPhrase` flag and a short SHA-256 hash preview.
- **Operator validation:** During activation reviews, confirm that the bridge log payload includes the `activation.activationHashPreview` field. Compare the preview with the expected hash reference in your secured runbook instead of the plaintext phrase.
- **Secret handling:** Because the activation phrase is never serialized to logs, operators must rely on secured key management procedures for full phrase retrieval. Any discrepancy between the preview hash and the expected reference should trigger an immediate incident review.

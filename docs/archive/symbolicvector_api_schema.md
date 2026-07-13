# SymbolicVector API Schema

This document describes the JSON schema for the SymbolicVector data structure and upload response, as used in the Aurora CloudBank Symbolic system.

## SymbolicVector

- **symbol**: string — The symbolic label or name.
- **dim**: integer — The dimensionality of the vector (e.g., 512).
- **vector**: array of integers (values: -1 or 1) — The high-dimensional vector representation.

See: `symbolic_core_symbolicvector.schema.json`

## Upload Response

- **message**: string — Status message.
- **filename**: string — The filename of the uploaded bundle.

See: `symbolic_core_upload_response.schema.json`

---

These schemas should be referenced in REST/WebSocket API documentation and validated in endpoint implementations.

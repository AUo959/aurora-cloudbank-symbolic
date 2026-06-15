# GPT-5 Integration (Aurora CloudBank)

This repo includes a GPT-5 bridge for translating symbolic payloads with DLP anchoring.

## Env configuration
- AURORA_GPT5_API_KEY: required for live calls (omit to use dry-run)
- AURORA_GPT5_MODEL: defaults to `gpt-5`
- AURORA_GPT5_ENDPOINT: defaults to `https://api.openai.com/v1/completions`

Optionally place them in a `.env` file (loaded via python-dotenv).

## FastAPI endpoint
- POST `/gpt5/translate`

Request body:
```json
{
  "operation": "encode_concepts",
  "data": {"concepts": ["alpha"], "dimension": 512},
  "context_tag": "session-1",
  "dry_run": true
}
```

Response includes DLP `dlp_tag_id`, `symbolic_payload`, and `gpt5_result` (mocked in dry-run).

## In-code usage
```python
from src.integrations.gpt5_bridge import GPT5Bridge
bridge = GPT5Bridge()
res = bridge.translate_symbolic(
    operation="encode_concepts",
    data={"concepts": ["alpha"], "dimension": 512},
    context_tag="session-1",
    dry_run=True,
)
```

## Dev server
```bash
make run-api-reload
```
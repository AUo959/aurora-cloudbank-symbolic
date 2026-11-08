# Direct current OpenAI model migration

Published catalog checked 2026-11-08 UTC (November 7 in New York).

The direct OpenAI default is now `gpt-6.1-sol`, OpenAI's current general model
for complex coding and professional work. `gpt-6-astra`, the current flagship
for the most demanding work, can be selected explicitly. Astra is not an
automatic cost escalation in fallback chains. GPT-4o is disabled before its
scheduled 2027-01-14 shutdown; legacy enum names remain for compatibility.
Older unverified GPT-5 profiles remain disabled and are not default routes.

## Published specifications

| Model | Context | Maximum output | Standard input / 1M | Output / 1M |
| --- | ---: | ---: | ---: | ---: |
| gpt-6.1-sol | 1,050,000 | 128,000 | $2 | $10 |
| gpt-6-astra | 1,050,000 | 128,000 | $10 | $50 |

The maximum input is 922,000 tokens. Requests above 272K input tokens have
2x input/cache and 1.5x output prices for the full request. Cache, service tier,
regional, and tool charges are separate. The existing capability price field
records only standard uncached input cost; latency/strength fields are internal
routing estimates, not measured performance claims. The primary API retains
its existing conservative prompt and output bounds.

## Runtime behavior

- The unified adapter calls `AsyncOpenAI.responses.create` directly. It maps
  system prompts to `instructions`, output budget to `max_output_tokens`, and
  tools to flat Responses function definitions. No ChatGPT session token or
  intermediary service is involved.
- Reasoning defaults to `medium`; supported values are `low`, `medium`, `high`,
  `xhigh`, and `max`. Unsupported sampling controls are omitted. Compatibility
  temperature/top_p fields are not sent to these reasoning models.
- Text, token usage, response status, and returned function calls are decoded.
  Tools are returned for the caller to handle; this adapter does not execute
  them or implement a multi-turn tool loop. Incomplete responses are not
  reported as successful. Streaming is explicitly unsupported by AIResponse.
- `store=False` disables provider response storage for these calls.
- An explicit constructor `openai_api_key` takes precedence over the existing
  server-side `OPENAI_API_KEY` environment variable. No key goes to the browser.
- GPT hub defaults (including code and agent routes) and Claude's OpenAI
  fallback use Sol. The `GPT5IntegrationHub` class/module name remains a public
  compatibility surface; historical GPT-5 enable routes are unchanged.

The authenticated, CSRF-protected primary completion endpoint accepts:

```json
{"prompt":"Explain this module", "model_preference":"gpt-6.1-sol", "reasoning_effort":"medium", "max_tokens":2048}
```

Send it to `POST /api/ai/complete` using the existing server authentication.
Omit `model_preference` for normal task routing. General/code tasks start with
Sol; reasoning/math retain Claude-first routing with Sol as the OpenAI fallback.
Use `gpt-6-astra` explicitly for the flagship. Models are visible in
`GET /api/ai/models`; catalog availability does not establish account access.

This migration targets the direct AI-core path. Independent mesh provider
configuration and GitHub Models prompt files are separate integrations.

## Verification boundary

Offline SDK HTTP-contract tests check the actual serialized `/v1/responses`
request, supported parameters, tools, text, usage, and function-call decoding.
Primary API tests check model and reasoning preference forwarding. Catalog,
fallback, hub, and budget tests protect retirement and accounting behavior.
No paid provider inference or account entitlement is claimed by those tests.

## Official sources

- https://developers.openai.com/api/docs/models.md
- https://developers.openai.com/api/docs/models/gpt-6.1-sol.md
- https://developers.openai.com/api/docs/models/gpt-6-astra.md
- https://developers.openai.com/api/docs/guides/latest-model.md
- https://developers.openai.com/api/docs/deprecations

The previous dated catalog receipt is historical; this document supersedes its
GPT-4o routing decision. Source byte digests are recorded below.

- `openai-current-models.md` SHA-256: `658283021cf6d85f3fcc8da66b551c619b168b5a2a39ac19887189e6dc6583f0`

- `gpt-6.1-sol.md` SHA-256: `02dff9ef937bbc97fb24ba7c936269a549563cfb8a49b91a6ba1c1575d2b77c0`

- `gpt-6-astra.md` SHA-256: `a9b79d0f5988c879aea6f4f7adb19743c469ee538d8e19744bdaee13d0c50ae2`

- `openai-latest-guide.md` SHA-256: `746dd4b734bbc9f0221710c3aabaf5ffc4a6e1e03f3538cdbea5bd0a9ec4d828`

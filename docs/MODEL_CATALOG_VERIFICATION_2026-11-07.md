# Published model catalog verification — 2026-11-07

This refresh checks provider documentation, not authenticated Models API access.
It updates the four previously dated 2026-07-25 entries in
`modules/ai_core/unified_ai_interface.py`. `verified_source="pricing-docs"`
means published model, pricing, and lifecycle pages were reviewed on this date.

| Model ID | Published lifecycle | Context / max output | Standard input USD / 1M | Catalog action |
| --- | --- | --- | --- | --- |
| `claude-opus-5` | Active legacy model; retirement no sooner than 2027-07-24 | 1,000,000 / 128,000 | $5 | Retain availability and profile; refresh source/date |
| `claude-sonnet-5` | Active legacy model; retirement no sooner than 2027-06-30 | 1,000,000 / 128,000 | $2 | Correct input price from $3; refresh source/date |
| `gpt-4` | Shut down 2026-10-23 | 8,192 / 8,192 (historical profile) | $30 (historical) | Set `available=False`; correct output ceiling |
| `gpt-4o` | Deprecated; scheduled shutdown 2027-01-14 | 128,000 / 16,384 | $2.50 | Correct price from $5 and output ceiling from 4,096; retain current availability |

GPT-4 remains an enum member for callers that store its name, but the existing
availability gate now refuses to select it, including when explicitly preferred.
Existing available fallback models are used instead. This does not introduce a
new provider or select a newer model on the owner's behalf.
The mathematical fallback chain now uses the already-available GPT-4o entry
in place of GPT-4, preserving fallback when both Anthropic entries fail.

**GPT-4o must be migrated or disabled before 2027-01-14.** That date precedes
the next 90-day freshness deadline. The current boolean catalog does not
automatically enforce future provider retirement dates. Its eventual replacement
should be selected with workload validation, not inferred from this receipt.

## Sources

All pages were retrieved on 2026-11-07. Exact SHA-256 digests below identify the
retrieved source bytes; raw HTML remains scratch evidence outside the repo.

1. [Claude Opus 5 model page](https://platform.claude.com/docs/en/models/opus-5/overview)
   — ID, availability, context, output, standard pricing.
   `6b41006b31ff8e5812cd2c6cc6a8598c8d387621b71d97846fafb16ac0949195`
2. [Claude Sonnet 5 model page](https://platform.claude.com/docs/en/models/sonnet-5/overview)
   — ID, availability, context, output, standard pricing.
   `40b849c9b28aa7a300785df699a70abaaccfa4bfaa2750d406e440c6bcb42bce`
3. [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)
   — corroborates $5/$25 input/output for Opus 5 and $2/$10 for Sonnet 5 per 1M tokens.
   `4e9bb347f204387b18a5d47dafd190768258081813631003d0ae80ec4a65168f`
4. [Anthropic model deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations)
   — active status and earliest retirement commitments.
   `70f746036d7e2420ef55088e11c7407d08961a5e0514e8813e8a2de65bbe57b1`
5. [GPT-4 model page](https://developers.openai.com/api/docs/models/gpt-4.md)
   — shut-down status and historical context/output/pricing.
   `411e079e1a39a591237d123f56a2d42091732a4774da34f509a6c08f1781513c`
6. [GPT-4o model page](https://developers.openai.com/api/docs/models/gpt-4o.md)
   — deprecated status, alias snapshot, context/output, $2.50/$10 standard input/output.
   `22950725c1d75a0098d1c5f046f10c946ffdd41e76d37d14b44e80a6dab8abee`
7. [OpenAI deprecations](https://developers.openai.com/api/docs/deprecations)
   — GPT-4 shutdown on 2026-10-23 and GPT-4o scheduled shutdown on 2027-01-14.
   `a1e94d8079d6bc56b9b3de1021e764ed6130ab68a08ad64c751d35474b6970ba`

## Verification boundaries

The scalar `cost_per_1k_tokens` stores standard uncached input pricing; it is
not a complete billing model. Output pricing, cache rates, tool fees, batch
discounts, and long-context tiers require separate accounting. Strength scores
and latency values remain local estimates, not provider-verified benchmarks.
Optional provider tool integrations are not established by catalog membership.

GPT-5 placeholders remain unavailable and unverified in this scoped change.
No provider API request or paid inference was used for the verification.
Local smoke tests and mocked unit tests do not establish account-specific model
access, live model responses, or production credentials.

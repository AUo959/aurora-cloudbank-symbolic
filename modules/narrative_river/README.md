# Narrative River Adapter

Passive Phase 1 implementation of the Narrative River Adapter specification.

## What is implemented

- strict Pydantic v2 models for `NarrativeRiverFrame` and `SceneRiverDelta`;
- deterministic JSON/YAML serialization;
- stable frame IDs;
- explicit import of prior-scene questions, sediment, and next-scene obligations;
- compact prose-generation prompt contracts;
- advisory checks for self-aware narration, repeated clipped dialogue, generic trailer lines, contrast templates, and RiverCycle terminology bleed.

## What is not implemented

- no API route or background service;
- no simulation mutation;
- no automatic memory persistence;
- no automatic narrative rewriting;
- no CanonRec writes or canon promotion;
- no claim that numeric pressure values represent psychological truth.

## Minimal use

```python
from modules.narrative_river import NarrativeRiverAdapter

adapter = NarrativeRiverAdapter()
frame = adapter.build_frame(
    scene_request=scene_payload,
    canon_snapshot={
        "repository": "AUo959/CanonRec",
        "commit_sha": "<reviewed-sha>",
        "source_files": ["canon/L2/example.md"],
        "authority_status": "mixed",
    },
)

prompt_contract = adapter.render_prompt_contract(frame)
report = adapter.validate_draft(frame, draft_text)
```

Persistence is truthful only when a frame or delta has a durable storage receipt. Git and CanonRec remain the authorities for committed canon.

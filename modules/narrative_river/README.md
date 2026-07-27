# Narrative River Adapter

The Narrative River Adapter now has an explicit operator trigger and durable scene-chain workflow.

## Trigger

Run it from the repository root:

```bash
python -m modules.narrative_river --help
```

Available commands:

```text
build-frame
render-prompt
validate-draft
close-scene
run-scene
status
```

The strongest first-use path is `run-scene`, which performs the complete explicit cycle:

1. load a scene request and canon snapshot;
2. import the approved prior delta, when one exists;
3. build and persist the new frame;
4. render and persist the prose prompt packet;
5. validate the supplied draft and persist the advisory report;
6. validate and persist the approved scene delta;
7. mark that delta as the default continuity input for the next scene.

```bash
python -m modules.narrative_river run-scene \
  --workspace narrative/river \
  --scene-request scene_request.yaml \
  --canon-snapshot canon_snapshot.yaml \
  --axioms narrative_axioms.md \
  --draft chapter_scene.md \
  --delta scene_delta.yaml
```

The command prints a machine-readable JSON receipt containing every generated path.

## Durable layout

```text
narrative/river/
├── frames/
├── deltas/
├── prompt_packets/
├── validation_reports/
└── manifest.json
```

Writes are path-contained beneath the selected workspace and use atomic replacement. The manifest records SHA-256 digests and verifies stored deltas before they are carried into a later scene.

## Review and safety boundaries

- unsupported frame or delta schema versions fail closed;
- questions closed by the prior delta are removed from the next frame;
- resolved sediment is removed before new residue is imported;
- validation remains advisory unless `--fail-on-error` is supplied;
- `run-scene --fail-on-error` persists the frame, prompt, and report but does not close the scene or advance the continuity chain when errors are present;
- no prose is rewritten automatically;
- no simulation state is mutated;
- no CanonRec content is written or promoted;
- the latest delta is imported automatically only through an explicit CLI invocation and can be disabled with `--no-auto-prior`.

## Individual commands

```bash
python -m modules.narrative_river build-frame \
  --scene-request scene_request.yaml \
  --canon-snapshot canon_snapshot.yaml

python -m modules.narrative_river render-prompt \
  --frame narrative/river/frames/SCENE.frame.yaml \
  --axioms narrative_axioms.md

python -m modules.narrative_river validate-draft \
  --frame narrative/river/frames/SCENE.frame.yaml \
  --draft chapter_scene.md

python -m modules.narrative_river close-scene \
  --frame narrative/river/frames/SCENE.frame.yaml \
  --delta scene_delta.yaml

python -m modules.narrative_river status
```

Git and CanonRec remain the authorities for committed canon. The adapter stores narrative working state; it does not promote that state.

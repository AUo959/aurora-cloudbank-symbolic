# Constellation Knowledge Indexes

This directory stores aggregated and cached knowledge indexes from QGIA constellation nodes.

## Files

| File | Description | Updated By |
|------|-------------|------------|
| `aggregated-knowledge-index.json` | Merged index from all QGIA repos | `constellation-knowledge-aggregator` workflow |
| `corpus-knowledge-index.json` | Cached copy from QGIA-CORPUS | Auto-fetched on `qgia.knowledge.updated` event |
| `spine-knowledge-index.json` | Cached copy from QGIA-SPINE | Auto-fetched on `qgia.knowledge.updated` event |

## Schema

All indexes conform to `constellation-contracts/schemas/knowledge-index.schema.json`.

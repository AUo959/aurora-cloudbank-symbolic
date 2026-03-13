# Constellation Contracts

Inter-repository contract definitions for the Aurora Constellation, as defined in the **Aurora Constellation Architecture Proposal v1.0.0**.

## Overview

This directory contains the shared schemas, type definitions, API specifications, and manifest templates that enable the 6 Aurora constellation repos to operate as a unified system.

## Structure

```
constellation-contracts/
  schemas/            # JSON Schema definitions for all inter-repo data structures
  openapi/            # OpenAPI 3.0 spec for the constellation gateway API
  types/
    python/           # Python dataclass type definitions
    typescript/       # TypeScript interface and Zod schema definitions
  manifests/          # Template manifests for each spoke repo
  VERSION             # Current contract version
  CHANGELOG.md        # Change log
```

## Schemas

| Schema | Description |
|--------|-------------|
| `forecast-request.schema.json` | QSFE forecast submission requests |
| `forecast-result.schema.json` | QSFE forecast result payloads |
| `constellation-event.schema.json` | Event bus message envelope |
| `knowledge-index.schema.json` | QGIA knowledge index entries |
| `constellation-health.schema.json` | Node health check responses |
| `manifest.schema.json` | Constellation manifest structure |

## Usage

### Python
```python
from constellation_contracts.types.python.constellation_types import (
    ForecastRequest, ForecastResult, ConstellationEvent,
    validate_against_schema
)
```

### TypeScript
```typescript
import { ForecastRequest, ForecastResult, ConstellationEvent } from './constellation-contracts/types/typescript/constellation-types';
```

## Governance

All contracts are governed under the **Picard_Delta_3** charter with L3 compliance enforcement via Caelion anchoring.

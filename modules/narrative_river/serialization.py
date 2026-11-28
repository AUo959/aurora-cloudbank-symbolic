"""Deterministic JSON and YAML serialization for narrative river artifacts."""

from __future__ import annotations

import json
from typing import TypeVar

import yaml
from pydantic import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


def dumps_json(model: BaseModel) -> str:
    """Serialize a model deterministically as UTF-8 JSON text."""

    return json.dumps(
        model.model_dump(mode="json"),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )


def loads_json(model_type: type[ModelT], payload: str) -> ModelT:
    """Validate JSON text against a model type."""

    return model_type.model_validate_json(payload)


def dumps_yaml(model: BaseModel) -> str:
    """Serialize a model as stable, human-readable YAML."""

    return yaml.safe_dump(
        model.model_dump(mode="json"),
        allow_unicode=True,
        sort_keys=False,
    )


def loads_yaml(model_type: type[ModelT], payload: str) -> ModelT:
    """Validate YAML text against a model type."""

    parsed = yaml.safe_load(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YAML payload must contain a mapping at the document root")
    return model_type.model_validate(parsed)

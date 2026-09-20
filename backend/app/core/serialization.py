"""JSON-safe serialization helpers for API boundaries."""
from decimal import Decimal
from typing import Any


def to_jsonable(data: Any) -> Any:
    """Convert Decimal (and nested containers) to JSON-safe floats.

    Pydantic v2 serializes Decimal to string in mode='json', which breaks
    frontend math (NaN from string division). Call this at the API boundary
    so repositories and services can keep using Decimal.
    """
    if isinstance(data, Decimal):
        return float(data)
    if isinstance(data, dict):
        return {k: to_jsonable(v) for k, v in data.items()}
    if isinstance(data, list):
        return [to_jsonable(v) for v in data]
    return data

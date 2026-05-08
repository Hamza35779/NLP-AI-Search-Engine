"""Small helpers reused across the package."""

from __future__ import annotations

import math
import os
import pickle
from typing import Iterable, Iterator, List, TypeVar


T = TypeVar("T")


def ensure_dir(path: str) -> None:
    """Create the parent directory of `path` if it doesn't exist."""
    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)


def save_pickle(obj: object, path: str) -> None:
    ensure_dir(path)
    with open(path, "wb") as fh:
        pickle.dump(obj, fh, protocol=pickle.HIGHEST_PROTOCOL)


def load_pickle(path: str) -> object:
    with open(path, "rb") as fh:
        return pickle.load(fh)


def chunked(iterable: Iterable[T], size: int) -> Iterator[List[T]]:
    """Yield lists of length `size` from `iterable` (last chunk may be shorter)."""
    if size <= 0:
        raise ValueError("chunk size must be positive")
    chunk: List[T] = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) == size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def cosine(a: dict, b: dict) -> float:
    """Cosine similarity for two sparse term -> weight dicts."""
    if not a or not b:
        return 0.0
    # Iterate over the smaller dict for the dot product.
    if len(a) > len(b):
        a, b = b, a
    dot = 0.0
    for term, weight in a.items():
        other = b.get(term)
        if other is not None:
            dot += weight * other
    if dot == 0.0:
        return 0.0
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def safe_log(x: float) -> float:
    """log() that returns 0 for non-positive inputs instead of crashing."""
    return math.log(x) if x > 0 else 0.0

from pathlib import Path

from fastapi import HTTPException

from .config import STORAGE_ROOT


def resolve_safe(user_path: str | None) -> Path:
    cleaned = (user_path or "").strip().lstrip("/\\")
    candidate = (STORAGE_ROOT / cleaned).resolve()
    if candidate != STORAGE_ROOT and STORAGE_ROOT not in candidate.parents:
        raise HTTPException(status_code=400, detail="Invalid path")
    return candidate

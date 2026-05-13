import shutil
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from ..config import STORAGE_ROOT
from ..safe_path import resolve_safe
from ..schemas import EntryInfo, ListResponse, RenameRequest

router = APIRouter(tags=["folders"])


def _entry_info(p: Path) -> EntryInfo:
    stat = p.stat()
    is_dir = p.is_dir()
    return EntryInfo(
        name=p.name,
        type="folder" if is_dir else "file",
        size=None if is_dir else stat.st_size,
        modified=datetime.fromtimestamp(stat.st_mtime),
    )


def _list_directory(target: Path) -> ListResponse:
    if not target.exists():
        raise HTTPException(status_code=404, detail="Folder not found")
    if not target.is_dir():
        raise HTTPException(status_code=400, detail="Path is not a folder")
    entries = sorted(
        (_entry_info(child) for child in target.iterdir()),
        key=lambda e: (e.type == "file", e.name.lower()),
    )
    rel = "" if target == STORAGE_ROOT else target.relative_to(STORAGE_ROOT).as_posix()
    return ListResponse(path=rel, entries=entries)


@router.get("/folders", response_model=ListResponse)
def list_root() -> ListResponse:
    return _list_directory(STORAGE_ROOT)


@router.get("/folders/{path:path}", response_model=ListResponse)
def list_folder(path: str) -> ListResponse:
    target = resolve_safe(path)
    return _list_directory(target)


@router.post("/folders/{path:path}", status_code=status.HTTP_201_CREATED)
def create_folder(path: str) -> dict:
    target = resolve_safe(path)
    if target == STORAGE_ROOT:
        raise HTTPException(status_code=400, detail="Cannot create root folder")
    if target.exists():
        raise HTTPException(status_code=409, detail="Folder already exists")
    target.mkdir(parents=True, exist_ok=False)
    return {"path": target.relative_to(STORAGE_ROOT).as_posix(), "created": True}


@router.put("/folders/{path:path}")
def rename_folder(path: str, body: RenameRequest) -> dict:
    target = resolve_safe(path)
    if target == STORAGE_ROOT:
        raise HTTPException(status_code=400, detail="Cannot rename root")
    if not target.exists() or not target.is_dir():
        raise HTTPException(status_code=404, detail="Folder not found")
    if "/" in body.new_name or "\\" in body.new_name or body.new_name in (".", ".."):
        raise HTTPException(status_code=400, detail="Invalid new_name")
    destination = (target.parent / body.new_name).resolve()
    if STORAGE_ROOT not in destination.parents and destination != STORAGE_ROOT:
        raise HTTPException(status_code=400, detail="Invalid destination")
    if destination.exists():
        raise HTTPException(status_code=409, detail="Destination already exists")
    target.rename(destination)
    return {"path": destination.relative_to(STORAGE_ROOT).as_posix(), "renamed": True}


@router.delete("/folders/{path:path}")
def delete_folder(path: str, recursive: bool = False) -> dict:
    target = resolve_safe(path)
    if target == STORAGE_ROOT:
        raise HTTPException(status_code=400, detail="Cannot delete root")
    if not target.exists() or not target.is_dir():
        raise HTTPException(status_code=404, detail="Folder not found")
    try:
        if recursive:
            shutil.rmtree(target)
        else:
            target.rmdir()
    except OSError as exc:
        raise HTTPException(
            status_code=409,
            detail="Folder is not empty; use recursive=true",
        ) from exc
    return {"path": target.relative_to(STORAGE_ROOT).as_posix(), "deleted": True}

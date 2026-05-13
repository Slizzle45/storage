import shutil

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from ..config import STORAGE_ROOT
from ..safe_path import resolve_safe

router = APIRouter(tags=["files"])


def _write_upload(upload: UploadFile, destination) -> int:
    with destination.open("wb") as out:
        shutil.copyfileobj(upload.file, out)
    return destination.stat().st_size


@router.post("/files/{path:path}", status_code=status.HTTP_201_CREATED)
def upload_file(path: str, file: UploadFile = File(...)) -> dict:
    target = resolve_safe(path)
    if target == STORAGE_ROOT or target.is_dir():
        raise HTTPException(status_code=400, detail="Invalid file path")
    if not target.parent.exists():
        raise HTTPException(status_code=404, detail="Parent folder not found")
    if target.exists():
        raise HTTPException(status_code=409, detail="File already exists")
    size = _write_upload(file, target)
    return {
        "path": target.relative_to(STORAGE_ROOT).as_posix(),
        "size": size,
        "created": True,
    }


@router.get("/files/{path:path}")
def download_file(path: str) -> FileResponse:
    target = resolve_safe(path)
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=target, filename=target.name)


@router.put("/files/{path:path}")
def replace_file(path: str, file: UploadFile = File(...)) -> dict:
    target = resolve_safe(path)
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    size = _write_upload(file, target)
    return {
        "path": target.relative_to(STORAGE_ROOT).as_posix(),
        "size": size,
        "updated": True,
    }


@router.delete("/files/{path:path}")
def delete_file(path: str) -> dict:
    target = resolve_safe(path)
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    target.unlink()
    return {"path": target.relative_to(STORAGE_ROOT).as_posix(), "deleted": True}

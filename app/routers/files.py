import shutil

from fastapi import APIRouter, File, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse

from ..config import STORAGE_ROOT
from ..safe_path import resolve_safe

router = APIRouter(tags=["files"])


def _write_upload(upload: UploadFile, destination) -> int:
    with destination.open("wb") as out:
        shutil.copyfileobj(upload.file, out)
    return destination.stat().st_size


@router.post("/files/{path:path}", status_code=status.HTTP_201_CREATED)
async def upload_file(path: str, request: Request, file: UploadFile = File(None)) -> dict:
    target = resolve_safe(path)
    if target == STORAGE_ROOT or target.is_dir():
        raise HTTPException(status_code=400, detail="Invalid file path")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise HTTPException(status_code=409, detail="File already exists")

    if file is not None:
        size = _write_upload(file, target)
    else:
        body = await request.body()
        if not body:
            raise HTTPException(status_code=400, detail="No file content provided")
        with target.open("wb") as out:
            out.write(body)
        size = target.stat().st_size

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
async def replace_file(path: str, request: Request, file: UploadFile = File(None)) -> dict:
    target = resolve_safe(path)
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    if file is not None:
        size = _write_upload(file, target)
    else:
        body = await request.body()
        if not body:
            raise HTTPException(status_code=400, detail="No file content provided")
        with target.open("wb") as out:
            out.write(body)
        size = target.stat().st_size

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

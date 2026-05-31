from pathlib import Path

STORAGE_ROOT = (Path(__file__).resolve().parent.parent / "storage").resolve()
HOST = "0.0.0.0"
PORT = 8000

STORAGE_ROOT.mkdir(parents=True, exist_ok=True)

# Storage API

A lightweight RESTful API for file and folder management, built with FastAPI. Supports full CRUD operations on a local storage directory with path traversal protection.

## Features

- **Folder operations** — list, create, rename, delete (with optional recursive delete)
- **File operations** — upload, download, replace, delete
- **Security** — path traversal protection; all paths are resolved within the storage root
- **Interactive docs** — Scalar UI available at `/docs`
- **Health check** — `GET /health`

## Requirements

- Python 3.10+

## Installation

```bash
git clone https://github.com/Slizzle45/storage.git
cd storage
pip install -r requirements.txt
```

## Running

```bash
python run.py
```

The server starts at `http://127.0.0.1:8000` with hot-reload enabled.

## API Reference

Interactive documentation is available at [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs) once the server is running.

### Folders

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/folders` | List root folder contents |
| `GET` | `/folders/{path}` | List a specific folder |
| `POST` | `/folders/{path}` | Create a folder |
| `PUT` | `/folders/{path}` | Rename a folder |
| `DELETE` | `/folders/{path}?recursive=true` | Delete a folder |

### Files

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/files/{path}` | Upload a file |
| `GET` | `/files/{path}` | Download a file |
| `PUT` | `/files/{path}` | Replace a file |
| `DELETE` | `/files/{path}` | Delete a file |

## Project Structure

```
storage-api/
├── app/
│   ├── main.py          # FastAPI app & routes setup
│   ├── config.py        # Storage root path & server config
│   ├── safe_path.py     # Path traversal protection
│   ├── schemas.py       # Pydantic models
│   └── routers/
│       ├── files.py     # File endpoints
│       └── folders.py   # Folder endpoints
├── run.py               # Entry point
├── requirements.txt
└── storage/             # Created automatically at runtime
```

## Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/)
- [Scalar](https://scalar.com/) — API docs UI
- [Pydantic](https://docs.pydantic.dev/)

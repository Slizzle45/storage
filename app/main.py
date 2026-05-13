from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from .routers import files, folders

app = FastAPI(
    title="Storage API",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
)

app.include_router(folders.router)
app.include_router(files.router)


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok"}


@app.get("/docs", include_in_schema=False)
def scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
        default_open_all_tags=True,
        expand_all_model_sections=True,
        expand_all_responses=True,
        hide_models=False,
        persist_auth=True,
        telemetry=False,
    )

"""Gateway (backend for the web front end): static files + one public /api.

    uvicorn trussapp.services.gateway:create_default_app --factory --port 8000
"""
from __future__ import annotations

from pathlib import Path

from fastapi import Body, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ..presentation.i18n import LANGUAGES, Translator
from .clients import ModelClient, SceneClient
from .ports import ModelPort, ScenePort, ServiceError

STATIC_DIR = Path(__file__).parent / "static"


class CreateRequest(BaseModel):
    template: str | None = None
    truss: dict | None = None


def _http_error(exc: ServiceError) -> HTTPException:
    status = exc.status if exc.status in (400, 404, 409, 422) else 502
    return HTTPException(status, exc.detail)


def create_app(model: ModelPort, scene: ScenePort) -> FastAPI:
    app = FastAPI(title="Truss gateway", version="1.0")

    @app.get("/api/health")
    async def health():
        report = {"gateway": "ok"}
        for name, port in (("model", model), ("scene", scene)):
            try:
                report[name] = (await port.health())["status"]
            except ServiceError as exc:
                report[name] = f"unreachable ({exc.detail})"
        return report

    @app.get("/api/languages")
    def languages():
        return LANGUAGES

    @app.get("/api/i18n/{lang}")
    def i18n(lang: str):
        if lang not in LANGUAGES:
            raise HTTPException(404, f"language '{lang}' not found")
        return Translator(lang).bundle()

    @app.get("/api/templates")
    async def templates():
        try:
            return await model.list_templates()
        except ServiceError as exc:
            raise _http_error(exc) from exc

    @app.post("/api/trusses", status_code=201)
    async def create(request: CreateRequest):
        try:
            return await model.create_truss(request.template, request.truss)
        except ServiceError as exc:
            raise _http_error(exc) from exc

    @app.get("/api/trusses/{truss_id}")
    async def get(truss_id: str):
        try:
            return await model.get_truss(truss_id)
        except ServiceError as exc:
            raise _http_error(exc) from exc

    @app.put("/api/trusses/{truss_id}")
    async def save(truss_id: str, body: dict = Body(...)):
        try:
            return await model.save_truss(truss_id, body)
        except ServiceError as exc:
            raise _http_error(exc) from exc

    @app.get("/api/trusses/{truss_id}/view")
    async def view(truss_id: str, mode: str = Query("overview"), target: str | None = None,
                   lang: str = "en"):
        """Everything the page needs to draw one state: scene, tables and status."""
        try:
            stored = await model.get_truss(truss_id)
            rendered = await scene.render(stored["truss"], mode, target, lang)
        except ServiceError as exc:
            raise _http_error(exc) from exc
        return {"id": truss_id, "truss": stored["truss"], **rendered}

    @app.get("/")
    def index():
        return FileResponse(STATIC_DIR / "index.html")

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    return app


def create_default_app() -> FastAPI:
    return create_app(ModelClient(), SceneClient())

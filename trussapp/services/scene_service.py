"""Scene service: turns (truss, selection, language) into drawing primitives and tables.

It asks the solver service for the analysis and holds no state.

    uvicorn trussapp.services.scene_service:create_default_app --factory --port 8003
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from ..core.errors import InvalidSelectionError, UnknownEntityError
from ..core.result_serialization import analysis_from_dict
from ..core.serialization import truss_from_dict
from ..presentation.i18n import Translator
from ..presentation.panels import PanelPresenter
from ..presentation.scene import SceneBuilder
from ..presentation.selection import Selection
from .clients import SolverClient
from .ports import ServiceError, SolverPort


class RenderRequest(BaseModel):
    truss: dict
    mode: str = "overview"
    target: str | None = None
    lang: str = "en"


def create_app(solver: SolverPort, builder: SceneBuilder | None = None,
               panels: PanelPresenter | None = None) -> FastAPI:
    app = FastAPI(title="Truss scene service", version="1.0")
    builder, panels = builder or SceneBuilder(), panels or PanelPresenter()

    @app.get("/health")
    async def health():
        try:
            solver_health = await solver.health()
        except ServiceError as exc:
            return {"service": "scene", "status": "degraded", "solver": exc.detail}
        return {"service": "scene", "status": "ok", "solver": solver_health["status"]}

    @app.post("/render")
    async def render(request: RenderRequest):
        t = Translator(request.lang)
        try:
            selection = Selection.parse(request.mode, request.target)
            analysis_data = await solver.analyze(request.truss)
            truss, analysis = truss_from_dict(request.truss), analysis_from_dict(analysis_data)
            scene = builder.build(truss, analysis, selection, t)
            tables = panels.present(truss, analysis, selection, t)
        except InvalidSelectionError as exc:
            raise HTTPException(409, str(exc)) from exc
        except UnknownEntityError as exc:
            raise HTTPException(404, str(exc)) from exc
        except ServiceError as exc:
            raise HTTPException(502, f"solver service: {exc.detail}") from exc
        status = analysis.status.value
        return {
            "mode": selection.mode.value,
            "target": selection.target_id,
            "status": status,
            "status_text": t(f"status.{status}"),
            "issues": [t.issue(i) for i in analysis.issues],
            "scene": scene.to_dict(),
            "panels": [p.to_dict() for p in tables],
        }

    return app


def create_default_app() -> FastAPI:
    return create_app(SolverClient())

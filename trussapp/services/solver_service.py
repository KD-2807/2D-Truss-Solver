"""Solver service: stateless statics (reactions, member forces, joint/member free bodies).

    uvicorn trussapp.services.solver_service:create_app --factory --port 8002
"""
from __future__ import annotations

from fastapi import Body, FastAPI

from ..core.analysis import TrussAnalysisService
from ..core.result_serialization import analysis_to_dict
from ..core.serialization import truss_from_dict


def create_app(analysis: TrussAnalysisService | None = None) -> FastAPI:
    app = FastAPI(title="Truss solver service", version="1.0")
    service = analysis or TrussAnalysisService()

    @app.get("/health")
    def health():
        return {"service": "solver", "status": "ok"}

    @app.post("/analyze")
    def analyze(truss: dict = Body(...)):
        return analysis_to_dict(service.analyze(truss_from_dict(truss)))

    return app

"""Model service: stores trusses (CRUD), serves the examples, validates input.

    uvicorn trussapp.services.model_service:create_default_app --factory --port 8001
"""
from __future__ import annotations

import json
import os
import threading
import uuid
from abc import ABC, abstractmethod
from pathlib import Path

from fastapi import Body, FastAPI, HTTPException
from pydantic import BaseModel

from ..core.serialization import truss_from_dict, truss_to_dict
from ..core.templates import list_templates, template_dict
from ..core.validation import TrussValidator


class TrussRepository(ABC):
    """Persistence port: stores truss documents (plain dicts) by id."""

    @abstractmethod
    def list_ids(self) -> list: ...

    @abstractmethod
    def get(self, truss_id: str) -> dict | None: ...

    @abstractmethod
    def put(self, truss_id: str, truss: dict) -> None: ...

    @abstractmethod
    def delete(self, truss_id: str) -> bool: ...


class InMemoryTrussRepository(TrussRepository):
    def __init__(self):
        self._data, self._lock = {}, threading.Lock()

    def list_ids(self) -> list:
        with self._lock:
            return list(self._data)

    def get(self, truss_id: str):
        with self._lock:
            return self._data.get(truss_id)

    def put(self, truss_id: str, truss: dict) -> None:
        with self._lock:
            self._data[truss_id] = truss

    def delete(self, truss_id: str) -> bool:
        with self._lock:
            return self._data.pop(truss_id, None) is not None


class JsonFileTrussRepository(TrussRepository):
    """One <id>.json file per truss in a directory."""

    def __init__(self, directory: str | Path):
        self._dir = Path(directory)
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path(self, truss_id: str) -> Path:
        if not truss_id.isalnum():
            raise ValueError("invalid truss id")
        return self._dir / f"{truss_id}.json"

    def list_ids(self) -> list:
        return sorted(p.stem for p in self._dir.glob("*.json"))

    def get(self, truss_id: str):
        path = self._path(truss_id)
        return json.loads(path.read_text("utf-8")) if path.exists() else None

    def put(self, truss_id: str, truss: dict) -> None:
        path = self._path(truss_id)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(truss, indent=2, ensure_ascii=False), "utf-8")
        tmp.replace(path)

    def delete(self, truss_id: str) -> bool:
        path = self._path(truss_id)
        if path.exists():
            path.unlink()
            return True
        return False


class CreateRequest(BaseModel):
    template: str | None = None
    truss: dict | None = None


def _normalize(data: dict) -> dict:
    """Parse + dump: stored documents are always clean and complete."""
    return truss_to_dict(truss_from_dict(data))


def create_app(repository: TrussRepository) -> FastAPI:
    app = FastAPI(title="Truss model service", version="1.0")
    validator = TrussValidator()

    def load_or_404(truss_id: str) -> dict:
        data = repository.get(truss_id)
        if data is None:
            raise HTTPException(404, f"truss '{truss_id}' not found")
        return data

    @app.get("/health")
    def health():
        return {"service": "model", "status": "ok"}

    @app.get("/templates")
    def templates():
        return list_templates()

    @app.get("/templates/{key}")
    def template(key: str):
        try:
            return template_dict(key)
        except KeyError:
            raise HTTPException(404, f"template '{key}' not found") from None

    @app.get("/trusses")
    def list_trusses():
        return repository.list_ids()

    @app.post("/trusses", status_code=201)
    def create(request: CreateRequest):
        if request.template:
            try:
                data = template_dict(request.template)
            except KeyError:
                raise HTTPException(404, f"template '{request.template}' not found") from None
        else:
            data = _normalize(request.truss or {})
        truss_id = uuid.uuid4().hex[:8]
        repository.put(truss_id, data)
        return {"id": truss_id, "truss": data}

    @app.get("/trusses/{truss_id}")
    def get(truss_id: str):
        return {"id": truss_id, "truss": load_or_404(truss_id)}

    @app.put("/trusses/{truss_id}")
    def save(truss_id: str, body: dict = Body(...)):
        load_or_404(truss_id)
        data = _normalize(body)
        repository.put(truss_id, data)
        return {"id": truss_id, "truss": data}

    @app.delete("/trusses/{truss_id}", status_code=204)
    def delete(truss_id: str):
        if not repository.delete(truss_id):
            raise HTTPException(404, f"truss '{truss_id}' not found")

    @app.post("/validate")
    def validate(body: dict = Body(...)):
        issues = validator.validate(truss_from_dict(body))
        return {"valid": not issues, "issues": [{"code": i.code, "params": i.params} for i in issues]}

    return app


def create_default_app() -> FastAPI:
    directory = os.environ.get("TRUSS_DATA_DIR")
    return create_app(JsonFileTrussRepository(directory) if directory else InMemoryTrussRepository())

"""HTTP implementations of the service ports (httpx)."""
from __future__ import annotations

import os

import httpx

from .ports import ServiceError

DEFAULT_URLS = {"model": "http://127.0.0.1:8001", "solver": "http://127.0.0.1:8002",
                "scene": "http://127.0.0.1:8003"}


def service_url(name: str) -> str:
    return os.environ.get(f"{name.upper()}_SERVICE_URL", DEFAULT_URLS[name])


class _HttpClient:
    def __init__(self, base_url: str, client: httpx.AsyncClient | None = None):
        # `client` can be injected (e.g. an ASGI transport in tests)
        self._http = client or httpx.AsyncClient(base_url=base_url, timeout=15.0)

    async def _request(self, method: str, path: str, **kwargs):
        try:
            response = await self._http.request(method, path, **kwargs)
        except httpx.HTTPError as exc:
            raise ServiceError(502, f"service unreachable: {exc}") from exc
        if response.status_code >= 400:
            try:
                detail = response.json().get("detail", response.text)
            except ValueError:
                detail = response.text
            raise ServiceError(response.status_code, str(detail))
        return response.json()

    async def health(self) -> dict:
        return await self._request("GET", "/health")


class ModelClient(_HttpClient):
    def __init__(self, base_url: str | None = None, client: httpx.AsyncClient | None = None):
        super().__init__(base_url or service_url("model"), client)

    async def list_templates(self) -> list:
        return await self._request("GET", "/templates")

    async def create_truss(self, template: str | None = None, truss: dict | None = None) -> dict:
        return await self._request("POST", "/trusses", json={"template": template, "truss": truss})

    async def get_truss(self, truss_id: str) -> dict:
        return await self._request("GET", f"/trusses/{truss_id}")

    async def save_truss(self, truss_id: str, truss: dict) -> dict:
        return await self._request("PUT", f"/trusses/{truss_id}", json=truss)


class SolverClient(_HttpClient):
    def __init__(self, base_url: str | None = None, client: httpx.AsyncClient | None = None):
        super().__init__(base_url or service_url("solver"), client)

    async def analyze(self, truss: dict) -> dict:
        return await self._request("POST", "/analyze", json=truss)


class SceneClient(_HttpClient):
    def __init__(self, base_url: str | None = None, client: httpx.AsyncClient | None = None):
        super().__init__(base_url or service_url("scene"), client)

    async def render(self, truss: dict, mode: str, target: str | None, lang: str) -> dict:
        return await self._request("POST", "/render", json={"truss": truss, "mode": mode,
                                                            "target": target, "lang": lang})

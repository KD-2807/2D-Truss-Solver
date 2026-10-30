"""Service ports (dependency inversion): what a service needs from its neighbours.

The HTTP clients in `clients.py` implement them for real deployments; tests (or a
single-process setup) can plug in any other implementation.
"""
from __future__ import annotations

from typing import Protocol


class ServiceError(Exception):
    """A neighbouring service answered with an error (or could not be reached)."""

    def __init__(self, status: int, detail: str = ""):
        super().__init__(f"{status}: {detail}")
        self.status, self.detail = status, detail


class ModelPort(Protocol):
    async def health(self) -> dict: ...
    async def list_templates(self) -> list: ...
    async def create_truss(self, template: str | None = None, truss: dict | None = None) -> dict: ...
    async def get_truss(self, truss_id: str) -> dict: ...
    async def save_truss(self, truss_id: str, truss: dict) -> dict: ...


class SolverPort(Protocol):
    async def health(self) -> dict: ...
    async def analyze(self, truss: dict) -> dict: ...


class ScenePort(Protocol):
    async def health(self) -> dict: ...
    async def render(self, truss: dict, mode: str, target: str | None, lang: str) -> dict: ...

"""Launcher.

    python main.py desktop            local app (PySide6)
    python main.py web                gateway + model + solver + scene services (4 processes)
    python main.py service <name>     one service: model | solver | scene | gateway

Environment: TRUSS_DATA_DIR (persist trusses as JSON files), *_SERVICE_URL, HOST.
"""
from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys

SERVICES = {  # name -> (uvicorn app factory, port)
    "model": ("trussapp.services.model_service:create_default_app", 8001),
    "solver": ("trussapp.services.solver_service:create_app", 8002),
    "scene": ("trussapp.services.scene_service:create_default_app", 8003),
    "gateway": ("trussapp.services.gateway:create_default_app", 8000),
}


def uvicorn_command(name: str, host: str) -> list:
    factory, port = SERVICES[name]
    return [sys.executable, "-m", "uvicorn", factory, "--factory", "--host", host, "--port", str(port)]


def run_web(host: str) -> int:
    processes = [subprocess.Popen(uvicorn_command(name, host)) for name in SERVICES]
    print(f"Open http://{host}:{SERVICES['gateway'][1]}  (Ctrl+C to stop)")

    def stop(*_):
        for p in processes:
            p.terminate()

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    for p in processes:
        p.wait()
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("desktop")
    web = sub.add_parser("web")
    web.add_argument("--host", default=os.environ.get("HOST", "127.0.0.1"))
    one = sub.add_parser("service")
    one.add_argument("name", choices=SERVICES)
    one.add_argument("--host", default=os.environ.get("HOST", "127.0.0.1"))
    args = parser.parse_args(argv)

    if args.command == "desktop":
        from trussapp.desktop.app import run
        return run()
    if args.command == "web":
        return run_web(args.host)
    return subprocess.call(uvicorn_command(args.name, args.host))


if __name__ == "__main__":
    raise SystemExit(main())

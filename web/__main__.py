"""Entry point: python -m web [--host HOST] [--port PORT] [--reload] [--build]"""
import argparse
import os
import subprocess
import sys


FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
DIST_DIR = os.path.join(FRONTEND_DIR, "dist")


def build_frontend(force: bool = False) -> None:
    if force or not os.path.exists(DIST_DIR):
        print("[absynthe-web] Building frontend …")
        subprocess.run(["npm", "install"], cwd=FRONTEND_DIR, check=True)
        subprocess.run(["npm", "run", "build"], cwd=FRONTEND_DIR, check=True)
        print("[absynthe-web] Frontend ready.")
    else:
        print("[absynthe-web] Frontend already built. Pass --build to force rebuild.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Absynthe Web UI")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Bind port (default 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable hot-reload (dev)")
    parser.add_argument("--build", action="store_true", help="Force frontend rebuild")
    args = parser.parse_args()

    build_frontend(force=args.build)

    import uvicorn

    print(f"[absynthe-web] Serving at http://{args.host}:{args.port}")
    uvicorn.run(
        "web.backend.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()

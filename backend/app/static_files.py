from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import FRONTEND_DIST, SERVE_STATIC


def _file_route(path: Path):
    async def handler():
        return FileResponse(path)

    return handler


def mount_frontend(app: FastAPI) -> bool:
    """Serve built React PWA from FastAPI — one link for phone + PC install."""
    dist = Path(FRONTEND_DIST)
    if not SERVE_STATIC or not dist.is_dir():
        return False

    index_html = dist / "index.html"
    if not index_html.is_file():
        return False

    assets = dist / "assets"
    if assets.is_dir():
        app.mount("/assets", StaticFiles(directory=str(assets)), name="static-assets")

    icons_dir = dist / "icons"
    if icons_dir.is_dir():
        app.mount("/icons", StaticFiles(directory=str(icons_dir)), name="static-icons")

    for name in (
        "manifest.webmanifest",
        "sw.js",
        "registerSW.js",
        "favicon.ico",
        "apple-touch-icon.png",
        "pwa-192x192.png",
        "pwa-512x512.png",
    ):
        p = dist / name
        if p.is_file():
            media = "application/manifest+json" if name.endswith(".webmanifest") else None
            route = app.get(f"/{name}")(_file_route(p))
            if media:
                pass  # FileResponse infers type

    @app.get("/")
    async def spa_root():
        return FileResponse(index_html)

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        if full_path.startswith("api"):
            raise HTTPException(404)
        target = dist / full_path
        if target.is_file():
            return FileResponse(target)
        return FileResponse(index_html)

    return True

import os
from pathlib import Path

APP_PORT = int(os.getenv("PORT", "8080"))
APP_HOST = os.getenv("HOST", "0.0.0.0")

# Frontend build output (single-URL mobile app)
FRONTEND_DIST = Path(
    os.getenv(
        "FRONTEND_DIST",
        str(Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"),
    )
)

_cors = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8080,http://127.0.0.1:8080",
)
CORS_ORIGINS = [o.strip() for o in _cors.split(",") if o.strip()]

# Allow LAN / tunneled installs when enabled (e.g. phone on same Wi-Fi)
if os.getenv("CORS_ALLOW_ALL", "").lower() in ("1", "true", "yes"):
    CORS_ORIGINS = ["*"]

SERVE_STATIC = os.getenv("SERVE_STATIC", "true").lower() in ("1", "true", "yes")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "")

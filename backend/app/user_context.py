"""Per-device user identity via X-User-Id header (syncs phone + PC when same ID)."""

from __future__ import annotations

import re
import uuid

from fastapi import Header, HTTPException

_USER_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{8,64}$")


def normalize_user_id(raw: str | None) -> str:
    if raw and _USER_ID_RE.match(raw.strip()):
        return raw.strip()
    raise HTTPException(
        status_code=400,
        detail="Missing or invalid X-User-Id header. Reload the app to generate a study profile.",
    )


def get_user_id(x_user_id: str | None = Header(default=None, alias="X-User-Id")) -> str:
    return normalize_user_id(x_user_id)


def new_user_id() -> str:
    return uuid.uuid4().hex

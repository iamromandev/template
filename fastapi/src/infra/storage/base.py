"""File-storage base — shared helpers for local / S3 / MinIO adapters.

Concrete subclasses override ``_put_raw``, ``_get_raw``, ``_delete_raw``,
and ``_url_raw``. This base handles content-type inference, path
normalisation, and key validation.
"""

from __future__ import annotations

import mimetypes
import re
from pathlib import PurePosixPath

_ALLOWED_KEY_PATTERN = re.compile(r"^[a-zA-Z0-9_./-]{1,512}$")


class BaseFileStorage:
    """Subclasses implement ``_put_raw`` / ``_get_raw`` / ``_delete_raw``."""

    def __init__(self, base_path: str = "") -> None:
        self._base_path = base_path.strip("/")

    # --- subclass hooks ---
    async def _put_raw(self, key: str, data: bytes, content_type: str) -> str:
        raise NotImplementedError

    async def _get_raw(self, key: str) -> bytes:
        raise NotImplementedError

    async def _delete_raw(self, key: str) -> bool:
        raise NotImplementedError

    async def _url_raw(self, key: str, expires_in: int) -> str:
        raise NotImplementedError

    # --- public API ---
    @staticmethod
    def _normalise_key(key: str) -> str:
        key = PurePosixPath(key).as_posix().lstrip("/")
        if not _ALLOWED_KEY_PATTERN.match(key):
            msg = f"Invalid storage key: {key!r}"
            raise ValueError(msg)
        return key

    @staticmethod
    def _infer_content_type(key: str, default: str = "application/octet-stream") -> str:
        guessed, _ = mimetypes.guess_type(key)
        return guessed or default

    def _full_key(self, key: str) -> str:
        normalised = self._normalise_key(key)
        if self._base_path:
            return f"{self._base_path}/{normalised}"
        return normalised

    async def put(
        self,
        key: str,
        data: bytes,
        content_type: str | None = None,
    ) -> str:
        ct = content_type or self._infer_content_type(key)
        full_key = self._full_key(key)
        return await self._put_raw(full_key, data, ct)

    async def get(self, key: str) -> bytes:
        return await self._get_raw(self._full_key(key))

    async def delete(self, key: str) -> bool:
        return await self._delete_raw(self._full_key(key))

    async def url(self, key: str, expires_in: int = 3600) -> str:
        return await self._url_raw(self._full_key(key), expires_in)


__all__ = ["BaseFileStorage"]

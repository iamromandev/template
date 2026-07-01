"""Local-filesystem implementation of ``BaseFileStorage``.

Stores files under a configurable root directory.  Intended for
development and single-server deployments.  For multi-server or
production, use ``S3FileStorage`` instead.
"""

from __future__ import annotations

from pathlib import Path

from loguru import logger

from src.infra.storage.base import BaseFileStorage


class LocalFileStorage(BaseFileStorage):
    def __init__(self, root: str = "/tmp/storage", base_path: str = "") -> None:
        super().__init__(base_path=base_path)
        self._root = Path(root).resolve()
        self._root.mkdir(parents=True, exist_ok=True)
        logger.info("LocalFileStorage root={}", self._root)

    def _resolve(self, key: str) -> Path:
        full = self._root / key
        full = full.resolve()
        if not str(full).startswith(str(self._root)):
            msg = f"Path traversal detected: {key}"
            raise PermissionError(msg)
        return full

    async def _put_raw(self, key: str, data: bytes, content_type: str) -> str:
        path = self._resolve(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        logger.debug("Stored {} ({}, {} bytes)", key, content_type, len(data))
        return str(path)

    async def _get_raw(self, key: str) -> bytes:
        path = self._resolve(key)
        return path.read_bytes()

    async def _delete_raw(self, key: str) -> bool:
        path = self._resolve(key)
        if path.exists():
            path.unlink()
            logger.debug("Deleted {}", key)
            return True
        return False

    async def _url_raw(self, key: str, expires_in: int) -> str:
        return self._resolve(key).as_uri()


__all__ = ["LocalFileStorage"]

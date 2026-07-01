"""AWS S3 / MinIO implementation of ``BaseFileStorage``.

Requires the ``boto3`` / ``aioboto3`` package (not included by default):

    uv sync --group s3
    # or
    pip install aioboto3

Credentials are resolved from the standard AWS env vars
(``AWS_ACCESS_KEY_ID``, ``AWS_SECRET_ACCESS_KEY``, ``AWS_REGION``)
or from the instance metadata service when running on EC2.
"""

from __future__ import annotations

from loguru import logger

from src.infra.storage.base import BaseFileStorage


class S3FileStorage(BaseFileStorage):
    def __init__(
        self,
        bucket: str,
        base_path: str = "",
        endpoint_url: str | None = None,
        region: str | None = None,
    ) -> None:
        super().__init__(base_path=base_path)
        self._bucket = bucket
        self._endpoint_url = endpoint_url
        self._region = region
        self._client = None

    async def _client(self):
        if self._client is None:
            try:
                import aioboto3
            except ImportError:
                msg = (
                    "aioboto3 is required for S3FileStorage. "
                    "Install it with 'uv sync --group s3' or 'pip install aioboto3'."
                )
                raise ImportError(msg) from None

            session = aioboto3.Session(region_name=self._region)
            self._client = await session.client(
                "s3",
                endpoint_url=self._endpoint_url,
            ).__aenter__()
        return self._client

    async def _put_raw(self, key: str, data: bytes, content_type: str) -> str:
        client = await self._client()
        await client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        logger.debug("S3 put bucket={} key={}", self._bucket, key)
        return key

    async def _get_raw(self, key: str) -> bytes:
        client = await self._client()
        response = await client.get_object(Bucket=self._bucket, Key=key)
        data = await response["Body"].read()
        return data

    async def _delete_raw(self, key: str) -> bool:
        client = await self._client()
        await client.delete_object(Bucket=self._bucket, Key=key)
        logger.debug("S3 delete bucket={} key={}", self._bucket, key)
        return True

    async def _url_raw(self, key: str, expires_in: int) -> str:
        client = await self._client()
        return await client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": key},
            ExpiresIn=expires_in,
        )

    async def close(self) -> None:
        if self._client:
            await self._client.__aexit__(None, None, None)
            self._client = None


__all__ = ["S3FileStorage"]

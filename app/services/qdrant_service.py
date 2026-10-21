from typing import Optional, Dict, Any, List
import os
from qdrant_client import QdrantClient, AsyncQdrantClient
from qdrant_client.http import models as rest_models
from app.core.config import settings
from app.core.logging import logger


class QdrantService:
    def __init__(self):
        self.host = settings.QDRANT_HOST
        self.port = settings.QDRANT_PORT
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.vector_dim = settings.EMBEDDING_DIMENSION
        self.local_path = settings.QDRANT_LOCAL_PATH
        self._async_client: Optional[AsyncQdrantClient] = None
        self._sync_client: Optional[QdrantClient] = None
        self._mode = "remote"  # or "embedded"

    def get_sync_client(self) -> QdrantClient:
        if self._sync_client is None:
            if self._mode == "embedded":
                os.makedirs(self.local_path, exist_ok=True)
                self._sync_client = QdrantClient(path=self.local_path)
            else:
                try:
                    client = QdrantClient(
                        host=self.host,
                        port=self.port,
                        api_key=settings.QDRANT_API_KEY,
                        timeout=3.0,
                    )
                    # Test connection
                    client.get_collections()
                    self._sync_client = client
                except Exception as e:
                    logger.warning(f"Could not connect to remote Qdrant at {self.host}:{self.port} ({e}), falling back to embedded local storage at '{self.local_path}'")
                    self._mode = "embedded"
                    os.makedirs(self.local_path, exist_ok=True)
                    self._sync_client = QdrantClient(path=self.local_path)
        return self._sync_client

    async def get_async_client(self) -> AsyncQdrantClient:
        if self._async_client is None:
            if self._mode == "embedded":
                os.makedirs(self.local_path, exist_ok=True)
                self._async_client = AsyncQdrantClient(path=self.local_path)
            else:
                try:
                    client = AsyncQdrantClient(
                        host=self.host,
                        port=self.port,
                        api_key=settings.QDRANT_API_KEY,
                        timeout=3.0,
                    )
                    await client.get_collections()
                    self._async_client = client
                except Exception as e:
                    logger.warning(f"Could not connect to remote AsyncQdrant at {self.host}:{self.port} ({e}), falling back to embedded local storage at '{self.local_path}'")
                    self._mode = "embedded"
                    os.makedirs(self.local_path, exist_ok=True)
                    self._async_client = AsyncQdrantClient(path=self.local_path)
        return self._async_client

    async def check_health(self) -> Dict[str, Any]:
        """Verify Qdrant server/storage responsiveness and check collection status."""
        try:
            client = await self.get_async_client()
            collections_res = await client.get_collections()
            collections_list = [c.name for c in collections_res.collections]

            return {
                "status": "healthy",
                "mode": self._mode,
                "host": self.host if self._mode == "remote" else "embedded_local",
                "port": self.port if self._mode == "remote" else 0,
                "collections": collections_list,
                "target_collection": self.collection_name,
                "collection_exists": self.collection_name in collections_list,
            }
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return {
                "status": "unhealthy",
                "mode": self._mode,
                "error": str(e),
                "host": self.host,
                "port": self.port,
            }

    async def init_collection(self) -> bool:
        """Create target Qdrant collection if it does not already exist."""
        try:
            client = await self.get_async_client()
            collections_res = await client.get_collections()
            existing = [c.name for c in collections_res.collections]

            if self.collection_name not in existing:
                logger.info(f"Creating Qdrant collection '{self.collection_name}' (dim={self.vector_dim}, cosine distance)...")
                await client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=rest_models.VectorParams(
                        size=self.vector_dim,
                        distance=rest_models.Distance.COSINE
                    )
                )
                logger.info(f"Qdrant collection '{self.collection_name}' created successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant collection '{self.collection_name}': {e}")
            return False


qdrant_service = QdrantService()

from typing import List, Union
import numpy as np
from fastembed import TextEmbedding
from app.core.config import settings
from app.core.logging import logger


class EmbeddingService:
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self._model: TextEmbedding | None = None

    @property
    def model(self) -> TextEmbedding:
        if self._model is None:
            logger.info(f"Loading FastEmbed model '{self.model_name}'...")
            self._model = TextEmbedding(model_name=self.model_name)
            logger.info(f"FastEmbed model '{self.model_name}' initialized.")
        return self._model

    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string into a float vector."""
        generator = self.model.embed([text])
        embedding = list(generator)[0]
        return embedding.tolist() if hasattr(embedding, "tolist") else list(embedding)

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Embed a batch of text strings into float vectors."""
        if not texts:
            return []
        generator = self.model.embed(texts, batch_size=batch_size)
        results = []
        for emb in generator:
            results.append(emb.tolist() if hasattr(emb, "tolist") else list(emb))
        return results


embedding_service = EmbeddingService(model_name="BAAI/bge-small-en-v1.5")

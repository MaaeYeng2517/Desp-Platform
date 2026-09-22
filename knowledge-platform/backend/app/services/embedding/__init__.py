"""
Embedding service for generating token embeddings from text.

Uses ``sentence-transformers`` (a high-level wrapper around
``transformers`` + ``torch``) to produce dense vector representations.
Falls back to a deterministic hash-based embedding when the model
cannot be loaded so the system remains functional in lightweight
environments.
"""
from typing import List, Optional, Union
import hashlib
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Generate embeddings for arbitrary text using a sentence-transformers
    model.

    The model is loaded lazily on first use to avoid import overhead
    when the embedding functionality is not needed.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        vector_size: int = 384,
    ):
        self.model_name = model_name
        self.vector_size = vector_size
        self._model = None

    # ------------------------------------------------------------------
    # Model management
    # ------------------------------------------------------------------

    @property
    def model(self):
        """Lazily load the SentenceTransformer model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(self.model_name)
                logger.info(
                    "Loaded embedding model: %s (dim=%d)",
                    self.model_name,
                    self.vector_size,
                )
            except Exception as exc:
                logger.warning(
                    "Could not load SentenceTransformer (%s); "
                    "using hash-based fallback",
                    exc,
                )
                self._model = None
        return self._model

    @property
    def is_loaded(self) -> bool:
        """Return ``True`` when the transformer model is available."""
        return self._model is not None

    # ------------------------------------------------------------------
    # Embedding generation
    # ------------------------------------------------------------------

    def embed(
        self,
        texts: Union[str, List[str]],
    ) -> List[List[float]]:
        """
        Embed one or more texts.

        Parameters
        ----------
        texts : str | List[str]
            A single string or a list of strings.

        Returns
        -------
        List[List[float]]
            A list of embedding vectors. When *texts* is a single
            string, a one-element list is returned.
        """
        if isinstance(texts, str):
            texts = [texts]

        model = self.model
        if model is not None:
            embeddings = model.encode(
                texts,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
            return embeddings.tolist()

        # Fallback: deterministic hash-based embedding
        logger.debug("Using fallback embedding for %d texts", len(texts))
        return [self._hash_embed(text) for text in texts]

    def embed_query(self, query: str) -> List[float]:
        """Embed a single query string and return the vector."""
        return self.embed(query)[0]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _hash_embed(self, text: str) -> List[float]:
        """Generate a deterministic pseudo-embedding via SHA-256 hashing."""
        hash_val = hashlib.sha256(text.encode()).digest()
        vec: List[float] = []
        for i in range(self.vector_size):
            chunk = hash_val[i % len(hash_val):] + hash_val[: i]
            h = hashlib.md5(chunk).digest()
            vec.append(
                (int.from_bytes(h[:4], "little") / (2**32)) * 2 - 1
            )
        # Normalise
        norm = sum(v * v for v in vec) ** 0.5
        if norm == 0:
            return vec
        return [v / norm for v in vec]

    def dim(self) -> int:
        """Return the dimensionality of the embedding vectors."""
        return self.vector_size


# Global embedding service instance
embedding_service = EmbeddingService()

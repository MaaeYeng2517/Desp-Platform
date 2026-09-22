"""Token-aware chunking service for splitting text into token-bounded chunks."""
from typing import Any, Dict, List, Optional
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class TokenChunker:
    """
    Split text into chunks bounded by token count rather than character count.

    Uses a Hugging Face tokenizer when available; falls back to a
    whitespace + BPE approximation otherwise.
    """

    def __init__(
        self,
        chunk_size: int = 256,
        chunk_overlap: int = 64,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.model_name = model_name
        self._tokenizer = None

    # ------------------------------------------------------------------
    # Tokenizer management
    # ------------------------------------------------------------------

    @property
    def tokenizer(self):
        """Lazily load the tokenizer from the embedding model."""
        if self._tokenizer is None:
            try:
                from transformers import AutoTokenizer

                self._tokenizer = AutoTokenizer.from_pretrained(
                    self.model_name
                )
                logger.info(
                    "Loaded tokenizer: %s", self.model_name
                )
            except Exception as exc:
                logger.warning(
                    "Could not load tokenizer (%s); using fallback", exc
                )
                self._tokenizer = _FallbackTokenizer()
        return self._tokenizer

    # ------------------------------------------------------------------
    # Counting
    # ------------------------------------------------------------------

    def count_tokens(self, text: str) -> int:
        """Return the number of tokens in *text*."""
        return len(self.tokenizer.encode(text, add_special_tokens=False))

    # ------------------------------------------------------------------
    # Chunking
    # ------------------------------------------------------------------

    async def chunk(
        self,
        text: str,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Split *text* into overlapping token-bounded chunks.

        Parameters
        ----------
        text : str
            Raw text to chunk.
        chunk_size : int, optional
            Maximum tokens per chunk (defaults to ``self.chunk_size``).
        chunk_overlap : int, optional
            Overlapping tokens between consecutive chunks.

        Returns
        -------
        List[Dict[str, Any]]
            One dict per chunk with keys: ``content``, ``chunk_index``,
            ``start_token``, ``end_token``, ``token_count``.
        """
        size = chunk_size or self.chunk_size
        overlap = chunk_overlap or self.chunk_overlap

        # Pre-process: split into sentences to avoid breaking mid-sentence
        sentences = _split_sentences(text)

        # Token-encode each sentence once for efficiency
        sentence_tokens = [
            self.tokenizer.encode(s, add_special_tokens=False)
            for s in sentences
        ]

        chunks: List[Dict[str, Any]] = []
        current_tokens: List[int] = []
        current_text_parts: List[str] = []
        chunk_index = 0
        start_token_idx = 0

        for sent_text, sent_tokens in zip(sentences, sentence_tokens):
            if len(current_tokens) + len(sent_tokens) > size and current_tokens:
                # Flush current chunk
                chunks.append(
                    self._make_chunk(
                        chunk_index,
                        current_text_parts,
                        current_tokens,
                        start_token_idx,
                    )
                )

                # Carry over overlap
                carry = current_tokens[-overlap:] if overlap < len(current_tokens) else []
                overlap_text = self.tokenizer.decode(carry) if carry else ""
                current_tokens = carry
                current_text_parts = [overlap_text] if overlap_text else []
                start_token_idx = chunks[-1]["end_token"] - overlap if overlap else chunks[-1]["end_token"]
                chunk_index += 1

            current_tokens.extend(sent_tokens)
            current_text_parts.append(sent_text)

        # Flush remaining
        if current_tokens:
            chunks.append(
                self._make_chunk(
                    chunk_index,
                    current_text_parts,
                    current_tokens,
                    start_token_idx,
                )
            )

        logger.info("Chunked into %d token-bounded chunks", len(chunks))
        return chunks

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _make_chunk(
        self,
        index: int,
        text_parts: List[str],
        tokens: List[int],
        start_token: int,
    ) -> Dict[str, Any]:
        content = " ".join(p.strip() for p in text_parts if p.strip())
        return {
            "content": content,
            "chunk_index": index,
            "start_token": start_token,
            "end_token": start_token + len(tokens),
            "token_count": len(tokens),
            "created_at": datetime.utcnow().isoformat(),
        }


class _FallbackTokenizer:
    """Simple whitespace tokenizer used when transformers is unavailable."""

    def encode(self, text: str, add_special_tokens: bool = False) -> List[int]:
        return [abs(hash(w)) % (2**31 - 1) for w in text.split()]

    def decode(self, tokens: List[int]) -> str:
        return " ".join(str(t) for t in tokens)


def _split_sentences(text: str) -> List[str]:
    """Split text into sentences on punctuation boundaries."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if s.strip()]


# Global chunker instance
token_chunker = TokenChunker()

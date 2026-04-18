"""
Text chunking strategies for RAG-style pipelines and post-processing long model outputs.

Implements character-based sliding windows, sentence windows, and section splits (e.g. Markdown ``##``).
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Pattern, Union


class ChunkingStrategy(ABC):
    """Abstract strategy: split ``text`` into ordered chunks."""

    @abstractmethod
    def chunk(self, text: str) -> List[str]:
        ...


@dataclass
class CharacterChunker(ChunkingStrategy):
    """
    Fixed-size chunks with optional overlap (sliding window over characters).

    Parameters
    ----------
    chunk_size:
        Maximum characters per chunk.
    chunk_overlap:
        Characters shared with the next chunk; must be less than ``chunk_size``.
    """

    chunk_size: int = 150
    chunk_overlap: int = 20

    def __post_init__(self) -> None:
        if self.chunk_size < 1:
            raise ValueError("chunk_size must be >= 1")
        if self.chunk_overlap < 0:
            raise ValueError("chunk_overlap must be >= 0")
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be < chunk_size to make forward progress")

    def chunk(self, text: str) -> List[str]:
        if not text:
            return []
        chunks: List[str] = []
        start_idx = 0
        n = len(text)
        while start_idx < n:
            end_idx = min(start_idx + self.chunk_size, n)
            chunks.append(text[start_idx:end_idx])
            if end_idx >= n:
                break
            start_idx = end_idx - self.chunk_overlap
        return chunks


@dataclass
class SentenceChunker(ChunkingStrategy):
    """
    Group sentences into chunks, with overlap measured in sentence count.

    Sentences are split on punctuation ``.!?`` followed by whitespace (regex).
    """

    max_sentences_per_chunk: int = 5
    overlap_sentences: int = 1

    def __post_init__(self) -> None:
        if self.max_sentences_per_chunk < 1:
            raise ValueError("max_sentences_per_chunk must be >= 1")
        if self.overlap_sentences < 0:
            raise ValueError("overlap_sentences must be >= 0")
        if self.overlap_sentences >= self.max_sentences_per_chunk:
            raise ValueError(
                "overlap_sentences must be < max_sentences_per_chunk to avoid an infinite loop"
            )

    def chunk(self, text: str) -> List[str]:
        if not text.strip():
            return []
        sentences = [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]
        if not sentences:
            return [text.strip()]

        chunks: List[str] = []
        start_idx = 0
        step = self.max_sentences_per_chunk - self.overlap_sentences
        while start_idx < len(sentences):
            end_idx = min(start_idx + self.max_sentences_per_chunk, len(sentences))
            chunks.append(" ".join(sentences[start_idx:end_idx]))
            start_idx += step
        return chunks


@dataclass
class SectionChunker(ChunkingStrategy):
    """
    Split on a heading or section delimiter (default: Markdown ``##`` headings).

    Uses ``re.split``; the delimiter is removed from chunks—prefix headings in downstream
    processing if you need to preserve structure.
    """

    section_pattern: Union[str, Pattern[str]] = r"\n## "

    def chunk(self, text: str) -> List[str]:
        if not text:
            return []
        pattern = self.section_pattern
        parts = re.split(pattern, text)
        return [p for p in parts if p.strip()]


def chunk_text(text: str, strategy: ChunkingStrategy) -> List[str]:
    """Apply a :class:`ChunkingStrategy` to ``text`` (convenience wrapper)."""
    return strategy.chunk(text)

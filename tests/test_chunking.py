"""Unit tests for utils.chunking strategies."""

import unittest

from utils.chunking import (
    CharacterChunker,
    SectionChunker,
    SentenceChunker,
    chunk_text,
)


class TestCharacterChunker(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(CharacterChunker().chunk(""), [])

    def test_short_text_single_chunk(self):
        t = "hello"
        self.assertEqual(CharacterChunker(chunk_size=10, chunk_overlap=2).chunk(t), ["hello"])

    def test_overlap_progress(self):
        c = CharacterChunker(chunk_size=4, chunk_overlap=1)
        out = c.chunk("abcdefghij")
        self.assertTrue(all(len(x) <= 4 for x in out))

    def test_invalid_overlap(self):
        with self.assertRaises(ValueError):
            CharacterChunker(chunk_size=10, chunk_overlap=10)


class TestSentenceChunker(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(SentenceChunker().chunk(""), [])
        self.assertEqual(SentenceChunker().chunk("   "), [])

    def test_single_sentence(self):
        self.assertEqual(
            SentenceChunker(max_sentences_per_chunk=3, overlap_sentences=0).chunk("One. Two."),
            ["One. Two."],
        )

    def test_multiple_chunks(self):
        s = "A. B. C. D. E."
        out = SentenceChunker(max_sentences_per_chunk=2, overlap_sentences=1).chunk(s)
        self.assertGreater(len(out), 1)

    def test_overlap_guard(self):
        with self.assertRaises(ValueError):
            SentenceChunker(max_sentences_per_chunk=2, overlap_sentences=2)


class TestSectionChunker(unittest.TestCase):
    def test_no_sections(self):
        t = "Just prose without headings."
        self.assertEqual(SectionChunker().chunk(t), [t])

    def test_split_on_markdown_h2(self):
        t = "Intro line\n## Section A\nBody A\n## Section B\nBody B"
        parts = SectionChunker().chunk(t)
        self.assertGreaterEqual(len(parts), 2)
        self.assertIn("Section A", "\n".join(parts) or "")
        self.assertIn("Body B", "\n".join(parts))


class TestChunkText(unittest.TestCase):
    def test_wrapper(self):
        strat = CharacterChunker(chunk_size=3, chunk_overlap=0)
        self.assertEqual(chunk_text("abcdef", strat), ["abc", "def"])


if __name__ == "__main__":
    unittest.main()

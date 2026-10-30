"""Unit tests for Phase 1 ingestion utilities and batched Chroma writes."""

import importlib
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from ingestion_utils import sha256_file, stable_document_id


class IngestionUtilityTests(unittest.TestCase):
    def test_sha256_changes_when_content_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "notice.txt"
            path.write_text("first version", encoding="utf-8")
            first = sha256_file(path, chunk_size=3)
            path.write_text("second version", encoding="utf-8")
            second = sha256_file(path, chunk_size=3)
            self.assertNotEqual(first, second)
            self.assertEqual(len(second), 64)

    def test_stable_id_is_repeatable_and_distinguishes_same_stem_paths(self):
        self.assertEqual(stable_document_id("a/notice.pdf"), stable_document_id("a/notice.pdf"))
        self.assertNotEqual(stable_document_id("a/notice.pdf"), stable_document_id("b/notice.pdf"))

    def test_hash_rejects_invalid_chunk_size(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "file.txt"
            path.write_text("data", encoding="utf-8")
            with self.assertRaises(ValueError):
                sha256_file(path, chunk_size=0)


class FakeCollection:
    def __init__(self):
        self.records = {}
        self.upsert_calls = []
        self.deleted_ids = []

    def upsert(self, documents, embeddings, metadatas, ids):
        self.upsert_calls.append(list(ids))
        for document, embedding, metadata, item_id in zip(documents, embeddings, metadatas, ids):
            self.records[item_id] = {"document": document, "embedding": embedding, "metadata": metadata}

    def get(self, where=None, include=None, limit=None):
        path = (where or {}).get("document_path")
        matches = [(item_id, row) for item_id, row in self.records.items()
                   if path is None or row["metadata"].get("document_path") == path]
        if limit is not None:
            matches = matches[:limit]
        result = {"ids": [item_id for item_id, _ in matches]}
        if include and "metadatas" in include:
            result["metadatas"] = [row["metadata"] for _, row in matches]
        return result

    def delete(self, ids):
        self.deleted_ids.extend(ids)
        for item_id in ids:
            self.records.pop(item_id, None)


class FakeClient:
    def __init__(self, collection):
        self._collection = collection

    def get_or_create_collection(self, name):
        return self._collection


class VectorStoreTests(unittest.TestCase):
    def setUp(self):
        self.fake_collection = FakeCollection()
        fake_module = types.SimpleNamespace(
            PersistentClient=lambda path: FakeClient(self.fake_collection)
        )
        self.chromadb_patch = patch.dict(sys.modules, {"chromadb": fake_module})
        self.chromadb_patch.start()
        sys.modules.pop("vector_store", None)
        self.vector_store = importlib.import_module("vector_store")

    def tearDown(self):
        sys.modules.pop("vector_store", None)
        self.chromadb_patch.stop()

    def make_chunk(self, number):
        return {
            "text": f"chunk {number}",
            "chunk_id": f"doc_chunk_{number}",
            "document_id": "doc",
            "document_name": "notice.txt",
            "document_path": "data/documents/notice.txt",
            "document_type": "txt",
            "document_hash": "abc123",
        }

    def test_add_documents_uses_batches_and_upserts(self):
        chunks = [self.make_chunk(i) for i in range(5)]
        embeddings = [[float(i), 0.0] for i in range(5)]
        self.vector_store.add_documents(chunks, embeddings, batch_size=2)
        self.assertEqual([len(batch) for batch in self.fake_collection.upsert_calls], [2, 2, 1])
        self.assertEqual(len(self.fake_collection.records), 5)

    def test_prune_removes_only_stale_chunks_for_same_document(self):
        self.vector_store.add_documents(
            [self.make_chunk(1), self.make_chunk(2)],
            [[1.0], [2.0]],
        )
        removed = self.vector_store.prune_document_chunks(
            "data/documents/notice.txt", ["doc_chunk_2"]
        )
        self.assertEqual(removed, 1)
        self.assertIn("doc_chunk_2", self.fake_collection.records)
        self.assertNotIn("doc_chunk_1", self.fake_collection.records)

    def test_required_metadata_is_checked(self):
        with self.assertRaises(ValueError):
            self.vector_store.add_documents([{"text": "x", "chunk_id": "x"}], [[0.0]])


if __name__ == "__main__":
    unittest.main()

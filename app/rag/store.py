from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection


class VectorStore:
    def __init__(self, persist_path: str, collection_name: str = "documents"):
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection: Collection = self.client.get_or_create_collection(name=collection_name)

    def upsert(
        self,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]],
    ) -> None:
        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def query(
        self,
        query_embedding: list[float],
        top_k: int = 4,
    ) -> dict[str, Any]:
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )
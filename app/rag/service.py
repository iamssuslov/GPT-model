from pathlib import Path

from app.core.config import settings
from app.rag.chunker import TextChunker
from app.rag.embeddings import EmbeddingService
from app.rag.loaders import SUPPORTED_EXTENSIONS, is_supported_file, load_document
from app.rag.store import VectorStore


class RagService:
    def __init__(self):
        self.docs_path = Path(settings.docs_path)
        self.docs_path.mkdir(parents=True, exist_ok=True)

        self.chunker = TextChunker(
            chunk_size=settings.rag_chunk_size,
            chunk_overlap=settings.rag_chunk_overlap,
        )
        self.embedding_service = EmbeddingService(settings.embedding_model)
        self.vector_store = VectorStore(settings.chroma_path)

    def save_uploaded_file(self, filename: str, content: bytes) -> dict:
        safe_name = Path(filename).name
        target_path = self.docs_path / safe_name

        if not is_supported_file(target_path):
            raise ValueError(
                f"Unsupported file type. Allowed: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
            )

        target_path.write_bytes(content)

        return {
            "filename": safe_name,
            "path": str(target_path),
            "size": len(content),
        }

    def list_supported_files(self) -> list[Path]:
        if not self.docs_path.exists():
            return []

        files: list[Path] = []
        for path in self.docs_path.rglob("*"):
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
                files.append(path)

        return sorted(files)

    def index_documents(self) -> dict[str, int]:
        files = self.list_supported_files()

        total_files = 0
        total_chunks = 0

        for file_path in files:
            text = load_document(file_path)
            chunks = self.chunker.split_text(text)
            if not chunks:
                continue

            embeddings = self.embedding_service.embed_documents(chunks)

            ids: list[str] = []
            metadatas: list[dict[str, str | int]] = []

            for idx, _ in enumerate(chunks):
                ids.append(f"{file_path.resolve()}::{idx}")
                metadatas.append(
                    {
                        "source": str(file_path),
                        "filename": file_path.name,
                        "chunk_index": idx,
                    }
                )

            self.vector_store.upsert(
                ids=ids,
                documents=chunks,
                embeddings=embeddings,
                metadatas=metadatas,
            )

            total_files += 1
            total_chunks += len(chunks)

        return {
            "files_indexed": total_files,
            "chunks_indexed": total_chunks,
        }

    def search(self, query: str, top_k: int | None = None) -> list[dict]:
        query_embedding = self.embedding_service.embed_query(query)
        result = self.vector_store.query(
            query_embedding=query_embedding,
            top_k=top_k or settings.rag_top_k,
        )

        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0] if result.get("distances") else []

        items: list[dict] = []
        for idx, document in enumerate(documents):
            metadata = metadatas[idx] if idx < len(metadatas) else {}
            distance = distances[idx] if idx < len(distances) else None

            items.append(
                {
                    "content": document,
                    "metadata": metadata,
                    "distance": distance,
                }
            )

        return items

    def build_rag_context(self, query: str, top_k: int | None = None) -> str | None:
        results = self.search(query, top_k=top_k)
        if not results:
            return None

        parts = [
            "Ниже приведены релевантные фрагменты документов пользователя.",
            "Используй их в ответе, если они действительно помогают.",
            "Если информации недостаточно, не выдумывай.",
            "",
        ]

        for idx, item in enumerate(results, start=1):
            metadata = item["metadata"]
            source = metadata.get("filename", "unknown")
            chunk_index = metadata.get("chunk_index", "?")
            parts.append(f"[Источник {idx}: {source}, chunk {chunk_index}]")
            parts.append(item["content"])
            parts.append("")

        return "\n".join(parts).strip()
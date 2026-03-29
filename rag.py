import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from config import DATA_FOLDER, EMBEDDING_MODEL

class RAGSystem:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.documents = []
        self.index = None
        self._load_or_build_index()

    def _load_or_build_index(self):
        index_path = os.path.join(DATA_FOLDER, "faiss_index.bin")
        docs_path = os.path.join(DATA_FOLDER, "documents.json")

        if os.path.exists(index_path) and os.path.exists(docs_path):
            self.index = faiss.read_index(index_path)
            with open(docs_path, "r") as f:
                self.documents = json.load(f)
        else:
            self._build_index()

    def _build_index(self):
        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)

        self.documents = self._load_documents()
        if not self.documents:
            return

        embeddings = self.model.encode(self.documents, show_progress_bar=True)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings).astype("float32"))

        faiss.write_index(self.index, os.path.join(DATA_FOLDER, "faiss_index.bin"))
        with open(os.path.join(DATA_FOLDER, "documents.json"), "w") as f:
            json.dump(self.documents, f)

    def _load_documents(self):
        docs = []
        if not os.path.exists(DATA_FOLDER):
            return docs

        for filename in os.listdir(DATA_FOLDER):
            if filename.endswith((".txt", ".md", ".json")):
                filepath = os.path.join(DATA_FOLDER, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    if filename.endswith(".json"):
                        try:
                            data = json.loads(content)
                            if isinstance(data, list):
                                docs.extend(data)
                            elif isinstance(data, dict):
                                docs.append(json.dumps(data))
                        except json.JSONDecodeError:
                            docs.append(content)
                    else:
                        chunks = self._chunk_text(content)
                        docs.extend(chunks)
        return docs

    def _chunk_text(self, text, chunk_size=500):
        sentences = text.replace("\n", " ").split(". ")
        chunks = []
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks

    def retrieve(self, query, top_k=5):
        if not self.documents or self.index is None:
            return []

        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(
            np.array(query_embedding).astype("float32"), 
            min(top_k, len(self.documents))
        )

        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                results.append({
                    "content": self.documents[idx],
                    "distance": float(distances[0][i])
                })
        return results

rag_system = RAGSystem()

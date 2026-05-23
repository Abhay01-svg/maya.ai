from duckduckgo_search import DDGS
import importlib
import os
import pickle
import argparse
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except Exception as e:
    SentenceTransformer = None

try:
    import faiss
    _HAS_FAISS = True
except Exception:
    from sklearn.neighbors import NearestNeighbors
    _HAS_FAISS = False


class SimpleRAG:
    """Simple RAG indexer using SentenceTransformers + FAISS (or sklearn fallback).

    Index is persisted as a pickle with keys: 'embeddings' (np.array), 'metadata' (list).
    Metadata items are dicts: {'source': url, 'text': content}.
    """

    def __init__(self, embed_model='all-MiniLM-L6-v2', index_path='rag_index.pkl'):
        if SentenceTransformer is None:
            raise ImportError('Please install sentence-transformers: pip install sentence-transformers')
        self.embedder = SentenceTransformer(embed_model)
        self.index_path = index_path
        self.embeddings = None
        self.metadata = []
        self._index = None

    def save(self):
        payload = {'embeddings': self.embeddings, 'metadata': self.metadata}
        with open(self.index_path, 'wb') as f:
            pickle.dump(payload, f)

    def load(self):
        if not os.path.exists(self.index_path):
            return False
        with open(self.index_path, 'rb') as f:
            payload = pickle.load(f)
        self.embeddings = payload['embeddings']
        self.metadata = payload['metadata']
        self._build_index()
        return True

    def add_documents(self, docs):
        # docs: list of {'source':..., 'text':...}
        texts = [d['text'] for d in docs if d.get('text')]
        if not texts:
            print('No document texts to embed; skipping add_documents.')
            return
        embs = self.embedder.encode(texts, convert_to_numpy=True)
        if self.embeddings is None:
            self.embeddings = embs
            self.metadata = docs.copy()
        else:
            self.embeddings = np.vstack([self.embeddings, embs])
            self.metadata.extend(docs)
        self._build_index()
        self.save()

    def _build_index(self):
        if self.embeddings is None:
            return
        if _HAS_FAISS:
            d = self.embeddings.shape[1]
            self._index = faiss.IndexFlatL2(d)
            self._index.add(self.embeddings.astype(np.float32))
        else:
            self._index = NearestNeighbors(n_neighbors=5, algorithm='auto').fit(self.embeddings)

    def search(self, query, k=5):
        q_emb = self.embedder.encode([query], convert_to_numpy=True)
        if self._index is None:
            return []
        if _HAS_FAISS:
            D, I = self._index.search(q_emb.astype(np.float32), k)
            idxs = I[0]
        else:
            dists, idxs = self._index.kneighbors(q_emb, n_neighbors=min(k, len(self.metadata)))
            idxs = idxs[0]
        results = [self.metadata[i] for i in idxs if i < len(self.metadata)]
        return results


def fetch_ddg(query, max_results=10):
    results = DDGS().text(query, max_results=max_results)
    docs = []
    for r in results:
        text = r.get('body') or ''
        docs.append({'source': r.get('href'), 'text': text})
    return docs


def build_index_from_query(seed_query, index_path='rag_index.pkl'):
    print(f"Fetching search results for seed query: {seed_query}")
    docs = fetch_ddg(seed_query, max_results=20)
    if not docs:
        print('No search results found; using fallback example documents for index build.')
        docs = [
            {'source': 'local:example1', 'text': 'Artificial intelligence (AI) is the simulation of human intelligence processes by machines.'},
            {'source': 'local:example2', 'text': 'Machine learning is a subset of AI that gives systems the ability to automatically learn.'},
            {'source': 'local:example3', 'text': 'Deep learning uses neural networks with many layers to model complex patterns.'}
        ]
    rag = SimpleRAG(index_path=index_path)
    rag.add_documents(docs)
    print(f"Indexed {len(docs)} documents into {index_path}")


def maya_rag_query(query, index_path='rag_index.pkl', k=5, model='llama3.2:3b'):
    rag = SimpleRAG(index_path=index_path)
    if not rag.load():
        # If no index, build a small one from query itself
        print('No index found, fetching and indexing nearby results...')
        docs = fetch_ddg(query, max_results=10)
        rag.add_documents(docs)

    top_docs = rag.search(query, k=k)
    context = ''
    for i, d in enumerate(top_docs, 1):
        context += f"\nSource {i}: {d.get('source')}\n{d.get('text')}\n" 

    system_msg = 'Tum Maya ho. Niche diye gaye internet data se user ko sahi jawab do.'
    user_msg = f"Context:\n{context}\n\nQuestion: {query}"

    try:
        ollama = importlib.import_module('ollama')
    except Exception:
        print('\nWarning: `ollama` package is not installed. Skipping LLM call.')
        print('\n--- Retrieved context (first 500 chars) ---\n')
        print(context[:500])
        return

    response = ollama.chat(model=model, messages=[
        {'role': 'system', 'content': system_msg},
        {'role': 'user', 'content': user_msg}
    ])

    print('\nMaya ka Jawab:\n', response['message']['content'])


def main():
    parser = argparse.ArgumentParser(description='Simple RAG-enabled web reader')
    parser.add_argument('--build', '-b', help='Seed query to build index', default=None)
    parser.add_argument('--query', '-q', help='Ask a question (will use index if present)', default=None)
    parser.add_argument('--index', help='Path to index file', default='rag_index.pkl')
    parser.add_argument('--k', type=int, default=5, help='Number of passages to retrieve')
    args = parser.parse_args()

    if args.build:
        build_index_from_query(args.build, index_path=args.index)
    elif args.query:
        maya_rag_query(args.query, index_path=args.index, k=args.k)
    else:
        q = input('Kya search karun? ')
        maya_rag_query(q, index_path=args.index, k=args.k)


if __name__ == '__main__':
    main()

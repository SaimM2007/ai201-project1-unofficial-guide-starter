import os
import chromadb
from sentence_transformers import SentenceTransformer

DOCS_DIR = "docs"
CHUNK_SIZE = 400
OVERLAP = 50

def load_documents(docs_dir):
    docs = []
    for filename in os.listdir(docs_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(docs_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            docs.append({"filename": filename, "text": text})
    return docs

def clean_text(text):
    import re
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r' +', ' ', text)
    return text.strip()

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start += chunk_size - overlap
    return chunks

def build_vector_store():
    docs = load_documents(DOCS_DIR)
    model = SentenceTransformer("all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path="./chroma_db")
    
    try:
        client.delete_collection("rutgers_profs")
    except:
        pass
    
    collection = client.create_collection("rutgers_profs")
    
    all_chunks = []
    all_ids = []
    all_metadatas = []
    
    chunk_index = 0
    for doc in docs:
        clean = clean_text(doc["text"])
        chunks = chunk_text(clean)
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_ids.append(f"chunk_{chunk_index}")
            all_metadatas.append({
                "source": doc["filename"],
                "chunk_num": i
            })
            chunk_index += 1
    
    print(f"Total chunks: {len(all_chunks)}")
    
    print("\n--- 5 SAMPLE CHUNKS ---")
    for i in range(min(5, len(all_chunks))):
        print(f"\n[{all_metadatas[i]['source']}] chunk {i}:")
        print(all_chunks[i])
        print("-" * 40)
    
    embeddings = model.encode(all_chunks).tolist()
    
    collection.add(
        documents=all_chunks,
        embeddings=embeddings,
        ids=all_ids,
        metadatas=all_metadatas
    )
    
    print(f"\nDone! {len(all_chunks)} chunks stored in ChromaDB.")

if __name__ == "__main__":
    build_vector_store()
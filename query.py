import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("rutgers_profs")
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def retrieve(query, k=5):
    query_embedding = model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )
    chunks = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]
    return chunks, metadatas, distances

def ask(question):
    chunks, metadatas, distances = retrieve(question)
    
    context = ""
    for i, (chunk, meta) in enumerate(zip(chunks, metadatas)):
        context += f"[Source: {meta['source']}]\n{chunk}\n\n"
    
    sources = list(set(meta["source"] for meta in metadatas))
    
    system_prompt = """You are a helpful assistant that answers questions about Rutgers CS professors.
Answer the question using ONLY the information in the provided documents below.
Do not use any outside knowledge.
If the documents don't contain enough information to answer the question, say exactly: "I don't have enough information on that in my documents."
Always cite which document(s) your answer comes from."""

    user_prompt = f"""Documents:
{context}

Question: {question}

Answer based only on the documents above, and cite your sources."""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=1000
    )
    
    answer = response.choices[0].message.content
    
    return {
        "answer": answer,
        "sources": sources,
        "chunks": chunks
    }

if __name__ == "__main__":
    test_queries = [
        "What do students say about Sesh Venugopal's exams?",
        "Is Ana Centeno a good professor for CS111?",
        "How is grading in Hamidi's class?"
    ]
    
    for q in test_queries:
        print(f"\n{'='*60}")
        print(f"QUERY: {q}")
        chunks, metadatas, distances = retrieve(q)
        for i, (chunk, meta, dist) in enumerate(zip(chunks, metadatas, distances)):
            print(f"\n[Result {i+1}] Source: {meta['source']} | Distance: {dist:.4f}")
            print(chunk[:200])
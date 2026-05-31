import os
import json
import chromadb
from chromadb.utils import embedding_functions

def main():
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "chroma_db"))
    print(f"Initializing ChromaDB at {db_path}...")
    client = chromadb.PersistentClient(path=db_path)

    # Use BAAI/bge-small-en-v1.5
    print("Loading BAAI/bge-small-en-v1.5 embedding model...")
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="BAAI/bge-small-en-v1.5")
    
    collection = client.get_or_create_collection(
        name="mutual_funds_faq",
        embedding_function=emb_fn,
        metadata={"hnsw:space": "cosine"}
    )
    
    processed_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "processed"))
    if not os.path.exists(processed_dir):
        print(f"Error: {processed_dir} not found. Run phase 2 first.")
        return

    documents = []
    metadatas = []
    ids = []
    
    fund_folders = [f for f in os.listdir(processed_dir) if os.path.isdir(os.path.join(processed_dir, f))]
    print(f"Found {len(fund_folders)} processed funds.")
    
    for idx, folder in enumerate(fund_folders):
        chunks_path = os.path.join(processed_dir, folder, "chunks.json")
        if not os.path.exists(chunks_path):
            continue
            
        with open(chunks_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                for chunk in data.get("chunks", []):
                    # ChromaDB metadata cannot contain null values.
                    metadata = {
                        "scheme_name": chunk.get("scheme_name", ""),
                        "section": chunk.get("section", ""),
                        "source_url": chunk.get("source_url", ""),
                        "last_updated": chunk.get("last_updated", "")
                    }
                    documents.append(chunk["text"])
                    metadatas.append(metadata)
                    ids.append(chunk["id"])
            except Exception as e:
                print(f"Error reading {chunks_path}: {e}")

    batch_size = 500
    total_chunks = len(documents)
    print(f"Total chunks to embed and ingest: {total_chunks}")
    
    for i in range(0, total_chunks, batch_size):
        end = min(i + batch_size, total_chunks)
        print(f"Ingesting batch {i} to {end}...")
        collection.add(
            documents=documents[i:end],
            metadatas=metadatas[i:end],
            ids=ids[i:end]
        )
        
    print(f"\nPhase 3 Complete! Successfully ingested {total_chunks} chunks into local Vector DB.")
    
    # Verification
    print("\n--- Verifying Database ---")
    query = "What is the expense ratio for HDFC Defence Fund?"
    print(f"Test Query: '{query}'")
    results = collection.query(
        query_texts=[query],
        n_results=1
    )
    if results['documents'] and results['documents'][0]:
        print("Top Result:")
        print(results['documents'][0][0])
    else:
        print("No results found.")

if __name__ == "__main__":
    main()

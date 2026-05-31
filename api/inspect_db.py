import os
import chromadb

def inspect_db():
    # 1. Connect to ChromaDB
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "chroma_db"))
    client = chromadb.PersistentClient(path=db_path)
    
    # 2. Get our collection
    collection = client.get_collection(name="mutual_funds_faq")
    
    # 3. Fetch the first 2 items, INCLUDING their embeddings
    results = collection.get(
        limit=2,
        include=["embeddings", "documents", "metadatas"]
    )
    
    print(f"Total chunks in DB: {collection.count()}\n")
    
    for i in range(len(results["ids"])):
        print(f"--- Chunk ID: {results['ids'][i]} ---")
        print(f"Metadata: {results['metadatas'][i]}")
        print(f"Text: {results['documents'][i]}")
        
        # Embeddings are large lists of floats (384 dimensions)
        embedding = results["embeddings"][i]
        print(f"Embedding Array Length: {len(embedding)} dimensions")
        print(f"Embedding Snippet (first 5 floats): {embedding[:5]}...\n")

if __name__ == "__main__":
    inspect_db()

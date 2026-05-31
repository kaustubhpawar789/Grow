import os
import json
import chromadb

def export_all():
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "chroma_db"))
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_collection(name="mutual_funds_faq")
    
    print("Fetching all 9,006 embeddings from ChromaDB (this might take a few seconds)...")
    
    # By not specifying 'limit', it fetches everything
    results = collection.get(
        include=["embeddings", "documents", "metadatas"]
    )
    
    export_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "all_embeddings_export.json"))
    
    export_data = []
    for i in range(len(results["ids"])):
        export_data.append({
            "id": results["ids"][i],
            "scheme_name": results["metadatas"][i].get("scheme_name", ""),
            "section": results["metadatas"][i].get("section", ""),
            "text": results["documents"][i],
            "embedding": results["embeddings"][i].tolist() if hasattr(results["embeddings"][i], "tolist") else list(results["embeddings"][i])
        })
        
    print(f"Writing data to {export_path}...")
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2)
        
    print("Export Complete! You can now open 'data/all_embeddings_export.json' to see all of them.")

if __name__ == "__main__":
    export_all()

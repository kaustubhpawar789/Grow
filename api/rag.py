import os
import chromadb
from chromadb.utils import embedding_functions
from groq import Groq
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder
from duckduckgo_search import DDGS

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("LLM_API_KEY")
GROQ_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
groq_client = Groq(api_key=GROQ_API_KEY)

# Setup ChromaDB Client
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "chroma_db"))
chroma_client = chromadb.PersistentClient(path=db_path)
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="BAAI/bge-small-en-v1.5")
collection = chroma_client.get_collection(name="mutual_funds_faq", embedding_function=emb_fn)

# --- Phase 5.1: Initialize BM25 for Hybrid Search ---
print("Initializing BM25 for Hybrid Search...")
all_data = collection.get(include=["documents", "metadatas"])
all_documents = all_data["documents"]
all_metadatas = all_data["metadatas"]
all_ids = all_data["ids"]
tokenized_corpus = [doc.lower().split() for doc in all_documents]
bm25_model = BM25Okapi(tokenized_corpus)

# --- Phase 5.2: Initialize Cross-Encoder for Re-ranking ---
print("Loading Cross-Encoder for Re-ranking...")
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def retrieve_context(query: str, top_k: int = 3):
    """Phase 5.1 & 5.2: Hybrid Retrieval + Cross-Encoder Re-ranking"""
    
    # 1. Dense Retrieval (ChromaDB)
    dense_results = collection.query(query_texts=[query], n_results=10)
    dense_docs = dense_results["documents"][0] if dense_results["documents"] else []
    dense_metas = dense_results["metadatas"][0] if dense_results["metadatas"] else []
    
    # 2. Sparse Retrieval (BM25)
    tokenized_query = query.lower().split()
    bm25_scores = bm25_model.get_scores(tokenized_query)
    top_n_sparse_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:10]
    
    sparse_docs = [all_documents[i] for i in top_n_sparse_indices]
    sparse_metas = [all_metadatas[i] for i in top_n_sparse_indices]
    
    # 3. Combine Sets (Deduplicate)
    combined_docs = []
    combined_metas = []
    seen = set()
    
    for doc, meta in zip(dense_docs + sparse_docs, dense_metas + sparse_metas):
        if doc not in seen:
            seen.add(doc)
            combined_docs.append(doc)
            combined_metas.append(meta)
            
    if not combined_docs:
        return "", None
        
    # 4. Phase 5.2: Cross-Encoder Re-ranking
    cross_inp = [[query, doc] for doc in combined_docs]
    cross_scores = cross_encoder.predict(cross_inp)
    
    # Sort by cross-encoder score descending
    ranked_results = sorted(zip(cross_scores, combined_docs, combined_metas), key=lambda x: x[0], reverse=True)
    
    # Select top_k
    top_results = ranked_results[:top_k]
    
    contexts = [res[1] for res in top_results]
    best_metadata = top_results[0][2]
    
    return "\n\n---\n\n".join(contexts), best_metadata

def rewrite_query(query: str, history: list) -> str:
    """Use the LLM to rewrite the query based on conversation history."""
    if not history:
        return query
        
    # Format history for the prompt
    history_str = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in history[-4:]])
    
    prompt = f"""You are a query formulation tool. Given the conversation history, rewrite the user's latest query so that it becomes a fully self-contained search query. If it uses pronouns like "it", "this", or "that fund", replace them with the actual fund name from the history.
Do not answer the query, just output the rewritten query.

History:
{history_str}

User: {query}
Rewritten Query:"""

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=GROQ_MODEL,
            temperature=0.0,
            max_tokens=50,
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception:
        return query

def live_web_search(query: str):
    """Fallback search using DuckDuckGo to find real-time info if ChromaDB misses."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=2))
            if not results:
                return "", None
            
            snippets = [f"Web Source: {r.get('title', '')} - {r.get('body', '')}" for r in results]
            best_url = results[0].get('href', 'Unknown Web Source')
            return "\n\n".join(snippets), best_url
    except Exception as e:
        print(f"Web search failed: {e}")
        return "", None

def generate_answer(query: str, history: list = None) -> str:
    """End-to-end Conversational RAG pipeline with Live Web Fallback."""
    if history is None:
        history = []
        
    # 1. Rewrite query if we have history
    search_query = rewrite_query(query, history) if history else query
    print(f"Original Query: {query} -> Rewritten Search: {search_query}")
    
    # 2. Retrieve Context (Offline)
    context, metadata = retrieve_context(search_query)
    
    # 3. Retrieve Context (Live Web Fallback)
    web_context, web_url = live_web_search(search_query)
    
    combined_context = "OFFLINE DATABASE RESULTS:\n" + (context if context else "None")
    if web_context:
        combined_context += "\n\nLIVE WEB SEARCH RESULTS:\n" + web_context
    
    # 4. Conversational Prompt Engineering
    system_prompt = f"""You are a helpful, professional Mutual Fund FAQ Assistant.
You must answer the user's question using ONLY the provided context.
Rules:
1. Be conversational but concise (maximum 3 sentences).
2. Absolutely no investment advice, opinions, or hallucinations.
3. Prioritize the OFFLINE DATABASE RESULTS. If they do not contain the answer, use the LIVE WEB SEARCH RESULTS.
4. If the user asks about a broad company without specifying a specific fund name, politely ask them to clarify WHICH specific fund they mean.
5. If NEITHER context contains the answer, politely tell the user you couldn't find that specific data. Do not just say 'I do not have that information' - be conversational.

Context:
{combined_context}"""

    # Build messages array with history
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add last few messages for conversational flow (prevent context overflow)
    for msg in history[-4:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
        
    messages.append({"role": "user", "content": query})
    
    # 5. Generate response
    chat_completion = groq_client.chat.completions.create(
        messages=messages,
        model=GROQ_MODEL,
        temperature=0.3, # slight temperature for conversational tone
        max_tokens=200,
    )
    
    answer = chat_completion.choices[0].message.content.strip()
    
    # 6. Conditional formatting — only attach source if the answer is actually about a fund
    # Skip source for greetings, casual chat, clarification requests, and refusals
    skip_phrases = [
        "clarify which specific fund", "couldn't find", "do not have",
        "how can i assist", "how can i help", "hello", "hi there",
        "what would you like to know", "feel free to ask",
        "happy to help", "assist you"
    ]
    answer_lower = answer.lower()
    if any(phrase in answer_lower for phrase in skip_phrases):
        return answer
    
    # Also skip if the original query was a greeting / not fund-related
    greeting_patterns = ["hi", "hello", "hey", "good morning", "good afternoon", 
                         "good evening", "thanks", "thank you", "bye", "ok", "okay"]
    query_lower = query.strip().lower().rstrip("!.,?")
    if query_lower in greeting_patterns:
        return answer
    
    # Determine which source we probably used
    # If offline context had data, we likely used it. Otherwise, we used web.
    if context:
        source_url = metadata.get("source_url", "Unknown Source") if metadata else "Unknown"
        last_updated = metadata.get("last_updated", "Unknown Date") if metadata else "Unknown"
    else:
        source_url = web_url if web_url else "Unknown Web Source"
        last_updated = "Live Web"
    
    return f"{answer}\n\nSource: {source_url}\n*Last updated from sources: {last_updated}*"

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from .guardrails import check_pii, check_advisory_intent
from .rag import generate_answer
from .scheduler import start_scheduler, stop_scheduler, run_full_refresh, get_refresh_history

app = FastAPI(
    title="Mutual Fund FAQ Assistant API", 
    version="1.0.0",
    description="A facts-only RAG assistant API for Mutual Fund queries."
)

# Enable CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str
    history: list = []

class ChatResponse(BaseModel):
    response: str
    is_refusal: bool = False

@app.on_event("startup")
async def startup_event():
    """Phase 7.1: Start the background scheduler on app boot (every 1 hour)."""
    start_scheduler(interval_minutes=60)

@app.on_event("shutdown")
async def shutdown_event():
    """Gracefully stop the scheduler when the app shuts down."""
    stop_scheduler()

@app.get("/health")
async def health_check():
    """Phase 4.1: Basic health endpoint"""
    return {"status": "healthy", "message": "Mutual Fund FAQ API is running smoothly."}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Phase 4 & 5: Main endpoint with Guardrails and Groq RAG Engine"""
    query = request.query
    
    # --- PHASE 4.2: PII FILTER ---
    if check_pii(query):
        raise HTTPException(
            status_code=400, 
            detail="Query rejected: Personal Identifiable Information (PII) detected. Please ensure your query does not contain PAN, Aadhaar, Phone numbers, or Email addresses."
        )
        
    # --- PHASE 4.3: INTENT CLASSIFIER ---
    if check_advisory_intent(query):
        return ChatResponse(
            response="I am a facts-only assistant and cannot provide investment advice, recommendations, or predictions. For guidance on investing, please consult a registered financial advisor or refer to the official AMFI investor education portal (https://www.amfiindia.com).",
            is_refusal=True
        )
        
    # --- PHASE 5: CORE RAG INFERENCE (Groq + ChromaDB) ---
    try:
        final_answer = generate_answer(query, request.history)
        return ChatResponse(response=final_answer, is_refusal=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

# --- PHASE 7.5: Manual Refresh Endpoint ---
@app.post("/refresh")
async def manual_refresh():
    """Phase 7.5: Trigger an on-demand re-scrape and re-index of the knowledge base."""
    try:
        summary = run_full_refresh()
        return {"status": "success", "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refresh failed: {str(e)}")

@app.get("/refresh/history")
async def refresh_history():
    """Phase 7.4: View the log of all past scheduled and manual refresh runs."""
    return {"history": get_refresh_history()}

# Serve frontend statically
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")


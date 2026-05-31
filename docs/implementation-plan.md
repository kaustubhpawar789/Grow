# Phase-Wise Implementation Plan: Mutual Fund FAQ Assistant

This document outlines the step-by-step implementation plan for the Mutual Fund FAQ Assistant, based on the established Context and Architecture.

## Phase 1: Project Setup & Environment Configuration
**Objective:** Set up the foundational structure, repositories, and development environment.
* **1.1. Repository Setup:** Initialize the Git repository with appropriate `.gitignore` (Python/Node).
* **1.2. Environment Setup:** Set up a virtual environment (e.g., `venv` or `poetry`) and define `requirements.txt` / `pyproject.toml` for the backend.
* **1.3. API Keys & Secrets Management:** Configure `.env` files for necessary API keys (OpenAI/Claude/Local LLM, Vector Database).
* **1.4. Basic Scaffolding:** Create directory structures for `data/`, `scraper/`, `api/`, `frontend/`, and `notebooks/`.

## Phase 2: Data Ingestion Pipeline (Offline)
**Objective:** Collect, clean, and process the raw data from official mutual fund sources.
* **2.1. URL Collection:** Finalize the 100-150 public URLs (Factsheets, KIMs, SIDs, AMFI FAQs) as specified in the Corpus Definition.
* **2.2. Web Scraping & PDF Parsing:** 
  * Develop scraping scripts (using `Playwright` or `BeautifulSoup`) for HTML pages.
  * Develop PDF parsing scripts (using `PyPDF2` or `pdfplumber`) for Factsheets and SIDs.
* **2.3. Data Cleaning:** Strip unnecessary headers, footers, HTML tags, and boilerplate text.
* **2.4. Section-Based (Metadata-Aware) Chunking:** Instead of fixed-size text splitting, chunk data logically by distinct sections (Overview, Expense Ratio, Exit Load, Minimum Investment, Fund Management, AUM). Prepend each chunk with its Scheme Name and Section Name to ensure context is perfectly preserved for retrieval.

## Phase 3: Vector Database & Embeddings
**Objective:** Convert textual chunks into vector representations and index them for rapid retrieval.
* **3.1. Embedding Generation:** Integrate the free, open-source `BAAI/bge-small-en-v1.5` model via `sentence-transformers` to rapidly convert the text chunks locally, completely avoiding paid APIs.
* **3.2. Vector Database Setup:** Setup a 100% free and local Vector Database (e.g., `ChromaDB` or `Qdrant-Local`) that runs directly in the Python environment without cloud sign-ups, network latency, or API keys.
* **3.3. Data Ingestion:** Upload the embeddings alongside crucial metadata (Source URL, Scheme name, Section name) into the local Vector Database.
* **3.4. Verification:** Query the VDB directly to verify that semantic searches return the expected chunks.

## Phase 4: Guardrails & API Layer (Online)
**Objective:** Implement the security, privacy, and intent-filtering mechanisms before queries hit the LLM.
* **4.1. FastAPI Setup:** Initialize the async backend service with basic endpoints (`/chat`, `/health`).
* **4.2. PII Filter Implementation:** Integrate Regex and NLP-based redaction (e.g., Microsoft Presidio) to block PAN, Aadhaar, OTPs, and contact details from incoming queries.
* **4.3. Intent Classifier (Refusal Handler):** Implement a zero-shot classifier or lightweight LLM routing to detect subjective/advisory questions ("Should I invest?") and immediately return the standard polite refusal.

## Phase 5: Core RAG Inference Engine
**Objective:** Build the retrieval, prompt construction, and response generation logic.
* **5.1. Hybrid Retrieval:** Implement hybrid search logic (Dense Vector Search + BM25) to query the Vector Database accurately for both semantic concepts and exact keywords (like scheme codes).
* **5.2. Re-ranking (Optional):** Integrate a Cross-Encoder to re-rank the retrieved chunks and pick the absolute best context.
* **5.3. Prompt Engineering:** Develop the strict system prompt that enforces:
  * Maximum 3 sentences.
  * Absolute reliance on retrieved context (no hallucinations).
  * Inclusion of the required Source Link and the footer ("Last updated from sources: <date>").
* **5.4. LLM Integration (Groq):** Connect the engineered prompt and retrieved context to the **Groq API** (using models like `Llama3-8b-8192` or `Mixtral-8x7b`) to generate the final response with near-instant inference speed.

## Phase 6: Frontend Development
**Objective:** Create the minimal, user-friendly interface.
* **6.1. Framework Setup:** Initialize a lightweight frontend app (React, Next.js, or simple HTML/Vanilla JS).
* **6.2. UI Components:**
  * Welcome screen and highly visible Disclaimer ("Facts-only. No investment advice.").
  * 3 predefined example prompts for immediate user engagement.
  * Chat interface (input box, message bubbles).
* **6.3. API Integration:** Connect the frontend to the FastAPI `/chat` endpoint.

## Phase 7: Scheduled Data Refresh Pipeline
**Objective:** Automate periodic re-scraping and re-indexing to keep the ChromaDB knowledge base up to date with the latest official data.
* **7.1. Scheduler Setup:** Integrate a lightweight Python scheduler (e.g., `APScheduler` or `schedule`) into the backend to trigger the data ingestion pipeline on a configurable interval (e.g., weekly).
* **7.2. Re-Scraping Logic:** Re-run the scraper scripts from Phase 2 against the full URL corpus to fetch the latest content from official AMC/AMFI sources.
* **7.3. Incremental Re-Indexing:** Compare newly scraped content against existing ChromaDB chunks. Update only changed/new chunks to avoid redundant embedding computation.
* **7.4. Logging & Notifications:** Log each scheduled run with timestamp, number of chunks updated, and any errors encountered. Optionally send a summary notification.
* **7.5. Manual Trigger Endpoint:** Expose a `/refresh` API endpoint to allow on-demand re-indexing without waiting for the next scheduled run.

## Phase 8: Testing, Evaluation, & Deployment
**Objective:** Ensure factual accuracy, strict compliance, and prepare for production.
* **8.1. Retrieval Evaluation:** Test the retriever using a curated set of 50-100 factual queries to ensure the correct context is pulled.
* **8.2. Guardrail Testing:** Attempt to bypass the system with PII queries and advisory requests ("Which fund is best?") to ensure strict refusal rates.
* **8.3. End-to-End Testing:** Verify that answers are strictly within the 3-sentence limit, include the exact citation link, and do not hallucinate.
* **8.4. Deployment:** Containerize the application using Docker and deploy the FastAPI backend and frontend to a cloud provider (e.g., AWS, GCP, Vercel, or Render).


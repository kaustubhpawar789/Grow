"""
Phase 7: Scheduled Data Refresh Pipeline
Automates periodic re-scraping and re-indexing to keep ChromaDB up to date.
"""

import os
import sys
import json
import asyncio
import hashlib
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Configure logging
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "logs"))
os.makedirs(LOG_DIR, exist_ok=True)

log_file = os.path.join(LOG_DIR, "refresh.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("scheduler")


def compute_chunk_hash(text: str) -> str:
    """Hash a chunk's text content to detect changes."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run_scraper():
    """Phase 7.2: Re-run the scraper pipeline from Phase 2."""
    logger.info("Starting re-scraping of URL corpus...")
    scraper_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scraper"))
    sys.path.insert(0, scraper_dir)

    try:
        from url_collection import extract_urls
        from html_scraper import scrape_urls
        from pdf_parser import parse_pdfs
        from data_cleaner import clean_html_files

        extract_urls()
        asyncio.run(scrape_urls())
        parse_pdfs()
        clean_html_files()
        logger.info("Re-scraping completed successfully.")
        return True
    except Exception as e:
        logger.error(f"Re-scraping failed: {e}")
        return False
    finally:
        sys.path.pop(0)


def run_incremental_ingest():
    """Phase 7.3: Incremental re-indexing — only update changed/new chunks."""
    import chromadb
    from chromadb.utils import embedding_functions

    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "chroma_db"))
    processed_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "processed"))

    if not os.path.exists(processed_dir):
        logger.error(f"Processed directory not found: {processed_dir}")
        return {"added": 0, "updated": 0, "skipped": 0, "errors": 0}

    logger.info(f"Initializing ChromaDB at {db_path}...")
    client = chromadb.PersistentClient(path=db_path)
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="BAAI/bge-small-en-v1.5")
    collection = client.get_or_create_collection(
        name="mutual_funds_faq",
        embedding_function=emb_fn,
        metadata={"hnsw:space": "cosine"}
    )

    # Load all existing IDs and their hashes from the collection
    existing_ids = set()
    try:
        existing_data = collection.get(include=["documents"])
        if existing_data and existing_data["ids"]:
            existing_ids = set(existing_data["ids"])
            # Build hash map of existing docs
            existing_hashes = {}
            for i, doc_id in enumerate(existing_data["ids"]):
                existing_hashes[doc_id] = compute_chunk_hash(existing_data["documents"][i])
    except Exception:
        existing_hashes = {}

    stats = {"added": 0, "updated": 0, "skipped": 0, "errors": 0}

    fund_folders = [f for f in os.listdir(processed_dir) if os.path.isdir(os.path.join(processed_dir, f))]
    logger.info(f"Found {len(fund_folders)} processed fund folders.")

    for folder in fund_folders:
        chunks_path = os.path.join(processed_dir, folder, "chunks.json")
        if not os.path.exists(chunks_path):
            continue

        try:
            with open(chunks_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            for chunk in data.get("chunks", []):
                chunk_id = chunk["id"]
                chunk_text = chunk["text"]
                new_hash = compute_chunk_hash(chunk_text)
                metadata = {
                    "scheme_name": chunk.get("scheme_name", ""),
                    "section": chunk.get("section", ""),
                    "source_url": chunk.get("source_url", ""),
                    "last_updated": chunk.get("last_updated", "")
                }

                if chunk_id in existing_ids:
                    old_hash = existing_hashes.get(chunk_id)
                    if old_hash == new_hash:
                        stats["skipped"] += 1
                        continue
                    else:
                        # Content changed — update it
                        collection.update(
                            ids=[chunk_id],
                            documents=[chunk_text],
                            metadatas=[metadata]
                        )
                        stats["updated"] += 1
                else:
                    # New chunk — add it
                    collection.add(
                        ids=[chunk_id],
                        documents=[chunk_text],
                        metadatas=[metadata]
                    )
                    stats["added"] += 1

        except Exception as e:
            logger.error(f"Error processing {chunks_path}: {e}")
            stats["errors"] += 1

    logger.info(f"Incremental ingest complete: {stats}")
    return stats


def run_full_refresh():
    """Phase 7.1 + 7.2 + 7.3: Full scheduled refresh pipeline."""
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info(f"SCHEDULED REFRESH STARTED at {start_time.isoformat()}")
    logger.info("=" * 60)

    # Step 1: Re-scrape
    scrape_ok = run_scraper()

    # Step 2: Incremental re-index
    if scrape_ok:
        stats = run_incremental_ingest()
    else:
        stats = {"added": 0, "updated": 0, "skipped": 0, "errors": 1}
        logger.warning("Skipping re-indexing because scraping failed.")

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Step 3: Log summary
    summary = {
        "timestamp": end_time.isoformat(),
        "duration_seconds": round(duration, 2),
        "scrape_success": scrape_ok,
        "chunks_added": stats["added"],
        "chunks_updated": stats["updated"],
        "chunks_skipped": stats["skipped"],
        "errors": stats["errors"]
    }

    # Append to a JSON log for easy querying
    summary_log = os.path.join(LOG_DIR, "refresh_history.json")
    history = []
    if os.path.exists(summary_log):
        try:
            with open(summary_log, "r") as f:
                history = json.load(f)
        except Exception:
            history = []
    history.append(summary)
    with open(summary_log, "w") as f:
        json.dump(history, f, indent=2)

    logger.info(f"REFRESH COMPLETE in {duration:.1f}s | Added: {stats['added']} | Updated: {stats['updated']} | Skipped: {stats['skipped']} | Errors: {stats['errors']}")
    logger.info("=" * 60)

    return summary


# --- Scheduler instance (Phase 7.1) ---
scheduler = BackgroundScheduler()


def start_scheduler(interval_minutes: int = 15):
    """Start the background scheduler to run every N minutes."""
    scheduler.add_job(
        run_full_refresh,
        trigger=IntervalTrigger(minutes=interval_minutes),
        id="data_refresh_job",
        name=f"Data Refresh (every {interval_minutes} min)",
        replace_existing=True
    )
    scheduler.start()
    logger.info(f"Background scheduler started. Refresh interval: every {interval_minutes} minute(s).")


def stop_scheduler():
    """Gracefully stop the background scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Background scheduler stopped.")


def get_refresh_history():
    """Return the log of all past refresh runs."""
    summary_log = os.path.join(LOG_DIR, "refresh_history.json")
    if os.path.exists(summary_log):
        with open(summary_log, "r") as f:
            return json.load(f)
    return []

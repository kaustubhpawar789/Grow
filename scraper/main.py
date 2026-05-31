import asyncio
from url_collection import extract_urls
from html_scraper import scrape_urls
from pdf_parser import parse_pdfs
from data_cleaner import clean_html_files

async def main():
    print("Starting Data Ingestion Pipeline (Phase 2.1 - 2.3)...")
    
    print("\n--- Step 1: URL Collection ---")
    extract_urls()
    
    print("\n--- Step 2: HTML Scraping ---")
    await scrape_urls()
    
    print("\n--- Step 3: PDF Parsing ---")
    parse_pdfs()
    
    print("\n--- Step 4: Data Cleaning ---")
    clean_html_files()
    
    print("\nPipeline completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import os
import random
from playwright.async_api import async_playwright

async def scrape_urls(urls_file="data/raw/urls.txt", output_dir="data/raw/html/"):
    """Scrape HTML content using Playwright to handle dynamic rendering."""
    print(f"Reading URLs from {urls_file}...")
    try:
        with open(urls_file, "r") as f:
            urls = f.read().splitlines()
    except FileNotFoundError:
        print(f"Error: {urls_file} not found. Run url_collection.py first.")
        return

    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Starting Playwright to scrape {len(urls)} URLs...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = await context.new_page()

        for i, url in enumerate(urls, 1):
            if not url.strip():
                continue
                
            # Generate a safe filename from the URL slug
            slug = url.strip().split('/')[-1]
            if not slug:
                slug = f"page_{i}"
            filename = os.path.join(output_dir, f"{slug}.html")
            
            # Skip if already scraped to allow resuming
            if os.path.exists(filename):
                print(f"[{i}/{len(urls)}] Skipping already scraped: {slug}")
                continue

            print(f"[{i}/{len(urls)}] Scraping: {url}")
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                # Small wait to ensure React hydration completes
                await page.wait_for_timeout(2000)
                
                content = await page.content()
                
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(content)
                
                # Add random delay to avoid rate limiting
                await asyncio.sleep(random.uniform(1.0, 3.0))
            except Exception as e:
                print(f"[{i}/{len(urls)}] Failed to scrape {url}: {e}")
                
        await browser.close()
        print("Scraping completed.")

if __name__ == "__main__":
    asyncio.run(scrape_urls())

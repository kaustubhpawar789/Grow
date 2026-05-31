import asyncio
import os
import random
from playwright.async_api import async_playwright

async def scrape_single_url(url, i, total, output_dir, context, sem):
    slug = url.strip().split('/')[-1]
    if not slug:
        slug = f"page_{i}"
    filename = os.path.join(output_dir, f"{slug}.html")
    
    if os.path.exists(filename):
        print(f"[{i}/{total}] Skipping already scraped: {slug}")
        return

    async with sem:
        print(f"[{i}/{total}] Scraping: {url}")
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            # Small wait to ensure React hydration completes
            await page.wait_for_timeout(2000)
            
            content = await page.content()
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
                
            # Add random delay to avoid rate limiting
            await asyncio.sleep(random.uniform(0.5, 1.5))
        except Exception as e:
            print(f"[{i}/{total}] Failed to scrape {url}: {e}")
        finally:
            await page.close()

async def scrape_urls(urls_file="data/raw/urls.txt", output_dir="data/raw/html/"):
    """Scrape HTML content using Playwright to handle dynamic rendering."""
    print(f"Reading URLs from {urls_file}...")
    try:
        with open(urls_file, "r") as f:
            urls = [u for u in f.read().splitlines() if u.strip()]
    except FileNotFoundError:
        print(f"Error: {urls_file} not found. Run url_collection.py first.")
        return

    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Starting Playwright to scrape {len(urls)} URLs concurrently...")
    
    # Process up to 3 URLs simultaneously to avoid OOM crashes on Render
    sem = asyncio.Semaphore(3)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        
        tasks = [scrape_single_url(url, i, len(urls), output_dir, context, sem) for i, url in enumerate(urls, 1)]
        await asyncio.gather(*tasks)
                
        await browser.close()
        print("Scraping completed.")

if __name__ == "__main__":
    asyncio.run(scrape_urls())

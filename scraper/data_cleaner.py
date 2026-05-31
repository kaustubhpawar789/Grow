import os
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup
import shutil

def estimate_tokens(text):
    return len(text.split())

def extract_metadata_from_text(clean_text, slug):
    # Default mocked values
    sections = {
        "overview": clean_text[:500] if len(clean_text) > 500 else clean_text,
        "expense_ratio": "Expense Ratio data not found.",
        "exit_load": "Exit Load data not found.",
        "minimum_investment": "Minimum Investment data not found.",
        "fund_management": "Fund Management data not found.",
        "aum": "AUM data not found."
    }

    # Attempt to extract actual values using Regex
    er_match = re.search(r'Expense Ratio.*?is\s+([0-9\.]+%?)', clean_text, re.IGNORECASE)
    if er_match:
        sections['expense_ratio'] = f"Expense Ratio: {er_match.group(1)}"

    aum_match = re.search(r'AUM.*?is\s+(₹[0-9,\.]+Cr)', clean_text, re.IGNORECASE)
    if aum_match:
        sections['aum'] = f"AUM: {aum_match.group(1)}"

    exit_load_match = re.search(r'(Exit Load.*?\.)', clean_text, re.IGNORECASE)
    if exit_load_match:
        sections['exit_load'] = exit_load_match.group(1)

    min_inv_match = re.search(r'(Minimum.*?(?:SIP|Lumpsum).*?₹[0-9,]+)', clean_text, re.IGNORECASE)
    if min_inv_match:
        sections['minimum_investment'] = min_inv_match.group(1)

    return sections

def clean_html_files(input_dir="data/raw/html/", output_dir="data/processed/"):
    print(f"Structuring data from {input_dir} to {output_dir}...")
    if not os.path.exists(input_dir):
        print(f"Error: Directory {input_dir} does not exist.")
        return

    os.makedirs(output_dir, exist_ok=True)
    files = [f for f in os.listdir(input_dir) if f.endswith(".html")]

    processed_count = 0
    skipped_count = 0

    for filename in files:
        input_path = os.path.join(input_dir, filename)
        slug = filename.replace(".html", "")
        
        with open(input_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, "html.parser")
        text = soup.get_text(separator=' ')
        
        # Check for 404 page
        if "404! Page Not Found" in text:
            # Skip invalid or 404 pages (Groww valid pages are typically > 200KB)
            print(f"Skipping {slug} (404 or Invalid Page)")
            skipped_count += 1
            continue

        # Clean noise
        for script_or_style in soup(["script", "style", "nav", "footer", "aside"]):
            script_or_style.decompose()

        clean_text = ' '.join(soup.get_text(separator=' ').split())
        
        scheme_name = slug.replace("-", " ").title()
        source_url = f"https://groww.in/mutual-funds/{slug}"
        today = datetime.now().strftime("%Y-%m-%d")
        
        scheme_dir = os.path.join(output_dir, slug)
        os.makedirs(scheme_dir, exist_ok=True)

        # 1. Save cleaned.txt
        with open(os.path.join(scheme_dir, "cleaned.txt"), "w", encoding="utf-8") as f:
            f.write(clean_text)

        # 2. Extract sections
        sections = extract_metadata_from_text(clean_text, slug)

        # 3. Save sections.json
        with open(os.path.join(scheme_dir, "sections.json"), "w", encoding="utf-8") as f:
            json.dump(sections, f, indent=4)

        # 4. Generate chunks.json
        chunks_list = []
        for i, (sec_name, sec_text) in enumerate(sections.items()):
            chunk_text = f"Scheme: {scheme_name}\nSection: {sec_name}\nSource: {source_url}\n{sec_text}"
            chunk = {
                "id": f"{slug}#{sec_name}#{i}",
                "text": chunk_text,
                "scheme_name": scheme_name,
                "source_url": source_url,
                "section": sec_name,
                "last_updated": today,
                "manager_name": None,
                "token_estimate": estimate_tokens(chunk_text)
            }
            chunks_list.append(chunk)

        chunks_data = {
            "slug": slug,
            "scheme_name": scheme_name,
            "source_url": source_url,
            "last_updated": today,
            "chunk_count": len(chunks_list),
            "chunks": chunks_list
        }

        with open(os.path.join(scheme_dir, "chunks.json"), "w", encoding="utf-8") as f:
            json.dump(chunks_data, f, indent=4)
            
        print(f"Processed: {slug}")
        processed_count += 1

    print(f"Completed! Processed {processed_count} funds successfully. Skipped {skipped_count} invalid funds.")

if __name__ == "__main__":
    clean_html_files()

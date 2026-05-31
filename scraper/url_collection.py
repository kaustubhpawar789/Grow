import os
import re

def extract_urls(input_file="docs/problemstatement.md", output_file="data/raw/urls.txt", max_urls=100):
    """Extracts URLs from the markdown file under the Groww URLs section."""
    print(f"Reading {input_file}...")
    try:
        with open(input_file, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return

    # Find the section containing the URLs
    section_match = re.search(r'## Groww Mutual Funds URLs(.*?)(?:##|\Z)', content, re.DOTALL)
    if not section_match:
        print("Error: Could not find '## Groww Mutual Funds URLs' section.")
        return

    section_text = section_match.group(1)
    
    # Extract URLs
    urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', section_text)
    
    # Take only the first max_urls
    urls = urls[:max_urls]
    
    print(f"Extracted {len(urls)} URLs. Saving to {output_file}...")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, "w") as f:
        for url in urls:
            f.write(f"{url}\n")
            
    print("Done.")

if __name__ == "__main__":
    extract_urls()

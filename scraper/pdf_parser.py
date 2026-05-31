import os
from PyPDF2 import PdfReader

def parse_pdfs(input_dir="data/raw/pdf/", output_dir="data/processed/"):
    print(f"Parsing PDFs from {input_dir}...")
    if not os.path.exists(input_dir):
        print(f"No PDF directory found at {input_dir}. Skipping.")
        return
        
    files = [f for f in os.listdir(input_dir) if f.endswith(".pdf")]
    
    for filename in files:
        filepath = os.path.join(input_dir, filename)
        slug = filename.replace(".pdf", "")
        
        try:
            reader = PdfReader(filepath)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
                    
            scheme_dir = os.path.join(output_dir, slug)
            os.makedirs(scheme_dir, exist_ok=True)
            
            with open(os.path.join(scheme_dir, "cleaned.txt"), "a", encoding="utf-8") as f:
                f.write("\n--- PDF EXTRACT ---\n")
                f.write(text)
                
            print(f"Parsed PDF: {filename}")
        except Exception as e:
            print(f"Failed to parse {filename}: {e}")

if __name__ == "__main__":
    parse_pdfs()

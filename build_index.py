import json
import os
import pdfplumber
from pathlib import Path

DATA_DIR = Path("uploads")
INDEX_FILE = "index.json"

def extract_lines_from_pdf(pdf_path):
    lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                for line in text.split("\n"):
                    line_stripped = line.strip()
                    if line_stripped:
                        lines.append(line_stripped)
    return lines

def build_index():
    index = []

    for file_path in DATA_DIR.glob("*.pdf"):
        print(f"Elaboro: {file_path.name}")
        lines = extract_lines_from_pdf(file_path)
        for line in lines:
            index.append({
                "filename": file_path.name,
                "line": line
            })

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"Indice creato: {INDEX_FILE} ({len(index)} righe)")

if __name__ == "__main__":
    build_index()

import streamlit as st
import json
from pathlib import Path
import os
pdf_files = [f for f in os.listdir("uploads") if f.endswith('.pdf')]
st.write(f"PDF precaricati: {pdf_files}")


DATA_DIR = Path("uploads")
INDEX_FILE = "index.json"


def load_index():
    if not Path(INDEX_FILE).exists():
        st.error("File `index.json` non trovato. Esegui prima `build_index.py`.")
        st.stop()
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


index = load_index()

st.title("Ricerca nelle righe dei PDF")

st.markdown(
    """
    Caricati una volta i PDF in `uploads/` e creato `index.json` con `build_index.py`,  
    puoi usare questa pagina per fare ricerche senza ricaricare i file.
    """
)

query = st.text_input("Inserisci il termine da cercare (es. a)", "")

if query:
    hits = []
    for item in index:
        if query.lower() in item["line"].lower():
            hits.append(item)

    if hits:
        st.markdown("### Risultati trovati")
        st.markdown(f"**{len(hits)}** righe trovate.")
        for item in hits:
            st.markdown(f"📄 `{item['filename']}` → `{item['line']}`")
    else:
        st.info("Nessuna riga contiene il termine cercato.")

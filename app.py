import streamlit as st
import pdfplumber
import pandas as pd
import os

st.set_page_config(layout="wide")
st.title("🔍 Ricerca Globale Preventivi - TUTTI PDF + Volantini")

# === CARICA TUTTI PDF AUTOMATICO ===
if os.path.exists("uploads"):
    pdf_files = [f for f in os.listdir("uploads") if f.endswith('.pdf')]
    st.success(f"✅ {len(pdf_files)} PDF caricati: {', '.join(pdf_files)}")
    
    # === ESTRAI DA TUTTI I PDF (TABELLE + TESTO + VOLANTINI) ===
    all_data = []
    for pdf_file in pdf_files:
        pdf_path = f"uploads/{pdf_file}"
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    # 1. TABELLE
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            if len(table) > 1:
                                headers = table[0]
                                for row in table[1:]:
                                    all_data.append({
                                        'PDF': pdf_file,
                                        'Pagina': i+1,
                                        'Tipo': '📊 TAB',
                                        'Dati': dict(zip(headers[:5], row[:5]))
                                    })
                    
                    # 2. TESTO LIBERO (MIGLIORATO PER PROMOZIONI)
                    page_text = page.extract_text(layout=True)
                    if page_text:
                        lines = [l.strip() for l in page_text.split('\n') if len(l.strip()) > 3]
                        for line in lines[:10]:
                            all_data.append({
                                'PDF': pdf_file,
                                'Pagina': i+1,
                                'Tipo': '📄 TXT', 
                                'Dati': {'Testo': line[:120]}
                            })
                    else:
                        # 3. CARATTERI INDIVIDUALI (VOLANTINI)
                        chars = page.chars
                        if chars:
                            char_text = ''.join([c['text'] for c in chars[:300] if c['text'].strip()])
                            if len(char_text) > 20:
                                all_data.append({
                                    'PDF': pdf_file,
                                    'Pagina': i+1,

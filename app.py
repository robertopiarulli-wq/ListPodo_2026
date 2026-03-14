import streamlit as st
import pdfplumber
import pandas as pd
import os

st.set_page_config(layout="wide")
st.title("🔍 Ricerca Globale Preventivi - TUTTI PDF")

# === CARICA TUTTI PDF AUTOMATICO ===
if os.path.exists("uploads"):
    pdf_files = [f for f in os.listdir("uploads") if f.endswith('.pdf')]
    st.success(f"✅ {len(pdf_files)} PDF caricati: {', '.join(pdf_files)}")
    
    # === ESTRAI DA TUTTI I PDF ===
    all_data = []
    for pdf_file in pdf_files:
        pdf_path = f"uploads/{pdf_file}"
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        if len(table) > 1:
                            headers = table[0]
                            for row in table[1:]:
                                all_data.append({
                                    'PDF': pdf_file,
                                    'Pagina': i+1,
                                    'Dati': dict(zip(headers[:5], row[:5]))
                                })
    
    if all_data:
        df = pd.DataFrame(all_data)
        st.success(f"📊 {len(df)} righe totali estratte da tutti i PDF!")
        
        # === RICERCA GLOBALE (SEMPRE VISIBILE) ===
        st.subheader("🔍 RICERCA SU TUTTI I PDF")
        col1, col2, col3 = st.columns(3)
        with col1:
            query_tutti = st.text_input("🔎 Cerca in tutti i campi")
        with col2:
            query_codice = st.text_input("📱 Codice/SKU") 
        with col3:
            query_prodotto = st.text_input("📦 Prodotto/Descrizione")
        
        # === FILTRA SU TUTTI I CAMPI ===
        df_display = df.copy()
        for query in [q for q in [query_tutti, query_codice, query_prodotto] if q]:
            df_display = df_display[df_display['Dati'].astype(str).str.contains(query, case=False, na=False)]
        
        st.success(f"🔎 {len(df_display)} risultati trovati")
        
        # === SOLO COLONNA DATI - CARATTERI GRANDI ===
        st.subheader(f"📋 {len(df_display)} Risultati (solo Dati)")
        for idx, row in df_display.iterrows():
            dati_str = " | ".join([f"{k}: {v}" for k,v in row['Dati'].items() if v])
            st.markdown(f"""
            <div style='font-size: 18px; padding: 12px; border-bottom: 1px solid #eee; margin: 5px 0;'>
                <strong style='color: #1f77b4;'>{row['PDF']} (Pg.{row['Pagina']})</strong><br>
                {dati_str}
            </div>
            """, unsafe_allow_html=True)
        
        st.download_button("💾 Scarica risultati", df_display.to_csv(index=False), "ricerca.csv")
    else:
        st.info("📄 Nessuna tabella trovata. Solo testo?")
else:
    st.error("❌ Cartella 'uploads/' mancante!")

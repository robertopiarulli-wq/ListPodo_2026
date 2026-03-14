import streamlit as st
import pdfplumber
import pandas as pd
import os

st.set_page_config(layout="wide")
st.title("📊 Preventivo da PDF")

# === LISTA PDF ===
if os.path.exists("uploads"):
    pdf_files = [f for f in os.listdir("uploads") if f.endswith('.pdf')]
    st.success(f"✅ {len(pdf_files)} PDF nuovi caricati!")
    st.write(pdf_files)
    
    selected_pdf = st.selectbox("🔽 Scegli PDF", pdf_files)
    
    if selected_pdf:
        pdf_path = f"uploads/{selected_pdf}"
        with pdfplumber.open(pdf_path) as pdf:
            data = []
            for i, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        if len(table) > 1:
                            headers = table[0]
                            for row in table[1:]:
                                data.append({
                                    'PDF': selected_pdf,
                                    'Pagina': i+1,
                                    'Dati': dict(zip(headers, row[:5]))
                                })
            
            if data:
                df = pd.DataFrame(data)
                
                # === RICERCA ESTESA (QUI!) ===
                st.subheader("🔍 RICERCA SU TUTTI I CAMPI")
                col1, col2, col3 = st.columns(3)
                with col1:
                    query_tutti = st.text_input("🔎 Cerca ovunque")
                with col2:
                    query_codice = st.text_input("📱 Codice")
                with col3:
                    query_prodotto = st.text_input("📦 Prodotto")
                
                # FILTRA
                df_display = df.copy()
                for query in [q for q in [query_tutti, query_codice, query_prodotto] if q]:
                    df_display = df_display[df_display['Dati'].astype(str).str.contains(query, case=False, na=False)]
                
                st.success(f"📊 {len(df_display)} righe trovate")
                st.dataframe(df_display, use_container_width=True, hide_index=True)
            else:
                st.info("📄 Solo testo, nessun tabella trovata")
else:
    st.error("❌ Crea cartella 'uploads/' su GitHub!")

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
    
    # === ESTRAI DA TUTTI I PDF (TABELLE + TESTO LIBERO) ===
    all_data = []
    for pdf_file in pdf_files:
        pdf_path = f"uploads/{pdf_file}"
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    # === 1. TABELLE (come prima) ===
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            if len(table) > 1:
                                headers = table[0]
                                for row in table[1:]:
                                    all_data.append({
                                        'PDF': pdf_file,
                                        'Pagina': i+1,
                                        'Tipo': 'TAB',
                                        'Dati': dict(zip(headers[:5], row[:5]))
                                    })
                    
                    # === 2. TESTO LIBERO (per volantini) ===
                    page_text = page.extract_text()
                    if page_text:
                        lines = [line.strip() for line in page_text.split('\n') if line.strip() and len(line.strip()) > 3]
                        for line_num, line in enumerate(lines[:10]):  # Prime 10 righe per pg
                            all_data.append({
                                'PDF': pdf_file,
                                'Pagina': i+1,
                                'Tipo': 'TESTO',
                                'Dati': {'Testo': line[:100]}
                            })
                    
                    # === 3. IMMAGINI ===
                    images = page.images
                    if images:
                        for img_idx, img in enumerate(images):
                            all_data.append({
                                'PDF': pdf_file,
                                'Pagina': i+1,
                                'Tipo': 'IMG',
                                'Dati': {'Immagine': f'Img{img_idx+1} {img["size"]}'}
                            })
        except:
            st.warning(f"⚠️ Errore lettura {pdf_file}")
    
    if all_data:
        df = pd.DataFrame(all_data)
        st.success(f"📊 {len(df)} righe totali (Tabelle: {len([x for x in all_data if x['Tipo']=='TAB'])}, Testo: {len([x for x in all_data if x['Tipo']=='TESTO'])}, Img: {len([x for x in all_data if x['Tipo']=='IMG'])})")
        
        # === RICERCA GLOBALE ===
        st.subheader("🔍 RICERCA SU TUTTI I PDF")
        col1, col2, col3 = st.columns(3)
        with col1:
            query_tutti = st.text_input("🔎 Cerca ovunque")
        with col2:
            query_codice = st.text_input("📱 Codice/SKU") 
        with col3:
            query_prodotto = st.text_input("📦 Prodotto/Descrizione")
        
        # === FILTRA ===
        df_display = df.copy()
        for query in [q for q in [query_tutti, query_codice, query_prodotto] if q]:
            df_display = df_display[df_display['Dati'].astype(str).str.contains(query, case=False, na=False)]
        
        st.success(f"🔎 {len(df_display)} risultati trovati")
        
        # === SOLO COLONNA DATI - GRANDI ===
        st.subheader(f"📋 {len(df_display)} Risultati")
        for idx, row in df_display.iterrows():
            dati_str = " | ".join([f"{k}: {v}" for k,v in row['Dati'].items() if v])
            tipo_emoji = {'TAB':'📊', 'TESTO':'📄', 'IMG':'🖼️'}[row['Tipo']]
            st.markdown(f"""
            <div style='font-size: 18px; padding: 12px; border-bottom: 1px solid #eee; margin: 5px 0;'>
                <strong style='color: #1f77b4;'>{tipo_emoji} {row['PDF']} (Pg.{row['Pagina']})</strong><br>
                {dati_str}
            </div>
            """, unsafe_allow_html=True)
        
        st.download_button("💾 Scarica", df_display.to_csv(index=False), "ricerca_completa.csv")
    else:
        st.info("📄 Nessun dato estratto")
else:
    st.error("❌ Cartella 'uploads/' mancante!")

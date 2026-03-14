import streamlit as st
import pdfplumber
import pandas as pd
import os

st.set_page_config(layout="wide")
st.title("🔍 Ricerca Globale Preventivi - DEBUG PDF")

# === CARICA TUTTI PDF con DIAGNOSTICA ===
if os.path.exists("uploads"):
    pdf_files = [f for f in os.listdir("uploads") if f.endswith('.pdf')]
    st.success(f"✅ {len(pdf_files)} PDF caricati: {', '.join(pdf_files)}")
    
    all_data = []
    debug_info = []
    
    for pdf_file in pdf_files:
        pdf_path = f"uploads/{pdf_file}"
        st.write(f"🔍 Analizzo **{pdf_file}**...")
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                st.write(f"   📄 {total_pages} pagine totali")
                
                page_content_types = []
                has_content = False
                
                for i, page in enumerate(pdf.pages[:3]):  # Prime 3 pg
                    # 1. TABELLE
                    tables = page.extract_tables()
                    num_tables = len(tables or [])
                    if num_tables > 0:
                        page_content_types.append(f"TAB({num_tables})")
                        for table in tables:
                            if len(table) > 1:
                                headers = table[0]
                                for row in table[1:2]:  # Solo 1 riga x esempio
                                    all_data.append({
                                        'PDF': pdf_file, 'Pagina': i+1, 'Tipo': 'TAB',
                                        'Dati': dict(zip(headers[:5], row[:5]))
                                    })
                        has_content = True
                    
                    # 2. TESTO
                    page_text = page.extract_text()
                    num_lines = len([l for l in page_text.split('\n') if l.strip()])
                    if num_lines > 2:
                        page_content_types.append(f"TXT({num_lines})")
                        lines = [l.strip() for l in page_text.split('\n') if l.strip()]
                        for line in lines[:3]:  # Prime 3 righe
                            all_data.append({
                                'PDF': pdf_file, 'Pagina': i+1, 'Tipo': 'TXT',
                                'Dati': {'Testo': line[:100]}
                            })
                        has_content = True
                
                debug_info.append(f"{pdf_file}: {', '.join(page_content_types) if page_content_types else 'VUOTO'}")
                
                if not has_content:
                    st.warning(f"⚠️ {pdf_file}: Nessun contenuto rilevato")
                else:
                    st.success(f"✅ {pdf_file}: OK")
                    
        except Exception as e:
            st.error(f"❌ {pdf_file}: ERRORE {str(e)[:50]}")
            debug_info.append(f"{pdf_file}: ERRORE")
    
    st.subheader("📋 DEBUG RIEPILOGO")
    for info in debug_info:
        st.write(info)
    
    if all_data:
        df = pd.DataFrame(all_data)
        st.success(f"📊 {len(df)} righe estratte totali")
        
        # RICERCA SEMPLICE
        query = st.text_input("🔍 Cerca")
        if query:
            df_filtered = df[df['Dati'].astype(str).str.contains(query, case=False, na=False)]
            st.subheader(f"📋 {len(df_filtered)} risultati")
            for _, row in df_filtered.iterrows():
                dati_str = " | ".join([f"{k}: {v}" for k,v in row['Dati'].items() if v])
                st.markdown(f"""
                <div style='font-size: 16px; padding: 10px; border-bottom: 1px solid #eee;'>
                    <strong>{row['PDF']} (Pg.{row['Pagina']})</strong>: {dati_str}
                </div>
                """, unsafe_allow_html=True)

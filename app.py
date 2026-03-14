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
                                    'Dati': dict(zip(headers, row[:5]))  # Prime 5 colonne
                                })
            
            if data:
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
                
                # RICERCA
                query = st.text_input("🔍 Cerca (es. 'prezzo' o 'codice')")
                if query:
                    filtered = df[df['Dati'].astype(str).str.contains(query, case=False)]
                    st.dataframe(filtered)
            else:
                st.info("📄 Solo testo? Prossimo step: estrazione testo.")
else:
    st.error("❌ Crea 'uploads/' su GitHub!")

# Dopo estrazione df (riga ~35)
st.subheader("🔍 RICERCA ESTESA")
col1, col2, col3 = st.columns(3)
with col1: query_tutti = st.text_input("🔎 Cerca ovunque")
with col2: query_codice = st.text_input("📱 Codice")
with col3: query_prodotto = st.text_input("📦 Prodotto")

# Filtra
df_display = df.copy()
if query_tutti: 
    df_display = df_display[df['Dati'].astype(str).str.contains(query_tutti, case=False)]
if query_codice or query_prodotto:
    for query in [q for q in [query_codice, query_prodotto] if q]:
        df_display = df_display[df_display['Dati'].astype(str).str.contains(query, case=False)]

st.dataframe(df_display)

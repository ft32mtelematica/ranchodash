import streamlit as st
st.title("PREVISÃO DE RANCHO")

pg = st.navigation([
    st.Page("pages/geral.py", title="Valores Diários", icon="📊"),
    st.Page("pages/por_pessoa2.py", title="Valores por Pessoa", icon="👤"),
    st.Page("pages/fluxodecaixa.py", title="Fluxo de Caixa", icon=("💰")),
])

pg.run()

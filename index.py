import streamlit as st
st.title("PREVISÃO DE RANCHO")

pg = st.navigation([
    st.Page("geral.py", title="Valores Diários", icon="📊"),
    st.Page("por_pessoa2.py", title="Valores por Pessoa", icon="👤"),
    st.Page("fluxodecaixa.py", title="Fluxo de Caixa", icon=("💰")),
])

pg.run()

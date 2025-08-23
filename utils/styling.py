import streamlit as st

def apply_global_styles():
    """
    Aplica estilos CSS globais lendo um arquivo .css e injetando na aplicação.
    """
    try:
        with open(".streamlit/style.css", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Arquivo .streamlit/style.css não encontrado. Estilos personalizados não serão aplicados.")

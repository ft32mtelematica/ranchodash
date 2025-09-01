import streamlit as st
from utils.styling import apply_global_styles, render_card

apply_global_styles()

st.subheader("Visão Geral")

col1, col2, col3 = st.columns(3)

with col1:
    render_card(
        label="Total Arrecadado",
        value="R$ 1.250,00",
        content="Conteúdo do Card 1."
    )

with col2:
    render_card(
        label="Saldo Atual",
        value="R$ 345,70",
        content="Conteúdo do Card 2."
    )

with col3:
    render_card(
        label="Militares no Rancho",
        value="42",
        content="Conteúdo do Card 3."
    )

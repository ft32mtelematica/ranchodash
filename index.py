# ==============================================================================
# 1. IMPORTAÇÃO DAS BIBLIOTECAS
# ==============================================================================
import streamlit as st
from utils.styling import apply_global_styles

# ==============================================================================
# 2. CONFIGURAÇÃO DA PÁGINA PRINCIPAL E NAVEGAÇÃO
# ==============================================================================
# Aplica os estilos globais definidos no arquivo .streamlit/style.css
apply_global_styles()

# Define o título principal que aparecerá no topo da aplicação.
st.logo("/home/ramos/DESENVOLVIMENTO/previsao_de_rancho_V5/images/Brasao32BPMM.png", size="large")
st.title("Previsão de Rancho")

# Utiliza a nova função `st.navigation` do Streamlit para criar um menu de navegação
# na barra lateral. Cada `st.Page` representa um link para um arquivo de página diferente.
pg = st.navigation([
    # Link para a página de visualização geral dos valores diários.
    st.Page("pages/geral.py", title="Valores Diários", icon="📊"),
    # Link para a página de consulta de valores por pessoa.
    st.Page("pages/por_pessoa4.py", title="Valores por Pessoa", icon="👤"),
    # Link para a página de registro de entradas e saídas do caixa.
    st.Page("pages/fluxodecaixa.py", title="Fluxo de Caixa", icon="💰"),
    # Link para a página de registro de retiradas específicas.
    st.Page("pages/retiradas.py", title="Retiradas", icon="💸"),
])

caminho_logo = "/home/ramos/DESENVOLVIMENTO/previsao_de_rancho_V5/images/Brasao32BPMM.png"
st.sidebar.image(caminho_logo, width=200) # Aumente ou diminua este valor

# Executa a navegação, fazendo com que o menu e as páginas funcionem.
pg.run()

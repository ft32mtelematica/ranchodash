import streamlit as st
import os

def apply_global_styles():
    """
    Aplica estilos CSS globais lendo um arquivo .css e injetando na aplicação.
    Usa um caminho absoluto para garantir que o arquivo seja encontrado,
    independentemente de onde a função é chamada.
    """
    try:
        # Constrói o caminho absoluto para o arquivo style.css
        current_dir = os.path.dirname(os.path.abspath(__file__)) # Diretório do arquivo atual (utils)
        project_root = os.path.dirname(current_dir)              # Diretório raiz do projeto
        css_file_path = os.path.join(project_root, ".streamlit", "style.css") # Caminho completo para o CSS

        with open(css_file_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Arquivo de estilo não encontrado em: {css_file_path}. Estilos personalizados não serão aplicados.")
        

def render_card(label, value=None, content=None, chart=None, render_now=True):
    """
    Cria o HTML para um card de métrica.
    
    Args:
        label (str): O rótulo do card.
        value (str): O valor principal do card.
        content (str): O conteúdo descritivo do card.
        render_now (bool): Se True, renderiza o card imediatamente com st.markdown. 
                           Se False, retorna a string HTML do card.
    """
    # CSS específico para o card. O padding é aplicado aqui.
    card_html = f"""
    <div style="
        background-color: #131314;
        border: 5px solid #FFD700;
        border-radius: 10px;
        margin-bottom: 15px;
        padding: 20px;
        box-sizing: border-box;
        height: 93%;
    ">
        <div style="font-family: Verdana, Geneva, sans-serif; color: #E0E0E0; font-size: 14px;">{label}</div>
        <div style="font-family: Arial Black, Gadget, sans-serif; color: white; font-size: 32px; margin: 10px 0;">{value}</div>
        <div style="font-family: Verdana, Geneva, sans-serif; color: #E0E0E0; font-size: 14px;">{content}</div>
    </div>
    """
    if render_now:
        st.markdown(card_html, unsafe_allow_html=True)
    else:
        return card_html

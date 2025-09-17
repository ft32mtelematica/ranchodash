# ==============================================================================
# 1. IMPORTAÇÃO DAS BIBLIOTECAS (sem alterações)
# ==============================================================================
import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from utils.styling import apply_global_styles
from utils.g_sheets_connector import get_gspread_client

# ==============================================================================
# 2. CONFIGURAÇÃO DAS COLUNAS 
# ==============================================================================
COLUNA_DATA = "REGISTRO"
COLUNA_VALOR = "LANÇAMENTOS"

# ==============================================================================
# 3. FUNÇÃO DE CARREGAMENTO DE DADOS 
# ==============================================================================
@st.cache_data(ttl=10)
def load_fluxo_caixa_data(_client):
    
    try:
        spreadsheet = _client.open("Previsao_de_Rancho")
        worksheet = spreadsheet.worksheet("FLUXO DE CAIXA")
        data = worksheet.get_all_records()
        if not data:
            st.info("A aba 'FLUXO DE CAIXA' está vazia.")
            return pd.DataFrame()
        df = pd.DataFrame(data)
        if COLUNA_DATA in df.columns:
            df[COLUNA_DATA] = pd.to_datetime(df[COLUNA_DATA], format='%d/%m/%Y %H:%M:%S', errors='coerce').dt.tz_localize(None)
            df.dropna(subset=[COLUNA_DATA], inplace=True)
            df = df.sort_values(by=COLUNA_DATA).reset_index(drop=True)
        else:
            st.warning(f"A coluna '{COLUNA_DATA}' não foi encontrada.")
            return pd.DataFrame()
        if COLUNA_VALOR in df.columns:
            df[COLUNA_VALOR] = pd.to_numeric(df[COLUNA_VALOR], errors='coerce').fillna(0)
        else:
            st.warning(f"A coluna '{COLUNA_VALOR}' não foi encontrada.")
            return pd.DataFrame()
        df['Saldo'] = df[COLUNA_VALOR].cumsum()
        return df
    except gspread.exceptions.WorksheetNotFound:
        st.error("Erro: A aba 'FLUXO DE CAIXA' não foi encontrada.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return pd.DataFrame()

# ==============================================================================
# 4. INÍCIO DA INTERFACE DO APLICATIVO
# ==============================================================================
# Aplica os estilos globais definidos no arquivo .streamlit/style.css
apply_global_styles()

client = get_gspread_client()
if client:
    df_caixa = load_fluxo_caixa_data(client)
else:
    st.error("A conexão com o Google Sheets falhou.")
    df_caixa = pd.DataFrame()

if not df_caixa.empty:
    # ==============================================================================
    # CARD DINÂMICO PARA O SALDO ATUAL
    # ==============================================================================
    
    # 1. Obter o saldo atual
    saldo_atual = df_caixa['Saldo'].iloc[-1] if not df_caixa.empty else 0

    # 2. Definir a cor e um ícone com base no valor do saldo
    if saldo_atual >= 0:
        cor_do_saldo = "#28a745"  # Verde (mesma cor do gráfico)
        icone_saldo = "🔼"
    else:
        cor_do_saldo = "#dc3545"  # Vermelho (mesma cor do gráfico)
        icone_saldo = "🔽"

    # 3. Usar st.markdown para criar o card com HTML e CSS dinâmico
    #    A "f-string" (f"...") nos permite injetar as variáveis Python diretamente no HTML/CSS
    
    st.markdown(f"""
    <div style="
        border: 2px solid #31333F;
        border-radius: 10px;
        padding: 1px;
        text-align: center;
        background-color: {cor_do_saldo}; 
        margin-bottom: 1px;
    ">
        <span style="font-size: 22px; font-weight: bold; color: #31333F;">Saldo Atual do Caixa</span>
        <h2 style="color: #f0f2f6; font-size: 36px; margin-top: 1px; margin-bottom: 0;">
            {icone_saldo} R$ {saldo_atual:,.2f}
        </h2>
    </div>
    """, unsafe_allow_html=True)

    # O st.metric original foi substituído pelo card acima.
    # st.metric(label="**Saldo Atual do Caixa**", value=f"R$ {saldo_atual:,.2f}")

    # ==============================================================================
    # Gráfico de barras para variação do saldo
    # ==============================================================================
    
    if 'num_lancamentos_slider' not in st.session_state:
        st.session_state.num_lancamentos_slider = min(80, len(df_caixa))

    #st.subheader(f"Variação do Saldo (Últimos {st.session_state.num_lancamentos_slider} Lançamentos)")
    
    df_filtrado = df_caixa.tail(st.session_state.num_lancamentos_slider).copy()
    df_filtrado['Status'] = ['Positivo' if val >= 0 else 'Negativo' for val in df_filtrado['Saldo']]
    df_filtrado['Eixo_X'] = df_filtrado[COLUNA_DATA].dt.strftime('%d/%m %H:%M')

    fig = px.bar(df_filtrado, x='Eixo_X', y='Saldo', color='Status', color_discrete_map={'Positivo': '#28a745', 'Negativo': '#dc3545'}, text='Saldo')
    fig.update_layout(xaxis_title='Data do Lançamento', yaxis_title='Saldo (R$)', xaxis_type='category', xaxis_fixedrange=True, yaxis_fixedrange=True, showlegend=False, bargap=0.2, yaxis_rangemode='tozero')
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    st.slider(
        "Selecione o número de lançamentos para visualizar:",
        min_value=5,
        max_value=min(100, len(df_caixa)),
        value=st.session_state.num_lancamentos_slider,
        step=5,
        key='num_lancamentos_slider'
    )

    with st.expander("Ver todos os lançamentos do Fluxo de Caixa"):
        st.dataframe(df_caixa)

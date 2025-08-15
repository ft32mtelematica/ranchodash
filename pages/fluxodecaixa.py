# ==============================================================================
# 1. IMPORTAÇÃO DAS BIBLIOTECAS
# ==============================================================================
import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from utils.g_sheets_connector import get_gspread_client

# ==============================================================================
# 2. CONFIGURAÇÃO DAS COLUNAS
# ==============================================================================

COLUNA_DATA = "REGISTRO"   # Coluna que contém a data e hora das transações.
COLUNA_VALOR = "LANÇAMENTOS"     # Coluna que contém os valores (entradas/saídas).


# ==============================================================================
# 3. FUNÇÃO DE CARREGAMENTO DE DADOS
# ==============================================================================
# Esta função é responsável por buscar os dados da planilha e armazená-los em cache.
@st.cache_data(ttl=300) # Cache de 5 minutos
def load_fluxo_caixa_data(_client):
    """Carrega e processa dados da aba 'FLUXO DE CAIXA'."""
    try:
        spreadsheet = _client.open("Previsao_de_Rancho")
        worksheet = spreadsheet.worksheet("FLUXO DE CAIXA")
        data = worksheet.get_all_records()
        
        if not data:
            st.info("A aba 'FLUXO DE CAIXA' está vazia.")
            return pd.DataFrame()

        df = pd.DataFrame(data)

        # --- Processamento dos Dados ---
        # Garante que a coluna de data/hora seja do tipo datetime para ordenação correta.
        if COLUNA_DATA in df.columns:
            df[COLUNA_DATA] = pd.to_datetime(df[COLUNA_DATA], format='%d/%m/%Y %H:%M:%S', errors='coerce')
            df = df.sort_values(by=COLUNA_DATA).reset_index(drop=True)
        else:
            st.warning(f"A coluna '{COLUNA_DATA}' não foi encontrada na planilha 'FLUXO DE CAIXA'. Verifique a configuração no topo do script. O gráfico pode não ser exibido corretamente.")
            return pd.DataFrame()

        # Garante que a coluna de valor seja numérica para os cálculos.
        # O nome desta coluna é definido na variável COLUNA_VALOR no topo do arquivo.
        if COLUNA_VALOR in df.columns:
            df[COLUNA_VALOR] = pd.to_numeric(df[COLUNA_VALOR], errors='coerce').fillna(0)
        else:
            st.warning(f"A coluna '{COLUNA_VALOR}' não foi encontrada. Verifique a configuração no topo do script. Os cálculos de saldo não podem ser realizados.")
            return pd.DataFrame()

        # Calcula o saldo acumulado para o gráfico.
        df['Saldo'] = df[COLUNA_VALOR].cumsum()

        return df

    except gspread.exceptions.WorksheetNotFound:
        st.error("Erro: A aba 'FLUXO DE CAIXA' não foi encontrada. Verifique o nome na sua planilha.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar ou processar os dados do fluxo de caixa: {e}")
        return pd.DataFrame()

# ==============================================================================
# 4. INÍCIO DA INTERFACE DO APLICATIVO
# ==============================================================================
st.title("Dashboard do Fluxo de Caixa")
st.write("Acompanhe o saldo e a movimentação financeira do caixa.")

# Conecta ao Google Sheets e carrega os dados.
client = get_gspread_client()
if client:
    df_caixa = load_fluxo_caixa_data(client)
else:
    st.error("A conexão com o Google Sheets falhou. Não é possível carregar os dados.")
    df_caixa = pd.DataFrame()

# Só exibe o dashboard se os dados foram carregados com sucesso.
if not df_caixa.empty:
    # Pega o último valor da coluna 'Saldo' que calculamos.
    saldo_atual = df_caixa['Saldo'].iloc[-1] if not df_caixa.empty else 0

    # Exibe o saldo atual em destaque.
    st.metric(label="**Saldo Atual do Caixa**", value=f"R$ {saldo_atual:,.2f}")
    st.markdown("---")

    # Cria o gráfico de variação do saldo.
    st.subheader("Variação do Saldo")
    fig = px.area(df_caixa, x=COLUNA_DATA, y='Saldo', title='Evolução do Saldo do Caixa ao Longo do Tempo', markers=True)
    fig.update_layout(xaxis_title='Data', yaxis_title='Saldo (R$)')
    st.plotly_chart(fig, use_container_width=True)

    # Expansor para visualizar os dados brutos, como em 'por_pessoa4.py'.
    with st.expander("Ver todos os lançamentos do Fluxo de Caixa"):
        st.dataframe(df_caixa)

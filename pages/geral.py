import streamlit as st
import pandas as pd
import gspread
import plotly.express as px
from utils.styling import apply_global_styles, render_card
from utils.g_sheets_connector import get_gspread_client

# ==============================================================================
# FUNÇÃO DE CARREGAMENTO DE DADOS
# ==============================================================================
@st.cache_data(ttl=10)
def load_form_data(_client):
    """Carrega dados da aba 'Respostas_ao_formulario_1'."""
    try:
        spreadsheet = _client.open("Previsao_de_Rancho")
        worksheet = spreadsheet.worksheet("Respostas_ao_formulario_1")
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)

        # Tratamento de colunas de texto
        colunas_texto = ["Quitado", "RE (Sem dígito):"]
        for col in colunas_texto:
            if col in df.columns:
                df[col] = df[col].astype(str)

        # Tratamento de colunas numéricas para os cards de refeição
        colunas_numericas = ["QTD CAFÉ HJ", "QTD ALMOÇO HJ", "TOTAL"]
        for col in colunas_numericas:
            if col in df.columns:
                # Converte para numérico, força erros a virarem NaN, e substitui NaN por 0.
                # Para a coluna TOTAL, convertemos para float, para as outras, para int.
                tipo_numerico = float if col == "TOTAL" else int
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(tipo_numerico)

        return df
    except gspread.exceptions.WorksheetNotFound:
        st.error("Erro: A aba 'Respostas_ao_formulario_1' não foi encontrada.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar os dados do formulário: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=10)
def load_total_arrecadado(_client):
    """Carrega o valor do total arrecadado da célula J1 da aba 'FLUXO DE CAIXA'."""
    try:
        spreadsheet = _client.open("Previsao_de_Rancho")
        worksheet = spreadsheet.worksheet("FLUXO DE CAIXA")
        # gspread.acell() é mais eficiente para buscar um único valor de célula.
        total_value = worksheet.acell('J1').value
        # Retorna o valor encontrado ou um padrão se a célula estiver vazia.
        return total_value if total_value else "R$ 0,00"
    except gspread.exceptions.WorksheetNotFound:
        st.error("Aba 'FLUXO DE CAIXA' não encontrada para buscar o total arrecadado.")
        return "Erro"
    except Exception as e:
        st.error(f"Erro ao buscar o total arrecadado: {e}")
        return "Erro"


apply_global_styles()

st.subheader("Visão Geral")

# ==============================================================================
# LÓGICA DE PAGAMENTO PENDENTE
# ==============================================================================
client = get_gspread_client()
if client:
    df_form = load_form_data(client)
    total_arrecadado_valor = load_total_arrecadado(client)
else:
    st.error("A conexão com o Google Sheets falhou. Não é possível carregar os dados.")
    df_form = pd.DataFrame()
    total_arrecadado_valor = "Indisponível"

# Inicializa as variáveis para os totais
total_cafe = 0
total_almoco = 0
total_pendente = 0.0

# Converte o valor arrecadado (string) para um número (float) para usar nos cálculos
total_arrecadado_numerico = 0.0
if isinstance(total_arrecadado_valor, str) and "R$" in total_arrecadado_valor:
    try:
        # Limpa a string (remove "R$", espaços, separador de milhar) e converte para float
        valor_limpo = total_arrecadado_valor.replace("R$", "").strip().replace(".", "").replace(",", ".")
        total_arrecadado_numerico = float(valor_limpo)
    except (ValueError, TypeError):
        total_arrecadado_numerico = 0.0 # Mantém 0 se a conversão falhar


if not df_form.empty:
    # Calcula o total para o café de hoje
    if "QTD CAFÉ HJ" in df_form.columns:
        total_cafe = df_form["QTD CAFÉ HJ"].sum()
    
    # Calcula o total para o almoço de hoje
    if "QTD ALMOÇO HJ" in df_form.columns:
        total_almoco = df_form["QTD ALMOÇO HJ"].sum()

    # Calcula o valor total pendente de quitação
    if "Quitado" in df_form.columns and "RE (Sem dígito):" in df_form.columns:
        df_pendentes = df_form[df_form['Quitado'] != 'Sim']
        # Soma a coluna "TOTAL" do dataframe filtrado de pendentes
        if "TOTAL" in df_pendentes.columns:
            total_pendente = df_pendentes["TOTAL"].sum()

# ==============================================================================
# RENDERIZAÇÃO DOS CARDS 
# ==============================================================================
col1, col2, col3 = st.columns(3)

with col1:
    render_card(
        label="Total Arrecadado",
        value=total_arrecadado_valor,
        content="Valor total recebido no período."
    )

with col2:
    # 1. Geramos o HTML para cada card sem renderizá-los imediatamente (render_now=False).
    card_cafe_html = render_card(
        label="Café", # Label abreviado para caber melhor
        value=str(total_cafe),
        content="Para hoje",
        render_now=False
    )
    card_almoco_html = render_card(
        label="Almoço",
        value=str(total_almoco),
        content="Para hoje",
        render_now=False
    )
    
    # Os dois HTMLs dentro de um contêiner flexível.
    #    'display: flex' alinha os itens filhos na horizontal.
    #    'gap' adiciona um espaço entre eles.
    #    'flex: 1' faz com que cada card ocupe o mesmo espaço disponível.
    st.markdown(f"""
    <div style="display: flex; gap: 15px;">
        <div style="flex: 1;">{card_cafe_html}</div>
        <div style="flex: 1;">{card_almoco_html}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    # Cria os dados para o gráfico de anel
    dados_grafico = {
        'Status': ['Arrecadado', 'Pendente'],
        'Valores': [total_arrecadado_numerico, total_pendente]
    }
    df_grafico = pd.DataFrame(dados_grafico)

    # Só exibe o gráfico se houver algum valor
    if total_arrecadado_numerico > 0 or total_pendente > 0:
        fig = px.pie(
            df_grafico, 
            values='Valores', 
            names='Status', 
            hole=0.6,
            color='Status',
            color_discrete_map={
                'Arrecadado': '#28a745',
                'Pendente': '#ffc107'
            }
        )
# CÓDIGO CORRIGIDO

        fig.update_traces(
            textinfo='none',
            hoverinfo='label+value',
            # CORRETO: Usando aspas triplas para permitir múltiplas linhas
            hovertemplate="""<b>%{label}</b>  
R$ %{value:,.2f}<extra></extra>"""
        )


        
        fig.update_layout(
            showlegend=False,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)', #
            plot_bgcolor='#131314', # Transparente
            height=150
        )

        # 1. Use st.container(border=True). O CSS fará a estilização.
        with st.container(border=True):
            # Adiciona o título do card
            st.markdown("""
                <div style="text-align: center; font-family: Verdana, Geneva, sans-serif; color: #E0E0E0; font-size: 14px;">
                    Receita Total (Arrecadado vs. Pendente)
                </div>
            """, unsafe_allow_html=True)

            # Renderiza o gráfico dentro do contêiner
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

            # Adiciona o rodapé com os valores
            st.markdown(f"""
                <div style="text-align: center; font-size: 14px; margin-top: -15px;">
                    <span style="color: #28a745;"><b>Arrecadado:</b> R$ {total_arrecadado_numerico:,.2f}</span> | <span style="color: #ffc107;"><b>Pendente:</b> R$ {total_pendente:,.2f}</span>
                </div>
            """, unsafe_allow_html=True)
    else:
        # Se não houver dados, renderiza um card padrão
        render_card(
            label="Receita Total",
            value="R$ 0,00",
            content="Sem dados de receita para exibir."
        )

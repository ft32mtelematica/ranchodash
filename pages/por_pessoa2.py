import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. FUNÇÃO DE CONEXÃO MODIFICADA PARA DEPLOY ---

@st.cache_resource
def get_gspread_client():
    """Conecta ao Google Sheets usando st.secrets para o deploy."""
    try:
        
        creds_dict = st.secrets["gcp_service_account"]
        
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        
        client = gspread.authorize(creds)
        return client
        
    except KeyError:
        st.error("Segredo '[gcp_service_account]' não encontrado. Verifique a configuração no Streamlit Cloud.")
        return None
    except Exception as e:
        st.error(f"Erro ao conectar com a Planilha Google via st.secrets: {e}")
        return None



@st.cache_data(ttl=300)
def load_data(_client):
    """Carrega dados da aba 'Respostas_ao_formulario_1'."""
    # Adicionamos uma verificação para o caso da conexão falhar
    if _client is None:
        return pd.DataFrame()
    try:
        spreadsheet = _client.open("Previsao_de_Rancho")
        worksheet_form = spreadsheet.worksheet("Respostas_ao_formulario_1")
        data_form = worksheet_form.get_all_records()
        df_form = pd.DataFrame(data_form)
        return df_form
    except gspread.exceptions.WorksheetNotFound:
        st.error("Erro: A aba 'Respostas_ao_formulario_1' não foi encontrada. Verifique o nome.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return pd.DataFrame()

# --- Início da Lógica do Dashboard ---

st.title("Consulta e Quitação de Valores")

# Inicializa os estados da sessão
if 'resultado_busca' not in st.session_state:
    st.session_state.resultado_busca = pd.DataFrame()
if 'quitado_sucesso' not in st.session_state:
    st.session_state.quitado_sucesso = False
if "busca_re_input" not in st.session_state:
    st.session_state.busca_re_input = ""

# Conecta e carrega os dados
client = get_gspread_client()
df = load_data(client)



if not df.empty:
    if st.session_state.quitado_sucesso:
        st.success("Pagamento quitado com sucesso! A tela foi atualizada.")
        st.session_state.resultado_busca = pd.DataFrame()
        st.session_state.busca_re_input = ""
        st.session_state.quitado_sucesso = False
        st.cache_data.clear()

    st.subheader("Buscar por RE")
    busca_re = st.text_input('Digite o RE (Sem dígito)', key='busca_re_input')
    
    if st.button('Buscar', key='buscar_btn'):
        # ... (lógica de busca)
        if busca_re:
            try:
                coluna_re = "RE (Sem dígito):"
                if coluna_re in df.columns:
                    df[coluna_re] = df[coluna_re].astype(str)
                    resultado = df[df[coluna_re] == busca_re]
                    
                    if resultado.empty:
                        st.info("Nenhum resultado encontrado para o RE informado.")
                        st.session_state.resultado_busca = pd.DataFrame()
                    else:
                        st.session_state.resultado_busca = resultado
                else:
                    st.error(f"Coluna '{coluna_re}' não encontrada na planilha.")
                    st.session_state.resultado_busca = pd.DataFrame()
            except Exception as e:
                st.error(f"Erro na busca: {e}")
                st.session_state.resultado_busca = pd.DataFrame()
        else:
            st.warning("Digite um RE para realizar a busca.")
            st.session_state.resultado_busca = pd.DataFrame()

    if not st.session_state.resultado_busca.empty:
        # ... (lógica de exibição e quitação com o laço for)
        st.write("Resultado da busca:")
        resultado_salvo = st.session_state.resultado_busca.copy()
        
        if "Quitado" in resultado_salvo.columns:
            resultado_salvo.loc[resultado_salvo['Quitado'] == 'Sim', 'TOTAL'] = 0
        
        st.dataframe(
            resultado_salvo[["Graduação:", "Nome de Guerra:", "TOTAL", "Quitado"]]
            .style.format({"TOTAL": "R$ {:.2f}"})
            .set_properties(**{'background-color': "#3D3A3A", 'color': 'white'})
        )
        
        soma_total = resultado_salvo["TOTAL"].sum()
        
        col1, col2 = st.columns([1, 4])
        col1.metric(label="TOTAL A PAGAR", value=f"R$ {soma_total:.2f}")
        
        if soma_total > 0:
            if col2.button("Quitar", key='quitar_btn'):
                try:
                    spreadsheet = client.open("Previsao_de_Rancho")
                    worksheet = spreadsheet.worksheet("Respostas_ao_formulario_1")
                    header = worksheet.row_values(1)
                    col_num = header.index("Quitado") + 1
                    celulas_para_atualizar = []
                    for idx_pandas in resultado_salvo.index:
                        if resultado_salvo.loc[idx_pandas, "Quitado"] != "Sim":
                            idx_gspread = int(idx_pandas) + 2
                            celula = gspread.Cell(row=idx_gspread, col=col_num, value="Sim")
                            celulas_para_atualizar.append(celula)
                    if celulas_para_atualizar:
                        worksheet.update_cells(celulas_para_atualizar)
                    st.session_state.quitado_sucesso = True
                    st.rerun()
                except gspread.exceptions.APIError as e:
                    st.error(f"Erro de API do Google: {e}. Verifique as permissões de Editor da conta de serviço.")
                except Exception as e:
                    st.error(f"Erro ao tentar quitar o valor: {e}")
else:
    st.warning("Não foi possível carregar os dados da Planilha Google. Verifique as configurações de conexão.")

# Expansor para ver todos os dados da planilha
if not df.empty:
    with st.expander("Ver todos os dados da planilha"):
        st.dataframe(df)

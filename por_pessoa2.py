import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Função para carregar dados da Planilha Google com cache ---
@st.cache_data(ttl=600) # Cache de 10 minutos
def load_google_sheet_data():
    """Conecta na Planilha Google e carrega os dados da primeira aba."""
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        client = gspread.authorize(creds)

        # Nome da planilha
        spreadsheet = client.open("Previsao_de_Rancho") 
        
        # Pega a primeira aba por padrão. Se for outra, use spreadsheet.worksheet("Nome da Aba")
        worksheet = spreadsheet.sheet1 
        
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        return df
    except gspread.exceptions.SpreadsheetNotFound:
        st.error("Planilha não encontrada. Verifique o nome e se ela foi compartilhada com o e-mail de serviço.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao conectar com a Planilha Google: {e}")
        return pd.DataFrame()

# --- Início da Lógica do Dashboard ---

# Carrega os dados da Planilha Google online
df = load_google_sheet_data()

st.title("Valores por Pessoa")

# Só continua se os dados foram carregados com sucesso
if not df.empty:
    st.subheader("Todos os dados da planilha")
    st.dataframe(df)

    busca_re = st.text_input('Buscar por RE (Sem dígito)')
    buscar_btn = st.button('Buscar')

    if buscar_btn:
        if busca_re:
            try:
                # Garante que a coluna existe e converte para string para evitar problemas de tipo
                coluna_re = "RE (Sem dígito):" # Nome exato da coluna na sua planilha
                
                if coluna_re in df.columns:
                    # Converte a coluna para string para a comparação funcionar corretamente
                    df[coluna_re] = df[coluna_re].astype(str)
                    
                    resultado = df[df[coluna_re] == busca_re]
                    
                    if resultado.empty:
                        st.info("Nenhum resultado encontrado.")
                    else:
                        st.write("Resultado da busca:")
                        # Exibe as colunas desejadas do resultado
                        st.dataframe(resultado[["Graduação:", "Nome de Guerra:", "TOTAL"]])
                else:
                    st.error(f"Coluna '{coluna_re}' não encontrada no DataFrame.")
            
            except Exception as e:
                st.error(f"Erro na busca: {e}")
        else:
            st.warning("Digite um valor para buscar.")
else:
    st.warning("Não foi possível carregar os dados da Planilha Google para iniciar o dashboard.")
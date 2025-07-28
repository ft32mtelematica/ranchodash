# Dentro do seu arquivo .py (ex: por_pessoa2.py)

import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

@st.cache_data(ttl=600)
def load_google_sheet_data():
    """Conecta na Planilha Google no Streamlit no formato TOML."""
    try:
        # Pede ao Streamlit pela seção [gcp_service_account] 
        creds_dict = st.secrets["gcp_service_account"]
        
        # Define os escopos (permissões)
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
               
        # Passe o dicionário E os escopos na mesma chamada
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        
        # Agora, autorize diretamente com o objeto 'creds' já configurado
        client = gspread.authorize(creds)

        
        spreadsheet = client.open("Previsao_de_Rancho") 
        worksheet = spreadsheet.sheet1 
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        return df
        
    except KeyError:
        st.error("Segredo '[gcp_service_account]' não encontrado. Verifique a configuração no Streamlit Cloud.")
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
                        #
                        soma_total = resultado["TOTAL"].sum()
                        #
                        st.metric(label="TOTAL", value=f"{soma_total:.2f}")
                else:
                    st.error(f"Coluna '{coluna_re}' não encontrada no DataFrame.")
            
            except Exception as e:
                st.error(f"Erro na busca: {e}")
        else:
            st.warning("Digite um valor para buscar.")
else:
    st.warning("Não foi possível carregar os dados da Planilha Google para iniciar o dashboard.")

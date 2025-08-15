# ==============================================================================
# 1. IMPORTAÇÃO DAS BIBLIOTECAS
# ==============================================================================
import streamlit as st                                  # Usado para caching (@st.cache_resource) e para acessar os 'secrets' em produção.
import gspread                                          # Biblioteca para interagir com a API do Google Sheets.
from oauth2client.service_account import ServiceAccountCredentials # Classe para autenticação via conta de serviço.
import os                                               # Usado para manipular caminhos de arquivos do sistema operacional.

# ==============================================================================
# 2. FUNÇÃO DE CONEXÃO COM O GOOGLE SHEETS
# ==============================================================================
# O decorator `@st.cache_resource` é crucial aqui. Ele garante que a conexão com
# o Google Sheets seja estabelecida apenas UMA VEZ e depois reutilizada em todo
# o aplicativo. Isso economiza tempo e recursos, evitando múltiplas autenticações.
@st.cache_resource
def get_gspread_client():
    """
    Conecta ao Google Sheets de forma inteligente, priorizando o ambiente local.
    - Localmente, usa o arquivo credentials.json (se existir).
    - Em produção (Streamlit Cloud), usa st.secrets.
    """
    # Define o escopo de permissões. 'feeds' para ler/escrever em planilhas e 'drive' para gerenciar arquivos.
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    # Constrói um caminho absoluto para o arquivo de credenciais.
    # Isso é uma prática robusta que garante que o arquivo `credentials.json` seja
    # encontrado, não importa de qual subpasta o script esteja sendo executado.
    current_dir = os.path.dirname(os.path.abspath(__file__)) # Pega o diretório do arquivo atual (utils/).
    project_root = os.path.dirname(current_dir)              # Sobe um nível para a raiz do projeto.
    creds_path = os.path.join(project_root, 'credentials.json') # Monta o caminho completo: /path/to/project/credentials.json

    try:
        # --------------------------------------------------------------------------
        # LÓGICA DE AUTENTICAÇÃO HÍBRIDA (LOCAL vs. PRODUÇÃO)
        # --------------------------------------------------------------------------

        # 1. Prioriza o arquivo local para desenvolvimento.
        if os.path.exists(creds_path):
            creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
            # st.info("Conectado via credentials.json (Local).") # Descomente para depuração.
        
        # 2. Se não houver arquivo local, tenta usar os 'secrets' do Streamlit (para produção).
        #    Quando o app é hospedado no Streamlit Community Cloud, as credenciais são
        #    armazenadas de forma segura em `st.secrets`.
        elif hasattr(st, 'secrets') and "gcp_service_account" in st.secrets:
            creds_dict = st.secrets["gcp_service_account"]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            # st.info("Conectado via Streamlit Secrets (Produção).") # Descomente para depuração.
        
        # 3. Se nenhum método de credencial funcionar, exibe uma mensagem de erro clara.
        else:
            st.error("Nenhuma credencial encontrada. Adicione 'credentials.json' para desenvolvimento local ou configure os 'secrets' do Streamlit para produção.")
            return None # Retorna None para indicar falha na conexão.
            
        # Autoriza a conexão com as credenciais obtidas.
        client = gspread.authorize(creds)
        return client # Retorna o objeto cliente, pronto para ser usado.

    # Captura qualquer exceção que possa ocorrer durante o processo de autenticação.
    except Exception as e:
        st.error(f"Erro ao autenticar com o Google Sheets: {e}")
        return None # Retorna None em caso de erro.
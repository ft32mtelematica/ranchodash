# ==============================================================================
# 1. IMPORTAÇÃO DAS BIBLIOTECAS
# ==============================================================================
import streamlit as st                                  # Biblioteca principal para criar a interface web.
import gspread                                          # Biblioteca para interagir com a API do Google Sheets.
from datetime import datetime                           # Módulo para obter a data e hora atuais.
from utils.g_sheets_connector import get_gspread_client # Importa nossa função de conexão centralizada.

# ==============================================================================
# 2. INTERFACE DO USUÁRIO
# ==============================================================================

# Define o título e uma breve descrição para a página.
st.subheader("Lançamento de Retiradas")
st.write("Aqui você pode registrar as saídas do caixa do Rancho.")

# ==============================================================================
# 3. FORMULÁRIO DE ENTRADA DE DADOS
# ==============================================================================
# `st.form` é usado para agrupar vários campos de entrada. Os dados só são enviados
# quando o botão de submissão dentro do formulário é clicado.
# `clear_on_submit=True` limpa os campos do formulário após o envio bem-sucedido.
with st.form(key="RETIRADAS_form", clear_on_submit=True):
    # Campos de entrada de texto e número para o usuário preencher.
    motivo = st.text_input("Motivo*", help="Ex: Compra de material de limpeza, Venda de bebidas")
    local = st.text_input("Local", help="Ex: Supermercado X, Cantina")
    produto = st.text_input("Produto/Descrição*", help="Ex: Água sanitária, Detergente, Refrigerante")
    
    # Campo de valor. Note que pedimos um valor positivo para facilitar a digitação do usuário.
    valor_input = st.number_input("Valor (R$)*", min_value=0.0, format="%.2f", help="Use somente valores positivos, ele será convertido automaticamente para negativo.")
    
    # Botão de submissão do formulário.
    submit_button = st.form_submit_button(label="Enviar Registro")
    
# ==============================================================================
# 4. LÓGICA DE SUBMISSÃO DO FORMULÁRIO
# ==============================================================================
# Este bloco de código só é executado quando o `submit_button` é pressionado.
if submit_button:
    # --------------------------------------------------------------------------
    # 4.1. VALIDAÇÃO E PROCESSAMENTO DOS DADOS DE ENTRADA
    # --------------------------------------------------------------------------
    # Verifica se os campos obrigatórios foram preenchidos.
    if not motivo or not produto or valor_input == 0:
        st.warning("Por favor, preencha todos os campos obrigatórios (*) com valores válidos.")
    else:
        # Converte o valor positivo inserido pelo usuário em um valor negativo,
        # pois esta página registra apenas retiradas (saídas de caixa).
        valor = valor_input * -1

        # --------------------------------------------------------------------------
        # 4.2. ENVIO DOS DADOS PARA A PLANILHA
        # --------------------------------------------------------------------------
        client = get_gspread_client() # Obtém o cliente de conexão com o Google Sheets.
        if client: # Procede apenas se a conexão foi bem-sucedida.
            try:
                # Abre a planilha pelo nome.
                spreadsheet = client.open("Previsao_de_Rancho")
                sheet_name = "RETIRADAS" # Define o nome da aba de destino.
                
                # Tenta acessar a aba. Se não existir, cria uma nova.
                try:
                    worksheet = spreadsheet.worksheet(sheet_name)
                except gspread.exceptions.WorksheetNotFound:
                    st.info(f"Aba '{sheet_name}' não encontrada. Criando uma nova...")
                    worksheet = spreadsheet.add_worksheet(title=sheet_name, rows="100", cols="10")
                    # Adiciona o cabeçalho à nova aba.
                    header = ["Data/Hora", "Motivo", "Local", "Produto/Descrição", "Valor"]
                    worksheet.append_row(header, value_input_option='USER_ENTERED')

                # Prepara a nova linha de dados para ser inserida.
                timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S') # Formata a data/hora atual no padrão brasileiro.
                new_row = [timestamp, motivo, local, produto, valor] # Monta a lista com os dados.
                
                # Adiciona a nova linha ao final da planilha.
                worksheet.append_row(new_row, value_input_option='USER_ENTERED')
                
                # Fornece feedback de sucesso ao usuário.
                st.success("Registro enviado com sucesso para a planilha!")
                #st.balloons() # Balões 

            # Tratamento de erros específicos e genéricos.
            except gspread.exceptions.SpreadsheetNotFound:
                st.error("Erro: A planilha 'Previsao_de_Rancho' não foi encontrada. Verifique o nome e as permissões da sua conta de serviço.")
            except ImportError as e:
                st.error(f"Ocorreu um erro ao tentar enviar os dados: {e}")

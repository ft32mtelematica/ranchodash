# ==============================================================================
# 1. IMPORTAÇÃO DAS BIBLIOTECAS
# ==============================================================================
# Importa as bibliotecas necessárias para o funcionamento do aplicativo.

import streamlit as st                                  # Biblioteca principal para criar a interface web do aplicativo.
import pandas as pd                                     # Biblioteca para manipulação e análise de dados, usada aqui como um DataFrame.
import gspread                                          # Biblioteca para interagir com a API do Google Sheets.
from utils.styling import apply_global_styles           # Importa nossa função de estilo.
from utils.g_sheets_connector import get_gspread_client # Importa a função de conexão centralizada que criamos.

# --- Funções de Conexão e Carregamento de Dados  ---

# ==============================================================================
# 2. FUNÇÃO DE CARREGAMENTO DE DADOS
# ==============================================================================
# Esta função é responsável por buscar os dados da planilha e armazená-los em cache.
@st.cache_data(ttl=300)
def load_data(_client):
    """Carrega dados da aba 'Respostas_ao_formulario_1'."""
    try:
        spreadsheet = _client.open("Previsao_de_Rancho")
        worksheet_form = spreadsheet.worksheet("Respostas_ao_formulario_1")
        data_form = worksheet_form.get_all_records()
        df_form = pd.DataFrame(data_form) # Converte os dados recebidos em um DataFrame do Pandas.

        # --- Limpeza e Conversão de Tipos ---
        # Esta é a correção principal. Garantimos que as colunas tenham tipos
        # consistentes para evitar os erros de serialização do Arrow.

        # Colunas que devem ser tratadas como texto (string).
        # Adicionado "IDENTIFICAÇÃO" como medida de segurança caso a coluna exista com esse nome.
        colunas_texto = ["RE (Sem dígito):", "Graduação:", "Nome de Guerra:", "Quitado", "IDENTIFICAÇÃO"]
        for col in colunas_texto:
            if col in df_form.columns:
                # .astype(str) converte todos os valores da coluna para texto.
                df_form[col] = df_form[col].astype(str)

        # Para colunas que deveriam ser numéricas, como 'TOTAL'.
        if "TOTAL" in df_form.columns:
            # pd.to_numeric com errors='coerce' transforma qualquer valor não-numérico em NaN (vazio).
            # .fillna(0) então substitui esses vazios por 0. É a forma mais segura de limpar colunas numéricas.
            df_form["TOTAL"] = pd.to_numeric(df_form["TOTAL"], errors='coerce').fillna(0)

        return df_form # Retorna o DataFrame para ser usado no aplicativo.
    except gspread.exceptions.WorksheetNotFound:
        st.error("Erro: A aba 'Respostas_ao_formulario_1' não foi encontrada. Verifique o nome.")
        return pd.DataFrame() # Retorna um DataFrame vazio em caso de erro para evitar que o app quebre.
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return pd.DataFrame() # Retorna um DataFrame vazio em caso de erro.

# --- Início da Lógica do Dashboard ---

# ==============================================================================
# 3. INÍCIO DA INTERFACE DO APLICATIVO
# ==============================================================================
# Aplica os estilos globais definidos no arquivo .streamlit/style.css
apply_global_styles()

# Define o título da página.
st.subheader("Consulta e Quitação de Valores por Pessoa")

# ==============================================================================
# 4. INICIALIZAÇÃO DO ESTADO DA SESSÃO (SESSION STATE)
# ==============================================================================
# O `st.session_state` é um dicionário que o Streamlit usa para guardar variáveis
# entre as interações do usuário (como clicar em um botão). Sem ele, a cada
# interação, todas as variáveis seriam resetadas.

if 'resultado_busca' not in st.session_state:    # Guarda o resultado da busca para não se perder.
    st.session_state.resultado_busca = pd.DataFrame()
if 'quitado_sucesso' not in st.session_state:    # Funciona como um "sinalizador" para mostrar a mensagem de sucesso após quitar.
    st.session_state.quitado_sucesso = False
if "busca_re_input" not in st.session_state:     # Guarda o valor digitado no campo de busca para não ser apagado.
    st.session_state.busca_re_input = ""

# ==============================================================================
# 5. CONEXÃO E CARREGAMENTO INICIAL DOS DADOS
# ==============================================================================
# Tenta conectar ao Google Sheets e carregar os dados.
client = get_gspread_client() # Chama nossa função de conexão centralizada.

# Adiciona uma verificação para garantir que a conexão foi bem-sucedida antes de prosseguir.
if client: # Se a conexão funcionou...
    df = load_data(client) # ...carrega os dados da planilha.
else: # Se a conexão falhou...
    st.error("A conexão com o Google Sheets falhou. Não é possível carregar os dados da página.")
    df = pd.DataFrame() # ...cria um DataFrame vazio para evitar que o resto do código quebre.

# ==============================================================================
# 6. LÓGICA PRINCIPAL DO DASHBOARD
# ==============================================================================
# Todo o código a seguir só é executado se os dados foram carregados com sucesso.
if not df.empty:

    # --------------------------------------------------------------------------
    # 6.1. LÓGICA DE FEEDBACK E LIMPEZA PÓS-QUITAÇÃO
    # --------------------------------------------------------------------------
    # Este bloco verifica se uma quitação acabou de ocorrer (usando o "sinalizador"
    # que criamos no session_state) para mostrar uma mensagem de sucesso e
    # limpar a tela para uma nova consulta.
    if st.session_state.quitado_sucesso:
        st.success("Pagamento quitado com sucesso! A tela foi atualizada.")
        
        # Limpa os estados da sessão para resetar a interface.
        st.session_state.resultado_busca = pd.DataFrame() # Limpa a tabela de resultados.
        st.session_state.busca_re_input = ""              # Limpa o campo de texto da busca.
        st.session_state.quitado_sucesso = False          # Reseta o "sinalizador" para não mostrar a mensagem de novo.
        st.cache_data.clear()                             # Limpa o cache de dados para forçar uma nova busca na planilha na próxima interação.

    # --------------------------------------------------------------------------
    # 6.2. LÓGICA DE BUSCA
    # --------------------------------------------------------------------------
    # Cria a interface para o usuário digitar o RE e buscar.
    st.subheader("Buscar por RE")
    busca_re = st.text_input('Digite o RE (Sem dígito)', key='busca_re_input') # O `key` vincula este campo ao nosso session_state.
    
    if st.button('Buscar', key='buscar_btn'): # Se o botão 'Buscar' for pressionado...
        if busca_re: # ...e se o campo de busca não estiver vazio...
            try:
                coluna_re = "RE (Sem dígito):" # Nome da coluna na planilha.
                if coluna_re in df.columns: # Verifica se a coluna realmente existe no DataFrame.
                    df[coluna_re] = df[coluna_re].astype(str) # Garante que a coluna RE seja tratada como texto para a comparação.
                    resultado = df[df[coluna_re] == busca_re] # Filtra o DataFrame, pegando só as linhas onde o RE bate.
                    
                    if resultado.empty: # Se o filtro não retornou nenhuma linha...
                        st.info("Nenhum resultado encontrado para o RE informado.")
                        st.session_state.resultado_busca = pd.DataFrame() # Limpa o resultado anterior.
                    else: # Se encontrou resultados...
                        st.session_state.resultado_busca = resultado # ...guarda no session_state para exibir.
                else: # Se a coluna de RE não foi encontrada na planilha...
                    st.error(f"Coluna '{coluna_re}' não encontrada na planilha.")
                    st.session_state.resultado_busca = pd.DataFrame()
            except Exception as e:
                st.error(f"Erro na busca: {e}")
                st.session_state.resultado_busca = pd.DataFrame()
        else: # Se o botão foi clicado, mas o campo de busca estava vazio...
            st.warning("Digite um RE para realizar a busca.")
            st.session_state.resultado_busca = pd.DataFrame()

    # --------------------------------------------------------------------------
    # 6.3. LÓGICA DE EXIBIÇÃO DO RESULTADO E QUITAÇÃO
    # --------------------------------------------------------------------------
    # Este bloco só é executado se houver um resultado de busca guardado no session_state.
    if not st.session_state.resultado_busca.empty: # Verifica se a busca retornou algum resultado.
        st.write("Resultado da busca:")
        
        # Pega o resultado da sessão. Usar .copy() é uma boa prática para evitar avisos do Pandas
        # ao modificar um DataFrame que é uma "fatia" de outro.
        resultado_salvo = st.session_state.resultado_busca.copy() 
        
        # Modificação condicional: Se a coluna 'Quitado' for 'Sim', o valor em 'TOTAL' é zerado
        # apenas para a exibição e cálculo da soma, sem alterar os dados originais.
        if "Quitado" in resultado_salvo.columns: # Verifica se a coluna 'Quitado' existe.
            resultado_salvo.loc[resultado_salvo['Quitado'] == 'Sim', 'TOTAL'] = 0
        
        # Exibe o DataFrame com o resultado, selecionando colunas específicas e aplicando formatação.
        st.dataframe(
            resultado_salvo[["Graduação:", "Nome de Guerra:", "TOTAL", "Quitado"]] # Seleciona as colunas a serem exibidas.
            .style.format({"TOTAL": "R$ {:.2f}"}) # Formata a coluna 'TOTAL' como moeda.
            .set_properties(**{'background-color': "#3D3A3A", 'color': 'white'}) # Aplica estilo CSS na tabela.
        )
        
        # Calcula a soma da coluna 'TOTAL' (que já foi zerada para os itens quitados).
        soma_total = resultado_salvo["TOTAL"].sum() 
        
        # Cria duas colunas para organizar o total e o botão de quitar.
        col1, col2 = st.columns([1, 4]) 
        col1.metric(label="TOTAL A PAGAR", value=f"R$ {soma_total:.2f}") # Exibe o total a pagar.
        
        # Botão condicional: O botão "Quitar" só aparece se houver um valor a ser pago.
        if soma_total > 0: # Garante que o botão não apareça se o valor for zero.
            if col2.button("Quitar", key='quitar_btn'): # Se o botão 'Quitar' for pressionado...
                try:
                    # --------------------------------------------------------------------------
                    # 6.3.1. LÓGICA DE ATUALIZAÇÃO EM LOTE (BATCH UPDATE)
                    # --------------------------------------------------------------------------
                    # Esta é a forma mais eficiente de atualizar múltiplas células. Em vez de
                    # fazer uma chamada de API para cada célula, preparamos uma lista de
                    # todas as mudanças e enviamos tudo de uma só vez.

                    # Abre a planilha e a aba específica.
                    spreadsheet = client.open("Previsao_de_Rancho")
                    worksheet = spreadsheet.worksheet("Respostas_ao_formulario_1")
                    
                    header = worksheet.row_values(1) # Pega a primeira linha (cabeçalho).
                    col_num = header.index("Quitado") + 1 # Encontra o número da coluna "Quitado" (+1 porque a contagem começa em 1).

                    celulas_para_atualizar = [] # Cria uma lista vazia para armazenar as células que vamos modificar.

                    # Itera sobre cada linha do DataFrame de resultado. O `.index` aqui se refere ao
                    # índice original da linha no DataFrame `df` completo.
                    for idx_pandas in resultado_salvo.index:
                        # Ignora as linhas que já estão quitadas para não fazer trabalho desnecessário na API.
                        if resultado_salvo.loc[idx_pandas, "Quitado"] != "Sim":
                            # Calcula o índice da linha na Planilha Google.
                            # (+2 porque o índice do Pandas começa em 0 e a planilha em 1, e ainda temos a linha do cabeçalho).
                            idx_gspread = int(idx_pandas) + 2
                            
                            # Cria um objeto de célula (gspread.Cell) com a linha, coluna e o novo valor ("Sim").
                            celula = gspread.Cell(row=idx_gspread, col=col_num, value="Sim")
                            celulas_para_atualizar.append(celula) # Adiciona o objeto à nossa lista de atualizações.

                    # Se a lista não estiver vazia, envia todas as atualizações de uma vez.
                    if celulas_para_atualizar: 
                        worksheet.update_cells(celulas_para_atualizar)
                    # --------------------------------------------------------------------------

                    # Define o "sinalizador" de sucesso como True.
                    st.session_state.quitado_sucesso = True 
                    # Força o recarregamento da página do topo. O Streamlit vai executar o script
                    # novamente, e o bloco 6.1 será acionado para mostrar a mensagem de sucesso.
                    st.rerun() 
                
                # Tratamento de erros específicos da API do Google.
                except gspread.exceptions.APIError as e:
                    st.error(f"Erro de API do Google: {e}. Verifique as permissões de Editor da conta de serviço.")
                # Tratamento de outros erros genéricos.
                except Exception as e:
                    st.error(f"Erro ao tentar quitar o valor: {e}")
else:
    # Mensagem exibida caso a conexão inicial com a planilha falhe (bloco 5).
    st.warning("Não foi possível carregar os dados da Planilha Google para iniciar o dashboard.")

# ==============================================================================
# 7. EXPANSOR PARA VISUALIZAÇÃO DOS DADOS BRUTOS
# ==============================================================================
# Oferece uma forma de visualizar todos os dados da planilha, útil para depuração.
if not df.empty: # Só mostra o expansor se os dados foram carregados.
    with st.expander("Ver todos os dados da planilha"):
        st.dataframe(df) # Exibe o DataFrame completo.

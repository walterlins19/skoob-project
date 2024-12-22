import streamlit as st
import pandas as pd





# Título do aplicativo
st.set_page_config(page_title="skoob", page_icon="📚")
st.title("Visualizador de Arquivo Excel (.xlsm)")

# Carregar o arquivo Excel
uploaded_file = st.file_uploader("Carregar um arquivo Excel (.xlsm)", type=["xlsm"])
if uploaded_file is not None:
    # Ler o arquivo Excel
    xls = pd.ExcelFile(uploaded_file)
    
    # Exibir as planilhas disponíveis
    sheet_names = xls.sheet_names
    selected_sheet = st.selectbox("Selecione uma planilha", sheet_names)
    
    # Ler a planilha selecionada
    df = pd.read_excel(xls, sheet_name=selected_sheet)
    st.session_state['df_livros'] = df
    st.dataframe(df)
        # Contar a quantidade de livros por país
# Mensagem opcional se nenhum arquivo for carregado
if uploaded_file is None:
    st.info("Por favor, carregue um arquivo Excel (.xlsm) para ver os dados.")



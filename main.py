import streamlit as st
import pandas as pd
st.set_page_config(page_title="skoob", page_icon="📚")
st.title("Visualizador de Arquivo Excel (.xlsm)")

st.markdown("""
Para usar este aplicativo, você pode fazer upload de um arquivo .xlsm ou usar o arquivo local padrão.
[Clique aqui para baixar o template](https://link-to-your-template.xlsm) Em construção 🛠️!!
""")

# Create two columns for the upload options
col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Carregar um arquivo Excel (.xlsm)", type=["xlsm"])

with col2:
    use_local_file = st.button("Usar arquivo local padrão (Livros de Lucas Oliveira)")

# Handle file loading
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.session_state['df_livros'] = df
    st.success("Arquivo carregado com sucesso!")
    st.dataframe(df)
elif use_local_file:
    try:
        local_file_path = "Book1.xlsm"
        df = pd.read_excel(local_file_path)
        st.session_state['df_livros'] = df
        st.success("Arquivo local carregado com sucesso!")
        st.dataframe(df)
    except FileNotFoundError:
        st.error("Arquivo local 'Book1 (3).xlsm' não encontrado. Verifique se o arquivo está no diretório correto.")
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo local: {str(e)}")

if uploaded_file is None and not use_local_file:
    st.info("Por favor, carregue um arquivo Excel (.xlsm) ou use o arquivo local padrão para ver os dados.")

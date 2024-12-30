import streamlit as st
import pandas as pd

st.set_page_config(page_title="skoob", page_icon="📚")
st.title("Visualizador de Arquivo Excel (.xlsm)")

st.markdown("""
Para usar este aplicativo, você precisa de um arquivo .xlsm no formato correto.
[Clique aqui para baixar o template](https://link-to-your-template.xlsm)
""")

uploaded_file = st.file_uploader("Carregar um arquivo Excel (.xlsm)", type=["xlsm"])
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.session_state['df_livros'] = df
    st.dataframe(df)

if uploaded_file is None:
    st.info("Por favor, carregue um arquivo Excel (.xlsm) para ver os dados.")
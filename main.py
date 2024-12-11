import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.express as px
import pycountry

from deep_translator import GoogleTranslator

# Inicializa o tradutor do googletrans
def traduzir_para_ingles(pais_em_portugues):
    try:
        # Tenta traduzir o nome do país de português para inglês
        traducao = GoogleTranslator(source='pt', target='en').translate(pais_em_portugues)
        return traducao
    except Exception as e:
        print(f"Erro ao traduzir o país {pais_em_portugues}: {e}")
        return pais_em_portugues  # Retorna o nome original caso haja erro

        return pais_em_portugues  # Retorna o nome original caso haja erro
    


def obter_codigo_iso(pais):
    try:
        # Tenta traduzir o nome do país para inglês
        pais_em_ingles = traduzir_para_ingles(pais)
        
        # Buscar o país usando o nome em inglês
        country = pycountry.countries.get(name=pais_em_ingles)
        
        # Verifica se encontrou o país e retorna o código ISO alpha-3
        if country:
            return country.alpha_3
        else:
            return None  # Caso o país não seja encontrado
    except Exception as e:
        print(f"Erro ao buscar o código para {pais}: {e}")
        return None
    
def quantidade_livros_por_pais(df, coluna_pais, coluna_livro):
    """
    Cria um DataFrame com a quantidade de livros por país.
    
    Parameters:
    - df (pd.DataFrame): DataFrame com os dados de livros.
    - coluna_pais (str): Nome da coluna que indica o país de origem do livro.
    - coluna_livro (str): Nome da coluna que identifica cada livro (pode ser o título ou outro identificador).
    
    Returns:
    - pd.DataFrame: DataFrame com a quantidade de livros por país.
    """
    # Agrupar os dados pelo país e contar o número de livros
    df_livros_por_pais = df.groupby(coluna_pais)[coluna_livro].count().reset_index()
    
    # Renomear as colunas para maior clareza
    df_livros_por_pais.columns = [coluna_pais, "Quantidade_Livros"]
    
    return df_livros_por_pais

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
    st.dataframe(df)
        # Contar a quantidade de livros por país
    if 'País' in df.columns:  # Substitua 'país' pelo nome da coluna que contém os países
        #df['Codigo_ISO'] = df['País'].apply(obter_codigo_iso)
        df_livros_por_pais = quantidade_livros_por_pais(df, 'País', 'Título')
        df_livros_por_pais['Codigo_ISO'] = df_livros_por_pais['País'].apply(obter_codigo_iso)
        print(df_livros_por_pais)
        fig = px.choropleth(df_livros_por_pais, locations="Codigo_ISO",
                            color="Quantidade_Livros", # lifeExp is a column of gapminder
                            hover_name="País", # column to add to hover information
                            color_continuous_scale=px.colors.sequential.Plasma)
        fig.show()

# Mensagem opcional se nenhum arquivo for carregado
if uploaded_file is None:
    st.info("Por favor, carregue um arquivo Excel (.xlsm) para ver os dados.")



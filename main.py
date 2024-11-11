import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

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
        # Contar a quantidade de livros por país
    if 'País' in df.columns:  # Substitua 'país' pelo nome da coluna que contém os países
        country_counts = df['País'].value_counts().reset_index()
        country_counts.columns = ['País', 'Quantidade']
        
        # Ler as coordenadas dos países
        country_coords = pd.read_csv('country_coordinates.csv')
        
        # Unir os dados para obter as coordenadas dos países
        heat_data = country_counts.merge(country_coords, left_on='País', right_on='Country', how='left')
        heat_data = heat_data.dropna(subset=['Latitude', 'Longitude'])
        
        # Criar um mapa
        m = folium.Map(location=[20, 0], zoom_start=2)
        
        # Adicionar dados de calor ao mapa
        heat_map_data = [[row['Latitude'], row['Longitude'], row['Quantidade']] for index, row in heat_data.iterrows()]
        HeatMap(heat_map_data).add_to(m)
        
        # Exibir o mapa no Streamlit
        st_folium(m, width=700, height=500)

# Mensagem opcional se nenhum arquivo for carregado
if uploaded_file is None:
    st.info("Por favor, carregue um arquivo Excel (.xlsm) para ver os dados.")



import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from io import BytesIO
import requests
import time
from typing import List


import http.client


from datetime import datetime


def preparar_dados_para_analise(df):
    """
    Prepara o DataFrame para análise, garantindo tipos de dados corretos.
    
    Args:
        df (pandas.DataFrame): DataFrame original
    
    Returns:
        pandas.DataFrame: DataFrame preparado
    """
    # Converte colunas para os tipos corretos
    df['Conclusão'] = pd.to_datetime(df['Conclusão'], errors='coerce')
    df['Ano de Publicação'] = pd.to_numeric(df['Ano de Publicação'], errors='coerce')
    df['Páginas'] = pd.to_numeric(df['Páginas'], errors='coerce')
    df['Nota'] = pd.to_numeric(df['Nota'], errors='coerce')
    
    # Remove linhas com datas inválidas
    df_limpo = df.dropna(subset=['Conclusão'])
    
    return df_limpo

def filtrar_livros_por_anos(df, anos_selecionados):
    """
    Filtra livros para os anos selecionados.
    
    Args:
        df (pandas.DataFrame): DataFrame preparado
        anos_selecionados (List[int]): Anos selecionados para análise
    
    Returns:
        pandas.DataFrame: DataFrame filtrado
    """
    return df[df['Conclusão'].dt.year.isin(anos_selecionados)]

def criar_visualizacoes_livros(df):
    """
    Cria múltiplas visualizações de dados de livros usando Plotly.
    
    Args:
        df (pandas.DataFrame): DataFrame com informações dos livros
    """
    # Título da página
    st.title("📊 Análise Detalhada de Leitura")
    
    # Divide a página em colunas
    tab1, tab2, tab3, tab4 = st.tabs([
        "Distribuição de Notas e Páginas", 
        "Análise de Gêneros", 
        "Perfil dos Autores", 
        "Tendências de Leitura"
    ])
    
    with tab1:
        st.header("Distribuição de Notas e Páginas")
        
        # Scatter plot de Notas vs Páginas
        fig_notas_paginas = px.scatter(
            df, 
            x='Páginas', 
            y='Nota', 
            color='Gênero',
            hover_data=['Título', 'Autor'],
            title='Relação entre Número de Páginas e Nota',
            labels={'Páginas': 'Número de Páginas', 'Nota': 'Nota do Livro'}
        )
        fig_notas_paginas.update_layout(height=600)
        st.plotly_chart(fig_notas_paginas, use_container_width=True)
        
        # Box plot de notas por gênero
        fig_notas_genero = px.box(
            df, 
            x='Gênero', 
            y='Nota',
            title='Distribuição de Notas por Gênero',
            labels={'Gênero': 'Gênero Literário', 'Nota': 'Nota do Livro'}
        )
        fig_notas_genero.update_layout(height=600)
        st.plotly_chart(fig_notas_genero, use_container_width=True)
    
    with tab2:
        st.header("Análise de Gêneros Literários")
        
        # Gráfico de contagem de livros por gênero
        genero_counts = df['Gênero'].value_counts()
        fig_generos = px.pie(
            values=genero_counts.values, 
            names=genero_counts.index,
            title='Distribuição de Livros por Gênero',
            hole=0.3
        )
        st.plotly_chart(fig_generos, use_container_width=True)
        
        # Gráfico de médias de notas por gênero
        notas_por_genero = df.groupby('Gênero')['Nota'].mean().sort_values(ascending=False)
        fig_notas_genero = px.bar(
            x=notas_por_genero.index, 
            y=notas_por_genero.values,
            title='Média de Notas por Gênero',
            labels={'x': 'Gênero', 'y': 'Média da Nota'}
        )
        st.plotly_chart(fig_notas_genero, use_container_width=True)
    
    with tab3:
        st.header("Perfil dos Autores")
        
        # Distribuição de autores por sexo
        sexo_autor_counts = df['Sexo Autor'].value_counts()
        fig_sexo_autor = px.pie(
            values=sexo_autor_counts.values, 
            names=sexo_autor_counts.index,
            title='Distribuição de Livros por Sexo do Autor',
            hole=0.3
        )
        st.plotly_chart(fig_sexo_autor, use_container_width=True)
        
        # Gráfico de etnia dos autores
        etnia_counts = df['Etnia'].value_counts()
        fig_etnia = px.bar(
            x=etnia_counts.index, 
            y=etnia_counts.values,
            title='Número de Livros por Etnia do Autor',
            labels={'x': 'Etnia', 'y': 'Número de Livros'}
        )
        st.plotly_chart(fig_etnia, use_container_width=True)
    
    with tab4:
        st.header("Tendências de Leitura")
        
        # Preparar dados de conclusão
        df['Conclusão'] = pd.to_datetime(df['Conclusão'])
        df['Mês Conclusão'] = df['Conclusão'].dt.to_period('M')
        
        # Gráfico de livros lidos por mês
        livros_por_mes = df.groupby('Mês Conclusão').size()
        fig_livros_mes = px.line(
            x=livros_por_mes.index.astype(str), 
            y=livros_por_mes.values,
            title='Número de Livros Lidos por Mês',
            labels={'x': 'Mês', 'y': 'Número de Livros'}
        )
        st.plotly_chart(fig_livros_mes, use_container_width=True)
        
        # Gráfico de páginas lidas por mês
        paginas_por_mes = df.groupby('Mês Conclusão')['Páginas'].sum()
        fig_paginas_mes = px.bar(
            x=paginas_por_mes.index.astype(str), 
            y=paginas_por_mes.values,
            title='Total de Páginas Lidas por Mês',
            labels={'x': 'Mês', 'y': 'Número de Páginas'}
        )
        st.plotly_chart(fig_paginas_mes, use_container_width=True)

def verificar_colunas(df, required_columns):
    """
    Verifica se todas as colunas necessárias estão presentes no DataFrame.
    
    Args:
        df (pandas.DataFrame): DataFrame a ser verificado
        required_columns (List[str]): Lista de colunas necessárias
    
    Raises:
        ValueError: Se alguma coluna estiver faltando
    """
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"As seguintes colunas estão faltando: {missing_columns}")


def organizar_e_filtrar_livros(df):
    """
    Organiza os livros do mais recente ao mais antigo e filtra os livros lidos no ano atual.
    
    Args:
        df (pandas.DataFrame): DataFrame com informações dos livros
    
    Returns:
        pandas.DataFrame: DataFrame filtrado e ordenado
    """
    # Verifica se a coluna 'Conclusão' existe
    if 'Conclusão' not in df.columns:
        raise ValueError("A coluna 'Conclusão' não existe no DataFrame.")
    
    # Converte a coluna 'Conclusão' para datetime
    df['Conclusão'] = pd.to_datetime(df['Conclusão'], errors='coerce')
    
    # Remove linhas com datas inválidas
    df_limpo = df.dropna(subset=['Conclusão'])
    
    # Ordena do mais recente ao mais antigo
    df_ordenado = df_limpo.sort_values('Conclusão', ascending=False)
    
    # Obtém o ano atual
    ano_atual = datetime.now().year
    
    # Filtra livros lidos no ano atual
    df_ano_atual = df_ordenado[df_ordenado['Conclusão'].dt.year == ano_atual]
    
    return df_ano_atual

def app_retrospectiva_leitura(df):
    """
    Aplicativo Streamlit para retrospectiva de leitura.
    
    Args:
        df (pandas.DataFrame): DataFrame original de livros
    """
    # Preparar dados
    df_preparado = preparar_dados_para_analise(df)
    
    # Título do aplicativo
    st.sidebar.title("🔍 Filtros de Retrospectiva")
    
    # Obter anos únicos de conclusão
    anos_disponiveis = sorted(df_preparado['Conclusão'].dt.year.unique())
    
    # Seleção de anos com múltipla escolha
    anos_selecionados = st.sidebar.multiselect(
        "Selecione os anos para análise",
        options=anos_disponiveis,
        default=anos_disponiveis  # Por padrão, seleciona todos os anos
    )
    
    # Se nenhum ano for selecionado, usa todos os anos
    if not anos_selecionados:
        st.warning("Nenhum ano selecionado. Por favor, escolha pelo menos um ano.")
        return
    
    # Filtrar livros
    df_filtrado = filtrar_livros_por_anos(df_preparado, anos_selecionados)
    metricas = {
        'Total de Livros': len(df_filtrado),
        'Total de Páginas': df_filtrado['Páginas'].sum() if 'Páginas' in df_filtrado.columns else 0,
        'Média de Páginas por Livro': round(df_filtrado['Páginas'].mean(), 2) if 'Páginas' in df_filtrado.columns else 0,
        'Número de Autores Únicos': df_filtrado['Autor'].nunique() if 'Autor' in df_filtrado.columns else 0
        }
    criar_cards_metricas(metricas)
    # Criar visualizações
    criar_visualizacoes_livros(df_filtrado)

def criar_cards_metricas(metricas):
    """
    Cria cards de métricas no estilo Power BI usando Streamlit.
    
    Args:
        metricas (dict): Dicionário com métricas calculadas
    """
    # Configuração de layout de colunas
    cols = st.columns(4)
    
    # Definição de ícones e cores para cada métrica
    icones_metricas = {
        'Total de Livros': '📚',
        'Total de Páginas': '🌐',
        'Média de Páginas por Livro': '📖',
        'Número de Autores Únicos': '👥'
    }
    
    cores_metricas = {
        'Total de Livros': 'background-color: #3498db; color: white;',
        'Total de Páginas': 'background-color: #2ecc71; color: white;',
        'Média de Páginas por Livro': 'background-color: #e74c3c; color: white;',
        'Número de Autores Únicos': 'background-color: #f39c12; color: white;'
    }
    
    # Criação dos cards
    for i, (nome, valor) in enumerate(metricas.items()):
        with cols[i]:
            st.markdown(f"""
            <div style="
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                {cores_metricas[nome]}
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            ">
                <h3 style="margin-bottom: 10px;">{icones_metricas[nome]} {nome}</h3>
                <p style="font-size: 24px; font-weight: bold;">{valor:,}</p>
            </div>
            """, unsafe_allow_html=True)

def add_book_covers(df, title_column='Título'):
    """
    Enhance an existing DataFrame by adding book cover images.
    
    Args:
        df (pandas.DataFrame): Input DataFrame containing book titles
        title_column (str): Name of the column containing book titles
    
    Returns:
        pandas.DataFrame: DataFrame with an added 'Book Cover' column
    """
    # Create a copy of the DataFrame to avoid modifying the original
    enhanced_df = df.copy()
    
    # List to store book cover images
    book_covers = []
    
    # API connection setup
    conn = http.client.HTTPSConnection("hapi-books.p.rapidapi.com")
    
    headers = {
        'x-rapidapi-key': "567a545e60msh8fecd6a13c95adbp106bacjsn41754a801cde",
        'x-rapidapi-host': "hapi-books.p.rapidapi.com"
    }
    
    # Process each book title
    for title in df[title_column]:
        try:
            # Prepare the search query (replace spaces with +)
            formatted_query = title.replace(" ", "+")
            
            # Make API request
            conn.request("GET", f"/search/{formatted_query}", headers=headers)
            res = conn.getresponse()
            data = res.read().decode("utf-8")
            
            # Parse the JSON response
            import json
            book_data = json.loads(data)
            
            # Try to get the first book's cover
            if book_data and len(book_data) > 0:
                cover_url = book_data[0].get('cover')
                
                # Download book cover
                if cover_url:
                    response = requests.get(cover_url)
                    if response.status_code == 200:
                        # Open image with Pillow
                        img = Image.open(BytesIO(response.content))
                        book_covers.append(img)
                        time.sleep(15)
                    else:
                        # If download fails, append None
                        book_covers.append(None)
                else:
                    book_covers.append(None)
            else:
                book_covers.append(None)
        
        except Exception as e:
            print(f"Error fetching cover for {title}: {e}")
            book_covers.append(None)
    
    # Add book covers to the DataFrame
    enhanced_df['Book Cover'] = book_covers
    
    return enhanced_df

def display_books_with_covers(enhanced_df):
    """
    Display books with their covers in a Streamlit app.
    
    Args:
        enhanced_df (pandas.DataFrame): DataFrame with book covers
    """
    st.title("Books with Covers")
    
    # Ensure we have a Book Cover column
    if 'Book Cover' not in enhanced_df.columns:
        st.error("No book covers found. Please add covers first.")
        return
    
    # Display books
    for index, row in enhanced_df.iterrows():
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # Display book cover
            if row['Book Cover'] is not None:
                st.image(row['Book Cover'], width=150)
            else:
                st.write("No cover available")
        
        with col2:
            # Display book details
            for column in enhanced_df.columns:
                if column != 'Book Cover':
                    st.write(f"{column}: {row[column]}")
        
        # Add a separator
        st.markdown("---")




st.sidebar.header('Carregar Arquivo Excel')

# File uploader for the user to upload an XLSM file
uploaded_file = st.sidebar.file_uploader("Escolha um arquivo XLSM", type=["xlsm"])

if uploaded_file is not None:
    try:
        # Read the uploaded XLSM file using pandas (Excel can be .xlsm, .xlsx)
        df = pd.read_excel(uploaded_file, sheet_name='DB', engine='openpyxl')
        #df, df.columns = df[1:] , df.iloc[0]
        # Streamlit Layout
        st.title('Dashboard: Livros')
        print(df)
        df = df.drop(columns=['ID'])

        # Show basic stats
        st.header('Estatísticas gerais')

        required_columns = [
        "Título", "Gênero", "Ficção", "País", "Região", "Autor", "Editora", 
        "Ano de Publicação", "Séc", "Sexo Autor", "Etnia", "Páginas", "Conclusão", "Nota"
        ]
 
        app_retrospectiva_leitura(df)
        #df = add_book_covers(df)
            # Verifica as colunas
        verificar_colunas(df, required_columns)
        
        # Cria visualizações
        #criar_visualizacoes_livros(df)
    except Exception as e:
        print(f"Erro: {e}")


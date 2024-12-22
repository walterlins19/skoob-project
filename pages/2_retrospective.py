import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from io import BytesIO
import requests
import time
from typing import List
import numpy as np


import http.client


from datetime import datetime
def load_data():
    """
    Carrega os dados do session_state.
    Retorna None se os dados não estiverem disponíveis.
    """
    if 'df_livros' in st.session_state:
        return st.session_state['df_livros']
    else:
        st.error("Por favor, carregue os dados na página principal primeiro.")
        return None

def criar_linha_tempo_leitura(df):
    """
    Cria uma linha do tempo interativa de leitura usando Streamlit e Plotly
    
    Parâmetros:
    df (pandas.DataFrame): DataFrame com informações de leitura
        Colunas esperadas:
        - 'Título': Título do livro
        - 'Conclusão': Data de conclusão da leitura
        - 'Nota': Nota dada ao livro
    """
    # Verificar colunas necessárias
    colunas_necessarias = ['Título', 'Conclusão', 'Nota']
    for coluna in colunas_necessarias:
        if coluna not in df.columns:
            st.error(f"Coluna '{coluna}' não encontrada no DataFrame")
            return

    # Converter coluna de Conclusão para datetime se não estiver
    if not pd.api.types.is_datetime64_any_dtype(df['Conclusão']):
        df['Conclusão'] = pd.to_datetime(df['Conclusão'])

    # Ordenar por data de conclusão
    df_ordenado = df.sort_values('Conclusão')

    # Título da seção
    st.header("📚 Linha do Tempo de Leitura")

    # Opções de visualização
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Filtro de ano
        anos_unicos = sorted(df_ordenado['Conclusão'].dt.year.unique())
        ano_selecionado = st.selectbox(
            "Selecione o Ano", 
            anos_unicos, 
            index=len(anos_unicos) - 1  # Seleciona o ano mais recente por padrão
        )
    
    with col2:
        # Opção de mostrar todos os anos
        mostrar_todos = st.checkbox("Mostrar Todos os Anos", value=False)

    # Filtrar dados
    if not mostrar_todos:
        df_filtrado = df_ordenado[df_ordenado['Conclusão'].dt.year == ano_selecionado]
    else:
        df_filtrado = df_ordenado

    fig = go.Figure()
    
    # Criar frames para animação
    frames = []
    
    for frame_idx in range(len(df_filtrado)):
        frame_data = []
        
        # Dados até o frame atual
        current_data = df_filtrado.iloc[:frame_idx + 1]
        
        # Adicionar linha conectando os pontos
        if len(current_data) > 1:
            frame_data.append(
                go.Scatter(
                    x=current_data['Conclusão'],
                    y=list(range(1, len(current_data) + 1)),
                    mode='lines',
                    line=dict(color='rgba(100, 100, 100, 0.5)', width=2),
                    hoverinfo='skip'
                )
            )
        
        # Adicionar pontos até o frame atual
        for idx, (_, linha) in enumerate(current_data.iterrows(), 1):
            frame_data.append(
                go.Scatter(
                    x=[linha['Conclusão']],
                    y=[idx],
                    mode='markers+text',
                    marker=dict(
                        size=15,
                        color=linha['Nota'],
                        colorscale='Viridis',
                        colorbar=dict(title="Nota"),
                        showscale=True,
                        cmin=df_filtrado['Nota'].min(),
                        cmax=df_filtrado['Nota'].max()
                    ),
                    text=[f"{linha['Título']} Nota: {linha['Nota']:.1f}"],
                    textposition="top center",
                    hoverinfo='text'
                )
            )
        
        frames.append(go.Frame(data=frame_data, name=f"frame{frame_idx}"))
    
    # Adicionar o primeiro ponto como estado inicial
    first_row = df_filtrado.iloc[0]
    fig.add_trace(
        go.Scatter(
            x=[first_row['Conclusão']],
            y=[1],
            mode='markers+text',
            marker=dict(
                size=15,
                color=first_row['Nota'],
                colorscale='Viridis',
                colorbar=dict(title="Nota"),
                showscale=True,
                cmin=df_filtrado['Nota'].min(),
                cmax=df_filtrado['Nota'].max()
            ),
            text=[f"{first_row['Título']} Nota: {first_row['Nota']:.1f}"],
            textposition="top center",
            hoverinfo='text'
        )
    )
    
    # Adicionar frames à figura
    fig.frames = frames
    
    # Calcular o range do eixo x para melhor visualização
    date_range = df_filtrado['Conclusão'].max() - df_filtrado['Conclusão'].min()
    x_min = df_filtrado['Conclusão'].min() - (date_range * 0.1)
    x_max = df_filtrado['Conclusão'].max() + (date_range * 0.1)
    
    # Adicionar controles de animação
    fig.update_layout(
        title="Linha do Tempo de Leitura",
        height=600,
        width=800,
        xaxis=dict(
            title="Data de Conclusão",
            range=[x_min, x_max],
            type='date'
        ),
        yaxis=dict(
            title="Livros",
            tickmode='linear',
            tick0=1,
            dtick=1,
            showticklabels=False
        ),
        margin=dict(l=50, r=50, t=100, b=50),  # Aumentado margem superior
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(label="Play",
                         method="animate",
                         args=[None, {"frame": {"duration": 300, "redraw": True},
                                    "fromcurrent": True,
                                    "transition": {"duration": 200}}]),
                    dict(label="Pause",
                         method="animate",
                         args=[[None], {"frame": {"duration": 0, "redraw": False},
                                      "mode": "immediate",
                                      "transition": {"duration": 0}}])
                ],
                x=0.1,
                y=1.2  # Movido para fora do gráfico
            )
        ]
    )
    

    st.plotly_chart(fig)

    # Configuração de cores para as métricas
    st.subheader("Personalização das Estatísticas")
    cores_disponiveis = {
        'Azul': '#0000FF',
        'Verde': '#00FF00',
        'Vermelho': '#FF0000',
        'Roxo': '#800080',
        'Laranja': '#FFA500',
        'Rosa': '#FF69B4',
        'Amarelo': '#FFD700',
        'Ciano': '#00FFFF'
    }
    
    # Seleção de cores para cada métrica
    col1_color, col2_color, col3_color = st.columns(3)
    with col1_color:
        cor_total = st.selectbox('Cor Total de Livros', list(cores_disponiveis.keys()))
    with col2_color:
        cor_media = st.selectbox('Cor Nota Média', list(cores_disponiveis.keys()))
    with col3_color:
        cor_melhor = st.selectbox('Cor Melhor Livro', list(cores_disponiveis.keys()))

    # Estatísticas com cores personalizadas
    st.subheader("Estatísticas de Leitura")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style='padding: 1rem; border-radius: 0.5rem; background-color: {cores_disponiveis[cor_total]}20;'>
            <h3 style='color: {cores_disponiveis[cor_total]}; margin: 0;'>Total de Livros</h3>
            <p style='font-size: 2rem; color: {cores_disponiveis[cor_total]}; margin: 0;'>{len(df_filtrado)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='padding: 1rem; border-radius: 0.5rem; background-color: {cores_disponiveis[cor_media]}20;'>
            <h3 style='color: {cores_disponiveis[cor_media]}; margin: 0;'>Nota Média</h3>
            <p style='font-size: 2rem; color: {cores_disponiveis[cor_media]}; margin: 0;'>{df_filtrado['Nota'].mean():.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        melhor_livro = df_filtrado.loc[df_filtrado['Nota'].idxmax(), 'Título']
        st.markdown(f"""
        <div style='padding: 1rem; border-radius: 0.5rem; background-color: {cores_disponiveis[cor_melhor]}20;'>
            <h3 style='color: {cores_disponiveis[cor_melhor]}; margin: 0;'>Melhor Livro</h3>
            <p style='font-size: 1.5rem; color: {cores_disponiveis[cor_melhor]}; margin: 0;'>{melhor_livro}</p>
        </div>
        """, unsafe_allow_html=True)

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
    tab1, tab2, tab3, tab4,tab5 = st.tabs([
        "Distribuição de Notas e Páginas", 
        "Análise de Gêneros", 
        "Perfil dos Autores", 
        "Tendências de Leitura",
        "Linha do tempo"
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
    with tab5:
        st.header("Linha do tempo")

        criar_linha_tempo_leitura(df)

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
    ano_min, ano_max = min(anos_disponiveis), max(anos_disponiveis)
    
    # Seleção de intervalo de anos com slider
    st.sidebar.subheader("Período de Análise")
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        ano_inicio = st.slider(
            "Ano Inicial",
            min_value=ano_min,
            max_value=ano_max,
            value=ano_min,
            step=1,
            key="ano_inicio"
        )
    
    with col2:
        ano_fim = st.slider(
            "Ano Final",
            min_value=ano_min,
            max_value=ano_max,
            value=ano_max,
            step=1,
            key="ano_fim"
        )
    
    # Verificar se o intervalo é válido
    if ano_inicio > ano_fim:
        st.sidebar.error("O ano inicial não pode ser maior que o ano final!")
        return
    
    # Gerar lista de anos selecionados
    anos_selecionados = list(range(ano_inicio, ano_fim + 1))
    
    # Mostrar anos selecionados
    anos_texto = f"📅 Período selecionado: {ano_inicio} - {ano_fim}"
    st.sidebar.markdown(f"<div style='text-align: center; padding: 10px; background-color: #000000; border-radius: 5px;'>{anos_texto}</div>", unsafe_allow_html=True)
    
    # Filtrar livros
    df_filtrado = filtrar_livros_por_anos(df_preparado, anos_selecionados)


    
    if df_filtrado.empty:
        st.warning("Nenhum livro encontrado no período selecionado.")
        return
    
    # Calcular e mostrar métricas
    metricas = {
        'Total de Livros': len(df_filtrado),
        'Total de Páginas': df_filtrado['Páginas'].sum() if 'Páginas' in df_filtrado.columns else 0,
        'Média de Páginas por Livro': int(round(df_filtrado['Páginas'].mean(), 0)) if 'Páginas' in df_filtrado.columns else 0,
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
df = load_data()

if df is not None:
    try:

        # Streamlit Layout
        st.title('Dashboard: Livros')
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


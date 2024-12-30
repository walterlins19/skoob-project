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
import math
# Paleta de cores para os gráficos
cores_graficos = px.colors.qualitative.Pastel
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
    

def criar_estrelas(df, coluna_notas):
    """
    Cria uma nova coluna com emojis de estrelas baseada nas notas
    
    Parameters:
    df (pandas.DataFrame): DataFrame com as notas
    coluna_notas (str): Nome da coluna que contém as notas
    
    Returns:
    pandas.DataFrame: DataFrame com a nova coluna de estrelas
    """
    def converter_nota_para_estrelas(nota):
        # Arredonda para 0.5 mais próximo
        nota_arredondada = round(nota * 2) / 2
        
        # Separa a parte inteira e decimal
        estrelas_cheias = math.floor(nota_arredondada)
        tem_meia = (nota_arredondada % 1) == 0.5
        
        # Cria a string de estrelas
        estrelas = '⭐' * estrelas_cheias
        if tem_meia:
            estrelas += '✨'
            
        return estrelas
    
    # Cria a nova coluna aplicando a função
    df_copy = df.copy()
    df_copy['estrelas'] = df_copy[coluna_notas].apply(converter_nota_para_estrelas)
    
    return df_copy

def assign_frames(df, date_column):
    """
    Creates a 'frames' column in a DataFrame assigning frame numbers based on date order.
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame
    date_column (str): Name of the date column to use for ordering
    
    Returns:
    pandas.DataFrame: DataFrame with new 'frames' column
    """
    # Make a copy to avoid modifying the original DataFrame
    df_copy = df.copy()
    
    # Sort the DataFrame by date
    df_copy = df_copy.sort_values(by=date_column)
    
    # Create frames column starting from 1 to length of DataFrame
    df_copy['frames'] = range(1, len(df_copy) + 1)
    
    # Return the DataFrame sorted back to its original order
    return df_copy.sort_index()

def criar_timeline_animada_combinada(df):
    """
    Cria uma timeline animada de livros usando Plotly (scatter + line plot) e exibe no Streamlit.

    Args:
        df (pd.DataFrame): DataFrame contendo os dados dos livros, com as colunas:
            'Título', 'Conclusão' (datetime), 'Nota', e outras colunas para personalização.
    """

    # Converter 'Conclusão' para datetime se ainda não for
    df = criar_estrelas(df,'Nota')
    df['Conclusão'] = pd.to_datetime(df['Conclusão'])
    df['Conclusão'] = pd.to_datetime(df['Conclusão']
                            .astype(str)
                            .str[:10],
                            format="%Y-%m-%d") # Control ChatGPT date format output
    df = df.sort_values('Conclusão', ignore_index=True)

    # Ordenar o DataFrame pela data de conclusão
    df_indexed = assign_frames(df,'Conclusão')
    # df_indexed = pd.DataFrame()
    # for index in np.arange(start=0,
    #                    stop=len(df)+1,
    #                    step=1):
    #     df_slicing = df.iloc[:index].copy()
    #     df_slicing['frames'] = (index//1)
    #     df_indexed = pd.concat([df_indexed, df_slicing])



    print(df_indexed)

    # Scatter Plot
    scatter_plot = px.scatter(
        df_indexed,
        x='Conclusão',
        y='Nota',
        color='Título',
        animation_frame='frames'
        #text=df['estrelas']
        #color_discrete_sequence=RETAIL_GROUP_COLORS
    )
    scatter_plot.update_traces(mode="markers+lines", hovertemplate=None)
    scatter_plot.update_layout(hovermode="x")


    for frame in scatter_plot.frames:
        for data in frame.data:
            data.update(mode='markers',
                        showlegend=True,
                        opacity=1)
            data['x'] = np.take(data['x'], [-1])
            data['y'] = np.take(data['y'], [-1])

    # Line Plot
    line_plot = px.line(
        df_indexed,
        x='Conclusão',
        y='Nota',
        color='Título',
        animation_frame='frames',
        #color_discrete_sequence=RETAIL_GROUP_COLORS,
        width=1000,
        height=500,
        line_shape='spline'  # make a line graph curvy
    )
    line_plot.update_traces(showlegend=False)  # legend will be from line graph
    for frame in line_plot.frames:
        for data in frame.data:
            data.update(mode='lines', opacity=0.8, showlegend=False)

    # Stationary combined plot
    combined_plot = go.Figure(
        data=line_plot.data + scatter_plot.data,
        frames=[
            go.Frame(data=line_plot.data + scatter_plot.data, name=scatter_plot.name)
            for line_plot, scatter_plot in zip(line_plot.frames, scatter_plot.frames)
        ],
        layout=line_plot.layout
    )

    combined_plot.update_yaxes(
        gridcolor='#03060d',
        griddash='dot',
        gridwidth=.5,
        linewidth=2,
        tickwidth=2
    )

    combined_plot.update_xaxes(
        title_font=dict(size=16),
        linewidth=2,
        tickwidth=2
    )

    combined_plot.update_traces(
        line=dict(width=5),
        marker=dict(size=25))

    combined_plot.update_layout(
        font=dict(size=18),
        yaxis=dict(tickfont=dict(size=16)),
        xaxis=dict(tickfont=dict(size=16)),
        showlegend=True,
        legend=dict(
            title='Livro'),
        template='simple_white',
        title="<b>Progressão de Notas de Leitura</b>",
        yaxis_title="<b>Nota</b>",
        xaxis_title="<b>Data</b>",
        yaxis_showgrid=True,
        xaxis_range=[df_indexed['Conclusão'].min() - pd.DateOffset(days=5),
                    df_indexed['Conclusão'].max() + pd.DateOffset(days=5)],
        yaxis_range=[df_indexed['Nota'].min() * 0.75,
                    df_indexed['Nota'].max() * 1.25],
        plot_bgcolor='#9c1e2a',
        paper_bgcolor='#1f08a1',
        title_x=0.5
    )

    # adjust speed of animation
    #combined_plot['layout'].pop("sliders")
    combined_plot.layout.updatemenus[0].buttons[0]['args'][1]['frame']['duration'] = 300
    combined_plot.layout.updatemenus[0].buttons[0]['args'][1]['transition']['duration'] = 150
    combined_plot.layout.updatemenus[0].buttons[0]['args'][1]['transition']['redraw'] = False


    # Ajustar as configurações do gráfico para melhor apresentação no Streamlit
    st.plotly_chart(combined_plot)

def criar_linha_tempo_leitura(df):
    """
    Cria uma linha do tempo interativa de leitura com animação, usando Streamlit e Plotly,
    começando no livro mais antigo e progredindo até o mais recente.

    Parâmetros:
    df (pandas.DataFrame): DataFrame com informações de leitura.
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

    # Ordenar por data de conclusão (do mais antigo para o mais novo)
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

    # Configuração inicial do gráfico com o primeiro ponto
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

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go



def criar_visualizacoes_livros(df):
    """
    Cria múltiplas visualizações de dados de livros usando Plotly e Streamlit.

    Args:
        df (pandas.DataFrame): DataFrame com informações dos livros
    """
     # Estilo CSS para as tabs
    st.markdown(
        """
        <style>
        div[data-baseweb="tab"] > div {
        
            border-radius: 6px 6px 0px 0px;
            background-color: #3498db;
            color: white;
            padding: 8px;
            margin-bottom: -1px;
          }
        
        div[data-baseweb="tab"]:first-child > div {
           background-color: #e74c3c; /* Vermelho para a primeira tab*/
         }
        
        div[data-baseweb="tab"]:nth-child(2) > div {
            background-color: #2ecc71; /* Verde para a segunda tab */
        }
        div[data-baseweb="tab"]:nth-child(3) > div {
            background-color: #f39c12; /* Laranja para a terceira tab */
        }
        div[data-baseweb="tab"]:nth-child(4) > div {
            background-color: #9b59b6; /* Roxo para a quarta tab */
        }
        div[data-baseweb="tab"]:nth-child(5) > div {
            background-color: #34495e; /* Azul escuro para a quinta tab */
        }

        
        div[data-baseweb="tab"].selected div {
            background-color: white !important;
            color: black !important;
           }
        
        
        </style>
        """,
        unsafe_allow_html=True,
    )
    # Título da página
    st.title("📊 Análise Detalhada de Leitura")

    # Divide a página em colunas
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Estatísticas Gerais",
        "Análise de Gêneros",
        "Perfil dos Autores",
        "Tendências de Leitura",
        "Geográfico",
    ])

    with tab1:
        st.header("Estatísticas Gerais dos Livros")

        st.subheader("Resumo dos Livros")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📚 Livros Lidos", df.shape[0])
        with col2:
            st.metric("📖 Páginas Totais", df['Páginas'].sum())
        with col3:
            st.metric("📏 Média de Páginas", f"{df['Páginas'].mean():.0f}")

        col4, col5, col6 = st.columns(3)
        with col4:
            st.metric("💯 Nota média", f"{df['Nota'].mean():.1f}")
        with col5:
            st.metric("🌎 Países", df['País'].nunique())
        with col6:
            st.metric("✍️ Autores", df['Autor'].nunique())
        st.subheader("Livros em Destaque")
        col_maior, col_menor = st.columns(2)
        with col_maior:
            maior_livro = df.loc[df['Páginas'].idxmax()]
            st.markdown(f"**Livro Mais Longo:**")
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 1.2em;">📚</span>
                    <span style="margin-left: 5px;"><strong>{maior_livro['Título']}</strong></span>
                </div>
                <div><span style="font-size: 1em;">📖</span> <span style="margin-left: 5px;"><em>Páginas: {maior_livro['Páginas']}</em></span></div>
                """, unsafe_allow_html=True
            )
            
        with col_menor:
            menor_livro = df.loc[df['Páginas'].idxmin()]
            st.markdown(f"**Livro Mais Curto:**")
            st.markdown(
                    f"""
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 1.2em;">📖</span>
                    <span style="margin-left: 5px;"><strong>{menor_livro['Título']}</strong></span>
                    </div>
                <div><span style="font-size: 1em;">📄</span> <span style="margin-left: 5px;"><em>Páginas: {menor_livro['Páginas']}</em></span></div>
                """, unsafe_allow_html=True
            )
        
        # --- Mais Antigo vs Mais Novo ---
        col_antigo, col_novo= st.columns(2)
        with col_antigo:
            mais_antigo = df.loc[df['Ano de Publicação'].idxmin()]
            st.markdown(f"**Livro Mais Antigo:**")
            st.markdown(
                    f"""
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 1.2em;">🕰️</span>
                    <span style="margin-left: 5px;"><strong>{mais_antigo['Título']}</strong></span>
                    </div>
                <div><span style="font-size: 1em;">🗓️</span> <span style="margin-left: 5px;"><em>Ano: {mais_antigo['Ano de Publicação']}</em></span></div>
                """, unsafe_allow_html=True
            )
        with col_novo:
            mais_novo = df.loc[df['Ano de Publicação'].idxmax()]
            st.markdown(f"**Livro Mais Recente:**")
            st.markdown(
                    f"""
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 1.2em;">🆕</span>
                        <span style="margin-left: 5px;"><strong>{mais_novo['Título']}</strong></span>
                    </div>
                    <div><span style="font-size: 1em;">🗓️</span> <span style="margin-left: 5px;"><em>Ano: {mais_novo['Ano de Publicação']}</em></span></div>
                """, unsafe_allow_html=True
            )
        st.subheader("Diversidade de Leituras")
        col_metric1, col_metric2= st.columns(2)
# --- Métricas Ficção vs Não Ficção ---
        with col_metric1:
            total_books = len(df)
            
            # Calculate counts and percentages for Fiction
            ficcao_count = df['Ficção'].value_counts().get('Sim', 0)
            ficcao_percentage = (ficcao_count / total_books * 100) if total_books > 0 else 0
            
            # Calculate counts and percentages for Non-Fiction
            nao_ficcao_count = df['Autor/Temática LGBTQIA+?'].value_counts().get('Sim', 0)
            nao_ficcao_percentage = (nao_ficcao_count / total_books * 100) if total_books > 0 else 0
            
            # Display metrics with percentages as deltas
            st.metric(
                label="📚 Ficção", 
                value=ficcao_count,
                delta=f"{ficcao_percentage:.1f}% do total"
            )
            
            st.metric(
                label="🌈 LGBT", 
                value=nao_ficcao_count,
                delta=f"{nao_ficcao_percentage:.1f}% do total"
            )

        # --- Métricas Negro vs Branco ---
        with col_metric2:
            if 'Etnia' in df.columns:
                # Calculate counts and percentages for Black authors
                negro_count = df['Etnia'].value_counts().get('Negra', 0)
                total_books = len(df)
                negro_percentage = (negro_count / total_books * 100) if total_books > 0 else 0
                
                # Calculate counts and percentages for Women authors
                mulheres_count = df['Sexo Autor'].value_counts().get('F', 0)  # Assuming 'F' for Female
                mulheres_percentage = (mulheres_count / total_books * 100) if total_books > 0 else 0
                
                # Display metrics with percentages as deltas
                st.metric(
                    label="🔳 Autores Negros", 
                    value=negro_count,
                    delta=f"{negro_percentage:.1f}% do total"
                )
                
                st.metric(
                    label="👩 Autores Mulheres", 
                    value=mulheres_count,
                    delta=f"{mulheres_percentage:.1f}% do total"
                )

        # --- Distribuição em Gêneros ---
        st.subheader("Distribuição de Gêneros")
        genero_counts = df['Gênero'].value_counts()
        fig_generos = px.pie(
            values=genero_counts.values, 
            names=genero_counts.index,
             title=f'📚 Distribuição de Livros por Gênero 📚',
            color_discrete_sequence=cores_graficos,
        )
        fig_generos.update_traces(textinfo='percent+label', textfont_size=12)
        st.plotly_chart(fig_generos, use_container_width=True, key="tab1_generos_pie")

         # --- Distribuição das Notas ---
        st.subheader("Distribuição das Notas")
        fig_notas = px.histogram(
            df,
            x='Nota',
            title=f'📊 Distribuição das Notas Atribuídas 💯',
            labels={'Nota': 'Nota do Livro'},
            color_discrete_sequence=cores_graficos,
        )
        st.plotly_chart(fig_notas, use_container_width=True, key="tab1_notas_hist")
        
        # --- Maior vs Menor Livro ---
        
    with tab2:
        st.header("Análise de Gêneros Literários")

        # Gráfico de contagem de livros por gênero
        col_etnia, col_genero = st.columns(2)
        with col_genero:
            genero_counts = df['Gênero'].value_counts()
            fig_generos = px.pie(
                values=genero_counts.values,
                names=genero_counts.index,
                title=f'📚 Distribuição de Livros por Gênero 📚',
                color_discrete_sequence=cores_graficos,
            )
            fig_generos.update_traces(textinfo='percent+label', textfont_size=12)
            st.plotly_chart(fig_generos, use_container_width=True, key="tab2_generos_pie")

        # Gráfico de médias de notas por gênero
        with col_etnia:
            notas_por_genero = df.groupby('Gênero')['Nota'].mean().sort_values(ascending=False)
            fig_notas_genero = px.bar(
                x=notas_por_genero.index,
                y=notas_por_genero.values,
                title=f'⭐ Média de Notas por Gênero 🌟',
                labels={'x': 'Gênero', 'y': 'Média da Nota'},
                color_discrete_sequence=cores_graficos,
            )
            st.plotly_chart(fig_notas_genero, use_container_width=True, key="tab2_notas_genero_bar")

    with tab3:
        st.header("Perfil dos Autores")
        
         # Distribuição de autores por sexo
        sexo_autor_counts = df['Sexo Autor'].value_counts()
        fig_sexo_autor = px.pie(
            values=sexo_autor_counts.values, 
            names=sexo_autor_counts.index,
            title=f'🚻 Distribuição de Livros por Sexo do Autor 🚻',
            color_discrete_sequence=cores_graficos,
        )
        fig_sexo_autor.update_traces(textinfo='percent+label', textfont_size=12)
        st.plotly_chart(fig_sexo_autor, use_container_width=True, key="tab3_sexo_autor_pie")
        
        # Gráfico de etnia dos autores
        etnia_counts = df['Etnia'].value_counts()
        fig_etnia = px.bar(
            x=etnia_counts.index, 
            y=etnia_counts.values,
             title=f'🌍 Número de Livros por Etnia do Autor 🌍',
            labels={'x': 'Etnia', 'y': 'Número de Livros'},
            color_discrete_sequence=cores_graficos,
        )
        st.plotly_chart(fig_etnia, use_container_width=True, key="tab3_etnia_bar")


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
             title=f'📅 Número de Livros Lidos por Mês 📚',
            labels={'x': 'Mês', 'y': 'Número de Livros'},
            color_discrete_sequence=cores_graficos,
        )
        st.plotly_chart(fig_livros_mes, use_container_width=True, key="tab4_livros_mes_line")

        # Gráfico de páginas lidas por mês
        paginas_por_mes = df.groupby('Mês Conclusão')['Páginas'].sum()
        fig_paginas_mes = px.bar(
            x=paginas_por_mes.index.astype(str),
            y=paginas_por_mes.values,
            title=f'📖 Total de Páginas Lidas por Mês 🗓️',
            labels={'x': 'Mês', 'y': 'Número de Páginas'},
             color_discrete_sequence=cores_graficos,
        )
        st.plotly_chart(fig_paginas_mes, use_container_width=True, key="tab4_paginas_mes_bar")
    
    with tab5:
        st.header("Análise Geográfica")
        
        # Estatísticas Geográficas
        st.subheader("Estatísticas Geográficas")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Número de Países", df['País'].nunique())
        with col2:
           mais_lido = df['País'].value_counts().idxmax() if not df['País'].value_counts().empty else 'N/A'
           st.metric("País Mais Lido", mais_lido)
        with col3:
            st.metric("Número de Continentes", df['Região'].nunique())
        
        # Continente Mais Lido
        st.subheader("Continente Mais Lido")
        continente_mais_lido = df['Região'].value_counts().idxmax() if not df['Região'].value_counts().empty else 'N/A'
        st.markdown(f"**O continente mais lido é:** {continente_mais_lido}")
        
        # Distribuição por Regiões
        st.subheader("Distribuição de Livros por Região")
        regiao_counts = df['Região'].value_counts()
        fig_regioes = px.pie(
            values=regiao_counts.values,
            names=regiao_counts.index,
            title=f'🗺️ Distribuição de Livros por Região 🌍',
            color_discrete_sequence=cores_graficos,
        )
        fig_regioes.update_traces(textinfo='percent+label', textfont_size=12)
        st.plotly_chart(fig_regioes, use_container_width=True, key="tab5_regioes_pie")
    
    
        



    with tab2:
        st.header("Análise de Gêneros Literários")

        # Gráfico de contagem de livros por gênero
        col_etnia, col_genero = st.columns(2)
        with col_genero:
            genero_counts = df['Gênero'].value_counts()
            fig_generos = px.pie(
                values=genero_counts.values,
                names=genero_counts.index,
                title=f'📚 Distribuição de Livros por Gênero 📚',
                color_discrete_sequence=cores_graficos,
            )
            fig_generos.update_traces(textinfo='percent+label', textfont_size=12)
            st.plotly_chart(fig_generos, use_container_width=True, key="tab2_generos_pie")

        # Gráfico de médias de notas por gênero
        with col_etnia:
            notas_por_genero = df.groupby('Gênero')['Nota'].mean().sort_values(ascending=False)
            fig_notas_genero = px.bar(
                x=notas_por_genero.index,
                y=notas_por_genero.values,
                title=f'⭐ Média de Notas por Gênero 🌟',
                labels={'x': 'Gênero', 'y': 'Média da Nota'},
                color_discrete_sequence=cores_graficos,
            )
            st.plotly_chart(fig_notas_genero, use_container_width=True, key="tab2_notas_genero_bar")

    with tab3:
        st.header("Perfil dos Autores")
        
         # Distribuição de autores por sexo
        sexo_autor_counts = df['Sexo Autor'].value_counts()
        fig_sexo_autor = px.pie(
            values=sexo_autor_counts.values, 
            names=sexo_autor_counts.index,
            title=f'🚻 Distribuição de Livros por Sexo do Autor 🚻',
            color_discrete_sequence=cores_graficos,
        )
        fig_sexo_autor.update_traces(textinfo='percent+label', textfont_size=12)
        st.plotly_chart(fig_sexo_autor, use_container_width=True, key="tab3_sexo_autor_pie")
        
        # Gráfico de etnia dos autores
        etnia_counts = df['Etnia'].value_counts()
        fig_etnia = px.bar(
            x=etnia_counts.index, 
            y=etnia_counts.values,
             title=f'🌍 Número de Livros por Etnia do Autor 🌍',
            labels={'x': 'Etnia', 'y': 'Número de Livros'},
            color_discrete_sequence=cores_graficos,
        )
        st.plotly_chart(fig_etnia, use_container_width=True, key="tab3_etnia_bar")


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
             title=f'📅 Número de Livros Lidos por Mês 📚',
            labels={'x': 'Mês', 'y': 'Número de Livros'},
            color_discrete_sequence=cores_graficos,
        )
        st.plotly_chart(fig_livros_mes, use_container_width=True, key="tab4_livros_mes_line")

        # Gráfico de páginas lidas por mês
        paginas_por_mes = df.groupby('Mês Conclusão')['Páginas'].sum()
        fig_paginas_mes = px.bar(
            x=paginas_por_mes.index.astype(str),
            y=paginas_por_mes.values,
            title=f'📖 Total de Páginas Lidas por Mês 🗓️',
            labels={'x': 'Mês', 'y': 'Número de Páginas'},
             color_discrete_sequence=cores_graficos,
        )
        st.plotly_chart(fig_paginas_mes, use_container_width=True, key="tab4_paginas_mes_bar")
    
    with tab5:
        st.header("Análise Geográfica")
        
        # Estatísticas Geográficas
        st.subheader("Estatísticas Geográficas")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Número de Países", df['País'].nunique())
        with col2:
           mais_lido = df['País'].value_counts().idxmax() if not df['País'].value_counts().empty else 'N/A'
           st.metric("País Mais Lido", mais_lido)
        with col3:
            st.metric("Número de Continentes", df['Região'].nunique())
        
        # Continente Mais Lido
        st.subheader("Continente Mais Lido")
        continente_mais_lido = df['Região'].value_counts().idxmax() if not df['Região'].value_counts().empty else 'N/A'
        st.markdown(f"**O continente mais lido é:** {continente_mais_lido}")
        
        # Distribuição por Regiões
        st.subheader("Distribuição de Livros por Região")
        regiao_counts = df['Região'].value_counts()
        fig_regioes = px.pie(
            values=regiao_counts.values,
            names=regiao_counts.index,
            title=f'🗺️ Distribuição de Livros por Região 🌍',
            color_discrete_sequence=cores_graficos,
        )
        fig_regioes.update_traces(textinfo='percent+label', textfont_size=12)
        st.plotly_chart(fig_regioes, use_container_width=True, key="tab5_regioes_pie")

    



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


def criar_metricas_livros(df):
    """
    Cria métricas e visualizações para um DataFrame de livros no Streamlit
    
    Parameters:
    df (pandas.DataFrame): DataFrame com as informações dos livros
    """
    # Converter colunas para tipos apropriados
    df['Ano de Publicação'] = pd.to_numeric(df['Ano de Publicação'], errors='coerce')
    df['Páginas'] = pd.to_numeric(df['Páginas'], errors='coerce')
    df['Nota'] = pd.to_numeric(df['Nota'], errors='coerce')
    
    # Layout de métricas em colunas
    col1, col2, col3, col4 = st.columns(4)
    
    # Métricas básicas
    with col1:
        st.metric("Total de Livros", len(df))
        
    with col2:
        media_paginas = df['Páginas'].mean()
        st.metric("Média de Páginas", f"{media_paginas:.0f}")
        
    with col3:
        media_nota = df['Nota'].mean()
        st.metric("Média das Notas", f"{media_nota:.1f}")
        
    with col4:
        total_paginas = df['Páginas'].sum()
        st.metric("Total de Páginas Lidas", f"{total_paginas:,.0f}")
    
    # Segunda linha de métricas com cards expandidos
    st.markdown("## Métricas de Livros")
    st.markdown("### Mais novo e mais velho")
    col5, col6= st.columns(2)

    with col5:
        livro_mais_velho = df.loc[df['Ano de Publicação'].idxmin()]
        with st.container():
            st.metric("Livro Mais Antigo", f"{livro_mais_velho['Ano de Publicação']:.0f}")
            st.markdown(f"**Título:** {livro_mais_velho['Título']}")
            st.markdown(f"**Autor:** {livro_mais_velho['Autor']}")
        
    with col6:
        livro_mais_novo = df.loc[df['Ano de Publicação'].idxmax()]
        with st.container():
            st.metric("Livro Mais Recente", f"{livro_mais_novo['Ano de Publicação']:.0f}")
            st.markdown(f"**Título:** {livro_mais_novo['Título']}")
            st.markdown(f"**Autor:** {livro_mais_novo['Autor']}")
        
    st.markdown("### Maior e Menor")
    col7, col8= st.columns(2)

    with col7:
        maior_livro = df.loc[df['Páginas'].idxmax()]
        with st.container():
            st.metric("Maior Livro", f"{maior_livro['Páginas']:.0f} págs")
            st.markdown(f"**Título:** {maior_livro['Título']}")
            st.markdown(f"**Autor:** {maior_livro['Autor']}")

        
    with col8:
        menor_livro = df.loc[df['Páginas'].idxmin()]
        with st.container():
            st.metric("Menor Livro", f"{menor_livro['Páginas']:.0f} págs")
            st.markdown(f"**Título:** {menor_livro['Título']}")
            st.markdown(f"**Autor:** {menor_livro['Autor']}")
    
    # Distribuição das Notas
    st.markdown("### Distribuição das Notas")
    fig_notas = px.histogram(df, x='Nota', nbins=10, 
                            title="Distribuição das Notas",
                            color_discrete_sequence=['#1f77b4'])
    st.plotly_chart(fig_notas, use_container_width=True)
    
    # Análises por categoria
    col9, col10 = st.columns(2)
    
    with col9:
        st.subheader("Top 5 Gêneros")
        generos = df['Gênero'].value_counts().head()
        fig_generos = px.bar(x=generos.index, y=generos.values,
                            title="Top 5 Gêneros",
                            color_discrete_sequence=['#2ecc71'])
        st.plotly_chart(fig_generos, use_container_width=True)
        
    with col10:
        st.subheader("Top 5 Países")
        paises = df['País'].value_counts().head()
        fig_paises = px.bar(x=paises.index, y=paises.values,
                           title="Top 5 Países",
                           color_discrete_sequence=['#e74c3c'])
        st.plotly_chart(fig_paises, use_container_width=True)
    
    # Análises adicionais com pie charts
    col11, col12 = st.columns(2)
    
    with col11:
        st.subheader("Distribuição por Sexo do Autor")
        sexo_autor = df['Sexo Autor'].value_counts()
        fig_sexo = px.pie(values=sexo_autor.values, 
                         names=sexo_autor.index,
                         title="Distribuição por Sexo do Autor")
        st.plotly_chart(fig_sexo, use_container_width=True)
        
    with col12:
        st.subheader("Ficção vs Não-Ficção")
        ficcao = df['Ficção'].value_counts()
        fig_ficcao = px.pie(values=ficcao.values, 
                           names=ficcao.index,
                           title="Ficção vs Não-Ficção")
        st.plotly_chart(fig_ficcao, use_container_width=True)
    
    # Métricas de diversidade
    st.subheader("Distribuição por Etnia")
    etnia_count = df['Etnia'].value_counts()
    fig_etnia = px.bar(x=etnia_count.index, y=etnia_count.values,
                       title="Distribuição por Etnia",
                       color_discrete_sequence=['#9b59b6'])
    st.plotly_chart(fig_etnia, use_container_width=True)
    
    # Média de notas por década
    st.subheader("Média de Notas por Década")
    df['Década'] = (df['Ano de Publicação'] // 10) * 10
    notas_decada = df.groupby('Década')['Nota'].mean().round(2)
    fig_decada = px.line(x=notas_decada.index, y=notas_decada.values,
                        title="Média de Notas por Década",
                        labels={'x': 'Década', 'y': 'Nota Média'})
    st.plotly_chart(fig_decada, use_container_width=True)


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
    print(df_filtrado['Ano de Publicação'])


    
    if df_filtrado.empty:
        st.warning("Nenhum livro encontrado no período selecionado.")
        return
    
    # Calcular e mostrar métricas
    metricas = {
        'Total de Livros': len(df_filtrado),
        'Total de Páginas': df_filtrado['Páginas'].sum() if 'Páginas' in df_filtrado.columns else 0,
        'Média de Páginas por Livro': int(round(df_filtrado['Páginas'].mean(), 0)) if 'Páginas' in df_filtrado.columns else 0,
        'Nota média': df_filtrado['Nota'].mean() if 'Nota' in df_filtrado.columns else 0
    }
    #criar_cards_metricas(metricas)
    #criar_metricas_livros(df_filtrado)
    
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
        'Nota média': '👥'
    }
    
    cores_metricas = {
        'Total de Livros': 'background-color: #3498db; color: white;',
        'Total de Páginas': 'background-color: #2ecc71; color: white;',
        'Média de Páginas por Livro': 'background-color: #e74c3c; color: white;',
        'Nota média': 'background-color: #f39c12; color: white;'
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


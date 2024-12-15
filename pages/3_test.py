import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def calcular_metricas_livros(df):
    """
    Calcula métricas principais do DataFrame de livros.
    
    Args:
        df (pandas.DataFrame): DataFrame com informações dos livros
    
    Returns:
        dict: Dicionário com métricas calculadas
    """
    metricas = {
        'Total de Livros': len(df),
        'Total de Páginas': df['Número de Páginas'].sum() if 'Número de Páginas' in df.columns else 0,
        'Média de Páginas por Livro': round(df['Número de Páginas'].mean(), 2) if 'Número de Páginas' in df.columns else 0,
        'Número de Autores Únicos': df['Autor'].nunique() if 'Autor' in df.columns else 0
    }
    
    return metricas

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

def criar_grafico_distribuicao_paginas(df):
    """
    Cria um gráfico de distribuição do número de páginas dos livros.
    
    Args:
        df (pandas.DataFrame): DataFrame com informações dos livros
    """
    if 'Número de Páginas' not in df.columns:
        st.warning("Coluna 'Número de Páginas' não encontrada.")
        return
    
    st.subheader("Distribuição do Número de Páginas")
    
    # Gráfico de histograma interativo
    fig = px.histogram(df, x='Número de Páginas', 
                       title='Distribuição de Páginas por Livro',
                       labels={'Número de Páginas': 'Número de Páginas'},
                       color_discrete_sequence=['#3498db'])
    
    fig.update_layout(
        xaxis_title='Número de Páginas',
        yaxis_title='Número de Livros'
    )
    
    st.plotly_chart(fig)

def dashboard_livros(df):
    """
    Cria um dashboard completo de métricas de livros.
    
    Args:
        df (pandas.DataFrame): DataFrame com informações dos livros
    """
    st.title("📊 Dashboard de Livros")
    
    # Calcular métricas
    metricas = calcular_metricas_livros(df)
    
    # Criar cards de métricas
    criar_cards_metricas(metricas)
    
    # Adicionar espaço
    st.markdown("---")
    
    # Criar gráfico de distribuição de páginas
    criar_grafico_distribuicao_paginas(df)

# Exemplo de uso
def main():
    # Exemplo de DataFrame (substitua pelo seu DataFrame real)
    df_exemplo = pd.DataFrame({
        'Título': ['Moby Dick', 'Dom Quixote', '1984', 'O Pequeno Príncipe'],
        'Autor': ['Herman Melville', 'Miguel de Cervantes', 'George Orwell', 'Antoine de Saint-Exupéry'],
        'Número de Páginas': [720, 863, 336, 96]
    })
    
    # Criar dashboard
    dashboard_livros(df_exemplo)

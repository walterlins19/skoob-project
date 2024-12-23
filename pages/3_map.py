import streamlit as st
import pandas as pd
import plotly.express as px
import pycountry
import unidecode
import difflib
import pycountry_convert as pc

import numpy as np





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
# Inicializa o tradutor do googletrans

def get_continent(iso_code):
    """Retorna o continente baseado no código ISO do país"""
    try:
        continent_code = pc.country_alpha2_to_continent_code(iso_code)
        continent_name = pc.convert_continent_code_to_continent_name(continent_code)
        return continent_name
    except:
        return "Desconhecido"
    
def create_stats_cards(df_paises):
    """Cria cards com estatísticas gerais"""
    
    # Adiciona coluna de continente
    df_paises['Continente'] = df_paises['Codigo_ISO'].apply(get_continent)
    
    # Layout de 3 colunas para os cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total de Países",
            value=len(df_paises),
            delta=f"{len(df_paises['Continente'].unique())} Continentes"
        )
    
    with col2:
        total_livros = df_paises['Quantidade_Livros'].sum()
        media_livros = df_paises['Quantidade_Livros'].mean()
        st.metric(
            label="Total de Livros",
            value=f"{total_livros:,.0f}",
            delta=f"Média: {media_livros:,.1f} por país"
        )
    
    with col3:
        pais_mais_livros = df_paises.loc[df_paises['Quantidade_Livros'].idxmax(), 'País']
        max_livros = df_paises['Quantidade_Livros'].max()
        st.metric(
            label="País com Mais Livros",
            value=pais_mais_livros,
            delta=f"{max_livros:,.0f} livros"
        )
    


def preparar_dados_mapa_livros(df_livros):
    """
    Prepara dados de livros para visualização no mapa mundial
    
    Parâmetros:
    df_livros (pandas.DataFrame): DataFrame original com informações dos livros
        Colunas esperadas:
        - País: Nome do país de publicação
        - Nota: Nota do livro
        - Título ou colunas adicionais que identifiquem o livro
    
    Retorna:
    pandas.DataFrame: DataFrame agregado com informações por país
    """
    # Verificar colunas necessárias
    colunas_necessarias = ['País', 'Nota']
    print(df_livros)
    for coluna in colunas_necessarias:
        if coluna not in df_livros.columns:
            raise ValueError(f"Coluna '{coluna}' não encontrada no DataFrame")
    
    # Dicionário de mapeamento de países para códigos ISO
    # Adicione mais países conforme necessário
    
    # Identificar o livro com maior nota por país
    def encontrar_livro_top(grupo):
        livro_top = grupo.loc[grupo['Nota'].idxmax()]
        return pd.Series({
            'Quantidade_Livros': len(grupo),
            'Livro_Maior_Nota': livro_top['Título'] if 'Título' in grupo.columns else 'N/A',
            'Maior_Nota': livro_top['Nota']
        })
    
    # Agregar dados por país
    df_paises = df_livros.groupby('País').apply(encontrar_livro_top).reset_index()
    
    # Adicionar código ISO à agregação
    df_paises['Codigo_ISO'] = df_paises['País'].apply(obter_codigo_iso)
    #df_paises = completar_paises_com_zero(df_paises)
    # Remover países sem código ISO
    df_paises = df_paises.dropna(subset=['Codigo_ISO'])
    
    return df_paises

def obter_codigo_iso(pais):
    """
    Obtém o código ISO alpha-3 de um país, lidando com variações de nome
    
    Parâmetros:
    pais (str): Nome do país em português
    
    Retorna:
    str: Código ISO alpha-3 do país ou None se não encontrado
    """
    # Remover acentos e converter para maiúsculas para comparação
    pais_normalizado = unidecode.unidecode(pais.upper().strip())
    
    # Dicionário de mapeamentos especiais
    mapeamentos_especiais = {
        'RUSSIA': 'RUS',
        'UNIAO SOVIETICA': 'SUN',
        'ESTADOS UNIDOS': 'USA',
        'REINO UNIDO': 'GBR',
        'COREIA DO SUL': 'KOR',
        'COREIA DO NORTE': 'PRK',
        'REPUBLICA TCHECA': 'CZE',
        'ARABIA SAUDITA': 'SAU',
        'EMIRADOS ARABES UNIDOS': 'ARE',
        'ESPANHA': 'ESP',
        'REPUBLICA DOMINICANA': 'DOM',
        'REPUBLICA DOMINICANA DA': 'DOM',
        # Adicione mais mapeamentos conforme necessário
    }
    
    # Verificar mapeamentos especiais primeiro
    if pais_normalizado in mapeamentos_especiais:
        return mapeamentos_especiais[pais_normalizado]
    
    # Tentativas de encontrar o código ISO
    tentativas = [
        # 1. Tentar com traduções padrão
        pais.title(),  # Primeira letra maiúscula
        pais.upper(),  # Maiúsculas
        pais.lower(),  # Minúsculas
    ]
    
    # Adicionar variações sem acentos
    tentativas.extend([
        unidecode.unidecode(p) for p in tentativas
    ])
    
    # Adicionar algumas variações comuns
    variacoes = {
        'UNIAO': 'UNION',
        'SUL': 'SOUTH',
        'NORTE': 'NORTH',
        'REPUBLICA': 'REPUBLIC'
    }
    
    for variacao, substituicao in variacoes.items():
        tentativas.extend([
            p.replace(variacao, substituicao) for p in tentativas
        ])
    
    # Função para buscar país usando pycountry
    def buscar_pais(nome):
        try:
            # Tentar encontrar pelo nome
            country = pycountry.countries.get(name=nome)
            if country:
                return country.alpha_3
            
            # Se não encontrar, tentar pela busca difusa
            paises = list(pycountry.countries)
            matches = difflib.get_close_matches(nome, [p.name for p in paises], n=1, cutoff=0.6)
            
            if matches:
                country = next((p for p in paises if p.name == matches[0]), None)
                return country.alpha_3 if country else None
        except Exception as e:
            print(f"Erro ao buscar o código para {nome}: {e}")
        return None
    
    # Tentar encontrar o código ISO
    for tentativa in tentativas:
        codigo = buscar_pais(tentativa)
        if codigo:
            return codigo
    
    # Se não encontrar, imprimir aviso
    print(f"Código ISO não encontrado para: {pais}")
    return None
def add_flag_emoji(df, iso_column='Codigo_ISO'):
    """
    Adds a column with flag emojis to a DataFrame based on ISO country codes.
    
    Parameters:
    df (pandas.DataFrame): DataFrame containing country information
    iso_column (str): Name of the column containing ISO country codes
    
    Returns:
    pandas.DataFrame: DataFrame with new 'flag' column
    """
    def get_flag_emoji(iso_code):
        if pd.isna(iso_code):
            return ''
            
        # Convert ISO code to uppercase regional indicator symbols
        # Regional indicator symbols are 127397 code points after uppercase letters
        iso_code = iso_code.upper()
        return ''.join(chr(ord(c) + 127397) for c in iso_code)
    
    # Create a copy to avoid modifying the original DataFrame
    result = df.copy()
    
    # Add the flag column
    result['flag'] = result[iso_column].apply(get_flag_emoji)
    
    return result

def mapear_cor(quantidade):
    if quantidade == 0:
        return "rgb(255, 255, 255)"  # Branco (sem livros)
    elif quantidade <= 5:
        return "rgb(255, 255, 204)"  # Amarelo claro
    elif quantidade <= 10:
        return "rgb(255, 255, 102)"  # Amarelo mais forte
    elif quantidade <= 15:
        return "rgb(255, 204, 0)"    # Amarelo-ouro
    elif quantidade <= 20:
        return "rgb(255, 153, 0)"    # Laranja
    elif quantidade <= 25:
        return "rgb(255, 102, 0)"    # Laranja forte
    elif quantidade <= 30:
        return "rgb(255, 51, 0)"     # Laranja-avermelhado
    elif quantidade <= 35:
        return "rgb(255, 0, 0)"      # Vermelho
    elif quantidade <= 40:
        return "rgb(204, 0, 0)"      # Vermelho escuro
    else:
        return "rgb(139, 0, 0)"      # Vermelho sangue



def criar_mapa_livros_mundial(df_paises):
    """
    Cria mapa mundial de livros por país com bandeiras no hover e escala de cores suavizada
    
    Parâmetros:
    df_paises (pandas.DataFrame): DataFrame agregado de livros por país
    
    Retorna:
    plotly.graph_objs.Figure: Mapa mundi interativo com bandeiras
    """
    
    def normalize_with_log(series):
        """
        Normaliza os valores usando log para suavizar outliers
        """
        # Adiciona 1 para evitar log(0)
        log_values = np.log1p(series)
        # Normaliza para [0,1]
        return (log_values - log_values.min()) / (log_values.max() - log_values.min())
    
    # Adiciona emojis de bandeira
    df_paises = add_flag_emoji(df_paises)
    
    # Normaliza a quantidade de livros usando log scale
    df_paises['normalized_books'] = normalize_with_log(df_paises['Quantidade_Livros'])
    
    # Crie o mapa coroplético
    fig = px.choropleth(
        df_paises, 
        locations="Codigo_ISO",
        color="Quantidade_Livros",
        hover_name="flag",
        hover_data={
            'normalized_books': False,  # Esconde a coluna normalizada
            'País': True,
            'Quantidade_Livros': True,
            'Maior_Nota': ':.1f',
            'Livro_Maior_Nota': True,
            'flag': False,
            'Codigo_ISO': False
        },
        color_continuous_scale='Sunset',  # Usa uma escala de azuis mais suave
        labels={'normalized_books': 'Quantidade de Livros', 'Maior_Nota': 'Maior Nota', 'Livro_Maior_Nota': 'Livro com a maior nota','Quantidade_Livros': 'Quantidade de livros'}  # Renomeia a legenda
    )
    
    # Personalize o layout
    fig.update_layout(
        title={
            'text': 'Publicações de Livros por País',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24}
        },
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular',
            showcountries=True,
            countrycolor='rgba(128, 128, 128, 0.3)',  # Cor mais suave para as bordas
            coastlinecolor='rgba(128, 128, 128, 0.3)',
            showland=True,
            landcolor='rgba(250, 250, 250, 0.95)'
        ),
        height=600,
        width=1000,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    # Atualiza a barra de cores
    fig.update_coloraxes(
        colorbar_title="Quantidade<br>de Livros",
        colorbar_thickness=15,
        colorbar_len=0.7,
        colorbar_title_font_size=12,
        colorbar_tickfont_size=10,
        showscale=True
    )
    
    return fig
    
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

def main():
    # Configuração da página
    st.set_page_config(
        page_title="Skoob-Doo Map",
        page_icon="🗺️",
        layout="wide"
    )
    
    # Título e descrição
    st.title("🗺️ Mapa dos seus livros")
    st.write("Visualize a distribuição global dos seus livros lidos")
    
    # Carregar dados
    df = load_data()
    df_paises = preparar_dados_mapa_livros(df)
    if df_paises is not None:
        # Botão para gerar visualização
        if st.button("Gerar Visualização", type="primary"):
            with st.spinner("Gerando visualizações..."):
                # Preparar dados

                
                # Container para estatísticas
                st.subheader("📊 Estatísticas Gerais")
                create_stats_cards(df_paises)
                
                # Container para o mapa
                st.subheader("🌎 Distribuição Global")
                fig = criar_mapa_livros_mundial(df_paises)
                st.plotly_chart(fig, use_container_width=True)
                
                # Adicionar download dos dados
                csv = df_paises.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download dos dados",
                    data=csv,
                    file_name="livros_por_pais.csv",
                    mime="text/csv"
                )
    else:
        st.error("Não foi possível carregar os dados. Verifique se o arquivo está disponível.")

main()





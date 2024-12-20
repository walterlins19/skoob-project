import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.express as px
import pycountry
import unidecode
import difflib

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
    Cria mapa mundial de livros por país
    
    Parâmetros:
    df_paises (pandas.DataFrame): DataFrame agregado de livros por país
    
    Retorna:
    plotly.graph_objs.Figure: Mapa mundi interativo
    """

    # Criar uma coluna de cores mapeadas
    df_paises['Cor_Livros'] = df_paises['Quantidade_Livros'].apply(mapear_cor)
    media = df_paises['Quantidade_Livros'].mean()
    # Crie o mapa coroplético
    fig = px.choropleth(
        df_paises, 
        locations="Codigo_ISO",
        color="Cor_Livros",
        hover_name="Livro_Maior_Nota", 
        color_discrete_map={cor: cor for cor in df_paises['Cor_Livros'].unique()},
        hover_data={
            "Codigo_ISO": False,  # Esconde o código ISO
            "Quantidade_Livros": ":.0f",  # Formata número de livros sem casas decimais
            "Maior_Nota": ":.2f",  # Mostra a nota com duas casas decimais
            "País": True  # Mostra o nome do país
        }
    )
    
    # Personalize o layout
    fig.update_layout(
        title_text='Publicações de Livros por País',
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular',
            showcountries=True
        ),
        title_x=0.5,  # Centraliza o título
        height=600,   # Altura do mapa
        width=1000    # Largura do mapa
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
        df_paises = preparar_dados_mapa_livros(df)
        fig = criar_mapa_livros_mundial(df_paises)
        fig.show()
# Mensagem opcional se nenhum arquivo for carregado
if uploaded_file is None:
    st.info("Por favor, carregue um arquivo Excel (.xlsm) para ver os dados.")



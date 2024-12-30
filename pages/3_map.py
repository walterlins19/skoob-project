import streamlit as st
import pandas as pd
import plotly.express as px
import pycountry
import unidecode
import difflib
import pycountry_convert as pc
from datetime import datetime
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
    return df_filtrado

def get_continent(iso_code):
    """Retorna o continente baseado no código ISO do país"""
    try:
        continent_code = pc.country_alpha2_to_continent_code(iso_code)
        continent_name = pc.convert_continent_code_to_continent_name(continent_code)
        return continent_name
    except:
        return "Desconhecido"
    
def create_stats_cards(df_paises):
    """Cria cards com estatísticas gerais, incluindo livros por continente"""
    
    # Adiciona coluna de continente
    df_paises['Continente'] = df_paises['Codigo_ISO'].apply(get_continent)
    
    # Agrupar por continente
    df_continentes = df_paises.groupby('Continente').agg(
        total_livros=('Quantidade_Livros', 'sum'),
        media_livros=('Quantidade_Livros', 'mean')
    ).reset_index()
    
    # Layout de 3 colunas para os cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total de Países",
            value=len(df_paises),
            label_visibility='visible'
            #delta=f"{len(df_paises['Continente'].unique())} Continentes"
        )
    
    with col2:
        # Identificar o continente com mais livros
        continente_mais_livros = df_continentes.loc[df_continentes['total_livros'].idxmax(), 'Continente']
        total_livros_continente = df_continentes['total_livros'].max()
        st.metric(
            label="Continente com Mais Livros",
            value=continente_mais_livros,
            delta=f"{total_livros_continente:,.0f} livros"
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
        'UCRANIA': 'UKR',
        'ALEMANHA': 'DEU',
        'SUICA': 'CHE',
        'IRLANDA': 'IRL',
        'PORTUGAL': 'PRT',
        'CHINA': 'CHN',
        'CHEQUIA': 'CZE',
        'NORUEGA': 'NOR',
        'GRECIA': 'GRC'
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
def get_flag_emoji_from_iso3(iso3_code):
    country_codes ={
            "AFG": "AF",
            "ALB": "AL",
            "DZA": "DZ",
            "ASM": "AS",
            "AND": "AD",
            "AGO": "AO",
            "AIA": "AI",
            "ATA": "AQ",
            "ATG": "AG",
            "ARG": "AR",
            "ARM": "AM",
            "ABW": "AW",
            "AUS": "AU",
            "AUT": "AT",
            "AZE": "AZ",
            "BHS": "BS",
            "BHR": "BH",
            "BGD": "BD",
            "BRB": "BB",
            "BLR": "BY",
            "BEL": "BE",
            "BLZ": "BZ",
            "BEN": "BJ",
            "BMU": "BM",
            "BTN": "BT",
            "BOL": "BO",
            "BIH": "BA",
            "BWA": "BW",
            "BVT": "BV",
            "BRA": "BR",
            "BRN": "BN",
            "BGR": "BG",
            "BFA": "BF",
            "BDI": "BI",
            "KHM": "KH",
            "CMR": "CM",
            "CAN": "CA",
            "CPV": "CV",
            "CYM": "KY",
            "CAF": "CF",
            "TCD": "TD",
            "CHL": "CL",
            "CHN": "CN",
            "CXR": "CX",
            "CCK": "CC",
            "COL": "CO",
            "COM": "KM",
            "COG": "CG",
            "COD": "CD",
            "COK": "CK",
            "CRI": "CR",
            "CIV": "CI",
            "HRV": "HR",
            "CUB": "CU",
            "CYP": "CY",
            "CZE": "CZ",
            "DNK": "DK",
            "DJI": "DJ",
            "DMA": "DM",
            "DOM": "DO",
            "ECU": "EC",
            "EGY": "EG",
            "SLV": "SV",
            "GNQ": "GQ",
            "ERI": "ER",
            "EST": "EE",
            "ETH": "ET",
            "FLK": "FK",
            "FRO": "FO",
            "FJI": "FJ",
            "FIN": "FI",
            "FRA": "FR",
            "GUF": "GF",
            "PYF": "PF",
            "GAB": "GA",
            "GMB": "GM",
            "GEO": "GE",
            "DEU": "DE",
            "GHA": "GH",
            "GIB": "GI",
            "GRC": "GR",
            "GRL": "GL",
            "GRD": "GD",
            "GLP": "GP",
            "GUM": "GU",
            "GTM": "GT",
            "GIN": "GN",
            "GNB": "GW",
            "GUY": "GY",
            "HTI": "HT",
            "HMD": "HM",
            "HND": "HN",
            "HKG": "HK",
            "HUN": "HU",
            "ISL": "IS",
            "IND": "IN",
            "IDN": "ID",
            "IRN": "IR",
            "IRQ": "IQ",
            "IRL": "IE",
            "ISR": "IL",
            "ITA": "IT",
            "JAM": "JM",
            "JPN": "JP",
            "JOR": "JO",
            "KAZ": "KZ",
            "KEN": "KE",
            "KIR": "KI",
            "PRK": "KP",
            "KOR": "KR",
            "KWT": "KW",
            "KGZ": "KG",
            "LAO": "LA",
            "LVA": "LV",
            "LBN": "LB",
            "LSO": "LS",
            "LBR": "LR",
            "LBY": "LY",
            "LIE": "LI",
            "LTU": "LT",
            "LUX": "LU",
            "MAC": "MO",
            "MKD": "MK",
            "MDG": "MG",
            "MWI": "MW",
            "MYS": "MY",
            "MDV": "MV",
            "MLI": "ML",
            "MLT": "MT",
            "MHL": "MH",
            "MTQ": "MQ",
            "MRT": "MR",
            "MUS": "MU",
            "MYT": "YT",
            "MEX": "MX",
            "FSM": "FM",
            "MDA": "MD",
            "MCO": "MC",
            "MNG": "MN",
            "MSR": "MS",
            "MAR": "MA",
            "MOZ": "MZ",
            "MMR": "MM",
            "NAM": "NA",
            "NRU": "NR",
            "NPL": "NP",
            "NLD": "NL",
            "NCL": "NC",
            "NZL": "NZ",
            "NIC": "NI",
            "NER": "NE",
            "NGA": "NG",
            "NIU": "NU",
            "NFK": "NF",
            "MNP": "MP",
            "NOR": "NO",
            "OMN": "OM",
            "PAK": "PK",
            "PLW": "PW",
            "PSE": "PS",
            "PAN": "PA",
            "PNG": "PG",
            "PRY": "PY",
            "PER": "PE",
            "PHL": "PH",
            "PCN": "PN",
            "POL": "PL",
            "PRT": "PT",
            "PRI": "PR",
            "QAT": "QA",
            "REU": "RE",
            "ROU": "RO",
            "RUS": "RU",
            "RWA": "RW",
            "SHN": "SH",
            "KNA": "KN",
            "LCA": "LC",
            "SPM": "PM",
            "VCT": "VC",
            "WSM": "WS",
            "SMR": "SM",
            "STP": "ST",
            "SAU": "SA",
            "SEN": "SN",
            "SYC": "SC",
            "SLE": "SL",
            "SGP": "SG",
            "SVK": "SK",
            "SVN": "SI",
            "SLB": "SB",
            "SOM": "SO",
            "ZAF": "ZA",
            "SGS": "GS",
            "ESP": "ES",
            "LKA": "LK",
            "SDN": "SD",
            "SUR": "SR",
            "SJM": "SJ",
            "SWZ": "SZ",
            "SWE": "SE",
            "CHE": "CH",
            "SYR": "SY",
            "TWN": "TW",
            "TJK": "TJ",
            "TZA": "TZ",
            "THA": "TH",
            "TLS": "TL",
            "TGO": "TG",
            "TKL": "TK",
            "TON": "TO",
            "TTO": "TT",
            "TUN": "TN",
            "TUR": "TR",
            "TKM": "TM",
            "TCA": "TC",
            "TUV": "TV",
            "UGA": "UG",
            "UKR": "UA",
            "ARE": "AE",
            "GBR": "GB",
            "USA": "US",
            "UMI": "UM",
            "URY": "UY",
            "UZB": "UZ",
            "VUT": "VU",
            "VAT": "VA",
            "VEN": "VE",
            "VNM": "VN",
            "VGB": "VG",
            "VIR": "VI",
            "WLF": "WF",
            "ESH": "EH",
            "YEM": "YE",
            "ZMB": "ZM",
            "ZWE": "ZW"
            } # The JSON mapping above
    iso2_code = country_codes.get(iso3_code.upper())
    if iso2_code:
        return get_flag_emoji(iso2_code)
    return ''

def get_flag_emoji(country_code):
    """
    Convert a two-letter country code to a flag emoji.
    
    Args:
        country_code (str): Two-letter country code (ISO 3166-1 alpha-2)
        
    Returns:
        str: Flag emoji for the country code, or empty string if input is invalid
    """
    country_code = country_code.upper()
    return ''.join(chr(ord(c) + 127397) for c in country_code)

def add_flag_emoji_column(df, country_code_column):
    """
    Add a new column with flag emojis based on country codes.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        country_code_column (str): Name of the column containing country codes
        
    Returns:
        pd.DataFrame: DataFrame with new 'flag' column
    """
    result = df.copy()
    result['flag'] = result[country_code_column].apply(get_flag_emoji_from_iso3)
    return result



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
    df_paises = add_flag_emoji_column(df_paises, 'Codigo_ISO')
    print(df_paises)
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
        color_continuous_scale='YlOrRd',  # Usa uma escala de azuis mais suave
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
    df = app_retrospectiva_leitura(df)
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





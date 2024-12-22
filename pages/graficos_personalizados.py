# pages/graficos_personalizados.py
import streamlit as st
import pandas as pd
import pygwalker as pyg
from pygwalker.api.streamlit import StreamlitRenderer

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

def preparar_dados_para_graficos(df):
    """
    Prepara os dados para uso no criador de gráficos.
    
    Args:
        df (pandas.DataFrame): DataFrame original
        
    Returns:
        pandas.DataFrame: DataFrame preparado para visualização
    """
    df_prep = df.copy()
    
    # Tratamento de datas
    df_prep['Conclusão'] = pd.to_datetime(df_prep['Conclusão'])
    df_prep['Ano'] = df_prep['Conclusão'].dt.year
    df_prep['Mês'] = df_prep['Conclusão'].dt.month
    df_prep['Mês_Nome'] = df_prep['Conclusão'].dt.strftime('%B')
    df_prep['Trimestre'] = df_prep['Conclusão'].dt.quarter
    
    # Converter Ano de Publicação para numérico
    df_prep['Ano de Publicação'] = pd.to_numeric(df_prep['Ano de Publicação'], errors='coerce')
    
    # Calcular métricas agregadas
    df_prep['Páginas_por_Mês'] = df_prep.groupby(['Ano', 'Mês'])['Páginas'].transform('sum')
    df_prep['Nota_Média_por_Gênero'] = df_prep.groupby('Gênero')['Nota'].transform('mean')
    df_prep['Nota_Média_por_Autor'] = df_prep.groupby('Autor')['Nota'].transform('mean')
    
    # Médias móveis
    df_prep['Média_Móvel_Páginas'] = df_prep.groupby('Ano')['Páginas'].transform(
        lambda x: x.rolling(window=3, min_periods=1).mean()
    )
    df_prep['Média_Móvel_Notas'] = df_prep.groupby('Ano')['Nota'].transform(
        lambda x: x.rolling(window=3, min_periods=1).mean()
    )
    
    # Criar categorias úteis
    df_prep['Tamanho'] = pd.cut(
        df_prep['Páginas'],
        bins=[0, 100, 300, 500, float('inf')],
        labels=['Curto', 'Médio', 'Longo', 'Muito Longo']
    )
    
    df_prep['Faixa_Nota'] = pd.cut(
        df_prep['Nota'],
        bins=[0, 2, 3, 4, 5],
        labels=['Ruim', 'Regular', 'Bom', 'Excelente']
    )
    
    # Remover a coluna ID que não é necessária para visualização
    if 'Mês Conclusão' in df_prep.columns:
        df_prep = df_prep.drop('Mês Conclusão', axis=1)
    
    return df_prep

def main():
    st.set_page_config(
        page_title="Criador de Gráficos Personalizados",
        page_icon="📊",
        layout="wide"
    )

    st.title("📊 Criador de Gráficos Personalizados")
    
    # Carregar dados
    df = load_data()
    if df is None:
        return
        
    # Informações de uso
    with st.expander("ℹ️ Como usar o criador de gráficos"):
        st.markdown("""
        ### Instruções de Uso:
        
        1. **Análises Temporais:**
           - Use 'Conclusão' ou 'Ano de Publicação' para análises ao longo do tempo
           - Combine com 'Nota' ou 'Páginas' para ver tendências
        
        2. **Análises Demográficas:**
           - Explore distribuições por 'País', 'Região', 'Sexo Autor' e 'Etnia'
           - Compare notas médias por diferentes grupos
        
        3. **Análises Literárias:**
           - Compare 'Gênero' com outras métricas
           - Analise diferenças entre 'Ficção' e não ficção
           - Explore tendências por 'Séc' de publicação
        """)
    
    # Preparar dados
    df_prep = preparar_dados_para_graficos(df)

    
    try:
        # Configurar tema do PyGWalker
        config = {
            "theme": "streamlit",
            "dark_mode": True,
            "layout": {
                "width": "100%",
                "height": "800px"
            }
        }
        
        # Criar interface do PyGWalker
        pyg_app = StreamlitRenderer(df_prep)
        
        pyg_app.explorer()

                # Adicionar sugestões de análises
        with st.expander("💡 Sugestões de Análises"):
            st.markdown("""
            ### Análises Recomendadas:
            
            1. **Padrões de Leitura**
               - Livros lidos por mês/ano
               - Páginas lidas ao longo do tempo
               - Notas médias por período
            
            2. **Diversidade Literária**
               - Distribuição por gênero e ficção/não-ficção
               - Representatividade por sexo do autor e etnia
               - Distribuição geográfica (país/região)
            
            3. **Tendências Históricas**
               - Comparação entre ano de publicação e data de leitura
               - Análise por século de publicação
               - Evolução das notas por período histórico
            
            4. **Análises Editoriais**
               - Distribuição por editora
               - Relação entre editora e número de páginas
               - Notas médias por editora
            """)
        
        # Mostrar campos disponíveis
        with st.expander("📋 Campos Disponíveis para Análise"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### Dados Temporais")
                st.markdown("""
                - Conclusão
                - Ano de Publicação
                - Séc
                - Mês
                - Ano
                - Trimestre
                """)
                
                st.markdown("### Métricas")
                st.markdown("""
                - Páginas
                - Nota
                - Média Móvel de Páginas
                - Média Móvel de Notas
                """)
            
            with col2:
                st.markdown("### Categorias Literárias")
                st.markdown("""
                - Gênero
                - Ficção
                - Editora
                - Título
                """)
                
                st.markdown("### Dados Geográficos")
                st.markdown("""
                - País
                - Região
                """)
            
            with col3:
                st.markdown("### Dados Demográficos")
                st.markdown("""
                - Autor
                - Sexo Autor
                - Etnia
                """)
                
                st.markdown("### Campos Calculados")
                st.markdown("""
                - Livros por Período
                - Páginas por Período
                - Notas Médias
                """)
        
    except Exception as e:
        st.error(f"""
        Erro ao carregar o PyGWalker: {str(e)}
        
        Certifique-se de que o PyGWalker está instalado:
        ```bash
        pip install pygwalker
        ```
        """)
        
        # Mostrar DataFrame como fallback
        st.write("Mostrando dados em formato tabular como alternativa:")
        st.dataframe(df_prep)
        
    except Exception as e:
        st.error(f"""
        Erro ao carregar o PyGWalker: {str(e)}
        
        Certifique-se de que o PyGWalker está instalado:
        ```bash
        pip install pygwalker
        ```
        """)
        
        # Mostrar DataFrame como fallback
        st.write("Mostrando dados em formato tabular como alternativa:")
        st.dataframe(df_prep)

if __name__ == "__main__":
    main()
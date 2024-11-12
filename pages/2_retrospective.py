import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load the dataset (this should be a .csv or any data source you have)
# For demonstration, I will use a placeholder for loading the dataset
st.title('Análise de Dados de Livros')

st.sidebar.header('Carregar Arquivo Excel')

# File uploader for the user to upload an XLSM file
uploaded_file = st.sidebar.file_uploader("Escolha um arquivo XLSM", type=["xlsm"])

if uploaded_file is not None:
    try:
        # Read the uploaded XLSM file using pandas (Excel can be .xlsm, .xlsx)
        df = pd.read_excel(uploaded_file, sheet_name='DB', engine='openpyxl')
        # Streamlit Layout
        st.title('Dashboard: Books Read in a Year')

        # Show basic stats
        st.header('Basic Statistics')
        total_books = len(df)
        total_pages = df['Páginas'].sum()
        average_pages = df['Páginas'].mean()

        st.write(f"Total de livros lidos: {total_books}")
        st.write(f"Total de páginas lidas: {total_pages}")
        st.write(f"Média de páginas por livro: {average_pages:.2f}")

        # Plot the most read genres
        st.header('Gêneros Mais Lidos')
        genre_count = df['Gênero'].value_counts().reset_index()
        genre_count.columns = ['Gênero', 'Contagem']

        fig_genre = px.bar(genre_count, x='Gênero', y='Contagem', title="Contagem de Livros por Gênero")
        st.plotly_chart(fig_genre)

        # Plot the number of books by author
        st.header('Número de Livros por Autor')
        author_count = df['Autor'].value_counts().reset_index()
        author_count.columns = ['Autor', 'Contagem']

        fig_author = px.bar(author_count.head(10), x='Autor', y='Contagem', title="Top 10 Autores com Mais Livros Lidos")
        st.plotly_chart(fig_author)

        # Pie chart of the fiction vs non-fiction books
        st.header('Ficção vs Não Ficção')
        ficcao_count = df['Ficção'].value_counts().reset_index()
        ficcao_count.columns = ['Ficção', 'Contagem']

        fig_ficcao = px.pie(ficcao_count, names='Ficção', values='Contagem', title="Distribuição de Livros Ficção e Não Ficção")
        st.plotly_chart(fig_ficcao)

        # Yearly distribution of books read
        st.header('Distribuição de Livros Lidos por Ano')
        yearly_count = df['Ano de Publicação'].value_counts().reset_index()
        yearly_count.columns = ['Ano de Publicação', 'Contagem']

        fig_yearly = px.line(yearly_count.sort_values('Ano de Publicação'), x='Ano de Publicação', y='Contagem',
                            title="Número de Livros Lidos por Ano")
        st.plotly_chart(fig_yearly)

        # Gender of the authors
        st.header('Gênero dos Autores')
        gender_count = df['Sexo Autor'].value_counts().reset_index()
        gender_count.columns = ['Sexo Autor', 'Contagem']

        fig_gender = px.pie(gender_count, names='Sexo Autor', values='Contagem', title="Distribuição de Gênero dos Autores")
        st.plotly_chart(fig_gender)

        # Ethnicity of the authors
        st.header('Etnia dos Autores')
        ethnicity_count = df['Etnia'].value_counts().reset_index()
        ethnicity_count.columns = ['Etnia', 'Contagem']

        fig_ethnicity = px.pie(ethnicity_count, names='Etnia', values='Contagem', title="Distribuição Étnica dos Autores")
        st.plotly_chart(fig_ethnicity)

        # Pages distribution visualization
        st.header('Distribuição de Páginas Lidas')
        fig_pages = px.histogram(df, x='Páginas', nbins=20, title="Distribuição do Número de Páginas Lidas")
        st.plotly_chart(fig_pages)

        # Author's Country and Region
        st.header('País e Região dos Autores')
        country_region_count = df.groupby(['País', 'Região']).size().reset_index(name='Contagem')

        fig_country_region = px.sunburst(country_region_count, path=['País', 'Região'], values='Contagem',
                                        title="Distribuição dos Autores por País e Região")
        st.plotly_chart(fig_country_region)

        # Conclusion rate visualization
        st.header('Taxa de Conclusão dos Livros')
        conclusion_count = df['Conclusão'].value_counts().reset_index()
        conclusion_count.columns = ['Conclusão', 'Contagem']

        fig_conclusion = px.pie(conclusion_count, names='Conclusão', values='Contagem', title="Taxa de Conclusão dos Livros")
        st.plotly_chart(fig_conclusion)

        # Additional interactivity
        st.sidebar.header('Filtros de Visualização')
        genre_filter = st.sidebar.multiselect('Selecione o(s) Gênero(s)', df['Gênero'].unique())
        author_filter = st.sidebar.multiselect('Selecione o(s) Autor(es)', df['Autor'].unique())

        # Filter dataset based on selections
        if genre_filter:
            df = df[df['Gênero'].isin(genre_filter)]
        if author_filter:
            df = df[df['Autor'].isin(author_filter)]

        # Display filtered dataset in a table
        st.subheader('Tabela de Livros Filtrados')
        st.write(df)
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {str(e)}")


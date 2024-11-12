import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Streamlit UI
st.title('Análise de Dados de Livros')

st.sidebar.header('Carregar Arquivo Excel')

# File uploader for the user to upload an XLSM file
uploaded_file = st.sidebar.file_uploader("Escolha um arquivo XLSM", type=["xlsm"])

if uploaded_file is not None:
    try:
        # Read the uploaded XLSM file using pandas (Excel can be .xlsm, .xlsx)
        df = pd.read_excel(uploaded_file, sheet_name='DB', engine='openpyxl')
        
        # Display the first few rows of the dataframe
        st.subheader("Visão Geral dos Dados")
        st.write(df.head())
        
        # Check if the necessary columns exist in the dataframe
        required_columns = [
            "ID", "Título", "Gênero", "Ficção", "País", "Região", "Autor", "Editora", 
            "Ano de Publicação", "Séc", "Sexo Autor", "Etnia", "Páginas", "Conclusão", "Nota"
        ]
        available_columns = df.columns.tolist()
        
        # Inform user if any of the expected columns are missing
        missing_columns = [col for col in required_columns if col not in available_columns]
        if missing_columns:
            st.warning(f"Alerta: As seguintes colunas obrigatórias estão faltando: {', '.join(missing_columns)}")
        
        # Sidebar to select a column to visualize
        column_options = available_columns
        selected_column = st.sidebar.selectbox("Selecione uma Coluna para o Gráfico", column_options)

        # Display a summary of the selected column
        st.subheader(f'Visão Geral da Coluna {selected_column}')
        st.write(df[selected_column].value_counts())

        # Generate graphs based on the selected column
        if selected_column == "País":
            # Plot a bar chart for countries
            st.subheader('Livros por País')
            country_count = df['País'].value_counts()
            st.bar_chart(country_count)

        elif selected_column == "Autor":
            # Plot a bar chart for authors
            st.subheader('Livros por Autor')
            author_count = df['Autor'].value_counts()
            st.bar_chart(author_count)

        elif selected_column == "Gênero":
            # Plot a pie chart for genres
            st.subheader('Livros por Gênero')
            genre_count = df['Gênero'].value_counts()
            st.write(genre_count)
            fig, ax = plt.subplots()
            ax.pie(genre_count, labels=genre_count.index, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            st.pyplot(fig)

        elif selected_column == "Ano de Publicação":
            # Plot a line graph for the distribution of books over the years
            st.subheader('Livros por Ano de Publicação')
            year_count = df['Ano de Publicação'].value_counts().sort_index()
            st.line_chart(year_count)

        elif selected_column == "Sexo Autor":
            # Plot a bar chart for authors' gender
            st.subheader('Livros por Sexo do Autor')
            gender_count = df['Sexo Autor'].value_counts()
            st.bar_chart(gender_count)

        elif selected_column == "Etnia":
            # Plot a bar chart for authors' ethnicity
            st.subheader('Livros por Etnia do Autor')
            ethnicity_count = df['Etnia'].value_counts()
            st.bar_chart(ethnicity_count)

        elif selected_column == "Ficção":
            # Plot a bar chart for fiction books
            st.subheader('Livros de Ficção vs Não-Ficção')
            fiction_count = df['Ficção'].value_counts()
            st.bar_chart(fiction_count)

        # Additional analysis: Filter by year range (optional)
        st.sidebar.header('Análise Adicional')
        year_min = st.sidebar.slider("Ano Mínimo", min_value=int(df["Ano de Publicação"].min()), 
                                     max_value=int(df["Ano de Publicação"].max()), value=int(df["Ano de Publicação"].min()))
        year_max = st.sidebar.slider("Ano Máximo", min_value=int(df["Ano de Publicação"].min()), 
                                     max_value=int(df["Ano de Publicação"].max()), value=int(df["Ano de Publicação"].max()))
        filtered_df = df[(df['Ano de Publicação'] >= year_min) & (df['Ano de Publicação'] <= year_max)]

        # Show filtered data and a plot of the filtered year range
        st.subheader(f"Livros Filtrados (de {year_min} até {year_max})")
        st.write(filtered_df)

        # Create a plot of the filtered data
        if selected_column == "Ano de Publicação":
            year_filtered_count = filtered_df['Ano de Publicação'].value_counts().sort_index()
            st.line_chart(year_filtered_count)

        elif selected_column == "País":
            country_filtered_count = filtered_df['País'].value_counts()
            st.bar_chart(country_filtered_count)

        elif selected_column == "Autor":
            author_filtered_count = filtered_df['Autor'].value_counts()
            st.bar_chart(author_filtered_count)

        elif selected_column == "Gênero":
            genre_filtered_count = filtered_df['Gênero'].value_counts()
            fig, ax = plt.subplots()
            ax.pie(genre_filtered_count, labels=genre_filtered_count.index, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            st.pyplot(fig)

        elif selected_column == "Sexo Autor":
            gender_filtered_count = filtered_df['Sexo Autor'].value_counts()
            st.bar_chart(gender_filtered_count)

        elif selected_column == "Etnia":
            ethnicity_filtered_count = filtered_df['Etnia'].value_counts()
            st.bar_chart(ethnicity_filtered_count)

        elif selected_column == "Ficção":
            fiction_filtered_count = filtered_df['Ficção'].value_counts()
            st.bar_chart(fiction_filtered_count)

        # Display the number of pages per genre (example of cross-column analysis)
        if st.sidebar.checkbox("Mostrar Número de Páginas por Gênero"):
            st.subheader("Número de Páginas por Gênero")
            genre_pages = df.groupby('Gênero')['Páginas'].sum()
            st.bar_chart(genre_pages)

        # Display the average rating per genre
        if st.sidebar.checkbox("Mostrar Média de Nota por Gênero"):
            st.subheader("Média de Nota por Gênero")
            genre_avg_rating = df.groupby('Gênero')['Nota'].mean()
            st.bar_chart(genre_avg_rating)

    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {str(e)}")
else:
    st.info("Por favor, carregue um arquivo Excel (.xlsm) para começar.")

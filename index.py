import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from io import BytesIO
from fpdf import FPDF

# Configuração visual
df = None
sns.set_theme(style="whitegrid", palette="pastel")
st.set_page_config(page_title="Análises Visuais de Filmes", layout="wide")

# Título principal
st.title("\U0001F3AC Análises Visuais de Filmes")
st.markdown("---")

# Carregar dados
arquivo_excel = "C:/Users/famil/Desktop/Trabalho A3/Analise_de_30_Filmes.xlsx"
df = pd.read_excel(arquivo_excel)

# Filtros laterais
st.sidebar.header("\U0001F50D Filtros")
filtro_genero = st.sidebar.selectbox("\U0001F39E️ Gênero:", ["Sem Filtro"] + sorted(df['Gênero(s)'].dropna().unique()))
filtro_ano = st.sidebar.selectbox("📅 Ano mínimo:", ["Sem Filtro"] + sorted(df['Ano de Lançamento'].dropna().unique()))

# Aplicar filtros
df_filtrado = df.copy()
if filtro_genero != "Sem Filtro":
    df_filtrado = df_filtrado[df_filtrado['Gênero(s)'].str.contains(filtro_genero, na=False)]
if filtro_ano != "Sem Filtro":
    df_filtrado = df_filtrado[df_filtrado['Ano de Lançamento'] >= int(filtro_ano)]

# Gráficos em colunas
col1, col2 = st.columns(2)

with col1:
    st.subheader("⭐ Distribuição de Notas IMDb")
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    sns.histplot(df_filtrado['Nota IMDb'].dropna(), bins=10, kde=True, color='steelblue', ax=ax1)
    ax1.set_xlabel('Nota IMDb')
    ax1.set_ylabel('Frequência')
    st.pyplot(fig1)

with col2:
    st.subheader("🎭 Quantidade de Filmes por Gênero")
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    df_filtrado['Gênero(s)'].value_counts().plot(kind='bar', color='coral', ax=ax2)
    ax2.set_xlabel('Gênero')
    ax2.set_ylabel('Quantidade')
    st.pyplot(fig2)

with st.expander("💸 Orçamento vs Bilheteria"):
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    df_plot = df_filtrado.dropna(subset=['Orçamento (USD)', 'Bilheteria Mundial (USD)', 'Nota IMDb'])
    sns.scatterplot(
        data=df_plot,
        x='Orçamento (USD)',
        y='Bilheteria Mundial (USD)',
        hue='Nota IMDb',
        palette="cool",
        ax=ax3
    )
    ax3.set_title('Orçamento vs Bilheteria Mundial')
    ax3.set_xlabel('Orçamento (USD)')
    ax3.set_ylabel('Bilheteria Mundial (USD)')
    st.pyplot(fig3)

with st.expander("🍅 Rotten Tomatoes: Público vs Crítica"):
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    df_rt = df_filtrado.dropna(subset=['Nota Rotten Tomatoes (Crítica)', 'Nota Rotten Tomatoes (Público)'])
    sns.scatterplot(
        data=df_rt,
        x='Nota Rotten Tomatoes (Crítica)',
        y='Nota Rotten Tomatoes (Público)',
        color='purple',
        ax=ax4
    )
    ax4.set_title('RT: Crítica vs Público')
    ax4.set_xlabel('Nota RT Crítica')
    ax4.set_ylabel('Nota RT Público')
    st.pyplot(fig4)

with st.expander("⏱️ Duração Média por Gênero"):
    fig5, ax5 = plt.subplots(figsize=(10, 6))
    df_filtrado.dropna(subset=['Duração (min)', 'Gênero(s)']).groupby('Gênero(s)')['Duração (min)'].mean().plot(kind='bar', color='limegreen', ax=ax5)
    ax5.set_title('Duração Média por Gênero')
    ax5.set_xlabel('Gênero')
    ax5.set_ylabel('Duração Média (min)')
    st.pyplot(fig5)

with st.expander("📈 Filmes por Ano de Lançamento"):
    fig6, ax6 = plt.subplots(figsize=(10, 6))
    df_filtrado['Ano de Lançamento'].dropna().value_counts().sort_index().plot(kind='line', color='dodgerblue', ax=ax6)
    ax6.set_title('Número de Filmes por Ano')
    ax6.set_xlabel('Ano de Lançamento')
    ax6.set_ylabel('Quantidade de Filmes')
    st.pyplot(fig6)

# Classe PDF
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Análise de Desempenho de Bilheteria", 0, 1, "C")

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", 0, 0, "C")

# Funções para relatório
def gerar_relatorio_pdf(df, categoria, ano):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(0, 10, f"Categoria: {categoria}", ln=True)
    pdf.cell(0, 10, f"Ano: {ano}", ln=True)
    pdf.cell(0, 10, f"Bilheteria Total Estimada: {df['Bilheteria Mundial (USD)'].sum():,.2f} USD", ln=True)
    pdf.ln(10)

    texto = (
        "Este resultado reflete o comportamento do público em relação aos títulos lançados nesse período, \n"
        "considerando fatores como recepção crítica, estratégias de marketing, distribuição e tendências do \n"
        "mercado cinematográfico.\n\n"
        "A análise contribui para a compreensão do impacto comercial da categoria no ano em questão, \n"
        "servindo como referência para estudos de mercado, projeções futuras e estratégias de produção e \n"
        "lançamento de novos títulos."
    )
    pdf.multi_cell(0, 10, texto)

    buffer = BytesIO()
    buffer.write(pdf.output(dest='S').encode('latin1'))
    buffer.seek(0)
    return buffer

def gerar_relatorio_excel(df):
    buffer = BytesIO()
    df.to_excel(buffer, index=False, sheet_name="Relatório Filtrado")
    buffer.seek(0)
    return buffer

# Botões de relatório
st.sidebar.header("📄 Gerar Relatórios")
if st.sidebar.button("Gerar Relatório"):
    categoria = filtro_genero if filtro_genero != "Sem Filtro" else "Todos os Gêneros"
    ano = filtro_ano if filtro_ano != "Sem Filtro" else "Todos os Anos"

    pdf_buffer = gerar_relatorio_pdf(df_filtrado, categoria, ano)
    excel_buffer = gerar_relatorio_excel(df_filtrado)

    st.sidebar.download_button(
        label="📅 Baixar PDF",
        data=pdf_buffer,
        file_name="Relatorio_Filmes.pdf",
        mime="application/pdf"
    )
    st.sidebar.download_button(
        label="📊 Baixar Excel",
        data=excel_buffer,
        file_name="Relatorio_Filmes.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Rodapé
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>Desenvolvido por Grupo 6 • Trabalho A3</p>",
    unsafe_allow_html=True
)

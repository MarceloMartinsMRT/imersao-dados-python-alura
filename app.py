import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(
    page_title="Dashboard de  Salarios na Área de Dados", 
    page_icon=":bar_chart:",
    layout="wide")

#Carregamento dos dados
df = pd.read_csv('dados-imersao-final.csv')

#Barra lateral (filtros )

#Filtro de ano
anos_disponiveis = sorted(df['ano'].unique())
ano_selecionados = st.sidebar.multiselect('Ano', anos_disponiveis, default=anos_disponiveis)

#Filtro de Senioridade
senioridade_disponiveis = sorted(df['senioridade'].unique())
senioridade_selecionadas = st.sidebar.multiselect('Senioridade', senioridade_disponiveis, default=senioridade_disponiveis)

#Filtro por Tipo de Contrato
contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect('Tipo de Contrato', contratos_disponiveis, default=contratos_disponiveis)

#Filtro por Tamanho da Empresa
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect('Tamanho da Empresa', tamanhos_disponiveis, default=tamanhos_disponiveis)

#Filtragem do DataFrame
#O DataFrame é filtrado com base nos filtros selecionados na barra lateral
df_filtrado = df[
    (df['ano'].isin(ano_selecionados)) &
    (df['senioridade'].isin(senioridade_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

#Conteudo Principal
st.title('Dashboard de Analise de Salários na Área de Dados')
st.markdown("Explore os dados saláriaiss na área de dados nos ultimos anos.Utilize os filtros à esquerda")

#Metricas principais (KPIs)

st.subheader("Metricas gerais (Salario anual em USD)")

if not df_filtrado.empty:
    media_salario = df_filtrado['usd'].mean()
    max_salario = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_recente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_comum = 0, 0, 0, ""

col1, col2, col3, col4 = st.columns(4)

col1.metric("Salário Médio", f"${media_salario:,.0f}")
col2.metric("Salário Máximo", f"${max_salario:,.0f}")
col3.metric("Total de Registros", f"{total_registros:,}")
col4.metric("Cargo Mais Recente", cargo_mais_recente)

st.markdown("---")

#analises virtuais com plotly express

st.subheader("Graficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        graficos_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title='Top 10 Cargos por salario medio',
            labels={'usd': 'Média salarial anual (USD)', 'cargo': ''}
        )
        graficos_cargos.update_layout(title_x=0.1, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(graficos_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para exibir o gráfico de cargos.")

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title='Distribuição Salarial Anual',
            labels={'usd': 'Faixa salarial Anual (USD)', 'count': 'Número de Registros'}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para exibir o gráfico de distribuição salarial.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Distribuição de Trabalho Remoto',
            hole=0.5
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para exibir o gráfico de trabalho remoto.")


with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='Viridis', #rdylgn
            title='Média Salarial Anual de Data Scientists por País',
            labels={'usd': 'Média Salarial Anual (USD)', 'residencia_iso3': 'País'})
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para exibir o gráfico de média salarial por país.")

#Tabela de dados Detalhados
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)
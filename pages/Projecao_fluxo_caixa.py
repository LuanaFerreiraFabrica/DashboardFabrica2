import streamlit as st
import pandas as pd
from utils.queries import *
from utils.functions.dados_gerais import *
from utils.functions.fluxo_de_caixa import *
from workalendar.america import Brazil

st.set_page_config(
    page_title="Fluxo_Caixa",
    page_icon="💰",
    layout="wide"
)

if 'loggedIn' not in st.session_state or not st.session_state['loggedIn']:
    st.switch_page('Login.py')


st.title('PROJEÇÃO - Fluxo de Caixa')
config_sidebar()

df_projecao_bares = config_projecao_bares()
df_projecao_grouped = config_grouped_projecao(df_projecao_bares.copy())

bares = df_projecao_bares["Empresa"].unique()
with st.container(border=True):
  bar = st.selectbox("Bar", bares)
  df_projecao_bar = df_projecao_bares[df_projecao_bares["Empresa"] == bar]
  df_projecao_bar_com_soma = somar_total(df_projecao_bar)
  columns_projecao_bar_com_soma = ['Data', 'Empresa', 'Saldo_Inicio_Dia', 'Valor_Liquido_Recebido', 'Valor_Projetado_Zig', 'Receita_Projetada_Extraord',
                                 'Despesas_Aprovadas_Pendentes', 'Despesas_Pagas', 'Saldo_Final']
  df_projecao_bar_com_soma = df_projecao_bar_com_soma[columns_projecao_bar_com_soma]
  st.dataframe(df_projecao_bar_com_soma, use_container_width=True, hide_index=True)

st.divider()

# Projeção Agrupada
with st.container(border=True):
  st.subheader('Projeção de bares agrupados:' )
  st.markdown(
    """*Bar Brahma, Bar Léo, Bar Brasilia, Edificio Rolim, Hotel Maraba, 
    Jacaré, Orfeu, Riviera, Tempus, Escritorio Fabrica de Bares, Priceless*
    """
  )

  df_projecao_grouped_com_soma = somar_total(df_projecao_grouped)

  columns_projecao_grouped = ['Data', 'Saldo_Inicio_Dia', 'Valor_Liquido_Recebido', 'Valor_Projetado_Zig', 'Receita_Projetada_Extraord',
                            'Despesas_Aprovadas_Pendentes', 'Despesas_Pagas', 'Saldo_Final']

  st.dataframe(df_projecao_grouped_com_soma[columns_projecao_grouped], use_container_width=True, hide_index=True)

st.divider()

with st.container(border=True):
  st.subheader('Despesas do dia')
  lojasComDados = preparar_dados_lojas_user()
  col1, col2, col3 = st.columns([5, 2, 3])

  # Adiciona seletores
  with col1:
    lojasSelecionadas = st.multiselect(label='Selecione Lojas', options=lojasComDados, key='lojas_multiselect')
  with col2:
    checkbox = st.checkbox(label='Adicionar lojas agrupadas')
    if checkbox:
      lojasAgrupadas = [
            'Bar Brahma - Centro', 'Bar Léo - Centro', 'Bar Brasilia - Aeroporto',
            'Bar Brasilia - Aeroporto', 'Delivery Bar Leo Centro', 'Delivery Fabrica de Bares',
            'Delivery Orfeu', 'Edificio Rolim', 'Hotel Maraba', 'Jacaré', 'Orfeu',
            'Riviera Bar', 'Tempus', 'Escritorio Fabrica de Bares', 'Priceless'
      ]
      lojasSelecionadas.extend(lojasAgrupadas)
    checkbox2 = st.checkbox(label='Apenas Pendentes')
    checkbox3 = st.checkbox(label='Apenas Pagas')
  with col3:
    dataSelecionada = st.date_input('Data de Início', value=datetime.today(), key='data_inicio_input', format="DD/MM/YYYY")

  dataSelecionada = pd.to_datetime(dataSelecionada)
  df = config_despesas_a_pagar(lojasSelecionadas, dataSelecionada)
  if checkbox2:
    df = filtrar_por_classe_selecionada(df, 'Status_Pgto', ['Pendente'])
  if checkbox3:
    df = filtrar_por_classe_selecionada(df, 'Status_Pgto', ['Pago'])
  st.dataframe(df, use_container_width=True, hide_index=True)
  valorTotal = df['Valor'].sum()
  valorTotal = format_brazilian(valorTotal)
  df = format_columns_brazilian(df, ['Valor'])
  st.write('Valor total das despesas selecionadas = R$', valorTotal)
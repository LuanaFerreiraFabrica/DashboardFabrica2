import streamlit as st
import pandas as pd
from utils.queries import *
from utils.functions.dados_gerais import *
from utils.functions.previsao_faturamento import *
from workalendar.america import Brazil
from streamlit_echarts import st_echarts


st.set_page_config(
    page_title="Previsao_faturamento",
    page_icon="💰",
    layout="wide"
)

if 'loggedIn' not in st.session_state or not st.session_state['loggedIn']:
    st.switch_page('Login.py')


st.title('PREVISÃO DE FATURAMENTO')
config_sidebar()
st.divider()

dfCompensacoes = GET_COMPENSACOES_ZIG_AGRUPADAS()
dfCompensacoes['Data_Compensacao'] = pd.to_datetime(dfCompensacoes['Data_Compensacao'])
df_parciais = criar_parciais(dfCompensacoes)
df_parciais = df_parciais.loc[:,~df_parciais.columns.duplicated()]
df_unificado = unificar_parciais(df_parciais)



# Filtre os dados com base no intervalo de datas
grouped_df = df_unificado.groupby(['Data_Parcial', 'Empresa'], as_index=False).agg({'Valor_Parcial': 'sum'})
sorted_df = grouped_df.sort_values(by=['Data_Parcial', 'Empresa'])

lojasComDados = preparar_dados_lojas_user()
data_inicio_default = datetime.today() - timedelta(days=7)
data_fim_default = datetime.today() + timedelta(days=7)
lojasSelecionadas, data_inicio, data_fim = criar_seletores(lojasComDados, data_inicio_default, data_fim_default)
st.divider()

sorted_df.rename(columns = {'Empresa': 'Loja', 'Data_Parcial': 'Data', 'Valor_Parcial': 'Valor Projetado'}, inplace=True)
faturamentoReal = GET_FATURAMENTO_REAL()

faturamentoReal['Data'] = pd.to_datetime(faturamentoReal['Data'])
sorted_df['Data'] = pd.to_datetime(sorted_df['Data'])

dfComparacao = sorted_df.merge(faturamentoReal, on=['Data', 'Loja'], how='left')
dfComparacao = filtrar_por_datas(dfComparacao, data_inicio, data_fim, 'Data')
dfComparacao = filtrar_por_classe_selecionada(dfComparacao, 'Loja', lojasSelecionadas)
dfComparacao.rename(columns = {'Valor_Faturado': 'Valor Faturado'}, inplace=True)
dfComparacao['Diferença'] = dfComparacao['Valor Faturado'] - dfComparacao['Valor Projetado']

dfComparacao2 = dfComparacao.copy()

dfComparacaoAgg = dfComparacao.groupby('Loja').agg({
  'Valor Projetado': 'sum',
  'Valor Faturado': 'sum',
  'Diferença': 'sum'
}).reset_index()

dfComparacao = format_date_brazilian(dfComparacao, 'Data')
dfComparacao = format_columns_brazilian(dfComparacao, ['Valor Projetado', 'Valor Faturado', 'Diferença'])
dfComparacaoStyled = dfComparacao.style.map(highlight_values, subset=['Diferença'])

dfComparacaoAgg = format_columns_brazilian(dfComparacaoAgg, ['Valor Projetado', 'Valor Faturado', 'Diferença'])
dfComparacaoAggStyled = dfComparacaoAgg.style.map(highlight_values, subset=['Diferença'])


with st.container(border=True):
  col, col1, col2 = st.columns([1, 8, 1])
  with col1:
    st.subheader('Previsão e Faturamento Real:')
  col, col1, col2 = st.columns([3, 8, 3])
  with col1:
    st.dataframe(dfComparacaoStyled, width=700, hide_index=True)



with st.container(border=True):
  col, col1, col2 = st.columns([1, 8, 1])
  with col1:
    st.subheader('Agrupamento Pelo Período Selecionado:')
  col, col1, col2 = st.columns([3, 8, 3])
  with col1:
    st.dataframe(dfComparacaoAggStyled, width=700, hide_index=True)
    



def grafico_previsao_faturamento(df):
  dfComparacaoAgg = df.groupby('Data').agg({
    'Valor Projetado': 'sum',
    'Valor Faturado': 'sum'
  }).reset_index()

  dfComparacaoAgg = format_date_brazilian(dfComparacaoAgg, 'Data')
  dfComparacaoAgg['Valor Projetado'] = dfComparacaoAgg['Valor Projetado'].astype(float)
  dfComparacaoAgg['Valor Faturado'] = dfComparacaoAgg['Valor Faturado'].astype(float)

  # Prepare os dados para o gráfico
  dates = dfComparacaoAgg['Data'].tolist()
  faturamento = dfComparacaoAgg['Valor Faturado'].tolist()
  valor_previsto = dfComparacaoAgg['Valor Projetado'].tolist()

  option = {
    'title': {
        'text': ' '
    },
    'tooltip': {
        'trigger': 'axis'
    },
    'legend': {
        'data': ['Valor Faturado', 'Valor Projetado']
    },
    'xAxis': {
        'type': 'category',
        'data': dates,
        'axisLabel': {
            # 'interval': 1,  # Ajuste conforme a quantidade de dados para evitar sobrecarga
            'rotate': 45
        }
    },
    'yAxis': {
        'type': 'value'
    },
    'series': [
        {
            'name': 'Valor Faturado',
            'type': 'line',
            'data': faturamento
        },
        {
            'name': 'Valor Projetado',
            'type': 'line',
            'data': valor_previsto
        }
    ]
  }

  # Exibe o gráfico no Streamlit
  st_echarts(options=option, width=1000)
  return



with st.container(border=True):
  col, col1, col2 = st.columns([1, 8, 1])
  with col1:
    st.subheader('Valores Projetado vs Faturado por Dia:')
  col, col1, col2 = st.columns([1, 8, 1])
  with col1:
    grafico_previsao_faturamento(dfComparacao2)

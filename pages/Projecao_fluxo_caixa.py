import streamlit as st
import pandas as pd
from utils.queries import *
from utils.functions_fluxo_caixa import *
from utils.functions import config_sidebar
from workalendar.america import Brazil


st.set_page_config(
  page_title="Fluxo_Caixa",
  page_icon="💰",
  layout="wide"
)

if 'loggedIn' not in st.session_state or not st.session_state['loggedIn']:
  st.switch_page('Login.py')

config_sidebar()



df_projecao_bares = config_projecao_bares()
df_projecao_grouped = config_grouped_projecao(df_projecao_bares.copy())

bares = df_projecao_bares["Empresa"].unique()
bar = st.selectbox("Bar", bares)

df_projecao_bar = df_projecao_bares[df_projecao_bares["Empresa"] == bar]
df_projecao_bar_com_soma = somar_total(df_projecao_bar)

columns_projecao_bar_com_soma = ['Data', 'Empresa', 'Saldo_Inicio_Dia', 'Valor_Liquido_Recebido', 'Valor_Projetado_Zig', 'Receita_Projetada_Extraord',
                                 'Despesas_Aprovadas_Pendentes', 'Despesas_Pagas', 'Saldo_Final']

st.dataframe(df_projecao_bar_com_soma[columns_projecao_bar_com_soma])

st.divider()

# Projeção Agrupada
st.markdown(
    """
    **Projeção de bares agrupados**: *Bar Brahma, Bar Léo, Bar Brasilia, Edificio Rolim, Hotel Maraba, 
    Jacaré, Orfeu, Riviera, Tempus, Escritorio Fabrica de Bares*
    """
)

df_projecao_grouped_com_soma = somar_total(df_projecao_grouped)

columns_projecao_grouped = ['Data', 'Saldo_Inicio_Dia', 'Valor_Liquido_Recebido', 'Valor_Projetado_Zig', 'Receita_Projetada_Extraord',
                            'Despesas_Aprovadas_Pendentes', 'Despesas_Pagas', 'Saldo_Final']

st.dataframe(df_projecao_grouped_com_soma[columns_projecao_grouped])


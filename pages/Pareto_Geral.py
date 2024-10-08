import streamlit as st
import pandas as pd
from utils.queries import *
from utils.functions.pareto import *
from utils.functions.dados_gerais import *
from utils.components import *

st.set_page_config(
  layout = 'wide',
  page_title = 'Análise Pereto',
  page_icon='🎯',
  initial_sidebar_state="collapsed"
)

if 'loggedIn' not in st.session_state or not st.session_state['loggedIn']:
  st.switch_page('Login.py')

def main ():
  config_sidebar()
  streamlit_style = """
    <style>
    iframe[title="streamlit_echarts.st_echarts"]{ height: 300px;} 
   </style>
    """
  st.markdown(streamlit_style, unsafe_allow_html=True)

  st.title('CURVA ABC - Diagrama de Pareto')

  dfComparativo = GET_COMPRAS_PRODUTOS_QUANTIA_NOME_ESTOQUE()

  tab1, tab2, tab3, tab4 = st.tabs(["COMPARATIVO ENTRE LOJAS", "ALIMENTOS", "BEBIDAS", " PRODUTOS DE LIMP/HIGIENE"])
  with tab1:
    comparativo_valor_mais_baixo(dfComparativo)
    comparativo_entre_lojas(dfComparativo)

  with tab2:
    dfNomeEstoque, dfNomeCompras, lojas = config_tabela_para_pareto(GET_COMPRAS_PRODUTOS_QUANTIA_NOME_ESTOQUE(), GET_COMPRAS_PRODUTOS_QUANTIA_NOME_COMPRA(), 'ALIMENTOS', 1)
    config_diagramas_pareto(dfNomeEstoque, dfNomeCompras, 'ALIMENTOS', 'Alimentos')
    with st.container(border=True):
      dfNomeEstoque = dfNomeEstoque.drop(['Categoria', 'Fator de Proporção'], axis=1)
      pesquisa_por_produto(dfNomeEstoque, 1, 'Compras de insumos arupadas por período selecionado')
    with st.container(border=True):
      config_compras_insumos_detalhadas('ALIMENTOS', 'datainicio1', 'datafim1', 'insumosdetalhados1', lojas)

  with tab3:
    dfNomeEstoque2, dfNomeCompras2, lojas2 = config_tabela_para_pareto(GET_COMPRAS_PRODUTOS_QUANTIA_NOME_ESTOQUE(), GET_COMPRAS_PRODUTOS_QUANTIA_NOME_COMPRA(), 'BEBIDAS', 2)
    config_diagramas_pareto(dfNomeEstoque2, dfNomeCompras2, 'BEBIDAS', 'Bebidas')
    with st.container(border=True):
      dfNomeEstoque2 = dfNomeEstoque2.drop(['Categoria', 'Fator de Proporção'], axis=1)
      pesquisa_por_produto(dfNomeEstoque2, 2, 'Compras de insumos arupadas por período selecionado')
    with st.container(border=True):
      config_compras_insumos_detalhadas('BEBIDAS', 'datainicio2', 'datafim2', 'insumosdetalhados2', lojas2)

  with tab4:
    dfNomeEstoque3, dfNomeCompras3, lojas3 = config_tabela_para_pareto(GET_COMPRAS_PRODUTOS_QUANTIA_NOME_ESTOQUE(), GET_COMPRAS_PRODUTOS_QUANTIA_NOME_COMPRA(), 'DESCARTAVEIS/HIGIENE E LIMPEZA', 3)
    config_diagramas_pareto(dfNomeEstoque3, dfNomeCompras3, 'DESCARTAVEIS/HIGIENE E LIMPEZA', 'Produtos de Limpeza e Higiene')
    with st.container(border=True):
      dfNomeEstoque3 = dfNomeEstoque3.drop(['Categoria', 'Fator de Proporção'], axis=1)
      pesquisa_por_produto(dfNomeEstoque3, 3, 'Compras de insumos arupadas por período selecionado')
    with st.container(border=True):
      config_compras_insumos_detalhadas('DESCARTAVEIS/HIGIENE E LIMPEZA', 'datainicio3', 'datafim3', 'insumosdetalhados3', lojas3)



if __name__ == '__main__':
  main()


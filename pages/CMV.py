import streamlit as st
import pandas as pd
from babel.dates import format_date
from utils.queries import *
from utils.functions.cmv import *
from utils.functions.dados_gerais import *
from utils.components import *
from utils.user import logout

st.set_page_config(
  layout = 'wide',
  page_title = 'CMV',
  page_icon=':⚖',
  initial_sidebar_state="collapsed"
)  
pd.set_option('future.no_silent_downcasting', True)

if 'loggedIn' not in st.session_state or not st.session_state['loggedIn']:
  st.switch_page('Login.py')


def main():
  config_sidebar()
  col, colx = st.columns([5, 1])
  with col:
    st.title('CMV')
  with colx:
    if st.button("Logout"):
      logout()
  
  st.divider()

  lojasComDados = preparar_dados_lojas_user()

  if 'Abaru - Priceless' in lojasComDados and 'Notiê - Priceless' in lojasComDados:
    lojasComDados.remove('Abaru - Priceless')
    lojasComDados.remove('Notiê - Priceless')
  if 'Blue Note - São Paulo' in lojasComDados and 'Blue Note SP (Novo)' in lojasComDados:
    lojasComDados.remove('Blue Note - São Paulo')
    lojasComDados.remove('Blue Note SP (Novo)')
    lojasComDados.append('Blue Note - Agregado')

  lojasComDados.sort()

  data_inicio_default, data_fim_default = preparar_datas_ultimo_mes()
  lojas_selecionadas, data_inicio, data_fim = criar_seletores_cmv(lojasComDados, data_inicio_default, data_fim_default)
  st.divider()

  data_inicio_mes_anterior = (data_inicio.replace(day=1) - timedelta(days=1)).replace(day=1)
  data_fim_mes_anterior = data_inicio.replace(day=1) - timedelta(days=1)

  df_faturamento_delivery, df_faturamento_zig, faturamento_bruto_alimentos, faturamento_bruto_bebidas, faturamento_alimentos_delivery, faturamento_bebidas_delivery = config_faturamento_bruto_zig(data_inicio, data_fim, lojas_selecionadas)
  df_faturamento_eventos, faturamento_alimentos_eventos, faturamento_bebidas_eventos = config_faturamento_eventos(data_inicio, data_fim, lojas_selecionadas, faturamento_bruto_alimentos, faturamento_bruto_bebidas)
  df_compras, compras_alimentos, compras_bebidas = config_compras(data_inicio, data_fim, lojas_selecionadas)
  df_valoracao_estoque_atual = config_valoracao_estoque(data_inicio, data_fim, lojas_selecionadas)
  df_valoracao_estoque_mes_anterior = config_valoracao_estoque(data_inicio_mes_anterior, data_fim_mes_anterior, lojas_selecionadas)
  df_diferenca_estoque = config_diferenca_estoque(df_valoracao_estoque_atual, df_valoracao_estoque_mes_anterior)
  df_variacao_estoque, variacao_estoque_alimentos, variacao_estoque_bebidas = config_variacao_estoque(df_valoracao_estoque_atual, df_valoracao_estoque_mes_anterior)
  valor_total, df_insumos_sem_pedido = config_insumos_blueme_sem_pedido(data_inicio, data_fim, lojas_selecionadas)
  df_insumos_com_pedido, valor_total_com_pedido, valor_alimentos, valor_bebidas, valor_hig, valor_gelo, valor_utensilios, valor_outros = config_insumos_blueme_com_pedido(data_inicio, data_fim, lojas_selecionadas)
  df_transf_e_gastos = config_transferencias_gastos(data_inicio, data_fim, lojas_selecionadas)


  df_faturamento_total = config_faturamento_total(df_faturamento_delivery, df_faturamento_zig, df_faturamento_eventos)
  df_valoracao_estoque_atual = format_columns_brazilian(df_valoracao_estoque_atual, ['Valor_em_Estoque'])

  cmv_alimentos = compras_alimentos - variacao_estoque_alimentos # - consumo interno + entrada transf - saida transf
  cmv_bebidas = compras_bebidas - variacao_estoque_bebidas
  faturamento_total_alimentos = faturamento_bruto_alimentos + faturamento_alimentos_delivery + faturamento_alimentos_eventos
  faturamento_total_bebidas = faturamento_bruto_bebidas + faturamento_bebidas_delivery + faturamento_bebidas_eventos

  if faturamento_total_alimentos != 0 and faturamento_total_bebidas != 0:
    cmv_percentual_alim = (cmv_alimentos / faturamento_total_alimentos) * 100
    cmv_percentual_bebidas = (cmv_bebidas / faturamento_total_bebidas) * 100
    cmv_percentual_geral = ((cmv_alimentos + cmv_bebidas)/(faturamento_total_alimentos+faturamento_total_bebidas)) * 100
  else:
    cmv_percentual_alim = 0
    cmv_percentual_bebidas = 0
    cmv_percentual_geral = 0

  faturamento_bruto_alimentos = format_brazilian(faturamento_bruto_alimentos)
  faturamento_bruto_bebidas = format_brazilian(faturamento_bruto_bebidas)
  faturamento_alimentos_delivery = format_brazilian(faturamento_alimentos_delivery)
  faturamento_bebidas_delivery = format_brazilian(faturamento_bebidas_delivery)
  faturamento_alimentos_eventos = format_brazilian(faturamento_alimentos_eventos)
  faturamento_bebidas_eventos = format_brazilian(faturamento_bebidas_eventos)
  compras_alimentos = format_brazilian(compras_alimentos)
  compras_bebidas = format_brazilian(compras_bebidas)
  variacao_estoque_alimentos = format_brazilian(variacao_estoque_alimentos)
  variacao_estoque_bebidas = format_brazilian(variacao_estoque_bebidas) 
  cmv_alimentos = format_brazilian(cmv_alimentos)
  cmv_bebidas = format_brazilian(cmv_bebidas)
  cmv_percentual_alim = format_brazilian(cmv_percentual_alim)
  cmv_percentual_bebidas = format_brazilian(cmv_percentual_bebidas)
  cmv_percentual_geral = format_brazilian(cmv_percentual_geral)


  col1, col2, col3, col4, col5, col6 = st.columns(6)
  with col1:
    with st.container(border=True):
      st.write('Faturam. Alimentos')
      st.write('R$', faturamento_bruto_alimentos)
  with col2:
    with st.container(border=True):
      st.write('Faturam. Bebidas')
      st.write('R$', faturamento_bruto_bebidas)  
  with col3:
    with st.container(border=True):
      st.write('Faturam. Alim. Delivery.')
      st.write('R$', faturamento_alimentos_delivery)  
  with col4:
    with st.container(border=True):
      st.write('Faturam. Beb. Delivery.')
      st.write('R$', faturamento_bebidas_delivery)
  with col5:
    with st.container(border=True):
      st.write('Faturam. Alim. Eventos.')
      st.write('R$', faturamento_alimentos_eventos)
  with col6:
    with st.container(border=True):
      st.write('Faturam. Beb. Eventos.')
      st.write('R$', faturamento_bebidas_eventos)

  col7, col8, col9, col10 = st.columns(4)
  with col7:
    with st.container(border=True):
      st.write('Variação Estoque Alimentos')
      st.write('R$', variacao_estoque_alimentos)
  with col8:
    with st.container(border=True):
      st.write('Variação Estoque Bebidas')
      st.write('R$', variacao_estoque_bebidas)
  with col9:
    with st.container(border=True):
      st.write('Compras Alimentos')
      st.write('R$', compras_alimentos)
  with col10:
    with st.container(border=True):
      st.write('Compras Bebidas')
      st.write('R$', compras_bebidas)

  col11, col12, col13, col14, col15 = st.columns(5)
  with col11:
    with st.container(border=True):
      st.write('CMV Alimentos')
      st.write(' R$', cmv_alimentos)
  with col12:
    with st.container(border=True):
      st.write('CMV Bebidas')
      st.write('R$', cmv_bebidas)
  with col13:
    with st.container(border=True):
      st.write('CMV Percentual Alimentos')
      st.write(cmv_percentual_alim, '%')
  with col14:
    with st.container(border=True):
      st.write('CMV Percentual Bebidas')
      st.write(cmv_percentual_bebidas, '%')
  with col15:
    with st.container(border=True):
      st.write('CMV Percentual Geral')
      st.write(cmv_percentual_geral, '%')

  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 12, 1])
    with col1:
      st.subheader('Faturamento Bruto por Categoria')
      
      st.dataframe(df_faturamento_total, hide_index=True)

  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 12, 1])
    with col1:
      st.subheader('Compras')
      st.dataframe(df_compras, hide_index=True)
      classificacoes = preparar_dados_classe_selecionada(df_insumos_sem_pedido, 'Classificacao')
      fornecedores_com_pedido = preparar_dados_classe_selecionada(df_insumos_com_pedido, 'Fornecedor') 
      with st.expander("Detalhes Insumos BlueMe Sem Pedido"):
        col3, col4, col5 = st.columns(3)
        with col4:
          classificacoes_selecionadas = st.multiselect(label='Selecione Classificação', options=classificacoes, key=1)
          df_insumos_sem_pedido = filtrar_por_classe_selecionada(df_insumos_sem_pedido, 'Classificacao', classificacoes_selecionadas)
        with col5:
          fornecedores_sem_pedido = preparar_dados_classe_selecionada(df_insumos_sem_pedido, 'Fornecedor') 
          fornecedores_selecionados = st.multiselect(label='Selecione Fornecedores', options=fornecedores_sem_pedido, key=3)
        df_insumos_sem_pedido = filtrar_por_classe_selecionada(df_insumos_sem_pedido, 'Fornecedor', fornecedores_selecionados)
        st.dataframe(df_insumos_sem_pedido, use_container_width=True, hide_index=True)
        st.write('Valor total = R$', valor_total)
      with st.expander("Detalhes Insumos BlueMe Com Pedido"):
        col3, col4, col5 = st.columns(3)
        with col5:
          fornecedores_selecionados = st.multiselect(label='Selecione Fornecedores', options=fornecedores_com_pedido, key=2)
        df_insumos_com_pedido = filtrar_por_classe_selecionada(df_insumos_com_pedido, 'Fornecedor', fornecedores_selecionados)
        st.dataframe(df_insumos_com_pedido, use_container_width=True, hide_index=True)
        st.write(
          f"Valor Total = R\\$ {valor_total_com_pedido},  \n"
          f"Valor Alimentos = R\\$ {valor_alimentos},  \n"
          f"Valor Bebidas = R\\$ {valor_bebidas},  \n"
          f"Valor Hig/Limp. = R\\$ {valor_hig},  \n"
          f"Valor Gelo = R\\$ {valor_gelo},  \n"
          f"Valor Utensílios = R\\$ {valor_utensilios},  \n"
          f"Valor Outros = R\\$ {valor_outros}"
        )


  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 12, 1])
    with col1:
      st.subheader('Valoração e Variação de Estoque')
      st.dataframe(df_variacao_estoque, use_container_width=True, hide_index=True)
      with st.expander("Detalhes Valoração Estoque Atual"):
        st.dataframe(df_valoracao_estoque_atual, use_container_width=True, hide_index=True)
      with st.expander("Diferença de Estoque"):
        st.dataframe(df_diferenca_estoque, use_container_width=True, hide_index=True)

  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 12, 1])
    with col1:
      st.subheader('Transferências e Gastos Extras')
      st.dataframe(df_transf_e_gastos, use_container_width=True, hide_index=True)


if __name__ == '__main__':
  main()

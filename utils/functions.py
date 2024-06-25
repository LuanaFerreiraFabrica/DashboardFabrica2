import streamlit as st
import pandas as pd
from workalendar.america import Brazil
from datetime import datetime, timedelta
from utils.queries import *
from utils.components import *

####### DADOS GERAIS #######

def config_sidebar():
  if st.session_state['loggedIn']:
    st.sidebar.title("Menu")
    st.sidebar.page_link("pages/Faturamento_Zig.py", label="Faturamento Zig")
    st.sidebar.page_link("pages/Faturamento_Receitas_Extraordinárias.py", label="Faturamento Receitas Extraordinárias")
    st.sidebar.page_link("pages/Despesas.py", label="Despesas")
    st.sidebar.page_link("pages/CMV.py", label="CMV")
    st.sidebar.page_link("pages/Pareto_Geral.py", label="Pareto")
  else:
    st.sidebar.write("Por favor, faça login para acessar o menu.")

def preparar_dados_lojas(df):
  DfLojas = df.copy()
  LojasComDados = DfLojas['Loja'].unique().tolist()
  LojasComDados.sort(key=str.lower)
  return LojasComDados

def preparar_dados_datas():
  # Inicializa o calendário do Brasil
  cal = Brazil()
  today = datetime.today()

  # Determinar o primeiro e último dia do mês passado
  first_day_of_last_month = today.replace(day=1) - timedelta(days=1)
  first_day_of_last_month = first_day_of_last_month.replace(day=1)
  last_day_of_last_month = today.replace(day=1) - timedelta(days=1)

  # Usar esses valores como default
  data_inicio_default = first_day_of_last_month.date()
  data_fim_default = last_day_of_last_month.date()
  
  return data_inicio_default, data_fim_default

def preparar_dados_classificacoes(dataframe):
  classificacoes = dataframe
  classificacoes = classificacoes['Classificacao'].unique().tolist()
  return classificacoes

def preparar_dados_fornecedores(dataframe):
  fornecedores = dataframe
  fornecedores = fornecedores['Fornecedor'].unique().tolist()
  return fornecedores

def filtrar_por_datas(dataframe, data_inicio, data_fim, categoria):
  data_inicio = pd.Timestamp(data_inicio)
  data_fim = pd.Timestamp(data_fim)
  
  # Ensure the 'categoria' column is converted to datetime correctly
  dataframe.loc[:, categoria] = pd.to_datetime(dataframe[categoria])
  
  # Apply the filter using .loc to avoid SettingWithCopyWarning
  dataframe_filtered = dataframe.loc[
      (dataframe[categoria] >= data_inicio) & (dataframe[categoria] <= data_fim)
  ]
  
  return dataframe_filtered

def filtrar_por_lojas(dataframe, lojas_selecionadas):
  if lojas_selecionadas:
    dataframe = dataframe[dataframe['Loja'].isin(lojas_selecionadas)]
  return dataframe

def filtrar_por_classificacao(dataframe, classificacoes_selecionadas):
  if classificacoes_selecionadas:
    dataframe = dataframe[dataframe['Classificação'].isin(classificacoes_selecionadas)]
  return dataframe

def filtrar_por_fornecedor(dataframe, fornecedores_selecionados):
  if fornecedores_selecionados:
    dataframe = dataframe[dataframe['Fornecedor'].isin(fornecedores_selecionados)]
  return dataframe

def format_brazilian(num):
  try:
    # Convertendo para float
    num = float(num)
    return f"{num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
  except (ValueError, TypeError):
    # Em caso de falha na conversão, retorna o valor original
    return num

def format_columns_brazilian(df, numeric_columns):
  for col in numeric_columns:
    if col in df.columns:
      df[col] = df[col].apply(format_brazilian)
  return df

def format_date_brazilian(df, date_column):
  df[date_column] = pd.to_datetime(df[date_column])
  df[date_column] = df[date_column].dt.strftime('%d-%m-%Y')
  return df

####### PÁGINA FATURAMENTO ZIG #######

def config_Faturamento_zig(lojas_selecionadas, data_inicio, data_fim):
  FaturamentoZig = GET_FATURAM_ZIG(data_inicio, data_fim)

  categorias_desejadas = ['Alimentos', 'Bebidas', 'Couvert', 'Gifts', 'Serviço']
  FaturamentoZig = FaturamentoZig[FaturamentoZig['Categoria'].isin(categorias_desejadas)]
  FaturamentoZig = filtrar_por_lojas(FaturamentoZig, lojas_selecionadas)
  FaturamentoZig = pd.DataFrame(FaturamentoZig)

  FaturamentoZig.drop(['Loja', 'Data_Evento'], axis=1, inplace=True)
  FaturamentoZig['Valor Bruto Venda'] = FaturamentoZig['Preco'] * FaturamentoZig['Qtd_Transacao']
  FaturamentoZig['Valor Líquido Venda'] = FaturamentoZig['Valor Bruto Venda'] - FaturamentoZig['Desconto']
  FaturamentoZig = FaturamentoZig.rename(columns = {'ID_Venda_EPM': 'ID Venda', 'Data_Venda': 'Data da Venda', 
                                                    'ID_Produto_EPM': 'ID Produto', 'Nome_Produto': 'Nome Produto', 
                                                    'Preco':'Preço Unitário', 'Qtd_Transacao': 'Quantia comprada', 
                                                    'Valor Bruto Venda': 'Valor Bruto Venda', 'Desconto':'Desconto', 
                                                    'Valor Líquido Venda': 'Valor Líquido Venda', 'Categoria': 'Categoria', 
                                                    'Tipo': 'Tipo'})
  
  FaturamentoZig = format_date_brazilian(FaturamentoZig, 'Data da Venda')
  FaturamentoZig = pd.DataFrame(FaturamentoZig)
  return FaturamentoZig

def config_orcamento_faturamento(lojas_selecionadas, data_inicio, data_fim):
  FaturamZigAgregado = GET_FATURAM_ZIG_AGREGADO()
  OrcamFaturam = GET_ORCAM_FATURAM()

  # Conversão de tipos para a padronização de valores
  FaturamZigAgregado['ID_Loja'] = FaturamZigAgregado['ID_Loja'].astype(str)
  OrcamFaturam['ID_Loja'] = OrcamFaturam['ID_Loja'].astype(str)  
  FaturamZigAgregado['Primeiro_Dia_Mes'] = pd.to_datetime(FaturamZigAgregado['Primeiro_Dia_Mes'], format='%y-%m-%d')
  OrcamFaturam['Primeiro_Dia_Mes'] = pd.to_datetime(OrcamFaturam['Primeiro_Dia_Mes'])

  # Padronização de categorias (para não aparecer as categorias não desejadas)
  categorias_desejadas = ['Alimentos', 'Bebidas', 'Couvert', 'Gifts', 'Serviço']
  OrcamFaturam = OrcamFaturam[OrcamFaturam['Categoria'].isin(categorias_desejadas)]
  FaturamZigAgregado = FaturamZigAgregado[FaturamZigAgregado['Categoria'].isin(categorias_desejadas)]

  # Faz o merge das tabelas
  OrcamentoFaturamento = pd.merge(FaturamZigAgregado, OrcamFaturam, on=['ID_Loja', 'Primeiro_Dia_Mes', 'Categoria'], how='left')
  OrcamentoFaturamento = OrcamentoFaturamento.dropna(subset=['Categoria'])
  OrcamentoFaturamento['Data_Evento'] = pd.to_datetime(OrcamentoFaturamento['Data_Evento'])

  # Agora filtra  
  OrcamentoFaturamento = filtrar_por_datas(OrcamentoFaturamento, data_inicio, data_fim, 'Data_Evento')
  OrcamentoFaturamento = filtrar_por_lojas(OrcamentoFaturamento, lojas_selecionadas)
  OrcamentoFaturamento = pd.DataFrame(OrcamentoFaturamento)

  # Exclui colunas que não serão usadas na análise, agrupa tuplas de valores de categoria iguais e renomeia as colunas restantes
  OrcamentoFaturamento.drop(['ID_Loja', 'Loja', 'Data_Evento', 'Primeiro_Dia_Mes'], axis=1, inplace=True)
  OrcamentoFaturamento = OrcamentoFaturamento.groupby('Categoria').agg({
        'Orcamento_Faturamento': 'sum',
        'Valor_Bruto': 'sum',
        'Desconto': 'sum',
        'Valor_Liquido': 'sum'
  }).reset_index()
  OrcamentoFaturamento.columns = ['Categoria', 'Orçamento', 'Valor Bruto', 'Desconto', 'Valor Líquido']

  # Conversão de valores para padronização
  cols = ['Orçamento', 'Valor Bruto', 'Desconto', 'Valor Líquido']
  OrcamentoFaturamento[cols] = OrcamentoFaturamento[cols].astype(float)

  # Criação da coluna 'Faturam - Orçamento' e da linha 'Total Geral'
  OrcamentoFaturamento['Faturam - Orçamento'] = OrcamentoFaturamento['Valor Líquido'] - OrcamentoFaturamento['Orçamento']
  Total = OrcamentoFaturamento[['Orçamento', 'Valor Bruto', 'Desconto', 'Valor Líquido', 'Faturam - Orçamento']].sum()
  NovaLinha = pd.DataFrame([{'Categoria': 'Total Geral', 'Orçamento': Total['Orçamento'], 'Valor Bruto': Total['Valor Bruto'],
                              'Desconto': Total['Desconto'], 'Valor Líquido': Total['Valor Líquido'], 
                              'Faturam - Orçamento': Total['Faturam - Orçamento']}])
  OrcamentoFaturamento = pd.concat([OrcamentoFaturamento, NovaLinha], ignore_index=True)
  
  OrcamentoFaturamento = pd.DataFrame(OrcamentoFaturamento)
  return OrcamentoFaturamento

def top_dez(dataframe, categoria):
  df = dataframe[dataframe['Categoria'] == categoria]

  # Agrupar por ID Produto
  agrupado = df.groupby(['ID Produto', 'Nome Produto']).agg({
    'Preço Unitário': 'mean',
    'Quantia comprada': 'sum',
    'Valor Bruto Venda': 'sum',
    'Desconto': 'sum',
    'Valor Líquido Venda': 'sum'
  }).reset_index()

  # Ordenar por Valor Líquido Venda em ordem decrescente
  topDez = agrupado.sort_values(by='Valor Líquido Venda', ascending=False).head(10).reset_index(drop=True)

  topDez['Valor Líquido Venda'] = topDez['Valor Líquido Venda'].astype(float)
  topDez['Valor Bruto Venda'] = topDez['Valor Bruto Venda'].astype(float)
  max_valor_liq_venda = topDez['Valor Líquido Venda'].max()
  max_valor_bru_venda = topDez['Valor Bruto Venda'].max()

  topDez = format_columns_brazilian(topDez, ['Preço Unitário', 'Desconto'])
  
  st.data_editor(
    topDez,
    width=1080,
    column_config={
      "Valor Líquido Venda": st.column_config.ProgressColumn(
        "Valor Líquido Venda",
        help="O Valor Líquido da Venda do produto em reais",
        format="R$%f",
        min_value=0,
        max_value=max_valor_liq_venda,
      ),
      "Valor Bruto Venda": st.column_config.ProgressColumn(
        "Valor Bruto Venda",
        help="O Valor Bruto da Venda do produto em reais",
        format="R$%f",
        min_value=0,
        max_value=max_valor_bru_venda,
      ),
    },
    disabled=True,
    hide_index=True,
  )
  return topDez


####### PÁGINA FATURAMENTO RECEITAS EXTRAORDINÁRIAS #######

def config_receit_extraord(lojas_selecionadas, data_inicio, data_fim):
  ReceitExtraord = GET_RECEIT_EXTRAORD()

  classificacoes = preparar_dados_classificacoes(GET_CLSSIFICACAO())
  ReceitExtraord = ReceitExtraord[ReceitExtraord['Classificacao'].isin(classificacoes)]

  ReceitExtraord = filtrar_por_datas(ReceitExtraord, data_inicio, data_fim, 'Data_Evento')
  ReceitExtraord = filtrar_por_lojas(ReceitExtraord, lojas_selecionadas)

  ReceitExtraord = pd.DataFrame(ReceitExtraord)
  ReceitExtraord.drop(['Loja', 'ID_Evento'], axis=1, inplace=True)

  ReceitExtraord = ReceitExtraord.rename(columns = {'ID_receita': 'ID', 'Cliente' : 'Cliente', 'Classificacao': 'Classificação', 
                                                    'Nome_Evento': 'Nome do Evento', 'Categ_AB': 'Categ. AB', 
                                                    'Categ_Aluguel': 'Categ. Aluguel', 'Categ_Artist': 'Categ. Artista', 
                                                    'Categ_Couvert': 'Categ. Couvert', 'Categ_Locacao': 'Categ. Locação', 
                                                    'Categ_Patroc': 'Categ. Patrocínio', 'Categ_Taxa_Serv': 'Categ. Taxa de serviço', 
                                                    'Valor_Total': 'Valor Total', 'Data_Evento': 'Data Evento'})

  ReceitExtraord = format_date_brazilian(ReceitExtraord, 'Data Evento')
  ReceitExtraord = pd.DataFrame(ReceitExtraord)
  return ReceitExtraord

def faturam_receit_extraord(df):
  df = df.drop(['ID', 'Cliente', 'Data Evento', 'Nome do Evento'], axis=1)
  colunas_a_somar = ['Categ. AB', 'Categ. Aluguel', 'Categ. Artista', 'Categ. Couvert', 'Categ. Locação', 
                     'Categ. Patrocínio', 'Categ. Taxa de serviço', 'Valor Total']
  agg_funct = {col: 'sum' for col in colunas_a_somar}
  agrupado = df.groupby(['Classificação']).agg(agg_funct).reset_index()
  agrupado['Quantia'] = df.groupby(['Classificação']).size().values
  agrupado = agrupado.sort_values(by='Quantia', ascending=False) 
  agrupado = format_columns_brazilian(agrupado, ['Categ. AB', 'Categ. Aluguel', 'Categ. Artista', 'Categ. Couvert', 'Categ. Locação', 'Categ. Patrocínio', 'Categ. Taxa de serviço', 'Valor Total'])

  return agrupado




####### PÁGINA DESPESAS #######

def config_despesas_por_classe(df):
  df = df.sort_values(by=['Class_Plano_de_Contas', 'Plano_de_Contas'])
  df = df.groupby(['Class_Plano_de_Contas', 'Plano_de_Contas'], as_index=False).agg({
    'Orcamento': 'sum',
    'ID': 'count',
    'Valor_Liquido': 'sum'
}).rename(columns={'ID': 'Qtd_Lancamentos'})

  formatted_rows = []
  current_category = None

  for _, row in df.iterrows():
    if row['Class_Plano_de_Contas'] != current_category:
      current_category = row['Class_Plano_de_Contas']
      formatted_rows.append({'Class_Plano_de_Contas': current_category, 'Plano_de_Contas': '', 'Qtd_Lancamentos': '', 'Orcamento': '', 'Valor_Liquido': ''})
    formatted_rows.append({'Class_Plano_de_Contas': '', 'Plano_de_Contas': row['Plano_de_Contas'], 'Qtd_Lancamentos': row['Qtd_Lancamentos'], 'Orcamento': row['Orcamento'], 'Valor_Liquido': row['Valor_Liquido']})

  df = pd.DataFrame(formatted_rows)
  df = df.rename(columns = {'Class_Plano_de_Contas': 'Classe Plano de Contas', 'Plano_de_Contas' : 'Plano de Contas', 'Qtd_Lancamentos': 'Qtd. de Lançamentos', 
                            'Orcamento': 'Orçamento', 'Valor_Liquido': 'Valor Realizado'})
  
  df['Orçamento'] = pd.to_numeric(df['Orçamento'], errors='coerce')
  df['Valor Realizado'] = pd.to_numeric(df['Valor Realizado'], errors='coerce')
  df.fillna({'Orçamento': 0, 'Valor Realizado': 0}, inplace=True)
  df['Orçamento'] = df['Orçamento'].astype(float)
  df['Valor Realizado'] = df['Valor Realizado'].astype(float)

  df['Orçamento - Realiz.'] = df['Orçamento'] - df['Valor Realizado']

  df = format_columns_brazilian(df, ['Orçamento', 'Valor Realizado', 'Orçamento - Realiz.'])
  return df

def config_despesas_detalhado(df):
  df.drop(['ID', 'Orcamento', 'Class_Plano_de_Contas'], axis=1, inplace=True)
  df = df.rename(columns = {'Loja': 'Loja', 'Plano_de_Contas' : 'Plano de Contas', 'Fornecedor': 'Fornecedor', 'Doc_Serie': 'Doc_Serie', 'Data_Evento': 'Data Emissão',
                             'Data_Vencimento': 'Data Vencimento', 'Descricao': 'Descrição', 'Status': 'Status', 'Valor_Liquido': 'Valor'})

  df = format_date_brazilian(df, 'Data Emissão')
  df = format_date_brazilian(df, 'Data Vencimento')

  df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
  df.fillna({'Valor': 0}, inplace=True)
  df['Valor'] = df['Valor'].astype(float)
  valorTotal = df['Valor'].sum()
  df = format_columns_brazilian(df, ['Valor'])
  return df, valorTotal



  ############# CMV FUNCTIONS #############

def merge_dataframes(df1, df2, df3, df4, df5, df6):
  # Realiza a junção das tabelas
  merged_df = df1.merge(df2, on=['ID_Loja', 'Primeiro_Dia_Mes'], how='left', suffixes=('', '_df2'))
  merged_df = merged_df.merge(df3, on=['ID_Loja', 'Primeiro_Dia_Mes'], how='left', suffixes=('', '_df3'))
  merged_df = merged_df.merge(df4, on=['ID_Loja', 'Primeiro_Dia_Mes'], how='left', suffixes=('', '_df4'))
  merged_df = merged_df.merge(df5, on=['ID_Loja', 'Primeiro_Dia_Mes'], how='left', suffixes=('', '_df5'))
  merged_df = merged_df.merge(df6, on=['ID_Loja', 'Primeiro_Dia_Mes'], how='left', suffixes=('', '_df6'))

  # Preenche os valores nulos com zero (similar ao COALESCE)
  merged_df.fillna(0, inplace=True)
  merged_df.infer_objects(copy=False)

  # Calcular as colunas de compras (alimentos e bebidas)
  merged_df['Compras_Alimentos'] = (merged_df['BlueMe_Sem_Pedido_Alimentos'] + 
                                    merged_df['BlueMe_Com_Pedido_Valor_Liq_Alimentos'])
  merged_df['Compras_Bebidas'] = (merged_df['BlueMe_Sem_Pedido_Bebidas'] + 
                                  merged_df['BlueMe_Com_Pedido_Valor_Liq_Bebidas'])

  # Selecionar as colunas conforme a query SQL original
  result_df = merged_df[['ID_Loja', 'Loja', 'Primeiro_Dia_Mes', 'Faturam_Bruto_Aliment', 
                         'Faturam_Bruto_Bebidas', 'Estoque_Inicial_Alimentos', 
                         'Estoque_Final_Alimentos', 'Estoque_Inicial_Bebidas', 
                         'Estoque_Final_Bebidas', 'Estoque_Inicial_Descart_Hig_Limp', 
                         'Estoque_Final_Descart_Hig_Limp', 'BlueMe_Sem_Pedido_Alimentos', 
                         'BlueMe_Com_Pedido_Valor_Liq_Alimentos', 'Compras_Alimentos', 
                         'BlueMe_Sem_Pedido_Bebidas', 'BlueMe_Com_Pedido_Valor_Liq_Bebidas', 
                         'Compras_Bebidas', 'Entrada_Transf_Alim', 
                         'Saida_Transf_Alim', 'Entrada_Transf_Bebidas', 
                         'Saida_Transf_Bebidas', 'Consumo_Interno', 'Quebras_e_Perdas']]
  return result_df

def config_tabelas_iniciais_cmv(lojas_selecionadas, data_inicio, data_fim):
  df1 = GET_FATURAM_ZIG_ALIM_BEB_MENSAL()
  df2 = GET_ESTOQUES_POR_CATEG_AGRUPADOS()
  df3 = GET_INSUMOS_AGRUPADOS_BLUE_ME_POR_CATEG_SEM_PEDIDO()  
  df4 = GET_INSUMOS_AGRUPADOS_BLUE_ME_POR_CATEG_coM_PEDIDO()
  df5 = GET_TRANSF_ESTOQUE_AGRUPADOS()  
  df6 = GET_PERDAS_E_CONSUMO_AGRUPADOS()

  df3 = df3[df3['ID_Loja'] != 296]

  df1 = filtrar_por_lojas(df1, lojas_selecionadas)
  df1 = filtrar_por_datas(df1, data_inicio, data_fim, 'Primeiro_Dia_Mes')
  df2 = filtrar_por_lojas(df2, lojas_selecionadas)
  df2 = filtrar_por_datas(df2, data_inicio, data_fim, 'Primeiro_Dia_Mes')
  df3 = filtrar_por_lojas(df3, lojas_selecionadas)
  df3 = filtrar_por_datas(df3, data_inicio, data_fim, 'Primeiro_Dia_Mes')
  df4 = filtrar_por_lojas(df4, lojas_selecionadas)
  df4 = filtrar_por_datas(df4, data_inicio, data_fim, 'Primeiro_Dia_Mes')
  df5 = filtrar_por_lojas(df5, lojas_selecionadas)
  df5 = filtrar_por_datas(df5, data_inicio, data_fim, 'Primeiro_Dia_Mes')
  df6 = filtrar_por_lojas(df6, lojas_selecionadas)
  df6 = filtrar_por_datas(df6, data_inicio, data_fim, 'Primeiro_Dia_Mes')

  dfFinal = merge_dataframes(df1, df2, df3, df4, df5, df6)
  return dfFinal

def config_tabela_CMV(df):
  df = pd.DataFrame(df)
  newDF = df.drop(['ID_Loja', 'BlueMe_Sem_Pedido_Alimentos', 'BlueMe_Com_Pedido_Valor_Liq_Alimentos', 
                   'Compras_Alimentos', 'BlueMe_Sem_Pedido_Bebidas', 'BlueMe_Com_Pedido_Valor_Liq_Bebidas', 
                   'Compras_Bebidas', 'Entrada_Transf_Alim', 'Saida_Transf_Alim', 'Entrada_Transf_Bebidas', 
                   'Saida_Transf_Bebidas', 'Consumo_Interno', 'Quebras_e_Perdas', ], axis=1)
  
  newDF.rename(columns = {'Loja': 'Loja', 'Primeiro_Dia_Mes': 'Mês', 'Faturam_Bruto_Aliment': 'Faturam. Alim.', 
                         'Estoque_Inicial_Alimentos': 'Estoque Inicial Alim.', 'Estoque_Final_Alimentos': 'Estoque Final Alim.',
                          'Faturam_Bruto_Bebidas': 'Faturam. Bebidas', 'Estoque_Inicial_Bebidas': 'Estoque Inicial Bebidas', 
                         'Estoque_Final_Bebidas': 'Estoque Final Bebidas', 'Estoque_Inicial_Descart_Hig_Limp': 'Estoque Inicial Limp/Hig', 
                         'Estoque_Final_Descart_Hig_Limp': 'Estoque Final Limp/Hig'}, inplace=True)
  
  newDF = format_date_brazilian(newDF, 'Mês')
  return newDF

def config_tabela_compras(df):
  df = pd.DataFrame(df)
  newDF = df.drop(['ID_Loja', 'Faturam_Bruto_Aliment', 'Faturam_Bruto_Bebidas', 
                   'Estoque_Inicial_Alimentos', 'Estoque_Final_Alimentos', 'Estoque_Inicial_Bebidas', 
                   'Estoque_Final_Bebidas', 'Estoque_Inicial_Descart_Hig_Limp', 
                   'Estoque_Final_Descart_Hig_Limp', 'Entrada_Transf_Alim', 'Saida_Transf_Alim', 
                   'Entrada_Transf_Bebidas', 'Saida_Transf_Bebidas', 'Consumo_Interno', 'Quebras_e_Perdas', ], axis=1)
  
  newDF.rename(columns = {'Loja': 'Loja', 'Primeiro_Dia_Mes': 'Mês', 'Compras_Alimentos': 'Compras Alim.', 'BlueMe_Sem_Pedido_Alimentos': 'BlueMe S/ Pedido Alim.', 
                          'BlueMe_Com_Pedido_Valor_Liq_Alimentos': 'BlueMe C/ Pedido Alim.',  'Compras_Bebidas': 'Compras Bebidas',
                          'BlueMe_Sem_Pedido_Bebidas': 'BlueMe S/ Pedido Bebidas', 'BlueMe_Com_Pedido_Valor_Liq_Bebidas': 'BlueMe C/ Pedido Bebidas'},
                          inplace=True)

  newDF = format_date_brazilian(newDF, 'Mês')
  return newDF

def config_tabela_transferencias(df):
  df = pd.DataFrame(df)
  newDF = df.drop(['ID_Loja', 'Faturam_Bruto_Aliment', 'Faturam_Bruto_Bebidas', 'Estoque_Inicial_Alimentos', 'Estoque_Final_Alimentos', 
                   'Estoque_Inicial_Bebidas', 'Estoque_Final_Bebidas', 'Estoque_Inicial_Descart_Hig_Limp', 
                   'Estoque_Final_Descart_Hig_Limp', 'BlueMe_Sem_Pedido_Alimentos', 'BlueMe_Com_Pedido_Valor_Liq_Alimentos', 
                   'Compras_Alimentos', 'BlueMe_Sem_Pedido_Bebidas', 'BlueMe_Com_Pedido_Valor_Liq_Bebidas', 'Compras_Bebidas'], axis=1)
  
  newDF.rename(columns = {'Loja': 'Loja', 'Primeiro_Dia_Mes': 'Mês', 'Entrada_Transf_Alim': 'Entrada Transf. Alim.', 'Saida_Transf_Alim': 'Saida Transf. Alim.', 
                          'Entrada_Transf_Bebidas': 'Entrada Transf. Bebidas', 'Saida_Transf_Bebidas': 'Saida Transf. Bebidas', 
                          'Consumo_Interno': 'Consumo Interno', 'Quebras_e_Perdas': 'Quebras e Perdas'}, inplace=True)

  newDF = format_date_brazilian(newDF, 'Mês')
  return newDF

def config_insumos_blueme_sem_pedido(df, data_inicio, data_fim):
  df = pd.DataFrame(df)
  df = df.drop(['ID_Loja', 'Primeiro_Dia_Mes'], axis=1)
  df = filtrar_por_datas(df, data_inicio, data_fim, 'Data_Emissao')

  df = format_date_brazilian(df, 'Data_Emissao')

  df.rename(columns = {'tdr_ID': 'tdr ID', 'Loja': 'Loja', 'Fornecedor': 'Fornecedor', 'Plano_de_Contas': 'Classificacao',
                       'Doc_Serie': 'Doc_Serie', 'Data_Emissao': 'Data Emissão', 'Valor_Liquido': 'Valor Líquido'}, inplace=True)

  return df


def config_insumos_blueme_com_pedido(df, data_inicio, data_fim):
  df = pd.DataFrame(df)
  df = df.drop(['ID_Loja', 'Primeiro_Dia_Mes'], axis=1)
  df = filtrar_por_datas(df, data_inicio, data_fim, 'Data_Emissao')

  df = format_date_brazilian(df, 'Data_Emissao')

  df.rename(columns = {'tdr_ID': 'tdr ID', 'Loja': 'Loja', 'Fornecedor': 'Fornecedor', 'Doc_Serie': 'Doc_Serie', 'Data_Emissao': 'Data Emissão',
                       'Valor_Liquido': 'Valor Líquido', 'Valor_Insumos': 'Valor Insumos', 'Valor_Liq_Alimentos': 'Valor Líq. Alimentos',
                       'Valor_Liq_Bebidas': 'Valor Líq. Bebidas', 'Valor_Liq_Descart_Hig_Limp': 'Valor Líq. Hig/Limp.', 
                       'Valor_Liq_Outros': 'Valor Líq. Outros'}, inplace=True)
  return df




#########################  DIAGRAMA DE PARETO  ############################

def config_compras_quantias(df, data_inicio, data_fim, lojas_selecionadas):
  df = df.sort_values(by='Nome Produto', ascending=False)

  df = filtrar_por_datas(df, data_inicio, data_fim, 'Data Compra')
  df = filtrar_por_lojas(df, lojas_selecionadas)

  df['Quantidade'] = df['Quantidade'].astype(str)
  df['Valor Total'] = df['Valor Total'].astype(str)
  df['Quantidade'] = df['Quantidade'].str.replace(',', '.').astype(float)
  df['Valor Total'] = df['Valor Total'].str.replace(',', '.').astype(float)
  df['Fator de Proporção'] = df['Fator de Proporção'].astype(float)

  df = df.groupby(['Nome Produto', 'Loja', 'Categoria'], as_index=False).agg({
    'Quantidade': 'sum',
    'Valor Total': 'sum',
    'Unidade de Medida': 'first',
    'Fator de Proporção': 'first',
    'Fornecedor': 'first'
  })

  df['Quantidade Ajustada'] = df['Quantidade'] * df['Fator de Proporção']
  df['Valor Unitário'] = df['Valor Total'] / df['Quantidade']
  df['Valor Unit. Ajustado'] = df['Valor Total'] / df['Quantidade Ajustada']

  df['Quantidade'] = df['Quantidade'].round(2)
  df['Quantidade Ajustada'] = df['Quantidade Ajustada'].round(2)
  df['Valor Total'] = df['Valor Total'].round(2)
  df['Valor Unitário'] = df['Valor Unitário'].round(2)
  df['Valor Unit. Ajustado'] = df['Valor Unit. Ajustado'].round(2)

  return df


def config_por_categ_avaliada(df, categoria):
  df.sort_values(by=categoria, ascending=False, inplace=True)
  df['Porcentagem Acumulada'] = df[categoria].cumsum() / df[categoria].sum() * 100
  df['Porcentagem'] = (df[categoria] / df[categoria].sum()) * 100
  return df


def preparar_filtros(tabIndex):
  lojasComDados = preparar_dados_lojas(GET_FATURAM_ZIG_ALIM_BEB_MENSAL())
  data_inicio_default, data_fim_default = preparar_dados_datas()
  lojas_selecionadas, data_inicio, data_fim = criar_seletores_pareto(lojasComDados, data_inicio_default, data_fim_default, tab_index=tabIndex)
  st.divider()
  return lojas_selecionadas, data_inicio, data_fim



def config_tabela_para_pareto(dfNomeEstoque, dfNomeCompras, categoria, key):
  lojas_selecionadas, data_inicio, data_fim = preparar_filtros(key)
  dfNomeEstoque = config_compras_quantias(dfNomeEstoque, data_inicio, data_fim, lojas_selecionadas)
  dfNomeCompras = config_compras_quantias(dfNomeCompras, data_inicio, data_fim, lojas_selecionadas)

  dfNomeEstoque = dfNomeEstoque[dfNomeEstoque['Categoria'] == categoria]
  return dfNomeEstoque, dfNomeCompras


def config_diagramas_pareto(dfNomeEstoque, dfNomeCompras, categoria, categString):
  df_por_valor = config_por_categ_avaliada(dfNomeEstoque.copy(), 'Valor Total')
  df_valor_unitario = config_por_categ_avaliada(dfNomeCompras.copy(), 'Valor Unitário')
  df_valor_unit_ajust = config_por_categ_avaliada(dfNomeEstoque.copy(), 'Valor Unit. Ajustado')  

  keyDiagrama1 = categoria + '_valor'
  keyDiagrama2 = categoria + '_valor_unitario'
  keyDiagrama3 = categoria + '_valor_unit_ajust'

  with st.container(border=True):
    st.subheader('Diagrama de Pareto sobre ' + categString + ' em relação ao valor total')
    diagrama_pareto_por_categ_avaliada(df_por_valor, 'Valor Total', key=keyDiagrama1)
  with st.container(border=True):    
    st.subheader('Diagrama de Pareto sobre ' + categString + ' em relação ao valor Unitário de cada')
    diagrama_pareto_por_categ_avaliada(df_valor_unitario, 'Valor Unitário', key=keyDiagrama2)
  with st.container(border=True):
    st.subheader('Diagrama de Pareto sobre ' + categString + ' em relação ao valor unitário ajustado')
    diagrama_pareto_por_categ_avaliada(df_valor_unit_ajust, 'Valor Unit. Ajustado', key=keyDiagrama3)


def pesquisa_por_produto(dfNomeEstoque, key):
  dfNomeEstoque = dfNomeEstoque.drop(['Fornecedor'], axis=1)
  col0, col, col1, col2 = st.columns([1.6, 15, 8, 2])
  with col:
    st.subheader('Informações detalhadas dos produtos')
  with col1:
    search_term = st.text_input('Pesquisar por nome do produto:', '', key=key)
    if search_term:
      filtered_df = dfNomeEstoque[dfNomeEstoque['Nome Produto'].str.contains(search_term, case=False, na=False)]
    else:
      filtered_df = dfNomeEstoque
  row1 = st.columns([1, 15, 1])
  row1[1].dataframe(filtered_df, width=1100 ,hide_index=True)

def create_columns_comparativo(df):
  df.loc[:,'Quantidade'] = df['Quantidade'].astype(str)
  df.loc[:,'Valor Total'] = df['Valor Total'].astype(str)
  df.loc[:,'Quantidade'] = df['Quantidade'].str.replace(',', '.').astype(float)
  df.loc[:, 'Valor Total'] = df['Valor Total'].str.replace(',', '.').astype(float)
  df = df.groupby(['Nome Produto', 'Loja'], as_index=False).agg({
    'Valor Total': 'sum',
    'Quantidade': 'sum',
    'Fornecedor': 'first',
    'Unidade de Medida': 'first',
  })

  df['Valor Unitário'] = df['Valor Total'] / df['Quantidade']
  df['Valor Unitário'] = df['Valor Unitário'].round(2)
  df = df.drop(['Valor Total', 'Quantidade', 'Loja'], axis=1)

  return df


def comparativo_entre_lojas(df):
  data_inicio_default, data_fim_default = preparar_dados_datas()
  # Seletores para loja e produto
  lojas = df['Loja'].unique()
  col, col1 = st.columns(2)
  with col:
    loja1 = st.selectbox('Selecione a primeira loja:', lojas)
  with col1:
    loja2 = st.selectbox('Selecione a segunda loja:', lojas)

  col, col1, col2, col3 = st.columns([3, 2, 1, 1])
  with col:
    search_term = st.text_input('Pesquise parte do nome de um produto:', '')
    # Filtrando produtos com base no termo de pesquisa
    if search_term:
      produtos_filtrados = df[df['Nome Produto'].str.contains(search_term, case=False, na=False)]['Nome Produto'].unique()
    else:
      produtos_filtrados = df['Nome Produto'].unique()
  with col1:
    # Seletor de produto com base na pesquisa
    if len(produtos_filtrados) > 0:
      produto_selecionado = st.selectbox('Selecione o produto com base na pesquisa:', produtos_filtrados)
    else:
      produto_selecionado = None
      st.warning('Nenhum produto encontrado.')
  with col2:
    data_inicio = st.date_input('Data de Início', value=data_inicio_default, key='data_inicio_input', format="DD/MM/YYYY")
  with col3:
    data_fim = st.date_input('Data de Fim', value=data_fim_default, key='data_fim_input', format="DD/MM/YYYY")

  data_inicio = pd.to_datetime(data_inicio)
  data_fim = pd.to_datetime(data_fim)

  # Filtrando os dataframes com base nas seleções
  if produto_selecionado:
    df_loja1 = df[(df['Loja'] == loja1) & (df['Nome Produto'] == produto_selecionado)]
    df_loja2 = df[(df['Loja'] == loja2) & (df['Nome Produto'] == produto_selecionado)]

    filtrar_por_datas(df_loja1, data_inicio, data_fim, 'Data Compra')
    filtrar_por_datas(df_loja2, data_inicio, data_fim, 'Data Compra')

    df_loja1 = create_columns_comparativo(df_loja1)
    df_loja2 = create_columns_comparativo(df_loja2)

    # Exibindo os dataframes filtrados lado a lado
    with st.container(border=True):
      col1, col2 = st.columns(2)
      with col1:
        st.subheader(f'{loja1}')
        st.dataframe(df_loja1, hide_index=True)

      with col2:
        st.subheader(f'{loja2}')
        st.dataframe(df_loja2, hide_index=True)
  else:
      st.info('Selecione um produto para visualizar os dados.')
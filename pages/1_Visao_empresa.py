# Importacao das bibliotecas
import pandas as pd
import plotly.express as px
import folium
import streamlit as st
from PIL import Image
# importação da biblioteca para encontrarmos a distância entre os pontos 
from haversine import haversine
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Empresa', page_icon='📈',layout='wide')

# ===================
# Funções
# ===================

def clean_code(df1):
    ''' ESTA FUNÇÃO TEM A RESPONSABILIDADE DE LIMPAR O DATAFRAME
        
        TIPOS DE LIMPEZA:
        1. REMOÇÃO DOS DADOS NaN
        2. MUDANÇA DO TIPO DE COLUNA DE DADOS
        3. REMOÇÃO DOS ESPAÇOS DAS VARIÁVEIS EM TEXTO
        4. FORMATAÇÃO DA COLUNA DE DATAS
        5. LIMPEZA DA COLUNA DE TEMPO (REMOÇÃO DO TEXTO DA VARIÁVEL NUMÉRICA)

        INPUT: DATAFRAME
        OUTPUT: DATAFRAME
    
    '''
    
    # convertendo a coluna age em int
    linhas_selecionadas = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas,]
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    # convertendo a coluna ratings em float
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    # convertendo a coluna Order_Date para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y') 
    # convertendo o multiple_deliveries para int
    linhas_selecionadas = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas,]
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    df1 = df1.reset_index(drop=True)
    # removendo os espaços do ID
    df1.loc[:,'ID'] = df1.loc[:,'ID'].str.strip()
    
    # Vamos realizar aqui mais uma limpeza de dados para remover o 'NaN ' das cidades
    linhas_selecionadas = df1['City'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas,]
    df1 = df1.reset_index(drop=True)
    # limpeza da coluna Time Orderd
    linhas_selecionadas = df1['Time_Orderd'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas,]
    # limpeza da coluna Weatherconditions
    linhas_selecionadas = df1['Weatherconditions'] != 'conditions NaN'
    df1 = df1.loc[linhas_selecionadas,]
    # limpeza do road traffic density
    linhas_selecionadas = df1['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas,]
    # limpeza dos valores faltantes na coluna Festival
    linhas_selecionadas = df1['Festival'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas,]
    df1 = df1.reset_index(drop=True)
    # limpeza da coluna Weatherconditions removendo o condition
    
    df1['Weatherconditions'] = df1['Weatherconditions'].str.replace('conditions ','',regex=False)
    df1['Time_taken(min)'] = df1['Time_taken(min)'].str.replace('(min) ','',regex=False)
    # convertendo a coluna time taken de str para int
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1

def order_metric(df1):
    # seleção de colunas
    cols = ['ID','Order_Date']
    #execução do agrupamento por Data de pedido
    df_aux = df1.loc[:,cols].groupby(['Order_Date']).count().reset_index()
    # desenhar o gráfico de linhas
    fig = px.bar(df_aux, x='Order_Date',y='ID')
    return fig            

def traffic_order_share(df1):
    df_aux = df1.loc[:,['ID','Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    # Porém, queremos a porcertagem. Então iremos realizar uma divição para encontrar o percentual
    df_aux['entregas_%'] = (df_aux['ID'] / df_aux['ID'].sum())*100 
    fig = px.pie(df_aux, values = 'entregas_%', names = 'Road_traffic_density')
    return fig                        
    
def traffic_order_city(df1):
   # para fazermos esse gráfico necessitamos de três colunas ID, CITY e tipo de tráfego
   df_aux = df1.loc[:,['ID','Road_traffic_density','City']].groupby(['City','Road_traffic_density']).count().reset_index()
   # para construir um gráfico de bolhas utilizamos o livro scatter()
   fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
   return fig

def order_by_week(df1):
   # criar uma coluna nova para auxiliar
   df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')  
   # O .dt transforma a lista numa sequencia de datas
   # O %U indica que a semana inicia pelo domingo.
   #Para conferir se a semana está correta, verificar no google calendar 365
   df_aux = df1.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index()
   fig = px.line(df_aux,x='week_of_year',y='ID')
   return fig
    
def order_share_week(df1):
  # Quantidade de pedidos por semana / Número únicos de entregadores por semana
  # agrupamos primeiro pedidos por semana
  df_aux01 = df1.loc[:,['ID','week_of_year']].groupby(['week_of_year']).count().reset_index()
  # agora, agrupamos entregadores por semana
  df_aux02 = df1.loc[:,['Delivery_person_ID','week_of_year']].groupby(['week_of_year']).nunique().reset_index()
  # unindo os dois data frames
  df_aux = pd.merge(df_aux01,df_aux02,how='inner')
  df_aux['Order_by_Deliver'] = df_aux['ID'] / df_aux ['Delivery_person_ID']
  fig = px.line(df_aux, x='week_of_year',y='Order_by_Deliver')
  return fig
def country_maps(df1):
   df_aux = df1.loc[:,['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']].groupby(['City','Road_traffic_density']).median().reset_index()
   map_1 = folium.Map()
   # para criar um mapa com os pinos é necessário criar uma lista com for de maneira iterativa
   for index, location_info in df_aux.iterrows():
       folium.Marker( [location_info['Delivery_location_latitude'], 
                        location_info['Delivery_location_longitude']], 
                        popup=location_info[['City','Road_traffic_density']]).add_to(map_1)
   folium_static(map_1,width=1024, height=600)

# -------------------------------------------- INÍCIO DA ESTRUTURA LÓGICA DO CÓDIGO -------------------------------------------- #
#carregando o dataset
df = pd.read_csv("train.csv")

# limpando os dados 
df1 = clean_code(df)


# ============================
# Visao empresa
# ============================



# seleção de colunas

cols = ['ID','Order_Date']

#execução do agrupamento por Data de pedido
df_aux = df1.loc[:,cols].groupby(['Order_Date']).count().reset_index()

# desenhar o gráfico de linhas

px.bar(df_aux, x='Order_Date',y='ID')

# ===============================
# Barra lateral
# ===============================
st.header("Marketplace - Visão Empresa")

# image_path=('/Users/wigso/Documents/repos/FTC/CICLO-03/images/image.jpg')
image = Image.open('image.jpg')
st.sidebar.image(image,width=300)


st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('''---''')

st.sidebar.markdown('## Selecione uma data limite')
date_slider=st.sidebar.slider(
    'Até qual valor?',
    value=pd.datetime(2022,4,13),
    min_value=pd.datetime(2022,2,11),
    max_value=pd.datetime(2022,4,6),
    format='DD-MM-YYYY')
st.header(date_slider)
st.sidebar.markdown('''---''')

traffic_options=st.sidebar.multiselect(
    'Quais as condições de trânsito',
    ['Low ','Medium ','High ','Jam '],
    default=['Low ','Medium ','High ','Jam '])

st.sidebar.markdown('''---''')
st.sidebar.markdown('### Powered by Wigson')


# filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider

df1 = df1.loc[linhas_selecionadas,:]

# filtro de trânsito
linhas_selecionadas = df1[ 'Road_traffic_density' ].isin( traffic_options )
df1 = df1.loc[ linhas_selecionadas, : ]
st.dataframe(df1)



# ===============================
# layout no streamlit
# ===============================    

tab1,tab2,tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])

with tab1:
    #Order Metric
    with st.container():
        st.markdown('# Orders by date')
        fig = order_metric(df1)
        st.plotly_chart(fig,use_conteiner_width=True)
                    
        with st.container():
            col1, col2 = st.columns( 2 )
    
            with col1:
                st.header('Traffic Order Share')
                fig = traffic_order_share(df1)
                         
                st.plotly_chart(fig,use_container_width=True)
                    
            with col2:
                st.header('Traffic Order City')
                fig = traffic_order_city(df1)
                
                st.plotly_chart(fig,use_container_width=True)
    
with tab2:
    with st.container():
        st.markdown('# Orders by Week')                
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)
    
    with st.container():
        st.markdown('# Orders Share by Week')
        fig = order_share_week(df1)
        st.plotly_chart(fig, use_container_width=True)
        
with tab3:
    st.markdown('# Country Maps')
    country_maps(df1)
        



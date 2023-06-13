# Importacao das bibliotecas
import pandas as pd
import plotly.express as px
import folium
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from PIL import Image
# importação da biblioteca para encontrarmos a distância entre os pontos 
from haversine import haversine
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Restaurantes', page_icon='♨️',layout='wide')

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

def distance(df1,fig):
    # criação de nova coluna para aplicarmos a distância entre os pontos do restaurante e ponto de entrega
    # df2.insert(8, column = 'distance(Km)', value = 0)
    # seleção das colunas e aplicando a função haversine
    if fig==False:
        cols = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude'] 
        df1['distance(Km)'] = df1.loc[:,cols].apply( lambda x: haversine( (x['Restaurant_latitude'],x['Restaurant_longitude']),     (x['Delivery_location_latitude'],x['Delivery_location_longitude']) ), axis=1)
        avg_distance = np.round(df1['distance(Km)'].mean(),2)
        return avg_distance
    else:
       # criação de nova coluna para aplicarmos a distância entre os pontos do restaurante e ponto de entrega
       # df2.insert(8, column = 'distance(Km)', value = 0)
       # seleção das colunas e aplicando a função haversine
       cols = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
       df1['distance(Km)'] = df1.loc[:,cols].apply( lambda x: haversine( (x['Restaurant_latitude'],x['Restaurant_longitude']),(x['Delivery_location_latitude'],x['Delivery_location_longitude']) ), axis=1)
       # colunas_selecionadas = ['distance(Km)','City']  
       avg_distance = df1.loc[:,['distance(Km)','City']].groupby(['City']).mean().reset_index()
       # criando o gráfico e sua exibição
       fig = go.Figure(data=[go.Pie( labels=avg_distance['City'], values=avg_distance['distance(Km)'], pull=[0,0.1,0])]) 
       return fig 


def avg_std_time(df1,festival, op):
   """
      Esta função calcula o tempo médio e o desvio padrão do tempo de entrega
      Parâmetros:
      Input:
        - df: Dataframe com os dados necessários para o cálculo
        - op: Tipo de operação que precisa ser calculado
              'avg_time': Calcula o tempo médio
              'std_time': Calcula o desvio padrão do tempo
      Output: 
        - df: Dataframe com 2 colunas e 1 linha.
   """
   cols = ['Time_taken(min)','Festival']
   df_aux = df1.loc[:,cols].groupby(['Festival']).agg({'Time_taken(min)': ['mean','std']})
   df_aux.columns = ['avg_time','std_time']
   df_aux = df_aux.reset_index()
   df_aux = np.round(df_aux.loc[df_aux['Festival']==festival,op],2)
   return df_aux

def avg_std_time_graph(df1):
   cols = ['City','Time_taken(min)']
   df_aux = df1.loc[:,cols].groupby(['City']).agg(['mean','std'])
   df_aux.columns = ['avg_time','std_time']
   df_aux = df_aux.reset_index()
   fig = go.Figure()
   fig.add_trace(go.Bar(name = 'Control',x=df_aux['City'],y=df_aux['avg_time'],error_y=dict(type='data',array=df_aux['std_time'])))
   fig.update_layout(barmode='group')
   return fig

def avg_std_time_on_traffic(df1):
    cols = ['City','Time_taken(min)','Road_traffic_density']
    df_aux = df1.loc[:,cols].groupby(['City','Road_traffic_density']).agg(['mean','std'])
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux,path=['City', 'Road_traffic_density'], values = 'avg_time', color = 'std_time', color_continuous_scale = 'RdBu', color_continuous_midpoint=np.average(df_aux['std_time']))
    return fig
   
    
    
#carregando o dataset
df = pd.read_csv("train.csv")

# limpeza do dataset
df1 = clean_code(df)

# ====================================
# Visao empresa
# ====================================


# seleção de colunas
cols = ['ID','Order_Date']

#execução do agrupamento por Data de pedido
df_aux = df1.loc[:,cols].groupby(['Order_Date']).count().reset_index()

# desenhar o gráfico de linhas

px.bar(df_aux, x='Order_Date',y='ID')

# ===============================
# Barra lateral
# ===============================
st.header("Marketplace - Visão Restaurantes")

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

# ==============================================
# VISÃO RESTAURANTES
# ==============================================

# ==============================================
# LAYOUT NO STREAMLIT
# ==============================================

tab1, tab2, tab3 = st.tabs(['Visão Restaurantes','_','_'])

with tab1: 
    with st.container():
        st.markdown('''---''')
        st.title('Overal Metrics')

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            unicos = df1['Delivery_person_ID'].nunique()
            col1.metric('Entregadores únicos', unicos)
        
        with col2:
            avg_distance = distance(df1,False)
            col2.metric('Distância média', avg_distance)
        
        with col3:
            df_aux = avg_std_time(df1,'Yes ','avg_time')
            col3.metric('Tempo médio', df_aux)
            
        with col4:
            df_aux = avg_std_time(df1,'Yes ','std_time')
            col4.metric('STD p/ Festival', df_aux)
        
        with col5:
            df_aux = avg_std_time(df1,'No ','avg_time')
            col5.metric('Tempo médio', df_aux)
        
        with col6:
            df_aux = avg_std_time(df1,'No ','std_time')
            col6.metric('STD da entrega', df_aux) 
    
    with st.container():
        st.markdown('''---''')
        st.title('Tempo médio de entrega por cidade')

        col1, col2 = st.columns(2)
        with col1:
            fig = avg_std_time_graph(df1)
            st.plotly_chart(fig)
                  
        with col2:
            cols = ['City','Time_taken(min)','Type_of_order']
            df_aux = df1.loc[:,cols].groupby(['City','Type_of_order']).agg(['mean','std'])
            df_aux.columns = ['avg_time','std_time']
            df_aux = df_aux.reset_index()
            st.dataframe(df_aux)

    with st.container():
        st.markdown('''---''')
        st.title('Distribuição do tempo')
 
        col1, col2 = st.columns(2)
        with col1:
            fig = distance(df1,fig=True)   
            st.plotly_chart(fig)
       
        with col2:
            fig = avg_std_time_on_traffic(df1)    
            st.plotly_chart(fig)


































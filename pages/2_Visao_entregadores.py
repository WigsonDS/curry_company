# Importacao das bibliotecas
import pandas as pd
import plotly.express as px
import folium
import streamlit as st
from PIL import Image
# importação da biblioteca para encontrarmos a distância entre os pontos 
from haversine import haversine
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Entregadores', page_icon='🛵',layout='wide')

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

def top_delivers(df_concat, top_asc):
    # seleção de colunas
    cols = ['Delivery_person_ID','City','Time_taken(min)']
    # Agrupamento do tempo médio por entregador
    df_aux = df1.loc[:,cols].groupby(['City','Delivery_person_ID']).mean().sort_values(['City','Time_taken(min)'],ascending=top_asc).reset_index()
    # Seleção dos 10 entregadores mais rápidos por cidade
    df_aux01 = df_aux.loc[df_aux['City']=='Metropolitian ',:].head(10)
    df_aux02 = df_aux.loc[df_aux['City']=='Urban ',:].head(10)
    df_aux03 = df_aux.loc[df_aux['City']=='Semi-Urban ',:].head(10)
    # Criação de um dataframe concatenado com os dataframes selecionados por cidade
    df_concat = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
    return df_concat 

    
#carregando o dataset
df = pd.read_csv("train.csv")

#limpeza do dataset
df1 = clean_code(df)

# ===============================
# VISÃO ENTREGADORES
#================================

# ===============================
# Barra lateral
# ===============================
st.header("Marketplace - Visão Entregadores")

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

# ===============================
# layout no streamlit
# ===============================    

tab1,tab2,tab3 = st.tabs(['Visão Gerencial','_','_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4,gap='large')

        with col1:
            # A maior idade dos entregadores
            
            maior_idade = df1['Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idade)
            
        with col2:
            # A menor idade dos entregadores
            
            menor_idade = df1['Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
            
        with col3:
            # A melhor condição de veículos
            
            melhor_condicao = df1['Vehicle_condition'].max()
            col3.metric('Melhor condição', melhor_condicao)

        with col4:
            # A pior condição de veículos
            
            pior_condicao = df1['Vehicle_condition'].min()
            col4.metric('Pior condição', pior_condicao)

    with st.container():
        st.markdown('''---''')
        st.title('Avaliações')
        
        col1, col2 = st.columns(2)
       
        with col1:
            st.markdown('##### Avaliações médias por entregador')
            # Seleção das colunas para avaliação
            cols = ['Delivery_person_Ratings','Delivery_person_ID']
            # Realização do agrupamento por Entregador e aplicando o método mean e reiniciando o índice para organização da tabela
            df_aux = df1.loc[:,cols].groupby(['Delivery_person_ID']).mean().reset_index()
            
            # Apresentação da tabela organizando a avaliação média por entregador
            st.dataframe(df_aux)

        with col2:
            st.markdown('##### Avaliação média por trânsito')
            # seleção das colunas da avaliação média e tipo de tráfego
            cols = ['Delivery_person_Ratings','Road_traffic_density']
            df_aux = df1.loc[:,cols].groupby(['Road_traffic_density']).agg(['mean','std'])
            df_aux.columns = ['avg_rate','std_rate']
            df_aux.reset_index()
            st.dataframe(df_aux)
            
            st.markdown('##### Avaliação média por clima')
            # seleção das colunas da avaliação média e tipo de tráfego
            cols = ['Delivery_person_Ratings','Weatherconditions']
            # agrupamento das avaliações médias por condição climática
            df_aux = df1.loc[:,cols].groupby(['Weatherconditions']).agg(['mean','std'])
            df_aux.columns = ['avg_rate','std_rate']
            df_aux.reset_index()
            st.dataframe(df_aux)
            
    
    with st.container():
        st.markdown('''---''')

        st.title('Velocidade de entrega')
        
        
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Top entregadores mais rápidos')
            df_concat = top_delivers(df1,top_asc=True)
            st.dataframe(df_concat)    
        
        with col2:
            st.markdown('##### Top entregadores mais lentos')
            
            df_concat = top_delivers(df1,top_asc=False)
            st.dataframe(df_concat)
            
            
            
























            
            
        
        



















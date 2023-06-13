import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='🎲'
)
# image_path=('C:/Users/wigso/Documents/repos/FTC/CICLO-03/')
image=Image.open('image.jpg')
st.sidebar.image(image,width=300)

st.sidebar.markdown(' Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('''---''')

st.write('# Curry Company Growth Dashboard')
st.markdown(
    """
        Growth Dashboard foi construído para acompanhar as métricas de crescimento dos entregadores e restaurantes.
        ### Como utilizar esse Growth dashboard?
        - Visão Empresa:
            - Visão Gerencial: Métricas gerais de comportamento.
            - Visão Tática: indicadores semanais de crescimento 
            - Visão Geográfica: insights de geolocalização
        - Visão Entregador 
            - Acompanhamento dos indicadores semanais de crescimento 
        - Visão Restaurante:
            - Indicadores semanais de crescimentos dos restaurantes
        
        ### ASK FOR HELP
        - Time de Data Science no Discord
            - @WigsonBastos
    """)

        
            
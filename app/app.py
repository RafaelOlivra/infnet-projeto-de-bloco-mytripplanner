import streamlit as st
from dotenv import load_dotenv

####################
# CONFIGURATION
####################

# Load environment variables
load_dotenv('../.env')

####################
# PAGE CONFIG
####################

# Set page title
st.title('🗺️ MyTripPlanner')
st.write(
    '''
    O MyTripPlanner é um aplicativo de planejamento de viagens que ajuda os usuários a organizarem suas viagens, fornecendo previsões meteorológicas, condições de trânsito e notificações sobre possíveis problemas, como vias interditadas e restrições de rodízio de placas. O app utiliza dados em tempo real e históricos para recomendar as melhores rotas e horários para viajar, garantindo uma jornada tranquila e sem contratempos.
    '''
)

# Useful links
st.write(
    '''
    ### Links Úteis
    ### Artefatos
    - [Repositório no GitHub](https://github.com/RafaelOlivra/python-llms-if-tp1)
    - [Business Model Canvas](https://docs.google.com/drawings/d/1LDVFgGZBJcKsntF1MJgB_Y5skqeSBI1mjtDtm7hmOt8/edit)
    - [Project Charter](https://docs.google.com/document/d/1aqE3sguPtd9xvBwgypT2NwycYuOskVr0EFID9omDIic/edit?usp=sharing)
    - [Data Summary Report](https://docs.google.com/document/d/1jie_4x3r550BwLlOtSxuLYOwWTwRtqeiXuroQSZUtJQ/edit?usp=sharing)
    ### Fontes de dados e APIs
    Essas fontes **poderão** ser utilizadas no desenvolvimento do MyTripPlanner
    - [OpenWeatherMap](https://openweathermap.org/)
    - [Meteoblue](https://content.meteoblue.com/pt/solucoes-para-empresas/api-meteorologica/free-weather-api)
    - [INMET](https://bdmep.inmet.gov.br/)
    - [Google Maps](https://cloud.google.com/maps-platform)
    - [Waze](https://www.waze.com/pt-BR/)
    - [Here Maps](https://developer.here.com/)
    - [Perplexity AI](https://www.perplexity.ai/)
    - [Phind](https://www.phind.com/search?home=true)
    - [OpenAI](https://openai.com/)
    ### Inspirações
    - [Agenda 2030](https://brasil.un.org/pt-br/91863-agenda-2030-para-o-desenvolvimento-sustent%C3%A1vel)
    '''
)
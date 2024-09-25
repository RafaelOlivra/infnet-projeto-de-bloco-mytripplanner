import streamlit as st  # Home Page


def About():

    # Set page title
    st.set_page_config(
        page_title="Artefatos",
        page_icon="⭐",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    st.title("🗺️ MyTripPlanner")
    st.write(
        """
        O MyTripPlanner é um aplicativo de planejamento de viagens, projetado para ajudar os usuários a organizarem suas jornadas de forma eficiente e personalizada. O app oferece previsões meteorológicas detalhadas e sugestões de roteiros para o destino escolhido, utilizando dados precisos de diversas APIs e integração com Inteligência Artificial. Com o MyTripPlanner, os viajantes podem desfrutar de uma experiência tranquila e agradável, sem surpresas indesejadas pelo caminho.
        
        ---
        """
    )

    # Useful links
    st.write(
        """
        ### Links Úteis

        ### Artefatos
        - [Repositório no GitHub](https://github.com/RafaelOlivra/python-llms-if-tp1)
        - [Business Model Canvas](https://docs.google.com/drawings/d/1LDVFgGZBJcKsntF1MJgB_Y5skqeSBI1mjtDtm7hmOt8/edit)
        - [Project Charter](https://docs.google.com/document/d/1aqE3sguPtd9xvBwgypT2NwycYuOskVr0EFID9omDIic/edit?usp=sharing)
        - [Data Summary Report](https://docs.google.com/document/d/1jie_4x3r550BwLlOtSxuLYOwWTwRtqeiXuroQSZUtJQ/edit?usp=sharing)

        ### Fontes de dados e APIs
        Essas fontes **poderão** ser utilizadas no desenvolvimento do MyTripPlanner
        - [OpenWeatherMap](https://openweathermap.org/)
        - [Google Maps](https://cloud.google.com/maps-platform)
        - [Yelp](https://www.yelp.com.br/)
        - [Perplexity AI - EM ANÁLISE](https://www.perplexity.ai/)
        - [Phind - EM ANÁLISE](https://www.phind.com/search?home=true)
        - [OpenAI - EM ANÁLISE](https://openai.com/)

        ### Inspirações
        - [Agenda 2030](https://brasil.un.org/pt-br/91863-agenda-2030-para-o-desenvolvimento-sustent%C3%A1vel)
        - [Streamlit Gallery](https://www.streamlit.io/gallery)
        """
    )


# --------------------------
# INIT
# --------------------------
About()

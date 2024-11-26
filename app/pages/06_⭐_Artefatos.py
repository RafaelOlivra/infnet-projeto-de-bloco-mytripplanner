import streamlit as st
from services.AppData import AppData


def About():
    # Set logo
    assets_dir = AppData().get_config("assets_dir")
    st.logo(f"{assets_dir}my-trip-planner-logo.svg", size="large")

    # Set page title
    st.set_page_config(
        page_title="Artefatos",
        page_icon="⭐",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.image(f"{assets_dir}my-trip-planner-logo.svg", width=350)
    st.write(
        """
        O MyTripPlanner é um aplicativo de planejamento de viagens, projetado para ajudar os usuários a organizarem suas jornadas de forma eficiente e personalizada. O app oferece previsões meteorológicas detalhadas e sugestões de roteiros para o destino escolhido, utilizando dados precisos de diversas APIs e integração com Inteligência Artificial. Com o MyTripPlanner, os viajantes podem desfrutar de uma experiência tranquila e agradável, sem surpresas indesejadas pelo caminho.
        
        ---
        """
    )

    # Styles
    with open(f"{assets_dir}style.css") as css:
        st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

    st.write("### ODS e ESG")
    assets_dir = AppData().get_config("assets_dir")
    st.image(f"{assets_dir}objetivos_port.png", use_container_width=True)
    st.write(
        """
        Os dados obtidos e analisados pelo MyTripPlanner podem gerar um impacto social e ambiental positivo. Ao obter informações como
        padrões de viagem por cidade, escolhas de transporte e feedback dos usuários, é possível colaborar com governos
        locais e ministérios do turismo para promover um turismo sustentável. Por exemplo, é possível incentivar viagens
        fora de temporada para reduzir a sobrecarga em destinos turísticos, promover o uso de transportes ecológicos e
        destacar atrações que apoiem a cultura local e a biodiversidade. Essas ações contribuem para os
        ODS 11 (Cidades e Comunidades Sustentáveis), ODS 12 (Consumo e Produção Responsáveis) e
        ODS 13 (Combate as Alterações Climáticas).

        Além disso, a análise de sentimentos e feedbacks dos usuários pode fornecer informações valiosas
        sobre preocupações com acessibilidade, impacto ambiental e cultura local. Esses dados podem ser
        compartilhados com as autoridades competentes para orientar estratégias e políticas de turismo.
        Considerando também os ODS 16 (Paz, Justiça e Instituições Eficazes) e 10 (Redução das Desigualdades),
        o MyTripPlanner pode contribuir para promover práticas de turismo mais inclusivas e responsáveis. Essa abordagem abre
        possíveis oportunidades de parcerias com governos, ONGs e empresas do setor turístico.
        """
    )

    # Useful links
    st.write(
        """
        ### Links Úteis

        #### Artefatos
        - [Repositório no GitHub](https://github.com/RafaelOlivra/python-llms-if-tp1)
        - [Business Model Canvas](https://docs.google.com/drawings/d/1LDVFgGZBJcKsntF1MJgB_Y5skqeSBI1mjtDtm7hmOt8/edit)
        - [Business Model Canvas - Detalhado](https://docs.google.com/document/d/1dMvBe4FH52Bsh3mDYgn-a84B_LyIfZvZKMUeaZPACbw/edit)
        - [Project Charter](https://docs.google.com/document/d/1aqE3sguPtd9xvBwgypT2NwycYuOskVr0EFID9omDIic/edit?usp=sharing)
        - [Data Summary Report](https://docs.google.com/document/d/1jie_4x3r550BwLlOtSxuLYOwWTwRtqeiXuroQSZUtJQ/edit?usp=sharing)

        #### Fontes de dados e APIs
        Essas fontes **poderão** ser utilizadas no desenvolvimento do MyTripPlanner
        - [OpenWeatherMap](https://openweathermap.org/)
        - [Google Maps](https://cloud.google.com/maps-platform)
        - [Yelp](https://www.yelp.com.br/)
        - [Google Places API](https://developers.google.com/maps/documentation/places/web-service/overview?hl=pt-br)
        - [Google Gemini](https://ai.google.dev/)
        - [OpenAI](https://openai.com/index/openai-api/)

        #### Inspirações
        - [Agenda 2030](https://brasil.un.org/pt-br/91863-agenda-2030-para-o-desenvolvimento-sustent%C3%A1vel)
        - [Streamlit Gallery](https://www.streamlit.io/gallery)
        """
    )


# --------------------------
# INIT
# --------------------------
About()

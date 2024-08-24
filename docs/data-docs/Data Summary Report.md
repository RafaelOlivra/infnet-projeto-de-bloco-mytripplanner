# Data Summary Report \- MyTripPlanner

## Introdução

Este documento resume as fontes de dados que serão utilizadas no desenvolvimento do MyTripPlanner, um aplicativo de planejamento de viagens que fornece informações sobre condições climáticas, trânsito e outras variáveis que podem impactar a jornada dos usuários.

## Fontes de Dados

### [OpenWeatherMap API](https://www.geeksforgeeks.org/python-find-current-weather-of-any-city-using-openweathermap-api/)

* **Tipo de Dados**: Condições climáticas atuais e previsões de curto prazo.  
* **Objetivo de Uso**:  
  * Fornecer informações climáticas em tempo real e previsões para os próximos dias, focando nas localidades específicas dos usuários.  
  * Integrar dados climáticos diretamente no aplicativo para permitir que os usuários planejem suas viagens com base em condições meteorológicas precisas.

### [Google Maps API](https://developers.google.com/maps/apis-by-platform?hl=pt-br)

* **Tipo de Dados**: Dados de trânsito em tempo real, mapeamento de rotas, e informações sobre locais de interesse.  
* **Objetivo de Uso**:  
  * Fornecer informações sobre as condições de tráfego e rotas otimizadas, ajudando os usuários a planejar seus itinerários de viagem.

### [Yelp](https://www.yelp.com.br/s%C3%A3o-paulo)

*   
  **Tipo de Dados:** Informações sobre atrações turísticas, restaurantes, e serviços locais.  
* **Objetivo de Uso:**  
  * Integrar informações sobre atrações e locais de interesse nos destinos de viagem, permitindo que os usuários descubram e planejem visitas a esses pontos durante suas viagens.

### [OpenAI](https://openai.com/) (Em Análise)

* **Tipo de Dados**: Inteligência Artificial para geração de textos e sugestões de roteiros.  
* **Objetivo de Uso**:  
  * Integrar com o MyTripPlanner para gerar roteiros de viagem personalizados e oferecer recomendações baseadas em preferências do usuário e dados coletados.

### [Perplexity AI](https://www.perplexity.ai/) (Em Análise)

* **Tipo de Dados**: Ferramenta de busca inteligente para oferecer respostas rápidas e precisas.  
* **Objetivo de Uso**:  
  * Utilizar como alternativa para gerar roteiros e recomendações do MyTripPlanner, fornecendo informações adicionais relevantes para o planejamento de viagens.

### [Phind](https://www.phind.com/) (Em Análise)

* **Tipo de Dados**: Ferramenta de busca para desenvolvedores e pesquisadores.  
* **Objetivo de Uso**:  
  * Auxiliar na busca de informações técnicas e dados adicionais que possam melhorar as funcionalidades do MyTripPlanner.

## Conclusão

Essas fontes de dados foram selecionadas para garantir que o MyTripPlanner possa fornecer previsões precisas e em tempo real sobre condições que podem impactar as viagens dos usuários. O objetivo é utilizar essas informações para otimizar a experiência de viagem, ajudando os usuários a evitar contratempos relacionados ao clima, trânsito e outras variáveis externas.

Este é o primeiro esboço do **Data Summary Report** para o MyTripPlanner e será expandido conforme novas fontes de dados sejam identificadas e integradas ao projeto.
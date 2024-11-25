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

### [Google Places API](https://developers.google.com/maps/documentation/places/web-service/overview?hl=pt-br)

* **Tipo de Dados:** Informações sobre atrações turísticas, restaurantes, e serviços locais.  
* **Objetivo de Uso:**  
  * Integrar informações sobre atrações e locais de interesse nos destinos de viagem, permitindo que os usuários descubram e planejem visitas a esses pontos durante suas viagens.

### [Yelp](https://www.yelp.com.br/s%C3%A3o-paulo) (Alternativa)

* **Tipo de Dados:** Informações sobre atrações turísticas, restaurantes, e serviços locais.  
* **Objetivo de Uso:**  
  * Integrar informações sobre atrações e locais de interesse nos destinos de viagem, permitindo que os usuários descubram e planejem visitas a esses pontos durante suas viagens.

### [OpenAI](https://openai.com/index/openai-api/)

* **Tipo de Dados**: Inteligência Artificial para geração de textos e sugestões de roteiros.  
* **Objetivo de Uso**:  
  * Integrar com o MyTripPlanner para gerar roteiros de viagem personalizados e oferecer recomendações baseadas em preferências do usuário e dados coletados.

### [GoogleGemini](https://ai.google.dev/) (Alternativa)

* **Tipo de Dados**: Inteligência Artificial para geração de textos e sugestões de roteiros.  
* **Objetivo de Uso**:  
  * Integrar com o MyTripPlanner para gerar roteiros de viagem personalizados e oferecer recomendações baseadas em preferências do usuário e dados coletados.

### [HuggingFace](https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english)

* **Tipo de Dados**: Inteligência Artificial para prover análise de sentimentos.  
* **Objetivo de Uso**:  
  * Integrar com o MyTripPlanner fornecendo análise de sentimento baseado no feedback fornecido pelos usuários.

Essas fontes de dados foram selecionadas para garantir que o MyTripPlanner possa fornecer previsões precisas e em tempo real sobre condições que podem impactar as viagens dos usuários. O objetivo é utilizar essas informações para otimizar a experiência de viagem, ajudando os usuários a evitar contratempos relacionados ao clima, trânsito e outras variáveis externas.
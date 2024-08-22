# Data Summary Report \- MyTripPlanner

## Introdução

Este documento resume as fontes de dados que serão utilizadas no desenvolvimento do MyTripPlanner, um aplicativo de planejamento de viagens que fornece informações sobre condições climáticas, trânsito e outras variáveis que podem impactar a jornada dos usuários.

## Fontes de Dados

### **1\. [INMET \- Instituto Nacional de Meteorologia](https://bdmep.inmet.gov.br/)**

* **Tipo de Dados**: Dados meteorológicos históricos e em tempo real para várias localidades no Brasil.  
* **Objetivo de Uso**:  
  * Integrar dados em tempo real para fornecer atualizações precisas sobre as condições climáticas durante a viagem do usuário.

### **2\. [Meteoblue \- API Meteorológica](https://content.meteoblue.com/pt/solucoes-para-empresas/api-meteorologica/free-weather-api)**

* **Tipo de Dados**: Previsões meteorológicas globais, incluindo temperatura, precipitação, vento, entre outros.  
* **Objetivo de Uso**:  
  * Fornecer previsões meteorológicas de curto e médio prazo para as datas de viagem dos usuários.  
  * Complementar os dados do INMET com previsões globais em regiões onde os dados locais não são suficientes.

### **3\. [OpenWeatherMap API](https://www.geeksforgeeks.org/python-find-current-weather-of-any-city-using-openweathermap-api/)**

* **Tipo de Dados**: Condições climáticas atuais e previsões de curto prazo.  
* **Objetivo de Uso**:  
  * Fornecer informações climáticas em tempo real e previsões para os próximos dias, focando nas localidades específicas dos usuários.  
  * Integrar dados climáticos diretamente no aplicativo para permitir que os usuários planejem suas viagens com base em condições meteorológicas precisas.

### **4\. [Google Maps API](https://developers.google.com/maps/apis-by-platform?hl=pt-br)**

* **Tipo de Dados**: Dados de trânsito em tempo real, mapeamento de rotas, e informações sobre locais de interesse.  
* **Objetivo de Uso**:  
  * Fornecer informações sobre as condições de tráfego e rotas otimizadas, ajudando os usuários a planejar seus itinerários de viagem.

### **5\. [Waze](https://www.waze.com/)**

* **Tipo de Dados**: Dados de tráfego gerados por usuários, incluindo informações sobre acidentes, congestionamentos, e bloqueios de estradas.  
* **Objetivo de Uso**:  
  * Integrar dados de tráfego em tempo real para oferecer as melhores rotas e alertar sobre possíveis problemas nas estradas.

### **6\. [Here Maps](https://www.here.com/)**

* **Tipo de Dados**: Dados de mapeamento e trânsito, incluindo opções de transporte público e navegação.  
* **Objetivo de Uso**:  
  * Fornecer dados complementares de trânsito e mapeamento para melhorar a precisão das recomendações de rotas.

### **7\. [OpenAI](https://openai.com/)**

* **Tipo de Dados**: Inteligência Artificial para geração de textos e sugestões de roteiros.  
* **Objetivo de Uso**:  
  * Integrar com o MyTripPlanner para gerar roteiros de viagem personalizados e oferecer recomendações baseadas em preferências do usuário e dados coletados.

### **8\. [Perplexity AI](https://www.perplexity.ai/)**

* **Tipo de Dados**: Ferramenta de busca inteligente para oferecer respostas rápidas e precisas.  
* **Objetivo de Uso**:  
  * Utilizar como alternativa para gerar roteiros e recomendações do MyTripPlanner, fornecendo informações adicionais relevantes para o planejamento de viagens.

### **9\. [Phind](https://www.phind.com/)**

* **Tipo de Dados**: Ferramenta de busca para desenvolvedores e pesquisadores.  
* **Objetivo de Uso**:  
  * Auxiliar na busca de informações técnicas e dados adicionais que possam melhorar as funcionalidades do MyTripPlanner.

## Conclusão

Essas fontes de dados foram selecionadas para garantir que o MyTripPlanner possa fornecer previsões precisas e em tempo real sobre condições que podem impactar as viagens dos usuários. O objetivo é utilizar essas informações para otimizar a experiência de viagem, ajudando os usuários a evitar contratempos relacionados ao clima, trânsito e outras variáveis externas.

Este é o primeiro esboço do **Data Summary Report** para o MyTripPlanner e será expandido conforme novas fontes de dados sejam identificadas e integradas ao projeto.
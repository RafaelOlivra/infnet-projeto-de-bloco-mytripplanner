# Data Summary Report \- MyTripPlanner

## Introdução

Este documento resume as fontes de dados que serão utilizadas no desenvolvimento do MyTripPlanner, um aplicativo de planejamento de viagens que fornece informações sobre condições climáticas, trânsito e outras variáveis que podem impactar a jornada dos usuários.

## Fontes de Dados

### **1\. [INMET \- Instituto Nacional de Meteorologia](https://bdmep.inmet.gov.br/)**

* **Tipo de Dados**: Dados meteorológicos históricos e em tempo real para várias localidades no Brasil.  
* **Objetivo de Uso**:  
  * Utilizar dados climáticos históricos para treinar modelos de previsão do tempo.  
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

## Conclusão

Essas fontes de dados foram selecionadas para garantir que o MyTripPlanner possa fornecer previsões precisas e em tempo real sobre condições que podem impactar as viagens dos usuários. O objetivo é utilizar essas informações para otimizar a experiência de viagem, ajudando os usuários a evitar contratempos relacionados ao clima e outras variáveis externas.

Este é o primeiro esboço do **Data Summary Report** para o MyTripPlanner e será expandido conforme novas fontes de dados sejam identificadas e integradas ao projeto.


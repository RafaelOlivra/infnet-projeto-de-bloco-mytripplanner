# Project Charter \- MyTripPlanner

## Business Background

* **Client**: MyTripPlanner  
* **Business Domain**: Tecnologia de viagens e planejamento  
* **Business Problems**:  
  * Os viajantes enfrentam dificuldades para planejar suas viagens devido a imprevistos, como mudanças climáticas, condições de trânsito, rodízio de placas e vias interditadas.  
  * Falta de integração entre informações que possam afetar a experiência de viagem dos usuários, resultando em atrasos e frustrações.

## Scope

* **Data Science Solutions**:  
  * Integrar um sistema de previsão e notificação que antecipe problemas climáticos, condições de tráfego e outras restrições que possam impactar a viagem dos usuários.  
  * Implementar algoritmos de aprendizado de máquina para prever as melhores rotas e horários de viagem com base em dados históricos e em tempo real.  
  * Integrar essas previsões em uma interface amigável que permita ao usuário planejar suas viagens de forma fácil e eficiente.  
* **What Will We Do**:  
  * Desenvolver um sistema de previsão para condições climáticas, trânsito e rodízio de placas.  
  * Criar uma aplicação que analise dados regularmente e forneça notificações ao usuário.  
  * Construir uma interface de usuário intuitiva que permita fácil acesso e visualização das informações.  
* **How Will The Customer consume it**:  
  * O usuário final acessará o MyTripPlanner por meio de um aplicativo web, onde poderá agendar viagens e receber notificações personalizadas sobre possíveis problemas e a melhor forma de evitá-los.

## Personnel

* **Who Are On This Project**:  
  * **MyTripPlanner Team**:  
    * **Project Lead**: Rafael Soares de Oliveira  
      * Desenvolvedor Web  
      * Cursando Data Science no Infnet

## Metrics

* **Qualitative Objectives**:  
  * Melhorar a experiência de planejamento de viagens dos usuários, reduzindo surpresas e problemas inesperados.  
  * Aumentar a satisfação do usuário ao garantir que as viagens sejam realizadas sem contratempos.  
* **Quantifiable Metrics**:  
  * Reduzir o número de viagens afetadas por problemas climáticos ou de trânsito em 30% no primeiro ano.  
  * Aumentar a taxa de retenção de usuários que utilizam o app para planejar viagens em 25% dentro de 6 meses.  
* **Baseline Values**:  
  * Atualmente, cerca de 50% dos usuários relatam problemas não antecipados em suas viagens.  
* **Measurement**:  
  * Comparar a frequência de problemas relatados antes e depois da implementação dos novos recursos através de feedback dos usuários.

## Plan

* **Phases**:  
  1. **Phase 1: Pesquisa e Planejamento** (3 semanas)  
     * Pesquisa de campo para analisar as dificuldades e necessidades dos usuários ao planejar uma viagem.  
     * Pesquisa de APIs que forneçam os dados necessários para o app.  
     * Análise de aplicações semelhantes ou possíveis competidores a fim de descobrir padrões e possíveis áreas de melhoria.  
     * Esboço inicial da aplicação.  
  2. **Phase 2: Pesquisa de APIs Climáticas** (2 semanas)  
     * Pesquisar APIs que forneçam dados para clima.  
     * Testes e validação das APIs.  
  3. **Phase 3: Desenvolvimento da Interface e API** (3 semanas)  
     * Criação da interface do usuário no Streamlit.  
     * Integração com APIs.  
  4. **Phase 4: Testes e Iteração** (2 semanas)  
     * Testes de usabilidade com um grupo de usuários.  
     * Ajustes e melhorias baseados no feedback.  
  5. **Phase 5: Lançamento Inicial (Beta)** (2 semanas)  
     * Lançamento oficial do app beta com as funcionalidades básicas.  
     * Ajustes e melhorias baseados no feedback.  
  6. **Phase 6: Pesquisa de APIs de Trânsito** (2 semanas)  
     * Pesquisar APIs que forneçam dados de trânsito e rodízio de placas.  
  7. **Phase 7: Integração APIs de Trânsito** (4 semanas)  
     * Integração com APIs.  
  8. **Phase 8: Lançamento e Monitoramento** (2 semanas)  
     * Lançamento oficial do app.  
     * Monitoramento e análise contínua de desempenho.

## Architecture

* **Data**:  
  * **Expected Data**: Dados meteorológicos em tempo real, informações de trânsito, dados de rodízio de placas, e dados de localização de usuários.  
  * **Data Movement**:  
    * Dados coletados de APIs externas e movidos para o banco de dados central do MyTripPlanner.  
    * Dados históricos armazenados localmente para análise e melhoria.  
* **Tools and Resources**:  
  * **Database SQLite** para armazenamento de dados.  
  * **Streamlit** como ferramenta para criação da aplicação inicial.  
* **Web Service Consumption**:  
  * Os dados coletados serão utilizados pelo app Streamlit, que utilizará as previsões para notificar os usuários sobre condições adversas e recomendar rotas ou horários alternativos.  
  * Fluxo de dados e integração contínua para atualização em tempo real.

## Communication

* **How Will We Keep in Touch**:  
  * Análise semanal do progresso geral da aplicação.  
  * Atualizações em um repositório do GitHub contendo todo o histórico da aplicação.  
* **Contact Persons**:  
  * **MyTripPlanner**:  
    * **Project Lead**: Rafael Soares de Oliveira

